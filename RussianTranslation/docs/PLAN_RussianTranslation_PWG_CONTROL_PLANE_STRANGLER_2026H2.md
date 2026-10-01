# PLAN — PWG translation control-plane strangler (2026 H2)

_Created: 30-08-2026 · Last updated: 30-08-2026_

## Goal

Replace the PWG translation programme's overlapping operator state machines and route-specific
money/store behavior with one comprehensible lifecycle while preserving the proven translation
engine. The target is one standard-library control-plane package, one transactional campaign
database, one paid-call kernel, pure audits, and coordinator-journaled writes. Wave 1 migrates the
PWG-TM xAI route, provides a DeepSeek fallback adapter, shadow-adapts the existing Claude headless
lane, and proves parity without changing prompts or canonical data.

## Audit verdict

**Architectural redesign is warranted, but a ground-up translation rewrite is not.** The live
Claude path already has strong manifest sealing, call reservations, timeouts, deterministic gates,
store locking, and promotion recovery. The risk is architectural divergence around it:

1. The current tree has 585 Python files under `RussianTranslation/src`, including 236 under
   `src/pilot`; 519 files expose CLI-style entry points.
2. Coordinator JSON, orchestrator SQLite, supervisor checkpoints, call ledgers, and the promotion
   journal overlap as state authorities.
3. The operator-visible close path still exposes direct promotion although repository policy
   requires coordinator-journaled promotion.
4. Audit code can rename/quarantine artifacts, so verdict production is not pure.
5. The newer PWG-TM live route can make billed xAI calls outside the hardened reservation,
   timeout, cost, and sealed-provenance boundary; refill and canonical migration lack the mature
   promotion transaction.
6. The current canonical TM bytes match their recorded count/hash, but recursive inspection found
   79 rows (609 occurrences) with nested `{Tn}` residue while reconciliation still reports success.

## Layer documents

1. [Roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_PWG_CONTROL_PLANE_2026H2.md)
2. [Architecture](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_PWG_CONTROL_PLANE.md)
3. [Implementation](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_PWG_CONTROL_PLANE.md)
4. [Verification](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_PWG_CONTROL_PLANE.md)
5. [Plan metadoc](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.meta.md)

## Decisions taken

| # | Fork | Ruling | Consequence |
|---|---|---|---|
| R1.1 | Audit boundary | Production PWG→RU lifecycle, every provider adapter, and the `pwg-ru-data` boundary | Cologne source/build and unrelated research/export scripts remain dependencies, not redesign targets. |
| R1.2 | Target | One operator CLI and lifecycle with provider adapters | No parallel supported operator protocols. |
| R1.3 | Primary objective | Safety and comprehensibility first | Canonical state, spend, and mutations must be attributable before throughput work. |
| R1.4 | Migration posture | Strangler migration with compatibility adapters | Preserve working behavior and retire old paths only after parity proof. |
| R1.5 | Wave-1 live scope | Fixture-backed changes plus bounded live canaries | No production promotion. |
| R2.1 | Paid execution | One shared execution kernel | Claude, xAI, DeepSeek, OpenRouter, and future routes share reservation/timeout/usage/sealing. |
| R2.2 | State owner | Transactional SQLite campaign database | JSON manifests and receipts are immutable evidence exports, not mutable authorities. |
| R2.3 | Promotion authority | Coordinator journal only | Direct promoters become dry-run/build helpers or compatibility shims. |
| R2.4 | Audit behavior | Pure verdict computation | Quarantine, denylist, refill, and rewrites move to explicit apply commands. |
| R2.5 | Domain model | `Campaign → Job → Attempt → Call → Artifact → Verdict → Promotion` | Whole-card and fragment work differ by cardinality, not by unrelated schemas. |
| R3.1 | Code home | New `RussianTranslation/src/pwg_pipeline/` package | Existing modules are wrapped before any relocation. |
| R3.2 | Dependencies | Python standard library first | Use `sqlite3`, dataclasses, `argparse`, and existing atomic I/O; no ORM/workflow framework. |
| R3.3 | State migration | Import, shadow-compare, then cut over by lifecycle stage | Avoid prolonged dual-write. |
| R3.4 | Wave-1 slice | Shared kernel/schema; fully wrap PWG-TM/xAI; DeepSeek fallback; shadow Claude | Do not rewrite the proven Claude engine. |
| R3.5 | Legacy CLIs | Compatibility shims call the facade | Disable an old writer after two canaries plus one production-equivalent replay. |
| R3.6 | Initial canary | Non-promotable provider canaries | Fixture input, explicit caps, sealed usage, no store write. |
| R4.1 | Parity | Exact contract parity on frozen fixtures | Compare state, calls, verdicts, artifacts, requeue, and promotion deltas. |
| R4.2 | Replay matrix | Four campaigns | Clean, partial/requeue, provider failure/timeout, and interrupted promotion/recovery. |
| R4.3 | Data bar | Recursive validation of every row | Required provenance, identity, hashes, and zero unresolved placeholders. |
| R4.4 | Fault injection | Every irreversible boundary | Recovery must be idempotent before cutover. |
| R4.5 | xAI canary cap | One request, bounded output and spend | Missing usage or route mismatch is NO-GO. |
| R4.6 | Cutover gate | Automation plus independent review | Money/store paths need a second evidence pass. |
| R5.1 | Ambiguity | Default-and-log only for reversible choices | Park money, canonical-data, credential, or publication ambiguity. |
| R5.2 | Stop conditions | Global halt on accounting/route/integrity/secrets/non-idempotence | Ordinary adapter/test failures stop only their track. |
| R5.3 | Landing | Isolated worktree, scoped PRs, merge on green review | Never use the dirty shared checkout. |
| R5.4 | Fence | No canonical mutation, prompt-policy change, publication, credential copying, or PWG-source edit | Wave 1 remains a control-plane migration. |
| R5.5 | Adjacent work | No opportunistic cleanup | Route residuals separately. |
| R5.6 | Provider authority | At most one xAI request plus one DeepSeek request; USD 4 total | `max_calls=2`, no retries/rerolls/promotion; both require all offline gates green. |

