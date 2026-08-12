# H2591 — bounded Claude comparison on sealed Flash PREP contexts

_Created: 12-08-2026 · Last updated: 12-08-2026_

Sealed artifacts for [H2591](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2591-Opus_SanskritLexicography_pwg-flash-prep-claude-bounded-context-compare_12.08.26.md)
(**Opus 5** — Run bounded Claude comparison on sealed Flash PREP contexts). Driver:
[prep_context_compare.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_context_compare.py)
· hermetic matrix:
[prep_context_compare_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_context_compare_selftest.py).

## Status — run EXECUTED 12-08-2026, verdict **INCONCLUSIVE**

A human authorized the spend with billing explicitly classified UNKNOWN
(`--check --authorize-unknown-billing`), all eight `--check` conditions passed with **0
transport calls**, and the sealed order ran to completion: **16 of 16 reserved calls, no
stop condition, every reservation finalized exactly once.**

The verdict is **INCONCLUSIVE**, and the reason is the most useful thing this run produced.

| | arm A (baseline) | arm B (PREP) |
|---|---|---|
| audited pass | 4 / 8 | 4 / 8 |
| schema returned | 5 / 8 | 5 / 8 |
| wall total | 2 092 s | 1 529 s |
| calls with zero-filled usage | 4 | 3 |
| calls with unattested model | 1 | 0 |

### Why the first receipt said GO, and why that was wrong

The GO rule is *lose ≤1 audited card **and** improve wall or non-cache tokens by >10 %*.
PREP lost zero cards and showed a **+26.9 % wall-time margin**, so the arithmetic fired GO.
Decomposing the margin kills it:

* arm A's three failed calls burned **967 s**; arm B's three burned **625 s**. The margin is
  mostly the difference between how long each arm took to **fail**, which says nothing about
  translating a card.
* On the four cards both arms actually returned schema for, the paired margin falls to
  **+20.9 %** and is dominated by one card (`spfS`, −247 s) against another going the other
  way (`SvAsa`, +96 s). n=4, two signs.

### The token axis does not exist — zero-filled usage

**Seven of sixteen calls returned every usage counter zeroed** — including two arm-A calls
that produced full cards passing the deterministic audit at coverage 1.0, which is
arithmetically impossible.

`usage_evaluable()` checked the **shape** of the usage block, not whether it said anything,
so a zero-filled dict passed as present usage. That is worse than absent usage: it silently
deflates whichever arm receives it, so a token comparison built over it reads as a
measurement instead of as a hole. The reported "PREP costs 2.4× the non-cache tokens" is a
hole, not a finding. **The run should have stopped at call 1.**

Fixed in the same pass: all-zero usage now reads as missing (stopping the run), and any
usage hole or unattested model forces INCONCLUSIVE ahead of the GO arithmetic. Pinned by
`test_zero_filled_usage_is_missing_usage_not_a_measurement` (matrix now 13/13).

### What the run did establish

* **The markup-heavy stratum is unqualifiable at this call shape.** `Srama` and `samIpa`
  (234 placeholders each) returned non-JSON at char 0 in **both** arms, at 141–324 s. The
  card defeats the whole-card call regardless of context — a statement about production's
  presplit lane, not about context design.
* **The two asymmetric pairs cancel.** `vyavasTA` passed only in B, `SudDi` only in A, at
  near-identical wall times. The silent-empty failures look stochastic, not arm-driven.
* **A real content defect:** `rAtra` arm A emitted `{T2}`, a placeholder the source never
  contained, and dropped `{T72}`/`{T73}`. Both arms failed that card. Exactly the class the
  deterministic gate exists for.
* **Billing:** `unknown_gateway` throughout, as authorized. `observed_cost_usd` is 0 because
  there is no observed cash under a Max credit — that 0 is **not** "free".

### Per-call record

