_Created: 24-09-2026 · Last updated: 25-09-2026_

# H5402, 24-09-2026: `kast_ur_i` free gates green, paid run stopped because the minimum spend (4 calls) is over the 3-call cap

Handoff: [H5402](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5402-Opus_SanskritLexicography_pwg-ru-kasturi-promote-after-bot-gate-fix_24.09.26.md). Human ruling, 24-09-2026: option 1, a paid retry, "up to 3 paid calls on `c1` (canary + probe legs + 1 card)". Executor: Opus 5.5 (`claude-opus-5-5`), Mac session driving MSI over Tailscale SSH. Follows [H4527_BOT_BINOMIAL_GATE_FIX_23-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_BOT_BINOMIAL_GATE_FIX_23-09-2026.md).

## 1. Gates run: all green, 0 paid calls (06:06–06:12Z)

1. **Route.** MSI `D:\ClaudeTools\profiles\claude1\.claude\settings.json` was last written 23-09 20:47:52Z. Its `env` keys are `PYTHONUTF8`, `PYTHONIOENCODING`, `DEEPPAPERNOTE_OBSIDIAN_VAULT`, `ENABLE_TOOL_SEARCH`, `SHUNT_MIN_LINES`, `API_TIMEOUT_MS` and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. It has no `ANTHROPIC_BASE_URL`, and neither do the User or Machine environments. No line contains `z.ai` or `glm`. `model` is `sonnet`. Result: **Anthropic route**. Only key names were read.
2. **Ration.** `max_account_orchestrator.py probe-ration --account c1` returned `attempts_today: []` and `legal_now: true`, fingerprint `9321e2c1…acd6b`.
3. **Requeue.** `coordinator.py prepare-requeue --defect h4527vol14` exited 0 and wrote `artifacts\h4527vol14\requeue\rq02-defect\` (manifest v2 plus a harness for 1 card). The TM denylist gained 1 card address. The lease moved from `needs_requeue` to **`requeue_prepared`**.
4. **Zero-call dry run.** `bounded_staged_run.py … --repair-lease h4527vol14 --cohort-path --cohort-width 1 --only-profile c1 --max-calls 2 --run-id h5402-repair-240924` exited 0 with `job_id h4527vol14::rq02-defect`, `projected_calls: 1`, `windows_not_prepared_skipped: []`, admission `serial route (width 1)`. The `--cwd` folder `C:\Users\user\AppData\Local\Temp\pwg-bare-h5402` was created first, so the 23-09 `WinError 267` crash cannot recur.

## 2. Why the paid run did not start

The smallest possible live attempt costs **4** paid calls. The ruling allows **3**.

| Call | Why it cannot be skipped |
|---|---|
| 1 canary (`dq_canary_puregloss`) | `bounded_staged_run.py --execute` refuses to start without a canary GO receipt from the last 6 h (`canary_gate.DEFAULT_MAX_AGE_SECONDS = 6*3600`). The 23-09 receipt is about 28 h old. |
| 2 probe legs (`probe:warmup` + `probe:measured`) | `--execute` always runs a fleet probe first, and there is no flag to skip it. The 23-09 ledger [calls.repair.230923.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/calls.repair.230923.json) shows exactly these two legs ahead of the cards. |
| 1 card (`kast_ur_i~~h0_zz_pw`) | the work itself |

The mint text passes `--max-calls 3` to the driver, which covers probe + card. The ruling text counts the canary inside the 3 as well. Starting anyway would breach the handoff's own fail condition ("more than 3 paid calls"). Starting with a smaller cap would spend the canary and both probe legs, with no card generated.

## 3. State left behind

- Lease `h4527vol14` is `requeue_prepared` (`rq02-defect`). Per the 22-09 note, prepared leases keep, so the run can happen any day.
- `c1` is on Anthropic as of 06:06Z. It has been silently reverted twice before, so re-probe right before the paid run.
- Nothing was spent. The `c1` ration is untouched.

## 4. The run a human authorizes: 4 calls

Run on MSI from `RussianTranslation\src\pilot` after an `ANTHROPIC_BASE_URL` re-probe. Canary per [/pwg-live-gate](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) Step 2 (1 call), then:

```text
python bounded_staged_run.py --plan output\h4527vol\plan.json --coord-dir output\coordinator --coordinator coordinator.py --cwd C:\Users\user\AppData\Local\Temp\pwg-bare-h5402 --events ..\..\pwg_ru\h5402\repair.events.jsonl --repair-lease h4527vol14 --execute --cohort-path --cohort-width 1 --only-profile c1 --canary-receipt <fresh receipt> --max-calls 3 --call-reservation output\h4527vol\calls.h5402.json --run-id h5402-repair-240924 --checkpoint ..\..\pwg_ru\h5402\repair.checkpoint.json --report ..\..\pwg_ru\h5402\repair.report.json
```

## 5. Ruling "yes, 4", then `c1` rejects auth with 403 (06:17–06:22Z)

1. **Human ruling (chat, 24-09-2026):** «yes, 4 and do not reask for such minor spends from now on». The cap is 4 paid calls.
2. **Route re-probe:** `settings.json` was unchanged since 23-09 20:47:52Z, with 0 lines matching `BASE_URL|z.ai|glm`, so it still routes to Anthropic.
3. **Canary manifest** `output\h5402gate`: built at 0 calls, sha256 `c49bd9a50969bf675c3a7d3c729ba9bde850b52d442bdfa47e4a50ba97ccef84`.
4. **Canary** `h5402-canary-240924`, worker capped at `--max-calls 1`: exit 1, classified `process`. The envelope reads `api_error_status 403`, `Failed to authenticate. API Error: 403 Request not allowed`, `duration_api_ms 0`, 0 input and 0 output tokens, 888 ms. The call ledger `calls.canary.json` shows `calls_spent 1`, and no model output was produced.
5. **Auth reading:** `claude auth status` with `CLAUDE_CONFIG_DIR` set to the `c1` profile returned `loggedIn true`, `authMethod claude.ai`, `subscriptionType max`, `apiProvider firstParty`. CLI version 2.1.278; `.credentials.json` last written 23-09 18:29Z. A direct `claude -p` ping got the same 403, again with 0 tokens.
6. **Verdict:** `CANARY_FAIL(auth 403)`, a NO-GO. The paid run was not started, no probe legs or card call were made, and `kast_ur_i` stays `requeue_prepared`. Promotion is blocked on `c1` authentication, not on spend. A human needs to log the `c1` profile in again. After that, the whole section 4 recipe runs unchanged: a fresh canary, then up to 3 more calls.

## 6. Second attempt, 24-09-2026 18:20–18:30Z: auth re-login landed, but the `c1` probe ration is spent until 21:20:17Z

Unattended worker pass (Opus 5 `claude-opus-5[1m]`, Mac session over Tailscale SSH to `msi` / `WIN-NJTORH3267V`). Zero paid calls made, zero code changed. Findings, all live-probed:

1. **Auth re-login DID happen.** `D:\ClaudeTools\profiles\claude1\.claude\.credentials.json` was rewritten **2026-09-24T14:48:44Z** — after the 06:22Z 403. `claude auth status` under that `CLAUDE_CONFIG_DIR`: `loggedIn true`, `authMethod claude.ai`, `apiProvider firstParty`, `subscriptionType max`, org `1ccfe5f5-…`. The §5 blocker as written ("a human needs to log the `c1` profile in again") is **retired**.
2. **Route gate still green.** `settings.json` unchanged since 23-09 20:47:52Z, 0 lines matching `BASE_URL|z\.ai|glm`; no `ANTHROPIC*` variable in either the User or the Machine environment. Anthropic route confirmed.
3. **Ration gate is RED — this is the new blocker.** `max_account_orchestrator.py probe-ration --account c1` (fingerprint `9321e2c1…acd6b`) returns `legal_now: false`, `attempts_today: ["2026-09-24T15:20:17Z"]`, `next_legal_utc: "2026-09-24T21:20:17Z"`, against `max_per_utc_day: 2` / `min_gap_s: 21600`. The subcommand exits **3** when rationed, so `--execute` cannot legally start before 21:20:17Z.
4. **Who spent it: the sibling handoff H5403, not H5402.** The ration ledger's only entry today is `{"purpose": "probe:warmup", "utc": "2026-09-24T15:20:17Z", "pid": 13784}`. `artifact_registry.jsonl` shows an H5403 session preparing four nominal leases (`h5403vol25` `kunt_i`, `h5403vol35` `ma_d_uka`, `h5403vol39` `matsy_akz_i`, `h5403vol40` `mayo_bu`) at 14:49:46–14:55:17Z, a plan at `output\h5403vol\plan.json` 15:17:50Z, and a canary manifest at `output\h5403vgate24\` 15:32:54Z. **That canary never ran** — no `status.canary.json`, no `calls*.json` in that folder, and no file anywhere under `pilot\output` written after 15:32:54Z. So no card was generated on `c1` today by anyone, and there is still **no receipt proving a 200 on `c1` since the re-login** — auth is *probably* fixed (§6.1) but is **unproven** until the next canary.
5. **`kast_ur_i` is untouched and still ready to go.** Lease `h4527vol14` remains `requeue_prepared` at attempt 2 (`rq02-defect`, prepared 06:09:09Z, `selected_keys: ["kast_ur_i~~h0_zz_pw"]`, preflight sha256 `901263660c89c070…e1e00f91d`). The §4 recipe applies unchanged.
6. **Nothing was overridden.** `legal_now: false` is a gate, and the handoff's own fail condition plus [rules/agent-never-self-authorizes-an-escape.md](https://github.com/gasyoun/claude-config/blob/main/rules/agent-never-self-authorizes-an-escape.md) forbid a session from ruling itself past it. The worker stopped here rather than spend.

### What the next session does (no human action needed)

At or after **2026-09-24T21:20:17Z** — and noting that this is the day's **second and last** probe attempt, so the H5403 session must not take it first — re-run the §4 recipe from the top on `msi`, in `RussianTranslation\src\pilot`:

```text
python max_account_orchestrator.py probe-ration --account c1
```

must exit 0 with `legal_now: true`; then the fresh `dq_canary_puregloss` canary (1 call, the auth proof §6.4 is missing), then the §4 `bounded_staged_run.py` line. Cap: 4 paid calls total, per the second ruling. If the canary 403s again, the blocker reverts to auth and belongs to a human.

## 7. Third attempt, 24-09-2026 23:05–23:20Z: auth 403 RETIRED by a live canary GO — new blocker is the H2157 cost-gate shape, one word from a human

Unattended worker pass 1 on executor Claude/c1 (Opus 5 `claude-opus-5[1m]`), running **locally on MSI** (no SSH hop). **1 paid call spent of the 4 authorized.** `kast_ur_i` is still `requeue_prepared` — not promoted.

### 7.1 Free gates, all green

1. **Route.** `settings.json` `env` keys are `API_TIMEOUT_MS`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DEEPPAPERNOTE_OBSIDIAN_VAULT`, `ENABLE_TOOL_SEARCH`, `PYTHONIOENCODING`, `PYTHONUTF8`, `SHUNT_MIN_LINES` — no `ANTHROPIC_BASE_URL`; `grep -ic "BASE_URL|z\.ai|glm"` over the file returns **0**; no `ANTHROPIC*` variable in the shell environment. **Anthropic route.**
2. **Ration.** `probe-ration --account c1` exit **0**, `legal_now: true`, `attempts_today: ["2026-09-24T15:20:17Z"]` (the H5403 entry from §6.3), `next_legal_utc` now in the past against `min_gap_s: 21600`. Fingerprint `9321e2c1…acd6b`. One of the day's two attempts remains.
3. **Lease.** `h4527vol14` unchanged at attempt **2** (`rq02-defect`, `current_artifact_dir …/requeue/rq02-defect`), `config_dir` the `c1` profile. The §4 recipe still applies.

