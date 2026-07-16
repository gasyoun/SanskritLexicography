# H963 — c4 five-hour correction-evidence campaign (offline)

_Created: 16-07-2026 · Last updated: 16-07-2026_

**Executor:** Opus 4.8 (`claude-opus-4-8[1m]`) orchestrating; census/analysis agents on the session model.
**Worktree:** [`SanskritLexicography-h963-c4-live/RussianTranslation`](https://github.com/gasyoun/SanskritLexicography/tree/h963-c4-live-rung3/RussianTranslation), branch `h963-c4-live-rung3`, clean.
**Brief:** `H963_C4_FIVE_HOUR_CORRECTION_EVIDENCE_CAMPAIGN.md` (untracked, GitHub root), 12:33 MSK 16-07-2026.
**Companion artifacts:** [`campaign_journal.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/campaign_journal.md) · [`campaign_windows.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/campaign_windows.jsonl) · [`campaign_cards.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/campaign_cards.jsonl) · [`candidate_selection.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/candidate_selection.jsonl)

---

## 1. Executive result

**This campaign fired ZERO live generation calls.** Not one Workflow call, one `agent()` call, or one `claude` invocation was made. Every number below is either read from a committed artifact of an earlier run or computed offline from committed constants. Nothing was written to the canonical store, the TM, or any tracked pipeline file by this pass.

**Why zero.** Two independent reasons, each sufficient on its own:

1. **This session is not the c4 session, and cannot become it.** The brief mandates `c4 only` via `D:\ClaudeTools\profiles\claude4\.claude`. This session's `CLAUDE_CONFIG_DIR` is **unset**, so it runs the default profile `C:\Users\user\.claude`. Workflow subagents inherit the orchestrating session's credentials, so "c4 only" is **unenforceable from here** and every call fired would authenticate and bill as the wrong account — mis-attributed provenance, which is the brief's own **"manifest provenance fails"** hard stop.
2. **Two of the brief's own hard stop conditions were already tripped** by the owner-override pilot it instructed us to close first. That pilot's real call **exceeded the 180,000 ms kill ceiling**, and its two manifests **were launched concurrently by mistake**. The brief's instruction on either condition is: stop all further live calls and spend the remainder on the offline audit. That is exactly what was done.

**What WAS produced.** A committed offline evidence packet: an append-only campaign journal, a pre-registered 8-cell window ledger with every cell marked `NOT_RUN` and its reason, a per-card ledger, a 114-head candidate census with an offline kill-gate deliverability classification, and the ten analysis answers reproduced in §6. The campaign's headline finding (C-01) is offline arithmetic on committed constants: **the 180 s kill ceiling stopped scaling with the work, and at that ceiling 46–66% of the runnable nominal universe is undeliverable on ANY route, healthy or degraded.**

**What this does NOT establish.**

- **H963 is NOT PASS.** Production readiness is **not** established by this pass and was not moved one step closer to established.
- **The historical c4 NO-GO stands, unreinterpreted.** Gate-0 (16-07-2026): warm-up 53,290 ms, measured 104,870 ms, 0 connection errors, on a **6,828 B trivial probe** against a **30,000 ms** ceiling — 1.78× and 3.50× over. NO-GO.
- **The pilot's concurrency deviation is PRESERVED as recorded**, never softened.
- **H255 / no-PWG stays FROZEN.** The canonical store is unchanged: **11,605 rows** before and after, sha256 `cc1d544ed92d201ca8cbecde0b5e9a8191994dfd1baf20841da82f1f9ae7c805`.
- **The offline audit is NOT a substitute for the unrun live matrix.** §8 lists, plainly, which of the brief's questions remain unanswered for want of serial live data.

---

## 2. The escalation chain

Four briefs, each authored after a measured failure, each overriding the stop condition the prior one had set. Presented factually; no judgment is offered on the chain itself.

| # | Brief | Time (MSK, 16-07-2026) | Prior stop condition it overrode | What it authorised |
|---|---|---|---|---|
| 1 | `H963_OPUS_STATUS_CORRECTION` | 09:19 | — (entry point) | Correct the recorded H963 status; establish the true state of the rung. |
| 2 | `H963_C4_LIVE_RESUME` | 10:41 | The standing latency NO-GO barring live launches | Resume live c4 work notwithstanding the NO-GO. |
| 3 | `H963_C4_OWNER_OVERRIDE_PRODUCTION` | 11:14 | The Gate-0 health gate (30 s ceiling), measured NO-GO at 104,870 ms | Owner override: launch the production pilot on a route that had failed the health gate. |
| 4 | `H963_C4_FIVE_HOUR_CORRECTION_EVIDENCE_CAMPAIGN` | 12:33 | The pilot's outcome (0/2 clean, 1 kill-timeout at the ceiling, recorded concurrency deviation) | A five-hour campaign: close the pilot, then run a pre-registered 8-cell live matrix; with an explicit hard-stop clause returning to the offline audit if a call exceeds the kill ceiling or calls overlap. |

Brief 4's own hard-stop clause was already satisfied by brief 3's outcome at the moment brief 4 was written. This campaign executed the clause as written: offline audit only.

---

## 3. The pre-registered live matrix — PLANNED, NOT RUN

Reproduced verbatim from [`campaign_windows.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/campaign_windows.jsonl) rows 3–10. **This is honest reporting of a plan, not a result.** Every cell is `status: NOT_RUN`; every telemetry field is `null` by construction, never zero.

| Cell | Stratum | Planned shape | Heads | Purpose | Status | Reason |
|---|---|---|---|---|---|---|
| 1 | tiny-A | smallest eligible, raw <6 KiB, low sense/citation | 2 | serial tiny baseline | **NOT RUN** | wrong profile → provenance fails; brief's hard stops already tripped; C-01 predicts nulls |
| 2 | tiny-B | same stratum, disjoint keys | 4 | batching effect at tiny complexity | **NOT RUN** | ditto |
| 3 | typical-A | eligible mid-shape, roughly 6–12 KiB | 2 | typical serial baseline | **NOT RUN** | ditto |
| 4 | typical-B | same stratum, disjoint keys | 4 | batching effect at typical complexity | **NOT RUN** | ditto |
| 5 | upper-normal-A | largest still `run-now-low`, no presplit/monster | 1 | upper-normal single-card | **NOT RUN** | ditto |
| 6 | upper-normal-B | same stratum, disjoint keys | 2 | upper-normal batching effect | **NOT RUN** | ditto |
| 7 | restoration-target | record grammar and/or multiple `{Tn}` masked tokens | 2 | token-restoration evidence | **NOT RUN** | ditto |
| 8 | end control | natural schema-carrying D-K prompt or clean synthetic control | 1 | within-session latency drift | **NOT RUN** | ditto |

**Cells run: 0 of 8. Live calls fired: 0. Keys selected: none — selection never ran.**

The ledger's own `not_run_reason` field carries the three-part reason on every row; the third part (finding C-01) is a *prediction*, and the first two are the sufficient causes.

---

## 4. Why the matrix would likely have produced nulls — **a PREDICTION, not a measurement**

Explicitly labelled: **this section is a prediction with a stated basis. Nothing in it was measured this campaign.** It is not offered as a substitute for the missing data, only as the reason the missing data would probably have been null.

The measured anchors:

| Observation | Payload | Outcome |
|---|---|---|
| Gate-0 measured probe (16-07) | **6,828 B** trivial probe | **104,870 ms** — 3.50× the 30 s ceiling, 0 conn errors |
| Pilot real call (16-07) | **5,606 B** masked skeleton | **no return at 180,000 ms** — kill-timeout |

The matrix asks cells 3–4 for "roughly 6–12 KiB typical" cards and cells 5–6 for the "largest still `run-now-low`" card. The nominal-core runnable pool (282 lemmas, 114 with prebuilt inputs) has a **raw median of 12,556 B** — i.e. **larger than the 5,606 B skeleton that already timed out**, and roughly double the 6,828 B trivial probe that took 104,870 ms.

The mechanical basis (offline, from committed constants — `KILL_FACTOR=2.0`, `KILL_BASE_MS=20000`, `KILL_SLOPE_MS=45`, `KILL_FLOOR_MS=45000`, `KILL_CEIL_MS=180000`):

> `killBudgetMs(S) = min(180000, max(45000, 2.0 × (20000 + 45 × S)))`
>
> The `180000` clamp binds for every `S ≥ 1,556 B`. Every real nominal head is past that point. So the **work sums, the budget does not move.** For the pilot's real batch: expected `20000 + 45 × 5606 = 272,270 ms`, granted `180,000 ms` — **0.66×**, reproducing the ledger's recorded `kill_budget_vs_expected: 0.66` to the digit.

**Predicted cell outcomes** (from [`campaign_windows.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/campaign_windows.jsonl) `predicted_outcome_if_run`, reproduced verbatim): tiny strata (cells 1–2) SAFE..COIN-FLIP; typical (3–4) COIN-FLIP..DOOMED; upper-normal (5–6) DOOMED at the centre rate. **PREDICTION from finding C-01, NOT a measurement.**

