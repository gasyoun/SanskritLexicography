#!/usr/bin/env python
"""Hermetic exact-dispatch acceptance matrix for H2554."""
import copy
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, os.path.join(REPO, 'src')):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import gateway_attestation as att  # noqa: E402
import gateway_external_selftest as base  # noqa: E402
from gateway_route import canonical_json_bytes  # noqa: E402


START = '2026-08-10T02:00:00.000Z'
END = '2026-08-10T02:00:01.250Z'
DISPATCH = base.DISPATCH_ID
USAGE = {
    'input_tokens': 11, 'output_tokens': 22,
    'cache_creation_input_tokens': 3, 'cache_read_input_tokens': 4,
    'service_tier': 'standard',
}


def tool_use(ticket, dispatch_id=DISPATCH, sidechain=False,
             event_uuid='use-event', prompt=None):
    return {
        'type': 'assistant', 'uuid': event_uuid,
        'timestamp': '2026-08-10T02:00:00.300Z',
        'isSidechain': sidechain,
        'message': {
            'role': 'assistant', 'model': base.MODEL, 'usage': USAGE,
            'content': [{
                'type': 'tool_use', 'name': 'Agent', 'id': dispatch_id,
                'input': {'prompt': prompt or ticket['request']['prompt'],
                          'subagent_type': 'general-purpose'},
            }],
        },
    }


def tool_result(dispatch_id=DISPATCH, model=base.MODEL, status='completed',
                event_uuid='result-event', source_uuid='use-event', usage=USAGE,
                is_error=False):
    return {
        'type': 'user', 'uuid': event_uuid,
        'timestamp': '2026-08-10T02:00:00.900Z',
        'isSidechain': False, 'sourceToolAssistantUUID': source_uuid,
        'message': {'role': 'user', 'content': [{
            'type': 'tool_result', 'tool_use_id': dispatch_id,
            'is_error': is_error, 'content': 'omitted synthetic result',
        }]},
        'toolUseResult': {
            'agentId': 'agent-h2554', 'agentType': 'general-purpose',
            'resolvedModel': model, 'status': status, 'usage': usage,
            'content': [], 'prompt': 'omitted', 'totalDurationMs': 600,
            'totalTokens': 33, 'totalToolUseCount': 0,
        },
    }


def adjacent(model, stamp, uuid):
    return {
        'type': 'assistant', 'uuid': uuid, 'timestamp': stamp,
        'isSidechain': False,
        'message': {'role': 'assistant', 'model': model, 'usage': USAGE,
                    'content': []},
    }


def write_transcript(path, events, malformed=False):
    with open(path, 'w', encoding='utf-8') as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False) + '\n')
        if malformed:
            handle.write('{malformed\n')
    return path


def build(tmp, ticket, events, dispatch_id=DISPATCH, name='att.json',
          malformed=False):
    transcript = write_transcript(
        os.path.join(tmp, name + '.jsonl'), events, malformed=malformed)
    record = att.build_dispatch_attestation(
        transcript_path=transcript, dispatch_id=dispatch_id,
        run_id=ticket['run_id'], reservation_id=ticket['reservation_id'],
        requested_model=ticket['requested_model'],
        ticket_sha256=ticket['ticket_sha256'],
        request_prompt_sha256=(
            ticket['dispatch_binding']['request_prompt_sha256']),
        started_at=START, ended_at=END)
    out = os.path.join(tmp, name)
    with open(out, 'wb') as handle:
        handle.write(canonical_json_bytes(record))
    return record, out


def expect_attestation_error(fn, needle):
    try:
        fn()
    except att.AttestationError as exc:
        assert needle in str(exc), (needle, str(exc))
        return
    raise AssertionError('expected AttestationError: ' + needle)


def test_exact_main_and_sidechain_dispatches_bind_end_to_end():
    for sidechain in (False, True):
        with tempfile.TemporaryDirectory() as tmp:
            paths = base.fixture(tmp, run_id='scope-%s' % sidechain)
            ticket = base.prepare(paths)
            record, att_path = build(
                tmp, ticket, [tool_use(ticket, sidechain=sidechain), tool_result()])
            assert record['dispatch_id'] == DISPATCH
            assert record['is_sidechain'] is sidechain
            assert record['attestation_scope'] == 'dispatch'
            assert record['attested_model'] == base.MODEL
            env = base.record(
                paths, ticket, response=base.wrapper(ticket),
                attestation_path=att_path)
            assert env['dispatch_id'] == DISPATCH
            assert env['dispatch_attested'] is True
            assert env['attestation_scope'] == 'dispatch'
            assert env['model_matches_request'] is True


def test_adjacent_same_and_different_models_are_irrelevant():
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        events = [
            adjacent(base.MODEL, '2026-08-10T02:00:00.100Z', 'adjacent-a'),
            tool_use(ticket),
            adjacent('claude-haiku-4-5', '2026-08-10T02:00:00.500Z', 'adjacent-b'),
            tool_result(),
        ]
        record, _ = build(tmp, ticket, events)
        assert record['attested_model'] == base.MODEL
        assert record['usage_totals']['output_tokens'] == 22


