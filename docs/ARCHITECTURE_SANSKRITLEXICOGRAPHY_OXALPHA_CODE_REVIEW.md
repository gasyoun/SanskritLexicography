# SanskritLexicography OxAlpha code-review architecture

_Created: 26-08-2026 · Last updated: 26-08-2026_

## Components

1. Canonical adapter: [issue tracker](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/issue-tracker.md), [triage labels](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/triage-labels.md), and [domain rules](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/domain.md).
2. Risk selector: at most ten fixed-window PRs; executable and critical-path risk outranks raw churn.
3. Standards reviewer: repo rules plus the fixed smell baseline; hard violations remain separate from judgment calls.
4. Spec reviewer: resolves the ruled evidence chain and reports missing/partial requirements, scope creep, or wrong implementation.
5. Evidence ledger: [planned report](https://github.com/gasyoun/SanskritLexicography/blob/master/reports/OXALPHA_30D_CODE_REVIEW_2026-08-26.md) preserves both axes and exact proof.
6. Fix lane: only proven P0/P1, one minimal regression-tested PR per independent defect.
7. Gate design: [planned design](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/OXALPHA_STATUS_GATE_DESIGN_2026.md) remains inactive.

## Contract

Each manifest row records PR, merge SHA/base, executable paths, exclusions, risk reasons, spec source, and both review states. A finding is valid only with severity, exact location, failure mode, and repro/test. The proposed check returns pass, evidence-backed fail, or infrastructure-neutral; it never silently passes an unavailable reviewer.

## Prior art

PARTIAL: existing CI and review assets do not provide formal PR code review. Reuse the canonical two-axis review and adapter; build only selection, evidence, urgent-fix, and inactive-gate layers.

_Dr. Mārcis Gasūns_
