# How to Make the Brill Book — *Digital Sanskrit Lexicography*

_Created: 06-07-2026 · Last updated: 11-07-2026_

A build plan for a single-authored English monograph at Brill, drawn from work already
committed across the `sanskrit-lexicon` / `gasyoun` GitHub repos, and coordinated with
Mārcis Gasūns's докторская defense at the Institute of Linguistics, RAS (ИЯз РАН). It
supersedes the 1-line M01 stub in
[Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) and expands
the 10-chapter sketch in
[SanskritLexicography/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
Part III.

---

## 0. Executive summary

**Decisions locked (MG, 06-07-2026):** ① the 15 in §2 are **approved as proposed** (pending
the A12 sole-authorship check); ② primary series = **de Gruyter *Lexicographica. Series
Maior* (LSM)** — the field's flagship lexicography series, now under the merged **De Gruyter
Brill** imprint, so it still satisfies "printed at Brill"; **Brill's Indological Library**
is the fallback; ③ **standard subscription**, not Open Access. Implication of ②: the book is
placed with the *lexicography* readership (IJL / EURALEX world), so the "evidence-graded
lexicography" method is the lead frame and Sanskrit is the case study — pitch the method
first, the language second.

- **Two separate books, confirmed with MG:**
  - **Book A — the monograph** (this plan's focus): a *single-authored* argument that
    glues ~15 mostly-English articles into one account, on the spine **"two lexicographic
    traditions (European 1832–1957 vs indigenous kośa/Pāṇinian), unified by evidence-graded
    lexicography — the dictionary as a layered evidence graph."** → Registry **M01**.
  - **Book B — the comprehensive handbook** (separate, later track): a reference work on
    the Sanskrit dictionaries as digital objects. This maps to a *different* Brill vehicle
    (see §7) and is scoped in a companion plan, not here.
- **Series target for Book A (locked):** primary **de Gruyter *Lexicographica. Series
  Maior* (LSM)** — the field's flagship lexicography series (De Gruyter Brill imprint);
  fallback **Brill's Indological Library (BIL)**. (§7.)
- **Readiness is unusually high.** ~13 of the proposed 15 articles (now **14 chapters**
  after the Ch. 6 merge, §3) already exist as journal-article drafts at **4–5/5**. The book
  is a *gluing + framing* job, not a first-drafting job — which is exactly the "slightly
  reworked edition of the articles glued together" MG asked for.
- **The critical path is NOT writing — it is data-citability and rights.** (1) **No minted
  DOI exists anywhere** across the repos; (2) the correction dataset carries a *false* DOI;
  (3) a per-article **copyright/reuse table** is required because the book reworks the
  author's own journal articles. These are the real blockers (§6, §9).

---

## 1. The organizing thesis (the book's spine)

From [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
Part II, confirmed by MG:

> A digital dictionary is not a text but a **layered evidence graph**. Every lexicographic
> statement — headword, sense, gender, citation, cross-reference — is a node carrying
> (a) its source dictionary and convention, (b) an explicit evidence grade
> (`observed | derived | inferred | reviewed`), (c) corpus attestation where available,
> and (d) review provenance. Sanskrit — with **two parallel lexicographic civilizations**
> (European 1832–1957 and indigenous kośa/Pāṇinian), nineteen centuries of depth, and a
> 5.6M-token tagged corpus — is the ideal testbed. What is new versus ELEXIS / Lexonomy /
> TEI-Lex0 is that those standardize *encoding*; this book standardizes *epistemics*:
> graded, reviewable, corpus-anchored evidence per statement, with the indigenous tradition
> as first-class data, not exotic noise.

Every chapter is a probe into that graph from one structural angle (macro-, micro-, medio-,
mega-structure) and across the two-tradition contrast.

---

## 2. Book A — the proposed 15 articles

MG asked me to propose 15 from the ~50 in the registry. Selection rule: **English (or
readily English-convertible), sole-author, lexicography-topical, and distinct as a chapter.**
This deliberately differs from the Q3 submission batch in
[Uprava/PUBLICATION_ROADMAP_2026Q3.md](https://github.com/gasyoun/Uprava/blob/main/PUBLICATION_ROADMAP_2026Q3.md),
which was engineered for *submission readiness* and mixes in the Russian translation-studies
papers that belong to a **different** book (§5).

| # | ID | Chapter topic | Repo | Readiness | Lang |
|---|----|---------------|------|:---------:|:----:|
| 1 | **A36** | The Latin discretion-screen — history + metalanguage (1832–1959) | [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena_note.md) | 5/5 | EN |
| 2 | **A01** | The measurement framework — evidence-graded method | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_measurement_framework.md) | 4/5 | EN |
| 3 | **A40** | The CDSL headword inventory — 12-yr growth + corpus-grounding | [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) | data 4/5 | EN |
| 4 | **A06** | Order is the dictionary — kośa macrostructure | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md) | 4/5 | EN |
| 5 | **A16** | The block economy of Monier-Williams — the European entry anatomized | [MWS](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md) | 5/5 | EN |
| 6 | **A02** | Sense inheritance — condensation, not inflation | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md) | 4/5 | EN |
| 7 | **A33** | Genetic, not historical — what sense order encodes | [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md) | 4/5 | EN |
| 8 | **A04** | Grammar without tags — indigenous verbal-root microstructure | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_indigenous_microstructure.md) | 4/5 | EN |
| 9 | **A35** | Pāṇinian derivation across ten lexica | [csl-orig](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/PAPER_DRAFT.md) | 4/5 | EN |
| 10 | **A05** | Pointing inward — cross-reference graphs & descent (absorbs A03/A07) | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md) | 4/5 | EN |
| 11 | **A08** | Two citation registers — European `<ls>` vs indigenous *iti* | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md) | 4/5 | EN |
| 12 | **A50** | What the tradition cites — the `<ls>` citation-frequency graph (11 dicts) | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A50_ls_citation_frequency_graph.md) | data 4/5 | EN |
| 13 | **A10** | Apparatus, not errors — shared inheritance as forensic signal | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) | 4/5 | EN |
| 14 | **A34** | Renou's registers — an orthogonal lexicographic axis | [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_renou_register_note.md) | 4/5 | EN |
| 15 | **A12** | Fifty thousand corrections — an error typology of collaborative maintenance | [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_paper_draft.md) | 4/5 | EN |

