"""Regression tests for the H1349 wave-2 precision-panel scaffold.

Pins the pure helpers of the sampler + aggregator (freq bands, Wilson CI, panel
majority vote, tier x frequency stratification) — no heavy deps, no live panel.

Run: `pytest tests/test_saru_gloss_wave2.py` (working dir RussianTranslation).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import saru_gloss_sample as S      # noqa: E402
import saru_gloss_aggregate as A   # noqa: E402


def test_freq_band_boundaries():
    assert S.freq_band(1) == 'hapax(1)'
    assert S.freq_band(2) == 'low(2-9)'
    assert S.freq_band(9) == 'low(2-9)'
    assert S.freq_band(10) == 'mid(10-99)'
    assert S.freq_band(99) == 'mid(10-99)'
    assert S.freq_band(100) == 'high(100+)'
    assert S.freq_band(5000) == 'high(100+)'


def test_wilson_interval():
    assert A.wilson(0, 0) == (0.0, 0.0)
    lo, hi = A.wilson(10, 10)          # all-correct: hi hits ~100, lo well below
    assert hi > 99.0 and lo < 100.0 and lo > 60.0
    lo, hi = A.wilson(5, 10)           # 50% centred, interval straddles 50
    assert lo < 50.0 < hi
    lo, hi = A.wilson(80, 100)         # tighter with n
    assert 70.0 < lo < 80.0 < hi < 88.0


def test_panel_majority():
    assert A.majority(['correct', 'correct', 'correct']) == ('correct', 'unanimous')
    assert A.majority(['correct', 'correct', 'wrong']) == ('correct', 'majority')
    lbl, agree = A.majority(['correct', 'wrong', 'unsure'])
    assert agree == 'split'            # no value reaches 2 of 3


def test_stratified_balances_cells_and_is_reproducible():
    # 3 tiers x 2 bands populated unevenly; k=3/cell; a small cell takes all.
    rows = []
    for tier in ('dcs', 'vidyut', 'marker'):
        for n in (1, 1, 1, 1, 1, 50, 50, 50, 50, 50):   # 5 hapax + 5 mid per tier
            rows.append({'slp1': f'{tier}{n}', 'sa': 'x', 'n': n, 'tier': tier,
                         'lemma': 'l', 'upos': 'NOUN', 'root': '', 'top_ru': 'ru'})
    # shrink one cell so it must take all it has
    rows = [r for r in rows if not (r['tier'] == 'marker' and r['n'] == 50)][:26] + \
        [r for r in rows if r['tier'] == 'marker' and r['n'] == 50][:2]

    s1, cells = S.stratified(rows, 3, seed=42)
    s2, _ = S.stratified(rows, 3, seed=42)
    assert [r['slp1'] for r in s1] == [r['slp1'] for r in s2]   # reproducible

    import collections
    comp = collections.Counter((r['tier'], S.freq_band(r['n'])) for r in s1)
    # every populated cell present; capped at min(3, available)
    for cell, avail in cells.items():
        assert comp[cell] == min(3, len(avail))
