# RussianTranslation — results log

_Created: 09-07-2026 · Last updated: 02-08-2026_

Append-only, reverse-chronological. Each entry: date, context, model tier, table.

## 02-08-2026 (H2190) — the cost table under-reported every 1 h cache write by 1.6×; repriced against the vendor's own figure

Opus 5 (`claude-opus-5`), [H2190](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2190-Opus_SanskritLexicography_pwg-cache-write-1h-pricing_02.08.26.md)
(executed inside [H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md)).
**Offline — 0 paid calls.** Every committed H2158 envelope repriced with
[`parse_workflow_cost`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py)
before and after the TTL split, checked against each envelope's own
`modelUsage.costUSD` — the vendor's number, not ours.

| envelope | 1 h write (tok) | output (tok) | flat-5 m $ (old) | TTL-aware $ (new) | billed $ (vendor) |
|---|---:|---:|---:|---:|---:|
| [`raw/liveness_clean`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2158/raw/liveness_clean.envelope.json) | 126 | 1 070 | 0.056525 | **0.056809** | 0.056809 |
| [`raw_slow/cli_nakzatra_1`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2158/raw_slow/cli_nakzatra_1.envelope.json) | 46 117 | 34 215 | 0.696736 | **0.800499** | 0.800499 |
| **total** | | | **0.753261** | **0.857308** | **0.857308** |

**The TTL-aware figure reconciles to the cent on both; the old one reconciles on
neither.** The gap is **$0.104047 = 12.1 % of the true bill**, and it ran in the
dangerous direction: every gate and projection computed from `PRICE` believed the
CLI lane cheaper than it is. Both envelopes report
`cache_creation.ephemeral_1h_input_tokens` with zero 5 m tokens, so this is not an
estimate — the bucket was in the data all along and the rate table had no field for it.

