#!/usr/bin/env python
r"""Hermetic self-test for bounded_supervisor.py (H960 gap #6).

Zero live generation: run_window is a scripted fake that writes a trivial fixture
wf_output JSON in a tempdir and records call order; the auditor is an injected fake
returning scripted requeue/clean/cost/satisfied reports. Every one of the gap's bound
cases is exercised end to end:

  (a) window-count bound stops after exactly N
  (b) clean-target bound stops when queue + backlog are both drained
  (c) requeue-partials: reported keys are appended as ONE work-item and pulled BEFORE any
      new plan window next iteration
  (d) running-budget bound stops mid-queue once accumulated cost crosses the cap
  (e) consecutive-empty bound stops on the zero-progress streak
  (f) crash recovery: re-instantiate from the persisted checkpoint and resume at the right
      index/budget/backlog with NO completed window re-run
  (g) an already-promoted requeue key with zero store-delta is satisfied-not-failed
  (h) the offline default H920 auditor requeues a null card hermetically (no live gen)

  python src/pilot/bounded_supervisor_selftest.py
"""
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bounded_supervisor as bs
from bounded_supervisor import (
    BoundedSupervisor,
    STOP_WINDOW_COUNT,
    STOP_BUDGET,
    STOP_CLEAN_TARGET,
    STOP_CONSECUTIVE_EMPTY,
)


def _safe(name):
    return re.sub(r'[^A-Za-z0-9]+', '_', str(name))


class ScriptedRunner:
    """Fake run_window: records the order of windows run and returns a fixture wf_output
    path (a trivial JSON file in the tempdir). Optionally raises on the Nth call to
    simulate a mid-loop crash for the recovery test."""

    def __init__(self, td, raise_on_call=None):
        self.td = td
        self.raise_on_call = raise_on_call
        self.run_order = []       # window ids, in run order
        self.run_windows = []     # full window items

    def __call__(self, window):
        self.run_windows.append(window)
        self.run_order.append(window['id'])
        if self.raise_on_call is not None and len(self.run_order) == self.raise_on_call:
            raise RuntimeError('simulated crash while running %s' % window['id'])
        path = os.path.join(self.td, 'wf_%s.json' % _safe(window['id']))
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'meta': {}, 'results': []}, f)
        return path


def make_plan(n):
    return [{'id': 'w%d' % i, 'keys': ['k_%d' % i]} for i in range(n)]


def clean_report(cost=1):
    return {'requeue_keys': [], 'clean_count': 1, 'cost': cost, 'satisfied_keys': []}


# ---------------------------------------------------------------------------

def test_a_window_count(td):
    plan = make_plan(5)
    runner = ScriptedRunner(td)

    def audit(wf_output, window):
        return clean_report()

    cp = os.path.join(td, 'a.json')
    sup = BoundedSupervisor(plan, runner, cp, audit=audit, max_windows=3)
    summ = sup.run()
    assert summ['stop_reason'] == STOP_WINDOW_COUNT, summ
    assert summ['windows_done'] == 3, summ
    assert runner.run_order == ['w0', 'w1', 'w2'], runner.run_order
    print('  (a) window-count bound stops after exactly N: PASS')


def test_b_clean_target(td):
    plan = make_plan(2)
    runner = ScriptedRunner(td)

    def audit(wf_output, window):
        return clean_report()

    cp = os.path.join(td, 'b.json')
    sup = BoundedSupervisor(plan, runner, cp, audit=audit, max_windows=10)
    summ = sup.run()
    assert summ['stop_reason'] == STOP_CLEAN_TARGET, summ
    assert summ['windows_done'] == 2, summ
    assert runner.run_order == ['w0', 'w1'], runner.run_order
    print('  (b) clean-target bound stops when queue+backlog drained: PASS')


