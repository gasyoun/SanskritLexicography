# RESEARCH_CAPABILITY_ROADMAP_2026-07-09.meta.md — metadoc for `RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md)
- **Purpose:** A 30-card, ranked research-capability programme for `pwg_ru` — turns the H335
  capability audit's four questions into falsifiable, measurable research cards (Claim / Data
  / Metric / Acceptance / Dependency flag), anchored to an ACL method spine (word alignment,
  MT/QE, bitext mining, WSD, BLI, annotation reliability, etc.).
- **Audience:** Whoever picks up the next `pwg_ru` capability-hardening card — each card is
  self-contained enough to hand to a fresh session.
- **Format / contract:** Additive to three existing docs it names as its baseline
  (`PIPELINE_CAPABILITY_AUDIT_2026-07-08.md`, `ACL_TM_CROSSWALK_MEMO.md`,
  `DECISIONS_PIPELINE_CAPABILITY_H335.md`) — never restates them. Cards are numbered and keep
  a fixed 5-field contract (Claim/Data/Metric/Acceptance/Dependency flag); new cards append,
  existing cards' numbers should not be reused if one is dropped.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`) — this metadoc. The
  subject document itself dates to 09-07-2026 per its own header (same day for created/updated
  — authored in one pass, not yet revisited).
- **Next hardening:** none scheduled — cards get picked up individually as `pwg_ru` capacity
  allows; no batch revisit planned.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Card 1 (COMET-QE calibration) — needs a frozen human A/B/C gold slice before it can run | Explicitly flagged `needs gold sample` in the card itself; blocks validating/replacing the `tm_grade.py` proxy | parked — no gold slice built yet, no handoff minted |
| 2 | Card 3 (BLI evaluation of `corpus_lexicon`) — needs a 300-item Sa→Ru gold set | Same gold-sample dependency as card 1; this roadmap and [ROADMAP_ACL_LESSONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md) B1 describe overlapping BLI-evaluation work — worth reconciling which doc owns the actual build before both are separately picked up | parked — see cross-doc overlap note below |
| 3 | This doc and `research/ROADMAP_ACL_LESSONS_2026.md` / `research/ROADMAP_CEILING_2026.md` were authored the same week (08–09-07-2026) with visibly overlapping scope (BLI, WSD, COMET-QE all appear in more than one) — a consolidation pass would prevent divergent card numbering for the same underlying work | Three near-simultaneous roadmaps in the same subsystem risk drifting out of sync as cards get picked off independently | parked — needs a human decision on which doc is canonical for BLI/WSD before consolidating |

## Known limitations / caveats
- This metadoc's author read roughly the first third of the doc (ACL method spine + cards
  1–6 of 30) — the remaining ~24 cards were not individually audited; treat the backlog above
  as a sample, not exhaustive coverage of every card's status.
- Several cards share the `needs gold sample` dependency flag and no gold sample currently
  exists per the doc's own text — most of the roadmap is blocked on that one shared
  prerequisite until a gold-annotation session runs.
- Visible overlap with `research/ROADMAP_ACL_LESSONS_2026.md`'s B1 (BLI evaluation) and
  `research/ROADMAP_CEILING_2026.md`'s C1 (in-context WSD) — this doc's cards 3–4 cover
  similar ground under different card numbering. Not yet resolved which is authoritative.

## Intended use / known misuse
- **For:** picking the next `pwg_ru` research-hardening task in priority order, with each
  card's acceptance threshold pre-defined so the work is falsifiable, not open-ended.
- **Misuse:** starting a `needs gold sample` card without first building the gold set —
  several cards are silently blocked on that shared prerequisite even though nothing in the
  doc marks them "blocked" at the top level.

## Maintenance & sunset plan
- Owner: whoever is driving `pwg_ru` research-capability work (RussianTranslation subsystem).
  No dedicated maintainer.
- Sunset: superseded once the overlap with the two `research/ROADMAP_*_2026.md` docs is
  reconciled (see backlog item 3) — at that point either this doc absorbs them or is folded
  into whichever survives as canonical.

## Deprecation status
`active` — cards not yet individually triaged as done/in-progress/blocked at the doc level.

## Related documents
- [ROADMAP_ACL_LESSONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md) — overlapping BLI/WSD scope, see backlog item 3.
- [ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md) — overlapping WSD scope, see backlog item 3.
- [REVIEW_AND_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md) — the higher-level `pwg_ru` build retrospective and phase plan this roadmap's cards feed into.
- [RussianTranslation/PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) — required prior reading before touching `pwg_ru` code, per the repo's own CLAUDE.md.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |

_Dr. Mārcis Gasūns_
