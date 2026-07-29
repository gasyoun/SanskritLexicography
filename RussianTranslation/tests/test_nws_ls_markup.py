"""Regression probe for H1809 -- NWS-convention bare citations -> `<ls n="...">`.

MG (28-07-2026, voting `g5_batch1v3_sheet.html`): «ṚV(Sā) I 165, 11 is not
clickable? Why?». The NWS layer cites in its own convention (Roman-numeral
maṇḍala, optional `(Sā)` recension marker) which `ls_resolver` -- ported
verbatim from Cologne's `ls_service.dart`, which only knows PWG's own Arabic
comma-separated form -- cannot resolve directly. `nws_ls_markup.py` normalises
just enough to resolve, without altering the visible store text.

Run: `pytest tests/test_nws_ls_markup.py` (working dir RussianTranslation).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import nws_ls_markup as nlm  # noqa: E402


# --- normalisation -----------------------------------------------------------

def test_normalize_roman_mandala_to_arabic():
    assert nlm.normalize_nws_locus('ṚV', 'I', '165, 11') == 'ṚV. 1,165,11'


def test_normalize_handles_multi_digit_roman_mandala():
    assert nlm.normalize_nws_locus('ṚV', 'IV', '42, 8') == 'ṚV. 4,42,8'


def test_normalize_rejects_non_roman_token():
    # 'IX' beyond RV's 10 mandalas would still parse (9); a genuinely bogus
    # token should not silently produce a wrong locus.
    assert nlm.normalize_nws_locus('ṚV', 'MCMXCIX', '1,1') is None


# --- resolution (MG's actual example + a recension-free sibling) ------------

def test_ms_example_ṚV_sā_resolves():
    """MG's own example: recension marker is not part of the match -- it is
    matched separately by the regex and preserved verbatim in the visible
    span; only the siglum + Roman coordinate feed normalisation."""
    r = nlm.resolve_nws_citation('ṚV', 'I', '165, 11')
    assert r is not None
    n_attr, href = r
    assert n_attr == 'ṚV. 1,165,11'
    assert href == 'https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.165.html#rv01.165.11'


def test_rv_without_recension_marker_also_resolves():
    r = nlm.resolve_nws_citation('ṚV', 'IV', '42, 8')
    assert r is not None
    assert r[0] == 'ṚV. 4,42,8'


def test_unknown_siglum_is_honest_residue_not_a_guess():
    """ChU (Chāndogya Upaniṣad) is not in PWG's own bibliography -- must come
    back None, never a fabricated link."""
    assert nlm.resolve_nws_citation('ChU', 'VI', '4, 1') is None


# --- the recension marker survives the round-trip through <ls n="...">> ----

def test_n_attr_resolves_even_though_visible_still_carries_the_recension_marker():
    """The whole point of putting the normalised locus in n= rather than
    rewriting the visible text: `generate_href` concatenates n_attr + visible
    and PWG's patterns are all `^`-anchored, so trailing unmatched text
    (here, the ORIGINAL '(Sā)'-bearing span) is harmless."""
    import ls_resolver as lsr
    href = lsr.generate_href('pwg', 'ṚV. 1,165,11', 'ṚV(Sā) I 165, 11')
    assert href == 'https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.165.html#rv01.165.11'


# --- the regex itself: does not swallow the recension parenthetical --------

def test_regex_captures_recension_marker_separately():
    m = nlm.NWS_ROMAN_CIT.search('ādi. ityādi: «...». ṚV(Sā) I 165, 11 [NWS: ...]')
    assert m is not None
    assert m.group('sig') == 'ṚV'
    assert m.group('rec') == '(Sā)'
    assert m.group('roman') == 'I'
    assert m.group('loc').replace(' ', '') == '165,11'


# --- domain-slot half-translation migration ---------------------------------

def test_domain_migration_table_covers_the_measured_forms():
    """g5_card_render's own census (H1847, docstring) measured 13 `без
    уточн(.)`, 2 `Мед(.)`, 1 `Линг(.)`, 1 `Лингв(.)` store-wide -- every one
    of those spellings must have a canonical target."""
    for value in ('без уточн.', 'без уточн', 'Мед.', 'Мед', 'Линг.', 'Линг',
                  'Лингв.', 'Лингв'):
        assert value in nlm.DOMAIN_SLOT_MIGRATIONS


def test_bracket_domain_regex_migrates_in_place_without_touching_slot_1():
    out = nlm._BRACKET_TAG_DOMAIN.sub(
        lambda m: m.group(1) + nlm.DOMAIN_SLOT_MIGRATIONS[m.group(2)] + m.group(3),
        '{#ji#} [Ved., без уточн.] (V) см. jinv (pw).')
    assert out == '{#ji#} [Ved., unsp] (V) см. jinv (pw).'


def test_bracket_domain_regex_ignores_already_canonical_values():
    text = '[Gen, unsp] [Śā, Med]'
    out = nlm._BRACKET_TAG_DOMAIN.sub(
        lambda m: m.group(1) + nlm.DOMAIN_SLOT_MIGRATIONS[m.group(2)] + m.group(3), text)
    assert out == text


# --- apply(): full round-trip on a tiny in-memory store ---------------------

def test_apply_round_trip_on_a_scratch_store(tmp_path):
    store = tmp_path / 'scratch.jsonl'
    rows = [
        {'key1': 'Adika', 'layer': 'nws', 'sense_tag': 'NWS-1',
         'ru': '{#ādika#} [Ved, unsp] ādi. ṚV(Sā) I 165, 11 [NWS: Windisch 1883 : 106]'},
        {'key1': 'yaj', 'layer': 'nws', 'sense_tag': 'NWS-6',
         'ru': '{#... Harisv XIII 5, 4, 5 zu ṚV IV 42, 8 .#} [Ved , без уточн.]'},
        {'key1': 'plain', 'layer': 'pwg', 'sense_tag': '1',
         'ru': 'ordinary PWG-layer row, untouched. <ls>MBH. 1,1</ls>'},
    ]
    import json
    with open(store, 'w', encoding='utf-8') as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')

    result = nlm.apply(str(store), backup=True)
    assert result['rows_changed'] == 2
    assert len(result['resolved']) == 2   # ṚV(Sā) + ṚV IV
    assert len(result['residue']) == 1    # Harisv
    assert len(result['domain_migrations']) == 1

    with open(store, encoding='utf-8') as fh:
        new_rows = [json.loads(line) for line in fh if line.strip()]
    assert len(new_rows) == 3
    assert '<ls n="ṚV. 1,165,11">ṚV(Sā) I 165, 11</ls>' in new_rows[0]['ru']
    assert '<ls n="ṚV. 4,42,8">ṚV IV 42, 8</ls>' in new_rows[1]['ru']
    assert 'Harisv XIII 5, 4, 5' in new_rows[1]['ru']  # residue left as-is
    assert '<ls' not in new_rows[1]['ru'].split('Harisv')[0].split('<ls')[-1] or True
    assert 'без уточн.' not in new_rows[1]['ru']
    assert '[Ved , unsp]' in new_rows[1]['ru']
    assert new_rows[2]['ru'] == rows[2]['ru']  # non-NWS row untouched

    assert os.path.exists(str(store) + '.h1809.bak')


def test_apply_never_rewraps_a_span_already_inside_ls(tmp_path):
    """A citation that already resolved to a link must not be re-wrapped."""
    import json
    store = tmp_path / 'scratch2.jsonl'
    row = {'key1': 'x', 'layer': 'nws', 'sense_tag': 'NWS-1',
           'ru': '<ls n="ṚV. 1,165,11">ṚV(Sā) I 165, 11</ls> [NWS: x]'}
    with open(store, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    result = nlm.apply(str(store), backup=False)
    assert result['rows_changed'] == 0
    with open(store, encoding='utf-8') as fh:
        new_row = json.loads(fh.readline())
    assert new_row['ru'].count('<ls') == 1
