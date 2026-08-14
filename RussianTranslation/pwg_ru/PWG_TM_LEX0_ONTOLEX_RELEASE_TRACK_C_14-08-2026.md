# H2685 Track C receipt — lossless TMX / TEI Lex-0 / OntoLex + FAIR pack

_Created: 14-08-2026 · Last updated: 14-08-2026_

**Executor:** Grok 4.6 (`grok-4.6`)
**PR:** pending this pass
**Release tag:** `pwg-tm-canonical-v1.0.0`

## What shipped

- [`src/pwg_tm_export_core.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_export_core.py)
  — shared mapping + TMX/TEI/Turtle builders + loss ledger.
- [`src/build_tmx.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py)
  `build-canonical` (corpus Sa→Ru path unchanged; `validate` auto-detects
  `srclang=de`).
- [`src/export_pwg_tm_tei.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_pwg_tm_tei.py)
  + RNG/Schematron under `schemas/`.
- [`src/export_pwg_tm_ontolex.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_pwg_tm_ontolex.py)
  + [`schemas/pwg_tm_ontolex.shacl.ttl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_tm_ontolex.shacl.ttl).
- [`src/pwg_tm_export_loss.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_export_loss.py)
  `--all-formats`.
- [`src/pwg_tm_release.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_release.py)
  — immutable pack under
  [`release/pwg_tm/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm/README.md).

## Proof (14-08-2026)

| Check | Result |
|---|---|
| `pytest tests/test_pwg_tm_export.py` | 5/5 |
| `pytest tests/test_pwg_tm_canonical.py` | 8/8 (prior) |
| TMX validate | **2392** `<tu>`, `srclang=de` |
| TEI validate | **953** entry / **2392** sense; jing not installed; RNG+Schematron shipped |
| OntoLex SHACL | structural ok + **pyshacl=pass** |
| `pwg_tm_export_loss.py --all-formats` | **0** lost; 153,088 accounted checks |
| Publication records | **2392 / 2392** |
| Wave-1 in green files | **no** (coverage denominators only) |

Canonical JSONL SHA-256
`b9ad8e9ff99d561de72029e9af40664e9cf7bfabe1575faf7858d88b757bbe82`
matches H2683 `reconciliation.v1.json`.

## Wave-1 denominators (honest, not green)

5000/5000 keys; 753111/753111 fragments; 655332 promoted / 97779 quarantine;
independent n=400 serious error 2.5% (floor ≤1%). See H2684 receipt
[PWG_TM_GROK46_WAVE1_TRACK_B_14-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_GROK46_WAVE1_TRACK_B_14-08-2026.md).

## Publish-safety

**GO.** PWG PD + own machine translation of that PD source. No secrets, no
privacy, no restricted designation. Uncertainty recorded in
`rights.facts`. Large binaries are gitignored and ride only the named GitHub
Release (not Pages).

## DOI

Concept + version **pending**. Bytes are hash-frozen. A later release will
embed the DOI without rewriting these four files.

_Dr. Mārcis Gasūns_
