"""Explicit effects (H3714 Wave 1, implementation step 4.2).

Audit computes; ApplyService *acts* -- and only on an intent an operator asked
for by name.  ``requeue``, ``quarantine`` and ``refill`` are recorded as
transactional intents keyed by ``(verdict, intent)``, so replaying an apply is a
no-op rather than a second effect.  ``promote`` is never executed here: it is
delegated whole to [`promotion.py`](promotion.py), which owns the coordinator
journal (R2.3).
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from . import faults, model
from .evidence import canonical_sha256
from .repository import Repository, RepositoryError

SCHEMA = 'pwg.pipeline.apply.v1'


class ApplyRefusal(RuntimeError):
    """An intent was refused: wrong verdict class, wrong state, or fenced."""


# Which verdict classes may legally produce which intent.
LEGAL_INTENTS: dict[str, frozenset[str]] = {
    model.VERDICT_CLEAN: frozenset({model.INTENT_PROMOTE}),
    model.VERDICT_REQUEUE: frozenset({model.INTENT_REQUEUE,
                                      model.INTENT_REFILL}),
    model.VERDICT_DEFECT: frozenset({model.INTENT_QUARANTINE}),
    model.VERDICT_INCONCLUSIVE: frozenset({model.INTENT_QUARANTINE}),
}


class ApplyService:
    """Record and apply explicit intents against an accepted verdict."""

    def __init__(self, repository: Repository, *,
                 fault_hook: faults.FaultHook | None = None) -> None:
        self.repository = repository
        self.fault_hook = fault_hook

    def record(self, *, verdict: model.Verdict, intent: str,
               payload: Mapping[str, Any] | Sequence[Any]) -> str:
        """Record one intent transactionally; identical replays are no-ops."""
        model.require_choice(intent, model.APPLY_INTENTS, 'apply.intent')
        allowed = LEGAL_INTENTS.get(verdict.verdict_class, frozenset())
        if intent not in allowed:
            raise ApplyRefusal(
                'intent %r is illegal for a %r verdict (allowed: %s)'
                % (intent, verdict.verdict_class,
                   ', '.join(sorted(allowed)) or 'none'))
        payload_sha = canonical_sha256(payload)
        intent_id = self.repository.record_intent(
            verdict_id=verdict.verdict_id, job_id=verdict.job_id,
            intent=intent, payload_sha256=payload_sha)
        faults.fault(self.fault_hook, faults.AFTER_APPLY_INTENT_COMMIT)
        return intent_id

    def apply_requeue(self, verdict: model.Verdict,
                      payload: Mapping[str, Any]) -> str:
        """Return the job to ``planned`` through the recorded intent only."""
        intent_id = self.record(verdict=verdict,
                                intent=model.INTENT_REQUEUE, payload=payload)
        state = self.repository.job_state(verdict.job_id)
        if state == model.AUDITED:
            self.repository.transition_job(
                verdict.job_id, model.AUDITED, model.NEEDS_REQUEUE,
                reason='apply:requeue', evidence_sha=verdict.result_artifact_sha256)
            state = model.NEEDS_REQUEUE
        if state == model.NEEDS_REQUEUE:
            self.repository.transition_job(
                verdict.job_id, model.NEEDS_REQUEUE, model.PLANNED,
                reason='apply:requeue')
        self.repository.mark_intent_applied(intent_id)
        return intent_id

    def apply_quarantine(self, verdict: model.Verdict,
                         payload: Mapping[str, Any]) -> str:
        """Block the job.  No file is renamed and no denylist is appended."""
        intent_id = self.record(verdict=verdict,
                                intent=model.INTENT_QUARANTINE, payload=payload)
        state = self.repository.job_state(verdict.job_id)
        if state == model.AUDITED:
            self.repository.transition_job(
                verdict.job_id, model.AUDITED, model.BLOCKED,
                reason='apply:quarantine',
                evidence_sha=verdict.result_artifact_sha256)
        self.repository.mark_intent_applied(intent_id)
        return intent_id

    def apply_refill(self, verdict: model.Verdict,
                     payload: Mapping[str, Any]) -> str:
        """Refill is a *prepared* intent; the write goes through promotion."""
        intent_id = self.record(verdict=verdict,
                                intent=model.INTENT_REFILL, payload=payload)
        state = self.repository.job_state(verdict.job_id)
        if state == model.AUDITED:
            self.repository.transition_job(
                verdict.job_id, model.AUDITED, model.NEEDS_REQUEUE,
                reason='apply:refill',
                evidence_sha=verdict.result_artifact_sha256)
        self.repository.mark_intent_applied(intent_id)
        return intent_id

    def prepare_promotion(self, verdict: model.Verdict,
                          rows: Sequence[Mapping[str, Any]]) -> str:
        """Record the promote intent.  Execution belongs to PromotionService."""
        if verdict.verdict_class != model.VERDICT_CLEAN:
            raise ApplyRefusal('only a clean verdict may be promoted (got %r)'
                               % verdict.verdict_class)
        intent_id = self.record(verdict=verdict, intent=model.INTENT_PROMOTE,
                                payload=list(rows))
        state = self.repository.job_state(verdict.job_id)
        if state == model.AUDITED:
            self.repository.transition_job(
                verdict.job_id, model.AUDITED, model.AWAITING_REVIEW,
                reason='apply:promote-prepared',
                evidence_sha=verdict.result_artifact_sha256)
        return intent_id

    def dispatch(self, verdict: model.Verdict, intent: str,
                 payload: Mapping[str, Any] | Sequence[Any]) -> str:
        handlers = {
            model.INTENT_REQUEUE: self.apply_requeue,
            model.INTENT_QUARANTINE: self.apply_quarantine,
            model.INTENT_REFILL: self.apply_refill,
        }
        if intent == model.INTENT_PROMOTE:
            return self.prepare_promotion(verdict, list(payload))  # type: ignore[arg-type]
        handler = handlers.get(intent)
        if handler is None:
            raise ApplyRefusal('unknown intent: %r' % (intent,))
        return handler(verdict, payload)  # type: ignore[arg-type]


def intent_for(verdict_class: str) -> str | None:
    """The single default intent for a verdict class, or None when ambiguous."""
    allowed = LEGAL_INTENTS.get(verdict_class, frozenset())
    return next(iter(allowed)) if len(allowed) == 1 else None


__all__ = ['SCHEMA', 'ApplyService', 'ApplyRefusal', 'LEGAL_INTENTS',
           'intent_for', 'RepositoryError']
