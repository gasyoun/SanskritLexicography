# H2117 — Sonnet 5 independent re-verify of H2043 G7–G9 (dual-run compare vs Grok 4.5)

_Created: 03-08-2026 · Last updated: 03-08-2026_

**Model:** Sonnet 5 (`claude-sonnet-5`) · offline, no paid calls
**Source handoff:** [H2043](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2043-Sonnet_SanskritLexicography_g7-g9-pwg-standing-goals-reverify_31.07.26.md) (intended executor, ran instead by Grok 4.5 under override)
**Override lane already merged:** [Uprava PR #1630](https://github.com/gasyoun/Uprava/pull/1630)
**This residual:** [H2117](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2117-Sonnet_SanskritLexicography_h2043-override-dual-run-compare_01.08.26.md)

## Method

Independently re-read G7–G9 in `GOALS_MANUAL.md` and the "Goal-based invocation" sections
of [`/pwg-drain`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-drain.md),
[`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md),
[`/pwg-bounded-run`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md),
[`/pwg-window-close`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-window-close.md)
directly from disk (`~/.claude/commands/`) — did not read Grok's PR diff first. Re-ran the two
offline gates Grok's re-verify cited, and independently grep+read-confirmed the A2/A3/A6 code
claims from Grok's [`H_OFFLINE_SPEED_A2_A6_VERIFY_2026-08-01.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H_OFFLINE_SPEED_A2_A6_VERIFY_2026-08-01.md).

## Per-claim comparison (dual-run-salvage classes)

| Claim (GOALS_MANUAL G7–G9, Grok 4.5, 01-08-2026) | Sonnet 5 independent finding | Class |
|---|---|---|
| G7: skill wiring still names G7 on `/pwg-drain` + `/pwg-bounded-run` + `/pwg-window-close` | Confirmed — `pwg-drain.md` frontmatter `goal: G7 G8 G9 G10` + §"Goal-based invocation (G7–G10)"; `pwg-bounded-run.md` frontmatter `goal: G7 G8 G9 G46`; `pwg-window-close.md` frontmatter `goal: G7 G10` + Phase 3 "This is the **G7** goal loop" | IDENTICAL |
| G7: bootstrap still forbids requeue | Confirmed — `pwg-window-close.md` Phase 3: "Bootstrap mode forbids requeue entirely"; `pwg-bounded-run.md`: "Bootstrap forbids retries, requeues, replacement candidates, and widening" | IDENTICAL |
| G7: no architecture drift | Mostly true, with one net-new addendum: since Grok's 01-08-2026 pass, `/pwg-bounded-run` picked up three new hard-fail guardrails — H2157 (`--execute` now requires `--max-calls`+`--cost-ceiling`), H2158 (`--cwd` must be a bare scratch dir, not repo — cost/latency finding), H2159 (`--execute` now requires `--canary-receipt`) — all dated 02-08-2026, i.e. AFTER Grok's PR #1630 merged (01-08-2026 13:28 UTC). These harden G8/G9 preconditions further; they do not contradict or weaken the G7–G9 wiring Grok verified. Not a correction to Grok's work — it was accurate as of its own timestamp. | NET-NEW (post-dates Grok's pass, non-conflicting) |
| G8: still on `/pwg-drain` + `/pwg-live-gate` + `/pwg-bounded-run`; exact preflight + `STOP_COST_UNEVALUABLE` still documented | Confirmed — `pwg-bounded-run.md` line 19 "(G8)" on exact preflight, line 69 `STOP_COST_UNEVALUABLE` (G8) terminal-stop text unchanged | IDENTICAL |
| G8: offline `lang_parity_check` 90 entries, 0 drift | Re-ran `python src/pilot/lang_parity_check.py`: **91 entries, 0 drift** (was 90 in Grok's same-session run). Verdict (0 drift, all complete) is unchanged; the +1 entry is intervening-commit growth between 01-08 and 03-08, not a discrepancy in Grok's finding. | EQUIVALENT |
| G9: max-wide=1 bootstrap + 180s ceiling + fingerprint serialization still in skill text | Confirmed — `pwg-bounded-run.md` line 24: "One prepared plan, one profile, one serial call lane, the worker's 180-second per-call kill ceiling, and fingerprint serialization (G9)" | IDENTICAL |
| G9: residual ledger / promote refuse-defect / wall-clock auto-derive present (A2/A3/A6 shipped) | Independently grep+read-confirmed all five functions exist exactly as Grok's verify doc names them: `window_reports.derive_wall_clock_minutes` (line 118) + `build_production_metrics` (line 155); `dashboard_events.emit_stage_boundary` (line 94); `promote_final_cards.discover_defect_keys_path` (line 92) + `refuse_defect_keys` (line 114); `requeue_from_audit.py` calling `residual_ledger.append_from_audit_report` (line 188); `no_pwg_residual_ledger.append_from_audit_report` (line 117) + `backfill_documented` (line 142) | IDENTICAL |
| G9: (implicit — not explicitly re-run by Grok's static-check pass) | Ran `python src/pilot/no_pwg_residual_ledger.py selftest` fresh: **PASS**. Adds a mechanical execution confirmation on top of Grok's static code-presence check. | NET-NEW (additive verification, non-conflicting) |

## Verdict

No hard offline red. No overclaim or under-verification found in Grok 4.5's H2043 override
work — every G7/G8/G9 claim in [PR #1630](https://github.com/gasyoun/Uprava/pull/1630) holds
up under independent Sonnet 5 re-read + re-run. Per the H2117 guardrail ("do not flip standing
🔵 to ✅ unless a hard offline red appears"), standing status for G7/G8/G9 is unchanged: 🔵
standing (wired). GOALS_MANUAL.md rows for G7/G8/G9 get a Sonnet-reconfirmation note appended
(not a correction) with the 91-entry lang-parity count and the H2157–H2159 net-new hardening
pointer, so a future reader sees both passes' evidence.

## Adjudication — keep the best of both

Keep Grok's original evidence text (accurate, sourced, still true) AND append Sonnet's
independent reconfirmation + the two net-new deltas (H2157–H2159 hardening; 91 vs 90 parity
count) rather than overwriting either. No conflicting claims to resolve.

_Dr. Mārcis Gasūns_
