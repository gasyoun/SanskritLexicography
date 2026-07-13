# «Санскрит в цифрах» — Wave 0: owned modules assembled

_Created: 13-07-2026 · Last updated: 13-07-2026_

> Assembles the modules already **owned** by sibling papers/datasets (modules 2 and 7 —
> cited, never recomputed here) plus modules 1/3/4 (owned data, one new computation: the
> Zipf coverage curve the roadmap flagged as "partial"). Executes Wave 0 of
> [ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md)
> under handoff [H813](https://github.com/gasyoun/Uprava/blob/main/handoffs/H813-Sonnet_SanskritLexicography_sanskrit_in_numbers_wave1_new_modules_12.07.26.md).
> Generator: [module0_wave0_assembly.py](module0_wave0_assembly.py) → [module0_wave0_owned_modules.json](module0_wave0_owned_modules.json).

## Module 1 — lemma vs token

**Owner:** [VisualDCS](https://github.com/gasyoun/VisualDCS) (DCS-2026 release). Cited, not recomputed.

| Metric | n | Source |
|---|---|---|
| Texts | 270 | VisualDCS DCS-2026 |
| Tokens | 5,688,416 | `DCS-data-2026/dcs_full.sqlite` |
| Sentences | 754,726 | same |
| Distinct lemmas attested | 90,349 | same, exact per-token join (see Module 3/4 caveat below re: the coarser published summary) |

## Module 2 — vocabulary size (union ≠ naive sum)

**Owner:** [A40 headword census](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md)
+ [A55 union index](https://github.com/gasyoun/kosha/blob/main/papers/A55_UNION_HEADWORDS_DATA_PAPER_JOHD.md)
+ [HEADWORD_OVERLAP_UNION15_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/HEADWORD_OVERLAP_UNION15_2026.md).
Cited, not recomputed — the family-only figures below are a **filter** of the
already-published 15-dict [union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
down to the Petersburg family (PWG+PWK+SCH, D6 basis), not a new census.

| Metric | n |
|---|---|
| Full 15-dict de-duplicated union | 323,425 |
| Petersburg family (PWG+PWK+SCH) headwords, naive sum | 285,799 |
| Petersburg family, de-duplicated union | 167,904 |
| **Naive-sum double-count inflation** | **+70.2%** |
| Headwords attested in all three (PWG ∩ PWK ∩ SCH) | 7,605 |
| PWG rows in the union | 106,054 |
| PWK rows in the union | 151,314 |
| SCH rows in the union | 28,431 |

**The caveat the portrait must state on its face (D2+D6):** PWK abridges PWG (finer
splitting inflates its own headword count even as it summarizes PWG), and SCH is an
addenda layer — summing `PWG + PWK + SCH` overstates true vocabulary size by **70%**. The
honest number is the de-duplicated union (167,904), not the naive sum (285,799).

## Module 3/4 — frequency, POS, and the Zipf coverage curve

**Owner:** [VisualDCS](https://github.com/gasyoun/VisualDCS) (DCS-2026 release) for the raw
frequencies; the coverage curve itself is **NEW this wave** (flagged "partial" in the
roadmap, not owned by a sibling paper) — computed once from the already-committed DCS-2026
corpus (`token.lemma_id` exact per-token counts, not the coarser `freqBand` (1–5) in
[dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json),
which cannot support a precise coverage curve).

**Duden's own headline stat:** "100 words cover about half the [running] text." Sanskrit's
answer, from DCS:

| Top-N lemmas | Cumulative tokens | % of corpus |
|---|---|---|
| 1 | 197,087 | 3.46% |
| 10 | 852,064 | 14.98% |
| 50 | 1,673,921 | 29.43% |
| **100** | **2,054,399** | **36.12%** |
| 200 | 2,485,217 | 43.69% |
| 500 | 3,190,620 | 56.09% |
| 1,000 | 3,776,049 | 66.38% |
| 2,000 | 4,361,773 | 76.68% |
| 5,000 | 5,002,905 | 87.95% |
| 10,000 | 5,333,485 | 93.76% |
| 20,000 | 5,525,765 | 97.14% |
| 50,000 | 5,645,261 | 99.24% |

Sanskrit's top 100 lemmas cover **36.1%** of the corpus versus German's ~50% for the
Dudenkorpus — a genuinely lower concentration, plausibly reflecting DCS's much smaller,
more genre-skewed (Vedic/śāstra/kāvya-heavy) corpus versus a balanced 5.2-billion-word
modern reference corpus. See [module0_wave0_owned_modules.json](module0_wave0_owned_modules.json)
for the top-20 lemma list and full curve.

**Honest scale caveat (repeat of the roadmap's own framing):** the Dudenkorpus is 5.2
**billion** word forms; DCS is 5.7 **million** — roughly a thousandfold smaller. Sanskrit has
no billion-word balanced contemporary corpus and never will, being a classical language.
Corpus-unattested ≠ non-existent (the A40 caveat carries over): a lemma absent from this
curve is unattested-in-DCS, not a ghost word.

## Module 7 — grammar-category (POS) distribution

**Owner:** [A56 Zaliznyak grammar-token index](https://github.com/gasyoun/kosha/blob/main/papers/A56_ZALIZNYAK_GRAMMAR_INDEX_DATA_PAPER_JOHD.md)
(kosha, release [data-v0.1.0](https://github.com/gasyoun/kosha/releases/tag/data-v0.1.0)).
Cited, not recomputed.

| Metric | n |
|---|---|
| PWG headwords classified | 98,639 |
| Distinct paradigm tokens (closed inventory) | 335 |

Module 8 of this wave (gender distribution) reuses the SAME already-released dataset's
`lex` column for a different cut (gender, not paradigm token) — legitimate reuse of a
committed asset, not duplication of A56's own novelty (the paradigm-token inventory
itself).

---

## Anti-salami boundary (restated)

Modules 2 and 7 are **cited, never re-derived** here, per the roadmap's §5. The
self-layering of the Petersburg family (why PWK's headword count exceeds PWG's) is
[A49](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)'s territory, not this
wave's. This file's only new computation is the Module 3/4 Zipf coverage curve.

## Wave 1 — the five NEW modules

Built separately, each with its own generator + dataset + trust block:

| # | Module | Generator | Dataset |
|---|---|---|---|
| 5 | akṣara / phoneme frequency | [module5_akshara_phoneme_freq.py](module5_akshara_phoneme_freq.py) | [module5_akshara_phoneme_freq.json](module5_akshara_phoneme_freq.json) |
| 6 | longest compounds | [module6_longest_compounds.py](module6_longest_compounds.py) | [module6_longest_compounds.json](module6_longest_compounds.json) |
| 8 | gender distribution | [module8_gender_distribution.py](module8_gender_distribution.py) | [module8_gender_distribution.json](module8_gender_distribution.json) |
| 9 | samāsa types (best-effort) | [module9_samasa_types.py](module9_samasa_types.py) | [module9_samasa_types.json](module9_samasa_types.json) |
| 10 | verb classes + voice | [module10_verb_class_voice.py](module10_verb_class_voice.py) | [module10_verb_class_voice.json](module10_verb_class_voice.json) |

See [WAVE1_SUMMARY.md](WAVE1_SUMMARY.md) for the headline numbers and trust blocks.

_Dr. Mārcis Gasūns_
