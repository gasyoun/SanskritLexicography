"""Provider adapters (H3714 Wave 1, implementation step 3.1).

An adapter owns exactly four things: ``prepare_request``, ``invoke``,
``parse_result`` and ``normalize_usage``.  It does **not** own budgets, retries,
persistence, promotion, or canonical paths -- those belong to the kernel
(architecture, boundary rule 2).  Keeping the protocol this small is what stops
provider differences from silently becoming accounting differences.

Wave-1 adapters:

* :class:`XaiTmAdapter` -- the PWG-TM route, migrated first.
* :class:`DeepSeekTmAdapter` -- the bounded fallback lane.
* :class:`ClaudeHeadlessShadowAdapter` -- read-only evidence over the proven
  headless worker; it refuses to execute anything.
* :class:`FakeAdapter` -- fixture-driven, used by every offline gate.

Credentials are read from the environment at invoke time and never stored,
logged, hashed into evidence, or written to the database.
"""
from __future__ import annotations

import dataclasses
import json
import os
import re
from typing import Any, Mapping, Protocol, Sequence

from . import model
from .evidence import canonical_sha256

SCHEMA = 'pwg.pipeline.provider.v1'

XAI_BASE_URL = 'https://api.x.ai/v1'
XAI_DEFAULT_MODEL = 'grok-4.6'
XAI_KEY_ENV = 'XAI_API_KEY'

DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
DEEPSEEK_DEFAULT_MODEL = 'deepseek-v4-flash'
DEEPSEEK_KEY_ENV = 'DEEPSEEK_API_KEY'

# Provider list prices, USD per million tokens. Used ONLY to estimate a ceiling
# before dispatch; the sealed cost always prefers provider-reported usage.
PRICE_PER_MTOK_USD: dict[str, dict[str, float]] = {
    model.ROUTE_XAI: {'input': 3.0, 'output': 15.0},
    model.ROUTE_DEEPSEEK: {'input': 0.28, 'output': 0.42},
}


class ProviderError(RuntimeError):
    """The adapter could not produce an evaluable, attributable result."""


class ProviderUnavailable(ProviderError):
    """A credential or SDK is missing: this adapter's track stops, alone.

    Per the Wave-1 stop conditions an unavailable optional provider halts only
    its own track -- and the other provider must never consume the unused call
    as a retry.
    """


@dataclasses.dataclass(frozen=True)
class ProviderRequest:
    """What the kernel dispatches. Never carries a credential."""

    route: str
    requested_model: str
    payload: dict[str, Any]
    max_output_tokens: int
    timeout_ms: int

    @property
    def sha256(self) -> str:
        return canonical_sha256({
            'route': self.route,
            'requested_model': self.requested_model,
            'payload': self.payload,
            'max_output_tokens': self.max_output_tokens,
        })


@dataclasses.dataclass(frozen=True)
class ProviderResponse:
    """A raw provider reply, before parsing. Sealed as-is."""

    raw_text: str
    served_model: str | None
    raw_usage: dict[str, Any]

    @property
    def sha256(self) -> str:
        return canonical_sha256({
            'raw_text': self.raw_text,
            'served_model': self.served_model,
            'raw_usage': self.raw_usage,
        })


def normalized_usage(*, input_tokens: Any, output_tokens: Any,
                     observed_cost_usd: Any = None,
                     route: str | None = None) -> dict[str, Any]:
    """Normalize provider usage; refuse to guess when it is not evaluable.

    Missing or non-numeric token counts make the call *unevaluable* rather than
    zero-cost.  A derived-only cost is allowed but marked, so a receipt can
    never present an estimate as an observation.
    """
    def _number(value: Any) -> float | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if value < 0:
            return None
        return float(value)

    tokens_in = _number(input_tokens)
    tokens_out = _number(output_tokens)
    if tokens_in is None or tokens_out is None:
        return {'cost_evaluable': False, 'input_tokens': 0, 'output_tokens': 0,
                'observed_cost_usd': 0.0, 'cost_basis': 'unevaluable'}
    cost = _number(observed_cost_usd)
    basis = 'provider_reported'
    if cost is None:
        prices = PRICE_PER_MTOK_USD.get(route or '', None)
        if prices is None:
            return {'cost_evaluable': False, 'input_tokens': int(tokens_in),
                    'output_tokens': int(tokens_out), 'observed_cost_usd': 0.0,
                    'cost_basis': 'unevaluable'}
        cost = (tokens_in * prices['input'] + tokens_out * prices['output']) / 1e6
        basis = 'list_price_derived'
    return {
        'cost_evaluable': True,
        'input_tokens': int(tokens_in),
        'output_tokens': int(tokens_out),
        'observed_cost_usd': round(float(cost), 6),
        'cost_basis': basis,
    }


class ProviderAdapter(Protocol):
    """The whole adapter surface. Four methods, no budget or persistence."""

    name: str
    route: str

    def prepare_request(self, job_payloads: Sequence[Mapping[str, Any]], *,
                        requested_model: str, max_output_tokens: int,
                        timeout_ms: int) -> ProviderRequest: ...

    def invoke(self, request: ProviderRequest) -> ProviderResponse: ...

    def parse_result(self, response: ProviderResponse) -> dict[str, Any]: ...

    def normalize_usage(self, response: ProviderResponse) -> dict[str, Any]: ...


