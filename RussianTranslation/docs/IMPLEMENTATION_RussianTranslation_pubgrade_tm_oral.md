# IMPLEMENTATION — Publication-Grade Sa→Ru TM (finish H215), wave 1

_Created: 22-07-2026 · Last updated: 22-07-2026_

Implementation layer of the [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md).
File-level, dependency-ordered build steps for the three parallel tracks. Every printing script sets
`sys.stdout/stderr.reconfigure(encoding='utf-8')`; every output-capturing `subprocess.run` uses
`encoding='utf-8'`; no BOM. Multi-step logic goes in a `.py` file, not inline shell. Commit per step with
an `ai-wip:` prefix in the worktree; PR + auto-merge per track on green CI.

## Step 0 — spike S1: external API smoke-test (BLOCKS A2, A5) — do FIRST

`src/nn_api.py` — thin adapter over HuggingFace Inference API. Smoke-test in this order and pick the first
that serves in-environment; **log the choice**:
1. embeddings: `sentence-transformers/LaBSE` → 768-d vectors for a 5-pair Sa/Ru probe; confirm cosine
   separates a true pair from a mismatched one.
2. QE: a COMET-QE endpoint (e.g. `Unbabel/wmt22-cometkiwi-da` or an available reference-free COMET) on
   the same probe; confirm a monotone score.
- Fallbacks (logged, never stall): OpenAI/Cohere multilingual embeddings for #1; an LLM-as-judge QE proxy
  via the existing Claude-workflow / DeepSeek path for #2. Cache all responses on disk keyed by input hash.
- **Output:** `src/nn_api.py` + `research/nn_api_smoketest.md` (which model served, latency, cost/1k).
- **If nothing serves** → stop condition: mark A2/A5 blocked, keep A1/A3/A4 + Track B/C moving.

## Track A — technical hardening

**A1 — frozen gold grade sample** (no external dep; can start immediately).
- Driver: `src/build_grade_gold.py` — load the H136 stratified sample from `gold/`, emit a
  `/gold-adjudicate` worklist of segments needing an A/B/C label, add oral + prose strata rows.
- Human-gated adjudication round (surface via `/gold-adjudicate`); freeze to `gold/grade_gold.jsonl`.
- Report inter-annotator Cohen's κ to `gold/GRADE_GOLD_MEMO.md`.

