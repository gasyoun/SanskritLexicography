# H7228 — record-boundary attribution: method note

_Created: 28-10-2026 · Handoff: [H7228](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7228-DeepSeek_SanskritLexicography_h7223-record-boundary-parser_23.10.26.md) · Supersedes the v1 (`-U6`) method of [H7223](COLOGNE_YEARLY_ENTRY_CENSUS_2026-10-22.md) · Data pin unchanged: csl-orig `55e8addb` (26-09-2026)_

## The v1 failure mode

The v1 parser attributed each added line to the nearest preceding `<L>` header **visible in the
same `-U6` hunk**. A hunk whose six context lines never reach an `<L>` — a correction deep inside a
long record, or a scattered rewrite — left the line unattributed: 277,536 added lines (5.88%) landed
in a counted residual bucket. The residual was honest but large; the fix is to stop asking "what
record is near this hunk" and ask "what record owns this **line**".

## The v2 algorithm (record-boundary attribution)

One streaming pass, same source, same axes:

1. **Stream.** `git log --no-color --date=short --reverse --topo-order --full-index -p -U0
   --pretty=format:\x01%H\x01%ad\x01%s <pin> -- v02` — oldest-first, context-free (`-U0`), with full
   blob hashes. Context lines are not needed: the parser *reconstructs* the file instead of sampling
   a window around the change.
2. **Post-image state.** For every changed file the parser keeps the current post-image as two
   parallel per-line arrays: `ids[i]` = index of the `<L>` occurrence owning line *i* (−1 outside any
   record) and `kinds[i]` ∈ {normal, header, `<LEND>`}. A line inherits the owner of the line above
   unless it *is* an `<L>` (opens a record, allocates a headword entry) or a `<LEND>` (closes it).
   Headword entries are interned per distinct `(L-id, headword)` pair, so blob resyncs of unchanged
   records reuse entries instead of growing the table (an empty headword is never interned, keeping
   v1's late-`<k1>` patch per-occurrence).
3. **Apply each hunk** to the state. Git's hunk positions are **pre-image** line numbers, while the
   carried state accumulates the hunks applied before: a hunk deletes `b` entries at
   `a − 1 + Δ` (insertion point `a + Δ` when `b = 0`), where Δ is the net line delta of the earlier
   hunks of the same file diff. The state is verified against the `index` line's pre-image blob SHA
   **once per file diff** (rebuilding via `git cat-file` on first sight or on merge/rename drift);
   re-verifying per hunk would reset the state to the pre-image between hunks and corrupt both the
   reconstruction and the attribution — the failure mode the extended `--selftest` fixture pins.
4. **Tail repair.** A structural insert/delete can change which record owns the *unchanged* lines
   after the hunk (e.g. an added `<LEND>` cuts a record early). The segment from the hunk's end to
   the next `<L>` header is re-assigned from the last line before it; membership past the next
   header is provably unaffected, so the repair stops there.
5. **Blob pinning.** `--full-index` reports the pre-image blob SHA of every file diff. The carried
   state is checked against it **once per file diff**; on mismatch (first sight of a path,
   merge/reorder drift, rename) the state is resynced by `git cat-file` of that one blob — so the
   reconstruction is correct under any commit ordering, including the 46 v02-touching merge commits.
6. **Attribution.** An added `<L>` header line ⇒ **add** row for that `(dict, L)`; an added non-blank
   content line with owner ≥ 0 ⇒ **mod** row for that record; blank and `<LEND>` lines attribute
   nothing; an added non-blank line with owner −1 (outside every record: file preamble, `<H>` section
   markup, appendix blocks without `<L>` structure) is **counted as residual, never dropped**.
7. **Unchanged from v1:** dedupe per `(commit, dict, L)`; `dc_year` = DC date from the commit subject,
   falling back to the commit year; row schema
   `dc_year, dict, L, headword, kind, issue, commit, commit_date`; deterministic sort + gzip
   (`mtime=0`).

## Why the checks are independent of the parser

`--check` re-runs the pass and demands byte-identical output, then prints four canaries that do not
consult the parser's internals: (1) distinct `(dict, L)` pairs vs the H7223 figure, (2) 2019
additions vs the H7223 figure, (3) per-year commit sets vs the H7223 figure, and (4) presence of the
hand spot-check file, whose rows were verified against `git show <sha>` itself — the source of truth,
not the parser.

## Residual classes (named)

Lines outside every `<L>…<LEND>` span are classified, not guessed:

- `markup-outside-record` — structural lines starting with `<` outside any record (`<H>` section
  heads, `<H>` page headers, file tail markers).
- `text-outside-record` — non-markup lines outside any record (appendix/headword-extra blocks that
  the source never wrapped in `<L>` structure).

Both classes are *real structure of the source files*, not parser misses: no record exists to
attribute them to. The per-file concentration is printed by every run (the bulk sits in a small set
of `_hwextra`/appendix files), and the totals appear in the report's residual line.