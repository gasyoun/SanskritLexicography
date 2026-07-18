# Maintainer Manual — SanskritLexicography

_Created: 10-07-2026 · Last updated: 18-07-2026_

For the person (or agent) who **operates and extends** this repository. If you
just want to *use* the data, read the
[Data-Reuse Manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md)
instead; if you want the *research programme*, read the
[Researcher Manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md).

---

## 1. What this repository actually is

A **personal research-and-data workspace** for Sanskrit digital lexicography —
`gasyoun/SanskritLexicography`, default branch **`master`** (not `main`). It is
*not* part of the `sanskrit-lexicon` GitHub org (it is gasyoun-personal; confirm
with `git remote -v` before assuming org tooling applies). The unifying thesis
is **evidence-graded lexicography**: treat a dictionary as a layered evidence
graph where every claim carries source, evidence grade, corpus attestation, and
review provenance (see the
[Researcher Manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md)
and
[ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)).

**The hybrid framing.** The repo-level
[CLAUDE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md)
says the same since 10-07-2026 (the older "no source code / no `.py`" wording
is gone): the *root* is data + Markdown, but several subprojects carry
substantial Python — the two translation pipelines in
[RussianTranslation/src/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src),
the headword tooling in
[HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists),
the site builder in
[docs_site/build_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/build_site.py),
and the three dashboard generators. Treat the repo as **hybrid**: a data/docs workspace with
live tooling embedded in the active subprojects.

## 2. The subprojects — one map

