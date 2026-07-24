#!/usr/bin/env python
"""Selftests for promotion_receipt.py (H1554 Track B — VERIFICATION B1–B4).

Offline only. No live store, no coordinator, no paid generation.

    python src/pilot/promotion_receipt_selftest.py

B1 — schema v1 load/save round-trip
B2 — reconcile: promote_missing / skip_already_present / error_inconsistent fixtures
B3 — (review) no multi-profile live route change — this module is pure
B4 — this selftest green

Authored for H1554 by Grok 4.5 (model-lock override of Opus 4.8).
"""
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

import promotion_receipt as pr  # noqa: E402

FIXTURES = os.path.join(HERE, 'fixtures', 'cohort_scaffold')


def fail(message: str) -> None:
    raise AssertionError(message)


def load_fixture(name: str) -> dict:
    path = os.path.join(FIXTURES, name)
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# B1 — AttemptRunBinding + PromotionReceipt round-trip
# ---------------------------------------------------------------------------
def test_b1_schema_round_trip() -> None:
    binding = pr.AttemptRunBinding(
        run_id='run-rt-1',
        attempt_id='attempt-9',
        lease_id='lease-x',
    )
    receipt = pr.make_receipt(
        binding,
        keys_accepted=['k.1', 'k.2'],
        keys_rejected=['k.3'],
        store_path='tmp/store.jsonl',
        row_count_before=100,
        row_count_after=102,
        tm_rebuild=False,
        created_at='2026-07-23T10:00:00Z',
    )
    if receipt.schema != pr.SCHEMA_V1:
        fail('schema must be %r, got %r' % (pr.SCHEMA_V1, receipt.schema))
    if receipt.binding() != binding:
        fail('binding() must round-trip AttemptRunBinding fields')

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'lease-x' + pr.RECEIPT_FILENAME_SUFFIX)
        written = pr.write_receipt(path, receipt)
        if not os.path.isfile(written):
            fail('write_receipt did not create %s' % written)
        loaded = pr.load_receipt(written)
        if loaded.to_dict() != receipt.to_dict():
            fail('load_receipt != written receipt:\n  wrote=%s\n  load=%s'
                 % (receipt.to_dict(), loaded.to_dict()))

        # Directory loader picks the file by suffix.
        batch = pr.load_receipts(tmp)
        if len(batch) != 1 or batch[0].to_dict() != receipt.to_dict():
            fail('load_receipts must return the single written receipt')

    # Reject bad schema / empty ids / overlap / non-int counts.
    bad_cases = [
        ({'schema': 'nope'}, 'schema'),
        ({
            'schema': pr.SCHEMA_V1, 'run_id': '', 'attempt_id': 'a',
            'lease_id': 'l', 'keys_accepted': [], 'keys_rejected': [],
            'store_path': 's', 'row_count_before': 0, 'row_count_after': 0,
            'tm_rebuild': False, 'created_at': 't',
        }, 'run_id'),
        ({
            'schema': pr.SCHEMA_V1, 'run_id': 'r', 'attempt_id': 'a',
            'lease_id': 'l', 'keys_accepted': ['x'], 'keys_rejected': ['x'],
            'store_path': 's', 'row_count_before': 0, 'row_count_after': 1,
            'tm_rebuild': False, 'created_at': 't',
        }, 'overlap'),
        ({
            'schema': pr.SCHEMA_V1, 'run_id': 'r', 'attempt_id': 'a',
            'lease_id': 'l', 'keys_accepted': [], 'keys_rejected': [],
            'store_path': 's', 'row_count_before': True, 'row_count_after': 0,
            'tm_rebuild': False, 'created_at': 't',
        }, 'bool-as-int'),
    ]
    for payload, label in bad_cases:
        try:
            pr.receipt_from_mapping(payload)
        except ValueError:
            pass
        else:
            fail('expected ValueError for bad case %s: %r' % (label, payload))


