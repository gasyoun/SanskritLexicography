# Union headwords 16 dicts — rebuild from now-2026 lists, overlap matrix (H4797)

_Created: 19-09-2026 · Last updated: 19-09-2026_

**What this is.** The 16-dict union headword index rebuilt from the per-dict
unique key1/key2 lists ON DISK in
[now-2026/](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/now-2026/)
(16 dicts, 25 data files: AP BHS BUR CAE CCS GRA INM MD MW PD PWG PWK SCH SKD
VCP VEI), plus the pairwise overlap matrix over it. This unblocks the
overlap-matrix / routing analysis from the 15-dict union
([data/HEADWORD_OVERLAP_UNION15_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/HEADWORD_OVERLAP_UNION15_2026.md)):
**PD joins for the first time**, and every dict's count is refreshed to the
current now-2026 snapshot. Handoff:
[H4797](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4797-OxAlpha_SanskritLexicography_union-headwords-16dict-extension_14.09.26.md).
Computed 19-09-2026 by OxAlpha (`opencode/z-ai/glm-5.3-flash`).

## Headline numbers

- **Union: 417,184 headwords over 16 dicts** (15-dict baseline: 323,425; +PD
  ~104.9k raw keys, heavy overlap as expected).
- Corroboration histogram: n=1: 232,375 · n=2: 63,045 · n=3: 47,346 ·
  n=4: 29,354 · n=5: 17,729 · n=6: 10,578 · n=7: 6,019 · n=8: 4,053 ·
  n=9: 2,959 · n=10: 1,933 · n=11: 1,019 · n=12: 505 · n=13: 203 · n=14: 53 ·
  n=15: 11 · **n=16: 2** (`aNga`, `aRu` — attested in every dictionary).
- Matrix: **120 unordered pairs** (was 105) →
  [headword_overlap_matrix.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union-16dicts/headword_overlap_matrix.tsv);
  per-dict totals/uniques →
  [headword_unique_counts.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union-16dicts/headword_unique_counts.tsv).
- Top pairs by Jaccard: CAE-CCS J=0.672 (26,836 shared) · PWG-PWK J=0.630
  (99,456) · MW-PWK J=0.596 (129,004) · MW-PWG J=0.461 (94,782) · CCS-MD
  J=0.323 (11,918).
- Bottom pairs: PD-VEI J=0.001 (67 shared) · PD-SKD J=0.002 (267) · INM-PD
  J=0.002 (262) — PD's printed Petersburg key space barely intersects the
  small Cologne dicts.
- PD is 89.0% single-dict unique (93,462 of 104,962) — the key2-only printed
  forms have almost no Cologne counterpart.

## Key normalization contract (the load-bearing part)

Union key = bare SLP1 lemma. key1 lines are used as-is (verified bare); key2
print forms are normalized:

1. parenthetical segments stripped whole — annotations like
   `akzuRRa(-vyAkaraRa)`, `acalitasumana(s)`, `aYja (aYjas)`;
2. marks removed: `/` (udātta), `˚` (elision), `*` (reconstructed), `'`
   (avagraha), `^`/`|` (uncertainty), `-`/`–`/`—`/`‐` (compound hyphens) —
   each verified absent from the k1 key space (printed `ato'nya` is `atonya`
   in MW k1; `aMSa˚prakalpanA` joins MD's `aMSaprakalpanA`);
3. a line STARTING with `(` or a digit, or still carrying a mark after (1)+(2),
   is **residue: counted per class and EXCLUDED** — never guessed into the
   union (microstructure rule). Residue total 1,997 of 1,676,661 raw lines
   (0.12%); full per-dict, per-class breakdown in
   [per_dict_profile.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union-16dicts/per_dict_profile.tsv).

Per dict, membership = norm(key1) ∪ norm(key2). Known differences vs the
published 15-dict union: NO feminine folding here (the 237 `-inī` folds of
build_union.py are a morphological audit, out of scope for a raw key-space
overlap index) and homograph numbering is already absent from the now-2026
files. The `iast` column is deliberately absent — sanskrit-util is not on the
run box and a passthrough fake transliteration would be worse than none
(H3985 rule).

## Prove with

```
python3 HeadwordLists/build_union16.py --selftest        # 18 classification canaries PASS
python3 HeadwordLists/build_union16.py                   # rebuilds union_headwords_16.tsv + per_dict_profile.tsv
python3 data/headword_overlap_matrix.py \
  --union HeadwordLists/union-16dicts/union_headwords_16.tsv \
  --outdir HeadwordLists/union-16dicts                   # 417184 rows; 16 dicts; 120 pairs
python3 -m pytest tests/test_data_modules.py::test_headword_overlap_matrix_on_mini_union -q   # PASS (unchanged default behavior)
```

Own-data canaries (all PASS): `akzuRRa` ← BHS `akzuRRa(-vyAkaraRa)` in 7
dicts · `akz` ← BUR `*akz` in 9 · `aMSaprakalpanA` ← CAE `aMSa˚prakalpanA` in
5 (CAE+MD both) · `atonya` ← MW `ato-'nya` in MW+PD · PD k2-only `agopoha`
present · `aNga`/`aRu` in all 16 dicts.

## Files

- [build_union16.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/build_union16.py) — the builder (offline, reads only now-2026/)
- [union_headwords_16.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union-16dicts/union_headwords_16.tsv) — 417,184 rows, `slp1 n_dicts dicts`
- [per_dict_profile.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union-16dicts/per_dict_profile.tsv) — per-dict raw/bare/residue-by-class
- [headword_overlap_matrix.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union-16dicts/headword_overlap_matrix.tsv) · [headword_unique_counts.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union-16dicts/headword_unique_counts.tsv)

The published 15-dict artifacts (`HeadwordLists/union/`, `data/headword_overlap_matrix.tsv`)
are untouched.

_Гасунс_