Two caveats that weaken the prediction and must travel with it: it rests on a skel/raw ratio band measured on **n=2 keys** (0.537 `zaz`, 0.750 `upama`) — the campaign journal names this its weakest link — and on a rate band from a single benchmark whose largest skeleton was **2,929 B**, roughly half the pilot's real batch. The prediction extrapolates beyond its fitted range in both directions.

---

## 5. Historical Block 0 — the pilot's two calls

Reported **with** the concurrency caveat, which is not detachable from the numbers.

> **⚠️ RECORDED PROTOCOL DEVIATION.** The two manifests were launched **concurrently by mistake** — the owner brief required serial. `max_wide=1` is a within-manifest dispatch cap and does **not** serialise two separately-launched manifests. The wall-clock figures below are **overlapping, not serial**. They are **NOT serial c4 throughput or economy evidence and must not be quoted as such.**

| Run | Keys | Skel B | Wall | Cards | clean | null | Classification | Subagent tokens |
|---|---|---|---|---|---|---|---|---|
| `h963_c4_canary` | `dq_canary_puregloss` (synthetic) | 2,046 | ~118 s | 1 | **1** | 0 | success | **59,250** |
| `h963_c4_real` | `zaz`, `upama` | **5,606** | ~206 s | 2 | **0** | **2** | **kill-timeout** @ 180,000 ms | **null** — killed before return |

**Verdict: GENERATED, NOT PROMOTED.** Real clean rate 0% vs an 80% floor. The canary's 1/1 is categorically unpromotable (synthetic, never promotable by policy) — the one clean card in the pilot is the one card that can never be promoted.

**Store verified unchanged:** 11,605 rows before and after; sha256 `cc1d544ed92d201ca8cbecde0b5e9a8191994dfd1baf20841da82f1f9ae7c805` on both sides; mtime unchanged.

The canary's `subagent_tokens: 59,250` is n=1, synthetic, measured under concurrent self-load, and the model **recognised the card as a test** in its own notes — biasing representativeness in the direction that flatters the result. The real lane's recorded `subagent_tokens: 0` means **killed before return** — a non-observation, not a measurement of zero. Real-lane spend is **null, unrecoverable from this run**.

---

## 6. Latency / token / quality / cost findings

Ten analysis questions, answered offline against committed artifacts. Each answer's full evidence chain is in the companion artifacts; the load-bearing numbers are reproduced here.

### 6.1 Q1 — Fixed overhead vs bytes, senses, citations, batch size

**PARTIALLY ANSWERABLE. Headline is a clean null: with output held constant, input bytes explain ~0% of wall time.** The decomposition into a *fixed* overhead term is **not identified**, because the term that should be fixed is not fixed — it swings 5.9× at identical work, and the largest single driver in the data is **the calendar date**, not any property of the card.

The only dataset sweeping input size with output pinned — `src/pilot/h898_sweep.jsonl`, n=15, 5 sizes × 3 reps, 14-07-2026, all 15 calls returning 1,480–1,504 B:

| total input B | n | min ms | median ms | max ms | max/min | median output B |
|---|---|---|---|---|---|---|
| 93 | 3 | 28,041 | 37,369 | 52,800 | 1.88× | 1,495 |
| 1,033 | 3 | 10,093 | 21,211 | 40,735 | 4.04× | 1,491 |
| 2,533 | 3 | 20,162 | 36,569 | 59,206 | 2.94× | 1,491 |
| 5,033 | 3 | 19,258 | 27,636 | 30,342 | 1.58× | 1,483 |
| 6,554 | 3 | 15,443 | 25,769 | 52,759 | 3.42× | 1,485 |

One-way ANOVA on size (computed from the 15 raw rows): between-size SS 606,580,946 (**20.4%**), within-size SS 2,371,953,351 (**79.6%**). `F(4,10) = 0.639` vs critical 3.48 at α=0.05 → **not significant**. `η² = 0.204` but **`ω² = −0.106`** — the bias-corrected estimate is negative, i.e. **the best estimate of the true byte effect is zero**. Pearson `r = −0.141`; permutation test N=200,000, two-sided **p = 0.614**. OLS slope is **negative** (−0.82 ms/B). A **70× span** in input bytes produces no detectable latency signal.

**The "25 ms/skel-byte" rate is not a byte cost.** The competing 04-07-2026 benchmark (n=6 batch calls) fits `wall_ms = −11,819 + 32.33 × skel_B`, r² = 0.878 — **and refutes itself: the intercept is −11.8 s.** A negative fixed overhead is physically impossible, so the model is misspecified. All six leave-one-out jackknife intercepts are negative, so the impossibility is not one outlier. The reconciliation is in the design doc's own words: *"output volume, not citation count, is what takes time."* In the benchmark, skel bytes covary with output volume; in the sweep, output is pinned. **The 25–44 ms/skel-B rate is an output-generation rate wearing an input-byte label.**

| predictor | r | r² | note |
|---|---|---|---|
| skel bytes | +0.937 | 0.878 | proxy for output volume, not input cost |
| cards in call | +0.856 | 0.733 | **collinear with skel bytes (r=+0.764)** — not separable at n=6 |
| Σ `<ls>` citations | +0.549 | 0.301 | confounded; `pari` at 86 `<ls>` ran in 32.5 s, *faster* than an 11-card batch at 62 `<ls>` / 83.8 s |
| Σ senses | +0.109 | **0.012** | essentially nothing |

**The actual dominant term is the date.** Sweep @6,554 B (14-07): 15,443 / **25,769** / 52,759 ms. Gate-0 @6,828 B (16-07): **104,870 ms**. **+4% bytes → +307% latency** — 4.07× the sweep median, 1.99× the sweep's own maximum, same model, same trivial output. Three independent verbatim corroborations of payload-independence exist in `LAUNCH_FUCKUPS.md` (`:409` *"call latency is independent of payload size"*; `:383` an 11-byte fragment killed at the 45 s floor; `:436` *"ceiling timeouts independent of payload size"*).

| component | share of wall time | basis |
|---|---|---|
| input raw bytes | **~0%** (ω² < 0, p=0.61) | n=15, output pinned |
| senses | ~1% (r²=0.012) | n=6, confounded |
| citations | ≤30% (r²=0.301), contradicted by `pari` | n=6 |
| batch size | **not separable** from skel bytes (r=0.764) | n=6 |
| fixed per-agent overhead | **≤10.1 s** (lowest wall ever observed) | n=15 |
| **time-varying route/queueing** | **the remainder — the largest term** | 5.87× spread at identical work; 4.07× across 2 days |

**"Fixed overhead" is the wrong frame.** What looks like a large fixed cost is a large *stochastic* cost.

### 6.2 Q2 — Does batching improve cards-per-agent without more semantic defects?

**UNANSWERABLE as a measurement — the exact experiment was pre-registered (cells 1–4) and never run.** But the *mechanism* is deterministic and points opposite the question's premise: **under the current kill gate, batching cannot improve cards-per-agent, because the batch dies.**

The only live batch evidence is n=1 and it overlapped a second call:

