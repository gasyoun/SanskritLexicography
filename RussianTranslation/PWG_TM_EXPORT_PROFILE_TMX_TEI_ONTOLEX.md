# PWG TM export profile — TMX 1.4b + TEI Lex-0 + OntoLex

_Created: 14-08-2026 · Last updated: 14-08-2026_

Field mapping for the H2685 Track C exporters. Canonical store:
[`schemas/pwg_tm_canonical.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_tm_canonical.schema.json).
Generators:
[`src/pwg_tm_export_core.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_export_core.py),
[`src/build_tmx.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py)
`build-canonical`,
[`src/export_pwg_tm_tei.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_pwg_tm_tei.py),
[`src/export_pwg_tm_ontolex.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_pwg_tm_ontolex.py),
[`src/pwg_tm_export_loss.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_export_loss.py).

This is **not** a replacement for the DE-only edition graph
([DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md))
or the Sa→Ru corpus TMX ([BUILD_TMX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/BUILD_TMX.md)).

## First-class vs extension

| Path | TMX 1.4b | TEI Lex-0 | OntoLex |
|---|---|---|---|
| `source_string` | `<tuv xml:lang="de"><seg>` | `cit[@type=sourceEquivalent]/quote` | `skos:definition@de` |
| `target_string` | `<tuv xml:lang="ru"><seg>` | `cit[@type=translationEquivalent]/quote` | `skos:definition@ru` |
| `record_id` | `tu@tuid` + prop | `idno[@type=record_id]` | `pwglex:recordId` |
| `entry_id` / lemma | props + grouping | `entry/form/orth` | `ontolex:LexicalEntry` + `Form` |
| `fragment_class` | prop | `usg[@type=fragmentClass]` | `pwglex:f_fragment_class` |
| scalars (trust, hashes, locator, rights, …) | `<prop type=path>` | `<note type=path>` | `pwglex:f_<path>` |
| nested objects (provenance, evidence, …) | `scholarly_extension` JSON | same, `format=application/json` | `pwglex:scholarlyExtension` JSON |
| `source_publication` (full nested row) | hash only | hash only | `pwglex:sourcePublicationHash` |

JSONL remains the only complete store. The nested publication payload is
hashed, not dumped into TMX/TEI/RDF. `pwg_tm_export_loss.py` fails if any
ledger path is unaccounted.

OntoLex uses core + `vartrans:Translation` for the DE→RU pair. `lexicog:Entry`
is emitted only when one `entry_id` has more than one record (dictionary-view
order that core cannot express). PROV-O stamps `prov:Activity` /
`prov:SoftwareAgent` / `prov:generatedAtTime` per sense.

IRIs: `https://w3id.org/sanskrit-lexicon/repwg/tm/` (same w3id spine as
[LOD_GRAPH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LOD_GRAPH.md);
not yet registered — do not claim dereferenceability).

_Dr. Mārcis Gasūns_
