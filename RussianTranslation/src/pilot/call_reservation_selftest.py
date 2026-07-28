#!/usr/bin/env python
"""Hermetic self-test for the paid-call reservation ledger."""
import multiprocessing
import json
import os
import subprocess
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
            assert mao.live_probe(cfg, call_reservation=probes, account='a') < 30000
            assert probes.spent() == 2 and len(calls) == 2
            assert probes.usage()['observed_cost_usd'] == 0.02

            mao.run_tree_kill = lambda *_a, **_k: SimpleNamespace(
                returncode=0, stderr='', stdout='not-json')
            malformed = CallReservationLedger(path, 'probe-malformed', 3)
            try:
                mao.live_probe(cfg, call_reservation=malformed, account='a')
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
                mao.live_probe(cfg, call_reservation=timeout, account='a')
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
                cfg, 'claude', 30, route='test', window='w', account_label='a',
                sample_index=0, warmup=False, git_sha='x', cli_version='x',
                call_reservation=sweep_zero)
            raise AssertionError('latency sweep bypassed max_calls=0')
        except CallLimitReached:
            pass
        assert sweep_zero.spent() == 0
    print('call_reservation_selftest: PASS (0/1/N, race/resume, finalization, probes/cost)')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
