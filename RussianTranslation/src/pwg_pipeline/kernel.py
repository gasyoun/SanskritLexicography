"""The one shared paid-call kernel (H3714 Wave 1, implementation step 3.2).

Every billed provider request in the PWG programme goes through exactly one
sequence:

``validate budget -> reserve -> persist -> dispatch under timeout ->
capture usage and returned route -> seal evidence -> finalize``

and finalizes exactly one call record on *every* exit path: success, refusal,
malformed output, timeout, or exception.  It fails closed on missing usage,
ambiguous cost, route substitution, malformed response, timeout, or a ceiling
breach, and it performs no automatic retry, reroll, fallback, or extra probe --
Wave 1 gives the kernel no semantic-retry authority at all.

The reservation ledger is the existing hardened
[`src/pilot/call_reservation.py`](../pilot/call_reservation.py); this module
adds the transactional call row and the sealed evidence around it rather than a
second accounting authority.
"""
from __future__ import annotations

import dataclasses
import os
import sys
import threading
from typing import Any, Callable, Mapping, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for _path in (SRC, os.path.join(SRC, 'pilot')):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import call_reservation  # noqa: E402  (hardened reservation ledger, reused)

from . import faults, model, providers  # noqa: E402
from .evidence import seal  # noqa: E402
from .repository import Repository, new_id  # noqa: E402

SCHEMA = 'pwg.pipeline.kernel.v1'

DEFAULT_TIMEOUT_MS = 120000
DEFAULT_MAX_OUTPUT_TOKENS = 2048

# Failure vocabulary sealed into every non-success call row.
FAILURE_BUDGET = 'budget_refusal'
FAILURE_CEILING = 'cost_ceiling'
FAILURE_TIMEOUT = 'timeout'
FAILURE_MALFORMED = 'malformed_response'
FAILURE_UNEVALUABLE = 'unevaluable_usage'
FAILURE_ROUTE = 'route_substitution'
FAILURE_UNAVAILABLE = 'provider_unavailable'
FAILURE_EXCEPTION = 'provider_exception'


class KernelRefusal(RuntimeError):
    """The kernel refused before or after dispatch. Always terminally accounted."""

    def __init__(self, message: str, *, failure_class: str,
                 dispatched: bool = False) -> None:
        super().__init__(message)
        self.failure_class = failure_class
        self.dispatched = dispatched


class GlobalStop(KernelRefusal):
    """A global-stop class: accounting, route, integrity, secrets, idempotence.

    Wave-1 stop conditions halt the *whole* wave on these, not just one track.
    """


@dataclasses.dataclass(frozen=True)
class CallOutcome:
    """What one kernel invocation produced, whatever the exit path."""

    call_id: str
    state: str
    route: str
    requested_model: str
    served_model: str | None
    usage: dict[str, Any]
    failure_class: str | None
    request_sha256: str
    response_sha256: str | None
    artifacts: dict[str, dict[str, Any]]
    parsed: dict[str, Any] | None

    @property
    def succeeded(self) -> bool:
        return self.state == model.CALL_SUCCEEDED


def _run_with_timeout(function: Callable[[], Any], timeout_ms: int) -> Any:
    """Run ``function`` under a hard wall-clock ceiling.

    The provider SDKs are synchronous and not cancellable, so the worker thread
    is abandoned on expiry rather than killed -- but the *call* is terminally
    accounted as a timeout either way, which is the property the ledger needs.
    A daemon thread cannot keep the process alive past its own exit.
    """
    box: dict[str, Any] = {}

    def target() -> None:
        try:
            box['value'] = function()
        except BaseException as exc:  # noqa: BLE001 - re-raised on the caller
            box['error'] = exc

    worker = threading.Thread(target=target, daemon=True,
                              name='pwg-pipeline-call')
    worker.start()
    worker.join(timeout_ms / 1000.0)
    if worker.is_alive():
        raise TimeoutError('provider call exceeded %d ms' % timeout_ms)
    if 'error' in box:
        raise box['error']
    return box['value']


