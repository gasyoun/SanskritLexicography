# Digital Sanskrit Lexicography (Brill monograph) — changelog

_Created: 07-07-2026 · Last updated: 10-07-2026_

Tracks changes to the book build plan and any future manuscript/front-matter drafts in this
folder. Registry ID **M01** in [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md).

## [Unreleased]

### Changed — 10-07-2026 (MG ruling on H505's Ch. 7 `@DECIDE`)

- **Ch. 7 (A33) folded into Ch. 6 (A02) as its second half**, "Senses: Inheritance and
  Order" — MG resolved H505's crosswalk fork as option (b). The book collapses from 15 to
  **14 chapters**; every chapter after the old Ch. 6 renumbers down by one (old Ch. 8→7,
  9→8, 10→9, 11→10, 12→11, 13→12, 14→13, 15→14). Updated:
  [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
  §0/§3/§4/§9, [BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md)
  §5/§6, and the two written sample chapters' internal cross-references
  ([ch02_measurement_framework.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md)).
  The standalone-corpus-methods-chapter fork ([LITERATURE_CROSSWALK.md §4.2](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md))
  remains open and unaffected.

### Added — 10-07-2026 (H505 execution)

- [LITERATURE_CROSSWALK.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md):
  the 37-work Lexicography-Manuals library read against the plan, proposal, and both
  written chapters — per-chapter grounding map, gap analysis (corpus-absence induction
  problem = top referee risk), competing-works positioning (novelty vs LSM 164 restated as
  the evidence-grade layer), comparative part-bridge recommendation (Baalbaki/Ferri/Dickey),
  and the chapter-by-chapter quality-bar audit (no cuts; four mandatory reframes; the Ch. 7
  keep-vs-merge fork parked as `@DECIDE`).
- [literature/md/Lexicography-Manuals/LEXICOGRAPHY_MANUALS.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/LEXICOGRAPHY_MANUALS.meta.md):
  directory metadoc for the library — provenance (committed 07-07-2026 inside PR #219),
  bibliographic identities + one-line tags for all 37 works, hygiene defects (1 empty scan,
  1 duplicate, 1 mangled filename, 1 low-authority anthology), and the ranked beyond-M01
  backlog (A30/A31/A32, pwg_ru grading, A39, teaching shelf).

### Changed — 10-07-2026

- [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md):
  §11 gains the H505 done-entry pointing at the crosswalk. Pending corrections surfaced by
  the audit (Klosa-Kückelhaus sole-editor fix in BRILL_PROPOSAL §7; Vogel 1979 + Baalbaki
  2014 comparables additions) are listed in LITERATURE_CROSSWALK.md §6, deliberately not
  applied in this pass.

### Added — 09-07-2026 (H430 execution)

- [chapters/ch02_measurement_framework.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md):
  book-form sample chapter converted from the A01 journal draft
  ([csl-atlas paper_measurement_framework.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_measurement_framework.md))
  — journal front/back matter stripped, re-anchored to the evidence-graph thesis,
  companion-paper pointers remapped to sibling chapters (Chs. 4/5/6/8/10/11), all figures
  and measured numbers unchanged.
- [chapters/ch05_mw_block_economy.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch05_mw_block_economy.md):
  book-form sample chapter converted from the A16 journal draft
  ([MWS papers/microanalysis/PAPER.md, `docs-pass`](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md))
  — IJL submission header/abstract stripped, voice unified to first-person singular,
  relative repo links upgraded to full `docs-pass` URLs, re-anchored to Ch. 2's framework;
  all tables, figures, and measured numbers unchanged. Reference lists normalized to one
  Chicago author-date convention across both chapters (book-wide bibliography merge and
  section renumbering deferred to a later production pass).
- `.gitignore`: `!chapters/*.md` added to the allowlist so the sample chapters are tracked.

### Added — 08-07-2026 (H248 execution)

- [RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md):
  chapter → article → venue → publisher → copyright → self-reuse matrix (§7c deliverable).
  Finding: all 15 source articles are unpublished drafts, so copyright is 100% author-held
  today and no chapter is rights-blocked; the standing task is a per-venue CTA read at each
  article's acceptance.
- [BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md):
  full De Gruyter LSM / Brill BIL proposal draft — author, title, aim & scope,
  series/readership, ToC + per-chapter summaries, length/figures/timeline, comparables,
  rights disclosure (§7b deliverable).

### Changed — 08-07-2026

- [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md):
  A12 authorship confirmed sole-authored (§2/§10 — Ch. 15 locks); §11 next-actions updated
  with completed items.

### Added — 06-07-2026

- [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md):
  initial build plan for the single-authored monograph — organizing thesis, proposed 15-chapter
  table drawn from the article registry, locked series target (primary: de Gruyter
  *Lexicographica. Series Maior*; fallback: Brill's Indological Library), and the
  data-citability/rights blockers ahead of drafting.

---

_Dr. Mārcis Gasūns_
