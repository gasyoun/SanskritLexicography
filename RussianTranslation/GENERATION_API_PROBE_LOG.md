# Generation-API probe log — pwg_ru Workflow launches

_Created: 10-07-2026 · Last updated: 22-07-2026_

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
| 2026-07-12T15:07:27Z | warmup | NO-GO | 35.7s | 0 | 6542B | no_pwg_w07 | H255 | post-H805 2nd reading; 6577-char clean RU reply, 0 conn-err, 48.5K tok. latency=total workflow duration; WORSE than the 31.6s reading ~1h earlier — env not recovering. NO drain window fired. |
| 2026-07-12T15:28:48Z | warmup | GO | 54.0s | 0 | 6542B | no_pwg_w07 | H255 | SCHEMA-CARRYING probe (real StructuredOutput CARDS_SCHEMA path on a live small w07 sub-card, anirvacanIya) — valid RU card in 53.9s, 0 conn-err. HEALTHY for a card call: baseline ~55-105s fixed StructuredOutput latency, kill ceiling 180s (H220). GO overrides the 30s plain-probe ceiling, which does NOT apply to schema/StructuredOutput calls. The plain probes (31.6/35.7s) over-stated degradation; the real generation path is fine. |
| 2026-07-12T15:42:11Z | launch | GO | 54.0s | 0 | 6542B | no_pwg_w07 | H255 | w07 launch after the schema-carrying GO; isolated 1-wide probe was 54s but the ~10-wide window degraded |
| 2026-07-12T16:34:14Z | warmup | GO | 26.0s | 0 | 6491B | h709-reprobe | H709 | H709 SERVER_OUTAGES re-probe: load-representative warm-up (6491B masked band-4 skeleton). GO by mechanical gate but latency ~26s vs 3.3s healthy baseline = marginal/degraded-recovering; expensive medium50 launch deliberately NOT fired (H709 cheapest-task-only rule + medium50 paused on code side). |
| 2026-07-12T17:31:06Z | launch | GO | 0.0s | 0 | — | no_pwg_w07_rq1 | H255 | H811 --max-wide=3 --stagger-ms=2000 requeue of w07's 31 nulls (low-width validation); no pre-launch probe — the point was to test <=3-wide on a still-degraded API |
| 2026-07-12T17:57:40Z | launch | GO | 0.0s | 0 | — | no_pwg_w07_rq2 | H255 | H811 --max-wide=2 --stagger-ms=3000 pass on rq1's 8 residual non-presplit kills (width-sweep step) |
| 2026-07-13T03:15:50Z | warmup | GO | 18.7s | 0 | 6491B | no_pwg_w08 | H255 | H255 pre-flight probe ahead of no_pwg_w08 (20-headword window, start-index 8). duration_ms from Workflow runtime; probe returned valid RU 6245 chars, 0 conn-errors, 51084 tokens. Healthy: below the two prior GO warmups (21180/21050ms). |
| 2026-07-13T03:41:42Z | launch | GO | — | — | — | no_pwg_w08 | H255 | no_pwg_w08 fresh 20-headword/21-subcard window off origin/master (worktree h255-no-pwg-w08). GO probe (18.7s) UNDER-PREDICTED the ~10-wide concurrent window: 1 clean (cUlikA) / 1 defect (cakrikA) / 19 transient 180s-CEIL kill-timeouts on 126-975B skeletons, 0 conn-errors, budget not tripped. Classic H811 concurrency-degradation. Store 11553->11555. 19 transients -> --max-wide=3 requeue. |
| 2026-07-13T04:14:27Z | launch | GO | — | — | — | no_pwg_w08_rq1 | H255 | H811 --max-wide=3 --stagger-ms=2000 requeue of w08's 18 non-content-hard nulls (dropped avy_ahata/avyagra). Throughput jumped 14/18 non-null (vs 1/21 at ~10-wide) confirming H811; but 8/14 returned content-defective on these hard headwords -> 6 clean promoted, store 11555->11562. 4 null (2 fidelity-reject + 2 kill-timeout arvant/b_ahlika). 0 conn-errors. |
| 2026-07-13T05:58:08Z | launch | GO | — | — | — | no_pwg_w09 | H255 | no_pwg_w09 fresh queue window (--start-index 9), run bounded --max-wide=3 from the start given this session's demonstrated ~10-wide degradation. 12/21 non-null (vs w08's 2/21 at ~10-wide) — bounding fixed throughput — but 15/21 are content-defects (9 non-null defect + 6 fidelity-reject), only 3 clean promoted (brahmani/cakrika/hatya). Store 11562->11567. Bottleneck now content-fidelity not concurrency. 0 conn-errors. |
| 2026-07-13T21:43:54Z | launch | GO | — | 0 | — | no_pwg_w10 | H255 | bounded --max-wide=3 --stagger-ms=2000 from launch, no isolated pre-probe (mitigation applied regardless, per w09 precedent); 11/18 non-null (9 real + 2 degenerate), 7 residual (6 fidelity-reject known-class incl. 2 newly-confirmed members arvant/jawAyus, 1 kill-timeout) |
| 2026-07-16T07:59:44Z | warmup | NO-GO | 104.9s | 0 | 6828B | — | H963 | H963 Gate-0 single-profile c4 D-K health attempt (one fresh dated reading, no reroll): warm-up 53290ms / measured 104870ms, BOTH classification=success (no auth/conn/malformed failure), output 1488B/1487B, actual prompt 6828B, exact model claude-sonnet-5, ceiling 30000ms. Pure-latency NO-GO, ~2x WORSE than the 15-07 baseline (29743/52815). Canary NOT launched; store unchanged 11605. Probe tooling >= v1.9.17 natural schema-carrying prompt. |
| 2026-07-18T08:37:19Z | warmup | GO | 15.7s | 0 | 6491B | medium50_canary | H1209 | H1209 step 0a controller-worker LANE probe (Workflow agent(), NOT c4 headless). Single generation call 15.74s (08:32:01.559->17.302), StructuredOutput emit 14.37s, full 2-call schema round-trip 30.15s; 0 conn-errors, schema valid, 30/30 lines, no kill-timeout. Sharp contrast to same-day c4 headless NO-GO (H1110 18-07 98625ms / H963 16-07 104870ms): the direct Workflow-agent() API path is healthy while the profile/headless transport is degraded. subagent_tokens=59291. |
| 2026-07-22T07:12:06Z | warmup | GO | 16.6s | 0 | 6491B | h1447_medium50_gate | H1447 | H1447 Phase 1 health: ONE fresh D-K attempt via h963_c4_gate0_probe.py, profile c4 (D:/ClaudeTools/profiles/claude4/.claude, fingerprint e96ee46471ec057e), route claude-cli-headless. warm-up 17972 ms success + measured 16621 ms success, both strictly < 30000 ms, 0 conn errors -> GATE-0 PASS. Canary verdict + LIVE_GO derivation in pwg_ru/h1447/H1447_C4_LIVE_GATE_2026-07-22.md (canary is a translation-class call; this log's 30 s probe ceiling does not apply to it). Executor session Fable 5 (claude-fable-5); generation model claude-sonnet-5. |
| 2026-07-22T07:20:08Z | warmup | NO-GO | 19.5s | 0 | 6491B | h1447-m50-w1 | H1447 | H1447 Phase 2 bounded starter: bounded_staged_run --execute fleet probe (probe_fleet -> live_probe), c4 warm-up returned a VALID result envelope (subtype success, 1481 B, 19477 ms) whose structured schema result was not {ok:true} -> classification=content, schema_valid=false -> immediate STOP per the warm-up policy. STOP-on-any-NO-GO: zero dispatch, zero production calls, zero usage/cost. All 5 medium50 leases (h1447-m50-w1..w5, 48 keys) remain prepared and unconsumed; resume only after a NEW representative health PASS. Same code path passed twice at 07:03Z (gate-0) -- a content flake 14 min later, not a tooling defect (process/malformed would classify otherwise). Executor Fable 5 (claude-fable-5). |

## Measured launch outcomes

| ts (UTC) | window | clean | agents | tokens | kill-timeouts | conn-err | tripped |
|---|---|---:|---:|---:|---:|---:|:--:|
| 2026-07-10T07:44:19Z | h317_w1b | 0/12 | 58 | 1.80M | 7 | 2 | yes |
| 2026-07-11T12:37:49Z | no_pwg_w03 | 11/27 | 27 | 1.25M | 14 | 0 | no |
| 2026-07-12T15:42:11Z | no_pwg_w07 | 5/36 | 38 | 0.53M | 32 | 0 | no |
| 2026-07-12T17:31:06Z | no_pwg_w07_rq1 | 17/31 | 34 | 1.89M | 15 | 0 | no |
| 2026-07-12T17:57:41Z | no_pwg_w07_rq2 | 5/8 | 10 | 0.68M | 3 | 0 | no |
| 2026-07-13T03:41:43Z | no_pwg_w08 | —/— | — | — | — | — | no |
| 2026-07-13T04:14:28Z | no_pwg_w08_rq1 | —/— | — | — | — | — | no |
| 2026-07-13T05:58:09Z | no_pwg_w09 | —/— | — | — | — | — | no |
| 2026-07-13T21:43:54Z | no_pwg_w10 | 11/18 | 30 | 1.74M | 9 | 0 | no |

_Dr. Mārcis Gasūns_
