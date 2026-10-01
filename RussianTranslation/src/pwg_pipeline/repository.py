"""Transactional campaign state (H3714 Wave 1, implementation step 1).

Standard-library ``sqlite3`` only (R3.2): foreign keys, WAL, a busy timeout,
explicit ``BEGIN IMMEDIATE`` transactions, compare-and-set state transitions,
non-negative accounting constraints, and idempotency keys.

The database is the mutable system of record.  It never stores secrets,
credential-bearing prompts, or profile directories -- only identities, hashes,
state, bindings, and relative paths.
"""
from __future__ import annotations

import contextlib
import datetime
import os
import sqlite3
import uuid
from typing import Any, Iterable, Iterator, Mapping, Sequence

from . import model
from .evidence import canonical_sha256

SCHEMA = 'pwg.pipeline.repository.v1'
SCHEMA_VERSION = 1
BUSY_TIMEOUT_MS = 15000

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR = os.path.join(HERE, 'schema')


class RepositoryError(RuntimeError):
    """A persistence-level refusal."""


class ConcurrentModification(RepositoryError):
    """A compare-and-set transition lost its race and must be retried."""


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        '%Y-%m-%dT%H:%M:%SZ')


def new_id(prefix: str) -> str:
    return '%s_%s' % (prefix, uuid.uuid4().hex)


def _migration_sql(version: int) -> str:
    path = os.path.join(SCHEMA_DIR, '%03d_initial.sql' % version)
    if not os.path.exists(path):
        raise RepositoryError('missing migration %03d' % version)
    with open(path, encoding='utf-8') as handle:
        return handle.read()


