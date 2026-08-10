#!/usr/bin/env python
"""Hermetic acceptance matrix for the H2537 served-model/usage attestation.

Offline throughout: transcripts are synthesised on disk, no transport is
invoked, and the bridge helpers are reused from
[`gateway_external_selftest.py`](gateway_external_selftest.py) so ticket/ledger
construction stays identical to the released contract.

The property under test is narrow and specific: an envelope must never claim a
model binding it did not observe.  Before H2537, ``model_matches_request`` was
the literal ``True`` and the envelope schema pinned it to ``{"const": true}``,
so a router substitution was unrecordable by construction.
"""

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
import gateway_external as ext  # noqa: E402
import gateway_external_selftest as base  # noqa: E402
from gateway_route import canonical_json_bytes, sha256_bytes  # noqa: E402


START = '2026-08-10T02:00:00.000Z'
END = '2026-08-10T02:00:01.250Z'
USAGE = {
    'input_tokens': 11,
    'output_tokens': 22,
    'cache_creation_input_tokens': 3,
    'cache_read_input_tokens': 4,
    'service_tier': 'standard',
}


def transcript(path, turns):
    """Write a synthetic harness transcript containing ``turns``."""
    with open(path, 'w', encoding='utf-8') as handle:
        for turn in turns:
            handle.write(json.dumps(turn, ensure_ascii=False) + '\n')
    return path


def turn(model=base.MODEL, stamp='2026-08-10T02:00:00.500Z', sidechain=True,
         usage=None, etype='assistant'):
    return {
        'type': etype,
        'uuid': 'u-%s-%s' % (model, stamp),
        'timestamp': stamp,
        'isSidechain': sidechain,
        'message': {
            'role': 'assistant',
            'model': model,
            'usage': USAGE if usage is None else usage,
        },
    }


def attest(tmp, ticket, turns, requested_model=None, name='att.json',
           sidechain_only=True):
    path = transcript(os.path.join(tmp, 'transcript.jsonl'), turns)
    record = att.build_attestation(
        transcript_path=path,
        started_at=START,
        ended_at=END,
        run_id=ticket['run_id'],
        reservation_id=ticket['reservation_id'],
        requested_model=requested_model or ticket['requested_model'],
        sidechain_only=sidechain_only,
    )
    out = os.path.join(tmp, name)
    with open(out, 'wb') as handle:
        handle.write(canonical_json_bytes(record))
    return record, out


def test_attested_match_is_observed_not_asserted():
    """A matching served model yields model_attested + a true, sealed match."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        record, att_path = attest(tmp, ticket, [turn()])
        assert record['attested_model'] == base.MODEL
        assert record['model_matches_request'] is True
        assert record['turns_in_window'] == 1
        assert record['usage_totals']['output_tokens'] == 22

        env = base.record(paths, ticket, response=base.wrapper(ticket, usage=USAGE),
                          attestation_path=att_path)
        assert env['model_attested'] is True
        assert env['attested_model'] == base.MODEL
        assert env['model_matches_request'] is True
        assert env['attestation_sha256'] == record['attestation_sha256']
        assert env['attested_usage_totals']['input_tokens'] == 11
        assert env['schema_compliant'] is True
        assert env['promotable'] is False
        # assert_not_promotable always raises; the *message* proves the envelope
        # was recognised as a well-formed synthetic one, not "unrecognized".
        base.expect_refusal(lambda: ext.assert_not_promotable(env),
                            'permanently non-promotable')


def test_absent_attestation_is_null_never_true():
    """Without attestation the match is unestablished — null, not True.

    This is the core integrity fix: the pre-H2537 envelope wrote True here on
    no evidence at all.
    """
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        env = base.record(paths, ticket, response=base.wrapper(ticket, usage=USAGE))
        assert env['model_attested'] is False
        assert env['model_matches_request'] is None, (
            'unattested envelope must not claim a verified model match')
        assert env['attested_model'] is None
        assert env['attestation_sha256'] is None
        assert env['attested_usage_totals'] is None
        # An unattested call is still a well-formed, sealed, compliant record.
        assert env['schema_compliant'] is True


def test_substituted_model_is_sealed_not_silently_refused():
    """A router substitution is recorded truthfully and marked non-compliant."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        substituted = 'claude-haiku-4-5'
        record, att_path = attest(tmp, ticket, [turn(model=substituted)])
        assert record['attested_model'] == substituted
        assert record['model_matches_request'] is False

        response = base.wrapper(ticket, usage=USAGE)
        response['returned_model'] = substituted
        env = base.record(paths, ticket, response=response,
                          attestation_path=att_path)
        assert env['model_matches_request'] is False
        assert env['attested_model'] == substituted
        assert env['returned_model'] == substituted
        assert env['schema_compliant'] is False
        assert env['failure_class'] == 'model_substituted'
        assert 'differs from requested' in (env['error'] or '')
        # A non-compliant call must never carry a cost claim or a result.
        assert env['cost_evaluable'] is False
        assert env['result'] is None
        base.expect_refusal(lambda: ext.assert_not_promotable(env),
                            'permanently non-promotable')


