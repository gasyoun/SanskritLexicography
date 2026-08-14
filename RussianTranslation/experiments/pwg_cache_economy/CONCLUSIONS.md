# PWG cache-economy conclusions (H2703 + H2704)

_Created: 14-08-2026 · Last updated: 14-08-2026_

Sealed numbers. Adoption **NO-GO** still stands as a *product* verdict (do not flip `DEFAULT_MODEL`, do not promote a local cache). The 20% dual-lane bar is **not** a licence to treat the Flash 3.9% as zero.

Sources: [H2704 REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/REPORT.md) · [H2703 REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/REPORT.md) · [ADOPTION.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/ADOPTION.json) · [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/VERDICT_RULE.md). Residual: [H2754 (Grok 4.6) — Flash PREP one-shot vs incremental warm (correct denominator)](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2754-Grok_SanskritLexicography_pwg-cache-flash-oneshot-vs-warm_14.08.26.md).

## What was measured

| Quantity | Value | Meaning |
|---|---|---|
| First-200 TM yield | **0 / 0 / 0 / 200** | whole-card / fragment / PREP evidence / miss. Local TM did not fire. |
| Flash PREP parseable | **100/100** | reliability PASS |
| Flash PREP spend | **$0.041929** | 50 pairs, 100 slots, `deepseek-v4-flash` |
| Flash cold | $0.022056 · mean **$0.000441** · cache-hit tokens **87** | first-touch of the pair |
| Flash warm | $0.019872 · mean **$0.000397** · cache-hit tokens **445** | byte-identical second call |
| Warm − cold | −$0.0000437 · 95% CI **[−$0.000134, +$0.000040]** | interval **includes zero** |
| Generation parseable | **42/44** (95.5%) | reliability PASS |
| Generation spend | **$0.555956** | 22 pairs, `deepseek-v4-pro` |
| Generation unique `det_clean` | **20** | H2676 had 21 |
| L3 | **192/200** parseable, **$0.046207** | reliability scale-out, not a baseline |
| Canonical hashes | unchanged | no store/TM promotion |

## Three denominators (do not mix them)

The 20% floor is **USD per unique mechanically clean artifact versus the one-shot baseline**, and **both** lanes had to clear it ([VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/VERDICT_RULE.md)).

| Denominator | Flash PREP | Generation Pro | What it answers |
|---|---:|---:|---|
| **A. Pair cost / unique cards** (H2704 adoption arithmetic) | $0.041929 / 50 = **$0.000839** vs H2675 **$0.000873** → **−3.9%** | $0.555956 / 20 = **$0.02780** vs H2676 **$0.01991** → **+39.6%** | “If we *always* buy a cold+warm pair per card, are we 20% cheaper than one-shot?” |
| **B. Same-card incremental save** (cold − warm) / cold | **9.9%** ($0.0000437 / $0.000441) | noisy; generation “cold” already had **~13.6k** cache-hit tokens | “Does a *repeat* of the same request cost less?” |
| **C. One-shot production cost** (cold only / unique parseable) | **$0.000441**/card | **$0.01367** mean cold | “What does a *new* card cost if we ship the first parseable?” |

**A is the wrong unit for a production drain.** A drain pays one successful PREP (or one successful generation) per card. Charging the card for a deliberate second call, then asking that pair to beat a one-shot baseline by 20%, is a denominator artifact: it can hide a real Flash save and it almost automatically makes Pro look worse.

**ADOPTION.json used a fourth, worse PREP denominator:** `unique_clean: 1` (generation-style `det_clean` fired on 1/100 slots) so `usd_per_unique_clean` became **$0.041929** and `vs_baseline` **48×**. That number must not be quoted. PREP acceptance in the report is parseable + fence, 50/50 cards, **$0.000839**.

## Why the 3.9% is not “ignore”

- It is a **real point-estimate** against the sealed H2675 one-shot ($0.000873 → $0.000839).
- Same-card warm is cheaper still (**9.9%**), and cache-hit tokens rose **87 → 445**.
- Reliability on Flash is already at the ceiling (100/100).
- The CI on the paired dollar delta **includes zero**, so 3.9% / 9.9% are not yet distinguishable from noise at n=50. That is **INCONCLUSIVE on magnitude**, not “no economy”.
- The 20% bar + AND-both-lanes rule discarded this number because Pro failed. A Pro failure is not evidence about Flash.

## Why Pro +39.6% is too much (and partly accounting)

Agree: do **not** adopt a Pro pair-cache as the generation path.

- The pair design **buys two Pro generations per card**, then divides by unique `det_clean`. Versus H2676’s one-shot $0.01991 that is almost guaranteed to lose.
- Generation “cold” was **not** an empty prefix: mean cache-hit tokens on the first slot were already **13,585**. The pair never measured a true first-touch Pro cost.
- Unique clean dropped 21 → 20. Reliability passed (42/44); economy did not.

Keep Pro as a one-shot rematch tool (H2676). Do not rerun Pro pairs to “fix” the +39.6%.

## Product conclusions (locked)

1. **Do not flip `DEFAULT_MODEL`.** Flash stays the default.
2. **Do not promote** experimental TM or a PWG-local compiler/scheduler from this wave. Canonical hashes stay as frozen.
3. **Keep the instrumentation** (request identity, ledger, provider-neutral contract, extraction plan on paper).
4. **Do not treat NO-GO as “Flash cache is worthless.”** Record the 3.9% / 9.9% and re-test Flash under denominator B/C.
5. **Do not AND Flash to Pro** on the next sitting. Flash-only GO/NO-GO/INCONCLUSIVE.
6. **Local TM is not the lever here.** 0/200 exact yield on the first-200 drain-head.

## What H2754 must test

Shipped as [H2756](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2756_flash/REPORT.md) (H2754 locked by precheck exit 4 on [#1713](https://github.com/gasyoun/SanskritLexicography/pull/1713)).

Primary question: on a **fresh** Flash PREP miss set (not the H2704 50 — those prefixes may already be warm), is the **same-card incremental save** (denominator B) positive with a CI that excludes zero?

**Answer (14-08-2026):** **INCONCLUSIVE.** 99/100 parseable, $0.038405, hashes unchanged. Ratio-of-means save **0.2%**, bootstrap 95% CI includes 0. Keep the point estimate. Do not write “no economy”. Product NO-GO unchanged.

- Control = first-touch USD per unique parseable card (denominator C).
- Treatment = byte-identical repeat USD.
- Never score (cold+warm) / unique cards as the adoption metric.
- Informational only: amortized cost after R = 2, 5, 10 repeats.
- Pro is out of scope.

_Dr. Mārcis Gasūns_
