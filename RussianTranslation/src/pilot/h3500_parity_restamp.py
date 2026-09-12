#!/usr/bin/env python3
"""H3510 parity re-stamp after H3500: append the re-derivation note to every ledger entry
that hashes `src/promote_final_cards.py`, then refresh those hashes via lang_parity_check.py.
Same class as `h2254_parity_restamp.py` / `h2504_parity_restamp.py` / `h3144_parity_restamp.py`
— meta-tooling kept as the receipt for a documented review. It never translates, audits,
gates, promotes, or touches the store; it edits LANG_PARITY.md and shells out to
lang_parity_check.py.

WHY the mass re-stamp is honest here. H3500 (#1884, 25-08-2026) changed exactly one
function of `src/promote_final_cards.py`: `merge_store_rows` now collapses incoming
duplicate rows keyed on `(sense_tag, ru)` before comparison and lands from the collapsed
map (21 changed lines). The key names a RU field — which is precisely why this needed a
real re-derivation rather than a hash bump — but `promote_en.py` imports only `TN_RE`,
`UnrestoredPlaceholder`, `PromotionContractError`, `_fsynced_backup`, `_atomic_write_rows`,
`model_tier` and the defect-key helpers from promote_final_cards, never `merge_store_rows`
(measured: `grep -n merge_store_rows src/promote_en.py` → 0). The RU-only merge is inside
the RU-only promote script that the ledger already records as INTENTIONAL-DIVERGENCE
(`promotion_scripts_separate`), so nothing the EN lane executes changed. Every SHARED /
INTENTIONAL-DIVERGENCE verdict that merely references `promote_final_cards.py` still
holds; what moved is the file hash, not the parity semantics. The H3500 merge itself
landed with the ledger un-stamped, which is what turned the required
`RussianTranslation gates` check red on master.

Run: python src/pilot/h3500_parity_restamp.py

H4408: the ledger + checker mechanics live in parity_restamp.py; this receipt
keeps only its H3510 note and the drifted-file predicate.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr  # noqa: E402

DRIFTED = "src/promote_final_cards.py"

NOTE = (
    " H3510 re-stamp (25-08-2026, Fable 5 `claude-fable-5`): re-derived, verdict stands. "
    "The drift since this entry's stamp is H3500 (#1884): `merge_store_rows` collapses "
    "incoming duplicates keyed on `(sense_tag, ru)` and lands from the collapsed map "
    "(21 lines). The key names a RU field, so this was re-derived on the call graph, not "
    "asserted: `promote_en.py` never imports or calls `merge_store_rows` (0 hits), so the "
    "RU-only merge cannot reach the EN lane; the EN store writer still shares only the "
    "P9 `_atomic_write_rows` primitive. Nothing this entry tracks outside that function "
    "changed. Merged un-stamped, which turned the required gate red on master."
)


def main():
    text, start, end, entries = pr.load_ledger()
    touched = []
    for e in entries:
        if DRIFTED in (e.get("verified_sha256") or {}):
            if "H3510 re-stamp" not in (e.get("note") or ""):
                e["note"] = (e.get("note") or "").rstrip() + NOTE
            touched.append(e["id"])
    pr.write_ledger(text, start, end, entries)
    rc = pr.finish(touched)
    print(f"re-stamped {len(touched)} entries: {', '.join(touched)}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
