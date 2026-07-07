# Corpus lexicon — precision/recall memo for A42

_Created: 07-07-2026 · Last updated: 07-07-2026_

The single place A42 (Корпус санскритско-русских соответствий, [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)) should cite for evaluation numbers on the 1,091,528-row Sanskrit→Russian word-alignment lexicon (`src/corpus_lexicon.jsonl`, gitignored; builder: [build_corpus_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py), DeepSeek, June 2026).

## Headline numbers

| axis | value | 95% CI | sample | status |
|---|---|---|---|---|
| **Precision** (good renderings) | **84.4%** | 80.0–87.9 | 320 pairs, stratified period×kind, seed=42 | LLM-judged (38-agent panel + adversarial verification, 2026-06-16); human packets pending |
| good + partial | 93.1% | — | same | same |
| **Recall** (word-level, within processed groups) | **92.1%** | 88.4–94.7 | 287 content lemmata / 32 groups, stratified by period, seed=42 | LLM-adjudicated (Fable 5 `claude-fable-5`, single reading pass, 07-07-2026); human spot-check pending |
| **Group-level coverage** (eligible groups with ≥1 row) | **98.9%** | — | full corpus scan, 58,897 eligible groups | deterministic |
| End-to-end coverage of translated content words | ≈91.1% | — | recall × group coverage | derived |

## Provenance

- **Precision:** [precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md); frozen scaffold [gold_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl); rubric [HUMAN_GOLD_PROTOCOL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md). Weakest strata: Classical/Medieval (78.8% each); commentary pairs err more than translation pairs (11.2% vs 2.5%).
- **Recall + coverage:** [recall_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_report.md); frozen per-group adjudication [recall_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_set.jsonl); sampler [gold_recall_sample.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_recall_sample.py). Weakest stratum: Medieval (84.0%), driven by a structural failure class — mūla-only alignment of verse+commentary groups; runner-up class: temporal/manner adverbs skipped by the noun/verb/adjective prompt wording.

## How A42 should phrase it

The resource is LLM-induced, not deterministic; both P and R are LLM-estimated with committed, re-checkable gold scaffolds awaiting human confirmation (packets under [reviewer_packets/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/gold/reviewer_packets)). Until the human pass completes, cite as "LLM-judged estimates over frozen stratified samples": precision 84.4% (95% CI 80.0–87.9, n=320 pairs), word-level recall 92.1% (95% CI 88.4–94.7, n=280 translated content lemmata), group-level coverage 98.9% (n=58,897, deterministic). State the two known systematic weaknesses (Medieval commentary tails; adverb skips) — they are findable, bounded, and fixable by a targeted re-harvest.

_Dr. Mārcis Gasūns_
