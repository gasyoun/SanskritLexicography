#!/usr/bin/env python3
"""Pins for `cohort_live_admission` (H4527) — the record-gated LIVE cohort-width admission.

Every pin here is a fail-closed claim: the module must refuse unless an evidence-bearing
acceptance record exists AND validates AND the requested width is within the code cap.
Run: `python cohort_live_admission_selftest.py`
"""
import copy
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cohort_live_admission as cla  # noqa: E402

VALID = {
    'schema': cla.SCHEMA,
    'serial_acceptance': {
        'run_id': 'bsr-20260911T000000Z',
        'window_id': 'no_pwg_w02',
        'profile': 'c1',
        'completed_utc': '2026-09-11T00:00:00Z',
        'byte_identical_to_serial': True,
        'via_cohort_path': True,
        'evidence': ['pwg_ru/h4527/SERIAL_ACCEPTANCE_PACKET.md'],
    },
    'reviewer_sign_off': {
        'reviewer': 'Codex',
        'session': 'codex-review-h4527',
        'verdict': 'PASS',
        'dated': '2026-09-11',
        'evidence': ['pwg_ru/h4527/H4527_REVIEW_CODEX.md'],
    },
    'max_admitted_width': 2,
    'admitted_profiles': ['c1', 'c2'],
}


def _write(td, record):
    path = os.path.join(td, 'record.json')
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)
    return path


def test_a_serial_never_needs_a_record(td):
    for width in (None, 0, 1):
        ok, why, rec = cla.admit(width, path=os.path.join(td, 'missing.json'))
        assert ok, (width, why)
        assert rec is None and 'serial' in why, (width, why)
    print('  (a) width <= 1 is the serial route: admitted with no record: PASS')


def test_b_no_record_refuses(td):
    ok, why, _ = cla.admit(2, path=os.path.join(td, 'missing.json'))
    assert not ok and 'no acceptance record' in why, why
    broken = os.path.join(td, 'broken.json')
    with open(broken, 'w', encoding='utf-8') as handle:
        handle.write('{not json')
    ok, why, _ = cla.admit(2, path=broken)
    assert not ok and 'unreadable' in why, why
    print('  (b) missing / unparseable record refuses width 2 (fail closed): PASS')


def test_c_valid_record_admits_width_2(td):
    ok, why, rec = cla.admit(2, path=_write(td, VALID))
    assert ok, why
    assert rec['admitted_profiles'] == ['c1', 'c2'], rec
    assert 'Codex' in why and 'bsr-20260911T000000Z' in why, why
    print('  (c) a complete, evidence-bearing record admits width 2: PASS')


def test_d_width_3_refused_even_with_a_record(td):
    generous = copy.deepcopy(VALID)
    generous['max_admitted_width'] = 3
    generous['admitted_profiles'] = ['c1', 'c2', 'c5']
    path = _write(td, generous)
    ok, why, _ = cla.admit(3, path=path)
    assert not ok and 'exceeds the admitted maximum' in why, why
    # ...and the over-generous record does not even admit width 2: it is rejected whole,
    # never silently clamped.
    ok2, why2, _ = cla.admit(2, path=path)
    assert not ok2 and 'exceeds the code cap' in why2, why2
    assert cla.MAX_ADMITTED_WIDTH == 2, cla.MAX_ADMITTED_WIDTH
    print('  (d) width 3 refused by the code cap; an over-generous record is rejected '
          'whole, not clamped: PASS')


def test_e_every_missing_field_refuses(td):
    cases = [
        ('schema', lambda r: r.update({'schema': 'pwg.something_else.v9'})),
        ('serial block', lambda r: r.pop('serial_acceptance')),
        ('serial run_id', lambda r: r['serial_acceptance'].update({'run_id': '  '})),
        ('serial profile', lambda r: r['serial_acceptance'].pop('profile')),
        ('byte-identity', lambda r: r['serial_acceptance'].update(
            {'byte_identical_to_serial': 'yes'})),
        ('via-cohort-path missing', lambda r: r['serial_acceptance'].pop('via_cohort_path')),
        ('via-cohort-path not true', lambda r: r['serial_acceptance'].update(
            {'via_cohort_path': 'yes'})),
        ('serial evidence', lambda r: r['serial_acceptance'].update({'evidence': []})),
        ('reviewer block', lambda r: r.pop('reviewer_sign_off')),
        ('reviewer verdict', lambda r: r['reviewer_sign_off'].update({'verdict': 'INCONCLUSIVE'})),
        ('reviewer evidence', lambda r: r['reviewer_sign_off'].update({'evidence': ''})),
        ('width type', lambda r: r.update({'max_admitted_width': True})),
        ('profiles empty', lambda r: r.update({'admitted_profiles': []})),
        ('profiles dup', lambda r: r.update({'admitted_profiles': ['c1', 'c1']})),
        ('fleet narrower than width', lambda r: r.update({'admitted_profiles': ['c1']})),
    ]
    for label, mutate in cases:
        record = copy.deepcopy(VALID)
        mutate(record)
        ok, why, _ = cla.admit(2, path=_write(td, record))
        assert not ok, 'a record broken at [%s] was ADMITTED: %s' % (label, why)
    print('  (e) %d record defects each refuse width 2 (no "assume yes" branch): PASS'
          % len(cases))


def test_f_repo_record_path_and_cli(td):
    path = cla.record_path()
    assert path.endswith(os.path.join('pwg_ru', 'h4527', 'COHORT_LIVE_ACCEPTANCE.json')), path
    assert os.path.isabs(path), path
    # The CLI exit code IS the verdict: non-zero while the gate is shut.
    assert cla.main(['--width', '2', '--record', os.path.join(td, 'missing.json')]) == 1
    assert cla.main(['--width', '1', '--record', os.path.join(td, 'missing.json')]) == 0
    assert cla.main(['--width', '2', '--record', _write(td, VALID)]) == 0
    print('  (f) record_path points at pwg_ru/h4527; CLI exit code mirrors the verdict: PASS')


def main():
    with tempfile.TemporaryDirectory() as td:
        test_a_serial_never_needs_a_record(td)
        test_b_no_record_refuses(td)
        test_c_valid_record_admits_width_2(td)
        test_d_width_3_refused_even_with_a_record(td)
        test_e_every_missing_field_refuses(td)
        test_f_repo_record_path_and_cli(td)
    print('cohort_live_admission_selftest: 6 pins PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
