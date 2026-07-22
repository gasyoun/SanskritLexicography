# VERIFICATION — Publication-Grade Sa→Ru TM (finish H215)

_Created: 22-07-2026 · Last updated: 22-07-2026_

Verification layer of the [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md).
Acceptance criteria per deliverable, the command/flow that proves each, and the risks/spikes register.

## Acceptance criteria

| Deliverable | Passes when | Proof command / flow |
|---|---|---|
| S1 API smoke-test | one embedding + one QE endpoint serve in-env (or a logged fallback does); probe separates true vs mismatched pair | `python src/nn_api.py --smoketest`; read `research/nn_api_smoketest.md` |
| A1 gold | `gold/grade_gold.jsonl` frozen with A/B/C labels + strata; κ reported | `python src/build_grade_gold.py --verify`; κ in `gold/GRADE_GOLD_MEMO.md` |
| A2 COMET-QE | grade path runs; **Spearman ρ ≥ 0.40** vs gold; calibration band written | `python src/tm_grade.py --qe comet --calibrate`; ρ in `src/GRADE_CALIBRATION.md` |
| A3 aligner gate | per-pair `align_confidence.agreement` persisted; calibrated gate beats the flat 97 % line on the precision samples | `python src/tm_align.py --calibrate`; curve in `src/ALIGN_GATE.md` |
| A4 mined filter | P/R reported vs the H224 baseline; promoted set written | `python src/mined_filter_bicleaner.py --report` |
| A5 LaBSE aligner | **precision@sample ≥ 0.80** on the hand-checked Leitan Sundarakāṇḍa pilot | `python src/tm_saru_align_labse.py --pilot leitan_sundara`; number in `src/LABSE_ALIGN.md` |
| A6 retrieval | quality + wall-clock/token delta (TM vs no-TM) reported on the fixed batch | `python src/tm_retrieval_eval.py --batch eval`; `src/RETRIEVAL_EVAL.md` |
| B1 schema | optional fields added; existing 148-source corpus re-ingests unchanged (byte-identical for old fields) | SamudraManthanam converter selftest; diff a re-ingested source vs committed jsonl |
| B2 converter | one provided transcript → canonical JSONL at all 3 granularities; round-trips; Sanskrit detected | `python web/corpus_builder/oral_transcript_to_canonical.py --selftest <talk>` |
| B3 alignment | anchored ślokas key-join; free turns LaBSE-aligned; oral L0 emitted with `modality=oral` | `python src/build_oral_l0.py --verify` |
| B4 grade/consume | oral units graded with the cap (≤ B unless a written translation agrees); appear in the combined TMX with `modality` prop | `python src/build_tmx.py --grades <sidecar> --include-oral`; grep `<prop type="modality">oral` |
| C1 terminology | `term_count > 0`; manifest + datasheet present; DOI slot **reserved not minted** | `python src/terminology_build.py --verify`; check `manifest.json` |
| C2 bundles | public-full has NO grey RU text; derived-only has NO RU surface text at all; grey full-text stays gitignored | `python src/build_release_bundles.py --audit-rights` (asserts 0 grey RU strings in any tracked bundle) |
| C3 datasheet | Bender/Friedman + Gebru sections filled; per-source rights table present | markdown lint + a checklist review |
| C4 A42 | ARTICLES A42 row names the TM resource; A42 draft has the resource section | `/articles-update` dry-run; diff |
| C5 packet | `PUBLISH_PACKET.md` lists per-source clearance evidence + the human publish steps | review; the packet exists and the agent did NOT publish |

**Global gate:** the SanskritLexicography CI `RussianTranslation gates` job compiles the pipeline scripts +
runs their fixture selftests; every PR must be green before auto-merge. Markdown lint + link-check clean.

## The one test that matters most

`python src/build_release_bundles.py --audit-rights` — it is the machine proof of the fence. It must assert
that **no tracked release bundle contains any grey/no-redistribution Russian surface text** (0 hits), so a
copyright leak cannot slip into a public artifact even by accident. If this fails, halt track C.

## Risks & spikes register

| Risk | Likelihood | Impact | Mitigation / spike |
|---|---|---|---|
| **External API can't serve LaBSE/COMET in-env** | Med | High (blocks A2/A5) | **Spike S1 first.** Logged fallbacks (OpenAI/Cohere embeddings; LLM-as-judge QE). If all fail, A1/A3/A4 + B + C still proceed; grade stays proxy-preliminary. |
| **Rights leak** — grey RU text reaches a public bundle | Low | Severe (copyright) | The `--audit-rights` gate (0-grey-string assertion); the fence forbids publish entirely; human `/publish-safety-check` before go-live. |
| **COMET-QE doesn't transfer to Sa→Ru** (ρ < 0.4) | Med | Med | Documented floor → keep proxy, mark preliminary; this is itself a publishable low-resource-QE result (memo TM-H2). |
| **LaBSE weak on transliterated Sanskrit** (FINDINGS §65: mBERT is) | Med | Med | Pilot precision@sample gate before bulk; try XLM-R / a Sanskrit-aware encoder as the S1 fallback; anchored ślokas don't need embeddings. |
| **Transcript format varies** (raw RU + Sanskrit, PDF) | Med | Med | Converter normalizer + `\x0c` handling; per-talk selftest before batch; unresolved Sanskrit spans logged, not dropped. |
| **DeepSeek-style hallucination** (the 166k-invention class) recurs in a generative step | Low | High | Reuse the `has_cyr()` / never-invent guards; the `--audit-rights` + grounding cross-check (`tm_align`) catch placeholder leakage. |
| **SamudraManthanam schema change breaks the 148-source corpus** | Low | High | All new fields optional; re-ingest-diff selftest (B1 acceptance) proves byte-identity on old fields. |
| **Parallel tracks collide on shared files** (`tm_grade.py`, `build_tmx.py`) | Med | Med | One handoff per track in separate worktrees; A owns `tm_grade.py`, B consumes it read-only until A merges; sequence A2 before B4. |
| **Two sessions on the same handoff** | Low | Med | Session-unique worktree names (`-<pid>`); collision surfaces harmlessly at push (non-fast-forward). |

## Spikes to run before committing to the architecture

- **S1 (blocking):** external embedding + QE API liveness (Step 0 above).
- **S2:** one real user-provided transcript through B2 end-to-end, to validate the Sanskrit-detection +
  three-granularity split before building the batch path.
- **S3:** confirm `tm_grade.py`/`build_tmx.py` accept an added `modality`/`qe` field without breaking the
  existing 2,392-record release manifest validation (`translation_memory.py validate`).

_Dr. Mārcis Gasūns_
