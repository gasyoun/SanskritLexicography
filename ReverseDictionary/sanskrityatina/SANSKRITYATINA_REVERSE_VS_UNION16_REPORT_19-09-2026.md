# Sanskrityatina reverse index vs union-16 headwords — coverage, overlap, Russian-school-only residue (H4800)

_Created: 19-09-2026 · Last updated: 17-10-2026_

Executor: OxAlpha (`opencode/z-ai/glm-5.3-flash`), drain worker on Claude/c4 · Handoff: [H4800](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4800-OxAlpha_SanskritLexicography_sanskrityatina-reverse-vs-union_14.09.26.md)

## 1. The per-headword stock was recovered first (metadoc backlog item 2 — resolved)

The H4475 census left the 187,992-headword per-headword stock as "not in `04_Reverse`". It is: **`.doc.pdf/reverse-index-full.doc`** (13,846,528 B, OLE2 Word 97, mtime 2014) — the FULL working reverse index in IAST, one entry per paragraph, `SOURCE_CODE\xa0headword` or a bare headword. Builder: [`tools/h4800_union_join.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/tools/h4800_union_join.py) (raw stays gitignored; refetch: `rclone copy 'yadisk:Sanskrityatina/04_Reverse/.doc.pdf/reverse-index-full.doc' raw/`).

- **266,709 entries extracted → 266,703 unique** (6 dupes); 134,797 carry a single-letter source code (M 57,176 · A 20,987 · H 12,549 · S 10,311 · G 7,551 · I 6,714 · B 6,851 · R 6,620 · N 3,542 · P 1,919 · V 577), 131,906 uncoded; 6,691 non-entry lines (binary/formatting) excluded.
- 266,703 vs the canonical 266,820 master ([`266820-reverse-Gasuns.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md)) — delta 117: this 2014 .doc is the master's working ancestor, NOT a new object.
- Legend anchors (H4475): `paryantīkṛta` ✓ · `paryavadāpayitar` ✓ · `aṃśagaṇa` **absent** (no spelling variant present) — the `IEG,PD` example postdates or bypasses this doc; recorded, not reconciled.
- The legend's 187,992 ("class 0, in ≥2 dictionaries") matches NEITHER column of this doc (codes are single-source letters) — the legend taxonomy and the doc's coding are different systems; both recorded verbatim, no forced reconciliation.
- ⚠ Transliteration hazard: a stratum of the doc writes intervocalic **`ḷ` for `l`** (`bāḷa`, `aheḷa` — MW has `bāla`); `form_key` preserves ḷ≠l, so these count as residue. The residue-by-code table shows this stratum is concentrated in specific source codes, so it is a coding-era artefact, not join noise.

## 2. Join to union-16 headwords (H4797, 417,184 keys)

Join key: `sanskrit-util form_key(headword_iast)` == `slp1_form_key(union slp1)`, pinned to **sanskrit-util 0.12.0 @ `7968fde`** (the H3975 medial-anusvāra-before-labial fold; recorded in the provenance `sanskrit_util` block). Output: [`sanskrityatina_reverse_union16_join.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina_reverse_union16_join.tsv); stock: [`sanskrityatina_reverse_full_stock.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/sanskrityatina_reverse_full_stock.tsv); all counts: [`h4800_provenance.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/sanskrityatina/h4800_provenance.json). Idempotence: two consecutive runs byte-identical (sha-checked). Rejoin without the raw doc: `python3 tools/h4800_union_join.py --stock-tsv sanskrityatina_reverse_full_stock.tsv`.

| Metric | Value |
|---|---|
| Stock headwords (unique) | 266,703 |
| **In the 16-dict union** | **244,195 (91.56%)** |
| **Residue — in NO Cologne dict of the union** | **22,508 (8.44%)** |
| Per-dict overlap (top) | MW 195,308 · PWK 148,425 · PWG 109,089 · AP 44,113 · VCP 42,976 |

## 3. The Russian-school-only residue (mission target)

22,508 union-absent forms, by source code: **A 12,124 · I 5,453 · P 1,435 · S 1,030 · R 1,026 · M 748 · B 240 · uncoded 168 · G 158 · N 63 · H 47 · V 16**.

- **Code M corroborated as Monier(-Williams)**: 57,176 M-coded, only 748 (1.3%) absent from the union — and MW alone covers 196K of the stock.
- **Code A is the Russian-school stratum**: 12,124 of its 20,987 (58%) exist in NO Cologne dictionary — the single largest genuinely-new corpus (Apte-unabsorbed and/or NCC-era additions; adjudicating A's identity is a follow-up, not guessed here).
- Code I (6,714 → 5,453 absent, 81%) behaves like a non-Cologne source too (IEG-shaped).
- Distinct from xwalk-a9 (H4714): that wired the ReverseDictionary 266,820 master consumer via the sch-cases slice; this unit keys the recovered full stock against the Cologne union and isolates the school-only slice.

## 3a. Rework after the independent verifier FAIL (17-10-2026)

The 20-09-2026 verifier (DeepSeek, independent) re-ran this builder against the canonical `sanskrit-util` and got **244,195 / 91.56 % / 22,508** — not the 243,985 / 91.48 % / 22,718 committed here. It also reproduced the committed TSV byte-for-byte by replaying the **pre-H3975** `form_key` (no medial-anusvāra-before-labial fold), which pinned the cause: the artifacts were keyed with a superseded library and no artifact recorded the version, so the report's own recompute instruction diverged.

Rework (this revision) fixes exactly that, without touching the extraction:

- **Version pin.** `h4800_provenance.json` now carries a `sanskrit_util` block (`version 0.12.0`, `commit 7968fde…`, local path) and an `extraction_mode` field; the join re-ran against that pinned library.
- **Artifacts refreshed** to the reproducible numbers above. Diff against the superseded commit: **1,707 form_key cells**, **210 `in_union` flips** (all in one direction — the fold rescues 210 forms), 1,455 `union_dicts` changes, 3,003 rows touched in total.
- **Rejoin path.** The raw `.doc` is an off-git yadisk asset and the WebDAV host answered `503` throughout the rework window, so the builder gained `--stock-tsv`: the join stage re-executes from the committed extraction (whose 266,703 headwords the verifier independently re-derived), re-keys and re-looks-up without the doc. Extraction counts are left `null` rather than copied forward. Pipeline still: extract (needs the doc) → join (reproducible without it).
- **Not re-proven here:** extraction itself. It stands on the 20-09-2026 verifier's independent OLE2 re-derivation (doc `sha256=79ae7a55…b284826`, WordDocument 13,555,774 B, 266,709 / 6,691 / 6 / 266,703) and is unchanged by this revision.

## 4. Verified limits

- Extraction is charset-filtered decode of the UTF-16LE WordDocument stream, NOT a piece-table Word parse: 6,691 excluded lines were inspected as binary/formatting; anchor + master-count cross-checks above bound the error.
- Source-code letters are carried verbatim; semantics unadjudicated (see §3 hypotheses, evidence-cited, not settled).
- The `ḷ`-stratum (§1) inflates the residue honestly; a follow-up `ḷ→l` sensitivity pass would size it exactly (not in this unit's budget).

_Dr. Mārcis Gasūns (draft prepared with a little help from my Chinese friend)_
