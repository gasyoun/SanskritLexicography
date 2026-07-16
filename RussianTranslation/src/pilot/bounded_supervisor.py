#!/usr/bin/env python
r"""bounded_supervisor.py — a self-contained, bounded continuous-run supervisor for the
no-PWG drain lane (the offline half of the 'nonstop' scaffolding, H960 gap #6).

WHAT THIS IS (and is NOT)
-------------------------
This module is the *offline, hermetic* control loop that a continuous ("nonstop") drain
would sit inside: pull a window from a plan, run it, audit the output, requeue the
partials, and stop the moment a bound is crossed — persisting its whole state to a JSON
checkpoint every iteration so a crash resumes exactly where it left off.

It is deliberately SEPARABLE from live generation. The one thing it does NOT own is the
actual model call: that is injected as a `run_window(window) -> wf_output_path` callable.
Production would wrap the live staged-run/promotion path (max_account_orchestrator
cmd_staged_run + coordinator promotion) in that callable; the self-test injects a
fixture-returning fake and does ZERO live generation. Wiring this loop to the real
cmd_staged_run against validated accounts is a LIVE-GATED follow-up (H960 gap #6 verify
verdict: SPLIT) and is intentionally NOT implemented here.

Design constraints honoured (all from the gap spec):
  * The loop is driven by a SUPPLIED plan list — it never calls no_pwg_scale_plan against
    the gitignored local store (that read is non-hermetic and would re-offer promoted
    headwords).
  * Auditing never shells out to audit_window.main() (its INPUT_DIR module constant is
    bound to the untracked live input dir). Instead the loop accepts an injected
    requeue-key report, or falls back to the H920 sense-count gate helper
    (sense_count.scan_sense_shortfall) pointed at a caller-supplied tmp dir.

THE AUDIT REPORT CONTRACT
-------------------------
The injected `audit(wf_output_path, window) -> report` returns a plain dict. Recognised
fields (all optional, safe defaults shown):
  requeue_keys   : list[str]  keys that still need rework -> appended as a requeue
                              work-item and pulled BEFORE any new plan window next round.
  clean_count    : int        clean cards this window (0). Drives the consecutive-empty
                              streak and the clean-target signal.
  cost           : number     per-window cost accumulated toward the running-budget cap
                              (0). Overridable via an injected cost_fn.
  satisfied_keys : list[str]  requeue keys resolved with a ZERO canonical-store delta —
                              i.e. an already-promoted key. These are treated as
                              satisfied-not-failed: they are NOT re-requeued and NOT a
                              hard error (a zero store_delta on a fresh promotion is the
                              coordinator's hard-fail signal, but on a REQUEUE key it just
                              means the earlier window already landed it). ([]).

THE CHECKPOINT
--------------
Every iteration the full loop state is written atomically (temp file + os.replace) to
`checkpoint_path` as `pwg.bounded_supervisor.v1`. Re-instantiating with `resume=True`
(or via `from_checkpoint`) restores windows_done / budget_spent / requeue_backlog /
empty_streak / next_index / completed_window_ids, so no completed window is ever re-run
and no spent budget is double-counted.

Pure control flow: no model calls, no network, no store mutation, no promotion. The only
side effect is writing the JSON checkpoint.
"""
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SCHEMA = 'pwg.bounded_supervisor.v1'

# Stop reasons — the loop stops on the FIRST of these to fire.
STOP_WINDOW_COUNT = 'window_count'          # ran the configured max number of windows/calls attempted
STOP_BUDGET = 'budget'                       # accumulated per-window cost crossed the cap
STOP_CLEAN_TARGET = 'clean_target'           # plan queue AND requeue backlog both drained
STOP_CONSECUTIVE_EMPTY = 'consecutive_empty'  # N consecutive zero-progress iterations
STOP_CALL_COUNT = 'call_count'               # cumulative model calls crossed the max-calls ceiling
STOP_CLEAN_QUOTA = 'clean_quota'             # cumulative clean rows reached the requested quota
STOP_COST_UNEVALUABLE = 'cost_unevaluable'   # a cost ceiling is active but a window's cost could
#                                              NOT be evaluated -> FAIL CLOSED (never treat missing
#                                              cost as zero and keep spending). Distinct from
#                                              STOP_BUDGET: this is a data-integrity stop, not an
#                                              over-ceiling stop (H963 cost fail-closed contract).


