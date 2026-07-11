# Changelog

All notable changes to SanskritLexicography are documented here.

Entries use dated, versioned releases. Keep upcoming work under [Unreleased],
then **cut a new version every time the changelog is updated** (promote
[Unreleased] to the next `x.y.z` with today's date and start a fresh
[Unreleased]).

## [Unreleased]

## [1.5.2] - 2026-07-11

### Added — RussianTranslation deep manual (H606)
- New [`docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md):
  first subsystem deep manual per the
  [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
  queue — mw_ru covered as a finished-pipeline post-mortem, pwg_ru as the live
  operator procedure (production window step-by-step with traps inline, lanes +
  medium50 pause state, kill-gate mechanics, RU/EN parity contract, 216-script
  census with destructive-on-rerun table, data-assets/rights boundary).
  Fact-checked against sources; router row, PROFILE queue flip, and metadoc
  revision row in the same change. Fable 5 (`claude-fable-5`), 11-07-2026.

## [1.5.1] - 2026-07-11

### Fixed — FINDINGS.md duplicate section keys (H616)
- Repaired the seven accidentally duplicated `§N` citation keys found by the
  H604 fact-check: the later twin of each pair renumbered to a fresh key with a
  one-line tombstone under the renamed heading — §60→§70 (pwg_ru TM composite
  grade), §62→§71 (PWG case-government census), §63→§72 (VedaWeb `id_gra` =
  GRA `<L>`), §64→§73 (VedaWeb license fields), §65→§74 (ls-graph degeneracy
  for MW), §69→§75 (Devībhāgavata not on GRETIL). The second "§56" was a
  verbatim double-append of §68 (spellchecker landscape, PRs #305/#307) and was
  removed with a tombstone under §68. Header max-number marker corrected
  (§65→§75); stale citations of the renamed twins repointed in
  [`STALENESS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md),
  [`ROADMAP_VEDAWEB_REUSE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md),
  [`RussianTranslation/PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md),
  [`RussianTranslation/USE_CASES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md)
  and `RussianTranslation/.ai_state.md`; duplication caveats dropped from
  [`docs/manuals/MAINTAINER_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md) §3
  and [`docs/manuals/RESEARCHER_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md) §5;
  metadoc backlog item 4 closed.

## [1.5.0] - 2026-07-11

### Added — audience manuals
- New [`docs/manuals/`](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals):
  four deep, standalone manuals for distinct audiences — maintainer, researcher,
  student (Russian), and data-reuser — plus a
  [router README](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md).
  Linked from the root README documentation map. Language follows audience
  (student = Russian; the rest English). Built under
  [Uprava H535](https://github.com/gasyoun/Uprava/blob/main/handoffs/H535-Opus_SanskritLexicography_audience-manuals-quartet_10.07.26.md).

### Changed — CLAUDE.md reflects the repo is now hybrid (data + code)
- Corrected the stale "no source code (no `.py`…)" and "Python/JS lint jobs …
  never fire because no such files exist" claims in
  [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md):
  the repo now carries substantial Python (263 tracked `.py`, a root
  `requirements.txt`) and CI's Python lint + RussianTranslation gates do fire.
  Follow-up flagged under H535 (already noted in the maintainer manual).

### Added — other highlights since v1.4.0 (synthesized from git log)
- Public PWG→RU translation **progress dashboard**
  ([PR #315](https://github.com/gasyoun/SanskritLexicography/pull/315)).
- pwg_ru article site: `<ab>`/`<ls>` tooltips + RU-column abbreviation purity per
  [`RussianTranslation/ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
  ([PR #308](https://github.com/gasyoun/SanskritLexicography/pull/308)); multi-second
  freeze on large articles fixed ([PR #320](https://github.com/gasyoun/SanskritLexicography/pull/320)).
- M01 literature crosswalk + 37-manual library metadoc, H505
  ([PR #319](https://github.com/gasyoun/SanskritLexicography/pull/319)).
- FINDINGS §66–§69 (QL SLP1 truncation, PWG article-size confound, spellchecker
  landscape, DBhP absence from GRETIL) and DEAD_ENDS/GAPS/ASSUMPTIONS episteme
  entries for the Sundara apparatus and F4-DCS edition-mismatch dead ends.
- Editorial rule applied repo-wide: drop `ё` (keep the всё/все distinction), H543
  ([PR #324](https://github.com/gasyoun/SanskritLexicography/pull/324)).

## [1.1.5] - 2026-07-03

### Added — Indische Sprüche dataset
- New [`IndischeSprueche/`](https://github.com/gasyoun/SanskritLexicography/tree/master/IndischeSprueche)
  data asset: the full Böhtlingk *Indische Sprüche* collection (2nd ed. 1870–1873),
  7,537 sayings exported from `VisualDCS` archive.sqlite's `subhashita` table (D4)
  via the new `VisualDCS/src/DCS-data-2026/export_subhashita_jsonl.py`, as
  [`IndischeSprueche/data/indische_sprueche.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl).
  PWG cites this collection 6,666 times and PWK 138 times as `Spr. N` — see
  [`IndischeSprueche/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/README.md)
  for provenance and the scoped PWG/PWK citation-crosswalk follow-on
  ([Uprava H143](https://github.com/gasyoun/Uprava/blob/main/handoffs/H143_pwg_pwk_indische_sprueche_crosswalk.md)).

## [1.1.4] - 2026-07-03

## [0.0.42] - 2026-07-02

### Changed — A36 ready to send (Fable S9 pre-submission pass)
- [`papers/A36_latin_obscena_note.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena_note.md)
  reaches **5/5 ready-to-send** for *Beiträge zur Geschichte der Sprachwissenschaft*: referee-style
  review [`papers/A36_review_fable5.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_review_fable5.md)
  (7 major + 7 minor findings, all applied same pass — history-first retitle, Liddell–Scott /
  Cambridge-Greek-Lexicon comparandum in §0, Bopp-has-no-√yabh + MW72-etymological-*cunnus*
  source corrections against csl-orig, Adams register set re-defined, §3c table repaired; every
  table figure re-verified against the three CSVs). Cover letters (EN/DE) synced.
  ([PR #74](https://github.com/gasyoun/SanskritLexicography/pull/74)) — Fable 5 (`claude-fable-5`).

### Added — FINDINGS §44
- Raw Latin-string tallies over gloss text include etymological false positives (MW72's lone
  *cunnus* glosses a Lithuanian cognate); Bopp lacks √*yabh* entirely — reuse caveats for
  [`papers/A36_corpus_screen.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_corpus_screen.csv).
  ([PR #76](https://github.com/gasyoun/SanskritLexicography/pull/76))

## [0.0.41] - 2026-07-02

### Fixed — dashboard: single-snapshot charts no longer render as a floating dot
- With only one monthly snapshot, each tracked-metric chart drew a lone centered dot in an
  empty box (looked broken). Single-snapshot metrics now render as a stat card (big value +
  "trend line appears with the next monthly refresh"); real multi-point series gain min/max
  axis labels, first/last month labels, gridlines, and an emphasized last point. Both states
  browser-verified (the multi-point branch against a synthetic two-snapshot series).

## [0.0.40] - 2026-07-02

### Added — FINDINGS dashboard (recurring visualization of the registry)
- New [`findings_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard):
  a single-file dashboard (vanilla JS + inline SVG, no build step) live at
  <https://gasyoun.github.io/SanskritLexicography/findings/> — importance × section matrix,
  staleness flags (> 180 days, 🔴-first), monthly time series for the re-measurable findings
  (§12 DCS→CDSL linkage, §13 glossary coverage, §21 citation coverage, §25 queue decay,
  registry size), and the §41 platform-liveness board (12 platforms).
- **Refresh = monthly, mixed:** GitHub Actions cron
  ([`findings-dashboard.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml),
  3rd of month) for registry meta + metric collection; a local Task-Scheduler run
  ([`monthly_refresh.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/monthly_refresh.py))
  for the platform probes, which need residential egress (GHA IPs are blocked by several
  hosts). Collectors verified against live values (81.4 / 86.6 / 83.2 / 0.82 %).
- Scope: public SL registry only — the private Uprava infra registry is deliberately excluded.
- Built by Fable 5 (`claude-fable-5`); page render browser-verified before publish.

## [0.0.39] - 2026-07-02

### Added — FINDINGS.md: importance labels on every finding
- Every finding (§1–§43) now carries a 3-level colour dot at the start of its claim line and
  index entry — 🔴 3 important · 🟠 2 medium · 🟡 1 not that important — mirroring the issue
  taxonomy's severity palette (minor/medium/hard). Legend + assign-on-append rule added to the
  schema. Same treatment in
  [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (§1–§9).
  Plain emoji — no HTML; heading anchors untouched (dots live outside the headings).

## [0.0.38] - 2026-07-02

### Changed — FINDINGS.md: HTML Source styling reverted to plain blockquotes
- The v0.0.37 `<div align="right">` + `<sub>` Source styling was **rejected on review**
  ("looks ugly, never repeat") and removed same day. Every **Source** paragraph in
  [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  (and [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)) is now
  a plain blockquote `> **Source:** …` — left indent + GitHub's muted rendering, zero HTML.
  The no-HTML-in-md rule is restored as absolute (global rule, md-hygiene skill, and memory
  updated with the tested-and-rejected verdict). § numbering from 0.0.37 stays.

## [0.0.37] - 2026-07-02

### Changed — FINDINGS.md: § signs + right-aligned small Source lines
- Every finding number now carries the paragraph sign (`### §16. …`, mirrored in the index;
  anchors unchanged — GitHub strips `§` from slugs). Every **Source** paragraph is right-aligned
  small type via `<div align="right">` + `<sub>` — the one **sanctioned HTML** in the FINDINGS
  registries (grey text is impossible on GitHub around clickable links; right+small is the
  agreed stand-in). Same treatment in
  [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (§1–§8).
  The global no-HTML-in-md rule, the md-hygiene skill, and memory carry the matching carve-out.

## [0.0.36] - 2026-07-02

### Changed — FINDINGS.md: numbered findings + Source as own paragraph
- Every finding in [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  now carries a paragraph number in its heading (1–40, **append-only** — a new finding takes
  the next free number, existing numbers never shift, mirrored in the index anchors), and each
  **Source** line is its own paragraph so it renders on a separate line. Same treatment applied
  to the [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) infra
  registry (8 findings).

## [0.0.35] - 2026-07-02

### Changed — FINDINGS.md restructured into an indexed, anchored registry
- [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md):
  every finding is now a `###` heading with a stable anchor, plus a MEMORY-style one-line
  index at the top (40 findings) — recall without reading bodies. Dated header + byline
  added; the intro's `PILOT_LESSONS`/`SHARED_CODE` links upgraded to full blob URLs.
- Re-sectioned: the four Sanskrit-data findings mis-filed under "Tooling & infra" moved to a
  new **Etymology & derivation** section / "Dictionary structure & markup"; the CodeQL-has-no-PHP
  finding moved to [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
  (infra registry), leaving a pointer.

### Added — 15 new verified findings from a six-repo sweep
- Sweep of WhitneyRoots, VisualDCS, SanskritSpellCheck, csl-atlas, csl-apidev, csl-observatory,
  csl-corrections + this repo (6 parallel Fable 5 `claude-fable-5` Explore agents, then a
  dedicated Fable 5 fact-check agent re-verified every number against its source file — 12
  agent-reported inaccuracies corrected before commit). Highlights: DCS `OccId`/`sent_id` non-unique (134,047
  tokens / 449 sentences dropped pre-fix); UD `Tense=Past` conflates aorist/perfect; homonym
  token-split ceiling (5/38 gaṇa-splittable); Sa→Ru glossary 86.6 % token coverage; PWG∩MW
  union = 94,753; MW inherited PWG's apparatus skeleton (0.81 citation-order concordance);
  gloss-language ortho-drift ∝ reform type (RU 358/1k ≫ DE 10.3 ≫ FR/EN ≤ 0.5 ≫ LA 0);
  body-text headword mining dead end (38.6 % precision — negative result rescued from a
  deleted review artifact).
- Note: tag `v0.0.34` exists (kosha triage, 2026-07-02) without a changelog entry — left as-is;
  this release is numbered past it.

## [0.0.33] - 2026-06-29

### Added — grammar-layer FAIR package + VedaWeb accent-axis probe (follow-up to 0.0.32)
- **Declension display** shipped (`nominal_grammar.py --table`, `reverse_index.py --show`) — vidyut
  paradigm table per headword / per paradigm token. Per-word grammar dataset materialized into
  `headword_index.tsv` (98,639 rows; kept out of translation — portraits untouched).
- **FAIR data package** `RussianTranslation/src/datapackage.json` (Frictionless, CC-BY-SA-4.0) over
  the five grammar resources with field schemas, sources, and deterministic-rebuild provenance;
  archivable on its own DOI track.
- **VedaWeb accent-axis probe CONFIRMED**: VedaWeb 2.0 API live (`vedaweb.uni-koeln.de/api`); the
  Casaretto et al. (2025) annotation layer returns udātta-marked, position-aligned per-word forms
  (RV 6.59.3: `…agnī́; ávasā; …devā́`) with co-located lemma+morphology and a bulk export — the
  accent a–f axis is de-risked (only the Whitney-rule encoding + join remain). Turnkey API path +
  resource IDs recorded in `ZALIZNYAK_INDEX.md` and `FINDINGS.md`.

## [0.0.32] - 2026-06-29

### Added — pwg_ru structured grammar layer (nominal grammar, Zaliznyak index, reverse dictionary)
- **Nominal grammar layer**: `RussianTranslation/src/nominal_grammar.py` (stem class, Whitney §§,
  vidyut subanta paradigm with the `nyap` fix for feminine ā/ī/ū stems) + `src/mw_compounds.py`
  (106,603 MW `<k2>` compound segmentations). Whitney exception §§ folded into the root layer
  (`whitney_grammar.json`, 289 records). Docs: `GRAMMAR_LAYER.md` (hub).
- **A/B test → grammar-in-translation REJECTED** (`NOMINAL_GRAMMAR_AB.md` +
  `NOMINAL_GRAMMAR_AB_DETAIL.md`): blind Opus judge over 8 stratified headwords, arm A (grammar
  OFF) 5 / tie 2 / arm B (ON) 1; both arms 0 nulls, 100% markup fidelity. Nominal windows run
  grammar **OFF**; the layer is kept as structured data only (portraits left untouched).
- **Zaliznyak inflection index** (`ZALIZNYAK_INDEX.md`): compact per-word token `G·T S F`
  (e.g. `m·8n*`); **reverse dictionary** over all 123,366 PWG entries → 98,639 indexed → 335
  paradigm tokens; per-word FAIR dataset `headword_index.tsv` + `reverse_paradigm_index.json` +
  `paradigm_stats.tsv`; **declension display** via vidyut (`--show` / `--table`).
- **Accent a–f axis** spec'd + unblocked: Whitney's per-case accent §§ already ingested + PWG
  `key2` accents + **VedaWeb** (CC BY 4.0) as the validation set; logged in `FINDINGS.md`.

## [0.0.31] - 2026-06-26

### Fixed — stale-doc cleanup across the pwg_ru planning/runbook set
- Aligned the `RussianTranslation/` docs with the current pipeline after the judge-escalation +
  harvest-port changes: corrected present-tense "Opus judges every card" claims to the
  Sonnet-bulk + Opus-on-reject policy (STRATEGY.md, FREQ_TEST_RUNBOOK.md, HANDOFF); marked the
  four prompt nits and the `--root-split` hook as done; noted the dropped `pwg_preverb1.txt`
  sandhi-join follow-up; added superseded-pointers to the pre-Max-harness plans
  (IMPLEMENTATION_PLAN.md, PIPELINE_ARCHITECTURE.md) and a "now-implemented" note to PILOT_COST §7.
  Correct historical statements (the Opus-run validation passes) were left intact;
  `research/JUDGE_POLICY.md` is the single source of truth for the judge policy.

## [0.0.30] - 2026-06-26

### Changed — pwg_ru judge escalation: Sonnet bulk, Opus only on hard cases
- Implemented the decided judge policy (`RussianTranslation/research/JUDGE_POLICY.md`) in the Max
  harness (`RussianTranslation/src/pilot/run_pilot_wf.js`): **Sonnet judges every card; Opus
  re-judges ONLY the rejects** (`ok=false || severity>=3`), Opus verdict final. Publishable cards
  (sev 1–2) spend no Opus tokens — the weekly-quota headroom that makes the bulk run feasible on one
  Max seat. Justified by the κ=1.0 / 474-card A/B (`JUDGE_AB.md`). Pipeline now 3-stage
  (Translate · Judge · Adjudicate); `node --check` clean. Runbook + policy docs marked implemented.

## [0.0.29] - 2026-06-26

### Changed — pwg_ru bulk-run preflight: harvest ported into the production harness
- **Launch-readiness audit** of the PWG→Russian bulk run (translator = Sonnet, judge =
  Opus 4.8). Verdict: GREEN to start the first instrumented window. Confirmed all four
  "pre-run prompt nits" already encoded in the Max harness and all gate scripts wired.
- **Literature-harvest refinements ported into the live harness**
  (`RussianTranslation/src/pilot/run_pilot_wf.js`, which inlines its own prompt and does not
  read `pwg_ru_prompts/*.txt`): samāsa right-headedness, the *yad…tad* correlative map,
  śāstric formula equivalents, synonym-string cardinality, comma/semicolon sense-grouping,
  manner/position forcing, plus a soft judge check. `node --check` clean.
- **Runbook + docs updated:** `RUN_FREQ_MAX.md` window loop (SECTION warning + fidelity-gate
  step); [`MANUALS_FIVE_DEEP_DIVE.md`](RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md) closing
  section rewritten as a per-finding pipeline-status table (live / ported / deferred);
  `pwg_ru.md` gains a theoretical-basis pointer to the literature docs.

## [0.0.28] - 2026-06-26

### Added — literature shelf mined for the Sanskrit→Russian dictionary
- **Per-manual audit + theory deep-dive for pwg_ru.** Three new docs under
  `RussianTranslation/`: [`LITERATURE_FOR_PWG_RU.md`](RussianTranslation/LITERATURE_FOR_PWG_RU.md)
  (three-pass full-text harvest of the whole `literature/md/` shelf, distilled by pipeline
  insertion point), [`MANUALS_FOR_PWG_RU.md`](RussianTranslation/MANUALS_FOR_PWG_RU.md) (all
  **37** `Lexicography-Manuals/` walked one at a time — 19 drive theory, 2 marginal, 15 serve
  other repos, 1 OCR-blocked), and
  [`MANUALS_FIVE_DEEP_DIVE.md`](RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md) (detailed,
  text-grounded theory of the five load-bearing manuals — Apresjan, Riemer, Hartmann & James,
  Gonda–Vogel, Klosa — for making a Sanskrit–Russian dictionary).
- **Harvest folded into the live pipeline:** the pwg_ru translator and QA-judge prompts plus a
  new hand-curated glossary `RussianTranslation/glossaries/de_ru_translation_aids.md` (samāsa
  types, case-absolute constructions, śāstric formulas, the *yad…tad* correlative map, the
  19th-c. German orthography decoder).
- **Literature index refreshed.** [`literature/md/INDEX.md`](literature/md/INDEX.md) gains the
  **⚠ blocked** convention (5 files un-mineable until re-OCR'd / re-extracted), RuTrans tags on
  Renou/Apresjan/Tubb, and ✓-fixed notes on the two re-sliced NLP-proceedings bundles
  (Adapting-NLP, Performance-POS). README documentation-map updated to point at the new docs.

## [0.0.27] - 2026-06-26

### Fixed — doc consolidation
- **Broken relative links repaired.** `union/UNION.md` (generated) linked its scripts and
  sibling TSVs with HeadwordLists-relative paths although the file lives in `union/`; fixed
  in `build_union.py`'s md generation (`../build_union.py`, `../screen_candidates.py`,
  same-dir TSVs) and the Catalan §7 `accent_review.py` link → `../accent_review.py`. All **143
  internal links across the 19 HeadwordLists md files now resolve** (0 broken).
- **`.ai_state.md`** gains a "Current status (2026-06-26)" header: HeadwordLists print-readiness
  agent-prep complete (A–F), pwg_ru Track A ongoing.
## [0.0.26] - 2026-06-26

### Added — accent disagreements rendered for adjudication (item C)
- [`accent_review.py`](HeadwordLists/accent_review.py) → [`Catalan-Pujol/accent_disagreements.tsv`](HeadwordLists/Catalan-Pujol/accent_disagreements.tsv):
  the **63** Pujol-vs-Cologne accent-position disagreements (32 vs GRA, 31 vs MW), each
  rendered as **accented IAST on both sides** (`bhagá` vs `bhága`) with the vowel ordinal and
  a `recommend` column (Cologne RV/MW canonical). The print list (the union) already uses the
  Cologne `<k2>` accents, so item C resolves to: **use Cologne accents; the 63 are a QA list
  for the Catalan editors**, not a change to the print list. §7 + PRINT_READINESS C updated.
- **All PRINT_READINESS agent-prep is now complete** (A–F): the remaining work is human
  verification/decisions, and the two headline findings stand — CDSL coverage of attested
  vocabulary is essentially complete (B), and the MW/PWG spine is gated only by 16 typos (A).
## [0.0.25] - 2026-06-26

### Changed — typo queue extended to all 122; coverage additions cross-tagged
- **A — all 122 typos.** [`assemble_typo_queue.py`](HeadwordLists/assemble_typo_queue.py) now
  auto-discovers every dict's FILE-FIRST queue → [`A_TYPO_QUEUE.md`](HeadwordLists/A_TYPO_QUEUE.md)
  is the full **122 across 11 dicts** (spine MW 4 + PWG 12 first, then SHS 37, YAT 27, ACC 22,
  MCI 10, SKD 3, WIL 3, PW 2, GST 1, VCP 1), each with IAST + error type + entry-body evidence.
- **B — cross-tagged.** [`crosstag_additions.py`](HeadwordLists/crosstag_additions.py) tags the 416
  priority additions with Catalan/Huet external attestation
  ([`union/coverage_additions_crosstagged.tsv`](HeadwordLists/union/coverage_additions_crosstagged.tsv)).
  **Only 25/416 (6 %) are externally corroborated, and ~8 are genuine real words** (`karkandhū`
  jujube, `maṇikā` jar, `cittamātra`, `nistaraṅga`…); the rest are verb roots / Pāṇinian affixes
  (`ghañ`, `ktvā`) Catalan/Huet also headword. **Conclusion: CDSL coverage of attested vocabulary
  is essentially complete — the print list needs ~nothing added.**
## [0.0.24] - 2026-06-26

### Added — MW+PWG typo queue assembled (item A)
- [`assemble_typo_queue.py`](HeadwordLists/assemble_typo_queue.py) consolidates the print
  spine's body-confirmed FILE-FIRST typos from
  [SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) into
  [`A_TYPO_QUEUE.md`](HeadwordLists/A_TYPO_QUEUE.md): **16 (MW 4 + PWG 12)**, each with SLP1 +
  IAST, an **error-type** label (n→ṇ, vowel-length, sibilant, b↔v, aspirate) and the
  dictionary's **own entry-body evidence**. PWG's are mostly **b↔v** (Fraktur-OCR). Verify on
  scan → flip `n`→`y` → file to csl-corrections (workflow stays in SanskritSpellCheck). The
  spine's "don't print known typos" pass is now a 16-row checklist.
## [0.0.23] - 2026-06-26

### Added — coverage additions ranked by DCS band (item B)
- [`coverage_additions.py`](HeadwordLists/coverage_additions.py) → DCS-corpus lemmas absent
  from all 15 CDSL dicts (the union, with folded feminines added back to the baseline),
  ranked by frequency band: [`COVERAGE_ADDITIONS.md`](HeadwordLists/COVERAGE_ADDITIONS.md) +
  [`union/coverage_additions.tsv`](HeadwordLists/union/coverage_additions.tsv).
- **21,759 absent**, but the high-frequency end is **lemmatisation artifacts** (causative `-ay`
  stems, prefixed/desiderative roots, bīja, indeclinables — flagged by a `kind` column), not
  real gaps. Genuine **nominal** additions concentrate low-band; the **actionable priority =
  409 band-3 nominal** (e.g. `bhasmasūta`, `bhṛgutīrtha`, `āntarika`). Confirms the Catalan §5
  pattern: real coverage gaps are rare words. PRINT_READINESS B marked ranked.
## [0.0.22] - 2026-06-26

### Added — gloss pre-screen of the low-confidence fold candidates
- [`screen_candidates.py`](HeadwordLists/screen_candidates.py) pulls the short **MW gloss** for
  both forms of each of the 426 low-confidence `-ā/-ī` fold candidates →
  [`union/low_candidates_screened.tsv`](HeadwordLists/union/low_candidates_screened.tsv). Result:
  **419 likely-distinct** (reject at a glance — `ārā` "awl" vs `āra` "brass"; `īṣā` "carriage-pole"
  vs `īṣa` "the month Āśvina") and **7 MAYBE-related** to eyeball (`tālikā`/`tālika` same gloss;
  `adharmā`/`adharma`). Cuts the editor's low-set review from 426 to ~7; the gloss is the first MW
  sense (text after `</lex>`, before the first `<ls>` citation, etymology stripped).
## [0.0.21] - 2026-06-26

### Changed — union now covers all 15 dicts + fold candidates ranked
- **Fuller union.** `build_union.py` now reads `<k1>` directly from current csl-orig for
  **all 15 dicts** with a source (adds the 7 key2-only dicts BHS/BUR/CAE/CCS/INM/MD/SCH to
  the original 8) → **323,425** headwords (was 295,298), 180,989 in ≥2 dicts.
- **Fold candidates ranked for review.** The `-ā`/`-ī` candidates in
  [`union/fold_candidates.tsv`](HeadwordLists/union/fold_candidates.tsv) now carry a
  `confidence` (+ `n_shared_dicts`, `masc_gender`): **3,569 high** (the masculine base is
  itself `mfn`, so the `-ā/-ī` genuinely is its feminine — `parā←para`) vs **426 low** (masc
  `m`-only → likely a distinct lexeme like `āśā`≠`āśa`). Review high first. 237 `-inī`
  auto-folded. Gender is MW/AP-driven (BUR has no `<lex>`).
## [0.0.20] - 2026-06-26

### Added — cross-dict UNION headword index (scope E) with feminine fold (F)
- **Scope decided = union**, feminines folded under the masculine. [`build_union.py`](HeadwordLists/build_union.py)
  merges the 8 key1 dicts (AP GRA MW PWG PWK SKD VCP VEI) from `now-2026/` into a single
  **295,298-headword** index with per-headword **provenance** (which dicts attest it) and
  **gender** aggregated from each dict's `<lex>` (parsed per multi-line `<L>` record).
  → [`union/UNION.md`](HeadwordLists/union/UNION.md), `union/union_headwords.tsv`
  (`slp1, iast, n_dicts, dicts, gender, fem_fold`).
- **Feminine fold, gender-driven and split for safety:** only the unambiguous **`-inī`→`-in`**
  (238, gender-confirmed) is auto-folded — the masculine base gets an `mf(ī)` marker; the
  **3,993 `-ā`/`-ī`** cases go to [`union/fold_candidates.tsv`](HeadwordLists/union/fold_candidates.tsv)
  for editor review, because a feminine `-ā` noun often shares a stem with an unrelated
  masculine `-a` (e.g. `āśā` "hope" ≠ feminine of `āśa` "corner"). Auto-fold audit in
  `union/folded_feminines.tsv`. Covers the 8 key1 dicts; key2-only dicts mergeable next.
## [0.0.19] - 2026-06-26

### Added — item-F candidate lists (`alternate_headwords.py` + `f_candidates/`)
- Generated the editor worklists for PRINT_READINESS item **F**:
  [`alternate_headwords.py`](HeadwordLists/alternate_headwords.py) emits, from the 2026
  key1 sets, feminine↔masculine pairs, orphan feminines, variant-spelling pairs
  (b~v / ś~ṣ / geminate), and multi-`<k2>` alternate groups (SLP1 + IAST) into
  [`f_candidates/`](HeadwordLists/f_candidates/), summarised in
  [`ALTERNATE_HEADWORDS.md`](HeadwordLists/ALTERNATE_HEADWORDS.md). **MW: 5,036
  feminine↔masculine pairs, 22,298 orphan feminines, 1,217 variant pairs, 0 multi-`<k2>`**
  (alternate comma-lists negligible). SKD generated as a union-case sample. These are
  candidates to filter (morphological-shape pairing includes semantic non-pairs); the
  fold/keep/merge policy stays human.
## [0.0.18] - 2026-06-26

### Changed — PRINT_READINESS: add alternate/feminine headword gate (F)
- New checklist item **F — alternate & feminine headword policy** in
  [`PRINT_READINESS.md`](HeadwordLists/PRINT_READINESS.md). MW (2026) is **~14 % ā/ī-stems**
  (18,186 `-ā` + 9,148 `-ī`) and CDSL headwords feminines *inconsistently* — only 24 % of
  `-ā` feminines have a separate masculine base, 30 % of `-inī` have the `-in`. Pujol/INRIA
  list feminines separately; the corpus attests feminines CDSL omits. Plus variant/alternate
  spellings (b~v ≈ 397 MW pairs) and same-lemma multi-`<k2>` forms (comma-lists in SKD/VCP,
  which the now-2026 key2 split into separate lines). Policy (headword separately / fold with
  `mf(ā/ī)` / merge-and-cross-ref) is human; the candidate pair-lists are agent-doable. The
  MW/PWG print spine is largely unaffected (MW key2 = one clean form per entry).
## [0.0.17] - 2026-06-26

### Added — key2 re-extracted as SLP1 + a print-readiness checklist
- **key2 now regenerated as clean SLP1** into [`now-2026/`](HeadwordLists/now-2026/) for
  every dict (was key1-only). The 2014 key2 files are legacy numeric transliteration; the
  current `<k2>` is SLP1 but a naïve `<k2>([^<]*)` over-captured entry-body text / `{#..#}`
  compound blobs (a 64 MB dump). Fixed in `headword_diff.py` (`key2_forms`): stop the
  capture at the `¦` separator, strip `{#..#}`, split comma-lists → clean **print/citation
  form** keeping `/` accent, `-`/`—`, `(...)`, `*`, `˚` (e.g. `aMSa—karaRa`; SKD recovered
  40,817 vs the 64 MB blob). 23 now-2026 files (key1+key2; PD has no source).
- **[`HeadwordLists/PRINT_READINESS.md`](HeadwordLists/PRINT_READINESS.md)** — consolidates
  the A–E checks for publishing a printed headword list, with per-dictionary verdicts.
  **MW/PWG are the print-ready spine** (stable, +0.1 %/−0.0 % since 2014); the gates are
  human/editorial — **A** clear SanskritSpellCheck's 122 fileable typos (the "don't print
  known typos" pass, highest value), **B** coverage additions, **C** accents, **E** scope —
  while **D** (key2 as SLP1) is now closed.

## [0.0.16] - 2026-06-26

### Changed — foldered the snapshots (`then-2014/` + `now-2026/`) + % and TOTAL columns
- **Dated the snapshots.** The committed headword lists were verified (git) to have been
  extracted **2014-10-05** ("Cologne headwords"), so all 31 root `*.txt` now live in
  [`HeadwordLists/then-2014/`](HeadwordLists/then-2014/), and the current regeneration in
  [`HeadwordLists/now-2026/`](HeadwordLists/now-2026/) (was `now/`). Paths updated across
  the README, the Huet doc, and `huet_coverage.py`.
- **`NOW_VS_THEN.md` gains a `growth %` column and a TOTAL row.** Net change per list
  (e.g. **AP +146.6 %**, PWK +14.7 %, MW +0.1 %) and the aggregate over the 9 comparable
  lists: **605,813 → 733,617 (+21.1 %)**; grand total of all 26 snapshots' then-counts =
  1,721,983.

## [0.0.15] - 2026-06-26

### Added — `HeadwordLists/now/` current regeneration of the key1 snapshots
- Regenerated the **key1** lists from the **current** csl-orig into
  [`HeadwordLists/now/`](HeadwordLists/now/) (filename = now-count), Sanskrit-collated;
  the parent THEN files are kept frozen so the two can be compared directly.
  `headword_diff.py now` produces them.
- **key1 only, deliberately** — it's the genuinely comparable set (THEN and NOW both
  SLP1 `<k1>`). key2 is skipped: the THEN `<k2>` is legacy numeric transliteration
  (format migration, not a headword diff), and several dicts' raw `<k2>` is `{#..#}`
  compound blobs, not lemmas (a naïve dump was 64 MB of markup). 8 written
  (AP, GRA, MW, PWG, PWK, SKD, VCP, VEI); PD has no csl-orig source.
- Notable now-counts: **AP 88,867** (was 36,030), **PWK 151,349** (was 131,918),
  **MW 194,084**, PWG 106,082, VCP 48,636. `now/README.md` documents scope + the
  Sanskrit-collation (compare by set, not line-diff) caveat; refreshed `NOW_VS_THEN.md`
  to match (csl-orig had drifted a little since the previous run).

## [0.0.14] - 2026-06-26

### Added — `HeadwordLists/` drift tooling, Huet/INRIA control, accent check, use cases
- **Now-vs-then diff of the `*-unique-key{1,2}-N.txt` snapshots.** `headword_diff.py`
  regenerates each list from current csl-orig; `NOW_VS_THEN.md` is the summary. The
  **key1** (SLP1) lists are comparable and have drifted: **AP 36,030 → 88,701**,
  **PWK 131,918 → 151,349** (large real growth), **MW 193,978 → 194,084** (+753/−647),
  PWG/GRA/SKD/VCP/VEI small. The **key2** snapshots are in the *legacy Cologne numeric
  transliteration* (`am2s4a` = aṃśa) vs current SLP1 — a format migration, flagged not
  reported. PD is not in csl-orig. (`removed`-word lists embedded for QA; scratch
  `_diff/` dumps gitignored.)
- **Huet / INRIA Heritage wordlist** — a non-Cologne control alongside Catalan-Pujol.
  `huet_coverage.py` decodes Huet's VH/Velthuis (`z`=ś, `f`=ṅ, `.s`=ṣ, `aa/ii/uu`) to
  IAST→SLP1 and runs the same coverage. 21,055 keys, **MW 83.5 % / all CDSL 86.2 %,
  DCS-attested 60.0 %**. Headline ([`Huet-INRIA-Wordlist-vs-Cologne.md`]): both are MW
  subsets, but the reader's lexicon is far more corpus-attested than Pujol's full
  dictionary spine (60 % vs 46 %) — less dictionary "dark matter".
- **Catalan-Pujol additions.** The full 177-lemma corpus-attested-no-CDSL list
  (`DCS-attested-no-CDSL.md`, §5, triaged); the **accent comparison** (§7,
  `accent_compare.py`): Pujol marks udātta with a combining acute, Cologne with `/`
  after the vowel, but **~97 %** agree on position (GRA 96.9 %, MW 97.1 %).
- **Use-case sections** added to all three studies: Catalan-Pujol §8 (CDSL gloss layer,
  corpus-confirmed candidate headwords, editor QA list, morphology overlay, learner's
  layer), Huet §5 (corpus-weighted core vocab, VH↔SLP1 bridge, benchmark), and
  `NOW_VS_THEN.md` (snapshot refresh, removed-word audit, re-transcoding triage).

## [0.0.13] - 2026-06-26

### Added — `HeadwordLists/Catalan-Pujol/` dataset + full coverage analysis
- **The dataset.** An external Sanskrit headword spine and its CDSL/corpus coverage
  analysis: the **61,266-lemma list** of the *Diccionari Sànscrit–Català* (Òscar Pujol,
  Enciclopèdia Catalana, 2005 — the first Sanskrit→Catalan dictionary), mirrored from
  `sanskrit-lexicon/CORRECTIONS`. In accented IAST with `√`-roots, Vedic udātta, and
  Pujol's compound-segmenting hyphens; UTF-8 **with BOM**.
- **Dictionary axis** — the list is essentially a Monier-Williams subset: **MW alone
  covers 88.5 %**, all 15 compared CDSL dicts together 91.0 %; the ~4,680 lemmas no CDSL
  dictionary covers are bucketed (simple / compound / root / prefixed-root / suspect-char)
  under `Catalan-uncovered/`. Two transcoding traps documented (display-added line
  numbers; `ś`=s+U+0301 accent collision; match rate 78 %→89 % after the fix).
- **Corpus axis (vs DCS)** — only **46.4 %** of the list is attested in the DCS-2021
  corpus though 91 % sits in a dictionary; **44.9 % is dictionary-listed but
  corpus-unattested** ("lexicographic dark matter"). The 0.3 % (177) corpus-attested with
  no CDSL entry is **triaged**: ~55 lemmatisation/morphology convention (41 prefixed/
  denominative verb roots, 9 productive `-tā/-tva/-tara/-tama/-vat`, 5 bīja), 29
  unheadworded compounds, ~93 simple/feminine — within which a genuine residue of
  corpus-attested **rare lexemes absent from all 43 CDSL dictionaries** (plant/animal
  names: `alasāndra-` cowpea, `kustumburī-` coriander, `kaṅkolī-`, `udumbarī-`, …) are
  real candidate additions.
- **Pujol's 11 headword conventions documented** (§6): `√`-roots, preverb+root
  segmentation with `√` on the final root, sandhi-resolution parens, Vedic udātta,
  compound hyphens, stem/feminine/productive-suffix forms, homograph numbering, bīja
  syllables, BOM + precomposed-`ś` encoding, and export artifacts.
- **Scripts** (repo-portable, IAST→SLP1 via `sanskrit-util`): `coverage_by_dict.py`,
  `match_rate.py`, `make_uncovered_lists.py`, and `coverage_vs_dcs.py` (dictionary ×
  corpus cross-tab against `VisualDCS/dcs_lemma_summary.json`). Full write-up in
  `HeadwordLists/Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md`; indexed in
  `HeadwordLists/README.md`.

> Provenance note: the dataset files were first committed in `56564a0` (initially via an
> accidental `git add -A`), then adopted and refactored repo-portable by a parallel
> session (`75b917d`); kept by decision. This entry consolidates all Pujol work.

## [0.0.12] - 2026-06-26

### Changed
- **`article-comparison/*.table.md` — rows ordered chronologically by edition year**
  (oldest → newest), so the side-by-side reads as the lexicographic tradition
  developing: WIL 1832 → YAT 1846 → BOP 1847 → PWG (Bd. I) 1855 → … → AP 1957 →
  PE 1975 → PD 1976. The `#` column renumbers to the new order. Sorting is in
  `_build_tables.py` (stable on the prior order for same-year ties, e.g. BUR/BEN 1866,
  GRA/VCP 1873, pw/PWK 1879).

## [0.0.11] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — full, untruncated entries.** The side-by-side
  tables previously capped each cell at ~800 chars with a trailing ` …`, so longer
  entries (e.g. STC, PWG, AP90, VCP, PE) showed only a fragment. Every cell now
  carries the **complete** condensed entry (citations in `[ ]` stripped, SLP1→IAST,
  paragraphs joined with ▸); PD remains its full sense skeleton (its verbatim entry is
  20–234 KB and stays in the verbatim/IAST files). 40 truncated cells expanded.

### Added
- **`RussianTranslation/src/_build_tables.py`** — the table builder, now committed (it
  never was). Regenerates all four tables from the full `*.iast.md` sections (+ the
  `*.pd-min.md` skeleton for the PD row), reproducing the original condensation but
  without the length cap, and with **nested-citation-safe** bracket stripping (fixes a
  stray `]` the old run left on `[m., [RāmatUp.]]`-style nested refs, e.g. akṣara/MW).

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
