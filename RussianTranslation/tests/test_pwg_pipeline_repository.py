"""H3714 Wave 1 — transactional state (V1, V2, V4, and the kernel contract).

Pins uniqueness, compare-and-set transitions, rollback, terminal call
accounting, budget refusal *before* provider I/O, and import idempotency.
"""
import hashlib
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from pwg_pipeline import (audit, import_legacy, kernel, model,  # noqa: E402
                          providers, repository)
from pwg_pipeline.evidence import sha256_text, tree_digest  # noqa: E402

CAMPAIGN = 'test-campaign'


def make_repo(tmp_path, *, max_calls=4, ceiling=4.0, promotable=False):
    repo = repository.open_repository(str(tmp_path / 'campaign.sqlite'))
    repo.create_campaign(model.Campaign(
        campaign_id=CAMPAIGN, scope='test', language='ru',
        route=model.ROUTE_XAI, max_calls=max_calls, cost_ceiling_usd=ceiling,
        promotable=promotable, created_by='pytest'))
    return repo


def add_job(repo, identity='pwg.x.1', job_id='job1'):
    job = model.Job(job_id=job_id, campaign_id=CAMPAIGN, kind='fragment',
                    source_identity=identity, source_hash=sha256_text(identity))
    repo.add_job(job)
    return job


def make_kernel(repo, tmp_path):
    return kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=str(tmp_path / 'ledger.json'))


PAYLOAD = [{'fragment_id': 'f1', 'fragment_class': 'definition_gloss',
            'source_string': 'Feuer'}]


def test_migration_is_idempotent(tmp_path):
    repo = repository.open_repository(str(tmp_path / 'a.sqlite'))
    assert repo.migrate() == repository.SCHEMA_VERSION
    assert repo.migrate() == repository.SCHEMA_VERSION
    repo.close()


def test_duplicate_source_identity_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    add_job(repo)
    with pytest.raises(Exception):
        add_job(repo, job_id='job2')
    repo.close()


def test_compare_and_set_transition_refuses_a_stale_expectation(tmp_path):
    repo = make_repo(tmp_path)
    add_job(repo)
    repo.transition_job('job1', model.PLANNED, model.PREPARED)
    with pytest.raises(repository.ConcurrentModification):
        repo.transition_job('job1', model.PLANNED, model.PREPARED)
    assert repo.job_state('job1') == model.PREPARED
    repo.close()


def test_transition_can_require_a_sealed_artifact(tmp_path):
    repo = make_repo(tmp_path)
    add_job(repo)
    repo.transition_job('job1', model.PLANNED, model.PREPARED)
    with pytest.raises(repository.RepositoryError):
        repo.transition_job('job1', model.PREPARED, model.RESERVED,
                            require_artifact_kind='manifest')
    repo.record_artifact(model.Artifact(
        artifact_id='a1', campaign_id=CAMPAIGN, kind='manifest',
        path='m.json', sha256=sha256_text('m')), job_id='job1')
    repo.transition_job('job1', model.PREPARED, model.RESERVED,
                        require_artifact_kind='manifest')
    repo.close()


def test_a_failed_transaction_rolls_back(tmp_path):
    repo = make_repo(tmp_path)
    add_job(repo)
    with pytest.raises(RuntimeError):
        with repo.transaction() as conn:
            conn.execute('UPDATE jobs SET state = ? WHERE job_id = ?',
                         (model.COMPLETE, 'job1'))
            raise RuntimeError('boom')
    assert repo.job_state('job1') == model.PLANNED
    repo.close()


def test_one_provider_request_makes_exactly_one_finalized_call(tmp_path):
    """V1 — success path."""
    repo = make_repo(tmp_path)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    adapter = providers.FakeAdapter(model.ROUTE_XAI)
    outcome = paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                           requested_model='grok-4.6', idempotency_key='k1')
    assert outcome.succeeded
    accounting = repo.call_accounting(CAMPAIGN)
    assert accounting['calls'] == 1
    assert accounting['pending_calls'] == 0
    assert accounting['cost_evaluable'] is True
    assert repo.unfinalized_calls(CAMPAIGN) == []
    repo.close()


@pytest.mark.parametrize('adapter_kwargs,expected_state,failure', [
    ({'raises': TimeoutError('slow')}, model.CALL_TIMED_OUT,
     kernel.FAILURE_TIMEOUT),
    ({'raises': RuntimeError('kaboom')}, model.CALL_ERRORED,
     kernel.FAILURE_EXCEPTION),
    ({'raises': providers.ProviderUnavailable('no key')}, model.CALL_REFUSED,
     kernel.FAILURE_UNAVAILABLE),
])
def test_every_failure_path_finalizes_exactly_one_call(
        tmp_path, adapter_kwargs, expected_state, failure):
    """V1 — refusal, timeout and exception all account terminally."""
    repo = make_repo(tmp_path)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    adapter = providers.FakeAdapter(model.ROUTE_XAI, **adapter_kwargs)
    outcome = paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                           requested_model='grok-4.6', idempotency_key='k1')
    assert outcome.state == expected_state
    assert outcome.failure_class == failure
    accounting = repo.call_accounting(CAMPAIGN)
    assert accounting['calls'] == 1
    assert accounting['pending_calls'] == 0
    assert repo.unfinalized_calls(CAMPAIGN) == []
    repo.close()


