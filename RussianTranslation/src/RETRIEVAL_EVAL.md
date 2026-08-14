# RETRIEVAL_EVAL — H2686 live no-TM vs graded-fragment-TM

_Created: 22-07-2026 · Last updated: 14-08-2026_

Harness: [`tm_retrieval_eval.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_retrieval_eval.py) (Grok 4.6, `grok-4.6`). Engine **deepseek** / model **deepseek-v4-flash**. Frozen batch sha256 `b7ed1b7d134157ef2ecc59d601756110584f0139bb088dd0b5c8c7c462faff6f`. Gold sha256 `72c282933c395702324db1072dcfe49cae1feac3bb8db50e9737f7b75ecb6ed7`.

Wave 1 is immutable. This measurement does not rewrite promoted or quarantined Wave-1 fragments.

## Status: LIVE

| Arm | n | mean quality | serious error | mean edit | tokens | wall s | cost USD | exact reuse | fragment reuse |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| no-TM | 9 | 0.590 | 6/9 (66.7%) | 0.609 | 5167 | 92.15 | 0.001089 | 0 | 0 |
| fragment-TM | 9 | 0.800 | 5/9 (55.6%) | 0.471 | 11102 | 76.11 | 0.001856 | 2 | 9 |

Deltas (TM − no-TM): quality **+0.210**, edit **-0.138**, serious-error rate **-0.111**, tokens **+5935**, wall **-16.04 s**, cost **+0.000767 USD**.

## Per fragment class (TM arm)

| Class | n | mean quality | mean edit | serious error |
|---|---:|---:|---:|---:|
| definition_gloss | 3 | 0.500 | 0.413 | 2 |
| recurring_formula | 3 | 1.000 | 0.000 | 0 |
| sense | 3 | nan | 1.000 | 3 |

## Route / cost provenance

- Translate+judge route: `https://api.deepseek.com/chat/completions`
- Requested model: `deepseek-v4-flash`
- Price card: `pre-1608`
- Ledger calls: **36** (translate + judge, both arms)
- Total cost USD: **0.004138**
- Mock: **False**

_Dr. Mārcis Gasūns_
