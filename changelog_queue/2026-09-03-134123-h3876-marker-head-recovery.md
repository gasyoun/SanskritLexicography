- **H3876 — marker-residual recovery, tier `marker-head` (Opus 5 `claude-opus-5`, 03-09-2026).**
  The 1,389 unresolved Sa→Ru forms carrying `+`/`-` morpheme marks are recovered **1,018 forms /
  1,783 tokens** by lemmatizing the rightmost element through the *existing* DCS form→lemma map:
  `A-brahma-BuvanAt` fell through only because `BuvanAt` is an ablative of `Buvana` — in neither
  the bare-root nor the bare-lemma inventory, but a DCS form key all along. Nothing is segmented,
  so the wave-3 `vidyut.cheda` NO-GO stands untouched. Token coverage 87.11 % → **87.28 %**,
  resolved forms 111,996 → 113,014 (58.7 % → 59.2 %), typology row 1,389/2,312 → 371/529,
  +17 lemma and +3 root entries, nothing lost. Two guards, each bought with a measurement: DCS
  form keys only (all 42 vidyut-sourced heads adjudicated exhaustively — 35/42, with 7 bogus
  lemmas like `vart`→`varDi`; wave 2 independently put the vidyut tier at 71.8 %) and head length
  ≥ 3 (every 1–2 char head resolved to a pronoun homograph, `zA`→`tad`). Lemma precision **25/25**
  on the canonical D5 tier × frequency sample (single-judge, not the 3-judge panel — that run is
  still owed) against the wave-2 `marker` baseline of 93.3 %; layer impact 27 top-1 gloss flips in
  40,387 lemma entries (0.067 %), 23 of them ties between two one-occurrence glosses, one mild
  degradation (`saMsiD`). The gloss axis is the honest weak point — a compound's Russian attaches
  to its head lemma, systematic lemma defect #3 the wave-2 panel already named, extended here to
  1,018 more forms and not solved. `marker-head` registered in the `TIERS` tuple of
  `saru_gloss_sample.py` + `saru_gloss_aggregate.py` so the next panel measures it; 10 new
  regression tests. Published `.tsv`/`.jsonl` untouched (D8 fence). Report:
  [docs/REPORT_H3876_saru_marker_head_recovery_03-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/REPORT_H3876_saru_marker_head_recovery_03-09-2026.md).
