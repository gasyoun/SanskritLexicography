#!/usr/bin/env python
r"""cohort_engine_selftest.py — the H1437 Phase 0 RED suite for the offline cohort engine.

STATUS: EXPECTED RED. Written BEFORE any production code (H1437 Phase 0, TDD): every RED
line below names an intended MISSING behavior of the bounded multi-profile cohort engine
(audit finding P1#8 "bounded staging is serial" + the audit's Verification specification
items 4 and 6 + H1437 load-bearing constraints 1-7), never a fixture defect. The suite
must flip GREEN across H1437 Phases 1-3 with NO edits outside the `build_engine` adapter
below (the one sanctioned seam if the Phase 2 constructor differs — any adapter change is
Codex-reviewable in isolation).

This file is deliberately NOT in the CI gate list (.github/workflows/ci.yml) yet; adding
it there is Phase 4 closeout work, after it is green.

THE PINNED CONTRACT (offline, fake workers only — zero live generation, zero store/TM/
coordinator mutation; promotion and TM rebuild are INJECTED fakes):

  (1) A cohort holding two DIFFERENT-profile leases AND a same-profile pair (c1 x2)
      under width 2: the cross-profile pair meets on a barrier (peak_concurrency >= 2)
      while the same-profile pair NEVER overlaps (at most one job per account,
      constraint 2 — the same-profile pair makes the exclusion assertion falsifiable).
  (2) Reverse completion order — OBSERVED via the fake-side completion trace (B really
      finishes before A), never assumed — yields the EXPECTED non-empty store bytes and
      the EXPECTED non-None accepted order of serial width=1 execution (constraint 4
      determinism; a no-op engine comparing b''==b'' / None==None cannot pass).
  (3) One worker crash mid-wave (leaseB launched AND died, asserted) resumes ONLY that
      lease from durable ON-DISK per-lease receipts — the checkpoint file must exist and
      record the completed sibling BEFORE resume, engine module memory is purged between
      lifetimes, and the completed sibling's model work is NEVER relaunched (constraint 5).
  (4) An audit rejection requeues ONLY its own keys; the TWO clean siblings batch into
      the wave's EXACTLY-ONE promotion commit — a rejected member never blocks them and
      extra commits are a failure (constraint 3).
  (5) A crash before AND a crash after the promotion barrier each RAISE out of the first
      life (a normal return is a failure), leave the pinned pre-resume state (no commit
      before the promoter crash; one commit + zero successful TM rebuilds after the TM
      crash), and produce EXACTLY one effective promotion and one TM rebuild per accepted
      wave after resume (constraints 4/5; audit P0#3's engine-facing half).
  (6) max_calls=0/1/3 is a RESERVATION consumed by probes, FAILED probes, CRASHED
      workers, retries AND successes alike, taken ATOMICALLY before every spawn (two
      leases racing width=2 for max_calls=1 admit exactly one) — the bound is never
      discovered exceeded after the fact, and nothing retries against an exhausted
      ledger (constraint 6; audit P0#4, Verification spec item 4).
  (7) A custom coordinator directory is OBSERVABLE from inside every child at call time
      (not merely echoed in the summary), and with EVERY admitted profile parked the
      engine dispatches nothing and stops naming the parked condition even when a
      healthy EXCLUDED profile exists in the plan (H1386 D4 exactness; audit P1#10).

Corrected 22-07-2026 per the Codex (GPT-5) Phase 0 review — 8 findings (5 P1 / 3 P2), all
addressed test-side; the suite remains EXPECTED RED until Phases 1-3 land the engine.

Tests (6) and (7) additionally run the CURRENT production code paths (BoundedSupervisor
ceilings, bounded_staged_run.make_run_window's pre-dispatch parked guard) to print
measured evidence of today's behavior; those existing suites' own green pins are NOT
contradicted — the assertions here bind only the new reservation/admitted-fleet contract.

  python src/pilot/cohort_engine_selftest.py

Exit code: non-zero while any pin is RED (so the suite cannot be mistaken for a green
gate); 0 only when the whole contract holds.

Authored for H1437 Phase 0 by Fable 5 (claude-fable-5); Codex (GPT-5) is the phase
reviewer.
"""
import json
import os
import sys
import tempfile
import threading

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bounded_staged_run as bsr                     # noqa: E402
import bounded_supervisor as bs                      # noqa: E402
import max_account_orchestrator as mao               # noqa: E402


class MissingBehavior(AssertionError):
    """A RED that names intended missing engine behavior (never a fixture defect)."""


class SimulatedCrash(RuntimeError):
    """Injected fault for the crash/resume and promotion-barrier pins."""


ENGINE_MISSING = (
    'no cohort engine exists (src/pilot/cohort_engine.py is not importable) — the bounded '
    'driver still represents one supervisor item as one lease and blocks through dispatch, '
    'audit and promotion (audit P1#8), so this pin cannot hold yet: %s')


def load_cohort_engine():
    try:
        import cohort_engine                          # noqa: F401
    except ModuleNotFoundError as exc:
        # Codex review #8: ONLY the engine module itself being absent is the sanctioned
        # Phase 0 RED. A transitive import failure inside an existing cohort_engine.py is
        # a real defect and must surface loudly — misreporting it as "no engine exists"
        # would hide broken Phase 1-3 code behind the expected-RED banner.
        if exc.name == 'cohort_engine':
            return None
        raise
    return sys.modules['cohort_engine']


