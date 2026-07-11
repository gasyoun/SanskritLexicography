# Researcher Manual — SanskritLexicography

_Created: 10-07-2026 · Last updated: 11-07-2026_

For the **lexicographer, digital-humanities researcher, or historian of
dictionaries** who wants to understand the intellectual programme here, cite its
data, or build on its method. To operate the repo, see the
[Maintainer Manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md);
to reuse the raw data programmatically, see the
[Data-Reuse Manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md).

---

## 1. The thesis: evidence-graded lexicography

The programme's one sentence (from
[ROADMAP_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_2026_2027.md),
Part II):

> A digital dictionary is not a text but a **layered evidence graph**. Every
> lexicographic statement — headword, sense, gender, citation, cross-reference —
> is a node carrying (a) its source dictionary and convention, (b) an explicit
> evidence grade, (c) corpus attestation where available, and (d) review
> provenance.

What is genuinely new versus existing DH lexicography (ELEXIS, Lexonomy, TEI
Lex-0 projects): they standardize *encoding*; this programme standardizes
*epistemics* — graded, reviewable, corpus-anchored evidence per statement. The
in-house evidence vocabulary is `observed | derived | inferred | reviewed`, with
a chart-trust template (Evidence · Limitations · Validation · Owner · Next use).
Publishing per-claim epistemic status is *ahead* of most published DH dictionary
projects.

**The two-civilizations axis** is the most original framing: Sanskrit has two
parallel lexicographic traditions — the European (Petersburg/Monier-Williams/
Apte, 1832–1957) and the indigenous (kośa + Pāṇinian: Śabdakalpadruma,
Vācaspatyam, Amarakośa). The programme models them as **parallel evidence
systems**, not flattened into one format. The **zero-meaning doctrine** — refusing
to read marker-absence in SKD/VCP as content-absence, and recovering the
indigenous apparatus on its own terms — is methodologically the centre of gravity.

## 2. The spine (already exists in pieces)

```
Whitney roots (938)  ──┐
DCS lemmas + freq    ──┼──►  Lemma spine (SLP1 + homonym key)
28.5k lemma dossier  ──┘          │
                                  ├── sense layer   (R2 alignments, evidence-graded)
                                  ├── grammar layer (gaṇa/pada/transitivity, Whitney classes)
                                  ├── citation layer (canonical sigla + aliases; <ls> + iti)
                                  └── review layer  (community adjudication, κ-measured)
```

The learner's reading layer is then just one *view* over the graph: filter by
DCS frequency band, rank senses by survival evidence, surface the paradigm cell.

## 3. The paper pipeline (feeds the book chapter-for-chapter)

The publication plan (roadmap Part III). Primary venue class = lexicography
journals (IJL, Lexicographica, Lexikos, Dictionaries); the book is an
English article-based monograph.

| # | Working title | Venue | Submit |
|---|---|---|---|
| P1 | *The block economy of Monier-Williams: a data-grounded microanalysis of 286,561 entries* | IJL | Q3 2026 |
| P2 | *Sense inheritance in the Sanskrit dictionary family: condensation, survival, and the citation advantage* | Lexicographica | Q4 2026 |
| P3 | *Two citation registers: European source apparatus and indigenous* iti *quotation in nine Sanskrit dictionaries* | Dictionaries | Q1 2027 |
| P4 | *When zero means nothing: recovering the indigenous microstructure of Śabdakalpadruma and Vācaspatya* | IJL / WSC 2027 | Q1–Q2 2027 |
| P5 | *Fifty thousand corrections: an error typology of twelve years of collaborative dictionary maintenance* | Lexikos | Q2 2027 |
| P6 | *A frequency-graded reading layer for Sanskrit learners: joining corpus, grammar, and seven dictionaries* | Lexikos (pedagogical) / eLex 2027 | Q2 2027 |

