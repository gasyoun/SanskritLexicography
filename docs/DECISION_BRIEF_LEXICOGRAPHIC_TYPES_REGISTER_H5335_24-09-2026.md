_Created: 24-09-2026 · Last updated: 24-09-2026_

# Decision brief — a controlled register of Sanskrit lexicographic types, or typing left implicit (H5335)

**Handoff:** [H5335](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5335-Fable_SanskritLexicography_lexicographic-types-register-decision-brief_23.09.26.md) (Fable 5, `claude-fable-5-1`, 24-09-2026) · epic E014 · seed: [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md § Methodological lineage](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md), the `@DECIDE seed` bullet. Every count below is a live probe run on 24-09-2026 against the local clones named in § Sources; nothing is quoted from memory.

## What is being chosen

Whether the evidence graph gets an explicit, controlled vocabulary of **Sanskrit lexicographic types** (Apresyan's *лексикографические типы*: groups of lexemes that the same grammatical rules are sensitive to and that must therefore be described on one grid) as a first-class layer sitting next to the four evidence labels, or whether typing stays where it is today: implicit, scattered across each dictionary's own microstructure and across five unrelated derived tables. The decision has a clock because P4 (*When zero means nothing: recovering the indigenous microstructure of Śabdakalpadruma and Vācaspatya*) is about to lock the record schema its paper and its Lex-0 export are built on (H5321, H5324).

## The two options, as plain sentences

1. **Adopt a minimal register now.** Publish one controlled vocabulary file of Sanskrit lexicographic types, parallel to [EVIDENCE_LABELS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md), limited in version 0 to the derivation-defined families the mission names (causatives, deverbal nouns, root derivatives), populated entirely by *derived* rules over tables that already exist, and reserve one optional `lexType` slot in the P4 record schema, the Lex-0 pilot envelope and the megastructure schema. No new human annotation. Cost: about two agent sessions plus one optional field in two schemas before P4 locks.
2. **Leave typing implicit.** Keep the four evidence labels as the only cross-cutting vocabulary; each dictionary's placement of causatives and derivatives stays a fact about that dictionary's microstructure (P4's kāraka apparatus, PWG's four enumeration tiers, MW's inline `Caus.` blocks), and any cross-dictionary comparison of a type is assembled ad hoc per paper. Cost: zero now; a schema migration, a Lex-0 re-pin and a re-export of the published P4 samples later, if a register is wanted after P4 is out, estimated at three to four sessions and a published-schema change.

## What a register would contain

Apresyan himself says a full inventory of types for a whole language is "scarcely possible" and begins by sector ([Systematic Lexicography](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Systematic%20Lexicography.md), ch. 3 §1; the LT definition is at ch. 10 §1). The register proposed here is therefore not a semantic taxonomy of the Sanskrit lexicon. It is a short vocabulary of **formally defined** types, each with a membership rule that an existing observed marker satisfies, a grid of fields every member must be described on, and the table that populates it. Version 0 has twelve rows.

| Type id | Membership rule (observed marker) | Grid every member is described on | Populated from (existing table) | Label |
|---|---|---|---|---|
| `verb.causative` | verbal lexeme carrying a `Caus.` sub-block in MW / PWG / AP90 / GRA, or a vidyut ṇic derivation | base root (Whitney anchor), class and pada, valency shift, own senses vs inherited senses, placement per dictionary (nested / own headword / absent), citation | csl-orig txt inline marks; `derivation_status.tsv` | derived |
| `verb.desiderative` | `Desid.` sub-block or vidyut san derivation | same grid | same | derived |
| `verb.intensive` | `Intens.` sub-block or vidyut yaṅ derivation | same grid | same | derived |
| `verb.denominative` | `Nom.` sub-block or vidyut denominative | same grid | same | derived |
| `noun.action` | indigenous `bhāve` kāraka, or WIL/MW affix group "Action / result noun" | root, affix (SLP1 and Pāṇinian name), kāraka, gender, own headword or not, definition class (WS2.4 rubric) | `karaka_distribution.csv`, `group_distribution.csv`, `mw_etymology.tsv` | derived |
| `noun.agent` | `kartari` kāraka, or affix group "Agent" | same grid | same | derived |
| `noun.instrument` | `karaṇe` kāraka | same grid | same | derived |
| `noun.locus` | `adhikaraṇe` kāraka | same grid | same | derived |
| `noun.object` | `karmaṇi` kāraka | same grid | same | derived |
| `noun.abstract` | affix group "Abstract quality" (-tā, -tva) | same grid | same | derived |
| `root.zero-derivative` | affix group "Bare root / zero affix" (kvip and kin) | root, attested forms, own headword or not, per-dictionary placement | `group_distribution.csv`, Whitney | derived |
| `participle.headword` | kta / ktavatu / śatṛ form entered as its own headword | root, affix, per-dictionary placement (this is the lemmatization-policy join) | H5332 census output | derived |

Two rules keep the register controlled. A type is admitted only if its membership rule names an observed marker or a reproducible derivation, so every assignment can carry `derived`, never `inferred`. Semantic types in Apresyan's sense (statives, factives, the vocabulary of emotion) are out of scope for version 0; they would need human annotation and are the reason the register must stay small.

## What typing already exists, implicitly, in five disjoint layers

The register would not create typing. It would name and join typing that five layers already do with five vocabularies that never meet.

| Layer | What it types | Live count (24-09-2026) | Vocabulary it uses |
|---|---|---|---|
| European dictionaries, inline | causative, desiderative, intensive as sub-blocks inside the root article, never as headwords | MW 286,525 records: `Caus.` 2,989 · `Desid.` 918 · `Intens.` 602. PWG 123,366: 3,657 · 757 · 440. AP90 34,882: 871 · 146 · 0. GRA 12,785: 658 · 129 · 223. Zero `<H2>`-style nested headwords in any of the four txt files | Latin abbreviations, per dictionary |
| MW derivation extractor | root vs affix vs prefix per `parse=` member; root class and Whitney anchor | `mw_roots.tsv` 2,113 roots (1,363 `root`, 750 `genuineroot`); `mw_etymology.tsv` 9,377 rows | root / affix / prefix |
| Indigenous apparatus (SKD, VCP, Apte, AP, SHS, KRM) | kāraka of the derivative, plus affix | `bhāve` 1,010 / 1,975 / 206 / 202 / 178 / 30 · `kartari` 291 / 516 / 56 / 61 / 39 / 227 · `karmaṇi` 445 / 409 / 0 / 0 / 1 / 0 · `karaṇe` 341 / 709 / 67 / 73 / 38 / 26 · `adhikaraṇe` 109 / 5 / 0 / 0 / 1 / 19 | Pāṇinian kāraka + pratyaya |
| WIL and Sanskrit-side affix groups | semantic-functional group of the affix | "Action / result noun": WIL 2,138 · SKD 1,219 · VCP 1,968; "Agent": WIL 2,484 · SKD 259 · VCP 449; "Bare root / zero affix": WIL 221 · SKD 60 · VCP 107 | English group names |
| vidyut-prakriya harness | which grammatical cell derives each attested form | `derivation_status.tsv` 401,368 rows; grammar-lab gaps: 4 of 14 exemplar roots are total failures across 6 of 32 topics | Pāṇinian cells |

Two further facts constrain the decision. The PWG four-enumeration-tier rule affects 28.02 % of the pwg_ru store ([pwg-lane-invariants](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/pwg-lane-invariants.md)), which is how much of one dictionary's microstructure hinges on a placement convention no other dictionary shares. And cross-dictionary affix agreement in the indigenous layer is 90 to 100 % (SKD↔VCP 94 %, Apte↔AP 100 %, VCP↔SHS 98 %, per [etymology_stats/README.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/README.md)), so a join across that layer is cheap and reliable; Wilson is the outlier at 23 % against SKD.

## Costs, side by side

| | Adopt a minimal register now | Leave typing implicit |
|---|---|---|
| Before P4 locks | one vocabulary file + validator in csl-atlas (mirrors the evidence-labels pattern); one backfill run assigning types by rule over the five tables above, with a coverage report; one optional field in the P4 record schema, the Lex-0 pilot envelope (H5320) and the megastructure schema (H5324). About two agent sessions | nothing |
| Annotation | none in version 0; every assignment is `derived` | none |
| Risk taken | the twelve rows are wrong or too coarse and must be revised; mitigated because the register is a vocabulary file with a version, like the evidence labels | P4 publishes a schema without the slot; retrofitting after publication means a schema version bump, a Lex-0 re-pin and re-exporting the published SKD sample. Three to four sessions, plus the published-artifact churn |
| What stays free either way | any paper can still compute a type on the fly from the five tables | same |

## What P4 gains or loses

P4's thesis is that marker absence in SKD and VCP is not content absence. The indigenous apparatus marks derivation type explicitly (kāraka plus pratyaya) where the European dictionaries mark it inline with a Latin abbreviation and where MW marks it in a `parse=` attribute. With a register, P4 gets one cross-tradition table per type: how SKD, VCP, MW and PWG each encode the same causative or action noun, on one grid, with counts, which is a paper-grade figure that today has to be assembled by hand from four vocabularies. Without a register, P4 loses nothing in its own argument, since the kāraka apparatus is a component of its record either way; it loses the comparison figure and it publishes a schema that has no place to put a type later. The slot must be optional so that P4's schema is not blocked on the register's readiness.

## What the definition-typology work gains or loses

The WS2.4 rubric classifies 1,496,157 records across 44 dictionaries into four definition classes ([DEFINITION_TYPOLOGY_WS2_4_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md)), and H5330 is drawing the double-keyed 300 × 7 pool now. A type register lets the pool be stratified by lexicographic type at draw time, so the paper can ask whether causatives and action nouns are defined by equivalent more often than by encyclopedic prose. Because every type assignment is derived by rule, the same join can be made after the fact on an already-drawn sample; the definition-typology work therefore gains a stratum if the register exists first and loses only convenience if it does not. The lemmatization-policy census (H5332) is the closer dependency: its unit of measurement (how verbs, nominal stems, compounds and derivatives are entered per dictionary) is exactly the `placement per dictionary` grid field above, so the register and the census should share one vocabulary rather than mint two.

## Recommendation

**Adopt the minimal register now: a twelve-row, derivation-only, rule-populated vocabulary file parallel to the evidence labels, and one optional `lexType` slot in the P4, Lex-0 and megastructure schemas before P4 locks; no semantic types and no human annotation in version 0.**

What would reverse it, any one of these:

1. H5332 finds that the seven dictionaries agree on the placement of derivatives in more than 90 % of the sample, which would make the type redundant with a per-dictionary policy statement.
2. The Lex-0 pilot schema (H5320) cannot carry an optional field without breaking its pinned validation, so the slot would cost a schema version before it earns one.
3. The backfill run shows that fewer than about 80 % of the register's rows can be populated from the five tables by rule, which would mean the register needs annotation to be useful and its cost is no longer two sessions.

## The concrete act

Reply in this chat, in words: adopt the minimal register now, or leave typing implicit until after P4. If adopted, the two follow-on units are minted the same pass: the vocabulary file and validator in csl-atlas, and the rule-based backfill with a coverage report over the five tables. The GTD card carrying this brief is the `@DECIDE` row minted by H5335 in [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).

## Sources and probes

1. Apresyan, *Systematic Lexicography* (OUP 2000, tr. Windle), local text [Systematic Lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/Systematic%20Lexicography.md): LT definition and the four principles (ch. 10 §1); the "scarcely possible to offer an inventory" sector strategy (ch. 3 §1).
2. Roadmap seed and the Apresyan ↔ ACL crosswalk: [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md), § Methodological lineage (H942).
3. Evidence-label vocabulary the register would sit next to: [csl-atlas docs/EVIDENCE_LABELS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md). The PROV-O crosswalk (H5301) was not yet on csl-atlas `origin/main` at probe time (24-09-2026, `git ls-tree origin/main docs/` shows only `EVIDENCE_LABELS.md`).
4. Inline causative counts: `grep -o -i 'Caus\.' v02/<dict>/<dict>.txt | wc -l` over the local `csl-orig` clone, records by `grep -c '^<L>'`; the counts are string occurrences, not entries, and are an upper bound on marked causatives.
5. MW derivation tables: [csl-orig v02/mw/README_etymology.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/README_etymology.md), `mw_roots.tsv`, `mw_etymology.tsv` (row counts by `wc -l` minus header).
6. Indigenous kāraka and affix-group tables: [csl-orig v02/etymology_stats/](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/README.md), `karaka_distribution.csv`, `group_distribution.csv`.
7. vidyut derivation harness and gaps: [kosha datasets manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json), ids `panini-derivation-status` (401,368 rows) and `grammar-lab-derivation-gaps` (H4795).
8. PWG four-tier store impact: [docs/agents/pwg-lane-invariants.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/pwg-lane-invariants.md) (H3948, 28.02 %).
9. Sibling units whose schemas the slot touches: [H5320](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5320-OxAlpha_csl-standards_lex0-pilot-schema-validation-ci_23.09.26.md) Lex-0 pilot schema · [H5321](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5321-Opus_csl-standards_lex0-skd-indigenous-sample-export_23.09.26.md) SKD Lex-0 sample · [H5324](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5324-Opus_csl-atlas_megastructure-catalogue-schema-pilot-skd-mw_23.09.26.md) megastructure schema · [H5330](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5330-OxAlpha_SanskritLexicography_definition-typology-300x7-double-key-sheets_23.09.26.md) definition-typology pool · [H5332](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5332-Opus_csl-atlas_lemmatization-policy-census-seven-dicts_23.09.26.md) lemmatization census · [H5327](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5327-Opus_Uprava_p4-venue-decision-brief-ijl-vs-wsc2027_23.09.26.md) P4 venue brief.

_Гасунс_
