# Audit — multi-card vs one-card call shape under the c4 ceiling (H2152)

_Created: 02-08-2026 · Last updated: 02-08-2026_

**Model:** Opus 5 1M (`claude-opus-5[1m]`), executing [H2152](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2152-Opus_RussianTranslation_c4-quota-call-shape-audit_02.08.26.md).
Audit only — no bounded window, no store write, no constant moved. **One paid call was made**
(the same-moment route/quota ping in §2), billed at `$0.3456`.

**Parent:** [H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md).
**Evidence base:** [Uprava FINDINGS §266–§270, §273](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) ·
[`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md)
entries of 01-08 and 02-08-2026 ·
[`H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md).

---

## 1. Executive recommendation

| Verdict | Shape | Preconditions |
|---|---|---|
| **HOLD one-card — and stop treating call shape as the lever** | Keep the small shape (`--output-budget=1`), already implemented and already correct. Do **not** flip to batching. | None to keep it. Batching (option B) is gated behind **both** a human ruling on `HARD_TIMEOUT_MS` **and** a measured cut in per-call overhead. |

**The premise this handoff was minted on has expired.** H2152 was written to resolve a tension
between MG's one-card instrument-everything mandate and [§270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)'s
"one item per call is the worst shape under a quota ceiling." That tension is **conditional on
quota binding, and quota does not bind today.** Auth was restored on 01-08-2026, the 02-08 paid
run made 16 calls that all returned or were killed by *our own* ceiling, and a same-moment ping
taken while writing this memo returned a full envelope in 58.8 s (§2). §270's signature — a
silent hang with no return — is absent.

**What binds instead is per-call wall clock against `HARD_TIMEOUT_MS = 180000`**
([`headless_worker.py:45`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L45)),
and the two constraints pull in **opposite** directions. A quota ceiling penalises *many* calls;
a per-call wall-clock ceiling penalises *large* ones. Under the constraint that is actually
binding, the small shape is the right shape — so MG's mandate and §270 are not in conflict at
all right now, and the audit's job is to say so rather than to trade one off against the other.

**But the honest conclusion goes further, and it is the one worth carrying forward: neither
shape fixes the current failure.** The 02-08 run died with heal groups **already at the floor** —
six of `nakzatra`'s eight groups held a *single fragment*, and single-fragment calls still hit
180 s. There is no smaller shape than one. Shrinking cannot rescue a lane whose *fixed* per-call
cost already consumes the budget. So a session that spends itself tuning batch sizes will spend
itself on the wrong variable. The levers that matter are in §6.

