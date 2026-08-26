# SanskritLexicography OxAlpha code-review roadmap

_Created: 26-08-2026 · Last updated: 26-08-2026_

Owner: H3547 (OxAlpha) — SanskritLexicography 30-day risk-ranked code review and future independent review gate; intended executor OxAlpha (x-preview-f-free).

## Wave 0 — adapter

1. Add the canonical GitHub tracker, default triage labels, PR intake OFF, and single-context domain docs.
2. Update the existing agent-instruction file in place.
3. Merge a setup-only green PR.

## Wave 1 — retrospective

1. Rank fixed-window merged PRs by executable risk, missing review, critical paths, breadth, and churn.
2. Retain at most ten; exclude generated/vendor/data-only changes unless behavior changed.
3. Run separate Standards and Spec passes.
4. Publish one evidence ledger without merging the two axes.

## Wave 2 — urgent fixes

Reproduce candidates; drop unproven claims; repair only P0/P1 with a regression test; merge minimal green PRs.

## Wave 3 — future gate

Design executable-path filtering, independent OxAlpha review, human approval for security/production paths, failure policy, rollout, observability, and rollback. Do not activate it.

## Non-goals

No P2/P3 repairs, generated-data rewrite, deployment, branch-protection mutation, or workflow activation.

_Dr. Mārcis Gasūns_
