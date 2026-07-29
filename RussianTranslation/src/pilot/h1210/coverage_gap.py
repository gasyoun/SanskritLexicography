#!/usr/bin/env python
r"""H1210 — where arm A's coverage gap actually falls, by entry-length quartile.

Arm A completed 87 of the 100 selected cards: three of the ten size-bounded chunks
(06, 08, 09) never produced a `slice_result`, so their cards were never attempted. Because
`pack_chunks.py` packs by BYTES, a missing chunk is not a random 13 cards — it is a
contiguous band of the length distribution. That makes arm A's headline audit-clean %
non-comparable to arm B's head-to-head, and the direction of the bias is exactly the one
that flatters arm A (the long entries are where both arms degrade).

This script measures the gap instead of asserting it: it reports, per length quartile, how
many selected cards each arm attempted and which card ids arm A is missing. Read it
alongside `length_breakdown.py` — that one gives the per-quartile clean rates on what WAS
attempted, this one gives the denominators those rates rest on.

Usage:
  python src/pilot/h1210/coverage_gap.py \
      --arm-a-result src/pilot/h1210/arm_a.chunk*.slice_result.json \
      --arm-b-result src/pilot/h1210/arm_b.slice_result.json \
      --worklist src/pilot/h1210/H1210_ab100_worklist.28.07.26.json \
      --out src/pilot/h1210/H1210_coverage_gap.29.07.26.json
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from ab_report import card_id, load, merge_results          # noqa: E402  (one join contract)


def attempted_ids(paths):
    return {r['key1'] for r in merge_results(paths)['results']}


def quartiles(worklist):
    """Same cut as length_breakdown.py: quartiles over `bytes`, no_pwg as its own band."""
    byts = {card_id(r): r['bytes'] for r in worklist['detail']}
    sized = sorted((k for k in byts if byts[k] is not None), key=lambda k: byts[k])
    n = len(sized)
    bands = []
    for i in range(4):
        grp = sized[i * n // 4:(i + 1) * n // 4]
        bands.append(('Q%d (%d-%d B)' % (i + 1, byts[grp[0]], byts[grp[-1]]), grp))
    nb = [k for k in byts if byts[k] is None]
    if nb:
        bands.append(('no_pwg (no byte size)', nb))
    return bands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm-a-result', nargs='+', required=True)
    ap.add_argument('--arm-b-result', nargs='+', required=True)
    ap.add_argument('--worklist', required=True)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    worklist = load(a.worklist)
    A, B = attempted_ids(a.arm_a_result), attempted_ids(a.arm_b_result)

    rows, out_rows = [], []
    for label, grp in quartiles(worklist):
        miss = [k for k in grp if k not in A]
        rows.append((label, '%d/%d' % (len(grp) - len(miss), len(grp)),
                     '%d/%d' % (sum(1 for k in grp if k in B), len(grp)),
                     ', '.join(miss) or '-'))
        out_rows.append({'stratum': label, 'n_selected': len(grp),
                         'arm_a_attempted': len(grp) - len(miss),
                         'arm_b_attempted': sum(1 for k in grp if k in B),
                         'arm_a_missing': miss})

    md = ['| entry-length quartile | arm A attempted | arm B attempted | not attempted in arm A |',
          '|---|---:|---:|---|']
    md += ['| %s | %s | %s | %s |' % r for r in rows]
    print('\n'.join(md))

    if a.out:
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'schema': 'pwg.h1210_coverage_gap.v1',
                       'arm_a_attempted': len(A), 'arm_b_attempted': len(B),
                       'n_selected': worklist['n_selected'], 'rows': out_rows},
                      f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('\nwrote %s' % a.out)


if __name__ == '__main__':
    main()
