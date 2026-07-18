# ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.meta.md — metadoc for `ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

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
| 1 | L1 "Definition typology (synonym vs equivalent vs encyclopedic)" — ○ not started | Flagged as an "ATLAS_FAIR micro-gap" in the subject's own L1 table, ties directly to the publications roadmap's Part I microstructure gap list | parked — no handoff minted yet |
| 2 | L2 "Form→lemma ambiguity rate" — ○ not started | Named directly in the subject's L2 table as the one remaining morphology-layer gap | parked — no handoff minted yet |
| 3 | L3 "Meter / prosody statistics" — ○ not started | Named in the subject's L3 table; natural home is SanskritKaraoke per the "Where" column | parked — no handoff minted yet, likely SanskritKaraoke-side work |
| 4 | L3 "Vedic accent coverage" — ○ not started, pending VedaWeb reuse | Explicitly gated on VedaWeb M13 in the subject's own table | parked — depends on [ROADMAP_VEDAWEB_REUSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md) Phase 2/6 landing first |

## Known limitations / caveats
- Only Part 0 (L1–L3 of 7 layers) was read closely when this metadoc was authored — L4–L7
  (translation, review/QA, publication, and any further layers) exist in the doc but were not
  individually audited here; a future metadoc pass should extend the backlog once those
  sections are read.
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

_Dr. Mārcis Gasūns_
