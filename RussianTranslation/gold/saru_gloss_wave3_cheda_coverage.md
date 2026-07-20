# Sa→Ru gloss layer — wave-3 coverage spike: vidyut-cheda on unresolved forms

_Created: 20-07-2026 · Last updated: 20-07-2026_

Wave 3 (H1349) set out to recover the **78,842 forms no tier resolved**
(`surface_unresolved.tsv` — 57,101 simplexes + 21,741 long compounds) by compound
segmentation with **vidyut.cheda** (D7 — reuse, don't build), measured against the
wave-2 precision baseline. **Verdict: NO-GO.** vidyut-cheda on *isolated* forms is
too low-precision to wire in; doing so would inject exactly the recovered-but-wrong
regressions the wave-3 acceptance bar forbids. This document is the measured
negative result + the recommended path forward.

## What was built

[`src/build_compound_split.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_compound_split.py)
wraps the offline `vidyut.cheda` Chedaka (kosha `data/vidyut`, the `compare_sandhi_methods.py`
method-B pattern) and applies a **strict precision gate**: accept a segmentation only if
it has ≥2 tokens **and every member lemma is already glossable** (in `lemma_glossary`).
This is the highest-precision gate a spike found (see below).

## Coverage ceiling (the optimistic half)

| gate | forms recovered | % of 78,842 unresolved | tokens |
|---|--:|--:|--:|
| "any segment glossable" (naive) | ~37,400 | ~47% | — |
| **"≥2 tokens AND all members glossable" (shipped gate)** | **28,673** | **36.4%** | 55,008 (39% of 140,667 unresolved tokens) |

## Precision (the disqualifying half)

A 2-judge panel (Opus 4.8 `claude-opus-4-8`, Sonnet 5 `claude-sonnet-5`) scored a
random 40-item sample of the gated recoveries on two axes — is the **segmentation**
a correct decomposition, and is the recovered **gloss** right:

| axis | both judges correct | either judge "wrong" | acceptable (neither "wrong") |
|---|--:|--:|--:|
| segmentation | 28% | 72% | — |
| gloss | 18% | 60% | 40% |

Against the **wave-2 baseline** (gloss precision 85.3%, lemmatization 86.1%), this is a
catastrophic regression: roughly **half** the gated recoveries are outright wrong. Adding
this tier would trade a measured 85% layer for 36% more coverage at ~18–40% precision — a
net-negative to the layer's trustworthiness.

## Root cause

vidyut-cheda is a **running-text** segmenter; on an isolated OOV form it has no context and
routinely **shatters an inflected/dual/plural word into a stem + a spurious "member"** that
happens to be a real lemma:

- dual/plural endings parsed as particles: `sahadevaśca`→`sahadeva`+`ca`, `-au`→`u` ("и"),
  so the last-member "head" becomes a stray particle glossed "и"/"идет"/"о";
- sandhi not reconstructed: `divyakalpa`→`div`+`aj`+`alpa` ("небо+выгнал+мало");
- meaning inversions: `hīna`→`a`+`hīna` (not-deprived), `sahita`→`ahita` (enemy),
  `drumavarṣa`→drought.

The strict "all members glossable" gate cannot fix this, because the spurious members
(`ca`, `u`, `a`, `i`) are themselves glossable function words.

## Decision + path forward

- **NO-GO on wiring vidyut-cheda into the rollup** (isolated-form recovery). The tool +
  gate are committed for reproducibility and for a running-text application later.
- **Recommended path (backlog):** kosha's own [`compare_sandhi_methods.py`](https://github.com/gasyoun/kosha/blob/main/scripts/compare_sandhi_methods.py)
  already benchmarked the **DharmaMitra neural segmenter (method C) as "near-perfect
  precision, far outperforms vidyut-cheda."** Compound recovery should run a **context-aware
  neural segmenter over the aligned *verse text*** (which this corpus has — forms trace back
  to source verses), not vidyut-cheda over isolated forms. That is the shape of a future
  wave-3.5.
- The 78,842 unresolved forms therefore stay unresolved for now — an honest coverage gap,
  not a low-precision patch. Wave-2's measured 85% layer is unregressed.

Evidence: [`saru_gloss_wave3_cheda_sample.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/saru_gloss_wave3_cheda_sample.jsonl)
+ per-judge labels (`saru_gloss_wave3_cheda_labels_opus.jsonl` / `_sonnet.jsonl`).

_Dr. Mārcis Gasūns_
