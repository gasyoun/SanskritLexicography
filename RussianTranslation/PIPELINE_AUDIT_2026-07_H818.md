# PWG→RU full-pipeline audit — H818

<!-- markdownlint-disable MD013 MD036 MD060 -->

_Created: 12-07-2026 · Last updated: 12-07-2026_

Model: Codex / GPT-5. Audit host: Windows development checkout, not the required foreign Linux server.

## Verdict

**NO-GO for a real translation run on this host.** The ≥5 KB probe reached Claude Code CLI 2.1.207 but returned `401 Invalid authentication credentials`, with zero tokens. The four authenticated Max profiles and target foreign server were not supplied. No translation or store mutation was attempted after this gate failed.

Prior-art verdict: **PARTIAL**. Queue selection, Workflow generation, audit, serialized promotion, model provenance, and canonical-store resolution already exist. H818 now adds a canonical manifest, headless execution adapter, and outer account scheduler; live acceptance remains external-host gated.

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
| Prepare | `coordinator.py:prepare` → `perf_preflight.py` → `gen_opt_harness2.py` | lease → preflight + Workflow JS + execution manifest | Implemented |
| Generate | `headless_worker.py` → `claude -p --json-schema` | manifest → Workflow-compatible result | Implemented; live profile proof pending |
| Record/audit | `coordinator.py:record_output` → `audit_window.py` | wrapper → normalized output/report/requeue | Implemented |
| Promote | `coordinator.py:promote_ready` → `promote_final_cards.py` | ready outputs → canonical store + TM | Implemented; promotion lock serializes it |
| Persist | `src/store_path.py:canonical_store` | worktree path → canonical checkout store | Implemented |
| Outer dispatch | `src/pilot/max_account_orchestrator.py` | SQLite + profiles → per-job output | Implemented/self-tested; real profiles unavailable |

## Architectural decision

The scheduler **wraps, rather than replaces, `coordinator.py`**. SQLite owns cross-account dispatch only; coordinator leases own targets and the single promotion lock. This prevents four workers from racing on store/TM writes.

The generator now emits one versioned manifest beside the legacy Workflow JS. The headless worker consumes the same prompts, masked inputs, placeholder maps, output schema, key metadata, and exact model, then returns the existing `{meta, summary, results}` contract. It refuses presplit manifests in v1: those still require the Workflow heal/bisection runtime, and silently treating them as ordinary whole-card calls would be false parity.

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
- Real promoted translation: **blocked** by authenticated profiles/foreign host.
- Four-account batch: **blocked** by the same external host gate.

Not audited: real server networking, quota/reset payloads, live Workflow transcript, or real store delta. These require H818's owner-supplied external inputs.

_Dr. Mārcis Gasūns_
