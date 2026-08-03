# Glyph quarantine sample — 200 of 10881 (report only)

_Created: 01-08-2026 · Last updated: 03-08-2026_

**Model:** Grok 4.5 (`grok-4.5`) · offline Sonnet-tier batch · **no re-translate**

## Ruling

Sample-first before mass re-translate (MG 29-07-2026 weekly @DECIDE). Quarantine is a segmentation/sense-count flag, not a gold RU defect label.

## Method

- Population: [`reports/pwg_ru_glyph_quarantine.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pwg_ru_glyph_quarantine.jsonl) (10881 rows).
- Sample size: **200** (seed=20260801), stratified by SHA-256(`key1`) mod 10 round-robin.
- Join: optional [`pwg_sense_glyph_audit.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pwg_sense_glyph_audit.json) per-key1 sense-count deltas.
- Script: [`src/sample_glyph_quarantine.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sample_glyph_quarantine.py).

## Results

| Metric | Value |
|---|---:|
| Population | 10881 |
| Sampled | 200 |
| Unique key1 in sample | 44 |
| Rows with audit join | 39 |

### Class counts (mechanical)

| Class | n | Meaning |
|---|---:|---|
| `segmentation_flag` | 200 | Sense-count changed under corrected 〉 splitter — not a RU-text gold fail |

## Interpretation

1. **Do not treat the 93% population flag as "93% bad Russian."** Every sampled row that carries the default reason is a *segmentation* quarantine candidate; `ru_quality_verdict` is deliberately `unknown_not_measured`.
2. **Mass re-translate is not authorised** by this sample alone. Next step if RU quality is in doubt: a human/paid read of a smaller nested sample of the segmentation_flag class (e.g. 30 cards), not a full paid re-run of 10k rows.
3. Machine-readable sample: `reports/pwg_ru_glyph_quarantine_sample_2026-08-01.json`.

_Dr. Mārcis Gasūns_
