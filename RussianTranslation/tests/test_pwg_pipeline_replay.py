"""H3714 Wave 1 — exact replay of the four frozen campaigns (V9, R4.1/R4.2).

The comparison is structural, not a count: selection, transitions, calls,
route/model bindings, verdicts, requeue decisions, promotion deltas and the
store projection all have to match the frozen expectation exactly.
"""
import json
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from pwg_pipeline import model, replay  # noqa: E402

MATRIX = os.path.join(ROOT, 'tests', 'fixtures', 'pwg_pipeline')


def frozen(name):
    with open(os.path.join(MATRIX, name, 'expected.json'), encoding='utf-8') \
            as handle:
        return json.load(handle)


def test_the_four_campaigns_are_frozen_on_disk():
    assert replay.CAMPAIGNS == ('clean_success', 'partial_requeue',
                                'provider_timeout', 'promotion_interrupt')
    for name in replay.CAMPAIGNS:
        assert os.path.isfile(os.path.join(MATRIX, name, 'campaign.json'))
        assert os.path.isfile(os.path.join(MATRIX, name, 'expected.json'))


@pytest.mark.parametrize('name', replay.CAMPAIGNS)
def test_each_campaign_replays_exactly(tmp_path, name):
    report = replay.replay(os.path.join(MATRIX, name),
                           workdir=str(tmp_path / name), exact=True)
    assert report['frozen'] is True
    assert report['mismatches'] == []
    assert report['exact'] is True


def test_the_whole_matrix_has_zero_unexplained_mismatches():
    report = replay.replay_matrix(MATRIX, exact=True)
    assert report['unexplained_mismatches'] == 0
    assert report['exact'] is True
    assert len(report['campaigns']) == 4


def test_replay_is_deterministic(tmp_path):
    first = replay.replay(os.path.join(MATRIX, 'clean_success'),
                          workdir=str(tmp_path / 'a'))
    second = replay.replay(os.path.join(MATRIX, 'clean_success'),
                           workdir=str(tmp_path / 'b'))
    assert first['projection_sha256'] == second['projection_sha256']


def test_clean_success_promotes_every_job_to_complete():
    expected = frozen('clean_success')
    assert [job['state'] for job in expected['jobs']] == \
        [model.COMPLETE, model.COMPLETE]
    assert expected['store']['rows'] == 2
    assert expected['promotion_phases'] == [model.COMPLETE, model.COMPLETE]
    assert expected['accounting']['cost_evaluable'] is True


def test_partial_requeue_separates_clean_requeue_and_defect():
    expected = frozen('partial_requeue')
    by_identity = {job['source_identity']: job for job in expected['jobs']}
    assert by_identity['pwg.mixed.clean']['state'] == model.COMPLETE
    assert by_identity['pwg.mixed.empty']['verdicts'][0]['verdict_class'] == \
        model.VERDICT_REQUEUE
    assert by_identity['pwg.mixed.defect']['verdicts'][0]['verdict_class'] == \
        model.VERDICT_DEFECT
    # Identity-exact apply intents: one of each, never a blanket sweep.
    assert sorted(row['intent'] for row in expected['intents']) == \
        ['promote', 'quarantine', 'requeue']
    # Only the clean row reached the store.
    assert expected['store']['rows'] == 1


def test_provider_timeout_finalizes_once_and_promotes_nothing():
    expected = frozen('provider_timeout')
    by_identity = {job['source_identity']: job for job in expected['jobs']}
    timeout_call = by_identity['pwg.timeout.1']['calls'][0]
    assert timeout_call['state'] == model.CALL_TIMED_OUT
    assert timeout_call['failure_class'] == 'timeout'
    assert timeout_call['cost_evaluable'] == 0
    # Exactly one call per job: a timeout is never retried in Wave 1.
    assert all(len(job['calls']) == 1 for job in expected['jobs'])
    assert expected['promotion_phases'] == []
    assert expected['store']['exists'] is False
    # A malformed reply still carries attributable billed usage.
    malformed = by_identity['pwg.malformed.1']['calls'][0]
    assert malformed['state'] == model.CALL_MALFORMED
    assert malformed['input_tokens'] == 40


def test_a_diverging_run_is_reported_not_swallowed(tmp_path):
    fixture = tmp_path / 'diverging'
    fixture.mkdir()
    with open(os.path.join(MATRIX, 'clean_success', 'campaign.json'),
              encoding='utf-8') as handle:
        spec = json.load(handle)
    spec['jobs'][0]['script'] = [{'mode': replay.MODE_EMPTY_TARGET}]
    with open(fixture / 'campaign.json', 'w', encoding='utf-8',
              newline='\n') as handle:
        json.dump(spec, handle, ensure_ascii=False, indent=2)
    with open(os.path.join(MATRIX, 'clean_success', 'expected.json'),
              encoding='utf-8') as handle:
        expectation = handle.read()
    with open(fixture / 'expected.json', 'w', encoding='utf-8',
              newline='\n') as handle:
        handle.write(expectation)
    with pytest.raises(replay.ReplayMismatch):
        replay.replay(str(fixture), workdir=str(tmp_path / 'work'), exact=True)


def test_diff_reports_readable_paths():
    findings = replay.diff({'a': {'b': 1}}, {'a': {'b': 2}})
    assert findings == ['$.a.b: 1 != 2']
    assert replay.diff({'a': [1, 2]}, {'a': [1]})[0].startswith('$.a: length')


def test_normalize_drops_run_scoped_identifiers(tmp_path):
    projection = replay.run_campaign(os.path.join(MATRIX, 'clean_success'),
                                     str(tmp_path / 'work'))
    raw = json.dumps(projection)
    normalized = replay.normalize(projection)
    as_text = json.dumps(normalized)
    # The raw projection carries run-scoped keys; the normalized one must not,
    # or two identical runs would never compare equal.
    assert 'job_id' in raw and 'payload_sha256' in raw
    assert 'job_id' not in as_text
    assert 'payload_sha256' not in as_text
    assert 'promotion_id' not in as_text
    assert 'sha256' not in json.dumps(normalized['store'])
