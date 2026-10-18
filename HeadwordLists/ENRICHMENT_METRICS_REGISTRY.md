# ENRICHMENT_METRICS_REGISTRY — measured share-in-annexure vs share-in-main pairs

_Created: 17-09-2026 · Last updated: 17-09-2026_

Registry of measured **enrichment pairs** (source set **S** × target dictionary **D**) computed by the generic stdlib builder [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) (H5056, epic E009). It generalizes the bespoke arithmetic that first produced the published figures in [`MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md) §2/§6. Sibling consumers: H5057 (BHS annexure-layer decomposition), H5058 (PWG-vs-MW99 main-vs-annexure). csl-orig is read-only input throughout.

## 0 · Locked counting conventions (deviating forks the numbers)

| id | convention |
|---|---|
| C1 | Source headword sets are `<k1>`-only, verbatim field values, no normalization. |
| C2 | Target annexure = set of k1 whose entry body contains the annexure tag (default `<info n="sup"/>`, the MW99 Supplemental-Word annexure; 6,067 k1). |
| C3 | Target main = k1_all **minus** annexure — a proper partition on duplicate k1s (a k1 appearing both tagged and untagged counts annexure-only; the naive tag-absence set overlaps the annexure on duplicate k1s — DeepSeek verifier finding 14-09-2026). MW99: k1_all 194,083 = annexure 6,067 + main 188,016. |
| C4 | enrichment(S, D) = (|S ∩ annexure| / |annexure|) / (|S ∩ main| / |main|). Set-overlap ratio, **not** citation counts — it ranks provenance likelihood (caveat §9.1 of the 15-09 report). `inf` when S hits the annexure but not main; `n/a` when the target has no annexure split (matrix-only pair). |
| C5 | pw-Nachträge sup-layer headword = k2 with **all** leading `*` characters stripped (`lstrip("*")`, the prior-art convention) when k2 starts with `*`, else k1; deduped. |

## 1 · Registry of measured pairs

Tolerance for reproduction: **±0.01× absolute** against the published 2-dp figure (builder emits 2-dp). All four published pairs reproduce with delta 0.00.

| measured | source set S | target D | n(S) | in annexure | in main | enrichment | builder | first published | verified |
|---|---|---|--:|--:|--:|--:|---|---|---|
| 17-09-2026 | pw `sup_7` Nachträge, letzte Teil (1889) | mw (MW99) | 13,094 | 1,798 (29.6 %) | 7,157 (3.8 %) | **7.79×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | 15-09-2026 report §2 | two-tier PASS 17-09-2026 (§4) |
| 17-09-2026 | pw `sup_1`…`sup_7` all layers (1879–1889) | mw (MW99) | 14,401 | 1,956 (32.2 %) | 7,659 (4.1 %) | **7.91×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | 15-09-2026 report §2 | two-tier PASS 17-09-2026 (§4) |
| 17-09-2026 | `pwkvn` standalone Nachträge digitization | mw (MW99) | 14,995 | 1,971 (32.5 %) | 7,787 (4.1 %) | **7.84×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | 15-09-2026 report §2 (7.84× first in the 14-09 recheck) | two-tier PASS 17-09-2026 (§4) |
| 17-09-2026 | `bhs` Edgerton (1953), k1-only | mw (MW99) | 17,777 | 413 (6.8 %) | 6,128 (3.3 %) | **2.09×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | 15-09-2026 report §2/§6 | two-tier PASS 17-09-2026 (§4) |
| 17-09-2026 | `pwg` Böhtlingk-Roth great PW, 1855–1875, k1-only | mw (MW99) | 106,082 | 1,001 (16.5 %) | 93,778 (49.9 %) | **0.33×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | [`PWG_MW99_ENRICHMENT_17-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/PWG_MW99_ENRICHMENT_17-09-2026.md) §2 (H5058) | probe PASS 17-09-2026; DeepSeek tier INCONCLUSIVE — provider weekly-credit ceiling, rerun owed (report §5) |

