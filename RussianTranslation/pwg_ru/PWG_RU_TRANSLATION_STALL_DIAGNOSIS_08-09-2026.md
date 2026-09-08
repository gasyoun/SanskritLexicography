_Created: 08-09-2026 · Last updated: 08-09-2026_

# Why the PWG→RU translation has produced nothing for two months — measured diagnosis, 08-09-2026

Answer to MG's question of 08-09-2026: «Why is the translation not going on for 2 months now?»
Every number below was probed live on the Windows box on 08-09-2026 (Opus 5, `claude-opus-5[1m]`),
not read from a status row. This document is the evidence base for
[H4342](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4342-Sonnet_SanskritLexicography_pwg-ru-translation-stall-full-audit_08.09.26.md)
— *PWG-RU translation stall — full audit: can the pipeline still produce, or is it retired?* —
minted the same pass (🔴3 hard, launch box Windows). §9 below is that handoff's acceptance list.

## 1. The one-sentence answer

**Translation output stopped on 13-07-2026 and never restarted.** The last production window in
[`src/pilot/RUN_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md)
is `no_pwg_w10` (13-07-2026); since then the estate has minted 347 handoffs against this pipeline,
added **86 rows** to the store, and shipped **zero** promotion records. The five causes are stacked,
not alternative — fixing any one of them alone still yields zero cards.

## 2. Measured: the store has not grown

Store: [`tm/pwg_ru_translated.jsonl`](https://github.com/gasyoun/pwg-ru-data/blob/main/tm/pwg_ru_translated.jsonl),
11,519 rows, sha256 `79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65`.
Rows carry `provenance.generated_at`; the histogram is unambiguous.

| Generation date | Rows | Share |
|---|---:|---:|
| 29-06-2026 | 6,026 | 52.3 % |
| 30-06-2026 | 2,530 | 22.0 % |
| 01-07-2026 | 1,192 | 10.3 % |
| 03-07 → 06-07-2026 | 1,313 | 11.4 % |
| 09-07 → 14-07-2026 | 363 | 3.2 % |
| **15-07 → 24-08-2026 (41 days)** | **0** | **0 %** |
| 25-08 → 29-08-2026 | 95 | 0.8 % |
| **30-08 → 08-09-2026 (10 days)** | **0** | **0 %** |

- 99.2 % of the entire store was generated in the **sixteen days** 29-06 → 14-07-2026.
- The 95 August rows come from generator `autosplit_requeue.topup`, not from a production window —
  they are repair top-ups of existing cards, not new translation.
- Review state: 11,514 `ai_translated`, 3 `approved`, 2 `needs_review`. **Human review has touched
  5 rows of 11,519** (0.04 %), so the "translated" figure has never been ratified at scale either.

Lane position from [`progress_dashboard/progress_data.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/progress_data.json)
(snapshot 07-09-2026): nominal lane **41 promoted of 5,039 candidates (0.81 %)**, 4,251 runnable;
verb lane **48 promoted of 1,882**, **0 runnable**, 701 blocked. The headline "41.4 % coverage" in
the same file is `dcs_attested_headwords / total_headwords` — a corpus-attestation ratio, **not**
translation progress. Nothing on the dashboard reports "translated share of PWG", which is part of
why the stall stayed invisible for two months.

## 3. Cause 1 — the production lane was paused on 09-07-2026 and never un-paused

`progress_data.json` carries the pause verbatim:

- `medium50_pause_reason.code`: `killgate_cascade`
- label: *"paused — kill-gate/self-heal budget cascade on dense band-4 nominal singletons"*
- detail: H437 isolated the cascade (2/37 clean, every window tripped `MAX_AGENTS`); **H442 scoped
  the recalibration and the detail text still says "still open"**.

Both handoffs are dated **09-07-2026** — [H437](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H437-Sonnet_RussianTranslation_pwg-ru-medium50-resume-post-h428_09.07.26.md)
and [H442](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H442-Opus_RussianTranslation_pwg-ru-killgate-recalibration-nominal-medium_09.07.26.md).
Both sit in `handoffs/archive/`, i.e. the registry treats them as terminal, while the dashboard the
same estate publishes says the condition they describe is unresolved. **That contradiction is the
two-month gap.** The registry closed the tickets; nobody closed the cascade.

