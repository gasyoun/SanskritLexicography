# M01 literature crosswalk — the 37-manual library against the book plan

_Created: 10-07-2026 · Last updated: 10-07-2026_

The book-scoped deliverable of handoff
[H505](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H505-Fable_SanskritLexicography_m01_literature_crosswalk_gap_audit_10.07.26.md):
the 37-work lexicography / corpus-linguistics / historical-linguistics library at
[literature/md/Lexicography-Manuals/](https://github.com/gasyoun/SanskritLexicography/tree/master/literature/md/Lexicography-Manuals)
read against
[BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md),
[BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md),
and the two written chapters
([ch02](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md),
[ch05](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch05_mw_block_economy.md)).
Five lenses, per MG's brief: grounding map · gap analysis · competing-works positioning ·
new-chapter candidates · quality-bar/abandonment audit. Per-work bibliographic identities and
one-line tags live in the library's own metadoc,
[LEXICOGRAPHY_MANUALS.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/LEXICOGRAPHY_MANUALS.meta.md)
— this memo does not duplicate them.

**Provenance.** Produced 10-07-2026 by Fable 5 (`claude-fable-5`) under H505: 9 parallel
read passes over the 37 files (close-reads of the 12 load-bearing works, skims of the
rest), plus a full read of the book's own four documents. Analysis/recommendation only —
no chapter prose, plan architecture, or proposal text was edited in this pass.

---

## 0. Executive summary

1. **No chapter needs to be cut.** All 15 survive the quality-bar audit — but four need
   mandatory repositioning (Ch. 2, 3, 7, 14) and one (Ch. 7) is a genuine merge candidate
   parked as `@DECIDE` (§5).
2. **The novelty claim survives, but narrowly, and must be restated.** *Internet
   Lexicography* (LSM 164 — the very series M01 targets) already treats dictionaries as
   graph databases, RDF statement-sets, Git-style versioning, and crowdsourced correction.
   M01's contribution is real but sits one layer up: the **typed evidence-grade +
   review-provenance ontology per statement**, not "dictionary as graph" (§3).
3. **The single biggest referee liability is corpus-absence inference.** "Headwords the
   corpus never attests" (Ch. 3) and "68.3 % of épigraphique headwords corpus-absent"
   (Ch. 14) instantiate what McEnery & Brezina call "the problem of induction writ large,"
   on a 5.6 M-token corpus one to two orders of magnitude below the field's sense-capture
   size floor. Reframe as bounded DCS-coverage observations (§2.1, §5).
4. **One genuinely new structural element is warranted:** a comparative part-bridge
   *"Sanskrit among the lexicographical civilizations"* carried by Baalbaki (Arabic), with
   Ferri (Latin) and Dickey (Greek) as section-level comparanda (§4.1) — plus a decision on
   a standalone corpus-methods chapter (§4.2).
5. **Two factual corrections to existing book documents** are pending (Klosa-Kückelhaus is
   the *sole* editor of LSM 164; Vogel 1979 must join the comparables) — listed in §6, not
   silently applied.

---

## 1. Theoretical grounding map

Which works, and which specific concepts inside them, each part of M01 must cite or
engage. **Bold** = engagement is mandatory at the de Gruyter LSM bar; plain = strengthens.
Short titles resolve in the
[metadoc](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/LEXICOGRAPHY_MANUALS.meta.md).

| M01 chapter | Works → concepts to engage |
|---|---|
| **Introduction** | **Hartmann & James** → lexicography as "reference science", dictionary-research vs dictionary-making strands; **Bloomsbury Companion (Piotrowski)** → "A Theory of Lexicography – Is There One?" — the frame for M01's claim to supply one; **Bloomsbury (Bogaards)** → historiography of the research field; Zgusta 1980 *Theory and Method* (via Hartmann & James bibliography) → the founding Western/non-Western comparison; Jackson *Introduction* → record-vs-reference dual function |
| **Ch. 1 — Latin discretion-screen** | **Ferri (Maltby essay)** → Servius' *grandiloquus/medius/humilis* register system and *lucerna propter uilitatem* decorum-avoidance — the Greco-Roman genealogy of lexicographic decorum; Baalbaki → *laḥn al-ʿāmma* correctness-policing as the contrast case (purity, not prudery); note: **neither the Arabic nor the Latin volume has a sexual-taboo screen — Ch. 1's phenomenon is Europe-specific, which strengthens its originality claim** |
| **Ch. 2 — measurement framework** | ***Internet Lexicography* (Herold/Meyer/Wiegand Ch. 4)** → graph databases, RDF "statements about two resources", TEI/LMF — the existing modelling layer M01's epistemics sits on top of; **Hartmann & James** → the macro/micro/medio/megastructure canon (Hausmann & Wiegand 1989) + the coarse "evidence"/"authentication" entries M01's four grades refine; **Apresjan** → unification (lexicographic types) vs individuation (portraits) — the systematic-description layer the evidence graph annotates; **McEnery & Brezina** → falsification, effect sizes + CIs ("new statistics"), Kilgarriff 2005 significance-at-scale critique; **Biagetti/Hellwig et al. (Vedic Treebank)** → IAA methodology grounding the `reviewed` grade; Egbert/Larsson/Biber → "minimally sufficient statistics"; Bloomsbury (Piotrowski) → theory-status framing |
| **Ch. 3 — headword inventory + corpus grounding** | **McEnery & Brezina** → negative evidence / problem of induction (the corpus-absence reframe); **Routledge Corpus Handbook (Reppen Ch. 3; Walter Ch. 31)** → representativeness (Biber 1993), the tens-to-hundreds-of-millions size floor for sense capture, low-frequency-vs-absence indistinguishability, genre-skew caveat; **Bloomsbury (Kilgarriff)** → corpus noise/bias in headword-list building ("the corpus is never good enough"); **Hellwig POS-tagger** → measured downstream cost of MW's lemma-inclusion policy — headword inclusion as a gradable, reviewable claim; Jackson → Thorndike's 105-block inventory balancing, data-sources triad; Szudarski → type/token/lemma/word-family counting standards; Inglese & Geupel → *ādi*-compounds as a headword-vs-construction boundary case |
| **Ch. 4 — kośa macrostructure** | **Vogel, *Indian Lexicography* (1979)** → THE survey of the kośa tradition (synonymic vs *nānārtha*; Amarakośa commentaries; Hemacandra corpus) — the chapter's primary secondary source; **Baalbaki** → *mubawwab* (onomasiological) vs *muǧannas* (semasiological) + the three formal orders (phonetic-permutative/alphabetical/rhyme) — proof "alphabetical" is not one thing, and the practitioners' own retrieval-vs-semantic-map trade-off debate; **Hartmann & James** → access structures, monoaccessible/polyaccessible; Jackson Ch. 12 → the European thematic/onomasiological tradition (Hüllen, McArthur); Partridge → the *set* case study: even the alphabet is a designed, imperfect compromise; Dickey → Greek first-letter/first-syllable partial ordering |
| **Ch. 5 — MW block economy** | Already exemplary — ch05 engages Wiegand, Atkins & Rundell, Hausmann with a κ-scored gold benchmark; add: **Apresjan** → the entry as *lexicographic portrait* (name the ancestry); Ferri (Lhommé) → what epitomizers drop (Verrius→Festus→Paul) as the compression comparandum; Bloomsbury (Lew) → sense-division-as-judgment explains the low F09/sense κ cells |
| **Ch. 6 — sense inheritance** | **Bloomsbury (Lew)** → sense individuation: are senses discrete entities or artifacts of dictionary structure (Hanks, Sinclair)? — must be engaged before senses become graph nodes; **Apresjan** → regular polysemy as the mechanism of sense propagation; Routledge Semantics Handbook → sense relations, semantic shift; Walter (Routledge Corpus Ch. 31) → the "salutary" finding that many dictionary senses are corpus-unattested |
| **Ch. 7 — sense ordering** | **Apresjan** → the synchronic-derivational ("genetic") ordering principle *with its mechanism* (literal→figurative via assertive-component removal; the *vyiti* portrait) — **the chapter reads as reinventing a solved problem unless it engages this**; **Bloomsbury (Considine)** → weakly vs strongly historical dictionaries — the field's own vocabulary for M01's axis; Walter → frequency-based ordering as the modern default; Jackson §14.5 + Kipfer 1984 → sense-order indeterminacy as a named open problem; Partridge → intra-entry order as deliberate editorial choice |
| **Ch. 8 — indigenous verbal-root microstructure** | **Vogel** → tradition context; **Apresjan** → integrated grammar–dictionary description (the Moscow-school frame for "the kośa entry presupposes the grammar"); Baalbaki → root-and-pattern (*wazn/jaḏr*) macro-microstructure as the Arabic structural analogue of *dhātu* organization; Lowe → the participle/root lemmatization boundary in Vedic; Gerow → how the indigenous apparatus was actually transmitted (framing footnote) |
| **Ch. 9 — Pāṇinian derivation** | **Baalbaki** → *al-ištiqāq* + lexicography born as grammar's twin (*ʿAyn* ∥ Sībawayhi); Routledge Historical Handbook (Koch; Mailhammer) → morphological reconstruction, etymology methods; Ferri (Pieroni) → **caution**: Latin etymologizing is associative/rhetorical — do *not* equate it with rule-governed *vyutpatti* without the caveat; Partridge → cognate-grouping vs cross-referencing as a universal design fork (Skeat/Weekley debate) |
| **Ch. 10 — cross-reference graphs & descent** | **Hartmann & James** → mediostructure: "a framework for their systematic study … is still to be developed" — **the explicit gap in the field's own reference work that Ch. 10 fills; claim it as the warrant**; Routledge Historical Handbook (Weiss; Hale; François; Dunn) → comparative method, trees/waves, phylogenies — the vocabulary for dictionary stemmatics; *Internet Lexicography* (Engelberg/Müller-Spitzer/Schmidt Ch. 5) → linking + access structures as the field's current frame; Ferri (Lhommé; Maltby) → Verrius→Festus→Paul and Donatus→Servius(+Auctus) as worked descent chains |
| **Ch. 11 — two citation registers** | **Baalbaki** → the *šawāhid* apparatus + *ʿuṣūr al-iḥtiǧāǧ* (epochs of reliable usage) + Bedouin-informant screening — a *doctrinally theorized* witness system that out-formalizes the European `<ls>` register and mirrors *iti*; Ferri (Gatti) → Nonius' ~40-author *auctores* canon with ordered citations (Lindsay's law); Hartmann & James → "source code" as the field's term for citation sigla; Jackson → Murray's OED reader instructions + citation slips |
| **Ch. 12 — citation-frequency graph** | **McEnery & Brezina (Kilgarriff 2005)** → significance is near-meaningless at N = 828 K — effect sizes and dispersion, not p-values; Routledge Corpus (O'Keeffe & Farr Ch. 10) → normalization, log-likelihood not chi-square, reference-corpus design; Ferri (Gatti) → the closed Roman citation canon as a scale-contrast comparandum (flag the asymmetry) |
| **Ch. 13 — shared inheritance as forensic signal** | **Hartmann & James** → **"dictionary archaeology"** — the field's own term for genetic-affiliation forensics: use it, don't coin a rival; Zgusta 1988 *Copying in lexicography* (already in ch02's references — carry into Ch. 13's frame); Jackson/Landau → "all dictionaries are based on preexisting works" — the *fact* of inheritance is a textbook truism; **M01's delta is quantification at corpus scale, and must say so**; Baalbaki → a millennium of documented *and concealed* borrowing (Ibn Manẓūr absorbing the *Nihāya*; "without mentioning him as his source"); Dickey → the Homer-scholia *Viermännerkommentar* with explicit source-precedence ordering — a pre-digital layered evidence graph; Routledge Corpus Ch. 41 → forensic-linguistics fingerprinting methods; Ferri (Furno) → humanist accretion (Calepino→Estienne) |
| **Ch. 14 — Renou's registers** | **McEnery & Brezina** → the corpus-absence caveat applies at full strength to "68.3 % corpus-absent" — reframe as DCS-coverage statement; Ferri (Maltby) → Servius' three-register system as the Roman analogue of register labelling; Dickey → Atticist lexica's normative register-marking; *Internet Lexicography* (Geyken & Lemnitzer Ch. 7) → diasystematic labelling from corpus metadata as current practice; Partridge → the slang/colloquial/catch-phrase/vulgarism scale as the informal precedent Ch. 14 formalizes |
| **Ch. 15 — fifty thousand corrections** | ***Internet Lexicography* (Abel & Meyer Ch. 8)** → user participation: direct/indirect/accessory, user-submitted corrections, quality-voting — Ch. 15 is a *case* of this literature; ***Internet Lexicography* (Klosa-Kückelhaus & Tiberius Ch. 3)** → error handling in the lexicographic process — a near-exact abstract of the OBS-T workflow; *Internet Lexicography* (Herold/Meyer/Wiegand Ch. 1) → versioning, per-entry revision histories (OED Online) — cite, don't reinvent; Bloomsbury (Akasu) → dictionary-criticism methodology as the frame the error typology extends; Bloomsbury (Brewer) → OED revision layers as the versioned-dictionary precedent; Hartmann & James → error analysis explicitly sanctioned as evidence; Partridge → pre-digital collaborative revision |
| **Conclusion** | McEnery & Brezina → what corpus evidence licenses (the honest epistemic close); Bloomsbury (Fuertes-Olivera; Nielsen) → e-lexicography futures the evidence graph answers; Baalbaki Epilogue → the ordering trade-off as a cross-civilizational universal |

---

## 2. Gap analysis — what the field expects that the plan does not yet engage

Ranked by referee risk at de Gruyter LSM.

### 2.1 Corpus-methods epistemics (highest risk)

The plan's corpus-grounding claims (Ch. 3, 14) currently make the singular-to-universal
inference — corpus-absent ⇒ lexicon-phantom — that McEnery & Brezina (*Fundamental
Principles*, 2022) dissect as "the problem of induction writ large," citing the exact
Tognini-Bonelli passage that licenses it. Compounding factors a reviewer will stack:

- **Size floor.** Reppen and Walter (Routledge Corpus Handbook) put lexicographic sense
  capture at tens-to-hundreds of millions of words (Biber 1990/1993); DCS is 5.6 M.
- **No sampling frame.** A 19-century historical corpus skewed to epic + śāstra cannot be
  "representative" of épigraphique or lyric registers — so Ch. 14's corpus-absence rate
  partly measures DCS's holes.
- **Low-frequency vs absence.** Walter's neologism caveat is the mirror of M01's claim: in
  a small corpus the two are indistinguishable.
- **Significance at scale.** Kilgarriff 2005: on N in the hundreds of thousands, p-values
  reject trivially; the field's bar is effect sizes + CIs + dispersion (Desagulier for the
  R-practice standard).

