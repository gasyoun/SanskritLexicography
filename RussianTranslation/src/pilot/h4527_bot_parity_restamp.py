#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4527_bot_parity_restamp.py — the H4527 (23-09-2026) LANG_PARITY re-derivation receipt
(same class as h5259b_/h4943_/h2254_parity_restamp.py).

H4527 (23-09-2026) changed three hashed production/test files: `prompt_rule_audit.py`
(`looks_foreign_literal` strips markup tags before classifying, so
`{%<bot>Hibiscus abelmoschus</bot>%}` is read as a Latin binomial kept verbatim, not as
untranslated German), `pwg_mask.py` (`looks_botany_binomial` strips tags the same way, so the
masker hides that span instead of sending it to the model as German — the gate and the masker
agree, per the independent critic) and `window_selftest.py` (four test-only pins). `bounded_staged_run.py` also refuses a missing
`--cwd` before run() — language-neutral argument validation. Only the entries whose hashed
files drifted are re-derived and re-stamped; no verdict moves.

Usage: python src/pilot/h4527_bot_parity_restamp.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr  # noqa: E402

STAMP = ('H4527 <bot> gate fix (23-09-2026, Opus 5.5 `claude-opus-5-5`): re-derived, verdict '
         'stands. `prompt_rule_audit.looks_foreign_literal` now strips markup tags (content '
         'kept) before classifying a braced SOURCE gloss, and `pwg_mask.looks_botany_binomial` '
         'does the same, so a PW `{%<bot>Latin binomial</bot>%}` is masked at stage 0 and read '
         'as foreign-literal by the residue gate instead of translated/flagged as German (5 705 '
         'PW source glosses, all strict binomials, 0 in PWG; receipt '
         '`h4527_bot_binomial_census.py`). Both read the German SOURCE span only, before any '
         '`--lang` branch, with no `lang` parameter: the masker change reaches the RU and EN '
         'lanes identically. `prompt_rule_audit` is imported by '
         'the RU auditor only, and the EN auditor already strips tags in `audit_window_en.prose()` '
         'before its word-list residue check, so the change closes a RU-side blind spot the EN '
         'side never had. `window_selftest.py` gained only test-only pins; `bounded_staged_run.py` '
         'refuses a missing `--cwd` before run(), identical for every lane. No new mechanism with a '
         'RU/EN surface, so no new ledger entry.')


def main():
    ids = pr.drifted_ids()
    print('re-stamping %d re-derived parity entries' % len(ids))
    text, start, end, entries = pr.load_ledger()
    if pr.stamp_drifted(entries, ids, STAMP):
        pr.write_ledger(text, start, end, entries)
    return pr.finish(ids)


if __name__ == '__main__':
    sys.exit(main())
