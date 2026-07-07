# PWG-RU launch failure ledger

_Created: 07-07-2026 · Owner: every session that launches Workflow/API work_

This is the canonical per-launch failure ledger for `RussianTranslation`.
[`PIPELINE_HISTORY.md`](PIPELINE_HISTORY.md) is the curated narrative map; this
file is the operational incident register. Every Workflow/API launch that hits a
failure, drift, retry, kill, stale artifact, cost blow-up, or suspicious
residual gets one entry here before the handoff is closed.

## Closeout rule

A launch handoff is not done until each failure is classified as one of the
categories below and has a disposition: fixed, structurally guarded,
accepted-as-proven-residual, or routed to a new bug-hunt handoff. Do not leave a
second occurrence of the same `unknown` shape in this ledger; the second
occurrence requires a bug-hunt handoff.

Run the check before closing launch work:

```powershell
python src\pilot\check_launch_ledger.py --handoff H220
python src\pilot\check_launch_ledger.py --since 2026-07-05
```

## Failure typology

- `concurrency/api`: rate limits, connection loss, mid-stream stalls, provider
  throttling, transient API nulls.
- `structured-output-limit`: model cannot emit the required schema because the
  whole-card/whole-batch output is too large or complex.
- `complexity-estimate-drift`: preflight or cost estimate misses real agent,
  token, or fragment fan-out.
- `kill-gate-calibration`: timeout budget is too loose, too strict, or lacks a
  fallback lane for this launch shape.
- `gate-bug`: deterministic audit or semantic-risk gate misclassifies a valid
  or invalid card.
- `artifact/provenance`: stale output, rootmap/input hash mismatch, ordering
  bug, missing SHA/provenance, or manual-save loss.
- `tm/cache`: translation memory or cache serves content that should have been
  regenerated or rejected.
- `filesystem/watcher`: untracked/gitignored output is deleted or overwritten
  by local repo automation.
- `key/schema-mismatch`: valid model output is dropped because keys, safe names,
  wrappers, or schema paths disagree.
- `operator/process`: concurrency discipline, claim/registry drift, manual
  capture, or handoff procedure fails.
- `external-api`: non-Workflow service quirks such as JSON-mode requirements,
  escaped-character parsing, or retriable DeepSeek failures.
- `unknown`: not yet explained. A repeated `unknown` shape must be escalated to
  a bug-hunt handoff.

## Machine ledger

Keep this fenced block valid JSON. The checker enforces required fields, valid
classes, expected-vs-actual metrics, residual status, and unknown recurrence.

