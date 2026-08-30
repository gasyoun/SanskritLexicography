"""Unified PWG control-plane domain model (H3714 Wave 1, decision R2.5).

``Campaign -> Job -> Attempt -> Call -> Artifact -> Verdict -> Promotion``.

Card work and fragment work differ by *cardinality*, not by schema: a card job
may own one call, a split card owns child jobs, and one provider batch call may
cover several jobs through the ``call_jobs`` join table.  Call count is never
inferred from returned rows (retired architecture item 2).

This module is pure: it defines entities and the legal transition graph and
raises on an illegal move.  It performs no I/O.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Mapping

SCHEMA = 'pwg.pipeline.model.v1'

# --- job lifecycle ---------------------------------------------------------

PLANNED = 'planned'
PREPARED = 'prepared'
RESERVED = 'reserved'
RUNNING = 'running'
CAPTURED = 'captured'
AUDITED = 'audited'
NEEDS_REQUEUE = 'needs_requeue'
BLOCKED = 'blocked'
AWAITING_REVIEW = 'awaiting_review'
FAILED = 'failed'
APPLY_PREPARED = 'apply_prepared'
STORE_COMMITTED = 'store_committed'
DERIVED_VALIDATED = 'derived_validated'
COORDINATOR_COMMITTED = 'coordinator_committed'
COMPLETE = 'complete'

JOB_STATES: tuple[str, ...] = (
    PLANNED, PREPARED, RESERVED, RUNNING, CAPTURED, AUDITED,
    NEEDS_REQUEUE, BLOCKED, AWAITING_REVIEW, FAILED,
    APPLY_PREPARED, STORE_COMMITTED, DERIVED_VALIDATED,
    COORDINATOR_COMMITTED, COMPLETE,
)

TERMINAL_STATES: frozenset[str] = frozenset({COMPLETE, FAILED, BLOCKED})

# Every legal move. A transition may advance only when its required artifact
# hashes exist -- that precondition is enforced by the repository, not here.
JOB_TRANSITIONS: dict[str, frozenset[str]] = {
    PLANNED: frozenset({PREPARED, BLOCKED, FAILED}),
    PREPARED: frozenset({RESERVED, BLOCKED, FAILED}),
    RESERVED: frozenset({RUNNING, FAILED}),
    RUNNING: frozenset({CAPTURED, FAILED}),
    CAPTURED: frozenset({AUDITED, FAILED}),
    AUDITED: frozenset({AWAITING_REVIEW, NEEDS_REQUEUE, BLOCKED, FAILED}),
    NEEDS_REQUEUE: frozenset({PLANNED, BLOCKED}),
    AWAITING_REVIEW: frozenset({APPLY_PREPARED, NEEDS_REQUEUE, BLOCKED}),
    APPLY_PREPARED: frozenset({STORE_COMMITTED, BLOCKED}),
    STORE_COMMITTED: frozenset({DERIVED_VALIDATED}),
    DERIVED_VALIDATED: frozenset({COORDINATOR_COMMITTED}),
    COORDINATOR_COMMITTED: frozenset({COMPLETE}),
    COMPLETE: frozenset(),
    FAILED: frozenset(),
    BLOCKED: frozenset({PLANNED}),
}

# Once a promotion has begun the only legal continuation is forward through the
# journal; a restart reconciles, it never re-plans (architecture, state model).
PROMOTION_STATES: tuple[str, ...] = (
    APPLY_PREPARED, STORE_COMMITTED, DERIVED_VALIDATED,
    COORDINATOR_COMMITTED, COMPLETE,
)

# --- call lifecycle --------------------------------------------------------

CALL_RESERVED = 'reserved'
CALL_DISPATCHED = 'dispatched'
CALL_SUCCEEDED = 'succeeded'
CALL_REFUSED = 'refused'
CALL_TIMED_OUT = 'timed_out'
CALL_MALFORMED = 'malformed'
CALL_ERRORED = 'errored'

CALL_STATES: tuple[str, ...] = (
    CALL_RESERVED, CALL_DISPATCHED, CALL_SUCCEEDED, CALL_REFUSED,
    CALL_TIMED_OUT, CALL_MALFORMED, CALL_ERRORED,
)

# Every non-reserved, non-dispatched state is terminal: the kernel finalizes
# exactly one call record on success, refusal, malformed output, timeout, or
# exception (architecture, boundary rule 3).
CALL_TERMINAL_STATES: frozenset[str] = frozenset({
    CALL_SUCCEEDED, CALL_REFUSED, CALL_TIMED_OUT, CALL_MALFORMED, CALL_ERRORED,
})

CALL_TRANSITIONS: dict[str, frozenset[str]] = {
    CALL_RESERVED: frozenset({CALL_DISPATCHED, CALL_REFUSED, CALL_ERRORED}),
    # `refused` is reachable after dispatch too: an unavailable credential or a
    # provider-side rejection is a refusal, not an error, and it still finalizes
    # exactly one call record.
    CALL_DISPATCHED: frozenset({
        CALL_SUCCEEDED, CALL_REFUSED, CALL_TIMED_OUT, CALL_MALFORMED,
        CALL_ERRORED}),
    CALL_SUCCEEDED: frozenset(),
    CALL_REFUSED: frozenset(),
    CALL_TIMED_OUT: frozenset(),
    CALL_MALFORMED: frozenset(),
    CALL_ERRORED: frozenset(),
}

# --- verdict / intent vocabularies ----------------------------------------

VERDICT_CLEAN = 'clean'
VERDICT_REQUEUE = 'requeue'
VERDICT_DEFECT = 'defect'
VERDICT_INCONCLUSIVE = 'inconclusive'
VERDICT_CLASSES: tuple[str, ...] = (
    VERDICT_CLEAN, VERDICT_REQUEUE, VERDICT_DEFECT, VERDICT_INCONCLUSIVE)

INTENT_REQUEUE = 'requeue'
INTENT_QUARANTINE = 'quarantine'
INTENT_REFILL = 'refill'
INTENT_PROMOTE = 'promote'
APPLY_INTENTS: tuple[str, ...] = (
    INTENT_REQUEUE, INTENT_QUARANTINE, INTENT_REFILL, INTENT_PROMOTE)

JOB_KIND_CARD = 'card'
JOB_KIND_FRAGMENT = 'fragment'
JOB_KINDS: tuple[str, ...] = (JOB_KIND_CARD, JOB_KIND_FRAGMENT)

ARTIFACT_KINDS: tuple[str, ...] = (
    'manifest', 'input', 'request', 'response', 'result', 'audit',
    'receipt', 'report', 'review',
)

# Wave-1 adapters. `deterministic` and `imported_draft` are non-billable
# provenance routes and must stay distinguishable in every receipt (V3).
ROUTE_XAI = 'xai-tm'
ROUTE_DEEPSEEK = 'deepseek-tm'
ROUTE_CLAUDE_SHADOW = 'claude-headless-shadow'
ROUTE_DETERMINISTIC = 'deterministic-reuse'
ROUTE_IMPORTED = 'imported-draft'
ROUTES: tuple[str, ...] = (
    ROUTE_XAI, ROUTE_DEEPSEEK, ROUTE_CLAUDE_SHADOW,
    ROUTE_DETERMINISTIC, ROUTE_IMPORTED,
)
BILLABLE_ROUTES: frozenset[str] = frozenset({ROUTE_XAI, ROUTE_DEEPSEEK})

SHA_RE = re.compile(r'^[0-9a-f]{64}$')


class ModelError(ValueError):
    """A domain-rule violation that must never reach persistence."""


class TransitionError(ModelError):
    """An illegal lifecycle move."""


def require_sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or not SHA_RE.match(value):
        raise ModelError('%s must be a lowercase sha256 hex digest' % field)
    return value


def require_choice(value: Any, allowed: tuple[str, ...], field: str) -> str:
    if value not in allowed:
        raise ModelError('%s must be one of %s (got %r)'
                         % (field, ', '.join(allowed), value))
    return str(value)


def assert_job_transition(current: str, following: str) -> None:
    """Raise unless ``current -> following`` is a legal job move."""
    if current not in JOB_TRANSITIONS:
        raise TransitionError('unknown job state: %r' % (current,))
    if following not in JOB_STATES:
        raise TransitionError('unknown job state: %r' % (following,))
    if following not in JOB_TRANSITIONS[current]:
        raise TransitionError('illegal job transition %s -> %s'
                              % (current, following))


def assert_call_transition(current: str, following: str) -> None:
    """Raise unless ``current -> following`` is a legal call move."""
    if current not in CALL_TRANSITIONS:
        raise TransitionError('unknown call state: %r' % (current,))
    if following not in CALL_STATES:
        raise TransitionError('unknown call state: %r' % (following,))
    if following not in CALL_TRANSITIONS[current]:
        raise TransitionError('illegal call transition %s -> %s'
                              % (current, following))


def reachable_job_states(start: str = PLANNED) -> frozenset[str]:
    """Every job state reachable from ``start`` (used to pin the graph)."""
    seen: set[str] = set()
    stack = [start]
    while stack:
        state = stack.pop()
        if state in seen:
            continue
        seen.add(state)
        stack.extend(JOB_TRANSITIONS.get(state, frozenset()))
    return frozenset(seen)


@dataclasses.dataclass(frozen=True)
class Campaign:
    """Stable scope, language, budgets, fence, creator, lifecycle version."""

    campaign_id: str
    scope: str
    language: str
    route: str
    max_calls: int
    cost_ceiling_usd: float
    promotable: bool
    created_by: str
    lifecycle_version: str = 'pwg_pipeline.v1'
    fence: str = 'wave1'

    def __post_init__(self) -> None:
        if not self.campaign_id:
            raise ModelError('campaign_id is required')
        require_choice(self.route, ROUTES, 'campaign.route')
        if isinstance(self.max_calls, bool) or not isinstance(self.max_calls, int) \
                or self.max_calls < 0:
            raise ModelError('campaign.max_calls must be a non-negative integer')
        if isinstance(self.cost_ceiling_usd, bool) or \
                not isinstance(self.cost_ceiling_usd, (int, float)) or \
                self.cost_ceiling_usd < 0:
            raise ModelError('campaign.cost_ceiling_usd must be non-negative')
        if not isinstance(self.promotable, bool):
            raise ModelError('campaign.promotable must be boolean')


@dataclasses.dataclass(frozen=True)
class Job:
    """One whole card or fragment unit with provider-independent intent."""

    job_id: str
    campaign_id: str
    kind: str
    source_identity: str
    source_hash: str
    state: str = PLANNED
    parent_job_id: str | None = None

    def __post_init__(self) -> None:
        if not self.job_id:
            raise ModelError('job_id is required')
        require_choice(self.kind, JOB_KINDS, 'job.kind')
        require_choice(self.state, JOB_STATES, 'job.state')
        require_sha256(self.source_hash, 'job.source_hash')
        if not self.source_identity:
            raise ModelError('job.source_identity is required')
        if self.parent_job_id == self.job_id:
            raise ModelError('job cannot be its own parent')


@dataclasses.dataclass(frozen=True)
class Attempt:
    """One execution try: adapter, route, requested model, outcome."""

    attempt_id: str
    job_id: str
    adapter: str
    route: str
    requested_model: str
    ordinal: int
    outcome: str | None = None

    def __post_init__(self) -> None:
        if not self.attempt_id:
            raise ModelError('attempt_id is required')
        require_choice(self.route, ROUTES, 'attempt.route')
        if isinstance(self.ordinal, bool) or not isinstance(self.ordinal, int) \
                or self.ordinal < 1:
            raise ModelError('attempt.ordinal must be a positive integer')


@dataclasses.dataclass(frozen=True)
class Call:
    """One billable provider request, reserved before I/O, finalized once."""

    call_id: str
    attempt_id: str
    route: str
    requested_model: str
    reservation_id: str
    idempotency_key: str
    state: str = CALL_RESERVED
    served_model: str | None = None
    observed_cost_usd: float = 0.0
    cost_evaluable: bool = False

    def __post_init__(self) -> None:
        if not self.call_id:
            raise ModelError('call_id is required')
        require_choice(self.route, ROUTES, 'call.route')
        require_choice(self.state, CALL_STATES, 'call.state')
        if not self.reservation_id:
            raise ModelError('call.reservation_id is required: reserve before I/O')
        if not self.idempotency_key:
            raise ModelError('call.idempotency_key is required')
        if isinstance(self.observed_cost_usd, bool) or \
                not isinstance(self.observed_cost_usd, (int, float)) or \
                self.observed_cost_usd < 0:
            raise ModelError('call.observed_cost_usd must be non-negative')

    @property
    def is_terminal(self) -> bool:
        return self.state in CALL_TERMINAL_STATES


@dataclasses.dataclass(frozen=True)
class Artifact:
    """Immutable manifest/input/result/audit/receipt addressed by SHA-256."""

    artifact_id: str
    campaign_id: str
    kind: str
    path: str
    sha256: str
    media_type: str = 'application/json'

    def __post_init__(self) -> None:
        require_choice(self.kind, ARTIFACT_KINDS, 'artifact.kind')
        require_sha256(self.sha256, 'artifact.sha256')
        if not self.path:
            raise ModelError('artifact.path is required')


@dataclasses.dataclass(frozen=True)
class Verdict:
    """Pure gate output bound to exact input/result artifacts."""

    verdict_id: str
    job_id: str
    verdict_class: str
    result_artifact_sha256: str
    validator_version: str
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_choice(self.verdict_class, VERDICT_CLASSES, 'verdict.verdict_class')
        require_sha256(self.result_artifact_sha256, 'verdict.result_artifact_sha256')
        if not self.validator_version:
            raise ModelError('verdict.validator_version is required')


@dataclasses.dataclass(frozen=True)
class Promotion:
    """Journaled apply transaction with before/after hashes and phase."""

    promotion_id: str
    campaign_id: str
    phase: str
    store_path: str
    before_sha256: str | None = None
    after_sha256: str | None = None
    journal_path: str | None = None

    def __post_init__(self) -> None:
        require_choice(self.phase, PROMOTION_STATES, 'promotion.phase')
        if not self.store_path:
            raise ModelError('promotion.store_path is required')
        for name in ('before_sha256', 'after_sha256'):
            value = getattr(self, name)
            if value is not None:
                require_sha256(value, 'promotion.%s' % name)


def entity_from_row(row: Mapping[str, Any], cls: type) -> Any:
    """Build a frozen entity from a sqlite row-like mapping."""
    fields = {f.name for f in dataclasses.fields(cls)}
    return cls(**{k: row[k] for k in fields if k in row})


__all__ = [
    'SCHEMA', 'JOB_STATES', 'JOB_TRANSITIONS', 'TERMINAL_STATES',
    'PROMOTION_STATES', 'CALL_STATES', 'CALL_TRANSITIONS',
    'CALL_TERMINAL_STATES', 'VERDICT_CLASSES', 'APPLY_INTENTS', 'JOB_KINDS',
    'ARTIFACT_KINDS', 'ROUTES', 'BILLABLE_ROUTES',
    'ModelError', 'TransitionError',
    'assert_job_transition', 'assert_call_transition', 'reachable_job_states',
    'require_sha256', 'require_choice', 'entity_from_row',
    'Campaign', 'Job', 'Attempt', 'Call', 'Artifact', 'Verdict', 'Promotion',
    'PLANNED', 'PREPARED', 'RESERVED', 'RUNNING', 'CAPTURED', 'AUDITED',
    'NEEDS_REQUEUE', 'BLOCKED', 'AWAITING_REVIEW', 'FAILED', 'APPLY_PREPARED',
    'STORE_COMMITTED', 'DERIVED_VALIDATED', 'COORDINATOR_COMMITTED', 'COMPLETE',
    'CALL_RESERVED', 'CALL_DISPATCHED', 'CALL_SUCCEEDED', 'CALL_REFUSED',
    'CALL_TIMED_OUT', 'CALL_MALFORMED', 'CALL_ERRORED',
    'VERDICT_CLEAN', 'VERDICT_REQUEUE', 'VERDICT_DEFECT', 'VERDICT_INCONCLUSIVE',
    'INTENT_REQUEUE', 'INTENT_QUARANTINE', 'INTENT_REFILL', 'INTENT_PROMOTE',
    'JOB_KIND_CARD', 'JOB_KIND_FRAGMENT',
    'ROUTE_XAI', 'ROUTE_DEEPSEEK', 'ROUTE_CLAUDE_SHADOW',
    'ROUTE_DETERMINISTIC', 'ROUTE_IMPORTED',
]
