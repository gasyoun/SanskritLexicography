# H3985 — `/document` sweep report (Cyrillic → SLP1 proper-noun table)

_Created: 03-09-2026 · Last updated: 03-09-2026_

Closing record for **H3985 (Opus 5) — Validated Cyrillic-to-SLP1 proper-noun table over the IAST-bearing seeds (GAPS §6)**, executed 03-09-2026 by Opus 5 (`claude-opus-5`) under the standing `/go` chain (mint → do → commit → PR → merge → `/cut-release` → `/handoff-close` → `/document`).

## 1. The deliverable

[`RussianTranslation/data/cyrillic_proper_noun_slp1.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.tsv) — 534 rows, 92 442 bytes, `rule_derived_keys: 0`. Every key is attested in an IAST-bearing seed; no row is produced by character-level transliteration rules.

| Artifact | Role |
|---|---|
| [`data/cyrillic_proper_noun_slp1.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.tsv) | the table (534 validated rows) |
| [`data/cyrillic_proper_noun_slp1.meta.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.meta.md) | metadoc: provenance, coverage, ranked backlog |
| [`tools/h3985_cyr_slp1_table.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h3985_cyr_slp1_table.py) | builder |
| [`tools/h3985_seed_inventory.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h3985_seed_inventory.py) | seed census (`files_scanned: 85`, `files_with_inline_iast: 32`, `files_cyrillic_heavy_no_iast: 20`) |
| [`reports/H3985_cyr_slp1_validation.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3985_cyr_slp1_validation.json) | validation receipt |
| [`document_sweep_2026-09-03_h3985.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/document_sweep_2026-09-03_h3985.json) | sweep exit-gate receipt |

### Coverage (partial by design)

| Seed | Keyed | Total | Share |
|---|---|---|---|
| Erman–Temkin | 174 | 478 | 36.4 % |
| Кадамбари | 130 | 393 | 33.1 % |
| Потапова | 128 | 326 | 39.3 % |

The Potapova HTML twin reports 2/77 — a disclosed parser artifact, not a coverage claim. Twenty pure-Cyrillic seed files carry no inline IAST and are deliberately left unkeyed: keying them would require exactly the rule-derived guessing this handoff exists to avoid.

### What it refutes

[H1746 (Grok 4.5) — Cyrillic proper-noun → SLP1 lookup seed inventory (FINDINGS §495)](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1746-Grok_SanskritLexicography_cyrillic-proper-noun-slp1-lookup_27.07.26.md) reported 61/47 figures from [`tools/gaps_s6_cyrillic_name_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/gaps_s6_cyrillic_name_probe.py). Two defects made those numbers stale: `SEARCH_ROOTS` names a `C:\Users\user\Documents\GitHub\SamudraManthanam` path that never resolves on this host, and `"all_hits": hits[:80]` truncates the hit list. The probe's own `verdict` block already named the recoverable path — a validated lookup table seeded from IAST-bearing indices — which is what H3985 built.

## 2. Sweep table — 25 surfaces

