_Created: 22-09-2026 · Last updated: 22-09-2026_

- H5259 follow-up c: **the `LANG_PARITY.md` ledger loader now refuses two entries sharing one `id`, and a second ledger fence.**
  The duplicate-key refusal (H5259b) could not see a merge/replay that re-appends a WHOLE entry: no key
  repeats inside either copy, yet `check()` evaluated both (the stale one reads as drift) and
  `--update-hash` re-stamped every match, so the duplicate persisted silently.
  [`lang_parity_check.parse_ledger_json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lang_parity_check.py)
  now raises `DuplicateKeyError` naming each repeated id and its list positions as a merge/replay artifact
  (ledger block only; the coverage map is untouched). `load_ledger` and
  [`parity_restamp.load_ledger`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parity_restamp.py)
  also refuse a second ```` ```json lang_parity_ledger ```` fence, which was never read past the first.
  The real ledger has 117 entries, no repeated id, one fence. The new hermetic
  `window_selftest.test_lang_parity_ledger_refuses_duplicate_entry_ids` pin fails against the old checker;
  the 42 entries hashing `window_selftest.py` are re-stamped by
  [`h5259c_parity_restamp.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h5259c_parity_restamp.py)
  (test-only pin, no verdict moved).
