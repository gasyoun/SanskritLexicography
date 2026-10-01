# ROADMAP_ACC_NCC — Catalogue-of-Works asset (Aufrecht × New Catalogus Catalogorum)

_Created: 03-07-2026 · Last updated: 05-09-2026_

> **Truth-pass 27-08-2026** (Grok 4.6 `grok-4.6`). Closed references checked against the combined registry. Kept in place ([FINDINGS §475](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) clause 3). Not archived.

Goal: build a **catalogue-of-works data asset** by joining **ACC** (Aufrecht's
*Catalogus Catalogorum*, Cologne) as the spine with **NCC** (*New Catalogus
Catalogorum*) as a rich enrichment overlay. The asset is derived and maintained
**here in SanskritLexicography** (alongside the `HeadwordLists/` union spine);
the **kosha** product repo *consumes* the resulting crosswalk exactly as it
already consumes
[`union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv),
and serves it both as a browsable works module and as searchable title-lemmas.

Rulings elicited from MG 03-07-2026 (interview + placement decision run by
Opus 4.8, `claude-opus-4-8`). Home = SanskritLexicography per MG 03-07-2026
(supersedes the initial kosha-local draft).

## 0. Decisions locked (MG, 03-07-2026)

| Fork | Ruling |
|---|---|
| **Match strategy** | **Full fuzzy (max recall)** — exact + variant/prefix + edit-distance, every non-exact tier human-adjudicated. |
| **Data model** | **ACC spine + NCC overlay** — one work entry keyed on ACC where it exists; NCC bodies/mss-witnesses attach as enrichment. NCC-only works become their own entries. |
| **The Su-→Ha gap** | **NCC is final** — no further volumes will be printed. `ha-` and the late `sa-` tail are **permanently ACC-only**, flagged `ncc_coverage: none`. MG will re-verify the local NCC file is not merely stale before the build is frozen. |
| **Scope (in kosha)** | **Both** — a bibliographic works module AND title-lemmas exposed in kosha's main search index. |
| **Home repo** | **SanskritLexicography** (this repo) owns the derived asset; kosha consumes it. |
| **Rights** | ✅ Resolved — see §5. NCC = CC BY-NC 4.0; ACC = CC BY-SA 4.0; the asset is **dual-licensed**. |

## 1. Where things stand — measured 03-07-2026

Sources (consumed, not rebuilt):

- **ACC** — [csl-orig `v02/acc/acc.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/acc/acc.txt)
  (format in [acc-meta2.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/acc/acc-meta2.txt)):
  **49,833** entries, complete alphabet **A → Ha**, Cologne `<L>…<LEND>` records,
  SLP1 headwords (`k1`), `<pc>` scan refs to the 3-volume print. Terse (~164 B/entry).
- **NCC** — [VisualDCS `non-derived/NCC/…/SktNewCatalogus_Catalogorum_combined.txt`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/NCC/files/src/SktNewCatalogus_Catalogorum_combined.txt)
  (abbreviations in [Skt_ncc_abbr.txt](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/NCC/files/src/Skt_ncc_abbr.txt)):
  **152,378** entries across 39 volumes, **A → Su-** (stops mid-`sa`; no `ha`).
  TSV — Devanāgarī · IAST · structured ID `vol_page_col_seq` · numeric ID · HTML
  `<p>` body. Rich (~299 B/entry): many mss-witnesses + structural notes per work.

**Exact normalized-key join** (`sanskrit-util` `slp1_simplify` fold, IAST→SLP1 both sides):

| | ACC | NCC |
|---|---|---|
| Entries | 49,833 | 152,378 |
| Distinct match-keys | 32,287 | 124,651 |
| **Shared (exact)** | **8,413** (26.1% of ACC) | 8,413 (6.7% of NCC) |
| Source-only | 23,874 | 116,238 |

