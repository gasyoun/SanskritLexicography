# sanskrityatina-sch-cases — metadoc

_Created: 11-09-2026 · Last updated: 11-09-2026_

- **Purpose:** machine-readable record of the Sanskrityatina `04_Reverse/Experimental` SCH-experimental XML research cases — six accent/usage note collections (fiction, gedruckt, grade, pw-comparison, zu-betonen, zu-lesen), keyed via sanskrit-util (`from_slp1`/`slp1_form_key`) and carrying the `L`/`pc` page-column refs the sibling coding legend ([sanskrityatina-reverse-index](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina-reverse-index.meta.md)) lacks.
- **Provenance:** [H4533](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4533-OxAlpha_SanskritLexicography_h4475-sch-xml-cases-tsv_11.09.26.md) (OxAlpha, `zai-coding-plan/glm-5.3-flash`, 11-09-2026) · source `yadisk:Sanskrityatina/04_Reverse/Experimental/` (6 files, 6,294,178 B, UTF-16LE with BOM, sha256 per file in [sanskrityatina_sch_cases_provenance.json](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina_sch_cases_provenance.json)) · raw gitignored by mission (fetched via rclone WebDAV backend, no rclone binary config on this Windows box — see [H4473 access note](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/H4475_FORMAT_TABLE_10-09-2026.md)).
- **Format grammar:** [H4475_FORMAT_TABLE_10-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/H4475_FORMAT_TABLE_10-09-2026.md) SS4 (census that named this as the natural follow-up).
- **Rebuild:** `python3 ReverseDictionary/sanskrityatina/tools/h4533_build_sch_cases.py` (idempotent, byte-identical double-run verified; refetch command in `--help`; needs sibling clone `~/Documents/GitHub/sanskrit-util`).
- **Consumers:** none yet (registered in kosha as `sanskrityatina-sch-cases`, 11-09-2026).

## Schema

One row per `<H1>` case: `key1_slp1`, `key2_accented` (Schwarz's own numeric-accent transliteration -- e.g. `t2`=retroflex t, `s4`=palatal ś, `4`/`1` mark accent placement -- passed through **verbatim**, never re-derived or re-keyed), `iast` + `form_key` (both computed from `key1_slp1` via sanskrit-util), `case_class` (one of `fiction`/`gedruckt`/`grade`/`pw-comparison`/`zu-betonen`/`zu-lesen`, from the source filename), `L` (the source file's entry/line number), `pc` (page-column ref, e.g. `007-3`), `source_xml` (source filename).

`<body>` (the German gloss) and `<hom>` (homonym index, ~10% of rows) exist in the source and are read past during parsing but **not emitted** — outside the mission's TSV schema.

## The filename-count acceptance denominator is false on contact

Same class of finding as the sibling legend's "187992 headwords.txt ≠ a list of 187,992" (format table SS2): the six filenames encode a case count (`fiction-3147`, `zu betonen-83`, etc.) that the mission named as the acceptance denominator (sum 16,243). The **real** parsed total is **16,304** (+61), verified per file against a direct `<H1>`-occurrence grep, not just the parser's own tally:

| file | filename count | actual `<H1>` entries | note |
|---|---|---|---|
| fiction-3147 | 3,147 | 3,148 | +1, unexplained; open/close tag counts balance, not a parser artifact |
| gedruckt-86 | 86 | 86 | matches |
| grade-12427 | 12,427 | 12,427 | matches |
| pw-comparison-319 | 319 | 319 | matches |
| zu betonen-83 | 83 | **143** | the file unions two phrasings: 83× "zu betonen" + 60× "zu akzentuieren" (both German for "to be accented thus") — the filename names only the first |
| zu-lesen-181 | 181 | 181 | matches |

Full counts, per-file sha256 and these notes: [sanskrityatina_sch_cases_provenance.json](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina_sch_cases_provenance.json).

## Limitations

- `key2_accented` is Schwarz's internal accent notation, not IAST and not standard SLP1 — it is carried for provenance/cross-reference only; no transcoding function for it exists in sanskrit-util (unlike `key1_slp1`, which is genuine SLP1).
- One `key1_slp1` value (`ja|u`, zu-betonen file, `L=13803`, `pc=190-3`) carries a literal `|` — a source-data typo, not a parser bug (`sanskrit_util.from_slp1` maps unmapped characters to themselves rather than raising, so the glitch propagates unchanged into `iast`/`form_key` for that one row).
- `case_class` groups by source file, not by a controlled taxonomy — "fiction" vs "grade" (German *Grad* — degree/rank, likely a dictionary-comparison grading scale) vs "gedruckt" (printed) name different editorial review categories from the original 2013–2015 workshop; none is documented beyond the filename itself.

## Related

- [sanskrityatina-reverse-index metadoc](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina-reverse-index.meta.md) — the sibling coding-legend dataset (H4475); this dataset is its named backlog item 1.
- [kosha manifest row](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `sanskrityatina-sch-cases`.
- [sanskrit-util](https://github.com/gasyoun/sanskrit-util) — key pipeline authority (SLP1: `R`=ṇ, `N`=ṅ, `f`=ṛ).

_Revision history:_ v1 (11-09-2026) — initial landing, H4533.

_Dr. Mārcis Gasūns_
