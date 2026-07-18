# ROADMAP_ACC_NCC.meta.md — metadoc for `ROADMAP_ACC_NCC.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[ROADMAP_ACC_NCC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ACC_NCC.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [ROADMAP_ACC_NCC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ACC_NCC.md)
- **Purpose:** Specifies and tracks the ACC (Aufrecht's *Catalogus Catalogorum*) × NCC (*New
  Catalogus Catalogorum*) catalogue-of-works crosswalk build — decisions locked, phased plan
  P0–P5, rights resolution, and current status per phase.
- **Audience:** Whoever picks up the P2 adjudication gate or a downstream P3–P5 phase (kosha
  consumer work); also the reference for "why is this asset dual-licensed" questions.
- **Format / contract:** Numbered phases (P0–P5) each with a deliverable and status marker
  (✅ DONE / BLOCKED / queued); a decisions-locked table; a rights section. New phase status
  updates edit the status cell in place, they do not fork the doc.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`).
- **Next hardening:** none scheduled — update opportunistically when P2 unblocks or a later
  phase lands.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Unblock P2 adjudication ([Draft PR #264](https://github.com/gasyoun/SanskritLexicography/pull/264)) — MG vote on the full 49,019-row sheet | Doc has said "BLOCKED on MG's vote" since 09-07-2026; the whole P3–P5 chain is gated on this one human decision | parked — MG `@DECIDE`, tracked in Uprava GTD, not this metadoc's job to chase |
| 2 | MG re-verify the local NCC dump isn't stale before the Su→Ha gap is frozen (§4 of the subject) | Explicitly flagged in the subject as a pre-freeze condition, not yet done | parked — MG `@DECIDE` |
| 3 | Once P2 clears, fold the realized P3 (kosha `works` table) status back into this doc rather than leaving it as a forward-looking deliverable description | Keeps the roadmap from drifting into a stale plan once work ships | parked — depends on item 1 |

## Known limitations / caveats
- The doc's own Tier-A/B exact+nasal-fold match counts (8,413 / +2,041/+2,047) are frozen at
  the 03–06-07-2026 measurement; re-verify before citing in a paper if NCC/ACC source files
  change upstream in csl-orig or VisualDCS.
- Rights section states NCC = CC BY-NC 4.0 and ACC = CC BY-SA 4.0, dual-licensed per field —
  any consumer must preserve this split, never flatten to one license.
- The whole downstream chain (P3 kosha consumption, P4 surfaces, P5 release) is inert until
  the P2 human vote lands; treat "queued" status literally, not as "in progress."

## Intended use / known misuse
- **For:** orienting a session that picks up P2 adjudication, or any kosha-side session
  building the `works` table consumer, on what the crosswalk asset contains and where its
  rights boundary sits.
- **Misuse:** treating the Tier C/D fuzzy-match candidate counts as accepted matches — they
  are unadjudicated candidates by design (full-fuzzy manufactures false joins); only P2's
  `works_crosswalk.tsv` output, once produced, is a citable join.

## Maintenance & sunset plan
- Owner: whoever next works the ACC/NCC works-catalogue asset (SanskritLexicography or
  kosha side). No dedicated maintainer assigned.
- Sunset: once P5 (release, DOI) ships and the asset is frozen, this roadmap becomes a
  historical record — retitle its status line "archived: see the release" rather than
  deleting it, since it documents the rights-resolution reasoning that a release note alone
  would not carry.

## Deprecation status
`active` — P0/P1 done, P2 blocked on a pending human decision, P3–P5 not started.

## Related documents
- [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) — the works-catalogue asset, once shipped, belongs in the Data assets table here.
- [kosha/data/SOURCES.md](https://github.com/gasyoun/kosha/blob/main/data/SOURCES.md) — the consumption-pattern precedent P3 follows.
- [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) — carries the P2 `@DECIDE`/Waiting-on-Me row.
- [docs/permissions/NCC_permission_2026-06-25.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/permissions/NCC_permission_2026-06-25.md) — the formal rights record §5 of the subject summarizes.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |

_Dr. Mārcis Gasūns_
