#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h5259c_parity_restamp.py — the second H5259 follow-up LANG_PARITY re-derivation receipt (same
class as h5259b_/h4943_/h2254_parity_restamp.py).

The H5259b verifier found a gap in the duplicate-KEY refusal: a merge/replay that re-appends a
WHOLE entry leaves two ledger entries with one `id` and no key repeated inside either, so it
went undetected (check() evaluated both copies; --update-hash re-stamped every match). This pass
makes `lang_parity_check.parse_ledger_json` refuse a repeated entry id in the ledger block, and
`load_ledger` / `parity_restamp.load_ledger` refuse a second ```json lang_parity_ledger fence
(only the first was ever read). Pinned by the new hermetic
`window_selftest.test_lang_parity_ledger_refuses_duplicate_entry_ids`. That pin is the only
change to a hashed file: `lang_parity_check.py` is coverage-exempt and `parity_restamp.py` is not
language-aware, so no new ledger entry — only the entries hashing `src/pilot/window_selftest.py`
are re-derived and re-stamped.

Usage: python src/pilot/h5259c_parity_restamp.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr  # noqa: E402

STAMP = ('H5259 follow-up c (22-09-2026, Opus 5.5 `claude-opus-5-5`): re-derived, verdict stands. '
         '`src/pilot/window_selftest.py` drifted only by ONE added test-only pin, '
         '`test_lang_parity_ledger_refuses_duplicate_entry_ids`, and its registration in the '
         'runner list. It exercises the ledger parser on throwaway ledgers in a temp dir; no '
         'existing test, constant or production path changed, no target-language field is read, '
         'and no RU/EN branch exists in it, so no verdict this entry holds can move.')


def main():
    ids = pr.drifted_ids()
    print('re-stamping %d re-derived parity entries' % len(ids))
    text, start, end, entries = pr.load_ledger()
    if pr.stamp_drifted(entries, ids, STAMP):
        pr.write_ledger(text, start, end, entries)
    return pr.finish(ids)


if __name__ == '__main__':
    sys.exit(main())
