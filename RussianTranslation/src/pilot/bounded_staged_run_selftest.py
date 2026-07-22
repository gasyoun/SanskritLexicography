#!/usr/bin/env python
r"""Hermetic self-test for bounded_staged_run.py (H963).

ZERO live generation: the bounded loop is driven with a scripted fake run_window (writes a
fixture wf_output) and injected audit reports; the scope-isolation test seeds a real sqlite
jobs table via the orchestrator's own CLI but never dispatches a model call. Every H963
characterization/regression case is exercised end to end:

  (a) plan scope        — only prepared headless windows enter scope; a bad --lease-id raises
  (b) dry-run           — the default path prints the planning view and makes ZERO calls
                          (probe_fleet is monkeypatched to raise; the dry-run never reaches it)
  (c) historical jobs   — an unrelated other-plan job (failed/done) is invisible to the
                          current plan's scoped counts/claims
  (d) clean completion  — a full drain over N leases stops at clean-target, all windows done
  (e) restart / no-dup  — resume from a checkpoint re-runs NO completed lease (exactly-once)
  (f) ceiling exhaustion— a call-count ceiling stops the run mid-queue
  (g) cost fail-closed  — an unevaluable window cost under a cost ceiling stops closed, and the
                          pre-run economy-ledger cost check refuses an unpriceable ceiling
  (h) consecutive-empty — a non-productive streak stops the run
  (i) audit seam        — audit_from_coordinator reads a lease's clean/requeue/satisfied/calls

  python src/pilot/bounded_staged_run_selftest.py
"""
import argparse
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bounded_staged_run as bsr
import bounded_supervisor as bs
import max_account_orchestrator as mao
from bounded_supervisor import (
    STOP_CLEAN_TARGET, STOP_CALL_COUNT, STOP_COST_UNEVALUABLE, STOP_CONSECUTIVE_EMPTY,
)


def _plan(roots, headless=True):
    """A synthetic pwg.no_pwg_scale_plan.v1-shaped plan with `roots` prepared headless windows."""
    windows = []
    for i, root in enumerate(roots):
        windows.append({
            'root': root, 'headwords': ['hw_%s' % root], 'subcards': ['%s~~h0_zz_pw' % root],
            'headless': {'projected_calls': 2, 'manifest_sha256': 'sha_%d' % i} if headless else None,
        })
    return {'schema': 'pwg.no_pwg_scale_plan.v1', 'windows': windows}


class FakeRunWindow:
    """run_window fake: records order, writes a trivial wf_output fixture, returns its path."""

    def __init__(self, td, raise_on_call=None):
        self.td = td
        self.raise_on_call = raise_on_call
        self.order = []

    def __call__(self, window):
        self.order.append(window['id'])
        if self.raise_on_call is not None and len(self.order) == self.raise_on_call:
            raise RuntimeError('simulated crash on %s' % window['id'])
        path = os.path.join(self.td, 'wf_%s.json' % window['id'].replace('/', '_'))
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'summary': {}, 'results': []}, f)
        return path


def _ceilings(**over):
    base = {'max_windows': None, 'max_calls': None, 'max_clean': None, 'cost_ceiling': None,
            'empty_streak': None, 'max_accounts': 0}
    base.update(over)
    return base


# ---------------------------------------------------------------------------

def test_a_plan_scope(td):
    plan = _plan(['no_pwg_w02', 'no_pwg_w03'])
    plan['windows'].append({'root': 'no_pwg_w04', 'headwords': ['x'], 'subcards': None,
                            'headless': None})   # plan-only, NOT in scope
    windows, scope = bsr.scope_windows(plan)
    assert [w['id'] for w in windows] == ['no_pwg_w02', 'no_pwg_w03'], windows
    assert scope['expected_windows'] == 2 and scope['expected_headwords'] == 2, scope
    # a --lease-id subset must equal the prepared roots or staged_plan_scope raises.
    _, s2 = bsr.scope_windows(plan, ['no_pwg_w02', 'no_pwg_w03'])
    assert s2['lease_ids'] == ['no_pwg_w02', 'no_pwg_w03'], s2
    raised = False
    try:
        bsr.scope_windows(plan, ['no_pwg_w04'])   # w04 is not a prepared headless root
    except SystemExit:
        raised = True
    assert raised, 'an unprepared/mismatched --lease-id must raise'
    print('  (a) plan scope: only prepared headless windows enter; bad --lease-id raises: PASS')


