#!/usr/bin/env python
r"""Repair the H1080 PWG->Russian store corruption without model calls.

The repair is dry-run by default.  It restores raw ``{Tn}`` placeholders from an exact
content-addressed raw source or from the exact ``PH`` map embedded in a historical generated
harness.  A historical harness is accepted only when its ``META.input_hashes`` binds the key
to the SHA-256 recorded on the store row.  It also reconstructs record ``h``/``iast`` from
immutable card identity for rows whose stitch discarded the record owner.

Only the two measured C-42 ``banD`` rows are quarantined.  Any other unresolved token, hash
drift, unexpected quarantine candidate, row-multiset drift, or source-store drift fails the
repair closed.  ``--apply`` requires ``--expected-sha256`` and uses fsynced same-directory
temporary files plus ``os.replace``.  The original store is retained as a hash-named backup.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, 'pilot')
for path in (HERE, PILOT):
    if path not in sys.path:
        sys.path.insert(0, path)

import card_fields
import corpus_gate as cg
import pwg_mask
from safe_filename import decode_safe_name
from store_path import canonical_store

TN_RE = re.compile(r'\{T(\d+)\}')
ROOT_CARD_RE = re.compile(r'^.+~~h\d+_\d+_(.+)$')
LOCAL_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
QUARANTINE_SUBCARDS = {
    'ban_d~~h0_11_ni',
    'ban_d~~h0_21_upasam_0',
}

ROW_ALIAS = {'tag': 'sense_tag', 'russian': 'ru', 'german': 'de'}
STORE_FIELDS = tuple(ROW_ALIAS.get(name, name)
                     for _level, name in card_fields.promoted_pairs('russian'))


class RepairRefusal(RuntimeError):
    """The repair contract could not be proved; no production replacement is allowed."""


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def default_input_dir(store_path):
    return os.path.join(os.path.dirname(os.path.abspath(store_path)), 'pilot', 'input')


def default_recovery_dir(store_path):
    return os.path.join(os.path.dirname(os.path.abspath(store_path)), 'pilot', 'output',
                        'h1080_recovery_sources')


def default_harness_dir(store_path):
    # Both the frozen legacy archive and later coordinator attempt directories are ignored
    # runtime evidence under this root.  The per-key META hash, not the directory name, is
    # the authority.
    return os.path.join(os.path.dirname(os.path.abspath(store_path)), 'pilot')


def read_rows(path):
    rows = []
    with open(path, encoding='utf-8') as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise RepairRefusal('malformed store JSON at line %d: %s' % (lineno, exc))
    return rows


def row_sha(row):
    data = json.dumps(row, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')
    return sha256_bytes(data)


def row_address(row):
    return (row.get('provenance') or {}).get('input_raw_sha256')


def affected_fields(row):
    return [field for field in STORE_FIELDS
            if isinstance(row.get(field), str) and TN_RE.search(row[field])]


def raw_maps(source_dirs, wanted):
    """Return ``(key, sha) -> (ph, evidence)`` for exact named raw sources only.

    H1080 has 86 affected cards and their key is retained on every row.  Looking up those
    exact names is both faster and safer than hashing 110k unrelated inputs.  Renamed legacy
    inputs are recovered from their generated harness instead.
    """
    found = {}
    for key, sha in wanted:
        if not key or not sha:
            continue
        for directory in source_dirs:
            path = os.path.join(directory, key + '.raw.txt')
            if not os.path.isfile(path) or sha256_file(path) != sha:
                continue
            with open(path, encoding='utf-8') as fh:
                raw = fh.read()
            skeleton, ph, _stats = pwg_mask.mask(raw)
            if pwg_mask.restore(skeleton, ph) != raw:
                raise RepairRefusal('mask round-trip failed for %s' % path)
            found[(key, sha)] = (ph, {
                'kind': 'exact_raw', 'path': os.path.abspath(path), 'sha256': sha,
            })
            break
    return found


def _json_constant(line, name):
    prefix = 'const %s = ' % name
    if not line.startswith(prefix):
        return None
    value = line[len(prefix):].rstrip('\r\n')
    if value.endswith(';'):
        value = value[:-1]
    return json.loads(value)


def harness_maps(harness_dirs, wanted):
    """Index exact PH maps bound by generated-harness ``META.input_hashes``."""
    wanted = set(wanted)
    found = {}
    for directory in harness_dirs:
        if not os.path.isdir(directory):
            continue
        for root, _dirs, names in os.walk(directory):
            for name in names:
                if not name.endswith('.js'):
                    continue
                path = os.path.join(root, name)
                phmaps = meta = None
                try:
                    with open(path, encoding='utf-8') as fh:
                        for line in fh:
                            if line.startswith('const PH = '):
                                phmaps = _json_constant(line, 'PH')
                            elif line.startswith('const META = '):
                                meta = _json_constant(line, 'META')
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if not isinstance(phmaps, dict) or not isinstance(meta, dict):
                    continue
                input_hashes = meta.get('input_hashes') or {}
                for key, hashes in input_hashes.items():
                    sha = (hashes or {}).get('raw_sha256')
                    address = (key, sha)
                    if address not in wanted or key not in phmaps:
                        continue
                    evidence = {
                        'kind': 'generated_harness_phmap',
                        'path': os.path.abspath(path),
                        'sha256': sha256_file(path),
                        'input_raw_sha256': sha,
                        'generated_at': meta.get('generated_at'),
                    }
                    prior = found.get(address)
                    candidate = (phmaps[key], evidence)
                    if prior and prior[0] != candidate[0]:
                        raise RepairRefusal('conflicting historical PH maps for %s @ %s'
                                            % address)
                    found[address] = candidate
    return found


def restore_text(value, ph, where):
    unresolved = []

    def repl(match):
        index = int(match.group(1))
        if not 1 <= index <= len(ph):
            unresolved.append(match.group(0))
            return match.group(0)
        return ph[index - 1]

    restored = TN_RE.sub(repl, value)
    if unresolved or TN_RE.search(restored):
        raise RepairRefusal('%s has unresolved/out-of-range token(s): %s (map has %d)'
                            % (where, ', '.join(sorted(set(unresolved))), len(ph)))
    return restored


def slp1_iast(value):
    return ''.join(cg._S2I.get(ch, ch) for ch in cg.form_key(value or ''))


def canonical_record_head(row):
    """Reconstruct a stable display head from immutable row/subcard identity.

    Existing row ``iast`` is authoritative for nominal/no-PWG cards.  For root cards, the
    suffix encodes the upasarga; head/secondary/supplement lanes deliberately fall back to
    the root.  This avoids reusing another model-authored row as repair evidence.
    """
    current = row.get('iast')
    if isinstance(current, str) and current.strip():
        return current.strip()
    root = row.get('key1') or ''
    root_iast = slp1_iast(root)
    subcard = row.get('subcard') or ''
    match = ROOT_CARD_RE.match(subcard)
    if not match:
        return root_iast
    suffix = match.group(1)
    if (suffix.startswith(('pwg', 'sec_', 'zz_')) or suffix == 'head'):
        return root_iast
    suffix = re.sub(r'_(?:0|1)$', '', suffix)
    try:
        prefix = decode_safe_name(suffix)
    except (TypeError, ValueError):
        prefix = ''
    if not prefix or prefix.startswith(('pwg', 'sec', 'zz')):
        return root_iast
    return slp1_iast(prefix + root)


def plan_repair(store_path, source_dirs, harness_dirs):
    rows = read_rows(store_path)
    original_multiset = collections.Counter((r.get('key1'), r.get('subcard')) for r in rows)
    corrupt = [r for r in rows if affected_fields(r)]
    already_clean = not corrupt and not any(r.get('h') is None for r in rows)
    wanted = {(r.get('subcard'), row_address(r)) for r in corrupt}
    maps = raw_maps(source_dirs, wanted)
    for address, value in harness_maps(harness_dirs, wanted).items():
        maps.setdefault(address, value)

    repaired = []
    quarantine = []
    entries = []
    source_evidence = {}
    stats = collections.Counter()

    for lineno, original in enumerate(rows, 1):
        row = json.loads(json.dumps(original, ensure_ascii=False))
        fields = affected_fields(row)
        address = (row.get('subcard'), row_address(row))
        if fields:
            stats['placeholder_rows'] += 1
            source = maps.get(address)
            if source is None:
                raise RepairRefusal('no exact raw/PH-map provenance for line %d %s @ %s'
                                    % (lineno, address[0], address[1]))
            ph, evidence = source
            try:
                fixes = {field: restore_text(row[field], ph, '%s.%s' % (address[0], field))
                         for field in fields}
            except RepairRefusal as exc:
                if address[0] not in QUARANTINE_SUBCARDS:
                    raise
                quarantine.append({
                    'schema': 'pwg_ru.store_quarantine.v1',
                    'key': row.get('key1'),
                    'subcard': address[0],
                    'reason': str(exc),
                    'original_row_sha256': row_sha(original),
                    'input_raw_sha256': address[1],
                    'row': original,
                })
                stats['quarantined_rows'] += 1
                entries.append({'line': lineno, 'subcard': address[0], 'status': 'quarantine'})
                continue
            if address[0] in QUARANTINE_SUBCARDS:
                raise RepairRefusal('expected measured C-42 quarantine row unexpectedly became '
                                    'restorable: %s' % address[0])
            row.update(fixes)
            stats['placeholder_repaired'] += 1
            source_evidence[evidence['path']] = evidence
            entries.append({'line': lineno, 'subcard': address[0], 'status': 'token_repaired',
                            'fields': sorted(fixes), 'evidence': evidence})

        if row.get('h') is None:
            head = canonical_record_head(row)
            if not head:
                raise RepairRefusal('cannot reconstruct record h at line %d (%s)'
                                    % (lineno, row.get('subcard')))
            row['h'] = head
            if row.get('iast') is None:
                row['iast'] = head
            if row.get('grammar') is None:
                row['grammar'] = ''
            stats['null_headword_repaired'] += 1
            entries.append({'line': lineno, 'subcard': row.get('subcard'),
                            'status': 'record_owner_repaired', 'h': head})
        repaired.append(row)

    if not already_clean and set(q['subcard'] for q in quarantine) != QUARANTINE_SUBCARDS:
        raise RepairRefusal('quarantine set drift: expected %s, got %s'
                            % (sorted(QUARANTINE_SUBCARDS),
                               sorted(q['subcard'] for q in quarantine)))
    if any(affected_fields(row) for row in repaired):
        raise RepairRefusal('post-repair store still contains raw {Tn}')
    if any(row.get('h') is None for row in repaired):
        raise RepairRefusal('post-repair store still contains h == null')

    expected_multiset = original_multiset.copy()
    for q in quarantine:
        key = (q['row'].get('key1'), q['subcard'])
        expected_multiset[key] -= 1
        if expected_multiset[key] == 0:
            del expected_multiset[key]
    repaired_multiset = collections.Counter((r.get('key1'), r.get('subcard')) for r in repaired)
    if repaired_multiset != expected_multiset:
        raise RepairRefusal('key/subcard multiplicity changed outside the quarantine delta')

    stats['input_rows'] = len(rows)
    stats['output_rows'] = len(repaired)
    if already_clean:
        stats['already_clean'] = 1
    return {
        'schema': 'pwg_ru.store_repair_plan.v1',
        'store': os.path.abspath(store_path),
        'store_before_sha256': sha256_file(store_path),
        'stats': dict(stats),
        'entries': entries,
        'source_evidence': sorted(source_evidence.values(), key=lambda x: x['path']),
        'quarantine': quarantine,
    }, repaired


def jsonl_bytes(rows):
    return ''.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n'
                   for row in rows).encode('utf-8')


def atomic_write_bytes(path, data):
    directory = os.path.dirname(os.path.abspath(path)) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.%s.' % os.path.basename(path), suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def apply_repair(store_path, repaired, quarantine, expected_sha, quarantine_path):
    actual = sha256_file(store_path)
    if actual.lower() != expected_sha.lower():
        raise RepairRefusal('source-hash drift: expected %s, got %s' % (expected_sha, actual))
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = '%s.pre-h1080.%s.%s.bak' % (store_path, actual[:16], stamp)
    with open(store_path, 'rb') as fh:
        original = fh.read()
    atomic_write_bytes(backup, original)
    atomic_write_bytes(quarantine_path, jsonl_bytes(quarantine))
    atomic_write_bytes(store_path, jsonl_bytes(repaired))
    return backup, sha256_file(store_path), sha256_file(quarantine_path)


def write_report(path, report):
    atomic_write_bytes(path, (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--store', default=None, help='store path (default: canonical_store())')
    ap.add_argument('--source-dir', action='append', default=[],
                    help='exact raw source directory (repeatable)')
    ap.add_argument('--harness-dir', action='append', default=[],
                    help='historical generated-harness directory (repeatable)')
    ap.add_argument('--apply', action='store_true', help='atomically replace the store')
    ap.add_argument('--expected-sha256', default=None,
                    help='required source-store lock for --apply')
    ap.add_argument('--quarantine-out', default=None,
                    help='uncommitted quarantine JSONL path')
    ap.add_argument('--report', default=None, help='write machine-readable plan/result JSON')
    args = ap.parse_args(argv)

    store_path = args.store or canonical_store(LOCAL_STORE)
    if not os.path.isfile(store_path):
        raise RepairRefusal('canonical store does not exist: %s' % store_path)
    source_dirs = args.source_dir or [default_input_dir(store_path),
                                      default_recovery_dir(store_path)]
    harness_dirs = args.harness_dir or [default_harness_dir(store_path)]
    plan, repaired = plan_repair(store_path, source_dirs, harness_dirs)
    plan['source_dirs'] = [os.path.abspath(p) for p in source_dirs]
    plan['harness_dirs'] = [os.path.abspath(p) for p in harness_dirs]
    plan['mode'] = 'apply' if args.apply else 'dry_run'

    if not args.apply:
        if args.report:
            write_report(args.report, plan)
        print(json.dumps(plan['stats'], ensure_ascii=False, sort_keys=True))
        print('DRY RUN -- no store, backup, or quarantine file written')
        return 0
    if not args.expected_sha256:
        raise RepairRefusal('--apply requires --expected-sha256')
    if sha256_file(store_path).lower() != args.expected_sha256.lower():
        raise RepairRefusal('source-hash drift: expected %s, got %s'
                            % (args.expected_sha256, sha256_file(store_path)))
    if plan['stats'].get('already_clean'):
        if args.report:
            write_report(args.report, plan)
        print(json.dumps(plan['stats'], ensure_ascii=False, sort_keys=True))
        print('NO-OP: store already satisfies the H1080 repair invariants')
        return 0
    quarantine_path = args.quarantine_out or store_path + '.h1080_quarantine.jsonl'
    backup, after_sha, quarantine_sha = apply_repair(
        store_path, repaired, plan['quarantine'], args.expected_sha256, quarantine_path)
    plan.update({
        'store_after_sha256': after_sha,
        'backup_path': os.path.abspath(backup),
        'backup_sha256': sha256_file(backup),
        'quarantine_path': os.path.abspath(quarantine_path),
        'quarantine_sha256': quarantine_sha,
    })
    if args.report:
        write_report(args.report, plan)
    print(json.dumps(plan['stats'], ensure_ascii=False, sort_keys=True))
    print('APPLIED: %s -> %s' % (plan['store_before_sha256'], after_sha))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except RepairRefusal as exc:
        sys.exit('REFUSED: %s' % exc)
