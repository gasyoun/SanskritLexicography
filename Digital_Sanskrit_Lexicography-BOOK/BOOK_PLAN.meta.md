# BOOK_PLAN.meta.md — metadoc for `BOOK_PLAN.md`

_Created: 13-07-2026 · Last updated: 18-07-2026 (H1241 backlog-5 tick)_

This is a **metadoc** — a document *about* a document. Its subject is
[BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md),
the plan of record for **Book A — the Brill monograph** *Digital Sanskrit Lexicography*
(registry **M01**). It does not duplicate the plan's content; it records everything *around* it
— why it exists, who built it, what it is for, what is still missing, and how it has evolved.
Kept per the standing "for every important document, a companion metadoc" convention
([`~/.claude/CLAUDE.md`](https://github.com/gasyoun/claude-config/blob/main/references/metadocs.md)).

## Subject

- **Document:** [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
- **Purpose:** the build plan of record for a single-authored English monograph at
  de Gruyter *Lexicographica. Series Maior* (LSM primary) / Brill's Indological Library (BIL
  fallback), assembled from ~15 already-committed research articles into a 14-chapter book on
  the thesis "the dictionary as a layered evidence graph, across two lexicographic
  civilizations."
- **Audience:** the author (MG) and any future agent/session continuing the book build; the
  eventual acquisitions editor reads the derived
  [BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md),
  not this plan.
- **Format / contract:** authored Markdown (dated header + `_Dr. Mārcis Gasūns_` byline, full
  blob URLs, `DD-MM-YYYY` dates, model attribution as tier + exact version). Chapter↔article
  mapping is by **stable A-IDs**, never P-numbers (the ROADMAP P1–P6 ≠ csl-atlas `PUBLICATIONS.md`
  P1–P6 — a known drift, BOOK_PLAN §9).

## Provenance

- **Created:** 09-07-2026 (H248 line, Opus 4.8 `claude-opus-4-8`), as the expansion of the M01
  stub in [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) and the
  10-chapter sketch in
  [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
  Part III.
- **Major hardenings:** H505 (10-07-2026, Fable 5 `claude-fable-5`) literature crosswalk +
  quality-bar audit; MG rulings 10-07-2026 (Ch. 7→Ch. 6 merge, 15→14 chapters) and 13-07-2026
  (corpus-methods = section in Ch. 2); the 13-07-2026 chapter-conversion wave (H846–H866, Opus
  4.8 `claude-opus-4-8[1m]`) that moved the book from 2 to **12 of 14 chapters in book form**.
- **Next hardening:** the two prose-thin data chapters (Ch. 3, Ch. 11) and the front/back matter
  — see backlog.

## Use cases

Who consults this document and for what — and what the book plus its committed assets can be
*used for* beyond the monograph itself.

### Who reads BOOK_PLAN.md, and why

| Consumer | Reads it to… |
|---|---|
| A resuming agent/session | learn the 14-chapter architecture, the A-ID↔chapter map, what is drafted vs. new-writing, and the critical path before touching any chapter |
| MG (author) | track chapter status, hold the locked decisions (series, the 15, the merges), and see what human-gated blockers remain (DOI/rights) |
| `/articles-update` · GTD sweeps | reconcile the M01 registry row and readiness against the plan |
| A crosswalk / grounding pass | find which secondary works each chapter must engage (via the sibling [LITERATURE_CROSSWALK.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md)) |
| A rights/permission check | confirm the author-held-copyright posture and per-venue CTA obligations (via [RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md)) |

### What the book + its assets can be used for

- **The monograph** — the primary deliverable: a single-authored LSM/BIL book placing the
  "evidence-graded lexicography" method with the lexicography readership, Sanskrit as the case
  study.
- **The 12 committed chapters as standalone journal articles** — each chapter carries a
  provenance headnote pointing at an independently-citable journal version (IJL, Lexicographica,
  DSH, LREC-COLING, Lexikos, WSC 2027 …); the book and the article stream feed each other.
- **The dissertation coordination** — the same article base supports MG's докторская at ИЯз РАН
  «по совокупности работ» (BOOK_PLAN §8); the plan is the shared source, no self-plagiarism
  conflict.
- **The datasets as reusable FAIR resources** — the evidentiary base (correction-event corpus,
  `<ls>` citation graph, union headwords, kośa macrostructure, MW block-economy tables, the
  Renou register glossaries) are committed, CC-licensed, and consumable independently of the
  book once DOI-deposited (BOOK_PLAN §6).
- **A de-veiling / register-tagging layer for CDSL re-editions** — several chapters ship
  ready-to-consume keys (the A36 Latin discretion-screen CSV as a de-veiling key; the Renou
  register glossaries; the anubandha decode) that a learner-facing or evidence-graded interface
  can consume directly.
- **A reusable measurement methodology** — Chapter 2's ten estimators + traceability discipline
  are stated as a portable method for *any* family of related digital dictionaries, not only
  Sanskrit.
- **Book B (the handbook)** — the reference-work sibling (HdO Section 2) that the excluded
  reference-flavoured material (A45, A46, the co-authored observatory papers) feeds; scoped in a
  separate plan, not here.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | **Ch. 3 ← A40** — write the CDSL-headword-inventory + corpus-grounding chapter from data | one of two chapters not yet in book form; A40 is data-only (no article prose to convert) — genuine first-drafting atop [HeadwordLists/NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) + union_headwords.tsv + dcs_cdsl_xref.tsv; **mandatory** McEnery & Brezina corpus-absence/representativeness reframe | **launched 18-07-2026** — [H1240](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1240-Fable_SanskritLexicography_m01-ch03-a40-ch11-a50-data-chapter-prose_18.07.26.md) |
| 2 | **Ch. 11 ← A50** — write the `<ls>` citation-frequency-graph chapter from data | A50 is a readiness-2/5 **skeleton** (prose 1/5); its §4 tradition-profiles rest on an **inferred map, 0/119 human-reviewed** that must NOT be asserted as fact yet; needs the review gate cleared or the section written as explicitly inferred; **mandatory** significance-at-N=828K (effect-sizes-not-p-values) reframe | **launched 18-07-2026** — [H1240](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1240-Fable_SanskritLexicography_m01-ch03-a40-ch11-a50-data-chapter-prose_18.07.26.md); the `tradition_tags.tsv` review gate is **still uncleared**, so §4 must ship as explicitly-inferred or be deferred — the handoff carries this as a hard constraint |
| 3 | **Ch. 2 corpus-methods section** — write the ~6–8 pp. "The corpus as a bounded witness" section into ch02 | MG ruled (b) on 13-07-2026 (fold, not a standalone chapter); the DCS-disclosure + statistical-practice + absence-inference material is owed at ch02's next revision | ✅ **done 17-07-2026** (H1078, Fable 5 `claude-fable-5`) — [ch02 §6](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md) |
| 4 | **FAIR/DOI sprint** — Zenodo-deposit every cited dataset, re-mint the false correction-dataset DOI, get the DCS denominator DOI (Hellwig sign-off), add CITATION.cff to kosha/SanskritLexicography/SanskritRussian | the real critical path — nothing citable ships without it; the DOI *minting* is a human/credentials @DO | ⏸ **deferred by MG to ~09-08-2026** |
| 5 | **Front/back matter** — Introduction, 5 Part-bridges, Conclusion, unified method appendix, index | the genuine remaining new-writing load once the 14 chapters exist (BOOK_PLAN §4); the comparative part-bridge is upgraded by the crosswalk §4.1 (Baalbaki/Ferri/Dickey) | ✅ **drafted 18-07-2026** ([H1241](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1241-Fable_SanskritLexicography_m01-introduction-part-bridges-conclusion-glue_18.07.26.md), Fable 5 `claude-fable-5`): Introduction (A61-argument-seeded per BOOK_PLAN §10 ruling 1) + 5 bridges (Part III carries the crosswalk §4.1 comparative upgrade) + Conclusion, all in [chapters/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK/chapters); framing calls parked for the author in [SIGNOFF_M01_glue_framing_calls.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/SIGNOFF_M01_glue_framing_calls.md). **Residue:** Part II/IV bridges carry ⚠️ re-describe-against-merged-Ch. 3/11 obligations (H1240); the unified method appendix + index wait for the chapter freeze by design |
| 6 | **κ / second-annotator** — one recruitment fixes the "reviewed"-claim reliability gap | the evidence-graded thesis's own selling point has unmeasurable reliability at n=1 reviewer (BOOK_PLAN §6/§9) | parked — human/recruitment @DO |
| 7 | **Автореферат / dissertation apparatus** — decide if a formal ИЯз РАН thesis doc is needed | open `@DECIDE` (BOOK_PLAN §10); no автореферат file exists in any repo | parked — MG `@DECIDE` |

## Known limitations / caveats

- **The plan supersedes but does not replace** the M01 ARTICLES.md stub and the ROADMAP Part III
  sketch — check all three before editing chapter scope (BOOK_PLAN §Dev-notes).
- **P-numbering is a trap:** the ROADMAP's P1–P6 ≠ csl-atlas `PUBLICATIONS.md` P1–P6; always map
  chapters through the **A-IDs**, never P-numbers.
- **Two source-path staleness bugs found during conversion** (now noted in-plan): A12's source is
  `paper-obs-t-error-typology.md` (not the §2 `reports/obs_t_paper_draft.md`); the A12 snapshot is
  52,498 events (not the §6 table's 50,953).
- **Folder is intentionally quiet** — an allowlist `.gitignore` (`!chapters/*.md`); it is a
  planning sideproject, not active development. Don't loosen the blanket `*` rule without reason.
- **Rights posture is unusually clean** but conditional: all source articles are unpublished
  drafts ⇒ copyright is 100% author-held today, with a per-venue CTA read owed only at each
  article's acceptance (RIGHTS_TABLE.md).

## Intended use / known misuse

- **Intended:** the orientation + status document a resuming session reads first; the source of
  truth for chapter architecture and the locked decisions.
- **Misuse to avoid:** (a) treating it as the manuscript — the chapters live in
  [chapters/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK/chapters);
  (b) mapping chapters by P-number instead of A-ID; (c) reading a chapter's "corpus-absent" or
  "zero" figures as absolute claims — several are convention/coverage statements by design
  (Ch. 4/7 zero-means-nothing, Ch. 13 DCS-coverage reframe); (d) asserting A50's inferred
  tradition map as fact before its human review.

## Maintenance & sunset plan

- **Kept alive by:** the book-folder CHANGELOG + `.ai_state.md` (session journal) and the M01 row
  in the Uprava hub; each chapter conversion/merge ticks BOOK_PLAN §11 and this metadoc's backlog.
- **"Done" looks like:** all 14 chapters + front/back matter drafted, DOIs minted, proposal
  submitted to LSM. At that point the plan freezes to a historical record and the live surface
  moves to the manuscript + the proposal correspondence.
- **Sunset:** on acceptance the plan is archived; the datasets persist independently via their
  Zenodo deposits and the kosha data manifest.

## Deprecation status

`active`.

## Related documents

- [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md) — the subject (plan of record).
- [BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md) — the editor-facing proposal derived from the plan.
- [LITERATURE_CROSSWALK.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md) — per-chapter secondary-lit grounding map (the source of every chapter's "grounding woven in").
- [RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md) — chapter → article → journal → copyright → permission matrix.
- [CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/CHANGELOG.md) · [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/.ai_state.md) — change record + session journal.
- [chapters/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK/chapters) — the 12 chapters in book form.
- [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) — the M01 registry row.

## Metadoc revision history

| Date | Event | Who (tier + version) |
|---|---|---|
| 18-07-2026 | **Backlog #5 drafted** — the seven glue pieces (Introduction seeded from A61's argument, chronicle/quotations excluded; 5 part-bridges with the crosswalk §4.1 comparative upgrade at Part III; Conclusion) land as new writing in `chapters/`, with the author-veto ledger [SIGNOFF_M01_glue_framing_calls.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/SIGNOFF_M01_glue_framing_calls.md); Part II/IV bridges carry explicit ⚠️ pending-Ch. 3/11 revision obligations; method appendix + index stay post-freeze | H1241, Fable 5 `claude-fable-5` |
| 13-07-2026 | Metadoc created; captures the 13-07-2026 conversion wave (2→12 chapters in book form, H846–H866), the two locked MG rulings, the use-cases inventory, and the ranked backlog (Ch. 3 / Ch. 11 / ch02-section / DOI / matter) | H867, Opus 4.8 `claude-opus-4-8[1m]` |
| 18-07-2026 | **A61 question ruled** — A61 feeds the Introduction as argument only, never a chapter; the 15-article/14-chapter architecture is explicitly *not* reopened (no 16th, no swap). Three riders ruled with it: venue stays de Gruyter LSM primary (BRILL_PROPOSAL.md flagged for a venue-neutral rename), WSC-2027 dual use permitted with cross-citation (book appears first ⇒ A61 is the derivative), and both writing tracks proceed now while the DOI sprint stays deferred. Backlog #1/#2/#5 launched as [H1240](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1240-Fable_SanskritLexicography_m01-ch03-a40-ch11-a50-data-chapter-prose_18.07.26.md)/[H1241](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1241-Fable_SanskritLexicography_m01-introduction-part-bridges-conclusion-glue_18.07.26.md); a non-chapter-reuse row added to [RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md); BOOK_PLAN §11's stale "convert A16/A01 as samples" item retired (done in H430, 09-07) | Opus 4.8 `claude-opus-4-8` |
| 17-07-2026 | Backlog #3 closed: ch02 §6 *The corpus as a bounded witness* written (~7 pp., DCS disclosure + absence-inference rule + statistical contract + Ch. 3/5/11/13 binding map); BOOK_PLAN §11 and the crosswalk §4.2 carry the ✍️-written notes with the 15→14-chapter consumer-numbering mapping | H1078, Fable 5 `claude-fable-5` |

_Dr. Mārcis Gasūns_
