- H5279: **Jev re-rank of the frozen defgen candidate glosses** — TypeSafe
  «System One» (jev-1.13.0) scored all 500 headwords × 5 frozen arms
  (2,500 candidate calls) against the DCS corpus context (headword + grammar +
  ≤5 attestation sentences + ONE candidate gloss; the MW gold gloss is NOT in
  the state, so the Jev arm is a different — corpus-grounded — signal from the
  H730 `deepseek-chat` adequacy judge). **Verdict GO on all three locked
  checks:** Jev reproduces the baseline judge's arm ranking exactly
  (F1 > A1 > A3 > A2 > A0), separates the random floor (A0 0.71 vs systems 4.29,
  gap 3.58; baseline judge gap 4.12), and costs **2.6×** less per 500-headword
  pass ($0.063 vs ~$0.161 reconstructed at the H1210 deepseek-chat rate).
  Rank agreement: Kendall τ-b 0.58 vs the baseline judge (0.31 vs chrF-MW),
  per-item top-1 127/500 vs judge (159/500 vs chrF; 8/500 items carry a
  constant baseline row, capping agreement). **Design finding: the H5277
  all-candidates-in-one-state shape collapses on this task** — floor gap 0.011
  (every arm hedged ~3.70) — so the pass uses isolated-candidate scoring; the
  probe is committed as evidence. Measurement-only — no defgen lane is rewired.
  Script:
  [tools/h5279_jev_defgen_gloss_rerank.py](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/h5279_jev_defgen_gloss_rerank.py)
  (`--selftest`/`--smoke`/`--run`/`--analyze`); report
  [data/DEFGEN_JEV_RERANK_REPORT_2026-09-24.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFGEN_JEV_RERANK_REPORT_2026-09-24.md);
  artifacts under
  [data/defgen_jev_rerank/](https://github.com/gasyoun/SanskritLexicography/tree/master/data/defgen_jev_rerank).
  Reuses Uprava `tools/jev_probe.py` (H5275) and consumes kosha
  `data/eval/defgen/` read-only.
