"""Pin slp1_norm join keys (H5707 R10/R7): the space-stripping normalization
exists so SLP1 keys join across stores, but distinct inputs CAN collapse onto
one key ("a ja" vs "aja"). These tests document both the intended joins and
the known collision class, so any change to the normalization surfaces here
instead of silently re-keying joins.
"""
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import slp1_norm  # noqa: E402


def test_canonical_slp1_join():
    assert slp1_norm.slp1_norm('aMsa') == slp1_norm.slp1_norm('amsa')


def test_internal_spaces_stripped():
    # a key split across a space in one store joins with the packed form
    assert slp1_norm.slp1_norm('a ja') == slp1_norm.slp1_norm('aja')


def test_homonym_number_stripped():
    assert slp1_norm.slp1_norm('as1') == slp1_norm.slp1_norm('as2')


def test_anusvara_collapse():
    assert slp1_norm.slp1_norm('ABAsanaM') == slp1_norm.slp1_norm('ABAsanam')


def test_documented_collision_class():
    # KNOWN (H5707 L10): space-stripping is not injective — distinct readings
    # can collide. If this test ever FAILS because norm became injective,
    # delete it and the review-doc caveat together.
    distinct = {'a ja': None, 'aja': None}
    keys = {slp1_norm.slp1_norm(k) for k in distinct}
    assert len(keys) == 1, 'space-stripping collision regressed/changed'
