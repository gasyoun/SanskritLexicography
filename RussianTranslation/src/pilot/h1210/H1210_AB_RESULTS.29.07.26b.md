| metric | arm A — Claude-native | arm B — DeepSeek + same controller |
|---|---|---|
| generator model | 3 chunk(s)/13 cards measured: controllers claude-opus-5[1m] / workers claude-sonnet-5 | 7 chunk(s)/87 cards not recorded (pre-H1846 collection), documented as: workers claude-sonnet-5 / controller claude-opus-4-8 | deepseek-chat |
| cards attempted | 100 | 100 |
| **audit-clean % (canonical promote-DRY)** | **93.00% (93/100)**  | **78.00% (78/100)** |
| rig self-report clean (vs audit) | 72 (-21) | 72 (-6) |
| generation calls | 188 | 149 |
| controller calls | 104 | 50 |
| calls / clean card | 3.14 | 2.55 |
| controller share of calls | 35.60% | 25.10% |
| retries (rate/card) | 88 (0.88) | 69 (0.69) |
| escalated to review-sheet | 14 (14.00%) | 15 (15.00%) |
| complexity-trigger false-flag rate | 71.90% (41/57) | 63.20% (36/57) |
| USD total | — | 0.73 |
| **USD / clean card** | **—** | **0.01** |
| wall clock (s) | 17973.60 | 1254.60 |

| defect class (canonical audit) | arm A | arm B |
|---|---:|---:|
| NULL-CARD | 3 | 9 |
| fidelity-reject | 2 | 12 |
| soft:tnmask-mismatch | 2 | 11 |
| translation-fidelity-reject | 4 | 13 |