**Swap bench** (all EN, sole-author, low external gate) if any of the 15 slips or MG
prefers a different cut: **A03** (three axes of descent), **A07** (redundancy & descent),
**A09** (sense alignment across 15 dicts), **A44** (dictionary-body triage — a DH-method
chapter), **A37** (orthographic drift as a dater — a philology chapter).

> ✅ **A12 authorship confirmed sole-authored (08-07-2026).** The
> [OBS-T draft](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_paper_draft.md)
> byline is **Mārcis Gasūns** alone; Jim Funderburk and Dhaval Patel appear only as
> *correctors within the dataset* (the 50,953 events) and as acknowledgees, not co-authors
> (contrast the genuinely co-authored A13/A14, correctly excluded). **Ch. 15 = A12 locks;**
> no swap to A48 needed.

---

## 3. Book A — chapter architecture (5 parts, 14 chapters)

The 15 articles map onto **14 chapters** — 13 one-to-one, plus Ch. 6 merging A02+A33
(ruling below) — the remaining **glue** (Introduction, the Part-opening bridges,
Conclusion, a unified method appendix, the index) is the new writing.

**Front matter / Introduction — *new*.** The two civilizations; why Sanskrit is the
testbed; the evidence-graph thesis stated; roadmap of the book. (~15–20 pp.)

**Part I — Two traditions, one method**
- Ch. 1 ← **A36** — history: how the 19th-c. European dictionaries were made, read, and
  self-censored; the metalanguage-relative method (opens the "two metalanguages" motif).
- Ch. 2 ← **A01** — the measurement framework: evidence grading, reproducibility, the graph
  model. (The methodological spine the later chapters lean on.)

