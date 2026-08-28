# H3627 — c1 re-ingest windows: cost gate cut 61 → 23, both runs spent, neither delivered a card

_Created: 28-08-2026 · Last updated: 28-08-2026_

Follows the [c1 live gate GO](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3627/H3627_C1_LIVE_GATE_GO_28-08-2026.md).
MG authorised the windows, then authorised "start with 23, after the 38 if needed". Two runs
were made. **Both spent. Neither produced a durable card.** The store is unchanged at
11 462 rows, sha `19fcf5258e5ea384…`.

> **Correction (28-08-2026).** A draft of this file said the first run cost **zero**,
> "verifiable" from the reservation ledger. **That was wrong.** The reader used
> `run['calls']`; the real field is `run['reservations']`. The first run spent **11 calls**.
> The error was mine, not the tooling's — the ledger was correct and complete throughout.
> The false claim was caught before it merged, so no released changelog entry ever carried
> it. See §5.

## 1. The cost gate refuses 38 of the 61 — the window is ~$414, not a rounding error

The gate packet's "spend not evaluable" is true of **actual receipt telemetry**. It does not
mean the work cannot be *projected*: `perf_preflight.py` prices it, and must be run before
any window is called cheap.

| scope | keys | expected calls | projected | per card | `--refuse-over-cost` |
|---|---:|---:|---:|---:|---|
| all 61 | 61 | 898 | **~$414.03** (~219.5 M tok) | ~$6.90 | **FAIL** (exit 1) |
| `cost_partition.run_now` | **23** | 22 | **~$5.08** (~2.7 M tok) | ~$0.23 | **PASS** (exit 0) |
| `cost_partition.defer_monster` | **38** | — | ~$409 balance | — | deferred |

Ceilings are H189: **$2.00/card, $25.00/window**. `/pwg-bounded-run` precondition 2 is
explicit that over-ceiling keys are **deferred, never squeezed in**, so the window was scoped
to the 23 and `--allow-over-cost` was never touched.

The 38 deferred monsters, for whoever budgets them:

```
aDvan aSani BAra Bara bARa Gawa Goza kalaSa maKa manoraTa mAza nIla pAka pariGa parihAra
pAtra pramARa praSna Salya sAmba sAnu satkAra Savas Soza SUla sUri utsAha vAsa vaSA vaSa
vasA vAsin vaSin vaSya vedikA viGna viSAla vitAna
```

## 2. "Queued" was not "runnable" — the 61 had no prepared inputs

The pipeline needs `<safe_name>.raw.txt` + `<safe_name>.portrait.json` per key, and **0 of
61 had them** — not in the canonical `src/pilot/input/` (406 pairs, none ours), not in
`pwg-ru-data/raws` (85 pairs).

The failure mode would have been **silent**: `coordinator.nominal_candidates()` *filters on
both files existing*, so `claim --kind nominal` would have skipped all 61 and claimed
unrelated keys from `assembled_cards.jsonl` order — spending an authorised window on the
wrong work with no error. All 61 *were* present as assembled cards (61/61); only the pilot
inputs had never been generated.

Fixed offline, no model calls: `PWG_INPUT_DIR=<canonical> python src/_pilot_gen_merged.py
<61 keys>` → **61/61 written** (406 → 467 pairs). These are durable and survive the session.

**Names are safe-name encoded, not SLP1** — `aDvan → a_dvan`, `viSAla → vi_s_ala`,
`yAtu → y_atu`, the same convention as the `d_a~~h0_05_anu` subcards.
`window_common.input_paths()` takes the key **verbatim**, so a preflight handed raw SLP1
lemmas reports `missing input for aDvan` while the correctly-named files sit right there.

## 3. Four configuration aborts — `classification: configuration`, none billed

A `configuration` classification is a **provisioning refusal**: no call spawned, nothing
charged.

| refusal | fix |
|---|---|
| `profile-bound manifest v2 production is CLI/headless-only` | `--execution-route=claude-cli-headless`, not `headless_cli` |
| `paid v2 execution requires --preflight` | emit `pwg.performance_preflight.v1` whose `selected_keys` match `manifest.meta.selected_keys` exactly, `cost_gate.over_ceiling: false` |
| `--max-agents=1 starves a 23-key window` | **omit `--max-agents`** so manifest budgets apply |
| `can't open file …\Uprava\src\pilot\headless_worker.py` | wrong cwd — relaunch from the worktree |

**The `--max-agents` one is a defect in the `/pwg-bounded-run` playbook, not a slip.** Its
explicit-manifest line says to drive `headless_worker.py` with
`--only-profile c4 --max-agents 1 --timeout 300`. That is the **canary** shape;
`--max-agents` is a **total spawn ceiling, not concurrency width**, so copying it onto any
multi-key window starves it. The worker refuses by name
(`LAUNCH_FUCKUPS C2_M50_W1_MAX_AGENTS1_2026-07-24`) — the same starvation class CLAUDE.md's
H1618 sync rule exists to prevent. The playbook should mark `--max-agents 1` canary-only.

Set deliberately: **`--budget=1`**, giving 23 cards in 22 single-card batches instead of the
default citation-weighted batching (8 batches of 2–3), because one unevaluable call
otherwise destroys cost attribution for every card in its batch. The `HARNESS OVERSIZE`
warning (539 970 B > 480 000) is the **Workflow `scriptPath`** cap and does not bind the
headless route, which consumes the manifest.

## 4. Run 2 (`…1612Z`): 50 minutes, 20 priced calls, **19 successes, 0 cards kept**

