# H858 — c4 live gate: HEALTH_NOGO (25-07-2026), rate_limit on the warm-up

_Created: 25-07-2026 · Last updated: 25-07-2026_

Executor: Opus 5 (`claude-opus-5[1m]`). Skill followed:
[/pwg-live-gate](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md)
c4, invoked exactly once — no retry, no re-warm, no reroll. Requested to gate the
paid validation window still owed by
[H858 Part B](https://github.com/gasyoun/Uprava/blob/main/handoffs/H858-Opus_SanskritLexicography_pwg_ru_sense_fidelity_anchor_repair_13.07.26.md)
(code landed [PR #725](https://github.com/gasyoun/SanskritLexicography/pull/725),
[v1.61.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.61.0)).

## Verdict

```
gate_reason = HEALTH_NOGO
verdict     = NO-GO
```

**No canary was run. No production window. Nothing promoted. One paid call was made
(the warm-up), and it was rate-limited.**

## Step 1 — health: the ONE attempt taken today

| Reading | Elapsed | Classification | Output | UTC |
|---|---|---|---|---|
| warm-up | **17 878 ms** | **`rate_limit`** | 831 B | 2026-07-25T16:02:31Z |
| measured | — | **never ran** | — | — |

`live_probe` fail-closed on the warm-up (`warm-up probe rate_limit -> STOP`), so the
measured call was never issued. Latency is not the blocker here — 17.9 s is comfortably
inside the 30 000 ms ceiling. The blocker is **account state**: c4 is rate-limited.

- Profile: `D:\ClaudeTools\profiles\claude4\.claude` · exact model `claude-sonnet-5`
- Prompt: 6 828 B actual (≥ 5 KiB floor), schema-carrying, load-representative
- Binary resolution clean (`[node.exe, cli-wrapper.cjs]`) — not the D-R tooling defect
- Events (append-only): `src/pilot/output/h963_c4_gate0_probe_events.jsonl`

## c4 recent history (same events log, all rows)

The account has not produced a clean pair since 23-07. Two `auth` readings earlier today
precede today's `rate_limit`:

| UTC | Purpose | Elapsed | Classification |
|---|---|---|---|
| 2026-07-22T14:57:34Z | warm-up | 21 280 ms | content |
| 2026-07-22T20:03:04Z | warm-up | 59 831 ms | success |
| 2026-07-22T20:04:47Z | measured | 102 874 ms | auth |
| 2026-07-23T06:06:52Z | warm-up | 40 003 ms | success |
| 2026-07-23T06:09:40Z | measured | 168 352 ms | success |
| 2026-07-24T04:23:53Z | warm-up | 10 838 ms | rate_limit |
| 2026-07-24T07:35:29Z | warm-up | 9 949 ms | rate_limit |
| 2026-07-25T03:16:04Z | warm-up | 17 587 ms | auth |
| 2026-07-25T03:18:34Z | warm-up | 10 918 ms | auth |
| **2026-07-25T16:02:31Z** | **warm-up** | **17 878 ms** | **rate_limit** |

Note the H1447 22-07 LIVE_GO pair (17 972 / 16 621 ms, both success) is **not** in this
log — that run wrote to `pwg_ru/h1447/h1447_gate0_probe_events.jsonl`.

## Probe reporting defect found by this run — the verdict cited a two-day-old reading

The probe printed, among its NO-GO reasons:

```
  - measured latency 168352 ms >= 30000 ms ceiling
```

**No measured call was made today.** 168 352 ms is the row from **2026-07-23T06:09:40Z**.
Cause: [`h963_c4_gate0_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py)
hardcodes `RUN_ID = 'h963-c4-single-profile-gate0-2026-07-16'`, then filters the
append-only log by that constant and keeps the **last row per purpose**. Every run appends
to and re-reads the same bucket, so "RAW READINGS (append-only telemetry, this run_id)"
is the whole history, and `by_purpose` can pair today's warm-up with a stale `measured`.

Today that only made the reason list wrong, not the verdict — the warm-up failed on its
own. **The dangerous direction is the inverse:** a stale `measured` row that was `success`
and under the ceiling, paired with a passing warm-up, yields `GATE-0 VERDICT: PASS`
citing a measured call that was never made this session — a gate that authorizes paid
spend off a two-day-old number. Tracked as
[integrity issue #729](https://github.com/gasyoun/SanskritLexicography/issues/729).

**FIXED 25-07-2026** ([PR #732](https://github.com/gasyoun/SanskritLexicography/pull/732)):
the run id is now minted per invocation (`new_run_id()` = campaign prefix + UTC second +
pid) and the reader (`readings_for`) matches it EXACTLY — never by prefix, which is the
defect itself. The old constant survives as `CAMPAIGN`, a grouping label the H1110/H1447
reports still cite, but it is no longer a read scope. Verdict derivation moved to the pure
`derive_fails()`, and the module now carries a `--selftest` that seeds exactly this log
shape (a historical PASSING pair + a fresh warm-up-only run) and asserts both halves: the
scoped read is NO-GO naming its OWN absent measured reading, and the contaminated pairing
is demonstrably PASS-shaped. Pinned in `window_selftest.test_c4_gate0_probe_run_scope`
(186/186). Re-running today's verdict through the fixed reader gives, correctly:

```
  - warm-up reading absent (probe stopped before it ran)
  - measured reading absent (probe stopped before it ran)
```

for a fresh run that made no call — and for the 16:02Z run, the warm-up `rate_limit` alone.
The 168 352 ms citation cannot recur.

## Resume condition (unchanged, and it is not a formality)

Per the skill's hand-off: **make no paid translation call** — not a canary rerun, not a
bounded window. Resume only after a **NEW** representative ≥ 5 KB c4 health call (Step 1)
returns PASS. A stale or prior GO — including H1447's 22-07 LIVE_GO — does not authorize
resumption. The H858 validation window stays owed and unstarted.

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H858-Opus_SanskritLexicography_pwg_ru_sense_fidelity_anchor_repair_13.07.26.md and execute it.
```

_Dr. Mārcis Gasūns_
