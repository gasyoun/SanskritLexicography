# MW missing intended entries vs Böhtlingk's Nachträge — AI trial run

_Created: 14-09-2026 · Last updated: 14-09-2026_

**Question source:** [csl-corrections#119, comment 4359094604](https://github.com/sanskrit-lexicon/csl-corrections/issues/119#issuecomment-4359094604) (Andhrabharati, 01-05-2026): MW's annexure (MW99) carries the Nachträge entry `kārāpaka` but **skipped `kāritra`** (phonetically close to `kārayitṛ` "agent"; BHS sense) — *"I recall even suggesting (once) to add such entries by comparing MW with PWG/pwk."* Trial question: **can AI do that comparison?**

**Verdict of the trial: yes, mechanically — 49 s wall-clock for the whole cross-dictionary pass, 1,751 absent-entry candidates, of which 547 sit in the strong "annexure-neighbour" pattern (the `kārāpaka`-next-to-`kāritra` shape). The bottleneck is not recall but precision: the fuzzy tier must be human-reviewed, and MW does not promise full PWK coverage.**

## 0 · Relationship to [H4837](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4837-OxAlpha_SanskritLexicography_mw-missing-pw-nachtrag-adjudication_14.09.26.md) — read this first

[H4837](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4837-OxAlpha_SanskritLexicography_mw-missing-pw-nachtrag-adjudication_14.09.26.md) (minted 14-09-2026, OxAlpha, hard, ~240 min) is the **adjudication unit of record** for this same question, with a **wider scope**: `pw.txt` + `pwkvn.txt`, `<k2>*` starred Nachträge headers across all layers → **3,024** headwords missing from MW, tiered by cross-dictionary corroboration (A 618 / B 1,427 / C 979; 273 cite Mahāvyutpatti). Its artifacts (`MW-missing-PW-Nachtrag-candidates-14-09-2026.md/.tsv`, `pw_nachtrag_vs_mw.py`) are **not yet on disk** — the unit is open, its Acceptance/Evidence/Delivery sections still unfilled.

This trial is an **independent, narrower pass** (`sup_7` tag-scoped, 13,208 entries) that adds three things H4837's stated method does not carry:

1. **Annexure-neighbour ranking** (rank A/B/C) — the `kāritra`-class signal: a candidate whose alphabetical neighbour *was* carried into the MW99 annexure. H4837 tiers by cross-dict corroboration instead; the two axes are complementary.
2. **The reverse-direction measurement** — 30 % of MW annexure headwords are verbatim `sup_7` entries (§3), which tests Andhrabharati's dependency hypothesis directly.
3. **[CONTRADICTIONS §18](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)** — the census/H4537 code mapping (PWK → `pwg`) is contradicted by the Cologne headers.

**The candidate TSV here is not a competing adjudication list** — it is trial evidence for H4837, whose executor owns the verdict workbook. Numbers will not reconcile exactly (different scope by design: 1,751 absent from `sup_7` alone vs H4837's 3,024 across all Nachträge layers).

## 1 · Edition codes — read before filing anything

| Name | Identity | Cologne code | Probe evidence |
|---|---|---|---|
| MG's «PWK» / Andhrabharati's «pwk7» | Böhtlingk, *Sanskrit-Wörterbuch in kürzerer Fassung* (1879–89) | **`pw`** — [`v02/pw/pw.txt`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pw) | `pwheader.xml` title "Böhtlingk's Sanskrit-Wörterbuch in Kürzerer Fassung"; 31.5 MB, **170,556** entries; carries the `sup_1`…`sup_7` Nachträge tags; holds both `kAritra` and `kArApaka` at `pc 7-331-d` |
| the Nachträge, standalone | same edition, *Nachträge und Verbesserungen* | **`pwkvn`** — [`v02/pwkvn/pwkvn.txt`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pwkvn) | `pwkvnheader.xml`; 24,976 entries; contains `kAritra` (L 16013) and `kArApaka` (L 16011) |
| the "big" Petersburg dictionary | Böhtlingk & Roth, *Sanskrit Wörterbuch* (1855–75) | **`pwg`** — [`v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pwg) | `pwgheader.xml` "Böhtlingk and Roth's Sanskrit Wörterbuch"; 54.6 MB, **123,366** entries, long citation-rich entries; **no** Nachträge tags; contains **neither** `kAritra` nor `kArApaka` |

⚠️ [YADISK census §2](https://github.com/gasyoun/SanskritLexicography/blob/master/YADISK_05_SANSKRIT_LEXICON_TREES_CENSUS_10-09-2026.md) line 19 and the [H4537 corrigenda note](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_PWK_CORRIGENDA_PAIRS_11-09-2026.md) map «1879-PWK» to code **`pwg`** — the Cologne headers and the file probes say the opposite. Filed as **[CONTRADICTIONS §18](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)**; until ruled, **any PWK-side filing targets `v02/pw/` (and `v02/pwkvn/` for the Nachträge), not `v02/pwg/`**.

## 2 · Method

Builder: [`mw_pwk_nachtraege_missing_entries.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pwk_nachtraege_missing_entries.py) (stdlib only; `python -u mw_pwk_nachtraege_missing_entries.py [csl-orig/v02]`).

1. One pass over `pw.txt` — collect every entry whose definition lines carry `info n="sup_1"`…`"sup_7"` (the Nachträge layers).
2. One pass over `mw.txt` — collect every `k1`/`k2` headword, plus the **annexure** subset (entries whose body carries `info n="sup"`, i.e. the MW99 additions).
3. Tier-match each sup_7 headword against the MW headword set:
   - **exact** (SLP1, markers stripped);
   - **stem** (final-vowel/stem relaxation, e.g. `kanyas`↔`kanyasa`);
   - **near-form** (difflib ≥ 0.80 inside a first-char × length bucket) — a *review flag*, not a match (see §4);
   - **NO-MATCH** = candidate MW omission.
4. Rank each NO-MATCH candidate by neighbour evidence: **A** = an alphabetical sup_7 neighbour is in the MW annexure (the `kārāpaka` pattern), **B** = neighbour in MW main, **C** = no neighbour in MW.

Sanity checks in-run: `kAritra` in MW = False (expected), `kArApaka` in MW = True (expected) — both OK.

## 3 · Results (14-09-2026, `csl-orig` @ local main)

| metric | value |
|---|---|
| PWK entries tagged `sup_1..7` | 22,611 |
| PWK `sup_7` entries (letzte Nachträge) | 13,208 |
| MW headwords (`k1`+`k2`) | 194,283 |
| MW annexure-tagged headwords | 6,082 |
| sup_7 present in MW — exact | 8,978 |
| sup_7 present in MW — stem-normalized | 482 |
| sup_7 near-form only (needs review) | 1,918 |
| **sup_7 absent from MW (candidates)** | **1,751** |
| — rank A (neighbour in MW annexure) | **547** |
| — rank B (neighbour in MW main) | 800 |
| — rank C (no neighbour in MW) | 404 |

**Reverse direction — does the MW99 annexure really draw on the letzte Nachträge?**

- 1,800 of 6,082 MW annexure headwords (30 %) are **verbatim** `sup_7` headwords.
- 1,959 of 6,082 (32 %) are in *some* PWK Nachträge layer.

That is direct, measurable support for Andhrabharati's dependency hypothesis — and the 70 % that trace elsewhere show MW's annexure has several sources, so a sup_7-only diff will not explain the whole annexure.

**Verification spot-check** (exact grep on `mw.txt`, not the set logic): `akarmavant`, `akalitātman`, `akūjita` → 0 hits each; their annexure neighbours `akali`, `akalita`, `akUjana` → present. The rank-A candidates are genuinely absent headwords, not normalization artifacts.

## 4 · Precision caveats (the honest part)

1. **The near-form tier is the precision bottleneck.** The motivating case `kAritra` matched `kArita` at 0.92 — a *different* word (causative participle vs. the abstract "activity"). Near-form hits are **review flags, not evidence of presence**; a reviewer resolves them in seconds, an automated threshold cannot.
2. **Absence from MW is not automatically an MW error.** MW does not aim to list every PWK compound; the 404 rank-C candidates (no MW neighbour at all) are the weakest tier. Rank A is where the `kāritra`-class error lives: a neighbour carried into the annexure while the word itself was skipped.
3. **MW's annexure has sources beyond sup_7** (§3), so a candidate list is a *worklist*, never a verdict list.
4. The trial covers the **PWK side only**. Andhrabharati's phrasing "MW with PWG/pwk" also invites a `pwg` (1855–75) comparison — a much larger, noisier diff (MW deliberately omits most of the big dictionary's material), which this trial does not attempt.

## 5 · Files

- [`mw_pwk_nachtraege_missing_entries.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pwk_nachtraege_missing_entries.py) — builder (stdlib only, ~49 s).
- [`mw_pwk_nachtraege_candidates_14-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pwk_nachtraege_candidates_14-09-2026.tsv) — 4,151 rows (stem + near-form + absent), columns `pwk_L · pwk_pc · slp1 · iast · tier · rank · mw_fuzzy · evidence`.

## 6 · Not done here (next steps)

1. Re-run against **`pwkvn`** (24,976 entries, the dedicated Nachträge digitization) and cross-check against the `pw.txt` sup tags — two independent digitizations of the same block.
2. Human-review the **547 rank-A** candidates (and the near-form tier) into a verdict workbook — the `kāritra` class is in there.
3. If the estate wants it, a `pwg`-side sweep (MW vs 1855–75) as a separate, lower-precision pass.

_Гасунс_
