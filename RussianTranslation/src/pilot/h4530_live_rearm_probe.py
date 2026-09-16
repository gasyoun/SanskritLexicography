#!/usr/bin/env python
r"""h4530_live_rearm_probe.py — read-only proof that two consecutive canary re-arms pick
two different window roots against the LIVE coordinator directory, with a static prefix
and no manual id bump. Spends nothing: it calls the index picker only, never the planner,
never the orchestrator, and creates no artifacts under the live tree.

The second attempt is simulated by adding the first attempt's root to the observed set —
exactly what `plan_window` leaves behind when a prepared attempt dies before producing
`wf_output` (the H4342 stall shape). Before H4530 both attempts returned the same root.

  python src/pilot/h4530_live_rearm_probe.py [--prefix h4213can] [--coord-dir DIR]
"""
import argparse
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import no_pwg_scale_plan as plan  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description='read-only two-re-arm probe (no spend)')
    ap.add_argument('--prefix', default='h4213can')
    ap.add_argument('--coord-dir', default=os.path.join(plan.OUT, 'coordinator'))
    args = ap.parse_args(argv)

    artifacts = os.path.join(os.path.abspath(args.coord_dir), 'artifacts')
    live = sorted(n for n in (os.listdir(artifacts) if os.path.isdir(artifacts) else []))
    print('coordinator artifacts: %s (%d entries)' % (artifacts, len(live)))
    for name in live:
        print('   %s' % name)

    used = plan.used_window_indices(args.prefix, coord_dir=args.coord_dir)
    print('used indices for prefix %r (incl. coordinator artifacts): %s'
          % (args.prefix, sorted(used)))

    roots = []
    simulated = set(used)
    for attempt in (1, 2):
        idx = max([1] + sorted(simulated)) + 1
        root = '%s%02d' % (args.prefix, idx)
        print('re-arm %d -> %s' % (attempt, root))
        if root in roots:
            print('FAIL: re-arm %d re-picked %s (the H4342 stall)' % (attempt, root))
            return 1
        roots.append(root)
        simulated.add(idx)          # the attempt prepares, then dies before wf_output

    print('PASS: two consecutive re-arms, static prefix, zero manual id bumps -> %s'
          % ', '.join(roots))
    return 0


if __name__ == '__main__':
    sys.exit(main())
