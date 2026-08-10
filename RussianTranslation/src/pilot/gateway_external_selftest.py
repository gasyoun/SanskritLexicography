#!/usr/bin/env python
"""Hermetic acceptance matrix for the durable router.cheap Agent bridge.

No transport is invoked here.  Tests stop at immutable request tickets or feed
saved public response wrappers into the recorder.  Every path is temporary and
offline.
"""

import concurrent.futures
import copy
import hashlib
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(REPO, 'src')):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import gateway_external as ext  # noqa: E402
from call_reservation import CallReservationLedger  # noqa: E402


MODEL = 'claude-opus-5'
PURPOSE = 'h2533:synthetic-capability'
RESULT = {
    'ok': True,
    'cards': [{
        'key': 'dq_canary_puregloss~~h0_zz_pw',
        'senses': ['первый', 'второй', 'третий'],
    }],
}
SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'type': 'object',
    'required': ['ok', 'cards'],
    'additionalProperties': False,
    'properties': {
        'ok': {'const': True},
        'cards': {
            'type': 'array',
            'minItems': 1,
            'maxItems': 1,
            'items': {
                'type': 'object',
                'required': ['key', 'senses'],
                'additionalProperties': False,
                'properties': {
                    'key': {'const': 'dq_canary_puregloss~~h0_zz_pw'},
                    'senses': {
                        'type': 'array',
                        'minItems': 3,
                        'maxItems': 3,
                        'items': {'type': 'string', 'minLength': 1},
                    },
                },
            },
        },
    },
}


class ExpectedCrash(RuntimeError):
    pass


def write_json(path, value):
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')


