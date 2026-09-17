#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4436_parity_restamp.py — the H4436 LANG_PARITY re-derivation receipt (same class as
h4527_/h4528_/h4861_/h4943_parity_restamp.py).

H4436 (16/17-09-2026) closed the last paid spawn in `max_account_orchestrator.py` that still
carried the operator's full interactive profile: the `profile:init` validation call inside
`profile_status()` now appends `--safe-mode` exactly when
`headless_worker.resolve_safe_mode({}, claude)` (the paid lane's own resolver, default ON
since H2251) says the lane would -- the same posture the readiness probe took under H4527.
Its selftest gains one pin for that argv. The spawn carries no card and reads no
target-language field -- the RU and EN lanes validate one and the same profile -- so every
ledger entry that tracks one of the two touched files keeps its SHARED verdict. This driver:

1. appends one dated re-derivation sentence to the note of every entry the check reports as
   drifted (never rewriting an existing sentence);
2. adds the H4436 entry itself (SHARED) if it is not there yet;
3. re-stamps each affected entry through `lang_parity_check.update_hash`, the tool's own
   writer, so the ledger keeps its canonical serialisation.

Idempotent: a second run finds no drift and no missing entry, and writes nothing.

Usage: python src/pilot/h4436_parity_restamp.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parity_restamp as pr  # noqa: E402

ENTRY_ID = 'profile_init_safe_mode_h4436'

STAMP = ('H4436 (17-09-2026, Fable 5.1 `claude-fable-5-1`): re-derived, SHARED stands. The drift '
         'is the `profile:init` validation spawn in `profile_status()` adopting the paid lane\'s '
         '`--safe-mode` via `headless_worker.resolve_safe_mode({}, claude)`, plus its selftest '
         'pin. Spawn-shape only -- no prompt change, no language branch, no target-language '
         'field read; the RU and EN lanes validate one and the same profile.')

NEW_ENTRY = {
    'id': ENTRY_ID,
    'mechanism': ('Profile validation surface: the `profile:init` call in '
                  '`max_account_orchestrator.profile_status` appends `--safe-mode` exactly when '
                  '`headless_worker.resolve_safe_mode({}, claude)` (the paid lane\'s own resolver, '
                  'default ON since H2251) says the lane would -- derived, never a literal, so an '
                  'unsupporting CLI degrades exactly as the lane does'),
    'files': [
        'src/pilot/max_account_orchestrator.py',
        'src/pilot/max_account_orchestrator_selftest.py',
    ],
    'languages': ['ru', 'en'],
    'verdict': 'SHARED',
    'note': ('H4436 (17-09-2026, Fable 5.1 `claude-fable-5-1`). The validation call is '
             'language-free by construction: a fixed `Return exactly OK.` prompt, zero cards, and '
             'no `--lang` input, so a Russian and an English window are admitted by the '
             'byte-identical profile check. The flag is derived from the same resolver '
             '`headless_worker` uses for BOTH lanes\' generation spawns and that H4527 gave the '
             'readiness probe, so probe, validation and every lane they gate strip the same '
             'profile surface. Live evidence: gate-0 probe on c1 16-09-2026 02:46Z, 8 712 / 9 274 '
             'ms both `success` with `cli_safe_mode_effective` true, against the unflagged '
             '142 799 / 176 814 / 151 327 ms baseline (last a refusal citing the operator hook '
             'stack). Test: max_account_orchestrator_selftest "H4436 profile:init --safe-mode" '
             'pin (flag present when the resolver says ON, absent when the CLI lacks it).'),
}


def main():
    return pr.restamp_receipt(STAMP, NEW_ENTRY)


if __name__ == '__main__':
    sys.exit(main())
