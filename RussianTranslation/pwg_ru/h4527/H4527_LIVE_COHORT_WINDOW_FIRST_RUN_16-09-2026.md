# H4527 — the first live window ever dispatched through the cohort path (width 1, c1, 16-09-2026)

_Created: 16-09-2026 · Last updated: 16-09-2026_

Executor: Opus 5 (`claude-opus-5`), unattended worker on the Mac driving the MSI box over
tailnet ssh. Elapsed ~30 min. **Paid calls: 2** — one `dq_canary_puregloss` control, one
translation window call. Probe attempts spent on `c1`: **1** (the window's own warm-up +
measured pair, which the ration counts as one attempt).

## What happened, in order

| # | Step | Result |
|---|---|---|
| 1 | `max_account_orchestrator.py probe-ration` (H4527 read-only reporter, zero calls) | exit 3 at 08:43:31Z (`next_legal_utc 08:46:48Z`), exit **0** at 08:47:46Z — `legal_now: true` |
| 2 | `canary_manifest_build.py --profile-slot c1` (zero calls) | manifest sha256 `330645e09b79ac7d3b40923367337db7922d68e3c5c30caa2fef8131a7cb47a7` |
| 3 | `headless_worker.py` on the canary manifest (**1 paid call**) | `classification: success`, 29 427 ms, key `dq_canary_puregloss~~h0_zz_pw`, `cli_safe_mode_effective: true` |
| 4 | `canary_gate.py judge` | **CANARY GO** → `src/pilot/output/h4527gate0916/canary_receipt.json`, run `h4527-canary-160916` |
| 5 | `bounded_staged_run.py` dry run (zero calls) | `importable_prepared_leases: ["h4527acc05"]`, 1 window, 1 subcard, `live_admission.admitted: true (serial route, width 1)` |
| 6 | `bounded_staged_run.py --execute --cohort-path --cohort-width 1` (**1 paid call**) | the window RAN; exit 1 on a transient null card (below) |

## The route is proven live; the acceptance record is not writable yet

**Proven for the first time** — before this pass the cohort path had never dispatched a live
paid call at any width:

- **Readiness probe passed on both legs:** warm-up 16 453 ms (api 10 266), measured 17 008 ms
  (api 19 523), both `classification: success`, `policy: production_v4` (240 000 ms ceiling),
  `cli_safe_mode_effective: true`, `probe_prompt_sha: 90e2f1f6698b`. That is the **third**
  independent clean reading since the 15-09 injection-shape repair, and the fastest yet.
- **The cohort dispatch bound, dispatched, audited and settled exactly one wave:**
  `cohort.path: "live"`, `fleet: ["c1"]`, `reason: "fleet admits width 1: c1"`,
  `peak_concurrency: 1`, `effective_width: 1`.
- **Accounting is exact:** `calls_spent: 1` = `calls_reserved: 1` against `--max-calls 3`;
  one `attempt_start` → one `model_call` (80 818 ms, `classification: success`) → one
  `attempt_end` in the run events; one wave promote (`wave.promoted: true`) and one TM
  callback (`wave.tm_done: true`) — the single-promoter rule held.
- **No guardrail was touched:** no `--skip-canary-gate`, no `ALLOW_*`, no retry after the
  audit verdict. `--allow-unbounded` was passed because the cohort path refuses the
  supervisor's `--cost-ceiling` by design (rung 4's contract); `--max-calls 3` stayed the bound.

**Not proven, and therefore NOT recorded:** the card came back **null**, class
`missing-or-mismatched-key` (transient, not a content defect):

```
cards 1 · clean keys 0 · requeue 1 (asa_mskfta~~h0_zz_nws00) · transient 1 · defect 0
lease h4527acc05 -> transient_only ; accepted_order: [] ; store_delta: null
```

