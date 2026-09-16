#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4436_parity_restamp.py — the H4436 LANG_PARITY receipt (same class as
h4527_/h4527b_/h4528_/h4861_parity_restamp.py).

H4436 makes `profile_status`'s paid `profile:init` validation spawn append
`--safe-mode` exactly when `headless_worker.resolve_safe_mode({}, claude)` says
the paid lane would — the last paid spawn in `max_account_orchestrator.py` that
still carried the operator's full interactive profile. One new SHARED entry
(`profile_init_safe_mode_h4436`); every existing entry pinned to
`max_account_orchestrator.py` / `max_account_orchestrator_selftest.py` is
re-derived and re-stamped.

Written against the merge of origin/master `374182cb7` into `h4436-drain`: the
first refresh (`28b7403a4`, 16-09 06:00 +0300) pinned the branch's own file
content, but master had meanwhile taken H4527 #2245 (`0b5a800c1`) on both
files, so a PR-merge CI run would have compared the ledger against merged
content and stayed red. This receipt runs on the merged tree.

Usage (from RussianTranslation/): python src/pilot/h4436_parity_restamp.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr  # noqa: E402

STAMP = ('H4436 (16-09-2026, Fable 5.1 `claude-fable-5-1`): re-derived, verdict '
         'stands. The drift is the `profile:init` validation spawn in '
         '`profile_status` adopting the paid lane\'s `--safe-mode` via '
         '`headless_worker.resolve_safe_mode({}, claude)` (the same resolver '
         '`_probe_call` and `headless_worker.call` use) plus its selftest pin. '
         'Spawn-shape only: a fixed "Return exactly OK." prompt, no card, no '
         '`--lang` input, no target-language field read; RU and EN accounts are '
         'validated by the byte-identical spawn.')

NEW_ENTRY = {
    "id": "profile_init_safe_mode_h4436",
    "mechanism": ("Profile validation surface: `profile_status`'s paid "
                  "`profile:init` call appends `--safe-mode` exactly when "
                  "`headless_worker.resolve_safe_mode({}, claude)` (the paid "
                  "lane's own resolver) says the lane would -- the last paid "
                  "spawn in the module that still carried the operator's full "
                  "interactive profile"),
    "files": [
        "src/pilot/max_account_orchestrator.py",
        "src/pilot/max_account_orchestrator_selftest.py",
    ],
    "languages": ["ru", "en"],
    "verdict": "SHARED",
    "note": ("H4436 (16-09-2026, Fable 5.1 `claude-fable-5-1`). The validation "
             "call is language-free by construction: a fixed 'Return exactly OK.' "
             "prompt, no cards, no `--lang` input, so a Russian and an English "
             "account are validated by the byte-identical spawn. Same resolver as "
             "`_probe_call` (probe_safe_mode_h4527) and `headless_worker.call`, so "
             "the three cannot drift; an unsupporting CLI degrades identically on "
             "every lane. Selftest pin asserts equality with the resolver both ways."),
    "verified_sha256": {},
}


def main():
    return pr.restamp_receipt(STAMP, NEW_ENTRY)


if __name__ == '__main__':
    sys.exit(main())
