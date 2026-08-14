# H2756 Flash-only verdict rule

_Created: 14-08-2026 · Last updated: 14-08-2026_

Primary metric (denominator **B**): paired `(mean cold USD − mean warm USD) / mean cold USD` on complete parseable + cost-evaluable pairs. This is the H2704 CONCLUSIONS 9.9% construction (ratio of means). The mean of per-pair ratios is not scored: small-cold / noisy-warm pairs explode it. Interval is a 2000-draw bootstrap 95% CI of that ratio-of-means, seed `2756`.

| Verdict | When |
|---|---|
| **GO** | parseable ≥ 95/100, every parseable slot evaluable, retry amplification 1.0, hashes unchanged, point save > 0, CI excludes 0 |
| **INCONCLUSIVE** | reliability holds and point save > 0 but CI includes 0. Keep the point estimate. Do not write “no economy”. |
| **NO-GO** | point save ≤ 0, or parseability / billing / hash / served-model gate fails |

Denominator **A** `(cold+warm) / unique cards` may be printed as *not scored*. Denominator **C** (cold only vs H2675 $0.000873) is historical context, not a kill. Pro is out of scope. Never flip `DEFAULT_MODEL`. Never promote.

_Dr. Mārcis Gasūns_
