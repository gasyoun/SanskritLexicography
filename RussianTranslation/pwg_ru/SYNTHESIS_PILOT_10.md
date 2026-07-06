# Synthesis pilot — synthesize-first vs after-translation remix (10 words)

_Created: 06-07-2026 · Last updated: 06-07-2026_

**Deliverable 3 (comparison pilot) of
[H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md).**
Before committing the whole corpus to after-translation remixing
([`REGLUE_SPEC.md`](REGLUE_SPEC.md)), MG asked for a **bake-off**: for 10 maximally
diverse headwords, produce two outputs and compare.

- **Arm A — after-translation remix** (canonical): interleave the *already-translated*
  sub-cards per [`REGLUE_SPEC.md`](REGLUE_SPEC.md). Zero new translation.
- **Arm B — synthesize-German-first**: for each headword, **synthesize ONE coherent
  German entry from all its layers, THEN translate that single entry to Russian.** This
  *loses* free re-glue (a new translation per headword) and can drift from the source —
  the pilot measures whether the coherence gain is ever worth that cost.

This pilot answers "how good or bad synthesize-first is" *before* the whole mix — it does
**not** change the canonical ruling (Arm A stays canonical unless Arm B decisively wins).

## The 10 words (measured 06-07-2026 — span the full 1→5 layer range)

The translated corpus is verb-root-first (per H179/H201), so all ten are roots; they are
chosen to be as different as possible in **layer count, sub-card volume, and special-case
coverage**:

| # | key1 | layers | sub-cards | why chosen |
|---|---|---|---:|---|
| 1 | `dah` | 1 (pwg) | 63 | PWG-only baseline — Arm A ≡ Arm B should be ~identical (control) |
| 2 | `As` | 2 (pwg,pw) | 90 | minimal abridging layer |
| 3 | `car` | 2 (pwg,pw) | 257 | larger 2-layer; PW abridgement stress |
| 4 | `siD` | 3 (pwg,pw,pwkvn) | 187 | Nachträge layer present |
| 5 | `viS` | 3 (pwg,pw,pwkvn) | 537 | high-volume 3-layer (handoff-named) |
| 6 | `Ap` | 4 (pwg,pw,sch,pwkvn) | 152 | SCH `*`-sense + PWKVN caus (real special cases) |
| 7 | `DA` | 4 (pwg,pw,pwkvn,sch) | 803 | volume stress — coherence under load |
| 8 | `Cid` | 5 | 154 | NWS **English** foreign-fragment (`needs_ru_from_en`) |
| 9 | `gA` | 5 | 319 | all five layers, high volume |
| 10 | `Sam` | 5 | 172 | all five layers, second 5-layer point |

## Metrics (per word, both arms)

| axis | how scored |
|---|---|
| **fidelity** | does every source sense/citation survive? (count vs the layered store) |
| **coherence** | reads as one entry vs a pile-up (1–5 human) |
| **redundancy** | duplicated glosses across layers (lower better) |
| **fluency** | Russian readability (1–5 human) |
| **provenance-loss** | can each sense still be traced to its layer? (Arm B risk) |
| **hallucination risk** | any sense/citation not in any source? (Arm B risk; must be 0) |
| **cost** | Arm A = 0 new translations; Arm B = 1 synth + 1 translate per word |

Fidelity, redundancy, provenance-loss, hallucination are **machine-checkable** against
the layered store; coherence + fluency need a small human pass (interactive HTML sheet —
[[feedback_interactive_review_not_checkboxes]]).

## Procedure

1. Arm A: run `src/build_reglue.py` (per [`REGLUE_SPEC.md`](REGLUE_SPEC.md)) on the 10.
2. Arm B: `src/synth_de_first.py` — assemble all layers' German (`de`) for a headword →
   one LLM synthesis prompt → one translation prompt. **Isolated, pilot-only script; not
   wired into the production pipeline.** Report tier + exact model version at both steps.
3. Score both on the six axes + cost; write the side-by-side table here.
4. **Recommendation:** does synthesize-first ever beat after-translation-remix by enough
   to justify losing free re-glue and accepting hallucination risk? Default expectation
   (to be tested): Arm B may win *coherence/fluency* on the 5-layer monsters (`gA`, `Sam`,
   `Cid`) but loses *provenance* and *cost* everywhere; the PWG-only control (`dah`)
   should tie. State the verdict per layer-count band, not just overall.

## Result table (Arm-B run 06-07-2026, Opus 4.8 `claude-opus-4-8` synthesis)

**Arm A (after-translation re-glue) is the uniform baseline** — lossless by
construction (citations copied verbatim from the store): **fidelity 1.000 ·
hallucination 0 · provenance-loss 0 (every sense stays layer-tagged in the
structured store) · cost 0** for all 10 words. Its redundancy is the raw
cross-layer pile-up (supplements stacked, not merged) — the thing Arm B is meant
to reduce.

**Arm B (synthesize-German-first)** — 10 merged German entries synthesized by
Opus 4.8, scored against the layered store by
[`src/synth_score.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_score.py)
([`ARMB_SCORES.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/reglue/synth_outputs/) — gitignored, embeds `de`). `method`: **P** = programmatic
assembly (fragments reordered + concatenated verbatim), **F** = free-hand prose
synthesis.

