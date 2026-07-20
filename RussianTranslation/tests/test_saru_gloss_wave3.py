"""Regression test for the H1349 wave-3 compound-split precision gate.

The gate is the load-bearing decision (a lax gate injected the recovered-but-wrong
regressions the wave-3 spike measured). No vidyut dep: the Chedaka is imported
lazily inside main(), and gate() is pure.

Run: `pytest tests/test_saru_gloss_wave3.py` (working dir RussianTranslation).
"""
import os
import sys
from types import SimpleNamespace as T

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import build_compound_split as C   # noqa: E402


def tok(lemma):
    return T(lemma=lemma, text=lemma)


def test_gate_requires_two_tokens_all_glossable():
    gm = {'sveta': 'белый', 'uzRIza': 'тюрбан', 'sat': 'сущий', 'AcAra': 'обычай'}
    # good: 2 members, both glossable
    assert C.gate([tok('sveta'), tok('uzRIza')], gm) == ['sveta', 'uzRIza']
    # single token -> rejected (nothing decomposed)
    assert C.gate([tok('sveta')], gm) is None
    # a member not glossable -> rejected (the junk-split guard)
    assert C.gate([tok('sveta'), tok('xyz')], gm) is None
    # a member with no lemma (None) -> rejected
    assert C.gate([tok('sveta'), tok(None)], gm) is None
    # three glossable members -> accepted
    assert C.gate([tok('sat'), tok('AcAra'), tok('sveta')], gm) == ['sat', 'AcAra', 'sveta']
    # empty -> rejected
    assert C.gate([], gm) is None
