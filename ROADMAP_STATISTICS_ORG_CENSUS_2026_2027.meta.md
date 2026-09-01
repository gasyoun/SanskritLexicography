# ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.meta.md — metadoc for `ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md`

_Created: 18-07-2026 · Last updated: 01-09-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md)
- **Purpose:** The org-wide "what statistics can we compute over all ~85 repos, in what
  order" measurement roadmap — a 7-layer counting register (L1–L7, each stat marked
  ✅/◐/○) feeding the publications roadmap, a public observatory, internal QA, and product
  analytics.
- **Audience:** Whoever is asked "has X already been counted org-wide" before running a new
  census script; explicitly the deconfliction point against re-measuring something already ✅.
- **Format / contract:** "Part 0 — the counting register" is the living scoreboard (7 layers,
  each row: Statistic / Count-status / Where); later parts (not fully read in this pass) carry
  the sequencing plan. Status symbols (✅ computed · ◐ partial · ○ not started) update in
  place as work lands — this is the doc's core contract, don't restructure the table shape.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`).
- **Next hardening:** none scheduled — revisit whenever a census item flips status, per the
  doc's own "drive every ○ and ◐ to ✅" framing.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 0 | **Adopt one denominator for the register, and refresh the machine feed** (01-09-2026, H3793) | The subject is counted three ways — Part 0 prose ~48, Part IV KPI 48, and the machine feed [`stats_census_register.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/stats_census_register.csv) **59** — so the KPI percentage is not computable. The feed is also stale (12–18-07-2026) and understates three rows. It is the surface the public dashboard pages render from. | **open — highest-value; it is the Q2 entry condition** |
| 1 | L1 "Definition typology (synonym vs equivalent vs encyclopedic)" — ◐ (H1483, 24-07-2026) | Flagged as an "ATLAS_FAIR micro-gap". **Superseded twice:** first pass 15 dicts / 926,759 records / gold 63/79 = 79.7 %; current committed `--all` table 44/44 dicts / 1,496,157 records / gold **55/79 = 69.6 %** in [`data/DEFINITION_TYPOLOGY_WS2_4_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md). The subject's Part II quoted the superseded wave until 01-09-2026 | all-dict pass landed; double-key 300×7 pool + Wilson `E.` peel + sense-level split still open — only the pool yields a citable precision |
| 2 | L2 "Form→lemma ambiguity rate" — ○ not started | Named directly in the subject's L2 table as the one remaining morphology-layer gap | parked — no handoff minted yet |
| 3 | L3 "Meter / prosody statistics" — ○ not started | Named in the subject's L3 table; natural home is SanskritKaraoke per the "Where" column | parked — no handoff minted yet, likely SanskritKaraoke-side work |
| 4 | L3 "Vedic accent coverage" — ○ not started, pending VedaWeb reuse | Explicitly gated on VedaWeb M13 in the subject's own table | parked — depends on [ROADMAP_VEDAWEB_REUSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md) Phase 2/6 landing first |

## Known limitations / caveats
- ~~Only Part 0 (L1–L3 of 7 layers) was read closely when this metadoc was authored~~ —
  **closed 01-09-2026 (H3793):** all seven registers were audited against live artifacts at the
  Q1→Q2 quarter boundary; the per-register delivery statement is
  [`Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md).
- **Two register rows are capped, not pending** — sense/polysemy (11/44 dicts; the other 33
  carry no structural sense markers) and corpus root-class (accent collapse). The subject's
  contract "drive every ○ and ◐ to ✅" is unachievable as written; the register needs a
  **capped** status distinct from **partial**.
- **The subject's figures inherit live disagreements.**
  [CONTRADICTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
  §11 (kosha.db build drift, L2) and §13 (`corpus_lexicon` rows, L4) are 🔴 unresolved, and
  §14 (MW resolves to 5 placeholder nodes in the `<ls>` graph) gates the Q2 network-statistics
  workstream. §10 and §12 were **ruled** 26-08-2026 — cite 323,425 and name the pipeline stage
  for the Petersburg naive sum.
- Counts in the register are dated "as of the 06–12-07-2026 census re-measure" per the doc's
  own caveat — re-verify before citing in a paper if it has been more than a few weeks.
- This doc is explicitly **not** the publications roadmap (that's
  [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md))
  and not the asset inventory (that's `FEATURES_INDEX.md`) — it is specifically the
  measurement-scoping layer between them.

## Intended use / known misuse
- **For:** checking whether an org-wide statistic has already been computed before running a
  new census script — the doc's whole point is "don't recompute, check the register first."
- **Misuse:** treating a ✅ status as permanently current without checking the census
  re-measure date, or treating a ◐ partial as ✅ (several rows are explicitly partial with a
  named remaining scope, e.g. sense/polysemy distribution at 11/44 dicts).

## Maintenance & sunset plan
- Owner: whoever runs org-wide census/statistics work (closely tied to csl-observatory).
  No single named maintainer.
- Sunset: the doc's own framing is "the year is: finish the census... land it as a citable
  observatory + FAIR release set + a methods chapter" — sunset trigger is that methods
  chapter shipping, at which point this roadmap becomes historical planning material.

## Deprecation status
`active` — L1–L3 partially computed per the register; full L1–L7 sweep not yet complete.

## Related documents
- [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) — the publications roadmap this one feeds.
- [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) — "what assets exist"; this doc answers "what statistics can we compute over them."
- [Uprava/DATA_LAYERS_CENSUS.md](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md) — "what large data sits uncounted on disk," the sibling hub this doc distinguishes itself from.
- [ROADMAP_VEDAWEB_REUSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md) — gates the L3 Vedic accent coverage row.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |
| 01-09-2026 | Q1→Q2 quarter-boundary pass: all seven registers audited against live artifacts; backlog row 0 added (register denominator + stale machine feed); L1 typology row corrected to the superseding all-dict wave; capped-vs-partial and the inherited contradictions recorded | Opus 5 (`claude-opus-5[1m]`), H3793 |

_Dr. Mārcis Gasūns_
