#!/usr/bin/env python3
"""Pins for `cohort_live_dispatch` (H4527 rung 4) — the LIVE cohort wiring.

Each pin is a claim about the live route that no live window is needed to check: the profile
binding is deterministic, a width the fleet cannot fill is refused before anything is spent,
a wave promotes exactly ONCE for the whole accepted set, and no supervisor-only ceiling is
ever silently dropped.
Run: `python cohort_live_dispatch_selftest.py`
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cohort_live_dispatch as cld  # noqa: E402


def test_a_binding_is_deterministic_round_robin():
    windows = [{'id': 'w1'}, {'id': 'w2'}, {'id': 'w3'}]
    first = cld.assign_profiles(windows, ['c1', 'c2'])
    assert [w['profile'] for w in first] == ['c1', 'c2', 'c1'], first
    # Same inputs -> same binding, or a resumed wave would re-bind its leases and the engine's
    # per-profile exclusion would mean nothing across lives.
    again = cld.assign_profiles(windows, ['c1', 'c2'])
    assert [w['profile'] for w in again] == [w['profile'] for w in first]
    # The caller's dicts are never mutated (the serial path shares those window objects).
    assert all('profile' not in w for w in windows), windows
    # An explicit binding always wins over the round robin.
    pinned = cld.assign_profiles([{'id': 'w1', 'profile': 'c2'}, {'id': 'w2'}], ['c1', 'c2'])
    assert [w['profile'] for w in pinned] == ['c2', 'c1'], pinned
    try:
        cld.assign_profiles(windows, [])
        raise AssertionError('an empty fleet must not bind anything')
    except ValueError:
        pass
    print('  (a) profile binding is deterministic, round-robin, non-mutating; empty fleet '
          'raises: PASS')


def test_b_fleet_guard_refuses_a_width_the_fleet_cannot_fill():
    ok, why = cld.fleet_guard(2, ['c1'])
    assert not ok and 'needs 2 distinct' in why and 'c1' in why, why
    assert 'human roster act' in why, 'the refusal must say who can widen the fleet: %r' % why
    ok2, why2 = cld.fleet_guard(2, ['c1', 'c2'])
    assert ok2, why2
    ok3, why3 = cld.fleet_guard(1, ['c1'])
    assert ok3, why3
    for bad in ([], None):
        ok4, why4 = cld.fleet_guard(1, bad)
        assert not ok4 and 'no probed-healthy profile' in why4, why4
    ok5, why5 = cld.fleet_guard('two', ['c1', 'c2'])
    assert not ok5 and 'not an integer' in why5, why5
    # Duplicates are not a fleet: the same profile twice still runs one job at a time.
    ok6, why6 = cld.fleet_guard(2, ['c1', 'c1'])
    assert not ok6, why6
    print('  (b) fleet_guard refuses width > distinct healthy profiles (and dedupes): PASS')


def test_c_unsupported_ceilings_are_named_not_dropped():
    assert cld.unsupported_ceilings({}) == []
    assert cld.unsupported_ceilings({'max_calls': 4}) == []
    named = cld.unsupported_ceilings({'cost_ceiling': 2.0, 'max_clean': 3,
                                      'max_windows': None, 'empty_streak': 0})
    assert named == ['cost_ceiling', 'max_clean'], named
    assert set(cld.SUPERVISOR_ONLY_CEILINGS) == {
        'cost_ceiling', 'max_clean', 'max_windows', 'empty_streak'}
    print('  (c) supervisor-only ceilings that are SET are named for refusal: PASS')


def test_d_wave_promotes_exactly_once_for_the_whole_accepted_set():
    calls = []

    def promote_leases(lease_ids, gen_model_version):
        calls.append((list(lease_ids), gen_model_version))
        return {'returncode': 0, 'promoted_at': '2026-09-11T06:00:00Z', 'stdout_tail': 'ok'}

    promote_wave = cld.make_wave_promoter(promote_leases, 'claude-sonnet-5')
    receipt = promote_wave([{'id': 'w1'}, {'id': 'w2'}])
    assert len(calls) == 1, 'a wave must promote ONCE, not per lease: %r' % (calls,)
    assert calls[0] == (['w1', 'w2'], 'claude-sonnet-5'), calls
    assert receipt['members'] == ['w1', 'w2'] and receipt['promoted'] is True, receipt
    assert receipt['returncode'] == 0 and receipt['promoted_at'], receipt
    import json
    json.dumps(receipt)   # the engine persists this receipt: it must be serialisable
    # An empty accepted set still calls through once with nothing (the coordinator's
    # 'no ready leases' no-op), never silently claims a promotion it did not make.
    calls.clear()
    empty = promote_wave([])
    assert calls == [([], 'claude-sonnet-5')] and empty['members'] == [], (calls, empty)
    print('  (d) one batched promote per wave, serialisable receipt naming its leases: PASS')


def test_e_profileless_window_is_refused_loudly(td):
    def never(_window):
        raise AssertionError('a refused cohort run must not dispatch anything')

    try:
        cld.run_cohort_live([{'id': 'w1'}], 1, never,
                            os.path.join(td, 'cp.json'), admitted={'c1'})
        raise AssertionError('a profile-less live window was accepted')
    except SystemExit as exc:
        assert 'profile binding' in str(exc) and 'w1' in str(exc), exc
    # ...and a width the fleet cannot fill is refused at the same door, before dispatch.
    try:
        cld.run_cohort_live([{'id': 'w1', 'profile': 'c1'}], 2, never,
                            os.path.join(td, 'cp2.json'), admitted={'c1'})
        raise AssertionError('width 2 ran on a one-profile fleet')
    except SystemExit as exc:
        assert 'needs 2 distinct' in str(exc), exc
    print('  (e) a profile-less window and an unfillable width are both refused before any '
          'dispatch: PASS')


def test_f_live_wave_runs_through_the_engine(td):
    """The wiring end to end on fake workers: two profiles, one wave, one promote."""
    dispatched = []
    promoted = []

    def run_window(window):
        dispatched.append((window['id'], window.get('profile'), window.get('wave_promote')))
        path = os.path.join(td, window['id'] + '.json')
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write('{}')
        return path

    def audit(_path, window):
        return {'clean': True, 'id': window['id']}

    def promote_leases(lease_ids, _gen):
        promoted.append(list(lease_ids))
        return {'returncode': 0, 'promoted_at': '2026-09-11T06:00:00Z'}

    windows = cld.assign_profiles(
        [{'id': 'w1', 'wave_promote': True}, {'id': 'w2', 'wave_promote': True}], ['c1', 'c2'])
    summary = cld.run_cohort_live(
        windows, 2, run_window, os.path.join(td, 'wave.json'), audit=audit,
        promote_wave=cld.make_wave_promoter(promote_leases, 'claude-sonnet-5'),
        admitted={'c1', 'c2'}, max_calls=4)
    assert sorted(d[0] for d in dispatched) == ['w1', 'w2'], dispatched
    assert sorted(d[1] for d in dispatched) == ['c1', 'c2'], (
        'each lease must have been dispatched on its OWN profile: %r' % (dispatched,))
    assert all(d[2] is True for d in dispatched), (
        'a wave-dispatched window must carry wave_promote so run_window stands down: %r'
        % (dispatched,))
    assert len(promoted) == 1, 'exactly one promote per wave: %r' % (promoted,)
    assert sorted(promoted[0]) == ['w1', 'w2'], promoted
    assert summary.get('peak_concurrency', 0) >= 1, summary
    print('  (f) a live-shaped wave dispatches per profile and promotes once: PASS')


def main():
    import tempfile
    test_a_binding_is_deterministic_round_robin()
    test_b_fleet_guard_refuses_a_width_the_fleet_cannot_fill()
    test_c_unsupported_ceilings_are_named_not_dropped()
    test_d_wave_promotes_exactly_once_for_the_whole_accepted_set()
    with tempfile.TemporaryDirectory() as td:
        test_e_profileless_window_is_refused_loudly(td)
        test_f_live_wave_runs_through_the_engine(td)
    print('cohort_live_dispatch_selftest: 6 pins PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
