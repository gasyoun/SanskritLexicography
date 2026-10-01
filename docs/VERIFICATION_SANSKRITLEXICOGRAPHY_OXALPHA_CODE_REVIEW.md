# SanskritLexicography OxAlpha code-review verification and risks

_Created: 26-08-2026 · Last updated: 26-08-2026_

## Acceptance

| Deliverable | Proof | Failure |
|---|---|---|
| Adapter | Three docs, one agent block, five labels, PR intake OFF | Missing or duplicate configuration |
| Selection | Zero to ten fixed-window rows with risk evidence | Churn substituted for risk |
| Standards | Rule or named smell plus exact hunk | Generic advice |
| Spec | Quoted requirement or no spec available | Inference presented as fact |
| Finding | Severity, location, failure mode, repro/test | No reproducible evidence |
| Fix | Regression fails before and passes after; CI green | Untested or fenced mutation |
| Gate design | Rollout and rollback present; no activation | Workflow/protection enabled |

## Commands

Run focused selftests, then pytest tests -q from RussianTranslation and all applicable jobs in the CI workflow. Run git diff --check and verify every full link resolves.

## Risks

local-only PWG stores/TM; canonical store resolution; paid-call concurrency; backup integrity; BOM variance; generated release data. Never mutate local-only stores, start paid calls, or edit generated/data-only outputs.

## Stop policy

Stop only the affected fix for secrets/PII, production state, irreversible migration, unclear money behavior, or generated/vendor/data bulk. Record the blocker and continue safe slices.

## Autonomy gate

PASS: architecture, ordered steps, acceptance criteria, and risks exist for every wave-1 deliverable; no blocking decision remains.

_Dr. Mārcis Gasūns_
