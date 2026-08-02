# VERIFICATION — RussianTranslation ask-batch residual

_Created: 02-08-2026 · Last updated: 02-08-2026_

## Acceptance per unit

| ID | Done when | Proof (executable) |
|---|---|---|
| W1-RV | Residual unit from sibling PLAN lands | Sibling VERIFICATION command for that unit, or green targeted test + PR URL |
| W1-TM | One TM residual lands | Sibling VERIFICATION one-liner exit 0 + PR URL |
| W1-GL | One gloss residual lands | Sibling VERIFICATION one-liner exit 0 + PR URL |
| W1-GATE | Table of 5 paired probes + locked metric committed | File path exists on branch; `n=5` rows; metric name explicit; zero promote/store writes in diff |

## Risks

| Risk | Mitigation |
|---|---|
| Research unit already shipped | Status check first; close as no-op with evidence |
| Paid probes burn $ without locking metric | Cap at 5; stop after table; no retries beyond plan |
| Store wipe class (H2025) | Fence: no promote; no store mutation |
| Wall vs API metric disagreement | Table both; human-locked default is “pick one and document” — agent locks the lower-noise metric if clear, else wall-clock with caveat |

## Autonomy-readiness gate (wave-1)

| Unit | Arch | Steps | Accept | Risks | Blocking @DECIDE |
|---|---|---|---|---|---|
| W1-RV | ✅ sibling | ✅ | ✅ | ✅ | none (votes deferred) |
| W1-TM | ✅ sibling | ✅ | ✅ | ✅ | none |
| W1-GL | ✅ sibling | ✅ | ✅ | ✅ | none |
| W1-GATE | ✅ this residual | ✅ | ✅ | ✅ | none (ceiling floor is measurement outcome) |

**Gate: PASS** for residual mint.

_Dr. Mārcis Gasūns_
