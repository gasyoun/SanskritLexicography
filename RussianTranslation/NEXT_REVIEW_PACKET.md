# Next Review Packet: Fresh sTA + Print Feasibility

Date: 2026-06-29

This is the narrow executable packet for the next review. It exists to avoid
another broad readiness pass.

Claude Code Max handoff:
[HANDOFF_2026-06-29_claude_code_max.md](HANDOFF_2026-06-29_claude_code_max.md).

## Verdict Target

| question | current answer | this packet can change? |
|---|---|---|
| Ready to continue bulk translation? | **Yes, after fresh `sTA`.** | Yes: fresh audit can clear `sTA` for `BU`. |
| Ready for reviewed core tranche? | **Not yet.** | Partly: begins evidence, but G5/G6/G7 still decide. |
| Ready for immutable DH edition? | **Not yet.** | No: waits for G5/G6/G7/G10. |
| Ready for printed bilingual dictionary? | **Not yet.** | No: this only locks renderer feasibility questions. |

Stop discussing the full 144k tail here. The first publishable target remains a
reviewed DCS-frequency core tranche.

## Required Inputs

| input | status | source |
|---|---|---|
| `sTA` root window | structurally ready | `python src\pilot\root_window_status.py sTA` |
| fresh Max output | **missing** | must be saved as `wf_output.json` after running `src/pilot/run_pilot_wf.opt.js` |
| audit command | ready | `python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue` |
| clean follow-up roots | ready after harness generation | `BU` 59 sub-cards, `as` 98, `i` 204 |
| stale follow-up roots | hold until prune/recheck | `gam`, `yuj`, `vid`, `han` have stale generated raw/portrait inputs |
| print examples | ready as prototypes | `PRINT_ENTRY_EXAMPLES.md` using `agni`, `akzara`, `ap` |
| publication evidence | missing | G5/G6/G7/G10 remain blocked |

## Stage Policy: No 10-Root Blast Yet

Do not ask Max to translate 10 big dhātus in one broad run. The current evidence
supports a staged run:

1. Stage A: fresh `sTA` only.
2. Stage B: after `sTA` is clean, run structurally clean roots `BU`, `as`, and
   `i` one root at a time.
3. Stage C: expand to `gam`, `yuj`, `vid`, and `han` only after pruning stale
   generated inputs and rechecking status.

This gives about 484 sub-cards across `sTA` + `BU` + `as` + `i`, enough for a
serious first estimate of throughput, quota, requeue churn, and semantic-risk
rate without mixing clean roots with avoidable stale-input failures.

## Step 1: Fresh sTA Audit

Run from the repository root:

```powershell
python src\pilot\root_window_status.py sTA
```

Expected before Max:

- state is `stale_artifact`;
- 123/123 raw files present;
- 123/123 portrait files present;
- next action says to run generated optimized harness.

Then run `src/pilot/run_pilot_wf.opt.js` in Max Workflow and save the result as
`wf_output.json`.

Audit:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue
```

## Step 2: Mechanical Stop/Go

| audit result | action |
|---|---|
| stale artifact | reject output; rerun current optimized harness |
| `requeue.keys.txt` non-empty | run `python src\pilot\requeue_from_audit.py sTA`, rerun Max only for named keys, then audit again |
| prompt/manual drift failure | fix harness/prompt wiring before more Max spend |
| NWS/markup/coverage/sense-dupe failures | requeue only named keys |
| mechanical gates clean | proceed to Step 3 |

Do not use semantic judgment to override mechanical audit failures.

## Step 3: Minimum Semantic Review

Review only these, in order:

1. high-confidence mechanical semantic risks in `audit_window.report.md`
   / `prompt_semantic`;
2. `judge_sample.keys.txt`;
3. no other clean cards unless a sampled failure shows a repeated class.

If the sample finds a repeated semantic class, add that class to the next
deterministic audit proposal. Do not manually browse the whole window.

## Step 4: Advance or Hold

| condition | next command |
|---|---|
| fresh `sTA` clean and semantic sample acceptable | `python src\pilot\root_window_status.py BU` |
| `BU` structurally ready | `python src\pilot\gen_opt_harness.py BU` |
| fresh `sTA` still has requeue keys | continue targeted requeue, not `BU` |
| Max output cannot be made fresh | hold production; do not claim scale progress |

After `BU` is audited clean, continue the clean-ready Stage B roots:

```powershell
python src\pilot\gen_opt_harness.py as
# Run Max, save wf_output.json, audit with --root as.

