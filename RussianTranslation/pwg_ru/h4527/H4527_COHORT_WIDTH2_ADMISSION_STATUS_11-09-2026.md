_Created: 11-09-2026 · Last updated: 11-09-2026_

# H4527 — cohort width-2 admission: what landed, what the live half still needs

**Executor:** Opus 5 (`claude-opus-5`), unattended handoff worker (pool `sonnet`, executor Claude/c1), ~45-minute unit.
**Handoff:** [H4527](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4527-Opus_RussianTranslation_pwg-ru-cohort-live-acceptance-width2_10.09.26.md) (Opus, 🔴3 hard, class **money**).
**Scope executed:** work item 4 only (the deliberate, fail-closed refusal flip + the (q) pin).
**Scope NOT executed:** work items 1, 2, 3 — the live serial-acceptance window, the Codex sign-off and the live width-2 window. Zero paid calls were made in this pass; the live route is untouched.

## Why the live half was not attempted (probed, not assumed)

| Probe | Command | Result (11-09-2026) |
|---|---|---|
| Live-gate receipt freshness | `python src/pilot/probe_log.py gate` | `GO: last warm-up 2026-08-28T14:20:51Z — production_v3` — **14 days old**. [/pwg-live-gate](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) requires a fresh GO **≤ 6 h** per profile before any window, so both windows would have had to start with a fresh paid canary. |
| Live latency policy | `git diff RussianTranslation/src/pilot/probe_log.py` in the shared checkout | An **uncommitted** `production_v4` bump (`latency_ceil_ms` 80 000 → 240 000, MG human ruling 10-09-2026) exists only in the main tree. `origin/master` — what this worktree runs — is still `production_v3` at 80 000 ms, while the 10-09 evidence records a schema-valid success at **156 802 ms wall** on this box. A live window launched from `origin/master` today would NO-GO by policy, not by route health. |
| Money-class close | handoff header, H4358 | The close requires a **different session's** PASS in `## Verifier`; work item 2 requires a **Codex reviewer session**. Neither is reachable from inside one unattended worker. |

Consequence: attempting a live window in this unit would have spent paid calls into a near-certain NO-GO and consumed the ≤ 2 attempts/UTC-day ration for no evidence. It was not attempted, and no [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md) entry is owed (no launch failure occurred — nothing launched).

## What landed instead (offline, fail-closed, safe to merge before the live half)

1. **[`src/pilot/cohort_live_admission.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cohort_live_admission.py)** — the one artifact that can ever open the gate: `pwg_ru/h4527/COHORT_LIVE_ACCEPTANCE.json` (schema `pwg.cohort_live_acceptance.v1`). It must carry BOTH halves the Phase 3 refusal names — a live serial-acceptance window (`run_id`, `window_id`, `profile`, `completed_utc`, `byte_identical_to_serial: true`, ≥1 evidence pointer) and a reviewer sign-off (`reviewer`, `session`, `verdict: PASS`, `dated`, ≥1 evidence pointer) — plus `max_admitted_width` and `admitted_profiles`. Missing file, unreadable file, wrong schema, blank field, non-PASS verdict, evidence-free half, duplicate profiles or a fleet narrower than the width all **refuse**. No environment variable overrides it.
2. **`MAX_ADMITTED_WIDTH = 2` is a code cap, not data.** Width 3+ is refused even by a perfect record, and a record that *asks* for width 3 is rejected **whole** rather than silently clamped — Slice-D's 18-wide and H317's 3-wide cascades are the standing counter-examples. Width 3 gets its own rung, its own evidence and its own deliberate edit of that constant.
3. **Rung 2, the anti-footgun**: when a record DOES admit width 2, `bounded_staged_run --execute` still refuses — naming `COHORT_LIVE_WIRING`. The live path builds a **serial** bounded supervisor and `run_cohort_offline` is unreachable from it (plan-scoped windows carry no per-profile binding, which `CohortEngine`'s one-job-per-profile invariant requires). Without this rung, flipping the gate would have made `--cohort-width=2` run as an ordinary serial window under a misleading width label — a worse outcome than the refusal it replaced.
4. **The dry-run planning view now answers the admission question without a run**: `plan_view(...)['cohort']['live_admission']` carries `admitted`, `reason`, `record_path`, `max_admitted_width`, `admitted_profiles`.
5. **The (q) pin was edited deliberately, in the same commit as the gate** (the handoff's own "a silent (q)-pin edit = FAIL" condition), and now asserts all three branches: no record → the H1437 live-acceptance refusal; valid record → ADMITTED + rung-2 refusal; width 3 → the code cap. Plus six new pins in [`cohort_live_admission_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cohort_live_admission_selftest.py).

**Net runtime behaviour on master today is unchanged**: no acceptance record exists, so `--execute --cohort-width=2` refuses exactly as it did before, with a more specific reason.

## The remaining rungs, in order

1. **Live serial acceptance window** (handoff work item 1) — fresh canary GO ≤ 6 h, one bounded window at width 1 on the then-live slot, sealed artifacts + journal + promotion-DRY compared byte-for-byte against the serial route. Packet lands next to this file.
2. **Codex sign-off** on that packet (work item 2) — the reviewer half of the record.
3. **Write `COHORT_LIVE_ACCEPTANCE.json`** from 1+2 (this is the only act that opens the gate).
4. **Wire the live cohort dispatch** (rung 2 above): per-profile window binding on the execute path, one promote + one TM per wave, one shared reservation run-id — then delete the `COHORT_LIVE_WIRING` refusal in the same commit that pins the wiring.
5. **One live width-2 window** (work item 3) with `peak_concurrency >= 2` and byte-identical accounting.
6. **Verifier PASS** from a different session (money class, H4358).

Items 1–3 and 5 are paid-lane work and inherit the [H4342](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4342-Sonnet_SanskritLexicography_pwg-ru-translation-stall-full-audit_08.09.26.md) re-arm rulings; they also want the `production_v4` policy bump landed first (it is currently an uncommitted edit in the shared checkout, owned by another session — **not** touched by this pass).

## Checks actually run in this pass

```text
cohort_live_admission_selftest      PASS (6 pins)
bounded_staged_run_selftest         PASS   — (q) pin PASS on the new three-branch contract
cohort_engine_selftest              PASS (10 pins)
window_selftest                     see the PR body (run on this branch)
lang_parity_check                   see the PR body (run on this branch)
```

_Dr. Mārcis Gasūns_
