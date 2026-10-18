# NCC MSS precision gate — 100-unit adjudication, H7073

_Created: 18-10-2026 · H7073 (DeepSeek v4.1 Flash) · edition filter shipped; adjudication **handed off** — workbook absent_

## Verdict first

**HOLD** for the full 152,526-entry census.

The edition/journal filter is implemented and committed, and the seeded 100-unit
draw re-draws identically. The **hand adjudication did not run on this launch box**
because the corroboration workbook
`VisualDCS/non-derived/NCC/Works-Share-NCC/NCC-mss-counting-1 031 077.xlsx` is
absent. H7073's own fallback says: *if it is absent, commit the filter + a
reproduced pilot-table delta and hand off the adjudication — do not substitute
the workbook counts.* That is what this pass did. No precision figure is quoted:
without the 100 hand verdicts there is nothing to put a Wilson interval around.

A GO is impossible in this state for three independent reasons: the 100 verdict
rows do not exist, the Skandapurāṇa canary is still **INCONCLUSIVE**, and the
post-filter body counts still disagree with the VisualDCS canary rows for both
Mahābhārata and Rāmāyaṇa in opposite directions.

## What changed

`census_ncc_mss.py` now removes the four measured non-accession classes before a
unit is emitted:

| class | rule | pilot removals (raw units) |
|---|---|---:|
| roman volume marker | roman-only sigla are dropped from the catalogue regex (67 of 991 sigla); their numbers are re-attached to the preceding real catalogue instead of minting a phantom unit | not counted as units — 67 sigla excluded |
| journal/series | `JPTS`, `JRAS`, `RASB`, `BBRAS`, `Bk`, `Ser(ies)`, `J.`, `Extr`, `Rep` | 452 |
| year-like | a 4-digit year followed by a year list or page ref (`1890, 91`, `1890, p. 12`) | 57 |
| page/volume prefix | the catalogue is followed by `p.`, `pp.`, `pt.`, `vol.` or `no.` before any number | 19 |
| **total** | | **528** |

The roman-sigla fix matters beyond counting: keeping `IV` as a catalogue match
ended the preceding catalogue's segment before its accession, so `Adyar D. IV.
950` lost 950. Dropping roman sigla from the regex returns 950 to `Adyar D.`.

New CLI: `--adjudication-sample N --seed <int>` draws the volume-stratified
sample; `--no-edition-filter` reproduces the pre-filter baseline. The sampler
writes `verdict` / `reason` **empty** — it draws the sample, it does not
adjudicate it.

## Pilot delta (500 entries, 39 volumes)

Same parser, same lexicon, only the filter toggled:

| metric | pre-filter | post-filter |
|---|---:|---:|
| catalogue mentions | 1,648 | 1,648 |
| raw witness units | 1,854 | 1,854 harvested → **1,326 kept** |
| per-entry distinct units | 1,809 | **1,290** |
| entries with no unit | 202 | 237 |
| volumes represented | 39 | 39 |

Reproduce with:

```bash
python census_ncc_mss.py --ncc ncc.jsonl --pilot 500 --no-edition-filter --out-dir /tmp/h7073
python census_ncc_mss.py --ncc ncc.jsonl --pilot 500 --out-dir /tmp/h7073
```

The committed post-filter pilot table is
[`ncc_mss_census_pilot_500_post_filter.tsv`](ncc_mss_census_pilot_500_post_filter.tsv);
the machine-readable delta is
[`ncc_mss_filter_delta_2026-10-18.json`](ncc_mss_filter_delta_2026-10-18.json).

**This is not a reproduction of the published pilot's 2,080.** Without the
workbook the abbreviation lexicon is 991 sigla (924 after dropping roman
volumes); H6995's run used the workbook's catalogue keys as well. The baseline
here is therefore 1,809 per-entry distinct units, not 2,080. The delta above is
the filter's effect on the same no-workbook baseline; the missing-workbook gap
is a separate, named unknown.

## Sample design (locked, ready for the follow-up)

- Source: the same 500 pilot entries as H6995 (`pilot_sample`, systematic over
  `(volume, ncc_id)`), post-filter units only.
- Stratification: all 39 volumes, proportional allocation with a floor of 2 per
  volume, capped by supply; the 100 draw reaches **39 volumes** (volume 23
  supplies one unit; every other volume supplies at least two).
- Seed: **20261018**. Re-draw is byte-identical.
- `source_span`: 80 characters before and 160 after the catalogue mention, from
  the cleaned `body_html`.
- Verdict vocabulary (locked before any verdict row): `SUPPORTED` ·
  `FALSE_POSITIVE` · `AMBIGUOUS`; precision = `SUPPORTED ÷ (SUPPORTED +
  FALSE_POSITIVE)`, `AMBIGUOUS` excluded and reported separately.
- GO rule (locked): point precision ≥ 95 % **and** Wilson 95 % lower bound ≥ 90 %
  **and** `AMBIGUOUS ≤ 10` **and** the canary re-run with the filter names both
  Mahābhārata and Rāmāyaṇa numbers. HOLD otherwise.

Draw command:

```bash
python census_ncc_mss.py --ncc ncc.jsonl --adjudication-sample 100 \
  --seed 20261018 --adjudication-out ncc_mss_adjudication_100.tsv