def test_b_dry_run_no_generation_call(td):
    plan = _plan(['no_pwg_w02'])
    coord = os.path.join(td, 'coord'); os.makedirs(coord)
    with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
        json.dump({'leases': [{'id': 'no_pwg_w02', 'state': 'prepared'}]}, f)
    plan_path = os.path.join(td, 'plan.json')
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f)

    # Monkeypatch probe_fleet AND make_run_window to raise: if the dry-run path touched either,
    # the test blows up. It must not — dry-run returns before any live wiring.
    _pf, _mrw = mao.probe_fleet, bsr.make_run_window
    calls = {'probe': 0, 'run_window': 0}

    def _boom_probe(*a, **k):
        calls['probe'] += 1
        raise AssertionError('dry-run must NOT probe the fleet')

    def _boom_mrw(*a, **k):
        calls['run_window'] += 1
        raise AssertionError('dry-run must NOT build a run_window')

    mao.probe_fleet = _boom_probe
    bsr.make_run_window = _boom_mrw
    try:
        args = argparse.Namespace(
            plan=plan_path, coord_dir=coord, db=os.path.join(td, 'nope.sqlite'),
            checkpoint=os.path.join(td, 'cp.json'), lease_id=None, execute=False, report=None,
            max_windows=1, max_calls=None, max_clean=None, cost_ceiling=None, empty_streak=None,
            max_accounts=0)
        rc = bsr.run(args)
    finally:
        mao.probe_fleet, bsr.make_run_window = _pf, _mrw
    assert rc == 0, rc
    assert calls == {'probe': 0, 'run_window': 0}, calls
    print('  (b) dry-run planning view makes ZERO generation calls (default off): PASS')


def test_c_historical_jobs_excluded(td):
    # Seed a real sqlite jobs table (via the orchestrator CLI) holding an UNRELATED other-plan
    # job plus the current plan's lease. The current plan's scope must exclude the historical
    # job from every scoped count — the isolation the live run_window relies on.
    db = os.path.join(td, 'scope.sqlite')
    mao.main(['--db', db, 'init', '--account', 'acc=' + os.path.join(td, 'acc'),
              '--skip-profile-check'])
    for ext in ('other_plan_w99', 'no_pwg_w02'):
        mao.main(['--db', db, 'enqueue', '--external-id', ext, '--argv-json',
                  json.dumps([sys.executable, '-c', 'print(1)']), '--cwd', td,
                  '--output', os.path.join(td, ext + '.json')])
    con = mao.connect(db)
    with con:
        con.execute("UPDATE jobs SET state='failed' WHERE external_id='other_plan_w99'")
    con.close()
    scope = {'no_pwg_w02'}
    con = mao.connect(db)
    # the unrelated failed job is invisible to the current plan's scoped counts
    assert mao.scoped_job_count(con, scope, "state='failed'") == 0, 'historical failed job leaked into scope'
    assert mao.scoped_job_count(con, scope, "state='pending'") == 1, 'current lease not pending in scope'
    assert [r['external_id'] for r in mao.scoped_jobs(con, scope, "1=1")] == ['no_pwg_w02'], 'scope not isolated'
    con.close()
    # a scoped claim never touches the historical job
    claimed = mao.claim(db, 'acc', only_external_ids=scope)
    assert claimed and claimed['external_id'] == 'no_pwg_w02', claimed
    con = mao.connect(db)
    assert con.execute("SELECT state FROM jobs WHERE external_id='other_plan_w99'").fetchone()[0] == 'failed', \
        'historical job must be untouched by the scoped claim'
    con.close()
    print('  (c) unrelated historical/other-plan jobs excluded from the current scope: PASS')


def test_d_clean_completion(td):
    plan = _plan(['no_pwg_w02', 'no_pwg_w03', 'no_pwg_w05'])
    windows, _ = bsr.scope_windows(plan)
    runner = FakeRunWindow(td)

    def audit(wf_output, window):
        return {'requeue_keys': [], 'clean_count': 1, 'cost': 0.5, 'calls': 1, 'satisfied_keys': []}

    sup = bsr.build_supervisor(windows, os.path.join(td, 'd.json'), _ceilings(), runner, audit)
    summ = sup.run()
    assert summ['stop_reason'] == STOP_CLEAN_TARGET, summ
    assert summ['windows_done'] == 3, summ
    assert runner.order == ['no_pwg_w02', 'no_pwg_w03', 'no_pwg_w05'], runner.order
    assert summ['completed_window_ids'] == ['no_pwg_w02', 'no_pwg_w03', 'no_pwg_w05'], summ
    print('  (d) full clean completion drains all leases to clean-target: PASS')


