# H5279 — Jev gloss re-rank/judge on the defgen frozen sample — report

_Created: 24-09-2026 · Executor: OxAlpha (opencode/z-ai/glm-5.3-flash)_

**Mission:** on the frozen 500-headword defgen sample (F48), use TypeSafe Jev
(`jev-1.13.0`) to judge the 5 frozen arm candidates per headword and compare
against the existing blinded DeepSeek-chat LLM-judge baseline on judge-quality
agreement + cost. Replace the bench's ranking step ONLY if Jev beats the
baseline at lower cost; measurement-only otherwise. No product change.

**Verdict: MEASURE-ONLY** — Jev does not replace the defgen judge. It passes
the floor-separation gate and correlates with both the baseline judge
(per-item Spearman ρ̄ 0.72) and chrF (ρ 0.39–0.51, matching the baseline's
0.39–0.47 band), is highly stable (canary |Δ|=0.005), and costs
**$0.0199/1000 candidates** — but it is **not cheaper in substance** than the
judge-class baseline ($0.020–0.039/1000 reconstructed at current tariffs) and
it **breaks the reference-invariant arm ordering** that makes the frozen
bench's judged ranking trustworthy (Jev ranks the reasoner arm 2nd; the
baseline judge, both H2408 references and chrF all rank it 4th).

## 1. Call-architecture calibration (a reusable TypeSafe finding)

Three live calibration probes (24-09-2026) before any scoring:

| Form | Gold-copy candidate | Deranged candidate | Discriminates? |
|---|---|---|---|
| 5 `score` questions in one request, candidates only in state | 4.37/6 | 4.39/6 | **NO** |
| 10 questions (5×`score` + 5×`noul`) in one request, candidates quoted in questions | 4.48/6 · noul 0.36 | 4.45/6 · noul 0.36 | **NO** |
| **ONE call per candidate, single `noul` question** (H5277 form) | **noul 0.95** | **noul 0.02** | **YES** |

Batch multi-question requests against a shared state are content-insensitive
on this API (answers cluster near a fixed point regardless of evidence); the
estate's discrimination-proven form is one-call-one-candidate-one-question.
This replicates and extends the H5277 architecture note and constrains every
future Jev bench (it also makes per-candidate scoring the minimum call
granularity — a 500×5 full sweep would need 2500 calls, over this handoff's
≤550 fence).

A 15-call control confirms the `score` primitive ALSO discriminates in
single-question form (floor arm 0.00 vs system arms 2.45–3.25) — the failure
above is the batch form, not the primitive. `noul` stayed primary because it
carries the H5276/H5277 calibration record.

## 2. Protocol

- **Data:** kosha `data/eval/defgen` frozen sample (500 headwords, seed 730)
  + 5 frozen arms + frozen judge baseline + per-item chrF — consumed
  READ-ONLY, never regenerated.
- **Subset:** budget fence ≤550 external calls forced a seeded stratified
  **100-headword subset** (seed-family `h5279-subset:730`, proportional per
  freq×poly cell: 12+11×8, [subset_100.tsv](subset_100.tsv) +
  [subset_100.meta.json](subset_100.meta.json)). Baseline columns below are
  recomputed on the SAME 100 items for apples-to-apples.
- **Jev arm:** one call per (headword, arm) — 500 calls, 8 workers, 500/500
  OK, 2m34s wall. State = headword (SLP1+IAST) + grammar + GOLD reference
  gloss + ≤5 DCS attestations + the single candidate; question = `noul`
  "does the candidate convey the gold meaning" (criteria
  {true,false}), answer noul∈[0,1] ×5 onto the 0–5 adequacy scale.
- **Controls:** gold-copy/deranged calibration (above); canary = 25 re-scored
  calls (5 seeded items × 5 arms); score-primitive control = 15 calls.
- **Total external calls: 545/550** (3 batch probes + 2 calibration + 500 run
  + 25 canary + 15 control). Input 235,545 tokens → **$0.0099**.
- Runner (committed, resumable, `--dry-run`/`--probe`/`--analyze` offline
  modes): [jev_defgen_rerank.py](jev_defgen_rerank.py), client reused
  verbatim from Uprava `tools/jev_probe.py` (H5275).

## 3. Judge-quality agreement vs the frozen baseline

| Arm | Jev mean (noul×5, n=100) | baseline mean (same 100) | baseline full-500 | Jev~chrF ρ | baseline~chrF ρ (full-500) |
|---|---|---|---|---|---|
| A0_random_floor | **0.21** | 0.16 | 0.186 | −0.146 | 0.117 |
| A1_chat_ctx | 3.24 | 4.18 | 4.322 | 0.433 | 0.391 |
| A2_chat_noctx | 3.15 | 3.99 | 4.084 | 0.391 | 0.466 |
| A3_reasoner_ctx | 3.33 | 3.89 | 4.208 | 0.402 | 0.423 |
| F1_fable_ctx | **3.65** | 4.47 | 4.600 | **0.513** | 0.415 |

- **Floor separation (protocol gate 1): PASS** — A0 floors at 0.21, systems
  at 3.15–3.65; gap 3.04 (baseline 4.02).
- **Per-item agreement with the baseline judge: mean Spearman ρ̄ = 0.7165**
  (97/100 items valid; 3 dropped where one judge's 5 scores are constant —
  ρ undefined, standard treatment).
- **Top-1 agreement: 85/100 tie-aware** (Jev's argmax inside the baseline
  max-set — baseline integer scores tie at 5 frequently); strict top-1 where
  the baseline has a unique winner: 16/24 = 66.7%.
