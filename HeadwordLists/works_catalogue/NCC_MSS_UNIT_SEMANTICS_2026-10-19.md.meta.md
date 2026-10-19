# NCC_MSS_UNIT_SEMANTICS_2026-10-19.md.meta.md — metadoc for `NCC_MSS_UNIT_SEMANTICS_2026-10-19.md`

_Created: 19-10-2026 · Last updated: 19-10-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[NCC_MSS_UNIT_SEMANTICS_2026-10-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/NCC_MSS_UNIT_SEMANTICS_2026-10-19.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [NCC_MSS_UNIT_SEMANTICS_2026-10-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/NCC_MSS_UNIT_SEMANTICS_2026-10-19.md)
- **Purpose:** Settles what a manuscript witness unit is for the NCC MSS census — the
  printed-reference unit (parser) vs the VisualDCS workbook's `mss` cell — measures the
  20-work canary both ways, rules on the locked canary clause, and files a versioned v2
  proposal for human ratification.
- **Audience:** Whoever re-runs the canary, ratifies/rejects the v2 proposal, or touches
  [`census_ncc_mss.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/census_ncc_mss.py).
- **Format / contract:** decision brief — verdict first, two definitions with worked
  examples, a 20-work table, a control section, a ruling, and a separate versioned
  proposal file. The measurement artifacts are the TSV/JSON beside it.

## Provenance
- **Created:** 19-10-2026 (H7085, DeepSeek v4.1 Flash `deepseek-flash`).
- **Measured at:** `origin/master` `55df10a6` (post-H7084 `MD` exemption, PR #2439).
- **Supersedes:** none; the H6995/H7073 canary report remains the pilot record.
- **Next hardening:** re-run when the workbook or `census_ncc_mss.py` changes; ratify or
  reject the v2 proposal.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Human ratifies or rejects [v2 proposal](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/NCC_MSS_UNIT_SEMANTICS_PROPOSAL_V2_2026-10-19.md) | The locked clause is vacuous as a gate; the amendment decides whether it stays one | parked — MG `@DECIDE`, GTD row |
| 2 | Re-run the tool if the VisualDCS workbook is refreshed | The workbook side is the moving part; the body side is pinned to the corpus | pending |
| 3 | Replace the first-exact-row workbook reader with an alias-aware, order-stable one | Bhāgavata's alias row (`mss=1`) sits before the main row; the current reader is title-variant sensitive | parked — H7085 residual, no handoff |

## Known limitations / caveats
- The control rule is a disclosed selection rule (single workbook row, `mss` ≥ 500,
  ≥ 100 body units); 3/102 agree within ±5 %, so the controls are narrow.
- The workbook reader takes the first row whose IAST equals the label exactly — a
  title-variant or row-order change moves the "exact-row" value.
- Body counts are post-H7084 `MD` exemption; the pre-#2439 numbers differ (Rāmāyaṇa
  814 vs 819), which is why the subject states its measured commit.