def _forget_engine_module():
    """Codex review #6: kill module/class-level memory between engine LIFETIMES so a
    resume can only be fed by the durable on-disk receipts (build_engine re-imports the
    module fresh). In-process resume fixtures would otherwise accept an engine whose
    'durability' is a dict keyed by checkpoint path."""
    sys.modules.pop('cohort_engine', None)


def build_engine(windows, run_window, checkpoint, audit=None, promote_wave=None,
                 rebuild_tm=None, width=1, admitted=(), parked=(), max_calls=None,
                 probe=None, coord_dir=None, resume=False, contract=''):
    """THE ADAPTER — the single sanctioned seam between this suite and the Phase 2 engine.

    Pinned constructor shape (mirrors BoundedSupervisor vocabulary; adjust HERE, and only
    here, if Phase 2 lands a different signature — with Codex review):

      cohort_engine.CohortEngine(
          plan, run_window, checkpoint_path,
          audit=...,            # callable(wf_output, window) -> report (same contract as
                                #   BoundedSupervisor's injected auditor)
          promote_wave=...,     # callable(clean_members) -> receipt; ONE call per accepted
                                #   wave (replaces the per-lease in-loop promote)
          rebuild_tm=...,       # callable(receipt); ONE call per accepted wave
          width=N,              # cohort width; width=1 must preserve serial semantics
          admitted=set(...),    # probed-healthy dispatch allow-list (profile slots)
          parked=set(...),      # currently-parked profile slots
          max_calls=N,          # campaign reservation ledger ceiling (probes+calls)
          probe=...,            # callable(profile) -> latency; consumes the SAME ledger
          coord_dir=...,        # custom coordinator dir; must reach every child env
          resume=bool,          # restore from durable per-lease phase receipts
      ).run() -> summary dict with at least 'peak_concurrency'.
    """
    eng = load_cohort_engine()
    if eng is None:
        raise MissingBehavior(ENGINE_MISSING % contract)
    return eng.CohortEngine(
        windows, run_window, checkpoint, audit=audit, promote_wave=promote_wave,
        rebuild_tm=rebuild_tm, width=width, admitted=set(admitted), parked=set(parked),
        max_calls=max_calls, probe=probe, coord_dir=coord_dir, resume=resume)


# ---------------------------------------------------------------------------
# Fakes — every observable the pins assert on lives on the FAKE side, so the
# engine is judged by its effects, not its internals.
# ---------------------------------------------------------------------------

class ConcurrencyProbe:
    """Thread-safe launch log + global and per-profile peak-concurrency meter."""

    def __init__(self):
        self.lock = threading.Lock()
        self.active = 0
        self.peak = 0
        self.active_by_profile = {}
        self.peak_by_profile = {}
        self.launches = []

    def enter(self, window):
        with self.lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
            profile = window.get('profile')
            n = self.active_by_profile.get(profile, 0) + 1
            self.active_by_profile[profile] = n
            self.peak_by_profile[profile] = max(self.peak_by_profile.get(profile, 0), n)
            self.launches.append(window['id'])

    def exit(self, window):
        with self.lock:
            self.active -= 1
            profile = window.get('profile')
            self.active_by_profile[profile] = self.active_by_profile.get(profile, 1) - 1


class FakeWorker:
    """run_window fake: meters concurrency, optionally rendezvouses on a barrier, waits on
    events, crashes on cue — then writes a trivial wf_output fixture and returns its path."""

    def __init__(self, td, probe, barrier=None, barrier_wait_s=0.7,
                 wait_for=None, signal_done=None, crash_ids=()):
        self.td = td
        self.probe = probe
        self.barrier = barrier
        self.barrier_wait_s = barrier_wait_s
        self.wait_for = wait_for or {}          # window id -> threading.Event to wait on
        self.signal_done = signal_done or {}    # window id -> threading.Event to set
        self.crash_ids = set(crash_ids)
        self.met_barrier = []
        self.completion_log = []                # Codex review #1: OBSERVED completion
        self._log_lock = threading.Lock()       # order of successful workers, fake-side

    def __call__(self, window):
        wid = window['id']
        self.probe.enter(window)
        try:
            if self.barrier is not None:
                try:
                    self.barrier.wait(self.barrier_wait_s)
                    self.met_barrier.append(wid)
                except threading.BrokenBarrierError:
                    pass          # serial execution: the rendezvous never happens
            event = self.wait_for.get(wid)
            if event is not None:
                event.wait(2.0)
            if wid in self.crash_ids:
                raise SimulatedCrash('simulated worker crash on %s' % wid)
            path = os.path.join(self.td, 'wf_%s.json' % wid)
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump({'meta': {'window': wid}, 'results': []}, f)
            with self._log_lock:
                self.completion_log.append(wid)
            return path
        finally:
            done = self.signal_done.get(wid)
            if done is not None:
                done.set()
            self.probe.exit(window)


class FakePromoter:
    """promote_wave fake: appends each accepted member id to a store file IN THE ORDER THE
    ENGINE PRESENTS THEM (so store bytes expose ordering), counts commits, can crash."""

    def __init__(self, store_path, fail_times=0):
        self.store_path = store_path
        self.fail_times = fail_times
        self.attempts = 0
        self.commits = []                        # list of member-id tuples, one per commit

    def __call__(self, members):
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise SimulatedCrash('simulated crash BEFORE the promotion commit')
        ids = tuple(m['id'] if isinstance(m, dict) else m for m in members)
        with open(self.store_path, 'a', encoding='utf-8', newline='\n') as f:
            for member_id in ids:
                f.write('%s\n' % member_id)
        self.commits.append(ids)
        return {'receipt': len(self.commits), 'members': list(ids)}


