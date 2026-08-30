# ARCHITECTURE — PWG translation control plane

_Created: 30-08-2026 · Last updated: 30-08-2026_

Parent: [PLAN — PWG translation control-plane strangler](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.md).

## Target component map

```text
operator / scheduler / compatibility shim
                    │
                    ▼
             pwg_pipeline CLI
                    │
          CampaignService + SQLite
                    │
       ┌────────────┴─────────────┐
       ▼                          ▼
 provider adapter          pure audit adapter
       │                          │
       ▼                          ▼
 shared paid-call kernel      sealed Verdict
 reserve → timeout → call          │
 usage → seal → finalize           ▼
       │                    explicit ApplyService
       ▼                          │
 sealed Artifact                  ▼
       └──────────────────► coordinator promotion journal
                                      │
                                      ▼
                           canonical stores + derived TM
```

## Boundary rules

1. The CLI/facade is the only supported operator entry point.
2. Provider adapters translate provider-specific request and usage shapes; they do not own
   budgets, retries, persistence, promotion, or canonical paths.
3. The paid-call kernel reserves before spawn/request and finalizes exactly one call record on
   success, refusal, malformed output, timeout, or exception.
4. Audit accepts immutable artifacts and returns a sealed verdict. It has no filesystem mutation
   methods.
5. ApplyService consumes an approved verdict and delegates every canonical mutation to the
   coordinator promotion journal.
6. The database is the mutable system of record. Manifests, results, and receipts are immutable
   evidence addressed by hashes.

## Unified domain model

| Entity | Required identity and role |
|---|---|
| `Campaign` | Stable scope, language, budgets, fence, creator, lifecycle version. |
| `Job` | One whole card or fragment unit, source identity/hash, provider-independent intent. |
| `Attempt` | One execution try for a job; records adapter, route, requested model, and outcome. |
| `Call` | One billable provider request; reserved before I/O and finalized exactly once. |
| `Artifact` | Immutable manifest/input/result/audit/receipt with SHA-256, media type, and path. |
| `Verdict` | Pure gate output tied to exact input/result artifacts and validator versions. |
| `Promotion` | Journaled apply transaction with before/after hashes and recovery phase. |

Card and fragment work use the same entities. A card job may have one call; a split card owns
child jobs; a provider batch call may cover several jobs through an explicit join table. Call count
is never inferred from returned rows.

## State model

```text
planned → prepared → reserved → running → captured → audited
                                      │          │
                                      │          ├─→ needs_requeue
                                      │          ├─→ blocked
                                      │          └─→ awaiting_review
                                      └─→ failed

awaiting_review → apply_prepared → store_committed → derived_validated
                → coordinator_committed → complete
```

Every transition is transactional and append-recorded. A transition may advance only when its
required artifact hashes exist. Restart reads the database and reconciles an incomplete promotion
through the existing journal; it does not infer progress from filenames.

## Shared paid-call kernel

The kernel owns:

1. route/model/profile validation;
2. pre-spawn call and cost reservation;
3. hard timeout and descendant/process cleanup where applicable;
4. request and response hashing;
5. provider usage capture and normalization;
6. cost evaluability and ceiling checks;
7. terminal call finalization on every exit path;
8. sealed artifact creation.

The adapter protocol owns only `prepare_request`, `invoke`, `parse_result`, and
`normalize_usage`. The initial adapters are `XaiTmAdapter`, `DeepSeekTmAdapter`, and
`ClaudeHeadlessShadowAdapter`. The Claude adapter delegates to the current worker and never
duplicates its model logic.

## Persistence

Use standard-library `sqlite3` with foreign keys, WAL mode, explicit transactions, and schema
migrations recorded in a `schema_version` table. Immutable artifact content remains in files;
SQLite stores identities, hashes, state, bindings, and relative paths. Secrets, prompts containing
credentials, and profile directories never enter the database.

## Canonical-write protocol

1. Pure audit emits a verdict.
2. Human or autonomous policy selects a verdict for apply.
3. ApplyService prepares a promotion bundle with exact before/after hashes.
4. The existing coordinator journal advances `prepared → store_committed → derived_validated →
   coordinator_committed → complete` under the canonical store claim.
5. Refill and migration use the same bundle protocol; they never truncate one store and append to
   another outside a transaction.

## Migration architecture

1. Import legacy coordinator/orchestrator/ledger/journal state into a new campaign database.
2. Shadow the same legacy action and compare state transitions plus artifact hashes.
3. Explain or eliminate every mismatch.
4. Redirect one legacy CLI through the facade while its underlying engine remains unchanged.
5. Disable the old writer only after the ruled acceptance gate.
6. Avoid dual-write beyond the bounded shadow interval.

## Build-versus-reuse verdict

| Component | Verdict | Source of truth |
|---|---|---|
| Manifest construction | Reuse | `src/pilot/gen_opt_harness2.py` |
| Claude execution | Reuse | `src/pilot/headless_worker.py` |
| Reservation/limits | Extend | `src/pilot/call_reservation.py`, `src/pilot/execution_contract.py` |
| Deterministic gates | Extract/reuse | `src/pilot/audit_window.py` |
| Promotion recovery | Reuse | `src/pilot/promotion_journal.py`, `src/pilot/coordinator.py` |
| Store locking/atomic I/O | Reuse | `src/store_write.py`, `src/promote_lock.py`, `src/rt_io.py` where safe |
| PWG-TM translation logic | Reuse | `src/pwg_tm_generate.py` |
| Unified lifecycle/DB/facade | New | `src/pwg_pipeline/` |
| Recursive validator | Extend | `src/pwg_tm_canonical.py` through a pure package validator |

## Explicitly retired architecture

1. Direct provider SDK calls from translation-domain modules.
2. Output-row-derived call accounting.
3. Audit-time mutation.
4. Direct canonical promotion from the close runbook.
5. Mutable JSON plus SQLite as co-equal state authorities.
6. Treating forensic workflow JavaScript as the production executable artifact.

_Dr. Mārcis Gasūns_