| run | heads | Σ skel B | cards | clean | null | realised cards/agent | semantic defects |
|---|---|---|---|---|---|---|---|
| `h963_c4_canary` | 1 (synthetic) | 2,046 | 1 | 1 | 0 | **1.0** | 0 FP (n=1, model knew it was a canary) |
| `h963_c4_real` | **2** | 5,606 | 2 | 0 | 2 | **0.0** | **null — NOT zero** |

The defect half is **strictly unmeasurable**: both real cards record `"unmeasurable_reason": "no output produced; every quality metric is null, NEVER zero"`.

**Batching is free work at zero extra budget.** From the generated harness: `skelBytesOfKeys` **sums** skeletons; `killBudgetForCur` grants a *single-card* call the full `KILL_CEIL_MS` unconditionally; and the ceiling clamp binds at `S ≥ 1,556 B`, which every real head exceeds.

| stratum | heads | Σ skel B | budget ms | harness's OWN expected ms | budget/expected | band @25–44 ms/B |
|---|---|---|---|---|---|---|
| tiny (`zaz` 2,046) | 1 | 2,046 | 180,000 | 112,070 | **1.61×** | SAFE |
| tiny | **2** | 4,092 | 180,000 | 204,140 | **0.88×** | COIN-FLIP |
| tiny | **4** | 8,184 | 180,000 | 388,280 | **0.46×** | **DOOMED** |
| typical (skel ~8,224) | 1 | 8,224 | 180,000 | 390,080 | **0.46×** | **DOOMED** |
| typical | **2** | 16,448 | 180,000 | 760,160 | **0.24×** | **DOOMED** |
| typical | **4** | 32,896 | 180,000 | 1,500,320 | **0.12×** | **DOOMED** |

The mechanism reproduces the pilot's telemetry exactly (`zaz`+`upama` → 0.66×), which is what makes it trustworthy. **Batching is strictly dominated:** run solo, those two heads get 1.61× and 1.00×; batched, a joint **0.66×** — the harness killed the call at **66% of the time its own model says the work needs**, violating its own stated design invariant that *"no legit call (even a +50% variance one) is ever killed."*

**Projected answer: batching 4 tiny or 2 typical heads does not raise cards-per-agent — it drives it toward 0**, and makes the defect question permanently unmeasurable. **This is a PREDICTION** from an n=2 ratio band and an n=13 rate band whose largest skeleton was 2,929 B.