class FakeTM:
    """rebuild_tm fake: counts successful rebuilds, can crash on the first N calls."""

    def __init__(self, fail_times=0):
        self.fail_times = fail_times
        self.attempts = 0
        self.successes = 0

    def __call__(self, receipt):
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise SimulatedCrash('simulated crash AFTER promotion, before the TM rebuild')
        self.successes += 1


def clean_audit(wf_output, window):
    return {'requeue_keys': [], 'clean_count': 1, 'cost': 0, 'calls': 1,
            'satisfied_keys': []}


def _store_bytes(path):
    if not os.path.exists(path):
        return b''
    with open(path, 'rb') as f:
        return f.read()


# ---------------------------------------------------------------------------
# The seven pins.
# ---------------------------------------------------------------------------

def test_1_barrier_concurrency(td):
    """Two profile-bound leases meet on a barrier: peak_concurrency >= 2; same-profile
    leases never overlap."""
    td = os.path.join(td, 't1'); os.makedirs(td)
    windows = [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}]

    # EVIDENCE — the current driver is serial: the identical barrier fixture through
    # BoundedSupervisor (the loop bounded_staged_run drives) records peak_concurrency == 1.
    probe = ConcurrencyProbe()
    worker = FakeWorker(td, probe, barrier=threading.Barrier(2), barrier_wait_s=0.7)
    bs.BoundedSupervisor(list(windows), worker, os.path.join(td, 'serial_cp.json'),
                         audit=clean_audit).run()
    print('    (1) EVIDENCE serial baseline: BoundedSupervisor drained %s with '
          'peak_concurrency=%d (barrier rendezvous met by %d of 2 workers)'
          % ('+'.join(probe.launches), probe.peak, len(worker.met_barrier)))
    assert probe.peak == 1, 'fixture defect: serial baseline must measure peak 1'

    # THE PIN — the cohort engine dispatches profile-bound leases concurrently. Codex
    # review #4: the cohort MUST contain two leases on the SAME profile (leaseA + leaseC
    # on c1) — with only cross-profile leases the per-profile exclusion assertion is
    # tautological and cannot detect an engine that overlaps two same-account leases.
    cohort = [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'},
              {'id': 'leaseC', 'profile': 'c1'}]
    probe2 = ConcurrencyProbe()
    worker2 = FakeWorker(td, probe2, barrier=threading.Barrier(2), barrier_wait_s=2.0)
    engine = build_engine(
        cohort, worker2, os.path.join(td, 'cohort_cp.json'), audit=clean_audit,
        promote_wave=FakePromoter(os.path.join(td, 'store.txt')), rebuild_tm=FakeTM(),
        width=2, admitted={'c1', 'c2'},
        contract='two DIFFERENT-profile leases must block on a barrier together and prove '
                 'peak_concurrency >= 2, while the two SAME-profile leases (c1 x2) under '
                 'width 2 must never overlap')
    summary = engine.run()
    assert probe2.peak >= 2, (
        'measured peak_concurrency=%d — the cohort was not dispatched concurrently'
        % probe2.peak)
    assert summary.get('peak_concurrency', 0) >= 2, summary
    assert probe2.peak_by_profile.get('c1', 0) <= 1, (
        'the two c1-bound leases overlapped (constraint 2: at most one job per '
        'account): %r' % probe2.peak_by_profile)
    assert max(probe2.peak_by_profile.values()) <= 1, (
        'a single profile ran two jobs at once (constraint 2: at most one job per '
        'account): %r' % probe2.peak_by_profile)
    assert sorted(probe2.launches) == ['leaseA', 'leaseB', 'leaseC'], (
        'every cohort member must launch exactly once: %r' % probe2.launches)


