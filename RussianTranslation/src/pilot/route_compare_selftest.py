#!/usr/bin/env python
"""Hermetic acceptance matrix for the PWG transport comparison."""
from __future__ import annotations

import json
import os
import sys
import tempfile

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import anthropic_messages_route as amr  # noqa: E402
import route_compare as rc  # noqa: E402
from call_reservation import CallReservationLedger  # noqa: E402
from gateway_route import validate_complete_schema  # noqa: E402
from route_transport import (  # noqa: E402
    ANTHROPIC_ROUTE, GATEWAY_ROUTE, TransportRefusal, atomic_json,
    canonical_hash, candidate_pass, verify_envelope,
)


FULL_USAGE = {
    'input_tokens': 1200,
    'output_tokens': 340,
    'cache_creation_input_tokens': 800,
    'cache_read_input_tokens': 0,
}


def message(result, model=rc.MODEL, usage=None):
    return {
        'model': model,
        'usage': FULL_USAGE if usage is None else usage,
        'content': [{'type': 'tool_use', 'name': 'emit_cards', 'input': result}],
    }


def request_pair():
    return rc.build_requests()


def ledger(tmp, run_id='route-selftest', max_calls=1):
    return CallReservationLedger(os.path.join(tmp, 'ledger.json'), run_id, max_calls)


def test_frozen_prompt_schema_model_identity():
    preflight = rc.offline_check(check_auth=False)
    assert preflight['offline_passed'], preflight
    assert preflight['gateway_anthropic_prompt_identical'] is True
    assert preflight['gateway_anthropic_schema_identical'] is True
    assert preflight['model'] == rc.MODEL
    assert preflight['canary_audit_passed'] is True
    t1, t2 = request_pair()
    assert rc.verify_preflight(preflight, t1, t2, require_auth=False)


def test_execute_requires_bound_preflight():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            rc.execute(out=tmp, run_id='missing-preflight', transport=lambda _: None)
            raise AssertionError('execute admitted a missing preflight')
        except TransportRefusal as exc:
            assert 'preflight' in str(exc), exc


def test_anthropic_success_and_pricing():
    _, request = request_pair()
    expected = rc.canary.prompt_derived_instance(request['prompt'])
    with tempfile.TemporaryDirectory() as tmp:
        book = ledger(tmp)
        path = os.path.join(tmp, 'envelope.json')
        env = amr.AnthropicMessagesCall(
            book, lambda req: message(expected)).invoke(request, path)
        assert candidate_pass(env), env
        assert env['route'] == ANTHROPIC_ROUTE
        expected_cost = (
            1200 * 5 + 340 * 25 + 800 * 10) / 1_000_000
        assert env['observed_cost_usd'] == round(expected_cost, 9), env
        assert env['usage']['pricing_basis'] == amr.PRICING_BASIS
        assert env['usage']['price_per_mtok_usd'] == amr.PRICE_PER_MTOK
        assert book.spent() == 1 and book.usage()['cost_evaluable'] is True


def _failure(request, transport, expected):
    with tempfile.TemporaryDirectory() as tmp:
        env = amr.AnthropicMessagesCall(ledger(tmp), transport).invoke(
            request, os.path.join(tmp, 'envelope.json'))
        assert env['failure_class'] == expected, env
        assert not candidate_pass(env), env
        return env


class HttpError(RuntimeError):
    def __init__(self, status):
        super().__init__('http %d' % status)
        self.status_code = status


def test_typed_transport_failures():
    _, request = request_pair()

    def raises(exc):
        def transport(_):
            raise exc
        return transport

    _failure(request, raises(HttpError(401)), 'authentication')
    _failure(request, raises(HttpError(429)), 'rate_limit')
    _failure(request, raises(ConnectionError('down')), 'connection')
    _failure(request, raises(TimeoutError('late')), 'timeout')


def test_model_malformed_usage_and_schema_fail_closed():
    _, request = request_pair()
    good = rc.canary.prompt_derived_instance(request['prompt'])
    _failure(request, lambda _: message(good, model='claude-sonnet-5'),
             'model_substitution')
    _failure(request, lambda _: {'model': rc.MODEL, 'usage': FULL_USAGE,
                                  'content': [{'type': 'text', 'text': '{}'}]},
             'malformed_output')
    _failure(request, lambda _: message(good, usage={}), 'unevaluable_cost')
    bad = json.loads(json.dumps(good, ensure_ascii=False))
    bad['cards'][0]['records'][0]['senses'].pop()
    _failure(request, lambda _: message(bad), 'schema_failure')


