"""H3714 Wave 1 — recursive full-row validation (V7, V8).

A defect in the *middle* of a file, nested several levels deep, must be found
and located; the validator must never mutate what it reads; and when schema
validation is required but unavailable it must fail closed.
"""
import json
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from pwg_pipeline import validation  # noqa: E402
from pwg_pipeline.evidence import sha256_file  # noqa: E402


def clean_row(index):
    return {
        'tm_record_id': 'row-%d' % index,
        'target_string': 'огонь',
        'generation': {'route_id': 'xai-tm', 'pipeline_version': 'v1'},
        'nested': {'deep': [{'note': 'fine'}]},
    }


def write_jsonl(path, rows):
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write('\n')
    return str(path)


def test_a_middle_row_placeholder_at_depth_is_found(tmp_path):
    rows = [clean_row(i) for i in range(5)]
    rows[2]['nested']['deep'][0]['note'] = 'residue {T3} left behind'
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    report = validation.validate_jsonl(path)
    assert report['rows'] == 5
    assert report['defective_rows'] == 1
    assert report['by_code'][validation.UNRESOLVED_PLACEHOLDER] == 1
    finding = report['rows_detail'][0]['findings'][0]
    assert finding['path'] == '$[2].nested.deep[0].note'
    assert finding['token'] == '{T3}'
    assert report['rows_detail'][0]['identity'] == 'row-2'


def test_every_occurrence_in_a_row_is_counted(tmp_path):
    rows = [clean_row(0)]
    rows[0]['target_string'] = '{T1} и {T2}'
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    report = validation.validate_jsonl(path)
    assert report['by_code'][validation.UNRESOLVED_PLACEHOLDER] == 2
    assert report['defective_rows'] == 1


def test_registered_sentinels_are_defects_at_any_depth(tmp_path):
    rows = [clean_row(0)]
    rows[0]['nested']['deep'][0]['note'] = '__TODO__'
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    report = validation.validate_jsonl(path)
    assert report['by_code'][validation.REGISTERED_SENTINEL] == 1


def test_missing_provenance_is_a_defect(tmp_path):
    rows = [{'tm_record_id': 'x', 'target_string': 'огонь'}]
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    report = validation.validate_jsonl(path)
    assert validation.MISSING_PROVENANCE in report['by_code']
    relaxed = validation.validate_jsonl(path, require_provenance=False)
    assert validation.is_clean(relaxed)


def test_duplicate_identity_is_reported(tmp_path):
    rows = [clean_row(0), clean_row(0)]
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    report = validation.validate_jsonl(path)
    assert report['by_code'][validation.DUPLICATE_IDENTITY] == 1


def test_broken_hash_lineage_is_reported(tmp_path):
    rows = [clean_row(0)]
    rows[0]['source_hash'] = 'not-a-digest'
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    report = validation.validate_jsonl(path)
    assert report['by_code'][validation.BROKEN_HASH_LINEAGE] == 1


def test_route_model_mismatch_is_reported(tmp_path):
    rows = [clean_row(0)]
    rows[0]['generation'].update({'requested_model': 'grok-4.6',
                                  'served_model': 'grok-mini'})
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    report = validation.validate_jsonl(path)
    assert report['by_code'][validation.ROUTE_MODEL_MISMATCH] == 1


def test_validation_never_mutates_the_file(tmp_path):
    """V8 — the canonical digest is unchanged by a read-only pass."""
    rows = [clean_row(i) for i in range(3)]
    rows[1]['target_string'] = '{T9}'
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    before = sha256_file(path)
    report = validation.validate_jsonl(path)
    assert report['read_only'] is True
    assert report['sha256'] == before
    assert sha256_file(path) == before


def test_fence_reports_without_proposing_a_repair(tmp_path):
    rows = [clean_row(i) for i in range(4)]
    rows[1]['target_string'] = '{T1}'
    rows[3]['target_string'] = '{T2}'
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    fence = validation.fence_report(validation.validate_jsonl(path))
    assert fence['mutation'] == 'none'
    assert fence['fenced_rows'] == 2
    assert fence['identities'] == ['row-1', 'row-3']
    assert sha256_file(path) == fence['sha256']


def test_schema_validation_fails_closed_when_jsonschema_is_absent(tmp_path,
                                                                 monkeypatch):
    """V7 — required schema validation must never silently downgrade."""
    path = write_jsonl(tmp_path / 'store.jsonl', [clean_row(0)])
    real_import = __builtins__['__import__'] if isinstance(__builtins__, dict) \
        else __builtins__.__import__

    def refuse(name, *args, **kwargs):
        if name == 'jsonschema':
            raise ImportError('no module named jsonschema')
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr('builtins.__import__', refuse)
    with pytest.raises(validation.ValidationError):
        validation.validate_jsonl(path, require_schema=True)
    # Not requiring schema validation still works without the dependency.
    assert validation.is_clean(validation.validate_jsonl(path))


def test_walk_yields_every_node_with_a_jsonpath():
    value = {'a': [{'b': 'x'}], 'weird key': 1}
    paths = {path for path, _ in validation.walk(value)}
    assert '$' in paths
    assert '$.a' in paths
    assert '$.a[0].b' in paths
    assert "$['weird key']" in paths


def test_in_memory_row_validation_matches_the_file_pass(tmp_path):
    rows = [clean_row(0), dict(clean_row(1), target_string='{T4}')]
    path = write_jsonl(tmp_path / 'store.jsonl', rows)
    from_file = validation.validate_jsonl(path)
    in_memory = validation.validate_rows(rows)
    assert from_file['by_code'] == in_memory['by_code']
    assert from_file['defective_rows'] == in_memory['defective_rows']


def test_a_non_object_row_is_an_invalid_row(tmp_path):
    path = tmp_path / 'store.jsonl'
    path.write_text('[1, 2, 3]\n', encoding='utf-8')
    report = validation.validate_jsonl(str(path))
    assert report['by_code'][validation.INVALID_ROW] == 1
