"""H4057 — the GLM 5.3 Flash route qualification (offline, zero provider calls).

Proves the adapter seam and its fail-closed economics: resolved identity, own
route + credential, verbatim markup replays, malformed/missing-usage refusals,
reservation accounting exactly once, and a dollar-bounded campaign refusing
BEFORE any reservation because no verified price card exists for the route.

No test in this file makes a network call and no Claude CLI is invoked.
"""
import io
import json
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from pwg_pipeline import kernel, model, providers  # noqa: E402
from pwg_pipeline.repository import open_repository  # noqa: E402

TOOLS = os.path.join(ROOT, 'tools')

CARD = {
    'fragment_id': 'agnísikhā',
    'fragment_class': 'card',
    'source_string': 'f. Feuerflamme {#agni#}-Comp. {#śikhā#}',
    'context': 'keep {#...#} fences verbatim',
}


@pytest.fixture(autouse=True)
def no_provider_credentials(monkeypatch):
    monkeypatch.delenv(providers.GLM_KEY_ENV, raising=False)
    monkeypatch.delenv(providers.XAI_KEY_ENV, raising=False)
    monkeypatch.delenv(providers.DEEPSEEK_KEY_ENV, raising=False)


@pytest.fixture()
def synthetic_price_card():
    """A qualification-only synthetic card (never a borrowed real price)."""
    saved = providers.PRICE_PER_MTOK_USD.get(model.ROUTE_GLM)
    providers.PRICE_PER_MTOK_USD[model.ROUTE_GLM] = {'input': 1.0, 'output': 1.0}
    yield
    if saved is None:
        providers.PRICE_PER_MTOK_USD.pop(model.ROUTE_GLM, None)
    else:
        providers.PRICE_PER_MTOK_USD[model.ROUTE_GLM] = saved


def glm_reply(payload, *, served_model=providers.GLM_DEFAULT_MODEL,
              usage=None):
    return providers.ProviderResponse(
        raw_text=json.dumps(payload, ensure_ascii=False, sort_keys=True),
        served_model=served_model,
        raw_usage=usage if usage is not None
        else {'prompt_tokens': 312, 'completion_tokens': 88})


def test_the_resolved_identity_is_the_installed_one():
    assert providers.GLM_DEFAULT_MODEL == 'glm-5.3-flash'
    assert model.ROUTE_GLM == 'glm-flash'
    assert model.ROUTE_GLM in model.ROUTES
    assert model.ROUTE_GLM in model.BILLABLE_ROUTES


def test_the_glm_adapter_is_registered_and_bound_to_its_own_route():
    adapter = providers.adapter_for('glm')
    assert isinstance(adapter, providers.GlmFlashAdapter)
    assert adapter.route == model.ROUTE_GLM
    assert adapter.route not in {model.ROUTE_XAI, model.ROUTE_DEEPSEEK}
    assert adapter.base_url == providers.GLM_BASE_URL
    assert adapter.key_env == providers.GLM_KEY_ENV


def test_the_glm_adapter_refuses_without_a_key_rather_than_dialing():
    adapter = providers.adapter_for('glm')
    with pytest.raises(providers.ProviderUnavailable):
        adapter.invoke(providers.ProviderRequest(
            route=model.ROUTE_GLM, requested_model='glm-5.3-flash',
            payload={}, max_output_tokens=16, timeout_ms=1000))


def test_card_replays_keep_markup_verbatim():
    adapter = providers.adapter_for('glm')
    request = adapter.prepare_request(
        [CARD], requested_model=providers.GLM_DEFAULT_MODEL,
        max_output_tokens=256, timeout_ms=1000)
    assert request.requested_model == 'glm-5.3-flash'
    reply = glm_reply({'fragments': [{
        'fragment_id': CARD['fragment_id'],
        'target_string': 'RU<%s>' % CARD['source_string']}]})
    parsed = adapter.parse_result(reply)
    assert CARD['source_string'] in parsed['fragments'][0]['target_string']
    usage = adapter.normalize_usage(reply)
    # No price card: token counts survive, cost stays unknown.
    assert usage['input_tokens'] == 312 and usage['output_tokens'] == 88
    assert usage['cost_evaluable'] is False
    assert usage['cost_basis'] == 'unevaluable'


@pytest.mark.parametrize('raw', [
    'Sure! Here is your translation. Hope this helps!',
    '{"fragments": "not-a-list"}',
    '',
])
def test_malformed_replies_are_refused_not_guessed(raw):
    adapter = providers.adapter_for('glm')
    with pytest.raises(providers.ProviderError):
        adapter.parse_result(providers.ProviderResponse(
            raw_text=raw, served_model='glm-5.3-flash', raw_usage={}))


def test_missing_usage_is_unevaluable_and_never_zero():
    adapter = providers.adapter_for('glm')
    usage = adapter.normalize_usage(providers.ProviderResponse(
        raw_text='{"fragments":[]}', served_model='glm-5.3-flash',
        raw_usage={}))
    assert usage['cost_evaluable'] is False
    assert usage['cost_basis'] == 'unevaluable'


def test_no_price_card_exists_for_glm_and_none_is_borrowed():
    assert model.ROUTE_GLM not in providers.PRICE_PER_MTOK_USD
    with pytest.raises(providers.ProviderError):
        providers.estimate_cost_usd(model.ROUTE_GLM, input_tokens=1000,
                                    max_output_tokens=2048)


