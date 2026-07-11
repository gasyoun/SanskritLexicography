# SanskritLexicography

_Created: 09-07-2026 · Last updated: 11-07-2026_

A **data and research workspace** for Sanskrit digital lexicography — not a
software project. Its focus is Cologne Digital Sanskrit Lexicon headword lists,
cross-dictionary comparison, AI-assisted Russian translations of the dictionaries,
and teaching material for Sanskrit lexical and syntactic study.

The repository is part of the wider
[Sanskrit Lexicon](https://github.com/sanskrit-lexicon) ecosystem. It collects
large reference files, headword exports, research notes, translation pipelines,
and lecture material that support work on dictionary structure, corpus alignment,
and learner-facing lexicographic tools. Some Python tooling now lives under
[RussianTranslation/src/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src),
so the repo is hybrid in practice — but the content, not the code, is the point.

For a capability inventory (what dictionaries, interfaces, datasets, and tools
actually exist across the ecosystem, each with a stable ID and a real example),
see [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md).

## Contents

| Path | Purpose |
|---|---|
| [HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) | Exported and derived headword lists for CDSL dictionaries (MW, PWG, PWK, AP, BHS, CAE, CCS, SCH, SKD, VCP, VEI, and more), aggregate comparison files, and the external [Catalan-Pujol/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/Catalan-Pujol) Sanskrit–Catalan wordlist + CDSL-coverage analysis. |
| [RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) | Two independent AI translation pipelines: `mw_ru` (Monier-Williams → Russian) and `pwg_ru` (PWG/Böhtlingk-Roth → Russian/English), plus their prompts, audits, and reference-shelf harvests. See the pipeline pointers below. |
| [Syntax-Lectures/](https://github.com/gasyoun/SanskritLexicography/tree/master/Syntax-Lectures) | Markdown and HTML lecture material (mostly Russian) on Sanskrit particles and syntax, including the interactive [particle explorer](https://github.com/gasyoun/SanskritLexicography/blob/master/Syntax-Lectures/sanskrit_particles_explorer.html). |
| [literature/md/](https://github.com/gasyoun/SanskritLexicography/tree/master/literature/md) | Full-text markdown extractions of the research literature collection. See [literature/md/INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/INDEX.md) for the cross-repo relevance map (sources tagged by which dictionary repo, corpus pipeline, or paper they serve). PDFs are not versioned; only the markdown index is tracked. |
| [ROADMAP_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_2026_2027.md) | Research roadmap covering csl-atlas review, publication plans, FAIR gaps, standards exports, and learner-layer work. |
| [REFERENCES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/REFERENCES.md) | Provenance (source, date, producer, size) for the large reference assets — `CDSL-2025.pdf`, `DCS_statistical_evaluation.htm`, `DCS-Moniers-roots-w-references.html`, `helpmorphids.html`, `gasuns_cologne-zograf_2019.pdf`, and others. |

## Documentation map

Where to read what.

**Orientation**

- [README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/README.md) — this file: overview and entry points.
- [ROADMAP_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_2026_2027.md) — research direction, publication plan, FAIR/standards gaps.
- [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) — capability inventory (what exists across the ecosystem, with stable IDs).
- [changelog.md](https://github.com/gasyoun/SanskritLexicography/blob/master/changelog.md) — what changed, by dated snapshot.

**Manuals (by audience)** — deep, standalone guides in
[docs/manuals/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals)
([router](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md)):

- [MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md)
  — operating/extending the repo (conventions, the pipelines, the epistemic
  registries). English.
- [RESEARCHER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md)
  — the evidence-graded thesis, paper pipeline, what's citable. English.
- [STUDENT_MANUAL_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/STUDENT_MANUAL_RU.md)
  — teaching material and what's usable today. Русский.
- [DATA_REUSE_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md)
  — dataset formats, encodings, traps, rights. English.

**Contributors & agents**

- [CONTRIBUTING.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRIBUTING.md) — how to contribute.
- [CLAUDE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) — repo conventions for Claude Code (key1/key2, BOM caveat, external-refs-as-plain-text); defers ecosystem/taxonomy to the org-level CLAUDE.md one directory up.
- [HANDOFF.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HANDOFF.md) — orientation for the next agent continuing documentation work: conventions, link-sweep recipes, open gaps.
- [CODE_OF_CONDUCT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CODE_OF_CONDUCT.md) — community expectations.

**Epistemic registries** — the acts a FINDINGS log can't hold (relying,
disagreeing, not-yet-knowing, abandoning, reproducing, decaying, defining):
[FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) ·
[ASSUMPTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) ·
[CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) ·
[GAPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) ·
[DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) ·
[RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) ·
[STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md) ·
[GLOSSARY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md).

**Material, by area**

- [HeadwordLists/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/README.md) — headword exports: naming, key1/key2, encoding, the dictionary-code table.
- [Syntax-Lectures/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Syntax-Lectures/README.md) — particle lectures, Zaliznyak schema, interactive explorer, Apte entries.
- [RussianTranslation/mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md) — how the AI Russian Monier-Williams translation was made (+ the stage prompts in [RussianTranslation/mw_ru_prompts/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru_prompts/README.md)).
- [RussianTranslation/PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) — chronological orientation for the `pwg_ru` PWG→RU/EN pipeline (major fixes, recurring failure patterns, current state); read before touching pwg_ru code.
- [RussianTranslation/NWS_AUDIT_REPORT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NWS_AUDIT_REPORT.md) — living cumulative report of the NWS attribution-parser audit (per-section roll-up, real-loss taxonomy, source errata).
- [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md) — how a PWG entry is assembled from up to 5 dictionary layers (PWG/PW/SCH/PWKVN/NWS), the fixed merge order in `dict_merge.py`, and a measured co-occurrence tally showing no-PWG combinations (esp. PW-only) are common, not edge cases.
- [RussianTranslation/LITERATURE_FOR_PWG_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LITERATURE_FOR_PWG_RU.md) — the reference-shelf harvest for the Sanskrit→Russian PWG translation, mined by pipeline insertion point; with the per-manual audit [RussianTranslation/MANUALS_FOR_PWG_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/MANUALS_FOR_PWG_RU.md) and the five-manual theory deep-dive [RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md).
- [REFERENCES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/REFERENCES.md) — provenance for the large reference assets.
- [literature/md/INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/INDEX.md) — cross-repo relevance map for the research literature collection.

## Headword lists

The files in [HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists)
are named to show both the dictionary/source and the kind of key exported. For
example: `MW-unique-key1-193978.txt`, `MW-unique-key2-198220.txt`,
`PWK-unique-key2-133741.txt`, `SCH-accents-IAST-20247.txt`,
`mw-apte-mcdonell-hk.txt`, `sanhw1.xlsx`. The trailing number usually records
the entry count in that export.

### key1 and key2

- `key1` is a normalized computational key. It may not exist as a form printed
  in the source dictionary, but it is useful for machine comparison — matching,
  deduplication, joining.
- `key2` is closer to the original printed form (retains `-`, `--`, `/` accent
  marks) and is generally the better key for display, citation, and
  philological inspection — editorial review, citation, checking the digitized
  text against the printed source.

The full naming/encoding conventions (including the BOM caveat — some exports
carry a UTF-8 BOM and some do not) live in
[HeadwordLists/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/README.md).

## Russian translation pipelines

[RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation)
holds two independent, high-traffic AI translation efforts:

- **`mw_ru`** — a multi-pass, multi-model AI Russian translation of
  Monier-Williams (translate → two independent QA judges → re-translate of
  rejects). Only English "wrapper" prose is translated; Sanskrit, grammar
  abbreviations, and source references are deliberately left untouched. See
  [RussianTranslation/mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md).
- **`pwg_ru`** — a separate PWG (Böhtlingk-Roth) → Russian (primary) and English
  (secondary) pipeline, run headword-by-headword at scale. Start at
  [RussianTranslation/PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
  for orientation before touching any pwg_ru code.

## Research directions

The current roadmap frames the work around evidence-graded digital lexicography:

- dictionary evidence should be reproducible and citable;
- inferred, derived, observed, and reviewed claims should be kept distinct;
- Sanskrit's European and indigenous lexicographic traditions should be modeled
  as parallel evidence systems rather than flattened into one format;
- learner-facing tools should connect dictionary evidence with corpus frequency
  and grammatical information.

See [ROADMAP_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_2026_2027.md)
for the publication plan, FAIR/standards gaps, and proposed learner-layer work.

## Working with the data

Most files are plain text and can be inspected with standard command-line tools
or loaded into scripts. A few files are large enough to be awkward in an editor
— especially `sanhw1.xlsx`, `DCS_statistical_evaluation.htm`, and the PWG/PWK
error-list exports — so use streaming/CLI tools on those. All files are UTF-8;
BOM state is inconsistent across exports, so check before transforming and
preserve the existing state on write.

Suggested entry points:

1. `HeadwordLists/*unique-key1*.txt` for normalized matching tasks.
2. `HeadwordLists/*unique-key2*.txt` for print-form and display tasks.
3. [HeadwordLists/mw-apte-mcdonell-hk.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw-apte-mcdonell-hk.txt) for a ready-made comparison across major Sanskrit dictionary traditions.
4. [Syntax-Lectures/sanskrit_particles_lectures.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Syntax-Lectures/sanskrit_particles_lectures.md) as the main teaching note for the particles material, and [Syntax-Lectures/sanskrit_particles_explorer.html](https://github.com/gasyoun/SanskritLexicography/blob/master/Syntax-Lectures/sanskrit_particles_explorer.html) in a browser for the interactive, student-facing version.
5. [ROADMAP_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_2026_2027.md) to understand how this repository connects with csl-atlas, VisualDCS, csl-standards, and publication work.

## Contributing

Contributions should follow
[CONTRIBUTING.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRIBUTING.md).
In short: fork, create a feature branch, submit a pull request referencing any
related issue. For larger data changes, include the source of the data, the
transformation method, and enough counts or checksums for another maintainer to
reproduce the result.

## License

Distributed under the MIT License. See
[LICENSE](https://github.com/gasyoun/SanskritLexicography/blob/master/LICENSE).

_Dr. Mārcis Gasūns_
