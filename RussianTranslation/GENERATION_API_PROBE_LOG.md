# Generation-API probe log — pwg_ru Workflow launches

_Created: 10-07-2026 · Last updated: 10-07-2026_

Append-only, machine-written. Source of truth is
[`src/pilot/generation_api_probe_log.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/generation_api_probe_log.jsonl);
regenerate this table with `python src/pilot/probe_log.py render`. Do not hand-edit.

This log keys on the **reading**, not on a launch. A probe that blocked a launch
(`abort` / `NO-GO`) is a row here, which is exactly what
[`LAUNCH_STATS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md)
cannot see: its denominator counts only windows that actually launched.

Gate (per [`Uprava/SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)):
0 `Connection closed mid-response` and latency < 30s.

## Readings

| ts (UTC) | kind | verdict | latency | conn-err | window | H### | note |
|---|---|---|---:|---:|---|---|---|
| 2026-07-10T00:00:00Z | launch | NO-GO | — | 3 | h317_w1b | H442 | run-1 per-card cap; BACKFILL from MEASUREMENT doc, time-of-day not recorded; 58 kill-timeouts |
| 2026-07-10T00:30:00Z | launch | NO-GO | — | 3 | h317_w1b | H442 | run-2 +depth-1 precursor; BACKFILL, approximate ts; 76 kill-timeouts |
| 2026-07-10T01:00:00Z | abort | NO-GO | — | 3 | h317_w1b | H442 | 3rd allowed launch DELIBERATELY NOT FIRED into the degradation (~2.2M tokens saved) -- the row no launch ledger can hold |
| 2026-07-10T07:13:59Z | warmup | GO | 3.3s | 0 | h317_w1b | H442 | one trivial sonnet agent() call, per SERVER_OUTAGES row 29 |
| 2026-07-10T07:29:04Z | launch | GO | — | 0 | h317_w1b | H442 | regenerated from post-#301 generator; NOT token-comparable to the 61-agent runs (frag-TM grew to 217) |

## Measured launch outcomes

| ts (UTC) | window | clean | agents | tokens | kill-timeouts | conn-err | tripped |
|---|---|---:|---:|---:|---:|---:|:--:|
| 2026-07-10T07:44:19Z | h317_w1b | 0/12 | 58 | 1.80M | 7 | 2 | yes |

_Dr. Mārcis Gasūns_
