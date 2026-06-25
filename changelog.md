# Changelog

All notable changes to SanskritLexicography are documented here.

Entries use dated, versioned releases. Keep upcoming work under [Unreleased],
then **cut a new version every time the changelog is updated** (promote
[Unreleased] to the next `x.y.z` with today's date and start a fresh
[Unreleased]).

## [Unreleased]

## [0.0.10] - 2026-06-25

### Added
- **`article-comparison/agni.gloss-review.md` — agent draft review of agni's 130
  hand-authored RU sense-glosses.** An Opus-4.8 editorial pass against the English PD
  sense + Sanskrit term + Russian Indological norm (Kochergina / Elizarenkova),
  produced as a **sign-off worklist** (the glosses themselves are untouched — they
  remain the draft they were flagged as). Findings: 1 factual category error (the
  *agnicayana* altar↔rite mix-up at senses 4i/4vi), 3 transliteration/precision fixes
  (ахаванья→ахавания; hotṛ "возливатель"→"призыватель"; udātta), 3 optional polish,
  4 optional add-glosses, and 6 English-source OCR typos already corrected in the RU.
  This is the agent-doable half of the Track B gloss review; final scholarly sign-off
  is the human step.

## [0.0.9] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — multi-volume Petersburg dictionaries now name
  the volume, not just the span.** A 7-volume dictionary's true year is the year of
  the *volume* containing the headword's letter. All four study words are a-stems, so
  the PWG / pw / PWK labels now read **Bd./Th. I** with the volume-1 year (PWG
  `Bd. I, 1855`; pw/PWK `Th. I, 1879`) instead of a bare year that read as the whole
  1855–1875 / 1879–1889 run. Header note explains the volume convention.

## [0.0.8] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — every quote now carries its dictionary's
  edition year.** Previously only a few EN dictionaries showed a year (MW 1899,
  AP90 1890, WIL 1832, MW72 1872); the Dictionary column now labels all 20 sources
  with their CDSL edition year — e.g. PWG 1855, pw/PWK 1879, GRA 1873, VCP 1873,
  SKD 1886, SHS 1900, BUR 1866, CAE 1891, BEN 1866, YAT 1846, BOP 1847, STC 1932,
  AP 1957, PE 1975, PD 1976. Years are taken from the authoritative
  [CDSL front page](https://www.sanskrit-lexicon.uni-koeln.de/) catalog (via
  `csl-guides/src/data/dictionaries.json`), the same source as the existing labels;
  a provenance note was added to each table header.

## [0.0.7] - 2026-06-25

### Changed
- **`article-comparison/` — Max-LLM residual per-sense pass (Track B tail).** Each
  attested Russian rendering the deterministic matcher left in the
  `### Не привязано к значению` bucket of every `*.persense-ru.md` was adjudicated
  by an Opus-4.8 pass against the full bilingual PD sense skeleton and routed to a
  specific sense — or kept as honest "other" (function-word / context / off-headword
  name). Per-sense coverage rises to **97–100 %** (`agni` 100 %, `akṣara` 99 %,
  `anya`/`ananta` 97 %). Implemented as a reproducible `LLM_ASSIGN` override map in
  `RussianTranslation/src/_build_persense_ru.py` (surface form → sense ordinal,
  mirroring `SYN`/`ROUTE`); LLM-assigned renderings carry a **°** marker and the
  coverage line reports the deterministic-vs-LLM split.

## [0.0.6] - 2026-06-25

> Backfilled to match tag `v0.0.6` (cut by a parallel actor against the project
> narrative `RussianTranslation/CHANGELOG.md`); this section records the same scope
> in the semver changelog.

### Added
- **Renou *register* axis** — an orthogonal multi-label `renou_register` field
  (20-code lattice: épigraphique, bhāṣya, jaina, …) parallel to the I–V Renou
  *state*, per `RussianTranslation/RENOU_SUBSECTIONS_PLAN.md`. Two provenance-tagged
  detector routes (DCS corpus `build_dcs_renou.py` + `<ls>` citation
  `renou_register.py`) plus a dedicated `épig` detector; wired end-to-end through
  `renou_audit.py` (register mode) and `renou_portrait.py`. The state axis is
  unchanged.

### Changed
- **Judge-model A/B settled — Sonnet bulk judge + Opus repass/audit.** Across
  ~650 judged cards a Sonnet QA judge is statistically indistinguishable from Opus
  (κ = 1.0 on real cards; both 99 % recall / 0 % FP on a 250-item ground-truth
  defect battery). Policy: Sonnet judges the bulk, Opus re-judges every reject + a
  ~5 % audited sample. New `src/judge_disagreements.py` / `src/judge_ab_score.py`.
  The synthetic semantic-defect test was dropped (a word-pair gloss is undecidable
  out of context). See `RussianTranslation/research/JUDGE_AB.md` / `JUDGE_POLICY.md`.

