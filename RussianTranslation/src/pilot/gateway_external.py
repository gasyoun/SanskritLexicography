#!/usr/bin/env python
"""Crash-safe two-phase bridge for interactive router.cheap Agent calls.

``prepare-external`` durably spends a reservation and publishes an immutable
ticket before an external Agent turn is allowed.  ``record-external`` consumes
only a saved public response wrapper, validates every bound field and the full
JSON Schema, finalizes that exact reservation, and atomically seals a
non-promotable envelope.  This module never reads a credential or invokes a
model, gateway, subprocess, coordinator, store, TM, or promotion path.
"""

import argparse
import datetime as dt
import glob
import json
import os
import sys
import tempfile
import uuid

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(REPO, 'src')):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from call_reservation import (  # noqa: E402
    CallLimitReached,
    CallReservationLedger,
    _durable_replace,
)
from execution_contract import (  # noqa: E402
    PRODUCTION_HARD_TIMEOUT_MS,
    assert_timeout_within_ceiling,
)
from gateway_attestation import ATTESTATION_SCHEMA  # noqa: E402
from gateway_route import (  # noqa: E402
    GATEWAY_ROUTE,
    SYNTHETIC_PROVENANCE,
    canonical_json_bytes,
    final_text,
    sha256_bytes,
    structured_from_transcript,
    telemetry_from_gateway_usage,
    validate_complete_schema,
)


ROUTE = GATEWAY_ROUTE
TICKET_SCHEMA = 'pwg.gateway_external_ticket.v2'
RESPONSE_SCHEMA = 'pwg.gateway_external_response.v2'
ENVELOPE_SCHEMA = 'pwg.gateway_external_envelope.v2'
RECOVERY_SCHEMA = 'pwg.gateway_external_recovery.v2'
OWNER_WAIVER_ID = 'router-cheap-agent-owner-waiver-2026-08-09.v1'
DETAIL_SCHEMA = 'pwg.gateway_external_prepare.v1'
DISPATCH_BINDING_SCHEMA = 'pwg.gateway_external_dispatch_binding.v1'
PROTOCOL_SCHEMA_PATHS = {
    TICKET_SCHEMA: os.path.join(REPO, 'schemas', 'pwg_gateway_external_ticket.schema.json'),
    RESPONSE_SCHEMA: os.path.join(REPO, 'schemas', 'pwg_gateway_external_response.schema.json'),
    ENVELOPE_SCHEMA: os.path.join(REPO, 'schemas', 'pwg_gateway_external_envelope.schema.json'),
}


class ExternalRefusal(RuntimeError):
    """A fail-closed bridge refusal."""


def _require_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ExternalRefusal('%s must be a non-empty string' % name)
    return value


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, indent=2,
                      sort_keys=True).encode('utf-8') + b'\n'


def _canonical_hash(value):
    return sha256_bytes(canonical_json_bytes(value))


def _request_prompt_sha256(request):
    if not isinstance(request, dict):
        raise ExternalRefusal('request must be an object for dispatch binding')
    prompt = request.get('prompt')
    if not isinstance(prompt, str) or not prompt:
        raise ExternalRefusal('request prompt must be non-empty text')
    return sha256_bytes(prompt.encode('utf-8'))


def _read_json(path, label):
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except FileNotFoundError as exc:
        raise ExternalRefusal('%s is missing: %s' % (label, path)) from exc
    try:
        value = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExternalRefusal('%s is not complete UTF-8 JSON: %s' % (label, exc)) from exc
    return value, raw


def _validate_protocol(value, schema_id):
    schema, _ = _read_json(PROTOCOL_SCHEMA_PATHS[schema_id], 'protocol schema')
    try:
        validate_complete_schema(value, schema)
    except ValueError as exc:
        raise ExternalRefusal('%s validation failed: %s' % (schema_id, exc)) from exc
    return value


def _fire(fault, phase):
    if fault is not None:
        fault(phase)


