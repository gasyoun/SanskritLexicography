#!/usr/bin/env python
"""Deterministic regression tests for the H1080 atomic store repair."""
import hashlib
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import backfill_tn_residue as repair


def write_jsonl(path, rows):
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')


def raw(path, text):
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    return repair.sha256_file(path)


def row(subcard, sha, **values):
    payload = {
        'key1': values.pop('key1', subcard.split('~~', 1)[0]),
        'subcard': subcard,
        'iast': values.pop('iast', 'x'),
        'h': values.pop('h', 'x'),
        'grammar': values.pop('grammar', ''),
        'sense_tag': values.pop('sense_tag', '1'),
        'de': values.pop('de', 'Deutsch'),
        'ru': values.pop('ru', 'русский'),
        'differentia': values.pop('differentia', ''),
        'provenance': {'input_raw_sha256': sha},
    }
    payload.update(values)
    return payload


def fixture(td):
    sources = os.path.join(td, 'sources')
    harnesses = os.path.join(td, 'harnesses')
    os.makedirs(sources)
    os.makedirs(harnesses)

    raw_key = 'raw~~h0_zz_pw'
    raw_sha = raw(os.path.join(sources, raw_key + '.raw.txt'), '{#raw#} Gloss')
    harness_key = 'harness~~h0_zz_pw'
    harness_sha = hashlib.sha256(b'historical source').hexdigest()
    meta = {'generated_at': '2026-01-01T00:00:00Z',
            'input_hashes': {harness_key: {'raw_sha256': harness_sha}}}
    with open(os.path.join(harnesses, 'attempt.js'), 'w', encoding='utf-8') as fh:
        fh.write('const PH = %s\n' % json.dumps({harness_key: ['{#harness#}']}))
        fh.write('const META = %s\n' % json.dumps(meta))

    q_rows = []
    for key in sorted(repair.QUARANTINE_SUBCARDS):
        q_path = os.path.join(sources, key + '.raw.txt')
        q_sha = raw(q_path, '{#banD#}')
        q_rows.append(row(key, q_sha, ru='{T9}', de='Deutsch'))

    rows = [
        row(raw_key, raw_sha, h='{T1}'),
        row(harness_key, harness_sha, differentia='см. {T1}'),
        row('null~~h0_zz_pw', None, key1='null', iast='nūll', h=None, grammar=None),
        *q_rows,
    ]
    store = os.path.join(td, 'store.jsonl')
    write_jsonl(store, rows)
    return store, sources, harnesses


def test_plan_and_apply():
    with tempfile.TemporaryDirectory() as td:
        store, sources, harnesses = fixture(td)
        before = repair.sha256_file(store)
        plan, repaired = repair.plan_repair(store, [sources], [harnesses])
        assert plan['stats'] == {
            'placeholder_rows': 4,
            'placeholder_repaired': 2,
            'null_headword_repaired': 1,
            'quarantined_rows': 2,
            'input_rows': 5,
            'output_rows': 3,
        }, plan['stats']
        assert len(repaired) == 3
        assert not any(repair.affected_fields(r) for r in repaired)
        assert all(r.get('h') is not None for r in repaired)
        assert next(r for r in repaired if r['key1'] == 'null')['h'] == 'nūll'

        quarantine = os.path.join(td, 'quarantine.jsonl')
        backup, after, q_sha = repair.apply_repair(
            store, repaired, plan['quarantine'], before, quarantine)
        assert repair.sha256_file(backup) == before
        assert repair.sha256_file(store) == after
        assert repair.sha256_file(quarantine) == q_sha
        assert len(repair.read_rows(quarantine)) == 2

        second, second_rows = repair.plan_repair(store, [sources], [harnesses])
        assert second['stats']['already_clean'] == 1
        assert second_rows == repair.read_rows(store)
    print('  plan/apply/quarantine/idempotence: PASS')


def test_source_hash_drift_refused():
    with tempfile.TemporaryDirectory() as td:
        store, sources, harnesses = fixture(td)
        plan, repaired = repair.plan_repair(store, [sources], [harnesses])
        before_bytes = open(store, 'rb').read()
        try:
            repair.apply_repair(store, repaired, plan['quarantine'], '0' * 64,
                                os.path.join(td, 'q.jsonl'))
        except repair.RepairRefusal as exc:
            assert 'source-hash drift' in str(exc)
        else:
            raise AssertionError('source hash drift was accepted')
        assert open(store, 'rb').read() == before_bytes
    print('  source-hash drift fail-closed: PASS')


def test_atomic_failure_preserves_previous_file():
    with tempfile.TemporaryDirectory() as td:
        target = os.path.join(td, 'artifact.json')
        with open(target, 'wb') as fh:
            fh.write(b'old')
        real_replace = repair.os.replace

        def fail_replace(_src, _dst):
            raise OSError('synthetic replace failure')

        repair.os.replace = fail_replace
        try:
            try:
                repair.atomic_write_bytes(target, b'new')
            except OSError as exc:
                assert 'synthetic' in str(exc)
            else:
                raise AssertionError('replace failure was swallowed')
        finally:
            repair.os.replace = real_replace
        assert open(target, 'rb').read() == b'old'
        leftovers = [name for name in os.listdir(td) if name.endswith('.tmp')]
        assert leftovers == [], leftovers
    print('  atomic failure preservation/cleanup: PASS')


def main():
    test_plan_and_apply()
    test_source_hash_drift_refused()
    test_atomic_failure_preserves_previous_file()
    print('backfill_tn_residue selftest: PASS')


if __name__ == '__main__':
    main()
