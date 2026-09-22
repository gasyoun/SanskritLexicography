# H4527 — repair-lease driver shipped, zero-call dry run green, c1 back on z.ai (22-09-2026)

_Created: 22-09-2026 · Last updated: 22-09-2026_

Opus 5.5 (`claude-opus-5-5`), Mac session driving MSI over Tailscale SSH. **0 paid calls.**
Follows [H4527_C1_ANTHROPIC_ROUTE_RESTORED_VOLUME_LAUNCH_22-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_C1_ANTHROPIC_ROUTE_RESTORED_VOLUME_LAUNCH_22-09-2026.md)
(its afternoon addendum specified this driver change).

## 1. What shipped

[#2310](https://github.com/gasyoun/SanskritLexicography/pull/2310) merged 20:37:10Z as `d1324403f`. It superseded [#2309](https://github.com/gasyoun/SanskritLexicography/pull/2309): the stale-base guard refused an own-line follow-up on the pushed branch, so the change was squashed onto a new ref. No override was used.

1. `bounded_staged_run.py --repair-lease <id>` (repeatable, never together with `--lease-id`) scopes a paid run to the named leases only. A `requeue_prepared` lease drains its prepared `<lease>::rqNN-<kind>` attempt. A prepared `defect-repair` lease imports like any prepared lease. Every other state is refused. All gates still apply: canary receipt, probe ration, `--max-calls` reservation, preflight validation.
2. `coordinator.py claim --kind defect-repair --nominal` re-makes a no-PWG nominal card. It is built the way the planner built the original (grammar layer on), with `--no-tm` on both children.
3. An independent logic critic (read-only Opus agent) returned PASS-WITH-NOTES. All three should-fixes are in the merged commit:
   - A requeue of a defect-repair lease now stays TM-off, including a transient requeue. Without this, a 0-call TM hit would have promoted the card's own defective text as "repaired".
   - A `run()`-level pin proves `--execute` validates only the named leases. I mutation-tested it: reverting the scope line turns it red.
   - A repair run is documented as not resumable once dispatched. It fails closed, and the operator finishes by hand.
4. Gates: `window_selftest` 229/229, `bounded_staged_run_selftest` PASS, `coordinator_hardening_selftest` PASS, `cohort_engine_selftest` 12/12, `lang_parity_check` clean.
5. H1618 twin: [claude-config#505](https://github.com/gasyoun/claude-config/pull/505) (`/pwg-bounded-run`). It still needs a merge; see §4.

## 2. Zero-call preparation on MSI (checkout at `d1324403f`)

1. `darv_i` re-make lease: `coordinator.py claim --lane no_pwg_windows100 --kind defect-repair --owner h4527-redo --lease-id h4527dr01 --root darv_i --keys darv_i~~h0_zz_pw --nominal`, then `prepare h4527dr01 --profile-slot c1 --config-dir D:\ClaudeTools\profiles\claude1\.claude`. The lease is `prepared`, with harness `artifacts\h4527dr01\run_pilot_wf.h4527dr01.js`. Its preflight shows `tm_auto: false`, 0 TM hits, `agent_expected_after_tm: 1`. Prepared leases do not expire; only `claimed` ones have a TTL.
2. Dry run (no `--execute`), saved as [repair.dryrun.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/repair.dryrun.json) (sha256 `13e2547ed51079841ef7b2d5b4b226e06f942473b231f11477a9bfebaa7ad0ef`):

   | field | value |
   |---|---|
   | `lease_ids` | `h4527vol14`, `h4527dr01` |
   | `repair_leases` | `h4527vol14` → job `h4527vol14::rq01-defect` (`kast_ur_i~~h0_zz_pw`, 1 call); `h4527dr01` → job `h4527dr01` (`darv_i~~h0_zz_pw`, 1 call) |
   | `projected_calls_from_plan` | **2** |
   | `windows_not_prepared_skipped` | none |
   | cohort | width 1, serial route, admitted |

   **Acceptance 1 of the (2) spec is met:** the two named leases are importable, 2 calls are projected, and nothing else is in scope.

   Hash note: `13e2547e…` is the CRLF file as written on MSI. The committed copy is LF-normalized by git, and its sha256 is `8a22ad66e737426cad8afcd2fa93a3103126dff881701415b218476618fe9570`.
3. The dry run rewrote `progress_dashboard/progress_data.json` and `progress_timeseries.json`, the known hazard. Both were restored. Right afterwards `kitchen_data.json` and `quality_timeseries.json` showed as modified. The dry run did not touch those two (they were absent from its post-run status), so they were left alone.
4. Probe ration for c1 at 20:41:51Z: one attempt today (11:45:13Z), `legal_now: true`. One probe is left for the 22-09 UTC day, and the count resets at 00:00Z.

## 3. Blocker for the paid run: c1 is on z.ai again

`D:\ClaudeTools\profiles\claude1\.claude\settings.json` has `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic` again. The file was rewritten at **13:06:49Z** on 22-09 and is byte-identical to `settings.json.pre-h4527-restore-anthropic-22-09.bak`. No commit or note records who did this. It was still set at 20:25Z.

The 22-09 volume run (11:45–11:50Z) happened before the revert, so its cards came from Anthropic. A paid run now would make both cards with GLM under a `claude-sonnet-5` label, which is the exact defect this redo exists to undo. **No paid call was made.** A human decides the route.

## 4. What a human decides / does

1. **The c1 route.** Either restore Anthropic on c1 again, as ruled 22-09 («restore Anthropic»), or leave c1 on z.ai.
   - **If restored:** the next session runs the redo: a fresh canary (1 call), then the run below, 2 probe legs + 2 cards under `--max-calls 4`, so 5 paid calls in total. `kast_ur_i` is promoted or re-requeued with its defect named. The three `darv_i` rows are replaced by Anthropic output.
   - **If not:** `kast_ur_i` stays `requeue_prepared` and `darv_i` stays GLM-made in the store, both waiting. Nothing is lost. The prepared leases keep, and the run can happen any day.
   - Someone switched c1 back to z.ai at 13:06Z. If that was deliberate (for example, to share the Max quota with another lane), a restore will fight it. Whoever owns c1 should say which route it serves.
2. **Merge [claude-config#505](https://github.com/gasyoun/claude-config/pull/505)** (doc-only twin). Its CI jobs never got a runner: 0 steps, and `main` shows the same failures. The agent's merge over red checks was blocked by the permission classifier.

The paid-run argv for the next session, run from `RussianTranslation\src\pilot` on MSI after a fresh `CANARY GO` receipt and a re-probe of `ANTHROPIC_BASE_URL`:

```text
python bounded_staged_run.py --plan output\h4527vol\plan.json --coord-dir output\coordinator --coordinator coordinator.py --cwd C:\Users\user\AppData\Local\Temp\pwg-bare-h4527rep --events ..\..\pwg_ru\h4527\repair.events.jsonl --repair-lease h4527vol14 --repair-lease h4527dr01 --execute --cohort-path --cohort-width 1 --only-profile c1 --canary-receipt <fresh receipt> --max-calls 4 --allow-unbounded --call-reservation output\h4527vol\calls.repair.json --run-id h4527-repair-<yymmdd> --checkpoint ..\..\pwg_ru\h4527\repair.checkpoint.json --report ..\..\pwg_ru\h4527\repair.report.json
```

_Гасунс_
