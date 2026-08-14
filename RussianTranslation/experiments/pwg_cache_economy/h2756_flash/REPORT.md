# H2756 — Flash PREP one-shot vs incremental warm

_Created: 14-08-2026 · Last updated: 14-08-2026_

**Flash-only verdict: INCONCLUSIVE.** Residual of [H2754 (Grok 4.6) — Flash PREP one-shot vs incremental warm (correct denominator)](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2754-Grok_SanskritLexicography_pwg-cache-flash-oneshot-vs-warm_14.08.26.md), which is locked by precheck exit 4 on [SanskritLexicography#1713](https://github.com/gasyoun/SanskritLexicography/pull/1713). Product adoption from H2704 stays **NO-GO**. `DEFAULT_MODEL` is not flipped. Canonical hashes unchanged.

Rule: [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2756_flash/VERDICT_RULE.md). Spend: [SPEND_AUTH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2756_flash/SPEND_AUTH.md). Summary: [h2756/run/summary.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2756_flash/h2756/run/summary.json).

## Reliability

| Gate | Sealed | Measured | Hold |
|---|---|---|:---:|
| Pairs | 50 fresh first-200 misses, disjoint from H2704 | 50 | yes |
| Parseable | ≥95/100 | 99/100 | yes |
| Served model | deepseek-v4-flash | 99/99 parseable slots; `iz` cold empty transport | yes |
| Cost-evaluable | every parseable slot | 99/99 | yes |
| Retry amplification | 1.0 | 1.0 | yes |
| Canonical hashes | equal freeze | True | yes |
| Promotable | false | false | yes |

Stop reason: `None`. Lane: PASS. Verdict reasons: CI includes 0. One cold slot (`iz`) returned empty transport (unparseable, not billed); its warm sibling is excluded from denominator B (n=49 complete pairs).

## Three denominators

| Denominator | Value | Role |
|---|---|---|
| **A. Pair cost / unique cards** | $0.000784 vs H2675 $0.000873 → -10.2% | *not scored* (H2704-comparable) |
| **B. Same-card incremental save** (cold − warm) / cold | **0.2%** bootstrap 95% CI [-40.0%, 23.8%] n=49 | **primary** |
| **C. One-shot cold / parseable card** | $0.000380 vs H2675 $0.000873 → -56.5% | historical context |

Paired dollar delta (cold − warm): mean $0.000001 bootstrap 95% CI [$-0.000113, $0.000117].

## Cold / warm arms

| Arm | n | total USD | mean USD | median USD | mean cache-hit tokens |
|---|---:|---:|---:|---:|---:|
| cold | 49 | 0.018611 | 0.00037981714285714285 | 0.00016766 | 128.0 |
| warm | 50 | 0.019793 | 0.00039586959999999996 | 0.0002235 | 412.16 |

Total attributable USD **$0.038405**. Amortized mean USD after R repeats: R=2 $0.000379, R=5 $0.000379, R=10 $0.000379.

## Blinded pair classes

| Class | n |
|---|---:|
| disagree | 2 |
| equivalent_structure | 6 |
| identical | 41 |
| none | 1 |

## Verdict

**INCONCLUSIVE** on denominator B. Point save is positive but the CI includes zero. Keep the point estimate. This is not “no economy”.

This is a **USD** result on a **repeat of the same PREP request**, not a wall-clock result for the drain. A production drain pays one PREP per new card (about $0.0004) and, when needed, a generation pass (about $0.02). Even a real 10% PREP-repeat save would be a few tenths of a percent of a full translation. The 0.2% here will not make the PWG→RU drain feel faster. Plain-language write-up: [CONCLUSIONS.md — What this means for a production drain](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/CONCLUSIONS.md).

H2704 product NO-GO is unchanged. Pro was not run.

_Dr. Mārcis Gasūns_
