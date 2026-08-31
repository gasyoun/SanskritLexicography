"""Schema and Track A CLI tests for the PWG TM canonical v1 layer (H2683)."""
import json
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import pwg_tm_canonical as C  # noqa: E402
import pwg_tm_fragmentize as F  # noqa: E402
import pwg_tm_migrate_v1 as M  # noqa: E402
import pwg_tm_priority as P  # noqa: E402

FIX = os.path.join(ROOT, 'schemas', 'fixtures',
                   'pwg_tm_canonical.publication.fixture.jsonl')


def _pubs():
    return C.read_jsonl(FIX)


def test_schema_file_declares_six_classes():
    schema = C.load_schema()
    classes = schema['$defs']['fragment_class']['enum']
    assert classes == list(C.FRAGMENT_CLASSES)
    assert len(classes) == 6


def test_migrate_fixture_is_lossless_and_stable():
    pubs = _pubs()
    wrapped = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    receipt = C.reconcile(pubs, wrapped)
    assert receipt['ok']
    assert receipt['in_count'] == receipt['out_count'] == 2
    assert receipt['lost_field_records'] == 0
    assert wrapped[0]['source_publication'] == pubs[0]
    again = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    assert [r['record_id'] for r in again] == [r['record_id'] for r in wrapped]
    assert wrapped[0]['record_id'].startswith('pwg.tm.v1:')
    assert wrapped[0]['tm_record_id'] == pubs[0]['tm_record_id']


def test_single_sense_is_mapped_multi_is_unresolved():
    pubs = _pubs()
    card, frag = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    assert card['sense_alignment'] == 'mapped'
    assert frag['sense_alignment'] == 'unresolved'
    assert 'unresolved' in frag['sense_id']


def test_jsonschema_accepts_migrated_and_fragment_rows():
    jsonschema = pytest.importorskip('jsonschema')
    pubs = _pubs()
    parents = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    frags = F.fragmentize_rows(parents)
    schema = C.load_schema()
    for row in parents + frags:
        jsonschema.validate(row, schema)
        ok, why = C.validate_canonical(row)
        assert ok, why


def test_fragmentize_emits_all_six_classes():
    pubs = _pubs()
    parents = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    frags = F.fragmentize_rows(parents)
    report = F.inventory(frags, parents)
    assert report['ok']
    assert report['orphan_count'] == 0
    assert report['duplicate_fragment_ids'] == 0
    for klass in C.FRAGMENT_CLASSES:
        assert report['by_class'][klass] >= 1, klass
    parents_ids = {p['record_id'] for p in parents}
    assert all(f['parent_record_id'] in parents_ids for f in frags)


def test_fragment_ids_are_deterministic():
    pubs = _pubs()
    parents = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    a = [f['fragment_id'] for f in F.fragmentize_rows(parents)]
    b = [f['fragment_id'] for f in F.fragmentize_rows(parents)]
    assert a == b


def test_migrate_verify_fixture_path():
    ok, msg = M.verify_fixture()
    assert ok, msg


def test_is_interrupted_gloss_rejoined_before_fragmenting():
    """H3753 (GAPS §18) RED-pin: viSveSa 2 — `{%die%} <is>Viśve
    Devaḥ</is> {%zur Gottheit habend%}` is ONE gloss. Before the fix
    GLOSS_RE matched the two halves independently, emitting a bare German
    article `{%die%}` as a standalone, untranslatable definition_gloss
    fragment. The rejoin must merge them into a single fragment that still
    carries the <is> span, and must never emit `{%die%}` alone."""
    german = '{%die%} <is>Viśve Devaḥ</is> {%zur Gottheit habend%}'
    russian = '{%%}' + german[len('{%die%} '):]  # untranslated placeholder, same shape
    rows = F.extract_from_sense(
        {'record_id': 'r1', 'entry_id': 'pwg.entry:viSveSa', 'lang': 'ru'},
        '2', german, russian, '', 1, mapped=True)
    glosses = [r for r in rows if r['fragment_class'] == 'definition_gloss']
    assert len(glosses) == 1, glosses
    assert glosses[0]['source_string'] == (
        '{%die <is>Viśve Devaḥ</is> zur Gottheit habend%}')
    assert glosses[0]['source_string'] != '{%die%}'
    assert not any(g['source_string'].strip() == '{%die%}' for g in glosses)


def test_rejoin_is_interrupted_glosses_chain_and_noop():
    assert F._rejoin_is_interrupted_glosses('') == ''
    plain = '{%no interruption here%}'
    assert F._rejoin_is_interrupted_glosses(plain) == plain
    chain = '{%a%} <is>x</is> {%b%} <is>y</is> {%c%}'
    assert F._rejoin_is_interrupted_glosses(chain) == '{%a <is>x</is> b <is>y</is> c%}'


def test_priority_limit_is_unique_and_reproducible():
    if not os.path.exists(P.HEADWORD_INDEX) or not os.path.exists(P.FREQ_ORDER):
        pytest.skip('frequency/index assets absent')
    chosen, excluded, manifest = P.build(25, out_dir=None)
    keys = [r['k1'] for r in chosen]
    assert len(keys) == 25
    assert len(set(keys)) == 25
    assert [r['rank'] for r in chosen] == list(range(1, 26))
    again, _ex, man2 = P.build(25, out_dir=None)
    assert [r['k1'] for r in again] == keys
    assert man2['manifest_sha256'] == manifest['manifest_sha256']
    assert excluded
    assert manifest['universe_index_rows'] == P.EXPECTED_INDEX_ROWS
