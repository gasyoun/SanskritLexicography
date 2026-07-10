# Corpus harvest layer (pwg_ru)

How the parallel corpus becomes **attested Russian senses** for each PWG
headword. This is the *reuse multiplier*: a sense PWG cites from the Ṛgveda
harvests the Russian that real translators used for that word in the Ṛgveda,
not a fresh machine rendering.

```
SamudraManthanam verse-aligned corpus
        │  (DeepSeek word-alignment, batched, stratified)
        ▼
corpus_lexicon.jsonl            SLP1 key → {ru, work, genre, period, date, kind}
        │
        ├── corpus_strata.json   genre (Renou) + date (Dharmamitra) + size per text
        ├── ls_source_map.json   PWG <ls> source → stratum + corpus works
        ▼
corpus_harvest.py  ──►  per headword: Russian renderings, lemma-grouped,
                        stratified by period/genre, counted, translation vs
                        commentary, with the cited stratum first
```

## Components

| File | Role |
|---|---|
| [src/build_corpus_lexicon.py](src/build_corpus_lexicon.py) | DeepSeek word-aligns each verse pair → `corpus_lexicon.jsonl` (SLP1-keyed, stratified). Cyrillic-guarded so untranslated placeholder verses are never aligned. |
| [src/build_strata.py](src/build_strata.py) → [src/corpus_strata.json](src/corpus_strata.json) | Classifies each corpus text: genre (Renou), date (Dharmamitra median + 95% CI), period bucket, size 1–5, genuine-translated group count. |
| [src/build_ls_map.py](src/build_ls_map.py) → [src/ls_source_map.json](src/ls_source_map.json) | Enumerates PWG `<ls>` citations and maps the major sources to strata. |
| [src/corpus_harvest.py](src/corpus_harvest.py) | The reader. SLP1 key → attested Russian, lemma-grouped (pymorphy3), POS-filtered, stratified, `<ls>`-cited stratum first. |
| [src/_audit.py](src/_audit.py) | Deterministic integrity check (run at each build milestone). |

## `<ls>` coverage (against real PWG citations)

PWG uses **772,534** `<ls>` citations across **3,554** distinct source keys.
The curated map covers the top **45** sources = **72.4%** of all citations:

- **corpus-harvestable: 29.8%** — the source has a Russian verse translation, so
  its senses harvest stratum-correct Russian. Biggest: MBH (67k → 18 parvas),
  ṚV (56k → 10 books), R (38k → ramayana), Manu (23k), AV (16k), Raghuvaṃśa,
  Gītā, Kumārasambhava, Meghadūta, Viṣṇu-Purāṇa.
- **stratum-tagged only: 42.6%** — lexica/Brāhmaṇas/grammar with no verse
  translation (Amarakośa, Hemacandra, Śatapatha-Br., Pāṇini…). These get a
  genre/period tag but fall back to the dictionary signals for the gloss.

## What the reader returns

`python src/corpus_harvest.py <slp1> [LS_KEY] [--raw]`

- **lemma-grouped**: царя/царю/царем collapse to **царь** (count summed, surface
  forms kept as evidence).
- **stratified**: renderings split by period + genre; the same word shows its
  era-specific Russian — e.g. `dharma` → **дхарма** in Manu (legal term) vs
  **добродетель / долг** (virtue / duty) in the Rāmāyaṇa.
- **`<ls>`-aware**: pass the PWG source key (e.g. `M` for Manu) and that stratum
  surfaces first (`◀ cited stratum`).
- **noise-filtered**: function-word and pronoun renderings are suppressed for
  content headwords; `--raw` (or an all-function stratum) keeps them so particle
  headwords like `ca` → **и / а / или** still harvest.
- **commentary-aware**: renderings tag `+comm` when commentary footnotes (not
  just the verse translation) attest them.

## Stratum coverage is build-dependent — check it

The corpus lexicon fills **biggest-first**, so strata fill unevenly while the
build runs. A sense cited from an empty stratum has no corpus Russian yet — do
not let it silently fall back to another era. Always check:

```
python src/corpus_harvest.py coverage
```

reports rows / keys / groups-done-vs-total / % per stratum and flags `EMPTY` /
`thin` strata. As of the mid-build snapshot only the Epic stratum is well-covered
(~44%); Ṛgvedic, Classical, and Medieval are still empty and fill as the
Rigveda / kāvya / later texts are processed. **Do not assemble print cards whose
`<ls>` resolves to a below-floor stratum until that stratum lands.**

## Next

- Wire the reader into [src/assemble.py](src/assemble.py): for each PWG sense,
  resolve its `<ls>` → stratum, harvest the top renderings of that stratum, and
  emit them as additional attested senses alongside the dictionary signals.
- A frequency floor + the content filter to keep only well-attested senses.
- Proper-name handling: a foreign name pymorphy3 doesn't know (e.g. Дашаратха)
  currently classes as content; harmless at low counts, refine if needed.