## [0.0.5] - 2026-06-25

### Added
- **`article-comparison/` — one headword across every CDSL dictionary.** A study
  comparing four "a-" headwords — `agni`, `anya` (non-samāsa) and `akṣara`,
  `ananta` (a-samāsa / nañ-privative) — each chosen as most-frequent in DCS 2026
  **and** present in the unfinished Deccan **PD** dictionary (PD's "a" stops at
  ~`apaca-`, the real constraint). Six views per word: `.table.md` (side-by-side
  all dicts, SLP1→IAST), `.pd-min.md` (PD `{@..@}` sense skeleton),
  `.pd-min.ru.md` (bilingual EN/RU), `.corpus-ru.md` (attested Russian from the
  DeepSeek word-alignment lexicon + published SamudraManthanam verse pairs),
  `.persense-ru.md` (each rendering hung under its PD sense, 88–99 % coverage),
  `.verbatim.md`/`.iast.md` (full). Builders in `RussianTranslation/src/`
  (`_build_corpus_ru.py`, `_build_skeletons_ru.py`, `_build_agni_ru.py`,
  `_build_persense_ru.py`). Audited; 2 per-sense assignment bugs fixed. Headline:
  the per-sense attested-RU split (`agni`→Агни/огонь, `akṣara`→слог/Непреходящее,
  `ananta`→бесконечный/Ананта).
- `RussianTranslation/src/run_batch.py review_csv` exports the existing
  `_review_queue.jsonl` human worklist to `_review_queue.csv` for spreadsheet
  review. The CSV keeps the severity-sorted machine evidence and adds blank
  `reviewer_id` / `decision` / `edit` / `notes` columns without advancing any
  review state.
- `RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md` and
  `RussianTranslation/src/gold_review_csv.py` define and export the human
  precision-review scaffold: 320 balanced `period × kind` rows, LLM labels kept
  separate from blank human-label/adjudication columns.
- `RussianTranslation/schemas/pwg_ru_lexicographic_portrait.schema.json` and
  `RussianTranslation/src/validate_portrait_schema.py` define a v1 Apresjan
  portrait contract and validate live `microstructure.portrait()` output.

## [0.0.4] - 2026-06-23

_(Backfilled 2026-06-25 — this release was tagged and published on GitHub but
not previously recorded here.)_

### Fixed
- **NWS attribution: the `av` `+ upa` owner slide root-caused & gated.**
  `compile_translatable.mask_nws_gloss` strips the leading owner *bleed* — a
  roman-numeral co-owner cite (`Rivelex (2) : XLV`) that `nws_split`'s digit-only
  OWNER can't tag was riding onto the next gloss's prose and misleading the LLM
  assembly. `nws_split` OWNER now stops at `;`; `check` uses word-boundary locator
  matching (kills the `apāṃ`-in-`apāṃpitta` false MISATTRIBUTION).

### Added
- **NWS attribution gate** (`run_real_test.py audit`): a fresh non-protected card
  whose NWS owners disagree with the deterministic `nws_split` parse is rejected
  (→ `<safe>.merged.REJECTED.md`, re-queued; run exits non-zero); protected
  hand-authored cards are audited but never quarantined.

## [0.0.3] - 2026-06-19

### Added
- `RussianTranslation/src/pilot/run_real_test.py` — driver for the real-conditions
  pilot test (run locally on the Max subscription, two phases, one command each):
  `prep [N] [OFFSET]` selects a coverage-first a-section batch, marks fresh vs
  protected (hand-authored `aMSa`/`anna`/`ap`) cards, and sets the workflow's
  `OFFSET`/`LIMIT`; `audit <wf_output.json>` renders via `_pilot_collect.py`,
  runs `nws_split.py check` per card, and reports judge pass rate +
  NWS-attribution (F12) clean count + misattributions.
- The audit phase was pre-flighted with a synthetic `ap` workflow output:
  collect → protected-card preservation → `nws_split.py check` → report. Result:
  publishable 1/1, NWS audit CLEAN 1, F12 misattribution 0.
- Materialized the human-review worklist with `run_batch.py review`: 217
  `legacy_needs_review` cards, severity-sorted, with no reviewer decisions
  advanced.

