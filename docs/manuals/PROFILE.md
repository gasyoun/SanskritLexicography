# Workspace-manual profile — SanskritLexicography

_Created: 11-07-2026 · Last updated: 11-07-2026_

Per-repo overlay read by the
[/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md)
skill (Phase 0) when it generates or refreshes the manual set in this
directory. The profile **adds** to the generic procedure, never contradicts it.

## Canonical set + thin sheets

- Canonical: the four manuals in
  [docs/manuals/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals)
  plus this profile and the
  [README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md) router.
- Thin root sheets (index + hard rules only, defer here):
  [MANUAL_LEXICON_WORKSPACE_AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_AGENTS.md) ·
  [MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md).

## Subsystem deep-manual queue (each a separate Fable handoff)

The audience set above is the *orientation* layer. Subsystem *depth* is queued
as dedicated manuals, one handoff each (H604 ruling, 11-07-2026):

| Subsystem | Deep manual handoff | Status |
|---|---|---|
| [RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) (mw_ru + pwg_ru pipelines) | [H606](https://github.com/gasyoun/Uprava/blob/main/handoffs/H606-Fable_SanskritLexicography_russiantranslation-pipeline-deep-manual_11.07.26.md) | ✅ done 11-07-2026 — [RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) |
| [HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) (cross-dict analytics) | [H607](https://github.com/gasyoun/Uprava/blob/main/handoffs/H607-Fable_SanskritLexicography_headwordlists-analytics-deep-manual_11.07.26.md) | queued |
| [papers/](https://github.com/gasyoun/SanskritLexicography/tree/master/papers) + [Digital_Sanskrit_Lexicography-BOOK/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK) + [docs_site/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site) (publication pipeline) | [H608](https://github.com/gasyoun/Uprava/blob/main/handoffs/H608-Fable_SanskritLexicography_papers-book-publication-deep-manual_11.07.26.md) | ✅ done 11-07-2026 → [PUBLICATION_PIPELINE_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md) |

A finished deep manual lands as `docs/manuals/<SUBSYSTEM>_DEEP_MANUAL.md` (or
`_RU.md` per audience), gets a router row, and flips its row here to done.

## Language overrides

None — the generic default holds (RU: student + human sheet; EN: maintainer,
researcher, data-reuse, agents sheet).

## Traps that must survive every refresh

Any regeneration of the manuals MUST keep, verbatim or stronger:

- The **shared-tree rule** (worktree + PR, never direct edits, never
  `git add -A`) — H214 incident.
- The **BOM-is-inconsistent** warning + `head -c 3 | xxd` check (HeadwordLists
  exports differ file-by-file).
- The **≤3 global concurrent translation lanes** ceiling and the
  **never-relaunch-medium50-blind** gate (H317→H442 kill-gate saga).
- The **gitignored-translation-store** rights boundary (public repo,
  unpublished RU text).
- The **key1 vs key2** semantics table and the **filename-N-is-the-true-count**
  rule.
- The **stream-never-Read** list of giant root files
  (`DCS_statistical_evaluation.htm` ~75 MB etc.).

_Dr. Mārcis Gasūns_
