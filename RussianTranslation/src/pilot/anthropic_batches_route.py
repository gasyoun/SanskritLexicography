#!/usr/bin/env python
"""Ledger-backed Anthropic **Message Batches** transport for PWG qualification (H4531).

The blind spot this closes: the H1403 speed audit ledger #8 / action A8 named the async
Batches API -- latency-immune by design, 50 % pricing -- and nothing in this repo had
ever probed it, while PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md proved the
synchronous home route is jitter-dominated (8.9 -> 59.2 s, a third over ceiling).

Contract, deliberately the SAME one ``anthropic_messages_route`` obeys:

* one card per **batch request** (the H4054 shape). N cards inside ONE request is the
  H2152-rejected shape and this module refuses it structurally -- it only ever accepts
  a list of already-built single-card ``pwg.transport_request.v1`` objects.
* one ``pwg.call_reservation.v1`` reservation per request, taken BEFORE the submit, so
  the hard ceiling is spent-or-refused before a single token is billable.
* one sealed ``pwg.transport_envelope.v1`` per request on retrieval, synthetic and
  non-promotable, so ``audit_window.py`` and the promote gates consume the output
  unchanged and nothing can promote out of a probe.
* no prompt-cache breakpoint. The H2674-H2756 cache chain closed NO-GO "must not be
  rerun"; a batch request here carries plain text blocks only.

The credential is read by ``anthropic_messages_route._read_secret`` (env first, then the
prepared secrets file) and never enters argv, a log line or an artifact.
"""
from __future__ import annotations

import os
import time

import anthropic_messages_route as amr
from call_reservation import (
    CallLimitReached,
    CallReservationLedger,
    normalize_telemetry,
    unevaluable_telemetry,
)
from route_transport import (
    ANTHROPIC_BATCHES_ROUTE,
    TransportRefusal,
    atomic_json,
    audit_canary,
    canonical_hash,
    read_json,
    seal_envelope,
    verify_envelope,
    verify_request,
)
from usage_accounting import (
    API_BATCH,
    SONNET_POLICY,
    SONNET_STANDARD_PER_MTOK_USD,
    build as build_accounting,
    legacy_telemetry,
)


#: The production PWG lane model; the comparison arm must be the same one.
MODEL = 'claude-sonnet-5'
PRICING_BASIS = 'anthropic-batch-50pct-sonnet-5-list-2026-09-10.v1'
#: Batch-level processing statuses. ``ended`` is the only one that yields results.
BATCH_ENDED = 'ended'
MAX_CUSTOM_ID = 64
#: Provider error names mapped onto the frozen FAILURE_CLASSES vocabulary.
ERROR_CLASSES = {
    'authentication_error': 'authentication',
    'permission_error': 'authentication',
    'rate_limit_error': 'rate_limit',
    'overloaded_error': 'rate_limit',
    'timeout_error': 'timeout',
    'invalid_request_error': 'transport_error',
    'api_error': 'transport_error',
}


def _nonnegative_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def normalize_usage(raw):
    """Return priced ledger telemetry at the 50 % batch schedule, or ``None``.

    ``None`` means *unevaluable*, never zero: a missing usage block must not be able to
    report a free call (the ``cost_evaluable`` semantics the money class turns on).
    """
    if not isinstance(raw, dict):
        return None
    source = {
        'input_tokens': raw.get('input_tokens'),
        'output_tokens': raw.get('output_tokens'),
        'cache_creation_tokens': raw.get('cache_creation_input_tokens') or 0,
        'cache_read_tokens': raw.get('cache_read_input_tokens') or 0,
    }
    if not all(_nonnegative_int(value) for value in source.values()):
        return None
    accounting = build_accounting(
        source, billing_mode=API_BATCH, pricing_policy=SONNET_POLICY,
        rate_card=SONNET_STANDARD_PER_MTOK_USD)
    return normalize_telemetry(legacy_telemetry(accounting))


def custom_id_for(ordinal, request):
    """Stable, provider-legal per-request id that leaks no card text."""
    value = 'r%04d-%s' % (int(ordinal), request['request_sha256'][:24])
    if len(value) > MAX_CUSTOM_ID:  # pragma: no cover - arithmetic guarantee
        raise TransportRefusal('custom_id exceeds %d characters' % MAX_CUSTOM_ID)
    return value


def batch_request_params(request):
    """One card, one batch request -- the H4054 shape, no cache breakpoint."""
    verify_request(request)
    return {
        'model': request['requested_model'],
        'max_tokens': request['max_output_tokens'],
        'messages': [{
            'role': 'user',
            'content': [{'type': 'text', 'text': request['prompt']}],
        }],
        'tools': [{
            'name': 'emit_cards',
            'description': 'Return the frozen PWG qualification result.',
            'input_schema': request['output_schema'],
        }],
        'tool_choice': {'type': 'tool', 'name': 'emit_cards'},
    }


