"""Named fault points at every irreversible boundary (step 9, V4/V6).

Production code calls :func:`fault` at a named boundary; in production the hook
is ``None`` and the call is a no-op.  Tests install a hook that terminates the
process (or raises) at exactly one point, then reopen the state and prove the
recovery is idempotent.

The point names are a *contract*: the fault-injection matrix in the verification
document names these exact strings, and :data:`FAULT_POINTS` is asserted against
the matrix, so a boundary cannot be silently dropped.
"""
from __future__ import annotations

import os
from typing import Callable, Iterator

SCHEMA = 'pwg.pipeline.faults.v1'

AFTER_RESERVATION = 'after_reservation'
AFTER_PROVIDER_RESPONSE = 'after_provider_response'
AFTER_USAGE_CAPTURE = 'after_usage_capture'
AFTER_ARTIFACT_SEAL = 'after_artifact_seal'
AFTER_VERDICT_COMMIT = 'after_verdict_commit'
AFTER_APPLY_INTENT_COMMIT = 'after_apply_intent_commit'
AFTER_STORE_BACKUP = 'after_store_backup'
AFTER_STORE_COMMIT = 'after_store_commit'
AFTER_DERIVED_REBUILD = 'after_derived_rebuild'
AFTER_JOURNAL_ADVANCE = 'after_journal_advance'
BEFORE_CAMPAIGN_COMMIT = 'before_campaign_commit'

FAULT_POINTS: tuple[str, ...] = (
    AFTER_RESERVATION,
    AFTER_PROVIDER_RESPONSE,
    AFTER_USAGE_CAPTURE,
    AFTER_ARTIFACT_SEAL,
    AFTER_VERDICT_COMMIT,
    AFTER_APPLY_INTENT_COMMIT,
    AFTER_STORE_BACKUP,
    AFTER_STORE_COMMIT,
    AFTER_DERIVED_REBUILD,
    AFTER_JOURNAL_ADVANCE,
    BEFORE_CAMPAIGN_COMMIT,
)

# Environment escape used by the subprocess crash tests: the child process is
# started with PWG_PIPELINE_FAULT=<point> and hard-exits there.
FAULT_ENV = 'PWG_PIPELINE_FAULT'
FAULT_EXIT_CODE = 97

FaultHook = Callable[[str], None]


class InjectedFault(RuntimeError):
    """A test-only fault fired at a named irreversible boundary."""

    def __init__(self, point: str) -> None:
        super().__init__('injected fault at %s' % point)
        self.point = point


def require_point(point: str) -> str:
    if point not in FAULT_POINTS:
        raise ValueError('unknown fault point: %r' % (point,))
    return point


def fault(hook: FaultHook | None, point: str) -> None:
    """Fire ``hook`` at ``point``; a no-op in production."""
    require_point(point)
    if hook is not None:
        hook(point)


def env_hook() -> FaultHook | None:
    """A hook that hard-exits the process at the point named in the environment.

    ``os._exit`` skips atexit handlers and buffer flushes on purpose: the crash
    tests must prove recovery from a genuinely abrupt death, not a clean exit.
    """
    wanted = os.environ.get(FAULT_ENV)
    if not wanted:
        return None
    require_point(wanted)

    def hook(point: str) -> None:
        if point == wanted:
            os._exit(FAULT_EXIT_CODE)

    return hook


def raising_hook(point: str) -> FaultHook:
    """A hook that raises :class:`InjectedFault` at exactly ``point``."""
    require_point(point)

    def hook(fired: str) -> None:
        if fired == point:
            raise InjectedFault(fired)

    return hook


def recording_hook(sink: list[str]) -> FaultHook:
    """A hook that records every boundary crossed, firing nothing."""

    def hook(point: str) -> None:
        sink.append(point)

    return hook


def iter_points() -> Iterator[str]:
    yield from FAULT_POINTS


__all__ = [
    'SCHEMA', 'FAULT_POINTS', 'FAULT_ENV', 'FAULT_EXIT_CODE', 'FaultHook',
    'InjectedFault', 'fault', 'require_point', 'env_hook', 'raising_hook',
    'recording_hook', 'iter_points',
    'AFTER_RESERVATION', 'AFTER_PROVIDER_RESPONSE', 'AFTER_USAGE_CAPTURE',
    'AFTER_ARTIFACT_SEAL', 'AFTER_VERDICT_COMMIT',
    'AFTER_APPLY_INTENT_COMMIT', 'AFTER_STORE_BACKUP', 'AFTER_STORE_COMMIT',
    'AFTER_DERIVED_REBUILD', 'AFTER_JOURNAL_ADVANCE', 'BEFORE_CAMPAIGN_COMMIT',
]
