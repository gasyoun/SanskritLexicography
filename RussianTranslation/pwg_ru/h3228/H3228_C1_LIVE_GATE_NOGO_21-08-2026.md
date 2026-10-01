# H3228 — c1 live gate 21-08-2026: HEALTH_NOGO (weekly Pro cap)

_Created: 21-08-2026 · Last updated: 21-08-2026_

Executor: Grok 4.6 (`grok-4.6`). Skill followed:
[/pwg-live-gate](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md)
on **c1** — the operator ruled 19-08-2026 that **c4 is dead, c1 is the only live lane**.
Handoff:
[H3228 (Grok 4.6) — Budgeted monster session: nominal ADAna + ABIra via prepare --allow-over-cost](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3228-Grok_SanskritLexicography_adana-abira-monster-allow-over-cost_21.08.26.md).
`--allow-over-cost` is authorized by that mint. It does **not** override a live-gate NO-GO.

## Step 3 — mechanical verdict

```
gate_reason = HEALTH_NOGO
verdict     = NO-GO
```

Warm-up `classification=rate_limit` (`api_error_status` 429). Measured reading absent
(fail-closed stop before it ran). Canary not started. No lease claimed. No
`--allow-over-cost` prepare. No bounded window. Paid translation spend: **$0**.

The 429 is **not** a per-minute throttle. The CLI envelope says:

> You've hit your weekly limit · resets Aug 23, 2pm (Europe/Moscow)

That is 2026-08-23 14:00 Europe/Moscow = 2026-08-23 11:00 UTC. A second probe in this
UTC day would consume the remaining daily ration against the same weekly cap and would
not be a health reading.

## Step 1 — health: NO-GO

```
GATE-0 VERDICT: NO-GO
  - warm-up classification=rate_limit (not success)
  - measured reading absent (probe stopped before it ran)
```

| Reading | Wall `elapsed_ms` | Route `duration_api_ms` | Classification | Output | Envelope |
|---|---|---|---|---|---|
| **warm-up** | **11 868 ms** | 0 | `rate_limit` (`err_pattern` 429) | 1 167 B | weekly Pro cap; `total_cost_usd` 0; all usage fields 0 |
| measured | — | — | never ran | — | — |

Provenance of the attempt:

