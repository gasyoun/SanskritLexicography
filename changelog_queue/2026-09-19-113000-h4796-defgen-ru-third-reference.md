- H4796: **Russian third reference joined to the defgen eval** — corpus-attested
  sa-ru-glossary renderings (SanskritRussian lemma layer, kosha dataset
  `sa-ru-glossary`) as the THIRD witness after the EN MW baseline and the H2408
  Heritage FR second reference. Three-way census: 500 frozen ∩ 333 FR ∩ **384 RU**
  → **287 all-three headwords** (76.8% RU coverage of the frozen sample);
  [tools/h4796_defgen_ru_third_reference.py](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/h4796_defgen_ru_third_reference.py)
  (`build`/`metrics`/`threeway`/`judge`/`report`; FR freeze check reproduces all
  333 kosha H2408 digests before anything is scored). Measured on the subset: the
  RU surface channel is **script-degenerate** (token-F1 ≈ 0.0000 vs Cyrillic for
  every arm regardless of meaning — the blinded judge is mandatory for RU
  adequacy; resumable `judge` subcommand landed, deliberately not run in this
  offline unit), and the surface MW-familiarity gradient reproduces for every
  arm (chrF_MW − chrF_FR: floor +2.9 < ctx arms +8.2…+10.7 < F1 +14.1, all CIs
  exclude 0, seeded sign test ≤ 2.7e-28); surface arm ranking stable except the
  bottom-tail A3/A0 swap. RIGHTS: FR (LGPLLR) and RU (tier=restricted,
  corpus-derived) text never committed — digest+word-count subset only.
  Report:
  [data/DEFGEN_RU_THIRD_REFERENCE_REPORT_2026-09-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFGEN_RU_THIRD_REFERENCE_REPORT_2026-09-19.md);
  artifacts under
  [data/defgen_ru_third_reference/](https://github.com/gasyoun/SanskritLexicography/tree/master/data/defgen_ru_third_reference).
  F48 row extended; kosha consumed read-only (H4812 dual-run tombstone → H4796);
  kosha-side manifest/protocol edge left as the named residual.
