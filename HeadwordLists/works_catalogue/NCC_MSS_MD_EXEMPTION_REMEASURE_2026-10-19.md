# NCC MSS — the `MD` exemption and a corrected re-measurement on the workbook lexicon (H7084)

_Created: 19-10-2026 · DeepSeek v4.1 Flash (`deepseek-flash`) · launch box: Mac · workbook **present**_
_Parent: [H7080 adjudication](NCC_MSS_ADJUDICATION_100_2026-10-19.md) · locked design: [NCC_MSS_PRECISION_100_2026-10-18.md](NCC_MSS_PRECISION_100_2026-10-18.md) (rule quoted, never edited)_

## Verdict first

**HOLD** for the full 152,526-entry census.

| gate | value | threshold | pass |
|---|---|---:|---|
| point precision | **86 / 100 = 86.0 %** | ≥ 95 % | **NO** |
| Wilson 95 % lower bound | **77.863 %** | ≥ 90 % | **NO** |
| `AMBIGUOUS` count | **0** | ≤ 10 | yes |
| canary names both numbers | Mahābhārata **2,355** · Rāmāyaṇa **819** | both named | yes (but both DIFF — see below) |

The GO rule is the one locked on 18-10-2026 before any verdict row existed; it is reproduced here
unchanged and was not edited after these results. Two of its four conditions fail, and they are the
two that decide the gate: the parser is 9 points short of 95 % and the interval floor is 12 points
short of 90 %.

**The corrected measurement is not better than the old one — it is 1.9 points worse** (87.9 % →
86.0 %) and it is measured on a different, larger population. That is the honest result of doing the
comparison on the population the census actually intends: the old 87.9 % described a parser with the
corpus's third-largest catalogue silently removed, and one of the two `MD`-caused false positives in
that draw (`Jain 8771`) is a SUPPORTED `MD` unit today. The two intervals overlap almost completely,
so the difference is not evidence of a regression; the parser is simply still ≈ 12 points short.

## Why this handoff exists

H7080's 100-unit adjudication exposed two independent causes, both proved on 19-10-2026, and this
pass fixes them as one unit.

1. **`MD` was dropped from the catalogue lexicon.** `catalogue_regex()` removes every key matching
   `ROMAN_RE` — correct for the 66 genuine volume markers (`II`, `III`, `LXXVIII`) and wrong for
   `MD`, which is spelled entirely in roman-numeral letters but is a real NCC catalogue with
   **11,672 witnesses** (third-largest siglum after `II` 31,166 and `III` 14,387). `MD.` therefore
   never terminated a segment; MD accessions folded into whatever catalogue preceded them.
2. **The H7080 sampler ran without `--vdcs-details`.** Its population was the 991-siglum lexicon's
   1,290 units, not the workbook lexicon's. With the workbook the lexicon holds 1,293 sigla and the
   pilot yields 2,021 raw units — within 3 % of the 2,080 H6995 always named — versus 1,854 without.

Both numbers are reproduced exactly below, on this box, before the fix.

## The exemption, and why the two obvious fixes were refused

The sanctioned fix is evidence-based and lives in a committed allowlist, not in a run-time rule:

[`ncc_roman_catalogue_allowlist.json`](ncc_roman_catalogue_allowlist.json) — one entry, `MD`, with
its roman value (1,500), its 7,771 workbook `Details` mentions, its 11,672 witnesses, the evidence
that it is a catalogue, and the defect it closes. [`census_ncc_mss.py`](census_ncc_mss.py) reads it at
import and **fails loudly if the file is missing** (it prints the path and says not to fall back to
dropping every roman-shaped siglum). The loader cannot tell a *deliberately* empty allowlist from a
lost one, so the emptiness guard is the selftest, not the loader: if the workbook vocabulary loses
its last roman-shaped key, the vocabulary test below must be updated in the same change.

Provenance is a second committed artifact: [`ncc_vdcs_catalogue_keys_2026-10-19.json`](ncc_vdcs_catalogue_keys_2026-10-19.json)
holds the workbook's **435 catalogue keys** and their `Details` mention counts, dumped by
`--dump-vdcs-keys`. Of those 435 keys exactly **one** is roman-shaped: `MD`. The workbook's `mss`
column is never read; no count in that file is a manuscript census.

Two candidate rules were measured and rejected before this one was adopted:

