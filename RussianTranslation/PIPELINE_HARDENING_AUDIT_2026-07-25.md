_Created: 01-08-2026 · Last updated: 05-09-2026_

# PWG Russian pipeline hardening audit — 2026-07-25

**Audited revision:** `f96361caa4279dde579de6ea0ca3d40784ea0863`

**Scope:** the current single-Max-account, headless PWG German-to-Russian
generation route; its coordinator/audit/promotion boundary; and the remaining
offline orchestration cost. This is a current-code audit, not a restatement of
the July audit backlog.

**Release verdict:** generation is eligible to proceed only through
`AWAITING_REVIEW` after the paid-path fixes named below pass. Live promotion is
**NO-GO** until the store/coordinator/TM close seam has a durable journal and
startup reconciliation. All live work must use `--stop-before-promote`.

No paid Claude call, login, network probe, canonical-store mutation, TM rebuild,
or promotion was performed during this audit.

## Actual one-profile call graph

```text
coordinator claim / prepare
  -> perf_preflight.py
  -> enforce_cost_gate()
  -> gen_opt_harness2.py
  -> sealed execution manifest v2

bounded_staged_run.py --execute --stop-before-promote
  -> probe_fleet([one profile])
     -> live_probe()
        -> warm-up Claude call
        -> measured Claude call
  -> BoundedSupervisor.run()
     -> make_run_window()                 # one lease, synchronous
        -> max_account_orchestrator import-coordinator / import-requeue
        -> max_account_orchestrator cmd_run_once()
           -> atomic profile-specific SQLite claim
           -> coordinator begin-run
           -> run_claimed()
              -> headless_worker.py
                 -> execution/profile/fingerprint validation
                 -> ActiveCallClaim
                 -> HeadlessEngine.call()
                    -> Claude translate / retry / split / heal calls
                 -> output + status hashes
           -> cmd_record_done()
              -> coordinator record-output
                 -> audit_window.py subprocess
                 -> clean subset / retry provenance
        -> AWAITING_REVIEW checkpoint
```

If promotion is later authorized, the close path is:

```text
coordinator promote-ready
  -> revalidate status / report / clean-output SHA
  -> promote_final_cards.py --batch-manifest
     -> promotion lock
     -> read / merge / backup
     -> fsynced temp + atomic canonical-store replace
     -> batch report
  -> mark leases promoted
  -> rebuild + optionally harvest + validate RU translation memory
```

`cohort_engine.py` is an offline injected-worker test engine. It is not the
production route above.

## Reproduced current findings

### P0 — Windows timeout cleanup can leave a paid descendant alive

`proc_tree.terminate_tree()` delegates to `taskkill /T /F`, then falls back to
killing only the immediate `Popen` parent
(`src/pilot/proc_tree.py:29-61`). Both paid worker calls and readiness probes
use this helper.

Both shipped depth-three checks failed on this Windows host:

- `python src\pilot\headless_worker_selftest.py`: the grandchild wrote its
  survival marker;
- `python src\pilot\max_account_orchestrator_selftest.py`: a probe-tree
  descendant survived.

A timed-out native Claude descendant can therefore continue holding the
profile/API call while the worker retries, making spend and one-profile
serialization untrustworthy. The Windows route needs kernel-backed process
containment (a kill-on-close Job Object) with the existing bounded fallback.

### P0 — promotion is not one recoverable store/coordinator/TM transaction

The canonical replace occurs in `src/promote_final_cards.py:802`. The child
writes the batch report only afterward (`:841`). Coordinator state changes and
TM rebuild occur only after the child returns
(`src/pilot/coordinator.py:1716-1778`).

Failure windows remain:

1. process death/report-write failure after the store replace leaves the store
   committed, leases `ready`, and TM stale;
2. death after leases are marked promoted but before TM validation leaves
   terminal coordinator state with stale or truncated TM;
3. resume can treat “no ready leases” as harmless and miss the divergence.

`promotion_receipt.py` is an offline scaffold, not a production call site. Its
current row-delta invariant is also false for multi-sense cards and
replacements. It must not be wired into production unchanged.

Required close design: a durable journal with phases
`prepared -> store_committed -> tm_validated`, clean-output and store hashes,
per-lease metrics, atomic TM replacement, and startup reconciliation by hashes
and provenance rather than key presence.

### P1 — automated result ingestion is not bound to its saved hash and run

