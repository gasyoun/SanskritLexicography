# Metadoc — H960_FOUR_PROFILE_PRODUCTION_READINESS_GATE_2026-07-15.md

_Created: 15-07-2026 · Last updated: 15-07-2026_

- **Purpose.** The GO/NO-GO record for H960: verify H920 and earn four-profile nonstop PWG-RU scale.
  Documents what was earned offline (six load-bearing gaps closed as soft/report-only guards + the
  economy ledger + four-profile scheduler + bounded supervisor) and the single residual NO-GO (the
  owner-gated live auth→latency→canary→arm→10→20→multi-profile ladder).
- **Audience.** The owner (M.G.) deciding whether to run the live ladder; any future session picking up
  PWG-RU scale or arming the soft guards.
- **Provenance.** Handoff [H960](https://github.com/gasyoun/Uprava/blob/main/handoffs/H960-Opus_SanskritLexicography_pwg-ru-four-profile-production-readiness_15.07.26.md)
  (a stub; the real mission was reconstructed from the post-H920 Codex audit recorded in
  `.ai_state.md` #474 and the [H911 gate](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md)).
  Executor Opus 4.8 (`claude-opus-4-8[1m]`), Ultracode. Built with a deep parallel gap-audit workflow
  (adversarially verified) + parallel implementation of the file-disjoint gaps + a correctness-review pass.
- **Improvement backlog (ranked).**
  1. Run the live ladder (owner) → replace the NO-GO with a measured verdict.
  2. After a live canary measures the false-flag rate, arm `SANLOSS_HARD_REJECT` / `TNMASK_HARD_REJECT`
     and promote `dropped_sanskrit_span` to a requeue trigger.
  3. Delegate `max_account_orchestrator.cmd_staged_run` to `bounded_supervisor` with the live
     `run_window` seam (makes the tested loop the shipping loop).
  4. Bless the `economy_ledger` ceilings (calls/clean ≤ 1.75, $/clean ≤ 0.75) from calibrated data.
- **Limitations.** Soft-only (no live quality-rate improvement claimed); `$/clean` is a bounded band;
  bounded_supervisor is a parallel module not yet wired to live generation.
- **Revision history.** 15-07-2026 — created with the H960 offline deliverable (Opus 4.8, Ultracode).

_Dr. Mārcis Gasūns_
