#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4943_parity_restamp.py — the H4943 LANG_PARITY re-derivation receipt (same class as
h2254_/h2504_/h4438_parity_restamp.py).

H4943 is a pure extract-method structural refactor of `src/pilot/coordinator.py`'s
oversized functions (`claim`, `prepare`, `prepare_requeue`, `promote_ready`): each
function's existing branches were pulled into private helpers with the SAME argv order,
the SAME control flow, and the SAME exception/cleanup semantics -- zero logic changed,
verified via `window_selftest.py` (225/225, unchanged) and
`coordinator_hardening_selftest.py` (unchanged) run before and after the edit. No new
mechanism was introduced, so no new ledger entry is added here -- only the four existing
entries whose tracked file (`src/pilot/coordinator.py`) moved are re-derived and
re-stamped.

Usage: python src/pilot/h4943_parity_restamp.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr  # noqa: E402

STAMP = ('H4943 (16-09-2026, Sonnet 5 `claude-sonnet-5`): re-derived, SHARED stands. '
         'coordinator.py drifted solely because `claim`, `prepare`, `prepare_requeue` and '
         '`promote_ready` were split into private helpers (`_claim_target_*`, '
         '`_prepare_run_preflight`/`_prepare_run_gen_harness`, `_hydrate_pending_requeue`/'
         '`_write_requeue_defect_fshas`/`_execute_requeue_attempt`, '
         '`_validate_lease_for_promotion`) -- pure code motion, same argv order, same '
         'control flow, same exception/cleanup semantics. No target-language field is read '
         'anywhere in the moved code and no `--lang`/RU-EN branch is added or removed; '
         'window_selftest.py exercises `coordinator.prepare`, `coordinator.prepare_requeue` '
         'and `coordinator.promote_ready` directly and passed 225/225 unchanged before and '
         'after.')


def main():
    ids = pr.drifted_ids()
    print('re-stamping %d re-derived parity entries' % len(ids))
    text, start, end, entries = pr.load_ledger()
    if pr.stamp_drifted(entries, ids, STAMP):
        pr.write_ledger(text, start, end, entries)
    return pr.finish(ids)


if __name__ == '__main__':
    sys.exit(main())
