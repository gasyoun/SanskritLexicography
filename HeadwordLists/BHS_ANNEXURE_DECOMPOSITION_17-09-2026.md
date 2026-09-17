# BHS annexure enrichment (2.09×) decomposed — Edgerton (1953) vs MW99 (1899)

_Created: 17-09-2026 · Last updated: 17-09-2026_

H5057. Companion to [`MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md) (§2/§6, where the 2.09× headline and the 95-candidate class were first measured). Builder: [`bhs_enrichment_decompose.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/bhs_enrichment_decompose.py). csl-orig read-only throughout.

## 1 · Headline re-derived (convention-robustness)

| convention | BHS set | in annexure | in main | enrichment |
|---|--:|--:|--:|--:|
| k1-only (doc §2 convention) | 17,777 | 413 | 6,128 | **2.09×** |
| k1∪k2 | 21,146 | 413 | 6,128 | 2.09× |

MW99 k1 total 194,083 = annexure 6,067 + main 188,016 — matches doc §2 to the row. The headline figure is **identical under both conventions** (2.09×), so the 2.09× is not a k1/k2 artifact.

## 2 · Decomposition by BHS entry class (the volume axis)

The Cologne digitization is **one printed volume** — Edgerton, *BHSD* Vol II: Dictionary (1953); `bhs-meta2.txt` pins 17,839 entries. There is no multi-volume layer to split (unlike PW's `sup_1`…`sup_7`), so the volume axis resolves into the entry-class cut the digitization itself carries: gloss-bearing full entries vs bracketed cross-reference entries ([… see …]).

| BHS class | entries (k1) | in annexure | in main | enrichment | reading |
|---|--:|--:|--:|--:|---|
| full (gloss-bearing) | 17,071 | 407 | 5,958 | **2.12×** | the 2.09× is carried here |
| cross-reference | 706 | 6 | 170 | 1.09× | enrichment-neutral pointers |
| all | 17,777 | 413 | 6,128 | 2.09× | = headline |

**Reading:** the entire annexure enrichment comes from Edgerton's *definitional* vocabulary (2.12×); his 712 cross-reference entries (706 unique k1 after dedup) behave like housekeeping (1.09×). The 2.09× headline is therefore a genuine signal about Buddhist-Hybrid **word-stock** MW99 lacked, not an artifact of reference-structure — and it stays far below the PW-Nachträge 7.79–7.91×, because Edgerton post-dates MW99 by 54 years and could not have fed it.

## 3 · Decomposition by Edgerton's own Buddhist-technical markers

| marker class | entries (k1) | in annexure | in main | enrichment |
|---|--:|--:|--:|--:|
| mvy_cites (Mvy = Mahāvyutpatti) | 3,186 | 124 | 1,848 | 2.08× |
| no_mvy_cites (Mvy = Mahāvyutpatti) | 14,591 | 289 | 4,280 | 2.09× |
| tib_gloss (<tib>) | 1,882 | 69 | 923 | 2.32× |
| no_tib_gloss (<tib>) | 15,895 | 344 | 5,205 | 2.05× |

**Reading:** entries where Edgerton cites the Mahāvyutpatti are *less* represented in MW99 overall (MW99 barely carries Buddhist-technical vocabulary anywhere), but the marker cut shows where MW99's small Buddhist layer lives; the class cut (§2) remains the load-bearing decomposition.

## 4 · The 95 BHS-corroborated confirmed-missing candidates

Of the 1,751 `confirmed-missing` rows in [`MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv), **95** are attested in BHS/Edgerton — reproduced exactly. Full enumeration with DCS bands, BHS loci (`<L>` tag + page,column), both MAHAVY ref surfaces (PW-side `mahavy_refs` from the adjudication + BHS-side `<ls>Mvy</ls>` citations — distinct from `Mv` = Mahāvastu) and corroboration: [`BHS-CORROBORATED-MISSING-95-17-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/BHS-CORROBORATED-MISSING-95-17-09-2026.tsv).

| DCS band | candidates | note |
|---|--:|---|
| 3 (uncommon, 10–99) | 1 | |
| 2 (rare, 2–9) | 5 | |
| 1 (hapax) | 5 | |
| 0 (unattested) | 84 | **88 % of the class — DCS-2021 carries almost no Buddhist canon, so absence there is expected, not disqualifying** |

Entry classes of the 95: full 92 · crossref 3. BHS-side Mvy citations: 58 · PW-side mahavy_refs: 60. Every row keeps `proposed_action = add-entry` and the printed-scan-verification caveat of the parent proposal list.

## 5 · Reproduction

```sh
python3 HeadwordLists/bhs_enrichment_decompose.py            # ~40 s, stdlib only
python3 HeadwordLists/bhs_enrichment_decompose.py --selftest  # exit 1 on headline drift
```

Reads `csl-orig/v02` (`CSL_ORIG_V02`) + `VisualDCS/dcs_lemma_summary.json` (`DCS_LEMMA_JSON`) + the adjudication TSV; auto-falls back to the sibling clones. Selftest pins: 17,839 entries · 17,777 k1 · 21,146 k1∪k2 · 413 annexure · 6,128 main · 2.09× · 1,751 confirmed-missing · 95 BHS-corroborated.

## 6 · Caveats

1. Set overlaps, not citations (parent doc §9.1 applies unchanged).
2. `dcs_band 0` = not attested in the DCS-2021 snapshot; the corpus is classical-heavy — treat as a coverage fact of the *control corpus*, not of the candidates.
3. Two counting bases, both stated: the class table (§2) counts **unique k1** headwords after dedup (full 17,071 + crossref 706 = 17,777); the entry census (`bhs-meta2.txt`) counts **17,839 entries** (712 of them cross-reference). A headword occurring as both keeps its full record (5 k1 collisions).
4. `Mvy` regex deliberately excludes `<ls>Mv</ls>` (Mahāvastu) — same trap as the parent doc's MAHĀVY two-pattern note.

## 7 · Verifier (H5057) — two-pass, 17-09-2026

- **Pass 1, execution-capable (worker session, OxAlpha `opencode/z-ai/glm-5.3-flash`):** independent throwaway probes re-derived 194,083/6,067/188,016 and 413/6,128 → 2.0886× and the 95-candidate class from `csl-orig` **before** the builder was written; then `bhs_enrichment_decompose.py --selftest` pinned all ten headline counts + the class partition (exit 0). TSV top rows match parent doc §5 sample in order.
- **Pass 2, independent static recheck (DeepSeek `deepseek-v4.1-flash` seat, read-only):** recomputed every §1–§3 enrichment label from its own stated counts (all reproduce), validated TSV shape/bands/order (95 rows, {3:1, 2:5, 1:5, 0:84}), checked parent-doc parity line-by-line, and validated the `<L>`-line parsing convention against `tests/fixtures/csl_orig_mini`. Its one real finding — §2 prose hardcoded «712 … 1.07×» contradicting the computed table «706 … 1.09×» (entry-count vs unique-k1 basis) — was fixed by deriving the prose from the computed values (the seat had no execution/sandbox access, so the source-side counts were certified by Pass 1).
- **Overall: PASS** (parity certified statically; source-side counts re-derived executably; found defect fixed and re-run green).

_Гасунс_
