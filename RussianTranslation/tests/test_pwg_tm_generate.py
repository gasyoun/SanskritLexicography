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


def test_source_lexicon_reuses_exact_gloss_across_lemmas():
    lex = {
        Gen.source_lexicon_key('definition_gloss', '{%Feuer%}'): '{%огонь%}',
    }
    frag = {
        'fragment_id': 'g1',
        'fragment_class': 'definition_gloss',
        'source_string': '{%Feuer%}',
        'reuse_key': 'other-lemma',
        'reuse_policy': 'suggest_only',
    }
    filled, stats = Gen.apply_targets([frag], {}, {}, lex)
    assert stats['source_reuse'] == 1
    assert filled[0]['target_string'] == '{%огонь%}'
    assert filled[0]['generation']['origin'] == 'exact_source_reuse'


def test_source_lexicon_does_not_reuse_sense_wrappers():
    lex = {
        Gen.source_lexicon_key('sense', 'long wrapper'): 'long RU',
    }
    frag = {
        'fragment_id': 's1',
        'fragment_class': 'sense',
        'source_string': 'long wrapper',
    }
    filled, stats = Gen.apply_targets([frag], {}, {}, lex)
    assert stats['source_reuse'] == 0
    assert stats['unfilled'] == 1
    assert (filled[0].get('target_string') in (None, '')) or (
        filled[0]['generation']['origin'] == 'unfilled')


def test_drain_seed_copies_once(tmp_path):
    seed = tmp_path / 'slice'
    dest = tmp_path / 'wave'
    seed.mkdir()
    (seed / 'checkpoint.json').write_text(
        json.dumps({'processed_keys': ['agni']}), encoding='utf-8')
    (seed / 'promoted.jsonl').write_text(
        '{"fragment_id":"a"}\n', encoding='utf-8')
    assert Gen.seed_out_dir(str(dest), str(seed)) is True
    assert (dest / 'promoted.jsonl').read_text(encoding='utf-8') == '{"fragment_id":"a"}\n'
    (dest / 'promoted.jsonl').write_text('{"fragment_id":"kept"}\n', encoding='utf-8')
    assert Gen.seed_out_dir(str(dest), str(seed)) is False
    assert (dest / 'promoted.jsonl').read_text(encoding='utf-8') == '{"fragment_id":"kept"}\n'


def test_live_complete_requires_key(monkeypatch):
    monkeypatch.delenv('XAI_API_KEY', raising=False)
    with pytest.raises(SystemExit):
        Gen.live_complete([{'fragment_id': 'x', 'fragment_class': 'definition_gloss',
                            'source_string': '{%x%}'}])


def test_refill_moves_drafted_gloss(tmp_path, monkeypatch):
    out = tmp_path / 'wave'
    out.mkdir()
    src = '{%Feuer%}'
    row = {
        'fragment_id': 'g-fire',
        'fragment_class': 'definition_gloss',
        'parent_record_id': 'p',
        'source_string': src,
        'source_hash': C.sha256_text(src),
        'target_string': None,
        'generation': {
            'model_id': 'grok-4.6',
            'route_id': 'grok-4.6',
            'prompt_sha256': Gen.prompt_sha256(),
            'pipeline_version': Gen.PIPELINE_VERSION,
            'source_hash': C.sha256_text(src),
            'origin': 'unfilled',
        },
    }
    (out / 'quarantine.jsonl').write_text(
        json.dumps(row, ensure_ascii=False) + '\n', encoding='utf-8')
    (out / 'promoted.jsonl').write_text('', encoding='utf-8')
    draft_path = tmp_path / 'drafts.jsonl'
    draft_path.write_text(json.dumps({
        'fragment_id': 'g-fire',
        'target_string': '{%огонь%}',
        'origin': 'grok-4.6-draft',
        'source_string': src,
    }, ensure_ascii=False) + '\n', encoding='utf-8')

    class Args:
        route = 'grok-4.6'
        out_dir = str(out)
        drafts = str(draft_path)
        publication = None
        no_reuse = True
        lexicon_extra = None

    monkeypatch.setattr(Gen.C, 'DEFAULT_PUBLICATION', str(tmp_path / 'missing.jsonl'))
    rc = Gen.cmd_refill(Args())
    assert rc == 0
    promoted = C.read_jsonl(str(out / 'promoted.jsonl'))
    quarantine = C.read_jsonl(str(out / 'quarantine.jsonl'))
    assert len(promoted) == 1
    assert promoted[0]['target_string'] == '{%огонь%}'
    assert quarantine == []
