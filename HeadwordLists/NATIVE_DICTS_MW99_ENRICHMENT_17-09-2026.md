# NATIVE_DICTS_MW99_ENRICHMENT — 6×2 matrix (share in MW99 annexure vs main) with publication years

_Created: 17-09-2026 · Last updated: 17-09-2026_

H5059 (epic E009, child of H4360). Measured with the generic stdlib builder [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) (H5056) under the locked counting conventions C1–C4 of [`ENRICHMENT_METRICS_REGISTRY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/ENRICHMENT_METRICS_REGISTRY.md) §0 (C5 sup-layer headword rule not exercised — all six sources are plain `CODE` k1 sets). csl-orig is read-only input throughout. Sibling measurements: pw-Nachträge 7.79–7.91×, Edgerton BHS 2.09× (registry §1); H5057 decomposes the BHS pair.

## 1 · The six Sanskrit-native dictionaries and their publication years

Publication years are read from the TEI source descriptions of the digitizations themselves — `<date>` inside `<biblStruct>` in [`csl-orig/v02/<code>/<code>header.xml`](https://github.com/csl-orig) (read-only), not from memory:

| code | work (TEI title) | author(s) | publication year(s) |
|---|---|---|---|
| ap90 | The Practical Sanskrit-English Dictionary | Vaman Shivram Apte | **1890** |
| ap | Revised and enlarged edition of Prin. V. S. Apte's The practical Sanskrit-English dictionary | Apte / Gode / Karve (Prasad Prakashan) | **1957–1959** |
| sch | Nachträge zum Sanskrit-Wörterbuch (zu Böhtlingks kürzerer Fassung) | Richard Schmidt (Harrassowitz) | **1928** |
| vcp | Vācaspatyam (Bṛhatsaṃskṛtābhidhāna) | Tārānātha Tarkavācaspati (Calcutta) | **1873–1884** (1962 Varanasi reprint also in header) |
| skd | Śabdakalpadruma (7 vols, Calcutta) | Rādhākānta Deva | **1821–1851** (an 1886 edition is also cited in the header) |
| mw72 | A Sanskrit-English Dictionary, 1st ed. | Monier Monier-Williams | **1872** |

Note on genre: `sch` is included in the native-dict batch as briefed, but it is not a kośa — it is the **Nachträge** (supplement) to Böhtlingk's shorter Petersburg Wörterbuch, i.e. genre-mate of `pw:sup`/`pwkvn`, and the matrix below shows it behaving accordingly.

## 2 · The 6×2 matrix (MW99 target: 194,083 k1 = 6,067 annexure + 188,016 main)

Target anchors reproduce the H5056 run exactly (delta 0). Shares are of the **target** sets (C4): annexure share = |S ∩ annexure| / 6,067; main share = |S ∩ main| / 188,016.

| source | year | n(S) | in annexure | annexure share | in main | main share | enrichment |
|---|---|--:|--:|--:|--:|--:|--:|
| ap90 | 1890 | 34,277 | 330 | **5.4 %** | 16,846 | **9.0 %** | 0.61× |
| ap | 1957–1959 | 88,872 | 556 | **9.2 %** | 37,651 | **20.0 %** | 0.46× |
| sch | 1928 | 28,455 | 2,060 | **34.0 %** | 12,463 | **6.6 %** | **5.12×** |
| vcp | 1873–1884 | 48,636 | 655 | **10.8 %** | 38,408 | **20.4 %** | 0.53× |
| skd | 1821–1851 | 40,817 | 66 | **1.1 %** | 8,789 | **4.7 %** | 0.23× |
| mw72 | 1872 | 51,159 | 672 | **11.1 %** | 45,184 | **24.0 %** | 0.46× |

Machine-readable TSV: [`native_dicts_mw99_enrichment_17-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/native_dicts_mw99_enrichment_17-09-2026.tsv) (full-precision `.json` beside it); rows also appended to [`enrichment_metrics_registry_17-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_metrics_registry_17-09-2026.tsv)/`.json` per registry §3.

## 3 · Reading (set-overlap signature, not causation — C4 caveat)

1. **Five of six native dictionaries DEPLETE (enrichment < 1×): 0.23×–0.61×.** The MW99 annexure is not where the Sanskrit-native lexicographic tradition's vocabulary lives. Śabdakalpadruma is the extreme: only 66 of the 6,067 annexure headwords (1.1 %) are skd headwords, vs a 4.7 % main share.
2. **`sch` is the sole enricher (5.12×) — and it is a Nachträge, not a kośa.** 2,060 of the 6,067 annexure headwords (34.0 %) are also Schmidt k1 — equivalently 7.2 % of Schmidt's 28,455 k1 sit in the annexure. This lands the six-row matrix squarely on the same line as the registry's pw-Nachträge rows (7.79–7.91×): the annexure carries **supplement-genre vocabulary**, whatever the source's civilization.
3. **Chronology honesty.** MW99 printed in 1899, Schmidt's Nachträge in 1928, Apte's revised edition in 1957–1959 — later sources cannot have fed the annexure at print time, and the annexure could not have fed them its post-1899 additions. The shares are **shared-substrate signatures**: what the 1899 annexure collected is the same vocabulary the later Nachträge tradition collected, not a citation relation.
4. **mw72 as the native baseline (0.46×):** the 1872 first edition's headword set covers 24.0 % of MW99 main but only 11.1 % of the annexure — the annexure is disproportionately vocabulary **absent from 1872** (that is what a 27-year supplement is). Continuity side-fact: 45,856 of MW72's 51,159 k1 (89.6 %) appear in MW99 at all — 45,184 in main + 672 in the annexure (JSON matrix row `n_in_mw` = 45,856).
5. **ap90 → ap growth does not chase the annexure:** the 1957–1959 revision adds ~54,600 k1 over the 1890 edition, yet annexure share moves only 5.4 % → 9.2 % — a genre ceiling, not a quantity effect.

## 4 · Reproduction

```sh
python3 HeadwordLists/enrichment_compare.py --selftest
python3 HeadwordLists/enrichment_compare.py --target mw \
  --source ap90 --source ap --source sch --source vcp --source skd --source mw72 \
  --tsv HeadwordLists/native_dicts_mw99_enrichment_17-09-2026.tsv \
  --json HeadwordLists/native_dicts_mw99_enrichment_17-09-2026.json
```

Env `CSL_ORIG` overrides the csl-orig/v02 location (default `../csl-orig/v02` beside the checkout). Deterministic stdlib builder, ~1 min end-to-end (six 5–50 MB sources), csl-orig read-only, 3-try stop-budget per source (all six sources OK here, no flags).

## 5 · Verifier

Two-tier verification, 17-09-2026:

1. **Executor-run runtime tier — PASS.** `--selftest` PASS (C2–C5 fixtures incl. the C3 proper-partition duplicate-k1 fixture). Full §4 command re-ran 17-09-2026 producing the committed TSV/JSON (target 194,083 = 6,067 + 188,016; six rows as §2, no source errors). **Independent re-derivation probe** — a separate single-pass state-machine implementation (no entry generator, no shared code, string-scan parsing, temp-dir scratch, not committed) — reproduced **all 12 matrix cells + 3 target anchors** exactly: ap90 34,277/330/16,846; ap 88,872/556/37,651; sch 28,455/2,060/12,463; vcp 48,636/655/38,408; skd 40,817/66/8,789; mw72 51,159/672/45,184.

2. **DeepSeek read-only recheck (paired verifier family) — PASS (round 2, all four tiers).** Conventions parity (C1–C4 claimed, C5 correctly marked unexercised), report-claims parity (§2 vs TSV vs registry TSV/JSON cell-for-cell), arithmetic re-derivation (all six enrichments recomputed at 2 dp from the raw cells against 6,067 / 188,016; anchors 194,083 = 6,067 + 188,016), and honesty check (set-overlap framing, no causation). **Round 1 verdict was FAIL on two §3 prose defects** — a sch share attached to the wrong denominator (34.0 % is of the annexure; 7.2 % of Schmidt's 28,455 k1) and MW72→MW99 survival understated (main-only 45,184 = 88.3 % instead of 45,856 = 89.6 % incl. the annexure overlap) — both repaired in the same pass and re-verified; **the matrix cells themselves were exact in both rounds**. Scope limit recorded honestly: the seat has no shell and no csl-orig access, so corpus-level execution and the §1 publication years (TEI sourceDesc) were outside its reach.

_Gasūns_
