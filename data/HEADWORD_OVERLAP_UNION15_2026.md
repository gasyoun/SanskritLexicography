# Headword pairwise-overlap matrix — 15-dict union, 2026

_Created: 11-07-2026 · Last updated: 13-07-2026_

**What this is.** The "headword union & pairwise overlap" row of the
statistics-to-compute table in
[DATA_LAYERS_CENSUS.md §3](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md):
which dictionaries share which headwords, and which headwords are unique to one
dictionary. Handoff:
[H684](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H684-Fable_SanskritLexicography_headword-pairwise-overlap-matrix_11.07.26.md)
(Lane B, Fable sprint). Computed 11-07-2026 by Fable 5 (`claude-fable-5`).

## Method — and the key normalization, documented

- Input: the existing
  [union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
  (**323,425 rows, 15 dictionaries** — AP BHS BUR CAE CCS GRA INM MD MW PWG PWK
  SCH SKD VCP VEI), consumed as-is per the reuse rule — the union is never
  rebuilt here.
- **Key normalization (per
  [UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)):**
  the union key is the bare **SLP1 lemma from each dict's csl-orig `<k1>`**,
  homograph numbering (`<h>`) collapsed, with 237 gender-confirmed `-inī`
  feminines folded onto their `-in` base. Overlap below is therefore **exact
  SLP1 string equality on that key** — no NFD/strip-diacritics or other ad-hoc
  normalization is applied (the known NFD+strip-Mn trap that kills vowel length
  and retroflex dots never enters this pipeline).
- Script:
  [headword_overlap_matrix.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/headword_overlap_matrix.py).
  Outputs
  [headword_overlap_matrix.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/headword_overlap_matrix.tsv)
  (105 unordered pairs: `dict_a dict_b shared union jaccard`) and
  [headword_unique_counts.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/headword_unique_counts.tsv)
  (per dict: total, unique-to-dict, unique share).
- **The stale "94,753" resolved.** Older references (including the H684 handoff
  itself and the census row) describe the union as "94 k". The union is
  323,425; **94,753 is exactly the MW∩PWG shared-headword count** computed
  here — the old figure was an intersection mislabeled as the union.

## Per-dict totals and unique inventories

| dict | headwords | unique to dict | unique share |
|---|--:|--:|--:|
| AP | 88,744 | 35,762 | 40.3% |
| BHS | 17,761 | 10,434 | 58.7% |
| BUR | 19,135 | 4,625 | 24.2% |
| CAE | 38,476 | 661 | 1.7% |
| CCS | 28,743 | 178 | 0.6% |
| GRA | 11,108 | 467 | 4.2% |
| INM | 9,431 | 2,355 | 25.0% |
| MD | 20,095 | 399 | 2.0% |
| MW | 193,852 | 44,156 | 22.8% |
| PWG | 106,054 | 2,511 | 2.4% |
| PWK | 151,314 | 8,155 | 5.4% |
| SCH | 28,431 | 8,836 | 31.1% |
| SKD | 40,703 | 17,333 | 42.6% |
| VCP | 48,583 | 6,303 | 13.0% |
| VEI | 3,702 | 446 | 12.0% |

Sanity anchors: PWG 106,054 ≈ the frozen
[PWG-unique-key1-106085](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/PWG-unique-key1-106085.txt)
export and MW 193,852 ≈ MW-unique-key1-193978 (small deltas = the union's
feminine folds and homograph collapse).

## Shared-count matrix (diagonal = dict totals)

| | AP | BHS | BUR | CAE | CCS | GRA | INM | MD | MW | PWG | PWK | SCH | SKD | VCP | VEI |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| **AP** | 88744 | 1962 | 7246 | 13048 | 9982 | 3733 | 2212 | 8269 | 38082 | 23708 | 26648 | 4535 | 18828 | 15753 | 890 |
| **BHS** | 1962 | 17761 | 1567 | 2433 | 2163 | 599 | 957 | 1763 | 6525 | 4779 | 6088 | 2212 | 599 | 2599 | 353 |
| **BUR** | 7246 | 1567 | 19135 | 7510 | 6853 | 2639 | 1705 | 6447 | 13908 | 12534 | 12566 | 2920 | 2097 | 10217 | 1150 |
| **CAE** | 13048 | 2433 | 7510 | 38476 | 27008 | 6780 | 3300 | 13366 | 35053 | 29051 | 34144 | 4898 | 1697 | 14307 | 2138 |
| **CCS** | 9982 | 2163 | 6853 | 27008 | 28743 | 5708 | 2779 | 11924 | 25881 | 23856 | 27174 | 4047 | 1522 | 11940 | 1919 |
| **GRA** | 3733 | 599 | 2639 | 6780 | 5708 | 11108 | 918 | 4107 | 9752 | 8961 | 9645 | 1277 | 713 | 3987 | 1505 |
| **INM** | 2212 | 957 | 1705 | 3300 | 2779 | 918 | 9431 | 2045 | 6772 | 5561 | 5900 | 1035 | 622 | 3755 | 658 |
| **MD** | 8269 | 1763 | 6447 | 13366 | 11924 | 4107 | 2045 | 20095 | 18631 | 15187 | 17833 | 3866 | 1608 | 9452 | 1581 |
| **MW** | 38082 | 6525 | 13908 | 35053 | 25881 | 9752 | 6772 | 18631 | 193852 | 94753 | 128971 | 14499 | 8743 | 39011 | 3166 |
| **PWG** | 23708 | 4779 | 12534 | 29051 | 23856 | 8961 | 5561 | 15187 | 94753 | 106054 | 99437 | 7778 | 5497 | 34622 | 2949 |
| **PWK** | 26648 | 6088 | 12566 | 34144 | 27174 | 9645 | 5900 | 17833 | 128971 | 99437 | 151314 | 18285 | 5635 | 35251 | 3017 |
| **SCH** | 4535 | 2212 | 2920 | 4898 | 4047 | 1277 | 1035 | 3866 | 14499 | 7778 | 18285 | 28431 | 967 | 5366 | 557 |
| **SKD** | 18828 | 599 | 2097 | 1697 | 1522 | 713 | 622 | 1608 | 8743 | 5497 | 5635 | 967 | 40703 | 6892 | 341 |
| **VCP** | 15753 | 2599 | 10217 | 14307 | 11940 | 3987 | 3755 | 9452 | 39011 | 34622 | 35251 | 5366 | 6892 | 48583 | 1817 |
| **VEI** | 890 | 353 | 1150 | 2138 | 1919 | 1505 | 658 | 1581 | 3166 | 2949 | 3017 | 557 | 341 | 1817 | 3702 |

## Findings

- **Most-overlapping pairs (Jaccard):** CAE–CCS **0.672** (Cappeller's English
  and German editions of the same dictionary — the expected maximum), PWG–PWK
  **0.630** (Böhtlingk large vs small), MW–PWK **0.597**, MW–PWG **0.462**.
  The lexicographic core is one Böhtlingk–Monier-Williams lineage. **That
  lineage is why "attested in N dicts" overstates corroboration** — see the
  [witness-independence re-audit](WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md),
  which collapses these non-independent witnesses (operationalizing the
  [FINDINGS §83/§97](../FINDINGS.md) ruling) and finds the union's corroborated
  share falls from 55.9% to 34.7% once MW folds into the Petersburg witness.
- **Least-overlapping pairs:** SKD–VEI 0.008, AP–VEI 0.010, BHS–SKD 0.010 —
  the Vedic index (VEI), the Buddhist Hybrid lexicon (BHS) and the
  Sanskrit–Sanskrit Śabdakalpadruma (SKD) live in near-disjoint lexical worlds.
- **Biggest unique inventories (absolute):** MW 44,156 · AP 35,762 · SKD
  17,333 · BHS 10,434 · SCH 8,836. Apte's 40.3% unique share is the
  under-appreciated result — nearly half of AP is in no other dictionary of
  the union.
- **Most isolated (unique share):** BHS 58.7% — by far; then SKD 42.6% and AP
  40.3%. **Most subsumed:** CCS 0.6%, CAE 1.7%, MD 2.0%, PWG 2.4% — the
  school dictionaries are almost fully contained in the MW/PWK superset, and
  PWG's headword list survives nearly whole in its own abridgements.
- **Provenance recap** (from UNION.md): 142,673 singletons (44.1% of the
  union) vs 180,752 shared headwords.

## FAIR release

This dataset (E40) is bundled into
[FAIR Release #1](FAIR_RELEASE_1.md) (H817 WS1.4) alongside the markup-tag
census and (cross-linked) the csl-atlas citation graph — CC-BY-4.0, Zenodo
deposit metadata prepared, deposit itself parked as `@DO`.

_Dr. Mārcis Gasūns_