def test_e_restart_no_duplicate_completion(td):
    # Realistic interruption = a kill/crash mid-window (the checkpoint keeps stop_reason=None,
    # so --resume continues; a CLEAN ceiling stop is terminal by design and resume is a no-op).
    plan = _plan(['no_pwg_w02', 'no_pwg_w03', 'no_pwg_w05'])
    windows, _ = bsr.scope_windows(plan)
    cp = os.path.join(td, 'e.json')

    def audit(wf_output, window):
        return {'requeue_keys': [], 'clean_count': 1, 'cost': 1, 'calls': 1, 'satisfied_keys': []}

    # First pass CRASHES while running the 3rd lease (2 completed + checkpointed).
    runner_a = FakeRunWindow(td, raise_on_call=3)
    sup_a = bsr.build_supervisor(windows, cp, _ceilings(), runner_a, audit)
    crashed = False
    try:
        sup_a.run()
    except RuntimeError:
        crashed = True
    assert crashed, 'expected a simulated crash on the 3rd lease'
    state = json.load(open(cp, encoding='utf-8'))
    assert state['windows_done'] == 2 and state['completed_window_ids'] == ['no_pwg_w02', 'no_pwg_w03'], state
    assert state['stop_reason'] is None, state          # crashed mid-loop, not a clean stop

    # Resume: ONLY the uncompleted 3rd lease runs — no completed lease re-run/re-recorded.
    runner_b = FakeRunWindow(td)
    sup_b = bsr.build_supervisor(windows, cp, _ceilings(), runner_b, audit, resume=True)
    summ_b = sup_b.run()
    assert runner_b.order == ['no_pwg_w05'], runner_b.order   # exactly-once: w02/w03 NOT re-run
    assert summ_b['windows_done'] == 3, summ_b
    assert summ_b['completed_window_ids'] == ['no_pwg_w02', 'no_pwg_w03', 'no_pwg_w05'], summ_b
    assert summ_b['stop_reason'] == STOP_CLEAN_TARGET, summ_b
    print('  (e) restart after interruption re-runs NO completed lease (exactly-once): PASS')


def test_f_ceiling_exhaustion(td):
    plan = _plan(['no_pwg_w0%d' % i for i in range(6)])
    windows, _ = bsr.scope_windows(plan)
    runner = FakeRunWindow(td)

    def audit(wf_output, window):
        return {'requeue_keys': [], 'clean_count': 1, 'cost': 1, 'calls': 2, 'satisfied_keys': []}

    sup = bsr.build_supervisor(windows, os.path.join(td, 'f.json'),
                               _ceilings(max_calls=5), runner, audit)
    summ = sup.run()
    assert summ['stop_reason'] == STOP_CALL_COUNT, summ
    assert summ['calls_spent'] == 6 and summ['windows_done'] == 3, summ   # 3 windows * 2 calls
    print('  (f) a call-count ceiling stops the run mid-queue: PASS')


def test_g_cost_fail_closed(td):
    # runtime fail-closed: an unevaluable window cost under an active cost ceiling stops closed.
    plan = _plan(['no_pwg_w02', 'no_pwg_w03', 'no_pwg_w05'])
    windows, _ = bsr.scope_windows(plan)
    runner = FakeRunWindow(td)

    def audit(wf_output, window):
        if window['id'] == 'no_pwg_w03':
            return {'requeue_keys': [], 'clean_count': 1, 'calls': 1, 'satisfied_keys': []}  # NO cost
        return {'requeue_keys': [], 'clean_count': 1, 'cost': 1, 'calls': 1, 'satisfied_keys': []}

    sup = bsr.build_supervisor(windows, os.path.join(td, 'g.json'),
                               _ceilings(cost_ceiling=100), runner, audit)
    summ = sup.run()
    assert summ['stop_reason'] == STOP_COST_UNEVALUABLE, summ
    assert runner.order == ['no_pwg_w02', 'no_pwg_w03'], runner.order   # stops on the unpriceable one
    # pre-run fail-closed: a cost ceiling requested but the economy ledger cannot price it.
    empty_ledger = {'aggregate': {'cost_per_clean_band': None}}
    ok, reason = bsr.cost_ceiling_evaluable(0.75, empty_ledger)
    assert ok is False and 'UNEVALUABLE' in reason, (ok, reason)
    ok2, _ = bsr.cost_ceiling_evaluable(None, empty_ledger)   # no ceiling -> never a breach
    assert ok2 is True
    priced = {'aggregate': {'cost_per_clean_band': {'floor_usd': 0.07, 'ceil_usd': 0.70}}}
    ok3, reason3 = bsr.cost_ceiling_evaluable(0.75, priced)
    assert ok3 is True and 'cost basis' in reason3, (ok3, reason3)
    print('  (g) cost fail-closed: unevaluable cost stops closed; unpriceable ceiling refused: PASS')


