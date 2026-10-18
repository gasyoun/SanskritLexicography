_Created: 22-09-2026 · Last updated: 22-09-2026_

- H4527: **`kast_ur_i`'s defect requeue is prepared, and the redo run is waiting on a driver change.**
  A human ruled to retry `kast_ur_i` and to re-make the GLM-made `darv_i` card on Anthropic in the same
  run. `coordinator.py prepare-requeue h4527vol14 --defect` built attempt `rq01-defect` (1 card) and
  appended the intended `blocked` row for the key to `no_pwg_residuals.jsonl` (landed here
  byte-identical). A zero-call dry run then showed that `bounded_staged_run.py` cannot run either card:
  it imports no `requeue_prepared` lease (a requeue runs only as an in-run serial supervisor item, and the
  cohort engine only records its backlog), and no plan window can point it at a `defect-repair` lease for
  an already-promoted card. Running the harness directly would skip the probe ration, the canary receipt
  and the call cap, so it was not done. The store side is already safe: `merge_store_rows` is
  better-attempt-wins, and the three `darv_i` rows are `ai_translated` with no reviewer. 0 paid calls.
