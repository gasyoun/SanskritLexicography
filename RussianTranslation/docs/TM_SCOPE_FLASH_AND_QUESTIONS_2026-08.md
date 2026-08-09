# Translation Memory — Flash role, doc index, and question lists

_Created: 08-08-2026 · Last updated: 08-08-2026_

One-page answers to: (1) what R4.3a / R4.1 ban Flash from doing, (2) where the TM-only docs live, (3) written vs oral coverage, (4) questions the TM **will** / **will not** / **could later** answer.

Not a new charter — indexes decisions already locked in H215 / D1–D14 / pubgrade plan.

---

## 1. Do the anti-patterns ban Flash from all TM work?

**No.** They ban two *roles*, not Flash as a tool near TM.

| Anti-pattern (DeepSeek lane map) | Meaning | Flash still may… |
|---|---|---|
| **Flash writes directly to TM** (fence **R4.3a**) | Only the **promoter path** writes the TM store / TM sidecars | **Read** TM (exact + fuzzy rank); emit **read-only** `tm_fuzzy_hits` in prep; never set `store_write` / `tm_fence.may_write` |
| **Flash sole judge for auto-promote** (H1210 + halt **R4.1**) | Flash alone cannot decide “ship to store” | Draft / prep / rank under an Opus controller or promoter; production role only after pre-registered A/B win (R2.3) |

**R4.3** (multilane plan, full fence text): TM store written **ONLY** by the promoter path; plus csl-orig, runner isolation, profile-dir rules — see [PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md).

**Lane map shape:**

```text
[2] Flash PREP  →  TM fuzzy rank (READ-ONLY hits)
[3] Router
[4] promoter + TM FENCE  ← write path; not Flash
```

Canonical short form: **rank proposes reuse; fence blocks prep/Flash from writing.**

---

## 2. TM-only (or TM-primary) documents

| Doc | Role |
|---|---|
| [TRANSLATION_MEMORY_DECISIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DECISIONS.md) | **Charter** D1–D14 (auto-reuse, fuzzy advisory, MW ban on RU prompts, speed priority, …) |
| [TRANSLATION_MEMORY_DATASHEET.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md) | Bender/Friedman + Gebru datasheet — composition, rights, **intended / forbidden uses** |
| [PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md) | Finish-H215 plan index (tracks A/B/C, oral rulings) |
| [ROADMAP_RussianTranslation_pubgrade_tm_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_pubgrade_tm_2026H2.md) | Wave-1 deliverables A1–A6 · B1–B5 · C1–C5 + non-goals + later waves |
| [ARCHITECTURE_RussianTranslation_pubgrade_tm_oral.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_pubgrade_tm_oral.md) | Component map, written/oral data model, rights partition |
| [IMPLEMENTATION_RussianTranslation_pubgrade_tm_oral.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pubgrade_tm_oral.md) | Ordered build steps |
| [VERIFICATION_RussianTranslation_pubgrade_tm_oral.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_pubgrade_tm_oral.md) | Gates / risks |
| [ACL_TM_CROSSWALK_MEMO.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ACL_TM_CROSSWALK_MEMO.md) | ACL methods + TM-H1…H7 hypotheses |
| [src/BUILD_TMX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/BUILD_TMX.md) | Operator build of TMX / L0 / grader |
| [src/pilot/translation_memory.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py) | Content-addressed exact/fragment TM (code + module docstring) |
| [schemas/translation_memory.schema.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/translation_memory.schema.json) | Publication contract v1 |
| [H215 handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md) | Owning programme handoff |