def test_h_consecutive_empty(td):
    plan = _plan(['no_pwg_w0%d' % i for i in range(6)])
    windows, _ = bsr.scope_windows(plan)
    runner = FakeRunWindow(td)

    def audit(wf_output, window):
        return {'requeue_keys': ['%s~~h0_zz_pw' % window['id']], 'clean_count': 0, 'cost': 0,
                'calls': 1, 'satisfied_keys': []}   # non-productive: 0 clean, only requeue

    sup = bsr.build_supervisor(windows, os.path.join(td, 'h.json'),
                               _ceilings(empty_streak=3), runner, audit)
    summ = sup.run()
    assert summ['stop_reason'] == STOP_CONSECUTIVE_EMPTY, summ
    assert summ['empty_streak'] == 3, summ
    print('  (h) a consecutive non-productive streak stops the run: PASS')


def test_i_audit_from_coordinator(td):
    coord_state_path = os.path.join(td, 'state.json')
    wf = os.path.join(td, 'wf_w02.json')
    with open(wf, 'w', encoding='utf-8') as f:
        json.dump({'summary': {'translate_agents_spent': 4, 'heal_agents_spent': 1,
                               'subagent_tokens': 1_000_000}}, f)
    # a recorded lease: 3 clean, one defect key still pending, positive store delta.
    with open(coord_state_path, 'w', encoding='utf-8') as f:
        json.dump({'leases': [{
            'id': 'no_pwg_w02', 'state': 'promoted_partial', 'audit_state': 'needs_requeue',
            'clean_count': 3, 'store_delta': 5,
            'pending_requeue': {'transient': [], 'defect': ['d~~h0_zz_pw']},
        }]}, f)
    rep = bsr.audit_from_coordinator(coord_state_path, wf, {'id': 'no_pwg_w02'})
    assert rep['clean_count'] == 3, rep
    assert rep['requeue_keys'] == ['d~~h0_zz_pw'], rep
    assert rep['satisfied_keys'] == [], rep
    assert rep['calls'] == 5, rep                                    # 4 + 1
    assert rep['cost'] is not None and rep['cost'] > 0, rep          # priced from tokens
    # a zero-delta requeue window: the pending key is satisfied-not-failed
    with open(coord_state_path, 'w', encoding='utf-8') as f:
        json.dump({'leases': [{'id': 'no_pwg_w02', 'state': 'promoted', 'clean_count': 0,
                               'store_delta': 0,
                               'pending_requeue': {'transient': ['t~~h0_zz_pw'], 'defect': []}}]}, f)
    rep2 = bsr.audit_from_coordinator(coord_state_path, wf, {'id': 'no_pwg_w02', 'requeue': True})
    assert rep2['satisfied_keys'] == ['t~~h0_zz_pw'] and rep2['requeue_keys'] == [], rep2
    print('  (i) audit_from_coordinator reads clean/requeue/satisfied/calls/cost from the lease: PASS')


