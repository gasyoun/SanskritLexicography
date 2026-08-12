#!/usr/bin/env python
r"""Hermetic test matrix for [prep_context_compare.py](prep_context_compare.py) (H2591).

Zero network, zero spend, zero repo mutation: every case builds a synthetic manifest +
sealed `pwg.prep_context.v1` contexts in a temp dir and drives the driver through an
injected ``caller``. The matrix is the one H2591 names as evidence:

    prompt identity · context hash · TM fence · reservation exhaustion · crash/resume ·
    model substitution · missing usage · exact-once finalization

plus the offline-check fence set (manifest source, billing attribution, plan replay) and
the receipt's GO / NO-GO / INCONCLUSIVE arithmetic.

Run standalone or through ``prep_context_compare.py --selftest``; also wired into
``window_selftest.py`` as ``test_h2591_prep_context_compare_matrix``.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(HERE)
SRC = os.path.dirname(PILOT)
for _path in (HERE, PILOT, SRC):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import prep_context_compare as pcc                          # noqa: E402
import prep_pack                                            # noqa: E402
from call_reservation import CallReservationLedger          # noqa: E402
from headless_worker import build_prompt                    # noqa: E402

KEYS = ['aKey%d' % i for i in range(1, pcc.PAIR_COUNT + 1)]


# --------------------------------------------------------------------------- fixtures

def _manifest(tmp, *, credit=True):
    """A minimal but SHAPE-REAL manifest: build_prompt must accept it unchanged."""
    inputs = {}
    for index, key in enumerate(KEYS):
        inputs[key] = {
            'skeleton': 'sense {T%d} gloss\n' % (index + 1),
            'portrait': '{"key1": "%s"}' % key,
            'ls': 1, 'sk': 0, 'senses': 1, 'source_senses': 1, 'nws': 0,
        }
    manifest = {
        'schema': 'pwg.headless_execution_manifest.v2',
        'field': 'russian',
        'model': 'claude-sonnet-5',
        'execution': {
            'profile_slot': 'selftest',
            'execution_route': 'claude-cli-headless',
            'agent_sdk_credit_claimed': bool(credit),
            'agent_sdk_credit_claim_evidence': 'selftest-credit-claim:2026-08' if credit else None,
        },
        'prompt': {'preamble': 'PRE\n', 'translation': 'TR\n', 'grammar': 'GR\n',
                   'grammars': {}, 'nws_rule': 'NWS'},
        'output_schema': {'type': 'object', 'properties': {'cards': {'type': 'array'}}},
        'inputs': inputs,
        'placeholder_maps': {k: ['<ls>x</ls>'] for k in KEYS},
    }
    path = os.path.join(tmp, 'execution_manifest.selftest.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=1)
    return path, manifest


def _contexts(tmp, manifest_path, manifest):
    """Seal one manifest-sourced context per key via prep_pack's own writer."""
    context_dir = os.path.join(tmp, 'contexts')
    manifest_sha = pcc.sha256_file(manifest_path)
    for index, key in enumerate(KEYS):
        pack = prep_pack.empty_pack(key, mode='dry')
        pack['sense_inventory'] = [{'i': 0, 'sense_tag': '1',
                                    'de_anchor': 'gloss {T%d}' % (index + 1), 'layer': 'de'}]
        pack['source_evidence'] = {
            'kind': 'execution_manifest',
            'sha256': pcc.sha256_text(manifest['inputs'][key]['skeleton']),
            'manifest_sha256': manifest_sha,
        }
        pack['tm_fuzzy_hits'] = [{
            'rank': 1, 'key1': key, 'score': 0.71, 'match_type': 'key1_difflib',
            'ru_preview': 'preview', 'reuse_hint': 'advisory', 'evidence_sha256': None,
            'may_auto_reuse': False, 'advisory_only': True,
            'decision_authority': 'promoter_only',
        }]
        pack['route_hint'] = 'full_worker'
        prep_pack.write_compact_context(context_dir, pack)
    return context_dir