One near-miss that must not be misread: `no_pwg_w08` (1/21 non-null at ~10-wide) vs `no_pwg_w08_rq1` (14/18 at `--max-wide=3`) varies **concurrency width**, not cards-per-agent, and is selection-confounded (rq1 ran w08's hard residual keys; 8 of its 14 non-null were content-defective → only 6 clean). Not batch-size evidence.

### 6.3 Q3 — Which input feature best predicts latency, tokens, audit failure, SANLOSS?

**Split verdict: ANSWERABLE for latency (from an n=7 historical benchmark). UNANSWERABLE for token use, audit failure, and SANLOSS.**

**(a) Latency — winner: `skel_bytes`.** From the 04-07-2026 `tyaj` benchmark (13 agent calls; **7** with both skel-byte and wall-clock):

| feature | Pearson r (n=7) | Spearman ρ (n=7) | 95% CI (Pearson) | Pearson r, batch-only (n=6) |
|---|---|---|---|---|
| **`skel_bytes`** | **0.858** | **0.883** | **[0.30, 0.98]** | **0.937** |
| `card_count` | 0.856 | 0.638 | [0.15, 0.98] | 0.856 |
| `Σ <ls>` | 0.468 | 0.519 | [−0.44, 0.90] | 0.549 |
| `Σ senses` | 0.142 | 0.091 | [−0.68, 0.81] | 0.109 |

OLS on all 7: `wall_ms = −3,668 + 29.41 × skelB`, R² = 0.737. Per-call rate mean 26.6, median 24.2, sd 9.6, min 16.8, max 44.0 ms/skel-B — consistent with the doc's own "centre ≈ 25, ceiling ≈ 44". Two hard caveats: at n=7 every CI is very wide and `card_count` is statistically indistinguishable from `skel_bytes`; and the benchmark's largest skeleton was **2,929 B** while the pilot's real call was **5,606 B**, i.e. **1.9× outside the fitted range**. Extrapolating gives 165 s (OLS centre) to 247 s (observed-max rate) against a 180 s ceiling — the straddle that is exactly the COIN-FLIP verdict.

**(b) Feature collinearity (n=114, features only, no outcomes)** — Spearman ρ over the candidate census:

| | raw_bytes | senses | ls_count | sa_spans | band | rank_score |
|---|---|---|---|---|---|---|
| **raw_bytes** | 1.000 | 0.433 | **0.863** | **0.851** | 0.413 | 0.759 |
| source_sense_count | 0.433 | 1.000 | 0.461 | 0.461 | 0.255 | 0.408 |
| ls_citation_count | 0.863 | 0.461 | 1.000 | 0.858 | 0.313 | 0.725 |
| sanskrit_spans | 0.851 | 0.461 | 0.858 | 1.000 | 0.389 | 0.789 |
| band | 0.413 | 0.255 | 0.313 | — | 1.000 | 0.770 |
| worklist_rank_score | 0.759 | 0.408 | 0.725 | 0.789 | 0.770 | 1.000 |

`raw_bytes`, `ls_citation_count` and `sanskrit_spans` are mutually collinear (ρ 0.85–0.86); `raw_bytes` is a sufficient proxy for all three; `sense_count` is the odd one out. Note ρ(raw_bytes, worklist_rank_score) = **0.759**: **scholarly priority is positively correlated with size**, hence anti-correlated with deliverability.

**The weakest link:** `skel_bytes` — the predictor that works — is **not in the candidate scan**. It must be projected from `raw_bytes` through a skel/raw ratio measured on **n=2 keys** (0.537, 0.750). That band is the dominant uncertainty in every downstream deliverability number.

**(c) Token use — UNANSWERABLE (n=1 agent).** Canary 59,250 (synthetic, model knew); real **0 = killed before return**, not a measurement; input / cache_read / cache_create all **null** — *"not recorded by the harness; not recoverable post-hoc"*. The billing-relevant *split* (cache-read is ~10× cheaper than fresh input) is null by telemetry gap.

**(d) Audit failure — UNANSWERABLE (0 real cards).** No outcome variable exists. What is known is mechanical, not statistical: the failure was fully determined by `skel_bytes` via the kill gate — by construction, not by fit, at n=1.

**(e) SANLOSS — UNANSWERABLE for the rate that matters.** Across all 3 cards: `sanloss_shortfalls=0`, `sanloss_detail=[]`, `tnmask_mismatches=0`. Zero events ⇒ zero variance ⇒ no feature rankable. Per finding C-03: true-positive sensitivity is already proven offline by fixtures (for the modelled drop shapes only); the **false-positive rate on real output is genuinely unmeasured** and needs clean real cards, which the 180 s ceiling prevents from existing.

**(f) Features untestable at all — null with reason.** `masked_token_count`, `record_grammar_token_count`, `fragment_presplit_count`: **0/114 non-null** — *"not emitted by candidate_scan.json schema v1; would need a re-scan"*. These are precisely what a TNMASK-restoration predictor would need.

### 6.4 Q4 — Does the 30 s health threshold predict card success?

**The 30 s threshold is a throughput/cost policy, not a card-success predictor — and it says so in its own defining comment.** No policy was changed by this pass.

| Threshold | Canonical definition | Enforcement |
|---|---|---|
| **30 s health gate** | `max_account_orchestrator.py:491` — `PROBE_LATENCY_CEILING_MS = 30000` | `probe_log.py:76-77`; also declared `probe_log.py:39`, `h963_c4_gate0_probe.py:56`, `latency_sweep_analyze.py:25` |
| **90 s schema precedent** | **PROSE ONLY — no code constant exists.** `Uprava/SERVER_OUTAGES.md:29` (682,753 ms = "~7.6× the 90 s schema-carrying ceiling"; 682753/90000 = 7.586 ✓) | **NONE.** `grep -rn "90000\|90_000"` over `src/`, `pwg_ru/`, `*.md` returns **zero** hits |
| **180 s kill ceiling** | `gen_opt_harness2.py:183` — `KILL_CEIL_MS = 180000` ("Was 480000") | `gen_opt_harness2.py:1469`, called `:1856`; asserted `window_selftest.py:4057-4058`. **Design doc still says 480000** at `FAILURE_MODES_AND_KILL_GATE_2026-07-04.md:150` — live doc/code drift on a load-bearing constant |

**Reconciliation finding:** `SERVER_OUTAGES.md:29` states the `probe_log.py` gate owns the gating, but `probe_log.py` enforces **only** 30 s, for every prompt shape. There is no schema-mode branch. **The 90 s schema-carrying ceiling is an unimplemented prose convention.** This is a finding, not a recommendation.

**The three numbers are not commensurable.** 30 s probes an **inert filler** payload with a trivial `{"ok": boolean}` schema; a real card does full DE→RU translation. The repo's own measured healthy baseline for a real schema card is **~55–105 s** — *entirely above the gate*. A perfectly healthy card is 1.8×–3.5× the gate. Read as three different objects they are consistent: 30 s = *is the route responding at baseline on near-zero work* · ~90 s = *what a real card legitimately costs* · 180 s = *when to abandon a call*.

**Measured joint distribution — GO arm, n=9 windows / 192 cards:**

| run_id | window | gate reading | cards | clean | rate |
|---|---|---|---|---|---|
| `wf_33290004-c35` | h317_w1b | 3,269 ms GO | 12 | 0 | **0.0%** |
| `wf_a2b29683-835` | no_pwg_w03 | 21,180 ms GO | 27 | 11 | 40.7% |
| `wf_5ed6f8e0-b0b` | no_pwg_w07 | 53,956 ms → GO (**override**) | 36 | 5 | 13.9% |
| `wf_7e016611-b78` | w07_rq1 | GO | 31 | 17 | 54.8% |
| `wf_e670c54b-24b` | w07_rq2 | GO | 8 | 5 | 62.5% |
| `wf_811e50e7-2b2` | no_pwg_w08 | 18,716 ms GO | 21 | 1 | 4.8% |
| `wf_8d3bea69-5dd` | w08_rq1 | GO | 18 | 6 | 33.3% |
| `wf_2629ccda-c57` | no_pwg_w09 | GO | 21 | 3 | 14.3% |
| `wf_dbde820a-82e` | no_pwg_w10 | GO | 18 | 11 | 61.1% |
| **pooled** | | | **192** | **59** | **30.7%** |

**NO-GO arm — n=1 window / 2 cards:** the 16-07 pilot, 0/2 = **0.0%**.

- Windows meeting the 80% clean floor: **GO 0/9 · NO-GO 0/1**.
- Fisher exact at the ≥80% endpoint: **degenerate, p = 1.0** — both arms all-failure; **zero measured discriminative power** for the endpoint that governs promotion.
- The NO-GO arm's 0% lies **inside** the GO range [0.0%, 62.5%] — `wf_33290004-c35` was also 0% after a **3.3 s GO**.

The false-GO is documented in the repo's own words (`generation_api_probe_log.jsonl:6`): *"WARM-UP FAILED TO PREDICT: trivial 3.3s probe was GO, real load produced 2 conn-errors + 7 kill-timeouts at the 180s CEILING"*; and `SERVER_OUTAGES.md:29`: *"the one-call warm-up gate is NECESSARY BUT NOT SUFFICIENT"*. **The one time the 30 s NO-GO was overridden on 90 s/schema grounds, the override was wrong** — probe-log entry 14 (12-07) recorded GO at 53,956 ms on exactly that rationale and produced 5/36 = 13.9% with 32 kill-timeouts. That is an **anti-precedent** for reading the 90 s ceiling as a licence to launch.

**Survivorship censoring:** the two 12-07 NO-GO readings (31,607 / 35,730 ms) were correctly followed by no launch, so their outcomes are unobserved. Every NO-GO→outcome cell except the pilot is censored by construction.

**The n=1 datapoint, honestly.** The gate said NO-GO; the run proceeded under owner override; the real card died at the ceiling. **The gate's direction of prediction was borne out. n=1** — and doubly confounded:

- **Confound A — the card was doomed at 180 s on *any* route.** budget(5,606) = 180,000 ms fully clamped; the harness's own expected time = **272,270 ms** = **1.51× above the budget granted**. The clamp inverts the design invariant at `skel > 3,555.6 B`. This is finding C-01: *"the pipeline did not lose the ability to translate large cards because a route got slow; it lost it when the ceiling stopped scaling with the work."* The kill is over-determined; route latency is not identified.
- **Confound B — concurrency**, a recorded deviation. The pilot report itself refuses the clean reading: *"This run does not establish that a real card cannot finish inside 180 s on a quiet, serially-driven c4."*
- **Confound C — the arm is not distinguishable.** n=1 in an arm whose value is interior to the other arm's range is, statistically, no information.

**Reconciling the three ceilings against the 16-07 readings (arithmetic only, no policy change):**

| reading | vs 30 s | vs 90 s (prose) | vs 180 s |
|---|---|---|---|
| warm-up 53,290 ms | **NO-GO** (1.78×) | GO (0.59×) | GO (0.30×) |
| measured 104,870 ms | **NO-GO** (3.50×) | **NO-GO** (1.17×) | GO (0.58×) |

**The H963 NO-GO survives being re-read under the 90 s schema precedent: 104,870 > 90,000.** Substituting 90 s for 30 s would **not** have flipped it. And the reverse test: a hypothetical 180 s health gate would have said **GO** on both readings, immediately before a card died at 180 s.

**Definitional caveat:** the 9 GO windows' "clean" is the `audit_window.py` clean rate; the pilot's 80% floor is its own promotion floor. Close but not proven identical — the pooled 30.7% should not be quoted as directly commensurable with the pilot's 0%. It does not affect the headline (0/9 vs 0/1 both fail any floor ≥ 65%).

### 6.5 Q5 — Self-profile / parent-session contention

**Zero new serial calls exist. This campaign fired none — so there is no contrast to compute, and no contention magnitude can be estimated.** The serial arm is **empty by construction**, not merely unmeasured.

| Statement | Status |
|---|---|
| Two pilot manifests overlapped on c4; owner brief required serial | **CONTROLLED (recorded self-reported deviation)** |
| canary ~118 s wall, 1/1 ok, 59,250 subagent tokens | **CONTROLLED (measured, n=1)** |
| real ~206 s wall, 0/2 ok, 1 kill-timeout @180,000 ms, skelBytes=5606 | **CONTROLLED (measured, n=1 call / 2 cards)** |
| Gate-0: warm-up 53,290 ms · measured 104,870 ms on 6,828 B, 0 conn errors | **CONTROLLED (measured, n=1 each)** |
| "How much of the timeout is self-contention vs c4 baseline latency" | **UNRESOLVED — verbatim: *"unresolved and unresolvable from this run"*** |
| Parent-session-vs-subprocess contention | **INFERRED confound, explicitly not excluded** |
| Any number attributing X ms or X% to contention | **NOT PRODUCED — would be fabrication** |

**Why unresolvable, formally.** Each latency decomposes as `L = B (baseline) + C (contention)` — **one equation, two unknowns, per cell.** All four live c4 observations (2 Gate-0 probe phases, canary, real) were taken with at least one contention source active (the c4-hosted parent session); the two pilot calls additionally with a second call in flight. **There is not one contention-free cell**, so the system is **unidentified**. Serial arm n = **0**. This is a design property, not a precision problem.

**What CAN be bounded:**

| # | Bound | Value | Basis |
|---|---|---|---|
| B1 | **Canary alone busts the gate with only ONE other call in flight** | ~118 s = **3.93×** the 30 s ceiling | pilot report |
| B2 | Contention degree capped at **2 calls total** | `max_agents:1` × 2 manifests; `agents_spent=1` each | pilot report |
| B3 | **Contention is not necessary** to explain the NO-GO — the verdict is over-determined | Gate-0's 104,870 ms had **no second pilot call in flight** and was still **3.50×** over; fastest-ever reading 53,290 ms is **1.78×** over | Gate-0 report |
| B4 | Removing the companion call would need a **≥74.6%** speed-up for the canary to pass | 1 − 30/118 = 0.746 | derived from B1 |
| B5 | **Sample sizes:** c4 live calls = 4; serial cells = **0**; variance estimate = **null** (single measurement by design, reroll prohibited) | — | Gate-0 report |

B1 is load-bearing: a *trivial synthetic* card, 1-agent ceiling, exactly one companion call, took ~118 s — **~3.9× over the gate**. Whatever share is self-contention, one companion call cannot plausibly account for ~88 s of the ~118 s — **but that last clause is inference, not evidence**, and is offered as such.

**Q5b — can the contention share of the 180 s kill be quantified? UNANSWERABLE.** A share cannot be computed. One arithmetic observation, flagged **ASSUMPTION-LADEN inference, not evidence**: if both manifests launched at ~t=0 back-to-back, the canary's ~118 s ended while the real call still had ~62 s (≈34% of its pre-kill life) to run, i.e. it ran a final solo interval and still did not return. **Not a controlled result** — the walls are manifest wall-clock, not per-call timestamps; the launch offset is **UNVERIFIED** (no artifact records it); parent-session contention persists across even the "solo" interval; n=1 with no variance estimate. Missing telemetry: per-call launch/return timestamps **null**; real-lane subagent tokens **null** (killed before return); machine load and network conditions **null** — *"not instrumented and cannot be reconstructed"*.

**Q5c — the strongest defensible latency statement.** Exactly one sentence, already written in the source: *a real ~5,606 B-skeleton card did not complete within 180 s while a second call was in flight on the same profile.* Everything stronger — "c4 cannot do a real card in 180 s", "serial c4 is viable", "c4 throughput is X" — is **not supported**.

| Reading | payload | latency | × 30 s ceiling | companion pilot call in flight? |
|---|---|---|---|---|
| Gate-0 warm-up | 6,828 B trivial probe | 53,290 ms | **1.78×** | **no** |
| Gate-0 measured | 6,828 B trivial probe | 104,870 ms | **3.50×** | **no** |
| pilot canary | synthetic 3-sense card | ~118,000 ms | **~3.93×** | **yes (1)** |
| pilot real | 5,606 B masked skeleton | ≥180,000 ms (killed) | **≥6.00×** | **yes (1), partially** |

All four exceed the ceiling; the two with no companion call already exceed it by 1.78× and 3.50×, so **self-contention is not required to produce a NO-GO**. Residual caveat: **none of the four is contention-free** — all share the c4-hosted-parent confound. The table bounds how far over the ceiling the observations sit; it does **not** establish c4's contention-free baseline, which remains **null — never measured**.

### 6.6 Q6 — Accuracy of the preflight and cost model

**Every prediction was arithmetically correct and jointly useless. The preflight predicted the right thing — cheapness — and the run failed on a variable the preflight does not contain a single term for.**

The preflight arithmetic reproduces exactly:

| quantity | formula | value | published |
|---|---|---|---|
| `agent_expected_after_tm` | from `gh.build` META | 1 | 1 ✓ |
| `est_agents_with_realism` | 1 × 1.35 | 1.4 | — |
| `est_tokens` | 1.35 × 184,000 | 248,400 | — |
| `est_cost_usd` | 1.35 × 0.347 | **$0.47** | **$0.47** ✓ |
| `est_cost_per_card_usd` | 0.47 / 2 | $0.23 vs $2.00 ceiling | `ok` ✓ |
| `recommended_action` | `1 ≤ 15` | **`run-now-low`** | ✓ |

| predictor | predicted | actual | accuracy | honest reading |
|---|---|---|---|---|
| `agent_expected_after_tm` | 1 | `agents_used=1` (both windows) | exact, n=2 | **Not a validation** — `max_agents:1` mechanically capped it. The only *unconstrained* test on record is pril10_w1: **174 predicted vs 230 actual = 1.32× under**, n=1. |
| `projected_calls` (`est_agents_with_realism`) | **1.35** | ceiling was **1** | **incoherent** | The realism factor projects *more* agents than the mandated ceiling permits. Preflight never reads `max_agents`. |
| `run-now-low` | `run-now-low` | 180 s kill, 0 cards | **correct and irrelevant** | `recommendation()` is a **pure function of agent count**: `0→skip-cached`, `≤15→run-now-low`, `≤20→run-next`, else `defer-calibrate`. A *cheapness* band. It was never a deliverability prediction, and was never wrong about cheapness. |
| cost model | $0.47 / 248,400 tok | canary **59,250 tok** for 1 agent; real **null** | **over-estimates 3.1–4.2×, n=1** | 184,000/59,250 = **3.11×**; with realism 248,400/59,250 = **4.19×** |

**The mechanical fact the preflight could have computed for free, and did not** — the real call was doomed at manifest-write time, from a number the harness already had: expected 272,270 ms, granted 180,000 ms, **granted/expected = 0.661**. The `KILL_FACTOR = 2` safety margin **never applied** — clamped away by `KILL_CEIL_MS`. The call needed ~165 s at the OLS centre and ~247 s at the observed-max rate against a 180 s budget. **Preflight said `run-now-low · cost ok`.**

**What the cost model does NOT model.** A grep of `perf_preflight.py` for `kill|skel|latency|timeout|wall|deliver|route|profile` returns **zero substantive hits**. The model is `agents → tokens → dollars`, a one-variable linear map. Absent:

1. **Delivery probability.** No `skel_bytes` term, no kill-budget term. **A card that cannot be delivered is priced identically to one that can.** This is the whole failure.
2. **Route/profile health.** The Gate-0 NO-GO is invisible to preflight; `run-now-low` would be emitted on a dead route.
3. **Tokens burned by a killed call.** The gate *"does not save the tokens the doomed call already burned up to the timeout — without `AbortController` it can't."* The real lane's `subagent_tokens: 0` is harness accounting, not billing: true cost is **null, not $0**. No term for spend-without-yield.
4. **`max_agents` / `max_heal_agents` coupling.** `max_agents=1` forces `max_heal_agents:0`, so one kill nulls **every card in the batch** with no heal lane — observed: 2 cards → 2 nulls, `"budget-kill-switch[heal]: hit 0 agent() calls"`. No "cards lost per kill" term.
5. **Batch super-additivity.** `skelBytesOfKeys` sums against one shared budget while a single-card call gets the full ceiling unconditionally. The cost model treats cards additively; the kill gate does not. **Batching two $0.23 cards created one undeliverable 5,606 B call.**
6. **Uncertainty.** Point estimate only, no interval, fitted on **one** window.
7. **Rate currency.** The Sonnet 5 promo is deliberately excluded — which the source flags would move $/agent ~−33%, a "FLAG-for-human event". The artifact records: `preflight_cost_caveat: "point estimate from a rate table whose currency was NOT verified this campaign"`.

**Calibration provenance — the whole model rests on n=1 window:**

| const | value | recomputation | n |
|---|---|---|---|
| `PER_AGENT_TOKENS` | 184,000 | 42,316,604/230 = **183,985** ✓ | 1 window |
| `PER_AGENT_USD` | 0.347 | 79.83/230 = **$0.3471** ✓ | 1 window |
| `REALISM_FACTOR` | 1.35 | 230/174 = **1.322** (rounded up) | 1 window |

**Every constant is fitted on a single window — the pril10_w1 blow-up, i.e. the pathological run the gate exists to prevent — and never re-fitted.** The one clean agent since came in at **0.32×** the constant. A model calibrated on a blow-up systematically over-prices healthy work, making its `cost ok` verdict **permissive in exactly the wrong direction**: it flags monsters on price while waving through anything cheap, including cards that are structurally undeliverable.

**One line:** the cost model is a **price** model wearing a **launch-gate**'s badge. It answers "will this be expensive?" (correctly: no, $0.47) and is read as "should this run?" (catastrophically: yes). The pilot is the clean demonstration — a correct $0.47, an exact agent count, a legitimate `run-now-low`, and 0 cards.

### 6.7 Q7 — Three agents vs 117 projected calls

**RESOLVED. The contradiction is real-but-not-a-contradiction — and the stated hypothesis is REFUTED as worded, while its conclusion survives for a different reason.**

`projected_calls` **IS** `agent_expected_after_tm` — literally the same field, assigned by one line (`no_pwg_scale_plan.py:315`). The 3-vs-117 gap is **not** two counting units and **not** mislabelling: it is the **same counter evaluated under two different `--output-budget` settings**. The 3-agent window ran at the default citation-weighted budget **90** (batching ON: 95 runnable keys → 3 batches); the H818 windows100 lane hard-codes **`--output-budget=1`** (batching OFF by construction: one card per batch), so its dispatch-slot count degenerates to ≈ one per subcard.

| Term | Definition | Anchor |
|---|---|---|
| **batch** | keys packed greedily until summed `sizer()` exceeds budget; an oversize item still gets its own group | `gen_opt_harness2.py:496-515` |
| **agent** (`agent_expected_after_tm`) | `len(batches) + Σ fragment groups` — "one call per batch + one per presplit fragment group"; an **optimistic FLOOR** (no retries) | `gen_opt_harness2.py:1186-1190` |
| **`projected_calls`** | `preflight.get('agent_expected_after_tm')` — **an alias, nothing more** | `no_pwg_scale_plan.py:315` |
| plan-level `projected_calls` | sum over the five windows | `no_pwg_scale_plan.py:515` |
| **the divergent knob** | `'--output-budget=1'` in `preflight_json()` | `no_pwg_scale_plan.py:221`, generator `:294` |

`sizer(k) = 1 + ls ≥ 1` for every card, so at `budget = 1` any non-empty group plus a next item gives `≥ 2 > 1` → **every card becomes its own batch, unconditionally.** The code says so: `--output-budget=1` is *"the no-PWG single-card lane"*.

| | 100-key nominal window | H818 windows100 dry-run |
|---|---|---|
| removed pre-batching | 5 degenerate pass-through, `tm_cards: 0` → 95 runnable | not recoverable from artifacts |
| **`output_budget`** | **90** | **1** |
| `presplit_keys` | `[]` | 0 (H823 cite floor) |
| **`batch_count`** | **3** | ≈117 |
| **`agent_expected_after_tm`** | **3** | **117** |
| keys per dispatch slot | 95/3 ≈ **31.7** | ≈ **1.0** |

Cross-check: H911 records the same lane as **"124 subcards → 124 initial calls"** — the 1:1 ratio is stable, exactly what `--output-budget=1` predicts and what a batching lane would never produce.

| Claim under test | Verdict |
|---|---|
| "'agents' counts DISPATCH SLOTS after TM/batching collapse" | **CONFIRMED** |
| "'calls' counts PER-KEY units BEFORE the collapse" | **REFUTED** — `projected_calls` is a verbatim alias of the *same* post-collapse count; it only *looks* per-key because the lane's budget makes slots and keys 1:1 |
| "not contradictory, only mislabelled" | **CONFIRMED in conclusion, wrong in mechanism** — a genuine **configuration** difference (budget 90 vs 1), not a labelling artifact |

**Residual naming defect (observation, not a fix):** the alias renames a field whose semantics are budget-dependent without carrying the budget alongside it. `perf_preflight.py` propagates `output_budget` into its report but `headless_meta` drops it — so a reader sees `projected_calls: 117` with no way to know it was computed at budget=1. **That is the whole mechanism by which the two numbers read as a contradiction.**

**Nulls:** the exact 117 is **NOT machine-verifiable in this worktree** — the windows100 plan manifest is absent; 117 exists only as prose in two docs. Its *definition* is fully traceable; its *value* is **UNVERIFIED** here. The 120→117 delta is **INFERRED** from the definition, not read from an artifact — split = **null (artifact absent), not 0**. No code was executed for this answer.

### 6.8 Q8 — Do deterministic audit results agree with manual inspection?

**UNANSWERABLE as a rate at n=1.** This pilot produced exactly ONE audit-vs-manual comparison, on a synthetic card the model knew was a test.

| run | key | `audit_classification` | `manual_review_verdict` | agree? | usable as a rate? |
|---|---|---|---|---|---|
| `h963_c4_canary` | `dq_canary_puregloss` | `clean` | `clean — all 3 pure-gloss senses rendered` | ✅ | **no — n=1, synthetic** |
| `h963_c4_real` | `zaz` | `null / hard-failure` | `unverifiable — no output to inspect` | n/a | **no — not an agreement observation** |
| `h963_c4_real` | `upama` | `null / hard-failure` | `unverifiable — no output to inspect` | n/a | **no** |

**The two real rows must not be scored as agreements.** Both verdicts are statements that *no data exists*, not concordant judgments about quality. Counting them 2/2 would let a latency failure masquerade as detector validation.

- **Agreement on inspectable cards: 1/1 = 100%.** Wilson 95% CI = **[20.6%, 100%]** — a 79-point interval is not a measurement; it is compatible with a detector that agrees with humans 21% of the time.
- **Agreement on REAL cards: 0/0 — undefined.** Not 100%, not 0%.
- **The one datum is biased toward flattery**, per the artifact's own caveat: the model *explicitly recognised the card as a synthetic canary in its notes*.

**The one real agreement measurement that does exist** (pre-H963, different guard) shows the shape a real Q8 answer has — `prompt_rule_audit.py:112-114` records **n=22 firings, 21 manually adjudicated as false positives, 1 genuine → 4.5% precision** before the exclusion was added. These guards *can* disagree with manual inspection catastrophically until calibrated. Caveat: that is the H960 `dropped_sanskrit_span` guard, not SAN-LOSS/TNMASK, and it predates H963 — it does not transfer.

### 6.9 Q9 — What guard telemetry was actually EXERCISED?

**Exactly ONE guard fired a true positive live, and it was not a quality guard — it was the budget/kill-timeout.**

| Guard | Live FP on clean | Live TP (sensitivity) | Why not exercised | Verdict |
|---|---|---|---|---|
| **SAN-LOSS** | **0** on 1 card / 3 senses | ❌ **NEVER** | canary emitted 3/3 — the trap never sprang | **UNVALIDATED live** |
| **TNMASK** | **0** | ❌ **NEVER** | *"n/a — canary carries no `{Tn}`"* — **structurally incapable of firing** | **UNVALIDATED live** |
| **`dropped_sanskrit_span`** | **0** | ❌ **NEVER** | *"canary carries no `{#..#}`/`<ls>` by construction"* — **structurally incapable** | **UNVALIDATED live** |
| **ls/sk fidelity-reject** | not observed | ❌ **NEVER** | 0 real cards returned; canary is ls:0/sk:0 | **UNVALIDATED live** |
| **`count_source_senses`** | not observed on real raw | ❌ **NEVER** | 0 real cards returned | **UNVALIDATED live** |
| **Hard-reject arming** | n/a | ❌ **NEVER ARMED** | both `HARD_REJECT` flags `false` throughout | **UNVALIDATED live** |
| **Budget kill-switch** | n/a | ✅ **TRUE POSITIVE** | kill @180,000 ms, skelBytes=5606 | **only guard with live TP evidence** |
| **`max_agents:1` ceiling** | n/a | ✅ mechanically honoured | — | enforcement confirmed |

**The critical asymmetry:** *zero false positives* and *proven sensitivity* are separate experiments, and only the first was run. Two of the three quality guards **could not have fired by construction of the canary itself**. Their `0` is a **null with a reason**, and the artifact records it that way (`build_campaign_evidence.py:87-88` writes `0 if tag == "canary" else None` with an explicit reason field). **Missing telemetry is null, never zero — honoured.**

**Statistical worth of the 0-FP result:** 0 FPs in 1 card / 3 sense-observations → rule-of-three upper 95% bound ≈ **100%**. **Formally uninformative. It excludes nothing.** The pilot report says it itself: *"A guard that never fired on a card where nothing was wrong tells us nothing about whether it fires when something is."*

> **⚠️ The brief's premise needs correcting: the offline fixtures ALREADY EXIST, already prove true-positive sensitivity, and already run in CI.** `window_selftest.py` is **5,333 lines** (`wc -l` confirms the brief's figure exactly) and — with `accept_sensecount_test.js` — already contains TP cases for every quality guard: SAN-LOSS (4 drop-shapes each firing), the SAN-LOSS audit gate (darvI 2/3 → returncode 1 + requeue), TNMASK (dropped `{T2}` → mismatch 1), `dropped_sanskrit_span` (mid-sense `{#kar#}` drop + 3 controls incl. the 95%-FP headword-label class), ls/sk fidelity-reject, and hard-reject arming. `.github/workflows/ci.yml:149` runs them. The JS fixture extracts the **real emitted `accept()`** verbatim from the generator by regex so it cannot drift from production code. **Execution status: UNVERIFIED — I did not run them.** The brief authorised offline selftests only if explicitly told to, and told me to look, not run. CI wiring asserts they pass; I did not observe it.

