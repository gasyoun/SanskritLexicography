# H4740 — Samsaadhanii morph.cgi → glossary layer report

_Created: 15-09-2026 · tier: OxAlpha (opencode/z-ai/glm-5.3-flash)_

**VALIDATION-ONLY** — Samsaadhanii/SCL outputs carry no LICENSE; this layer
is a second independent form→analysis witness, never an overwrite of
human-reviewed data (SAMSAADHANII_INDEX.md license gate).

## Sample design (on our data)

- Population: DCS token.m_unsandhied distinct single-word forms (5.69M tokens)
- Stratum top: top 20 forms by corpus frequency (rank ≤500)
- Stratum mid: 20 random forms from rank 500-50000 (pool 49501, seed 4740)
- Retrieved: 2026-09-15 from `https://scl.samsaadhanii.in/cgi-bin/scl/MT/prog/morph/morph.cgi`

## Result

| stratum | forms | covered | coverage |
|---|---|---|---|
| overall | 40 | 34 | 85.0% |
| top-frequency | 20 | 17 | 85.0% |
| mid-band random | 20 | 17 | 85.0% |

Per-form records (40): [reports/H4740_scl_morph_sample.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4740_scl_morph_sample.jsonl) — cache gitignored (`glossary/scl_morph_cache.jsonl`).

## Misses (6) and ambiguity

- Uncovered: `amṛṣyamāṇaḥ`, `anamitram`, `apāṃsi`, `mahā`, `sa`, `tatas` — typology: indeclinables/avyaya without analyzer entry (tatas, anamitram), compound members (mahā), pro-drop pronoun fragments (sa), middle-participle morphology (amṛṣyamāṇaḥ), split-compound residue (apāṃsi).

- Forms with >1 competing analysis (homograph/polysemy — the adjudication value): 10/40.

## Checks

- `python3 RussianTranslation/src/scl_morph_glossary.py selftest` → PASS (parser fixture, IAST↔SLP1 round-trip via canonical sanskrit-util)
- malformed-HTML handling proven live: the CGI emits unclosed `<tr>/<td>`; parser is boundary-based
- transient-failure policy: 3 retries with backoff per call; polite 1–1.5 s gap + UA-identified

_Гасунс_