def _plan(tmp, *, credit=True):
    manifest_path, manifest = _manifest(tmp, credit=credit)
    context_dir = _contexts(tmp, manifest_path, manifest)
    plan = pcc.build_plan(manifest_path, context_dir)
    pcc.atomic_json(os.path.join(tmp, 'plan.json'), plan)
    return plan, manifest_path, manifest, context_dir


def _wrapper(*, cards, cost=0.42, usage=True, model='claude-opus-5'):
    value = {'is_error': False, 'duration_api_ms': 900, 'total_cost_usd': cost,
             'model': model, 'structured_output': {'cards': cards}}
    if usage:
        value['usage'] = {'input_tokens': 1000, 'output_tokens': 200,
                          'cache_creation_input_tokens': 10, 'cache_read_input_tokens': 5}
    return value


def _good_card(key, token):
    return {'key1': key, 'notes': '',
            'records': [{'grammar': '', 'senses': [
                {'tag': '1', 'german': 'gloss %s' % token, 'russian': 'глосса %s' % token}]}]}


def _caller_factory(*, model='claude-opus-5', usage=True, drop_token_for=(),
                    wall_ms=1000, prep_wall_ms=None, log=None):
    """An injected caller: deterministic, offline, and arm-aware via the prompt bytes."""

    def caller(argv, prompt, timeout):                       # noqa: ANN001
        is_prep = pcc.PREP_OPEN in prompt
        key = next(k for k in KEYS if ('=== CARD %s ===' % k) in prompt)
        token = '{T%d}' % (KEYS.index(key) + 1)
        card = _good_card(key, '' if key in drop_token_for and is_prep else token)
        if log is not None:
            log.append((key, 'B' if is_prep else 'A'))
        return pcc.CallResult(
            returncode=0, timed_out=False,
            wall_ms=(prep_wall_ms if (is_prep and prep_wall_ms is not None) else wall_ms),
            stdout=json.dumps(_wrapper(cards=[card], usage=usage, model=model)), stderr='')

    return caller


def _run(tmp, plan, caller, *, run_id='h2591-selftest', out='run', billing=None):
    return pcc.execute(plan, ledger_path=os.path.join(tmp, 'ledger.json'), run_id=run_id,
                       out_dir=os.path.join(tmp, out), caller=caller,
                       billing=billing or {'max_agent_sdk_credit_claimed': True,
                                           'credit_claim_evidence': 'selftest-credit-claim:2026-08'})


# --------------------------------------------------------------------------- cases

def test_prompt_identity_and_single_prep_block():
    with tempfile.TemporaryDirectory() as tmp:
        plan, manifest_path, manifest, context_dir = _plan(tmp)
        contexts = pcc.load_contexts(context_dir, KEYS)
        for key in KEYS:
            prompt_a, prompt_b = pcc.arm_prompts(manifest, key, contexts[key]['context'])
            assert prompt_a == build_prompt(manifest, [key]), 'arm A must be production bytes'
            assert prompt_b.startswith(prompt_a), 'arm B must extend arm A byte-exactly'
            assert prompt_b.count(pcc.PREP_OPEN) == 1
            assert prompt_b.count(pcc.PREP_CLOSE) == 1
            assert pcc.PREP_OPEN not in prompt_a
            assert pcc.sha256_text(prompt_a) == plan['prompts'][key]['A']['sha256']
            assert pcc.sha256_text(prompt_b) == plan['prompts'][key]['B']['sha256']
        print('  ok   prompt identity: A is production, B = A + exactly one PREP block')


def test_plan_replays_byte_identically():
    with tempfile.TemporaryDirectory() as tmp:
        plan, manifest_path, _manifest_value, context_dir = _plan(tmp)
        again = pcc.build_plan(manifest_path, context_dir, selection=plan['strata'] or None)
        assert again['plan_sha256'] == plan['plan_sha256'], 'plan must exclude observation time'
        pcc.verify_plan_hash(plan)
        tampered = json.loads(json.dumps(plan))
        tampered['output_limit'] = plan['output_limit'] + 1
        try:
            pcc.verify_plan_hash(tampered)
        except pcc.FenceFailure:
            pass
        else:
            raise AssertionError('a tampered plan must not verify')
        print('  ok   plan hash replays byte-identically and detects tampering')


