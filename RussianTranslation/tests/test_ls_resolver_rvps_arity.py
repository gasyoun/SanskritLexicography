"""Regression probe for H1714 / gasyoun/SanskritLexicography#826.

Two defect classes fixed:

  1. Mislink -- 'RV. PRAT.' / 'RV. PRATIS.' (Rgveda-Pratisakhya) used to
     resolve through the Rgveda-hymn generator ('rvAvHymnUrl2'), silently
     returning a plausible-looking wrong URL (a different text) instead of
     the rvps scan. The undotted 'RV. PRAT.' spelling matched no pattern at
     all and fell through to the fallback RV/AV helper, producing a
     nonexistent rv00.* mandala-00 URL.
  2. Arity gaps -- TS. and TBR. resolved only at 4-parameter arity because
     their fallback dispatch branches tested the citation-code literal
     ('TS.') instead of the prefix-map value the dispatch actually receives
     ('taittiriyas'); TBR. additionally had no fallback wired at all
     (uppercase 'TBR.' was absent from the prefix map).

Run: `pytest tests/test_ls_resolver_rvps_arity.py` (working dir RussianTranslation).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import ls_resolver as lsr  # noqa: E402


# --- Rgveda-Pratisakhya (rvps) mislink --------------------------------------

def test_rvps_undotted_spelling_resolves_to_rvps_scan():
    url = lsr.generate_href('pwg', 'RV. PRAT. ', '4,12')
    assert url == 'https://sanskrit-lexicon-scans.github.io/rvps/app1/?4,12'


def test_rvps_diacritic_spelling_resolves_to_rvps_scan():
    url = lsr.generate_href('pwg', 'ṚV. PRĀTIŚ. ', '4,12')
    assert url == 'https://sanskrit-lexicon-scans.github.io/rvps/app1/?4,12'


def test_rvps_undotted_spelling_does_not_fall_through_to_rv_hymn_pages():
    url = lsr.generate_href('pwg', 'RV. PRAT. ', '4,12')
    assert url is not None
    assert 'rv00' not in url
    assert 'rvlinks' not in url


def test_bare_rv_citation_still_resolves_to_the_hymn_pages():
    """Regression guard: the rvps pattern must not shadow ordinary RV citations."""
    url = lsr.generate_href('pwg', 'ṚV. ', '10,85,24')
    assert url == 'https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv10.085.html#rv10.085.24'


# --- Taittiriya Samhita (TS.) arity gap -------------------------------------

def test_ts_resolves_at_4_param_arity():
    url = lsr.generate_href('pwg', 'TS. ', '1,2,3,4')
    assert url == 'https://sanskrit-lexicon-scans.github.io/taittiriyas/app1?1,2,3,4'


def test_ts_resolves_at_3_param_arity():
    url = lsr.generate_href('pwg', 'TS. ', '1,2,3')
    assert url == 'https://sanskrit-lexicon-scans.github.io/taittiriyas/app1?1,2,3'


# --- Taittiriya Brahmana (TBR.) arity gap -----------------------------------

def test_tbr_resolves_at_4_param_arity():
    url = lsr.generate_href('pwg', 'TBR. ', '1,2,3,4')
    assert url == 'https://sanskrit-lexicon-scans.github.io/taittiriyabr/app1?1,2,3,4'


def test_tbr_resolves_at_3_param_arity():
    url = lsr.generate_href('pwg', 'TBR. ', '1,2,3')
    assert url == 'https://sanskrit-lexicon-scans.github.io/taittiriyabr/app1?1,2,3'


# --- Pancaratra (PANCAR.) -- confirm existing arities still resolve --------

def test_pancar_resolves_at_3_param_arity():
    url = lsr.generate_href('pwg', 'PAÑCAR. ', '1,2,3')
    assert url == 'https://sanskrit-lexicon-scans.github.io/pancar/app1?1,2,3'


def test_pancar_resolves_at_page_form():
    url = lsr.generate_href('pwg', 'PAÑCAR. ', 'S. 100')
    assert url == 'https://sanskrit-lexicon-scans.github.io/pancar/app0?100'