def _extract_json(text: str) -> Any:
    """Parse a provider reply, tolerating a prose wrapper but not silence."""
    stripped = (text or '').strip()
    if not stripped:
        raise ProviderError('provider returned an empty body')
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', stripped, re.S)
        if not match:
            raise ProviderError('provider reply contains no JSON object')
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ProviderError('provider reply is malformed JSON: %s' % exc)


class _OpenAICompatibleAdapter:
    """Shared body for the two OpenAI-wire-format providers."""

    name = 'openai-compatible'
    route = model.ROUTE_XAI
    base_url = ''
    key_env = ''
    default_model = ''
    system_prompt = (
        'Translate each PWG fragment. Return strict JSON: '
        '{"fragments":[{"fragment_id":"...","target_string":"..."}]}. '
        'Leave Sanskrit, grammar abbreviations and source references untouched.')

    def prepare_request(self, job_payloads: Sequence[Mapping[str, Any]], *,
                        requested_model: str, max_output_tokens: int,
                        timeout_ms: int) -> ProviderRequest:
        payload = {
            'system': self.system_prompt,
            'fragments': [
                {'fragment_id': item.get('fragment_id'),
                 'fragment_class': item.get('fragment_class'),
                 'source_string': item.get('source_string'),
                 'context': item.get('context')}
                for item in job_payloads],
        }
        return ProviderRequest(route=self.route,
                               requested_model=requested_model or self.default_model,
                               payload=payload,
                               max_output_tokens=int(max_output_tokens),
                               timeout_ms=int(timeout_ms))

    def _client(self, timeout_ms: int):
        key = os.environ.get(self.key_env)
        if not key:
            raise ProviderUnavailable(
                '%s is unset; the %s adapter track stops here'
                % (self.key_env, self.name))
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderUnavailable(
                'the %s adapter needs the openai SDK: %s' % (self.name, exc))
        return OpenAI(api_key=key, base_url=self.base_url,
                      timeout=timeout_ms / 1000.0, max_retries=0)

    def invoke(self, request: ProviderRequest) -> ProviderResponse:
        client = self._client(request.timeout_ms)
        payload = dict(request.payload)
        system = payload.pop('system', self.system_prompt)
        completion = client.chat.completions.create(
            model=request.requested_model,
            messages=[{'role': 'system', 'content': system},
                      {'role': 'user',
                       'content': json.dumps(payload, ensure_ascii=False)}],
            temperature=0,
            max_tokens=request.max_output_tokens,
        )
        usage = getattr(completion, 'usage', None)
        raw_usage: dict[str, Any] = {}
        for field in ('prompt_tokens', 'completion_tokens', 'total_tokens'):
            raw_usage[field] = getattr(usage, field, None)
        return ProviderResponse(
            raw_text=(completion.choices[0].message.content or ''),
            served_model=getattr(completion, 'model', None),
            raw_usage=raw_usage)

    def parse_result(self, response: ProviderResponse) -> dict[str, Any]:
        parsed = _extract_json(response.raw_text)
        if not isinstance(parsed, Mapping):
            raise ProviderError('provider reply is not a JSON object')
        rows = parsed.get('fragments') or parsed.get('items') or []
        if not isinstance(rows, list):
            raise ProviderError('provider reply has a non-list fragments field')
        return {'fragments': rows}

    def normalize_usage(self, response: ProviderResponse) -> dict[str, Any]:
        return normalized_usage(
            input_tokens=response.raw_usage.get('prompt_tokens'),
            output_tokens=response.raw_usage.get('completion_tokens'),
            observed_cost_usd=response.raw_usage.get('observed_cost_usd'),
            route=self.route)


class XaiTmAdapter(_OpenAICompatibleAdapter):
    """The PWG-TM xAI route, now behind the shared kernel (R3.4)."""

    name = 'xai'
    route = model.ROUTE_XAI
    base_url = XAI_BASE_URL
    key_env = XAI_KEY_ENV
    default_model = XAI_DEFAULT_MODEL


class DeepSeekTmAdapter(_OpenAICompatibleAdapter):
    """The bounded DeepSeek fallback lane, same request/result contract."""

    name = 'deepseek'
    route = model.ROUTE_DEEPSEEK
    base_url = DEEPSEEK_BASE_URL
    key_env = DEEPSEEK_KEY_ENV
    default_model = DEEPSEEK_DEFAULT_MODEL


