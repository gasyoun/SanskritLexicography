#!/usr/bin/env python
r"""Daily R4.1 surveillance tick for ONE lane — spot-check, then halt rule (H2264).

H2175 built both halves of ruling R4.1 (``spot_check_daily.py`` samples 10% of a
day's auto-promoted cards; ``lane_guard.py`` evaluates >=2 sev-3 / any SAN-LOSS and
freezes + reverts) — but wired NEITHER to a trigger. H2246's dual-run compare found
them invoked only as ``--selftest`` in CI: the sole compensating control that makes
the auto-promote trial safe (ARCHITECTURE §3) could never fire. This module is that
trigger, as ONE definition the PC / prod / routine lanes all call, so the three
surfaces cannot drift into three different halt rules.

    tick = spot_check_daily (deterministic gates over what actually LANDED in the
           store, + optional judge pass) -> lane_guard (R4.1 verdict; freeze +
           revert the lane's unreviewed windows on a hit)

Exit codes are the operator contract:
    0  clean            — no sev-3 threshold breach, no SAN-LOSS; lane keeps running
    2  lane FROZEN      — R4.1 fired; nonstop_scheduler refuses this lane from now on
    1  could not judge  — the spot-check itself failed; INCONCLUSIVE, never "clean"

Exit 1 matters: a surveillance job that dies must not read as a pass. The caller
(Task Scheduler / systemd timer) should alert on 1 exactly as loudly as on 2.

``--execute`` forwards to lane_guard's store revert; without it the freeze verdict
is still recorded but the store is untouched (lane_guard's own dry-run default).
"""
import argparse
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

import data_root as dr                         # noqa: E402
import gate_evidence as ge                     # noqa: E402
import lane_guard                              # noqa: E402
import spot_check_daily as scd                 # noqa: E402

# A spotcheck report older than this no longer counts as live surveillance.
# 48h, not 24h: the job runs daily, so one missed run is tolerated, two is not.
SPOTCHECK_MAX_AGE_SECONDS = 48 * 3600


def spotcheck_path(telemetry_dir, date):
    return os.path.join(telemetry_dir, 'spotcheck_%s.json' % date)


def fresh_spotcheck(telemetry_dir, now=None, max_age=SPOTCHECK_MAX_AGE_SECONDS,
                    evidence_path=None):
    """Path of the newest spotcheck report still inside the freshness window, else
    None. Pure filesystem read — nonstop_scheduler uses this to fail CLOSED on
    auto-promote when R4.1 surveillance is not actually running.

    W1 (H3748, #1803 C2-2): the predicate is unchanged — it is still a filename prefix
    and an mtime, and it still accepts a 0-byte or truncated report, which is the live
    half of C2-2 and stays filed. What is new is the evidence sidecar
    :func:`fresh_spotcheck_evidence` builds: every candidate is named, sized and hashed,
    so a report this gate blessed **without reading a byte of it** is now visible as a
    0-byte input with a warning, instead of vanishing behind a returned path.
    """
    path, ev = fresh_spotcheck_evidence(telemetry_dir, now=now, max_age=max_age)
    ev.emit(evidence_path or ge.default_sidecar('lane_spotcheck_freshness'))
    return path


def fresh_spotcheck_evidence(telemetry_dir, now=None, max_age=SPOTCHECK_MAX_AGE_SECONDS):
    """(fresh_path_or_None, GateEvidence) — the freshness answer plus what produced it.

    Verdict vocabulary follows this module's own exit-code contract: a fresh report is
    ``pass``; **no candidate at all is ``inconclusive``, never a pass** — "a surveillance
    job that dies must not read as a pass". So this gate has no legitimately-empty input
    class, and a declared-empty PASS here would launder a refusal into a green light.
    """
    now = time.time() if now is None else now
    ev = ge.GateEvidence('lane_spotcheck_freshness',
                         'R4.1 surveillance freshness window (C2-2)')
    best = None
    try:
        names = sorted(os.listdir(telemetry_dir))
    except OSError:
        names = []
        ev.add_input('telemetry_dir', path=telemetry_dir, units=0, exists=False)
    candidates = 0
    for name in names:
        if not (name.startswith('spotcheck_') and name.endswith('.json')):
            continue
        path = os.path.join(telemetry_dir, name)
        try:
            age = now - os.path.getmtime(path)
        except OSError:
            continue
        candidates += 1
        # Hashing here is the whole point: the predicate below reads only the mtime,
        # so without this the record could not say WHICH bytes were blessed.
        ev.add_input('spotcheck:%s' % name, path=path, units=1)
        ev.note('age_seconds:%s' % name, int(age))
        if age <= max_age and (best is None or age < best[0]):
            best = (age, path)
    ev.add_predicate('within_freshness_window', evaluations=candidates,
                     hits=candidates - (1 if best else 0))
    ev.note('max_age_seconds', max_age)
    ev.note('fresh_report', os.path.basename(best[1]) if best else None)
    ev.note('surveillance_live', bool(best))
    ev.set_verdict('pass' if best else 'inconclusive')
    ev.assert_nonvacuous()
    return (best[1] if best else None), ev