def test_missing_wrong_and_duplicate_identifiers_refuse():
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        expect_attestation_error(
            lambda: build(tmp, ticket, [tool_use(ticket), tool_result()],
                          dispatch_id='toolu_01WrongIdentifier'),
            'exactly one Agent tool_use')
        expect_attestation_error(
            lambda: build(tmp, ticket, [tool_use(ticket)], name='missing.json'),
            'exactly one tool_result')
        duplicate = [tool_use(ticket), copy.deepcopy(tool_use(ticket)), tool_result()]
        expect_attestation_error(
            lambda: build(tmp, ticket, duplicate, name='duplicate.json'),
            'exactly one Agent tool_use')


def test_prompt_substitution_and_cross_ticket_replay_refuse():
    with tempfile.TemporaryDirectory() as tmp:
        first_paths = base.fixture(tmp, run_id='first', ticket_name='first.json')
        first = base.prepare(first_paths)
        expect_attestation_error(
            lambda: build(tmp, first, [
                tool_use(first, prompt='substituted prompt'), tool_result()],
                name='prompt.json'),
            'does not match ticket request')

        record, att_path = build(
            tmp, first, [tool_use(first), tool_result()], name='first-att.json')
        second_paths = base.fixture(tmp, run_id='second', ticket_name='second.json')
        second = base.prepare(second_paths)
        response = base.wrapper(second)
        base.expect_refusal(
            lambda: base.record(second_paths, second, response=response,
                                attestation_path=att_path),
            'run_id mismatch')
        assert record['ticket_sha256'] == first['ticket_sha256']


def test_incomplete_error_and_unrelated_result_refuse():
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        expect_attestation_error(
            lambda: build(tmp, ticket, [tool_use(ticket),
                                        tool_result(status='running')],
                          name='running.json'), 'not completed')
        expect_attestation_error(
            lambda: build(tmp, ticket, [tool_use(ticket),
                                        tool_result(is_error=True)],
                          name='error.json'), 'error/refusal')
        expect_attestation_error(
            lambda: build(tmp, ticket, [tool_use(ticket),
                                        tool_result(source_uuid='other')],
                          name='source.json'), 'source does not match')


def test_substituted_model_is_sealed_noncompliant():
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        substituted = 'claude-haiku-4-5'
        record, att_path = build(
            tmp, ticket, [tool_use(ticket), tool_result(model=substituted)])
        response = base.wrapper(ticket)
        response['returned_model'] = substituted
        env = base.record(paths, ticket, response=response,
                          attestation_path=att_path)
        assert record['model_matches_request'] is False
        assert env['schema_compliant'] is False
        assert env['failure_class'] == 'model_substituted'


def test_malformed_transcript_and_tampered_attestation_refuse():
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        expect_attestation_error(
            lambda: build(tmp, ticket, [tool_use(ticket), tool_result()],
                          name='malformed.json', malformed=True),
            'unparseable line')
        record, _ = build(tmp, ticket, [tool_use(ticket), tool_result()])
        record['agent_id'] = 'tampered'
        out = os.path.join(tmp, 'tampered.json')
        with open(out, 'wb') as handle:
            handle.write(canonical_json_bytes(record))
        base.expect_refusal(
            lambda: base.record(paths, ticket, response=base.wrapper(ticket),
                                attestation_path=out),
            'self-hash does not verify')


def test_legacy_h2539_remains_window_scoped_nonpromotable():
    path = os.path.join(REPO, 'pwg_ru', 'h2539', 'evidence',
                        't2_attestation.json')
    with open(path, 'r', encoding='utf-8') as handle:
        legacy = att.classify_legacy_attestation(json.load(handle))
    assert legacy['attestation_scope'] == 'legacy_window'
    assert legacy['dispatch_attested'] is False
    assert legacy['promotable'] is False


def test_unknown_usage_stays_unknown_not_zero():
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        record, att_path = build(
            tmp, ticket, [tool_use(ticket), tool_result(usage=None)])
        env = base.record(paths, ticket, response=base.wrapper(ticket),
                          attestation_path=att_path)
        assert record['usage_totals'] is None
        assert env['cost_evaluable'] is False
        assert env['observed_cost_usd'] is None


TESTS = [
    test_exact_main_and_sidechain_dispatches_bind_end_to_end,
    test_adjacent_same_and_different_models_are_irrelevant,
    test_missing_wrong_and_duplicate_identifiers_refuse,
    test_prompt_substitution_and_cross_ticket_replay_refuse,
    test_incomplete_error_and_unrelated_result_refuse,
    test_substituted_model_is_sealed_noncompliant,
    test_malformed_transcript_and_tampered_attestation_refuse,
    test_legacy_h2539_remains_window_scoped_nonpromotable,
    test_unknown_usage_stays_unknown_not_zero,
]


def selftest():
    failed = []
    for test in TESTS:
        try:
            test()
            print('  PASS: ' + test.__name__)
        except BaseException as exc:  # noqa: BLE001
            failed.append(test.__name__)
            print('  FAIL: %s -- %s: %s' % (
                test.__name__, exc.__class__.__name__, exc))
    if failed:
        print('gateway_attestation_selftest: FAILED (%d/%d): %s' % (
            len(failed), len(TESTS), ', '.join(failed)))
        return False
    print('gateway_attestation_selftest: PASS (%d/%d groups)' % (
        len(TESTS), len(TESTS)))
    return True


if __name__ == '__main__':
    sys.exit(0 if selftest() else 1)