| candidate rule | measurement | verdict |
|---|---|---|
| keep roman sigla that lead a witness string | all 67 dropped sigla lead — `II`/`III` are orphaned volume markers whose catalogue was stripped upstream (`Hpr. III. 49` split into two witnesses, leaving `II. 48`) | discriminates nothing |
| keep roman sigla that rarely follow another catalogue | `II` reads 53-after/132-standalone, `MD` reads **12-after/17-standalone** | `MD` scores *worse* than `II` |

The adopted rule is the only one with an outside witness: the workbook's own catalogue vocabulary.
Because the allowlist is committed, an offline run without the workbook behaves identically (and
`MD` is in the lexicon from `mss_witnesses` anyway, so the exemption binds in both states).

## What changed

- **`census_ncc_mss.py`** — allowlist load + `catalogue_regex(lexicon, allowlist=None)` keeps
  allowlisted roman-shaped sigla (and adds them even to a narrow lexicon);
  `edition_reference_reason()` no longer classes an allowlisted siglum as `roman_volume`;
  `dump_vdcs_catalogue_keys()` / `--dump-vdcs-keys` writes the vocabulary artifact;
  `--no-roman-allowlist` reproduces the pre-fix baseline on demand (the same baseline-toggle pattern
  H7073 used for `--no-edition-filter`); `extract_units(..., trace=[])` records body coordinates per
  kept unit, and `producing_span()` / `--enrich-spans` turn that into an auditable
  `producing_span` column on a drawn TSV.
- **`ncc_roman_catalogue_allowlist.json`** (new) — the exemption with provenance and rejected
  alternatives.
- **`ncc_vdcs_catalogue_keys_2026-10-19.json`** (new) — the workbook catalogue vocabulary the
  allowlist is checked against.
- **`ncc_mss_adjudication_100_seed20261019.tsv`** (new) — the corrected draw with 100 hand verdicts,
  reason per unit and `producing_span`.
- **`test_census_ncc_mss.py`** — 8 new tests (16 total): the exemption, the edition-filter
  exemption, the `--no-roman-allowlist` baseline, offline matching, **allowlist == committed
  vocabulary**, **allowlist == live workbook when present**, producing-span location, span
  enrichment.

The two provenance tests are the requested selftest: the module fails when the allowlist and the
workbook vocabulary disagree. The first runs offline against the committed artifact; the second
re-reads the workbook when it is on the box and skips (loudly) when it is not.

## Pre-fix numbers reproduced, then the corrected population

Same parser, same 500-entry pilot (39 volumes), only the lexicon and the allowlist toggled. Every
cell reproduces from the two flags, no workbook edit involved:

```bash
WB="$HOME/Documents/GitHub/VisualDCS/non-derived/NCC/Works-Share-NCC/NCC-mss-counting-1 031 077.xlsx"
python census_ncc_mss.py --ncc ncc.jsonl --pilot 500 --out-dir /tmp/h7084                      # no workbook, exemption on
python census_ncc_mss.py --ncc ncc.jsonl --pilot 500 --no-roman-allowlist --out-dir /tmp/h7084 # no workbook, exemption off (H7073 baseline)
python census_ncc_mss.py --ncc ncc.jsonl --vdcs-details "$WB" --pilot 500 --out-dir /tmp/h7084 # workbook, exemption on (corrected)
python census_ncc_mss.py --ncc ncc.jsonl --vdcs-details "$WB" --pilot 500 --no-roman-allowlist --out-dir /tmp/h7084 # workbook, exemption off (H7080 state)
```

| lexicon | `MD` | mentions | raw units | kept after filter | per-entry distinct |
|---|---|---:|---:|---:|---:|
| 991 sigla (no workbook) — H7073/H7080 baseline | dropped | 1,648 | **1,854** | 1,326 | **1,290** |
| 991 sigla | kept | 1,677 | 1,882 | 1,355 | 1,319 |
| 1,293 sigla (workbook) — H7080's pre-fix state | dropped | 1,750 | **2,021** | 1,490 | **1,449** |
| 1,293 sigla — **corrected** | kept | 1,779 | **2,046** | 1,518 | **1,477** |

The first and third rows reproduce the handoff's 1,854 / 1,290 and 2,021 / 1,449 exactly, which is
the check that this box measures what H7080 measured. The corrected raw harvest (2,046) is **1.6 %
below** the 2,080 H6995 named. `MD` now yields **44 units across 27 pilot entries**; the net raw
delta is +25 because the other 19 already sat inside a preceding catalogue's segment.

