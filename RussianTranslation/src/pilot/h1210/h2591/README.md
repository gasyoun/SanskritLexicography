# H2591 — bounded Claude comparison on sealed Flash PREP contexts

_Created: 12-08-2026 · Last updated: 12-08-2026_

Sealed artifacts for [H2591](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2591-Opus_SanskritLexicography_pwg-flash-prep-claude-bounded-context-compare_12.08.26.md)
(**Opus 5** — Run bounded Claude comparison on sealed Flash PREP contexts). Driver:
[prep_context_compare.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_context_compare.py)
· hermetic matrix:
[prep_context_compare_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_context_compare_selftest.py).

## Status — `BLOCKED_ON_BILLING_ATTRIBUTION`, zero Claude calls spent

Everything offline is built, sealed and green. **No paid call was made**, because the
handoff's own eighth precondition fires:

> affirmative local evidence that the Max Agent SDK credit was claimed; otherwise
> classify billing as unknown and require human authorization before `--execute`.

There is no such evidence anywhere in the repo, and that is not an oversight in this
pass — see *The billing gate* below. `--execute` therefore refuses, by design.

| Condition (handoff `--check` list) | Verdict |
|---|---|
| 1 · one immutable manifest source + manifest SHA per key | ✅ |
| 2 · valid, hash-replay-identical `pwg.prep_context.v1` | ✅ |
| 3 · identical base prompt bytes, schema, model id, output limit across arms | ✅ |
| 4 · arm A = production prompt unchanged | ✅ |
| 5 · arm B = same prompt + one canonical delimited PREP block | ✅ |
| 6 · `promotable=false`, `tm_policy.may_write=false`, fuzzy hits advisory | ✅ |
| 7 · fresh reservation ledger, ceiling 16 | ✅ |
| 8 · Max Agent SDK credit claim evidence | ⛔ **blocked** — billing UNKNOWN |

Offline transport calls attempted during `--check`: **0** (proven by a socket trap that
counts and refuses, not by assertion — [check.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/check.json) `network_calls`).

## Evidence in this directory

| File | What it pins |
|---|---|
| [selection.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/selection.json) | the eight frozen keys, their strata, the metrics, and which stratum predicates fell back |
| `execution_manifest.h2591.json` | the immutable execution manifest; the plan binds its SHA-256 |
| [plan.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/plan.json) | the sealed plan — `plan_sha256` `15f1f3a6db141828…`, both arms' prompt hashes, context hashes, argv hash, the GO rule, and the known non-equivalences |
| [check.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/check.json) | the offline fail-closed report, including the blocked condition |
| `contexts/` | eight sealed `pwg.prep_context.v1` seeds, manifest-sourced |
| `prep/` | the full prep sidecars those contexts were compiled from |
| `call_reservation.json` | the fresh ledger, ceiling 16, zero spent |

## The eight cards, and how they were chosen

The rule is recorded in [selection.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/selection.json) **before** any call, and a failed
card is never replaced after seeing output.

| Stratum | Keys | Predicate met? |
|---|---|---|
| long / monster-adjacent | `SvAsa` (11 427 B), `spfS` (11 134 B) | ✗ fell back to the two largest — no card in the pool reaches the 12 000 B monster threshold |
| markup-heavy | `Srama` (234 placeholders), `samIpa` (234) | ✓ |
| polysemous | `vyavasTA` (11 senses), `SudDi` (9) | ✓ |
| simple | `rAtra` (2 409 B), `zoqaSan` (2 891 B) | ✗ fell back to the two smallest — no PWG card is markup-light enough to meet `placeholders ≤ 2` |

Both fallbacks are recorded rather than hidden: those four cards are "the two most X
available", not "two cards that met the X threshold", and a receipt that blurred the two
would overstate what `n=8` covers.

**Two pool defects the selection surfaced**, both fixed before sealing:

1. The pilot input dir holds several cards **twice** under a transliterated and a
   safe-name spelling with byte-identical raws (`vyavasTA` / `vyavas_t_a`, `Srama` /
   `_srama`, `SvAsa` / `_sv_asa`). The first selection pass picked both members of three
   such pairs — a "stratified eight" that was really five cards. Selection now dedupes on
   the raw content SHA-256; the pool is 48 distinct cards, not 85 filenames.
2. The curated synthetic canary (`dq_canary_puregloss`) sits beside real cards and was
   picked into the *simple* stratum. H2591 requires eight **real** cards, so synthetic
   fixtures are now excluded by prefix.

## `prep_pack --manifest` could not actually produce a manifest-sourced context

