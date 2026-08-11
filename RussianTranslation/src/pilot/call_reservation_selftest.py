#!/usr/bin/env python
"""Hermetic self-test for the paid-call reservation ledger."""
import multiprocessing
import json
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace

from call_reservation import (CallLimitReached, CallReservationLedger,
                              normalize_telemetry, unevaluable_telemetry)


def _race(path, run_id, limit, out):
    ledger = CallReservationLedger(path, run_id, limit)
    try:
        out.put(ledger.reserve('race')['ordinal'])
    except CallLimitReached:
        out.put(None)


def main():
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'calls.json')
        zero = CallReservationLedger(path, 'zero', 0)
        try:
            zero.reserve('worker')
            raise AssertionError('max_calls=0 permitted a reservation')
        except CallLimitReached:
            pass
        assert zero.spent() == 0

        one = CallReservationLedger(path, 'one', 1)
        one.reserve('probe:warmup')
        try:
            one.reserve('probe:measured')
            raise AssertionError('max_calls=1 permitted a second reservation')
        except CallLimitReached:
            pass
        assert one.spent() == 1

        q = multiprocessing.Queue()
        procs = [multiprocessing.Process(target=_race, args=(path, 'race', 7, q))
                 for _ in range(20)]
        for proc in procs:
            proc.start()
        for proc in procs:
            proc.join(20)
            assert proc.exitcode == 0, proc.exitcode
        won = [q.get(timeout=2) for _ in procs]
        assert len([x for x in won if x is not None]) == 7, won
        resumed = CallReservationLedger(path, 'race', 7)
        assert resumed.spent() == 7
        try:
            resumed.reserve('resume')
            raise AssertionError('resume exceeded the durable ceiling')
        except CallLimitReached:
            pass

        cumulative = CallReservationLedger(path, 'usage', 3)
        failed = cumulative.reserve('failed')
        cumulative.finalize(failed, unevaluable_telemetry())
        # Exact replay is idempotent; a conflicting replay is refused.
        cumulative.finalize(failed, unevaluable_telemetry())
        try:
            cumulative.finalize(
                failed, {'cost_evaluable': True, 'observed_cost_usd': 1.0})
            raise AssertionError('conflicting finalization was accepted')
        except ValueError:
            pass
        success = cumulative.reserve('success')
        cumulative.finalize(success, {
            'cost_evaluable': True, 'observed_cost_usd': 0.25,
            'input_tokens': 10, 'output_tokens': 2,
        })
        usage = cumulative.usage()
        assert usage['finalized_calls'] == 2 and usage['unevaluable_calls'] == 1, usage
        assert usage['cost_evaluable'] is False and usage['observed_cost_usd'] == 0.25, usage
        for bad in (float('nan'), -1, True):
            try:
                normalize_telemetry({
                    'cost_evaluable': True, 'observed_cost_usd': bad})
                raise AssertionError('invalid telemetry accepted: %r' % bad)
            except ValueError:
                pass
            try:
                normalize_telemetry({
                    'cost_evaluable': True, 'observed_cost_usd': 0,
                    'input_tokens': bad})
                raise AssertionError('invalid token telemetry accepted: %r' % bad)
            except ValueError:
                pass

        # Probe integration: the profile claim covers the pair and each phase reserves before
        # entering the raw call. A malformed warmup spends one; a measured timeout spends two.
        import max_account_orchestrator as mao
        cfg = os.path.join(td, 'cfg')
        os.makedirs(cfg)
        original_runner = mao.run_tree_kill
        try:
            calls = []

            def success_runner(*_args, **_kwargs):
                calls.append(1)
                # A nested claim must fail: live_probe still owns the pair-wide profile lock.
                try:
                    with mao.ActiveCallClaim(mao.config_dir_fingerprint(cfg)):
                        raise AssertionError('profile claim was released within probe pair')
                except RuntimeError:
                    pass
                return SimpleNamespace(
                    returncode=0, stderr='', stdout=json.dumps({
                        'type': 'result', 'subtype': 'success', 'is_error': False,
                        'structured_output': {'ok': True},
                        'usage': {'input_tokens': 3, 'output_tokens': 1},
                        'total_cost_usd': 0.01,
                    }))

            mao.run_tree_kill = success_runner
            probes = CallReservationLedger(path, 'probes-ok', 2)
            assert mao.live_probe(cfg, claude=sys.executable, call_reservation=probes, account='a') < 30000
            assert probes.spent() == 2 and len(calls) == 2
            assert probes.usage()['observed_cost_usd'] == 0
            assert probes.usage()['cost_evaluable'] is False

            mao.run_tree_kill = lambda *_a, **_k: SimpleNamespace(
                returncode=0, stderr='', stdout='not-json')
            malformed = CallReservationLedger(path, 'probe-malformed', 3)
            try:
                mao.live_probe(cfg, claude=sys.executable, call_reservation=malformed, account='a')
                raise AssertionError('malformed warmup was accepted')
            except SystemExit:
                pass
            assert malformed.spent() == 1 and malformed.usage()['cost_evaluable'] is False

            phase = [0]

            def timeout_runner(*args, **kwargs):
                phase[0] += 1
                if phase[0] == 2:
                    raise subprocess.TimeoutExpired(args[0] if args else 'probe', 1)
                return success_runner(*args, **kwargs)

            mao.run_tree_kill = timeout_runner
            timeout = CallReservationLedger(path, 'probe-timeout', 3)
            try:
                mao.live_probe(cfg, claude=sys.executable, call_reservation=timeout, account='a')
                raise AssertionError('measured timeout was accepted')
            except SystemExit:
                pass
            assert timeout.spent() == 2 and timeout.usage()['cost_evaluable'] is False
        finally:
            mao.run_tree_kill = original_runner

        import latency_payload_sweep as sweep
        sweep_zero = CallReservationLedger(path, 'sweep-zero', 0)
        try:
            sweep.one_call(
                cfg, sys.executable, 30, route='test', window='w', account_label='a',
                sample_index=0, warmup=False, git_sha='x', cli_version='x',
                # `active_claim` is REQUIRED keyword-only on one_call; None is its documented
                # "acquire one for me" contract (_probe_call self-claims when it is None). The
                # selftest omitted it entirely, so this case raised TypeError before it could
                # ever reach the max_calls=0 refusal it exists to prove. Found on rebase onto
                # master, 26-07-2026 -- the defect is in the branch as delivered, not the rebase.
                call_reservation=sweep_zero, active_claim=None)
            raise AssertionError('latency sweep bypassed max_calls=0')
        except CallLimitReached:
            pass
        assert sweep_zero.spent() == 0
    _test_h2079_945_duration_capture()
    print('call_reservation_selftest: PASS (0/1/N, race/resume, finalization, probes/cost, durations)')


