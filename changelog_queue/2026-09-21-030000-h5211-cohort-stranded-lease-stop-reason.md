_Created: 21-09-2026 · Last updated: 21-09-2026_

- H5211 (Opus 5 `claude-opus-5`): **a cohort wave that strands a runnable lease on resume no
  longer exits 0.** H5209's verifier found two resume states that passed every check in
  `cohort_exit_code` while an admitted, unparked lease never ran: (B) a resume that unparks
  a profile after the wave was promoted, and (C) a fully settled wave whose plan gained a
  member. `cohort_engine.run()` now records a `stop_reason` that names each such lease, with
  the cause `wave_already_promoted` or `wave_already_settled`. The shipped exit contract
  already scores any `stop_reason` as non-zero, so `bounded_staged_run.py` did not change.
  Dispatch, admission and spend paths are unchanged. New pins 11 and 12 in
  `cohort_engine_selftest` drive the real engine, (C) from a hand-crafted checkpoint. Both
  were RED against the pre-fix engine and exited 0 there. A mutation check that removes
  one half of the fix turns only that half's pin RED. Clean controls stay at exit 0, and
  H5209 case (v) plus its own-data canary stay green. The `h1437_cohort_width_offline`
  parity entry was re-derived (SHARED stands) and its hash was bumped. 0 paid calls.