### 7.2 The auth blocker of §5 is RETIRED — proven, not inferred

A fresh canary was built and run (1 paid call, the only spend of this pass):

- **Build (0 calls):** `canary_manifest_build.py --profile-slot c1 --outdir src/pilot/output/h5402gate25`, manifest sha256 `16d1596c5b79cebf5f214c6d56f3caac4343c264762f1aa1e29883045294b8a4`.
- **Execute (1 call):** `headless_worker.py … --only-profile c1 --max-agents 1 --timeout 600 --max-calls 1 --run-id h5402-canary-250925`. Exit **0**, `classification: "success"`, `elapsed_ms 19064`, `result_sha256 15c9a8b2…7084fd1`. Ledger [calls.canary.250925.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5402/calls.canary.250925.json): `calls_spent 1`, purpose `headless:translate`, profile `c1`.
- **Judge (0 calls):** `canary_gate.py judge` → **`CANARY GO`**. Receipt [canary_receipt.250925.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5402/canary_receipt.250925.json): `verdict GO`, `reasons []`, `sense_counts [["dq_canary_puregloss~~h0_zz_pw", 3]]`, `tn_hits []`, `marker_hits []`.

Against §5.4's `403 Request not allowed` / 0 tokens, and §6.4's "no receipt proving a 200 on `c1` since the re-login" — **that receipt now exists.** `c1` authenticates and generates.

