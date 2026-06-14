# Changelog

All notable changes to SanskritLexicography are documented here.

This repository does not currently publish versioned release notes. Entries use
dated maintenance snapshots; keep upcoming work under [Unreleased] until it is
ready for a dated entry.

## [1.0.1] - 2026-06-14

### Added
- `CLAUDE.md` — repository-level guidance for Claude Code. Documents what is
  specific to this data/research workspace (no source code): `HeadwordLists/`
  naming and key1/key2 semantics, the inconsistent UTF-8 BOM state across
  exports, the `mw_ru` translation format invariant, and the lint-only
  CI/pre-commit expectations. Ecosystem/workflow/taxonomy conventions are
  deferred to the org-level `../CLAUDE.md`.
- `Syntax-Lectures/sanskrit_particles_explorer.html` — a self-contained,
  Russian-language interactive explorer that digests the particle lectures for
  students: a clickable positional map (Zaliznyak / Wackernagel) over 16
  particles, with per-particle function, examples (deep-linked to the Gītā/Manu
  parallel corpus, Whitney, Speyer, Archive.org and DCS), Gonda/König/Hock
  citations, the full bibliography, and the folded-in Apte (1957) dictionary
  entries for the seven particles that have them. Built from
  `sanskrit_particles_lectures.md`, `sanskrit_particles_schema.html`, and the
  `Apte_1957-*_RU.md` series.
- `Syntax-Lectures/README.md` — Russian index of the particle materials: a
  start-here pointer to the lectures conspect, a table of the three primary
  files (lectures, the Zaliznyak positional schema, the interactive explorer),
  and a mapping of the seven `Apte_1957-*_RU.md` particle entries (those of the
  16 explorer particles that have an Apte article).
- `RussianTranslation/mw_ru.md` — new section 7 "Внешние документы", an
  appendix tabling the six files referenced from the mw_ru docs that live in
  the separate working repo (`kosha_ai_translation.md`, `improvements.md`,
  `yandex_api.md`, the two glossary JSONs, the QA scripts): what each is and
  where it is cited.

### Fixed
- mw_ru docs: demoted four dead links pointing at external working-repo files
  to plain text (`improvements.md` and `docs/yandex_api.md` in `qa_judge_v4.md`;
  two glossary JSONs in `mw_ru.md`), so all relative links in
  `RussianTranslation/` now resolve. Added `qa_judge_v4.md` to the prompts
  `README.md` index, marked as a proposed v4 update to the stage-2 judge.

## [1.0.0] - 2026-06-13

### Added
- Added this changelog so repository-level changes have a stable home.
- Recorded the current repository purpose: Research and data workspace for Sanskrit digital lexicography, with a focus on Cologne Digital Sanskrit Lexicon headword lists, cross-dictionary comparison, and teaching materials for Sanskrit lexical and syntactic study.

### Recent Git History
- 2026-06-12 Add 12-month research roadmap: csl-atlas DH review, paper pipeline P1-P6, book plan
- 2026-05-29 ai-wip: add .pre-commit-config.yaml (yaml-only)
- 2026-05-29 ai-wip: add .github/dependabot.yml for GitHub Actions auto-updates
- 2026-05-29 ai-wip: add CODE_OF_CONDUCT.md (Contributor Covenant 2.1)
- 2026-05-29 ai-wip: add CI workflow (generic-text)
