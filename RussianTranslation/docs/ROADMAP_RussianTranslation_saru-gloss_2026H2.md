# ROADMAP — Sa→Ru gloss layer (2026 H2)

_Created: 19-07-2026 · Last updated: 19-07-2026_

Index: [PLAN_RussianTranslation_saru-gloss-quality_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_saru-gloss-quality_2026H2.md).
Four waves, strict dependency order (D2). Each states what unblocks it.

## Wave 1 — Defects + honesty (unblocks: everything; depends on: nothing)

Fix the three pipeline defects that corrupt the rollup, consolidate documentation, and make the
public dataset honest about accuracy. Must land before wave 2, because measuring a defective
rollup wastes the measurement.

Deliverables:
- **W1.1** — Pseudo-root fix. `build_dcs_maps.py` currently writes a prefixed verb lemma with no
  matching root-suffix as *its own root* (`ls\tls\tunresolved`), silently inflating the 2,021-root
  layer with pseudo-roots. Emit these to a separate `dcs_lemma2root_unresolved.tsv` and exclude
  them from the root layer; recount.
- **W1.2** — Homograph completeness. `build_rollup_glossaries.py` inspects only the *second*
  candidate (`cands[1]`); a form with ≥3 near-equal lemmas logs at most one alternate. Iterate all
  candidates past the primary and emit every qualifying alternate to `ambiguity_homographs.tsv`.
- **W1.3** — Vidyut ambiguity trail. `build_vidyut_fallback.py` counts ambiguous forms
  (`stats['ambiguous']`) but never writes them out — the Vidyut tier has no auditable trail
  comparable to the DCS side. Emit `vidyut_ambiguity.tsv`.
- **W1.4** — Doc consolidation (D11). Method/coverage/typology/accuracy becomes ONE canonical doc
  owned by `gasyoun/SanskritRussian`; `RussianTranslation/glossary/README.md` shrinks to a build
  runbook + a full-blob-URL pointer. Fix the `√gam` count discrepancy (README 195/176/140 vs
  USE_CASES 196/177/141) and the stale `.ai_state.md` (says v1.0.0, repo is v1.1.0).
- **W1.5** — Honesty caveat (D3). A prominent "coverage ≠ accuracy" block in the canonical README
  and `index.html`, citing the 84.4 % upstream pair precision as a ceiling on any rolled-up gloss.
- **W1.6** — Regression tests (D9). One known-bad fixture test per W1.1–W1.3.

Acceptance: tests green; a `RESULTS_LOG` delta table showing the root-count drop, the added
homograph alternates, and the new Vidyut-ambiguity row count.

## Wave 2 — Measure accuracy (unblocks: wave 3 baseline; depends on: wave 1)

Produce the first accuracy figure the layer has ever had.

Deliverables:
- **W2.1** — Stratified sampler (D5): tier (dcs/vidyut/marker) × frequency (high/mid/hapax) +
  a homograph stratum. Reuse `gold/gold_sample.py` machinery; seed fixed for reproducibility.
- **W2.2** — Two-part rubric (D6): each sampled entry judged on (a) form→lemma→root attribution
  correctness, (b) top-ranked Russian gloss acceptability — independently.
- **W2.3** — LLM panel run (D4, D12): panel + adversarial verification, per the existing
  `precision_report.md` shape. Output labelled **model-vs-model, NOT gold**.
- **W2.4** — Per-tier precision report committed under `gold/`, plugged into the existing protocol;
  a `@DO` row for the human spot-check slot.

Acceptance: `gold/saru_gloss_precision_report.md` exists with a per-tier × per-frequency precision
table and explicit model-vs-model provenance; `gold_agreement.py`-compatible artifacts present.

## Wave 3 — Coverage on the miss classes (unblocks: nothing downstream; depends on: wave 2)

Reduce the 78,842 unresolved forms, measured against the wave-2 baseline so the gain is a
*measured accuracy-preserving* gain, not just a coverage bump.

Deliverables:
- **W3.1** — Simplex recovery: sandhi-normalization retries on the 48,646 unrecognized simplexes
  (91,548 tokens) before declaring a miss.
- **W3.2** — Compound splitting via **`vidyut.cheda`** (D7, reuse — installed v0.4.0), evaluated
  against `kosha/scripts/compare_sandhi_methods.py`'s existing benchmark. Target the 20,823 long
  compounds (≥14 chars). Splitter output feeds the existing rightmost-element / joined-form retry.
- **W3.3** — Re-measure the affected strata against wave 2; a form recovered but wrong is a
  regression, not a win.

Acceptance: coverage delta table + a precision check on a sample of newly-resolved forms showing
no precision regression vs wave 2.

## Wave 4 — Downstream wiring (depends on: wave 1; independent of 2/3)

Turn the published dataset into a *used* one.

Deliverables:
- **W4.1** — pwg_ru/mw_ru translation-memory lookup (D10): expose the lemma/root glossaries as a
  lookup layer the dictionary-card translation path can query for candidate Russian renderings.
- **W4.2** — Register in [Uprava/PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)
  as a wired downstream (currently "mostly not yet wired").

Acceptance: a smoke test resolving a known dictionary headword through the TM lookup; the
INTERLINKS row flipped from planned to wired with the PR link.

## Non-goals (explicit)

- **Regenerating/republishing the `SanskritRussian` data** — D8 fences this to a later gated pass.
- **Re-running `corpus_lexicon.jsonl`** (the 290 MB DeepSeek alignment) — out of scope, costs money.
- **A second independent aligner** for the upstream — tracked in `CAPABILITY_OBSERVATORY.md`, not here.
- **Nominal (noun) roots** — Layer 3 stays verbal-only by design.
- **Any Tier-0 / revenue-repo integration** — wave 4 is pwg_ru inside RussianTranslation only.

_Dr. Mārcis Gasūns_
