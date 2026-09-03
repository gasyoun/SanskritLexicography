- H3982: **forward pwg_ru provenance — the GAPS §19 hole can no longer grow.**
  `pipeline_version.stamp()`, the single chokepoint every newly written store row
  passes through, now (a) archives each component's file SET to a content-addressed
  write-once blob store keyed on the same 16-hex `component_sha` it already records,
  and (b) stamps `source_commit` + `worktree_dirty` (+ `dirty_component_sha`) beside
  the existing `<name>_version`/`<name>_sha`. Runs against an uncommitted working tree
  — the measured root cause of the 10,773-row loss — stay legal but can no longer hide,
  and every future `*_sha` expands back into real bytes instead of resolving to nothing.
  Implements [SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md)
  §2.3 only; the era-A ruling, the ledger and the `provenance_class` write remain
  design-only and unauthorized, and **not one existing row was touched** (store
  byte-identical to its last commit, `changed_ru=0`).
  The archive resolves like [`store_path.canonical_store()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py)
  (`$PWG_RU_BLOB_DIR` → canonical main checkout → local): a worktree-local archive would
  die with the worktree while the rows it explains survive in the shared store — the H255
  loss mode one layer down, i.e. the "hash that resolves to nothing" this work exists to
  prevent. Contract: [`reports/pipeline_blobs/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pipeline_blobs/README.md).
  Proven by [`src/canary_forward_provenance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/canary_forward_provenance.py),
  which drives the real `promote_final_cards.py` CLI against a deliberately dirty tree
  into a scratch store — `worktree_dirty: true`, `dirty_component_sha 3a3275488183cea4`,
  all three recorded component hashes resolvable, `forward_unresolved: []`
  ([evidence](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3982_CANARY_FORWARD_PROVENANCE_03-09-2026.json)).
  Spec field `source_worktree_dirty` shipped as **`worktree_dirty`** — H3982's acceptance
  wording is the later document and the operative lock; the spec records the supersession.
  New `pipeline_version.py blobs` reports per-era coverage and exits 1 on an unresolved
  *forward* hash, never blaming pre-H3982 rows for a gap they predate.
