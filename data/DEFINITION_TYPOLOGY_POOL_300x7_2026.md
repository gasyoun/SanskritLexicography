# Definition typology pool — stratified 300 × 7 double-keyed sample (round 2)

_Created: 24-09-2026 · Last updated: 24-09-2026_

**Handoff:** [H5330](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5330-OxAlpha_SanskritLexicography_definition-typology-300x7-double-key-sheets_23.09.26.md) · **Executor:** OxAlpha (`opencode/z-ai/glm-5.3-flash`) · **Epic:** [E014](https://github.com/gasyoun/Uprava/blob/main/handoffs/epics/E014-SanskritLexicography_atlas-fairpubs-wave-1_23.09.26.md)

## What this is

The reproducible sampling frame for definition-typology round 2 (roadmap item 6 of [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)): **2,100 rows = 300 entries × 7 dictionaries**, stratified by the [H1483 classifier](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_classifier.py)'s predicted WS2.4 class, rendered as **double-keyed review sheets** (two independent annotator keys per row). **No annotation happened** — per the handoff, this pass only samples and renders.

## Artifacts

| Artifact | What it is | Committed |
|---|---|---|
| [definition_typology_pool_sampler.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_pool_sampler.py) | Seeded stratified draw (`--selftest` = offline positive/negative controls) | yes |
| [definition_typology_pool_300x7_manifest.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_pool_300x7_manifest.tsv) | 2,100 rows: dict, l_id, k1, predicted, sample_seq — **ids only, no definition text** | yes |
| [definition_typology_pool_300x7_strata.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_pool_300x7_strata.tsv) | Per dict × class: class_total, allocated | yes |
| [definition_typology_pool_300x7_meta.json](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_pool_300x7_meta.json) | seed 5330, dicts, allocator rule, input sha1_12 fingerprints | yes |
| [build_typology_pool_sheets.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/build_typology_pool_sheets.py) | Renders the 14 double-keyed sheets + `--dry-run` decisions validator | yes |
| `data/typology_pool_300x7_sheets/` | Rendered HTML (14 packsets, 30 packs each) + dry-run `*_decisions.json` | **no** — gitignored |

## Reproduce

```bash
python3 data/definition_typology_pool_sampler.py --csl-orig ../csl-orig/v02 --seed 5330
python3 data/build_typology_pool_sheets.py --csl-orig ../csl-orig/v02 --dry-run \
    # under a venv with csl_pyutil (sheet-smoke)
```

Same csl-orig checkout + seed 5330 ⇒ byte-identical manifest (re-run diff-verified in the delivery PR). The rendered sheets live only locally: cards carry csl-orig-derived definition text, and the never-commit-csl-orig guard keeps bulk dictionary bodies out of git — the committed manifest carries ids only, and the sheets regenerate from manifest + seed.

## Strata design

- **Dictionary × predicted class** (WS2.4 rubric: synonym / equivalent / encyclopedic / residual), predicted by the H1483 classifier reused verbatim (imported, never re-derived).
- **Allocation:** proportional to the per-dict predicted class distribution, **min quota 10 per class** (every class with ≥10 entries in a dict gets ≥10 so agreement per class is estimable), largest-remainder rounding, exact 300 per dict. Allocator refusals are fail-closed (`ValueError`) and selftested.
- **Seed:** 5330, single `random.Random(5330)`; dicts in fixed sorted order; rows sorted (dict, class, l_id).

### The seven dictionaries

No canonical estate "7 dicts" list exists, so the set is fixed in the sampler (module docstring), spanning all four rubric classes with the estate's core comparative set: **mw** (anchor, 89.6% equivalent) · **pw** (heaviest residual, 14.1%) · **pwg** (30.0% encyclopedic, P4 subject) · **ap90** (Apte student encyclopedic, 46.6%) · **vcp** (45.2%) · **skd** (indigenous kosa, 56.0%) · **ben** (synonym-heavy, 30.3%). Swapping one is a one-line change in `SEVEN_DICTS` + a re-run.

### Double-key design

Per dictionary, **two sheet variants of the same 300 rows**: `-a` (manifest order) and `-b` (same rows reshuffled, variant seed) with distinct `sheet_id`s (`h5330typ-<dict>-a` / `-b`) so the two annotators' localStorage records never collide and each exports an independent `*_decisions.json`. Cards are **prediction-blind** (the machine's class is never shown — anchoring is why round 1's gold stayed single-pass); the 4-class force-choice rides the standard rating row (1 synonym · 2 equivalent · 3 encyclopedic · 4 residual), approve/reject carries card usability.

## Checks (this pass)

- `python3 data/definition_typology_pool_sampler.py --selftest` → **PASS** (determinism, exact 300/dict, min-quota floors genuinely bound, allocator refuses undersized input)
- re-draw diff vs first run → **byte-identical** (seed canary)
- `build_typology_pool_sheets.py --dry-run` → **PASS**: 14 sheets × 300 cards parsed back out of the rendered HTML, 14 decisions files, A/B id sets identical per dict
- 2 PreflightWarnings per sheet (V9 evidence-manifest, V13 identity-gate) are the documented csl-pyutil migration ramp (errors only in 1.0.0) — acceptable for this pass, named here so the verifier sees they were seen

## Risks

- The classifier's citation-strip eats bare Latin words (sigla-shaped, re.I), which is the **published H1483 behavior of record** (it is why MW reads 89.6% equivalent) — strata follow that behavior; a future classifier recalibration re-baselines the strata, not this sample's ids.
- Rounds-of-annotation economics: 300 cards/dict is 30 packs per key; a full two-key pass is 4,200 card-decisions per dictionary pair — recruitment (H5311) should budget per-key, not per-row.

_Гасунс_
