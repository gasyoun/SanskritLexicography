# Progress kitchen — improvements inventory

_Created: 02-08-2026 · Last updated: 04-08-2026_

**Shipped residual (H2218, 02-08-2026):** B1 subscription loader+UI · B9 idle-reason taxonomy · B10 article-site parity · R4 ledger metric backfill script (best-effort; unrecoverable rows stay null).

**Surface:** [gasyoun.github.io/…/progress/](https://gasyoun.github.io/SanskritLexicography/progress/)  
**Builders:** [`build_progress_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_progress_data.py) · [`build_kitchen_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_kitchen_data.py) · [`kitchen_slices.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_slices.py)  
**Inventory handoff:** [H2211](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2211-Grok_SanskritLexicography_progress-kitchen-improvements-inventory_02.08.26.md)  
**Implement handoff:** [H2212](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2212-Grok_SanskritLexicography_progress-kitchen-k1-k8-implement_02.08.26.md) — **K1–K8 shipped** (02-08-2026)

This is a **measurement / product** backlog for the public kitchen + progress page — not a rewrite plan. Local ops (`:8765`, 5 s) stays the place for sub-second gates; the web page should answer *how is the campaign going?* for a human who opens the link once a day or once a week.

---

## 1. What we already measure and show

### Progress (results)

| Metric | Source | Note |
|---|---|---|
| Verb funnel (universe → DCS → promoted → runnable / blocked) | `verb_batch_worklist.json` | Honest denominators |
| Nominal candidates / promoted / medium-50 | `nominal_batch_worklist.json` | Medium-50 status is a prose string |
| Store depth (senses, roots) | `pwg_ru_translated.jsonl` | Live count |
| AI vs human review bar | store `review_status` | Currently ~all AI first-pass |
| DCS-attested coverage % | frequency assets + fallback total headwords | Denominator can be a documented constant |
| Corpus / TM pairs + recall % | corpus asset + H309 constant | Recall marked `*` |
| Daily trend (senses, verb promoted, coverage) | `progress_timeseries.json` | Sparse — few rebuild days |

### Kitchen (process) — post H2204

| Metric | Source | Note |
|---|---|---|
| Cards last hour / 24h | store `provenance.generated_at` | Zero when idle for days |
| Mean min / window | `window_ledger` `production_metrics` | Sparse: wall-clock present on only ~12/473 rows |
| Mean tokens / window | ledger | Often null |
| Current idle / last idle / total idle / idle-by-month | stage gaps + ledger fallback | H2204 |
| $ band / clean card | economy ledger / probe log | Band, not invoice |
| Total $ clean dictionary vs prep/redo | token piles × price band | H2204 |
| Agents / clean card | economy aggregate | Incl. requeues |
| Recent windows + idle gaps (equal length, expand) | ledger + events | H2204 |
| Campaign calendar (cards/day heatmap) | store by day + window counts | Last 120 days |
| Web changelog | `RussianTranslation/CHANGELOG.md` | Method versions |

### Activity chip (already computed, partly shown)

`activity.translation_on`, `window_state`, `window_root`, `next_action` live in `kitchen_data.json` — chip shows on/idle/stale, but **next_action / last root / needs_requeue** are not first-class cards.

---

## 2. What we measure but barely show (high ROI)

Data already exists in gitignored pilot artifacts; builders just do not surface it.

| # | Opportunity | Evidence on disk (census 02-08-2026) | Suggested UI |
|---|---|---|---|
| A1 | **Window outcome mix** | Ledger 473 rows: `needs_requeue` 350, `stale_artifact` 108, `clean` 3, … | Stacked bar or donut: clean / requeue / stale / blocked / partial |
| A2 | **Requeue load** | `requeue_count` sum 4422; transient 903 / defect 1428 where present | Cards: mean requeues/window; transient vs defect split |
| A3 | **Clean-key yield** | `clean_key_count` sum 13666, mean ~29.5 | Clean keys last 24h / mean clean keys/window |
| A4 | **Last window + next action** | `window_status.json`: state, root, `next_action`, requeue keys | One “operator strip”: root · state · next_action (sanitized) |
| A5 | **Audit gate summary** | Events: 3661 `gate_summary`, 696 `requeue_summary`, 372 `glue_result` | Pass rate of last N gates; top failure reasons |
| A6 | **Root concentration** | Top ledger root `sTA` alone = 98/473 windows | “Most revisited roots” table (bottleneck signal) |
| A7 | **Production wall-clock coverage** | Only 12/473 rows have `wall_clock_minutes` | Show “measured on N windows” under mean min; fix instrumentation |
| A8 | **Store review truth** | progress has `approved` 3 / `ai_translated` 11598 / `needs_review` 2, but UI collapses human to 0 via wrong field | Align `human_reviewed` with `approved` + show three-way bar |
| A9 | **Campaign age + last card** | Store oldest ~2026-06-29, newest ~2026-07-14; ledger last 2026-07-15 | “Days since last promotion” + “campaign day N” |
| A10 | **ETA / burn-down** | Verb: 48/749 promoted; speed series exists | Projected days to verb-scope @ 14d mean (label **estimate**) |
| A11 | **Cost completeness** | Economy probe log is a **tiny** priced sample vs full campaign | Badge: “priced sample n=… cards” so band is not read as total invoice |
| A12 | **Calendar idle overlay** | Idle gaps + heatmap both exist | Grey/red idle days on calendar, not only green card days |

**Priority order (show-only):** A4 → A1 → A2 → A8 → A9 → A10 → A5 → A6 → A12 → A11 → A7.

---

## 3. What we do not measure (but should)

Instrumentation gaps — no honest number on the page until a writer exists.

| # | Gap | Why it matters | How to measure (sketch) |
|---|---|---|---|
| B1 | **True billed $ (or subscription units)** | Band is extremes (cache-read vs fresh-input); Claude Max is subscription, not list-price | **H2218 shipped:** loader + UI + example schema; paste weekly usage export → `economy_subscription.json` (first real $ still needs human paste) |
| B2 | **Per-window wall-clock + token completeness** | Speed/cost cards are statistically weak | Always write `production_metrics` on every audit close (not 12/473) |
| B3 | **Health / route readiness (c4 …)** | Nonstop plan blocked on bimodal c4; kitchen never says GO/NO-GO | Append-only `health_probe_log.jsonl` (profile, wall_ms, api_ms, verdict) → sparkline + last verdict |
| B4 | **Quality / fidelity over time** | Throughput without quality is vanity | Sample judge scores or fidelity aggregate per root/window; % gates green |
| B5 | **Human review throughput** | 11.6k AI cards, almost zero approved | Daily approved count; queue of `needs_review`; G5 sheet open rate |
| B6 | **Promotion vs generation** | Store grows without “promoted clean window” | Count ledger `state==clean` and promote events; cards promoted this week |
| B7 | **Lane burn-down beyond verb** | Nominal medium-50 paused; no public reason depth | Structured pause reasons + runnable backlog age |
| B8 | **Multi-PC / multi-profile split** | Future nonstop multilane | `gen_model` / host / profile tags on ledger (only 15 rows have `gen_model` today) |
| B9 | **Idle reason class** | Idle days are opaque | **H2218 shipped:** taxonomy + `idle_reason_log.jsonl` + auto-rules with evidence; silence → unknown |
| B10 | **Article-site parity** | Progress store count vs published articles | **H2218 shipped:** kitchen card diffs store roots vs article_site; measured=false if site absent |
| B11 | **Error / crash rate** | `crash_state` events rare but load-bearing | Crashes per 100 windows; last crash root |
| B12 | **Judge coverage** | `judge_sample_*` on ledger | % windows with judge sample; mean sample size |

**Priority order (instrument):** B2 → B3 → B6 → B4 → B5 → B9 → B1 → rest.

---

## 4. What not to put on the public page

| Keep off public web | Why |
|---|---|
| Full requeue key lists, local paths, workflow temp JSON paths | Noise + machine layout leak |
| Live 5 s gate streaming | That is `:8765` |
| Raw Max/Workflow account emails or subscription receipts | Privacy |
| Per-card text / DE→RU content | Rights + size; article site owns finished text |
| Undocumented constants presented as live | Trust block already exists — keep `*` discipline |

---

## 5. Suggested product slices (implementation units)

Each slice is one PR / handoff-sized unit.

| Unit | Delivers | Depends on | Status |
|---|---|---|---|
| **K1 — Operator strip** | Last root, window state, next_action (sanitized), days since last card | A4, A9 | ✅ H2212 |
| **K2 — Yield quality** | Outcome mix + requeue/transient/defect + clean-key yield + top roots | A1–A3, A6 | ✅ H2212 |
| **K3 — Review honesty** | Three-way store bar (approved / needs_review / ai_translated); human_reviewed = approved | A8 | ✅ H2212 |
| **K4 — ETA strip** | Verb % + estimated days at 14d card rate (labelled estimate) | A10 | ✅ H2212 |
| **K5 — Health ribbon** | Last probe GO/NO-GO + recent sparkline from gate0 probe logs | B3 (read existing probes) | ✅ H2212 |
| **K6 — Instrumentation harden** | Coverage % on wall-clock/tokens/gen_model; audit path always stamps metric keys | B2, B8 | ✅ H2212 (forward + coverage UI) |
| **K7 — Calendar + idle fusion** | Heatmap idle-marked days (≥1h idle, 0 cards) | A12 | ✅ H2212 |
| **K8 — Cost honesty** | Sample-size badge on $/clean band | A11 | ✅ H2212 |

Also surfaced: gate exit=0 rate, fidelity aggregate, judge coverage, crash count (quality panel).

H2204 already shipped last idle, monthly idle days, spend split, equal lists — do not re-mint those.

---

## 6. Snapshot numbers that motivated this list (02-08-2026)

Local main checkout census (gitignored artifacts; not CI):

- Store: **11 603** senses / **254** roots; review sample-class: almost all `ai_translated`
- Verb: **48 / 749** promoted; **0** runnable; **701** blocked (rootmap)
- Ledger: **473** windows; states dominated by `needs_requeue` (350) and `stale_artifact` (108); only **3** `clean`
- Wall-clock minutes present on **12** rows only
- Idle gaps: **127** (kitchen); calendar still green-only for cards
- Economy: small priced probe sample → per-card band + H2204 absolute clean vs prep/redo
- Timeseries: **3–4** snapshot days → trends almost flat

---

## 7. Residual Grok queue (minted 03-08-2026)

K1–K8 UI is shipped (H2212). Remaining measurement gaps → **Grok 4.5** handoffs (execute in order; H2230 first):

| Order | ID | Effort | Title / gap |
|---|---|---|---|
| 1 | [H2230](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2230-Grok_SanskritLexicography_progress-kitchen-wallclock-token-dense_03.08.26.md) | hard | Dense wall-clock + tokens (B2 / K6 residual) — ✅ done: append_ledger already stamped `wall_clock_minutes`/`max_total_tokens` on every row (H2212) and a backfill script already existed (`backfill_ledger_metrics.py`, H2218 R4); the real gap was the blended `wall_clock_coverage_pct` conflating historical (pre-instrumentation, legitimately null) rows with post-cut ones — fixed by splitting `instrumentation_coverage()` into `post_cut`/`historical` buckets keyed on presence of a `wall_clock_source` field |
| 2 | [H2231](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2231-Grok_SanskritLexicography_progress-kitchen-gen-model-host-profile_03.08.26.md) | medium | gen_model / host / profile (B8) |
| 3 | [H2232](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2232-Grok_SanskritLexicography_progress-kitchen-true-cost-subscription_03.08.26.md) | medium | True $ / subscription units (B1) |
| 4 | [H2233](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2233-Grok_SanskritLexicography_progress-kitchen-verb-eta-roots-per-day_03.08.26.md) | medium | Verb ETA roots/day (K4 residual) |
| 5 | [H2234](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2234-Grok_SanskritLexicography_progress-kitchen-idle-reason-tags_03.08.26.md) | medium | Idle reason tags (B9) |
| 6 | [H2235](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2235-Grok_SanskritLexicography_progress-kitchen-review-throughput-series_03.08.26.md) | medium | Review throughput series (B5) |
| 7 | [H2236](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2236-Grok_SanskritLexicography_progress-kitchen-quality-timeseries_03.08.26.md) | hard | Quality timeseries (B4) |
| 8 | [H2237](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2237-Grok_SanskritLexicography_progress-kitchen-promote-vs-generate_03.08.26.md) | medium | Promote vs generate (B6) |
| 9 | [H2238](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2238-Grok_SanskritLexicography_progress-kitchen-nominal-burn-down_03.08.26.md) | medium | Nominal burn-down (B7) |
| 10 | [H2239](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2239-Grok_SanskritLexicography_progress-kitchen-article-parity_03.08.26.md) | medium | Article-site parity (B10) |
| 11 | [H2240](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2240-Grok_SanskritLexicography_progress-kitchen-health-probe-log_03.08.26.md) | medium | Canonical health_probe_log (B3 residual) — ✅ done (override dual-run, Sonnet 5 lane): `live_probe`'s `_emit` (`RussianTranslation/src/pilot/max_account_orchestrator.py`) now writes every probe reading straight into `output/health_probe_log.jsonl` alongside the existing per-account file; `kitchen_slices.health_ribbon` prefers that single canonical file exclusively when present, falling back to the old per-account glob scrape otherwise; `migrate_health_probe_log.py` folds pre-H2240 history in once, idempotently; pinned by `progress_dashboard/health_ribbon_selftest.py` |
| 12 | [H2241](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2241-Grok_SanskritLexicography_progress-kitchen-timeseries-slices_03.08.26.md) | medium | Kitchen slices in progress_timeseries |

**Starter (first residual):**

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H2230-Grok_SanskritLexicography_progress-kitchen-wallclock-token-dense_03.08.26.md and execute it.
```

Grok 4.5 (`grok-4.5`) · worktree off `origin/master` in SanskritLexicography.

_Dr. Mārcis Gasūns_
