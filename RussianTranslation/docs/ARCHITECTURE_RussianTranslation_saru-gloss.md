# ARCHITECTURE — Sa→Ru gloss layer

_Created: 19-07-2026 · Last updated: 19-07-2026_

Index: [PLAN_RussianTranslation_saru-gloss-quality_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_saru-gloss-quality_2026H2.md).

## Current pipeline (as-built)

```
SamudraManthanam verse-aligned Sa↔Ru jsonl
        │  build_corpus_lexicon.py  (DeepSeek word-alignment)  ── FENCED, out of scope
        ▼
src/corpus_lexicon.jsonl  (1,091,528 aligned tokens, SLP1)   ── 290 MB, gitignored
        │  build_surface_glossary.py
        ▼
surface_glossary.jsonl  (190,838 forms → ranked Ru)  =  LAYER 1
        │
        │  build_dcs_maps.py ──► dcs_form2lemma.tsv (408,660) + dcs_lemma2root.tsv
        │  build_vidyut_fallback.py ──► vidyut_form2lemma.tsv (from surface_dcs_misses.tsv)
        ▼
build_rollup_glossaries.py  (two-pass bootstrap: rollup → vidyut → rollup)
        ├─► lemma_glossary.{jsonl,tsv}   (40,370)      =  LAYER 2
        ├─► root_glossary.{jsonl,tsv}    (2,021)       =  LAYER 3
        ├─► surface_dcs_misses.tsv   (Vidyut input, stable)
        ├─► surface_unresolved.tsv   (78,842, final typology)
        └─► ambiguity_homographs.tsv (9,521 DCS homographs)
        ▼
gasyoun/SanskritRussian  (published: data + index.html)  ── data files FENCED
```

## Resolution tiers (the join that this span validates)

Every form's lemma/root is attached by a **context-free** join (not per-passage), in a strict
precedence:

1. **DCS morphology (primary)** — `dcs_full.sqlite` (VisualDCS, 5.69 M tokens). Root of a prefixed
   verb lemma = **longest member of DCS's own simple-root inventory that is a suffix of the lemma**,
   min length 2 (sidesteps preverb sandhi: `uddhṛ` ← `ut`, not `ud`). `source='dcs'`.
2. **Vidyut kosha (fallback)** — Pāṇinian FST v0.4.0, only for DCS-missed forms, inserted with a
   synthetic count of 1 so it always sorts below DCS. Tiebreak: most entries, then shortest lemma.
   `source='vidyut'`.
3. **Morpheme-marker recovery** — forms carrying a corpus boundary mark (`A+gam`) split on `[+-]`;
   joined string retried as a form, else rightmost element if it is a known root/lemma. `source='marker'`.
4. **Unresolved** — kept in Layer 1, characterised in the failure typology.

Provenance is carried per record (`source` field). **This tiering is exactly what wave 2 measures
per-tier** — the architecture's central untested assumption is that these three heuristics produce
correct lemmatization, and no number has ever tested it.

## Component boundaries after this span

| Component | Owns | Changed by |
|---|---|---|
| `src/build_*.py` (pipeline) | The four build scripts + the two-pass bootstrap | W1.1–W1.3 (defect fixes), W3.2 (cheda hook) |
| `gold/` | Sampling, panel, agreement, human protocol | W2.1–W2.4 (new sampler + report **plug into** existing machinery — never rewrite it) |
| `gasyoun/SanskritRussian` | **Canonical** method/coverage/typology/accuracy doc + published data | W1.4/W1.5 docs only; data FENCED |
| `RussianTranslation/glossary/README.md` | Build runbook + pointer only (after W1.4) | W1.4 |
| pwg_ru/mw_ru TM path | Dictionary-card translation lookup | W4.1 (new consumer of the glossary) |

## Data model

- **Surface record** (JSONL): `slp1`, `sa`, ranked `ru` list, `kinds`, `periods`, `genres`,
  `registers`, sample `works` (SRC_CAP=25). TSV drops period/genre/kind facets.
- **Lemma/root record** (JSONL): `key`, `ru` (ranked), `n`, `n_total`, `n_forms`, `upos`, `source`,
  `registers`, `forms`, `lemmas`. TSV drops facets.
- **New in this span:** `dcs_lemma2root_unresolved.tsv` (W1.1), `vidyut_ambiguity.tsv` (W1.3),
  `gold/saru_gloss_sample.jsonl` + `gold/saru_gloss_precision_report.md` (W2).

## Build-vs-reuse verdicts (prior-art check, D7)

| Piece | Verdict | Evidence |
|---|---|---|
| Samāsa / compound splitter | **REUSE `vidyut.cheda`** | Installed v0.4.0, `import vidyut.cheda` OK. Never write a homegrown splitter. |
| Segmentation benchmark | **REUSE** `kosha/scripts/compare_sandhi_methods.py` + `kosha/app/segmenter.py` | Sibling repo already compares sandhi methods. |
| Gold sampling / agreement / protocol | **REUSE** `gold/gold_sample.py`, `gold_agreement.py`, `HUMAN_GOLD_PROTOCOL.md` | Full machinery exists from the alignment precision work (A42/A44). |
| LLM panel + adversarial verify | **REUSE** the `precision_report.md` pattern | Same shape already ran for `corpus_lexicon` (n=320, 84.4 %). |
| Transliteration | **REUSE** `indic_transliteration.sanscript` | Already the pipeline's transcoder; `sanskrit-util` consolidation is a separate later cleanup. |
| `sanskrit_parser` | **DO NOT depend** | Not installed in this environment. |

Nothing in this span is a from-scratch build of an existing asset.

_Dr. Mārcis Gasūns_
