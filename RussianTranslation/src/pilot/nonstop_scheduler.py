#!/usr/bin/env python
r"""Nonstop lane scheduler — ONE tick per invocation (H2175 step 9).

The idle-time fix: an external timer (Windows Task Scheduler on the PC lane,
systemd timer on samskrte.ru) fires this hourly. A tick is:

    frozen? -> skip (lane_guard freeze file; other lanes unaffected)
    paused? -> skip (quota-hang pause until the next weekly reset)
    live gate (health probe, fallback roster c4->c1->c5->c6 per R5.1) -> NO-GO? skip
    canary receipt fresh?           -> absent/stale? run --canary-cmd or skip
    weekly cost ceiling (R3.2)      -> exhausted? skip until reset
    auto-promote only: fresh R4.1 spotcheck? -> absent? REFUSE the window (H2264:
                    the halt rule is auto-promote's safety case, so a lane may not
                    promote unsupervised; lanes without --auto-promote-until skip
                    this gate entirely)
    bounded window (--execute --auto-promote-until ..., H2157 ceilings, H2159
                    canary receipt; the headless machinery keeps the H2158
                    bare-cwd rule — this module NEVER overrides the CLI cwd)
    quota-hang classification (§270) -> hang? write pause-until-reset
    telemetry: append the tick record; git commit+push the data root (best effort)

EVERY branch appends a tick record to telemetry/scheduler_ticks_<lane>.jsonl —
"≥95% of eligible ticks produced a window or a recorded pause reason" is measured
from this ledger, so an unexplained idle tick is a bug by construction.

All side-effecting steps are injectable callables (see Runners) so the selftest
drives the full tick state machine with zero live calls. Kill-ceiling policy and
the health-gate authoritative number are open @DECIDEs (02-08-2026): this module
deliberately inherits current gate behavior unchanged and encodes no new numbers.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

import data_root as dr                     # noqa: E402
import lane_guard                          # noqa: E402
import lane_spotcheck_tick                 # noqa: E402
import profile_lane                        # noqa: E402

SCHEMA = 'pwg.scheduler_tick.v1'

# R5.1 (MG 02-08-2026): the profile fallback roster, in ruling order.
# Overridable without code edits (MG 24-08-2026): $PWG_PROFILE_ROSTER=c1,c4 sets
# the order outright; $PWG_PROFILE_SLOT=c1 rotates the active slot to the front.
DEFAULT_ROSTER = ('c4', 'c1', 'c5', 'c6')


def effective_roster(cfg=None, env=None):
    """Config roster → profile_lane knob ($PWG_PROFILE_ROSTER / active slot) → R5.1 default."""
    cfg = cfg or {}
    return (cfg.get('roster')
            or profile_lane.active_roster(env=env, default_roster=DEFAULT_ROSTER)
            or DEFAULT_ROSTER)

# §270: a reservation-ledger row with wall clock at/over this and NO api duration
# is the hang signature (observed cluster 180 04x-180 23x ms at the 180 s kill).
HANG_WALL_MS = 175_000

CANARY_MAX_AGE_SECONDS = 6 * 3600          # canary_gate.DEFAULT_MAX_AGE_SECONDS


def now_epoch():
    return time.time()


def next_weekly_reset(now, day='MON', hour=0):
    """Epoch of the next weekly reset (UTC). day: MON..SUN, hour: 0-23."""
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    target = days.index(day.upper())
    t = time.gmtime(now)
    ahead = (target - t.tm_wday) % 7
    base = time.mktime((t.tm_year, t.tm_mon, t.tm_mday, hour, 0, 0, 0, 0, 0)) \
        - (time.timezone if not t.tm_isdst else time.altzone) + ahead * 86400
    # mktime is local-time; rebuild in UTC via calendar
    import calendar
    base = calendar.timegm((t.tm_year, t.tm_mon, t.tm_mday, hour, 0, 0, 0, 0, 0)) \
        + ahead * 86400
    if base <= now:
        base += 7 * 86400
    return base


def iso_week(ts):
    t = time.gmtime(ts)
    y, w, _ = time.strftime('%G %V %u', t).split()
    return '%s-W%s' % (y, w)


def pause_path(gatelogs_dir, lane):
    return os.path.join(gatelogs_dir, 'lane_pause_%s.json' % lane)


def paused_until(gatelogs_dir, lane):
    try:
        rec = json.load(open(pause_path(gatelogs_dir, lane), encoding='utf-8'))
        return float(rec.get('until_epoch') or 0), rec.get('reason')
    except (OSError, ValueError):
        return 0.0, None


def write_pause(gatelogs_dir, lane, until_epoch, reason):
    os.makedirs(gatelogs_dir, exist_ok=True)
    p = pause_path(gatelogs_dir, lane)
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'schema': 'pwg.lane_pause.v1', 'lane': lane,
                   'until_epoch': until_epoch, 'reason': reason,
                   'written_at': int(now_epoch())}, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, p)
    return p


def classify_quota_hang(ledger_rows):
    """§270 signature over call-reservation rows: any finalized call whose wall clock
    sits at/over the kill ceiling with NO api duration recorded. Pure."""
    for row in ledger_rows or []:
        reserved = row.get('reserved_at_ns')
        finalized = row.get('finalized_at_ns')
        if reserved is None or finalized is None:
            continue
        wall_ms = (finalized - reserved) / 1e6
        env = row.get('telemetry') or {}
        if wall_ms >= HANG_WALL_MS and not env.get('duration_api_ms') \
                and not env.get('duration_ms'):
            return True
    return False


def week_spend(tick_ledger_path, week):
    """Sum of observed window costs recorded by THIS lane's ticks in the ISO week."""
    total = 0.0
    if not os.path.exists(tick_ledger_path):
        return total
    with open(tick_ledger_path, encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get('week') == week and rec.get('window_cost_usd'):
                total += float(rec['window_cost_usd'])
    return total


def append_tick(tick_ledger_path, record):
    os.makedirs(os.path.dirname(tick_ledger_path), exist_ok=True)
    with open(tick_ledger_path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')


class Runners:
    """Injectable side-effecting steps; production defaults spawn the real tools."""

    def __init__(self, cfg):
        self.cfg = cfg

    def gate_probe(self, profile):
        """(go: bool, detail). Production: h963_c4_gate0_probe.py exit 0 == GO."""
        cmd = [sys.executable, os.path.join(HERE, 'h963_c4_gate0_probe.py'),
               '--account', profile]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                              timeout=self.cfg.get('gate_timeout', 900))
        return proc.returncode == 0, (proc.stdout or '')[-400:]

    def canary_receipt(self, profile):
        """Path of a fresh GO receipt for the profile, or None. Production: reuse a
        fresh receipt from gatelogs/, else run --canary-cmd when configured."""
        path = os.path.join(self.cfg['gatelogs_dir'],
                            'canary_receipt_%s.json' % profile)
        try:
            rec = json.load(open(path, encoding='utf-8'))
            age = now_epoch() - float(rec.get('judged_at_epoch') or 0)
            if rec.get('verdict') == 'GO' and age <= CANARY_MAX_AGE_SECONDS:
                return path
        except (OSError, ValueError):
            pass
        canary_cmd = self.cfg.get('canary_cmd')
        if canary_cmd:
            cmd = canary_cmd.replace('{profile}', profile).replace('{receipt}', path)
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                  encoding='utf-8',
                                  timeout=self.cfg.get('canary_timeout', 1800))
            if proc.returncode == 0 and os.path.exists(path):
                return path
        return None

    def bounded_run(self, profile, receipt, remaining_budget):
        """(exit_code, window_cost_usd, ledger_rows). Production: bounded_staged_run
        --execute with the H2157 ceilings + H2159 receipt + auto-promote trial."""
        cfg = self.cfg
        checkpoint = os.path.join(cfg['manifests_dir'],
                                  'sched_%s.checkpoint.json' % cfg['lane'])
        cmd = [sys.executable, os.path.join(HERE, 'bounded_staged_run.py'),
               '--plan', cfg['plan'], '--data-root', cfg['data_root'],
               '--coordinator', os.path.join(HERE, 'coordinator.py'),
               '--cwd', HERE, '--events',
               os.path.join(cfg['gatelogs_dir'], 'sched_%s.events.jsonl' % cfg['lane']),
               '--checkpoint', checkpoint,
               '--execute', '--only-profile', profile,
               '--max-windows', '1',
               '--max-calls', str(cfg.get('max_calls', 40)),
               '--cost-ceiling', '%.4f' % remaining_budget,
               '--canary-receipt', receipt]
        if cfg.get('auto_promote_until'):
            cmd += ['--auto-promote-until', cfg['auto_promote_until']]
        else:
            cmd += ['--stop-before-promote']
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                              timeout=cfg.get('window_timeout', 4 * 3600))
        cost, rows = 0.0, []
        try:
            ledger = json.load(open(checkpoint + '.calls.json', encoding='utf-8'))
            rows = ledger.get('calls') or []
            for row in rows:
                usage = (row.get('telemetry') or {})
                if usage.get('observed_cost_usd'):
                    cost += float(usage['observed_cost_usd'])
        except (OSError, ValueError):
            pass
        return proc.returncode, cost, rows

    def commit_telemetry(self, message):
        """git add/commit/push the data root; best-effort (offline tick still counts)."""
        root = self.cfg['data_root']
        try:
            subprocess.run(['git', '-C', root, 'add', '-A'], capture_output=True,
                           text=True, encoding='utf-8', timeout=300)
            subprocess.run(['git', '-C', root, 'commit', '-m', message],
                           capture_output=True, text=True, encoding='utf-8', timeout=300)
            push = subprocess.run(['git', '-C', root, 'push'], capture_output=True,
                                  text=True, encoding='utf-8', timeout=600)
            return push.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False


