# CLAUDE.md

_Created: 06-08-2026 · Last updated: 08-09-2026_

This file guides Claude Code in this repository.

> Org-level conventions (the wider `sanskrit-lexicon` ecosystem, the csl-orig
> correction workflow, GitHub issue taxonomy, `.ai_state.md` protocol, Windows
> encoding rules) live in [`../CLAUDE.md`](../Uprava-h4060-drain/CLAUDE.md) and load
> automatically. This file covers only what is specific to **this** repository.

## What this repository is

Primarily a **data and research workspace**: exported headword lists, large
reference HTML/PDF documents, AI-produced Russian translations of
Monier-Williams and the Petersburg Dictionary, Russian teaching material on
Sanskrit syntax. **Not code-free** — substantial Python tooling in the two
translation pipelines under
[`RussianTranslation/src/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src), the headword tooling in
[`HeadwordLists/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists), the site builder
[`docs_site/build_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/build_site.py), three dashboard generators
([`epistemic_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/epistemic_dashboard), [`findings_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard),
[`progress_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/progress_dashboard) — public kitchen at
[/progress/](https://gasyoun.github.io/SanskritLexicography/progress/), local ops twin
`dashboard_server.py` → `127.0.0.1:8765`). Treat as **hybrid**: work spans
data/docs and pipeline code. Orientation by audience: [`docs/manuals/`](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals).

No single top-level build, but tests/selftests exist (e.g.
[`docs_site/test_docs_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/test_docs_site.py)) and CI
([`.github/workflows/ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)) runs Markdown/YAML/Python/JS lint, link-check,
RussianTranslation gates, docs-site pytest, and an **offline contract-pins**
job (H4353) running
[`tests/run_offline_suite.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tests/run_offline_suite.py) — 201 pins over 62 modules, network off,
fixtures under `tests/fixtures` only, literal record-count floors per
headword list (evidence:
[`tests/OFFLINE_CONTRACT_PINS_08-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/tests/OFFLINE_CONTRACT_PINS_08-09-2026.md)). **Regenerating a list or
changing a parser updates the pinned floor/vector in the same PR** — a
shrink or silent contract change fails CI by design. Pre-commit hooks
([`.pre-commit-config.yaml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.pre-commit-config.yaml)): `check-yaml`, `end-of-file-fixer`,
`trailing-whitespace`, `check-merge-conflict`, plus local
`russian-translation-review-changelog`.

## HeadwordLists/ — naming and key semantics

The analytical heart of the repo. Exports split by era:
[`then-2014/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014) frozen snapshot,
[`now-2026/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026) current regenerated exports (slightly
different counts). Filenames encode source/key/count:
`{DICT}-unique-{key1|key2}-{N}.txt` (`N` = entry/line count),
`{DICT}-fehlerhaft-{N}.txt` (German "erroneous" — flagged entries with full
XML records, not bare headwords, e.g.
[`PWG-fehlerhaft-1661.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/PWG-fehlerhaft-1661.txt)), `SCH-accents-IAST-{N}.txt` (accented IAST),
cross-dictionary joins like
[`mw-apte-mcdonell-hk.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/mw-apte-mcdonell-hk.txt) (Harvard-Kyoto, sorted).

**key1 vs key2:** key1 = normalized computational key, may not match any
printed form (matching/dedup/joins); key2 = closer to printed source
(retains `-`, `--`, `/` accents, e.g. `a/MSa`, `a--kAra`; editorial review,
checking digitized text against the scan).

Dictionary codes: AP, BHS, BUR, CAE, CCS, GRA, INM, MD, MW, PD, PWG, PWK, SCH,
SKD, VCP, VEI (table: [`README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/README.md)).

## Dual changelog — shared 1.144.x namespace (H3258)