def test_j_stop_before_promote_awaiting_review(td):
    from types import SimpleNamespace

    def _wf(path, keys):
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'meta': {'selected_keys': keys, 'gen_model': 'claude-sonnet-5',
                                 'execution': {'profile_slot': 'c4',
                                               'execution_route': 'claude-cli-headless',
                                               'executor_lane': 'serial', 'validation_method': 'audit',
                                               'config_dir_fingerprint': 'f' * 64,
                                               'model_identifier': 'claude-sonnet-5'}},
                       'summary': {'usage': {'input_tokens': 10, 'observed_cost_usd': 0.01,
                                             'cost_evaluable': True}}, 'results': []}, f)
        return path

    # (1) gating — only a clean, productive audit is eligible; a rejected/empty one is not.
    assert bsr._audit_is_clean({'clean_count': 2, 'requeue_keys': []})
    assert bsr._audit_is_clean({'satisfied_keys': ['k'], 'requeue_keys': []})
    assert not bsr._audit_is_clean({'clean_count': 1, 'requeue_keys': ['k']})   # audit-rejected
    assert not bsr._audit_is_clean({'requeue_keys': [], 'clean_count': 0})       # nothing produced
    assert not bsr._audit_is_clean({})

    jdir = os.path.join(td, 'r10'); os.makedirs(jdir)
    wf = _wf(os.path.join(jdir, 'wf.json'), ['b', 'a'])
    ctx = SimpleNamespace(checkpoint=os.path.join(jdir, 'cp.json'), run_id='r10', stop_before_promote=True)
    report = {'clean_count': 2, 'requeue_keys': [], 'satisfied_keys': [], 'state': 'clean', 'calls': 1}

    # (2) a clean audit writes a durable, hash-bound, self-hashing checkpoint; store/TM untouched.
    path, record = bsr.write_awaiting_review_checkpoint(ctx, {'id': 'lease1', 'attempt': 1}, wf, report)
    assert bsr.verify_awaiting_review_checkpoint(path)
    hs = record['payload']['bound']['hashes']
    for k in ('execution_manifest', 'lease_attempt', 'audit_report', 'clean_candidate',
              'profile_route_model', 'usage_audit_state'):
        assert hs.get(k), (k, hs)
    assert record['payload_sha256'] and record['payload']['status'] == 'AWAITING_REVIEW'
    files = set(os.listdir(jdir))
    assert 'wf.json' in files and os.path.basename(path) in files, files
    assert not any('translated' in f or 'translation_memory' in f or f.endswith('.jsonl')
                   for f in files), files                          # no store, no TM

    # (3) tampering with the checkpoint payload OR the bound wf artifact invalidates it.
    rec = json.load(open(path, encoding='utf-8'))
    rec['payload']['bound']['selected_keys'] = ['tampered']
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rec, f)
    assert not bsr.verify_awaiting_review_checkpoint(path), 'tampered payload verified'
    bsr.write_awaiting_review_checkpoint(ctx, {'id': 'lease1', 'attempt': 1}, wf, report)  # restore
    assert bsr.verify_awaiting_review_checkpoint(path)
    with open(wf, 'a', encoding='utf-8') as f:
        f.write('\n#tampered')
    assert not bsr.verify_awaiting_review_checkpoint(path), 'tampered artifact verified'

    # (4) through the real supervisor: clean audit -> AWAITING_REVIEW per window; resume relaunches nothing.
    class RichRunner:
        def __init__(self, tdir):
            self.tdir, self.order = tdir, []
        def __call__(self, window):
            self.order.append(window['id'])
            return _wf(os.path.join(self.tdir, 'wf_%s.json' % window['id']), [window['id']])

    plan = _plan(['no_pwg_w02', 'no_pwg_w03'])
    windows, _ = bsr.scope_windows(plan)
    cp2 = os.path.join(jdir, 'sup.json')
    ctx2 = SimpleNamespace(checkpoint=cp2, run_id='sup', stop_before_promote=True)

    def wrapped_audit(wf_output, window):
        rep = {'requeue_keys': [], 'clean_count': 1, 'calls': 1, 'satisfied_keys': []}
        if ctx2.stop_before_promote and bsr._audit_is_clean(rep):
            bsr.write_awaiting_review_checkpoint(ctx2, window, wf_output, rep)
        return rep

    runner = RichRunner(jdir)
    bsr.build_supervisor(windows, cp2, _ceilings(), runner, wrapped_audit).run()
    assert runner.order == ['no_pwg_w02', 'no_pwg_w03'], runner.order
    for w in ('no_pwg_w02', 'no_pwg_w03'):
        cpath = bsr.awaiting_review_path(ctx2, w)
        assert os.path.exists(cpath) and bsr.verify_awaiting_review_checkpoint(cpath), cpath
    runner2 = RichRunner(jdir)
    bsr.build_supervisor(windows, cp2, _ceilings(), runner2, wrapped_audit, resume=True).run()
    assert runner2.order == [], runner2.order            # restart launches the model for NO window

    # (5) backward compatible: default (flag absent) writes no AWAITING_REVIEW checkpoint.
    off = os.path.join(jdir, 'off.json')
    ctx_off = SimpleNamespace(checkpoint=off, run_id='off', stop_before_promote=False)
    runner3 = RichRunner(jdir)

    def audit_off(wf_output, window):
        rep = {'requeue_keys': [], 'clean_count': 1, 'calls': 1, 'satisfied_keys': []}
        if ctx_off.stop_before_promote and bsr._audit_is_clean(rep):
            bsr.write_awaiting_review_checkpoint(ctx_off, window, wf_output, rep)
        return rep

    bsr.build_supervisor(windows, off, _ceilings(), runner3, audit_off).run()
    assert not os.path.exists(bsr.awaiting_review_path(ctx_off, 'no_pwg_w02')), 'flag-off wrote a checkpoint'
    print('  (j) --stop-before-promote: durable hash-bound AWAITING_REVIEW; clean-only; tamper-evident; '
          'no relaunch; flag-off backward compatible: PASS')


