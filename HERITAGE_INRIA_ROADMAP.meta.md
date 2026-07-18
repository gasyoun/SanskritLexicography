# HERITAGE_INRIA_ROADMAP.meta.md — metadoc for `HERITAGE_INRIA_ROADMAP.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md)
- **Purpose:** Tracks reuse of Gérard Huet's Sanskrit Heritage Platform (sanskrit.inria.fr) —
  access reality (bot-walled site, GitHub mirror), the LGPLLR×BY-SA rights resolution, and a
  6-phase integration plan (morphology databanks, MW↔Heritage crosswalk, frequency tables,
  DICO gloss layer, segmenter service).
- **Audience:** Sessions touching Heritage-derived assets in kosha, HeadwordLists, csl-atlas,
  or SanskritSpellCheck; anyone re-checking the Huet outreach/rights status.
- **Format / contract:** Numbered phases (0–6) each with consumer/gate/status columns; a
  rulings section; an execution log pointing at the handoffs that did the work. Status cells
  update in place as phases land.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`).
- **Next hardening:** none scheduled — revisit when Phase 3 (frequency tables) or Phase 6
  (segmenter-as-service) is picked up.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Phase 3 — ingest `DATA/*.tsv` pada/compound/transition frequencies, diff against VisualDCS M1–M8 and `corpus_lexicon`, register in PROJECT_INTERLINKS | Explicitly queued in the subject ("⬜ queued, own H###") — cheapest remaining phase, mirror-only, no gate | parked — needs its own H### mint when picked up |
| 2 | Phase 6 — segmenter-as-service cross-validation vs DharmaMitra GPU morphology | Queued in the subject; unlocks a second morphology witness for csl-atlas/RussianTranslation | parked — needs its own H### mint when picked up |
| 3 | Transcribe Gérard Huet's exact reply wording (attribution phrasing, conditions) into this repo | Subject flags this explicitly as "not transcribed into this repo yet" — a rights-precision gap | parked — needs the actual email text located first |
| 4 | kosha ingest of Heritage's 928k surplus forms (flagged as Phase 4 follow-on, explicitly "not built") | Left as a GTD `@DECIDE`, not built, per the subject's own phase-4 row | parked — MG `@DECIDE`, tracked in GTD |

## Known limitations / caveats
- The current morphology XML databanks are **not** in the GitHub mirror — they require either
  a manual browser download (past the Anubis bot-wall) or a local Platform install; Phase 1's
  "done" status is explicitly the mirror-fallback path, not the human-downloaded export.
- `DATA/mw_index.rem` (OCaml `Marshal` binary) was never decoded and is out of scope per the
  subject's own inventory note.
- Phase 4's 78.3% agreement figure between Heritage and kosha forms is measured against a
  small raw overlap (94,264 of ~1M+410k forms); most of that low overlap is attributed to
  engine-surplus and lemmatization-policy differences, not error — don't over-read it as a
  precision number without re-reading the hand-adjudication note in the subject.

## Intended use / known misuse
- **For:** checking rights status before using any Heritage-derived asset, and finding which
  phase (if any) already covers a given Heritage integration need before rebuilding it.
- **Misuse:** treating "Phases 1–5 done" as "everything from Heritage is ingested" — several
  explicit follow-ons (kosha surfacing, kosha ingest of surplus forms) are flagged done-but-
  not-built and sit as GTD `@DECIDE` rows, not completed work.

## Maintenance & sunset plan
- Owner: whoever next works Heritage-derived data (SanskritLexicography/HeadwordLists side).
  No dedicated maintainer assigned.
- Sunset: once Phases 3 and 6 land (or are explicitly deprioritized), this roadmap is fully
  executed and becomes a historical record of the integration — retitle rather than delete,
  since it also documents the LGPLLR×BY-SA rights ruling other sessions may need to cite.

## Deprecation status
`active` — Phases 0–2, 4–5 done; Phases 3 and 6 queued with no handoff minted yet.

## Related documents
- [SAMSAADHANII_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/SAMSAADHANII_INDEX.md) — companion external-stack roadmap (the SCL side, first mature external computational-Sanskrit stack).
- [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — §41 (Anubis bot-wall), §47 (GitLab also walled), §49/§52/§54 (execution findings) referenced throughout the subject.
- [HeadwordLists/HERITAGE_MIRROR_INVENTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/HERITAGE_MIRROR_INVENTORY.md) — the mirror contents inventory.
- [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) — carries the kosha-ingest `@DECIDE`.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |

_Dr. Mārcis Gasūns_
