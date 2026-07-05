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

## Result table (to fill after runs)

| key1 | arm | fidelity | coherence | redundancy | fluency | prov-loss | halluc | cost |
|---|---|---|---|---|---|---|---|---|
| dah | A | | | | | | | 0 |
| dah | B | | | | | | | 1+1 |
| … | | | | | | | | |

## Guardrails

- Arm B is a **calibration probe only** — running it does not commit the corpus to
  synthesize-first, and it must not touch the production translate pipeline or the
  canonical layered store.
- Never blocks the H179 run.
- Report model tier + exact version for every Arm-B generation
  ([[feedback_state_model_tier]]).

_Dr. Mārcis Gasūns_
