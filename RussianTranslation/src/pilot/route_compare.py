#!/usr/bin/env python
"""Resumable three-reservation PWG transport qualification.

Order is fixed: router.cheap capability -> router.cheap frozen canary -> the
same canary through Anthropic Messages.  The gateway remains an external Agent
dispatch; rerun this command after placing each response and exact-dispatch
attestation in the output directory.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import anthropic_messages_route as amr  # noqa: E402
import gateway_canary_contract as canary  # noqa: E402
import gateway_external as gex  # noqa: E402
from call_reservation import CallReservationLedger  # noqa: E402
from execution_contract import PRODUCTION_HARD_TIMEOUT_MS  # noqa: E402
from route_transport import (  # noqa: E402
    ANTHROPIC_ROUTE,
    COMPARISON_SCHEMA,
    GATEWAY_ROUTE,
    TransportRefusal,
    atomic_json,
    audit_canary,
    build_request,
    candidate_pass,
    canonical_hash,
    file_sha256,
    read_json,
    seal_envelope,
    verify_envelope,
    verify_request,
)


MODEL = 'claude-opus-5'
MAX_CALLS = 3
COST_CEILING_USD = 10.0
MAX_OUTPUT_TOKENS = 2048
SOURCE_MANIFEST = os.path.join(
    REPO, 'pwg_ru', 'h994', 'canary',
    'dq_canary_puregloss~~h0_zz_pw.manifest.v2.json')
CAPABILITY_REQUEST = os.path.join(
    REPO, 'pwg_ru', 'h2539', 'evidence', 't1_request.json')
CAPABILITY_SCHEMA = os.path.join(
    REPO, 'pwg_ru', 'h2539', 'evidence', 't1_schema.json')


def paths(out):
    root = os.path.abspath(out)
    return {
        'root': root,
        'ledger': os.path.join(root, 'call_reservation.json'),
        'preflight': os.path.join(root, 'preflight.json'),
        'receipt': os.path.join(root, 'route_comparison.json'),
        't1_request': os.path.join(root, 't1_request.json'),
        't1_schema': os.path.join(root, 't1_schema.json'),
        't1_transport': os.path.join(root, 't1_transport_request.json'),
        't1_ticket': os.path.join(root, 't1_ticket.json'),
        't1_response': os.path.join(root, 't1_response.json'),
        't1_attestation': os.path.join(root, 't1_attestation.json'),
        't1_gateway_envelope': os.path.join(root, 't1_gateway_envelope.json'),
        't1_envelope': os.path.join(root, 't1_transport_envelope.json'),
        't2_request': os.path.join(root, 't2_request.json'),
        't2_schema': os.path.join(root, 't2_schema.json'),
        't2_transport': os.path.join(root, 't2_transport_request.json'),
        't2_ticket': os.path.join(root, 't2_ticket.json'),
        't2_response': os.path.join(root, 't2_response.json'),
        't2_attestation': os.path.join(root, 't2_attestation.json'),
        't2_gateway_envelope': os.path.join(root, 't2_gateway_envelope.json'),
        't2_envelope': os.path.join(root, 't2_transport_envelope.json'),
        'anthropic_envelope': os.path.join(root, 'anthropic_transport_envelope.json'),
    }


def _write_immutable(path, value, label):
    if os.path.isfile(path):
        existing = read_json(path, label)
        if existing != value:
            raise TransportRefusal('%s differs from the sealed comparison run' % label)
        return existing
    return atomic_json(path, value)


def build_requests(model=MODEL, manifest_path=SOURCE_MANIFEST,
                   timeout_ms=PRODUCTION_HARD_TIMEOUT_MS,
                   max_output_tokens=MAX_OUTPUT_TOKENS):
    if model != MODEL:
        raise TransportRefusal('comparison requires exact %s' % MODEL)
    manifest_sha = file_sha256(manifest_path)
    capability_request = read_json(CAPABILITY_REQUEST, 'frozen capability request')
    capability_schema = read_json(CAPABILITY_SCHEMA, 'frozen capability schema')
    canary_request, canary_schema = canary.request_and_schema()
    t1 = build_request(
        prompt=capability_request['prompt'], output_schema=capability_schema,
        requested_model=model, purpose='transport_compare:gateway_capability',
        manifest_sha256=manifest_sha, hard_timeout_ms=timeout_ms,
        max_output_tokens=max_output_tokens)
    t2 = build_request(
        prompt=canary_request['prompt'], output_schema=canary_schema,
        requested_model=model, purpose='transport_compare:frozen_canary',
        manifest_sha256=manifest_sha, hard_timeout_ms=timeout_ms,
        max_output_tokens=max_output_tokens)
    return t1, t2


def offline_check(client=None, model=MODEL, manifest_path=SOURCE_MANIFEST,
                  check_auth=True):
    t1, t2 = build_requests(model=model, manifest_path=manifest_path)
    derived = canary.prompt_derived_instance(t2['prompt'])
    audit_ok, reasons = audit_canary(derived, t2['output_schema'])
    auth = {'authenticated': None, 'model_available': None,
            'reason': 'skipped'}
    if check_auth:
        if client is None:
            client, _ = amr.api_client()
        auth = amr.check_auth_and_model(client, model)
    return {
        'schema': 'pwg.route_comparison_preflight.v1',
        'model': model,
        'manifest_path': os.path.abspath(manifest_path),
        'manifest_sha256': t2['manifest_sha256'],
        'canary_prompt_sha256': t2['prompt_sha256'],
        'canary_schema_sha256': t2['output_schema_sha256'],
        'gateway_anthropic_prompt_identical': True,
        'gateway_anthropic_schema_identical': True,
        'canary_audit_passed': audit_ok,
        'canary_audit_reasons': reasons,
        'capability_request_sha256': t1['request_sha256'],
        'canary_request_sha256': t2['request_sha256'],
        'anthropic': auth,
        'offline_passed': bool(
            audit_ok and (not check_auth or (
                auth.get('authenticated') and auth.get('model_available')))),
    }


def verify_preflight(value, t1, t2, require_auth=True):
    """Bind execution to the exact successful offline qualification."""
    if not isinstance(value, dict) or \
            value.get('schema') != 'pwg.route_comparison_preflight.v1':
        raise TransportRefusal('comparison preflight schema mismatch')
    expected = {
        'model': t2['requested_model'],
        'manifest_sha256': t2['manifest_sha256'],
        'capability_request_sha256': t1['request_sha256'],
        'canary_request_sha256': t2['request_sha256'],
        'canary_prompt_sha256': t2['prompt_sha256'],
        'canary_schema_sha256': t2['output_schema_sha256'],
    }
    for name, wanted in expected.items():
        if value.get(name) != wanted:
            raise TransportRefusal('comparison preflight %s mismatch' % name)
    if value.get('offline_passed') is not True:
        raise TransportRefusal('comparison preflight did not pass')
    auth = value.get('anthropic') or {}
    if require_auth and not (
            auth.get('authenticated') is True
            and auth.get('model_available') is True):
        raise TransportRefusal('comparison preflight lacks Anthropic auth/model evidence')
    return value


def _materialize(p, t1, t2):
    _write_immutable(p['t1_request'], {'prompt': t1['prompt']}, 'T1 request')
    _write_immutable(p['t1_schema'], t1['output_schema'], 'T1 schema')
    _write_immutable(p['t1_transport'], t1, 'T1 transport request')
    _write_immutable(p['t2_request'], {'prompt': t2['prompt']}, 'T2 request')
    _write_immutable(p['t2_schema'], t2['output_schema'], 'T2 schema')
    _write_immutable(p['t2_transport'], t2, 'T2 transport request')


def _verify_gateway_saved(envelope):
    if envelope.get('schema') != gex.ENVELOPE_SCHEMA:
        raise TransportRefusal('gateway envelope schema mismatch')
    copied = dict(envelope)
    stated = copied.pop('saved_envelope_sha256', None)
    if canonical_hash(copied) != stated:
        raise TransportRefusal('gateway envelope self-hash mismatch')
    if envelope.get('route') != GATEWAY_ROUTE:
        raise TransportRefusal('gateway envelope route mismatch')
    if envelope.get('promotable') is not False:
        raise TransportRefusal('gateway qualification envelope became promotable')
    return envelope


def normalize_gateway(envelope, ticket, request, capability=False):
    """Adapt the released external envelope to the shared transport contract."""
    _verify_gateway_saved(envelope)
    verify_request(request)
    if envelope.get('run_id') != ticket.get('run_id'):
        raise TransportRefusal('gateway run binding mismatch')
    if envelope.get('reservation_id') != ticket.get('reservation_id'):
        raise TransportRefusal('gateway reservation binding mismatch')
    if envelope.get('request_sha256') != canonical_hash({'prompt': request['prompt']}):
        raise TransportRefusal('gateway prompt binding mismatch')
    if envelope.get('schema_sha256') != request['output_schema_sha256']:
        raise TransportRefusal('gateway schema binding mismatch')
    if envelope.get('requested_model') != request['requested_model']:
        raise TransportRefusal('gateway requested-model binding mismatch')
    if ticket.get('max_output_tokens') != request['max_output_tokens']:
        raise TransportRefusal('gateway output-limit binding mismatch')

    result = envelope.get('result')
    if capability and envelope.get('schema_compliant'):
        audit_passed, audit_reasons = True, []
    elif result is not None:
        audit_passed, audit_reasons = audit_canary(result, request['output_schema'])
    else:
        audit_passed, audit_reasons = False, ['no_result']
    schema_compliant = bool(envelope.get('schema_compliant'))
    model_ok = bool(
        envelope.get('dispatch_attested')
        and envelope.get('attestation_scope') == 'dispatch'
        and envelope.get('model_attested')
        and envelope.get('model_matches_request') is True)
    cost_evaluable = envelope.get('cost_evaluable') is True

    failure = None
    error = envelope.get('error')
    source_failure = envelope.get('failure_class')
    if not model_ok:
        failure = 'model_substitution'
        error = error or 'gateway model/dispatch attestation is absent or mismatched'
    elif not schema_compliant:
        failure = ('timeout' if source_failure == 'timeout'
                   else 'malformed_output' if source_failure == 'empty_output'
                   else 'schema_failure')
    elif not audit_passed:
        failure = 'content_audit_failure'
        error = error or '; '.join(audit_reasons)
    usage = envelope.get('attested_usage_totals') or envelope.get('ledger_telemetry') or {}
    reservation = {
        'reservation_id': ticket['reservation_id'],
        'ordinal': ticket['reservation_ordinal'],
    }
    return seal_envelope(
        route=GATEWAY_ROUTE, request=request, run_id=ticket['run_id'],
        reservation=reservation, returned_model=envelope.get('attested_model'),
        wall_ms=envelope.get('wall_ms'), usage=usage,
        cost_evaluable=cost_evaluable,
        observed_cost_usd=envelope.get('observed_cost_usd'),
        result=result, schema_compliant=schema_compliant,
        audit_passed=audit_passed, audit_reasons=audit_reasons,
        failure_class=failure, error=error,
        source_envelope_sha256=envelope['saved_envelope_sha256'],
        dispatch_id=envelope.get('dispatch_id'),
        dispatch_attested=envelope.get('dispatch_attested'))


def _record_gateway_if_ready(p, prefix, run_id):
    envelope_path = p['%s_gateway_envelope' % prefix]
    if os.path.isfile(envelope_path):
        return read_json(envelope_path, '%s gateway envelope' % prefix.upper())
    response = p['%s_response' % prefix]
    attestation = p['%s_attestation' % prefix]
    if not os.path.isfile(response) or not os.path.isfile(attestation):
        return None
    return gex.record_external(
        ticket_path=p['%s_ticket' % prefix], ledger_path=p['ledger'],
        run_id=run_id, response_path=response,
        schema_path=p['%s_schema' % prefix], envelope_path=envelope_path,
        attestation_path=attestation)


def _prepare_gateway(p, prefix, run_id, request):
    return gex.prepare_external(
        ledger_path=p['ledger'], run_id=run_id, max_calls=MAX_CALLS,
        purpose=request['purpose'], requested_model=request['requested_model'],
        request_path=p['%s_request' % prefix], schema_path=p['%s_schema' % prefix],
        ticket_path=p['%s_ticket' % prefix], timeout_ms=request['hard_timeout_ms'],
        max_output_tokens=request['max_output_tokens'])


def choose_candidate(gateway, anthropic):
    candidates = [row for row in (gateway, anthropic) if candidate_pass(row)]
    if not candidates:
        return None, 'neither route passed'
    if len(candidates) == 1:
        return candidates[0]['route'], 'only passing route'
    by_route = {row['route']: row for row in candidates}
    gw = by_route[GATEWAY_ROUTE]
    api = by_route[ANTHROPIC_ROUTE]
    gw_wall, api_wall = gw.get('wall_ms'), api.get('wall_ms')
    if isinstance(gw_wall, (int, float)) and isinstance(api_wall, (int, float)):
        slower = max(gw_wall, api_wall)
        if slower and abs(gw_wall - api_wall) / slower > 0.10:
            return (GATEWAY_ROUTE if gw_wall < api_wall else ANTHROPIC_ROUTE,
                    'wall time differs by more than 10%')
    gw_cost, api_cost = gw.get('observed_cost_usd'), api.get('observed_cost_usd')
    if isinstance(gw_cost, (int, float)) and isinstance(api_cost, (int, float)):
        pricier = max(gw_cost, api_cost)
        if pricier and abs(gw_cost - api_cost) / pricier > 0.10:
            return (GATEWAY_ROUTE if gw_cost < api_cost else ANTHROPIC_ROUTE,
                    'observed cost differs by more than 10%')
    return GATEWAY_ROUTE, 'within 10% tie; deterministic gateway preference'


def _receipt(run_id, status, verdict, candidate, reason, t1, t2, calls,
             evidence, cost_ceiling=COST_CEILING_USD):
    value = {
        'schema': COMPARISON_SCHEMA,
        'run_id': run_id,
        'status': status,
        'verdict': verdict,
        'candidate_route': candidate,
        'selection_reason': reason,
        'limits': {
            'max_calls': MAX_CALLS,
            'observed_cash_cost_ceiling_usd': cost_ceiling,
        },
        'contract': {
            'manifest_sha256': t2['manifest_sha256'],
            'capability_request_sha256': t1['request_sha256'],
            'canary_request_sha256': t2['request_sha256'],
            'canary_prompt_sha256': t2['prompt_sha256'],
            'canary_schema_sha256': t2['output_schema_sha256'],
            'requested_model': MODEL,
            'max_output_tokens': t2['max_output_tokens'],
        },
        'calls': calls,
        'evidence': evidence,
        'promotable': False,
        'production_default_changed': False,
        'cli_fallback_preserved': True,
    }
    value['receipt_sha256'] = canonical_hash(value)
    return value


def _publish(p, *args, **kwargs):
    calls = args[7]
    artifact_by_purpose = {
        'transport_compare:gateway_capability': p['t1_envelope'],
        'transport_compare:frozen_canary': p['t2_envelope'],
    }
    evidence = []
    gateway_canary_seen = False
    for row in calls:
        if row['route'] == ANTHROPIC_ROUTE:
            artifact = p['anthropic_envelope']
        elif row['purpose'] == 'transport_compare:frozen_canary' and not gateway_canary_seen:
            artifact = p['t2_envelope']
            gateway_canary_seen = True
        else:
            artifact = artifact_by_purpose[row['purpose']]
        evidence.append({
            'artifact': os.path.basename(artifact),
            'envelope_sha256': row['envelope_sha256'],
            'route': row['route'],
            'purpose': row['purpose'],
        })
    value = _receipt(*args, evidence=evidence, **kwargs)
    verify_receipt(value)
    atomic_json(p['receipt'], value)
    return value


def verify_receipt(value):
    if not isinstance(value, dict) or value.get('schema') != COMPARISON_SCHEMA:
        raise TransportRefusal('comparison receipt schema mismatch')
    copied = dict(value)
    stated = copied.pop('receipt_sha256', None)
    if canonical_hash(copied) != stated:
        raise TransportRefusal('comparison receipt self-hash mismatch')
    calls = value.get('calls')
    evidence = value.get('evidence')
    if not isinstance(calls, list) or len(calls) > MAX_CALLS:
        raise TransportRefusal('comparison receipt call count is invalid')
    if not isinstance(evidence, list) or len(evidence) != len(calls):
        raise TransportRefusal('comparison evidence references are incomplete')
    for row, ref in zip(calls, evidence):
        verify_envelope(row)
        if ref.get('envelope_sha256') != row['envelope_sha256'] or \
                ref.get('route') != row['route'] or \
                ref.get('purpose') != row['purpose']:
            raise TransportRefusal('comparison evidence binding mismatch')
    if value.get('promotable') is not False or \
            value.get('production_default_changed') is not False or \
            value.get('cli_fallback_preserved') is not True:
        raise TransportRefusal('comparison receipt violates qualification-only policy')
    return value


def execute(*, out, run_id, model=MODEL, max_calls=MAX_CALLS,
            cost_ceiling=COST_CEILING_USD, transport=None, preflight=None):
    if max_calls != MAX_CALLS:
        raise TransportRefusal('comparison requires exactly --max-calls 3')
    if cost_ceiling > COST_CEILING_USD or cost_ceiling <= 0:
        raise TransportRefusal('cost ceiling must be >0 and <= $10')
    p = paths(out)
    os.makedirs(p['root'], exist_ok=True)
    t1, t2 = build_requests(model=model)
    if preflight is None:
        preflight = read_json(p['preflight'], 'successful comparison preflight')
        require_auth = True
    else:
        require_auth = False  # dependency-injected hermetic execution
    verify_preflight(preflight, t1, t2, require_auth=require_auth)
    _materialize(p, t1, t2)
    ledger = CallReservationLedger(p['ledger'], run_id, max_calls)
    calls = []

    _prepare_gateway(p, 't1', run_id, t1)
    source1 = _record_gateway_if_ready(p, 't1', run_id)
    if source1 is None:
        return _publish(
            p, run_id, 'awaiting_gateway_capability', 'INCOMPLETE', None,
            'dispatch T1 from its immutable ticket, then save response+attestation',
            t1, t2, calls, cost_ceiling=cost_ceiling)
    ticket1 = read_json(p['t1_ticket'], 'T1 ticket')
    common1 = normalize_gateway(source1, ticket1, t1, capability=True)
    _write_immutable(p['t1_envelope'], common1, 'T1 transport envelope')
    calls.append(common1)
    if not candidate_pass(common1):
        return _publish(
            p, run_id, 'complete', 'NO-GO', None,
            'gateway capability failed: %s' % common1.get('failure_class'),
            t1, t2, calls, cost_ceiling=cost_ceiling)

    _prepare_gateway(p, 't2', run_id, t2)
    source2 = _record_gateway_if_ready(p, 't2', run_id)
    if source2 is None:
        return _publish(
            p, run_id, 'awaiting_gateway_canary', 'INCOMPLETE', None,
            'dispatch T2 from its immutable ticket, then save response+attestation',
            t1, t2, calls, cost_ceiling=cost_ceiling)
    ticket2 = read_json(p['t2_ticket'], 'T2 ticket')
    common2 = normalize_gateway(source2, ticket2, t2, capability=False)
    _write_immutable(p['t2_envelope'], common2, 'T2 transport envelope')
    calls.append(common2)
    known_cost = sum(row.get('observed_cost_usd') or 0 for row in calls)
    if known_cost > cost_ceiling:
        return _publish(
            p, run_id, 'complete', 'NO-GO', None,
            'observed cost ceiling reached before Anthropic call',
            t1, t2, calls, cost_ceiling=cost_ceiling)

    if transport is None:
        client, _ = amr.api_client()
        auth = amr.check_auth_and_model(client, model)
        if not auth.get('authenticated') or not auth.get('model_available'):
            return _publish(
                p, run_id, 'complete', 'NO-GO', None,
                'Anthropic authentication/model check failed: %s' % auth.get('reason'),
                t1, t2, calls, cost_ceiling=cost_ceiling)
        transport = amr.sdk_transport(client)
    anthropic = amr.AnthropicMessagesCall(ledger, transport).invoke(
        t2, p['anthropic_envelope'])
    calls.append(anthropic)
    total = sum(row.get('observed_cost_usd') or 0 for row in calls)
    if total > cost_ceiling:
        return _publish(
            p, run_id, 'complete', 'NO-GO', None,
            'observed cost ceiling exceeded after completed call',
            t1, t2, calls, cost_ceiling=cost_ceiling)
    candidate, reason = choose_candidate(common2, anthropic)
    verdict = 'GO' if candidate is not None else 'NO-GO'
    return _publish(p, run_id, 'complete', verdict, candidate, reason,
                    t1, t2, calls, cost_ceiling=cost_ceiling)


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true',
                      help='zero-token auth/model + frozen-contract preflight')
    mode.add_argument('--execute', action='store_true',
                      help='advance the durable comparison state machine')
    parser.add_argument('--out', default=os.path.join(
        REPO, 'src', 'pilot', 'output', 'route_comparison'))
    parser.add_argument('--run-id')
    parser.add_argument('--model', default=MODEL)
    parser.add_argument('--max-calls', type=int, default=MAX_CALLS)
    parser.add_argument('--cost-ceiling', type=float, default=COST_CEILING_USD)
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        if args.check:
            result = offline_check(model=args.model)
            os.makedirs(os.path.abspath(args.out), exist_ok=True)
            atomic_json(paths(args.out)['preflight'], result)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if result['offline_passed'] else 2
        if not args.run_id:
            raise TransportRefusal('--execute requires a stable --run-id')
        result = execute(
            out=args.out, run_id=args.run_id, model=args.model,
            max_calls=args.max_calls, cost_ceiling=args.cost_ceiling)
    except (TransportRefusal, gex.ExternalRefusal, ValueError) as exc:
        print('REFUSED: %s' % exc, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get('verdict') in ('GO', 'INCOMPLETE') else 2


if __name__ == '__main__':
    sys.exit(main())
