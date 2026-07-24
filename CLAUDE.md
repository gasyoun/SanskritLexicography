# CLAUDE.md

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
[`progress_dashboard/`](progress_dashboard)) — plus a root
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
Control-plane tools (FEATURES_INDEX **L11**):
[`cohort_engine.py`](RussianTranslation/src/pilot/cohort_engine.py) (offline multi-profile),
[`no_pwg_residual_ledger.py`](RussianTranslation/src/pilot/no_pwg_residual_ledger.py) (C-49).
**`<ab>`/`<ls>` tooltips + RU-column abbreviation purity** (a pwg_ru-specific
policy, distinct from mw_ru's "leave `<gram>` untouched" rule above —
grammatical-category abbreviations stay international Latin with a tooltip,
editorial/cross-reference ones translate to Russian, both decided 10-07-2026):
[`RussianTranslation/ABBREVIATIONS_RU.md`](RussianTranslation/ABBREVIATIONS_RU.md).

## Authoring conventions

- Markdown is the primary authored format (roadmap, changelog, lectures, the
  `mw_ru` docs). Keep it lint-clean and link-check-clean (see CI above).
- [`changelog.md`](changelog.md) uses dated maintenance snapshots; keep upcoming
  work under `[Unreleased]` until it gets a dated entry.
- [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) frames the research direction
  (evidence-graded lexicography, csl-atlas review, paper pipeline P1–P6) and is
  the orientation document for how this repo connects to the broader project.
- Per the global rule, render every path/URL as a clickable Markdown link in
  chat and in GitHub issue/PR/release bodies. Do not put repository file paths
  in bare backticks when a human is expected to click them. In GitHub bodies,
  use full `blob`/`tree` URLs; relative links do not resolve reliably there.

## Operational hazard notes

Destructive-risk facts for this repo (do-not-rerun scripts, decoys, traps) are
registered centrally in an org-private hub
([Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md),
org members only); the public-safe subset is mirrored in the generated block of
[AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/AGENTS.md). Check them
before running anything that writes.