def tick(cfg, runners):
    """One scheduler tick. Returns the appended tick record (every branch records)."""
    lane = cfg['lane']
    started = now_epoch()
    record = {'schema': SCHEMA, 'lane': lane, 'tick_id': uuid.uuid4().hex[:12],
              'ts': int(started), 'week': iso_week(started), 'verdict': None}
    ledger_path = os.path.join(cfg['telemetry_dir'],
                               'scheduler_ticks_%s.jsonl' % lane)

    def done(verdict, reason=None, **extra):
        record['verdict'] = verdict
        if reason:
            record['reason'] = reason
        record.update(extra)
        record['elapsed_s'] = round(now_epoch() - started, 1)
        append_tick(ledger_path, record)
        runners.commit_telemetry('telemetry(%s): tick %s %s'
                                 % (lane, record['tick_id'], verdict))
        return record

    # 1. frozen lane (R4.1) — other lanes' schedulers are untouched by this file
    if lane_guard.frozen(cfg['gatelogs_dir'], lane):
        return done('skip', 'lane_frozen (lane_guard R4.1; unfreeze is a human act)')
    # 2. quota-hang pause until the weekly reset
    until, why = paused_until(cfg['gatelogs_dir'], lane)
    if until > started:
        return done('skip', 'paused_until_reset', paused_until=int(until),
                    pause_reason=why)
    # Steps 3-7 all spawn subprocesses with timeouts. H2246: a raised runner exception
    # (subprocess.TimeoutExpired above all — the EXPECTED outcome of the very CLI-hang
    # class this module exists to detect, and of the 4h window timeout) used to escape
    # tick() before any append_tick(), so the ledger recorded NOTHING and the tick became
    # exactly the "unexplained idle tick" the module's contract calls a bug by
    # construction. The ≥95% acceptance metric is computed from this ledger, so an
    # unrecorded crash silently inflated it. Record, then let the verdict speak.
    try:
        # 3. live gate with the R5.1 fallback roster
        profile = None
        gate_trail = []
        for slot in effective_roster(cfg):
            go, detail = runners.gate_probe(slot)
            gate_trail.append({'profile': slot, 'go': go})
            if go:
                profile = slot
                break
        record['gate_trail'] = gate_trail
        if not profile:
            return done('skip', 'live_gate_no_go_all_roster')
        record['profile'] = profile
        # 4. canary receipt (H2159 — consumed mechanically by the bounded run too)
        receipt = runners.canary_receipt(profile)
        if not receipt:
            return done('skip', 'no_fresh_canary_receipt')
        # 5. weekly cost ceiling (R3.2: the week is the only wall)
        ceiling = float(cfg.get('weekly_cost_ceiling') or 0)
        spent = week_spend(ledger_path, record['week'])
        remaining = ceiling - spent
        if remaining <= 0:
            return done('skip', 'weekly_cost_ceiling_exhausted', week_spent_usd=spent)
        # 5b. H2264: auto-promote may only run while R4.1 surveillance is LIVE.
        # Auto-promote's whole safety case (ARCHITECTURE §3) is the daily spot-check
        # + halt rule; H2246 found that chain had no trigger at all, so the trial
        # could have promoted into the store with zero defect surveillance. Fail
        # CLOSED: no fresh spotcheck report -> no auto-promoting window. A lane
        # running WITHOUT --auto-promote-until is unaffected (nothing promotes, so
        # there is nothing to survey) and keeps ticking normally.
        if cfg.get('auto_promote_until'):
            fresh = lane_spotcheck_tick.fresh_spotcheck(cfg['telemetry_dir'])
            if not fresh:
                return done('skip', 'no_fresh_spotcheck_auto_promote_refused',
                            hint='run lane_spotcheck_tick.py --lane %s daily; '
                                 'auto-promote is gated on live R4.1 surveillance'
                                 % lane)
            record['spotcheck'] = os.path.basename(fresh)
        # 6. the bounded window
        code, cost, rows = runners.bounded_run(profile, receipt, remaining)
        record['window_exit'] = code
        record['window_cost_usd'] = cost
        # 7. §270 quota-hang classification -> pause until the next weekly reset
        if code != 0 and classify_quota_hang(rows):
            reset = next_weekly_reset(started, cfg.get('reset_day', 'MON'),
                                      cfg.get('reset_hour', 0))
            write_pause(cfg['gatelogs_dir'], lane, reset, 'quota_hang (§270 signature)')
            return done('window_failed', 'quota_hang_pause_written',
                        paused_until=int(reset))
        return done('window' if code == 0 else 'window_failed',
                    None if code == 0 else 'bounded_run_exit_%d' % code)
    except subprocess.TimeoutExpired as exc:
        # A timed-out probe/canary/window is a RECORDED failure, never a silent gap.
        return done('window_failed', 'runner_timeout',
                    failed_step=_step_of(exc), timeout_s=getattr(exc, 'timeout', None))
    except Exception as exc:                      # noqa: BLE001 — record, never vanish
        return done('window_failed', 'runner_exception',
                    exception='%s: %s' % (type(exc).__name__, str(exc)[:300]))