```json launch_failure_ledger
[
  {
    "id": "SLICE_D_2026-06-30",
    "handoff": "H151",
    "date": "2026-06-30",
    "title": "Slice D 18-wide bulk run collapsed into transient nulls",
    "lane": "verb batch",
    "model": "claude-sonnet-5",
    "orchestrator": "Workflow",
    "expected": {
      "agents": "one root at a time; no 18-root fan-out",
      "tokens": "not recorded"
    },
    "actual": {
      "agents": "~140-250 peak concurrent agents",
      "tokens": "not recorded"
    },
    "passes": 1,
    "symptoms": "80+ server-side 429s and 117 transient null cards after 18 roots were launched in parallel.",
    "classification": "concurrency/api",
    "root_cause": "Provider/server concurrency cliff; the same period's single-root run had zero transient failures.",
    "guardrail": "Standing production discipline: roots run one at a time, <=3-wide maximum, and no bulk parallel Workflow fan-out.",
    "residual_status": "structurally-guarded",
    "residual_risk": "Only process drift can reintroduce this; check launch width before every run."
  },
  {
    "id": "PRIL10_W1_2026-07-05",
    "handoff": "H189",
    "date": "2026-07-05",
    "title": "pril10_w1 nominal monster window cost and latency blow-up",
    "lane": "nominal monster",
    "model": "claude-sonnet-5",
    "orchestrator": "Opus 4.8 Max/Workflow surface",
    "expected": {
      "agents": "174 fragment groups estimated before the fix",
      "tokens": "nominal bulk economics expected to be viable"
    },
    "actual": {
      "agents": "230 agents over 581 turns before abort",
      "tokens": "42,316,604 total tokens; about $79.83"
    },
    "passes": 1,
    "symptoms": "After about 20 minutes only about 3 of 8 monster cards were done; agents burned 3-6.5 minutes and up to about 900K tokens each.",
    "classification": "complexity-estimate-drift",
    "root_cause": "Nominal presplit mode made each fragment an agent call, defeating opt2 batching and re-paying framework cache overhead per fragment.",
    "guardrail": "H189/H191 added presplit-lane re-batching, tighter kill budgets, a live agent kill-switch, harness-size split warnings, and perf_preflight cost partition/defer-monster gating.",
    "residual_status": "structurally-guarded",
    "residual_risk": "kAla-class monster windows remain human-budgeted/defer lane work, not ordinary bulk launches."
  },
  {
    "id": "NOMINAL_W1_100SMALL_2026-07-06",
    "handoff": "H201",
    "date": "2026-07-06",
    "title": "nominal_w1_100small pass-1 transient outage",
    "lane": "nominal small",
    "model": "claude-sonnet-5",
    "orchestrator": "Opus 4.8 Max/Workflow surface",
    "expected": {
      "agents": "3 expected agents for one clean pass",
      "tokens": "~745,200 tokens; about $1.41"
    },
    "actual": {
      "agents": "37 agents across three passes",
      "tokens": "2,498,796 subagent tokens"
    },
    "passes": 3,
    "symptoms": "Pass 1 returned 5 ok / 95 null with budget_kill_switch_tripped after all batches, including a 4-card batch, hit Connection closed mid-response.",
    "classification": "concurrency/api",
    "root_cause": "Transient infrastructure/network outage during the run window, not content complexity or batch sizing.",
    "guardrail": "Treat same transport error across all batches as transient infra; rerun cleanly and requeue only real residual nulls.",
    "residual_status": "accepted-as-proven-residual",
    "residual_risk": "A transient pass can still double spend; expected-vs-actual ledger must record clean-pass estimate and actual passes separately."
  },
  {
    "id": "DAH_TAIL_2026-07-06",
    "handoff": "H178",
    "date": "2026-07-06",
    "title": "dah tail topup left one documented PW-addenda residual",
    "lane": "verb batch",
    "model": "claude-sonnet-5",
    "orchestrator": "Fable 5 Workflow surface",
    "expected": {
      "agents": "1 defect requeue agent plus 17 topup fragment agents per attempt",
      "tokens": "not pre-estimated in the log"
    },
    "actual": {
      "agents": "35 agents across defect requeue and two topup attempts",
      "tokens": "2,368,224 subagent tokens"
    },
    "passes": 3,
    "symptoms": "dah~~h0_zz_pw__s10p0 hard-failed the StructuredOutput retry cap on both fresh topup attempts; the union recovered 16/17 fragments.",
    "classification": "structured-output-limit",
    "root_cause": "A single PW-addenda sense fragment still exceeded the schema-emission envelope even after bounded topup retries.",
    "guardrail": "H178 accepted the card only after the two-attempt cap and documented the exact residual; TM was rebuilt and provenance audited clean.",
    "residual_status": "accepted-as-proven-residual",
    "residual_risk": "This is a known StructuredOutput retry-cap residual, not the H220 kill-gate class; future similar fragments should be routed through the same bounded topup/acceptance rule."
  },
  {
    "id": "NO_PWG_W1_FIRST_RUN_2026-07-06",
    "handoff": "H214",
    "date": "2026-07-06",
    "title": "no_pwg_w1 first run validated plumbing but exposed throughput blockers",
    "lane": "no-PWG single",
    "model": "claude-sonnet-5",
    "orchestrator": "Opus 4.8 Workflow surface",
    "expected": {
      "agents": "preflight about 497K tokens / $0.94 for the first 58-card lane run",
      "tokens": "~497K tokens preflight estimate"
    },
    "actual": {
      "agents": "three Workflow passes, including batched, 9-batch, and 46 single-card rounds",
      "tokens": "~3.4M subagent tokens"
    },
    "passes": 3,
    "symptoms": "Only 21/58 distinct sub-cards were ok; budget kill-switches tripped, audit needed nominal no-rootmap handling, and the path was validated but not promotable at first.",
    "classification": "kill-gate-calibration",
    "root_cause": "The no-PWG lane combined no-fallback singleton latency, strict key echo behavior, and nominal audit assumptions that were inherited from rootmap-backed lanes.",
    "guardrail": "H214 fixed the Lbody pointer leak and nominal audit crash; H220 then fixed the no-fallback kill budget and nominal key echo mismatch, raising the diagnostic window to 10/10.",
    "residual_status": "fixed",
    "residual_risk": "Scale no-PWG through small single-card windows and keep H220 lane-specific calibration; do not use stale nominal audit defect counts as requeue truth."
  },
  {
    "id": "NO_PWG_DIAG_2026-07-06",
    "handoff": "H220",
    "date": "2026-07-06",
    "title": "no-PWG single-card throughput false kills and key echo drops",
    "lane": "no-PWG single",
    "model": "claude-sonnet-5",
    "orchestrator": "Opus 4.8 Max/Workflow surface",
    "expected": {
      "agents": "diagnostic 10-card window should converge without structural nulls",
      "tokens": "not recorded"
    },
    "actual": {
      "agents": "9 agents on verified rerun",
      "tokens": "not recorded"
    },
    "passes": 2,
    "symptoms": "Before the fix, the diagnostic window yielded about 40%; 6 of 6 nulls were kill-timeouts, and some valid outputs were dropped by strict key matching.",
    "classification": "kill-gate-calibration",
    "root_cause": "The kill gate was calibrated on dense verb batches; no-fallback single supplement cards have fixed StructuredOutput latency and no selfheal lane. Separately, clean SLP1 portrait keys pulled the model away from mangled safe-name headers.",
    "guardrail": "No-fallback singles now receive the 180s CEIL budget, nominal windows use a gated nominal_keymap re-key, and selfHeal preserves upstream failure reasons.",
    "residual_status": "fixed",
    "residual_risk": "Recalibrate per lane; never apply the dense-root kill profile blindly to no-fallback singleton launches."
  },
  {
    "id": "ARMB_SYNTH_FANOUT_2026-07-06",
    "handoff": "H234",
    "date": "2026-07-06",
    "title": "Arm-B 10-agent synthesis fan-out orchestration failure",
    "lane": "synth fan-out",
    "model": "claude-opus-4-8",
    "orchestrator": "Opus 4.8 async sub-agents",
    "expected": {
      "agents": "10 synthesis agents",
      "tokens": "not recorded"
    },
    "actual": {
      "agents": "10 initial agents plus replacements/resumes",
      "tokens": "not recorded"
    },
    "passes": 2,
    "symptoms": "False-stall kill from 0-byte transcripts, mid-stream API stalls at 10-wide, a 34-minute silent hang, watcher-wiped outputs, zombie overwrite, and free-form collapse on >800 citation entries.",
    "classification": "operator/process",
    "root_cause": "Bare async fan-out used unsafe liveness signals, shared output paths, repo-local untracked outputs, and too-wide concurrency for large Opus generations.",
    "guardrail": "src/synth_dispatch.py now caps concurrency, watches output-file growth only, confirms dead-before-redispatch, uses private staging and watcher-safe landing, seals outputs, and routes >800 <ls> entries to deterministic assembly.",
    "residual_status": "structurally-guarded",
    "residual_risk": "All future pwg_ru multi-agent fan-outs must go through synth_dispatch.py; bare fan-outs are banned."
  }
]
```

_Dr. Mārcis Gasūns_
