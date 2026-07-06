# build_tmx.py — corpus Sa→Ru TM as TMX 1.4b

_Created: 06-07-2026 · Last updated: 06-07-2026_

[`src/build_tmx.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py)
is **Slice 1 of [H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md)**
— the cheapest publication-grade representation of the corpus translation memory.
It turns the word-aligned corpus lexicon into a standards-compliant
[TMX 1.4b](https://www.gala-global.org/tmx-14b) interchange artifact that is both a
citable resource and a retrieval feed for the pwg_ru engine.

## What it reads and writes

- **Input:** [`src/corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src)
  (gitignored) — DeepSeek **L1** units, one row per aligned Sanskrit content word ↔
  Russian rendering, produced by
  [`src/build_corpus_lexicon.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)
  and stratified by
  [`src/corpus_strata.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_strata.json)
  (work → genre/period/date).
- **Output:** `release/corpus_tm/corpus_tm.sa-ru.tmx` (**gitignored**, rights — see below).

Each L1 unit becomes one TMX `<tu>`:

- source `<tuv xml:lang="sa-slp1">` → the **SLP1 key** (matches the header `srclang`);
  the printed surface Sanskrit is kept as `<prop type="surface">`.
- target `<tuv xml:lang="ru">` → the Russian rendering.
- `<prop>`s carry the full provenance/grading spine:
  `layer` (L1), `grade`, `modality`, `kind`, `surface`, `work`, `passage`, `group`,
  `genre`, `period`, `date`.

## Layers and grade (H215 architecture)

TMX today emits the **L1** (word/phrase) layer; the **L0** verse-segment layer
(real `<tu>` segment pairs) arrives with **Slice 3**. Every unit is stamped
**`grade=C`** ("usage/citation only") until the composite grader
(**Slice 2**, `src/tm_grade.py`: COMET-QE + source-weight + alignment confidence +
consensus → A/B/C) assigns a real grade. Do **not** hand-promote grades in this
exporter.

## Usage

```
python src/build_tmx.py build                 # corpus_lexicon.jsonl → release TMX
python src/build_tmx.py build --sample 500     # first 500 L1 units (reviewable slice)
python src/build_tmx.py build --in PATH --out PATH
python src/build_tmx.py validate <file.tmx>    # round-trip parse + structural checks
python src/build_tmx.py selftest               # fixture → export → re-parse, assert
```

- Fixture input for CI/demo:
  [`src/fixtures/corpus_lexicon.fixture.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/fixtures/corpus_lexicon.fixture.jsonl).
- `build` self-validates its output (round-trip parse); a failed validation is a
  non-zero exit.
- [`src/_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_audit.py)
  round-trip-validates the release TMX when it is present.

## Never-invent guards

The exporter re-applies the same invariants
[`_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_audit.py)
enforces on the lexicon, at export time, so a contaminated row can never reach a
published TMX (the 166k-hallucination lesson,
[FAILURE_GALLERY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/failures/FAILURE_GALLERY.md)
F1): rows with a non-Cyrillic `ru`, an empty SLP1 key, or `ru == sa` are dropped.
`tuid`s are content-derived (deterministic — no clock/random), so the same lexicon
yields byte-identical TMX.

## Rights — why the output is gitignored

`corpus_lexicon.jsonl` mixes public-domain and **in-copyright** named modern Russian
translations (Семенцов / Эрман / Сыркин / Смирнов / Васильков …). The TMX inherits
that, so the output directory `release/corpus_tm/` is gitignored exactly like the
lexicon. **No public release before per-translator rights clearance** — H215 Slice 5,
via [/publish-safety-check](https://github.com/gasyoun/Uprava) then
[/data-release](https://github.com/gasyoun/Uprava). Only this generator and this
README are committed.

_Dr. Mārcis Gasūns_