| key1 | layers | method | fidelity | halluc | redund | prov-loss | cost |
|---|---|---|---:|---:|---:|---|---|
| dah | 1 | F | 0.997 | 0 | 9 | inline-only | 1 synth |
| As | 2 | F | 0.996 | 0 | 12 | inline-only | 1 synth |
| car | 2 | P | 1.000 | 0 | 25 | inline-only | 1 synth |
| siD | 3 | F | 0.997 | 1 | 41 | inline-only | 1 synth |
| viS | 3 | P | 1.000 | 0 | 72 | inline-only | 1 synth |
| Ap | 4 | F | 0.977 | 0 | 22 | inline-only | 1 synth |
| DA | 4 | P | 1.000 | 1 | 191 | inline-only | 1 synth |
| Cid | 5 | F | 0.990 | 1 | 17 | inline-only | 1 synth |
| gA | 5 | **F** | 0.989 | **46** | 63 | inline-only | 1 synth |
| Sam | 5 | F | 1.000 | 0 | 21 | inline-only | 1 synth |

*(coherence + fluency = the two human axes — deferred to the 4th HTML voting
sheet, which needs the Sonnet-5 Russian translation of each synth; the
citation-level machine axes above are language-independent and complete now.)*

### Findings (per the layer-count bands)

- **Control (`dah`, 1-layer): A ≈ B as predicted** — fidelity 0.997, hallucination
  0. With no supplement layers there is nothing to merge, so synthesize-first buys
  nothing.
- **2–4 layers: Arm B is faithful when assembled carefully** — fidelity ≥ 0.977,
  hallucination ≤ 1. The ≤1.3% fidelity dips (`Ap` 0.977, `As`/`siD`/`dah` ~0.996)
  are almost entirely **citation-form drift** (`ṚV` vs `ṚV.`, spacing, continuation
  `<ls n=…>` expansion), not dropped sources — exact `<ls>`-body matching penalizes
  reformatting.
- **The hallucination risk is REAL and fires exactly where predicted — 5-layer,
  high-volume, free-hand (`gA`):** 46 citations in the output not matching any
  source `<ls>` (net **+39** distinct citations vs source). Some are `ṚV`/`ṚV.`
  reformatting, but the volume is an order of magnitude above every other word — the
  free-hand synthesis of a large 5-layer entry **drifted**. `Sam` and `Cid` (also
  5-layer) stayed clean (0–1) — the difference is `gA`'s size × free-hand method.
- **Programmatic assembly (`car`/`viS`/`DA`) is exact** (fidelity 1.000,
  hallucination ≤1) — but programmatic assembly is *not* real synthesis; it is Arm
  A wearing Arm B's clothes (verbatim reorder, no coherent re-prose). It only proves
  that when Arm B is forced to preserve, it can — at the cost of the coherence gain
  that was its entire reason to exist.
- **Provenance is `inline-only` in every Arm-B output** — the agents did mark
  supplements inline (`[PW]`, `[SCH]`, `‹en›`), but that is prose-embedded, not the
  structured per-sub-card layer tag Arm A keeps. Machine-tracing a sense back to its
  layer is **lost** in Arm B; Arm A keeps it for free.

### Recommendation

**Arm A (after-translation re-glue) remains canonical — synthesize-first does not
decisively win.** Arm B's *only* uncontested advantage is potential
coherence/fluency on the 5-layer monsters, and that is precisely the axis still
unmeasured (human sheet pending). Against it, Arm B costs a fresh generation per
word (vs 0), forfeits structured provenance, and — on the one large free-hand case
(`gA`) — introduced real citation drift that Arm A structurally cannot. The bake-off
verdict per band: **1-layer tie · 2–4-layer Arm A on cost+provenance with Arm B
fidelity-acceptable · 5-layer Arm A unless the human coherence pass shows a decisive
Arm-B readability win big enough to justify the drift + cost.** Do not switch the
corpus to synthesize-first; keep the free re-glue and revisit only if the deferred
coherence sheet overturns this.

## Status (06-07-2026) — both arms scored on the machine axes

- **Arm A (after-translation remix)** is built for all 10 words as part of the
  [reglue pilot](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md#5a-pilot-run-results-06-07-2026-arm-a--zero-re-translation-proven)
  (`dah…Sam` ⊂ the 15-headword set) — zero re-translation, lossless.
- **Arm B (synthesize-German-first) — RUN 06-07-2026.** Inputs were assembled by
  [`src/synth_de_first.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_de_first.py);
  the **synthesis step** then ran as 10 isolated **Opus 4.8 (`claude-opus-4-8`)**
  sub-agents (one merged German entry per word → `pwg_ru/reglue/synth_outputs/*.de_synth.txt`,
  gitignored — embeds `de`). Both arms scored on the citation-level machine axes by
  [`src/synth_score.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_score.py)
  → results table above. **Run note (finding worth keeping):** free-hand synthesis of
  the largest entries repeatedly stalled mid-stream; the three biggest (`car`, `viS`,
  `DA`) only completed reliably via **programmatic assembly** (verbatim fragment
  reorder), which trades away the coherent re-prose that is Arm B's whole point — a
  practical strike against synthesize-first at scale.
- **Still deferred:** the **Sonnet-5 (`claude-sonnet-5`) Russian translation** of each
  synth + the **human coherence/fluency HTML sheet** (the 4th H180 sheet) — the two
  axes the machine run cannot score. Only that sheet can overturn the recommendation.
- **Measured layer coverage** (from the assembler) refines this doc's approximate table:
  `As`=pwg+pwkvn, `car`=pwg+pw, `siD`=pwg+pw+**nws**, `viS`=pwg+pw+pwkvn,
  `Cid`/`gA`/`Sam`=all five. The manifest is
  [`synth_inputs/MANIFEST.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/reglue/synth_inputs/MANIFEST.tsv).

## Guardrails

- Arm B is a **calibration probe only** — running it does not commit the corpus to
  synthesize-first, and it must not touch the production translate pipeline or the
  canonical layered store.
- Never blocks the H179 run.
- Report model tier + exact version for every Arm-B generation
  ([[feedback_state_model_tier]]).

_Dr. Mārcis Gasūns_
