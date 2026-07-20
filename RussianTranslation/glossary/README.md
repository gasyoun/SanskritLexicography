# Sanskrit → Russian glossary — generation pipeline (build runbook)

_Created: 01-07-2026 · Last updated: 20-07-2026_

**This directory holds only the generation pipeline** (`../src/build_*.py`). The data is
git-ignored here — regenerate it locally with the runbook below. The committed data, the
searchable site, and the **canonical documentation** (method, coverage, failure typology,
accuracy) live in the data repo:

> 📖 **Canonical doc:** [gasyoun/SanskritRussian · README.md](https://github.com/gasyoun/SanskritRussian/blob/main/README.md)
> — three layers (surface · lemma · root), the `√gam` worked example, the coverage table, the
> failure typology, and the **coverage ≠ accuracy** caveat.
> 🔎 **Live site:** <https://gasyoun.github.io/SanskritRussian/>

This repo's own GitHub Pages slot serves the PWG article dashboard (`gh-pages` branch), which
is why the glossary has its own repo.

## Pipeline scripts (this directory's `../src/`)

| Script | Stage | Emits |
|---|---|---|
| [`build_dcs_maps.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_maps.py) | B — DCS morphology | `dcs_form2lemma.tsv`, `dcs_lemma2root.tsv`, `dcs_lemma2root_unresolved.tsv` |
| [`build_surface_glossary.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_surface_glossary.py) | A — surface layer | `surface_glossary.jsonl` / `.tsv` (Layer 1) |
| [`build_rollup_glossaries.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_rollup_glossaries.py) | D — lemma/root rollup | `lemma_glossary.*`, `root_glossary.*`, `surface_dcs_misses.tsv`, `ambiguity_homographs.tsv` |
| [`build_vidyut_fallback.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_vidyut_fallback.py) | C — Vidyut fallback | `vidyut_form2lemma.tsv`, `vidyut_ambiguity.tsv` |
| [`build_ru_gloss_gap_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ru_gloss_gap_stats.py) | per-dict gap-list (H685) | `ru_gloss_gap_stats.json`, `ru_gloss_gaps.tsv` |
| [`measure_wave1_delta.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/measure_wave1_delta.py) | wave-1 delta (H1349) | prints the before/after defect-fix table |

Bucket filenames are **case-folded to upper** (`a` and `A` share one file): SLP1 is
case-significant but Windows' filesystem is case-insensitive, so separate `a`/`A` files would
collide and truncate. The phonemic distinction is preserved inside each record's `slp1` field.

## Regenerate (two-pass bootstrap)

From [`RussianTranslation/src/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src):

```sh
python build_dcs_maps.py            # DCS form→lemma + lemma→root maps   (needs VisualDCS dcs_full.sqlite)
python build_surface_glossary.py    # Layer 1
python build_rollup_glossaries.py   # 1st pass: emits surface_dcs_misses.tsv (Vidyut input)
python build_vidyut_fallback.py <kosha_dir>   # lemmatize the DCS misses (needs vidyut.download_data())
python build_rollup_glossaries.py   # 2nd pass: folds in Vidyut + marker tier -> Layers 2 & 3
```

The rollup emits the DCS-miss list the Vidyut stage consumes, so run it **once before Vidyut
and once after**. `surface_dcs_misses.tsv` is snapshotted before the Vidyut supplement, so the
second pass does not disturb the Vidyut input.

Vidyut data: `python -c "import vidyut; vidyut.download_data('vidyut_data')"`, then pass
`vidyut_data/kosha` to the fallback. Transcoding uses `indic_transliteration`; both are
pip-installable. `vidyut` and `indic_transliteration` are imported **lazily** (inside
`main()` / `to_slp1()`), so the pure helpers are unit-testable without them installed — see
[`tests/test_saru_gloss_pipeline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_saru_gloss_pipeline.py).

_Dr. Mārcis Gasūns_
