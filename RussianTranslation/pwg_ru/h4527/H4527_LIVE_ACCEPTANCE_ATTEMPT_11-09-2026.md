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

## A hazard found in passing — recorded before it bites someone

`no_pwg_scale_plan.py` silently regenerates four **tracked** dashboard JSONs as a side effect of
planning: `progress_dashboard/kitchen_data.json`, `progress_data.json`, `progress_timeseries.json`,
`quality_timeseries.json`. Run from a checkout behind `origin/master` — the shared main tree was
**behind 5** — that rebuild is a net **−2191 lines** on `kitchen_data.json` and walks
`store.senses` 11519 → 11516. A session that planned a window and then committed everything it
touched would erase curated data with no gate objecting. Reverted here (`git checkout --` on those
four paths only, after confirming all four carried this run's own 16:06Z mtime); the shared tree is
back to its two pre-existing H4213 edits.

## Status of the five work items

| # | item | state |
|---|---|---|
| 1 | live serial acceptance through `--cohort-path` | **blocked on card availability** — not on code, gate, ration or spend authority |
| 2 | Codex sign-off on the packet | not reachable from one session; needs a reviewer window |
| 3 | width-2 enablement | **parked** on the standing fleet condition (MG 11-09: `c2` not opened; `claude4/5/6` unfunded until the pipeline works end to end) |
| 4 | flip the refusal deliberately | **done** ([#2170](https://github.com/gasyoun/SanskritLexicography/pull/2170) + [#2176](https://github.com/gasyoun/SanskritLexicography/pull/2176)) |
| 5 | N-probe estimator if admission proves flappy | not triggered — no false NO-GO this pass |

## The next physical step, in order

1. Re-generate `arvant~~h0_zz_nws00` on `c1` — one paid call, the canary gate is already open
   until ~22:00Z. Either lane's route works; H4213's is
   `python src/pilot/requeue_from_audit.py h4213can091108282902`.
2. Once that card promotes, its lease frees the key, and `no_pwg_scale_plan.py --headless` can
   prepare an H4527 acceptance window on the **next** of the 121 remaining headwords.
3. Then the width-1 `--cohort-path` window, the packet, and only then the acceptance record with
   `serial_acceptance.via_cohort_path: true`.

_Dr. Mārcis Gasūns_