`run_claimed()` persists `result_sha256`
(`src/pilot/max_account_orchestrator.py:418-425`), but
`cmd_record_done()` neither recomputes that hash nor supplies `--run-id`
(`:673-696`). Coordinator checks a run ID only when the caller supplies one
(`src/pilot/coordinator.py:1421-1433`).

A temporary-fixture reproduction replaced a completed output after its hash
was recorded. The replacement was still sent to `record-output`. A stale or
substituted result can consequently be audited under another attempt.

Required fix: persist the dispatch run ID with the job, require a non-empty
saved output hash for manifest jobs, recompute and compare it immediately
before ingestion, pass the saved `--run-id`, and require it when the running
lease has a sealed run ID.

### P1 — malformed paid wrappers can look evaluable at zero cost

`HeadlessEngine.call()` validates `structured_output.cards[]` before calling
`_accumulate_usage()` (`src/pilot/headless_worker.py:466-474`). A paid wrapper
with valid usage/cost but malformed structured content is retried without
recording spend.

The reproduction used two wrappers that each declared `$0.25`. The resulting
summary incorrectly reported:

```json
{
  "cost_evaluable": true,
  "observed_cost_usd": 0.0,
  "priced_calls": 0,
  "missing_usage_calls": 0
}
```

Required fix: parse the envelope and accumulate usage/cost before validating
the structured result. If the envelope itself is unreadable, count the paid
attempt and mark the run cost unevaluable.

### P1 — readiness probes bypass the per-profile active-call lock

Production generation acquires `ActiveCallClaim`
(`src/pilot/headless_worker.py:830-836`). `_probe_call()` invokes Claude
directly without that lock
(`src/pilot/max_account_orchestrator.py:877-894`).

Two operators can therefore probe a profile already translating. The warm-up
and measured calls must be inside the same profile lock used by production.

### P1 — `--max-calls` and cost ceilings remain post-hoc

The two readiness calls occur before `BoundedSupervisor` is created
(`src/pilot/bounded_staged_run.py:752-768`). The supervisor checks
`max_calls` only after an entire window completes
(`src/pilot/bounded_supervisor.py:268-365`).

The shipped bounded-run selftest explicitly permits `max_calls=5` to finish
with six calls. This means:

- `--max-calls 0` does not cover readiness calls;
- a window can overshoot by its retries and heals;
- a failed worker without a workflow summary may not enter accounting;
- cost ceilings stop only after the window.

The H1618 `cohort_engine` reservation ledger does not close this production
gap. A true hard ceiling needs a durable reservation consumed immediately
before every warm-up, measured, translate, failed, malformed, timed-out, retry,
and heal call. Until that lands, the handoff must not describe `--max-calls` or
`--cost-ceiling` as a strict pre-spawn guarantee; manifest agent ceilings remain
the enforced spawn bound.

### P2 — required preparation evidence can fail open

`coordinator.enforce_cost_gate()` returns when a required preflight is missing
or malformed (`src/pilot/coordinator.py:878-887`), then preparation proceeds.
Unreadable price evidence can therefore authorize paid execution.

Malformed canonical-store rows are also skipped while completed keys are
derived, and occupied-manifest parse failures are ignored during import. These
secondary parse gaps should be repaired separately; required preflight evidence
must fail closed before this live run.

### P2 — audit recovery and test isolation defects

- Threaded audit gates use unguarded `future.result()`
  (`src/pilot/audit_window.py:583`). An unexpected child exception aborts
  before durable report/requeue emission.
- Quarantine deletes the prior destination before replacement
  (`src/pilot/audit_window.py:221`), so replacement failure can lose recovery
  evidence.
- `test_coordinator_defect_requeue_uses_no_tm_and_out` invokes a synthetic
  defect requeue without `--no-residual`
  (`src/pilot/window_selftest.py:3545`), appending test key `a` to the tracked
  production residual registry.

These do fail closed against promotion, but they damage recovery evidence or
pollute production state. The stop-before-promote route should convert threaded
exceptions into full-window requeue evidence and isolate the residual selftest.

### P1 — card-TM rebuild is destructive and non-atomic

`translation_memory.build()` writes the live JSON file directly
(`src/pilot/translation_memory.py:444`). A crash during `json.dump` can
truncate the prior good TM. This is part of the promotion NO-GO and must be
fixed with temp-write, validation, fsync, and same-directory atomic replace.

Fragment sidecar malformed tails are skipped by the runtime loader; that is
audit-readable but should be reconciled with the denylist’s fail-closed torn
line policy.

