# SIGNOFF A40 — author-voice pass on "HeadwordLists — now (2026) vs then (2014)"

_Created: 06-09-2026 · Last updated: 06-09-2026_

Scope: the manuscript [HeadwordLists/NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md), pass 1, under handoff [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md), executed by Fable 5.1 (`claude-fable-5-1`) on 06-09-2026. Voice, register and framing only; no number, claim or citation altered; mechanical drift gate CLEAN (numbers 339/339, URLs 28/28, citations 30/30, headings 23/23, table rows 29/29, run with [tools/voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against `origin/master`). The manuscript is a data note (one comparison table, a legend, four use cases and the per-list removed-headword excerpts), so the pass was light: the prose is under 500 words and every data line was left byte-identical.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Header | `Last updated` bumped 05-09-2026 → 06-09-2026 | Dated-header rule; no status paragraph exists, so no pass note was added elsewhere. |
| 2 | Under the H1 | Added the academic byline line `Mārcis Gasūns, independent scholar (ORCID 0000-0003-4513-884X), gasyoun@ya.ru` | The note carried only the closing `_Dr. Mārcis Gasūns_`; the paper byline block was absent. Delete the line if the note is meant to stay a repo README rather than a citable data note. |
| 3 | Intro, sentence 2 | "This compares each against the current csl-orig" → "Here I compare each against the current csl-orig" | Agentless "this compares" hid the author; first-person singular is the standing voice. Nothing else in the sentence changed. |
| 4 | Legend, `format-migrated` bullet | dropped the bold on "**not** a real headword change" | Decorative emphasis; the sentence already says it. |
| 5 | Legend, `format-migrated` bullet | "can't be line-diffed" → "cannot be line-diffed" | Register: the only contraction in the note. |
| 6 | Use case 1 | dropped the bold on "key1 **and** key2" | Bold-every-other-word; the "and" carries no contrast that needs marking. |
| 7 | Use case 2 label | "**`removed` = a data-loss / correction audit.**" → "**`removed` as a data-loss / correction audit.**" | The "=" was telegram syntax standing in for a verb; the other three labels are noun phrases, so this one now matches them. |
| 8 | Use case 3 | "carries the **current key2 as clean SLP1** (the print/citation form — keeps `/` accent, `-`, `(...)`)" → "carries the current key2 as clean SLP1 (the print/citation form, which keeps the `/` accent, `-` and `(...)`)" | Dropped the decorative bold; the parenthesis had a dropped subject ("— keeps") and an em dash doing the work of a clause. The three kept tokens are unchanged. |
| 9 | Use case 4 | "has evolved — useful for citation and for deciding" → "has evolved, and they are useful for citation and for deciding" | Em-dash-as-copula; the dash hid the subject of "useful". |

Calls deliberately not made: "drifted hard" in use case 1 is colloquial but is a magnitude word attached to a measured effect, so it stays; the legend's "**comparable** — …" / "**format-migrated** — …" pattern is a definition list, where the dash is conventional; the relative links `then-2014/`, `now-2026/`, `_diff/` are URLs and were not touched (the full-URL rule was applied to this signoff only).

## 2. Substance flags carried (not fixed)

1. **Filename count vs. table "then" column.** The intro states that the filename count `N` "is its line count when extracted", but the table disagrees for four rows: AP-unique-key2-36704 has then = 36126, MD-unique-key2-20748 has then = 20108, PD-unique-key1-104936 has then = 104935, VEI-unique-key1 and others match. Either the intro should say "line count, before de-duplication" (or whatever the difference is) or the rows should be explained. Not changed.
2. **"~100 %" for format-migrated lists.** The legend says the raw then-vs-now diff for format-migrated lists is "~100 %", yet the table shows overlap 44.5 % / 44.4 % for the two MW key2 rows and 19.4 % for SCH, i.e. a raw diff nearer 55 % and 80 %. Only BHS (9.7 %), GRA key2 (6.1 %) and VEI key2 (0.0 %) fit "~100 %". The sentence overstates; a human should decide whether to reword the legend or explain why MW's numeric-transliteration keys half-overlap SLP1.
3. **Two MW key2 snapshots.** MW-unique-key2-198220 and MW-unique-key2-198231 both appear (then 198220 and 198231); the note never says why two 2014 key2 snapshots of MW exist or which one is canonical. Both are counted in the grand total of 26 snapshots.
4. **PD entry count.** The PD bullet says the SanskritSpellCheck digitization has "107,630 tagged entries, matching the then-2014 extraction size exactly", but the PD then-2014 rows carry 104935 / 104941. The three figures cannot all be exact matches of one another; the "exactly" needs a referent (raw entries vs. unique keys?).
5. **Internal handoff reference.** "(H1365, 20-07-2026)" in the PD bullet is an org-internal handoff id, meaningless to an outside reader; keep for the repo, drop or expand for any external version.
6. **Totals verified, no action.** Recomputed from the table: 20 comparable rows, then 1264957, now 1416311, added 172827, removed 21473, growth +11.96 % → "+12.0 %"; grand total of 26 then-counts 1721983; the MD (45) and VEI (17) removed lists match their row counts. All as stated.
7. **Reproducibility path.** The link to `headword_diff.py` is a full blob URL, but the `_diff/` outputs the text repeatedly points to are described as landing locally; if `_diff/` is gitignored, a reader cannot follow "full list in `_diff/`". Not checked here (shallow clone, no history probe).

## 3. Read-and-sign

About 30 minutes: read the intro and legend against flags 1, 2 and 4 (the three places where the prose and the table disagree on a number), then skim the nine voice calls. Proposed readiness after that read: 3/5 (propose only; the numeric inconsistencies in flags 1, 2 and 4 are what keep it below 4). Venue: this is a repository data note rather than a journal paper; if it is to be cited, a Zenodo/data-release wrapper of `now-2026/` with this note as README is the natural venue (recommendation only).

_Dr. Mārcis Gasūns_