def test_context_hash_and_tm_fence():
    with tempfile.TemporaryDirectory() as tmp:
        plan, manifest_path, _m, context_dir = _plan(tmp)
        report = pcc.check(plan, ledger_path=os.path.join(tmp, 'ledger.json'), run_id='check-ok')
        assert report['ok'] and report['network_calls'] == 0
        assert report['conditions']['context_hash_replay']
        assert report['conditions']['tm_fence_intact']

        # A context whose sealed hash no longer replays is fatal, not a warning.
        path = os.path.join(context_dir, '%s.context.json' % pcc._stem(KEYS[0]))
        with open(path, encoding='utf-8') as handle:
            value = json.load(handle)
        value['sense_count'] = (value['sense_count'] or 0) + 5
        with open(path, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(value, handle, ensure_ascii=False, indent=1)
        try:
            pcc.check(plan, ledger_path=os.path.join(tmp, 'ledger2.json'), run_id='check-bad')
        except SystemExit:
            pass                                   # prep_pack.verify_compact_context raises this
        except pcc.FenceFailure:
            pass
        else:
            raise AssertionError('a drifted context must fail the check')
        print('  ok   context hash replay + TM fence are fail-closed')


def test_fuzzy_hit_never_reusable():
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, context_dir = _plan(tmp)
        path = os.path.join(context_dir, '%s.context.json' % pcc._stem(KEYS[0]))
        with open(path, encoding='utf-8') as handle:
            value = json.load(handle)
        value['tm_hits'][0]['may_auto_reuse'] = True          # fuzzy claimed as exact reuse
        unsigned = {k: v for k, v in value.items() if k != 'context_sha256'}
        value['context_sha256'] = pcc.sha256_bytes(prep_pack._canonical_bytes(unsigned))
        with open(path, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(value, handle, ensure_ascii=False, indent=1)
        try:
            pcc.check(plan, ledger_path=os.path.join(tmp, 'ledger.json'), run_id='fuzzy')
        except (SystemExit, pcc.FenceFailure):
            pass
        else:
            raise AssertionError('a fuzzy hit marked auto-reusable must fail the check')
        print('  ok   a fuzzy / same-key TM hit is never exact-content reuse')


def test_billing_unknown_requires_authorization():
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp, credit=False)
        try:
            pcc.check(plan, ledger_path=os.path.join(tmp, 'l1.json'), run_id='nobill')
        except pcc.FenceFailure as exc:
            assert 'UNKNOWN' in str(exc)
        else:
            raise AssertionError('unattributed billing must refuse without authorization')
        report = pcc.check(plan, ledger_path=os.path.join(tmp, 'l2.json'), run_id='nobill2',
                           authorize_unknown_billing=True)
        assert report['billing']['billing_mode'] == 'unknown_gateway'
        assert report['billing']['authorized_unknown_billing'] is True
        print('  ok   missing credit evidence => UNKNOWN billing + explicit authorization')


def test_reservation_exhaustion_and_exact_once_finalization():
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp)
        run = _run(tmp, plan, _caller_factory())
        assert run['calls_spent'] == pcc.MAX_CALLS, run['calls_spent']
        assert run['stopped'] is None
        ledger = CallReservationLedger.open_existing(os.path.join(tmp, 'ledger.json'),
                                                     'h2591-selftest')
        snapshot = ledger.snapshot()
        assert len(snapshot['reservations']) == pcc.MAX_CALLS
        assert all(row['finalized'] for row in snapshot['reservations'])
        assert snapshot['usage']['finalized_calls'] == pcc.MAX_CALLS
        assert snapshot['usage']['pending_calls'] == 0
        # Under a claimed Max credit there is no observed cash, so the ledger's
        # cost_evaluable is False BY DESIGN while token evidence is complete.
        assert snapshot['usage']['cost_evaluable'] is False
        assert snapshot['usage']['unevaluable_calls'] == pcc.MAX_CALLS
        assert all(pcc.usage_evaluable(row['telemetry'])
                   for row in snapshot['reservations'])
        # A 17th reservation is refused by the ledger itself, not by driver etiquette.
        try:
            ledger.reserve('overflow')
        except Exception as exc:                              # CallLimitReached
            assert 'ceiling' in str(exc)
        else:
            raise AssertionError('reservation 17 must be refused')
        print('  ok   16 reservations, each finalized exactly once; the 17th is refused')


