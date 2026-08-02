# ARCHITECTURE — RussianTranslation ask-batch residual

_Created: 02-08-2026 · Last updated: 02-08-2026_

## Component boundaries

| Unit | Owns | Does not own |
|---|---|---|
| W1-RV | Residual RV evidence-layer code/data under sibling RV ARCHITECTURE | AV; bulk re-export of VedaWeb |
| W1-TM | Residual TM/oral surfaces under sibling TM ARCHITECTURE | Live PWG store promote |
| W1-GL | Residual gloss index/quality under sibling gloss ARCHITECTURE | Full lemma rewrite |
| W1-GATE | Probe harness + policy write (metric + ceiling floor) | Store mutation; promote path |

## Build-vs-reuse (prior-art)

| Piece | Verdict | Cite |
|---|---|---|
| RV spine/typing | **Reuse** H1843/H1844 + RV PLAN | sibling RV docs |
| TM / oral | **Reuse** pubgrade PLAN | sibling TM docs |
| Gloss | **Reuse** saru-gloss PLAN | sibling gloss docs |
| Live-gate / headless CLI | **Reuse** `/pwg-live-gate`, `/pwg-bounded-run` | org skills; do not reimplement CLI |
| Ceiling policy | **Extend** existing timeout constants + FINDINGS row | surgical only |

## Interfaces

- Research units: commit artifacts under `RussianTranslation/` per sibling IMPLEMENTATION paths.
- W1-GATE: write a committed measurement table (path named in VERIFICATION) + optional FINDINGS/policy one-liner; exit code of the probe driver is the proof.

_Dr. Mārcis Gasūns_
