# Screening evidence — H1650 (pwg_ru h178/h180/g5)

_Created: 01-08-2026 · Last updated: 01-08-2026_

| Rule | Class | What it does |
|---|---|---|
| `citation_tm` | (b) lookup | Panel per card: every `<ls>` with status + SA/RU when hit |
| `A2-retire-mqm-likert-pairwise` | (a) policy | Three h178 arms withdrawn; instrument = h178_da + agent_pass |
| `frozen-eval-sample` | note | Sample is frozen (H1301), not live store after H1302/H1305 |
| `machine_flags_D1_D3_D4` | (a) | G5 auto-reject; **counts as reject in N** (MG Б) |
| `visible_german_residue` | (a) | G5 excludes reader-visible German (H1655) |

Generators: [`src/sheet_screening.py`](../src/sheet_screening.py).  
Probe (org): `python Uprava/tools/screen_cards.py --all`.  
H274: gate released onto h178_da human + agent_pass; every metric labels agent-vs-human or agent-only.

_Dr. Mārcis Gasūns_
