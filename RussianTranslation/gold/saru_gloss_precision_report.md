# Sa→Ru gloss layer — precision panel (H1349 wave 2)

_Created: 20-07-2026 · Last updated: 20-07-2026_

**Model-vs-model LLM panel, NOT a human gold set.** 3 judges (haiku, opus, sonnet) independently labelled a tier × frequency stratified sample of **110** automatic glossary resolutions on two independent axes (D6): **lemmatization** (is the lemma/root a correct reduction of the surface form?) and **gloss** (is the top Russian rendering correct?). Per-item label = panel majority (≥2 of 3); split/correct-vs-wrong disagreements were sent to an adversarial-verify pass. Precision excludes "unsure" from its denominator. Wilson 95% CI. The frozen sample + labels are the scaffold for a human spot-check (see the GTD @DO).

## Overall

| axis | n (judged) | precision | 95% CI | breakdown |
|---|--:|--:|--:|---|
| lemmatization | 108 | **86.1%** | 78.3–91.4 | correct 93 · wrong 15 · unsure 2 |
| gloss | 109 | **85.3%** | 77.5–90.8 | correct 93 · partial 13 · wrong 3 · unsure 1 |

good+partial (gloss): **97.2%** of 109 judged. Inter-judge pairwise agreement: lemmatization 87.0%, gloss 86.4%.

## By tier (which heuristic resolved the form)

| tier | n | lemma prec | 95% CI | gloss prec | 95% CI |
|---|--:|--:|--:|--:|--:|
| dcs | 40 | 94.9% | 83.1–98.6 | 87.5% | 73.9–94.5 |
| vidyut | 40 | 71.8% | 56.2–83.5 | 79.5% | 64.5–89.2 |
| marker | 30 | 93.3% | 78.7–98.2 | 90.0% | 74.4–96.5 |

## By frequency band

| band | n | lemma prec | 95% CI | gloss prec | 95% CI |
|---|--:|--:|--:|--:|--:|
| hapax(1) | 30 | 79.3% | 61.6–90.2 | 80.0% | 62.7–90.5 |
| low(2-9) | 30 | 96.6% | 82.8–99.4 | 72.4% | 54.3–85.3 |
| mid(10-99) | 30 | 86.7% | 70.3–94.7 | 96.7% | 83.3–99.4 |
| high(100+) | 20 | 80.0% | 58.4–91.9 | 95.0% | 76.4–99.1 |

## Tier × frequency (lemma prec / gloss prec, n)

| tier \\ band | hapax(1) | low(2-9) | mid(10-99) | high(100+) |
|---|---|---|---|---|
| dcs | 78% / 70% (n=10) | 100% / 80% (n=10) | 100% / 100% (n=10) | 100% / 100% (n=10) |
| vidyut | 80% / 80% (n=10) | 89% / 44% (n=10) | 60% / 100% (n=10) | 60% / 90% (n=10) |
| marker | 80% / 90% (n=10) | 100% / 90% (n=10) | 100% / 90% (n=10) | – |

Disagreements sent to adversarial verify: **8** (resolved via gold/saru_gloss_verify.jsonl).

## Systematic lemma-defect classes (wave-3 targets)

The panel + adversarial verify converged on three recurring, *actionable* lemmatization error classes — concentrated in the **vidyut** tier (lemma prec 71.8 %, well below dcs 94.9 % / marker 93.3 %):

1. **ṛ/ṝ root-vowel length collapsed to short** — e.g. `kiranto` tagged `√kṛ` (do) instead of `√kṝ` (scatter); `anudīryate` tagged `√dṛ` instead of `√dṝ` (the `-īr-` passive betrays the heavy ṝ). A vowel-length-aware root match.
2. **Derived nominals lemmatized to a bare verbal root** — `janitṛ` (agent noun) → `jan`; `liṅgin` (possessive `-in`) → `liṅg`; `vidhunvāna` (participle of vi+dhū) → the noun `vidhu`. The nominal stem, not the root, is the lemma.
3. **Compound tokens lemmatized to their final member only** — `anartha-trivarga` → `trivarga`; `tridaśeśvara-nātha` → `nātha`. The marker/rightmost rule keeps only the last member, dropping the prior stem.

These directly shape wave 3: a recovered-but-mis-lemmatized form must count as a regression, not a coverage win.

_Dr. Mārcis Gasūns_
