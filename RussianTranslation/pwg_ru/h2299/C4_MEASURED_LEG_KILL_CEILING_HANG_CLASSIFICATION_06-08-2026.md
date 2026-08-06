# c4's measured leg hangs to the kill ceiling — classification of the 03-08 and 05-08 NO-GOs

_Created: 06-08-2026 · Last updated: 06-08-2026_

**Handoff:** [H2299](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2299-Opus_RussianTranslation_c4-measured-leg-hangs-to-kill-ceiling-diagnose_05.08.26.md)
· **Model:** Opus 5 1M (`claude-opus-5[1m]`) · **Spend:** none — every number below is read
off ledgers that already existed; no probe call was fired.

**Sources of every figure, without exception:**
[h963_c4_gate0_probe_events.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/output/h963_c4_gate0_probe_events.jsonl)
(27 `probe_call` rows, local-only) and
[h963_c4_gate0_calls.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/output/h963_c4_gate0_calls.json)
(6 run reservations, local-only). Reproduce with
[h2299_series_analysis.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2299_series_analysis.py).

## Verdict in one line

The measured-leg hang is **candidate 2 — prompt/cache-state dependence — with a located,
fixed mechanism**: the gate's probe spawned the CLI from the **repo** working directory, so
every probe call paid full project-context injection, the very tax
[H2158](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2158/ROUTE_AB_MESSAGES_API_VS_CLI_HEADLESS_02-08-2026.md)
measured at **−33 % cost / −30 % wall** and removed from the **paid** lane. Candidate 3
(local scaffolding overhead) is the same defect seen from the other side, not a separate
one. Candidate 1 (quota/throttle) is contradicted by the load ordering in the series.

## Table 1 — `purpose` × `classification` over the full series

Counts, all 27 `probe_call` rows (16-07 campaign through 05-08-2026):

| purpose | auth | content | process | rate_limit | success | timeout | total |
|---|--:|--:|--:|--:|--:|--:|--:|
| measured | 1 | 0 | 1 | 0 | 7 | 1 | **10** |
| warmup | 2 | 1 | 0 | 4 | 10 | 0 | **17** |

## Table 2 — the series row by row, with the route decomposition

