# PWG cache contract — provider-neutral identity, migration, ledger

_Created: 14-08-2026 · Last updated: 14-08-2026_

Operating contract for [H2702 (Grok 4.6) — PWG cache economy residual A: provider-neutral contracts, identity, migration, and ledger](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2702-Grok_SanskritLexicography_pwg-cache-economy-contract-foundation_14.08.26.md). Paid generation proof is [H2703 (Grok 4.6) — PWG cache economy residual B: exact-request generation cold/warm proof](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2703-Grok_SanskritLexicography_pwg-cache-economy-generation-cold-warm_14.08.26.md). PREP/TM census, Flash pairs, conditional L3, and the ADOPT/NO-GO decision are [H2704 (Grok 4.6) — PWG cache economy residual C: PREP/TM proof, bounded L3, and adoption verdict](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2704-Grok_SanskritLexicography_pwg-cache-economy-prep-tm-adoption-verdict_14.08.26.md). Extraction stays on paper: [PWG_CACHE_EXTRACTION_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PWG_CACHE_EXTRACTION_PLAN.md).

Plan index: [PWG cache economy](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CACHE_ECONOMY_2026Q3.md).

## What this layer is

One request is identified by the SHA-256 of a canonical JSON object (UTF-8, no BOM, LF, sorted keys) over the answer-affecting fields only:

- provider and requested model
- generation parameters
- compiler version and response-schema hash
- stable-prefix hash and volatile-tail hash
- source-card / source-fragment hashes
- TM, denylist, retrieved-evidence, grammar, NWS, PREP, and other dependency hashes
- parent request id and repair-variant code

Timestamps, secrets, filesystem paths, run ids, connection ids, and retry ordinals are excluded. A Windows path cannot change the identity.

The compiler wraps the existing Claude (`headless_worker.prompt_blocks`), DeepSeek generation (`deepseek_arm.SYSTEM_TMPL` + `prep_slice`), and Flash PREP (`prep_pack.flash_messages`) builders. v0 reconstructs those payload bytes. Adapters may add transport headers; they may not reinterpret content.

## Modules

| Module | Role |
|---|---|
| [cache_identity.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_identity.py) | Canonical JSON, request id, exclusion list |
| [prompt_compiler.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_compiler.py) | v0 Claude / DeepSeek compile + golden reconstruction |
| [cache_migrate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_migrate.py) | `check` / `convert` / `verify`; refuse ambiguity; never in-place |
| [cache_event_ledger.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_event_ledger.py) | Sealed run manifest, append-only JSONL, crash/resume, torn fail-closed |
| [cache_reuse.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_reuse.py) | Whole-card TM → fragment TM → evidence → provider cache → generation |
| [cache_scheduler.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_scheduler.py) | Exact prefix-group order; cold first; resume keeps cold/warm |
| [cache_baseline_freeze.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_baseline_freeze.py) | Source commit + dependency hashes |

Schemas: [pwg_cache_request.schema.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_cache_request.schema.json), [pwg_cache_event.schema.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_cache_event.schema.json), [pwg_cache_run_manifest.schema.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_cache_run_manifest.schema.json), [pwg_prompt_bundle.schema.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_prompt_bundle.schema.json).

## Fences

- Experimental TM is only `run_dir/tm/`. It cannot resolve to a canonical path and cannot promote.
- Missing usage is `null` plus a reason. All-zero usage is unevaluable, never a free call.
- Legacy and v1 stay side by side. Rollback selects the legacy adapter and leaves v1 evidence.
- No paid/provider call lives in this layer.

## Offline proof

```text
python src/pilot/cache_contract_selftest.py
python -m pytest tests/test_pwg_cache_economy.py
python src/pilot/cache_migrate.py check --input src/pilot/fixtures/pwg_cache_economy/legacy_claude_prompt.json
```

Baseline: [experiments/pwg_cache_economy/baseline/manifest.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/baseline/manifest.json).

_Dr. Mārcis Gasūns_