**Part II — Macrostructure: the shape of the dictionary**
- Ch. 3 ← **A40** — coverage and growth of the headword inventory; the corpus-grounding
  bridge (dictionary ↔ DCS). _Documentary-lexicography baseline for the root- vs
  lexeme-oriented headword contrast: Coward & Grimes 2000 §4.6/§6.1 (already wired into
  A40 §1) — carry the citation into the chapter at conversion._
- Ch. 4 ← **A06** — *Order is the dictionary*: the kośa macrostructural type — the book's
  most original European/indigenous contrast.

**Part III — Microstructure: inside the entry**
- Ch. 5 ← **A16** — the block economy of Monier-Williams (the European entry, anatomized).
- Ch. 6 ← **A02 + A33** — senses: inheritance and order. Merged 10-07-2026 (MG ruling on
  H505's `@DECIDE`, [LITERATURE_CROSSWALK.md §5](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md)):
  A02's condensation/survival/citation-advantage material as the chapter's first half, A33's
  sense-*ordering* material (genetic vs historical, PWG/MW vs Apte/Kochergina — reframed per
  the crosswalk as an empirical test of Apresjan's ordering principle against the European
  Sanskrit family, not a restatement of it) as the second half, "senses: inheritance and
  order." Collapses the book to **14 chapters** — see §4/§9 below. _Documentary-lexicography
  baseline for the homonymy-vs-polysemy / sense-grouping contrast: Coward & Grimes 2000 §6.3
  (already wired into A33 §1) — carry the citation into the chapter at conversion._
- Ch. 7 ← **A04** — the indigenous entry: recovering the kośa/Pāṇinian apparatus on its own
  terms (the "zero means nothing" doctrine).
- Ch. 8 ← **A35** — comparative derivation: Pāṇinian *vyutpatti* across ten lexica.

**Part IV — Mediostructure & the citation apparatus**
- Ch. 9 ← **A05** — cross-reference graphs and descent (stemmatics of the family).
- Ch. 10 ← **A08** — two citation registers: `<ls>` (European) vs *iti* (indigenous).
- Ch. 11 ← **A50** — what the tradition cites: the citation-frequency graph.
- Ch. 12 ← **A10** — apparatus, not errors: shared inheritance as a forensic signal
  (MW inherited the Petersburg lexicon).

**Part V — The living dictionary**
- Ch. 13 ← **A34** — Renou's registers as an orthogonal axis (usage/register labels).
- Ch. 14 ← **A12** — fifty thousand corrections: the error typology of twelve years of
  collaborative maintenance — the field-unique dataset.

**Conclusion — *new*.** The evidence graph as a general model; FAIR infrastructure; what
the two traditions teach lexicography at large. (~10–15 pp.)

---

## 4. What exists vs. what needs new writing

| Bucket | Content | Effort |
|---|---|---|
| **Already drafted (4–5/5)** | 13 of 15 articles exist as referee-passed drafts (all but A40 data-only and A50 prose-1/5); Ch. 6 draws on two of them (A02+A33) | *Convert* journal→book: strip article front/back matter, unify voice, de-duplicate shared method into Ch. 2; Ch. 6 additionally needs the two articles' prose interleaved into one chapter, not just concatenated |
| **Data-ready, prose-thin** | A40 (data 4/5), A50 (data 4/5) | Write ~1 chapter of prose each atop committed data |
| **New writing from scratch** | Introduction, 5 Part-bridges, Conclusion, unified method appendix, index, cross-chapter connective tissue | The genuine drafting load |

**Page estimate:** a Brill monograph runs ~300–450 pp. The 15 article drafts represent on
the order of **~180–220 pp** of existing prose; after journal→book conversion (which *removes*
duplicated method/lit-review) plus ~40–50 pp of new framing, a realistic target is
**~320–380 pp**. Roughly **60–70% of the raw prose already exists** — the book is closer to
done than a from-scratch monograph by a wide margin. The Ch. 6 merge does not change this
estimate materially — it consolidates existing prose rather than adding or cutting content.

---

## 5. What is deliberately excluded (and where it goes)

- **Russian translation-studies papers — A19, A20, A21, A22, A23, A24 (CommentaryStrategies).**
  These belong to a **different monograph** — *The Reader as Addressee* (ИЛИ РАН postdoc
  stream, [roadmap_postdoc_2026.md](https://github.com/gasyoun/CommentaryStrategies/blob/main/roadmap_postdoc_2026.md)).
  They are RU and off-spine for a Brill *lexicography* book. (The Q3 batch mixed them in for
  submission-count reasons; do not carry that mix into this book.)
- **Corpus / translation data-papers — A38 (DCS release), A41 (Samudra parallel corpus),
  A42 (1.09M Sa→Ru lexicon), A43.** These are *data papers* and/or rights-encumbered RU-corpus
  work — better as standalone LREC/JOHD deposits or as **appendices/the handbook**, not core
  chapters. A38's DCS denominator is still *cited* by Ch. 3.
- **Co-authored observatory papers — A13, A14, A15.** Not sole-author; they feed the FAIR /
  infrastructure story (a possible appendix or the handbook), not a signed chapter.
- **A45 (botanical crosswalk), A46 (MW preface edition).** Reference-flavoured → **Book B
  (handbook)** or appendices.

---

## 6. Data → figures, tables, appendices (and the blockers)

The book's evidentiary base already exists as committed datasets. Highest-value inputs
(condensed from the data-asset audit; full list on request):

| Chapter | Dataset (repo) | Headline number | Book element |
|---|---|---|---|
| 1 (A36) | `A36_corpus_screen.csv` (SanskritLexicography) | 2,104 Latin-glossed senses / 11 dicts | table + figure |
| 3 (A40) | `union_headwords.tsv` (SanskritLexicography) | 323,425 union headwords, per-dict provenance | coverage/Jaccard figure |
| 3 (A40) | `dcs_cdsl_xref.tsv` (csl-apidev) | 15,902 DCS lemmas, 81.4% linked | corpus↔dict table |
| 4/8 (A06/A04) | kośa macrostructure + gaṇa apparatus (csl-atlas) | 85.5% gaṇa agreement | worked example |
| 5 (A16) | MW block-economy tables/figures (MWS) | 286,561 entries; G5 P 0.86 / R 0.87 | figures 1–3 |
| 9 (A35) | `mw_etymology.tsv` + oracle (csl-orig) | 9,377 derivations, 10 dicts | derivation-agreement figure |
| 11/12 (A08/A50) | `<ls>` citation graph (csl-atlas) | 828,505 citations → 912 texts | flagship network figure |
| 15 (A12) | `correction_events_release.csv` (csl-observatory) | 50,953 events × 43 dicts × 210 correctors | figure + appendix dataset |
| — (data-hub) | [kosha data-v0.1.0](https://github.com/gasyoun/kosha/releases/tag/data-v0.1.0) | 7 datasets, ~718k rows, CC BY-SA | appendix manifest |

**Data blockers (the real critical path — see §9):**
1. **No minted DOI anywhere.** `CITATION.cff` exists in only 4 repos; every DOI field is
   empty. A Brill book must cite *citable* data. → Zenodo-deposit sprint required first.
2. **The correction dataset (Ch. 15) carries a FALSE DOI** (`10.5281/zenodo.15834721`
   resolves to an unrelated preprint, never minted). Must be re-minted before Ch. 15 ships.
3. **The DCS corpus denominator (Ch. 3) has no DOI** and is gated on Hellwig CC-BY sign-off
   (A38). Every corpus-grounding claim needs it.
4. **Translation datasets are rights-blocked**, not just DOI-blocked (in-copyright RU) —
   another reason they stay out of the core 15.

**Data gaps a reviewer will probe:** a hand-annotated **gold benchmark** for MW block
detection (G5, planned but unbuilt — armours Ch. 5); a **definition-typology** dataset
(the missing classical microstructural dimension); **access-structure** (`Zugriffsstrukturen`)
data; **κ / inter-annotator agreement beyond OBS-T** (with n=1 reviewer, "reviewed" claims —
the book's own selling point — have unmeasurable reliability); a **PROV-O / TEI `@cert`
crosswalk** for the evidence vocabulary.

---

## 7. How to make the book *at Brill*

### 7a. Series (Book A — the monograph)

| Series | Publisher | Vehicle | Reader community | Fit |
|---|---|---|---|---|
| **Brill's Indological Library (BIL)** | Brill | monographs | Indology (language/text) | **Lead target** |
| Gonda Indological Studies (GIS) | Brill | mono + edited | classical Indology | strong; weaker on "digital" |
| **Lexicographica. Series Maior (LSM)** | de Gruyter | mono + edited | lexicography / meta-lexicography | **best method-fit alternative** |
| Digital Linguistics (OA) | de Gruyter | mono + edited (OA) | DH / language resources | good for a "dictionary-as-data" cut |
| HdO Sec. 2 South Asia | Brill | **reference works** | Indology | **Book B (handbook)**, not the monograph |

**Decision (MG, 06-07-2026): primary = de Gruyter *Lexicographica. Series Maior* (LSM);
fallback = Brill's Indological Library (BIL).** LSM (now a De Gruyter Brill imprint) places
the book with the lexicography/meta-lexicography readership — the natural home for the
"evidence-graded lexicography" thesis, with Sanskrit as the case study. Editors: Idalete
Dias, Rufus H. Gouws, Anja Lobenstein-Reichmann, Stefan J. Schierholz; English submissions
accepted (cf. vol. 164 *Internet Lexicography*, 2024). Keep **BIL** ready as the Indology-home
fallback (contact Albert Hoffstädt). Cite Brill's own *Methods in Latin Computational
Linguistics* (McGillivray) and de Gruyter's *Sixty Years of Swedish Computational
Lexicography* (2025) as precedent for a single-tradition computational-lexicography monograph.
**HdO Section 2 is reserved for Book B, the handbook** (a reference-tool series — wrong for a
research monograph).

### 7b. The proposal (what Brill requires)

A Brill book proposal must contain: author; title; aim & scope; **table of contents + a
per-chapter summary**; the **series** you target; primary readership; **comparable/competing
titles with publisher**; **total word count** (incl. notes + bibliography); image/table
count; a **non-Latin-script** note (Devanāgarī/IAST — relevant here); length, timeline,
submission date. Sample chapters are commonly requested at manuscript stage.
[Brill Book Proposal Guidelines](https://brill.com/fileasset/downloads_products/brill_bookproposal_guidelines.pdf).

**Process:** proposal (may go to an external specialist) → draft manuscript → peer review
(1–3 reviewers, single/double blind) → accept / accept-with-revisions / reject. Indicative
time-to-print ≈ a year from accepted final manuscript.
**Contact:** **Albert Hoffstädt**, Senior Acquisitions Editor for Sanskrit/Buddhist Studies
(verify he is still in post via Brill's [Acquisitions Editors](http://www.brill.com/about/contact/acquisitions-editors) page).
**Open Access:** Brill Open, default CC-BY, author keeps copyright; book OA fee is
page-based, quoted individually (secondary sources cite ~€7,000+VAT — verify);
`openaccess@brill.com`.

### 7c. Article-to-book rights (mandatory, because the book reworks the author's articles)

Brill states that re-using **your own** text in **your own** forthcoming monograph needs **no
written permission**. But: Brill runs iThenticate, so **disclose the article base in the
proposal** and acknowledge each source. Copyright differs by where each article appeared —
**Brill-owned journals** (e.g. *Indo-Iranian Journal*) are effectively in-house; **non-Brill
journals** hold copyright under their CTA (most permit self-reuse in a later book, terms
vary). **Deliverable:** a **chapter → article → journal → publisher → copyright-holder →
permission-status** table, built into the proposal. This is the one item that must be
checked article-by-article.

### 7d. Comparables to name in the proposal

Gilliver, *The Making of the OED* (OUP 2016) — the closest genre analog · Considine (ed.),
*The Cambridge World History of Lexicography* (CUP 2019) — the reference frame to engage ·
Klosa-Kückelhaus, *Internet Lexicography* (de Gruyter LSM 164, 2024) — the digital-lexicography
neighbor · Dannélls/Blensenius/Borin (eds.), *Sixty Years of Swedish Computational
Lexicography* (de Gruyter, 2025, OA) — a directly parallel "one tradition as data" model ·
McGillivray, *Methods in Latin Computational Linguistics* (Brill, 2013) — Brill precedent ·
Patkar, *History of Sanskrit Lexicography* (1981) — the topical predecessor this book updates.

---

## 8. Dissertation ⇄ book coordination

MG's framing: **the Brill book and the докторская run in parallel** (not book-after-defense),
and the book is a *lightly reworked English edition of the ~15 articles glued together* — i.e.
the **«по совокупности работ» / article-based** shape.

- There is **no self-plagiarism conflict** between a Russian dissertation deposit and a
  foreign-language monograph: different language, audience, publisher; a dissertation is
  gray literature; reusing one's own thesis in one's own book is the expected norm.
- The only rights question is **per-journal** (§7c), entirely separate from the dissertation.
- A published монография is itself one of the strongest supporting works for a докторская,
  which is precisely why writing the book *alongside* the defense is coherent.
- What changes between the RU dissertation apparatus and the EN book: strip the *положения
  выносимые на защиту* / новизна / ГОСТ machinery; replace with narrative argument + the
  press's author-date house style.

**No dissertation / автореферат file exists in any repo** — the thesis structure lives only
as these monograph outlines. If a formal автореферат is needed for ИЯз РАН, it is a separate
artifact to draft (open item, §11).

---

## 9. Critical path, sequence, risks

**Critical path (what actually gates the book):**
1. **FAIR / DOI sprint** — Zenodo-deposit every dataset the book cites; add `CITATION.cff`
   to the repos still missing it (kosha, SanskritLexicography, SanskritRussian); **re-mint
   the false correction-dataset DOI**; get the DCS denominator DOI (Hellwig sign-off). *This
   is the top blocker; nothing citable ships without it.*
2. **Rights table** — the chapter → article → journal → copyright → permission matrix.
3. **≥1–2 chapters "under review"** at proposal time — the Q3 sprint (A16, A02) already
   delivers this; the proposal can truthfully say "under review."
4. **κ / second-annotator** — one recruitment fixes the "reviewed"-claim reliability gap
   that otherwise undermines the evidence-graded thesis.

**Risks (from the ROADMAP + registry):**
- **Bus factor 1 / burnout** — the plan front-loads infrastructure so the writing window is
  mostly *gluing*, not building.
- **P-numbering drift** — the ROADMAP's P1–P6 ≠ csl-atlas `PUBLICATIONS.md` P1–P6; always
  map chapters through the **A-IDs** here, not P-numbers.
- **Anti-salami clusters** — Ch. 6 itself now merges A02↔A33 (10-07-2026 ruling, no longer
  a cross-chapter risk); Ch. 7/8 (A04↔A35), Ch. 9 (A05↔A03↔A07), Ch. 10/11 (A08↔A50) still
  attack neighboring objects; inside one book they must be *sections that cross-reference*,
  not chapters that re-derive each other.
- **M01 registry entry understates scope** — it says "from A01–A06"; the true source set is
  the 15 above (atlas + MWS + csl-orig + observatory + SanskritLexicography). Reconcile M01.

---

## 10. Open decisions for a human (MG)

**Resolved 06-07-2026:** ✅ the 15 (§2) **approved as proposed** · ✅ series = **de Gruyter
LSM primary, BIL fallback** · ✅ **standard subscription** (not OA).
**Resolved 08-07-2026:** ✅ **A12 authorship = sole-authored** (§2 note; Ch. 15 locks, no swap).

Still open:
1. **Book B (handbook):** confirm HdO Section 2 as its home, and its priority/timing
   relative to Book A.
2. **Автореферат / dissertation apparatus:** is a formal ИЯз РАН thesis document needed, and
   should it be generated from the same article base?

---

## 11. Next actions

**Done 08-07-2026 (H248 execution, Opus 4.8 `claude-opus-4-8`):**
- ✅ **A12 authorship confirmed sole-authored** (§2/§10) — Ch. 15 locks.
- ✅ **Rights table built** →
  [RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md).
  Key finding: all 15 are unpublished drafts ⇒ copyright 100% author-held today; no chapter
  is rights-blocked; the only standing task is a per-venue CTA read *at each article's
  acceptance* (OUP + Nodus rows), with the CC-BY venues clean.
- ✅ **Brill/De Gruyter proposal drafted** →
  [BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md)
  — author, title, aim & scope, series/readership, full ToC + per-chapter summaries,
  length/figures/timeline, comparables, rights disclosure, author open items.
- ✅ **M01 reconciled** in [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)
  to the true 15-article source set (was "from A01–A06").

**Done 10-07-2026 (H505 execution, Fable 5 `claude-fable-5`):**
- ✅ **Literature crosswalk + quality-bar audit** against the 37-work manuals library →
  [LITERATURE_CROSSWALK.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md)
  (grounding map per chapter, gap analysis, competing-works positioning for the proposal,
  comparative part-bridge recommendation, chapter-by-chapter abandonment audit — no cuts;
  original Ch. 2/3/12/13/14 need named reframes [renumbered above], Ch. 7 merge question
  parked as `@DECIDE`). Library index:
  [LEXICOGRAPHY_MANUALS.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/LEXICOGRAPHY_MANUALS.meta.md).

**Ruled 10-07-2026 (MG):** the Ch. 7 `@DECIDE` above is resolved as **(b) — fold into
Ch. 6** as its second half ("senses: inheritance and order"), collapsing the book to
**14 chapters** (§3 chapter list updated above).

**Ruled 13-07-2026 (MG):** the standalone-corpus-methods-chapter fork
([LITERATURE_CROSSWALK.md §4.2](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md))
is resolved as **(b) — a marked section inside Ch. 2** ("The corpus as a bounded witness",
~6–8 pp.), *not* a standalone chapter. The 14-chapter/15-article architecture is unchanged;
the DCS-disclosure + statistical-practice + absence-inference material is written into Ch. 2
at its next revision. Both `@DECIDE` forks from H505 are now closed.

**Done 13-07-2026 (H846 execution, Opus 4.8 `claude-opus-4-8`):**
- ✅ **Ch. 1 converted journal→book** →
  [chapters/ch01_latin_discretion_screen.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch01_latin_discretion_screen.md)
  (from A36, the Latin discretion-screen note). Abstract/venue apparatus stripped, register
  unified to the book's, the Ferri (Servius decorum) + Baalbaki (Arabic correctness-screen
  contrast) grounding and the Europe-specific honesty clause woven in per crosswalk §1/§4.1,
  cross-references remapped to sibling chapters (Ch. 2 method, Ch. 4/7 kośa contrast, Ch. 6
  senses, Ch. 13 Renou); every count and table carried over unchanged.

**Done 13-07-2026 (H851 execution, Opus 4.8 `claude-opus-4-8[1m]`):**
- ✅ **Ch. 4 converted journal→book** →
  [chapters/ch04_kosha_macrostructure.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch04_kosha_macrostructure.md)
  (from A06, *Order Is the Dictionary*, csl-atlas source). Abstract/keywords stripped, the
  companion-paper "P-numbers" remapped to book chapters (P1→Ch. 2, P4→Ch. 7), the crosswalk
  §1 grounding woven in (Vogel already primary; added Baalbaki's *mubawwab/muǧannas* + three
  formal orders, Hartmann & James access structures, Jackson/Hüllen European onomasiological
  tradition, Partridge, Dickey), the two draft "author to verify" placeholders resolved into
  a clean footnote (Wilson-1819 descent kept as asserted lineage, not quantified). Every
  count and table carried over unchanged. **4 of 14 chapters now in book form** (ch01, ch02,
  ch04, ch05).

**Still to do:**
1. Run the **FAIR/DOI sprint** (Zenodo deposits + re-mint the false correction-dataset DOI
   + Hellwig DCS sign-off) — the DOI *minting* is a human/credentials @DO; the mechanical
   **CITATION.cff** add to kosha / SanskritLexicography / SanskritRussian is a Fable/Sonnet
   follow-on (those 3 lack a `.cff`; atlas/observatory/orig/MWS already have one).
2. Convert the two most-mature chapters (A16, A01) to book form as sample chapters
   (Fable/Sonnet-tier mechanical conversion).

_Dr. Mārcis Gasūns_
