_Created: 03-09-2026 · Last updated: 03-09-2026_

# `pipeline_blobs/` — the bytes behind every recorded `<name>_sha`

This directory is the content-addressed **component blob archive** specified in
[SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md)
§2.3 item 2 and implemented by H3982. It exists so that
[GAPS §19](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) — 10,773
pwg_ru rows whose producing prompt, glossary and script bytes are gone — **cannot grow**.

## The contract

- One file per distinct component state: `<component_sha>.zip`, where `<component_sha>`
  is the same 16-hex value already written into `provenance.pipeline.<name>_sha` by
  [`src/pipeline_version.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_version.py).
  Resolving a hash is therefore a plain file lookup, never a search.
- Each zip holds the component's whole file SET at repo-relative paths, plus a
  `.blobmeta.json` (`schema: pwg_ru.pipeline_blob.v1`, the `component_sha`, the sorted
  file list). Entries are written with a fixed timestamp `(1980,1,1,0,0,0)` and mode
  `0o644` so the archive is **deterministic**.
- **Write-once.** An existing `<sha>.zip` is never rewritten; a new component state
  produces a new file and never evicts an old one. Writes go to a pid-suffixed `.tmp`
  and land via `os.replace`, so a killed run leaves no half-zip behind a valid name.
- The archive is written by `pipeline_version.stamp()` at the moment the hash is
  computed — the one chokepoint every newly written store row passes through.

## Where it lives

Resolved exactly the way
[`store_path.canonical_store()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py)
resolves the store, and for the same reason: `$PWG_RU_BLOB_DIR` → the **canonical main
checkout's** `RussianTranslation/reports/pipeline_blobs` → local. A hash written into the
canonical store must resolve on the machine holding that store; an archive under a
throwaway session worktree would be deleted with the worktree while the rows it explains
survive — the H255 loss mode one layer down, i.e. the very "hash that resolves to nothing"
this work exists to prevent. `$PWG_RU_BLOB_DIR` pins a directory for tests and
deliberately isolated runs, as `$PWG_RU_TM_DIR` does for sidecars.

## Why the zips are gitignored

They are runtime data in the same sense as the pwg_ru store itself (`src/*.jsonl` is
likewise ignored): ~300 KB per distinct state, dominated by the glossary set. Committing
them would be near-duplicate storage of bytes git *already has* for every committed state,
while the archive's unique and irreplaceable content is precisely the states git never had
— runs against an uncommitted working tree, which are exactly what §2.3 item 1 records via
`worktree_dirty`. This README is the committed half of the contract; the blobs are the
local half, and they must not be deleted casually.

## Inspecting it

```sh
python src/pipeline_version.py blobs                  # list the archive
python src/pipeline_version.py blobs --store <store>  # coverage; exit 1 on an unresolved forward hash
python src/pipeline_version.py blobs <sha> --extract <dir>
```

Coverage is reported per era: rows stamped by the forward path (`source_commit` present)
**must** resolve 100 %; pre-H3982 rows are counted and never blamed.

_Dr. Mārcis Gasūns_
