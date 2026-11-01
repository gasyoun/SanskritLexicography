# H7241 — `window_selftest.py` split into pytest-collectable modules

_Created: 25-10-2026 · DeepSeek Flash (opencode/deepseek/deepseek-flash)_

## What changed

`src/pilot/window_selftest.py` was 10,321 lines / 229 test functions / 14 helpers with **no
pytest anywhere behind it**, so nothing in it was selectable: checking one guardrail cost the
whole suite and a reviewer could not ask "did this PR touch the guardrails it should have".

The split is **mechanical** — source text was moved, not rewritten — by
`src/pilot/archive/h7241_split_window_selftest.py` (committed, one-shot):

| before | after |
|---|---|
| one 10,321-line file, 229 tests, no pytest | 11 subject modules + `_support.py` + `conftest.py`, 229 tests collected by pytest |
| `src/pilot/window_selftest.py` holds all tests | `src/pilot/window_selftest.py` = 314-line thin wrapper (same CLI, same output) |

Module map (full list of test → module → old line number in
[`src/pilot/tests/MODULE_MAP.md`](../src/pilot/tests/MODULE_MAP.md)):

| module | tests |
|---|---|
| `tests/test_workflow_and_harness.py` | 15 |
| `tests/test_no_pwg_lane.py` | 12 |
| `tests/test_senses_and_glosses.py` | 26 |
| `tests/test_markup_and_language_gates.py` | 19 |
| `tests/test_coverage_and_parity.py` | 10 |
| `tests/test_requeue_and_audit_state.py` | 11 |
| `tests/test_tm_and_fragments.py` | 27 |
| `tests/test_budget_and_preflight.py` | 31 |
| `tests/test_coordinator_and_promotion.py` | 38 |
| `tests/test_audit_and_reporting.py` | 35 |
| `tests/test_prompt_and_policy.py` | 5 |
| `tests/_support.py` | 14 fixtures/helpers + imports + isolation guard |

## What did NOT change

- **Every assertion is the original text.** `h7241_split_window_selftest.py --check` compares
  the AST of each of the 243 moved definitions (229 tests + 14 helpers) against the original
  segment and refuses on any difference: `PASS: every test and fixture is present once,
  body-identical to the original` (243/243 seen, 0 missing, 0 duplicated).