def test_reservation_exhaustion_and_ambiguous_resume():
    _, request = request_pair()
    good = rc.canary.prompt_derived_instance(request['prompt'])
    with tempfile.TemporaryDirectory() as tmp:
        zero = ledger(tmp, max_calls=0)
        try:
            amr.AnthropicMessagesCall(zero, lambda _: message(good)).invoke(
                request, os.path.join(tmp, 'zero.json'))
            raise AssertionError('zero ceiling admitted a call')
        except TransportRefusal as exc:
            assert 'reservation_exhausted' in str(exc), exc

        pending = ledger(tmp, run_id='pending', max_calls=1)
        key = canonical_hash({'route': ANTHROPIC_ROUTE, 'run_id': 'pending',
                              'request_sha256': request['request_sha256']})
        pending.reserve(request['purpose'], profile=request['requested_model'],
                        detail=ANTHROPIC_ROUTE, idempotency_key=key)
        calls = {'n': 0}

        def should_not_run(_):
            calls['n'] += 1
            return message(good)

        try:
            amr.AnthropicMessagesCall(pending, should_not_run).invoke(
                request, os.path.join(tmp, 'missing.json'))
            raise AssertionError('ambiguous pending call was replayed')
        except TransportRefusal as exc:
            assert 'ambiguous_resume' in str(exc), exc
        assert calls['n'] == 0


def test_exact_once_replay_and_post_write_recovery():
    _, request = request_pair()
    good = rc.canary.prompt_derived_instance(request['prompt'])
    with tempfile.TemporaryDirectory() as tmp:
        calls = {'n': 0}

        def transport(_):
            calls['n'] += 1
            return message(good)

        book = ledger(tmp, max_calls=1)
        path = os.path.join(tmp, 'envelope.json')
        first = amr.AnthropicMessagesCall(book, transport).invoke(request, path)
        second = amr.AnthropicMessagesCall(book, transport).invoke(request, path)
        assert first == second and calls['n'] == 1 and book.spent() == 1

    class FailFinalize(CallReservationLedger):
        def finalize(self, reservation, telemetry, evidence=None):
            raise RuntimeError('synthetic crash after envelope write')

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'envelope.json')
        broken = FailFinalize(os.path.join(tmp, 'ledger.json'), 'recover', 1)
        try:
            amr.AnthropicMessagesCall(broken, transport).invoke(request, path)
            raise AssertionError('fault did not fire')
        except RuntimeError as exc:
            assert 'synthetic crash' in str(exc)
        assert os.path.isfile(path)
        recovered = CallReservationLedger.open_existing(
            os.path.join(tmp, 'ledger.json'), 'recover')
        before = calls['n']
        env = amr.AnthropicMessagesCall(recovered, transport).invoke(request, path)
        assert verify_envelope(env) and calls['n'] == before
        assert recovered.usage()['pending_calls'] == 0


def fake_gateway_source(ticket, request, result, cost=0.05,
                        schema_compliant=True, model=rc.MODEL):
    value = {
        'schema': rc.gex.ENVELOPE_SCHEMA,
        'route': GATEWAY_ROUTE,
        'requested_model': request['requested_model'],
        'attested_model': model,
        'model_matches_request': model == request['requested_model'],
        'model_attested': True,
        'dispatch_attested': True,
        'attestation_scope': 'dispatch',
        'dispatch_id': 'toolu_selftest12345678',
        'run_id': ticket['run_id'],
        'reservation_id': ticket['reservation_id'],
        'reservation_ordinal': ticket['reservation_ordinal'],
        'request_sha256': canonical_hash({'prompt': request['prompt']}),
        'schema_sha256': request['output_schema_sha256'],
        'schema_compliant': schema_compliant,
        'failure_class': None if schema_compliant else 'malformed_output',
        'error': None if schema_compliant else 'bad result',
        'result': result,
        'wall_ms': 100,
        'attested_usage_totals': FULL_USAGE,
        'ledger_telemetry': {},
        'cost_evaluable': cost is not None,
        'observed_cost_usd': cost,
        'promotable': False,
    }
    value['saved_envelope_sha256'] = canonical_hash(value)
    return value


