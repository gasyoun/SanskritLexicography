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
JB_PATH = os.path.join(PWG_RU_DIR, 'jamison_brereton_en_2014.json')
RENOU_WITNESS_PATH = os.path.join(PWG_RU_DIR, 'rv_renou_evp_witness.jsonl')
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


@pytest.fixture(scope='module')
def jb_doc():
    with open(JB_PATH, encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope='module')
def renou_witness_records():
    return _read_jsonl(RENOU_WITNESS_PATH)


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
    for key in ('grassmann_de_1876', 'elizarenkova_ru_1989', 'jamison_brereton_en_2014'):
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


@pytest.mark.skipif(not os.path.exists(rv_spine_build.LEMMATIZATION_PATH),
                    reason='RV lemmatization not built in this checkout (derived data is '
                           'gitignored) — the invariant cannot be exercised')
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


@pytest.mark.skipif(not (os.path.exists(STANZA_PATH) and os.path.exists(LEMMA_PATH)),
                    reason='RV spine JSONL not built in this checkout (derived data is '
                           'gitignored) — nothing to validate against the schema')
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


# =============================================================================
# Wave 1b (H1844) — typing, layer B, pipeline bridge, wisdomlib
# =============================================================================

import rv_divergence_type  # noqa: E402
import rv_pipeline_bridge  # noqa: E402
import rv_wisdomlib_bridge  # noqa: E402
import rv_wordlevel_align  # noqa: E402

PILOT_PATH = os.path.join(PWG_RU_DIR, 'rv_divergence_pilot.jsonl')
PRECISION_REPORT = os.path.normpath(
    os.path.join(HERE, '..', 'gold', 'rv_wordlevel_precision_report.md'))
GOLD_WORDLEVEL = os.path.normpath(
    os.path.join(HERE, '..', 'gold', 'rv_wordlevel_gold.jsonl'))
TM_SCHEMA = os.path.join(SCHEMAS_DIR, 'translation_memory.schema.json')
TM_WEIGHTS = os.path.normpath(os.path.join(HERE, '..', 'src', 'tm_source_weights.json'))


# --- W1.6 · divergence pilot --------------------------------------------------

def test_divergence_module_selftests_pass():
    """Every wave-1b module carries deterministic asserts that need no model and no
    network; they must stay green in CI, which has neither."""
    assert rv_divergence_type.selftest() == 0
    assert rv_wordlevel_align.selftest() == 0
    assert rv_pipeline_bridge.selftest() == 0
    assert rv_wisdomlib_bridge.selftest() == 0


def test_divergence_absent_pairs_are_deterministic_not_model_decided():
    """W1.6 acceptance: every `absent_from_source` pair is labelled `omitted_by_one`
    WITHOUT a model call. RV 10.106.5–8 (Geldner's gap) is the known ground truth.

    The expected count tracks the translator count rather than being hardcoded — H1910
    took it from 3-of-6 to 4-of-10, and a sixth witness would move it again."""
    stanza = {
        'location': '10.106.5', 'mandala': 10, 'hymn': 106, 'stanza': 5,
        'translations': {
            'grassmann_de_1876': {'status': 'present', 'text': 'x'},
            'geldner_de_1951': {'status': 'absent_from_source', 'text': None},
            'elizarenkova_ru_1989': {'status': 'present', 'text': 'y'},
            'griffith_en_1896': {'status': 'present', 'text': 'z'},
            'jamison_brereton_en_2014': {'status': 'present', 'text': 'w'},
        }}
    det = rv_divergence_type.deterministic_pairs(stanza)
    assert len(det) == len(rv_divergence_type.TRANSLATORS) - 1 == 4
    for key, entry in det.items():
        assert 'geldner' in key
        assert entry['class'] == 'omitted_by_one'
        assert entry['method'] == 'deterministic'


