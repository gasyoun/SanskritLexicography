_Created: 05-09-2026 · Last updated: 05-09-2026_

- H4055: **a content-only mirror sync is no longer byte-shaped like a no-op.** The
  [refresh_tm_mirror.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/refresh_tm_mirror.py)
  ledger row (and a new `--receipt FILE` durable copy) now carries the content view beside
  the existing row-set counters — `src_sha256`, `noop`, `shared_ids`/`ru_equal`/
  `changed_ru` and capped `changed_ru_keys` (semantic row identity = the shared
  `rid()` = `key1|subcard|sense_tag|de[:80]`, identical to `audit_store_gates.diff_stores`).
  The H3751 refresh of 31-08 was the live demonstration of the defect: every row counter 0,
  yet `mirror_sha 3022239c63ac → 58c2172607c3` — nothing in the receipt could say why.
  The copy itself now goes through
  [`store_write.locked_store_rewrite`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_write.py)
  (PromoteClaim + unique fsynced backup + atomic replace) as raw-line passthrough, verified
  **byte-identical to src after the write** (any drift restores the backup and raises) — the
  mirror stays a straight copy, never a re-serialization. Selftest 17 → 35/35: the two
  acceptance fixtures (content-only update and byte-identical no-op, both with all-zero
  row-set counters) now separate on `changed_ru` 1 vs 0 and on sha movement; proven by
  [h4055_store_lineage_evidence.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4055_store_lineage_evidence.py)
  with durable receipts
  ([content-only](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4055_receipt_content_only.json),
  [no-op](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4055_receipt_noop.json)).
  The src/mirror/box evidence matrix
  ([json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4055_store_mirror_box_matrix.json),
  [md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4055_store_mirror_box_matrix.md))
  records the 04/05-09 state: Mac store **MISSING** (gitignored, per-box — the explicit
  missing-box state), mirror hydrated sha256 = H3947 ledger `mirror_sha_after` = LFS pointer
  oid `79d72dbcb4b3…` at [pwg-ru-data `2c4f770`](https://github.com/gasyoun/pwg-ru-data/commit/2c4f770642bd1c9f766d6bb63de5636ca855fdbf)
  (pointer ≠ bytes; all three agree), Windows-box observations UNAVAILABLE, cross-box
  equality NOT ASSERTED, row counts (11,462 / 11,519) recorded as historical sizes, never
  lineage. Zero provider calls; live mirror not refreshed (02-09 already synchronized,
  `only_src=0 only_mirror=0 changed_ru=0` re-evidenced by the hash chain); canonical store
  untouched; real ledger untouched.

_Dr. Mārcis Gasūns_