## The corrected draw (pre-declared)

- Population: **1,477** distinct post-filter units, 39 volumes.
- Seed: **20261019** — declared before the first verdict was read, and never re-drawn after results.
- Stratification unchanged: proportional allocation, floor 2 per volume, capped by supply; the draw
  reaches all **39 volumes**.
- Draw file: [`ncc_mss_adjudication_100_seed20261019.tsv`](ncc_mss_adjudication_100_seed20261019.tsv),
  101 lines (header + 100 units), **77 distinct `ncc_id`**, 49 distinct sigla.
- Two hashes, because they are two artifacts: the **sampler output** (before any hand work) is
  `a657ed79ab69dbe9f34ebd2d9a071a30b45d9a7d8f41fcc1a9c01f0f6f3166f9`, and an identical second run
  produced the same bytes (`cmp` clean) — that is the reproducibility claim. The **committed** file
  (verdicts + `producing_span`) is `b8e2fdc147932483380deea4fb2620104a5053b1e27f75dd5fe6897b0433c1ac`.
- Seed **20261018 was not re-drawn on this lexicon** — that is the post-hoc re-draw the locked design
  forbids; the old draw and its report are untouched.

## Method (H7080's, with the evidence moved to where the accession came from)

The sampler's `source_span` is keyed on the *first* mention of a catalogue in the body; where a body
mentions the same catalogue twice, that span can point at an occurrence that produced a different
accession. This pass therefore adds a `producing_span` column — the quote around the mention whose
segment actually yielded the drawn accession — and every verdict below was read against it. Where
the two spans differ, `producing_span` is the one that decides.

