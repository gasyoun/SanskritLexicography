# Jev gloss judge on the defgen sample — KEEP_BASELINE (H5279)

_Generated: 2026-09-24 · model `jev-1.13.0` (TypeSafe System One) · blinded 5-candidate scoring, 500 frozen headwords · H5279_

**Verdict: KEEP_BASELINE** — rule: pairwise rho>=0.7 on n>=500 AND arm-rank rho>=0.8 AND floor gap>=1.0 AND cost<baseline-est.

| Metric | Jev | Baseline (deepseek-chat) |
|---|---|---|
| Pairwise agreement vs baseline | ρ=0.239 (Pearson 0.203), n=2500 | — |
| Arm-rank agreement | ρ=-0.3 | — |
| Floor separation (ctx−A0) | -0.0 | 4.117 |
| Cost per judgment | $7.9e-06 (measured) | ~$0.000336 (est) |

| Arm | Jev mean | Jev ρ~chrF | Base mean | Base ρ~chrF |
|---|---|---|---|---|
| A0_random_floor | 4.046 | 0.008 | 0.186 | 0.117 |
| A1_chat_ctx | 4.048 | 0.151 | 4.322 | 0.391 |
| A2_chat_noctx | 4.047 | 0.106 | 4.084 | 0.466 |
| A3_reasoner_ctx | 4.045 | 0.189 | 4.208 | 0.423 |
| F1_fable_ctx | 4.045 | 0.296 | 4.6 | 0.415 |

Calls: 500 OK / 500 billed, $0.0196 total. Full per-item dump: [DEFGEN_JEV_GLOSS_JUDGE_2026-09-24.json](DEFGEN_JEV_GLOSS_JUDGE_2026-09-24.json). External anchor: TypeSafe's own skill-suggestion cookbook reports 7.3% wrong picks on a 182-skill ranking roster — same order of task.

## Validation (negative control + raw shape)

- Legend sent per question (score `criteria` list, per the TypeSafe 2–10 level-string contract): `["0","1","2","3","4","5"]`.
- Raw response sample (pre-run smoke, item `AyA`): A 4.48 / B 4.46 / C 4.52 / D 4.46 / E 4.47, confidence 0.64–0.68 — the tight cluster was visible before the full run and reproduced on all 500 items.
- Distribution (full run): n=2500, mean 4.046, sd 0.334, min 2.03, max 4.69; 20/2500 scores <3; within-item range mean 0.071 (max 0.37) — real variance exists, but candidates within one headword are not separated, and the derangement-floor negative control is not detected (Jev 4.046 vs baseline 0.186).
- Independent verifier (DeepSeek, 24-09): **PASS** — gate arithmetic reproduced (baseline floor gap 4.117 re-derived by hand), cost cross-corroborated (1-call smoke $4e-05/call ≈ batch $3.92e-05/call); residual note: request-shape-bug exclusion is inferential (no raw dump in earlier drafts) — recorded here with the legend + raw sample; a confirmed shape bug would only reinforce KEEP_BASELINE.

_Гасунс_
