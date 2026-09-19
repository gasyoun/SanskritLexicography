- **H4807 (OxAlpha `opencode/z-ai/glm-5.3-flash`) — Wisdomlib dictionary glosses vs csl-orig MW/AP90: borrowed vs own (census C6 sibling leg, shortlist cand.7).** New
  [provenance report](https://github.com/gasyoun/SanskritLexicography/blob/master/data/h4807_gloss_provenance/H4807_GLOSS_PROVENANCE_REPORT.md) +
  [share table](https://github.com/gasyoun/SanskritLexicography/blob/master/data/h4807_gloss_provenance/h4807_provenance_table.tsv):
  708,875 Sanskrit-dictionary gloss blocks over 255,348 definition pages (reconciles the L8 index exactly) — **90.0 % declare Cologne-dictionary provenance
  in wisdomlib's own per-gloss `Source :` attributions** (MW 25.0 %, Apte-1890-as-DDSA 10.0 %, other Cologne 55.0 %), 10.0 % own/other-external. Text-verification
  lane (canonical `sanskrit_util` keys, tiered headword lookup + `form_key` sense-segment match) proves **≥32.8 % verbatim-grade borrowing** in the MW/AP lane
  (MW 42.0 %, AP90 10.0 %); 123,362 D1 headword-misses + 43,347 D2 no-text-matches are the defect rows a reader-pack consumer must resolve before treating any
  wisdomlib gloss as a csl-orig equivalent. Builders committed:
  [h4807_msi_extract.py](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/h4807_msi_extract.py) (read-only scrape-store sweep on the MSI box),
  [h4807_ap90_glosses.py](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/h4807_ap90_glosses.py) (AP90 English TM from read-only csl-orig,
  selftest PASS),
  [h4807_gloss_provenance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/h4807_gloss_provenance.py) (matcher; SELFTEST/PASS =
  50/50 seeded sample revalidated in
  [h4807_sample50.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/h4807_gloss_provenance/h4807_sample50.tsv)). 20.6 MB match TSV not
  committed (bulk norm) — rebuild command in the report. csl-orig untouched; license mix BY 4.0 × BY-SA 4.0 ⇒ BY-SA 4.0 derivatives.
