# Appendix A — The MW-unabsorbed census: data tables

_Created: 17-09-2026 · Last updated: 17-09-2026_

> **Placement note.** The book's unified method appendix (BOOK_PLAN §6) is gated on the chapter
> freeze and does not exist yet; this entry is the first committed appendix artefact and will be
> renumbered/absorbed at freeze without content change. Cited from Chapter 12, §3.5 ("The
> unabsorbed residual"), which carries the prose reading of the numbers below; per the 17-09-2026
> routing ruling the chapter itself stays prose and the tables live here.

**Source.** Census of what the Petersburg *Nachträge* (the seven supplement volumes of Böhtlingk's
`pw`) hold that Monier-Williams never absorbed; volume 7 base (35,581 entries) unless a row names
another layer (`sup_1`…`sup_6`). Built by
[`mw_unabsorbed_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_unabsorbed_census.py)
(deterministic, stdlib-only, ~8 s) from the Cologne digitizations; method, canaries and the full
class-by-class reading in
[`MW-UNABSORBED-CENSUS-WIDENED-16-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-WIDENED-16-09-2026.md)
(frozen and verifier-PASSed 16-09-2026). The three machine-readable outputs are committed beside
the builder:
[HOMONYM-EXTENSIONS (571 rows)](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-HOMONYM-EXTENSIONS-16-09-2026.tsv) ·
[POS-CLASS](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-POS-CLASS-16-09-2026.tsv) ·
[ALL-LAYERS](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-ALL-LAYERS-16-09-2026.tsv).

## A.1 — All supplement layers (ALL-LAYERS)

Unique headwords per supplement layer, and where MW did and did not take them up. `skipped by
both` = absent from MW72 *and* MW99. The volume-7 row is the chapter's headline base.

| layer | entries (unique) | in PW main body (extensions) | new headwords | `<hom>`-tagged | in MW72 | in MW99 | skipped by both |
|---|--:|--:|--:|--:|--:|--:|--:|
| `sup_1` | 1,755 | 765 | 990 | 62 | 342 | 991 | 758 |
| `sup_2` | 1,464 | 530 | 934 | 40 | 259 | 757 | 703 |
| `sup_3` | 1,712 | 707 | 1,005 | 70 | 361 | 1,136 | 573 |
| `sup_4` | 1,016 | 359 | 657 | 45 | 180 | 669 | 347 |
| `sup_5` | 2,192 | 1,056 | 1,136 | 140 | 564 | 1,568 | 615 |
| `sup_6` | 1,229 | 522 | 707 | 70 | 264 | 808 | 420 |
| **`sup_7`** | **13,094** | **4,688** | **8,406** | **541** | **2,892** | **8,955** | **4,112** |

## A.2 — Part-of-speech cross-cut (POS-CLASS)

`share_pct` is the share within the class. The broad extension class is 85.6 % untagged — its POS
distribution is reported as sparsity, not claimed as a distribution (the census's own refutation
clause); the informative cross-cut is the homonym-extension class, where the unabsorbed further
homonyms are **adjectives first, by a wide margin**.

| class | POS | n | share % | note |
|---|---|--:|--:|---|
| homonym-extension (`sup_7`) | adj. | 296 | 51.8 | vol-7 `<hom>` > MW main max |
| homonym-extension (`sup_7`) | (no lex) | 129 | 22.6 | vol-7 `<hom>` > MW main max |
| homonym-extension (`sup_7`) | m. | 69 | 12.1 | vol-7 `<hom>` > MW main max |
| homonym-extension (`sup_7`) | f. | 28 | 4.9 | vol-7 `<hom>` > MW main max |
| homonym-extension (`sup_7`) | n. | 27 | 4.7 | vol-7 `<hom>` > MW main max |
| homonym-extension (`sup_7`) | adv. | 20 | 3.5 | vol-7 `<hom>` > MW main max |
| homonym-extension (`sup_7`) | other | 2 | 0.4 | vol-7 `<hom>` > MW main max |
| extension-of-PW-main-body (`sup_7`) | (no lex) | 4,011 | 85.6 | sup_7 headword present in PW main body |
| extension-of-PW-main-body (`sup_7`) | m. | 228 | 4.9 | sup_7 headword present in PW main body |
| extension-of-PW-main-body (`sup_7`) | n. | 150 | 3.2 | sup_7 headword present in PW main body |
| extension-of-PW-main-body (`sup_7`) | f. | 144 | 3.1 | sup_7 headword present in PW main body |
| extension-of-PW-main-body (`sup_7`) | adj. | 141 | 3.0 | sup_7 headword present in PW main body |
| extension-of-PW-main-body (`sup_7`) | adv. | 14 | 0.3 | sup_7 headword present in PW main body |
| new-headword (`sup_1`) | (not tabulated) | 990 | — | absent from PW main body |
| new-headword (`sup_2`) | (not tabulated) | 934 | — | absent from PW main body |
| new-headword (`sup_3`) | (not tabulated) | 1,005 | — | absent from PW main body |
| new-headword (`sup_4`) | (not tabulated) | 657 | — | absent from PW main body |
| new-headword (`sup_5`) | (not tabulated) | 1,136 | — | absent from PW main body |
| new-headword (`sup_6`) | (not tabulated) | 707 | — | absent from PW main body |
| new-headword (`sup_7`) | (not tabulated) | 8,406 | — | absent from PW main body |
| never-seen-MW72-and-MW99 (`sup_7`) | (all) | 4,112 | — | absent from both MW editions |
| dropped-between-editions (`sup_7`) | (all) | 27 | — | MW72 had it, MW99 lost it |

## A.3 — Reading caveats (they travel with the tables)

1. **Numbering comparability.** MW's `<h>` and Petersburg's `<hom>` numbering are not proven 1:1
   comparable; the 571 homonym-extensions move within a **498–626** band across defensible
   definitions of "extension" (main-body max 571 · annexure-inclusive 563 · `<h>`-attribute base
   507 · entry-own-marker 498 · MW-headedness not required 626). All variants stay machine-checkable
   in the HOMONYM-EXTENSIONS TSV's `mw_*_max_hom` / `annexure_covers` columns.
2. **The annexure coincidence.** For exactly 8 of the 571, MW's *annexure* carries a homonym number
   ≥ N — a numbering coincidence, not semantic coverage: the canary `kārin³` (MW annexure,
   "scattering, destroying," fr. √kṛ) is a *different derivation* from the pw volume-7 homonym 3
   (`pw.txt` line 620966). The other **563** have no MW annexure homonym number ≥ N at all.
3. **Digitization provenance.** Every figure in this appendix describes the **Cologne digitizations**
   (`csl-orig`), not the printed page — canary `kāritra` (`pw.txt` line 620963, `7-331-d`)
   reproduces from the digitized source alone. Print-page collation is a separate, unstarted lane.
4. **Disjointness.** The 571-class is disjoint from the sup_7 adjudication pool (0/571 overlap):
   these are words MW already heads, resolved by *numbering* rather than by headword absence.

_Гасунс_
