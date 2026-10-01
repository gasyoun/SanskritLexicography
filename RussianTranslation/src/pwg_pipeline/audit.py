"""Pure audit: sealed artifacts in, sealed verdict out (step 4, R2.4).

The module deliberately has **no filesystem-mutation surface**.  It cannot
rename a file, append a denylist, refill a quarantine, change coordinator state,
or touch canonical data -- those effects now belong to
[`apply.py`](apply.py), and a caller that wants one has to say so explicitly.

The current [`src/pilot/audit_window.py`](../pilot/audit_window.py) result is
translated into the new verdict model here *without* invoking any of its
mutating options, so verdicts stay comparable across the cutover (V9).
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from . import model, validation
from .evidence import canonical_sha256, read_sealed
from .repository import new_id

SCHEMA = 'pwg.pipeline.audit.v1'
AUDIT_VERSION = 'pwg_pipeline.audit.v1'

# Reason codes. Stable: they end up inside sealed, compared evidence.
REASON_EMPTY_TARGET = 'empty_target'
REASON_MISSING_FRAGMENT = 'missing_fragment'
REASON_PLACEHOLDER_RESIDUE = 'placeholder_residue'
REASON_UNEVALUABLE_USAGE = 'unevaluable_usage'
REASON_CALL_FAILED = 'call_failed'
REASON_ROUTE_MISMATCH = 'route_mismatch'
REASON_NO_RESULT = 'no_result_artifact'


def verdict_for_result(result: Mapping[str, Any], *,
                       expected_fragment_ids: Sequence[str]) -> dict[str, Any]:
    """Compute one pure verdict from a sealed result artifact.

    Returns a plain dict; persistence and effects are somebody else's job.
    """
    reasons: list[str] = []
    detail: dict[str, Any] = {}

    usage = result.get('usage') or {}
    if not usage.get('cost_evaluable'):
        reasons.append(REASON_UNEVALUABLE_USAGE)

    requested = result.get('requested_model')
    served = result.get('served_model')
    if requested and served and requested != served:
        reasons.append(REASON_ROUTE_MISMATCH)
        detail['route'] = {'requested': requested, 'served': served}

    parsed = result.get('parsed') or {}
    rows = parsed.get('fragments') if isinstance(parsed, Mapping) else None
    rows = rows if isinstance(rows, list) else []
    by_id = {str(row.get('fragment_id')): row for row in rows
             if isinstance(row, Mapping) and row.get('fragment_id')}

    missing = [str(fid) for fid in expected_fragment_ids if fid not in by_id]
    if missing:
        reasons.append(REASON_MISSING_FRAGMENT)
        detail['missing_fragment_ids'] = sorted(missing)

    empty = sorted(fid for fid, row in by_id.items()
                   if not str(row.get('target_string') or '').strip())
    if empty:
        reasons.append(REASON_EMPTY_TARGET)
        detail['empty_fragment_ids'] = empty

    residue = validation.scan_value(parsed, '$.parsed')
    placeholder = [item for item in residue
                   if item['code'] in (validation.UNRESOLVED_PLACEHOLDER,
                                       validation.REGISTERED_SENTINEL)]
    if placeholder:
        reasons.append(REASON_PLACEHOLDER_RESIDUE)
        detail['placeholder_paths'] = [item['path'] for item in placeholder]

    if REASON_UNEVALUABLE_USAGE in reasons or REASON_ROUTE_MISMATCH in reasons:
        verdict_class = model.VERDICT_INCONCLUSIVE
    elif REASON_PLACEHOLDER_RESIDUE in reasons:
        verdict_class = model.VERDICT_DEFECT
    elif reasons:
        verdict_class = model.VERDICT_REQUEUE
    else:
        verdict_class = model.VERDICT_CLEAN

    return {
        'schema': SCHEMA,
        'validator_version': AUDIT_VERSION,
        'verdict_class': verdict_class,
        'reasons': sorted(set(reasons)),
        'detail': detail,
        'fragments_seen': sorted(by_id),
    }


def verdict_for_failure(failure: Mapping[str, Any]) -> dict[str, Any]:
    """A terminally-failed call still gets a pure, sealed verdict."""
    failure_class = str(failure.get('failure_class') or 'unknown')
    reasons = [REASON_CALL_FAILED]
    if failure_class in ('unevaluable_usage',):
        reasons.append(REASON_UNEVALUABLE_USAGE)
    if failure_class in ('route_substitution',):
        reasons.append(REASON_ROUTE_MISMATCH)
    inconclusive = REASON_UNEVALUABLE_USAGE in reasons \
        or REASON_ROUTE_MISMATCH in reasons
    return {
        'schema': SCHEMA,
        'validator_version': AUDIT_VERSION,
        'verdict_class': (model.VERDICT_INCONCLUSIVE if inconclusive
                          else model.VERDICT_REQUEUE),
        'reasons': sorted(set(reasons)),
        'detail': {'failure_class': failure_class,
                   'detail': failure.get('detail')},
        'fragments_seen': [],
    }


def audit_call(repository, *, job_id: str, campaign_id: str,
               result_path: str | None = None,
               failure_path: str | None = None,
               expected_fragment_ids: Sequence[str] = ()) -> model.Verdict:
    """Read sealed artifacts, compute a verdict, and record it.

    Recording a verdict is a database write, not a filesystem mutation: the
    audited artifacts and the tree around them are untouched, which is what V5
    pins with a before/after tree digest.
    """
    if result_path:
        artifact = read_sealed(result_path)
        computed = verdict_for_result(
            artifact, expected_fragment_ids=expected_fragment_ids)
        bound = artifact.get('response_sha256') or canonical_sha256(artifact)
    elif failure_path:
        artifact = read_sealed(failure_path)
        computed = verdict_for_failure(artifact)
        bound = artifact.get('request_sha256') or canonical_sha256(artifact)
    else:
        raise ValueError('audit_call needs a result or a failure artifact')

    verdict = model.Verdict(
        verdict_id=new_id('verdict'), job_id=job_id,
        verdict_class=computed['verdict_class'],
        result_artifact_sha256=str(bound),
        validator_version=computed['validator_version'],
        reasons=tuple(computed['reasons']))
    repository.record_verdict(verdict)
    return verdict


def translate_legacy_verdict(legacy: Mapping[str, Any]) -> str:
    """Map an ``audit_window.py``-shaped result onto a verdict class.

    Called with the *result* of the existing gate, never with its mutating
    options; the legacy module keeps its behavior and this keeps the two
    comparable during the shadow interval.
    """
    if legacy.get('quarantine') or legacy.get('defect'):
        return model.VERDICT_DEFECT
    if legacy.get('requeue') or legacy.get('missing'):
        return model.VERDICT_REQUEUE
    if legacy.get('unevaluable') or legacy.get('cost_evaluable') is False:
        return model.VERDICT_INCONCLUSIVE
    if legacy.get('clean'):
        return model.VERDICT_CLEAN
    return model.VERDICT_INCONCLUSIVE


def summarize(verdicts: Sequence[model.Verdict]) -> dict[str, Any]:
    counts: dict[str, int] = {name: 0 for name in model.VERDICT_CLASSES}
    for verdict in verdicts:
        counts[verdict.verdict_class] = counts.get(verdict.verdict_class, 0) + 1
    return {
        'schema': 'pwg.pipeline.audit_summary.v1',
        'validator_version': AUDIT_VERSION,
        'total': len(verdicts),
        'by_class': counts,
        'clean_only': all(v.verdict_class == model.VERDICT_CLEAN
                          for v in verdicts) and bool(verdicts),
    }


__all__ = [
    'SCHEMA', 'AUDIT_VERSION', 'verdict_for_result', 'verdict_for_failure',
    'audit_call', 'translate_legacy_verdict', 'summarize',
    'REASON_EMPTY_TARGET', 'REASON_MISSING_FRAGMENT',
    'REASON_PLACEHOLDER_RESIDUE', 'REASON_UNEVALUABLE_USAGE',
    'REASON_CALL_FAILED', 'REASON_ROUTE_MISMATCH', 'REASON_NO_RESULT',
]