def test_crash_resume_never_respends():
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp)
        log = []
        _run(tmp, plan, _caller_factory(log=log))
        assert len(log) == pcc.MAX_CALLS
        # Second pass over the same out-dir: every envelope already exists.
        again = []
        run = _run(tmp, plan, _caller_factory(log=again))
        assert again == [], 'a resumed run must not re-issue a finalized call'
        assert run['calls_spent'] == pcc.MAX_CALLS
        assert len(run['envelopes']) == pcc.MAX_CALLS
        print('  ok   crash/resume replays sealed envelopes without re-spending')


def test_model_substitution_stops_the_run():
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp)
        run = _run(tmp, plan, _caller_factory(model='claude-sonnet-5'))
        assert run['stopped'] and 'model_substitution' in run['stopped'], run['stopped']
        assert run['calls_spent'] == 1, 'the run must stop on the FIRST substitution'
        print('  ok   model substitution stops the run at the first call')


def test_missing_usage_stops_the_run():
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp)
        run = _run(tmp, plan, _caller_factory(usage=False))
        assert run['stopped'] and 'missing_usage' in run['stopped'], run['stopped']
        assert run['calls_spent'] == 1
        envelope = run['envelopes'][0]
        assert envelope['telemetry']['cost_evaluable'] is False
        assert envelope['result_sha256'] is None
        print('  ok   corrupt/missing usage stops the run and is never priced at zero')


def test_receipt_go_no_go_inconclusive():
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp)
        report = pcc.check(plan, ledger_path=os.path.join(tmp, 'chk.json'), run_id='r')

        # NO-GO: PREP is neither faster nor cheaper (identical arms).
        run = _run(tmp, plan, _caller_factory(), run_id='flat', out='flat')
        receipt = pcc.build_receipt(plan, run, check_report=report)
        assert receipt['complete'] is True
        assert receipt['verdict'] == 'NO-GO', receipt['verdict']
        assert receipt['arm_a_baseline']['audited_pass'] == pcc.PAIR_COUNT
        assert receipt['promotion'] == {'store_written': False, 'tm_written': False,
                                        'promotion_journal_written': False,
                                        'production_default_changed': False}

        # GO: PREP halves wall time and loses no audited card.
        run = _run(tmp, plan, _caller_factory(wall_ms=1000, prep_wall_ms=400),
                   run_id='fast', out='fast')
        receipt = pcc.build_receipt(plan, run, check_report=report)
        assert receipt['deltas']['wall_ms_relative_gain'] > 0.10
        assert receipt['verdict'] == 'GO', receipt['verdict']

        # NO-GO despite a speedup: PREP loses two audited cards.
        run = _run(tmp, plan, _caller_factory(wall_ms=1000, prep_wall_ms=400,
                                              drop_token_for=(KEYS[0], KEYS[1])),
                   run_id='lossy', out='lossy')
        receipt = pcc.build_receipt(plan, run, check_report=report)
        assert receipt['deltas']['audited_cards_lost_by_prep'] == 2
        assert receipt['verdict'] == 'NO-GO', receipt['verdict']

        # INCONCLUSIVE: a stopped run is never a verdict on the design.
        run = _run(tmp, plan, _caller_factory(usage=False), run_id='stop', out='stop')
        receipt = pcc.build_receipt(plan, run, check_report=report)
        assert receipt['verdict'] == 'INCONCLUSIVE', receipt['verdict']
        assert 'descriptive qualification' in receipt['evidence_class']
        print('  ok   receipt arithmetic: GO / NO-GO / INCONCLUSIVE all reachable')


