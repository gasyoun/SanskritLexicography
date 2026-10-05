"""Pin iast_to_cyrillic transliteration (H5707 R7/R10): IAST → Cyrillic for
<is> names in RU prose. The contract is IAST IN — ASCII vowels are legitimate
IAST (a/i/u/e/o) and must map; the docstring's "non-Sanskrit chars pass
through" covers punctuation/digits only, NOT Latin words. These tests pin the
intended mapping plus that documented boundary.
"""
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import iast_to_cyrillic as I2C


def test_basic_vowels_and_consonants():
    assert I2C.transliterate('a') == 'а'
    assert I2C.transliterate('ka') == 'ка'
    assert I2C.transliterate('aṃśa') == 'амша'


def test_clusters_longest_match_first():
    assert I2C.transliterate('kṣa') == 'кша'
    assert I2C.transliterate('jñāna') == 'джнана'
    assert I2C.transliterate('buddhi') == 'буддхи'      # dh → дх before d


def test_capitalized_initial_stays_capitalized():
    out = I2C.transliterate('Aṃśa')
    assert out[0] == 'А' and out == 'Амша'


def test_punctuation_and_digits_pass_through():
    assert I2C.transliterate('aṃśa, 7') == 'амша, 7'
    assert I2C.transliterate('ṛcā-vāk') == 'рича-вак'


def test_documented_boundary_ascii_words_are_cyrillized():
    # DOCUMENTED BOUNDARY (H5707 L10): the function expects IAST; a Latin word
    # that is NOT IAST still goes through the table (no Sanskrit-ness guard).
    # Callers must feed <is> content only. If this test fails because a guard
    # was added, update the review doc — that closes L10's second half.
    assert I2C.transliterate('lat') == 'лат'