## Autonomy contract

### On ambiguity

Apply a marked default and log it only when the choice is reversible and cannot affect money,
canonical data, credentials, publication, or translation semantics. Park any ambiguity on those
five axes and continue only unaffected tracks.

### Stop conditions

Halt the whole wave on unevaluable or inconsistent usage, execution-route mismatch, canonical
integrity failure, suspected secret exposure, or a recovery path that is not demonstrably
idempotent. Halt only the affected track for an ordinary test failure, unavailable optional
provider, or adapter-local defect. One genuine repair attempt is allowed; then preserve evidence
and stop that track.

### Commit and review authority

Work only in an isolated worktree. Use scoped commits and PRs. Merge only when the required
automated gates and an independent review of money/store paths are green. Never commit or push
from the dirty shared checkout.

### Fence

1. Never mutate the canonical PWG card store or canonical PWG-TM data in Wave 1.
2. Never change prompts, translation policy, sense semantics, or editorial decisions.
3. Never copy credentials or profile directories; consume existing environment bindings only.
4. Never publish, change repository visibility, or edit the PWG/csl-orig source repositories.
5. The only paid work is one xAI plus one DeepSeek non-promotable canary, maximum two calls and
   USD 4 total, with no retry, reroll, fallback call beyond those two, or promotion.

## Prior-art verdicts

| Concern | Verdict | Reuse / gap |
|---|---|---|
| Claude manifest compiler and engine | **EXISTS** | Reuse `gen_opt_harness2.py` and `headless_worker.py`; add an adapter, do not rewrite. |
| Deterministic acceptance gates | **EXISTS** | Reuse `audit_window.py` gate functions; split verdict calculation from mutations. |
| Call reservation and timeout ceilings | **EXISTS** | Reuse `call_reservation.py` and `execution_contract.py` inside the shared kernel. |
| Store lock and recovery journal | **EXISTS** | Reuse `store_write.py`, `promote_lock.py`, and `promotion_journal.py`. |
| PWG-TM xAI generation | **PARTIAL** | Preserve translation logic; replace its live call/accounting boundary. |
| DeepSeek provider path | **PARTIAL** | Adapt existing OpenRouter/DeepSeek plumbing to the same kernel. |
| Unified lifecycle state | **NEW** | One transactional schema and facade are the genuine gap. |
| Recursive canonical validation | **PARTIAL** | Extend current validators to nested payloads and fail closed if JSON Schema is unavailable. |

## Autonomy-readiness gate

**PASS, conditional on the execution handoff honoring the provider fence.** Every Wave-1
deliverable has an architecture contract, ordered file-level sequence, acceptance criteria, and
risk treatment. No blocking design fork remains. The only live actions are explicitly bounded;
all canonical writes remain forbidden.

## Execution handoff

[H3714 (Codex) — PWG translation control-plane strangler: shared paid-call kernel,
transactional campaign state, and journaled TM path](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3714-Codex_SanskritLexicography_pwg-control-plane-strangler-wave1_30.08.26.md)

```text
Read C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\docs\PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.md and execute it.
```

_Dr. Mārcis Gasūns_
