# H4528 — whole-card "hang" forensics and the no-output-progress watchdog on the headless worker

_Created: 14-09-2026 · Last updated: 15-09-2026_

**Handoff:** [H4528](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4528-Opus_RussianTranslation_pwg-ru-whole-card-hang-watchdog_10.09.26.md) (Opus 5, 🔴3 hard). **Executor:** Opus 5 (`claude-opus-5`). **Paid calls:** zero. Every measurement below comes from committed telemetry or from the real `claude` CLI (2.1.251) talking to a fake Messages API on localhost.

## Bottom line

1. **No whole-card hang has ever been shown to be non-terminating.** Every card that was killed and later re-run with a higher ceiling finished. The one kill never followed by a finish is H2250 b5, attempt 1, at 900 000 ms. That result is censored, not proven infinite.
2. **Card shape does not separate killed calls from clean ones.** The same nakzatra card was killed at 180 044, 300 073 and 300 000 ms, and also completed at every wall time from 115 373 to 511 908 ms. The smallest card, rAtra (2 418 B), was killed at 180 025 ms.
3. **The zero-byte stalls hit the 6.8 KB readiness probe, not cards.** On 31-07, tiny pings also hung on a control config dir. That points at the CLI or host, not at content.
4. **Quota has never presented as a hang.** Every recorded rate-limit response came back quickly and with text, in 6 424–42 851 ms. The premise that a throttled CLI hangs instead of returning 429 came from an invalid probe.
5. **The watchdog is built, but it is opt-in.** [headless_worker.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) can now spawn on the CLI's token stream. On that stream the 90 s no-output-progress window is armed, and its kill is stamped `no_progress_kill`. It stays off by default because the evidence cannot yet rule out killing a healthy call (§5).
6. **Both ceilings are unchanged.** `PRODUCTION_HARD_TIMEOUT_MS` is still 600 000 and `PRODUCTION_NO_OUTPUT_PROGRESS_MS` is still 90 000, and nothing was trimmed from the payload or prompt.

## 1. The hang corpus, classified

The corpus was collected read-only from four places: [RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md), the `pwg_ru/h*` memos and their raw folders, the private `pwg-ru-data` gate logs, and Uprava [FINDINGS.md](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md). Rows are sorted into the six probe-reading classes that `/pwg-live-gate` defines:

1. success;
2. hang (treated as a quota candidate first);
3. our own kill at `HARD_TIMEOUT_MS`;
4. an up-front `rate_limit`;
5. a `StructuredRefusal`;
6. `malformed_output`.

### 1a. Whole-card translate calls

| # | date | run | card · shape | elapsed ms | live-gate class | why |
|---|---|---|---|---|---|---|
| 1 | 16-07 | h963_c4_real (Workflow lane) | zaz, upama · 5 606 B skeleton | 180 000 | 3 · own kill | Workflow kill ceiling; a second call was running on the same profile at the same time |
| 2 | 02-08 | h1447-m50 b0 | nakzatra · 80 citation units, 5 495 B | 180 044 | 3 · own kill | ceiling +44 ms, which is setTimeout latency, not a stall |
| 3 | 02-08 | h1447-m50 b1 | sarvatra · 79 units, 3 008 B | 180 134 | 3 · own kill | ceiling +134 ms |
| 4 | 02-08 | h1447-m50b b0 | nakzatra | 300 073 | 3 · own kill | ceiling +73 ms |
| 5 | 02-08 | H2011 b0 | rAtra · 2 418 B (the smallest card) | 180 025 | 3 · own kill | exit 124 at the ceiling |
| 6 | 02-08 | H2158 CLI arm | nakzatra ×2, sarvatra | 300 000 ×3 | 3 · own kill | finished at 375 003 once a higher ceiling allowed it |
| 7 | 03-08 | H2189 paid card | nakzatra · 24 770-char prompt | 300 000 | 3 · own kill | usage `{}` |
| 8 | 06-08 | H2250 b4 | h1209_slice3 card | 300 000 ×2 | 3 · own kill | CLI 2.1.223 |
| 9 | 06-08 | H2250 b5, attempt 1 | same card | **900 000** | 3 · own kill, **censored** | the only kill with no finish after it |

None of the nine rows carries 429, rate-limit or auth text, so none belongs in class 2 or 4. Every killed child left 0 B. Part of the reason is that the tree-kill helper used to discard a killed child's stdout and stderr (FINDINGS §273).

### 1b. Heal and fragment kills