class PaidCallKernel:
    """One reservation, timeout, usage and sealing boundary for every route."""

    def __init__(self, repository: Repository, *, campaign_id: str,
                 evidence_dir: str, ledger_path: str,
                 fault_hook: faults.FaultHook | None = None,
                 timeout_runner: Callable[[Callable[[], Any], int], Any] | None = None
                 ) -> None:
        self.repository = repository
        self.campaign_id = campaign_id
        self.evidence_dir = os.path.abspath(evidence_dir)
        self.ledger_path = os.path.abspath(ledger_path)
        self.fault_hook = fault_hook
        self._run_call = timeout_runner or _run_with_timeout
        os.makedirs(self.evidence_dir, exist_ok=True)
        campaign = repository.campaign(campaign_id)
        self.campaign = campaign
        self.ledger = call_reservation.CallReservationLedger(
            self.ledger_path, campaign_id, max_calls=campaign.max_calls)

    # -- budget ------------------------------------------------------------

    def remaining_calls(self) -> int:
        return max(0, self.campaign.max_calls - self.ledger.spent())

    def spent_usd(self) -> float:
        return float(
            self.repository.call_accounting(self.campaign_id)['observed_cost_usd'])

    def assert_budget(self, route: str, *, input_tokens: int,
                      max_output_tokens: int) -> float:
        """Refuse before any provider I/O when a ceiling would be breached (V2).

        A route with no verified price card (H4057: ``glm-flash``) cannot be
        bounded in dollars, so a dollar-bounded dispatch fails *closed* here --
        before a reservation is taken -- instead of raising past the caller.
        """
        if self.remaining_calls() <= 0:
            raise KernelRefusal(
                'call ceiling reached for campaign %s (max_calls=%d)'
                % (self.campaign_id, self.campaign.max_calls),
                failure_class=FAILURE_BUDGET)
        try:
            estimate = providers.estimate_cost_usd(
                route, input_tokens=input_tokens,
                max_output_tokens=max_output_tokens)
        except providers.ProviderError as exc:
            raise KernelRefusal(
                'no verified price card for route %r; a dollar-bounded campaign'
                ' (ceiling USD %.2f) fails closed: %s'
                % (route, self.campaign.cost_ceiling_usd, exc),
                failure_class=FAILURE_CEILING) from exc
        projected = self.spent_usd() + estimate
        if projected > self.campaign.cost_ceiling_usd + 1e-9:
            raise KernelRefusal(
                'worst-case cost USD %.4f would exceed the campaign ceiling'
                ' USD %.2f (already spent USD %.4f)'
                % (projected, self.campaign.cost_ceiling_usd, self.spent_usd()),
                failure_class=FAILURE_CEILING)
        return estimate

    # -- the one sequence --------------------------------------------------

    def execute(self, adapter: Any, *, job_ids: Sequence[str],
                job_payloads: Sequence[Mapping[str, Any]],
                requested_model: str,
                idempotency_key: str,
                attempt_id: str | None = None,
                timeout_ms: int = DEFAULT_TIMEOUT_MS,
                max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
                estimated_input_tokens: int = 1000) -> CallOutcome:
        """Reserve, dispatch, seal and finalize exactly one provider call."""
        route = adapter.route
        model.require_choice(route, model.ROUTES, 'adapter.route')
        if route not in model.BILLABLE_ROUTES:
            raise KernelRefusal(
                'route %r is not billable and must not enter the paid kernel'
                % route, failure_class=FAILURE_ROUTE)
        if not job_ids:
            raise KernelRefusal('a call must be bound to at least one job',
                                failure_class=FAILURE_BUDGET)

        # 1. validate budget -- strictly before any I/O.
        self.assert_budget(route, input_tokens=estimated_input_tokens,
                           max_output_tokens=max_output_tokens)

        request = adapter.prepare_request(
            job_payloads, requested_model=requested_model,
            max_output_tokens=max_output_tokens, timeout_ms=timeout_ms)

        if attempt_id is None:
            attempt_id = self._open_attempt(adapter, job_ids[0], route,
                                            requested_model)

        # 2. reserve, then 3. persist -- both before dispatch.
        reservation = self.ledger.reserve(
            purpose='pwg_pipeline.call', profile=route,
            detail=requested_model, idempotency_key=idempotency_key)
        call = model.Call(
            call_id=new_id('call'), attempt_id=attempt_id, route=route,
            requested_model=requested_model,
            reservation_id=str(reservation['reservation_id']),
            idempotency_key=idempotency_key)
        self.repository.record_reserved_call(call, job_ids=job_ids)
        request_receipt = self._seal('request', call.call_id, {
            'schema': 'pwg.pipeline.request.v1',
            'route': route, 'requested_model': requested_model,
            'request_sha256': request.sha256,
            'max_output_tokens': max_output_tokens, 'timeout_ms': timeout_ms,
            'payload': request.payload,
        })
        faults.fault(self.fault_hook, faults.AFTER_RESERVATION)

        artifacts = {'request': request_receipt}
        self.repository.transition_call(call.call_id, model.CALL_RESERVED,
                                        model.CALL_DISPATCHED)

        # 4. dispatch under a hard timeout.
        try:
            response = self._run_call(lambda: adapter.invoke(request), timeout_ms)
        except providers.ProviderUnavailable as exc:
            return self._finalize_failure(call, request, artifacts,
                                          FAILURE_UNAVAILABLE, str(exc),
                                          model.CALL_REFUSED)
        except TimeoutError as exc:
            return self._finalize_failure(call, request, artifacts,
                                          FAILURE_TIMEOUT, str(exc),
                                          model.CALL_TIMED_OUT)
        except BaseException as exc:  # noqa: BLE001 - always terminally accounted
            return self._finalize_failure(call, request, artifacts,
                                          FAILURE_EXCEPTION, repr(exc),
                                          model.CALL_ERRORED)
        faults.fault(self.fault_hook, faults.AFTER_PROVIDER_RESPONSE)

        response_receipt = self._seal('response', call.call_id, {
            'schema': 'pwg.pipeline.response.v1',
            'route': route, 'served_model': response.served_model,
            'raw_text': response.raw_text, 'raw_usage': response.raw_usage,
            'response_sha256': response.sha256,
        })
        artifacts['response'] = response_receipt

        # 5. capture usage and the returned route.
        usage = adapter.normalize_usage(response)
        faults.fault(self.fault_hook, faults.AFTER_USAGE_CAPTURE)
        if not usage.get('cost_evaluable'):
            outcome = self._finalize_failure(
                call, request, artifacts, FAILURE_UNEVALUABLE,
                'provider usage is missing or not evaluable',
                model.CALL_MALFORMED, response=response)
            raise GlobalStop(
                'unevaluable usage on call %s: accounting uncertainty halts the'
                ' wave' % call.call_id, failure_class=FAILURE_UNEVALUABLE,
                dispatched=True)
        served = response.served_model
        if served and requested_model and served != requested_model:
            self._finalize_failure(
                call, request, artifacts, FAILURE_ROUTE,
                'requested %r but %r was served' % (requested_model, served),
                model.CALL_MALFORMED, response=response, usage=usage)
            raise GlobalStop(
                'route substitution on call %s: requested %r, served %r'
                % (call.call_id, requested_model, served),
                failure_class=FAILURE_ROUTE, dispatched=True)

        try:
            parsed = adapter.parse_result(response)
        except providers.ProviderError as exc:
            return self._finalize_failure(
                call, request, artifacts, FAILURE_MALFORMED, str(exc),
                model.CALL_MALFORMED, response=response, usage=usage)

        # 6. seal evidence, then 7. finalize.
        result_receipt = self._seal('result', call.call_id, {
            'schema': 'pwg.pipeline.result.v1',
            'route': route, 'served_model': served,
            'requested_model': requested_model,
            'usage': usage, 'parsed': parsed,
            'request_sha256': request.sha256,
            'response_sha256': response.sha256,
        })
        artifacts['result'] = result_receipt
        faults.fault(self.fault_hook, faults.AFTER_ARTIFACT_SEAL)

        self.repository.transition_call(call.call_id, model.CALL_DISPATCHED,
                                        model.CALL_SUCCEEDED)
        self._finalize(call, model.CALL_SUCCEEDED, usage, served,
                       request.sha256, response.sha256, None)
        return CallOutcome(
            call_id=call.call_id, state=model.CALL_SUCCEEDED, route=route,
            requested_model=requested_model, served_model=served, usage=usage,
            failure_class=None, request_sha256=request.sha256,
            response_sha256=response.sha256, artifacts=artifacts, parsed=parsed)

    # -- helpers -----------------------------------------------------------

    def _open_attempt(self, adapter: Any, job_id: str, route: str,
                      requested_model: str) -> str:
        attempt = model.Attempt(
            attempt_id=new_id('attempt'), job_id=job_id,
            adapter=getattr(adapter, 'name', 'unknown'), route=route,
            requested_model=requested_model,
            ordinal=self.repository.next_attempt_ordinal(job_id))
        self.repository.add_attempt(attempt)
        return attempt.attempt_id

    def _seal(self, kind: str, call_id: str, value: Mapping[str, Any]
              ) -> dict[str, Any]:
        directory = os.path.join(self.evidence_dir, call_id)
        os.makedirs(directory, exist_ok=True)
        receipt = seal(os.path.join(directory, '%s.json' % kind), dict(value))
        artifact = model.Artifact(
            artifact_id=new_id('artifact'), campaign_id=self.campaign_id,
            kind=kind, path=receipt['path'], sha256=receipt['sha256'])
        self.repository.record_artifact(artifact, call_id=call_id)
        return receipt

    def _finalize(self, call: model.Call, state: str, usage: Mapping[str, Any],
                  served_model: str | None, request_sha: str | None,
                  response_sha: str | None,
                  failure_class: str | None) -> None:
        """Write the terminal row to *both* accounting authorities, once."""
        self.repository.finalize_call(
            call.call_id, state=state, telemetry=usage,
            served_model=served_model, request_sha256=request_sha,
            response_sha256=response_sha, failure_class=failure_class)
        self.ledger.finalize(
            {'reservation_id': call.reservation_id},
            {'cost_evaluable': bool(usage.get('cost_evaluable')),
             'input_tokens': int(usage.get('input_tokens') or 0),
             'output_tokens': int(usage.get('output_tokens') or 0),
             'observed_cost_usd': float(usage.get('observed_cost_usd') or 0.0)},
            evidence={'route': call.route, 'served_model': served_model,
                      'request_sha256': request_sha,
                      'response_sha256': response_sha,
                      'failure_class': failure_class})

    def _finalize_failure(self, call: model.Call,
                          request: providers.ProviderRequest,
                          artifacts: dict[str, dict[str, Any]],
                          failure_class: str, detail: str, state: str, *,
                          response: providers.ProviderResponse | None = None,
                          usage: Mapping[str, Any] | None = None) -> CallOutcome:
        """Seal the failure and account the call terminally, exactly once."""
        effective = dict(usage) if usage else {
            'cost_evaluable': False, 'input_tokens': 0, 'output_tokens': 0,
            'observed_cost_usd': 0.0, 'cost_basis': 'unevaluable'}
        receipt = self._seal('audit', call.call_id, {
            'schema': 'pwg.pipeline.call_failure.v1',
            'route': call.route, 'failure_class': failure_class,
            'detail': detail, 'requested_model': call.requested_model,
            'served_model': response.served_model if response else None,
            'request_sha256': request.sha256,
            'response_sha256': response.sha256 if response else None,
            'usage': effective,
        })
        artifacts['failure'] = receipt
        current = self.repository.call_state(call.call_id)
        if current != state:
            self.repository.transition_call(call.call_id, current, state)
        self._finalize(call, state, effective,
                       response.served_model if response else None,
                       request.sha256,
                       response.sha256 if response else None, failure_class)
        return CallOutcome(
            call_id=call.call_id, state=state, route=call.route,
            requested_model=call.requested_model,
            served_model=response.served_model if response else None,
            usage=effective, failure_class=failure_class,
            request_sha256=request.sha256,
            response_sha256=response.sha256 if response else None,
            artifacts=artifacts, parsed=None)


__all__ = [
    'SCHEMA', 'PaidCallKernel', 'CallOutcome', 'KernelRefusal', 'GlobalStop',
    'DEFAULT_TIMEOUT_MS', 'DEFAULT_MAX_OUTPUT_TOKENS',
    'FAILURE_BUDGET', 'FAILURE_CEILING', 'FAILURE_TIMEOUT',
    'FAILURE_MALFORMED', 'FAILURE_UNEVALUABLE', 'FAILURE_ROUTE',
    'FAILURE_UNAVAILABLE', 'FAILURE_EXCEPTION',
]
