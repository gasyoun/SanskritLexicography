#!/usr/bin/env python
r"""Offline re-derivation of the `{Tn}` placeholders leaked into the canonical store (C-01).

WHAT HAPPENED
-------------
`restore_card` unmasked three fields while `promote_final_cards.rows_for` read six, so
`card.iast` / `record.h` / `sense.tag` / `sense.differentia` were promoted with their mask
placeholders intact. Measured against the 11,605-row store: **670 rows** carry a raw `{Tn}`
(`sense_tag` 376, `h` 223, `differentia` 72, `ru` 2, `de` 2) -- including 223 rows whose
HEADWORD field reads literally `{T104}`. The generator side is fixed (see `card_fields.py`);
this repairs the rows already written.

WHY IT IS RECOVERABLE AT ALL
----------------------------
Masking is deterministic and the source is content-addressed: every store row records
`provenance.input_raw_sha256`, the SHA-256 of the exact `.raw.txt` it was generated from.
`pwg_mask.mask(raw)` re-derives the identical placeholder list `ph`, and `{Tn}` indexes `ph`
1-based. So the true value is `pwg_mask.restore(field, ph)` -- not a guess, a re-computation.

The source is located BY CONTENT ADDRESS, never by filename: `translation_memory.py` is
explicit that the address survives key renames, and it matters here -- `_ap~~h0_00_pwg01`
has no file of that name any more, yet 596 rows still resolve. Two independent guards run
before any row is touched: the recorded SHA must match a real file, and `mask/restore` must
round-trip that file byte-for-byte (the same invariant `gen_opt_harness2.py:950` asserts).

WHAT IT CANNOT DO -- MEASURED, NOT ASSUMED
------------------------------------------
* **74 of the 670 rows are NOT recoverable.** Their recorded `input_raw_sha256` addresses no
  file on disk: the source drifted after translation, so no map can be re-derived. The packet
  anticipated exactly this ("rows whose source drifted need re-translation, not
  re-derivation"). They are reported, never guessed at. This includes the 2 C-42 rows
  (`ban_d~~h0_11_ni`, `ban_d~~h0_21_upasam_0`), whose `{Tn}` is out-of-range by construction.
* **The 468 `h is None` rows are out of scope and CANNOT be repaired by any offline means.**
  That value was destroyed at the stitch, before it was ever persisted -- it is not in the
  store, not in `wf_output` (already null there), not in the portraits (they carry no `h`),
  and not in the TM (which is built FROM the store). `h` is free lexicographic text, not a
  function of the key, so it cannot be synthesised. They need re-translation.

USAGE
-----
    python src/backfill_tn_residue.py                 # dry run: report only, writes nothing
    python src/backfill_tn_residue.py --apply         # rewrite the store (atomic, with .bak)
    python src/backfill_tn_residue.py --json out.json # machine-readable per-row plan

Dry run is the default and is READ-ONLY. `--apply` writes via tmp + `os.replace` and keeps a
timestamped `.premerge.<stamp>.bak`, mirroring `promote_final_cards.py`'s existing convention
rather than inventing a second one.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import pwg_mask
import card_fields
from store_path import canonical_store

TN_RE = re.compile(r'\{T\d+\}')
LOCAL_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')


def default_input_dir(store_path):
    """Resolve `pilot/input` ALONGSIDE the store being repaired, not beside this script.

    Both the store and the `*.raw.txt` sources are gitignored, so they exist only in the MAIN
    checkout: a linked worktree has the code but 0 of the 110,374 raw files. Defaulting to
    `dirname(__file__)/pilot/input` therefore reads an EMPTY directory while
    `canonical_store()` correctly resolves the store back to the main checkout -- every row
    then reports "source gone" and the tool concludes, with total confidence, that nothing is
    recoverable. That is C-19's defect class exactly ("--data-root defaults to its own
    checkout ... a worktree run swaps the denominator"), and this tool reproduced it on its
    first run. Deriving the path from the resolved store keeps the two halves in one place.
    """
    return os.path.join(os.path.dirname(os.path.abspath(store_path)), 'pilot', 'input')

# The fields a store ROW carries, mapped to the card level they were promoted from. Derived
# from card_fields so this tool cannot drift from the restore/promote sides.
ROW_FIELDS = tuple(name for _level, name in card_fields.promoted_pairs('russian'))
# `rows_for` renames two of them on the way into the store.
ROW_ALIAS = {'tag': 'sense_tag', 'russian': 'ru', 'german': 'de'}
STORE_FIELDS = tuple(ROW_ALIAS.get(n, n) for n in ROW_FIELDS)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def build_address_index(input_dir):
    """sha256(raw bytes) -> path, over every `*.raw.txt`. The address IS the content."""
    index = {}
    for name in os.listdir(input_dir):
        if name.endswith('.raw.txt'):
            path = os.path.join(input_dir, name)
            index.setdefault(sha256_file(path), path)
    return index


def plan(store_path, input_dir):
    """Return (rows, plan_entries, stats). Reads only."""
    index = build_address_index(input_dir)
    ph_cache = {}
    rows, entries = [], []
    stats = collections.Counter()

    with open(store_path, encoding='utf-8') as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip('\n')
            if not line.strip():
                continue
            row = json.loads(line)
            rows.append(row)
            hit = [f for f in STORE_FIELDS
                   if isinstance(row.get(f), str) and TN_RE.search(row[f])]
            if not hit:
                continue
            stats['corrupt_rows'] += 1
            sha = (row.get('provenance') or {}).get('input_raw_sha256')
            subcard = row.get('subcard')
            if not sha:
                entries.append({'line': lineno, 'subcard': subcard, 'status': 'no_sha',
                                'reason': 'row records no provenance.input_raw_sha256'})
                stats['no_sha'] += 1
                continue
            if sha not in index:
                entries.append({'line': lineno, 'subcard': subcard, 'status': 'source_gone',
                                'reason': 'no raw source at content address %s' % sha[:12]})
                stats['source_gone'] += 1
                continue
            if sha not in ph_cache:
                raw = open(index[sha], encoding='utf-8').read()
                skel, ph, _ = pwg_mask.mask(raw)
                ph_cache[sha] = ph if pwg_mask.restore(skel, ph) == raw else None
            ph = ph_cache[sha]
            if ph is None:
                entries.append({'line': lineno, 'subcard': subcard, 'status': 'roundtrip_fail',
                               'reason': 'mask/restore does not round-trip this source'})
                stats['roundtrip_fail'] += 1
                continue
            bad = [t for f in hit for t in TN_RE.findall(row[f])
                   if not (1 <= int(t[2:-1]) <= len(ph))]
            if bad:
                entries.append({'line': lineno, 'subcard': subcard, 'status': 'out_of_range',
                                'reason': 'index past the map (%s); map has %d (C-42)'
                                          % (', '.join(sorted(set(bad))), len(ph))})
                stats['out_of_range'] += 1
                continue
            fixes = {f: pwg_mask.restore(row[f], ph) for f in hit}
            entries.append({'line': lineno, 'subcard': subcard, 'status': 'recoverable',
                            'source': os.path.basename(index[sha]),
                            'fields': {f: {'before': row[f], 'after': v}
                                       for f, v in fixes.items()}})
            stats['recoverable'] += 1
    return rows, entries, stats


def apply_plan(store_path, rows, entries):
    """Rewrite the store atomically, keeping a timestamped backup. Only called for --apply."""
    by_line = {e['line']: e for e in entries if e['status'] == 'recoverable'}
    changed = 0
    for i, row in enumerate(rows, 1):
        entry = by_line.get(i)
        if not entry:
            continue
        for field, delta in entry['fields'].items():
            row[field] = delta['after']
        changed += 1

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = '%s.premerge.%s.bak' % (store_path, stamp)
    with open(store_path, 'rb') as src, open(backup, 'wb') as dst:
        dst.write(src.read())
    tmp = store_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    os.replace(tmp, store_path)
    return changed, backup


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--store', default=None, help='store path (default: canonical_store())')
    ap.add_argument('--input-dir', default=None,
                    help='raw sources (default: pilot/input beside the RESOLVED store)')
    ap.add_argument('--apply', action='store_true',
                    help='rewrite the store (default is a read-only dry run)')
    ap.add_argument('--json', dest='json_out', default=None, help='write the plan as JSON')
    args = ap.parse_args()

    store_path = args.store or canonical_store(LOCAL_STORE)
    input_dir = args.input_dir or default_input_dir(store_path)
    if not os.path.isdir(input_dir):
        sys.exit('REFUSED: source dir does not exist: %s' % input_dir)
    n_raw = sum(1 for n in os.listdir(input_dir) if n.endswith('.raw.txt'))
    if not n_raw:
        # Fail loud rather than reporting a confident, wrong "nothing is recoverable".
        sys.exit('REFUSED: %s holds no *.raw.txt. Refusing to report every row as '
                 'unrecoverable off an empty source dir (C-19 class).' % input_dir)
    args.input_dir = input_dir
    print('store      : %s' % store_path)
    print('sources    : %s (%d raw files)' % (input_dir, n_raw))
    print('mode       : %s' % ('APPLY' if args.apply else 'dry run (read-only)'))
    print()

    rows, entries, stats = plan(store_path, args.input_dir)
    print('store rows            : %d' % len(rows))
    print('rows carrying a {Tn}  : %d' % stats['corrupt_rows'])
    print('  recoverable offline : %d' % stats['recoverable'])
    print('  source gone         : %d' % stats['source_gone'])
    print('  out of range (C-42) : %d' % stats['out_of_range'])
    print('  no sha recorded     : %d' % stats['no_sha'])
    print('  round-trip failed   : %d' % stats['roundtrip_fail'])
    print()

    unrec = [e for e in entries if e['status'] != 'recoverable']
    if unrec:
        print('NOT RECOVERABLE -- these need RE-TRANSLATION, never a guess:')
        for sub, group in sorted(collections.Counter(e['subcard'] for e in unrec).items()):
            reason = next(e['reason'] for e in unrec if e['subcard'] == sub)
            print('  %-34s %d row(s)  %s' % (sub, group, reason))
        print()

    sample = [e for e in entries if e['status'] == 'recoverable'][:3]
    if sample:
        print('SAMPLE of the re-derivation:')
        for e in sample:
            for f, d in e['fields'].items():
                print('  line %-6d %s.%s' % (e['line'], e['subcard'], f))
                print('    before: %r' % d['before'][:70])
                print('    after : %r' % d['after'][:70])
        print()

    if args.json_out:
        with open(args.json_out, 'w', encoding='utf-8') as fh:
            json.dump({'store': store_path, 'stats': dict(stats), 'entries': entries},
                      fh, ensure_ascii=False, indent=2)
        print('plan written: %s' % args.json_out)

    if not args.apply:
        print('DRY RUN -- nothing written. Re-run with --apply to rewrite the store.')
        return 0

    changed, backup = apply_plan(store_path, rows, entries)
    print('APPLIED: %d row(s) re-derived' % changed)
    print('backup : %s' % backup)
    residue = sum(1 for r in rows for f in STORE_FIELDS
                  if isinstance(r.get(f), str) and TN_RE.search(r[f]))
    print('remaining {Tn} rows: %d (the unrecoverable set above)' % residue)
    return 0


if __name__ == '__main__':
    sys.exit(main())