Machine-readable: [`enrichment_metrics_registry_17-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_metrics_registry_17-09-2026.tsv) + `.json` (full-precision enrichment, conventions echo). Cross-read of the four rows unchanged since 15-09: the MW99 annexure is ~7.8× enriched for PW-Nachträge vocabulary vs ~2.1× for Edgerton BHS — ~3.7× more PW-flavoured than BHS-flavoured, the quantitative form of Andhrabharati's annexure-draws-on-Nachträge postulate. H5058 adds the pwg half: **the great-PW core DEPLETES in the annexure at 0.33×** while occupying 49.9 % of MW99 main — PW-influence on MW99 splits by genre, core absorption into main vs annexure supplement-genre enrichment (Nachträge 7.79–7.91×); shares are set-overlap signatures, not causation (MW99 1899 postdates pwg 1875).
| 17-09-2026 | `ap90` Apte Practical Skt-Eng, 1890 | mw (MW99) | 34,277 | 330 (5.4 %) | 16,846 (9.0 %) | **0.61×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | [`NATIVE_DICTS_MW99_ENRICHMENT_17-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NATIVE_DICTS_MW99_ENRICHMENT_17-09-2026.md) §2 (H5059) | probe + DeepSeek PASS 17-09-2026 (report §5) |
| 17-09-2026 | `ap` Apte rev. & enlarged, 1957–1959 | mw (MW99) | 88,872 | 556 (9.2 %) | 37,651 (20.0 %) | **0.46×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | H5059 report §2 | probe + DeepSeek PASS 17-09-2026 (report §5) |
| 17-09-2026 | `sch` Schmidt Nachträge, 1928 | mw (MW99) | 28,455 | 2,060 (34.0 %) | 12,463 (6.6 %) | **5.12×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | H5059 report §2 | probe + DeepSeek PASS 17-09-2026 (report §5) |
| 17-09-2026 | `vcp` Vācaspatyam, 1873–1884 | mw (MW99) | 48,636 | 655 (10.8 %) | 38,408 (20.4 %) | **0.53×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | H5059 report §2 | probe + DeepSeek PASS 17-09-2026 (report §5) |
| 17-09-2026 | `skd` Śabdakalpadruma, 1821–1851 | mw (MW99) | 40,817 | 66 (1.1 %) | 8,789 (4.7 %) | **0.23×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | H5059 report §2 | probe + DeepSeek PASS 17-09-2026 (report §5) |
| 17-09-2026 | `mw72` Monier-Williams 1st ed., 1872 | mw (MW99) | 51,159 | 672 (11.1 %) | 45,184 (24.0 %) | **0.46×** | [`enrichment_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_compare.py) | H5059 report §2 | probe + DeepSeek PASS 17-09-2026 (report §5) |

Machine-readable: [`enrichment_metrics_registry_17-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_metrics_registry_17-09-2026.tsv) + `.json` (full-precision enrichment, conventions echo) — 10 measured pairs after H5059. Cross-read of the first four rows unchanged since 15-09: the MW99 annexure is ~7.8× enriched for PW-Nachträge vocabulary vs ~2.1× for Edgerton BHS — ~3.7× more PW-flavoured than BHS-flavoured, the quantitative form of Andhrabharati's annexure-draws-on-Nachträge postulate. H5059 adds the native-dict half: **five of six Sanskrit-native dictionaries deplete below 1× (0.23×–0.61×)**, the sole enricher being Schmidt's 1928 **Nachträge** (5.12×) — the annexure carries supplement-genre, not kośa-genre, vocabulary; shares are set-overlap signatures, not causation (MW99 1899 predates sch 1928 / ap 1957–59).

## 2 · SxD coverage matrix (17-09-2026 run)

Share of S present in each dictionary's k1 set (MW99 split into annexure/main in §1). Full TSV: [`enrichment_matrix_17-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/enrichment_matrix_17-09-2026.tsv).

