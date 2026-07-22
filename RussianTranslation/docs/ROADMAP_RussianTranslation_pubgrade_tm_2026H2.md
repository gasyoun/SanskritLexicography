# ROADMAP — Publication-Grade Sa→Ru TM (finish H215), 2026 H2

_Created: 22-07-2026 · Last updated: 22-07-2026_

Roadmap layer of the [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md).
Three tracks run **in parallel** in wave 1 (R1.2). Each deliverable states what unblocks it.

## Wave 1 — three parallel tracks

### Track A — Technical hardening (ACL-defensible grade + gates + aligner)

| A# | Deliverable | Unblocked by | ACL method |
|---|---|---|---|
| A1 | **Frozen gold grade sample** — extend the H136 320-row stratified sample with an adjudicated A/B/C grade label per segment (+ oral/prose strata), report Cohen's κ | `/gold-adjudicate` over existing `gold/` sample; human adjudication round | reference for QE calibration |
| A2 | **COMET-QE integration** into [`tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py) — replace the hand-weighted proxy; report Spearman ρ vs the A1 gold + calibration band | A1 gold; HF Inference API smoke-test (spike S1) | COMET ([`2020.emnlp-main.213`](https://aclanthology.org/2020.emnlp-main.213/)) |
| A3 | **awesome-align calibrated gate** — turn [`tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py)'s agreement rate into a per-pair confidence replacing the flat 97 % threshold; agreement-bucket P/R | committed precision samples as gold | awesome-align ([`2021.eacl-main.181`](https://aclanthology.org/2021.eacl-main.181/)) |
| A4 | **Learned mined-tier filter** — Bicleaner-style per-pair score for the 10,132 `mined` pairs, superseding the flat gate; dual-model agree-gate | mined tier + precision samples | Bicleaner ([`2020.eamt-1.31`](https://aclanthology.org/2020.eamt-1.31/)) |
| A5 | **LaBSE/Vecalign sentence-aligner** (shared with Track B) — embedding margin-mining for anchorless segments; precision@sample on a hand-checked set | HF Inference API (spike S1); rights-clean pilot text (Leitan Sundarakāṇḍa) | LaBSE ([`2022.acl-long.62`](https://aclanthology.org/2022.acl-long.62/)) · margin ([`P19-1309`](https://aclanthology.org/P19-1309/)) · Vecalign ([`D19-1136`](https://aclanthology.org/D19-1136/)) |
| A6 | **Retrieval measurement** — does the graded TMX retrieved as fuzzy context improve draft quality/speed vs no-TM on a fixed card batch? report the delta | graded TM (A2); a fixed eval batch | Neural Fuzzy Repair ([`P19-1175`](https://aclanthology.org/P19-1175/)) |

### Track B — Oral-corpus formalization (from provided transcripts)

| B# | Deliverable | Unblocked by |
|---|---|---|
| B1 | **Schema extension** — optional `time_start`/`time_end`/`speaker`/`media_ref`/`source_channel` (own/systema/thirdparty/public) fields added to the SamudraManthanam canonical JSONL contract; back-compatible (all optional) | [`CONVERTER_SPEC.md`](https://github.com/gasyoun/SamudraManthanam/blob/main/docs/CONVERTER_SPEC.md) extension, PR to SamudraManthanam |
| B2 | **Oral converter** `oral_transcript_to_canonical.py` — ingest raw-Russian-with-embedded-Sanskrit (text + PDF via the existing `pdftotext` path); detect + segment Sanskrit citations; emit canonical JSONL at all three granularities | B1 schema; user-provided transcripts; PDF pipeline reuse |
| B3 | **Sa↔Ru oral alignment** — verse-anchor cited ślokas where a known text matches; LaBSE-align the free ones (reuses A5); term-extract for the terminology feed | B2 output; A5 aligner |
| B4 | **Oral grade + consume** — grade oral units (oral-alone caps at **B**; reaches **A** only when a written translation agrees, per the 19-07 ruling); consume via `build_oral_l0` into the TM as a graded `modality=oral` layer | B3 aligned pairs; A2 grader |
| B5 | **Rights-channel tagging** — every oral unit carries `source_channel` + `rights` so track C can partition clean vs grey at release time | B1 fields |

### Track C — Publication / release preparation (no auto-publish)

| C# | Deliverable | Unblocked by |
|---|---|---|
| C1 | **Terminology dataset populated** — the curated Sa→Ru terminology (D13) filled from MW-derived-then-curated terms + term-level oral/corpus pairs; own DOI path + datasheet drafted | R3.4; term-level feeds from A/B |
| C2 | **Release bundles prepared** — two-layer: full-text bundle (own/PD/cleared) + derived-layer bundle (Sanskrit/SLP1/alignments/grades/provenance) for grey; both TMX 1.4b + JSONL; НКРЯ-export-compatible | A2 grades; B4 oral; rights tags (B5) |
| C3 | **Bender/Friedman data statement + datasheet** — align [`TRANSLATION_MEMORY_DATASHEET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md) to the Bender/Friedman + Gebru schema; per-source provenance + rights table | corpus `.meta.json` rights; A/B/C outputs |
| C4 | **A42 fold-in** — wire the TM as A42's shipped resource contribution; update [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) row + the A42 draft resource section | C2/C3 artifacts |
| C5 | **Publish packet for the human gate** — assemble a `/publish-safety-check` packet: per-source clearance-evidence checklist, the exact public/gitignored split, the DOI-mint steps — for a human to execute | C2/C3; the fence forbids the agent doing the publish itself |

## Non-goals (explicitly out this span)

- **Auto-publishing anything** — no public push, visibility flip, Pages, or DOI mint by the agent (fence).
- **kNN-MT / retrieval-augmented decoding** inside the engine — A6 measures TM-as-context only; wiring retrieval into decoding is a later engine-side wave.
- **OntoLex-Lemon / TEI modelling** of the TMX — routes to csl-standards.
- **Prose corpus_builder ingestion internals** (GRETIL TEI machinery) — SamudraManthanam owns it (H308); Track A/B consume aligned output only.
- **Rebuilding** `corpus_lexicon.jsonl`, `corpus.db`, `build_tmx.py`, `tm_grade.py`, or the PDF pipeline.
- **Running the НКРЯ submission** — C2 keeps output export-compatible; the actual НКРЯ delivery is its own workstream (H753/H754).

## Later waves (post wave-1, not planned in detail here)

- **W2** — engine-side retrieval-augmented decoding (kNN-MT / Neural Fuzzy Repair in the translate loop), gated on A6's result.
- **W2** — VecMap unsupervised drift-audit channel (TM-H7), audit-only.
- **W2** — diachronic gloss-density section + viz over `corpus_strata.json` (TM-H4 / Viz-1) — low-cost, deferred only to keep wave 1 focused.
- **W3** — public release execution once per-source clearance completes (human-driven; the agent prepared everything in C5).

_Dr. Mārcis Gasūns_
