#!/usr/bin/env python
"""H3948 (FINDINGS Sec.453) -- would-change store impact of the four-tier parser. READ-ONLY.

Measures how many rows of the pwg_ru RU store the corrected sense segmentation
WOULD change, and writes nothing but a side report. The handoff's fence is
verbatim: "No store writes of any kind. No re-segmentation of existing rows, no
requeue, no mirror refresh, no ledger row that mutates content." The store is
opened 'r' and its sha256 is asserted equal before and after the pass.

Method (this is the "query that produced the number", stated in full):

  1. Every pwg.txt record is segmented twice through microstructure's own
     leaf_senses() code path -- once with MARK/ADJACENT_MARKERS temporarily
     reverted to the pre-H3948 two-tier forms (Sec.447: digit + latin), once as
     they stand now (roman division + digit + latin + greek).
  2. Per key1 (all its homograph records folded together) the result is a map
     sense_id -> sorted list of gloss digests. A key1 is CHANGED when that map
     differs between the two parsers -- a new id, a lost id, or the same id now
     carrying different text because children were split off it.
  3. Join to the store on key1 ALONE. This repeats the documented join of
     audit_sense_glyph.py (H1350 W1.4) and FINDINGS Sec.454: the store's `h`
     field is not a homograph key -- live inspection on this Mac found it
     holding the literal string '<div n="1">' -- so no per-homograph join is
     available. key1-only over-flags and never under-flags.

  Two numbers come out of that join, and the difference between them matters:

    conservative (key1-only)  every store row whose key1 has ANY changed
                              homograph. The upper bound, comparable with the
                              H1350 audit.
    tag-resolved              rows whose own `sense_tag` is an id that the
                              pre-H3948 parser actually emitted for that key1
                              AND whose id/text changed. The lower bound.

  Rows whose `sense_tag` matches no pre-H3948 id (upstream tags such as
  'caus-1', 'note', or a tag from a homograph the fold cannot separate) are
  counted as their own UNRESOLVED class and are claimed for neither bound --
  the handoff's ambiguity policy: leave it unresolved and count it separately
  rather than guessing.

    python pwg_four_tier_store_impact.py
    python pwg_four_tier_store_impact.py --limit 5000      # debug, partial corpus
    python pwg_four_tier_store_impact.py --store <path>
"""
import argparse
import collections
import hashlib
import json
import math
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_mask              # noqa: E402
import microstructure as ms  # noqa: E402

REPORTS_DIR = os.path.join(HERE, '..', 'reports')
REPORT_PATH = os.path.join(REPORTS_DIR, 'H3948_four_tier_store_impact.json')

# The RU store is a large (26MB), rights-fenced data file that lives in the
# private pwg-ru-data repo, not in this tree. audit_sense_glyph.py's two
# hardcoded paths (a local src/ copy, a Windows main-tree path) both miss on
# this Mac; the canonical location is checked first here and the older two are
# kept as fallbacks so the script still runs on the Windows box.
STORE_CANDIDATES = [
    os.path.join(HERE, '..', '..', '..', 'pwg-ru-data', 'tm',
                 'pwg_ru_translated.jsonl'),
    os.path.expanduser('~/Documents/GitHub/pwg-ru-data/tm/pwg_ru_translated.jsonl'),
    os.path.join(HERE, 'pwg_ru_translated.jsonl'),
    r'C:\Users\user\Documents\GitHub\pwg-ru-data\tm\pwg_ru_translated.jsonl',
    r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pwg_ru_translated.jsonl',
]

# The Sec.447 two-tier forms, exactly as they stood before H3948 (identical to
# the constants the selftest reverts to, kept in sync by test_revert_constants).
PRE_H3948_MARK = re.compile(r'(?<![^\s—])(?P<t>\d{1,2}|[a-z])[)〉]')
PRE_H3948_ADJACENT = re.compile(r'([)〉])(?=(?:\d{1,2}|[a-z])[)〉])')


