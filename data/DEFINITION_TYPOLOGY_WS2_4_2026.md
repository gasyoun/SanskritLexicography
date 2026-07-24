# Definition typology (WS2.4) — synonym / equivalent / encyclopedic

_Created: 24-07-2026 · Last updated: 24-07-2026_

**Handoff:** [H1483](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1483-Opus_SanskritLexicography_definition-typology-classifier-ws2-4_22.07.26.md) · **Executor:** Grok 4.5 (`grok-4.5`), Opus-lock override · **Scope:** classical microstructural axis flagged absent in [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) Part I and [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) L1 / WS2.4.

## What this is

A **documented classification rubric** plus a **per-dictionary distribution** of definition types over **every csl-orig dictionary with a main `.txt`** (**44 dicts · 1,496,157** `<L>` records), with a **hand-adjudicated stratified sample** (n=79) for precision.

| Wave | Scope | Records |
|---|---|--:|
| H1483 first pass | 15 core (union-family + WIL) | 926,759 |
| **This table (current)** | **`--all` = 44 / 44 csl-orig dicts** | **1,496,157** |

This is **not** yet the ATLAS_FAIR review-pool design (300 entries × 7 dicts, double-keyed). It is the machine-readable first cut that makes that pool designable.

## Rubric (operational)

Classical axis (Wiegand / Svensén / Landau): **synonym gloss** vs **translational equivalent** vs **encyclopedic description**. Operationalised for CDSL text after markup strip; body after `¦` when present.

| Class | Code | Operational rule (priority) |
|---|---|---|
| **residual** | `residual` | Empty; POS-only; pure equation `= lemma`; see/s.u./q.v.; citation-only; `Lbody=N`; bare sense number |
| **equivalent** | `equivalent` | Short translational / onomastic unit (`N. of…` / `N. pr.…`, or short flat gloss after apparatus strip) |
| **synonym** | `synonym` | 2+ short gloss items (comma/semicolon/slash); or short paryāya / *iti medinī* chain |
| **encyclopedic** | `encyclopedic` | Numbered multi-sense blocks, relative/purpose clauses, long prose, quoted definitions |

**Apparatus strip (linear).** Trailing citations and SCH `part=` crumbs are removed before length/list features. The first-pass nested `+(…)+$` citation-tail regex catastrophic-backtracked on ACC-style chains (`Baudh. IO. 395. L. 758…`) and hung the all-dict run; replaced by a linear unit remover (`--all` now finishes in ~3 min).

## Method

```text
python data/definition_typology_classifier.py --all --csl-orig ../csl-orig/v02
python data/definition_typology_classifier.py --verify data/definition_typology_gold.tsv
```