| # | arm | key | wall | outcome | model |
|---|---|---|---|---|---|
| 01 | A | SvAsa | 358.9 s | audited ✅ cov 1.0 | attested |
| 02 | B | SvAsa | 454.9 s | audited ✅ cov 1.0 | attested |
| 03 | B | spfS | 169.8 s | audited ✅ cov 1.0 | attested |
| 04 | A | spfS | 416.8 s | audited ✅ cov 1.0 | attested |
| 05 | A | Srama | 300.9 s | `unstructured_result` | attested |
| 06 | B | Srama | 291.5 s | `unstructured_result` | attested |
| 07 | B | samIpa | 141.1 s | `unstructured_result` | attested |
| 08 | A | samIpa | 323.9 s | `unstructured_result` | attested |
| 09 | A | vyavasTA | 342.5 s | `unstructured_result` | **unattested** |
| 10 | B | vyavasTA | 168.9 s | audited ✅ cov 1.0 | attested |
| 11 | B | SudDi | 192.6 s | `unstructured_result` | attested |
| 12 | A | SudDi | 194.7 s | audited ✅ cov 1.0 | attested |
| 13 | A | rAtra | 65.8 s | audit fail cov 0.99 | attested |
| 14 | B | rAtra | 60.2 s | audit fail cov 0.94 | attested |
| 15 | B | zoqaSan | 50.8 s | audited ✅ cov 1.0 | attested |
| 16 | A | zoqaSan | 88.8 s | audited ✅ cov 1.0 | attested |

### Driver defects this run exposed (fix before any larger experiment)

1. **Zero-filled usage passed as present usage** — fixed here.
2. **Envelopes discard the raw result text.** For a content failure the returned string *is*
   the evidence, and only the parse error was kept, so calls 5–8/9/11's actual output is
   unrecoverable. Not fixed here (it would change the envelope schema mid-run).
3. **An absent `returned_model` does not stop the run.** Absence is not substitution, so the
   stop condition reads it as clean; call 09 is a paid, unattested call. It now forces
   INCONCLUSIVE at receipt time, but it should stop at call time.

## Evidence in this directory


| File | What it pins |
|---|---|
| [selection.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/selection.json) | the eight frozen keys, their strata, the metrics, and which stratum predicates fell back |
| `execution_manifest.h2591.json` | the immutable execution manifest; the plan binds its SHA-256 |
| [plan.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/plan.json) | the sealed plan — `plan_sha256` `15f1f3a6db141828…`, both arms' prompt hashes, context hashes, argv hash, the GO rule, and the known non-equivalences |
| [check.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/check.json) | the offline fail-closed report, including the blocked condition |
| `contexts/` | eight sealed `pwg.prep_context.v1` seeds, manifest-sourced |
| `prep/` | the full prep sidecars those contexts were compiled from |
| `call_reservation.json` | the ledger — 16 of 16 spent, all finalized exactly once |
| `envelopes/` | 16 immutable per-call envelopes with usage, timings and audit verdicts |
| [comparison_receipt.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/comparison_receipt.json) | the sealed `pwg.prep_context_comparison.v1` receipt — verdict INCONCLUSIVE |

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

## The billing gate — cleared by human authorization on 12-08-2026

`headless_worker` reads `execution.agent_sdk_credit_claimed` /
`agent_sdk_credit_claim_evidence` from the manifest, and **nothing in the repo ever writes
them**. `gen_opt_harness2` does not emit them; `max_account_orchestrator.profile_status`
calls `telemetry_from_cli_wrapper(max_agent_sdk_credit=True)` with no claim evidence at
all. `usage_accounting.build` then deliberately downgrades the billing mode to
`unknown_gateway` and nulls the list equivalent.

So today **every** Max-route call in this pipeline is accounted as UNKNOWN billing, and
the credit-accounting path added for it is dormant. For H2591 the eighth precondition was cleared by **route (a)** — a human authorized the
spend with billing explicitly classified UNKNOWN. Route (b) remains the better standing
fix and is still open:

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
