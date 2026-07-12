# Generation-API probe log — pwg_ru Workflow launches

_Created: 10-07-2026 · Last updated: 12-07-2026_

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
| 2026-07-10T17:35:27Z | launch | GO | — | — | — | no_pwg_w02 | H255 | 20 non-null / 47 cards; 27 transient kill-timeouts (mostly 180s KILL_CEIL on tiny single-fragment skeletons 150-2200 bytes), 4 defect, 16 promoted clean (Bagavat/CAyA/GaRwA/SAKA/SamBu/Sreyas/dayita/duzkfta/sat; gAyatrI fully lost to transient+defect). Same signature as the H442 medium50 degraded-API pattern (SERVER_OUTAGES.md) but on cheap single-fragment cards -- suggests host-level degradation, not heal-lane-specific. Paused further no_pwg windows pending API recovery per H442 guardrail. |
| 2026-07-11T12:26:11Z | warmup | GO | 21.2s | 0 | 6431B | no_pwg_w03 | H255 | H255 pre-flight probe (own translated-lines prompt, load-representative >=5KB); real-time check ahead of resuming the no_pwg drain given SERVER_OUTAGES row 29's still-degraded 11-07 H566 reading (682753ms) |
| 2026-07-11T12:37:39Z | launch | GO | — | 0 | — | no_pwg_w03 | H255 | requeue of no_pwg_w02's 27 transient keys, --no-tm; 13/27 returned non-null, audit downgraded 2 to defect -> 11 clean promoted, 14 kill-timeout (all 180s KILL_CEIL) + 2 defect = 16 requeue-flagged, 0 conn-errors |
| 2026-07-11T14:01:42Z | warmup | GO | 21.1s | 0 | 6492B | no_pwg_w03 | H255 | H255 no_pwg_w03 (fresh 6-headword/13-subcard window, post-STORE-path-fix PR #349) pre-launch probe |
| 2026-07-12T13:45:39Z | warmup | NO-GO | 31.6s | 0 | 6542B | no_pwg_w07 | H255 | Opus4.8-orchestrated Workflow, gen Sonnet5; 6453-char clean RU reply, placeholders intact, 0 conn-err, 48.5K tok. latency=total workflow duration (agent latency ~26-30s after orch overhead) — borderline vs 30s ceiling but a different regime from the 285-683s degraded readings of 10-11 Jul. |

## Measured launch outcomes

| ts (UTC) | window | clean | agents | tokens | kill-timeouts | conn-err | tripped |
|---|---|---:|---:|---:|---:|---:|:--:|
| 2026-07-10T07:44:19Z | h317_w1b | 0/12 | 58 | 1.80M | 7 | 2 | yes |
| 2026-07-11T12:37:49Z | no_pwg_w03 | 11/27 | 27 | 1.25M | 14 | 0 | no |

_Dr. Mārcis Gasūns_