Flash-lane policy (not TM-only, but write fence): [DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md](https://github.com/gasyoun/Uprava/blob/main/docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md).

---

## 3. Written and oral corpus — will the TM hold both?

**Yes, by plan** — not all layers are live yet.

| Pool | Status (datasheet / plan) | In TM? |
|---|---|---|
| **Written — PWG DE→RU exact/fragment** | Built / growing (publication slice ~2.4k records; full store larger) | Yes — primary exact TM |
| **Written — Samudra parallel (1.09M word alignments)** | L0/L1 layers; full bilingual `corpus_lexicon` **local/gitignored** (grey rights) | Structure + derived yes; RU surface text **not** in public bundle until clearance |
| **Oral** (own talks · Systema · third-party · public video) | Track **B** (B1–B5): schema + converter + align + grade + `modality=oral` | **Planned**; oral alone caps grade **B**, grade **A** only if a written translation agrees (19-07 ruling) |
| **ASR from raw audio** | **Out** — R2.3: user provides transcripts, no Whisper | Never as planned |

Aligner scope R4.2: **one** LaBSE/Vecalign for written prose **and** oral.

---

## 4. Questions the TM **will** answer (intended)

From datasheet §E + DECISIONS D1–D2 + plan goals:

| # | Question | Mechanism |
|---|---|---|
| Q1 | Has this **exact** masked German/source already been translated (byte-identical content address)? | Exact card/fragment TM (`lookup` by sha) |
| Q2 | May draft windows **auto-reuse** that hit? | Only if machine-gated exact + D1; human-reviewed outranks machine (D8) |
| Q3 | What **wording suggestions** exist for similar German / Sanskrit / semantic tags? | Fuzzy/suggestion TM — **advisory only** (D2); never pre-resolves cards |
| Q4 | What is the Sa→Ru **term gloss** for this headword (curated)? | Terminology dataset D13 (not raw MW English — D9) |
| Q5 | What is the **provenance / gate / trust** of a reused unit? | Publication schema fields |
| Q6 | Does graded TM-as-context improve draft quality/speed? | Measurement A6 (Neural Fuzzy Repair framing) — in-scope experiment |
| Q7 | (Structure only) Which Sa content-words align where in the parallel corpus? | `corpus_tm/derived_only` (no RU text in public bundle) |

Prep Flash path reuses Q1–Q3 as **read-only** `tm_fuzzy_hits` (rank), never as write.

---

## 5. Questions the TM **will not** answer (explicit non-goals / forbidden uses)

| # | Question / use | Where forbidden |
|---|---|---|
| N1 | “Did Flash alone decide this card is shippable?” | R4.1 + map anti-pattern |
| N2 | “Can Flash write this into TM?” | R4.3a |
| N3 | “What does the Russian of work X say?” for grey Samudra RU in the **public** bundle | Datasheet B2/E — RU stripped |
| N4 | “Is `needs_review` clearance?” | Datasheet E |
| N5 | “What does MW English say as RU evidence?” | D4 / D9 |
| N6 | “Run kNN-MT / retrieval-augmented decoding in the engine this wave?” | ROADMAP non-goals; later W2 if A6 wins |
| N7 | “Model this as OntoLex/TEI?” | Plan R1.3 → csl-standards |
| N8 | “Ingest GRETIL TEI prose internals here?” | SamudraManthanam H308 owns |
| N9 | “Auto-publish / mint DOI / flip Pages?” | Plan fence + datasheet F |
| N10 | “Transcribe this video with ASR into TM?” | R2.3 |
| N11 | “Treat fuzzy hit as exact reuse?” | D2 |

---

## 6. Questions it **could** answer later if minted / after wave gates

These are **not** open `@DECIDE`s; they are roadmap **later waves** or residual handoffs. Minting a handoff (or finishing the named A/B/C unit) is the unlock.

| # | Future question | Unlock |
|---|---|---|
| F1 | Does retrieval-augmented decoding (kNN-MT / in-loop Neural Fuzzy Repair) beat draft-without-TM? | W2 after A6 measurement |
| F2 | What is diachronic gloss-density over `corpus_strata`? | W2 (TM-H4 / Viz-1) |
| F3 | Unsupervised drift-audit of TM vs corpus (VecMap channel)? | W2 (TM-H7) |
| F4 | Full public bilingual release of currently grey parallel works? | Per-source clearance + human publish gate (C5/W3) |
| F5 | Oral units at grade A without a written twin? | Explicit re-rule (today: oral alone ≤ B) |
| F6 | Flash as **production** draft-lane Q1–Q2 generator into controller? | E1 win on Flash 0731 (map R2.3 / R3.4) — still not TM write |
| F7 | Flash as bulk labeler for oral/align/mined tiers? | Allowed as prep/label role when not sole promote judge; separate A/B if it feeds auto-promote |
| F8 | Separate terminology DOI live? | C1 populate + human publish path (D13) |

---

## 7. How to widen and deepen (practical)

| Axis | Widen | Deepen |
|---|---|---|
| **Coverage** | More PWG heads through promoter (not Flash→TM); more Samudra works once rights clear | Sense-level / fragment TM quality; last-audit denylist (OPT-7) |
| **Modalities** | Finish Track B oral ingest | Oral grade caps + written-agree path to A |
| **Quality** | Track A gold + COMET-QE + align gates | Per-pair confidence instead of flat thresholds |
| **Engine use** | Prep fuzzy rank + exact reuse (today) | A6 measure → optional W2 retrieval decoding |
| **Cheap lanes** | Flash PREP rank + draft under controller | Never Flash sole promote; never Flash TM write |

---

## 8. Provenance

Assembled 08-08-2026 (Grok 4.5 `grok-4.5`) from the linked charters after a Flash PREP / R4.3a discussion — so the three question lists are not chat-only.

_Dr. Mārcis Gasūns_
