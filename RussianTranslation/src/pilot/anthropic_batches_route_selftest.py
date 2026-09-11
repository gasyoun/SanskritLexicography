#!/usr/bin/env python
"""Hermetic selftest for the H4531 Anthropic Message Batches transport.

No network, no credential, no spend: the provider triple is injected, so every contract
the money class depends on is asserted offline --

  B-01  one card per batch request; a multi-card manifest batch is refused (H2152)
  B-02  no prompt-cache breakpoint rides a batch request (H2674-H2756 closed NO-GO)
  B-03  the ledger ceiling is spent BEFORE the provider is called
  B-04  a ceiling below the request count refuses instead of submitting
  B-05  batch pricing is exactly half the standard Sonnet schedule
  B-06  errored / expired / canceled results seal with their own failure class and a
        NULL cost -- never a false zero
  B-07  retrieving a batch that has not ended is refused
  B-08  a sealed envelope is reused on re-retrieve; the reservation finalizes once
  B-09  resubmitting a different request set under one receipt is ambiguous_resume
"""
from __future__ import annotations

import copy
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import anthropic_batches_route as abr  # noqa: E402
from call_reservation import CallReservationLedger  # noqa: E402
from route_transport import (  # noqa: E402
    ANTHROPIC_BATCHES_ROUTE,
    TransportRefusal,
    build_request,
    candidate_pass,
    read_json,
    verify_envelope,
)
from usage_accounting import (  # noqa: E402
    API_BATCH,
    API_STANDARD,
    SONNET_STANDARD_PER_MTOK_USD,
    equivalent_usd,
)


FAILURES = []
SENSE = {'type': 'object', 'additionalProperties': False,
         'required': ['german', 'russian'],
         'properties': {'german': {'type': 'string'},
                        'russian': {'type': 'string'}}}
