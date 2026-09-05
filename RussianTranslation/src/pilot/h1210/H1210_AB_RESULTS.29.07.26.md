_Created: 01-08-2026 · Last updated: 05-09-2026_

| metric | arm A — Claude-native | arm B — DeepSeek + same controller |
|---|---|---|
| generator model | workers claude-sonnet-5 / controller claude-opus-4-8 | deepseek-chat |
| cards attempted | 87 | 100 |
| **audit-clean % (canonical promote-DRY)** | **95.40% (83/87)**  | **78.00% (78/100)** |
| rig self-report clean (vs audit) | 70 (-13) | 72 (-6) |
| generation calls | 152 | 149 |
| controller calls | 94 | 50 |
| calls / clean card | 2.96 | 2.55 |
| controller share of calls | 38.20% | 25.10% |
| retries (rate/card) | 65 (0.75) | 69 (0.69) |
| escalated to review-sheet | 12 (13.80%) | 15 (15.00%) |
| complexity-trigger false-flag rate | 77.80% (35/45) | 63.20% (36/57) |
| USD total | — | 0.73 |
| **USD / clean card** | **—** | **0.01** |
| wall clock (s) | 9625.20 | 1254.60 |

| defect class (canonical audit) | arm A | arm B |
|---|---:|---:|
| NULL-CARD | 0 | 9 |
| fidelity-reject | 2 | 12 |
| soft:tnmask-mismatch | 2 | 11 |
| translation-fidelity-reject | 4 | 13 |

_Dr. Mārcis Gasūns_
