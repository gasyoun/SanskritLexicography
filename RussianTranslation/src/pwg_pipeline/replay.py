"""Exact campaign replay (H3714 Wave 1, implementation step 8).

A replay drives a frozen fixture campaign through the *real* control plane --
the same repository, the same paid-call kernel, the same pure audit, the same
journaled promotion -- with a scripted adapter standing in for the provider.
Nothing is stubbed except the network.

The comparison is exact and structural: selected jobs, state transitions,
attempts, calls, route/model bindings, artifact hashes, verdicts, requeue
decisions, promotion deltas and the final store projection.  Counts alone are
never the proof (R4.1).

Four campaigns are frozen: ``clean_success``, ``partial_requeue``,
``provider_timeout`` and ``promotion_interrupt``.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from typing import Any, Mapping, Sequence

from . import apply as apply_module
from . import audit, faults, kernel, model, promotion, providers
from .evidence import canonical_bytes, read_sealed, sha256_bytes, sha256_file
from .repository import Repository, new_id, open_repository

SCHEMA = 'pwg.pipeline.replay.v1'

CAMPAIGNS: tuple[str, ...] = (
    'clean_success', 'partial_requeue', 'provider_timeout',
    'promotion_interrupt',
)

MODE_OK = 'ok'
MODE_EMPTY_TARGET = 'empty_target'
MODE_MISSING = 'missing_fragment'
MODE_PLACEHOLDER = 'placeholder_residue'
MODE_TIMEOUT = 'timeout'
MODE_MALFORMED = 'malformed'
MODE_NO_USAGE = 'no_usage'

# The replay's fixed apply policy. Requeue-vs-refill is a genuine operator
# choice, so the engine pins one rather than letting `intent_for` return None.
DEFAULT_INTENT: dict[str, str] = {
    model.VERDICT_REQUEUE: model.INTENT_REQUEUE,
    model.VERDICT_DEFECT: model.INTENT_QUARANTINE,
    model.VERDICT_INCONCLUSIVE: model.INTENT_QUARANTINE,
}

REVIEW_RECEIPT_STUB = {
    'schema': 'pwg.pipeline.review_receipt.v1',
    'reviewer': 'fixture-reviewer',
    'commit': 'fixture',
    'bundle_sha256': '0' * 64,
    'disposition': 'approved',
}


class ReplayMismatch(RuntimeError):
    """A replay diverged from its frozen expectation."""


class ScriptedAdapter:
    """A fixture-driven provider. Route and model bindings are real."""

    name = 'scripted'

    def __init__(self, route: str, script: Sequence[Mapping[str, Any]]) -> None:
        self.route = route
        self._script = [dict(item) for item in script]
        self.calls = 0

    def _next(self) -> dict[str, Any]:
        if not self._script:
            return {'mode': MODE_OK}
        return self._script.pop(0)

    def prepare_request(self, job_payloads, *, requested_model,
                        max_output_tokens, timeout_ms):
        return providers.ProviderRequest(
            route=self.route, requested_model=requested_model,
            payload={'fragments': [dict(item) for item in job_payloads]},
            max_output_tokens=int(max_output_tokens), timeout_ms=int(timeout_ms))

    def invoke(self, request):
        self.calls += 1
        step = self._next()
        mode = step.get('mode', MODE_OK)
        if mode == MODE_TIMEOUT:
            raise TimeoutError('scripted provider timeout')
        fragments = request.payload.get('fragments') or []
        if mode == MODE_MALFORMED:
            return providers.ProviderResponse(
                raw_text='not json at all',
                served_model=request.requested_model,
                raw_usage={'prompt_tokens': 40, 'completion_tokens': 0})
        rows = []
        for item in fragments:
            target = 'ru:%s' % (item.get('source_string') or '')
            if mode == MODE_EMPTY_TARGET:
                target = ''
            elif mode == MODE_PLACEHOLDER:
                target = 'ru:{T3} %s' % (item.get('source_string') or '')
            rows.append({'fragment_id': item.get('fragment_id'),
                         'target_string': target})
        if mode == MODE_MISSING:
            rows = rows[:-1] if len(rows) > 1 else []
        usage = {'prompt_tokens': 120, 'completion_tokens': 60}
        if mode == MODE_NO_USAGE:
            usage = {'prompt_tokens': None, 'completion_tokens': None}
        return providers.ProviderResponse(
            raw_text=json.dumps({'fragments': rows}, ensure_ascii=False,
                                sort_keys=True),
            served_model=step.get('served_model', request.requested_model),
            raw_usage=usage)

    def parse_result(self, response):
        try:
            parsed = json.loads(response.raw_text)
        except (json.JSONDecodeError, ValueError) as exc:
            raise providers.ProviderError(
                'scripted reply is malformed JSON: %s' % exc)
        rows = parsed.get('fragments') if isinstance(parsed, Mapping) else None
        if not isinstance(rows, list):
            raise providers.ProviderError('scripted reply has no fragments list')
        return {'fragments': rows}

    def normalize_usage(self, response):
        return providers.normalized_usage(
            input_tokens=response.raw_usage.get('prompt_tokens'),
            output_tokens=response.raw_usage.get('completion_tokens'),
            route=self.route)


def load_fixture(directory: str) -> dict[str, Any]:
    path = os.path.join(directory, 'campaign.json')
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


def _promotion_rows(job: Mapping[str, Any], parsed: Mapping[str, Any]
                    ) -> list[dict[str, Any]]:
    rows = []
    for item in parsed.get('fragments') or []:
        rows.append({
            'fragment_id': item.get('fragment_id'),
            'target_string': item.get('target_string'),
            'source_identity': job['source_identity'],
            'generation': {'route_id': job.get('route'),
                           'pipeline_version': 'pwg_pipeline.v1'},
        })
    return rows


def run_campaign(fixture_dir: str, workdir: str, *,
                 fault_point: str | None = None,
                 resume: bool = False) -> dict[str, Any]:
    """Execute one frozen campaign and return its comparable projection."""
    spec = load_fixture(fixture_dir)
    os.makedirs(workdir, exist_ok=True)
    database = os.path.join(workdir, 'campaign.sqlite')
    evidence_dir = os.path.join(workdir, 'evidence')
    journal_dir = os.path.join(workdir, 'journal')
    store_path = os.path.join(workdir, 'scratch_store.jsonl')
    ledger_path = os.path.join(workdir, 'call_reservations.json')

    repository = open_repository(database)
    campaign_id = str(spec['campaign_id'])
    route = str(spec.get('route', model.ROUTE_XAI))
    requested_model = str(spec.get('requested_model', 'grok-4.6'))

    if not resume:
        repository.create_campaign(model.Campaign(
            campaign_id=campaign_id, scope=str(spec.get('scope', 'fixture')),
            language=str(spec.get('language', 'ru')), route=route,
            max_calls=int(spec.get('max_calls', 8)),
            cost_ceiling_usd=float(spec.get('cost_ceiling_usd', 4.0)),
            promotable=bool(spec.get('promotable', True)),
            created_by='replay'))

    hook = faults.raising_hook(fault_point) if fault_point else None
    paid = kernel.PaidCallKernel(
        repository, campaign_id=campaign_id, evidence_dir=evidence_dir,
        ledger_path=ledger_path, fault_hook=hook)
    service = apply_module.ApplyService(repository, fault_hook=hook)
    promoter = promotion.PromotionService(
        repository, campaign_id=campaign_id, journal_dir=journal_dir,
        fault_hook=hook)

    # The scratch store is promoted as a whole: every promotion carries the
    # cumulative rows, so before/after hashes describe the real store delta
    # rather than one job's slice.
    store_rows: list[dict[str, Any]] = []
    jobs = list(spec['jobs'])
    if not resume:
        for index, job in enumerate(jobs):
            repository.add_job(model.Job(
                job_id='%s.job%02d' % (campaign_id, index),
                campaign_id=campaign_id, kind=str(job.get('kind', 'fragment')),
                source_identity=str(job['source_identity']),
                source_hash=sha256_bytes(
                    str(job['source_string']).encode('utf-8'))))

    for index, job in enumerate(jobs):
        job_id = '%s.job%02d' % (campaign_id, index)
        job = dict(job, route=route)
        if repository.job_state(job_id) != model.PLANNED:
            continue
        adapter = ScriptedAdapter(route, job.get('script', []))
        repository.transition_job(job_id, model.PLANNED, model.PREPARED,
                                  reason='plan')
        repository.transition_job(job_id, model.PREPARED, model.RESERVED,
                                  reason='reserve')
        payload = [{'fragment_id': job.get('fragment_id', job['source_identity']),
                    'fragment_class': job.get('fragment_class', 'definition_gloss'),
                    'source_string': job['source_string'],
                    'context': job.get('context')}]
        repository.transition_job(job_id, model.RESERVED, model.RUNNING,
                                  reason='dispatch')
        try:
            outcome = paid.execute(
                adapter, job_ids=[job_id], job_payloads=payload,
                requested_model=requested_model,
                idempotency_key='%s:%s:1' % (campaign_id, job_id),
                estimated_input_tokens=200, max_output_tokens=256)
        except kernel.GlobalStop:
            repository.transition_job(job_id, model.RUNNING, model.FAILED,
                                      reason='global_stop')
            continue
        repository.transition_job(job_id, model.RUNNING, model.CAPTURED,
                                  reason='capture')
        if outcome.succeeded:
            verdict = audit.audit_call(
                repository, job_id=job_id, campaign_id=campaign_id,
                result_path=outcome.artifacts['result']['path'],
                expected_fragment_ids=[item['fragment_id'] for item in payload])
        else:
            verdict = audit.audit_call(
                repository, job_id=job_id, campaign_id=campaign_id,
                failure_path=outcome.artifacts['failure']['path'])
        repository.transition_job(job_id, model.CAPTURED, model.AUDITED,
                                  reason='audit',
                                  evidence_sha=verdict.result_artifact_sha256)

        if verdict.verdict_class == model.VERDICT_CLEAN:
            rows = _promotion_rows(job, outcome.parsed or {})
            service.prepare_promotion(verdict, rows)
            if spec.get('promote', True):
                store_rows.extend(rows)
                promotion_id = '%s.%s' % (campaign_id, job_id)
                promoter.prepare(
                    promotion_id=promotion_id, verdict=verdict,
                    rows=list(store_rows), store_path=store_path,
                    review_receipt=dict(REVIEW_RECEIPT_STUB),
                    implementer='replay-engine')
                promoter.commit(promotion_id, list(store_rows))
        else:
            intent = DEFAULT_INTENT.get(verdict.verdict_class)
            if intent:
                service.dispatch(verdict, intent,
                                 {'reasons': list(verdict.reasons)})

    projection = repository.state_projection(campaign_id)
    projection['store'] = {
        'exists': os.path.exists(store_path),
        'sha256': sha256_file(store_path) if os.path.exists(store_path) else None,
        'rows': sum(1 for line in open(store_path, encoding='utf-8')
                    if line.strip()) if os.path.exists(store_path) else 0,
    }
    repository.close()
    return projection


def normalize(projection: Mapping[str, Any]) -> dict[str, Any]:
    """Strip run-scoped identifiers so two runs are byte-comparable."""
    jobs = []
    for job in projection.get('jobs', []):
        jobs.append({
            'source_identity': job['source_identity'],
            'kind': job['kind'],
            'state': job['state'],
            'source_hash': job['source_hash'],
            'transitions': list(job['transitions']),
            'calls': [{
                'route': call['route'],
                'requested_model': call['requested_model'],
                'served_model': call['served_model'],
                'state': call['state'],
                'input_tokens': call['input_tokens'],
                'output_tokens': call['output_tokens'],
                'cost_evaluable': call['cost_evaluable'],
                'failure_class': call['failure_class'],
            } for call in job['calls']],
            'verdicts': [{
                'verdict_class': verdict['verdict_class'],
                'validator_version': verdict['validator_version'],
            } for verdict in job['verdicts']],
        })
    by_identity = {job['source_identity']: job for job in jobs}
    intents = sorted(
        ({'intent': row['intent']} for row in projection.get('intents', [])),
        key=lambda row: row['intent'])
    return {
        'schema': SCHEMA,
        'jobs': [by_identity[key] for key in sorted(by_identity)],
        'accounting': {
            'calls': projection['accounting']['calls'],
            'pending_calls': projection['accounting']['pending_calls'],
            'unevaluable_calls': projection['accounting']['unevaluable_calls'],
            'cost_evaluable': projection['accounting']['cost_evaluable'],
        },
        'intents': intents,
        'promotion_phases': sorted(row['phase']
                                   for row in projection.get('promotions', [])),
        'store': {
            'exists': projection['store']['exists'],
            'rows': projection['store']['rows'],
        },
        'artifact_kinds': sorted({row['kind']
                                  for row in projection.get('artifacts', [])}),
    }


def diff(expected: Mapping[str, Any], actual: Mapping[str, Any]) -> list[str]:
    """Every structural difference, as readable paths."""
    findings: list[str] = []

    def walk(left: Any, right: Any, path: str) -> None:
        if isinstance(left, Mapping) and isinstance(right, Mapping):
            for key in sorted(set(left) | set(right)):
                if key not in left:
                    findings.append('%s.%s: unexpected %r' % (path, key, right[key]))
                elif key not in right:
                    findings.append('%s.%s: missing (expected %r)'
                                    % (path, key, left[key]))
                else:
                    walk(left[key], right[key], '%s.%s' % (path, key))
        elif isinstance(left, list) and isinstance(right, list):
            if len(left) != len(right):
                findings.append('%s: length %d != %d' % (path, len(left),
                                                         len(right)))
            for index, (a, b) in enumerate(zip(left, right)):
                walk(a, b, '%s[%d]' % (path, index))
        elif left != right:
            findings.append('%s: %r != %r' % (path, left, right))

    walk(expected, actual, '$')
    return findings


def replay(fixture_dir: str, *, workdir: str | None = None,
           exact: bool = True) -> dict[str, Any]:
    """Run one campaign and compare it with its frozen ``expected.json``."""
    temporary = workdir is None
    directory = workdir or tempfile.mkdtemp(prefix='pwg-replay-')
    try:
        projection = run_campaign(fixture_dir, directory)
        actual = normalize(projection)
        expected_path = os.path.join(fixture_dir, 'expected.json')
        if not os.path.exists(expected_path):
            return {'schema': SCHEMA, 'campaign': os.path.basename(fixture_dir),
                    'frozen': False, 'actual': actual, 'mismatches': []}
        with open(expected_path, encoding='utf-8') as handle:
            expected = json.load(handle)
        mismatches = diff(expected, actual)
        if exact and mismatches:
            raise ReplayMismatch('%s: %s' % (os.path.basename(fixture_dir),
                                             '; '.join(mismatches)))
        return {
            'schema': SCHEMA,
            'campaign': os.path.basename(fixture_dir),
            'frozen': True,
            'exact': not mismatches,
            'mismatches': mismatches,
            'projection_sha256': sha256_bytes(canonical_bytes(actual)),
        }
    finally:
        if temporary:
            shutil.rmtree(directory, ignore_errors=True)


def replay_matrix(matrix_dir: str, *, exact: bool = True) -> dict[str, Any]:
    """Replay all four frozen campaigns and seal one comparison report."""
    reports = []
    for name in CAMPAIGNS:
        directory = os.path.join(matrix_dir, name)
        if not os.path.isdir(directory):
            raise ReplayMismatch('frozen campaign is missing: %s' % directory)
        reports.append(replay(directory, exact=exact))
    return {
        'schema': 'pwg.pipeline.replay_matrix.v1',
        'campaigns': reports,
        'exact': all(report.get('exact') for report in reports),
        'unexplained_mismatches': sum(len(report['mismatches'])
                                      for report in reports),
    }


def freeze(fixture_dir: str) -> dict[str, Any]:
    """Write ``expected.json`` from a run.  Used once, when a fixture is minted."""
    directory = tempfile.mkdtemp(prefix='pwg-freeze-')
    try:
        actual = normalize(run_campaign(fixture_dir, directory))
    finally:
        shutil.rmtree(directory, ignore_errors=True)
    path = os.path.join(fixture_dir, 'expected.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(actual, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
    return actual


__all__ = [
    'SCHEMA', 'CAMPAIGNS', 'ReplayMismatch', 'ScriptedAdapter', 'run_campaign',
    'normalize', 'diff', 'replay', 'replay_matrix', 'freeze', 'load_fixture',
    'MODE_OK', 'MODE_EMPTY_TARGET', 'MODE_MISSING', 'MODE_PLACEHOLDER',
    'MODE_TIMEOUT', 'MODE_MALFORMED', 'MODE_NO_USAGE', 'read_sealed',
    'Repository', 'new_id',
]
