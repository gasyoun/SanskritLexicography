"""Sole journaled promotion authority (H3714 Wave 1, implementation step 5).

Promotion requires a bound clean verdict *and* an independent-review receipt.
It then runs one transaction:

``apply_prepared -> store_committed -> derived_validated ->
coordinator_committed -> complete``

Each phase is durably journaled before its effect, so a restart reconciles from
the journal instead of inferring progress from filenames, and reconciliation is
idempotent at every phase (V6, fault matrix).

**Wave-1 fence.** Only scratch stores may be written.  The canonical PWG card
store and canonical PWG-TM data are refused by path, and the derived-TM rebuild
is a validation, never a canonical regeneration.  Cutover to the canonical path
happens through [`src/pilot/promotion_journal.py`](../pilot/promotion_journal.py),
whose durability primitives this module reuses rather than re-implements.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable, Mapping, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for _path in (SRC, os.path.join(SRC, 'pilot')):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import promotion_journal as legacy_journal  # noqa: E402  (durability primitives)

from . import faults, model, validation  # noqa: E402
from .evidence import jsonl_bytes, seal, sha256_bytes, sha256_file  # noqa: E402
from .repository import Repository, utc_now  # noqa: E402

SCHEMA = 'pwg.pipeline.promotion.v1'

PHASES: tuple[str, ...] = model.PROMOTION_STATES

# Canonical paths that Wave 1 may never write. Matched on a normalized suffix so
# a worktree, a clone, or a drive letter cannot smuggle one past the fence.
CANONICAL_FENCE: tuple[str, ...] = (
    'release/pwg_tm_canonical/canonical.v1.jsonl',
    'release/pwg_tm_canonical/priority_5000.jsonl',
    'release/pwg_tm_canonical/priority_5000_w2.jsonl',
    'src/pilot/store/final_cards.jsonl',
    'store/final_cards.jsonl',
)


class PromotionRefusal(RuntimeError):
    """A promotion was refused before any byte was written."""


class FenceViolation(PromotionRefusal):
    """A canonical path was proposed in a wave that may not touch one."""


def assert_scratch_store(path: str) -> str:
    """Refuse a canonical destination.  This is the last line before bytes."""
    normalized = os.path.abspath(path).replace('\\', '/')
    for fenced in CANONICAL_FENCE:
        if normalized.endswith(fenced):
            raise FenceViolation(
                'Wave 1 must not write the canonical store: %s' % normalized)
    return normalized


def verify_receipt(receipt: Mapping[str, Any], *, commit: str | None = None,
                   implementer: str | None = None) -> None:
    """Require a hash-bound receipt signed by somebody other than the author."""
    for field in ('schema', 'reviewer', 'commit', 'bundle_sha256', 'disposition'):
        if not receipt.get(field):
            raise PromotionRefusal('review receipt lacks %r' % field)
    if str(receipt['disposition']).lower() not in ('approved', 'approve'):
        raise PromotionRefusal('review receipt is not an approval: %r'
                               % receipt['disposition'])
    if implementer and str(receipt['reviewer']) == implementer:
        raise PromotionRefusal(
            'the implementer may not sign their own review receipt (%s)'
            % implementer)
    if commit and str(receipt['commit']) != commit:
        raise PromotionRefusal(
            'review receipt is bound to commit %s, not %s'
            % (receipt['commit'], commit))


class PromotionService:
    """One promotion transaction, journaled before every irreversible step."""

    def __init__(self, repository: Repository, *, campaign_id: str,
                 journal_dir: str,
                 fault_hook: faults.FaultHook | None = None,
                 derived_builder: Callable[[str], dict[str, Any]] | None = None
                 ) -> None:
        self.repository = repository
        self.campaign_id = campaign_id
        self.journal_dir = os.path.abspath(journal_dir)
        self.fault_hook = fault_hook
        self.derived_builder = derived_builder or default_derived_builder
        os.makedirs(self.journal_dir, exist_ok=True)

    # -- journal -----------------------------------------------------------

    def journal_path(self, promotion_id: str) -> str:
        return os.path.join(self.journal_dir, '%s.journal.json' % promotion_id)

    def _write_journal(self, promotion_id: str,
                       journal: Mapping[str, Any]) -> None:
        legacy_journal.atomic_write_json(self.journal_path(promotion_id),
                                         dict(journal))

    def _read_journal(self, promotion_id: str) -> dict[str, Any] | None:
        path = self.journal_path(promotion_id)
        if not os.path.exists(path):
            return None
        # The legacy loader validates the *Claude close-path* journal schema;
        # this is the pipeline-scoped journal, so it is read directly and
        # checked against our own phase vocabulary.
        with open(path, encoding='utf-8') as handle:
            journal = json.load(handle)
        if journal.get('schema') != SCHEMA:
            raise PromotionRefusal('unsupported journal schema %r at %s'
                                   % (journal.get('schema'), path))
        model.require_choice(str(journal.get('phase')), PHASES,
                             'promotion.phase')
        return journal

    def _advance(self, journal: dict[str, Any], phase: str) -> dict[str, Any]:
        model.require_choice(phase, PHASES, 'promotion.phase')
        journal['phase'] = phase
        journal['updated_at'] = utc_now()
        journal.setdefault('history', []).append(
            {'phase': phase, 'at': journal['updated_at']})
        self._write_journal(str(journal['promotion_id']), journal)
        self.repository.upsert_promotion(model.Promotion(
            promotion_id=str(journal['promotion_id']),
            campaign_id=self.campaign_id, phase=phase,
            store_path=str(journal['store']['path']),
            before_sha256=journal['store'].get('before_sha256'),
            after_sha256=journal['store'].get('after_sha256'),
            journal_path=self.journal_path(str(journal['promotion_id']))))
        faults.fault(self.fault_hook, faults.AFTER_JOURNAL_ADVANCE)
        return journal

    # -- the transaction ---------------------------------------------------

    def prepare(self, *, promotion_id: str, verdict: model.Verdict,
                rows: Sequence[Mapping[str, Any]], store_path: str,
                review_receipt: Mapping[str, Any],
                implementer: str | None = None) -> dict[str, Any]:
        """Validate everything recursively, then journal a PREPARED intent."""
        if verdict.verdict_class != model.VERDICT_CLEAN:
            raise PromotionRefusal(
                'promotion requires a clean verdict, got %r'
                % verdict.verdict_class)
        verify_receipt(review_receipt, implementer=implementer)
        normalized = assert_scratch_store(store_path)

        report = validation.validate_rows(rows)
        if not validation.is_clean(report):
            raise PromotionRefusal(
                'recursive validation refused %d of %d proposed rows: %s'
                % (report['defective_rows'], report['rows'],
                   report['by_code']))

        existing = self._read_journal(promotion_id)
        payload = jsonl_bytes(list(rows))
        after = sha256_bytes(payload)
        before = sha256_file(normalized) if os.path.exists(normalized) else None
        if existing is not None:
            if existing['store']['after_sha256'] != after:
                raise PromotionRefusal(
                    'an open journal for %s promotes different bytes'
                    % promotion_id)
            return existing

        journal = {
            'schema': SCHEMA,
            'promotion_id': promotion_id,
            'campaign_id': self.campaign_id,
            'phase': model.APPLY_PREPARED,
            'verdict_id': verdict.verdict_id,
            'job_id': verdict.job_id,
            'validator_version': report['validator_version'],
            'review_receipt': {
                'reviewer': review_receipt['reviewer'],
                'commit': review_receipt['commit'],
                'bundle_sha256': review_receipt['bundle_sha256'],
            },
            'store': {
                'path': normalized,
                'before_sha256': before,
                'after_sha256': after,
                'backup_path': None,
                'row_count': len(rows),
            },
            'derived': {'validated_at': None, 'observations': []},
            'coordinator': {'committed_at': None},
            'created_at': utc_now(),
            'updated_at': utc_now(),
            'history': [],
        }
        self._write_journal(promotion_id, journal)
        return self._advance(journal, model.APPLY_PREPARED)

    def commit(self, promotion_id: str,
               rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        """Drive a prepared promotion to ``complete``; safe to re-enter."""
        journal = self._read_journal(promotion_id)
        if journal is None:
            raise PromotionRefusal('no prepared journal for %s' % promotion_id)
        payload = jsonl_bytes(list(rows))
        if sha256_bytes(payload) != journal['store']['after_sha256']:
            raise PromotionRefusal(
                'the rows offered to commit are not the prepared bytes')
        return self._drive(journal, payload)

    def reconcile(self, promotion_id: str,
                  rows: Sequence[Mapping[str, Any]] | None = None
                  ) -> dict[str, Any]:
        """Resume an interrupted promotion from whatever phase survived.

        Recovery is idempotent: re-running it from any phase produces the same
        final bytes exactly once and never re-writes a committed store.
        """
        journal = self._read_journal(promotion_id)
        if journal is None:
            raise PromotionRefusal('no journal to reconcile for %s'
                                   % promotion_id)
        payload = jsonl_bytes(list(rows)) if rows is not None else None
        if payload is not None and \
                sha256_bytes(payload) != journal['store']['after_sha256']:
            raise PromotionRefusal(
                'reconciliation was offered different bytes than the journal')
        return self._drive(journal, payload)

    def _drive(self, journal: dict[str, Any],
               payload: bytes | None) -> dict[str, Any]:
        promotion_id = str(journal['promotion_id'])
        store_path = assert_scratch_store(str(journal['store']['path']))
        target = journal['store']['after_sha256']

        if journal['phase'] == model.APPLY_PREPARED:
            if os.path.exists(store_path) and sha256_file(store_path) == target:
                # A crash after the replace but before the journal advance:
                # the store already holds the prepared bytes. Do not rewrite.
                journal = self._advance(journal, model.STORE_COMMITTED)
            else:
                if payload is None:
                    raise PromotionRefusal(
                        'reconciliation of a pre-commit promotion needs the rows')
                backup = self._backup(store_path, promotion_id)
                journal['store']['backup_path'] = backup
                faults.fault(self.fault_hook, faults.AFTER_STORE_BACKUP)
                legacy_journal.atomic_write_bytes(store_path, payload)
                faults.fault(self.fault_hook, faults.AFTER_STORE_COMMIT)
                journal = self._advance(journal, model.STORE_COMMITTED)

        if journal['phase'] == model.STORE_COMMITTED:
            committed = sha256_file(store_path)
            if committed != target:
                raise PromotionRefusal(
                    'committed store bytes %s do not match the journalled %s'
                    % (committed, target))
            observation = self.derived_builder(store_path)
            faults.fault(self.fault_hook, faults.AFTER_DERIVED_REBUILD)
            journal['derived'] = {'validated_at': utc_now(),
                                  'observations': [observation]}
            journal = self._advance(journal, model.DERIVED_VALIDATED)

        if journal['phase'] == model.DERIVED_VALIDATED:
            journal['coordinator'] = {'committed_at': utc_now()}
            journal = self._advance(journal, model.COORDINATOR_COMMITTED)

        if journal['phase'] == model.COORDINATOR_COMMITTED:
            faults.fault(self.fault_hook, faults.BEFORE_CAMPAIGN_COMMIT)
            self._complete_job(journal)
            journal = self._advance(journal, model.COMPLETE)

        elif journal['phase'] == model.COMPLETE:
            # Finalization is idempotent: a second reconcile changes nothing.
            self._complete_job(journal)
        return journal

    def _backup(self, store_path: str, promotion_id: str) -> str | None:
        if not os.path.exists(store_path):
            return None
        backup = os.path.join(self.journal_dir,
                              '%s.store.backup' % promotion_id)
        with open(store_path, 'rb') as handle:
            legacy_journal.atomic_write_bytes(backup, handle.read())
        return backup

    def _complete_job(self, journal: Mapping[str, Any]) -> None:
        """Walk the job forward to ``complete``, skipping anything already done."""
        job_id = str(journal['job_id'])
        wanted = [model.APPLY_PREPARED, model.STORE_COMMITTED,
                  model.DERIVED_VALIDATED, model.COORDINATOR_COMMITTED,
                  model.COMPLETE]
        state = self.repository.job_state(job_id)
        if state == model.AWAITING_REVIEW:
            self.repository.transition_job(
                job_id, model.AWAITING_REVIEW, model.APPLY_PREPARED,
                reason='promotion:%s' % journal['promotion_id'])
            state = model.APPLY_PREPARED
        if state not in wanted:
            return
        for following in wanted[wanted.index(state) + 1:]:
            self.repository.transition_job(
                job_id, state, following,
                reason='promotion:%s' % journal['promotion_id'],
                evidence_sha=journal['store'].get('after_sha256'))
            state = following

    # -- reporting ---------------------------------------------------------

    def seal_receipt(self, promotion_id: str, path: str) -> dict[str, Any]:
        journal = self._read_journal(promotion_id)
        if journal is None:
            raise PromotionRefusal('no journal for %s' % promotion_id)
        return seal(path, {
            'schema': 'pwg.pipeline.promotion_receipt.v1',
            'promotion_id': promotion_id,
            'phase': journal['phase'],
            'store': journal['store'],
            'derived': journal['derived'],
            'review_receipt': journal['review_receipt'],
        })


def default_derived_builder(store_path: str) -> dict[str, Any]:
    """Validate the derived projection of a committed scratch store.

    Wave 1 *validates* rather than regenerates: it re-reads the committed bytes,
    recursively validates every row, and refuses on any defect.  Canonical
    derived-TM regeneration stays with the existing pipeline.
    """
    report = validation.validate_jsonl(store_path)
    if not validation.is_clean(report):
        raise PromotionRefusal(
            'derived validation refused the committed store: %s'
            % report['by_code'])
    return {
        'kind': 'derived_validation',
        'path': report['path'],
        'sha256': report['sha256'],
        'rows': report['rows'],
        'validator_version': report['validator_version'],
    }


__all__ = [
    'SCHEMA', 'PHASES', 'CANONICAL_FENCE', 'PromotionService',
    'PromotionRefusal', 'FenceViolation', 'assert_scratch_store',
    'verify_receipt', 'default_derived_builder',
]
