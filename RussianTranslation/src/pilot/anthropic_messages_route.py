#!/usr/bin/env python
"""Ledger-backed Anthropic Messages transport for PWG qualification.

The adapter is dependency-injected for hermetic tests.  Its live transport uses
one forced ``emit_cards`` tool call and a one-hour cache breakpoint on the exact
prompt bytes shared with the gateway ticket.
"""
from __future__ import annotations

import os
import time

from call_reservation import (
    CallLimitReached,
    CallReservationLedger,
    normalize_telemetry,
    unevaluable_telemetry,
)
from route_transport import (
    ANTHROPIC_ROUTE,
    TransportRefusal,
    atomic_json,
    audit_canary,
    canonical_hash,
    read_json,
    seal_envelope,
    verify_envelope,
    verify_request,
)
from usage_accounting import API_STANDARD, build as build_accounting, legacy_telemetry


MODEL = 'claude-opus-5'
PRICING_BASIS = 'anthropic-standard-opus-5-2026-08-11.v1'
# Official pricing says the Opus 4.5+ schedule applies to future models:
# https://platform.claude.com/docs/en/about-claude/pricing
PRICE_PER_MTOK = {
    'input_tokens': 5.00,
    'output_tokens': 25.00,
    'cache_creation_tokens': 10.00,  # explicit one-hour cache write = 2x input
    'cache_read_tokens': 0.50,
}
SECRETS_ENV = r'C:\Users\user\.secrets\anthropic.env'


def _nonnegative_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def normalize_usage(raw):
    """Return priced ledger telemetry or ``None`` when usage is incomplete."""
    if not isinstance(raw, dict):
        return None
    source = {
        'input_tokens': raw.get('input_tokens'),
        'output_tokens': raw.get('output_tokens'),
        'cache_creation_tokens': raw.get('cache_creation_input_tokens'),
        'cache_read_tokens': raw.get('cache_read_input_tokens'),
    }
    if not all(_nonnegative_int(value) for value in source.values()):
        return None
    cost = sum(source[name] * PRICE_PER_MTOK[name] for name in source) / 1_000_000
    accounting = build_accounting(
        source, billing_mode=API_STANDARD, observed_cash_usd=round(cost, 9))
    return normalize_telemetry(legacy_telemetry(accounting))


