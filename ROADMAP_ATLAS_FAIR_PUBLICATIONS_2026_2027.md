# Digital Sanskrit Lexicography 2026–2027
## Review of csl-atlas, a research programme, and a 12-month publication roadmap

_Created: 12-06-2026 · Last updated: 14-07-2026_

Decisions baked in: primary venue = lexicography journals (IJL, Lexicographica, Lexikos, Dictionaries); book = English article-based monograph; student deliverable = frequency-graded learner's reading layer; review capacity = student/community review pool.

---

## Part I — Review of csl-atlas against digital-humanities standards

### What already meets or exceeds the field's standards

1. **Evidence labelling** (`observed | derived | inferred | reviewed`, docs/EVIDENCE_LABELS.md) plus the chart trust template (Evidence | Limitations | Validation | Owner | Next use) is *ahead* of most published DH dictionary projects. Almost no lexicographic resource publishes per-claim epistemic status.
2. **Deterministic reproducibility**: every dataset carries `schemaVersion / generatedAt / sourcePath / recordCount / assumptions / warnings`; validators and 147 tests gate builds. This is the reproducibility bar DSH reviewers ask for and rarely get.
3. **Immutable generated data + human review overlays** (review-report.schema.json, canonical status vocabulary) is a genuinely novel pattern — machine output is never silently edited; corrections live in a separate adjudication layer.
4. **Boundary discipline** (BOUNDARY_RULES.md, the 2026-06-03 four-repo split: atlas / standards / VisualDCS / observatory) — clean separation of evidence, export, corpus, and observability concerns.
5. **The zero-meaning doctrine** (MICROSTRUCTURE_ZERO_MEANING.md): refusing to read marker-absence in SKD/VCP as content-absence, and building M4 to recover the indigenous apparatus on its own terms, is methodologically the most important thing in the repo.

### Gaps against the highest DH standard (FAIR / CLARIN / ELEXIS norms)

