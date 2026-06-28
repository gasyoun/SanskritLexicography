# RussianTranslation Use Cases

Operational scenarios for the PWG -> Russian production pipeline. The canonical
runbook remains [src/pilot/RUN_FREQ_MAX.md](src/pilot/RUN_FREQ_MAX.md); this
page is a quick map from intent to command path.

## 1. Preflight the Next Root

Use when deciding whether a frequency-window root is ready for Max spend.

```powershell
python src\pilot\root_window_status.py <root>
```

Expected outcome: one `next action` and one `next command`. Trust this output
over older handoff prose. A matching optimized harness must have the same root,
rootmap hash, and selected key scope.

## 2. Run a Fresh Max Window

Use when a root is structurally ready and no fresh workflow output exists.

```powershell
python src\pilot\gen_opt_harness.py <root>
# run src\pilot\run_pilot_wf.opt.js in Claude/Max Workflow
# save the JSON as wf_output.json
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

Mechanical acceptance requires the deterministic audit to pass. The audit checks
workflow provenance, NWS owner attribution, markup fidelity, sense coverage, and
cross-part duplicate senses before writing queue/status files.

## 3. Recover from Stale Output

Use when `wf_output.json` belongs to an older rootmap or harness.

```powershell
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

Expected outcome: state `stale_artifact`. The audit refuses collect/gates/glue
and preserves the existing `requeue.keys.txt`. Regenerate the harness and rerun
Max; use `--allow-stale` only for forensic inspection.

## 4. Rerun Only Mechanical Failures

Use when `src/pilot/output/requeue.keys.txt` is non-empty.

```powershell
python src\pilot\requeue_from_audit.py <root>
# run the regenerated optimized harness in Max Workflow
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

The rerun harness is built only from current rootmap keys. Stale or invalid
requeue keys are rejected before Max spend.

## 5. Send a Semantic Judge Sample

Use after all mechanical gates pass and `judge_sample.keys.txt` is non-empty.

```powershell
Get-Content src\pilot\output\judge_sample.keys.txt
```

This queue contains all Python-gate failures plus a deterministic clean-card
sample. It is for semantic mistranslation review only; it is not the mechanical
requeue list.

## 6. Monitor Local Operations

Use while running or auditing windows.

```powershell
python src\pilot\dashboard_server.py --port 8765
```

Open `http://127.0.0.1:8765/`. The dashboard reads local status, audit reports,
ledger rows, dashboard events, queue files, freshness data, and print-gate
snapshots. It does not create human review decisions.

## 7. Check Release and Print Readiness

Use when validating downstream artifacts without cutting an edition.

```powershell
python src\preflight_remaining_gates.py
python src\release_readiness.py --release-dir release
python src\validate_interop.py --dir release
```

The print-readiness scripts are report-only by default. Add `--fail-on-blocked`
when using them as a CI/go-no-go gate. Current G5/G6/G7/G10 blockers require
human review/gold work.

## 8. Resume Corpus Lexicon API Work

Use when DeepSeek/OpenRouter calls fail during corpus-lexicon construction.

```powershell
python src\build_corpus_lexicon.py build <textfile> [N] [workers] --retry-failed
```

Tune `DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`,
`DEEPSEEK_READ_TIMEOUT`, and `DEEPSEEK_BACKOFF_BASE` for unstable network
conditions. Failed batches are logged locally and retried append-only.
