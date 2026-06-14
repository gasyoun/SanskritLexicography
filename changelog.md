# Changelog

All notable changes to SanskritLexicography are documented here.

This repository does not currently publish versioned release notes. Entries use
dated maintenance snapshots; keep upcoming work under [Unreleased] until it is
ready for a dated entry.

## [Unreleased]

### Added
- `RussianTranslation/pwg_ru.md` + `RussianTranslation/pwg_ru_prompts/` — scaffold
  for the **planned** Russian translation of the German Petersburg dictionary
  (PWG, Böhtlingk–Roth), mirroring the `mw_ru` kit. Editor-facing doc
  (`pwg_ru.md`: a card-format guide for a German source — the `{%…%}`
  German-gloss vs. Latin rule, the placeholder scheme, the `mw_ru`-seed
  mechanism) plus five stage prompts: `1_perevod.txt` (German→Russian translate
  with a 179+80-pair DE→RU glossary), the two QA judges
  (`2_qa_sudya_opus.txt`, `2_qa_sudya_yandexgpt.txt`),
  `3_pereperevod_opus.txt` (re-translate rejects), and a new
  `4_korpus_proverka.txt` — a non-blocking, two-signal Sanskrit→Russian corpus
  gate (independent-correctness + KOW reference-agreement). Framed throughout as
  planned/not-yet-run.

### Notes
- The PWG corpus-check gate (stage 4) is designed as a **non-blocking annotator**
  emitting two separate signals per card: (1) *correctness* against independently
  compiled Sanskrit→Russian dictionaries (Kochergina, FRI, KNA), and
  (2) *reference-agreement* against KOW — itself a partial human PWG→Russian
  translation (Wilson-derived), so used only as a secondary, non-decisive
  reference, never to decide correctness. SKD/VCP are Sanskrit→Sanskrit and serve
  as Sanskrit-side sense corroboration only, never as a Russian authority. FRI is
  already on disk (`csl-orig/v02/fri/fri.txt`, Russian in `<lang n="russian">`);
  Kochergina/KNA/KOW are to be supplied. Coverage is measured at ingest, not a
  blocker.

## [1.0.2] - 2026-06-14

### Added
- `HeadwordLists/README.md` — index of the headword exports: SLP1/Velthuis
  encoding, the `{DICT}-unique-{key1|key2}-{N}` naming (with the `wc -l` = N−1
  trailing-newline caveat), variant patterns (`fehlerhaft` = full XML records,
  `accents-IAST`, count-prefix, the HK aggregate, the 41 MB `sanhw1.xlsx`),
  key1/key2 semantics, the two-MW-key2 version note, the BOM-inconsistency
  caveat, and a 16-code dictionary table cross-checked against the CDSL site
  (resolves PD = Encyclopedic Dictionary on Historical Principles, CCS =
  Cappeller Sanskrit→German).
- `REFERENCES.md` — provenance (source, date, producer, size) for the root
  reference assets (`CDSL-2025.pdf`, the two DCS HTML exports,
  `helpmorphids.html`, `gasuns_cologne-zograf_2019.pdf`, and the previously
  unlisted `WSC 2025 Reviews 7.pdf`), read from each file's own metadata with
  inferred descriptions flagged; linked from the README Contents table.
- `README.md` — new "Documentation map" section grouping every doc by purpose
  (Orientation; Contributors & agents; Material by area) with a one-line hook
  and link each, so a newcomer can find the right entry point.

### Changed
- `CONTRIBUTING.md` — expanded from the 3-step stub: formalised the data-change
  provenance expectation (source + transformation + counts/checksums) that
  previously lived only in README prose, plus filename-count and BOM conventions,
  a Documentation-changes section, and a Hygiene section.

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
