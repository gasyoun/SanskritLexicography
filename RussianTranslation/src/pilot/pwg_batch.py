#!/usr/bin/env python
"""Sealed, credential-free preparation and resumable Anthropic Message Batches.

``prepare`` and ordinary ``check`` are strictly offline. Live subcommands use a
dependency-injected transport and refuse when no Anthropic credential exists.
Every emitted artifact is synthetic/non-promotable; this module never touches
the canonical store, translation memory, promotion journal, or route default.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone

from call_reservation import (
    CallLimitReached,
    CallReservationLedger,
    normalize_telemetry,
    unevaluable_telemetry,
)
from gateway_route import validate_complete_schema
from headless_worker import (
    build_fragment_prompt,
    build_prompt,
    fragment_prompt_blocks,
    prompt_blocks,
    validate_manifest,
)
from route_transport import atomic_json, canonical_hash, read_json, sha256_bytes
from usage_accounting import API_BATCH, build as build_accounting, legacy_telemetry


PLAN_SCHEMA = 'pwg.batch_plan.v1'
STATE_SCHEMA = 'pwg.batch_state.v1'
RESULT_SCHEMA = 'pwg.batch_result.v1'
SUPPORTED_MODELS = ('claude-sonnet-5', 'claude-opus-5')
DEFAULT_MAX_REQUESTS = 100
HARD_MAX_REQUESTS = 100_000
HARD_MAX_BYTES = 256 * 1024 * 1024
EXPIRY_HOURS = 24
RETENTION_DAYS = 29
CACHE_CONTROL = {'type': 'ephemeral', 'ttl': '1h'}
TOOL_NAME = 'emit_cards'
SECRETS_ENV = r'C:\Users\user\.secrets\anthropic.env'
PLAN_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'schemas', 'pwg_batch_plan.schema.json')


class BatchRefusal(RuntimeError):
    """Fail-closed batch contract refusal."""


def _now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _file_bytes(path):
    try:
        with open(path, 'rb') as handle:
            return handle.read()
    except OSError as exc:
        raise BatchRefusal('manifest unavailable: %s' % exc) from exc


def _manifest(path):
    payload = _file_bytes(path)
    try:
        value = json.loads(payload.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BatchRefusal('manifest is not valid UTF-8 JSON: %s' % exc) from exc
    if not isinstance(value, dict):
        raise BatchRefusal('manifest must be a JSON object')
    try:
        validate_manifest(value, require_v2=False)
    except (ValueError, KeyError) as exc:
        raise BatchRefusal('manifest validation failed: %s' % exc) from exc
    model = value.get('model')
    if model not in SUPPORTED_MODELS:
        raise BatchRefusal(
            'source manifest must explicitly name one supported model: %s'
            % ', '.join(SUPPORTED_MODELS))
    maximum = (value.get('runtime') or {}).get('max_output_tokens')
    if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum <= 0:
        raise BatchRefusal(
            'source manifest must explicitly declare runtime.max_output_tokens')
    return payload, value


def _custom_id(manifest_sha, wave, ordinal, work):
    suffix = canonical_hash({
        'manifest_sha256': manifest_sha,
        'wave': wave,
        'ordinal': ordinal,
        'work': work,
    })[:20]
    return 'pwg-w%02d-r%04d-%s' % (wave, ordinal, suffix)


def _request(manifest, manifest_sha, wave, ordinal, work, stable, volatile):
    if not stable or not isinstance(stable, str) or not isinstance(volatile, str):
        raise BatchRefusal('batch prompt blocks must be text with a non-empty stable prefix')
    schema = manifest.get('output_schema')
    try:
        validate_complete_schema({}, schema)
    except ValueError as exc:
        if 'output schema is invalid' in str(exc):
            raise BatchRefusal(str(exc)) from exc
    custom_id = _custom_id(manifest_sha, wave, ordinal, work)
    params = {
        'model': manifest['model'],
        'max_tokens': manifest['runtime']['max_output_tokens'],
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': stable,
                 'cache_control': dict(CACHE_CONTROL)},
                {'type': 'text', 'text': volatile},
            ],
        }],
        'tools': [{
            'name': TOOL_NAME,
            'description': 'Return PWG translation cards under the manifest schema.',
            'input_schema': schema,
        }],
        'tool_choice': {'type': 'tool', 'name': TOOL_NAME},
    }
    value = {
        'custom_id': custom_id,
        'work': work,
        'params': params,
        'prompt_sha256': sha256_bytes((stable + volatile).encode('utf-8')),
        'stable_prefix_sha256': sha256_bytes(stable.encode('utf-8')),
        'output_schema_sha256': canonical_hash(schema),
    }
    value['request_sha256'] = canonical_hash(value)
    return value


def _wave_zero_work(manifest):
    for batch_index, keys in enumerate(manifest.get('batches') or []):
        if keys:
            yield {
                'kind': 'whole', 'batch_index': batch_index,
                'keys': list(keys),
            }
    for key in manifest.get('presplit_keys') or []:
        groups = (manifest.get('fragment_groups') or {}).get(key) or []
        cached_groups = (manifest.get('fragment_tm') or {}).get(key) or []
        for group_index, group in enumerate(groups):
            cached = cached_groups[group_index] if group_index < len(cached_groups) else []
            indices = [index for index in range(len(group))
                       if index >= len(cached) or not cached[index]]
            if indices:
                yield {
                    'kind': 'fragment', 'key': key,
                    'group_index': group_index, 'indices': indices,
                    'keys': ['%s_f%d' % (key, index) for index in indices],
                }


def _blocks(manifest, work):
    if work['kind'] == 'whole':
        stable, volatile = prompt_blocks(manifest, work['keys'])
        if stable + volatile != build_prompt(manifest, work['keys']):
            raise BatchRefusal('whole prompt block concatenation changed prompt bytes')
        return stable, volatile
    key = work['key']
    groups = (manifest.get('fragment_groups') or {}).get(key) or []
    index = work['group_index']
    if index < 0 or index >= len(groups):
        raise BatchRefusal('fragment work references an absent group')
    group = groups[index]
    stable, volatile = fragment_prompt_blocks(manifest, key, group, work['indices'])
    if stable + volatile != build_fragment_prompt(
            manifest, key, group, work['indices']):
        raise BatchRefusal('fragment prompt block concatenation changed prompt bytes')
    return stable, volatile


def _estimate(requests):
    """Conservative visible-byte estimate, explicitly not tokenizer telemetry."""
    input_tokens = 0
    output_tokens = 0
    cache_write = 0
    cache_read = 0
    seen_prefixes = set()
    for request in requests:
        content = request['params']['messages'][0]['content']
        stable = content[0]['text']
        volatile = content[1]['text']
        stable_tokens = math.ceil(len(stable.encode('utf-8')) / 3)
        volatile_tokens = math.ceil(len(volatile.encode('utf-8')) / 3)
        input_tokens += volatile_tokens
        prefix = request['stable_prefix_sha256']
        if prefix in seen_prefixes:
            cache_read += stable_tokens
        else:
            cache_write += stable_tokens
            seen_prefixes.add(prefix)
        output_tokens += request['params']['max_tokens']
    accounting = build_accounting({
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'cache_creation_tokens': cache_write,
        'cache_read_tokens': cache_read,
    }, billing_mode=API_BATCH)
    return {
        'method': 'utf8_bytes_div_3_plus_declared_output_ceiling.v1',
        'input_tokens_upper_estimate': input_tokens,
        'output_tokens_upper_estimate': output_tokens,
        'cache_creation_tokens_estimate': cache_write,
        'cache_read_tokens_estimate': cache_read,
        'batch_cash_upper_estimate_usd': accounting['observed_cash_usd'],
        'pricing_policy': accounting['pricing_policy'],
    }


def compile_plan(manifest_path, *, max_requests=DEFAULT_MAX_REQUESTS,
                 cost_ceiling=10.0, wave=0, work_items=None):
    if (isinstance(max_requests, bool) or not isinstance(max_requests, int)
            or max_requests <= 0 or max_requests > HARD_MAX_REQUESTS):
        raise BatchRefusal('max_requests must be 1..100000')
    if isinstance(cost_ceiling, bool) or not isinstance(cost_ceiling, (int, float)) \
            or not 0 < cost_ceiling <= 10:
        raise BatchRefusal('observed-cash cost ceiling must be >0 and <=10')
    payload, manifest = _manifest(manifest_path)
    manifest_sha = sha256_bytes(payload)
    work = list(_wave_zero_work(manifest) if work_items is None else work_items)
    if len(work) > max_requests:
        raise BatchRefusal('batch plan exceeds project max_requests (%d > %d)'
                           % (len(work), max_requests))
    requests = []
    for ordinal, item in enumerate(work, start=1):
        stable, volatile = _blocks(manifest, item)
        requests.append(_request(
            manifest, manifest_sha, wave, ordinal, item, stable, volatile))
    estimate = _estimate(requests)
    if estimate['batch_cash_upper_estimate_usd'] > cost_ceiling:
        raise BatchRefusal(
            'estimated batch cash %.6f exceeds ceiling %.6f'
            % (estimate['batch_cash_upper_estimate_usd'], cost_ceiling))
    plan = {
        'schema': PLAN_SCHEMA,
        'wave': wave,
        'source_manifest_path': os.path.abspath(manifest_path),
        'source_manifest_sha256': manifest_sha,
        'model': manifest['model'],
        'max_output_tokens': manifest['runtime']['max_output_tokens'],
        'output_schema_sha256': canonical_hash(manifest['output_schema']),
        'requests': requests,
        'request_count': len(requests),
        'request_body_bytes': 0,
        'limits': {
            'project_max_requests': max_requests,
            'provider_max_requests': HARD_MAX_REQUESTS,
            'provider_max_request_bytes': HARD_MAX_BYTES,
            'expires_after_hours': EXPIRY_HOURS,
            'result_retention_days': RETENTION_DAYS,
            'observed_cash_cost_ceiling_usd': float(cost_ceiling),
        },
        'estimate': estimate,
        'cache_policy': {
            'ttl': '1h',
            'stable_segments': ['preamble', 'translation'],
            'volatile_segments': ['grammar', 'nws_rule', 'cards'],
        },
        'provenance_class': 'synthetic_control',
        'promotable': False,
        'production_default_changed': False,
        'store_write_authorized': False,
        'tm_write_authorized': False,
    }
    plan['request_body_bytes'] = len(json.dumps(
        {'requests': requests}, ensure_ascii=False,
        separators=(',', ':')).encode('utf-8'))
    if plan['request_body_bytes'] > HARD_MAX_BYTES:
        raise BatchRefusal('batch request body exceeds 256 MB provider limit')
    plan['plan_sha256'] = canonical_hash(plan)
    return verify_plan(plan)


def verify_plan(plan):
    if not isinstance(plan, dict) or plan.get('schema') != PLAN_SCHEMA:
        raise BatchRefusal('batch plan schema mismatch')
    copy = dict(plan)
    stated = copy.pop('plan_sha256', None)
    if canonical_hash(copy) != stated:
        raise BatchRefusal('batch plan self-hash mismatch')
    if plan.get('model') not in SUPPORTED_MODELS:
        raise BatchRefusal('batch plan model is not supported')
    requests = plan.get('requests')
    if not isinstance(requests, list) or len(requests) != plan.get('request_count'):
        raise BatchRefusal('batch plan request count mismatch')
    limits = plan.get('limits') or {}
    if len(requests) > limits.get('project_max_requests', 0) \
            or len(requests) > HARD_MAX_REQUESTS:
        raise BatchRefusal('batch plan request limit exceeded')
    ids = set()
    for request in requests:
        if not isinstance(request, dict):
            raise BatchRefusal('batch request is not an object')
        copied = dict(request)
        request_sha = copied.pop('request_sha256', None)
        if canonical_hash(copied) != request_sha:
            raise BatchRefusal('batch request self-hash mismatch')
        custom_id = request.get('custom_id')
        if not isinstance(custom_id, str) or not custom_id or len(custom_id) > 64 \
                or custom_id in ids:
            raise BatchRefusal('batch custom_id is invalid or duplicated')
        ids.add(custom_id)
        params = request.get('params') or {}
        if params.get('model') != plan['model'] \
                or params.get('max_tokens') != plan['max_output_tokens']:
            raise BatchRefusal('batch request changed manifest model/output limit')
        content = ((params.get('messages') or [{}])[0].get('content') or [])
        if len(content) != 2 or content[0].get('cache_control') != CACHE_CONTROL \
                or 'cache_control' in content[1]:
            raise BatchRefusal('batch cache block layout mismatch')
        if sha256_bytes((content[0].get('text', '') + content[1].get('text', '')).encode(
                'utf-8')) != request.get('prompt_sha256'):
            raise BatchRefusal('batch prompt hash mismatch')
        tools = params.get('tools') or []
        if len(tools) != 1 or tools[0].get('name') != TOOL_NAME \
                or params.get('tool_choice') != {'type': 'tool', 'name': TOOL_NAME}:
            raise BatchRefusal('batch structured output is not forced')
    body_bytes = len(json.dumps(
        {'requests': requests}, ensure_ascii=False,
        separators=(',', ':')).encode('utf-8'))
    if body_bytes != plan.get('request_body_bytes') or body_bytes > HARD_MAX_BYTES:
        raise BatchRefusal('batch request-byte accounting mismatch')
    if plan.get('promotable') is not False \
            or plan.get('production_default_changed') is not False \
            or plan.get('store_write_authorized') is not False \
            or plan.get('tm_write_authorized') is not False:
        raise BatchRefusal('batch plan violates non-promotable policy')
    return plan


def offline_check(plan_path):
    plan = verify_plan(read_json(plan_path, 'batch plan'))
    try:
        validate_complete_schema(
            plan, read_json(PLAN_SCHEMA_PATH, 'batch plan JSON schema'))
    except ValueError as exc:
        raise BatchRefusal('batch plan JSON Schema failure: %s' % exc) from exc
    payload, manifest = _manifest(plan['source_manifest_path'])
    if sha256_bytes(payload) != plan['source_manifest_sha256']:
        raise BatchRefusal('source manifest bytes changed after plan sealing')
    replay = compile_plan(
        plan['source_manifest_path'],
        max_requests=plan['limits']['project_max_requests'],
        cost_ceiling=plan['limits']['observed_cash_cost_ceiling_usd'],
        wave=plan['wave'],
        work_items=[request['work'] for request in plan['requests']],
    )
    if replay['plan_sha256'] != plan['plan_sha256']:
        raise BatchRefusal('batch plan is not replay deterministic')
    # ``_manifest`` already validates schema/model/limits. This explicit check
    # makes offline network-freedom testable through dependency injection.
    if manifest['model'] != plan['model']:
        raise BatchRefusal('manifest model no longer matches batch plan')
    return {
        'ok': True,
        'network_calls': 0,
        'credentials_required': False,
        'plan_sha256': plan['plan_sha256'],
        'request_count': plan['request_count'],
        'request_body_bytes': plan['request_body_bytes'],
        'batch_cash_upper_estimate_usd': plan['estimate'][
            'batch_cash_upper_estimate_usd'],
    }


def _credential():
    for name in ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN'):
        value = (os.environ.get(name) or '').strip()
        if value:
            return value, name
    if os.path.isfile(SECRETS_ENV):
        with open(SECRETS_ENV, encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                name, _, value = line.partition('=')
                if name.strip() in ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN') \
                        and value.strip().strip('"').strip("'"):
                    return value.strip().strip('"').strip("'"), name.strip()
    return None, None


class AnthropicBatchTransport:
    """Thin SDK boundary; tests inject an in-memory transport instead."""

    def __init__(self, client):
        self.client = client

    @classmethod
    def from_environment(cls):
        secret, _source = _credential()
        if not secret:
            raise BatchRefusal('Anthropic batch command unavailable: no credential')
        try:
            import anthropic
        except ImportError as exc:
            raise BatchRefusal('Anthropic SDK is not installed') from exc
        return cls(anthropic.Anthropic(api_key=secret))

    def check(self, model):
        info = self.client.models.retrieve(model)
        returned = getattr(info, 'id', None)
        return {'authenticated': True, 'model_available': returned == model,
                'returned_model': returned}

    def create(self, requests):
        return self.client.messages.batches.create(requests=requests).model_dump()

    def retrieve(self, batch_id):
        return self.client.messages.batches.retrieve(batch_id).model_dump()

    def results(self, batch_id):
        rows = self.client.messages.batches.results(batch_id)
        return [row.model_dump() if hasattr(row, 'model_dump') else row for row in rows]


def live_check(plan_path, transport=None):
    plan = verify_plan(read_json(plan_path, 'batch plan'))
    transport = transport or AnthropicBatchTransport.from_environment()
    try:
        result = transport.check(plan['model'])
    except Exception as exc:  # noqa: BLE001 - public typed summary only
        raise BatchRefusal('live authentication/model check failed: %s' % type(exc).__name__) from exc
    if not isinstance(result, dict) or not result.get('authenticated') \
            or not result.get('model_available') \
            or result.get('returned_model') != plan['model']:
        raise BatchRefusal('live check did not attest the exact manifest model')
    return result


def _state_path(plan_path, state_path):
    return os.path.abspath(state_path or (plan_path + '.state.json'))


def _ledger_path(plan_path, ledger_path):
    return os.path.abspath(ledger_path or (plan_path + '.reservations.json'))


def _load_state(path, plan):
    if not os.path.isfile(path):
        return None
    value = read_json(path, 'batch state')
    copied = dict(value)
    stated = copied.pop('state_sha256', None)
    if canonical_hash(copied) != stated:
        raise BatchRefusal('batch state self-hash mismatch')
    if value.get('schema') != STATE_SCHEMA \
            or value.get('plan_sha256') != plan['plan_sha256']:
        raise BatchRefusal('batch state/plan binding mismatch')
    return value


def _write_state(path, value):
    copied = dict(value)
    copied.pop('state_sha256', None)
    copied['state_sha256'] = canonical_hash(copied)
    return atomic_json(path, copied)


def _provider_id(response):
    if isinstance(response, dict):
        value = response.get('id')
        if isinstance(value, str) and value:
            return value
    return None


def submit(plan_path, *, state_path=None, ledger_path=None, transport=None, ledger=None):
    plan = verify_plan(read_json(plan_path, 'batch plan'))
    state_path = _state_path(plan_path, state_path)
    ledger_path = _ledger_path(plan_path, ledger_path)
    state = _load_state(state_path, plan)
    if state:
        if state.get('status') == 'ambiguous_submit':
            raise BatchRefusal(
                'ambiguous_submit: operator reconciliation required; automatic retry forbidden')
        if state.get('provider_batch_id'):
            return state
        raise BatchRefusal('submission intent already persisted without provider batch id')
    ledger = ledger or CallReservationLedger(
        ledger_path, plan['plan_sha256'], max_calls=plan['request_count'])
    reservations = []
    try:
        for request in plan['requests']:
            reservations.append(ledger.reserve(
                'batch:%s' % request['work']['kind'], profile=plan['model'],
                detail=request['custom_id'], idempotency_key=request['request_sha256']))
    except CallLimitReached as exc:
        raise BatchRefusal('reservation_exhausted: %s' % exc) from exc
    state = {
        'schema': STATE_SCHEMA,
        'plan_sha256': plan['plan_sha256'],
        'status': 'submission_intent',
        'submission_intent_at': _now(),
        'provider_batch_id': None,
        'reservations': {
            request['custom_id']: reservation['reservation_id']
            for request, reservation in zip(plan['requests'], reservations)
        },
        'terminal_custom_ids': [],
        'result_hashes': {},
    }
    _write_state(state_path, state)  # durable intent before irreversible create
    transport = transport or AnthropicBatchTransport.from_environment()
    try:
        response = transport.create([
            {'custom_id': request['custom_id'], 'params': request['params']}
            for request in plan['requests']])
        batch_id = _provider_id(response)
        if batch_id is None:
            raise ValueError('create response has no provider batch id')
    except BaseException as exc:  # noqa: BLE001 - create may have succeeded remotely
        state['status'] = 'ambiguous_submit'
        state['ambiguous_submit_at'] = _now()
        state['error_class'] = type(exc).__name__
        _write_state(state_path, state)
        raise BatchRefusal(
            'ambiguous_submit: create response cannot be retried automatically') from exc
    state['status'] = 'submitted'
    state['provider_batch_id'] = batch_id
    state['submitted_at'] = _now()
    _write_state(state_path, state)
    return state


def status(plan_path, *, state_path=None, transport=None):
    plan = verify_plan(read_json(plan_path, 'batch plan'))
    state_path = _state_path(plan_path, state_path)
    state = _load_state(state_path, plan)
    if not state or not state.get('provider_batch_id'):
        raise BatchRefusal('batch has not been unambiguously submitted')
    transport = transport or AnthropicBatchTransport.from_environment()
    try:
        provider = transport.retrieve(state['provider_batch_id'])
    except Exception as exc:  # noqa: BLE001
        raise BatchRefusal('batch status failed: %s' % type(exc).__name__) from exc
    state['provider_status'] = provider
    state['status_checked_at'] = _now()
    _write_state(state_path, state)
    return state


def _tool_result(message):
    if not isinstance(message, dict):
        raise ValueError('succeeded batch result has no message object')
    blocks = message.get('content')
    matches = [block for block in blocks or [] if isinstance(block, dict)
               and block.get('type') == 'tool_use' and block.get('name') == TOOL_NAME]
    if len(matches) != 1 or not isinstance(matches[0].get('input'), dict):
        raise ValueError('expected exactly one structured emit_cards tool result')
    return matches[0]['input']


def _terminal_accounting(result_type, message):
    if result_type == 'succeeded':
        raw = message.get('usage') if isinstance(message, dict) else None
        if not isinstance(raw, dict):
            return None
        usage = {
            'input_tokens': raw.get('input_tokens'),
            'output_tokens': raw.get('output_tokens'),
            'cache_creation_tokens': raw.get('cache_creation_input_tokens', 0),
            'cache_read_tokens': raw.get('cache_read_input_tokens', 0),
        }
        accounting = build_accounting(usage, billing_mode=API_BATCH)
        return accounting if accounting['usage_evaluable'] else None
    # Anthropic documents terminal errored/canceled/expired requests as not
    # billed when the result evidence says no message ran. Preserve explicit 0.
    return build_accounting({
        'input_tokens': 0, 'output_tokens': 0,
        'cache_creation_tokens': 0, 'cache_read_tokens': 0,
    }, billing_mode=API_BATCH, observed_cash_usd=0)


def _result_envelope(plan, request, provider_row):
    result = provider_row.get('result') if isinstance(provider_row, dict) else None
    result_type = result.get('type') if isinstance(result, dict) else None
    if result_type not in ('succeeded', 'errored', 'canceled', 'expired'):
        raise BatchRefusal('provider result has unknown terminal type')
    message = result.get('message') if result_type == 'succeeded' else None
    accounting = _terminal_accounting(result_type, message)
    structured = None
    schema_compliant = False
    failure_class = None
    error = None
    returned_model = message.get('model') if isinstance(message, dict) else None
    if result_type == 'succeeded':
        if returned_model != plan['model']:
            failure_class = 'model_substitution'
            error = 'returned model differs from manifest model'
        else:
            try:
                structured = _tool_result(message)
                validate_complete_schema(
                    structured, request['params']['tools'][0]['input_schema'])
                schema_compliant = True
            except ValueError as exc:
                failure_class = ('malformed_output' if structured is None
                                 else 'schema_failure')
                error = str(exc)
        if accounting is None and failure_class is None:
            failure_class = 'unevaluable_cost'
            error = 'succeeded result usage is absent or malformed'
    else:
        failure_class = 'timeout' if result_type == 'expired' else 'transport_error'
        error = str(result.get('error') or result_type)[:500]
    envelope = {
        'schema': RESULT_SCHEMA,
        'plan_sha256': plan['plan_sha256'],
        'custom_id': request['custom_id'],
        'request_sha256': request['request_sha256'],
        'terminal_type': result_type,
        'requested_model': plan['model'],
        'returned_model': returned_model,
        'model_matches_request': returned_model == plan['model']
        if returned_model is not None else None,
        'usage_evaluable': bool(accounting and accounting['usage_evaluable']),
        'accounting': accounting,
        'schema_compliant': schema_compliant,
        'audit_status': 'pending_local_pwg_audit' if schema_compliant else 'not_eligible',
        'failure_class': failure_class,
        'error': error,
        'result': structured,
        'result_sha256': canonical_hash(structured) if structured is not None else None,
        'provenance_class': 'synthetic_control',
        'promotable': False,
    }
    envelope['envelope_sha256'] = canonical_hash(envelope)
    return envelope


def _unresolved_work(request, envelope):
    if envelope['terminal_type'] != 'succeeded' or not envelope['schema_compliant']:
        return [request['work']]
    expected = list(request['work'].get('keys') or [])
    cards = envelope['result'].get('cards') or []
    returned = {(card.get('key') or card.get('key1')) for card in cards
                if isinstance(card, dict)}
    missing = [key for key in expected if key not in returned]
    if not missing:
        return []
    if request['work']['kind'] == 'whole':
        return [{'kind': 'whole', 'batch_index': request['work'].get('batch_index'),
                 'keys': missing}]
    indices = [int(key.rsplit('_f', 1)[1]) for key in missing]
    return [{**request['work'], 'indices': indices, 'keys': missing}]


def fetch(plan_path, *, state_path=None, ledger_path=None, out_dir=None,
          next_plan_path=None, transport=None, ledger=None):
    plan = verify_plan(read_json(plan_path, 'batch plan'))
    state_path = _state_path(plan_path, state_path)
    ledger_path = _ledger_path(plan_path, ledger_path)
    state = _load_state(state_path, plan)
    if not state or not state.get('provider_batch_id'):
        raise BatchRefusal('batch has not been unambiguously submitted')
    transport = transport or AnthropicBatchTransport.from_environment()
    try:
        provider_rows = list(transport.results(state['provider_batch_id']))
    except Exception as exc:  # noqa: BLE001
        raise BatchRefusal('batch result fetch failed: %s' % type(exc).__name__) from exc
    by_id = {}
    for row in provider_rows:
        custom_id = row.get('custom_id') if isinstance(row, dict) else None
        if custom_id in by_id:
            raise BatchRefusal('provider returned duplicate custom_id')
        by_id[custom_id] = row
    expected = {request['custom_id'] for request in plan['requests']}
    if set(by_id) != expected:
        raise BatchRefusal('provider results do not exactly match planned custom_ids')
    ledger = ledger or CallReservationLedger.open_existing(
        ledger_path, plan['plan_sha256'])
    snapshot = ledger.snapshot()
    by_reservation = {row['reservation_id']: row for row in snapshot['reservations']}
    out_dir = os.path.abspath(out_dir or (plan_path + '.results'))
    os.makedirs(out_dir, exist_ok=True)
    envelopes = []
    unresolved = []
    for request in plan['requests']:
        envelope = _result_envelope(plan, request, by_id[request['custom_id']])
        destination = os.path.join(out_dir, request['custom_id'] + '.json')
        if os.path.isfile(destination):
            existing = read_json(destination, 'batch result envelope')
            if existing.get('envelope_sha256') != envelope['envelope_sha256']:
                raise BatchRefusal('exact-once result replay changed sealed evidence')
        else:
            atomic_json(destination, envelope)
        reservation_id = state['reservations'][request['custom_id']]
        reservation = by_reservation[reservation_id]
        telemetry = (legacy_telemetry(envelope['accounting'])
                     if envelope['accounting'] is not None else unevaluable_telemetry())
        ledger.finalize(reservation, telemetry, evidence={
            'schema': 'pwg.batch_finalization.v1',
            'custom_id': request['custom_id'],
            'terminal_type': envelope['terminal_type'],
            'envelope_sha256': envelope['envelope_sha256'],
        })
        state['result_hashes'][request['custom_id']] = envelope['envelope_sha256']
        envelopes.append(envelope)
        unresolved.extend(_unresolved_work(request, envelope))
    state['terminal_custom_ids'] = sorted(expected)
    state['status'] = 'fetched'
    state['fetched_at'] = _now()
    state['unresolved_work_count'] = len(unresolved)
    if next_plan_path and unresolved:
        next_plan = compile_plan(
            plan['source_manifest_path'],
            max_requests=plan['limits']['project_max_requests'],
            cost_ceiling=plan['limits']['observed_cash_cost_ceiling_usd'],
            wave=plan['wave'] + 1, work_items=unresolved)
        if os.path.exists(next_plan_path):
            old = verify_plan(read_json(next_plan_path, 'existing heal-wave plan'))
            if old['plan_sha256'] != next_plan['plan_sha256']:
                raise BatchRefusal('existing heal-wave plan differs from deterministic replay')
        else:
            atomic_json(next_plan_path, next_plan)
        state['next_plan_sha256'] = next_plan['plan_sha256']
    _write_state(state_path, state)
    return {'state': state, 'results': envelopes, 'unresolved_work': unresolved}


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare')
    prepare.add_argument('--manifest', required=True)
    prepare.add_argument('--out', required=True)
    prepare.add_argument('--max-requests', type=int, default=DEFAULT_MAX_REQUESTS)
    prepare.add_argument('--cost-ceiling', type=float, default=10.0)
    check = commands.add_parser('check')
    check.add_argument('--plan', required=True)
    check.add_argument('--live', action='store_true')
    for name in ('submit', 'status', 'fetch'):
        command = commands.add_parser(name)
        command.add_argument('--plan', required=True)
        command.add_argument('--state')
        if name in ('submit', 'fetch'):
            command.add_argument('--ledger')
        if name == 'fetch':
            command.add_argument('--out')
            command.add_argument('--next-plan')
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        if args.command == 'prepare':
            plan = compile_plan(
                args.manifest, max_requests=args.max_requests,
                cost_ceiling=args.cost_ceiling)
            if os.path.exists(args.out):
                old = verify_plan(read_json(args.out, 'existing batch plan'))
                if old['plan_sha256'] != plan['plan_sha256']:
                    raise BatchRefusal('existing output differs from deterministic plan')
            else:
                atomic_json(args.out, plan)
            result = {'ok': True, 'plan_sha256': plan['plan_sha256'],
                      'request_count': plan['request_count']}
        elif args.command == 'check':
            result = offline_check(args.plan)
            if args.live:
                result['live'] = live_check(args.plan)
        elif args.command == 'submit':
            result = submit(args.plan, state_path=args.state, ledger_path=args.ledger)
        elif args.command == 'status':
            result = status(args.plan, state_path=args.state)
        else:
            result = fetch(
                args.plan, state_path=args.state, ledger_path=args.ledger,
                out_dir=args.out, next_plan_path=args.next_plan)['state']
    except BatchRefusal as exc:
        print('REFUSED: %s' % exc, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
