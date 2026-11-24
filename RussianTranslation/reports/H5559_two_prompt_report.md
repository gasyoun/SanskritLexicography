# H5559 — DSPy Evaluate harness for Sa→Ru prompts: two-prompt score report on the frozen BLI gold

_Created: 25-11-2026 · Last updated: 25-11-2026_

_Dr. Mārcis Gasūns_

## What shipped

| Artifact | Path |
|---|---|
| Harness script (ONLY file importing `dspy`) | [`src/eval/h5559_dspy_evaluate_harness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_dspy_evaluate_harness.py) |
| Metric definition (pure stdlib, no dspy, no network) | [`src/eval/h5559_saru_metric.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_saru_metric.py) |
| Frozen split (beside the script) | [`src/eval/h5559_bli_gold_split.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_bli_gold_split.jsonl) |
| Two prompts (current vs variant) | [`src/eval/h5559_prompts.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_prompts.json) |
| Predictions + judge verdicts | [`reports/H5559_predictions_current.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H5559_predictions_current.jsonl) · [`reports/H5559_predictions_variant.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H5559_predictions_variant.jsonl) |
| Scores (summary + per item) | [`reports/H5559_scores_current.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H5559_scores_current.json) · [`reports/H5559_scores_variant.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H5559_scores_variant.json) |
| Per-item table (both prompts) | [`reports/H5559_per_item_table.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H5559_per_item_table.tsv) |

## Gold provenance (read before quoting any number)

The frozen split derives **unchanged** from [`gold/gold_set.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl)
(320 rows ≈ the "~300-item Sa→Ru gold" of H3172 card 3's intent; review lock
`h215-gold-full-320-2026-08-14`). No row re-cut, no label rewritten — the split file
carries a `_meta` provenance line and `build-split` refuses drift. The H2401
stratified 500-frame (`gold_frame_b1_stratified_500.tsv`) is still **label-free** by
design (its annotation sheet is unvoted), so it cannot be the scored gold yet; when
that vote lands, re-derive a new versioned split, do not mutate this one (H3172's
freeze rule). Rows carry their gold `label` (`correct` 200 · `lemma-variant` 46 ·
`partial` 28 · `proper-name` 24 · `wrong-sense` 13 · `hallucinated` 9); headline
numbers below are over the **full 320** as the handoff demands — the per-item TSV
lets a reader re-cut by label and see the defective-gold effect themselves.

## Metric contract

`score = 0` if **any hard fail**, else `0.5 × fidelity + 0.5 × tm_match`.

- **fidelity-judge** — batched LLM verdict (temp 0, [`h5559_saru_metric.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_saru_metric.py) `JUDGE_PROMPT`): is the candidate a usable Russian equivalent of the Sanskrit input, gold pair as navigation?
- **TM-match** — Dice over Cyrillic content tokens (len≥4), the house rule already producing P@1/MRR in [`bli_eval.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/bli_eval.py).
- **IAST exactness (hard fail)** — any Latin token carrying IAST diacritics or stripping to an input token must be byte-identical to it (`yuvānam`→`yuvanam` fails the row).
- **Case-government (hard fail)** — if the gold governs with a preposition, the prediction must govern in the same slot (в/во · к/ко · с/со · о/об/обо); a different governing preposition zeroes the row.
- **Semantic-F1 alone is banned** (on record in the metric file): it Goodharts into fluent-but-wrong Russian and cannot see IAST mangling or wrong case government.

## Two-prompt result (full 320-row BLI gold, dspy.Evaluate, replay program)

| prompt | score | fidelity | tm_match | hard-fail rate | iast fails | case fails | n |
|---|---|---|---|---|---|---|---|
| current (mw_ru stage-1 verbatim) | 0.4019 | 0.7594 | 0.0854 | 0.05 | 2 | 14 | 320 |
| variant (+equivalent/IAST/case rules) | 0.4126 | 0.725 | 0.1315 | 0.0469 | 0 | 15 | 320 |

**Verdict:** variant wins on the composite (**0.4126 vs 0.4019**), driven by
TM-match (0.1315 vs 0.0854) and zero IAST fails (0 vs 2),
at a small fidelity cost (0.725 vs 0.7594). Current's long
dictionary-entry style outputs score fidelity well but miss the short gold equivalent
on token overlap, and produced the set's only 2 IAST mangling fails. This is a
**harness demo, not an adoption verdict** — no prompt changes shipped anywhere.

## Own-data canary (determinism)

- Render + judge at **temp 0**, `gpt-oss:120b-cloud` via the local ollama proxy (model id recorded per prediction row).
- `evaluate` is **offline by construction**: replay program + pure metric, zero LM, zero network.
  Rerun twice: `reports/H5559_scores_{current,variant}.json` **byte-identical** (`cmp` PASS both).
- Best-effort caveat kept honest: temp-0 LLM render/judge is deterministic in practice but
  not contractually bit-stable upstream; the committed prediction files + offline evaluate
  are the reproducible artifact — rerun *those*, not the live phases, to reproduce the scores.

## Run commands (for consumers)

```bash
python src/eval/h5559_dspy_evaluate_harness.py selftest                 # offline, no LM
python src/eval/h5559_dspy_evaluate_harness.py render --prompt current  # live, scratch venv with dspy
python src/eval/h5559_dspy_evaluate_harness.py judge  --file reports/H5559_predictions_current.jsonl
python src/eval/h5559_dspy_evaluate_harness.py evaluate --file reports/H5559_predictions_current.jsonl --name current
```

## Consumer note (first adopting lane)

**First adopter: the dictionary chain (`mw_ru`)** — its stage-1/stage-3 translation
prompts are exactly the `current` prompt family scored here, and its QA-judge stages
currently judge ad hoc; swapping the ad-hoc QA score for this harness's verdict on a
sample is the smallest real step. `pwg_ru` cards and KeySwap hints are next in line.
Adoption = **copy the verdict, not the code path**: consuming lanes stay dspy-free
(SKILLOPT_PIPELINE_MEMO); the harness runs in a scratch venv on demand.

## Fences

BLI gold only; no personal data in harness, examples, or report. No live-lane contact:
nothing here touched the store, TM, promotion, or any production prompt.