def test_divergence_taxonomy_projects_losslessly_to_the_coarse_fallback():
    """K3's fallback taxonomy must be a projection of the five classes, so a run typed
    at five classes is still usable if the fine distinction is ruled non-separable."""
    assert set(rv_divergence_type.COARSE_MAP) == set(rv_divergence_type.FIVE_CLASSES)
    assert set(rv_divergence_type.COARSE_MAP.values()) == set(rv_divergence_type.COARSE_CLASSES)
    assert rv_divergence_type.COARSE_MAP['omitted_by_one'] == 'omission'
    assert rv_divergence_type.COARSE_MAP['agreement'] == 'agreement'


# --- H2192 · the asymmetric classes are directional, or they are one class -------

def test_converse_classes_share_a_coarse_class():
    """`added_by_one` and `omitted_by_one` name ONE undirected event from opposite ends, so
    the coarse projection must not move when a labeller picks one name over the other.

    RED before H2192: the map sent added_by_one -> 'divergence' and omitted_by_one ->
    'omission', so a semantically vacuous relabelling changed the coarse class too. The
    defect was latent (added_by_one had fired 0/12,000), which is why every published
    coarse kappa is unchanged by the fix -- see rv_added_by_one_diagnosis.py coarse-kappa.
    """
    cm = rv_divergence_type.COARSE_MAP
    assert cm['added_by_one'] == cm['omitted_by_one'] == 'omission'
    assert set(rv_divergence_type.ASYMMETRIC_CLASSES) == {'added_by_one', 'omitted_by_one'}


def test_asymmetric_labels_demand_a_direction():
    """The prompt must fix a reading point and require `surplus_side`. Without it the two
    converse names are indistinguishable and one absorbs the whole event class -- measured
    at added_by_one 0/12,000 in the H1844 pilot, and 0/300, 0/300, 0/267 across H1901's
    three independently-trained arms."""
    assert 'surplus_side' in rv_divergence_type.SYSTEM
    assert 'FIRST translator named in the pair key' in rv_divergence_type.SYSTEM


def test_surplus_side_is_resolved_against_its_own_pair_never_coerced():
    pk = 'grassmann_de_1876|griffith_en_1896'
    assert rv_divergence_type.normalise_side('griffith_en_1896', pk) == ('griffith_en_1896', None)
    # A model asked for `griffith_en_1896` will sometimes answer `Griffith`.
    assert rv_divergence_type.normalise_side('Griffith', pk) == ('griffith_en_1896', None)
    # A translator outside THIS pair, an absent value, and an unresolvable one are each
    # recorded as a gap rather than snapped to the nearest side — the posture H1901 already
    # took with out-of-enum classes (`class: null`, never a nearest-class coercion).
    assert rv_divergence_type.normalise_side('geldner_de_1951', pk)[0] is None
    assert rv_divergence_type.normalise_side(None, pk) == (None, 'missing')
    assert rv_divergence_type.normalise_side('both', pk)[0] is None


def test_deterministic_arm_carries_the_same_direction():
    """Where the direction is a fact about the source rather than a judgment, it is emitted
    both ways round: the side missing the stanza, and the side holding the surplus."""
    stanza = {
        'location': '10.106.5', 'mandala': 10, 'hymn': 106, 'stanza': 5,
        'translations': {
            t: {'status': 'absent_from_source' if t == 'geldner_de_1951' else 'present',
                'text': None if t == 'geldner_de_1951' else 'x'}
            for t in rv_divergence_type.TRANSLATORS}}
    det = rv_divergence_type.deterministic_pairs(stanza)
    assert det
    for pair_key, row in det.items():
        assert row['missing_side'] == 'geldner_de_1951'
        assert row['surplus_side'] in pair_key.split('|')
        assert row['surplus_side'] != row['missing_side']


def test_added_by_one_diagnosis_selftest_passes():
    """The H2192 diagnosis module carries the guard properties for this defect: the
    direction field, the non-coercing resolver, and the invariant coarse projection."""
    import rv_added_by_one_diagnosis
    assert rv_added_by_one_diagnosis.selftest() == 0


