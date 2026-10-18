# NCC MSS census from bodies — strict witness unit, 500-entry pilot and 20-work canary

_Created: 18-10-2026 · H6995 (DeepSeek v4.1 Flash) · pilot + canary only; full run deliberately withheld_

## Verdict first

The pilot and canary ran, but **the full census is not publishable yet**. Two named
stopping conditions fired:

1. **Skandapurāṇa is absent from the bodies file.** `ncc.jsonl` (152,526 rows, the
   `SkhNewCatalogus`-derived bodies) contains **no IAST title beginning `Sk`** at all
   (also no `Sl`, `Sm`, `Sn`, `So`, `Sr`, `St`). The Skandapurāṇa canary cannot be
   computed from these bodies, so that canary is **INCONCLUSIVE**, not PASS.
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
| Skandapurāṇa | 0 | 0 | **0** | 17 | — | **INCONCLUSIVE (absent from bodies)** |
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
  block is missing from this bodies export. The 17 is therefore unverifiable here, not
  confirmed.

## Why no full run

The pre-registered order is pilot → canary → full. The canary did **not** clear:
Skandapurāṇa is absent, and the two computable canaries disagree in opposite directions
for identifiable reasons. Running the full 152,526-entry census now would ship a number
whose precision is 67 % at best and whose Sk section does not exist. That is a named stop,
not a footnote.

Next gates:

1. Recover the missing `Sk`/`Sl`/`Sm`/`Sn`/`So`/`Sr`/`St` fascicles (or prove the bodies
   export is complete and the titles are filed elsewhere).
2. Add an edition/journal filter and hand-adjudicate 100 pilot units; target ≥95 % precision.
3. Only then run `--full` and publish per-work distinct counts with the strict unit stated.

## Reproduce

```bash
python HeadwordLists/works_catalogue/census_ncc_mss.py \
  --ncc HeadwordLists/works_catalogue/ncc.jsonl \
  --vdcs-details "NCC-mss-counting-1 031 077.xlsx" \
  --pilot 500 --canary
```

The workbook is not committed (rights + size); pass its path explicitly.

## Delivery (five fields)

- **Changed:** new `census_ncc_mss.py`, pilot TSV (500 rows), canary TSV (20 rows), this report.
- **Unchanged:** `ncc.jsonl`, `parse_ncc.py`, the ACC×NCC crosswalk, every existing count.
- **Checks:** pilot 500 entries / 39 volumes / 2,080 distinct units; canary 20 works run;
  `1,032,077` re-derived from the workbook and labelled a workbook total, not a census.
- **Risks:** body parser still admits edition/year refs (67.0 % corroboration); Sk block
  missing; no hand precision audit yet.
- **Inspect:** `ncc_mss_canary_20.tsv` first, then `census_ncc_mss.py:extract_units`.
