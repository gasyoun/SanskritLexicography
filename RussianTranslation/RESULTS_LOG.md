# RussianTranslation — results log

_Created: 09-07-2026 · Last updated: 09-07-2026_

Append-only, reverse-chronological. Each entry: date, context, model tier, table.

## 09-07-2026 — pwg_ru medium50 relaunch (H437, post-classifier-unblock)

Windows `h317_w1b`/`w2a`/`w2b` relaunched solo (1-wide) after
[H428](https://github.com/gasyoun/Uprava/blob/main/handoffs/H428-Sonnet_RussianTranslation_opt2-schema-slim-classifier-unblock_09.07.26.md)
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