Ran 16:09:31Z → 16:59:29Z, exit 1.

| | |
|---|---|
| batches attempted | **20** (b0–b13 + 2 batch retries + 4 heals) |
| successful calls | **19** |
| terminal failure | `b13` = `_sr_avaka`, `classification: process` |
| CLI terminal reason | **`structured_output_retry_exhausted`** — "Failed to provide valid structured output after 5 attempts" |
| `out.h3627.json` | **never written** |
| cards persisted | **0** |

**The whole window is lost on one bad key.** The worker holds results in memory and writes
`--output` only on clean completion, and no per-batch intermediate is kept anywhere on disk
(checked: nothing under `src/pilot/`, no temp spool). So 19 successful translations —
`_anana`, `anukampA`, `Apta`, `aSru`, `Atura`, `havyavAha`, `hUti`, `jarAyu`, `kAnana`,
`kzuDA`, `menA`, `rAmaWa`, `sattA` — were paid for and discarded. That is an all-or-nothing
failure mode, and it is the single most important fact for sizing any larger window.

`_sr_avaka` failing on structured output is not isolated: it is the same family as the
25-07 gate NO-GO (`representative schema payload did not validate`) and the concurrent
H3361 lane's `vivAda` "spawn-state schema-binding defect (validator rejected all payloads
incl. minimal test)".

Also observed: `kzu_d_a` needed a batch retry plus **four** heal calls (`#g1`, two `g1`
retries, `#g2`), and `men_a` needed a retry — heal thrash is a real cost multiplier, and
`_atura` (the 21 818 B presplit portrait) went through fine.

### Cost: token usage IS evaluable, and the CLI envelope carries real dollars

| field | run 2 total |
|---|---:|
| output tokens | 266 739 |
| **cache-creation tokens** | **600 653** |
| cache-read tokens | 1 754 675 |
| subagent total (legacy misnomer for the sum) | 2 622 153 |
| `priced_calls` / `missing_usage_calls` | 20 / **0** |
| `usage_evaluable` | **true** |
| `cost_evaluable` | false, `observed_cost_usd: 0.0` |

`cost_evaluable: false` is a **pipeline attribution gap, not an absence of price data**. The
failing call's own CLI envelope reports `total_cost_usd: 0.4131022`, itemised
`claude-sonnet-5 $0.4001562` + `claude-haiku-4-5 $0.012946`, with
`cache_creation.ephemeral_1h_input_tokens: 39265`. Scaling that one real data point by the
run's totals (output ≈ 13.8×, cache-creation ≈ 15.3×) puts run 2 at roughly **$5–6** —
which independently corroborates the preflight's ~$5.08 estimate for these 23 keys. The
preflight is trustworthy; it is the *actual-cost plumbing* that is blind.

Cache-creation is the charge that matters (it bills ~20× read), and the `ephemeral_1h`
bucket is what distinguishes "prefix unstable" from "cache expired" — a combined token
total hides both.

## 5. Run 1 (`…1600Z`): the "zero spend" claim was wrong

Launched 15:25Z, killed externally ~15:55Z. Originally recorded here as *"0 call rows … no
call was ever spawned … spend zero, verifiable"*.

**It spent 11 calls** — 6 `headless:translate` (b0–b4 plus a `b3.retry1`) and 5
`headless:heal`, all thrashing on `_atura` (`#g1`, `g1.retry1`, `#g2`, `g2.retry1`, `#g3`).
Usage: output 145 888, cache-creation 369 587, cache-read 952 030, 1 467 549 total;
`finalized_calls` 10, `unevaluable_calls` 10, 1 pending. No cards persisted, same as run 2.

Root cause of the false claim: the analysis script read `run['calls']`, but
`call_reservation.reserve()` writes to `run['reservations']` under a cross-process lock. The
missing key returned an empty list, which was reported as a verified zero. The ledger was
right the whole time; the reader was wrong, and "unevaluable" was additionally collapsed
into "zero" — the exact distinction the gate's rules warn about.

Corollary worth keeping: **the run never "hung" either.** `headless_worker` has a ~12-minute
silent setup before its first spawn and prints nothing during a window; run 1's stdout was
additionally piped through `tail`, which buffers, so 30 minutes of progress was invisible
and lost on the kill. Silence is not evidence of a stall — the reservation ledger is.

## Where this leaves the programme

| thing | state |
|---|---|
| store | **unchanged** — 11 462 rows, sha `19fcf5258e5ea384…` |
| TM mirror | clean, `only_mirror` 0 |
| gate | GO, receipt judged 14:17Z, expires **~20:17Z** |
| 61 prepared inputs | written, durable |
| 23-key manifest + preflight | built, sha `24703b15a6d16f3f…`, reusable |
| **cards delivered** | **0** |
| **calls spent across both runs** | **31** (11 + 20), ~4.1 M tokens, roughly **$8–9** |
| 38 monsters | still deferred, unbudgeted |

**Recommendation before any further spend.** A window that discards 19 paid successes
because the 20th call failed schema validation is not safe to scale. The ~$409 monster lane
carries the same all-or-nothing risk at 45× the cost. Two cheap fixes should land first:
persist per-batch results as they succeed (so a mid-window failure costs one card, not the
window), and treat `structured_output_retry_exhausted` as a park-and-continue rather than a
window-fatal error — `parked_queue` already exists for exactly this shape in
`gen_opt_harness2.py`. Re-running the same 23 keys unchanged would most likely buy the same
outcome.

_Dr. Mārcis Gasūns_
