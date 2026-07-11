# Markup-tag frequency census — csl-orig/v02, all 44 dictionaries

_Created: 11-07-2026 · Last updated: 11-07-2026_

**What this is.** The first computed row of the statistics-to-compute table in
[DATA_LAYERS_CENSUS.md §3](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md):
a per-dictionary frequency census of every markup tag in the Cologne source texts,
normalized per 1,000 entries, with under-marking / inconsistency verdicts.
Handoff: [H683](https://github.com/gasyoun/Uprava/blob/main/handoffs/H683-Fable_SanskritLexicography_markup-tag-census-43-dicts_11.07.26.md)
(Lane B, Fable sprint). Computed 11-07-2026 by Fable 5 (`claude-fable-5`).

## Method

- Source: local [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) `v02/` at
  commit `78cbb257` (2026-07-04). One main text file `<code>/<code>.txt` per
  dictionary; 44 found (the census-row estimate said 43 — the real count is 44).
  `etymology_stats/` is not a dictionary and is skipped.
- Script: [markup_tag_census.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.py)
  (committed beside the output). Counts every *opening* angle-bracket tag
  `<tag ...>` (closing `</tag>` forms are not counted, so one logical use counts
  once) plus the Cologne brace markers `{#...#}` (SLP1 Sanskrit), `{%...%}`
  (italics), `{@...@}` (bold), `{~...~}`, `{!...!}`, `{|...|}` as pseudo-tags.
- Entries = lines starting with `<L>` (the v02 record marker). Cross-check: this
  equals the `<LEND>` count in **all 44** dictionaries. (BEN and IEG additionally
  carry 6 and 3 *inline* `<L>` occurrences mid-line — stray cross-reference text,
  not extra records.)
- Rates are per 1,000 entries. Input BOMs are stripped transparently
  (`utf-8-sig`); output is UTF-8, no BOM, LF.
- Output: [markup_tag_census.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv)
  — long format `dict · entries · tag · count · per_1000_entries`, 671 rows.

**Headline totals:** 44 dictionaries · 1,496,157 entries · 17,476,964 tag hits ·
96 distinct tags org-wide.

## Core-tag rates per 1,000 entries

Structural record tags (`<L>`, `<LEND>`, `<pc>`, `<k1>`, `<k2>`, `<h>`, `<e>`,
`<info>`) sit at ~1000/1000 by construction and are omitted here; the TSV has
everything. The seven columns below are the semantic/display markers the census
question asked about.

| dict | entries | `<s>` | `<ls>` | `<ab>` | `<lex>` | `{#...#}` | `{%...%}` | `{@...@}` | distinct tags |
|---|---|---|---|---|---|---|---|---|---|
| abch | 1,965 | 5358.8 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| acc | 49,833 | 0 | 0 | 0 | 0 | 1001.7 | 27.2 | 0 | 14 |
| acph | 163 | 6233.1 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| acsj | 240 | 4250.0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| ae | 11,359 | 6413.9 | 100.5 | 3146.9 | 2014.2 | 0 | 0.2 | 2988.6 | 13 |
| ap | 90,843 | 0 | 751.6 | 361.7 | 332.3 | 2588.2 | 405.2 | 170.8 | 20 |
| ap90 | 34,882 | 0 | 1258.3 | 1320.6 | 0 | 3853.0 | 898.6 | 2079.4 | 13 |
| armh | 7,907 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 |
| ben | 17,310 | 0 | 2844.3 | 3947.3 | 0 | 1278.8 | 3321.0 | 2214.9 | 12 |
| bhs | 17,839 | 0 | 2714.2 | 2616.5 | 856.9 | 0 | 1399.3 | 1923.8 | 24 |
| bop | 8,961 | 0 | 0 | 0 | 0 | 4433.8 | 2598.5 | 0 | 14 |
| bor | 24,609 | 0 | 21.4 | 0 | 0 | 3632.9 | 959.5 | 1017.6 | 10 |
| bur | 19,776 | 0 | 0 | 3310.1 | 0 | 1004.0 | 3653.8 | 5.2 | 14 |
| cae | 40,069 | 0 | 0 | 638.0 | 1121.2 | 1469.7 | 0 | 0 | 13 |
| ccs | 30,010 | 0 | 0 | 0 | 0 | 1553.7 | 1402.5 | 0 | 10 |
| fri | 8,155 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| gra | 12,785 | 0 | 183.1 | 3576.5 | 0 | 0 | 1874.5 | 2008.9 | 21 |
| gst | 6,780 | 0 | 0 | 0 | 0 | 7362.4 | 1025.5 | 0.3 | 15 |
| ieg | 7,932 | 0 | 1436.0 | 521.6 | 0 | 2.7 | 2287.7 | 0 | 13 |
| inm | 12,647 | 0 | 0 | 0 | 0 | 0 | 6159.5 | 4276.4 | 15 |
| krm | 2,061 | 36300.8 | 0 | 0 | 0 | 0 | 66.5 | 1004.9 | 19 |
| lan | 4,944 | 0 | 1195.8 | 2673.1 | 0 | 0 | 2654.1 | 3089.2 | 14 |
| lrv | 53,441 | 0 | 311.6 | 0 | 0 | 1351.7 | 831.4 | 0 | 11 |
| mci | 2,643 | 0 | 0 | 0 | 0 | 3.8 | 12374.2 | 2572.5 | 19 |
| md | 20,749 | 0 | 2.8 | 2263.1 | 2704.9 | 1022.7 | 1419.2 | 2185.5 | 22 |
| mw | 286,525 | 1223.7 | 1119.7 | 680.2 | 704.8 | 0 | 0 | 0 | 32 |
| mw72 | 55,390 | 0.02 | 0 | 0 | 0 | 468.7 | 4307.0 | 0.02 | 17 |
| mwe | 32,378 | 0 | 0 | 0 | 0 | 4875.6 | 1963.9 | 0 | 10 |
| nmmb | 506 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| pe | 8,799 | 0 | 0 | 0 | 0 | 3.0 | 390.4 | 0.2 | 16 |
| pgn | 485 | 0 | 0 | 0 | 0 | 1381.4 | 7509.3 | 0 | 17 |
| pui | 17,512 | 0 | 0 | 0 | 0 | 0.2 | 1335.9 | 0.6 | 15 |
| pw | 170,556 | 0 | 577.4 | 632.1 | 1042.4 | 1575.5 | 1246.3 | 0 | 26 |
| pwg | 123,366 | 0 | 6499.3 | 1465.0 | 1060.8 | 5023.0 | 1562.5 | 0 | 41 |
| pwkvn | 24,976 | 0 | 705.8 | 248.0 | 476.1 | 1240.3 | 474.6 | 0 | 16 |
| sch | 29,125 | 0 | 1065.8 | 0.07 | 0 | 0 | 1406.8 | 0 | 10 |
| shs | 47,326 | 0.02 | 0 | 0 | 0 | 4416.2 | 0.2 | 0 | 9 |
| skd | 42,531 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 |
| snp | 453 | 0 | 0 | 0 | 0 | 0 | 2715.2 | 0 | 12 |
| stc | 24,574 | 0 | 0 | 3271.2 | 0 | 0 | 1845.2 | 1027.0 | 15 |
| vcp | 50,135 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 22 |
| vei | 3,834 | 0 | 0 | 0 | 0 | 0 | 4488.3 | 2417.3 | 18 |
| wil | 44,577 | 0 | 0.1 | 1520.9 | 1189.6 | 4517.2 | 218.8 | 0 | 18 |
| yat | 45,206 | 0 | 0 | 0 | 0 | 2056.8 | 1243.4 | 0 | 12 |

## Verdicts

### Richly structured (machine-usable semantic markup)

**PWG** is the org's markup maximum — 41 distinct tags, `<ls>` at 6,499/1,000
(6.5 source citations per entry), plus full `<ab>`/`<lex>`/brace coverage.
**MW** (32 tags) is the angle-tag counterpart: heavy `<s>`/`<ls>`/`<ab>`/`<lex>`
and **zero brace markup** — MW's Sanskrit lives in `<s>`, everyone else's in
`{#...#}`. **PW**, **BHS** (24 tags incl. etymological `<bot>`/`<toch>`/`<gk>`),
**MD**, **AP**, **AP90**, **BEN**, **GRA**, **AE** follow. These are the dicts
where citation extraction, abbreviation expansion, and grammar harvesting work
today (the csl-atlas `<ls>` citation graph, E38, draws exactly from this tier).

### Display-only markup (under-structured, not under-marked)

**ACC, MWE, SHS, YAT, CCS, BOP, GST, MW72, INM, MCI, VEI, SNP, PGN, PUI, PE,
BOR, LRV** carry brace markup (`{#...#}` SLP1 and/or `{%...%}` italics) but no
— or trace-only — `<ls>`/`<ab>`/`<lex>` structure. The text renders, but
sources, abbreviations, and grammar are not machine-addressable.
**MW72 is the starkest case:** 55,390 entries and essentially one semantic
angle tag total, next to its sibling MW's full structure — the 1872 edition is
a rendering surface, not a database.

### Plain text (under-marked outright)

**ARMH** (7,907 entries, 6 tags — all structural), **FRI** (8,155, 7),
**NMMB** (506, 5 — the org minimum). Zero semantic or display markup of any
kind. Any future use of these three beyond full-text search requires a markup
pass first.

### Sanskrit–Sanskrit by construction (expected zeros — not a discovery)

**SKD** and **VCP** carry ~0 Western markup tags by design (standing baseline,
pre-registered in the handoff): no `<s>`/`<ls>`/`<ab>` because the entire body
is Sanskrit. Their 20–22 distinct tags are their own structural set — the
`<C1>`–`<C12>` column/section markers appear only here.

### `<s>`-only specialist indexes

**ABCH, ACPH, ACSJ** mark Sanskrit (`<s>` at 4,250–6,233/1,000) and nothing
else; **KRM** is the `<s>` density record — 36,301/1,000, ~36 tagged Sanskrit
strings per entry (it is a kṛdanta root-form index, so nearly every token is
Sanskrit).

### Inconsistently tagged (trace tags — abandoned starts or strays)

Tags applied at a rate under 1 per 1,000 entries are noise, not structure.
The full list is computable from the TSV; the flagrant cases:

- **SCH** `<ab>` ×2 in 29,125 entries — an abbreviation-tagging start that
  never happened; SCH otherwise has real `<ls>` (1,066/1,000).
- **MW72** `<s>` ×1 and `{@...@}` ×1 in 55,390 entries.
- **SHS** `<s>` ×1 in 47,326; `{%...%}` ×7.
- **WIL** `<ls>` ×6 in 44,577 — WIL has genuine `<ab>`/`<lex>` (1,521/1,190
  per 1,000) but its source citations are untagged.
- **PUI/PE/GST** `{#...#}` or `{@...@}` at 0.2–3.8/1,000 — brace residue.
- Cross-dict: rare-language tags (`<arab>`, `<heb>`, `<rus>`, `<ocs>`,
  `<mong>`, `<toch>`, `<zen>`) appear at trace rates in PW/PWG/BHS/MD — these
  are *legitimately rare* (loan-word etymologies), not inconsistency.

### Data-quality footnotes

- `<L>` = `<LEND>` in all 44 dicts (record integrity clean). BEN and IEG have
  6 and 3 inline `<L>` strays inside entry bodies worth a one-off look.
- MW's `<i>` (×197), `<chg>`/`<old>`/`<new>` (×39/35) are editorial-apparatus
  tags at trace rates — apparatus, not under-marking.

_Dr. Mārcis Gasūns_