- The only substitution inside a test body is `os.path.dirname(os.path.abspath(__file__))` →
  `HERE`. `HERE` in `_support.py` **is** the old `src/pilot` directory (asserted in
  `_support.py`'s header comment and verified by the 229-test run below).
- No test added, none deleted, none skipped, no `xfail`, no ordering change: `conftest.py`
  sorts collection by `_support.ORIGINAL_ORDER`, the exact `tests = [...]` list order the old
  `main()` used, so an order-sensitive failure cannot move.
- Production isolation is unchanged: `_support.py` imports `selftest_isolation.guard()` and
  runs it **before** every repo import, exactly like the old file header.

## Checks

| command | result |
|---|---|
| `python src/pilot/window_selftest.py` (BEFORE, pre-split tree) | `ran 229/229 defined -- 222 passed, 7 failed` |
| `python -m pytest src/pilot/tests -q` (AFTER) | `8 failed, 221 passed in 35.08s`, 229 collected |
| `python src/pilot/window_selftest.py` (AFTER, legacy wrapper) | `ran 229/229 defined -- 221 passed, 8 failed` |
| `h7241_split_window_selftest.py --check` | PASS, 243/243 definitions body-identical |

**CI (Linux, the platform where the suite is green)** — `RussianTranslation gates` on PR #2464
runs `window_selftest.py` against the split tree:

```
window selftest: ran 229/229 defined -- 228 passed, 1 failed
FAILED (1): test_lang_parity_ledger_complete
```

All seven tests that fail on this Windows box (`test_split_agent_pools_all_heal_runtime`,
`test_lowwide_staggered_dispatch`, `test_h960_accept_sanloss_soft_gate`,
`test_tnmask_persist_and_offline_detect`, `test_grammar_field_restore_behavioral`,
`test_german_anchor_repair_behavioral`, `test_h3675_target_anchor_repair_behavioral`) **PASS
on CI with the split in place** — they are platform-specific and pre-existing, not moved
assertions breaking. So on the platform that matters the split is 228/229 green and the sole
red is the ledger hash gate below.

**Failure-set parity** (`reports/H7241_parity.json`): the two runners agree exactly —
identical 8-failure set, identical 221 passes. Versus the pre-split baseline:

- 7 baseline failures still fail, same names, same messages
  (`test_split_agent_pools_all_heal_runtime`, `test_lowwide_staggered_dispatch`,
  `test_h960_accept_sanloss_soft_gate`, `test_tnmask_persist_and_offline_detect`,
  `test_grammar_field_restore_behavioral`, `test_german_anchor_repair_behavioral`,
  `test_h3675_target_anchor_repair_behavioral`).
- **One pass did not survive, and it is not a test-logic change:**
  `test_lang_parity_ledger_complete` (next section).
- Zero other passes lost; zero tests invented.

## The one explained delta — needs a human, on purpose

`test_lang_parity_ledger_complete` reads `LANG_PARITY.md` and refuses any tracked file whose
sha256 drifted since its entry was last verified. 42 ledger entries list
`src/pilot/window_selftest.py`; moving the file's bytes necessarily trips all 42:

```
LANG_PARITY.md has 42 unresolved parity violation(s):
  latin_cue_masking: src/pilot/window_selftest.py changed since last parity verification
  (recorded a0e49325b926..., now a9ede8f5d9f3...)
```

`lang_parity_check.py --update-hash` exists for exactly this, but the repo reserves it: drift
means *a human re-opens the entry and re-affirms its verdict*, which is deliberately not an
agent's call (see the policy comment that travels with this suite). So this PR leaves
`LANG_PARITY.md` untouched and hands over the exact remediation:

1. For each of the 42 entries, repoint `files` from `src/pilot/window_selftest.py` to the
   module(s) now holding the tests that evidence that verdict — `tests/MODULE_MAP.md` gives
   test → module, and `git grep -n <test_name> src/pilot/tests` the line.
2. Then `python src/pilot/lang_parity_check.py --update-hash <id>` per entry, after confirming
   the verdict still holds.
3. Re-run `python -m pytest src/pilot/tests -q` → expected `7 failed, 222 passed`.

Re-hashing the wrapper alone would be wrong (it would silently end the ledger's coverage of the
test bodies, which now live in `tests/`), and rewriting 42 provenance entries is a data-governance
change that needs an independent check — so it is deliberately **not** in this PR. Residual is
tracked as GTD row `WH3`.

## Definition of done — status

| DoD item | status |
|---|---|
| `pilot/tests/test_<area>.py` modules that pytest collects | ✅ 229 collected |
| every assertion preserved | ✅ AST-identical, 243/243 |
| no test invented / skipped | ✅ 229 in = 229 out, no marks |
| old file removed or left as a thin wrapper | ✅ 314-line wrapper, same CLI |
| before/after pass counts recorded and equal | ⚠️ equal except the one human-gated ledger entry (`228/1` vs `229/0` on CI) |
| no behaviour change | ✅ both runners agree on every test outcome |


## Risks

- **Order-dependent tests.** Mitigated by pinning collection order to the legacy `main()` order
  in `conftest.py`; the identical failure set on both runners is the evidence.
- **`__file__` semantics.** The only rewritten expression; `HERE` is the old directory by
  construction. Modules that need to know *their own* file (`gh.__file__`, `tm.__file__`) were
  left alone.
- **A future test added to a module** is collected automatically; a test added to the wrapper is
  not (the wrapper has no `test_*` defs any more) — the archive splitter documents the routing
  rules for anyone redoing this.
- **`tests/` is not a package** (no `__init__.py`): pytest's rootdir insertion and the wrapper's
  explicit `sys.path` insert both resolve `_support`; keep it that way to avoid a second import
  path.

## Inspect first

`src/pilot/tests/_support.py` (the header is the contract), then
`src/pilot/window_selftest.py` (what is left), then `src/pilot/tests/MODULE_MAP.md`.
