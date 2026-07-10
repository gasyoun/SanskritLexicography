# Generation-API probe log — pwg_ru Workflow launches

_Created: 10-07-2026 · Last updated: 11-07-2026_

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

H532 addendum: size-representative proved insufficient — a 24.5s GO on the bare 6.5KB
prompt preceded 0/12 clean with every card >= 146s, because the bare probe omits the
`CARDS_SCHEMA` StructuredOutput + `CONV_TR` system prompt that add most of the per-card
latency. A warm-up now only authorizes a launch if it is **schema-carrying**
(`python src/pilot/probe_schema.py emit` → one agent() with the real production shape),
judged against a per-card-budget ceiling of 90s (= KILL_CEIL/2, safety factor 2).

## Readings

| ts (UTC) | kind | verdict | latency | conn-err | payload | schema | window | H### | note |
|---|---|---|---:|---:|---:|:--:|---|---|---|
| 2026-07-10T00:00:00Z | launch | NO-GO | — | 3 | — | no | h317_w1b | H442 | run-1 per-card cap; BACKFILL from MEASUREMENT doc, time-of-day not recorded; 58 kill-timeouts |
| 2026-07-10T00:30:00Z | launch | NO-GO | — | 3 | — | no | h317_w1b | H442 | run-2 +depth-1 precursor; BACKFILL, approximate ts; 76 kill-timeouts |
| 2026-07-10T01:00:00Z | abort | NO-GO | — | 3 | — | no | h317_w1b | H442 | 3rd allowed launch DELIBERATELY NOT FIRED into the degradation (~2.2M tokens saved) -- the row no launch ledger can hold |
| 2026-07-10T07:13:59Z | warmup | GO | 3.3s | 0 | — | no | h317_w1b | H442 | one trivial sonnet agent() call, per SERVER_OUTAGES row 29 |
| 2026-07-10T07:29:04Z | launch | GO | — | 0 | — | no | h317_w1b | H442 | regenerated from post-#301 generator; NOT token-comparable to the 61-agent runs (frag-TM grew to 217) |
| 2026-07-10T16:38:24Z | warmup | GO | 24.5s | 0 | 6491B | no | h317_w1b | H442 | H462 load-representative re-probe (6491B band-4 skeleton, model=sonnet, run wf_0eec1a0f-24f). agent() latency 24531ms = 16:34:31.597Z->16:34:56.128Z, single request req_011CcthaoN2KAwFs7Yk7c3x2 no retry; workflow-total 30422ms incl ~5.9s harness spawn/teardown; TTFT ~10.5s. 0 conn-errors, agents_error=0, result 6275 chars, {Tn} preserved. CAVEAT: 7x slower than the 3.3s trivial probe, only 18% under the 30s ceiling; single-call probe canNOT reproduce the 58-agent concurrency that degraded wf_33290004-c35 (07:44Z: 2 conn-err, 7 kill-timeouts, 0/12 clean, kill-switch tripped). |
| 2026-07-10T16:40:05Z | launch | GO | — | — | — | no | h317_w1b | H442 | H442/H462 split-pool canary launch, gated by the 24531ms/0-conn GO warmup (wf_0eec1a0f-24f). Split pools: MAX_TRANSLATE=34 + MAX_HEAL=125, per-card heal budget=12, 180s kill-gate, budget-kill-switch on. 8 batches over 12 keys (3 dense pre-split). fresh TM (tm_cards=0), so NOT token-comparable to the frag-TM=217 run wf_33290004-c35. Outcome row to follow. |
| 2026-07-10T20:00:23Z | warmup | NO-GO | 27.1s | 0 | 6546B | no | h317_w1b | H532 | H532 env pre-gate, BARE shape (deliberately non-authorizing under the new rule): wall-clock of the whole 1-agent workflow, startup ~2-5s not subtracted; agent latency ~22-25s vs 3.3s healthy baseline = env still degraded |
| 2026-07-10T20:00:24Z | abort | NO-GO | 27.1s | 0 | 6546B | no | h317_w1b | H532 | H532 pre-gate stop: bare probe still ~7x baseline (>10s recovery bar) - env NOT recovered; schema-carrying gate built+wired (probe_schema.py, SCHEMA_LATENCY_CEIL_MS=90000) but no launch authorized; ~2.3M tokens saved |
| 2026-07-10T20:43:43Z | warmup | GO | 45.9s | 0 | 13906B | yes | h317_w1b | H532 | H532 schema-carrying warm-up (probe_schema.py emit, real PREAMBLE+GRAMMAR+CONV_TR+CARDS_SCHEMA, 1 synth band-4 card): whole 1-agent workflow wall-clock 45.9s (startup ~2-5s not subtracted), 67727 subagent tokens, got_cards=1, 0 conn-errors. Under 90s KILL_CEIL/2 ceiling => GO. Note: ~46s for ONE card is ~14x the 3.3s healthy baseline; env slow but within the schema-representative headroom. |
| 2026-07-10T20:59:24Z | launch | GO | — | — | — | no | h317_w1b | H532 | h317_w1b split-pool launch after H532 schema-carrying GO (warm-up 45.9s < 90s). KILL_SWITCH on: 34 translate + 125 heal pools, 180s kill ceiling. 12 keys / 8 batches / 3 presplit. Expected ~16 agents on a clean run. |

## Measured launch outcomes

| ts (UTC) | window | clean | agents | tokens | kill-timeouts | conn-err | tripped |
|---|---|---:|---:|---:|---:|---:|:--:|
| 2026-07-10T07:44:19Z | h317_w1b | 0/12 | 58 | 1.80M | 7 | 2 | yes |
| 2026-07-10T17:03:28Z | h317_w1b | 0/12 | 66 | 2.28M | 66 | 0 | no |
| 2026-07-10T21:22:37Z | h317_w1b | 0/12 | 59 | 4.17M | 54 | 0 | no |

_Dr. Mārcis Gasūns_
