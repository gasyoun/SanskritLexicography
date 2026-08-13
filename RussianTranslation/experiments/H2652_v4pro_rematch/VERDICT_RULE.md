# H2652 pre-declared verdict rule (frozen BEFORE any Pro token)

_Created: 13-08-2026 · Last updated: 13-08-2026_

**Question.** Does **DeepSeek-V4-Pro-0813** (`deepseek-v4-pro`, `reasoning_effort=high`) earn a **Q3 draft-assist** role (generation + free `det_gate` only) on the frozen H1210 Q3 keys, at the 13-08-2026 Pro list price?

This is **not** E1 and does **not** replace [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/VERDICT_RULE.md) (Flash vs c4). Production Q1–Q2 draft-lane still waits on H2488.

**Sample (frozen).** The 22 H1210 keys with source bytes in [670, 4349] — see [sample_keys.json](sample_keys.json). S2∩Q4 monsters stay out of the main arm (optional 3-card `max` sub-arm is telemetry only and cannot flip this rule).

**Control.** Published H1210 arm B (`deepseek-chat`) on the same Q3 slice: **shippable 15/22 (68%)**, audit-clean 19/22. This sitting does **not** re-run the Opus controller (R1.1: no Claude API; controller is subscription Workflow). The free-gate analogue is `det_gate_clean` = `det.issues` empty.

**Pricing table for Pro (first-party, until 16-08-2026 16:00 UTC):** cache-miss in $0.435 / cache-hit in $0.003625 / out $0.87 per 1M. Fail = applying Flash PRICE_* to this arm.

**Verdict (pre-declared).** Pro wins **Q3 draft-assist** (prep/context seed + optional draft under Opus controller — **not** TM write, **not** auto-promote, **not** Q4) **iff ALL** of:

1. **det_gate_clean** ≥ **15/22** on the frozen Q3 keys (H1210 Q3 shippable floor).
2. **Served model** is `deepseek-v4-pro` on every successful generation call (`model_matches_request` true, or recorded mismatch explained).
3. **`$/det_gate_clean`** is computed from the Pro table above (cost_evaluable true, or explicitly `false` with a reason — never a fake zero).
4. **Zero** TM / store writes from this arm.

Otherwise Pro stays measurement-only. No post-hoc rule change. A production draft-lane claim still requires E1 (H2488) **and** the shared controller path.

Optional `max` sub-arm (3 smallest S2×Q4 keys) is **descriptive**. It cannot PASS this rule and cannot authorise unattended Q4.

_Dr. Mārcis Gasūns_
