# PWG scan pair census — Boethlingk_PWGScan.csv + _Devanagary.xlsx (H4536)

_Created: 11-09-2026 · Last updated: 11-09-2026_

Executor: OxAlpha (glm-5.3-flash, opencode) · Handoff: [H4536](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4536-OxAlpha_SanskritLexicography_pwg-devanagari-scan-pair_11.09.26.md) · class: data (awaiting different-session Verifier) · **derived-only** (MG ruling 07-09-2026 — raw pair stays on yadisk).

## 1 · Provenance

- Source: yadisk `Sanskrityatina/05_Sanskrit-Lexicon/1855-PWG/` — MG's own 2013 PWG scan-processing (files dated 2014-09-28 on the disk), fetched read-only via `rclone copy` into scratch; **no raw byte committed**.
- sha256: `a416996981dafdb1…` (Boethlingk_PWGScan.csv, 31 262 290 B) · `1f48edb1cf4804c7…` (Boethlingk_PWGScan_Devanagary.xlsx, 21 448 442 B).
- Anchor source: `csl-orig/v02/pwg/pwg.txt` (123 366 `<L>` records, **106 082 distinct k1** — exactly the PWG base layer of [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md)).

## 2 · What the pair is (census)

| File | Rows | Keying | Content |
|---|---:|---|---|
| `Boethlingk_PWGScan.csv` | 109 567 records / 93 936 distinct words | `;`-CSV, **SLP1(z) word in the URL column** (2013 header mislabel: header says `Word`, data puts the word in URL and the sense no in Word) | SLP1 headword + sense no + Numerik + `[L=N]` + German body (mixed-encoding bodies: stray `"`/cp1251 artefacts; ASCII key columns unaffected) |
| `Boethlingk_PWGScan_Devanagary.xlsx` | 109 375 data rows | sheet `Boethlingk_PWGScan_Devanagary`: col0 **devanagari**, col1 translit (IAST-ish), col2 sense no, col3 Numerik, col4 `[L=N]` | devanagari + translit + sense + page + per-sense body |

The two files are row-parallel passes over the same scan: **108 676 rows overlap by `[L=]` ref (99.2% of the smaller side)**. The CSV carries the German text, the xlsx the devanagari — the devanagari exists nowhere else in the estate (H4477 «star asset» row).

## 3 · Which anchor is faithful (the load-bearing finding)

The xlsx carries two candidate anchors into pwg.txt. Validated on a 4 000-row sample with an IAST→SLP1 normaliser (ś→S, ṣ→z, ṭ→w, ḍ→q, ṇ→R, digraphs bh→B, dh→D, …):

- `[L=N]` refs: word-confirm only **68.8%** — a noisy 2013 backfill (e.g. xlsx says aṃśabhāj→L=62410, but L=62410 is *aMSarUpA*; the true record is L=62407).
- **Numerik = pwg.txt `<pc>` page**: word-confirm **93.75%** exact page, **99.9%** when the Numerik page *ranges* (`1-0003 , 1-0004`) are walked — MG's scan pagination is reproduced verbatim in the Cologne file.

**Join policy (precision-first): a row joins only when page AND word both confirm** — pc page (ranges walked) with k1/k2 == translit, sense no picking `<h>` when a page holds several homs; `[L=]` kept as a self-confirming fallback (fires 0 times in the final run — pc+range subsumes it).

## 4 · Derived join table

[`RussianTranslation/pwg_ru/pwg_scan_devanagari_join.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/pwg_scan_devanagari_join.tsv) — `L · key1 (SLP1, lane spine) · devanagari · translit · sense · pc · anchor`; 109 279 rows + header. Builder: [`RussianTranslation/src/pilot/pwg_scan_devanagari_join.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/pwg_scan_devanagari_join.py) (`--emit` / `--check` parity gate, idempotent).

- **joined: 109 279 / 109 375 rows (99.91%)**, all page+word-confirmed; 107 742 distinct pwg records.
- **Coverage vs the pwg root list: 92 619 / 106 082 distinct key1 = 87.31%** (87.34% of records).
- **Unjoined residue: 96 rows (0.09%)** — 40 without usable Numerik/translit, 56 word/page mismatches that are scan-data defects (corrupted translit like `aृṇin` for *afRin*, `klṛpta` vs Cologne *klfpta*-class spelling drift). Honest residue: kept out of the TSV, counted here.

## 5 · Parity evidence

- Spot rows: xlsx aṃśaka senses 1/2/3 → L=9/10/11 (`<k1>aMSaka<h>1/2/3`, pc 1-0004) ✓; aṃśabhāj → L=62407 `aMSaBAj`, pc 5-0941 ✓ (both read back off the TSV).
- Mechanical self-check: 500 random TSV rows re-verified against pwg.txt header lines — **500 OK, 0 BAD**.
- Builder re-run with `--check`: **PARITY OK** (byte-identical re-derive).
- CSV z-SLP1 vs pwg.txt S-SLP1 ś-conventions differ by design (documented; join never compares raw spellings across sources).

## 6 · Registration

- Artifact row added to [docs/ARCHITECTURE_SanskritLexicography_PWG_DATA_LAYERS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_DATA_LAYERS.md) §4 (Data model — new/changed artifacts).
- No duplicate: no scan/devanagari layer existed in the doc, the lane, or kosha before this pass.

## 7 · Limits / next

- The 12.7% headword gap (13 463 key1) = entries the 2013 scan pass never reached or spelled past matching — a future diff list (`pwg root list minus join key1`) is one `comm` away if the lane wants a targeted re-scan queue.
- Numerik pages carry the 1855-75 volume-page grid as reproduced by Cologne; no attempt was made to map them to modern edition pagings.
