# PWG_MW99_ENRICHMENT — pwg (Böhtlingk-Roth great PW, 1855–1875) vs MW99 annexure-vs-main

_Created: 17-09-2026 · Last updated: 17-09-2026_

H5058 (epic E009, child of H4360) — **the other half of the PW/PWG-influence question.** H5056/H5059 measured how PW-**Nachträge** vocabulary concentrates in the MW99 annexure (7.79–7.91×) and how native kośas deplete (0.23×–0.61×); this measurement completes the pair with the great PW **core** itself: pwg headword enrichment in the MW99 annexure vs main, same locked conventions and years as the Nachtraege metric. Measured with the generic stdlib builder [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) (H5056) under conventions C1–C4 of [`ENRICHMENT_METRICS_REGISTRY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/ENRICHMENT_METRICS_REGISTRY.md) §0 (C5 sup-layer headword rule not exercised — `pwg` is a plain `CODE` k1 set). csl-orig is read-only input throughout.

## 1 · Source and target, publication years from the TEI headers

Years read from the digitizations' own TEI `<date>` elements (H5059 precedent — never from memory): [`csl-orig/v02/pwg/pwgheader.xml`](https://github.com/csl-orig) `<date>1855-1875</date>`; [`csl-orig/v02/mw/mwheader.xml`](https://github.com/csl-orig) `<date>1899</date>`.

| code | work (TEI title) | author(s) | publication year(s) |
|---|---|---|---|
| pwg | Böhtlingk and Roth's Sanskrit Wörterbuch (the great Petersburg Wörterbuch, 7 vols) | Otto von Böhtlingk · Rudolph von Roth | **1855–1875** |
| mw | (target) Monier-Williams Sanskrit-English Dictionary, 1899 ed. | Monier Monier-Williams | **1899** (annexure = Supplemental-Word appendix, `<info n="sup"/>`) |

## 2 · The measurement (MW99 target: 194,083 k1 = 6,067 annexure + 188,016 main)

Target anchors reproduce the H5056/H5059 runs exactly (delta 0). Shares are of the **target** sets (C4): annexure share = |S ∩ annexure| / 6,067; main share = |S ∩ main| / 188,016.

| source | year | n(S) | in annexure | annexure share | in main | main share | enrichment |
|---|---|--:|--:|--:|--:|--:|--:|
| pwg | 1855–1875 | 106,082 | 1,001 | **16.5 %** | 93,778 | **49.9 %** | **0.33×** |

Full-precision enrichment 0.330791. SxD coverage row (share of pwg k1 in each dictionary): mw72 **33.0 %** (35,000) · pw **93.8 %** (99,455) · bhs 4.5 % (4,780) · mw **89.3 %** (94,779) · pwkvn 3.8 % (4,041). Machine-readable TSV: [`pwg_mw99_enrichment_17-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/pwg_mw99_enrichment_17-09-2026.tsv) + full-precision `.json` beside it; row appended to [`enrichment_metrics_registry_17-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_metrics_registry_17-09-2026.tsv)/`.json` per registry §3 (registry matrix regenerated with the pwg row, all four published rows byte-identical).

## 3 · Reading — the core depletes where the supplements enrich (set-overlap signature, not causation — C4 caveat)

1. **pwg DEPLETES at 0.33×** — (1,001/6,067) / (93,778/188,016) ≈ 0.331. Only Śabdakalpadruma (0.23×) depletes harder among the eleven measured pairs; the great PW core sits **below even the mw72 native baseline (0.46×)**. The 1899 annexure is not where 1855–75 core vocabulary lives.
2. **The absorption is in MAIN, and it is massive:** 93,778 of MW99's 188,016 main headwords (49.9 %) are pwg k1. Of pwg's own 106,082 headwords, 94,779 (89.3 %) appear in MW99 at all — and 98.9 % of that overlap (93,778/94,779) sits in the main body, only 1.1 % in the annexure. MW99 did not miss the great PW; it digested it into the letter A–that-ends-in-ḥ of the main alphabet.
3. **The two halves now close the loop.** PW-influence on MW99 splits cleanly by genre: the **core** (pwg, finished 1875) depletes in the annexure at 0.33× while occupying 49.9 % of main; the **late Nachträge stream** (pw sup_1…sup_7, 1879–1889) enriches the annexure at 7.79–7.91× while covering under 4 % of main. The annexure is where vocabulary from *after/alongside* MW's core-digestion landed — supplement-genre territory (sch 5.12× confirms), not delayed pwg-core territory: only 16.5 % of the 6,067 annexure headwords are pwg k1, vs 29.6 % for sup_7 alone.
4. **Chronology honesty.** MW72 (1872) covers only 33.0 % of pwg k1 — most of the great PW was still appearing as the first MW edition printed — while MW99 (1899) carries 89.3 %: the absorption window is exactly the 1872→1899 revision. The 1,001 annexure-headword overlap is a **shared-substrate signature** (C4 caveat), not a citation relation; no claim is made that MW's annexure drew on pwg.
5. **Framing for the Andhrabharati postulate (csl-corrections#119).** The postulate's quantitative form now has both legs: annexure ≈ supplement-genre vocabulary (Nachträge 7.8–7.9×, sch 5.12×), annexure ≠ core vocabulary of any finished predecessor (pwg 0.33×, kośas 0.23×–0.61×).

## 4 · Reproduction

```sh
python3 HeadwordLists/enrichment_compare.py --selftest
python3 HeadwordLists/enrichment_compare.py --target mw --source pwg \
  --tsv HeadwordLists/pwg_mw99_enrichment_17-09-2026.tsv \
  --json HeadwordLists/pwg_mw99_enrichment_17-09-2026.json
# registry regeneration (adds the pwg row + matrix row; 4 published rows byte-identical):
python3 HeadwordLists/enrichment_compare.py --target mw \
  --source pw:sup_7 --source pw:sup --source pwkvn --source bhs --source pwg \
  --matrix-dict mw72 --matrix-dict pw --matrix-dict pwg \
  --tsv HeadwordLists/enrichment_metrics_registry_17-09-2026.tsv \
  --matrix-tsv HeadwordLists/enrichment_matrix_17-09-2026.tsv \
  --json HeadwordLists/enrichment_metrics_registry_17-09-2026.json
```

Env `CSL_ORIG` overrides the csl-orig/v02 location (default `../csl-orig/v02` beside the checkout). Deterministic stdlib builder, ~10 s end-to-end, csl-orig read-only, 3-try stop-budget per source (source OK, no flags).

## 5 · Verifier

Two-tier verification, 17-09-2026:

1. **Executor-run runtime tier — PASS.** `--selftest` PASS (C2–C5 fixtures incl. the C3 proper-partition duplicate-k1 fixture). Both §4 commands re-ran 17-09-2026 producing the committed TSV/JSON (target 194,083 = 6,067 + 188,016; pwg row as §2; the four published registry rows byte-identical in `git diff`). **Independent re-derivation probe** — a separate single-pass string-scan state machine (no entry generator, no shared code, `<L>`/`<k1>` index parsing, /tmp scratch, not committed) — reproduced **every cell exactly**: pwg n=106,082; in_annex 1,001 (16.5 %); in_main 93,778 (49.9 %); enrichment 0.330791 → 0.33×; plus the derived cells 94,779 (89.3 %) total overlap / 11,303 (10.7 %) absent.

2. DeepSeek read-only recheck (paired verifier family) — see below.

_Gasūns_
