# H2889 — PWG translation runtime dependency graph

_Created: 18-08-2026 · Last updated: 18-08-2026_

**Frozen commit:** `af58b3b01836e7e888b066b1cd499c3ee53dc602` (`origin/master`, 18-08-2026)
· **Executor:** Opus 5 (`claude-opus-5`), maximum effort
· **Handoff:** [H2889-Opus_PWG_pwg-translation-comprehensive-code-review_16.08.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2889-Opus_PWG_pwg-translation-comprehensive-code-review_16.08.26.md)

This document proves the review boundary. It is not a design sketch: every node below
is a file that exists at the frozen commit, and every edge is a line number in a file
that names it. Nothing is included because it "feels related", and nothing is excluded
because it "looks peripheral" — exclusion needs the same evidence as inclusion.

## 0. How the boundary was proven

Three mechanical passes, all read-only, all reproducible from
[`RussianTranslation/pwg_ru/h2889/H2889_REVIEW_MANIFEST.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_REVIEW_MANIFEST.tsv):

1. **Enumerate.** Every `.py` under
   [`RussianTranslation/src`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src),
   [`RussianTranslation/tests`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/tests),
   [`RussianTranslation/tools`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/tools),
   [`RussianTranslation/experiments`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/experiments),
   plus repo-root `tools/` and `scripts/` — **561 files, 0 parse errors** under an `ast`
   walk that extracts imports, `subprocess` argv heads, `os.environ` keys, path literals
   and URL literals.
2. **Seed from proven entrypoints only** — six classes, table §1. A file is a seed
   because a workflow, a systemd unit, an operator skill, `pytest` collection, a live
   operating document, or another file's `subprocess.run` *names it*.
3. **Close under imports.** Transitive closure of the seed set over the resolved
   first-party import edges. Everything the closure does not reach is out of scope and
   carries that verdict, with the reason, in the manifest.

**Result: 361 in-scope Python files of 561 (64 %).** The 200 outside are not "not looked
at" — they are `not-applicable`, each with the explicit verdict *no proven live edge from
a PWG-translation entrypoint*, and each individually listed in the manifest. Adding the
non-Python first-party artifacts on a live edge (9 CI workflows, 2 systemd units, the
schema and prompt assets) gives the manifest's **610 rows, 410 in scope**.

## 1. Entrypoints — what starts a PWG translation run

| Seed class | Entrypoints | Example edge (evidence) |
|---|---:|---|
| CI workflow | 119 | [`scripts/changelog_duplicate_bullets.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/scripts/changelog_duplicate_bullets.py) ← [`.github/workflows/changelog-lint.yml:31`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/changelog-lint.yml) |
| systemd unit | 2 | [`RussianTranslation/src/pilot/max_account_orchestrator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py) ← [`RussianTranslation/deploy/pwg-ru-max-orchestrator.service:10`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/deploy/pwg-ru-max-orchestrator.service) |
| operator skill | 9 | [`RussianTranslation/src/pilot/headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) ← [`/pwg-bounded-run`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md) |
| pytest | 21 | [`RussianTranslation/tests/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/tests) (collection) |
| live operating doc | 171 | [`RussianTranslation/src/pilot/max_account_orchestrator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py) ← [`RussianTranslation/.ai_state.md:4203`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) |
| runtime subprocess spawn | 2 | [`RussianTranslation/src/pilot/perf_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py) ← [`RussianTranslation/src/pilot/window_selftest.py:3270`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py) |

The production route is the one the two systemd `ExecStart` lines name, not the one the
architecture document describes: a profile-bound headless CLI on manifest v2
([`headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
driven by
[`coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py)
and
[`bounded_staged_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run.py)),
with the Max-Workflow lane retired to forensics —
[`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md)
is the live procedure and
[`PIPELINE_ARCHITECTURE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md)
carries a correct HISTORICAL banner.

## 2. Shape of the closure

| Import depth from an entrypoint | Files |
|---|---:|
| 0 (entrypoint itself) | 269 |
| 1 | 85 |
| 2 | 7 |
| **total in scope** | **361** |

The graph is **wide and shallow**. Three quarters of the in-scope files are entrypoints in
their own right — a CLI with `argparse` and a `__main__`. That is a structural fact with a
review consequence: there is almost no deep call stack to reason about, but there are ~270
independent front doors, each with its own argument parsing, its own path resolution and
its own failure policy. Consistency between them cannot be assumed anywhere; it has to be
checked per door. Every divergence found in this review is of that shape.

## 3. Trust-boundary hubs — where a defect propagates furthest