def test_2_reverse_completion_determinism(td):
    """Reverse completion order yields the serial accepted order and store bytes."""
    td = os.path.join(td, 't2'); os.makedirs(td)
    windows = [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}]

    # Serial reference: width=1, natural order.
    serial_store = os.path.join(td, 'store_serial.txt')
    engine = build_engine(
        windows, FakeWorker(td, ConcurrencyProbe()), os.path.join(td, 'serial_cp.json'),
        audit=clean_audit, promote_wave=FakePromoter(serial_store), rebuild_tm=FakeTM(),
        width=1, admitted={'c1', 'c2'},
        contract='reverse completion order must yield the same accepted order and final '
                 'store bytes as serial width=1 execution')
    serial_summary = engine.run()

    # Codex review #1: the serial reference must produce the EXPECTED store bytes and a
    # NON-None accepted order — comparing two empty stores (b'' == b'') or None == None
    # would let a no-op engine that runs, audits and promotes nothing pass this pin.
    EXPECTED_STORE = b'leaseA\nleaseB\n'
    EXPECTED_ORDER = ['leaseA', 'leaseB']
    assert _store_bytes(serial_store) == EXPECTED_STORE, (
        'serial reference must actually promote both members in plan order: %r'
        % _store_bytes(serial_store))
    assert serial_summary.get('accepted_order') == EXPECTED_ORDER, serial_summary

    # Width=2 with completion REVERSED: leaseA's worker holds until leaseB has finished.
    b_done = threading.Event()
    reversed_store = os.path.join(td, 'store_reversed.txt')
    probe = ConcurrencyProbe()
    worker = FakeWorker(td, probe, wait_for={'leaseA': b_done},
                        signal_done={'leaseB': b_done})
    engine2 = build_engine(
        windows, worker, os.path.join(td, 'reversed_cp.json'), audit=clean_audit,
        promote_wave=FakePromoter(reversed_store), rebuild_tm=FakeTM(),
        width=2, admitted={'c1', 'c2'},
        contract='reverse completion order must yield the same accepted order and final '
                 'store bytes as serial width=1 execution')
    reversed_summary = engine2.run()

    # Codex review #1: the reversal must be OBSERVED, not assumed — the 2 s event wait
    # tolerates a serial engine that times out and completes A first; the fake-side
    # completion trace is the proof that B genuinely finished before A.
    assert worker.completion_log == ['leaseB', 'leaseA'], (
        'the reversed-completion fixture did not actually reverse: observed completion '
        'order %r (leaseB must complete before leaseA)' % worker.completion_log)
    assert _store_bytes(reversed_store) == EXPECTED_STORE, (
        'store bytes diverge from the serial reference under reversed completion: %r vs %r'
        % (_store_bytes(reversed_store), EXPECTED_STORE))
    assert reversed_summary.get('accepted_order') == EXPECTED_ORDER, (
        serial_summary, reversed_summary)


def test_3_crash_resumes_only_its_lease(td):
    """One worker crash resumes only that lease; the completed sibling is never
    relaunched."""
    td = os.path.join(td, 't3'); os.makedirs(td)
    windows = [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}]
    checkpoint = os.path.join(td, 'cp.json')
    store = os.path.join(td, 'store.txt')

    # Life 1: leaseB crashes AFTER leaseA completed (ordered via the a_done event).
    a_done = threading.Event()
    probe1 = ConcurrencyProbe()
    worker1 = FakeWorker(td, probe1, wait_for={'leaseB': a_done},
                         signal_done={'leaseA': a_done}, crash_ids={'leaseB'})
    promoter = FakePromoter(store)
    tm = FakeTM()
    engine = build_engine(
        windows, worker1, checkpoint, audit=clean_audit, promote_wave=promoter,
        rebuild_tm=tm, width=2, admitted={'c1', 'c2'},
        contract='a crash of one cohort member must resume only that lease from durable '
                 'per-lease receipts; the completed sibling is never relaunched')
    crashed = False
    try:
        engine.run()
    except SimulatedCrash:
        crashed = True
    assert crashed, 'the injected leaseB crash must propagate out of the wave'
    assert probe1.launches.count('leaseA') == 1, probe1.launches
    # Codex review #6: the crash must be attributable — leaseB launched and died.
    assert probe1.launches.count('leaseB') == 1, (
        'leaseB must have launched (and crashed) in life 1: %r' % probe1.launches)
    # Codex review #6: durability means ON DISK. Before any resume, the checkpoint must
    # exist and record leaseA's completed receipt — module/class memory keyed by the
    # checkpoint path is not a receipt.
    assert os.path.exists(checkpoint), (
        'no durable checkpoint written by life 1 at %s' % checkpoint)
    with open(checkpoint, 'rb') as f:
        receipt_bytes = f.read()
    assert b'leaseA' in receipt_bytes, (
        'the durable checkpoint does not record the completed leaseA receipt: %r'
        % receipt_bytes[:200])

    # Codex review #6: purge any in-memory engine state so life 2 can ONLY resume from
    # the on-disk receipts (build_engine re-imports the module fresh).
    _forget_engine_module()

    # Life 2: resume. Only leaseB may launch; the wave then completes with ONE promotion.
    probe2 = ConcurrencyProbe()
    worker2 = FakeWorker(td, probe2)
    engine2 = build_engine(
        windows, worker2, checkpoint, audit=clean_audit, promote_wave=promoter,
        rebuild_tm=tm, width=2, admitted={'c1', 'c2'}, resume=True,
        contract='a crash of one cohort member must resume only that lease from durable '
                 'per-lease receipts; the completed sibling is never relaunched')
    engine2.run()
    assert probe2.launches == ['leaseB'], (
        'resume relaunched %r — completed model work must never be re-run (constraint 5)'
        % probe2.launches)
    assert len(promoter.commits) == 1, promoter.commits
    assert set(promoter.commits[0]) == {'leaseA', 'leaseB'}, promoter.commits


