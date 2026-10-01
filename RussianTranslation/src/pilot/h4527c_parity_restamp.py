#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4527c_parity_restamp.py — the third H4527 LANG_PARITY re-derivation receipt (same class as
h4527_/h4527b_/h4528_/h4861_parity_restamp.py, mechanics in `parity_restamp.restamp_receipt`).

H4527 pass 17-09-2026 added `--require-senses N` to `no_pwg_scale_plan.py`: the planner now
prepares only sub-cards whose input sidecars declare at least N top-level SOURCE senses, and omits
a head whose eligible sub-cards are all sense-poor, exactly as it already omits a fully-blocked
head. The count is read from the portrait sidecar's stamped `source_senses`, falling back to
`sense_count.count_source_senses` over the raw source blob — both of which describe the GERMAN/
Sanskrit source entry, before any target field exists. There is no `lang` parameter anywhere on
the new path, no RU/EN branch and no target-language field read, so a Russian and an English drain
plan the identical window from the identical sidecars; every drifted entry keeps its verdict and
only the file hash moved. This driver stamps that re-derivation onto each drifted entry, adds the
gate's own entry, and re-stamps through `lang_parity_check`'s own writer.

ONE-SHOT RECEIPT: it stamps whatever the check reports as drifted, so running it after some later,
unrelated change would mis-attribute that drift to this pass. Re-derive later drift with its own
receipt, never this one.
Usage: python src/pilot/h4527c_parity_restamp.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parity_restamp as pr  # noqa: E402

ENTRY_ID = 'no_pwg_sense_gate_h4527'
STAMP = ('H4527 pass 7 (17-09-2026, Opus 5 `claude-opus-5`): re-derived, verdict stands. The drift '
         'is the planner\'s new `--require-senses N` sub-card gate (`no_pwg_scale_plan.py`) and its '
         'selftest pin (`test_no_pwg_require_senses_gate`). The gate counts SOURCE senses from the '
         'input sidecars (portrait stamp, else `sense_count.count_source_senses` over the raw '
         'source blob) before any card exists; no `lang` parameter, no target-language field, no '
         'RU/EN branch. Off by default (0), so the historical planning path is unchanged.')
NEW_ENTRY = {
    'id': ENTRY_ID,
    'mechanism': ('Planner sub-card admission: `no_pwg_scale_plan --require-senses N` keeps only '
                  'sub-cards whose input sidecars declare N+ top-level source senses '
                  '(`subcard_source_senses` / `filter_sense_poor_subcards`) and omits a head whose '
                  'eligible sub-cards are all sense-poor'),
    'files': [
        'src/pilot/no_pwg_scale_plan.py',
        'src/pilot/window_selftest.py',
    ],
    'languages': ['ru', 'en'],
    'verdict': 'SHARED',
    'note': ('H4527 (17-09-2026, Opus 5 `claude-opus-5`). Why it exists: `agent_budget` derives a '
             'card\'s self-heal pool from its sense groups, so a zero-sense sub-card runs with '
             '`max_heal_agents: 0` — one paid shot and no repair lane; the 16-09-2026 live '
             'acceptance window spent a call on exactly that topology (`asa_mskfta~~h0_zz_nws00`, '
             '`senses: []`) and came back null, and the 17-09 census showed the zero is structural '
             'for the whole `~~h0_zz_nws00` class (0 of 10 declare a sense). Parity: both readings '
             'of the count describe the source entry — the portrait sidecar\'s stamped '
             '`source_senses` and `sense_count.count_source_senses`, which counts line-opening '
             'top-level ordinals in the raw German source — and both run before generation, so the '
             'RU and EN lanes admit the identical sub-cards. Strictly narrowing: an unprovable '
             'count (None) is skipped rather than admitted, and nothing is written to the residual '
             'registry. Test: `test_no_pwg_require_senses_gate`.'),
}


def main():
    return pr.restamp_receipt(STAMP, NEW_ENTRY)


if __name__ == '__main__':
    sys.exit(main())
