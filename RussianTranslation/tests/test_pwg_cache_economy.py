"""Focused cache-economy contract tests (H2702/H2703). Zero paid calls."""
import os
import sys
import tempfile

PILOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'pilot'))
sys.path.insert(0, PILOT)

import cache_baseline_freeze  # noqa: E402
import cache_economy_report  # noqa: E402
import cache_event_ledger  # noqa: E402
import cache_generation_pairs as pairs  # noqa: E402
import cache_identity  # noqa: E402
import cache_migrate  # noqa: E402
import cache_pair_compare  # noqa: E402
import cache_reuse  # noqa: E402
import cache_scheduler  # noqa: E402
import prompt_compiler  # noqa: E402


def test_identity():
    assert cache_identity.selftest() == 0


def test_compiler_golden_bytes():
    assert prompt_compiler.selftest() == 0


def test_migrate_round_trip_and_refusal():
    assert cache_migrate.selftest() == 0


def test_ledger_crash_resume_and_torn():
    assert cache_event_ledger.selftest() == 0


def test_reuse_namespace_fence():
    assert cache_reuse.selftest() == 0


def test_scheduler_order():
    assert cache_scheduler.selftest() == 0


def test_baseline_manifest():
    assert cache_baseline_freeze.selftest() == 0


def test_pair_expansion_contiguous_cold_warm():
    compiled = []
    for index in range(22):
        compiled.append({
            'key1': 'k%02d' % index,
            'bundle': {
                'provider': 'deepseek',
                'requested_model': 'deepseek-v4-pro',
                'stable_prefix_sha256': 'prefix-a',
            },
            'request': {'request_id': 'rid-%02d' % index},
        })
    ordered, slots = pairs.expand_pairs(compiled)
    assert len(ordered) == 22
    assert len(slots) == 44
    pairs.expand_and_check_pairs(slots)
    assert slots[0]['cold_warm'] == 'cold'
    assert slots[1]['cold_warm'] == 'warm'
    assert slots[0]['request_id'] == slots[1]['request_id']
    assert slots[0]['source_ordinal'] == slots[1]['source_ordinal']
    assert [s['slot_ordinal'] for s in slots] == list(range(44))


def test_completed_pair_slots_keep_warm_open():
    events = [
        {'kind': 'terminal_response', 'request_id': 'rid-00', 'cold_warm': 'cold'},
        {'kind': 'completion', 'request_id': 'rid-00'},
    ]
    done = cache_event_ledger.completed_pair_slots(events)
    assert ('rid-00', 'cold') in done
    assert ('rid-00', 'warm') not in done
    assert 'rid-00' in cache_event_ledger.completed_request_ids(events)


def test_blind_compare_retains_disagreement():
    a = {'records': [{'grammar': '{T1}', 'senses': [
        {'german': '{T1} a', 'russian': '{T1} а'}]}]}
    b = {'records': [{'grammar': '{T1}', 'senses': [
        {'german': '{T1} a', 'russian': '{T1} б'}]}]}
    same = cache_pair_compare.compare_blind(a, a)
    diff = cache_pair_compare.compare_blind(a, b)
    assert same['identical'] is True
    assert same['class'] == 'identical'
    assert diff['identical'] is False
    assert diff['class'] in ('equivalent_structure', 'disagree')
    assert 'left_sha256' in diff and 'right_sha256' in diff


def _term(rid, cw, parseable, clean, usd, hit, miss, ordinal):
    return {
        'kind': 'terminal_response',
        'request_id': rid,
        'cold_warm': cw,
        'source_ordinal': ordinal,
        'requested_model': 'deepseek-v4-pro',
        'served_model': 'deepseek-v4-pro',
        'usage': {
            'prompt_tokens': miss + hit,
            'completion_tokens': 10,
            'cache_hit_tokens': hit,
            'cache_miss_tokens': miss,
        },
        'cost_evaluable': True,
        'observed_cost_usd': usd,
        'detail': {
            'parseable': parseable,
            'det_clean': clean,
            'key1': rid,
        },
    }


def test_economy_report_pass_and_fail():
    manifest = {
        'sealed': True,
        'run_id': 't',
        'manifest_sha256': '0' * 64,
        'promotable': False,
    }
    events = []
    for i in range(22):
        rid = 'r%02d' % i
        events.append(_term(rid, 'cold', True, True, 0.02, 0, 100, i))
        events.append(_term(rid, 'warm', True, True, 0.01, 80, 20, i))
    derived = cache_economy_report.derive(manifest, events)
    assert derived['generation_lane_verdict'] == 'PASS'
    assert derived['parseable'] == 44
    assert derived['unique_clean_cards'] == 22
    assert derived['adoption'] == 'deferred_to_H2704'
    assert derived['cache_hit_is_not_accepted_artifact'] is True
    assert derived['paired_delta_warm_minus_cold']['n'] == 22

    fail_events = events[:40]
    fail_events.append(_term('r20', 'cold', False, False, 0.02, 0, 100, 20))
    fail_events.append(_term('r20', 'warm', False, False, 0.02, 0, 100, 20))
    fail_events.append(_term('r21', 'cold', False, False, 0.02, 0, 100, 21))
    fail_events.append(_term('r21', 'warm', False, False, 0.02, 0, 100, 21))
    failed = cache_economy_report.derive(manifest, fail_events)
    assert failed['generation_lane_verdict'] == 'FAIL'
    assert failed['parseable'] < 42


def test_compile_only_seals_without_provider_calls(tmp_path=None):
    cohort = pairs.load_cohort()
    baseline = cache_baseline_freeze.build_manifest()
    compiled, extra, prefixes = pairs.compile_cohort(cohort, baseline)
    assert len(compiled) == 22
    assert extra['requested_model'] == 'deepseek-v4-pro'
    assert extra['generation_parameters']['reasoning_effort'] == 'high'
    assert extra['generation_parameters']['max_tokens'] == 32768
    ids = [row['request']['request_id'] for row in compiled]
    assert len(set(ids)) == 22
    assert prefixes
    _, slots = pairs.expand_pairs(compiled)
    pairs.expand_and_check_pairs(slots)
    with tempfile.TemporaryDirectory() as tmp:
        runner = pairs.PairRunner(
            os.path.join(tmp, 'run'), compiled, slots, cohort, baseline)
        man = runner.seal(baseline.get('source_commit') or '0' * 40)
        assert man['n'] == 22
        assert man['call_ceiling'] == 44
        assert man['promotable'] is False
        assert man['requested_model'] == 'deepseek-v4-pro'
        assert len(man['schedule']) == 44
        done = runner.load_resume()
        assert done == set()
