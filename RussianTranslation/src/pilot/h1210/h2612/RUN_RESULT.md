# H2612 executed — the fragment lane returns **NO-GO**, and H2591's zero-usage class is solved

_Created: 13-08-2026 · Last updated: 13-08-2026_

The paid half of [H2612](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2612-Opus_SanskritLexicography_pwg-prep-fragment-lane-compare_12.08.26.md)
(**Opus 5** — Qualify PREP context on the FRAGMENT lane, where 92 % of cards actually go),
run on human authorization with billing explicitly classified UNKNOWN. Opus 5
(`claude-opus-5`), 13-08-2026. Sealed plan `0e6a6e2516abf418…` — unchanged from
[the offline pass](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2612/README.md).

## Verdict: NO-GO

**16 of 16 calls, no stop, every reservation finalized exactly once, zero evidence holes**
— the first run of this rig to reach a verdict that is not INCONCLUSIVE.

| | arm A (baseline) | arm B (PREP) |
|---|---|---|
| calls | 8 | 8 |
| schema returned | 7 | 8 |
| audited pass | 6 | 7 |
| wall total | 1 601 s | 1 437 s |
| usage holes | 0 | 0 |
| unattested model | 0 | 0 |

The GO rule is *lose ≤1 audited card **and** improve wall or non-cache tokens by >10 %*.
On arm totals it fires: **+10.21 %** wall, and PREP loses nothing. **It does not survive
decomposition** — and this time the decomposition is a committed script, not an eyeball:

| basis | wall margin |
|---|---|
| arm totals (what the old rule read) | **+10.21 %** |
| failed calls removed | **−8.85 %** |
| **paired, over the 7 units both arms returned schema** | **+4.25 %** |

Arm A carries one `cli_error_exit` refusal at 280 s (`SvAsa#g2`). That single failed call
*is* the margin. Paired, PREP is faster on **4 of 7** units and slower on 3, and the total
is carried by one unit (`SudDi#g2`, +192 s) against `samIpa#g0` going the other way
(−145 s). Paired non-cache tokens: **+3.34 %** for PREP. Neither axis clears 10 %.

**So: PREP context does not earn a route change on the fragment lane at n=7.** It does not
hurt either — no audited card was lost to it, and it was marginally cheaper on tokens.
[decompose_margin.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2612/decompose_margin.py)
reproduces every number above.

## The rule that let a GO fire twice on an artefact — now fixed

H2591's GO was withdrawn because its +26.9 % was mostly the difference between how long
each arm took to **fail**. H2612's GO fired on the same class: one arm-A refusal. Twice in
two runs, so the arithmetic itself was wrong, not the reading of it.

`build_receipt` now keys the GO off **`paired_deltas`** — wall and token margins over the
units where *both* arms returned schema — and reports the arm totals for continuity only,
labelled as not the basis. An arm total silently rewards the arm that fails **faster**,
which is the opposite of what a qualification measures. Pinned by
`test_go_rests_on_the_paired_margin_not_on_how_fast_an_arm_failed`, whose fixture makes the
arm total look like a win and asserts the verdict is NO-GO anyway.

The originally-sealed [comparison_receipt.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2612/run3/comparison_receipt.json)
(verdict GO, `3f6c7b2b…`) is **kept exactly as sealed** — it is the evidence for changing
the rule, and overwriting it would erase that. The re-grade sits beside it as
[comparison_receipt.regraded.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2612/run3/comparison_receipt.regraded.json)
(verdict NO-GO, `7b51bc39…`), naming the original it supersedes.

## H2591's unexplained zero-usage class: identified, and recovered

B1 left it as *intermittent, root cause UNPROVEN*. It reproduced on this run's second
attempt at ordinal 5 (`SvAsa#g1`, arm A) — and the `usage_cross_check` shipped for B1
caught it instead of holing the comparison:

```
type: result · subtype: success · terminal_reason: completed · is_error: false
num_turns: 2 · total_cost_usd: 0.4029715 · a full audited card at coverage 1.0
usage: all zeros          modelUsage: 73 620 tokens
```

A completely successful call whose **top-level `usage` block was dropped while `modelUsage`
kept the real counts**. Not limit churn, not a failed call, not a driver misread — the
accounting block is simply absent sometimes on an otherwise-clean result. That is the class
behind H2591's "2 of 16 rc=0 calls with zero usage", now named.

