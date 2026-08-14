# H2704 — first-200 TM/retrieval zero-call census

_Created: 14-08-2026 · Last updated: 14-08-2026_

Frozen H2675 first-200 population. No provider calls. H2675 live sidecars are excluded from the evidence tier (they are paid PREP outputs, not independent retrieval).

| Tier | Count | Calls |
|---|---:|---:|
| Exact whole-card TM | 0 | 0 |
| Complete exact fragment TM | 0 | 0 |
| Deterministic committed PREP evidence | 0 | 0 |
| Miss | 200 | 1 (would-be) |
| Fuzzy TM | advisory only | — |

Raw address was `assembled_skeleton` SHA-256 for every key (production `pilot/input` raws are absent for this drain-head). Fragment planner therefore saw one whole-card chunk per key. Canonical TM lookup used `translation_memory.lookup('ru', raw_sha256)` and complete fragment coverage; neither hit.

50 PREP pairs were then selected from the 200 misses by salt `h2704-prep-50-v1` after size×polysemy stratification. L3 100-card non-monster cohort sealed separately (`h2704-l3-100-v1`) and is not dispatched unless both lanes PASS.

Artifacts: [census.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/census.json), [prep50.manifest.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/prep50.manifest.json), [l3.manifest.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/l3.manifest.json).

_Dr. Mārcis Gasūns_
