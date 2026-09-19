# sanskrityatina-reverse-index — metadoc

_Created: 10-09-2026 · Last updated: 19-09-2026_

- **Purpose:** machine-readable record of the Sanskrityatina `04_Reverse` reverse-dictionary coding legend (187,992-headword Schwarz-based stock, coded `IEG/PD/BHS/MW/SCH`) — coding-class TSV + attested-example TSV keyed via sanskrit-util (`slp1_form_key`/`slp1_norm`/`norm`).
- **Provenance:** [H4475](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4475-OxAlpha_SanskritLexicography_sanskrityatina-reverse-index_09.09.26.md) (OxAlpha, `zai-coding-plan/glm-5.3-flash`, 10-09-2026) · source `yadisk:Sanskrityatina/04_Reverse/187992 headwords.txt` (1,706 B, ASCII CRLF, sha256 `c269e11f…`, full facts in [provenance.json](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/provenance.json)) · raw gitignored by mission.
- **Format table + folder census:** [H4475_FORMAT_TABLE_10-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/H4475_FORMAT_TABLE_10-09-2026.md).
- **Rebuild:** `python3 ReverseDictionary/sanskrityatina/tools/h4475_build_reverse_index.py` (idempotent; refetch command in `--help`; needs sibling clone `~/Documents/GitHub/sanskrit-util`).
- **Consumers:** H4714 (15-09-2026) — class-level consumer in the ReverseDictionary master-list complement join (stock 187,992 = legend context; the per-headword slice came from the sibling `sanskrityatina-sch-cases`); registered in kosha as `sanskrityatina-reverse-index`, 10-09-2026. H4800 (19-09-2026, primary lane) — the recovered per-headword coded stock (266,703, `reverse-index-full.doc`) joined to the 16-dict union: 91.48 % coverage, 22,718 Russian-school-only residue. H4800 (19-09-2026, complementary lane) — the xlsm hyphenation master word list (252,134 tagged words, a different 2014 artifact) joined by the same form_key pipeline: 81.37 % match, 46,985 residue ([tools/h4800_reverse_stock_vs_union16.py](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/tools/h4800_reverse_stock_vs_union16.py)).

## Ranked improvement backlog

1. **Land the SCH-experimental XML cases as a keyed TSV** (16,243 cases, UTF-16LE, csl-orig markup, **with `<L>/<pc>` page-column refs** — the refs the legend lacks). Highest value; mechanical once decoded (the format table §4 carries the grammar). Natural next unit.
2. **Recover the per-headword coded list** — **DONE 19-09-2026 (H4800, dual-run reconciled):** the carrier was none of the census candidates but `.doc.pdf/reverse-index-full.doc` (266,703 unique IAST headwords, 134,797 single-letter source codes, the 266,820 master's 2014 ancestor); landed as [`sanskrityatina_reverse_full_stock.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina_reverse_full_stock.tsv) and joined to union-16 (91.48% coverage, 22,718 Russian-school-only residue) — [report](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/SANSKRITYATINA_REVERSE_VS_UNION16_REPORT_19-09-2026.md). Complementary lane (same handoff, second session): census candidate `IAST-hyphenation_b7.xlsm` decoded — it is a DIFFERENT 2014 workshop artifact, the hyphenation master word list (252,134 IAST words, one-letter source tags, no class codes) — landed as its own keyed join [`sanskrityatina_reverse_stock_union16_join.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina_reverse_stock_union16_join.tsv) (81.37 % match, 46,985 residue); raw xlsm stays gitignored under `raw/`.
3. **NCC lists as a separate dataset** (`127980 non-duplicate` UTF-8 IAST 1/line, plus the 152,576 raw superset) — trivially parseable, but NOT reverse-index; needs its own manifest row (`sanskrityatina-ncc-headwords`).
4. **PD-tag cross-validation** — `aMSagaRa`'s `PD` tag is unprobeable (no `pd` dict in csl-orig v02; PD ≈ Petersburger Wörterbuch ≈ `pw`/`pwg`?) — settle the abbreviation mapping and complete the 3/3 tag audit.

**Update 11-09-2026 (H4533):** backlog item 1 is DONE — landed as its own dataset, [`sanskrityatina-sch-cases`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina-sch-cases.meta.md) (16,304 rows, not the census's 16,243 — see that metadoc for the delta).

## Limitations

- The legend is a SUMMARY (24 class lines: 1 stock + 23 subclasses), not the stock: per-headword codes do not exist here (backlog 2).
- `source_page_ref` column exists for schema continuity with a future SCH-XML join and is empty by construction.
- Subclass counts overlap (sum 197,019 > stock 187,992); the TSV transcribes, it does not de-overlap.

## Related

- [ReverseDictionary README](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md) — the 266,820-headword canonical master (different object; see format table §1 verdict).
- [kosha manifest row](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `sanskrityatina-reverse-index`.
- [sanskrit-util](https://github.com/gasyoun/sanskrit-util) — key pipeline authority (SLP1: `R`=ṇ, `N`=ṅ, `f`=ṛ).
- [sanskrityatina-sch-cases metadoc](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina-sch-cases.meta.md) — the SCH-experimental XML cases dataset (H4533), backlog item 1 above.

_Revision history:_ v1 (10-09-2026) — initial landing, H4475.
_Revision history v2 (11-09-2026):_ backlog item 1 landed as `sanskrityatina-sch-cases`, H4533.
_Revision history v3 (15-09-2026):_ first consumer — H4714 master-list complement join (class-level; row-level slice via the sibling sch-cases dataset).
_Revision history v4 (19-09-2026):_ H4800 dual-run — primary lane recovered the full per-headword stock from `reverse-index-full.doc` (266,703 rows, 91.48 % union-16 coverage, 22,718 Russian-school-only residue), joined and registered in kosha as `sanskrityatina-reverse-vs-union16`; complementary lane decoded the census-candidate xlsm into a second keyed join (252,134-word tagged master list, 81.37 % / 46,985 residue).

_Dr. Mārcis Gasūns_
