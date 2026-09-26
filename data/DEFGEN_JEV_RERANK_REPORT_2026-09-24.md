# H5279 — Jev gloss re-rank on the frozen defgen sample

_Created: 2026-09-24 · Last updated: 2026-09-24_

**Handoff:** H5279 (OxAlpha) · **Executor:** OxAlpha (opencode/z-ai/glm-5.3-flash) · **Model:** jev-1.13.0 (TypeSafe System One)

## What was measured

- **Sample:** kosha frozen defgen sample (seed 730, n=500) — scored **500/500** headwords (**2500** candidate calls).
- **Jev state:** headword + grammar + <=5 DCS attestation sentences + ONE candidate gloss (gold gloss NOT in state).
- **Jev question:** score per candidate: how faithful to the corpus sense (6-level 0-5 list), one call per candidate (isolated).
- **Baseline:** deepseek-chat adequacy 0-5 vs MW gold gloss (kosha judge_<arm>.jsonl, H730).
- **Measurement-only:** no lane is rewired. The Jev arm judges against the DCS corpus context, the baseline judge against the MW gold gloss — the comparison asks *does Jev reproduce the ranking step, and at what cost*, never which is more correct.

### Design probe (why this shape)

- 8 high-freq items: all-candidates-in-one-state score -> floor gap 0.011; isolated-candidate score -> floor gap +4.283 (tools/h5279_jev_design_probe.py).
- The all-candidates-in-one-state shape (mirroring the H5277 rerank) collapses on this task: with a shared state the model hedges every candidate near 3.7 regardless of arm, so the random floor is not separated. The isolated-candidate shape used here is the one that measures.

## Arm scores (mean per candidate, 0–5)

| Arm | Jev 0–5 | baseline judge 0–5 | chrF-MW |
|---|---|---|---|
| A0_random_floor | 0.7127 | 0.186 | 11.82 |
| A1_chat_ctx | 4.3481 | 4.322 | 24.61 |
| A2_chat_noctx | 3.9865 | 4.084 | 22.49 |
| A3_reasoner_ctx | 4.3419 | 4.208 | 20.48 |
| F1_fable_ctx | 4.4835 | 4.6 | 30.33 |

- **Floor separation** — Jev: A0 0.7127 vs systems 4.29 (**gap 3.5773**); baseline judge: A0 0.186 vs systems 4.3035 (gap 4.1175).

## Rank agreement

- Mean per-item Kendall τ-b Jev vs baseline judge: **0.5815** (vs chrF: 0.3133)
- Per-item top-1 agreement: **127/500** vs baseline judge, **159/500** vs chrF (8/500 items carry a constant baseline-judge row, where no ranking is defined — that caps the judge agreement).
- Per-arm Spearman ρ (Jev score vs baseline adequacy): A0_random_floor 0.3112, A1_chat_ctx 0.3185, A2_chat_noctx 0.4144, A3_reasoner_ctx 0.1765, F1_fable_ctx 0.0999
- Arm ranking (best→worst) — Jev: F1_fable_ctx > A1_chat_ctx > A3_reasoner_ctx > A2_chat_noctx > A0_random_floor; judge: F1_fable_ctx > A1_chat_ctx > A3_reasoner_ctx > A2_chat_noctx > A0_random_floor; chrF: F1_fable_ctx > A1_chat_ctx > A2_chat_noctx > A3_reasoner_ctx > A0_random_floor

## Cost + latency

| arm | calls | input tokens | cost |
|---|---|---|---|
| Jev (measured) | 2500 | 1,499,617 | $0.06298 |
| baseline judge (reconstructed, priced at deepseek-chat 0.27/1M in (H1210 arm-B historical note)) | 2500 | ~595,929 | ~$0.1609 |

- Jev per-call latency: mean 1379 ms, p50 1010 ms.
- Per 500-headword pass: Jev $0.06298 vs baseline ~$0.1609 (2.6x).

## Verdict

| check | value |
|---|---|
| arm ranking identical to baseline | True |
| A0 floor separated (gap > 1.0) | True |
| cheaper than the baseline judge | True |
| **GO** (all three) | **True** |

**GO** — Jev reproduces the baseline judge's arm ranking on the frozen sample, separates the random floor, and costs less per pass. Replacing the defgen ranking step with Jev is a legitimate *future* unit; this report rewires nothing.

## Checks

```
python tools/h5279_jev_defgen_gloss_rerank.py --selftest   # offline
python tools/h5279_jev_defgen_gloss_rerank.py --run        # live, resumable
python tools/h5279_jev_defgen_gloss_rerank.py --analyze    # report
```

Artifacts: `data/defgen_jev_rerank/jev_per_item.json` (per-item scores), `jev_rerank_aggregate.json` (aggregate), this report, `tools/h5279_jev_design_probe.py` (the design probe).

_Гасунс_
