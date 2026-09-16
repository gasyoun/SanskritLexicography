# H4527 — 16-09-2026: the window was legal for the first time, and a sibling had already spent the ration

_Created: 16-09-2026 · Last updated: 16-09-2026_

Pass 4 of [H4527](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4527-Opus_RussianTranslation_pwg-ru-cohort-live-acceptance-width2_10.09.26.md)
(Opus 5 `claude-opus-5`, unattended worker on MSI, **0 paid calls**). The 15-09 (3) pass set a
floor of 16-09 00:00Z for the acceptance window. That floor has passed. The window still did not
run, and the reason is new.

## What was probed, live, this pass

| Check | Command | Result |
|---|---|---|
| UTC clock | `date -u` | `2026-09-16T02:49:48Z` — past the 00:00Z floor |
| Shared checkout | `git fetch origin && git log -1 origin/master` | `8a0889c41` (H4915, #2243) — **at origin/master**, step 2 of the ordered list already true |
| Lease + admission | `bounded_staged_run.py --plan output/h4527acc/plan.v2.json --coord-dir output/coordinator --lease-id h4527acc05 --cohort-path --cohort-width 1 --only-profile c1` (dry run, zero calls) | `importable_prepared_leases: ["h4527acc05"]`, 1 window, 1 subcard, `live_admission.admitted: true (serial route, width 1)` |
| Probe ration | ledger `%TEMP%/pwg-probe-ration/9321e2c1…jsonl` | one attempt on 16-09 UTC at **02:46:48Z** — **next legal 08:46:48Z** |

## The blocker: a sibling lane spent today's ration three minutes before this pass started

The H4915 ration ledger records exactly one attempt for `c1` on 16-09 UTC: **02:46:48Z**, pid 31592
(`purpose: probe:warmup`). The matching rows in
`RussianTranslation/src/pilot/output/health_probe_log.jsonl` show both legs of that probe returning
`classification: success` — warm-up 8 712 ms, measured 9 274 ms, `cli_safe_mode_effective: true`,
`probe_prompt_sha: 90e2f1f6698b`, against the 240 000 ms `production_v4` ceiling. **The 15-09 probe
fix is confirmed working on a second, independent reading** — 4–7× faster than the 11-09 readings,
and the first clean `success` pair since the injection-shape repair.

That attempt was not this handoff's. It came from another session on the same box, and the ration is
machine-wide by design (H4915's whole point). `PROBE_RATION_MIN_GAP_S` is 6 h, so:

```
last attempt 2026-09-16T02:46:48Z + 6 h  ⇒  next legal 2026-09-16T08:46:48Z
```

`bounded_staged_run.py --execute` calls `mao.probe_fleet` unconditionally
([bounded_staged_run.py:1064](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run.py)),
and `probe_fleet` now pre-checks the ration for every profile before spending anything. So the
acceptance window is **code-refused** until 08:46:48Z. Nothing was overridden, no `ALLOW_*` was set,
no `--skip-canary-gate` was reached for; the handoff's own instruction is that a limit resetting is
a wait, not a defect.

**The canary was deliberately NOT bought.** A `dq_canary_puregloss` GO receipt is valid 6 h. Buying
one at ~03:00Z would expire at ~09:00Z, minutes after the window becomes legal — a paid call spent
on a receipt that would be a coin-flip at use time. The receipt is bought on the next pass, after
08:46:48Z, where it costs one call and no probe attempt.

## Shipped this pass: the ration is now readable without spending an attempt

H4915 made the ration a **code gate** but left it readable only by *attempting* a probe —
`probe_fleet` and `_probe_call` raise `ProbeRationRefused`, and that was the only surface. Two
consecutive passes of this handoff (15-09 (3), and this one) therefore had to learn the lane was
closed by hand-grepping a JSONL under `%TEMP%`. A batch drain, which claims a handoff *before* it
reads anything, cannot do even that — which is exactly the dispatcher gap the 15-09 (3) pass named
and left open, and it has now cost two dispatches.

New read-only subcommand, zero calls and zero writes:

```sh
python src/pilot/max_account_orchestrator.py --db src/pilot/max_orchestrator.sqlite probe-ration
```

Exit **0** = a probe is legal now for every validated profile · **3** = at least one is rationed ·
**1** = the ledger is unreadable (fail closed, the same verdict the gate itself gives). Live output
this pass:

```json
{"account": "c1", "attempts_today": ["2026-09-16T02:46:48Z"],
 "last_attempt_utc": "2026-09-16T02:46:48Z", "next_legal_utc": "2026-09-16T08:46:48Z",
 "legal_now": false, "ledger": "C:\\Users\\user\\AppData\\Local\\Temp\\pwg-probe-ration\\9321e2c1….jsonl"}
```

It reports the recorded attempts and the next legal UTC time per profile, so a dispatcher can branch
on an exit code instead of parsing prose. Pinned by
`_test_h4527_probe_ration_status_is_readable_without_probing`: exit 3 when rationed, exit 0 when
legal, **zero spawns and zero ledger writes either way**, and an unknown `--account` refuses rather
than reporting a falsely green empty set.

## Checks

| Gate | Result |
|---|---|
| `window_selftest` | **225/225** |
| `max_account_orchestrator_selftest` | PASS (new H4527 pin) |
| `cohort_engine_selftest` | 10 pins PASS |
| `cohort_live_admission_selftest` | 6 pins PASS |
| `cohort_live_dispatch_selftest` | 6 pins PASS |
| `bounded_staged_run_selftest` | PASS |
| `call_reservation_selftest` | PASS |
| `lang_parity_check` | 115 entries, all verdicts complete, no drift (8 entries re-derived, verdicts stand) |

Nothing was launched, so no
[LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
entry is owed. **A ration refusal is not a launch failure** — it is the guard working, and the
attempt it protected was a sibling's legitimate one.

## Ordered next step (unchanged in shape, with one step now cheap)

1. `python src/pilot/max_account_orchestrator.py --db src/pilot/max_orchestrator.sqlite probe-ration`
   — exit 0 means go, exit 3 prints the wall-clock time to wait for. Earliest today: **08:46:48Z**.
2. Buy a fresh `dq_canary_puregloss` GO receipt (one paid call, no probe attempt).
3. From `RussianTranslation\src\pilot`:

```sh
python bounded_staged_run.py --plan output\h4527acc\plan.v2.json --coord-dir output\coordinator --lease-id h4527acc05 --execute --cohort-path --cohort-width 1 --only-profile c1 --canary-receipt <fresh GO receipt> --max-calls 3 --allow-unbounded --checkpoint ..\..\pwg_ru\h4527\acceptance.checkpoint.json --report ..\..\pwg_ru\h4527\acceptance.report.json
```

4. Audit, compare against the serial route, write the packet, then the acceptance record with
   `serial_acceptance.via_cohort_path: true`.
5. Work item 2 (Codex sign-off) and the money-class `## Verifier` PASS each still need a different
   session. Work item 3 (width 2) stays parked on the one-lane condition of the 11-09 MG ruling —
   nobody is waiting to decide it.

**Timing note for whoever runs step 3:** `--max-calls 3` is needed because the warm-up and measured
probe legs draw from the same ledger as the card call. The window's own probe *is* the day's second
attempt, so once it runs the lane is closed until 17-09 00:00Z — there is no third try today.

_Гасунс_
