# -*- coding: utf-8 -*-
"""H2876 — German apparatus metalanguage must never be rendered as gloss.

H2787's independent n=400 gate measured arm B's dominant serious-error class:
German grammatical apparatus (``eines``, ``im Comp. vorangehend``, ``so``,
``Ergänzung``) read as ordinary prose and "translated" (``{%eines%}`` →
«поручать кому-л.», ``{%die%}`` → «боги»). Those spans are legal German text,
so the ``{Tn}`` placeholder gate never sees them. This test wires the canonical
detector (sanskrit-util ``classify_german_metalanguage``, imported through the
``src/sanskrit_util.py`` shim — NOT a second private token table) into
``store_flags`` and pins:

  1. a fixture card that treats ``eines`` / ``im Comp. vorangehend`` as an
     ordinary gloss FAILS ``store_flags.row_metalanguage_ok`` (the H2876
     acceptance fixture);
  2. genuine gloss prose passes;
  3. the ``uncertain`` fence: ambiguous tokens (``so``, bare ``Ergänzung``)
     are treated as not-gloss (flagged) and logged to stderr;
  4. the shim resolves and its classifier agrees with the library's own
     golden expectations on the H2787/H2684 tokens.
"""
import io
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import store_flags  # noqa: E402
import sanskrit_util  # noqa: E402


def _row(de, ru):
    return {'de': de, 'ru': ru, 'key1': 'test', 'subcard': 'a',
            'review_status': 'approved'}


# ---- 1. the H2876 acceptance fixture: apparatus-as-gloss must FAIL ----------

def test_eines_as_gloss_fails():
    """`{%eines%}` → «поручать кому-л.» — the literal H2787 defect row."""
    assert not store_flags.row_metalanguage_ok(_row('eines', 'поручать кому-л.'))


def test_im_comp_vorangehend_as_gloss_fails():
    row = _row('im Comp. vorangehend', 'предшествующий в сложном слове')
    assert not store_flags.row_metalanguage_ok(row)


def test_die_as_gloss_fails():
    """`{%die%}` → «боги» — bare article reused as a translation unit."""
    assert not store_flags.row_metalanguage_ok(_row('die', 'боги'))


def test_grammar_label_as_gloss_fails():
    assert not store_flags.row_metalanguage_ok(_row('m. f. n.', 'мужской род'))


# ---- 2. genuine gloss prose passes ------------------------------------------

def test_real_gloss_passes():
    assert store_flags.row_metalanguage_ok(_row('Gabe, Geschenk', 'дар, подарок'))


def test_mid_text_function_word_passes():
    """`eines` INSIDE real prose is not apparatus (Name eines Baumes)."""
    assert store_flags.row_metalanguage_ok(
        _row('Name eines Baumes', 'название дерева'))


def test_mixed_apparatus_plus_prose_passes():
    """A formula plus real prose is a mixed unit — not the whole-span defect."""
    assert store_flags.row_metalanguage_ok(
        _row('vgl. das Vorhergehende', 'ср. предыдущее'))


def test_empty_ru_never_flags():
    assert store_flags.row_metalanguage_ok(_row('eines', ''))


# ---- 3. the uncertain fence: treat as not-gloss, log ------------------------

def test_uncertain_so_treated_as_not_gloss_and_logged():
    old = sys.stderr
    sys.stderr = io.StringIO()
    try:
        ok = store_flags.row_metalanguage_ok(_row('so', 'так'))
        logged = sys.stderr.getvalue()
    finally:
        sys.stderr = old
    assert not ok, 'ambiguous `so` must be treated as not-gloss (H2876 fence)'
    assert 'uncertain' in logged and "'so'" in logged


def test_uncertain_ergaenzung_treated_as_not_gloss():
    assert not store_flags.row_metalanguage_ok(_row('Ergänzung', 'дополнение'))


# ---- 4. shim + classifier sanity against the H2787/H2684 tokens -------------

def test_shim_resolves_and_reports_source():
    assert sanskrit_util.SANSKRIT_UTIL_SOURCE in ('sibling', 'vendored')
    assert callable(sanskrit_util.classify_german_metalanguage)


def test_h2787_and_h2684_token_categories():
    cgm = sanskrit_util.classify_german_metalanguage
    assert cgm('eines')[0]['category'] == 'function_word'
    assert cgm('so')[0]['category'] == 'uncertain'
    assert cgm('Ergänzung')[0]['category'] == 'uncertain'
    assert cgm('im Comp. vorangehend')[0]['category'] == 'recurring_formula'
    for extra in ('demin.', 'personif.', 'Uebertr.'):
        assert cgm(extra)[0]['category'] == 'recurring_formula', extra
    assert cgm('Gabe, Geschenk') == []


def test_fragmentize_has_no_private_token_table():
    """pwg_tm_fragmentize must consume the shared inventories, not redefine them."""
    import pwg_tm_fragmentize as fz
    assert fz.GRAMMAR_AB is sanskrit_util.GERMAN_GRAMMAR_AB
    assert fz.FORMULA_AB is sanskrit_util.GERMAN_FORMULA_AB
    src = open(os.path.join(SRC, 'pwg_tm_fragmentize.py'), encoding='utf-8').read()
    assert "GRAMMAR_AB = {" not in src and "FORMULA_AB = {" not in src
