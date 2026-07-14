# Digital Sanskrit Lexicography (Brill monograph) — changelog

_Created: 07-07-2026 · Last updated: 13-07-2026_

Tracks changes to the book build plan and any future manuscript/front-matter drafts in this
folder. Registry ID **M01** in [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md).

## [Unreleased]

### Added — 13-07-2026 (H867, BOOK_PLAN metadoc)

- **Companion metadoc created** →
  [BOOK_PLAN.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.meta.md),
  the sibling record for the plan of record — purpose/audience/provenance, a **Use cases**
  section (who consults the plan + what the book, its 12 committed chapters as standalone
  articles, and its datasets can be used for), a ranked improvement backlog (Ch. 3 / Ch. 11 /
  ch02 corpus-section / DOI sprint / front-back matter, each with an owner or `parked` verdict),
  known limitations (P-number trap, source-path staleness bugs, rights posture), intended-use /
  known-misuse, and maintenance/sunset plan. `.gitignore` allowlist extended with `!*.meta.md`.

### Added — 13-07-2026 (H866, Ch. 6 merge)

- **Ch. 6 written as a genuine MERGE of two articles** (A02 + A33), not a conversion →
  [chapters/ch06_senses_inheritance_and_order.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch06_senses_inheritance_and_order.md).
  Per the [BOOK_PLAN §3](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
  merge ruling: **Part I — Inheritance** = A02 *Condensation, Not Inflation* (csl-atlas
  [paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md));
  **Part II — Order** = A33 *Genetic, Not Historical* (local
  [papers/A33_sense_ordering_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md)).
  Both halves reframed against **Apresjan** (regular polysemy as the sense-propagation mechanism;
  the synchronic-derivational/genetic ordering principle as the theory the 73.5% lead-sense-oldest
  result *tests* — the crosswalk mandate), plus **Lew** (sense individuation before senses become
  graph nodes — Hanks/Sinclair), **Considine** (weakly/strongly historical dictionaries),
  **Walter** (frequency ordering / corpus-unattested senses), **Jackson §14.5 + Kipfer**
  (sense-order indeterminacy), **Partridge** (intra-entry order as editorial choice). Provenance
  headnote flags the dual sourcing; both articles stay independently citable. Every count and
  table from both (H1 r=0.036 flat, family means 1.00–2.42; H2 0.762 vs 0.705 overall / 0.768 vs
  0.661 within-edge z=1.80 p=0.07, 82/84 cited on one edge; H3 Wilson→Śabda-Sāgara 0.906 copy /
  Wilson→Yates 9→5.7 / Apte 10.8→7.8; SKD 53.3% / VCP 77.6% fusion; PWG 73.5% lead-oldest τ=0.375,
  MW 69.4%; Vedic density 23.4/24.8/2.3/0.0%; 26.5% lead-sense change on re-sort) carried over
  unchanged. **12 of 14 chapters now in book form** (all but the two prose-thin data chapters
  Ch. 3 / Ch. 11).

### Added — 13-07-2026 (H865, Ch. 7 conversion)

- **Ch. 7 converted journal→book** →
  [chapters/ch07_indigenous_microstructure.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch07_indigenous_microstructure.md),
  the book-form version of A04 *Grammar Without Tags: The Verbal-Root Microstructure of the
  Indigenous Sanskrit Kośa* (csl-atlas source
  [paper_indigenous_microstructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_indigenous_microstructure.md))
  — the last straight one-to-one conversion. Abstract + keywords stripped, provenance headnote
  added (A04 stays citable at IJL / WSC 2027), companion "P-numbers" remapped (root-parser
  agreement → **Ch. 2 §3.9**, sense/citation companions → **Ch. 6 / Ch. 10**, derivation sibling
  → **Ch. 8**), and the crosswalk grounding woven in — **Apresjan** (integrated
  grammar–dictionary description: the entry presupposes the grammar), **Baalbaki** (Arabic
  *jaḏr/wazn* root-and-pattern as the structural analogue of *dhātu* organisation), **Lowe** (the
  participle/root lemmatization boundary), **Gerow** (transmission of the indigenous apparatus),
  atop the already-cited **Vogel**. The zero-means-nothing doctrine tied to its macrostructure
  twin (Ch. 4). Every count and table (SKD 2,544 roots / VCP 2,230 / KRM 1,757 / YAT 1,643 /
  SHS 463 vs ≤8 in every European dict; anubandha resolves gaṇa 1,737 / pada 1,498; 85.5% gaṇa
  agreement across 1,526 roots, SKD–VCP 92.8%, SKD–KRM 95.0%, pada 75.3%, transitivity 81.4%)
  carried over unchanged. **11 of 14 chapters now in book form** (all but Ch. 3 / Ch. 11
  prose-thin and Ch. 6 interleave).

### Added — 13-07-2026 (H863, Ch. 14 conversion)

- **Ch. 14 converted journal→book** →
  [chapters/ch14_error_typology.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch14_error_typology.md),
  the book-form version of A12 *Surface, Not Substance: A Two-Axis Error Typology of Twelve
  Years of Correction* (csl-observatory source
  [paper-obs-t-error-typology.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md)).
  Abstract + keywords stripped, provenance headnote added (A12 stays citable at LREC-COLING /
  IJL), snapshot noted as the current **52,498-event** cut (the book's data table listed an
  earlier 50,953), the OBS-Q process companion kept as a companion finding and the csl-atlas
  microstructure companions remapped to **Ch. 10 / Ch. 6 / Ch. 7**. Crosswalk grounding woven
  in — **Abel & Meyer** (user-participation direct/indirect/accessory + quality-voting — Ch. 14
  is a *case* of this literature), **Klosa-Kückelhaus & Tiberius** (error-handling in the
  lexicographic process), **Herold/Meyer/Wiegand** + **Brewer** (versioning / per-entry revision
  histories / OED-Online + OED revision layers — cite, don't reinvent), **Akasu** + **Hartmann &
  James** (dictionary-criticism methodology / error analysis as evidence), **Partridge**
  (pre-digital collaborative revision). The `observed`/`derived`/`inferred` evidence labels tied
  explicitly to Ch. 2's grade vocabulary; "corrected ≠ wrong" framed as the book's
  interpretive-bounds discipline. Every count and table (52,498 events / 43 dicts / 208
  correctors, 2014–2026; 64.3% derived; sense 52.7% of located edits; minor-edit rate headword
  85.6% / sense 38.2% / markup 5.2%; χ²=26,192.5, Cramér's V=0.432; headword 0.88→0.10, markup
  0.00→0.17; b→v 341; median edit distance 2, 63% ≤2 chars) carried over unchanged. **10 of 14
  chapters now in book form** (ch01, ch02, ch04, ch05, ch08, ch09, ch10, ch12, ch13, ch14).

### Added — 13-07-2026 (H861, Ch. 13 conversion)

- **Ch. 13 converted journal→book** →
  [chapters/ch13_renou_registers.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch13_renou_registers.md),
  the book-form version of A34 *Register, Not Just Period: Renou's Subsections as an Orthogonal
  Axis* (local papers source
  [A34_renou_register_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_renou_register_note.md)).
  Abstract + status apparatus stripped, provenance headnote added (A34 stays citable at Lexikos
  / IJL / eLex), the A08 citation-register companion remapped to **Ch. 10**. **Mandatory
  crosswalk reframe applied:** the headline "68.3% corpus-absent" recast as an explicit
  statement about **DCS-corpus coverage** (the DCS is a literary corpus containing no
  inscriptions), under the **McEnery & Brezina** corpus-absence caveat — not a claim of absence
  from the language. Further grounding woven in — **Ferri/Maltby** (Servius' three-register
  *grandiloquus/medius/humilis* system, tying back to Ch. 1's decorum), **Dickey** (Atticist
  normative register-marking), **Geyken & Lemnitzer** (diasystematic labelling from corpus
  metadata as current practice), **Partridge** (graded register scales). Every count and table
  (770,292 entries / 8 dicts; 709 épigraphique / 484 = 68.3% corpus-absent, strict 518/73.1%;
  bhāṣya 14,498 / kāvya 26,973 / bauddha 25,740 / jaina 286 at 0%; cross-axis slices 6,895 /
  20,758 / 25,220; finite-verb density 14.4%→6.7%, bhāṣya 6.25% vs kāvya 7.48%) carried over
  unchanged. **9 of 14 chapters now in book form** (ch01, ch02, ch04, ch05, ch08, ch09, ch10,
  ch12, ch13).

### Added — 13-07-2026 (H860, Ch. 12 conversion)

- **Ch. 12 converted journal→book** →
  [chapters/ch12_apparatus_not_errors.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch12_apparatus_not_errors.md),
  the book-form version of A10 *Apparatus, Not Errors: How Monier-Williams Inherited the
  Petersburg Lexicon* (csl-atlas source
  [article_21_apparatus_not_errors.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md)).
  Abstract folded into the opening, provenance headnote added (A10 stays citable at *Digital
  Scholarship in the Humanities*), companion redundancy/L0 material remapped to **Ch. 9** + the
  **Ch. 2 §3.1** containment-is-a-floor rule, and the crosswalk grounding woven in — **Hartmann
  & James** ("dictionary archaeology"), **Zgusta 1988** (*Copying in Lexicography*, carried
  from Ch. 2), **Jackson/Landau** (inheritance-is-a-truism → M01's delta is quantification at
  corpus scale), **Baalbaki** (Ibn Manẓūr absorbing the *Nihāya* "without mentioning him"),
  **Dickey** (the Homer-scholia *Viermännerkommentar* source-precedence), **Ferri/Furno**
  (Calepino→Estienne accretion), **O'Keeffe & McCarthy** (forensic-linguistics fingerprinting).
  Every count and table (41-dict calibration; rare-lemma containment PWG→MW 0.70/0.82; citation
  source-Jaccard 0.16–0.19 vs 0.004–0.017 null; 587 rare shared refs, 41,552 compressions;
  homonym 64–77%; citation-order 0.811 / 47.8% identical; Ahlborn 2/123≈0% shared error; 206/565
  Harivaṃśa corroborated ≈75× null) carried over unchanged. **8 of 14 chapters now in book
  form** (ch01, ch02, ch04, ch05, ch08, ch09, ch10, ch12).

### Added — 13-07-2026 (H857, Ch. 8 conversion)

- **Ch. 8 converted journal→book** →
  [chapters/ch08_paninian_derivation.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch08_paninian_derivation.md),
  the book-form version of A35 *Cross-Dictionary Consistency of Pāṇinian Derivation in the
  Cologne Lexica* (csl-orig source
  [PAPER_DRAFT.md](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/PAPER_DRAFT.md)).
  Two internal planning memos (submission-readiness, technique-adoption assessment) stripped,
  abstract folded into the opening, provenance headnote added (A35 stays citable at IJL /
  Lexicographica / ISCLS), the A04 microstructure companion remapped to **Ch. 7**, and the
  crosswalk §1 grounding woven in — **Baalbaki** (*al-ištiqāq* + the *ʿAyn* ∥ Sībawayhi
  "lexicography born as grammar's twin"), **Bowern & Evans** / Koch / Mailhammer (the
  comparative-method / morphological-reconstruction frame), **Ferri/Pieroni** (the *caution*
  that Latin etymologizing is associative, not rule-governed like *vyutpatti*), **Partridge**
  (the Skeat–Weekley cognate-grouping-vs-cross-referencing design fork). Every count and table
  (68,510 derivational statements over 10 dicts; affix agreement 91.7–100%; kāraka 89–100%;
  WIL 50.1% canonical, WIL↔SKD 22.9%→66.7% filtered; 30/48 same-surface, 4/48 genuinely
  different; MW↔PWG root 64.2%) carried over unchanged. **7 of 14 chapters now in book form**
  (ch01, ch02, ch04, ch05, ch08, ch09, ch10).

### Added — 13-07-2026 (H854, Ch. 10 conversion)

- **Ch. 10 converted journal→book** →
  [chapters/ch10_citation_registers.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch10_citation_registers.md),
  the book-form version of A08 *Two Citation Registers and the Dictionary-to-Book Gap*
  (csl-atlas source
  [paper_citation_registers.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md)).
  Abstract + keywords stripped, provenance headnote added (A08 stays citable at IJL),
  companion "P-numbers" remapped (resolvability/register metrics → Ch. 2 §3.4/§3.5, P2 →
  Ch. 6), and the crosswalk grounding woven in — **Baalbaki** (the *šawāhid* + *ʿuṣūr
  al-iḥtiǧāǧ* epochs-of-sound-usage + Bedouin-informant screening as a doctrinally-theorized
  third witness system), **Ferri/Gatti** (Nonius' *auctores* canon + Lindsay's law as the
  European antecedent of the bounded citation list), **Hartmann & James** ("source code"),
  **Jackson** (Murray's OED reader-slip method). The SKD rank inversion (`<ls>`-last vs
  *iti*-2nd of 44) tied explicitly to the Ch. 4/7 "zero means instrument, not absence"
  doctrine. Every count and table (1,245,644 `<ls>` citations; 59.3% locator-bearing;
  ~507,000 bare / ~41% dictionary-to-book gap; 2,166 sources ≥10×; SKD 80,164 / VCP 15,619 /
  KRM 12,359 *iti*) carried over unchanged. **6 of 14 chapters now in book form** (ch01,
  ch02, ch04, ch05, ch09, ch10).

### Added — 13-07-2026 (H853, Ch. 9 conversion)

- **Ch. 9 converted journal→book** →
  [chapters/ch09_xref_lineage.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch09_xref_lineage.md),
  the book-form version of A05 *Pointing Inward: Cross-Reference Graphs as a Signal of
  Dictionary Descent* (csl-atlas source
  [paper_xref_lineage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md)).
  Abstract + keywords stripped, provenance headnote added (A05 stays citable at a DH /
  metalexicography venue / WSC 2027), companion "P-numbers" remapped to book chapters
  (P1→Ch. 2 §3.6 metric, P2→Ch. 6, P4→Ch. 7, P6→Ch. 4), the A03 "three axes of descent"
  companion **absorbed** into the chapter's own content/convention/inheritance decomposition
  (BOOK_PLAN §3 "Ch. 9 absorbs A03/A07"), and the crosswalk grounding woven in — **Hartmann &
  James** (mediostructure "a framework … still to be developed" claimed as the chapter's
  warrant), the **Routledge Historical Linguistics handbook** phylogenetics vocabulary
  (Weiss/Hale/François/Dunn), **Engelberg et al.** (linking/access-structure frame), **Ferri**
  (Verrius→Festus→Paul / Donatus→Servius as documented descent-chain comparanda). **Correctness
  fix:** the source's §3.2 swapped the AP/AP90 edition labels — corrected against Table 1 and
  the referee note (AP90 = 1890, AP = 1957 revision). Every count and table (PWG 22,937 edges;
  MW 7,637; the AP×AP90 85.5% positive control at J=0.74; MW×PWG 641 shared edges / 21.8% at
  J=0.069; the prefix-hub *a°* 320 / *mahā°* 254; Benfey's zero) carried over unchanged. **5
  of 14 chapters now in book form** (ch01, ch02, ch04, ch05, ch09).

### Added — 13-07-2026 (H851, Ch. 4 conversion)

- **Ch. 4 converted journal→book** →
  [chapters/ch04_kosha_macrostructure.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch04_kosha_macrostructure.md),
  the book-form version of A06 *Order Is the Dictionary: A Macrostructural Model of the
  Versified Synonymic Kośa* (csl-atlas source
  [paper_kosha_macrostructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md)).
  Abstract + keywords stripped, provenance headnote added (A06 stays citable at IJL / WSC
  2027), companion "P-numbers" remapped to book chapters (P1→Ch. 2 method, P4→Ch. 7
  indigenous microstructure), the crosswalk §1 grounding woven in — Vogel (already primary),
  **Baalbaki** (*mubawwab/muǧannas* + the three formal orders; the alphabet is not one
  thing), **Hartmann & James** (access structures), **Jackson**/Hüllen (European
  onomasiological tradition), **Partridge**, **Dickey** — and the two draft "author to
  verify" placeholders resolved into one honest footnote (the Wilson-1819 kośa descent kept
  as asserted lineage, quantification deferred to the sense-alignment study). Every count and
  table (7,907 ARMH records / 860 verses / 9.2 syn-per-verse; 1,965 ABCH records / 4,619
  lexemes; the 56-Viṣṇu peak; the gender apparatus) carried over unchanged. **4 of 14
  chapters now in book form** (ch01, ch02, ch04, ch05).

### Added — 13-07-2026 (H846, Ch. 1 conversion)

- **Ch. 1 converted journal→book** →
  [chapters/ch01_latin_discretion_screen.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch01_latin_discretion_screen.md),
  the book-form version of the A36 Latin discretion-screen note
  ([papers/A36_latin_obscena_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena_note.md)).
  Abstract + venue/status apparatus stripped, register unified to the book's first-person,
  a provenance headnote added, the crosswalk §1/§4.1 grounding woven in (Ferri on Servius'
  decorum-hierarchy as the Greco-Roman genealogy; Baalbaki on the Arabic *laḥn al-ʿāmma*
  correctness-screen as the contrast case; the "phenomenon is Europe-specific" honesty
  clause), and cross-references remapped to sibling chapters (Ch. 2 method, Ch. 4/7 kośa
  contrast, Ch. 6 senses, Ch. 13 Renou registers). Every count and table (2,104 senses;
  875 in the Petersburg core; the vulgar-veil list of 79 senses; the diachronic and
  corpus-wide sweeps) carried over unchanged. **3 of 14 chapters now in book form** (ch01,
  ch02, ch05).

### Changed — 13-07-2026 (MG ruling on H505's corpus-methods `@DECIDE`)

- **Standalone corpus-methods chapter fork resolved as option (b)** — a marked section
  inside Ch. 2 ("The corpus as a bounded witness", ~6–8 pp.), *not* a standalone chapter.
  The 14-chapter/15-article architecture is unchanged; the DCS-disclosure +
  statistical-practice + absence-inference material is written into Ch. 2 at its next
  revision. Both H505 `@DECIDE` forks are now closed. Updated
  [LITERATURE_CROSSWALK.md §4.2](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md)
  and [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
  §11.

### Added — 12-07-2026 (H782, A58 comparative-taxonomy aside)

- **Ch. 2 §3.10** gains a one-paragraph comparative aside on the varga scaffold itself:
  the A58 semdom ↔ Amarakosha crosswalk's structure agreement (67%) and the counted
  grammatical-annex symmetry (AK kāṇḍa 3 46.4% of synsets vs semdom top-9 9.4% of
  domains, converging 10.7% vs 9.4% without nānārtha —
  [SL FINDINGS §77](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)),
  as validation that the indigenous taxonomy works as a cross-epoch measurement frame.
  Citation-level only; A58 stays outside M01's 15-article glue list.

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
  ([MWS papers/microanalysis/PAPER.md, `docs-pass`](https://github.com/sanskrit-lexicon/MWS/blob/master/papers/microanalysis/PAPER.md))
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