def build_batch(requests):
    """Build the provider payload, refusing any multi-model or duplicate shape."""
    if not isinstance(requests, (list, tuple)) or not requests:
        raise TransportRefusal('batches transport needs a non-empty request list')
    payload = []
    seen = set()
    for ordinal, request in enumerate(requests, start=1):
        if request['requested_model'] != requests[0]['requested_model']:
            raise TransportRefusal('one batch must carry exactly one requested model')
        custom_id = custom_id_for(ordinal, request)
        if custom_id in seen:
            raise TransportRefusal('duplicate custom_id %r in one batch' % custom_id)
        seen.add(custom_id)
        payload.append({'custom_id': custom_id, 'params': batch_request_params(request)})
    return payload


def sdk_transport(client):
    """Live submit/poll/retrieve triple. The credential never enters an artifact."""
    if client is None:
        raise TransportRefusal('Batches transport has no authenticated client')

    def submit(payload):
        return client.messages.batches.create(requests=payload).model_dump()

    def poll(batch_id):
        return client.messages.batches.retrieve(batch_id).model_dump()

    def results(batch_id):
        return [entry.model_dump() if hasattr(entry, 'model_dump') else entry
                for entry in client.messages.batches.results(batch_id)]

    return {'submit': submit, 'poll': poll, 'results': results}


def _result_message(entry):
    """Return ``(message, failure_class, error)`` for one per-request result."""
    result = entry.get('result') if isinstance(entry, dict) else None
    if not isinstance(result, dict):
        return None, 'malformed_output', 'batch result entry has no result object'
    kind = result.get('type')
    if kind == 'succeeded':
        message = result.get('message')
        if not isinstance(message, dict):
            return None, 'malformed_output', 'succeeded result carries no message'
        return message, None, None
    if kind == 'expired':
        return None, 'batch_expired', 'batch request expired before processing'
    if kind == 'canceled':
        return None, 'batch_canceled', 'batch request was canceled'
    if kind == 'errored':
        error = result.get('error') or {}
        inner = error.get('error') if isinstance(error, dict) else None
        name = inner.get('type') if isinstance(inner, dict) else None
        return None, ERROR_CLASSES.get(name, 'transport_error'), str(error)[:400]
    return None, 'transport_error', 'unknown batch result type %r' % (kind,)


