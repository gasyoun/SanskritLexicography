#!/usr/bin/env python
"""Hermetic Message Batches compiler/lifecycle regression matrix."""
import copy
import json
import os
import tempfile

from call_reservation import CallLimitReached, CallReservationLedger
import pwg_batch as batch


HERE = os.path.dirname(os.path.abspath(__file__))
BASE_MANIFEST = os.path.join(HERE, 'h1209_slice3.manifest.json')


def fixture(tmp, *, model='claude-sonnet-5'):
    with open(BASE_MANIFEST, encoding='utf-8') as handle:
        value = json.load(handle)
    value['model'] = model
    value['runtime']['max_output_tokens'] = 8192
    path = os.path.join(tmp, 'manifest.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=1)
        handle.write('\n')
    return path, value


def save_plan(tmp, **kwargs):
    manifest, _ = fixture(tmp, **kwargs)
    plan = batch.compile_plan(manifest)
    path = os.path.join(tmp, 'plan.json')
    batch.atomic_json(path, plan)
    return path, plan


def card(key):
    return {
        'key1': key, 'iast': '', 'notes': '',
        'records': [{
            'h': '', 'grammar': '',
            'senses': [{'tag': '1', 'german': 'Quelle', 'russian': 'перевод'}],
        }],
    }


def message(model, keys, usage=True):
    value = {
        'model': model,
        'content': [{
            'type': 'tool_use', 'name': batch.TOOL_NAME,
            'input': {'cards': [card(key) for key in keys]},
        }],
    }
    if usage:
        value['usage'] = {
            'input_tokens': 10, 'output_tokens': 5,
            'cache_creation_input_tokens': 2, 'cache_read_input_tokens': 3,
        }
    return value


class FakeTransport:
    def __init__(self, rows=None, create_error=None, create_response=None):
        self.rows = rows or []
        self.create_error = create_error
        self.create_response = create_response or {'id': 'msgbatch_test'}
        self.calls = []

    def check(self, model):
        self.calls.append(('check', model))
        return {'authenticated': True, 'model_available': True, 'returned_model': model}

    def create(self, requests):
        self.calls.append(('create', requests))
        if self.create_error:
            raise self.create_error
        return self.create_response

    def retrieve(self, batch_id):
        self.calls.append(('retrieve', batch_id))
        return {'id': batch_id, 'processing_status': 'ended'}

    def results(self, batch_id):
        self.calls.append(('results', batch_id))
        return list(self.rows)


def test_prepare_is_offline_deterministic_and_byte_exact():
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path, manifest = fixture(tmp)
        one = batch.compile_plan(manifest_path)
        two = batch.compile_plan(manifest_path)
        assert one == two and one['plan_sha256'] == two['plan_sha256']
        assert one['request_count'] == len(manifest['batches'])
        ids = [row['custom_id'] for row in one['requests']]
        assert len(ids) == len(set(ids)) and all(len(value) <= 64 for value in ids)
        for request in one['requests']:
            blocks = request['params']['messages'][0]['content']
            assert blocks[0]['cache_control'] == batch.CACHE_CONTROL
            assert 'cache_control' not in blocks[1]
            assert request['params']['model'] == manifest['model']
            assert request['params']['max_tokens'] == 8192
            assert request['params']['tool_choice'] == {
                'type': 'tool', 'name': batch.TOOL_NAME}
        path = os.path.join(tmp, 'plan.json')
        batch.atomic_json(path, one)
        assert batch.offline_check(path)['network_calls'] == 0


def test_manifest_binding_and_limits():
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path, value = fixture(tmp, model='claude-opus-5')
        plan = batch.compile_plan(manifest_path)
        assert plan['model'] == 'claude-opus-5'
        value['model'] = 'claude-opus-5-override'
        bad = os.path.join(tmp, 'bad-model.json')
        with open(bad, 'w', encoding='utf-8') as handle:
            json.dump(value, handle)
        try:
            batch.compile_plan(bad)
            raise AssertionError('unapproved model was accepted')
        except batch.BatchRefusal:
            pass
        try:
            batch.compile_plan(manifest_path, max_requests=2)
            raise AssertionError('project request cap was ignored')
        except batch.BatchRefusal:
            pass
        too_many = copy.deepcopy(plan)
        too_many['request_body_bytes'] = batch.HARD_MAX_BYTES + 1
        too_many['plan_sha256'] = batch.canonical_hash(
            {k: v for k, v in too_many.items() if k != 'plan_sha256'})
        try:
            batch.verify_plan(too_many)
            raise AssertionError('request byte mismatch was accepted')
        except batch.BatchRefusal:
            pass


def test_credential_free_refusal_and_live_injection():
    with tempfile.TemporaryDirectory() as tmp:
        plan_path, plan = save_plan(tmp)
        fake = FakeTransport()
        assert batch.live_check(plan_path, fake)['returned_model'] == plan['model']
        assert fake.calls == [('check', plan['model'])]


def test_succeeded_model_usage_and_schema_fail_closed():
    with tempfile.TemporaryDirectory() as tmp:
        _path, plan = save_plan(tmp)
        request = plan['requests'][0]
        good = {'custom_id': request['custom_id'], 'result': {
            'type': 'succeeded',
            'message': message(plan['model'], request['work']['keys']),
        }}
        envelope = batch._result_envelope(plan, request, good)
        assert envelope['schema_compliant'] is True
        assert envelope['usage_evaluable'] is True
        assert envelope['accounting']['billing_mode'] == 'api_batch'
        substituted = copy.deepcopy(good)
        substituted['result']['message']['model'] = 'claude-opus-5'
        assert batch._result_envelope(
            plan, request, substituted)['failure_class'] == 'model_substitution'
        missing_usage = copy.deepcopy(good)
        missing_usage['result']['message'].pop('usage')
        assert batch._result_envelope(
            plan, request, missing_usage)['failure_class'] == 'unevaluable_cost'
        bad_schema = copy.deepcopy(good)
        bad_schema['result']['message']['content'][0]['input'] = {'cards': []}
        assert batch._result_envelope(
            plan, request, bad_schema)['failure_class'] == 'schema_failure'


def test_ambiguous_submit_never_retries():
    with tempfile.TemporaryDirectory() as tmp:
        plan_path, plan = save_plan(tmp)
        state = plan_path + '.state.json'
        ledger_path = plan_path + '.reservations.json'
        fake = FakeTransport(create_error=TimeoutError('lost create response'))
        try:
            batch.submit(plan_path, state_path=state, ledger_path=ledger_path,
                         transport=fake)
            raise AssertionError('ambiguous create succeeded')
        except batch.BatchRefusal as exc:
            assert 'ambiguous_submit' in str(exc)
        assert len([call for call in fake.calls if call[0] == 'create']) == 1
        book = CallReservationLedger.open_existing(ledger_path, plan['plan_sha256'])
        assert book.spent() == plan['request_count']
        try:
            batch.submit(plan_path, state_path=state, ledger_path=ledger_path,
                         transport=fake)
            raise AssertionError('ambiguous create retried')
        except batch.BatchRefusal as exc:
            assert 'automatic retry forbidden' in str(exc)
        assert len([call for call in fake.calls if call[0] == 'create']) == 1


class ExhaustedLedger:
    run_id = 'fake'

    def reserve(self, *_args, **_kwargs):
        raise CallLimitReached('test ceiling')


def test_reservation_exhaustion_precedes_transport():
    with tempfile.TemporaryDirectory() as tmp:
        plan_path, _ = save_plan(tmp)
        fake = FakeTransport()
        try:
            batch.submit(plan_path, transport=fake, ledger=ExhaustedLedger())
            raise AssertionError('reservation exhaustion was ignored')
        except batch.BatchRefusal as exc:
            assert 'reservation_exhausted' in str(exc)
        assert fake.calls == []


def test_unordered_terminals_crash_resume_and_exact_once():
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path, _ = fixture(tmp)
        seed = batch.compile_plan(manifest_path)
        work = [copy.deepcopy(seed['requests'][0]['work']) for _ in range(4)]
        plan = batch.compile_plan(manifest_path, work_items=work)
        plan_path = os.path.join(tmp, 'plan.json')
        batch.atomic_json(plan_path, plan)
        rows = []
        types = ('succeeded', 'errored', 'canceled', 'expired')
        for request, terminal in zip(plan['requests'], types):
            result = {'type': terminal}
            if terminal == 'succeeded':
                result['message'] = message(plan['model'], request['work']['keys'])
            else:
                result['error'] = {'type': terminal}
            rows.append({'custom_id': request['custom_id'], 'result': result})
        fake = FakeTransport(rows=list(reversed(rows)))
        state = batch.submit(plan_path, transport=fake)
        assert state['status'] == 'submitted'
        assert batch.submit(plan_path, transport=fake)['provider_batch_id'] == 'msgbatch_test'
        assert len([call for call in fake.calls if call[0] == 'create']) == 1
        fetched = batch.fetch(plan_path, transport=fake,
                              next_plan_path=os.path.join(tmp, 'heal.json'))
        assert [row['terminal_type'] for row in fetched['results']] == list(types)
        book = CallReservationLedger.open_existing(
            plan_path + '.reservations.json', plan['plan_sha256'])
        assert book.usage()['finalized_calls'] == 4
        assert book.usage()['pending_calls'] == 0
        assert all(row['promotable'] is False for row in fetched['results'])
        for row in fetched['results'][1:]:
            assert row['accounting']['observed_cash_usd'] == 0
        heal = batch.verify_plan(batch.read_json(os.path.join(tmp, 'heal.json')))
        assert heal['wave'] == 1 and heal['request_count'] == 3
        replay = batch.fetch(plan_path, transport=fake,
                             next_plan_path=os.path.join(tmp, 'heal.json'))
        assert replay['state']['result_hashes'] == fetched['state']['result_hashes']
        assert book.usage()['finalized_calls'] == 4


TESTS = (
    test_prepare_is_offline_deterministic_and_byte_exact,
    test_manifest_binding_and_limits,
    test_credential_free_refusal_and_live_injection,
    test_succeeded_model_usage_and_schema_fail_closed,
    test_ambiguous_submit_never_retries,
    test_reservation_exhaustion_precedes_transport,
    test_unordered_terminals_crash_resume_and_exact_once,
)


def main():
    for test in TESTS:
        test()
        print('  PASS:', test.__name__)
    print('pwg_batch_selftest: PASS (%d/%d groups)' % (len(TESTS), len(TESTS)))


if __name__ == '__main__':
    main()
