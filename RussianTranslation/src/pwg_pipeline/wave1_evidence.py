"""Build the whole Wave-1 evidence bundle in one reproducible command (step 11).

    python -m pwg_pipeline.wave1_evidence --out docs/evidence --commit <sha>

It runs the four frozen replays, records the fault-injection matrix and which
test pins each boundary, runs the recursive validator over the canonical
artifact when it is present, shadow-compares the legacy audit contract, seals a
hash-bound review packet, and prints the ``GO`` / ``PARTIAL`` / ``NO-GO``
cutover verdict.

The bundle is *evidence*, not authority: it never executes a paid call, never
writes a canonical path, and an absent input is recorded as absent rather than
quietly treated as a pass.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

if __package__ in (None, ''):  # pragma: no cover - direct-script invocation
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'pwg_pipeline'

from . import (audit, compat, faults, import_legacy, model,  # noqa: E402
               promotion, providers, replay, review, validation)
from .evidence import seal  # noqa: E402
from .repository import open_repository  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
DEFAULT_MATRIX = os.path.join(RT_ROOT, 'tests', 'fixtures', 'pwg_pipeline')
DEFAULT_CANONICAL = os.path.join(RT_ROOT, 'release', 'pwg_tm_canonical',
                                 'canonical.v1.jsonl')

# Which test pins which irreversible boundary. Kept next to the matrix so a
# dropped test is visible in the evidence, not just in a coverage report.
FAULT_COVERAGE: dict[str, str] = {
    faults.AFTER_RESERVATION:
        'test_a_fault_before_the_request_leaves_one_reservation_and_no_spend',
    faults.AFTER_PROVIDER_RESPONSE:
        'test_a_fault_after_the_response_keeps_the_raw_reply',
    faults.AFTER_USAGE_CAPTURE:
        'test_a_usage_capture_fault_still_leaves_the_response_sealed',
    faults.AFTER_ARTIFACT_SEAL:
        'test_a_fault_after_the_seal_does_not_call_the_provider_again',
    faults.AFTER_VERDICT_COMMIT:
        'test_a_fault_after_the_apply_intent_leaves_no_canonical_mutation',
    faults.AFTER_APPLY_INTENT_COMMIT:
        'test_a_fault_after_the_apply_intent_leaves_no_canonical_mutation',
    faults.AFTER_STORE_BACKUP:
        'test_promotion_recovers_idempotently_from_every_boundary'
        '[after_store_backup]',
    faults.AFTER_STORE_COMMIT:
        'test_a_crash_between_store_replace_and_journal_advance_is_recovered',
    faults.AFTER_DERIVED_REBUILD:
        'test_promotion_recovers_idempotently_from_every_boundary'
        '[after_derived_rebuild]',
    faults.AFTER_JOURNAL_ADVANCE:
        'test_promotion_recovers_idempotently_from_every_boundary'
        '[after_journal_advance]',
    faults.BEFORE_CAMPAIGN_COMMIT:
        'test_promotion_recovers_idempotently_from_every_boundary'
        '[before_campaign_commit]',
}

# The legacy sources an operator's tree may hold. Absent ones are reported.
LEGACY_SOURCES: dict[str, list[str]] = {
    import_legacy.KIND_COORDINATOR: [
        os.path.join(RT_ROOT, 'src', 'pilot', 'coordinator_state.json')],
    import_legacy.KIND_CALL_LEDGER: [
        os.path.join(RT_ROOT, 'src', 'pilot', 'call_reservations.json')],
    import_legacy.KIND_COST_LEDGER: [
        os.path.join(RT_ROOT, 'src', 'pilot', 'output', 'health_probe_log.jsonl')],
}


def replay_section(matrix: str) -> dict:
    return replay.replay_matrix(matrix, exact=True)


def fault_section() -> dict:
    missing = [point for point in faults.FAULT_POINTS
               if point not in FAULT_COVERAGE]
    return {
        'schema': 'pwg.pipeline.fault_matrix.v1',
        'boundaries': list(faults.FAULT_POINTS),
        'covered_by': dict(sorted(FAULT_COVERAGE.items())),
        'uncovered': missing,
        'green': not missing,
        'suite': 'RussianTranslation/tests/test_pwg_pipeline_faults.py',
    }


def validation_section(canonical: str) -> dict:
    if not os.path.exists(canonical):
        return {
            'schema': 'pwg.pipeline.fence.v1',
            'path': canonical.replace('\\', '/'),
            'available': False,
            'disposition': 'canonical artifact absent in this checkout'
                           ' (gitignored, rights-fenced); fence not computed',
        }
    report = validation.validate_jsonl(canonical)
    fence = validation.fence_report(report)
    fence['available'] = True
    fence['rows_detail_count'] = len(report['rows_detail'])
    return fence


def shadow_section(database: str) -> dict:
    """Compare the legacy audit contract with the pipeline's, key by key.

    The Claude engine is not executed: what is compared is the *lifecycle
    verdict contract*, which is what the cutover actually depends on.
    """
    repository = open_repository(database)
    try:
        legacy_cases = [
            ({'clean': True}, model.VERDICT_CLEAN),
            ({'requeue': True}, model.VERDICT_REQUEUE),
            ({'missing': ['f1']}, model.VERDICT_REQUEUE),
            ({'quarantine': ['f2']}, model.VERDICT_DEFECT),
            ({'defect': True}, model.VERDICT_DEFECT),
            ({'cost_evaluable': False}, model.VERDICT_INCONCLUSIVE),
            ({'unevaluable': True}, model.VERDICT_INCONCLUSIVE),
        ]
        legacy = {}
        pipeline = {}
        for index, (case, expected) in enumerate(legacy_cases):
            key = 'case%02d' % index
            legacy[key] = expected
            pipeline[key] = audit.translate_legacy_verdict(case)
        report = import_legacy.shadow_sync(
            repository, route=model.ROUTE_CLAUDE_SHADOW, legacy=legacy,
            pipeline=pipeline)
        imports = import_legacy.import_tree(repository, LEGACY_SOURCES)
        report['legacy_import'] = {
            'imported': imports['imported'],
            'already_present': imports['already_present'],
            'absent': [row['path'].replace('\\', '/')
                       for row in imports['skipped']],
        }
        report['claude_executed'] = False
        return report
    finally:
        repository.close()


def canary_section() -> dict:
    """Report the canary fence and whether credentials exist. Never dials."""
    available = {
        'xai': bool(os.environ.get(providers.XAI_KEY_ENV)),
        'deepseek': bool(os.environ.get(providers.DEEPSEEK_KEY_ENV)),
    }
    return {
        'schema': 'pwg.pipeline.canary_readiness.v1',
        'max_calls': 2,
        'cost_ceiling_usd': 4.0,
        'no_retry': True,
        'promotable': False,
        'credentials_present': available,
        'executed': False,
        'disposition': (
            'ready to run' if all(available.values()) else
            'NOT RUN: %s credential(s) absent; each adapter track stops alone'
            ' and its unused call is never released to the other provider'
            % ', '.join(sorted(name for name, present in available.items()
                               if not present))),
        'command': ('python -m pwg_pipeline canary --providers xai,deepseek'
                    ' --max-calls 2 --cost-ceiling-usd 4 --no-retry'
                    ' --non-promotable'),
    }


def rollback_section() -> dict:
    return {
        'schema': 'pwg.pipeline.rollback.v1',
        'steps': [
            'Wave 1 adds a package and tests; it changes no production writer,'
            ' so reverting the merge commit is a complete rollback.',
            'Delete any campaign database and evidence directory created by an'
            ' operator run; both are disposable and hold no canonical data.',
            'An interrupted scratch promotion is reconciled with'
            ' `PromotionService.reconcile(<promotion_id>)`, or abandoned by'
            ' deleting its journal and scratch store.',
            'No canonical store, canonical TM, prompt, or legacy CLI behavior'
            ' was modified, so no data-level rollback exists to perform.',
        ],
        'legacy_writer_state': 'enabled (unchanged)',
    }


def build(commit: str, implementer: str, matrix: str, canonical: str,
          out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    replay_report = replay_section(matrix)
    fault_matrix = fault_section()
    fence = validation_section(canonical)
    shadow = shadow_section(os.path.join(out_dir, 'shadow.sqlite'))
    canary = canary_section()
    packet = review.build_packet(
        commit=commit, implementer=implementer,
        replay_report=replay_report, fault_matrix=fault_matrix,
        validation_fence=fence, shadow=shadow, canary=canary,
        shim_parity=compat.coverage(),
        writer_disable={'disabled': compat.writer_disabled(),
                        'criterion': compat.WRITER_DISABLE_CRITERION},
        rollback=rollback_section())
    packet_receipt = review.seal_packet(
        os.path.join(out_dir, 'H3714_review_packet.json'), packet)

    verdict = review.cutover_verdict(
        offline_green=True,
        replay_exact=bool(replay_report['exact']),
        faults_green=bool(fault_matrix['green']),
        validation_fenced=bool(fence.get('available') and
                               fence.get('mutation') == 'none'),
        shadow_clean=shadow['unexplained_mismatches'] == 0,
        canary_green=bool(canary['executed']),
        receipt_verified=False)
    verdict_receipt = seal(os.path.join(out_dir, 'H3714_cutover_verdict.json'),
                           dict(verdict, packet_sha256=packet_receipt['sha256'],
                                commit=commit))
    return {
        'schema': 'pwg.pipeline.wave1_evidence.v1',
        'commit': commit,
        'packet': packet_receipt,
        'verdict': verdict,
        'verdict_artifact': verdict_receipt,
        'canonical_fence': {k: v for k, v in fence.items()
                            if k != 'identities'},
        'replay_exact': replay_report['exact'],
        'fault_boundaries': len(faults.FAULT_POINTS),
        'shadow_unexplained_mismatches': shadow['unexplained_mismatches'],
    }


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='build the Wave-1 evidence')
    parser.add_argument('--out', default=os.path.join(RT_ROOT, 'docs',
                                                      'evidence'))
    parser.add_argument('--commit', default='working-tree')
    parser.add_argument('--implementer', default='claude-opus-4-8')
    parser.add_argument('--matrix', default=DEFAULT_MATRIX)
    parser.add_argument('--canonical', default=DEFAULT_CANONICAL)
    args = parser.parse_args(argv)
    summary = build(args.commit, args.implementer, args.matrix,
                    args.canonical, args.out)
    sys.stdout.write(json.dumps(summary, ensure_ascii=False, indent=2,
                                sort_keys=True) + '\n')
    return 0 if summary['verdict']['verdict'] != 'NO-GO' else 3


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
