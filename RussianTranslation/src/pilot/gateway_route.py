#!/usr/bin/env python
"""Gateway (router.cheap) execution route for PWG Russian qualification.

H2504. This module is a SEPARATE execution route from the production
``claude-cli-headless`` (c4) lane. It does not modify, weaken, or reuse
``HeadlessEngine``; it borrows only route-agnostic primitives:

* ``call_reservation.CallReservationLedger``  -- pwg.call_reservation.v1
* ``call_reservation.unevaluable_telemetry`` -- paid-but-unpriceable
* ``execution_contract.assert_timeout_within_ceiling`` -- the 600 000 ms ceiling

Design constraints locked by the handoff (H2504):

1. Route id is ``router-cheap-agent``. It is NEVER ``claude-cli-headless``
   and never ``c4``. The two routes are MUTUALLY EXCLUSIVE: this module
   refuses a headless manifest, and the headless executor keeps refusing
   this route (``execution_contract.validate_profile``). Nothing is widened.
2. Reservation is a strict PRE-CALL ceiling. ``max_calls=0`` or an exhausted
   run must produce zero gateway calls.
3. Usage is accounted BEFORE content is validated. Absent or unpriceable
   usage is ``cost_evaluable=False`` -- never ``$0``.
4. Final JSON is parsed ONLY from the final response block. A thinking-only
   transcript is ``empty_output`` and fails closed. Hidden reasoning is never
   copied into the result.
5. Output is synthetic and NON-PROMOTABLE by construction.

The gateway surface itself (the harness Agent tool) is not callable from a
Python subprocess on this box, so this module is deliberately split:
``capture`` (transcript -> envelope) is pure and hermetically testable, and
the transport is injected. See GATEWAY_QUALIFICATION_REPORT for the boundary.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
for _p in (HERE, os.path.join(REPO, 'src')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from call_reservation import (  # noqa: E402
    CallLimitReached,
    CallReservationLedger,
    normalize_telemetry,
    unevaluable_telemetry,
)
from execution_contract import (  # noqa: E402
    PRODUCTION_HARD_TIMEOUT_MS,
    assert_timeout_within_ceiling,
)

SCHEMA = 'pwg.gateway_call_envelope.v1'

#: This route's identity. Deliberately distinct from
#: ``execution_contract.HEADLESS_ROUTE`` -- see module docstring rule 1.
GATEWAY_ROUTE = 'router-cheap-agent'

#: The route that this module must never impersonate.
FORBIDDEN_ROUTES = ('claude-cli-headless', 'c4', 'anthropic-routine-in-session')

#: Gateway base URL this route is qualified against.
GATEWAY_BASE_URL = 'https://router.cheap'

#: Classification for a transcript that carried reasoning but no final text.
#: The c4 executor has no such class (it reports ``malformed_output``); a
#: thinking-only gateway turn is a distinct, non-retryable platform outcome.
EMPTY_OUTPUT = 'empty_output'

#: Process-tree kill is owned by c4's headless_worker, not this route.
#: A timeout in a live transport SHOULD call this delegate; in the hermetic
#: selftest the transport raises ``subprocess.TimeoutExpired`` instead.
TREE_KILL_DELEGATE = 'headless_worker.run_tree_kill'

#: Provenance class for everything this route produces during qualification.
SYNTHETIC_PROVENANCE = 'synthetic_control'

#: INDICATIVE ONLY -- Sonnet-class public list prices carried over from
#: ``parse_workflow_cost.PRICE`` (USD per 1M tokens). The gateway's real rate
#: card is NOT verified, and this route runs Opus 5, whose list price differs.
#: These rates may therefore produce a rough sanity figure and must NEVER set
#: ``cost_evaluable``: pricing a paid call from an unverified table is exactly
#: how a confident wrong dollar number enters the ledger.
INDICATIVE_PRICE_PER_MTOK = {
    'input_tokens': 3.00,
    'output_tokens': 15.00,
    'cache_creation_tokens': 3.75,
    'cache_read_tokens': 0.30,
}


class GatewayRefusal(RuntimeError):
    """A pre-call contract violation. No gateway call was made."""


class GatewayProvenanceError(RuntimeError):
    """Route/model/profile provenance could not be established or was substituted."""


def credential_status(env=None):
    """Report gateway credential shape WITHOUT revealing any value.

    Returns a dict of booleans only. A token value must never reach a log,
    an artifact, or a command line.
    """
    env = os.environ if env is None else env
    base = (env.get('ANTHROPIC_BASE_URL') or '').strip()
    return {
        'base_url_present': bool(base),
        'base_url_is_gateway': base.rstrip('/') == GATEWAY_BASE_URL,
        'auth_token_present': bool((env.get('ANTHROPIC_AUTH_TOKEN') or '').strip()),
        'api_key_present': bool((env.get('ANTHROPIC_API_KEY') or '').strip()),
    }


def assert_route(route):
    """Refuse any attempt to run this adapter under a borrowed route id."""
    if route != GATEWAY_ROUTE:
        raise GatewayProvenanceError(
            'gateway adapter refuses execution_route=%r (this route is %r)'
            % (route, GATEWAY_ROUTE))
    return route


def assert_not_impersonating(route):
    """Belt-and-braces: the gateway route may never carry a c4/headless id."""
    if route in FORBIDDEN_ROUTES:
        raise GatewayProvenanceError(
            'gateway adapter may not impersonate production route %r' % (route,))
    return route


def gateway_tokens(usage):
    """Extract the four priced token counts, or None if any is unusable."""
    if not isinstance(usage, dict):
        return None
    tokens = {
        'input_tokens': usage.get('input_tokens'),
        'output_tokens': usage.get('output_tokens'),
        'cache_read_tokens': usage.get('cache_read_input_tokens'),
        'cache_creation_tokens': usage.get('cache_creation_input_tokens'),
    }
    for value in tokens.values():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            return None
    return tokens


def indicative_cost(tokens):
    """A rough, NON-authoritative dollar figure. Never gates ``cost_evaluable``.

    Returned for human sanity-checking only, under the unverified rate table
    above. A partial token record yields None rather than collapsing to 0.0.
    """
    if not isinstance(tokens, dict):
        return None
    total = 0.0
    for field, rate in INDICATIVE_PRICE_PER_MTOK.items():
        value = tokens.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            return None
        total += (value / 1_000_000.0) * rate
    return round(total, 6)


def indicative_price(usage):
    """Convenience: indicative cost straight from a gateway ``usage`` block."""
    return indicative_cost(gateway_tokens(usage))


def telemetry_from_gateway_usage(usage):
    """Map a gateway ``usage`` block to pwg.call_reservation.v1 telemetry.

    Returns ``(telemetry, reason)`` where ``reason`` is None when cost is
    evaluable and a short string naming the defect otherwise.

    Cost is evaluable ONLY when the gateway itself reports a price
    (``total_cost_usd``). Token counts alone are recorded but do NOT make a
    call evaluable: this route's real rate card is unverified, so repricing
    from the indicative table would fabricate authority. That is the H2504
    contract condition "an unpriceable nonzero result is cost_evaluable=false,
    never $0" -- and it is why known tokens still fail closed.
    """
    tokens = gateway_tokens(usage)
    if tokens is None:
        return unevaluable_telemetry(), 'usage_absent_or_malformed'
    values = dict(tokens)
    values['subagent_tokens'] = sum(tokens.values())
    reported = usage.get('total_cost_usd')
    if isinstance(reported, bool) or not isinstance(reported, (int, float)) or reported < 0:
        values['observed_cost_usd'] = 0
        values['cost_evaluable'] = False
        return normalize_telemetry(values), 'gateway_reported_no_price'
    values['observed_cost_usd'] = float(reported)
    values['cost_evaluable'] = True
    return normalize_telemetry(values), None


def final_text(transcript):
    """Return the FINAL assistant text only -- never hidden reasoning.

    ``transcript`` is a dict with a ``content`` list of blocks. Only blocks of
    type ``text`` contribute. ``thinking`` / ``redacted_thinking`` blocks are
    ignored entirely: a reasoning transcript is not translation data.
    """
    if not isinstance(transcript, dict):
        return ''
    blocks = transcript.get('content')
    if not isinstance(blocks, list):
        return ''
    parts = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        if block.get('type') != 'text':
            continue
        text = block.get('text')
        if isinstance(text, str):
            parts.append(text)
    return ''.join(parts).strip()


def structured_from_transcript(transcript):
    """Parse the final JSON object from the final response block.

    Raises ``ValueError`` tagged ``empty_output`` when there is no final text
    at all (the H2375 thinking-only shape), and a plain ``ValueError`` when a
    final block exists but is not the expected JSON object.
    """
    text = final_text(transcript)
    if not text:
        raise ValueError('%s: no final text block in gateway transcript' % EMPTY_OUTPUT)
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError('gateway final block is not JSON: %s' % exc)
    if not isinstance(value, dict):
        raise ValueError('gateway final block is not a JSON object')
    return value


def classify_transcript_error(message):
    """Map a capture failure message to this route's classification."""
    return EMPTY_OUTPUT if str(message).startswith(EMPTY_OUTPUT) else 'malformed_output'


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def atomic_json(path, payload):
    """Write JSON with LF newlines + fsync -- these bytes are hash-bound."""
    directory = os.path.dirname(os.path.abspath(path)) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return path


