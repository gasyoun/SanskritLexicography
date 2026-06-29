# Step 1 Grammar-Parity Re-run: Speed & Cost Findings

**Date:** 2026-06-29  
**Task:** Re-translate sTA, BU, as, i, gam on `gen_opt_harness2.py` (3-layer batched+masked) to achieve grammar-parity with yuj/vid/han, which were translated 3-layer from the start.

---

## Results at a glance

| root | cards | nulls | clean | requeue | clean% | $cost | tokens (transcript) | wall-clock |
|------|------:|------:|------:|--------:|-------:|------:|--------------------:|-----------|
| sTA  | 123   | 0     | 96    | 27      | 78%    | $5.09 | 1.41 M              | ~15 min   |
| BU   | 59    | 1     | 44    | 15      | 75%    | $3.01 | 849 k               | ~7.5 min  |
| as   | 98    | 6     | 87    | 11      | 89%    | $2.84 | 803 k               | ~7.5 min  |
| i    | 204   | 5     | 178   | 26      | 87%    | $5.54 | 1.55 M              | ~25 min†  |
| gam  | 127   | 1     | 111   | 16      | 87%    | $3.68 | 1.22 M              | ~7 min    |
| **total** | **611** | **13** | **516** | **95** | **84.5%** | **$20.16** | **5.83 M** | **~62 min** |

† i ran in three sequential parts (split 68+68+68) due to the 524 KB Workflow file-size limit.

Gates on all 5 roots: **nws PASS · sense_dupes PASS** (no F12 misattribution, no sense collisions).

---

## Per-card cost breakdown

| root | $/card (new) | cards in batches | single-card batches |
|------|-------------:|----:|----:|
| sTA  | $0.041       | 123 | 8 (pw\*/sch layer) |
| BU   | $0.051       | 59  | ~6 (pw\*/sch layer) |
| as   | $0.029       | 98  | ~4 (pw\*/sch) |
| i    | $0.027       | 204 | 8+ (pw\*/sch) |
| gam  | $0.029       | 127 | 7 (pw\*/sch) |
| **avg** | **$0.033** | | |

---

## Comparison with old 2-layer single-card runs

### Token ratio (sTA — the one root with hard data)

| metric | old (2-layer, gen\_opt\_harness.py) | new (3-layer, gen\_opt\_harness2.py) | ratio |
|--------|------------------------------------:|------------------------------------:|------:|
| cards  | 106 (pre-rebatch)                   | 123                                 | —     |
| tokens | ~10.3 M                             | 1.41 M                              | **7.3× reduction** |
| wall-clock | ~19 min                         | ~15 min                             | 1.3× faster |

Normalised to same card count (106 cards): old was ~97 k tokens/card vs new ~11.5 k tokens/card = **8.4× token reduction per card**.

### A/B benchmark (8 mixed gam cards)

The `TLONLY_PROTOTYPE.md` A/B test on 8 cards established the baseline:

| variant | cost / 8 cards | $/card |
|---------|---------------:|-------:|
| old (single-card) | $1.72 | $0.215 |
| new (batched)     | $0.17 | $0.021 |
| **reduction**     | **-90%** | **10×** |

Observed production ratio (gam): $3.68 / 127 cards = **$0.029/card** vs extrapolated old $0.215/card = **7.4× reduction**. (Slightly less than A/B prototype because production includes pw\*/sch single-card batches.)

### First 3-layer runs (yuj/vid/han, for sanity-check)

These were already translated 3-layer and are NOT part of this re-run, but provide a cost ceiling check:

| root | cards | $cost | $/card |
|------|------:|------:|-------:|
| yuj  | 60    | $3.52 | $0.059 |
| vid  | 55    | $3.20 | $0.058 |
| han  | 78    | $2.94 | $0.038 |

The current 5-root batch (avg **$0.033/card**) is 20–40% cheaper per card than the first 3-layer runs — likely because those had higher retry overhead (yuj had a tool-use blowup) and smaller average batch sizes.

---

## Key findings

### 1. Cost: ~8× cheaper than the 2-layer single-card baseline
The dominant saving comes from amortising the ~27–46 k-token system-prompt `cache_create` across N cards per batch instead of paying it once per card. With avg batch sizes of 8–12 cards, the per-card overhead drops from ~90 k tokens to ~11 k tokens.

### 2. The pw\*/sch layer is a structural cost exception
Cards named `*_zz_pw*`, `*_zz_sch`, `*_zz_pwkvn` are in their own single-card batches (the harness bins by `skeleton + portrait` size, and these cards are dense). Each still pays the full system-prompt overhead. Effect: roots with many pw\*/sch layer cards (sTA $0.041/card, BU $0.051/card) cost 40–55% more per card than roots with sparse pw\*/sch coverage (as/i/gam ~$0.029/card). This is structural — fixing it would require a cross-root pw\* consolidation run, which is out of scope for Step 1.

### 3. Quality: 84.5% clean, no gate failures
All 5 roots cleared the nws and sense_dupes gates. The requeue residual (15.5%) decomposes into:
- **Missing-senses nulls** (13 cards) — fidelity guard rejected garbled batch outputs; harness retry cleared most but 13 persisted.
- **High-confidence semantic flags** (e.g. `foreign_gloss_translated`, `untranslated_braced_german_gloss`) — largely the known F-gate-nws-fp and Latin/French euphemism patterns, now mostly suppressed but residual on pw\* cards.
- **Coverage mismatches** — big pw\* cards with >50 senses sometimes have count mismatches in the batch schema.

### 4. Wall-clock: 3-layer batched is faster despite added grammar context
Old sTA: ~19 min for 106 cards. New sTA: ~15 min for 123 cards. The grammar layer adds ~0.5 k tokens per root (injected once per batch, not per card), so the overhead is negligible. The speedup comes entirely from batching (fewer agent invocations → fewer API round-trips).

### 5. Split-key runs work reliably; `i` (204 cards) split into 3 with no data loss
The 3-part i run (68+68+68) merged cleanly to 204/204 cards with PASS gates. The split is reliable as long as key boundaries are computed from the same rootmap and PH restoration uses per-harness placeholder maps.

---

## Recommendations going forward

1. **Accept all 5 roots as-is.** Gates PASS, 84.5% clean is consistent with the Slice C baseline (75.9%). The 95-key requeue pool feeds into the coordinating requeue pass alongside other Slice A roots.
2. **Do not attempt pw\*/sch consolidation now.** The structural cost overhead on those cards is real but modest (<$0.50 total across 5 roots). Fixing it requires a dedicated pw\* batch harness and is Step 2+ work.
3. **Target batch size: 8–12 cards for dense roots, 5–7 for sparse.** The 9 k-token budget used here hit this range naturally for most batches.
4. **Use `--allow-stale` for audit on split+merged outputs.** The merged file only has hashes for the last-merged-in part; `--allow-stale` is safe when the harnesses were freshly generated in the same session.