**What is genuinely unvalidated — and it is not fixture-shaped.** The fixtures validate detector arithmetic *given a correct `source_senses`*. Three links remain open and no fixture can close them:

1. **False-flag RATE on real production output** — needs real cards. 0 returned.
2. **`count_source_senses` accuracy on the real corpus at scale** — the fixture is 6 hand-picked strings; the corpus is 11,605 store rows. The 21/22 (95% FP) history is direct evidence that hand-picked fixtures do **not** predict corpus-wide behaviour for this guard family. *Partially addressable offline* — no live call required.
3. **Whether the model silently drops senses in production at all** — a fact about model behaviour under load. Only a live run answers it.

**Bottom line for Q8 and Q9: the limiting factor is n, not missing fixtures.** Building more offline fixtures would rebuild what exists. The single exception worth building is item 2.

### 6.10 Q10 — Promotable rows, calls/clean, tokens/clean under serial c4

**Promotable rows = 0. calls/clean = null. tokens/clean = null. Serial c4 = never measured (n=0 runs).** No part of Q10 is answerable. Each null has a distinct reason; they are not interchangeable.

| Lane | cards | ok (clean) | null | clean_rate | promotable |
|---|---|---|---|---|---|
| real (`h963_c4_real`) | 2 (`zaz`, `upama`) | **0** | 2 | **0.0%** | **0** |
| canary | 1 | 1 | 0 | 100.0% | **0 — synthetic, never promotable** |
| **total promotable** | | | | | **0** |

