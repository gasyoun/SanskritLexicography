# build_tmx.py — corpus Sa→Ru TM as TMX 1.4b + composite grader + L0/alignment

_Created: 06-07-2026 · Last updated: 07-07-2026_

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

TMX emits the **L1** (word/phrase) layer by default; **Slice 3** adds the **L0**
verse-segment layer (real `<tu segtype="block">` segment pairs) via `build --l0`,
and a real word-alignment cross-check — see
[the L0 + alignment section](#l0-verse-segment-layer--alignment-cross-check-slice-3)
below. The composite A/B/C grade is
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
| `alignment_confidence` | **real** (Slice 3) — [`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py) | grounding cross-check of every L1 pair vs its L0 verse (`proxy`), or SimAlign-style embedding alignment (`embed`); `grade --align <sidecar>` supersedes the old token-count proxy |

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

## L0 verse-segment layer + alignment cross-check (Slice 3)

Slice 3 adds the two pieces the L1-only exporter was missing: the **L0** layer (the
verse the word-pairs hang off) and a **real** `alignment_confidence`.

### L0 — the verse layer ([`src/build_l0.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_l0.py))

Where the corpus's L1 word-pairs came from is the **verse-aligned** Sanskrit↔Russian
text bundled in
[`SamudraManthanam/web/corpus_builder/jsonl/`](https://github.com/gasyoun/SamudraManthanam/tree/master/web/corpus_builder/jsonl)
— the same source DeepSeek word-aligned to *produce* L1. Each `group` there is one
verse with `seg=sa` (Sanskrit), `seg=ru` (the Russian translation) and `seg=comm*`
(Russian commentary notes). `build_l0.py` emits one L0 unit per verse-translation and
one per commentary note, stripping the interleaved edition/citation noise (`БхГ 1.1`,
daṇḍas, verse numbers) the corpus embeds in the Sanskrit. `group` is the join key
back to the L1 units in `corpus_lexicon.jsonl`.

```
python src/build_l0.py build            # SamudraManthanam corpus → release/corpus_tm/corpus_l0.jsonl
python src/build_l0.py status           # unit / work / token counts
python src/build_tmx.py build --l0 release/corpus_tm/corpus_l0.jsonl   # add L0 <tu segtype="block"> to the TMX
```

**Measured (07-07-2026, Opus 4.8 `claude-opus-4-8`).** The full corpus yields
**99,733 L0 units — 58,893 verse translations + 40,840 commentary notes — over 116
works** (mean 29.7 SLP1 tokens / 40.6 Russian tokens per unit). L0 `<tu>`s carry the
same provenance `<prop>` spine as L1 plus `segtype="block"`; source seg is the cleaned
SLP1 verse (`srclang="sa-slp1"`), IAST surface kept as `<prop type="surface">`. A
per-verse grade aggregated from the child L1 grades is a documented follow-up; L0 `<tu>`s
stamp `grade=C` for now.

### Alignment cross-check ([`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py))

For every DeepSeek L1 word-pair, an **independent** aligner asks "does this pairing
actually hold in the parent verse?" and writes a real per-unit `alignment_confidence`
that `tm_grade.py --align` consumes in place of the Slice-2 token-count proxy.

| Backend | Needs | What it scores |
|---|---|---|
| `proxy` (default) | nothing — deterministic, runs on the full corpus | **grounding**: is the L1 Sanskrit word a token of the L0 verse (form_key exact → 1.0; shared stem-prefix → 0.6)? are the L1 Russian rendering's stems present in the L0 Russian? `conf = 0.5·sa_ground + 0.5·ru_ground` |
| `embed` | `transformers` + a multilingual MLM (e.g. `bert-base-multilingual-cased`) | **SimAlign** (Jalili Sabet 2020): cosine of contextual subword embeddings, mutual-argmax links; per-unit confidence = max cosine between the sa token matching `slp1` and the ru tokens matching the rendering. Falls back to `proxy` if the package/model is absent, logged (same pattern as `--qe comet`) |

```
python src/tm_align.py cross  --l0 release/corpus_tm/corpus_l0.jsonl   # → release/corpus_tm/corpus_tm.align.jsonl
python src/tm_align.py agree                                           # confidence distribution + by-kind means
python src/tm_grade.py grade --align release/corpus_tm/corpus_tm.align.jsonl   # real align into the grade
```

**Measured (07-07-2026, `proxy` backend, full corpus).** Over all **1,091,528** L1
pairs: mean `alignment_confidence` **0.684**, **93.4 % grounded** in their verse; only
18 pairs (0.0 %) lacked an indexed parent. Distribution: 0.0 → **6.6 %**, (0,0.3] →
6.6 %, (0.3,0.6] → 27.1 %, (0.6,0.9] → 33.9 %, (0.9,1.0] → 25.8 %. The **6.6 % that
ground to nothing** — Sanskrit word not in the verse *and* Russian not in the
translation — are exactly the pairs the grade should distrust, a signal the shape-only
Slice-2 proxy could not see.

**Grade shift from the real cross-check (full corpus, `qe=proxy`).** Feeding the real
`alignment_confidence` into the grader moves the distribution the right way versus the
Slice-2 proxy baseline:

| Grade | Slice 2 (proxy align) | Slice 3 (real `tm_align`) |
|---|---|---|
| A (publication) | 5.7 % | **5.3 %** |
| B (corroborating) | 94.0 % | 93.8 % |
| C (usage-only) | 0.3 % | **0.9 %** (≈3×) |

The real aligner is more conservative than the token-count proxy: ungrounded pairs the
proxy over-credited now fall to C, and a few drop below the A gate — tightening the
publication-grade stamp, which is the point.

**`embed` proof-of-run (07-07-2026).** The SimAlign-style backend is not just a hook —
`bert-base-multilingual-cased` (layer 8) downloaded and ran on a 400-pair sample: mean
`alignment_confidence` 0.305, 56.5 % grounded. The numbers are lower than `proxy`
because this head-sample is Vedic Atharvaveda (the hardest text) and mBERT is weakly
trained on *transliterated* Sanskrit, so its cross-lingual cosines are muted; a
representative full-corpus `embed` run (or XLM-R / a Sanskrit-aware encoder) plus a
composite-weight retune is the documented next lift for the semantic discrimination the
reference-free signals still lack. Set `TM_ALIGN_MODEL` / `TM_ALIGN_LAYER` to try
another encoder.

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

## Slice 4 — the oral register

Recorded/spoken Sanskrit with a Russian rendering flows through this same L0 → grade
→ TMX pipeline via
[`src/ingest_oral.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ingest_oral.py)
(cleaned VTT/SRT transcript → `corpus_builder/<work>.jsonl` tagged `modality=oral`
with `t_start`/`t_end` time anchors + `source_media`). See
[`ORAL_INGEST.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ORAL_INGEST.md)
for the shared schema (coordinated with
[H174](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H174-Opus_spoken-sanskrit-corpus_spoken_sanskrit_corpus_scaffold_04.07.26.md)),
the grade policy, and the pilot results.

Two touch-points here: `l0_tu_xml` emits `modality`/`t_start`/`t_end`/`source_media`/
`asr_conf` props (absent on written L0, so written TMX is byte-unchanged), and the
shared `oral_cap()` — the **lowered base grade** — forbids grade **A** for an oral
unit on the automatic signals alone (capped at B; only human adjudication lifts it),
paired with `tm_grade.ORAL_PENALTY` on the composite. Fixture pilot: the same
corroborated units grade 6×A written vs 6×B oral.

## Rights — why the output is gitignored

`corpus_lexicon.jsonl` mixes public-domain and **in-copyright** named modern Russian
translations (Семенцов / Эрман / Сыркин / Смирнов / Васильков …). The TMX inherits
that, so the output directory `release/corpus_tm/` is gitignored exactly like the
lexicon. **No public release before per-translator rights clearance** — H215 Slice 5,
via [/publish-safety-check](https://github.com/gasyoun/Uprava) then
[/data-release](https://github.com/gasyoun/Uprava). Only this generator and this
README are committed.

_Dr. Mārcis Gasūns_
