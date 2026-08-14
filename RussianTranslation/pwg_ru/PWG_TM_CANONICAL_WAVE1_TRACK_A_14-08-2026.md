# PWG TM canonical v1 — Track A receipt (H2683)

_Created: 14-08-2026 · Last updated: 14-08-2026_

Grok 4.6 (`grok-4.6`). Execution of [H2683](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2683-Grok_RussianTranslation_pwg-tm-canonical-fragment-priority-w1_13.08.26.md) Track A from [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pwg_tm_dh_lexicography.md).

## Migration

| Check | Result |
|---|---|
| In / out | **2392 / 2392** |
| exact_card + exact_fragment | 2175 + 217 |
| Lost scholarly / source / hash / reuse fields | **0** |
| Orphan or duplicate IDs | **0** |
| Unresolved sense alignment (entry-level, not invented) | 1153 |
| Source SHA-256 | `02a24c1eb8b1e1fb73a6991fca49b8350b0e470283c4c12c68a119ce15e16dc6` |
| Canonical SHA-256 | `b9ad8e9ff99d561de72029e9af40664e9cf7bfabe1575faf7858d88b757bbe82` |

Receipt: [release/pwg_tm_canonical/reconciliation.v1.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/reconciliation.v1.json).

## Fragment classes

| Class | Count |
|---|---:|
| sense | 11129 |
| definition_gloss | 15781 |
| grammar_label | 6820 |
| citation | 41145 |
| example | 31592 |
| recurring_formula | 5655 |
| **total** | **112122** |

Zero orphans, zero duplicate fragment IDs, all six classes present. The 155 MB `fragments.v1.jsonl` is regenerable (`pwg_tm_fragmentize.py`) and gitignored; inventory hash `793ad333643d53f560c448f764fd94834193338209fa982e077806e1ab389ecb`.

## Priority queue (limit 5000)

| Item | Value |
|---|---|
| Selected unique k1 | **5000** |
| Index rows / unique k1 universe | 98639 / 94074 |
| Freq-matched (DCS/archive) | 34036 |
| Manifest SHA-256 | `f024ec4b0b2e58f75868462d84fd51858e4de473d07c0dd825a487f3b73d952a` |
| Selected-keys SHA-256 | `a7acf80f5cb0fce17e0a6b35c7ba1b4ce76c270b9973d31d707f338ce15fb84c` |
| Strata | attested_high 3600 · lexical_core 500 · complex 400 · rare_attested 300 · index_tail 200 |

Weights frozen in [priority_5000.manifest.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/priority_5000.manifest.json): frequency 0.40, attestation 0.15, citation 0.15, predicted reuse 0.10, core/DCS 0.10, stratification 0.10.

## Proof

```text
python src/pwg_tm_migrate_v1.py --verify
python src/pwg_tm_fragmentize.py --verify
python src/pwg_tm_priority.py --verify --limit 5000
pytest tests/test_pwg_tm_canonical.py
```

All three `--verify` commands green; 8/8 schema tests green. Existing `translation_memory.py selftest` green.

_Dr. Mārcis Gasūns_