SCHEMA = {
    'type': 'object', 'additionalProperties': False, 'required': ['cards'],
    'properties': {'cards': {'type': 'array', 'items': {
        'type': 'object', 'additionalProperties': False,
        'required': ['key1', 'records'],
        'properties': {
            'key1': {'type': 'string'},
            'records': {'type': 'array', 'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['senses'],
                'properties': {'senses': {'type': 'array', 'items': SENSE}}}}}}}},
}
RESULT = {'cards': [{'key1': 'd_a', 'records': [{'senses': [
    {'german': 'geben', 'russian': 'давать'},
    {'german': 'schenken', 'russian': 'даровать'},
    {'german': 'reichen', 'russian': 'подавать'},
]}]}]}
USAGE = {'input_tokens': 4000, 'output_tokens': 1200,
         'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0}


def check(label, condition, detail=''):
    if condition:
        print('  ok   %s' % label)
    else:
        FAILURES.append('%s %s' % (label, detail))
        print('  FAIL %s %s' % (label, detail))


def requests_for(count, model=abr.MODEL):
    return [build_request(
        prompt='=== CARD d_a~~%02d ===\nein Wort' % index, output_schema=SCHEMA,
        requested_model=model, purpose='selftest:card%02d' % index,
        manifest_sha256='b' * 64, hard_timeout_ms=300000, max_output_tokens=4096)
        for index in range(count)]


def succeeded(custom_id, model=abr.MODEL, usage=None, result=None):
    return {'custom_id': custom_id, 'result': {'type': 'succeeded', 'message': {
        'model': model, 'usage': dict(usage or USAGE),
        'content': [{'type': 'tool_use', 'name': 'emit_cards',
                     'input': copy.deepcopy(result or RESULT)}]}}}


class FakeProvider:
    """Records what the provider was asked to do, and when."""

    def __init__(self, entries=None, status='ended'):
        self.payload = None
        self.submits = 0
        self.spent_at_submit = None
        self.status = status
        self.entries = entries
        self.ledger = None

    def triple(self):
        def submit(payload):
            self.payload = payload
            self.submits += 1
            self.spent_at_submit = self.ledger.spent() if self.ledger else None
            return {'id': 'msgbatch_selftest', 'created_at': '2026-09-11T00:00:00Z',
                    'processing_status': 'in_progress'}

        def poll(batch_id):
            return {'id': batch_id, 'processing_status': self.status,
                    'request_counts': {'succeeded': len(self.entries or [])},
                    'ended_at': '2026-09-11T00:05:00Z'}

        def results(batch_id):
            return list(self.entries or [])

        return {'submit': submit, 'poll': poll, 'results': results}


def run_one(tmp, requests, entries, max_calls=None, status='ended', run_id='r1'):
    provider = FakeProvider(entries=entries, status=status)
    ledger = CallReservationLedger(
        os.path.join(tmp, '%s.ledger.json' % run_id), run_id,
        max_calls=len(requests) if max_calls is None else max_calls)
    provider.ledger = ledger
    call = abr.AnthropicBatchesCall(ledger, provider.triple())
    return call, ledger, provider


def test_shape(tmp):
    print('B-01/B-02 request shape')
    requests = requests_for(3)
    payload = abr.build_batch(requests)
    check('B-01 one payload entry per request', len(payload) == 3)
    check('B-01 custom_ids unique',
          len({entry['custom_id'] for entry in payload}) == 3)
    params = payload[0]['params']
    check('B-01 exactly one user message', len(params['messages']) == 1)
    check('B-01 exactly one text block', len(params['messages'][0]['content']) == 1)
    check('B-02 no cache_control on a batch request',
          'cache_control' not in params['messages'][0]['content'][0])
    check('B-01 forced emit_cards tool',
          params['tool_choice'] == {'type': 'tool', 'name': 'emit_cards'})
    mixed = requests_for(1) + requests_for(1, model='claude-opus-5')
    try:
        abr.build_batch(mixed)
        check('B-01 mixed models refused', False, '(no refusal)')
    except TransportRefusal:
        check('B-01 mixed models refused', True)


def test_h2152(tmp):
    print('B-01 H2152 multi-card manifest batch')
    import h4531_batches_probe as probe
    manifest = {'schema': 'pwg.headless_execution_manifest.v1',
                'batches': [['k1', 'k2']], 'output_schema': SCHEMA,
                'prompt': {'preamble': 'p', 'translation': 't'},
                'inputs': {'k1': {}, 'k2': {}}}
    path = os.path.join(tmp, 'multi.manifest.json')
    from route_transport import atomic_json
    atomic_json(path, manifest)
    try:
        probe.build_requests(path)
        check('B-01 N-cards-in-one-request refused', False, '(no refusal)')
    except TransportRefusal as exc:
        check('B-01 N-cards-in-one-request refused', 'H2152' in str(exc), str(exc)[:80])


def test_reserve_before_submit(tmp):
    print('B-03/B-04 ceiling before the provider call')
    requests = requests_for(4)
    call, ledger, provider = run_one(tmp, requests, [], run_id='reserve')
    call.submit(requests, os.path.join(tmp, 'reserve.receipt.json'))
    check('B-03 all 4 reservations spent before submit', provider.spent_at_submit == 4,
          'spent_at_submit=%r' % provider.spent_at_submit)
    check('B-03 provider called exactly once', provider.submits == 1)

    tight, _, tight_provider = run_one(tmp, requests, [], max_calls=2, run_id='tight')
    try:
        tight.submit(requests, os.path.join(tmp, 'tight.receipt.json'))
        check('B-04 ceiling below request count refuses', False, '(no refusal)')
    except TransportRefusal:
        check('B-04 ceiling below request count refuses', tight_provider.submits == 0)


def test_pricing(tmp):
    print('B-05 batch pricing is half the standard Sonnet schedule')
    tokens = {'input_tokens': 1_000_000, 'output_tokens': 1_000_000,
              'cache_creation_tokens': 0, 'cache_read_tokens': 0}
    standard = equivalent_usd(tokens, API_STANDARD, SONNET_STANDARD_PER_MTOK_USD)
    batch = equivalent_usd(tokens, API_BATCH, SONNET_STANDARD_PER_MTOK_USD)
    check('B-05 standard = 3 + 15 USD/MTok', abs(standard - 18.0) < 1e-9, standard)
    check('B-05 batch = exactly half', abs(batch - standard / 2) < 1e-9, batch)
    telemetry = abr.normalize_usage(USAGE)
    expected = equivalent_usd(
        {'input_tokens': 4000, 'output_tokens': 1200, 'cache_creation_tokens': 0,
         'cache_read_tokens': 0}, API_BATCH, SONNET_STANDARD_PER_MTOK_USD)
    check('B-05 envelope cost uses the batch schedule',
          abs(telemetry['observed_cost_usd'] - expected) < 1e-9,
          '%r vs %r' % (telemetry['observed_cost_usd'], expected))
    check('B-05 absent usage is unevaluable, not zero',
          abr.normalize_usage({'input_tokens': 1}) is None)


def test_success_and_failures(tmp):
    print('B-05/B-06/B-08 sealing')
    requests = requests_for(4)
    payload = abr.build_batch(requests)
    ids = [entry['custom_id'] for entry in payload]
    entries = [
        succeeded(ids[0]),
        {'custom_id': ids[1], 'result': {'type': 'errored', 'error': {
            'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'slow down'}}}},
        {'custom_id': ids[2], 'result': {'type': 'expired'}},
        {'custom_id': ids[3], 'result': {'type': 'canceled'}},
    ]
    call, ledger, provider = run_one(tmp, requests, entries, run_id='seal')
    receipt = call.submit(requests, os.path.join(tmp, 'seal.receipt.json'))
    out = os.path.join(tmp, 'seal-envelopes')
    os.makedirs(out, exist_ok=True)
    envelopes = call.retrieve(requests, receipt, out, wall_ms=300000)
    check('B-08 one envelope per request', len(envelopes) == 4)
    good = envelopes[0]
    check('B-08 route recorded as batches', good['route'] == ANTHROPIC_BATCHES_ROUTE)
    check('B-08 success passes every gate', candidate_pass(good),
          '%r %r' % (good['failure_class'], good['audit_reasons']))
    check('B-08 envelope is synthetic/non-promotable',
          good['provenance_class'] == 'synthetic_control' and good['promotable'] is False)
    check('B-06 rate_limit classified', envelopes[1]['failure_class'] == 'rate_limit',
          envelopes[1]['failure_class'])
    check('B-06 expired classified', envelopes[2]['failure_class'] == 'batch_expired',
          envelopes[2]['failure_class'])
    check('B-06 canceled classified', envelopes[3]['failure_class'] == 'batch_canceled',
          envelopes[3]['failure_class'])
    for index in (1, 2, 3):
        check('B-06 failed card cost is null not zero #%d' % index,
              envelopes[index]['observed_cost_usd'] is None
              and envelopes[index]['cost_evaluable'] is False)
    usage = ledger.usage()
    check('B-08 every reservation finalized once',
          usage['pending_calls'] == 0 and usage['finalized_calls'] >= 1, usage)
    again = call.retrieve(requests, receipt, out, wall_ms=300000)
    check('B-08 re-retrieve reuses the sealed envelopes',
          [e['envelope_sha256'] for e in again] == [e['envelope_sha256'] for e in envelopes])
    check('B-08 sealed envelope verifies from disk',
          verify_envelope(read_json(os.path.join(out, '%s.envelope.json' % ids[0]),
                                    'envelope'))['envelope_sha256'] == good['envelope_sha256'])


def test_not_ended(tmp):
    print('B-07 retrieve refuses a live batch')
    requests = requests_for(2)
    call, _, _ = run_one(tmp, requests, [], status='in_progress', run_id='live')
    receipt = call.submit(requests, os.path.join(tmp, 'live.receipt.json'))
    out = os.path.join(tmp, 'live-envelopes')
    os.makedirs(out, exist_ok=True)
    try:
        call.retrieve(requests, receipt, out)
        check('B-07 non-ended batch refused', False, '(no refusal)')
    except TransportRefusal as exc:
        check('B-07 non-ended batch refused', 'still' in str(exc), str(exc)[:80])


def test_ambiguous_resume(tmp):
    print('B-09 resume discipline')
    requests = requests_for(2)
    call, _, provider = run_one(tmp, requests, [], run_id='resume')
    path = os.path.join(tmp, 'resume.receipt.json')
    call.submit(requests, path)
    again = call.submit(requests, path)
    check('B-09 identical resubmit replays the receipt, not the batch',
          provider.submits == 1 and again['batch_id'] == 'msgbatch_selftest')
    try:
        call.submit(requests_for(3), path)
        check('B-09 different request set refused', False, '(no refusal)')
    except TransportRefusal as exc:
        check('B-09 different request set refused', 'ambiguous_resume' in str(exc),
              str(exc)[:80])


def main():
    with tempfile.TemporaryDirectory() as tmp:
        test_shape(tmp)
        test_h2152(tmp)
        test_reserve_before_submit(tmp)
        test_pricing(tmp)
        test_success_and_failures(tmp)
        test_not_ended(tmp)
        test_ambiguous_resume(tmp)
    if FAILURES:
        print('\nFAIL: %d assertion(s)' % len(FAILURES))
        for row in FAILURES:
            print('  - %s' % row)
        return 1
    print('\nPASS anthropic_batches_route_selftest')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
