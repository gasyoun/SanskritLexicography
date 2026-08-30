# ROADMAP — PWG translation control-plane strangler (2026 H2)

_Created: 30-08-2026 · Last updated: 30-08-2026_

Parent: [PLAN — PWG translation control-plane strangler](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.md).

## Wave 0 — freeze contracts and evidence

1. Freeze four representative replay packets: clean success, partial/requeue, provider
   timeout/failure, and interrupted promotion/recovery.
2. Record current state transitions and artifact hashes from the legacy paths.
3. Turn the current audit findings into executable negative tests, including false call counts,
   missing usage, route ambiguity, non-transactional refill, non-atomic migration, and nested
   placeholder residue.
4. Correct operator-document drift only where necessary to make coordinator promotion the named
   authority; do not change live behavior yet.

**Unblocks:** a stable comparison target for every later cutover.

## Wave 1 — common control-plane foundation

1. Add the `pwg_pipeline` package with the unified domain records and SQLite repository.
2. Add an importer for coordinator JSON, orchestrator SQLite, call ledgers, and promotion receipts.
3. Emit immutable JSON evidence receipts from the database; never treat those exports as writable
   state.
4. Add the shared paid-call kernel with pre-spawn reservation, timeout, usage normalization,
   sealed output, and terminal accounting on every outcome.

**Unblocks:** route adapters with one safety contract.

## Wave 2 — migrate the divergent PWG-TM lane

1. Wrap the existing xAI translation request behind the shared kernel.
2. Add DeepSeek as a provider adapter using the same request/result contract.
3. Replace output-derived call accounting with one ledger row per provider request.
4. Move refill and canonical migration behind journaled, atomic apply operations.
5. Add recursive full-row validation and fence the 81 currently detected placeholder-bearing rows
   without editing them.

**Unblocks:** safe non-promotable provider canaries and trustworthy economics.

## Wave 3 — shadow the proven Claude path and purify audit

1. Add a Claude-headless adapter that delegates to the existing compiler and worker.
2. Shadow-record its lifecycle in the new database while the legacy path remains authoritative.
3. Extract pure verdict functions from audit; move quarantine, denylist, residual stamping, and
   renames into explicit apply commands.
4. Make the coordinator journal the sole promotion authority and turn direct close/promote paths
   into compatibility shims.

**Unblocks:** exact shadow comparison without rewriting the translation engine.

## Wave 4 — verification and bounded live evidence

1. Replay the four frozen campaigns through legacy and new facades; require zero unexplained
   contract mismatches.
2. Run the irreversible-boundary fault-injection matrix and prove idempotent recovery.
3. Run the full existing RussianTranslation gates and language-parity checks.
4. Obtain independent review of every money/store-path diff.
5. If and only if all offline gates are green, run one xAI and one DeepSeek non-promotable canary
   under a shared `max_calls=2`, USD 4 total ceiling, bounded output, and no retry.

**Unblocks:** a cutover recommendation, not production promotion.

## Wave 5 — later cutover (not authorized by this plan)

1. Cut over lifecycle stages one at a time after separate authorization.
2. Disable old writers only after two successful canaries plus one production-equivalent replay.
3. Retain shims for one release window, then remove them with evidence that no callers remain.
4. Consider throughput and multi-profile work only after the state and accounting model is singular.

## Non-goals

1. Rewriting the Claude translation compiler or worker.
2. Changing prompts, language policy, sense segmentation, or editorial judgments.
3. Mutating the canonical card store or canonical TM in Wave 1.
4. Redesigning Cologne PWG source/build workflows.
5. Consolidating unrelated research, export, and review-sheet scripts.
6. Adding an ORM, service daemon, queue broker, or external workflow framework.

_Dr. Mārcis Gasūns_