def test_ambiguous_window_refuses_to_guess():
    """Two distinct served models in the window leave the match unresolved."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        record, att_path = attest(tmp, ticket, [
            turn(model=base.MODEL, stamp='2026-08-10T02:00:00.400Z'),
            turn(model='claude-sonnet-5', stamp='2026-08-10T02:00:00.900Z'),
        ])
        assert record['ambiguous'] is True
        assert record['attested_model'] is None
        assert record['model_matches_request'] is None
        assert len(record['models_observed']) == 2

        env = base.record(paths, ticket, response=base.wrapper(ticket, usage=USAGE),
                          attestation_path=att_path)
        assert env['attestation_ambiguous'] is True
        assert env['model_matches_request'] is None
        assert env['attested_model'] is None


def test_window_and_provenance_filters():
    """Out-of-window, non-sidechain and <synthetic> turns are excluded."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        record, _ = attest(tmp, ticket, [
            turn(stamp='2026-08-10T01:59:59.000Z'),          # before window
            turn(stamp='2026-08-10T02:00:05.000Z'),          # after window
            turn(sidechain=False),                            # main-loop turn
            turn(model=att.SYNTHETIC_MODEL),                  # harness-synthesised
            turn(etype='user'),                               # not an assistant turn
            turn(stamp='2026-08-10T02:00:00.600Z'),          # the only valid one
        ])
        assert record['turns_in_window'] == 1, record['turns_in_window']
        assert record['models_observed'] == [base.MODEL]

        # Including main-loop turns is opt-in and must widen the window.
        wide, _ = attest(tmp, ticket, [
            turn(sidechain=False, stamp='2026-08-10T02:00:00.300Z'),
            turn(sidechain=True, stamp='2026-08-10T02:00:00.700Z'),
        ], name='wide.json', sidechain_only=False)
        assert wide['turns_in_window'] == 2
        assert wide['sidechain_only'] is False


def test_misbound_or_tampered_attestation_is_refused():
    """Wrong run/reservation/model/window, or a broken self-hash, refuses."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        record, att_path = attest(tmp, ticket, [turn()])
        response = base.wrapper(ticket, usage=USAGE)

        def rewrite(mutate, name):
            bad = json.loads(json.dumps(record))
            mutate(bad)
            out = os.path.join(tmp, name)
            with open(out, 'wb') as handle:
                handle.write(canonical_json_bytes(bad))
            return out

        cases = [
            (lambda d: d.update(run_id='not-the-run'), 'run_id mismatch', 'a.json'),
            (lambda d: d.update(reservation_id='nope'), 'reservation_id mismatch', 'b.json'),
            (lambda d: d.update(requested_model='other-model'),
             'requested_model mismatch', 'c.json'),
            (lambda d: d.update(ended_at='2026-08-10T09:99:99.000Z'),
             'window does not match', 'd.json'),
            (lambda d: d.update(schema='pwg.wrong.v1'), 'schema mismatch', 'e.json'),
        ]
        for mutate, needle, name in cases:
            bad_path = rewrite(mutate, name)
            base.expect_refusal(
                lambda p=bad_path: base.record(
                    paths, ticket, response=response, attestation_path=p),
                needle)

        # Tampering with an attested field while keeping the stale hash must fail.
        tampered = json.loads(json.dumps(record))
        tampered['attested_model'] = 'claude-haiku-4-5'
        out = os.path.join(tmp, 'tampered.json')
        with open(out, 'wb') as handle:
            handle.write(canonical_json_bytes(tampered))
        base.expect_refusal(
            lambda: base.record(paths, ticket, response=response,
                                attestation_path=out),
            'self-hash does not verify')


def test_attestation_hash_is_canonical_and_stable():
    """The self-hash covers every field and is reproducible byte-for-byte."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = base.fixture(tmp)
        ticket = base.prepare(paths)
        first, _ = attest(tmp, ticket, [turn()], name='one.json')
        second, _ = attest(tmp, ticket, [turn()], name='two.json')
        assert first['attestation_sha256'] == second['attestation_sha256']
        body = dict(first)
        stated = body.pop('attestation_sha256')
        assert sha256_bytes(canonical_json_bytes(body)) == stated


def test_missing_transcript_and_bad_window_refuse():
    """Absent transcript or an inverted window refuses instead of guessing."""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            att.build_attestation(
                transcript_path=os.path.join(tmp, 'absent.jsonl'),
                started_at=START, ended_at=END, run_id='r', reservation_id='x',
                requested_model=base.MODEL)
            raise AssertionError('missing transcript must refuse')
        except att.AttestationError as exc:
            assert 'transcript not found' in str(exc)

        path = transcript(os.path.join(tmp, 't.jsonl'), [turn()])
        try:
            att.build_attestation(
                transcript_path=path, started_at=END, ended_at=START,
                run_id='r', reservation_id='x', requested_model=base.MODEL)
            raise AssertionError('inverted window must refuse')
        except att.AttestationError as exc:
            assert 'precedes' in str(exc)


def test_unparseable_lines_are_counted_not_swallowed():
    """A corrupt transcript line is reported, never silently dropped."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 't.jsonl')
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(json.dumps(turn()) + '\n')
            handle.write('{not valid json\n')
            handle.write('\n')
        record = att.build_attestation(
            transcript_path=path, started_at=START, ended_at=END,
            run_id='r', reservation_id='x', requested_model=base.MODEL)
        assert record['unparseable_lines'] == 1
        assert record['turns_in_window'] == 1


TESTS = [
    test_attested_match_is_observed_not_asserted,
    test_absent_attestation_is_null_never_true,
    test_substituted_model_is_sealed_not_silently_refused,
    test_ambiguous_window_refuses_to_guess,
    test_window_and_provenance_filters,
    test_misbound_or_tampered_attestation_is_refused,
    test_attestation_hash_is_canonical_and_stable,
    test_missing_transcript_and_bad_window_refuse,
    test_unparseable_lines_are_counted_not_swallowed,
]


def selftest():
    failed = []
    for test in TESTS:
        try:
            test()
            print('  PASS: ' + test.__name__)
        except BaseException as exc:  # noqa: BLE001 - aggregate the entire matrix
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