**A2 — COMET-QE into the grader** (dep: S1, A1). Extend
[`src/tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py):
- add a `--qe comet` path calling `nn_api.qe(sa, ru)`; write `qe.{model,score}` into the record.
- calibrate: map COMET-QE score → A/B/C thresholds against `grade_gold.jsonl`; report Spearman ρ + a
  calibration band to `src/GRADE_CALIBRATION.md`. Keep the proxy as `--qe proxy` for A/B fallback.
- **Floor:** ρ ≥ 0.4 to claim "defensible"; below → keep proxy, mark grade preliminary (stop condition).

**A3 — awesome-align calibrated gate** (dep: A1 precision samples; independent of S1 if awesome-align runs
locally, else via `nn_api`). Extend
[`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py):
- persist a per-pair `align_confidence.agreement` column (awesome-align ∩ DeepSeek).
- bucket by agreement; adjudicate P/R against the committed precision samples
  ([`running_text_mining_precision_sample.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/running_text_mining_precision_sample.jsonl)).
- replace the flat 97 % gate with the calibrated threshold; write the curve to `src/ALIGN_GATE.md`.

**A4 — learned mined-tier filter** (dep: A3 method). `src/mined_filter_bicleaner.py`:
- Bicleaner-style features (length ratio, alignment score, LM/entropy) + a dual-model agree-gate over the
  10,132 `mined` pairs; P/R vs the H224 single-model baseline table; promote pairs above threshold.

**A5 — LaBSE/Vecalign sentence-aligner** (dep: S1; shared with B3). `src/tm_saru_align_labse.py`:
- embed Sa + Ru segments via `nn_api.embed`; margin-based candidate scoring; Vecalign for sequence
  alignment where order is monotone (prose). Pilot on the rights-clean Leitan Sundarakāṇḍa; precision@k
  on a hand-checked sample to `src/LABSE_ALIGN.md`. **Floor:** precision@sample ≥ 0.80.

**A6 — retrieval measurement** (dep: A2 graded TM). `src/tm_retrieval_eval.py`:
- fixed eval batch of cards; run the translate path (a) no-TM, (b) graded-TMX-as-fuzzy-context; report
  quality (judge severity) + wall-clock/token delta to `src/RETRIEVAL_EVAL.md`. Measurement only — does
  not wire retrieval into the production decode loop.

## Track B — oral-corpus formalization (in a SamudraManthanam worktree)

**B1 — schema extension** (PR to SamudraManthanam). Edit
[`docs/CONVERTER_SPEC.md`](https://github.com/gasyoun/SamudraManthanam/blob/main/docs/CONVERTER_SPEC.md):
add the optional `time_start`/`time_end`/`speaker`/`media_ref`/`source_channel`/`granularity` fields; state
back-compat (all optional). Add a schema-version bump note; do NOT touch existing 148-source records.

**B2 — oral converter** `web/corpus_builder/oral_transcript_to_canonical.py` (SamudraManthanam):
- input: per-talk text or PDF (raw Russian with embedded Sanskrit). PDF via the existing `pdftotext -enc
  UTF-8` path; handle the `\x0c` form-feed gotcha.
- Sanskrit-citation detection: script-run segmentation (Cyrillic vs Latin/IAST/Devanagari) + a known-text
  matcher against corpus work/passage keys.
- emit canonical JSONL (B1 schema) at three granularities: `sloka` (anchored citation), `turn` (speaker
  utterance), `term` (spoken term). Route `term` rows to the terminology feed (C1).

**B3 — oral alignment** (dep: A5, B2). In RussianTranslation, `src/build_oral_l0.py` (extend the H174
scaffold): verse-anchor `sloka` units by key-join; LaBSE-align (A5) the free `turn` units; write oral L0
pairs with `modality=oral`, `source_channel`, `media_ref`.

**B4 — oral grade + consume** (dep: A2, B3). Grade oral units via `tm_grade` with the **oral cap**
(`grade ≤ B` unless a written translation on the same key agrees → then A, per the 19-07 ruling). Feed the
TM via the content-addressed store as a `modality=oral` layer. Export into the combined TMX via
[`build_tmx.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py)
(a `modality` `prop`).

**B5 — rights-channel tagging** — ensure every oral unit carries `source_channel` + resolves to a release
class (public-full / derived-only / gated) via the C2 partition logic.

## Track C — publication / release preparation (NO publish)

**C1 — terminology dataset** (dep: MW-derived terms + A/B term feeds). `src/terminology_build.py`:
- curate Sa→Ru terms (MW-English → curated RU per D9, its hidden build step) + term-level oral/corpus
  pairs; emit `release/sa_ru_terminology/terminology.jsonl` + `manifest.json` (`term_count > 0`) +
  `DATASHEET.md`; reserve its own DOI slot (`doi_status: reserved`, NOT minted).

**C2 — release bundles** (dep: A2, B4, B5). `src/build_release_bundles.py`:
- partition every unit by release class; emit `release/corpus_tm/public_full.{tmx,jsonl}` (own/PD/cleared)
  and `release/corpus_tm/derived_only.{tmx,jsonl}` (structure only, NO grey RU surface text); keep the
  grey full-text bundle **gitignored**. Ensure НКРЯ-export field compatibility (TMX + TSV).

**C3 — data statement + datasheet** — align
[`TRANSLATION_MEMORY_DATASHEET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md)
to the Bender/Friedman ([`Q18-1041`](https://aclanthology.org/Q18-1041/)) + Gebru datasheet schema; embed
the per-source provenance + rights table (from the SamudraManthanam `.meta.json` sidecars).

**C4 — A42 fold-in** — update the [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) A42
row to name the TM as its resource contribution; add a resource section to the A42 draft; run `/articles-update`.

**C5 — publish packet** — `release/PUBLISH_PACKET.md`: per-source clearance-evidence checklist, the exact
public-vs-gitignored split, and the ordered `/publish-safety-check` → DOI-mint steps for a **human** to
execute. The agent stops here; it never publishes.

## Suggested handoff decomposition (Phase 5)

One handoff per track keeps unattended runs isolated and PR-scoped:
- **Track A** → Sonnet 5 (`claude-sonnet-5`) build, Opus 4.8 judge (A2/A4 need judgment).
- **Track B** → Opus 4.8 (`claude-opus-4-8`) (converter + alignment judgment; spans two repos).
- **Track C** → Sonnet 5 (`claude-sonnet-5`) (assembly + docs; release prep only).

_Dr. Mārcis Gasūns_
