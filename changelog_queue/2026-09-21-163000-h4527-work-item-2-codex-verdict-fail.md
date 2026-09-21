_Created: 21-09-2026 · Last updated: 21-09-2026_

- H4527: **work item 2 ran, and the Codex reviewer returned FAIL.** Codex `gpt-5.6-sol`
  ran read-only on MSI (session `01a0c4ac-fbca-7103-a164-7ca779101aa0`, `origin/master`
  `28beaa4ac`). It confirmed the 20-09 run's identity, the live cohort route, the 1 == 1
  accounting, the single promote and TM callback, that no gate was bypassed, and the
  width-1 `["c1"]` record envelope. It failed the sign-off on one point:
  `byte_identical_to_serial: true` overclaims. The live receipt compares file sets and
  schemas, not bytes; the byte proof is H1437's offline simulation; and the raw compare
  inputs and the canary receipt were never retained. The verdict is recorded verbatim in
  `pwg_ru/h4527/H4527_WORK_ITEM_2_CODEX_VERDICT_FAIL_21-09-2026.md`.
  `COHORT_LIVE_ACCEPTANCE.json` stays unwritten, and width 2 stays fail-closed.
  0 paid PWG calls.
