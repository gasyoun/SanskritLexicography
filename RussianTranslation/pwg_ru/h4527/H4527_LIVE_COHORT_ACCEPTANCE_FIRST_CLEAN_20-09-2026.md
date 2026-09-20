# H4527 — the cohort path accepted and promoted its first card: work item 1's live evidence is complete

_Created: 20-09-2026 · Last updated: 20-09-2026_

**Executor:** Opus 5 (`claude-opus-5`), interactive `/go` from the Mac over MSI ssh ·
**Paid calls:** 4 (1 canary, 1 card, 2 readiness-probe legs = the day's one ration attempt) ·
**Lane box:** `WIN-NJTORH3267V` (MSI), shared checkout at `99b21e67e`.

On 16-09 the cohort path ran live for the first time and returned a **null card**, so the
acceptance record stayed unwritten. On 17-09 that null was diagnosed — the card had
`senses: []`, therefore `max_heal_agents: 0`, therefore one shot and no repair lane — and the
planner gate that avoids the whole class, `--require-senses`, was written but not merged.

This pass merged the gate and ran the window it was built for. **The window came back
`clean`: one card, zero requeue, nine audit gates green, one promote, one TM callback, store
11 521 → 11 524.** That is the first card ever accepted through the live cohort dispatch.

## What ran, in order, all of it gated

| # | Step | Result |
|---|---|---|
| 1 | [#2261](https://github.com/gasyoun/SanskritLexicography/pull/2261) CI re-checked | 1 red check — **FINDINGS index drift, not this PR's code**; branch was 22 commits stale |
| 2 | Branch updated from `master`, CI re-run | **10/10 green**, merged as `99b21e67e` |
| 3 | MSI shared checkout fast-forwarded | `71f72f07e` → `db63bcb64` → `99b21e67e`, tree clean |
| 4 | Lease prepared with `--require-senses 1` | `h4527sen08` — **1 window, 1 sub-card, 1 projected call** |
| 5 | Zero-call dry run | `live_admission.admitted: true`, lease importable, `windows_not_prepared_skipped: []` |
| 6 | `probe-ration --account c1` | **exit 0**, `attempts_today: []`, `legal_now: true` |
| 7 | `dq_canary_puregloss` | **CANARY GO** (`h4527-canary-200920`, 52 756 ms, `cli_safe_mode_effective: true`) |
| 8 | `--execute --cohort-path --cohort-width 1` | **clean, accepted, promoted** |

### Step 4 — the gate did exactly what the census predicted

`no_pwg_scale_plan.py --window-size 1 --limit-windows 1 --require-senses 1 --headless
--profile-slot c1 --prefix h4527sen` walked past five sense-poor heads and stopped at the
sixth:

```
omitting h4527sen02..h4527sen07: every unpromoted subcard is a blocked residual or sense-poor
                                 / no unpromoted subcard declares 1+ source sense(s)
preparing  h4527sen08: 1 headword(s)   → darvI
```

The manifest records the skips with their measured counts — `darv_i~~h0_zz_nws00` (0 senses),
`asa_mskfta~~h0_zz_nws00` (0), `asvatantra~~h0_zz_nws00` / `~~h0_zz_pw` (0), `avy_ahata~~h0_zz_nws00` (0).
`asa_mskfta~~h0_zz_nws00` is the exact card the 16-09 window burned a call on; the gate now
refuses to hand it to a paid window. The prepared window is **one** sub-card,
`darv_i~~h0_zz_pw` (3 source senses, so a real repair lane), which is the 17-09 census's own
objection to `darvI` — "a two sub-card window, 2 paid card calls" — removed.

**No tracked-file drift:** `git status --porcelain` was empty before and after. The
`progress_dashboard/*.json` rewrite hazard of the 11-09 (3) pass did not trigger.

### Step 8 — the window

Run id `h4527-acc-200920`, wall clock 5.557 min, `gen_model: claude-sonnet-5`.

| Event | Reading |
|---|---|
| `probe_call` warm-up | 20 637 ms (api 19 045) · `success` · `policy: production_v4`, ceiling 240 000 ms |
| `probe_call` measured | 23 429 ms (api 20 820) · `success` · `probe_prompt_sha: 90e2f1f6698b` |
| `attempt_start` | 18:01:32.296Z · lease `h4527sen08` · account `c1` |
| `model_call` | 77 224 ms · `success` · 1 key · `darv_i~~h0_zz_pw` |
| `attempt_end` | `success` · `result_hash 2c42706997291abd…` |

Both probe legs passed with safe mode effective — the fourth independent clean reading since
the 15-09 injection-shape repair, and consistent with the 4–7× speed-up that fix bought.

**Audit: 9/9 gates PASS, 1/1 clean, 0 requeue.** `nws` · `translation` (`3/3 san s/o`, ru Y) ·
`stage2_mechanical` · `coverage` (raw 4 → card 3, ok) · `sense_dupes` · `prompt_semantic` ·
`sense_loss` (no card short of its source sense count) · `ru_style` · F12 misattribution gate.
`prompt_semantic` filed 5 advisory risks on the key at score 320 with **high_confidence = 0**,
so nothing was requeued — advisory review-queue output, not a gate failure.

**Accounting and promotion discipline:**

```
accepted_order      : ["h4527sen08"]        ← non-empty for the first time
calls_spent         : 1  ==  calls_reserved : 1
peak_concurrency    : 1        effective_width : 1
cohort.path         : "live"   fleet : ["c1"]
wave.promoted       : true     wave.tm_done : true      ← one promote, one TM
requeue_backlog_keys: []       stop_reason : null
BATCH PROMOTE: 1 lease(s), 1 subcard(s), 3 sense rows; store 11521 -> 11524 rows
```

The single-promoter rule held: one `promote-ready` for the whole accepted set, landed by the
coordinator in a single `batch_promote` transaction, one TM callback. No guardrail was
touched — no `--skip-canary-gate`, no `ALLOW_*`, no retry after the audit verdict.
`--allow-unbounded` was passed because the cohort path refuses the supervisor's
`--cost-ceiling` by design (rung 4's own contract) and `--max-calls 3` stayed the bound; two of
those three were never spent.

## Serial-vs-cohort comparison — what it proves, and the limit it does not hide

Receipt: [`src/pilot/h4527_acceptance_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4527_acceptance_compare.py)
(read-only, spawns nothing, costs nothing), comparing `h4527sen08` (cohort, clean) against
`h4213can091108282902` (serial supervisor). **Exit 0 — PASS:**

```
sealed_artifacts : shared 19 · route_driven_differences [] · schema_mismatches []
                   outcome_driven_differences ["requeue/", "wf_output.clean.<lease>.json"]
journal          : window_status keys identical (31) · ledger row key sets identical
```

Every file present on one side and absent on the other is explained by the window's
**outcome**, not its route: a requeued window writes `requeue/`, a clean one writes
`wf_output.clean.*`. Once those and the content-hash in `submitted_result.<sha>.json` are
accounted for, the two routes produce the same artifact set, the same schemas, and — the
strongest signal — the same `window_status.json` and `window_ledger.jsonl` **field sets**,
which is exactly where a route that advanced the journal differently would show it.

**The limit, stated rather than papered over.** Two things this comparison is not:

1. It is not a same-card A/B, and no run can be. A sub-card is translated once and promoted
   once; re-running a promoted key is a different window on different input.
2. It is not even a same-**outcome** comparison (`same_outcome: false`). The only
   serial-supervisor window on this box settled `needs_requeue`; the cohort window settled
   `clean`. **There is no clean accepted serial-route window on disk to diff against.**

Card-byte identity across widths 1/2/3 was proven offline by
[H1437 Phase 4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1437/H1437_PHASE4_CLOSEOUT_2026-08-29.md)
(clean/requeue decisions, accepted order and store bytes byte-identical on simulated waves).
This receipt is the **live structural half** of that claim, not a replacement for it.

## Defect found by this window: a clean accepted cohort wave exits 1 (FINDINGS §642)

`bounded_staged_run.py` ends on:

```python
return 0 if summary.get('stop_reason') in (bs.STOP_CLEAN_TARGET, bs.STOP_WINDOW_COUNT,
                                           bs.STOP_CLEAN_QUOTA, bs.STOP_CALL_COUNT) else 1
```

Those four are **supervisor** stop reasons. The cohort branch returns `cld.run_cohort_live(...)`,
whose summary carries `stop_reason: null` — no stop condition fired, the wave simply finished.
So `--execute --cohort-path` returns **1 on a fully clean, fully accepted, fully promoted
wave**, and the comment above that line ("a cost-unevaluable / non-clean stop is a non-zero
exit so callers can gate on it") describes behaviour the cohort path cannot produce.

This was invisible until now for one reason: **no cohort wave had ever completed cleanly.** The
16-09 run returned a null card, so its non-zero exit looked correct. Any caller that gates on
the exit code — a drain lane, a scheduled wrapper, CI — would read this window's success as a
failure.

Not fixed here: it is money-path code and a distinct concern from work item 1, whose evidence
is complete. Routed to its own handoff (see below) so the fix arrives selftest-backed rather
than bolted onto an acceptance pass.

## Why `COHORT_LIVE_ACCEPTANCE.json` is still NOT written

`cohort_live_admission.validate_record` requires **both** halves, and the second one does not
exist yet: `reviewer_sign_off` needs `reviewer`, `session`, `dated`, `verdict: PASS` and at
least one evidence pointer. That is **work item 2**, a Codex reviewer session, and no session
may write its own sign-off. Writing the record with a fabricated or empty reviewer block would
be precisely the silent gate-opening this handoff's *Fail* list bans — and it would be
rejected by the validator anyway, so nothing is gained by staging an invalid one.

**Nothing is left to re-derive.** The `serial_acceptance` half is fully determined by this
pass; a reviewer session pastes it verbatim and adds only its own block:

```json
{
  "schema": "pwg.cohort_live_acceptance.v1",
  "max_admitted_width": 2,
  "serial_acceptance": {
    "run_id": "h4527-acc-200920",
    "window_id": "h4527sen08",
    "profile": "c1",
    "completed_utc": "2026-09-20T18:02:59Z",
    "via_cohort_path": true,
    "byte_identical_to_serial": true,
    "evidence": [
      "RussianTranslation/pwg_ru/h4527/H4527_LIVE_COHORT_ACCEPTANCE_FIRST_CLEAN_20-09-2026.md",
      "RussianTranslation/pwg_ru/h4527/acceptance.sen.report.json",
      "RussianTranslation/pwg_ru/h4527/acceptance.sen.events.jsonl",
      "RussianTranslation/src/pilot/h4527_acceptance_compare.py"
    ]
  },
  "reviewer_sign_off": { "…": "work item 2 — a DIFFERENT session fills this" }
}
```

`byte_identical_to_serial: true` is claimed on the evidence above — the structural PASS plus
H1437's offline decision/accepted-order/store-byte proof — **and the reviewer is asked to
weigh exactly that claim**, including the `same_outcome: false` limit, rather than take it on
trust. A reviewer who judges the live structural half insufficient should say so; that is what
the sign-off is for, and width 2 stays refused meanwhile.

## Ration and spend, stated honestly

`c1`'s 20-09 UTC ration: **one attempt spent** (18:01Z, this window's own probe pair), one
remaining. The canary costs a call but no probe attempt. Four paid calls total; the window's
usage block carries `cost_evaluable: false`, i.e. *not evaluable* — never a measured total.

No [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
entry is owed: nothing failed at launch. The exit-code defect is a reporting bug in a window
that succeeded, not a launch failure, and it is recorded in FINDINGS instead.

## What remains on H4527

1. **Work item 2 — Codex reviewer sign-off** on this packet. The only thing between here and a
   written acceptance record. A different session, by construction.
2. **Work item 4 tail — the exit-code defect** above, its own handoff.
3. **Work item 3 — width 2** stays parked on the 11-09 MG one-lane ruling (`c1` is the whole
   fleet; `c2`'s token expired 24-07). Parked on a **condition, not a decision** — nobody is
   waiting to rule on it.
4. **The money-class `## Verifier` PASS** (H4358) — a different session again.

_Гасунс_
