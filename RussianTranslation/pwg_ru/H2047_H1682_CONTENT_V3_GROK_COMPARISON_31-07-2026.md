# H2047 Grok comparison pass — results for Opus

_Created: 31-07-2026 · Last updated: 31-07-2026_

**Executor:** Grok 4.5 (`grok-4.5`) — explicit override of Opus filename lock so Opus can compare.

## Done criteria (handoff) vs this pass

| # | Criterion | Status |
|---|---|---|
| 1 | Case section stay-Latin; no `Acc.→акк.` bulk | PASS — case composition shows `оставить латиницей (stay Latin)` for Acc./Loc./… families; only metalanguage mentions of `акк.` (policy text) |
| 2 | Voice/tense: expansion + `(n=…)` + case-fold families | PASS — e.g. `caus. (Causativ, n=453) · Caus. (Causativ, n=378) → предложение: кауз. (H2048/N8)` |
| 3 | 1–5 clickable examples on bulk + residue | PASS — KWIC 269/269 tokens ≥1 example; cap 5; kosha links present (`gasyoun.github.io/kosha`) |
| 4 | Lock hash updated; generator PR | in progress this pass |
| 5 | GTD `@DO` vote row rewritten | in progress this pass |

## Artifacts

- Generators (committed): `RussianTranslation/src/build_h1682_abbrev_rules_sheet.py`, `h1682_abbrev_collapse.py`, `build_h1303_abbrev_sheet.py`
- Lock: `RussianTranslation/review/locks/h1682_abbrev_rules.lock.json` → `sha256:88f7db782d96a824651f38b74edb3a20ffa3676f872c04b9df9b4d53c0247d0f`
- Sheet (gitignored): `review/h1682_abbrev_rules_sheet.html` — also copied to main-tree review path for `file://` open
- Selftest: `h1682_abbrev_collapse --selftest` → PASS (269 tokens: 252 bulk / 17 residue / 12 sections)

## Design choices Opus may want to revisit

1. **Case `ru` in O overlay** = Latin form itself (`ru='Acc.'`), not `ru=None` (would force residue under current `_AMBIG_RE` heuristic). Alternative: stay-Latin sentinel + collapse exception.
2. **Non-case grammar** still shows prior O proposals (`кауз.`, `аор.`, …) as *предложение* with H2048/N8 caveats — did not blank them to pure stay-Latin (handoff preferred interim stay-Latin default; N8 pins Caus.).
3. **KWIC** scans the shared canonical store once; de-dupes by `(key1, token)`; stops early when all tokens are full.
4. **datt./locc.** still render as single-surface lines (prop Dat./Loc.) rather than merging into Dat./Loc. families — minor display gap.

## Reproduce

```
cd SanskritLexicography/RussianTranslation
python src/h1682_abbrev_collapse.py --selftest
python src/build_h1682_abbrev_rules_sheet.py
```

_Dr. Mārcis Gasūns_
