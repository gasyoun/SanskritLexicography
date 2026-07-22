# PLAN — Publication-Grade Sa→Ru Translation Memory: finish H215 (3 parallel tracks)

_Created: 22-07-2026 · Last updated: 22-07-2026_

Cover/index for a `/ask` layered plan. Scope: **finish** the Publication-Grade
Sanskrit→Russian Translation Memory ([H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md))
— it is ~70 % built (Slices 1–4 merged) — by driving three parallel tracks:
**(A) technical hardening**, **(B) oral-corpus formalization**, **(C) publication/release prep**.
Owner repo: [`SanskritLexicography/RussianTranslation`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation);
one consumed edge into [`SamudraManthanam`](https://github.com/gasyoun/SamudraManthanam) (oral schema + converter).

This is the doc a wave-1 execution handoff points at. Everything a builder needs is here or in the four layer docs:

- Roadmap → [ROADMAP_RussianTranslation_pubgrade_tm_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_pubgrade_tm_2026H2.md)
- Architecture → [ARCHITECTURE_RussianTranslation_pubgrade_tm_oral.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_pubgrade_tm_oral.md)
- Implementation → [IMPLEMENTATION_RussianTranslation_pubgrade_tm_oral.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pubgrade_tm_oral.md)
- Verification + risks → [VERIFICATION_RussianTranslation_pubgrade_tm_oral.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_pubgrade_tm_oral.md)

## Goal (one paragraph)

The Publication-Grade Sa→Ru TM already exists as a built asset (content-addressed exact/fragment TM,
layered **TMX 1.4b** exporter, L0 verse layer + L1 word-alignment over 1.09 M pairs, an A/B/C grader, an
independent-aligner cross-check, a JSON-Schema publication contract, and a 2,392-record release manifest).
**This span finishes it to an ACL-defensible, citable resource** by: replacing the proxy grade with real
reference-free QE (COMET-QE) calibrated on a frozen gold sample; promoting the independent aligner to a
calibrated confidence gate (awesome-align) and adding a learned mined-tier filter (Bicleaner-style);
building one embedding sentence-aligner (LaBSE/Vecalign) that serves both the anchorless written prose
(H308 Track A) and the new oral track; **formalizing the oral Sa→Ru corpus** from user-provided
transcripts (raw Russian with embedded Sanskrit + PDFs) as a first-class graded layer with a schema
extension in SamudraManthanam; populating the curated Sa→Ru terminology dataset with its own DOI path;
measuring whether the graded TM improves the translation engine when retrieved as fuzzy context; and
**preparing** (not auto-publishing) a full-text + derived-layer release that folds into the A42 data paper.
Publication itself stays a human GO/NO-GO gate.

## Decisions taken (from the `/ask` interview, 22-07-2026)

Every ruling below is locked; the execution agent trusts these without re-deriving. Settled H215 charter
decisions ([`TRANSLATION_MEMORY_DECISIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DECISIONS.md)
D1–D14) remain in force and are **not** re-opened here.

| # | Fork | Ruling | Rationale / consequence |
|---|---|---|---|
| R1.1 | Primary objective | **Technical hardening first** | Land COMET-QE + awesome-align + LaBSE so every unit is ACL-defensible before publication or oral scale-out. |
| R1.2 | Wave-1 sequencing | **All three forks as parallel tracks** | A (hardening) · B (oral) · C (release prep) run concurrently; the autonomy contract (below) makes parallel unattended execution safe. |
| R1.3 | Out of scope | **Fences applied** (user deferred) | OUT: OntoLex/TEI modelling (→ csl-standards), prose-ingestion internals (→ SamudraManthanam per H308). kNN-MT decoding stays OUT, but a **minimal** retrieval measurement is IN (R4.4). |
| R1.4 | Quality bar | **ACL-defensible grade + provenance** | Real COMET-QE (not proxy), frozen gold sample, reported Cohen's κ, Bender/Friedman data statement. |
| R2.1 | Oral sources | **All four** (own talks · Systema · third-party lectures · public video) | Mixed rights: own/Systema clean; third-party + public grey → gated by track C rights policy (R4.1). |
| R2.2 | Oral aligned unit | **All three granularities** | śloka→gloss (verse-anchored where cited), speaker-turn utterance, and term-level (feeds terminology, R3.4). |
| R2.3 | Transcription | **User provides transcripts — no ASR** | No Whisper/forced-alignment; the oral track ingests + aligns + grades provided transcripts. |
| R2.4 | Oral home | **Extend SamudraManthanam canonical schema + new oral converter** | Optional `time_start`/`time_end`/`speaker`/`media_ref` fields; one corpus, one query API; RussianTranslation consumes via `build_oral_l0`. |
| R3.2 | Paper strategy | **Fold TM into A42 as its resource contribution** | No new paper ID / no separate TM-paper DOI; TM ships as [A42](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)'s artifact. (Terminology keeps its **own** DOI per D13/R3.4.) |
| R3.3 | Transcript form | **Raw Russian with embedded Sanskrit + PDF** | Converter must detect/segment the Sanskrit and align it to surrounding Russian — reuses the PDF pipeline + the LaBSE aligner. |
| R3.4 | Terminology dataset | **Populate + give its own DOI this push** | The MW→RU-safe path (D9); term-level oral pairs feed it; mostly own/PD rights. Second citable resource. |
| R4.1 | Rights / release | **Clearance treated as in-hand → plan full-text publication, but hard human GO/NO-GO before go-live** | Agent PREPARES full-text + derived bundles; a human runs `/publish-safety-check` with per-source clearance evidence. **Nothing auto-publishes.** |
| R4.2 | Aligner scope | **Both written prose AND oral** | One LaBSE/Vecalign aligner serves H308 prose Track A and the oral transcripts. |
| R4.3 | Gold sample | **Extend the H136 gold (320-row stratified)** | Adjudicate an A/B/C grade label per segment via `/gold-adjudicate`, add oral + prose strata, freeze, report κ. |
| R4.4 | Engine retrieval | **Include a minimal retrieval measurement** | One experiment: does the graded TMX as fuzzy context improve draft quality/speed vs no-TM (Neural Fuzzy Repair framing)? Validates the H215 "feeds the engine" claim + strengthens A42. |
| R5.1 | On ambiguity | **Pick the marked default, log it, continue** | Never stall; record every default taken in the handoff decision log. |
| R5.2 | Commit authority | **Full: commit → PR → auto-merge (worktree, green CI)** | Per the standing handoff-scoped autonomy rule; release artifacts prepared but never published. |
| R5.3 | The fence | **Data-safety fences confirmed; publish fences retained** | See the autonomy contract. Publish/DOI/visibility/copyrighted-push fences are held as non-negotiable (consistent with R4.1 + copyright law), even though not re-checked in the multiselect. |
| R5.4 | Compute | **External API for embeddings + QE** | HuggingFace Inference API (LaBSE + COMET) primary; smoke-test spike before any bulk run. DeepSeek is chat-only (no embeddings). |

## Autonomy contract (verbatim — the execution agent obeys this)

**On unplanned ambiguity.** Apply the plan's marked default for that fork, record the choice in the
handoff decision log, and continue. Never halt to wait for a human on a foreseeable fork.

**Stop conditions (halt + report, do not press on).** Halt if: (a) CI goes red and the fix is outside
the plan's scope; (b) a calibration result falls below its stated floor — COMET-QE vs gold Spearman
ρ < 0.4, or oral/prose aligner precision@sample < 0.80 — meaning "ACL-defensible" can no longer be claimed
for that track (mark it preliminary, halt that track, continue the others); (c) a rights ambiguity on a
specific source that the R4.1 policy does not resolve; (d) any destructive-guard or worktree-isolation
hook trips.

**Commit authority.** Full commit → PR → auto-merge on green CI, per track, in an isolated worktree
(`<repo>-h<id>-<pid>`), across [`RussianTranslation`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation)
and [`SamudraManthanam`](https://github.com/gasyoun/SamudraManthanam). Delete the branch after merge; remove the worktree same pass.

**The fence — never do these unattended:**

1. **No publication.** Never make anything public, flip repo visibility, enable Pages, or mint/register a
   DOI. All release goes through a human `/publish-safety-check` with per-source clearance evidence. The
   agent only PREPARES release bundles (full-text where clearance is asserted, derived-layer everywhere).
2. **No copyrighted surface text to any public remote.** Grey / no-redistribution Russian text (and
   third-party lecture/video text) stays gitignored and local. The derived layer (Sanskrit, SLP1 keys,
   alignments, A/B/C grades, provenance) may be prepared, never the copyrighted words themselves, until
   clearance is proven per source.
3. **No direct commits to `csl-orig` or any guarded main-tree checkout.** Worktree-isolation flow only.
4. **Never destroy the non-rebuildable assets.** `corpus_lexicon.jsonl` (1.09 M rows) and SamudraManthanam
   `corpus.db` are read-only; never overwrite, delete, or regenerate-in-place.

> Fence items 1–2 are held as non-negotiable regardless of the Round-5 multiselect, because they are
> identical to the Round-4 ruling ("hard human GO/NO-GO before go-live; nothing auto-publishes") and
> because auto-publishing copyrighted third-party material cannot be delegated to an unattended agent.

## Prior-art verdict (build-vs-reuse, evidence-cited)

**Reuse, do not rebuild** (hub-confirmed, [SHARED_CODE §10](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md),
[PROJECT_INTERLINKS](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)): the TMX exporter
[`build_tmx.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py),
grader [`tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py),
aligner cross-check [`tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py),
L0 builder [`build_l0.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_l0.py),
content-addressed [`translation_memory.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py),
the word-alignment lexicon `corpus_lexicon.jsonl`, the schema
[`translation_memory.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/translation_memory.schema.json),
the SamudraManthanam PDF pipeline
[`PDF_INGESTION_PIPELINE.md`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/corpus_builder/PDF_INGESTION_PIPELINE.md),
and the corpus query API (`/api/morph`, `/api/search`, `/compare`).

**Build (the delta this span adds):** COMET-QE integration into the grader; awesome-align → calibrated
gate; Bicleaner-style learned mined-tier filter; the LaBSE/Vecalign sentence-aligner (prose + oral); the
oral schema extension + converter; the terminology-dataset population; the retrieval measurement; the
release-bundle preparation. All detailed in the ARCHITECTURE + IMPLEMENTATION layer docs.

## Governing prior docs (read before executing)

- [H215 handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md) — the owning handoff.
- [`ACL_TM_CROSSWALK_MEMO.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ACL_TM_CROSSWALK_MEMO.md) — 22 live-verified ACL methods, TM-H1…7 hypotheses, viz specs, backlog. This plan operationalizes it.
- [`TRANSLATION_MEMORY_DECISIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DECISIONS.md) — D1–D14 charter.
- [`src/BUILD_TMX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/BUILD_TMX.md) — TMX + grader + L0 build reference.
- [`SanskritLexicography/FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) §65 (alignment grounding) + §70 (grade distribution, proxy-QE is near-useless for adequacy).
- [A41 corpus descriptor](https://github.com/gasyoun/SamudraManthanam/blob/main/papers/A41_parallel_corpus_descriptor.md) + [НКРЯ export roadmap](https://github.com/gasyoun/SamudraManthanam/blob/main/docs/ROADMAP_NKRYA_PARALLEL_RUSCORPORA_2026_2027.md).

_Dr. Mārcis Gasūns_