class Repository:
    """One campaign database.  Short, explicit, immediate transactions."""

    def __init__(self, path: str) -> None:
        self.path = os.path.abspath(path)
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self._conn = sqlite3.connect(self.path, timeout=BUSY_TIMEOUT_MS / 1000.0,
                                     isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute('PRAGMA foreign_keys = ON')
        self._conn.execute('PRAGMA busy_timeout = %d' % BUSY_TIMEOUT_MS)
        try:
            self._conn.execute('PRAGMA journal_mode = WAL')
        except sqlite3.DatabaseError:  # pragma: no cover - exotic filesystems
            pass
        self._depth = 0

    # -- lifecycle ---------------------------------------------------------

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> 'Repository':
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def migrate(self) -> int:
        """Apply pending migrations; return the resulting schema version."""
        # `executescript` issues its own COMMIT, so a migration cannot run
        # inside `transaction()`; each script is its own atomic unit and the
        # version row is written immediately after it.
        self._conn.executescript(
            'CREATE TABLE IF NOT EXISTS schema_version ('
            ' version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL,'
            ' description TEXT NOT NULL)')
        current = self.schema_version()
        for version in range(current + 1, SCHEMA_VERSION + 1):
            self._conn.executescript(_migration_sql(version))
            self._conn.execute(
                'INSERT OR IGNORE INTO schema_version'
                ' (version, applied_at, description) VALUES (?, ?, ?)',
                (version, utc_now(), 'pwg_pipeline migration %03d' % version))
        return self.schema_version()

    def schema_version(self) -> int:
        row = self._conn.execute(
            'SELECT MAX(version) AS v FROM schema_version').fetchone()
        return int(row['v'] or 0)

    @contextlib.contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """A short ``BEGIN IMMEDIATE`` block; nesting joins the outer one."""
        if self._depth:
            self._depth += 1
            try:
                yield self._conn
            finally:
                self._depth -= 1
            return
        self._conn.execute('BEGIN IMMEDIATE')
        self._depth = 1
        try:
            yield self._conn
        except BaseException:
            self._conn.execute('ROLLBACK')
            raise
        else:
            self._conn.execute('COMMIT')
        finally:
            self._depth = 0

    # -- campaigns ---------------------------------------------------------

    def create_campaign(self, campaign: model.Campaign) -> model.Campaign:
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO campaigns (campaign_id, scope, language, route,'
                ' max_calls, cost_ceiling_usd, promotable, created_by,'
                ' lifecycle_version, fence, created_at)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (campaign.campaign_id, campaign.scope, campaign.language,
                 campaign.route, campaign.max_calls, float(campaign.cost_ceiling_usd),
                 1 if campaign.promotable else 0, campaign.created_by,
                 campaign.lifecycle_version, campaign.fence, utc_now()))
        return campaign

    def campaign(self, campaign_id: str) -> model.Campaign:
        row = self._conn.execute(
            'SELECT * FROM campaigns WHERE campaign_id = ?',
            (campaign_id,)).fetchone()
        if row is None:
            raise RepositoryError('unknown campaign: %s' % campaign_id)
        return model.Campaign(
            campaign_id=row['campaign_id'], scope=row['scope'],
            language=row['language'], route=row['route'],
            max_calls=int(row['max_calls']),
            cost_ceiling_usd=float(row['cost_ceiling_usd']),
            promotable=bool(row['promotable']), created_by=row['created_by'],
            lifecycle_version=row['lifecycle_version'], fence=row['fence'])

    # -- jobs --------------------------------------------------------------

    def add_job(self, job: model.Job) -> model.Job:
        now = utc_now()
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO jobs (job_id, campaign_id, kind, source_identity,'
                ' source_hash, state, parent_job_id, created_at, updated_at)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (job.job_id, job.campaign_id, job.kind, job.source_identity,
                 job.source_hash, job.state, job.parent_job_id, now, now))
            conn.execute(
                'INSERT INTO job_transitions (job_id, from_state, to_state,'
                ' reason, evidence_sha, at) VALUES (?, ?, ?, ?, ?, ?)',
                (job.job_id, '', job.state, 'created', None, now))
        return job

    def job_state(self, job_id: str) -> str:
        row = self._conn.execute(
            'SELECT state FROM jobs WHERE job_id = ?', (job_id,)).fetchone()
        if row is None:
            raise RepositoryError('unknown job: %s' % job_id)
        return str(row['state'])

    def jobs_in_state(self, campaign_id: str, state: str) -> list[str]:
        rows = self._conn.execute(
            'SELECT job_id FROM jobs WHERE campaign_id = ? AND state = ?'
            ' ORDER BY job_id', (campaign_id, state)).fetchall()
        return [str(row['job_id']) for row in rows]

    def transition_job(self, job_id: str, expected: str, following: str, *,
                       reason: str | None = None,
                       evidence_sha: str | None = None,
                       require_artifact_kind: str | None = None) -> str:
        """Compare-and-set one job move; append-record it in the same tx.

        A transition may advance only when its required artifact hashes exist
        (architecture, state model), so ``require_artifact_kind`` is checked
        inside the transaction rather than by the caller.
        """
        model.assert_job_transition(expected, following)
        now = utc_now()
        with self.transaction() as conn:
            if require_artifact_kind is not None:
                row = conn.execute(
                    'SELECT COUNT(*) AS n FROM artifacts'
                    ' WHERE job_id = ? AND kind = ?',
                    (job_id, require_artifact_kind)).fetchone()
                if not int(row['n']):
                    raise RepositoryError(
                        'transition %s -> %s requires a sealed %s artifact for %s'
                        % (expected, following, require_artifact_kind, job_id))
            cursor = conn.execute(
                'UPDATE jobs SET state = ?, updated_at = ?'
                ' WHERE job_id = ? AND state = ?',
                (following, now, job_id, expected))
            if cursor.rowcount != 1:
                actual = conn.execute(
                    'SELECT state FROM jobs WHERE job_id = ?',
                    (job_id,)).fetchone()
                if actual is None:
                    raise RepositoryError('unknown job: %s' % job_id)
                raise ConcurrentModification(
                    'job %s is in state %r, not the expected %r'
                    % (job_id, actual['state'], expected))
            conn.execute(
                'INSERT INTO job_transitions (job_id, from_state, to_state,'
                ' reason, evidence_sha, at) VALUES (?, ?, ?, ?, ?, ?)',
                (job_id, expected, following, reason, evidence_sha, now))
        return following

    def transitions(self, job_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            'SELECT from_state, to_state, reason, evidence_sha FROM'
            ' job_transitions WHERE job_id = ? ORDER BY transition_id',
            (job_id,)).fetchall()
        return [dict(row) for row in rows]

    # -- attempts and calls ------------------------------------------------

    def next_attempt_ordinal(self, job_id: str) -> int:
        row = self._conn.execute(
            'SELECT MAX(ordinal) AS o FROM attempts WHERE job_id = ?',
            (job_id,)).fetchone()
        return int(row['o'] or 0) + 1

    def add_attempt(self, attempt: model.Attempt) -> model.Attempt:
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO attempts (attempt_id, job_id, adapter, route,'
                ' requested_model, ordinal, outcome, created_at)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (attempt.attempt_id, attempt.job_id, attempt.adapter,
                 attempt.route, attempt.requested_model, attempt.ordinal,
                 attempt.outcome, utc_now()))
        return attempt

    def set_attempt_outcome(self, attempt_id: str, outcome: str) -> None:
        with self.transaction() as conn:
            conn.execute('UPDATE attempts SET outcome = ? WHERE attempt_id = ?',
                         (outcome, attempt_id))

    def record_reserved_call(self, call: model.Call,
                             job_ids: Sequence[str] = ()) -> model.Call:
        """Persist a reservation *before* any provider I/O."""
        if call.state != model.CALL_RESERVED:
            raise RepositoryError('a call is persisted in the reserved state')
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO calls (call_id, attempt_id, route, requested_model,'
                ' reservation_id, idempotency_key, state, reserved_at)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (call.call_id, call.attempt_id, call.route, call.requested_model,
                 call.reservation_id, call.idempotency_key, call.state, utc_now()))
            for job_id in job_ids:
                conn.execute(
                    'INSERT OR IGNORE INTO call_jobs (call_id, job_id)'
                    ' VALUES (?, ?)', (call.call_id, job_id))
        return call

    def call_state(self, call_id: str) -> str:
        row = self._conn.execute(
            'SELECT state FROM calls WHERE call_id = ?', (call_id,)).fetchone()
        if row is None:
            raise RepositoryError('unknown call: %s' % call_id)
        return str(row['state'])

    def transition_call(self, call_id: str, expected: str, following: str) -> str:
        model.assert_call_transition(expected, following)
        with self.transaction() as conn:
            cursor = conn.execute(
                'UPDATE calls SET state = ? WHERE call_id = ? AND state = ?',
                (following, call_id, expected))
            if cursor.rowcount != 1:
                actual = conn.execute(
                    'SELECT state FROM calls WHERE call_id = ?',
                    (call_id,)).fetchone()
                if actual is None:
                    raise RepositoryError('unknown call: %s' % call_id)
                raise ConcurrentModification(
                    'call %s is in state %r, not the expected %r'
                    % (call_id, actual['state'], expected))
        return following

    def finalize_call(self, call_id: str, *, state: str,
                      telemetry: Mapping[str, Any],
                      served_model: str | None = None,
                      request_sha256: str | None = None,
                      response_sha256: str | None = None,
                      failure_class: str | None = None) -> dict[str, Any]:
        """Terminally account one call.  Idempotent for identical accounting."""
        if state not in model.CALL_TERMINAL_STATES:
            raise RepositoryError('finalization requires a terminal call state')
        cost = float(telemetry.get('observed_cost_usd') or 0.0)
        if cost < 0:
            raise RepositoryError('observed_cost_usd must be non-negative')
        evaluable = 1 if telemetry.get('cost_evaluable') else 0
        payload = (state, int(telemetry.get('input_tokens') or 0),
                   int(telemetry.get('output_tokens') or 0), cost, evaluable,
                   served_model, request_sha256, response_sha256, failure_class)
        with self.transaction() as conn:
            row = conn.execute(
                'SELECT * FROM calls WHERE call_id = ?', (call_id,)).fetchone()
            if row is None:
                raise RepositoryError('unknown call: %s' % call_id)
            if row['finalized_at']:
                existing = (row['state'], int(row['input_tokens']),
                            int(row['output_tokens']),
                            float(row['observed_cost_usd']),
                            int(row['cost_evaluable']), row['served_model'],
                            row['request_sha256'], row['response_sha256'],
                            row['failure_class'])
                if existing != payload:
                    raise RepositoryError(
                        'call %s is already finalized with different accounting'
                        % call_id)
                return dict(row)
            conn.execute(
                'UPDATE calls SET state = ?, input_tokens = ?, output_tokens = ?,'
                ' observed_cost_usd = ?, cost_evaluable = ?, served_model = ?,'
                ' request_sha256 = ?, response_sha256 = ?, failure_class = ?,'
                ' finalized_at = ? WHERE call_id = ?',
                payload + (utc_now(), call_id))
            row = conn.execute(
                'SELECT * FROM calls WHERE call_id = ?', (call_id,)).fetchone()
        return dict(row)

    def call_accounting(self, campaign_id: str) -> dict[str, Any]:
        """Ledger-truth spend for a campaign: rows, never returned-row counts."""
        row = self._conn.execute(
            'SELECT COUNT(*) AS calls,'
            ' COALESCE(SUM(observed_cost_usd), 0) AS cost,'
            ' SUM(CASE WHEN finalized_at IS NULL THEN 1 ELSE 0 END) AS pending,'
            ' SUM(CASE WHEN finalized_at IS NOT NULL AND cost_evaluable = 0'
            '     THEN 1 ELSE 0 END) AS unevaluable'
            ' FROM calls c JOIN attempts a ON a.attempt_id = c.attempt_id'
            ' JOIN jobs j ON j.job_id = a.job_id WHERE j.campaign_id = ?',
            (campaign_id,)).fetchone()
        pending = int(row['pending'] or 0)
        unevaluable = int(row['unevaluable'] or 0)
        return {
            'calls': int(row['calls'] or 0),
            'observed_cost_usd': round(float(row['cost'] or 0.0), 6),
            'pending_calls': pending,
            'unevaluable_calls': unevaluable,
            'cost_evaluable': pending == 0 and unevaluable == 0,
        }

    def unfinalized_calls(self, campaign_id: str) -> list[str]:
        rows = self._conn.execute(
            'SELECT c.call_id FROM calls c'
            ' JOIN attempts a ON a.attempt_id = c.attempt_id'
            ' JOIN jobs j ON j.job_id = a.job_id'
            ' WHERE j.campaign_id = ? AND c.finalized_at IS NULL'
            ' ORDER BY c.call_id', (campaign_id,)).fetchall()
        return [str(row['call_id']) for row in rows]

    # -- artifacts, verdicts, intents --------------------------------------

    def record_artifact(self, artifact: model.Artifact, *,
                        job_id: str | None = None,
                        call_id: str | None = None) -> model.Artifact:
        with self.transaction() as conn:
            existing = conn.execute(
                'SELECT * FROM artifacts WHERE campaign_id = ? AND kind = ?'
                ' AND sha256 = ?',
                (artifact.campaign_id, artifact.kind, artifact.sha256)).fetchone()
            if existing is not None:
                if str(existing['path']) != artifact.path:
                    raise RepositoryError(
                        'artifact %s is already sealed at a different path: %s'
                        % (artifact.sha256, existing['path']))
                return artifact
            conn.execute(
                'INSERT INTO artifacts (artifact_id, campaign_id, job_id,'
                ' call_id, kind, path, sha256, media_type, created_at)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (artifact.artifact_id, artifact.campaign_id, job_id, call_id,
                 artifact.kind, artifact.path, artifact.sha256,
                 artifact.media_type, utc_now()))
        return artifact

    def artifacts(self, campaign_id: str,
                  kind: str | None = None) -> list[dict[str, Any]]:
        sql = ('SELECT * FROM artifacts WHERE campaign_id = ?'
               + (' AND kind = ?' if kind else '') + ' ORDER BY sha256')
        args: tuple[Any, ...] = (campaign_id, kind) if kind else (campaign_id,)
        return [dict(row) for row in self._conn.execute(sql, args).fetchall()]

    def record_verdict(self, verdict: model.Verdict) -> model.Verdict:
        with self.transaction() as conn:
            existing = conn.execute(
                'SELECT * FROM verdicts WHERE job_id = ?'
                ' AND result_artifact_sha256 = ? AND validator_version = ?',
                (verdict.job_id, verdict.result_artifact_sha256,
                 verdict.validator_version)).fetchone()
            reasons = canonical_sha256(list(verdict.reasons))
            if existing is not None:
                if str(existing['verdict_class']) != verdict.verdict_class:
                    raise RepositoryError(
                        'a different verdict is already bound to this result:'
                        ' %s vs %s' % (existing['verdict_class'],
                                       verdict.verdict_class))
                return verdict
            conn.execute(
                'INSERT INTO verdicts (verdict_id, job_id, verdict_class,'
                ' result_artifact_sha256, validator_version, reasons_json,'
                ' created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (verdict.verdict_id, verdict.job_id, verdict.verdict_class,
                 verdict.result_artifact_sha256, verdict.validator_version,
                 reasons, utc_now()))
        return verdict

    def record_intent(self, *, verdict_id: str, job_id: str, intent: str,
                      payload_sha256: str,
                      intent_id: str | None = None) -> str:
        model.require_choice(intent, model.APPLY_INTENTS, 'apply.intent')
        identifier = intent_id or new_id('intent')
        with self.transaction() as conn:
            existing = conn.execute(
                'SELECT * FROM apply_intents WHERE verdict_id = ? AND intent = ?',
                (verdict_id, intent)).fetchone()
            if existing is not None:
                if str(existing['payload_sha256']) != payload_sha256:
                    raise RepositoryError(
                        'intent %s for verdict %s is already recorded with a'
                        ' different payload' % (intent, verdict_id))
                return str(existing['intent_id'])
            conn.execute(
                'INSERT INTO apply_intents (intent_id, verdict_id, job_id,'
                ' intent, payload_sha256, applied_at, created_at)'
                ' VALUES (?, ?, ?, ?, ?, NULL, ?)',
                (identifier, verdict_id, job_id, intent, payload_sha256,
                 utc_now()))
        return identifier

    def mark_intent_applied(self, intent_id: str) -> None:
        with self.transaction() as conn:
            conn.execute(
                'UPDATE apply_intents SET applied_at = COALESCE(applied_at, ?)'
                ' WHERE intent_id = ?', (utc_now(), intent_id))

    def intents(self, campaign_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            'SELECT i.* FROM apply_intents i JOIN jobs j ON j.job_id = i.job_id'
            ' WHERE j.campaign_id = ? ORDER BY i.job_id, i.intent',
            (campaign_id,)).fetchall()
        return [dict(row) for row in rows]

    # -- promotions --------------------------------------------------------

    def upsert_promotion(self, promotion: model.Promotion) -> model.Promotion:
        now = utc_now()
        with self.transaction() as conn:
            row = conn.execute(
                'SELECT * FROM promotions WHERE promotion_id = ?',
                (promotion.promotion_id,)).fetchone()
            if row is None:
                conn.execute(
                    'INSERT INTO promotions (promotion_id, campaign_id, phase,'
                    ' store_path, before_sha256, after_sha256, journal_path,'
                    ' created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (promotion.promotion_id, promotion.campaign_id,
                     promotion.phase, promotion.store_path,
                     promotion.before_sha256, promotion.after_sha256,
                     promotion.journal_path, now, now))
                return promotion
            current = str(row['phase'])
            if current != promotion.phase:
                order = model.PROMOTION_STATES
                if order.index(promotion.phase) < order.index(current):
                    raise RepositoryError(
                        'promotion %s cannot move backwards %s -> %s'
                        % (promotion.promotion_id, current, promotion.phase))
            conn.execute(
                'UPDATE promotions SET phase = ?, before_sha256 = ?,'
                ' after_sha256 = ?, journal_path = ?, updated_at = ?'
                ' WHERE promotion_id = ?',
                (promotion.phase, promotion.before_sha256,
                 promotion.after_sha256, promotion.journal_path, now,
                 promotion.promotion_id))
        return promotion

    def promotion(self, promotion_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            'SELECT * FROM promotions WHERE promotion_id = ?',
            (promotion_id,)).fetchone()
        return dict(row) if row is not None else None

    def open_promotions(self, campaign_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            'SELECT * FROM promotions WHERE campaign_id = ? AND phase <> ?'
            ' ORDER BY promotion_id', (campaign_id, model.COMPLETE)).fetchall()
        return [dict(row) for row in rows]

    # -- legacy import and shadow -----------------------------------------

    def record_import(self, *, source_kind: str, source_path: str,
                      content_sha256: str, campaign_id: str | None,
                      row_count: int) -> tuple[str, bool]:
        """Record one legacy import.  Returns ``(import_id, was_new)``.

        A repeat of the same path with the same content is a no-op; the same
        path with a changed payload is a refusal (implementation step 6.2).
        """
        normalized = source_path.replace('\\', '/')
        with self.transaction() as conn:
            row = conn.execute(
                'SELECT * FROM legacy_imports WHERE source_path = ?',
                (normalized,)).fetchone()
            if row is not None:
                if str(row['content_sha256']) != content_sha256:
                    raise RepositoryError(
                        'legacy import identity changed payload: %s'
                        ' (imported=%s, now=%s)'
                        % (normalized, row['content_sha256'], content_sha256))
                return str(row['import_id']), False
            identifier = new_id('import')
            conn.execute(
                'INSERT INTO legacy_imports (import_id, source_kind,'
                ' source_path, content_sha256, campaign_id, row_count,'
                ' imported_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (identifier, source_kind, normalized, content_sha256,
                 campaign_id, int(row_count), utc_now()))
        return identifier, True

    def imports(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self._conn.execute(
            'SELECT * FROM legacy_imports ORDER BY source_path').fetchall()]

    def record_shadow(self, *, route: str, legacy_key: str,
                      legacy_value: str | None, pipeline_value: str | None,
                      explanation: str | None = None) -> bool:
        """Record one shadow comparison row.  Returns whether it matched."""
        matched = legacy_value == pipeline_value
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO shadow_observations (observation_id, route,'
                ' legacy_key, legacy_value, pipeline_value, matched,'
                ' explanation, observed_at)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
                ' ON CONFLICT(route, legacy_key) DO UPDATE SET'
                ' legacy_value = excluded.legacy_value,'
                ' pipeline_value = excluded.pipeline_value,'
                ' matched = excluded.matched,'
                ' explanation = excluded.explanation,'
                ' observed_at = excluded.observed_at',
                (new_id('shadow'), route, legacy_key, legacy_value,
                 pipeline_value, 1 if matched else 0, explanation, utc_now()))
        return matched

    def shadow_mismatches(self, route: str | None = None) -> list[dict[str, Any]]:
        """Every unexplained mismatch: an explained one is not a failure."""
        sql = ('SELECT * FROM shadow_observations WHERE matched = 0'
               " AND (explanation IS NULL OR explanation = '')")
        args: tuple[Any, ...] = ()
        if route:
            sql += ' AND route = ?'
            args = (route,)
        return [dict(row) for row in
                self._conn.execute(sql + ' ORDER BY legacy_key', args).fetchall()]

    # -- projections -------------------------------------------------------

    def state_projection(self, campaign_id: str) -> dict[str, Any]:
        """The comparison surface used by replay: state, not counts alone."""
        jobs = self._conn.execute(
            'SELECT job_id, kind, source_identity, source_hash, state,'
            ' parent_job_id FROM jobs WHERE campaign_id = ? ORDER BY job_id',
            (campaign_id,)).fetchall()
        projection: dict[str, Any] = {
            'campaign_id': campaign_id,
            'jobs': [],
            'accounting': self.call_accounting(campaign_id),
            'intents': [
                {'job_id': row['job_id'], 'intent': row['intent'],
                 'payload_sha256': row['payload_sha256']}
                for row in self.intents(campaign_id)],
            'artifacts': [
                {'kind': row['kind'], 'sha256': row['sha256']}
                for row in self.artifacts(campaign_id)],
            'promotions': [
                {'promotion_id': row['promotion_id'], 'phase': row['phase'],
                 'before_sha256': row['before_sha256'],
                 'after_sha256': row['after_sha256']}
                for row in self._conn.execute(
                    'SELECT * FROM promotions WHERE campaign_id = ?'
                    ' ORDER BY promotion_id', (campaign_id,)).fetchall()],
        }
        for job in jobs:
            calls = self._conn.execute(
                'SELECT c.route, c.requested_model, c.served_model, c.state,'
                ' c.input_tokens, c.output_tokens, c.observed_cost_usd,'
                ' c.cost_evaluable, c.failure_class FROM calls c'
                ' JOIN attempts a ON a.attempt_id = c.attempt_id'
                ' WHERE a.job_id = ? ORDER BY a.ordinal, c.call_id',
                (job['job_id'],)).fetchall()
            verdicts = self._conn.execute(
                'SELECT verdict_class, result_artifact_sha256,'
                ' validator_version FROM verdicts WHERE job_id = ?'
                ' ORDER BY verdict_id', (job['job_id'],)).fetchall()
            projection['jobs'].append({
                'job_id': job['job_id'],
                'kind': job['kind'],
                'source_identity': job['source_identity'],
                'source_hash': job['source_hash'],
                'state': job['state'],
                'parent_job_id': job['parent_job_id'],
                'transitions': [
                    '%s->%s' % (row['from_state'], row['to_state'])
                    for row in self.transitions(str(job['job_id']))],
                'calls': [dict(row) for row in calls],
                'verdicts': [dict(row) for row in verdicts],
            })
        return projection


def open_repository(path: str) -> Repository:
    """Open (creating if needed) a migrated campaign database."""
    repository = Repository(path)
    repository.migrate()
    return repository


def iter_rows(rows: Iterable[sqlite3.Row]) -> Iterator[dict[str, Any]]:
    for row in rows:
        yield dict(row)


__all__ = [
    'SCHEMA', 'SCHEMA_VERSION', 'Repository', 'RepositoryError',
    'ConcurrentModification', 'open_repository', 'utc_now', 'new_id',
    'iter_rows',
]