1. **02-08, h1447:** 11 of 16 calls died in the 180 040–180 231 ms band, 9 of them heals. This is class 3, the ceiling band.
2. **02-08, H2011 heal rAtra_f0:** killed at 180 020 and 180 072 ms. The identical call then succeeded at 142 638 ms.
3. **nakzatra#g1.retry1 / #g2:** killed at 300 038 and 300 024 ms. #g2 is the heaviest heal (14 378 B); successes were 8 249–11 476 B.
4. **13-08, H2612 vyavasTA#g1:** killed at 1 800 000 ms. The byte-identical re-issue succeeded in 307 s.

### 1c. Readiness-probe stalls (a ~6.8 KB prompt, not a card)

| date | elapsed ms | evidence | class |
|---|---|---|---|
| 31-07 | 300 544 | 0 B; tiny pings also hung, on a control config dir and on the native exe; CLI 2.1.220 | 2 · hang, CLI/host |
| 03-08 | 297 949 (api 276 183) | 1 146 B, 2 output tokens, returned just under the ceiling | 1 · success, slow |
| 05-08 | 300 099 | 0 B; the API never reported; auth status was logged in, Max plan ([PR #1144](https://github.com/gasyoun/SanskritLexicography/pull/1144)) | 2 · hang, CLI/host |
| 13-08 | 300 198 | 1-byte raw envelope, no 429 text; 97 % memory load on the box | 2 · hang, CLI/host (possible self-contention) |

### 1d. CLI/runtime hang vs content that never terminates

1. **The runtime class exists, and it is small-payload.** The three real zero-byte stalls hit a probe roughly one-seventh the size of a card. On one of those days, tiny pings stalled too. A defect that hits a 6.8 KB prompt and a ping is not a property of card content.
2. **The content class has no evidence.** No card appears only among the killed. Output size drives wall time: output tokens run 4 091–34 215, and output is 64 % of cost per H2158. So a heavy card is slow, and a 180 s or 300 s ceiling killed slow calls that were still alive. The kills land 25–231 ms after the ceiling. That is our timer firing, not a stall the timer caught.
3. **Quota was treated as the first candidate and rejected.** H2299 recorded four `rate_limit` rows, which returned in 9 949–19 903 ms. The 07-08 run printed "You've hit your weekly limit" and returned. FINDINGS §270's claim that a throttled CLI hangs without a 429 rests on a probe that was invalid; the correction is already in FINDINGS.
4. **What the records cannot settle.** Every lane ran `--output-format json`, which writes the whole envelope in one burst at the end, and killed children left no bytes. So no record can tell a still-generating call from a stalled one. The watchdog below exists to make that distinction measurable in future.

## 2. The H2160 b0 presplit trigger

H2160 b0 was nakzatra on its own. It was killed at 180 044 and 300 073 ms, which RUN_FREQ_MAX called "converging on neither".

1. Both kills land at the ceiling plus 44 or 73 ms, so the call was alive when we killed it.
2. The reason b0 ran whole was a presplit predicate bug: the card should have been split into fragments. That was fixed in v1.134.0.
3. [h2160_batch_shape_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2160_batch_shape_probe.py) still says, in lines 1–19, that the card "dies at every ceiling tried… non-terminating rather than slow". The eleven later nakzatra completions, up to 511 908 ms, contradict that. The docstring is left for the residual list rather than edited here, because the handoff scopes this pass to the worker.

## 3. What the CLI actually writes (the fake-server shape probe)

A local fake Messages API (SSE) was run against the real `claude` 2.1.251 binary. Each run logged every stdout arrival and every request the CLI sent.

| run | output args | fake behaviour | stdout arrivals | first byte | longest quiet |
|---|---|---|---|---|---|
| a | `--output-format json` | 20 deltas × 0.3 s | **1** | 10.18 s | 10.18 s (the whole call) |
| b1 | `stream-json --verbose` | 3 s TTFT, 20 × 0.5 s | 4 | 0.60 s | 18.17 s |
| b2 | `stream-json --verbose --include-partial-messages` | same | 40 | 0.29 s | **3.03 s** |
| c | b2 | every request answered 429 | 9 (7 `system/api_retry`) | 0.66 s | 35.4 s, killed at 75 s |
| e | b2 | 25 s of thinking, no pings | 44 | 0.53 s | **25.0 s** |
| f | b2 | 25 s of thinking, pings every 5 s | 46 (2 `stream_event/ping`) | 0.53 s | 10.0 s |

What the runs show:

1. **`json` buffers the whole call.** Any no-progress window on it is a wall-clock timeout under another name. That is why H2878 left the window observe-only on this lane.
2. **Plain `stream-json` is still per-message buffered.** One turn can be silent for its whole generation, 18 s out of 18.8 s here.
3. **Only `--include-partial-messages` gives token-level liveness.** That is the one shape on which a 90 s window can mean anything.
4. **During a quota stall the CLI stays busy retrying.** It emits `system/api_retry` lines (`error_status` 429) while it retries. Counting those as progress would keep a quota-stalled call alive indefinitely. So they are filtered out: only `stream_event`, `assistant`, `user` and `result` lines count.
5. **Thinking is silent on stdout.** The CLI sends `thinking: {type: "adaptive"}` with no `display`, and the API's default display is `"omitted"`. A 25 s thinking phase is therefore 25.0 s of silence. API `ping` events are forwarded as `stream_event/ping`, but only some of them: 2 of 4 got through, so the longest gap was 10.0 s.
6. **A hidden flag exists.** `--thinking-display summarized` puts `display: "summarized"` into the request (checked on the fake server), which would turn thinking into visible deltas. It is not wired in: it is undocumented, and it changes billed output. The `showThinkingSummaries` setting is ignored in `-p` mode.

## 4. Sizing the window from committed telemetry

[h4528_ttft_census.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4528/h4528_ttft_census.py) reads 31 healthy committed envelopes, all from repo paths, and writes [h4528_ttft_census.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4528/h4528_ttft_census.json).

| field (ms) | min | p50 | p90 | max |
|---|---|---|---|---|
| `ttft_stream_ms` (first streamed byte) | 2 480 | 7 210 | 17 248 | 19 759 |
| `time_to_request_ms` | 81 | 927 | 3 621 | 4 042 |
| `ttft_ms` (first *content* token) | 3 122 | 62 487 | 212 292 | **391 798** |
| `duration_ms` | 3 137 | 122 613 | 276 142 | 499 468 |
| `duration_api_ms` | 2 813 | 120 720 | 272 455 | 494 603 |
| `api_gap_ms` (wall − api) | −14 410 | 1 401 | 10 840 | 15 695 |

The worst request-plus-first-byte time is 21 883 ms, 4.1× under the 90 s window, so the window is not tight against first-byte latency. But 9 of the 31 calls waited more than 90 s before their first content token. That silence is the thinking phase from §3. On the token stream it would read as no progress unless the API pings often enough through it.

Full-card completions, n = 19, confirm that slow calls are routine:

1. wall: min 49 404 · p50 189 548 · p90 471 083 · max **511 908** ms;
2. API time: max 494 603 ms;
3. 11 of 19 ran past 180 s, and 3 of 19 ran past 300 s.

The selftest `test_h4528_window_is_sized_from_committed_clean_call_telemetry` reads the census JSON. It fails if any of these stops holding:

1. the first-event figure times three is still under the window;
2. some `ttft_ms` is still over the window (the reason the default is off);
3. `DEFAULT_CLI_TOKEN_STREAM` is `False`;
4. 511 908 ms is still under the hard ceiling.

## 5. Why the watchdog ships OFF by default

The handoff's fail condition is killing a measured-clean slow call. The 511 908 ms call must survive. Two facts together mean default-ON cannot yet be shown to meet that:

1. Up to 391 798 ms of a clean call can pass before the first content token.
2. How often the real API pings during a long thinking phase has never been measured. The fake server shows the CLI forwards some pings, not how many the API sends.

So the switch follows the H2189/H2251 precedent: a manifest tri-state `execution.cli_token_stream` (`true` / `false` / absent = `DEFAULT_CLI_TOKEN_STREAM = False`), plus a cached capability probe of `claude --help` for `--include-partial-messages`. If a manifest asks for it and the CLI lacks the flag, the worker falls back to the buffered lane and says so loudly on stderr.

The flip to ON waits for one confirmatory live call under a fresh `/pwg-live-gate` GO with a `--max-calls` reservation. That call should run on a dense card and record `quiet_ms`, `first_progress_ms` and `progress_events`. If the longest quiet stretch on a healthy dense card stays well under 90 s, ON is safe; otherwise the evidence points at `--thinking-display summarized` or a longer window.

### 5a. Addendum, 15-09-2026 — the confirmatory call was NOT run; the default stays OFF

**Executor:** Opus 5 (`claude-opus-5`), via [H4842](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4842-Opus_RussianTranslation_watchdog-token-stream-default-flip-stale-records_14.09.26.md). **Paid calls:** zero.

1. **No live reading exists.** The call is paid and needs a fresh `/pwg-live-gate` GO with a `--max-calls 1` reservation, given by a human. No GO was given in the H4842 session, so no dense card was run and `first_progress_ms`, `progress_events`, `quiet_ms`, `ttft_ms`, `duration_api_ms` and `api_gap_ms` stay unmeasured on the token stream.
2. **Decision on that evidence: `DEFAULT_CLI_TOKEN_STREAM = False` is unchanged.** The flip rule needs a longest quiet stretch of at most about 30 000 ms on a healthy dense card; with no reading, the two §5 facts still stand. [headless_worker.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py), its selftest pin and LANG_PARITY are therefore untouched, so no restamp receipt is owed.
3. **Neither ceiling moves.** The 90 000 ms window and the 600 000 ms hard ceiling are not the fix, whatever the reading shows.
4. **What the call must record when it runs:** one nakzatra-class whole card (70+ citation units), production profile, `execution.cli_token_stream: true`, through `headless_worker.py`; the six fields above, written into a §5b beside this one. If `quiet_ms` > ~30 000 ms, keep OFF and cost a separate GO for `--thinking-display summarized` (it changes billed output).

### 5b. Addendum, 15-09-2026 14:23Z — human GO given, live gate NO-GO at health; the default stays OFF

**Executor:** Opus 5 (`claude-opus-5`), via [H4842](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4842-Opus_RussianTranslation_watchdog-token-stream-default-flip-stale-records_14.09.26.md), driving the Windows profiles box over Tailscale SSH (the `c1` profile is provisioned only there). **Paid calls:** one, the health warm-up. The canary and the dense card were not run.

1. **The GO was given.** MG answered the H4842 decision brief with «quota is ok», which met its one stated condition (c1 weekly headroom). Ration check: the last `c1` probe was H4527's at 01:35Z, 12 h 48 min earlier, so this was the second and last legal attempt for 15-09 UTC.
2. **Step 1 of `/pwg-live-gate` returned NO-GO on the warm-up.** Code at `07652c51` (includes the H4527 `--safe-mode` probe fix), policy `production_v4`, ceiling 240 000 ms:

   ```
   python src\pilot\h963_c4_gate0_probe.py --account c1 --evidence-dir C:\Users\user\.pwg_ru_evidence
   run_id   h963-c1-single-profile-gate0/2026-09-15T14:23:09Z-pid18072
   warmup   58 316 ms  classification=content  schema_valid=false  cli_safe_mode_effective=true
            duration_api_ms 55 345 · api_gap_ms 2 971 · ttft_ms 42 226 · 4 turns · 1 972 thinking tokens
            structured_output {"ok": false} · stop: completed, is_error false
   measured — (STOP before it ran)
   GATE-0 VERDICT: NO-GO   host commit 86-87 %
   ```

   The first attempt at 14:21Z refused before any spend (`profile already has an active model call`). A no-spend lock test a minute later found the `c1` lock free, so that was another session's brief call, not a stuck lock.
3. **Class: content, not hang, quota or latency.** The call finished well under both ceilings. The model answered the readiness prompt and chose `{"ok": false}`. That is the same answer as the 11-09 18:08Z probe in [H4527 §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_PROBE_SAFE_MODE_DIAGNOSIS_15-09-2026.md), but this time `--safe-mode` was on. So the profile surface does not fully explain the intermittent refusal: safe-mode readings on this code are now 1 PASS and 1 `{"ok": false}`. Raw envelope: `C:\Users\user\.pwg_ru_evidence\h963_c4_gate0_probe_raw_h963-c1-single-profile-gate0_2026-09-15T14_23_09Z-pid18072.txt` on the profiles box; the row is also in `health_probe_log.jsonl` and `c1\h963_c1_gate0_probe_events.jsonl` there. The CLI envelope reports $0.192 at list price (Max route).
4. **Decision: `DEFAULT_CLI_TOKEN_STREAM = False` is unchanged.** Under a health NO-GO the gate forbids the canary and every production call, so the token-stream reading still does not exist. `headless_worker.py`, its selftest pin and LANG_PARITY stay untouched, and no restamp receipt is owed.
5. **Incidental data point for §5, not a flip input.** The probe is on `json`, not the token stream, but its envelope still shows a first content frame at 22 075 ms and `ttft_ms` 42 226 ms on a ~10.7 KB prompt. That is a short prompt, not a dense card, so it says nothing about `quiet_ms` on a 70-unit card.
6. **Resume condition.** The next legal `c1` probe is 16-09-2026 00:00Z or later (at most 2 attempts per UTC day, at least 6 h apart). Two `{"ok": false}` readings on the readiness prompt, one with and one without safe mode, make the probe refusal a diagnosis task for H4527 before it is a reason to re-probe. The flip reading still needs a fresh GO, then a PASS health probe, then a canary GO receipt, then one dense card with `--max-calls 1`.

## 6. What was built

1. **The window is derived from argv, not pinned.** In [execution_contract.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py), `progress_window_ms_for_argv` returns 90 000 only for `stream-json` plus `--include-partial-messages`. It returns `None` (observe only) for `json` and for plain `stream-json`, which corrects H2878's assumption that plain `stream-json` streams.
2. **Liveness counts content lines only.** The new [cli_stream.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cli_stream.py) module does three jobs:
   - `is_progress_line` accepts `stream_event` / `assistant` / `user` / `result` and rejects `system/api_retry`;
   - `result_envelope_text` reduces NDJSON to its final `type: result` line, which has the same keys as the `json` envelope, so `parse_cli_wrapper` is unchanged downstream;
   - `classification_text` feeds only `system`/`result` lines to the auth/rate/connection regexes, so a "429" inside card content (for example "RV. 1, 429") never reads as `rate_limit`.
3. **The progress filter is threaded through the process runner.** [proc_tree.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py) threads `progress_filter` through `run_tree_kill` → `_drain_pipe` with line assembly, and records `progress_events` and `first_progress_ms`.
4. **The kill class is distinct.** `kill_classification` maps `no_output_progress` → `no_progress_kill` and everything else → `timeout`. An auth or rate-limit cause found in the CLI's own lines still wins over both. `no_progress_kill` joins `INFRA_FAILURE_REASONS`, so the audit treats it as transient infrastructure, not a content defect. `kill_timeouts` still counts every kill; `no_progress_kills` is the watchdog's subset.
5. **The probe half is split, as in PR #1837.** [max_account_orchestrator.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py) stamps a probe kill through the same `kill_classification`, and [h963_c4_gate0_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py) counts `no_progress_kill` among connection-class errors. The probe itself stays on `json`.
6. **Ceiling hygiene.** Every successful reading now records `duration_ms`, `duration_api_ms`, `ttft_stream_ms`, `ttft_ms`, `num_turns` and `api_gap_ms = wall − duration_api_ms` separately. A killed attempt keeps its last 20 `api_retry_statuses` as quota evidence. The worker status reports `cli_token_stream_effective` and `progress_window_ms_effective`.

## 7. Fix-parity

The change is classified SHARED in [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) under the new entry `whole_card_no_progress_watchdog_h4528`. The watchdog acts on the CLI child process, below the language layer. The RU and EN spawns take the same argv, filter and kill path, and the target-language field is never read. The 47 entries whose tracked files drifted were re-derived through the receipt [h4528_parity_restamp.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4528_parity_restamp.py). The result is 111 entries and 0 violations.

## 8. Residuals

1. **The confirmatory live call** from §5. It gates the flip to ON, and a human should decide it under a fresh `/pwg-live-gate` GO. The 15-09 GO ended at a health NO-GO (§5b), so the call is still owed.
2. **`--thinking-display summarized`.** It is the candidate fix if the live call shows long silent thinking. It is hidden and changes billed output, so it was not wired here.
3. **Stale records** that were deliberately not edited in this pass — **all four corrected 15-09-2026 by H4842**, each as a dated correction note beside the original text, not a rewrite. One refinement on contact: the 48 414 ms call has three clocks, harness wall 107 659 ms, CLI `duration_ms` 64 109 ms and API 48 414 ms ([h2189_card_rows.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/raw/b6_card_repeat/h2189_card_rows.json), [h2189_card_paid_nakzatra_1.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/raw/b6_card_repeat/h2189_card_paid_nakzatra_1.json)). The correction states all three.
   - [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md), lines 182–201, gives "48 414 ms over 4 turns" as a wall time. It is API time; the real wall was 107 659 ms and the call produced 0 cards.
   - Line 188 of the same file calls "v1.130.0" a "still-open defect". It is a repo release (the bare-cwd change, CHANGELOG `## [1.130.0]`), not a CLI version, and the defect is not open.
   - The `h2160_batch_shape_probe.py` docstring still says "non-terminating" (§2).
   - The H2250 memo and RESULTS_LOG label "1.127.0" a CLI version. That is the same mislabel: it is a repo release.
4. **H2250 b5 attempt 1**, killed at 900 000 ms, stays censored. The watchdog records `quiet_ms` / `first_progress_ms` on any future recurrence, and that is what would settle it.

_Гасунс_