> **Folded in after first publication — [PR #986](https://github.com/gasyoun/SanskritLexicography/pull/986), landed the same night.** The 02-08 run's
> "199 370 **subagent** tokens" was a misnomer, not a measurement of subagent scaffolding:
> [`call_reservation.py:92`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py#L92)
> sets `values['subagent_tokens'] = sum(values.values())`, so the field is the **sum of the other
> four token fields** under a legacy name. No subagents are involved. The real composition —
> every call re-creating 56–68 k tokens of **cache** at the premium write rate, ~71 % of its cost —
> is what the misnomer was hiding. **This does not change the recommendation; it sharpens §6
> item 2 from "cut per-call overhead" to a named mechanism, and §2 corroborates it independently.**

---

## 2. Quota state at the time of writing — measured, not assumed

The handoff's protocol step 2 asks for a cheap authenticated probe **outside** the CLI work path
(the one that settled §270 by returning `400`/`429` in ~1 s). **That probe was not available to
this session:** reading the OAuth token out of the profile credential store was refused by the
harness permission classifier. Recorded here so the next session does not burn turns
rediscovering it — either request that permission up front, or use the substitutes below.

Two substitutes were used instead, and between them they answer the question more strongly than
the 429 probe would have:

**(a) Free credential check** — `claude auth status --json` against
`D:\ClaudeTools\profiles\claude4\.claude`: `loggedIn: true`, `authMethod: claude.ai`,
`subscriptionType: max`. Costs nothing, ~1 s. **Trap worth naming: this proves credentials, not
quota.** It returned exactly this on 31-07 while the account was throttled. Never read it as a
quota signal.

**(b) One paid tiny ping**, 02-08-2026, `claude -p --model claude-sonnet-5 --output-format json`,
~30 B prompt, c4 profile:

| field | value | reading |
|---|---|---|
| wall clock | **58 765 ms** | returned; not the §270 hang |
| `duration_api_ms` | **13 110 ms** | route is healthy |
| derived `api_gap_ms` | **45 655 ms** | **78 % of wall is outside the API call** |
| `cache_creation_input_tokens` | **50 450** | payload-independent scaffolding, **one** call |
| `cache_read_input_tokens` | 107 416 | " |
| `input_tokens` / `output_tokens` | 4 / 713 | |
| `total_cost_usd` | **$0.3456** | fixed cost of asking for one word |
| `num_turns` | 5 | see caveat |

**Verdict: NOT rate-limited.** A throttled CLI hangs without returning (§270); this returned a
real envelope with real usage.

**Independent corroboration of the cache-creation finding — this ping prices out exactly.**
[PR #986](https://github.com/gasyoun/SanskritLexicography/pull/986) reproduced a *heal* call's
ledger cost from list rates and found cache creation to be ~71 % of it. The same arithmetic on
this ping — a different call class entirely, a trivial 30 B prompt with no translation work at
all — reproduces the recorded figure to the fourth decimal:

| component | tokens | list rate | cost |
|---|---|---|---|
| cache creation | 50 450 | $6/M | **$0.3027** |
| cache read | 107 416 | $0.30/M | $0.0322 |
| output | 713 | $15/M | $0.0107 |
| input | 4 | $3/M | $0.00001 |
| **total** | | | **$0.3456** vs recorded **$0.3456318** |

**Cache creation is 87.6 % of the cost of asking for one word.** That is the strongest form of
the §4 argument: the dominant per-call charge is *entirely independent of the payload*, so it is
neither a translation cost nor something a smaller shape can avoid — and the ~50 k write also
costs wall clock, which is why it attacks the 180 s wall and the 4.7× cost overrun at once.

**Caveat, stated so the number is not over-read:** the ping ran a plain agentic loop in a repo
cwd, so `num_turns: 5` means the 45.7 s gap includes four inter-turn round trips, not pure
startup. It is an **upper bound** for a multi-turn call, not a clean startup measurement. The
directly comparable figures are the gate's own 01-08 readings on schema-carrying 6 828 B
prompts — `api_gap` **18 266 ms** and **22 779 ms**, i.e. **~45 % of wall is non-API**. The
*token* figures above are payload-independent and need no such discount: **~50 k cache-creation
per single call** is the fixed scaffolding price, whatever the prompt says.

### What of the latency series is contaminated

| Series | Status as *route* evidence |
|---|---|
| 15-07, 16-07, 31-07 readings | **Contaminated** (§270) — taken through a retrying CLI with no same-moment quota check; they measure backoff, not route. |
| The 30 000 → 65 000 ms ceiling raise | **Partly calibrated against backoff.** Not re-derived. [#946](https://github.com/gasyoun/SanskritLexicography/issues/946) / H2138 wants ≥5 paired readings; it stays open. |
| 01-08 readings | **First uncontaminated and first decomposable** — the H2095 `duration_api_ms` instrumentation produced its first rows. n = 1 measured + 1 warm-up. |
| This memo's 02-08 ping | One further uncontaminated point. **Not** a re-derivation; no constant was moved. |

---

## 3. Call-shape inventory — what the code actually does

**Headline: one-card-per-call is not enforced anywhere in code. The production default is
batched, and always has been.** The "one-card lane" is (a) a prose mandate in H2011 and (b) an
existing, already-hardened CLI knob. Nothing has to be built to run it.

| Site | file:line | What it does |
|---|---|---|
| `OUTPUT_BUDGET = 90` | [`gen_opt_harness2.py:102`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L102) | **The default is multi-card.** Batches are sized by citation-weighted output complexity (`1 + <ls>` per card), calibrated 03-07-2026 against byte-mode. |
| batch construction | [`gen_opt_harness2.py:1257`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L1257) | `_group_by_budget` over fallback-having and no-fallback keys separately (collateral-null isolation, 04-07-2026). |
| **the one-card knob** | [`gen_opt_harness2.py:137`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L137) | `--output-budget=1` is named in-code as "the no-PWG single-card lane". **It already exists and has already been debugged.** |
| its companion fix | [`gen_opt_harness2.py:134`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L134), predicate at [`:559`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L559) | `PRESPLIT_SOLO_CITE_FLOOR = 40` exists **solely** so `--output-budget=1` does not degenerate — at budget 1 every citation-bearing card would otherwise be force-routed into the heal lane (H255/H823). |
| `SELFHEAL_GROUP_BUDGET = 12` | [`gen_opt_harness2.py:61`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L61) | Fragments are grouped; the JS heal issues **one call per group**. This is a second, independent batching axis. |
| `MAX_WIDE = 3` | [`gen_opt_harness2.py:223`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L223) | Concurrency, not batch size — bounded dispatch is the default since H1283 (non-null ~10 % → ~78 % on a degraded transport). Orthogonal to shape; do not conflate. |
| prompt assembly | [`headless_worker.py:196`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L196) → [`:201`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L201) | `build_prompt` concatenates one `card_block` **per key in the group** — the shape is entirely a property of the manifest's `batches`, not of the worker. |
| dispatch | [`headless_worker.py:1014`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L1014) | `run_all` iterates `manifest['batches']`, one `resolve_group` call per batch, then `presplit_keys` one at a time. |
| the hard ceiling | [`headless_worker.py:45`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L45) | `HARD_TIMEOUT_MS = 180000`, carrying the standing in-code ruling `"NOTHING runs past 3 min (MG)"` (R4/C-15). |
| manifest guard | [`execution_contract.py:60`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py#L60) | P-1: no key in `batches`/`presplit_keys` may fall outside `selected_keys`, else it is billed silently. |

**What would have to change to run one card per call: nothing.** `--output-budget=1` plus the
existing solo-cite floor is the lane. That materially cheapens the option — the decision is a
run-time flag, not an engineering project.

---

## 4. Options A / B / C, priced on this pipeline

Fixed per-call overhead, measured (§2): **~50 k cache-creation tokens · ~$0.35 · ~18–46 s of
non-API wall**, independent of payload. Against a 180 s ceiling that is **~10–26 % of the budget
spent before any translation happens**, and it is paid once per *call*, not per *card*.

| Option | Attribution | Quota load | Wall-clock load | Viable today? |
|---|---|---|---|---|
| **A. One card per call** (`--output-budget=1`) | **Observed** per card — satisfies MG's mandate exactly | Worst: maximises call count | **Best**: each card gets the full residual budget | **Yes** — and it is the only shape whose failures are attributable to their own content |
| **B. Multi-card batch** (`OUTPUT_BUDGET=90`, today's default) | **Derived** — arithmetic over the batch | Best: amortises the ~50 k scaffolding over N cards | **Worst**: per-call work grows with N against a fixed ceiling | **No.** The 02-08 run shows the margin already gone at current sizes: successes ran 120.4 → 132.0 → 134.5 → **164.3 s**, i.e. 67 % → **91 %** of budget. Any call above the median dies. |
| **C. Hybrid** (one-card sample + batched bulk) | Mixed | Middle | Middle | **No** — its bulk half *is* option B, which is what is failing. Hybrid is the right answer only once B is unblocked. |

### The attribution argument against B is stronger than H2011 recorded

H2011 noted that batching makes per-card cost arithmetic rather than observed. There is a
sharper, unrecorded consequence in the ledger's own contract:
[`call_reservation.py:378`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py#L378)
propagates `cost_evaluable=False` from any single call to the whole usage record, and
[`:69`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py#L69)
`unevaluable_telemetry()` carries no duration at all. So under a batch of N, **one unevaluable
call destroys the cost attribution of all N cards in it**, not one. At the 02-08 run's rate — 12
of 16 calls unevaluable — batching does not merely derive attribution instead of observing it;
it *amplifies* attribution loss by the batch factor. That is a first-class argument for A under
the instrument-everything mandate, independent of the wall-clock argument.

### A correction to a premise this handoff inherited

H2152's own scope section, and H2011 before it, price the scaffolding at "~90 k cache-creation
per call". **That is a two-call aggregate.**
[`perf_preflight.py:55–67`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py#L55)
already carries the correction in-code (~45 243 per call), and this memo's single-call ping
independently measures **50 450**. The per-call figure is therefore ~45–50 k, not ~90 k — the
amortisation prize from batching is **half** what the handoff assumed. `$0.29/call` survives
intact ($0.5848 / 2); this ping's $0.3456 is the same order.

---

## 5. Quota-first gate design — the data source already exists and is being discarded

The handoff asks for a cheap authenticated probe wired into `/pwg-live-gate` so a 429 is never
reclassified as latency. The important finding is that **a new probe is the second-best answer.**

[§273](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) established that the rate-limit
text *does* reach the parent process and is then thrown away one layer below the handlers blamed
for losing it:
[`proc_tree.py:270`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py#L270)
drains the killed CLI's stdout/stderr into locals after `terminate_tree`, then bare-`raise`s the
original `TimeoutExpired` attaching only `cleanup_trouble`. `headless_worker`'s
`RATE_RE = re.compile(r'429|rate.?limit|usage limit|too many requests')`
([`headless_worker.py:35`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L35))
is therefore matched against an empty string on exactly the calls that need it.

**So the cheapest quota classifier is not a probe at all — it is attaching the already-drained
output to the exception.** It costs zero paid calls, needs no credential access (which this
session could not obtain anyway), and converts every future timeout into a classified one
retrospectively. Design deltas, in order of value:

1. **Attach the drained streams** at `proc_tree.py:270` so `RATE_RE`/`AUTH_RE`/`CONN_RE` see the
   text on the timeout path. Highest value, smallest diff, already an open `[integrity]` issue.
2. **Gate on `duration_api_ms`, not wall clock.** The envelope has carried it since H2095;
   `api_gap_ms` should get its **own** budget rather than silently consuming the route ceiling.
   This is the structural fix for the §267/§270 conflation — a threshold on the outer number
   encodes machine load and CLI scaffolding into what is supposed to be a route measurement.
   Note `STRICT_CEILING_MS` already derives from the orchestrator constant
   ([`h963_c4_gate0_probe.py:125`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py#L125),
   [`coordinator.py:71`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py#L71),
   [`max_account_orchestrator.py:1113`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py#L1113)),
   so a second ceiling would follow the same one-source-of-truth pattern.
3. **Classify three outcomes, never two.** The gate currently reasons about `success` vs
   `timeout`. There are three: route-slow, quota-throttled (hang, no return), and
   **killed-by-our-own-ceiling** — which is what the 02-08 run actually was, and which no
   artifact distinguished until `reservation_timeline.py` differenced the stamps.
4. **Never treat `auth status` as a quota signal** (§2a). Cheap and free, but it was green during
   the 31-07 throttle.
5. **Persist the raw event rows.** `src/pilot/output/h963_c4_gate0_probe_events.jsonl` is
   gitignored (`.gitignore:67`), so every gate series dies with its worktree and the committed
   table is the only copy — the durability gap that made the whole pre-H2095 series
   undecomposable.

---

## 6. Ordered backlog — the levers that are actually load-bearing

1. **Human ruling on `HARD_TIMEOUT_MS`** (§7). Nothing downstream can be planned around a
   3-minute wall that single-fragment calls already exceed. **Blocking.**
2. **Stop re-creating the cache on every call.** This is the sharpened form of "cut per-call
   overhead", and after [PR #986](https://github.com/gasyoun/SanskritLexicography/pull/986) it has
   a named mechanism: the framework prompt is written to cache **on each invocation** instead of
   being amortised across them — 56–68 k tokens at the premium write rate on a heal call, 50 450
   on this memo's trivial ping, while reads sit at only ~35.6 k. That single quantity is **71 %
   of a heal call's cost and 87.6 % of the ping's**, and it makes *both* shapes fail: it is what
   batching exists to amortise and what one-card pays per card. Because writing ~60 k tokens also
   costs wall clock, it is the one lever that attacks the 4.7× cost overrun **and** the 180 s wall
   **without** touching the "NOTHING runs past 3 min (MG)" ruling. Stated there as a hypothesis
   and still untested: either the cache prefix is not stable across `claude -p` invocations, or
   the TTL lapses between 2–3-minute calls. **Testing that is the highest-value next experiment in
   this whole arc** — and it is cheap.
3. **Attach drained output on the timeout path** (§5.1) — zero-cost, unblocks quota
   classification permanently.
4. **Fix cost-unevaluable accounting** ([#949](https://github.com/gasyoun/SanskritLexicography/issues/949)).
   While 75 % of calls report `$0` for real spend, no call-shape decision has trustworthy cost
   data underneath it, and `perf_preflight`'s `PER_AGENT_USD_HEALTHY = 0.113`
   ([`perf_preflight.py:69`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py#L69))
   remains 4.7× under the measured ~$0.53.
5. **Split the gate's route and overhead budgets** (§5.2).
6. **Then, and only then, revisit B/C.** With overhead cut and a ruled ceiling, hybrid becomes
   the natural end state: a one-card instrumented sample for per-card truth, batched bulk for the
   remaining ~140 000 words.

**Non-goals, restated:** no ceiling raise, no re-run of the §268 exclusion ladder, no process
cleanup as a "fix" (refuted, §267 addendum), no foreign-route work (H909), no `/pwg-drain` or
multi-root paid window, and no production batch-size flip.

---

## 7. Open question for a human — one, and it is genuinely a decision

`HARD_TIMEOUT_MS = 180000` carries the explicit standing ruling `"NOTHING runs past 3 min (MG)"`.
The 02-08 run shows that a **single fragment** — the smallest unit the pipeline can produce —
does not reliably finish inside it. Three mutually exclusive resolutions, all human:

- **Relax the 3-minute ruling** to a measured ceiling. Cheapest to execute, and the one this
  memo will not take on its own authority: raising a threshold so work fits it is the
  weaken-a-guard-to-pass-a-gate move the whole H2011 arc exists to refuse.
- **Cut the per-call overhead first** and keep 3 minutes. Correct but slower; item 2 above.
- **Accept partial cards** — let a call return what it finished at the ceiling. Changes the
  quality contract, not just the schedule.

Until one is chosen, the call-shape question is decided but inert: **A is the right shape, and
the lane still cannot finish.**

---

## 8. Definition of done for this audit

| Required | Where |
|---|---|
| Memo + recommendation | this file, §1 |
| Inventory with file:line | §3 |
| Quota-aware gate design | §5 |
| Contamination statement | §2 |
| Measured same-moment quota reading | §2b, mirrored to [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md) |
| Cross-link from H2011 | H2011 status block, updated in the same pass |

Zero windows opened, zero store writes, zero constants moved, one paid call ($0.3456).

---

_Dr. Mārcis Gasūns_
