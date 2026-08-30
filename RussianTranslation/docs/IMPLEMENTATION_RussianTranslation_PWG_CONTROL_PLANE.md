# IMPLEMENTATION — PWG translation control plane

_Created: 30-08-2026 · Last updated: 30-08-2026_

Parent: [PLAN — PWG translation control-plane strangler](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.md).

This is the file-level execution sequence for Wave 1. It replaces the PWG-TM/xAI control
path, adds DeepSeek as the bounded fallback/provider lane, and shadow-imports the proven
Claude path. It does not rewrite prompts, deterministic translation gates, the Claude
compiler/worker, or canonical translation policy.

## Reuse before build

1. Reuse [`src/pilot/call_reservation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py) for reserve-before-dispatch semantics.
2. Reuse [`src/pilot/usage_accounting.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/usage_accounting.py) and [`src/pilot/route_transport.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/route_transport.py) for evaluable usage and route envelopes.
3. Reuse [`src/pilot/promotion_journal.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/promotion_journal.py), [`src/pilot/store_write.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/store_write.py), and [`src/pilot/promote_lock.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/promote_lock.py) for journaled, locked mutation.
4. Reuse [`src/pilot/h1210/deepseek_arm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/deepseek_arm.py) for DeepSeek streaming and usage parsing.
5. Treat [`src/pilot/headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) as an external legacy adapter in Wave 1; do not change its semantics.

## Step 1 — domain and transactional state

1. Add `src/pwg_pipeline/model.py` with typed `Campaign → Job → Attempt → Call → Artifact → Verdict → Promotion` entities and legal transitions.
2. Add `src/pwg_pipeline/schema/001_initial.sql` for campaigns, jobs, attempts, calls, artifacts, verdicts, promotions, legacy imports, and schema migrations.
3. Add `src/pwg_pipeline/repository.py` with `BEGIN IMMEDIATE`, compare-and-set transitions, foreign keys, non-negative accounting constraints, and idempotency keys.
4. Add `tests/test_pwg_pipeline_model.py` and `tests/test_pwg_pipeline_repository.py` before implementation; pin transition refusal, uniqueness, transaction rollback, and reopen/recovery behavior.

## Step 2 — sealed evidence and recursive validation

1. Add `src/pwg_pipeline/evidence.py` for canonical UTF-8/LF JSON, temporary-file write, `fsync`, atomic replacement, SHA-256 binding, and byte-different collision refusal.
2. Add `src/pwg_pipeline/validation.py` to traverse every nested dictionary, list, and string and report JSONPath-like locations.
3. Detect missing provenance, duplicate identities, broken hash lineage, route/model mismatches, invalid canonical rows, and unresolved `{T<number>}` or registered sentinels at any depth.
4. Fence the existing defective rows in a sealed report; never rewrite them as part of this step.

## Step 3 — one paid-call kernel

1. Add `src/pwg_pipeline/providers.py` with a provider protocol, xAI adapter, DeepSeek adapter, and read-only Claude evidence adapter.
2. Add `src/pwg_pipeline/kernel.py` implementing exactly one sequence: validate budget → reserve → persist → dispatch under timeout → capture usage and returned route → seal evidence → finalize.
3. Fail closed on missing usage, ambiguous cost, route substitution, malformed response, timeout, or ceiling breach.
4. Permit no automatic retry, reroll, fallback, or extra probe in Wave 1.

## Step 4 — pure audit and explicit effects

1. Add `src/pwg_pipeline/audit.py`; it reads sealed artifacts and emits only a sealed verdict.
2. Add `src/pwg_pipeline/apply.py`; it consumes an accepted verdict and records explicit `requeue`, `quarantine`, or `refill` intents.
3. Prevent audit code from renaming files, appending denylists, refilling quarantine, changing coordinator state, or touching canonical data.
4. Translate the current `audit_window.py` result into the new verdict model without invoking its mutating options.

## Step 5 — sole journaled promotion authority

1. Add `src/pwg_pipeline/promotion.py` and require a bound clean verdict plus independent-review receipt.
2. Validate every proposed row recursively, prepare the SQLite intent, advance the existing promotion journal, write once under the canonical-store lock, validate committed bytes and derived outputs, then commit database state.
3. Reconcile every intermediate journal phase idempotently.
4. Exercise Wave 1 promotion only against scratch stores; canonical store and TM mutation remain fenced.

## Step 6 — import and shadow comparison

