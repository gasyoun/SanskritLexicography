# Datasheet — PWG DE edition graph sidecars

_Created: 16-08-2026 · Last updated: 16-08-2026_

Structured after Gebru et al., *Datasheets for Datasets*, and Bender & Friedman,
*Data Statements for NLP*. The companion datasheet for the Russian translation
memory is [`TRANSLATION_MEMORY_DATASHEET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md);
this one deliberately describes the **German-only** artifact.

## Motivation

**Why was this dataset created?** Sanskrit lexicography's largest scholarly
dictionary, the Petersburger Wörterbuch, exists digitally as marked-up text but
not as a queryable *edition graph*: the relationship between a PWG sense, its
abridgement in PW, and the later Nachträge layers is implicit in the markup. This
dataset makes those relationships, and the grammatical/citational structure of
each German sense, explicit and machine-readable in two community standards.

**Who created it?** Mārcis Gasūns (Институт лингвистических исследований РАН),
as part of the Sanskrit Lexicon project.

**Who funded it?** Unfunded; the project is maintained by its author.

## Composition

**What do the instances represent?** Two nested instance types: a *lexical entry*
(a headword with a homonym number) and a *lexical sense* belonging to one edition
layer of that entry. 459 entries, 11,581 senses.

**Is any information missing?** Yes, by construction and by defect:

- The Russian and English translations, review status, reviewer identity,
  evidence grade and corpus gate are **removed** — that is the point of the
  profile, not an omission to be repaired.
- 22 senses are withheld (quarantined) because their German is contaminated with
  Cyrillic; they are enumerated in `manifest.json`.
- 110 sense labels were reduced to an ASCII skeleton for the same reason. The
  German text of those senses is intact.

**Does the dataset contain confidential or personal data?** No. It contains
19th-century lexicographic German, Sanskrit citation forms, and machine-derived
structure. The only proper names are the cited authors and works of the Sanskrit
canon and their 19th-century editors.

**Is it a sample?** Yes, and not a random one. Coverage follows the pwg_ru
pipeline's headword selection, which prioritises DCS-attested and
higher-frequency headwords. High-frequency Sanskrit headwords are systematically
longer, more polysemous and more citation-dense than the dictionary average, so
per-sense counts here should **not** be read as PWG-wide rates.

## Collection

**How was the data acquired?** The German text derives from the Cologne Digital
Sanskrit Dictionaries digitisation of the printed editions. The structural layers
were computed, not collected: each is recomputed from the German string at export
time by the shipped extractor (`government_census`, `form_labels`,
`citation_edges`, `edition_rel`, `pwg_mask`), so the artifact does not depend on
any particular vintage of stored annotation.

**Over what timeframe?** Source editions 1855–1928. Structural layers built
July–August 2026.

**Was there an ethical review process?** Not applicable — no human subjects.

## Preprocessing / cleaning / labelling

Every input row passes a hard field allowlist (`key1`, `iast`, `subcard`,
`sense_tag`, `layer`, `volume`, `page`, `column`, `de`) before any emitter sees
it. Rows whose German-bearing fields carry Cyrillic are quarantined; sense labels
carrying Cyrillic are reduced to their ASCII skeleton and marked `[ru elided]`.
The serialized bytes are then re-checked for Cyrillic and for forbidden field
names, and the export **fails** rather than emitting a suspect artifact.

The store's free-text `h` field is deliberately never read: it carries Russian
disambiguation prose, so consuming it would import a contaminated field for no
structural gain.

**Is the raw data available?** The German source markup is available from the
Cologne project. The project's own store is not redistributed (see Rights).

## Uses

**What is it suitable for?** Querying the PWG edition graph — which senses
restate, abridge or supplement which; what government a sense assigns; what a
sense cites. It supports linked-data joins against corpus frequency data via the
SPARQL queries in [`release/query/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/query).

**What should it NOT be used for?**

- **Not a corpus of PWG.** It is a structured slice, biased toward frequent
  headwords; do not compute dictionary-wide statistics from it.
- **Not adjudicated editorial fact.** `edition_rel` is machine classification.
  The 10.69% inter-layer derivation conflict rate measured under H1624 G6 is
  flagged `needs_human`, not resolved.
- **Not a translation resource.** There is no Russian or English in it.

**Is there anything that might cause harm or unfair treatment?** The German text
is 19th-century scholarly prose and reflects the period's framing of Indian
religion, caste and gender. It is reproduced as a historical document; the
project neither endorses nor silently modernises it.

## Distribution

Deposited on Zenodo as a dataset record with its own concept DOI — deliberately
**not** the repository's software DOI (`10.5281/zenodo.21306715`), which
describes the codebase, not this derived dataset. Also attached to a GitHub
release; the bytes are hash-identical, verifiable against `SHA256SUMS`.

**Licence.** Source editions PWG/PW/SCH/PWKVN are public domain. NWS (432
senses, 3.7%) is the Cologne Nachtragswörterbuch working layer. The derived
structure is the authors' own work, released CC-BY-SA-4.0.

## Maintenance

Maintained by the author in [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography).
The pack is rebuilt by `src/build_de_sidecar_pack.py` from a fresh
`src/export_de_edition.py` run; each release is a new Zenodo version under the
same concept DOI. Errata and coverage growth are expected as the pwg_ru pipeline
extends beyond its current 459 headwords.

_Dr. Mārcis Gasūns_