### 7.3 Zero-call dry run: still green

`bounded_staged_run.py … --repair-lease h4527vol14 --cohort-path --cohort-width 1 --only-profile c1 --max-calls 3 --run-id h5402-repair-250925` exit **0**, `projected_calls: 1`, cohort `serial (production default, width 1)`, `live_admission.admitted true` (`serial route (width 1)`), `validated_accounts ["c1"]`. The `--cwd` scratch folder was created first, so the §6/23-09 `WinError 267` cannot recur.

### 7.4 The new blocker: the §4 recipe as authorized cannot start

Running the §4 line verbatim with `--execute` exits **2 before any spend**, on argparse:

```text
bounded_staged_run.py: error: --execute is a PAID run and refuses to start unbounded:
missing --cost-ceiling (H2157). Pass explicit ceilings, or --allow-unbounded for a
deliberate unbounded window.
```

The §4 recipe carries neither flag, so **the authorized command is not runnable as written**. Both ways out were examined and neither is an agent's to take:

1. **`--cost-ceiling <usd>` — provably burns 2 paid calls for 0 cards on this lane.** The fleet probe's two legs land in the same `--call-reservation` ledger *before* the supervisor loop, and Max-route calls carry no usage telemetry, so at the top of iteration 1 `budget_cap is not None and not self._durable_cost_evaluable` fires `STOP_COST_UNEVALUABLE` ([bounded_supervisor.py:301-303](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_supervisor.py#L301)). Measured live **this pass**, not assumed: the canary ledger reads `cost_evaluable: false`, `observed_cost_usd: 0.0`; the 23-09 ledger [calls.repair.230923.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/calls.repair.230923.json) reads `unevaluable_calls: 4` of 4. [H3659](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3659/H3659_NO_PWG_W09_WINDOW_29-08-2026.md) already named the consequence: "while billing telemetry is dormant, a cost-bounded window on this lane is not merely unpriced; it is **unrunnable**." It would also consume the day's last ration attempt.
2. **`--allow-unbounded` — the disclosed escape, and not mine to issue.** It leaves `budget_cap = None` and skips the guard; `--max-calls 3` and the window cap still bind pre-spawn, so only *dollars* go unbounded, and they are unmeasurable on this lane either way. H3659 ruled on exactly this substitution in exactly these terms: the flag exists to be visible in command review for a *deliberate* unbounded window, "substituting one for the other on an agent's own judgment is exactly the guard-tunnelling defect recorded at H2851. The choice belongs to a human." The H5402 rulings authorized a **spend** (4 calls, «do not reask for such minor spends») — they say nothing about the guard shape, and [rules/agent-never-self-authorizes-an-escape.md](https://github.com/gasyoun/claude-config/blob/main/rules/agent-never-self-authorizes-an-escape.md) rule 1 forbids setting an `ALLOW_*`-shaped override in response to a refusal just hit. Splitting the probe onto a second ledger to leave the supervisor's ledger empty at loop start would tunnel the same guard less visibly, and was rejected for that reason.

Note the 23-09 run that remade `dārvī` and generated this very `kast_ur_i` card completed 4 unpriced calls, so the human's own PowerShell line that day must have carried `--allow-unbounded`; the abridged quote in [the 23-09 packet](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_REPAIR_RUN_DARVI_REMADE_KASTURI_GATE_FALSE_POSITIVE_23-09-2026.md) §1 omits it. That is a human having chosen the escape once, not a standing delegation.

### 7.5 Selftests

`bounded_staged_run_selftest.py` → **PASS** (exit 0); `cohort_engine_selftest.py` → **PASS (12 pins)** (exit 0). Both run from the main checkout's `src/pilot`.

### 7.6 State left behind

- `kast_ur_i` (`h4527vol14`) is `requeue_prepared`, attempt 2 `rq02-defect` — **not promoted**. Prepared leases keep; the run can happen any day.
- **Spend: 1 paid call** (the canary) of the 4 authorized. 3 remain authorized.
- **Ration: 1 of 2 attempts still free today** — no fleet probe ran. It resets at 00:00Z.
- Canary receipt is fresh for 6 h from 23:11Z, i.e. usable until **2026-09-25T05:11Z**; after that a new canary is another call.
- Nothing was overridden, no code changed.

### 7.7 What a human does — one word

The whole unblock is choosing the dollar-axis flag. In plain words: the runner refuses to start a paid window unless it is told either a dollar ceiling or that dollars are deliberately not capped; on a Max subscription the API reports no per-call price, so a dollar ceiling stops the run dead after it has already paid for two warm-up probes. Reply in chat with **"run it unbounded"** (or decline), and any session runs, from `RussianTranslation\src\pilot` on MSI, within the canary's freshness window:

```text
python bounded_staged_run.py --plan output\h4527vol\plan.json --coord-dir output\coordinator --coordinator coordinator.py --cwd C:\Users\user\AppData\Local\Temp\pwg-bare-h5402 --events ..\..\pwg_ru\h5402\repair.events.jsonl --repair-lease h4527vol14 --execute --cohort-path --cohort-width 1 --only-profile c1 --canary-receipt output\h5402gate25\receipt.canary.json --allow-unbounded --max-calls 3 --call-reservation output\h4527vol\calls.h5402.json --run-id h5402-repair-250925 --checkpoint ..\..\pwg_ru\h5402\repair.checkpoint.json --report ..\..\pwg_ru\h5402\repair.report.json
```

**If you say it:** `kast_ur_i` is generated and promoted into the store with Anthropic-id provenance, ~3 more paid calls, ~5 minutes. **If you do not:** the card stays `requeue_prepared` indefinitely — H5402 cannot close, and the H4527 volume-14 lease stays one card short. **Откат:** none needed; a failed window re-requeues the lease with the defect named and spends nothing further.

_Гасунс_