def test_zero_filled_usage_is_missing_usage_not_a_measurement():
    """H2591 measured run: 7/16 calls returned every counter zeroed — two of them after
    producing a card that passed the audit at coverage 1.0. `usage_evaluable` checked the
    SHAPE of the usage block and passed them, so the run spent all 16 calls and the receipt
    graded a token comparison built over holes. A completed call always consumes tokens.
    """
    zeroed = {'accounting': {'usage_evaluable': True, 'input_tokens': 0, 'output_tokens': 0,
                             'cache_read_tokens': 0, 'cache_creation_tokens': 0},
              'input_tokens': 0, 'output_tokens': 0, 'cache_read_tokens': 0,
              'cache_creation_tokens': 0, 'cost_evaluable': False}
    assert not pcc.usage_evaluable(zeroed), 'all-zero usage must read as MISSING'
    real = dict(zeroed, output_tokens=40417)
    real['accounting'] = dict(zeroed['accounting'], output_tokens=40417)
    assert pcc.usage_evaluable(real), 'a real credit-mode call must stay evaluable'

    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp)
        report = pcc.check(plan, ledger_path=os.path.join(tmp, 'chk.json'), run_id='holes')

        # The run now stops at the first zero-filled call instead of spending sixteen.
        def zero_usage_caller(argv, prompt, timeout):
            card = _good_card(KEYS[0], '{T1}')
            wrapper = _wrapper(cards=[card])
            wrapper['usage'] = {k: 0 for k in wrapper['usage']}
            return pcc.CallResult(returncode=0, timed_out=False, wall_ms=1000,
                                  stdout=json.dumps(wrapper), stderr='')

        run = _run(tmp, plan, zero_usage_caller, run_id='zero', out='zero')
        assert run['stopped'] and 'missing_usage' in run['stopped'], run['stopped']
        assert run['calls_spent'] == 1, 'a holed measurement must not spend the whole ceiling'

        # And a complete run carrying any hole can never be graded GO.
        holed = _run(tmp, plan, _caller_factory(wall_ms=1000, prep_wall_ms=100),
                     run_id='graded', out='graded')
        for envelope in holed['envelopes'][:1]:
            envelope['telemetry'] = zeroed
        receipt = pcc.build_receipt(plan, holed, check_report=report)
        assert receipt['evidence_holes']['usage_unevaluable_calls'] >= 1
        assert receipt['verdict'] == 'INCONCLUSIVE', receipt['verdict']
        print('  ok   zero-filled usage is a hole, not a measurement; holes force INCONCLUSIVE')


def test_b1_capture_gap_terminal_fields_raw_text_and_modelusage_crosscheck():
    """H2591 B1: the run's seven zero-usage calls were undiagnosable because the driver
    kept none of the evidence. Five were rc=1 refusals (zero usage is correct there), two
    were rc=0 successes with a full audited card and no tokens — and one `subtype` reading
    would have split them. The anomaly did not reproduce on a byte-identical re-issue, so
    the fix is capture, not a root-cause guard.
    """
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp)

        # modelUsage carries tokens the top-level usage block dropped -> a CONTRADICTION,
        # detectable, instead of a silent hole that deflates one arm.
        def contradicting(argv, prompt, timeout):
            card = _good_card(KEYS[0], '{T1}')
            wrapper = _wrapper(cards=[card])
            wrapper['usage'] = {k: 0 for k in wrapper['usage']}
            wrapper['modelUsage'] = {'claude-opus-5': {
                'inputTokens': 2, 'outputTokens': 12685,
                'cacheReadInputTokens': 0, 'cacheCreationInputTokens': 62948}}
            wrapper.update({'subtype': 'success', 'terminal_reason': 'completed',
                            'stop_reason': 'tool_use', 'num_turns': 2})
            return pcc.CallResult(returncode=0, timed_out=False, wall_ms=171359,
                                  stdout=json.dumps(wrapper), stderr='')

        run = _run(tmp, plan, contradicting, run_id='xcheck', out='xcheck')
        assert run['stopped'] and 'usage_contradiction' in run['stopped'], run['stopped']
        env = run['envelopes'][0]
        assert env['usage_cross_check']['agree'] is False
        assert env['usage_cross_check']['model_usage_total'] == 75635
        assert 'all-zero' in env['usage_cross_check']['contradiction']
        assert env['terminal']['subtype'] == 'success'
        assert env['terminal']['terminal_reason'] == 'completed'
        assert env['terminal']['num_turns'] == 2

        # An rc=1 refusal is its OWN class, keeps its raw text, and does NOT stop the run:
        # it is a provider verdict on one call, not proof the ledger is lying.
        def refusing(argv, prompt, timeout):
            wrapper = _wrapper(cards=[])
            wrapper['result'] = "You've hit your weekly limit · resets Aug 10"
            wrapper.pop('structured_output')
            wrapper.update({'subtype': 'error', 'is_error': True,
                            'terminal_reason': 'error', 'api_error_status': 429})
            return pcc.CallResult(returncode=1, timed_out=False, wall_ms=42851,
                                  stdout=json.dumps(wrapper), stderr='')

        run = _run(tmp, plan, refusing, run_id='refuse', out='refuse')
        env = run['envelopes'][0]
        assert env['failure_class'] == 'cli_error_exit', env['failure_class']
        assert 'weekly limit' in env['raw_result'], 'the refusal text IS the evidence'
        assert env['terminal']['api_error_status'] == 429
        assert run['calls_spent'] == pcc.MAX_CALLS, 'a refusal must not stop the run'
        print('  ok   B1 capture: terminal fields, raw result text, modelUsage cross-check')