The call itself succeeded (`returncode 0`, 6 873 output tokens, 64 343 cache-read,
`budget_stops: 1`); the harness could not match the returned card to the nominal masked key
`asa~005fmskfta~007e~007eh0~005fzz~005fnws00`. So the wave promoted an **empty** accepted set.
A width-1 window that accepts nothing cannot prove «sealed artifacts, journal advancement and
promotion discipline match the serial route byte-for-byte» on an accepted card — the very
claim the acceptance record exists to carry. **`COHORT_LIVE_ACCEPTANCE.json` was therefore left
unwritten**: fail-closed is the correct reading of a null-card window, and writing
`serial_acceptance.via_cohort_path: true` off this run would have been the silent gate-opening
this handoff's own Fail-list bans.

## Evidence (committed with this packet)

- [acceptance.report.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/acceptance.report.json) — full `pwg.bounded_staged_run.v1` report, run `h4527acc160916`
- [acceptance.events.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/acceptance.events.jsonl) — probe pair, dispatch, model call, attempt end
- [acceptance.checkpoint.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/acceptance.checkpoint.json)
- On the MSI box (gitignored, durable): `src/pilot/output/coordinator/artifacts/h4527acc05/`
  (`wf_output`, `audit_window.report.json`, `window_status.json`, `window_ledger.jsonl`) and
  `src/pilot/output/h4527gate0916/` (canary manifest, output, receipt, reservation ledger)

## Ration state after this pass

`c1` has now spent **both** attempts for 16-09 UTC — 02:46:48Z (a sibling session) and
08:48Z (this window's own probe). The next legal attempt is **17-09-2026 00:00Z**. There is no
second try today, so the rerun below is a next-day action, not a retry.

## Ordered next step (earliest 17-09-2026 00:00Z)

1. `python src/pilot/max_account_orchestrator.py --db src/pilot/max_orchestrator.sqlite probe-ration --account c1` — exit 0 means go.
2. Re-prepare or resume lease `h4527acc05` (it settled `transient_only`, so its key
   `asa_mskfta~~h0_zz_nws00` is in the requeue backlog — a transient requeue is a cheap re-run,
   not a rework).
3. Buy a fresh `dq_canary_puregloss` GO receipt (one paid call, no probe attempt).
4. Re-run the same command as step 6 above. **A clean accepted card is the whole remaining
   acceptance**: with one accepted key the report carries `accepted_order`, a store delta and a
   promotion receipt, and only then may `COHORT_LIVE_ACCEPTANCE.json` record
   `serial_acceptance.via_cohort_path: true`.
5. Work item 2 (Codex sign-off) and the money-class `## Verifier` PASS each still need a
   different session. Work item 3 (width 2) stays parked on the one-lane condition of the
   11-09 MG ruling.

**The armed command, verbatim** (run from `RussianTranslation\src\pilot` on MSI; it needs
`--coordinator`, `--cwd` and `--events`, which every earlier armed form in this handoff omitted
— `--execute` exits at argparse without them, and `--cwd` must be a **bare scratch dir**, never
the repo, per H2158):

```sh
python bounded_staged_run.py --plan output\h4527acc\plan.v2.json --coord-dir output\coordinator --coordinator coordinator.py --cwd %TEMP%\pwg-bare-h4527acc --events ..\..\pwg_ru\h4527\acceptance.events.jsonl --lease-id h4527acc05 --execute --cohort-path --cohort-width 1 --only-profile c1 --canary-receipt <fresh GO receipt> --max-calls 3 --allow-unbounded --call-reservation output\h4527acc\calls.acc.json --run-id <run-id> --checkpoint ..\..\pwg_ru\h4527\acceptance.checkpoint.json --report ..\..\pwg_ru\h4527\acceptance.report.json
```

## Notes worth keeping

1. **The `--coordinator/--cwd/--events` omission cost nothing this time only because argparse
   fails before the probe.** Every armed command recorded in this handoff since 11-09 would
   have exited 2. The form above is the one that actually ran.
2. **`CLAUDE_CONFIG_DIR` is required for the canary leg** (H3144) and was set to
   `D:\ClaudeTools\profiles\claude1\.claude` for both paid legs.
3. **Cost is not evaluable on this route:** the window's usage block carries
   `observed_cost_usd: 0.0` with `cost_evaluable: false` — that zero is *not measured spend*.

_Гасунс_
