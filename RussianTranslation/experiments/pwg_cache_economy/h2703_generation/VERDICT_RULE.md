# H2703 generation-lane verdict rule (frozen before token 1)

_Created: 14-08-2026 · Last updated: 14-08-2026_

**Question.** On the exact frozen H2676 22-card Q3 population, do 22 contiguous exact-request DeepSeek V4 Pro cold/warm pairs produce attributable provider-cache economics with reliable parseable terminals? This is **not** the H2704 adoption verdict.

**Population.** The 22 keys in [H2676 sample_keys.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/sample_keys.json) `main_arm.keys`, payload order from [payload_key_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/payload_key_map.json). Do not rerun H2674, H2675, or H2676.

**Sealed request.** One `pwg.cache_request.v1` per card from `compile_deepseek_v0`. Model `deepseek-v4-pro`, `reasoning_effort=high`, `max_tokens=32768`, temperature 0.2, JSON object format. Cold and warm of a card are byte-identical. Controller-feedback, compact, cap, or partition changes are undeclared variants and stop the experiment.

**Budget.** N=22 pairs, `max_base_calls=44`. Each slot is reserved before dispatch. One HTTP attempt per slot so 22 pairs fit the ceiling. Exact sealed transport retries would count as billable attempts and are therefore not used here.

**Price fence.** Before 16-08-2026 16:00 UTC: authorized pre-1608 card. At or after that instant: `refuse_if_peak()` before every dispatch. Peak is never paid.

**Generation-lane PASS iff all of:**

1. 22 pairs attempted in sealed order (44 slots).
2. At least 42/44 parseable terminal responses (≥95%).
3. Every successful generation call served `deepseek-v4-pro`.
4. Every parseable call has evaluable usage and a Pro `price_card` cost (never a fake zero).
5. Canonical store/TM SHA-256 values equal the pre-token freeze.
6. No undeclared variant, no promotion, every candidate `promotable: false`.

Otherwise **FAIL**. Missing evidence is **INCONCLUSIVE**. A cache hit is explanatory, not an accepted artifact. H2704 owns adoption.

Stop before the next request on: parseability already unable to reach 42/44; served-model mismatch; missing/malformed usage on a returned body; unevaluable billing; canonical hash change; undeclared variant; call or cost ceiling (`$5`); repeated systemic failure; peak window after the switch.

_Dr. Mārcis Gasūns_
