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

1. 🟡 Subsystem deep manuals per the
   [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
   queue — H606 (RussianTranslation) ✅ done 11-07-2026
   ([RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md));
   H607 (HeadwordLists), H608 (papers/book/docs_site) still queued.
2. ⬜ Refresh the dated state snapshots (AGENTS §4, HUMAN_RU §3–4) on the next
   monthly pass — they are staleness-prone by design; verify against
   `.ai_state.md` first.
3. ⬜ Consider an external-contributor manual (how to submit corrections
   upstream) once the Cologne batched-PR cadence stabilizes.
4. ⬜ FINDINGS.md carries seven accidentally duplicated `§N` pairs
   (§56, §60, §62–65, §69 — H604 fact-check, 11-07-2026): repair by renaming
   the *later* twin of each pair to a fresh number and leaving a tombstone
   note, then drop the caveat lines from MAINTAINER §3 / RESEARCHER §5.

## Known limitations

- State snapshots inside the manuals date fast; the disclaimer ("verify
  against .ai_state before trusting") is the mitigation, not a fix.
- STUDENT_MANUAL_RU §1 depends on gitignored ReverseDictionary data files a
  clone does not contain — flagged inline.

## Revision history

| Date | Change | Session |
|---|---|---|
| 10-07-2026 | Set created (4 manuals + router + root pair) | H479/H535 |
| 11-07-2026 | H604 consolidation (see Provenance) | H604 |
| 11-07-2026 | RUSSIANTRANSLATION_DEEP_MANUAL.md added (first subsystem deep manual: mw_ru post-mortem + pwg_ru operator depth); router row + PROFILE queue flip | H606 |

_Dr. Mārcis Gasūns_