**Fix (no architecture change):** state every corpus-absence figure as a bounded
observation about DCS coverage with dispersion and size disclosed, and route all
quantitative chapters through one explicit statistical-practice statement (where that
statement lives is the §4.2 decision). This converts the biggest liability into a
methodological showcase — exactly what the evidence-grading thesis claims to do.

### 2.2 Dictionary-use / reception research

Nesi and Pastor & Alcina (Bloomsbury) and Müller-Spitzer & Wolfer (*Internet Lexicography*
Ch. 9 — a full chapter in the series-mate volume) treat empirical user research as
first-class metalexicography. M01 is entirely production-/source-side: no user, no look-up
behaviour, no reception. **Fix:** one honest paragraph in the Introduction scoping the book
to the evidence side and citing the use-research literature as the complementary
programme — do not bolt on a user study.

### 2.3 Sense ontology

Lew (Bloomsbury) argues lexicographic senses "cannot be expected to mirror linguistic
reality" (Hanks's meaning potentials, Sinclair's idiom principle). M01 reifies senses as
graph nodes. **Fix:** Ch. 2 and Ch. 6 must state that the graph models *the dictionaries'
sense assertions*, not language-internal sense entities — a one-move concession that
disarms the objection and is already implicit in the evidence-graph thesis.

### 2.4 The structural-terminology canon