class GatewayCall:
    """One reserved, metered, hash-bound gateway call.

    ``transport`` is a callable ``(request) -> transcript`` returning a dict
    with ``model``, ``content`` blocks, and ``usage``. It is injected so the
    whole envelope path is hermetically testable without spending anything;
    the live transport is the harness Agent tool, which no subprocess can
    reach on this box.
    """

    def __init__(self, ledger, route, model, transport,
                 timeout_ms=PRODUCTION_HARD_TIMEOUT_MS,
                 provenance=SYNTHETIC_PROVENANCE, profile=None):
        if not isinstance(ledger, CallReservationLedger):
            raise GatewayRefusal('gateway call requires a pwg.call_reservation.v1 ledger')
        assert_not_impersonating(assert_route(route))
        if not model or not isinstance(model, str):
            raise GatewayProvenanceError('gateway call requires an explicit model identifier')
        if provenance != SYNTHETIC_PROVENANCE:
            raise GatewayRefusal(
                'H2504 qualification is synthetic-only; refusing provenance=%r' % (provenance,))
        assert_timeout_within_ceiling(timeout_ms, 'gateway_route.timeout_ms')
        self.ledger = ledger
        self.route = route
        self.model = model
        self.transport = transport
        self.timeout_ms = int(timeout_ms)
        self.provenance = provenance
        self.profile = profile

    def _content_outcome(self, transcript, schema, wall_ms):
        """Judge a transcript. Pure -- touches no ledger and spends nothing."""
        if not transcript.get('model'):
            return {'schema_compliant': False, 'cards_returned': 0, 'result': None,
                    'classification': 'provenance',
                    'error': 'gateway transcript carries no model identifier'}
        if self.timeout_ms and wall_ms > self.timeout_ms:
            return {'schema_compliant': False, 'cards_returned': 0, 'result': None,
                    'classification': 'timeout',
                    'error': 'wall_ms %d exceeded hard ceiling %d ms'
                             % (wall_ms, self.timeout_ms)}
        try:
            result = structured_from_transcript(transcript)
        except ValueError as exc:
            return {'schema_compliant': False, 'cards_returned': 0, 'result': None,
                    'classification': classify_transcript_error(exc), 'error': str(exc)}
        if schema is not None:
            missing = [key for key in schema.get('required', []) if key not in result]
            if missing:
                return {'schema_compliant': False, 'cards_returned': 0, 'result': None,
                        'classification': 'malformed_output',
                        'error': 'final JSON missing required keys: %s'
                                 % ', '.join(sorted(missing))}
        cards = result.get('cards')
        return {'schema_compliant': True, 'result': result, 'error': None,
                'cards_returned': len(cards) if isinstance(cards, list) else 0,
                'classification': 'success'}

    def invoke(self, request, purpose, schema=None):
        """Reserve, call, account, judge, finalize once. Returns an envelope.

        Money invariants, in this order:

        1. the slot is durably reserved BEFORE the transport runs;
        2. usage is captured from the transcript and can never be lost;
        3. a content failure DEMOTES the telemetry to ``cost_evaluable=False``
           *before* ``finalize`` -- so the ledger never reports a failed call
           as priced (this mirrors ``headless_worker`` exactly);
        4. ``finalize`` runs exactly once per reservation, on every path.
        """
        try:
            reservation = self.ledger.reserve(
                purpose, profile=self.profile, detail=self.route)
        except CallLimitReached as exc:
            raise GatewayRefusal('budget_exceeded:max_calls (%s)' % exc)

        started = time.monotonic()
        transcript = None
        transport_error = None
        transport_timed_out = False
        try:
            transcript = self.transport(request)
        except subprocess.TimeoutExpired as exc:
            transport_error = '%s: %s' % (exc.__class__.__name__, exc)
            transport_timed_out = True
        except BaseException as exc:  # noqa: BLE001 -- reservation is irreversible
            transport_error = '%s: %s' % (exc.__class__.__name__, exc)
        wall_ms = int((time.monotonic() - started) * 1000)

        if transport_error is not None or not isinstance(transcript, dict):
            telemetry = unevaluable_telemetry()
            _cls = 'timeout' if transport_timed_out else 'transport'
            outcome = {
                'schema_compliant': False, 'cards_returned': 0, 'result': None,
                'classification': _cls,
                'error': transport_error or 'gateway transport returned no transcript'}
            returned_model = None
            text = ''
        else:
            telemetry, _ = telemetry_from_gateway_usage(transcript.get('usage'))
            outcome = self._content_outcome(transcript, schema, wall_ms)
            returned_model = transcript.get('model')
            text = final_text(transcript)

        if not outcome['schema_compliant']:
            # A transcript that failed validation is permanently unpriceable:
            # the paid/result association itself did not hold.
            telemetry = dict(telemetry, cost_evaluable=False)
        self.ledger.finalize(reservation, telemetry)

        envelope = {
            'schema': SCHEMA,
            'route': self.route,
            'requested_model': self.model,
            'returned_model': returned_model,
            'model_matches_request': (returned_model == self.model),
            'gateway_base_url': GATEWAY_BASE_URL,
            'provenance_class': self.provenance,
            'promotable': False,
            'run_id': self.ledger.run_id,
            'reservation_id': reservation.get('reservation_id'),
            'reservation_ordinal': reservation.get('ordinal'),
            'purpose': purpose,
            'hard_timeout_ms': self.timeout_ms,
            'wall_ms': wall_ms,
            'usage': dict(telemetry),
            'cost_evaluable': bool(telemetry.get('cost_evaluable')),
            'observed_cost_usd': telemetry.get('observed_cost_usd'),
            'final_text_sha256': (sha256_bytes(text.encode('utf-8')) if text else None),
            'final_text_bytes': len(text.encode('utf-8')),
            'failure_class': (None if outcome['schema_compliant']
                              else outcome['classification']),
        }
        envelope.update(outcome)
        if outcome['schema_compliant']:
            envelope['result_sha256'] = sha256_bytes(
                json.dumps(outcome['result'], ensure_ascii=False, sort_keys=True,
                           separators=(',', ':')).encode('utf-8'))
        else:
            envelope['result_sha256'] = None
        return envelope


def seal_envelope(path, envelope):
    """Persist an envelope and bind the saved bytes by SHA-256."""
    atomic_json(path, envelope)
    with open(path, 'rb') as handle:
        digest = sha256_bytes(handle.read())
    return digest


if __name__ == '__main__':
    status = credential_status()
    print('gateway_route: route=%s base=%s' % (GATEWAY_ROUTE, GATEWAY_BASE_URL))
    print('  credential shape (booleans only): %s'
          % json.dumps(status, sort_keys=True))
    print('  hard ceiling: %d ms' % PRODUCTION_HARD_TIMEOUT_MS)
