# Birthday-paradox collision baselines for MW headwords (SanskritLexicography, 26-09-2026)

_Context: MG asked how the birthday paradox (35 people → 81,4% shared birthday) relates to
our data, Cologne / Sanskrit generally and phonetics/combinations specifically, for k=10 cases._

Measured from `csl-orig/v02/mw/mw.txt`, `<k1>` SLP1 keys, **194 083 unique headwords**.
Collision probability for k=10 cases: `P ≈ 1 − exp(−45·H)`, H = Herfindahl index Σpᵢ²
of the actual distribution (NOT uniform 1/n — Sanskrit is heavily skewed).

| Field (k=10 cases) | Categories | m_eff = 1/H | P(any 2 collide) |
|---|---|---|---|
| Exact lemma | 194 083 | ~194k | ~0% (sampled without replacement) |
| First 3 letters | 5 566 | 304 | 13,7% |
| Onset cluster (initial vowels + first consonant run) | 3 115 | 81 | 42,6% |
| First 2 letters | 680 | 71 | 46,8% |
| Final 2 letters | 709 | 31 | 77,1% |
| First letter | 47 | 15 | 95,1% |
| Final letter | 50 | **2,6** | **~100%** |

## Takeaways

1. Sanskrit phonetic space is extremely narrow at the edges: finals collapse to
   m_eff ≈ 2,6 (dominance of `-a`), onsets to m_eff ≈ 15–80. Two of ten random entries
   sharing a first/last letter is the **background norm**, not a signal.
2. Significance threshold for k=10: a collision is surprising (<5%) only for fields with
   m_eff ≳ 900 — in MW that means first-3-letters-or-longer / whole lemma.
3. Correction-queue implication: a cluster of 2–3 corrections sharing onset/final must be
   tested against these baselines before calling it a systematic defect; eyeballed
   phonetic clusters in ≤10 cases are expected noise.

Method repro: parse `<k1>([^<]+)` from mw.txt, unique keys, per-field Counter → Σpᵢ²,
P = 1 − exp(−C(10,2)·H). Screen session 26-09-2026, oxalpha (GLM).

_Гасунс_