@pytest.mark.skipif(not os.path.exists(PILOT_PATH), reason='pilot not run in this checkout')
def test_divergence_pilot_rows_are_well_formed():
    rows = _read_jsonl(PILOT_PATH)
    assert rows
    for rec in rows[:200]:
        assert rec['location'] and rec['arm'] and rec['model']
        for key, entry in rec['pairs'].items():
            assert key in rv_divergence_type.PAIR_KEYS
            assert entry['method'] in ('model', 'deterministic')
            if entry['class'] is not None:
                assert entry['class'] in rv_divergence_type.FIVE_CLASSES


# --- W1.10 · judge witness ----------------------------------------------------

def test_witness_present_for_spine_headword_absent_otherwise():
    """W1.10 acceptance, verbatim: a headword with an `id_pwg` in the spine receives a
    witness block; one without receives none."""
    stanzas, lemmas = _tiny_spine()
    idx = rv_pipeline_bridge.index_by_id_pwg(lemmas)
    assert rv_pipeline_bridge.witness_block_for_headword('349', idx, stanzas) is not None
    assert rv_pipeline_bridge.witness_block_for_headword('404404', idx, stanzas) is None


def test_witness_is_capped_at_three_loci_and_marked_advisory():
    stanzas, lemmas = _tiny_spine()
    idx = rv_pipeline_bridge.index_by_id_pwg(lemmas)
    w = rv_pipeline_bridge.witness_block_for_headword('349', idx, stanzas)
    assert len(w['loci']) <= rv_pipeline_bridge.WITNESS_N == 3
    assert w['advisory'] is True


# --- W1.11 · contradiction gate ----------------------------------------------

def test_gate_queues_contradicting_card_and_passes_agreeing_one():
    """W1.11 acceptance, verbatim: a synthetic contradicting card is queued, a synthetic
    agreeing card is not."""
    stanzas, lemmas = _tiny_spine()
    idx = rv_pipeline_bridge.index_by_id_pwg(lemmas)
    w = rv_pipeline_bridge.witness_block_for_headword('349', idx, stanzas)
    queued = rv_pipeline_bridge.gate_decision('колесница, боевая повозка', w)
    passed = rv_pipeline_bridge.gate_decision('Agni, der Priester des Opfers', w)
    assert queued['action'] == 'queue_for_review'
    assert passed['action'] != 'queue_for_review'


def test_gate_never_rejects_and_never_consults_layer_b():
    """ARCHITECTURE Sec.5 (queue, never reject) and R14 (layer B excluded after its gold
    precision failed on all three languages)."""
    stanzas, lemmas = _tiny_spine()
    idx = rv_pipeline_bridge.index_by_id_pwg(lemmas)
    w = rv_pipeline_bridge.witness_block_for_headword('349', idx, stanzas)
    for gloss in ('колесница', 'Agni', '', 'Priester'):
        d = rv_pipeline_bridge.gate_decision(gloss, w)
        assert d['action'] in ('queue_for_review', 'log_only', 'none')
        assert 'reject' not in d['action']
        assert d['layer_b_used'] is False


def _tiny_spine():
    stanzas = {
        '1.1.1': {'location': '1.1.1', 'translations': {
            'grassmann_de_1876': {'status': 'present', 'text': 'Den Priester Agni preise ich'},
            'geldner_de_1951': {'status': 'present', 'text': 'Agni berufe ich als Bevollmächtigten'},
            'elizarenkova_ru_1989': {'status': 'present', 'text': 'Агни призываю я жреца'},
            'griffith_en_1896': {'status': 'present', 'text': 'I Laud Agni the chosen Priest'}}},
    }
    lemmas = [{'lemma': 'agní-', 'id_pwg': ['349'], 'occurrence_count': 1724,
               'occurrences': [{'location': '1.1.1', 'form': 'agním',
                                'token_index': 0, 'wordlevel': None}]}]
    return stanzas, lemmas


# --- W1.12 · TM tier ----------------------------------------------------------

def test_tm_tier_added_and_reachable_on_both_languages():
    """W1.12: the new trust_level validates against the TM schema and the tier is
    reachable on BOTH `ru` and `en` (R7 — not for Russian only)."""
    with open(TM_SCHEMA, encoding='utf-8') as f:
        schema = json.load(f)
    assert 'corpus_translation_witness' in schema['$defs']['trust_level']['enum']
    assert 'suggest_only' in schema['$defs']['reuse_policy']['enum']
    assert set(schema['$defs']['lang']['enum']) == {'ru', 'en'}