Fallback is deliberately asymmetric: TTL-less legacy envelopes stay on the 5 m rate
for **reporting** (so the $79.83 golden window and every pre-split figure are
unchanged), while **cost gates** pass `unknown_ttl='1h'` and fail closed, because an
under-refusal spends money and an over-refusal only asks a human to look.
[FINDINGS §289](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) ·
[PR #1032](https://github.com/gasyoun/SanskritLexicography/pull/1032).

## 02-08-2026 (H2174) — second consecutive c4 health NO-GO: the named stop fired, and this time *every* candidate gate number fails

Opus 5 1M (`claude-opus-5[1m]`), [H2174](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2174-Opus_RussianTranslation_medium50-presplit-live-run-after-health-pass_02.08.26.md)
(residual of [H2160](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2160-Opus_RussianTranslation_whole-card-b0-hang-and-medium50-completion_02.08.26.md)).
**2 paid calls (the health probe only), $1.0929. No canary, no window, no store write.**
H2174's own `Fail =` clause names "a second health NO-GO" as a terminal stop; it fired at
Step 1, so per the handoff nothing downstream was attempted — no re-roll, no re-warm, no
reaching for the friendlier number.

### The reading (run `…/2026-08-02T11:04:20Z-pid11056`)

| purpose | wall `elapsed_ms` | CLI `duration_ms` | `duration_api_ms` | `api_gap_ms` | class |
|---|---:|---:|---:|---:|---|
| warmup | 55 803 | 35 272 | 28 603 | 27 200 | success |
| **measured** | **96 520** | **77 966** | **69 137** | 27 383 | success |

Ceiling 65 000 ms. **All three candidate measured numbers exceed it** — 96 520 / 77 966 /
69 137.

### The finding: the open "which number gates?" question would not have unblocked this window

H2174 inherited an unresolved disagreement — [`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md)
prose says gate on `duration_api_ms`, `probe_log.derive_fails` gates on the measured wall
reading — and on the 02-08 07:49 H2160 run the two **disagreed on the verdict** (wall 75 561
NO-GO vs api 29 069 comfortable PASS). That made the ruling look like the unblocker.

It is not. On this reading the two **agree**, and so does the third number nobody had named
(the CLI's own `duration_ms`). This is the first measured c4 row where `duration_api_ms`
itself breaches the ceiling. Whichever way a human rules, **this** window was NO-GO. The
ruling is still owed — it governs future runs — but it is no longer load-bearing for the
question "was H2160's fix blocked by a mis-read gate?" It was not.

### Why that matters: c4 is intermittent, not down

The full per-account series (`h963_c4_gate0_probe_events.jsonl`, both the canonical and this
run's worktree copy, deduped by `(ts, run_id, purpose)`):

| # | date (UTC) | purpose | wall `elapsed_ms` | wall | `duration_api_ms` | api | `api_gap_ms` | class |
|---:|---|---|---:|---|---:|---|---:|---|
| 1 | 2026-07-22 14:57:34 | warmup | 21 280 | PASS | — | n/a | — | content |
| 2 | 2026-07-22 20:03:04 | warmup | 59 831 | PASS | — | n/a | — | success |
| 3 | 2026-07-22 20:04:47 | measured | 102 874 | NO-GO | — | n/a | — | auth |
| 4 | 2026-07-23 06:06:52 | warmup | 40 003 | PASS | — | n/a | — | success |
| 5 | 2026-07-23 06:09:40 | measured | 168 352 | NO-GO | — | n/a | — | success |
| 6 | 2026-07-24 04:23:53 | warmup | 10 838 | PASS | — | n/a | — | rate_limit |
| 7 | 2026-07-24 07:35:29 | warmup | 9 949 | PASS | — | n/a | — | rate_limit |
| 8 | 2026-07-25 03:16:04 | warmup | 17 587 | PASS | — | n/a | — | auth |
| 9 | 2026-07-25 03:18:34 | warmup | 10 918 | PASS | — | n/a | — | auth |
| 10 | 2026-07-25 16:02:31 | warmup | 17 878 | PASS | — | n/a | — | rate_limit |
| 11 | 2026-07-25 18:18:27 | warmup | 19 903 | PASS | — | n/a | — | rate_limit |
| 12 | 2026-07-31 18:59:59 | warmup | 94 606 | NO-GO | — | n/a | — | success |
| 13 | 2026-07-31 19:01:17 | measured | 78 415 | NO-GO | — | n/a | — | success |
| 14 | 2026-08-01 20:21:03 | warmup | 39 437 | PASS | 21 171 | PASS | 18 266 | success |
| 15 | 2026-08-01 20:21:53 | measured | 50 336 | PASS | 27 557 | PASS | 22 779 | success |
| 16 | 2026-08-02 05:47:17 | warmup | 55 390 | PASS | 37 690 | PASS | 17 700 | success |
| 17 | 2026-08-02 05:48:01 | **measured** | **43 815** | **PASS** | 26 386 | PASS | 17 429 | success |
| 18 | 2026-08-02 07:48:25 | warmup | 236 328 | NO-GO | 43 646 | PASS | 192 682 | success |
| 19 | 2026-08-02 07:49:40 | measured | 75 561 | NO-GO | 29 069 | PASS | 46 492 | success |
| 20 | 2026-08-02 11:05:16 | warmup | 55 803 | PASS | 28 603 | PASS | 27 200 | success |
| 21 | 2026-08-02 11:06:53 | **measured** | **96 520** | **NO-GO** | **69 137** | **NO-GO** | 27 383 | success |

Measured readings: **7**; wall PASS **2/7**; api PASS **3/4** of those carrying the field.

Three measured attempts today (rows 17, 19, 21) — **PASS, NO-GO, NO-GO**, spanning 43 815 →
96 520 ms wall on the same profile, same prompt, same ceiling, within 5¼ hours. So the route
is **not dead and not reliably healthy**: it is bimodal on a timescale of hours. Two further
consequences fall out of the table:

- **`api_gap_ms` — the in-CLI scaffolding overhead — is itself unstable**, 17 429 → 192 682 ms
  across the rows that carry it. H2160's "~45 % of a wall reading is scaffolding" is a
  property of *that* reading, not a constant, so wall and api cannot be related by a fixed
  correction factor. This is a second, independent reason the wall-vs-api ruling cannot be
  settled by arithmetic and needs a human.
- **The `--selftest`-able gate logic behaved exactly as specified.** Both readings were
  written to the append-only events log *before* the fail-closed exit, so this NO-GO leaves
  the same immutable trace as a PASS (the #729 discipline). Nothing here is a tooling defect.

### Also verified offline (no spend): the prepared artifacts are still pre-fix

`h2160_regen_medium50.py --dry-run` against the five prepared windows, read from the
canonical checkout (`src/pilot/output/` is gitignored, so a fresh worktree has none):

| window | `presplit_keys` on disk | n_batches | n_inputs |
|---|---|---:|---:|
| h1447-m50-w1 | `[]` | 3 | 3 |
| h1447-m50-w2 | `Srama, samIpa, vAhana, vfzwi` | 8 | 12 |
| h1447-m50-w3 | `rAzwra, vicitra, vyavasTA` | 7 | 11 |
| h1447-m50-w4 | `SoDana, aDastAt` | 8 | 11 |
| h1447-m50-w5 | `sAhasra` | 10 | 11 |

**10/48 keys presplit** — exactly H2160's "before" figure, confirming the artifacts on disk
predate the merged fix and that regeneration is a genuine prerequisite, not a precaution. The
fix (v1.134.0, presplit 10/48 → 44/48) therefore **remains merged and undemonstrated**, for
the second session running.

## 02-08-2026 (H2160) — `b0` was never non-terminating: it was killed BY US at exactly the ceiling, because a per-card presplit floor was masked by the batch budget

Opus 5 1M (`claude-opus-5[1m]`), [H2160](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2160-Opus_RussianTranslation_whole-card-b0-hang-and-medium50-completion_02.08.26.md).
**2 paid calls (the health probe only), $0.9459. No canary, no window, no store write** — the
live gate returned NO-GO before any translation call (below). The entire `b0` diagnosis below
is **offline**, from the two committed 02-08 ledgers plus the harness source.

### The `b0` verdict — three prior framings corrected

**1. `b0` is not a 3-key batch.** The handoff and the earlier entries assumed the whole-card
call batches all three w1 cards. The manifest says otherwise: w1 holds **three separate
1-key batches**, and `b0` is `nakzatra` **alone** — 80 citation-units, 5 495 B skeleton, 10
fragments. So "does a 1-key whole-card batch terminate?" was already answered by the data:
`b0` **is** the 1-key case. Batch size is not the variable.

**2. The `b0` kill is OUR kill, and it fires at exactly `KILL_CEIL_MS`.** A single-card batch
is granted the ceiling unconditionally — [`killBudgetForCur`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py),
`cur.length === 1 ? KILL_CEIL_MS : killBudgetMs(...)` — so `b0`'s budget IS the ceiling,
whatever the ceiling is set to. That is why it "converged on no bound":

| ceiling | `b0` died at | overshoot |
|---|---|---|
| 180 000 ms | 180 044 ms | +44 ms |
| 300 000 ms | 300 073 ms | +73 ms |

The overshoot is `setTimeout` dispatch latency, not provider behaviour. **`b0` has never been
allowed to run to completion, so it has never been observed to hang.** "Non-terminating" was
an inference from a gate that was re-firing at its own new value.

**3. It is not a whole-card-lane property at all — the heal lane hit the identical wall.** The
180 s run's full ledger, which the "heal works / whole-card hangs" framing was drawn from:

| # | detail | evaluable | wall ms |
|---|---|---|---|
| 1 | `translate b0` | NO | 180 044 |
| 2 | `heal:nakzatra#g1` | yes | 120 375 |
| 3 | `heal:nakzatra#g1.retry1` | NO | 180 041 |
| 4 | `heal:nakzatra#g2` | yes | 134 511 |
| 5 | `heal:nakzatra#g2.retry1` | NO | 180 040 |
| 6–8 | `heal:nakzatra#g3` · `#g4` · `#g5` | NO | 180 148 · 180 176 · 180 102 |
| 9 | `heal:nakzatra#g6` | yes | 132 042 |
| 10 | `heal:nakzatra#g6.retry1` | NO | 180 231 |
| 11–12 | `heal:nakzatra#g7` · `#g8` | NO | 180 138 · 180 076 |
| 13 | `translate b1` | NO | 180 134 |
| 14 | `heal:sarvatra#g1` | NO | 180 128 |
| 15 | `heal:sarvatra#g2` | yes | 164 266 |
| 16 | `heal:sarvatra#g2.retry1` | NO | 18 845 (run stopped) |

**11 of 16 calls died at 180 0xx–180 2xx ms, and only ONE of them was whole-card.** Five of
`nakzatra`'s eight heal groups and all three retries died on the same gate. The heal lane was
not working — it was succeeding 3 times in 11 and being read as healthy. Both lanes saturate
the ceiling because `killBudgetMs = 2·(20 000 + 45·B)` clamps to CEIL for any payload above
~1.6 KB (old ceiling) / ~2.9 KB (new): **every call in these windows runs on a flat ceiling
budget**, so the gate provides no differentiation and a ceiling change moves every death at once.

### Independently corroborated by H2011, from the opposite direction — and it bounds this fix

[H2011](#02-08-2026-h2011-at-the-old-180-s-ceiling--c4-gate-pass-canary-pass-and-the-first-per-card-observed-economics-on-the-production-route)
ran the same morning and reached the same place by spending instead of reading. Its decisive
control: **calls 2–4 were the *identical* fragment `rAtra_f0`, at 180.0 / 180.1 / 142.6 s
success.** Same input, same lane, same profile — three outcomes. Held against this entry's
finding that the deaths land at exactly `KILL_CEIL_MS` whatever it is set to, the two runs pin
the phenomenon between them:

> **The wall is our ceiling meeting a heavy right tail.** Not a lane (whole-card vs heal), not
> card size, not the provider hanging. A fixed ceiling clips the tail of a highly variable
> latency distribution, and moving the ceiling moves the clip.

`rAtra` is also the sharpest available check on card size: at **2 418 B it is the smallest real
card in the set**, and H2011 spent **682 755 ms and 4 calls** on it for one partial card. So the
morning's "16 calls, 0 cards" reproduces at the floor.

**This bounds the fix below.** Routing citation-heavy cards away from a doomed whole-card attempt
is worth doing — it stops paying ceiling-length calls for a card that was never going to fit —
but the fragments it routes them into are drawn from the same distribution, and H2011 measured a
~75 % kill rate on one small card's fragments. **The presplit correction is necessary, not
sufficient**, and it should not be reported as "the zero-card problem is fixed" until a window
lands cards. Two further consequences worth carrying: `rAtra` (33 units) is one of the four cards
this fix deliberately leaves whole-card, so those four are *below the citation threshold*, not
*proven safe*; and H2011's Step 1 PASS at **43 815 ms** sits ~23 minutes before this entry's
NO-GO at **75 586 ms** — a 1.7× swing in the gating number itself, which is the same variance
arriving in the gate.

### The actual defect: a per-card threshold masked by a per-batch one

`_presplit_hit` routed a card to the fragment lane when

```
(1 + <ls>) > max(OUTPUT_BUDGET, PRESPLIT_SOLO_CITE_FLOOR)      # 90 vs 40
```

`PRESPLIT_SOLO_CITE_FLOOR = 40` is a per-**card** fail-solo fact (its own comment: "well above
the whole-card-safe 34 and below the 150 giants"). `OUTPUT_BUDGET = 90` is a per-**batch**
packing cap. Taking the `max()` let the batch number mask the card number, so the floor was
inert at every default run — the source said so outright: *"For OUTPUT_BUDGET >= 40 (default 90)
nothing changes."*

w1's three cards sit exactly in the gap this opened:

| card | citation-units | skeleton B | fragments | > floor 40 | > budget 90 | presplit before | after |
|---|---|---|---|---|---|---|---|
| `nakzatra` | 80 | 5 495 | 10 | ✅ | ❌ | no | **yes** |
| `sarvatra` | 79 | 3 008 | 9 | ✅ | ❌ | no | **yes** |
| `sakft` | 75 | 3 318 | 12 | ✅ | ❌ | no | **yes** |

All three were above the threshold that says a card cannot be emitted whole, all three below
the unrelated batch cap — so `presplit_keys` came out `[]`, all three were attempted whole, and
all three whole-card attempts were killed at the ceiling. **A card is not made easier to emit
whole by raising the number of cards you would have liked to batch beside it.**

Fix: the citation trigger now compares against `PRESPLIT_SOLO_CITE_FLOOR` and nothing else
(`OUTPUT_BUDGET` remains the on/off switch for citation mode). RED-verified pin
`test_presplit_cite_floor_is_not_masked_by_batch_budget` — RED on pre-fix master with the exact
observed `PRESPLIT=[]`.

### Re-planning all five windows on the fixed predicate

Regenerated with [`h2160_regen_medium50.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2160_regen_medium50.py)
(same invocation the coordinator's `prepare` uses, every argument read back out of the existing
manifest; `config_dir_fingerprint` verified unchanged on all five):

| window | presplit before | presplit after | whole-card batches left | keys still whole-card |
|---|---|---|---|---|
| w1 | 0 | **3** | 0 | — |
| w2 | 4 | **12** | 0 | — |
| w3 | 3 | **9** | 1 | `rAtra` (33) · `spfS` (30) |
| w4 | 2 | **9** | 1 | `idAnIm` (36) · `prasU` (31) |
| w5 | 1 | **11** | 0 | — |
| **total** | **10 / 48** | **44 / 48** | **2** | 4 keys, all ≤ 40 units |

The boundary behaves: the only four cards still attempted whole are the only four scoring at or
below the 40-unit fail-solo floor. Gates: `window_selftest` **200/200** (199 baseline + the new
pin), `lang_parity_check` **90 entries, all verdicts complete, no drift** (52 entries re-stamped
— both touched files are hash-tracked; the one functional line changed is language-blind, so
every SHARED/INTENTIONAL-DIVERGENCE verdict stands on unchanged structural grounds).

### The live gate said NO-GO, so the fix is UNPROVEN in production

`/pwg-live-gate` Step 1, `h963_c4_gate0_probe.py`, run `…2026-08-02T07:44:28Z-pid35600`:

| purpose | wall ms | `duration_ms` | `duration_api_ms` | USD | classification |
|---|---|---|---|---|---|
| warm-up | 236 358 | 53 300 | 43 646 | $0.5953 | success |
| measured | **75 586** | 38 179 | **29 069** | $0.3506 | success |

`GATE-0 VERDICT: NO-GO` — measured 75 561 ms ≥ the 65 000 ms `STRICT_CEILING_MS`. Policy is
unambiguous ("STOP. No canary. No production window. No reroll."), so **no canary was built and
no translation call was made**; the c4-bound canary manifest the previous two windows lacked is
still not built, and that gap is now moot until health passes. The presplit route is therefore
**implemented and gated but not yet demonstrated live** — proving it needs one w1 window after a
fresh health PASS.

⚠️ **Gate prose and gate code disagree about which number gates, and it decided this run.** The
skill text says "Gate on `duration_api_ms`"; `probe_log.derive_fails` gates on the measured
**wall** reading. On this run wall 75 586 ms fails and `duration_api_ms` 29 069 ms passes
comfortably — the same reading is NO-GO or GO depending on which of the two the operator
believes. The measured NO-GO is recorded as the verdict and **was not overridden** (re-reading
the gate on the friendlier number would be weakening a guard to pass it). Filed as a residual,
not fixed here.

⚠️ The 02-08 whole-card cost figures elsewhere in this log stand, but note the corrected
attribution: a `b0` "hang" is a call **we abandoned**, so its cost is billed and unrecoverable
while contributing $0 to the ledger (issue [#949](https://github.com/gasyoun/SanskritLexicography/issues/949)).
Raising the ceiling raised that waste per dead call from 180 s to 300 s without changing any outcome.

## 02-08-2026 (300 s re-run) — the ceiling relaxation is VALIDATED for the heal lane and REFUTED for the whole-card lane

Opus 5 1M (`claude-opus-5[1m]`), run `h1447-m50-2026-08-02b` on c4 after
[v1.128.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.128.0) raised the
per-call ceiling 180 s → 300 s and the five prepared artifacts were re-budgeted. **Run stopped
externally after 4 calls**, so w1 is incomplete — but the calls it did make settle the question.

### Same two calls, both ceilings

| call | 180 s run | 300 s run | verdict |
|---|---|---|---|
| `translate b0` | killed at **180 044 ms** | killed at **300 073 ms** | **hangs at ANY ceiling** |
| `heal:nakzatra#g1` | 120 375 ms ✓ | 82 459 ms ✓ | completes; huge variance |
| `heal:nakzatra#g2` | 134 511 ms ✓ | **176 952 ms ✓** | **3 048 ms of margin under the old ceiling** |

**Validated for the heal lane.** `g2` returning at 176 952 ms is the proof: under the old
180 000 ms bound that call had **three seconds** to spare. Across the two runs the same heal
groups ranged 82–120 s and 134–177 s, so the lane's upper tail was being systematically killed
by a ceiling it had outgrown — exactly the failure the relaxation targeted.

**Refuted for the whole-card lane, and this corrects the earlier entry's framing.** The
180 s-run diagnosis read "12 of 16 calls die at the ceiling" as "the ceiling is slightly too
tight". For `b0` that is false: it died at 180 044 ms and then at 300 073 ms, converging on
neither. It is a **non-terminating call**, and for that lane a higher ceiling strictly
*increases* waste — 300 s burned per dead attempt instead of 180 s. The whole-card hang is a
separate, still-unfixed defect and should not be filed under the ceiling fix.

Cost: `g2` alone billed **$0.8850**; 646 904 tokens across the 2 evaluable calls; recorded floor
$1.3182 with `cost_evaluable=false` (one 300 s dead call contributes 0).

⚠️ Raw ledger is gitignored (`.gitignore:67`) — this table is the only committed copy.

## 02-08-2026 (H2011, at the OLD 180 s ceiling) — c4 gate **PASS**, canary **PASS**, and the first per-CARD observed economics on the production route

Opus 5 1M (`claude-opus-5[1m]`), [H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md)
via [/pwg-live-gate](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md)
then [/pwg-bounded-run](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md).
**8 paid calls total** (2 gate + 1 canary + 5 window), **no promotion, no store write, no TM
mutation, no constant moved.** Run from worktree `SL-h2011-15072` off `origin/master`
[`64a4fa62`](https://github.com/gasyoun/SanskritLexicography/commit/64a4fa62).

⚠️ **Ceiling context:** this window ran at `HARD_TIMEOUT_MS = 180000`, i.e. **before**
[v1.128.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.128.0) raised it to
300 s. Read alongside the 300 s re-run entry above — the two agree and each supplies what the
other lacks. That entry shows `translate b0` dying at **both** 180 044 and 300 073 ms (a
non-terminating call, not a tight ceiling); this one shows the *heal* lane's kills are pure
variance, with the identical fragment failing twice and then finishing in 142.6 s. Together:
**raise the ceiling for the heal lane, and stop filing the whole-card hang under "ceiling".**

### Step 1 — health, `h963_c4_gate0_probe.py`, run `…2026-08-02T05:46:22Z-pid25748`

| purpose | wall `elapsed_ms` | `duration_api_ms` | `api_gap_ms` | ceiling | class |
|---|---|---|---|---|---|
| warm-up | 55 390 | 37 690 | 17 700 | 65 000 | success |
| **measured** | **43 815** | **26 386** | **17 429** | 65 000 | success |
| *(prior, 01-08)* | 50 336 | 27 557 | 22 779 | 65 000 | success |

**GATE-0 VERDICT: PASS** — measured 43 815 ms is 1.48× under the ceiling and the **fastest
decomposed** c4 reading on record. `api_gap` has now been ~17–23 s across three consecutive
uncontaminated readings, i.e. the non-API overhead is **stable**, not drifting.

### Step 2 — canary `dq_canary_puregloss~~h0_zz_pw`, manifest v2, headless CLI, ONE call

Manifest built by the canonical builder ([`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
`--nominal --no-grammar --manifest-out`), **never hand-written** — so the prompt is production's
own (preamble 1 226 ch + translation 12 423 ch), which is the H2011 trap this avoids.
`validate_manifest(require_v2=True)` OK, live `config_dir_fingerprint` match, sha256
`47e10d4b…5ce2`.

| axis | value |
|---|---|
| wall clock | **121 693 ms** (68 % of the 180 000 ms `HARD_TIMEOUT_MS`) |
| classification | `success`, 0 null, 0 heal, 0 budget stops |
| senses | **3/3** rendered |
| audit ([`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) `--ephemeral`) | 1/1 clean, 0 requeue; SAN-LOSS sense-count **PASS**, sense-dupe **PASS**, ru_style **PASS**, coverage 1/1 |
| `observed_cost_usd` | **$0.8660853**, `cost_evaluable: true` |

**`gate_reason = LIVE_GO`, `verdict = GO`** — derived mechanically, not asserted.

### The cost decomposition reproduces to the seventh decimal — a third independent confirmation

| component | tokens | list rate | cost | share |
|---|---|---|---|---|
| **cache creation** | **106 072** | $6/M | **$0.636432** | **73.5 %** |
| cache read | 380 511 | $0.30/M | $0.114153 | 13.2 % |
| output | 7 698 | $15/M | $0.115470 | 13.3 % |
| input | 10 | $3/M | $0.000030 | 0.0 % |
| **total** | | | **$0.8660853** | vs recorded **$0.8660853** |

So [PR #986](https://github.com/gasyoun/SanskritLexicography/pull/986)'s ~71 % (a heal call) and
[PR #994](https://github.com/gasyoun/SanskritLexicography/pull/994)'s 87.6 % (a trivial ping) are
now joined by **73.5 % on a real, schema-carrying, single-card translation** — the one call class
none of the earlier probes covered. The finding is not an artefact of trivial payloads.

### The preflight cost model is 5.8× low on a real card

[`perf_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py)
projected **$0.15** for this exact key; the ledger recorded **$0.8661**. That is a **5.8×**
underestimate, sharper than the 4.7× recorded against `PER_AGENT_USD_HEALTHY = 0.113` in
[issue #949](https://github.com/gasyoun/SanskritLexicography/issues/949) — and it is measured on
one card, with `cost_evaluable: true`, so it is not the missing-telemetry class.

⚠️ **n = 1 card.** This is an observed per-card figure, not a campaign rate. ⚠️ The worker records
`elapsed_ms` only, so the canary's wall clock is **not** decomposable into API vs overhead the way
the gate rows are.

### Soft advisory, reported because it is not zero

The canary card came back with the `{%…%}` gloss wrapper **dropped on all three senses**
(`markup_wrapper_dropped` ×3, `high_confidence=0`). Classified low-severity by
[`prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)
— meaning intact, wrapper gone — so it never blocks the gate, and the canary's own gate (the
SAN-LOSS sense-count guard) passed. Noted because [PR #789](https://github.com/gasyoun/SanskritLexicography/pull/789)
ruled `{%…%}` the store's documented convention and a dropped wrapper drift, not an alternative.

### Step 3 — the bounded one-card-per-call window: 5 calls, 1 partial card, 4 kills at the wall

3 real cards (`rAtra` 2 418 B · `divA` 2 993 B · `SvAsa` 11 480 B), `--output-budget=1`,
`--max-agents 5 --max-calls 5 --timeout 180`, driven straight through
[`headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
on the validated nominal manifest. **5 paid calls. No promotion, no store write** — the audit ran
`--ephemeral`.

| # | call | keys | rc | wall | class |
|---|---|---|---|---|---|
| 1 | `b0` (whole-card translate) | `rAtra` | 124 | **180 025 ms** | timeout |
| 2 | `heal:rAtra#g1` | `rAtra_f0` | 124 | **180 020 ms** | timeout |
| 3 | `heal:rAtra#g2` | `rAtra_f0` | 124 | **180 072 ms** | timeout |
| 4 | `heal:rAtra#g3` | `rAtra_f0` | 0 | **142 638 ms** | **success** |
| 5 | `heal:divA#g1` | `divA_f0..f2` | 124 | **180 100 ms** | timeout |

Result: `completed_with_residuals` — **1 of 3 cards**, and that one only **partial**.
`divA` → `timeout`, `SvAsa` → `budget_exceeded:heal` (never reached). `kill_timeouts: 4`,
`conn_errors: 0`, `budget_stops: 2`.

**The single most useful number here: `rAtra`, the smallest real card in the input set, cost
682 755 ms — 11.4 minutes — and 4 calls to yield one partial card.** The 02-08 morning run's "16
calls, 0 cards" was not a big-card problem; it reproduces at the floor.

**But the wall is a variance problem, not a size problem, and that is new.** Calls 2, 3 and 4 are
the *identical* fragment `rAtra_f0`. Two died at 180 s; the third finished in **142.6 s**. The work
fits inside the ceiling — the ceiling just clips a heavy right tail. So "the lane cannot finish"
is too strong: what is true is that a fixed 180 s wall turns a long-tailed latency distribution
into a ~75 % kill rate, and each kill costs a full call.

### Failure-class composition — the axis H1940 Phase 2 was supposed to move

| class | count | detail |
|---|---|---|
| **defect** (real content failure) | **0** | — |
| transient (cheap re-run) | 3 | `rAtra` (partial), `divA`, `SvAsa` |
| null reasons | 2 | `timeout` ×1, `budget_exceeded` ×1 |

**This is the before/after result MG asked for, and it is a pass on the axis that was actually
worked.** [PR #911](https://github.com/gasyoun/SanskritLexicography/pull/911) and predecessors were
durability and classification work, not speed work — and every failure in this window is
classified `transient`/`budget_exceeded`, **none misfiled as a content defect** (the H2a/H2b class),
with no hot-spin, no stranded cohort and no lost checkpoint. Throughput did not improve, exactly as
the handoff predicted it might not; correctness of attribution did.

### Cost: the ledger under-reports this window ~5×

| field | value |
|---|---|
| `observed_cost_usd` | **$0.6206808** |
| `cost_evaluable` | **false** |
| `priced_calls` / `missing_usage_calls` | 5 / **4** |
| tokens (the one priced call) | in 6 · out 8 702 · cache read 208 636 · **cache create 71 257** |

The recorded figure is the **one successful call**; the four kills return no envelope, so
[`unevaluable_telemetry()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py)
books them as zero. Real spend is ≈5× the recorded number. The priced call again decomposes to the
cent — 71 257 × $6/M + 208 636 × $0.30/M + 8 702 × $15/M + 6 × $3/M = **$0.6206808** vs recorded
**$0.6206808** — with **cache creation at 68.9 %**. That is the third call class in one day
(heal 71 %, ping 87.6 %, canary 73.5 %, this heal 68.9 %) where the dominant charge is
payload-independent scaffolding.

⚠️ **Do not scale this to the campaign.** n = 3 cards, 1 completed, on one profile in one hour.
A projection would multiply a 4-call-per-card figure that is itself a variance artefact.

### And the shape finding, free from the build

At `--output-budget=1`, `divA` (47 `<ls>`) and `SvAsa` (82 `<ls>`) **exceed the budget and route to
direct fragment translation** before any call is made. So "one card per call" is one call only for
small cards; citation-heavy cards expand into the presplit/heal lane, which is where 4 of these 5
calls went. Option A in [H2152](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2152-Opus_RussianTranslation_c4-quota-call-shape-audit_02.08.26.md)
§4 is therefore not a one-call-per-card lane in practice, and its per-card attribution is diluted
by exactly the fragment groups the ledger cannot price.

**First attempt, same window, blocked and recorded:** an earlier launch was refused before any paid
call with `classification: configuration`, `profile already has an active model call` — the
kernel-backed `ActiveCallClaim` on the c4 fingerprint was held by a **concurrent live session**.
Zero spend; the R9 guard did exactly its job.

### The `h1339_offline_bench` byte-identity control is STALE

H2011 names `9bd2a14297` as the control that must be unchanged. It does not reproduce:

| commit | date | interpreter | signature |
|---|---|---|---|
| [`64a4fa62`](https://github.com/gasyoun/SanskritLexicography/commit/64a4fa62) (HEAD) | 02-08 | 3.14.4 | `586d012b3d` |
| [`a75eaa17`](https://github.com/gasyoun/SanskritLexicography/commit/a75eaa17) | 31-07 | 3.14.4 | `586d012b3d` |
| [`a75eaa17`](https://github.com/gasyoun/SanskritLexicography/commit/a75eaa17) | 31-07 | 3.12 | `586d012b3d` |
| [`005d2f0f`](https://github.com/gasyoun/SanskritLexicography/commit/005d2f0f) | 30-07 | 3.14.4 | `586d012b3d` |

`a75eaa17` is the **very commit** whose close-out recorded "signature `9bd2a14297` unchanged".
Fixture content hash `569660c689d0659b`, 24 files, untouched since 25-07-2026; the bench still
reports `deterministic outputs: True (1 signature)` and identical fx1–fx5 outcomes. So determinism
holds and the *relative* control still works — what is broken is the **documented absolute value**,
which has been carried forward in prose across at least three commits without reproducing. A
byte-identity control nobody can reproduce is not a control.

## 02-08-2026 (later still) — the cache prefix is UNSTABLE, not expiring: a second identical call re-creates what the first just wrote

Opus 5 1M (`claude-opus-5[1m]`), follow-on to the H2152 audit. **4 paid calls, $1.0469, no
window, no store write.** Tool: [`src/pilot/cache_prefix_stability_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_prefix_stability_probe.py) (new).

[#986](https://github.com/gasyoun/SanskritLexicography/pull/986) left two candidates for why every
call re-creates 56–68 k tokens of cache: **(a)** the prefix is not stable across `claude -p`
invocations, or **(b)** the TTL lapses between 2–3-minute calls. **It is (a). (b) is refuted.**

Identical `claude -p --max-turns 1` calls, ~30 B prompt, output 4 tokens, back-to-back:

| arm | # | wall ms | `duration_api_ms` | cache **create** | cache **read** | USD |
|---|---|---|---|---|---|---|
| repo cwd | 1 | 26 262 | 2 995 | **49 153** | 28 882 | $0.3036 |
| repo cwd | 2 | 29 087 | 2 813 | **49 165** | 28 882 | $0.3037 |
| bare cwd | 1 | 20 401 | 2 193 | 37 814 | 28 882 | $0.2356 |
| bare cwd | 2 | 19 057 | 2 624 | **32 261** | **34 435** | **$0.2040** |

**(b) is dead on arithmetic.** Every write went to `ephemeral_1h_input_tokens` (`5m` = 0), and a
**1-hour** TTL cannot lapse between calls issued seconds apart. Two identical repo-cwd calls
re-created **49 153 → 49 165** tokens — the second re-wrote what the first had just written, with
cache read pinned at 28 882 both times. **Nothing carried over at all.**

**The prefix decomposes cleanly:** a stable cached core of **~29 k** that reads every time, plus a
**volatile ~49 k** segment that is re-written every time. In a bare cwd the volatile segment shrinks
to ~32–38 k, and bare #2 shows the only cross-call reuse in the whole run — read **+5 553**, create
**−5 553**, exactly complementary. So **project-context injection (CLAUDE.md + git state) is what
breaks the prefix**, and it is worth ~11–17 k tokens per call.

### The free win, measured

Running the lane from a **bare cwd** instead of the repo:

| | repo cwd | bare cwd | delta |
|---|---|---|---|
| cost/call | $0.3036 | $0.2040 | **−33 %** |
| wall/call | 26–29 s | 19–20 s | **−30 %** |
| `duration_api_ms` | 2 813–2 995 | 2 193–2 624 | −13 % |

Zero code change, no guard weakened, no ceiling moved.

### What it means for scaling

With `--max-turns 1` the floor is visible: **~19–29 s of every call is non-API overhead against
~2–3 s of actual API time**, and **~32–49 k tokens are re-written per call regardless of payload**.
At $6/M that fixed write **is** the ~$0.30, i.e. it is the entire cost of a call that translates
nothing. A one-shot CLI subprocess **cannot amortise its own system prompt** — each invocation is a
cold process paying a fresh cache write, which is structural to the route, not a tuning knob.

The equivalent stable prefix on the Messages API would be a **cache read of ~15 k at $0.30/M ≈
$0.0045/call** — roughly **65× cheaper** on the fixed component. That is the scaling lever, and it
also dissolves the 180 s subprocess ceiling, [§270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)'s
hang-instead-of-429, and [§273](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)'s destroyed
rate-limit signal in one move. Ported under
[H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md).

⚠️ These are 4-token-output calls; they isolate the **fixed** overhead and say nothing about
per-card translation cost. ⚠️ The 65× figure is an estimate from list rates and an assumed ~15 k
prefix, not a measurement — H2158 must measure it.

## 02-08-2026 (later) — H2152 call-shape audit: quota is not binding; wall clock is

Opus 5 1M (`claude-opus-5[1m]`), [H2152](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2152-Opus_RussianTranslation_c4-quota-call-shape-audit_02.08.26.md),
audit only — **1 paid call, no gate run, no window, no store write, no constant moved.**
Full memo: [`pwg_ru/h2152/AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2152/AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md).

### Same-moment quota/route ping — `claude -p --model claude-sonnet-5`, ~30 B prompt, c4

| field | value |
|---|---|
| wall clock | 58 765 ms |
| `duration_api_ms` | 13 110 ms |
| derived `api_gap_ms` | **45 655 ms (78 % of wall)** |
| `cache_creation_input_tokens` | **50 450** (one call) |
| `cache_read_input_tokens` | 107 416 |
| `input_tokens` / `output_tokens` | 4 / 713 |
| `total_cost_usd` | **$0.3456** |
| `num_turns` | 5 |

**Verdict: NOT rate-limited.** A throttled CLI hangs without returning ([FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md));
this returned a real envelope. Free `claude auth status --json` also green (`loggedIn`, `max`) —
but that proves credentials, **not** quota: it read the same on 31-07 during the throttle.

⚠️ The ping ran an agentic loop in a repo cwd (`num_turns: 5`), so the 45.7 s gap includes four
inter-turn round trips and is an **upper bound**, not a clean startup figure. The directly
comparable numbers are the 01-08 gate readings on schema-carrying prompts (`api_gap` 18 266 /
22 779 ms, ~45 % of wall). The **token** figures are payload-independent and need no discount.

### Call-shape verdict

| Option | Quota load | Wall-clock load | Viable today |
|---|---|---|---|
| A. one card per call (`--output-budget=1`, already implemented) | worst | **best** | **yes** |
| B. multi-card batch (`OUTPUT_BUDGET=90`, today's default) | best | worst | **no** — successes already at 67 %→91 % of the 180 s budget |
| C. hybrid | middle | middle | **no** — its bulk half is B |

**HOLD one-card, and stop treating call shape as the lever.** The two ceilings pull in opposite
directions and only one binds at a time; today it is wall clock, so the small shape is correct —
MG's instrument-everything mandate and §270 are not in conflict right now. But neither shape
fixes the current failure: single-fragment heal calls already time out, so there is no smaller
shape left. The levers are the `HARD_TIMEOUT_MS` ruling (human), the **per-call cache
re-creation** (below), and [#949](https://github.com/gasyoun/SanskritLexicography/issues/949).

### The ping prices out exactly — independent corroboration of the cache-creation finding

The [#986](https://github.com/gasyoun/SanskritLexicography/pull/986) correction landed the same
night on a *heal* call (cache creation ~71 % of cost). The same arithmetic on this ping — a
different call class, a trivial 30 B prompt with no translation work — reproduces the ledger to
the fourth decimal:

| component | tokens | list rate | cost |
|---|---|---|---|
| cache creation | 50 450 | $6/M | **$0.3027** |
| cache read | 107 416 | $0.30/M | $0.0322 |
| output | 713 | $15/M | $0.0107 |
| input | 4 | $3/M | $0.00001 |
| **total** | | | **$0.3456** vs recorded **$0.3456318** |

**Cache creation is 87.6 % of the cost of asking for one word.** The dominant per-call charge is
entirely payload-independent — not a translation cost, and not something a smaller shape can
avoid. Since writing ~50–60 k tokens also costs wall clock, this is the one lever that attacks
both the 4.7× cost overrun and the 180 s wall without touching the 3-minute ruling.

**Premise corrected:** the "~90 k cache-creation per call" figure carried by H2011/H2152 is a
**two-call aggregate**. Per call it is ~45–50 k ([`perf_preflight.py:55–67`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py#L55)
already says ~45 243; this ping measures 50 450). The amortisation prize from batching is **half**
what both handoffs assumed.

**Attribution amplification, previously unrecorded:** [`call_reservation.py:378`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py#L378)
propagates `cost_evaluable=False` from one call to the whole record, so under a batch of N a
single unevaluable call destroys attribution for **all N** cards. At the 02-08 run's 12/16 rate
that is a first-class argument for one-card, independent of wall clock.

## 02-08-2026 — medium50 w1 aborted: the heal lane cannot finish inside its own 3-minute ceiling

Opus 5 1M (`claude-opus-5[1m]`), live paid run on c4 (`h1447-m50-2026-08-02`), **16 calls,
run stopped by the operator after 2 of 3 keys, ZERO cards produced**. The first paid PWG→RU
attempt since 25-07-2026. Health gate had PASSed the same night (entry below); the Step 2
canary was **not** run, so this window ran on a half-satisfied gate.

### Per-call timeline (`src/pilot/reservation_timeline.py`, new)

| bucket | n | min | median | max |
|---|---|---|---|---|
| evaluable | 4 | 120 375 ms | 134 511 ms | 164 266 ms |
| **UNEVALUABLE** | **12** | 18 845 ms¹ | **180 128 ms** | **180 231 ms** |

¹ the single sub-ceiling row is the in-flight call killed by the operator stop.

**Every other unevaluable call landed at 180 04x–180 23x ms — `HARD_TIMEOUT_MS = 180000`, hit
to the millisecond.** This is a hard-timeout wall, not the FINDINGS §270 rate-limit hang (a
throttled CLI hangs *without* returning; these were killed by our own ceiling) and not content
failure. Route health was fine, exactly as the gate measured.

### Why it cannot be tuned away at the group level

The heal groups are **already at the floor** — splitting further is arithmetically impossible:

| key | groups | fragment sizes |
|---|---|---|
| `nakzatra` | 8 | 1, 1, 1, 1, 1, 1, 2, 2 |
| `sarvatra` | 7 | 1, 1, 1, 1, 1, 1, 3 |
| `sakft` | 6 | 1, 1, 1, 1, 1, 7 |

Six of `nakzatra`'s eight groups hold a **single fragment**, and single-fragment heal calls
still time out. The whole-card batches `b0` and `b1` timed out too, so it is not lane-specific.
The cost is per-call overhead, not content: one heal call for **one fragment** billed
**199 370 tokens in total**. Lowering `SELFHEAL_GROUP_BUDGET` therefore cannot fix this.

> **Correction (same day, same session).** An earlier revision of this entry called that
> figure "199 370 **subagent** tokens", implying subagent scaffolding. That is wrong and it
> points at the wrong remedy. `call_reservation.py:92` computes
> `values['subagent_tokens'] = sum(values.values())` — the field is the **sum of the other
> four token fields** under a legacy misnomer, and `economy_ledger.py:35-37` already
> documents it as "the blunt `subagent_tokens` totalTokens". **No subagents are involved.**
> The real composition is in *Where the money actually goes* below.

### The margin is gone, and shrinking

Successful calls: 120.4 s → 132.0 s → 134.5 s → **164.3 s**, i.e. 67 % → **91 %** of the 180 s
budget. Any call above the median dies. That is the mechanical answer to H818's owner brief
("1 month, nothing works, I want to start translating").

### Spend

`observed_cost_usd` = **$2.1543** with `cost_evaluable=false` — a **floor, not the spend**
([#949](https://github.com/gasyoun/SanskritLexicography/issues/949)). The 12 unevaluable calls
were real paid spawns that each burned up to a full 180 s of compute and contributed
**0** to that total. 609 106 tokens are billed across the 4 evaluable calls alone
(~152 k each). **75 % of the calls, and the majority of real spend, produced nothing.**

Measured per-call cost on the evaluable calls is **~$0.53**, against the `PER_AGENT_USD_HEALTHY
= $0.113` that `perf_preflight` prices windows with — 4.7×. The preflight put w1 at $0.46.

### Where the money actually goes — cache creation is ~71 % of every call

| call | in | out | cache_read | **cache_creation** | usd |
|---|---|---|---|---|---|
| `heal:nakzatra#g1` | 4 | 7 902 | 127 604 | **63 860** | 0.5400 |
| `heal:nakzatra#g2` | 2 | 11 335 | 35 590 | **56 379** | 0.5190 |
| `heal:nakzatra#g6` | 2 | 8 348 | 35 597 | **56 308** | 0.4738 |
| `heal:sarvatra#g2` | 4 | 11 791 | 126 595 | **67 785** | 0.6216 |

Pricing `g1` out at list rates reproduces the recorded figure exactly: cache_creation
63 860 × $6/M = **$0.383** · cache_read 127 604 × $0.30/M = $0.038 · output 7 902 × $15/M =
$0.119 → **$0.540** against a recorded `0.5399832`.

**Every call re-creates 56–68 k tokens of cache**, billed at the premium write rate, and that
is **~71 % of the call's cost**. The framework prompt is being written to cache on each
invocation instead of amortised across them — note `g2`/`g6` read only ~35.6 k while still
creating ~56 k. Since writing ~60 k tokens also costs wall-clock, this is the one lever that
attacks **both** the cost overrun and the 180 s timeout wall **without** touching the
`"NOTHING runs past 3 min (MG)"` ruling. Untested hypothesis, stated as such: the cache prefix
is not stable across `claude -p` invocations, or the TTL lapses between 2–3 minute calls.

⚠️ `HARD_TIMEOUT_MS` carries an explicit standing ruling in code — `"NOTHING runs past 3 min
(MG)"` (R4/C-15) — so raising the ceiling is a human decision, not a tuning fix. The open
options are all human: relax that ruling, cut per-call overhead (the ~25–30 k framework prompt
plus subagent scaffolding), or accept partial cards.

⚠️ Raw ledger is gitignored (`.gitignore:67`); this table and the timeline tool are the only
committed record.

## 01-08-2026 (later) — the first decomposed c4 readings; c4 auth restored

Opus 5 1M (`claude-opus-5[1m]`), live `/pwg-live-gate c4` Step 1 only — **2 paid calls, no
canary, no bounded window, no store write.** Directly supersedes the "no reading is
decomposable" finding in the H2118 entry immediately below: the H2095 instrumentation has now
produced rows.

**Context.** The paid lane had been stopped since 25-07-2026 on HTTP 403 across every profile.
A free `claude auth status --json` on the c4 config dir now returns `loggedIn: true`,
`authMethod: claude.ai`, `subscriptionType: max` — **the 403 blocker is cleared.**

### `h963_c4_gate0_probe.py`, run `…2026-08-01T20:20:23Z-pid5664`, model `claude-sonnet-5`

| purpose | wall `elapsed_ms` | `duration_api_ms` | `api_gap_ms` | ceiling recorded | policy | class |
|---|---|---|---|---|---|---|
| warm-up | 39 437 | **21 171** | 18 266 | 65 000 | `production_v2` | success |
| measured | 50 336 | **27 557** | 22 779 | 65 000 | `production_v2` | success |
| *(prior, 31-07)* | 78 415 | *absent* | *absent* | *absent* | `production_v1` | success |

Prompt 6 828 B (≥ 5 KiB floor), schema-carrying; wall clock 89.8 s; zero connection errors.

**Why this matters for [#946](https://github.com/gasyoun/SanskritLexicography/issues/946) /
H2138.** These are the first rows in the series carrying `duration_api_ms`, so for the first
time a c4 reading can be split into route time and in-CLI overhead:

- **Real API time is 21.2 s / 27.6 s — both under the 30 000 ms `STRICT_CEILING_MS` that the
  `/pwg-live-gate` skill text still names.** The wall readings fail that bar; the API readings
  pass it. The gap is **18.3 s / 22.8 s — about 45 % of each wall reading** — which is exactly
  the conflation Q1-F4 said made wall-clock gating unable to mean anything.
- **This is not a masked rate-limit.** Per [FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
  a throttled CLI hangs rather than answering; both calls returned `classification=success`
  with real envelopes inside the ceiling. The gap is process/startup scaffolding, not backoff.
- The verdict PASSed on the code's 65 000 ms ceiling, but **it did not need the widened
  ceiling** — it passes the stricter 30 000 ms bar too, once measured on the axis that means
  something. That is evidence for the H2138 re-derivation, though **not** the ≥5 paired
  readings it requires: this is n=1 measured (plus 1 warm-up), taken without the same-moment
  quota check §270 calls for.

⚠️ **The raw rows live only in `src/pilot/output/h963_c4_gate0_probe_events.jsonl`, which is
gitignored** (`.gitignore:67`, `RussianTranslation/src/pilot/output/`). This table is the only
committed copy — the same durability gap that let the whole pre-H2095 c4 series become
undecomposable in the first place.

## 01-08-2026 — H2118: the c4 probe-latency evidence base, and why no ceiling was derived

Opus 5 1M (`claude-opus-5[1m]`),
[H2118](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2118-Opus_RussianTranslation_rederive-probe-latency-ceiling-946_01.08.26.md),
issue [#946](https://github.com/gasyoun/SanskritLexicography/issues/946). **Zero paid calls.**
Full report:
[H2118_PROBE_CEILING_PROVENANCE_2026-08-01.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2118/H2118_PROBE_CEILING_PROVENANCE_2026-08-01.md).

### Every c4 probe reading on record (13 rows, `output/h963_c4_gate0_probe_events.jsonl`)

**None carries `duration_api_ms`** — the H2095 instrumentation this mission was built to consume
has never produced a single row, so no reading anywhere is decomposable into route time vs the
retry backoff [FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) identified.

| # | timestamp (UTC) | purpose | `elapsed_ms` | classification |
|---|---|---|---|---|
| 1 | 2026-07-22T14:57 | warmup | 21 280 | content |
| 2 | 2026-07-22T20:03 | warmup | 59 831 | success |
| 3 | 2026-07-22T20:04 | measured | 102 874 | auth |
| 4 | 2026-07-23T06:06 | warmup | 40 003 | success |
| 5 | 2026-07-23T06:09 | measured | 168 352 | success |
| 6 | 2026-07-24T04:23 | warmup | 10 838 | rate_limit |
| 7 | 2026-07-24T07:35 | warmup | 9 949 | rate_limit |
| 8 | 2026-07-25T03:16 | warmup | 17 587 | auth |
| 9 | 2026-07-25T03:18 | warmup | 10 918 | auth |
| 10 | 2026-07-25T16:02 | warmup | 17 878 | rate_limit |
| 11 | 2026-07-25T18:18 | warmup | 19 903 | rate_limit |
| 12 | 2026-07-31T18:59 | warmup | 94 606 | success |
| 13 | 2026-07-31T19:01 | measured | 78 415 | success |

### Derived distribution — the ceiling clears only 2 of 5 successes

| statistic | value |
|---|---|
| `success` readings | 5 of 13 |
| success band | 40 003 – 168 352 ms |
| success median | 78 415 ms |
| **clear the 65 000 ms ceiling** | **2 of 5** (40 003 · 59 831) |
| **exceed it** | **3 of 5** (78 415 · 94 606 · 168 352) |
| `rate_limit`-classified | 4 of 13, band 9 949 – 19 903 ms |

The four readings cited in the constant's own justification (52 815 · 104 870 · 31 623 · 47 953)
live in the H963/H994/H1447 gate reports, **not in this log** — the two populations barely
overlap, and neither is decomposable. A reading is also not self-certifying: rows 11 and 13 are
the same account, minutes apart, at 19 903 ms `rate_limit` and 78 415 ms `success`.

### Gate ceilings before and after

| site | before | after | mechanism |
|---|---|---|---|
| `probe_log.POLICIES['production_v1']` | 30 000 | 30 000 | frozen — historical rows were judged here |
| `probe_log.POLICIES['production_v2']` | — | 65 000 | **new**; what the live gates stamp |
| `max_account_orchestrator.PROBE_LATENCY_CEILING_MS` | 65 000 hard-coded | 65 000 **derived** | `probe_log.ceiling_for()` |
| `coordinator.PROBE_LATENCY_CEILING_MS` | 65 000 hard-coded | 65 000 **derived** | `probe_log.ceiling_for()` |
| `h963_c4_gate0_probe.CEILING_MS` | derived from orchestrator | unchanged | transitively one table |

**The value did not move.** What moved is that a 50 000 ms reading no longer passes one gate and
fails the other under one policy name. Gates: `window_selftest` 198/198,
`max_account_orchestrator_selftest` PASS, `execution_contract_selftest` PASS.

## 30-07-2026 — H1910: Jamison–Brereton 2014 as the fifth column, Renou EVP as a witness

Opus 5 1M (`claude-opus-5[1m]`),
[H1910](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1910-Opus_RussianTranslation_rv-jamison-brereton-renou-fifth-witness_29.07.26.md).
J–B extracted by [`src/rv_jamison_brereton_extract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_jamison_brereton_extract.py)
from the archive.org OCR of all three print volumes (an INPUT, never committed); Renou joined
from the committed H1843 citation index by
[`src/rv_renou_evp_witness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_renou_evp_witness.py).

### J–B coverage — the acceptance bar was Griffith's, not Geldner's

J–B translate the complete RV, so anything short of 10,552 with 0 unmatched means the parser
is wrong rather than the book incomplete (handoff requirement 4).

| Gate | Result |
|---|---:|
| Canonical loci covered | **10,552 / 10,552** |
| Unmatched loci | **0** |
| Duplicate loci | 0 |
| Loci outside the canonical set | 0 |
| Hymns short of their canonical stanza count | 0 |
| Hymn headings anchored from the OCR | 1,020 / 1,028 |
| Hymns resolved positionally (heading destroyed by OCR) | 8 |
| Commentary leaks (J–B introductions/notes inside a stanza) | **0** |
| Stanzas ending in page/running-head furniture | **0** |

### Text-quality controls, against the Griffith layer as an independent control

Griffith was extracted by a different script from a different source, so its rates are a
usable baseline rather than a self-comparison. Every defect below is one a locus count cannot
see — each held at 10,552/10,552 while it was present, which is the point.

| Measure | J–B 2014 | Griffith 1896 (control) |
|---|---:|---:|
| Stanzas | 10,552 | 10,552 |
| Characters of text | 1,937,825 | 1,618,483 |
| Median stanza length | 188 | — |
| Longest stanza | 454 | — |
| No terminal punctuation | 264 (2.50%) | 197 (1.87%) |

| Defect found during the run | Extent | Longest stanza |
|---|---:|---:|
| Next hymn's whole heading block swallowed (OCR-destroyed heading) | 8 hymns | 5,751 |
| `Mandala N` section introduction swallowed at a mandala boundary | 9 stanzas | 4,387 |
| Hymn-group introduction swallowed (no heading, no metre line) | 11 detected | 2,434 |
| Page number + running head embedded mid-text | 1,031 open-ended (9.77%) | — |
| Mangled running head glued to the last word (`V111.78`, `VI.43^4`) | 16 stanzas | — |
| **After the fixes** | **0** | **454** |

### Renou EVP as a locus-keyed witness — not a sixth column

EVP is a selective commentary, so a `translations` column would be mostly
`absent_from_source` and would corrupt `omitted_by_one`, whose meaning rests on absence being
meaningful.

| Measure | Value |
|---|---:|
| Renou mentions in the committed H1843 index | 2,213 |
| `locus_unresolved` (front matter / hymn-group intro) | 31 |
| Resolved onto a locus | 2,182 |
| — of those, carrying a quoted French fragment | 458 |
| **Distinct loci carrying a Renou witness** | **1,908** |
| Loci with at least one quoted fragment | 431 |
| Of the 100 sampled gate-sheet items, those at a Renou locus | 14 |

Per mandala (loci with a witness): 1:457 · 2:116 · 3:160 · 4:116 · 5:156 · 6:110 · 7:169 ·
8:122 · 9:223 · 10:279.

The 458 quoted figure sits one below H1843's measured 459 because one quoted mention is
`locus_unresolved` and so carries no locus. Neither reconciles to the H1843 spec's published
368 — H1843 logged that discrepancy rather than tuning to match, and this pass does not
re-open it.

### Scope impact of the fifth translator

| Quantity | Before (4 translators) | After (5) |
|---|---:|---:|
| Translator pairs (n choose 2) | 6 | **10** |
| Pairs decided deterministically by Geldner's gap | 3 of 6 | **4 of 10** |
| Flat TSV mirror rows | 659,032 | **823,790** |
| Flat TSV mirror size | 173.6 MB | **216.6 MB** (gitignored; 500-row sample committed) |
| Labels for a full typing run | 63,312 | **105,520** |
| Cost at the measured pilot rate ($1.06/12,000 labels) | ≈ $5.6 | **≈ $9.3** |

### One measured philological fact worth keeping

At **RV 10.106.5–8** — the four stanzas Geldner omits — J–B print *transliterated Vedic*,
not English: they decline to translate rather than skip. Those loci are therefore `present`
in the spine but are not an English rendering, and the divergence typer must not read them as
one. Pinned by `test_jb_untranslated_loci_are_present_not_absent`.

## 29-07-2026 — H1847: NWS tag vocabulary — in-card legend + faceted browse

Opus 5 1M (`claude-opus-5[1m]`),
[H1847](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1847-Opus_SanskritLexicography_nws-tag-vocabulary-facets_29.07.26.md).
Tag reach measured over the whole RU store (`src/pwg_ru_translated.jsonl` — local-only,
gitignored) with [`g5_card_render.card_tags`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/g5_card_render.py);
corpus figures from the committed census aggregate.

| Scope | Denominator | Carrying an NWS tag | Rate |
|---|---:|---:|---:|
| RU translation store | 11,603 rows | 255 | 2.20% |
| G5 batch1v3 sheet (150-card live slice) | 150 cards | 4 | 2.7% |
| NWS corpus (census denominator, for contrast) | 34,101 cards | 48,214 tagged senses | — |

Vocabulary actually present in our slice — the facet bar is built from this, the chip's
percentage from the corpus census:

| Slot | Distinct in store | Top values (store counts) |
|---|---:|---|
| diasystem | 10 | `Ved` 115 · `Śā` 67 · `Gen` 33 · `Buddh` 16 · `Reg` 8 |
| domain | 12 | `unsp` 170 · `Med` 34 · `Soc` 15 · `без уточн` 13 · `Ling` 12 |
| position | 2 | `ifc` 3 · `Bhvr` 1 |

Worktree sibling-path degradation — same command, same inputs, only the checkout differing
(FINDINGS §503; the left column is what would have reached the reviewer):

| Layer in the re-issued 150-card sheet | Built in a worktree | With `CSL_SIBLING_ROOT` set |
|---|---:|---:|
| `<ab>` spans with German/Russian expansion | 0 | 253 |
| unlinked-citation marks (needs `pwgbib`) | 1 | 8 |
| Cologne `<ls>` links (needs neither table) | 988 | 988 |
| NWS tag tooltips | 47 | 47 |
| facet chips / in-card tag panels | 8 / 4 | 8 / 4 |

Non-goals / caveats: the two store-side tag defects (17 half-translated tags, 1 malformed
bracket) are **reported, not repaired** — repair is store-side. Nine further `src/` modules still
carry the worktree-fragile sibling-root guess. The pinned re-issue proved 150/150 card digests
byte-identical, so votes already cast still bind. Findings: §503, §504.

## 29-07-2026 (later) — H1210 coverage fill (H1846): the A/B at 100 vs 100, and the metric flips the winner

Arm A's 13 unattempted cards run from the frozen payloads (Opus 5 1M `claude-opus-5[1m]`
session; workers Sonnet 5 `claude-sonnet-5`, controller resolved to `claude-opus-5[1m]` for
these 13 vs `claude-opus-4-8` for the original 87). Both arms now at **100/100 attempted**.
Report updated in place:
[H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md).

**The fill overturned the earlier conclusion — via the metric, not the new cards.**
`canonical_audit.py` scores `cards_out`, which holds the last attempt that *returned*, while
`final_status` records how the card *ended*; a card whose controller rejected attempt 1 and
whose attempt 2 died mid-stream ends `worker-null-death` yet still carries attempt 1's text
into the audit. So "audit-clean" includes cards the pipeline refused to ship — 21 in arm A,
8 in arm B.

| entry-length quartile | A audit-clean | B audit-clean | A shippable | B shippable |
|---|---:|---:|---:|---:|
| Q1 (28–176 B) | 22/22 (100%) | 21/22 (95%) | 22/22 (100%) | 21/22 (95%) |
| Q2 (180–526 B) | 23/23 (100%) | 21/23 (91%) | 23/23 (100%) | 21/23 (91%) |
| Q3 (670–4349 B) | 19/22 (86%) | 19/22 (86%) | 15/22 (68%) | 15/22 (68%) |
| Q4 (4553–11974 B) | 20/23 (87%) | 8/23 (35%) | **3/23 (13%)** | **4/23 (17%)** |
| no_pwg | 9/10 (90%) | 9/10 (90%) | 9/10 (90%) | 9/10 (90%) |
| **TOTAL** | **93/100** | **78/100** | **72/100** | **70/100** |

`shippable` = audit promote-DRY **and** the rig ended the card `clean-no-review` /
`clean-controller-approved`. On that metric the arms **tie (72 vs 70)** and Q4 **reverses**
(13% vs 17%): neither pipeline ships long entries unattended. The S2 defect-culprit stratum
shows it sharpest — arm A 13 audit-clean → **4** shippable (9 refused), arm B 3 → **2**.

**The earlier "length-routed hybrid" recommendation is withdrawn** — it rested on arm A's
93% vs 35% on Q4, which does not survive the pipeline metric. Two caveats bound the tie:
the 13 filled cards ran on a later controller tier, and **8 of them lost attempts to API
transport failures** (`stalled mid-stream` / `connection closed`), so arm A's Q4 13% is a
floor. Largest available lever is now the retry/transport layer (a null attempt consumes one
of three), not the generator.

## 29-07-2026 — H1210: DeepSeek vs Claude-native on 100 stratified PWG cards

Runs 28-07-2026, report 29-07-2026. Controller in **both** arms Opus 4.8
(`claude-opus-4-8`); arm-A workers Sonnet 5 (`claude-sonnet-5`); arm-B generator
`deepseek-chat`. Report, coverage audit and blind sheet: Opus 5 1M (`claude-opus-5[1m]`).
Full method, limitations and what the numbers do *not* support:
[pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md).
Both arms promote-DRY; nothing entered the store.

**Read the coverage row before the clean rates.** Arm A completed 87 of 100 cards — three
size-bounded chunks never ran — and because chunks pack by BYTES the gap is a contiguous
band, not a random 13: 9 of the 13 fall in Q4, and **all ten S4 verb-root cards are missing**.
The two headline percentages are therefore *not* a head-to-head; the quartile table is.

| metric | arm A — Claude-native | arm B — DeepSeek + same controller |
|---|---|---|
| cards attempted | 87/100 (S4 verb roots: 0/10) | 100/100 |
| audit-clean % (canonical promote-DRY) | 95.4% (83/87) — not comparable, see above | 78.0% (78/100) |
| **Q1 28–176 B / Q2 180–526 B** | **100% (22/22) / 100% (22/22)** | **95% (21/22) / 91% (21/23)** |
| **Q3 670–4349 B / Q4 4553–11974 B** | **89% (17/19) / 93% (13/14)** | **86% (19/22) / 35% (8/23)** |
| defect-culprit stratum S2 | 11/12 | 3/15 |
| NULL-CARD / worker-null-death | 0 / 5 | 9 / 13 |
| calls per clean card (controller share) | 2.96 (38.2%) | 2.55 (25.1%) |
| escalated to review-sheet | 12 (13.8%) | 15 (15.0%) |
| generation USD → per clean card | n/a (subscription lane); 16.54 M subagent tokens | **$0.7255 → $0.0093** |
| wall clock | 9,625 s (median 114 s/card) | 1,255 s |

The two arms are a wash below ~4.5 kB and diverge sharply above it — a single averaged
percentage over a length-stratified sample is a weighted artifact of the selection rule, not
a quality delta. Arm B's $ figure is **generation only** (its controller runs on the same
subscription lane, uncosted), and the 7.7× wall-clock difference is lane latency (Workflow
agent harness vs a direct HTTP loop), not model latency.

Generator-independent findings from the same run: the rig's self-report **understates**
audited cleanliness in both arms (70 vs 83; 72 vs 78 — H1209 v1 saw it overstate, so the
canonical audit is the verdict either way), and the complexity trigger false-flags 77.8%
(A) / 63.2% (B) of the cards it escalates. Blind 40-item human vote (20/arm, unlabelled) is
generated and pending a reviewer; verdicts are the top quality layer and can still move the
conclusion.

## 26-07-2026 - H1681 follow-up: the compound-`differs` blind arm re-cut, deduped and BOUND

Executor: Opus 5 1M (`claude-opus-5[1m]`). MG ruled **re-cut** on the H1681 `@DECIDE`
(re-cut vs retro-lock). Generator
[`src/pilot/compound_differs_review_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_review_sample.py)
repaired on both counts and the sheet re-drawn from the same `seed=1628`.

| | before | after |
|---|---|---|
| frame sampled from | 4,226 rows (103 sharing a card id) | **4,123**, one per `(k1, hom)` card id |
| sample | 200 rows / **199** distinct ids | 200 rows / **200** distinct ids |
| binding | none — `validate_decisions.py` would reject the export | `sha256:31c106bb13cd2bad…`, lock committed, gate `G6-compound` |

**The duplicate card was the visible end of a queue-wide mismatch:** `headword_index.tsv`
carries one row per part-of-speech reading (`agraRI` as `adj.` and as `m.`; 2,383 of its
keys are multi-row), while a card id is only `(k1, hom)`. So the `differs` queue's 4,226
rows are **4,123 distinct cards**. The adjudication is unaffected — all 103 duplicate rows
agree with their twin on both members and verdict (0 disagreements), since a compound's
analysis does not depend on the entry's `lex`.

Arm coverage after the re-cut (200 cards): `same_split_pwg_lemma_form` 138 → max Wilson-95
lb 0.973, still the only stratum that can clear the 0.90 gate; `pwg_lexeme_vs_mw_suffixed_tail`
17 · `mw_cut_leaves_nonword` 11 · rest unchanged. **Promotion ceiling stays 3,018/4,226
(71.4 %)** — the second, rule-stratified arm remains [H1703](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1703-Opus_SanskritLexicography_compound-differs-second-arm-and-sheet-binding_26.07.26.md)
and is still sequenced behind [SanskritGrammar#527](https://github.com/gasyoun/SanskritGrammar/issues/527)
+ [#801](https://github.com/gasyoun/SanskritLexicography/issues/801).

The HTML stays gitignored; `generated` is pinned to `26-07-2026` so a regeneration
reproduces the exact bytes the lock binds. `csl_pyutil` is **0.4.0** here, not the 0.3.1
the H1404 manual records — the stamp anchors still matched.

## 26-07-2026 - H1681: all 4,226 PWG-vs-MW compound `differs` rows adjudicated by rule

Executor: Opus 5 1M (`claude-opus-5[1m]`), Claude Code. В2 arm of the H1664 triage. Full
method + limitations:
[research/PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md);
verdicts:
[research/pwg_compound_differs_adjudication.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_adjudication.tsv).
**No store field changed; the 200-card blind arm was not touched.**

The queue is not "one dictionary is wrong": PWG's parenthesis states the compound's
members **as lexemes**, MW's `<k2>` is a **surface segmentation** — MW's members
concatenate back to the headword in 4,215/4,226 rows (99.7 %), PWG's in 81 (1.9 %).

| Verdict | rows | share | = sheet vote |
|---|---:|---:|---|
| `pwg_members-right` | 3,724 | 88.1 % | approve |
| `index_members-right` | 180 | 4.3 % | reject |
| `unresolved` | 322 | 7.6 % | defer |

20 rules, first-match-wins; the five largest: `same_split_pwg_lemma_form` 3,018 ·
`pwg_lexeme_vs_mw_suffixed_tail` 323 · `mw_cut_leaves_nonword` 277 ·
`cut_moved_both_readings_lexical` 253 (unresolved — both readings lexical) ·
`pwg_layer_no_headword_paren` 82.

**Four upstream defects found and worked around in memory (nothing rewritten):**

| Defect | In queue | Whole dataset |
|---|---:|---|
| `pwg_compound_split.py` takes the first `+`-chain with no bracket awareness — inner sub-analysis or a *different word's* parenthesis | 162 | 344/16,738 wrong chain (2.06 %) + 368 unverifiable (2.20 %) |
| `mw_compounds._clean_member` strips `;` and the space, fusing MW `<k2>` variants into one bogus member | 10 | 41/106,603 MW compound records (0.04 %) |
| transcription typos in PWG's own member strings (`sda` for *sūda*, `hasaM` for *haṃsa*) | 12 | csl-orig batch candidates, not swept further |
| the H1628 sheet has no lock/content-hash and a duplicate card (200 rows, 199 ids) | — | `validate_decisions.py` would reject the vote export |

**Promotion plan (gate: per-stratum Wilson-95 % lb ≥ 0.90, provenance `agent`, never
`human_reviewed`):** only `same_split_pwg_lemma_form` (3,018 rows, 140 arm cards, max lb
0.973) can clear the gate — **the 200 votes close 3,018 of 4,226 rows (71.4 %), not all
of them.** A stratum needs ≥ 35 arm cards at 100 % agreement to reach 0.90, and the H1628
sample was stratified by length × DCS frequency before these rule strata existed. The
remaining 1,208 rows need a second, rule-stratified arm of ~280 cards.

## 26-07-2026 - H1682: h1303_abbrev rule-collapse — 273 → 33 cards

Executor: Sonnet 5 (`claude-sonnet-5`),
[H1682](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1682-Sonnet_SanskritLexicography_h1303-abbrev-rule-collapse_26.07.26.md).
Full method + per-section table:
[H1682_ABBREV_RULE_COLLAPSE_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1682_ABBREV_RULE_COLLAPSE_REPORT_2026-07-26.md);
100% classification: [H1682_ABBREV_RULE_COLLAPSE_CLASSIFICATION_2026-07-26.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1682_ABBREV_RULE_COLLAPSE_CLASSIFICATION_2026-07-26.tsv).

| | count |
|---|--:|
| ab-tokens classified (100%) | 269 |
| rule-bulk (folds into a section policy) | 252 |
| residue (classifier-flagged ambiguous) | 17 |
| Rule cards | 12 |
| Residue + ls-border + meta cards | 17 + 3 + 1 |
| **New sheet total** (`h1682_abbrev_rules`) | **33** |
| Old sheet (`h1303_abbrev`, superseded-unvoted) | 273 |

No token reclassified — every rule/residue label is re-grouped from
`build_h1303_abbrev_sheet.py`'s existing `O` overlay (H1303 Session 1,
21-07-2026) via its own 12 `# --- ...` section headers, parsed straight from
source (no hand-retyped token lists). Found + fixed in passing: the H1682
mandate's own "CONTRADICTIONS §7" (and `.ai_state.md`'s) is stale — renumbered
to §4 by H1364 (20-07-2026).

## 26-07-2026 - H1664: voting-queue triage — a verdict for every pending sheet, human bill recounted

Executor: Fable 5 (`claude-fable-5`),
[H1664](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1664-Fable_SanskritLexicography_voting-queue-agent-adjudication-triage_26.07.26.md).
Full verdict table (all 42 pending sheets org-wide, each with its enabling dataset):
[VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md).

| Bucket | Sheets | Judgments now | Owed after routing |
|---|---|---|---|
| AGENT-RULEABLE | 1 (+2 zombie rows) | 17 | 0 |
| HYBRID (В2: agent adjudicates, human votes a blind stratified arm) | 20 | 2,282 | ~666 |
| HUMAN-ONLY | 21 | 663 | 663 |
| **Pending queue total** | **42** | **2,962** | **~1,329 (−55 %)** |
| acc_ncc lane (rerouted 26-07, executed; post-H1671 key repair the C/D set is 10,614) | 1 | 49,019 | 698 |

SL-specific outcomes: compound-`differs` goes В2 —
[H1681](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1681-Opus_SanskritLexicography_pwg-compound-differs-b2-full-queue-adjudication_26.07.26.md)
adjudicates all ~4,226 and the H1628 200-card sheet becomes the blind verification arm (same
200 votes then close the whole queue); h1303_abbrev collapses to rule-level cards
([H1682](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1682-Sonnet_SanskritLexicography_h1303-abbrev-rule-collapse_26.07.26.md),
273 → ~30); the 32 article-comparison edits get source-checked pre-vote
([H1683](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1683-Sonnet_SanskritLexicography_article-comparison-source-check_26.07.26.md));
h180 stays routed via H1650. HUMAN-ONLY (kept, with the why): G6 gold starter (the label is
the instrument), G5 batch1v3 (already the В2 human arm), h1306 style, Renou pilot 70,
Kochergina 4. The acc_ncc blind spot-check (698 rows post-H1671 re-draw; the pre-repair 686 sample was voided unvoted) is now registered in
[REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md)
the H1671 sequencing gate resolved itself the same day — the key repair merged ([PR #785](https://github.com/gasyoun/SanskritLexicography/pull/785)) and the fresh sample is safe to vote. HY "after" numbers
are planning estimates — exact arm sizes derive per stratum at execution
([PR #783](https://github.com/gasyoun/SanskritLexicography/pull/783) pattern).

## 26-07-2026 - H1628: stratified 200-item review sheet, PWG-vs-index compound `differs` (H1624 G6 residual)

Executor: Sonnet 5 (`claude-sonnet-5`). Sampled from the ~4226-row `differs` queue the
[H1624 G6](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md)
`enrich_portrait_derivation.py --conflict-rate` flags (39539 rows scanned, 4226/39539 =
10.69% conflict, 10577/39539 = 26.75% needs_human — unchanged from G6's freeze). Sampling
script:
[`src/pilot/compound_differs_review_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_review_sample.py)
(`--selftest` wired; `--report` dry-runs the strata; `--write` emits the frame + sheet).

**Sample frame — two-stage stratified, seed=1628 (deterministic, reproducible):**

1. `vs_index_class` (how PWG's split disagrees with the pre-existing
   `headword_index.tsv` `compound_members`, not itself stratifiable since the whole
   queue is `compound_status=differs`): `member_count_diff` (76/4226, 1.8%) gets a flat
   **guaranteed quota of 20** — proportional allocation would round it to ~1-2 items and
   bury a structurally distinct failure mode; `same_count_diff_split` (4150/4226) fills
   the remaining 180 proportionally across length x frequency cells (largest-remainder
   rounding to land exactly on 180).
2. `length_bucket` (`len(k1)`): short ≤8 / medium 9-10 / long ≥11 (quartile-derived cuts
   on the full differs frame).
3. `freq_bucket` (DCS attestation count via
   [`src/pwg_freq_order.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_freq_order.tsv)):
   `no_dcs_freq` (no match, 58.1% of the frame) / low 1-2 / mid 3-9 / high ≥10.

| stratum | full differs frame (n=4226) | sample (n=200) |
|---|---:|---:|
| vs_index_class: member_count_diff | 76 (1.8%) | 20 (10.0%, oversampled by design) |
| vs_index_class: same_count_diff_split | 4150 (98.2%) | 180 (90.0%) |
| length: short(≤8) | 1904 (45.1%) | 83 (41.5%) |
| length: medium(9-10) | 1622 (38.4%) | 78 (39.0%) |
| length: long(≥11) | 700 (16.6%) | 39 (19.5%) |
| freq: no_dcs_freq | 2456 (58.1%) | 123 (61.5%) |
| freq: low(1-2) | 660 (15.6%) | 28 (14.0%) |
| freq: mid(3-9) | 503 (11.9%) | 22 (11.0%) |
| freq: high(≥10) | 607 (14.4%) | 27 (13.5%) |

Sample frame (metadata only — k1/hom/both splits/strata/panini/gaṇa, no `ru`/`de` store
text) committed at
[`review/sanskritlexicography-pwg-compound-differs_stratified200_frame.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/sanskritlexicography-pwg-compound-differs_stratified200_frame.tsv).
The interactive sheet itself
(`review/sanskritlexicography-pwg-compound-differs_stratified200_review.html`) stays
**gitignored**, per the `/review-sheet` contract — personal voting artifact, not a repo
deliverable.

**Vote → store contract (so `derivation.human_reviewed` never gets a bulk overwrite):**
`decisions.json` export carries one decision per `(k1, hom)` id — `approve` = PWG's split
is correct (a future apply step sets that entry's `derivation.compound.human_reviewed =
true` with `members` taken from `pwg_members`); `reject` = the index's split is correct
(same overlay, `members` taken from `index_members`, PWG layer flagged
`needs_correction`); `defer` = no vote, stays `needs_human`. The overlay write touches
**only the ~200 sampled `(k1, hom)` keys** — `enrich_portrait_derivation.enrich_portrait_obj`
already refuses to touch any entry whose `derivation.human_reviewed` is truthy, so applying
this batch cannot silently re-stamp the other ~4026 unsampled `differs` rows.

**Explicit non-goal:** the remaining ~4026 `differs` rows (4226 − 200) stay `needs_human`;
this sheet closes zero rows on its own until MG votes and `/decisions-apply` runs.

## 26-07-2026 - P1 ruling applied: machine-flag layer over the live queue, batch1v3 (H1655)

Executor: Fable 5 (`claude-fable-5`). MG ruled the voting-queue triage `@DECIDE` «auto-reject»
(screening-audit §7: machine-flagged cards never reach a human sheet). `machine_flags` (D1/D3/D4)
added to
[`review_residue_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_residue_gate.py);
batch1v2 superseded UNVOTED by `g5-live-queue-batch1v3-2026-07-26`.

| Metric | n |
|---|---:|
| queue rows | 11,163 |
| excluded: reader-visible German | 636 |
| excluded: machine flags D1/D3/D4 | 3,236 |
| ... D4 slot-count mismatch / D3 gloss-drift «…» / D1 Cyrillic in `{#…#}` | 3,067 / 370 / 20 |
| already decided | 5 |
| eligible for sheets | 7,286 (65.3%) |
| batch1v3 cards (0 leaks, both layers) | 150 |

D5 (gloss byte-identical to DE) deliberately not flagged — audit-measured ~false-positive.
Store-side repair of flagged rows: H1651 (queued, Sonnet).

## 26-07-2026 - H1631: edition-diff reading surface (N14 pilot) — subtype counts on the 7 REGLUE_SPEC pilot roots

Executor: Sonnet 5 (`claude-sonnet-5`). Fixture-driven static page +
[`src/pilot/build_edition_diff_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_edition_diff_site.py)
(`--selftest` wired into CI). Renders the PWG sense skeleton with PW/SCH/PWKVN/NWS
supplements attached at their `edition_rel` insertion point, each badged with its
subtype — the H1624 G4 classifier is the only typology used, no new classes invented.
Table below is a local `--out` run against the (gitignored, uncommitted) live store's
5-layer pilot keys from [`REGLUE_SPEC.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md) Sec.5 — counts only, no store text
published (N9).

| subtype | count (7 pilot roots, 1077 rows) |
|---|---|
| base | 433 |
| restate | 475 |
| pw_correct | 0 |
| sch_star | 11 |
| derived_sense | 3 |
| a2a | 13 |
| nws_at_sense | 111 |
| foreign_fragment | 31 |

Pilot roots: `gA`, `Cid`, `Sam`, `jIv`, `rakz`, `vraj`, `yat` (the 5-layer set). No
`pw_correct` (gender-conflict) instance among these 7 — consistent with REGLUE_SPEC's own
finding that PW mostly *restates* rather than corrects at this sample. N14 partial close:
demo covers PWG/PW/SCH/PWKVN/NWS badges for the pilot set; scaling to the full store,
per-sense visual grouping polish, and any editorial adjudication of `differs` cases are
explicitly out of scope (non-goals).

## 26-07-2026 - H1629 DE edition-graph export (OntoLex + TEI Lex-0) + three integrity findings

Executor: Opus 5 (`claude-opus-5[1m]`). New generator
[`src/export_de_edition.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py);
profile doc
[`DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md).

**Golden-fixture export** (22 DE-only rows → `release/fixture/de_edition/`, `--generated-at 2026-07-26`):

| entries | senses exported | quarantined | sanitized tags | government | form_notes | citation_edges | gloss_spans | edition_rel |
|---|---|---|---|---|---|---|---|---|
| 7 | 20 | 2 | 1 | 15 | 2 | 42 | 3 | 17 |

Edition-layer coverage in the fixture: `pwg` 3 · `pw` 6 · `sch` 3 · `pwkvn` 5 · `nws` 3.
Artifacts: `pwg_de_edition.ttl` 42 KB · `pwg_de_edition.tei.xml` 23 KB · manifest 1.4 KB.

**Finding 1 — Russian tokens inside the German `de` field.** 11 of 11,603 store rows
(0.09%). Verified against csl-orig: `huti` reads `{%Opfer%} in {#sarva˚#} **und**
{#havirhuti#}` upstream but `… **и** …` in the store (and the store row also dropped the
`(von 1. {#hu#})` etymology parenthesis).

| symptom | example row |
|---|---|
| `и` for `und` | `huti`: `{%Opfer%} in {#sarva˚#} и {#havirhuti#}` |
| `для` for `für` | `parihara`: `<ab>v. l.</ab> для {#parihAra#}` |
| `в` for `in` | `nI` desid-3: `<ls>VĀRĀHA-P.</ls> в <ls>Verz. d. Oxf. H. 59,a,3.</ls>` |
| `С` for `Mit` | `viS` 175: `<div n="p">— С {#anUpa#}` |
| `корригенда` | `DA` pw: `Mit <div n="p"> — корригенда` |
| **total rows with Cyrillic in `de`** | **11 / 11,603 (0.09%)** |

**Finding 2 — Russian prose in DE-side structural fields.** `sense_tag`: 110/11,603 rows
(0.95%), e.g. `c) с dat. лица и instr. предмета`. The `h` field likewise carries Russian
disambiguation prose (`PW 3 (с sam, о супружеском намерении)`). The export quarantines
`de`-contaminated rows, reduces a contaminated `sense_tag` to its ASCII skeleton, and drops
`h` from the allowlist entirely.

**Finding 3 — G1 `gloss_lang` classifier false positives.** Census over every `{%…%}` span
in the store's German text:

| lang | rule_id | spans | German-looking | FP rate |
|---|---|---|---|---|
| en | `english_content` | 153 | 117 | **76.5%** |
| la | `botany_binomial` | 68 | 5 | 7.4% |
| ambig | `homograph_ambig` | 8 | 0 | 0.0% |
| **total non-DE** | | **229** | **122** | **53.3%** |

Base: 15,901 spans scanned; 229 (1.44%) classified non-DE. Examples of misfires — all
unmistakably German: `bis an's Ziel bringen`, `an sich nehmen, empfangen, erlangen,
erhalten` (→ `en`); `Gelegenheit gefunden habend`, `Willens sein` (→ `la` botany binomial).
Because `pwg_mask.classify_pct_detail` marks `la`/`en` spans `translate: False`, these
German glosses are also masked out of the translate path upstream. "German-looking" is a
heuristic proxy (umlaut / German function word / `-en` verb ending), so the rate is ±;
the direction is not in doubt. **Not fixed here** — changing the classifier changes masking
behaviour pipeline-wide and needs its own measured A/B.
## 26-07-2026 - G5 batch1 decisions applied + reader-visible German gate over the live queue (H1655)

Executor: Fable 5 (`claude-fable-5`). Reviewer MG aborted batch 1 at 5/150 votes («Переделай
все» — German must be screened BEFORE a human sees a card). Votes applied through
`apply_decisions --gate G5` → `run_batch apply_review`; new
[`review_residue_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_residue_gate.py)
swept the queue; batch1v2 rebuilt gate-clean. Full audit:
[decisions_applied_2026-07-26_g5-batch1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-26_g5-batch1.md).

| Metric | n |
|---|---:|
| batch1 votes: approve / reject / unvoted (abort) | 3 / 2 / 145 |
| live queue rows swept | 11,163 |
| flagged: reader-visible German | 637 (5.7%) |
| ... hits by layer: prose (H1302 class b) / ls-tail `fg.` / German `ab` | 457 / 371 / 145 |
| clean rows eligible for sheets | 10,526 |
| batch1v2 cards (all verified German-free) | 150 |
| positional-id drift: votes initially unresolvable against grown store | 2/5 (fixed: suffix fallback + CI pin) |

## 26-07-2026 — H1630 top-N `citation_edges` sigla → Cologne scan/HTML link coverage

Executor: Sonnet 5 (`claude-sonnet-5`), isolated worktree. Script: `src/citation_edges.py`
(`topn` subcommand, new; `scan_href` field, new — H1624 G3 parent). Store: the live
11,603-row `pwg_ru_translated.jsonl` (gitignored, main-worktree canonical copy).

**What's new.** `extract_citation_edges()` gained an additive `scan_href` field —
`ls_resolver.generate_href('pwg', n_attr, raw_ls)` when it actually resolves a Cologne
scan/HTML target, else `null`. This is a *different* axis from the existing
`resolver_status` (map/bib/orphan): `resolver_status` only asks "is this siglum a known
work", not "does a clickable Cologne target exist for this exact locator" — e.g. `AK. 1`
is `map` (Amarakośa is a known work) but `scan_href` is `null` (the resolver pattern for
Amarakośa needs 3–4 coordinate parts, not one).

**Top-25 sigla by raw citation frequency → `scan_href` coverage:**

| siglum | citations | `scan_href` resolved | coverage | sample target |
|---|---:|---:|---:|---|
| MBH | 5,753 | 5,737 | 99.7% | [mbhcalc?1.1090](https://sanskrit-lexicon-scans.github.io/mbhcalc?1.1090) |
| ṚV | 3,705 | 3,697 | 99.8% | [rv01.100.html#rv01.100.05](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.100.html#rv01.100.05) |
| R | 3,126 | 3,123 | 99.9% | [ramayanaschl/?1,4,18](https://sanskrit-lexicon-scans.github.io/ramayanaschl/?1,4,18) |
| BHĀG. P | 2,167 | 2,152 | 99.3% | [bhagp_bom/app1/?10,19,13](https://sanskrit-lexicon-scans.github.io/bhagp_bom/app1/?10,19,13) |
| ŚAT. BR | 1,781 | 1,770 | 99.4% | [shatapathabr/app1?10,1,2,1](https://sanskrit-lexicon-scans.github.io/shatapathabr/app1?10,1,2,1) |
| M | 1,636 | 1,635 | 99.9% | [manu/index.html?2,109](https://sanskrit-lexicon-scans.github.io/manu/index.html?2,109) |
| KATHĀS | 1,472 | 1,472 | 100.0% | [kss/index.html?17,32](https://sanskrit-lexicon-scans.github.io/kss/index.html?17,32) |
| AV | 1,207 | 1,199 | 99.3% | [av09.005.html#av09.005.12](https://sanskrit-lexicon.github.io/avlinks/avhymns/av09.005.html#av09.005.12) |
| P (Pāṇini) | 1,049 | 1,034 | 98.6% | [sutraani/6/4/57](https://ashtadhyayi.com/sutraani/6/4/57) |
| Spr | 1,039 | 1,038 | 99.9% | [boesp1/app1/?1402](https://sanskrit-lexicon-scans.github.io/boesp1/app1/?1402) |
| HARIV | 905 | 902 | 99.7% | [hariv?3964](https://sanskrit-lexicon-scans.github.io/hariv?3964) |
| R. GORR | 671 | 671 | 100.0% | [ramayanagorr/?2,5,27](https://sanskrit-lexicon-scans.github.io/ramayanagorr/?2,5,27) |
| RAGH | 668 | 668 | 100.0% | [raghuvamsa/app1?12,52](https://sanskrit-lexicon-scans.github.io/raghuvamsa/app1?12,52) |
| PAÑCAT | 607 | 606 | 99.8% | [pantankose/app2?71,24](https://sanskrit-lexicon-scans.github.io/pantankose/app2?71,24) |
| VARĀH. BṚH. S | 576 | 555 | 96.4% | [brihatsam/app1?79,14](https://sanskrit-lexicon-scans.github.io/brihatsam/app1?79,14) |
| RĀJA-TAR | 575 | 575 | 100.0% | [rajatar/app1?5,424](https://sanskrit-lexicon-scans.github.io/rajatar/app1?5,424) |
| ŚĀK | 525 | 522 | 99.4% | [shakuntala/app1?62](https://sanskrit-lexicon-scans.github.io/shakuntala/app1?62) |
| BHAṬṬ | 460 | 431 | 93.7% | [bhattikavya/app1?2,28](https://sanskrit-lexicon-scans.github.io/bhattikavya/app1?2,28) |
| Spr. (II) | 450 | 450 | 100.0% | [boesp2/web1/boesp.html?7515](https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?7515) |
| VOP | 428 | 404 | 94.4% | [mugdhabodha/app1?26,215](https://sanskrit-lexicon-scans.github.io/mugdhabodha/app1?26,215) |
| AIT. BR | 409 | 407 | 99.5% | [aitbr/app1?2,16](https://sanskrit-lexicon-scans.github.io/aitbr/app1?2,16) |
| TS | 394 | 390 | 99.0% | [taittiriyas/app1?6,6,11,5](https://sanskrit-lexicon-scans.github.io/taittiriyas/app1?6,6,11,5) |
| MĀRK. P | 367 | 367 | 100.0% | [markandeyapurana/app1?101,8](https://sanskrit-lexicon-scans.github.io/markandeyapurana/app1?101,8) |
| KĀTY. ŚR | 328 | 328 | 100.0% | [katyasr/app1?22,6,16](https://sanskrit-lexicon-scans.github.io/katyasr/app1?22,6,16) |
| HIT | 308 | 307 | 99.7% | [hitopadesha/app2?20,15](https://sanskrit-lexicon-scans.github.io/hitopadesha/app2?20,15) |

**Residual (top-25 sigla with ZERO `scan_href` hits): none.** Every one of the 25
highest-frequency works (33,251 of 41,115 total citations, 80.9%) already resolves to a
Cologne scan/HTML target for the overwhelming majority of its individual locators
(93.7%–100%); the small per-siglum shortfalls (BHAṬṬ 93.7%, VOP 94.4%, VARĀH. BṚH. S 96.4%)
are individual malformed/unusual coordinates, not missing targets — the pattern-driven
resolver already covers this frequency band essentially completely.

**Where the real gaps are (beyond top-25): genuinely-uncovered high-frequency works.**
`resolver_status == "orphan"` (siglum unknown to `ls_source_map`/`pwgbib` at all — a
different, stricter failure than a `scan_href` miss) ranked by occurrences with a numeric
locator (excludes non-coordinate labels like "ed. Bomb."/"ed. Calc." — edition/cross-ref
notes with no locus, never linkable per the existing `build_citation_index.py` convention):

| rank | siglum | citations | work |
|---:|---|---:|---|
| 1 | JĀTAKAM / Jātakam | 95 | Jātaka tales |
| 2 | MAHĀVY / Mahāvy | 32 | Mahāvyutpatti |
| 3 | VAJRACCH / Vajracch | 24 | Vajracchedikā |
| 4 | CAMPAKA | 20 | (Buddhist Skt. text) |
| 5 | Journ. of the Am | 19 | Journal of the American Oriental Society |
| 6 | S | 18 | (ambiguous single-letter siglum) |
| 7 | KĀRAṆḌ | 18 | Kāraṇḍavyūha |
| 8 | Divyāvad | 16 | Divyāvadāna |
| 9 | HARṢAC / Harṣac | 14 | Harṣacarita |
| 10 | Kir | 8 | Kirātārjunīya |
| 11 | Maitr. S | 8 | Maitrāyaṇī Saṃhitā |
| 12 | Kauṭ | 8 | Kauṭilīya (Arthaśāstra) |

These are almost entirely Buddhist-Sanskrit / less-common works with **no scan repository
in `sanskrit-lexicon-scans`** — matches the pre-existing note in `build_citation_index.py`
("coverage is target-limited, not resolver-limited"). Hard gaps (no Cologne target exists
to link to at all) — route through [`/cologne-link-target`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-link-target.md)
if/when digitization work is prioritized; not attempted here (N15 out of scope, per H1630).

Reproduce: `python src/citation_edges.py topn --n 25` (JSON; the store resolves via
`store_path.canonical_store`, so this also works unmodified from a linked worktree).
Selftest for `scan_href` + `topn_scan_coverage`: `python src/citation_edges.py --selftest`.

## 26-07-2026 - H858 c1 live gate: HEALTH_NOGO (rate_limit) - profile sweep now 3/3 NO-GO

Executor: Opus 5 (`claude-opus-5[1m]`). Third profile gated for the same owed H858 window.

| Profile | UTC | Calls | Latency | Blocker |
|---|---|---|---|---|
| c4 | 25-07 16:02Z, 18:18Z | warm-up `rate_limit`, measured never ran | 17.9 s / 19.9 s - fine | quota |
| c5 | 25-07 18:56Z | warm-up + measured both `success` | 59.7 s / 53.0 s - ~2x ceiling | route latency |
| c1 | 26-07 02:37Z | warm-up `rate_limit`, measured never ran | 6.4 s - fine | quota |

c1: warm-up 6 424 ms `rate_limit`, measured never ran, wall clock 6.4 s. Same class as c4,
fastest rejection of the three.

**Two things this sweep establishes.** (1) The blockers are orthogonal - two profiles have
latency headroom but no quota, one has quota but no speed - so profile-swapping does not
unblock the window, it only changes which NO-GO you get. (2) **The wait is not "until
tomorrow":** c1 was probed at 02:37Z on a FRESH UTC day and still returned `rate_limit`, so
the binding cap does not reset at the date boundary. A future session must re-probe and read
the answer rather than assume a date change cleared anything.

No canary, no window, nothing promoted. Per-account evidence:
`src/pilot/output/h963_<account>_gate0_probe_events.jsonl`.

## 25-07-2026 — medium50 “all without --max-agents”: LIVE STOP (auth 403) + offline prep

Executor: Grok 4.5 · intent: fresh live-gate then **all five** medium50 windows
(`h1447-m50-w1…w5`, 48 keys) headless with **no** production `--max-agents`.

### Live gate (paid) — mechanical NO-GO

| profile | config_dir | health | detail |
|---|---|---|---|
| **c4** | `D:\ClaudeTools\profiles\claude4\.claude` | **NO-GO** | `h963_c4_gate0_probe`: warmup **auth**; events also show rate_limit/auth; measured history 168s ceiling breach |
| **c2** | `D:\ClaudeTools\profiles\claude2\.claude` | **NO-GO** | warmup **auth** 7358 ms |
| c1 / c4 / c5 / default | same stack | **403** | direct `claude -p` → `Failed to authenticate. API Error: 403 Request not allowed` for default, sonnet, opus, `claude-sonnet-5` |

**Stop reason:** `HEALTH_NOGO` / org-wide CLI **403** — no canary, no production calls, no store write.
Probe log rows: `gate0-c4-fresh-2026-07-25`, `gate0-c2-fresh-2026-07-25`.

**Human unblock:** re-auth / fix Max org permission so `claude -p` succeeds on a roster profile, then re-run live-gate.

### Offline prep completed (ready when GO returns)

| artifact | n |
|---|---:|
| merged 5-layer inputs (`_pilot_gen_merged`) | 48 keys |
| bare-key input aliases for `gen_opt_harness2.input_paths` | 48 |
| execution_manifest.v2 + harness per window | **5** (`w1` 3 keys agent_exp=3; `w2` 12→20; `w3` 11→14; `w4` 11→12; `w5` 11→12) |
| manifest `max_translate_agents` (no CLI max-agents) | 19 / 34 / 31 / 34 / 40 |

Resume recipe (gitignored output tree):
`src/pilot/output/MEDIUM50_NO_MAX_AGENTS_RESUME_2026-07-25.md` — headless lines
**omit** `--max-agents` on multi-key windows; canary alone may use `--max-agents 1`.

## 25-07-2026 - H858 c5 live gate: HEALTH_NOGO (latency ~2x ceiling) - orthogonal to c4

Executor: Opus 5 (`claude-opus-5[1m]`). First gate ever run on c5, after two c4 attempts the
same day returned HEALTH_NOGO on `rate_limit`. Packet:
[`pwg_ru/h858/H858_C5_LIVE_GATE_HEALTH_NOGO_2026-07-25.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h858/H858_C5_LIVE_GATE_HEALTH_NOGO_2026-07-25.md).

| Reading | Elapsed | Classification | Verdict input |
|---|---|---|---|
| warm-up | 59 651 ms | `success` | >= 30 000 ms ceiling -> FAIL |
| measured | 52 960 ms | `success` | >= 30 000 ms ceiling -> FAIL |

Both calls SUCCEEDED with real output and zero connection errors - this is not quota, not
auth. Wall clock 112.6 s for the pair.

### The finding: c4 and c5 fail for ORTHOGONAL reasons

| Profile | Calls | Latency | Blocker |
|---|---|---|---|
| c4 (16:02Z, 18:18Z) | warm-up `rate_limit`, measured never ran | 17.9 s / 19.9 s - fine | quota / account state |
| c5 (18:56Z) | warm-up + measured both `success` | 59.7 s / 53.0 s - ~2x ceiling | route latency |

Neither is a code defect and they share no cause: c4 has headroom but no quota, c5 has
quota but no speed. **Swapping profiles does not unblock the window** - it trades one
NO-GO for a different one. c5's numbers sit in the degradation band tracked since mid-July
(H963 104 870 ms; H1110 98 625 ms) and match H898's size-independent route-jitter finding:
the identical 6 828 B prompt read 16 621 ms on c4 at the 22-07 LIVE_GO.

Operational note: c5 is the profile this session runs on - a paid window there competes
with interactive sessions for the same quota, independent of today's latency verdict.

## 25-07-2026 - H858 c4 live gate: HEALTH_NOGO (rate_limit), no window opened

Executor: Opus 5 (`claude-opus-5[1m]`). `/pwg-live-gate c4`, one attempt, no reroll.
Packet: [`pwg_ru/h858/H858_C4_LIVE_GATE_HEALTH_NOGO_2026-07-25.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h858/H858_C4_LIVE_GATE_HEALTH_NOGO_2026-07-25.md).

| Reading | Elapsed | Classification | Verdict input |
|---|---|---|---|
| warm-up | 17 878 ms | `rate_limit` | fail-closed -> STOP |
| measured | - | never ran | - |

`gate_reason = HEALTH_NOGO` -> `verdict = NO-GO`. **Not a latency block** (17.9 s is well
inside the 30 000 ms ceiling) - c4 is rate-limited. No canary, no bounded window, nothing
promoted; one paid warm-up call was spent. The H858 Part B validation window stays owed.

c4 has produced no clean pair since 23-07: `rate_limit` x2 on 24-07, `auth` x2 earlier on
25-07, `rate_limit` today.

### Attempt 2 (18:18Z, through the fixed probe v1.63.0)

| Reading | Elapsed | Classification | Verdict input |
|---|---|---|---|
| warm-up | 19 903 ms | `rate_limit` | fail-closed -> STOP |
| measured | - | never ran | - |

Same `HEALTH_NOGO`. c4's rate-limit window has not reset: three `rate_limit` readings now
span 24-07 -> 25-07 18:18Z with two `auth` between, and latency is fine in every one
(9.9-19.9 s, all far inside the 30 000 ms ceiling). Quota/account state, not code or route -
further probing today is spend without information.

First live proof of the #729 fix: RAW READINGS printed ONE row (this run's, under a
per-invocation run id) and the NO-GO reasons name this run's own absent measured reading.
The old constant `RUN_ID` would have re-read all 10 historical rows and cited the 23-07
168 352 ms again.

### Probe defect found by this run (integrity)

| Defect | Impact | Tracking |
|---|---|---|
| `h963_c4_gate0_probe.py` hardcodes `RUN_ID`, then filters the append-only log by it and keeps the last row per purpose - so every run re-reads the whole history and can pair today's warm-up with a **stale** `measured` | today it only mis-stated a NO-GO reason (cited a 23-07 reading of 168 352 ms for a call never made). The inverse is the hazard: a stale passing `measured` + a passing warm-up prints `GATE-0 VERDICT: PASS`, which Step 3 turns into `LIVE_GO` and authorizes paid spend off a two-day-old number | [#729](https://github.com/gasyoun/SanskritLexicography/issues/729) |

## 25-07-2026 - H858 Part B: german-anchor repair — offline verification (NO paid run)

Executor: Opus 5 (`claude-opus-5`). Isolated worktree off `origin/master` @ `f96361ca`.
**Scope honesty: these are OFFLINE gates only.** The handoff's own validation — a bounded
no_pwg window showing the `{#…#}`-drop null class eliminated — is a PAID run and was NOT
performed: it needs a fresh live-gate GO, and the last c2/c4 readings were NOGO/rate-limited.
The live answer will come from `summary.german_anchor_repairs` on the first window that runs.

### Gates run

| Gate | Lane | Result |
|---|---|---|
| `german_anchor.selftest()` | Python (authored source) | 8/8 OK |
| `german_anchor_test.js` vs a REAL generated harness | JS (interpolated twin) | 21/21 PASS |
| `headless_worker_selftest.py` (incl. the new H858 test) | Python production route | PASS |
| `window_selftest.py` | both | **185/185**, 0 failed |
| `promote_final_cards.py --selftest` | store provenance | PASS |
| `lang_parity_check.py` | ledger | 82 entries, no drift, coverage complete |

### Behaviour pinned (both lanes, identical fixtures)

| Case | Before | After |
|---|---|---|
| headword `{#…#}` dropped from the echo (`{# 0/1`) | card NULLED, requeue reproduces it | repaired at sense head, stamped, promoted |
| mid-card span dropped (`1/2`, `1/3`) | card NULLED | re-injected at its nearest surviving neighbour |
| span dropped in a multi-sense card | card NULLED | lands in the correct sense (nearest-neighbour, not always-after) |
| echo faithful | accepted | accepted, **byte-identical, unstamped** |
| echo duplicates / fabricates / reorders a span | rejected | rejected, reason recorded (`german-anchor duplicate-token`, …) |
| german repaired but TARGET field dropped the span | `translation-fidelity-reject` | `translation-fidelity-reject` (unchanged — no laundering) |

### Integrity defect found in passing (pre-existing, unrelated to H858)

| File | Defect | Fix |
|---|---|---|
| `src/pilot/window_selftest.py` (coordinator-requeue test) | ran a real `--defect` requeue without `--no-residual`, appending a junk `{"key": "a"}` row to the tracked `no_pwg_residuals.jsonl` on EVERY suite run — the registry that decides which keys are BLOCKED from requeue | `--no-residual` added; polluting row reverted; the test's own assertions unaffected |

## 25-07-2026 - H1624 DH follow-up batch minted (H1626–H1635)

Executor: Grok 4.5. Mint-only (no execution). Parent: H1624 German layers closed G1–G6.

| ID | Priority | Topic | Status |
|---|---|---|---|
| H1626 | P0 | H1303 abbrev apply | ⏸ vote |
| H1627 | P0 | H1306 style / G5 | ⏸ vote |
| H1628 | P1 | compound differs sheet | QUEUED |
| H1629 | P2 | OntoLex/TEI DE graph | QUEUED |
| H1630 | P3 | citation top-N scans | QUEUED |
| H1631 | P4 | edition-diff UI | QUEUED |
| H1632 | P5 | sense–DCS pilot | QUEUED |
| H1633 | P7 | gold cut + methods | QUEUED |
| H1634 | docs | editorial principles | QUEUED |
| H1635 | FAIR | Zenodo public sidecars | QUEUED (rights) |

G7: existing H1333 (XLS-gated). Spec: Uprava/handoffs/_batch_h1624_dh_followups.tsv.

## 25-07-2026 - H1624 G6: compound conflict flags + G5/G7 blockers

Executor: Grok 4.5.

### G6 conflict rate (pwg_derivation_layer.tsv)

| metric | n | pct |
|---|---:|---:|
| rows | 39539 | 100 |
| conflict (differs) | 4226 | 10.69 |
| needs_human (differs+index-only) | 10577 | 26.75 |
| agrees | 6180 | — |
| pwg-new-fill | 6386 | — |

Never auto-adjudicates differs — future /review-sheet sample.

### G5 blocked
Awaiting pwg_ru/eval/h1306_style.decisions.json (sheet exists; vote not exported).

### G7 blocked
Palsule XLS not present; delegate H1333 when XLS lands.

## 25-07-2026 - H1624 G4: edition_rel on DE subcards

Executor: Grok 4.5.
Structured edition relationship flags on each sense (no DE rewrite).

| subtype | typical layer |
|---|---|
| base | pwg |
| restate | pw |
| pw_correct | pw (gender conflict) |
| sch_star / derived_sense | sch |
| a2a / derived_sense | pwkvn |
| nws_at_sense / foreign_fragment | nws |

Selftest: python src/edition_rel.py --selftest; promote stamp.

## 25-07-2026 - H1624 G3: citation_edges normalized DE <ls> graph

Executor: Grok 4.5 - offline.
Additive per-sense edges; raw <ls> not stripped.

| resolver_status | meaning |
|---|---|
| map | hit in ls_source_map (renou I-V) |
| bib | pwgbib expansion only |
| orphan | neither |
| empty | unparseable |

Selftest: python src/citation_edges.py --selftest; promote stamp; annotate --selftest.
Coverage CLI: python src/citation_edges.py report

## 25-07-2026 - H1624 form_notes: dedicated Nom/Voc field

Executor: Grok 4.5.
orm_notes = first-class field for nominative/vocative citation-form markers only.

| field | covers |
|---|---|
| government | acc loc instr gen dat abl |
| form_labels | number, gender, case_form, voice |
| form_notes | nom, voc only ({case, kind, span}) |

Selftest: form_labels --selftest; promote stamps form_notes.

## 25-07-2026 - H1624 form_labels: number / gender / nom-voc / voice on DE senses

Executor: Grok 4.5 - offline.
Sibling of government (Rektion). Acc/Loc/Instr/Gen/Dat/Abl stay in government;
form notes go to form_labels.

| axis | values | sources |
|---|---|---|
| number | sg, du, pl | ab sg./du./pl. (paren or bare) |
| gender | m, f, n, m.n, ... | lex primary; masc./fem./neutr. ab |
| case_form | nom, voc | parenthetical form notes (not Rektion) |
| voice | act, med, pass | ab med./act./pass. |

Not gender: bare ab n. (ambiguous with note). Not form_labels: Rektion cases.

Selftest: python src/form_labels.py --selftest; promote + microstructure stamp.
LANG_PARITY SHARED form_labels_number_gender_voice_h1624.

## 25-07-2026 - H1624 G2: government on every DE sense (promote + portrait)

Executor: Grok 4.5 · offline · no paid window.
Closes the gap where structured Rektion only appeared after a separate
nnotate_government backfill. Schema shape unchanged (array of hit dicts, D4/H338).

| path | producer | notes |
|---|---|---|
| store row on promote | promote_final_cards.rows_for + xtract_government(de) | always stamped (empty list if none) |
| store retrofit | nnotate_government.py | existing rows / drift repair |
| portrait sense at gen | microstructure.sense_node | from full DE segment |
| portrait backfill | nrich_portrait_government.py | older local portraits |
| retrieval surface | government.html via uild_article_site | still re-extracts from de_raw; floor banner |

Selftests: government_census selftest, nnotate_government --selftest,
promote_final_cards --selftest (PW (Instr.)), nrich_portrait_government --selftest,
uild_article_site --selftest. LANG_PARITY SHARED government_on_promote_and_portrait_h1624_g2.

## 25-07-2026 - H1624 G1: per-span gloss_lang on {%...%} (DE|LA|EN)

Executor: Grok 4.5 (session override; handoff pinned Opus 4.8) · offline · no paid window.
Artifact: [src/pwg_mask.py](src/pwg_mask.py) classify_pct_detail / gloss_lang_spans; residue shares classifier via [prompt_rule_audit.py](src/pilot/prompt_rule_audit.py); LANG_PARITY SHARED gloss_lang_spans_h1624_g1.

| vector | expect | rule_id | mask |
|---|---|---|---|
| {%das Nichthandeln%} | de | default_de | inline |
| das lat. {%ignis%} / <ab>lat.</ab> {%ignis%} | la | latin_cue | {Tn} |
| {%De accentu comp.%} | la | latin_phrase | {Tn} |
| {%Trapa bispinosa%} | la | botany_binomial | {Tn} |
| WILS. ... durch {%leaving, abandoning%} | en | wilson_en | {Tn} |
| {%terrestrial latitude%}, WILS. | en | wilson_en | {Tn} |
| WILS. ... {%Honig%} | de | default_de | inline |
| {%Name eines Baumes%} | de | default_de | inline (not binomial) |

Selftest: python src/pwg_mask.py --selftest · window_selftest.test_pwg_mask_gloss_lang_g1 · lang_parity_check green.

## 24-07-2026 — c2 medium50 w1 forensics: only-b0 / all-nulls = `--max-agents 1` starvation

Executor: Grok 4.5 (session) · gen model: Sonnet 5 (`claude-sonnet-5`) · profile: **c2 Pro**
(not Max) · keys: `nakzatra` / `sarvatra` / `sakft` · artifacts under
`src/pilot/output/c2_m50_w1*` (gitignored). Ledger:
[`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) id `C2_M50_W1_MAX_AGENTS1_2026-07-24`.

| run | config | `--max-agents` | ok/null | attempts seen | translate/heal spent | budget_stops | cost USD | terminal |
|---|---|---:|---|---|---|---:|---:|---|
| full w1 | c2 full profile | **1** | 0/3 | **b0 only** (success 161.8s) | 1 / 0 | **24** | 0.599 | all errors `selfheal-nothing-resolved` |
| stripped w1 | c2-stripped (H1517) | **1** | 0/3 | **b0 only** (timeout 180.3s) | 1 / 0 | **23** | 0.000 | same error stamp |
| fix w1 | c2 full profile | **omit** (manifest 19/41) | aborted | b0 timeout + **many** `heal:nakzatra#g*` + b1 | multi-spawn | n/a (HardFailure) | partial (~0.50+ on last call) | **`rate_limit`** session limit; resets 15:30 Europe/Moscow |

**Root cause (operator/process, not Pro-host):** `--max-agents N` caps **total** model
spawns (translate+heal) for the whole run. `N=1` spends the budget on the first batch;
remaining work refuses as `budget_exceeded` without spawning; `self_heal` overwrites notes
with `selfheal-nothing-resolved`. Smoking gun triad: `budget_stops ≫ 0` +
`translate_agents_spent=1` + single `b0` in `headless_attempts`.

**Guardrail:** do not copy `--max-agents 1` from single-key canaries onto multi-key windows.
**Separate residual:** c2 Pro session limit blocked the fix-run before a clean 3/3; re-run
after reset without the flag.

## 20-07-2026 — Sa→Ru gloss layer, wave 4: read-only TM lookup wired (H1349 W4 — H1349 COMPLETE)

Downstream wave: [`src/saru_gloss_tm.py`](src/saru_gloss_tm.py) `GlossTM` exposes the lemma +
root gloss layers as a **read-only** lookup for the pwg_ru/mw_ru card path — given a Sanskrit
lemma/root (SLP1) it returns ranked candidate Russian renderings. Additive consumer only; it
does not touch `pilot/translation_memory.py`, the store, or anything the safety-plan PRs
#547/#550 touch (the wave-4 risk fence). Smoke test on the published `SanskritRussian` data:

| query | layer | top candidates |
|---|---|---|
| `gam` (prefer root) | root | пришел (196) · отправился (177) · ушел (141) · пришли (100) |
| `karman` | lemma | действия (240) · деяния (186) · действие … |

Fixture-backed regression test (`tests/test_saru_gloss_tm.py`, 6 cases) wired into CI;
PROJECT_INTERLINKS glossary downstream row flipped planned→wired. **This closes H1349** —
waves 1 (defect fixes) + 2 (measured 85% precision) shipped; wave 3 (coverage) a measured
NO-GO (DEAD_ENDS §11); wave 4 (this) wires the read-only consumer.

## 20-07-2026 — Sa→Ru gloss layer, wave-3 coverage spike: vidyut-cheda NO-GO (H1349 W3)

Tried recovering the 78,842 unresolved forms via `vidyut.cheda` compound segmentation
(D7 reuse). **Measured NO-GO.** A strict gate (≥2 tokens + every member glossable,
[`src/build_compound_split.py`](src/build_compound_split.py)) recovers 28,673 forms (36.4% of
unresolved / 55,008 tokens) — but a 2-judge panel (Opus 4.8 `claude-opus-4-8` + Sonnet 5
`claude-sonnet-5`) on 40 gated recoveries scored segmentation **28% both-correct / 72%
either-wrong**, gloss **18% both-correct / 60% either-wrong / 40% acceptable**. Against the
wave-2 baseline (85.3% gloss) that is a catastrophic regression — ~half the recoveries are
outright wrong. Root cause: vidyut-cheda is a *running-text* segmenter; on isolated OOV forms
it shatters inflected/dual/plural words into stem + spurious glossable particle (`sahadevaśca`
→ `sahadeva`+`ca`, head "и"). **Decision: not wired in** — the 85% layer stays unregressed;
the 78,842 stay an honest coverage gap. Recommended path (backlog): the DharmaMitra **neural**
segmenter over the aligned *verse text*, which kosha's `compare_sandhi_methods.py` already
benchmarked as near-perfect and far above vidyut-cheda. Full write-up:
[`gold/saru_gloss_wave3_cheda_coverage.md`](gold/saru_gloss_wave3_cheda_coverage.md).

## 20-07-2026 — Sa→Ru gloss layer, measured precision (H1349 wave 2)

First **accuracy** measurement of the gloss layer (every prior number was coverage).
**Model-vs-model LLM panel, NOT human gold** (org gold-provenance rule): 3 judges
(Opus 4.8 `claude-opus-4-8`, Sonnet 5 `claude-sonnet-5`, Haiku 4.5 `claude-haiku-4-5`)
independently labelled a **tier × frequency stratified** sample of 110 resolutions on two
axes (lemmatization, gloss — D6); 9 split/correct-vs-wrong disagreements adversarially
adjudicated by a 4th model (Fable 5 `claude-fable-5`). Sampler + aggregator
[`src/saru_gloss_sample.py`](src/saru_gloss_sample.py) / [`src/saru_gloss_aggregate.py`](src/saru_gloss_aggregate.py);
full report [`gold/saru_gloss_precision_report.md`](gold/saru_gloss_precision_report.md).
Wilson 95% CI; "unsure" excluded from the denominator.

| axis | precision | 95% CI | note |
|---|--:|--:|---|
| lemmatization (overall) | **86.1%** | 78.3–91.4 | correct 93 · wrong 15 · unsure 2 |
| gloss (overall) | **85.3%** | 77.5–90.8 | ≈ the 84.4% upstream pair-precision ceiling; good+partial 97.2% |

| tier | lemma prec | gloss prec |
|---|--:|--:|
| dcs (n=40) | 94.9% | 87.5% |
| **vidyut (n=40)** | **71.8%** | 79.5% |
| marker (n=30) | 93.3% | 90.0% |

The **vidyut** tier is the lemmatization weak spot. Panel + verify converged on three
systematic, actionable defect classes (wave-3 targets): (1) ṛ/ṝ root-vowel length collapsed
to short (`kiranto`→√kṛ not √kṝ); (2) derived nominals lemmatized to a bare verbal root
(`janitṛ`→jan, `liṅgin`→liṅg); (3) compound tokens lemmatized to their final member only
(`anartha-trivarga`→trivarga). A human spot-check of the frozen sample is queued as a GTD @DO.

## 20-07-2026 — Sa→Ru gloss layer, wave-1 defect fixes (H1349 W1.1–W1.3)

Three pipeline-defect fixes in the Sa→Ru gloss layer, measured before/after over
one regenerated two-pass bootstrap (DCS `dcs_full.sqlite` 5.69M tokens + vidyut
kosha 0.4.0 + `surface_glossary.jsonl`). Fixes + measurement Opus 4.8
(`claude-opus-4-8`);
[`src/measure_wave1_delta.py`](src/measure_wave1_delta.py) replays the OLD and NEW
rule over identical inputs so each row isolates the code change alone. Regressions
pinned by [`tests/test_saru_gloss_pipeline.py`](tests/test_saru_gloss_pipeline.py)
(7 passing).

| Defect | Before | After | Note |
|---|--:|--:|---|
| W1.1 distinct root keys in lemma→root map | 3,570 | 3,147 | 434 self-mapped pseudo-root rows split out to `dcs_lemma2root_unresolved.tsv` (net −423 distinct keys); `root_glossary` layer now 1,853 roots |
| W1.2 homograph alternate rows | 9,521 | 11,289 | +1,768 rows; the old code inspected only `cands[1]`, so a genuine 3rd+ homograph was dropped — now the full trail over 9,733 forms |
| W1.3 vidyut ambiguity rows recorded | 0 | 5,952 | `stats['ambiguous']` was a bare counter (4,133 forms); now a `vidyut_ambiguity.tsv` competitor trail mirroring the DCS schema |

Two-pass bootstrap outcome (regen, fixed pipeline): 40,370 lemmas / 1,853 roots;
surface-form resolution 43.6 % (DCS) → 58.7 % (+vidyut +marker). The published
`SanskritRussian` data (still showing 2,021 roots) is **not** regenerated here —
D8 fences republish behind a human GO; a wave-2-gated republish will drop the root
count to ~1,853. Accuracy of these glosses is still unmeasured (coverage ≠
accuracy — wave 2 publishes a per-tier precision figure).

## 12-07-2026 — E2 sense-genre vs DCS attestation (H833 / H350 backlog #3)

Does per-sense citation-genre predict DCS corpus attestation better than the
lemma's aggregate genre? Analysis Opus 4.8 (`claude-opus-4-8`);
[`research/analyze_sense_genre_attestation.py`](research/analyze_sense_genre_attestation.py),
full write-up [`research/SENSE_GENRE_ATTESTATION_FINDINGS.md`](research/SENSE_GENRE_ATTESTATION_FINDINGS.md).
n = 1316 headword lemmas (grouped by normalised IAST, **not** `key1`=root),
49.8% DCS-attested. 5-fold stratified CV AUC (out-of-fold):

| Model | Features | AUC |
|---|---|---:|
| 0 | size only (n_senses, citation mass) | 0.700 |
| A | 0 + lemma union coarse-genre | 0.716 |
| B | 0 + sense-resolution genre | 0.710 |
| A+B | 0 + both | 0.714 |

ΔAUC(B−A) = **−0.006**, 95% bootstrap CI [−0.020, +0.009] → **thesis not
supported**: sense-resolution adds no separable signal over the lemma aggregate
at this scale. Attestation is driven by citation *volume* (genre adds ~+0.016);
per-genre, a *pure* sense in kāvya/purāṇa/kośa/śāstra raises attestation odds
(OR 2.2–3.5, CI>1) but Vedic-only senses do not (OR 1.06) — antiquarian signal.

## 09-07-2026 — pwg_ru medium50 relaunch (H437, post-classifier-unblock)

Windows `h317_w1b`/`w2a`/`w2b` relaunched solo (1-wide) after
[H428](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H428-Sonnet_RussianTranslation_opt2-schema-slim-classifier-unblock_09.07.26.md)
slimmed the opt2 schema. Orchestrator Opus 4.8 (`claude-opus-4-8`); generation
Sonnet 5 (`claude-sonnet-5`, harness-pinned). Full account +
n=50 tally: [`MEASUREMENT_2026-07-08_H317.md`](MEASUREMENT_2026-07-08_H317.md)
(H437 section). Finding: classifier unblocked (agents ran, 0 connection errors),
but every window tripped its `MAX_AGENTS` budget-kill-switch via the self-heal
cascade — the kill-gate miscalibration for dense band-4 nominal singletons is now
the isolated blocker.

| window | cards | agents (spent/max) | net clean (promoted) | defect | transient-null | subagent tokens |
|---|---:|---:|---:|---:|---:|---:|
| h317_w1b | 12 | 61/61 | 1 (`yuvan`) | 2 | 9 | 2,898,353 |
| h317_w2a | 13 | 49/49 | 1 (`ṛtvij`) | 2 | 10 | 1,628,556 |
| h317_w2b | 12 | 52/52 | 0 | 2 | 10 | 2,153,758 |
| **total** | **37** | **162** | **2** | **6** | **29** | **6,680,667** |

medium50 net over the whole H317→H389→H437 arc: **2 / 50 promoted (4%)**;
kill-gate recalibration routed to a bug-hunt handoff (see
[`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) `H437_MEDIUM50_KILLGATE_CASCADE_2026-07-09`).

## 09-07-2026 — pwg_ru card stats rollup (annotate_stats.py)

Script v1.0.0 · Sonnet 5 (claude-sonnet-5)

| metric | value |
|---|---|
| lemmas | 145 |
| records (homonym groups) | 563 |
| senses | 11261 |
| government markers | 0 |
| lemmas with case variation | 0 |
| evidence: provides | 1734 |
| evidence: supports | 1935 |

## 12-07-2026 — pwg_ru card stats rollup (annotate_stats.py)

Script v1.1.0 · Opus 4.8 (claude-opus-4-8)

| metric | value |
|---|---|
| lemmas | 205 |
| records (homonym groups) | 635 |
| senses | 11505 |
| government markers | 508 |
| lemmas with case variation | 2 |
| grammar-joined lemmas (single homonym) | 32 |
| … whitney irregularities counted | 46 |
| grammar ambiguous-homonym (alignment owed) | 17 |
| dcs-matched lemmas | 170 |
| <ls> citations (total) | 41031 |
| evidence: provides | 1699 |
| evidence: supports | 1893 |

Numbers are over the current 205-lemma pwg_ru_translated store (the gitignored working
copy); the fields (`government`, `stats`, `sense_stats`, `record_stats`) are materialised
locally by re-running the annotator chain — the store itself is not committed. Contrast the
09-07 v1.0.0 row above (0 government markers, no grammar counts) with this v1.1.0 row: H777
joined the grammar block (`n_irregularities` no longer stuck at 0) and added the layer /
markup / QA / frequency families.

## 12-07-2026 — PWG case-government census, frozen (H778, government_census.py freeze)

Script v1.1.0 · Opus 4.8 (`claude-opus-4-8`). Corpus-level marker census over the **whole
raw** [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
(sha `430c910f8b0c9229`), frozen to the committed [`src/census_stats.json`](src/census_stats.json)
sidecar so the scan is not re-run on every question. This is the corpus answer to "сколько
таких помет в PWG"; the per-205-lemma store rollup above is the pwg_ru subset.

| metric | value |
|---|---|
| PWG entries scanned | 123366 |
| sense units scanned | 288991 |
| government markers (total) | 3853 |
| … paren-single / variation / mit-phrase | 2309 / 40 / 1504 |
| entries with ≥1 marker | 1476 |
| sense units with ≥1 marker | 3222 |

## 29-07-2026 — RV multi-translation evidence layer, wave 1b (H1844)

Context: [H1844](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1844-Opus_RussianTranslation_rv-multitranslation-typing-w1b_29.07.26.md) — divergence taxonomy, advisory word-level layer B, and the pwg_ru/en pipeline wiring, over the wave-1a spine. Orchestration and adjudication: **Opus 5 (`claude-opus-5[1m]`)**. Divergence typing generator: **`deepseek-chat`** (DeepSeek V3, OpenAI-compatible endpoint). Alignment models: **`bert-base-multilingual-cased`** (committed default) and **`sentence-transformers/LaBSE`**, both via the committed `tm_align.embed_aligner_factory`.

### Divergence-class distribution — pilot, 2,000 stanzas × 6 translator pairs

12,000 labels, of which 11,997 model-decided and 3 deterministic. Cost **$1.0582** (849,276 cache-miss + 1,033,344 cache-hit input, 687,741 output tokens).

| Class | Pilot n=12,000 | Spike n=300 |
|---|--:|--:|
| `agreement` | 37.2 % (4,462) | 37.7 % |
| `semantic_shift` | 54.4 % (6,533) | 62.0 % |
| `lexical_variant` | 6.0 % (719) | 0.3 % |
| `omitted_by_one` | 2.4 % (286) | 0.0 % |
| `added_by_one` | **0.0 % (0)** | 0.0 % |
| coarse: agreement / divergence / omission | 37.2 % / 60.4 % / 2.4 % | 37.7 % / 62.3 % / 0.0 % |

The spike/pilot column split is itself the result: a 300-observation spike read `lexical_variant` as dead (1 label) when its rate at scale is 6.0 %. `added_by_one` is inert at both scales — 0 of 12,000 — which is implausible against Griffith's freely supplied material and is flagged as a prompt/taxonomy defect, not a fact about the corpus.

### Spike S2 — inter-model agreement on the divergence taxonomy (H1901, 29-07-2026)

Three arms, same seeded 50-stanza sample (seed 1844), 300 (stanza × pair) labels each. Arms: **`deepseek-chat`** (DeepSeek, direct), **`openai/gpt-4o-mini`** and **`google/gemini-2.5-flash`** (both via OpenRouter). Orchestration Opus 5 (`claude-opus-5[1m]`). Cost for the two new arms: **$0.054**.

| Pair | n | five-class κ | coarse κ | `lexical_variant` vs `semantic_shift` κ |
|---|--:|--:|--:|--:|
| deepseek ↔ gpt-4o-mini | 300 | 0.222 | 0.235 | **0.089** |
| deepseek ↔ gemini-2.5-flash | 267 | 0.357 | 0.350 | **−0.012** |
| gpt-4o-mini ↔ gemini-2.5-flash | 267 | 0.227 | 0.216 | **0.256** |

Per-arm class usage on the shared sample:

| Class | deepseek | gpt-4o-mini | gemini-2.5-flash |
|---|--:|--:|--:|
| `agreement` | 37.7 % | 20.3 % | 27.3 % |
| `lexical_variant` | 0.3 % | 11.0 % | 6.7 % |
| `semantic_shift` | 62.0 % | 68.7 % | 65.9 % |
| `omitted_by_one` | 0.0 % | 0.0 % | 0.0 % |
| `added_by_one` | **0.0 %** | **0.0 %** | **0.0 %** |

**Verdict: the fine distinction is not separable** (mean κ ≈ 0.11, one arm-pair below chance) — K3 fires. Collapsing to coarse raises κ only to 0.216–0.350, "fair" but not reliable, so the coarse taxonomy is *more* reproducible without being demonstrated *reliable*; the step-8 human gate is the instrument for that and is now more load-bearing, not less.

**Methodological caution, recorded because it nearly shipped as a positive result:** raw agreement on the `lexical_variant`/`semantic_shift` subset reads 89.0 % / 95.1 % / 85.7 % — near-consensus by appearance, worthless in fact. All three models default to `semantic_shift`, so they agree by sharing a prior; κ removes that expected agreement and leaves ~nothing. Under extreme base-rate skew, percent-agreement measures the skew. `added_by_one` never fires in any arm (0/300, 0/300, 0/267), which indicts the instrument rather than the corpus.

### Layer-B word-level precision — 300-token gold, 69 adjudicated

Bar: ≥ 85 % per target language (R14). Annotator Opus 5 (`claude-opus-5[1m]`); sample frequency-stratified, seed 1844.

| Target | n | Correct | Precision | Verdict |
|---|--:|--:|--:|---|
| de | 24 | 7 | 29.2 % | **FAIL** |
| ru | 26 | 5 | 19.2 % | **FAIL** |
| en | 19 | 2 | 10.5 % | **FAIL** |

All three below the bar ⇒ **stop condition 3**: spine A ships alone, layer B ships flagged `low_confidence` and excluded from the contradiction gate, the 0.20 gate is not re-tuned, and the ~8.8 h full-scale run is **not** executed.

### Layer-B alignment run — 150 stanzas per model arm

| Metric | `bert-base-multilingual-cased` | `sentence-transformers/LaBSE` |
|---|--:|--:|
| Candidate token→span alignments | 9,400 | 9,400 |
| Dropped by the 0.20 ALIGN_GATE | **0** | **0** |
| Mutual-argmax confirmed | 30.2 % | 28.6 % |
| Modal confidence bucket | [0.5,0.6) — 6,016 | [0.5,0.6) — 6,462 |
| Throughput | 3.03 s/stanza | 2.83 s/stanza |

A gate that rejects 0 of 9,400 is not a gate: the H1457 A3 threshold (calibrated on 30 mined rows with one negative) carries no discriminative power on Vedic. Swapping the alignment model reproduces the signature rather than fixing it, so the failure is a property of subword-embedding alignment on transliterated Vedic, not of one checkpoint (risk K1/K2 landing as predicted). Full-scale extrapolation: 10,552 stanzas ≈ **8.8 h**, not the 52 h a cold-start probe suggested.

### wisdomlib, four roles (R11) — coverage

| Role | Status | Rows |
|---|---|--:|
| 1 · EN gloss tier | not populated — no gloss text on disk | 0 |
| 2 · tradition disambiguation | zero overlap — Buddhist probe set vs RV lemmas | 0 |
| 3 · fifth gate witness | not populated — same missing gloss text | 0 |
| 4 · AV citation locus | staged — no AV data, wave-1 non-goal (R3) | 0 |

`word_traditions.jsonl` holds 63 Vajrayāna Buddhist terms against the RV's 9,539 lemmas; the join key was verified sound in both directions (`agni`→`agní-`, `indra`→`índra-`), so the empty intersection is correct. **W1.13 cannot be met as written** — recorded rather than asserted away.

## 30-07-2026 — NWS tag half-translation store repair, before/after (H1903)

Continuation of [H1809](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1809-Sonnet_SanskritLexicography_nws-bare-citation-ls-markup_28.07.26.md)'s
domain-only migration (17 rows, `_BRACKET_TAG_DOMAIN` anchored on a Latin diasystem in slot 1) —
its own `nws_ls_markup.py census` reports 0 domain-slot half-translations both before and after
this pass, confirming no overlap/double-processing. This pass covers what that regex's Latin-only
anchor structurally could not reach: a Cyrillic diasystem, the unbracketed `DIA , DOM >` header
form, source-fidelity date/place residue, and one gloss-bracket false-positive.

| Defect class | Rows touched | Fix |
|---|--:|---|
| Cyrillic diasystem and/or domain slot (bracketed) | 16 | Latin restored from the same row's `de` field (never mistranslated), position-aligned, occurrence-count verified |
| `>`-separator dropped when the tag was translated (`ajA` card) | 3 | restored `Ved , unsp >` verbatim from `de` |
| Manuscript date+place ran into the domain slot (source-fidelity — confirmed against the raw `pilot/nws/br_ahm_i.json` scraped card) | 14 (ru+de, 10 distinct rows) | split to 2-slot `[DIA, DOM]` + `(DATE, PLACE)` restored to the body, both fields |
| `[mahat, n. (…)]` gloss-note bracket read as a spurious tag by the shape-only detector | 1 | `[…]` → `(…)` so the shape no longer collides |

**Verify:** a vocabulary-anchored direct-text scan and `validate_final_card_schema.nws_tag_defects()`
(new write-time guard, wired into `validate_sense()`) both report **0** Cyrillic-valued and **0**
comma/digit-bearing NWS tag slots store-wide (11,603 rows, JSONL integrity re-checked — same row
count before/after). `python nws_ls_markup.py census`, `nws_tag_census.py --selftest`,
`g5_card_render.py`, `build_g5_review_sheet.py --selftest`, `validate_final_card_schema.py
--selftest` all pass. The compensating Cyrillic aliases in `g5_card_render.DOMAIN_RU` (`без
уточн.`, `Мед.`, `Линг`, `Лингв`) are retired — see [FINDINGS §504](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md#504-the-nws-tag-layer-reaches-only-22--of-the-ru-store--a-facet-bar-over-it-is-right-but-it-is-not-the-sheets-main-axis).

Model: Sonnet 5 (`claude-sonnet-5`).