This is the primary finding. Everything in §4–§7 is downstream of it: after 09-07 there was no
bulk production path, only repair attempts on the tail of the last window.

## 4. Cause 2 — the "nonstop" lane has never run once

Live `Get-ScheduledTask` / `Get-ScheduledTaskInfo` on the box, 08-09-2026:

| Task | State | Last run | Result |
|---|---|---|---:|
| `PWG-RU nonstop pc lane` | **Disabled** | **30.11.1999** (never) | 267011 (never run) |
| `PWG-RU h4213 heal wave` | Ready | 06.09.2026 19:15:15 | **3** (failed) |
| `PWG-RU h4213 heal wave r2` | Disabled | — | — |
| `PWG-RU spotcheck pc lane` | Ready | daily 07:00 | 0 (green) |
| `PWG citation coverage refresh` | Ready | — | — |
| `PWG_c1_gate0_probe_H2647` | Ready | — | — |

The lane that was supposed to make translation continuous — `PWG-RU nonstop pc lane`, the
[`pc_lane_tick.cmd`](https://github.com/gasyoun/pwg-ru-data/blob/main/pc_lane_tick.cmd) job stood up
under H2175 — **is disabled and has a never-run sentinel timestamp**. What does run every day is the
**spotcheck**. The estate has been faithfully measuring an assembly line that was switched off before
it ever started.

Corroboration: every `telemetry/spotcheck_*.json` from 27-08 to 07-09 reports `population: 0` and
`promotion_records: []`, and the gate evidence file states the reason in its own words —
*"no auto-promotion landed on 2026-09-07: sampling 10 % of nothing is not a failure of the sampler"*.
`output/coordinator/promotions/` holds **0 files**.

## 5. Cause 3 — the generation fleet is one account, and it is the human's own

[`src/pilot/max_orchestrator.sqlite`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_orchestrator.sqlite)
`accounts` table, read read-only on 08-09-2026, holds **exactly one row**:

| name | config_dir | validated | parked_until | updated_at |
|---|---|---:|---:|---|
| `c1` | `D:\ClaudeTools\profiles\claude1\.claude` | 1 | 0 | 2026-09-07T00:14:37Z |

`claude1` is the profile the interactive Claude Code session runs on. So the production lane and the
human's own working session draw on **the same rate-limit pool** — every interactive hour is an hour
the lane cannot generate, and the lane's 429s are self-inflicted by design.

Profile credential sizes on `D:\ClaudeTools\profiles\` (size is the health signal; contents not read):
`claude1` 509 B (healthy) · `claude2` 504 B · `claude3` 466 B · **`claude4` 281 B** · **`claude5` 281 B**
· `claude6` **no credentials file at all**. 281 B is the needs-`/login` shape. The 06-09 wave logged
exactly that: `c4: profile validation failed: not logged in`, likewise c5 and c6.

MG's 06-09 ruling «claude 4 5 6 is off the game for now» is recorded and stands — but its consequence
was never written down: **it reduces the fleet to a single shared account**, which is a throughput
ceiling, not a temporary inconvenience. Two `MG @DO` rows to authenticate c5/c6 have been open in the
GTD rollup since 22-07-2026, both marked "OPTIONAL … NOT a prerequisite". On a one-account roster that
classification is no longer true.

## 6. Cause 4 — the last three launch attempts died on a non-idempotent window id

[`src/pilot/output/h4213_wave_launch.log`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/output/h4213_wave_launch.log)
records all three runs of the one-shot Task Scheduler job:

1. **06-09 19:15:32** — probe GO on c1, then `FAIL: headless window id already exists: h4213can02`
   → `STOP: canary prep failed`. The launcher hard-codes the canary window id, so a prep that
   already exists makes the retry unrunnable. **Zero spend, zero cards.**
2. **07-09 03:14:05** — canary prep succeeded this time (manifest v2 sealed, FRAGS armed at
   `AUTOSPLIT_LS_BUDGET=6`), then `fleet probe STOP on account c1: warm-up probe content -> STOP`
   → `STOP: no canary wf_output`.
3. **07-09 03:14:46** — `FAIL: headless window id already exists: h4213can02` again.

Run 2 left the window id registered, which guaranteed run 3 would fail the way run 1 did. The job is
therefore **not re-armable without a manual id bump** — and it has not been re-armed since.
`PWG-RU h4213 heal wave r2` is disabled.

Standing gate on top of this: `bounded_staged_run.py --execute` refuses without a canary GO receipt
(H2159) — correct as a safety design, but it means a failed canary blocks the entire wave, and the
canary is exactly the step that keeps failing.

## 7. Cause 5 — the lane is frozen again, and the unfreeze is a human act

[`gatelogs/lane_freeze_pc.json`](https://github.com/gasyoun/pwg-ru-data/blob/main/gatelogs/lane_freeze_pc.json),
dated **07-09-2026**, `executed: true`:

- reason: `"SAN-LOSS reached the store (unconditional freeze)"`
- `rows_removed: 0`, `windows_reverted: []`, requeue worklist file is **empty** (0 bytes)
- `unfreeze`: `"HUMAN act: delete this file after the weekly review rules on it"`

The three offending rows are the same three every day: `m_a~~h0_zz_pw03` (SAN-LOSS 7/9),
`pat~~h0_zz_pw00` (0/2), `asvatantra~~h0_zz_pw` (1/3). They are July-era rows promoted under the old
"promote regardless of flag" guardrail. This freeze was already ruled on once — MG's «(b) hold until
the H4204 census lands» was satisfied on 06-09 and the file was deleted — and the daily spotcheck
**re-created it on 07-09**, because the three rows are still in the store. The freeze is a loop, not
an event: it will re-fire every morning at 07:00 until those three rows are repaired or exempted.

## 8. Where the two months of effort actually went

Handoff files naming `RussianTranslation` or `pwg` in
[`Uprava/handoffs/`](https://github.com/gasyoun/Uprava/tree/main/handoffs) (live + archive), by mint month:

| Month | Handoffs minted | Store rows added |
|---|---:|---:|
| July 2026 | 206 | ~363 (all before 15-07) |
| August 2026 | 121 | 95 (repair top-ups) |
| September 2026 (to 08-09) | 20 | 0 |
| **Total** | **347** | **458** |

**1.3 rows of translation per handoff minted.** The work was real — gate hardening, provenance,
mask parity, self-heal routing, span-drop fidelity, TM mirror reconciliation, four-tier microstructure
— but all of it is *infrastructure around* a lane that has not generated since 14-07. No handoff in
the September set has "produce N translated cards" as its acceptance criterion.

## 9. What the audit handoff must settle

1. **Is the H442 kill-gate cascade actually fixed?** The dashboard says open, the registry says
   archived. Requeue one dense band-4 nominal window and measure; that single result decides whether
   the pipeline can produce at all.
2. **Throughput arithmetic before any restart.** At the observed best rate (6,026 rows on the single
   best day, 29-06) versus the observed real rate (458 rows in 71 days ≈ 6.5/day), completing
   5,039 nominal candidates takes between one day and two years. The audit must state which regime is
   real on a one-account roster, with a measured number, before anyone re-arms a lane.
3. **Re-arm or retire `PWG-RU nonstop pc lane`.** A disabled task that has never run is either fixed
   this pass or deleted; keeping it listed is what made "nonstop" readable as a live capability.
4. **Break the freeze loop.** Repair, requeue or explicitly exempt the three SAN-LOSS rows so the
   07:00 spotcheck stops re-freezing the lane.
5. **Make the canary launcher idempotent** — unique window id per attempt — so a failed run does not
   poison the next one.
6. **Publish a translation-progress figure that means translation**, not DCS attestation, on the
   kitchen dashboard, so a 41-day production gap cannot repeat unnoticed.

## 10. What is NOT the cause — ruled out this pass

- **Not rights, licensing or data availability.** Inputs are present; `raws/` and the reverse-dictionary
  master (266,820 headwords) are intact and backed up on three machines.
- **Not a lost store.** 11,519 rows verified byte-exact against the `pwg-ru-data` mirror (sha above);
  the H3690/H3947 lineage reconcile closed on 05-09.
- **Not missing quality tooling.** Gates, judges, masks, self-heal and provenance all work; the
  spotcheck runs green daily. They have had nothing to inspect.
- **Not an unfixed bug in generation.** The 07-09 03:13 canary prep succeeded end to end and sealed a
  v2 manifest. Generation prep is healthy; the *launch* is what fails.

_Dr. Mārcis Gasūns_
