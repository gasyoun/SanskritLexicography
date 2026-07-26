#!/usr/bin/env python
"""Focused offline pins for coordinator hardening added after the 2026-07-25 audit."""
import contextlib
import io
import json
import os
import sys
import tempfile
from types import SimpleNamespace

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Isolation from production data, established before any repo import (several modules
# resolve store/coordinator constants at import time). See selftest_isolation.py.
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selftest_isolation import guard as _isolation_guard  # noqa: E402
_isolation_guard()

# Avoid resolving or touching the canonical shared store merely by importing coordinator from a
# linked worktree whose Git safe.directory policy may intentionally reject child git commands.
_IMPORT_SANDBOX = tempfile.TemporaryDirectory(prefix='coordinator_hardening_import_')
os.environ['PWG_RU_STORE'] = os.path.join(_IMPORT_SANDBOX.name, 'store.jsonl')
os.environ['PWG_RU_TM_DIR'] = os.path.join(_IMPORT_SANDBOX.name, 'tm')
os.environ['PWG_COORDINATOR_DIR'] = os.path.join(_IMPORT_SANDBOX.name, 'coordinator')

import coordinator


def expect_refusal(fn, needle):
    try:
        fn()
    except SystemExit as exc:
        if needle not in str(exc):
            raise AssertionError('expected %r in refusal, got %r' % (needle, str(exc)))
    else:
        raise AssertionError('expected SystemExit containing %r' % needle)


def test_preflight_fail_closed():
    with tempfile.TemporaryDirectory() as tmp:
        missing = os.path.join(tmp, 'missing.json')
        expect_refusal(
            lambda: coordinator.enforce_cost_gate(missing, 'x'),
            'required preflight is unreadable')

        malformed = os.path.join(tmp, 'malformed.json')
        with open(malformed, 'w', encoding='utf-8') as f:
            f.write('{')
        expect_refusal(
            lambda: coordinator.enforce_cost_gate(malformed, 'x'),
            'required preflight is unreadable')

        unsupported = os.path.join(tmp, 'unsupported.json')
        with open(unsupported, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'unknown', 'cost_gate': {'over_ceiling': False}}, f)
        expect_refusal(
            lambda: coordinator.enforce_cost_gate(unsupported, 'x'),
            'unsupported schema')

        missing_verdict = os.path.join(tmp, 'missing-verdict.json')
        with open(missing_verdict, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.performance_preflight.v1'}, f)
        expect_refusal(
            lambda: coordinator.enforce_cost_gate(missing_verdict, 'x'),
            'no boolean cost verdict')

        clean = os.path.join(tmp, 'clean.json')
        with open(clean, 'w', encoding='utf-8') as f:
            json.dump({
                'schema': 'pwg.performance_preflight.v1',
                'cost_gate': {'over_ceiling': False},
            }, f)
        coordinator.enforce_cost_gate(clean, 'x')

        matrix = os.path.join(tmp, 'matrix.json')
        with open(matrix, 'w', encoding='utf-8') as f:
            json.dump({
                'schema': 'pwg.performance_preflight.matrix.v1',
                'reports': [{
                    'schema': 'pwg.performance_preflight.v1',
                    'cost_gate': {'over_ceiling': False},
                }],
            }, f)
        coordinator.enforce_cost_gate(matrix, 'x')

        sealed_hash = coordinator.sha256_file(clean)
        lease = {
            'id': 'sealed',
            'target': 'nominal:x',
            'preflight_path': clean,
            'preflight_sha256': sealed_hash,
            'preflight_allow_over_cost': False,
        }
        coordinator.validate_lease_preflight(lease)
        with open(clean, 'a', encoding='utf-8') as f:
            f.write('\n')
        expect_refusal(
            lambda: coordinator.validate_lease_preflight(lease),
            'sealed preflight hash changed')
        expect_refusal(
            lambda: coordinator.validate_lease_preflight({
                'id': 'legacy', 'target': 'x', 'preflight_path': clean}),
            'no sealed preflight evidence')
    print('  preflight: schema/verdict/hash fail closed; v1 + matrix pass')


def test_record_output_batch_progress():
    original = coordinator.record_output
    seen = []

    def fake_record(args):
        seen.append((
            args.lease_id, args.workflow_result, args.run_id,
            args.result_sha256))
        if args.lease_id == 'b':
            raise SystemExit('synthetic second-item failure')

    coordinator.record_output = fake_record
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            expect_refusal(
                lambda: coordinator.record_output_batch(SimpleNamespace(
                    record=[['a', 'a.json', 'run-a', 'sha-a'],
                            ['b', 'b.json', 'run-b', 'sha-b'],
                            ['c', 'c.json', 'run-c', 'sha-c']],
                    allow_stale=False)),
                'synthetic second-item failure')
    finally:
        coordinator.record_output = original
    lines = [
        line.split(': ', 1)[1] for line in buf.getvalue().splitlines()
        if line.startswith('RECORD_OUTPUT_BATCH_PROGRESS: ')
    ]
    payloads = [json.loads(line) for line in lines]
    if seen != [
            ('a', 'a.json', 'run-a', 'sha-a'),
            ('b', 'b.json', 'run-b', 'sha-b')]:
        raise AssertionError('batch did not remain sequential/fail-fast: %r' % (seen,))
    if len(payloads) != 2:
        raise AssertionError('expected commit + failure progress, got %r' % payloads)
    if payloads[-1] != {
            'schema': coordinator.RECORD_BATCH_SCHEMA,
            'recorded': ['a'],
            'remaining': ['b', 'c'],
            'failed': {
                'lease_id': 'b',
                'type': 'SystemExit',
                'message': 'synthetic second-item failure',
            }}:
        raise AssertionError('unexpected failure receipt: %r' % payloads[-1])
    expect_refusal(
        lambda: coordinator.record_output_batch(SimpleNamespace(
            record=[['a', 'a', '-', '-'], ['a', 'b', '-', '-']],
            allow_stale=False)),
        'duplicate lease ids')
    print('  record batch: per-item semantics, durable prefix receipt, fail-fast remainder')


def test_result_submission_seal():
    with tempfile.TemporaryDirectory() as tmp:
        source = os.path.join(tmp, 'result.json')
        payload = b'{"result":{"results":[]}}\n'
        with open(source, 'wb') as f:
            f.write(payload)
        expected = coordinator.hashlib.sha256(payload).hexdigest()
        sealed = coordinator.seal_workflow_submission(
            source, os.path.join(tmp, 'artifacts'), expected)
        with open(source, 'wb') as f:
            f.write(b'{"substituted":true}\n')
        if open(sealed, 'rb').read() != payload:
            raise AssertionError('sealed submission changed with the source path')
        expect_refusal(
            lambda: coordinator.seal_workflow_submission(
                source, os.path.join(tmp, 'other'), expected),
            'result substitution refused')
    print('  result binding: copied bytes are hash-sealed before audit; substitution refused')


def test_registry_projection_fail_closed():
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        registry = coordinator.paths()['registry']
        lease = {
            'id': 'lease-1',
            'kind': 'nominal',
            'target': 'nominal:k',
            'state': 'promoted',
            'artifact_dir': os.path.join(tmp, 'artifacts', 'lease-1'),
        }
        event_data = {'journal': os.path.join(tmp, 'promotion.json')}
        event_ts = '2026-07-25T00:00:00Z'

        with open(registry, 'w', encoding='utf-8') as f:
            f.write('{malformed\n')
        try:
            coordinator.registry_promotion_event(
                lease, 'promotion-1', event_data, event_ts=event_ts)
            raise AssertionError('malformed registry was accepted')
        except coordinator.promotion_journal.JournalError as exc:
            assert 'malformed JSONL' in str(exc), exc

        with open(registry, 'w', encoding='utf-8') as f:
            json.dump({'schema': coordinator.REGISTRY_SCHEMA}, f)
        try:
            coordinator.registry_promotion_event(
                lease, 'promotion-1', event_data, event_ts=event_ts)
            raise AssertionError('parseable short registry row was accepted')
        except coordinator.promotion_journal.JournalError as exc:
            assert 'not newline-terminated' in str(exc), exc

        with open(registry, 'w', encoding='utf-8'):
            pass
        assert coordinator.registry_promotion_event(
            lease, 'promotion-1', event_data, event_ts=event_ts)
        before = open(registry, 'rb').read()
        assert before.endswith(b'\n')

        original_sync = coordinator.fsync_existing_path
        synced = []
        coordinator.fsync_existing_path = lambda path: synced.append(path)
        try:
            assert not coordinator.registry_promotion_event(
                lease, 'promotion-1', event_data, event_ts=event_ts)
        finally:
            coordinator.fsync_existing_path = original_sync
        assert synced == [registry]
        assert open(registry, 'rb').read() == before
        try:
            coordinator.registry_promotion_event(
                lease, 'promotion-1', {'journal': 'substituted'},
                event_ts=event_ts)
            raise AssertionError('same promotion identity with changed payload was accepted')
        except coordinator.promotion_journal.JournalError as exc:
            assert 'different payload' in str(exc), exc
    if old is None:
        os.environ.pop('PWG_COORDINATOR_DIR', None)
    else:
        os.environ['PWG_COORDINATOR_DIR'] = old
    print('  registry: malformed/short/substituted rows fail; retry re-fsyncs exact row')


def main():
    test_preflight_fail_closed()
    test_record_output_batch_progress()
    test_result_submission_seal()
    test_registry_projection_fail_closed()
    print('coordinator_hardening_selftest: PASS')


if __name__ == '__main__':
    try:
        main()
    finally:
        _IMPORT_SANDBOX.cleanup()