Store verified unchanged: 11,605 rows, sha256 `cc1d544e…c805` both sides.

**⚠️ Discrepancy flagged (not fixed — measurement pass):** `pilot_measurement.json` labels the canary run `"promotable_clean_keys": ["dq_canary_puregloss~~h0_zz_pw"]`, contradicting the pilot report's never-promotable policy. This is a **schema field-naming defect, not a promotion** — the store hash proves nothing was written. But the artifact asserts promotability for a key policy forbids promoting; **an automated promoter reading this field would promote synthetic output into the canonical store.**

**calls/clean = null — three independent reasons, each sufficient:**

1. **Division by zero.** clean_real = 0. The codebase enforces exactly this — `economy_ledger.py:133-143`: `if clean == 0: rec['agents_per_clean'] = None; rec['status'] = 'wasted_calls'`, docstring: *"dividing by it is undefined. Such a run is reported as `wasted_calls`, NEVER as an agents_per_clean value."*
2. **Not serial.** Recorded protocol deviation. **Serial c4 economy: n = 0 runs. Never measured.**
3. **The metric as worded does not exist in this pipeline.** `economy_ledger.py:11-15`: the numerator is `agents_used`, *"NOT the same as the `run_summary.calls` counter… we never call it 'calls per clean' without qualification."* **Even a fully successful run would not yield "calls/clean" as H963 words it.**