def _step_of(exc):
    """Best-effort name of the tool whose subprocess timed out (for the tick record)."""
    cmd = getattr(exc, 'cmd', None)
    text = ' '.join(cmd) if isinstance(cmd, (list, tuple)) else str(cmd or '')
    for needle, step in (('h963_c4_gate0_probe', 'live_gate'),
                         ('bounded_staged_run', 'bounded_window')):
        if needle in text:
            return step
    return 'canary_or_unknown'


def build_cfg(args):
    root = os.path.abspath(args.data_root)
    return {
        'lane': args.lane, 'data_root': root,
        'telemetry_dir': dr.resolve(root, 'telemetry_dir'),
        'gatelogs_dir': dr.resolve(root, 'gatelogs_dir'),
        'manifests_dir': dr.resolve(root, 'manifests_dir'),
        'plan': args.plan, 'roster': (args.roster.split(',') if args.roster else None),
        'auto_promote_until': args.auto_promote_until,
        'weekly_cost_ceiling': args.weekly_cost_ceiling,
        'max_calls': args.max_calls, 'canary_cmd': args.canary_cmd,
        'reset_day': args.reset_day, 'reset_hour': args.reset_hour,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lane', help='pc | prod | routine')
    ap.add_argument('--data-root', help='pwg-ru-data checkout')
    ap.add_argument('--plan', help='window plan JSON for bounded_staged_run')
    ap.add_argument('--roster', default=None,
                    help='comma profile fallback roster (default c4,c1,c5,c6 — R5.1)')
    ap.add_argument('--auto-promote-until', default=None,
                    help='forwarded to bounded_staged_run (absent -> --stop-before-promote)')
    ap.add_argument('--weekly-cost-ceiling', type=float, default=None,
                    help='R3.2: USD ceiling per ISO week for this lane (required)')
    ap.add_argument('--max-calls', type=int, default=40)
    ap.add_argument('--canary-cmd', default=None,
                    help='shell template producing a canary receipt: {profile} {receipt}')
    ap.add_argument('--reset-day', default='MON')
    ap.add_argument('--reset-hour', type=int, default=0)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.lane and args.data_root and args.plan):
        ap.error('--lane, --data-root and --plan are required (unless --selftest)')
    if args.weekly_cost_ceiling is None:
        ap.error('--weekly-cost-ceiling is required (R3.2: the weekly quota is the '
                 'only wall, but the wall must EXIST — H2157 fail-closed)')
    cfg = build_cfg(args)
    record = tick(cfg, Runners(cfg))
    print(json.dumps(record, ensure_ascii=False, indent=1))
    return 0 if record['verdict'] in ('window', 'skip') else 1


