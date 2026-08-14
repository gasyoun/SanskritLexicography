"""H2756 zero-call gates: CONCLUSIONS replay + disjoint 50-ID seal."""
import os
import sys

PILOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'pilot'))
sys.path.insert(0, PILOT)

import cache_prep_h2756 as h2756  # noqa: E402


def test_conclusions_replay_from_sealed_summaries():
    replay = h2756.verify_conclusions()
    assert replay['ok'] is True
    assert replay['flash_parseable'] == 100


def test_h2756_selection_disjoint_from_h2704():
    selected, pool, banned = h2756.select_50()
    keys = [row['key1'] for row in selected]
    assert len(keys) == 50
    assert len(set(keys)) == 50
    assert not (set(keys) & banned)
    assert len(banned) == 50
    assert len(pool) == 150
    again, _, _ = h2756.select_50()
    assert [row['key1'] for row in again] == keys


def test_h2756_salt_is_not_h2704_salt():
    assert h2756.PREP_SALT != 'h2704-prep-50-v1'
    assert h2756.PREP_SALT.startswith('h2756-')


def test_h2704_ratio_of_means_recovers_same_card_save():
    summary = h2756.load_json(os.path.join(
        h2756.H2704_DIR, 'prep50', 'run', 'summary.json'))
    save = h2756.paired_save_metrics(summary)
    assert save['n'] == 50
    assert round(save['point_save'], 3) == 0.099