def _fake_prepare(p, prefix, run_id, request):
    book = CallReservationLedger(p['ledger'], run_id, rc.MAX_CALLS)
    key = canonical_hash({'prefix': prefix, 'request': request['request_sha256']})
    existing = next((row for row in book.snapshot()['reservations']
                     if row.get('idempotency_key') == key), None)
    reservation = existing or book.reserve(
        request['purpose'], profile=request['requested_model'], detail='fake-gateway',
        idempotency_key=key)
    ticket = {
        'run_id': run_id,
        'reservation_id': reservation['reservation_id'],
        'reservation_ordinal': reservation['ordinal'],
        'max_output_tokens': request['max_output_tokens'],
    }
    atomic_json(p['%s_ticket' % prefix], ticket)
    return ticket


def test_full_state_machine_and_selection():
    original_prepare = rc._prepare_gateway
    original_record = rc._record_gateway_if_ready
    t1, t2 = request_pair()
    capability = {
        'protocol_marker': {'name': 'router.cheap.canary', 'version': 'v1'},
        'language_sample': {'lang': 'ru', 'text': 'слово'},
    }
    canary_result = rc.canary.prompt_derived_instance(t2['prompt'])
    try:
        rc._prepare_gateway = _fake_prepare

        def fake_record(p, prefix, run_id):
            request = t1 if prefix == 't1' else t2
            result = capability if prefix == 't1' else canary_result
            ticket = rc.read_json(p['%s_ticket' % prefix])
            assert ticket['max_output_tokens'] == request['max_output_tokens']
            source = fake_gateway_source(ticket, request, result)
            # The fake bridge finalizes the same reservation once.
            book = CallReservationLedger.open_existing(p['ledger'], run_id)
            reservation = next(row for row in book.snapshot()['reservations']
                               if row['reservation_id'] == ticket['reservation_id'])
            if not reservation.get('finalized'):
                telemetry = amr.normalize_usage(FULL_USAGE)
                telemetry['observed_cost_usd'] = 0.05
                book.finalize(reservation, telemetry)
            return source

        rc._record_gateway_if_ready = fake_record
        with tempfile.TemporaryDirectory() as tmp:
            result = rc.execute(
                out=tmp, run_id='full-success',
                transport=lambda _: message(canary_result),
                preflight=rc.offline_check(check_auth=False))
            assert result['verdict'] == 'GO', result
            assert result['candidate_route'] == ANTHROPIC_ROUTE, result
            assert result['selection_reason'] == 'wall time differs by more than 10%'
            assert len(result['calls']) == 3
            book = CallReservationLedger.open_existing(
                os.path.join(tmp, 'call_reservation.json'), 'full-success')
            assert book.spent() == 3 and book.usage()['pending_calls'] == 0
            assert result['production_default_changed'] is False
            assert result['cli_fallback_preserved'] is True
            assert rc.verify_receipt(result)
            assert len(result['evidence']) == len(result['calls']) == 3

            transport_schema = rc.read_json(os.path.join(
                REPO, 'schemas', 'pwg_transport_envelope.schema.json'))
            for row in result['calls']:
                validate_complete_schema(row, transport_schema)
            receipt_schema = rc.read_json(os.path.join(
                REPO, 'schemas', 'pwg_route_comparison.schema.json'))
            registry = Registry().with_resource(
                transport_schema['$id'], Resource.from_contents(transport_schema))
            Draft202012Validator.check_schema(receipt_schema)
            Draft202012Validator(receipt_schema, registry=registry).validate(result)
    finally:
        rc._prepare_gateway = original_prepare
        rc._record_gateway_if_ready = original_record


