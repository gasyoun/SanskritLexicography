#!/usr/bin/env python
r"""H1210 A/B — freeze a 40-card STRATIFIED SUBSET of the frozen 100-card worklist (H2787).

Why a subset rather than a fresh draw (MG, 15-08-2026, "redraw a 40-card slice and run both
arms"). Arm A measured at ~350k tokens/card on the full slice — ~35M for 100 cards — so the
100-card A/B does not fit one sitting. Cutting to 40 makes it fit, and drawing those 40 from
inside `H1210_ab100_worklist.28.07.26.json` rather than from the 43,968-head universe buys
two things a fresh draw would throw away:

  * arm B is already run over all 100 cards, so a subset needs NO new DeepSeek spend;
  * whatever arm-A cards have already completed and fall inside the 40 are reusable.

It also keeps the frame comparable: every stratum of the H1210 selection rule survives,
proportionally (S1 60->24, S2 15->6, S3 10->4, S4 10->4, S5 5->2), so the 40 is the same
instrument at 40% scale, not a different experiment.

Deterministic: cards are ordered as the frozen worklist ordered them and taken by an even
stride within each stratum. No RNG, no seed to record, byte-identical on re-run.

Usage:
  python src/pilot/h1210/select_ab40_subset.py [--n 40] [--date 15.08.26]
Writes: src/pilot/h1210/H1210_ab40_worklist.<date>.json  (committed, auditable)
        src/pilot/h1210/card_ids_ab40.txt                (LF, no CR — see FINDINGS §535)
"""
import argparse
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, 'H1210_ab100_worklist.28.07.26.json')

# The H1210 selection rule's own stratum sizes, and the 40-card cut of each. The worklist
# labels sub-strata (`S1_decile_7`, `S2_h920_sense_loss`, `S3_no_pwg`, …); we group on the
# `S<n>` prefix and stride WITHIN the group, which — because the rows keep worklist order,
# i.e. decile 1 … decile 10 — spreads the cut across every sub-stratum instead of eating
# the first few whole. Each decile of 6 therefore contributes 2 or 3 of the 24.
PLAN_100 = [('S1', 60), ('S2', 15), ('S3', 10), ('S4', 10), ('S5', 5)]


def stratum_group(row):
    """`S1_decile_7` -> `S1`; an unlabelled row -> `S?`."""
    return str(row.get('stratum') or 'S?').split('_')[0]


def stride_pick(rows, n):
    """`n` items spread evenly across `rows`, order preserved. Deterministic."""
    if n >= len(rows):
        return list(rows)
    if n <= 0:
        return []
    step = len(rows) / float(n)
    return [rows[int(i * step)] for i in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--worklist', default=DEFAULT_SRC)
    ap.add_argument('--card-ids', default=os.path.join(HERE, 'card_ids.txt'))
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--date', default='15.08.26')
    a = ap.parse_args()

    src = json.load(io.open(a.worklist, encoding='utf-8'))
    detail = src['detail']
    if len(detail) != src['n_selected']:
        raise SystemExit('worklist detail (%d) != n_selected (%d)'
                         % (len(detail), src['n_selected']))

    # The frozen card_ids.txt is ORDER-ALIGNED with `detail`, and it is the only place the
    # no-PWG sub-card ids (`…~~h0_zz_pw`) exist — they are not derivable from key1 alone.
    # Strip CR: these lists are CRLF on disk and a stray \r forks the id (FINDINGS §535).
    ids = [l.strip() for l in io.open(a.card_ids, encoding='utf-8') if l.strip()]
    if len(ids) != len(detail):
        raise SystemExit('card_ids (%d) != worklist detail (%d) — not order-aligned'
                         % (len(ids), len(detail)))
    for row, cid in zip(detail, ids):
        row = row.setdefault('card_id', cid)

    by_stratum = collections.OrderedDict()
    for row in detail:
        by_stratum.setdefault(stratum_group(row), []).append(row)

    total_100 = sum(n for _s, n in PLAN_100)
    chosen, plan = [], []
    for stratum, n100 in PLAN_100:
        rows = by_stratum.get(stratum, [])
        want = int(round(n100 * a.n / float(total_100)))
        take = stride_pick(rows, min(want, len(rows)))
        plan.append({'stratum': stratum, 'in_100': len(rows), 'wanted': want,
                     'taken': len(take),
                     'sub_strata': dict(collections.Counter(
                         r.get('stratum') for r in take))})
        chosen.extend(take)

    # Any stratum label the plan does not name (S? etc.) is carried only if we are short.
    if len(chosen) < a.n:
        rest = [r for s, rows in by_stratum.items() if s not in dict(PLAN_100)
                for r in rows]
        chosen.extend(stride_pick(rest, a.n - len(chosen)))
    chosen = chosen[:a.n]

    keys = [r['key1'] for r in chosen]
    chosen_ids = [r['card_id'] for r in chosen]
    out = {
        'schema': 'h1210.ab40_subset.v1',
        'handoff': 'H2787',
        'source_worklist': os.path.basename(a.worklist),
        'source_n': src['n_selected'],
        'selection_rule': ('proportional stratified subset of the frozen H1210 100-card '
                           'worklist; even stride within each stratum, worklist order '
                           'preserved; no RNG'),
        'n_selected': len(chosen),
        'strata_plan': plan,
        'keys': keys,
        'detail': chosen,
    }
    out_path = os.path.join(HERE, 'H1210_ab40_worklist.%s.json' % a.date)
    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write('\n')

    ids_path = os.path.join(HERE, 'card_ids_ab40.txt')
    with io.open(ids_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(chosen_ids) + '\n')

    print('wrote %s (%d cards)' % (out_path, len(chosen)))
    print('wrote %s' % ids_path)
    for p in plan:
        print('  %-3s in100=%-3d taken=%-3d %s'
              % (p['stratum'], p['in_100'], p['taken'],
                 ' '.join('%s:%d' % kv for kv in sorted(p['sub_strata'].items()))))


if __name__ == '__main__':
    main()
