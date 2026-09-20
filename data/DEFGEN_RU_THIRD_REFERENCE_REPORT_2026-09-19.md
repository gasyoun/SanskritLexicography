# H4796 — Definition-generation eval: Russian third reference — report

_Created: 19-09-2026 · Executor: OxAlpha (opencode/z-ai/glm-5.3-flash), offline deterministic lane_

**Mission:** join the corpus-attested Russian witness (SanskritRussian / sa-ru-glossary lemma layer, kosha dataset `sa-ru-glossary`) as the THIRD reference of the MW definition-generation eval — after the EN MW baseline and the H2408 Heritage FR second reference — measure the three-way agreement surface, and leave the judge-ready harness for the paid lane. kosha/data/eval/defgen consumed READ-ONLY; both text layers (FR LGPLLR, RU tier=restricted) stay local, committed artifacts carry sha256 digests only.

## 1. Three-way census (the headline)

| Witness set | Headwords |
|---|---|
| frozen MW sample | 500 |
| ∩ Heritage FR (H2408) | 333 |
| ∩ sa-ru RU (this handoff) | 384 |
| ∩ all three | **287** |

The RU witness covers **76.8%** of the frozen sample (384/500) and **86.2%** of the FR overlap; the three-witness subset is **287 headwords** (high/mono 51, high/poly2_4 47, high/poly5p 48, low/mono 6, low/poly2_4 13, low/poly5p 16, mid/mono 30, mid/poly2_4 33, mid/poly5p 43).

## 2. Reference-divergence triangle (subset n=287)

| Pair | corpus chrF | mean token-F1 |
|---|---|---|
| MW-EN vs Heritage-FR | 17.86 | 0.0400 |
| MW-EN vs sa-ru-RU | 0.26 | 0.0000 |
| Heritage-FR vs sa-ru-RU | 0.39 | — |

Cross-lingual pairs are structurally near-degenerate — the triangle quantifies the degeneracy, it does not measure semantic agreement. Mean gloss lengths: MW 55.1 words, FR 44.0, RU 5.1 (top-5 renderings).

## 3. Surface familiarity gradient on the three-witness subset (d = chrF_MW − chrF_FR, seed 4796)

| Arm | mean d | 95% CI | n nonzero | MW>FR | FR>MW | sign p |
|---|---|---|---|---|---|---|
| A0_random_floor | +2.936 | [+2.361, +3.514] | 282 | 207 | 75 | <1e-6 |
| A1_chat_ctx | +10.742 | [+9.389, +12.091] | 287 | 256 | 31 | <1e-6 |
| A2_chat_noctx | +9.917 | [+8.562, +11.326] | 285 | 244 | 41 | <1e-6 |
| A3_reasoner_ctx | +8.190 | [+6.772, +9.685] | 287 | 234 | 53 | <1e-6 |
| F1_fable_ctx | +14.125 | [+12.586, +15.654] | 287 | 263 | 24 | <1e-6 |

Positive d = candidates sit measurably closer to the MW wording than to the independent FR authority on this subset — the surface analogue of the H2408 MW-familiarity premium, reproduced without any provider call. Per-item chrF_MW~chrF_FR Spearman (pooled over arms): **0.5867**.

Two reading guards. **Floor:** the seeded-derangement arm A0 shows the SMALLEST gradient (+2.9 vs +8…+14 for system arms) — a random string matches neither authority, and the ordering floor < context arms < F1_fable_ctx is itself the sanity signal. **Tail:** the surface arm ranking swaps only in the bottom tail (A3_reasoner_ctx and A0 exchange places 4-5 under chrF-FR) — the surface channel does not separate the tail, which is consistent with the protocol's near-degeneracy caveat; the H2408 judge-level reference-invariance of the arm ranking remains the adequacy-grade result and is neither reproduced nor overturned here.

Surface arm ranking: by chrF-MW `F1_fable_ctx > A1_chat_ctx > A2_chat_noctx > A3_reasoner_ctx > A0_random_floor`; by chrF-FR `F1_fable_ctx > A1_chat_ctx > A2_chat_noctx > A0_random_floor > A3_reasoner_ctx`; identical: **False**.

## 4. The RU surface channel is script-degenerate — judge required

| Arm | mean token-F1 vs RU | max | mean sent-chrF vs RU |
|---|---|---|---|
| A0_random_floor | 0.0000 | 0.0000 | 0.14 |
| A1_chat_ctx | 0.0000 | 0.0000 | 0.02 |
| A2_chat_noctx | 0.0000 | 0.0000 | 0.01 |
| A3_reasoner_ctx | 0.0000 | 0.0000 | 0.02 |
| F1_fable_ctx | 0.0000 | 0.0000 | 0.39 |

EN candidates against Cyrillic references score structurally ~0 on token-F1/chrF regardless of meaning: the RU channel CANNOT be arbitrated by surface metrics, one script further than the FR near-degeneracy the protocol already documents. Meaning-level three-way agreement therefore requires the blinded judge (resumable subcommand `judge`, NOT run in this offline unit — needs `DEEPSEEK_API_KEY`; ~287 items x 5 arms calls).

## 5. Per-arm reference table (corpus chrF)

| Arm | MW | FR | RU | multi MW+FR | multi MW+FR+RU |
|---|---|---|---|---|---|
| A0_random_floor | 12.03 | 8.69 | 0.18 | 13.36 | 13.36 |
| A1_chat_ctx | 18.25 | 10.77 | 0.02 | 19.33 | 19.33 |
| A2_chat_noctx | 16.06 | 9.58 | 0.01 | 17.00 | 17.00 |
| A3_reasoner_ctx | 11.91 | 7.04 | 0.02 | 13.05 | 13.05 |
| F1_fable_ctx | 22.40 | 11.89 | 0.44 | 23.17 | 23.17 |

Adding RU to the multi-reference pool moves corpus chrF by ~0 (script gap), as §4 predicts; the FR uplift over MW-only is the surface part of the H2408 story reproduced on this subset.

## 6. Residuals

1. **RU judge run (paid lane)** — `judge` subcommand ready and resumable; then a MW-vs-RU judge delta (H2408 `defgen_heritage_delta.py` method) completes the three-way adequacy triangle. GTD row minted by this handoff.
2. **kosha-side edge** — the sa-ru-glossary manifest row's `consumers` list gains `defgen eval` and kosha's docs/protocol gains the third-reference section; kosha was consumed read-only here (dual-run tombstone H4812 → H4796), so the kosha-side commit is a separate small lane.

## Artifacts

- `data/defgen_ru_third_reference/ru_ref_subset.tsv` — 287 rows, digests only
- `data/defgen_ru_third_reference/ru_ref_subset.meta.json` — census + input digests
- `data/defgen_ru_third_reference/ru_ref_scores.json` — metrics + threeway blocks
- `data/defgen_ru_third_reference/ru_ref_per_item.tsv` — per item x arm
- `tools/h4796_defgen_ru_third_reference.py` — this pipeline

