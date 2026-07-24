#!/usr/bin/env python
r"""cohort_engine.py — offline multi-profile cohort wave engine (H1437 Phase 2).

Dispatches a plan of profile-bound leases concurrently up to ``width``, with at most
one in-flight job per profile, a pre-spawn atomic ``max_calls`` reservation ledger,
durable per-lease checkpoints, one batched promote_wave after every member is
audited, and one rebuild_tm per accepted wave.

Pure control plane: ``run_window``, ``audit``, ``promote_wave``, ``rebuild_tm`` and
``probe`` are injected. No live generation, store mutation, or coordinator I/O.
"""
from __future__ import annotations

import json
import os
import sys
import threading
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SCHEMA = 'pwg.cohort_engine.v1'
PHASE_PENDING = 'pending'
PHASE_RUNNING = 'running'
PHASE_DONE = 'done'
PHASE_FAILED = 'failed'


class CohortEngine:
    """Bounded multi-profile cohort wave scheduler (offline / fake-worker ready)."""

    def __init__(self, plan, run_window, checkpoint_path,
                 audit=None, promote_wave=None, rebuild_tm=None,
                 width=1, admitted=None, parked=None, max_calls=None,
                 probe=None, coord_dir=None, resume=False):
        if not callable(run_window):
            raise TypeError('run_window must be callable(window) -> wf_output_path')
        self.plan = [dict(w) if isinstance(w, dict) else {'id': 'w%03d' % i, 'value': w}
                     for i, w in enumerate(plan or [])]
        for i, w in enumerate(self.plan):
            w.setdefault('id', w.get('root') or ('w%03d' % i))
        self.run_window = run_window
        self.checkpoint_path = checkpoint_path
        self.audit = audit
        self.promote_wave = promote_wave
        self.rebuild_tm = rebuild_tm
        self.width = max(1, int(width or 1))
        self.admitted = set(admitted or ())
        self.parked = set(parked or ())
        self.max_calls = max_calls
        self.probe = probe
        self.coord_dir = os.path.abspath(coord_dir) if coord_dir else None
        self.resume = bool(resume)

        # Durable / runtime state
        self.leases = {}            # id -> {phase, wf_output, report, ...}
        self.wave = {'promoted': False, 'tm_done': False, 'receipt': None}
        self.calls_spent = 0        # worker launches that completed (ok or crash)
        self.calls_reserved = 0     # probes + worker reservations (ledger)
        self.peak_concurrency = 0
        self.requeue_backlog_keys = []
        self.accepted_order = []
        self.stop_reason = None
        self.effective_width = 1

        self._ledger_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._active = 0
        self._probed = set()
        self._failed_profiles = set()

        if self.resume and self.checkpoint_path and os.path.exists(self.checkpoint_path):
            self._load_checkpoint()

    # ---- checkpoint -----------------------------------------------------------

    def _checkpoint_payload(self):
        return {
            'schema': SCHEMA,
            'leases': self.leases,
            'wave': self.wave,
            'calls_spent': self.calls_spent,
            'calls_reserved': self.calls_reserved,
            'peak_concurrency': self.peak_concurrency,
            'requeue_backlog_keys': list(self.requeue_backlog_keys),
            'accepted_order': list(self.accepted_order),
            'stop_reason': self.stop_reason,
            'effective_width': self.effective_width,
            'probed': sorted(self._probed),
            'failed_profiles': sorted(self._failed_profiles),
            'coord_dir': self.coord_dir,
        }

    def _save_checkpoint(self):
        if not self.checkpoint_path:
            return
        payload = self._checkpoint_payload()
        parent = os.path.dirname(os.path.abspath(self.checkpoint_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        tmp = self.checkpoint_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(tmp, self.checkpoint_path)

    def _load_checkpoint(self):
        with open(self.checkpoint_path, encoding='utf-8') as f:
            data = json.load(f)
        self.leases = dict(data.get('leases') or {})
        wave = dict(data.get('wave') or {})
        wave.setdefault('promoted', False)
        wave.setdefault('tm_done', False)
        wave.setdefault('receipt', None)
        self.wave = wave
        self.calls_spent = int(data.get('calls_spent') or 0)
        self.calls_reserved = int(data.get('calls_reserved') or 0)
        self.peak_concurrency = int(data.get('peak_concurrency') or 0)
        self.requeue_backlog_keys = list(data.get('requeue_backlog_keys') or [])
        self.accepted_order = list(data.get('accepted_order') or [])
        self.stop_reason = data.get('stop_reason')
        self.effective_width = int(data.get('effective_width') or 1)
        self._probed = set(data.get('probed') or [])
        self._failed_profiles = set(data.get('failed_profiles') or [])
        # Clear non-terminal running phases so resume re-dispatches them.
        for wid, lease in list(self.leases.items()):
            if lease.get('phase') == PHASE_RUNNING:
                lease['phase'] = PHASE_PENDING

    # ---- reservation ledger ---------------------------------------------------

    def _reserve(self):
        """Atomically consume one unit from max_calls. Returns False if exhausted."""
        with self._ledger_lock:
            if self.max_calls is not None and self.calls_reserved >= self.max_calls:
                return False
            self.calls_reserved += 1
            return True

    # ---- fleet filtering ------------------------------------------------------

    def _fleet(self):
        if self.admitted:
            return set(self.admitted)
        return {w.get('profile') for w in self.plan if w.get('profile') is not None}

    def _runnable_profiles(self):
        return self._fleet() - set(self.parked)

    def _is_window_runnable(self, window):
        profile = window.get('profile')
        fleet = self._fleet()
        if profile not in fleet:
            return False
        if profile in self.parked:
            return False
        if profile in self._failed_profiles:
            return False
        return True

    def _lease_done(self, wid):
        lease = self.leases.get(wid) or {}
        return lease.get('phase') == PHASE_DONE

    # ---- worker body ----------------------------------------------------------

    def _run_one(self, window):
        """Execute one lease: run_window + audit + durable receipt. Raises on crash."""
        wid = window['id']
        with self._state_lock:
            self.leases[wid] = {
                'phase': PHASE_RUNNING,
                'wf_output': None,
                'report': None,
            }
            self._active += 1
            if self._active > self.peak_concurrency:
                self.peak_concurrency = self._active
            self._save_checkpoint()

        try:
            if self.coord_dir:
                window = dict(window)
                window['coord_dir'] = self.coord_dir
            path = self.run_window(window)
            report = {}
            if self.audit is not None:
                report = self.audit(path, window) or {}
            with self._state_lock:
                self.leases[wid] = {
                    'phase': PHASE_DONE,
                    'wf_output': path,
                    'report': report,
                }
                self.calls_spent += 1
                self._save_checkpoint()
            return path, report
        except Exception:
            with self._state_lock:
                # Failed lease is NOT done — resume will re-run it. Reservation was
                # already consumed at spawn time; count the attempt as spent.
                prev = self.leases.get(wid) or {}
                if prev.get('phase') != PHASE_DONE:
                    self.leases[wid] = {
                        'phase': PHASE_FAILED,
                        'wf_output': None,
                        'report': None,
                        'error': 'worker_crash',
                    }
                    self.calls_spent += 1
                    self._save_checkpoint()
            raise
        finally:
            with self._state_lock:
                self._active = max(0, self._active - 1)

    # ---- dispatch -------------------------------------------------------------

    def _dispatch(self):
        """Run unfinished runnable leases with concurrent different-profile width."""
        pending = []
        for w in self.plan:
            if not self._is_window_runnable(w):
                continue
            if self._lease_done(w['id']):
                continue
            pending.append(dict(w))

        if not pending:
            return []

        errors = []
        budget_exhausted = False
        profile_busy = set()
        in_flight = {}  # future -> window
        max_workers = max(1, self.effective_width)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            while pending or in_flight:
                # Fill free slots in plan order, respecting per-profile exclusion.
                while pending and len(in_flight) < self.effective_width and not budget_exhausted:
                    launched = False
                    for i, w in enumerate(list(pending)):
                        profile = w.get('profile')
                        if profile in profile_busy:
                            continue
                        if profile in self._failed_profiles:
                            pending = [x for x in pending if x.get('profile') != profile]
                            launched = True  # retry outer while with shorter pending
                            break
                        # Probe once per profile (consumes the same ledger).
                        if self.probe is not None and profile not in self._probed:
                            if not self._reserve():
                                budget_exhausted = True
                                break
                            try:
                                self.probe(profile)
                                self._probed.add(profile)
                            except Exception:
                                # Failed probe still consumed the reservation; park
                                # the profile for this wave and continue other work.
                                self._probed.add(profile)
                                self._failed_profiles.add(profile)
                                pending = [x for x in pending
                                           if x.get('profile') != profile]
                                launched = True
                                break
                        if profile in self._failed_profiles:
                            continue
                        # Atomic pre-spawn reservation for the worker itself.
                        if not self._reserve():
                            budget_exhausted = True
                            break
                        pending.pop(pending.index(w))
                        profile_busy.add(profile)
                        child = dict(w)
                        if self.coord_dir:
                            child['coord_dir'] = self.coord_dir
                        fut = pool.submit(self._run_one, child)
                        in_flight[fut] = child
                        launched = True
                        break
                    if not launched or budget_exhausted:
                        break

                if not in_flight:
                    break

                done, _ = wait(list(in_flight.keys()), return_when=FIRST_COMPLETED)
                for fut in done:
                    window = in_flight.pop(fut)
                    profile_busy.discard(window.get('profile'))
                    try:
                        fut.result()
                    except Exception as exc:
                        errors.append(exc)
                        # No retry: reservation already consumed. Leave lease failed.

                # After a worker crash, drain siblings already in flight but do not
                # admit further pending work (wave aborts for resume).
                if errors:
                    while in_flight:
                        done, _ = wait(list(in_flight.keys()), return_when=FIRST_COMPLETED)
                        for fut in done:
                            window = in_flight.pop(fut)
                            profile_busy.discard(window.get('profile'))
                            try:
                                fut.result()
                            except Exception as exc:
                                errors.append(exc)
                    break

        self._save_checkpoint()
        return errors

    # ---- promote / TM barrier -------------------------------------------------

    def _collect_clean_and_requeue(self):
        clean_members = []
        requeue_keys = []
        for w in self.plan:
            wid = w['id']
            lease = self.leases.get(wid) or {}
            if lease.get('phase') != PHASE_DONE:
                continue
            report = lease.get('report') or {}
            rq = [k for k in (report.get('requeue_keys') or []) if k]
            if rq:
                requeue_keys.extend(rq)
                continue
            clean_members.append(dict(w))
        return clean_members, requeue_keys

    def _promote_and_tm(self):
        clean_members, requeue_keys = self._collect_clean_and_requeue()
        self.requeue_backlog_keys = list(requeue_keys)

        if not self.wave.get('promoted'):
            if clean_members:
                if self.promote_wave is not None:
                    # Crash here leaves promoted=False so resume re-attempts once.
                    receipt = self.promote_wave(clean_members)
                else:
                    receipt = {'members': [m['id'] for m in clean_members]}
                self.wave['receipt'] = receipt
                self.wave['promoted'] = True
                self.accepted_order = [m['id'] for m in clean_members]
                self._save_checkpoint()
            else:
                # Nothing clean to promote — still mark the wave settled.
                self.wave['promoted'] = True
                self.accepted_order = []
                self._save_checkpoint()

        if self.wave.get('promoted') and not self.wave.get('tm_done'):
            receipt = self.wave.get('receipt')
            if self.rebuild_tm is not None and receipt is not None:
                # Crash here leaves promoted=True / tm_done=False — resume skips promote.
                self.rebuild_tm(receipt)
            self.wave['tm_done'] = True
            self._save_checkpoint()

    # ---- summary --------------------------------------------------------------

    def summary(self):
        return {
            'peak_concurrency': self.peak_concurrency,
            'accepted_order': list(self.accepted_order),
            'requeue_backlog_keys': list(self.requeue_backlog_keys),
            'calls_spent': self.calls_spent,
            'calls_reserved': self.calls_reserved,
            'effective_width': self.effective_width,
            'coord_dir': self.coord_dir,
            'stop_reason': self.stop_reason,
            'wave': dict(self.wave),
            'leases': {k: dict(v) for k, v in self.leases.items()},
        }

    # ---- main entry -----------------------------------------------------------

    def run(self):
        # Propagate coordinator dir to child env for the duration of the wave.
        old_env = os.environ.get('PWG_COORDINATOR_DIR')
        if self.coord_dir:
            os.environ['PWG_COORDINATOR_DIR'] = self.coord_dir

        try:
            runnable = self._runnable_profiles()
            fleet = self._fleet()

            # All admitted profiles parked (even if excluded healthy profiles exist).
            if fleet and not runnable:
                self.effective_width = 0
                self.stop_reason = (
                    'all admitted profiles parked — no runnable fleet '
                    '(admitted=%s parked=%s)' % (sorted(fleet), sorted(self.parked))
                )
                self._save_checkpoint()
                return self.summary()

            self.effective_width = min(self.width, max(1, len(runnable)))

            # Already fully settled on resume?
            if self.wave.get('promoted') and self.wave.get('tm_done'):
                return self.summary()

            # max_calls=0: reserve nothing, launch nothing.
            if self.max_calls is not None and self.max_calls <= 0:
                self.stop_reason = self.stop_reason or 'max_calls=0'
                self._save_checkpoint()
                return self.summary()

            # If wave already fully audited (all runnable leases done) skip dispatch.
            need_dispatch = False
            for w in self.plan:
                if not self._is_window_runnable(w):
                    continue
                if not self._lease_done(w['id']):
                    need_dispatch = True
                    break

            errors = []
            if need_dispatch and not self.wave.get('promoted'):
                errors = self._dispatch()

            if errors:
                # Durable receipts for completed siblings already on disk; re-raise.
                self._save_checkpoint()
                raise errors[0]

            # Promote when every admitted/unparked plan member is audited, OR the
            # campaign ledger is exhausted (partial wave of what finished), OR the
            # wave was already promoted (TM-only resume).
            terminal_ok = True
            for w in self.plan:
                profile = w.get('profile')
                if self.admitted and profile not in self.admitted:
                    continue
                if profile in self.parked:
                    continue
                lease = self.leases.get(w['id']) or {}
                if lease.get('phase') != PHASE_DONE:
                    # Budget-exhausted partial wave: allow promote of what finished.
                    if self.max_calls is not None and self.calls_reserved >= self.max_calls:
                        continue
                    # Profile probe failed: no work will ever run here this life.
                    if profile in self._failed_profiles:
                        continue
                    terminal_ok = False
                    break

            if terminal_ok or self.wave.get('promoted'):
                self._promote_and_tm()

            return self.summary()
        finally:
            if self.coord_dir is not None:
                if old_env is None:
                    os.environ.pop('PWG_COORDINATOR_DIR', None)
                else:
                    os.environ['PWG_COORDINATOR_DIR'] = old_env
