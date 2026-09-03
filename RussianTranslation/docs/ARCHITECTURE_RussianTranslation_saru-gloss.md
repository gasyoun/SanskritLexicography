# ARCHITECTURE — Sa→Ru gloss layer

_Created: 19-07-2026 · Last updated: 03-09-2026_

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
3b. **Marker head-form recovery (H3876)** — same split, but the rightmost element is itself
   *inflected* (`A-brahma-BuvanAt` → `BuvanAt`), so it is lemmatized through the **DCS**
   form→lemma map. Two measured guards: DCS keys only (vidyut lemmatizes compound-internal
   elements at 35/42, and wave 2 put the whole vidyut tier at 71.8 %) and head length ≥ 3
   (every 1–2 char head resolved to a pronoun homograph). Recovers 1,018 forms / 1,783 tokens
   of the 1,389-form marker residual. `source='marker-head'` — a separate tag, because this is
   the layer's weakest evidence and must stay filterable. Nothing is segmented here: the
   corpus's own marks supply the decomposition, which is why this is **not** the wave-3 cheda
   route that returned NO-GO. Evidence:
   [REPORT_H3876_saru_marker_head_recovery_03-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/REPORT_H3876_saru_marker_head_recovery_03-09-2026.md).
4. **Unresolved** — kept in Layer 1, characterised in the failure typology.

Provenance is carried per record (`source` field). **This tiering is exactly what wave 2 measures
per-tier** — the architecture's central assumption is that these heuristics produce correct
lemmatization. Wave 2 tested the first three (dcs 94.9 % · vidyut 71.8 % · marker 93.3 % lemma
precision, 3-judge panel, n=110:
[gold/saru_gloss_precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/saru_gloss_precision_report.md));
`marker-head` is registered in the `TIERS` tuple of the sampler and the aggregator but has only a
single-judge number so far (25/25 lemma) — the panel run for it is still owed.

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
