# Handoff — Claude Code Max staged PWG run

Date: 2026-06-29

Audience: Claude Code Max / Max Workflow operator.

Goal: produce enough fresh audited data to decide whether the PWG->Russian bulk
run is moving quickly and safely. Do not try to translate 10 big dhātus at once.
Run the staged evidence plan below.

## Current Verdict

| readiness question | answer |
|---|---|
| Continue bulk translation? | **Yes, after fresh `sTA`.** |
| Reviewed DCS-frequency core tranche? | **Not yet.** Needs fresh audited windows plus G5/G6/G7 evidence. |
| Immutable DH edition? | **Not yet.** G5/G6/G7/G10 block it. |
| Printed bilingual dictionary? | **Not yet.** Print examples/spec exist, but reviewed rows and renderer/front matter are missing. |

The next useful review is fresh `sTA` audit plus print-renderer feasibility from
real examples, not another broad readiness document.

## Non-Negotiable Rules

- Do not run 10 big dhātus in one Max push yet.
- Do not advance to `BU` until fresh `sTA` is audited.
- Do not use stale `wf_output.json` as evidence.
- Do not combine several roots into one `wf_output.json`; audit economics and
  requeue keys must stay root-scoped.
- Do not manually judge whole windows. Use `prompt_semantic` risks first and
  `judge_sample.keys.txt` second.
- Do not claim print readiness from these Max runs. G5/G6/G7/G10 still decide
  publication readiness.

## Root Status Snapshot

Verified locally on 2026-06-29:

| root | status | sub-cards | action |
|---|---:|---:|---|
| `sTA` | structurally ready, but stale-output blocked | 123 | Run current optimized harness in Max and audit fresh output. |
| `BU` | clean-ready after harness generation | 59 | Run only after `sTA` clears. |
| `as` | clean-ready after harness generation | 98 | Stage B after `BU`. |
| `i` | clean-ready after harness generation | 204 | Stage B after `as`. |
| `gam` | stale generated raw/portrait inputs | 127 | Prune/recheck before harness generation. |
| `yuj` | stale generated raw/portrait inputs | 60 | Prune/recheck before harness generation. |
| `vid` | stale generated raw/portrait inputs | 55 | Prune/recheck before harness generation. |
| `han` | stale generated raw/portrait inputs | 78 | Prune/recheck before harness generation. |

Stage A + Stage B (`sTA` + `BU` + `as` + `i`) gives about 484 sub-cards, enough
for a serious first estimate of throughput, quota pressure, requeue churn, and
semantic-risk rate.

## Stage A — Fresh sTA Only

From the `RussianTranslation` repo root:

```powershell
python src\pilot\root_window_status.py sTA
```

Expected status:

- `current state: stale_artifact`;
- 123/123 raw files present;
- 123/123 portrait files present;
- next action says to run generated optimized harness.

Then in Claude Code Max / Max Workflow:

1. Run the current generated harness:

   ```text
   src/pilot/run_pilot_wf.opt.js
   ```

2. Save the Workflow JSON result as:

   ```text
   wf_output.json
   ```

3. If Max reports token/time numbers, keep them. They are important.

Back in the repo shell, audit:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue
```

If token/time numbers are available, prefer:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue `
  --wall-clock-minutes <n> `
  --max-cache-read-tokens <n> `
  --max-total-tokens <n>
```

If `requeue.keys.txt` is non-empty:

```powershell
python src\pilot\requeue_from_audit.py sTA
```

Run the regenerated optimized harness in Max for only those keys, save the next
`wf_output.json`, and audit again.

## Stage B — Clean-Ready Follow-Up Roots

Start Stage B only after fresh `sTA` is mechanically clean or has a targeted
rerun plan.

Run one root at a time:

```powershell
python src\pilot\gen_opt_harness.py BU
# Run src/pilot/run_pilot_wf.opt.js in Max.
# Save wf_output.json.
python src\pilot\audit_window.py wf_output.json --root BU --write-requeue

python src\pilot\gen_opt_harness.py as
# Run Max, save wf_output.json.
python src\pilot\audit_window.py wf_output.json --root as --write-requeue

python src\pilot\gen_opt_harness.py i
# Run Max, save wf_output.json.
python src\pilot\audit_window.py wf_output.json --root i --write-requeue
```

Record the same token/time fields for every root.

## Stage C — Hold Until Pruned/Rechecked

Do not run these roots yet:

```text
gam, yuj, vid, han
```

Before any Max spend on them, prune stale generated inputs and recheck:

```powershell
python src\pilot\root_window_status.py gam --prune-stale
python src\pilot\root_window_status.py yuj --prune-stale
python src\pilot\root_window_status.py vid --prune-stale
python src\pilot\root_window_status.py han --prune-stale
```

Then run `python src\pilot\root_window_status.py <root>` again. Generate a
harness only when the root reports clean structural readiness.

## What To Bring Back

For each root, return these artifacts or values:

| item | source |
|---|---|
| Max wall-clock minutes | Max run output / operator note |
| Max cache-read tokens | Max run output |
| Max total tokens | Max run output |
| audit result | `src/pilot/output/audit_window.report.md` |
| requeue count | `src/pilot/output/requeue.keys.txt` |
| judge sample count | `src/pilot/output/judge_sample.keys.txt` |
| high-confidence semantic risks | `prompt_semantic` section in audit report |
| next action | `src/pilot/output/window_status.md` |

If a weekly Max cap fires, record the cumulative token number at the moment it
fires.

## Print Feasibility Side Check

Do not use stale `wf_output.json` as print evidence. For print layout, use:

- `PRINT_ENTRY_SPEC.md`;
- `PRINT_ENTRY_EXAMPLES.md`;
- examples: `agni`, `akzara`, `ap`.

The known renderer decisions are:

- citation compaction;
- nested sense labels;
- homonym blocks;
- compact one-owner NWS badges;
- Nachträge display;
- `{%...%}`, `<ls>`, `<ab>`, and sigla policy;
- abbreviation/sigla front matter.

These examples are layout/QA prototypes, not publication text.

## Fast Command Summary

```powershell
# Stage A
python src\pilot\root_window_status.py sTA
# Run src/pilot/run_pilot_wf.opt.js in Max, save wf_output.json.
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue

# If needed
python src\pilot\requeue_from_audit.py sTA

# Stage B, after sTA clears
python src\pilot\gen_opt_harness.py BU
python src\pilot\gen_opt_harness.py as
python src\pilot\gen_opt_harness.py i

# Stage C, not before pruning/rechecking
python src\pilot\root_window_status.py gam --prune-stale
python src\pilot\root_window_status.py yuj --prune-stale
python src\pilot\root_window_status.py vid --prune-stale
python src\pilot\root_window_status.py han --prune-stale
```

Primary handoff file for operator decisions:

```text
NEXT_REVIEW_PACKET.md
```

Canonical runbook:

```text
src/pilot/RUN_FREQ_MAX.md
```
