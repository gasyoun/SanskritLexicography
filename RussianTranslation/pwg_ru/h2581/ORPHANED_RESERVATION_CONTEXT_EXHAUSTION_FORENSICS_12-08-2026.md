_Created: 12-08-2026 · Last updated: 12-08-2026_

# H2581 — an authorised call was spent on 11-08-2026 and its evidence lost to context exhaustion

Addendum to
[ROUTER_CHEAP_REQUALIFICATION_ZERO_CALL_STOP_12-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2581/ROUTER_CHEAP_REQUALIFICATION_ZERO_CALL_STOP_12-08-2026.md)
(PR [#1655](https://github.com/gasyoun/SanskritLexicography/pull/1655)). Found by **Opus 5**
(`claude-opus-5`) on 12-08-2026 while removing this session's worktree.

> ## ⚠️ Correction — supersedes the first version of this file
>
> This report was first published (PR [#1657](https://github.com/gasyoun/SanskritLexicography/pull/1657),
> filename `ORPHANED_UNAUTHORISED_RESERVATION_FORENSICS_…`) asserting the 11-08 reservation
> was made **without authorisation**, against the handoff's ⛔ prohibition. **That was wrong.**
>
> The prior session's transcript carries an explicit human authorisation at
> **2026-08-11T13:34:48Z**, 24 minutes *before* the reservation:
>
> > *"I authorise exactly two router.cheap Agent reservations and two dispatches for H2581
> > requalification on v1.144.32."*
>
> The first version inferred "unauthorised" from the handoff's ⛔ BLOCKED banner plus the
> absence of any authorisation record *in the repo* — without reading the transcript that was
> already in hand. The call was legitimate. What actually went wrong was **context
> exhaustion**, not a contract breach. The integrity defect below is unchanged and, if
> anything, more serious for it: this is what a *correctly behaving* session leaves behind.

## What actually happened

| Time (11-08-2026 UTC) | Event |
|---|---|
| 13:15:43 | Session `e405c30c-fb72-4b6b-a236-e775b57a3207` starts; human invokes `/go H2581` |
| **13:34:48** | **Human authorises exactly two reservations and two dispatches** |
| 13:38 | Handoff claimed (`🔒 CLAIMED — Opus 5 (claude-opus-5)`) |
| 13:45 | Context exhausted — conversation compacted (1st) |
| 13:54 | Context exhausted — compacted (2nd) |
| 13:58:13 | Reservation **1 of 2** published (`88d5ccf0a0014c57a680d11acf8cbb4d`, pid 7068) |
| 13:58:43 | Agent dispatch #1 → `is_error: true`, refused before reaching a model |
| **14:01:49** | Agent dispatch #2 → **`status: completed`, `resolvedModel: claude-opus-5`** |
| 14:13:22 | Context exhausted — compacted (3rd) |
| — | Session ends at 342 events with **no response wrapper, no attestation, no envelope** |

The session was Opus 5 throughout (119 assistant turns on `claude-opus-5`, 1 `<synthetic>`),
working in `SanskritLexicography/RussianTranslation`, in worktree
`SanskritLexicography-h2581-6584` on branch `h2581-exec-6584` — which it never pushed and
never committed to.

**Three compactions in one 58-minute sitting.** The bridge's two-phase design assumes the
operator survives long enough to seal: `prepare-external` spends the reservation, the Agent
turn happens, then `record-external` binds it. This session was cut in half between phase one
and phase two — twice before the reservation, once after the dispatch.

## Ledger state as found

| Field | Value |
|---|---|
| `run_id` | `h2581-requalification-v1.144.32` |
| `max_calls` | `2` |
| **`calls_spent`** | **`1`** |
| **`pending_calls`** | **`1`** |
| `finalized_calls` | `0` |
| Reservation 1 | `88d5ccf0a0014c57a680d11acf8cbb4d`, ordinal 1, `2026-08-11T13:58:13.045Z` |
| State | `pending_with_ticket` |
| Ticket sha256 | `f5cfc584936ef858fb10810c330bfa9be80cf3a23fe61677dd5bb915eff05806` |
| Sealed `request_prompt_sha256` | `b20a7dae56d3a8071ddef06a6aeae8e3e16f91d8da26b338c53a61564b3c6a7e` |

Present: ticket, request, schema. **Absent**: response wrapper, attestation, envelope.

## A model really was reached — proven, not inferred

The ledger alone cannot tell "reserved then abandoned" from "reserved, called, never recorded":
a reservation is published *before* the call, so `pending` is consistent with both.
[dispatch_forensics.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2581/dispatch_forensics.py)
settles it by matching the ticket's sealed prompt hash against the transcript (0 unparseable
lines):

| Agent `tool_use` | line | `tool_result` |
|---|---|---|
| `tooluse_90LJDJiET9U13DAAqwSk6A` | 258 | `is_error: true` — refused before dispatch |
| `tooluse_YN7nzLEEDqmKpAQCD6znJ9` | 275 | **`status: completed`, `resolvedModel: claude-opus-5`** |

One dispatch completed. A call was genuinely spent — authorised, but with **no sealed
evidence**. Under the dormant-billing state of `pwg_ru` its cost is **UNKNOWN**; it must not
be recorded as free.

## The integrity defect (unchanged by the correction)

The spend existed **only as untracked files in a zero-commit worktree**: no branch pushed, no
commit, no PR, no registry row, no `.ai_state.md` entry — nothing
[`precheck_handoff.py`](https://github.com/gasyoun/Uprava/blob/main/tools/precheck_handoff.py)
reads. One `/worktree-gc` pass would have deleted the only record that a paid call happened,
and it would have looked like the *safest* removal on the list, having zero commits.

That this came from a fully authorised, correctly behaving session is the point. The failure
mode is ordinary — a long sitting runs out of context between reserving and sealing — so it
will recur.

## Consequence for the 12-08 authorisation

A second authorisation was given on 12-08-2026 ("Authorising exactly two router.cheap
reservations/dispatches for H2581 on v1.144.32"). Against this run id:

- 1 reservation is already spent, leaving **1** under `max_calls: 2`.
- A fresh two-ticket sitting would attempt a **third** reservation on this ledger: refused
  mechanically (`budget_exceeded:max_calls`) and forbidden by the handoff — *"no retry,
  reroll, replacement reservation, repair, or third call under any outcome."*

Whether the 12-08 authorisation **renews** the 11-08 one (two calls total, one already spent →
one left) or **grants two more** (three total) is not determinable from the wording and is a
human's to settle. Either reading requires a **fresh `run_id` and ledger**, so the 11-08 call
is never silently absorbed into a later count.

## Human ruling, 12-08-2026: the second authorisation RENEWS the first

M.G. ruled that the 12-08 authorisation **renews** the 11-08 one rather than adding to it.
Settled accounting for H2581:

| | |
|---|---|
| Authorised total | **2** reservations / 2 dispatches |
| Spent | **1** (11-08, completed dispatch, never sealed) |
| **Remaining** | **1** |

### The remaining call cannot execute the handoff as written

The contract is two tickets in a fixed order: a tiny capability probe, then — *only* on its
clean PASS — the `dq_canary_puregloss` translation. One call cannot run a two-ticket gated
sequence.

### And the spent call cannot be salvaged to recover the first ticket

There was an appealing route: reservation 1 is `pending`, not consumed, so finalizing it costs
**zero new calls** — seal the 11-08 dispatch late and spend the remaining call on Ticket 2.
`record_external` always takes an operator-constructed wrapper, so building one now is arguably
the designed phase-two step arriving late rather than the banned "manual repair".

**That route is closed, on evidence.** The 11-08 session's route binding was never observed.
Searching its transcript for `credential_status()` output returns only the *source* of the
function being read — the check was never run. So whether that dispatch was served by
`https://router.cheap` or by the default endpoint is unknown, and the process environment that
could have answered is gone. Sealing it would stamp `route: router-cheap-agent` and the
router.cheap owner waiver onto a call whose gateway binding was never established — the same
false-provenance failure that stopped the 12-08 session, only retroactive and unfixable.

Note what that implies about the 11-08 sitting: it dispatched without ever checking binding.
`prespend_gate.py` exists precisely so no sitting can do that again.

### So the handoff is unexecutable as written, and needs a human to re-scope

Three options, for a human to choose:

1. **Re-scope to a single-ticket run** *(the workable one)* — spend the one remaining call
   directly on the frozen `dq_canary_puregloss` ticket, dropping the capability probe. Its
   purpose was to avoid wasting the expensive ticket on a broken route; that risk is now partly
   retired, since the 11-08 dispatch proved a completed Agent turn returns at all. The cost is
   real: the canary runs ungated, so a route fault burns the last call.
2. **Grant additional calls** — contradicts the renewal ruling; would need a new authorisation.
3. **Close as NO-GO** — preserve the evidence, mint no `gateway-w1`, and leave router.cheap
   unqualified at `v1.144.32`.

Every option still requires a **gateway-bound Opus 5 session** and a **fresh `run_id`**. Without
the binding, none of the three can produce a truthful artifact.

## What must not be done

- **Do not finalize the orphaned reservation.** Reconstructing a wrapper from the transcript's
  `tool_result` text is the "manual repair" the handoff bans.
- **Do not delete `SanskritLexicography-h2581-6584`** until a human has ruled; it is the
  primary record.
- **Do not reuse `run_id: h2581-requalification-v1.144.32`.**

## Still open

Whether the 11-08 dispatch was served by `https://router.cheap` or by the default endpoint is
**not determinable** from these artifacts — the transcript records `resolvedModel`, never the
gateway. That is the same question that stopped the 12-08 session, and it applies retroactively
to this call too.

## Preserved artifacts

[orphaned_11-08-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2581/orphaned_11-08-2026)
— verbatim copies of the ledger, ticket, request, schema, and the prior session's three helper
scripts. Nothing was modified, finalized, or completed.

_Dr. Mārcis Gasūns_
