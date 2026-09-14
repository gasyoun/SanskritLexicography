- **H4713 stem co-occurrence expansion of pwg-sense-attestation-window shipped (OxAlpha/GLM) — Census A7 closed with a second evidence class on all 53,003 senses.**
  [`h4713_cooc_window_expand.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4713_cooc_window_expand.py)
  (`--selftest` green) joins kosha `dcs-stem-cooccurrence-full` (VisualDCS 1-222342.csv, 353,351 stem-pair rows) onto the
  C2P1 window universe via canonical `sanskrit_util.to_slp1`, self-excluded, L+R pooled;
  per-sense `cooc_*` + `expanded_*` fields never touch the BR `earliest`/`latest`.
  Output: [`pwg_sense_attestation_window_cooc_expanded.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sense_attestation_window_cooc_expanded.jsonl)
  (40,013 senses / 75.5% with cooc evidence; 5,603 window-less senses gain an explicitly-labelled `cooccurrence-only` window;
  33,958 BR windows widened; 35,390 flagged `cooc_saturated` at the corpus horizon — recommended consumer filter).
  Held-out verification (seed 4713, n=300, pre-registered ≥50% intersection): **PASS** — informative non-saturated stratum 89.3% intersection / 71.4% containment.
  Report: [`H4713_COOC_WINDOW_EXPANSION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/H4713_COOC_WINDOW_EXPANSION.md) ·
  validation: [`H4713_cooc_window_expansion_validation.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4713_cooc_window_expansion_validation.json).
  Handoff [H4713](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4713-OxAlpha_SanskritLexicography_xwalk-a7-cooccurrence-attest-window_14.09.26.md).
