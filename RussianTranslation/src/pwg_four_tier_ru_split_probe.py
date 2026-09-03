#!/usr/bin/env python
"""H3948 option-2: can the 12 rows be split MECHANICALLY, or only by a translator?

The inspect pass showed all 12 candidates are splits: the greek tier moved the
substance of e.g. `4a` into new `4aalpha/beta/gamma`, leaving the parent id with
only its head. A split is mechanical ONLY IF the stored Russian carries the same
enumeration markers as the German -- then the same four-tier segmentation applies
to `ru` and no wording is invented. This probe answers exactly that, per row:

  * marker counts in `de` and in `ru` (greek, latin, digit, roman);
  * whether the store already holds rows for the new child ids;
  * the review status, i.e. whether the row is paid human work or machine output.

Read-only.

    python pwg_four_tier_ru_split_probe.py
"""
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_four_tier_store_impact as impact  # noqa: E402

REPORTS_DIR = os.path.join(HERE, '..', 'reports')
CANDIDATES = os.path.join(REPORTS_DIR, 'H3948_four_tier_rewrite_candidates.json')

GREEK = re.compile(r'[α-ω][)〉]')
LATIN = re.compile(r'(?<![^\s—])[a-z][)〉]')
DIGIT = re.compile(r'(?<![^\s—])\d{1,2}[)〉]')
ROMAN = re.compile(r'(?<![^\s—])[ivxlIVXL]{1,5}[)〉]')


def counts(s):
    s = s or ''
    return (len(GREEK.findall(s)), len(LATIN.findall(s)),
            len(DIGIT.findall(s)), len(ROMAN.findall(s)))


def main():
    cand = json.load(open(CANDIDATES, encoding='utf-8'))
    want = {(r['key1'], r['subcard']): r for r in cand['rows']}
    store = impact.find_store(None)
    seen = {}
    child_tags = collections.Counter()
    keys = {r['key1'] for r in cand['rows']}
    with open(store, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            k1 = row.get('key1') or ''
            if k1 in keys:
                t = str(row.get('sense_tag') or '')
                if GREEK.search(t) or any(g in t for g in 'αβγδε'):
                    child_tags[(k1, t)] += 1
            k = (k1, row.get('subcard'))
            if k in want:
                seen[k] = row

    print('greek-suffixed sense_tags already in the store for these 7 keys: %d'
          % sum(child_tags.values()))
    print()
    hdr = ('%-22s %-5s %-14s  de(g/l/d/r)      ru(g/l/d/r)      len_de len_ru'
           % ('subcard', 'tag', 'review'))
    print(hdr)
    print('-' * len(hdr))
    mechanical = 0
    for k, r in sorted(want.items()):
        row = seen.get(k)
        if row is None:
            print('%-22s MISSING FROM STORE' % r['subcard'])
            continue
        de, ru = row.get('de') or '', row.get('ru') or ''
        cd, cr = counts(de), counts(ru)
        if cd[0] > 0 and cd[0] == cr[0]:
            mechanical += 1
        print('%-22s %-5s %-14s  %-16s %-16s %6d %6d'
              % (r['subcard'][:22], r['sense_tag'],
                 (row.get('review_status') or '')[:14],
                 '/'.join(map(str, cd)), '/'.join(map(str, cr)), len(de), len(ru)))
    print()
    print('rows whose ru carries the SAME number of greek markers as de: %d / %d'
          % (mechanical, len(want)))
    print()
    for k, r in sorted(want.items()):
        row = seen.get(k)
        if not row:
            continue
        print('== %s  tag=%s' % (r['subcard'], r['sense_tag']))
        print('   de: %s' % ' '.join((row.get('de') or '').split())[:300])
        print('   ru: %s' % ' '.join((row.get('ru') or '').split())[:300])
    return 0


if __name__ == '__main__':
    sys.exit(main())