### Changed
- `RussianTranslation/src/pilot/run_pilot_wf.js` — the translate→judge workflow is
  now **manifest-driven** instead of a hardcoded 15-key list: it reads
  `scale_route.py`'s coverage-first `scale_manifest.<section>.json` and runs a
  `[OFFSET, OFFSET+LIMIT)` slice (editable consts), so the full a-section's 12,155
  inputs can be translated in successive batches. Falls back to the original 15-key
  pilot list if the manifest can't be read. Verified: a 30-card batch resolves
  30/30 inputs on disk via the shared `safeName()` stem.
- `run_pilot_wf.js` translator prompt — new **HARD RULE 5 (NWS layer format)**:
  render the NWS "Kleines Zitat" fragment as ONE entry per source, tagged `[NWS:]`,
  keeping each OWNER citation (`Author year : page`) verbatim as the last citation,
  never merging/compressing owners, never sliding the owner onto the next gloss
  (failure F12 reading-direction trap), sub-lemmas as first-class rows. Encodes the
  format the deterministic `nws_split.py` auditor requires — found while validating
  the loop manually on card `ap` (2026-06-19): the translation was sound but the
  first draft failed the audit purely on output format; the rule makes future cards
  audit-ready (re-checked: `nws_split.py check ap` → CLEAN, 0 misattributions).
- `_pilot_collect.py` now writes audited `<safe>.merged.md` files directly using
  the shared `safe_name()` encoder; `run_real_test.py` no longer uses the brittle
  external `<key>.md` → `<key>.merged.md` copy bridge.
- `run_real_test.py prep` was refreshed for the June-22 batch window
  (`OFFSET=0`, `LIMIT=10`): `as As Ap api amfta agni Atman anu arjuna arTa`,
  now correctly all fresh after exact-case output checks.

### Fixed
- Legacy `.merged.md` compatibility checks now require exact filenames, avoiding
  Windows case-insensitive false positives such as `Ap` being treated as protected
  because `ap.merged.md` exists.
- Generated the missing writable a-section input for `arI|a` (`|` escaped as
  `~007c`); pilot inputs now cover 12,156/12,156 a-section manifest cards.

## [0.0.2] - 2026-06-19

### Fixed
- **Case-collision in pilot input filenames (F10) — silently dropped 1,237 of
  12,156 a-section cards.** SLP1 headword keys are case-sensitive (`api`/`Api`/`ApI`,
  `as`/`As`/`aS`) but Windows filenames are not, so `_pilot_gen_merged.py` writing
  `<key>.raw.txt` made case-variants overwrite each other — including high-value
  heads (`api`, `arTa`, `As`, `aNga`), whose translation inputs held the wrong
  variant's content. Applied the NWS scraper's proven `safe_name()` (uppercase →
  `_`+lower, injective) across every reader/writer of these files
  (`_pilot_gen_merged.py`, the superseded `_pilot_gen.py`, `nws_split.py`, and the
  JS workflow `run_pilot_wf.js` with a matching `safeName()`); Python/JS encodings
  verified identical. The full a-section regenerated CLEAN (12,155 distinct files =
  12,155 by-key lookups, no collisions; 1 unwritable, `arI|a`, which contains a `|`).
  Also added per-card error-resilience so a single unwritable key no longer aborts
  an 11k-card run.

### Added
- `_pilot_gen_merged.py` now supports a manifest-driven scaled mode
  (`--manifest <section> --limit N`) driven by `scale_route.py`'s coverage-first
  order, used to generate the **full a-section** merged+NWS inputs (12,155 cards;
  PW 90 % / SCH 13 % / PWKVN 10 % / NWS-extra 35 %). `nws_split.py` (deterministic
  NWS "Kleines Zitat" splitter, F12 audit tool) is now tracked.

## [0.0.1] - 2026-06-18

### Added
- **NWS layer fully scraped, drift-validated, and folded into the merge spine.**
  `RussianTranslation/src/nws_scrape.py section all` captured all **167,990**
  headwords of the *Nachtragswörterbuch des Sanskrit* (Halle); `_nws_audit.py all`
  = CLEAN (0 missing / 0 case-collisions / 0 dups / 0 refusals), net-new
  `has_nws_extra` = 34,101 (20 %). `_nws_drift.py all` confirms the a-section's "LOW
  staleness" finding across the whole dictionary (Schmidt 96.7 % identical, mean
  Jaccard 0.987; pw 80.9 % overlap, only 0.1 % NWS-only). `dict_merge.merged()` now
  appends NWS as a 5th "external" layer — net-new only, per-key on demand, kept out
  of `LAYERS` since it adds no new headwords. (NWS scraped data stays gitignored and
  provisional pending a formal Halle data request.)
