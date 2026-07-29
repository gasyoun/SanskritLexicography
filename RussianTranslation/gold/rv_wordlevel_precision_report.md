# Layer-B word-level precision report (H1844 step 11, W1.9 / R14)

_Created: 29-07-2026 · Last updated: 29-07-2026_

Bar: **precision ≥ 85 % per target language** on a frequency-stratified token sample (R14). Scored over the adjudicated rows of [`gold/rv_wordlevel_gold.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/rv_wordlevel_gold.jsonl).

| Target language | n | Correct | Precision | Verdict |
|---|--:|--:|--:|---|
| de | 24 | 7 | 29.2 % | **FAIL** |
| ru | 26 | 5 | 19.2 % | **FAIL** |
| en | 19 | 2 | 10.5 % | **FAIL** |

| Frequency stratum | n | Precision |
|---|--:|--:|
| hapax | 20 | 15.0 % |
| rare | 17 | 11.8 % |
| mid | 17 | 23.5 % |
| frequent | 15 | 33.3 % |

| Confidence signal | n | Precision |
|---|--:|--:|
| mutual-argmax confirmed | 18 | 50.0 % |
| flagged `low_confidence` | 51 | 9.8 % |

## Verdict

**All three languages fall below the 85 % bar — stop condition 3.** Per PLAN §4 the response is fixed in advance and is not a judgment call made after seeing the number: ship spine A alone, mark layer B `low_confidence`, exclude it from the contradiction gate, and report. The 0.20 confidence gate is NOT re-tuned to rescue the number — that is the blind tuning R14 and risk K2 exist to forbid.

_Dr. Mārcis Gasūns_
