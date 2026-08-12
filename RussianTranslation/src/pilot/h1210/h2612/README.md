# H2612 — the FRAGMENT lane, sealed and offline-green at zero spend

_Created: 12-08-2026 · Last updated: 12-08-2026_

Artifacts for [H2612](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2612-Opus_SanskritLexicography_pwg-prep-fragment-lane-compare_12.08.26.md)
(**Opus 5** — Qualify PREP context on the FRAGMENT lane, where 92 % of cards actually go),
lane **B** of [H2598](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/README.md)'s
decision. Opus 5 (`claude-opus-5`), 12-08-2026.

**Status: plan sealed, `--check` 7/8 with 0 transport calls, blocked exactly where it should
be — the human billing gate. No call was reserved and no spend occurred.**

## Why a second lane and not a second rig

H2598 measured the pool at **4 whole-card / 44 presplit**: production sends 92 % of these
cards as presplit *groups*, so the whole-card A/B qualifies PREP for the 8 % lane. The fix
is not a new rig — it is the same rig with the call **shape** production uses.

The lane already existed in the data. The generator emits `presplit_keys` and
`fragment_groups` into the execution manifest, and
[`headless_worker.build_fragment_prompt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
is the function that turns one group into one production agent call — the same one
[pwg_batch.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/pwg_batch.py)
consumes. So **arm A is that function's bytes, untouched**, exactly as arm A has always been
`build_prompt`'s bytes on the whole lane. Nothing about the fragment shape is re-implemented
here; if production's builder changes, arm A changes with it.

`lane` is sealed **into the plan**, never a runtime flag — a comparison whose call shape
could change between `--check` and `--execute` would be measuring two things under one hash.
Plans sealed before this lane existed carry no `lane` key and read as `whole`, so H2591's
sealed plan still replays its original hash (pinned by
`test_whole_lane_plan_hash_survives_the_fragment_lane`).

## The sampling trap this rig walked into once and backed out of

The first sealed plan ranked groups by fragment count and drew the eight biggest. It looked
clean — 8 groups, 4 parent cards, cap honoured, no relaxation. It was **the same error
H2598 had just caught, one level down**: of the 46 groups in this manifest, **31 (67 %) are
solo** — one fragment, one call. A size-ranked sample draws entirely from the multi-fragment
minority and then reports on "the fragment lane".

The rule now stratifies by call **shape** and takes four of each:

| stratum | what it is | share |
|---|---|---|
| `multi_fragment` | 2+ fragments in one call | 4 of 8 |
| `solo_fragment` | exactly 1 fragment in one call — 67 % of this manifest's groups | 4 of 8 |

with **at most 2 groups per parent card** across both strata, because `samIpa` alone
contributes 31 solo groups and would otherwise *be* the sample. A stratum that cannot fill
its share, or a cap that has to relax, is **recorded in the plan**
(`group_selection_relaxations`), never quietly absorbed.

## The sealed sample

`plan_sha256` `0e6a6e2516abf418…` · 8 groups · 16 calls · 5 parent cards.

| unit | fragments | stratum | arm A | arm B |
|---|---|---|---|---|
| `vyavasTA#g1` | 11 | multi | 27 379 B | 29 180 B |
| `SudDi#g1` | 10 | multi | 26 562 B | 28 730 B |
| `SvAsa#g1` | 10 | multi | 26 354 B | 27 698 B |
| `vyavasTA#g0` | 9 | multi | 27 567 B | 29 368 B |
| `Srama#g3` | 1 | solo | 27 467 B | 28 858 B |
| `SudDi#g2` | 1 | solo | 27 839 B | 30 007 B |
| `SvAsa#g2` | 1 | solo | 31 535 B | 32 879 B |
| `samIpa#g0` | 1 | solo | 28 219 B | 29 954 B |

No relaxations were needed.

## The audit is production's rule, not a new one

A fragment call returns `<key>_f<i>` cards, and
[`headless_worker.heal_group`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
accepts each on two conditions and no others: it is addressable at that fragment key, and
its `{Tn}` multiset equals **that fragment's own** skeleton's. `audit_fragment_group` reuses
exactly that, and reports coverage as fragments accepted over fragments requested.

The obvious shortcut — scoring fragments against the whole card's placeholder map — reads as
mass loss on every fragment and **inverts the verdict**. `test_fragment_audit_scores_each_
fragment_against_its_own_skeleton` drives that case from both sides: a faithful group passes
at coverage 1.0, a group answering with the whole card's token map is
`fragment-fidelity-reject`ed, a dropped token gives partial coverage, and an unaddressable
group is a miss rather than an exception.

## What is NOT equivalent to production (stated, not buried)

Both are recorded in the plan's `known_non_equivalences`:

- **No heal / bisect ladder and no kill gate.** Production retries, bisects and kill-times a
  group; this rig records a failed group as failed. Both arms are affected identically, so
  the paired comparison is unharmed — the absolute figures are not production figures.
- **PREP context is per-CARD, a fragment call is part of a card.** Arm B hands a group the
  whole card's context, so the context block does not shrink with the group. That is the
  design under test, not a defect, but a cost comparison must read it that way — it is why
  the solo-group rows above carry the largest B−A byte deltas.

## Verification

| | |
|---|---|
| `prep_context_compare --selftest` | **19/19** hermetic cases, zero calls |
| `window_selftest.py` | **211/211** |
| `--check --plan-file h2612/plan.json` | **7 of 8** conditions, `network_calls: 0` |
| blocked by | `billing_attributable_or_authorized` — by design |

[check.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2612/check.json)
records the blocked state rather than a bare refusal: the gate fired, and which condition
fired is evidence the next session needs.

## To run it — a human's line, not this session's

Every Max-route call in this pipeline is accounted `unknown_gateway`; nothing in the repo
writes the credit claim ([integrity issue #1649](https://github.com/gasyoun/SanskritLexicography/issues/1649)).
So condition 8 stays closed until a human authorizes the spend with billing explicitly
classified UNKNOWN:

```
python src/pilot/h1210/prep_context_compare.py --check --plan-file src/pilot/h1210/h2612/plan.json --run-id h2612 --authorize-unknown-billing
python src/pilot/h1210/prep_context_compare.py --execute --plan-file src/pilot/h1210/h2612/plan.json --run-id h2612
python src/pilot/h1210/prep_context_compare.py --receipt --plan-file src/pilot/h1210/h2612/plan.json --run-id h2612
```

The run halts loudly on `usage_contradiction`, `missing_usage`, `model_unattested` or
`model_substitution`; an `rc=1` provider refusal is recorded and the run continues. Per
[H2598's B1 finding](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/README.md),
the provider churn that holed H2591 is **per-call**, so a halt at any ordinal is possible —
read the envelope's `subtype` / `terminal_reason` / `api_error_status` / `raw_result` before
re-running.

## Reproduce (offline, free)

```
python src/pilot/h1210/prep_context_compare.py --selftest
python src/pilot/h1210/prep_context_compare.py --plan --lane fragment \
    --manifest src/pilot/h1210/h2612/execution_manifest.h2612.json \
    --context-dir src/pilot/h1210/h2612/contexts --out-dir src/pilot/h1210/h2612
python src/pilot/h1210/prep_context_compare.py --check --plan-file src/pilot/h1210/h2612/plan.json --run-id h2612
```

_Dr. Mārcis Gasūns_
