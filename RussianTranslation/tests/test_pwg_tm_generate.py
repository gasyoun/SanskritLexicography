"""H2684 Track B — Grok 4.6 route, gates, resume, independent quality."""
import json
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import pwg_tm_canonical as C  # noqa: E402
import pwg_tm_gates as G  # noqa: E402
import pwg_tm_generate as Gen  # noqa: E402
import pwg_tm_quality as Q  # noqa: E402

PILOT = os.path.join(SRC, 'pilot')


def test_default_production_route_is_not_grok():
    assert Gen.DEFAULT_PRODUCTION_ROUTE is None
    assert Gen.ROUTE_ID == 'grok-4.6'
    bsr = os.path.join(PILOT, 'bounded_staged_run.py')
    text = open(bsr, encoding='utf-8').read()
    assert 'grok-4.6' not in text


def test_require_route_refuses_implicit():
    with pytest.raises(SystemExit):
        Gen.require_route(None)
    with pytest.raises(SystemExit):
        Gen.require_route('claude-cli-headless')
    Gen.require_route('grok-4.6')


def test_gates_selftest_and_quarantine_retention():
    assert G.main(['--selftest']) == 0
    src = '{%Feuer.%}'
    frag = {
        'fragment_id': 'q1',
        'fragment_class': 'definition_gloss',
        'parent_record_id': 'p',
        'source_string': src,
        'source_hash': C.sha256_text(src),
        'target_string': '',
        'generation': {
            'model_id': 'grok-4.6',
            'route_id': 'grok-4.6',
            'prompt_sha256': Gen.prompt_sha256(),
            'pipeline_version': Gen.PIPELINE_VERSION,
            'source_hash': C.sha256_text(src),
        },
    }
    rec = G.gate_fragment(frag)
    row = G.apply_gate(frag, rec)
    assert row['promotion_status'] == 'quarantine'
    assert row['confidence_tier'] == 'uncertain'
    assert row['quarantine_reasons']
    assert row['reuse_policy'] == 'suggest_only'


def test_generate_verify_fixture():
    ok, msg = Gen.verify()
    assert ok, msg


def test_generate_resume_skips_done(tmp_path):
    ckpt = {
        'schema': 'pwg.tm.generate.checkpoint.v1',
        'processed_keys': ['agni'],
        'pending_keys': ['akzara'],
    }
    path = tmp_path / 'checkpoint.json'
    path.write_text(json.dumps(ckpt), encoding='utf-8')
    loaded = Gen.load_checkpoint(str(path))
    assert loaded['processed_keys'] == ['agni']


def test_reconciliation_zero_silent_drops():
    promoted = [{'fragment_class': 'sense', 'k1': 'a'}]
    quarantine = [{'fragment_class': 'citation', 'k1': 'a'}]
    recon = Gen.reconcile(
        [{'k1': 'a'}], [{'k1': 'a'}], promoted, quarantine, [],
        Gen.empty_ledger(), {'manifest_sha256': 'x'})
    assert recon['silent_drops'] == 0
    assert recon['promoted_fragments'] + recon['quarantine_fragments'] == 2
    assert recon['unaccounted_promotions'] == 0


def test_quality_refuses_grok_self_score_as_independent():
    assert Q._selftest() == 0
    packet = Q.blind_packet([{
        'fragment_id': 'f0',
        'fragment_class': 'sense',
        'generation': {'model_id': 'grok-4.6'},
        'gate_status': 'pass',
    }])
    assert 'generation' not in packet[0]
    assert packet[0]['adjudication']['fidelity'] is None
    fake = dict(packet[0])
    fake['adjudication'] = {
        'fidelity': 'pass', 'equivalence': 'correct', 'serious_error': False,
        'judge_id': 'grok-4.6', 'judge_model': 'grok-4.6',
    }
    report = Q.verify(sample_n=400, adjudication=[fake])
    assert report['independent_gate'] == 'refused_not_independent'
    assert report['ok'] is False


def test_quality_verify_without_adjudication_is_honest_not_run():
    report = Q.verify(sample_n=400, adjudication=None)
    assert report['independent_gate'] == 'not_run'
    assert report['ok'] is False
    assert any('no independent' in r for r in report['reasons'])


def test_quality_cli_verify_not_run():
    assert Q.main(['verify', '--sample', '400']) == 0