def test_malformed_output_finalizes_once_and_stays_attributable(tmp_path):
    repo = make_repo(tmp_path)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    adapter = providers.FakeAdapter(model.ROUTE_XAI, responses=[
        providers.ProviderResponse(
            raw_text='<html>gateway</html>', served_model='grok-4.6',
            raw_usage={'prompt_tokens': 30, 'completion_tokens': 0})])
    outcome = paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                           requested_model='grok-4.6', idempotency_key='k1')
    assert outcome.state == model.CALL_MALFORMED
    assert outcome.failure_class == kernel.FAILURE_MALFORMED
    # Billed usage, when present, remains attributable.
    assert outcome.usage['input_tokens'] == 30
    assert repo.call_accounting(CAMPAIGN)['calls'] == 1
    repo.close()


def test_call_ceiling_refuses_before_any_provider_io(tmp_path):
    """V2 — the fake adapter's call counter must stay at zero."""
    repo = make_repo(tmp_path, max_calls=0)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    adapter = providers.FakeAdapter(model.ROUTE_XAI)
    with pytest.raises(kernel.KernelRefusal) as excinfo:
        paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                     requested_model='grok-4.6', idempotency_key='k1')
    assert excinfo.value.failure_class == kernel.FAILURE_BUDGET
    assert adapter.calls == 0
    assert repo.call_accounting(CAMPAIGN)['calls'] == 0
    repo.close()


def test_cost_ceiling_refuses_before_any_provider_io(tmp_path):
    """V2 — a worst-case estimate over the ceiling never reaches the network."""
    repo = make_repo(tmp_path, ceiling=0.000001)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    adapter = providers.FakeAdapter(model.ROUTE_XAI)
    with pytest.raises(kernel.KernelRefusal) as excinfo:
        paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                     requested_model='grok-4.6', idempotency_key='k1',
                     max_output_tokens=4096)
    assert excinfo.value.failure_class == kernel.FAILURE_CEILING
    assert adapter.calls == 0
    repo.close()


def test_route_substitution_is_a_global_stop(tmp_path):
    """V3 / stop conditions — a served model that is not the requested one."""
    repo = make_repo(tmp_path)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    adapter = providers.FakeAdapter(model.ROUTE_XAI, served_model='grok-mini')
    with pytest.raises(kernel.GlobalStop):
        paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                     requested_model='grok-4.6', idempotency_key='k1')
    accounting = repo.call_accounting(CAMPAIGN)
    assert accounting['calls'] == 1
    assert accounting['pending_calls'] == 0
    repo.close()


def test_unevaluable_usage_is_a_global_stop(tmp_path):
    repo = make_repo(tmp_path)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    adapter = providers.FakeAdapter(model.ROUTE_XAI, responses=[
        providers.ProviderResponse(
            raw_text='{"fragments": []}', served_model='grok-4.6',
            raw_usage={'prompt_tokens': None, 'completion_tokens': None})])
    with pytest.raises(kernel.GlobalStop):
        paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                     requested_model='grok-4.6', idempotency_key='k1')
    assert repo.call_accounting(CAMPAIGN)['unevaluable_calls'] == 1
    repo.close()


def test_a_non_billable_route_may_not_enter_the_paid_kernel(tmp_path):
    repo = make_repo(tmp_path)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    shadow = providers.ClaudeHeadlessShadowAdapter()
    with pytest.raises(kernel.KernelRefusal):
        paid.execute(shadow, job_ids=['job1'], job_payloads=PAYLOAD,
                     requested_model='claude', idempotency_key='k1')
    repo.close()


def test_call_count_is_never_inferred_from_returned_rows(tmp_path):
    """One batch call covering three jobs is still exactly one Call row."""
    repo = make_repo(tmp_path)
    for index in range(3):
        add_job(repo, identity='pwg.batch.%d' % index, job_id='job%d' % index)
    paid = make_kernel(repo, tmp_path)
    adapter = providers.FakeAdapter(model.ROUTE_XAI)
    payload = [{'fragment_id': 'f%d' % index,
                'fragment_class': 'definition_gloss',
                'source_string': 'w%d' % index} for index in range(3)]
    outcome = paid.execute(adapter, job_ids=['job0', 'job1', 'job2'],
                           job_payloads=payload, requested_model='grok-4.6',
                           idempotency_key='batch')
    assert len(outcome.parsed['fragments']) == 3
    assert repo.call_accounting(CAMPAIGN)['calls'] == 1
    repo.close()


