# Corpus lexicon — precision/recall memo for A42

_Created: 07-07-2026 · Last updated: 08-07-2026_

The single place A42 (Корпус санскритско-русских соответствий, [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)) should cite for evaluation numbers on the ~1,093,391-row Sanskrit→Russian word-alignment lexicon (`src/corpus_lexicon.jsonl`, gitignored; builder: [build_corpus_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py), DeepSeek, June 2026; targeted commentary-tail re-harvest [H309](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H309-Sonnet_RussianTranslation_corpus-lexicon-reharvest-gaps_07.07.26.md), 08-07-2026).

## Headline numbers

| axis | value | 95% CI | sample | status |
|---|---|---|---|---|
| **Precision** (good renderings) | **84.4%** | 80.0–87.9 | 320 pairs, stratified period×kind, seed=42 | LLM-judged (38-agent panel + adversarial verification, 2026-06-16); human packets pending |
| good + partial | 93.1% | — | same | same |
| **Recall** (word-level, within processed groups) | **95.4%** (was 92.1%) | 92.2–97.3 | 287 content lemmata / 32 groups, stratified by period, seed=42 | LLM-adjudicated (Fable 5 `claude-fable-5`, H136, 07-07-2026; Medieval stratum re-adjudicated post-re-harvest by Sonnet 5 `claude-sonnet-5`, H309, 08-07-2026); human spot-check pending |
| **Group-level coverage** (eligible groups with ≥1 row) | **98.9%** | — | full corpus scan, 58,897 eligible groups | deterministic |
| End-to-end coverage of translated content words | ≈94.3% (was 91.1%) | — | recall × group coverage | derived |

## Provenance

- **Precision:** [precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md); frozen scaffold [gold_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl); rubric [HUMAN_GOLD_PROTOCOL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md). Weakest strata: Classical/Medieval (78.8% each); commentary pairs err more than translation pairs (11.2% vs 2.5%). Not re-measured by H309 (recall-only fix).
- **Recall + coverage:** [recall_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_report.md); frozen per-group adjudication [recall_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_set.jsonl); sampler [gold_recall_sample.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_recall_sample.py). Weakest stratum: Medieval, **84.0%→95.1%** post-H309 — the mūla-only-alignment hypothesis was refined (the real cause was single-pass dilution on a dense fused verse+commentary `sa` blob, not a skipped `comm1` segment) and fixed for the 780-group genre-tagged commentary population via a widened, exhaustiveness-instructed prompt; 4 residual misses documented. Adverb-skip class: prompt fixed for all future harvests, not retroactively applied outside the re-harvested population.

## How A42 should phrase it

The resource is LLM-induced, not deterministic; both P and R are LLM-estimated with committed, re-checkable gold scaffolds awaiting human confirmation (packets under [reviewer_packets/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/gold/reviewer_packets)). Until the human pass completes, cite as "LLM-judged estimates over frozen stratified samples": precision 84.4% (95% CI 80.0–87.9, n=320 pairs), word-level recall 95.4% (95% CI 92.2–97.3, n=280 translated content lemmata, post-H309), group-level coverage 98.9% (n=58,897, deterministic). State the residual known weakness (a small number of adverb-class misses persist outside the 780-group commentary population re-harvested this pass; 4 residual commentary-class misses even within it) — bounded and documented, not eliminated.

_Dr. Mārcis Gasūns_
