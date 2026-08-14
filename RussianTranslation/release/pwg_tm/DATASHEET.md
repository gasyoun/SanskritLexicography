# Datasheet — PWG TM canonical v1 four-format pack

_Created: 14-08-2026 · Last updated: 14-08-2026 (DOI minted)_

Filled from the
[csl-observatory DATASHEET_TEMPLATE](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET_TEMPLATE.md)
for release `pwg-tm-canonical-v1.0.0`. Sibling of
[TRANSLATION_MEMORY_DATASHEET.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md)
(H215 Sa→Ru corpus TM). This sheet covers **only** the 2,392-record PWG
German→Russian publication TM.

## Motivation

- **Purpose.** Make the migrated canonical scholarly JSONL citable as
  interchange: TMX 1.4b, TEI Lex-0, OntoLex-Lemon/vartrans/PROV-O, with a
  zero-loss field ledger.
- **Who created it.** Mārcis Gasūns (Sanskrit Lexicon project). Exporters are
  deterministic (Grok 4.6 `grok-4.6`, H2685). Underlying cards were machine
  translated (Claude Sonnet family) and migrated losslessly (H2683).
- **Funding.** No external grant.

## Composition

- **Instances.** One publication record = one PWG headword card or exact
  fragment: German source string, Russian rendering, stable IDs, provenance,
  rights, supersession.
- **Count.** 2,392 (2,175 exact-card + 217 exact-fragment). 953 TEI/OntoLex
  entries after grouping by `entry_id`.
- **Encoding.** SLP1 + IAST locators; German and Russian as UTF-8 with PWG
  markup (`<ls>`, `{#…#}`, `{%…%}`) preserved.
- **Is this a sample?** Yes of PWG as a dictionary (2.2% of 98,639 indexed
  headwords). No of the current publication TM (100% of 2,392).
- **Missing / withheld.** Wave-1 655,332 promoted fragments are withheld from
  this green pack because the independent 400-row gate failed the serious-error
  floor (2.5% > 1%). Coverage is in [coverage.json](coverage.json).
- **Sensitive data.** None. No reviewer names, emails, or student records.

## Collection process

- **Source edition.** Böhtlingk–Roth, *Sanskrit-Wörterbuch* (PWG), St.
  Petersburg 1855–1875, via Cologne `csl-orig` (read-only).
- **How obtained.** Existing publication JSONL
  (`release/translation_memory/translation_memory.ru.publication.jsonl`)
  wrapped by
  [`pwg_tm_migrate_v1.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_migrate_v1.py)
  without changing source/Russian strings or hashes.
- **Who collected.** Project pipeline; no crowd annotators on this pack.
- **Timeframe.** Publication TM harvested 2026; canonical wrap 13-08-2026;
  interchange export 14-08-2026.

## Preprocessing / known gaps

- 1,153 records have `sense_alignment=unresolved` (multi-sense cards). That
  is preserved, not invented.
- Some Russian targets equal the German (e.g. `<ab>dass.</ab>`). That is
  attested identity, not a drop.
- Label quality of the 2,392 is `legacy_promoted` / `machine_exact`, not a
  human gold cut.

## Uses

- **Intended.** Scholarly reuse, CAT/TM interchange, LLOD federation on the
  `https://w3id.org/sanskrit-lexicon/repwg/tm/` spine, audit of the canonical
  store.
- **Not intended.** Do not treat Wave-1 5,000-key drafts as published green
  data. Do not treat this pack as a complete PWG.

## Distribution

- **Licence.** CC BY 4.0 for the pack; PWG source Public Domain Mark 1.0.
  See [LICENSE-DATA](LICENSE-DATA).
- **How to get it.** GitHub Release `pwg-tm-canonical-v1.0.0` on
  [gasyoun/SanskritLexicography](https://github.com/gasyoun/SanskritLexicography).
  Rebuild locally with `python src/pwg_tm_release.py`.
- **DOI.** Concept [10.5281/zenodo.21932900](https://doi.org/10.5281/zenodo.21932900)
  (cite this). Version 1.0.0
  [10.5281/zenodo.21932901](https://doi.org/10.5281/zenodo.21932901).
  Verified 14-08-2026: both resolve to this pack (title + 12 files, including
  the four interchange files at the frozen byte sizes). Distinct from the
  repository software DOI [10.5281/zenodo.21306715](https://doi.org/10.5281/zenodo.21306715).
- **Maintenance.** RussianTranslation pipeline; issues on the repo.

_Dr. Mārcis Gasūns_
