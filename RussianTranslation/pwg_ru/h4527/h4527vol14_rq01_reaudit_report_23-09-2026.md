# Audit Window Report

State: `audited`

| metric | value |
|---|---:|
| workflow keys | 1 |
| clean keys | 1 |
| requeue keys | 0 |
| judge sample keys | 1 |
| judge sample seed | 91a85dd4fc10dfd7 |

## Production Metrics

| metric | value |
|---|---:|
| wall_clock_minutes | 740.612 |
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
| risky keys | 0 |
| risks | 0 |
| high-confidence risks | 0 |
| high-confidence keys | 0 |

| rank | key | score | high-confidence | top risks |
|---:|---|---:|---:|---|

| gate | exit | requeue |
|---|---:|---:|
| final_schema | 0 | 0 |
| nws | 0 | 0 |
| sense_loss | 0 | 0 |
| prompt_semantic | 0 | 0 |
| translation | 0 | 0 |
| stage2_mechanical | 0 | 0 |
| coverage | 0 | 0 |
| sense_dupes | 0 | 0 |
| ru_style | 0 | 0 |

## Requeue Keys

(none)

## Judge Sample Keys

kast_ur_i~~h0_zz_pw
