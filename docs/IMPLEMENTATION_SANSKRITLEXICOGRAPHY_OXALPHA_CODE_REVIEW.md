# SanskritLexicography OxAlpha code-review implementation

_Created: 26-08-2026 · Last updated: 26-08-2026_

## Ordered sequence

1. Create a fresh worktree from origin/master; read [agent instructions](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md), [Codex instructions](https://github.com/gasyoun/SanskritLexicography/blob/master/AGENTS.md), state, README, changelog, and relevant plans.
2. Add the three adapter docs under [docs/agents](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents), update the existing instruction file, keep PR intake OFF, create only missing canonical labels, and merge this PR alone.
3. Validate and risk-rank these candidate slices: #1884, #1837, #1868, #1841, #1852, #1871, #1870, #1867, #1861, #1860. Replace any out-of-window or non-executable candidate rather than expanding past ten.
4. For each retained PR, fetch body, commits, files, issues, base SHA, and head SHA; resolve the Spec source in the ruled order.
5. Run independent bounded Standards and Spec passes. Primary focus: RussianTranslation control-plane, store writers, orchestration, promotion, corpus gates, and TM generation.
6. Publish [the evidence report](https://github.com/gasyoun/SanskritLexicography/blob/master/reports/OXALPHA_30D_CODE_REVIEW_2026-08-26.md), including exclusions and no-spec outcomes.
7. For each proven P0/P1, add a regression test beside the affected seam, implement the smallest repair, run focused and repo gates, open a minimal PR, and merge only when green.
8. Write [the future-gate design](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/OXALPHA_STATUS_GATE_DESIGN_2026.md); do not change live protection or workflows.
9. Update changelog and state with landed evidence; close only when adapter, report, applicable fixes, and design exist.

_Dr. Mārcis Gasūns_
