# PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.meta.md — metadoc

_Created: 30-08-2026 · Last updated: 30-08-2026_

This is the companion record for the [PWG translation control-plane strangler
plan](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.md).
It records why the plan exists, how it was derived, and how it should be maintained; it does not
duplicate the plan.

## Subject

- **Purpose:** execution-ready specification for replacing overlapping PWG translation control
  planes without rewriting the proven translation engine.
- **Audience:** implementation agents, independent reviewers, and operators approving cutover.
- **Contract:** five cross-linked `/ask` layers, 27 interview rulings, explicit autonomy fence,
  file-level Wave-1 sequence, and machine-checkable acceptance evidence.

## Provenance

- **Created:** 30-08-2026, after a five-round `/ask` interview and fresh code-first pipeline audit,
  by Codex Sol (`gpt-5.6-sol`).
- **Execution owner:** [H3714 (Codex) — PWG translation control-plane strangler: shared paid-call
  kernel, transactional campaign state, and journaled TM path](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3714-Codex_SanskritLexicography_pwg-control-plane-strangler-wave1_30.08.26.md).
- **Next hardening:** independent money/store-path review inside the same execution handoff.

## Ranked improvement backlog

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Implement and verify Wave 1 | Removes the currently live PWG-TM money/data seams | queued — H3714 (Codex), title and link above |
| 2 | Perform separately authorized staged cutover | A plan cannot prove production parity by itself | parked until Wave-1 `GO` |
| 3 | Remove compatibility shims | Prevent permanent dual architecture | parked until two canaries plus one production-equivalent replay |
| 4 | Reassess throughput/multi-profile scheduling | Optimization is meaningful only after singular state/accounting | parked until cutover |

## Known limitations

1. The audit covered the production PWG→RU lifecycle, provider adapters, and `pwg-ru-data`
   boundary; it did not re-audit Cologne source/build or unrelated research/export scripts.
2. The 81 nested placeholder-bearing canonical rows were detected read-only; their semantic repair
   is deliberately outside this plan.
3. Provider canaries prove boundary behavior on at most two calls, not production quality or
   long-run reliability.
4. Exact file splits may adjust during implementation, but the component boundaries and acceptance
   contract may not change without an amended decision record.

## Intended use / known misuse

Use the subject as the authoritative build and verification contract for Wave 1. Do not read it as
authorization to repair translations, mutate canonical data, increase provider spend, shut down
legacy writers, or redesign the Claude engine.

## Maintenance and sunset plan

Keep the plan active through Wave-1 close and the independent review. Append implementation
evidence and PR links rather than rewriting interview rulings. Mark it superseded only when a
cutover plan with measured production evidence becomes authoritative.

## Deprecation status

`active`

## Related documents

1. [Roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_PWG_CONTROL_PLANE_2026H2.md)
2. [Architecture](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_PWG_CONTROL_PLANE.md)
3. [Implementation](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_PWG_CONTROL_PLANE.md)
4. [Verification](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_PWG_CONTROL_PLANE.md)

## Revision history

| Date | Event | Author |
|---|---|---|
| 30-08-2026 | Initial metadoc created with the interview, audit, execution owner, and maintenance contract | Codex Sol (`gpt-5.6-sol`) |

_Dr. Mārcis Gasūns_
