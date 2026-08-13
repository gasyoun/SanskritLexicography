#!/usr/bin/env python3
"""Does H2612's GO survive the inspection that killed H2591's?

H2591's receipt fired GO on a +26.9 % wall margin that turned out to be mostly the
difference between how long each arm took to FAIL. The GO arithmetic cannot see that, so
the decomposition has to be run by hand every time — this script is that inspection, kept
next to the receipt rather than done once in a chat and forgotten.

It reports the margin three ways: as the receipt computes it (all calls), with failed calls
removed, and paired per unit over the units where BOTH arms returned schema — the only
comparison that is actually about translating the same group twice.

Read-only, offline, free.

    python decompose_margin.py [--run-dir run3]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))


def load(run_dir: str) -> list[dict]:
    rows = []
    for path in sorted(glob.glob(os.path.join(run_dir, 'envelopes', '*.json'))):
        with open(path, encoding='utf-8') as handle:
            rows.append(json.load(handle))
    return sorted(rows, key=lambda e: e['ordinal'])


def gain(baseline: float, prep: float) -> float | None:
    """Positive = PREP is better (less wall / fewer tokens), as the receipt defines it."""
    return None if not baseline else round((baseline - prep) / baseline, 4)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', default=os.path.join(HERE, 'run3'))
    args = parser.parse_args()

    rows = load(args.run_dir)
    by_arm = {'A': [e for e in rows if e['arm'] == 'A'],
              'B': [e for e in rows if e['arm'] == 'B']}

    def wall(items):
        return sum((e.get('wall_ms') or 0) for e in items) / 1000

    print('=== 1. as the receipt computes it (every call) ===')
    print('A %7.0f s   B %7.0f s   wall gain %+.2f %%'
          % (wall(by_arm['A']), wall(by_arm['B']),
             100 * (gain(wall(by_arm['A']), wall(by_arm['B'])) or 0)))

    produced = {arm: [e for e in items if e.get('result_sha256')]
                for arm, items in by_arm.items()}
    print('\n=== 2. failed calls removed (schema-bearing only) ===')
    print('A %7.0f s over %d call(s)   B %7.0f s over %d call(s)   wall gain %+.2f %%'
          % (wall(produced['A']), len(produced['A']),
             wall(produced['B']), len(produced['B']),
             100 * (gain(wall(produced['A']), wall(produced['B'])) or 0)))
    print('   NOTE: unequal call counts — this is a total, not a paired comparison.')

    both = sorted({e['key1'] for e in produced['A']} & {e['key1'] for e in produced['B']})
    index = {(e['key1'], e['arm']): e for e in rows}
    print('\n=== 3. PAIRED over the %d unit(s) where BOTH arms returned schema ===' % len(both))
    print('%-16s %9s %9s %9s  %s' % ('unit', 'A wall', 'B wall', 'delta', 'audited A/B'))
    a_total = b_total = 0.0
    signs = {'prep_faster': 0, 'prep_slower': 0}
    for unit in both:
        a, b = index[(unit, 'A')], index[(unit, 'B')]
        a_wall, b_wall = (a.get('wall_ms') or 0) / 1000, (b.get('wall_ms') or 0) / 1000
        a_total += a_wall
        b_total += b_wall
        signs['prep_faster' if b_wall < a_wall else 'prep_slower'] += 1
        print('%-16s %8.0fs %8.0fs %+8.0fs  %s/%s'
              % (unit, a_wall, b_wall, a_wall - b_wall,
                 (a.get('audit') or {}).get('audited'), (b.get('audit') or {}).get('audited')))
    paired = gain(a_total, b_total)
    print('%-16s %8.0fs %8.0fs %+8.0fs' % ('TOTAL', a_total, b_total, a_total - b_total))
    print('paired wall gain %+.2f %%   (PREP faster on %d of %d units, slower on %d)'
          % (100 * (paired or 0), signs['prep_faster'], len(both), signs['prep_slower']))

    print('\n=== verdict inspection ===')
    receipt_path = os.path.join(args.run_dir, 'comparison_receipt.json')
    if os.path.exists(receipt_path):
        with open(receipt_path, encoding='utf-8') as handle:
            receipt = json.load(handle)
        headline = receipt['deltas']['wall_ms_relative_gain']
        print('receipt margin %+.2f %% vs paired %+.2f %% — the GO rule needs > +10.00 %%'
              % (100 * headline, 100 * (paired or 0)))
        print('token axis: %+.2f %% (negative = PREP costs MORE)'
              % (100 * receipt['deltas']['non_cache_token_relative_gain']))
        print('audited cards lost by PREP: %s (negative = PREP gained)'
              % receipt['deltas']['audited_cards_lost_by_prep'])
        if paired is not None and (paired > 0.10) != (headline > 0.10):
            print('*** the paired margin CROSSES the threshold the headline margin sits on: '
                  'the GO does not survive decomposition ***')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
