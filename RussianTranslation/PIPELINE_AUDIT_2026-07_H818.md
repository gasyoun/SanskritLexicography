# PWG→RU full-pipeline audit — H818

_Created: 12-07-2026 · Last updated: 12-07-2026_

Model: Codex / GPT-5. Audit host: Windows development checkout, not the required foreign Linux server.

## Verdict

**NO-GO for a real translation run on this host.** The ≥5 KB probe reached Claude Code CLI 2.1.207 but returned `401 Invalid authentication credentials`, with zero tokens. The four authenticated Max profiles and target foreign server were not supplied. No translation or store mutation was attempted after this gate failed.

Prior-art verdict: **PARTIAL**. Queue selection, Workflow generation, audit, serialized promotion, model provenance, and canonical-store resolution already exist. The gap is an outer account scheduler plus an execution adapter between Workflow JavaScript and a headless process.

## Reproduction

```powershell
$prompt = python RussianTranslation/src/pilot/probe_log.py prompt
claude -p $prompt --output-format json --permission-mode plan
```

Observed: `api_error_status: 401`, `Failed to authenticate`, `total_cost_usd: 0`; payload 6,491 bytes. H818's older `prompt --payload-bytes 5000` syntax has drifted: current `prompt` takes no option and enforces the floor itself.

## Real call graph

| Stage | Code source of truth | Reads → writes | Status |
|---|---|---|---|
| Select | `src/pilot/coordinator.py:claim` | worklist/store → lease | Works; verb supply remains rootmap-limited |
| Prepare | `coordinator.py:prepare` → `perf_preflight.py` → `gen_opt_harness2.py` | lease → preflight + Workflow JS | Works; artifact is Workflow-only |
| Generate | human coding session executes Workflow JS | harness → Workflow wrapper | **Not headless**; coordinator's module contract requires an operator |
| Record/audit | `coordinator.py:record_output` → `audit_window.py` | wrapper → normalized output/report/requeue | Implemented |
| Promote | `coordinator.py:promote_ready` → `promote_final_cards.py` | ready outputs → canonical store + TM | Implemented; promotion lock serializes it |
| Persist | `src/store_path.py:canonical_store` | worktree path → canonical checkout store | Implemented |
| Outer dispatch | `src/pilot/max_account_orchestrator.py` | SQLite + profiles → per-job output | Implemented/self-tested; real profiles unavailable |

## Architectural decision

The scheduler **wraps, rather than replaces, `coordinator.py`**. SQLite owns cross-account dispatch only; coordinator leases own targets and the single promotion lock. This prevents four workers from racing on store/TM writes.

H818 treats `claude -p` as interchangeable with the in-chat Workflow tool, but the generated JS calls the Workflow runtime and is not standalone Node/Claude CLI code. Production must either expose that runner noninteractively or port the translate call to a `claude -p` contract while preserving schema, masking, audit, `gen_model`, and promotion. This audit does not assume the port is equivalent.

## Silent-failure census

| Site | Class | Impact | Evidence |
|---|---|---|---|
| Probe command | doc/CLI drift | probe never starts | Observed rejected option |
| Audit-host profile | authentication | zero generation | Observed 401 |
| Workflow vs `claude -p` | execution-model mismatch | fan-out produces no translations | Verified in coordinator contract/generated calls |
| Reset time | unstable provider message | early/late rejoin | Scheduler parses epoch, otherwise parks five hours |
| Crash mid-job | partial state | lost/duplicate job | SQLite `in_progress`; `recover`; atomic output replace |
| Concurrent promotion | shared-store race | corrupt/lost store | Existing promotion lock remains sole promoter |

## Queue and defaults

Use RU-only `no_pwg` first: it is partially drained and avoids the verb lane's broad rootmap gate. Medium50 has recent API/kill-budget incidents. Start with one small card and choose chunk size from measured latency and clean rate; do not split capacity into EN before RU is stable.

## Deliverables and gates

- SQLite scheduler, parking, atomic output, recovery: implemented.
- systemd deployment and runbook: implemented.
- scheduler self-test: passed.
- Real promoted translation: **blocked** by authentication and execution adapter.
- Four-account batch: **blocked** by profiles/foreign host and the adapter.

Not audited: real server networking, quota/reset payloads, live Workflow transcript, or real store delta. These require H818's owner-supplied external inputs.

_Dr. Mārcis Gasūns_