def test_4_rejection_requeues_only_its_keys(td):
    """An audit rejection requeues only its own keys; clean siblings batch into the
    wave's promotion unblocked."""
    td = os.path.join(td, 't4'); os.makedirs(td)
    # Codex review #7: batching is only provable with AT LEAST TWO clean siblings — with
    # one clean member, per-lease promotion and batched promotion are indistinguishable,
    # and checking only commits[0] lets extra promotions slip through.
    windows = [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'},
               {'id': 'leaseC', 'profile': 'c1'}]

    def audit(wf_output, window):
        if window['id'] == 'leaseB' and not window.get('requeue'):
            return {'requeue_keys': ['kB1', 'kB2'], 'clean_count': 0, 'cost': 0,
                    'calls': 1, 'satisfied_keys': []}
        return clean_audit(wf_output, window)

    promoter = FakePromoter(os.path.join(td, 'store.txt'))
    engine = build_engine(
        windows, FakeWorker(td, ConcurrencyProbe()), os.path.join(td, 'cp.json'),
        audit=audit, promote_wave=promoter, rebuild_tm=FakeTM(),
        width=2, admitted={'c1', 'c2'}, max_calls=4,
        contract='an audit rejection must requeue only its own keys and must not block '
                 'the TWO clean siblings from batching into the wave\'s SINGLE promotion')
    summary = engine.run()
    assert len(promoter.commits) == 1, (
        'the accepted wave must produce EXACTLY one batched promotion commit, got %d: %r'
        % (len(promoter.commits), promoter.commits))
    assert promoter.commits[0] == ('leaseA', 'leaseC'), (
        'both clean siblings must batch into the ONE wave promotion, unblocked by the '
        'rejected member and in plan order: %r' % (promoter.commits,))
    assert summary.get('requeue_backlog_keys') == ['kB1', 'kB2'], summary
    accepted = {m for commit in promoter.commits for m in commit}
    assert 'leaseB' not in accepted, 'a rejected member must never be promoted'


def test_5_promotion_barrier_crash_exactly_once(td):
    """A crash before AND after the promotion barrier each yield exactly one effective
    promotion and one TM rebuild after resume."""
    td = os.path.join(td, 't5'); os.makedirs(td)
    windows = [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}]
    contract = ('a crash before and after the promotion barrier must produce exactly one '
                'promotion and one TM call per accepted wave (idempotent receipts)')

    # (a) crash BEFORE the promotion commit; resume must promote exactly once.
    cp_a = os.path.join(td, 'cp_before.json')
    promoter_a = FakePromoter(os.path.join(td, 'store_before.txt'), fail_times=1)
    tm_a = FakeTM()
    engine = build_engine(windows, FakeWorker(td, ConcurrencyProbe()), cp_a,
                          audit=clean_audit, promote_wave=promoter_a, rebuild_tm=tm_a,
                          width=2, admitted={'c1', 'c2'}, contract=contract)
    # Codex review #5: the first life MUST crash at the intended boundary — silently
    # accepting a normal return lets an engine defer all work to resume (or retry
    # internally) and still show the right final counts.
    crashed_a = False
    try:
        engine.run()
    except SimulatedCrash:
        crashed_a = True
    assert crashed_a, (
        'life 1 (a) must die on the injected pre-commit promoter crash — it returned '
        'normally instead')
    # Pre-resume state: the crash was BEFORE the commit, so nothing may be committed and
    # no TM rebuild may have succeeded yet.
    assert len(promoter_a.commits) == 0, (
        'crash BEFORE the commit must leave zero commits pre-resume: %r'
        % (promoter_a.commits,))
    assert tm_a.successes == 0, tm_a.successes
    _forget_engine_module()
    engine_resumed = build_engine(windows, FakeWorker(td, ConcurrencyProbe()), cp_a,
                                  audit=clean_audit, promote_wave=promoter_a,
                                  rebuild_tm=tm_a, width=2, admitted={'c1', 'c2'},
                                  resume=True, contract=contract)
    engine_resumed.run()
    assert len(promoter_a.commits) == 1, (
        'crash BEFORE the barrier: expected exactly 1 effective promotion, got %d'
        % len(promoter_a.commits))
    assert tm_a.successes == 1, tm_a.successes

    # (b) crash AFTER the promotion commit (TM rebuild dies); resume must NOT re-promote.
    cp_b = os.path.join(td, 'cp_after.json')
    promoter_b = FakePromoter(os.path.join(td, 'store_after.txt'))
    tm_b = FakeTM(fail_times=1)
    engine_b = build_engine(windows, FakeWorker(td, ConcurrencyProbe()), cp_b,
                            audit=clean_audit, promote_wave=promoter_b, rebuild_tm=tm_b,
                            width=2, admitted={'c1', 'c2'}, contract=contract)
    crashed_b = False
    try:
        engine_b.run()
    except SimulatedCrash:
        crashed_b = True
    assert crashed_b, (
        'life 1 (b) must die on the injected post-commit TM crash — it returned '
        'normally instead')
    # Pre-resume state: the commit landed, the TM rebuild did not.
    assert len(promoter_b.commits) == 1, (
        'crash AFTER the commit must leave exactly one commit pre-resume: %r'
        % (promoter_b.commits,))
    assert tm_b.successes == 0, (
        'the TM crash must leave zero SUCCESSFUL rebuilds pre-resume: %d' % tm_b.successes)
    _forget_engine_module()
    engine_b_resumed = build_engine(windows, FakeWorker(td, ConcurrencyProbe()), cp_b,
                                    audit=clean_audit, promote_wave=promoter_b,
                                    rebuild_tm=tm_b, width=2, admitted={'c1', 'c2'},
                                    resume=True, contract=contract)
    engine_b_resumed.run()
    assert len(promoter_b.commits) == 1, (
        'crash AFTER the barrier: resume double-promoted the wave (%d commits) — the '
        'promotion receipt must make the reconcile idempotent' % len(promoter_b.commits))
    assert tm_b.successes == 1, tm_b.successes


