#!/usr/bin/env python
"""Shared sealed-envelope contract for PWG transport qualification.

The translated payload deliberately remains the frozen H2554 canary contract.
The *actual* transport is recorded here, outside that payload, so replaying the
same prompt/schema through Anthropic cannot impersonate ``router.cheap``.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile

from gateway_route import canonical_json_bytes, validate_complete_schema
from usage_accounting import (
    UNKNOWN_GATEWAY,
    build as build_accounting,
    validate as validate_accounting,
)


SCHEMA = 'pwg.transport_envelope.v1'
COMPARISON_SCHEMA = 'pwg.route_comparison.v1'
GATEWAY_ROUTE = 'router-cheap-agent'
ANTHROPIC_ROUTE = 'anthropic-messages'
SUPPORTED_ROUTES = (GATEWAY_ROUTE, ANTHROPIC_ROUTE)
SYNTHETIC_PROVENANCE = 'synthetic_control'
FAILURE_CLASSES = (
    'authentication', 'rate_limit', 'connection', 'timeout',
    'model_substitution', 'malformed_output', 'schema_failure',
    'unevaluable_cost', 'content_audit_failure', 'reservation_exhausted',
    'ambiguous_resume', 'transport_error',
)
TN_RE = re.compile(r'\{T\d+\}')
LATIN_RE = re.compile(r'[A-Za-z]')
SHA_RE = re.compile(r'^[0-9a-f]{64}$')


class TransportRefusal(RuntimeError):
    """Fail-closed route-contract refusal."""


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def canonical_hash(value):
    return sha256_bytes(canonical_json_bytes(value))


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path, value):
    """Write one durable UTF-8/LF JSON artifact."""
    absolute = os.path.abspath(path)
    directory = os.path.dirname(absolute) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        dir=directory, prefix='.%s.' % os.path.basename(path), suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, absolute)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return value


def read_json(path, label='JSON artifact'):
    try:
        with open(path, encoding='utf-8') as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TransportRefusal('%s is unavailable or invalid: %s' % (label, exc)) from exc
    if not isinstance(value, dict):
        raise TransportRefusal('%s must be a JSON object' % label)
    return value


def build_request(*, prompt, output_schema, requested_model, purpose,
                  manifest_sha256, hard_timeout_ms, max_output_tokens):
    """Build the immutable request both transports must consume."""
    if not isinstance(prompt, str) or not prompt:
        raise TransportRefusal('transport prompt must be non-empty text')
    if not isinstance(output_schema, dict):
        raise TransportRefusal('transport output schema must be an object')
    try:
        validate_complete_schema({}, output_schema)
    except ValueError as exc:
        if 'output schema is invalid' in str(exc):
            raise TransportRefusal(str(exc)) from exc
    if not isinstance(requested_model, str) or not requested_model:
        raise TransportRefusal('requested model must be non-empty text')
    if not SHA_RE.fullmatch(str(manifest_sha256)):
        raise TransportRefusal('manifest_sha256 must be a lowercase SHA-256')
    if (isinstance(hard_timeout_ms, bool) or not isinstance(hard_timeout_ms, int)
            or hard_timeout_ms <= 0):
        raise TransportRefusal('hard_timeout_ms must be a positive integer')
    if (isinstance(max_output_tokens, bool) or not isinstance(max_output_tokens, int)
            or max_output_tokens <= 0):
        raise TransportRefusal('max_output_tokens must be a positive integer')
    value = {
        'schema': 'pwg.transport_request.v1',
        'purpose': str(purpose),
        'requested_model': requested_model,
        'manifest_sha256': manifest_sha256,
        'prompt': prompt,
        'prompt_sha256': sha256_bytes(prompt.encode('utf-8')),
        'output_schema': output_schema,
        'output_schema_sha256': canonical_hash(output_schema),
        'hard_timeout_ms': hard_timeout_ms,
        'max_output_tokens': max_output_tokens,
        'provenance_class': SYNTHETIC_PROVENANCE,
        'promotable': False,
    }
    value['request_sha256'] = canonical_hash(value)
    return value


def verify_request(value):
    if not isinstance(value, dict) or value.get('schema') != 'pwg.transport_request.v1':
        raise TransportRefusal('transport request schema mismatch')
    copy = dict(value)
    stated = copy.pop('request_sha256', None)
    if canonical_hash(copy) != stated:
        raise TransportRefusal('transport request self-hash mismatch')
    if sha256_bytes(value.get('prompt', '').encode('utf-8')) != value.get('prompt_sha256'):
        raise TransportRefusal('transport prompt hash mismatch')
    if canonical_hash(value.get('output_schema')) != value.get('output_schema_sha256'):
        raise TransportRefusal('transport output-schema hash mismatch')
    return value


def audit_canary(result, output_schema):
    """Deterministic content gate shared by both transport arms."""
    reasons = []
    try:
        validate_complete_schema(result, output_schema)
    except ValueError as exc:
        return False, ['schema: %s' % exc]
    cards = result.get('cards') or []
    senses = [sense for card in cards
              for record in card.get('records') or []
              for sense in record.get('senses') or []]
    if len(senses) != 3:
        reasons.append('sense_count:%d/3' % len(senses))
    for index, sense in enumerate(senses, start=1):
        russian = sense.get('russian')
        if not isinstance(russian, str) or not russian.strip():
            reasons.append('sense_%d:russian_missing' % index)
        elif LATIN_RE.search(russian):
            reasons.append('sense_%d:latin_residue' % index)
        elif 'ё' in russian or 'Ё' in russian:
            reasons.append('sense_%d:yo_forbidden' % index)
    blob = json.dumps(result, ensure_ascii=False, sort_keys=True)
    if TN_RE.search(blob):
        reasons.append('tnmask_unresolved')
    for marker in ('SAN-LOSS', 'UNMAPPED'):
        if marker in blob:
            reasons.append('literal_%s' % marker.lower())
    return not reasons, reasons


def _validate_nullable_number(value, name):
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise TransportRefusal('%s must be null or non-negative number' % name)


def seal_envelope(*, route, request, run_id, reservation, returned_model,
                  wall_ms, usage, cost_evaluable, observed_cost_usd,
                  result, schema_compliant, audit_passed, audit_reasons,
                  failure_class=None, error=None, source_envelope_sha256=None,
                  dispatch_id=None, dispatch_attested=None, accounting=None):
    """Create the common non-promotable, self-hashed transport envelope."""
    verify_request(request)
    if route not in SUPPORTED_ROUTES:
        raise TransportRefusal('unsupported transport route: %r' % route)
    if failure_class is not None and failure_class not in FAILURE_CLASSES:
        raise TransportRefusal('unstable failure class: %r' % failure_class)
    _validate_nullable_number(wall_ms, 'wall_ms')
    _validate_nullable_number(observed_cost_usd, 'observed_cost_usd')
    if cost_evaluable and observed_cost_usd is None:
        raise TransportRefusal('cost-evaluable envelope requires observed cost')
    if not cost_evaluable and observed_cost_usd is not None:
        raise TransportRefusal('unevaluable cost must be null, never a false zero')
    if result is not None and not isinstance(result, dict):
        raise TransportRefusal('transport result must be an object or null')
    if schema_compliant and result is None:
        raise TransportRefusal('schema-compliant envelope requires a result')
    model_matches = (returned_model == request['requested_model']
                     if isinstance(returned_model, str) else None)
    if accounting is None:
        accounting = build_accounting(
            usage, billing_mode=UNKNOWN_GATEWAY,
            observed_cash_usd=observed_cost_usd if cost_evaluable else None)
    validate_accounting(accounting)
    value = {
        'schema': SCHEMA,
        'route': route,
        'requested_model': request['requested_model'],
        'returned_model': returned_model,
        'model_matches_request': model_matches,
        'run_id': str(run_id),
        'reservation_id': reservation.get('reservation_id'),
        'reservation_ordinal': reservation.get('ordinal'),
        'purpose': request['purpose'],
        'provenance_class': SYNTHETIC_PROVENANCE,
        'promotable': False,
        'manifest_sha256': request['manifest_sha256'],
        'request_sha256': request['request_sha256'],
        'prompt_sha256': request['prompt_sha256'],
        'output_schema_sha256': request['output_schema_sha256'],
        'hard_timeout_ms': request['hard_timeout_ms'],
        'max_output_tokens': request['max_output_tokens'],
        'wall_ms': wall_ms,
        'usage': usage if isinstance(usage, dict) else {},
        'accounting': accounting,
        'cost_evaluable': bool(cost_evaluable),
        'observed_cost_usd': observed_cost_usd,
        'schema_compliant': bool(schema_compliant),
        'audit_passed': bool(audit_passed),
        'audit_reasons': list(audit_reasons or []),
        'failure_class': failure_class,
        'error': error,
        'result': result,
        'canonical_result_sha256': canonical_hash(result) if result is not None else None,
        'source_envelope_sha256': source_envelope_sha256,
        'dispatch_id': dispatch_id,
        'dispatch_attested': dispatch_attested,
    }
    value['envelope_sha256'] = canonical_hash(value)
    return verify_envelope(value)


def verify_envelope(value):
    if not isinstance(value, dict) or value.get('schema') != SCHEMA:
        raise TransportRefusal('transport envelope schema mismatch')
    copy = dict(value)
    stated = copy.pop('envelope_sha256', None)
    if canonical_hash(copy) != stated:
        raise TransportRefusal('transport envelope self-hash mismatch')
    if value.get('route') not in SUPPORTED_ROUTES:
        raise TransportRefusal('transport envelope route mismatch')
    if value.get('provenance_class') != SYNTHETIC_PROVENANCE \
            or value.get('promotable') is not False:
        raise TransportRefusal('transport envelope is not synthetic/non-promotable')
    if value.get('failure_class') not in (None, *FAILURE_CLASSES):
        raise TransportRefusal('transport envelope failure class is invalid')
    if value.get('model_matches_request') is False and \
            value.get('failure_class') != 'model_substitution':
        raise TransportRefusal('model substitution is not classified')
    try:
        validate_accounting(value.get('accounting'))
    except ValueError as exc:
        raise TransportRefusal(str(exc)) from exc
    return value


def candidate_pass(envelope):
    verify_envelope(envelope)
    return bool(
        envelope.get('model_matches_request') is True
        and envelope.get('schema_compliant')
        and envelope.get('audit_passed')
        and envelope.get('accounting', {}).get('usage_evaluable') is True
        and envelope.get('failure_class') is None
    )
