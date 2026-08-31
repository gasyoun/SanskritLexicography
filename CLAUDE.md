# CLAUDE.md

_Created: 06-08-2026 · Last updated: 31-08-2026_

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Org-level conventions (the wider `sanskrit-lexicon` ecosystem, the csl-orig
> correction workflow, GitHub issue taxonomy, `.ai_state.md` protocol, Windows
> encoding rules) live in [`../CLAUDE.md`](../CLAUDE.md) and are loaded
> automatically. This file covers only what is specific to **this** repository.

## What this repository is

Primarily a **data and research workspace** — most of the tree is exported
headword lists, large reference HTML/PDF documents, AI-produced Russian
translations of Monier-Williams and the Petersburg Dictionary, and
Russian-language teaching material on Sanskrit syntax. But it is **no longer
code-free** (the earlier "no `.py`" framing is stale): several subprojects now
carry substantial Python tooling — the two translation pipelines under
[`RussianTranslation/src/`](RussianTranslation/src), the headword tooling in
[`HeadwordLists/`](HeadwordLists), the site builder
[`docs_site/build_site.py`](docs_site/build_site.py), the three dashboard
generators ([`epistemic_dashboard/`](epistemic_dashboard),
[`findings_dashboard/`](findings_dashboard),
[`progress_dashboard/`](progress_dashboard) — public web kitchen at
[/progress/](https://gasyoun.github.io/SanskritLexicography/progress/), browser
poll **60 s**; local ops twin is
`RussianTranslation/src/pilot/dashboard_server.py` → `127.0.0.1:8765`, poll
**5 s** — see [progress_dashboard/README](progress_dashboard/README.md) and
[RU deep manual §2d](docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)) — plus a root
[`requirements.txt`](requirements.txt). Treat the repo as **hybrid**: a
data/docs workspace with live tooling embedded in the active subprojects, so
"working in the codebase" spans inspecting/transforming text data, authoring
Markdown, **and** the pipeline/tooling code. For orientation by audience, see
[`docs/manuals/`](docs/manuals).

There is no single top-level build, but there **are** tests/selftests (e.g.
[`docs_site/test_docs_site.py`](docs_site/test_docs_site.py) and the
RussianTranslation gate selftests) and CI exercises them. CI
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs Markdown lint,
Markdown link-check, YAML lint, a **Python lint job that now fires** (`.py`
files exist — the earlier "never fire because no such files exist" is stale), a
conditional JS lint, a **RussianTranslation gates** job that compiles the
pipeline scripts and runs their fixture selftests, and a **docs-site pytest**
job that runs `docs_site/test_docs_site.py`. The active pre-commit hooks
([`.pre-commit-config.yaml`](.pre-commit-config.yaml)) are `check-yaml`,
`end-of-file-fixer`, `trailing-whitespace` (markdown-aware), and
`check-merge-conflict`, plus the local
`russian-translation-review-changelog` guard
(`review_changelog_guard.py --staged`). Match these when editing: no trailing
whitespace, newline at EOF, valid YAML.

## HeadwordLists/ — naming and key semantics

This is the analytical heart of the repo. The exports are split by era:
[`HeadwordLists/then-2014/`](HeadwordLists/then-2014) is the frozen 2014-era
snapshot, [`HeadwordLists/now-2026/`](HeadwordLists/now-2026) holds the current
regenerated exports (slightly different counts). Filenames encode source, key
type, and count: `{DICT}-unique-{key1|key2}-{N}.txt`, where `N` is the entry
count (also the line count). Other patterns: `{DICT}-fehlerhaft-{N}.txt` (German
"erroneous" — flagged problem entries, e.g. [`HeadwordLists/then-2014/PWG-fehlerhaft-1661.txt`](HeadwordLists/then-2014/PWG-fehlerhaft-1661.txt),
which contain full XML records, not bare headwords), `SCH-accents-IAST-{N}.txt`
(accented IAST forms), and cross-dictionary join files like
[`HeadwordLists/then-2014/mw-apte-mcdonell-hk.txt`](HeadwordLists/then-2014/mw-apte-mcdonell-hk.txt)
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

## Dual changelog — shared 1.144.x namespace (H3258)

This repo has **two** Keep-a-Changelog files that share the **same** version
series. `/cut-release` must treat them as one namespace:

- [CHANGELOG.md](CHANGELOG.md) — repo-level
- [RussianTranslation/CHANGELOG.md](RussianTranslation/CHANGELOG.md) — pwg_ru project

The mechanical gate is [`Uprava/tools/cut_release.py`](https://github.com/gasyoun/Uprava/blob/main/tools/cut_release.py): before writing a heading it unions both files, `CITATION.cff` `version:`, and `git ls-remote --tags`. An explicit `--version` already used fails with exit 5 (replay: `python Uprava/tools/cut_release.py . --version 1.144.79` — H3144 cut that number from the nested file on 19-08-2026 while H3152 claimed it in the root file). Auto-bump stops after 5 tries. **Do not delete one changelog to resolve a collision.**

**Windows alias.** `CHANGELOG.md` and `changelog.md` are the same NTFS file; git tracks one spelling. Always `git add` the path `git ls-files` reports (Uprava FINDINGS §74 / §100 / §173 / §348). `ReverseDictionary/CHANGELOG.md` and `Digital_Sanskrit_Lexicography-BOOK/CHANGELOG.md` keep an independent `1.0.x` series and are **not** in this union.

## Encoding — BOM is inconsistent, check before editing

The org rule is "csl-orig files never have BOMs," but **that does not hold here**.
These are exports from many sources: some have a UTF-8 BOM, some do not (e.g.
[`HeadwordLists/then-2014/MW-unique-key1-193978.txt`](HeadwordLists/then-2014/MW-unique-key1-193978.txt)
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

## RussianTranslation/ — pwg_ru (PWG→RU/EN, a separate pipeline from mw_ru above)

**This directory is the code home for the private `pwg-ru-data` repo** — `pwg-ru-data`
holds the data (rights-fenced storage for the pwg_ru pipeline's outputs), and every
tool, prompt, pipeline stage, and doc that operates on it lives here in
`RussianTranslation/`. A session that lands in `pwg-ru-data` reads its own `CLAUDE.md`
pointer back to this repo before doing anything else (H3564, ruling F6).

A second, independent translation effort in the same directory: PWG
(Böhtlingk-Roth, "Petersburg Dictionary") → Russian (primary) and English
(secondary), run headword-by-headword at scale (749 DCS-attested verb roots
alone; store ~11.6k sense rows as of 24-07-2026). **Production route (H1110):**
profile-bound **headless CLI on manifest v2**
(`headless_worker.py` / `coordinator.py` / `bounded_staged_run.py`); the Max
Workflow lane is forensics only. Start at
[`RussianTranslation/PIPELINE_HISTORY.md`](RussianTranslation/PIPELINE_HISTORY.md)
for the chronological "how did we get here" orientation (major fixes,
recurring failure patterns, current state) before touching any pwg_ru code —
it exists specifically so a fresh session doesn't rediscover an already-fixed
bug. Editor-facing format + status:
[`RussianTranslation/pwg_ru.md`](RussianTranslation/pwg_ru.md). Live operating
procedure:
[`RussianTranslation/src/pilot/RUN_FREQ_MAX.md`](RussianTranslation/src/pilot/RUN_FREQ_MAX.md)
(+ operator depth
[`docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md`](docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)).
Paid windows require a fresh live-gate GO before spend. **Sync rule (H1618):** any
change to `--max-agents` semantics, residual registry schema, or cohort barrier rules
must update `RUN_FREQ_MAX.md` + `RussianTranslation/Agents.md` + the
`/pwg-bounded-run` skill in the same PR (copy-paste of canary `--max-agents 1` onto
multi-key windows re-creates the only-b0 starvation class). Cross-language
(RU/EN, and any future language) fix-parity policy — mandatory classification
of every fix as SHARED / INTENTIONAL-DIVERGENCE / GAP before closing a
session, mechanically enforced by a selftest gate:
[`RussianTranslation/LANG_PARITY.md`](RussianTranslation/LANG_PARITY.md).
Live session journal: [`RussianTranslation/.ai_state.md`](RussianTranslation/.ai_state.md).
**Control plane (H3714, Wave 1, 31-08-2026):**
[`RussianTranslation/src/pwg_pipeline/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pwg_pipeline) is the
supported facade for the PWG lifecycle — one transactional campaign database, one shared
paid-call kernel, pure audit, and journal-only promotion. It is a *strangler layer*: the
proven Claude headless engine is shadowed, not rewritten, and the legacy PWG-TM writers
still run (see
[`compat.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/compat.py) for the verb map and the
criterion that would disable them). Wave 1 closed **PARTIAL** — no provider canary and no
independent review receipt yet, so no cutover:
[WAVE1_REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/WAVE1_REPORT_RussianTranslation_PWG_CONTROL_PLANE_31-08-2026.md).
Control-plane tools (FEATURES_INDEX **L11**):
[`cohort_engine.py`](RussianTranslation/src/pilot/cohort_engine.py) (offline multi-profile),
[`no_pwg_residual_ledger.py`](RussianTranslation/src/pilot/no_pwg_residual_ledger.py) (C-49).
**Gate-evidence contract (H3748, W1, 31-08-2026):** every pwg_ru gate builds its verdict
*through* [`RussianTranslation/src/pilot/gate_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gate_evidence.py)
— hashed inputs, predicate evaluation + hit counts, a JSON sidecar, and
`assert_nonvacuous()`, which turns a PASS that examined nothing into a hard FAIL
([#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803)). Emptiness that is
legitimate is **declared by pre-registered name** (`LEGITIMATE_EMPTY` + the spike,
[SPIKE_PWG_GATE_EVIDENCE_LEGITIMATE_EMPTY_CLASSES_31-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/SPIKE_PWG_GATE_EVIDENCE_LEGITIMATE_EMPTY_CLASSES_31-08-2026.md)),
never inferred from silence. **Adding or touching a gate: build its verdict through a
`GateEvidence` record and register its `gate_id`** — CI's
`gate_evidence.py --require <gate_id>` fails when a gate leaves no sidecar. G9
(`validate_interop.py`) is expected **RED on the shipped
[`RussianTranslation/release/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release) artifacts**: they carry 12,374
duplicated entry ids ([#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798));
re-cutting them is a publication decision (Zenodo DOI), not a code fix.

**Printed-locus invariant (H3751, 31-08-2026):** `~~h<N>` in a pwg_ru sub-card key is a
0-based `enumerate` index over a headword's PWG records, **never** a printed homonym
number — comparing it against the source `<h>` (which starts at 1) is the #1801 defect
that put another homograph's column on 1,278 store rows. Resolve it positionally through
[`RussianTranslation/src/pwg_homonym.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_homonym.py),
and never re-spell the key: it is the identity of 11k already-promoted rows. FINDINGS §617.

**`<ab>`/`<ls>` tooltips + RU-column abbreviation purity** (a pwg_ru-specific
policy, distinct from mw_ru's "leave `<gram>` untouched" rule above —
grammatical-category abbreviations stay international Latin with a tooltip,
editorial/cross-reference ones translate to Russian, both decided 10-07-2026):
[`RussianTranslation/ABBREVIATIONS_RU.md`](RussianTranslation/ABBREVIATIONS_RU.md).

## Authoring conventions

- Markdown is the primary authored format (roadmap, changelog, lectures, the
  `mw_ru` docs). Keep it lint-clean and link-check-clean (see CI above).
- [`CHANGELOG.md`](CHANGELOG.md) uses dated maintenance snapshots; keep upcoming
  work under `[Unreleased]` until it gets a dated entry.
- [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) frames the research direction
  (evidence-graded lexicography, csl-atlas review, paper pipeline P1–P6) and is
  the orientation document for how this repo connects to the broader project.
- Per the global rule, render every path/URL as a clickable Markdown link in
  chat and in GitHub issue/PR/release bodies. Do not put repository file paths
  in bare backticks when a human is expected to click them. In GitHub bodies,
  use full `blob`/`tree` URLs; relative links do not resolve reliably there.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues in `gasyoun/SanskritLexicography`, driven by the `gh` CLI; PRs are **not** a triage surface. See [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md).

### Triage labels

The five canonical triage roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) are used as-is. See [docs/agents/triage-labels.md](docs/agents/triage-labels.md).

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at the repo root (created lazily); `CLAUDE.md` carries the current domain vocabulary. See [docs/agents/domain.md](docs/agents/domain.md).

## Operational hazard notes

Destructive-risk facts for this repo (do-not-rerun scripts, decoys, traps) are
registered centrally in an org-private hub
([Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md),
org members only); the public-safe subset is mirrored in the generated block of
[AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/AGENTS.md). Check them
before running anything that writes.
