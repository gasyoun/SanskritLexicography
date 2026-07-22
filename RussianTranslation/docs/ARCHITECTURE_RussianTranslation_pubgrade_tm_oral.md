# ARCHITECTURE — Publication-Grade Sa→Ru TM (finish H215)

_Created: 22-07-2026 · Last updated: 22-07-2026_

Architecture layer of the [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md).
Component boundaries, data model, interfaces, and the build-vs-reuse verdict per piece.

## Component map (what exists vs what this span adds)

```
                 SamudraManthanam (corpus owner)                RussianTranslation (TM owner)
 provided        corpus_builder/jsonl (verse, markup-aligned)   src/build_l0.py  --> L0 verse layer  [reuse]
 transcripts --> [NEW] oral_transcript_to_canonical.py  ------> src/build_oral_l0.py --> L0 oral layer [extend scaffold]
 (text+PDF)      [NEW] schema ext: time/speaker/media_ref        src/corpus_lexicon.jsonl --> L1 word [reuse, read-only]
                 corpus.db (FTS5) + /api/morph|search|compare    src/tm_align.py  --> [UPGRADE] awesome-align gate
                                                                 src/tm_grade.py  --> [UPGRADE] COMET-QE
                                                                 [NEW] src/tm_saru_align_labse.py (LaBSE/Vecalign)
                                                                 [NEW] src/mined_filter_bicleaner.py
                                                                 src/build_tmx.py --> TMX 1.4b (L0+L1+oral) [reuse]
                                                                 [NEW] src/terminology_build.py --> D13 dataset
                                                                 [NEW] src/tm_retrieval_eval.py --> A6 measurement
                                                                 release/ bundles (prepared, NOT published)
external API (HF Inference): LaBSE embeddings + COMET-QE   <---- used by tm_saru_align_labse.py, tm_grade.py
```

Legend: `[reuse]` untouched · `[UPGRADE]` extend an existing module · `[NEW]` new file · `[extend scaffold]` build on H174 stubs.

## Data model

### TM publication record — REUSE, do not change the contract
The publication contract [`schemas/translation_memory.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/translation_memory.schema.json)
("PWG Translation Memory Publication Contract v1") already carries `trust_level`, `reuse_policy`, three
fuzzy score channels, `gate_status`/`gate_version`, `source_hashes`, `provenance`, `evidence[]`,
`supersedes`. **New fields this span needs are additive** (bump to a v1.1, never break v1):

- `qe`: `{ model: "comet-qe", score: float, calibrated_grade: A|B|C, gold_rho: float }` — from A2.
- `align_confidence`: `{ method: "awesome-align"|"labse", agreement: float, gated: bool }` — from A3/A5.
- `modality`: `written|oral` — oral units set this; grade cap enforced downstream (oral ≤ B unless a written translation agrees).
- `source_channel`: `own|systema|thirdparty|public|corpus` — drives the rights partition.

### Oral canonical record — EXTEND the SamudraManthanam schema (B1)
Add to the canonical JSONL contract ([`CONVERTER_SPEC.md`](https://github.com/gasyoun/SamudraManthanam/blob/main/docs/CONVERTER_SPEC.md)),
**all optional / back-compatible** (existing 148-source corpus unaffected):

| Field | Type | Meaning |
|---|---|---|
| `time_start` / `time_end` | float (sec), optional | utterance window in the source media |
| `speaker` | string, optional | speaker label / turn owner |
| `media_ref` | string, optional | source media id (talk slug / URL id), NOT the media itself |
| `source_channel` | enum, optional | own / systema / thirdparty / public |
| `granularity` | enum | `sloka` / `turn` / `term` (the three oral units, R2.2) |

Group id keeps the existing `{work}:{passage}` form for verse-anchored oral units; free (unanchored)
oral units use `{talk_slug}:{seq}` with `granularity=turn`. Term-level units route to the terminology
dataset (C1), not the verse TM.

### Rights partition — the release contract (C2)
Every unit resolves to exactly one release class from `source_channel` + the per-source `rights` field
in the SamudraManthanam `.meta.json` sidecars:

- **public-full** — own / PD / cleared: full text (Sanskrit + Russian) publishable.
- **derived-only** — grey / no-redistribution / third-party / public-video: publish structure only
  (Sanskrit, SLP1 keys, alignments, grades, provenance); the Russian surface text stays gitignored.
- **gated** — anything whose rights are unknown/ambiguous: held entirely until clearance (stop condition R4.1(c)).

## Interfaces & contracts

1. **SamudraManthanam corpus query** — consume, do not duplicate. For aligned pairs, either the exporters
   ([`build_l0.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_l0.py))
   or a direct read of `corpus.db` (`SELECT canonical_id, line_text FROM corpus_lines WHERE ... LIKE '%#sa'`).
   Note the API caveat: `SearchResultItem` does **not** expose `canonical_id`/`group` — use the exporters or
   the DB for TM segment pairing (documented in the audit; do not rely on `/api/search` alone for group ids).
