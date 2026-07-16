# H963 — kill-budget saturation: classification, proof, and replacement spec

_Created: 16-07-2026 · Last updated: 16-07-2026_

**Classification: a kill-budget SATURATION defect. Not a cause of API latency. Not accidental.**

Supersedes the framing in [`campaign_journal.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/campaign_journal.md)
checkpoints 2–3, which mis-stated this as "the median card is undeliverable on any route" — a claim
about *delivery* built on a rate extrapolation. The defensible claim is narrower, mechanical, and does
not depend on any rate fit.

**Evidence campaign only — no correction implemented here**, per the brief's measure-first discipline.

---

## 1. What it is, and what it is not

The kill gate is a **client-side wait cap**: a `setTimeout` raced against the `agent()` promise
([`run_pilot_wf.real.js:183`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py);
`AbortController` is unavailable, so an abandoned call keeps running server-side —
`gen_opt_harness2.py:152-155`).

- **It cannot make Sonnet respond slowly.** It has no effect on the API, the route, or the model.
- **What it does:** decide how long the harness waits before abandoning a call.
- **The defect:** the budget **saturates at `KILL_CEIL_MS`** for essentially every real card, so the
  fitted complexity model is a constant in the real regime — and a slow or broken call therefore
  consumes **nearly the full 180 s allowance** instead of being abandoned early in proportion to its
  size. Abandoning early *is the purpose the gate exists for*
  (`FAILURE_MODES_AND_KILL_GATE_2026-07-04.md:103-110`: it "saves the *rest*… and, crucially, unblocks
  the run so the card is recovered the cheap way").

A size-doomed kill and a route-slow kill are also telemetrically identical, because `kill_timeouts` is
a bare counter (packet **C-15**).

## 2. Exact saturation threshold

```
budget(skel) = min(180000, max(45000, 2.0 * (20000 + 45 * skel)))
```

| band | condition | budget |
|---|---|---|
| floor | `skel ≤ 55.56 B` | 45,000 ms |
| **proportional** | `55.56 < skel < 1555.56 B` | tracks skel |
| **saturated** | **`skel ≥ 1555.56 B`** | **180,000 ms** |

**Threshold: `skel = 70000/45 = 1555.5556 B`** — solve `2·(20000 + 45·skel) = 180000`.

The fitted model is operative over a **1,500-byte window**. Everything else is a constant.

## 3. Current candidate universe — exact skeletons, no ratio estimate

Computed with `pwg_mask.mask(raw)[0]` — the same pure function the harness uses
(`gen_opt_harness2.py:949`), over the 114 runnable nominal-core lemmas that have prebuilt inputs
(168 of the 282 have none on disk). Script: `src/pilot/output/h963_c4_campaign/killbudget_saturation.py`.

Skeleton bytes: min **1,182** · p05 2,617 · p25 5,024 · **median 7,977** · p75 12,072 · max **25,920**.

| budget assigned by the byte-scaled model | cards | share |
|---|---:|---:|
| 45 s (floor) | 0 | **0.0 %** |
| intermediate (proportional) | 1 | **0.9 %** |
| **180 s (saturated)** | **113** | **99.1 %** |

The single non-saturated card is the smallest in the universe (skel 1,182 B = 0.76× the threshold).
The median is **5.1×** the threshold; the max is **16.7×**.

**Under the branch that actually runs, it is 100 %** — see §4.

By scholarly band:

| band | n | median skel | min skel | % saturated |
|---:|---:|---:|---:|---:|
| **5** (ultra-core) | 82 | 9,085 B | 2,046 B | **100.0 %** |
| 4 | 32 | 5,024 B | 1,182 B | 96.9 % |

## 4. Single-card vs multi-card — two mechanisms, one outcome

```js
killBudgetForCur = cur => (cur.length === 1) ? KILL_CEIL_MS : killBudgetMs(skelBytesOfKeys(cur))
```

- **Single-card:** budget = `KILL_CEIL_MS` = 180,000 ms **unconditionally**. The skeleton is never
  consulted. This is an **explicit branch, not saturation** — and it is **deliberate** (§6).
  ⇒ **100 % of single-card calls get 180 s**, for all 114 candidates.
- **Multi-card:** budget = `killBudgetMs(Σ member skeletons)`. `skelBytesOfKeys` **sums**, so a batch is
  ≥ its largest member and saturates *a fortiori*. The two **smallest** candidates batched together are
  **3,228 B = 2.1× the threshold**. ⇒ **no real batch in this universe can be non-saturated.**

**Consequence: no real call in the nominal-core lane is ever governed by the fitted model** — by fiat
if single, by saturation if batched.

## 5. Historical timeouts — did they consume the full ceiling?

A kill-timeout consumes **exactly** the budget it was armed with (the timer fires at `ms`), so
*"consumed nearly the full ceiling"* ≡ *"was armed at the ceiling"*. Parsed from every retained
`wf_output`'s `summary.logs` — the only place per-timeout `skelBytes` is recorded. Script:
`src/pilot/output/h963_c4_campaign/historical_timeouts.py`.

**58 recoverable events** (21 wf_outputs scanned):

| mechanism that armed the timer | events | share |
|---|---:|---:|
| byte-scaled (**the model actually governing**) | 2 | **3.4 %** |
| `CEIL` by single-card branch | 48 | 82.8 % |
| `CEIL` by saturation | 8 | 13.8 % |
| **→ consumed the full 180 s** | **56** | **96.6 %** |

**96.6 % of historical kill-timeouts were armed at the ceiling.** The gate's purpose — abandon a doomed
call early, in proportion to its size — fired on **2 of 58**.

> **Do not quote this as a global rate.** The recoverable population is dominated by the no_pwg
> fragment/singles lane (skel 112–2,217 B) simply because those windows' `wf_outputs` survive. The
> whole-card nominal-core lane has exactly **one** retained event (`h963_c4_real`, skel 5,606,
> saturated). n is small and the lane mix is not the future mix.
>
> **A telemetry gap sits underneath this.** `kill_timeouts` is a bare counter; `skelBytes` survives only
> as free text in `summary.logs`. The recoverable 58 exceed the 45 declared across those same files
> because the log array is not per-event and spans requeue siblings — i.e. the two populations cannot be
> reconciled. **The historical distribution is not fully recoverable**, and that unrecoverability is
> itself part of **C-15**.

## 6. Is it accidental? **No** — and the record is explicit

Checked before classifying, as instructed.

**The design comment** (`gen_opt_harness2.py:183`): *"hard ceiling — NOTHING runs past 3 min (MG). Was
480000 (8 min); the worst pril10_w1 agent ran 390 s (6.5 min) inside the old ceiling."* → the 480→180
change is a **deliberate owner policy ruling**, applied to suppress an observed 390 s stall.

**The single-card branch** is incident-driven, not incidental. Per
[`KILL_CALIBRATION_REAUDIT_2026-07-09.md:30`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/KILL_CALIBRATION_REAUDIT_2026-07-09.md)
(H426, **adversarial**): *"nominal no-PWG singles | `killBudgetForCur` → `KILL_CEIL_MS` = 180 s (`:1283`,
H220) | fixed CEIL because a single fragment with `!hasFallback` has **no smaller lane** for the gate to
route to | ✅ | the dense byte budget (53–104 s) is below a tiny single's fixed StructuredOutput latency
(55–105 s) → the `NO_PWG_DIAG` 6/6-null kill-timeout incident (H220)."* `LAUNCH_FUCKUPS.md:216-220`
records H220 as `classification: kill-gate-calibration`, residual risk *"keep H220 **lane-specific**
calibration"*.

**The introducing commit is not recoverable.** `gen_opt_harness2.py` has 13 commits and the first
(`c89d0cf8`) is the import — history is squashed. Provenance survives **only in prose**. So "who changed
it when" cannot be audited from git; the comment and the two re-audits are the entire record.

### The accurate classification: **lane-scope drift**, not carelessness

H426 enumerated **five lanes**, each with its own budget model, and stated the governing principle:
*"none inherits the dense-root default blindly."* Every lane was marked ✅ — correctly, **for the
skeleton sizes those lanes carry**:

| lane | skeleton scale | model status |
|---|---|---|
| dense verb roots | 744–2,929 B (benchmark) | proportional band; ✅ as reviewed |
| no_pwg singles / presplit fragments | 11–485 B | floor/proportional, or the deliberate H220 fixed CEIL; ✅ |
| **nominal-core whole cards** (this lane) | **median 7,977 B, max 25,920 B** | **inherits `killBudgetMs`, 3–9× outside its fitted range ⇒ 99.1 % saturated** |

**The nominal-core whole-card lane is a newer consumer that inherited the dense-root default —
precisely what H426's principle forbids — and nobody re-derived the envelope when it arrived.** The
constants are not careless; they are *correct for lanes that are not this one*. That is the defect, and
it is a scope defect, not a tuning error.

Two further honesty points:

- **H426's ✅ on the dense-root lane restated the invariant rather than testing the clamp.** *"the
  factor+slope headroom means no legit call (even +50 % variance) is killed"* holds within 744–2,929 B;
  it does not survive the clamp at 8–26 KB. The claim was propagated from the design comment, not
  independently verified against the clamp. Fair, since the whole-card lane was out of scope.
- **The 180 s ceiling kills no measured legit call** (§7). "The ceiling is too low" is **not** the
  finding.

## 7. Would a lower ceiling kill clean calls? Yes — measured

Against the **only** measured population of known-legit calls (the 13-call `tyaj --no-tm` benchmark,
`FAILURE_MODES_AND_KILL_GATE_2026-07-04.md:122-131`; 7 main-batch calls carry per-call skel attribution,
plus `zz_pw` fragment groups at 70–108 s):

| candidate ceiling | legit main-batch calls killed | 108 s `zz_pw` fragment |
|---:|---:|---|
| 45 s (the current floor) | **3 / 7** (52.0 s, 60.7 s, 83.8 s) | killed |
| 60 s | **2 / 7** (60.7 s, 83.8 s) | killed |
| 90 s | 0 / 7 | **killed** |
| 120 s | 0 / 7 | survives |
| **180 s (current)** | **0 / 7** | survives |
| 480 s (the doc's value) | 0 / 7 | survives |

**No measured legit call is killed by the current ceiling.** Lowering to 90 s starts destroying real
work (the 108 s fragment); 60 s kills 2/7; the 45 s floor kills 3/7.

> **Load-bearing caveat.** The benchmark's largest skeleton is **2,929 B**; the candidate median is
> **7,977 B** and the max **25,920 B**. This table therefore says **nothing** about whether a large
> whole card is legit-slow past 180 s. n=13, one run, 04-07-2026. **The question "does a large card
> legitimately need >180 s?" is unmeasured** — and it is the question that decides the replacement.

## 8. Replacement policy — specification only, DO NOT IMPLEMENT in this campaign

**Design goal:** restore *discrimination* (abandon a doomed call early, in proportion to its size)
without lowering the effective ceiling for legit work, and without touching the two deliberate
decisions (MG's 3-minute rule; H220's single-card fixed CEIL).

**P0 — telemetry first, and it is unblocked today.** Emit `{skel_bytes, budget_ms, elapsed_ms, branch,
lane}` as a **structured** field per kill, not a prose log line. Without it, nothing below can be
validated and the historical distribution stays unrecoverable (§5). *This is behaviour-preserving and
should ship regardless of which policy is chosen.*

**P1 — make the lane explicit rather than inherited.** Give the nominal-core whole-card lane its own
declared budget model, per H426's own principle. The inheritance is the defect; naming the lane is the
minimal fix.

**P2 — replace the hard clamp with a rate-based abandon rule.** The clamp destroys the model because it
is an *absolute* bound on a *size-proportional* quantity. A rate bound does not saturate:

```
abandon when  elapsed_ms > max(FLOOR_MS, RATE_CEIL_MS_PER_BYTE * skel_bytes)
```
with `RATE_CEIL_MS_PER_BYTE` set above the observed worst legit rate (44 ms/B → e.g. 66 ms/B for +50 %
headroom). This preserves the original intent exactly ("no legit call is ever killed; a ~5× stall blows
past") **at every size**, and it is what the design comment already describes — the clamp is what broke
it. **A 5,606 B card would get 370 s under this rule, which exceeds MG's 3-minute rule ⇒ it is gated on
the `@DECIDE`, not an agent call.**

**P3 — if the 3-minute rule is retained** (owner's call): then the ceiling is a **scope decision**, not a
timeout, and it should be enforced *at admission*, not at abandon time. Refuse to dispatch a card whose
`RATE_CEIL_MS_PER_BYTE × skel` exceeds the ceiling, and route it to presplit. That converts a silent
180 s burn into a loud preflight refusal — the same policy, at 1/∞ the cost.

**Explicitly out of scope for the fix:** re-raising `KILL_CEIL_MS` unilaterally (MG ruling) · touching
the H220 single-card branch (deliberate; a 180 s no-op on a 150 B fragment harms nothing) ·
`KILL_FACTOR = 2.0` semantics · the fail-closed "never emit a partial card" rule · retuning
`perf_preflight` constants (packet C-40).

## 9. Regression matrix — specification only

Every row is offline and fixture-based; none needs a live call.

| # | Test | Asserts | Status today |
|---|---|---|---|
| R1 | `test_budget_is_not_saturated_across_the_real_universe` | for each of the 114 exact skeletons, `budget(skel) < KILL_CEIL_MS` **or** the lane declares a fixed-CEIL policy explicitly | **FAILS** (113/114 saturate by inheritance) |
| R2 | `test_no_legit_call_is_killed` | for every benchmark call (skel, wall), `budget(skel) > wall` — the invariant the code asserts at `:164-166` | **passes** at 180 s; the point is to **pin** it so a future ceiling change cannot break it silently |
| R3 | `test_budget_discriminates_stall_from_legit` | `budget(skel) ≥ FACTOR × worst_legit_rate × skel` for skel across 1 KB…26 KB | **FAILS** for skel > 1,556 B |
| R4 | `test_single_card_branch_is_declared_not_incidental` | the `cur.length === 1 → CEIL` path is reachable **only** for lanes whose manifest declares `fixed_ceil_policy: h220` | **FAILS** (applies to every lane) |
| R5 | `test_kill_telemetry_carries_size_and_budget` | a kill emits structured `{skel_bytes, budget_ms, elapsed_ms, branch, lane}` | **FAILS** (bare counter + prose) — packet C-15 |
| R6 | `test_doc_and_code_constants_agree` | the constants table in `FAILURE_MODES_AND_KILL_GATE_2026-07-04.md` equals the `gen_opt_harness2.py` globals | **FAILS** on all three (BASE 30 000 vs 20 000 · FLOOR 120 000 vs 45 000 · CEIL 480 000 vs 180 000) |
| R7 | `test_batch_budget_is_superadditive_safe` | `budget(Σ skel) ≥ max(budget(skel_i))` — batching must never shrink the allowance below any member's | **passes today only because both are the clamp** — vacuous, and would become live under P2 |
| R8 | `test_oversize_card_is_refused_at_admission` | under P3, a card whose projected rate·skel exceeds the ceiling is refused by preflight, not abandoned at 180 s | n/a — new behaviour, gated on the `@DECIDE` |

**R2 and R7 pass today and must be landed anyway**: they pin invariants that the P2/P3 change would
otherwise be free to break silently. Landing the failing rows (R1, R3, R4, R5, R6) **red, before any
fix**, is the recommended order — pin the defect with an assertion rather than with prose.

## 10. What remains unmeasured

- **Does a large whole card legitimately need >180 s?** Unmeasured, and it decides P2 vs P3. The rate
  fit behind every estimate is **13 calls, largest skeleton 2,929 B, one run** — the candidate median is
  2.7× beyond it.
- **The historical distribution** (§5) is not fully recoverable from a bare counter.
- **Whether the nominal-core lane's inheritance was ever considered.** Not auditable — squashed history.

_Dr. Mārcis Gasūns_
