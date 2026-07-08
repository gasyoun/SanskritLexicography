# Book proposal — *Digital Sanskrit Lexicography: The Dictionary as a Layered Evidence Graph*

_Created: 08-07-2026 · Last updated: 08-07-2026_

Draft proposal for the single-authored monograph **M01**, built to the
[Brill Book Proposal Guidelines](https://brill.com/fileasset/downloads_products/brill_bookproposal_guidelines.pdf)
and equally usable for the primary De Gruyter *Lexicographica. Series Maior* target. Assembles
the ToC + per-chapter summaries + comparables + counts + rights disclosure required at
proposal stage. Source plan:
[BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md);
rights detail:
[RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md).

> **Status: DRAFT for MG review.** The bracketed `[VERIFY]` items are the author's calls
> (final title, submission date, editor-in-post confirmation). Everything else is assembled
> from committed work.

---

## 1. Author

**Dr. Mārcis Gasūns** — independent researcher (Sanskrit lexicography / digital humanities).
ORCID [0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X). Contact: gasyoun@ya.ru.
Principal of the Cologne Digital Sanskrit Lexicon tooling effort across the
[`sanskrit-lexicon`](https://github.com/sanskrit-lexicon) and
[`gasyoun`](https://github.com/gasyoun) GitHub organizations; author of ~15 sole-authored
studies on the digital analysis of Sanskrit dictionaries (2024–2026).

## 2. Title

**Primary:** *Digital Sanskrit Lexicography: The Dictionary as a Layered Evidence Graph*
**Alternative:** *Two Traditions, One Method: Evidence-Graded Digital Lexicography of Sanskrit*
[VERIFY — MG picks the final title; the "evidence graph" frame leads with the method, which
suits the primary De Gruyter LSM lexicography readership.]

## 3. Aim & scope

A digital dictionary is not a text but a **layered evidence graph**: every lexicographic
statement — headword, sense, gender, citation, cross-reference — is a node carrying its
source dictionary and convention, an explicit **evidence grade**
(`observed | derived | inferred | reviewed`), corpus attestation where available, and review
provenance. This book establishes that model and demonstrates it on the richest possible
testbed: **Sanskrit, which uniquely possesses two parallel lexicographic civilizations** —
the European scholarly dictionaries (1832–1957: Wilson, the Petersburg *Wörterbücher*,
Monier-Williams, Apte) and the indigenous *kośa* / Pāṇinian tradition — nineteen centuries of
depth, forty-four digitized dictionaries, and a 5.6-million-token tagged corpus.

Where existing standards (ELEXIS, Lexonomy, TEI-Lex0) standardize the *encoding* of
dictionaries, this book standardizes their **epistemics**: graded, reviewable,
corpus-anchored evidence per statement, with the indigenous tradition treated as first-class
structured data rather than exotic noise. The argument is delivered as a sequence of
quantitative probes into the evidence graph, each from one structural angle (macro-, micro-,
medio-, mega-structure) and across the two-tradition contrast, all reproducible from openly
committed datasets.

**Method leads, Sanskrit is the case study** — so the book speaks to lexicographers,
meta-lexicographers, and digital humanists first, and to Indologists second.

## 4. Series & readership

- **Primary target:** De Gruyter ***Lexicographica. Series Maior*** (LSM) — the field's
  flagship meta-lexicography series, now under the merged De Gruyter Brill imprint. Editors:
  Idalete Dias, Rufus H. Gouws, Anja Lobenstein-Reichmann, Stefan J. Schierholz. English
  submissions accepted (cf. vol. 164, *Internet Lexicography*, 2024). [VERIFY editors in post.]
- **Fallback target:** **Brill's Indological Library** (BIL) — the Indology home if the
  method framing is judged too narrow for LSM. Contact: **Albert Hoffstädt**, Senior
  Acquisitions Editor, Sanskrit/Buddhist Studies
  ([Brill Acquisitions Editors](http://www.brill.com/about/contact/acquisitions-editors)).
  [VERIFY still in post.]
- **Access model:** standard subscription (not Open Access), per MG's decision 06-07-2026.
- **Primary readership:** academic lexicographers and meta-lexicographers (EURALEX / IJL
  community); digital-humanities and language-resources researchers. **Secondary:**
  Indologists, Sanskritists, historians of scholarship.
- **Note on non-Latin script:** the book uses Devanāgarī and IAST transliteration throughout
  (headwords, examples). Camera-ready fonts and Unicode handling are established; a
  transliteration table will front the volume.

## 5. Table of contents & per-chapter summaries

The 15 sole-authored articles are the chapters; the **glue** — Introduction, five part-opening
bridges, Conclusion, a unified method appendix, and the index — is new writing. Each chapter's
source article ID (from [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md))
and current readiness are noted.

**Introduction — *The Two Civilizations of the Sanskrit Dictionary*** *(new; ~15–20 pp).*
The two lexicographic traditions; why Sanskrit is the ideal testbed; the evidence-graph
thesis stated; a roadmap of the book.

### Part I — Two traditions, one method

- **Ch. 1 · The Latin Discretion-Screen** *(← A36, 5/5).* How the 19th-century European
  dictionaries were made, read, and self-censored, and a metalanguage-relative method for
  detecting it. Case study: *obscaena Latine* across 11 Cologne dicts (1832–1959), 2,104
  Latin-glossed senses — register is metalanguage-relative; the screen targets sex
  specifically; a high-Victorian phenomenon absent before Wilson and after 1928. Opens the
  "two metalanguages" motif.
- **Ch. 2 · The Measurement Framework** *(← A01, 4/5).* The methodological spine: evidence
  grading, reproducibility, the graph model. The apparatus the later chapters lean on.

### Part II — Macrostructure: the shape of the dictionary

- **Ch. 3 · The Headword Inventory** *(← A40, data 4/5).* Twelve-year growth of the CDSL
  headword inventory (+14.3%; Apte +146%, MW/PWG flat) and the corpus-grounding bridge
  (dictionary ↔ DCS): which headwords the corpus never attests (VEI 69.8% … SKD 14.1%).
- **Ch. 4 · Order Is the Dictionary** *(← A06, 4/5).* The *kośa* macrostructural type — the
  book's most original European/indigenous contrast; how ordering *is* the semantics in the
  indigenous tradition.

### Part III — Microstructure: inside the entry

- **Ch. 5 · The Block Economy of Monier-Williams** *(← A16, 5/5).* The European entry
  anatomized: 286,561 entries, a nine-type block typology, a hand-adjudicated gold benchmark
  (G5: P 0.86 / R 0.87 / F1 0.88, κ 0.82).
- **Ch. 6 · Sense Inheritance** *(← A02, 4/5).* Condensation, not inflation: how senses
  survive and compress across the 1822–1957 European family; the citation advantage.
- **Ch. 7 · Genetic, Not Historical** *(← A33, 4/5).* What sense *ordering* encodes:
  PWG/MW sense-1 = oldest 73.5% (chance floor 52.7%, τ 0.375) vs Apte/Kochergina; Vedic
  density PWG 23.4% ≈ MW 24.8% ≫ AP90 2.3%.
- **Ch. 8 · Grammar Without Tags** *(← A04, 4/5).* Recovering the indigenous verbal-root
  *kośa* microstructure on its own terms — the "zero means nothing" doctrine.
- **Ch. 9 · Pāṇinian Derivation Across Ten Lexica** *(← A35, 4/5).* Comparative *vyutpatti*:
  ~67k derivations, the tradition agreeing 90–100% on affixes, Wilson 1832 the disjoint
  outlier (a partly measurement-driven artifact, carefully separated).

### Part IV — Mediostructure & the citation apparatus

- **Ch. 10 · Pointing Inward** *(← A05, 4/5; absorbs A03/A07).* Cross-reference graphs and
  descent — the stemmatics of the dictionary family.
- **Ch. 11 · Two Citation Registers** *(← A08, 4/5).* European `<ls>` vs indigenous *iti*:
  citation density and rank-order re-sort the 44 dictionaries entirely.
- **Ch. 12 · What the Tradition Cites** *(← A50, data 4/5).* The `<ls>` citation-frequency
  graph: 828,505 citations across 11 dicts canonicalized to 912 shared text-nodes — the
  flagship network figure.
- **Ch. 13 · Apparatus, Not Errors** *(← A10, 4/5).* Shared inheritance as a forensic signal:
  shared-error ≈ 0%, citation-order agreement 0.811 — MW inherited the Petersburg lexicon.

### Part V — The living dictionary

- **Ch. 14 · Renou's Registers** *(← A34, 4/5).* Register/usage labels as an axis orthogonal
  to the historical states; 68.3% of épigraphique headwords are corpus-absent — vocabulary
  invisible to corpus-only methods.
- **Ch. 15 · Fifty Thousand Corrections** *(← A12, 4/5).* The error typology of twelve years
  of collaborative maintenance: 50,953 correction events × 43 dicts × 210 correctors — a
  field-unique dataset. **Sole-authored (confirmed 08-07-2026: byline is Gasūns; Funderburk
  and Patel appear as correctors within the dataset and as acknowledgees, not co-authors).**

**Conclusion — *The Evidence Graph as a General Model*** *(new; ~10–15 pp).* FAIR
infrastructure; what the two traditions teach lexicography at large.

**Appendix — Unified method & the evidence vocabulary** *(new).* The
`observed | derived | inferred | reviewed` grading, its reproducibility contract, and a
crosswalk toward PROV-O / TEI `@cert`.

## 6. Length, figures, timeline

- **Estimated length:** ~320–380 pp. Roughly 60–70% of the raw prose (~180–220 pp) already
  exists as referee-passed article drafts; journal→book conversion *removes* duplicated
  method/lit-review, and ~40–50 pp of new framing is added.
- **Estimated word count:** ~120,000–140,000 words incl. notes and bibliography. [VERIFY at
  manuscript stage.]
- **Figures & tables:** ~30–40 (each anchored to a committed dataset; see
  [BOOK_PLAN.md §6](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)).
  Flagship: the `<ls>` citation network (Ch. 12), the MW block-economy figures (Ch. 5), the
  derivation-agreement figure (Ch. 9).
- **Data availability:** every chapter's evidence is openly committed; datasets are being
  deposited to Zenodo with DOIs and CITATION.cff (the FAIR sprint — the book's true critical
  path, [BOOK_PLAN.md §9](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)).
- **Timeline:** ≥1–2 chapters are "under review" at proposal time (A16, A02). Indicative
  full-manuscript delivery: [VERIFY — MG sets the submission date]; the book is written
  in parallel with the author's докторская defense at the Institute of Linguistics, RAS.

## 7. Comparable / competing titles

- Gilliver, *The Making of the OED* (OUP, 2016) — the closest genre analog (single dictionary
  tradition, as narrative).
- Considine (ed.), *The Cambridge World History of Lexicography* (CUP, 2019) — the reference
  frame this book engages.
- Klosa-Kückelhaus & Wolfer (eds.), *Internet Lexicography* (De Gruyter, LSM 164, 2024) — the
  digital-lexicography neighbour in the target series.
- Dannélls, Blensenius & Borin (eds.), *Sixty Years of Swedish Computational Lexicography*
  (De Gruyter, 2025, OA) — the closest "one tradition as data" model.
- McGillivray, *Methods in Latin Computational Linguistics* (Brill, 2013) — Brill precedent
  for a single-language computational-lexicography monograph.
- Patkar, *History of Sanskrit Lexicography* (1981) — the topical predecessor this book
  updates for the digital age.

**Gap this book fills:** none of the above grades evidence *per lexicographic statement*, and
none treats an indigenous lexicographic tradition as first-class structured data alongside the
European one. That is this book's contribution.

## 8. Rights disclosure

The monograph synthesizes the author's own sole-authored research, most of it being published
in parallel as journal articles. **No third-party-copyrighted text is reproduced.** All 15
source articles are currently unpublished drafts, so copyright is entirely author-held today;
where a chapter draws on an article published before manuscript submission, the original is
fully cited and reused under that venue's author-retained rights (the majority are Open
Access CC-BY). An iThenticate overlap with the author's own prior articles is expected and
disclosed here. Full matrix:
[RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md).

## 9. Open items for the author (before submitting the proposal)

1. Pick the final title (§2) and set the submission date (§6).
2. Confirm the LSM editors and BIL acquisitions editor are still in post (§4).
3. Run the FAIR/DOI sprint so the data-availability statement (§6) can cite real DOIs — the
   top blocker ([BOOK_PLAN.md §9](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)).
4. Decide Book B (handbook) home and timing relative to Book A ([BOOK_PLAN.md §10.2](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)).

---

_Dr. Mārcis Gasūns_
