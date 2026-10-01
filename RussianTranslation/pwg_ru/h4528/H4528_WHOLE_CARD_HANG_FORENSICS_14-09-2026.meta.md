# Metadoc — H4528_WHOLE_CARD_HANG_FORENSICS_14-09-2026.md

_Created: 14-09-2026 · Last updated: 14-09-2026_

- **Purpose:** the forensic classification of every recorded pwg_ru whole-card "hang" against the six `/pwg-live-gate` probe-reading classes; the measured CLI output shapes; the telemetry that sizes the no-output-progress window; and the reason the H4528 watchdog ships opt-in.
- **Audience:** whoever runs the next paid pwg_ru window or decides to flip `execution.cli_token_stream` to ON; maintainers of `headless_worker.py` / `proc_tree.py`.
- **Provenance:** H4528, Opus 5 (`claude-opus-5`), 14-09-2026. The corpus was collected read-only from committed RESULTS_LOG rows, `pwg_ru/h*` memos and raw folders, the private `pwg-ru-data` gate logs and Uprava FINDINGS. The shape probe ran the real `claude` 2.1.251 against a localhost fake Messages API. Zero paid calls.
- **Improvement backlog (ranked):**
  1. Add the confirmatory live call's `quiet_ms` / `first_progress_ms` / `progress_events` readings to §4–§5 once a `/pwg-live-gate` GO exists, and restate the default decision on that evidence.
  2. Measure how often the real API pings during adaptive thinking. It decides whether ON is safe without `--thinking-display summarized`.
  3. Fold the stale-record corrections (§8.3) into RUN_FREQ_MAX.md, the h2160 probe docstring and the H2250 memo in a records-only pass.
- **Limitations:**
  - Killed children in the historical corpus left no bytes, so "alive vs stalled" for those kills is inferred from timing (kills at ceiling +25–231 ms), not observed.
  - Ping forwarding was measured on a fake server, not the real API.
  - The census is n=31 envelopes and n=19 full-card completions.
- **Revision history:**
  - 14-09-2026 — created (H4528).

_Гасунс_
