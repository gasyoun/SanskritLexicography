_Created: 22-09-2026 · Last updated: 22-09-2026_

- H5259: **master is green again: duplicate stale-hash keys removed from `LANG_PARITY.md`, and FINDINGS §643/§644 are indexed.**
  The recovered PR #2305 (H4530) replayed its old re-hash hunk on a newer base. That appended 7 duplicate
  keys with stale hashes inside `headless_execution_manifest_h818.verified_sha256`, and because a JSON parse
  keeps the last key, the stale values overrode the correct ones. The required RussianTranslation gate then
  reported 8 parity violations. `--update-hash` collapsed the duplicates. The one real drift,
  `no_pwg_scale_plan.py` (H4530's `used_window_indices` now also scans coordinator and dry-run artifact
  directory names), was re-verified as still SHARED for both `headless_execution_manifest_h818` (it reads
  no dictionary text) and `no_pwg_sense_gate_h4527` (the admission code is untouched). The offline
  `test_epistemic_check_on_the_live_registries` pin was red because §643 (#2298, H4800) and §644 (#2299,
  kosha #592) had no Index rows; both rows are now added. #2303 and #2304 were not causes.