## Historical findings checked and closed

- profile-specific transactional claims, required-slot dispatch, and
  execution-time config fingerprint validation are active;
- manifest translate/heal/total agent ceilings and timeout clamping are
  enforced before worker spawn;
- H1618 refuses starving `--max-agents 1` on multi-key windows;
- the worker’s active-call claim is kernel-backed;
- normal/requeue missing output and unreadable audit artifacts fail closed;
- canonical store writes use same-directory fsynced atomic replacement;
- promotion backups are exclusive, fsynced, and unique;
- promotion lock stale reclaim is identity checked;
- worktree store/sidecar resolution fails closed;
- H1553 clean-subset and defect fences are revalidated immediately before
  promotion;
- H1420’s TM `finally` covers Python exceptions after a successful promote
  child return, though not process death or child failure after store replace.

## Capability and enforcement map

| Declared control | Current enforcement |
|---|---|
| v2 profile slot + config fingerprint | enforced before execution |
| exact manifest model | passed to Claude; no separate Sonnet allow-list |
| translate/heal/total agent ceilings | enforced before each worker spawn |
| timeout ceiling | clamped before each worker spawn |
| `--max-agents 1` multi-key starvation | refused before any call |
| one active generation call per profile | enforced for worker, not probe |
| `--max-calls` | post-window observation, not a reservation |
| `--cost-ceiling` | preparation estimate + post-window stop, not reservation |
| `execution_route` | enforced as `claude-cli-headless` |
| `executor_lane`, `validation_method` | non-empty metadata only |
| result SHA | produced, not checked at ingestion |
| run ID | sealed, but optional at automated ingestion |
| promotion receipt/journal | offline scaffold only |

## Measured remaining speed opportunity

The audit child must remain an isolated subprocess with its 30-minute timeout.
The avoidable residue is the parent coordinator startup: the current H1339
fixture launches `coordinator.py record-output` once per lease.

On this worktree:

- one `coordinator.py status` process: **0.861 s**;
- five processes: **5.195 s**;
- four avoidable starts: **4.333 s**.

The smallest safe optimization is a sequential `record-output-batch` command
that loops over the existing per-lease `record_output()` unit. Each item keeps
its own operation token, lock transitions, audit subprocess, timeout, report,
and state commit. It is deliberately fail-fast rather than one batch
transaction: earlier leases remain recorded and later leases remain running,
matching today’s sequential semantics.

Ship criterion: a hermetic A/B using the H1339 fixture must show deterministic
outputs, identical semantic store hash and per-lease states, and a lower audit
median. Only audit/total timing may differ.

## Current one-Max launch boundary

The five July medium50 manifests bind **generation** to
`claude-sonnet-5`. “Opus 5” is the orchestration/review session requested by the
operator; it must not rewrite the sealed generation model.

The surviving main-checkout artifacts are not currently sufficient for the
canonical bounded route: coordinator state lacks their leases and the artifact
directories lack required preflights. They must be rehydrated/reprepared before
execution. The safe live sequence is:

1. authenticate exactly one Max profile;
2. bind the same config-directory path/fingerprint used by newly prepared v2
   manifests;
3. run a fresh representative >=5 KiB gate and one-key synthetic canary;
4. dry-run, then execute one production window only;
5. omit `--max-agents` for multi-key work;
6. stop at `AWAITING_REVIEW`;
7. run a new live gate before every later paid window.

No result from one account authorizes another account or another window.

## Baseline verification

- `python src\pilot\window_selftest.py`: **183/183 passed**
- `python src\pilot\lang_parity_check.py`: **81 entries complete; no drift**
- hermetic benchmark: deterministic signature
  `7f056b6dc8...`; median total **30.968 s** over three measured runs
- `python src\pilot\headless_worker_selftest.py`: **failed**, depth-three
  grandchild survived
- `python src\pilot\max_account_orchestrator_selftest.py`: **failed**,
  probe-tree descendant survived
- focused result-substitution and malformed-wrapper fixtures: findings
  reproduced

The 183-test suite’s accidental residual-registry append was removed after the
baseline run; the audit itself left no intentional production-data change.

## Not audited

Paid model behavior, OAuth/login state, account billing identity, provider
quota, real 403 recovery, translation quality, canonical store/TM contents,
publication export, real power-loss behavior, EN end-to-end promotion, legacy
Workflow execution, and multi-profile live scheduling were not audited.

_Dr. Mārcis Gasūns_
