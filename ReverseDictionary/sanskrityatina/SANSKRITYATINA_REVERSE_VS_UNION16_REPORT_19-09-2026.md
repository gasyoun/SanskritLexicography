# Sanskrityatina reverse index vs union-16 headwords — coverage, overlap, Russian-school-only residue (H4800)

_Created: 19-09-2026 · Last updated: 19-09-2026_

Executor: OxAlpha (`opencode/z-ai/glm-5.3-flash`), drain worker on Claude/c4 · Handoff: [H4800](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4800-OxAlpha_SanskritLexicography_sanskrityatina-reverse-vs-union_14.09.26.md)

## 1. The per-headword stock was recovered first (metadoc backlog item 2 — resolved)

The H4475 census left the 187,992-headword per-headword stock as "not in `04_Reverse`". It is: **`.doc.pdf/reverse-index-full.doc`** (13,846,528 B, OLE2 Word 97, mtime 2014) — the FULL working reverse index in IAST, one entry per paragraph, `SOURCE_CODE\xa0headword` or a bare headword. Builder: [`tools/h4800_union_join.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/tools/h4800_union_join.py) (raw stays gitignored; refetch: `rclone copy 'yadisk:Sanskrityatina/04_Reverse/.doc.pdf/reverse-index-full.doc' raw/`).

- **266,709 entries extracted → 266,703 unique** (6 dupes); 134,797 carry a single-letter source code (M 57,176 · A 20,987 · H 12,549 · S 10,311 · G 7,551 · I 6,714 · B 6,851 · R 6,620 · N 3,542 · P 1,919 · V 577), 131,906 uncoded; 6,691 non-entry lines (binary/formatting) excluded.
- 266,703 vs the canonical 266,820 master ([`266820-reverse-Gasuns.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md)) — delta 117: this 2014 .doc is the master's working ancestor, NOT a new object.
- Legend anchors (H4475): `paryantīkṛta` ✓ · `paryavadāpayitar` ✓ · `aṃśagaṇa` **absent** (no spelling variant present) — the `IEG,PD` example postdates or bypasses this doc; recorded, not reconciled.
- The legend's 187,992 ("class 0, in ≥2 dictionaries") matches NEITHER column of this doc (codes are single-source letters) — the legend taxonomy and the doc's coding are different systems; both recorded verbatim, no forced reconciliation.
- ⚠ Transliteration hazard: a stratum of the doc writes intervocalic **`ḷ` for `l`** (`bāḷa`, `aheḷa` — MW has `bāla`); `form_key` preserves ḷ≠l, so these count as residue. The residue-by-code table shows this stratum is concentrated in specific source codes, so it is a coding-era artefact, not join noise.

## 2. Join to union-16 headwords (H4797, 417,184 keys)

Join key: `sanskrit-util form_key(headword_iast)` == `slp1_form_key(union slp1)`. Output: [`sanskrityatina_reverse_union16_join.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina_reverse_union16_join.tsv); stock: [`sanskrityatina_reverse_full_stock.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina_reverse_full_stock.tsv); all counts: [`h4800_provenance.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/h4800_provenance.json). Idempotence: two consecutive runs byte-identical (sha-checked).

| Metric | Value |
|---|---|
| Stock headwords (unique) | 266,703 |
| **In the 16-dict union** | **243,985 (91.48%)** |
| **Residue — in NO Cologne dict of the union** | **22,718 (8.52%)** |
| Per-dict overlap (top) | MW 196,281 · PWK 147,381 · PWG 108,392 · AP 43,798 · VCP 43,156 |

## 3. The Russian-school-only residue (mission target)

22,718 union-absent forms, by source code: **A 12,171 · I 5,464 · P 1,438 · R 1,170 · S 1,032 · M 749 · B 240 · uncoded 170 · G 158 · N 63 · H 47 · V 16**.

- **Code M corroborated as Monier(-Williams)**: 57,176 M-coded, only 749 (1.3%) absent from the union — and MW alone covers 196K of the stock.
- **Code A is the Russian-school stratum**: 12,171 of its 20,987 (58%) exist in NO Cologne dictionary — the single largest genuinely-new corpus (Apte-unabsorbed and/or NCC-era additions; adjudicating A's identity is a follow-up, not guessed here).
- Code I (6,714 → 5,464 absent, 81%) behaves like a non-Cologne source too (IEG-shaped).
- Distinct from xwalk-a9 (H4714): that wired the ReverseDictionary 266,820 master consumer via the sch-cases slice; this unit keys the recovered full stock against the Cologne union and isolates the school-only slice.

## 4. Verified limits

- Extraction is charset-filtered decode of the UTF-16LE WordDocument stream, NOT a piece-table Word parse: 6,691 excluded lines were inspected as binary/formatting; anchor + master-count cross-checks above bound the error.
- Source-code letters are carried verbatim; semantics unadjudicated (see §3 hypotheses, evidence-cited, not settled).
- The `ḷ`-stratum (§1) inflates the residue honestly; a follow-up `ḷ→l` sensitivity pass would size it exactly (not in this unit's budget).

_Dr. Mārcis Gasūns (draft prepared with a little help from my Chinese friend)_
