_Created: 15-09-2026 · Last updated: 15-09-2026_

# H4713 — Stem co-occurrence expansion of pwg-sense-attestation-window

_Created: 15-09-2026 · Handoff [H4713](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4713-OxAlpha_SanskritLexicography_xwalk-a7-cooccurrence-attest-window_14.09.26.md) · Base artifact: [C2P1_ATTESTATION_WINDOW.md](C2P1_ATTESTATION_WINDOW.md) (H3168)_

_Dr. Mārcis Gasūns_

**What this is:** the Census-A7 extension of the C2 phase-1 per-sense attestation
window with a **co-occurrence-based expansion**. Every sense of
[pwg_sense_attestation_window.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sense_attestation_window.jsonl)
(53,003 senses) gains a second evidence class derived from the kosha dataset
[dcs-stem-cooccurrence-full](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)
(VisualDCS `derived-data/Sochetaemost-sanskritskih-osnov/NEW/1-222342.csv`,
353,351 stem-pair rows): the headword's DCS co-occurring stems (L+R pooled,
self excluded) that themselves carry a C2P1 window vote a weighted window for
the headword.

**Output:** [pwg_sense_attestation_window_cooc_expanded.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sense_attestation_window_cooc_expanded.jsonl)
(53,003 rows; original fields untouched) + validation JSON
[H4713_cooc_window_expansion_validation.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4713_cooc_window_expansion_validation.json).
Builder: [h4713_cooc_window_expand.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4713_cooc_window_expand.py) (`--selftest` green).

## Honesty contract

The BR window stays *«per Böhtlingk–Roth's citations»* — a fact about the
dictionary. The new fields are a **different evidence class**: corpus
co-occurrence, i.e. *stems that share DCS passages with the headword*. A cooc
window is never a BR citation, never merged into `earliest`/`latest`, and a
`cooccurrence-only` window is explicitly labelled as inferred, not cited.

New fields per row: `cooc_partner_n`, `cooc_weight` (raw pooled pair counts),
`cooc_earliest` (weighted p10 of partner window-earliest values),
`cooc_latest` (weighted p90 of partner window-latest values),
`expanded_earliest`/`expanded_latest` (union of BR window and cooc window),
`expansion_delta_left`/`expansion_delta_right` (years pushed past the BR
window, ≥ 0), `cooc_saturated`, `window_basis` ∈ `br-citations` |
`br-citations+cooccurrence` | `cooccurrence-only` | `none`.

## The saturation finding (read this before consuming)

Co-occurrence degree dominates informativeness. High-degree heads (hundreds of
partners spanning all eras) saturate: their p10/p90 land on the corpus horizon
(-1125 Ṛgveda … 1830 Śabdakalpadruma) and the "expansion" is a wide net that
adds little discrimination. Low-degree heads (specialized collocations) get
genuinely informative windows — e.g. `saMropaRa` (1 partner, w=9) infers
70…1150 around its BR 400. The table therefore carries
`cooc_saturated: true` (35,390 of 40,013 senses with evidence — 88.4%) so
consumers can filter to the informative stratum. **Recommended consumer
filter: `cooc_saturated == false`.**

<!-- h4713:generated:start -->

## Coverage table

| Bucket | Senses | Share |
| --- | --- | --- |
| Total senses | 53,003 | 100% |
| With co-occurrence evidence (≥1 windowed partner) | 40,013 | 75.5% |
| …of which saturated at corpus horizon (flagged) | 35,390 | 66.8% of total |
| BR-windowed senses widened by co-occurrence | 33,958 | — |
| BR-windowed senses NOT widened (cooc inside BR window) | 452 | — |
| `cooccurrence-only` (no BR window; previously empty, now inferred-only) | 5,603 | 10.6% of total |
| Median expansion delta (BR-windowed, widened) | 2,305 years | — |

Join rate note: 50,468 of 80,776 co-occurrence stem rows transliterate into the
17,292-key1 window universe (14.3% direct) — the ceiling is the window file's
own coverage (numbered-sense headwords only, 19,454 of PWG's ~109k), not the
transliteration. Partner IDs unresolved by the CSV's own stem list: ~0.01%
(2 of 20,013 probed), counted, never guessed.

## Held-out verification (seed 4713, n=300 windowed senses)

The cooc window is derived WITHOUT the sense's own BR window (partners are
other stems by construction; self excluded both spellings) and checked against
the true window. Pre-registered PASS rule: intersection ≥ 50%. **PASS.**

| Stratum | n | Intersection rate | Containment rate |
| --- | --- | --- | --- |
| Overall | 300 | 99.0% | 97.3% |
| Saturated (trivial: union spans corpus horizon) | 272 | 100% | 100% |
| **Non-saturated (informative stratum)** | 28 | **89.3%** | **71.4%** |

The expansion cannot shrink a window by construction (union), so intersection
is the coverage floor; containment 71.4% on the informative stratum is the
honest precision figure. Consume the expansion as *widening evidence*, never
as a replacement for the BR window.

## Deterministic sample (every 2,500-th sense with cooc evidence)

| key1 | sense | BR window | cooc window (n, w) | expanded | basis |
| --- | --- | --- | --- | --- | --- |
| a | 0 | -900…1830 | -1125…1830 (938, 3822) | -1125…1830 | br+cooc (saturated) |
| avatAraNa | 1 | 70…1150 | -1125…1830 (14, 62) | -1125…1830 | br+cooc (saturated) |
| upaviZa | 0 | 1150…1150 | -1125…1830 (3, 17) | -1125…1830 | br+cooc (saturated) |
| kelikalA | 0 | — | -1125…1830 (3, 6) | -1125…1830 | cooccurrence-only |
| car | 46 | -1125…70 | -1125…1830 (679, 3164) | -1125…1830 | br+cooc (saturated) |
| tola | 0 | — | -1125…1830 (5, 10) | -1125…1830 | cooccurrence-only |
| nam | 18 | 200…200 | -1125…1830 (197, 608) | -1125…1830 | br+cooc (saturated) |
| parvan | 0 | -1125…1150 | -1125…1830 (202, 631) | -1125…1830 | br+cooc (saturated) |
| prAcya | 2 | — | -1125…1830 (32, 66) | -1125…1830 | cooccurrence-only |
| mardana | 1 | 1050…1050 | -1125…1830 (111, 398) | -1125…1830 | br+cooc (saturated) |
| kamala | 1 | 80…1830 | -1125…1830 (202, 647) | -1125…1830 | br+cooc (saturated) |
| raji | 1 | -1125…-1125 | -1125…1830 (7, 17) | -1125…1830 | br+cooc (saturated) |
| vahana | 1 | -500…1150 | -1125…1830 (23, 55) | -1125…1830 | br+cooc (saturated) |
| veSya | 2 | -1125…1200 | -1125…1830 (1, 2) | -1125…1830 | br+cooc |
| saMropaRa | 0 | 400…400 | **70…1150** (1, 9) | 70…1150 | br+cooc — informative |

<!-- h4713:generated:end -->

## Edge registration

- kosha `datasets.json`: `dcs-stem-cooccurrence-full` consumer added (this expansion), `awaiting-consumer` status retired.
- Uprava `interlinks_edges.tsv` + PROJECT_INTERLINKS.md: VisualDCS → SanskritLexicography edge row (`cooc-window-expansion`).

_Dr. Mārcis Gasūns_