The plan's own vocabulary ("layered", "blocks", "cross-reference graphs") must be mapped
onto the Hausmann & Wiegand macro/micro/medio/megastructure canon as codified in Hartmann
& James — ch05 already does this; ch02 and the plan's part-titles do not yet. Free win:
Hartmann & James flag mediostructure as *lacking* a systematic framework — Ch. 10 fills a
gap the standard reference itself names.

### 2.5 Dictionary criticism as method

Akasu (Bloomsbury) and Jackson Ch. 14 document an established evaluation methodology
(internal/external criteria, representative sampling). Ch. 15's error typology and every
comparative-evaluation move should position against it; Hartmann 1996's complaint that
criticism has been "beset by personal prejudice rather than … objective criteria" is a
ready-made warrant for the evidence-graded alternative.

### 2.6 Smaller expected touches

- **Function theory** (Fuertes-Olivera/Nielsen; the Aarhus school): one Introduction
  paragraph locating the evidence graph relative to lexicographic-function theory.
- **Definition typology / defining styles**: acknowledged in Ch. 5 or the method appendix
  (the plan's §6 already lists a definition-typology dataset as a known gap).
- **Bilingual-dictionary metalexicography** (Adamska-Sałaciak, Bloomsbury): MW/Apte are
  bilingual; one framing note on why M01 treats them as evidence sources rather than
  through equivalence theory.
- **κ methodology source**: none of the 37 works treats coefficient-based agreement
  properly — Ch. 5/15's κ apparatus must cite the computational-linguistics literature
  (Artstein & Poesio 2008; Krippendorff), which is *outside this library*.

---

## 3. Competing-works positioning (feeds BRILL_PROPOSAL §7 "gap this book fills")

**The stress test.** The library contains the strongest available challenge to M01's
novelty claim: *Internet Lexicography* (Klosa-Kückelhaus ed., De Gruyter, **LSM 164, 2024**
— the same series M01 targets, open access). Its Ch. 4 already states that "all lexical
resources can be represented in graph databases" and presents RDF triples as "statements
about two resources"; its Ch. 1 already recommends Git-style versioning with per-entry
revision histories; its Ch. 8 already surveys crowdsourced correction and user
quality-voting. **"Dictionary as graph" is therefore not citable as M01's contribution — a
referee from this author group would read it as reinvention.**

**What survives, precisely.** None of the 37 works — and none of the proposal's existing
comparables — carries a **typed evidence-grade vocabulary applied per lexicographic
statement** (`observed | derived | inferred | reviewed`) **with review provenance as a
first-class, machine-readable layer**, and none treats an indigenous lexicographic
tradition as structured data on equal terms. In the library's own terms:

- Hartmann & James have "evidence" only as an entry-level source-type continuum
  (introspection → fieldwork → corpus), never as a graded per-statement attribute.
- Apresjan systematizes *what a dictionary says* (types, portraits); M01 systematizes *the
  evidentiary status of each thing said* — orthogonal and complementary layers.
- *Internet Lexicography* has graphs, versioning, and provenance as *encoding and
  workflow*; the epistemic typing of each statement is absent — which is exactly the
  "encoding vs epistemics" slogan, now with a same-series citation to anchor it.
- Piotrowski (Bloomsbury) documents that the field openly disputes whether lexicography
  *has* a theory — M01 can position the evidence-graded model as a concrete answer.

**Paste-ready paragraph for the proposal (§7, replacing the current "gap" sentence):**

> The reference apparatus of the field — Hartmann & James's *Dictionary of Lexicography*,
> Jackson's *Bloomsbury Companion*, and, in this series, Klosa-Kückelhaus's *Internet
> Lexicography* (LSM 164) — now treats graph data models, versioned revision histories,
> and crowdsourced correction as established practice. What none of them provides, and
> what no competing title grades, is the **epistemic status of each lexicographic
> statement**: an explicit, machine-readable evidence grade
> (`observed | derived | inferred | reviewed`) with review provenance, attached per
> statement across a whole dictionary family — with an indigenous lexicographical
> tradition (kośa/Pāṇinian) entering the same graph as first-class structured data rather
> than exotic noise. Where existing standards and handbooks standardize the *encoding* of
> dictionaries, this book standardizes their *epistemics*; where Hartmann & James note
> that the systematic study of mediostructure "is still to be developed," Chapters 10–13
> supply exactly that framework, quantified over forty-four dictionaries.

**Comparables to add** (see §6): Vogel 1979 as the indigenous-survey predecessor
(complementing Patkar 1981); Baalbaki 2014 as the tradition-history genre model.

---

## 4. New chapter/section candidates

### 4.1 Comparative part-bridge: "Sanskrit among the lexicographical civilizations" — RECOMMENDED

The library supports it asymmetrically:

- **Baalbaki (Arabic) can carry the bridge alone**: a theorized macrostructure typology
  (*mubawwab/muǧannas* + three formal orders) ∥ Ch. 4; a doctrinal witness system
  (*šawāhid*, *ʿuṣūr al-iḥtiǧāǧ*) ∥ Ch. 11; a documented millennium of acknowledged and
  concealed borrowing ∥ Ch. 10/13.
- **Ferri (Latin) is section-level**, cited essay-by-essay (Maltby → registers;
  Lhommé → epitome descent; Gatti → citation canon; Furno → accretion).
- **Dickey (Greek) is the third leg**: glossography/scholia lineages, the
  *Viermännerkommentar* source-precedence hierarchy, Atticist register-marking.

**Recommended form:** a ~10–15 pp. part-bridge (most naturally opening Part IV, before the
mediostructure/citation chapters), structured on Baalbaki's three axes — **order** (how
each civilization solved retrieval-vs-semantic-map), **witness** (who counts as evidence,
until when), **copying** (how inheritance was practiced and concealed) — NOT a full
chapter: neither the Latin nor the Greek source sustains chapter-length comparison, and a
full chapter would dilute the sole-authored data-driven signature of the other 15. The
part-bridges are already budgeted as new writing in
[BOOK_PLAN.md §3](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md),
so this upgrades an existing slot rather than adding one. Honesty clause to keep: neither
comparandum has a sexual-taboo screen — Ch. 1's phenomenon is Europe-specific.

