# Contributing to SanskritLexicography

> Part of the [Sanskrit Lexicon](https://github.com/sanskrit-lexicon) project. Inherits the [org-wide contribution standard](https://github.com/sanskrit-lexicon/COLOGNE/blob/master/CONTRIBUTING.md).

This is a **data and research workspace**, not a software project: most changes
are data files, indexes, and documentation. The guidance below reflects that.

## Basic flow

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request, referencing any related issue.

## Data changes — provenance is required

For any non-trivial data change (new or regenerated headword list, export,
derived file), the PR description must let another maintainer **reproduce** the
result. Include:

- **Source** — which dictionary/corpus and which version/snapshot the data came
  from (e.g. a CDSL dictionary code, a DCS export, a specific input file).
- **Transformation** — the method: the script/command, normalisation, sort
  order, encoding conversion. Enough that the step can be re-run.
- **Counts / checksums** — entry count and, ideally, a checksum, so a reviewer
  can confirm they reproduced the same file.

Conventions to keep when touching data:

- **Filename counts are real.** `HeadwordLists/` uses
  `{DICT}-unique-{key1|key2}-{N}.txt` where `N` is the entry count; update `N` if
  the count changes. See [HeadwordLists/README.md](HeadwordLists/README.md).
- **Encoding: UTF-8, and check the BOM.** BOM presence is inconsistent across
  exports here — `head -c 3 file | xxd` before editing and preserve the file's
  existing BOM state; do not silently add or strip one.
- **Large reference assets** get a provenance row in
  [REFERENCES.md](REFERENCES.md) (source, date, producer, size).

## Documentation changes

- **Clickable links everywhere.** Every path/URL is a Markdown link. In repo
  files use relative links; in GitHub PR/issue bodies use full `blob`/`tree`
  URLs (relative links don't resolve there).
- **Match the material's language.** Russian-content directories get Russian
  indexes; the root README and CLAUDE.md are English.
- **Refer to files in other repos as plain text, not links** — a link to a file
  that isn't in this repo fails CI link-check. Note it as external instead.
- **Run a link check** before opening the PR (CI runs a Markdown link-check
  job too); fix any broken relative link.
- Add a `changelog.md` `[Unreleased]` entry for anything notable.

## Hygiene

- Keep Markdown lint-clean: no trailing whitespace, newline at end of file,
  valid YAML. The [pre-commit hooks](.pre-commit-config.yaml) and
  [CI](.github/workflows/ci.yml) enforce this.
- Don't commit large binaries or generated data casually — confirm intent first.

## See also

- [CLAUDE.md](CLAUDE.md) — repo conventions (key1/key2, BOM, external-refs rule).
- [HANDOFF.md](HANDOFF.md) — retired orientation note, now a pointer to the current manuals.
- [README.md](README.md) — the Documentation map (where to read what).