`Details` was used as a second opinion only, and it is demonstrably body-derived: it mixes accession
numbers with years and page ranges (`Ben 1897-1901, p. 173` → `SB. New DC.: {… 1897-1901 …}`), and
it carries the `|20|51|12|81|` page-marker artifacts as "accessions" (`Baroda: 5 {6933 20 51 12 81}`).
It corroborates **66 of the 86 SUPPORTED** units (the accession token appears somewhere in that
`numid`'s `Details` string). Where `Details` and the body disagree the body decides — **16 of the 86
SUPPORTED units** are units the workbook parser filed under a *different* catalogue key
(`Mysore N. D. 44110` under `Br. Mus.`, the whole `Oppert II. 360…` run under `Jha G. N.`,
`Allahabad D. 1207` under `SB.`, `Bikaner 5371` under `Adyar`, `CLB 94` under `BISM.`), and one drawn
unit (`Ind 219`) has no workbook row at all.

## Result

| verdict | count |
|---|---:|
| SUPPORTED | **86** |
| FALSE_POSITIVE | **14** |
| AMBIGUOUS | **0** |
| **total** | **100** |

`precision = 86 / 100 = 0.86` → **86.0 %**, Wilson 95 % CI **[77.863 %, 91.474 %]**
(exact bounds 0.778628 and 0.914737). No unit had to be excluded, so the corpus produced no
undecidable span in this draw.

Reproduce from the committed TSV alone:

```bash
awk -F'\t' 'NR>1 && $5=="SUPPORTED"{s++} NR>1 && $5=="FALSE_POSITIVE"{f++} NR>1 && $5=="AMBIGUOUS"{a++}
            END{printf "S=%d F=%d A=%d  precision=%.4f\n",s,f,a,s/(s+f)}' ncc_mss_adjudication_100_seed20261019.tsv
```

## The 14 false positives, by class

| class | n | units |
|---|---:|---|
| volume/part marker followed by a page range | 4 | `Vol 165`, `Vol 239`, `Vol 476`, `Vol 498` |
| journal title / publication-series volume | 5 | `Bulletin 2`, `L.D. Ser 5`, `Jaipur Mus. Ser 2`, `Jaipur Mus. Ser 8`, `Ind 219` |
| page run shielded by a roman volume marker | 2 | `Cordier 543`, `Ujjain 87` |
| year / imprint | 2 | `Ben 1897`, `Leipzig 1920` |
| comma-separated folio of a compound citation | 1 | `Udaipur II 14` |

| # | vol | siglum | acc | evidence |
|---:|---:|---|---:|---|
| 6 | 2 | Leipzig | 1920 | `German transl., 2 Vol.., Leipzig 1913, 1920.` — place of publication + years |
| 8 | 3 | Ind | 219 | `See Epi. Ind. XI. 219 ff` — the tail of the journal *Epigraphia Indica*; page + `ff` |
| 27 | 10 | Cordier | 543 | `Cordier III. p.. 540. 543.` — explicit page run; `PAGE_PREFIX_RE` tests the segment start, which is the roman `III.` |
| 44 | 17 | Bulletin | 2 | `See Adyar Library Bulletin IV. 2. p.. 66-67.` — journal volume, page follows |
| 45 | 18 | Ben | 1897 | `Skt. Col.. Ben. 1897-1901. p. 173` — acquisition years expanded 1897-1901 into five units; `YEAR_FOLLOWER_RE` does not accept a following `. p.` |
| 52 | 21 | Udaipur II | 14 | `213, 15, 14` — comma-second numbers are folios (133 appears twice, with folios 12 and 19), so 14 is a folio of ms 213 |
| 56 | 23 | L.D. Ser | 5 | `L.D. Ser. 5. 5359.` — publication series volume; `NON_ACCESSION_SIGLA` holds bare `ser`, not the compound key `L.D. Ser` |
| 72 | 29 | Ujjain | 87 | `Ujjain I. p.. 85. 87.` — page run shielded by the roman volume, as #27 |
| 75 | 31 | Vol | 165 | `J.. Ser. 10. Vol. XIX. 163-93, 429-510` — member of the page range 163-93 |
| 76 | 31 | Vol | 239 | `J.. Ser. 11, Vol. IV. 221-305` — member of 221-305 |
| 77 | 31 | Vol | 476 | member of 429-510 |
| 78 | 31 | Vol | 498 | member of 429-510 |
| 82 | 33 | Jaipur Mus. Ser | 2 | `Jaipur Mus. Ser. 2. p. 110.` — series volume, page follows |
| 93 | 36 | Jaipur Mus. Ser | 8 | `Jaipur Mus. Ser. 8. p.. 125-27.` — series volume |

Three patterns account for **10 of the 14** (6 + 3 + 1) and are new relative to H7080's class list:

1. **The page marker is shielded by a roman volume number** — 6 units (`Cordier 543`,
   `Ujjain 87`, and the four `Vol` units): `PAGE_PREFIX_RE` only looks at the character immediately
   after the siglum, so `I.`/`III.` hides the following `p.`. For the `Vol` units the shield is the
   same defect in a different place: `NON_ACCESSION_SIGLA` has no `vol`, and `PAGE_PREFIX_RE`
   requires `vol.` to be followed by a *digit*, so `Vol. XIX. 163-93` never trips it.
2. **Compound series keys bypass the journal filter** (`L.D. Ser`, `Jaipur Mus. Ser.` are keys whose
   tail is `Ser`, but the set holds only the bare `Ser`) — 3 units.
3. **A comma after an accession introduces folios, not accessions** (`Udaipur II. 213, 15, 14`) —
   1 unit, and the single largest silent inflator this draw exposes, because it multiplies one
   manuscript into two or three units.

The remaining 4 are the two imprint/year units (`Leipzig 1920`, `Ben 1897`) and the two journal-page
units (`Bulletin 2`, `Ind 219`), which are H7080 classes in a new spelling rather than new patterns.

H7080's six classes are otherwise gone from this draw: no scholar-name siglum, no subject marker, no
bibliographic page in a secondary source, and — the point of the pass — **no `MD`-fold unit**.

## `MD` coverage: closed

| probe | H7080 (seed 20261018) | H7084 (seed 20261019) |
|---|---:|---:|
| drawn units carrying `MD` | **0 / 100** | **3 / 100** |
| `MD`-caused false positives | 2 (`Adyar 6571`, `Jain 8771`) | **0** |
| `MD` units in the population | 0 (not expressible) | part of 1,477 |
| lexicon sigla dropped as roman volume markers | 67 | **66** |

The direct reproduction, both states in one run:

```bash
cd HeadwordLists/works_catalogue
python - <<'PY'
import sys; sys.path.insert(0, '.')
import census_ncc_mss as M
lex = sorted(['Adyar', 'II', 'MD', 'TD'], key=len, reverse=True)
for label, re_ in (('dropped (pre-fix)', M.catalogue_regex(lex, allowlist=())),
                   ('exempt  (H7084)  ', M.catalogue_regex(lex))):
    print(label, [m.group(0) for m in re_.finditer('Adyar II. p. 211a . MD. 6571-74.')])
PY
# dropped: ['Adyar']   exempt: ['Adyar', 'MD']
```

`II` is absent from **both** lists on purpose: it is a genuine volume marker, it is not on the
allowlist, and it is still dropped — which is exactly why `211a` is not harvested as an accession.

`MD 8771` and `MD 8772` are drawn as `MD` units in this sample and both are SUPPORTED — under
H7080's lexicon `8771` was a FALSE_POSITIVE recorded as `Jain 8771`. `MD 14142` is the third.

## Label truncation: measured, and gone

The handoff asked for a measurement, not an assumption. The test is: at the position where the
drawn siglum matched, does the body carry a **longer workbook catalogue key** that starts there?

| draw | lexicon | units with a longer catalogue name at the mention |
|---|---|---:|
| H7080, seed 20261018 | 991 sigla (no workbook) | **11 / 100** |
| H7084, seed 20261019 | 1,293 sigla (workbook) | **0 / 100** |

The H7080 arm is the positive control and it reproduces the reported class exactly: `Adyar 830 →
Adyar D`, `Mysore 704 → Mysore D`, `Allahabad 3392 → Allahabad D`, `Wai 2148 → Wai D`,
`Otani … → Suzuki, Otani`, `Trav. Uni …`, `Udaipur SS …`. It also finds one the H7080 report did not
list: `Lahore 7 → Lahore 1882` (a catalogue whose key carries its year).

The class disappears with the workbook because the regex is longest-first over a vocabulary that
already contains the compound names — `Adyar D`, `French Inst`, `Mysore D`, `Suzuki, Otani`,
`Trav. Uni`, `Udaipur SS` are all in the 302 keys the workbook adds. The residual is names absent
from **both** vocabularies (`B. J. Inst`, `Calcutta Uni`): none of this draw's SUPPORTED units hits
that shape, and the only drawn unit whose siglum is the tail of a longer key (`Ben 1897`, key
`Skt. Coll. Ben`) is a false positive for an unrelated reason — the body prints `Skt. Col.. Ben.`,
a double period no key matches.

## Canary after the fix (own data)

```bash
python census_ncc_mss.py --ncc ncc.jsonl --vdcs-details "$WB" --canary --out-dir /tmp/h7084
```

| work | body units (post-filter) | VisualDCS `mss` | delta | status |
|---|---:|---:|---:|---|
| Mahābhārata | **2,355** | 21 | +2,334 | DIFF |
| Rāmāyaṇa | **819** | 2,762 | −1,943 | DIFF |
| Skandapurāṇa | 0 | 17 | — | **INCONCLUSIVE (absent from bodies; स्क block absent from the 2022 NCC DB, H7078)** |

The GO rule's canary condition — "still names both numbers" — is satisfied literally. The `MD`
exemption moves Rāmāyaṇa **814 → 819** and Mahābhārata not at all (2,355 → 2,355), so the
siglum was carrying real Rāmāyaṇa accessions but no Mahābhārata ones. Both computable epics still
disagree with VisualDCS in opposite directions, which is the semantic mismatch H7073 and H7080
already recorded: the body parser counts strict `(catalogue, accession)` witness units across every
catalogue an entry mentions; VisualDCS's `mss` column counts one work's manuscripts in one
aggregation. A GO on precision alone would still ship a canary whose two epics disagree by thousands.

That question was measured in the parallel pass
[H7085](NCC_MSS_UNIT_SEMANTICS_2026-10-19.md) (merged five minutes before this report), which
settles it: the workbook's `mss` is **not one object** — its rows are partial index slices and, where
complete, count catalogue page ranges as manuscripts — so the locked canary clause is satisfiable
only vacuously. The census is to publish under the **printed-reference unit** (this parser's unit),
the workbook stays comparison only, and a versioned amendment awaits human ratification
([proposal v2](NCC_MSS_UNIT_SEMANTICS_PROPOSAL_V2_2026-10-19.md)). H7085 measured on `44fb7fe1`,
i.e. *before* this pass's `MD` exemption; the 2,355 / 819 numbers above are the post-exemption
values, and the +5 Rāmāyaṇa difference is `MD`'s contribution.

## What this number does *not* cover

1. **A unit is a witness, not a work.** The 100 units cover **77 distinct `ncc_id`** (one entry
   supplies four units), so a downstream join on `ncc_id` fans out silently.
2. **The population is the 500-entry pilot**, not the 152,526-entry corpus: this estimates *this
   parser on this pilot*. `--full` was not run and is not authorised by a HOLD.
3. **The canary delta is untouched by this pass.** Its *unit semantics* are settled separately by
   [H7085](NCC_MSS_UNIT_SEMANTICS_2026-10-19.md) (printed-reference unit, workbook comparison only,
   v2 amendment pending ratification); the measured delta itself remains, and precision cannot close
   it.
4. **The `MD` repair is correct but not exhaustive.** `AMIA`, `MIM`, or other roman-letter catalogue
   sigla that the workbook does not list would still be dropped; the allowlist makes that a one-line
   evidence-backed addition rather than a rule change, and the vocabulary test fails if one appears.

## Acceptance state

| required | state |
|---|---|
| `MD` exempted through a committed, provenance-carrying allowlist | **done** (`ncc_roman_catalogue_allowlist.json`) |
| offline run behaves identically (no workbook needed) | **done** (allowlist at import; `--no-roman-allowlist` for the baseline) |
| selftest fails when allowlist and workbook vocabulary disagree | **done** (2 tests: committed artifact, live workbook) |
| re-measure on the workbook lexicon | **done** (1,293 sigla; 2,021 → 2,046 raw; 1,449 → 1,477 distinct) |
| fresh-seed 100-unit adjudication, seed ≥ 20261019 | **done** (20261019, 100 units, 39 volumes, reproducible bytes) |
| precision + Wilson 95 % CI | **done** (86.0 %, [77.863 %, 91.474 %]) |
| false-positive classes counted with examples | **done** (5 classes, 14 units) |
| label-truncation class measured, not assumed | **done** (0/100 vs 11/100 control) |
| own-data canary | **done** (2,355 / 819 / INCONCLUSIVE) |
| explicit GO/HOLD under the locked rule | **HOLD** — 86.0 % < 95 %, Wilson floor 77.863 % < 90 % |

## Delivery (five fields)

- **Changed:** `census_ncc_mss.py` (allowlist, `--dump-vdcs-keys`, `--no-roman-allowlist`,
  `producing_span`/`--enrich-spans`); new `ncc_roman_catalogue_allowlist.json`,
  `ncc_vdcs_catalogue_keys_2026-10-19.json`, `ncc_mss_adjudication_100_seed20261019.tsv` and this
  report; `test_census_ncc_mss.py` 8 → 16 tests.
- **Unchanged:** `ncc.jsonl`, the H6995/H7073 pilot and canary TSVs, `ncc_mss_adjudication_100.tsv`
  (seed 20261018) and `NCC_MSS_ADJUDICATION_100_2026-10-19.md`, `NCC_MSS_PRECISION_100_2026-10-18.md`
  and its locked GO rule, `parse_ncc.py`. The workbook's `mss` column is quoted only in the canary
  comparison; `1,032,077` is not quoted as a census anywhere in this pass; `--full` was not run.
- **Checks:** `python -m pytest -q HeadwordLists/works_catalogue/test_census_ncc_mss.py` → **16
  passed**; `awk` precision line → `S=86 F=14 A=0 precision=0.8600`; the four-cell pilot matrix above
  (1,854/1,290 · 1,882/1,319 · 2,021/1,449 · 2,046/1,477); the seed-20261019 draw byte-identical on a
  second run; the `MD` reproduction prints `['Adyar']` vs `['Adyar', 'MD']`.
- **Risks:** the precision estimate is of the pilot, not the corpus; 14 false positives in five
  classes are all still live in the parser (the `Vol`/page-range cluster alone is 4 and comes from
  one entry); `Details` corroboration is body-derived and cannot break a tie on its own; the canary
  remains a semantic mismatch that precision cannot fix; `AMBIGUOUS` = 0 here does not prove the
  corpus has no undecidable spans at scale.
- **Inspect:** `catalogue_regex()` and the allowlist JSON first, then
  `ncc_mss_adjudication_100_seed20261019.tsv` rows `#27`, `#45`, `#52`, `#56`, `#67`, `#75`, then the
  four-cell matrix.

_Dr. Mārcis Gasūns_
