# Pipeline audit: PWG Russian translation

**Auditor:** Codex (GPT-5), with three independent read-only audit passes  
**Audit date:** 2026-07-21 (Europe/Moscow)  
**Repository:** `gasyoun/SanskritLexicography`  
**Immutable audit base:** [`50c6c5aa5d622a878b4966e1fee1a75e4b359a90`](https://github.com/gasyoun/SanskritLexicography/tree/50c6c5aa5d622a878b4966e1fee1a75e4b359a90)  
**Repair branch:** `codex/rt-pipeline-hardening-20260721`  
**Scope:** `RussianTranslation`, from prepared lease through headless execution, audit,
promotion, translation-memory rebuild, checkpoint/resume, and offline tests.  
**Not exercised:** paid Claude generation, live account probes, canonical-store promotion,
network APIs, publication export, or deployment. The audit used source inspection, temporary
fixtures, and hermetic self-tests only.

## Executive assessment

The content gates and deterministic regression coverage are strong, but the control plane is not
yet transactionally closed end to end. The highest risks sit between otherwise well-tested stages:
an account could claim a manifest bound to another profile; a worker result can be replaced after
its hash was recorded but before ingestion; a store commit can outlive its receipt and translation-
memory rebuild; and campaign cost/call limits omit some paid calls. Several error paths also turned
unreadable artifacts into empty reports.

The audited path is usable for bounded attended work after the repairs on this branch, but
unattended multi-profile scale-out should wait for the remaining P0 attempt-binding,
promotion-reconciliation, and campaign-ledger work. The current “bounded staged” driver probes a
fleet but drains one lease synchronously, so extra profiles mostly add probe cost, not throughput.

## Actual production call graph

```text
no_pwg_scale_plan.py
  -> perf_preflight.py + gen_opt_harness2.py
  -> coordinator.register_prepared_lease()

bounded_staged_run.py --execute
  -> probe_fleet()                         # paid readiness calls
  -> BoundedSupervisor.run()               # one lease/window, synchronous
     -> max_account_orchestrator.import-coordinator/import-requeue
     -> max_account_orchestrator.run-once
        -> coordinator begin-run
        -> run_claimed()
           -> headless_worker.py
              -> validate_manifest()/validate_profile()/ActiveCallClaim
              -> Claude CLI batches, retries, splits and healing
              -> workflow result + status artifacts
     -> max_account_orchestrator.record-done
        -> coordinator record-output
           -> normalize_workflow_result()
           -> audit_window.py
              -> collect + schema + NWS + semantic + sense + style gates
           -> clean output + ready/ready_partial/needs_requeue state
     -> coordinator promote-ready
        -> promote_final_cards.py --batch-manifest
           -> claim + backup + canonical-store replace + denylist + report
        -> per-lease coordinator state update
        -> RU TM build/build-frags/validate
     -> outer audit/accounting/checkpoint
```

`max_account_orchestrator.py staged-run` is a second monolithic entry point over much of the same
path. Maintaining both has allowed runtime-mode, coordinator-directory, accounting, and resume
semantics to drift.

## Capability and ownership map

| Concern | Owning component | Current behavior | Audit verdict |
|---|---|---|---|
| Lease preparation | [`coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/coordinator.py) | Reserves inputs and emits sealed manifests | Strong gates; preflight parse failures can fail open |
| Profile contract | [`execution_contract.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/execution_contract.py) | Validates v2 route/profile/model at worker start | Correct, but was enforced after scheduler claim |
| Fleet dispatch | [`max_account_orchestrator.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/max_account_orchestrator.py#L217) | SQLite claims, one active job/account, threaded workers | Profile and result/run binding were incomplete |
| Bounded stop/resume | [`bounded_supervisor.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/bounded_supervisor.py#L244) | Window/call/clean/cost/empty bounds, replace checkpoint | Some inputs failed open; checkpoint not fsync-durable |
| Live staged wrapper | [`bounded_staged_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/bounded_staged_run.py#L179) | Probes once, drains one lease, promotes, audits | Serial despite a fleet; usage-path drift |
| Content audit | [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/audit_window.py) | Parallel deterministic gates and requeue artifacts | Exception/report and quarantine semantics need hardening |
| Canonical promotion | [`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/promote_final_cards.py#L509) | Batch merge and atomic store replacement | Receipt/TM/coordinator state are outside the transaction |
| Translation memory | [`translation_memory.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/translation_memory.py) | Rebuilt and validated after promotion | Correct target resolution; repeated sidecar loads cost time |
| Observability | [`run_observability.py`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/run_observability.py) | Append-only events and census | Not the single atomic source for campaign spend |

## Ranked findings and repair disposition

### P0 — fix before unattended scale-out

1. **Scheduler claim ignored manifest profile binding.** The claim transaction selected the first
   pending row without filtering `execution.profile_slot`; validation occurred only after an
   attempt was consumed. Reverse queue/account order could burn all attempts as configuration
   failures. Base evidence: [`_claim_tx`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/max_account_orchestrator.py#L217) and
   [`run_claimed`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/max_account_orchestrator.py#L333).
   **Disposition:** fixed on the repair branch. Imported jobs persist `profile_slot`; manifest jobs
   are claimable only by that account; old valid v2 rows are backfilled; invalid rows stay
   unclaimable. A reverse-order regression protects the contract.

2. **Recorded output is not bound to the worker attempt at ingestion.** The scheduler records a
   result hash, but `record-done` checks only that the path exists and omits the coordinator run ID.
   An old or replaced file can be audited under a newer attempt. Evidence:
   [`result_sha256` recording](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/max_account_orchestrator.py#L388),
   [`cmd_record_done`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/max_account_orchestrator.py#L632), and
   [optional run guard](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/coordinator.py#L1373).
   **Disposition:** open. Persist the run/attempt ID, re-hash immediately before ingestion, require
   `--run-id` for automated jobs, and compare result execution/provenance with the sealed manifest.

3. **Store commit, receipt, coordinator state, and TM rebuild are not one recoverable
   transaction.** The canonical store is replaced before the non-atomic report write, and
   reconciliation begins only after the child returns. A crash can leave a committed store, a
   `ready` lease, and stale TM. Evidence:
   [`os.replace`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/promote_final_cards.py#L598),
   [report write](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/promote_final_cards.py#L621), and
   [coordinator invocation](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/coordinator.py#L1669).
   **Disposition:** open. Write an atomic fsynced receipt with before/after store hashes and make
   startup/promotion reconcile receipt, store, lease state, and TM idempotently.

4. **Cost/call ceilings do not cover the campaign.** Readiness probes occur before the supervisor
   ledger; failed/malformed calls can lack usage; limits are checked after a complete window.
   Evidence: [`probe call site`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/bounded_staged_run.py#L665) and
   [post-window accounting](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/bounded_supervisor.py#L268).
   **Disposition:** partially fixed. Current worker `summary.usage.observed_cost_usd` and nested
   tokens are now read correctly. One atomic campaign ledger must still reserve before every
   probe/model spawn.

### P1 — correctness, recovery, and throughput

5. **Missing/corrupt audit inputs could become zero-progress completion.** The live wrapper replaced
   unreadable coordinator/output JSON and a missing lease with empty dictionaries, then checkpointed
   the window as completed. Base evidence: [`audit_from_coordinator`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/bounded_staged_run.py#L179).
   **Disposition:** fixed on the repair branch; these paths now raise before checkpointing.

6. **Default audit failures could produce an all-clean synthetic report.** An unreadable Workflow
   payload or a crashed sense gate was converted to empty defects. **Disposition:** fixed on the
   repair branch; both fail closed and have a no-checkpoint regression.

7. **Bounded resume and custom coordinator routing have known local fixes not integrated into the
   audit base.** Normal windows returning `None` could complete silently; scope recovery passed the
   wrong object; direct promotion/requeue subprocesses could lose `PWG_COORDINATOR_DIR`. Fixes exist
   on the active dirty local branch `h1386-post-h1339-review-fixes` (`d46ccc6d`, `3e119790`).
   **Disposition:** do not duplicate or cherry-pick from an active dirty worktree; reconcile those
   focused commits after its owner finishes.

8. **Bounded staging is serial.** One supervisor item is one lease and `run_window` blocks through
   dispatch, audit, and promotion. Up to four profiles are probed, but only one lease is drained
   before the next item. Evidence: [`one-lease runner`](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/bounded_staged_run.py#L414) and
   [synchronous supervisor](https://github.com/gasyoun/SanskritLexicography/blob/50c6c5aa5d622a878b4966e1fee1a75e4b359a90/RussianTranslation/src/pilot/bounded_supervisor.py#L268).
   **Disposition:** open, assigned to the Fable 5 handoff after P0 prerequisites. Dispatch a bounded
   cohort, audit per lease, then perform one batch promotion/TM rebuild per accepted wave.

9. **Safety parses fail open.** Queued-manifest parse failures are ignored when deriving occupied
   keys; malformed canonical-store rows can be skipped; required preflight parse failures can
   proceed without a blocking price. **Disposition:** open; partial censuses and malformed required
   artifacts must fail with exact file/line diagnostics.

10. **Parked-account checks are wider than the dispatch allow-list.** A healthy excluded account
    can mask that all admitted accounts are parked, causing a hot loop. **Disposition:** open; count
    only the probed/admitted fleet.

### P2 — durability, performance, and maintenance

11. Critical replace-based writers do not consistently flush/fsync files and parent directories.
12. Promotion and coordinator subprocesses lack operation deadlines and process-tree timeouts.
13. Threaded audit exceptions can escape before a blocked report is written; NWS quarantine can
    mutate global output before the whole audit accepts.
14. Documentation mixes historical Max Workflow instructions with the headless production route.

## Performance evidence

An instrumented Windows profile found canonical path resolution launched 88 Git subprocesses in a
small preflight (4.50 s of 5.29 s). Caching checkout identity per normalized directory is process-
local and semantics-preserving; environment store/TM overrides remain outside the cache. Promotion
also scanned the 26 MB canonical store twice although its receipt already had exact row counts.

The frozen H1339 fixture was run once before and once after (`warmups=0`, `runs=1`, identical
Python/platform/fixture). This is a smoke comparison, not a statistical benchmark, but the output
signature was exactly identical:
`da1341e6ac112bf83c7c521d194f698aa39da067075b636463fa6748c43fb629`.

| Stage | Before | After | Change |
|---|---:|---:|---:|
| Prepare | 4.862 s | 5.153 s | +6.0% (single-run noise) |
| Normalize | 0.094 s | 0.056 s | -40.4% |
| Audit | 8.616 s | 4.156 s | -51.8% |
| Promotion plan | 0.748 s | 0.364 s | -51.3% |
| Store write | 4.270 s | 1.989 s | -53.4% |
| **Total** | **17.842 s** | **11.354 s** | **-36.4%** |

Next low-risk speed work is to snapshot directory names once per audit rather than rebuilding
`set(os.listdir(...))` per card. Higher-risk work is to avoid full harness rebuilds per preflight
partition, cache TM/denylist reads by file signature, move scans outside the claim lock, and add
cohort dispatch.

## Verification specification

1. Mutate a completed output after its recorded hash; `record-done` must refuse before audit.
2. Begin run A, release, begin run B, then submit A's output; run binding must refuse while B stays
   running.
3. Fault-inject after store replace but before report write; restart must reconcile TM and lease
   state without duplicate promotion.
4. Under `max_calls=0/1/3`, count probes, malformed calls, retries, failures, and successes in one
   ledger and prove the bound is never exceeded.
5. Feed missing, malformed, and over-ceiling preflight through both preparation entry points; all
   must refuse unless an audited override exists.
6. Block two or three fake profile workers on a barrier; prove peak concurrency, deterministic
   store bytes, exact per-window accounting, one promotion/TM rebuild per wave, and crash-safe
   resume without re-launching completed work.
7. Make each threaded audit gate raise; require a complete blocked report and requeue-all with no
   global quarantine mutation.

## Recommended sequence

1. Land the current fail-closed/profile-binding/path-cache/store-scan repairs.
2. Reconcile the focused H1386 resume/routing commits after that worktree is no longer active.
3. Implement attempt/result/run binding.
4. Add the atomic promotion receipt and startup reconciliation.
5. Add the campaign-wide call/cost reservation ledger.
6. Only then implement Fable 5's cohort scheduler and measure 1/2/3-profile scaling.