def strict_cost_fn(window, wf_output, report):
    """A fail-closed per-window cost reader for use when a cost/quota ceiling is enforced.

    Returns the report's numeric ``cost`` when present, else ``None`` — signalling the
    supervisor that this window's spend is UNEVALUABLE. Paired with an active ``budget_cap``
    the supervisor then stops with ``STOP_COST_UNEVALUABLE`` instead of silently treating the
    missing figure as zero (the anti-pattern the default reader keeps for backward compat).
    ``bool``/``str`` costs are rejected as invalid (None), not coerced."""
    cost = (report or {}).get('cost')
    if isinstance(cost, bool) or not isinstance(cost, (int, float)):
        return None
    return cost


class BoundedSupervisor:
    """A bounded, crash-resumable drain loop.

    Parameters
    ----------
    plan : list[dict]
        The supplied window backlog. Each entry is a window spec (any dict); an ``id`` is
        derived from ``id`` / ``root`` / position and used for dedupe + resume. The list is
        never mutated.
    run_window : callable(window) -> wf_output_path
        Injected. Runs one window and returns the path (or any handle) to its wf_output.
        In production this wraps live generation; tests inject a fixture-returning fake.
    audit : callable(wf_output_path, window) -> report dict, optional
        Injected auditor. When omitted, ``default_audit`` (the H920 sense-count gate against
        ``input_dir``) is used.
    checkpoint_path : str
        Where the atomic JSON checkpoint is written each iteration. Required for resume.
    max_windows : int, optional
        Window-count cap. ``None`` disables the bound.
    budget_cap : number, optional
        Running-budget (cost/quota) cap; the loop stops once accumulated cost is >= this.
        ``None`` disables the bound. When a ``budget_cap`` is set AND ``cost_fn`` reports an
        UNEVALUABLE cost (``None``) for a window, the loop FAILS CLOSED with
        ``STOP_COST_UNEVALUABLE`` rather than treating the missing figure as zero — pair it
        with ``strict_cost_fn`` (module-level) to get that fail-closed reader.
    empty_streak_cap : int, optional
        Stop after this many consecutive zero-progress (non-productive) iterations. ``None``
        disables it.
    max_calls : int, optional
        Ceiling on cumulative model calls attempted (summed from ``report['calls']``). The
        loop stops with ``STOP_CALL_COUNT`` once the running total is >= this. ``None``
        disables the bound.
    max_clean : int, optional
        Clean-rows quota: stop with ``STOP_CLEAN_QUOTA`` once cumulative clean cards
        (summed from ``report['clean_count']``) reach this many. ``None`` disables it.
        Distinct from the clean-TARGET drain (queue+backlog empty) — this is an explicit
        ceiling on how many clean rows to REQUEST before stopping.
    cost_fn : callable(window, wf_output_path, report) -> number|None, optional
        Per-window cost. Defaults to ``report.get('cost', 0)`` (missing -> 0, the legacy
        silent-zero kept for backward compatibility). Pass ``strict_cost_fn`` to make a
        missing cost ``None`` and engage the fail-closed policy above.
    input_dir : str, optional
        Portrait-sidecar dir for the default H920 auditor. When omitted a throwaway temp
        dir is used (so the default auditor stays hermetic — an empty dir yields no
        shortfall, only null-card requeues).
    resume : bool
        When True and ``checkpoint_path`` exists, restore state from it on construction.
    """

    def __init__(self, plan, run_window, checkpoint_path,
                 audit=None, max_windows=None, budget_cap=None,
                 empty_streak_cap=None, cost_fn=None, input_dir=None, resume=False,
                 max_calls=None, max_clean=None):
        if not callable(run_window):
            raise TypeError('run_window must be callable(window) -> wf_output_path')
        self.plan = [self._normalize_plan(w, i) for i, w in enumerate(plan or [])]
        self.run_window = run_window
        self.audit = audit
        self.checkpoint_path = checkpoint_path
        self.max_windows = max_windows
        self.budget_cap = budget_cap
        self.empty_streak_cap = empty_streak_cap
        self.max_calls = max_calls
        self.max_clean = max_clean
        self.cost_fn = cost_fn or (lambda window, wf_output, report: report.get('cost', 0) or 0)
        self.input_dir = input_dir
        self._own_input_dir = None

        # Loop state (all persisted).
        self.windows_done = 0
        self.budget_spent = 0.0
        self.calls_spent = 0
        self.clean_total = 0
        self.requeue_backlog = []
        self.empty_streak = 0
        self.next_index = 0
        self.completed_window_ids = []
        self.history = []
        self.stop_reason = None
        self._rq_counter = 0

        if resume and checkpoint_path and os.path.exists(checkpoint_path):
            self._load_checkpoint()

    # ---- construction helpers -------------------------------------------------

    @classmethod
    def from_checkpoint(cls, checkpoint_path, plan, run_window, **kw):
        """Build a supervisor already restored from ``checkpoint_path``."""
        kw.pop('resume', None)
        inst = cls(plan, run_window, checkpoint_path, resume=False, **kw)
        inst._load_checkpoint()
        return inst

    @staticmethod
    def _normalize_plan(window, index):
        """Shallow-copy a plan window and stamp a stable ``id``."""
        item = dict(window) if isinstance(window, dict) else {'value': window}
        item.setdefault('id', item.get('root') or ('w%03d' % index))
        item['requeue'] = False
        return item

    def _make_requeue_item(self, origin, keys):
        self._rq_counter += 1
        return {
            'id': 'rq-%03d-%s' % (self._rq_counter, origin.get('id')),
            'requeue': True,
            'origin': origin.get('id'),
            'keys': sorted(set(keys)),
        }

    def _ensure_input_dir(self):
        if self.input_dir:
            return self.input_dir
        if not self._own_input_dir:
            self._own_input_dir = tempfile.mkdtemp(prefix='bounded_supervisor_input_')
        return self._own_input_dir

    # ---- the loop -------------------------------------------------------------

    def _pull(self):
        """Next window to run, or None when both the requeue backlog and the plan queue
        are drained. The requeue backlog is ALWAYS pulled before a fresh plan window, so a
        partial's rework runs before new work (H304 requeue-first ordering)."""
        while self.requeue_backlog:
            item = self.requeue_backlog.pop(0)
            if item.get('id') in self.completed_window_ids:
                continue
            return item
        while self.next_index < len(self.plan):
            item = self.plan[self.next_index]
            self.next_index += 1
            if item.get('id') in self.completed_window_ids:
                continue
            return item
        return None

    def _run_audit(self, wf_output, item):
        if self.audit is not None:
            return self.audit(wf_output, item) or {}
        return self.default_audit(wf_output, item) or {}

    def run(self):
        """Drive the loop until the first bound fires. Idempotent once stopped:
        re-calling on an already-stopped (resumed-past-completion) supervisor is a no-op
        that returns the same summary."""
        if self.stop_reason:
            return self.summary()
        try:
            while True:
                # (5a) window-count bound — checked before pulling/running new work, so a
                # cap of N runs EXACTLY N windows.
                if self.max_windows is not None and self.windows_done >= self.max_windows:
                    self._finish(STOP_WINDOW_COUNT)
                    break

                # (1) PULL — requeue backlog first, then the plan queue.
                item = self._pull()
                if item is None:
                    # (5c) clean-target — queue + backlog both drained.
                    self._finish(STOP_CLEAN_TARGET)
                    break
                if item.get('id') in self.completed_window_ids:
                    # Defensive: never re-run a completed window on resume.
                    continue

                # (2) RUN — injected; returns a wf_output handle/path.
                wf_output = self.run_window(item)

                # (3) AUDIT — injected report, or the H920 gate helper on a tmp dir.
                report = self._run_audit(wf_output, item)

                raw_cost = self.cost_fn(item, wf_output, report)
                # A None cost means UNEVALUABLE — never coerce it to 0 for accounting. It
                # only fails the run closed when a cost ceiling (budget_cap) is active
                # (checked below); with no cost ceiling it is a harmless 0 contribution.
                cost_unevaluable = raw_cost is None
                cost = 0 if cost_unevaluable else (raw_cost or 0)
                self.budget_spent += cost
                calls = int(report.get('calls') or 0)
                self.calls_spent += calls
                self.windows_done += 1
                self.completed_window_ids.append(item['id'])

                # (4) REQUEUE PARTIALS — a work-item for the reported keys, pulled next
                # round before any new window.
                requeue_keys = [k for k in (report.get('requeue_keys') or []) if k]
                satisfied = [k for k in (report.get('satisfied_keys') or []) if k]
                if requeue_keys:
                    self.requeue_backlog.append(self._make_requeue_item(item, requeue_keys))

                clean = int(report.get('clean_count') or 0)
                self.clean_total += clean
                # (g) A satisfied (already-promoted, zero-store-delta) requeue key is
                # progress, not a hard error: it drains the backlog and resets the streak.
                made_progress = clean > 0 or bool(satisfied)
                if made_progress:
                    self.empty_streak = 0
                else:
                    self.empty_streak += 1

                self.history.append({
                    'window_id': item['id'],
                    'requeue': bool(item.get('requeue')),
                    'clean_count': clean,
                    'clean_total': self.clean_total,
                    'calls': calls,
                    'calls_spent': self.calls_spent,
                    'requeued_keys': sorted(set(requeue_keys)),
                    'satisfied_keys': sorted(set(satisfied)),
                    'cost': None if cost_unevaluable else cost,
                    'cost_unevaluable': cost_unevaluable,
                    'budget_spent': self.budget_spent,
                    'empty_streak': self.empty_streak,
                })

                # (6) PERSIST loop state atomically for crash resume.
                self._write_checkpoint()

                # (5b0) COST FAIL-CLOSED — a cost ceiling is enforced but this window's spend
                # could not be evaluated. Stop closed BEFORE any further work: never keep
                # spending against a budget we can no longer enforce. Checked first so it
                # pre-empts a would-be clean-target success on an unenforceable budget.
                if cost_unevaluable and self.budget_cap is not None:
                    self._finish(STOP_COST_UNEVALUABLE)
                    break

                # (5b) running-budget (cost/quota) bound — after accumulating this window's
                # cost, so the window that crosses the cap runs, then the loop stops mid-queue.
                if self.budget_cap is not None and self.budget_spent >= self.budget_cap:
                    self._finish(STOP_BUDGET)
                    break

                # (5e) call-count bound — cumulative model calls attempted.
                if self.max_calls is not None and self.calls_spent >= self.max_calls:
                    self._finish(STOP_CALL_COUNT)
                    break

                # (5f) clean-rows quota — stop once the requested number of clean rows is met.
                if self.max_clean is not None and self.clean_total >= self.max_clean:
                    self._finish(STOP_CLEAN_QUOTA)
                    break

                # (5d) consecutive-empty (non-productive) bound.
                if (self.empty_streak_cap is not None
                        and self.empty_streak >= self.empty_streak_cap):
                    self._finish(STOP_CONSECUTIVE_EMPTY)
                    break
        finally:
            self._cleanup_own_input_dir()
        return self.summary()

    def _finish(self, reason):
        self.stop_reason = reason
        self._write_checkpoint()

    def _cleanup_own_input_dir(self):
        if self._own_input_dir and os.path.isdir(self._own_input_dir):
            try:
                import shutil
                shutil.rmtree(self._own_input_dir)
            except OSError:
                pass
            self._own_input_dir = None

    # ---- the default (H920) auditor ------------------------------------------

    def default_audit(self, wf_output, item):
        """Offline fallback auditor: read the wf_output JSON, requeue null cards
        (transient) and H920 SAN-LOSS sense-shortfall cards (defect), and count the rest
        as clean. Uses sense_count.scan_sense_shortfall against a supplied/temp input dir
        — never audit_window.main(), whose INPUT_DIR is bound to the live input tree.

        NOTE: canonical-store deltas (the ``satisfied_keys`` reconciliation) are a
        promotion-time signal this offline auditor cannot observe, so it never emits
        satisfied_keys; that path is exercised via an injected report / the live wiring.
        """
        try:
            with open(wf_output, encoding='utf-8') as f:
                payload = json.load(f)
        except (OSError, ValueError, TypeError):
            return {'requeue_keys': [], 'clean_count': 0, 'cost': 0, 'satisfied_keys': []}
        results = payload.get('results') or []
        null_keys = [r.get('key') for r in results
                     if isinstance(r, dict) and r.get('key') and r.get('card') is None]
        defect_keys = []
        try:
            from sense_count import scan_sense_shortfall
            short = scan_sense_shortfall(results, self._ensure_input_dir())
            defect_keys = [s['key'] for s in short if s.get('key')]
        except Exception:
            defect_keys = []
        requeue = sorted(set(null_keys) | set(defect_keys))
        clean = sum(1 for r in results
                    if isinstance(r, dict) and r.get('key')
                    and r.get('card') is not None and r.get('key') not in set(defect_keys))
        cost = (payload.get('summary') or {}).get('cost') or 0
        return {'requeue_keys': requeue, 'clean_count': clean, 'cost': cost,
                'satisfied_keys': []}

    # ---- checkpoint persistence ----------------------------------------------

    def _state_dict(self):
        return {
            'schema': SCHEMA,
            'windows_done': self.windows_done,
            'budget_spent': self.budget_spent,
            'calls_spent': self.calls_spent,
            'clean_total': self.clean_total,
            'requeue_backlog': self.requeue_backlog,
            'empty_streak': self.empty_streak,
            'next_index': self.next_index,
            'completed_window_ids': self.completed_window_ids,
            'stop_reason': self.stop_reason,
            'rq_counter': self._rq_counter,
            'bounds': {
                'max_windows': self.max_windows,
                'budget_cap': self.budget_cap,
                'empty_streak_cap': self.empty_streak_cap,
                'max_calls': self.max_calls,
                'max_clean': self.max_clean,
            },
            'history': self.history,
        }

    def _write_checkpoint(self):
        if not self.checkpoint_path:
            return
        d = os.path.dirname(os.path.abspath(self.checkpoint_path))
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        tmp = self.checkpoint_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(self._state_dict(), f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(tmp, self.checkpoint_path)

    def _load_checkpoint(self):
        with open(self.checkpoint_path, encoding='utf-8') as f:
            state = json.load(f)
        if state.get('schema') != SCHEMA:
            raise ValueError('checkpoint schema mismatch: %r' % state.get('schema'))
        self.windows_done = int(state.get('windows_done') or 0)
        self.budget_spent = float(state.get('budget_spent') or 0)
        self.calls_spent = int(state.get('calls_spent') or 0)
        self.clean_total = int(state.get('clean_total') or 0)
        self.requeue_backlog = list(state.get('requeue_backlog') or [])
        self.empty_streak = int(state.get('empty_streak') or 0)
        self.next_index = int(state.get('next_index') or 0)
        self.completed_window_ids = list(state.get('completed_window_ids') or [])
        self.stop_reason = state.get('stop_reason')
        self._rq_counter = int(state.get('rq_counter') or 0)
        self.history = list(state.get('history') or [])
        return state

    # ---- reporting ------------------------------------------------------------

    def summary(self):
        return {
            'schema': SCHEMA,
            'stop_reason': self.stop_reason,
            'windows_done': self.windows_done,
            'budget_spent': self.budget_spent,
            'calls_spent': self.calls_spent,
            'clean_total': self.clean_total,
            'requeue_backlog_len': len(self.requeue_backlog),
            'requeue_backlog_keys': sorted(
                {k for item in self.requeue_backlog for k in (item.get('keys') or [])}),
            'empty_streak': self.empty_streak,
            'next_index': self.next_index,
            'completed_window_ids': list(self.completed_window_ids),
        }


if __name__ == '__main__':
    # Live delegation (wrapping cmd_staged_run against validated accounts) is a LIVE-GATED
    # follow-up and is intentionally NOT wired here. Run the hermetic self-test instead.
    print('bounded_supervisor: offline control-loop module (H960 gap #6).')
    print('Live delegation is deferred (SPLIT verdict). Run the self-test:')
    print('  python src/pilot/bounded_supervisor_selftest.py')
