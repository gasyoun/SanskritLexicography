"""H2686 — named QE backends and retrieval harness (no live spend)."""
import json
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import nn_api  # noqa: E402
import tm_grade  # noqa: E402
import tm_retrieval_eval as E  # noqa: E402


def test_comet_name_never_aliases_labse_or_proxy():
    fn, name = tm_grade.make_qe('comet')
    assert name in ('comet', 'proxy')
    assert name != 'labse'
    assert nn_api.qe_available('comet') is False
    rec = nn_api.qe_backend_receipt('comet')
    assert rec['backend'] == 'comet'
    assert rec['available'] is False
    assert rec['labelled_as_comet'] is False
    assert rec['mock'] is False


def test_labse_receipt_is_not_comet():
    rec = nn_api.qe_backend_receipt('labse')
    assert rec['backend'] == 'labse'
    assert rec['labelled_as_comet'] is False
    if rec['available']:
        score = nn_api.qe('karma', 'действие', backend='labse')
        assert score is not None
        assert 0.0 <= score <= 1.0
        assert nn_api.qe('karma', 'действие', backend='comet') is None
        _, name = tm_grade.make_qe('labse')
        assert name == 'labse'


def test_proxy_rho_constant_still_labelled_preliminary():
    assert tm_grade.PROXY_RHO_PRELIMINARY == pytest.approx(-0.0351)
    md = tm_grade._render_calibration_md(
        'labse', 320, -0.01, {'A': 0.6, 'B': 0.5, 'C': 0.4},
        [('A', 'B', 0.55)], False,
        'PRELIMINARY (genuine backend=labse)')
    assert '**not** COMET-QE' in md
    assert '-0.0351' in md
    assert '**QE backend used: `labse`.**' in md


def test_retrieval_selftest_and_live_renderer_refuses_mocks():
    assert E.selftest() == 0
    with pytest.raises(ValueError):
        E._render_live_md({'engine': 'none', 'mock': False},
                          {'n': 0}, {'n': 0})


def test_freeze_excludes_copy_through(tmp_path):
    sample = tmp_path / 'sample.jsonl'
    adj = tmp_path / 'adj.jsonl'
    rows = [
        {
            'fragment_id': 'copy1',
            'fragment_class': 'citation',
            'source_string': '<ls>X</ls>',
            'target_string': '<ls>X</ls>',
            'source_locator': {'lemma_slp1': 'a'},
            'promotion_status': 'promoted',
        },
        {
            'fragment_id': 'gloss1',
            'fragment_class': 'definition_gloss',
            'source_string': 'Feuer',
            'target_string': 'огонь',
            'source_locator': {'lemma_slp1': 'agni'},
            'promotion_status': 'promoted',
        },
        {
            'fragment_id': 'sense1',
            'fragment_class': 'sense',
            'source_string': 'gehen',
            'target_string': 'идти',
            'source_locator': {'lemma_slp1': 'gam'},
            'promotion_status': 'quarantine',
        },
    ]
    sample.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows),
                      encoding='utf-8')
    adj.write_text('', encoding='utf-8')
    batch, meta = E.freeze_batch(str(sample), str(adj), n_per_class=4)
    ids = {r['fragment_id'] for r in batch}
    assert 'copy1' not in ids
    assert 'gloss1' in ids
    assert 'sense1' in ids
    assert meta['copy_through_excluded'] == 1


def test_norm_edit_and_sha():
    assert E.norm_edit('огонь', 'огонь') == 0.0
    assert E.norm_edit('огонь', 'оген') > 0
    assert len(E.sha256_text('x')) == 64
