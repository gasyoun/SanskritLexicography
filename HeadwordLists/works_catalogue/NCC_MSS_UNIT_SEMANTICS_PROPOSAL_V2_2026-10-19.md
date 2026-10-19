# Proposal v2-2026-10-19 — amend the NCC MSS canary clause

_Proposed: 19-10-2026 · H7085 (DeepSeek v4.1 Flash, `deepseek-flash`) · **RATIFIED 19-10-2026 by MG** · in force from 19-10-2026_

This is a versioned proposal to amend **one clause** of the locked GO rule in
[`NCC_MSS_PRECISION_100_2026-10-18.md`](NCC_MSS_PRECISION_100_2026-10-18.md). That rule
was locked before results and is immutable after them; **this file does not edit it**,
and v1's text remains the historical lock; v2 was ratified on 19-10-2026 (see Ratification below).

## The clause in v1 (verbatim, unchanged)

> GO rule (locked): point precision ≥ 95 % **and** Wilson 95 % lower bound ≥ 90 % **and**
> `AMBIGUOUS ≤ 10` **and** the canary re-run with the filter names both Mahābhārata and
> Rāmāyaṇa numbers. HOLD otherwise.

## Why it needs amendment

The canary clause is satisfiable only **vacuously**. "Names both numbers" is already
true (H7080: Mahābhārata 2,355 · Rāmāyaṇa 814; H7084 post-`MD`: 2,355 · 819), yet both
numbers disagree with the
workbook by 112× in one direction and 0.30× in the other. The measurement in
[`NCC_MSS_UNIT_SEMANTICS_2026-10-19.md`](NCC_MSS_UNIT_SEMANTICS_2026-10-19.md) shows
that no slicing of the workbook rows can make the epics agree:

- the workbook's Mahābhārata row records **3 catalogues** while the bodies name **121**;
- the workbook's Rāmāyaṇa row counts a catalogue **page range** as manuscripts
  (`Bṛhatsūcī, Nepal: 427` from `p. 132-150`);
- union-of-all-rows closes **19.6 %** of the Rāmāyaṇa gap and **0 %** of the
  Mahābhārata gap;
- controls exist but are rare — **3 of 102** single-row works in the head of the index
  agree within ±5 %.

Leaving the clause as a gate therefore does one of two dishonest things: it passes
vacuously, or it forces the parser to reproduce a catalogue-level estimate it cannot
compute.

## Proposed amendment (v2-2026-10-19) — replacement text for the canary clause only

> **Canary (v2, 19-10-2026).** The canary re-run after the edition/journal filter must
> name, in one table: (a) the Mahābhārata and Rāmāyaṇa body counts; (b) the three
> positive controls — Vājasaneyisaṃhitā, Chāndogyopaniṣad, Mārkaṇḍeyapurāṇa — each
> with the workbook `mss` cell, the body count and the delta;
> (c) Skandapurāṇa as **absent** (block missing from the 2022 NCC database, H7078). The
> canary is a **reported diagnostic, not a gate**. The three controls must agree within
> ±5 %; the two epics are reported as measured exceptions and are **not** required to
> agree. No workbook `mss` value is a census denominator.

The precision conditions are **unchanged**: point precision ≥ 95 %, Wilson 95 % lower
bound ≥ 90 %, `AMBIGUOUS ≤ 10`, measured on a pre-declared fresh seed.

## What this amendment does and does not do

- **Does:** makes the canary honest (reports what the workbook can and cannot measure);
  keeps a positive-control check; removes the requirement that the parser reproduce a
  quantity the workbook does not hold.
- **Does not:** weaken the precision gate; touch the locked v1 text; change the census
  unit (printed-reference); authorise `--full`; make the workbook a census source; or
  quote the workbook total.

## Evidence

| claim | evidence |
|---|---|
| epics cannot be reconciled by row slicing | §2 table, `ncc_mss_unit_semantics_2026-10-19.tsv` |
| workbook rows are partial | Mahābhārata row 3 catalogues vs body 121; Rāmāyaṇa 27 vs 128 |
| page ranges inflate the workbook | `Bṛhatsūcī, Nepal: 427` vs 387 enumerated / 7 in body |
| controls exist but are rare | 3 of 102 single-row works within ±5 % |
| union repair is small | Rāmāyaṇa −381 of −1,943 (19.6 %); Mahābhārata 0 |

Reproduce with the commands in the report's §8.

## Ratification path

1. Human reads this proposal and the report.
2. Either **ratify v2** (then and only then does it replace the canary clause; record the
   ratification date in the GO rule's change log, not by editing the locked text), or
   **reject** (v1 stays, and the canary stays a vacuous pass — recorded as such).
3. H7084's fresh-seed re-measure and this decision are independent; a GO still requires
   the precision conditions.

## Ratification

**Ratified 19-10-2026 by Dr. Mārcis Gasūns (MG).** In force from the ratification
date. v2 replaces the v1 canary clause; the precision conditions are unchanged. The
ratification is recorded in the GO rule's append-only change log
([`NCC_MSS_PRECISION_100_2026-10-18.md`](NCC_MSS_PRECISION_100_2026-10-18.md)), not by
editing the locked v1 text.
