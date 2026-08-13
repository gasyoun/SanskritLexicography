# H2676 pre-declared verdict rule (frozen BEFORE any Pro token)

_Created: 14-08-2026 · Last updated: 14-08-2026_

**Question.** After the [H2674 (Grok 4.6) — W0 OpenAI SDK stream + max_tokens 32k + PRICE after-1608](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2674-Grok_SanskritLexicography_deepseek-w0-openai-stream-price_13.08.26.md) transport canary, does **DeepSeek-V4-Pro-0813** (`deepseek-v4-pro`, `reasoning_effort=high`, `max_tokens=32768`) earn a **Q3 draft-assist** role (generation + free `det_gate` only) on the frozen H1210 / H2652 Q3 keys?

This is **not** E1 and does **not** replace [E1 VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/VERDICT_RULE.md). It extends the [H2652 VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2652_v4pro_rematch/VERDICT_RULE.md) with PLAN D16’s second floor. Production Q1–Q2 draft-lane still waits on H2488.

**Sample (frozen).** The same 22 H1210 keys with source bytes in [670, 4349] as H2652 — see [sample_keys.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/sample_keys.json). S2∩Q4 monsters stay out of the main arm (optional 3-card `max` sub-arm is telemetry only and cannot flip this rule).

**Control.** Published H1210 arm B (`deepseek-chat`) on the same Q3 slice: **shippable 15/22 (68%)**, generation **$0.0093 / clean**. This sitting does **not** re-run the Opus controller. The free-gate analogue is `det_gate_clean` = `det.issues` empty (includes `pending-controller` when the issues list is empty).

**Pricing table for Pro (first-party, until 16-08-2026 16:00 UTC):** cache-miss in $0.435 / cache-hit in $0.003625 / out $0.87 per 1M. After the switch: off-peak only, via `price_card`. Fail = applying Flash PRICE_* to this arm.

**Flash cost floor for D16:** H1210 arm B generation **$0.0093 / clean**. Ceiling = **5 × $0.0093 = $0.0465 / det_gate_clean**.

**Verdict (pre-declared, dual floor — PLAN D16).** Pro wins **Q3 draft-assist** (prep/context seed + optional draft under Opus controller — **not** TM write, **not** auto-promote, **not** Q4) **iff ALL** of:

1. **22/22 attempted** on the frozen Q3 keys.
2. **det_gate_clean** ≥ **15/22**.
3. **`$/det_gate_clean` ≤ $0.0465** (5× Flash $0.0093), computed from the Pro `price_card` (cost_evaluable true, or explicitly `false` with a reason — never a fake zero).
4. **Served model** is `deepseek-v4-pro` on every successful generation call (`model_matches_request` true, or recorded mismatch explained).
5. **Zero** TM / store writes from this arm. `store_write` is never true. Promote-DRY only (`would_promote` may be recorded; nothing is written).

Otherwise Pro stays measurement-only. No post-hoc rule change. A production draft-lane claim still requires E1 (H2488) **and** the shared controller path.

Optional `max` sub-arm (3 smallest S2×Q4 keys) runs **only if** the high arm holds transport (no IncompleteRead after 3 retries on the batch). It is **descriptive**. It cannot PASS this rule and cannot authorise unattended Q4.

H2674 canary this rule depends on: [H2674 REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2674_w0_stream/REPORT.md) — **PASS** (3/3, $0.0006, 0 IncompleteRead). Do **not** rerun urllib (H2652 FAIL).

_Dr. Mārcis Gasūns_