def find_store(explicit=None):
    if explicit:
        return explicit
    for p in STORE_CANDIDATES:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def wilson_ci(k, n, z=1.96):
    """Wilson score interval, same helper shape as audit_sense_glyph.py."""
    if not n:
        return (0.0, 0.0)
    p = k / float(n)
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - s) / d), min(1.0, (c + s) / d))


def digest(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:8]


def segment(buf):
    """(sense_id, gloss digest) pairs exactly as leaf_senses() emits senses."""
    out = []
    body = ms.ADJACENT_MARKERS.sub(r'\1 ', '\n'.join(buf[1:]))
    for seg in ms.split_senses(body):
        if seg['n'] == '0':
            continue                       # pre-sense head text
        out.append((ms.sense_path(seg), digest(ms.clean_de(seg['text']))))
    return out


def scan_corpus(limit=None):
    """key1 -> {sense_id: [digests]} under both parsers, plus record counts."""
    old_maps = collections.defaultdict(lambda: collections.defaultdict(list))
    new_maps = collections.defaultdict(lambda: collections.defaultdict(list))
    records = 0
    saved = (ms.MARK, ms.ADJACENT_MARKERS)
    try:
        for buf in pwg_mask.records(limit=limit) if limit else pwg_mask.records():
            records += 1
            k1, _k2, _h = ms.header(buf)
            ms.MARK, ms.ADJACENT_MARKERS = PRE_H3948_MARK, PRE_H3948_ADJACENT
            for sid, dg in segment(buf):
                old_maps[k1][sid].append(dg)
            ms.MARK, ms.ADJACENT_MARKERS = saved
            for sid, dg in segment(buf):
                new_maps[k1][sid].append(dg)
    finally:
        ms.MARK, ms.ADJACENT_MARKERS = saved
    for maps in (old_maps, new_maps):
        for k1 in maps:
            for sid in maps[k1]:
                maps[k1][sid].sort()
    return old_maps, new_maps, records


def changed_keys(old_maps, new_maps):
    """key1 values whose folded sense map differs, and the per-id verdicts."""
    changed, per_id = set(), {}
    for k1 in set(old_maps) | set(new_maps):
        o = {k: v for k, v in old_maps.get(k1, {}).items()}
        n = {k: v for k, v in new_maps.get(k1, {}).items()}
        if o == n:
            continue
        changed.add(k1)
        per_id[k1] = {sid: (o.get(sid) != n.get(sid))
                      for sid in set(o) | set(n)}
    return changed, per_id


