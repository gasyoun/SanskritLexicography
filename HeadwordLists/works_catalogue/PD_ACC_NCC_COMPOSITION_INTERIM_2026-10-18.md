# PD → ACC → NCC composition — interim, AOB denominator

_Created: 18-10-2026 · H6994 (S3 of H6989) · Executor: DeepSeek v4.1 Flash (`deepseek/deepseek-flash`)_

**Flag on every number:** `interim, AOB denominator`. The Index of Works (H6992) is not yet the denominator; the AOB title layer is. Two denominators are named and never mixed: the **full AOB declared canon** (1,430 printed entries; interim, AOB denominator) and the **letter-a citation mass** (398,359 occurrences; 123,453 in the 164 adjudicated titles) (interim, AOB denominator).

## 1. What was joined

* PD works with an AOB title: **3224** sigla, **309876** occurrences (interim, AOB denominator).
* Exact folded ACC matches: **857** works, **98062** occurrences (interim, AOB denominator).
* Exact folded NCC matches: **978** works, **96835** occurrences (interim, AOB denominator).
* Provenance is fixed by the grill (Q10): `composed` = PD→ACC→NCC, `direct` = PD→NCC, `both` = both paths agree; `cd_bridge` lives only in the separate ledger.

## 2. Composition headline — never counts a bridged row

| measure | value | flag |
|---|---:|---|
| composition rows (PD siglum × ACC↔NCC edge) | 8930 | interim, AOB denominator |
| distinct ACC↔NCC edges | 3401 | interim, AOB denominator |
| distinct PD sigla covered | 993 | interim, AOB denominator |
| PD occurrences covered | 99178 | interim, AOB denominator |
| occurrence share of the 309876 AOB-title mass | 32.0% | interim, AOB denominator |
| `cd_bridge` rows in this table | 0 | interim, AOB denominator |

## 3. Provenance split

| provenance | rows | flag |
|---|---:|---|
| `composed` | 83 | interim, AOB denominator |
| `direct` | 657 | interim, AOB denominator |
| `both` | 8190 | interim, AOB denominator |

## 4. The C3 control (164 adjudicated titles, 123,453 occurrences)

| test | works | occurrences | flag |
|---|---:|---:|---|
| ACC exact folded headword | 122 / 164 | 106408 | interim, AOB denominator |
| ACC exact + containment | 155 / 164 | 117843 | interim, AOB denominator |
| NCC exact folded headword | 127 / 164 | 93934 | interim, AOB denominator |
| C3 baseline quoted in the sweep (exact) | 122 / 164 | 106,408 | interim, AOB denominator |
| C3 baseline quoted in the sweep (recoverable) | 161 / 164 | 122,365 | interim, AOB denominator |

The control reproduces the C3 baseline: **122/164 = 74.4%** exact and **106408/123,453 = 86.2%** occurrence-weighted (interim, AOB denominator). The wider AOB-title layer is larger and weaker at the same time: the extra titles are OCR-grade and mostly absent from either catalogue, so its headline share is not comparable to the 164-title control.

## 5. Two denominators (never mixed)

| denominator | value | use | flag |
|---|---:|---|---|
| full AOB declared canon | 1,430 printed entries | declared-coverage denominator | interim, AOB denominator |
| letter-a citation mass | 398,359 occurrences | exercised-citation denominator | interim, AOB denominator |
| adjudicated control mass | 123,453 occurrences | C3 baseline | interim, AOB denominator |
| AOB-title layer mass | 309876 occurrences | this composition | interim, AOB denominator |

## 6. C/D bridge ledger (separate; never in the headline)

| measure | value | flag |
|---|---:|---|
| C/D rows with score ≥ 0.90 and a PD match on ≥ 1 side | 50 | interim, AOB denominator |
| accepted bridges (ledger only) | 36 | interim, AOB denominator |
| rejected bridges | 14 | interim, AOB denominator |
| bridged rows in the headline | 0 | interim, AOB denominator |

### Named rejected contradiction (the check is live)

Row `19619` × `24_297_b_2976` (tier D, score 0.947) is rejected (interim, AOB denominator):
* ACC title: `rAjABizekapadDati`
* NCC title: `Rāmābhiṣekapaddhati`
* PD siglum matching both sides: `Abhise.;Abhiṣe.`
* verdict: **REJECT** — contradiction: same PD siglum matches two different titles (interim, AOB denominator)

The same siglum cannot name two different works. The row is retained in the ledger with its verdict and never enters the composition table.

## 7. Caveats

* The 164-title control is the reliable subset; the wider layer uses H6707 OCR-grade titles (interim, AOB denominator).
* ACC titles are SLP1, NCC titles IAST; both are folded with the same diacritic-free key, so aspiration and retroflex distinctions are intentionally flattened — homographs remain multiple rows.
* C/D bridges use the permissive exact-or-containment PD route; that is the point of a separate ledger (interim, AOB denominator).
* No cd_bridge row is a confirmed ACC↔NCC link (interim, AOB denominator).

## 8. Reproduce

```sh
python3 HeadwordLists/works_catalogue/pd_acc_ncc_composition.py \
  --acc acc.jsonl --ncc ncc.jsonl \
  --crosswalk works_crosswalk.tsv \
  --proposed works_crosswalk_agent_proposed.tsv \
  --pd-dir ../csl-atlas/data/pd
python3 HeadwordLists/works_catalogue/check_pd_acc_ncc_composition.py
```

_Dr. Mārcis Gasūns_
