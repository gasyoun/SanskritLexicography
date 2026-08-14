# H2704 — PREP/TM census, Flash pairs, L3, adoption

_Created: 14-08-2026 · Last updated: 14-08-2026_

**Adoption verdict: NO-GO.** PREP-lane **PASS**. Generation-lane **PASS** (H2703). Neither lane meets the 20% cost-per-clean bar. `DEFAULT_MODEL` and canonical TM/store stay unchanged.

Rule: [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/VERDICT_RULE.md). Spend: [SPEND_AUTH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/SPEND_AUTH.md). Census: [CENSUS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/CENSUS.md).

## Frozen before token 1

| Clause | Sealed value | Measured | Hold |
|---|---|---|:---:|
| First-200 TM census | 200 keys, zero calls | 0 / 0 / 0 / 200 (card / frag / evidence / miss) | yes |
| PREP pairs | 50 | 50 | yes |
| PREP parseable | ≥95/100 | 100/100 | yes |
| Served model | deepseek-v4-flash | all 100 slots | yes |
| Canonical hashes | equal freeze | True | yes |
| Promotable | false | false | yes |
| Cost / unique parseable card | vs H2675 $0.000873 | $0.000839 | no 20% |

Sealed source commit: `6874f4a98430530695ed0aba4a4c5d7f63d91b15`. Price card `pre-1608`. Cohort sha256 `5510c983f376a551eb50d6540fa8871653072e9b4e7c5757ab9cd1d81a0abaf0`.

## Zero-call TM yield

Exact whole-card TM, complete fragment TM, and committed PREP evidence were all **0/200**. Every first-200 key is a miss under content-addressed lookup on assembled-skeleton SHA-256 (production input raws absent for this drain-head). Fuzzy hits stay advisory.

## PREP Flash economy (50 pairs / 100 slots)

| Arm | n | total USD | mean USD | median USD | mean cache-hit tokens |
|---|---:|---:|---:|---:|---:|
| cold | 50 | 0.022056 | 0.000441 | 0.000223 | 87.04 |
| warm | 50 | 0.019872 | 0.000397 | 0.000247 | 445.44 |

Paired delta (warm − cold): n=50 mean=−$0.0000437 bootstrap 95% CI [−$0.000134, +$0.000040]. The interval **crosses zero**. Retry amplification **1.0**. Total attributable USD **$0.041929**. Cost per unique parseable card **$0.000839** (50/50 parseable cards), 3.9% below H2675's one-shot **$0.000873**, short of the 20% adoption floor. Generation-style `det_clean` fired on 1/100 slots; PREP acceptance is parseable + fence, not a final-card gate.

## Blinded 50-pair compare (30-pair sample is the first 30 by sealed hash order)

| Class | All 50 | First-30 sample |
|---|---:|---:|
| identical | 38 | 21 |
| equivalent_structure | 8 | 6 |
| disagree | 4 | 3 |

Disagreements are route_hint / ru_skeleton length, not a generation major-error class. No paid judge. Serious-error incidence on this PREP artifact is not comparable to H2676 card audit; the sample does not show a new systematic failure mode.

## Generation lane (H2703, inherited)

22/22 pairs, 42/44 parseable, unique det_clean 20, **$0.02780/clean** vs H2676 **$0.01991**. That is a cost *increase*. Generation therefore fails the 20% economy clause even though its reliability gate passed.

## L3

GO receipt: [L3_GO.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/L3_GO.md). 100/100 pairs attempted, **192/200 parseable (96%)**, unique det_clean 4, **$0.046207** (ceiling USD 25). Lane **PASS**. Canonical hashes equal. Eight transport-empty slots (`saMtrAsa` pair, `Ekya` pair, plus `brahmadatta`/`antarDAna`/`aditi`/`sikatA` one-sided) stayed under the 10-slot failure budget. L3 does not change the adoption arithmetic: it is a reliability scale-out, not a new baseline.

## Why NO-GO

Adoption requires **both** lanes ≥20% cheaper per clean artifact. Generation is more expensive per clean card because the pair design buys two Pro generations. PREP is only 3.9% cheaper per unique parseable card, and its warm-minus-cold CI includes zero. Instrumentation, the provider-neutral contract, and the paper-only extraction plan stay. The default Flash model is not flipped. Canonical hashes are unchanged.

## Addendum 14-08-2026 — 3.9% is economy, not noise-to-discard

The product NO-GO above is unchanged. The 3.9% Flash point-estimate is still a saving. Same-card (cold − warm) / cold is **9.9%**; the paired USD CI still includes zero, so magnitude is INCONCLUSIVE at n=50, not “zero economy”. `ADOPTION.json` `unique_clean: 1` / `$0.041929` per card is a PREP-denominator bug (generation-style `det_clean`); quote this report’s 50-card **$0.000839**, not that JSON field. Full tables and the residual design: [CONCLUSIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/CONCLUSIONS.md). Next sitting: [H2754 (Grok 4.6) — Flash PREP one-shot vs incremental warm (correct denominator)](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2754-Grok_SanskritLexicography_pwg-cache-flash-oneshot-vs-warm_14.08.26.md).

_Dr. Mārcis Gasūns_
