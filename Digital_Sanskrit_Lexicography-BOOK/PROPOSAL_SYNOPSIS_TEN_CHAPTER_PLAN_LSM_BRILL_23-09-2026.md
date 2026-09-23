# Book proposal draft — *Sanskrit Lexicography in the Digital Age: Evidence, Inheritance, and Two Traditions*

_Created: 23-09-2026 · Last updated: 23-09-2026_

Synopsis, rationale, ten-chapter plan with abstracts, market and timeline for the monograph
sketched in
[ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
Part II (the thesis) and Part III (the P1–P6 paper pipeline and the ten-chapter sketch).
Target series: De Gruyter *Lexicographica. Series Maior* (LSM), fallback Brill's Indological
Library. Handoff
[H5323](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5323-Fable_SanskritLexicography_book-proposal-synopsis-draft_23.09.26.md)
(epic E014, roadmap Q4 2026 item 4 «Book proposal drafted»).

> **Status: DRAFT, not sent.** Every readiness figure below is copied verbatim from the
> `Ready` column of [Uprava ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)
> as read from `origin/main` on 23-09-2026 (status table last compiled 15-08-2026, rows updated
> through 06-09-2026). Nothing is rounded up. Where a chapter has no source paper it is marked
> **new** and carries no readiness figure. `[VERIFY]` marks the author's calls.

## 0. Relation to the existing M01 proposal — read this first

A proposal for this monograph already exists:
[BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md)
(registry **M01**, 3/5, title *Digital Sanskrit Lexicography: The Dictionary as a Layered
Evidence Graph*), built 08-07-2026 from
[BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
with a **14-chapter** architecture gluing 15 articles, all 14 chapters already converted to
book form under
[chapters/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK/chapters).
BOOK_PLAN §0 states that it *supersedes* the roadmap's ten-chapter sketch.

This file does what H5323 asks — the **ten-chapter plan of roadmap Part III, mapped to P1–P6
with real readiness** — and does not overwrite M01. The two plans are the same book under two
tables of contents; the crosswalk is:

| Roadmap ch. | Roadmap content | M01 chapter(s) carrying the same material |
|---|---|---|
| 1 history & two civilizations | new | Introduction (new) + Ch. 1 (A36) |
| 2 method: evidence-graded lexicography | new, from Part II | Ch. 2 (A01, `ch02_measurement_framework.md`) |
| 3 ← P1 MW block economy | A16 | Ch. 5 (A16) |
| 4 ← P2 sense inheritance | A02 | Ch. 6 (A02 + A33) |
| 5 ← P3 two citation registers | A08 (+ A18) | Ch. 10 (A08) |
| 6 ← P4 indigenous microstructure | A30 | Ch. 7 (A04) — A30 is the SKD/VCP companion |
| 7 macrostructure & the kośa type | new, from the gap list | Ch. 3 (A40) + Ch. 4 (A06) |
| 8 ← P5 fifty thousand corrections | A31 (+ A12) | Ch. 14 (A12) |
| 9 ← P6 learner's reading layer | A32 | **absent from M01** |
| 10 FAIR infrastructure & four-repo architecture | new | Conclusion (new); A27 material |

What the ten-chapter plan has that M01 lacks: Ch. 9 (the learner's layer, P6) and a
standalone FAIR/infrastructure chapter. What M01 has that the ten-chapter plan lacks: the
Pāṇinian derivation chapter (A35), the cross-reference stemmatics chapter (A05), the
citation-frequency graph (A50), the apparatus-not-errors forensic chapter (A10), Renou's
registers (A34). **Which table of contents goes to the series editor is a human decision**
(§8).

## 1. Synopsis

A digital dictionary is not a text but a **layered evidence graph**. Every lexicographic
statement — headword, sense, gender, citation, cross-reference — is a node carrying its
source dictionary and convention, an explicit evidence grade
(`observed | derived | inferred | reviewed`), corpus attestation where one exists, and review
provenance. This book states that model and tests it on the one language that possesses
**two parallel lexicographic civilizations**: the European scholarly dictionaries of Sanskrit
(1832–1957: Wilson, the Petersburg *Wörterbücher*, Monier-Williams, Apte) and the indigenous
*kośa* / Pāṇinian tradition, nineteen centuries deep, now available as forty-four digitized
dictionaries beside a 5.6-million-token tagged corpus (DCS).

The argument runs in three movements. **Evidence** (Ch. 2–3): how a dictionary entry is
anatomized into countable blocks, how each claim is graded, and what a gold sample says about
the grading (MW: 286,561 entries; block detection macro F1 0.876, κ 0.817 on a 200-entry
double-annotated sample). **Inheritance** (Ch. 4–5, 8): what the European family copied,
condensed and cited across 125 years (cited senses survive at 0.762 against 0.591 for uncited
ones; descendants condense rather than expand), how two citation registers — the European
source apparatus and the indigenous *iti* quotation — coexist inside one entry, and what
52,498 corrections over twelve years of collaborative maintenance reveal about where dictionary
error actually originates. **Two traditions** (Ch. 6–7, 9): the indigenous microstructure of
Śabdakalpadruma and Vācaspatya recovered on its own terms (the «zero means nothing» doctrine),
the *kośa* as a macrostructural type with no European counterpart, and a frequency-graded
reading layer that shows what the graph is *for* — a learner sees, per lemma, its corpus band,
its survival-ranked senses and its paradigm cell. Ch. 10 closes with the FAIR infrastructure
that makes every figure in the book reproducible from a committed dataset with a DOI.

Method leads, Sanskrit is the case study. The book speaks to lexicographers and
meta-lexicographers first (the EURALEX / IJL readership of the target series), to
digital-humanities and language-resource researchers second, and to Indologists third.

## 2. Rationale against ELEXIS, Lexonomy and TEI Lex-0

The three reference points a lexicography editor will raise, and where this book stands to each:

1. **ELEXIS** (European Lexicographic Infrastructure) standardizes *interoperability*: a
   dictionary matrix, a sense-alignment benchmark, shared tooling. It says how dictionaries
   are linked, not how much any statement in them may be trusted. This programme has no ELEXIS
   linkage yet (roadmap gap G2, still open on 23-09-2026); the book treats ELEXIS as the
   infrastructure its graph would plug into, not as a competitor. The ELEXIS monolingual
   word-sense-alignment task is already named in M01 Ch. 2 as the benchmark tradition the
   sense-inheritance measures descend from.
2. **Lexonomy** (the ELEXIS dictionary-writing platform) standardizes *editing*: an XML entry
   is written, validated against a schema, and published. Its unit is the entry as authored.
   This programme's unit is the entry as **evidence**: machine output is immutable, corrections
   live in a separate adjudication layer with a canonical status vocabulary, and every reviewed
   claim reports inter-annotator agreement. Lexonomy is named in the repo as a candidate
   front-end for the review pool ([RussianTranslation/DICTIONARY_CHAIN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DICTIONARY_CHAIN.md)),
   i.e. as a consumer of the graph.
3. **TEI Lex-0** standardizes *encoding*. The programme ships a Lex-0 pilot in
   [csl-standards](https://github.com/sanskrit-lexicon/csl-standards) covering a Western (MW)
   and an indigenous *kośa* (SKD) entry with a CI validation gate
   ([docs/TEI_LEX0_PILOT.md](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/TEI_LEX0_PILOT.md)),
   and the pilot's finding is the book's point: Lex-0 has no slot for the indigenous
   sense/citation fusion (an *iti*-unit is a sense and a citation at once), so the export
   documents a **loss**. The gap note is H5322 (sibling of this handoff); Ch. 10 cites it.

The one-sentence version for the proposal: *ELEXIS, Lexonomy and TEI Lex-0 standardize the
encoding and exchange of dictionaries; this book standardizes their epistemics — a graded,
reviewable, corpus-anchored evidence status per statement — and shows that an indigenous
lexicographic tradition can be first-class structured data on the same graph.* No existing
title grades evidence per lexicographic statement, and none treats a non-European tradition
as data beside the European one (comparables in §5).

## 3. The ten chapters — abstracts, source paper, real readiness

Readiness is the ARTICLES.md `Ready` figure on 23-09-2026. «Owed before "under review"» is
what that row itself lists as pending. Child handoffs are E014 rows opened 23-09-2026.

### Ch. 1 — Two civilizations: a history of Sanskrit lexicography from *Amarakośa* to Cologne — **new**

From the versified synonymic *kośa* (Amarakośa: 24 *varga*s, 5,590 synsets, a 1,500-year-old
native semantic-domain organization) and the Pāṇinian *dhātupāṭha* through Wilson (1819), the
Petersburg *Wörterbücher* (1855–1889), Monier-Williams (1899) and Apte, to the Cologne Digital
Sanskrit Lexicon (1997–) that put forty-four of them in one encoding. The chapter's claim: the
two traditions never merged — the European dictionaries *cite* the indigenous ones (Ch. 5) and
mine them with the source deleted — and the digital corpus is the first place they meet as
data. Source: new prose; M01 Ch. 1 (A36, the Latin-discretion screen) and the M01 Introduction
supply the 19th-century half. No readiness figure quoted (no single source paper).

### Ch. 2 — Method: evidence-graded lexicography — **new, from roadmap Part II**

The layered-evidence-graph model; the four-grade vocabulary
(`observed | derived | inferred | reviewed`) and its crosswalk to W3C PROV-O and TEI
`@cert`/`@resp` (H5301); the lineage from Apresyan's systematic lexicography and integral
description to the ACL counterparts (WordNet, FrameNet, PropBank, VerbNet, Word Sketches)
and the synthesis: the rationalist grid supplies the axes, the corpus fills and falsifies them.
The chapter also carries the reproducibility contract every later figure obeys (dataset
envelope with `schemaVersion / generatedAt / sourcePath / recordCount`, validators, κ for every
reviewed claim, build commit per figure). Source: roadmap Part II; M01
`ch02_measurement_framework.md` (A01) exists as a convertible draft. No readiness figure
quoted (marked new in the roadmap). Open `@DECIDE` feeding it: a controlled register of
Sanskrit lexicographic types (H5335).

### Ch. 3 — The block economy of Monier-Williams — **← P1 = A16, readiness 5/5**

A data-grounded microanalysis of all 286,561 MW entries: the entry decomposed into countable
blocks (headword, grammar, gloss, source apparatus, cross-reference), their distribution, and
what MW's economy of blocks says about the 19th-century entry as a genre. Validated by the G5
gold sample (200 entries, two annotators: macro precision 0.860, recall 0.870, F1 0.876, mean
κ 0.817). Source: MWS
[papers/microanalysis/PAPER.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/PAPER.md),
venue IJL. **Owed before "under review":** the author's citation-dossier read-and-sign, the
`#195` merge, IJL formatting at submission (A16 row); submission-pack refresh is H5314. Not
yet submitted as of the ARTICLES.md read.

### Ch. 4 — Sense inheritance in the Sanskrit dictionary family — **← P2 = A02, readiness 4/5**

Condensation, survival and the citation advantage across the European family 1822–1957
(R2 alignments): sense granularity is a family trait (r≈0 trend), cited senses survive at
0.762 against 0.591 for uncited, descendants condense rather than expand; drift indices per
edge. Source: csl-atlas
[docs/articles/paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md),
venue Lexicographica. Author pass executed 06-09-2026. **Owed:** MG read-and-sign of the
author pass and the SKD adjudication (A02 row); the review-pool fold is H5316. Note for the
chapter: the by-repo entry records the pooled survival pair corrected to 0.768 (82 cited),
so the chapter must quote the post-correction figure, not the roadmap's 0.762.

### Ch. 5 — Two citation registers: European source apparatus and indigenous *iti* quotation — **← P3 = A08, readiness 4/5 (+ A18, 3/5)**

Register A (`<ls>` source sigla, 27 canonical, 138 aliases) against Register B (*iti*
quotation) across nine dictionaries; the two registers as two epistemologies of warrant. The
MW companion (A18) stratifies all 320,828 MW citations into five evidentiary strata (attested
18.96 % · bare 59.35 % · hedge 12.53 % · authority 6.02 % · relative 3.15 %) and shows that
`<ls>L.</ls>` is Register-B *kośa* content in a Register-A slot with the source deleted — the
book's cleanest proof that the two traditions were never separate. Sources: csl-atlas
[paper_citation_registers.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md)
(A08, 4/5, venue *Dictionaries* per roadmap; ARTICLES lists IJL) and MWS
[A18_citation_registers_paper.md](https://github.com/sanskrit-lexicon/MWS/blob/master/papers/p3_citation_registers/A18_citation_registers_paper.md)
(A18, 3/5, disposition GUIDE per MG 29-07-2026). **Owed:** A08 §4 figures confirmed stale on
04-09-2026 (totals 1,245,644 → 1,517,609; locator 59.3 % → 66.8 %) — revision owed before
submission; MG read-and-sign; SKD *iti* adjudication. A18 author pass is H5326.

### Ch. 6 — When zero means nothing: the indigenous microstructure of Śabdakalpadruma and Vācaspatya — **← P4 = A30, readiness 3/5**

The doctrine that marker-absence in SKD/VCP is not content-absence; the record-level entry
template recovered from the front-matter *anubandha* key; *iti*-unit fusion SKD 53.3 % vs VCP
77.6 %; the H6 structural register. Source:
[papers/A30_skd_vcp_microstructure_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_skd_vcp_microstructure_note.md)
(full draft merged 17-07-2026, author pass 06-09-2026). Venue is an open `@DECIDE` (IJL vs
WSC 2027, brief H5327). **Owed to 4/5:** hostile referee pass, SKD *iti* adjudication sample,
edition-facts check, MG read-and-sign (A30 row). Not selected for the PLUS5 prestige pool
(MG 29-07-2026) — it publishes on its own schedule, which suits a book chapter.

### Ch. 7 — Macrostructure and the *kośa* type — **new, from the roadmap gap list**

The European/indigenous macrostructure contrast, the roadmap's «most original axis»: the
thematic, versified, synonymic *kośa* (AMAR/ARMH/ABCH) as a macrostructural type with no
European counterpart, beside three paper-grade holes the gap list names as unstudied —
access structures (Wiegand's *Zugriffsstrukturen*: alphabetization regimes, homonym order,
anusvāra/visarga in sort order), lemmatization policy across the seven European dictionaries,
and megastructure (front/back matter as data, extending the SKD *anubandha*-key method to all
nine). Existing material: A06 *Order is the dictionary* (csl-atlas kośa macrostructure, 4/5,
author pass 06-09-2026, awaiting MG sign) and A40 headword inventory (M01 Ch. 3). Builders
opened 23-09-2026: kośa macrostructural model H5328, ARMH/ABCH stubs to data chapters H5329,
access-structures census H5331, lemmatization census H5332, megastructure catalogue
H5324/H5325. No readiness figure quoted for the chapter as a whole (its census half has no
paper yet).

### Ch. 8 — Fifty thousand corrections: an error typology of twelve years of collaborative maintenance — **← P5 = A31, readiness 3/5 (+ A12, 4/5)**

The OBS-T dataset — 52,498 correction events, released snapshot, concept DOI
10.5281/zenodo.21346705 — read on two axes: the *type* axis (A12, csl-observatory, canonical
two-axis manuscript, κ measured at 0.906 on the blind-LLM second-annotator pilot) and the
*origin* axis (A31: print-source / digitization / conversion-markup, per-class precision
0.90–0.97 on a 120-row hand-checked sample). No dictionary project has twelve years of
correction telemetry; the chapter argues that most «errors» are apparatus. Sources:
[papers/A31_fifty_thousand_corrections_error_origin_typology.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A31_fifty_thousand_corrections_error_origin_typology.md)
(Lexikos) and csl-observatory
[paper-obs-t-error-typology.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md)
(LREC-COLING). **Owed:** A31's origin-axis κ — one agent run of the cleared protocol on the
120-row sample, folded in by H5313 (second-annotator sheet H5312); Lexikos house style.

### Ch. 9 — A frequency-graded reading layer for Sanskrit learners — **← P6 = A32, readiness 1/5**

The graph as a *view*: per lemma, its DCS frequency band, best-attested senses ranked by the
survival evidence of Ch. 4, Whitney root and *gaṇa*, paradigm cell — joined from corpus,
grammar and seven dictionaries and shipped as a public page; then a task-based user study
(find-the-right-sense, timed, against plain Cologne lookup) with the review-pool students
(roadmap G7). Audience personas from the DharmaMitra workshop intake: translator, researcher,
student, practitioner, hobbyist. Source: A32 is an **idea** (1/5, no artifact of its own).
**Owed:** everything — learner's-layer v1 spec/build/page H5317–H5319, user-study protocol
H5336, paper scaffold H5337, then the study itself (Q2 2027). This is the chapter the proposal
must present honestly as *planned*, with the v1 page as the deliverable that exists at
proposal time.

### Ch. 10 — FAIR infrastructure and the four-repo architecture — **new**

The 2026-06-03 split of evidence (csl-atlas), export (csl-standards), corpus (VisualDCS) and
telemetry (csl-observatory); immutable generated data with human review overlays; the
serialization standard for the Petersburg family (A27, TEI / OntoLex / MDF, 4/5) and the
Lex-0 loss report (H5322); the correction loop as a GitHub maintenance ecosystem (A15, 4/5);
what FAIR cost and what it bought. State on 23-09-2026, quoted not projected: `CITATION.cff`
and `.zenodo.json` in all four repos with most ORCID iDs; two DOIs minted in the wider
programme (OBS-T 10.5281/zenodo.21346705, 16-08-2026; kosha data-v0.4.0
10.5281/zenodo.22102090, 25-08-2026); atlas data release v1 **not yet** on Zenodo (H5304,
H5305), PROV-O crosswalk page not yet published (H5301), per-dataset licence field not yet
audited (H5302/H5303). No readiness figure quoted (no single source paper; A27 and A15 feed).

## 4. Readiness ledger — the stop-condition table

| Ch. | Source | Ready (ARTICLES.md) | State of the manuscript | Blocking human act |
|---|---|---|---|---|
| 1 | new | — | not drafted; M01 Ch. 1 + Introduction reusable | — |
| 2 | new (Part II) | — | M01 `ch02_measurement_framework.md` reusable | H5335 `@DECIDE` types register |
| 3 | A16 (P1) | **5/5** | ready-to-send, not submitted | citation-dossier sign (~20 min) |
| 4 | A02 (P2) | **4/5** | author pass done 06-09 | read-and-sign + SKD adjudication |
| 5 | A08 (P3) · A18 | **4/5** · **3/5** | full drafts; A08 §4 stale | read-and-sign; §4 revision |
| 6 | A30 (P4) | **3/5** | full draft, author pass done 06-09 | venue `@DECIDE` (H5327) |
| 7 | new (gap list) · A06 | — · **4/5** | A06 author pass done 06-09; censuses opened | read-and-sign A06 |
| 8 | A31 (P5) · A12 | **3/5** · **4/5** | full drafts; A31 κ pending | none (agent run H5313) |
| 9 | A32 (P6) | **1/5** | idea only | none yet; study needs students |
| 10 | new · A27 · A15 | — · **4/5** · **4/5** | not drafted; feeders at 4/5 | Zenodo connection for atlas v1 |

Sum, stated plainly: of the six paper-backed chapters, **one is at 5/5, two at 4/5, two at
3/5, one at 1/5**; none is submitted, none is under review. The roadmap's condition for the
proposal — «P1–P2 under review» — is therefore **not yet true** on 23-09-2026 and the
proposal's own timeline (§6) is built from that fact, not from the roadmap's hope.

## 5. Market

Series, readership and comparables are already assembled in
[BRILL_PROPOSAL.md §4 and §7](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md)
and are not repeated at length. The points a series editor weighs, in this book's terms:

1. **Series fit.** LSM is the flagship meta-lexicography series; English submissions accepted
   (vol. 164, *Internet Lexicography*, 2024). The method-first framing puts this book beside
   *Internet Lexicography* and *Sixty Years of Swedish Computational Lexicography* (De Gruyter,
   2025) rather than in the Indology list. `[VERIFY editors in post: Dias, Gouws,
   Lobenstein-Reichmann, Schierholz.]`
2. **Primary readership.** Academic lexicographers and meta-lexicographers (EURALEX / IJL /
   Lexicographica / Lexikos / *Dictionaries* — the six chapters' own venues), language-resource
   and DH researchers (the FAIR / TEI / ELEXIS audience of Ch. 2 and Ch. 10).
3. **Secondary readership.** Indologists and Sanskritists (Ch. 1, 6, 7 are the first
   quantitative treatments of the *kośa* and of SKD/VCP microstructure in English); historians
   of scholarship (Ch. 4–5, 8).
4. **Course and library use.** Ch. 2 (method) and Ch. 9 (learner's layer) are teachable
   standalone; the datasets behind every figure are open, so the book doubles as a
   reproducible lab for a digital-lexicography seminar.
5. **Gap filled.** No comparable title grades evidence per lexicographic statement; none treats
   an indigenous tradition as first-class data beside the European one; none has a
   twelve-year correction-telemetry dataset. The topical predecessor (Patkar 1981) predates
   the corpus, the digitization and the maintenance record.
6. **Access model.** Standard subscription, not Open Access (MG 06-07-2026), unchanged.

## 6. Timeline — proposal, contract, manuscript

Anchored to the readiness ledger, not to the roadmap calendar. Dates are proposals for the
author to confirm `[VERIFY]`.

| When | Milestone | Precondition (from §4) |
|---|---|---|
| Q4 2026 | P1 (A16) submitted to IJL; P2 (A02) submitted to Lexicographica | two ~20-min sign-offs by the author; H5314, H5316 |
| Q4 2026 | this draft revised into the sent proposal (one ToC chosen, §8) | MG rulings in §8 |
| Q1 2027 | **proposal submitted** to LSM with «P1 and P2 under review» true and P1 + one of Ch. 2/Ch. 3 as sample chapters | P1/P2 acknowledged by the journals |
| Q1 2027 | P3 (A08) submitted; Ch. 7 censuses (H5324–H5332) landed as data | A08 §4 revision |
| Q2 2027 | contract; P5 (A31) and P6 (A32) submitted; new chapters 1, 2, 7, 10 drafted | κ fold (H5313); learner's layer v1 + G7 study |
| Q3–Q4 2027 | full manuscript delivered `[VERIFY]` | chapters 3–6, 8 revised from journal form; Ch. 9 from the study |

Length and figures as in BRILL_PROPOSAL §6 (~320–380 pp., ~30–40 figures each anchored to a
committed dataset). Risk carried from roadmap Part V: if the series wants two *published*
chapters rather than two under review, Q1 2027 slips to Q3 2027; the mitigation is unchanged
(Lexicographica and *Dictionaries* as second homes for P1).

## 7. What this draft deliberately does not do

1. It does not replace M01's BRILL_PROPOSAL.md; it is the roadmap-side twin (§0).
2. It quotes no readiness figure for a chapter marked new, and does not average, round or
   promote any figure from ARTICLES.md.
3. It does not restate the author, rights disclosure or comparables sections — those are
   complete in BRILL_PROPOSAL §1, §7, §8 and
   [RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md)
   and apply to both ToCs unchanged.
4. It is not sent, not formatted to the Brill/De Gruyter proposal form, and carries no cover
   letter.

## 8. Open decisions for a human (MG)

1. **One table of contents.** The ten-chapter plan (this file) or M01's fourteen — or M01's
   fourteen plus the two chapters only this plan has (learner's layer, FAIR infrastructure),
   which would make sixteen. The series editor sees one ToC. Recommendation: send M01's
   fourteen and add Ch. 9 (learner's layer) as a fifteenth once the v1 page exists, since M01's
   chapters are already in book form and P6 is at 1/5; keep the FAIR material in the
   Conclusion. What would reverse it: a series-editor preference for a shorter, six-paper book.
2. **Title.** *Sanskrit Lexicography in the Digital Age: Evidence, Inheritance, and Two
   Traditions* (roadmap) or *Digital Sanskrit Lexicography: The Dictionary as a Layered
   Evidence Graph* (M01). The roadmap title names the three movements of §1; the M01 title
   names the method. Recommendation: the M01 title, for the same series-fit reason as §5.1.
3. **Submission trigger.** Submit the proposal when P1 and P2 are *acknowledged* under review
   (Q1 2027 in §6), or now with «submitted» chapters only. Recommendation: wait for the two
   acknowledgements; they cost two sign-offs the author already owes.

## 9. Provenance

Drafted 23-09-2026 by Fable 5.1 (`claude-fable-5-1`) for H5323, worker 1 on executor
Claude/c1, in a worktree off `origin/master`. Inputs read this pass: roadmap Parts I–V,
E014 epic file, ARTICLES.md rows A02, A06, A08, A12, A16, A18, A27 (by-repo), A30, A31,
A32, M01 (from `origin/main`), BRILL_PROPOSAL.md, BOOK_PLAN.md §0 and §3, csl-standards README
and `data/pilot/tei-lex0/`. Nothing was fetched from the network.

_Гасунс_