def test_k_requeue_materialisation(td):
    """H1339 A4 (fuller fix): a supervisor requeue work-item becomes a REAL coordinator
    requeue attempt + scoped job -- idempotent at every seam, loud when unmaterialisable."""
    from execution_contract import config_dir_fingerprint
    coord = os.path.join(td, 'k_coord')
    adir = os.path.join(coord, 'artifacts', 'w1')
    rq_dir = os.path.join(adir, 'requeue', 'rq01-transient')
    os.makedirs(rq_dir)
    rq_manifest = os.path.join(rq_dir, 'execution_manifest.w1.rq01-transient.json')
    with open(rq_manifest, 'w', encoding='utf-8') as f:
        json.dump({'schema': 'pwg.headless_execution_manifest.v2',
                   'model': 'claude-sonnet-5',
                   'meta': {'lang': 'ru', 'selected_keys': ['k~~h0_zz_pw']},
                   'execution': {'profile_slot': 'c4',
                                 'config_dir_fingerprint': config_dir_fingerprint(td),
                                 'execution_route': 'claude-cli-headless',
                                 'executor_lane': 'serial-whole-card',
                                 'validation_method': 'audit_window+final_schema',
                                 'model_identifier': 'claude-sonnet-5'},
                   'key_provenance': {'k~~h0_zz_pw': 'real'}}, f)
    state_path = os.path.join(coord, 'state.json')

    def write_state(state_name, with_attempt):
        lease = {'id': 'w1', 'state': state_name, 'artifact_dir': adir,
                 'pending_requeue': {'transient': ['k~~h0_zz_pw'], 'defect': []}}
        if with_attempt:
            lease.update({'requeue_attempt': 1, 'requeue_kind': 'transient',
                          'execution_manifest': rq_manifest,
                          'current_attempt': {'number': 1, 'kind': 'transient',
                                              'artifact_dir': rq_dir,
                                              'execution_manifest': rq_manifest}})
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump({'leases': [lease]}, f)

    db = os.path.join(td, 'k_jobs.sqlite')
    mao.connect(db).close()
    ctx = bsr.RunContext(db=db, coord_dir=coord,
                         coordinator=os.path.join(HERE, 'coordinator.py'),
                         cwd=td, events=None, run_id='k', probe_latencies={})
    calls = []

    def fake_prepare(argv, **kw):
        calls.append(argv)
        assert 'prepare-requeue' in argv and '--transient' in argv, argv
        # H1386 D4 (the A7 class, repeated): every coordinator subprocess must carry THIS
        # run's coord dir -- without it a non-default --coord-dir run resolves the DEFAULT
        # coordinator state (wrong-dir SystemExit mid-drain, or a same-id foreign lease
        # mutated to requeue_prepared).
        env = kw.get('env') or {}
        assert env.get('PWG_COORDINATOR_DIR') == os.path.abspath(coord), \
            'prepare-requeue subprocess missing PWG_COORDINATOR_DIR=%s' % coord
        write_state('requeue_prepared', with_attempt=True)   # what the real command does
        return argparse.Namespace(returncode=0, stdout='', stderr='')

    # 1. needs_requeue + pending backlog -> prepare (transient first) + import: a REAL job.
    write_state('needs_requeue', with_attempt=False)
    rq_id = bsr.materialize_requeue(ctx, 'w1', run=fake_prepare)
    assert rq_id == 'w1::rq01-transient', rq_id
    assert len(calls) == 1
    dbc = mao.connect(db)
    row = dbc.execute('select manifest_path,max_attempts,state from jobs where external_id=?',
                      (rq_id,)).fetchone()
    dbc.close()
    assert row and row['manifest_path'] == rq_manifest and row['max_attempts'] == 2         and row['state'] == 'pending', (dict(row) if row else row)

    # 2. idempotent resume: lease already requeue_prepared (crash between prepare and
    #    import) -> prepare NOT re-run; the existing attempt job reused, never duplicated.
    def must_not_run(argv, **kw):
        raise AssertionError('prepare-requeue re-run on an already-prepared lease')
    assert bsr.materialize_requeue(ctx, 'w1', run=must_not_run) == rq_id
    dbc = mao.connect(db)
    assert dbc.execute('select count(*) from jobs where external_id=?',
                       (rq_id,)).fetchone()[0] == 1
    dbc.close()

    # 3. unmaterialisable -> LOUD (blocked lease; unknown lease).
    write_state('blocked', with_attempt=False)
    for lease_name in ('w1', 'ghost'):
        try:
            bsr.materialize_requeue(ctx, lease_name, run=must_not_run)
            raise AssertionError('unmaterialisable requeue did not fail loudly')
        except SystemExit:
            pass

    # 4. the audit seam reads the ORIGIN lease for a requeue window.
    write_state('promoted_partial', with_attempt=True)
    wf = os.path.join(td, 'k_wf.json')
    with open(wf, 'w', encoding='utf-8') as f:
        json.dump({'summary': {'translate_agents_spent': 1, 'heal_agents_spent': 0}}, f)
    rep = bsr.audit_from_coordinator(state_path, wf,
                                     {'id': 'rq-001-w1', 'origin': 'w1', 'requeue': True})
    assert rep['requeue_keys'] == ['k~~h0_zz_pw'], rep

    # 5. a requeue OF a requeue keeps the TRUE origin (the coordinator lease id).
    sup = bs.BoundedSupervisor([], lambda w: None, os.path.join(td, 'k_ckpt.json'))
    first = sup._make_requeue_item({'id': 'w1'}, ['a'])
    second = sup._make_requeue_item(first, ['b'])
    assert first['origin'] == 'w1' and second['origin'] == 'w1', (first, second)
    print('  (k) H1339 A4: requeue materialises to a real ::rq job; idempotent; loud when '
          'unmaterialisable; audit reads the origin lease; rq-of-rq keeps the true origin: PASS')


