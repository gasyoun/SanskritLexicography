"""H3714 Wave 1 — the bounded non-promotable canary fence (V13, R5.6).

Every property of the fence is proved offline: at most one xAI plus one DeepSeek
request, ``max_calls=2``, USD 4 total, no retry, nothing promotable, no
canonical-path access, and an unavailable provider stopping only its own track.

No test in this file makes a network call.  ``XAI_API_KEY`` and
``DEEPSEEK_API_KEY`` are removed from the environment first, so the adapters
refuse at the credential check rather than reaching a provider.
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

from pwg_pipeline import cli, kernel, model, promotion, providers  # noqa: E402
from pwg_pipeline.evidence import read_sealed  # noqa: E402


@pytest.fixture(autouse=True)
def no_provider_credentials(monkeypatch):
    monkeypatch.delenv(providers.XAI_KEY_ENV, raising=False)
    monkeypatch.delenv(providers.DEEPSEEK_KEY_ENV, raising=False)


def run_cli(argv):
    stream = io.StringIO()
    stdout = sys.stdout
    sys.stdout = stream
    try:
        code = cli.main(argv)
    finally:
        sys.stdout = stdout
    text = stream.getvalue()
    return code, json.loads(text) if text.strip() else None


def test_the_fence_constants_match_the_ruling():
    assert cli.CANARY_MAX_CALLS == 2
    assert cli.CANARY_COST_CEILING_USD == 4.0
    assert cli.CANARY_PROVIDERS == ('xai', 'deepseek')


def test_more_than_two_calls_is_refused(tmp_path):
    code, _ = run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
                       '--max-calls', '3', '--workdir', str(tmp_path / 'out')])
    assert code == cli.EXIT_REFUSED


def test_a_ceiling_above_four_dollars_is_refused(tmp_path):
    code, _ = run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
                       '--cost-ceiling-usd', '10',
                       '--workdir', str(tmp_path / 'out')])
    assert code == cli.EXIT_REFUSED


def test_a_promotable_canary_is_refused(tmp_path):
    code, _ = run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
                       '--promotable', '--workdir', str(tmp_path / 'out')])
    assert code == cli.EXIT_REFUSED


def test_an_unknown_provider_is_refused(tmp_path):
    code, _ = run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
                       '--providers', 'openrouter',
                       '--workdir', str(tmp_path / 'out')])
    assert code == cli.EXIT_REFUSED


def test_two_providers_do_not_fit_in_one_call(tmp_path):
    code, _ = run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
                       '--max-calls', '1', '--workdir', str(tmp_path / 'out')])
    assert code == cli.EXIT_REFUSED


def test_missing_credentials_stop_each_track_without_spending(tmp_path):
    """An unavailable provider stops its own track; the other keeps its slot."""
    workdir = str(tmp_path / 'out')
    code, report = run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
                            '--workdir', workdir])
    assert code == cli.EXIT_STOP          # INCONCLUSIVE, never a silent pass
    assert report['verdict'] == 'INCONCLUSIVE'
    assert report['successful_calls'] == 0
    assert report['observed_cost_usd'] == 0.0
    assert report['promotions'] == 0
    assert report['retries'] == 0
    assert {row['provider'] for row in report['stopped_tracks']} == \
        {'xai', 'deepseek'}
    # Each provider gets its own one-call campaign, so an unused slot can never
    # be consumed by the other adapter as a retry.
    assert len(report['envelopes']) == 2
    for envelope in report['envelopes']:
        assert envelope['promotable'] is False
        assert envelope['retries'] == 0
        assert envelope['failure_class'] == kernel.FAILURE_UNAVAILABLE


def test_the_canary_seals_one_envelope_per_provider(tmp_path):
    workdir = str(tmp_path / 'out')
    run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
             '--workdir', workdir])
    for name in cli.CANARY_PROVIDERS:
        path = os.path.join(workdir, 'envelope.%s.json' % name)
        assert os.path.exists(path)
        envelope = read_sealed(path)
        assert envelope['provider'] == name
        assert envelope['promotable'] is False
    report = read_sealed(os.path.join(workdir, 'canary_report.json'))
    assert report['max_calls'] == 2


def test_the_canary_never_touches_a_canonical_path(tmp_path):
    workdir = str(tmp_path / 'out')
    run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
             '--workdir', workdir])
    written = []
    for base, _dirs, files in os.walk(str(tmp_path)):
        for name in files:
            written.append(os.path.join(base, name).replace('\\', '/'))
    for path in written:
        for fenced in promotion.CANONICAL_FENCE:
            assert not path.endswith(fenced), path


def test_a_single_provider_track_is_allowed(tmp_path):
    code, report = run_cli(['--database', str(tmp_path / 'c.sqlite'), 'canary',
                            '--providers', 'deepseek', '--max-calls', '1',
                            '--cost-ceiling-usd', '2',
                            '--workdir', str(tmp_path / 'out')])
    assert code == cli.EXIT_STOP
    assert report['providers_requested'] == ['deepseek']
    assert report['calls_made'] == 1


def test_the_adapters_refuse_without_a_key_rather_than_dialing():
    for adapter in (providers.XaiTmAdapter(), providers.DeepSeekTmAdapter()):
        request = adapter.prepare_request(
            [{'fragment_id': 'f', 'source_string': 'x'}],
            requested_model=adapter.default_model, max_output_tokens=16,
            timeout_ms=1000)
        with pytest.raises(providers.ProviderUnavailable):
            adapter.invoke(request)


def test_the_two_paid_adapters_are_bound_to_their_own_routes():
    assert providers.XaiTmAdapter().route == model.ROUTE_XAI
    assert providers.DeepSeekTmAdapter().route == model.ROUTE_DEEPSEEK
    assert providers.XaiTmAdapter().base_url.startswith('https://api.x.ai')
    assert providers.DeepSeekTmAdapter().base_url.startswith(
        'https://api.deepseek.com')


def test_the_estimate_is_worst_case_not_optimistic():
    cheap = providers.estimate_cost_usd(model.ROUTE_DEEPSEEK,
                                        input_tokens=1000,
                                        max_output_tokens=1000)
    dear = providers.estimate_cost_usd(model.ROUTE_XAI, input_tokens=1000,
                                       max_output_tokens=1000)
    assert 0 < cheap < dear
    assert dear < cli.CANARY_COST_CEILING_USD


def test_env_example_documents_both_provider_keys():
    """Step 10.1 — empty placeholders plus a console hint, never a credential."""
    path = os.path.join(ROOT, '.env.example')
    with open(path, encoding='utf-8') as handle:
        text = handle.read()
    assert 'XAI_API_KEY=' in text
    assert 'DEEPSEEK_API_KEY=' in text
    for line in text.splitlines():
        for name in ('XAI_API_KEY', 'DEEPSEEK_API_KEY'):
            if line.strip().startswith('%s=' % name):
                assert line.strip() == '%s=' % name, 'no value may be committed'
