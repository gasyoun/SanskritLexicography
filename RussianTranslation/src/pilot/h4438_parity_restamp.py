#!/usr/bin/env python3
"""H4438 parity re-stamp: append the re-derivation note to the two ledger entries whose
hashed files H4438 touched, then refresh those hashes via lang_parity_check.py. Same class
as `h2254_parity_restamp.py` / `h2504_parity_restamp.py` / `h3144_parity_restamp.py` /
`h3500_parity_restamp.py` — meta-tooling kept as the receipt for a documented review. It
never translates, audits, gates, promotes, or touches the store; it edits LANG_PARITY.md
and shells out to lang_parity_check.py.

WHY BOTH VERDICTS STILL HOLD, re-derived rather than asserted.

`dhatup_palsule_enrichment_h1333` (SHARED) hashes `src/build_dhatup_palsule.py` and
`src/dhatup_palsule.py`, and H4438 changed both:

  * the builder now reads PWG's THIRD `DHĀTUP.` citation form (`<ls n="DHĀTUP.">4,13</ls>`),
    scopes `_HEAD_LEX` to markup before the citation, scopes the head/body discriminator,
    refuses a sole `<lex>` nominal head claimant, and builds `coordinate_ceilings()` from
    the spelled-out forms alone. Every one of those is a reading rule over the SOURCE
    dictionary's markup: the key stays the citation coordinate `gaṇa,serial` and the payload
    stays Sanskrit (the dhātu in SLP1/IAST plus Palsule's arthas and page siglum). No
    `--lang` path, no `de_raw`/`ru`/`en` field, and no target-language string is read or
    written anywhere in the file — `grep -c "lang" src/build_dhatup_palsule.py` finds no
    language branch to move.
  * `src/dhatup_palsule.py` drifted in its module docstring ONLY: the coverage header now
    reads 1573/1890 (83.2%) instead of 1465/1751 (83.7%), because the denominator changed
    when the third form was admitted. `palsule_for()` and every code path it owns are
    byte-identical.

So the entry's own argument — "the lookup key is the citation coordinate and the payload is
Sanskrit, called from the single pre-`--lang` path both editions share" — is untouched by
this change. A wider concordance is a wider concordance on both lanes.

`ed_bomb_ru_display_h2005` (INTENTIONAL-DIVERGENCE) hashes `src/pilot/ls_enrichment_selftest.py`,
which H4438 changed test-only: two ADDED tests (`test_dhatup_h4438_third_citation_form_refusals_are_published`,
`test_dhatup_h4438_sole_nominal_head_claimants_are_refused`) and their registration, `io`/`json`
imports, and re-pinned baseline numbers in existing dhatup tests. `test_h2005_ed_bomb_ru_display_not_resolve`
— the test that PINS this entry — is byte-identical, and no production module changed on
either lane. The RU-only `ed. Bomb.` → «Бомбейская ред.» display substitution is not
mentioned by anything H4438 wrote.

Run: python src/pilot/h4438_parity_restamp.py
"""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]          # .../RussianTranslation
LEDGER = ROOT / "LANG_PARITY.md"
CHECK = ROOT / "src" / "pilot" / "lang_parity_check.py"
BLOCK_OPEN = "```json lang_parity_ledger"
ENTRY_IDS = ("dhatup_palsule_enrichment_h1333", "ed_bomb_ru_display_h2005")

NOTE = (
    " H4438 re-stamp (09-09-2026, Opus 5 `claude-opus-5`; independent verifier required and "
    "delivered): re-derived, verdict stands. The drift is H4438, which admits PWG's THIRD "
    "`DHĀTUP.` citation form — `<ls n=\"DHĀTUP.\">4,13</ls>`, 320 occurrences over 270 "
    "coordinates, 141 cited no other way — and adds three scoping corrections plus a "
    "coordinate ceiling built from the spelled-out forms alone. Denominator 1751 → 1890, "
    "table 1465 → 1573 (131 added, 23 DELETED, 17 roots changed, 26 source-changed-only). "
    "Re-derived rather than asserted: every changed rule in `build_dhatup_palsule.py` reads "
    "the SOURCE dictionary's markup and keys on the citation coordinate with a Sanskrit-only "
    "payload; the file contains no `--lang` branch and touches no `ru`/`en`/`de_raw` field, "
    "so a wider concordance is wider on both lanes identically. `src/dhatup_palsule.py` "
    "drifted in its module docstring only (the coverage header, 1465/1751 → 1573/1890); "
    "`palsule_for()` is byte-identical. `src/pilot/ls_enrichment_selftest.py` drifted "
    "test-only — two ADDED tests and re-pinned baselines, with "
    "`test_h2005_ed_bomb_ru_display_not_resolve` itself byte-identical."
)


def load_block(text):
    start = text.index(BLOCK_OPEN) + len(BLOCK_OPEN)
    end = text.index("\n```", start)
    return start, end, json.loads(text[start:end])


def main():
    text = LEDGER.read_text(encoding="utf-8")
    start, end, entries = load_block(text)
    touched = []
    for e in entries:
        if e.get("id") in ENTRY_IDS:
            if "H4438 re-stamp" not in (e.get("note") or ""):
                e["note"] = (e.get("note") or "").rstrip() + NOTE
            touched.append(e["id"])
    body = json.dumps(entries, ensure_ascii=False, indent=2)
    LEDGER.write_text(text[:start] + "\n" + body + text[end:], encoding="utf-8", newline="\n")
    for entry_id in touched:
        subprocess.run([sys.executable, str(CHECK), "--update-hash", entry_id],
                       check=True, encoding="utf-8")
    r = subprocess.run([sys.executable, str(CHECK)], encoding="utf-8", capture_output=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-300:])
    print(f"re-stamped {len(touched)} entries: {', '.join(touched)}")
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