def scan_store(store_path, changed, per_id, old_maps):
    """Read the store once, read-only, and bucket every row."""
    sha_before = sha256_of(store_path)
    rows = 0
    key1_rows = collections.Counter()
    store_keys = set()
    conservative = 0                      # key1-only: the upper bound
    tag_changed = 0                       # tag resolves and its sense changed
    tag_unchanged = 0                     # tag resolves and its sense did not
    tag_unresolved = 0                    # tag is not a pre-H3948 sense id
    unresolved_shapes = collections.Counter()
    changed_key1_hits = collections.Counter()
    bad_json = 0
    with open(store_path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                bad_json += 1
                continue
            rows += 1
            k1 = row.get('key1') or ''
            store_keys.add(k1)
            key1_rows[k1] += 1
            if k1 not in changed:
                continue
            conservative += 1
            changed_key1_hits[k1] += 1
            tag = row.get('sense_tag')
            tag = '' if tag is None else str(tag)
            if tag in old_maps.get(k1, {}):
                if per_id.get(k1, {}).get(tag):
                    tag_changed += 1
                else:
                    tag_unchanged += 1
            else:
                tag_unresolved += 1
                unresolved_shapes[tag[:24] or '(empty)'] += 1
    sha_after = sha256_of(store_path)
    assert sha_before == sha_after, \
        'FENCE VIOLATION: RU store hash changed during a read-only pass'
    return {
        'sha256': sha_before,
        'rows': rows,
        'bad_json_lines': bad_json,
        'distinct_key1': len(store_keys),
        'store_key1_that_changed': len(changed_key1_hits),
        'store_key1_not_in_corpus_changed_set': len(store_keys - changed),
        'conservative_rows_key1_only': conservative,
        'tag_resolved_changed_rows': tag_changed,
        'tag_resolved_unchanged_rows': tag_unchanged,
        'tag_unresolved_rows': tag_unresolved,
        'tag_unresolved_top_shapes': unresolved_shapes.most_common(15),
        'top_changed_key1_by_rows': changed_key1_hits.most_common(15),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--limit', type=int, default=None,
                    help='debug: first N pwg.txt records only')
    ap.add_argument('--store', default=None, help='explicit RU store path')
    ap.add_argument('--no-report', action='store_true',
                    help='print only; do not write the side report')
    args = ap.parse_args(argv)

    store_path = find_store(args.store)
    print('H3948 four-tier store impact (READ-ONLY)')
    print('corpus: %s' % pwg_mask.PWG)
    print('store : %s' % (store_path or '(NOT FOUND)'))
    if not store_path:
        print('\nThe RU store is not on this machine. Tried:')
        for p in STORE_CANDIDATES:
            print('  %s' % p)
        return 2

    old_maps, new_maps, records = scan_corpus(args.limit)
    changed, per_id = changed_keys(old_maps, new_maps)
    print('\ncorpus: %d records, %d distinct key1, %d key1 whose segmentation '
          'changes' % (records, len(set(old_maps) | set(new_maps)), len(changed)))

    st = scan_store(store_path, changed, per_id, old_maps)
    lo, hi = wilson_ci(st['conservative_rows_key1_only'], st['rows'])
    tlo, thi = wilson_ci(st['tag_resolved_changed_rows'], st['rows'])

    print('\nstore: %d rows, %d distinct key1  (sha256 %s… unchanged across the pass)'
          % (st['rows'], st['distinct_key1'], st['sha256'][:16]))
    print('  key1 present in the store AND changed by the fix: %d'
          % st['store_key1_that_changed'])
    print('  CONSERVATIVE would-change rows (key1-only join): %d / %d = %.2f%% '
          '[95%% CI %.2f–%.2f%%]'
          % (st['conservative_rows_key1_only'], st['rows'],
             100.0 * st['conservative_rows_key1_only'] / max(st['rows'], 1),
             100 * lo, 100 * hi))
    print('  of those, by the row\'s own sense_tag:')
    print('    tag resolves to a pre-H3948 sense id AND that sense changed: %d '
          '(%.2f%% of all rows [95%% CI %.2f–%.2f%%])'
          % (st['tag_resolved_changed_rows'],
             100.0 * st['tag_resolved_changed_rows'] / max(st['rows'], 1),
             100 * tlo, 100 * thi))
    print('    tag resolves, that sense unchanged: %d'
          % st['tag_resolved_unchanged_rows'])
    print('    tag resolves to NO pre-H3948 sense id (unresolved class, '
          'claimed for neither bound): %d' % st['tag_unresolved_rows'])
    print('    unresolved tag shapes: %s'
          % ', '.join('%s×%d' % (s, c)
                      for s, c in st['tag_unresolved_top_shapes']))
    print('  most-affected key1 by row count: %s'
          % ', '.join('%s×%d' % (k, c) for k, c in st['top_changed_key1_by_rows']))
    print('\nNo store row was written. Nothing was requeued or re-segmented.')

    if not args.no_report:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        payload = {
            'handoff': 'H3948',
            'finding': 'FINDINGS Sec.453',
            'read_only': True,
            'corpus': pwg_mask.PWG,
            'corpus_records': records,
            'corpus_distinct_key1': len(set(old_maps) | set(new_maps)),
            'corpus_changed_key1': len(changed),
            'store_path': store_path,
            'join': 'key1 only (FINDINGS Sec.454; store h holds \'<div n="1">\')',
            'store': st,
            'conservative_ci95': [lo, hi],
            'tag_resolved_ci95': [tlo, thi],
            'limit': args.limit,
        }
        with open(REPORT_PATH, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        print('report: %s' % os.path.abspath(REPORT_PATH))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
