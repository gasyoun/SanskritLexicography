# data/viz — static charts over committed census feeds

_Created: 23-07-2026 · Last updated: 23-07-2026_

Offline single-file HTML pages that **chart already-committed derived stats** —
they do not re-crawl csl-orig or corpus_lexicon.

| Page | Feed | Handoff |
|---|---|---|
| [markup_tag_heatmap.html](https://github.com/gasyoun/SanskritLexicography/blob/master/data/viz/markup_tag_heatmap.html) | [`../markup_tag_census.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv) | H683 / E39 / FAIR #1 |
| [ru_gloss_gaps.html](https://github.com/gasyoun/SanskritLexicography/blob/master/data/viz/ru_gloss_gaps.html) | [`../../RussianTranslation/glossary/ru_gloss_gap_stats.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossary/ru_gloss_gap_stats.json) | H685 |

## Rebuild

```bash
python data/viz/build_viz_pages.py
```

Stops with a clear error if either feed is missing. Does **not** regenerate the
TSV/JSON — only re-embeds them into the HTML.

## Explicit non-goals

- Headword Jaccard heatmap — already on
  [csl-atlas dictionary-overlap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-overlap.md).
- Committing `ru_gloss_gaps.tsv` (gitignored full gap list).

Generated snapshot date baked into the HTML: **2026-07-23** (H1527).

_Dr. Mārcis Gasūns_