def test_6_reservation_ledger_max_calls(td):
    """max_calls=0/1/3 is one reservation covering probes+failures+retries+successes,
    reserved BEFORE spawn and never exceeded."""
    td = os.path.join(td, 't6'); os.makedirs(td)

    # EVIDENCE — today's ceiling is post-hoc accounting, not a reservation. (These runs
    # exercise the CURRENT BoundedSupervisor; its own selftest pins this overshoot as the
    # backward-compatible ceiling semantics, so no existing green pin is contradicted.)
    launches = []

    def worker(window):
        launches.append(window['id'])
        path = os.path.join(td, 'wf_%s.json' % window['id'])
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'meta': {}, 'results': []}, f)
        return path

    def audit_calls(n):
        return lambda wf, w: {'requeue_keys': [], 'clean_count': 1, 'cost': 0,
                              'calls': n, 'satisfied_keys': []}

    zero = bs.BoundedSupervisor([{'id': 'w0'}], worker, os.path.join(td, 'cp0.json'),
                                audit=audit_calls(2), max_calls=0).run()
    one = bs.BoundedSupervisor([{'id': 'w1'}], worker, os.path.join(td, 'cp1.json'),
                               audit=audit_calls(3), max_calls=1).run()
    print('    (6) EVIDENCE post-hoc ceiling today: max_calls=0 still launched %d '
          'window(s) and spent %d call(s); max_calls=1 finished with calls_spent=%d'
          % (launches.count('w0'), zero['calls_spent'], one['calls_spent']))
    assert launches.count('w0') == 1 and zero['calls_spent'] == 2, (launches, zero)
    assert one['calls_spent'] == 3, one

    # THE PIN — the engine's campaign reservation ledger.
    probes_made = []

    def probe(profile):
        probes_made.append(profile)
        return 1.0

    # max_calls=0: nothing may spawn — no probe, no worker launch.
    probe0 = ConcurrencyProbe()
    engine = build_engine(
        [{'id': 'leaseA', 'profile': 'c1'}], FakeWorker(td, probe0),
        os.path.join(td, 'eng_cp0.json'), audit=audit_calls(1),
        promote_wave=FakePromoter(os.path.join(td, 'store0.txt')), rebuild_tm=FakeTM(),
        width=1, admitted={'c1'}, max_calls=0, probe=probe,
        contract='max_calls=0/1/3 must be a reservation consumed by probes, failures, '
                 'retries and successes alike, reserved BEFORE every spawn and never '
                 'exceeded')
    engine.run()
    assert probes_made == [] and probe0.launches == [], (probes_made, probe0.launches)

    # max_calls=1 with two admitted profiles: at most ONE total consumption (the first
    # probe); dispatch must not start on an unreserved call.
    probes_made[:] = []
    probe1 = ConcurrencyProbe()
    engine = build_engine(
        [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}],
        FakeWorker(td, probe1), os.path.join(td, 'eng_cp1.json'), audit=audit_calls(1),
        promote_wave=FakePromoter(os.path.join(td, 'store1.txt')), rebuild_tm=FakeTM(),
        width=2, admitted={'c1', 'c2'}, max_calls=1, probe=probe,
        contract='max_calls=1 must cap probes+calls at one total consumption')
    engine.run()
    assert len(probes_made) + len(probe1.launches) <= 1, (probes_made, probe1.launches)

    # max_calls=3 with two admitted profiles: 2 probes + exactly 1 worker call fit; the
    # second window must never launch against an exhausted reservation.
    probes_made[:] = []
    probe3 = ConcurrencyProbe()
    engine = build_engine(
        [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}],
        FakeWorker(td, probe3), os.path.join(td, 'eng_cp3.json'), audit=audit_calls(1),
        promote_wave=FakePromoter(os.path.join(td, 'store3.txt')), rebuild_tm=FakeTM(),
        width=2, admitted={'c1', 'c2'}, max_calls=3, probe=probe,
        contract='max_calls=3 must fit 2 probes + 1 call and refuse the 4th consumption')
    summary = engine.run()
    consumed = len(probes_made) + summary.get('calls_spent', 0)
    assert consumed <= 3, 'reservation exceeded: %d consumed of 3' % consumed
    assert len(probe3.launches) == 1, probe3.launches

    # Codex review #3 (failures + retries consume the SAME ledger): a failed probe and a
    # crashed worker are consumptions too — an engine that counts only successes (or
    # releases failed attempts back to the pool) must be caught here. Fixture: probe(c1)
    # succeeds (1), probe(c2) FAILS (2), leaseA's worker launches (3) and CRASHES; with
    # max_calls=3 fully consumed there is NO budget for a retry or for leaseB.
    probe_attempts = []

    def failing_probe(profile):
        probe_attempts.append(profile)          # recorded BEFORE the failure — an
        if profile == 'c2':                     # attempt is a consumption either way
            raise SimulatedCrash('simulated probe failure on c2')
        return 1.0

    probe_f = ConcurrencyProbe()
    worker_f = FakeWorker(td, probe_f, crash_ids={'leaseA'})
    engine = build_engine(
        [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}],
        worker_f, os.path.join(td, 'eng_cpf.json'), audit=audit_calls(1),
        promote_wave=FakePromoter(os.path.join(td, 'storef.txt')), rebuild_tm=FakeTM(),
        width=2, admitted={'c1', 'c2'}, max_calls=3, probe=failing_probe,
        contract='a FAILED probe and a CRASHED worker consume the reservation exactly '
                 'like successes; with the ledger exhausted no retry and no further '
                 'lease may spawn (total attempts stay bounded)')
    try:
        engine.run()
    except SimulatedCrash:
        pass                                    # the engine may surface either failure
    total_attempts = len(probe_attempts) + len(probe_f.launches)
    assert total_attempts <= 3, (
        'failures/retries escaped the reservation ledger: %d attempts of 3 '
        '(probes=%r launches=%r)' % (total_attempts, probe_attempts, probe_f.launches))
    assert probe_f.launches.count('leaseA') <= 1, (
        'the crashed leaseA worker was RETRIED against an exhausted reservation: %r'
        % probe_f.launches)
    assert 'leaseB' not in probe_f.launches, (
        'leaseB spawned although the reservation was exhausted by failures: %r'
        % probe_f.launches)

    # Codex review #3 (reservation is taken ATOMICALLY before spawn): two leases race
    # for ONE reservation under width 2 — a check-then-act engine reserves post-hoc and
    # launches both (they would meet on the barrier); an atomic pre-spawn ledger admits
    # exactly one. No probe in this case, so the single reservation belongs to a worker.
    probe_r = ConcurrencyProbe()
    worker_r = FakeWorker(td, probe_r, barrier=threading.Barrier(2), barrier_wait_s=0.5)
    engine = build_engine(
        [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}],
        worker_r, os.path.join(td, 'eng_cpr.json'), audit=audit_calls(1),
        promote_wave=FakePromoter(os.path.join(td, 'storer.txt')), rebuild_tm=FakeTM(),
        width=2, admitted={'c1', 'c2'}, max_calls=1,
        contract='the reservation must be taken atomically BEFORE each concurrent spawn '
                 '— width 2 racing for max_calls=1 admits exactly one worker, never both')
    engine.run()
    assert len(probe_r.launches) == 1, (
        'concurrent spawn beat the reservation ledger (check-then-act race): %d workers '
        'launched against max_calls=1: %r' % (len(probe_r.launches), probe_r.launches))
    assert worker_r.met_barrier == [], (
        'both racing workers rendezvoused — the reservation was not atomic: %r'
        % worker_r.met_barrier)


