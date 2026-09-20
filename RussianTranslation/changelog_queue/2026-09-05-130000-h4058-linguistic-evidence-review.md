_Created: 05-09-2026 · Last updated: 05-09-2026_

- H4058: **independent linguistic / corpus-evidence review of the six post-GLM PWG
  deliveries — verdict NOT READY for human voting.** Reviewer Fable 5.1
  (`claude-fable-5-1`), frozen inputs: `origin/master` `182f5c339`, store sha256
  `79d72dbc…` 11,519 rows, pwg-ru-data `eaeb870`. Implementation correctness of
  H4052–H4057 PASSES on their expressly offline scope; corpus/alignment/TM evidence
  FAILS: `supports_senses` is a lemma-level roll-up copied onto every sense row
  (only 2,218 rows = 19.3 % carry a per-sense `evidence` item), the 1.09 M-row
  verse-aligned Sa↔Ru parallel corpus is consulted for lemma presence only and
  supports 0 senses, the mined tier and lecture transcripts are not on disk, the
  store has no English column, and the H4056 "TM 10/10 hit" is self-identity
  (TM built from the same store; entry-level addresses: 2,445 distinct over 11,510
  rows, hold-out replay 8/10 via sibling senses). Eight of the ten packet cards have
  no sense-level Russian evidence while the panel prints four "supporting"
  dictionaries; six are grammatical apparatus. Store-wide apparatus drift: 60 dropped
  / 68 added Sanskrit tokens, 118 `<ls>` count mismatches. Evidence:
  [review report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/H4058_PWG_POST_GLM_LINGUISTIC_EVIDENCE_REVIEW_05-09-2026.md),
  probes [h4058_evidence_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4058_evidence_probe.py) /
  [h4058_tm_address_collision.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4058_tm_address_collision.py),
  receipts [H4058_evidence_probe.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4058_evidence_probe.json) /
  [H4058_tm_address_collision.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4058_tm_address_collision.json).
  Read-only over the store; 0 provider calls; peer review H4059 not read; reviewed
  baseline untouched; seven prioritized repair residuals, one minted as an agent handoff.

_Dr. Mārcis Gasūns_
