# H3685 — akshara close-out tail: 3 genitive reformulations + homograph block reconciliation

_Created: 29-08-2026 · Last updated: 29-08-2026_

Executor: OxAlpha tier label (run under [H3688](https://github.com/gasyoun/Uprava/blob/main/handoffs/) — any executor may run any tier). Finishes the tail parked by the witty-cabin OpenCode session and recorded verbatim in the [H3500 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3500_PWGRU_TM_DEFECT_FIX_25-08-2026.md) "Deliberately NOT auto-fixed" section.

## 1. Three genitive prose leaks — before/after

The [H3500 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3500_PWGRU_TM_DEFECT_FIX_25-08-2026.md) left these 3 rows unrepaired deliberately: the German source (`de`, never touched) uses a genuine German genitive apostrophe-s ("Arjuna's", "Savitar's", "Indra's"), and the translation pass had left that specific span untranslated instead of rendering a Russian genitive. Each rewording below is re-derived from the row's own `de` field (never hand-invented):

| row (`key1`/`subcard`) | German source (`de`, untouched) | Before (`ru`) | After (`ru`) |
|---|---|---|---|
| `diS` / `di_s~~h0_22_samud` | "…wodurch sie die Schwiegertochter Arjuna's wurde, 489." | "…стала невесткой\n\<is\>Arjuna's\</is\> 489." | "…стала невесткой \<is\>Арджуны\</is\>, 489." |
| `su` / `su~~h1_00_pwg00` | "(von Savitar's Wirkung)" | "(о \<is\>Savitar's\</is\> воздействии)" | "(о воздействии \<is\>Савитара\</is\>)" |
| `vad` / `vad~~h0_08_anu` | "Laṅkā erklang wie Indra's Stadt" | "{%звучал подобно%} \<is\>Indra's\</is\> {%городу%}" | "{%звучал подобно%} {%городу%} \<is\>Индры\</is\>" |

Applied via [`src/h3685_genitive_fix.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3685_genitive_fix.py) — exact-substring match against the known BEFORE text (refuses on drift rather than fuzzy-patching), atomic write, ledger at [`reports/H3685_genitive_fix_ledger.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3685_genitive_fix_ledger.jsonl). Applied to the canonical committed store, [pwg-ru-data `tm/pwg_ru_translated.jsonl`](https://github.com/gasyoun/pwg-ru-data/blob/main/tm/pwg_ru_translated.jsonl) (11,462 rows, matching the store-lineage base H3690 step 0 reconciled). Re-running [`h3500_defect_scan.py --json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3500_defect_scan.py) confirms `class2_is_genitive_leaks` no longer lists any of the 3 rows.

**Store A not touched.** SanskritLexicography's local gitignored `RussianTranslation/src/pwg_ru_translated.jsonl` currently holds 11,519 rows (Windows-box surface) vs pwg-ru-data's 11,462 (Mac-reconciled base) — an active divergence under [H3690](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3690-OxAlpha_SanskritLexicography_lane-a-7keys-paid-fire_29.08.26.md) step 0. Editing Store A now would collide with that in-flight reconciliation; re-run `h3685_genitive_fix.py` on Store A once H3690 lands and the two stores agree on a base.

## 2. Cross-subcard homograph blocks — count reconciled, not "generated"

The mission text (inherited from the witty-cabin session's parked note) names **42** "information homograph blocks." That number is the [H3500 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3500_PWGRU_TM_DEFECT_FIX_25-08-2026.md)'s snapshot from **25-08-2026** against an 11,603/11,598-row store. These blocks are not a defect to "generate" or "repair" — H3500 already ruled them source-faithful (PWG legitimately lists one gloss under two homograph sections, e.g. `vAsin`≡`vaSin`) and assigned the fix to the entry assembler, [`pwg_ru_entry_join.assemble_entry`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_entry_join.py), not to the store.

Re-running the scanner's `class1b` measurement against the **current** store (11,462 rows, post H3591/H3627/H3690-step-0) gives **34** blocks, not 42 — the store has shrunk by 141 rows since the H3500 snapshot (H3591 restored 309 drifted rows into the mirror, H3627 refreshed the mirror, H3690 reconciled the lineage base), which changed which rows collide. Full enumeration (key1 + colliding subcards, schema-validity check per contributing row): [`reports/H3685_homograph_blocks_29-08-2026.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3685_homograph_blocks_29-08-2026.json), produced by [`src/h3685_homograph_blocks_report.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3685_homograph_blocks_report.py). All 34 blocks pass the schema check (every contributing row carries non-empty `key1`/`subcard`/`sense_tag`/`ru`) and none require a store edit — `assemble_entry` already collapses them at join time (verified by the existing B090 selftest/regression).

**Acceptance interpretation:** "42 blocks present and schema-valid" is read as "the class1b population is enumerated, schema-checked, and reconciled against the live store" rather than a literal count match — the literal 42 no longer exists in the live store and re-creating it would mean reverting legitimate cleanup from H3591/H3627/H3690.

## 3. Residual found, not in scope here

Re-scanning the current store surfaced **7 additional** `class2_is_genitive_leaks` beyond the 3 named in this handoff — `Śiva's` (×5: `_bid~~h0_23_sam`, `di_s~~h0_19_sam_a`, `di_s~~h1_00_pwg00`, `ji~~h0_23_vi`, `muc~~h0_28_vi_1`), `Bṛhaspati's` (`_d_a~~h1_00_pwg00`), `Viṣṇu's` (`vi_s~~h0_39_pra_0`) — introduced or newly measured since the H3500/H3685 mission text was written. Left unfixed: this handoff's acceptance names exactly 3 rows and fixing the extra 7 without a scoped mission risks the same "hand-invent inflection" mistake the mission explicitly warns against. Recorded here for the next tail handoff to pick up.

## 4. Tests

`pytest RussianTranslation/tests/test_h3685_genitive_fix.py RussianTranslation/tests/test_h3500_tm_defect_fix.py` — 12 passed. `h3500_defect_scan.py --check` on the repaired store: `class1a=0`, `class2 bare vgl=0`, `class3 unflagged=0` (class1b stays non-gate-failing by design).

_Dr. Mārcis Gasūns_
