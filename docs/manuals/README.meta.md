# Metadoc — the SanskritLexicography manual set

_Created: 11-07-2026 · Last updated: 11-07-2026_

Companion record for the audience-manual set in
[docs/manuals/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals)
(the four manuals + [README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md)
router + [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md))
and its two thin root sheets.

## Purpose & audience

Orientation layer for five audiences (maintainer, researcher, student,
data-reuser, agents) + the human owner over a ~12-subproject hybrid
data/research workspace. Canonical-vs-thin split: depth in `docs/manuals/`,
index/hard-rules at root.

## Provenance

- **H479 / H535** (10-07-2026, Fable 5 `claude-fable-5` / Opus 4.8
  `claude-opus-4-8`) — initial quartet + root pair.
- **H604** (11-07-2026, Fable 5 `claude-fable-5`) — consolidation: canonical
  ruling (docs/manuals wins), root pair cross-wired + thinned (multi-account
  protocol de-duplicated into AGENTS §5), stale CLAUDE.md-framing and CI
  claims fixed, PROFILE.md + this metadoc added; regeneration procedure
  encoded in [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md).

## Improvement backlog (ranked)

1. ✅ Subsystem deep manuals per the
   [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
   queue — all three shipped 11-07-2026: H606
   ([RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)),
   H607
   ([HEADWORDLISTS_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md)),
   H608
   ([PUBLICATION_PIPELINE_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md)).
2. ⬜ Refresh the dated state snapshots (AGENTS §4, HUMAN_RU §3–4) on the next
   monthly pass — they are staleness-prone by design; verify against
   `.ai_state.md` first.
3. ⬜ Consider an external-contributor manual (how to submit corrections
   upstream) once the Cologne batched-PR cadence stabilizes.
4. ✅ FINDINGS.md carried seven accidentally duplicated `§N` pairs
   (§56, §60, §62–65, §69 — H604 fact-check, 11-07-2026). Repaired 11-07-2026
   (H616): later twins renumbered §70–§75 with tombstone notes (the later
   "§56" was a verbatim copy of §68 and was removed), stale citations
   repointed, caveat lines dropped from MAINTAINER §3 / RESEARCHER §5.

## Known limitations

- State snapshots inside the manuals date fast; the disclaimer ("verify
  against .ai_state before trusting") is the mitigation, not a fix.
- STUDENT_MANUAL_RU §1 depends on gitignored ReverseDictionary data files a
  clone does not contain — flagged inline.

## Intended use / known misuse

**Intended use:** the entry point an agent or human reads at session start (or when
onboarding a new contributor) to pick the right depth for their role — maintainer,
researcher, student, data-reuser, or agent — before touching the ~12-subproject
workspace; the four manuals + [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
route deep-dives, the root pair stays thin/index-only.

**Known misuse:**
- Trusting the dated state snapshots (AGENTS §4, HUMAN_RU §3–4) as currently accurate
  without cross-checking `.ai_state.md` first — they are staleness-prone by design (see
  Known limitations below and backlog item 2).
- Using STUDENT_MANUAL_RU §1 without the gitignored ReverseDictionary data files present
  in the clone — the section assumes data that a bare clone does not contain.
- Treating a subsystem deep manual as a substitute for reading the actual subsystem code
  or its own docs — the deep manuals summarize and post-mortem, they are not exhaustive
  specs.
- Using this set as an external-contributor "how to submit a correction upstream" guide —
  that manual does not exist yet (backlog item 3); external submitters should be pointed
  elsewhere until it ships.

## Maintenance & sunset plan

Regenerated via the [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md)
skill whenever a new subsystem deep manual is added or the router/PROFILE queue changes
(as in H606/H607/H608 below). State snapshots (AGENTS §4, HUMAN_RU §3–4) are due a refresh
on the next monthly pass against `.ai_state.md` (backlog item 2) — no automated staleness
check exists yet. Owned by whichever session is actively driving workspace-manual work;
no fixed cadence beyond "monthly-ish" for the snapshot refresh.

## Deprecation status

`active`

## Revision history

| Date | Change | Session |
|---|---|---|
| 10-07-2026 | Set created (4 manuals + router + root pair) | H479/H535 |
| 11-07-2026 | H604 consolidation (see Provenance) | H604 |
| 11-07-2026 | FINDINGS duplicate-§N caveat dropped from MAINTAINER §3 / RESEARCHER §5 after the H616 key repair; backlog item 4 closed | H616 |
| 11-07-2026 | RUSSIANTRANSLATION_DEEP_MANUAL.md added (first subsystem deep manual: mw_ru post-mortem + pwg_ru operator depth); router row + PROFILE queue flip | H606 |
| 11-07-2026 | [PUBLICATION_PIPELINE_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md) added (papers · M01 book · docs_site) + router row + PROFILE queue flip — Fable 5 (`claude-fable-5`) | H608 |
| 11-07-2026 | HEADWORDLISTS_DEEP_MANUAL.md added (queue complete); router gains a "Subsystem deep manuals" table; PROFILE H607 row flipped done; backlog item 1 closed — Fable 5 `claude-fable-5` | H607 |
| 11-07-2026 | template v2 backfill (H663) | Sonnet 5 (claude-sonnet-5) |

_Dr. Mārcis Gasūns_