### 4.2 Standalone corpus-methods chapter — genuine fork, parked as `@DECIDE`

The corpus shelf argues *decisively* that the §2.1 material is chapter-sized: the
absence/representativeness/statistics caveats are orthogonal to Ch. 2's evidence-grading
machinery, and both serious corpus books structurally separate corpus epistemology from
analysis. Two honest options:

- **(a) New "Corpus as evidence" chapter** (or a formal half of Ch. 2 split): hosts the
  DCS disclosure (size, skew, no sampling frame), the statistical-practice contract
  (effect sizes + CIs + dispersion; log-likelihood; no bare p-values at scale), and the
  absence-inference rule, cited once by Ch. 3/5/12/14. Cost: alters the locked 15-chapter
  architecture (15 articles + glue), breaking the 1-chapter-per-article symmetry.
- **(b) Fold into Ch. 2 as a marked section** (~6–8 pp., "The corpus as a bounded
  witness"): preserves the architecture; risks burying the single caveat most likely to
  draw fire, inside the chapter a referee is least likely to re-read.

Because MG locked the 15 on 06-07-2026, this is a human call → parked as `@DECIDE` in
[Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
Recommendation if asked: **(b)** — the book's identity is the article spine; a disciplined
Ch. 2 section with a page of DCS disclosure satisfies the same referee at lower structural
cost.

### 4.3 Rejected candidates (considered, not recommended)

- **User-study/reception chapter** — no data exists and none is collectable on the book's
  timeline; the §2.2 Introduction paragraph is the honest treatment.
- **Separate "comparative etymology" chapter** from the Latin/Greek etymologica — the
  material is associative etymologizing, methodologically incommensurable with *vyutpatti*
  (Ch. 9 gets a caveat, not a sibling).
- **NLP/tooling chapter** from the Hellwig-circle papers — they serve as citations in
  Ch. 2/3; a tooling chapter would re-open the "measures the project, not the
  dictionaries" boundary error ch02 §1 explicitly quarantines.

---

## 5. Quality-bar / abandonment audit — chapter by chapter

Dispositions: **KEEP** (meets bar) · **KEEP+REframe** (survives only with named
repositioning) · **@DECIDE** (structural call for MG). No chapter earns CUT or
DOWNGRADE-to-appendix: the plan's §9 anti-salami clustering already absorbed the weak
stand-alone candidates (A03/A07 into Ch. 10), and each remaining chapter holds a distinct
dataset. The bar used: how the professional literature treats the topic (under-theorized /
solved-elsewhere / too narrow).

| Ch. | Verdict | The one-line reason |
|---|---|---|
| 1 | **KEEP** | Comparanda strengthen originality: no Arabic/Latin/Greek taboo-screen equal exists |
| 2 | **KEEP+REframe** | "Dictionary as graph" is standard in LSM 164; novelty must be restated as the evidence-grade layer |
| 3 | **KEEP+REframe** | Corpus-absence inference + sub-floor corpus size must be disclosed and bounded |
| 4 | **KEEP** | The book's most original chapter; Vogel + Baalbaki give it a comparative spine |
| 5 | **KEEP** | Already at bar — the model chapter (triangulation + κ-scored gold benchmark) |
| 6 | **KEEP** | Needs Lew (sense ontology) + Apresjan (regular polysemy) framing, both cheap |
| 7 | **@DECIDE** | Apresjan solved the principle; keep only as an empirical *test* of it — or merge into Ch. 6 |
| 8 | **KEEP** | Sound; Apresjan's integrated description supplies the missing Western frame |
| 9 | **KEEP** | Referee-hardened already (A35 M1–M5); add the Arabic *ištiqāq* parallel + Latin caveat |
| 10 | **KEEP** | Fills a gap Hartmann & James explicitly name — claim the mediostructure warrant |
| 11 | **KEEP** | *šawāhid* comparison upgrades it from binary contrast to three-system typology |
| 12 | **KEEP+REframe** | Prose (1/5) must be written to the Kilgarriff/log-likelihood/dispersion bar from day one |
| 13 | **KEEP+REframe** | Inheritance-as-fact is a textbook truism; the chapter's claim is the quantified forensic method |
| 14 | **KEEP+REframe** | The 68.3 % headline is the induction problem squared; reframe as DCS-coverage finding |
| 15 | **KEEP** | Data is field-unique; must enter the existing user-participation/error-handling literature |

### The four load-bearing reframes

**Ch. 2 (A01).** ch02 as written is *close*: its §7 already cites FAIR/PROV-O/data
statements and its no-inference-at-build rule is distinctive. What it lacks is the
same-series positioning: one paragraph conceding that graph/RDF modelling, versioning,
and crowdsourcing are established (Herold/Meyer/Wiegand; Abel & Meyer) and that the
contribution is the *epistemic typing* of each statement plus the enforcement granularity.
Also adopt the Hausmann & Wiegand structural canon by name (ch05 already does; ch02 §2
mentions Wiegand's microstructure only in passing), and add the Lew concession (§2.3).

**Ch. 3 (A40).** Data-only today (4/5 data, no prose) — so the reframe costs nothing: the
prose should be *born* compliant. Frame: growth of the *recorded* inventory (Thorndike's
balancing as the Western control), and corpus-grounding as a DCS-coverage map with
per-genre dispersion, never "words that don't exist." Hellwig's tagger paper gives the
chapter an unexpected weapon: MW's inventory decisions have *measured* downstream NLP
costs — inclusion policy is consequential, hence worth grading.

**Ch. 7 (A33) — the genuine `@DECIDE`.** Apresjan's *Systematic Lexicography* establishes
synchronic-derivational ("genetic") sense ordering as the correct principle *and supplies
its mechanism* (regular polysemy; assertive-component removal), and the field has further
named vocabulary (Considine's weakly/strongly historical; frequency ordering as modern
default). A chapter presenting "genetic, not historical" as a discovery restates a solved
problem — precisely MG's category (b). What is *not* solved: nobody has **measured**, on a
multi-dictionary family with a dated corpus, how often sense-1 is the historically oldest
sense (A33's 73.5 % vs 52.7 % floor, τ = 0.375) — i.e. how far actual 19th-century practice
diverges from both the historical and the Apresjanian ideal. Two dispositions, MG's call:
**(a)** keep as a chapter, rebuilt as "an empirical test of Apresjan's ordering principle
against the European Sanskrit family" (survives, and the anti-salami §9 note already
demands Ch. 6/7 cross-referencing); **(b)** fold into Ch. 6 as its second half ("senses:
inheritance and order"), yielding a 14-chapter book. Both honest; (a) preserves the
1-article-1-chapter symmetry, (b) is structurally safer against the "two chapters on
neighbouring sense phenomena" referee note. → `@DECIDE` row added to GTD.

**Ch. 13 (A10).** Keep the dataset, rebuild the pitch: cite Landau's dictum via Jackson
("all commercial dictionaries are based to some extent on preexisting works") *first*,
then define the contribution as the forensic method at scale (shared-error ≈ 0 %,
citation-order agreement 0.811) — "dictionary archaeology" (Hartmann & James) done
quantitatively, with Zgusta 1988 as the hand-probe ancestor (ch02 §7 already frames this
correctly; Ch. 13's own text must lead with it). Baalbaki's concealed-borrowing cases and
Dickey's VMK stratification supply the cross-civilizational depth that lifts the chapter
from a Sanskrit curiosity to a method statement.

### Under-theorized spots that are additions, not cuts

- Ch. 11/12 currently treat `<ls>` vs *iti* as a two-register story; Baalbaki's *šawāhid*
  makes it three — one added comparative section, no restructuring.
- The method appendix (PROV-O / TEI `@cert` crosswalk) should also cite *Internet
  Lexicography* Ch. 4's TEI/LMF/RDF inventory as the standards baseline.

---

## 6. Corrections to existing book documents (pending — not applied in this pass)

1. **[BRILL_PROPOSAL.md §7](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md)
   comparables entry is bibliographically wrong:** *Internet Lexicography* is
   **Klosa-Kückelhaus (ed.), sole editor** — not "Klosa-Kückelhaus & Wolfer (eds.)".
   Wolfer co-authors only its Ch. 9. A wrong citation of the target series' own volume, in
   the proposal sent to that series' editors, is a credibility hit — fix before submission.
2. **Comparables list additions** (BRILL_PROPOSAL §7 + BOOK_PLAN §7d): add **Vogel,
   *Indian Lexicography* (1979)** — the indigenous-survey predecessor alongside Patkar
   1981 — and **Baalbaki, *The Arabic Lexicographical Tradition* (Brill 2014)** as the
   genre model for a tradition-history at Brill (also the in-house precedent argument).
3. **BOOK_PLAN §6 data-gaps row**: the κ / inter-annotator item should name its method
   source (Artstein & Poesio 2008; Krippendorff) since no work in the 37 covers it.
4. **Library defect**: `Hints to the Study of Sanskrit Compounds.md` is an empty scan
   (Google boilerplate only, no OCR'd body) — re-OCR or drop; tracked in the
   [metadoc](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/LEXICOGRAPHY_MANUALS.meta.md)
   backlog.

---

_Dr. Mārcis Gasūns_
