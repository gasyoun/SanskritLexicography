# Definition typology (WS2.4) — synonym / equivalent / encyclopedic

_Created: 24-07-2026 · Last updated: 24-07-2026_

**Handoff:** [H1483](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1483-Opus_SanskritLexicography_definition-typology-classifier-ws2-4_22.07.26.md) · **Executor:** Grok 4.5 (`grok-4.5`), Opus-lock override · **Scope:** first operational pass over the classical microstructural axis flagged absent in [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) Part I and [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) L1 / WS2.4.

## What this is

A **documented classification rubric** plus a **per-dictionary distribution** of definition types over **926,759** csl-orig `<L>` records in **15** dictionaries, with a **hand-adjudicated stratified sample** (n=79) for precision.

This is **not** yet the ATLAS_FAIR review-pool design (300 entries × 7 dicts, double-keyed). It is the machine-readable first cut that makes that pool designable: a shared label set, a reproducible script, and measured error modes.

## Rubric (operational)

Classical axis (Wiegand / Svensén / Landau microstructure): **synonym gloss** vs **translational equivalent** vs **encyclopedic description**. Operationalised for CDSL digital text after markup strip (`{#…#}`, `{%…%}`, `<lex>`, `<ls>`, …). Body text is taken after the classical `¦` pipe when present.

| Class | Code | Operational rule (priority order) |
|---|---|---|
| **residual** | `residual` | Empty body; POS-only crumb; pure headword equation (`= other_lemma`); see/s.u./q.v. cross-ref; citation-only; `Lbody=N` subentry pointer noise; bare sense number |
| **equivalent** | `equivalent` | Short translational / onomastic unit: name-formula (`N. of…` / `N. pr.…`), or ≤12–14 content tokens without relative-clause markers and without numbered multi-sense blocks |
| **synonym** | `synonym` | Definition by synonym list: 2+ short gloss items (comma/semicolon/slash), citations stripped; or short explicit paryāya / *iti medinī*-style Skt-Skt chain |
| **encyclopedic** | `encyclopedic` | Numbered multi-sense microstructure, relative/purpose clauses, long descriptive prose (≥15 tokens or ≥130 chars or ≥2 sentence periods), or quoted definitional passages |

**Boundary notes (committed judgment, not free parameters):**

1. **Name formulas are equivalents**, not encyclopedic — even with a short place/person complement (`N. pr. eines Flusses…`).
2. **Headword equations are residual** only when the *whole* body is an equation; multi-sense continuations after `=` are classified on the full body (usually encyclopedic).
3. **Trailing citation crumbs** (`L.`, `MBh.`, `TS. …`) do not count as synonym-list items.
4. **Numbered sense blocks** (`1〉`, `--2`, `— 1`) force encyclopedic regardless of local gloss shortness (the microstructure is multi-unit).
5. **SKD/VCP paryāya** is synonym only while the body stays short; long multi-sense Skt prose with a paryāya cue stays encyclopedic.

## Method

