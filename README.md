# SanskritLexicography

Research and data workspace for Sanskrit digital lexicography, with a focus on
Cologne Digital Sanskrit Lexicon headword lists, cross-dictionary comparison,
and teaching materials for Sanskrit lexical and syntactic study.

The repository is part of the wider
[Sanskrit Lexicon](https://github.com/sanskrit-lexicon) ecosystem. It collects
large reference files, headword exports, research notes, and lecture material
that support work on dictionary structure, corpus alignment, and learner-facing
lexicographic tools.

## Contents

| Path | Purpose |
|---|---|
| `HeadwordLists/` | Exported and derived headword lists for CDSL dictionaries, including MW, PWG, PWK, AP, BHS, CAE, CCS, SCH, SKD, VCP, VEI, aggregate comparison files, and the external [Catalan-Pujol/](HeadwordLists/Catalan-Pujol/) Sanskrit–Catalan wordlist + CDSL-coverage analysis. |
| `Syntax-Lectures/` | Markdown and HTML lecture material (mostly Russian) on Sanskrit particles and syntax, including the interactive [particle explorer](Syntax-Lectures/sanskrit_particles_explorer.html). |
| `literature/md/` | Full-text markdown extractions of the research literature collection (65 files; 5 still **⚠ blocked** for mining — image-only scans / OCR-noise / un-isolated multi-paper bundles, flagged in the index). See [literature/md/INDEX.md](literature/md/INDEX.md) for the cross-repo relevance map. PDFs are not versioned; only the markdown index is tracked. |
| `ROADMAP_2026_2027.md` | Research roadmap covering csl-atlas review, publication plans, FAIR gaps, standards exports, and learner-layer work. |
| `CDSL-2025.pdf` | Snapshot/reference document for the 2025 CDSL-related work. |
| `DCS_statistical_evaluation.htm` | Statistical evaluation material connected with DCS and Sanskrit lexical data. |
| `DCS-Moniers-roots-w-references.html` | DCS and Monier-Williams root-reference material. |
| `helpmorphids.html` | Morphological identifier reference material. |
| `gasuns_cologne-zograf_2019.pdf` | Supporting publication/reference material. |
| [REFERENCES.md](REFERENCES.md) | Provenance (source, date, producer, size) for the reference assets above, including `WSC 2025 Reviews 7.pdf`. |

## Documentation map

Where to read what.

**Orientation**

- [README.md](README.md) — this file: overview and entry points.
- [ROADMAP_2026_2027.md](ROADMAP_2026_2027.md) — research direction, publication
  plan, FAIR/standards gaps.
- [changelog.md](changelog.md) — what changed, by dated snapshot.

**Contributors & agents**

- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute.
- [CLAUDE.md](CLAUDE.md) — repo conventions for Claude Code (key1/key2, BOM
  caveat, external-refs-as-plain-text); defers ecosystem/taxonomy to the
  org-level [../CLAUDE.md](../CLAUDE.md).
- [HANDOFF.md](HANDOFF.md) — orientation for the next agent continuing
  documentation work: conventions, link-sweep recipes, open gaps.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — community expectations.

**Material, by area**

- [HeadwordLists/README.md](HeadwordLists/README.md) — headword exports: naming,
  key1/key2, encoding, the dictionary-code table.
- [Syntax-Lectures/README.md](Syntax-Lectures/README.md) — particle lectures,
  Zaliznyak schema, interactive explorer, Apte entries.
- [RussianTranslation/mw_ru.md](RussianTranslation/mw_ru.md) — how the AI Russian
  Monier-Williams translation was made (+ the stage prompts in
  [RussianTranslation/mw_ru_prompts/README.md](RussianTranslation/mw_ru_prompts/README.md)).
- [RussianTranslation/NWS_AUDIT_REPORT.md](RussianTranslation/NWS_AUDIT_REPORT.md)
  — living cumulative report of the NWS attribution-parser audit (per-section
  roll-up, real-loss taxonomy, source errata).
- [RussianTranslation/LITERATURE_FOR_PWG_RU.md](RussianTranslation/LITERATURE_FOR_PWG_RU.md)
  — the reference-shelf harvest for the Sanskrit→Russian PWG translation, mined by
  pipeline insertion point (glossary, translator prompt, QA judge, corpus gate,
  display); with the per-manual audit
  [RussianTranslation/MANUALS_FOR_PWG_RU.md](RussianTranslation/MANUALS_FOR_PWG_RU.md)
  (all 37 Lexicography-Manuals, verdict per book) and the detailed five-manual
  theory deep-dive
  [RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md](RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md)
  (Apresjan · Riemer · Hartmann & James · Gonda–Vogel · Klosa).
- [REFERENCES.md](REFERENCES.md) — provenance for the large reference assets.
- [literature/md/INDEX.md](literature/md/INDEX.md) — cross-repo relevance map for
  the research literature collection: 65 sources tagged by which dictionary repo,
  corpus pipeline, or paper they serve, with a reverse lookup by repo.

## Headword Lists

The files in `HeadwordLists/` are named to show both the dictionary/source and
the kind of key exported. For example:

- `MW-unique-key1-193978.txt`
- `MW-unique-key2-198220.txt`
- `PWK-unique-key2-133741.txt`
- `SCH-accents-IAST-20247.txt`
- `mw-apte-mcdonell-hk.txt`
- `sanhw1.xlsx`

The trailing number usually records the count of entries in that export.

### key1 and key2

The historical README defined the two central headword keys this way:

- `key1` is a normalized computational key. It may not exist as a form printed
  in the source dictionary, but it is useful for machine comparison.
- `key2` is closer to the original printed form and is generally the better
  key for display, citation, and philological inspection.

When comparing dictionaries, start from `key1` if the task is algorithmic
matching, deduplication, or joining. Start from `key2` if the task is editorial
review, citation, or checking the digitized text against the printed source.

## Research Directions

The current roadmap frames the work around evidence-graded digital
lexicography:

- dictionary evidence should be reproducible and citable;
- inferred, derived, observed, and reviewed claims should be kept distinct;
- Sanskrit's European and indigenous lexicographic traditions should be modeled
  as parallel evidence systems rather than flattened into one format;
- learner-facing tools should connect dictionary evidence with corpus frequency
  and grammatical information.

See [`ROADMAP_2026_2027.md`](ROADMAP_2026_2027.md) for the publication plan,
FAIR/standards gaps, and proposed learner-layer work.

## Working With The Data

Most files are plain text and can be inspected with standard command-line tools
or loaded into scripts. A few files are large enough to be awkward in an editor,
especially `sanhw1.xlsx`, `DCS_statistical_evaluation.htm`, and the PWG/PWK
error-list exports.

Suggested entry points:

1. Use `HeadwordLists/*unique-key1*.txt` for normalized matching tasks.
2. Use `HeadwordLists/*unique-key2*.txt` for print-form and display tasks.
3. Use `HeadwordLists/mw-apte-mcdonell-hk.txt` for a ready-made comparison
   across major Sanskrit dictionary traditions.
4. Use [`Syntax-Lectures/sanskrit_particles_lectures.md`](Syntax-Lectures/sanskrit_particles_lectures.md)
   as the main teaching note for the particles material, and open
   [`Syntax-Lectures/sanskrit_particles_explorer.html`](Syntax-Lectures/sanskrit_particles_explorer.html)
   in a browser for the interactive, student-facing version (positional map plus
   per-particle function, deep-linked examples, citations, and the Apte 1957
   dictionary entries).
5. Use `ROADMAP_2026_2027.md` to understand how this repository connects with
   csl-atlas, VisualDCS, csl-standards, and publication work.

## Contributing

Contributions should follow [`CONTRIBUTING.md`](CONTRIBUTING.md). In short:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request and reference any related issue.

For larger data changes, include the source of the data, the transformation
method, and enough counts or checksums for another maintainer to reproduce the
result.

## License

The repository is distributed under the MIT License. See [`LICENSE`](LICENSE).
