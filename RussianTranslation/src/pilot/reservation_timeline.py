"""Difference the call-reservation ledger's `time_ns` stamps into a per-call timeline.

Why this exists
---------------
H2056 Q2 observed that `call_reservation.py` persists wall `time.time_ns()` stamps that
**nothing differences**. That gap matters precisely for the calls you most need to explain:
a call with no CLI envelope finalizes through `unevaluable_telemetry()`, which carries no
`duration_ms` at all, so an unevaluable call has its duration recorded *nowhere else*. Wall
`reserved_at_ns` -> `finalized_at_ns` is the only surviving signal, and differencing it is
what separates "hung to the ceiling" from "failed fast" -- two conditions with opposite
remedies that are otherwise indistinguishable in every artifact the run leaves behind.

It was written after a medium50 window recorded 12 unevaluable calls in 16: differencing the
stamps put every one of them at 180 04x-180 23x ms against `HARD_TIMEOUT_MS = 180000`, i.e.
a hard-timeout wall rather than the rate-limit hang of FINDINGS 270 or a content failure.
Nothing in the wf output, the status file or the usage summary showed that.

Read-only; it opens the ledger and prints. Usage:

    python src/pilot/reservation_timeline.py <ledger.json> [run_id]

`run_id` defaults to the lexically last run in the file.
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

HEADER = '%-4s %-18s %-26s %-9s %9s %9s %9s %10s'
EVALUABLE_LABEL = {True: 'yes', False: 'NO', None: 'in-flight'}


def load_run(path, run_id=None):
    with open(path, encoding='utf-8') as handle:
        data = json.load(handle)
    runs = data.get('runs') or {}
    if not runs:
        raise SystemExit('ledger has no runs: %s' % path)
    if run_id is None:
        run_id = sorted(runs)[-1]
    if run_id not in runs:
        raise SystemExit('run_id %r not in ledger (have: %s)' % (run_id, ', '.join(sorted(runs))))
    return run_id, runs[run_id]


def wall_ms(row):
    start, end = row.get('reserved_at_ns'), row.get('finalized_at_ns')
    if not start or not end:
        return None
    return (end - start) // 1_000_000


def report(run_id, run):
    rows = run.get('reservations') or []
    print('run_id      : %s' % run_id)
    print('max_calls   : %s' % run.get('max_calls'))
    print('reservations: %d' % len(rows))
    print()
    print(HEADER % ('#', 'purpose', 'detail', 'evaluable', 'wall_ms', 'dur_ms', 'api_ms', 'usd'))
    print('-' * 104)

    buckets = {True: [], False: []}
    subagent_total = 0
    for row in rows:
        tel = row.get('telemetry') or {}
        evaluable = tel.get('cost_evaluable')
        wall = wall_ms(row)
        if wall is not None and evaluable is not None:
            buckets[bool(evaluable)].append(wall)
        subagent_total += tel.get('subagent_tokens') or 0
        cost = tel.get('observed_cost_usd')
        print(HEADER % (
            row.get('ordinal'),
            (row.get('purpose') or '')[:18],
            (row.get('detail') or '')[:26],
            EVALUABLE_LABEL[evaluable],
            wall if wall is not None else '-',
            tel.get('duration_ms') or '-',
            tel.get('duration_api_ms') or '-',
            ('%.4f' % cost) if cost else '-',
        ))

    print()
    for flag, label in ((True, 'evaluable'), (False, 'UNEVALUABLE')):
        vals = sorted(buckets[flag])
        if vals:
            print('%-12s n=%-3d min=%6d  median=%6d  max=%6d ms'
                  % (label, len(vals), vals[0], vals[len(vals) // 2], vals[-1]))

    finalized = len(buckets[True]) + len(buckets[False])
    print()
    print('unevaluable calls : %d of %d finalized' % (len(buckets[False]), finalized))
    print('subagent tokens   : %d total' % subagent_total)
    usage = run.get('usage') or {}
    print('recorded floor    : $%.4f  (cost_evaluable=%s)'
          % (usage.get('observed_cost_usd') or 0, usage.get('cost_evaluable')))
    if buckets[False]:
        print()
        print('NOTE: the recorded cost is a FLOOR. Each unevaluable call was a real paid spawn')
        print('      that produced no envelope, so it contributes 0 to the total (issue #949).')


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    run_id, run = load_run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    report(run_id, run)


if __name__ == '__main__':
    main()