def test_7_coord_dir_and_admitted_parked_filtering(td):
    """Custom coordinator dir reaches every child; the parked guard counts only the
    admitted fleet."""
    td = os.path.join(td, 't7'); os.makedirs(td)
    problems = []

    # (7a) CURRENT CODE — bounded_staged_run.make_run_window's pre-dispatch parked guard
    # counts EVERY validated account, so a healthy EXCLUDED account masks that every
    # ADMITTED account is parked (audit P1#10) and dispatch is entered anyway.
    coord = os.path.join(td, 'coord'); os.makedirs(coord)
    with open(os.path.join(coord, 'state.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'leases': [{'id': 'leaseX', 'state': 'prepared'}]}, f)
    db = os.path.join(td, 'jobs.sqlite')
    dbc = mao.connect(db)
    with dbc:
        dbc.execute("INSERT INTO accounts(name,config_dir,parked_until,validated,"
                    "updated_at) VALUES('accX',?,?,1,?)",
                    (td, mao.PARKED_FOREVER, mao.now_iso()))
        dbc.execute("INSERT INTO accounts(name,config_dir,parked_until,validated,"
                    "updated_at) VALUES('accY',?,0,1,?)", (td, mao.now_iso()))
        dbc.execute("INSERT INTO jobs(external_id,cwd,output_path,manifest_path,"
                    "profile_slot,state) VALUES('leaseX',?,?,?, 'accX','pending')",
                    (td, os.path.join(td, 'out.json'), os.path.join(td, 'manifest.json')))
    dbc.close()
    ctx = bsr.RunContext(db=db, coord_dir=coord,
                         coordinator=os.path.join(HERE, 'coordinator.py'),
                         cwd=td, events=None, run_id='t7',
                         probe_latencies={'accX': 10.0})   # accX admitted; accY EXCLUDED
    dispatch_entered = {'n': 0}
    original_run_once = mao.cmd_run_once

    def spy_run_once(ns):
        dispatch_entered['n'] += 1
        return original_run_once(ns)

    mao.cmd_run_once = spy_run_once
    stop_msg = None
    try:
        try:
            bsr.make_run_window(ctx)({'id': 'leaseX'})
        except SystemExit as exc:
            stop_msg = str(exc)
    finally:
        mao.cmd_run_once = original_run_once
    print('    (7) EVIDENCE admitted accX parked + excluded-healthy accY present: '
          'dispatch entered %d time(s); stop message: %r'
          % (dispatch_entered['n'], stop_msg))
    if dispatch_entered['n']:
        problems.append(
            'the pre-dispatch guard counted the EXCLUDED healthy account as runnable and '
            'entered dispatch %d time(s) although every ADMITTED account is parked'
            % dispatch_entered['n'])
    if not stop_msg or 'parked' not in stop_msg.lower():
        problems.append(
            'the stop does not name the admitted-fleet-all-parked condition (got %r)'
            % stop_msg)

    # (7b) THE ENGINE PIN — width from the admitted-minus-parked fleet only, and the
    # custom coordinator dir OBSERVED FROM INSIDE every child (the H1386 D4 exactness the
    # engine must preserve). Codex review #2: a summary echo of the constructor argument
    # proves nothing — the child itself must be able to see the coordinator path (via the
    # window the engine hands it, or the child env), recorded AT CALL TIME on the fake
    # side.
    try:
        probe = ConcurrencyProbe()
        child_observed = []
        inner_worker = FakeWorker(td, probe)

        def observing_worker(window):
            child_observed.append(
                window.get('coord_dir') or os.environ.get('PWG_COORDINATOR_DIR'))
            return inner_worker(window)

        engine = build_engine(
            [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'}],
            observing_worker, os.path.join(td, 'eng_cp.json'), audit=clean_audit,
            promote_wave=FakePromoter(os.path.join(td, 'store.txt')), rebuild_tm=FakeTM(),
            width=2, admitted={'c1', 'c2'}, parked={'c2'}, coord_dir=coord,
            contract='wave width must be computed from the admitted-minus-parked fleet '
                     'and the custom coordinator dir must be OBSERVABLE from inside '
                     'every child at call time')
        summary = engine.run()
        if probe.launches.count('leaseB'):
            problems.append('a lease bound to a PARKED profile was dispatched')
        if summary.get('effective_width') not in (1,):
            problems.append('effective width must collapse to the admitted-minus-parked '
                            'fleet (expected 1, got %r)' % summary.get('effective_width'))
        expected_coord = os.path.abspath(coord)
        if not child_observed or any(obs != expected_coord for obs in child_observed):
            problems.append('the coordinator dir was not observable from inside the '
                            'child(ren) at call time (observed %r, expected %r) — an '
                            'engine-summary echo of the constructor argument is not '
                            'propagation' % (child_observed, expected_coord))
        if summary.get('coord_dir') != expected_coord:
            problems.append('the custom coordinator dir did not reach the engine children '
                            '(expected %r)' % expected_coord)
    except MissingBehavior as exc:
        problems.append(str(exc))

    # (7c) THE ENGINE PIN, all-admitted-parked — Codex review #2: the engine fixture must
    # itself contain the P1#10 shape: EVERY admitted profile parked while a healthy but
    # EXCLUDED profile (c3, bound to leaseX) exists in the plan. The engine must dispatch
    # NOTHING and stop with a reason naming the parked condition — the excluded healthy
    # profile must not mask it. (7a) above proves the CURRENT control path gets this
    # wrong; this pin binds the ENGINE.
    try:
        probe_p = ConcurrencyProbe()
        engine = build_engine(
            [{'id': 'leaseA', 'profile': 'c1'}, {'id': 'leaseB', 'profile': 'c2'},
             {'id': 'leaseX', 'profile': 'c3'}],
            FakeWorker(td, probe_p), os.path.join(td, 'eng_cp_parked.json'),
            audit=clean_audit,
            promote_wave=FakePromoter(os.path.join(td, 'store_parked.txt')),
            rebuild_tm=FakeTM(),
            width=2, admitted={'c1', 'c2'}, parked={'c1', 'c2'}, coord_dir=coord,
            contract='with EVERY admitted profile parked, the engine must dispatch '
                     'nothing and stop naming the parked condition — a healthy EXCLUDED '
                     'profile in the plan must not mask it')
        stop_reason = ''
        try:
            summary_p = engine.run()
            stop_reason = str(summary_p.get('stop_reason', ''))
        except SystemExit as exc:
            stop_reason = str(exc)
        if probe_p.launches:
            problems.append('with all admitted profiles parked the engine still '
                            'dispatched %r (the excluded healthy c3 must not count)'
                            % probe_p.launches)
        if 'parked' not in stop_reason.lower():
            problems.append('the engine stop does not name the admitted-fleet-all-parked '
                            'condition (got %r)' % stop_reason)
    except MissingBehavior as exc:
        problems.append(str(exc))
    if problems:
        raise MissingBehavior('; '.join(problems))


# ---------------------------------------------------------------------------
# Runner — run ALL pins, report each RED with its missing-behavior reason.
# ---------------------------------------------------------------------------

TESTS = [
    ('1 two profile-bound leases: peak_concurrency >= 2', test_1_barrier_concurrency),
    ('2 reverse completion == serial order/store bytes', test_2_reverse_completion_determinism),
    ('3 crash resumes only its lease, sibling not relaunched', test_3_crash_resumes_only_its_lease),
    ('4 rejection requeues only its keys, siblings batch', test_4_rejection_requeues_only_its_keys),
    ('5 promotion-barrier crash: exactly one promotion+TM', test_5_promotion_barrier_crash_exactly_once),
    ('6 max_calls=0/1/3 reservation never exceeded', test_6_reservation_ledger_max_calls),
    ('7 coord-dir exactness + admitted/parked filtering', test_7_coord_dir_and_admitted_parked_filtering),
]


def main():
    failures = []
    with tempfile.TemporaryDirectory() as td:
        for label, fn in TESTS:
            try:
                fn(td)
            except AssertionError as exc:
                failures.append((label, str(exc)))
                print('  RED   (%s):\n        %s' % (label, exc))
            else:
                print('  GREEN (%s)' % label)
    total = len(TESTS)
    if failures:
        print('cohort_engine_selftest: %d RED / %d GREEN — RED is the EXPECTED H1437 '
              'Phase 0 state: every RED above names missing Phase 1-3 behavior, not a '
              'fixture defect. The suite must flip GREEN with no edits outside the '
              'build_engine adapter.' % (len(failures), total - len(failures)))
        return 1
    print('cohort_engine_selftest: PASS (%d pins)' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