def _campaign(workdir, name, *, cost_ceiling_usd=4.0):
    repository = open_repository(os.path.join(workdir, '%s.sqlite' % name))
    campaign_id = 'h4057-%s' % name
    repository.create_campaign(model.Campaign(
        campaign_id=campaign_id, scope='h4057-glm-qualification',
        language='ru', route=model.ROUTE_GLM, max_calls=4,
        cost_ceiling_usd=cost_ceiling_usd, promotable=False,
        created_by='tests/test_pwg_pipeline_glm_route.py'))
    job_id = '%s.job' % campaign_id
    import hashlib
    repository.add_job(model.Job(
        job_id=job_id, campaign_id=campaign_id, kind='fragment',
        source_identity=CARD['fragment_id'],
        source_hash=hashlib.sha256(
            CARD['source_string'].encode('utf-8')).hexdigest()))
    paid = kernel.PaidCallKernel(
        repository, campaign_id=campaign_id,
        evidence_dir=os.path.join(workdir, 'evidence', name),
        ledger_path=os.path.join(workdir, '%s_ledger.json' % name))
    return repository, paid, job_id


def test_a_dollar_bounded_glm_campaign_refuses_before_any_reservation(tmp_path):
    """No verified price card: fail closed BEFORE reserve or dispatch."""
    repository, paid, job_id = _campaign(tmp_path, 'refusal')
    try:
        with pytest.raises(kernel.KernelRefusal) as excinfo:
            paid.execute(providers.adapter_for('glm'), job_ids=[job_id],
                         job_payloads=[CARD],
                         requested_model=providers.GLM_DEFAULT_MODEL,
                         idempotency_key='h4057:test:refusal',
                         max_output_tokens=256, estimated_input_tokens=200)
        assert excinfo.value.failure_class == kernel.FAILURE_CEILING
        assert 'no verified price card' in str(excinfo.value)
        assert paid.ledger.spent() == 0
        assert repository.call_accounting('h4057-refusal')[
            'observed_cost_usd'] == 0.0
    finally:
        repository.close()


def test_the_kernel_accepts_glm_and_accounts_exactly_once(
        tmp_path, synthetic_price_card):
    repository, paid, job_id = _campaign(tmp_path, 'success')

    class Stub(providers.GlmFlashAdapter):
        def invoke(self, request):
            return glm_reply({'fragments': [{
                'fragment_id': CARD['fragment_id'],
                'target_string': 'RU<%s>' % CARD['source_string']}]})

    try:
        outcome = paid.execute(Stub(), job_ids=[job_id], job_payloads=[CARD],
                               requested_model=providers.GLM_DEFAULT_MODEL,
                               idempotency_key='h4057:test:success',
                               max_output_tokens=256,
                               estimated_input_tokens=200)
        assert outcome.state == model.CALL_SUCCEEDED
        assert outcome.served_model == 'glm-5.3-flash'
        assert set(outcome.artifacts) == {'request', 'response', 'result'}
        assert paid.ledger.spent() == 1
    finally:
        repository.close()


def test_glm_usage_without_telemetry_halts_as_unevaluable(
        tmp_path, synthetic_price_card):
    """A dispatched reply carrying NO usage is unevaluable -> wave stops.

    The synthetic fixture card keeps the budget gate open; the reply's empty
    raw_usage then makes ``normalize_usage`` unevaluable, and the kernel stops
    the wave closed after terminal accounting -- the dollar-bound property
    H4057 requires (missing cost is never treated as zero).
    """

    class Stub(providers.GlmFlashAdapter):
        def invoke(self, request):
            return glm_reply({'fragments': [{
                'fragment_id': CARD['fragment_id'],
                'target_string': 'RU'}]}, usage={})

    repository, paid, job_id = _campaign(tmp_path, 'unevaluable')
    try:
        with pytest.raises(kernel.GlobalStop) as excinfo:
            paid.execute(Stub(), job_ids=[job_id], job_payloads=[CARD],
                         requested_model=providers.GLM_DEFAULT_MODEL,
                         idempotency_key='h4057:test:unevaluable',
                         max_output_tokens=256, estimated_input_tokens=200)
        assert excinfo.value.failure_class == kernel.FAILURE_UNEVALUABLE
        assert excinfo.value.dispatched is True
    finally:
        repository.close()


def test_the_qualification_tool_seals_a_report(tmp_path):
    sys.path.insert(0, TOOLS)
    import h4057_glm_route_qualification as qual
    report_path = tmp_path / 'report.json'
    code = qual.main(['replay', '--report', str(report_path)])
    assert code == 0
    with open(report_path, encoding='utf-8') as handle:
        report = json.load(handle)
    assert report['provider_calls'] == 0
    assert report['claude_cli_invocations'] == 0
    assert report['resolved_identity']['wire_model_id'] == 'glm-5.3-flash'
    scenarios = {s['scenario']: s for s in report['replays']['kernel_scenarios']}
    assert scenarios['success']['state'] == model.CALL_SUCCEEDED
    assert scenarios['dollar_bound_refuses']['dispatches'] == 0
    assert scenarios['dollar_bound_refuses']['reservations_consumed'] == 0