2. **External embedding + QE API** (R5.4) — HuggingFace Inference API: `sentence-transformers/LaBSE` for
   embeddings, a COMET-QE endpoint for quality. A thin adapter `src/nn_api.py` wraps both with:
   batching, on-disk response cache (deterministic, keyed by input hash), and a **logged fallback** — if a
   model won't load/serve, substitute an alternative endpoint and record the substitution (never stall).
   Keys live in the gitignored `src/.env` (existing pattern: `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`;
   add `HF_API_TOKEN`).
3. **Oral converter contract** — input is a per-talk file (text or PDF) of raw Russian with embedded
   Sanskrit; output is canonical JSONL conforming to the B1 schema. A normalizer maps common shapes
   (plain text, PDF-via-pdftotext) into the converter's expected pre-parse form; the `\x0c` form-feed
   gotcha from the PDF pipeline is handled (documented in [`PDF_INGESTION_PIPELINE.md`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/corpus_builder/PDF_INGESTION_PIPELINE.md)).
4. **Sanskrit-in-Russian detection** — script/citation detector: Cyrillic-vs-Latin/Devanagari run
   segmentation + a known-text matcher against corpus work/passage keys for anchoring. SLP1 keys via the
   length-preserving `form_key()` (never NFD-strip, per the IAST-normalization findings).

## Build-vs-reuse verdict (prior-art cited)

| Piece | Verdict | Evidence |
|---|---|---|
| TMX 1.4b exporter, grader, aligner cross-check, L0 builder, content-addressed TM, publication schema | **REUSE** | [SHARED_CODE §10](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) — "Don't write a second TMX emitter or grader." |
| Word-alignment lexicon `corpus_lexicon.jsonl` (1.09 M) | **REUSE, read-only** | NOT rebuildable ([SHADOW_ASSETS_POINTERS](https://github.com/gasyoun/Uprava/blob/main/SHADOW_ASSETS_POINTERS.md)). |
| SamudraManthanam PDF pipeline + corpus.db + query API | **REUSE** | [PDF_INGESTION_PIPELINE.md](https://github.com/gasyoun/SamudraManthanam/blob/main/web/corpus_builder/PDF_INGESTION_PIPELINE.md); query, don't duplicate. |
| COMET-QE grade | **BUILD** (integrate external model) | `tm_grade.py` proxy near-useless for adequacy (FINDINGS §70). |
| awesome-align calibrated gate | **BUILD** (upgrade `tm_align.py`) | ACL_TM_CROSSWALK_MEMO §1 P0. |
| LaBSE/Vecalign sentence-aligner | **BUILD** | No cross-language Sa→Ru sentence aligner exists (SHARED_CODE §18: helayo is intra-language only). |
| Bicleaner mined-tier filter | **BUILD** | Replaces H224 flat 97 % threshold. |
| Oral schema + converter | **BUILD** (extend H174 scaffold) | Oral corpus is greenfield (SamudraManthanam audit: no audio/transcript/media field exists). |
| Terminology dataset population | **BUILD** | D13 scaffolded, `term_count: 0`. |
| Retrieval measurement | **BUILD** | H215 states "feeds the engine"; unmeasured (memo §4e). |

_Dr. Mārcis Gasūns_
