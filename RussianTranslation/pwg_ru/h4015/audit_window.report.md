# Audit Window Report

State: `audited`

| metric | value |
|---|---:|
| workflow keys | 1 |
| clean keys | 0 |
| requeue keys | 1 |
| judge sample keys | 1 |
| judge sample seed | 748e29c420cfc18b |

## Production Metrics

| metric | value |
|---|---:|
| wall_clock_minutes | 367.772 |
| wall_clock_source | derived_mtime |

## Manual Rule Coverage

Live harness rules: Apresjan, Hartmann, Gonda/Vogel, Tubb, Baalbaki, Apte/Gillon/Inglese-Geupel, Mitrenina/Zaliznyak-Paducheva/Ruppel.
Methodology/design only: Riemer, Klosa.

| target | missing required rules |
|---|---:|
| `pilot\run_pilot_wf.js` | 0 |

## Semantic Risk Queue

| metric | value |
|---|---:|
| risky keys | 1 |
| risks | 13 |
| high-confidence risks | 0 |
| high-confidence keys | 0 |

| rank | key | score | high-confidence | top risks |
|---:|---|---:|---:|---|
| 1 | `_apta` | 67 | 0 | `suspicious_lexicographic_with_text_signal`, `markup_wrapper_dropped`, `suspicious_lexicographic_with_text_signal`, `markup_wrapper_dropped`, `suspicious_lexicographic_with_text_signal` |

| gate | exit | requeue |
|---|---:|---:|
| final_schema | 0 | 0 |
| nws | 0 | 0 |
| sense_loss | 0 | 0 |
| prompt_semantic | 0 | 0 |
| translation | 0 | 0 |
| stage2_mechanical | 0 | 0 |
| coverage | 1 | 1 |
| sense_dupes | 0 | 0 |
| ru_style | 0 | 0 |

## Requeue Keys

_apta

## Judge Sample Keys

_apta
