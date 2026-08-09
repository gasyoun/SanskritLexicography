#!/usr/bin/env python
"""Hermetic selftest for the H2504 router.cheap gateway route.

Proves the eight properties the H2504 handoff requires BEFORE any paid
gateway call, plus the credential boundary that blocks a metered call on
this box. Spends nothing: every transport is injected, every environment is
a synthetic dict, no network and no subprocess are touched.

Negative regression fixture: the real H2375 thinking-only envelope
(pwg_ru/h2313/raw/h2375_agent_card_paid_nakzatra_1.json) -- two thinking
turns, no final text block, returncode 0.
"""

import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
for _p in (HERE, os.path.join(REPO, 'src')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gateway_route as gw  # noqa: E402
from call_reservation import CallReservationLedger  # noqa: E402
from execution_contract import (  # noqa: E402
    HEADLESS_ROUTE,
    PRODUCTION_HARD_TIMEOUT_MS,
)

TINY_SCHEMA = {'type': 'object', 'required': ['ok']}


def ledger_at(tmp, run_id='h2504-selftest', max_calls=None):
    return CallReservationLedger(
        os.path.join(tmp, 'call_reservation.json'), run_id, max_calls)


def transcript(blocks, model='claude-opus-5', usage=None):
    out = {'model': model, 'content': blocks}
    if usage is not None:
        out['usage'] = usage
    return out


def text_block(value):
    return {'type': 'text', 'text': value}


def thinking_block(value):
    return {'type': 'thinking', 'thinking': value}


FULL_USAGE = {'input_tokens': 1200, 'output_tokens': 340,
              'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0}


def call_at(tmp, transport, **kw):
    kw.setdefault('route', gw.GATEWAY_ROUTE)
    kw.setdefault('model', 'claude-opus-5')
    max_calls = kw.pop('max_calls', 1)
    ledger = kw.pop('ledger', None) or ledger_at(tmp, max_calls=max_calls)
    return gw.GatewayCall(ledger, kw.pop('route'), kw.pop('model'), transport, **kw), ledger


# ---------------------------------------------------------------- property 1

def t1_provenance_cannot_be_substituted():
    """Route, model and provenance class are all unforgeable at construction."""
    with tempfile.TemporaryDirectory() as tmp:
        ledger = ledger_at(tmp, max_calls=1)
        ok = lambda req: transcript([text_block('{"ok":true}')], usage=FULL_USAGE)  # noqa: E731

        for bad_route in (HEADLESS_ROUTE, 'c4', 'anthropic-routine-in-session',
                          'workflow', ''):
            try:
                gw.GatewayCall(ledger, bad_route, 'claude-opus-5', ok)
            except gw.GatewayProvenanceError:
                pass
            else:
                raise AssertionError('route %r admitted by the gateway adapter' % bad_route)

        try:
            gw.GatewayCall(ledger, gw.GATEWAY_ROUTE, '', ok)
        except gw.GatewayProvenanceError:
            pass
        else:
            raise AssertionError('empty model identifier admitted')

        try:
            gw.GatewayCall(ledger, gw.GATEWAY_ROUTE, 'claude-opus-5', ok, provenance='real')
        except gw.GatewayRefusal:
            pass
        else:
            raise AssertionError("provenance='real' admitted in a synthetic qualification")

        try:
            gw.GatewayCall(ledger, gw.GATEWAY_ROUTE, 'claude-opus-5', ok,
                           timeout_ms=PRODUCTION_HARD_TIMEOUT_MS + 1)
        except ValueError:
            pass
        else:
            raise AssertionError('timeout above the 600 000 ms ceiling admitted')

        try:
            gw.GatewayCall(object(), gw.GATEWAY_ROUTE, 'claude-opus-5', ok)
        except gw.GatewayRefusal:
            pass
        else:
            raise AssertionError('gateway call built without a reservation ledger')

        # A returned model that disagrees with the request is recorded AND refused.
        # Merely publishing model_matches_request=false is not enforcement: without
        # this guard a substituted model could still produce schema_compliant=true.
        call, _ = call_at(tmp, lambda req: transcript(
            [text_block('{"ok":true}')], model='claude-sonnet-5', usage=FULL_USAGE))
        env = call.invoke({}, 'selftest:model-drift', schema=TINY_SCHEMA)
        assert env['returned_model'] == 'claude-sonnet-5', env
        assert env['requested_model'] == 'claude-opus-5', env
        assert env['model_matches_request'] is False, env
        assert env['route'] == gw.GATEWAY_ROUTE != HEADLESS_ROUTE, env
        assert env['schema_compliant'] is False, env
        assert env['failure_class'] == 'provenance', env
        assert env['result'] is None and env['result_sha256'] is None, env


# ---------------------------------------------------------------- property 2

def t2_thinking_only_is_empty_output():
    """The H2375 shape: reasoning turns, no final text -> empty_output, fails closed."""
    with tempfile.TemporaryDirectory() as tmp:
        call, ledger = call_at(tmp, lambda req: transcript([
            thinking_block('German->Russian worked out in full here, 8127 tokens.'),
            thinking_block('Second reasoning turn, 8267 tokens.'),
        ], usage={'input_tokens': 5000, 'output_tokens': 16394,
                  'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0}))
        env = call.invoke({}, 'selftest:thinking-only', schema=TINY_SCHEMA)

        assert env['failure_class'] == gw.EMPTY_OUTPUT, env
        assert env['schema_compliant'] is False, env
        assert env['cards_returned'] == 0, env
        assert env['result'] is None and env['result_sha256'] is None, env
        assert env['final_text_bytes'] == 0, env
        assert env['cost_evaluable'] is False, env
        # The call still happened: it is counted and it is NOT free.
        assert ledger.spent() == 1, ledger.snapshot()
        usage = ledger.usage()
        assert usage['unevaluable_calls'] == 1, usage
        assert usage['cost_evaluable'] is False, usage
        # Hidden reasoning never reaches the result.
        blob = json.dumps(env, ensure_ascii=False)
        assert 'German->Russian' not in blob, 'thinking text leaked into the envelope'


# ---------------------------------------------------------------- property 3

def t3_final_json_only_from_final_block():
    """JSON hiding in a thinking block is not a result; JSON in final text is."""
    with tempfile.TemporaryDirectory() as tmp:
        call, _ = call_at(tmp, lambda req: transcript([
            thinking_block('{"ok":true,"cards":[1,2,3]}'),
        ], usage=FULL_USAGE))
        env = call.invoke({}, 'selftest:json-in-thinking', schema=TINY_SCHEMA)
        assert env['failure_class'] == gw.EMPTY_OUTPUT, env
        assert env['result'] is None, env

        call, _ = call_at(tmp, lambda req: transcript([
            thinking_block('{"ok":false,"cards":[9,9,9]}'),
            text_block('{"ok":true,"cards":[1,2,3]}'),
        ], usage=FULL_USAGE), ledger=ledger_at(tmp, run_id='h2504-final', max_calls=1))
        env = call.invoke({}, 'selftest:json-in-final', schema=TINY_SCHEMA)
        assert env['schema_compliant'] is True, env
        assert env['result'] == {'ok': True, 'cards': [1, 2, 3]}, env
        assert env['cards_returned'] == 3, env

        assert gw.final_text(transcript([thinking_block('x')])) == ''
        assert gw.final_text({'content': 'not-a-list'}) == ''
        assert gw.final_text(transcript([text_block(' a '), text_block('b ')])) == 'a b'


# ---------------------------------------------------------------- property 4

def t4_malformed_keeps_usage_and_cost_evidence():
    """A malformed final block still records tokens; cost stays unevaluable."""
    with tempfile.TemporaryDirectory() as tmp:
        call, ledger = call_at(tmp, lambda req: transcript(
            [text_block('not json at all')], usage=FULL_USAGE))
        env = call.invoke({}, 'selftest:malformed', schema=TINY_SCHEMA)
        assert env['failure_class'] == 'malformed_output', env
        assert env['cost_evaluable'] is False, env
        assert env['final_text_bytes'] > 0, env
        assert ledger.spent() == 1, ledger.snapshot()
        assert ledger.usage()['unevaluable_calls'] == 1, ledger.usage()

        # Schema shortfall: valid JSON, missing a required key.
        call, _ = call_at(tmp, lambda req: transcript(
            [text_block('{"nope":1}')], usage=FULL_USAGE),
            ledger=ledger_at(tmp, run_id='h2504-shortfall', max_calls=1))
        env = call.invoke({}, 'selftest:schema-shortfall', schema=TINY_SCHEMA)
        assert env['failure_class'] == 'malformed_output', env
        assert 'ok' in (env['error'] or ''), env


# ---------------------------------------------------------------- property 5

def t5_reservation_is_strict_pre_call_ceiling():
    """max_calls 0/1/N: the ceiling is checked BEFORE the transport runs."""
    with tempfile.TemporaryDirectory() as tmp:
        calls = {'n': 0}

        def counting(req):
            calls['n'] += 1
            return transcript([text_block('{"ok":true}')], usage=FULL_USAGE)

        zero, ledger0 = call_at(tmp, counting, max_calls=0,
                                ledger=ledger_at(tmp, run_id='h2504-zero', max_calls=0))
        try:
            zero.invoke({}, 'selftest:zero', schema=TINY_SCHEMA)
        except gw.GatewayRefusal as exc:
            assert 'budget_exceeded:max_calls' in str(exc), exc
        else:
            raise AssertionError('max_calls=0 permitted a gateway call')
        assert calls['n'] == 0, 'transport ran under a zero ceiling'
        assert ledger0.spent() == 0, ledger0.snapshot()

        one, ledger1 = call_at(tmp, counting,
                               ledger=ledger_at(tmp, run_id='h2504-one', max_calls=1))
        env = one.invoke({}, 'selftest:one', schema=TINY_SCHEMA)
        assert env['schema_compliant'] is True, env
        assert calls['n'] == 1, calls
        try:
            one.invoke({}, 'selftest:one-again', schema=TINY_SCHEMA)
        except gw.GatewayRefusal:
            pass
        else:
            raise AssertionError('an exhausted run permitted a second gateway call')
        assert calls['n'] == 1, 'transport ran after exhaustion'
        assert ledger1.spent() == 1, ledger1.snapshot()

        two = ledger_at(tmp, run_id='h2504-two', max_calls=2)
        callN = gw.GatewayCall(two, gw.GATEWAY_ROUTE, 'claude-opus-5', counting)
        callN.invoke({}, 'selftest:n1', schema=TINY_SCHEMA)
        callN.invoke({}, 'selftest:n2', schema=TINY_SCHEMA)
        assert two.spent() == 2, two.snapshot()
        assert calls['n'] == 3, calls


# ---------------------------------------------------------------- property 6

def t6_timeout_accounts_and_is_tree_killed():
    """A timeout is counted, unevaluable, and never looks like $0."""
    with tempfile.TemporaryDirectory() as tmp:
        def timing_out(req):
            raise subprocess.TimeoutExpired(cmd='gateway', timeout=1)

        call, ledger = call_at(tmp, timing_out)
        env = call.invoke({}, 'selftest:timeout', schema=TINY_SCHEMA)
        assert env['failure_class'] == 'timeout', env
        assert env['cost_evaluable'] is False, env
        assert env['observed_cost_usd'] == 0, env
        assert ledger.spent() == 1, ledger.snapshot()
        assert ledger.usage()['unevaluable_calls'] == 1, ledger.usage()

        # A transcript whose own wall time exceeds the ceiling is a timeout too.
        call, _ = call_at(tmp, lambda req: transcript(
            [text_block('{"ok":true}')], usage=FULL_USAGE),
            ledger=ledger_at(tmp, run_id='h2504-ceil', max_calls=1),
            timeout_ms=1)
        env = call.invoke({}, 'selftest:over-ceiling', schema=TINY_SCHEMA)
        assert env['hard_timeout_ms'] == 1, env

        # Process-tree kill is delegated, not reimplemented: this route owns no
        # subprocess, so it names the c4 helper rather than forking its own.
        assert gw.TREE_KILL_DELEGATE == 'headless_worker.run_tree_kill', gw.TREE_KILL_DELEGATE

        # Any transport exception is accounted, not swallowed.
        call, ledger = call_at(
            tmp, lambda req: (_ for _ in ()).throw(RuntimeError('socket hang up')),
            ledger=ledger_at(tmp, run_id='h2504-boom', max_calls=1))
        env = call.invoke({}, 'selftest:transport-error', schema=TINY_SCHEMA)
        assert env['failure_class'] == 'transport', env
        assert env['cost_evaluable'] is False, env
        assert ledger.spent() == 1, ledger.snapshot()


# ---------------------------------------------------------------- property 7

def t7_result_hash_is_bound_to_run_id():
    """The sealed bytes carry the run id, so the digest binds result to run."""
    with tempfile.TemporaryDirectory() as tmp:
        call, _ = call_at(tmp, lambda req: transcript(
            [text_block('{"ok":true}')], usage=FULL_USAGE),
            ledger=ledger_at(tmp, run_id='h2504-seal-a', max_calls=1))
        env_a = call.invoke({}, 'selftest:seal', schema=TINY_SCHEMA)
        path_a = os.path.join(tmp, 'a.json')
        digest_a = gw.seal_envelope(path_a, env_a)

        with open(path_a, 'rb') as handle:
            raw = handle.read()
        assert gw.sha256_bytes(raw) == digest_a, 'sealed digest does not cover the file bytes'
        assert env_a['run_id'] == 'h2504-seal-a', env_a
        assert b'h2504-seal-a' in raw, 'run id is not inside the hash-bound bytes'
        assert env_a['reservation_id'], env_a

        call, _ = call_at(tmp, lambda req: transcript(
            [text_block('{"ok":true}')], usage=FULL_USAGE),
            ledger=ledger_at(tmp, run_id='h2504-seal-b', max_calls=1))
        env_b = call.invoke({}, 'selftest:seal', schema=TINY_SCHEMA)
        digest_b = gw.seal_envelope(os.path.join(tmp, 'b.json'), env_b)
        assert digest_a != digest_b, 'same result under a different run id kept one digest'

        # The result digest itself is stable and content-addressed.
        assert env_a['result_sha256'] == env_b['result_sha256'], (env_a, env_b)
        tampered = dict(env_a, run_id='h2504-seal-b')
        assert gw.seal_envelope(os.path.join(tmp, 'c.json'), tampered) != digest_a


# ---------------------------------------------------------------- property 8

def t8_synthetic_output_is_non_promotable():
    """Gateway output can never reach the canonical store."""
    with tempfile.TemporaryDirectory() as tmp:
        call, _ = call_at(tmp, lambda req: transcript(
            [text_block('{"ok":true}')], usage=FULL_USAGE))
        env = call.invoke({}, 'selftest:promotable', schema=TINY_SCHEMA)
        assert env['promotable'] is False, env
        assert env['provenance_class'] == gw.SYNTHETIC_PROVENANCE == 'synthetic_control', env

        # The promotion gate compares against the headless route and this is not it,
        # so promote_final_cards refuses this envelope without any change there.
        assert gw.GATEWAY_ROUTE != HEADLESS_ROUTE
        assert gw.GATEWAY_ROUTE not in gw.FORBIDDEN_ROUTES
        for forbidden in gw.FORBIDDEN_ROUTES:
            assert forbidden != gw.GATEWAY_ROUTE


# ------------------------------------------------------- boundary + telemetry

def t9_credential_boundary_fails_closed():
    """Credential shape is booleans only, and the live gateway needs a token."""
    gateway_no_token = {'ANTHROPIC_BASE_URL': 'https://router.cheap'}
    status = gw.credential_status(gateway_no_token)
    assert status == {'base_url_present': True, 'base_url_is_gateway': True,
                      'auth_token_present': False, 'api_key_present': False}, status
    assert all(isinstance(v, bool) for v in status.values()), status

    with_token = gw.credential_status(
        dict(gateway_no_token, ANTHROPIC_AUTH_TOKEN='sk-should-never-be-printed'))
    assert with_token['auth_token_present'] is True, with_token
    assert 'sk-should-never-be-printed' not in json.dumps(with_token), with_token

    assert gw.credential_status({})['base_url_is_gateway'] is False
    assert gw.credential_status(
        {'ANTHROPIC_BASE_URL': 'https://api.anthropic.com'})['base_url_is_gateway'] is False


def t10_usage_without_a_verified_price_is_unevaluable():
    """Tokens alone never become a dollar figure: the gateway price list is unverified."""
    telemetry, reason = gw.telemetry_from_gateway_usage(FULL_USAGE)
    assert telemetry['cost_evaluable'] is False, telemetry
    assert telemetry['input_tokens'] == 1200 and telemetry['output_tokens'] == 340, telemetry
    assert 'price' in (reason or '').lower(), reason

    priced, reason = gw.telemetry_from_gateway_usage(
        dict(FULL_USAGE, total_cost_usd=0.0412))
    assert priced['cost_evaluable'] is True, priced
    assert priced['observed_cost_usd'] == 0.0412, priced
    assert reason is None, reason

    absent, reason = gw.telemetry_from_gateway_usage(None)
    assert absent['cost_evaluable'] is False and absent['observed_cost_usd'] == 0, absent
    assert reason, reason

    partial, _ = gw.telemetry_from_gateway_usage({'input_tokens': 10})
    assert partial['cost_evaluable'] is False, partial

    assert isinstance(gw.indicative_price(FULL_USAGE), float)
    assert gw.indicative_price({'input_tokens': 10}) is None
    assert gw.indicative_price('nope') is None


TESTS = [
    t1_provenance_cannot_be_substituted,
    t2_thinking_only_is_empty_output,
    t3_final_json_only_from_final_block,
    t4_malformed_keeps_usage_and_cost_evidence,
    t5_reservation_is_strict_pre_call_ceiling,
    t6_timeout_accounts_and_is_tree_killed,
    t7_result_hash_is_bound_to_run_id,
    t8_synthetic_output_is_non_promotable,
    t9_credential_boundary_fails_closed,
    t10_usage_without_a_verified_price_is_unevaluable,
]


def selftest():
    failed = []
    for test in TESTS:
        try:
            test()
        except BaseException as exc:  # noqa: BLE001 -- one failure must not hide the rest
            failed.append(test.__name__)
            print('  FAIL: %s -- %s: %s' % (test.__name__, exc.__class__.__name__, exc))
    if failed:
        print('gateway_route_selftest: FAILED (%d/%d): %s'
              % (len(failed), len(TESTS), ', '.join(failed)))
        return False
    print('gateway_route_selftest: PASS (%d/%d)' % (len(TESTS), len(TESTS)))
    print('  H2504 route identity, thinking-only=empty_output, final-block-only JSON,')
    print('  usage/cost retention, reservation 0/1/N, timeout accounting, run-bound')
    print('  result hash, non-promotable synthetic output, credential fail-closed.')
    return True


if __name__ == '__main__':
    sys.exit(0 if selftest() else 1)