def sha(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def fixture(tmp, run_id='h2533-test', max_calls=2, purpose=PURPOSE,
            ticket_name='ticket.json'):
    request_path = os.path.join(tmp, 'request.json')
    schema_path = os.path.join(tmp, 'schema.json')
    ledger_path = os.path.join(tmp, 'calls.json')
    ticket_path = os.path.join(tmp, ticket_name)
    envelope_path = os.path.join(tmp, ticket_name + '.envelope.json')
    response_path = os.path.join(tmp, ticket_name + '.response.json')
    write_json(request_path, {'prompt': 'Return the exact synthetic fixture.', 'tools': []})
    write_json(schema_path, SCHEMA)
    return {
        'run_id': run_id,
        'max_calls': max_calls,
        'purpose': purpose,
        'request_path': request_path,
        'schema_path': schema_path,
        'ledger_path': ledger_path,
        'ticket_path': ticket_path,
        'envelope_path': envelope_path,
        'response_path': response_path,
    }


def prepare(paths, fault=None, **overrides):
    values = {
        'ledger_path': paths['ledger_path'],
        'run_id': paths['run_id'],
        'max_calls': paths['max_calls'],
        'purpose': paths['purpose'],
        'requested_model': MODEL,
        'request_path': paths['request_path'],
        'schema_path': paths['schema_path'],
        'ticket_path': paths['ticket_path'],
        'route': ext.ROUTE,
        'provenance': ext.SYNTHETIC_PROVENANCE,
        'timeout_ms': 600_000,
        'waiver_id': ext.OWNER_WAIVER_ID,
        'fault': fault,
    }
    values.update(overrides)
    return ext.prepare_external(**values)


def wrapper(ticket, result=RESULT, usage=None, blocks=None):
    if blocks is None:
        blocks = [
            {'type': 'thinking', 'thinking': 'must never enter the envelope'},
            {'type': 'text', 'text': json.dumps(result, ensure_ascii=False,
                                                sort_keys=True, separators=(',', ':'))},
        ]
    value = {
        'schema': ext.RESPONSE_SCHEMA,
        'run_id': ticket['run_id'],
        'reservation_id': ticket['reservation_id'],
        'route': ticket['route'],
        'requested_model': ticket['requested_model'],
        'returned_model': ticket['requested_model'],
        'purpose': ticket['purpose'],
        'nonce': ticket['nonce'],
        'started_at': '2026-08-10T02:00:00.000Z',
        'ended_at': '2026-08-10T02:00:01.250Z',
        'wall_ms': 1250,
        'content': blocks,
    }
    if usage is not None:
        value['usage'] = usage
    return value


def record(paths, ticket, response=None, fault=None, **overrides):
    if response is not None:
        write_json(paths['response_path'], response)
    values = {
        'ticket_path': paths['ticket_path'],
        'ledger_path': paths['ledger_path'],
        'run_id': paths['run_id'],
        'response_path': paths['response_path'],
        'schema_path': paths['schema_path'],
        'envelope_path': paths['envelope_path'],
        'fault': fault,
    }
    values.update(overrides)
    return ext.record_external(**values)


def crash_at(phase):
    def inject(actual):
        if actual == phase:
            raise ExpectedCrash(phase)
    return inject


def expect_refusal(fn, needle=None):
    try:
        fn()
    except ext.ExternalRefusal as exc:
        if needle is not None:
            assert needle in str(exc), (needle, str(exc))
        return str(exc)
    raise AssertionError('expected ExternalRefusal')


def test_prepare_contract_and_zero_one_n():
    with tempfile.TemporaryDirectory() as tmp:
        zero = fixture(tmp, run_id='zero', max_calls=0, ticket_name='zero.json')
        expect_refusal(lambda: prepare(zero), 'max_calls')
        assert not os.path.exists(zero['ticket_path'])
        assert CallReservationLedger(zero['ledger_path'], 'zero', 0).spent() == 0

        one = fixture(tmp, run_id='one', max_calls=1, ticket_name='one.json')
        first = prepare(one)
        second = prepare(one)
        assert first == second
        assert CallReservationLedger(one['ledger_path'], 'one', 1).spent() == 1

        many = fixture(tmp, run_id='many', max_calls=3, ticket_name='many1.json')
        prepare(many)
        for index in (2, 3):
            other = dict(many, purpose=PURPOSE + str(index),
                         ticket_path=os.path.join(tmp, 'many%d.json' % index))
            prepare(other)
        blocked = dict(many, purpose='fourth', ticket_path=os.path.join(tmp, 'many4.json'))
        expect_refusal(lambda: prepare(blocked), 'max_calls')
        assert CallReservationLedger(many['ledger_path'], 'many', 3).spent() == 3

        for field, bad in (
                ('route', 'c4'), ('provenance', 'real'), ('waiver_id', 'wrong'),
                ('timeout_ms', 600_001), ('requested_model', ''), ('purpose', '')):
            bad_paths = fixture(tmp, run_id='bad-' + field, max_calls=1,
                                ticket_name='bad-' + field + '.json')
            expect_refusal(lambda f=field, v=bad, p=bad_paths:
                           prepare(p, **{f: v}))
            if os.path.exists(bad_paths['ledger_path']):
                assert CallReservationLedger(
                    bad_paths['ledger_path'], bad_paths['run_id'], 1).spent() == 0


def test_competing_prepares_are_atomic():
    with tempfile.TemporaryDirectory() as tmp:
        same = fixture(tmp, run_id='same', max_calls=1)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: prepare(same), range(2)))
        assert outcomes[0] == outcomes[1]
        assert CallReservationLedger(same['ledger_path'], 'same', 1).spent() == 1

        race = fixture(tmp, run_id='race', max_calls=1, ticket_name='race-a.json')
        other = dict(race, purpose='different', ticket_path=os.path.join(tmp, 'race-b.json'))
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(prepare, value) for value in (race, other)]
        successes = 0
        refusals = 0
        for future in futures:
            try:
                future.result()
                successes += 1
            except ext.ExternalRefusal:
                refusals += 1
        assert (successes, refusals) == (1, 1)
        assert CallReservationLedger(race['ledger_path'], 'race', 1).spent() == 1


def test_prepare_fault_recovery_and_read_only_report():
    phases = ('after_reservation', 'during_ticket_temp_write',
              'after_ticket_replacement')
    for phase in phases:
        with tempfile.TemporaryDirectory() as tmp:
            paths = fixture(tmp, run_id='prep-' + phase, max_calls=1)
            try:
                prepare(paths, fault=crash_at(phase))
            except ExpectedCrash:
                pass
            else:
                raise AssertionError('fault did not fire: ' + phase)
            before = sha(paths['ledger_path'])
            report = ext.recovery_report(paths['ledger_path'], paths['run_id'])
            assert sha(paths['ledger_path']) == before, 'recovery report mutated the ledger'
            assert report['calls_spent'] == 1 and report['pending_calls'] == 1
            if phase != 'after_ticket_replacement':
                assert report['ambiguous_reserved_without_ticket'] == 1, report
            ticket = prepare(paths)
            assert ticket['reservation_ordinal'] == 1
            assert CallReservationLedger(paths['ledger_path'], paths['run_id'], 1).spent() == 1
            assert prepare(paths) == ticket


