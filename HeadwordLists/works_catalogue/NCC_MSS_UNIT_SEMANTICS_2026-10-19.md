# NCC MSS census canary — what a manuscript witness unit is

_Created: 19-10-2026 · H7085 (DeepSeek v4.1 Flash, `deepseek-flash`) · measurement report + decision brief · read-only against corpus and workbook_

Measured on `origin/master` **44fb7fe1** (before H7084's `MD` exemption lands). Parser:
[`census_ncc_mss.py`](census_ncc_mss.py). Workbook:
`VisualDCS/non-derived/NCC/Works-Share-NCC/NCC-mss-counting-1 031 077.xlsx`
(sheet `NCC_mss_counting- 1 032 077`, 140,848 data rows).

## Verdict first

**The locked canary clause is satisfiable only vacuously.** Read literally — *"the
canary re-run with the filter still names both numbers"* — it is already satisfied:
H7080's re-run named Mahābhārata 2,355 and Rāmāyaṇa 814. Read as a validation that the
parser reproduces the workbook, it is **not satisfiable** under any slicing of the
workbook rows, and the reason is measurable: the workbook's `mss` column is not one
object. Its rows are **partial index slices** (the Mahābhārata row records 3 catalogues;
the bodies name 121) and, where complete, count **catalogue page ranges as manuscripts**
(Rāmāyaṇa's `Bṛhatsūcī, Nepal: 427` comes from `p. 132-150`). A union of all rows
corrects a real defect — the current code compares the body's union across entries to
the *first* workbook row — but it closes only **381 of the 1,948-unit Rāmāyaṇa gap** and
**0 of the 2,334-unit Mahābhārata gap**.

**Decision.** The census publishes under the **printed-reference unit**: one distinct
`(catalogue, printed reference)` pair per body, catalogue ranges expanded. It is the only
definition computable from the corpus we hold, and the workbook is comparison only — its
`mss` column is never an answer and its total is never a census. The locked GO rule is
**not edited**; a versioned amendment for human ratification is
[`NCC_MSS_UNIT_SEMANTICS_PROPOSAL_V2_2026-10-19.md`](NCC_MSS_UNIT_SEMANTICS_PROPOSAL_V2_2026-10-19.md).

No precision claim is made here; the precision gate stands where H7080 left it (HOLD).

## 1. The two candidate unit definitions

**Definition A — printed-reference unit (the parser, `census_ncc_mss.extract_units`).**
One unit is a distinct `(catalogue, reference)` pair printed in an NCC body:
`Bikaner 851-946` is 96 units (851…946); `MD. 1915-53` is 39; `Bṛhatsūcī, Nepal II.
p.. 132-150 … 151` is 1 (a page range is not an accession and is skipped; `151` is).
The unit is "what the entry prints as a reference to a manuscript", not "the
catalogue's stated manuscript total".

**Definition B — workbook declared `mss` (the current canary's cell).**
One workbook row is one NCC entry (`id` == `ncc_numid`); its `mss` is the sum of the
per-catalogue counts the row's `Details` records, where a range counts as its size and
a catalogue page range counts as the number of manuscripts it estimates. The current
reader ([`census_ncc_mss.py:434-473`](census_ncc_mss.py)) takes the **first row whose
IAST equals the label exactly** and reads its `mss` cell. It reads only four labels
(`Mahābhārata`, `Rāmāyaṇa`, `Skandapurāṇa`, `Bhāgavata`); the other 16 canary works are
reported `COMPARED (no VisualDCS canary)` even where the workbook has rows for them.

**Definition B′ — union of all rows.** The same declared `mss` summed over every row of
the work (the handoff's *union-of-all-rows*). **Definition B″ — enumerated union.** The
distinct `(catalogue, accession)` pairs actually listed in the rows' `Details` braces,
ranges expanded — the only workbook number whose *unit* is the parser's.

### Worked examples

| # | body text | parser (A) | workbook (B / B″) | why they differ |
|---|---|---|---:|---|
| 1 | Mahābhārata: `Bikaner 851-946`, `MD. 1915-53`, `RORI III. A. 1346-98` | 2,355 | 21 / 21 | workbook row lists `Bikaner: 9 {78327 1636 72470 181 73441 5862-63 441 1039}` — **accession numbers**; the body prints **serial ranges**. The row covers 3 catalogues; the body names **121**. |
| 2 | Rāmāyaṇa: `Bṛhatsūcī, Nepal II. p.. 132-150 (one text). 151` | 814 | 2,762 / 2,381 | workbook chunk `Bṛhatsūcī, Nepal: 427` — a **catalogue page-range total**; the brace list enumerates 387 and the body yields 7 for that catalogue. 27 catalogues in the row vs **128** in the body. |
| 3 | Vājasaneyisaṃhitā: enumerated accessions on both sides | 762 | 776 / 624 | **control**: one complete row, 13 catalogues, body enumerates the same accessions → 1.8 % agreement. |
| 4 | Rāmāyaṇa: `Adyar I. p. 122a (15 mss.; 4 inc.)` | 0 | counted in the catalogue total | page reference plus a parenthetical count: no printed accession. |
| 5 | Mahābhārata: `MD. 1915-53` | 39 | 19 (`MD.`) | serial range vs enumerated accession list. |

The two numbers in each epic are therefore **not two measurements of one quantity**.
They are a printed-reference count and a catalogue-level manuscript estimate, and the
workbook mixes both kinds of row.

## 2. The canary computed both ways

Canonical table (all 20 canary works, plus the control pool) is
[`ncc_mss_unit_semantics_2026-10-19.tsv`](ncc_mss_unit_semantics_2026-10-19.tsv);
machine summary [`ncc_mss_unit_semantics_2026-10-19.json`](ncc_mss_unit_semantics_2026-10-19.json).

### The four named works

| work | body A | B first (current) | B′ sum of rows | B″ enumerated union | A−B | A−B′ | A−B″ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mahābhārata | 2,355 | 21 | 21 | 21 | +2,334 | +2,334 | +2,334 |
| Rāmāyaṇa | 814 | 2,762 | 2,799 | 2,381 | −1,948 | −1,985 | −1,567 |
| Bhāgavata | 5,472 | 2,248 | 2,250 | 2,259 | +3,224 | +3,222 | +3,213 |
| Skandapurāṇa | 0 | 17 | 17 | 17 | −17 | −17 | −17 |

Reading:

- **Mahābhārata**: one workbook row, so the union-of-all-rows is identical. The
  "current code compares a union to a single cell" defect contributes **0** here.
- **Rāmāyaṇa**: eight rows; the exact-row cell is the large one (2,762), the union of
  declared counts is 2,799 (worse), the enumerated union is 2,381 (−381). The union
  correction closes **19.6 %** of the gap; **80.4 % remains**.
- **Bhāgavata**: three rows; the exact-row cell is the large one (2,248), the union adds
  11 enumerated units. The union correction closes **0.3 %**.
- **Skandapurāṇa**: absent from the bodies; the 17 is unverifiable (H7078).

The direction pattern H7070/H7073 described — "disagree in opposite directions" — is
reproduced and explained: **Mahābhārata's body over-counts a workbook row that lists
accessions for 3 of 121 catalogues; Rāmāyaṇa's body under-counts a workbook row that
counts page ranges for 27 catalogues.** The pattern tracks what each side is able to
count — complete enumeration versus partial coverage, serial ranges versus page-range
totals — not the number of catalogues in which the work happens to be dispersed.

### The 16 other canary works (a row exists in the workbook)

Summing the declared `mss` over all rows changes the comparison materially only where
the work has several substantial rows — Śivapurāṇa 470 → **775** (A−B −81 → −386),
Padmapurāṇa 361 → **450**, Rāmāyaṇa 2,762 → **2,799** — and not at all for the epic with
a single row. See the TSV for all 20.

## 3. Controls: where the method can pass

Control rule, stated before use: **a work with exactly one workbook row, declared
`mss` ≥ 500, and ≥ 100 body units** — the row-slicing question is moot, only the unit
question remains. Pool: the 200 works with the largest workbook `mss` sum (head of the
index; not a census run). **102 works match the rule; 4 agree within ±5 %:**

| control | body A | workbook B | delta | rel. |
|---|---:|---:|---:|---:|
| Vājasaneyisaṃhitā | 762 | 776 | −14 | 1.8 % |
| Vṛttaratnākara | 710 | 687 | +23 | 3.2 % |
| Chāndogyopaniṣad | 561 | 537 | +24 | 4.3 % |
| Mārkaṇḍeyapurāṇa | 565 | 593 | −28 | 4.7 % |

**4 of 102 = 3.9 %.** The controls prove the pipeline *can* reproduce a workbook figure
when the row is a complete enumeration; they also show that this is the exception. Under
the enumerated-union definition the agreeing set is different (2 of 102: Muṇḍakopaniṣad,
Manusmṛti) — **no single workbook column is a stable comparator across works.**

## 4. Which definition the census publishes under, and its numbers

**Printed-reference unit (A).** Reasons: it is the pre-registered unit ("strict witness
unit `(catalogue, accession)`", H6995) and the only one computable from the corpus we
hold; the workbook's declared count is a catalogue-level estimate that cannot be turned
into distinct references without a catalogue concordance we do not have.

Under A, the canary's numbers are the body column: **Mahābhārata 2,355 · Rāmāyaṇa 814 ·
Bhāgavata 5,472 · Skandapurāṇa 0 (absent)**. The delta to each workbook definition is the
table in §2. The **total census number is not computed** — no `--full` run, by
constraint — and is not this handoff's output.

## 5. Ruling on the locked clause

The locked GO rule
([`NCC_MSS_PRECISION_100_2026-10-18.md`](NCC_MSS_PRECISION_100_2026-10-18.md)) reads:

> point precision ≥ 95 % **and** Wilson 95 % lower bound ≥ 90 % **and**
> `AMBIGUOUS ≤ 10` **and** the canary re-run with the filter names both Mahābhārata and
> Rāmāyaṇa numbers. HOLD otherwise.

- **Literal reading** — *names* both numbers: **satisfiable and already satisfied**
  (2,355 / 814). Nothing to amend; H7080's table already records "both named".
- **Substantive reading** — the canary validates that the body count reproduces the
  workbook: **not satisfiable**. Three measured reasons: (i) rows are partial index
  slices (Mahābhārata 3 catalogues vs 121); (ii) where complete they count page ranges
  as manuscripts (Rāmāyaṇa 2,762); (iii) the units are different layers (accession vs
  serial). The union-of-all-rows repair closes 19.6 % of the Rāmāyaṇa gap and 0 % of the
  Mahābhārata gap.
- **Consequence**: the clause as written is **vacuous** as a validation. It must not be
  treated as evidence that the parser tracks the workbook. This report does not edit it;
  the amendment is put to a human as a versioned proposal (§6).

## 6. Versioned proposal (for human ratification — NOT in force)

[`NCC_MSS_UNIT_SEMANTICS_PROPOSAL_V2_2026-10-19.md`](NCC_MSS_UNIT_SEMANTICS_PROPOSAL_V2_2026-10-19.md)
— `v2-2026-10-19`. In one line: **demote the canary from a gate to a reported
diagnostic**: the re-run must name both epic numbers, the four positive controls with
their deltas, and Skandapurāṇa as absent; the GO gate stays precision-based. The locked
v1 rule remains in force until a human ratifies v2.

## 7. Constraints honoured

- **Read-only** against `ncc.jsonl` and the workbook; no corpus or workbook byte written.
- **No `--full` run**; the control pool is a bounded head-of-index slice (top 200 by
  workbook `mss`), not a census.
- **Workbook `mss` comparison only**; no count copied as an answer; `1,032,077` is not
  quoted as a census.
- **No precision claims**; the precision gate is unchanged and still HOLD per H7080.
- **Locked GO rule untouched**; the proposal is a separate dated file.

## 8. Evidence and reproduce

```bash
cd HeadwordLists/works_catalogue
python ncc_mss_unit_semantics.py --selftest
python ncc_mss_unit_semantics.py \
  --ncc ncc.jsonl \
  --workbook "$HOME/Documents/GitHub/VisualDCS/non-derived/NCC/Works-Share-NCC/NCC-mss-counting-1 031 077.xlsx"
```

Outputs: the TSV above (20 canary rows + 102 control rows), the JSON summary, and the
`selftest` assertions for range expansion and `Details` enumeration.

## Delivery (five fields)

- **Changed:** new `ncc_mss_unit_semantics.py`, its selftest, its TSV + JSON outputs,
  this report and the v2 proposal.
- **Unchanged:** `ncc.jsonl`, the workbook, `census_ncc_mss.py`, the committed pilot and
  canary TSVs, the H6995 report, the locked GO rule, every existing count.
- **Checks:** `--selftest` OK; full run 23 s; 20 canary works + 102 control works; 4/102
  controls within ±5 %.
- **Risks:** the workbook reader takes the first exact-label row (title-variant
  sensitive); the control rule is a selection rule, disclosed; the parser's own false
  positives are unmeasured here (H7080/H7084 own precision).
- **Inspect:** the §2 four-work table first, then `details_units()` and
  `_wb_aggregate()` in the tool, then the TSV.
