# ROADMAP_ACC_NCC — Catalogue-of-Works asset (Aufrecht × New Catalogus Catalogorum)

_Created: 03-07-2026 · Last updated: 03-07-2026_

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

- **ACC** — [csl-orig `v02/acc/acc.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/acc/acc.txt)
  (format in [acc-meta2.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/acc/acc-meta2.txt)):
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
**reused** — [`sanskrit-util`](https://github.com/gasyoun/sanskrit-util) `to_slp1` /
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
- `HeadwordLists/works_catalogue/parse_acc.py` — [acc.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/acc/acc.txt)
  → JSONL: `{acc_L, pc_scan, k1_slp1, k2, body, sigla[], match_key}`.
- `HeadwordLists/works_catalogue/parse_ncc.py` — [combined.txt](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/NCC/files/src/SktNewCatalogus_Catalogorum_combined.txt)
  → JSONL: `{ncc_id, ncc_numid, deva, iast, body_html, sigla[], mss_witnesses, match_key}`.
- Both `match_key` via `sanskrit-util` `to_slp1`→`slp1_simplify`; strip parentheticals, underscores, fold anusvara.
- **Deliverable:** `HeadwordLists/works_catalogue/acc.jsonl`, `ncc.jsonl` + row counts logged.

### P1 — Full-fuzzy matching engine (tiered, scored) ✅ DONE (06-07-2026)
[`build_works_crosswalk.py`](HeadwordLists/works_catalogue/build_works_crosswalk.py) emits
`crosswalk_candidates.jsonl.gz` (169,260 rows), each tier + score — see
[`P1_COUNTS.md`](HeadwordLists/works_catalogue/P1_COUNTS.md) for the measured breakdown:

| Tier | Rule | Disposition | Measured (distinct keys) |
|---|---|---|---:|
| A | exact simplified-key | auto-accept | 8,397 ACC / 8,397 NCC (matches P0) |
| B | nasal-fold (`m`/`n`) + geminate-fold, beyond A | auto-accept | +2,041 ACC / +2,047 NCC |
| C | prefix containment (min 5-char key) | **adjudicate** | +1,254 ACC / +2,904 NCC |
| D | length-scaled edit-distance (rapidfuzz), blocked by first-letter+length | **adjudicate** | +7,552 ACC / +7,745 NCC |

- **Deliverable:** `crosswalk_candidates.jsonl.gz` with per-tier counts (measured, logged — no silent caps).

### P2 — Adjudication (human-gated — mandatory for full-fuzzy)
- `/review-sheet` HTML voting sheet over Tier C/D candidates → `decisions.json` → `/decisions-apply`.
- Full fuzzy manufactures false joins by design; C/D never auto-merge.
- **Deliverable:** `works_crosswalk.tsv` (accepted/rejected/deferred, with provenance).

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