def test_record_success_hashes_and_unknown_cost_waiver():
    with tempfile.TemporaryDirectory() as tmp:
        paths = fixture(tmp, max_calls=1)
        ticket = prepare(paths)
        env = record(paths, ticket, wrapper(ticket))
        assert env['schema'] == ext.ENVELOPE_SCHEMA
        assert env['schema_compliant'] is True and env['promotable'] is False
        assert env['cost_evaluable'] is False
        assert env['observed_cost_usd'] is None
        assert env['ledger_observed_cost_floor_usd'] == 0
        assert env['route'] == ext.ROUTE and env['provenance_class'] == ext.SYNTHETIC_PROVENANCE
        for name in ('ticket_sha256', 'request_sha256', 'schema_sha256',
                     'public_response_sha256', 'final_text_sha256',
                     'canonical_result_sha256', 'saved_envelope_sha256'):
            assert len(env[name]) == 64, (name, env.get(name))
        assert 'must never enter' not in json.dumps(env, ensure_ascii=False)
        snapshot = CallReservationLedger(paths['ledger_path'], paths['run_id'], 1).snapshot()
        item = snapshot['reservations'][0]
        assert item['finalized'] is True
        assert item['telemetry']['cost_evaluable'] is False
        assert item['finalization_evidence']['record_fingerprint_sha256']

        before = open(paths['envelope_path'], 'rb').read()
        again = record(paths, ticket)
        after = open(paths['envelope_path'], 'rb').read()
        assert again == env and after == before


def test_record_fault_recovery_is_byte_identical():
    phases = ('before_ledger_finalization', 'after_ledger_finalization',
              'during_envelope_temp_write', 'after_envelope_replacement')
    for phase in phases:
        with tempfile.TemporaryDirectory() as tmp:
            paths = fixture(tmp, run_id='record-' + phase, max_calls=1)
            ticket = prepare(paths)
            write_json(paths['response_path'], wrapper(ticket))
            try:
                record(paths, ticket, fault=crash_at(phase))
            except ExpectedCrash:
                pass
            else:
                raise AssertionError('fault did not fire: ' + phase)
            env = record(paths, ticket)
            first = open(paths['envelope_path'], 'rb').read()
            assert record(paths, ticket) == env
            assert open(paths['envelope_path'], 'rb').read() == first
            ledger = CallReservationLedger(paths['ledger_path'], paths['run_id'], 1)
            assert ledger.spent() == 1 and ledger.usage()['finalized_calls'] == 1


def test_provenance_substitution_refuses_without_finalizing():
    fields = ('run_id', 'reservation_id', 'route', 'requested_model',
              'returned_model', 'purpose', 'nonce')
    for field in fields:
        with tempfile.TemporaryDirectory() as tmp:
            paths = fixture(tmp, run_id='wrong-' + field, max_calls=1)
            ticket = prepare(paths)
            bad = wrapper(ticket)
            bad[field] = 'substituted'
            write_json(paths['response_path'], bad)
            expect_refusal(lambda: record(paths, ticket), field)
            usage = CallReservationLedger(paths['ledger_path'], paths['run_id'], 1).usage()
            assert usage['pending_calls'] == 1 and usage['finalized_calls'] == 0

    with tempfile.TemporaryDirectory() as tmp:
        paths = fixture(tmp, run_id='wrong-schema', max_calls=1)
        ticket = prepare(paths)
        changed = copy.deepcopy(SCHEMA)
        changed['properties']['ok'] = {'const': False}
        write_json(paths['schema_path'], changed)
        write_json(paths['response_path'], wrapper(ticket))
        expect_refusal(lambda: record(paths, ticket), 'schema')
        assert CallReservationLedger(paths['ledger_path'], paths['run_id'], 1).usage()[
            'pending_calls'] == 1


def test_missing_partial_divergent_response_and_timing():
    with tempfile.TemporaryDirectory() as tmp:
        paths = fixture(tmp, max_calls=1)
        ticket = prepare(paths)
        expect_refusal(lambda: record(paths, ticket), 'response')
        with open(paths['response_path'], 'w', encoding='utf-8') as handle:
            handle.write('{"partial":')
        expect_refusal(lambda: record(paths, ticket), 'response')
        assert CallReservationLedger(paths['ledger_path'], paths['run_id'], 1).usage()[
            'pending_calls'] == 1

    for mutation, needle in (
            ({'started_at': None}, 'started_at'),
            ({'ended_at': None}, 'ended_at'),
            ({'wall_ms': 600_001}, 'timeout'),
            ({'wall_ms': 2}, 'timestamp'),
            ({'started_at': 'not-a-time'}, 'started_at')):
        with tempfile.TemporaryDirectory() as tmp:
            paths = fixture(tmp, run_id='time-' + needle + str(len(mutation)), max_calls=1)
            ticket = prepare(paths)
            bad = wrapper(ticket)
            bad.update(mutation)
            env = record(paths, ticket, bad)
            assert env['schema_compliant'] is False
            assert needle in env['failure_class'] or needle in env['error']

    with tempfile.TemporaryDirectory() as tmp:
        paths = fixture(tmp, run_id='divergent', max_calls=1)
        ticket = prepare(paths)
        record(paths, ticket, wrapper(ticket))
        changed = wrapper(ticket, result=dict(RESULT, ok=False))
        write_json(paths['response_path'], changed)
        expect_refusal(lambda: record(paths, ticket), 'different response')
        assert CallReservationLedger(paths['ledger_path'], paths['run_id'], 1).usage()[
            'finalized_calls'] == 1