Condition 1 was **unsatisfiable through the released tool**, and this is the substantive
finding of the pass.

`prep_pack.fill_one` ranks `de_source` (a local `<key>.raw.txt`) above the manifest, and
`load_de_source` falls back to a hardcoded main-checkout input dir. So on any machine that
has the raws — i.e. every working checkout — `de_src` is truthy and the
`execution_manifest` branch is **dead code**. The immutable-source guarantee was reachable
only by accident, on a machine *missing* its inputs. That is the same
source-discovery class the H2489 spike measured as a 45% park rate.

Fix (this PR): an explicit
[`--manifest-authoritative`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_pack.py)
flag. Default behaviour is unchanged — a local raw still wins — but a consumer that must
bind immutable bytes can now say so. Pinned by a new `prep_pack --selftest` case asserting
both directions (raw wins by default; the flag flips the source kind and makes the
semantic PREP hash independent of which raws sit on this disk).

## The billing gate — why it cannot be cleared from inside a session

`headless_worker` reads `execution.agent_sdk_credit_claimed` /
`agent_sdk_credit_claim_evidence` from the manifest, and **nothing in the repo ever writes
them**. `gen_opt_harness2` does not emit them; `max_account_orchestrator.profile_status`
calls `telemetry_from_cli_wrapper(max_agent_sdk_credit=True)` with no claim evidence at
all. `usage_accounting.build` then deliberately downgrades the billing mode to
`unknown_gateway` and nulls the list equivalent.

So today **every** Max-route call in this pipeline is accounted as UNKNOWN billing, and
the credit-accounting path added for it is dormant. For H2591 that means the eighth
precondition can only be cleared by a human, in one of two ways:

```
# (a) authorize the spend with billing explicitly classified UNKNOWN
python src/pilot/h1210/prep_context_compare.py --check --plan-file src/pilot/h1210/h2591/plan.json --authorize-unknown-billing
python src/pilot/h1210/prep_context_compare.py --execute --plan-file src/pilot/h1210/h2591/plan.json
python src/pilot/h1210/prep_context_compare.py --receipt --plan-file src/pilot/h1210/h2591/plan.json

# (b) or first make the claim real: record the credit claim + its evidence string in the
#     manifest's execution block, after which --check passes condition 8 on its own.
```

Route (b) is the better one — it turns a standing accounting fiction into a fact — but it
is a change to what the org asserts about its own billing, not a code detail, so a human
should decide which route to take.

## Known non-equivalences (stated, not buried)

- **Whole-card single call per arm.** The generator reports 47 expected agent calls for
  this manifest: production would **presplit six of these eight cards** into fragments.
  The prompt *bytes* are production bytes; the call *shape* is not. Both arms are affected
  identically, so the paired A-vs-B comparison is unharmed — but the absolute wall-clock
  and token figures this rig would produce are **not** production figures.
- **Unbound manifest** (`pwg.headless_execution_manifest.v1`): this rig does not run
  through the coordinator/profile lane. It is a measurement rig, never a bulk path.
- The manifest declares `claude-sonnet-5` as the lane default; both arms explicitly
  request `claude-opus-5` and the returned model is attested per call, with any
  substitution stopping the run at that call.

## Reproduce

```
python src/pilot/h1210/prep_context_compare.py --selftest
python src/pilot/h1210/prep_context_compare.py --select --out-dir src/pilot/h1210/h2591
python src/pilot/gen_opt_harness2.py nominal_h2591 --nominal --no-grammar \
    --keys=SvAsa,spfS,Srama,samIpa,vyavasTA,SudDi,rAtra,zoqaSan \
    --out=<scratch>.js --manifest-out=src/pilot/h1210/h2591/execution_manifest.h2591.json
python src/pilot/h1210/prep_pack.py --manifest src/pilot/h1210/h2591/execution_manifest.h2591.json \
    --manifest-authoritative --out-dir src/pilot/h1210/h2591/prep \
    --context-out-dir src/pilot/h1210/h2591/contexts --store <store.jsonl>
python src/pilot/h1210/prep_context_compare.py --plan --manifest src/pilot/h1210/h2591/execution_manifest.h2591.json \
    --context-dir src/pilot/h1210/h2591/contexts --out-dir src/pilot/h1210/h2591
python src/pilot/h1210/prep_context_compare.py --check --plan-file src/pilot/h1210/h2591/plan.json
```

`--select`, `--plan` and `--check` are offline and free. `PWG_INPUT_DIR` must point at the
pilot input dir when generating the manifest.

_Dr. Mārcis Gasūns_
