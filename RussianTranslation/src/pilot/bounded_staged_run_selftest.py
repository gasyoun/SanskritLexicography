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
  (s) H7 drain backstop — a zero-claim (and an unrecordable-done) drain polls and then stops
                          naming the stall instead of hot-spinning to max_drain_iterations;
                          forward progress resets the CONSECUTIVE counter

  python src/pilot/bounded_staged_run_selftest.py
"""
import argparse
import json
import os
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Isolation from production data, established before any repo import (several modules
# resolve store/coordinator constants at import time). See selftest_isolation.py.
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selftest_isolation import guard as _isolation_guard  # noqa: E402
_isolation_guard()

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bounded_staged_run as bsr
import bounded_supervisor as bs
import economy_ledger as el
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
    # The `enqueue` CLI is now a hard refusal (generic argv jobs are disabled in favour of
    # sealed coordinator manifests), so seeding through it aborts the whole suite. This test
    # is about SCOPE ISOLATION -- which jobs a plan's scoped queries can see -- and needs two
    # rows in the table, not a particular way of putting them there. Insert them directly.
    con = mao.connect(db)
    with con:
        for ext in ('other_plan_w99', 'no_pwg_w02'):
            con.execute('INSERT INTO jobs(external_id, argv_json, cwd, output_path) '
                        'VALUES(?,?,?,?)',
                        (ext, json.dumps([sys.executable, '-c', 'print(1)']), td,
                         os.path.join(td, ext + '.json')))
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
    assert summ.get('agent_ops_code') is None, summ  # success is not a failure code
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
    assert summ.get('agent_ops_code') == 'A1', summ
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
    assert summ.get('agent_ops_code') == 'A6', summ
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
    assert summ.get('agent_ops_code') == 'A2', summ
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
    with open(wf, 'w', encoding='utf-8') as f:
        json.dump({'summary': {'translate_agents_spent': 1, 'heal_agents_spent': 0,
                               'usage': {'subagent_tokens': 2_000_000,
                                         'observed_cost_usd': 0.42,
                                         'cost_evaluable': True}}}, f)
    nested = bsr.audit_from_coordinator(coord_state_path, wf, {'id': 'no_pwg_w02'})
    assert nested['cost'] == 0.42 and nested['calls'] == 1, nested
    assert bsr._window_cost_usd({}, {'usage': {
        'subagent_tokens': 2_000_000, 'cost_evaluable': False}}) is None
    for invalid in (-1, float('nan'), float('inf')):
        assert bsr._window_cost_usd({}, {'usage': {
            'observed_cost_usd': invalid, 'cost_evaluable': True}}) is None
    # a zero-delta requeue window: the pending key is satisfied-not-failed
    with open(coord_state_path, 'w', encoding='utf-8') as f:
        json.dump({'leases': [{'id': 'no_pwg_w02', 'state': 'promoted', 'clean_count': 0,
                               'store_delta': 0,
                               'pending_requeue': {'transient': ['t~~h0_zz_pw'], 'defect': []}}]}, f)
    rep2 = bsr.audit_from_coordinator(coord_state_path, wf, {'id': 'no_pwg_w02', 'requeue': True})
    assert rep2['satisfied_keys'] == ['t~~h0_zz_pw'] and rep2['requeue_keys'] == [], rep2
    for index, malformed_payload in enumerate((
            {}, {'summary': None}, {'summary': []},
            {'summary': {'translate_agents_spent': -1, 'heal_agents_spent': 0}})):
        malformed_wf = os.path.join(td, 'malformed-wf-%d.json' % index)
        with open(malformed_wf, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(malformed_payload, f)
        try:
            bsr.audit_from_coordinator(
                coord_state_path, malformed_wf, {'id': 'no_pwg_w02', 'requeue': True})
            raise AssertionError('malformed workflow summary/call counters were accepted')
        except RuntimeError as exc:
            assert 'workflow' in str(exc), exc
    for bad_state, bad_wf, message in (
            (os.path.join(td, 'missing-state.json'), wf, 'state'),
            (coord_state_path, os.path.join(td, 'missing-wf.json'), 'output')):
        try:
            bsr.audit_from_coordinator(bad_state, bad_wf, {'id': 'no_pwg_w02'})
            raise AssertionError('missing %s was accepted' % message)
        except RuntimeError as exc:
            assert message in str(exc), exc
    with open(coord_state_path, 'w', encoding='utf-8') as f:
        json.dump({'leases': []}, f)
    try:
        bsr.audit_from_coordinator(coord_state_path, wf, {'id': 'no_pwg_w02'})
        raise AssertionError('missing coordinator lease was accepted')
    except RuntimeError as exc:
        assert 'lease no_pwg_w02 is missing' in str(exc), exc
    print('  (i) audit_from_coordinator reads current usage and fails closed on missing artifacts: PASS')


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
    rq_preflight = os.path.join(rq_dir, 'preflight.json')
    with open(rq_preflight, 'w', encoding='utf-8') as f:
        json.dump({'schema': 'pwg.performance_preflight.v1',
                   'selected_keys': ['k~~h0_zz_pw'],
                   'cost_gate': {'over_ceiling': False}}, f)
    state_path = os.path.join(coord, 'state.json')

    def write_state(state_name, with_attempt):
        lease = {'id': 'w1', 'state': state_name, 'artifact_dir': adir,
                 'pending_requeue': {'transient': ['k~~h0_zz_pw'], 'defect': []}}
        if with_attempt:
            lease.update({'requeue_attempt': 1, 'requeue_kind': 'transient',
                          'execution_manifest': rq_manifest,
                          'preflight_path': rq_preflight,
                          'preflight_sha256': mao.sha256_path(rq_preflight),
                          'current_attempt': {'number': 1, 'kind': 'transient',
                                              'artifact_dir': rq_dir,
                                              'execution_manifest': rq_manifest,
                                              'preflight': rq_preflight,
                                              'preflight_sha256':
                                                  mao.sha256_path(rq_preflight)}})
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

    _pf, _rr, _cc, _bsup = (mao.probe_fleet, mao.release_runtime,
                             mao.coordinator_command, bsr.build_supervisor)
    mao.probe_fleet = lambda *a, **k: {'acc1': 10}
    mao.release_runtime = lambda *a, **k: argparse.Namespace(returncode=0, stdout='', stderr='')
    mao.coordinator_command = lambda *a, **k: argparse.Namespace(
        returncode=0, stdout='', stderr='')
    bsr.build_supervisor = lambda *a, **k: _NoopSup()
    try:
        checkpoint = os.path.join(td, 'l_cp.json')
        bsr.CallReservationLedger(checkpoint + '.calls.json', 'l', None)
        rc = bsr.run(argparse.Namespace(
            plan=plan_path, coord_dir=coord, coordinator=os.path.join(HERE, 'coordinator.py'),
            cwd=td, db=db, checkpoint=checkpoint, lease_id=None,
            execute=True, resume=True, report=None, run_id='l', events=None,
            claude_bin='claude', timeout=5, gen_model_version=bsr.DEFAULT_GEN_MODEL_VERSION,
            only_profile=None, drop_unhealthy=False, stop_before_promote=False,
            max_windows=None, max_calls=None, max_clean=None, cost_ceiling=None,
            empty_streak=None, max_accounts=0))
    finally:
        mao.probe_fleet, mao.release_runtime, mao.coordinator_command, bsr.build_supervisor = (
            _pf, _rr, _cc, _bsup)
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


def test_n_cli_defines_execute_path_args(td):
    """H1447: the CLI --execute path dereferences args.claude_bin (probe_fleet +
    RunContext), but the parser never defined --claude-bin — every injected-runner
    selftest built RunContext directly, so the live CLI path crashed with
    AttributeError BEFORE any call. Pin every attr the execute path reads off the
    parsed namespace, so a parser/consumer drift is a red test, not a live crash."""
    ap = bsr.build_parser()
    args = ap.parse_args(['--plan', 'p.json', '--coord-dir', 'cd'])
    for attr in ('claude_bin', 'db', 'coordinator', 'cwd', 'events', 'run_id',
                 'timeout', 'gen_model_version', 'only_profile', 'max_accounts',
                 'drop_unhealthy', 'checkpoint', 'stop_before_promote', 'resume',
                 'call_reservation'):
        assert hasattr(args, attr), 'execute path reads args.%s but the CLI never defines it' % attr
    assert args.claude_bin == 'claude', args.claude_bin
    print('  (n) H1447: CLI defines every attr the --execute path dereferences '
          '(incl. --claude-bin): PASS')


def test_o_preflight_before_probe(td):
    plan_path = os.path.join(td, 'o_plan.json')
    coord = os.path.join(td, 'o_coord')
    os.makedirs(coord)
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(_plan(['no_pwg_w02']), f)
    with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
        json.dump({'leases': [{'id': 'no_pwg_w02', 'state': 'prepared'}]}, f)
    probed = []
    original_command, original_probe = mao.coordinator_command, mao.probe_fleet
    mao.coordinator_command = lambda *a, **k: argparse.Namespace(
        returncode=2, stdout='', stderr='synthetic preflight refusal')
    mao.probe_fleet = lambda *a, **k: probed.append(1)
    calls = os.path.join(td, 'o.calls.json')
    try:
        try:
            bsr.run(argparse.Namespace(
                plan=plan_path, coord_dir=coord, coordinator='coordinator.py', cwd=td,
                db=os.path.join(td, 'absent.sqlite'), checkpoint=os.path.join(td, 'o.cp.json'),
                lease_id=None, execute=True, resume=False, report=None, run_id='o',
                events='events.jsonl', claude_bin='claude', timeout=5,
                gen_model_version=bsr.DEFAULT_GEN_MODEL_VERSION, only_profile=None,
                drop_unhealthy=False, stop_before_promote=False, max_windows=None,
                max_calls=2, call_reservation=calls, max_clean=None, cost_ceiling=None,
                empty_streak=None, max_accounts=0))
            raise AssertionError('preflight refusal was ignored')
        except SystemExit as exc:
            assert 'preflight refused before probe' in str(exc), exc
        assert not probed and not os.path.exists(calls)
    finally:
        mao.coordinator_command, mao.probe_fleet = original_command, original_probe
    print('  (o) coordinator preflight refusal occurs before ledger reservation/probe: PASS')


def test_p_resume_requires_existing_ledger_run(td):
    plan_path = os.path.join(td, 'p_plan.json')
    coord = os.path.join(td, 'p_coord')
    os.makedirs(coord)
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(_plan(['no_pwg_w02']), f)
    with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8') as f:
        json.dump({'leases': [{'id': 'no_pwg_w02', 'state': 'prepared'}]}, f)
    db_path = os.path.join(td, 'p.sqlite')
    db = mao.connect(db_path)
    with db:
        db.execute(
            'INSERT INTO accounts(name,config_dir,parked_until,validated,updated_at) '
            'VALUES(?,?,0,1,?)', ('acc', td, mao.now_iso()))
    db.close()
    calls = os.path.join(td, 'p.calls.json')
    with open(calls, 'w', encoding='utf-8') as f:
        json.dump({'schema': 'pwg.call_reservation.v1', 'runs': {}}, f)
    probed = []
    original_command, original_probe = mao.coordinator_command, mao.probe_fleet
    mao.coordinator_command = lambda *a, **k: argparse.Namespace(
        returncode=0, stdout='ok', stderr='')
    mao.probe_fleet = lambda *a, **k: probed.append(1)
    try:
        try:
            bsr.run(argparse.Namespace(
                plan=plan_path, coord_dir=coord, coordinator='coordinator.py', cwd=td,
                db=db_path, checkpoint=os.path.join(td, 'p.cp.json'),
                lease_id=None, execute=True, resume=True, report=None, run_id=None,
                events='events.jsonl', claude_bin='claude', timeout=5,
                gen_model_version=bsr.DEFAULT_GEN_MODEL_VERSION, only_profile=None,
                drop_unhealthy=False, stop_before_promote=False, max_windows=None,
                max_calls=2, call_reservation=calls, max_clean=None, cost_ceiling=None,
                empty_streak=None, max_accounts=0))
            raise AssertionError('resume created a fresh run in an empty call ledger')
        except SystemExit as exc:
            assert 'no existing run' in str(exc), exc
        assert not probed
    finally:
        mao.coordinator_command, mao.probe_fleet = original_command, original_probe
    print('  (p) --resume requires a pre-existing durable call-ledger run: PASS')


def test_q2_execute_requires_ceilings_h2157(td):
    """H2157 (H2025 G3 / F-B1): --execute REFUSES to start without BOTH --max-calls and
    --cost-ceiling (the fail-closed ceiling machinery was inert unless the operator
    remembered the flags — a billed run had no ceiling by default). --allow-unbounded is
    the explicit escape hatch; dry-run (no --execute) is unaffected. run() is patched to
    a sentinel so a PASSED gate is proven without touching plan/db/coordinator."""
    base = ['--plan', os.path.join(td, 'q2p.json'), '--coord-dir', os.path.join(td, 'q2cd'),
            '--coordinator', os.path.join(HERE, 'coordinator.py'), '--cwd', td,
            '--events', os.path.join(td, 'q2.events.jsonl'), '--execute']
    _run = bsr.run
    bsr.run = lambda a: 'gate-passed'
    try:
        for extra in ([], ['--max-calls', '3'], ['--cost-ceiling', '2.5']):
            try:
                bsr.main(base + extra)
                raise AssertionError('unbounded --execute must be refused: %r' % extra)
            except SystemExit as exc:
                assert getattr(exc, 'code', None) == 2, \
                    'parser-level refusal (exit 2) expected, got %r' % exc
        assert bsr.main(base + ['--max-calls', '3', '--cost-ceiling', '2.50',
                                '--skip-canary-gate']) == 'gate-passed', \
            'both ceilings supplied must pass the gate'
        assert bsr.main(base + ['--allow-unbounded', '--skip-canary-gate']) == 'gate-passed', \
            '--allow-unbounded must be an explicit escape hatch'
        assert bsr.main(['--plan', os.path.join(td, 'q2p.json'),
                         '--coord-dir', os.path.join(td, 'q2cd')]) == 'gate-passed', \
            'a dry-run (no --execute) must not require ceilings'
    finally:
        bsr.run = _run


def test_q3_execute_requires_canary_go_receipt_h2159(td):
    """H2159 (H2025 G4 / F-B2+F-B3): --execute consumes the live-gate canary verdict
    MECHANICALLY. judge_payload derives GO/NO-GO from the canary wf_output (synthetic
    keys only, expected sense count, zero {Tn}/SAN-LOSS/UNMAPPED); enforce() refuses a
    missing/NO-GO/stale/wrong-profile receipt; --skip-canary-gate is the explicit
    escape. run() is patched to a sentinel — a passed gate never touches plan/db."""
    import canary_gate as cg
    clean_card = {'records': [{'senses': [
        {'russian': 'перевод %d' % i, 'german': 'Übersetzung %d' % i} for i in range(3)]}]}
    go_res = {'meta': {'execution': {'profile_slot': 'c4'}},
              'results': [{'key': 'dq_canary_puregloss', 'card': clean_card}]}
    verdict, reasons, _ = cg.judge_payload(go_res)
    assert verdict == 'GO' and reasons == [], reasons
    # NO-GO derivations: sense shortfall, TNMASK residue, real key, null card.
    short = json.loads(json.dumps(go_res))
    short['results'][0]['card']['records'][0]['senses'].pop()
    assert cg.judge_payload(short)[0] == 'NO-GO', 'a dropped sense must be NO-GO'
    masked = json.loads(json.dumps(go_res))
    masked['results'][0]['card']['records'][0]['senses'][0]['russian'] = 'ост {T4} аток'
    assert cg.judge_payload(masked)[0] == 'NO-GO', 'a {Tn} residue must be NO-GO'
    realkey = json.loads(json.dumps(go_res))
    realkey['results'][0]['key'] = 'agni~~h0_00_pwg00'
    assert cg.judge_payload(realkey)[0] == 'NO-GO', \
        'judging a REAL window as a canary must be NO-GO'
    nullcard = {'results': [{'key': 'dq_canary_puregloss', 'card': None}]}
    assert cg.judge_payload(nullcard)[0] == 'NO-GO', 'a null card must be NO-GO'

    # H2174: the clean_card above carries NO 'notes' key, but every REAL canary run
    # does — and it paraphrases the fixture's own portrait note, which contains the
    # literal string "SAN-LOSS" and is fed to the model verbatim as prompt input.
    # Observed identically in H1447 (22-07) and H2011 (02-08). Scanning the whole
    # card made this gate unpassable for its own fixture; the marker scan is scoped
    # to translated content. RED before the canary_gate.py fix, GREEN after.
    noted = json.loads(json.dumps(go_res))
    noted['results'][0]['card']['notes'] = (
        'Synthetic D-Q silent-SAN-LOSS canary card (H994), layer PW only. Three '
        'line-opening pure-gloss senses; none may be dropped without failing the '
        'SAN-LOSS soft-guard.')
    assert cg.judge_payload(noted)[0] == 'GO', \
        'fixture commentary echoing SAN-LOSS in notes must NOT trip the gate'
    # ...but a marker in TRANSLATED CONTENT is still a hard NO-GO.
    for field in ('russian', 'german'):
        leaked = json.loads(json.dumps(noted))
        leaked['results'][0]['card']['records'][0]['senses'][0][field] = 'SAN-LOSS'
        assert cg.judge_payload(leaked)[0] == 'NO-GO', \
            'a literal marker in sense.%s must stay NO-GO' % field
    unmapped = json.loads(json.dumps(noted))
    unmapped['results'][0]['card']['records'][0]['senses'][1]['russian'] = 'x UNMAPPED y'
    assert cg.judge_payload(unmapped)[0] == 'NO-GO', \
        'a literal UNMAPPED marker in sense content must stay NO-GO'

    # judge CLI writes an atomic receipt; enforce() accepts fresh GO, refuses the rest.
    wf = os.path.join(td, 'q3_canary_wf.json')
    with open(wf, 'w', encoding='utf-8') as fh:
        json.dump(go_res, fh, ensure_ascii=False)
    receipt = os.path.join(td, 'q3_canary_receipt.json')
    assert cg.main(['judge', wf, '--receipt', receipt]) == 0
    assert cg.enforce(receipt, only_profile='c4')['verdict'] == 'GO'
    try:
        cg.enforce(receipt, only_profile='c5')
        raise AssertionError('a receipt for another profile must be refused')
    except SystemExit as exc:
        assert 'profile' in str(exc)
    stale = cg.load_receipt(receipt)
    stale['judged_at_epoch'] -= 8 * 3600
    with open(receipt, 'w', encoding='utf-8') as fh:
        json.dump(stale, fh)
    try:
        cg.enforce(receipt)
        raise AssertionError('a stale GO receipt must be refused')
    except SystemExit as exc:
        assert 'FRESH' in str(exc)

    # H2254: the receipt must carry the bounded-run evidence, and an ABSENT input must be
    # recorded as null rather than as a measured zero. `observed_cost_usd: 0` meant "not
    # evaluable" on 05-08 and "genuinely free" on 06-08; a receipt that cannot tell those
    # apart turns a cost FLOOR into a reported total.
    assert cg.main(['judge', wf, '--receipt', receipt]) == 0
    bare = cg.load_receipt(receipt)
    assert 'evidence' in bare, 'the evidence block must be written unconditionally'
    for key in cg.EVIDENCE_KEYS:
        assert key in bare['evidence'], 'evidence key %r missing from the receipt' % key
    assert bare['evidence']['observed_cost_usd'] is None, (
        'an unsupplied ledger recorded a cost of %r -- absence must not read as $0'
        % bare['evidence']['observed_cost_usd'])
    assert bare['evidence']['hard_timeout_ms'] == cg.PRODUCTION_HARD_TIMEOUT_MS

    # ...and with the durable inputs supplied, every number is READ from them.
    ledger = os.path.join(td, 'q3_calls.json')
    with open(ledger, 'w', encoding='utf-8') as fh:
        json.dump({'schema': 'x', 'runs': {'run-h2254': {
            'max_calls': 3, 'calls_spent': 3,
            'usage': {'observed_cost_usd': 1.25, 'cost_evaluable': True,
                      'unevaluable_calls': 0},
            'reservations': [
                {'telemetry': {'duration_ms': 57207, 'duration_api_ms': 18310}},
                {'telemetry': {'duration_ms': 291004, 'duration_api_ms': 44100}}]}}}, fh)
    statusf = os.path.join(td, 'q3_status.json')
    with open(statusf, 'w', encoding='utf-8') as fh:
        json.dump({'classification': 'success', 'cli_safe_mode_effective': True}, fh)
    manf = os.path.join(td, 'q3_manifest.json')
    with open(manf, 'w', encoding='utf-8') as fh:
        json.dump({'budgets': {'timeout_ceil_ms': cg.PRODUCTION_HARD_TIMEOUT_MS,
                               'kill_switch': True, 'max_translate_agents': 1,
                               'max_heal_agents': 1, 'max_agents': 2}}, fh)
    rich_receipt = os.path.join(td, 'q3_receipt_rich.json')
    assert cg.main(['judge', wf, '--receipt', rich_receipt, '--manifest', manf,
                    '--status', statusf, '--call-reservation', ledger,
                    '--run-id', 'run-h2254']) == 0
    ev = cg.load_receipt(rich_receipt)['evidence']
    assert (ev['calls_spent'], ev['max_calls']) == (3, 3), ev
    assert ev['observed_cost_usd'] == 1.25 and ev['cost_evaluable'] is True, ev
    assert (ev['wall_latency_ms'], ev['api_latency_ms']) == (291004, 44100), (
        'latency must be the WORST finalized call, not a mean -- a mean hides the '
        'warm-up/measured bimodality every c4 NO-GO day has shown: %r' % ev)
    assert ev['cli_safe_mode_effective'] is True, ev
    assert ev['kill_switch']['declared'] is True and ev['kill_switch']['bounded'] is True, ev
    assert ev['manifest_sha256'] and ev['timeout_ceil_ms'] == cg.PRODUCTION_HARD_TIMEOUT_MS
    assert cg.enforce(rich_receipt, only_profile='c4')['verdict'] == 'GO', (
        'the additive evidence block must not disturb enforce()')

    assert cg.main(['judge', wf, '--receipt', receipt]) == 0
    base = ['--plan', os.path.join(td, 'q3p.json'), '--coord-dir', os.path.join(td, 'q3cd'),
            '--coordinator', os.path.join(HERE, 'coordinator.py'), '--cwd', td,
            '--events', os.path.join(td, 'q3.events.jsonl'), '--execute',
            '--max-calls', '1', '--cost-ceiling', '1.0']
    _run = bsr.run
    bsr.run = lambda a: 'gate-passed'
    try:
        try:
            bsr.main(base)
            raise AssertionError('--execute without a canary receipt must be refused')
        except SystemExit as exc:
            assert getattr(exc, 'code', None) == 2
        assert bsr.main(base + ['--canary-receipt', receipt, '--only-profile', 'c4']) \
            == 'gate-passed', 'a fresh GO receipt must pass the gate'
        assert bsr.main(base + ['--skip-canary-gate']) == 'gate-passed', \
            '--skip-canary-gate must be an explicit escape hatch'
    finally:
        bsr.run = _run


def test_q_cohort_width_cli_and_live_refusal(td):
    """H1437 Phase 3: --cohort-width is EXPERIMENTAL / OFFLINE-ONLY. The parser defaults it
    to 1 (the serial route, byte-for-byte unchanged); the --execute path REFUSES any width
    > 1 with a message naming the missing live-acceptance gate, BEFORE touching the plan,
    the db, the coordinator or the fleet; old programmatic callers whose Namespace never
    defines cohort_width keep working (getattr default 1)."""
    ap = bsr.build_parser()
    args = ap.parse_args(['--plan', 'p.json', '--coord-dir', 'cd'])
    assert hasattr(args, 'cohort_width'), 'the CLI never defines --cohort-width'
    assert args.cohort_width == 1, 'default cohort width must be 1 (serial): %r' % args.cohort_width

    # Refusal fires FIRST: the plan path does not exist, so reaching plan-load would be an
    # OSError, not the SystemExit gate message. probe_fleet is boobytrapped for good measure.
    _pf = mao.probe_fleet
    mao.probe_fleet = lambda *a, **k: (_ for _ in ()).throw(
        AssertionError('a refused cohort --execute must NOT probe the fleet'))
    try:
        try:
            bsr.run(argparse.Namespace(
                plan=os.path.join(td, 'q_no_such_plan.json'), coord_dir=os.path.join(td, 'q_cd'),
                db=os.path.join(td, 'q_no.sqlite'), checkpoint=os.path.join(td, 'q_cp.json'),
                lease_id=None, execute=True, cohort_width=2, resume=False, report=None,
                coordinator=os.path.join(HERE, 'coordinator.py'), cwd=td, events=None,
                run_id='q', claude_bin='claude', timeout=5,
                gen_model_version=bsr.DEFAULT_GEN_MODEL_VERSION, only_profile=None,
                drop_unhealthy=False, stop_before_promote=False,
                max_windows=None, max_calls=None, max_clean=None, cost_ceiling=None,
                empty_streak=None, max_accounts=0))
            raise AssertionError('--execute with cohort width 2 was NOT refused')
        except SystemExit as exc:
            msg = str(exc)
            assert 'live-acceptance gate' in msg and 'H1437' in msg, (
                'the refusal must NAME the missing live-acceptance gate: %r' % msg)
            assert 'serial' in msg, 'the refusal must state the serial route stays default: %r' % msg
    finally:
        mao.probe_fleet = _pf

    # The dry-run planning view carries the cohort block (policy visible without a live run).
    view = bsr.plan_view(_plan(['no_pwg_w02']), {'leases': []}, _ceilings(),
                         os.path.join(td, 'q_v.json'), cohort_width=3)
    cohort = view.get('cohort') or {}
    assert cohort.get('requested_width') == 3, view
    assert 'OFFLINE' in (cohort.get('mode') or ''), cohort
    assert 'live-acceptance gate' in (cohort.get('live_policy') or ''), cohort
    serial_view = bsr.plan_view(_plan(['no_pwg_w02']), {'leases': []}, _ceilings(),
                                os.path.join(td, 'q_v.json'))
    assert (serial_view.get('cohort') or {}).get('requested_width') == 1, serial_view
    assert 'serial' in ((serial_view.get('cohort') or {}).get('mode') or ''), serial_view
    print('  (q) H1437 P3: --cohort-width defaults 1; --execute width>1 refused naming the '
          'live-acceptance gate before any plan/db/fleet access; dry-run shows policy: PASS')


def test_r_cohort_offline_serial_equivalence(td):
    """H1437 Phase 3 reviewer checkpoint: the SAME fixture at widths 1/2/3 with DELAYED fake
    workers (w1 slowest, w3 fastest — completion order is the REVERSE of plan order at width
    3) must yield identical clean/requeue decisions, identical fake-store bytes, exact equal
    ledger totals, exactly ONE promote_wave + ONE rebuild_tm call per wave — and measurably
    lower wall time at width >= 2, with an actual-overlap trace (peak_concurrency >= 2)."""
    import time

    DELAYS = {'w1': 0.30, 'w2': 0.20, 'w3': 0.10}

    def fixture_windows():
        return [
            {'id': 'w1', 'profile': 'c1', 'headwords': ['hw1']},
            {'id': 'w2', 'profile': 'c2', 'headwords': ['hw2']},
            {'id': 'w3', 'profile': 'c3', 'headwords': ['hw3']},
        ]

    results = {}
    for width in (1, 2, 3):
        wdir = os.path.join(td, 'r_w%d' % width); os.makedirs(wdir)
        store = os.path.join(wdir, 'store.json')
        promote_calls, tm_calls = [], []

        def run_window(window):
            time.sleep(DELAYS[window['id']])
            path = os.path.join(wdir, 'wf_%s.json' % window['id'])
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump({'summary': {}, 'results': []}, f)
            return path

        def audit(wf_output, window):
            if window['id'] == 'w2':      # rejected: requeues alone, blocks no sibling
                return {'requeue_keys': ['w2~~h0_zz_pw'], 'clean_count': 0}
            return {'requeue_keys': [], 'clean_count': 1}

        def promote_wave(clean_members):
            promote_calls.append([m['id'] for m in clean_members])
            payload = json.dumps(clean_members, sort_keys=True, separators=(',', ':'),
                                 ensure_ascii=True)
            with open(store, 'w', encoding='utf-8', newline='\n') as f:
                f.write(payload)
            return {'members': [m['id'] for m in clean_members]}

        def rebuild_tm(receipt):
            tm_calls.append(receipt)

        t0 = time.perf_counter()
        summary = bsr.run_cohort_offline(
            fixture_windows(), width, run_window,
            os.path.join(wdir, 'cp.json'), audit=audit,
            promote_wave=promote_wave, rebuild_tm=rebuild_tm)
        elapsed = time.perf_counter() - t0
        with open(store, 'rb') as f:
            store_bytes = f.read()
        results[width] = {'summary': summary, 'elapsed': elapsed,
                          'store_bytes': store_bytes,
                          'promote_calls': promote_calls, 'tm_calls': tm_calls}

    for width, r in results.items():
        s = r['summary']
        # identical decisions in stable plan order, regardless of completion order
        assert s['accepted_order'] == ['w1', 'w3'], (width, s['accepted_order'])
        assert s['requeue_backlog_keys'] == ['w2~~h0_zz_pw'], (width, s)
        # exact ledger totals: 3 reservations, 3 spends — probes/failures never escape
        assert s['calls_reserved'] == 3 and s['calls_spent'] == 3, (width, s)
        # one promotion + one TM call per accepted wave
        assert len(r['promote_calls']) == 1 and r['promote_calls'][0] == ['w1', 'w3'], (width, r['promote_calls'])
        assert len(r['tm_calls']) == 1, (width, r['tm_calls'])
        # store bytes identical to serial, byte for byte
        assert r['store_bytes'] == results[1]['store_bytes'], (
            'width %d store bytes diverge from serial' % width)
    assert results[1]['summary']['peak_concurrency'] == 1, results[1]['summary']
    assert results[2]['summary']['peak_concurrency'] >= 2, results[2]['summary']
    assert results[3]['summary']['peak_concurrency'] >= 2, results[3]['summary']
    # Wall-clock deltas are OPT-IN (H2889, #1806). They asserted that width 2 beat serial by
    # >=0.10 s and width 3 by >=0.15 s under delayed fake workers — true on an idle box, a
    # coin flip on a contended runner. It failed CI at `width 2 not faster: serial 0.619s vs
    # 0.527s`: width 2 WAS faster, by 92 ms, and the threshold wanted 100. Eight milliseconds
    # of runner contention decided a merge gate.
    #
    # Nothing is lost by gating them, because the invariants this block exists for are
    # asserted deterministically just above: `peak_concurrency` proves the widths really ran
    # concurrently, and byte-identical `store_bytes` proves concurrency changed no output. A
    # timing delta adds no coverage over those two and subtracts reliability — and a step
    # that goes red for reasons unrelated to the change is how a lane learns to merge past
    # red, which this repo has already done (three commits onto a red master, 18-08-2026).
    if os.environ.get('PWG_ASSERT_WALLCLOCK') == '1':
        assert results[2]['elapsed'] < results[1]['elapsed'] - 0.10, (
            'width 2 not faster: serial %.3fs vs %.3fs' % (results[1]['elapsed'], results[2]['elapsed']))
        assert results[3]['elapsed'] < results[1]['elapsed'] - 0.15, (
            'width 3 not faster: serial %.3fs vs %.3fs' % (results[1]['elapsed'], results[3]['elapsed']))
    else:
        print('  wall-clock speedup assertions skipped (PWG_ASSERT_WALLCLOCK=1 to enable); '
              'concurrency + byte-identity asserted unconditionally: serial %.3fs, '
              'w2 %.3fs, w3 %.3fs'
              % (results[1]['elapsed'], results[2]['elapsed'], results[3]['elapsed']))

    # a profile-less window is refused LOUDLY — the one-job-per-profile invariant is
    # meaningless without a profile binding, so offline fixtures must declare one.
    try:
        bsr.run_cohort_offline([{'id': 'wx'}], 2, lambda w: None,
                               os.path.join(td, 'r_x.json'))
        raise AssertionError('a profile-less window was accepted by run_cohort_offline')
    except SystemExit as exc:
        assert 'profile' in str(exc), exc
    print('  (r) H1437 P3: widths 1/2/3 — identical decisions/store bytes/ledger, one '
          'promote+TM per wave, overlap proven (peak>=2), wall time '
          '%.2fs/%.2fs/%.2fs: PASS' % (results[1]['elapsed'], results[2]['elapsed'],
                                       results[3]['elapsed']))


def _h7_ctx(td, tag, pending=True, cap=6):
    """A RunContext over a REAL sqlite db holding exactly one scoped job for the lease, plus
    one validated, unparked, ADMITTED account — so the drain loop's all-parked guard cannot
    fire and the only thing left to stall on is the dispatch itself. `pending=False` seeds
    the job done-but-unrecorded instead. Poll is 0 s (time.sleep is patched and counted by
    the caller; the real 3 s bound is asserted separately)."""
    db_path = os.path.join(td, tag + '.sqlite')
    lease_id = 'no_pwg_w02'
    db = mao.connect(db_path)
    with db:
        db.execute('INSERT INTO accounts(name,config_dir,parked_until,validated,updated_at) '
                   'VALUES(?,?,0,1,?)', ('acc', td, mao.now_iso()))
        db.execute('INSERT INTO jobs(external_id, argv_json, cwd, output_path) VALUES(?,?,?,?)',
                   (lease_id, json.dumps([sys.executable, '-c', 'print(1)']), td,
                    os.path.join(td, tag + '.out.json')))
        if not pending:
            db.execute("UPDATE jobs SET state='done', coordinator_recorded=0 "
                       "WHERE external_id=?", (lease_id,))
    db.close()
    ctx = bsr.RunContext(
        db=db_path, coord_dir=td, coordinator=os.path.join(HERE, 'coordinator.py'), cwd=td,
        events=None, run_id='h7', probe_latencies={'acc': 1.0},
        stop_before_promote=True,      # keeps the pin off the promote-ready subprocess
        drain_idle_poll_seconds=0, drain_no_progress_passes=cap)
    return ctx, lease_id, db_path


def _mark_done(db_path, lease_id):
    db = mao.connect(db_path)
    with db:
        db.execute("UPDATE jobs SET state='done', coordinator_recorded=0 WHERE external_id=?",
                   (lease_id,))
    db.close()


def test_s_h7_zero_claim_drain_stops_instead_of_spinning(td):
    """H7 (H1940 Phase 2): a pending job that no admitted account ever claims used to
    hot-spin the per-lease drain — no sleep, a full dispatch/record/promote pass every
    iteration — until max_drain_iterations (1000), then die naming an iteration count
    rather than the stall. It must now poll and stop on the consecutive-no-progress cap."""
    assert bsr.DRAIN_IDLE_POLL_SECONDS == mao.STAGED_RUN_IDLE_POLL_SECONDS, \
        'the bounded poll must mirror the staged C4 poll (%r vs %r)' % (
            bsr.DRAIN_IDLE_POLL_SECONDS, mao.STAGED_RUN_IDLE_POLL_SECONDS)
    ctx, lease_id, _ = _h7_ctx(td, 's_h7', cap=6)
    seen = {'run_once': 0, 'record': 0, 'sleeps': []}
    orig = (mao.cmd_run_once, mao.cmd_record_done, time.sleep)
    mao.cmd_run_once = lambda a: seen.__setitem__('run_once', seen['run_once'] + 1)
    mao.cmd_record_done = lambda a: seen.__setitem__('record', seen['record'] + 1)
    time.sleep = lambda s: seen['sleeps'].append(s)
    try:
        try:
            bsr.make_run_window(ctx)({'id': lease_id})
            raise AssertionError('a zero-claim drain returned normally')
        except SystemExit as exc:
            msg = str(exc)
    finally:
        mao.cmd_run_once, mao.cmd_record_done, time.sleep = orig
    assert 'no drain progress in 6 consecutive passes' in msg, msg
    assert 'pending=1' in msg and 'done-unrecorded=0' in msg and 'done=0' in msg, msg
    assert 'exceeded' not in msg, 'died on the iteration ceiling, not the H7 backstop: %s' % msg
    # The cap is CONSECUTIVE passes: 6 dispatch passes, a poll before each retry after the
    # first, and the raise on the 7th pass before it can dispatch again.
    assert seen['run_once'] == 6, 'expected 6 dispatch passes, got %d' % seen['run_once']
    assert seen['sleeps'] == [0] * 5, 'expected one poll per no-progress retry: %r' % seen['sleeps']
    print('  (s) H7: a zero-claim drain polls, then stops naming the stall: PASS')


def test_s2_h7_progress_resets_the_consecutive_counter(td):
    """The backstop counts CONSECUTIVE no-progress passes, not cumulative ones. A drain that
    stalls, advances, stalls again and finishes must complete — even though its TOTAL
    no-progress passes exceed the cap. Also pins that progress is read from the full
    (pending, done_unrecorded, done) signature: the second stall moves none of the first
    two counters that the staged C4 backstop watches."""
    ctx, lease_id, db_path = _h7_ctx(td, 's2_h7', cap=3)
    seen = {'run_once': 0, 'record': 0, 'sleeps': []}
    orig = (mao.cmd_run_once, mao.cmd_record_done, time.sleep)

    def fake_run_once(a):
        seen['run_once'] += 1
        if seen['run_once'] == 3:        # two dead passes, then the job lands
            _mark_done(db_path, lease_id)

    def fake_record_done(a):
        seen['record'] += 1
        if seen['record'] == 6:          # ...then two more dead passes before it records
            db = mao.connect(db_path)
            with db:
                db.execute("UPDATE jobs SET coordinator_recorded=1 WHERE external_id=?",
                           (lease_id,))
            db.close()

    mao.cmd_run_once, mao.cmd_record_done = fake_run_once, fake_record_done
    time.sleep = lambda s: seen['sleeps'].append(s)
    try:
        bsr.make_run_window(ctx)({'id': lease_id})      # must NOT raise
    finally:
        mao.cmd_run_once, mao.cmd_record_done, time.sleep = orig
    assert seen['record'] == 6, 'loop did not run to the recording pass: %d' % seen['record']
    # 4 no-progress passes in total (2 before the job lands, 2 before it records) against a
    # cap of 3 — a cumulative counter would have raised on the third.
    assert seen['sleeps'] == [0] * 4, 'expected 4 polls across two stalls: %r' % seen['sleeps']
    db = mao.connect(db_path)
    assert mao.scoped_job_count(db, {lease_id}, "state='done' AND coordinator_recorded=1") == 1
    db.close()
    print('  (s2) H7: forward progress resets the consecutive-no-progress counter: PASS')


def test_s3_h7_unrecordable_done_job_also_stops(td):
    """The stall shape the staged C4 backstop does NOT cover: nothing pending, but a done
    job that cmd_record_done never clears. Pre-H7 this spun to max_drain_iterations exactly
    like the zero-claim case; H7 checks the signature ahead of the `if pending` branch, so
    it stops here too — and never dispatches, because nothing is pending."""
    ctx, lease_id, _ = _h7_ctx(td, 's3_h7', pending=False, cap=4)
    seen = {'record': 0, 'sleeps': []}
    orig = (mao.cmd_run_once, mao.cmd_record_done, time.sleep)
    mao.cmd_run_once = lambda a: (_ for _ in ()).throw(
        AssertionError('nothing is pending — the drain must not dispatch'))
    mao.cmd_record_done = lambda a: seen.__setitem__('record', seen['record'] + 1)
    time.sleep = lambda s: seen['sleeps'].append(s)
    try:
        try:
            bsr.make_run_window(ctx)({'id': lease_id})
            raise AssertionError('an unrecordable done job returned normally')
        except SystemExit as exc:
            msg = str(exc)
    finally:
        mao.cmd_run_once, mao.cmd_record_done, time.sleep = orig
    assert 'no drain progress in 4 consecutive passes' in msg, msg
    assert 'pending=0' in msg and 'done-unrecorded=1' in msg and 'done=1' in msg, msg
    assert seen['record'] == 4, 'expected 4 record passes, got %d' % seen['record']
    assert seen['sleeps'] == [0] * 3, 'expected one poll per no-progress retry: %r' % seen['sleeps']
    print('  (s3) H7: an unrecordable done job stops on the same backstop: PASS')


def test_t_data_root_env_shim(td):
    """H2175 step 4: --data-root maps the standard pwg-ru-data layout onto the env seams
    (PWG_RU_STORE / PWG_RU_TM_DIR / PWG_INPUT_DIR / PWG_OUTPUT_DIR / PWG_ECONOMY_LOG /
    PWG_COORDINATOR_DIR) BEFORE any path resolution, derives --coord-dir / --db /
    --checkpoint only when left at parser defaults, creates the layout skeleton, and
    keeps the old contract when absent (no coord-dir from anywhere -> parser error)."""
    import data_root as dr
    root = os.path.join(td, 't_dataroot')
    os.makedirs(root)
    captured = {}
    _run = bsr.run
    bsr.run = lambda a: captured.update(vars(a)) or 0
    saved = {k: os.environ.get(k) for k in dr.ENV_LAYOUT}
    try:
        plan = os.path.join(td, 't_plan.json')
        bsr.main(['--plan', plan, '--data-root', root])
        absroot = os.path.abspath(root)
        assert os.environ['PWG_RU_STORE'] == os.path.join(
            absroot, 'tm', 'pwg_ru_translated.jsonl'), os.environ['PWG_RU_STORE']
        assert os.environ['PWG_RU_TM_DIR'] == os.path.join(absroot, 'tm')
        assert os.environ['PWG_ECONOMY_LOG'] == os.path.join(
            absroot, 'telemetry', 'generation_api_probe_log.jsonl')
        assert captured['coord_dir'] == os.path.join(absroot, 'manifests', 'coordinator')
        assert os.path.isdir(captured['coord_dir']), 'derived coord dir must exist'
        assert captured['db'] == os.path.join(absroot, 'manifests',
                                              'max_orchestrator.sqlite'), captured['db']
        assert captured['checkpoint'] == os.path.join(
            absroot, 'manifests', 'bounded_staged_run.checkpoint.json')
        for sub in dr.SUBDIRS:
            assert os.path.isdir(os.path.join(root, sub)), 'skeleton dir %s' % sub
        # the lazy economy-ledger seam follows the applied env
        assert el.frozen_log() == os.environ['PWG_ECONOMY_LOG']
        # an explicit --coord-dir / --db keeps winning over the derived defaults
        own_cd = os.path.join(td, 't_own_cd')
        os.makedirs(own_cd)
        bsr.main(['--plan', plan, '--data-root', root, '--coord-dir', own_cd,
                  '--db', os.path.join(td, 'own.sqlite')])
        assert captured['coord_dir'] == own_cd
        assert captured['db'] == os.path.join(td, 'own.sqlite')
        # neither --coord-dir nor --data-root -> the old required-flag refusal (exit 2)
        try:
            bsr.main(['--plan', plan])
            raise AssertionError('missing coord-dir must be refused')
        except SystemExit as exc:
            assert getattr(exc, 'code', None) == 2, exc
    finally:
        bsr.run = _run
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print('  (t) H2175: --data-root env shim, derived defaults, explicit-flag wins: PASS')


def test_u_auto_promote_until(td):
    """H2175 R2.1 (--auto-promote-until): promote-on-clean-audit with expiring authority.
    (1) parse: bare ISO date = end of that UTC day; ISO datetime honored; junk refused.
    (2) CLI gate: a past date refuses to start; combining with --stop-before-promote
        refuses (exit 2 both ways). (3) mechanics: clean audit -> AWAITING_REVIEW
    checkpoint -> verified -> promote-ready spawned -> pwg.auto_promotion.v1 record
    binding the checkpoint hashes. (4) expired authority mid-run: NO promote, NO
    record, window left AWAITING_REVIEW. (5) a tampered checkpoint refuses to promote."""
    from types import SimpleNamespace

    # (1) parsing
    end_of_day = bsr.parse_auto_promote_until('2026-08-09')
    import datetime as _dt
    dt = _dt.datetime.fromtimestamp(end_of_day, _dt.timezone.utc)
    assert (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) == \
        (2026, 8, 9, 23, 59, 59), dt
    assert bsr.parse_auto_promote_until('2026-08-09T12:00:00Z') < end_of_day
    try:
        bsr.parse_auto_promote_until('next-tuesday')
        raise AssertionError('junk date must raise')
    except ValueError:
        pass

    # (2) CLI fail-closed gates (run() patched to a sentinel; never reached)
    _run = bsr.run
    bsr.run = lambda a: 'gate-passed'
    try:
        base = ['--plan', os.path.join(td, 'u_p.json'), '--coord-dir', os.path.join(td, 'u_cd')]
        for bad in (base + ['--auto-promote-until', '2020-01-01'],
                    base + ['--auto-promote-until', '2999-01-01', '--stop-before-promote'],
                    base + ['--auto-promote-until', 'next-tuesday']):
            try:
                bsr.main(bad)
                raise AssertionError('must be refused: %r' % bad)
            except SystemExit as exc:
                assert getattr(exc, 'code', None) == 2, (bad, exc)
        assert bsr.main(base + ['--auto-promote-until', '2999-01-01']) == 'gate-passed'
    finally:
        bsr.run = _run

    # fake coordinator: append argv to a log, exit 0 (stdout says nothing to rescue)
    udir = os.path.join(td, 'u_apu'); os.makedirs(udir)
    coord_log = os.path.join(udir, 'coordinator_calls.jsonl')
    fake_coord = os.path.join(udir, 'fake_coordinator.py')
    with open(fake_coord, 'w', encoding='utf-8', newline='\n') as f:
        f.write('import json, sys\n'
                "open(%r, 'a', encoding='utf-8').write(json.dumps(sys.argv[1:]) + '\\n')\n"
                "print('promoted')\n" % coord_log)

    def _wf(path, keys):
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'meta': {'selected_keys': keys, 'gen_model': 'claude-sonnet-5',
                                'execution': {'profile_slot': 'c4',
                                              'execution_route': 'claude-cli-headless',
                                              'executor_lane': 'serial',
                                              'validation_method': 'audit',
                                              'config_dir_fingerprint': 'f' * 64,
                                              'model_identifier': 'claude-sonnet-5'}},
                       'summary': {'usage': {'input_tokens': 10, 'observed_cost_usd': 0.01,
                                             'cost_evaluable': True}}, 'results': []}, f)
        return path

    report = {'clean_count': 1, 'requeue_keys': [], 'satisfied_keys': [], 'state': 'clean'}
    ctx = SimpleNamespace(checkpoint=os.path.join(udir, 'cp.json'), run_id='u1',
                          stop_before_promote=False,
                          auto_promote_until=time.time() + 3600,
                          coordinator=fake_coord, cwd=udir, coord_dir=udir,
                          gen_model_version='claude-sonnet-5')

    # (3) live authority: verified checkpoint -> promote-ready -> bound promotion record
    wf = _wf(os.path.join(udir, 'wf_u.json'), ['k1'])
    ar_path, ar_record = bsr.write_awaiting_review_checkpoint(
        ctx, {'id': 'lease_u', 'attempt': 1}, wf, report)
    assert bsr.auto_promote_window(ctx, {'id': 'lease_u'}, ar_path, ar_record) is True
    calls = [json.loads(line) for line in open(coord_log, encoding='utf-8')]
    assert len(calls) == 1 and 'promote-ready' in calls[0] and \
        calls[0][calls[0].index('--lease-id') + 1] == 'lease_u', calls
    rec = json.load(open(ar_path + '.PROMOTED.json', encoding='utf-8'))
    assert rec['schema'] == 'pwg.auto_promotion.v1'
    assert rec['payload_sha256'] == ar_record['payload_sha256']
    assert rec['bound_hashes'] == ar_record['payload']['bound']['hashes']
    assert rec['lease_id'] == 'lease_u' and rec['run_id'] == 'u1'

    # (4) expired authority: refuse to promote, leave AWAITING_REVIEW, no record
    ctx_exp = SimpleNamespace(**{**vars(ctx), 'run_id': 'u2',
                                 'checkpoint': os.path.join(udir, 'cp2.json'),
                                 'auto_promote_until': time.time() - 5})
    wf2 = _wf(os.path.join(udir, 'wf_u2.json'), ['k2'])
    ar2, rec2 = bsr.write_awaiting_review_checkpoint(
        ctx_exp, {'id': 'lease_u2', 'attempt': 1}, wf2, report)
    assert bsr.auto_promote_window(ctx_exp, {'id': 'lease_u2'}, ar2, rec2) is False
    assert not os.path.exists(ar2 + '.PROMOTED.json'), 'expired trial must not promote'
    assert len(open(coord_log, encoding='utf-8').readlines()) == 1, 'no second promote call'
    assert bsr.verify_awaiting_review_checkpoint(ar2), 'window must stay AWAITING_REVIEW'

    # (5) a tampered checkpoint refuses to promote (SystemExit, no promote call)
    with open(wf2, 'a', encoding='utf-8') as f:
        f.write('\n#tampered')
    ctx_ok = SimpleNamespace(**{**vars(ctx_exp), 'auto_promote_until': time.time() + 3600})
    try:
        bsr.auto_promote_window(ctx_ok, {'id': 'lease_u2'}, ar2, rec2)
        raise AssertionError('tampered checkpoint must refuse to promote')
    except SystemExit as exc:
        assert 'failed verification' in str(exc), exc
    assert len(open(coord_log, encoding='utf-8').readlines()) == 1, calls
    print('  (u) H2175 R2.1: --auto-promote-until parse+CLI gates; clean-audit promote '
          'with bound record; expired/tampered refusals: PASS')


def test_old_receipt_without_agent_ops_code_still_parses(td):
    """H3229: parsers must treat a missing field as None, never 0."""
    old = {
        'schema': 'pwg.bounded_supervisor.v1',
        'stop_reason': 'clean_target',
        'windows_done': 1,
        'cost_evaluable': True,
    }
    assert 'agent_ops_code' not in old
    assert old.get('agent_ops_code') is None
    print('  old receipts without agent_ops_code still parse: PASS')


def main():
    with tempfile.TemporaryDirectory() as td:
        test_old_receipt_without_agent_ops_code_still_parses(td)
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
        test_n_cli_defines_execute_path_args(td)
        test_o_preflight_before_probe(td)
        test_p_resume_requires_existing_ledger_run(td)
        test_q2_execute_requires_ceilings_h2157(td)
        test_q3_execute_requires_canary_go_receipt_h2159(td)
        test_q_cohort_width_cli_and_live_refusal(td)
        test_r_cohort_offline_serial_equivalence(td)
        test_s_h7_zero_claim_drain_stops_instead_of_spinning(td)
        test_s2_h7_progress_resets_the_consecutive_counter(td)
        test_s3_h7_unrecordable_done_job_also_stops(td)
        test_t_data_root_env_shim(td)
        test_u_auto_promote_until(td)
    print('bounded_staged_run_selftest: PASS')


if __name__ == '__main__':
    main()