The 8,413 is a **high-precision floor, not the true overlap.** The two catalogues
routinely differ in headword form — ACC lists *Abhayapradāna*, NCC lists
*Abhayapradānasāra* (same work); compound extension, sandhi, qualifiers, and the
`ṁ`/`ṃ` anusvara glyphs all defeat an exact key. Recovering that hidden overlap
is the point of the full-fuzzy pipeline below.

Prior-art check (03-07-2026): no existing ACC×NCC crosswalk in the org
(`csl-atlas`, `SanskritLexicography`, `Uprava` hubs searched). The transcoder is
**reused** — [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) `to_slp1` /
`slp1_simplify` — not rebuilt.

## 2. Target shape

```
ACC spine (A→Ha, complete)  ──┐
                              ├──►  works crosswalk asset (this repo,        ──►  kosha consumes  ──►  ┌ works module
NCC overlay (A→Su, rich)    ──┘      HeadwordLists/works_catalogue/)                                    └ title-lemmas in search
```

The asset lives under `HeadwordLists/works_catalogue/` (parsers + crosswalk TSV/JSONL),
a sibling of the union-headword build. kosha adds a `works` table that loads it,
per its own [data/SOURCES.md](https://github.com/gasyoun/kosha/blob/main/data/SOURCES.md)
consumption pattern.

## 3. Phased plan

### P0 — Parsers & canonical extraction (this repo) ✅ DONE ([PR #201](https://github.com/gasyoun/SanskritLexicography/pull/201), 06-07-2026)
- `HeadwordLists/works_catalogue/parse_acc.py` — [acc.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/acc/acc.txt)
  → JSONL: `{acc_L, pc_scan, k1_slp1, k2, body, sigla[], match_key}`.
- `HeadwordLists/works_catalogue/parse_ncc.py` — [combined.txt](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/NCC/files/src/SktNewCatalogus_Catalogorum_combined.txt)
  → JSONL: `{ncc_id, ncc_numid, deva, iast, body_html, sigla[], mss_witnesses, match_key}`.
- Both `match_key` via `sanskrit-util` `to_slp1`→`slp1_simplify`; strip parentheticals, underscores, fold anusvara.
- **Deliverable:** `HeadwordLists/works_catalogue/acc.jsonl`, `ncc.jsonl` + row counts logged.

### P1 — Full-fuzzy matching engine (tiered, scored) ✅ DONE ([PR #205](https://github.com/gasyoun/SanskritLexicography/pull/205), 06-07-2026)
[`build_works_crosswalk.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/build_works_crosswalk.py) emits
`crosswalk_candidates.jsonl.gz` (**260,416 rows**), each tier + score — see
[`P1_COUNTS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P1_COUNTS.md) for the measured breakdown.
Figures below are the **26-07-2026 re-run on repaired NCC keys** (H1671); the pre-repair
column is kept because every earlier document in this repo quotes it:

| Tier | Rule | Disposition | Measured (distinct keys) | pre-repair |
|---|---|---|---:|---:|
| A | exact simplified-key | auto-accept | **22,775** ACC / 22,775 NCC (matches P0) | 8,397 / 8,397 |
| B | nasal-fold (`m`/`n`) + geminate-fold, beyond A | auto-accept | +1,335 ACC / +1,336 NCC | +2,041 / +2,047 |
| C | prefix containment (min 5-char key) | **adjudicate** | +2,717 ACC / +3,729 NCC | +1,254 / +2,904 |
| D | length-scaled edit-distance (rapidfuzz), blocked by first-letter+length | **adjudicate** | +872 ACC / +972 NCC | +7,552 / +7,745 |

Tier D shrank by 42,091 rows because it was never mostly a fuzzy tier: it was where the
corrupted keys landed, one edit away from their own correct spelling. Full row-for-row
migration, including every one of the 3,711 candidate rows the repair removed:
[`NCC_KEY_REPAIR_MIGRATION_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/NCC_KEY_REPAIR_MIGRATION_2026.md).

- **Deliverable:** `crosswalk_candidates.jsonl.gz` with per-tier counts (measured, logged — no silent caps).

### P2 — Adjudication (human-gated — mandatory for full-fuzzy)
- `/review-sheet` HTML voting sheet over Tier C/D candidates → `decisions.json` → `/decisions-apply`.
- Full fuzzy manufactures false joins by design; C/D never auto-merge.
- **Deliverable:** `works_crosswalk.tsv` (accepted/rejected/deferred, with provenance).
- **Status (09-07-2026, H264, Sonnet 5 `claude-sonnet-5`): tooling shipped, BLOCKED on MG's
  vote.** Sample-size ruling (asked, not silently picked): full 49,019-row sheet, no
  sampling. [`HeadwordLists/works_catalogue/build_p2_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/build_p2_sheet.py)
  generates the virtualized-scroll sheet;
  [`apply_p2_decisions.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/apply_p2_decisions.py)
  is the smoke-tested `decisions.json` consumer. [Draft PR #264](https://github.com/gasyoun/SanskritLexicography/pull/264),
  branch `feat/acc-ncc-p2-adjudication`.
- **Status (26-07-2026, [H1657](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1657-Opus_SanskritLexicography_acc-ncc-p2-agent-adjudication-49k_26.07.26.md),
  Opus 5 1M `claude-opus-5[1m]`): all Tier C/D rows adjudicated by agent; awaiting the
  precision bar.** MG's ruling В2 of 26-07-2026 kept the 09-07 full-coverage ruling and
  moved only the adjudicator: the full sheet was never votable by a human (~14 working days at
  1 s/row). [`adjudicate_p2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/adjudicate_p2.py)
  casts agent verdicts with cited evidence;
  [`build_p2_spotcheck_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/build_p2_spotcheck_sheet.py)
  draws a blind stratified sample;
  [`p2_precision_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/p2_precision_gate.py)
  publishes Wilson 95% lower bounds per stratum and gates promotion. **Nothing is promoted
  yet** — all 10,614 post-repair C/D rows sit in `works_crosswalk_agent_proposed.tsv` until
  a human votes the sample and rules the bar.
  Full report: [`P2_AGENT_ADJUDICATION_REPORT.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P2_AGENT_ADJUDICATION_REPORT.md).
- **Status (30-07-2026, [H1951](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1951-Grok_SanskritLexicography_acc-ncc-p2-larger-sample_30.07.26.md),
  Grok 4.5 `grok-4.5`): larger blind sample re-drawn.** MG vote 4c (H1948) chose option (c)
  over locking 0.85/0.90: re-draw first so a **0.95** Wilson bar is attainable. New frame:
  **1,111 cards · 17 strata · n=73** per side (seed `19512026`; min n with perfect-agreement
  LB ≥ 0.95). Prior unvoted 698-card frame (n=50/40) superseded. Sheet stamped + locked
  (H1404). On a perfect vote, bar 0.95 promotes **858/920** approve rows (62-row census
  stratum cannot clear 0.95 by construction). **Next human:** vote the spot-check, then set
  the bar. Feasibility table: [`P2_PRECISION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P2_PRECISION.md).
- ✅ **The corrupted-NCC-key defect is FIXED (26-07-2026, H1671).** 60.0% of `ncc.jsonl`
  match-keys were wrong (uppercase IAST initials read as different SLP1 letters), which made
  93.3% of Tier D an artefact and hid **14,379 exact matches that were never proposed as
  candidates**. Measured in H1657, filed as
  [integrity issue #779](https://github.com/gasyoun/SanskritLexicography/issues/779), repaired
  and re-run end-to-end by
  [H1671](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1671-Opus_SanskritLexicography_acc-ncc-p0p1-ncc-key-repair-rerun_26.07.26.md)
  (`parse_ncc.match_key_for` now case-folds + NFC-normalizes before transliteration, pinned by
  [`test_parse_ncc.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/test_parse_ncc.py)).
  The P0/P1/P2 tables above are the post-repair numbers; the before/after is
  [`NCC_KEY_REPAIR_MIGRATION_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/NCC_KEY_REPAIR_MIGRATION_2026.md).
- **Status (26-07-2026, H1671, Opus 5 1M `claude-opus-5[1m]`): re-adjudicated on the repaired
  candidate set — 10,614 Tier C/D rows (was 49,019), 920 approve / 9,694 reject.** The two
  rules that carried the old run (`exact_after_key_repair` 40,757, `fold_after_key_repair`
  615) now fire **zero** times: those rows are Tier A upstream. The 686-card spot-check sample
  and any vote against it are **void** (drawn from a population that no longer exists; it was
  never voted, so nothing human was lost) — replaced by a blind **698-card** sample over 17
  strata. Still nothing promoted: all 10,614 sit in `works_crosswalk_agent_proposed.tsv` until
  a human rules the bar.

### P3 — kosha consumption (product repo)
- kosha adds a `works` table (canonical headword deva/IAST/SLP1; ACC body + sigla + `pc_scan`; NCC body + mss-witnesses; `match_tier`; `ncc_coverage`; per-source `license`), loading this repo's `works_crosswalk.tsv` — mirrors the union-spine load in [kosha `build_db.py`](https://github.com/gasyoun/kosha/blob/main/scripts/build_db.py).
- **Deliverable:** `works` table in kosha; asset registered in `PROJECT_INTERLINKS.md`.

### P4 — kosha surfaces (both)
- **Works module:** browse/search by title, author, subject-abbrev, mss location; ACC + NCC panes with a coverage badge.
- **Title-lemmas:** work-titles in the main search index, cross-linked to dictionary lemmas by normalized SLP1 key (reuse the range-seek prefix fix in kosha).

### P5 — Provenance, rights, release
- `/publish-safety-check` before public exposure. Rights are resolved (§5); ship **dual-licensed** (ACC BY-SA / NCC BY-NC), per-field license tags. `/data-release` + DOI.

## 4. The permanent Su-→Ha gap

NCC being final, `ha-` (an entire, large Sanskrit letter) and the late `sa-` tail
exist **only** in ACC. Every such entry carries `ncc_coverage: none`. **Before
freezing:** MG re-checks the local NCC dump against any newer VisualDCS export.

## 5. Rights — RESOLVED (CC BY-NC 4.0 for NCC; dual-licensed asset)

NCC redistribution was **granted** by Martin Gluckman (Vedic Society), relaying
the Madras / Raghavan rights-holders — email 25-06-2026, formal record in
[docs/permissions/NCC_permission_2026-06-25.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/permissions/NCC_permission_2026-06-25.md).
Scope: verbatim bodies + derived data. The apparent "same as CDSL" vs
"non-commercial" contradiction was **cleared by MG re-query (03-07-2026): "same
as CDSL" meant attribution style, not the license.** Operative terms:

- **NCC = CC BY-NC 4.0** (non-commercial, **no share-alike**), CDSL-style dual
  attribution to the NCC source **and** Gluckman.
- **ACC = CC BY-SA 4.0** (Cologne/CDSL).

The crosswalk asset is therefore **dual-licensed**: ACC spine + ACC-only entries
stay CC BY-SA 4.0; NCC bodies/overlay carry CC BY-NC 4.0, tagged per-field (or
NCC shipped as its own BY-NC asset). NCC is never relabeled BY-SA and BY-SA data
is never restricted to NC — ordinary dual-license packaging, not a merge conflict.

## 6. Diplomacy

NCC provenance sits with VisualDCS (gasyoun) and the Madras project; ACC with
Cologne/CDSL. Any external-facing release honours the kosha
[RELATIONS.md](https://github.com/gasyoun/kosha/blob/main/RELATIONS.md) §7 triggers.

_Dr. Mārcis Gasūns_