def _read_secret():
    for name in ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN'):
        value = (os.environ.get(name) or '').strip()
        if value:
            return value, '%s present in environment' % name
    if os.path.isfile(SECRETS_ENV):
        with open(SECRETS_ENV, encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                name, _, value = line.partition('=')
                if name.strip() in ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN'):
                    value = value.strip().strip('"').strip("'")
                    if value:
                        return value, '%s read from %s' % (name.strip(), SECRETS_ENV)
    return None, 'no Anthropic API credential found'


def api_client():
    import anthropic
    secret, note = _read_secret()
    return (anthropic.Anthropic(api_key=secret), note) if secret else (None, note)


def check_auth_and_model(client, model=MODEL):
    """Zero-token authenticated GET proving the exact model ID is addressable."""
    if client is None:
        return {'authenticated': False, 'model_available': False,
                'reason': 'no_client'}
    try:
        info = client.models.retrieve(model)
    except Exception as exc:  # noqa: BLE001 -- report the typed public class only
        return {
            'authenticated': getattr(exc, 'status_code', None) not in (401, 403),
            'model_available': False,
            'reason': '%s%s' % (
                type(exc).__name__,
                '' if getattr(exc, 'status_code', None) is None
                else ':http_%s' % exc.status_code),
        }
    returned = getattr(info, 'id', None)
    return {'authenticated': True, 'model_available': returned == model,
            'returned_model': returned, 'reason': None}


def sdk_transport(client):
    """Build the live callable. The credential never enters an artifact or argv."""
    if client is None:
        raise TransportRefusal('Anthropic transport has no authenticated client')

    def invoke(request):
        response = client.messages.create(
            model=request['requested_model'],
            max_tokens=request['max_output_tokens'],
            messages=[{
                'role': 'user',
                'content': [{
                    'type': 'text',
                    'text': request['prompt'],
                    'cache_control': {'type': 'ephemeral', 'ttl': '1h'},
                }],
            }],
            tools=[{
                'name': 'emit_cards',
                'description': 'Return the frozen PWG qualification result.',
                'input_schema': request['output_schema'],
            }],
            tool_choice={'type': 'tool', 'name': 'emit_cards'},
            timeout=request['hard_timeout_ms'] / 1000,
        )
        return response.model_dump()

    return invoke


def _classify_exception(exc):
    status = getattr(exc, 'status_code', None)
    if status in (401, 403):
        return 'authentication'
    if status == 429:
        return 'rate_limit'
    if status in (408, 504) or type(exc).__name__ in ('APITimeoutError', 'TimeoutError'):
        return 'timeout'
    if type(exc).__name__ in ('APIConnectionError', 'ConnectError', 'ConnectionError'):
        return 'connection'
    return 'transport_error'


def _extract_result(message):
    if not isinstance(message, dict):
        raise ValueError('Anthropic response is not an object')
    blocks = message.get('content')
    if not isinstance(blocks, list):
        raise ValueError('Anthropic response content is not a list')
    matches = [block for block in blocks if isinstance(block, dict)
               and block.get('type') == 'tool_use'
               and block.get('name') == 'emit_cards']
    if len(matches) != 1:
        raise ValueError('expected exactly one emit_cards tool result, got %d' % len(matches))
    value = matches[0].get('input')
    if not isinstance(value, dict):
        raise ValueError('emit_cards input is not an object')
    return value


def _reservation_for_key(ledger, key):
    return next((row for row in ledger.snapshot().get('reservations') or []
                 if row.get('idempotency_key') == key), None)


class AnthropicMessagesCall:
    """One exact-once-at-the-ledger-boundary Anthropic qualification call."""

    def __init__(self, ledger, transport):
        if not isinstance(ledger, CallReservationLedger):
            raise TransportRefusal('Anthropic call requires CallReservationLedger')
        self.ledger = ledger
        self.transport = transport

    def invoke(self, request, envelope_path):
        verify_request(request)
        if request['requested_model'] != MODEL:
            raise TransportRefusal('Anthropic comparison requires exact %s' % MODEL)
        key = canonical_hash({
            'route': ANTHROPIC_ROUTE,
            'run_id': self.ledger.run_id,
            'request_sha256': request['request_sha256'],
        })
        existing = _reservation_for_key(self.ledger, key)
        if existing and os.path.isfile(envelope_path):
            envelope = verify_envelope(read_json(envelope_path, 'Anthropic envelope'))
            telemetry = self._telemetry_from_envelope(envelope)
            self.ledger.finalize(existing, telemetry, evidence={
                'schema': 'pwg.anthropic_finalization.v1',
                'envelope_sha256': envelope['envelope_sha256'],
            })
            return envelope
        if existing:
            raise TransportRefusal(
                'ambiguous_resume: Anthropic reservation exists without a sealed envelope; '
                'the call must not be replayed')
        try:
            reservation = self.ledger.reserve(
                request['purpose'], profile=request['requested_model'],
                detail=ANTHROPIC_ROUTE, idempotency_key=key)
        except CallLimitReached as exc:
            raise TransportRefusal('reservation_exhausted: %s' % exc) from exc

        started = time.monotonic()
        message = None
        caught = None
        try:
            message = self.transport(request)
        except BaseException as exc:  # noqa: BLE001 -- reservation is irreversible
            caught = exc
        wall_ms = int((time.monotonic() - started) * 1000)

        usage_raw = message.get('usage') if isinstance(message, dict) else None
        telemetry = normalize_usage(usage_raw)
        cost_evaluable = telemetry is not None
        observed_cost = telemetry['observed_cost_usd'] if telemetry else None
        returned_model = message.get('model') if isinstance(message, dict) else None
        result = None
        schema_compliant = False
        audit_passed = False
        audit_reasons = []
        failure = None
        error = None

        if caught is not None:
            failure = _classify_exception(caught)
            error = '%s: %s' % (type(caught).__name__, str(caught)[:400])
        elif wall_ms > request['hard_timeout_ms']:
            failure = 'timeout'
            error = 'wall_ms exceeded hard timeout'
        elif returned_model != request['requested_model']:
            failure = 'model_substitution'
            error = 'returned model %r differs from requested %r' % (
                returned_model, request['requested_model'])
        else:
            try:
                result = _extract_result(message)
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
            error = 'Anthropic response usage is absent or incomplete'

        usage_evidence = dict(usage_raw) if isinstance(usage_raw, dict) else {}
        if telemetry is not None:
            usage_evidence.update({
                'pricing_basis': PRICING_BASIS,
                'price_per_mtok_usd': dict(PRICE_PER_MTOK),
            })

        envelope = seal_envelope(
            route=ANTHROPIC_ROUTE, request=request, run_id=self.ledger.run_id,
            reservation=reservation, returned_model=returned_model,
            wall_ms=wall_ms, usage=usage_evidence,
            cost_evaluable=cost_evaluable, observed_cost_usd=observed_cost,
            accounting=(telemetry.get('accounting') if telemetry else None),
            result=result, schema_compliant=schema_compliant,
            audit_passed=audit_passed, audit_reasons=audit_reasons,
            failure_class=failure, error=error)
        atomic_json(envelope_path, envelope)
        ledger_telemetry = telemetry or unevaluable_telemetry()
        self.ledger.finalize(reservation, ledger_telemetry, evidence={
            'schema': 'pwg.anthropic_finalization.v1',
            'envelope_sha256': envelope['envelope_sha256'],
        })
        return envelope

    @staticmethod
    def _telemetry_from_envelope(envelope):
        if not envelope.get('cost_evaluable'):
            return unevaluable_telemetry()
        raw = normalize_usage(envelope.get('usage'))
        if raw is None or raw['observed_cost_usd'] != envelope.get('observed_cost_usd'):
            raise TransportRefusal('sealed Anthropic envelope usage/cost mismatch')
        return raw
