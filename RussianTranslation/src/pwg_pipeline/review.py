"""Independent review packet and receipt (step 11, V12).

The packet seals, in one hash-bound bundle, everything a reviewer needs to
approve the money and canonical-store paths: the schema/transition summary,
replay diffs, the fault matrix, the recursive-validation fence report, canary
envelopes and accounting, shim parity, the writer-disable diff, and the rollback
procedure.

The receipt must be signed by somebody **other than the implementer**, and
``verify`` refuses a receipt that is unbound, self-signed, or bound to a
different bundle -- so an unsigned Wave-1 close reports honestly rather than
quietly passing.
"""
from __future__ import annotations

import os
from typing import Any, Mapping, Sequence

from . import faults, model, promotion
from .evidence import canonical_sha256, read_sealed, seal

SCHEMA = 'pwg.pipeline.review.v1'
RECEIPT_SCHEMA = 'pwg.pipeline.review_receipt.v1'

REQUIRED_SECTIONS: tuple[str, ...] = (
    'schema_summary', 'replay', 'fault_matrix', 'validation_fence',
    'shadow', 'canary', 'shim_parity', 'writer_disable', 'rollback',
)


class ReviewRefusal(RuntimeError):
    """A packet or receipt did not meet the independent-review bar."""


def schema_summary() -> dict[str, Any]:
    """The transition graph a reviewer signs off on, not prose about it."""
    return {
        'job_states': list(model.JOB_STATES),
        'job_transitions': {state: sorted(following) for state, following
                            in sorted(model.JOB_TRANSITIONS.items())},
        'call_states': list(model.CALL_STATES),
        'call_terminal_states': sorted(model.CALL_TERMINAL_STATES),
        'promotion_phases': list(model.PROMOTION_STATES),
        'billable_routes': sorted(model.BILLABLE_ROUTES),
        'fault_points': list(faults.FAULT_POINTS),
        'canonical_fence': list(promotion.CANONICAL_FENCE),
    }


def build_packet(*, commit: str, implementer: str,
                 replay_report: Mapping[str, Any],
                 fault_matrix: Mapping[str, Any],
                 validation_fence: Mapping[str, Any],
                 shadow: Mapping[str, Any],
                 canary: Mapping[str, Any],
                 shim_parity: Mapping[str, Any],
                 writer_disable: Mapping[str, Any],
                 rollback: Mapping[str, Any]) -> dict[str, Any]:
    packet = {
        'schema': SCHEMA,
        'commit': commit,
        'implementer': implementer,
        'schema_summary': schema_summary(),
        'replay': dict(replay_report),
        'fault_matrix': dict(fault_matrix),
        'validation_fence': dict(validation_fence),
        'shadow': dict(shadow),
        'canary': dict(canary),
        'shim_parity': dict(shim_parity),
        'writer_disable': dict(writer_disable),
        'rollback': dict(rollback),
    }
    missing = [name for name in REQUIRED_SECTIONS if not packet.get(name)]
    if missing:
        raise ReviewRefusal('review packet lacks %s' % ', '.join(missing))
    packet['bundle_sha256'] = canonical_sha256(
        {name: packet[name] for name in REQUIRED_SECTIONS})
    return packet


def seal_packet(path: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    return seal(path, dict(packet))


def sign(packet: Mapping[str, Any], *, reviewer: str,
         findings: Sequence[str] = (), disposition: str = 'approved'
         ) -> dict[str, Any]:
    """Produce a hash-bound receipt.  Self-signing is refused here, not later."""
    if reviewer == packet.get('implementer'):
        raise ReviewRefusal(
            'the implementer (%s) may not sign their own review receipt'
            % reviewer)
    return {
        'schema': RECEIPT_SCHEMA,
        'reviewer': reviewer,
        'commit': packet['commit'],
        'bundle_sha256': packet['bundle_sha256'],
        'findings': list(findings),
        'disposition': disposition,
    }


def verify(packet_path: str, receipt_path: str) -> dict[str, Any]:
    """Verify a receipt against its packet.  Refuses anything unbound."""
    for path in (packet_path, receipt_path):
        if not os.path.exists(path):
            raise ReviewRefusal('missing review artifact: %s' % path)
    packet = read_sealed(packet_path)
    receipt = read_sealed(receipt_path)
    recomputed = canonical_sha256(
        {name: packet[name] for name in REQUIRED_SECTIONS})
    if recomputed != packet.get('bundle_sha256'):
        raise ReviewRefusal('the packet bundle hash does not match its content')
    try:
        # One receipt contract for review and promotion; re-raised as a review
        # refusal so a caller of `verify` handles a single exception type.
        promotion.verify_receipt(receipt, commit=str(packet['commit']),
                                 implementer=str(packet['implementer']))
    except promotion.PromotionRefusal as exc:
        raise ReviewRefusal(str(exc)) from exc
    return {
        'schema': 'pwg.pipeline.review_verification.v1',
        'commit': packet['commit'],
        'reviewer': receipt['reviewer'],
        'bundle_sha256': packet['bundle_sha256'],
        'findings': receipt.get('findings', []),
        'verified': True,
    }


def cutover_verdict(*, offline_green: bool, replay_exact: bool,
                    faults_green: bool, validation_fenced: bool,
                    shadow_clean: bool, canary_green: bool,
                    receipt_verified: bool) -> dict[str, Any]:
    """``GO`` / ``PARTIAL`` / ``NO-GO`` per the verification document.

    ``GO`` requires V1-V13.  ``PARTIAL`` preserves landed offline
    infrastructure but authorizes no legacy-writer shutdown.  ``NO-GO``
    preserves evidence and leaves the existing production route authoritative.
    """
    offline = [offline_green, replay_exact, faults_green, validation_fenced,
               shadow_clean]
    if not all(offline):
        verdict = 'NO-GO'
    elif canary_green and receipt_verified:
        verdict = 'GO'
    else:
        verdict = 'PARTIAL'
    return {
        'schema': 'pwg.pipeline.cutover.v1',
        'verdict': verdict,
        'offline_green': bool(offline_green),
        'replay_exact': bool(replay_exact),
        'faults_green': bool(faults_green),
        'validation_fenced': bool(validation_fenced),
        'shadow_clean': bool(shadow_clean),
        'canary_green': bool(canary_green),
        'receipt_verified': bool(receipt_verified),
        'authorizes_writer_disable': verdict == 'GO',
    }


__all__ = [
    'SCHEMA', 'RECEIPT_SCHEMA', 'REQUIRED_SECTIONS', 'ReviewRefusal',
    'schema_summary', 'build_packet', 'seal_packet', 'sign', 'verify',
    'cutover_verdict',
]
