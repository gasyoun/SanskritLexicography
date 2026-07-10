# LEXICOGRAPHY_MANUALS.meta — metadoc for the 37-work manuals library

_Created: 10-07-2026 · Last updated: 10-07-2026_

Directory-level metadoc (per the org metadoc convention) for
[literature/md/Lexicography-Manuals/](https://github.com/gasyoun/SanskritLexicography/tree/master/literature/md/Lexicography-Manuals)
— the 37-file library of lexicography, corpus-linguistics, and historical-linguistics
manuals, handbooks, and papers in Markdown conversions.

## Purpose

Reference library assembled to ground the M01 Brill/De Gruyter monograph (*Digital
Sanskrit Lexicography: The Dictionary as a Layered Evidence Graph*,
[BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md))
in the professional metalexicography, corpus-methods, and comparative
lexicographical-historiography literature — and, beyond M01, to serve the
SanskritLexicography paper pipeline (A30/A31/A32 = roadmap P4–P6) and the wider project's
methods needs. The full M01 crosswalk (grounding map, gap analysis, positioning,
new-chapter candidates, quality-bar audit) lives in
[LITERATURE_CROSSWALK.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md)
— this metadoc holds only the library-level record and per-work tags.

## Provenance

- **Assembled by:** MG (file selection/conversion); committed **07-07-2026** in
  [`1a4520b`](https://github.com/gasyoun/SanskritLexicography/commit/1a4520b) — bundled
  inside the pwg_ru H215 Slice-4 PR
  [#219](https://github.com/gasyoun/SanskritLexicography/pull/219) ("oral register"),
  i.e. swept into an unrelated feature commit rather than landed as its own change; on
  `master` since that merge. The H505 handoff's note that the library lived only on a
  side branch was stale — the branch (`codex/pwg-selftest-hermetic`) is local-only and
  the library is fully tracked on `master`.
- **Format:** Markdown conversions of scanned/borrowed book PDFs and OA papers; sizes
  3 KB–2.8 MB; quality varies (see defects below).
- **First audit:** 10-07-2026, Fable 5 (`claude-fable-5`), handoff
  [H505](https://github.com/gasyoun/Uprava/blob/main/handoffs/H505-Fable_SanskritLexicography_m01_literature_crosswalk_gap_audit_10.07.26.md)
  — 9 parallel read passes (close-reads of the 12 load-bearing works, skims of the rest).

## The 37 works — one-line relevance tags

Sorted by role for M01; identities established by the 10-07-2026 audit (several files
carry no metadata — the identifications below are from internal evidence).

### Core metalexicography (close-read)

| File | Identity | Tag |
|---|---|---|
| [Dictionary of lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Dictionary%20of%20lexicography.md) | Hartmann & James 1998 (Routledge) | Canonical terminology of the field; macro/micro/medio/megastructure canon; names the open mediostructure gap M01 Ch. 10 fills |
| [Lexicography _ An Introduction.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Lexicography%20_%20An%20Introduction.md) | Jackson 2002 (Routledge) | English-centric textbook; data-sources triad, Thorndike inventory balancing, the field-standard dictionary-criticism method |
| [Systematic Lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Systematic%20Lexicography.md) | Apresjan 2000 (OUP, tr. Windle) | Lexicographic types + portraits; establishes "genetic" sense ordering with its mechanism — mandatory for M01 Ch. 7 |
| [The Bloomsbury Companion to Lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Bloomsbury%20Companion%20to%20Lexicography.md) | Jackson (ed.) 2013 | The field's research map: Kilgarriff on corpora, Lew on sense individuation, Piotrowski on theory-status, user research |
| [internet lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/internet%20lexicography.md) | Klosa-Kückelhaus (ed.) 2024, **De Gruyter LSM 164**, OA | Same-series benchmark; graphs/RDF/versioning/crowdsourcing already standard — the direct stress test of M01's novelty claim |
| [The Gentle Art of Lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Gentle%20Art%20of%20Lexicography.md) | Partridge 1963 (Deutsch) | Practitioner craft-memoir; alphabetical-order pathology (*set*), register scale, cognate-grouping fork |

### Comparative lexicographical traditions (close-read)

| File | Identity | Tag |
|---|---|---|
| [The Arabic Lexicographical Tradition.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Arabic%20Lexicographical%20Tradition.md) | Baalbaki 2014 (Brill HdO 107) | Strongest non-Sanskrit comparandum: *mubawwab/muǧannas* macrostructure typology, *šawāhid* witness doctrine, millennium of documented borrowing — can carry M01's comparative part-bridge alone |
| [The latin of roman lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20latin%20of%20roman%20lexicography.md) | Ferri (ed.) 2011 (Fabrizio Serra) | Proceedings, cite essay-by-essay: Maltby (Servius registers), Lhommé (Verrius→Festus→Paul epitome descent), Gatti (Nonius citation canon) |
| [Ancient Greek Scholarship.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Ancient%20Greek%20Scholarship.md) | Dickey 2007 (OUP/APA) | Greek glossography/scholia guide; VMK source-precedence hierarchy = pre-digital layered evidence graph; Atticist register-marking |
| [A history of Indian literature_ Vol_ 5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/A%20history%20of%20Indian%20literature_%20Vol_%205.md) | **Vogel, *Indian Lexicography* 1979** (HIL V.4, Harrassowitz) | THE survey of the indigenous kośa tradition — primary secondary source for M01 Ch. 4; belongs in the proposal's comparables |

### Corpus-linguistics methods (close-read core + skimmed shelf)

| File | Identity | Tag |
|---|---|---|
| [The fundamental principles of corpus linguistics.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20fundamental%20principles%20of%20corpus%20linguistics.md) | McEnery & Brezina 2022 (CUP) | Epistemology of corpus evidence: negative evidence / induction, effect sizes + CIs, replication — the source for M01's corpus-absence reframe |
| [The Routledge Handbook of Corpus Linguistics.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Corpus%20Linguistics.md) | O'Keeffe & McCarthy (eds.) 2010 | Walter Ch. 31 = corpus-driven dictionary-making (COBUILD); normalization/log-likelihood/representativeness toolkit |
| [Handbook of Corpus Linguistics.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Handbook%20of%20Corpus%20Linguistics.md) | Ryan (ed.) 2019 (Bibliotex) | ⚠️ Low-authority reprint anthology of unrelated CC papers — never cite as authority; trace originals instead |
| [Corpus Linguistics and Statistics with R.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Corpus%20Linguistics%20and%20Statistics%20with%20R.md) | Desagulier 2017 (Springer) | R statistical practice: dispersion, association measures — methods citation for quantitative chapters |
| [Doing Linguistics with a Corpus.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Doing%20Linguistics%20with%20a%20Corpus.md) | Egbert, Larsson & Biber 2020 (CUP Element) | Research-design checklist; "minimally sufficient statistics" principle |
| [Corpus Linguistics for Vocabulary.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Corpus%20Linguistics%20for%20Vocabulary.md) | Szudarski 2018 (Routledge) | Type/token/lemma/word-family counting standards + frequency-based inclusion → M01 Ch. 3 |
| [Programming for Corpus Linguistics with Python.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Programming%20for%20Corpus%20Linguistics%20with%20Python.md) | Keller 2024 (CUP Element) | Pandas/spaCy pipeline cookbook; implementation-standards reference only |
| [StrategiesDoing Corpus Linguistics.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/StrategiesDoing%20Corpus%20Linguistics.md) | Csomay & Crawford 2024, 2nd ed. (Routledge) | Undergraduate register-analysis textbook; marginal to M01 |
| [Corpus Linguistics for Education.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Corpus%20Linguistics%20for%20Education.md) | Pérez-Paredes 2021 (Routledge) | Education-domain 18-skills guide; marginal to M01 |

### Sanskrit / philology / NLP (skim-plus)

| File | Identity | Tag |
|---|---|---|
| [Lowe Participles in Rigvedic Sanskrit.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Lowe%20Participles%20in%20Rigvedic%20Sanskrit.md) | Lowe 2015 (OUP) | LFG analysis of Vedic participles; the root/participle lemmatization boundary → M01 Ch. 8/9, A39 |
| [The encoding of ad hoc categories in Sanskrit.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20encoding%20of%20ad%20hoc%20categories%20in%20Sanskrit.md) | Inglese & Geupel 2018 (*Folia Ling. Hist.*) | *ādi*-compounds as ad hoc category markers; headword-vs-construction boundary case |
| [Performance_of_a_Lexical_and_POS_Tagger.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Performance_of_a_Lexical_and_POS_Tagger.md) | Hellwig 2010 (ISCLS-4) | First Sanskrit tagger benchmark; measures MW lemma-redundancy costs — headword inclusion as a gradable claim |
| [Evaluating_Syntactic_Annotation_of_Ancie.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Evaluating_Syntactic_Annotation_of_Ancie.md) | Biagetti, Hellwig et al. 2021 (Vedic Treebank) | IAA methodology for ancient-language annotation — grounds M01's `reviewed` evidence grade |
| [Adapting_Standard_NLP_Tools_and_Resource.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Adapting_Standard_NLP_Tools_and_Resource.md) | Reiter, Hellwig et al. 2010 (LaTeCH) | NLP domain-adaptation to ritual texts; supporting citation for Ch. 2/3 |
| [Primary Education in Sanskrit.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Primary%20Education%20in%20Sanskrit.md) | Gerow 2002 (JAOS 122.4) | Traditional Sanskrit pedagogy/transmission; framing footnote for the indigenous chapters |
| [Patterns_of_Exchange.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Patterns_of_Exchange.md) | Hellwig 2010 (Heidelberg C10 report, German) | Quantitative model of travel-narrative corpora; no M01 use — author-context only |
| [Hints to the Study of Sanskrit Compounds.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Hints%20to%20the%20Study%20of%20Sanskrit%20Compounds.md) | 1896 samāsa primer (Bombay) | ⚠️ **Empty scan — Google boilerplate only, no OCR'd body**; re-OCR or drop |

### General linguistics handbooks (skimmed)

| File | Identity | Tag |
|---|---|---|
| [#x98;The#x9C; Routledge handbook of semantics.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/%23x98%3BThe%23x9C%3B%20Routledge%20handbook%20of%20semantics.md) | Riemer (ed.) 2016 | Sense individuation, decomposition, semantic shift → M01 Ch. 6/7 theory backbone (⚠️ mangled filename — rename candidate) |
| [THE ROUTLEDGE HANDBOOK OF HISTORICAL LINGUISTICS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/THE%20ROUTLEDGE%20HANDBOOK%20OF%20HISTORICAL%20LINGUISTICS.md) | Bowern & Evans (eds.) 2015 | Comparative method, trees/waves, phylogenies → M01 Ch. 10/13 stemmatics vocabulary |
| [The Routledge Handbook of Linguistics.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Linguistics.md) | Allan (ed.) 2016 | Survey-level; Peters's lexicography chapter as orientation only |
| [The Routledge Handbook of Syntax.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Syntax.md) | Carnie, Sato & Siddiqi (eds.) 2014 | Marginal to M01; syntax–lexicon interface background at most |

### Applied linguistics / teaching (skimmed — mostly beyond-M01)

| File | Identity | Tag |
|---|---|---|
| [The routledge handbook of applied linguistics.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20routledge%20handbook%20of%20applied%20linguistics.md) | Li Wei, Zhu Hua & Simpson (eds.) 2024, 2nd ed., Vol. 1 (PDF) | Fontenelle's lexicography chapter + COBUILD material; ⚠️ same book as the EPUB twin below — cite one edition |
| [The Routledge Handbook of Applied Linguistics; Second.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Applied%20Linguistics%3B%20Second.md) | Same work, EPUB edition | ⚠️ **Duplicate** of the PDF above — dedup candidate |
| [The Routledge Handbook of Second Language Acquisition.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Second%20Language%20Acquisition.md) | Wong & Barcroft (eds.) 2024 (SLA *and Input Processing*) | No M01 use; Hulstijn dictionary-use-in-reading strand for pedagogy work |
| [Corpus Linguistics and Second Language Acquisition.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Corpus%20Linguistics%20and%20Second%20Language%20Acquisition.md) | Lu 2023 (Routledge) | Learner-corpus methods; feeds a future Sanskrit learner-corpus effort, not M01 |
| [The Routledge Handbook of Teaching English to Young Learners.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Teaching%20English%20to%20Young%20Learners.md) | Garton & Copland (eds.) 2019 | Marginal; young-learner pedagogy backdrop only |
| [How to Use Corpora in Language Teaching.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/How%20to%20Use%20Corpora%20in%20Language%20Teaching.md) | Sinclair (ed.) 2004 (Benjamins SCL 12) | Corpus-driven learner dictionaries + DDL; the most lexicography-adjacent teaching title |

## Known defects / hygiene backlog

1. **Empty scan:** `Hints to the Study of Sanskrit Compounds.md` has no body text —
   re-OCR from the source scan or remove.
2. **Duplicate:** the two Applied Linguistics handbook files are the same 2024 edition in
   PDF and EPUB conversion — keep one (the PDF conversion is the more complete), or mark
   the EPUB as the citation copy.
3. **Mangled filename:** `#x98;The#x9C; Routledge handbook of semantics.md` carries
   unescaped entity fragments — rename to `The Routledge handbook of semantics.md`
   (breaks no inbound links; this metadoc and the crosswalk would need the one-line
   update).
4. **Low-authority volume:** Ryan 2019 "Handbook of Corpus Linguistics" is a repackaged
   reprint anthology — flagged so it is never cited as a standards source.
5. **No front-matter metadata** in most conversions — identities above are from internal
   evidence; spot-verify before citing page numbers in print.

## What this library is good for beyond M01 (ranked backlog)

1. **A30 (P4, ŚKD/VCP indigenous microstructure, 2/5):** Vogel (tradition survey) +
   Apresjan (portraits/integrated description) + Baalbaki (root-and-pattern comparandum)
   give A30 its entire theoretical frame — the highest-leverage reuse in the library.
2. **A31 (P5, error typology, 2/5):** *Internet Lexicography* Ch. 3/8 (error handling,
   user participation) + Bloomsbury (Akasu, criticism methodology; Brewer, OED revision
   layers) — the related-work section is essentially pre-assembled here.
3. **A32 (P6, frequency-graded reading layer, 1/5):** Szudarski (vocabulary/frequency
   methodology) + Sinclair 2004 (DDL, corpus-informed learner reference) + the SLA shelf
   (Lu; Wong & Barcroft) — the pedagogy-side citations A32's user study will need.
4. **pwg_ru / kosha evidence grading:** Baalbaki's *šawāhid* / *ʿuṣūr al-iḥtiǧāǧ*
   witness-authority doctrine is a ready vocabulary for attestation-authority tiers in
   the translation pipeline's grade system.
5. **A39 (verbal roots, grammar–corpus–dictionary):** Lowe (participle/root boundary) +
   Hellwig tagger (lemmatization costs).
6. **Methods sections anywhere:** Desagulier / Egbert-Larsson-Biber / McEnery & Brezina as
   the standing statistical-practice citations for the quantitative A-series.
7. **Systema-Sanscriticum teaching platform:** the applied/teaching shelf (DDL, learner
   corpora, young-learner pedagogy) if a corpus-informed Sanskrit teaching layer is built.

## Related documents

- [LITERATURE_CROSSWALK.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md) — the full M01 crosswalk this metadoc indexes for
- [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md) · [BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md)
- [ROADMAP_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_2026_2027.md) — P4–P6 paper pipeline the backlog above feeds

## Revision history

| Date | Change | Session |
|---|---|---|
| 10-07-2026 | Metadoc created: provenance, 37 per-work tags, defects, beyond-M01 backlog | H505, Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