def test_selection_rule_is_deterministic_and_stratified():
    pool = {}
    for index in range(40):
        pool['k%02d' % index] = {
            'bytes': 500 + index * 800, 'placeholders': index % 7,
            'source_senses': index % 9, 'ls': index % 3,
        }
    first = pcc.select_keys(pool)
    second = pcc.select_keys(dict(reversed(list(pool.items()))))
    assert first == second, 'selection must not depend on dict order'
    flat = [k for stratum in pcc.STRATA for k in first[stratum]]
    assert len(set(flat)) == pcc.PAIR_COUNT
    assert all(len(first[stratum]) == 2 for stratum in pcc.STRATA)
    assert all(pool[k]['bytes'] >= prep_pack.MONSTER_BYTES for k in first['long_monster'])
    print('  ok   selection is order-independent, disjoint, and two per stratum')


def test_offline_check_makes_no_transport_call():
    with tempfile.TemporaryDirectory() as tmp:
        plan, _mp, _m, _cd = _plan(tmp)
        report = pcc.check(plan, ledger_path=os.path.join(tmp, 'l.json'), run_id='net')
        assert report['network_calls'] == 0
        trap = pcc._NetworkTrap()
        trap.install()
        try:
            import socket
            probe = socket.socket()
            try:
                probe.connect(('127.0.0.1', 9))
            except pcc.FenceFailure:
                pass
            else:
                raise AssertionError('the trap must refuse a real connect')
            finally:
                probe.close()
        finally:
            trap.remove()
        assert trap.calls == 1, 'the trap must COUNT the attempt, not just refuse it'
        print('  ok   --check is offline, and the offline claim is falsifiable')


CASES = [
    test_prompt_identity_and_single_prep_block,
    test_plan_replays_byte_identically,
    test_context_hash_and_tm_fence,
    test_fuzzy_hit_never_reusable,
    test_billing_unknown_requires_authorization,
    test_reservation_exhaustion_and_exact_once_finalization,
    test_crash_resume_never_respends,
    test_model_substitution_stops_the_run,
    test_missing_usage_stops_the_run,
    test_receipt_go_no_go_inconclusive,
    test_zero_filled_usage_is_missing_usage_not_a_measurement,
    test_b1_capture_gap_terminal_fields_raw_text_and_modelusage_crosscheck,
    test_selection_rule_is_deterministic_and_stratified,
    test_offline_check_makes_no_transport_call,
]


def selftest() -> int:
    failed = []
    for case in CASES:
        try:
            case()
        except BaseException as exc:                          # noqa: BLE001
            failed.append(case.__name__)
            print('  FAIL %s -- %s: %s' % (case.__name__, exc.__class__.__name__, exc))
    if failed:
        print('prep_context_compare selftest: FAIL (%d/%d): %s'
              % (len(failed), len(CASES), ', '.join(failed)))
        return 1
    print('prep_context_compare selftest: PASS (%d/%d hermetic cases, zero calls)'
          % (len(CASES), len(CASES)))
    return 0


if __name__ == '__main__':
    sys.exit(selftest())
