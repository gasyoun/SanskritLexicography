"""Pin the pure <ls> comparison helpers of synth_score (H5707 R7).

fidelity/hallucination/redundancy are multiset arithmetic over normalized
<ls> bodies; a drift in norm_ls or ls_multiset silently moves the Arm-B
bake-off scores. These tests had zero coverage before.
"""
import collections
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import synth_score as SS  # noqa: E402


def test_norm_ls_collapses_whitespace_and_trailing_punct():
    assert SS.norm_ls('RV.  7,32,12 ') == 'RV. 7,32,12'
    assert SS.norm_ls(' MBH. 1,2,3.\n') == 'MBH. 1,2,3'
    assert SS.norm_ls('  ') == ''


def test_norm_ls_equivalent_markup_is_one_token():
    # whitespace-only differences (incl. newlines) must not count as
    # loss/hallucination; spacing AROUND punctuation is significant
    a = SS.norm_ls('RV.\n7,32,12')
    b = SS.norm_ls('RV. 7,32,12')
    assert a == b == 'RV. 7,32,12'


def test_ls_multiset_counts_and_skips_empty():
    text = '<ls>RV. 1,1,1</ls> x <ls n="2">RV. 1,1,1</ls> <ls> , ; </ls>'
    ms = SS.ls_multiset(text)
    assert ms == collections.Counter({'RV. 1,1,1': 2})


def test_multiset_fidelity_hallucination_math():
    source = SS.ls_multiset('<ls>RV. 1,1,1</ls><ls>RV. 1,1,2</ls><ls>RV. 1,1,3</ls>')
    arm_b = SS.ls_multiset('<ls>RV. 1,1,1</ls><ls>RV. 1,1,1</ls><ls>MBH. 2,9,9</ls>')
    kept = sum((source & arm_b).values())
    fidelity = kept / sum(source.values())
    halluc = sum((arm_b - source).values())
    redundancy = sum(c - 1 for c in arm_b.values() if c > 1)
    assert fidelity == 1 / 3
    assert halluc == 2                      # duplicate RV.1,1,1 + the MBH cite
    assert redundancy == 1
