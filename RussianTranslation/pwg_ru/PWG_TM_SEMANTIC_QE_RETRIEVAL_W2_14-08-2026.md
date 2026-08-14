# PWG TM — Track D semantic QE + live retrieval (H2686)

_Created: 14-08-2026 · Last updated: 14-08-2026_

Grok 4.6 (`grok-4.6`). Track D of [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pwg_tm_dh_lexicography.md). Wave 1 (H2684 / [PR #1695](https://github.com/gasyoun/SanskritLexicography/pull/1695)) is immutable.

## Status: MEASURED — genuine QE defensible; live two-arm ran

No mock numbers are reported as results. `selftest` mocks stay in the harness only.

## QE backend receipt

| Backend | Serves | Labelled as COMET? |
|---|---|---|
| `proxy` (surface heuristic) | yes | **no** — historical ρ=**-0.0351**, preliminary |
| `labse` (`sentence-transformers/LaBSE`) | **no** (WinError 1455 pagefile on load) | no |
| `comet` (`Unbabel/wmt22-cometkiwi-da`) | **no** (no cp314 wheel; gated HF not used as fallback) | n/a |
| `deepseek` (`deepseek-v4-flash` JSON judge) | **yes** after one repair | **no** |

Receipt: [src/QE_BACKEND_RECEIPT.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/QE_BACKEND_RECEIPT.json).

## Gold calibration

Deterministic A/B/C round-robin slice **n=80** of frozen [`gold/grade_gold.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/grade_gold.jsonl) (full gold sha256 `72c282933c395702324db1072dcfe49cae1feac3bb8db50e9737f7b75ecb6ed7`). Slice: [pwg_ru/h2686/GRADE_GOLD_CALIB_SLICE.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2686/GRADE_GOLD_CALIB_SLICE.jsonl). Report: [src/GRADE_CALIBRATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/GRADE_CALIBRATION.md).

| Item | Value |
|---|---|
| Backend | `deepseek` / `deepseek-v4-flash` |
| Spearman ρ vs A/B/C | **0.4195** |
| Floor | 0.40 |
| Status | **DEFENSIBLE** |
| Mean A / B / C | 0.9241 / 0.8465 / 0.5295 |
| Proxy on same gold | ρ=**-0.0351** (still preliminary; not rewritten) |

## Frozen retrieval batch

From H2684 sample400 + adjudication400. Copy-through excluded (156 rows, including all `example` and `grammar_label` in the sample). Drawn: 3 definition_gloss + 3 recurring_formula + 3 sense = **9**. Manifest sha256 `b7ed1b7d134157ef2ecc59d601756110584f0139bb088dd0b5c8c7c462faff6f`.

## Live two-arm result

Engine `deepseek-v4-flash`, route `https://api.deepseek.com/chat/completions`, served model matches request, price card `pre-1608`, mock **false**. Retriever: character 4-gram (LaBSE down). TM index: sample400 leave-one-out + 2392 publication senses (1191 rows used). Ledger: 36 calls, **$0.004138**.

| Arm | n | mean quality | serious error | mean edit | tokens | wall s | cost USD | exact reuse | fragment reuse |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| no-TM | 9 | 0.590 | 6/9 | 0.609 | 5167 | 92.15 | 0.001089 | 0 | 0 |
| fragment-TM | 9 | 0.800 | 5/9 | 0.471 | 11102 | 76.11 | 0.001856 | 2 | 9 |

Deltas (TM − no-TM): quality **+0.210**, edit **−0.138**, serious-error rate **−0.111**, tokens **+5935**, wall **−16.04 s**, cost **+$0.000767**.

Per class (TM arm): formula 3/3 quality 1.0 edit 0 serious 0; gloss 3 quality 0.50 serious 2; sense 3 empty hypotheses, quality undefined, serious 3. n=9 is small; Wilson intervals on 5/9 vs 6/9 overlap. The directional gain is concentrated in recurring formulas.

## Next-wave defaults (do not rewrite Wave 1)

1. Keep Wave 1 promoted/quarantine bytes unchanged.
2. Measurement QE default: `--qe deepseek`. Never stamp proxy or LaBSE as comet.
3. Next 5,000-headword wave: attach graded fragment-TM as **fuzzy context for `recurring_formula` and exact source matches**. Treat `sense` wrappers as a separate generation problem (empty outputs here; H2684 serious-error halt still stands). Gloss TM stays advisory.
4. Retriever: char-4gram until LaBSE loads; approximate hits remain advisory.
5. Carry the H2684 short-gloss denylist (`{%Jmd%}`, `{%die%}`, …) into the next wave. Do not run a second Wave-1 repair.
6. Re-measure on this same frozen 9-card batch after the next wave. Widen the gold QE slice toward 320 only if spend is authorized again.

## Proof

```text
python src/tm_grade.py selftest
python src/tm_retrieval_eval.py selftest
python -m pytest tests/test_tm_semantic_qe_retrieval.py -q
python src/pwg_tm_w2_run.py --probe
python src/pwg_tm_w2_run.py --all --gold-limit 80 --n-per-class 3
```

_Dr. Mārcis Gasūns_
