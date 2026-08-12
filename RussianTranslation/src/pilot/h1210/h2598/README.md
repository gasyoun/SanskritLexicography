# H2598 — clearing B1 and B2 before any call is reserved

_Created: 12-08-2026 · Last updated: 12-08-2026_

Pre-spend evidence for [H2598](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2598-Opus_SanskritLexicography_pwg-prep-compare-rerun-after-usage-reporting-trustworthy_12.08.26.md)
(**Opus 5** — Re-run the PREP context qualification once usage reporting is trustworthy and
dense cards go through the presplit lane). Opus 5 (`claude-opus-5`), 12-08-2026.
Predecessor: [H2591](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/README.md)
· [B1 diagnosis](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/B1_ZERO_USAGE_DIAGNOSIS_12-08-2026.md).

**Status: both blockers discharged, and the second one moved the goalposts.** The driver
defect the handoff named is fixed and pinned; B1's owed check came back *negative* on its
own hypothesis; B2's re-check shows the re-run **cannot** be re-selected as the handoff's
first option assumed. **No call was reserved and no spend occurred in this pass.**

## The driver defect: an absent `returned_model` now stops the run at call time

H2591's call 09 was reserved, finalized and paid while naming no model at all. The
substitution guard waved it through, because absence is not substitution — so the run
continued and the hole surfaced only at receipt time.
[`prep_context_compare.execute`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_context_compare.py)
now stops on `model_unattested` at the call that produced it.

This is deliberately **stricter** than the `cli_error_exit` continue-rule shipped for B1: a
provider refusal that still names its model is a verdict on one call, whereas an unattested
call leaves the ledger holding spend it cannot assign to anything. Pinned by
`test_absent_returned_model_stops_the_run`, which asserts both directions — a clean audited
card with no model stops the run, and so does the call-09 shape (`rc=1` **and** unattested),
while the attested refusal one case above still runs to the ceiling.

Matrix **15/15**, window suite **211/211**.

## B1 · the limit-window check came back negative — and the recorded window was wrong

The B1 diagnosis owed one check: *was the account under a limit window during 07:53–11:40
UTC on 12-08-2026?* Two corrections, both from
[b1_limit_window_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/b1_limit_window_probe.py)
reading the sealed reservation ledger's own timestamps:

1. **The run did not happen in that window.** H2591's sixteen calls ran
   **13:25:56 – 14:26:19 UTC**. The window the diagnosis named is an hour-and-a-half of
   clock nobody spent a call in, so checking it would have proved nothing either way.
2. **A single provider limit window is refuted, not merely unconfirmed.** The `rc=1`
   refusals are ordinals 5, 6, 7, 8, 9 **and 11** — and ordinal **10** sits between them:
   `rc=0`, an audited card at coverage 1.0, and **75 580** tokens reported, at 14:12:37,
   fifty-eight minutes into the run and squarely inside the refusal span. A limit window
   refuses everything inside it. This one did not.

| # | key | rc | started (UTC) | tokens | model |
|---|---|---|---|---|---|
| 8 | `samIpa` | 1 | 14:01:30 | 0 | attested |
| 9 | `vyavasTA` | 1 | 14:06:54 | 0 | **unattested** |
| **10** | **`vyavasTA`** | **0** | **14:12:37** | **75 580** | **attested** |
| 11 | `SudDi` | 1 | 14:15:25 | 0 | attested |

So the refusals are **per-call**, not per-window. That does not identify the cause — the
provider exposes no queryable limit history, and `claude auth status --json` reports
subscription type only — but it removes the one hypothesis B1 left standing, and it means a
re-run can meet the same churn at any ordinal. The mitigation is unchanged and already
shipped: the run now halts loudly on `usage_contradiction` / `missing_usage` /
`model_unattested` instead of grading a holed comparison.

Two further facts the timeline surfaces, both consistent with per-call churn: ordinal 5 was
`rc=1` yet reported **69 076** tokens (partial spend before the error), and the only two
`rc=0` zero-usage calls are ordinals **1 and 4** — the *first* and *fourth* calls, before
any refusal appeared.

## B2 · the premise did not merely weaken — the first option is unavailable

The handoff offers two ways forward: *"Either re-select to cards production takes whole, or
run through the fragment lane."*
[b2_whole_card_pool.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/b2_whole_card_pool.py)
classifies the whole pool with production's own predicate
(`gen_opt_harness2._presplit_hit`, cite floor 40 / sense budget 20 — read from the module,
never restated):

| lane | cards | share |
|---|---|---|
| whole-card | **4** — `spfS` (30), `prasU` (31), `rAtra` (33), `idAnIm` (36) | 8 % |
| presplit (fragment lane) | 44 | 92 % |

**The rig needs eight cards and the pool holds four.** Re-selecting to cards production
takes whole is arithmetically impossible at `PAIR_COUNT = 8`, and every portrait in the
project lives in the one pilot input dir (85 files, 48 distinct after content dedupe), so
there is no second pool to draw from without generating new portraits first.

Two consequences worth stating plainly rather than routing around:

- Of H2591's eight cards, **exactly two** (`spfS`, `rAtra`) were in production's whole-card
  lane. `spfS` passed the audit in both arms; `rAtra` failed in both, on the real content
  defect (`{T2}` emitted, `{T72}`/`{T73}` dropped). Neither was ever refused.
- A whole-card A/B — however clean its usage accounting — qualifies PREP for the lane that
  carries **8 %** of this pool. The design question production actually faces is about the
  fragment lane.

That is the substantive finding of this pass: the re-run as specified would buy a sound
verdict about a minority lane. Which is not what the sixteen calls are for.

## What a human decides next

Three paths, and the choice reallocates real spend, so it is not this session's to make:

| | shape | calls | what it buys |
|---|---|---|---|
| **A** | 4 pairs on the 4 whole-card cards | 8 | production-faithful, honest, `n` halved and all four strata collapse (whole-card cards are citation-light by construction) |
| **B** | build the fragment-lane comparison | new build | qualifies PREP where 92 % of cards go — the lane that matters |
| **C** | generate ~100 new portraits to find 8 whole-card cards | offline first, then 16 | keeps `n = 8` and the rig untouched; strata still collapse, and it still measures the 8 % lane |

Under any of them the run may still halt on the unproven `rc=0` class — by design, loudly.

The spend gate is unchanged and human-owned: `--check` fails condition 8 until a human
authorizes with billing explicitly classified UNKNOWN (`--authorize-unknown-billing`),
because [every Max-route call in this pipeline is accounted `unknown_gateway`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/README.md).

## Evidence in this directory

| File | What it pins |
|---|---|
| [b1_limit_window_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/b1_limit_window_probe.py) | rebuilds the per-call UTC timeline from the sealed ledger and tests refusal-contiguity; refutes, never confirms |
| [b1_limit_window_timeline.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/b1_limit_window_timeline.json) | the sixteen calls with start/end UTC, exit code, tokens, attestation |
| [b2_whole_card_pool.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/b2_whole_card_pool.py) | classifies every pool card by production's own presplit predicate |
| [b2_whole_card_pool.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/b2_whole_card_pool.json) | the 4 / 44 split, per-card cite units, senses and placeholders |

Both scripts are read-only, offline and free; neither writes unless `--out` is given.

## Reproduce

```
python src/pilot/h1210/prep_context_compare.py --selftest
python src/pilot/window_selftest.py
python src/pilot/h1210/h2598/b1_limit_window_probe.py
python src/pilot/h1210/h2598/b2_whole_card_pool.py
```

_Dr. Mārcis Gasūns_
