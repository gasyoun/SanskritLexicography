_Created: 05-09-2026 · Last updated: 05-09-2026_

- H4119: **the evidence panel now shows the sense's own evidence, the corpus supports
  senses, and the TM receipt is non-circular.** The three P0/P1 defects ranked by the
  H4058 review, repaired and measured read-only over the canonical store — no provider
  call, no promotion. **(P0)** `evidence_summary` is a LEMMA roll-up attached identically
  to every row sharing a `key1`; rendering its `supports_senses` as sense support credits
  a sense with a sibling sense's evidence — **8,584 of 11,519 rows** are credited by the
  roll-up alone, an ×4.87 inflation over the 2,218 rows carrying their own per-sense
  `evidence`. [build_h4056_evidence_packet.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h4056_evidence_packet.py)
  now gates eligibility on `row['evidence']` (roll-up-only rows counted in a new
  `rollup_only_no_sense_evidence` funnel bucket, never silently admitted) and renders the
  per-sense array under «Свидетельства ЭТОГО значения», with the roll-up under an
  explicitly lemma-scoped label. **(P1)** `corpus` was a presence-only NONRU lane, so a
  1.09M-row verse-aligned Sa-Ru resource supported 0 senses; new
  [corpus_lexicon_lane.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_lexicon_lane.py)
  makes it token-comparable — 1,093,391 usable Russian renderings (`translation` 992,265 ·
  `commentary` 101,126), **166/221 store key1 covered (75.11 %)**, matched/missed/ambiguous/
  no_lane = **575 / 9,038 / 1,793 / 113** over 11,519 rows, **205 rows newly supported**.
  The lane can never reach `provides` and never emits `contradicts` (a verse rendering is
  one translator's choice, not an equivalent statement), and it is wired into
  `annotate_evidence` behind `CORPUS_LEX_LANE`, **off by default** — switching it on is a
  store promotion, not a code default. **(P2)** A TM built from the store and queried with
  that store's own addresses hits 100 % by construction; the receipt now states the address
  unit (entry-level `ru:<input_raw_sha256>`, **2,445 distinct addresses over 11,510
  addressable rows**, 9 unaddressable) and runs a HOLD-OUT replay — 60 addresses withheld,
  TM rebuilt without them: **hit 0 / miss 59 / defer 1**. There is no cross-card reuse in
  this store; the TM's value is re-run idempotence, not deduplication. Probe
  [tools/h4119_evidence_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4119_evidence_probe.py)
  (+ `--selftest` on committed fixtures), receipt
  [reports/H4119_evidence_probe.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4119_evidence_probe.json),
  report
  [docs/H4119_PWG_EVIDENCE_PANEL_SENSE_LEVEL_REPAIR_05-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/H4119_PWG_EVIDENCE_PANEL_SENSE_LEVEL_REPAIR_05-09-2026.md).
  Four selftests green; store writes 0.

_Dr. Mārcis Gasūns_