class _FakeRunners:
    def __init__(self, gate=None, canary='receipt.json', run=(0, 1.0, []),
                 log=None):
        self.gate = {'c4': True} if gate is None else gate
        self.canary = canary
        self.run = run
        self.log = log if log is not None else []

    def gate_probe(self, profile):
        return self.gate.get(profile, False), 'fake'

    def canary_receipt(self, profile):
        return self.canary

    def bounded_run(self, profile, receipt, remaining):
        self.log.append(('run', profile, receipt, round(remaining, 4)))
        return self.run

    def commit_telemetry(self, message):
        self.log.append(('commit', message.split(':')[0]))
        return True


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        cfg = {'lane': 'pc', 'data_root': td,
               'telemetry_dir': os.path.join(td, 'telemetry'),
               'gatelogs_dir': os.path.join(td, 'gatelogs'),
               'manifests_dir': os.path.join(td, 'manifests'),
               'plan': 'plan.json', 'roster': None, 'auto_promote_until': None,
               'weekly_cost_ceiling': 10.0, 'max_calls': 5, 'canary_cmd': None,
               'reset_day': 'MON', 'reset_hour': 0}
        ledger = os.path.join(cfg['telemetry_dir'], 'scheduler_ticks_pc.jsonl')

        # (1) healthy tick -> window runs on c4 with the remaining weekly budget
        r = _FakeRunners()
        rec = tick(cfg, r)
        assert rec['verdict'] == 'window' and rec['profile'] == 'c4'
        assert r.log[0] == ('run', 'c4', 'receipt.json', 10.0), r.log
        assert rec['window_cost_usd'] == 1.0

        # (2) R5.1 roster walk: c4 NO-GO, c1 GO
        r2 = _FakeRunners(gate={'c4': False, 'c1': True})
        rec2 = tick(cfg, r2)
        assert rec2['profile'] == 'c1' and [g['go'] for g in rec2['gate_trail']] == \
            [False, True]

        # (3) all NO-GO -> recorded skip, no run
        r3 = _FakeRunners(gate={})
        rec3 = tick(cfg, r3)
        assert rec3['verdict'] == 'skip' and rec3['reason'] == \
            'live_gate_no_go_all_roster' and not any(x[0] == 'run' for x in r3.log)

        # (4) weekly ceiling: prior ticks' costs count; exhausted -> recorded skip
        spent = week_spend(ledger, iso_week(now_epoch()))
        assert spent == 2.0, spent          # ticks (1) and (2) each ran a $1 window
        cfg_low = dict(cfg, weekly_cost_ceiling=2.0)
        rec4 = tick(cfg_low, _FakeRunners())
        assert rec4['verdict'] == 'skip' and rec4['reason'] == \
            'weekly_cost_ceiling_exhausted'

        # (5) missing canary -> recorded skip (H2159 stays binding)
        rec5 = tick(cfg, _FakeRunners(canary=None))
        assert rec5['reason'] == 'no_fresh_canary_receipt'

        # (6) quota hang: failed window with the §270 signature -> pause until reset,
        # and the NEXT tick skips on the pause
        hang_rows = [{'reserved_at_ns': 0, 'finalized_at_ns': int(180_100 * 1e6),
                      'telemetry': {}}]
        rec6 = tick(cfg, _FakeRunners(run=(1, 0.0, hang_rows)))
        assert rec6['verdict'] == 'window_failed' and rec6['paused_until'] > now_epoch()
        rec7 = tick(cfg, _FakeRunners())
        assert rec7['verdict'] == 'skip' and rec7['reason'] == 'paused_until_reset'
        os.remove(pause_path(cfg['gatelogs_dir'], 'pc'))

        # (7) a slow-but-successful call is NOT a hang (§270 latency class)
        slow_ok = [{'reserved_at_ns': 0, 'finalized_at_ns': int(180_100 * 1e6),
                    'telemetry': {'duration_api_ms': 179_000}}]
        assert not classify_quota_hang(slow_ok)

        # (8) frozen lane -> skip; freeze file is lane-scoped
        os.makedirs(cfg['gatelogs_dir'], exist_ok=True)
        with open(lane_guard.freeze_path(cfg['gatelogs_dir'], 'pc'), 'w',
                  encoding='utf-8') as f:
            f.write('{}')
        rec8 = tick(cfg, _FakeRunners())
        assert rec8['reason'].startswith('lane_frozen')

        os.remove(lane_guard.freeze_path(cfg['gatelogs_dir'], 'pc'))   # unfreeze for 8b/8c

        # (8b) H2246: a runner that TIMES OUT is recorded, not vanished. This is the
        # expected shape of the §270 CLI hang and of the 4h window timeout; before the
        # fix the exception escaped tick() with no ledger row at all, so the crash
        # counted as an unexplained idle tick AND silently inflated the ≥95% metric.
        class _TimeoutRunners(_FakeRunners):
            def bounded_run(self, profile, receipt, remaining):
                raise subprocess.TimeoutExpired(
                    cmd=[sys.executable, 'bounded_staged_run.py'], timeout=14400)

        rec8b = tick(cfg, _TimeoutRunners())
        assert rec8b['verdict'] == 'window_failed', rec8b
        assert rec8b['reason'] == 'runner_timeout' and \
            rec8b['failed_step'] == 'bounded_window' and rec8b['timeout_s'] == 14400, rec8b

        # (8c) any other runner exception is likewise recorded, never silent
        class _BoomRunners(_FakeRunners):
            def gate_probe(self, profile):
                raise OSError('probe binary missing')

        rec8c = tick(cfg, _BoomRunners())
        assert rec8c['verdict'] == 'window_failed' and \
            rec8c['reason'] == 'runner_exception' and \
            rec8c['exception'].startswith('OSError'), rec8c

        # (8d) H2264: with auto-promote ON and no fresh spotcheck, the tick REFUSES
        # the window (fail closed — R4.1 surveillance is auto-promote's safety case).
        cfg_ap = dict(cfg, auto_promote_until='2099-01-01')
        rec8d = tick(cfg_ap, _FakeRunners())
        assert rec8d['verdict'] == 'skip' and \
            rec8d['reason'] == 'no_fresh_spotcheck_auto_promote_refused', rec8d

        # (8e) drop a fresh spotcheck report in and the same tick proceeds
        os.makedirs(cfg['telemetry_dir'], exist_ok=True)
        with open(os.path.join(cfg['telemetry_dir'], 'spotcheck_2026-08-03.json'),
                  'w', encoding='utf-8') as f:
            f.write('{}')
        rec8e = tick(cfg_ap, _FakeRunners())
        assert rec8e['verdict'] == 'window' and \
            rec8e['spotcheck'] == 'spotcheck_2026-08-03.json', rec8e

        # (9) EVERY branch above appended a tick record (the ≥95% metric source)
        rows = [json.loads(l) for l in open(ledger, encoding='utf-8')]
        assert len(rows) == 12, len(rows)
        assert all(r0.get('verdict') for r0 in rows)

        # (10) next_weekly_reset is strictly ahead and lands on the right weekday
        nr = next_weekly_reset(now_epoch(), 'MON', 0)
        assert nr > now_epoch() and time.gmtime(nr).tm_wday == 0
    print('nonstop_scheduler selftest: PASS (tick state machine, R5.1 roster, weekly '
          'ceiling, canary + freeze + pause gates, §270 hang vs latency, runner '
          'timeout/exception recorded (H2246), auto-promote fails closed without '
          'live R4.1 surveillance (H2264), every branch recorded)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
