# RussianTranslation

Russian-edition working area for Sanskrit lexicography projects, with the live
PWG → Russian production pipeline as the active track.

## Current PWG Path

The current production route is the frequency-window Max workflow documented in
[`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md):

```powershell
python src\pilot\root_window_status.py <root>
python src\pilot\gen_opt_harness.py <root>
# run src\pilot\run_pilot_wf.opt.js in Claude/Max Workflow and save wf_output.json
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

The generated optimized harness inlines inputs, disables tools for translation
agents, carries provenance metadata, and is audited by deterministic Python gates
before any mechanical acceptance.

For task-oriented operator flows, see [USE_CASES.md](USE_CASES.md). It covers
preflight, fresh Max windows, stale-output recovery, targeted requeue, sampled
semantic judging, dashboard monitoring, release readiness checks, and corpus API
retry work.

## Guardrails

- `root_window_status.py` is the pre-spend truth source for each root. It checks
  rootmap/input structure and verifies that the optimized harness matches the
  intended selected-key scope.
- `audit_window.py` refuses stale workflow artifacts before collect/gates/glue,
  preserves existing requeue files on stale refusal, and writes status/ledger
  artifacts for the dashboard.
- `nws_split.py` audits NWS owner attribution with root-split sub-card filename
  handling; missing raw/card files requeue, while cards with no NWS layer remain
  neutral.

## Flaky Network Policy

Claude production translation is not a Python Claude API loop. It runs through
the Claude/Max Workflow surface, and interruptions are handled by deterministic
state files:

- null or failed cards are written into `src/pilot/output/requeue.keys.txt`;
- `requeue_from_audit.py` builds a rerun harness for only those cards;
- stale `wf_output.json` artifacts are refused before they can mutate outputs.

DeepSeek/OpenRouter corpus-lexicon builds are append-only and resumable. Tune
`DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`, `DEEPSEEK_READ_TIMEOUT`, and
`DEEPSEEK_BACKOFF_BASE` when the connection is poor. Failed API batches are
logged locally to `src/corpus_lexicon.failures.jsonl` and can be retried later:

```powershell
python src\build_corpus_lexicon.py build <textfile> [N] [workers] --retry-failed
```

## Runtime Artifacts

Generated workflow, dashboard, status, ledger, requeue, and corpus retry files
are ignored by git. Superseded Max/a-section artifacts live in
[`src/pilot/archive/legacy_max_2026-06-27/`](src/pilot/archive/legacy_max_2026-06-27/)
for audit history only.