- **Input:** local [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02) (sibling; never committed).
- **Script:** [`definition_typology_classifier.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_classifier.py) (`--all` discovers every `<code>/<code>.txt`).
- **Outputs:** `definition_typology_per_dict.tsv`, `definition_typology_sample.tsv`, `definition_typology_gold.tsv`, `definition_typology_run_meta.tsv`.

## Full distribution — all 44 dictionaries (n = 1,496,157)

Sorted by dictionary code. **Bold** = class share ≥ 70% for that dict.

| dict | entries | synonym % | equivalent % | encyclopedic % | residual % |
|---|--:|--:|--:|--:|--:|
| abch | 1,965 | 23.4 | **72.5** | 4.1 | 0.0 |
| acc | 49,833 | 8.0 | **71.4** | 8.2 | 12.4 |
| acph | 163 | 33.7 | 61.3 | 4.9 | 0.0 |
| acsj | 240 | 5.8 | **91.2** | 2.9 | 0.0 |
| ae | 11,359 | 19.6 | **70.4** | 3.9 | 6.1 |
| ap | 90,843 | 11.1 | **71.3** | 5.5 | 12.1 |
| ap90 | 34,882 | 2.2 | 39.7 | 46.6 | 11.5 |
| armh | 7,907 | 6.5 | **76.7** | 16.8 | 0.0 |
| ben | 17,310 | 30.3 | 53.6 | 13.2 | 3.0 |
| bhs | 17,839 | 26.9 | 55.9 | 9.8 | 7.4 |
| bop | 8,961 | 2.1 | **77.0** | 20.8 | 0.1 |
| bor | 24,609 | 9.9 | **86.7** | 3.4 | 0.0 |
| bur | 19,776 | 28.9 | 67.1 | 4.0 | 0.0 |
| cae | 40,069 | 0.6 | **95.9** | 0.8 | 2.7 |
| ccs | 30,010 | 6.1 | **90.4** | 0.8 | 2.8 |
| fri | 8,155 | 37.1 | 60.5 | 2.4 | 0.0 |
| gra | 12,785 | 33.6 | 30.7 | 26.7 | 9.0 |
| gst | 6,780 | 16.1 | **75.5** | 7.1 | 1.3 |
| ieg | 7,932 | 7.0 | 29.6 | 61.2 | 2.2 |
| inm | 12,647 | 1.1 | 45.8 | 24.4 | 28.7 |
| krm | 2,061 | 6.1 | 14.1 | **79.8** | 0.0 |
| lan | 4,944 | 17.5 | 63.9 | 16.1 | 2.5 |
| lrv | 53,441 | 4.4 | **70.6** | 7.7 | 17.2 |
| mci | 2,643 | 38.3 | 6.2 | 50.2 | 5.3 |
| md | 20,749 | 22.6 | **71.5** | 5.9 | 0.0 |
| mw | 286,525 | 2.1 | **89.6** | 0.6 | 7.7 |
| mw72 | 55,390 | 8.2 | **79.1** | 7.9 | 4.8 |
| mwe | 32,378 | 2.8 | **91.3** | 4.6 | 1.3 |
| nmmb | 506 | 21.9 | **76.7** | 1.4 | 0.0 |
| pe | 8,799 | 10.4 | 31.4 | 53.6 | 4.5 |
| pgn | 485 | 2.1 | 0.6 | **97.1** | 0.2 |
| pui | 17,512 | 0.0 | **70.7** | 28.3 | 0.9 |
| pw | 170,556 | 2.0 | 65.8 | 18.1 | 14.1 |
| pwg | 123,366 | 7.3 | 59.5 | 30.0 | 3.2 |
| pwkvn | 24,976 | 1.3 | 49.7 | 7.7 | 41.3 |
| sch | 29,125 | 7.5 | **80.9** | 3.7 | 8.0 |
| shs | 47,326 | 9.0 | **84.1** | 6.2 | 0.7 |
| skd | 42,531 | 1.5 | 41.8 | 56.0 | 0.8 |
| snp | 453 | 6.2 | 13.7 | **70.4** | 9.7 |
| stc | 24,574 | 27.6 | 68.9 | 2.9 | 0.6 |
| vcp | 50,135 | 2.4 | 48.9 | 45.2 | 3.5 |
| vei | 3,834 | 0.5 | 1.0 | **93.4** | 5.1 |
| wil | 44,577 | 12.5 | **86.4** | 0.3 | 0.7 |
| yat | 45,206 | 1.1 | **98.4** | 0.4 | 0.2 |

### Family fingerprints (all-dict view)

1. **Most large bilingual dictionaries land as equivalent-dominant** after citation strip (MW 89.6%, CAE 95.9%, WIL 86.4%, YAT 98.4%, SCH 80.9%). Short gloss + trailing `<ls>`/siglum is the house style once apparatus is peeled.
2. **Encyclopedic outliers:** VEI 93.4%, PGN 97.1%, KRM 79.8%, IEG 61.2%, AP90 46.6%, SKD 56.0%, VCP 45.2% — descriptive / multi-sense / specialized prose.
3. **Petersburg still denser than MW:** PWG 30% encyclopedic vs MW 0.6%; PW 18% encyclopedic — multi-sense microstructure survives apparatus strip.
4. **Synonym peaks (still modest at full scale):** MCI 38%, FRI 37%, GRA 34%, ABCH 33%, BEN 30% — short multi-gloss house styles.
5. **High residual:** PWKVN 41.3%, INM 28.7%, LRV 17.2%, PW 14.1% — equations, empty sense crumbs, catalog pointers.
6. **ACC (catalog, 49.8k)** is 71% equivalent — short work-title / locus bodies, not definitional prose; treat as a different macro-genre when interpreting typology.

## Hand-verified sample precision

- **Sample:** n=79 stratified gold ([`definition_typology_gold.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_gold.tsv)).
- **Accuracy after linear apparatus strip:** **55/79 = 69.6%** (residual 19/19; main confusion = equivalent ↔ synonym on short multi-gloss and equivalent → encyclopedic on borderline length).
- Gold is single-pass, not independent double-key. ATLAS 300×7 pool remains the precision path for paper claims.

## Open items

1. Sense-level split inside numbered multi-sense bodies (would raise synonym/equivalent recovery in PWG/PW).
2. Genre flag for catalog/list dictionaries (ACC, PUI, …) vs true lexica.
3. ATLAS_FAIR double-key pool (300 × 7).
4. Independent second annotator κ.

## Provenance

| Field | Value |
|---|---|
| Handoff | H1483 (+ all-dict extension same day) |
| Model | Grok 4.5 (`grok-4.5`), Opus-lock override |
| Date | 24-07-2026 |
| Records | **1,496,157** across **44** dicts (`--all`) |
| Gold precision | 55/79 = 69.6% |

_Dr. Mārcis Gasūns_
