# SHIVA_SUTRAS_PRATYAHARA_REPORT_2026-09-10.meta.md — metadoc

_Created: 10-09-2026 · Last updated: 10-09-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[SHIVA_SUTRAS_PRATYAHARA_REPORT_2026-09-10.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SHIVA_SUTRAS_PRATYAHARA_REPORT_2026-09-10.md).

## Subject

- **Document:** [SHIVA_SUTRAS_PRATYAHARA_REPORT_2026-09-10.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SHIVA_SUTRAS_PRATYAHARA_REPORT_2026-09-10.md)
- **Purpose:** Schema inspection of `yadisk:Panini/ShivaSutras.xlsx`/`.docx`, prior-art check against kosha/VisualDCS/Sangram/vidyut, and the derived pratyāhāra-range dataset it produced.
- **Audience:** Anyone building pratyāhāra-based sandhi rules or asking "do we already have the Śiva Sūtras machine-readable."
- **Format / contract:** Schema table → prior-art table with verdicts → derived-dataset description → explicit kosha-registration skip verdict. Row count (42) must match `shiva_sutras_pratyahara_ranges.tsv` after a re-run.

## Provenance

- **Created:** 10-09-2026, handoff [H4471](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4471-OxAlpha_SanskritLexicography_shivasutras-dataset_09.09.26.md) (claimed OxAlpha (opencode/z-ai/glm-5.3-flash), executed Sonnet 5 `claude-sonnet-5` under H3688 — any executor may run any tier).
- **Sibling artifacts:**
  - [shiva_sutras_pratyahara_ranges.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/shiva_sutras_pratyahara_ranges.tsv) / [.json](https://github.com/gasyoun/SanskritLexicography/blob/master/data/shiva_sutras_pratyahara_ranges.json)
  - [build_shiva_sutras_pratyahara_ranges.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/build_shiva_sutras_pratyahara_ranges.py)

## Known limitations

- Anubandha markers are not stripped from `phonemes_devanagari` — the
  "real" letter-only phoneme list per pratyāhāra is a documented follow-up,
  not computed here (see report § Derived dataset).
- kosha registration (`shiva-sutras-machine`) is an explicit skip, not a
  completion — see report § kosha registration.
- Rights on the source xlsx/docx are unconfirmed; raw files stay
  gitignored under `data/_raw_local/`.

## Revision history

| Date | Change |
|---|---|
| 10-09-2026 | Created with the H4471 close-out (Sonnet 5 `claude-sonnet-5`). |

_Dr. Mārcis Gasūns_