class ClaudeHeadlessShadowAdapter:
    """Read-only evidence over the proven Claude headless lane (R3.4).

    It delegates nothing and executes nothing: Wave 3 shadows the existing
    worker, it does not duplicate its model logic.  ``invoke`` always refuses,
    so an operator cannot accidentally route paid Claude work through the new
    facade before the shadow interval closes.
    """

    name = 'claude-headless-shadow'
    route = model.ROUTE_CLAUDE_SHADOW

    def prepare_request(self, job_payloads: Sequence[Mapping[str, Any]], *,
                        requested_model: str, max_output_tokens: int,
                        timeout_ms: int) -> ProviderRequest:
        return ProviderRequest(
            route=self.route, requested_model=requested_model,
            payload={'shadow_of': [dict(item) for item in job_payloads]},
            max_output_tokens=int(max_output_tokens), timeout_ms=int(timeout_ms))

    def invoke(self, request: ProviderRequest) -> ProviderResponse:
        raise ProviderError(
            'the Claude shadow adapter never executes; it compares the existing'
            ' headless lane and holds zero execution authority')

    def parse_result(self, response: ProviderResponse) -> dict[str, Any]:
        return {'fragments': []}

    def normalize_usage(self, response: ProviderResponse) -> dict[str, Any]:
        return normalized_usage(input_tokens=None, output_tokens=None)

    def observe(self, legacy_result: Mapping[str, Any]) -> ProviderResponse:
        """Wrap an already-produced legacy result as read-only evidence."""
        return ProviderResponse(
            raw_text=json.dumps(dict(legacy_result), ensure_ascii=False,
                                sort_keys=True),
            served_model=str(legacy_result.get('model_id') or '') or None,
            raw_usage=dict(legacy_result.get('usage') or {}))


class FakeAdapter:
    """Fixture-driven adapter for every offline gate.

    ``calls`` counts real dispatches, so V2 can pin that a ceiling refusal
    happens *before* provider I/O.
    """

    name = 'fake'

    def __init__(self, route: str = model.ROUTE_XAI, *,
                 responses: Sequence[ProviderResponse] | None = None,
                 raises: BaseException | None = None,
                 served_model: str | None = None) -> None:
        self.route = route
        self.calls = 0
        self.requests: list[ProviderRequest] = []
        self._responses = list(responses or [])
        self._raises = raises
        self._served_model = served_model

    def prepare_request(self, job_payloads: Sequence[Mapping[str, Any]], *,
                        requested_model: str, max_output_tokens: int,
                        timeout_ms: int) -> ProviderRequest:
        return ProviderRequest(
            route=self.route, requested_model=requested_model,
            payload={'fragments': [dict(item) for item in job_payloads]},
            max_output_tokens=int(max_output_tokens), timeout_ms=int(timeout_ms))

    def invoke(self, request: ProviderRequest) -> ProviderResponse:
        self.calls += 1
        self.requests.append(request)
        if self._raises is not None:
            raise self._raises
        if self._responses:
            return self._responses.pop(0)
        fragments = request.payload.get('fragments') or []
        body = {'fragments': [
            {'fragment_id': item.get('fragment_id'),
             'target_string': 'ru:%s' % (item.get('source_string') or '')}
            for item in fragments]}
        return ProviderResponse(
            raw_text=json.dumps(body, ensure_ascii=False, sort_keys=True),
            served_model=self._served_model or request.requested_model,
            raw_usage={'prompt_tokens': 100, 'completion_tokens': 50})

    def parse_result(self, response: ProviderResponse) -> dict[str, Any]:
        parsed = _extract_json(response.raw_text)
        rows = parsed.get('fragments') if isinstance(parsed, Mapping) else None
        if not isinstance(rows, list):
            raise ProviderError('fake adapter reply has no fragments list')
        return {'fragments': rows}

    def normalize_usage(self, response: ProviderResponse) -> dict[str, Any]:
        return normalized_usage(
            input_tokens=response.raw_usage.get('prompt_tokens'),
            output_tokens=response.raw_usage.get('completion_tokens'),
            observed_cost_usd=response.raw_usage.get('observed_cost_usd'),
            route=self.route)


ADAPTERS: dict[str, type] = {
    'xai': XaiTmAdapter,
    'deepseek': DeepSeekTmAdapter,
    'claude-shadow': ClaudeHeadlessShadowAdapter,
}


def adapter_for(name: str):
    """Instantiate a registered adapter by operator-facing name."""
    if name not in ADAPTERS:
        raise ProviderError('unknown provider adapter: %r (known: %s)'
                            % (name, ', '.join(sorted(ADAPTERS))))
    return ADAPTERS[name]()


def estimate_cost_usd(route: str, *, input_tokens: int,
                      max_output_tokens: int) -> float:
    """Worst-case list-price cost, used for the pre-dispatch ceiling check."""
    prices = PRICE_PER_MTOK_USD.get(route)
    if prices is None:
        raise ProviderError('no price card for route %r' % (route,))
    return round((input_tokens * prices['input']
                  + max_output_tokens * prices['output']) / 1e6, 6)


__all__ = [
    'SCHEMA', 'ProviderError', 'ProviderUnavailable', 'ProviderRequest',
    'ProviderResponse', 'ProviderAdapter', 'XaiTmAdapter', 'DeepSeekTmAdapter',
    'ClaudeHeadlessShadowAdapter', 'FakeAdapter', 'ADAPTERS', 'adapter_for',
    'normalized_usage', 'estimate_cost_usd', 'PRICE_PER_MTOK_USD',
    'XAI_KEY_ENV', 'DEEPSEEK_KEY_ENV',
]
