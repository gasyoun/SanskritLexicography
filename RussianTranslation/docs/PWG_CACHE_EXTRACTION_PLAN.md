# PWG cache contract — extraction backlog (paper only)

_Created: 14-08-2026 · Last updated: 14-08-2026_

Wave-1 ruling 29: author the provider-neutral contract and this extraction plan; do **not** port siblings or extract a package. This file is the backlog, not a license to edit other repositories.

Plan index: [PWG cache economy](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CACHE_ECONOMY_2026Q3.md). Operating contract: [PWG_CACHE_CONTRACT_PROVIDER_NEUTRAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PWG_CACHE_CONTRACT_PROVIDER_NEUTRAL.md).

## Compatibility (what a future shared package would have to keep)

| Surface | PWG-local module | Must stay byte-stable |
|---|---|---|
| Request identity | [`cache_identity.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_identity.py) | UTF-8, no BOM, LF, sorted keys; path/run/secret exclusion |
| Compiler v0 | [`prompt_compiler.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_compiler.py) | Reconstructs Claude `prompt_blocks`, DeepSeek `SYSTEM_TMPL`, Flash PREP `flash_messages` |
| Ledger | [`cache_event_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_event_ledger.py) | Sealed manifest + append-only JSONL + torn fail-closed |
| Reuse | [`cache_reuse.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_reuse.py) | Whole-card → fragment → evidence → provider cache → generation; experimental TM under `run_dir/tm/` only |
| Scheduler | [`cache_scheduler.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_scheduler.py) | Prefix-group contiguous; cold before warm; resume keeps labels |
| Billing | [`deepseek_arm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/deepseek_arm.py) | Missing/all-zero usage is unevaluable; `refuse_if_peak()` |

A sibling (kosha, SamudraManthanam, Systema) may consume these schemas after an ADOPT verdict. Until then the PWG tree is the only implementation.

## Extraction backlog (do not start)

1. Lift `cache_identity` + the four JSON schemas into a versioned package **after** ADOPT.
2. Keep provider adapters in the owning repo; the package emits hashes and envelopes only.
3. Do not vendor TM stores. The package takes paths; it never opens a canonical sidecar.
4. Port `refuse_if_peak` as a policy hook, not a DeepSeek hard-code, when a second paid provider exists.
5. Re-run both PWG lanes against the extracted package with a golden-diff of request ids before any other repo imports it.

H2704's ADOPT/NO-GO decides whether item 1 is eligible. A NO-GO leaves this backlog parked and keeps the PWG-local modules as instrumentation.

_Dr. Mārcis Gasūns_
