# Metadoc — STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md

_Created: 26-07-2026 · Last updated: 26-07-2026_

- **Purpose:** design-of-record for the human gold cut over the DE→RU
  translation store — population, strata, size justification, label proposal,
  tiered κ plan, H1404 binding mechanics. Parked for human sign-off; nothing
  executed.
- **Audience:** the maintainer running review rounds; the A51 paper's methods
  section cites it.
- **Provenance:** H1633, Fable 5 (`claude-fable-5`), 26-07-2026. Inputs:
  [HUMAN_GOLD_PROTOCOL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md),
  [GRADE_GOLD_MEMO.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/GRADE_GOLD_MEMO.md),
  [JUDGE_POLICY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/JUDGE_POLICY.md),
  [REVIEW_GOLD_VOTING_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.md),
  H1624 acceptance matrix.
- **Improvement backlog (ranked):**
  1. After sign-off: write `build_store_gold_sheet.py` + selftest; freeze seed
     and pool counts into the lock.
  2. Measure real intra-lemma ICC from the first labeled batch; replace the
     assumed ρ=0.1 in the DEFF row.
  3. Fold the cut into HUMAN_REVIEW_MINIMIZATION.md gate arithmetic if ruled a
     named gate.
- **Limitations:** sizes are planning arithmetic, not measurements; pool counts (7,286 of
  11,163) are as-of 26-07-2026 and recomputed at generation time.
- **Revision history:**
  - 26-07-2026 — created (H1633).
  - 26-07-2026 — rulings R1–R5 recorded in §8 (MG, chat): n=400, labels adopted, NO second reviewer through 2027 (intra-rater plan is permanent), named gate G6b, sequencing after g6/g5 votes; execution routed to H1665, additionally gated on H1664 queue triage. Fable 5 (`claude-fable-5`).

_Dr. Mārcis Gasūns_
