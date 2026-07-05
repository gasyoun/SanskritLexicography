# VERIFY_H189 — deterministic H191 verification

_Created: 05-07-2026 · Executor: Codex/GPT-5 · No Max/Workflow run performed._

## Summary

All H189 deterministic checks passed. H191 code follow-ups B1/B2/B3 are pinned in
`window_selftest.py`; `lang_parity_check.py` is clean after refreshing the existing parity
ledger hashes. The staged 100-small nominal window is ready for a downstream Sonnet Max
Workflow session; Codex did not run Max.

## A1. Green Baseline

✅ `python src/pilot/window_selftest.py` → PASS (`window selftest OK`).

✅ `python src/pilot/lang_parity_check.py` → PASS (`20 entries, all verdicts complete, no drift`).

✅ `python src/pilot/translation_memory.py selftest` → PASS (`translation_memory selftest OK`).

Local note: the clean worktree needed the gitignored `src/pilot/input/` sidecars,
`translation_memory.ru.json`, and `src/pilot/output/scale_manifest.freq.json`; these were
copied/generated locally for deterministic checks only.

## A2. Economics Reproduce

✅ `python src/pilot/parse_workflow_cost.py <wA> <wB> <wC>` reproduced the POSTMORTEM totals:

| run | input | cache-write | cache-read | output-est | total | $ |
|---|---:|---:|---:|---:|---:|---:|
| `wf_34133e5b-777` | 1,677,339 | 4,152,906 | 7,885,813 | 153,415 | 13,869,473 | 25.2724 |
| `wf_41d050b6-722` | 2,250,863 | 5,239,445 | 9,269,580 | 244,480 | 17,004,368 | 32.8486 |
| `wf_1640c173-628` | 1,378,615 | 3,346,159 | 6,513,379 | 204,610 | 11,442,763 | 21.7071 |
| **TOTAL** | **5,306,817** | **12,738,510** | **23,668,772** | **602,505** | **42,316,604** | **79.8281** |

Cache-write share remains 60% of the bill, matching the post-mortem.

## A3. Guardrails

✅ Presplit re-batching: `gen_opt_harness2.py gam` reports 124/127 TM hits and
`agent_expected_after_tm=6` for the remaining presplit giants, not the pre-H189 18-agent
shape. `META.presplit_group_cite_budget=60` and `META.presplit_group_sense_cap=18` drive
the grouping.

✅ Kill gate: `window_selftest.py::test_kill_gate_recalibrated_envelope` confirms
`KILL_FLOOR_MS <= 45000` and `KILL_CEIL_MS <= 180000`.

✅ Budget kill-switch: `META.max_agents = ceil(agent_expected_after_tm * 3) + 10`; `gam`
reports expected 6 → max 28. `MAX_AGENTS_FLOOR` is absent and the harness summary exposes
`budget_kill_switch_tripped`.

✅ Harness-size guard: pre-B1 `gam` emitted 1,104,201 bytes and a 3-way exact key split;
after B1 it emits 747,215 bytes and a 2-way exact key split. The full 100-small harness is
274,848 bytes, under the 480 KB cap. `node --check src/pilot/run_pilot_wf.nominal_w1_100small.js`
passed.

✅ Cost gate: `window_selftest.py::test_perf_preflight_cost_gate` pins monster-shape refusal
and cheap high-count pass. B3 adds `cost_partition` with `run_now` and `defer_monster`.

✅ Empty portrait: `_slp1_lex_for_key` returns `('', '')` for `[]`; pinned by the nominal
keymap tests.

## A4. Adversarial Holes

✅ `count_cap` + JS binary-split heal: confirmed. Python groups presplit fragments with
`count_cap=PRESPLIT_GROUP_SENSE_CAP`; JS `healGroup()` still bisects unresolved groups and
returns partial progress plus exact missing fragment ids, so fragments are not dropped.

✅ `BudgetExceeded` short-circuit: confirmed. `agentKill()` throws `BudgetExceeded` before
calling `agent()` once `MAX_AGENTS` is hit; `isKill(e)` deliberately does not match
`BudgetExceeded`, so the budget stop does not route into more fragment calls.

✅ Cost constant drift: documented. The `$0.347/agent` / 184K-token constant is still
conservative post-H189 because it was measured during the framework re-cache blow-up. It was
not lowered speculatively; recalibration waits for a post-fix live run.

✅ TM/degenerate inlining hole: fixed in H191 B1. `INPUTS`/`PH` now contain only
agent-reachable keys; `TM_RESOLVED` and `DEGENERATE_RESOLVED` remain self-contained.
Pinned by `test_tm_pre_resolves_cards`.

## H191 B Fixes

✅ B1: stopped inlining raw+portrait payloads for TM-resolved and degenerate-pass-through
cards. `gam` size dropped 1,104,201 → 747,215 bytes; accounting smoke confirms
`selected=100`, `inputs=95`, `degenerate=5`, `accounting_ok=true` for the staged nominal window.

✅ B2: single-line monster senses now split at complete `<ls>...</ls>` spans, so no emitted
fragment exceeds the citation budget. Pinned by `test_cit_split_caps_single_line_monster_sense`
with a synthetic 150-`<ls>` one-sense fixture.

✅ B3: `perf_preflight.py` now emits `cost_partition.run_now`, `cost_partition.defer_monster`,
per-card estimates, grouped partition totals, and a recommendation to run `run_now` while
routing monsters to the human-budgeted lane. Pinned by `test_perf_preflight_partitions_mixed_monster_window`.

## Part C Staging

✅ Selected the 100 cheapest `pril5` runnable nominal cards after generating all missing local
input sidecars: 4,292 runnable candidates, 4,292 scored, 0 missing inputs.

✅ Preflight artifact: `src/pilot/NOMINAL_W1_100SMALL.preflight.json`:

- selected keys: 100
- degenerate pass-through: 5
- batches: 3
- expected agents: 3
- presplit keys: 0
- `cost_partition.run_now`: 100
- `cost_partition.defer_monster`: 0
- cost gate: ok, ~745,200 tokens / ~$1.41 / ~$0.01 per translated card

✅ Harness smoke: `gen_opt_harness2.py nominal_w1_100small --nominal --keys=<100>` emitted
274,848 bytes, under cap, and `node --check` passed.

_Dr. Mārcis Gasūns_
