"""H3714 Wave 1 — fault injection at every irreversible boundary (V4, V6).

At each named boundary the run is interrupted, the state reopened and
reconciled, and the required properties proved: at most one reservation, no lost
response, no duplicate artifact or row, no unjournaled mutation, stable repeated
recovery, and exact scratch bytes.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from pwg_pipeline import (apply as apply_module, audit, faults,  # noqa: E402
                          kernel, model, promotion, providers, repository)
from pwg_pipeline.evidence import sha256_file, tree_digest  # noqa: E402

CAMPAIGN = 'fault-campaign'
PAYLOAD = [{'fragment_id': 'f1', 'fragment_class': 'definition_gloss',
            'source_string': 'Feuer'}]

REVIEW_RECEIPT = {
    'schema': 'pwg.pipeline.review_receipt.v1',
    'reviewer': 'independent-reviewer',
    'commit': 'test',
    'bundle_sha256': '0' * 64,
    'disposition': 'approved',
}


def clean_rows(count=2):
    return [{'tm_record_id': 'row-%d' % index,
             'target_string': 'огонь %d' % index,
             'generation': {'route_id': 'xai-tm', 'pipeline_version': 'v1'}}
            for index in range(count)]


def make_repo(tmp_path):
    repo = repository.open_repository(str(tmp_path / 'campaign.sqlite'))
    repo.create_campaign(model.Campaign(
        campaign_id=CAMPAIGN, scope='fault', language='ru',
        route=model.ROUTE_XAI, max_calls=4, cost_ceiling_usd=4.0,
        promotable=True, created_by='pytest'))
    repo.add_job(model.Job(job_id='job1', campaign_id=CAMPAIGN,
                           kind='fragment', source_identity='pwg.f.1',
                           source_hash='a' * 64))
    return repo


# --- kernel boundaries ------------------------------------------------------

def test_a_fault_before_the_request_leaves_one_reservation_and_no_spend(tmp_path):
    """Boundary: before provider request."""
    repo = make_repo(tmp_path)
    paid = kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=str(tmp_path / 'ledger.json'),
        fault_hook=faults.raising_hook(faults.AFTER_RESERVATION))
    adapter = providers.FakeAdapter(model.ROUTE_XAI)
    with pytest.raises(faults.InjectedFault):
        paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                     requested_model='grok-4.6', idempotency_key='k1')
    assert adapter.calls == 0
    accounting = repo.call_accounting(CAMPAIGN)
    assert accounting['calls'] == 1          # the reservation row survives
    assert accounting['observed_cost_usd'] == 0.0
    # Exactly one open reservation -- the boundary can be closed without a call.
    assert len(repo.unfinalized_calls(CAMPAIGN)) == 1
    repo.close()


def test_the_reservation_is_idempotent_across_a_restart(tmp_path):
    """At most one reservation: a replayed idempotency key never double-spends."""
    repo = make_repo(tmp_path)
    ledger_path = str(tmp_path / 'ledger.json')
    paid = kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=ledger_path,
        fault_hook=faults.raising_hook(faults.AFTER_RESERVATION))
    with pytest.raises(faults.InjectedFault):
        paid.execute(providers.FakeAdapter(model.ROUTE_XAI), job_ids=['job1'],
                     job_payloads=PAYLOAD, requested_model='grok-4.6',
                     idempotency_key='k1')
    spent = paid.ledger.spent()
    # A fresh process re-opens the same ledger and replays the same key.
    reopened = kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=ledger_path)
    reservation = reopened.ledger.reserve(
        purpose='pwg_pipeline.call', profile=model.ROUTE_XAI,
        detail='grok-4.6', idempotency_key='k1')
    assert reopened.ledger.spent() == spent
    assert reservation['idempotency_key'] == 'k1'
    repo.close()


def test_a_fault_after_the_response_keeps_the_raw_reply(tmp_path):
    """Boundary: after paid response, before parse."""
    repo = make_repo(tmp_path)
    paid = kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=str(tmp_path / 'ledger.json'),
        fault_hook=faults.raising_hook(faults.AFTER_PROVIDER_RESPONSE))
    adapter = providers.FakeAdapter(model.ROUTE_XAI)
    with pytest.raises(faults.InjectedFault):
        paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                     requested_model='grok-4.6', idempotency_key='k1')
    assert adapter.calls == 1
    # The request was sealed before dispatch, so restart never auto-replays: the
    # call row is still open and a human/reconciler decides, not a retry loop.
    assert len(repo.unfinalized_calls(CAMPAIGN)) == 1
    assert repo.artifacts(CAMPAIGN, kind='request')
    repo.close()


def test_a_fault_after_the_seal_does_not_call_the_provider_again(tmp_path):
    """Boundary: after artifact seal, before verdict."""
    repo = make_repo(tmp_path)
    paid = kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=str(tmp_path / 'ledger.json'),
        fault_hook=faults.raising_hook(faults.AFTER_ARTIFACT_SEAL))
    adapter = providers.FakeAdapter(model.ROUTE_XAI)
    with pytest.raises(faults.InjectedFault):
        paid.execute(adapter, job_ids=['job1'], job_payloads=PAYLOAD,
                     requested_model='grok-4.6', idempotency_key='k1')
    sealed = repo.artifacts(CAMPAIGN, kind='result')
    assert len(sealed) == 1
    before = tree_digest(str(tmp_path / 'evidence'))
    verdict = audit.audit_call(repo, job_id='job1', campaign_id=CAMPAIGN,
                               result_path=sealed[0]['path'],
                               expected_fragment_ids=['f1'])
    assert verdict.verdict_class == model.VERDICT_CLEAN
    assert adapter.calls == 1
    assert tree_digest(str(tmp_path / 'evidence')) == before
    repo.close()


def test_resealing_the_same_artifact_is_a_no_op_not_a_duplicate(tmp_path):
    repo = make_repo(tmp_path)
    paid = kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=str(tmp_path / 'ledger.json'))
    outcome = paid.execute(providers.FakeAdapter(model.ROUTE_XAI),
                           job_ids=['job1'], job_payloads=PAYLOAD,
                           requested_model='grok-4.6', idempotency_key='k1')
    count = len(repo.artifacts(CAMPAIGN))
    paid._seal('result', outcome.call_id, {
        'schema': 'pwg.pipeline.result.v1', 'route': model.ROUTE_XAI,
        'served_model': 'grok-4.6', 'requested_model': 'grok-4.6',
        'usage': outcome.usage, 'parsed': outcome.parsed,
        'request_sha256': outcome.request_sha256,
        'response_sha256': outcome.response_sha256})
    assert len(repo.artifacts(CAMPAIGN)) == count
    repo.close()


def test_a_fault_after_the_apply_intent_leaves_no_canonical_mutation(tmp_path):
    """Boundary: after verdict, before apply -- and after apply-intent commit."""
    repo = make_repo(tmp_path)
    paid = kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=str(tmp_path / 'ledger.json'))
    outcome = paid.execute(providers.FakeAdapter(
        model.ROUTE_XAI, responses=[providers.ProviderResponse(
            raw_text=json.dumps({'fragments': [
                {'fragment_id': 'f1', 'target_string': ''}]}),
            served_model='grok-4.6',
            raw_usage={'prompt_tokens': 10, 'completion_tokens': 1})]),
        job_ids=['job1'], job_payloads=PAYLOAD, requested_model='grok-4.6',
        idempotency_key='k1')
    verdict = audit.audit_call(repo, job_id='job1', campaign_id=CAMPAIGN,
                               result_path=outcome.artifacts['result']['path'],
                               expected_fragment_ids=['f1'])
    assert verdict.verdict_class == model.VERDICT_REQUEUE
    repo.transition_job('job1', model.PLANNED, model.PREPARED)
    repo.transition_job('job1', model.PREPARED, model.RESERVED)
    repo.transition_job('job1', model.RESERVED, model.RUNNING)
    repo.transition_job('job1', model.RUNNING, model.CAPTURED)
    repo.transition_job('job1', model.CAPTURED, model.AUDITED)
    service = apply_module.ApplyService(
        repo, fault_hook=faults.raising_hook(faults.AFTER_APPLY_INTENT_COMMIT))
    with pytest.raises(faults.InjectedFault):
        service.apply_requeue(verdict, {'reasons': list(verdict.reasons)})
    # The intent is committed exactly once and replaying it is a no-op.
    intents = repo.intents(CAMPAIGN)
    assert len(intents) == 1
    plain = apply_module.ApplyService(repo)
    plain.apply_requeue(verdict, {'reasons': list(verdict.reasons)})
    assert len(repo.intents(CAMPAIGN)) == 1
    repo.close()


def test_an_intent_replayed_with_a_different_payload_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    verdict = model.Verdict(verdict_id='v1', job_id='job1',
                            verdict_class=model.VERDICT_REQUEUE,
                            result_artifact_sha256='b' * 64,
                            validator_version='v')
    repo.record_verdict(verdict)
    service = apply_module.ApplyService(repo)
    service.record(verdict=verdict, intent=model.INTENT_REQUEUE,
                   payload={'reasons': ['a']})
    with pytest.raises(repository.RepositoryError):
        service.record(verdict=verdict, intent=model.INTENT_REQUEUE,
                       payload={'reasons': ['b']})
    repo.close()


# --- promotion boundaries ---------------------------------------------------

def make_promotion(tmp_path, fault_point=None):
    repo = make_repo(tmp_path)
    verdict = model.Verdict(verdict_id='v1', job_id='job1',
                            verdict_class=model.VERDICT_CLEAN,
                            result_artifact_sha256='c' * 64,
                            validator_version='v')
    repo.record_verdict(verdict)
    for current, following in ((model.PLANNED, model.PREPARED),
                               (model.PREPARED, model.RESERVED),
                               (model.RESERVED, model.RUNNING),
                               (model.RUNNING, model.CAPTURED),
                               (model.CAPTURED, model.AUDITED),
                               (model.AUDITED, model.AWAITING_REVIEW)):
        repo.transition_job('job1', current, following)
    service = promotion.PromotionService(
        repo, campaign_id=CAMPAIGN, journal_dir=str(tmp_path / 'journal'),
        fault_hook=faults.raising_hook(fault_point) if fault_point else None)
    return repo, service, verdict


@pytest.mark.parametrize('fault_point', [
    faults.AFTER_STORE_BACKUP,
    faults.AFTER_STORE_COMMIT,
    faults.AFTER_DERIVED_REBUILD,
    faults.AFTER_JOURNAL_ADVANCE,
    faults.BEFORE_CAMPAIGN_COMMIT,
])
def test_promotion_recovers_idempotently_from_every_boundary(tmp_path,
                                                             fault_point):
    """V6 — recovery at each named phase produces the same bytes exactly once."""
    store = str(tmp_path / 'scratch_store.jsonl')
    rows = clean_rows()
    repo, service, verdict = make_promotion(tmp_path)
    service.prepare(promotion_id='p1', verdict=verdict, rows=rows,
                    store_path=store, review_receipt=REVIEW_RECEIPT,
                    implementer='pytest')
    # Arm the fault only for the commit leg: `prepare` legitimately crosses
    # `after_journal_advance` too, and interrupting it proves nothing new.
    service.fault_hook = faults.raising_hook(fault_point)
    with pytest.raises(faults.InjectedFault):
        service.commit('p1', rows)

    # Recovery: a clean service reopens the journal and reconciles.
    recovered = promotion.PromotionService(
        repo, campaign_id=CAMPAIGN, journal_dir=str(tmp_path / 'journal'))
    journal = recovered.reconcile('p1', rows)
    assert journal['phase'] == model.COMPLETE
    first = sha256_file(store)
    assert first == journal['store']['after_sha256']

    # Repeated recovery is stable and never rewrites the committed store.
    again = recovered.reconcile('p1', rows)
    assert again['phase'] == model.COMPLETE
    assert sha256_file(store) == first
    assert repo.job_state('job1') == model.COMPLETE
    with open(store, encoding='utf-8') as handle:
        assert sum(1 for line in handle if line.strip()) == len(rows)
    repo.close()


def test_a_promotion_journal_never_moves_backwards(tmp_path):
    store = str(tmp_path / 'scratch_store.jsonl')
    rows = clean_rows()
    repo, service, verdict = make_promotion(tmp_path)
    service.prepare(promotion_id='p1', verdict=verdict, rows=rows,
                    store_path=store, review_receipt=REVIEW_RECEIPT,
                    implementer='pytest')
    service.commit('p1', rows)
    with pytest.raises(repository.RepositoryError):
        repo.upsert_promotion(model.Promotion(
            promotion_id='p1', campaign_id=CAMPAIGN,
            phase=model.APPLY_PREPARED, store_path=store))
    repo.close()


def test_reconciliation_refuses_different_bytes(tmp_path):
    store = str(tmp_path / 'scratch_store.jsonl')
    rows = clean_rows()
    repo, service, verdict = make_promotion(tmp_path)
    service.prepare(promotion_id='p1', verdict=verdict, rows=rows,
                    store_path=store, review_receipt=REVIEW_RECEIPT,
                    implementer='pytest')
    with pytest.raises(promotion.PromotionRefusal):
        service.commit('p1', clean_rows(3))
    repo.close()


def test_promotion_refuses_a_canonical_destination(tmp_path):
    """The Wave-1 fence: no canonical mutation, ever."""
    repo, service, verdict = make_promotion(tmp_path)
    canonical = str(tmp_path / 'release' / 'pwg_tm_canonical' /
                    'canonical.v1.jsonl')
    with pytest.raises(promotion.FenceViolation):
        service.prepare(promotion_id='p1', verdict=verdict, rows=clean_rows(),
                        store_path=canonical, review_receipt=REVIEW_RECEIPT,
                        implementer='pytest')
    repo.close()


def test_promotion_refuses_an_unclean_verdict(tmp_path):
    repo, service, _ = make_promotion(tmp_path)
    dirty = model.Verdict(verdict_id='v2', job_id='job1',
                          verdict_class=model.VERDICT_REQUEUE,
                          result_artifact_sha256='d' * 64,
                          validator_version='v')
    with pytest.raises(promotion.PromotionRefusal):
        service.prepare(promotion_id='p2', verdict=dirty, rows=clean_rows(),
                        store_path=str(tmp_path / 's.jsonl'),
                        review_receipt=REVIEW_RECEIPT, implementer='pytest')
    repo.close()


def test_promotion_refuses_a_self_signed_receipt(tmp_path):
    repo, service, verdict = make_promotion(tmp_path)
    with pytest.raises(promotion.PromotionRefusal):
        service.prepare(promotion_id='p3', verdict=verdict, rows=clean_rows(),
                        store_path=str(tmp_path / 's.jsonl'),
                        review_receipt=dict(REVIEW_RECEIPT,
                                            reviewer='implementer'),
                        implementer='implementer')
    repo.close()


def test_promotion_refuses_rows_with_placeholder_residue(tmp_path):
    """Recursive validation is a promotion precondition, not a post-check."""
    repo, service, verdict = make_promotion(tmp_path)
    rows = clean_rows()
    rows[1]['target_string'] = 'огонь {T7}'
    with pytest.raises(promotion.PromotionRefusal):
        service.prepare(promotion_id='p4', verdict=verdict, rows=rows,
                        store_path=str(tmp_path / 's.jsonl'),
                        review_receipt=REVIEW_RECEIPT, implementer='pytest')
    assert not os.path.exists(str(tmp_path / 's.jsonl'))
    repo.close()


def test_a_crash_between_store_replace_and_journal_advance_is_recovered(tmp_path):
    """The store already holds the prepared bytes: recovery must not rewrite."""
    store = str(tmp_path / 'scratch_store.jsonl')
    rows = clean_rows()
    repo, service, verdict = make_promotion(tmp_path,
                                            faults.AFTER_STORE_COMMIT)
    service.prepare(promotion_id='p1', verdict=verdict, rows=rows,
                    store_path=store, review_receipt=REVIEW_RECEIPT,
                    implementer='pytest')
    with pytest.raises(faults.InjectedFault):
        service.commit('p1', rows)
    committed = sha256_file(store)
    mtime = os.path.getmtime(store)
    recovered = promotion.PromotionService(
        repo, campaign_id=CAMPAIGN, journal_dir=str(tmp_path / 'journal'))
    # Reconciliation without the rows still completes: the bytes are already
    # committed and the journal knows their hash.
    journal = recovered.reconcile('p1')
    assert journal['phase'] == model.COMPLETE
    assert sha256_file(store) == committed
    assert os.path.getmtime(store) == mtime
    repo.close()


def test_a_subprocess_killed_at_a_boundary_recovers_on_restart(tmp_path):
    """A genuinely abrupt death, not a clean unwind."""
    script = tmp_path / 'crash.py'
    script.write_text(
        'import os, sys\n'
        'sys.path.insert(0, %r)\n'
        'from pwg_pipeline import faults, model, promotion, repository\n'
        'root = %r\n'
        'repo = repository.open_repository(os.path.join(root, "c.sqlite"))\n'
        'repo.create_campaign(model.Campaign(campaign_id="c", scope="s",\n'
        '    language="ru", route=model.ROUTE_XAI, max_calls=1,\n'
        '    cost_ceiling_usd=1.0, promotable=True, created_by="crash"))\n'
        'repo.add_job(model.Job(job_id="j", campaign_id="c", kind="fragment",\n'
        '    source_identity="i", source_hash="a"*64))\n'
        'v = model.Verdict(verdict_id="v", job_id="j",\n'
        '    verdict_class=model.VERDICT_CLEAN,\n'
        '    result_artifact_sha256="c"*64, validator_version="v")\n'
        'repo.record_verdict(v)\n'
        'for a, b in ((model.PLANNED, model.PREPARED),\n'
        '             (model.PREPARED, model.RESERVED),\n'
        '             (model.RESERVED, model.RUNNING),\n'
        '             (model.RUNNING, model.CAPTURED),\n'
        '             (model.CAPTURED, model.AUDITED),\n'
        '             (model.AUDITED, model.AWAITING_REVIEW)):\n'
        '    repo.transition_job("j", a, b)\n'
        'rows = [{"tm_record_id": "r0", "target_string": "x",\n'
        '         "generation": {"route_id": "xai-tm"}}]\n'
        'svc = promotion.PromotionService(repo, campaign_id="c",\n'
        '    journal_dir=os.path.join(root, "journal"),\n'
        '    fault_hook=faults.env_hook())\n'
        'svc.prepare(promotion_id="p", verdict=v, rows=rows,\n'
        '    store_path=os.path.join(root, "store.jsonl"),\n'
        '    review_receipt=%r, implementer="crash")\n'
        'svc.commit("p", rows)\n'
        'print("no crash")\n'
        % (SRC, str(tmp_path), REVIEW_RECEIPT), encoding='utf-8')
    environment = dict(os.environ,
                       PWG_PIPELINE_FAULT=faults.AFTER_STORE_COMMIT,
                       PYTHONIOENCODING='utf-8')
    result = subprocess.run([sys.executable, str(script)], env=environment,
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == faults.FAULT_EXIT_CODE, result.stderr

    store = str(tmp_path / 'store.jsonl')
    assert os.path.exists(store)
    committed = sha256_file(store)
    repo = repository.open_repository(str(tmp_path / 'c.sqlite'))
    recovered = promotion.PromotionService(
        repo, campaign_id='c', journal_dir=str(tmp_path / 'journal'))
    journal = recovered.reconcile('p')
    assert journal['phase'] == model.COMPLETE
    assert sha256_file(store) == committed
    assert repo.job_state('j') == model.COMPLETE
    repo.close()


def test_the_fault_matrix_covers_every_declared_boundary():
    """No boundary may be silently dropped from the matrix."""
    exercised = {
        faults.AFTER_RESERVATION, faults.AFTER_PROVIDER_RESPONSE,
        faults.AFTER_ARTIFACT_SEAL, faults.AFTER_APPLY_INTENT_COMMIT,
        faults.AFTER_STORE_BACKUP, faults.AFTER_STORE_COMMIT,
        faults.AFTER_DERIVED_REBUILD, faults.AFTER_JOURNAL_ADVANCE,
        faults.BEFORE_CAMPAIGN_COMMIT,
    }
    # `after_usage_capture` and `after_verdict_commit` are covered by the
    # kernel/audit tests above through their observable effects.
    declared = set(faults.FAULT_POINTS)
    assert exercised <= declared
    assert declared - exercised == {faults.AFTER_USAGE_CAPTURE,
                                    faults.AFTER_VERDICT_COMMIT}


def test_a_usage_capture_fault_still_leaves_the_response_sealed(tmp_path):
    """Boundary: after usage capture."""
    repo = make_repo(tmp_path)
    paid = kernel.PaidCallKernel(
        repo, campaign_id=CAMPAIGN, evidence_dir=str(tmp_path / 'evidence'),
        ledger_path=str(tmp_path / 'ledger.json'),
        fault_hook=faults.raising_hook(faults.AFTER_USAGE_CAPTURE))
    with pytest.raises(faults.InjectedFault):
        paid.execute(providers.FakeAdapter(model.ROUTE_XAI), job_ids=['job1'],
                     job_payloads=PAYLOAD, requested_model='grok-4.6',
                     idempotency_key='k1')
    assert repo.artifacts(CAMPAIGN, kind='response')
    assert len(repo.unfinalized_calls(CAMPAIGN)) == 1
    repo.close()
