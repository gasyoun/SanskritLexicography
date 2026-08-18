# H2856 — spot-check of "corpus-absent" headwords

_Created: 18-08-2026 · Last updated: 18-08-2026_

Computed by Sonnet 5 (`claude-sonnet-5`). Driver: [`src/h2856_spot_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h2856_spot_check.py). Deterministic sample (every 4000th row of the 82487 exact-match-absent headwords in `research/h2856_ghost_headword_census.jsonl`), not random.

For each sampled headword: (1) does its `key1` occur as a **prefix** of some `corpus_lexicon.jsonl` `slp1` token (an inflected-form hint), and (2) does the independently-computed `renou_any_dcs` flag (from a different DCS-level pass) say it IS corpus-attested. "Confirmed absent" requires both checks negative.

| key1 | renou_any_dcs | prefix hits in corpus_lexicon.jsonl | verdict |
|---|---|---|---|
| `afRin` | False | — | confirmed absent |
| `aBivyApin` | False | — | confirmed absent |
| `Aryaduhitar` | False | — | confirmed absent |
| `ojasya` | True | — | likely false negative (exact-match too strict) |
| `kunAdIkA` | False | — | confirmed absent |
| `ganDamodana` | True | — | likely false negative (exact-match too strict) |
| `cyut` | True | `cyuta`; `cyutAm` | likely false negative (exact-match too strict) |
| `tElaspandA` | False | — | confirmed absent |
| `drOpada` | True | — | likely false negative (exact-match too strict) |
| `nIcaka` | False | — | confirmed absent |
| `piWarapAka` | False | — | confirmed absent |
| `prasekin` | True | — | likely false negative (exact-match too strict) |
| `Binnaviwka` | False | — | confirmed absent |
| `mApay` | True | `mApayAmAsuH`; `mApayAmAsa` | likely false negative (exact-match too strict) |
| `raTANgAhva` | False | — | confirmed absent |
| `varRasa` | False | `varRasaNkara`; `varRasaNkara` | likely false negative (exact-match too strict) |
| `vizAditA` | False | — | confirmed absent |
| `SArIrakaSAstradarpaRa` | False | — | confirmed absent |
| `saMveSanIya` | False | — | confirmed absent |
| `sidDAntalaGuKamARika` | False | — | confirmed absent |

## Result

**13 of 20 (65%) sampled "absent" headwords are confirmed absent** by both independent checks; the rest are likely false negatives of the exact-match test (the headword occurs only in an inflected surface form in the aligned corpus, or is attested by the separate DCS-level Renou pass). This is the concrete evidence behind the E4 report's stated caveat that exact-match `corpus_lexicon.jsonl` presence is a stricter, lossier test than `renou_dcs` — quantified here rather than only asserted.

_Dr. Mārcis Gasūns_
