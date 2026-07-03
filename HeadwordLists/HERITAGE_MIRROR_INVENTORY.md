# Heritage/INRIA GitHub-mirror inventory

_Created: 03-07-2026 · Last updated: 03-07-2026_

What [darkone23/Heritage_Resources](https://github.com/darkone23/Heritage_Resources)
(`develop-main`, sparse-checked-out `DATA/ MW/ DICO/ XML/` at
`HeadwordLists/heritage_mirror/`, gitignored per
[HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md)
Phase 0) actually contains, verified by inspection (03-07-2026), against the
roadmap's API-only claims.

## Sizes (sparse checkout: `DATA/ MW/ DICO/ XML/` only — `BOOK/` and `CORPUS/` not fetched)

| Dir | Size | File count | Contents |
|---|--:|--:|---|
| `MW/` | 118 MB | 318 `.html` + `style.css` | Hypertext Monier-Williams, split by CDSL page number, hyperlinked to DICO where Heritage covers an entry |
| `DICO/` | 27 MB | 76 `.html` | Hypertext Heritage dictionary (French glosses), split by page |
| `DATA/` | 22 MB | 37 files | OCaml `.rem` persistent lexicon banks + 6 plain-TSV frequency tables |
| `XML/` | 108 KB | 3 + LICENSES | Legacy DTDs (`SL_morph.dtd`, `WX_morph.dtd`) + LGPLLR license text/PDF/tex |

## MW↔Heritage coverage marking (confirms roadmap's "yellow areas")

The mirror's own `README` states: *"MW contains the hypertext version of the
Monier-Williams dictionary aligned with DICO. **The yellow areas show the
entries covered by Heritage.**"* In the static HTML (no longer live-styled),
this is encoded as a duplicate anchor: a covered MW entry carries both
`<a name="H_<key>">` and `<a name="<key>">` immediately before its Deva span;
an uncovered entry carries only `<a name="<key>">`. Verified counts:

- MW total `H_`-prefixed (covered) anchors across all 319 pages: **26,833**
- DICO total headword anchors (`<a class="navy" name="...">`) across all 76
  pages: **46,332** raw / **45,849** unique after dedup (DICO carries more
  entries than MW-covered because DICO also documents grammatical
  roots/affixes/proper nouns MW covers under different key conventions, and
  some DICO entries have no MW parallel at all).
- DICO anchor-key conventions **not present in the 2014 stem-list export**
  ([`then-2014/21562-huet-velthius.txt`](then-2014/21562-huet-velthius.txt)):
  a leading `U` marks a proper noun (`Uaadinaatha` = `aadinaatha` in the 2014
  list — the 2014 export drops the marker), a leading `-` marks a bound
  affix/suffix fragment, not a free stem (`-a`, `-tva`; **absent** from the
  2014 list entirely), and a trailing `#N` disambiguates homonyms sharing one
  key. [heritage_stem_extract.py](heritage_stem_extract.py) normalizes all
  three away for a like-for-like current-vs-2014 comparison (Phase 1).
- The `H_<key>` and DICO `navy` anchor keys use the **same VH-derived
  transliteration convention** and — for entries with a single-word key —
  the **same literal string**, so an MW-covered key can be looked up directly
  against the DICO anchor index without a separate crosswalk table. This is
  the mechanism [heritage_mw_crosswalk.py](heritage_mw_crosswalk.py) (Phase 2)
  uses.

## `DATA/*.rem` (OCaml persistent banks) — not parsed this session

37 `.rem` files (roots, nouns, indeclinables, participles, `mw_index.rem`,
`mw_exceptions.rem`, `guess_index.rem`, …) are OCaml `Marshal`-serialized
persistent data, not text — reading them requires the OCaml runtime and the
Heritage Platform's own type definitions. Out of scope for Phases 0–2; revisit
under roadmap Phase 4 (morphology databanks) only if the manual browser
download (@DO, current XML export) proves insufficient.

## `DATA/*.tsv` (frequency tables) — confirmed present, unparsed this session

`pada_freq.tsv` (526 KB), `pada_morph_freq.tsv` (1.6 MB), `pada_trans_freq.tsv`
(12 KB), `comp_freq.tsv` (312 KB), `comp_morph_freq.tsv` (755 KB),
`comp_trans_freq.tsv` (6 KB) — all present as claimed. Ingestion is roadmap
Phase 3, not bundled in this handoff.

## License

`XML/LICENSES/LGPLLR.*` confirms LGPLLR terms as expected (FINDINGS §47). Raw
mirror data stays gitignored (`HeadwordLists/heritage_mirror/`) pending the
Phase-0 @DECIDE (LGPLLR × CC BY-SA composition); only derived measurements
(this file, the coverage delta, the crosswalk TSV) are committed, each citing
its Heritage source per LGPLLR attribution terms.

_Dr. Mārcis Gasūns_
