# H3500 — pwg_ru TM defect-class fixes: before/after report

_Created: 25-08-2026 · Last updated: 25-08-2026_

Executor: OxAlpha (`opencode/x-preview-f-free`) · Inputs RESTRICTED (bench corpus local-only), fixes lane-internal

## Scope

Fix the three pwg_ru TM defect classes surfaced by the [H3456 blinded benchmark](https://github.com/gasyoun/kosha/blob/main/docs/PWGRU_VS_AKSHARA_MT_BENCHMARK_24.08.26.md) ([kosha PR #432](https://github.com/gasyoun/kosha/pull/432)) before the next c1 drain window (MG confirmed drain paused 25-08-2026).

## What the measurement actually showed

Re-running a tag-aware detector over the canonical store (`src/pwg_ru_translated.jsonl`, 11,603 rows) **reclassified most of the benchmark's impressions**:

| H3456 impression | Measured reality |
|---|---|
| «untranslated `N. pr.`» | `<ab>N. pr.</ab>` is render-time translated (`RU_MAP['N. pr.'] = 'имя собств.'`); the benchmark stripped tags before judging. **False positive at store level.** |
| «`s. см.`/`ср. vgl.` doubling» | 0 double-renderings exist; 335 of 336 `vgl.` tokens sit inside `<ab>` (render-translated). **1 true free-floating residue** (`Bid/_bid~~h0_zz_sch`). |
| «duplicate-line artifacts, worst B090 (`vasin`) whole entry twice» | Confirmed, two distinct mechanisms: (a) **5 byte-identical duplicate rows** in the store (same key1+subcard+sense_tag+ru); (b) **42 entries** where PWG legitimately lists one gloss under two homograph sections (`vAsin`≡`vaSin`; `DA` anusam under h0_80+h6_23) — naive per-key1 joins double them. |
| «[NWS]/[Reg] enrichment unflagged» | 13 rows, all `[Buddh]` BHSD advisory spans from one batch (`nominal_w1_100small`), zero provenance markers. Confirmed. |

## Fixes shipped (this PR)

1. **`src/h3500_defect_scan.py`** — the class detector (render-time-aware); `--check` gate mode exits 1 on any class1a/class2-vgl/class3 hit.
2. **`src/h3500_store_repair.py`** — surgical repair: keep-best dedupe of byte-identical `(key1, subcard, sense_tag, ru)` rows; bare-`vgl.` → `ср.` (H2849 precedent, tagged tokens untouched); additive `advisory_enrichment: ["bhsd"]` marker on the 13 advisory rows. Dry-run default; mass-drop guard (0.006% actual vs 1% ceiling); JSONL evidence ledger.
3. **`src/pwg_ru_entry_join.py`** — the canonical entry assembler: collapses identical normalised blocks at join time (first occurrence wins), never merges distinct senses. **B090 proof: naive join 207 chars → assembler 103 chars** for `vasin`.
4. **`promote_final_cards.py` guard** — `merge_store_rows` collapsed incoming duplicates by `(sense_tag, ru)` keep-best AND now lands from the collapsed set (previously the tail re-appended raw `promoted_rows`, the origin of the byte-identical copies).

## Applied results (both stores, identical deltas)

Store A: SanskritLexicography `RussianTranslation/src/pwg_ru_translated.jsonl` (gitignored, backup `.h3500-backup-25-08`)
Store B: [pwg-ru-data `tm/pwg_ru_translated.jsonl`](https://github.com/gasyoun/pwg-ru-data/blob/main/tm/pwg_ru_translated.jsonl) (committed, repaired in its own PR)

| metric | before | after |
|---|---|---|
| rows | 11,603 | 11,598 (−5 duplicates) |
| class1a duplicate excess | 5 (4 clusters) | **0** |
| class2 free-floating `vgl.` | 1 | **0** |
| class3 unflagged advisory rows | 13 | **0** (13 × `advisory_enrichment:["bhsd"]`) |
| content-mass drop | — | 0.0059% (guard ceiling 1%) |
| `h3500_defect_scan.py --check` | FAIL | **OK** |

Spot-check (probe vs backups): all 5 dropped clusters verified as exact `(tag, ru)` multiplicity reduction; 13/13 marker rows retain their `[Buddh]` span; the `vgl.` row diff is the single token.

## Deliberately NOT auto-fixed (manual follow-ups)

1. **3 English-genitive prose leaks** inside `<is>` spans (need per-row Russian rewording, not mechanical edit): `di_s~~h0_22_samud` («Arjuna's 489.»), `su~~h1_00_pwg00` («Savitar's воздействии»), `vad~~h0_08_anu` («Indra's городу»). `Kuhn's Z.` inside `<ls>` is a citation and stays.
2. **53 degenerate-tag copies** (identical ru under different zz-key sense_tags, e.g. `ud-prefix-3` vs `sam-prefix-3`) — source-faithful rows with noisy machine tags; retagging is a lane-level decision, not a repair.
3. **42 cross-subcard homograph blocks** — kept in the store (source fidelity); any consumer assembling entry-level text must use [`pwg_ru_entry_join.assemble_entry`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_entry_join.py) instead of a bare join. The H3456 benchmark builder should be rerun through it if the benchmark is ever refreshed.

## Tests

`pytest RussianTranslation/tests/test_h3500_tm_defect_fix.py` — 8 passed (entry-join collapse, merge-guard, repair behaviour incl. cross-tag survival, scanner predicate).

_Dr. Mārcis Gasūns_
