# Jev gloss judge on the defgen sample — KEEP_BASELINE (H5279)

_Created: 24-09-2026 · Last updated: 24-09-2026_

**Jev gloss judge on the defgen sample — KEEP_BASELINE (OxAlpha `opencode/z-ai/glm-5.3-flash`, 24-09-2026).** H5279: jev-1.13.0 score-channel judged all 2500 arm×item pairs of the frozen F48 defgen sample (blinded state = headword + gold gloss + attestations + candidates A–E; 500/500 requests OK, $0.0196). Result: no discrimination — every arm ≈4.05 including the seeded-derangement floor (Jev 4.046 vs baseline judge 0.186), pairwise agreement ρ=0.239, arm-rank ρ=−0.3, within-item range 0.071; only cost passes (measured $7.9e-06/judgment vs deepseek-chat est $3.36e-04). Verdict per the locked 4-gate rule: **KEEP_BASELINE — the deepseek-chat judge stands, no ranking-step replacement**. Independent DeepSeek verifier PASS (gate arithmetic re-derived, cost cross-corroborated). Runner: [tools/bench_defgen_jev_gloss_judge.py](../../tools/bench_defgen_jev_gloss_judge.py) · report: [reports/DEFGEN_JEV_GLOSS_JUDGE_2026-09-24.md](../../reports/DEFGEN_JEV_GLOSS_JUDGE_2026-09-24.md). FEATURES_INDEX F48 row extended.

_Гасунс_
