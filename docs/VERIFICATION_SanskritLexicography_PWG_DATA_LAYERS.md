_Created: 19-07-2026 · Last updated: 19-07-2026_

# VERIFICATION — PWG data layers

Cover: [PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md). Implementation: [IMPLEMENTATION_SanskritLexicography_PWG_DATA_LAYERS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_DATA_LAYERS.md).

## Acceptance criteria per deliverable

| ID | Deliverable | Acceptance criterion | Proof command / flow |
|----|-------------|----------------------|----------------------|
| V1 | Anatomy reference | Every parse-rules tag appears in the crosswalk with its count; all 24 pedagogical elements mapped or marked pedagogical-only. | `python RussianTranslation/src/build_anatomy_crosswalk.py --check` exits 0; manual diff of the matrix against `pwg.json` tag list. |
| V2 | RelaxNG grammar | `passes + Σ buckets == 123366`; zero `unclassified`. | `python RussianTranslation/src/validate_pwg_markup.py --assert-total`; inspect `reports/pwg_markup_validation.json` totals block. |
| V3 | Portrait JSON Schema | 100% parse-or-bucket; validated by the existing `validate_portrait_schema.py`. | `python RussianTranslation/src/validate_pwg_portrait.py --assert-total`. |
| V4 | `〉` audit + quarantine | One contamination number with a CI; quarantine row count == audit contaminated-row total; **store byte-identical before/after**. | `sha256` of `pwg_ru_translated.jsonl` unchanged across the step; `python -c "…"` comparing the two counts. |
| V5 | LLM sanity check | An agreement rate is reported, OR a skip is logged in `.ai_state.md`. | Read `reports/pwg_glyph_sanity.json` or the Dev-Notes skip line. |
| V6 | Citation coverage | Recognition ≥85%, or a written ceiling explanation with the unresolved tail catalogued. | `python RussianTranslation/src/extend_ls_coverage.py --report` prints old→new %; `reports/pwg_ls_unresolved.tsv` exists. |
| V7 | Sense/xref/government layers | Row counts + resolved-fraction reported; zero fabricated xref targets (all unresolved carry `resolved:false`). | `grep -c 'resolved.*false'` sanity; count deltas logged. |
| V8 | OntoLex rollup | TTL parses under rdflib; node count grows by expected cardinality; a known headword returns the new properties. | `python -c "import rdflib; g=rdflib.Graph(); g.parse('release/fixture/pwg_de_lexicon.ttl'); print(len(g))"`; SPARQL spot query on `agni`. |
| V9 | Defect staging | N change files in `batch_pending/` == N manifest rows; **zero csl-orig writes; zero maintainer-repo PRs opened**. | `git -C csl-orig status` clean & untouched; `gh pr list` shows no new PR to csl-orig/csl-corrections; manifest count == file count. |
| V10 | Hub sync + release | FINDINGS/PROJECT_INTERLINKS/SHARED_CODE rows present; CHANGELOG entry; release cut; GTD `@DECIDE` rows added. | `git log` shows the hub commits; `gh release view` shows the new tag. |

## Global invariants (must hold at run end)

- **INV-1 — csl-orig untouched.** `git -C csl-orig status --porcelain` is empty; no commit authored to csl-orig by this run.
- **INV-2 — RU store immutable.** `pwg_ru_translated.jsonl` (+ `.enriched`, `.quarantine`) sha256 identical to run start.
- **INV-3 — no maintainer-repo merge.** No PR merged into csl-orig / csl-corrections / csl-devanagari by the agent.
- **INV-4 — no paused lane launched.** No nominal/promote/requeue generation run triggered; no collision with the H1209 canary.
- **INV-5 — no unclassified drops.** Both validation reports account for all 123,366 records.
- **INV-6 — no synthesised sources.** Every citation resolution traces to `pwgbib.txt`/Verzeichniss; no LLM-guessed source in the citation layer.

## Risks & spikes register

| ID | Risk | Likelihood | Mitigation / spike |
|----|------|-----------|--------------------|
| R1 | `〉` re-segmentation over-corrects | med | Diff against the verified first-2500 fix (`_audit_micro.py`) **before** the full run; the ≤50-card sanity check (V5) is the second signal. Spike: run Step 4 on the first 2500 first, confirm it reproduces FINDINGS §447's numbers, then release to full. |
| R2 | RNG flags valid-but-irregular records as failures | med | The `unexpected-but-attested` bucket absorbs these; a human reviews buckets before any change file ships (Wave 2 gate). No change file is auto-generated from that bucket. |
| R3 | Citation resolver plateaus < 85% | med | Accepted per D8; catalogue the tail. Not a run failure. |
| R4 | csl-atlas shared-tree contention | med | Worktree off `origin/main` + PR; never a direct push. If rejected, stage as a patch in SL and `@DECIDE`. |
| R5 | DeepSeek backend unavailable | high | V5 is skippable by design; the run does not depend on it. |
| R6 | Store join ambiguity in the `〉` audit | low | Mark `ambiguous`, never guess (INV-6 spirit). |
| S1 | **Spike before committing to RNG:** confirm RelaxNG can express the `〉`-terminated sense structure at all. | — | 1-hour spike on 100 records; if RNG can't express it cleanly, fall back to expressing sense structure in the JSON Schema only and RNG covers spans/tags — log the decision. |

_Dr. Mārcis Gasūns_
