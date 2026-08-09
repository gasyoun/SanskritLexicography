# C4 ceiling remeasure — 5 paired probes (2026-08-04)

_Created: 04-08-2026 · Last updated: 04-08-2026_

**Handoff:** [H2195](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2195-Sonnet_RussianTranslation_askbatch-c4-ceiling-remeasure-2026-08_02.08.26.md) (Sonnet 5, `claude-sonnet-5`) · scope W1-GATE per [PLAN_RussianTranslation_ask_batch_residual_2026-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_ask_batch_residual_2026-08.md) §W1-GATE.

**Method:** five sequential runs of `src/pilot/h963_c4_gate0_probe.py` against the c4 profile (`D:\ClaudeTools\profiles\claude4\.claude`), policy `production_v3` (wall ceiling 80 000 ms, API route ceiling 45 000 ms). Each run reports its own `measured` reading's wall clock (`elapsed_ms`) and API duration (`duration_api_ms`) from `src/pilot/output/h963_c4_gate0_probe_events.jsonl`. No retries, no rerolls — each probe's own verdict was accepted as-is per the probe's fail-closed contract. This is a **measurement-only remeasure inside one sitting**; the pwg-live-gate skill's ≥6h/≤2-per-day probe ration applies only *between* sittings, not within one.

**Model:** Sonnet 5 (`claude-sonnet-5`), 04-08-2026.

## Paired readings (n=5)

| # | UTC time | wall `elapsed_ms` | `duration_api_ms` | classification | wall verdict (< 80 000) | api verdict (< 45 000) |
|---|---|---:|---:|---|---|---|
| 1 | 06:02:35 | 125 899 | 74 907 | success | FAIL | FAIL |
| 2 | 06:05:08 | 54 754 | 29 107 | success | PASS | PASS |
| 3 | 06:09:14 | 112 492 | 84 526 | process (non-success) | FAIL | FAIL |
| 4 | 06:14:41 | 50 855 | 18 748 | success | PASS | PASS |
| 5 | 06:20:19 | 50 269 | 13 536 | success | PASS | PASS |

**Median wall:** 54 754 ms · **Median API:** 29 107 ms · **Pass rate:** 3/5 (probes 1 and 3 breached both ceilings; probe 3 also carried a non-`success` classification).

## Locked fail metric

**Wall clock (`elapsed_ms`)** remains the locked gating metric, per the standing ruling (MG, H2160, option A) that the clock is wall, not API duration. `duration_api_ms` stays a required *second, independent* fail condition per `production_v3` (H2138) — a breach on either metric alone fails the probe — but the single metric named here as the report's locked metric is wall.

## Ceiling floor — unchanged

This 5-probe sample (median wall 54 754 ms, 2/5 probes exceeding the 80 000 ms ceiling by a wide margin — 125 899 ms and 112 492 ms) is consistent with the already-documented c4 **bimodal-route** behavior (H2174: PASS 43 815 ms → NO-GO 75 561 ms → NO-GO 96 520 ms across one day) that `production_v3`'s 80 000/45 000 ms ceilings (H2138, derived from an 8-reading series) were fitted to accommodate. **No ceiling change is warranted from this smaller n=5 sample** — it falls inside the variance the existing ceiling was already fitted against, not outside it. No config edit made; `--stop-before-promote` left as-is; no FINDINGS entry needed since the floor did not move.

## Diff fence

No store writes, no promote-path code touched, no config constants edited. `git diff` from this handoff's worktree shows only this new report file.

_Dr. Mārcis Gasūns_