Driven by [`Uprava/tools/document_check.py`](https://github.com/gasyoun/Uprava/blob/main/tools/document_check.py) with `GH_ROOT` pointed at a symlink shadow so Phase-2 hub checks read worktree state.

| # | Surface | Verdict | Evidence |
|---|---|---|---|
| 1 | `readme` | ✅ | [`README.md:110`](https://github.com/gasyoun/SanskritLexicography/blob/master/README.md#L110) |
| 2 | `claude_md` | ✅ | [`CLAUDE.md:227`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md#L227) — sync rule: manifest edit ⇒ rebuild directory |
| 3 | `cold_start` | ✅ | [`AGENTS.md:53`](https://github.com/gasyoun/SanskritLexicography/blob/master/AGENTS.md#L53) |
| 4 | `metadoc` | ✅ | [`data/cyrillic_proper_noun_slp1.meta.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.meta.md) created |
| 5 | `ai_state` | ✅ | [`.ai_state.md:25`](https://github.com/gasyoun/SanskritLexicography/blob/master/.ai_state.md#L25) |
| 6 | `features_index` | ✅ | [`FEATURES_INDEX.md:60`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md#L60) — ⚪ A7 |
| 7 | `kosha_manifest` | ✅ | [`kosha/data/manifest/datasets.json:2407`](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json#L2407) + `scripts/build_directory.py` rerun |
| 8 | `data_layers_census` | ✅ | [`DATA_LAYERS_CENSUS.md:167`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md#L167) |
| 9 | `project_interlinks` | ✅ | [`PROJECT_INTERLINKS.md:255`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md#L255) |
| 10 | `questions_log` | ✅ | [`QUESTIONS_LOG.md:99`](https://github.com/gasyoun/Uprava/blob/main/QUESTIONS_LOG.md#L99) — Q2607-24 Reps 17 → 18 |
| 11 | `repo_status_rollup` | ✅ | [`REPO_STATUS_ROLLUP.md:143`](https://github.com/gasyoun/Uprava/blob/main/REPO_STATUS_ROLLUP.md#L143) |
| 12 | `changelog` | ⛔ n/a | promoted separately by `/cut-release` — v1.144.145 and v1.144.146 already cut this pass |
| 13 | `sibling_domain_docs` | ⛔ n/a | no sibling manual owns Cyrillic-name keying; the metadoc is the reader's landing point |
| 14 | `issues` | ⛔ n/a | H3985 has no tracking issue |
| 15 | `gtd` | ⛔ n/a | creates no human action and no external wait |
| 16 | `handoffs_registry` | ⛔ n/a | closed by `/handoff-close H3985`, not by this sweep |
| 17 | `skills_index` | ⛔ n/a | a dataset, not a skill |
| 18 | `articles` | ⛔ n/a | not a paper |
| 19 | `danger_facts` | ⛔ n/a | no destructive-risk fact surfaced |
| 20 | `megabook` | ⛔ n/a | operational coverage, not a thesis refinement |
| 21 | `skills_manual_ru` | ⛔ n/a | no skill/tool contract changed |
| 22 | `hooks_index` | ⛔ n/a | no enforcement changed |
| 23 | `hub_manifest` | ⛔ n/a | not a long-lived hub or registry |
| 24 | `auto_derived_views` | ⛔ auto | sources updated; never hand-edited |
| 25 | `epistemic_registries` | ⛔ n/a | GAPS §6 stays open — H3985 closes its decidable half only, and the metadoc records the residue |

**Exit gate:** `present=0 missing=21 n/a=4` → `present=11 missing=0 n/a=14 (total=25)`. Zero unexplained `missing`; receipt committed as [`document_sweep_2026-09-03_h3985.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/document_sweep_2026-09-03_h3985.json) (the `_h####` suffix avoids collision with H3948's same-day receipt).

## 3. Delivery

| Repo | Change | Landed |
|---|---|---|
| SanskritLexicography | table + builder + validation + metadoc | [#2059](https://github.com/gasyoun/SanskritLexicography/pull/2059) merged |
| SanskritLexicography | release v1.144.145 / v1.144.146 | [#2060](https://github.com/gasyoun/SanskritLexicography/pull/2060) merged |
| SanskritLexicography | repo-local sweep edits + receipt | [#2063](https://github.com/gasyoun/SanskritLexicography/pull/2063) merged 2026-09-03T10:53:04Z |
| kosha | manifest row + `in_release` fix + README counts + directory rebuild | [#503](https://github.com/gasyoun/kosha/pull/503) merged 2026-09-03T10:57:17Z |
| Uprava | hub edits (census · interlinks · questions · rollup) | direct push `8f0e09856` |

### kosha red check — diagnosed, not force-merged

CI `Fixture build + tests` failed 2 of 629 tests, and the cause was mine. The manifest row carried `"in_release": "1.144.146"` — a SanskritLexicography release number — but kosha's D8 closed vocabulary in [`tests/test_directory.py`](https://github.com/gasyoun/kosha/blob/main/tests/test_directory.py) accepts only `unreleased`, `not-applicable`, or `data-vX.Y.Z`. The TSV ships from SanskritLexicography and is not a kosha release asset, so the honest value is `not-applicable`. The W1d invariant then required the README counts to move 117 → 118 datasets (98 → 99 public). Local `pytest tests/test_directory.py -q` → `12 passed in 0.23s`; CI green; auto-merge landed.

## 4. Honest caveats

1. The clean exit-gate numbers were read through the `GH_ROOT` symlink shadow, which sees the worktrees. The guarded main-tree clones agree only once refreshed — and they must not be pulled into: Uprava's carries uncommitted WIP plus a stash.
2. H3985 has no tracking issue, so no results comment was owed or posted.
3. No `EFFORT_LOG` line was written for this run.
4. `elapsed:` is **not reportable** — no session-start timestamp survives in this context, and inventing one would be worse than omitting it. No `tok/s` either: interactive run, no output log to measure.
5. Neither H1746's nor H3985's registry row carries an `{effort: …}` token, so the effort light cannot be quoted for them; the rule forbids guessing it.

_Dr. Mārcis Gasūns_