- **Merged+NWS pilot scaled from 6 hardcoded keys to a manifest-driven run.**
  `_pilot_gen_merged.py --manifest <section> --limit N` consumes `scale_route.py`'s
  coverage-first manifest to generate full layered inputs (PWG+PW+SCH+PWKVN+NWS) at
  volume, resumable. On the top-300 dense a-section heads, NWS-extra coverage reaches
  95 % (vs 20 % dict-wide). `RussianTranslation/DICTIONARY_CHAIN.md` updated with the
  all-sections scrape/drift/fold status.

### Fixed
- `_pilot_gen_merged.py` resumable skip now verifies a pre-existing `<key>.raw.txt`
  is actually in merged (`=== LAYER:`) format. The superseded PWG-only `_pilot_gen.py`
  writes the same filenames in `=== RECORD` format; trusting mere file existence
  silently skipped ~17 of the top-300 cards (e.g. `api`, `Atman`), leaving them
  un-merged. Now those stale files are regenerated.

## [1.1.3] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — `tune` now draws a reproducible
  random sample (same fixed seed as `coverage`) instead of the first N keys, so
  mid-size runs are representative. A random 4000-sample matches the full-PWG
  agreement shape (head-term Jaccard ≥0.5 ≈3.6% vs the full 3.7%); `n ≥ total`
  still reports the full run (106,085 headwords, 2,585 ≥2-dict pairs). Completes
  the random-sampling fix begun for `coverage` in 1.1.2.

## [1.1.2] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — `coverage` now draws a **random**
  sample (fixed seed, reproducible) instead of the first N keys. PWG headwords are
  SLP1-sorted and the `a-` section is over-covered (especially KOW), so first-N
  coverage badly overstated true numbers (3000-sample KOW was 39.8% vs the full
  8.0%). The corpus signal also gets its own random sub-sample. A random
  3000-sample now matches the full run (independent correctness 16.6% vs 16.4%,
  KOW 7.0% vs 8.0%, corpus ~15%). Full-PWG coverage of 106,085 headwords:
  independent correctness ≈16%, KOW reference ≈8%, corpus ≈15%.

## [1.1.1] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — the stage-4 corpus query returned 0
  aligned verses for common headwords (agni, rāma, kṛṣṇa, deva). `corpus_lines`
  (FTS) also holds dictionary rows (no `#sa`/`#ru` suffix); the query did
  `MATCH ? LIMIT 400` with no `#sa` filter in SQL, so for high-frequency words the
  first 400 matches were all dictionary rows and the Python `#sa` filter discarded
  every one. Pushed the `#sa` filter into SQL so `LIMIT` captures Sanskrit verse
  lines. Found while validating the gate end-to-end (lookup/card/coverage/tune all
  run; 5 dictionaries = 57,640 entries; coverage on a 3000-key sample: independent
  correctness 20.4%, KOW reference 39.8%, corpus 20.7%).

## [1.1.0] - 2026-06-14

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
  gate (independent-correctness + KOW reference-agreement). The translation
  pipeline itself is framed as planned/not-yet-run.
- `RussianTranslation/src/` — the stage-4 corpus-gate layer (code only; the
  `*.jsonl` dictionary data is gitignored, regenerated by `build_src.py`):
  `build_src.py` extracts five SLP1-keyed Sanskrit→Russian dictionaries from the
  sibling SamudraManthanam corpus (Kochergina 29,177; Kossovich/KOW 13,488;
  Knauer 3,271; Frisch/FRI 8,156; Smirnov 3,548 — ≈57,640 entries); `corpus_gate.py`
  joins a PWG headword to those dictionaries (+ optional SamudraManthanam parallel
  corpus) and emits the `4_korpus_proverka.txt` input, with coverage/tune modes.
- `RussianTranslation/SAMUDRA_INTEGRATION.md` — roadmap for how the sibling
  SamudraManthanam parallel-corpus tool feeds the Russian-translation projects
  (`pwg_ru`, `mw_ru`) and the WhitneyRoots crosswalk; separates built from
  planned, with verified extraction counts only.

### Notes
- The PWG corpus-check gate (stage 4) is designed as a **non-blocking annotator**
  emitting two separate signals per card: (1) *correctness* against independently
  compiled Sanskrit→Russian dictionaries (Kochergina, FRI, KNA), and
  (2) *reference-agreement* against KOW — itself a partial human PWG→Russian
  translation (Wilson-derived), so used only as a secondary, non-decisive
  reference, never to decide correctness. SKD/VCP are Sanskrit→Sanskrit and serve
  as Sanskrit-side sense corroboration only, never as a Russian authority. The
  five correctness/reference dictionaries are now extracted into
  `RussianTranslation/src/` from SamudraManthanam (≈57,640 SLP1-keyed entries);
  coverage is measured at ingest, not a blocker.

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
