# Legacy Max Artifacts

Archived on 2026-06-28 during production-window cleanup.

These files document the pre-optimized a-section/Workflow path. They are kept
for audit history only. Current production windows use:

```powershell
python src\pilot\root_window_status.py <root>
python src\pilot\gen_opt_harness.py <root>
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

The active runbook is `src/pilot/RUN_FREQ_MAX.md`.
