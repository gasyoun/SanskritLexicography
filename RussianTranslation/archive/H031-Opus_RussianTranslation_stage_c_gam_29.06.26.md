# Handoff — Claude Code Max Stage C `gam`

Date: 2026-06-29

Audience: Claude Code Max / Max Workflow operator.

Goal: begin Stage C with **one root only: `gam`**. The prior Stage C stale-input
hold has been cleared structurally; do not batch `gam`, `yuj`, `vid`, and `han`
together.

## Current State

Stage A + B are accepted for the staged evidence run:

| root | status |
|---|---|
| `sTA` | accepted with documented F-gate-nws-fp residuals |
| `BU` | accepted with same documented-FP pattern |
| `as` | accepted with same documented-FP pattern |
| `i` | accepted with same documented-FP pattern |

Stage C stale generated inputs were pruned and rechecked on 2026-06-29:

| root | stale files pruned | structural status |
|---|---:|---|
| `gam` | 206 | PASS: 127/127 raw + portrait, 0 stale |
| `yuj` | 90 | PASS: 60/60 raw + portrait, 0 stale |
| `vid` | 70 | PASS: 55/55 raw + portrait, 0 stale |
| `han` | 128 | PASS: 78/78 raw + portrait, 0 stale |

This handoff supersedes the old Stage C "hold until pruned/rechecked" block in
`HANDOFF_2026-06-29_claude_code_max.md`.

## Non-Negotiable Rules

- Run **only `gam` next**. Do not start `yuj`, `vid`, or `han` until `gam` is
  audited and the result is understood.
- Do not combine roots into one `wf_output.json`.
- Do not use stale `wf_output.json` as evidence.
- Do not do a broad Sonnet re-loop to chase the known F-gate-nws-fp.
- Do not claim print readiness from this run. G5/G6/G7/G10 still decide that.

## Next Commands

From:

```powershell
C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation
```

Confirm status:

```powershell
python src\pilot\root_window_status.py gam
```

Expected:

- `PASS: root window is structurally ready`
- `sub-cards: 127`
- raw files `127 declared / 127 present / 0 stale`
- portrait files `127 declared / 127 present / 0 stale`
- next command `python src\pilot\gen_opt_harness.py gam`

Generate the optimized harness:

```powershell
python src\pilot\gen_opt_harness.py gam
```

Then in Claude Code Max / Max Workflow, run:

```text
src/pilot/run_pilot_wf.opt.js
```

Save the Workflow result as:

```text
wf_output.json
```

Audit locally:

```powershell
python src\pilot\audit_window.py wf_output.json --root gam --write-requeue
```

If Max reports timing/token fields, prefer:

```powershell
python src\pilot\audit_window.py wf_output.json --root gam --write-requeue `
  --wall-clock-minutes <minutes> `
  --max-cache-read-tokens <n> `
  --max-cache-create-tokens <n> `
  --max-output-tokens <n> `
  --max-total-tokens <n>
```

If weekly cap fires, also add:

```powershell
  --weekly-cap-fired --weekly-cap-cumulative-tokens <n>
```

## Decision Rule After Audit

Inspect:

```text
src/pilot/output/audit_window.report.md
src/pilot/output/window_status.md
src/pilot/output/requeue.keys.txt
src/pilot/output/judge_sample.keys.txt
```

Use this stop/go:

| audit outcome | action |
|---|---|
| NWS + sense-dupes pass, residual dominated by F-gate-nws-fp | accept `gam` with documented residuals, then consider `yuj` |
| real mechanical failures in `requeue.keys.txt` | generate targeted requeue with `python src\pilot\requeue_from_audit.py gam` |
| stale artifact refusal | discard/replace `wf_output.json`; rerun Max from current harness |
| crashed gate | inspect gate stderr in `audit_window.report.json`; do not advance |

The known non-blocking follow-ups are still:

- fix F-gate-nws-fp by teaching `has_text_signal()` to count NWS owner citations;
- optionally escalate the small set of real `untranslated_braced_german_gloss`
  cards to Opus.

## What To Bring Back

Return these values/artifacts:

| item | source |
|---|---|
| Max wall-clock minutes | Max run output/operator note |
| Max cache-read tokens | Max run output |
| Max cache-create tokens | Max run output |
| Max output tokens | Max run output |
| Max total tokens | Max run output |
| cap fired? | Max run output/operator note |
| audit summary | `src/pilot/output/audit_window.report.md` |
| requeue count | `src/pilot/output/requeue.keys.txt` |
| judge sample count | `src/pilot/output/judge_sample.keys.txt` |
| next action | `src/pilot/output/window_status.md` |

Canonical runbook:

```text
src/pilot/RUN_FREQ_MAX.md
```