# ---------------------------------------------------------------------------
# B2 — three cohort_scaffold fixtures
# ---------------------------------------------------------------------------
def _run_fixture(filename: str, expected_kind: str) -> pr.ReconcilePlan:
    fix = load_fixture(filename)
    if fix.get('expected_kind') != expected_kind:
        fail('%s fixture expected_kind drift: %r' % (filename, fix.get('expected_kind')))
    receipts = [pr.receipt_from_mapping(r) for r in fix['receipts']]
    plan = pr.reconcile_startup(receipts, fix['observed_store_keys'])
    return plan


def test_b2_promote_missing_fixture() -> None:
    plan = _run_fixture('promote_missing.json', pr.PROMOTE_MISSING)
    if len(plan.promote_missing) != 1:
        fail('promote_missing fixture: want 1 promote action, got %s'
             % plan.to_dict())
    if plan.skip_already_present or plan.error_inconsistent:
        fail('promote_missing fixture must not emit other buckets: %s'
             % plan.to_dict())
    action = plan.promote_missing[0]
    if list(action.keys) != ['dah.1', 'dah.2']:
        fail('promote_missing keys wrong: %s' % list(action.keys))
    if action.lease_id != 'lease-dah-w01':
        fail('promote_missing lease_id wrong: %s' % action.lease_id)


def test_b2_skip_already_present_fixture() -> None:
    plan = _run_fixture('skip_already_present.json', pr.SKIP_ALREADY_PRESENT)
    if len(plan.skip_already_present) != 2:
        fail('skip fixture: want 2 skip actions (double receipt), got %s'
             % plan.to_dict())
    if plan.promote_missing or plan.error_inconsistent:
        fail('skip fixture must not emit other buckets: %s' % plan.to_dict())
    for action in plan.skip_already_present:
        if list(action.keys) != ['dah.1', 'dah.2']:
            fail('skip keys wrong: %s' % list(action.keys))


def test_b2_error_inconsistent_fixture() -> None:
    plan = _run_fixture('error_inconsistent.json', pr.ERROR_INCONSISTENT)
    if len(plan.error_inconsistent) != 2:
        fail('error fixture: want 2 error actions, got %s' % plan.to_dict())
    if plan.promote_missing or plan.skip_already_present:
        fail('error fixture must not emit other buckets: %s' % plan.to_dict())
    reasons = ' | '.join(a.reason for a in plan.error_inconsistent)
    if 'partial presence' not in reasons:
        fail('error fixture must include partial-presence reason: %s' % reasons)
    if 'row_count delta' not in reasons:
        fail('error fixture must include row_count delta reason: %s' % reasons)


def test_b2_fixture_files_present() -> None:
    required = (
        'promote_missing.json',
        'skip_already_present.json',
        'error_inconsistent.json',
    )
    missing = [n for n in required if not os.path.isfile(os.path.join(FIXTURES, n))]
    if missing:
        fail('missing cohort_scaffold fixtures: %s' % missing)


# ---------------------------------------------------------------------------
# Extra pure pins (still offline)
# ---------------------------------------------------------------------------
def test_empty_accept_skips() -> None:
    receipt = pr.make_receipt(
        pr.AttemptRunBinding('r', 'a', 'l'),
        keys_accepted=[],
        store_path='s',
        row_count_before=5,
        row_count_after=5,
        created_at='t',
    )
    plan = pr.reconcile_startup([receipt], ['anything'])
    if len(plan.skip_already_present) != 1:
        fail('empty accept should skip, got %s' % plan.to_dict())


def main() -> int:
    tests = [
        test_b1_schema_round_trip,
        test_b2_fixture_files_present,
        test_b2_promote_missing_fixture,
        test_b2_skip_already_present_fixture,
        test_b2_error_inconsistent_fixture,
        test_empty_accept_skips,
    ]
    failed = 0
    for test in tests:
        name = test.__name__
        try:
            test()
        except Exception as exc:
            failed += 1
            print('FAIL %s: %s' % (name, exc))
        else:
            print('ok   %s' % name)
    print()
    if failed:
        print('%d/%d failed' % (failed, len(tests)))
        return 1
    print('%d/%d passed (H1554 Track B selftest green)' % (len(tests), len(tests)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
