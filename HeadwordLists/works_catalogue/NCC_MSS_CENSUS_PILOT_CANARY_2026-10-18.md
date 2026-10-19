# NCC MSS census from bodies — strict witness unit, 500-entry pilot and 20-work canary

_Created: 18-10-2026 · Last updated: 19-10-2026 (H7078, gate 1 — Skandapurāṇa canary reason now measured) · H6995 (DeepSeek v4.1 Flash) · pilot + canary only; full run deliberately withheld_

## Verdict first

The pilot and canary ran, but **the full census is not publishable yet**. Two named
stopping conditions fired:

1. **Skandapurāṇa is absent from the bodies file — and the block is not recoverable
   from the 2022 database either (settled 19-10-2026, H7078).** `ncc.jsonl` (152,526
   rows) carries **no** `स्क`/`Sk` title. Gate 1 asked whether the fascicles sit in the
   bundled 2022 NCC desktop database
   ([`ncc.rar`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/NCC/files/ncc/ncc.rar))
   but were dropped from the export. They do not: the archive holds **zero** `स्क`/`Sk`
   titles across all seven of its title tables, and the export carries exactly the same
   records, titles and order as it — 152,526 records, identical `vol_page_col_seq`
   **sets and order**, 0 rows either way, **0** titles differing (bodies differ in 26
   records, where the archive *truncates* and the export is the fuller source) — so the
   gap is the database's, not the
   export's. Records run in catalogue order to vol 39 p. 378 (`सुहोदित · Suhodita`),
   the database's frontier. The canary therefore stays **INCONCLUSIVE**, now with a
   measured reason instead of an open question. Proof:
   [`NCC_SK_BLOCK_COVERAGE_2026-10-19.md`](https://github.com/gasyoun/VisualDCS/blob/main/reports/NCC_SK_BLOCK_COVERAGE_2026-10-19.md).
   Prefix note from the same measurement: `Sm`/`So`/`Sr` are empty as *printed*
   prefixes but three titles are printed parenthetical-first
   (`(स्मृति)_रत्नमञ्जूषा`, `(सोसले)_रेवणाराध्य`, `(स्री)सागरसेन`) and reach
   those letters only after normalization; `St` holds exactly one entry — the junk
   title `Study.`
2. **Naive body parsing still over-counts edition/page references.** Only 67.0 % of
   pilot units have their accession literal in the VisualDCS `Details` string for the
   same entry (after range expansion). The rest include journal/year references such as
   `JPTS 1890`, `JRAS 1911`, `Series 51`.

Never publish **1,032,077** as a census. That number is the sum of the `mss` column over
all 140,848 rows of `NCC-mss-counting-1 031 077.xlsx` (verified in this pass), including
`Author` / `Commentary` rows and catalogue page-range serials. It is a workbook total,
not a distinct-manuscript count.

## Strict witness unit and method

The shipped `ncc.jsonl` `mss_witnesses` field cannot be the census base: `parse_ncc.py`
only matches `Abbrev. 123`, so it drops `Bikaner 1042-48`, `Adyar D. XIII. 899. 902.`,
`Bodl. Sup. 39-41` and most prose witnesses.

`census_ncc_mss.py` (this directory) re-reads `body_html`:

- catalogue lexicon = sigla already visible in `mss_witnesses` **plus** the catalogue keys
  of the VisualDCS workbook (used only as an abbreviation table; no count is copied);
- after each catalogue mention, harvest only the immediate prefix of roman volume markers,
  accession numbers, ranges, page refs and punctuation; the first ordinary word ends the
  list (keeps `New Delhi, 1991` and `ed. by …` out);
- expand `1042-48` the catalogue way (→ 1042…1048);
- normalise and dedupe on `(catalogue, accession)`; a unit is one strict witness.

## Pilot — 500 entries, stratified by volume

Systematic sample over rows sorted by `(volume, ncc_id)`; all 39 volumes represented.

| metric | value |
|---|---:|
| entries sampled | 500 |
| catalogue mentions matched | 2,268 |
| raw witness units | 2,143 |
| **distinct witness units** (strict dedupe) | **2,080** |
| entries with no extracted witness | 153 (30.6 %) |
| volumes represented | 39 |

Artifact: [`ncc_mss_census_pilot_500.tsv`](ncc_mss_census_pilot_500.tsv).

### Corroboration audit (proxy, not hand adjudication)

For each pilot unit, the accession literal was looked up in the VisualDCS `Details`
string of the same `ncc_numid`, after expanding its ranges:

- **1,345 / 2,006 = 67.0 % corroborated**
- 661 uncorroborated; spot inspection shows both real catalogue misses and clear false
  positives from edition/journal references: `Udāna — JPTS 1890`, `Udāna — JRAS 1911`,
  `Anavalobhanamantra — Bk 1938`, `Adhyātmopadeśa — Series 51`.

**Precision is therefore unverified at the level a census needs.** A 100-unit hand
adjudication is the next gate.

## 20-work canary (18 Mahāpurāṇas + Mahābhārata + Rāmāyaṇa)

VisualDCS values are the exact-row `mss` cells of the workbook; body values are strict
distinct units from this pass.

| work | body entries | body raw units | **body distinct** | VisualDCS `mss` | delta | status |
|---|---:|---:|---:|---:|---:|---|
| Mahābhārata | 1 | 2,585 | **2,519** | 21 | +2,498 | DIFF |
| Rāmāyaṇa | 10 | 1,097 | **1,006** | 2,762 | −1,756 | DIFF |
| Skandapurāṇa | 0 | 0 | **0** | 17 | — | **INCONCLUSIVE (absent from bodies; `स्क` block absent from the 2022 NCC DB, H7078)** |
| Bhāgavata | 4 | 16,560 | **6,699** | 2,248 | +4,451 | DIFF |
| Viṣṇupurāṇa | 3 | 1,018 | **839** | — | — | compared |
| Nāradapurāṇa | 1 | 44 | **43** | — | — | compared |
| Garuḍapurāṇa | 1 | 295 | **280** | — | — | compared |
| Padmapurāṇa | 2 | 392 | **389** | — | — | compared |
| Varāhapurāṇa | 1 | 473 | **441** | — | — | compared |
| Matsyapurāṇa | 1 | 441 | **417** | — | — | compared |
| Kūrmapurāṇa | 3 | 135 | **132** | — | — | compared |
| Liṅgapurāṇa | 1 | 316 | **302** | — | — | compared |
| Śivapurāṇa | 5 | 572 | **524** | — | — | compared |
| Agnipurāṇa | 1 | 123 | **123** | — | — | compared |
| Bhaviṣyapurāṇa | 2 | 223 | **218** | — | — | compared |
| Brahmavaivartapurāṇa | 1 | 447 | **411** | — | — | compared |
| Mārkaṇḍeyapurāṇa | 1 | 935 | **856** | — | — | compared |
| Vāmanapurāṇa | 2 | 199 | **191** | — | — | compared |
| Brahmāṇḍapurāṇa | 2 | 2,270 | **1,435** | — | — | compared |
| Vāyupurāṇa | 1 | 292 | **289** | — | — | compared |

Artifact: [`ncc_mss_canary_20.tsv`](ncc_mss_canary_20.tsv).

### Reading the three named canaries

- **Mahābhārata 21 → 2,519.** The workbook row is 3 catalogues / 21 serials; the body
  text lists thousands of accessions (`TD`, `VI`, `II`, `Bikaner`, `America`, …). 21 is
  **not** a Mahābhārata MSS count.
- **Rāmāyaṇa 2,762 → 1,006.** The workbook value counts catalogue **page ranges**
  (e.g. `Bṛhatsūcī, Nepal II. p.. 132-150` → 427) as manuscripts. That is the inflation
  mechanism, and it is why the workbook total (1,032,077) must never be published.
- **Skandapurāṇa 17 → INCONCLUSIVE.** No body entry exists in `ncc.jsonl`; the letter
  block is missing from this bodies export. H7078 (gate 1, 19-10-2026) then showed the
  block is missing from the bundled **2022 database itself** and that the export carries
  the same records, titles and order (bodies differ in 26) — so this is not an export
  defect awaiting re-extraction.
  The 17 is unverifiable here, not confirmed, and stays unverifiable until an NCC
  fascicle past vol 39 p. 378 (or a newer database export) arrives.

> **Unit semantics settled (19-10-2026, H7085).** The body count and the workbook `mss`
> are not one quantity: the workbook row is a partial index slice (Mahābhārata 3
> catalogues vs 121 in the bodies) and counts catalogue page ranges as manuscripts
> (Rāmāyaṇa `Bṛhatsūcī, Nepal: 427` from `p. 132-150`). Union-of-all-rows closes 19.6 %
> of the Rāmāyaṇa gap and 0 % of the Mahābhārata gap. See
> [NCC_MSS_UNIT_SEMANTICS_2026-10-19.md](NCC_MSS_UNIT_SEMANTICS_2026-10-19.md) and the
> v2 proposal.

## Why no full run

The pre-registered order is pilot → canary → full. The canary did **not** clear:
Skandapurāṇa is absent, and the two computable canaries disagree in opposite directions
for identifiable reasons. Running the full 152,526-entry census now would ship a number
whose precision is 67 % at best and whose Sk section does not exist. That is a named stop,
not a footnote.

Next gates:

1. ~~Recover the missing `Sk`/`Sl`/`Sm`/`Sn`/`So`/`Sr`/`St` fascicles (or prove the bodies
   export is complete and the titles are filed elsewhere).~~ **Closed 19-10-2026 (H7078).**
   The export *is* complete and the bundled 2022 database does not hold the block, so
   recovery is no longer an analysis on our data — it needs an acquisition: an NCC
   fascicle past vol 39 p. 378, or a current NCC database export to re-run
   [`tools/ncc_sk_block_probe.py`](https://github.com/gasyoun/VisualDCS/blob/main/tools/ncc_sk_block_probe.py).
   The `St` half of this gate was never a gap: the single `St` entry is `Study.`, a junk
   title, and `Sm`/`So`/`Sr` are empty only as printed prefixes (three parenthetical-first
   titles reach them after normalization).
2. Add an edition/journal filter and hand-adjudicate 100 pilot units; target ≥95 % precision.
3. Only then run `--full` and publish per-work distinct counts with the strict unit stated.

## Reproduce

```bash
python HeadwordLists/works_catalogue/census_ncc_mss.py \
  --ncc HeadwordLists/works_catalogue/ncc.jsonl \
  --vdcs-details "NCC-mss-counting-1 031 077.xlsx" \
  --pilot 500 --canary
```

The workbook is not committed (rights + size) — it is tracked in VisualDCS at
`non-derived/NCC/Works-Share-NCC/NCC-mss-counting-1 031 077.xlsx`; pass its path explicitly.

> **Caveat (19-10-2026, H7078).** This command no longer reproduces the committed
> [`ncc_mss_canary_20.tsv`](ncc_mss_canary_20.tsv) numbers, and that is pre-existing, not
> a regression from gate 1: H7073 made the edition/journal filter default-on inside
> `extract_units`, which `run_canary()` does not parameterise, so a fresh run measures the
> post-filter figure (Mahābhārata 2,585 → 2,457 with the workbook, 1,922 without) while
> the committed table is the pre-filter one. Gate 1 therefore **carried the 18-10-2026
> numbers unchanged** and edited only the `Skandapurāṇa` status cell; no count was
> recomputed. Reconciling the two baselines belongs to H7073's own gate, not here.

## Delivery (five fields)

- **Changed:** new `census_ncc_mss.py`, pilot TSV (500 rows), canary TSV (20 rows), this report.
- **Unchanged:** `ncc.jsonl`, `parse_ncc.py`, the ACC×NCC crosswalk, every existing count.
- **Checks:** pilot 500 entries / 39 volumes / 2,080 distinct units; canary 20 works run;
  `1,032,077` re-derived from the workbook and labelled a workbook total, not a census.
- **Risks:** body parser still admits edition/year refs (67.0 % corroboration); Sk block
  missing; no hand precision audit yet.
- **Inspect:** `ncc_mss_canary_20.tsv` first, then `census_ncc_mss.py:extract_units`.
