#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h7864_parity_restamp.py — the H7864 LANG_PARITY re-derivation receipt (same class
as h5259b_/h4527_/h4943_parity_restamp.py).

H5263 (PR #2333) landed a 21-line delta to `src/pilot/headless_worker.py` — the advisory
NKRYa corpus-evidence block — without its policy-1 ledger act, drifting every entry
hashing that file (7 found by the checker). This receipt re-derives each drifted entry
(no verdict moves: the delta is prompt-assembly only, see STAMP), and ledgers the new
mechanism itself as `nkrya_prompt_evidence_block_h5263` (SHARED, de-facto RU-data only —
the homonym_locus_positional_h3751 shape), the classification the H5263 session owed.

Usage: python src/pilot/h7864_parity_restamp.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr

STAMP = ('H7864 (08-11-2026, GLM 5.3 `glm-5.3`): re-derived, verdict stands. '
         '`src/pilot/headless_worker.py` drifted only by the H5263 advisory NKRYa '
         'evidence block: a new `nkrya_block(inp)` helper (empty string when the manifest '
         'input carries no `nkrya` payload; lazy import of `src/nkrya_prompt_evidence.py`) '
         'appended after `inp[\'portrait\']` in `card_block`. Prompt assembly only — no '
         'fidelity count, manifest/execution-contract field, promote/store path, anchor '
         'repair or watchdog spawn argv is touched; the added lines read no target-language '
         'field and carry no RU/EN branch (the new module greps clean against the coverage '
         'scanner\'s LANG_SIGNAL set), and an absent `nkrya` input keeps the prompt '
         'byte-identical (pinned by `tests/test_nkrya_prompt_evidence.py`), so RU and EN '
         'cards assemble identically.')

NEW_ENTRY = {
    "id": "nkrya_prompt_evidence_block_h5263",
    "mechanism": (
        "Advisory NKRYa corpus-evidence block in the card prompt: when a manifest input "
        "carries an `nkrya` payload, `headless_worker.nkrya_block` renders it (lazily "
        "importing `src/nkrya_prompt_evidence.py`) and `card_block` appends the block "
        "after the portrait on the ONE shared prompt-assembly path both lanes drive; "
        "absent key => empty string => byte-identical prompt."),
    "files": [
        "src/nkrya_prompt_evidence.py",
        "src/pilot/headless_worker.py",
    ],
    "languages": ["ru", "en"],
    "verdict": "SHARED",
    "verified_sha256": {},
    "note": (
        "H7864 (08-11-2026, GLM 5.3 `glm-5.3`) — the policy-1 classification the H5263 "
        "session owed. Language-agnostic BY CONSTRUCTION: the block is prompt CONTENT "
        "delivered through a manifest input key, not code branching — `nkrya_block` reads "
        "no target-language field, `src/nkrya_prompt_evidence.py` greps clean against the "
        "coverage scanner's LANG_SIGNAL set, and an input without `nkrya` yields the "
        "byte-identical prompt (pinned by `tests/test_nkrya_prompt_evidence.py` and the "
        "H5263 prompt-evidence probe diff, `reports/H5263_prompt_evidence_diff.json`). "
        "De-facto RU-only TODAY exactly in the homonym_locus_positional_h3751 shape: only "
        "the c1 PWG-RU manifests carry `nkrya` inputs because the EN lane has no "
        "NKRYa-evidence manifest yet; the moment an EN manifest supplies the input the "
        "block reaches the EN lane with no port."),
}


def main():
    return pr.restamp_receipt(STAMP, NEW_ENTRY)


if __name__ == '__main__':
    sys.exit(main())