Two Keep-a-Changelog files share the **same** version series;
`/cut-release` treats them as one namespace:
[CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CHANGELOG.md) (repo-level),
[RussianTranslation/CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md) (pwg_ru). Gate:
[`Uprava/tools/cut_release.py`](https://github.com/gasyoun/Uprava/blob/main/tools/cut_release.py) unions both files, `CITATION.cff` `version:`, and
`git ls-remote --tags` before writing a heading; a used `--version` fails
exit 5. Auto-bump stops after 5 tries. **Do not delete one changelog to
resolve a collision.**

**Windows alias.** `CHANGELOG.md`/`changelog.md` are the same NTFS file; git
tracks one spelling — always `git add` the path `git ls-files` reports
(Uprava FINDINGS §74/§100/§173/§348). `ReverseDictionary/CHANGELOG.md` and
`Digital_Sanskrit_Lexicography-BOOK/CHANGELOG.md` keep an independent `1.0.x`
series, **not** in this union.

## Encoding — BOM is inconsistent, check before editing

Org rule "csl-orig files never have BOMs" **does not hold here**: some
exports carry a UTF-8 BOM, some don't (e.g.
[`MW-unique-key1-193978.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/MW-unique-key1-193978.txt) **has** BOM `EF BB BF`; its key2 sibling does
**not**). Before transforming a file: `head -c 3 file | xxd`, preserve the
existing BOM state on write, never silently add/strip one. All UTF-8.

Files too large for an editor: `sanhw1.xlsx`,
`DCS_statistical_evaluation.htm` (~75 MB), `DCS-Moniers-roots-w-references.html`
(~16 MB), PWG/PWK error lists — use streaming/CLI tools, not Read.

## RussianTranslation/ — mw_ru

[`mw_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md) documents how the AI Russian translation of Monier-Williams was
produced (287,358 cards, multi-pass, multi-model). Per-stage prompts:
[`mw_ru_prompts/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/mw_ru_prompts) — one per stage (translate → two independent QA judges →
re-translate rejects). **Key format invariant:** only the English "wrapper"
prose is translated; Sanskrit (`<s>`), grammar abbreviations (`<gram>`),
source refs (`<ls>`) stay untouched deliberately. Most content is in Russian.

## RussianTranslation/ — pwg_ru (PWG→RU/EN, separate pipeline from mw_ru)

**Code home for the private `pwg-ru-data` repo** — it holds the rights-fenced
data; every tool/prompt/stage/doc operating on it lives here. A session in
`pwg-ru-data` reads its own `CLAUDE.md` pointer back to this repo first
(H3564, ruling F6).

Independent effort: PWG (Böhtlingk-Roth) → Russian (primary) + English
(secondary), headword-by-headword at scale (~11.6k sense rows as of
24-07-2026).

- **Production (H1110):** headless CLI on manifest v2 (`headless_worker.py` /
  `coordinator.py` / `bounded_staged_run.py`); Max Workflow lane is forensics
  only. Orientation:
  [`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md). Format+status:
  [`pwg_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md). Procedure:
  [`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) (+
  [deep manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)). Paid windows need a fresh live-gate GO. **Sync
  (H1618):** `--max-agents`/registry-schema/cohort-barrier changes update
  `RUN_FREQ_MAX.md` + `Agents.md` + `/pwg-bounded-run` same PR.
- **Fix-parity:** every fix classified SHARED / INTENTIONAL-DIVERGENCE / GAP
  before closing, gated by a selftest:
  [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md).
- **Control plane (H3714):**
  [`src/pwg_pipeline/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pwg_pipeline) — supported PWG-lifecycle facade: one campaign DB, one
  paid-call kernel, pure audit, journal-only promotion. Strangler layer over
  the proven headless engine; legacy PWG-TM writers still run
  ([`compat.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/compat.py)). Wave 1 closed **PARTIAL** (no provider canary, no
  independent review, no cutover):
  [WAVE1_REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/WAVE1_REPORT_RussianTranslation_PWG_CONTROL_PLANE_31-08-2026.md). Tools:
  [`cohort_engine.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cohort_engine.py), [`no_pwg_residual_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_residual_ledger.py).