| # | Gap | Severity | Fix |
|---|---|---|---|
| G1 | **No persistent identifiers anywhere**: no dataset DOIs, no CITATION.cff, 0/16 contributors with ORCID (observatory's own finding). The data is *findable on GitHub* but not *citable* in a journal's sense. | High | Zenodo deposit per data release + CITATION.cff in atlas/standards/VisualDCS + register ORCID; cite DOIs in every paper. |
| G2 | **Standards exports are deferred, not delivered**: TEI Lex-0 / OntoLex-Lemon moved to csl-standards but no actual export exists; no ELEXIS linkage. Lexicography reviewers will ask "where is the TEI?" | High | One pilot: MW + one indigenous dict (SKD) → TEI Lex-0, validated against the Lex-0 schema; OntoLex later. |
| G3 | **In-house evidence vocabulary is unmapped**: `observed/derived/inferred/reviewed` is excellent but private. | Medium | Publish a one-page crosswalk to W3C PROV-O / TEI `@cert`/`@resp`; costs a day, makes the labels citable. |
| G4 | **Single-reviewer bottleneck = methodological weakness, not just a queue**: 10 R2 checkpoint rows, 105 H4 rows, 50 xref rows blocked on one person. With n=1 there is no inter-annotator agreement, so reviewed claims have unmeasurable reliability. | High | The community-review decision fixes this *if* every packet is double-keyed and κ is reported (OBS-T already demonstrated Fleiss κ=0.42 tooling). |
| G5 | **Regex-based structure detection has no gold standard**: MW block detection limits are documented (PAPER.md §9, DOUBTS.md) but never benchmarked against a hand-annotated sample. | Medium | 200-entry stratified gold sample, hand-annotated by 2 reviewers, report precision/recall per block type. One-time cost; armours every paper. |
| G6 | **Licensing is repo-level, not dataset-level**; derived JSON inherits unclear rights from mixed-licence sources. | Medium | Per-dataset licence field in the envelope (most can be CC BY 4.0; flag exceptions). |
| G7 | **No user-facing evaluation**: the atlas claims to serve readers but no usage study, no analytics, no student testing exists. Pedagogical-lexicography venues (Lexikos) will ask. | Medium | Fold into the learner's-layer track: small task-based study with the same students doing review-pool work. |
| G8 | **Bus factor 1** on the atlas itself (and 65/76 org repos). | Structural | Partially mitigated by reproducible builds + this roadmap's community pool; name a co-maintainer for atlas data builds by Q2 2027. |

### Micro- and macro-level coverage audit

**Macrostructure — well covered:** lemma coverage matrix (7 dicts), pairwise Jaccard overlap, unique vocabularies, homonym-split disagreement, headword-vs-subentry promotion trade-off (M1/M2: MW promotes, Petersburg nests).

**Macrostructure — not yet studied (each is a paper-grade hole):**
- **Access structures** (Wiegand's *Zugriffsstrukturen*): alphabetization regimes, ordering of homonyms, treatment of anusvāra/visarga in sort order, running heads — nothing yet, and the dictionaries genuinely differ.
- **Lemmatization policy**: what counts as a lemma (root vs 3sg present vs stem) across the seven — touched by M1/M2 but not theorized.
- **The kośa macrostructure**: AMAR/ARMH/ABCH are thematic, versified, synonymic — an entirely different macrostructural type, currently chapter stubs. The European/indigenous macrostructure contrast is the book's most original axis.

**Microstructure — well covered:** sense segmentation (structural + R2 prose), sense inheritance (H1/H2/H3R: granularity is a family trait; cited senses survive 0.762 vs 0.591; descendants condense, not expand), cross-references/mediostructure (M3/M6 lineage graph), indigenous root apparatus (M4/M7: anubandha key, 85.5% gaṇa agreement), citation registers (`<ls>` vs *iti*), semantic fields (M8/H4 Amarakośa vargas), structural register (H6).

**Microstructure — not yet studied:**
- **Definition typology**: synonym gloss vs equivalent vs encyclopedic description per dictionary — the single most classical microstructural dimension, absent.
- **Usage and register labels** (poetic, Vedic, lexicographers-only `<ls>L.</ls>` is started in MWS PAPER.md but not comparative).
- **Etymology component** comparative treatment (PWG vs MW vs indigenous *vyutpatti*).
- **Megastructure**: front/back matter as data — the SKD anubandha key proved front matter decodes microstructure; do this for all 9.

---

## Part II — The reinvention: evidence-graded lexicography

The thesis that unifies the articles and the book:

> A digital dictionary is not a text but a **layered evidence graph**. Every lexicographic statement — headword, sense, gender, citation, cross-reference — is a node carrying (a) its source dictionary and convention, (b) an explicit evidence grade, (c) corpus attestation where available, and (d) review provenance. Sanskrit, with two parallel lexicographic civilizations (European 1832–1957 and indigenous kośa/Pāṇinian), nineteen centuries of depth, and a 5.6M-token tagged corpus, is the best testbed on earth for this model.

Concretely, the spine already exists in pieces:

```
Whitney roots (938)  ──┐
DCS lemmas + freq    ──┼──►  Lemma spine (SLP1 + homonym key)
28.5k lemma dossier  ──┘          │
                                  ├── sense layer   (R2 alignments, evidence-graded)
                                  ├── grammar layer (M4/M7 gaṇa/pada/transitivity, Whitney classes)
                                  ├── citation layer (27 canonical sigla, 138 aliases; <ls> + iti)
                                  └── review layer  (community adjudication, κ-measured)
```

What is genuinely new versus existing DH lexicography (ELEXIS, Lexonomy, TEI Lex-0 projects): they standardize *encoding*; this programme standardizes *epistemics* — graded, reviewable, corpus-anchored evidence per statement, with the indigenous tradition as first-class data rather than exotic noise. The learner's reading layer is then just one *view* over the graph: filter by DCS frequency band, rank dictionary senses by survival evidence, surface the form's paradigm cell.

### Methodological lineage: systematic lexicography (Apresyan) and its ACL counterpart

_Added 14-07-2026 (H942). Gives the "system, not a list" thesis above its intellectual genealogy and seeds the monograph's evidence-graded-method framing chapter._

The evidence-graded thesis has a lineage. The claim that **a dictionary is a system, not a list of isolated entries** was first made rigorous by Ju. D. Apresyan's *systematic lexicography* (системная лексикография) and the Moscow Semantic School's *integral description of language* (интегральное описание языка); the ACL / computational-linguistics tradition arrived at the same claim from corpus evidence. This programme sits at their intersection — Apresyan supplies the schema (typed, grammar-coordinated, decompositional description), ACL supplies the corpus-and-model instrument to populate and falsify it, and the two-civilization Sanskrit testbed is where both get exercised per claim.

**Why Apresyan is the pivot.** Before him, lexicography was entry-craft: each article internally coherent, mutually inconsistent. He turned it into a reproducible formal model of the whole lexicon, coordinated with the grammar and engineered to run inside a machine (the ETAP MT system). The specific innovations:

1. **Systematic lexicography / lexicographic types** (*лексикографические типы*) — words fall into classes sharing morphological, syntactic, semantic and combinatorial behaviour, and every member of a type is described on the same grid. The dictionary describes a system, not a heap of entries.
2. **Integral description** (*интегральное описание*) — grammar and dictionary are two mutually tuned components of one model: the dictionary states exactly what the rules consume, and no rule presupposes data the dictionary omits.
3. **Portrait ↔ type dialectic** — each lexeme gets an exhaustive individual *portrait* (*лексикографический портрет*), but the *type* fixes the axes so portraits stay comparable. Every word is at once an individual and a class member — the disciplined form of the lumping/splitting problem.
4. **Reductive semantic metalanguage** — толкования built from a restricted set of primitives under strict rules (substitutability, no vicious circles, ordered components); meaning becomes decomposable and falsifiable rather than paraphrase-in-kind.
5. **Lexical functions + the Explanatory Combinatorial Dictionary** (with Mel'čuk) — collocations formalised as ~60 universal functions (Magn, Oper, Func, Real…); the *active* (production-oriented) dictionary that tells a speaker how to *say* a meaning.
6. **Pragmatics, connotation, communicative structure inside the entry** — categories earlier left to intuition, given systematic slots.
7. **New Explanatory Dictionary of Synonyms of Russian** (Новый объяснительный словарь синонимов) — the flagship demonstration: synonym sets described on a fixed multi-dimensional grid, so synonymy becomes a matrix of explicit differential features rather than vague near-equivalence.

**The ACL counterpart — same insight, opposite epistemology.** Where Apresyan is top-down, rationalist and introspective, the ACL tradition is bottom-up, empirical and distributional; both conclude that the lexicon is systematic. His concepts map onto standard computational resources:

| Apresyan concept | ACL Anthology counterpart |
|---|---|
| лексикографический тип | Levin verb classes → **VerbNet**, classes defined by syntactic alternations and corpus-checkable ([L06-1280](https://aclanthology.org/L06-1280/)) |
| интегральное описание / government (модель управления) | **FrameNet** ([P98-1013](https://aclanthology.org/P98-1013/)), **PropBank** ([J05-1004](https://aclanthology.org/J05-1004/)) — argument structure as the grammar↔lexicon join |
| relational lexicon / sense inventory | **WordNet** ([H94-1111](https://aclanthology.org/H94-1111/)) |
| лексикографический портрет | corpus **Word Sketches** (Sketch Engine; EURALEX 2004, not in the Anthology) — an automatically computed portrait of a word's grammar and collocation |
| portrait ↔ type / discreteness of senses | Kilgarriff, *"I don't believe in word senses"* (CHum 1997; [arXiv cmp-lg/9712006](https://arxiv.org/abs/cmp-lg/9712006)), and the **WSD** evaluation frame ([E17-1010](https://aclanthology.org/E17-1010/)) |
| лексические функции | collocation classification into an LF typology ([P19-1576](https://aclanthology.org/P19-1576/)) |
| толкование / reductive metalanguage | **definition modelling** ([P18-2043](https://aclanthology.org/P18-2043/)); LLM-generated definitions as semantic representations ([2024.findings-acl.339](https://aclanthology.org/2024.findings-acl.339/)) |

The payload is the tension and its resolution. Apresyan's method was always vulnerable at one joint — the reproducibility of introspective judgment. Corpus methods (Word Sketches, distributional and contextual embeddings) and now LLM definition generation turn that from a matter of authority into a matter of auditable evidence: the rationalist grid supplies the axes, the empirical model fills and checks them at scale.

**Reading list — verified ACL Anthology anchors.**

- **WordNet** — G. A. Miller, "WordNet: A Lexical Database for English," HLT 1994 — [H94-1111](https://aclanthology.org/H94-1111/). The relational lexicon.
- **FrameNet** — C. Baker, C. Fillmore, J. Lowe, "The Berkeley FrameNet Project," COLING-ACL 1998 — [P98-1013](https://aclanthology.org/P98-1013/). Frame semantics as background/integral description.
- **PropBank** — M. Palmer, D. Gildea, P. Kingsbury, "The Proposition Bank: An Annotated Corpus of Semantic Roles," *Computational Linguistics* 31(1), 2005 — [J05-1004](https://aclanthology.org/J05-1004/). Predicate-argument structure = government patterns.
- **VerbNet** — K. Kipper, A. Korhonen, N. Ryant, M. Palmer, "Extending VerbNet with Novel Verb Classes," LREC 2006 — [L06-1280](https://aclanthology.org/L06-1280/). Levin classes as operationalised lexicographic types.
- **Kilgarriff** — A. Kilgarriff, "I don't believe in word senses," *Computers and the Humanities* 31(2), 1997 — [arXiv cmp-lg/9712006](https://arxiv.org/abs/cmp-lg/9712006). The empirical challenge to the fixed portrait (hosted at CHum/arXiv, not the Anthology).
- **WSD evaluation** — A. Raganato, J. Camacho-Collados, R. Navigli, "Word Sense Disambiguation: A Unified Evaluation Framework and Empirical Comparison," EACL 2017 — [E17-1010](https://aclanthology.org/E17-1010/). What sense discreteness costs, measured.
- **Lexical functions** — L. Espinosa Anke, S. Schockaert, L. Wanner, "Collocation Classification with Unsupervised Relation Vectors," ACL 2019 — [P19-1576](https://aclanthology.org/P19-1576/). Automatic classification into a Mel'čuk/Apresyan LF typology.
- **Definition modelling** — A. Gadetsky, I. Yakubovskiy, D. Vetrov, "Conditional Generators of Words Definitions," ACL 2018 — [P18-2043](https://aclanthology.org/P18-2043/). The толкование as a generatable object.
- **LLM definitions** — "Definition generation for lexical semantic change detection," Findings of ACL 2024 — [2024.findings-acl.339](https://aclanthology.org/2024.findings-acl.339/). Generated definitions as auditable semantic representations.

**How this feeds the programme.**

- **Monograph framing chapter.** The planned history/method chapter gets its spine here: rationalist systematic lexicography → empirical computational lexicography → the evidence-graded synthesis of Part II.
- **Lexicographic types → the Part I microstructure holes.** "Definition typology" and "lemmatization policy" (flagged unstudied above) are type-level questions: describe *all* causatives, deverbal nouns and root-derivatives on one grid rather than per-entry.
- **Lexicographic portrait → P1.** A corpus Word Sketch over DCS is the automatic portrait that can seed and audit the P1 MW-microanalysis gold sample.
- **Integral description = the existing spine.** The Whitney-roots + DCS + sense/grammar/citation/review layers diagrammed above *are* интегральное описание in miniature; naming them as such is free framing capital.
- **Lexical functions** are a candidate collocation export layer once R2 sense alignment stabilises.
- **@DECIDE seed.** Whether to adopt an explicit, controlled register of **Sanskrit lexicographic types** as a first-class layer of the evidence graph (parallel to the evidence-label vocabulary), or to leave typing implicit in the per-dictionary microstructure. A human should decide before P4 (indigenous microstructure) locks its schema.

---

## Part III — The paper pipeline (feeds the book chapter-for-chapter)

| # | Working title | Core data (exists today) | Venue | Submit |
|---|---|---|---|---|
| P1 | *The block economy of Monier-Williams: a data-grounded microanalysis of 286,561 entries* | MWS papers/microanalysis (consolidated draft done) + G5 gold-sample validation | **IJL** | **Q3 2026** |
| P2 | *Sense inheritance in the Sanskrit dictionary family: condensation, survival, and the citation advantage* | R2 H1/H2/H3R (r≈0 granularity trend; 0.762 vs 0.591 survival; drift indices) | **Lexicographica** | Q4 2026 |
| P3 | *Two citation registers: European source apparatus and indigenous* iti *quotation in nine Sanskrit dictionaries* | CITATION_REGISTERS, citation-apparatus.json, siglum alias table | **Dictionaries** | Q1 2027 |
| P4 | *When zero means nothing: recovering the indigenous microstructure of Śabdakalpadruma and Vācaspatya* | M4/M7, anubandha key, zero-meaning methodology, H6 register | **IJL** or WSC 2027 | Q1–Q2 2027 |
| P5 | *Fifty thousand corrections: an error typology of twelve years of collaborative dictionary maintenance* | OBS-T (50,953 corrections, two-axis typology, κ=0.42) | **Lexikos** | Q2 2027 |
| P6 | *A frequency-graded reading layer for Sanskrit learners: joining corpus, grammar, and seven dictionaries* | DCS bands + lemma dossier + Whitney + user study (G7) | **Lexikos** (pedagogical) or eLex 2027 | Q2 2027 |

**Book** (proposal to de Gruyter *Lexicographica Series Maior* or Brill, ~Q1 2027 after P1–P2 are under review):
*Sanskrit Lexicography in the Digital Age: Evidence, Inheritance, and Two Traditions* — Ch.1 history & the two civilizations (new); Ch.2 method: evidence-graded lexicography (new, from Part II); Ch.3 ← P1; Ch.4 ← P2; Ch.5 ← P3; Ch.6 ← P4; Ch.7 macrostructure & the kośa type (new, from the gap list); Ch.8 ← P5; Ch.9 ← P6 + the learner's layer; Ch.10 FAIR infrastructure & the four-repo architecture (from observatory + standards).

---

## Part IV — 12-month roadmap (Q3 2026 → Q2 2027)

### Q3 2026 (Jul–Sep) — *Unblock, harden, submit P1*
1. **FAIR sprint (G1, G3, G6)**: Zenodo DOI for atlas data release v1; CITATION.cff in csl-atlas, csl-standards, VisualDCS, csl-observatory; ORCID registered and added to papers; PROV-O crosswalk page for evidence labels; per-dataset licence fields.
2. **Gold-standard sprint (G5)**: 200-entry MW gold sample, double-annotated; precision/recall per block type; appendix to P1.
3. **Community review pool v1**: convert the three blocked packets (R2 ×10, H4 ×105, xref ×50) into a student-facing review UI (atlas already renders packets; add submission + double-keying + κ report). Recruit 5–10 students (samskrtam.ru network, Sanskrit students' lists). *The review tasks are the pedagogy*: each packet teaches dictionary reading.
4. **Submit P1 to IJL** (gold-sample results folded in).
5. Clear H5 maker proposal (divaraTa → diviraTa) to Cologne makers.

### Q4 2026 (Oct–Dec) — *Sense inheritance + learner's layer v1*
1. **P2 written and submitted** (R2 data is restored and reproducible; checkpoint rows now adjudicated by the pool).
2. **Learner's reading layer v1** in csl-atlas: DCS frequency bands (VisualDCS adapter contract: `dcs_lemma_summary.json`) joined to lemma-lookup + dossier; per-lemma card = frequency band, best-attested senses (survival-ranked from P2 data), Whitney root + gaṇa, paradigm-browser link. Ship as a public page. *Audience personas (adopted 02-07-2026 from the DharmaMitra workshop intake form — [analysis](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/Pre-Workshop_Questionnaire_ANALYSIS.md)): professional/published translator · academic/researcher · student · practitioner translating for practice · hobbyist/independent learner — the practitioner and hobbyist segments are first-class users of this layer, not an afterthought; actual segment sizes pending DharmaMitra's aggregated form results (MG asks at the workshop, GTD @DO).*
3. **TEI Lex-0 pilot (G2)** in csl-standards: MW sample + SKD sample exported and schema-validated; documents what the indigenous apparatus needs that Lex-0 lacks (itself publishable as a note).
4. **Book proposal drafted** (synopsis + P1/P2 as sample chapters).

### Q1 2027 (Jan–Mar) — *The indigenous turn*
1. **Megastructure study**: front/back matter of all 9 narrative dicts catalogued as data (extends the anubandha-key method); feeds P3 and P4.
2. **P3 submitted** (citation registers).
3. **P4 drafted** (indigenous microstructure); decide IJL vs WSC 2027 by deadline calendar.
4. **Kośa chapters**: ARMH/ABCH stubs → real chapters; first macrostructural model of versified synonymic dictionaries in the atlas (Ch.7 material; nothing comparable exists in English).
5. **Book proposal submitted** to de Gruyter/Brill.
6. Review pool round 2: definition-typology annotation (the missing classical dimension) — 300 entries × 7 dicts, double-keyed.

### Q2 2027 (Apr–Jun) — *Students, evaluation, book contract*
1. **Learner's layer v2 + user study (G7)**: task-based evaluation with the review-pool students (find-the-right-sense tasks, timed, vs plain Cologne lookup); results feed P6.
2. **P5 submitted** (error typology — the OBS-T dataset is unique in the field; no dictionary project has 12 years of correction telemetry).
3. **P6 submitted** (learner's layer + study).
4. **Book writing begins** against the contract; new chapters 1, 2, 7, 10 drafted (everything else is revision of P1–P6).
5. Co-maintainer named for atlas data builds (G8).

### Standing rules across all quarters
- Every paper cites dataset DOIs, reports κ for every reviewed claim, and links the exact build commit.
- Every analysis lands with its review packet *and* the packet goes to the pool the same week — no new single-reviewer debt.
- The atlas stays dictionary-evidence-only; exports live in csl-standards, corpus in VisualDCS, telemetry in csl-observatory (boundary rules unchanged).

---

## Part V — Risks

| Risk | Mitigation |
|---|---|
| Student pool doesn't materialize | Packets are sized so the author alone can clear the *blocking* minimum (R2 ×10 first); pool scales quality, not viability. |
| IJL rejects P1 on "single dictionary" scope | Lexicographica and Dictionaries are natural second homes; the gold-sample appendix addresses the likely methodological objection in advance. |
| DCS adapter contract slips | Learner's layer v1 can ship with the 2026-03-05 release snapshot frequencies; live contract is an upgrade, not a dependency. |
| Book proposal needs 2 published chapters | P1 submission Q3 2026 + P2 Q4 2026 makes "under review" true at proposal time; Q1 2027 submission is realistic. |
| Burnout / bus factor 1 | The roadmap front-loads infrastructure (FAIR, pool, gold standard) precisely so Q1–Q2 2027 is mostly *writing*, not building. |

_Dr. Mārcis Gasūns_