def test_gateway_unknown_cost_preserves_usage_and_allows_call_three():
    original_prepare = rc._prepare_gateway
    original_record = rc._record_gateway_if_ready
    t1, t2 = request_pair()
    capability = {
        'protocol_marker': {'name': 'router.cheap.canary', 'version': 'v1'},
        'language_sample': {'lang': 'ru', 'text': 'слово'},
    }
    canary_result = rc.canary.prompt_derived_instance(t2['prompt'])
    calls = {'api': 0}
    try:
        rc._prepare_gateway = _fake_prepare

        def fake_record(p, prefix, run_id):
            request = t1 if prefix == 't1' else t2
            result = capability if prefix == 't1' else canary_result
            ticket = rc.read_json(p['%s_ticket' % prefix])
            source = fake_gateway_source(ticket, request, result, cost=None)
            book = CallReservationLedger.open_existing(p['ledger'], run_id)
            reservation = next(row for row in book.snapshot()['reservations']
                               if row['reservation_id'] == ticket['reservation_id'])
            if not reservation.get('finalized'):
                telemetry = amr.normalize_usage(FULL_USAGE)
                telemetry['cost_evaluable'] = False
                telemetry['observed_cost_usd'] = 0
                book.finalize(reservation, telemetry)
            return source

        rc._record_gateway_if_ready = fake_record
        with tempfile.TemporaryDirectory() as tmp:
            def api(_):
                calls['api'] += 1
                return message(canary_result)
            result = rc.execute(
                out=tmp, run_id='unknown-cost', transport=api,
                preflight=rc.offline_check(check_auth=False))
            assert result['verdict'] == 'GO', result
            assert result['calls'][0]['failure_class'] is None
            assert result['calls'][0]['accounting']['usage_evaluable'] is True
            assert result['calls'][0]['accounting']['observed_cash_usd'] is None
            assert calls['api'] == 1
            book = CallReservationLedger.open_existing(
                os.path.join(tmp, 'call_reservation.json'), 'unknown-cost')
            assert book.spent() == 3
    finally:
        rc._prepare_gateway = original_prepare
        rc._record_gateway_if_ready = original_record


def test_priced_gateway_content_failure_can_be_compared():
    original_prepare = rc._prepare_gateway
    original_record = rc._record_gateway_if_ready
    t1, t2 = request_pair()
    capability = {
        'protocol_marker': {'name': 'router.cheap.canary', 'version': 'v1'},
        'language_sample': {'lang': 'ru', 'text': 'слово'},
    }
    canary_result = rc.canary.prompt_derived_instance(t2['prompt'])
    try:
        rc._prepare_gateway = _fake_prepare

        def fake_record(p, prefix, run_id):
            request = t1 if prefix == 't1' else t2
            result = capability if prefix == 't1' else None
            ticket = rc.read_json(p['%s_ticket' % prefix])
            source = fake_gateway_source(
                ticket, request, result, cost=0.05,
                schema_compliant=(prefix == 't1'))
            book = CallReservationLedger.open_existing(p['ledger'], run_id)
            reservation = next(row for row in book.snapshot()['reservations']
                               if row['reservation_id'] == ticket['reservation_id'])
            if not reservation.get('finalized'):
                telemetry = amr.normalize_usage(FULL_USAGE)
                telemetry['observed_cost_usd'] = 0.05
                book.finalize(reservation, telemetry)
            return source

        rc._record_gateway_if_ready = fake_record
        with tempfile.TemporaryDirectory() as tmp:
            result = rc.execute(
                out=tmp, run_id='priced-content-failure',
                transport=lambda _: message(canary_result),
                preflight=rc.offline_check(check_auth=False))
            assert result['verdict'] == 'GO', result
            assert result['candidate_route'] == ANTHROPIC_ROUTE
            assert result['calls'][1]['failure_class'] == 'schema_failure'
            assert len(result['calls']) == 3
    finally:
        rc._prepare_gateway = original_prepare
        rc._record_gateway_if_ready = original_record


TESTS = [
    test_frozen_prompt_schema_model_identity,
    test_execute_requires_bound_preflight,
    test_anthropic_success_and_pricing,
    test_typed_transport_failures,
    test_model_malformed_usage_and_schema_fail_closed,
    test_reservation_exhaustion_and_ambiguous_resume,
    test_exact_once_replay_and_post_write_recovery,
    test_full_state_machine_and_selection,
    test_gateway_unknown_cost_preserves_usage_and_allows_call_three,
    test_priced_gateway_content_failure_can_be_compared,
]


def selftest():
    for test in TESTS:
        test()
        print('  PASS: %s' % test.__name__)
    print('route_compare_selftest: PASS (%d/%d groups)' % (len(TESTS), len(TESTS)))
    return True


if __name__ == '__main__':
    sys.exit(0 if selftest() else 1)
