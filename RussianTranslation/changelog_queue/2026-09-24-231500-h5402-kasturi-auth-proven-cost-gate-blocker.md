- H5402: **`c1` auth is proven live again — `kast_ur_i` now waits only on which dollar-axis
  flag a human picks.** A third unattended pass ran locally on `msi` at 23:05–23:20Z and spent
  **1 paid call of the 4 authorized**. The §5 auth blocker is retired with a receipt rather
  than an inference: a fresh `dq_canary_puregloss` canary (manifest sha256 `16d1596c…5294b8a4`)
  returned `classification success` in 19 064 ms and `canary_gate.py judge` wrote
  **`CANARY GO`** with `reasons []` and `sense_counts [["dq_canary_puregloss~~h0_zz_pw", 3]]`
  — against §5's `403 Request not allowed` at 0 tokens, and closing §6.4's gap that no 200 on
  `c1` had been observed since the re-login. Route still Anthropic (0 lines matching
  `BASE_URL|z\.ai|glm`, no `ANTHROPIC*` in either environment); `probe-ration --account c1`
  exit 0 / `legal_now true` with one of the day's two attempts still unspent; the zero-call dry
  run green at `projected_calls 1`, `live_admission.admitted true`; `bounded_staged_run_selftest`
  and `cohort_engine_selftest` (12 pins) both PASS. What blocks now is a **shape, not a spend**:
  the authorized §4 recipe carries neither `--cost-ceiling` nor `--allow-unbounded`, so
  `--execute` exits 2 on H2157 before spending anything. A cost ceiling is unrunnable on this
  lane — Max-route calls report no usage telemetry (this pass's own ledger: `cost_evaluable
  false`, `observed_cost_usd 0.0`; the 23-09 ledger: `unevaluable_calls 4` of 4), so
  `STOP_COST_UNEVALUABLE` fires at the top of loop iteration 1 after the two fleet-probe legs
  have already been paid for. `--allow-unbounded` skips that guard and leaves `--max-calls`
  binding, but H3659 ruled that substituting it for a bounded authorization on an agent's own
  judgment is the H2851 guard-tunnelling defect, so the worker stopped rather than issue itself
  the escape. Lease `h4527vol14` stays `requeue_prepared` (`rq02-defect`,
  `kast_ur_i~~h0_zz_pw`); 3 paid calls remain authorized; the canary receipt is fresh until
  2026-09-25T05:11Z. Nothing was overridden and no code changed. Evidence §7:
  [H5402_KASTURI_GATES_PASSED_STOPPED_ON_CALL_CAP_24-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5402/H5402_KASTURI_GATES_PASSED_STOPPED_ON_CALL_CAP_24-09-2026.md).