The correct ledger status for this run is `wasted_calls`: 1 agent spent, 0 clean.

**tokens/clean = null — two independent reasons:** the same zero denominator, and **the numerator is itself null, not zero** — real `subagent_tokens = 0` annotated *"(killed before return)"*. A call that ran to a 180,000 ms kill consumed tokens; 0 is a reporting artifact. **True real-lane spend is unrecoverable from this run.**

**Non-generalizable canary datapoint (do NOT substitute):** 1 agent / 1 clean = 1.0 agents-per-clean; 59,250 tokens / 1 clean = 59,250 tokens-per-clean. Disqualified on four grounds: synthetic; n=1 (a point, not a rate); concurrent not serial; the model recognised the card as a test. `preflight est. cost $0.47` is an **estimate, not observed** — never quotable as measured economy.

**The economy targets, and how far the data is from testing them:**

| Target | Threshold | H911 status (14-07) | After this pilot (16-07) | Distance from testable |
|---|---|---|---|---|
| observed calls/clean | ≤ 1.75 | INCONCLUSIVE (`not_recoverable`) | **still INCONCLUSIVE — null** | needs ≥1 real clean row; have **0** |
| observed $/clean | ≤ $0.75 | INCONCLUSIVE (`not_recoverable`) | **still INCONCLUSIVE — null** | needs ≥1 real clean row **and** a returned token count; have **0** and **null** |

**Distance is not "close" — it is categorical.** Both gates were INCONCLUSIVE before the pilot and are INCONCLUSIVE after. The gap is not precision or sample size: **the denominator does not exist.** You cannot be 10% or 90% of the way to dividing by zero.

**A statistical note, stated to bound honesty rather than rescue the number:** observed real clean rate is 0/2. The 95% two-sided Clopper-Pearson upper bound is 1 − 0.025^(1/2) = **84.2%** (one-sided 95%: 77.6%). So **n=2 cannot statistically reject the 80% floor** — the interval [0%, 84.2%] straddles it. This does **not** soften the verdict: the promotion gate is a **hard rule on observed rows** (0 clean rows = nothing to promote), not a hypothesis test. But anyone tempted to read "0% clean rate" as a *measured property of c4* should note the data does not support that inference either — **n=2 measures almost nothing in both directions.**

**Upstream blocker: latency, not economy.** Economy cannot be measured until cards return at all.

---

## 7. Limitations and protocol deviations — exhaustive and unflattering

**Deviations introduced by this campaign: none.** The pilot's deviation is preserved as recorded, not reinterpreted.

**Limitations of this pass:**