python src\pilot\gen_opt_harness.py i
# Run Max, save wf_output.json, audit with --root i.
```

Before any Stage C root, prune and recheck stale generated inputs:

```powershell
python src\pilot\root_window_status.py gam --prune-stale
python src\pilot\root_window_status.py yuj --prune-stale
python src\pilot\root_window_status.py vid --prune-stale
python src\pilot\root_window_status.py han --prune-stale
```

Generate harnesses for those roots only after `root_window_status.py <root>`
reports clean structural readiness.

## Step 4b: Data To Record Per Root

Record these on or immediately after every audit:

| metric | why |
|---|---|
| wall-clock minutes | estimates calendar throughput |
| Max cache-read tokens | estimates Max quota pressure |
| Max total tokens | estimates run-to-cap behavior |
| sub-card count | normalizes cost and failure rate |
| `requeue.keys.txt` count | measures mechanical rework |
| `judge_sample.keys.txt` count | measures semantic review spend |
| high-confidence `prompt_semantic` risks | identifies deterministic audit candidates |
| advance/requeue/hold state | prevents ambiguous next steps |

When Max token numbers are available, pass them into the audit command:

```powershell
python src\pilot\audit_window.py wf_output.json --root BU --write-requeue `
  --wall-clock-minutes <n> `
  --max-cache-read-tokens <n> `
  --max-total-tokens <n>
```

## Step 5: Print Renderer Feasibility Review

Use `PRINT_ENTRY_EXAMPLES.md`, not stale `wf_output.json`, for print layout
questions.

| example | required renderer capability | decision owner |
|---|---|---|
| `agni` | citation compaction, Nachträge display, NWS owner rows, optional differentia apparatus | renderer + human_editor |
| `akzara` | nested labels, gender headers, complex sense grouping | renderer |
| `ap` | homonym blocks, `{%...%}` policy, `<ab>` display, compact NWS badges | renderer + human_editor |

Renderer feasibility is acceptable when every row above has a chosen policy in
`PRINT_ENTRY_SPEC.md` or an explicit open item in the roadmap. These examples
are not publication text until G5/G6/G7/G10 pass.

## Step 6: Human Gate Packet

Do not start open-ended human review. Use only:

| gate | file | validation |
|---|---|---|
| G5 | `src/_review_queue.csv` | `python src\run_batch.py validate_review` |
| G6 | `gold/_human_gold_review.csv` | `python src\gold_status.py gold\_human_gold_review.csv` and `python src\gold_validate.py gold\_human_gold_review.csv` |
| G7 | `gold/_double_review_queue.csv` | `python src\gold_double_review_verify.py gold\_double_review_queue.csv --sample-size 80`, ingest, then `python src\gold_agreement.py` |

## Completion Checklist

- [ ] Fresh `sTA` `wf_output.json` exists and is accepted by `audit_window.py`.
- [ ] `requeue.keys.txt` is empty or every key has a targeted rerun plan.
- [ ] `judge_sample.keys.txt` is reviewed only after mechanical gates are clean.
- [ ] `BU`, `as`, and `i` are run only after fresh `sTA` clears.
- [ ] `gam`, `yuj`, `vid`, and `han` are pruned/rechecked before any Max run.
- [ ] Print renderer feasibility is reviewed from `agni`, `akzara`, and `ap`.
- [ ] G5/G6/G7 remain the only path toward print-ready publication claims.

Current packet status: executable, but not complete. The missing external input
is fresh Max `sTA` output. A 10-root Max run is explicitly out of scope until
Stage B produces enough audit data.
