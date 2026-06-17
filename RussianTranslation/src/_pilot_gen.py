#!/usr/bin/env python
"""Pre-generate pilot inputs: per richest-reuse a-headword, the microstructure
portrait(s) (JSON) + the raw German PWG body, so pilot agents read files instead
of each rebuilding the 1.09M-row corpus index.

Output: src/pilot/input/<key>.portrait.json + <key>.raw.txt  (gitignored data).
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import microstructure as M

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'input')

CARDS = ['arTa', 'agni', 'amfta', 'anna', 'aNga', 'akzara', 'anta', 'antarikza',
         'ap', 'anya', 'apara', 'arjuna', 'anaGa', 'antar', 'api']


def main():
    os.makedirs(OUT, exist_ok=True)
    want = set(CARDS)
    portraits = {k: [] for k in CARDS}
    raws = {k: [] for k in CARDS}
    for buf in pwg_mask.records():
        k1, k2, h = M.header(buf)
        if k1 in want:
            portraits[k1].append(M.portrait(buf))     # builds corpus index once (first call)
            raws[k1].append('\n'.join(buf[1:]))
    for k in CARDS:
        if not portraits[k]:
            print('  MISSING: %s' % k); continue
        json.dump(portraits[k], open(os.path.join(OUT, k + '.portrait.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        open(os.path.join(OUT, k + '.raw.txt'), 'w', encoding='utf-8').write(
            ('\n\n=== RECORD ===\n\n').join(raws[k]))
        ns = sum(len([s for s in p['senses'] if s['n'] != '0']) for p in portraits[k])
        print('  %-12s %d record(s), %d senses, corpus n=%s'
              % (k, len(portraits[k]), ns,
                 sum((p.get('corpus_synonyms') or {}).get('n', 0) for p in portraits[k])))
    print('wrote pilot inputs → %s' % OUT)


if __name__ == '__main__':
    main()
