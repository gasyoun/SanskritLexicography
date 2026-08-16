# PWG DE edition graph — OntoLex-Lemon + TEI Lex-0 sidecars

_Created: 16-08-2026 · Last updated: 16-08-2026_

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21961709.svg)](https://doi.org/10.5281/zenodo.21961709)

The **German** side of the Petersburger Wörterbuch edition graph, serialized for
FAIR reuse. This pack is the citable form of the H1629 export profile; the
structural layers it carries were built by H1624 G1–G6.

**This dataset carries no translation, no review score and no evidence grade.**
The project's Russian translation store is excluded by a hard field allowlist at
read time and a post-serialization byte fence — see [Rights and scope](#rights-and-scope).

## What is in the deposit

| File | Size | Format |
|---|---:|---|
| `pwg_de_edition.ttl` | 26.5 MB | OntoLex-Lemon, Turtle |
| `pwg_de_edition.tei.xml` | 19.8 MB | TEI Lex-0, XML |
| `pwg_de_edition.manifest.json` | 18 KB | build manifest, incl. the quarantine ledger |

The two large artifacts are **deposit files and GitHub release assets, not
repository files**. This directory keeps the recipe, the datasheet and the
hashes so a download can be verified without a 46 MB rebuild:

```
sha256sum -c SHA256SUMS
```

## Coverage

459 lexical entries / 11,581 edition senses, drawn from five editions:

| Layer | Senses | Edition |
|---|---:|---|
| `pwg` | 5,573 | Böhtlingk–Roth, *Sanskrit-Wörterbuch* (1855–1875) |
| `pw` | 5,204 | Böhtlingk, kürzere Fassung (1879–1889) |
| `nws` | 432 | Nachtragswörterbuch (Cologne working layer) |
| `sch` | 210 | Schmidt, *Nachträge* (1928) |
| `pwkvn` | 162 | Nachträge to the kürzere Fassung |

Each sense carries the structural layers recomputed from the German string:

| Layer | Instances | Carried as |
|---|---:|---|
| citation edges | 40,700 | `pwglex:Citation` / TEI `cit`+`bibl` |
| edition relations | 6,008 | `vartrans:SenseRelation` / TEI `xr` |
| government | 2,125 | `pwglex:Government` / TEI `gramGrp` |
| non-German gloss spans | 86 | `pwglex:glossSpan` / TEI `gloss` |
| form notes | 42 | `pwglex:FormNote` / TEI `gram` |

Gloss spans are recorded **only** where the span is not German — the Latin cues,
botanical binomials and Wilson's English renderings a consumer must not read as
German. German spans are the unmarked default and are not enumerated.

## Rebuilding

The export is deterministic given the same store and `--generated-at`:

```
python src/export_de_edition.py --selftest
python src/export_de_edition.py export \
    --store src/pwg_ru_translated.jsonl \
    --out-dir <artifacts> --generated-at 2026-08-16
python src/build_de_sidecar_pack.py build --art-dir <artifacts> --version v1.0.0
```

The store (`src/pwg_ru_translated.jsonl`) is gitignored and is not redistributed:
it holds the Russian translation and its review state. Rebuilding therefore
reproduces the artifacts only inside the project. For everyone else the deposit
files **are** the data, which is why they are hashed here.

## Honest limitations

- **Coverage is the translated store's coverage, not all of PWG.** 459 headwords
  is the slice that has passed through the pwg_ru pipeline, selected by DCS
  attestation and frequency — it is not a random sample of the dictionary, and
  frequency-ranked headwords are longer and more polysemous than average.
- **22 senses are quarantined, not exported.** Their German fields contain
  Cyrillic, i.e. the source row is corrupted by RU-into-DE contamination. They
  are listed in `manifest.json` under `quarantined` so the defect is countable
  rather than invisible.
- **110 sense labels were reduced to an ASCII skeleton** (`sanitized_tag_rows`).
  Their German survives intact; only the structural label was scrubbed, and the
  scrub is marked `[ru elided]` in `rdfs:comment` / `@relEvidence`.
- **`edition_rel` is machine classification, not adjudicated editorial fact.**
  H1624 G6 measured 4,226 / 39,539 (10.69%) derivation conflicts between layers;
  those carry a `needs_human` flag and were deliberately not auto-resolved.
- **Citation resolution is partial.** `resolver_status` on each citation edge
  says whether the `ls` reference resolved to a work id; orphans are reported,
  not silently dropped.

## Rights and scope

PWG, PW, SCH and PWKVN are 19th–early-20th-century German editions in the
**public domain**. NWS (432 senses, 3.7%) is the Cologne *Nachtragswörterbuch*
working layer and is redistributed here as part of the edition graph. The
derived structure — the layers tabulated above — is the authors' own work and is
released under **CC-BY-SA-4.0**; see [`LICENSE-DATA`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_de_sidecars/LICENSE-DATA).

Full datasheet: [`DATASHEET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_de_sidecars/DATASHEET.md).
Field-by-field mapping: [`DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md).

## Citing

See [`CITATION.cff`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_de_sidecars/CITATION.cff).
Cite the concept DOI unless you need to pin one version.

| | |
|---|---|
| Concept DOI (cite this) | [10.5281/zenodo.21961709](https://doi.org/10.5281/zenodo.21961709) |
| Version DOI (v1.0.0) | [10.5281/zenodo.21961710](https://doi.org/10.5281/zenodo.21961710) |
| GitHub release | [`pwg-de-edition-v1.0.0`](https://github.com/gasyoun/SanskritLexicography/releases/tag/pwg-de-edition-v1.0.0) |

This is a **dataset** record with its own concept DOI. It is deliberately not
the repository's software DOI ([10.5281/zenodo.21306715](https://doi.org/10.5281/zenodo.21306715)),
which describes the codebase — do not cite that one for this data.

_Dr. Mārcis Gasūns_
