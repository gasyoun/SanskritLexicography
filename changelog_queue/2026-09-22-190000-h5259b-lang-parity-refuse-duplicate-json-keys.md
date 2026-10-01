_Created: 22-09-2026 · Last updated: 22-09-2026_

- H5259 follow-up: **the `LANG_PARITY.md` ledger loader now refuses a repeated JSON key instead of silently keeping the last copy.**
  The #2305 incident (7 duplicate stale-hash keys inside `headless_execution_manifest_h818.verified_sha256`,
  misreported as 8 file drifts) could recur because plain `json.loads` keeps the last value of a repeated
  key. [`lang_parity_check.parse_ledger_json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lang_parity_check.py)
  parses both ledger blocks with an `object_pairs_hook` that catches a repeat at any depth. It fails with
  one line per repeat naming the entry id, the JSON location and the key, and says it is a merge/replay
  artifact. The check, `--update-hash` (which used to collapse duplicates silently on its rewrite) and
  [`parity_restamp.load_ledger`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parity_restamp.py)
  all refuse and leave the file untouched. Replaying the #2305 ledger now names all 7 keys. The new
  hermetic `window_selftest.test_lang_parity_ledger_refuses_duplicate_keys` pin fails against the old
  checker. The 42 entries that hash `window_selftest.py` are re-stamped by
  [`h5259b_parity_restamp.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h5259b_parity_restamp.py);
  the only change there is a test-only pin, so no verdict moved.
