# Harvest recall — gold-standard measurement

_Created: 07-07-2026 · Last updated: 07-07-2026_

Companion to [precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md): that report asks "are the harvested pairs right?"; this one asks "of the Sanskrit content words the harvest saw, how many made it into [corpus_lexicon.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)?" (the 1.09M-row output itself is gitignored; link is to its builder).

> NOTE: like the precision report, this is an **LLM-adjudicated** estimate — a single frontier-model reading pass (Fable 5 `claude-fable-5`, H136 session, 07-07-2026), every token of every sampled group read against its source verse and published Russian translation. The frozen per-group labels ([recall_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_set.jsonl)) are the scaffold for a human spot-check.

## Group-level coverage (deterministic, not sampled)

Of the verse groups eligible for harvesting (a Sanskrit segment AND a Cyrillic-bearing Russian segment, works in `corpus_strata.json`), the share with ≥1 lexicon row — computed by `python src/gold_recall_sample.py coverage` over the full corpus:

| period | eligible groups | processed | coverage |
|---|---|---|---|
| Vedic | 16,472 | 16,463 | 99.9% |
| Epic / early-Classical | 37,681 | 37,401 | 99.3% |
| Classical | 3,323 | 2,996 | 90.2% |
| Medieval | 1,421 | 1,411 | 99.3% |
| **TOTAL** | **58,897** | **58,271** | **98.9%** |

## Word-level recall (adjudicated sample)

Sample: 32 processed groups, 8 per period stratum, seed=42 (`python src/gold_recall_sample.py sample 32`), 476 raw tokens → **287 unique content lemmata** after excluding particles, pronouns, copulas, and tokenization junk. Rubric per lemma:

- **covered** — the lexicon has a pair for it in this group (lemma/sandhi normalization allowed; a compound counts as covered when aligned whole OR via its member pairs);
- **miss-translated** — rendered in the published Russian but absent from the lexicon (**true recall loss**);
- **miss-untranslated** — no distinct Russian counterpart in this translation (the harvest prompt says omit these; reported separately, not a loss).

| metric | value |
|---|---|
| content lemmata | 287 |
| covered | 258 |
| miss-translated | 22 |
| miss-untranslated | 7 |
| **recall (covered / covered+miss-translated)** | **92.1%** (Wilson 95% CI 88.4–94.7) |
| coverage of all content lemmata | 89.9% |

### By stratum (period)

| stratum | content | covered | miss-tr | miss-untr | recall |
|---|---|---|---|---|---|
| Vedic | 73 | 71 | 2 | 0 | 97.3% |
| Epic / early-Classical | 49 | 42 | 4 | 3 | 91.3% |
| Classical | 81 | 77 | 3 | 1 | 96.3% |
| Medieval | 84 | 68 | 13 | 3 | 84.0% |

### Failure classes (the 22 true misses)

1. **Commentary-tail unaligned (13/22).** In groups that merge a mūla verse with its embedded prose commentary (Gītārthasaṃgraha above all), the harvest often aligned only the verse: group 6.44 alone contributes 8 misses (tāratamya, apavarga, śrīmat, geha, vighna, saṃsiddhi, mokṣātmikā, ah). Not absolute — sibling groups 2.20 and 5.22 show partially/fully aligned tails. This is why Medieval recall is the lowest stratum.
2. **Adverbs of time/manner dropped (5/22).** adya ×2, satatam ×2, parastāt — the "noun, verb, adjective" prompt wording steers the aligner away from adverbs even when the Russian renders them plainly (Теперь, всегда, вечно, после).
3. **Scattered single misses (4/22).** sarva ×2 (pronominal adjective, rendered «все/у всех»), eka («только лишь»), arh («подобает»), vid («не знают»), bhāvay, utpanna, pralī, gatasarvabhāvā — ordinary aligner omissions with no common cause.

### Caveats

- The Wilson CI treats lemmata as independent; they are cluster-sampled (32 groups), so the true interval is somewhat wider. The stratum gap (Medieval vs the rest) is driven by an identified structural cause, not noise.
- Recall is measured **within processed groups**; multiply by group-level coverage (98.9%) for end-to-end coverage of the eligible corpus: ≈ **91.1%** of translated content lemmata overall.
- Precision issues observed in passing (renderings swapped, wrong-sense pairs, src_ru span drift in range-merged sources) were noted in `recall_set.jsonl` but NOT counted here — they are the precision report's axis.

_Dr. Mārcis Gasūns_