Halting on it throws away a measurement that exists, so `recover_usage` adopts `modelUsage`
in **this one direction** (`usage` all-zero **and** `modelUsage` populated), marks the
envelope `usage_source: modelUsage`, and discloses every recovered call in the receipt's
`evidence_holes`. B1 had already measured the two sources agreeing exactly on healthy
calls, so this recovers a number rather than inventing one. Any other disagreement — both
populated and different, or `usage` populated while `modelUsage` is zero — remains
unexplained and still stops the run. The final run used the recovery **once**, on ordinal 13.

## Two more defects the run surfaced

1. **A timeout was unreachable as a class.** `parse_error` was checked before `timed_out`,
   and a timed-out call returns empty stdout which never parses — so every abandoned call
   was filed `malformed_envelope` ("the provider sent garbage") when the truth was "we
   stopped waiting". The first attempt died exactly there. Timeout now classifies first and
   stops the run with its own message, ahead of the unattested check that used to take the
   blame for it.
2. **A 30-minute stall that was not a size problem.** Attempt 1 halted when `vyavasTA#g1`
   (11 fragments) sat for the full 1800 s. [timeout_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2612/timeout_probe.py)
   re-issued that byte-identical prompt (hash-verified against the sealed plan) and it
   returned in **307 s** with 131 887 tokens and `subtype: success`. The ceiling was never
   the problem; it was the same per-call provider churn H2598 characterised. Raising the
   timeout would have been a fix for the wrong thing.

## Spend

| attempt | calls | outcome |
|---|---|---|
| run (attempt 1) | 1 | halted — `vyavasTA#g1` stalled past 1800 s, then filed as `malformed_envelope` |
| timeout probe | 1 | diagnostic, outside any ledger — same prompt returned in 307 s |
| run2 (attempt 2) | 5 | halted — `usage_contradiction` at ordinal 5, the class identified above |
| **run3 (attempt 3)** | **16** | **complete, no stop, verdict NO-GO** |

**23 paid calls total**, billing `unknown_gateway` throughout as authorized. No store, TM,
promotion or default-route write; `promotable=false` unchanged. Each halt produced a driver
fix that is now pinned by a test — matrix **22/22**, window suite **211/211**.

## Per-call record (run3)

| # | arm | unit | wall | outcome |
|---|---|---|---|---|
| 1 | A | `vyavasTA#g1` | 201 s | audited ✅ cov 1.0 |
| 2 | B | `vyavasTA#g1` | 178 s | audited ✅ cov 1.0 |
| 3 | B | `SudDi#g1` | 226 s | audited ✅ cov 1.0 |
| 4 | A | `SudDi#g1` | 190 s | audited ✅ cov 1.0 |
| 5 | A | `SvAsa#g1` | 167 s | audited ✅ cov 1.0 |
| 6 | B | `SvAsa#g1` | 175 s | audited ✅ cov 1.0 |
| 7 | B | `vyavasTA#g0` | 179 s | audited ✅ cov 1.0 |
| 8 | A | `vyavasTA#g0` | 192 s | audited ✅ cov 1.0 |
| 9 | A | `Srama#g3` | 137 s | audited ✅ cov 1.0 |
| 10 | B | `Srama#g3` | 121 s | audited ✅ cov 1.0 |
| 11 | B | `SudDi#g2` | 121 s | audited ✅ cov 1.0 |
| 12 | A | `SudDi#g2` | 313 s | audited ✅ cov 1.0 |
| 13 | A | `SvAsa#g2` | 280 s | `cli_error_exit` (usage recovered from `modelUsage`) |
| 14 | B | `SvAsa#g2` | 173 s | audited ✅ cov 1.0 |
| 15 | B | `samIpa#g0` | 264 s | audit fail cov 0.0 |
| 16 | A | `samIpa#g0` | 119 s | audit fail cov 0.0 |

Both arms failed `samIpa#g0` identically — a solo group whose single fragment came back
without its skeleton's token multiset. Same in both arms, so it says something about the
card, not about context design.

## What this does and does not license

- It **does** settle the question H2598 posed: on the lane that carries 92 % of cards, PREP
  context is not worth a route change at this sample size.
- It does **not** license a route switch in either direction, and it is **not** production
  evidence: n=7 paired units, no heal/bisect ladder, no kill gate, and arm B hands a group
  the whole card's context (a per-card artifact on a per-fragment call).
- [H2595](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2595-Opus_SanskritLexicography_pwg-flash-prep-larger-preregistered-experiment_12.08.26.md)
  stays parked. It was filled from H2591's withdrawn GO; nothing here revives it, and a
  NO-GO is not the premise it was written against.

_Dr. Mārcis Gasūns_
