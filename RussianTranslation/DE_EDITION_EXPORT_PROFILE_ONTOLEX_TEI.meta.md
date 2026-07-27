# DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md — metadoc

_Created: 26-07-2026 · Last updated: 26-07-2026_

Companion record for
[DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md).

## Purpose & audience

The mapping contract for the German edition graph's FAIR serialization: which
store/portrait field becomes which OntoLex-Lemon predicate and which TEI Lex-0
element, who produced it, and what a consumer must not trust. Audience: DH
consumers of the exported graph, `csl-standards` (which owns the *published*
TEI/OntoLex modelling), and any agent extending
[`export_de_edition.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py).

Read it **before** adding a field to the exporter — the profile's whole value is
that every emitted triple/element has a named producer and a stated reliability.

## Provenance

| Field | Value |
|---|---|
| Handoff | [H1629](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1629-Opus_SanskritLexicography_pwg-de-graph-ontolex-tei-export_25.07.26.md) |
| Parent | [H1624](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md) G1–G6 |
| Model | Opus 5 (`claude-opus-5[1m]`) |
| Date | 26-07-2026 |
| Prior art surveyed | `export_lod.py de-lexicon` (H772), `export_interop.py tei`, [H1495 routing contract](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1495-Sonnet_csl-observatory_obs-t-ontolex-tei-routing-contract_22.07.26.md) |

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Generator + golden fixture + selftest | **done** H1629 |
| 2 | Field mapping table with per-field producer | **done** H1629 |
| 3 | Rights fence (allowlist + quarantine + post-serialization guard) | **done** H1629 |
| 4 | Validate the TEI against the actual Lex-0 RNG/ODD | open — needs the schema; currently structure-checked only |
| 5 | Validate the Turtle with a real RDF parser + SHACL (`release/shapes.ttl`) | open — emitter is string-based, never parsed back |
| 6 | Full-store run + scale/coverage report (fixture is 22 rows) | open |
| 7 | Resolve the base-IRI `@DECIDE` before anything is published | **done** 27-07-2026 — ruled `…/repwg/` ([#809](https://github.com/gasyoun/SanskritLexicography/issues/809)) |
| 7a | Register the w3id PURL so the IRIs actually resolve | open — until then they are permanent identifiers that 404 |
| 7b | Emit `dct:creator` / `dct:publisher` on the lexicons | open — currently only source/license/wasGeneratedBy/created |
| 8 | Re-export once the G1 `gloss_lang` false-positive rate is fixed | open (blocked on the classifier issue) |
| 9 | Hand the *published* graph + SPARQL surface to `csl-standards` | open — boundary rule, not this repo's job |
| 10 | Couple with [H1635](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1635-Opus_SanskritLexicography_pwg-public-sidecar-zenodo-release_25.07.26.md) Zenodo packaging if the export becomes the package input | open |

## Known limitations

- Conformance to TEI Lex-0 is **structurally checked, not certified** — no ODD
  validation was run (backlog #4).
- The Turtle is emitted as text and never round-tripped through an RDF parser,
  so a syntax defect would only surface downstream (backlog #5).
- Every count in the document is from the 22-row golden fixture, not a
  full-store run; the store-wide numbers quoted in §5 (contamination, gloss_lang
  census) are measured, but the export itself has not been run at scale.
- The `gloss_lang` false-positive measurement uses a heuristic German detector,
  so the 53% figure is a proxy — the direction is certain (the sampled examples
  are unmistakably German), the exact rate is ±.

## Related documents

- [pwg_ru.md §8](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) — German-layers inventory
- [EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md)
- [LOD_GRAPH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LOD_GRAPH.md)
- [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)

## Revision history

| Date | Change |
|---|---|
| 26-07-2026 | Initial profile: generator, golden fixture, mapping table, rights fence, limitations |

_Dr. Mārcis Gasūns_
