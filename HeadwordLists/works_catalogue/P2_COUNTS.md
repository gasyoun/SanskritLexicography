_Created: 01-08-2026 · Last updated: 05-09-2026_

# ACC x NCC P2 -- adjudication counts

Sheet: `sanskritlexicography-acc_ncc_p2_c_d_review.html` · decisions file: `p2_gated_decisions.json` · decided=10614 · exported=H1657 gate (bar=unset)

| Tier | Rows | Approved | Rejected | Deferred | Unvoted |
|---|---:|---:|---:|---:|---:|
| A (auto) | 241970 | 241970 | 0 | 0 | 0 |
| B (auto) | 7832 | 7832 | 0 | 0 | 0 |
| C | 9039 | 0 | 0 | 9039 | 0 |
| D | 1575 | 0 | 0 | 1575 | 0 |

**Confirmed crosswalk rows (works_crosswalk.tsv):** 249802 (241970 Tier A + 7832 Tier B auto + 0 Tier C + 0 Tier D adjudicated).

**Confirmed non-matches logged (works_crosswalk_rejected.tsv):** 0.

**Agent-proposed, NOT promoted (works_crosswalk_agent_proposed.tsv):** 10614 -- rows carrying an agent verdict whose stratum has not cleared the measured precision bar. They are not crosswalk rows and not confirmed non-matches.

Coverage is still full (MG ruling 09-07-2026, unreversed): every Tier C/D row in crosswalk_candidates.jsonl.gz carries a verdict. What MG's ruling of 26-07-2026 (B2, H1657) changed is who casts it -- `adjudicate_p2.py` adjudicates all 10,614 with cited evidence, and a human votes a stratified sample to measure that adjudicator (`build_p2_spotcheck_sheet.py` -> `p2_precision_gate.py`).

**Sample (H1951 re-cut, 30-07-2026):** **1,111** cards over 17 strata, n=73 per side (min n with Wilson 95% LB ≥ 0.95 on a perfect vote). Supersedes the unvoted H1671 698-card frame (n=50/40). MG ruled re-draw first (vote 4c) so a 0.95 bar is attainable; the promotion bar itself is set **after** this sample is voted. On a perfect vote a 0.95 bar would promote **858** of 920 approve rows (the 62-row census stratum `C-same_author_prefix-c` tops out at LB 0.942). See [`P2_PRECISION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P2_PRECISION.md).

Promotion is gated per stratum on a Wilson 95% lower bound, so an unmeasured or weak stratum shows up in the agent-proposed count above rather than in the crosswalk.

_Dr. Mārcis Gasūns_