`gap_ms` = `elapsed_ms − duration_api_ms`; both are absent before
[#945](https://github.com/gasyoun/SanskritLexicography/pull/958) added `duration_api_ms`.

| ts (UTC) | purpose | class | wall_ms | api_ms | gap_ms | out_B | policy |
|---|---|---|--:|--:|--:|--:|---|
| 2026-07-22 14:57:34 | warmup | content | 21 280 | — | — | 1 281 | v1 |
| 2026-07-22 20:03:04 | warmup | success | 59 831 | — | — | 1 479 | v1 |
| 2026-07-22 20:04:47 | measured | auth | 102 874 | — | — | 992 | v1 |
| 2026-07-23 06:06:52 | warmup | success | 40 003 | — | — | 1 272 | v1 |
| 2026-07-23 06:09:40 | measured | success | 168 352 | — | — | 1 488 | v1 |
| 2026-07-24 04:23:53 | warmup | rate_limit | 10 838 | — | — | 780 | v1 |
| 2026-07-24 07:35:29 | warmup | rate_limit | 9 949 | — | — | 780 | v1 |
| 2026-07-25 03:16:04 | warmup | auth | 17 587 | — | — | 772 | v1 |
| 2026-07-25 03:18:34 | warmup | auth | 10 918 | — | — | 772 | v1 |
| 2026-07-25 16:02:31 | warmup | rate_limit | 17 878 | — | — | 831 | v1 |
| 2026-07-25 18:18:27 | warmup | rate_limit | 19 903 | — | — | 831 | v1 |
| 2026-07-31 18:59:59 | warmup | success | 94 606 | — | — | 1 380 | v1 |
| 2026-07-31 19:01:17 | measured | success | 78 415 | — | — | 1 400 | v1 |
| 2026-08-01 20:21:03 | warmup | success | 39 437 | 21 171 | 18 266 | 1 376 | v2 |
| 2026-08-01 20:21:53 | measured | success | 50 336 | 27 557 | 22 779 | 1 383 | v2 |
| 2026-08-02 05:47:17 | warmup | success | 55 390 | 37 690 | 17 700 | 1 382 | v2 |
| 2026-08-02 05:48:01 | measured | success | 43 815 | 26 386 | 17 429 | 1 382 | v2 |
| 2026-08-02 07:48:25 | warmup | success | 236 328 | 43 646 | 192 682 | 1 382 | v2 |
| 2026-08-02 07:49:40 | measured | success | 75 561 | 29 069 | 46 492 | 1 405 | v2 |
| 2026-08-02 11:05:16 | warmup | success | 55 803 | 28 603 | 27 200 | 1 391 | v2 |
| 2026-08-02 11:06:53 | measured | success | 96 520 | 69 137 | 27 383 | 1 381 | v2 |
| 2026-08-02 12:45:36 | warmup | success | 61 662 | 27 834 | 33 828 | 1 371 | v2 |
| 2026-08-02 12:46:42 | measured | success | 66 291 | 16 445 | 49 846 | 1 365 | v2 |
| 2026-08-03 09:28:34 | warmup | success | 69 082 | 15 315 | 53 767 | 1 387 | v3 |
| **2026-08-03 09:33:32** | **measured** | **process** | **297 949** | **276 183** | 21 766 | **1 146** | v3 |
| 2026-08-05 09:53:33 | warmup | success | 57 207 | 18 310 | 38 897 | 1 368 | v3 |
| **2026-08-05 09:58:33** | **measured** | **timeout** | **300 099** | **—** | — | **0** | v3 |

## Step 1 — is "warm-up passes, measured fails" a pattern or two coincidences?

**Two coincidences, not a pattern — the ordinal position inside a sitting does not predict
failure.** Ten sittings in the series carry both legs; **three** are warm-up-pass /
measured-fail (30 %), and **seven** pass both. Six of those seven clean sittings are the
consecutive 31-07 → 02-08 block, all with the identical second-call ordinal.

| sitting | warm-up | measured | verdict |
|---|---|---|---|
| 2026-07-22 | success | auth | warm-up pass / measured fail |
| 2026-07-23 | success | success | both pass |
| 2026-07-31T18:58:24Z-pid32116 | success | success | both pass |
| 2026-08-01T20:20:23Z-pid5664 | success | success | both pass |
| 2026-08-02T05:46:22Z-pid25748 | success | success | both pass |
| 2026-08-02T07:44:28Z-pid35600 | success | success | both pass |
| 2026-08-02T11:04:20Z-pid11056 | success | success | both pass |
| 2026-08-02T12:44:34Z-pid19136 | success | success | both pass |
| 2026-08-03T09:27:25Z-pid21980 | success | **process** | warm-up pass / measured fail |
| 2026-08-05T09:52:36Z-pid4284 | success | **timeout** | warm-up pass / measured fail |

Sittings whose warm-up already failed (the 24-07 and 25-07 `rate_limit` / `auth` rows) never
reached a measured call at all — `live_probe` STOPs on a bad warm-up — so they cannot bear on
this question either way.

Two facts survive this table and matter more than the headline ratio:

1. **The failure MODE is leg-specific even though the failure RATE is not.** Across 17
   warm-ups there is **not one** `process` or `timeout`; across 10 measured legs there are
   two, both in the last three days. Warm-up failures are all fast account-level refusals
   (9 949–19 903 ms). So the legs do fail differently — but only the recent measured legs
   fail by *hanging*.
2. **The historical record inverts the handoff's framing.** "The warm-up answers, the
   measured call does not" reads as a standing asymmetry; in fact the warm-up leg carries
   **7 of the series' 10 failures**. What is new is not that the measured leg is fragile —
   it is that a *hang* appeared at all, and only after 02-08.

## Step 2 — the three candidates, ruled on the ledgers

### Candidate 1 — quota / throttle (FINDINGS §270: a throttled CLI hangs rather than returning 429) — **CONTRADICTED**

Tested against the call ledger and the sitting spacing, not against `claude auth status`.

- **Load ordering runs the wrong way.** 02-08 fired **8 calls in one UTC day** — four
  sittings, double the ≤2-attempts ration — and **all eight classified `success`**. The two
  failing days fired **2 calls each**, after **20.70 h** (03-08) and **48.33 h** (05-08) of
  idle. Cumulative account pressure predicts the opposite of what happened.
- **This account's throttle signature is documented in the same file and looks nothing like
  a hang.** Four `rate_limit` rows exist (24-07 ×2, 25-07 ×2); every one returned in
  **9 949–19 903 ms** with 780–831 B of provider message. Not one ran long.
- **The 05-08 kill was already screened for an account-level message and none was found.**
  Since [#944](https://github.com/gasyoun/SanskritLexicography/pull/961),
  [`_probe_call`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py)
  routes the `TimeoutExpired` path through `_probe_err_class` on the killed child's drained
  output, precisely so a §270 hang is not mis-filed as `timeout`. It returned the bare
  `timeout` fall-through — the documented result when nothing account-level was said.
- **Cost is not near a cap.** Per-sitting observed spend stayed in the $0.5848–$1.0738 band
  throughout, failing days included.

**Not claimed:** that throttling is impossible. §270's whole point is that a throttled CLI is
indistinguishable from a slow one until something cheap succeeds or fails alongside it, and
this series contains no such control. What is claimed is that nothing in the ledgers
*supports* it, and the load ordering actively argues against it.

### Candidate 2 — prompt-size / cache-state dependence — **SUPPORTED, with a located mechanism**

The call-ledger telemetry is unambiguous. Warm-up leg, chronological:

| sitting | cache_read | cache_creation | out_tok | cost_usd | CLI duration_ms | measured leg |
|---|--:|--:|--:|--:|--:|---|
| 2026-07-31 | 29 005 | **48 352** | 825 | 0.3112 | — | success |
| 2026-08-01 | 81 267 | **81 437** | 679 | 0.5232 | 24 782 | success |
| 2026-08-02 07:44 | 165 429 | **83 896** | 2 819 | 0.5953 | 53 300 | success |
| 2026-08-02 12:44 | **0** | **88 147** | 1 009 | 0.5440 | 35 661 | success |
| 2026-08-03 | **0** | **91 608** | 930 | 0.5636 | 23 836 | **process** |
| 2026-08-05 | **0** | **93 462** | 592 | 0.5697 | 25 116 | **timeout** |

- `cache_creation_tokens` climbs **monotonically, 48 352 → 93 462 (+93 %)** across six
  sittings. Both failures sit at the top of that curve.
- `cache_read_tokens` **collapsed to 0** at the 02-08 12:44 sitting and never recovered.
  Nothing is being reused between calls any more; every call re-creates the whole prefix.
- The 03-08 measured leg shows what that costs when it goes wrong: **276 183 ms of route
  time and $0.4121 spent to return 2 output tokens** (`cache_read` 29 005, `cache_creation`
  62 632). It is not a slow generation — it is a call that connected, paid to build a prefix,
  and produced nothing.

**The mechanism, confirmed rather than inferred.** The probe spawns the CLI from the **repo**
directory. Proof from the c4 profile itself, not from reading the code: the 05-08 warm-up's
`probe_call` row is stamped **09:53:33.852Z**, and the CLI wrote that session into the c4
profile's project bucket
`D:\ClaudeTools\profiles\claude4\.claude\projects\C--Users-user-Documents-GitHub-SanskritLexicography-RussianTranslation\`
at **09:53:51Z** — 18 seconds later. The bucket name *is* the spawn cwd. The cause in code:
`_probe_call` called `run_tree_kill(...)` without a `cwd`, and that parameter defaults to
`None`, i.e. inherit.

That is exactly the tax
[H2158](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2158/ROUTE_AB_MESSAGES_API_VS_CLI_HEADLESS_02-08-2026.md)
measured on identical back-to-back calls — repo cwd **$0.3036 / 26–29 s** against bare cwd
**$0.2040 / 19–20 s**, i.e. **−33 % cost and −30 % wall** — and removed from
[`headless_worker`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
via `bare_cli_cwd()`. **The gate never adopted it.** The repo's own
[cache_prefix_stability_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_prefix_stability_probe.py)
had already established the same causal chain ("if `bare` creates materially less than
`repo`, the varying prefix is project context injection").

### Candidate 3 — local spawn / scaffolding defect — **SUPPORTED, but it is candidate 2, not a second finding**

The handoff's own test: "05-08's warm-up shows CLI `duration_ms` 25 116 against wall 57 207,
i.e. 32 091 ms outside the CLI. If that overhead is growing across the series it is ours, not
the route's." Computed over every warm-up that carries both numbers:

| sitting | wall_ms | CLI duration_ms | outside the CLI |
|---|--:|--:|--:|
| 2026-08-01 | 39 437 | 24 782 | **14 655** |
| 2026-08-02 07:44 | 236 328 | 53 300 | **183 028** |
| 2026-08-02 12:44 | 61 662 | 35 661 | **26 001** |
| 2026-08-03 | 69 082 | 23 836 | **45 246** |
| 2026-08-05 | 57 207 | 25 116 | **32 091** |

It is growing (14 655 → 32 091 ms outside the CLI, with one 183 s outlier), and it is ours.
But it is **the same defect**: project-context injection is paid both as prefix tokens (the
route half, candidate 2) and as local discovery/startup work (the wall half, candidate 3).
Filing them as two findings would double-count one cause.

## Correction to the handoff's own framing — the two deaths are one death

H2299 sets 03-08 (route failure — "the call came back") against 05-08 (our kill — "it never
came back") as **opposite** evidence. Mechanically that is right, and the distinction the
gate is required to draw is real. But on the numbers they are the *same* stall separated by
luck:

| | 03-08 measured | 05-08 measured |
|---|--:|--:|
| wall `elapsed_ms` | 297 949 | 300 099 |
| distance from the 300 000 ms ceiling | **2 051 ms inside** | **99 ms outside** |
| useful output | **2 output tokens** / 1 146 B | 0 tokens / 0 B |

**0.7 % of the budget** separates them, and 2 output tokens is functionally the same nothing
as zero. This does not weaken the handoff's central ruling — it strengthens it: 03-08 is a
**second reading of the same 0-output stall**, not an unrelated route failure, so the failing
sample is 2, not 1.

## Why a ceiling re-fit is the wrong instrument here — stated so it is not re-proposed

The documented response to a failing lane is
[H2138](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2138-Opus_RussianTranslation_probe-ceiling-paired-readings-946_01.08.26.md)
re-derivation. **It does not apply to this shape, and a future session must not open it for
this reading.**

1. **H2138 answers a distribution question** — "the healthy median sits too close to the
   ceiling, so honest readings are being refused." It re-fits a threshold to observed
   *values*.
2. **05-08 produced no value to fit.** `output_bytes` 0, no `duration_api_ms`, no envelope.
   The row's `elapsed_ms` 300 099 is not a latency measurement — it is the kill constant
   `HARD_TIMEOUT_MS` (300 000) plus 99 ms of teardown. Fitting a ceiling to it fits the
   ceiling to itself.
3. **No ceiling value admits it.** A wall ceiling above 300 099 cannot pass a call the
   harness already killed at 300 000; raising `STRICT_CEILING_MS` alone is inert unless
   `HARD_TIMEOUT_MS` moves too — and if it did, the "pass" would be a reading with no content
   in it. That is strictly worse than the NO-GO, because it converts a real defect into a
   green gate.
4. **The v3 `api_ceil_ms` guard cannot fire either.** It gates on `duration_api_ms`, which is
   absent by construction on a killed call — the code already declines to let absent
   instrumentation flip a verdict.

The apparent "all v3 measured legs fail (2/2), all v2 pass (5/5)" correlation is **not** a
reason to revisit v3's numbers. v2→v3 changed `latency_ceil_ms` 65 000→80 000 and added
`api_ceil_ms` 45 000 — both are *verdict thresholds*, which cannot make a call hang. The
policy label is a date marker for the 02-08/03-08 change window, not a cause.

## The fix that landed

**One line, and it is a two-defect fix.**
[`_probe_call`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py)
now spawns with `cwd=bare_cli_cwd()` — **derived from the paid lane's own helper, never a
literal path**, so gate and lane cannot drift apart again.

1. **Representativeness (the more serious defect).** The gate exists to predict the paid
   lane. Spawning from a different directory meant it **priced a different call** than the
   lane it gates — ~33 % more cost and ~30 % more wall, uncontrolled. Every GO/NO-GO in the
   series above was issued on that basis.
2. **Headroom.** That ~30 % is the margin against the 300 s kill which the 03-08 and 05-08
   measured legs ran out of.

Pinned by a new assertion in
[max_account_orchestrator_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator_selftest.py),
verified **red before the fix** (`AssertionError: probe spawned with cwd=None …`) and green
after. It asserts equality with `headless_worker.bare_cli_cwd()`, not a path literal.

## Guardrail compliance and honest caveats

- **No probe call was fired.** The 05-08 ration stands at 1 of 2 used; the next legal sitting
  is **15:58:34 UTC on 05-08**, anchored on the last `probe_call` at `09:58:33.976Z` per
  [FINDINGS §319](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) — never on the
  run-id start.
- **`observed_cost_usd: 0` on the 05-08 measured call means NOT EVALUABLE, not free.** The
  run carries `cost_evaluable: false` / `unevaluable_calls: 1`; the killed call still bills.
  For the same reason its `cache_read_tokens: 0` / `cache_creation_tokens: 0` are **absent,
  not measured** — no envelope survived the kill — and must never be read as data points on
  the cache curve above. Every per-sitting cost in this document is a **floor**.
- **The 02-08 over-ration is recorded, not endorsed.** That day fired 8 calls against a
  ≤2-attempts-per-day cap. It is load-bearing evidence against candidate 1 and simultaneously
  a ration breach worth its own note.
- **What this pass does NOT establish.** That the fix makes the gate pass. Confirming that
  requires a paid sitting, which this handoff was explicitly forbidden to spend, and a single
  green reading would not be proof either. The claim here is narrower and fully supported:
  the probe was demonstrably paying a cost the paid lane does not, that cost was growing
  monotonically, and both failures sit at the top of the curve.
- **Series comparability.** Readings after this change are **not** wall-comparable with the
  27 rows above; they price a different (correct) call. Treat 05-08 as the last row of the
  old series.

_Dr. Mārcis Gasūns_
