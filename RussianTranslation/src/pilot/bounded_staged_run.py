#!/usr/bin/env python
r"""bounded_staged_run.py — the OPT-IN bridge that runs the max-account staged-run path
under the bounded_supervisor control loop (H963; the live-wiring half of H960 gap #6).

WHAT THIS IS (and what it is NOT)
---------------------------------
`bounded_supervisor.BoundedSupervisor` is a hermetic, crash-resumable, bounded drain loop
whose one live dependency — the actual model call — is INJECTED as `run_window(window) ->
wf_output`. `max_account_orchestrator.cmd_staged_run` is the live probe→dispatch→record→
promote path, scoped to a plan's prepared coordinator leases. This module is the smallest
coherent bridge between the two: it drives the bounded loop over a staged plan's prepared
leases, one lease per window, reusing the EXISTING staged-run building blocks
(`probe_fleet`, `cmd_run_once`, `cmd_record_done`, coordinator `promote-ready`) as the
injected `run_window`, and adding the bounded loop's ceilings + checkpoint + cost
fail-closed policy AROUND them.

It is a NEW, standalone module with its own CLI. It edits NOTHING in
max_account_orchestrator.py / coordinator.py / bounded_supervisor.py — every existing
command and default is byte-for-byte unchanged, so this is a pure opt-in (H963 objective 1,
backward compatibility). The staged-run monolith is not refactored; its already-separate
callables are simply composed under a bounded loop.

SAFETY / DEFAULT-OFF
--------------------
The DEFAULT action is a DRY-RUN planning view that makes ZERO generation calls: it prints
the exact scoped work, the ceilings, the account allocation, the checkpoint path and the
stop policy, and returns. A live drain requires the explicit `--execute` opt-in AND a
healthy fleet probe (STOP-on-any-NO-GO by default). Without `--execute` no probe, no
dispatch, no promotion, no store write is ever attempted. This double-gates against an
accidental production run (H963 prohibits any production Max/Workflow translation call).

THE LEASE JOIN KEY
------------------
window['root'] == coordinator lease id == orchestrator job external_id (a single identifier
across the plan JSON, coordinator state.json, and the sqlite jobs table). Every bounded
window we build uses id == root, so the loop's completed_window_ids, the per-lease dispatch
scope (`only_external_ids={root}`) and the per-lease promotion scope (`--lease-id root`) all
line up. This is the mechanism that keeps transient/defect/pending/historical/unrelated-plan
work out of the current staged run (H963 objective 7): a job whose external_id is not in this
plan's lease set is invisible to every scoped count, claim, record and promote.

CEILINGS (H963 objective 4) — all optional, default-disabled, backward compatible:
  --max-windows   windows/calls attempted   (BoundedSupervisor.max_windows)
  --max-calls     cumulative model calls     (BoundedSupervisor.max_calls)
  --max-clean     clean rows requested       (BoundedSupervisor.max_clean)
  --empty-streak  consecutive non-productive (BoundedSupervisor.empty_streak_cap)
  --max-accounts  account/profile usage      (fleet cap, passed to probe/dispatch)
  --cost-ceiling  estimated/observed cost    (BoundedSupervisor.budget_cap)

COST FAIL-CLOSED (H963 objective 5): when --cost-ceiling is set the loop reads per-window
cost with bounded_supervisor.strict_cost_fn, which returns None (UNEVALUABLE) rather than a
silent zero when a window carries no trustworthy cost figure — the loop then stops with the
distinct STOP_COST_UNEVALUABLE reason. Additionally, BEFORE any live call, we fail closed if
a cost ceiling is requested but the economy ledger cannot price it at all (no clean cards on
record). Missing cost data is NEVER treated as zero. Accounting is the EXISTING economy
ledger + launch/probe ledgers — no parallel accounting store is introduced (objective 6).

Pure control-plane. The only side effects on the LIVE path are those cmd_staged_run already
performs (dispatch/record/promote); the dry-run and every code path in the self-test perform
none. Model authored by Opus 4.8 (claude-opus-4-8[1m]) for handoff H963.
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bounded_supervisor as bs                      # noqa: E402
import economy_ledger as el                          # noqa: E402
import max_account_orchestrator as mao               # noqa: E402
from bounded_supervisor import BoundedSupervisor, strict_cost_fn   # noqa: E402

SCHEMA = 'pwg.bounded_staged_run.v1'

# The exact-version contract coordinator.promote_ready enforces (rejects '', 'sonnet',
# 'claude-sonnet'); the staged loop hardcodes this same value. Never a bare tier alias.
DEFAULT_GEN_MODEL_VERSION = 'claude-sonnet-5'


# ---------------------------------------------------------------------------
# Scope — reuse staged_plan_scope verbatim so the bounded windows are exactly the
# staged-run's prepared headless leases (H963 objective 2/7: plan-scoped isolation).
# ---------------------------------------------------------------------------

def scope_windows(plan, requested_lease_ids=None):
    """Return (windows, scope) where `windows` is the bounded-loop plan list — one entry per
    prepared headless lease, id == window['root'] — and `scope` is the staged_plan_scope
    summary. A window that is not headless (plan-only / beyond --limit-windows) is NOT in
    scope, exactly as cmd_staged_run sees it. Pure; reads the frozen plan dict only."""
    scope = mao.staged_plan_scope(plan, requested_lease_ids)
    windows = []
    for window in scope['windows']:
        root = window['root']
        headless = window.get('headless') or {}
        windows.append({
            'id': root,                       # == lease id == job external_id (the join key)
            'root': root,
            'headwords': list(window.get('headwords') or []),
            'subcards': list(window.get('subcards') or []),
            'headless': True,
            'projected_calls': headless.get('projected_calls'),
            'manifest_sha256': headless.get('manifest_sha256'),
        })
    return windows, scope


def prepared_lease_ids(coord_state):
    """The set of lease ids the staged run can import — state=='prepared' only (a lease
    advanced past prepared is silently skipped by cmd_staged_run's import filter)."""
    return {lease.get('id') for lease in (coord_state or {}).get('leases', [])
            if lease.get('state') == 'prepared'}


# ---------------------------------------------------------------------------
# Cost fail-closed pre-check — reuse the economy ledger (objective 5/6).
# ---------------------------------------------------------------------------

def cost_ceiling_evaluable(cost_ceiling, ledger):
    """(ok, reason) for a requested monetary/quota ceiling, evaluated from the EXISTING
    economy ledger — never a parallel accounting source.

      * cost_ceiling is None -> (True, 'no cost ceiling requested').
      * a ceiling IS requested but the economy ledger has no priced clean cards (the pooled
        cost band is None — an all-wasted / empty log) -> (False, ...) FAIL CLOSED: we cannot
        price a single window, so a live run must not start against an unenforceable budget.
      * otherwise (True, <band basis>): the ledger yields a real per-clean cost band.

    This mirrors economy_ledger.gate(strict=True) semantics (a requested ceiling on
    unevaluable data is a breach) applied as a pre-run gate rather than a post-run one."""
    if cost_ceiling is None:
        return True, 'no cost ceiling requested'
    band = (ledger.get('aggregate') or {}).get('cost_per_clean_band')
    if band is None:
        return False, ('cost ceiling $%.4f requested but the economy ledger has no priced '
                       'clean cards (pooled cost band is None) — UNEVALUABLE, fail closed; '
                       'never treat missing cost data as zero' % cost_ceiling)
    return True, ('cost basis from economy ledger: $%.4f..$%.4f per clean (fresh-input ceil)'
                  % (band['floor_usd'], band['ceil_usd']))


# ---------------------------------------------------------------------------
# The audit callable — read the coordinator lease post-drain (LIVE path).
# ---------------------------------------------------------------------------

def _lease_by_id(coord_state, lease_id):
    for lease in (coord_state or {}).get('leases', []):
        if lease.get('id') == lease_id:
            return lease
    return None


def _window_cost_usd(lease, wf_summary):
    """A TRUSTWORTHY per-window cost in USD, or None when it cannot be honestly priced.

    Prefers observed subagent tokens (from the wf_output summary) priced at the economy
    ledger's fresh-input rate (the in-band figure, single-sourced from economy_ledger.PRICE);
    falls back to a recorded numeric cost on the lease. Returns None — NOT 0 — when neither is
    available (the common case: H911 found run-event tokens 'not_recoverable'), so a cost
    ceiling fails the run closed rather than silently under-counting."""
    tokens = (wf_summary or {}).get('subagent_tokens')
    if isinstance(tokens, (int, float)) and not isinstance(tokens, bool):
        return tokens * el.PRICE['input'] / 1e6
    cost = lease.get('cost') if isinstance(lease, dict) else None
    if isinstance(cost, (int, float)) and not isinstance(cost, bool):
        return cost
    if isinstance(cost, dict):
        usd = cost.get('est_cost_usd') if not cost.get('error') else None
        if isinstance(usd, (int, float)) and not isinstance(usd, bool):
            return usd
    return None


def audit_from_coordinator(coord_state_path, wf_output, window):
    """Build a bounded_supervisor audit report from the coordinator lease's post-drain state.

    clean_count   = lease['clean_count'] (promotable clean rows on record; 0 if not promotable)
    requeue_keys  = pending_requeue transient + defect keys (rework, NOT completion)
    satisfied_keys= a requeue key whose promotion produced a zero store-delta (already
                    promoted upstream) — progress, not a hard error
    calls         = wf summary translate_agents_spent + heal_agents_spent (model calls)
    cost          = trustworthy per-window USD, else None (drives the fail-closed policy)

    A blocked/unknown lease contributes clean_count 0 and its keys as requeue (non-productive),
    so it counts toward the consecutive-empty streak rather than as clean completion."""
    try:
        with open(coord_state_path, encoding='utf-8') as f:
            coord_state = json.load(f)
    except (OSError, ValueError, TypeError):
        coord_state = {}
    lease = _lease_by_id(coord_state, window['id']) or {}
    pending = lease.get('pending_requeue') or {}
    requeue_keys = [k for k in (list(pending.get('transient') or []) +
                                list(pending.get('defect') or [])) if k]
    clean_count = int(lease.get('clean_count') or 0)
    store_delta = lease.get('store_delta')
    satisfied = []
    if window.get('requeue') and requeue_keys and store_delta == 0:
        # an already-promoted (zero-delta) requeue key: satisfied-not-failed
        satisfied, requeue_keys = requeue_keys, []
    wf_summary = {}
    try:
        with open(wf_output, encoding='utf-8') as f:
            wf_summary = (json.load(f).get('summary') or {})
    except (OSError, ValueError, TypeError):
        wf_summary = {}
    calls = int((wf_summary.get('translate_agents_spent') or 0) +
                (wf_summary.get('heal_agents_spent') or 0))
    return {
        'requeue_keys': requeue_keys,
        'satisfied_keys': satisfied,
        'clean_count': clean_count,
        'calls': calls,
        'cost': _window_cost_usd(lease, wf_summary),
        'audit_state': lease.get('audit_state'),
        'lease_state': lease.get('state'),
        'store_delta': store_delta,
    }


# ---------------------------------------------------------------------------
# The run_window callable — drain ONE lease via the existing staged-run pieces (LIVE path).
# ---------------------------------------------------------------------------

class RunContext:
    """Everything the per-lease live drain needs. Built once per bounded run; the fleet is
    probed ONCE by the caller (not per window) and its healthy set passed in as
    `probe_latencies` so dispatch never reaches an unprobed account."""

    def __init__(self, db, coord_dir, coordinator, cwd, events, run_id, probe_latencies,
                 claude_bin='claude', timeout=7200, gen_model_version=DEFAULT_GEN_MODEL_VERSION,
                 max_drain_iterations=1000):
        self.db = db
        self.coord_dir = coord_dir
        self.coordinator = coordinator
        self.cwd = cwd
        self.events = events
        self.run_id = run_id
        self.probe_latencies = probe_latencies
        self.claude_bin = claude_bin
        self.timeout = timeout
        self.gen_model_version = gen_model_version
        self.max_drain_iterations = max_drain_iterations

    @property
    def coord_state_path(self):
        return os.path.join(os.path.abspath(self.coord_dir), 'state.json')


def _ensure_imported(ctx, lease_id):
    """Import this lease as a scoped job if it is prepared and not already present (mirrors
    cmd_staged_run's to_import filter, scoped to the single lease)."""
    db = mao.connect(ctx.db)
    existing = {row['external_id'] for row in db.execute('SELECT external_id FROM jobs')}
    db.close()
    if lease_id in existing:
        return
    with open(ctx.coord_state_path, encoding='utf-8') as f:
        coord_state = json.load(f)
    if lease_id not in prepared_lease_ids(coord_state):
        return  # not prepared (already advanced / unknown) -> nothing to import
    mao.cmd_import_coordinator(argparse.Namespace(
        db=ctx.db, coord_dir=ctx.coord_dir, cwd=ctx.cwd, lease_id=[lease_id], max_attempts=2))


def make_run_window(ctx):
    """Return run_window(window) -> wf_output_path: drain exactly ONE lease scoped to its own
    external_id, reusing cmd_run_once / cmd_record_done / coordinator promote-ready. The scope
    (only_external_ids={lease_id}, --lease-id lease_id) guarantees no other plan's job is
    dispatched, recorded or promoted (H963 objective 2/7). This is invoked ONLY on the live
    (--execute) path; the dry-run and the self-test never call it."""
    import subprocess
    import time

    def run_window(window):
        lease_id = window['id']
        scope = {lease_id}
        _ensure_imported(ctx, lease_id)
        iterations = 0
        while True:
            iterations += 1
            if iterations > ctx.max_drain_iterations:
                raise SystemExit('bounded_staged_run: lease %s exceeded %d drain iterations'
                                 % (lease_id, ctx.max_drain_iterations))
            db = mao.connect(ctx.db)
            pending = mao.scoped_job_count(db, scope, "state='pending'")
            done_unrecorded = mao.scoped_job_count(
                db, scope, "state='done' AND coordinator_recorded=0")
            failed = mao.scoped_job_count(db, scope, "state='failed'")
            db.close()
            if failed:
                raise SystemExit('bounded_staged_run: lease %s has %d failed job(s) — fail closed'
                                 % (lease_id, failed))
            if not pending and not done_unrecorded:
                break
            if pending:
                now_ts = int(time.time())
                db = mao.connect(ctx.db)
                runnable = db.execute(
                    "SELECT count(*) FROM accounts WHERE validated=1 AND parked_until<=?",
                    (now_ts,)).fetchone()[0]
                db.close()
                if not runnable:
                    raise SystemExit('bounded_staged_run: lease %s pending but all accounts '
                                     'parked — rerun with --resume after the reset' % lease_id)
                mao.cmd_run_once(argparse.Namespace(
                    db=ctx.db, timeout=ctx.timeout, events=ctx.events, run_id=ctx.run_id,
                    claude_bin=ctx.claude_bin, only_accounts=set(ctx.probe_latencies),
                    only_external_ids=scope))
            mao.cmd_record_done(argparse.Namespace(
                db=ctx.db, coordinator=ctx.coordinator, cwd=ctx.cwd, only_external_ids=scope))
            promote = subprocess.run(
                [sys.executable, os.path.abspath(ctx.coordinator), 'promote-ready',
                 '--gen-model-version', ctx.gen_model_version, '--lease-id', lease_id],
                cwd=os.path.abspath(ctx.cwd), text=True, encoding='utf-8', capture_output=True)
            if promote.returncode and 'no ready leases to promote' not in (
                    promote.stderr + promote.stdout):
                raise SystemExit('bounded_staged_run: lease %s promotion failed: %s'
                                 % (lease_id, (promote.stderr or promote.stdout)[-1000:]))
        # Return the lease's recorded output path (the wf_output the audit reads).
        db = mao.connect(ctx.db)
        rows = mao.scoped_jobs(db, scope)
        db.close()
        for job in rows:
            if job['output_path'] and os.path.exists(job['output_path']):
                return job['output_path']
        return None

    return run_window


# ---------------------------------------------------------------------------
# Dry-run planning view — the exact scoped work + ceilings + stop policy, NO calls.
# ---------------------------------------------------------------------------

def plan_view(plan, coord_state, ceilings, checkpoint_path, requested_lease_ids=None,
              accounts=None, ledger=None):
    """Pure planning view (H963 objective 8): what a live run WOULD do — scoped work,
    ceilings, account allocation, checkpoint path, cost-basis evaluability and the ordered
    stop policy — computed WITHOUT any generation call. `accounts` is the validated-account
    name list (optional); `ledger` is a prebuilt economy ledger (optional; built from the
    frozen probe log when omitted)."""
    windows, scope = scope_windows(plan, requested_lease_ids)
    prepared = prepared_lease_ids(coord_state)
    importable = [w['id'] for w in windows if w['id'] in prepared]
    not_prepared = [w['id'] for w in windows if w['id'] not in prepared]
    if ledger is None:
        try:
            ledger = el.build_ledger(el.read_rows(el.FROZEN_LOG))
        except (OSError, ValueError):
            ledger = {'aggregate': {}}
    cost_ok, cost_reason = cost_ceiling_evaluable(ceilings.get('cost_ceiling'), ledger)
    max_accounts = ceilings.get('max_accounts') or 0
    allocated = list(accounts or [])
    if max_accounts:
        allocated = allocated[:max_accounts]
    stop_policy = [
        'window-count ceiling (max_windows=%s)' % ceilings.get('max_windows'),
        'call-count ceiling (max_calls=%s)' % ceilings.get('max_calls'),
        'clean-rows quota (max_clean=%s)' % ceilings.get('max_clean'),
        'cost/quota ceiling (cost_ceiling=%s; UNEVALUABLE cost -> STOP_COST_UNEVALUABLE, '
        'fail closed)' % ceilings.get('cost_ceiling'),
        'consecutive non-productive streak (empty_streak=%s)' % ceilings.get('empty_streak'),
        'clean-target drain (plan queue + requeue backlog both empty)',
        'any failed job or all-accounts-parked -> fail closed',
    ]
    return {
        'schema': SCHEMA,
        'mode': 'dry-run (no generation call made)',
        'scope': {
            'lease_ids': scope['lease_ids'],
            'expected_windows': scope['expected_windows'],
            'expected_headwords': scope['expected_headwords'],
            'expected_subcards': sum(len(w['subcards']) for w in windows),
            'projected_calls_from_plan': sum((w.get('projected_calls') or 0) for w in windows),
            'importable_prepared_leases': sorted(importable),
            'windows_not_prepared_skipped': sorted(not_prepared),
        },
        'ceilings': dict(ceilings),
        'cost_basis': {'evaluable': cost_ok, 'reason': cost_reason},
        'account_allocation': {
            'validated_accounts': list(accounts or []),
            'max_accounts_cap': max_accounts or None,
            'allocated': allocated,
        },
        'checkpoint_path': checkpoint_path,
        'stop_policy': stop_policy,
        'live_requires': "explicit --execute AND a healthy fleet probe (STOP-on-any-NO-GO)",
    }


# ---------------------------------------------------------------------------
# Orchestration — build the bounded supervisor and (dry-run | execute).
# ---------------------------------------------------------------------------

def _validated_accounts(db_path):
    if not db_path or not os.path.exists(db_path):
        return []
    try:
        db = mao.connect(db_path)
        names = [row['name'] for row in
                 db.execute('SELECT name FROM accounts WHERE validated=1 ORDER BY name')]
        db.close()
        return names
    except Exception:  # noqa: BLE001 — a missing/locked db must not crash the dry-run
        return []


def build_supervisor(windows, checkpoint_path, ceilings, run_window, audit, resume=False):
    """Construct the BoundedSupervisor with the H963 ceilings wired through. strict_cost_fn is
    used exactly when a cost ceiling is active, so an unevaluable window cost fails closed."""
    cost_ceiling = ceilings.get('cost_ceiling')
    return BoundedSupervisor(
        windows, run_window, checkpoint_path,
        audit=audit,
        max_windows=ceilings.get('max_windows'),
        max_calls=ceilings.get('max_calls'),
        max_clean=ceilings.get('max_clean'),
        budget_cap=cost_ceiling,
        empty_streak_cap=ceilings.get('empty_streak'),
        cost_fn=strict_cost_fn if cost_ceiling is not None else None,
        resume=resume,
    )


def run(args):
    plan = json.load(open(args.plan, encoding='utf-8'))
    coord_state_path = os.path.join(os.path.abspath(args.coord_dir), 'state.json')
    coord_state = {}
    if os.path.exists(coord_state_path):
        with open(coord_state_path, encoding='utf-8') as f:
            coord_state = json.load(f)
    ceilings = {
        'max_windows': args.max_windows, 'max_calls': args.max_calls,
        'max_clean': args.max_clean, 'cost_ceiling': args.cost_ceiling,
        'empty_streak': args.empty_streak, 'max_accounts': args.max_accounts,
    }
    accounts = _validated_accounts(args.db)
    ledger = el.build_ledger(el.read_rows(el.FROZEN_LOG)) if os.path.exists(el.FROZEN_LOG) else \
        {'aggregate': {}}
    view = plan_view(plan, coord_state, ceilings, args.checkpoint,
                     requested_lease_ids=args.lease_id, accounts=accounts, ledger=ledger)

    if not args.execute:
        # DEFAULT: dry-run planning view. No probe, no dispatch, no promotion, no store write.
        print(json.dumps(view, ensure_ascii=False, indent=1))
        return 0

    # --- LIVE path (owner-gated). Everything below is only reached with --execute. ---
    windows, scope = scope_windows(plan, args.lease_id)
    if not windows:
        raise SystemExit('bounded_staged_run: staged plan has no prepared headless windows')
    # Cost fail-closed PRE-CHECK: refuse to start a cost-capped run we cannot price at all.
    cost_ok, cost_reason = cost_ceiling_evaluable(args.cost_ceiling, ledger)
    if not cost_ok:
        raise SystemExit('bounded_staged_run: %s' % cost_reason)
    db = mao.connect(args.db)
    validated = list(db.execute('SELECT * FROM accounts WHERE validated=1 ORDER BY name'))
    db.close()
    if not validated:
        raise SystemExit('bounded_staged_run requires at least one validated account')
    if args.max_accounts:
        validated = validated[:args.max_accounts]
    run_id = args.run_id or ('bsr-' + mao.now_iso().replace(':', '').replace('-', ''))
    # Probe the fleet ONCE (STOP-on-any-NO-GO by default; the honest-NO-GO stance).
    probe_latencies = mao.probe_fleet(
        validated, args.claude_bin, events_path=args.events, run_id=run_id,
        drop_unhealthy=args.drop_unhealthy)
    if args.drop_unhealthy:
        for acc in validated:
            if acc['name'] not in probe_latencies:
                mao.park(args.db, acc['name'], mao.PARKED_FOREVER,
                         'dropped after probe NO-GO (--drop-unhealthy); healthy subset proceeds')
    ctx = RunContext(
        db=args.db, coord_dir=args.coord_dir, coordinator=args.coordinator, cwd=args.cwd,
        events=args.events, run_id=run_id, probe_latencies=probe_latencies,
        claude_bin=args.claude_bin, timeout=args.timeout,
        gen_model_version=args.gen_model_version)
    run_window = make_run_window(ctx)

    def audit(wf_output, window):
        return audit_from_coordinator(ctx.coord_state_path, wf_output, window)

    sup = build_supervisor(windows, args.checkpoint, ceilings, run_window, audit,
                           resume=args.resume)
    summary = sup.run()
    report = {'schema': SCHEMA, 'run_id': run_id, 'plan_view': view, 'summary': summary}
    if args.report:
        mao.atomic_write(args.report, json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    # A cost-unevaluable / non-clean stop is a non-zero exit so callers can gate on it.
    return 0 if summary.get('stop_reason') in (bs.STOP_CLEAN_TARGET, bs.STOP_WINDOW_COUNT,
                                               bs.STOP_CLEAN_QUOTA, bs.STOP_CALL_COUNT) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan', required=True, help='the pwg.no_pwg_scale_plan.v1 plan JSON')
    ap.add_argument('--coord-dir', required=True, help='coordinator dir holding state.json')
    ap.add_argument('--coordinator', help='path to coordinator.py (required for --execute)')
    ap.add_argument('--cwd', help='working dir for record/promote subprocesses (--execute)')
    ap.add_argument('--db', default='max_orchestrator.sqlite')
    ap.add_argument('--lease-id', action='append', help='restrict scope to these lease roots')
    ap.add_argument('--checkpoint', default='bounded_staged_run.checkpoint.json')
    ap.add_argument('--execute', action='store_true',
                    help='OPT-IN: run the live drain. Default (absent) is a dry-run planning '
                         'view that makes ZERO generation calls.')
    ap.add_argument('--resume', action='store_true',
                    help='resume from --checkpoint (no completed lease re-run/re-promoted)')
    # Ceilings (all optional / default-disabled).
    ap.add_argument('--max-windows', type=int, default=None)
    ap.add_argument('--max-calls', type=int, default=None)
    ap.add_argument('--max-clean', type=int, default=None)
    ap.add_argument('--cost-ceiling', type=float, default=None,
                    help='max cumulative cost (USD). An UNEVALUABLE window cost fails closed.')
    ap.add_argument('--empty-streak', type=int, default=None)
    ap.add_argument('--max-accounts', type=int, default=0)
    ap.add_argument('--drop-unhealthy', action='store_true')
    ap.add_argument('--gen-model-version', default=DEFAULT_GEN_MODEL_VERSION)
    ap.add_argument('--timeout', type=int, default=7200)
    ap.add_argument('--events')
    ap.add_argument('--report')
    ap.add_argument('--run-id')
    args = ap.parse_args(argv)
    if args.execute and not (args.coordinator and args.cwd and args.events):
        ap.error('--execute requires --coordinator, --cwd and --events')
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
