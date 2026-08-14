"""H2704 PREP/TM census + Flash compiler tests. Zero paid calls."""
import os
import sys

PILOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'pilot'))
H1210 = os.path.join(PILOT, 'h1210')
sys.path.insert(0, PILOT)
sys.path.insert(0, H1210)

import cache_identity  # noqa: E402
import cache_pair_compare  # noqa: E402
import cache_prep_census as census  # noqa: E402
import cache_prep_pairs as pairs  # noqa: E402
import prep_pack  # noqa: E402
import prompt_compiler  # noqa: E402


def test_prep_compiler_matches_live_flash_messages():
    pack = {
        'key1': 'ca',
        'sense_inventory': [
            {'i': 1, 'sense_tag': '1', 'de_anchor': 'und'},
            {'i': 2, 'sense_tag': '2', 'de_anchor': 'auch'},
        ],
        'hard_flags': {
            'polysemy': False, 'monster_length': False, 'no_pwg': False,
        },
        'tm_fuzzy_hits': [
            {'key1': 'ca', 'score': 1.0, 'match_type': 'exact_content_sha'},
        ],
    }
    compiled = prompt_compiler.compile_prep_flash_v0(pack)
    system, user = prep_pack.flash_messages(pack)
    assert compiled['system'] == system
    assert compiled['user'] == user
    assert compiled['bundle']['requested_model'] == 'deepseek-v4-flash'
    assert compiled['bundle']['promotable'] is False


def test_stratified_selection_is_stable():
    rows = []
    for i, size in enumerate(('small', 'medium', 'large', 'monster')):
        for j, poly in enumerate(('sparse', 'poly')):
            for k in range(8):
                key = '%s-%s-%02d' % (size, poly, k)
                rows.append({
                    'key1': key,
                    'size_class': size,
                    'poly_class': poly,
                    'selection_hex': census.stable_hex(census.PREP_SALT, key),
                })
    first = [r['key1'] for r in census.allocate_stratified(rows, 50, census.PREP_SALT)]
    second = [r['key1'] for r in census.allocate_stratified(rows, 50, census.PREP_SALT)]
    assert first == second
    assert len(first) == 50
    assert len(set(first)) == 50


def test_pair_expansion_contiguous():
    compiled = []
    for index in range(50):
        compiled.append({
            'key1': 'k%02d' % index,
            'bundle': {
                'provider': 'deepseek',
                'requested_model': 'deepseek-v4-flash',
                'stable_prefix_sha256': 'prefix-a',
            },
            'request': {'request_id': 'rid-%02d' % index},
        })
    ordered, slots = pairs.expand_pairs(compiled)
    assert len(ordered) == 50
    assert len(slots) == 100
    pairs.expand_and_check_pairs(slots, 50)
    assert slots[0]['cold_warm'] == 'cold'
    assert slots[1]['cold_warm'] == 'warm'
    assert slots[0]['request_id'] == slots[1]['request_id']


def test_prep_blind_compare():
    a = {'ru_skeleton': ['и'], 'route_hint': 'park'}
    b = {'ru_skeleton': ['и'], 'route_hint': 'park'}
    c = {'ru_skeleton': ['или'], 'route_hint': 'full_worker'}
    assert cache_pair_compare.compare_prep_blind(a, b)['class'] == 'identical'
    assert cache_pair_compare.compare_prep_blind(a, c)['class'] == 'disagree'


def test_size_poly_classes():
    assert census.size_class(100) == 'small'
    assert census.size_class(2000) == 'medium'
    assert census.size_class(5000) == 'large'
    assert census.size_class(prep_pack.MONSTER_BYTES) == 'monster'
    assert census.poly_class(1) == 'sparse'
    assert census.poly_class(prep_pack.POLYSEMY_SENSE_FLOOR) == 'poly'


def test_compiler_selftest_still_green():
    assert prompt_compiler.selftest() == 0
    assert cache_identity.selftest() == 0
