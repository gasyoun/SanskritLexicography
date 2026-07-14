# Metadoc — H911 LOCAL-READINESS quality/economy gate

_Created: 14-07-2026 · Last updated: 14-07-2026_

**Subject:** [H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md](H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md)

## Purpose
The offline LOCAL-READINESS gate that decides whether the pwg_ru translation pipeline is
quality/economy-ready for scale — the first of two independent gates (the other is H909's
foreign-route latency gate) that both must PASS before any one-account foreign acceptance.
Records the `FAIL` verdict and its evidence so a future session does not re-litigate it.

## Audience
Whoever considers minting a live pwg_ru generation / foreign-route / four-account acceptance
handoff, or building on the H818 acceptance evidence.

## Provenance
- Handoff: [H911](https://github.com/gasyoun/Uprava/blob/main/handoffs/H911-Fable_SanskritLexicography_h818-local-quality-economy-readiness-gate_14.07.26.md) (minted for Fable 5).
- Executor: **Opus 4.8 (`claude-opus-4-8[1m]`) in Ultracode mode**, under an owner-authorized override of the minted Fable 5. Offline-only; no generation/probe/login/store-mutation.
- Owner corrections applied live via `review/sol.md` (denominator honesty, two-phase blind protocol, sealed-verdict join discipline, three-separate-measurements).
- Machine-readable companions: `h911_quality_economy_census.json`, `h911_blind_review_results.json`, `h911_blind_sample_manifest_v2.json` (+ invalidated v1 + `h911_freeze_v1_INVALID.txt`).

## Key result
`LOCAL-READINESS = FAIL`, resting on the **independently documented population clean-rate <80%** +
**recurring SAN-LOSS/`missing_senses`** — NOT on the incomplete 15/40 sealed-audit subset.

## Improvement backlog (ranked)
1. **Observed economy is unmeasurable** (tokens `not_recoverable`; no per-call telemetry). Persistent
   per-call token/cost instrumentation is a prerequisite for any future economy gate to yield a verdict
   instead of INCONCLUSIVE.
2. **Sealed per-card audit verdicts survive for only 15/40** (judge fields null; window audit reports
   overwritten). Preserving per-window audit reports (evidence-archive discipline) would let a future
   blind review compute agreement on the full sample.
3. **Blind worksheet cannot see whole-dropped senses** (source = per-output-sense German). A portrait-diff
   column would let the reviewer independently detect SAN-LOSS rather than defer to the audit.
4. Current-source drift of run-time input hashes vs live csl-orig was not checked (out of scope offline).

## Limitations
See the report's `## Limitations`. The gate is offline and evidence-bounded; it measures the *existing*
evidence, not a fresh run.

## Revision history
- 14-07-2026 — created with the FAIL verdict (Opus 4.8 executor, H911).

_Dr. Mārcis Gasūns_
