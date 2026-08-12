_Created: 12-08-2026 · Last updated: 12-08-2026_

# H2581 — an unauthorised reservation and a completed dispatch were already spent on 11-08-2026

Addendum to
[ROUTER_CHEAP_REQUALIFICATION_ZERO_CALL_STOP_12-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2581/ROUTER_CHEAP_REQUALIFICATION_ZERO_CALL_STOP_12-08-2026.md)
(PR [#1655](https://github.com/gasyoun/SanskritLexicography/pull/1655)). Found by **Opus 5**
(`claude-opus-5`) on 12-08-2026 while removing this session's worktree.

## Finding

> **1 of H2581's 2 authorised calls was already consumed — before any authorisation existed.**
>
> A prior session reserved ordinal **1 of 2** at **2026-08-11T13:58:13Z** and made a **real,
> completed Agent dispatch**, then abandoned the sitting without recording a response,
> attestation, or envelope. The reservation is still `pending_with_ticket`, never finalized.
>
> The handoff was minted 11-08-2026 carrying **⛔ BLOCKED — no spend is authorised**, and states
> plainly: *"do not claim this handoff, reserve a call, invoke Agent/router.cheap, or run a
> health probe"* until a fresh ruling exists. M.G.'s authorisation came **12-08-2026** — a day
> later. So this call was spent against an explicit prohibition.

This was invisible to every coordination check. It lived only as **untracked files in an
orphaned worktree** (`SanskritLexicography-h2581-6584`, branch `h2581-exec-6584`, still at the
`v1.144.32` tag with zero commits). No branch, no PR, no registry row, no `.ai_state.md` entry
— nothing `precheck_handoff.py` reads. One `/worktree-gc` pass would have deleted the only
record that a paid call ever happened.

## Ledger state as found

| Field | Value |
|---|---|
| `run_id` | `h2581-requalification-v1.144.32` |
| `max_calls` | `2` |
| **`calls_spent`** | **`1`** |
| **`pending_calls`** | **`1`** |
| `finalized_calls` | `0` |
| Reservation 1 id | `88d5ccf0a0014c57a680d11acf8cbb4d` |
| Reservation 1 purpose | `h2581-ticket1-capability-probe` |
| Reserved at | `2026-08-11T13:58:13.045Z` (pid 7068) |
| State | `pending_with_ticket` |
| Ticket sha256 | `f5cfc584936ef858fb10810c330bfa9be80cf3a23fe61677dd5bb915eff05806` |
| Sealed `request_prompt_sha256` | `b20a7dae56d3a8071ddef06a6aeae8e3e16f91d8da26b338c53a61564b3c6a7e` |

Artifacts present: ticket, request, schema. Artifacts **absent**: response wrapper,
attestation, envelope. The bridge's own `recovery-report` classifies it
`pending_with_ticket`, `ambiguous_reserved_without_ticket: 0`.

## Was a model actually called? Yes — proven, not inferred

The ledger alone cannot answer this: a reservation is published *before* the call, so
`pending` is equally consistent with "reserved then abandoned" and "reserved, called, never
recorded". [dispatch_forensics.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2581/dispatch_forensics.py)
settles it against the prior session's transcript
(`e405c30c-fb72-4b6b-a236-e775b57a3207.jsonl`, 0 unparseable lines) by matching the ticket's
sealed prompt hash:

| Agent `tool_use` | line | prompt sha256 | `tool_result` |
|---|---|---|---|
| `tooluse_90LJDJiET9U13DAAqwSk6A` | 258 | matches ticket | **`is_error: true`** — refused before dispatch |
| `tooluse_YN7nzLEEDqmKpAQCD6znJ9` | 275 | matches ticket | **`status: completed`, `resolvedModel: claude-opus-5`** |

So exactly one dispatch reached a model and completed. **A call was genuinely spent**, on
quota or money, with no authorisation and no sealed evidence. Under the memory-recorded state
that Max-route billing in `pwg_ru` is dormant, its billing is **UNKNOWN** — it must not be
recorded as free.

## Consequence for the authorised sitting

M.G. authorised **exactly two** reservations/dispatches on 12-08-2026. Against this run id:

- 1 reservation is already spent, leaving **1** under `max_calls: 2`.
- Running the authorised two-ticket sitting would attempt a **third** reservation. The ledger
  refuses it mechanically (`budget_exceeded:max_calls`), and the handoff forbids it absolutely
  — *"no retry, reroll, replacement reservation, repair, or third call under any outcome."*

This is a second, fully independent reason the zero-call stop was correct. Even had this
session been gateway-bound, the authorised sitting **could not have run to completion** on
this ledger without breaching the two-call ceiling.

## What must not be done

- **Do not finalize the orphaned reservation.** Reconstructing a response wrapper from the
  transcript's `tool_result` text is exactly the "manual repair" the handoff bans, and it would
  seal an envelope for a call made without authorisation.
- **Do not delete `SanskritLexicography-h2581-6584`** until a human has ruled. It is preserved
  here, but the original is the primary record.
- **Do not reuse `run_id: h2581-requalification-v1.144.32`.** Any authorised re-run needs a
  fresh run id and a fresh ledger, so the unauthorised call is never silently absorbed into an
  authorised count.

## Open question for a human

Whether the 11-08 dispatch was served by `https://router.cheap` or by the default endpoint is
**not determinable from these artifacts** — the transcript records `resolvedModel`, never the
gateway. If it was gateway-bound, one unauthorised router.cheap call exists unaccounted; if it
was not, the same false-provenance problem that stopped this session applies to it too.

## Preserved artifacts

[orphaned_11-08-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2581/orphaned_11-08-2026)
— verbatim copies of the ledger, ticket, request, schema, and the prior session's three helper
scripts, taken read-only from the orphaned worktree. Nothing was modified, finalized, or
completed.

_Dr. Mārcis Gasūns_