1. Add `src/pwg_pipeline/import_legacy.py` to import coordinator JSON, orchestrator SQLite, call ledgers, promotion journals, registry projections, PWG-TM checkpoints, cost ledgers, gates, promoted/quarantine artifacts, and refill receipts.
2. Key every import by source path plus content hash; a repeat is a no-op and a changed payload for the same identity is a refusal.
3. Add `shadow-sync` to compare Claude selection, attempts, calls, artifacts, audit state, requeues, and promotion deltas with zero execution or promotion authority.

## Step 7 — facade and compatibility shims

1. Add `src/pwg_pipeline/cli.py` with `init`, `import`, `plan`, `execute`, `audit`, `apply`, `review`, `promote`, `replay`, `shadow-sync`, and `canary` commands.
2. Convert `src/pwg_tm_generate.py` live paths into shims: `run/drain → execute`, `needed → plan`, `refill → apply --intent refill`, and `reconcile → audit`.
3. Convert `src/pwg_tm_w2_run.py` paid paths into shims: `--probe → canary --provider deepseek`; `--all` becomes an explicit plan/execute/audit sequence.
4. Preserve offline extraction helpers, emit a deprecation warning, propagate facade exit codes, and refuse old direct live/refill mutation.
5. Disable the old PWG-TM writer only after both provider canaries, production-equivalent replay, and two exact shim-parity runs pass.

## Step 8 — exact replay fixtures

1. Add `tests/fixtures/pwg_pipeline/clean_success/` for exact card/fragment completion and scratch promotion.
2. Add `tests/fixtures/pwg_pipeline/partial_requeue/` for mixed clean/null/defect results and identity-exact apply intents.
3. Add `tests/fixtures/pwg_pipeline/provider_timeout/` for a terminal reserved call with no retry or promotable artifact.
4. Add `tests/fixtures/pwg_pipeline/promotion_interrupt/` for recovery after store commit and before database commit.
5. Add `src/pwg_pipeline/replay.py` and compare selection, transitions, calls, verdicts, artifacts, requeues, hashes, and store deltas—not counts alone.

## Step 9 — fault-injection matrix

1. Add test-only named fault points after reservation, provider response, usage capture, artifact seal, verdict commit, apply-intent commit, store backup, store commit, derived-TM rebuild, journal advance, and before campaign commit.
2. At every point terminate the subprocess, reopen state, reconcile, and prove at most one reservation, no lost response, no duplicate artifact or row, no unjournaled mutation, stable repeated recovery, and exact scratch bytes.

## Step 10 — bounded non-promotable canary

1. Extend `.env.example` with empty `XAI_API_KEY=` and `DEEPSEEK_API_KEY=` placeholders plus provider-console source hints; credentials never enter Git or chat.
2. Create one synthetic request shared by both providers in a `promotable=false` scratch-only campaign.
3. Allow exactly one xAI request and one DeepSeek request, two calls total, USD 4 total, with hard timeouts and bounded output.
4. Permit no retries, rerolls, fallback, promotion, or canonical-path access.
5. Treat missing/evasive usage, ambiguous charge, route mismatch, malformed output, or budget breach as NO-GO.

## Step 11 — independent review and cutover

1. Add `src/pwg_pipeline/review.py` to seal the schema/transition summary, replay diffs, fault matrix, recursive-validation report, canary envelopes/accounting, shim parity, writer-disable diff, and rollback procedure.
2. Require a reviewer other than the implementation agent to sign a hash-bound receipt covering money, canonical paths, journal recovery, and rollback.
3. Add the complete offline gate to `.github/workflows/ci.yml`.
4. Cut over only when every test, replay, fault recovery, recursive validation, shadow comparison, canary, receipt, and rollback rehearsal is green.

## Planned verification commands

```powershell
Set-Location RussianTranslation
python -m pytest tests/test_pwg_pipeline_model.py tests/test_pwg_pipeline_repository.py tests/test_pwg_pipeline_validation.py tests/test_pwg_pipeline_replay.py tests/test_pwg_pipeline_faults.py tests/test_pwg_pipeline_compat.py tests/test_pwg_pipeline_canary.py -q
python -m pwg_pipeline.cli replay --matrix tests/fixtures/pwg_pipeline --exact
python -m pwg_pipeline.cli validate --recursive --fence-existing
python -m pwg_pipeline.cli shadow-sync --route claude-headless --compare-only
python -m pwg_pipeline.cli review verify
```

## Wave-1 stop conditions

1. Halt the full wave on accounting uncertainty, returned-route mismatch, secret exposure, canonical-integrity failure, or non-idempotent recovery.
2. Park irreversible ambiguity; log and default only when the choice is reversible.
3. Do not modify canonical PWG cards, canonical TM, prompts, translation policy, publication outputs, credentials, PWG source repositories, or proven Claude compiler/worker/gate behavior.

_Dr. Mārcis Gasūns_
