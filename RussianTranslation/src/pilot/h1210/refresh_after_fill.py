#!/usr/bin/env python
r"""H1846 — one command for the post-fill refresh of the H1210 A/B.

Arm A originally ran 87 of 100 cards; chunks 06/08/09 never produced a `slice_result`
(FINDINGS §500). Once those three Workflow runs land, every downstream artifact has to be
recomputed **together** — collecting a chunk without re-running the canonical audit, or
re-running the audit without refreshing `coverage_gap`, is exactly how a stale denominator
survives into a report. So this script does the whole chain or nothing:

  1. collect_arm_a.py for each newly-run chunk (task-output JSON -> slice_result)
  2. refresh arm_a.telemetry.json across ALL chunk task-outputs
  3. h1209/canonical_audit.py over all ten arm_a.chunk*.slice_result.json
  4. ab_report.py / length_breakdown.py / coverage_gap.py with a NEW date stamp

The 29-07 (87-card) artifacts are never overwritten: they are the evidence behind
FINDINGS §500 and issue #863, and must stay reproducible. New outputs carry their own date.

Usage:
  python src/pilot/h1210/refresh_after_fill.py --date 29.07.26b \
      --chunk chunk06=<task_output.json> --chunk chunk08=<...> --chunk chunk09=<...>
  (--chunk may be omitted entirely to just recompute from slice_results already on disk)
"""
import argparse
import glob
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(HERE)
RT = os.path.dirname(os.path.dirname(PILOT))
PY = sys.executable


def run(args, label):
    print('\n=== %s ===' % label)
    r = subprocess.run([PY] + args, cwd=RT, encoding='utf-8',
                       capture_output=True)
    sys.stdout.write(r.stdout or '')
    if r.returncode != 0:
        sys.stdout.write(r.stderr or '')
        sys.exit('FAIL (%s): exit %d' % (label, r.returncode))
    return r.stdout or ''


def rel(p):
    return os.path.relpath(p, RT).replace('\\', '/')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True, help='stamp for the new artifacts, e.g. 29.07.26b')
    ap.add_argument('--chunk', action='append', default=[],
                    help='chunkNN=<task_output.json>, repeatable')
    a = ap.parse_args()

    for spec in a.chunk:
        tag, _, out = spec.partition('=')
        if not out or not os.path.exists(out):
            sys.exit('FAIL: task output not found for %s: %r' % (tag, out))
        run([rel(os.path.join(HERE, 'collect_arm_a.py')), tag, out], 'collect %s' % tag)

    run([rel(os.path.join(HERE, 'collect_arm_a.py')), '--telemetry-out',
         rel(os.path.join(HERE, 'arm_a.telemetry.json'))], 'refresh arm A telemetry')

    slices = sorted(glob.glob(os.path.join(HERE, 'arm_a.chunk*.slice_result.json')))
    print('\narm A slice_results on disk: %d' % len(slices))
    if len(slices) < 10:
        print('WARN: fewer than ten chunks present — the coverage table below will say so')

    audit = os.path.join(HERE, 'arm_a.canonical_audit.%s.json' % a.date)
    run([rel(os.path.join(PILOT, 'h1209', 'canonical_audit.py'))]
        + [rel(p) for p in slices]
        + [rel(os.path.join(HERE, 'h1210_ab100.manifest.json')), '--out', rel(audit)],
        'canonical audit (all arm-A chunks)')

    worklist = rel(os.path.join(HERE, 'H1210_ab100_worklist.28.07.26.json'))
    arm_b_audit = rel(os.path.join(HERE, 'arm_b.canonical_audit.json'))

    run([rel(os.path.join(HERE, 'ab_report.py')),
         '--arm-a-result'] + [rel(p) for p in slices]
        + ['--arm-a-audit', rel(audit),
           '--arm-a-telemetry', rel(os.path.join(HERE, 'arm_a.telemetry.json')),
           '--arm-b-result', rel(os.path.join(HERE, 'arm_b.slice_result.json')),
           '--arm-b-audit', arm_b_audit,
           '--arm-b-telemetry', rel(os.path.join(HERE, 'arm_b.telemetry.json')),
           '--worklist', worklist,
           '--out-prefix', rel(os.path.join(HERE, 'H1210_AB_RESULTS.%s' % a.date))],
        'comparative report')

    run([rel(os.path.join(HERE, 'length_breakdown.py')),
         '--arm-a-audit', rel(audit), '--arm-b-audit', arm_b_audit,
         '--worklist', worklist,
         '--out', rel(os.path.join(HERE, 'H1210_length_breakdown.%s.json' % a.date))],
        'length-quartile breakdown')

    run([rel(os.path.join(HERE, 'coverage_gap.py')),
         '--arm-a-result'] + [rel(p) for p in slices]
        + ['--arm-b-result', rel(os.path.join(HERE, 'arm_b.slice_result.json')),
           '--worklist', worklist,
           '--out', rel(os.path.join(HERE, 'H1210_coverage_gap.%s.json' % a.date))],
        'coverage gap')

    print('\nDONE — new artifacts stamped %s; the 29.07.26 (87-card) set is untouched.' % a.date)


if __name__ == '__main__':
    main()
