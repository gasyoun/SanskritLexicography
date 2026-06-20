# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Org-level conventions (the wider `sanskrit-lexicon` ecosystem, the csl-orig
> correction workflow, GitHub issue taxonomy, `.ai_state.md` protocol, Windows
> encoding rules) live in [`../CLAUDE.md`](../CLAUDE.md) and are loaded
> automatically. This file covers only what is specific to **this** repository.

## What this repository is

A **data and research workspace** — not a software project. There is no source
code (no `.py`, `.js`, `.sh`, `package.json`, or `requirements.txt`). The
content is exported headword lists, large reference HTML/PDF documents, an
AI-produced Russian translation of Monier-Williams, and Russian-language
teaching material on Sanskrit syntax. "Working in the codebase" here means
inspecting, comparing, and transforming text data, plus authoring Markdown.

There is no build or test suite. CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml))
runs Markdown lint, Markdown link-check, and YAML lint only; the Python/JS lint
jobs are conditional and never fire because no such files exist. The active
pre-commit hooks ([`.pre-commit-config.yaml`](.pre-commit-config.yaml)) are
`check-yaml`, `end-of-file-fixer`, `trailing-whitespace` (markdown-aware), and
`check-merge-conflict`. Match these when editing: no trailing whitespace,
newline at EOF, valid YAML.

## HeadwordLists/ — naming and key semantics

This is the analytical heart of the repo. Filenames encode source, key type,
and count: `{DICT}-unique-{key1|key2}-{N}.txt`, where `N` is the entry count
(also the line count). Other patterns: `{DICT}-fehlerhaft-{N}.txt` (German
"erroneous" — flagged problem entries, e.g. [`HeadwordLists/PWG-fehlerhaft-1661.txt`](HeadwordLists/PWG-fehlerhaft-1661.txt),
which contain full XML records, not bare headwords), `SCH-accents-IAST-{N}.txt`
(accented IAST forms), and cross-dictionary join files like
[`HeadwordLists/mw-apte-mcdonell-hk.txt`](HeadwordLists/mw-apte-mcdonell-hk.txt)
(Harvard-Kyoto, sorted).

**key1 vs key2 — choose deliberately:**
- **key1** = normalized computational key. May not match any printed form;
  built for machine comparison. Use for matching, dedup, joins.
- **key2** = closer to the printed source (retains `-`, `--`, `/` accent marks,
  e.g. `a/MSa`, `a--kAra`). Use for editorial review, citation, checking
  digitized text against the scan.

Dictionary codes seen here: AP, BHS, BUR, CAE, CCS, GRA, INM, MD, MW, PD, PWG,
PWK, SCH, SKD, VCP, VEI (see [`README.md`](README.md) for the full ecosystem
table in [`../CLAUDE.md`](../CLAUDE.md)).

## Encoding — BOM is inconsistent, check before editing

The org rule is "csl-orig files never have BOMs," but **that does not hold here**.
These are exports from many sources: some have a UTF-8 BOM, some do not (e.g.
[`HeadwordLists/MW-unique-key1-193978.txt`](HeadwordLists/MW-unique-key1-193978.txt)
**has** a BOM `EF BB BF`; the key2 sibling does **not**). Before transforming a
file, check `head -c 3 file | xxd`, preserve the file's existing BOM state on
write, and never silently add or strip one. All files are UTF-8.

Several files are too large to open in an editor: `sanhw1.xlsx`,
`DCS_statistical_evaluation.htm` (~75 MB), `DCS-Moniers-roots-w-references.html`
(~16 MB), and the PWG/PWK error lists. Use streaming/CLI tools, not the Read
tool, on these.

## RussianTranslation/ — mw_ru

[`RussianTranslation/mw_ru.md`](RussianTranslation/mw_ru.md) is editor-facing
documentation of how the AI Russian translation of Monier-Williams was produced
(287,358 cards, multi-pass, multi-model). The per-stage system prompts live in
[`RussianTranslation/mw_ru_prompts/`](RussianTranslation/mw_ru_prompts/) — one
file per pipeline stage (translate → two independent QA judges → re-translate
of rejects). **Key format invariant:** only the English "wrapper" prose inside a
card is translated; Sanskrit (`<s>`), grammar abbreviations (`<gram>`), and
source references (`<ls>`) are deliberately left untouched. Do not "fix" that —
it is intentional. Most content in this directory is in Russian.

## Authoring conventions

- Markdown is the primary authored format (roadmap, changelog, lectures, the
  `mw_ru` docs). Keep it lint-clean and link-check-clean (see CI above).
- [`changelog.md`](changelog.md) uses dated maintenance snapshots; keep upcoming
  work under `[Unreleased]` until it gets a dated entry.
- [`ROADMAP_2026_2027.md`](ROADMAP_2026_2027.md) frames the research direction
  (evidence-graded lexicography, csl-atlas review, paper pipeline P1–P6) and is
  the orientation document for how this repo connects to the broader project.
- Per the global rule, render every path/URL as a clickable Markdown link in
  chat and in GitHub issue/PR/release bodies. Do not put repository file paths
  in bare backticks when a human is expected to click them. In GitHub bodies,
  use full `blob`/`tree` URLs; relative links do not resolve reliably there.