| Hub (in-degree inside the closure) | Importers | LOC |
|---|---:|---:|
| [`src/safe_filename.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/safe_filename.py) | 31 | 71 |
| [`src/store_path.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py) | 29 | 264 |
| [`src/pilot/call_reservation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py) | 21 | 498 |
| [`src/pilot/window_common.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_common.py) | 20 | 317 |
| [`src/pilot/execution_contract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py) | 19 | 255 |
| [`src/corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py) | 18 | 733 |
| [`src/pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py) | 15 | 538 |
| [`src/pwg_tm_canonical.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_canonical.py) | 14 | 489 |
| [`src/pilot/translation_memory.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py) | 13 | 2270 |
| [`src/pilot/cache_identity.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_identity.py) | 13 | 194 |
| [`src/store_write.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_write.py) | 12 | 196 |
| [`src/pilot/headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) | 11 | 1658 |
| [`src/ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py) | 11 | 1334 |
| [`src/sibling_root.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sibling_root.py) | 11 | 109 |
| [`src/promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) | 10 | 2227 |
| [`src/pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py) | 10 | 126 |
| [`src/review_binding.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_binding.py) | 10 | 343 |
| [`src/pilot/selftest_isolation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/selftest_isolation.py) | 9 | 249 |
| [`src/dict_merge.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/dict_merge.py) | 9 | 252 |
| [`src/pilot/gateway_route.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_route.py) | 8 | 470 |

Two of these deserve naming as *identity* boundaries rather than utility modules.
[`safe_filename.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/safe_filename.py)
decides, for 31 importers, what a Sanskrit headword's on-disk name is — a collision there
is two roots sharing one artifact.
[`cache_identity.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_identity.py)
decides, for 13 importers, when two generation requests are "the same" — an omission in
that key is paid work silently replaced by a stale answer.

## 4. External and sibling-repo edges — the untrusted-input boundary

| Sibling repo | In-scope files touching it | First proven edge |
|---|---:|---|
| `csl-orig` (upstream dictionary source, read-only) | 32 | [`src/annotate_genres.py:49`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_genres.py) |
| `SamudraManthanam` (corpus DB) | 19 | [`src/assemble.py:5`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/assemble.py) |
| `kosha` (datasets manifest) | 13 | [`src/annotate_evidence.py:26`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_evidence.py) |
| `VisualDCS` (DCS token corpus / frequency) | 12 | [`src/build_dcs_freq.py:4`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_freq.py) |
| `pwg-ru-data` (run data root) | 8 | [`src/pilot/ci_gate_runner.py:2`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/ci_gate_runner.py) |
| `csl-pywork` (pwgab / pwgbib tables) | 7 | [`src/g5_card_render.py:533`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/g5_card_render.py) |
| `csl-pyutil` (installed package — review-sheet emitter, anatomy) | 7 | [`src/build_g5_review_sheet.py:46`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_g5_review_sheet.py) |
| `rvlinks` (citation targets) | 7 | [`src/citation_edges.py:312`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_edges.py) |
| `WhitneyRoots` (root crosswalk) | 5 | [`src/export_lod.py:708`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_lod.py) |
| `sanskrit-util` (transcoder, `sys.path`-injected) | 4 | [`src/gold_evidence_panel.py:86`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_evidence_panel.py) |
| `SanskritGrammar` (register/genre layer) | 3 | [`src/build_renou_pilot_sheet.py:18`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_renou_pilot_sheet.py) |
| `SanskritRussian` (RU gloss rollups) | 3 | [`src/gold_evidence_panel.py:27`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_evidence_panel.py) |
| `CommentaryStrategies` (MBh concordance) | 2 | [`src/build_mbh_concordance.py:14`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_mbh_concordance.py) |
| `csl-lslink` (PWG `<ls>` link DB) | 1 | [`src/ls_links.py:18`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py) |

`pwgxml`, `csl-apidev` and `csl-websanlexicon` were named as *candidates* by the
commission. **No live edge to any of the three was found** at the frozen commit: no
import, no path literal, no subprocess, no workflow reference. They are therefore out of
scope with that verdict recorded, not silently dropped.

Every edge in this table is a directory read through a **path guess**, not a declared
dependency: there is no lockfile, no manifest and no version assertion on the sibling
checkouts. Only `csl-pyutil` is a declared dependency, and it is declared twice, at two
different versions — see the findings report.

### The two path-resolution regimes

[`sibling_root.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sibling_root.py)
exists precisely because eleven modules each independently guessed
`os.path.join(HERE, '..', '..', '..')` — true only in the canonical checkout, false in a
`git worktree`, which the org's shared-tree rule *requires* for this repo (FINDINGS §503,
H1847 / H1902). At the frozen commit **13 files import the canonical resolver and 41 still
guess**, so the two regimes coexist and disagree in exactly the environment the workflow
rules mandate. The consequences are findings, not graph facts, and are carried in
[`H2889_COMPREHENSIVE_CODE_REVIEW_2026-08.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_COMPREHENSIVE_CODE_REVIEW_2026-08.md).

## 5. Configuration and secrets surface

Environment variables are the pipeline's real configuration channel — there is no config
file. Census over the in-scope tree, by number of reading sites:

| Variable | Sites | Role | Trust note |
|---|---:|---|---|
| `PWG_COORDINATOR_DIR` | 41 | run/window artifact root | relocates every artifact a gate reads |
| `PWG_RU_STORE` | 24 | the promoted card store | relocates the system of record |
| `PWG_INPUT_DIR` | 21 | prepared input payloads | |
| `CLAUDE_CONFIG_DIR` | 12 | profile binding for a paid spawn | **billing identity** |
| `PWG_RU_TM_DIR` | 9 | translation-memory root | |
| `PWG_RU_DATA_ROOT` | 8 | `pwg-ru-data` layout root | |
| `CSL_SIBLING_ROOT` | 8 | explicit sibling assertion | flips optional-table degradation into an error |
| `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL` | 6 / 5 / 4 | third-party provider | **secret** |
| `REVIEW_LOCK_FORCE` | 5 | overrides a review lock | **guard override** |
| `PILOT_COLLECT_PROTECTED` | 4 | protected-collection flag | |
| `XAI_API_KEY` | 1 | third-party provider | **secret** |
| `PWG_SKIP_INTEGRITY_EXTRACT` | 1 | skips an integrity extract | **guard override** |

Two provider families (`DEEPSEEK_*`, `XAI_*`) sit inside a system whose documented
production route is the Anthropic headless CLI. Their presence is a real edge — the
review treats them as live provider paths, not dead code, because
[`src/pilot/openrouter_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/openrouter_worker.py)
is exercised by CI at
[`.github/workflows/ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml).

## 6. Data and control direction

| Edge | Direction | Trust boundary | Reviewed here |
|---|---|---|---|
| `csl-orig` → masker → cards | data in | **untrusted upstream**, read-only by policy | yes (contour 1) |
| worklist/freq → coordinator → headless worker | control | first-party | yes (contour 2, 4) |
| headless worker → Anthropic CLI (child process) | control + **paid** | external provider | yes (contour 4) |
| model output → validators → store | data in | **untrusted model output** | yes (contour 3, 5, 6) |
| store → export (JSONL/TMX/TEI/OntoLex/RDF) → release | data out | published artifact | yes (contour 7) |
| store → review sheet (HTML) → human → `decisions.json` → store | round trip | human-in-the-loop | yes (contour 6, 7) |
| systemd timer (15 s) → orchestrator → coordinator | control | prod host, root-adjacent | yes (contour 8) |
| repo → GitHub Actions → merge | control | supply chain | yes (contour 8) |

The two boundaries where untrusted bytes cross into a durable artifact are
`csl-orig` → masker and model output → store. Both are inside the closure and both were
given a dedicated lane.

## 7. Entrypoints named by a live edge but absent from the scanned tree

| Named target | Named by | Verdict |
|---|---|---|
| `docs_site/test_docs_site.py` | [`.github/workflows/ci.yml:415`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml) | exists; outside the PWG subtree, out of scope |
| `research/build_observatory.py` | [`.github/workflows/ci.yml:175`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml) | exists; observatory lane, out of scope |
| `findings_dashboard/build_findings_data.py`, `epistemic_dashboard/build_epistemic_dashboard.py` | [`.github/workflows/findings-dashboard.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml) | exist; registry dashboards, out of scope |
| `src/pilot/run_pilot_wf.js` | [`.github/workflows/ci.yml:332`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml) | exists; JavaScript, retired Max lane, syntax-checked only |
| `_audit.py`, `build_strata.py`, `corpus_harvest.py`, `build_corpus_lexicon.py` | [`src/add_corpus_text.py:78,100,101`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/add_corpus_text.py), [`src/_supervise.py:38`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_supervise.py) | exist, but are spawned by **bare filename** — resolution depends on the caller's cwd |
| `src/pilot/gen_opt_harness.py` | [`RussianTranslation/.ai_state.md:3498`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) | **does not exist**; the file is `gen_opt_harness2.py` |

## 8. What this graph does not prove

Stated so no reader over-reads it:

- **Dynamic imports and `importlib` are not followed.** The closure is static. A module
  loaded by name at runtime would be missed; none was observed, but absence of observation
  is not proof.
- **Data-file edges are proven by literal, not by execution.** A path literal in a file
  proves the code *can* read it, not that a given run *did*.
- **The `.ai_state.md` seed class is generous by design.** It brings in 171 entrypoints,
  some of them historical one-shot tools. That errs toward reviewing too much rather than
  too little; the alternative — dropping them — would have produced a silent remainder.
- **Sibling-repo internals are out of scope.** The edge is reviewed; `csl-orig`'s own code
  is not.

Reproduce: the extractor, seed builder and manifest builder are
`graph.py`, `closure.py`, `manifest.py` as recorded in
[`H2889_BASELINE_GATES_2026-08.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_BASELINE_GATES_2026-08.md) § Reproduce.

_Dr. Mārcis Gasūns_
