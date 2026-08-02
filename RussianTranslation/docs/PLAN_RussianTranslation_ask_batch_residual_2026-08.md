# PLAN — RussianTranslation ask-batch residual (2026-08)

_Created: 02-08-2026 · Last updated: 02-08-2026_

**Index / cover.** Staged by [`/ask-batch`](https://github.com/gasyoun/claude-config/blob/main/commands/ask-batch.md)
(`ASK_BATCH_STAGING_2026-08`, slice-3). **Nothing here executes until `/go` or `/next-task`.**

Does **not** rewrite the July umbrella or the three research PLANs. Those stay authoritative.
This residual orders **four wave-1 units** from the 02-08-2026 interview.

## Goal (one paragraph)

August residual replan for [`RussianTranslation/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation):
**research-first**, as **three equal small handoffs** (RV multi-translation residual · pubgrade TM residual · Sa→Ru gloss residual), plus **one parallel money-lane gate handoff** that remeasures five paired paid probes (wall vs `duration_api_ms`), locks **one** fail metric, and may relax the call ceiling to a measured floor — with **`--stop-before-promote` always** and **no store mutation** from the remeasure. No bulk c4 drain in this residual.

## Layer docs

| Layer | Doc |
|---|---|
| Waves / non-goals | [ROADMAP_RussianTranslation_ask_batch_residual_2026-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_ask_batch_residual_2026-08.md) |
| Boundaries / reuse | [ARCHITECTURE_RussianTranslation_ask_batch_residual.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_ask_batch_residual.md) |
| Ordered steps | [IMPLEMENTATION_RussianTranslation_ask_batch_residual.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_ask_batch_residual.md) |
| Acceptance / risks | [VERIFICATION_RussianTranslation_ask_batch_residual.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_ask_batch_residual.md) |

## Authoritative sibling plans (do not re-decide)

| Unit | PLAN (execute residual against this) |
|---|---|
| RV multi-trans | [PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md) |
| pubgrade TM | [PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md) |
| Sa→Ru gloss | [PLAN_RussianTranslation_saru-gloss-quality_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_saru-gloss-quality_2026H2.md) |
| July umbrella (offline factory residues) | [PLAN_RussianTranslation_full_audit_improvement_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_full_audit_improvement_2026H2.md) |

## Decisions taken (02-08-2026 interview)

| # | Fork | Ruling | Rationale |
|---|---|---|---|
| A1 | Primary objective | **Research first** (not production drain, not editorial-gold spine) | Human override of audit recommend-A |
| A2 | Research packing | **Equal three small handoffs** RV + TM + gloss | No single research primary |
| A3 | Money-lane residual | **Wave-1 parallel**: one paid-gate remeasure only | Unblocks future spend; not bulk drain |
| A4 | Ceiling / metric | **Remeasure 5 paired paid** (wall vs `duration_api_ms`), then lock ONE metric + relax ceiling to measured floor | Closes H2138/H2152 provenance |
| A5 | Promote fence (paid-gate unit) | **`--stop-before-promote` always; no store mutation** | Probes measure only |
| A6 | Verification bar | **Executable proof per unit** (command exit 0 or committed artifact path) | No chat-only done |
| A7 | Defaults locked | Surgical extends; worktree→PR; LANG_PARITY on SHARED; no rewrite of sibling PLANs | Standing |

## Autonomy contract

- **On ambiguity:** pick marked default in this PLAN or the sibling PLAN for that unit; log one line in `RussianTranslation/.ai_state.md` Dev Notes (`default-taken: …`); continue.
- **Stop conditions:** paid-gate burns budget with no paired measurements after 5 probes; any path that would mutate the gitignored store or promote; discovery that a residual unit is already ✅ on origin — close handoff as no-op with evidence link.
- **Commit authority:** worktree off `origin/master` → PR → merge on green. Never shared main-tree edit of SanskritLexicography.
- **Fence:** no bulk multi-window c4 drain; no Max Workflow production translate; no promote/merge of store from residual units; no re-opening closed H1811/H1940 tracks.

## Wave-1 handoffs (minted by ask-batch)

See ROADMAP § Wave 1. Each starter:

```
Read C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\docs\PLAN_RussianTranslation_ask_batch_residual_2026-08.md and execute it. Scope: <unit-id>.
```

_Dr. Mārcis Gasūns_
