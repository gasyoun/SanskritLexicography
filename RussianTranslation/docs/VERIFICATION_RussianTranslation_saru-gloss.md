# VERIFICATION — Sa→Ru gloss layer

_Created: 19-07-2026 · Last updated: 19-07-2026_

Index: [PLAN_RussianTranslation_saru-gloss-quality_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_saru-gloss-quality_2026H2.md).

## Acceptance criteria + proof commands

### Wave 1
| Deliverable | Acceptance | Proof |
|---|---|---|
| W1.1 pseudo-root fix | Root layer no longer contains self-mapped `unresolved` lemmas; count drops from 2,021 by the excluded number | `pytest tests/test_saru_gloss_pipeline.py -k pseudo_root`; delta row in `RESULTS_LOG.md` |
| W1.2 homograph completeness | A 3-lemma fixture yields ≥2 alternates | `pytest -k homograph`; `wc -l ambiguity_homographs.tsv` before/after |
| W1.3 Vidyut trail | `vidyut_ambiguity.tsv` exists and is non-empty after a rollup→vidyut→rollup run | `pytest -k vidyut_ambiguity`; file present |
| W1.4 doc consolidation | One canonical doc; pipeline README is a runbook+pointer; `√gam` counts consistent across README/USE_CASES/SAMPLE; `.ai_state.md` at v1.1.0 | grep the three files for the `√gam` triple; link-check the pointer |
| W1.5 caveat | "Coverage ≠ accuracy" block present in canonical README + `index.html` | grep both files |
| W1.6 tests | All three fixtures green | `pytest tests/test_saru_gloss_pipeline.py` |

### Wave 2
- `gold/saru_gloss_precision_report.md` exists with a **per-tier × per-frequency** precision table
  and a separate lemmatization-vs-gloss breakdown.
- Provenance line states **model-vs-model, NOT gold** (org gold-provenance rule).
- A `@DO` human-spot-check row exists in [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
- Proof: open the report; confirm the strata cells sum to the sample n; confirm `gold_agreement.py`
  runs against the produced artifacts without a "no double-reviewed item" hard-fail.

### Wave 3
- Coverage delta table (forms/tokens recovered) committed.
- **Precision non-regression:** a sample of newly-resolved forms scored against the wave-2 rubric
  shows no drop vs the wave-2 tier precision. A recovered-but-wrong form counts as a regression.
- Proof: `compare_sandhi_methods.py` bench output for the `vidyut.cheda` path; the re-measured strata table.

### Wave 4
- A smoke test resolves a known dictionary headword through the TM lookup and returns candidate
  Russian renderings from the glossary.
- The [Uprava/PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)
  downstream row for the glossary is flipped from planned to wired with the PR link.
- Proof: `pytest -k tm_lookup_smoke`; the INTERLINKS diff.

## Risks & spikes register

| Risk | Likelihood | Impact | Mitigation / spike |
|---|---|---|---|
| Pseudo-root exclusion (W1.1) drops *legitimate* roots that happen to self-map | Med | Med | Spike: hand-inspect 20 excluded lemmas before finalizing; if any is a true root, tighten the exclusion to "no suffix match AND lemma carries a preverb". |
| The measured per-tier precision is embarrassingly low (e.g. marker tier < 60 %) | Med | Low (that IS the finding) | Report it honestly; it directly justifies wave 3's re-measurement discipline. Not a blocker. |
| `vidyut.cheda` splits differ from the corpus's own `+`/`-` marks, causing double-recovery | Med | Med | Prefer the corpus marker when present; use cheda only where no marker exists. Bench on the kosha comparison set first (spike). |
| Regen in the worktree (Step 7) is slow / OOMs on the 290 MB corpus held in RAM | Low | Med | The rollup does not re-read corpus_lexicon (only surface_glossary.jsonl); if surface regen is needed and OOMs, that is a stop-condition — leave a note, do not stream-refactor unattended. |
| Panel run (W2.3) hits API limits mid-run | Med | Med | The gold sampler and panel are resumable (append-only, per the existing gold machinery); on limit, park with progress logged. |
| Wave 4 TM wiring touches the live pwg_ru card pipeline mid-flight (safety-plan PRs #547/#550 open) | Med | High | Wave 4 adds a *read-only lookup consumer*; do not modify the coordinator/runtime that #547/#550 touch. If a collision surfaces, park wave 4 and note it. |

## Spikes to run BEFORE committing to the arch

1. **Excluded-pseudo-root inspection** (W1.1) — 20-sample hand check, ~15 min, before the exclusion is final.
2. **cheda-vs-corpus-marker agreement** (W3.2) — bench `vidyut.cheda` against the corpus's own marks
   on a sample, decide precedence, before wiring it into the rollup.

_Dr. Mārcis Gasūns_