- **Enumeration tiers are FOUR, not two (H3948):**
  [`microstructure.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure.py) is the one sanctioned reading of PWG's four
  printed tiers — never re-derive from a marker's shape. Tier-rule change ⇒
  re-run [`microstructure_four_tier_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure_four_tier_selftest.py) + re-measure with
  [`pwg_four_tier_store_impact.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_four_tier_store_impact.py) same PR
  ([report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3948_four_tier_store_impact.json): 28.02% affected). A tier ambiguous in print
  stays unsplit, counted unresolved — **never guessed**
  ([FINDINGS §453](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
- **Gate-evidence contract (H3748):** every pwg_ru gate builds its verdict
  *through* [`gate_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gate_evidence.py) — hashed inputs, hit counts, a JSON
  sidecar, `assert_nonvacuous()` (a vacuous PASS is a hard FAIL, #1803).
  Legitimate emptiness is pre-registered by name (`LEGITIMATE_EMPTY` +
  [the spike](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/SPIKE_PWG_GATE_EVIDENCE_LEGITIMATE_EMPTY_CLASSES_31-08-2026.md)), never inferred from silence. New/changed gate registers a
  `gate_id` via `GateEvidence` — CI's `gate_evidence.py --require <gate_id>`
  fails on a missing sidecar. G9 (`validate_interop.py`) is expected **RED**
  on shipped [`release/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release) (12,374 duplicated ids, #1798) — re-cutting is a
  publication decision, not a code fix.
- **Printed-locus invariant (H3751):** `~~h<N>` in a pwg_ru sub-card key is a
  0-based `enumerate` index over PWG records, **never** the printed homonym
  number (source `<h>` starts at 1 — conflating them was #1801). Resolve
  positionally via
  [`pwg_homonym.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_homonym.py); never re-spell the key. FINDINGS §617.
- **`DHĀTUP.`→Palsule concordance — a same-author source is not an
  independent witness (H4349):** the concordance in
  [`build_dhatup_palsule.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dhatup_palsule.py)
  fills a coordinate from PWG first, then from **sibling passes** that run
  beside it rather than widening `_L` in place. MW may break a PWG tie — it is
  a different author, which is the whole coverage argument of H4339. **pw and
  PWG's dotted-id articles may not**: both are Böhtlingk, so a same-book
  claimant adds a vote to a tie the multi-claimant filter exists to drop, and
  may not invent a coordinate PWG never cites (Böhtlingk renumbered between
  editions — pw's `33,67` is pwg's `33,88`). Both classes are measured and
  **empty**; that is the result, not a gap. **Sync:** any change to the builder
  or a new sibling pass re-runs
  [`dhatup_h4349_verify.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/dhatup_h4349_verify.py)
  (17 checks, re-derives every published number from the artifact and the raw
  corpora **without importing the builder**; exits **2** when csl-orig is
  absent — a green run with zero checks was a real defect) **and**
  `ls_enrichment_selftest.py` in the same PR, and passes `same_book_conflicted`
  + `pwg_cited` to the new pass. **Since H4386 both are keyword-only with no
  default** — forgetting one is a `TypeError`, not an unscreened pass, which is
  exactly how the first cut shipped two wrong rows — and an empty `pwg_cited`
  raises rather than admitting everything. **The artifact is pinned to its
  builder:** `_stats.builder_sha256` carries the sha256 of
  `build_dhatup_palsule.py`, so a builder change without a rebuild fails the
  selftest; rebuild and commit the JSON in the same PR
  (`python src/build_dhatup_palsule.py --xls <the gitignored Palsule XLS>`).
- **`<ab>`/`<ls>` tooltips + RU-column purity** (grammatical abbreviations
  stay Latin with a tooltip, editorial ones translate to Russian):
  [`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md).
- **Abbreviation invariant (H3959):** every `<ab>` token belongs to one of
  three disjoint sets in
  [`pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py) — `RU_MAP` (Bucket A, **must** be Cyrillic),
  `BUCKET_B` (grammatical, stay Latin), `RESIDUE` (undecided, per-token
  reason). **Sync:** reclassifying a token runs `python pwg_ab_ru.py census`
  same PR. Never route Bucket-A to Latin. Ruling: [CONTRADICTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md);
  style rules 3.1–3.5: [style guide](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md).

## Cyrillic proper nouns — a lookup table, never reverse-transliteration rules

Russian scholarly indices print names in Cyrillic; no safe rule turns
Cyrillic back into SLP1 (FINDINGS §60). Only sanctioned mapping: the lookup
table
[cyrillic_proper_noun_slp1.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.tsv) — 534 rows, every key derived from an
IAST witness printed beside the Cyrillic form, **zero rule-derived keys**.

**Sync rule:** changing the table re-runs its builder
[h3985_cyr_slp1_table.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h3985_cyr_slp1_table.py) and refreshes
[H3985_cyr_slp1_validation.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3985_cyr_slp1_validation.json) **same PR** — `rule_derived_keys: 0` is the
invariant that makes the table citable. Never hand-add a row without an IAST
witness; the 20 pure-Cyrillic indices stay unkeyed until an onomasticon
covers them ([GAPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) §6).

## Authoring conventions

- Markdown is the primary authored format (roadmap, changelog, lectures,
  `mw_ru` docs); keep it lint-clean and link-check-clean (CI above).
- [`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CHANGELOG.md) uses dated maintenance snapshots; upcoming work stays
  under `[Unreleased]` until dated.
- [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) frames the research
  direction (evidence-graded lexicography, csl-atlas review, paper pipeline
  P1–P6) and orients this repo within the broader project.

## Agent skills

### Issue tracker

GitHub issues in `gasyoun/SanskritLexicography`, driven by `gh`; PRs are
**not** a triage surface. See
[docs/agents/issue-tracker.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/issue-tracker.md).

### Triage labels

Five canonical roles (`needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`), used as-is. See
[docs/agents/triage-labels.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/triage-labels.md).

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at repo root (lazy);
`CLAUDE.md` carries the current domain vocabulary. See
[docs/agents/domain.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/domain.md).

## Operational hazard notes

Destructive-risk facts (do-not-rerun scripts, decoys, traps) are registered
centrally in an org-private hub
([Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md), org members only); the public-safe subset is
mirrored in the generated block of
[AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/AGENTS.md). Check before running anything that writes.

_Dr. Mārcis Gasūns_
