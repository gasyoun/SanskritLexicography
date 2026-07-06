# build_tmx.py — corpus Sa→Ru TM as TMX 1.4b + composite grader

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
(real `<tu>` segment pairs) arrives with **Slice 3**. The composite A/B/C grade is
assigned by **Slice 2** ([`src/tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py),
below); `build_tmx build --grades <sidecar>` stamps those real grades. Without a
sidecar the exporter falls back to `grade=C` ("usage/citation only") — do **not**
hand-promote grades in the exporter.

## Composite grade — Slice 2 (`tm_grade.py`)

[`src/tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py)
assigns each unit the publication-grade **A/B/C** stamp MG specified, from a weighted
composite of four signals (weights versioned in the module, currently
qe 0.35 · source 0.30 · consensus 0.20 · align 0.15):

| Signal | This slice | Notes |
|---|---|---|
| `source_weight` | **real** — [`src/tm_source_weights.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_source_weights.json) | hand-ranked, versioned trust prior per work / translator / kind |
| `consensus` | **real** — computed over the whole corpus | distinct works giving a rendering for the same `(passage, slp1)`, and how far they agree |
| `qe_score` | pluggable — `proxy` (default) or `comet` | `proxy` = deterministic, reference-free **fluency/form** heuristic so it runs with no model; `comet` = COMET-QE (`Unbabel/wmt22-cometkiwi-da`) via `unbabel-comet` if installed |
| `alignment_confidence` | **proxy** (weighted low) | token-count plausibility; the real SimAlign / awesome-align score lands in **Slice 3** |

**Grade gates.** `A` = composite ≥ 0.70 **AND corroborated** (≥2 works agreeing,
≥50%) **OR** human-adjudicated — a publication/citable gloss. `B` = composite ≥ 0.55
(decent, single-reference, aligned — the corpus-signal role in `corpus_gate.py`).
`C` = everything else. The corroboration gate on `A` is deliberate: it is what makes
the stamp trustworthy, not the QE proxy alone.

```
python src/tm_grade.py grade [--in P] [--qe proxy|comet] [--sample N] [--out sidecar]
python src/tm_grade.py calibrate [--gold gold/gold_set.jsonl] [--in P]
python src/tm_grade.py selftest
python src/build_tmx.py build --grades release/corpus_tm/corpus_tm.grades.jsonl   # stamp real grades
```

**Measured (06-07-2026, `qe=proxy`, Opus 4.8 `claude-opus-4-8` orchestration).** Over
the full 1,091,528-unit corpus: **A 5.7% · B 94.0% · C 0.3%**. Every one of the 62,503
A units satisfies the consensus gate (0 violations) — A is driven by the
multi-translation clusters (Bhagavad-gītā ×10, repeated epic verses). Calibration on
the 320-row labelled [`gold/gold_set.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl)
shows **0 defective rows (`hallucinated`/`wrong-sense`/`partial`) ever reach A** — but
also that the reference-free proxy QE only weakly separates acceptable from defective
(ranking AUC ≈ 0.58): a **surface heuristic cannot detect wrong-sense** (a wrong gloss
is as fluent as a right one). Semantic discrimination therefore comes from *consensus*
and the *A-gate's conservatism*, not the proxy — which is precisely why `--qe comet`
(a trained adequacy model) and Slice 3's real aligner are the next lifts. The grades
sidecar is gitignored with the corpus; only the grader + weights table + this doc ship.

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
