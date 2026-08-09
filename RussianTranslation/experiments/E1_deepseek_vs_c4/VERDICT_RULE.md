# E1 pre-declared verdict rule (frozen BEFORE any arm runs — R2.3)

_Created: 02-08-2026 · Last updated: 08-08-2026_

**Question.** Does **DeepSeek-V4-Flash-0731** (`deepseek-v4-flash`) draft earn a
production DRAFT role (Q1–Q2 only) in the PWG→RU pipeline at its price point?

**Arms.** A = c4 (subscription Claude CLI) draft; B = DeepSeek V4 Flash 0731 draft.
SAME frozen sample ([sample_manifest.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/sample_manifest.json)),
same prompts, same free det_gate, same blinded Opus + det_gate protocol (judge never
sees the arm label). Model B default: `deepseek-v4-flash` (H2439 retarget; older
H1210 arm B used `deepseek-chat`).

**Pricing table for B (first-party, 08-08-2026):** cache-miss in $0.14 / cache-hit
in $0.0028 / out $0.28 per 1M tokens.

**Verdict (pre-declared, map §5 + R2.3 / VERIFICATION):** Flash wins a production
**draft-lane Q1–Q2** role **iff ALL** of:

1. **Shippable rate** (canonical audit / gate-clean after shared controller path) is
   within **5 percentage points** of c4 on the frozen sample: shippable_B ≥ shippable_A − 5pp.
2. **$/shippable** for B is **≤ 1/20** of c4's $/shippable on the same sample
   (list-price telemetry on B; subscription Max cost accounting for A as used in H1210).
3. Blinded judge severity distribution is **not worse** at p<0.05 (Mann–Whitney U on
   per-card max severity) — same as the 02-08-2026 VERIFICATION line.

Otherwise Flash gets, at most, **prep-pack / mechanical-QA** lanes (no auto-promote,
no Q4 unattended). No post-hoc rule changes; a rule change = a NEW pre-registered
experiment. Full unattended Flash→TM remains forbidden until this E1 wins **and**
auto-promote policy is re-ruled.

Org map: [DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md](https://github.com/gasyoun/Uprava/blob/main/docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md).

_Dr. Mārcis Gasūns_