- Profile: c1 = `D:\ClaudeTools\profiles\claude1\.claude` · exact model `claude-sonnet-5`
- Prompt 8 617 B actual (≥ 5 KiB floor), schema-carrying
- Binary resolution clean (`[node.EXE, cli-wrapper.cjs]`) — not the D-R tooling defect
- `run_id` `h963-c1-single-profile-gate0/2026-08-21T06:43:26Z-pid38172` (per-invocation, #729)
- Fired from this Grok session, **not** under the `claude1` parent profile (`host_proc_node` 0) — the 13-08 self-contention confound is absent
- Host: 3 706 MB free / 16 229 MB phys, commit 87.94 %, memory load 77 %, `host_proc_python` 238. Loaded, not the 13-08 97 % MemoryExhaustion class. The 429 fired at 11.9 s, so this is quota, not a hang-at-kill.
- Events (append-only, per-account series): `src/pilot/output/h963_c1_gate0_probe_events.jsonl` (gitignored; last row copied below)
- Raw envelope (committed here): [h963_c1_warmup_raw_2026-08-21T06_43_26Z-pid38172.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3228/h963_c1_warmup_raw_2026-08-21T06_43_26Z-pid38172.txt)
- Exactly ONE attempt. No retry, no re-warm, no reroll. Probe ration: **1 of 2** for 21-08 UTC. Next legal c1 health probe ≥ 12:43:26 UTC **and** after the weekly reset.

Free credential check (`claude auth status --json`) immediately before spend: `loggedIn` true, `subscriptionType` `pro`, email `sanskrit.research.institute@gmail.com`. Credentials are not quota. The envelope, not auth-status, is the quota signal.

### Event row (gitignored series, copied)

```
{"schema":"pwg.run_event.v1","ts":"2026-08-21T06:43:38.487Z","run_id":"h963-c1-single-profile-gate0/2026-08-21T06:43:26Z-pid38172","account":"c1","stage":"probe","event":"probe_call","purpose":"warmup","elapsed_ms":11868,"model":"claude-sonnet-5","output_bytes":1167,"classification":"rate_limit","policy":"production_v3","executor_lane":"claude-cli-headless/readiness-schema","schema_valid":false,"duration_api_ms":0,"api_gap_ms":11868,"latency_ceiling_ms":80000,"err_pattern":"429","raw_envelope_path":"h963_c4_gate0_probe_raw_h963-c1-single-profile-gate0_2026-08-21T06_43_26Z-pid38172.txt","host_total_phys_mb":16229,"host_avail_phys_mb":3706,"host_commit_limit_mb":60071,"host_commit_used_mb":52827,"host_commit_pct":87.94,"host_memory_load_pct":77,"host_proc_node":0,"host_proc_python":238}
```

### How this sits in c1's own series

| UTC | Purpose | Wall | Route | Classification |
|---|---|---|---|---|
| 2026-07-26T02:37:26Z | warm-up | 6 424 ms | — | `rate_limit` |
| 2026-08-13T12:40:43Z | warm-up | 300 198 ms | — | `timeout` (our-kill) |
| 2026-08-13T17:50:56Z | measured | 76 990 ms | 47 736 ms | `success` (route NO-GO) |
| 2026-08-19T09:45:12Z | measured | 57 022 ms | 36 059 ms | **PASS** |
| 2026-08-19T12:22:20Z | measured | 40 245 ms | 21 469 ms | **PASS** |
| **2026-08-21T06:43:38Z** | **warm-up** | **11 868 ms** | **0** | **`rate_limit` (weekly Pro cap)** |

19-08 was health PASS / canary NO-GO (null card). Today's sitting never reached the canary. The 19-08 GO is stale (>6 h) and does not authorize spend.

## Step 2 — canary: not run

Health NO-GO stops the gate. Zero canary calls. No receipt.

## Per-target preflight (free; over_ceiling still true)

Live portraits were regenerated this sitting with
`python src/_pilot_gen_merged.py ADAna ABIra` into the gitignored production input dir
(they were absent from the 420-file checkout cache). Preflight used the **filename
stems**, which are the coordinator `run_keys`:

| target | live `key1` | live `safe_name` / `defer_monster` | jsonl `keys` (15-08) | `over_ceiling` | est_usd | est_usd/card |
|---|---|---|---|---|---|---|
| `nominal:ADAna` | `ADAna` (IAST ādhāna) | `_a_d_ana` | `_a_d_ana` (match) | true | 10.31 | 10.31 |
| `nominal:ABIra` | `ABIra` (IAST ābhīra) | `_a_b_ira` | `_a_d_ara` (**mismatch**) | true | 7.03 | 7.03 |

`_a_d_ara` is `safe_name("ADAra")`, not ABIra. That is the h1339 offline-bench fixture mix
the handoff warned about. **Do not translate `_a_d_ara` for the ABIra target.** The live
ABIra key is `_a_b_ira`. The 15-08 jsonl estimate ($10.93 / $3.64) priced the wrong stem;
live ABIra is $7.03 for one card. Bound `--cost-ceiling` at the **live** estimate when a
future sitting gets GO.

Committed JSON:

- [perf_preflight_ADAna.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3228/perf_preflight_ADAna.json)
- [perf_preflight_ABIra.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3228/perf_preflight_ABIra.json)

## Named skip (both windows)

| target | skip reason |
|---|---|
| `nominal:ADAna` | live-gate `HEALTH_NOGO` — weekly Pro cap on c1; no lease, no prepare, no spend |
| `nominal:ABIra` | same sitting stop (handoff: do not open the second window after a named NO-GO; also do not spend H3157's no_pwg keys) |

`--allow-over-cost` was not used. Store/TM untouched. Coordinator journal untouched.

## Resume

1. After **2026-08-23 14:00 Europe/Moscow** (weekly reset named by the envelope).
2. Fresh `/pwg-live-gate` on **c1** (health then canary). A stale 19-08 PASS does not authorize.
3. Probe ration still binds: ≤ 2 c1 health attempts per UTC day, ≥ 6 h spacing. Do not burn the second 21-08 slot against a weekly cap that has not reset.
4. On GO: one target at a time, `max-wide=1`, `--allow-over-cost`, `--cost-ceiling` ≤ that target's **live** `est_cost_usd` (10.31 / 7.03), `--stop-before-promote`. ABIra keys = `_a_b_ira` only.
5. If the first window returns `STOP_COST_UNEVALUABLE`, promote if clean then stop — do not open the second.

This is not a substitute for
[H3157 (Opus 5) — H3144 residual: c1 paid no_pwg window measurement](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3157-Opus_SanskritLexicography_h3144-residual-c1-paid-window-measurement_19.08.26.md).
That lane is blocked by the same c1 weekly cap until the same reset.

_Dr. Mārcis Gasūns_
