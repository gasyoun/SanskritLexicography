# Harvest precision — gold-standard measurement (2026-06-16)

A stratified random sample of 320 corpus-lexicon alignments (seed=42, balanced across period × kind), each judged against its source verse, errors adversarially verified. "Precision" = correct + lemma-variant + proper-name (accurate renderings); partial = marginal; errors = wrong-sense + hallucinated.

> NOTE: this is an **LLM-judged** estimate (38-agent panel + adversarial verification of every flagged error). The frozen sample (`gold_set.jsonl`) is the scaffold for a human spot-check, which would confirm/adjust these numbers.

## Overall

| metric | value |
|---|---|
| sample size | 320 |
| **precision (good)** | **84.4%**  (95% CI 80.0–87.9) |
| partial (marginal) | 8.8% |
| errors (wrong-sense + hallucinated) | 6.9% |
| good + partial | 93.1% |

## By stratum (period)

| stratum | n | precision | 95% CI | partial | errors |
|---|---|---|---|---|---|
| Vedic | 80 | 90.0% | 81.5–94.8 | 3.8% | 6.2% |
| Epic / early-Classical | 80 | 90.0% | 81.5–94.8 | 6.2% | 3.8% |
| Classical | 80 | 78.8% | 68.6–86.3 | 11.2% | 10.0% |
| Medieval | 80 | 78.8% | 68.6–86.3 | 13.8% | 7.5% |

## By kind

| kind | n | precision | 95% CI | partial | errors |
|---|---|---|---|---|---|
| translation | 160 | 86.9% | 80.8–91.3 | 10.6% | 2.5% |
| commentary | 160 | 81.9% | 75.2–87.1 | 6.9% | 11.2% |

## Label distribution

correct: 200 · lemma-variant: 46 · proper-name: 24 · partial: 28 · wrong-sense: 13 · hallucinated: 9
