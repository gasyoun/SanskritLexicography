# sanskrityatina-reverse-index — metadoc

_Created: 10-09-2026 · Last updated: 10-09-2026_

- **Purpose:** machine-readable record of the Sanskrityatina `04_Reverse` reverse-dictionary coding legend (187,992-headword Schwarz-based stock, coded `IEG/PD/BHS/MW/SCH`) — coding-class TSV + attested-example TSV keyed via sanskrit-util (`slp1_form_key`/`slp1_norm`/`norm`).
- **Provenance:** [H4475](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4475-OxAlpha_SanskritLexicography_sanskrityatina-reverse-index_09.09.26.md) (OxAlpha, `zai-coding-plan/glm-5.3-flash`, 10-09-2026) · source `yadisk:Sanskrityatina/04_Reverse/187992 headwords.txt` (1,706 B, ASCII CRLF, sha256 `c269e11f…`, full facts in [provenance.json](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/provenance.json)) · raw gitignored by mission.
- **Format table + folder census:** [H4475_FORMAT_TABLE_10-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/H4475_FORMAT_TABLE_10-09-2026.md).
- **Rebuild:** `python3 ReverseDictionary/sanskrityatina/tools/h4475_build_reverse_index.py` (idempotent; refetch command in `--help`; needs sibling clone `~/Documents/GitHub/sanskrit-util`).
- **Consumers:** none yet (registered in kosha as `sanskrityatina-reverse-index`, 10-09-2026).

## Ranked improvement backlog

1. **Land the SCH-experimental XML cases as a keyed TSV** (16,243 cases, UTF-16LE, csl-orig markup, **with `<L>/<pc>` page-column refs** — the refs the legend lacks). Highest value; mechanical once decoded (the format table §4 carries the grammar). Natural next unit.
2. **Recover the per-headword coded list** (the actual 187,992 rows) — candidates: `IAST-hyphenation_b7.xlsm` (13.6 MB), `Freq2011.zip`, the 384k-word index docx; all binary forensics, out of H4475 scope.
3. **NCC lists as a separate dataset** (`127980 non-duplicate` UTF-8 IAST 1/line, plus the 152,576 raw superset) — trivially parseable, but NOT reverse-index; needs its own manifest row (`sanskrityatina-ncc-headwords`).
4. **PD-tag cross-validation** — `aMSagaRa`'s `PD` tag is unprobeable (no `pd` dict in csl-orig v02; PD ≈ Petersburger Wörterbuch ≈ `pw`/`pwg`?) — settle the abbreviation mapping and complete the 3/3 tag audit.

## Limitations

- The legend is a SUMMARY (24 class lines: 1 stock + 23 subclasses), not the stock: per-headword codes do not exist here (backlog 2).
- `source_page_ref` column exists for schema continuity with a future SCH-XML join and is empty by construction.
- Subclass counts overlap (sum 197,019 > stock 187,992); the TSV transcribes, it does not de-overlap.

## Related

- [ReverseDictionary README](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md) — the 266,820-headword canonical master (different object; see format table §1 verdict).
- [kosha manifest row](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `sanskrityatina-reverse-index`.
- [sanskrit-util](https://github.com/gasyoun/sanskrit-util) — key pipeline authority (SLP1: `R`=ṇ, `N`=ṅ, `f`=ṛ).

_Revision history:_ v1 (10-09-2026) — initial landing, H4475.

_Dr. Mārcis Gasūns_
