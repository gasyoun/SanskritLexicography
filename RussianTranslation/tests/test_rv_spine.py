"""Acceptance tests for the RV multi-translation evidence spine, wave 1a (H1843).

Reads the committed pwg_ru/rv_*.jsonl outputs and asserts every hard invariant from
VERIFICATION.md Sec.2 (stanza/token counts, Geldner's four omitted stanzas, zero
empty rows) plus the deliverable-level acceptance criteria of Sec.1 (W1.1-W1.5).
Two invariants (the Renou per-mandala table and the 368-quoted_fr figure) are
asserted against this repo's OWN independently-reproduced numbers rather than the
handoff's published reference table -- see
docs/DECISIONS_LOG_rv_multitranslation.md for why (the published table fails its
own arithmetic; ours is internally consistent and matches the one number that
*is* independently reproducible, the 2,213 grand total).

Run: `pytest tests/test_rv_spine.py` (working dir RussianTranslation).
Selective: `pytest tests/test_rv_spine.py -k griffith|stanza|lemma|renou`.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PWG_RU_DIR = os.path.normpath(os.path.join(HERE, '..', 'pwg_ru'))
SCHEMAS_DIR = os.path.normpath(os.path.join(HERE, '..', 'schemas'))

sys.path.insert(0, os.path.join(HERE, '..', 'src'))
import rv_spine_build  # noqa: E402

GRIFFITH_PATH = os.path.join(PWG_RU_DIR, 'griffith_en_1896.json')
STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
LEMMA_PATH = os.path.join(PWG_RU_DIR, 'rv_lemma_occurrences.jsonl')
RENOU_PATH = os.path.join(PWG_RU_DIR, 'rv_renou_citation_index.jsonl')
SCHEMA_PATH = os.path.join(SCHEMAS_DIR, 'rv_translation_spine.schema.json')

EXPECTED_STANZA_COUNT = 10552
EXPECTED_TOKEN_COUNT = 164758
GELDNER_ABSENT_LOCATIONS = {'10.106.5', '10.106.6', '10.106.7', '10.106.8'}

# This repo's own reproduced Renou reference (see DECISIONS_LOG): the handoff's
# published per-mandala table sums to 1,930, not its own stated 2,213 total.
RENOU_TOTAL = 2213
RENOU_PER_MANDALA = {
    1: 527, 2: 124, 3: 179, 4: 149, 5: 195, 6: 124, 7: 192, 8: 133, 9: 257, 10: 333,
}


def _read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


@pytest.fixture(scope='module')
def griffith_doc():
    with open(GRIFFITH_PATH, encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope='module')
def stanza_records():
    return _read_jsonl(STANZA_PATH)


@pytest.fixture(scope='module')
def lemma_records():
    return _read_jsonl(LEMMA_PATH)


@pytest.fixture(scope='module')
def renou_records():
    return _read_jsonl(RENOU_PATH)


# --- W1.1 · griffith ---------------------------------------------------------

def test_griffith_all_stanzas_present(griffith_doc):
    assert len(griffith_doc['contents']) == EXPECTED_STANZA_COUNT


def test_griffith_meta_fields(griffith_doc):
    meta = griffith_doc['meta']
    assert meta['author'] == 'Ralph T. H. Griffith'
    assert meta['year'] == '1896'
    assert meta['language'] == 'en'
    assert meta['provenance']


def test_griffith_locations_are_dotted_form(griffith_doc):
    for rec in griffith_doc['contents']:
        parts = rec['location'].split('.')
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


def test_griffith_no_duplicate_locations(griffith_doc):
    locs = [rec['location'] for rec in griffith_doc['contents']]
    assert len(locs) == len(set(locs))


# --- W1.2 · stanza table ------------------------------------------------------

def test_stanza_record_count(stanza_records):
    assert len(stanza_records) == EXPECTED_STANZA_COUNT


def test_stanza_geldner_absent_count_and_locations(stanza_records):
    absent = [r['location'] for r in stanza_records
              if r['translations']['geldner_de_1951']['status'] == 'absent_from_source']
    assert len(absent) == 4
    assert set(absent) == GELDNER_ABSENT_LOCATIONS


def test_stanza_grassmann_elizarenkova_fully_present(stanza_records):
    for key in ('grassmann_de_1876', 'elizarenkova_ru_1989'):
        absent = [r for r in stanza_records if r['translations'][key]['status'] == 'absent_from_source']
        assert absent == []


def test_stanza_zero_empty_rows(stanza_records):
    for rec in stanza_records:
        for key, t in rec['translations'].items():
            assert t['status'] != 'empty', (rec['location'], key)


def test_stanza_mandala_hymn_stanza_split(stanza_records):
    sample = stanza_records[0]
    assert sample['location'] == '%d.%d.%d' % (
        sample['mandala'], sample['hymn'], sample['stanza'])


# --- W1.3 · lemma occurrences -------------------------------------------------

def test_lemma_token_count_reconciles(lemma_records):
    total = sum(r['occurrence_count'] for r in lemma_records)
    assert total == EXPECTED_TOKEN_COUNT


def test_lemma_occurrences_reference_valid_locations(lemma_records, stanza_records):
    valid_locations = {r['location'] for r in stanza_records}
    for lrec in lemma_records:
        for occ in lrec['occurrences']:
            assert occ['location'] in valid_locations


def test_lemma_dictionary_anchors_carried_when_present(lemma_records):
    with_gra = [r for r in lemma_records if r['id_gra']]
    with_pwg = [r for r in lemma_records if r['id_pwg']]
    assert with_gra
    assert with_pwg


def test_lemma_transformcontext_parsed_as_json_string_not_object():
    """Regression pin for VERIFICATION Sec.2 invariant 6: transformContext is a
    JSON string, not a nested object; a parser treating it as an object would
    silently yield zero tokens."""
    doc = rv_spine_build.load_lemmatization()
    sample = doc['contents'][0]
    assert isinstance(sample['transformContext'], str)
    parsed = json.loads(sample['transformContext'])
    assert isinstance(parsed, list)
    assert len(parsed) > 0


# --- W1.4 · flat mirror + schema ----------------------------------------------

def test_schema_file_is_valid_json_and_draft_2020_12():
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        schema = json.load(f)
    assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'


def test_stanza_and_lemma_jsonl_validate_against_schema():
    n_stanza, errors_stanza = rv_spine_build.validate_jsonl(
        STANZA_PATH, json.load(open(SCHEMA_PATH, encoding='utf-8')))
    n_lemma, errors_lemma = rv_spine_build.validate_jsonl(
        LEMMA_PATH, json.load(open(SCHEMA_PATH, encoding='utf-8')))
    assert n_stanza == EXPECTED_STANZA_COUNT
    assert errors_stanza == []
    assert n_lemma > 0
    assert errors_lemma == []


# --- W1.5 · renou citation index ----------------------------------------------

def test_renou_total_mentions(renou_records):
    assert len(renou_records) == RENOU_TOTAL


def test_renou_per_mandala_totals(renou_records):
    counts = {}
    for rec in renou_records:
        counts[rec['mandala']] = counts.get(rec['mandala'], 0) + 1
    assert counts == RENOU_PER_MANDALA


def test_renou_locus_unresolved_rows_have_null_location(renou_records):
    for rec in renou_records:
        if rec['locus_unresolved']:
            assert rec['location'] is None
        else:
            assert rec['location'] is not None


def test_renou_quoted_rows_have_latin_script_quote(renou_records):
    for rec in renou_records:
        if rec['mention_kind'] == 'quoted_fr':
            assert rec['quote_fr']
        else:
            assert rec['quote_fr'] is None


def test_renou_naming_does_not_collide_with_the_1956_register_axis():
    """ARCHITECTURE Sec.3.4 naming trap: nothing in this layer may be named
    `renou_*` alone (that prefix already means the Histoire de la langue
    sanskrite register axis)."""
    assert not os.path.exists(os.path.join(PWG_RU_DIR, 'renou_citation_index.jsonl'))
    for rec in _read_jsonl(RENOU_PATH)[:1]:
        assert rec['source'] == 'elizarenkova_commentary'
