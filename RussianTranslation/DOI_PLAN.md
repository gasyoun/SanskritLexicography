# DOI Plan

The immutable edition cut is prepared locally under `release/edition_vN/`.

Before DOI registration:

1. Validate the assembled export, interoperable exports, review status, gold labels, and release manifest.
2. Upload the exact `release/edition_vN/` directory to the archival repository.
3. Register the DOI against that immutable directory and update `CITATION.cff` with the DOI and final version.
4. Keep the generated `release_manifest.json` with SHA256 checksums as the audit record.

## Structured grammar dataset — a separately archivable FAIR package

The nominal grammar layer ships its own Frictionless descriptor
[`src/datapackage.json`](src/datapackage.json) (CC-BY-SA-4.0) over `headword_index.tsv`,
`reverse_paradigm_index.json`, `paradigm_stats.tsv`, `mw_compounds.json`, `whitney_grammar.json`.
It is **independent of the translation edition** (the A/B kept grammar out of translation), so it
can be archived/DOI-registered on its own track — rebuild deterministically with
`python src/reverse_index.py --build` (provenance: read-only `csl-orig/v02/pwg/pwg.txt` + `mw.txt`).

## Curated Sanskrit-to-Russian terminology — separate DOI track

MG ruled on 04-07-2026 that curated Sanskrit-to-Russian terminology is **not** a subsection of
the PWG translation-memory artifact. It has its own release lane under
[`release/sa_ru_terminology/`](release/sa_ru_terminology/) and should receive its own DOI once
non-empty curated terms pass review. PWG TM suggestion rows should cite terminology `term_id` /
`source_hash` values rather than embedding the terminology dataset wholesale.
