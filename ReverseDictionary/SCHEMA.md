# Reverse Dictionary — dataset schema

_Created: 07-07-2026 · Last updated: 07-07-2026_

Documents the column semantics, source-code table, and encoding audit for the canonical
master list `.doc.pdf/266820-reverse-Gasuns.txt` (declared canonical in
[`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CHANGELOG.md)).
Written per [`ACL_DH_COMPATIBILITY_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md)
§4 step 3 ([H270](https://github.com/gasyoun/Uprava/blob/main/handoffs/H270-Sonnet_SanskritLexicography_reverse-dict-publication-prep_07.07.26.md)).
This documents the file's *actual* format, verified directly against the bytes, not a
proposed or aspirational one — a bare TSV, honestly, per the DH-standards analysis's own
recommendation not to force a premature TEI Lex-0 conversion.

## File format

- **Encoding:** UTF-8 with a leading BOM (`EF BB BF`) — verified with a raw byte read.
  Preserve this BOM in any tool that resaves the file (repo rule: never silently
  add/strip a BOM — see
  [`../CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md)).
- **Line ending:** CRLF (`\r\n`) throughout, except the final line, which has no
  trailing line terminator at all.
- **Row count:** 266,820 data lines (266,819 CRLF-terminated + 1 unterminated final
  line — this is why some notes elsewhere say "266,819 lines").
- **Delimiter:** one horizontal tab (`\t`) per line, exactly two columns.
- **Normalization:** every line is already Unicode NFC (checked with Python
  `unicodedata.normalize('NFC', line) == line` for all 266,820 lines — zero
  exceptions).
- **Duplicates:** zero exact-duplicate lines; zero duplicate *words* even ignoring the
  source-code column — every headword string is unique across the whole file.

## Columns

| # | Name | Content |
|---|---|---|
| 1 | `source_code` | A single letter (or empty) marking which dictionary this headword's *non-default* attestation comes from — see table below. Empty means "found in PWK" (the implicit default source, never itself marked — see "Source priority" in [`README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md)). |
| 2 | `headword` | The Sanskrit word in IAST transliteration, normalized to stem form (nominal endings stripped to the bare prātipadika; verbs cited as roots with MW's prefixes attached — see README "Methodology"). |

## Source-code → bibliography-key table

The bibliography ([`Словари-источники.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D0%B8-%D0%B8%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%D0%B8.mdx))
declares 30 letter codes (a 26-letter alphabet plus `Ā/Ö/Ś/Ü/ß` inserted to fit all 30
sources without reusing a letter). **Only 12 of those 30 codes actually appear** as a
marked source in the canonical file — checked directly by scanning the distinct values
of column 1 across all 266,820 lines:

| Code in file | Bibliography letter | Bib. key | Source | Lines | Copyright tier (per [`ACL_DH_COMPATIBILITY_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md) §3.1) |
|---|---|---|---|--:|---|
| *(empty)* | K | `pwk` | Böhtlingk & Roth, *Sanskrit-Wörterbuch in kürzerer Fassung* (PWK), merged with Schmidt's *Nachträge* — the implicit default/unmarked source | 131,916 | Public domain |
| `M` | M | `mwe` | Monier-Williams, *A Sanskrit–English Dictionary* (1899) | 57,177 | Public domain |
| `A` | Ā | `apt` | Apte, *The Practical Sanskrit-English Dictionary* (1957–59 rev. ed.) | 21,081 | Likely PD, verify (base 1890 ed. is PD; 1957–59 revision's own status is the open question) |
| `H` | H | `bhs` | Edgerton, *Buddhist Hybrid Sanskrit Grammar and Dictionary* (1953) | 12,552 | **In copyright** |
| `S` | S | `sch` | Schmidt, *Nachträge zum Sanskrit-Wörterbuch* (1928) | 10,311 | Public domain |
| `G` | G | `pwg` | Böhtlingk & Roth, *Sanskrit-Wörterbuch* (large PWG, 1855–75) | 7,551 | Public domain |
| `B` | B | `bur` | Burnouf, *Dictionnaire classique sanscrit-français* (1866) | 6,851 | Public domain |
| `I` | I | `pui` | Dīkshitar, *The Purana Index* (1951–55) | 6,714 | Likely PD, verify (author d. 1953 → India life+60 expired 2014) |
| `R` | R | `shs` | *Shabda-Sagara Sanskrit-English Dictionary* | 6,620 | Public domain |
| `N` | N | `inm` | Sørensen, *Index to the Names in the Mahabharata* (1904–14) | 3,551 | Public domain |
| `P` | P | `pex` | Vettam Mani, *Puranic Encyclopaedia* (1979, English) | 1,919 | **In copyright** |
| `V` | V | `vac` | Tarkavācaspati, *Vachaspatyam* (1969–70 reprint of 1873–84 orig.) | 577 | Public domain |

**Note on the `A`/`Ā` mismatch:** the bibliography table's letter for Apte is `Ā` (A with
macron, since plain `A` was needed for a different position in the 30-symbol scheme as
originally laid out); the actual corpus uses plain ASCII `A` (`U+0041`) for every Apte
row — verified byte-for-byte (`hex(ord(c))` for every distinct code in the file). The
macron was evidently dropped when the single-letter marker was typed into the working
file, since it's a bare symbol, not real Sanskrit text needing diacritics. The mapping
above is by **position in the bibliography list**, not by literal character match, and
is unambiguous: none of the 12 codes actually used in the file collide with each other
under this reading.

**The other 18 declared sources** (`C/cap`, `D/mcd`, `E/vei`, `F/stc`, `J/snp`, `L/acc`,
`O/puj`, `Q/kch`, `Ś/skd`, `ß/bop`, `T/tur`, `Ü/gst`, `U/hue`, `W/wil`, `X/mci`, `Y/yat`,
`Z/myl`) **never appear as a marked source-code** in the canonical file. This does not
mean they were unused in compiling the dictionary — the preface describes all 30 as
consulted — it means every headword uniquely or first attested in one of those 18 was
apparently absorbed under a higher-priority marked/default code rather than tagged with
its own letter, or simply contributed no headword that needed disambiguating from a
higher-priority source. This single-letter-per-line scheme cannot by itself answer
"which of the 30 sources does this headword ultimately come from" for those 18 — see the
caveat in the licensing-cost measurement note (mirrored to
[`GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)).

## Why not TEI Lex-0

[TEI Lex-0](https://lex-0.org/) is the DH-standard lexicographic markup, but it's
designed for full dictionary *entries* (`<form>`/`<sense>`/`<gramGrp>`). This file has no
senses, no grammar tags, no glosses — it is a bare headword + attribution list. Wrapping
two flat TSV columns in `<entry><form>` tags would add structure without adding
information, and there is no current consumer that needs it. A documented TSV schema
(this file) is the honest, sufficient standard for what this dataset actually is; TEI
Lex-0 remains a legitimate *later* interoperability layer if/when this data is joined
with a Cologne TEI dictionary that does carry senses.

---

_Dr. Mārcis Gasūns_
