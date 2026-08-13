# H2630 — Option A: the whole-card lane at n=4, sealed to the spend gate

_Created: 13-08-2026 · Last updated: 13-08-2026_

Pre-spend artifacts for [H2630](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2630-Opus_SanskritLexicography_prep-compare-whole-card-4-pairs-option-a_13.08.26.md)
(**Opus 5** — PREP compare Option A: 4 pairs on the 4 whole-card cards). Opus 5
(`claude-opus-5`), 13-08-2026. Predecessors:
[H2591](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/README.md)
(the n=8 run that came back INCONCLUSIVE) ·
[H2598](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/README.md)
(which measured the 4 / 44 lane split and tabled the three options) ·
[H2612](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2612/README.md)
(Option B, the 92 % lane, sealed and awaiting the same gate).

**Status: built, sealed and offline-green at zero spend.** `--check` passes **7 of 8**
conditions and fails closed on condition 8 exactly as designed — billing is UNKNOWN until a
human authorizes it. **No call was reserved and no spend occurred.**

## What a human chose, and what it cost to build

H2598 tabled three shapes and a human picked **A — 4 pairs on the 4 whole-card cards, 8
calls**. A was the one option H2598 had called *arithmetically unavailable*, and it was: the
rig hard-coded `PAIR_COUNT = 8` and the whole-card pool holds 4. The fix is not a smaller
copy of the rig but a **sealed sample size**:

- `pair_count` is threaded through selection, planning, the reservation ledger and the
  receipt, and is **sealed into plan.json** — keyed exactly the way `lane` is, so it appears
  only when it is not the default 8. H2591's and H2612's sealed plans therefore recompute
  their **original** hashes and still verify (both re-checked here; both still stop at the
  billing gate and nowhere earlier).
- It may only **shrink**. `build_plan` refuses `pair_count > 8`: this rig was authorized for
  at most sixteen irreversible calls, and a flag that could raise that would be a hole, not
  a feature.
- The ceiling is read from the **plan**, never from the module — `check`, `execute` and the
  receipt all take `2 x pair_count` off the sealed plan. Checking at one ceiling and
  executing at another was reachable before; it is not now, and
  `test_execute_ceiling_is_read_from_the_plan_not_the_module` pins it.

## The sample is a census, not a draw

`--select --pool whole-card` classifies the pool with production's own predicate
(`gen_opt_harness2._presplit_hit`, thresholds read from that module and never restated) and
returns every card production does **not** presplit:

| | keys | n |
|---|---|---|
| whole-card lane (this plan) | `idAnIm`, `prasU`, `rAtra`, `spfS` | **4** |
| pool | 48 distinct real cards after dedupe | 48 |

That reproduces H2598's measurement exactly. It also means the four cards are the
**population** of this lane, not a sample of it — there is no sampling error to quote, and
the four strata of `SELECTION_RULE` collapse by construction. The plan says so in
`whole_card_pool_rule.census_not_sample` rather than leaving a reader to infer it from an
empty `strata` dict.

## The correction this pass owes its own premise

H2598 argued A would at least be *production-faithful in call shape*. **The manifest refutes
that**, and the refutation is recorded in the sealed plan rather than smoothed over:

```
batches: [["idAnIm", "prasU"], ["rAtra", "spfS"]]     presplit_keys: []
```

Production does not **presplit** these cards — `presplit_keys` is empty, so the selector is
right about the lane — but it does **batch** them two per agent call. Production would issue
**2** calls per arm where this rig issues **4**. "Whole-card lane" means *un-split*, not
*one-card-per-call*. Both arms are affected identically, so the paired A-vs-B comparison is
unharmed; the absolute wall-clock and token figures are **not** production figures and must
not be quoted as such.

The other two non-equivalences are unchanged and also sealed: n=4 has real power loss
relative to n=8, and whole-card cards are citation-light **by construction** (that is *why*
production takes them whole), so this lane cannot exhibit the citation-dense failure mode at
all. A clean result here is not evidence about dense cards.

## Verification

| Check | Result |
|---|---|
| `prep_context_compare --selftest` | **24/24** hermetic cases, zero calls (19 before this pass; 5 new) |
| `window_selftest.py` | **211/211** |
| H2591 sealed plan re-checked | still verifies; blocks only at condition 8 |
| H2612 sealed plan re-checked | still verifies; blocks only at condition 8 |
| This plan `--check` | 7/8 conditions pass; **blocked at condition 8 (billing UNKNOWN)** |

Sealed here: `plan_sha256 = 3eb569a3d7d8b16242fb2ef6bc1f67cba561297c336b20c3ebae21ec3b061ff0`,
`pair_count = 4`, `max_calls = 8`, order `A B B A A B B A` over the four keys.

## The gate, which is not this session's to open

`--check` fails condition 8 until a human authorizes with `--authorize-unknown-billing`,
because [every Max-route call in this pipeline is accounted `unknown_gateway`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/README.md)
— nothing in the repo ever writes `execution.agent_sdk_credit_claimed`
([integrity issue #1649](https://github.com/gasyoun/SanskritLexicography/issues/1649)). Two
plans now stand at that one gate: this one (8 calls, 8 % lane) and H2612 (16 calls, 92 %
lane). Authorizing either is a spend decision.

Under either, the run may still halt on the unproven `rc=0` zero-usage class — by design,
loudly.

## Reproduce (offline, free)

```
python src/pilot/h1210/prep_context_compare.py --selftest
python src/pilot/h1210/prep_context_compare.py --select --pool whole-card \
    --out-dir src/pilot/h1210/h2630
python src/pilot/gen_opt_harness2.py nominal_h2630 --nominal --no-grammar \
    --keys=idAnIm,prasU,rAtra,spfS \
    --out=<scratch>.js --manifest-out=src/pilot/h1210/h2630/execution_manifest.h2630.json
python src/pilot/h1210/prep_pack.py --manifest src/pilot/h1210/h2630/execution_manifest.h2630.json \
    --manifest-authoritative --out-dir src/pilot/h1210/h2630/prep \
    --context-out-dir src/pilot/h1210/h2630/contexts
python src/pilot/h1210/prep_context_compare.py --plan \
    --manifest src/pilot/h1210/h2630/execution_manifest.h2630.json \
    --context-dir src/pilot/h1210/h2630/contexts --out-dir src/pilot/h1210/h2630
python src/pilot/h1210/prep_context_compare.py --check \
    --plan-file src/pilot/h1210/h2630/plan.json --run-id h2630
```

`PWG_INPUT_DIR` must point at the pilot input dir when generating the manifest. `--select`,
`--plan` and `--check` are offline and free; `--plan` takes its sample size from the
whole-card `selection.json`, so no flag can silently change it after the fact.

_Dr. Mārcis Gasūns_
