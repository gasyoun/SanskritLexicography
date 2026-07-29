# rv_wordlevel_align.py run log (H1844 step 10, layer B)

_Created: 29-07-2026 · Last updated: 29-07-2026_

Aligner: the committed `tm_align.embed_aligner_factory` (SimAlign-style contextual subword alignment), model `bert-base-multilingual-cased`, hidden layer 8. No new aligner was written (ARCHITECTURE §4, W1.9).

| Quantity | Value |
|---|--:|
| Stanzas aligned | 150 |
| Sampling | stratified by maṇḍala, proportional, seed 1844 |
| Translator-stanza pairs skipped (not `present`) | 0 |
| Candidate token→span alignments | 9400 |
| Emitted (confidence ≥ 0.20) | 9400 |
| Dropped below the gate | 0 |
| Mutual-argmax confirmed, of emitted | 2835 (30.2%) |
| Wall clock | 454.5 s (3.03 s/stanza) |

## Observed confidence distribution (pre-gate)

Recorded per the step-10 marked default: keep the 0.20 gate for the first pass, record what the distribution actually looks like, and re-calibrate only against the step-11 gold as a separate evidence-backed step.

| Bucket | All | de | ru | en |
|---|--:|--:|--:|--:|
| [0,0.1) | 0 | 0 | 0 | 0 |
| [0.1,0.2) | 0 | 0 | 0 | 0 |
| [0.2,0.3) | 5 | 0 | 0 | 5 |
| [0.3,0.4) | 6 | 0 | 0 | 6 |
| [0.4,0.5) | 465 | 239 | 104 | 122 |
| [0.5,0.6) | 6016 | 2860 | 1665 | 1491 |
| [0.6,0.7) | 2639 | 1413 | 544 | 682 |
| [0.7,0.8) | 243 | 166 | 37 | 40 |
| [0.8,0.9) | 26 | 22 | 0 | 4 |
| [0.9,1.0] | 0 | 0 | 0 | 0 |

_Dr. Mārcis Gasūns_