class AnthropicBatchesCall:
    """One bounded Batches submission: reserve N, submit once, seal N envelopes."""

    def __init__(self, ledger, transport):
        if not isinstance(ledger, CallReservationLedger):
            raise TransportRefusal('batches call requires CallReservationLedger')
        for name in ('submit', 'poll', 'results'):
            if not callable((transport or {}).get(name)):
                raise TransportRefusal('batches transport lacks a callable %r' % name)
        self.ledger = ledger
        self.transport = transport

    # -- phase 1: reserve the ceiling, then submit ----------------------------
    def submit(self, requests, receipt_path, model=MODEL):
        """Reserve one ledger call per request BEFORE the submit, then submit once."""
        shas = [request['request_sha256'] for request in requests]
        if os.path.isfile(receipt_path):
            existing = read_json(receipt_path, 'batches submission receipt')
            if existing.get('request_sha256_list') != shas:
                raise TransportRefusal(
                    'ambiguous_resume: a different request set is already submitted '
                    'under this receipt; the batch must not be replayed')
            return existing
        for request in requests:
            verify_request(request)
            if request['requested_model'] != model:
                raise TransportRefusal('batches comparison requires exact %s' % model)
        payload = build_batch(requests)
        reservations = []
        try:
            for ordinal, request in enumerate(requests, start=1):
                key = canonical_hash({
                    'route': ANTHROPIC_BATCHES_ROUTE,
                    'run_id': self.ledger.run_id,
                    'request_sha256': request['request_sha256'],
                })
                reservations.append(self.ledger.reserve(
                    request['purpose'], profile=model,
                    detail='%s:%s' % (ANTHROPIC_BATCHES_ROUTE,
                                      custom_id_for(ordinal, request)),
                    idempotency_key=key))
        except CallLimitReached as exc:
            raise TransportRefusal('reservation_exhausted: %s' % exc) from exc
        started = time.time()
        batch = self.transport['submit'](payload)
        receipt = {
            'schema': 'pwg.batches_submission.v1',
            'route': ANTHROPIC_BATCHES_ROUTE,
            'run_id': str(self.ledger.run_id),
            'requested_model': model,
            'batch_id': batch.get('id'),
            'submitted_epoch': started,
            'provider_created_at': str(batch.get('created_at')),
            'processing_status': batch.get('processing_status'),
            'request_count': len(requests),
            'request_sha256_list': shas,
            'custom_ids': [entry['custom_id'] for entry in payload],
            'reservation_ids': [row.get('reservation_id') for row in reservations],
            'reservation_ordinals': [row.get('ordinal') for row in reservations],
            'pricing_basis': PRICING_BASIS,
        }
        if not receipt['batch_id']:
            raise TransportRefusal('provider returned no batch id; reservations are spent')
        return atomic_json(receipt_path, receipt)

    # -- phase 2: poll -------------------------------------------------------
    def poll(self, receipt):
        batch = self.transport['poll'](receipt['batch_id'])
        return {
            'batch_id': batch.get('id'),
            'processing_status': batch.get('processing_status'),
            'request_counts': batch.get('request_counts') or {},
            'ended_at': str(batch.get('ended_at')),
            'ended': batch.get('processing_status') == BATCH_ENDED,
        }

    # -- phase 3: retrieve and seal -----------------------------------------
    def retrieve(self, requests, receipt, envelope_dir, wall_ms=None):
        """Seal one envelope per request and finalize each reservation exactly once."""
        status = self.poll(receipt)
        if not status['ended']:
            raise TransportRefusal(
                'batch %s is still %r; retrieve only an ended batch'
                % (receipt['batch_id'], status['processing_status']))
        entries = {entry.get('custom_id'): entry
                   for entry in self.transport['results'](receipt['batch_id'])}
        envelopes = []
        by_sha = {request['request_sha256']: request for request in requests}
        for ordinal, sha in enumerate(receipt['request_sha256_list'], start=1):
            request = by_sha[sha]
            custom_id = receipt['custom_ids'][ordinal - 1]
            path = os.path.join(envelope_dir, '%s.envelope.json' % custom_id)
            if os.path.isfile(path):
                envelopes.append(verify_envelope(read_json(path, 'batches envelope')))
                continue
            reservation = {'reservation_id': receipt['reservation_ids'][ordinal - 1],
                           'ordinal': receipt['reservation_ordinals'][ordinal - 1]}
            envelopes.append(self._seal_one(
                request, entries.get(custom_id), reservation, path, wall_ms))
        return envelopes

    def _seal_one(self, request, entry, reservation, path, wall_ms):
        message, failure, error = (None, 'malformed_output',
                                   'no batch result for this request')
        if entry is not None:
            message, failure, error = _result_message(entry)
        usage_raw = message.get('usage') if isinstance(message, dict) else None
        telemetry = normalize_usage(usage_raw)
        cost_evaluable = telemetry is not None
        observed_cost = telemetry['observed_cost_usd'] if telemetry else None
        returned_model = message.get('model') if isinstance(message, dict) else None
        result = None
        schema_compliant = False
        audit_passed = False
        audit_reasons = []
        if failure is None and returned_model != request['requested_model']:
            failure = 'model_substitution'
            error = 'returned model %r differs from requested %r' % (
                returned_model, request['requested_model'])
        elif failure is None:
            try:
                result = amr._extract_result(message)
            except ValueError as exc:
                failure = 'malformed_output'
                error = str(exc)
            if result is not None:
                audit_passed, audit_reasons = audit_canary(
                    result, request['output_schema'])
                schema_compliant = not any(
                    reason.startswith('schema:') for reason in audit_reasons)
                if not schema_compliant:
                    failure = 'schema_failure'
                    error = audit_reasons[0]
                elif not audit_passed:
                    failure = 'content_audit_failure'
                    error = '; '.join(audit_reasons)
        if failure is None and not cost_evaluable:
            failure = 'unevaluable_cost'
            error = 'batch result usage is absent or incomplete'
        usage_evidence = dict(usage_raw) if isinstance(usage_raw, dict) else {}
        if telemetry is not None:
            usage_evidence.update({
                'pricing_basis': PRICING_BASIS,
                'price_per_mtok_usd': {
                    name: rate * 0.5
                    for name, rate in SONNET_STANDARD_PER_MTOK_USD.items()},
            })
        envelope = seal_envelope(
            route=ANTHROPIC_BATCHES_ROUTE, request=request, run_id=self.ledger.run_id,
            reservation=reservation, returned_model=returned_model,
            wall_ms=wall_ms, usage=usage_evidence,
            cost_evaluable=cost_evaluable, observed_cost_usd=observed_cost,
            accounting=(telemetry.get('accounting') if telemetry else None),
            result=result, schema_compliant=schema_compliant,
            audit_passed=audit_passed, audit_reasons=audit_reasons,
            failure_class=failure, error=error)
        atomic_json(path, envelope)
        self.ledger.finalize(reservation, telemetry or unevaluable_telemetry(), evidence={
            'schema': 'pwg.batches_finalization.v1',
            'envelope_sha256': envelope['envelope_sha256'],
        })
        return envelope


def api_client():
    """Authenticated client + a provenance note that never contains the secret."""
    return amr.api_client()


def credential_note():
    """Printable credential provenance, computed without touching the secret's value."""
    return amr.credential_note()
