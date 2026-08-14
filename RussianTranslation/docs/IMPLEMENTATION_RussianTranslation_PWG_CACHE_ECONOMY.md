# Implementation — PWG prompt-cache economy

_Created: 13-08-2026 · Last updated: 14-08-2026_

Plan index: [PWG cache economy](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CACHE_ECONOMY_2026Q3.md).

## Outcome and fences

Wave 1 makes PWG generation and Flash PREP/TM retrieval measurable under one cache/economy contract. It may write only to an experimental TM namespace inside the sealed run directory. It does not change `DEFAULT_MODEL`, canonical store/TM, promotion allowlists, or sibling repositories; every generated artifact is `promotable: false`.

H2702 (14-08-2026) landed steps 0–2 and 4–6 offline: baseline hashes, schemas, compiler/identity, converter, ledger, reuse, scheduler. Steps 3 and 8 (paid transport/canary/Q3/PREP) already shipped as H2674–H2676 and must not be rerun. H2703 owns the generation half of step 8 L2 (exact-request Pro cold/warm) plus the generation-lane report. H2704 owns PREP/TM L2, bounded L3, and adoption (census 0/200 TM hits; Flash 50-pair runner; extraction plan on paper).

## Ordered build

### 0. Freeze baselines

In the isolated worktree, record the source commit and SHA-256 values for the frozen 22-key Q3 sample, slice/manifest, prompt bytes, output schema, relevant canonical TM/denylist files, PREP schema, and deterministic audit outputs. Store only hashes and publishable metadata under `experiments/pwg_cache_economy/baseline/manifest.json`.

Run existing selftests for `deepseek_arm`, `det_gate`, `headless_worker`, `translation_memory`, and `prep_pack`. Stop if the baseline is not green.

### 1. Add provider-neutral contracts

Add:

- `schemas/pwg_prompt_bundle.schema.json`
- `schemas/pwg_cache_event.schema.json`
- `schemas/pwg_cache_run_manifest.schema.json`
- `src/pilot/cache_identity.py`
- `src/pilot/prompt_compiler.py`
- focused identity/compiler tests

The compiler emits provider/model, compiler and schema versions, stable prefix and volatile tail bytes/hashes, output-schema and dependency hashes, generation parameters, token estimate, request hash, lineage, and `promotable: false`. Canonical JSON is UTF-8 without BOM, LF, sorted keys. Secrets, timestamps, paths, retry ordinal, and connection/run identity do not affect request identity.

Acceptance: base `v0` reconstructs legacy prompts byte-for-byte; every answer-affecting input is hashed; Windows path representation does not change identity.

### 2. Add reversible v2 migration

Add `src/pilot/cache_migrate.py`, fixtures, and tests; version the active H1210/PREP/transport schemas. Commands:

```powershell
python src/pilot/cache_migrate.py check --input <legacy.json>
python src/pilot/cache_migrate.py convert --input <legacy.json> --output <v2.json>
python src/pilot/cache_migrate.py verify --legacy <legacy.json> --converted <v2.json>
```

Never edit a legacy artifact in place. Record source hash and converter version; preserve unknown fields under compatibility metadata; require `migration_lossy: false`; refuse ambiguity; make conversion idempotent. Legacy and v2 modes remain side by side and rollback selects the legacy adapter.

### 3. Replace DeepSeek transport first

Add `src/pilot/h1210/deepseek_transport.py` with focused streamed-response tests; modify `deepseek_arm.py` and the common transport seam. Use a pinned OpenAI-compatible streaming client and one persistent pool per process. Accumulate content/reasoning deltas to a terminal frame and record final usage, requested/served model, finish reason, provider IDs, latency, termination class, and cache-hit/miss tokens.

Requirements: bounded connect/read/overall deadlines; exact sealed transport retry only; missing usage is unevaluable, never zero; model mismatch is terminal; partial streams never parse or enter TM; `refuse_if_peak()` runs before dispatch and before a retry that crosses a billing boundary. The failed `urllib` Pro/high route is retired.

### 4. Add sealed runs and append-only events

Add `src/pilot/cache_event_ledger.py` and tests; wire DeepSeek generation and PREP. Each run contains:

```text
run.manifest.json
events.jsonl
requests/<request_sha256>.json
responses/<request_sha256>.<attempt>.json
summary.json
tm/                                  # experimental only
```

The manifest seals source/cohort/pricing hashes, N, call/cost ceilings, schedule, model, retry ladder, acceptance rules, and namespaces before token 1. Events cover compile, TM short-circuit, seal, dispatch, retry, terminal response, parse, deterministic gate, repair, park, stop, and completion. Use a serialized writer and `fsync` terminal events. Summaries derive from sealed inputs and events.

Acceptance: simulated process death resumes completed requests without duplicate billing; torn/interleaved ledgers fail closed.

### 5. Wire hierarchical reuse and experimental TM

Add `src/pilot/cache_reuse.py`; wrap existing `translation_memory.py`, PREP, and DeepSeek paths. Resolution order is exact whole-card TM, complete exact fragment TM, deterministic canonical/experimental evidence retrieval, provider cache, then generation. Fuzzy matches remain advisory.

Experimental rows live under the run directory, carry request/dependency/gate provenance, and may contain only gate-clean non-promotable candidates. They never silently shadow a canonical conflict. Tests hash canonical TM/store before and after every lane and assert equality.

### 6. Schedule exact prefix groups

Add `src/pilot/cache_scheduler.py`; group by provider, requested model, and prefix-group ID. Keep groups contiguous and preserve original ordinal within a group. The first real request is the cold member—do not buy a warm-up. Record cold/warm position and preserve it on resume. Verify deterministic ordering under shuffled input and different worker counts.

### 7. Seal the overrun ladder

Predeclare:

1. `v0` base request;
2. `v1-compact` concise schema-preserving output;
3. `v2-cap` bounded output increase named in the manifest;
4. `v3-partition` deterministic card/fragment partition followed by existing reglue and full audit.

Transport retries retain request identity. Any prompt, cap, schema, evidence, or partition change creates a child identity with parent and reason. Exhaustion parks the item. Q4/monster classification stops before unattended partition execution.

### 8. Run the paid ladder

Each stage has a new sealed run folder and declared N before token 1:

- **L0:** three frozen Pro/high streaming canaries; require 3/3 parseable, matching served model, evaluable usage, no unclassified failure.
- **L1:** frozen 22-key Q3 rematch; require ≥21/22 parseable, ≥15/22 deterministic-clean, exact model, evaluable billing, no canonical writes.
- **L2:** generation and Flash PREP/TM exact-prefix cold/warm comparisons under identical content, caps, gates, concurrency, and sample.
- **L3:** larger bounded non-Q4/non-monster cohort only if L0–L2 pass; predeclare strata, N, USD/call ceilings, and blinded sample.

After 16-08-2026 16:00 UTC, dispatch only in the standing off-peak windows. Any immediate stop condition in the PLAN ends paid execution before the next request.

### 9. Report and extract the contract on paper

Add `src/pilot/cache_economy_report.py`, tests, an experiment README, `docs/PWG_CACHE_CONTRACT_PROVIDER_NEUTRAL.md`, and `docs/PWG_CACHE_EXTRACTION_PLAN.md`. Report total attributable USD per mechanical-clean and accepted artifact, parseable rate, hit/miss tokens, cold/warm delta, retry amplification, zero-call TM yield, major-error rate, and confidence intervals.

Adopt only if both generation and PREP/TM show ≥20% lower cost per clean artifact, ≥95% reliability, deterministic non-regression, and no meaningful blinded major-error increase. Otherwise keep the instrumentation and migration seam, record NO-GO, and retain the existing default.

## Verification commands

```powershell
python -m pytest <new focused cache/transport/migration tests>
python src/pilot/h1210/det_gate.py --selftest
python src/pilot/h1210/prep_pack.py --selftest
python src/pilot/translation_memory.py selftest
python src/pilot/headless_worker_selftest.py
python src/pilot/window_selftest.py
python src/pilot/lang_parity_check.py
python src/pilot/h1209/canonical_audit.py <result> <manifest> --out <audit>
python src/pilot/cache_economy_report.py --manifest <run.manifest.json> --ledger <events.jsonl> --out <summary.json>
git diff --check
```

Before concluding, rehash canonical store/TM files and prove byte equality with step 0.

_Dr. Mārcis Gasūns_