```

The draw was verified locally (`100` data rows, 38 volumes, seed echoed); the
`verdict` and `reason` columns are deliberately blank and **no
`ncc_mss_adjudication_100.tsv` is committed**.

## Precision

**Not computed.** Precision needs 100 hand verdicts; the file that would carry
them does not exist. Quoting a point estimate or a Wilson interval from the
parser's own labels would be the exact failure H7073 forbids ("units
auto-labelled by the same parser instead of read"). The VisualDCS `Details`
corroboration — the second opinion the method asks for — is also unavailable
with the workbook absent.

## Canary after the filter (own data)

Body counts are strict distinct units after the filter. VisualDCS values are the
exact-row `mss` cells recorded by H6995 and reproduced in the committed
[`ncc_mss_canary_20.tsv`](ncc_mss_canary_20.tsv); they are comparison only.

| work | body units (post-filter) | VisualDCS `mss` | delta | status |
|---|---:|---:|---:|---|
| Mahābhārata | 1,798 | 21 | +1,777 | DIFF |
| Rāmāyaṇa | 668 | 2,762 | −2,094 | DIFF |
| Skandapurāṇa | 0 | 17 | — | **INCONCLUSIVE (absent from bodies)** |

The filter narrows both epics substantially (Mahābhārata 2,519 → 1,798;
Rāmāyaṇa 1,006 → 668 in the committed H6995 canary), but the two computable
canaries still disagree in opposite directions and Skandapurāṇa is still absent.
Both canary conditions in the locked GO rule remain unmet.

## Inputs

| input | state |
|---|---|
| `ncc.jsonl` (152,526 bodies) | present, committed |
| `ncc_mss_census_pilot_500.tsv` | present, committed |
| `census_ncc_mss.py` | present, filter added |
| `ncc_mss_canary_20.tsv` | present, committed |
| VisualDCS counting workbook | **ABSENT on this launch box** — adjudication handed off |

No count from the workbook is used or substituted. `--full` was not run, and
the workbook total is never quoted as a census.

## Acceptance state

| required | state |
|---|---|
| filter committed in `census_ncc_mss.py` + raw → post-filter delta | **done** |
| seeded, stratified sampler committed | **done** (`--adjudication-sample`, seed 20261018) |
| `ncc_mss_adjudication_100.tsv` (100 hand verdicts) | **NOT DONE** — workbook absent |
| precision + Wilson 95 % CI | **NOT COMPUTED** — no verdicts |
| explicit GO/HOLD | **HOLD** |
| canary after filter | Mahābhārata 1,798 vs 21; Rāmāyaṇa 668 vs 2,762; Skandapurāṇa INCONCLUSIVE |

## Delivery (five fields)

- **Changed:** `census_ncc_mss.py` (edition/journal filter, roman-sigla fix,
  seeded stratified sampler, baseline toggle); new `test_census_ncc_mss.py`
  (8 tests); post-filter pilot table; filter-delta JSON; this report.
- **Unchanged:** `ncc.jsonl`, the committed pilot and canary TSVs, the H6995
  report, `parse_ncc.py`; no workbook count and no `--full` output.
- **Checks:** `python -m pytest -q HeadwordLists/works_catalogue/test_census_ncc_mss.py`
  → 8 passed; pilot 500 baseline 1,854 raw / 1,809 distinct → post-filter 1,326
  / 1,290; sampler 100 rows, 38 volumes, seed 20261018; canary re-run recorded
  above.
- **Risks:** the no-workbook lexicon (924 sigla) is narrower than H6995's; the
  filter may still leave non-accession refs (e.g. scholar-name editions such as
  `Fausboll 148`) that only hand adjudication can classify. The 100 verdicts and
  the Wilson interval remain the gate.
- **Inspect:** `census_ncc_mss.py:edition_reference_reason` and
  `catalogue_regex` first, then the delta JSON and `test_census_ncc_mss.py`.