def test_tm_source_weights_are_keyed_by_work_not_language():
    """The structural claim behind the SHARED parity verdict: a third language is a new
    row, not a rewrite. An English witness must already carry its own prior."""
    with open(TM_WEIGHTS, encoding='utf-8') as f:
        weights = json.load(f)
    by_work = weights['by_work']
    for translator in ('rigveda-grassmann-de-1876', 'rigveda-geldner-de-1951',
                       'rigveda-elizarenkova-ru-1989', 'rigveda-griffith-en-1896'):
        assert translator in by_work, translator
        assert 0.0 <= by_work[translator] <= 1.0
    assert by_work['rigveda-griffith-en-1896'] > 0, 'the EN path must be populated, not promised'


# --- W1.9 · layer-B precision (recorded failure) ------------------------------

@pytest.mark.skipif(not os.path.exists(PRECISION_REPORT), reason='gold not scored here')
def test_layer_b_precision_failure_is_recorded_not_silently_passed():
    """R14 / stop condition 3. Layer B measured de 29.2 % · ru 19.2 % · en 10.5 % against
    an 85 % bar. This test pins that the FAILURE is recorded — a future change that makes
    layer B look passing without new gold must break here."""
    text = open(PRECISION_REPORT, encoding='utf-8').read()
    assert 'stop condition 3' in text.lower()
    gold = _read_jsonl(GOLD_WORDLEVEL)
    labelled = [r for r in gold if r['verdict'] in ('correct', 'incorrect')]
    assert labelled, 'no adjudicated rows'
    for r in labelled:
        assert r['annotator'], 'every verdict must name its annotator (tier + version)'
    for target in ('de', 'ru', 'en'):
        rows = [r for r in labelled if r['target'] == target]
        if rows:
            precision = sum(1 for r in rows if r['verdict'] == 'correct') / len(rows)
            assert precision < 0.85, (target, precision)


# --- W1.13 · wisdomlib --------------------------------------------------------

def test_wisdomlib_join_key_is_sound_so_the_empty_result_is_a_data_fact():
    """The role-2 join returned 0 rows. This pins that the KEY is not why: the folded key
    demonstrably carries ASCII slugs onto IAST headwords. The zero is a property of the
    63-word Buddhist-terminology feed, not of the join."""
    assert rv_wisdomlib_bridge.fold_key('akshobhya') == rv_wisdomlib_bridge.fold_key('akṣobhya')
    assert rv_wisdomlib_bridge.fold_key(rv_wisdomlib_bridge.strip_lemma('agní-')) == 'agni'
    assert rv_wisdomlib_bridge.fold_key(rv_wisdomlib_bridge.strip_lemma('índra-')) == 'indra'
    wl = {'agni': {'word': 'agni', 'traditions': ['vedic'], 'gloss_count': 3, 'headings': []}}
    rv = {'agni': {'lemma': 'agní-', 'occurrence_count': 9, 'id_pwg': ['349']}}
    assert len(rv_wisdomlib_bridge.build_role2(wl, rv)) == 1


def test_wisdomlib_bridge_makes_no_network_calls():
    """W1.13 acceptance: the run makes zero network calls (R17)."""
    src = open(rv_wisdomlib_bridge.__file__, encoding='utf-8').read()
    import re as _re
    assert not _re.findall(
        r'^\s*(?:import|from)\s+(urllib|requests|httpx|socket|aiohttp|http)\b', src, _re.M)


# =============================================================================
# H1910 — Jamison–Brereton 2014 as the fifth column, Renou EVP as a witness
# =============================================================================

import build_rv_divergence_gate_sheet as gate  # noqa: E402
import rv_renou_evp_witness as evp             # noqa: E402

JB_UNTRANSLATED = {'10.106.5', '10.106.6', '10.106.7', '10.106.8'}


# --- the J–B column -----------------------------------------------------------