- **Input:** local [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02) `*.txt` (sibling of this repo). Never rebuilt; never committed.
- **Script:** [`definition_typology_classifier.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_classifier.py)
- **Outputs:**
  - [`definition_typology_per_dict.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_per_dict.tsv) — counts + % per class
  - [`definition_typology_sample.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_sample.tsv) — reservoir sample (seed 1483) for further review
  - [`definition_typology_gold.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_gold.tsv) — hand-adjudicated stratified subset
  - [`definition_typology_run_meta.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_run_meta.tsv) — seed, dict list, input SHA1-12 fingerprints

```text
python data/definition_typology_classifier.py --csl-orig ../csl-orig/v02
python data/definition_typology_classifier.py --verify data/definition_typology_gold.tsv
```

## Per-dictionary distribution (n = 926,759 records)

| dict | entries | synonym % | equivalent % | encyclopedic % | residual % |
|---|--:|--:|--:|--:|--:|
| **mw** | 286,525 | 47.5 | 20.0 | 25.2 | 7.2 |
| **pwg** | 123,366 | 8.2 | 7.1 | **81.5** | 3.2 |
| **pw** | 170,556 | 7.8 | 8.6 | 69.4 | 14.1 |
| **ap90** | 34,882 | 17.2 | 9.9 | 61.6 | 11.3 |
| **cae** | 40,069 | 37.5 | 4.2 | 55.6 | 2.7 |
| **wil** | 44,577 | 33.0 | 0.8 | 66.1 | 0.1 |
| **sch** | 29,125 | **74.5** | 1.9 | 16.1 | 7.5 |
| **md** | 20,749 | 58.9 | 3.2 | 37.9 | 0.0 |
| **ccs** | 30,010 | 35.7 | 12.8 | 48.7 | 2.8 |
| **gra** | 12,785 | 13.1 | 2.2 | 76.1 | 8.6 |
| **skd** | 42,531 | 27.5 | 0.0 | 71.7 | 0.8 |
| **vcp** | 50,135 | 0.8 | 8.1 | **87.6** | 3.6 |
| **bhs** | 17,839 | 15.3 | 22.0 | 55.0 | 7.7 |
| **bur** | 19,776 | 37.4 | 1.0 | 61.5 | 0.0 |
| **vei** | 3,834 | 0.2 | 0.3 | **94.4** | 5.1 |

### Reading the family fingerprint

1. **Petersburg (PWG, PW) and VCP/VEI lean encyclopedic** — long multi-sense microstructure and German/Skt descriptive prose dominate the label mass.
2. **Schmidt (SCH) and Macdonell (MD) lean synonym-list** — short comma-chains of glosses are the house style; SCH at 74.5% synonym is the extreme.
3. **MW is the most balanced core dictionary** among the large ones (~48/20/25/7), matching its mixed gloss + descriptive practice.
4. **SKD shows almost zero pure “equivalent”** under this bilingual-biased operationalisation — Skt-Skt definitions are synonym chains or encyclopedic *vyutpatti*/quoted definitions, not target-language one-word glosses. That is a **feature of the typology applied to monolingual kośa text**, not a bug in SKD.
5. **WIL’s near-zero equivalent share** is driven by Wilson’s `E.` etymology appendices riding on every body: after strip, many otherwise-short glosses exceed the flat-equivalent length gate and land as encyclopedic or synonym. A Wilson-specific pre-split on `E.` would raise equivalent %; left for a follow-on (see open items).

## Hand-verified sample precision

- **Sample:** n=79, stratified (up to 2 rows × 4 classes × 12 priority dicts) drawn from the reservoir sample (seed 1483).
- **Gold:** single-pass adjudication against the rubric above (same session as the classifier; **not** independent double-key).
- **Accuracy:** **49/79 = 62.0%**.

### Confusion (predicted → gold)

| | gold synonym | gold equivalent | gold encyclopedic | gold residual |
|---|--:|--:|--:|--:|
| **pred synonym** | 8 | 6 | 4 | 0 |
| **pred equivalent** | 1 | 14 | 4 | 0 |
| **pred encyclopedic** | 5 | 7 | 8 | 2 |
| **pred residual** | 0 | 0 | 1 | 19 |

### What the errors are

| Error mode | Count (approx.) | Implication |
|---|--:|---|
| synonym ↔ equivalent (short single vs multi-gloss) | ~11 | Classical boundary is soft; comma noise and citation stripping still leak |
| short ENC ↔ equivalent | ~11 | Length gates vs true paraphrastic content — the hard call for bilingual dicts |
| residual missing multi-sense after `=` | 1–2 | eqn-head residual too greedy on mixed bodies (partially fixed; residual still high-precision) |
| residual high precision | 19/20 OK | Cross-ref / Lbody / empty classes are reliable |

**Honest ceiling for this pass.** 62% on a *class-stratified hard sample* is not production-grade annotation. Residual and name-formula equivalent are usable now; synonym vs equivalent vs short-encyclopedic needs either (a) human double-key on a fixed 300×7 pool (ATLAS_FAIR round 2) or (b) a supervised model over that gold. The distribution table is still directionally informative for family fingerprints (SCH ≠ PWG is robust to the measured error rate).

## Open items (not this handoff)

1. **Wilson `E.` split** — peel etymology appendices before classifying the gloss.
2. **ATLAS_FAIR review pool** — 300 entries × 7 dicts, double-keyed, on this rubric (roadmap Part I item 6).
3. **Sense-level, not record-level** — numbered multi-sense bodies currently collapse to one encyclopedic label; a sense-splitter would raise synonym/equivalent recovery inside PWG/PW.
4. **Independent second annotator** — κ against this gold before any paper claim.

## Provenance

| Field | Value |
|---|---|
| Handoff | H1483 |
| Model | Grok 4.5 (`grok-4.5`), Opus-lock override |
| Date | 24-07-2026 |
| Records classified | 926,759 across 15 dicts |
| Gold precision | 49/79 = 62.0% (stratified hard sample) |
| Roadmaps updated | L1 Definition typology ○→◐; WS2.4 first-pass noted |

_Dr. Mārcis Gasūns_
