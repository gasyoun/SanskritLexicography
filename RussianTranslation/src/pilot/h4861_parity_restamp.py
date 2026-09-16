#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4861_parity_restamp.py — the H4861 LANG_PARITY re-derivation receipt (same class as
h4438_/h4528_parity_restamp.py).

H4861 made the h1339 offline bench hermetic for the cap-and-defer ledger: the bench drives
the REAL `coordinator prepare-batch --allow-over-cost`, whose cost gate called
`window_common.defer_monster` and appended dated `nominal:ADAna` / `nominal:ABIra` rows to
the TRACKED `src/pilot/deferred_monsters.jsonl` on every run (committed by accident in
H4528, #2201). `defer_monster` now honours a `PWG_DEFERRED_MONSTERS` path override per call
(unset = the tracked production ledger, unchanged), the bench points it into each run's
sandbox, and the bench fails if the tracked ledger's bytes change. Both touched files are
language-agnostic path plumbing, so every ledger entry that tracks one of them keeps its
SHARED verdict. This driver:

1. appends one dated re-derivation sentence to the note of every entry the check reports as
   drifted (never rewriting an existing sentence);
2. adds the H4861 entry itself (SHARED) if it is not there yet;
3. re-stamps each affected entry through `lang_parity_check.update_hash`, the tool's own
   writer, so the ledger keeps its canonical serialisation.

Idempotent: a second run finds no drift and no missing entry, and writes nothing.
Usage: python src/pilot/h4861_parity_restamp.py

H4408 follow-up: the stamp/ensure-entry/restamp mechanics this driver duplicated
with h4527_/h4527b_/h4528_parity_restamp.py now live once in
parity_restamp.restamp_receipt(); this file keeps only its own STAMP/NEW_ENTRY
receipt text.
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parity_restamp as pr  # noqa: E402

ENTRY_ID = 'deferred_monsters_ledger_sandbox_h4861'
STAMP = ('H4861 (14-09-2026, Opus 5 `claude-opus-5`): re-derived, SHARED stands. The drift is '
         'the `PWG_DEFERRED_MONSTERS` ledger-path override in `window_common.defer_monster` and '
         'the h1339 bench sandboxing it plus a tracked-ledger byte-identity guard. Path '
         'resolution only -- no language branch, no target-language field read; a Russian and '
         'an English window defer to the same ledger path.')
NEW_ENTRY = {
    'id': ENTRY_ID,
    'mechanism': ('Cap-and-defer ledger path override: `window_common.defer_monster` resolves '
                  '`path` -> `PWG_DEFERRED_MONSTERS` -> the tracked '
                  '`src/pilot/deferred_monsters.jsonl`, per call; h1339_offline_bench points the '
                  'override into each run\'s sandbox and fails the run if the tracked ledger '
                  'bytes change'),
    'files': [
        'src/pilot/window_common.py',
        'src/pilot/h1339_offline_bench.py',
    ],
    'languages': ['ru', 'en'],
    'verdict': 'SHARED',
    'note': ('H4861 (14-09-2026, Opus 5 `claude-opus-5`). The ledger path is chosen before and '
             'independently of the window language: `coordinator.prepare`\'s cost gate calls '
             '`defer_monster(target, ...)` identically for RU and EN windows, and the override '
             'is an environment path, not a lane switch. Production leaves it unset, so live '
             'deferrals still land in the tracked ledger. Tests: h1339_offline_bench --selftest '
             'check (5) (redirect lands in a temp ledger, tracked ledger byte-identical); the CI '
             'byte-identity bench run exits 1 if the tracked ledger moves (negative control: '
             'removing the sandbox env line fails the run with the signature still passing).'),
}


def main():
    return pr.restamp_receipt(STAMP, NEW_ENTRY)


if __name__ == '__main__':
    sys.exit(main())
