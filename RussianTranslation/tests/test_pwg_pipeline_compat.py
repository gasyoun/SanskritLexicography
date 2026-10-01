"""H3714 Wave 1 — compatibility shims and the facade (V10, V11).

Pins that every legacy live verb has a facade mapping, that the old writer is
*not* disabled in Wave 1, that the Claude lane is shadowed rather than executed,
and that the facade CLI surface is the one the operator documents promise.
"""
import io
import json
import os
import subprocess
import sys
import warnings

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from pwg_pipeline import cli, compat, model, providers  # noqa: E402


def run_cli(argv, database=None):
    stream = io.StringIO()
    stdout = sys.stdout
    sys.stdout = stream
    try:
        prefix = ['--database', database] if database else []
        code = cli.main(prefix + argv)
    finally:
        sys.stdout = stdout
    text = stream.getvalue()
    return code, json.loads(text) if text.strip() else None


def test_every_legacy_live_verb_has_a_facade_mapping():
    coverage = compat.coverage()
    assert coverage['mapped_verbs']['pwg_tm_generate.py'] == [
        'drain', 'needed', 'reconcile', 'refill', 'run']
    assert coverage['mapped_verbs']['pwg_tm_w2_run.py'] == ['--all', '--probe']


def test_the_documented_mappings_hold():
    assert compat.facade_invocation('pwg_tm_generate.py', 'run') == ('execute',)
    assert compat.facade_invocation('pwg_tm_generate.py', 'drain') == ('execute',)
    assert compat.facade_invocation('pwg_tm_generate.py', 'needed') == ('plan',)
    assert compat.facade_invocation('pwg_tm_generate.py', 'refill') == \
        ('apply', '--intent', 'refill')
    assert compat.facade_invocation('pwg_tm_generate.py', 'reconcile') == \
        ('audit',)
    assert compat.facade_invocation('pwg_tm_w2_run.py', '--probe') == \
        ('canary', '--provider', 'deepseek')


def test_an_unmapped_verb_is_refused():
    with pytest.raises(compat.ShimRefusal):
        compat.facade_invocation('pwg_tm_generate.py', 'invented')
    with pytest.raises(compat.ShimRefusal):
        compat.facade_invocation('unrelated.py', 'run')


def test_a_shim_emits_a_deprecation_notice():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        message = compat.warn_deprecated('pwg_tm_generate.py', 'drain')
    assert caught and issubclass(caught[0].category, DeprecationWarning)
    assert 'python -m pwg_pipeline execute' in message


def test_the_old_writer_is_not_disabled_in_wave_one():
    """R3.5 — disabling waits for canaries, a replay, and two parity runs."""
    assert compat.writer_disabled() is False
    assert 'canaries' in compat.WRITER_DISABLE_CRITERION


def test_offline_helpers_are_preserved_untouched():
    preserved = compat.PRESERVED_OFFLINE['pwg_tm_generate.py']
    assert 'extract' in preserved and '--verify' in preserved


def test_shim_parity_is_exact_or_named():
    same = compat.shim_parity({'a': 1, 'b': 2}, {'a': 1, 'b': 2})
    assert same['exact'] is True
    drifted = compat.shim_parity({'a': 1}, {'a': 2})
    assert drifted['exact'] is False
    assert drifted['mismatches'] == ['a']


def test_the_legacy_generate_module_still_imports_and_keeps_its_route():
    """V10 — the proven Claude/PWG-TM behavior is unchanged by Wave 1."""
    import pwg_tm_generate as legacy
    assert legacy.ROUTE_ID == 'grok-4.6'
    assert legacy.DEFAULT_PRODUCTION_ROUTE is None
    with pytest.raises(SystemExit):
        legacy.require_route(None)


def test_the_claude_adapter_never_executes():
    adapter = providers.ClaudeHeadlessShadowAdapter()
    request = adapter.prepare_request(
        [{'fragment_id': 'f'}], requested_model='claude',
        max_output_tokens=16, timeout_ms=1000)
    with pytest.raises(providers.ProviderError):
        adapter.invoke(request)
    observed = adapter.observe({'model_id': 'claude', 'usage': {}})
    assert observed.served_model == 'claude'


def test_the_facade_exposes_the_documented_commands():
    parser = cli.build_parser()
    actions = [action for action in parser._actions
               if getattr(action, 'choices', None)
               and 'init' in (action.choices or {})]
    assert actions, 'the facade must expose subcommands'
    commands = set(actions[0].choices)
    assert {'init', 'import', 'plan', 'execute', 'audit', 'apply', 'review',
            'promote', 'replay', 'shadow-sync', 'canary'} <= commands


def test_init_and_plan_round_trip(tmp_path):
    database = str(tmp_path / 'c.sqlite')
    code, payload = run_cli(['init', '--campaign', 'c1', '--max-calls', '2',
                             '--cost-ceiling-usd', '4'], database)
    assert code == 0
    assert payload['campaign_id'] == 'c1'
    assert payload['promotable'] is False
    code, payload = run_cli(['plan', '--campaign', 'c1'], database)
    assert code == 0 and payload['count'] == 0


def test_unfenced_execute_is_refused_in_wave_one(tmp_path, capsys):
    database = str(tmp_path / 'c.sqlite')
    run_cli(['init', '--campaign', 'c1'], database)
    code, _ = run_cli(['execute', '--campaign', 'c1'], database)
    assert code == cli.EXIT_REFUSED


def test_promote_reports_the_canonical_fence(tmp_path):
    database = str(tmp_path / 'c.sqlite')
    run_cli(['init', '--campaign', 'c1'], database)
    code, payload = run_cli(['promote', '--campaign', 'c1'], database)
    assert code == 0
    assert payload['authority'] == 'coordinator journal only'
    assert any('canonical.v1.jsonl' in row for row in payload['canonical_fence'])


def test_shadow_sync_is_compare_only(tmp_path):
    database = str(tmp_path / 'c.sqlite')
    run_cli(['init', '--campaign', 'c1'], database)
    code, payload = run_cli(['shadow-sync', '--route',
                             model.ROUTE_CLAUDE_SHADOW], database)
    assert code == 0
    assert payload['execution_authority'] is False
    assert payload['promotion_authority'] is False


def test_the_module_entry_point_runs(tmp_path):
    environment = dict(os.environ, PYTHONPATH=SRC, PYTHONIOENCODING='utf-8')
    result = subprocess.run(
        [sys.executable, '-m', 'pwg_pipeline', '--database',
         str(tmp_path / 'c.sqlite'), 'compat'],
        env=environment, capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload['writer_disabled'] is False
