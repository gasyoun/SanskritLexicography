# DEFINITION_TYPOLOGY_WS2_4_2026.meta.md — metadoc for `DEFINITION_TYPOLOGY_WS2_4_2026.md`

_Created: 24-07-2026 · Last updated: 24-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[DEFINITION_TYPOLOGY_WS2_4_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md).

## Subject

- **Document:** [DEFINITION_TYPOLOGY_WS2_4_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md)
- **Purpose:** Operational report for WS2.4 / ATLAS_FAIR micro-gap "definition typology" (synonym / equivalent / encyclopedic / residual) over all 44 csl-orig dictionaries.
- **Audience:** Anyone asking "how do MW vs PWG vs SKD *define*?" or closing the L1 census row; paper authors needing the family fingerprint before the 300×7 double-key pool.
- **Format / contract:** Rubric → method → full 44-row distribution table → gold precision → open items. Numbers must match `definition_typology_per_dict.tsv` after a `--all` re-run.

## Provenance

- **Created:** 24-07-2026 (handoff H1483, Grok 4.5 `grok-4.5`, Opus-lock override).
- **PRs:** [SanskritLexicography #698](https://github.com/gasyoun/SanskritLexicography/pull/698) (15-dict first pass), [#699](https://github.com/gasyoun/SanskritLexicography/pull/699) (gold reconcile), [#700](https://github.com/gasyoun/SanskritLexicography/pull/700) (all 44 dicts + linear apparatus strip).
- **Sibling artifacts:**
  - [definition_typology_classifier.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_classifier.py)
  - [definition_typology_per_dict.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_per_dict.tsv)
  - [definition_typology_gold.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_gold.tsv)
  - FEATURES_INDEX **E49**

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | ATLAS 300×7 double-key gold | Paper-grade κ; current 55/79 is single-pass hard sample | open |
| 2 | Sense-level split inside multi-sense bodies | PWG/PW under-count synonym/equivalent | open |
| 3 | Genre flag for catalog/list dicts (ACC, PUI…) | 71% "equivalent" on ACC is title-locus, not definition | open |
| 4 | Independent second annotator | Same-session gold is not κ | open |

## Known limitations

- Apparatus strip peels citations before length features — moves large bilingual dicts toward equivalent-dominant vs the first 15-dict pass.
- Gold labels are agent-adjudicated, not independent double-key.
- csl-orig is local-only input; TSVs are the committed derived product.

## Revision history

| Date | Change |
|---|---|
| 24-07-2026 | Metadoc created with H1483 closeout / artifact-propagate pass (Grok 4.5 `grok-4.5`). |

_Dr. Mārcis Gasūns_
