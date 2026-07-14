# Knob calibration — giant-head split granularity + output-budget headroom

_Created: 03-07-2026 · Last updated: 03-07-2026_

MG-authorized (02-07-2026) cheap A/B calibration of the two untuned big-article
knobs in [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py):
`AUTOSPLIT_LS_BUDGET` (giant-head fragment granularity, in
[`autosplit_requeue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py))
and `--output-budget` (citation-weighted batch sizing). Both were S10-era
values (18 and 60 respectively) never systematically tuned. Executed in a
fresh worktree off `origin/master` (`knob-calibration-20260703` branch) per
the handoff's branch-contention guardrail; all four runs SCRATCH only — never
touched `src/pwg_ru_translated.jsonl`.

Handoff: [`Uprava/handoffs/H066-Sonnet_SanskritLexicography_pwg_knob_calibration_02.07.26.md`](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H066-Sonnet_SanskritLexicography_pwg_knob_calibration_02.07.26.md).
Model: Sonnet 5 (`claude-sonnet-5`) throughout (generation + Workflow agents).

## 1. Giant-head split granularity — `AUTOSPLIT_LS_BUDGET` 18 (stock) vs 10 (finer)

Target: `gam~~h0_00_pwg00` (150 `<ls>`, presplit-routed to the fragment path
on both arms since it exceeds the output budget).

| | Arm A (stock, LS_BUDGET=18) | Arm B (finer, LS_BUDGET=10) |
|---|---:|---:|
| selfheal fragment groups | 9 | 17 |
| agent() calls | 13 | 21 |
| total tokens | 925,605 | 1,462,827 |
| tool calls | 18 | 34 |
| wall-clock | 615 s | 1,207 s |
| cards ok / null | 1 / 0 | 1 / 0 |
| outcome | healed, presplit | healed, presplit |

**Verdict: Arm A (stock 18) wins clearly.** Finer fragmentation produced
*more* fragment groups (17 vs 9), which drove up agent calls (+62%), tokens
(+58%), and wall-clock (+96%) for the **same** translated outcome (both
arms fully healed the one giant card, 0 null). Smaller fragments do not
reduce per-fragment failure risk enough to offset the added per-call
overhead at this citation density. **No change proposed** —
`AUTOSPLIT_LS_BUDGET` stays at its current default of 18.

## 2. Output-budget headroom — `--output-budget` 60 (stock) vs 90

Target: `hA` root, 56 cards (24 `h0_*` prefix cards + 30 `h1_*`/`h2_*`/`pw*`
cards, several dense enough to presplit).

| | Arm C60 (stock) | Arm C90 |
|---|---:|---:|
| batch count | 8 | 7 |
| presplit keys | 5 | 3 |
| selfheal groups (total) | 15 keys healed | 15 keys healed |
| agent() calls | 66 | 60 |
| total tokens | 4,675,011 | 4,025,248 |
| tool calls | 94 | 81 |
| wall-clock | 1,082 s | 496 s |
| cards ok / null | 56 / 0 (1 transient mid-stream stall, recovered) | 56 / 0 |
| partial (healed but incomplete-in-one-shot) keys | 1 | 1 |

**Verdict: Arm C90 wins clearly on both cost AND quality** (the handoff's
gating condition for a defaults-change PR): −9% agent calls, −14% tokens,
−14% tool calls, **−54% wall-clock**, identical null rate (0/56 both), and
*fewer* giant cards needed the presplit fragment path (3 vs 5, because more
cards fit whole within the larger budget). No retry-rate regression — the
one transient stall in Arm C60 does not appear in C90's failures. The
`yuj`-lesson risk (bigger budget → busier StructuredOutput retries eating
the token saving) did **not** materialize here.

## Decision

- `AUTOSPLIT_LS_BUDGET` — **unchanged at 18.**
- `--output-budget` default — **raised 60 → 90**, shipped in this same
  branch: [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  `OUTPUT_BUDGET = 90` (was 60), `window_selftest.py` 31/31 still green
  after the change (re-ran the canonical `run_pilot_wf.opt2.js` harness
  regeneration for `gam` to validate the harness-scope fixture).

## Caveats

- N=1 giant head and N=1 medium root — a single calibration point per arm,
  not a distribution. The direction (coarser is cheaper at these two
  knobs) is consistent with the general "fixed per-call overhead dominates"
  finding in [`TLONLY_PROTOTYPE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TLONLY_PROTOTYPE.md),
  but a wider sample (a few more giant heads / medium roots) would harden
  the output-budget=90 recommendation before pushing it further (e.g. to
  120) — not attempted here, out of session scope/budget.
- Quality (translation fidelity) was NOT separately judged in this session —
  "quality" here means the harness-level null/partial/retry signal only, per
  the handoff's instructions. A fidelity sample pass is a natural follow-up
  if 90 is scaled to a full freq-queue run.
- Follow-up calibrations should use
  [`calibrate_perf_harness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/calibrate_perf_harness.py)
  to generate scratch harness arms/manifests from a fixed key set, after checking
  the same keys with
  [`perf_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py).
  Keep the AB_TEST_LEAN_TR lesson: run live arms sequentially with cache cooldown;
  never run same-prompt arms in parallel.

_Dr. Mārcis Gasūns_
