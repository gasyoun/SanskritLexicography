# ARCHITECTURE — PWG Translation Memory as a Scholarly Lexicographic Resource

_Created: 13-08-2026 · Last updated: 13-08-2026_

Architecture layer of the [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_tm_dh_lexicography_2026H2.md).

## Component boundary

```text
PWG source (read-only) + corpus/frequency/citation assets
        -> frozen priority queue (5,000 headwords)
        -> portrait/fragment extraction
        -> Grok 4.6 draft
        -> deterministic fidelity and markup gates
        -> canonical scholarly JSONL + append-only provenance/supersession
        -> JSONL | TMX 1.4b | TEI Lex-0 | OntoLex/vartrans/PROV-O
        -> validation + 400-fragment independent adjudication
        -> immutable GitHub + Zenodo release
```

## Canonical record

The canonical JSONL contract is versioned and additive. Each record carries:

- persistent `record_id`, `entry_id`, `sense_id`, `fragment_id` and `fragment_class`;
- PWG source locator, exact source string/hash, language/script/transliteration declarations;
- German source, Russian rendering, structural markup, grammatical and citation context;
- confidence/trust tier, reuse policy, gate status/version, model/prompt/pipeline versions;
- evidence and provenance (PROV-O-compatible agents, activities, entities, timestamps and hashes);
- `supersedes`/`superseded_by`, never destructive replacement;
- rights facts and block-class flags; uncertainty is descriptive metadata, not a release stop;
- export-loss ledger proving every scholarly field maps into each derived format or an explicit extension.

## Fragment model

Fragments are addressable scholarly objects, not substrings without context:

1. `sense` — a complete sense unit and ordering context;
2. `definition_gloss` — reusable definitional translation;
3. `grammar_label` — POS, construction, government, register, inflectional note;
4. `citation` — bibliographic/locus statement and resolution status;
5. `example` — cited Sanskrit example with German/Russian context;
6. `recurring_formula` — repeated lexicographic metalanguage, guarded against sense leakage.

Reuse keys combine normalized content, fragment class, structural context, source/pipeline version, and required fidelity invariants. Approximate retrieval is advisory; automatic reuse requires an exact compatible address and green gate.

## Priority queue

Rank by a documented composite: corpus token frequency, number/diversity of corpus attestations, PWG citation degree, predicted fragment reuse, DCS/lexical-core membership, and a stratification term preventing only easy/common entries from dominating. Freeze inputs, weights, hashes, rank, and exclusion reasons in the wave manifest.

## Interchange mapping

- **TMX 1.4b:** translation-unit interchange; custom properties retain IDs, class, provenance, confidence, source locator, and supersession.
- **TEI Lex-0:** entry/form/sense/cit/quote/gramGrp structure and TEI header with source, encoding, revision and publication metadata.
- **OntoLex-Lemon:** lexical entries/forms/senses; `vartrans:Translation` for translation relations; lexicog only where dictionary ordering/components require it; PROV-O for generation and revision history.
- **JSONL:** lossless canonical source for regeneration and audits.

Every exporter emits a field-coverage ledger. “Schema-valid but silently lossy” is a failure.

## Release architecture

Each release is immutable and content-addressed: data files, schemas, validation receipts, quality report, datasheet, license/rights facts, checksums, citation metadata, and manifest. GitHub provides code and release assets; Zenodo provides the persistent DOI/archive. The DOI is embedded back into metadata/manifests when minted without rewriting prior release bytes: issue a new manifest/release that supersedes the pre-DOI candidate.

## Build versus reuse

Reuse current validators, TM/TMX builders, graders, aligners, schemas, manifests, corpus lexicon, frequency/citation assets, terminology builder, and existing LOD fixtures. New work is limited to the canonical fragment schema/migration, queue, Grok-scale runner, TEI/RDF exporters, loss ledger, independent sample apparatus, and release/PID automation.

_Dr. Mārcis Gasūns_