def tick(lane, data_root, date=None, fraction=0.10, judge_cmd=None, execute=False,
         store=None):
    """One surveillance tick. Returns (exit_code, spotcheck_path, frozen: bool)."""
    telemetry = dr.resolve(data_root, 'telemetry_dir')
    gatelogs = dr.resolve(data_root, 'gatelogs_dir')
    records = dr.resolve(data_root, 'manifests_dir')
    date = date or scd.utc_date(time.time())

    argv = ['--date', date, '--fraction', str(fraction),
            '--records-dir', records, '--out-dir', telemetry]
    if judge_cmd:
        argv += ['--judge-cmd', judge_cmd]
    if store:
        argv += ['--store', store]
    try:
        scd.main(argv)            # 0 clean, 1 = R4.1 inputs non-clean (not an error)
    except SystemExit as exc:     # argparse/refusal paths
        if exc.code not in (0, 1):
            print('spot-check FAILED to run (code %s) — INCONCLUSIVE, not clean'
                  % exc.code, file=sys.stderr)
            return 1, None, False
    except Exception as exc:      # noqa: BLE001 — a dead surveillance job is not a pass
        print('spot-check raised %s: %s — INCONCLUSIVE, not clean'
              % (type(exc).__name__, exc), file=sys.stderr)
        return 1, None, False

    report = spotcheck_path(telemetry, date)
    if not os.path.exists(report):
        print('spot-check wrote no report for %s — INCONCLUSIVE' % date, file=sys.stderr)
        return 1, None, False

    ns = argparse.Namespace(lane=lane, spotcheck=report, freeze_dir=gatelogs,
                            records_dir=records, store=store, execute=execute)
    code = lane_guard.run(ns)     # 0 = no freeze, 2 = frozen
    return (2, report, True) if code == 2 else (0, report, False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lane', help='pc | prod | routine')
    dr.add_arg(ap)
    ap.add_argument('--date', default=None, help='UTC date (default: today)')
    ap.add_argument('--fraction', type=float, default=0.10, help='R4.1 sample = 10%%')
    ap.add_argument('--judge-cmd', default=None,
                    help='forwarded to spot_check_daily (the stylistic net; absent '
                         'runs the deterministic half only)')
    ap.add_argument('--store', default=None)
    ap.add_argument('--execute', action='store_true',
                    help='let lane_guard perform the store revert on a freeze')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.lane and args.data_root):
        ap.error('--lane and --data-root are required (unless --selftest)')
    dr.apply(args.data_root, ensure_dirs=True)
    code, report, frozen = tick(args.lane, args.data_root, date=args.date,
                                fraction=args.fraction, judge_cmd=args.judge_cmd,
                                execute=args.execute, store=args.store)
    print('lane %s surveillance tick: exit=%d frozen=%s report=%s'
          % (args.lane, code, frozen, report))
    return code


def selftest():
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        dr.apply(td, ensure_dirs=True)
        telemetry = dr.resolve(td, 'telemetry_dir')
        manifests = dr.resolve(td, 'manifests_dir')
        gatelogs = dr.resolve(td, 'gatelogs_dir')
        now = int(time.time())
        date = scd.utc_date(now)
        store = os.path.join(td, 'store.jsonl')

        def write_store(rows):
            with open(store, 'w', encoding='utf-8', newline='\n') as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')

        # (1) a clean day: promoted card present and well-formed -> exit 0, no freeze
        scd._mk_promotion(manifests, 'wOK', ['r~~a'], now)
        write_store([{'subcard': 'r~~a', 'ru': 'перевод', 'h': 'r', 'grammar': 'n',
                      'layer': 'pwg', 'review_status': 'ai_translated'}])
        code, report, frozen = tick('pc', td, date=date, fraction=1.0, store=store)
        assert code == 0 and not frozen, (code, frozen)
        assert os.path.exists(report) and not lane_guard.frozen(gatelogs, 'pc')

        # (2) the acceptance case: inject 2 sev-3 defects -> lane FROZEN, exit 2
        scd._mk_promotion(manifests, 'wBAD', ['r~~b', 'r~~c'], now)
        write_store([
            {'subcard': 'r~~a', 'ru': 'перевод', 'h': 'r', 'grammar': 'n',
             'layer': 'pwg', 'review_status': 'ai_translated'},
            {'subcard': 'r~~b', 'ru': 'SAN-LOSS', 'h': 'r', 'grammar': 'n',
             'layer': 'pwg', 'review_status': 'ai_translated'},
            {'subcard': 'r~~c', 'ru': '', 'h': 'r', 'grammar': 'n',
             'layer': 'pwg', 'review_status': 'ai_translated'},
        ])
        code2, report2, frozen2 = tick('pc', td, date=date, fraction=1.0, store=store)
        assert code2 == 2 and frozen2, (code2, frozen2)
        assert lane_guard.frozen(gatelogs, 'pc')
        # per-lane by construction: a sibling lane is untouched by pc's freeze
        assert not lane_guard.frozen(gatelogs, 'prod')

        # (3) freshness helper: the report just written IS live surveillance...
        assert fresh_spotcheck(telemetry) == report2 or \
            os.path.basename(fresh_spotcheck(telemetry)).startswith('spotcheck_')
        # ...and the same report goes stale once it ages past the window
        assert fresh_spotcheck(telemetry, now=time.time() + 72 * 3600) is None
        # an absent telemetry dir is "no surveillance", not a crash
        assert fresh_spotcheck(os.path.join(td, 'nope')) is None
    print('lane_spotcheck_tick selftest: PASS (clean day exit 0; 2 sev-3 -> FROZEN '
          'exit 2 with per-lane isolation; freshness window incl. stale + absent)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