def test_jb_covers_every_canonical_locus_exactly_once(jb_doc):
    """H1910 requirement 4, the whole acceptance bar: J–B translate the complete RV, so
    anything short of 10,552 with 0 unmatched means the PARSER is wrong, not the book."""
    locs = [r['location'] for r in jb_doc['contents']]
    assert len(locs) == EXPECTED_STANZA_COUNT
    assert len(set(locs)) == EXPECTED_STANZA_COUNT


def test_jb_locations_match_the_spine_exactly(jb_doc, stanza_records):
    assert {r['location'] for r in jb_doc['contents']} == {r['location'] for r in stanza_records}


def test_jb_meta_records_source_and_its_limitations(jb_doc):
    meta = jb_doc['meta']
    assert meta['year'] == '2014' and meta['language'] == 'en'
    assert 'Jamison' in meta['author'] and 'Brereton' in meta['author']
    # Provenance must name the OCR it came from: this is not a publisher text, and a
    # consumer weighting it at 0.92 has to be able to see that.
    assert 'archive.org' in meta['provenance']
    assert meta['known_limitations']


def test_jb_carries_no_commentary(jb_doc):
    """Requirement 3, pinned. Three kinds of J–B editorial matter were measured leaking
    into stanza text — a heading block whose heading the OCR destroyed, a `Mandala N`
    section introduction, and a hymn-group introduction — and every one of them was
    invisible to the locus count, which read 10,552/10,552 throughout."""
    import rv_jamison_brereton_extract as jbx
    leaked = [r['location'] for r in jb_doc['contents']
              if jbx.COMMENTARY_RE.search(r['text'])]
    assert leaked == [], leaked[:10]


def test_jb_carries_no_page_furniture(jb_doc):
    """Page numbers and running heads were being stripped where markers are DETECTED but
    not where text is ASSEMBLED, so a stanza spanning a page break kept them mid-text."""
    import re as _re
    bad = [r['location'] for r in jb_doc['contents']
           if _re.search(r'\b\d{2,4}\s+\d{1,2}\.\d{1,3}\s*$', r['text'])
           or _re.search(r'\b\d{1,2}\.\d{1,3}\s+\d{2,4}\s*$', r['text'])]
    assert bad == [], bad[:10]


def test_jb_untranslated_loci_are_present_not_absent(jb_doc):
    """RV 10.106.5–8, the four stanzas Geldner omits, are the ones J–B print as
    transliterated Vedic rather than English: they decline to translate rather than skip.
    So they must be `present` (an absence here would be a parse failure) while not being
    an English rendering — a distinction the divergence typer depends on."""
    by_loc = {r['location']: r['text'] for r in jb_doc['contents']}
    for loc in JB_UNTRANSLATED:
        assert by_loc[loc].strip(), loc
        # transliteration, so effectively no English function words
        words = set(by_loc[loc].lower().split())
        assert not words & {'the', 'and', 'of', 'who', 'his', 'their'}, loc


# --- five translators, ten pairs ----------------------------------------------

def test_spine_has_five_translators_and_ten_pairs():
    assert len(rv_spine_build.TRANSLATOR_ORDER) == 5
    assert 'jamison_brereton_en_2014' in rv_spine_build.TRANSLATOR_ORDER
    assert len(rv_divergence_type.TRANSLATORS) == 5
    assert len(rv_divergence_type.PAIRS) == 10
    assert len(set(rv_divergence_type.PAIR_KEYS)) == 10


def test_schema_enumerates_the_fifth_translator():
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        schema = json.load(f)
    assert 'jamison_brereton_en_2014' in schema['$defs']['translator']['enum']
    props = schema['$defs']['stanza_record']['properties']['translations']['properties']
    assert 'jamison_brereton_en_2014' in props


def test_geldner_gap_now_decides_four_pairs_deterministically():
    """The deterministic arm scales with the translator count: Geldner's four omitted
    stanzas decide every pair he is in, which is 4 of 10 rather than 3 of 6."""
    stanza = {
        'location': '10.106.5', 'mandala': 10, 'hymn': 106, 'stanza': 5,
        'translations': {k: {'status': 'present', 'text': 'x'}
                         for k in rv_divergence_type.TRANSLATORS}}
    stanza['translations']['geldner_de_1951'] = {'status': 'absent_from_source', 'text': None}
    det = rv_divergence_type.deterministic_pairs(stanza)
    assert len(det) == 4
    assert all('geldner' in k for k in det)


