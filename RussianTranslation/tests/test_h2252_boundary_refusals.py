"""H2252 — the two fail-closed boundaries, pinned as *refusals before mutation*.

H2173 shipped the boundary values themselves (G5: an unaccountable result row
bills as a failure instead of vanishing; G8: promotion compares
``execution_route`` against ``execution_contract.HEADLESS_ROUTE`` rather than
merely proving it is a non-blank string) and pinned them in
``pilot/window_selftest.py``. Those probes assert the *verdict*.

What no probe asserted is the property an operator actually depends on: that the
refusal happens **before any state is touched**. A future refactor that moved the
journal write, the store backup, or the claim above the validation loop would keep
every existing assertion green while leaving a foreign-route artifact able to
mutate the canonical store on its way to being rejected. These tests pin the
ordering, and the G5 half pins the evidence the H2173 stamp was missing — the
source path, without which "row 4 was unaccountable" names no file to open.

Scratch stores only; nothing here touches canonical data, and no paid call is made.

Run: `pytest tests/test_h2252_boundary_refusals.py` (working dir RussianTranslation).
"""
import json
import os
import sys

import pytest

_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
sys.path.insert(0, _SRC)
sys.path.insert(0, os.path.join(_SRC, 'pilot'))

import execution_contract  # noqa: E402
import promote_final_cards as pfc  # noqa: E402
import workflow_payload as wp  # noqa: E402


# --- G5: an unaccountable row is a located failure ---------------------------

def _write_payload(tmp_path, results):
    path = tmp_path / 'wf.json'
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump({'meta': {'root': 'h2252'}, 'results': results}, fh)
    return str(path)


def test_malformed_row_names_its_source_path_and_index(tmp_path):
    path = _write_payload(tmp_path, [
        {'key': 'good', 'card': {'senses': [1]}},
        {'card': {'senses': [1]}},   # billed, attributable to no headword
        'not-a-dict',
    ])
    _payload, _meta, results, keys, nulls = wp.workflow_payload(path)

    stamped = [r for r in results if isinstance(r, dict) and r.get('malformed_result_row')]
    assert len(stamped) == 2
    for row in stamped:
        assert row['malformed_row_source'] == path
        assert path in row['error']['message']
        assert row['malformed_row_index'] in (1, 2)
        assert ('row %d' % row['malformed_row_index']) in row['error']['message']
    # The accounting property H2173 established still holds alongside the new field.
    assert len(keys) == 3 and len(nulls) == 2
    assert 'good' not in nulls


def test_wellformed_rows_carry_no_source_stamp(tmp_path):
    path = _write_payload(tmp_path, [{'key': 'good', 'card': {'senses': [1]}}])
    _payload, _meta, results, keys, nulls = wp.workflow_payload(path)
    assert keys == ['good'] and nulls == []
    assert 'malformed_row_source' not in results[0]


# --- G8: a foreign route dies before the store, journal or TM move ------------

def _v2_entry(route, subkey):
    """A promotion entry that is manifest-v2 SHAPED in every other respect, so the
    route is the only reason it can be refused."""
    return {
        'card': {'senses': [{'sense_tag': '1', 'ru': 'тест'}]},
        'meta': {
            'execution_manifest_schema': 'pwg.headless_execution_manifest.v2',
            'root': 'h2252',
            'execution': {
                'profile_slot': 'c4',
                'config_dir_fingerprint': 'abc',
                'execution_route': route,
                'executor_lane': 'headless',
                'validation_method': 'schema',
                'model_identifier': 'claude-sonnet-5',
            },
            'selected_keys': [subkey],
            'input_hashes': {subkey: {'raw_sha256': 'a' * 64, 'portrait_sha256': 'b' * 64}},
            'generator': 'headless_worker',
            'schema_version': 'v2',
            'generated_at': '2026-08-06T00:00:00Z',
            'provenance_classes': {subkey: 'real'},
        },
    }


@pytest.mark.parametrize('route', [
    'workflow',
    'max-workflow',
    execution_contract.HEADLESS_ROUTE.upper(),
    execution_contract.HEADLESS_ROUTE + ' ',
])
def test_foreign_route_is_refused_by_the_promotion_contract(route):
    subkey = 'p_a~~h5_00_pwg00'
    with pytest.raises(pfc.PromotionContractError) as exc:
        pfc.validate_promotion_entry(subkey, _v2_entry(route, subkey))
    assert 'execution_route' in str(exc.value)


def test_batch_promotion_refuses_before_touching_store_or_journal(tmp_path):
    """The ordering pin. `batch_promote` must validate every lease before it opens
    a claim, copies a backup, appends to the journal, or replaces the store — so a
    foreign-route bundle leaves the store byte-identical and the journal absent."""
    store = tmp_path / 'store.jsonl'
    subkey = 'p_a~~h5_00_pwg00'
    store.write_text(json.dumps({'subcard': subkey, 'ru': 'существующая строка'},
                                ensure_ascii=False) + '\n', encoding='utf-8')
    before = store.read_bytes()

    out_dir = tmp_path / 'clean'
    out_dir.mkdir()
    artifact = out_dir / 'wf_output_h2252.json'
    entry = _v2_entry('max-workflow', subkey)
    with open(artifact, 'w', encoding='utf-8') as fh:
        json.dump({'meta': entry['meta'],
                   'results': [{'key': subkey, 'card': entry['card']}]}, fh)

    journal = tmp_path / 'promotion_journal.jsonl'
    with pytest.raises(pfc.PromotionContractError) as exc:
        pfc.batch_promote(
            [{'lease_id': 'L1', 'glob': str(out_dir / 'wf_output_*.json'),
              'expected_subcards': [subkey]}],
            str(store), 'machine_pending', 'claude-sonnet-5',
            journal_path=str(journal), promotion_id='h2252-probe')

    assert 'execution_route' in str(exc.value)
    assert store.read_bytes() == before, 'a refused bundle must not touch the store'
    assert not journal.exists(), 'a refused bundle must not journal a promotion'
    assert sorted(p.name for p in tmp_path.glob('store.jsonl*')) == ['store.jsonl'], \
        'a refused bundle must not leave a backup or a .tmp behind'
