# IMPLEMENTATION — PWG→RU research-ceiling residual

_Created: 19-08-2026 · Last updated: 19-08-2026_

Index: [PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md).

Every unit starts with `precheck_handoff.py` + claim and a session-unique worktree
(`../SanskritLexicography-h<id>-<pid>` off `origin/master`); this is a guarded main
tree.

## R5 — [H3172 (Opus 5) — Shared gold sets unblocking WSD and BLI](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3172-Opus_SanskritLexicography_pwgru-shared-gold-wsd-bli_19.08.26.md)

1. **Write the protocol before annotating.** Name the frozen annotator-2 model id,
   prompt, decoding parameters and date. Freeze them; an undocumented annotator-2
   is the one failure that cannot be repaired afterwards.
2. Define and **write down a sampling frame per set** — WSD ~200 tokens,
   COMET-QE A/B/C translation slice, BLI 300 Sa→Ru. Sample from real pipeline
   material, not convenience-picked easy cases.
3. MG pass 1 → frozen model pass 2 → κ → `/gold-adjudicate` on disagreements.
4. Publish each set **versioned and frozen**, with a data statement, and register in
   [PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md).

**Stop before:** running any evaluation against these sets.

## R1 — [H3168 (Sonnet 5) — Ceiling C2 phase 1: per-sense attestation window](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3168-Sonnet_SanskritLexicography_ceiling-c2p1-sense-attestation-window_19.08.26.md)

1. Resolve each sense's `<ls>` citation set to works via the existing `ls_resolver`.
   **Carry the unresolved residue forward** — it is C7's standing census.
2. Join to [`ls_source_map.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json)
   (`date`/`period`/`renou`, 45 works). Emit `earliest`, `latest`, `n_dated_works`,
   `n_undated_citations` per sense; layer on `pwg_sense_stratum.jsonl` (consume it,
   do not re-derive).
3. Label every window *"per Böhtlingk–Roth's citations"*. No absolute
   sense-emergence field, in the data or the docs.
4. Coverage table: windowed / undated-only / unresolvable. Hand-check 25 senses
   against the printed PWG entry. Register the asset.

**Stop before:** the curated per-work dating table (C2 phase 2, Wave 2).

## R2 — [H3169 (Opus 5) — Ceiling C4: KEWA index normalization and join](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3169-Opus_SanskritLexicography_ceiling-c4-kewa-normalize-join_19.08.26.md)

1. Normalize the OCRed index at
   `SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt`: heading segmentation,
   SLP1 via the canonical transcoder, and an OCR-noise class census.
2. Join dhātu-aware — the `bhavati`→`bhū` gotcha
   ([LEARNER_APPARATUS_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/LEARNER_APPARATUS_SPEC.md))
   means a surface join drops the verbal core. `match_basis` ∈ {`exact`,
   `finite-form→root`, `sandhi/diacritic-normalized`, `ambiguous-multi`,
   `unmatched`}.
3. Keep the two lanes separately labelled: *traditional* (Cologne extractors) and
   *modern IE* (KEWA).
4. Record the rights facts once: permission held, terms not yet transcribed (N2 is
   the human act). Proceed with derived use.
5. ≥50-row hand adjudication weighted to `finite-form→root` and `ambiguous-multi`.

**Stop before:** publishing any KEWA heading text; EWA is out of scope (document
the crosswalk shape only).

## R3 — [H3170 (Sonnet 5) — Ceiling C8: DharmaMitra probe plus outreach draft](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3170-Sonnet_SanskritLexicography_ceiling-c8-dharmamitra-probe-outreach_19.08.26.md)

1. `/license-gated-ingest` on [lexicon.dharmamitra.org](https://lexicon.dharmamitra.org):
   fetchable inventory + licence **quoted verbatim** with URL and retrieval date.
2. File the composition/redistribution `@DECIDE` (N4) in
   [GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
3. `/outreach-draft` to the Berkeley team; **park it**, add the human `@DO` (N3).
4. Etiquette: cache, throttle, identify. Unreachable → log to
   [SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)
   and stop.

**Stop before:** sending anything; composing any derived corpus.

## R4 — [H3171 (Sonnet 5) — Heritage phase 6: segmenter-as-service cross-validation](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3171-Sonnet_SanskritLexicography_heritage-phase6-segmenter-service_19.08.26.md)

1. Evaluation set = the RussianTranslation glossary **adjudication** data (already
   hand-ruled — that is what makes this validation rather than a diff).
2. Run the UoHyd-mirror Heritage segmenter and DharmaMitra GPU morphology over it.
3. Report agreement **against the adjudication** and engine-vs-engine, separately.
   Classify disagreements as
   [`heritage_forms_oracle.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle.md)
   did: engine surplus · convention · lemmatization policy · genuine error.
4. Register the witness; flip phase 6's status in
   [HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md).

**Stop before:** overwriting any canonical morphology; ruling either engine correct.

## Truth-pass edits (already applied by H3001, listed so nobody redoes them)

| File | Correction |
|---|---|
| [RussianTranslation/research/ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md) | Wave 0 marked complete (H335 closed 08-07-2026); Wave 1 items now carry their minted H### |
| [HERITAGE_INRIA_ROADMAP.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.meta.md) | Stale backlog claiming phase 3 queued after it executed 26-07-2026; phase 6 now names H3171 |
| [RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md) | Shared gold-set blocker surfaced at doc level instead of hiding in per-card flags |
| [RussianTranslation/REVIEW_AND_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md) | "Build (next step): `freq_route.py`" corrected — it is built |

## Fences (all units)

- Guarded main tree — worktree only.
- No `csl-orig` dictionary text. No canonical-store mutation. No paid PWG run.
- No outreach sent. No KEWA text or composed DharmaMitra corpus published.
- Every percentage carries its denominator.

_Dr. Mārcis Gasūns_
