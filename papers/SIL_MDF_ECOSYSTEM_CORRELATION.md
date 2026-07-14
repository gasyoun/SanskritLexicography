# SIL MDF Ecosystem Correlation Map — Coward & Grimes 2000 vs the Cologne/CDSL Workbench

_Created: 11-07-2026 · Last updated: 11-07-2026_

Produced 11-07-2026 by Fable 5 (`claude-fable-5`) from a correlation analysis of
`MDF_2000.pdf` (local copy in `SanskritLexicography/papers/`, gitignored — canonical
source: [SIL Language & Culture Archives entry 5741](https://www.sil.org/resources/archives/5741),
not entry 90694 as originally cited here)
against the existing CDSL standards/export/translation infrastructure, plus the
[SIL Dictionaries & Lexicography hub](https://www.sil.org/dictionaries-lexicography).
MG rulings of the same date are recorded in §5; the resulting program of work (H721–H727) in §6.

**Rights check (H723, 11-07-2026):** the book's own copyright page (p. ii) reads "©1995,
2000 by SIL International. ALL RIGHTS RESERVED," granting only the right to share the
accompanying MDF software diskette non-commercially — not the text. `papers/MDF_2000.pdf`
is therefore `.gitignore`d (local working copy only); the software-independent chapters
4–10 + appendices are digested as notes/paraphrase, not full-text reproduction, at
[`literature/md/Lexicography-Manuals/making-dictionaries-mdf-coward-grimes-2000.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/making-dictionaries-mdf-coward-grimes-2000.md).

## 1. What the book is

Coward, David F. & Charles E. Grimes. 2000. *Making Dictionaries: A guide to lexicography
and the Multi-Dictionary Formatter.* SIL International. 243 pp. PDF-only edition of the
1995 text ([archive entry](https://www.sil.org/resources/archives/90694); the software's
own page: [MDF at SIL Language Technology](https://software.sil.org/shoebox/mdf/)).

Two books in one:

- **Chapters 4–10 — a software-independent practical lexicography manual**: audience and
  purpose (§4.2), mono/bi/trilingual structure (§4.3, §5.2), root-oriented vs
  lexeme-oriented databases (§4.6), headword choice (§6.1), homonymy vs polysemy (§6.3),
  semantic domains (§6.4), lexical functions (ch. 7), folk taxonomies (§8.1), parts of
  speech (ch. 9), abbreviation strategy + RANGE SETS consistency checks (§9.6–9.7),
  topical extraction and front matter (ch. 10).
- **Chapters 1–3 + Appendices A–E — the reference for the MDF field schema**
  (`\lx`, `\ps`, `\ge`, …) that Toolbox/FLEx-lineage tools still read: alphabetized field
  markers (App. A), canonical relative field order (App. B), starter semantic domains
  (App. C), starter lexical functions (App. D), starter abbreviations (App. E).

The software half is legacy (Word 5/6 merge macros); the schema and the lexicography
chapters are the enduring part.

## 2. Correlation with existing work

The book lands on already-built infrastructure: the
[MDF export mapping](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/MDF_EXPORT_MAPPING.md)
in `csl-standards` is an **implemented third export profile** (beside TEI and
OntoLex/FrAC) — [`export-mdf.mjs`](https://github.com/sanskrit-lexicon/csl-standards/blob/main/scripts/export-mdf.mjs)
+ [`validate-mdf-profile.mjs`](https://github.com/sanskrit-lexicon/csl-standards/blob/main/scripts/validate-mdf-profile.mjs),
250/250 pilot records passing, 281 model-loss markers. Until 11-07-2026 the schema
knowledge came second-hand via the MUDIDI benchmark and Toolbox lore; the book is the
citable primary authority behind it.

| Book section | Existing asset | What the book adds |
|---|---|---|
| App. A–B: field markers + canonical **relative field order** | [MDF export mapping](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/MDF_EXPORT_MAPPING.md) field inventory; [`validate-mdf-profile.mjs`](https://github.com/sanskrit-lexicon/csl-standards/blob/main/scripts/validate-mdf-profile.mjs) | Field *ordering* is not yet validated; App. B defines it. Citable source for every marker. |
| §2.3: `\ge` vs `\re` vs `\de` semantics | The deferred `\gn`/`\de` choice for the Sanskrit–Sanskrit koshas (SKD/VCP) in the mapping doc | Settles the semantics the mapping doc explicitly parked. |
| Ch. 7 + App. D: **lexical functions** `\lf` | Relation mapping currently flattened to untyped `\cf` (graded partial/lossy) | `\lf` is a typed-relation field MDF *does* have — can lift part of the recorded lossiness. |
| §4.6: **root-oriented vs lexeme-oriented databases** | The PWG-vs-MW structural axis (root-organized Böhtlingk vs lemma-organized MW); Whitney/MW/DCS root crosswalks | Independent documentary-lexicography treatment of our central structural contrast, with "a suggested compromise" (§4.6.3) — citable in M01 and the sense-ordering work. |
| §6.3 homonymy vs polysemy; §5.4.1 homonym sort; §6.1 headword choice | MWS microstructure (homonym handling, headword-promotion M1); [A40 headword inventory note](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md); [A33 sense-ordering note](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md) | The field-linguistics baseline the historical-dictionary findings can be contrasted against. |
| §9.6 abbreviation strategy; §9.7 **RANGE SETS**; App. E | [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) policy; the MW `<ab>` inventory (194,879 occurrences) | RANGE SETS = the 1990s ancestor of validator-gate consistency checks over closed abbreviation vocabularies — direct methodological lineage. |
| §2.3 + §3.3.4 **finderlists** (reversal built from curated `\ge`/`\re` fields) | csl-atlas body/reverse headword-mining, **rejected at 38.6% precision** | SIL builds reversals from curated gloss fields, never mined from body text — independent corroboration of the rejection. |
| §10.2 writing the dictionary **introduction** | `/cologne-preface-ocr` front-matter recovery across the Cologne dictionaries | A normative checklist of what a preface must contain — recovered Cologne prefaces can be graded against it. |
| §6.4 + App. C **semantic domains** `\sd`; [semdom.org](https://semdom.org) (~1800 hierarchical domains) | No CDSL semantic-domain layer exists | A genuinely new axis — see §3 and H725. |
| MUDIDI Stage 2 target schema | [Parse-rules framing](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PARSE_RULES_FRAMING.md) + [parse-rules JSONs](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/parse-rules) (11 dicts); [related-work note](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/paper/related-work.md) | The book is the arbiter for the one remaining mapping-doc step: cross-checking a Sanskrit MDF sample against MUDIDI's MDF conventions. |

## 3. What the SIL hub adds on top of the book

The [sil.org/dictionaries-lexicography](https://www.sil.org/dictionaries-lexicography) hub
shows the living ecosystem the 2000 book grew into:

1. **The 6-stage [Dictionary Development Process](https://www.sil.org/dictionaries-lexicography/dictionary-development-process)**
   (collect → expand → standardize → front/back matter → publish → archive) is an
   externally citable framing skeleton. Cologne retro-digitization walks the same stages:
   CDSL keying = collecting, corrections + microstructure = standardizing, preface OCR =
   front matter, Pages/Webonary = publishing, kosha data hub + Zenodo DOIs = archiving.
2. **[Lexique Pro](https://software.sil.org/lexiquepro/) reads MDF SFM directly, no
   import step.** The `export-mdf.mjs` output can be dropped into an actual SIL consumer
   as a real-world smoke test — a far stronger validation claim than self-validation
   (→ H722).
3. **[LIFT](https://github.com/sillsdev/lift-standard) (Lexicon Interchange Format)** is
   the modern XML successor; [FLEx](https://software.sil.org/fieldworks/) and Lexique Pro
   both exchange it. MDF SFM buys MUDIDI comparability; LIFT buys consumption by living
   SIL tools (→ H721).
4. **[Webonary](https://www.webonary.org/)** publishes bilingual/multilingual dictionaries
   to the web with minimal technical help; **[Dictionary App Builder](https://software.sil.org/dictionaryappbuilder/)**
   does the same for mobile (from LIFT data). Both are channels to put Sanskrit
   dictionaries in front of the language-documentation audience (→ H726).
   [Pathway](https://software.sil.org/pathway/) (FLEx → InDesign/PDF/Epub) parallels the
   in-house InDesign book pipeline.
5. **[Rapid Word Collection](https://www.rapidwords.net/) + [semdom.org](https://semdom.org)'s
   ~1800 hierarchical semantic domains** — striking for Sanskrit because koshas
   (Amarakosha-style; SKD/VCP-adjacent) are *natively* semantic-domain-organized. A
   semdom ↔ kosha crosswalk would be a paper-grade novelty; no Sanskrit exists in the
   SIL/MUDIDI semantic-domain world (→ H725).
6. **[DLS courses](https://sites.google.com/sil.org/dls-course/home) + the
   [Webonary newsletter](https://www.webonary.org/category/news)** — community contact
   points for offering the Sanskrit MDF/parse-rules sample to MUDIDI and the SIL
   lexicography community (→ H726).

## 4. How MDF thinking can change dictionary practice at Cologne

The ruling of 11-07-2026 asked specifically how the book can change the way dictionaries
are treated at Cologne, and how it applies to the PWG→RU pipeline and the kosha data hub.
The answer is one shift with five consequences:

**The shift: treat each dictionary as a database with an explicit field schema and entry
grammar, not as marked-up text.** That is the book's core doctrine (§5.1: database
structure vs unstructured text) and it is what the csl-atlas
[parse-rules JSONs](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/parse-rules)
already do for 11 dictionaries — field inventory + abbreviation key + entry-boundary
rules per dictionary. The MDF lens says: make that the norm for all 44, and grade every
transformation's adequacy against it.

1. **PWG→RU cards are already isomorphic to bilingual MDF records** — headword (`\lx`),
   grammar (`\ps`), Russian definition (`\de`), English gloss lane (`\ge`), sources
   (`\bb`). Making the isomorphism explicit gives the RU translation an exchange format
   (consumable by Lexique Pro/Webonary/App Builder), makes the
   [LANG_PARITY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
   RU/EN lane discipline exactly the book's `\ge`-vs-`\de` national-vs-English contrast,
   and imports RANGE-SET-style closed-vocabulary gates for the
   [RU abbreviation policy](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
   (→ H727).
2. **kosha as the distribution point**: register MDF (and LIFT, once H721 lands) exports
   as dataset rows in the
   [kosha manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)
   and serve them as `data-v*` releases — the documentation community consumes CDSL data
   with its own tools instead of ours (→ H727).
3. **Lossiness ledger as standard practice**: `csl-standards` already grades every
   export clean/partial/lossy; the book's field semantics make those grades justifiable
   entry-by-entry instead of convention-by-convention (→ H721).
4. **Reversal discipline**: finderlists come from curated gloss fields only — this is
   now doctrine, corroborating the rejected reverse-mining experiment.
5. **Front-matter grading**: recovered Cologne prefaces get graded against §10.2's
   checklist of what an introduction owes its reader.

## 5. MG rulings (11-07-2026)

1. **Role of the book**: all of — citation source for papers; spec to refine the MDF
   export; digestion into
   [literature/md/Lexicography-Manuals](https://github.com/gasyoun/SanskritLexicography/tree/master/literature/md/Lexicography-Manuals);
   **plus** implementation in the PWG translation pipeline + kosha, and an explicit
   account of how it changes dictionary treatment at Cologne (§4 above).
2. **LIFT**: add now (not parked) — fourth serialization beside TEI/OntoLex/MDF.
3. **Lexique Pro smoke test**: run it.
4. **SIL reach**: all four — semdom ↔ kosha crosswalk, Webonary channel, Dictionary App
   Builder, community outreach (drafts only; nothing auto-sends).

## 6. Program of work

| Handoff | Stream | Executor | Depends on |
|---|---|---|---|
| [H721](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H721-Sonnet_csl-standards_mdf-spec-refine-lift-export_11.07.26.md) | MDF profile refinements from the book (App. B order, `\de` ruling, `\lf`) + LIFT fourth serialization | Sonnet | — |
| [H722](https://github.com/gasyoun/Uprava/blob/main/handoffs/H722-Fable_csl-standards_lexique-pro-mdf-smoke-test_11.07.26.md) | Lexique Pro real-consumer smoke test of the MDF pilot | Fable | H721 helpful, not required |
| [H723](https://github.com/gasyoun/Uprava/blob/main/handoffs/H723-Sonnet_SanskritLexicography_mdf-book-literature-digest_11.07.26.md) | Digest the book into literature/md + rights check on committing the PDF | Sonnet | — |
| [H724](https://github.com/gasyoun/Uprava/blob/main/handoffs/H724-Opus_csl-standards_coward-grimes-citation-wiring_11.07.26.md) | Wire Coward & Grimes 2000 citations into csl-standards PAPER, atlas related-work, M01/A33/A40 | Opus | — |
| [H725](https://github.com/gasyoun/Uprava/blob/main/handoffs/H725-Fable_SanskritLexicography_semdom-kosha-crosswalk-scoping_11.07.26.md) | Scope the semdom ↔ kosha crosswalk (paper-grade novelty check first) | Fable | — |
| [H726](https://github.com/gasyoun/Uprava/blob/main/handoffs/H726-Opus_Uprava_sil-publishing-channels-outreach_11.07.26.md) | Webonary + Dictionary App Builder channels + SIL/MUDIDI outreach drafts | Opus | H721 (LIFT), H722; `/publish-safety-check` gate |
| [H727](https://github.com/gasyoun/Uprava/blob/main/handoffs/H727-Fable_SanskritLexicography_pwg-kosha-mdf-integration_11.07.26.md) | MDF/LIFT lens on the PWG→RU pipeline + kosha data-hub registration | Fable | H721 |

_Dr. Mārcis Gasūns_