**Book** (de Gruyter *Lexicographica Series Maior* or Brill): *Sanskrit
Lexicography in the Digital Age: Evidence, Inheritance, and Two Traditions* —
draft plan + first chapters in
[Digital_Sanskrit_Lexicography-BOOK/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK)
([BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md),
[BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md);
2 chapters drafted so far). Cross-repo paper status is tracked in
[Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md);
working notes/reviews live in
[papers/](https://github.com/gasyoun/SanskritLexicography/tree/master/papers).

## 4. Research objects and datasets you can cite

| Object | What it lets you study | Where |
|---|---|---|
| Petersburg layer model | How a PWG entry is assembled from up to 5 dictionary layers; ~36% of the headword union has *no* PWG record (PW-only is 24%, not an edge case) | [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md) |
| Cross-dictionary article study | Full microstructural comparison of one headword (agni, anya, akṣara, ananta) across dictionaries — verbatim / IAST / per-sense / corpus-RU views | [article-comparison/](https://github.com/gasyoun/SanskritLexicography/tree/master/article-comparison) |
| Headword union | 323,425 headwords across 15 csl-orig dicts with per-dict provenance + gender; feminines folded | [HeadwordLists/union/UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md) |
| Reverse dictionary | ~266,820-headword reverse index merging ~30 sources (1822–2005) — word-formation, verse endings, suffix study; a genuine Indological *desideratum* | [ReverseDictionary/](https://github.com/gasyoun/SanskritLexicography/tree/master/ReverseDictionary) |
| Indische Sprüche | 7,537 Böhtlingk gnomic verses (Deva + IAST + German + source attribution) — a clean Sa→De gnomic parallel corpus | [IndischeSprueche/](https://github.com/gasyoun/SanskritLexicography/tree/master/IndischeSprueche) |
| Sa→Ru translation memory | Graded (A/B/C) Sanskrit–Russian TM, TMX 1.4b exportable; FAIR release gated on rights | [RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/README.md) |
| Particle syntax | Positional classification of 16 Sanskrit particles (Whitney–Speyer–Gonda–Apte line; Zaliznyak positional schema) | [Syntax-Lectures/](https://github.com/gasyoun/SanskritLexicography/tree/master/Syntax-Lectures) |
| Reference literature map | 65 sources tagged by which dictionary/pipeline/paper they serve, with reverse lookup | [literature/md/INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/INDEX.md) |

## 5. The epistemic registries as a research method

The nine root registries are not bookkeeping — they *are* the reproducibility
apparatus a DSH/lexicography reviewer asks for and rarely gets. Cite findings by
their stable `§N` number:

- [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  — measured, evidence-backed facts (live dashboard at
  <https://gasyoun.github.io/SanskritLexicography/findings/>). Examples relevant
  to methodology: unaccented DCS cannot distinguish present class I from VI
  (§8 — 117 spurious corpus-derived additions reverted); no printed frequency
  dictionary of Sanskrit exists (§6 — DCS-frequency ordering is genuine
  innovation); PWG article size confounds every per-entry statistic (§67).
- [ASSUMPTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) ·
  [CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) ·
  [GAPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) ·
  [DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) ·
  [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) ·
  [STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md) ·
  [GLOSSARY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md)
  — the acts FINDINGS can't hold: what the programme *relies on*, where sources
  *disagree*, what is *not yet measured*, what was *abandoned* (and why), how to
  *reproduce* a heavy result, what is *decaying*, and how terms are *defined*.

For a reviewer or a co-author, DEAD_ENDS and CONTRADICTIONS are the most
valuable: they record negative results (e.g. body/reverse-headword mining
rejected at 38.6% precision; grammar-in-prompt does not improve DE→RU MT) so the
next study doesn't repeat them.

## 6. FAIR gaps — read before you cite

The programme's own audit (roadmap Part I) is honest about what is *not* yet at
the highest standard. The load-bearing caveats for a citing author:

- **G1 — persistent identifiers.** No dataset DOIs yet, `CITATION.cff` being
  rolled out, ORCID registered ([0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)).
  Data is *findable on GitHub* but full journal-grade citability (Zenodo DOI per
  release) is in progress. Cite the exact commit until a DOI exists.
- **G2 — standards exports deferred.** TEI Lex-0 / OntoLex-Lemon are planned in
  csl-standards; a validated export does not exist yet. If your work needs TEI,
  it isn't here today.
- **G4 — single-reviewer bottleneck.** Reviewed claims were largely single-keyed;
  inter-annotator agreement (κ) is being retrofitted via a community review pool.
  Treat `reviewed`-graded claims as author-adjudicated unless a κ is reported.
- **G5 — regex structure detection has no published gold standard yet** (a
  200-entry double-annotated MW sample is planned as a P1 appendix).

## 7. Provenance and how to reference

- Large reference assets carry provenance in
  [REFERENCES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/REFERENCES.md)
  (source, date, producer, size).
- The canonical data-hub manifest for cross-repo derived datasets is
  [kosha/data/manifest/datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json);
  the project dependency map is
  [Uprava/PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md).
- Author byline for citation: **Mārcis Gasūns**, ORCID
  [0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X). Several
  subprojects ship a `CITATION.cff` (e.g.
  [ReverseDictionary/CITATION.cff](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CITATION.cff)).

_Dr. Mārcis Gasūns_
