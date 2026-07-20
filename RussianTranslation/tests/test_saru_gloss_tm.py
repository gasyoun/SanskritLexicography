"""Regression test for the H1349 wave-4 read-only gloss TM lookup (GlossTM).

Fixture-backed, no glossary data / no heavy deps needed.

Run: `pytest tests/test_saru_gloss_tm.py` (working dir RussianTranslation).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import saru_gloss_tm as M   # noqa: E402

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'fixtures')


def _tm():
    return M.GlossTM(os.path.join(FIX, 'saru_gloss_lemma.fixture.jsonl'),
                     os.path.join(FIX, 'saru_gloss_root.fixture.jsonl'))


def test_lemma_lookup_ranked():
    hit = _tm().lookup('gam')
    assert hit['layer'] == 'lemma'
    assert [c['ru'] for c in hit['candidates']] == ['идти', 'пришёл']   # by n desc


def test_prefer_root_reaches_root_layer():
    hit = _tm().lookup('gam', prefer='root')
    assert hit['layer'] == 'root'
    assert hit['candidates'][0]['ru'] == 'пришел'


def test_avagraha_normalized_and_root_fallback():
    tm = _tm()
    assert tm.lookup("'gam")['layer'] == 'lemma'      # leading avagraha stripped
    assert tm.lookup('BU')['layer'] == 'root'          # lemma-miss falls back to root


def test_unknown_key_is_empty_not_error():
    assert _tm().lookup('zzz') == {'key': 'zzz', 'layer': None, 'candidates': []}


def test_top_k():
    assert len(_tm().lookup('gam', top=1)['candidates']) == 1


def test_module_selftest_passes():
    M.selftest()   # the shipped --selftest path
