#!/usr/bin/env python
"""h4342_requeue_sanloss_selftest.py — the documented SAN-LOSS restore puts back every row.

Hermetic (no store, no gatelogs, no network):

  python src/pilot/h4342_fixes/h4342_requeue_sanloss_selftest.py

H4530 verifier pass (15-09-2026): the restore matched on `(subcard, sense_tag)`, which is not
unique inside a subcard, so the live quarantine's `m_a~~h0_zz_pw03 / main` row — sharing its
key with two surviving `main` siblings — would have been skipped (dry-run: "3 row(s), 2 not
currently in the store"). These checks pin the content-matched replacement.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import h4342_requeue_sanloss as rq  # noqa: E402


def _row(subcard, tag, ru):
    return {"subcard": subcard, "sense_tag": tag, "ru": ru}


def fail(message):
    raise AssertionError(message)


def test_sibling_with_same_key_does_not_hide_a_quarantined_row():
    survivors = [_row("m_a~~h0_zz_pw03", "main", "мерить"),
                 _row("m_a~~h0_zz_pw03", "main", "измерять")]
    quarantined = [_row("m_a~~h0_zz_pw03", "main", "отмерять [SAN-LOSS]")]
    back = rq.rows_to_restore(quarantined, survivors)
    if back != quarantined:
        fail("a same-key sibling hid the quarantined row: %r" % back)


def test_restore_is_idempotent():
    quarantined = [_row("pat~~h0_zz_pw00", "1〉", "падать"),
                   _row("asvatantra~~h0_zz_pw", "1", "несамостоятельный")]
    store = [_row("pat~~h0_zz_pw00", "2〉", "лететь")]
    first = rq.rows_to_restore(quarantined, store)
    if first != quarantined:
        fail("first restore should return both rows, got %r" % first)
    if rq.rows_to_restore(quarantined, store + first):
        fail("a second restore must find every row already present")


def test_duplicate_rows_are_counted_not_collapsed():
    dup = _row("m_a~~h0_zz_pw03", "main", "мерить")
    back = rq.rows_to_restore([dup, dup], [dup])
    if back != [dup]:
        fail("two identical quarantined rows vs one in the store must restore one, got %r"
             % back)


def test_key_order_does_not_matter():
    stored = {"sense_tag": "main", "subcard": "m_a~~h0_zz_pw03", "ru": "мерить"}
    quarantined = {"subcard": "m_a~~h0_zz_pw03", "ru": "мерить", "sense_tag": "main"}
    if rq.rows_to_restore([quarantined], [stored]):
        fail("the same row with a different key order must read as present")


def main():
    tests = [test_sibling_with_same_key_does_not_hide_a_quarantined_row,
             test_restore_is_idempotent,
             test_duplicate_rows_are_counted_not_collapsed,
             test_key_order_does_not_matter]
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            failed += 1
            print("  FAIL %s — %s" % (test.__name__, exc))
        else:
            print("  PASS %s" % test.__name__)
    if failed:
        print("h4342 requeue restore selftest: FAIL (%d/%d)" % (failed, len(tests)))
        return 1
    print("h4342 requeue restore selftest: PASS (%d checks — content-matched restore, "
          "sibling keys, idempotence, duplicates)" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