| Directory | What | State | Primary reader |
|---|---|---|---|
| [RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) | Two LLM translation pipelines: `mw_ru` (Monier-Williams → RU, 287,358 cards, **done**) and `pwg_ru` (Petersburg Dict → RU/EN, **live production**, ~106k headwords) + grammar/TM assets. 714 tracked files as of 18-07-2026 (+ a large gitignored local store/TM not in a clone). | Active | maintainer + researcher |
| [HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) | Headword exports across ~16 CDSL dictionaries; key1/key2 semantics; comparison + union tooling | Active | data-reuser |
| [Digital_Sanskrit_Lexicography-BOOK/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK) | Book draft — 12 of the ~14 planned chapters drafted as of 18-07-2026, plus BOOK_PLAN / BRILL_PROPOSAL / RIGHTS_TABLE / LITERATURE_CROSSWALK and its own CHANGELOG (venue: de Gruyter primary since the M01 ruling) | Active | researcher |
| [papers/](https://github.com/gasyoun/SanskritLexicography/tree/master/papers) | Paper-pipeline notes/reviews/data (A30–A58 as of 18-07-2026: A30, A31, A33–A43, A58) | Active | researcher |
| [Syntax-Lectures/](https://github.com/gasyoun/SanskritLexicography/tree/master/Syntax-Lectures) | Russian particle-syntax lectures + interactive HTML explorer | Active | **student** |
| [ReverseDictionary/](https://github.com/gasyoun/SanskritLexicography/tree/master/ReverseDictionary) | Working materials for an unpublished reverse dictionary (~266,820 headwords) | Active | researcher/student |
| [IndischeSprueche/](https://github.com/gasyoun/SanskritLexicography/tree/master/IndischeSprueche) | Böhtlingk subhāṣita dataset (7,537 JSONL records) | Active (minimal) | data-reuser |
| [article-comparison/](https://github.com/gasyoun/SanskritLexicography/tree/master/article-comparison) | Cross-dictionary single-article study (4 finalists) | Complete | researcher |
| [literature/](https://github.com/gasyoun/SanskritLexicography/tree/master/literature) | Reference PDF/EPUB library + Markdown extractions + Lexicography-Manuals | Reference store | researcher |
| [docs_site/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site) | Static site built from research docs (zettelkasten); built and tested, **not deployed** (origin/gh-pages has no `research/` directory) — deploy is human-gated | Active | maintainer |
| [epistemic_dashboard/](https://github.com/gasyoun/SanskritLexicography/tree/master/epistemic_dashboard) · [findings_dashboard/](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard) | Generated HTML dashboards over the governance registries below | Active | maintainer |
| [progress_dashboard/](https://github.com/gasyoun/SanskritLexicography/tree/master/progress_dashboard) | Generated HTML dashboard tracking PWG→RU translation progress (per-lane denominators), companion to the article site | Active | maintainer |

## 3. The governance / epistemic layer — the load-bearing part

This is what distinguishes the repo from a pile of exports, and the thing most
likely to rot if you don't feed it. There are **nine registries at the root**,
each append-only:

- [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  — the empirical registry. **Schema per finding:** a `### §N` heading (the
  number is the stable citation, never reused/shifted — append-only; **a norm with known breaches**: H616 renumbered seven duplicate pairs to §70–§75 on 11-07-2026, and fresh duplicates exist again as of 18-07-2026 — §80, §86, §87 each carry two findings, repair queued — so cite by number **plus date/title** until renumbered), the
  **claim** in bold with a colour dot (🔴 important · 🟠 medium · 🟡 minor),
  then `Evidence:` (a number / file+line), `Implication:` (what to do), and a
  blockquoted `Source` line tagged `— repo · date`. **No HTML, ever** — use a
  `> ` blockquote for muting. Only *measured* facts go here.
- The **seven epistemic siblings** —
  [ASSUMPTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md),
  [CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md),
  [GAPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md),
  [DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md),
  [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md),
  [STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md),
  [GLOSSARY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md)
  — hold the acts FINDINGS can't: relying on an unproven premise, a source
  disagreement, a not-yet-measured gap, an abandoned approach, a reproducible
  recipe, a decaying fact, a defined term. Same 🔴🟠🟡 dots. Auto-seeded by
  [sanskrit-util/tools/epistemic/](https://github.com/sanskrit-lexicon/sanskrit-util/tree/main/tools/epistemic).
- [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md)
  — capability inventory (dicts / interfaces / datasets / tools, each with a
  real example + stable ID).

**Two dashboards render these** and are regenerated, not hand-edited:

```sh
python epistemic_dashboard/build_epistemic_dashboard.py \
  --dir . --side sanskrit \
  --repo-url https://github.com/gasyoun/SanskritLexicography/blob/master \
  --out epistemic_dashboard/epistemic.json   # all four flags are required
python findings_dashboard/build_findings_data.py   # -> findings_dashboard/data.json + timeseries.json (index.html is a static viewer, never touched)
```

The findings dashboard publishes to
<https://gasyoun.github.io/SanskritLexicography/findings/> (importance/section
breakdown, staleness flags, monthly time series, platform-liveness board;
refreshed monthly via
[findings_dashboard/monthly_refresh.py](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/monthly_refresh.py)).

**The append reflex is the whole point.** If you spend >10 min measuring a
non-obvious fact, it belongs in FINDINGS in the *same pass*; a caveat you relied
on → ASSUMPTIONS; a fork you couldn't resolve → CONTRADICTIONS; an approach you
killed → DEAD_ENDS. The registries are only as good as the last session that
fed them. Route Sanskrit-data facts here; route infra/platform/process gotchas
to [Uprava/FINDINGS.md](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
instead.

## 4. The RussianTranslation pipelines — read before you touch

This subproject is the largest and the easiest to break. Start at its own
[README](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/README.md),
then
[PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
(chronological "how did we get here" — it exists so you don't rediscover an
already-fixed bug). The live operating procedure is
[src/pilot/RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md).

**Hard guardrails — violating these is how the pipeline burns money or corrupts
output:**

- **Cost gate first, always:**
  [src/pilot/perf_preflight.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py)
  estimates agents/tokens/$ and refuses over-ceiling windows. Never launch a
  window without it.
- **≤3 concurrency.** The concurrency cliff (18-wide → 117 transient nulls) is
  measured; the standing rule is ≤3-wide.
- **Multi-agent fan-outs run *only* through
  [src/synth_dispatch.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py)**
  (≤4 concurrency, 10-min output-file kill-guard, sealed single-owner outputs,
  watcher-safe landing) — never bare async dispatches.
- **Never bulk-run `kAla`-class monster windows.** Preflight partitions mixed
  windows into `run_now` / `defer_monster`; keep the monster deferred. A single
  expensive card can cost ~2M tokens/window (see the pwg_ru staged-run history in
  [Uprava](https://github.com/gasyoun/Uprava) — gated, don't relaunch blind).
- **Output is accepted only by
  [audit_window.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)**
  (deterministic, zero-LLM gates: coverage, sense-dup, markup fidelity,
  untranslated-residue, ownership). Human judgment enters only at defined gates
  (HTML review sheets, gold-sample sessions) — never as silent post-editing.
- **Markup is a checkable invariant.** Only English/German wrapper prose is
  translated; Sanskrit (`<s>`/`{#…#}`), grammar labels (`<gram>`), and citations
  (`<ls>`) are masked and restored mechanically. Do **not** "fix" untranslated
  Sanskrit — that is correct behaviour.

**Data policy:** the translation store, TM files, learner scores, review sheets,
and re-glue outputs are **deliberately gitignored** — the repo is public, the
unpublished Russian text is not. Do not commit them. The TMX release is gated
behind rights clearance.

## 5. Repo conventions you must follow

Most are enforced by hooks in
[claude-config/hooks/](https://github.com/gasyoun/claude-config/tree/main/hooks);
the residue that isn't:

- **Clickable links everywhere.** Every path/URL is a Markdown link. In
  **committed** Markdown (this repo included) use **full `blob`/`tree` URLs**,
  never relative — relative links don't resolve when a doc is pasted into chat,
  an issue, or another repo, and a `check_md_full_urls.py` hook blocks relative
  links on write. In chat, working-dir-relative links are fine.
- **Dated header + byline** on every authored doc: `_Created: DD-MM-YYYY · Last
  updated: DD-MM-YYYY_` (dashes, not ISO) and a `_Dr. Mārcis Gasūns_` byline.
  When editing, find the real creation date
  (`git log --follow --diff-filter=A --format=%ad --date=short -- <path> | tail
  -1`) and bump only "Last updated".
- **No HTML in `.md`** — use a `> ` blockquote for indent/muting. Enforced
  (blocks on write).
- **Language matches the material.** Russian-content directories get Russian
  indexes ([Syntax-Lectures](https://github.com/gasyoun/SanskritLexicography/blob/master/Syntax-Lectures/README.md),
  the `mw_ru`/`pwg_ru` prompt READMEs); the root README and CLAUDE.md are
  English.
- **BOM is inconsistent** in
  [HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists)
  and the `.txt` corpora — check `head -c 3 file | xxd` before transforming and
  preserve the file's existing BOM state. The org "no BOM" rule does **not** hold
  here.
- **Commits:** `ai-wip:` prefix, one logical change each. Never commit binary or
  large data unless asked. Keep Markdown lint-clean (no trailing whitespace,
  newline at EOF, valid YAML).
- **Model attribution:** report the tier **and** exact version
  (`Opus 4.8 (claude-opus-4-8)`), never the bare tier, in any provenance file.

## 6. Concurrency safety — this tree is shared

Concurrent sessions (Claude *and* Codex) have collided in this exact tree before
(the H214 tree-intermix incident), and direct edits to the main checkout are
**blocked by a hook**. Before starting a handoff-shaped task:

1. **Isolate in a fresh `git worktree`** off `origin/master` and work there —
   `git worktree add ../SanskritLexicography-<slug> origin/master -b <branch>` —
   then deliver by PR. Do not edit the main checkout directly.
2. Read the closest `.ai_state.md` fresh — the subsystem-local
   [RussianTranslation/.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
   takes priority over the repo-root
   [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/.ai_state.md)
   when the work is under `RussianTranslation/`.
3. Check [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
   for a `🔒 CLAIMED` tag on the row.
4. **Never `git add -A`** — `git status` / `git diff --cached` right before
   committing so you commit only your own files, and reclaim finished worktrees
   the moment the PR lands — same pass, never deferred (org rule since 17-07-2026); [`/worktree-gc`](https://github.com/gasyoun/claude-config/blob/main/commands/worktree-gc.md) is only the periodic safety net for drift.

## 7. CI, pre-commit, releases

- **CI** ([.github/workflows/ci.yml](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)):
  Markdown lint + YAML lint + a Python lint job that
  **does fire** (`.py` files exist) + a conditional JS lint + a
  **RussianTranslation gates** job that compiles the pipeline scripts and runs
  their fixture selftests + a **docs-site pytest** job (`pytest
  docs_site/test_docs_site.py` after `pip install -r requirements.txt` — a
  `docs_site/` edit CAN break CI) — keep the tooling importable and the gate
  selftests green. **Markdown link-check is no longer per-push**: it moved to
  [.github/workflows/link-check.yml](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/link-check.yml)
  (weekly + manual dispatch) after burning ~47 min per push for zero
  per-run enforcement value.
- **Pre-commit** ([.pre-commit-config.yaml](https://github.com/gasyoun/SanskritLexicography/blob/master/.pre-commit-config.yaml)):
  `check-yaml`, `end-of-file-fixer`, `trailing-whitespace` (markdown-aware),
  `check-merge-conflict`, plus the local
  `russian-translation-review-changelog` guard
  (`review_changelog_guard.py --staged`).
- **Releases:** promote [changelog.md](https://github.com/gasyoun/SanskritLexicography/blob/master/changelog.md)
  `[Unreleased]` → `[X.Y.Z] - DATE`, annotated tag `vX.Y.Z`, `gh release create`.
  Release cadence follows the changelog's own rule: keep upcoming work under `[Unreleased]`, and **cut a new version every time the changelog is updated** — agent-cut releases are the norm (v1.20.0/v1.21.0 both agent-cut 18-07-2026). The old “never tag unprompted” stance is retired (see HANDOFF.md).

## 8. The docs site

[docs_site/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site)
is a real static site built by
[build_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/build_site.py)
(via the `zettelkastenwiki` package, **not** Docusaurus/Observable) from
[docs_site/wiki/research/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site/wiki/research).
The site is **built and tested, not deployed**: origin/gh-pages has no
`research/` directory, so nothing is live at
gasyoun.github.io/SanskritLexicography/research — the deploy is human-gated
(publish-safety pass below, then a human pushes the built `_site/` output).
Rebuild and test:

```powershell
python docs_site\build_site.py
python -m pytest docs_site\test_docs_site.py
```

Anything that becomes **public** (this site, the findings dashboard, any Pages
flip) goes through a
[publish-safety](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md)
pass first — this repo mixes public exports with rights-gated and unpublished
material.

## 9. Where to look when you're lost

- **"What changed"** → [changelog.md](https://github.com/gasyoun/SanskritLexicography/blob/master/changelog.md)
  + the closest `.ai_state.md`.
- **"Did someone already build this?"** → org
  [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md),
  [Uprava/PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md),
  and this repo's FINDINGS + FEATURES_INDEX before writing anything.
- **"Who decides / what's next"** → [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
- **Next-agent orientation** → [docs/manuals/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md)
  + the closest `.ai_state.md` ([HANDOFF.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HANDOFF.md)
  is retired, kept only as a pointer).
- **Org-level conventions** (issue taxonomy, csl-orig workflow, `.ai_state.md`
  protocol) → the org
  [CLAUDE.md](https://github.com/gasyoun/github-spine/blob/main/CLAUDE.md), loaded
  automatically.

_Dr. Mārcis Gasūns_
