_Created: 11-09-2026 · Last updated: 11-09-2026_

# H4527 rung 4 — the live cohort dispatch is wired; what now blocks the paid half is the fleet, not the code

**Executor:** Opus 5 (`claude-opus-5`), interactive `/go H4527` session on the Windows box.
**Handoff:** [H4527](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4527-Opus_RussianTranslation_pwg-ru-cohort-live-acceptance-width2_10.09.26.md) (Opus 5, 🔴3 hard, class **money**).
**Predecessor in the same handoff:** the offline admission gate, [PR #2170](https://github.com/gasyoun/SanskritLexicography/pull/2170), merged to `master` as `233256d5d` this session after an independent read of the diff (fail-closed in every branch, code-capped width, evidence-bearing record, no environment override, (q) pin edited deliberately; 10/10 checks green, `mergeStateStatus: CLEAN`).
**Scope executed here:** rung 4 (live cohort dispatch wiring) + the rung-1 record amendment it forces. **Zero paid calls.**

## What changed

| Piece | What it does | Why it had to exist |
|---|---|---|
| [`cohort_live_dispatch.assign_profiles`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cohort_live_dispatch.py) | binds each plan-scoped window to a probed-healthy profile, deterministically, round-robin in plan order | `CohortEngine` enforces one in-flight job per profile; a window with no `profile` is read as **not in fleet**, so an unbound wave settles having dispatched nothing — on a paid lane that reads as "the window ran and found no work" |
| `fleet_guard` | refuses width N unless N **distinct** probed-healthy profiles exist | a width the fleet cannot fill is a lie, not a wave. Refusing beats shrinking: a caller that asked for 2 and silently got 1 has been told a wave ran when a serial window did |
| `make_wave_promoter` | one `promote-ready --lease-id …` for the whole accepted set | the coordinator promotes that bundle in **one** `promote_final_cards.batch_promote` transaction, so "exactly one promote per wave" is true the first time it runs live rather than aspirational |
| `bounded_staged_run.run_window` | honours an optional per-window `profile` binding; stands its per-lease promote down when the window carries `wave_promote` | without the stand-down a wave would promote N times; without the binding the engine's invariant is decorative. **No binding ⇒ byte-for-byte the previous serial behaviour** |
| `--cohort-path` | runs the LIVE window through the cohort dispatch at `--cohort-width` (default 1) | this is the route work item 1 asks for — "one bounded headless window **through the cohort path** at width 1". Before this flag there was no way to run the cohort path live at all, at any width |
| `cohort_live_admission` + `via_cohort_path` | the acceptance record must record that its window went through the cohort path | now that both routes can run width 1, only a cohort-path window is evidence about the code a width-2 wave uses. A serial-supervisor window proves the route, not the wiring |

**Ceilings, stated rather than dropped.** `CohortEngine` bounds a run by `max_calls`; it has no equivalent of `BoundedSupervisor`'s cost / clean / window / empty-streak ceilings. The cohort path therefore **refuses** when one of those is set, instead of running a bounded-looking window with the bound quietly removed.

**Runtime behaviour on `master` is still unchanged.** No acceptance record exists, so `--execute --cohort-width 2` refuses exactly as before; `--cohort-path` is opt-in and nothing calls it yet.

## Checks actually run

```text
window_selftest                     223/223 passed, 0 failed
cohort_engine_selftest              PASS (10 pins)
cohort_live_admission_selftest      PASS (6 pins; 15 record defects each refusing)
cohort_live_dispatch_selftest       PASS (6 pins)
bounded_staged_run_selftest         PASS   — (q) pin re-asserted on the new contract
lang_parity_check                   109 entries, all verdicts complete, no drift
```

The (q) pin now asserts the flip **positively**: with a complete record the run is no longer refused at all (it reaches the plan load). A silent re-closing of the gate fails that pin — the previous shape, which only ever asserted refusals, could not have caught it.

## Why the paid half was still not attempted — probed, not assumed

| Probe | Command / file | Result (11-09-2026) |
|---|---|---|
| Live-gate receipt | `src/pilot/output/coordinator/probe_receipts/probe_receipt.h4213-canary-082926.json` | **GO at 05:33:42Z**, `c1`, 73 075 ms under the 240 000 ms `production_v4` ceiling. The lane is **healthy today** — the 14-day-stale receipt the 11-09 offline pass reported has been superseded |
| Who owns the lane right now | [GTD row 10l](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md), `window_status.json` | H4213's canary wave ran at 05:29–05:36Z and settled `needs_requeue` (content NO-GO: F12 NWS misattribution + R1_yo), with its own next step queued (rework the canary card → re-judge → 6-key wave ≤ $6) |
| Probe ration | [/pwg-live-gate](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) | ≥ 6 h spacing, ≤ 2 attempts/UTC day. One attempt spent today at 05:32Z, so the next legitimate window opens **≈ 11:33Z** — and spending it here spends H4213's remaining ration on the profile H4213 is mid-wave on |
| The fleet | `max_orchestrator.sqlite`, read-only | **one** validated row: `c1` → `D:\ClaudeTools\profiles\claude1\.claude`. There is no `c2` roster slot to admit |
| Latency policy | `git diff src/pilot/probe_log.py` in the shared checkout | `production_v4` (240 000 ms, MG ruling 10-09) is **still uncommitted**, owned by H4213 — deliberately untouched here. `origin/master` runs `production_v3` |

## The remaining rungs, in order

1. **Live serial-acceptance window** — `bounded_staged_run --execute --cohort-path --cohort-width 1 --max-calls N` on the then-live slot, with a fresh canary GO ≤ 6 h. Now runnable; it was not runnable before this pass at any time. Packet lands next to this file.
2. **Codex sign-off** on that packet (work item 2) — a reviewer session, not this one.
3. **Write `COHORT_LIVE_ACCEPTANCE.json`** from 1 + 2, including `serial_acceptance.via_cohort_path: true`. This is the only act that opens the gate.
4. ~~Wire the live cohort dispatch~~ — **done in this pass.**
5. **One live width-2 window** (work item 3) with `peak_concurrency >= 2`. **Blocked on a human ruling, not on code:** it needs a second admitted profile, and MG's 19-08 ruling made `c1` the sole live lane. Re-admitting `c2` (authenticated, 504 B credentials) is the human act that unblocks it; until then `fleet_guard` refuses width 2 with that exact reason.
6. **Verifier PASS** from a different session (money class, H4358).

Rungs 1, 3 and 5 also want the `production_v4` bump landed on `master`, which belongs to H4213.

_Dr. Mārcis Gasūns_
