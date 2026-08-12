#!/usr/bin/env python3
"""B2: which pool cards does PRODUCTION actually send as ONE whole-card call?

H2591's biggest stated non-equivalence is that its rig issues one whole-card call per arm
while production presplits six of those eight cards into the fragment lane. H2598 blocker
B2 asks for the premise to be re-checked before re-selecting, because B1 showed the two
"markup-heavy" cards failed by a non-zero CLI exit rather than by the model declining to
emit schema — so their density may be incidental.

This script answers the prior question the re-selection needs: **how large is the pool of
cards production takes whole?** It reuses the production predicate itself
(`gen_opt_harness2._presplit_hit`) rather than restating the thresholds, so the two can
never drift.

Read-only, offline, free. Makes no call and writes nothing unless --out is given.

    python b2_whole_card_pool.py [--input-dir DIR] [--out pool.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, PILOT)
sys.path.insert(0, os.path.dirname(HERE))

import gen_opt_harness2                                    # noqa: E402
import prep_context_compare as pcc                         # noqa: E402

H2591_KEYS = ('SvAsa', 'spfS', 'Srama', 'samIpa', 'vyavasTA', 'SudDi', 'rAtra', 'zoqaSan')


def classify(metrics: dict[str, dict]) -> dict[str, dict]:
    out = {}
    for key, value in metrics.items():
        cite_hit, sense_hit = gen_opt_harness2._presplit_hit(
            value['ls'], value['source_senses'], gen_opt_harness2.OUTPUT_BUDGET)
        out[key] = dict(value, cite_units=1 + value['ls'],
                        cite_hit=bool(cite_hit), sense_hit=bool(sense_hit),
                        whole_card=not (cite_hit or sense_hit))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', default=os.environ.get('PWG_INPUT_DIR')
                        or os.path.join(PILOT, 'input'))
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    metrics = pcc.pool_metrics(args.input_dir)
    table = classify(metrics)
    whole = sorted(k for k, v in table.items() if v['whole_card'])
    split = sorted(k for k, v in table.items() if not v['whole_card'])

    print('pool: %d distinct cards   whole-card in production: %d   presplit: %d'
          % (len(table), len(whole), len(split)))
    print('thresholds (read from the production module, not restated here): '
          'cite floor %s, sense budget %s'
          % (gen_opt_harness2.PRESPLIT_SOLO_CITE_FLOOR,
             gen_opt_harness2.SENSE_PRESPLIT_BUDGET))
    print('\n%-14s %7s %6s %6s %7s  %s' % ('key1', 'bytes', 'cite', 'senses', 'phold', 'lane'))
    for key in sorted(table, key=lambda k: (not table[k]['whole_card'],
                                            table[k]['cite_units'])):
        row = table[key]
        print('%-14s %7d %6d %6d %7d  %s%s'
              % (key, row['bytes'], row['cite_units'], row['source_senses'],
                 row['placeholders'], 'WHOLE' if row['whole_card'] else 'presplit',
                 '   <- H2591 sample' if key in H2591_KEYS else ''))

    inside = [k for k in H2591_KEYS if table.get(k, {}).get('whole_card')]
    print('\nH2591 sample cards production takes whole: %s (%d of 8)'
          % (', '.join(inside) or 'none', len(inside)))

    if args.out:
        with open(args.out, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump({'schema': 'pwg.b2_whole_card_pool.v1',
                       'cite_floor': gen_opt_harness2.PRESPLIT_SOLO_CITE_FLOOR,
                       'sense_budget': gen_opt_harness2.SENSE_PRESPLIT_BUDGET,
                       'pool_size': len(table), 'whole_card_keys': whole,
                       'presplit_keys': split,
                       'h2591_sample_whole_card': inside,
                       'cards': table}, handle, ensure_ascii=False, indent=1, sort_keys=True)
            handle.write('\n')
        print('wrote %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