def test_m_requeue_resume_after_crash(td):
    """H1386 C2: a post-audit origin state (ready/ready_partial/promoted/promoted_partial)
    with a COMPLETED ::rqNN attempt job is a RESUME, not a wedge -- materialize_requeue
    returns the existing job id and falls through to the drain loop (whose break + A2
    rescue promote handles recorded-but-unpromoted exactly as for plain windows). Pre-fix,
    every --resume re-pulled the checkpointed rq item and SystemExit'd permanently."""
    coord = os.path.join(td, 'm_coord'); os.makedirs(coord)
    state_path = os.path.join(coord, 'state.json')
    db = os.path.join(td, 'm_jobs.sqlite')
    dbc = mao.connect(db)
    with dbc:
        dbc.execute("INSERT INTO jobs(external_id,cwd,output_path,manifest_path,state,"
                    "coordinator_recorded) VALUES('w1::rq01-transient',?,?,?,'done',1)",
                    (td, os.path.join(td, 'm_out.json'), os.path.join(td, 'm_manifest.json')))
    dbc.close()
    ctx = bsr.RunContext(db=db, coord_dir=coord,
                         coordinator=os.path.join(HERE, 'coordinator.py'),
                         cwd=td, events=None, run_id='m', probe_latencies={})

    def must_not_run(argv, **kw):
        raise AssertionError('prepare-requeue must not run on a resumable post-audit lease')

    def write_lease(state_name, pending=None):
        with open(state_path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'leases': [{'id': 'w1', 'state': state_name,
                                   'pending_requeue': pending or {'transient': [],
                                                                  'defect': []}}]}, f)

    # 1. every post-audit state with a completed attempt job resumes to that job id.
    for state_name in ('ready', 'ready_partial', 'promoted', 'promoted_partial'):
        write_lease(state_name)
        rq = bsr.materialize_requeue(ctx, 'w1', run=must_not_run)
        assert rq == 'w1::rq01-transient', (state_name, rq)

    # 2. genuinely unmaterialisable states stay LOUD even with a completed attempt job.
    for state_name in ('blocked', 'needs_requeue'):
        write_lease(state_name)   # empty backlog: nothing preparable
        try:
            bsr.materialize_requeue(ctx, 'w1', run=must_not_run)
            raise AssertionError('%s lease did not fail loudly' % state_name)
        except SystemExit:
            pass

    # 3. a post-audit state WITHOUT any completed attempt job is still a loud raise
    #    (nothing to resume -- the rq item maps to no work at all).
    db2 = os.path.join(td, 'm_jobs_empty.sqlite')
    mao.connect(db2).close()
    ctx2 = bsr.RunContext(db=db2, coord_dir=coord,
                          coordinator=os.path.join(HERE, 'coordinator.py'),
                          cwd=td, events=None, run_id='m2', probe_latencies={})
    write_lease('ready')
    try:
        bsr.materialize_requeue(ctx2, 'w1', run=must_not_run)
        raise AssertionError('ready lease with no attempt job did not fail loudly')
    except SystemExit:
        pass
    print('  (m) H1386 C2: post-audit lease + completed ::rq job resumes to the existing '
          'job; blocked/no-backlog/no-job stay loud: PASS')