| S \ D | mw72 | pw | pwg | bhs | mw | pwkvn |
|---|--:|--:|--:|--:|--:|--:|
| pw:sup_7 (n=13,094) | 22.1 % | 99.9 % | 29.4 % | 11.8 % | 68.4 % | 99.9 % |
| pw:sup (n=14,401) | 20.9 % | 99.9 % | 27.7 % | 11.0 % | 66.8 % | 99.9 % |
| pwkvn (n=14,995) | 20.2 % | 99.9 % | 26.9 % | 10.7 % | 65.1 % | 100.0 % |
| bhs (n=17,777) | 17.1 % | 34.3 % | 26.9 % | 100.0 % | 36.8 % | 9.0 % |
| pwg (n=106,082) | 33.0 % | 93.8 % | 100.0 % | 4.5 % | 89.3 % | 3.8 % |

Sanity anchors vs the 15-09 report: `sup_7` ∩ MW72 = 2,892 (22 %) and ∩ MW99 = 8,955 (68 %) — both match §3 of the published uptake table.

## 3 · Reproduction

```sh
python3 HeadwordLists/enrichment_compare.py --selftest
python3 HeadwordLists/enrichment_compare.py --target mw \
  --source pw:sup_7 --source pw:sup --source pwkvn --source bhs --source pwg \
  --matrix-dict mw72 --matrix-dict pw --matrix-dict pwg \
  --tsv HeadwordLists/enrichment_metrics_registry_17-09-2026.tsv \
  --matrix-tsv HeadwordLists/enrichment_matrix_17-09-2026.tsv \
  --json HeadwordLists/enrichment_metrics_registry_17-09-2026.json
```

Env `CSL_ORIG` overrides the csl-orig/v02 location (default: `../csl-orig/v02` beside the repo checkout). ~4 s end-to-end, stdlib only, deterministic (sorted iterations; no hash-order-dependent output). Source spec grammar: `CODE` (k1 set), `CODE:sup_N` (one sup layer), `CODE:sup` (all layers); `--source-file LABEL=PATH` admits arbitrary one-per-line SLP1 sets; per-source failures are flagged (`status=ERROR:…`, 3-try stop-budget) and never stall the run. Adding a pair = one `--source` + one registry row with date and builder pin.

## 4 · Verifier

Two-tier verification, 17-09-2026:

1. **DeepSeek read-only recheck (paired verifier family) — PASS, static + parity tier.** Conventions-vs-code review (C1–C5 implemented, including the C3 proper partition asserted by the selftest duplicate-k1 fixture), report-claims parity of §1 against the published §2/§6 of [`MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md) (cell-for-cell), and independent arithmetic re-derivation of every registry cell — all four enrichment values reproduce at 2 dp with delta 0.00. Scope limit recorded honestly: the councillor seat has no shell and no csl-orig read access, so corpus-level execution was not runnable from that seat; it ruled the registry may carry the reproduction claim only once a runtime tier exists.
2. **Executor-run runtime tier — PASS (fills that gap, same day).** `--selftest` PASS; the exact §3 command re-ran 17-09-2026 producing the committed TSV/JSON (target 194,083 = 6,067 + 188,016; four rows as in §1); plus an **independent re-derivation probe** — a separate single-pass state-machine implementation (no entry generator, no body accumulation, /tmp scratch, not committed) — reproducing every count and all four enrichments: sup_7 13,094 / 1,798 / 7,157 / 7.79×; sup_all 14,401 / 1,956 / 7,659 / 7.91×; pwkvn 14,995 / 1,971 / 7,787 / 7.84×; bhs 17,777 / 413 / 6,128 / 2.09×.

**Verdict: counts re-derivable by two independent implementations; the published PW 7.79–7.91× and BHS 2.09× figures reproduce within tolerance (±0.01×, delta 0.00).**

_Gasūns_
