_Created: 21-09-2026 · Last updated: 21-09-2026_

- H4527: **work item 2 reviewer brief. The Codex review did not run, and the 20-09 packet's
  paste-ready acceptance record was invalid.** The read-only Codex reviewer launch died on
  the account usage limit before its first tool call, so no verdict exists and nothing was
  written. The 20-09 record object fails `cohort_live_admission.validate_record` even with a
  PASS review, because it has no `admitted_profiles`, and width 2 cannot validate on the
  one-profile `c1` fleet. The only valid record today is `max_admitted_width: 1` on
  `["c1"]`. The new
  `pwg_ru/h4527/H4527_WORK_ITEM_2_CODEX_REVIEWER_BRIEF_21-09-2026.md` carries the corrected
  shape, the validator probe table and a self-contained Codex brief (checks A–F).
  `COHORT_LIVE_ACCEPTANCE.json` stays unwritten, and width 2 stays fail-closed.
  0 paid calls.
