_Created: 24-09-2026 · Last updated: 24-09-2026_

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

_Гасунс_
