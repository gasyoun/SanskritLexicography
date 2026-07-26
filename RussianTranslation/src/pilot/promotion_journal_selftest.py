#!/usr/bin/env python
"""Offline/temp-store adversarial selftests for pwg.promotion_journal.v1."""
from __future__ import annotations

import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import promotion_journal as pj  # noqa: E402


def write_bytes(path: str, payload: bytes) -> bytes:
    pj.atomic_write_bytes(path, payload)
    return payload


def jsonl(rows: list[dict]) -> bytes:
    return b''.join(
        (json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n').encode('utf-8')
        for row in rows)


def make_prepared(directory: str):
    store = os.path.join(directory, 'store.jsonl')
    journal = os.path.join(directory, 'promotion.json')
    backup = os.path.join(directory, 'store.before.bak')
    clean = os.path.join(directory, 'clean.json')
    before = write_bytes(store, jsonl([{'subcard': 'old', 'ru': 'старый'}]))
    write_bytes(backup, before)
    after = jsonl([
        {'subcard': 'old', 'ru': 'новый'},
        {'subcard': 'new', 'ru': 'ряд'},
    ])
    write_bytes(clean, b'{"ok":true}\n')
    clean_fp = pj.aggregate_files([clean])
    bindings = {'lease-1': {'run_id': 'run-1', 'attempt_id': 'attempt-1'}}
    leases = {'lease-1': {
        **bindings['lease-1'],
        'clean_output': clean_fp,
        'subcards': 1,
        'subcard_keys': ['new'],
        'rows': 1,
        'rows_added': 1,
        'rows_replaced': 0,
        'store_delta': 1,
    }}
    store_record = {
        'path': pj.canonical_path(store),
        'before_sha256': pj.sha256_bytes(before),
        'before_rows': 1,
        'before_bytes': len(before),
        'expected_after_sha256': pj.sha256_bytes(after),
        'expected_after_rows': 2,
        'expected_after_bytes': len(after),
        'backup_path': pj.canonical_path(backup),
        'backup': {
            'path': pj.canonical_path(backup),
            'sha256': pj.sha256_bytes(before),
            'rows': 1,
            'bytes': len(before),
        },
    }
    report = {
        'schema': 'pwg.batch_promotion.v1',
        'promotion_id': 'promotion-1',
        'journal': pj.canonical_path(journal),
        'journal_phase': 'store_committed',
        'model_identifier': 'claude-sonnet-5',
        'review_status': 'ai_translated',
        'clean_output_sha256': clean_fp['sha256'],
        'store_sha256': pj.sha256_bytes(after),
        'store_rows_before': 1,
        'store_rows_after': 2,
        'leases': leases,
    }
    kwargs = {
        'promotion_id': 'promotion-1',
        'lease_ids': ['lease-1'],
        'run_ids': {'lease-1': 'run-1'},
        'bindings': bindings,
        'model_identifier': 'claude-sonnet-5',
        'review_status': 'ai_translated',
        'clean_output': {
            **clean_fp, 'subcards': ['new'], 'subcard_count': 1,
            'card_count': 1, 'sense_rows': 1,
        },
        'store': store_record,
        'leases': leases,
        'report': report,
    }
    pj.prepare(journal, **kwargs)
    return store, journal, before, after, kwargs


def canonical_coordinator_projection(
    journal_path: str,
    artifact_dir: str,
) -> tuple[bytes, list[dict]]:
    journal = pj.load(journal_path)
    lease_id = journal['lease_ids'][0]
    metrics = journal['leases'][lease_id]
    clean_file = metrics['clean_output']['files'][0]
    timestamp = journal['artifact_timestamp']
    journal_absolute = os.path.abspath(journal_path)
    outcome = 'promoted'
    state = {
        'schema': pj.COORDINATOR_STATE_SCHEMA,
        'updated_at': timestamp,
        'leases': [{
            'id': lease_id,
            'kind': 'nominal',
            'target': 'nominal:new',
            'state': outcome,
            'artifact_dir': artifact_dir,
            'clean_count': metrics['subcards'],
            'clean_output_sha256': clean_file['sha256'],
            'run_attempts': [{
                'run_id': journal['bindings'][lease_id]['run_id'],
                'run_operation_id': journal['bindings'][lease_id]['attempt_id'],
            }],
            'promoted_at': timestamp,
            'promotion_id': journal['promotion_id'],
            'promotion_journal': journal_absolute,
            'model_version': journal['model_identifier'],
            'store_before': journal['report']['store_rows_before'],
            'store_after': journal['report']['store_rows_after'],
            'store_delta': metrics['store_delta'],
            'bundle_store_delta': (
                journal['report']['store_rows_after']
                - journal['report']['store_rows_before']),
            'promoted_subcards': metrics['subcards'],
            'promoted_rows': metrics['rows'],
            'rows_added': metrics['rows_added'],
            'rows_replaced': metrics['rows_replaced'],
        }],
        'last_promotion': {
            'promotion_id': journal['promotion_id'],
            'journal': journal_absolute,
            'lease_outcomes': {lease_id: outcome},
            'model_identifier': journal['model_identifier'],
            'store_sha256': journal['store']['expected_after_sha256'],
            'committed_at': timestamp,
        },
    }
    event = {
        'schema': pj.PROMOTION_REGISTRY_SCHEMA,
        'ts': timestamp,
        'lease_id': lease_id,
        'event': 'promoted',
        'kind': 'nominal',
        'target': 'nominal:new',
        'state': outcome,
        'artifact_dir': artifact_dir,
        'data': {
            'glob': clean_file['path'],
            'journal': journal_absolute,
            'store_before': journal['report']['store_rows_before'],
            'store_after': journal['report']['store_rows_after'],
            'store_delta': metrics['store_delta'],
            'bundle_store_delta': (
                journal['report']['store_rows_after']
                - journal['report']['store_rows_before']),
            'rows_added': metrics['rows_added'],
            'rows_replaced': metrics['rows_replaced'],
            'batch_subcards': metrics['subcards'],
            'batch_rows': metrics['rows'],
            'promotion_id': journal['promotion_id'],
        },
    }
    return pj.stable_json_bytes(state), [event]


def test_prepared_fault_retry_and_immutable_intent() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store, journal, before, _after, kwargs = make_prepared(tmp)
        os.unlink(journal)

        def die(point):
            if point == 'prepared':
                raise RuntimeError('prepared death')

        try:
            pj.prepare(journal, fault_hook=die, **kwargs)
            raise AssertionError('prepared hook did not fire')
        except RuntimeError as exc:
            assert str(exc) == 'prepared death', exc
        assert os.path.isfile(journal)
        assert open(store, 'rb').read() == before
        pj.prepare(journal, **kwargs)
        assert len(pj.load(journal)['history']) == 1

        mutations = [
            ('promotion id', {'promotion_id': 'other'}),
            ('review status', {'review_status': 'approved'}),
            ('store path', {'store': {
                **kwargs['store'], 'path': pj.canonical_path(os.path.join(tmp, 'other'))}}),
            ('binding', {'bindings': {
                'lease-1': {'run_id': 'run-X', 'attempt_id': 'attempt-1'}}}),
            ('clean hash', {'clean_output': {
                **kwargs['clean_output'], 'sha256': '0' * 64}}),
            ('subcards', {'leases': {'lease-1': {
                **kwargs['leases']['lease-1'], 'subcard_keys': ['changed']}}}),
        ]
        for label, patch in mutations:
            changed = dict(kwargs)
            changed.update(patch)
            try:
                pj.prepare(journal, **changed)
                raise AssertionError('%s retry mismatch was accepted' % label)
            except pj.JournalError:
                pass


def test_before_after_unrelated_and_idempotence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store, journal, _before, after, _kwargs = make_prepared(tmp)
        assert pj.reconcile(journal)['action'] == 'retry_store_replace'
        write_bytes(store, after)
        assert pj.reconcile(journal)['action'] == 'adopt_store_commit'
        assert pj.reconcile(journal)['action'] == 'already_store_committed'
    with tempfile.TemporaryDirectory() as tmp:
        store, journal, _before, _after, _kwargs = make_prepared(tmp)
        write_bytes(store, jsonl([{'subcard': 'intruder'}]))
        try:
            pj.reconcile(journal)
            raise AssertionError('unrelated store hash was accepted')
        except pj.UnrelatedStoreError:
            pass


def test_derived_coordinator_adoption_and_final_faults() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_RU_STORE'] = os.path.join(tmp, 'env-store.jsonl')
        os.environ['PWG_RU_TM_DIR'] = tmp
        store, journal, _before, after, _kwargs = make_prepared(tmp)
        write_bytes(store, after)
        pj.mark_store_committed(journal)
        import translation_memory as tm
        card = os.path.join(tmp, 'card.tm.json')
        frag = os.path.join(tmp, 'frag.tm.jsonl')
        deny = os.path.join(tmp, 'deny.jsonl')
        write_bytes(deny, b'')
        tm.build(store, 'ru', out=card, journal_path=journal)
        tm.build_frags(
            [pj.load(journal)['clean_output']['files'][0]['path']],
            'ru', out=frag,
            journal_path=journal)
        pj.record_derived_observation(
            journal, 'denylist', artifact_path=deny, error='synthetic retry')
        pj.record_derived_observation(
            journal, 'denylist', artifact_path=deny, error=None)
        observed_derived = pj.load(journal)['derived']
        assert not observed_derived['errors']
        assert 'denylist: synthetic retry' in observed_derived['error_history']
        assert len(observed_derived['observations']) == 4

        def die_derived(point):
            if point == 'derived':
                raise RuntimeError('derived death')

        try:
            pj.mark_derived_validated(
                journal, denylist_path=deny, card_tm_path=card,
                fragment_tm_path=frag, fault_hook=die_derived)
            raise AssertionError('derived hook did not fire')
        except RuntimeError as exc:
            assert str(exc) == 'derived death', exc
        assert pj.load(journal)['phase'] == 'derived_validated'

        original_card = open(card, 'rb').read()
        write_bytes(card, b'{}\n')
        try:
            pj.verify_sealed_artifacts(journal)
            raise AssertionError('changed sealed card TM was accepted')
        except pj.JournalError:
            pass
        write_bytes(card, original_card)

        original_store = open(store, 'rb').read()
        write_bytes(store, b'{"unrelated":"store"}\n')
        registry = os.path.join(tmp, 'registry.jsonl')
        registry_events = [{
            'schema': 'pwg.sla_coordinator.artifact.v1',
            'ts': '2026-07-25T00:00:00Z',
            'lease_id': 'lease-1',
            'event': 'promoted',
            'kind': 'nominal',
            'target': 'nominal:new',
            'state': 'promoted',
            'artifact_dir': tmp,
            'data': {'promotion_id': 'promotion-1'},
        }]
        try:
            pj.prepare_coordinator_commit(
                journal,
                state_path=os.path.join(tmp, 'not-created.json'),
                expected_state_bytes=b'{}\n',
                lease_outcomes={'lease-1': 'promoted'},
                promotion_marker='promotion-1',
                registry_path=registry,
                registry_events=registry_events)
            raise AssertionError('changed canonical store reached coordinator commit')
        except pj.UnrelatedStoreError:
            pass
        write_bytes(store, original_store)

        state = os.path.join(tmp, 'coordinator.json')
        write_bytes(state, b'{"phase":"before"}\n')
        expected_state, canonical_events = canonical_coordinator_projection(
            journal, tmp)
        try:
            pj.prepare_coordinator_commit(
                journal, state_path=state,
                expected_state_bytes=expected_state,
                lease_outcomes={'lease-1': 'promoted'},
                promotion_marker='promotion-1',
                registry_path=registry,
                registry_events=registry_events)
            raise AssertionError('minimal public registry event was accepted')
        except pj.JournalError as exc:
            assert 'canonical promotion projection' in str(exc), exc
        inconsistent_events = json.loads(json.dumps(canonical_events))
        inconsistent_events[0]['data']['rows_added'] += 1
        try:
            pj.prepare_coordinator_commit(
                journal, state_path=state,
                expected_state_bytes=expected_state,
                lease_outcomes={'lease-1': 'promoted'},
                promotion_marker='promotion-1',
                registry_path=registry,
                registry_events=inconsistent_events)
            raise AssertionError('inconsistent public registry event was accepted')
        except pj.JournalError as exc:
            assert 'canonical promotion projection' in str(exc), exc
        pj.prepare_coordinator_commit(
            journal, state_path=state, expected_state_bytes=expected_state,
            lease_outcomes={'lease-1': 'promoted'},
            promotion_marker='promotion-1',
            registry_path=registry,
            registry_events=canonical_events)
        before_state = b'{"phase":"before"}\n'
        write_bytes(state, b'{"phase":"unrelated"}\n')
        try:
            pj.reconcile_coordinator(journal)
            raise AssertionError('unrelated coordinator state was accepted')
        except pj.JournalError:
            pass
        write_bytes(state, before_state)

        def die_state(point):
            if point == 'coordinator_state_saved':
                raise RuntimeError('state-save death')

        try:
            pj.commit_coordinator_state(journal, expected_state, fault_hook=die_state)
            raise AssertionError('coordinator state-save hook did not fire')
        except RuntimeError:
            pass
        assert pj.load(journal)['phase'] == 'derived_validated'
        assert pj.reconcile_coordinator(
            journal, adopt_after=False)['action'] == 'adopt_coordinator_commit'
        def die_adoption(point):
            if point == 'coordinator_adopted':
                raise RuntimeError('coordinator adoption death')
        try:
            pj.commit_coordinator_state(
                journal, expected_state, fault_hook=die_adoption)
            raise AssertionError('coordinator adoption hook did not fire')
        except RuntimeError as exc:
            assert 'adoption death' in str(exc)
        assert pj.load(journal)['phase'] == 'coordinator_committed'

        original_frag = open(frag, 'rb').read()
        write_bytes(frag, b'{}\n')
        try:
            pj.mark_complete(journal)
            raise AssertionError('changed sealed fragment TM was accepted')
        except pj.JournalError:
            pass
        write_bytes(frag, original_frag)
        try:
            pj.mark_complete(journal)
            raise AssertionError('missing registry projection was accepted')
        except pj.JournalError as exc:
            assert 'registry projection' in str(exc), exc
        write_bytes(registry, jsonl(canonical_events))

        def die_final(point):
            if point == 'final_journal_update':
                raise RuntimeError('final journal death')

        try:
            pj.mark_complete(journal, fault_hook=die_final)
            raise AssertionError('final-journal hook did not fire')
        except RuntimeError:
            pass
        assert pj.load(journal)['phase'] == 'complete'
        # Terminal evidence is historical: later promotions may legitimately
        # change the shared store/TMs/coordinator state.
        write_bytes(store, b'{"later":"promotion"}\n')
        write_bytes(card, b'{"later":"tm"}\n')
        write_bytes(state, b'{"later":"coordinator"}\n')
        assert pj.reconcile(journal)['action'] == 'terminal_complete'
        assert pj.mark_complete(journal)['phase'] == 'complete'


def main() -> int:
    tests = [
        test_prepared_fault_retry_and_immutable_intent,
        test_before_after_unrelated_and_idempotence,
        test_derived_coordinator_adoption_and_final_faults,
    ]
    for test in tests:
        test()
        print('ok  ', test.__name__)
    print('%d/%d passed (promotion journal adversarial)' % (len(tests), len(tests)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