1. **The campaign did not do what it was briefed to do.** Brief 4 asked for an 8-cell live matrix. **0 of 8 cells ran.** The offline packet is what was produced *instead*, and it is **not** a substitute. §8 is the honest accounting.
2. **The live matrix was unrunnable from this session by construction** — wrong profile, unenforceable `c4 only`, guaranteed provenance failure. This was knowable at intake and is not a mid-run discovery.
3. **The brief's own hard stops were already tripped before the campaign began** — the kill-ceiling overrun and the concurrency deviation both belong to the pilot brief 4 instructed us to close. The campaign therefore began already inside its own stop condition.
4. **Every regression in §6 extrapolates beyond its fitted range.** The 04-07 benchmark's largest skeleton (2,929 B) is roughly HALF the pilot's real batch (5,606 B) and a THIRD of the nominal-core median (~8,224 B).
5. **The skel/raw ratio band is n=2** (0.537, 0.750) and both measured ratios straddle the median's DOOMED threshold (0.573). The campaign journal names this its weakest link. Every deliverability percentage in §4 and §6.2 inherits it.
6. **The cost model's every constant is fitted on n=1 window** — and that window is the pathological pril10_w1 blow-up the gate exists to prevent. Never re-fitted.
7. **No dataset replicates across days at matched size** except the accidental sweep(n=3) vs Gate-0(n=2) pair at ~6.5 KB — which is the pair that produces the report's largest unexplained effect (4.07×).
8. **The Gate-0 readings are n=1 each, by design** (reroll prohibited by the brief) — **no variance estimate exists**. Machine load and network conditions were **not instrumented and cannot be reconstructed**.
9. **The pilot's two live calls are excluded from every latency statistic** in §6.1 because they overlapped. They contribute only as recorded facts, never as latency evidence.
10. **The canary is biased toward flattery** — the model recognised it as a test in its own notes. Every canary-derived number (59,250 tokens, 1/1 clean, 0 FPs) inherits that bias.
11. **Doc/code drift on a load-bearing constant:** `FAILURE_MODES_AND_KILL_GATE_2026-07-04.md:150` still documents `KILL_CEIL_MS = 480000` while the code says `180000`.
12. **The 480,000 → 180,000 lowering has NO reviewable provenance** — the repo history is squashed; the only surviving record is a code comment.
13. **The 90 s schema ceiling is prose-only** — zero code hits; `probe_log.py` enforces 30 s universally with no schema branch.
14. **The 117 in Q7 is UNVERIFIED in this worktree** — the plan manifest is absent; the number exists only as prose. Its definition is traceable; its value is not confirmed.
15. **`pilot_measurement.json`'s `promotable_clean_keys` labels the synthetic canary promotable** — a promotion-safety hazard, flagged and deliberately **not fixed** (this is a measurement pass).
16. **The selftests were NOT executed** this pass. Their pass/fail status is asserted by CI wiring, not observed by me.
17. **Three candidate features are 0/114 non-null** (`masked_token_count`, `record_grammar_token_count`, `fragment_presplit_count`) — schema v1 does not emit them; a TNMASK-restoration predictor cannot be built without a re-scan.
18. **Token split telemetry is null and not recoverable post-hoc** — no economy question is answerable until the harness persists input/cache_read/cache_create/output splits.
19. **Q4's pooled 30.7% is not proven commensurable** with the pilot's 80% promotion floor (different definitions of "clean").
20. **The survivorship censoring in Q4 is structural** — the probe log records only what the gate let through, so the gate cannot be validated from it.

---

## 8. What remains unanswered, and the exact measurement that would answer each

Stated plainly: **the offline audit answered none of the following. They remain unanswered for want of serial live data.** Each row names the measurement that would settle it. Every live item requires owner authorisation; the 30 s launch prohibition is live.

| # | Unanswered question | Why the offline pass cannot touch it | The exact measurement |
|---|---|---|---|
| 1 | **Does a real card return on a quiet, serially-driven c4 at all?** | Serial arm n=0; all four live c4 readings carry the parent-session confound | One c4 call, real ~5–6 KB skeleton, **serial**, from a session **not hosted on the c4 profile** — zero companion calls and zero parent contention on the same credentials |
| 2 | **How much of the latency is contention vs c4 baseline?** | `L = B + C`, one equation two unknowns, **no contention-free cell exists** | The same non-c4-hosted serial call: its latency estimates B; the pilot's observed minus that bounds C |
| 3 | **Fixed overhead vs output rate vs input rate** | The two existing datasets disagree because input and output are confounded in one and pinned in the other | A factorial probe **decoupling input from output**: ≥3 input sizes (1/5/15 KB) × ≥2 commanded output lengths × ≥5 reps × ≥3 time-of-day blocks ≈ 90 serial calls, one profile, `max_wide=1`, no overlap; emit input/output/cache tokens + TTFT + wall; fit `wall ~ input_B + output_tokens + (1|block)` |
| 4 | **Does batching improve cards-per-agent without more defects?** | Cells 1–4 not run; the mechanism predicts the batch dies before returning anything to score | {1,2,4 heads} × {tiny, typical} × ≥5 reps = 30 serial calls, keys randomly assigned within stratum. **Two blockers must clear first:** (a) correct the kill envelope or run with `--no-kill`/raised `--kill-factor`, else the cells only re-measure C-01; (b) drop `--max-agents=1`, which forces `max_heal_agents:0` and destroys the per-card outcome data |
| 5 | **Does the 30 s gate predict card failure?** | One uncensored NO-GO→launch pair, interior to the GO arm's range, kill over-determined by C-01 | Paired probe→card design launching on **both** verdicts, ~20–30 cards/arm (~80% power for a 30-point gap), skeletons **< 3,555 B** so kills attribute to route latency not the clamp, serial dispatch, and a **work-representative `CARDS_SCHEMA` probe** rather than the inert-filler `{ok:true}` probe |
| 6 | **Guard false-positive rate on real output** | 0 real cards; the 0-FP result's rule-of-three bound is ~100% — formally uninformative | ≥20–30 **real clean cards**, each audit verdict cross-tabulated against manual inspection into a 2×2. Requires the C-01 envelope corrected first — at a flat 180 s, 46–66% of the runnable universe cannot return a card at all, so no amount of live calling produces the sample |
| 7 | **Audit-vs-manual agreement rate (Q8)** | n=1, synthetic, model knew it was a test | Same ≥30 real clean cards; nothing offline substitutes — Q8 is definitionally about real model output |
| 8 | **Token use / cost model validation** | n=1 agent (0.32× the constant); split telemetry null and not recoverable | Instrument the harness to persist per-agent input/cache_read/cache_create/output splits (`parse_workflow_cost.py` already parses them — the pilot simply did not retain the transcript dir), then ≥20 agents across the size range |
| 9 | **True real-lane spend on a killed call** | `subagent_tokens: 0` means killed before return; the gate cannot save the tokens already burned | Incremental/streamed token accounting persisted **before** the kill fires, so a killed call reports true consumed spend rather than 0 |
| 10 | **Observed calls/clean ≤ 1.75 and $/clean ≤ $0.75** | Denominator = 0; not serial; metric name mismatch | ≥1 real clean row (defines the division) **plus** n≈30 for a rate (95% CI ≈ ±15 pp — enough to separate an 80% floor from a ~62% reality), on a properly sequenced serial run with surviving token telemetry |

**Offline / zero-call work that would materially reduce uncertainty, and is NOT yet done:**

| # | Measurement | Why it matters |
|---|---|---|
| A | **Compute `skel_bytes` for all 114 prebuilt-input heads** (`gen_opt_harness2.build` already emits it) | Replaces the **n=2** skel/raw ratio band — the single dominant uncertainty in every deliverability number in this report — with a real distribution. **Highest-value measurement available at zero live cost.** Already queued as an open hypothesis in the campaign journal |
| B | **Run `count_source_senses` over all 114 prebuilt raw inputs; hand-adjudicate a random n=30** | The one link where hand-picked fixtures have a **measured** history of failing to generalise (21/22 = 95% FP). No live call required |
| C | **Re-scan candidates emitting `masked_token_count` / `record_grammar_token_count` / `fragment_presplit_count` (schema v2)** | Without these, a TNMASK-restoration predictor cannot be built at all |
| D | **Verify the 117 by running `perf_preflight.py` on the five H818 windows at `--output-budget=1`, then A/B the same key-lists at `--output-budget=90`** | Would dissolve the Q7 contradiction mechanically on one screen. Prerequisite: recover the windows100 key-lists / plan manifest, which is absent from this worktree |

**One decision needs no run at all and is the cheapest unblock available:** resolve whether H963's "calls/clean ≤ 1.75" means `agents_per_clean` (what the ledger measures) or `run_summary.calls` (which the ledger explicitly refuses to conflate with it). These are different numbers against the same ceiling. Until this is settled, **a green run still could not report a verdict against the target as worded.** A human should decide.

---

## Compliance

Read-only measurement pass. No `claude` command, no generation/Workflow/`agent()` call, no opt2 harness run, no selftest execution, no write to the canonical store, the TM, or any tracked pipeline file. All arithmetic is hand-derived from constants read at cited lines; `killgate_envelope.py` was **read, not run**. Canonical store untouched: **11,605 rows**, `cc1d544ed92d201ca8cbecde0b5e9a8191994dfd1baf20841da82f1f9ae7c805`. **H963 is NOT PASS. H255 / no-PWG stays FROZEN.**

_Dr. Mārcis Gasūns_