def test_final_blocks_and_complete_json_schema():
    failures = [
        [],
        [{'type': 'thinking', 'thinking': json.dumps(RESULT)}],
        [{'type': 'text', 'text': 'not json'}],
        [{'type': 'text', 'text': json.dumps({'ok': True, 'cards': 'wrong'})}],
        [{'type': 'text', 'text': json.dumps({'ok': True, 'cards': []})}],
        [{'type': 'text', 'text': json.dumps({
            'ok': True, 'cards': [{'key': 'wrong', 'senses': ['a', 'b', 'c']}]})}],
        [{'type': 'text', 'text': json.dumps({
            'ok': True, 'cards': [{'key': RESULT['cards'][0]['key'],
                                   'senses': ['a', 'b', 'c'], 'extra': 1}]})}],
        [{'type': 'text', 'text': json.dumps(dict(RESULT, extra=True))}],
    ]
    for index, blocks in enumerate(failures):
        with tempfile.TemporaryDirectory() as tmp:
            paths = fixture(tmp, run_id='schema-%d' % index, max_calls=1)
            ticket = prepare(paths)
            env = record(paths, ticket, wrapper(ticket, blocks=blocks))
            assert env['schema_compliant'] is False, (index, env)
            assert env['promotable'] is False

    with tempfile.TemporaryDirectory() as tmp:
        paths = fixture(tmp, run_id='thinking-plus-final', max_calls=1)
        ticket = prepare(paths)
        env = record(paths, ticket, wrapper(ticket))
        assert env['schema_compliant'] is True
        assert env['result'] == RESULT


def test_waiver_is_exact_and_synthetic_never_promotes():
    assert ext.cost_policy(ext.ROUTE, ext.OWNER_WAIVER_ID, None) == {
        'cost_evaluable': False,
        'observed_cost_usd': None,
        'waiver_applied': True,
    }
    for route, waiver in ((ext.ROUTE, None), ('c4', ext.OWNER_WAIVER_ID),
                          ('claude-cli-headless', ext.OWNER_WAIVER_ID)):
        expect_refusal(lambda r=route, w=waiver: ext.cost_policy(r, w, None), 'usage')

    with tempfile.TemporaryDirectory() as tmp:
        paths = fixture(tmp, max_calls=1)
        ticket = prepare(paths)
        env = record(paths, ticket, wrapper(ticket))
        expect_refusal(lambda: ext.assert_not_promotable(env), 'non-promotable')
        assert env['route'] != 'claude-cli-headless'
        assert env['provenance_class'] == 'synthetic_control'


TESTS = [
    test_prepare_contract_and_zero_one_n,
    test_competing_prepares_are_atomic,
    test_prepare_fault_recovery_and_read_only_report,
    test_record_success_hashes_and_unknown_cost_waiver,
    test_record_fault_recovery_is_byte_identical,
    test_provenance_substitution_refuses_without_finalizing,
    test_missing_partial_divergent_response_and_timing,
    test_final_blocks_and_complete_json_schema,
    test_waiver_is_exact_and_synthetic_never_promotes,
]


def selftest():
    failed = []
    for test in TESTS:
        try:
            test()
            print('  PASS: ' + test.__name__)
        except BaseException as exc:  # noqa: BLE001 - aggregate the entire matrix
            failed.append(test.__name__)
            print('  FAIL: %s -- %s: %s' % (
                test.__name__, exc.__class__.__name__, exc))
    if failed:
        print('gateway_external_selftest: FAILED (%d/%d): %s' % (
            len(failed), len(TESTS), ', '.join(failed)))
        return False
    print('gateway_external_selftest: PASS (%d/%d groups)' % (len(TESTS), len(TESTS)))
    return True


if __name__ == '__main__':
    sys.exit(0 if selftest() else 1)
