_Created: 11-09-2026 · Last updated: 11-09-2026_

# H4527 — live-acceptance attempt, 11-09-2026 (third pass): the gate opened, the card did not

Executor: **Opus 5 (`claude-opus-5`)**, interactive `/go H4527`, elapsed ~50 min, **1 paid call** (the canary).
Prior passes the same day: the offline admission gate ([#2170](https://github.com/gasyoun/SanskritLexicography/pull/2170)) and the live cohort wiring ([#2176](https://github.com/gasyoun/SanskritLexicography/pull/2176)).

## What this pass changed

**1. `production_v4` reached `master` — [#2190](https://github.com/gasyoun/SanskritLexicography/pull/2190), merge `945a102d2`.**

Blocker #5 of the live half (*"the 240 000 ms policy is not on master, so a window launched today
NO-GOes by policy"*) was never a disagreement about MG's ruling. The ruling **was** committed on
10-09 as [`4092291ae`](https://github.com/gasyoun/SanskritLexicography/commit/4092291ae59d761d1edf0397e9aae1308fc38a67)
and had been sitting unmerged on `h4213-drain` behind [#2101](https://github.com/gasyoun/SanskritLexicography/pull/2101),
which is red on `RussianTranslation gates` for exactly **one** reason: `src/pilot/probe_log.py` is
tracked by **two** `LANG_PARITY.md` entries (`h1339_measurement_integrity`,
`h1386_resume_recovery_and_medium50`) and neither `verified_sha256` was refreshed after the policy
edit, so `window_selftest` failed 222/223 on `test_lang_parity_ledger_complete`. Both SHARED
verdicts were re-checked (the new `POLICIES` row is lane-agnostic — it reads and writes no
target-language field), both hashes updated, MG's commit cherry-picked with authorship intact.
All 10 checks green. **This also unblocks H4213's parked wave**, which sat behind the same gate.

**2. A fresh canary GO receipt exists on `c1` — the first in weeks, and it is still spendable.**

`dq_canary_puregloss` ran through the production headless route at 15:58Z: `classification:
success`, 82 862 ms wall, key `dq_canary_puregloss~~h0_zz_pw`, exit 0; `canary_gate.py judge`
returned **GO**.

| field | value |
|---|---|
| receipt | `src/pilot/output/h4527/canary_receipt.json` (worktree, gitignored) |
| run id | `h4527-canary-091116` |
| profile | `c1` (`max`, token valid to 23:51Z) |
| manifest sha256 | `fd8da65bbfebee8ed9dc5b1f6fd09b9131200346b7d99f5decdea2add5205ba3` |
| judged | 2026-09-11 ~16:00Z — **valid 6 h, so until ~22:00Z** |
| cost | 1 paid call, `cli_safe_mode_effective: true` |

The `--execute` spend key is therefore **open for the rest of today**, for either lane, without
spending another probe attempt.

## What stopped the acceptance window — a designed guard, not a failure

`bounded_staged_run --execute --cohort-path --cohort-width 1` needs a **prepared coordinator
lease**. Preparing one was refused:

> preparing h4527acc03: 1 headword(s)
>
> nominal lease keys already active: arvant~~h0_zz_nws00

The cause is a real scarcity, probed rather than assumed:

1. **The verb lane has zero runnable work.** `verb_worklist.py --top` reports *"verbs01 universe:
   1882 DCS-attested: 749 promoted: 48 REMAINING: 701 … runnable: 0 (0 source bytes) missing
   rootmap: 701"*. All 701 remaining roots lack rootmaps, so the handoff's *"a real small verb root
   from `verb_worklist.py --top`"* cannot be satisfied on this box today.
2. **The no-PWG queue has 122 headwords left, and `arvant` is at the head of the queue itself** —
   not merely at the head of the `still_null` tail. Blocking the still_null key through a
   plan-scoped `--residual-file` (the tracked `no_pwg_residuals.jsonl` was **not** touched) moved
   nothing: `build_order` returns `tail_heads + rest`, and `arvant` is `rest[0]` too.
3. **`arvant~~h0_zz_nws00` is held by H4213's open `needs_requeue` lease** `h4213can091108282902`,
   and the coordinator refuses a second nominal lease on an active key. That refusal is the
   stale-lease wedge guard working — the class that already cost H4213's wave one attempt.

So the only card the planner can build a window on today is the one card another lane holds, and
its release path (`requeue_from_audit.py` to a standalone rerun harness) is **not** the
`--cohort-path` route this acceptance window exists to prove. Nothing was overridden, no `ALLOW_*`
was set, and **no paid call was spent on the window**.

## Two findings worth keeping

**A. H4213's re-judge produces no canary receipt — the handoff's own *Armed launch* premise was
false.** It deferred the day's remaining probe attempt to H4213 because *"one canary GO receipt
satisfies both lanes"*. One receipt genuinely does serve both (same profile, 6 h) — but H4213's
05:29–05:36Z window was a **real card window** (`pwg.no_pwg_scale_plan.v1`, key
`arvant~~h0_zz_nws00`, `provenance_classes: real`), and that key does **not** match
`promote_final_cards.SYNTHETIC_KEY_RE` (`^(?:dq_canary_|zz~~synthetic|synthetic[_~-])`), so
`canary_gate.judge` refuses it outright: *"NOT a synthetic-control key — refusing to judge a real
window as a canary"*. Waiting for H4213 to produce the receipt would have waited forever. Running
the synthetic canary directly, as this pass did, is what actually opens the gate.

**B. H4213's F12 half is fixed; only the ё rule remains.** Re-judging H4213's existing `wf_output`
against the merged [#2179](https://github.com/gasyoun/SanskritLexicography/pull/2179) `nws_split`
owner-regex fix — offline, zero calls — moves the `nws` gate from **exit 1 / 1 requeue** to
**exit 0 / 0 requeue**. `ru_style` still hard-flags `R1_yo`. The card therefore needs a real
re-generation rather than a re-judge: one paid call, and the canary gate above is already open for
it. Report under `src/pilot/output/h4527-rejudge/` (gitignored).

## The dashboard hazard — corrected attribution (erratum, same day)

**The first version of this section blamed `no_pwg_scale_plan.py`. That was wrong**, and the
correction matters because the real cause cannot be fixed by not running the planner.

`progress_dashboard/{kitchen_data,progress_data,progress_timeseries,quality_timeseries}.json`
are rewritten by a **long-running local daemon**, not by any command a session types:

```
python -u progress_dashboard/live_refresh.py --idle-stop 0 --interval 60
       --active-within 900 --data-root C:\Users\user\Documents\GitHub\SanskritLexicography
```

PID 10616, started 04-09-2026, still running. Its own docstring says why it exists and why it
behaves this way: progress and kitchen numbers derive from **gitignored** RussianTranslation
artifacts that CI never sees, so it rebuilds them locally every `--interval` seconds whenever
the store, window_status or ledger mtime falls inside `--active-within`, and publishes to
`origin/gh-pages` — *"never spams master with minute-level commits"*. Any live-gate or planning
activity in `src/pilot/` therefore re-dirties those four tracked files within 60 seconds.
Reverting them is futile while the daemon runs; this pass reverted them once and they were back
in under two minutes.

**What is genuinely hazardous, and survives the correction:** the rebuild runs from the **shared
main checkout**, which was **behind `origin/master` by 5 commits** all day, so the diff it leaves
in the working tree is a net **−2191 lines** on `kitchen_data.json` and walks `store.senses`
11519 → 11516. Those four files are tracked. A session that runs `git add -A` in this tree — the
sweep the shared-tree guard already warns about — commits a large stale-checkout deletion it
never looked at, on top of whatever it meant to commit.

**How to stay safe:** stage explicit paths in this tree, never `git add -A`; treat a dirty
`progress_dashboard/*.json` as the daemon's normal state rather than as your own edit; and if the
diff ever needs to land, update the checkout first so the rebuild is derived from current
`master` rather than from a five-commit-old tree.


## Second attempt, 18:00–18:10Z — the card blocker cleared, a different gate stopped the window

MG said «4213 executed». It had not: at 17:54Z the registry row still read
`⛔ blocked on MG ruling — probe gate RED ×8 attempts`, the lease
`h4213can091108282902` was still `state: needs_requeue`, the last
`health_probe_log.jsonl` row was still `2026-09-11T05:33:42Z`, and there was no `.claim` and no
in-flight pilot process. So it was claimed and run here.

### H4213's card is done — the queue's head is finally clear

| step | result |
|---|---|
| re-generation (`headless_worker.py`, run `h4213-rq1-091117b`) | `classification: success`, 210 912 ms, no null keys |
| audit | **1/1 clean, 0 requeue**; all nine gates exit 0, `ru_style` included |
| promotion route | raw `--merge` **refused** by the H2089 route guard → coordinator path: `prepare-requeue --defect` → `begin-run` → `record-output` → `promote-ready` |
| store | **11516 → 11521 rows**, 1 subcard, 5 sense rows, TM denylist cleared, pre-merge backup written |

The coordinator **re-audited the result independently** on `record-output` (its own clean/defect
counts, not this session's) before moving the lease to `ready` — so the promotion rests on two
separate audits, and no extra paid call was needed to satisfy the state machine.

Two mechanical notes worth keeping: `requeue_from_audit.py` needs `--nominal` for a no-PWG
supplement window, and without it dies on `no rootmap for <root>` — which reads exactly like the
known missing-rootmap data gap but is a different thing entirely; and the first `headless_worker`
launch aborted `classification: configuration — paid v2 execution requires --preflight`, which is
a provisioning abort that spends nothing and consumes no attempt.

### The acceptance window then STOPped on the readiness probe — and the lane is demonstrably fine

With the key free, `no_pwg_scale_plan --headless` prepared `h4527acc05` on the next headword
(`h4527acc04`, arvant, correctly omitted: "every unpromoted subcard is a blocked residual" — its
`~~h0_zz_pw` sibling is a July residual). The dry run confirmed scope: 1 lease, 1 window,
importable. Host was healthy (4079 MB free, load 74%) and the canary receipt re-validated `GO
receipt valid` seconds before launch.

`bounded_staged_run --execute --cohort-path --cohort-width 1` then stopped before dispatching
anything:

> fleet probe STOP on account c1: warm-up probe content -> STOP (auth/model/output/rate-limit/timeout)

**Latency is not implicated.** The probe ran 113 531 ms wall / 93 090 ms api against a 240 000 ms
`production_v4` ceiling, at 80.38% host commit — the same band as the day's successful readings.
The envelope says what actually happened: `stop_reason: "tool_use"`, 8038 output tokens of which
**7312 thinking**, `num_turns: 2`, `is_error: false`, and `result: {"ok":false}`. The model reaches
for a tool instead of answering the plain readiness question, then returns the refusal token. That
is the §6.2/§6.3 class H4213 logged three times, with a sharper mechanism now visible.

**The decisive new evidence is a same-day counterexample on the same profile.** Three paid calls
succeeded on `c1` through `headless_worker.py` within the preceding two hours:

| time | call | result |
|---|---|---|
| 15:58Z | `dq_canary_puregloss` | success, 82 862 ms → judge **GO** |
| 16:19Z | `dq_canary_puregloss` (re-bought) | success, 50 824 ms → judge **GO** |
| 17:58Z | real nominal translation window | success, 210 912 ms → audit 1/1 clean → **promoted** |

`headless_worker.py` does not call `probe_fleet`; `bounded_staged_run --execute` does. So the
route, the credentials, the profile and the host are all provably healthy, and the only component
refusing is **the readiness warm-up prompt itself**. This is precisely the evidence H4213 §6.3
option (b) — *"retune `_probe_prompt` task-shape (selftest-backed)"* — was waiting for, and it now
outranks options (a), (c) and (e), which all target the host or the hooks. Any retune stays
selftest-backed and must not weaken what the probe asserts (H4213: *"must not be hand-weakened"*).

RED = STOP was honoured: no retry. The day's 2-attempt ration for `c1` is now spent (05:32Z and
18:08Z), so the next attempt belongs to a later UTC day. Ledger row:
`H4527_ACCEPTANCE_PROBE_REFUSAL_2026-09-11` in
[LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
(`check_launch_ledger.py` → 20 entries complete).

### Where work item 1 now stands

Everything except the probe is in place and survives to the next attempt: the cohort wiring, the
admission gate, a **prepared lease `h4527acc05`**, and a verified dry-run scope. What expires is
the canary receipt (`h4527-canary-gate-091116b`, judged ~16:19Z, valid to ~22:19Z) — a later
attempt buys a fresh one, which costs a call but not a probe attempt.

### Spend, stated honestly

Four paid calls this session: two canaries (one of them re-bought after the worktree deletion
recorded above), one translation window, one readiness probe. **The reservation ledgers record
`cost_evaluable: false` on every one** — Max-route credit billing is dormant, so ledger cost is
**UNKNOWN, not zero**. The one envelope read directly carried `total_cost_usd: 0.28122` with
`costBasis: "list"`, which is a list-equivalent price, not a charge.

## Status of the five work items

| # | item | state |
|---|---|---|
| 1 | live serial acceptance through `--cohort-path` | **blocked on the readiness warm-up probe** (card availability was cleared this pass; lease `h4527acc05` is prepared and waiting) |
| 2 | Codex sign-off on the packet | not reachable from one session; needs a reviewer window |
| 3 | width-2 enablement | **parked** on the standing fleet condition (MG 11-09: `c2` not opened; `claude4/5/6` unfunded until the pipeline works end to end) |
| 4 | flip the refusal deliberately | **done** ([#2170](https://github.com/gasyoun/SanskritLexicography/pull/2170) + [#2176](https://github.com/gasyoun/SanskritLexicography/pull/2176)) |
| 5 | N-probe estimator if admission proves flappy | not triggered — no false NO-GO this pass |

## The next physical step, in order

1. **Retune the readiness probe prompt, selftest-backed** — H4213 §6.3 option (b). This pass
   supplied the evidence that picks it out of the five options: on 11-09 the same profile
   completed three paid calls through `headless_worker.py` (two canary GO windows and one real
   translation that promoted) while `probe_fleet`'s warm-up returned `{"ok":false}` on
   `stop_reason: "tool_use"`. The host, the hooks and the ceiling are all exonerated by that
   counterexample. The retune must not weaken what the probe asserts.
2. **Then re-run the acceptance window.** `h4527acc05` is already prepared and its dry-run scope
   verified, so the sequence is: fresh canary GO receipt (one call, no probe attempt) →
   `bounded_staged_run --execute --cohort-path --cohort-width 1 --only-profile c1
   --canary-receipt <receipt> --max-calls 2 --allow-unbounded` (the cohort path refuses the
   supervisor's cost/clean/window ceilings by design, so `--max-calls` plus the shared reservation
   run-id is its bound) → audit → compare against the serial route → the packet →
   `serial_acceptance.via_cohort_path: true`.
3. **Work item 2** (Codex sign-off) and the money-class **Verifier PASS** each still need a
   different session.

_Dr. Mārcis Gasūns_
