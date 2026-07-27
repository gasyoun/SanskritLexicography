# H1702 — boundary-anchored auto-wrap for the H1651 D4 `ru_n==0` sub-pattern — report

_Created: 26-07-2026 · Last updated: 26-07-2026_

Handoff: [H1702](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1702-Sonnet_SanskritLexicography_pwg-ru-d4-unwrapped-gloss-boundary-repair_26.07.26.md)
· Model: Sonnet 5 (`claude-sonnet-5`) · Follow-up to
[H1651_WRAPPER_DEFECT_SWEEP_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1651_WRAPPER_DEFECT_SWEEP_REPORT_2026-07-26.md).

## What this was

H1651 found 2,539 rows (21.9% of the store) where `de` carries at least one `{%...%}`
gloss slot but `ru` carries zero — spot-checked and confirmed as a markup-fidelity gap,
not content omission: the Russian translation is present and correct, it is simply never
wrapped. H1651 declined to auto-fix this class because a naive "wrap the rest of the row"
heuristic risks swallowing following `{#...#}`/`<ab>`/`<ls>` citation content into the
gloss span, and recommended a follow-up handoff to build a boundary-anchored fix. H1702 is
that follow-up.

## Method

**Boundary anchoring.** `de` and `ru` are split on a fixed set of anchors that are never
translated and so are byte-identical between the two fields on a clean row: `{#...#}`
(Sanskrit/SLP1), `<ls>...</ls>` (citations), `<ab>...</ab>` (grammatical abbreviations —
per [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
these stay international Latin), `<is>...</is>` (transliterated foreign terms). `<div
n="...">` is deliberately excluded from the anchor set — some rows drop the leading
`<div>`/numbering marker on the RU side (a separate, pre-existing defect, not this pass's
concern) — so requiring it to match would either misfire on those rows or need special
casing; leaving it out means such rows simply fail the affix-match check below and are
safely skipped rather than mishandled.

If the anchor sequence in `de` (excluding `{%...%}` gloss spans, never literal in `ru`) is
not IDENTICAL to `ru`'s — same anchors, same order, same content — the row is ineligible.
Anchors otherwise partition both fields into the same number of "gaps." For each `de` gap
containing exactly one gloss span, split it into `(prefix, gloss, suffix)`. The
corresponding `ru` gap is wrapped only if it starts with `prefix` and ends with `suffix`
**exactly, byte-for-byte** — numbering markers like "— 2)" and trailing separators like
": " are themselves untranslated, so an exact affix match is required, not merely
available. A gap with ≥2 gloss spans, or any affix that doesn't match verbatim, leaves the
row untouched and reported as ineligible — never guessed.

**Two additional guards, both found mid-pass by diffing the applied fix against
independent invariants, not by the sample review:**

1. **`residual-d3-guillemet-present`.** A row still carrying an unresolved H1651 D3
   guillemet (`«...»`) anywhere in `ru` is refused wholesale, even if its other gloss
   slots would otherwise pass. Wrapping only the unrelated slots adds a `{%...%}` span
   that makes `wrapper_defect_scan.find_d3`'s `not ru_gloss` heuristic stop flagging the
   row — masking the still-open D3 defect from its own detector without resolving it (this
   surfaced as the D3 residual count dropping from 46 to 40 after a first, unguarded fix
   pass; reverted and re-run with the guard). 46 rows.
2. **`gloss-span-crosses-anchor`.** An anchor — typically `<ab>...</ab>` — sometimes sits
   *inside* a `{%...%}` gloss span (a real PWG pattern, e.g. `{%gekocht <ab>u. s. w.</ab>%}`).
   Naive anchor-splitting cuts such a gloss in two across the anchor boundary, so it reads
   as gloss-free to the per-gap loop while other, cleanly-anchored slots in the same row
   still get wrapped — a partial fix that breaks the all-or-nothing guarantee (found via a
   post-fix `de_n`/`ru_n` parity diff: 4 of 1434 first-pass fixes left one slot unwrapped).
   Closed by comparing the total `{%...%}` count in `de` against the sum of per-gap counts
   before touching anything; a mismatch refuses the whole row. 15 rows.

Implementation:
[src/pilot/d4_boundary_wrap.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/d4_boundary_wrap.py)
(detector + `try_boundary_wrap`),
[src/pilot/fix_d4_boundary_wrap.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_d4_boundary_wrap.py)
(`--store`/`--dry-run` runner, backup-before-write, mirrors the H1651
`fix_wrapper_defects.py` shape). CI gate:
`test_h1702_boundary_wrap_gate` in
[src/pilot/window_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py),
covering the positive wrap, the H1651 row-811 corruption-risk shape (gloss ends at a colon
before a citation — must not swallow it), the dropped-`<div>` refusal, and both guards
above.

## Precision verification

Before applying anything at scale: hand-reviewed samples at three points in the pass —
n=10 informal, n=25 (seed 11) after the first working version, and a final n=30 (seed 42)
against the actually-applied store diff — 65 rows total, zero incorrect wraps. One sample
(row `viS|vi_s~~h0_16_vi|1`) confirmed the fixer faithfully mirrors a pre-existing PWG
markup quirk (a `{%...%}` span in `de` itself misplaced across a parenthesis) rather than
"fixing" it — correct behavior, since re-interpreting the source's own boundary is exactly
the guessing this pass refuses to do.

## Result

| metric | value |
|---|---:|
| `ru_n==0` rows at start | 2,539 |
| mechanically eligible (both guards applied) | 1,430 |
| rows fixed | 1,430 |
| rows left, ineligible (manual review) | 1,109 |

Ineligible breakdown:

| reason | rows |
|---|---:|
| `prefix-no-match` | 576 |
| `suffix-no-match` | 344 |
| `multi-gloss-in-gap` | 83 |
| `residual-d3-guillemet-present` | 46 |
| `anchor-mismatch` | 31 |
| `gloss-span-crosses-anchor` | 15 |
| `overlap` | 7 |
| `bad-chars-in-candidate` | 7 |

Post-fix rescan (`wrapper_defect_scan.py`): D1 = 0 (unchanged), **D3 = 46 (unchanged —
confirms the guillemet guard prevented any masking of the D3 residual)**, D4 = 1,430 (down
from 2,860; the 1,430 fixed rows account for the entire drop, verified by a per-row
`de_n`/`ru_n` parity diff against the pre-fix backup — zero rows show a partial fix).
Row count unchanged: 11,603 before and after. Backup:
`pwg_ru_translated.jsonl.h1702.bak`.

The remaining 1,109 `ru_n==0` rows are genuinely not safe to auto-wrap under this method —
mostly rows where `ru` restructures the sentence relative to `de` (so no exact affix
survives) or drops the `<div>`/numbering prefix. They join the pre-existing D3
46-row residual as the manual-review worklist; no further mechanical pass is recommended
without a materially different anchoring strategy.

## Live generation-time gate: not needed, already covered

H1651's own D1 fix needed a new live-gate signal (`cyrillic_in_sanskrit_wrapper`) because
no existing risk detected that pattern. D4's `ru_n==0` sub-pattern does not need one:
`prompt_rule_audit.markup_sigla_risks`'s pre-existing `markup_wrapper_dropped` risk
(soft/report-only, predates H1651) fires whenever `sgloss > 0 and dgloss < sgloss` where
`sgloss`/`dgloss` are `{%...%}` counts in `de`/`ru` — `ru_n==0` is exactly the `dgloss==0`
special case of that condition, so a future generation run producing this defect is
already flagged. Soft/report-only is the right severity here too, for the same reason D4
overall was never given a HIGH_CONFIDENCE gate: the H1651 report's own D4 breakdown found
two other `de_n != ru_n` sub-patterns (`de_n<ru_n`, `de_n==0,ru_n>0`) that were legitimate
in 8/8 hand-sampled rows each, so a hard hallmark on ANY count mismatch would misfire.

## g5_batch1 / g6 overlap

H1651's report noted 35 of the 150 `g5_batch1` rows carried a D4 flag, "mostly the
`ru_n==0` unwrapped-but-present class — not acted." This pass does not re-derive that
30/35-row list or touch `g5_batch1_sheet.html`/its `decisions.json` (H1650's scope, not
this handoff's) — some of those rows are very likely now resolved as a byproduct of the
1,430-row fix, but disposition of the sheet itself is left to whoever executes H1650.

## Verification

- `python src/pilot/d4_boundary_wrap.py`: 1,430/2,539 eligible, matches the applied fix.
- `python src/pilot/window_selftest.py`: 193/193 passed (192 pre-existing + the new
  `test_h1702_boundary_wrap_gate`).
- `python -m pytest`: 18/18 passed.
- `LANG_PARITY.md`'s 35 recorded classifications re-attested (file-hash bump only — the
  new `d4_boundary_wrap.py`/`fix_d4_boundary_wrap.py` are single-language (RU-only)
  store-maintenance scripts with no `--lang` branching, the same shape as the pre-existing
  `wrapper_defect_scan.py`/`fix_wrapper_defects.py`, and so do not trip the coverage
  scanner — consistent with those files' own non-appearance in the ledger).

## Non-goals honored

Re-translation beyond what a wrapper repair required: none performed. `g5_batch1`/
`h178_*` sheets: not touched. D3's 46-row residual: not touched (guarded against
incidental masking, not fixed). `<ls>` citation wiring (H1652): not touched.

_Dr. Mārcis Gasūns_
