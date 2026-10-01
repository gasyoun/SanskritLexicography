# SanskritLexicography OxAlpha code-review hardening plan

_Created: 26-08-2026 · Last updated: 26-08-2026_

Goal: give H3547 (OxAlpha) — SanskritLexicography 30-day risk-ranked code review and future independent review gate a complete unattended route from canonical tracker setup through bounded retrospective review, urgent evidence-backed repair, and an implementation-ready but inactive future review gate.

## Decisions taken

| # | Ruling | Rationale |
|---|---|---|
| 1 | Eight repository-specific handoffs | Ownership and tests remain local. |
| 2 | Retrospective review plus future-gate design | Present defects and recurrence are both covered. |
| 3 | Fixed window 26-07-2026 through 25-08-2026 | Evidence cannot drift mid-run. |
| 4 | At most ten executable-code slices | Bounded depth beats a full-tree skim. |
| 5 | Exclude generated, vendor, and data-only churn unless behavior changed | Volume must not displace risk. |
| 6 | Independent Standards and Spec passes | One axis cannot mask the other. |
| 7 | GitHub Issues, default labels, PR intake OFF, single-context | Canonical Matt Pocock adapter. |
| 8 | PR body → issue → handoff/plan → matching doc → no spec available | Honest spec provenance. |
| 9 | Severity, exact location, failure mode, and repro/test required | No proof means no finding. |
| 10 | Fix only proven P0/P1 with regression tests | Limits unattended mutation. |
| 11 | Adapter and fixes use separate green PRs | Setup and remediation stay reviewable. |
| 12 | Design but do not enable the future gate | Activation is out of scope. |
| 13 | Human approval remains additional for security/production paths | Model review does not replace accountable release judgment. |

## Autonomy contract

Apply marked defaults and log them. Missing spec evidence skips only the Spec axis. Stop only an affected fix when secrets/PII, production state, irreversible migration, unclear money behavior, or bulk generated/vendor/data edits are required; continue the remaining review. Never mutate local-only stores, start paid calls, or edit generated/data-only outputs. The adapter lands alone. Findings are durable. Each proven P0/P1 gets a minimal regression-tested PR and merges only when required checks are green. Do not activate a workflow or branch-protection rule.

## Layers

1. [Roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_SANSKRITLEXICOGRAPHY_OXALPHA_CODE_REVIEW_2026Q3.md)
2. [Architecture](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SANSKRITLEXICOGRAPHY_OXALPHA_CODE_REVIEW.md)
3. [Implementation](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SANSKRITLEXICOGRAPHY_OXALPHA_CODE_REVIEW.md)
4. [Verification](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SANSKRITLEXICOGRAPHY_OXALPHA_CODE_REVIEW.md)

## Starter

Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H3547-OxAlpha_SanskritLexicography_oxalpha-30d-risk-review-gate_26.08.26.md and execute it.

_Dr. Mārcis Gasūns_