def test_l_resume_recovers_abandoned_jobs(td):
    """H1386 C1: --resume must reset THIS plan's abandoned in_progress jobs to pending.

    The pre-fix code passed the whole staged_plan_scope DICT as only_external_ids, so
    _scope_sql iterated its KEYS ('expected_headwords', 'lease_ids', ...) and the recovery
    UPDATE matched zero jobs -- a crashed window then checkpointed COMPLETED with zero
    output while its stuck in_progress job blocked the account for every future claim."""
    plan = _plan(['no_pwg_w02'])
    plan_path = os.path.join(td, 'l_plan.json')
    with open(plan_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(plan, f)
    coord = os.path.join(td, 'l_coord'); os.makedirs(coord)
    with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'leases': [{'id': 'no_pwg_w02', 'state': 'prepared'}]}, f)
    db = os.path.join(td, 'l_jobs.sqlite')
    dbc = mao.connect(db)
    with dbc:
        dbc.execute("INSERT INTO accounts(name,config_dir,validated,updated_at) "
                    "VALUES('acc1',?,1,?)", (td, mao.now_iso()))
        dbc.execute("INSERT INTO jobs(external_id,cwd,output_path,manifest_path,state) "
                    "VALUES('no_pwg_w02',?,?,?,'in_progress')",
                    (td, os.path.join(td, 'l_out.json'), os.path.join(td, 'l_manifest.json')))
    dbc.close()

    class _NoopSup:
        def run(self):
            return {'stop_reason': STOP_CLEAN_TARGET}

    _pf, _rr, _bsup = mao.probe_fleet, mao.release_runtime, bsr.build_supervisor
    mao.probe_fleet = lambda *a, **k: {'acc1': 10}
    mao.release_runtime = lambda *a, **k: argparse.Namespace(returncode=0, stdout='', stderr='')
    bsr.build_supervisor = lambda *a, **k: _NoopSup()
    try:
        rc = bsr.run(argparse.Namespace(
            plan=plan_path, coord_dir=coord, coordinator=os.path.join(HERE, 'coordinator.py'),
            cwd=td, db=db, checkpoint=os.path.join(td, 'l_cp.json'), lease_id=None,
            execute=True, resume=True, report=None, run_id='l', events=None,
            claude_bin='claude', timeout=5, gen_model_version=bsr.DEFAULT_GEN_MODEL_VERSION,
            only_profile=None, drop_unhealthy=False, stop_before_promote=False,
            max_windows=None, max_calls=None, max_clean=None, cost_ceiling=None,
            empty_streak=None, max_accounts=0))
    finally:
        mao.probe_fleet, mao.release_runtime, bsr.build_supervisor = _pf, _rr, _bsup
    assert rc == 0, rc
    dbc = mao.connect(db)
    state = dbc.execute("SELECT state FROM jobs WHERE external_id='no_pwg_w02'").fetchone()['state']
    dbc.close()
    assert state == 'pending', (
        'H1386 C1: --resume did not reset the abandoned in_progress job (state=%r)' % state)

    # Defense-in-depth (a): a dict/str scope must be a TypeError, never a silent zero-match.
    for bad in ({'lease_ids': ['x']}, 'no_pwg_w02'):
        try:
            mao._scope_sql(bad)
            raise AssertionError('_scope_sql accepted a %s scope' % type(bad).__name__)
        except TypeError:
            pass

    # Defense-in-depth (b): a NORMAL (non-requeue) window whose run_window returns None must
    # fail loudly -- never checkpoint COMPLETED with zero output (the crash-recovery hole C1
    # exposed: recovery matched nothing, the drain saw no jobs, run_window returned None).
    windows, _ = bsr.scope_windows(plan)
    sup = bs.BoundedSupervisor(windows, lambda w: None, os.path.join(td, 'l_none_cp.json'),
                               audit=lambda wf, w: {'clean_count': 0})
    try:
        sup.run()
        raise AssertionError('a None-output normal window checkpointed COMPLETED')
    except SystemExit:
        pass
    assert sup.completed_window_ids == [], sup.completed_window_ids
    print('  (l) H1386 C1: --resume resets abandoned in_progress jobs; dict/str scope is a '
          'TypeError; a None-output window fails loudly: PASS')


def main():
    with tempfile.TemporaryDirectory() as td:
        test_a_plan_scope(td)
        test_b_dry_run_no_generation_call(td)
        test_c_historical_jobs_excluded(td)
        test_d_clean_completion(td)
        test_e_restart_no_duplicate_completion(td)
        test_f_ceiling_exhaustion(td)
        test_g_cost_fail_closed(td)
        test_h_consecutive_empty(td)
        test_i_audit_from_coordinator(td)
        test_j_stop_before_promote_awaiting_review(td)
        test_k_requeue_materialisation(td)
        test_l_resume_recovers_abandoned_jobs(td)
        test_m_requeue_resume_after_crash(td)
    print('bounded_staged_run_selftest: PASS')


if __name__ == '__main__':
    main()
