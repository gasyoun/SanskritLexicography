Closes the resume of [H4436](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4436-Fable_SanskritLexicography_pwg-ru-automation-config-dir-isolation_09.09.26.md) (Fable 5.1, 🔴3 hard) — pwg_ru readiness probe/production calls no longer certified under the operator's full interactive profile.

**What the handoff asked vs what shipped.** The mission proposed a second `CLAUDE_CONFIG_DIR` holding c1's credentials without hooks. H2189 (03-08-2026) had already measured that option against the CLI's `--safe-mode` flag and ruled for the flag (a second profile = a second on-disk OAuth token + a second `ActiveCallClaim` fingerprint billing one account). H4527 (#2229, #2238) landed the flag on `_probe_call` on 15-09. This PR supplies the paid reading no offline test substitutes for, and closes the last unflagged paid spawn in the module.

**Live reading (acceptance #3), 16-09-2026 02:46Z, `h963_c4_gate0_probe.py --account c1`:**

| reading | wall ms | api ms | classification | `cli_safe_mode_effective` | `probe_prompt_sha` |
|---|---|---|---|---|---|
| warm-up | 8 712 | 4 104 | success | true | 90e2f1f6698b |
| measured | 9 274 | 2 700 | success | true | 90e2f1f6698b |
| baseline 08-09 | 132 934 / 162 739 | — | success | absent (full profile) | — |
| baseline 09-09 | 151 327 | 140 517 | **refusal** (cites operator Stop hook) | absent | — |

GATE-0 VERDICT: PASS. Host commit 83.7 % at spawn. Rows live in the gitignored `RussianTranslation/src/pilot/output/health_probe_log.jsonl` (run_id `h963-c1-single-profile-gate0/2026-09-16T02:46:48Z-pid31592`). Two consecutive successes meet the handoff's stop condition. This reading also discharges H4527's owed «live reading at or after 16-09 00:00Z».

**Code (residual):** [`max_account_orchestrator.profile_status`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py) — the `profile:init` validation spawn now appends `--safe-mode` via `headless_worker.resolve_safe_mode({}, claude)` (derived, never a literal). Selftest pin: equality with the lane resolver both ways.

**Checks:** `python max_account_orchestrator_selftest.py` → `PASS` (new line `H4436 profile:init --safe-mode: == headless_worker.resolve_safe_mode({}) both ways`).

**Unchanged:** no new profile directory, no credential copy, no `max_orchestrator.sqlite` change — c1 stays the only validated account. Branch `h4436-probe-safe-mode` is superseded (not deleted).

**Not done here:** H4342 (a)/(b) — a full paid band-4 window — is outside this handoff's edit scope and the lane budget; its probe precondition is now green.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
