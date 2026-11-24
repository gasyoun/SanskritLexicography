- H5559: **reusable OFFLINE DSPy Evaluate harness for Sa→Ru prompts ships on the frozen
  BLI gold — two prompts scored, current vs variant, zero DSPy in consuming lanes.**
  [src/eval/h5559_dspy_evaluate_harness.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_dspy_evaluate_harness.py)
  (the ONLY file importing `dspy`; dev tool, consumers copy the verdict not the code path)
  + metric contract [src/eval/h5559_saru_metric.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_saru_metric.py)
  (fidelity-judge + TM-match on the house `bli_eval.py` Cyrillic content-token rule;
  **IAST exactness and case-government are hard fails gating the score to 0**; semantic-F1
  alone is banned on record — it Goodharts into fluent-but-wrong Russian and cannot see
  diacritic mangling or a wrong governing preposition). Frozen split
  [src/eval/h5559_bli_gold_split.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_bli_gold_split.jsonl)
  derives unchanged from the frozen 320-row `gold/gold_set.jsonl` (H215 lock; H3172 card-3
  ≈300-item Sa→Ru intent) — no row re-cut, no label rewritten; the H2401 500-frame stays
  label-free until its sheet is voted. Demo: `current` = the mw_ru stage-1 system
  instruction verbatim (`mw_ru_prompts/1_perevod.txt`), `variant` = + equivalent/IAST/
  case-government rules ([src/eval/h5559_prompts.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/h5559_prompts.json)),
  both rendered temp-0 on `gpt-oss:120b-cloud` via the local ollama proxy, batched fidelity
  judge, then `dspy.Evaluate` over the devset with a replay program — the evaluate phase is
  offline by construction (no LM, no network) and is the own-data canary: rerun is
  byte-identical (H5559).