- **Arm ranking: MISMATCH** — Jev `F1 > A3 > A1 > A2 > A0` vs baseline
  `F1 > A1 > A2 > A3 > A0`. H2408 established the arm ranking is
  reference-invariant across two independent LLM judges (MW gold + Huet-FR
  gold) and chrF agrees (`A1 > A2 > A3`); Jev alone promotes the terse
  reasoner arm over both context arms. Winner (F1) and floor (A0) reproduce.
- **Canary stability: mean |Δnoul| = 0.005** over 25 re-scored calls, 56%
  bit-identical — the measurement itself is repeatable.

## 4. Cost

| Lane | per 1000 candidates | basis |
|---|---|---|
| **Jev (measured)** | **$0.0199** | 235,545 input tokens / 500 calls; output free; $0.042/1M |
| Baseline judge (reconstructed) | $0.020–0.039 | exact prompt strings, 440,461 chars ≈ 110,115 in-tokens (chars/4) + ~10 out-tokens/call, priced at current `deepseek-flash` list $0.30/1M in peak (off-peak $0.15) + $1.20/1M out — fetched 24-09-2026 |

The baseline run's own USD was never logged (no `usage` in
`judge_*.jsonl`), and `deepseek-chat` (the model actually used, 11-07-2026)
no longer appears on the DeepSeek pricing page — hence the reconstruction at
the current judge-class tariff, assumptions stated. Jev is at parity with
off-peak DeepSeek and ≤2× cheaper at peak; its state carries attestations
(~471 tok/call vs the baseline's ~220) — a slimmed Jev prompt could be ~40%
cheaper, but that changes the measurement, not the verdict. Per the B3
reference point, both are ~250× below a Sonnet-class judge (~$4.93/1000).

## 5. Why MEASURE-ONLY (and not REPLACE)

1. **Quality below baseline where it counts:** the replace decision gates on
   reproducing the judged arm ranking — the property H2408 proved
   reference-invariant. Jev breaks the mid-field ordering (A3>A1) against
   baseline judge, FR judge and chrF alike; ρ̄ 0.72 per-item and 85%
   tie-aware top-1 are healthy for a second opinion, not judge-equivalent.
2. **Cost not materially lower** — parity to 2× at current tariffs, and the
   baseline's actual historical price is unlogged.
3. **Evidence-map bar (JEV_NO_VALUE_EVIDENCE_MAP_24-09-2026, GTD row of
   24-09):** any GO needs two-box reproduction — this is a single-box run,
   and (1) already fails regardless. No local gloss-scoring BGE/cross-encoder
   exists in the estate to add as a third comparator (REUSE_INDEX /
   FEATURES_INDEX checked — building one is a separate capability, out of
   scope for a measurement-only unit).
4. Consistent with the fan pattern: Jev's proven niche remains calibrated
   binary judgment (H5276 PASS), not graded re-ranking (H5277 niche-only,
   H5274 NO-GO).

## 6. Limitations

- 100-headword subset, not the full 500 (call fence); baseline subset means
  track full-500 means closely (max |Δ| 0.10), but the subset adds sampling
  noise of its own to every number above.
- noul is a binary-faithfulness probability scaled ×5, not a graded adequacy
  rubric — a graded-judge comparison would prefer the `score` primitive,
  which discriminates only in single-question form (§1 control) and was not
  run at scale under this fence.
- Judge agreement here is measured against ONE baseline judge; the human
  subsample (protocol gate 3) remains owed for both.

## 7. Reproduce

```sh
python3 data/defgen_jev_rerank/jev_defgen_rerank.py --dry-run        # offline shape check
python3 data/defgen_jev_rerank/jev_defgen_rerank.py --probe          # live calibration (gold)
H5279_PROBE_CAND=deranged python3 data/defgen_jev_rerank/jev_defgen_rerank.py --probe
python3 data/defgen_jev_rerank/jev_defgen_rerank.py --run            # 500 calls, resumable
python3 data/defgen_jev_rerank/jev_defgen_rerank.py --canary         # 25 calls
python3 data/defgen_jev_rerank/jev_defgen_rerank.py --score-check    # 15 calls
python3 data/defgen_jev_rerank/jev_defgen_rerank.py --analyze        # -> jev_summary.json
```

Artifacts: [jev_scores.jsonl](jev_scores.jsonl) (raw noul answers + usage,
500 rows) · [jev_canary.jsonl](jev_canary.jsonl) ·
[jev_score_check.jsonl](jev_score_check.jsonl) · [jev_summary.json](jev_summary.json).

## Provenance

Runner + analysis + report: OxAlpha (`zai-coding-plan/glm-5.3-flash`),
24-09-2026, under [H5279](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5279-OxAlpha_SanskritLexicography_jev-defgen-gloss-rerank_23.09.26.md).
Jev client: Uprava [tools/jev_probe.py](https://github.com/gasyoun/Uprava/blob/main/tools/jev_probe.py) (H5275, e63a872d17), key never echoed.
Baseline: frozen DeepSeek-chat judge, kosha [DEFGEN_MW_GLOSS_EVAL_PROTOCOL.md](https://github.com/gasyoun/kosha/blob/main/docs/DEFGEN_MW_GLOSS_EVAL_PROTOCOL.md) (H730) + H2408 FR reference + H4796 RU third reference.
MW glosses public domain (1899); DCS sentences CC BY 4.0 (Oliver Hellwig).

_Гасунс_