def test_c_requeue_partials(td):
    plan = make_plan(2)
    runner = ScriptedRunner(td)
    reports = {
        'w0': {'requeue_keys': ['k1', 'k2'], 'clean_count': 1, 'cost': 1},
        'w1': clean_report(),
    }

    def audit(wf_output, window):
        if window.get('requeue'):
            # rework of the requeued keys comes back clean
            return {'requeue_keys': [], 'clean_count': 1, 'cost': 1}
        return reports[window['id']]

    cp = os.path.join(td, 'c.json')
    sup = BoundedSupervisor(plan, runner, cp, audit=audit, max_windows=10)
    summ = sup.run()
    # The requeue work-item (rq-001-w0) must run right after w0 and BEFORE the new plan
    # window w1.
    assert runner.run_order == ['w0', 'rq-001-w0', 'w1'], runner.run_order
    # Exactly the reported keys were appended, as one work-item.
    rq_items = [w for w in runner.run_windows if w.get('requeue')]
    assert len(rq_items) == 1, rq_items
    assert rq_items[0]['keys'] == ['k1', 'k2'], rq_items[0]
    assert rq_items[0]['origin'] == 'w0', rq_items[0]
    assert summ['stop_reason'] == STOP_CLEAN_TARGET, summ
    assert summ['windows_done'] == 3, summ
    print('  (c) requeue-partials appended and pulled before new windows: PASS')


def test_d_budget(td):
    plan = make_plan(10)
    runner = ScriptedRunner(td)

    def audit(wf_output, window):
        return clean_report(cost=1)

    cp = os.path.join(td, 'd.json')
    sup = BoundedSupervisor(plan, runner, cp, audit=audit, budget_cap=3)
    summ = sup.run()
    assert summ['stop_reason'] == STOP_BUDGET, summ
    assert summ['budget_spent'] == 3, summ
    assert summ['windows_done'] == 3, summ
    assert summ['next_index'] == 3 and summ['next_index'] < len(plan), summ  # stopped mid-queue
    assert runner.run_order == ['w0', 'w1', 'w2'], runner.run_order
    print('  (d) budget bound stops mid-queue at the cap: PASS')


def test_e_consecutive_empty(td):
    plan = make_plan(10)
    runner = ScriptedRunner(td)

    def audit(wf_output, window):
        # zero-progress: no clean cards, no requeue, no satisfied keys
        return {'requeue_keys': [], 'clean_count': 0, 'cost': 0, 'satisfied_keys': []}

    cp = os.path.join(td, 'e.json')
    sup = BoundedSupervisor(plan, runner, cp, audit=audit, empty_streak_cap=3)
    summ = sup.run()
    assert summ['stop_reason'] == STOP_CONSECUTIVE_EMPTY, summ
    assert summ['windows_done'] == 3, summ
    assert summ['empty_streak'] == 3, summ
    print('  (e) consecutive-empty bound stops on the zero-progress streak: PASS')


def test_f_crash_recovery(td):
    plan = make_plan(5)
    cp = os.path.join(td, 'f.json')

    # Supervisor A crashes while running the 3rd window (after 2 completed + checkpointed).
    runner_a = ScriptedRunner(td, raise_on_call=3)
    sup_a = BoundedSupervisor(plan, runner_a, cp, audit=lambda wf, w: clean_report(cost=2),
                              max_windows=None)
    crashed = False
    try:
        sup_a.run()
    except RuntimeError:
        crashed = True
    assert crashed, 'expected a simulated crash on the 3rd window'
    assert runner_a.run_order == ['w0', 'w1', 'w2'], runner_a.run_order  # w2 raised

    # The persisted checkpoint reflects the 2 COMPLETED windows only.
    state = json.load(open(cp, encoding='utf-8'))
    assert state['windows_done'] == 2, state
    assert state['next_index'] == 2, state          # w2 was not committed
    assert state['budget_spent'] == 4, state         # 2 windows * cost 2
    assert state['stop_reason'] is None, state       # crashed mid-loop, not a clean stop

    # Supervisor B resumes from the checkpoint with a raised window cap.
    runner_b = ScriptedRunner(td)
    sup_b = BoundedSupervisor.from_checkpoint(cp, plan, runner_b,
                                              audit=lambda wf, w: clean_report(cost=2),
                                              max_windows=10)
    assert sup_b.windows_done == 2, sup_b.windows_done
    assert sup_b.budget_spent == 4, sup_b.budget_spent
    assert sup_b.next_index == 2, sup_b.next_index
    summ = sup_b.run()
    # No completed window (w0/w1) is ever re-run; the resume picks up at w2.
    assert runner_b.run_order == ['w2', 'w3', 'w4'], runner_b.run_order
    assert summ['windows_done'] == 5, summ
    assert summ['budget_spent'] == 10, summ          # 4 carried + 3 * 2
    assert summ['stop_reason'] == STOP_CLEAN_TARGET, summ
    print('  (f) crash recovery resumes at the right index/budget, no window re-run: PASS')


