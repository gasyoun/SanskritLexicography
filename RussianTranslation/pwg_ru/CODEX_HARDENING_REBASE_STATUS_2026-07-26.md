# Codex pipeline-hardening branch — rebase + verification status (26-07-2026)

_Created: 26-07-2026 · Last updated: 26-07-2026_

Extraction of `SanskritLexicography-rt-harden-codex`
(`codex/rt-pipeline-hardening-speed`) onto current `master`, and the first time the
branch's own test suite has been run. Executor: Opus 5 (`claude-opus-5[1m]`).

**Verdict: NOT landable as-is. 7 pre-existing tests fail, all from one cause.** The work
itself is substantial and worth landing; what is missing is the fixture layer for the
contract it tightens.

## What was extracted

| | |
|---|---|
| source base | `f96361ca` — the same commit the H858/#729 work branched from, so the two ran in parallel all day |
| carried over | 2 unmerged `ai-wip:` commits + ~3 935 uncommitted insertions across 25 files + 5 new modules |
| new modules | `call_reservation.py`, `promotion_journal.py`, `coordinator_hardening_selftest.py`, + 2 selftests |
| conflicts on rebase | **4** — `h963_c4_gate0_probe.py`, `window_selftest.py`, `PIPELINE_HISTORY.md`, `CHANGELOG.md` |
| applied cleanly | 23 files, including `headless_worker.py` and `promote_final_cards.py` — the H858 work is untouched |

### How the four conflicts were resolved

- **`h963_c4_gate0_probe.py` — the real one.** Codex independently found the same
  fixed-`RUN_ID` defect as [#729](https://github.com/gasyoun/SanskritLexicography/issues/729)
  (same diagnosis — its comment reads "reusing its fixed run ID would make old append-only
  readings indistinguishable from the current invocation") and fixed it **incompatibly**: it
  *aborts* when the constant id is already present. Master
  ([v1.63.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.63.0)) mints a
  per-invocation id instead, which is strictly better — Codex's version refuses to run at all
  once the log holds one row. **Kept master's fix; grafted Codex's genuinely additive
  contribution**, the `CallReservationLedger` pre-spend cap (made per-account, like the
  events log) and the "exactly 2 readings" check. Both survive; selftest 7/7.
- **`window_selftest.py`** — both sides added tests. Kept master's file and re-inserted
  Codex's two (`test_threaded_gate_exception_requeues_full_window`,
  `test_quarantine_replace_failure_preserves_previous_destination`).
- **`CHANGELOG.md`, `PIPELINE_HISTORY.md`** — append-at-top docs; both sides' entries kept.

## Defects found in the branch as delivered

These are **not** rebase artifacts: each is Codex's own new guard against Codex's own
selftest, and each would fail identically in the original worktree. Fixed here.

| # | Symptom | Cause |
|---|---|---|
| 1 | `call_reservation_selftest` → `TypeError: one_call() missing 'active_claim'` | it added two required keyword-only params to `one_call` and passed only one |
| 2 | `headless_worker_selftest` aborts on its first `execute()` | new `CLAUDE_CONFIG_DIR` paid-boundary guard; the shared fixture helper and 4 direct call sites never supply one |
| 3 | same suite → `paid headless execution requires an explicit config directory` | 2 direct `HeadlessEngine(...)` constructions |
| 4 | same suite → `paid headless spawn requires the live canonical profile claim` | `test_durable_call_reservation` drives `.call()` without holding an `ActiveCallClaim` |
| 5 | `test_cli_reservation_and_preflight_gates` exits 2, not 0 | it sets `CLAUDE_CONFIG_DIR` only for its v2 half, after the `--max-calls 0` case that also needs it |
| 6 | `bounded_staged_run_selftest` aborts | it seeds fixtures through the `enqueue` CLI, which the branch turns into a hard refusal |

After those six fixes: `call_reservation`, `promotion_journal`, `coordinator_hardening`,
`headless_worker`, `max_account_orchestrator`, `bounded_staged_run`, `bounded_supervisor`
selftests and `lang_parity_check` are **all green**.

## What still fails — 7 tests, ONE cause

`window_selftest`: **188 defined, 181 pass, 7 fail.**

```
test_coordinator_nominal_reservations
test_coordinator_runtime_state_machine_and_cas
test_coordinator_requeue_attempt_manifests
test_coordinator_mixed_lane_public_state_sequence
test_coordinator_cost_gate_enforced
test_h1420_p11_record_output_binds_run_id
test_h1420_p10_promote_rebuilds_tm_in_finally
```

Every one is the same story: **the branch makes preflight evidence and sealed-v2 binding
mandatory, and the pre-existing fixtures still pass placeholders.** Traced individually:

- `register_prepared_lease` now hashes the preflight file; the reservation-race test passes
  the literal string `'preflight.json'`, which is not a file. **Both** racer threads die on
  `FileNotFoundError`, so the outcome is `['rejected','rejected']` and the serialization
  assertion fails. It reads like a concurrency regression and is not one.
- `begin_run` now calls `validate_lease_preflight`, so both racers `SystemExit` — same shape.
- the cost gate refuses with `required preflight has unsupported schema None` before it can
  reach the deferred-ledger message the test asserts.
- `record-output` now requires `--result-sha256` for a sealed run.
- promotion now refuses `v1/unbound workflow output` as historical-only — the guard working
  exactly as designed, against fixtures that build v1 outputs.

**The guards are behaving correctly; the fixtures are stale.** Bringing them up to the new
contract is real work, and it depends on what the branch author intends the sealed fixture
shape to be — which is why it stops here rather than being guessed at.

## Recommendation

Land in two steps, not one:

1. **Now, low risk:** the parts that are green and independent — `call_reservation.py`,
   `promotion_journal.py`, the probe's pre-spend ledger graft, the two new `window_selftest`
   tests, the `proc_tree` tree-kill hardening.
2. **After the fixture layer is rebuilt:** the coordinator/promotion sealing (the P0
   "promotion is not one recoverable transaction" work), together with the 7 fixtures it
   invalidates.

Nothing is lost either way — the branch is preserved here, rebased, with 6 of its own
defects fixed.

_Dr. Mārcis Gasūns_
