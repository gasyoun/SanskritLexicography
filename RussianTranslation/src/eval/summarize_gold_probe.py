#!/usr/bin/env python
"""summarize_gold_probe.py — human-readable digest of probe_gold_strata.py output.

H2401: the probe emits full JSON (every band x POS cell); this collapses it to the
tables the annotation protocol actually quotes, so the numbers in the protocol are
copied from a reproducible command rather than retyped by hand.

Usage: python summarize_gold_probe.py <probe_output.json>
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding='utf-8') as f:
        rep = json.load(f)

    for key in ('koch_standalone_entries', 'dcs_lemmas',
                'joined_candidates', 'glossable_candidates'):
        print(f'{key:28s} {rep[key]}')
    print(f'polysemy_buckets             {rep["polysemy_buckets"]}')

    print('\n--- band x POS cells (glossable >= 20) ---')
    print(f'{"band":>4} {"pos":<6} {"cand":>6} {"glossable":>10}')
    for c in rep['cells']:
        if c['glossable'] >= 20:
            print(f'{c["band"]:>4} {c["pos"]:<6} {c["candidates"]:>6} {c["glossable"]:>10}')

    small = [c for c in rep['cells'] if c['glossable'] < 20]
    print(f'\ncells below 20 glossable: {len(small)} '
          f'(total {sum(c["glossable"] for c in small)} lemmas) — merge or report')

    lp = rep.get('lexicon_presence')
    if lp:
        rate = lp['present'] / lp['probed'] if lp['probed'] else 0
        print(f'\n--- corpus_lexicon presence: {lp["present"]}/{lp["probed"]} '
              f'({rate:.1%}) ---')
        print(f'{"band":>4} {"pos":<6} {"probed":>7} {"present":>8} {"rate":>7}')
        for c in lp['by_cell']:
            if c['probed'] >= 20:
                print(f'{c["band"]:>4} {c["pos"]:<6} {c["probed"]:>7} '
                      f'{c["present"]:>8} {c["rate"]:>7.3f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