def test_jb_prior_is_the_highest_in_the_weights_file():
    """H1910: J–B is the current scholarly standard in English, so its prior sits above
    every other row — and the file must say why the OCR provenance does not lower it."""
    with open(TM_WEIGHTS, encoding='utf-8') as f:
        weights = json.load(f)
    by_work = weights['by_work']
    jb = by_work['rigveda-jamison-brereton-en-2014']
    assert jb == max(by_work.values())
    assert jb > by_work['rigveda-griffith-en-1896']
    assert 'OCR' in weights['_h1910_jb_comment']


# --- Renou: a witness, and never a column -------------------------------------

def test_renou_is_in_the_chronology_but_not_among_the_translators():
    """The load-bearing asymmetry of H1910. Renou belongs to the chronology — he sits
    between Geldner and Elizarenkova, and she argues with him constantly — but EVP is a
    selective commentary, so a translation column for it would be mostly
    `absent_from_source` and would corrupt `omitted_by_one`, whose meaning rests on
    absence being meaningful."""
    assert 'renou_fr_1955' in gate.WITNESS_CHRONO
    assert 'renou_fr_1955' in gate.CHRONO_ALL
    assert 'renou_fr_1955' not in gate.TRANSLATOR_CHRONO
    assert 'renou_fr_1955' not in rv_divergence_type.TRANSLATORS
    assert not any('renou' in k for k in rv_divergence_type.PAIR_KEYS)
    assert 'renou_fr_1955' not in rv_spine_build.TRANSLATOR_ORDER
    assert gate.WITNESS_CHRONO['renou_fr_1955'][0] == 1955
    year_geldner = gate.TRANSLATOR_CHRONO['geldner_de_1951'][0]
    year_eliz = gate.TRANSLATOR_CHRONO['elizarenkova_ru_1989'][0]
    assert year_geldner < 1955 < year_eliz


def test_renou_witness_records_have_no_translation_shape(renou_witness_records):
    assert renou_witness_records
    for rec in renou_witness_records[:200]:
        assert 'translations' not in rec and 'status' not in rec and 'text' not in rec
        assert rec['witness'] == 'renou_fr_1955'
        assert rec['mention_count'] >= 1
        assert rec['quoted_count'] <= rec['mention_count']
        assert rec['has_quote'] == bool(rec['quotes_fr'])


def test_renou_witness_loci_are_all_on_the_spine(renou_witness_records, stanza_records):
    spine = {r['location'] for r in stanza_records}
    off = [r['location'] for r in renou_witness_records if r['location'] not in spine]
    assert off == [], off[:10]


def test_renou_witness_mentions_reconcile_with_the_committed_index(renou_witness_records,
                                                                  renou_records):
    """Every mention is accounted for: resolved onto a locus, or explicitly unresolved.
    Nothing is silently dropped, and nothing is invented."""
    resolved = sum(r['mention_count'] for r in renou_witness_records)
    unresolved = sum(1 for r in renou_records if r['locus_unresolved'])
    assert resolved + unresolved == RENOU_TOTAL == len(renou_records)


def test_renou_witness_selftest_passes():
    assert evp.selftest() == 0


def test_gate_sheet_asymmetry_note_was_rederived_not_kept():
    """H1908's note said the only English witness was Griffith because R4 excluded J–B as
    in-copyright. R4 is lifted and J–B is a full column, so that claim is now false and
    must not survive anywhere in the builder."""
    src = open(gate.__file__, encoding='utf-8').read()
    assert 'LATEST_EN' not in src
    assert 'Единственный английский свидетель' not in src
    assert 'jamison_brereton_en_2014' in src
    assert set(gate.EN_TRANSLATORS) == {'griffith_en_1896', 'jamison_brereton_en_2014'}