def _atomic_json(path, value, artifact, fault=None):
    """Same-directory temp + file fsync + write-through atomic replacement."""
    absolute = os.path.abspath(path)
    directory = os.path.dirname(absolute) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        dir=directory, prefix='.%s.' % os.path.basename(path),
        suffix='.tmp.%d.%s' % (os.getpid(), uuid.uuid4().hex))
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(_json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        _fire(fault, 'during_%s_temp_write' % artifact)
        _durable_replace(temporary, absolute)
        _fire(fault, 'after_%s_replacement' % artifact)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return value


def _detail(operation_sha256, ticket_path):
    return json.dumps({
        'schema': DETAIL_SCHEMA,
        'operation_sha256': operation_sha256,
        'ticket_path': os.path.abspath(ticket_path),
    }, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _parse_detail(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict) or parsed.get('schema') != DETAIL_SCHEMA:
        return None
    return parsed


def _ticket_payload(reservation, descriptor, request, output_schema):
    reserved_at_ns = reservation['reserved_at_ns']
    reserved_at = dt.datetime.fromtimestamp(
        reserved_at_ns / 1_000_000_000, tz=dt.timezone.utc
    ).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    nonce = sha256_bytes(('gateway-external-nonce\0%s\0%s' % (
        reservation['reservation_id'], descriptor['operation_sha256'])).encode('utf-8'))
    payload = {
        'schema': TICKET_SCHEMA,
        'run_id': descriptor['run_id'],
        'reservation_id': reservation['reservation_id'],
        'reservation_ordinal': reservation['ordinal'],
        'max_calls': descriptor['max_calls'],
        'route': descriptor['route'],
        'requested_model': descriptor['requested_model'],
        'purpose': descriptor['purpose'],
        'provenance_class': descriptor['provenance_class'],
        'hard_timeout_ms': descriptor['hard_timeout_ms'],
        'reserved_at': reserved_at,
        'reserved_at_ns': reserved_at_ns,
        'nonce': nonce,
        'waiver_id': descriptor['waiver_id'],
        'operation_sha256': descriptor['operation_sha256'],
        'request_sha256': descriptor['request_sha256'],
        'schema_sha256': descriptor['schema_sha256'],
        'dispatch_binding': {
            'schema': DISPATCH_BINDING_SCHEMA,
            'tool_name': 'Agent',
            'dispatch_id_scheme': 'claude-agent-tool-use.v1',
            'request_prompt_sha256': descriptor['request_prompt_sha256'],
        },
        'request': request,
        'output_schema': output_schema,
    }
    if descriptor.get('max_output_tokens') is not None:
        payload['max_output_tokens'] = descriptor['max_output_tokens']
    payload['ticket_sha256'] = _canonical_hash(payload)
    return _validate_protocol(payload, TICKET_SCHEMA)


def _operation_from_ticket(value):
    operation = {
        'schema': DETAIL_SCHEMA,
        'run_id': value.get('run_id'),
        'max_calls': value.get('max_calls'),
        'route': value.get('route'),
        'requested_model': value.get('requested_model'),
        'purpose': value.get('purpose'),
        'provenance_class': value.get('provenance_class'),
        'hard_timeout_ms': value.get('hard_timeout_ms'),
        'waiver_id': value.get('waiver_id'),
        'request_sha256': value.get('request_sha256'),
        'schema_sha256': value.get('schema_sha256'),
        'request_prompt_sha256': (
            value.get('dispatch_binding') or {}).get('request_prompt_sha256'),
    }
    if value.get('max_output_tokens') is not None:
        operation['max_output_tokens'] = value['max_output_tokens']
    return operation


def _verify_ticket(value):
    if not isinstance(value, dict) or value.get('schema') != TICKET_SCHEMA:
        raise ExternalRefusal('ticket schema mismatch')
    saved_hash = value.get('ticket_sha256')
    unhashed = dict(value)
    unhashed.pop('ticket_sha256', None)
    if saved_hash != _canonical_hash(unhashed):
        raise ExternalRefusal('ticket hash mismatch')
    if value.get('request_sha256') != _canonical_hash(value.get('request')):
        raise ExternalRefusal('ticket request hash mismatch')
    binding = value.get('dispatch_binding')
    if not isinstance(binding, dict):
        raise ExternalRefusal('ticket dispatch binding is missing')
    if binding.get('schema') != DISPATCH_BINDING_SCHEMA:
        raise ExternalRefusal('ticket dispatch binding schema mismatch')
    if binding.get('tool_name') != 'Agent':
        raise ExternalRefusal('ticket dispatch tool mismatch')
    if binding.get('dispatch_id_scheme') != 'claude-agent-tool-use.v1':
        raise ExternalRefusal('ticket dispatch id scheme mismatch')
    if binding.get('request_prompt_sha256') != _request_prompt_sha256(
            value.get('request')):
        raise ExternalRefusal('ticket dispatch prompt hash mismatch')
    if value.get('schema_sha256') != _canonical_hash(value.get('output_schema')):
        raise ExternalRefusal('ticket schema hash mismatch')
    if value.get('operation_sha256') != _canonical_hash(_operation_from_ticket(value)):
        raise ExternalRefusal('ticket operation hash mismatch')
    if value.get('route') != ROUTE:
        raise ExternalRefusal('ticket route mismatch')
    if value.get('provenance_class') != SYNTHETIC_PROVENANCE:
        raise ExternalRefusal('ticket provenance mismatch')
    if value.get('waiver_id') != OWNER_WAIVER_ID:
        raise ExternalRefusal('ticket waiver mismatch')
    _require_text(value.get('run_id'), 'ticket run_id')
    _require_text(value.get('reservation_id'), 'ticket reservation_id')
    _require_text(value.get('requested_model'), 'ticket requested_model')
    _require_text(value.get('purpose'), 'ticket purpose')
    _require_text(value.get('nonce'), 'ticket nonce')
    try:
        assert_timeout_within_ceiling(
            value.get('hard_timeout_ms'), 'gateway_external.ticket.hard_timeout_ms')
    except (TypeError, ValueError) as exc:
        raise ExternalRefusal('ticket timeout is invalid: %s' % exc) from exc
    if value.get('max_output_tokens') is not None and (
            isinstance(value['max_output_tokens'], bool)
            or not isinstance(value['max_output_tokens'], int)
            or value['max_output_tokens'] <= 0):
        raise ExternalRefusal('ticket max_output_tokens must be a positive integer')
    try:
        validate_complete_schema({}, value.get('output_schema'))
    except ValueError as exc:
        # A valid schema may reject {}; distinguish schema invalidity by asking
        # jsonschema directly through the shared helper's stable prefix.
        if 'output schema is invalid' in str(exc):
            raise ExternalRefusal('ticket schema is invalid: %s' % exc) from exc
    _validate_protocol(value, TICKET_SCHEMA)
    return value


def prepare_external(*, ledger_path, run_id, max_calls, purpose,
                     requested_model, request_path, schema_path, ticket_path,
                     route=ROUTE, provenance=SYNTHETIC_PROVENANCE,
                     timeout_ms=PRODUCTION_HARD_TIMEOUT_MS,
                     waiver_id=OWNER_WAIVER_ID, max_output_tokens=None,
                     fault=None):
    """Reserve exactly once and publish one immutable external-call ticket."""
    _require_text(run_id, 'run_id')
    _require_text(purpose, 'purpose')
    _require_text(requested_model, 'requested_model')
    if route != ROUTE:
        raise ExternalRefusal('route must be %s' % ROUTE)
    if provenance != SYNTHETIC_PROVENANCE:
        raise ExternalRefusal('provenance must be synthetic_control')
    if waiver_id != OWNER_WAIVER_ID:
        raise ExternalRefusal('owner waiver must be %s' % OWNER_WAIVER_ID)
    if (isinstance(max_calls, bool) or not isinstance(max_calls, int)
            or max_calls < 0):
        raise ExternalRefusal('max_calls must be a non-negative integer')
    try:
        assert_timeout_within_ceiling(timeout_ms, 'gateway_external.timeout_ms')
    except (TypeError, ValueError) as exc:
        raise ExternalRefusal('timeout exceeds the 600000 ms ceiling: %s' % exc) from exc
    if max_output_tokens is not None and (
            isinstance(max_output_tokens, bool)
            or not isinstance(max_output_tokens, int)
            or max_output_tokens <= 0):
        raise ExternalRefusal('max_output_tokens must be a positive integer')
    request, _ = _read_json(request_path, 'request JSON')
    output_schema, _ = _read_json(schema_path, 'output schema')
    if not isinstance(request, dict):
        raise ExternalRefusal('request JSON must be an object')
    if not isinstance(output_schema, dict):
        raise ExternalRefusal('output schema must be an object')
    try:
        # check_schema happens before validation; {} may legitimately fail.
        validate_complete_schema({}, output_schema)
    except ValueError as exc:
        if 'output schema is invalid' in str(exc):
            raise ExternalRefusal(str(exc)) from exc

    descriptor = {
        'schema': DETAIL_SCHEMA,
        'run_id': run_id,
        'max_calls': max_calls,
        'route': route,
        'requested_model': requested_model,
        'purpose': purpose,
        'provenance_class': provenance,
        'hard_timeout_ms': int(timeout_ms),
        'waiver_id': waiver_id,
        'request_sha256': _canonical_hash(request),
        'schema_sha256': _canonical_hash(output_schema),
        'request_prompt_sha256': _request_prompt_sha256(request),
    }
    if max_output_tokens is not None:
        descriptor['max_output_tokens'] = max_output_tokens
    descriptor['operation_sha256'] = _canonical_hash(descriptor)
    ledger = CallReservationLedger(ledger_path, run_id, max_calls)
    try:
        reservation = ledger.reserve(
            purpose, profile=requested_model,
            detail=_detail(descriptor['operation_sha256'], ticket_path),
            idempotency_key=descriptor['operation_sha256'])
    except CallLimitReached as exc:
        raise ExternalRefusal('budget_exceeded:max_calls (%s)' % exc) from exc
    _fire(fault, 'after_reservation')
    ticket = _ticket_payload(reservation, descriptor, request, output_schema)
    if os.path.exists(ticket_path):
        existing, _ = _read_json(ticket_path, 'ticket')
        _verify_ticket(existing)
        if existing != ticket:
            raise ExternalRefusal('existing ticket differs from reserved operation')
        return existing
    return _atomic_json(ticket_path, ticket, 'ticket', fault=fault)


def recovery_report(ledger_path, run_id):
    """Read-only report of external reservations and ambiguous crash states."""
    ledger = CallReservationLedger.open_existing(ledger_path, run_id)
    snapshot = ledger.snapshot()
    rows = []
    ambiguous = 0
    for reservation in snapshot.get('reservations', []):
        detail = _parse_detail(reservation.get('detail'))
        if detail is None:
            continue
        ticket_path = detail.get('ticket_path')
        ticket_exists = bool(ticket_path and os.path.isfile(ticket_path))
        temp_files = sorted(glob.glob(
            os.path.join(os.path.dirname(ticket_path), '.%s.*.tmp.*'
                         % os.path.basename(ticket_path)))) if ticket_path else []
        state = 'finalized' if reservation.get('finalized') else (
            'pending_with_ticket' if ticket_exists else 'reserved_without_ticket')
        if state == 'reserved_without_ticket':
            ambiguous += 1
        rows.append({
            'reservation_id': reservation['reservation_id'],
            'ordinal': reservation['ordinal'],
            'state': state,
            'ticket_path': ticket_path,
            'ticket_exists': ticket_exists,
            'orphan_temp_files': temp_files,
            'dispatch_binding': (
                _read_json(ticket_path, 'ticket')[0].get('dispatch_binding')
                if ticket_exists else None),
        })
    return {
        'schema': RECOVERY_SCHEMA,
        'run_id': run_id,
        'calls_spent': snapshot.get('calls_spent'),
        'pending_calls': snapshot.get('usage', {}).get('pending_calls'),
        'ambiguous_reserved_without_ticket': ambiguous,
        'reservations': rows,
    }


def save_response_wrapper(response_path, wrapper, fault=None):
    """Durably publish a complete public Agent response wrapper.

    The interactive harness owns the call; this helper owns only the final
    same-directory temp/fsync/replace step.  A partial scratch capture is never
    accepted by ``record_external``.
    """
    if not isinstance(wrapper, dict) or wrapper.get('schema') != RESPONSE_SCHEMA:
        raise ExternalRefusal('response wrapper schema mismatch')
    if not isinstance(wrapper.get('content'), list):
        raise ExternalRefusal('response content must be a list')
    _validate_protocol(wrapper, RESPONSE_SCHEMA)
    if os.path.exists(response_path):
        existing, _ = _read_json(response_path, 'response wrapper')
        if existing != wrapper:
            raise ExternalRefusal('saved response wrapper differs from replay')
        return existing
    return _atomic_json(response_path, wrapper, 'response', fault=fault)


def cost_policy(route, waiver_id, usage):
    """Apply the exact owner waiver without turning unknown cost into zero."""
    telemetry, reason = telemetry_from_gateway_usage(usage)
    if reason is None:
        return {
            'cost_evaluable': True,
            'observed_cost_usd': telemetry['observed_cost_usd'],
            'waiver_applied': False,
        }
    if route != ROUTE or waiver_id != OWNER_WAIVER_ID:
        raise ExternalRefusal(
            'usage is absent/unevaluable and no exact router.cheap owner waiver applies')
    return {
        'cost_evaluable': False,
        'observed_cost_usd': None,
        'waiver_applied': True,
    }


def _parse_time(value, name):
    if not isinstance(value, str) or not value:
        return None, '%s evidence is missing' % name
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None, '%s evidence is malformed' % name
    if parsed.tzinfo is None:
        return None, '%s evidence must carry a timezone' % name
    return parsed.astimezone(dt.timezone.utc), None


def _timing_outcome(wrapper, timeout_ms):
    started, start_error = _parse_time(wrapper.get('started_at'), 'started_at')
    ended, end_error = _parse_time(wrapper.get('ended_at'), 'ended_at')
    wall_ms = wrapper.get('wall_ms')
    if start_error or end_error:
        return False, 'timing_missing', start_error or end_error
    if (isinstance(wall_ms, bool) or not isinstance(wall_ms, (int, float))
            or wall_ms < 0):
        return False, 'timing_missing', 'wall_ms evidence is missing or invalid'
    if ended < started:
        return False, 'timestamp_mismatch', 'ended_at precedes started_at'
    if wall_ms > timeout_ms:
        return False, 'timeout', 'wall_ms exceeded hard timeout'
    derived = (ended - started).total_seconds() * 1000
    if abs(derived - wall_ms) > 1:
        return False, 'timestamp_mismatch', (
            'timestamp interval %.3f ms disagrees with wall_ms %s' % (derived, wall_ms))
    return True, None, None


def _content_outcome(wrapper, output_schema):
    text = final_text(wrapper)
    try:
        result = structured_from_transcript(wrapper)
        validate_complete_schema(result, output_schema)
    except ValueError as exc:
        failure = 'empty_output' if str(exc).startswith('empty_output') else 'malformed_output'
        return False, failure, str(exc), None, text
    return True, None, None, result, text


def _validate_response_binding(wrapper, ticket, attestation=None):
    """Bind a saved wrapper to its ticket.

    ``returned_model`` is normally required to equal the requested model — the
    contract forbids substitution.  When an H2537 attestation is supplied and it
    *observed* a different served model, that equality is deliberately not
    enforced: refusing here would discard the only evidence of the substitution.
    ``record_external`` instead seals the mismatch truthfully
    (``model_matches_request: false``) and marks the call non-compliant.
    """
    if not isinstance(wrapper, dict) or wrapper.get('schema') != RESPONSE_SCHEMA:
        raise ExternalRefusal('response wrapper schema mismatch')
    attested_model = None
    if isinstance(attestation, dict):
        attested_model = attestation.get('attested_model')
    expected = {
        'run_id': ticket['run_id'],
        'reservation_id': ticket['reservation_id'],
        'route': ticket['route'],
        'requested_model': ticket['requested_model'],
        'returned_model': (
            attested_model if isinstance(attested_model, str) and attested_model
            else ticket['requested_model']),
        'purpose': ticket['purpose'],
        'nonce': ticket['nonce'],
        'dispatch_id': (
            attestation.get('dispatch_id') if isinstance(attestation, dict)
            else wrapper.get('dispatch_id')),
    }
    for field, value in expected.items():
        if wrapper.get(field) != value:
            raise ExternalRefusal(
                'response %s mismatch: expected %r, got %r'
                % (field, value, wrapper.get(field)))
    if not isinstance(wrapper.get('content'), list):
        raise ExternalRefusal('response content must be a list')
    _validate_protocol(wrapper, RESPONSE_SCHEMA)


def _validate_ticket_against_ledger(ticket, ledger):
    snapshot = ledger.snapshot()
    reservation = next((row for row in snapshot.get('reservations', [])
                        if row.get('reservation_id') == ticket['reservation_id']), None)
    if reservation is None:
        raise ExternalRefusal('ticket reservation is absent from the ledger')
    expected = {
        'ordinal': ticket['reservation_ordinal'],
        'purpose': ticket['purpose'],
        'profile': ticket['requested_model'],
        'idempotency_key': ticket['operation_sha256'],
    }
    for field, value in expected.items():
        if reservation.get(field) != value:
            raise ExternalRefusal('ledger reservation %s mismatch' % field)
    detail = _parse_detail(reservation.get('detail'))
    if not detail or detail.get('operation_sha256') != ticket['operation_sha256']:
        raise ExternalRefusal('ledger reservation operation mismatch')
    return reservation


def _load_attestation(attestation_path, ticket, wrapper):
    """Read and bind an H2537 served-model/usage attestation, or return None.

    The attestation is an independent observation written by the harness, so it
    must bind to the same run/reservation/model as the ticket and must cover the
    wrapper's declared call window.  A mis-bound attestation is refused rather
    than ignored: silently dropping it would return the envelope to the
    self-asserted state this feature exists to end.
    """
    if not attestation_path:
        return None
    record, raw = _read_json(attestation_path, 'attestation')
    if record.get('schema') != ATTESTATION_SCHEMA:
        raise ExternalRefusal('attestation schema mismatch')
    for field, expected in (
            ('run_id', ticket['run_id']),
            ('reservation_id', ticket['reservation_id']),
            ('requested_model', ticket['requested_model']),
            ('ticket_sha256', ticket['ticket_sha256']),
            ('request_prompt_sha256',
             ticket['dispatch_binding']['request_prompt_sha256']),
            ('dispatch_id', wrapper.get('dispatch_id'))):
        if record.get(field) != expected:
            raise ExternalRefusal(
                'attestation %s mismatch: expected %r, got %r'
                % (field, expected, record.get(field)))
    if record.get('attestation_scope') != 'dispatch':
        raise ExternalRefusal('attestation is not dispatch-scoped')
    if record.get('dispatch_status') != 'completed':
        raise ExternalRefusal('attestation dispatch is not completed')
    if record.get('started_at') != wrapper.get('started_at') or \
            record.get('ended_at') != wrapper.get('ended_at'):
        raise ExternalRefusal(
            'attestation window does not match the response wrapper window')
    recomputed = dict(record)
    stated = recomputed.pop('attestation_sha256', None)
    if sha256_bytes(canonical_json_bytes(recomputed)) != stated:
        raise ExternalRefusal('attestation self-hash does not verify')
    return record


def record_external(*, ticket_path, ledger_path, run_id, response_path,
                    schema_path, envelope_path, attestation_path=None,
                    fault=None):
    """Validate and seal one saved public response, idempotently."""
    ticket, _ = _read_json(ticket_path, 'ticket')
    _verify_ticket(ticket)
    if ticket['run_id'] != run_id:
        raise ExternalRefusal('ticket run_id mismatch')
    output_schema, _ = _read_json(schema_path, 'output schema')
    if _canonical_hash(output_schema) != ticket['schema_sha256']:
        raise ExternalRefusal('schema hash differs from the immutable ticket')
    if _canonical_hash(ticket['request']) != ticket['request_sha256']:
        raise ExternalRefusal('request hash differs from the immutable ticket')
    ledger = CallReservationLedger.open_existing(ledger_path, run_id)
    reservation = _validate_ticket_against_ledger(ticket, ledger)

    # Only after all ticket/request/schema/ledger bindings pass may response
    # content be read.
    wrapper, response_raw = _read_json(response_path, 'response wrapper')
    attestation = _load_attestation(attestation_path, ticket, wrapper)
    _validate_response_binding(wrapper, ticket, attestation)
    public_response_sha256 = sha256_bytes(response_raw)

    timing_ok, timing_failure, timing_error = _timing_outcome(
        wrapper, ticket['hard_timeout_ms'])
    content_ok, content_failure, content_error, result, text = _content_outcome(
        wrapper, output_schema)
    schema_compliant = timing_ok and content_ok
    failure_class = timing_failure or content_failure
    error = timing_error or content_error

    telemetry, usage_reason = telemetry_from_gateway_usage(wrapper.get('usage'))
    policy = cost_policy(ticket['route'], ticket['waiver_id'], wrapper.get('usage'))

    # An attested served-model mismatch is a hard contract breach: the route
    # returned a model the ticket did not request.  It is sealed truthfully and
    # marked non-compliant rather than refused, so the evidence survives.
    model_attested = attestation is not None
    attested_model = attestation.get('attested_model') if model_attested else None
    attestation_ambiguous = attestation.get('ambiguous') if model_attested else None
    model_matches_request = (
        attestation.get('model_matches_request') if model_attested else None)
    if model_matches_request is False:
        schema_compliant = False
        failure_class = failure_class or 'model_substituted'
        error = error or (
            'attested served model %r differs from requested %r'
            % (attested_model, ticket['requested_model']))

    if not schema_compliant:
        telemetry = dict(telemetry, cost_evaluable=False)
    observed = policy['observed_cost_usd']
    if observed is None and telemetry.get('observed_cost_usd'):
        observed = telemetry['observed_cost_usd']

    envelope = {
        'schema': ENVELOPE_SCHEMA,
        'route': ticket['route'],
        'requested_model': ticket['requested_model'],
        'returned_model': wrapper['returned_model'],
        'model_matches_request': model_matches_request,
        'provenance_class': ticket['provenance_class'],
        'promotable': False,
        'run_id': ticket['run_id'],
        'reservation_id': ticket['reservation_id'],
        'reservation_ordinal': ticket['reservation_ordinal'],
        'purpose': ticket['purpose'],
        'nonce': ticket['nonce'],
        'dispatch_id': wrapper['dispatch_id'],
        'dispatch_attested': model_attested,
        'attestation_scope': (
            attestation.get('attestation_scope') if model_attested else None),
        'waiver_id': ticket['waiver_id'],
        'waiver_applied': policy['waiver_applied'],
        'hard_timeout_ms': ticket['hard_timeout_ms'],
        'started_at': wrapper.get('started_at'),
        'ended_at': wrapper.get('ended_at'),
        'wall_ms': wrapper.get('wall_ms'),
        'schema_compliant': schema_compliant,
        'failure_class': failure_class,
        'error': error,
        'result': result if schema_compliant else None,
        'cost_evaluable': bool(policy['cost_evaluable'] and schema_compliant),
        'observed_cost_usd': observed,
        'ledger_observed_cost_floor_usd': telemetry['observed_cost_usd'],
        'ledger_telemetry': telemetry,
        'usage_policy_reason': usage_reason,
        'ticket_sha256': ticket['ticket_sha256'],
        'request_sha256': ticket['request_sha256'],
        'schema_sha256': ticket['schema_sha256'],
        'public_response_sha256': public_response_sha256,
        'final_text_sha256': sha256_bytes(text.encode('utf-8')) if text else None,
        'canonical_result_sha256': (
            _canonical_hash(result) if schema_compliant else None),
        'model_attested': model_attested,
        'attested_model': attested_model,
        'attestation_sha256': (
            attestation.get('attestation_sha256') if model_attested else None),
        'attested_usage_totals': (
            attestation.get('usage_totals') if model_attested else None),
        'attestation_ambiguous': attestation_ambiguous,
    }
    envelope['saved_envelope_sha256'] = _canonical_hash(envelope)
    _validate_protocol(envelope, ENVELOPE_SCHEMA)
    record_fingerprint = _canonical_hash({
        'ticket_sha256': ticket['ticket_sha256'],
        'public_response_sha256': public_response_sha256,
        'saved_envelope_sha256': envelope['saved_envelope_sha256'],
    })
    evidence = {
        'schema': ENVELOPE_SCHEMA,
        'record_fingerprint_sha256': record_fingerprint,
        'public_response_sha256': public_response_sha256,
        'saved_envelope_sha256': envelope['saved_envelope_sha256'],
        'ticket_sha256': ticket['ticket_sha256'],
    }

    _fire(fault, 'before_ledger_finalization')
    try:
        ledger.finalize(reservation, telemetry, evidence=evidence)
    except ValueError as exc:
        if 'already finalized with different' in str(exc):
            raise ExternalRefusal(
                'consumed ticket received a different response/evidence replay') from exc
        raise
    _fire(fault, 'after_ledger_finalization')

    if os.path.exists(envelope_path):
        existing, _ = _read_json(envelope_path, 'saved envelope')
        if existing != envelope:
            raise ExternalRefusal('saved envelope differs from finalized response evidence')
        return existing
    return _atomic_json(envelope_path, envelope, 'envelope', fault=fault)


def assert_not_promotable(envelope):
    """Explicit guard for consumers: external synthetic envelopes always refuse."""
    if (isinstance(envelope, dict)
            and envelope.get('schema') == ENVELOPE_SCHEMA
            and envelope.get('route') == ROUTE
            and envelope.get('provenance_class') == SYNTHETIC_PROVENANCE
            and envelope.get('promotable') is False):
        raise ExternalRefusal(
            'router.cheap synthetic external envelope is permanently non-promotable')
    raise ExternalRefusal('unrecognized external envelope is non-promotable')


def _parser():
    parser = argparse.ArgumentParser(
        description='Durable offline bridge around an external router.cheap Agent turn.')
    sub = parser.add_subparsers(dest='command', required=True)
    prepare = sub.add_parser(
        'prepare-external', help='reserve before spend and atomically write a ticket')
    prepare.add_argument('--ledger', required=True)
    prepare.add_argument('--run-id', required=True)
    prepare.add_argument('--max-calls', required=True, type=int)
    prepare.add_argument('--purpose', required=True)
    prepare.add_argument('--requested-model', required=True)
    prepare.add_argument('--request', required=True)
    prepare.add_argument('--schema', required=True)
    prepare.add_argument('--ticket', required=True)
    prepare.add_argument('--route', default=ROUTE)
    prepare.add_argument('--provenance', default=SYNTHETIC_PROVENANCE)
    prepare.add_argument('--timeout-ms', type=int, default=PRODUCTION_HARD_TIMEOUT_MS)
    prepare.add_argument('--max-output-tokens', type=int)
    prepare.add_argument('--waiver-id', default=OWNER_WAIVER_ID)

    record = sub.add_parser(
        'record-external', help='validate a saved public wrapper and seal its envelope')
    record.add_argument('--ticket', required=True)
    record.add_argument('--ledger', required=True)
    record.add_argument('--run-id', required=True)
    record.add_argument('--response', required=True)
    record.add_argument('--schema', required=True)
    record.add_argument('--envelope', required=True)
    record.add_argument(
        '--attestation',
        help='optional H2537 served-model/usage attestation json '
             '(gateway_attestation.py). When supplied, returned_model and usage '
             'are bound to an independent harness observation instead of being '
             'accepted as operator assertions.')

    save = sub.add_parser(
        'save-response', help='atomically publish a complete public response wrapper')
    save.add_argument('--source', required=True,
                      help='scratch JSON capture to validate and publish')
    save.add_argument('--response', required=True,
                      help='durable response-wrapper destination')

    recovery = sub.add_parser(
        'recovery-report', help='read-only report of pending/ambiguous reservations')
    recovery.add_argument('--ledger', required=True)
    recovery.add_argument('--run-id', required=True)
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        if args.command == 'prepare-external':
            result = prepare_external(
                ledger_path=args.ledger, run_id=args.run_id,
                max_calls=args.max_calls, purpose=args.purpose,
                requested_model=args.requested_model,
                request_path=args.request, schema_path=args.schema,
                ticket_path=args.ticket, route=args.route,
                provenance=args.provenance, timeout_ms=args.timeout_ms,
                waiver_id=args.waiver_id,
                max_output_tokens=args.max_output_tokens)
        elif args.command == 'record-external':
            result = record_external(
                ticket_path=args.ticket, ledger_path=args.ledger,
                run_id=args.run_id, response_path=args.response,
                schema_path=args.schema, envelope_path=args.envelope,
                attestation_path=args.attestation)
        elif args.command == 'save-response':
            wrapper, _ = _read_json(args.source, 'scratch response wrapper')
            result = save_response_wrapper(args.response, wrapper)
        else:
            result = recovery_report(args.ledger, args.run_id)
    except ExternalRefusal as exc:
        print('REFUSED: %s' % exc, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
