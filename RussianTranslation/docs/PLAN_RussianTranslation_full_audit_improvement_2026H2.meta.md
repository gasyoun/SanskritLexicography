# PLAN_RussianTranslation_full_audit_improvement_2026H2 — metadoc

_Created: 23-07-2026 · Last updated: 23-07-2026_

Companion record for [PLAN_RussianTranslation_full_audit_improvement_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_full_audit_improvement_2026H2.md)
and its four layer docs (ROADMAP / ARCHITECTURE / IMPLEMENTATION / VERIFICATION).

## Purpose

Execution-ready `/ask` umbrella for the RussianTranslation **full audit → improvement
portfolio**: offline wave-1 (production residues + cohort ledger scaffold + docs), then
health-gated drain, then existing TM/gloss/editorial programmes. Single cold-start index
so agents stop re-deriving priority from dozens of dated audits.

## Audience

- Fresh execution agents (Sonnet/Opus) on track handoffs A–E
- MG for human votes and wave-2 health GO

## Provenance

- Authored 23-07-2026 via `/ask` (interview 4 rounds: goals · architecture · implementation ·
  verification/autonomy).
- Model for this authoring session: Grok 4.5 (`grok-4.5` / xAI Grok Build).
- Audit inputs: live `.ai_state.md`, store ~11,603 rows, H1403 speed audit, H1437 handoff,
  existing pubgrade-TM and Sa→Ru gloss `/ask` plans, SCALE_READINESS and pipeline history.

## Key decisions

Must tracks A+F/B/C; best-effort D then E; no paid gen; never risk store; surgical edits;
umbrella indexes (does not supersede) H215 and gloss plans; one handoff per track; drain is
wave-2 after fresh health GO. Full table in the PLAN.

## Improvement backlog (ranked)

1. After Track A lands, re-measure ledger fill rate (target: wall_clock_source non-null on ≥80% of new rows).
2. When H1437 merges, mark Track B scaffold as consumed / delete duplicate if any.
3. After H1303/H1306 votes, promote Track D from dry-run to a gated apply handoff.
4. Optional wave-2+: Message Batches API probe (H1403 A8) as a separate research handoff.

## Limitations

- Wave-1 does not move store coverage numbers.
- Track B is intentionally weaker than full H1437 (scaffold only).
- Stale-audit map is a filter, not an archive migration (files stay in place).

## Revision history

- 23-07-2026 — created (`/ask` full-audit improvement).

_Dr. Mārcis Gasūns_
