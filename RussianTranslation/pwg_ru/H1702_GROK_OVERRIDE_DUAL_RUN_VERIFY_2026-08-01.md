# H1702 Grok override — dual-run independent re-verification

_Created: 01-08-2026 · Last updated: 01-08-2026_

**Source handoff:** [H1702](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1702-Sonnet_SanskritLexicography_pwg-ru-d4-unwrapped-gloss-boundary-repair_26.07.26.md)
(filename lock **Sonnet**; this pass is a **Grok 4.5 (`grok-4.5`) model-lock override**,
01-08-2026, dual-run protocol).

**Sonnet lane (already shipped):** [PR #810](https://github.com/gasyoun/SanskritLexicography/pull/810)
(merged 26-07-2026) · [H1702_D4_BOUNDARY_ANCHORED_WRAP_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1702_D4_BOUNDARY_ANCHORED_WRAP_REPORT_2026-07-26.md).

**Override lane goal:** re-execute the original stop condition independently against the
**current** store (post-PR #810), without rubber-stamping Sonnet numbers; record
identical / equivalent / conflicting / net-new vs the Sonnet report; **do not** relax the
≥0.90 precision bar or invent a second wrap strategy in this pass.

## Method (same code, fresh measurement)

1. Worktree off `origin/master` (`SanskritLexicography-h1702-29896`, branch
   `h1702-grok-override-d4-verify`).
2. Dry-run:
   `python src/pilot/fix_d4_boundary_wrap.py --store --dry-run` against
   `canonical_store` → main-tree gitignored
   `SanskritLexicography/RussianTranslation/src/pwg_ru_translated.jsonl`.
3. Residual sample: n=30 seed 42 from current `ru_n==0` ineligibles (hand-read DE/RU +
   refuse reason).
4. Fixed-row integrity sample: n=25 seed 11 from rows with `de_n == ru_n >= 1` — check no
   `{#…#}` / `<ls>` / `<ab>` inside an RU `{%…%}` span.
5. Synthetic row-811-class probe: gloss-before-colon + `{#…#}` citation must wrap only the
   gloss.
6. Probe only (not applied): would normalizing `〉`/`）` → `)` unlock additional residual
   rows under the **same** affix logic?
7. Tests: `python src/pilot/window_selftest.py`; `python -m pytest`.

Code under test (unchanged this pass):
[`src/pilot/d4_boundary_wrap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/d4_boundary_wrap.py),
[`src/pilot/fix_d4_boundary_wrap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_d4_boundary_wrap.py),
`test_h1702_boundary_wrap_gate` in
[`src/pilot/window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py).

## Results vs Sonnet report

| metric | Sonnet 26-07-2026 | Grok re-measure 01-08-2026 | class |
|---|---:|---:|---|
| store rows | 11,603 | 11,603 | **identical** |
| `ru_n==0` residual (post-fix) | 1,109 | 1,109 | **identical** |
| newly eligible for auto-wrap now | 0 (after apply) | **0** dry-run | **identical** |
| `prefix-no-match` | 576 | 576 | **identical** |
| `suffix-no-match` | 344 | 344 | **identical** |
| `multi-gloss-in-gap` | 83 | 83 | **identical** |
| `residual-d3-guillemet-present` | 46 | 46 | **identical** |
| `anchor-mismatch` | 31 | 31 | **identical** |
| `gloss-span-crosses-anchor` | 15 | 15 | **identical** |
| `overlap` | 7 | 7 | **identical** |
| `bad-chars-in-candidate` | 7 | 7 | **identical** |
| residual with Cyrillic in `ru` | (spot-check) | **1,109 / 1,109** | **equivalent** (all still present+unwrapped) |
| fixed-row sample: anchor swallowed into RU gloss | 0/65 hand-reviewed | **0/25** seed 11 | **equivalent** |
| colon-before-`{#…#}` synthetic | row-811 style in CI | wrap = `{%gloss%}: {#…#}` only | **identical** intent |
| `window_selftest` | 193/193 | **198/198** | **equivalent** (suite grew) |
| `pytest` | 18/18 | **96/96** | **equivalent** (suite grew) |

**Store write this pass:** none. Zero rows clear the existing mechanical eligibility gate;
re-applying would be a no-op and a second backup would add noise.

### Residual sample (n=30, seed 42) — refuse reasons still correct

Hand-read confirms the parked set is still **unsafe under exact-affix anchoring**, not a
regressed store:

- Dropped leading `<div n="…">` on RU (prefix fails) while DE keeps it.
- Numbering punctuation drift: DE `— N〉` vs RU `— N)` (fullwidth/CJK corner bracket vs
  ASCII `)`).
- Multi-gloss DE gaps and sentence restructure (RU moves gloss material relative to
  anchors).
- Genuine D3 guillemet residuals still refused wholesale (masking guard).

No sample row was judged “should have been wrapped by the shipped method.” Precision bar
for **new** wraps is N/A (eligible count = 0); residual refuse precision is effectively
100% on this sample (30/30 justified refuses).

### Net-new observation (probe only — not applied)

A **pure probe** (normalize `〉`/`）` → `)` and `〈`/`（` → `(` on both sides, then re-run
`try_boundary_wrap`) unlocks **63** additional residual rows that currently fail
prefix/suffix match **only** on that punctuation class.

| probe | count |
|---|---:|
| residual still 1,109 under shipped code | 1,109 |
| would unlock with `〉`/fullwidth-paren normalize | **63** |
| still refused after that normalize | 1,046 |

This is **net-new** relative to the Sonnet report (which did not quantify this subclass).
It is **not** promoted here: it is a material method change, needs its own ≥50-row / ≥90%
hand-check and guards before any store write. Parked for the Sonnet dual-run residual to
adjudicate (keep as report-only vs mint a D4b handoff).

### Conflicting

**None** on counts, ineligible breakdown, or “do not auto-wrap the residual under the
shipped method.”

## Acceptance re-check (original stop condition)

| criterion | verdict |
|---|---|
| Boundary-anchor detector still identifies safe RU gloss spans | **YES** — CI gate + synthetic + 0 eligible false positives on live residual |
| Apply only rows clearing bar | **N/A apply** — 0 eligible; prior 1,430 already in store |
| No corruption of `{#…#}` / `<ab>` / `<ls>` | **YES** on fixed sample + synthetic |
| Backup + dated report | backup already from Sonnet lane; **this** report is the override artifact |
| Tests green | **YES** 198/198 selftest, 96/96 pytest |
| Never relax bar to hit a count | **honored** — 63-row unlock left unapplied |

## Dual-run salvage classes (Grok vs Sonnet)

| topic | class | keep |
|---|---|---|
| 1,430 fixed / 1,109 residual / breakdown table | identical | Sonnet store state + both reports |
| Method + guards (D3 mask, gloss-crosses-anchor) | identical | shipped code |
| Test suite pass counts | equivalent | current suite |
| `〉`/fullwidth-paren residual subclass (n≈63) | **net-new** (Grok probe) | report only until Sonnet residual adjudicates |

## Non-goals (honored)

- No re-translation.
- No D3 residual repair.
- No store rewrite when dry-run fixed = 0.
- No relaxation of exact-affix matching.

_Dr. Mārcis Gasūns_