def _test_h2079_945_duration_capture():
    """H2079 / #945: the envelope's own timings are captured, and their absence is byte-invisible.

    Wall clock alone cannot separate a slow route from an in-CLI retry storm, which is what made the
    c4 latency series unusable as route evidence. The discriminator was already in the envelope and
    thrown away. The backward-compat half matters as much as the capture: `_read()` re-validates
    every stored item and `finalize()` compares an already-finalized item against a freshly
    normalized one, so a pre-H2079 ledger must normalize to EXACTLY the bytes it already holds.
    """
    import call_reservation as cr

    # 1. captured from the envelope, alongside (not instead of) the token/cost fields
    tel = cr.telemetry_from_cli_wrapper({
        'usage': {'input_tokens': 10, 'output_tokens': 2,
                  'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 90485},
        'total_cost_usd': 0.29, 'duration_ms': 78415, 'duration_api_ms': 12987,
    })
    assert tel['duration_api_ms'] == 12987 and tel['duration_ms'] == 78415, tel
    assert tel['cost_evaluable'] is True and tel['cache_creation_tokens'] == 90485, tel
    # the decomposition the whole issue exists to make possible
    assert tel['duration_ms'] - tel['duration_api_ms'] == 65428

    # 2. ABSENT -> the keys must not appear at all (never an explicit None)
    bare = cr.telemetry_from_cli_wrapper({'usage': {}, 'total_cost_usd': 0.0})
    assert 'duration_ms' not in bare and 'duration_api_ms' not in bare, bare
    assert cr.normalize_telemetry(dict(bare)) == bare, 'pre-H2079 telemetry did not round-trip'
    assert 'duration_ms' not in cr.unevaluable_telemetry()

    # 3. a garbage duration must NOT demote cost evaluability (evaluability is about COST)
    for junk in (-1, float('nan'), True, 'fast', None):
        noisy = cr.telemetry_from_cli_wrapper({
            'usage': {'input_tokens': 1, 'output_tokens': 1,
                      'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0},
            'total_cost_usd': 0.01, 'duration_api_ms': junk})
        assert noisy['cost_evaluable'] is True, (junk, noisy)
        assert 'duration_api_ms' not in noisy, (junk, noisy)

    # 4. an explicitly invalid duration handed straight to the validator is still refused
    for junk in (-1, float('inf'), True):
        try:
            cr.normalize_telemetry({'cost_evaluable': False, 'duration_api_ms': junk})
        except ValueError:
            pass
        else:
            raise AssertionError('normalize_telemetry accepted duration %r' % (junk,))

    # 5. it survives a real reserve/finalize round trip AND the ledger's own consistency re-read
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'ledger.json')
        ledger = CallReservationLedger(path, 'h2079', max_calls=2)
        item = ledger.finalize(ledger.reserve('probe'), tel)
        assert item['telemetry']['duration_api_ms'] == 12987, item
        reread = CallReservationLedger(path, 'h2079', max_calls=2).snapshot()
        assert reread['reservations'][0]['telemetry']['duration_api_ms'] == 12987
        # durations must NOT leak into the cumulative usage block (that is tokens + cost only)
        assert 'duration_api_ms' not in reread['usage'], reread['usage']
        # finalize() is idempotent only if normalization is stable across the new field
        assert ledger.finalize(item, tel)['telemetry']['duration_api_ms'] == 12987
    print('  H2079 #945: duration_ms/duration_api_ms captured, absent-is-invisible, ledger-stable')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
