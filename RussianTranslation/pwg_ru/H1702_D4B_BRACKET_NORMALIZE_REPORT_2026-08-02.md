# H1702 D4b — bracket-normalize unlock for the 63-row fullwidth-paren residual subclass

_Created: 02-08-2026 · Last updated: 02-08-2026_

**Handoff:** [H2144](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2144-Sonnet_SanskritLexicography_h1702-d4b-bracket-normalize-unlock_01.08.26.md)
· Model: Sonnet 5 (`claude-sonnet-5`) · Follows the adjudication in
[H1702_SONNET_DUAL_RUN_COMPARE_2026-08-01.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1702_SONNET_DUAL_RUN_COMPARE_2026-08-01.md)
§ Adjudication, which parked this exact 63-row unlock as report-only pending its own
hand-checked precision sample.

## What this does

Extends `d4_boundary_wrap.try_boundary_wrap` with an opt-in `normalize_brackets` parameter
(default `False`, so the H1702 exact-affix fixer's existing behavior and already-passing
rows are unchanged). When `True`, the prefix/suffix affix comparison treats DE's
fullwidth/CJK corner-bracket numbering marker (`〉`/`）`) as equivalent to RU's plain ASCII
(`)`/`(`) on both sides before the exact-affix check — the same equivalence table
(`BRACKET_NORMALIZE`) H2136's probe used, now promoted from a read-only probe into the
production code path with its own guard.

**Comparison-only, never rewrites stored content:** `BRACKET_NORMALIZE` is a strict 1:1,
length-preserving character map (each bracket char maps to exactly one ASCII char), so it
is used only to decide whether an affix *matches* — the actual prefix/suffix/candidate text
spliced into the result is always sliced from RU's own original (non-normalized) string.
A stronger guarantee than the handoff asked for: the code was additionally changed so the
splice uses RU's own prefix/suffix bytes (`gap_ru[:len(prefix)]` /
`gap_ru[len(gap_ru)-len(suffix):]`) rather than DE's, so RU's native bracket character
survives untouched in every case — confirmed in all 63 hand-checked rows below.

New apply script, modeled on the existing `fix_d4_boundary_wrap.py` --store/--dry-run/
`.h1702.bak` convention:
[`fix_d4b_bracket_normalize.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_d4b_bracket_normalize.py).
It scans only the pool that plain (`normalize_brackets=False`) `try_boundary_wrap` already
refuses, re-tries each with `normalize_brackets=True`, and reports/applies only the newly
unlocked subset — it never touches a row the exact-affix fixer already accepts.

## Results

| metric | value |
|---|---:|
| store rows | 11,603 |
| `ru_n==0` residual before this pass | 1,109 |
| newly unlocked by bracket-normalize | **63** (matches H2136's probe count exactly, no drift) |
| `ru_n==0` residual after apply | 1,046 |
| mechanically eligible (default, post-apply) | 0 |
| `window_selftest.py` | 199/199 (198 pre-existing + 1 new `test_h2144_d4b_bracket_normalize`) |
| `pytest` | 96/96 |

## Hand-check (63/63 — full population, not a sample)

Population is small enough that "≥50" means "nearly all of it," so every one of the 63
newly-eligible rows was read DE/RU/output, not just a sample.

- **Boundary correctness (63/63):** every wrap places `{%...%}` exactly at DE's gloss-span
  position, correctly mirroring numbering markers (`— N)`), dashes, asterisks, and
  parenthetical grammar tags (`(<ab>Acc.</ab>)`) as prefix/suffix text outside the gloss.
- **No anchor swallowing (63/63):** citations (`<ls>...`), abbreviations (`<ab>...`),
  transliterations (`<is>...`), and the non-anchor `<lex>` tag (row `BAzita|...|2)`) all sit
  outside every wrapped span.
- **Bracket preservation confirmed (63/63):** in every row DE uses the fullwidth `〉` and RU
  already used plain ASCII `)`; the applied output always keeps RU's own `)` — DE's `〉` is
  never written into the stored RU text.
- **Multi-gloss rows correctly split at each independent boundary** — two rows
  (`gam|gam~~h0_zz_pw00|5`, `gam|gam~~h0_zz_pw00|X9.1`) have a second gloss slot elsewhere in
  the row that itself needed no bracket normalization but was blocked at the whole-row level
  by the *other* slot's bracket mismatch; both slots now wrap correctly without corrupting
  the already-correct one.
- **Translations spot-checked as semantically faithful** across the full 63 (German→Russian
  correspondence).

**Precision: 63/63 clean = 100%**, well above the ≥90% (≥57/63) bar.

## Store write

Applied via `python src/pilot/fix_d4b_bracket_normalize.py --store`. Per the existing
`.h1702.bak` convention (shared with `fix_d4_boundary_wrap.py`), the backup is only taken if
absent — `pwg_ru_translated.jsonl.h1702.bak` already existed from the original H1702 apply
(26-07-2026) and was correctly left as the single anchor point for the whole H1702 fix
family, not overwritten per-run.

## Non-goals (honored)

- No relaxation beyond the two bracket-equivalence pairs (`〉`/`）`→`)`, `〈`/`（`→`(`).
- No re-translation, no D3 residual repair.
- No change to already-passing rows — `normalize_brackets` defaults to `False`; a control
  test (`test_h2144_d4b_bracket_normalize`) asserts identical output with the flag on vs.
  off for an already-exact-match row.

_Dr. Mārcis Gasūns_
