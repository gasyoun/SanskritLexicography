# IMPLEMENTATION — Sa→Ru gloss layer (wave-1 build sequence)

_Created: 19-07-2026 · Last updated: 19-07-2026_

Index: [PLAN_RussianTranslation_saru-gloss-quality_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_saru-gloss-quality_2026H2.md).
File-level, step-ordered. Each step names the files it touches and its dependency. All pipeline
work happens in a **worktree off `origin/master`**, never the shared checkout.

## Preconditions (stop-condition check — halt with a note if any absent)

- `../../../VisualDCS/src/DCS-data-2026/dcs_full.sqlite` present.
- `vidyut` importable, kosha data at `../../../kosha/data/vidyut/kosha`.
- `src/corpus_lexicon.jsonl` present (290 MB) — needed only if a regen is attempted (it is not in wave 1).
- `import vidyut.cheda` succeeds (wave 3).

## Wave 1 — ordered steps

### Step 1 — W1.1 pseudo-root fix · `src/build_dcs_maps.py`
Depends on: nothing.
- At the root-extraction loop (the `for r in roots_by_len` block, ~line 102–111), the `else` branch
  writes `f'{ls}\t{ls}\tunresolved\n'`. Redirect these rows to a new `dcs_lemma2root_unresolved.tsv`
  instead of the main `dcs_lemma2root.tsv`.
- In `build_rollup_glossaries.py`, when building the root layer, exclude lemmas whose only root is a
  self-mapped `unresolved` row from the 2,021 root count (they remain in the lemma layer).
- Emit a count of excluded pseudo-roots to stderr for the delta table.

### Step 2 — W1.2 homograph completeness · `src/build_rollup_glossaries.py`
Depends on: nothing (independent of Step 1).
- At the homograph block (~line 211–215, `if u2 != upos or c2 >= 0.5 * lcnt:`), replace the single
  `cands[1]` inspection with a loop over `cands[1:]`, emitting every candidate that meets the
  "different upos OR count ≥ 50 % of primary" test to `ambiguity_homographs.tsv`.
- Keep the primary attribution unchanged (no double-counting); only the alternates trail grows.

### Step 3 — W1.3 Vidyut ambiguity trail · `src/build_vidyut_fallback.py`
Depends on: nothing.
- Where `stats['ambiguous']` is incremented (~line 79–80), also append the form + its competing
  `(lemma, pos, cnt)` candidates to a new `vidyut_ambiguity.tsv` (mirror the DCS
  `ambiguity_homographs.tsv` schema).

### Step 4 — W1.6 regression tests · `tests/test_saru_gloss_pipeline.py` (new)
Depends on: Steps 1–3.
- Fixture A: a prefixed verb lemma with no root suffix → assert it lands in
  `dcs_lemma2root_unresolved.tsv`, not the root layer.
- Fixture B: a form with three near-equal lemmas → assert ≥2 alternates in `ambiguity_homographs.tsv`.
- Fixture C: an ambiguous Vidyut form → assert a row in `vidyut_ambiguity.tsv`.
- Use the existing committed `src/fixtures/corpus_lexicon.fixture.jsonl` as the seed where possible.

### Step 5 — W1.4 doc consolidation
Depends on: nothing (parallel with 1–4).
- In `gasyoun/SanskritRussian` (a separate clone/worktree — docs only, data FENCED): make
  `README.md` the canonical method/coverage/typology/accuracy doc. Fix the `√gam` counts to one
  consistent set (regenerate the showcase numbers from current data if present, else pick the
  README set and correct USE_CASES/SAMPLE to match). Refresh its `.ai_state.md` to v1.1.0 truth.
- In this repo: shrink `glossary/README.md` to a build runbook (the two-pass bootstrap + script
  list) + a full-blob-URL pointer to the canonical doc.
- Give the canonical doc a sibling `.meta.md`.

### Step 6 — W1.5 honesty caveat
Depends on: Step 5.
- Add a prominent "**Coverage ≠ accuracy**" block near the top of the canonical README and in
  `index.html`: state that 87.1 % is a *resolution* rate; the *accuracy* ceiling is the 84.4 %
  upstream pair precision, compounded by an as-yet-unvalidated lemmatization join; a measured
  per-tier figure is coming in wave 2.

### Step 7 — delta table + commit
- Run the two-pass bootstrap locally (rollup → vidyut → rollup) to regenerate the *tsv/jsonl in the
  worktree ONLY* (gitignored — not published; this proves the fixes, it does not touch SanskritRussian).
- Write the before/after counts to `RESULTS_LOG.md` (root count, homograph alternates, Vidyut-ambiguity rows).
- Commit in the worktree; open a PR to `master`; auto-merge.

## Waves 2–4 (sketch — full step lists authored at each wave's start)

- **Wave 2:** `gold/saru_gloss_sample.py` (stratified sampler reusing `gold_sample.py`) →
  `gold/saru_gloss_panel.py` (panel + adversarial verify, two-part rubric) →
  `gold/saru_gloss_precision_report.md`.
- **Wave 3:** `src/build_compound_split.py` wrapping `vidyut.cheda`, benched against
  `kosha/scripts/compare_sandhi_methods.py`; hook its output into the rollup's marker/rightmost retry;
  re-measure affected strata.
- **Wave 4:** a `tm_lookup` module exposing lemma/root glossaries to the pwg_ru/mw_ru card path;
  smoke test on a known headword; INTERLINKS row flip.

_Dr. Mārcis Gasūns_
