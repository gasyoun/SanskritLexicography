# Generation-API probe log — pwg_ru Workflow launches

_Created: 10-07-2026 · Last updated: 10-07-2026_

Append-only, machine-written. Source of truth is
[`src/pilot/generation_api_probe_log.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/generation_api_probe_log.jsonl);
regenerate this table with `python src/pilot/probe_log.py render`. Do not hand-edit.

This log keys on the **reading**, not on a launch. A probe that blocked a launch
(`abort` / `NO-GO`) is a row here, which is exactly what
[`LAUNCH_STATS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md)
cannot see: its denominator counts only windows that actually launched.

Gate (per [`Uprava/SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)
+ H462): 0 `Connection closed mid-response`, latency < 30s, and the
warm-up prompt must be load-representative — >= 5120 bytes of skeleton-shaped
payload (`python src/pilot/probe_log.py prompt`). A trivial one-word probe said GO on
10-07-2026 and the window still degraded; payload size is now part of the verdict.

## Readings

| ts (UTC) | kind | verdict | latency | conn-err | payload | window | H### | note |
|---|---|---|---:|---:|---:|---|---|---|
| 2026-07-10T00:00:00Z | launch | NO-GO | — | 3 | — | h317_w1b | H442 | run-1 per-card cap; BACKFILL from MEASUREMENT doc, time-of-day not recorded; 58 kill-timeouts |
| 2026-07-10T00:30:00Z | launch | NO-GO | — | 3 | — | h317_w1b | H442 | run-2 +depth-1 precursor; BACKFILL, approximate ts; 76 kill-timeouts |
| 2026-07-10T01:00:00Z | abort | NO-GO | — | 3 | — | h317_w1b | H442 | 3rd allowed launch DELIBERATELY NOT FIRED into the degradation (~2.2M tokens saved) -- the row no launch ledger can hold |
| 2026-07-10T07:13:59Z | warmup | GO | 3.3s | 0 | — | h317_w1b | H442 | one trivial sonnet agent() call, per SERVER_OUTAGES row 29 |
| 2026-07-10T07:29:04Z | launch | GO | — | 0 | — | h317_w1b | H442 | regenerated from post-#301 generator; NOT token-comparable to the 61-agent runs (frag-TM grew to 217) |
| 2026-07-10T16:38:24Z | warmup | GO | 24.5s | 0 | 6491B | h317_w1b | H442 | H462 load-representative re-probe (6491B band-4 skeleton, model=sonnet, run wf_0eec1a0f-24f). agent() latency 24531ms = 16:34:31.597Z->16:34:56.128Z, single request req_011CcthaoN2KAwFs7Yk7c3x2 no retry; workflow-total 30422ms incl ~5.9s harness spawn/teardown; TTFT ~10.5s. 0 conn-errors, agents_error=0, result 6275 chars, {Tn} preserved. CAVEAT: 7x slower than the 3.3s trivial probe, only 18% under the 30s ceiling; single-call probe canNOT reproduce the 58-agent concurrency that degraded wf_33290004-c35 (07:44Z: 2 conn-err, 7 kill-timeouts, 0/12 clean, kill-switch tripped). |
| 2026-07-10T16:40:05Z | launch | GO | — | — | — | h317_w1b | H442 | H442/H462 split-pool canary launch, gated by the 24531ms/0-conn GO warmup (wf_0eec1a0f-24f). Split pools: MAX_TRANSLATE=34 + MAX_HEAL=125, per-card heal budget=12, 180s kill-gate, budget-kill-switch on. 8 batches over 12 keys (3 dense pre-split). fresh TM (tm_cards=0), so NOT token-comparable to the frag-TM=217 run wf_33290004-c35. Outcome row to follow. |

## Measured launch outcomes

| ts (UTC) | window | clean | agents | tokens | kill-timeouts | conn-err | tripped |
|---|---|---:|---:|---:|---:|---:|:--:|
| 2026-07-10T07:44:19Z | h317_w1b | 0/12 | 58 | 1.80M | 7 | 2 | yes |
| 2026-07-10T17:03:28Z | h317_w1b | 0/12 | 66 | 2.28M | 66 | 0 | no |

_Dr. Mārcis Gasūns_
