#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h5259b_parity_restamp.py — the H5259 follow-up LANG_PARITY re-derivation receipt (same class
as h4943_/h2254_/h2504_parity_restamp.py).

H5259 (#2306) repaired master after recovered PR #2305 appended 7 duplicate stale-hash keys
inside `headless_execution_manifest_h818.verified_sha256` — plain `json.loads` kept the LAST
copy, so the checker misreported them as 8 file drifts. This follow-up pass makes the ledger
loader refuse a repeated key at any level (`lang_parity_check.parse_ledger_json`, also used
by `--update-hash` and `parity_restamp.load_ledger`), pinned by the new hermetic
`window_selftest.test_lang_parity_ledger_refuses_duplicate_keys`. That pin is the only
change to a hashed file: `lang_parity_check.py` is coverage-exempt (hashed by no entry) and
`parity_restamp.py` is not language-aware. No new mechanism with a RU/EN surface was added,
so no new ledger entry — only the entries hashing `src/pilot/window_selftest.py` are
re-derived and re-stamped.

Usage: python src/pilot/h5259b_parity_restamp.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr  # noqa: E402

STAMP = ('H5259 follow-up (22-09-2026, Opus 5 `claude-opus-5`): re-derived, verdict stands. '
         '`src/pilot/window_selftest.py` drifted only by ONE added test-only pin, '
         '`test_lang_parity_ledger_refuses_duplicate_keys`, and its registration in the runner '
         'list. It exercises the ledger parser on a throwaway ledger in a temp dir; no existing '
         'test, constant or production path changed, no target-language field is read, and no '
         'RU/EN branch exists in it, so no verdict this entry holds can move.')


def main():
    ids = pr.drifted_ids()
    print('re-stamping %d re-derived parity entries' % len(ids))
    text, start, end, entries = pr.load_ledger()
    if pr.stamp_drifted(entries, ids, STAMP):
        pr.write_ledger(text, start, end, entries)
    return pr.finish(ids)


if __name__ == '__main__':
    sys.exit(main())
