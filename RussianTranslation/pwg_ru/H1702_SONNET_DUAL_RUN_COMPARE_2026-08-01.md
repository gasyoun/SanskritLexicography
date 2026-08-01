# H1702 Sonnet dual-run compare — independent re-verification vs the Grok override

_Created: 01-08-2026 · Last updated: 01-08-2026_

**Handoff:** [H2136](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2136-Sonnet_SanskritLexicography_h1702-grok-dual-run-compare_01.08.26.md)
· Model: Sonnet 5 (`claude-sonnet-5`) · Compares
[H1702_D4_BOUNDARY_ANCHORED_WRAP_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1702_D4_BOUNDARY_ANCHORED_WRAP_REPORT_2026-07-26.md)
(Sonnet, PR [#810](https://github.com/gasyoun/SanskritLexicography/pull/810), 26-07-2026)
against
[H1702_GROK_OVERRIDE_DUAL_RUN_VERIFY_2026-08-01.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1702_GROK_OVERRIDE_DUAL_RUN_VERIFY_2026-08-01.md)
(Grok 4.5 `grok-4.5`, PR [#969](https://github.com/gasyoun/SanskritLexicography/pull/969), 01-08-2026).

## Why this exists

H1702 is Sonnet-filename-locked. A human overrode that lock so Grok could re-measure the
already-shipped Sonnet deliverable. Per the dual-run override protocol (H2048 class), the
override lane cannot be the only close — this residual (H2136) is Sonnet's own independent
re-run, so the compare is not a rubber-stamp of Grok's numbers.

## Method — independent, not a replay

Ran in a fresh worktree
([`SanskritLexicography-h2136-658811`](https://github.com/gasyoun/SanskritLexicography),
branch `h2136-sonnet-dual-run-compare`) off `origin/master`, against the live canonical
store (`RussianTranslation/src/pwg_ru_translated.jsonl`, resolved via
[`store_path.canonical_store`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py)
to the shared main-checkout copy, per the H255 worktree-store-loss guard — never a
worktree-local copy). Code under test unchanged this pass:
[`d4_boundary_wrap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/d4_boundary_wrap.py),
[`fix_d4_boundary_wrap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_d4_boundary_wrap.py).

Deliberately used **different seeds from Grok's** (7 / 91, not 42 / 11) so the hand-checked
samples are a genuinely independent draw, not a re-read of the same rows:

1. `python src/pilot/fix_d4_boundary_wrap.py --store --dry-run`
2. Residual sample: n=30, seed 7, from the current `ru_n==0` ineligible pool — hand-read
   DE/RU + refuse reason for each.
3. Fixed-row integrity sample: n=25, seed 91, from rows with `de_n == ru_n >= 1` — checked
   for citation/abbreviation markup (`{#…#}`, `<ls>`, `<ab>`, `<is>`) swallowed inside an RU
   `{%…%}` gloss span.
4. Bracket-normalize probe (own implementation, not copied from Grok's): normalize
   `〉`/`）`→`)` and `〈`/`（`→`(` on both `de`/`ru`, re-run `try_boundary_wrap` over the full
   ineligible pool.
5. `python src/pilot/window_selftest.py`; `python -m pytest`.

Script written for this pass:
[`h2136_sonnet_independent_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2136_sonnet_independent_check.py)
(kept in-tree as the reusable independent-verification harness for this handoff family).

## Results vs both prior reports

| metric | Sonnet 26-07-2026 | Grok 01-08-2026 | Sonnet 01-08-2026 (this pass) | class |
|---|---:|---:|---:|---|
| store rows | 11,603 | 11,603 | **11,603** | identical |
| `ru_n==0` residual (post-fix) | 1,109 | 1,109 | **1,109** | identical |
| newly eligible for auto-wrap now | 0 (after apply) | 0 dry-run | **0** dry-run | identical |
| `prefix-no-match` | 576 | 576 | **576** | identical |
| `suffix-no-match` | 344 | 344 | **344** | identical |
| `multi-gloss-in-gap` | 83 | 83 | **83** | identical |
| `residual-d3-guillemet-present` | 46 | 46 | **46** | identical |
| `anchor-mismatch` | 31 | 31 | **31** | identical |
| `gloss-span-crosses-anchor` | 15 | 15 | **15** | identical |
| `overlap` | 7 | 7 | **7** | identical |
| `bad-chars-in-candidate` | 7 | 7 | **7** | identical |
| residual sample refuse-precision | (spot-check) | 30/30 (seed 42) | **30/30** (seed 7) | equivalent |
| fixed-row sample: anchor swallowed into gloss | 0/65 hand-reviewed | 0/25 (seed 11) | **0/25** (seed 91, 1 initial flag hand-cleared — see below) | equivalent |
| bracket-normalize probe (unlock count) | — | 63 | **63** | identical |
| `window_selftest` | 193/193 | 198/198 | **198/198** | equivalent (suite unchanged since Grok) |
| `pytest` | 18/18 | 96/96 | **96/96** | equivalent (suite unchanged since Grok) |

**Store write this pass:** none (dry-run only; zero rows clear the mechanical eligibility
gate, matching both prior reports).

### Residual sample (n=30, seed 7) — refuse reasons independently confirmed correct

Hand-read all 30 rows (mix of `prefix-no-match`, `suffix-no-match`, `multi-gloss-in-gap`,
`overlap`) against their `de`/`ru` text. Every refusal is justified under the exact-affix
rule: DE-side numbering/punctuation (`3〉`, `— 2)`, guillemets) not reproduced byte-for-byte
on the RU side, RU dropping a leading `<div>`/marker, or a genuine multi-gloss gap. No row
should have been auto-wrapped by the shipped method. 30/30 justified — same conclusion as
Grok's independent 30/30 on a disjoint seed.

### Fixed-row integrity sample (n=25, seed 91) — one false-positive flag, hand-cleared

The mechanical "anchor characters inside the RU gloss span" check flagged 1/25:
`han|han~~h1_00_pwg00|han 2`. Hand inspection: the flagged `<ab>u. s. w.</ab>` sits inside
the DE gloss span itself —
`{%schlagend, tödtend, Mörder, zu Grunde richtend, vernichtend, verscheuchend <ab>u. s. w.</ab>%}`
— and RU mirrors it identically. This is a pre-existing PWG markup pattern (an anchor
nested inside a gloss span in the *source*, the exact case `d4_boundary_wrap.py`'s
`gloss-span-crosses-anchor` guard exists to refuse when the fixer would need to touch such
a row — see module docstring point 6), not a corruption introduced by the D4 wrap. **0/25
genuine defects**, matching Grok's 0/25.

### Bracket-normalize probe — independently reproduced at 63/1,109

Ran a from-scratch reimplementation of the probe (not Grok's code, same idea): normalizing
`〉`/`）`→`)` and `〈`/`（`→`(` on both sides before re-running `try_boundary_wrap` over the
full 1,109-row ineligible pool unlocks **63** rows, all currently refused on
`prefix-no-match`/`suffix-no-match` purely from that punctuation mismatch (DE uses a
fullwidth/CJK corner bracket for numbering, RU an ASCII `)`); 1,046 remain refused for
other reasons. Exact match to Grok's number — **identical**, upgraded from Grok's
single-report "net-new" to a cross-model-confirmed count.

### Conflicting

**None.** No count, breakdown, sample verdict, or test result diverges between the Sonnet
original, the Grok override, and this independent Sonnet re-run.

## Acceptance re-check (original H1702 stop condition)

| criterion | verdict |
|---|---|
| Boundary-anchor detector still identifies safe RU gloss spans | **YES** — 0 eligible on live residual, 30/30 independent refuse-sample justified |
| Apply only rows clearing the bar | **N/A apply** — 0 eligible; the 1,430 already-fixed rows remain correctly in store |
| No corruption of `{#…#}` / `<ab>` / `<ls>` | **YES** — 0/25 genuine defects on independent fixed-row sample |
| Tests green | **YES** — 198/198 selftest, 96/96 pytest |
| Never relax bar to hit a count | **honored** — 63-row bracket unlock left unapplied |

## Dual-run salvage classes (Sonnet independent vs Grok vs Sonnet original)

| topic | class | keep |
|---|---|---|
| 1,430 fixed / 1,109 residual / ineligible breakdown | identical (3-way) | Sonnet store state + all three reports |
| Method + guards (D3 mask, gloss-crosses-anchor) | identical (3-way) | shipped code, unchanged |
| Residual refuse-precision sample | equivalent — disjoint seeds (Grok 42, Sonnet 7), same conclusion | both samples as independent evidence |
| Fixed-row integrity sample | equivalent — disjoint seeds (Grok 11, Sonnet 91), same 0-defect conclusion (Sonnet's one flag was a detector false positive, hand-cleared) | both samples |
| `〉`/fullwidth-paren residual subclass (n=63) | identical — cross-model-confirmed count | **adjudicated below** |
| Test suite counts | equivalent — suite grew once (Sonnet 26-07 → Grok/Sonnet 01-08), stable since | current suite (198/96) |

## Adjudication: the 63-row bracket-normalize unlock

**Decision: keep report-only in this residual — do not apply here, do not skip promoting
it either.** The unlock is real and now confirmed by two independent implementations
across two models, so it is not noise. But applying it would relax the exact-affix
matching to a **new** affix class (fullwidth/CJK bracket ≡ ASCII paren), which per this
residual's own acceptance bar ("never relax the bar to hit a count") requires its own
≥50-row / ≥90% hand-checked sample and dedicated guards — that is new production work, not
compare-and-adjudicate work, and out of scope for a dual-run residual. **Mint a follow-up
D4b handoff** (`h1702-d4b-bracket-normalize-unlock`) scoped narrowly to: extend the anchor/
affix normalization to treat `〉`/`）`/`〈`/`（` as equivalent to `)`/`(`, hand-check a
≥50-row sample of the 63 (population is small enough that 50 is most of it), and apply only
if the precision bar holds. Until that handoff runs, the 63 rows stay in the `ru_n==0`
residual, correctly reported as ineligible.

## Non-goals (honored, this pass)

- No re-translation.
- No D3 residual repair.
- No store rewrite (dry-run only; 0 eligible).
- No relaxation of exact-affix matching in this pass — the bracket-normalize unlock is
  parked for D4b, not applied here.

_Dr. Mārcis Gasūns_