def test_g_satisfied_zero_delta(td):
    plan = make_plan(1)
    runner = ScriptedRunner(td)

    def audit(wf_output, window):
        if window.get('requeue'):
            # k9 was already promoted by w0 -> zero store-delta -> satisfied, NOT a failure.
            return {'requeue_keys': [], 'clean_count': 0, 'cost': 0,
                    'satisfied_keys': ['k9']}
        return {'requeue_keys': ['k9'], 'clean_count': 1, 'cost': 1, 'satisfied_keys': []}

    cp = os.path.join(td, 'g.json')
    # empty_streak_cap=1: if a satisfied requeue key were (wrongly) counted as a zero-
    # progress iteration, the requeue window would trip the consecutive-empty bound. It
    # must instead be treated as progress, so the loop drains to clean-target.
    raised = False
    try:
        sup = BoundedSupervisor(plan, runner, cp, audit=audit,
                                max_windows=10, empty_streak_cap=1)
        summ = sup.run()
    except Exception as exc:  # noqa: BLE001 — a satisfied key must never be a hard error
        raised = True
        summ = None
    assert not raised, 'a zero-store-delta requeue key must not be a hard error'
    assert summ['stop_reason'] == STOP_CLEAN_TARGET, summ
    assert summ['windows_done'] == 2, summ
    assert summ['requeue_backlog_len'] == 0, summ    # k9 was NOT re-requeued
    # The requeue window recorded k9 as satisfied, not requeued.
    rq_hist = [h for h in sup.history if h['requeue']]
    assert len(rq_hist) == 1, rq_hist
    assert rq_hist[0]['satisfied_keys'] == ['k9'], rq_hist[0]
    assert rq_hist[0]['requeued_keys'] == [], rq_hist[0]
    print('  (g) already-promoted zero-delta requeue key is satisfied-not-failed: PASS')


def test_h_default_h920_auditor(td):
    # Exercise the offline default auditor (H920 sense-count gate on a temp input dir).
    # A wf_output with one null card and one good card -> null card requeued, good clean.
    wf = os.path.join(td, 'wf_default.json')
    with open(wf, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'meta': {}, 'results': [
            {'key': 'good~~h0_zz_pw', 'card': {'records': [{'senses': [{'gloss': 'x'}]}]}},
            {'key': 'null~~h0_zz_pw', 'card': None},
        ]}, f)

    plan = [{'id': 'w0', 'keys': ['good~~h0_zz_pw', 'null~~h0_zz_pw']}]
    runner = ScriptedRunner(td)

    def run_window(window):
        runner(window)
        return wf   # return the pre-built fixture wf_output

    cp = os.path.join(td, 'h.json')
    empty_input = tempfile.mkdtemp(prefix='bs_empty_input_')
    # No injected auditor -> the default H920 auditor runs.
    sup = BoundedSupervisor(plan, run_window, cp, max_windows=1, input_dir=empty_input)
    sup.run()
    assert sup.history, sup.history
    h0 = sup.history[0]
    assert h0['requeued_keys'] == ['null~~h0_zz_pw'], h0   # null card requeued (transient)
    assert h0['clean_count'] == 1, h0                       # the good card counts clean
    print('  (h) default H920 auditor requeues a null card hermetically: PASS')


def main():
    with tempfile.TemporaryDirectory() as td:
        test_a_window_count(td)
        test_b_clean_target(td)
        test_c_requeue_partials(td)
        test_d_budget(td)
        test_e_consecutive_empty(td)
        test_f_crash_recovery(td)
        test_g_satisfied_zero_delta(td)
        test_h_default_h920_auditor(td)
    print('bounded_supervisor_selftest: PASS')


if __name__ == '__main__':
    main()
