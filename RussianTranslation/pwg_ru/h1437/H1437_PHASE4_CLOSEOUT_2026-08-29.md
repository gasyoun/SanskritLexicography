_Created: 29-08-2026 · Last updated: 05-09-2026_

# H1437 — Phase 4 closeout evidence (offline battery on master tip)

_Created: 29-08-2026_

**Executor:** OxAlpha — GLM 5.3 Flash (`glm-5.3-flash`), unattended roadmap-drain worker B01.
**Scope:** closeout only — all H1437 implementation phases were already landed; this pass ran the
Phase-4 evidence battery on the current `origin/master` tip (`4dec810e`), fixed one
macOS-specific master-tip gate blocker it uncovered, and refreshed the stale status docs.
Zero paid calls, zero store/TM writes, live route untouched.

## Where each handoff phase landed (already on master before this pass)

| Phase | Landed as | Evidence |
|---|---|---|
| 0 — red tests | branch `h1437-phase0-cohort-red-tests`; checkpoints `760cf128`, `b7371537` (8 Codex review findings corrected test-side) | `cohort_engine_selftest.py` pins |
| 1 — prerequisites | attempt/result/run binding + campaign reservation ledger folded into the cohort engine; promotion receipt + reconcile via H1554 Track B (#694, `8def6372`, fixtures `src/pilot/fixtures/cohort_scaffold/`) | CHANGELOG v1.60.0; paid-route hardening block in `RussianTranslation/AGENTS.md` (25-07, `pwg.call_reservation.v1` + `pwg.promotion_journal.v1`) |
| 2 — cohort engine | H1618 Track 2 (#704, v1.60.0): `src/pilot/cohort_engine.py` | 7/7 GREEN (now 10 pins after H1940 Phase 2) |
| 3 — CLI, live-disabled | **PR #843** (`3c21977e`): `--cohort-width` (default 1), `--execute` width>1 refused naming the live-acceptance gate BEFORE any plan/db/fleet access; `run_cohort_offline` thin adapter; Grok PASS verdict committed (`H1437_P3_REVIEW_GROK_2026-07-26.md`); reviewer handoff H1654 archived | selftests (o)/(p)/(q) |
| post-merge hardening | H1940 Phase 2: #899 (probe failure no longer strands cohort leases), #900, #911 (dup lease-id, fsync checkpoint, O(n²) ledger, evidence) | cohort_engine 10 pins |

## Phase-4 battery observed 29-08-2026 (this worktree, master tip + the one fix below)

```text
store_path --selftest                 PASS
headless_worker_selftest              PASS
execution_contract_selftest           PASS
max_account_orchestrator_selftest     PASS   (after the realpath fix below)
bounded_supervisor_selftest           PASS
bounded_staged_run_selftest           PASS   (q) live-refusal pin PASS
cohort_engine_selftest                PASS (10 pins)
window_selftest                       219/219 OK
lang_parity_check                     104 entries, all verdicts complete, no drift
h1339_offline_bench --warmups 2 --runs 10
  total median 2.430s p95 2.665s
  deterministic outputs: True — signature 5cfcedea1c8acf4643229b76c0b292b18e02a356192a4e552a43318e9da80fcd
  fx1..fx5 audit outcomes unchanged (clean / needs_requeue(transient+defect) / clean / clean / clean)
```

Cohort width equivalence (selftest (p), unconditional assertions — wall-clock speedup asserts
stay opt-in via `PWG_ASSERT_WALLCLOCK=1` per the H1654 flake finding): widths 1/2/3 produce
identical clean/requeue decisions, accepted order and store bytes, exact ledger totals, exactly
one promote + one TM call per wave, `peak_concurrency >= 2`; observed wall times
**serial 0.618 s · w2 0.316 s · w3 0.308 s** under delayed fake workers. Offline simulation only —
no real-model speedup is claimed. The live route remains hard-disabled: `--execute` width>1 still
refuses naming the live-acceptance gate (live serial acceptance + Codex sign-off never happened,
by design).

## One master-tip blocker found and fixed in this pass (macOS-only, pre-existing)

`window_selftest::test_c4_gate0_probe_run_scope` (via `h963_c4_gate0_probe.selftest`, case 9c)
failed on macOS: `#1936` (H3642) pinned the env tier of `resolve_health_probe_log` with
`os.path.abspath`, while the sibling resolver `h963_c4_gate0_probe.resolve_evidence_root` — which
the same docstring claims to mirror — uses `Path(...).expanduser().resolve()`. On macOS
`$PWG_EVIDENCE_DIR` under `/var/folders` (symlink to `/private/var/folders`) therefore produced
two different byte strings for the same file, and the two H3642 selftests contradicted each other
(fixing one flipped the other to red). Fix: the env tier now normalizes with `os.path.realpath`
(explicit tier keeps its documented already-resolved semantics; default tier byte-identical and
untouched); the orchestrator selftest pin was corrected to the sibling-consistent expectation.
Both selftests green on macOS; on Windows (`realpath == abspath`) behavior is unchanged.

LANG_PARITY re-verified after the edits: the three `max_account_orchestrator*` pinned verdicts
(`headless_execution_manifest_h818`, `h1339_requeue_materialisation_unattended`,
`h1386_resume_recovery_and_medium50`) are about claim/profile/requeue behavior this path fix
cannot touch — hashes refreshed, verdicts intact, ledger clean.

## Verdict

H1437 stop condition is met on the current tip: offline cohort engine proves `peak_concurrency>=2`
with exact per-window accounting, crash-safe resume, one acceptance barrier + one promotion/TM
callback per wave; all offline gates green; default live route still serial; the cohort width>1
live path remains gated on live-acceptance proof that was deliberately never attempted.

_Dr. Mārcis Gasūns_