def test_finalization_is_idempotent_for_identical_accounting(tmp_path):
    repo = make_repo(tmp_path)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    outcome = paid.execute(providers.FakeAdapter(model.ROUTE_XAI),
                           job_ids=['job1'], job_payloads=PAYLOAD,
                           requested_model='grok-4.6', idempotency_key='k1')
    telemetry = {'cost_evaluable': True, 'input_tokens': 100,
                 'output_tokens': 50,
                 'observed_cost_usd': outcome.usage['observed_cost_usd']}
    repo.finalize_call(outcome.call_id, state=model.CALL_SUCCEEDED,
                       telemetry=telemetry, served_model='grok-4.6',
                       request_sha256=outcome.request_sha256,
                       response_sha256=outcome.response_sha256)
    with pytest.raises(repository.RepositoryError):
        repo.finalize_call(outcome.call_id, state=model.CALL_SUCCEEDED,
                           telemetry=dict(telemetry, output_tokens=51),
                           served_model='grok-4.6',
                           request_sha256=outcome.request_sha256,
                           response_sha256=outcome.response_sha256)
    repo.close()


def test_audit_makes_no_filesystem_change(tmp_path):
    """V5 — the evidence tree digest is identical around an audit."""
    repo = make_repo(tmp_path)
    add_job(repo)
    paid = make_kernel(repo, tmp_path)
    outcome = paid.execute(providers.FakeAdapter(model.ROUTE_XAI),
                           job_ids=['job1'], job_payloads=PAYLOAD,
                           requested_model='grok-4.6', idempotency_key='k1')
    evidence_root = str(tmp_path / 'evidence')
    before = tree_digest(evidence_root)
    verdict = audit.audit_call(
        repo, job_id='job1', campaign_id=CAMPAIGN,
        result_path=outcome.artifacts['result']['path'],
        expected_fragment_ids=['f1'])
    assert verdict.verdict_class == model.VERDICT_CLEAN
    assert tree_digest(evidence_root) == before
    # Auditing twice is a no-op, not a second verdict row.
    audit.audit_call(repo, job_id='job1', campaign_id=CAMPAIGN,
                     result_path=outcome.artifacts['result']['path'],
                     expected_fragment_ids=['f1'])
    assert tree_digest(evidence_root) == before
    repo.close()


def test_audit_module_exposes_no_mutation_surface():
    banned = {'os', 'shutil', 'rename', 'unlink', 'remove', 'rmtree'}
    exported = set(dir(audit))
    assert not (banned & exported), sorted(banned & exported)


def test_legacy_import_is_idempotent_and_refuses_a_changed_payload(tmp_path):
    repo = make_repo(tmp_path)
    source = tmp_path / 'coordinator.json'
    source.write_text('{"a": 1}', encoding='utf-8')
    first = import_legacy.import_source(
        repo, source_kind=import_legacy.KIND_COORDINATOR, path=str(source))
    assert first['imported'] is True
    second = import_legacy.import_source(
        repo, source_kind=import_legacy.KIND_COORDINATOR, path=str(source))
    assert second['imported'] is False
    source.write_text('{"a": 2}', encoding='utf-8')
    with pytest.raises(repository.RepositoryError):
        import_legacy.import_source(
            repo, source_kind=import_legacy.KIND_COORDINATOR, path=str(source))
    repo.close()


def test_shadow_sync_records_rows_and_has_no_execution_authority(tmp_path):
    repo = make_repo(tmp_path)
    legacy = {'selected': ['a', 'b'], 'calls': 1, 'promoted': 0}
    report = import_legacy.shadow_sync(
        repo, route=model.ROUTE_CLAUDE_SHADOW, legacy=legacy, pipeline=legacy)
    assert report['unexplained_mismatches'] == 0
    drifted = import_legacy.shadow_sync(
        repo, route=model.ROUTE_CLAUDE_SHADOW, legacy=legacy,
        pipeline=dict(legacy, calls=2))
    assert drifted['unexplained_mismatches'] == 1
    explained = import_legacy.shadow_sync(
        repo, route=model.ROUTE_CLAUDE_SHADOW, legacy=legacy,
        pipeline=dict(legacy, calls=2),
        explanations={'calls': 'legacy counted returned rows (retired)'})
    assert explained['unexplained_mismatches'] == 0
    repo.close()


def test_usage_normalization_never_invents_a_zero_cost():
    unevaluable = providers.normalized_usage(input_tokens=None,
                                             output_tokens=5)
    assert unevaluable['cost_evaluable'] is False
    derived = providers.normalized_usage(input_tokens=1000, output_tokens=1000,
                                         route=model.ROUTE_DEEPSEEK)
    assert derived['cost_evaluable'] is True
    assert derived['cost_basis'] == 'list_price_derived'
    reported = providers.normalized_usage(input_tokens=10, output_tokens=10,
                                          observed_cost_usd=0.5,
                                          route=model.ROUTE_XAI)
    assert reported['cost_basis'] == 'provider_reported'
    assert reported['observed_cost_usd'] == 0.5


def test_source_hash_helper_matches_hashlib():
    assert sha256_text('Feuer') == hashlib.sha256(b'Feuer').hexdigest()
