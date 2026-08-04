# H1651 — pwg_ru store wrapper-defect sweep (D1/D3/D4) — report

_Created: 26-07-2026 · Last updated: 26-07-2026_

Handoff: [H1651](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1651-Sonnet_SanskritLexicography_pwg-ru-wrapper-defect-sweep-d1-d4_26.07.26.md)
· Model: Sonnet 5 (`claude-sonnet-5`) · Evidence base:
[VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md)
§5 · Data-integrity issue:
[gasyoun/SanskritLexicography#752](https://github.com/gasyoun/SanskritLexicography/issues/752).

## What this was

Store-wide sweep for three defect classes the audit found in the promoted store
(`RussianTranslation/src/pwg_ru_translated.jsonl`, 11,603 rows) that no review sheet has
ever surfaced: **D1** (Russian glosses wrapped in the Sanskrit `{#...#}` wrapper instead
of the gloss `{%...%}` wrapper), **D3** (the gloss wrapper rendered as guillemets `«...»`
in RU instead of `{%...%}`), and **D4** (a gloss-slot-count flag between DE and RU, not a
defect count on its own). D5 (multiword gloss byte-identical to German) was deliberately
excluded per the handoff — the sample is mostly Latin/IAST that must stay untranslated.

## Method

1. **Detector** —
   [src/pilot/wrapper_defect_scan.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/wrapper_defect_scan.py):
   `find_d1` (Cyrillic inside `{#...#}` — no false-positive mode, Cyrillic is never valid
   SLP1), `find_d3` (DE carries a `{%...%}` gloss, RU carries a guillemet span and no
   `{%...%}` at the same row), and a plain gloss-slot COUNT comparator for D4.
2. **Deterministic fix** —
   [src/pilot/fix_wrapper_defects.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_wrapper_defects.py)
   `--store` mode. D1: every `{#...#}` span containing Cyrillic is rewrapped to `{%...%}`,
   content unchanged. D3: every `«...»` span in `ru` is rewrapped to `{%...%}` **only**
   when the DE gloss-slot count exactly equals the RU guillemet-span count for that row
   (a positional 1:1 swap is safe under count parity; a mismatch means at least one span
   is not a clean drift instance, so those rows are left untouched and listed for manual
   review instead of guessed at).
3. **CI gate** — `test_h1651_wrapper_defect_gate` added to
   [src/pilot/window_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)
   (registered in the suite list, runs in CI's "Window selftest suite" step): plants a
   Cyrillic-in-`{#...#}` violation and a guillemet-drift violation, asserts both detectors
   fire, asserts the fixers repair cleanly, and asserts the count-mismatch guard refuses
   to guess. `LANG_PARITY.md`'s 35 recorded classifications were re-attested (file-hash
   bump only — no classified test body was touched, all SHARED/INTENTIONAL-DIVERGENCE/GAP
   verdicts hold as before).

## D1 — Cyrillic inside `{#...#}` (34 rows, 58 spans)

Repaired 100%: all 34 rows, 58 spans, exact match with the audit's count. Verified against
the worked example (`vid` / `vid~~h0_00_pwg01#6`): `{#полагать, думать, считать,
предполагать#}` → `{%полагать, думать, считать, предполагать%}`, content byte-identical,
only the wrapper delimiter changed. Post-fix rescan: **0 rows**.

Affected roots (pre-fix): `vid` (24), `dah` (3), `ahar` (2), `anaquh` (2), `brAhmI` (2),
`anukampa` (1) — matches the issue's affected-root list exactly.

## D3 — gloss-wrapper drift, DE `{%...%}` rendered as RU `«...»`

**Ruling:** `{%...%}` is the store's documented convention — `pwg_ru/DATA_STATEMENT.md`
§D states plainly "`{%...%}` — italicized glosses/emphases from the print." `«...»` is not
a documented store-level wrapper anywhere in the schema docs. Sampled 8 drift rows by
hand before ruling; all 8 showed the same pattern (DE gloss slot → RU guillemet span,
1:1, same content). **Ruling: yes, `{%...%}` is the convention; `«...»` in the promoted
store is drift, not an alternate valid form.**

**Applied:** 463 rows carried at least one DE-gloss/RU-guillemet count match-or-mismatch
signal (a broader scan than the audit's original 338 — this session's detector does not
require RU to have zero existing `{%...%}` slots, so it also catches partially-drifted
rows the narrower scan skipped). Of those:

- **343 rows / 639 spans — mechanically fixed** (exact DE-gloss-count == RU-guillemet-count
  parity; positional 1:1 rewrap, content unchanged).
- **120 rows — left untouched**, count mismatch (`de_n != ru_n`), listed in the fixer's
  dry-run output for manual review. A mismatch means at least one guillemet span in that
  row is not a clean drift instance (nested quote, stray `«...»`, or a genuine translation
  restructuring), so a positional swap risks corrupting content rather than repairing it.

Post-fix rescan: **46 rows** still carry unresolved guillemet spans (the residual of the
120 skipped, after re-scoping to `find_d3`'s narrower original definition) — these are the
manual-review worklist, not touched this pass.

## D4 — gloss-slot count mismatch (flag, not defect count)

Post-D1/D3-fix count: **2,860 rows** (down from an initial 3,199; the D3 fix itself
resolved ~340 of the original flags by restoring count parity).

| sub-pattern | rows | share of D4 | disposition |
|---|---:|---:|---|
| `de_n > ru_n` (DE has more gloss slots than RU) | 2,795 | 97.7% | see breakdown below |
| `de_n < ru_n` (RU has more gloss slots than DE) | 41 | 1.4% | **not acted** — 8/8 hand-sampled rows are RU legitimately adding a translated gloss where DE's slot held only a bare form (e.g. `nis`, `˚āni`); false-positive rate for "genuine defect" ≈ 100% in sample |
| `de_n == 0, ru_n > 0` (RU glosses content DE left as plain prose) | 24 | 0.8% | **not acted** — 8/8 hand-sampled rows are RU correctly gloss-marking translated content; not a defect |

**`de_n > ru_n` breakdown (2,795 rows):**

| sub-sub-pattern | rows | share |
|---|---:|---:|
| `ru_n == 0` — RU carries **zero** gloss-wrapped spans anywhere in the row | 2,539 | 90.8% |
| `ru_n > 0` — partial (some DE slots wrapped in RU, some not) | 256 | 9.2% |

**Finding, not previously reported:** the `ru_n == 0` sub-sub-pattern (2,539 rows, **21.9%
of the entire store**) is a **markup-fidelity gap, not content omission**. Length-ratio
spot check (n=15, `len(ru)/len(de)`, seed 3): ratios 0.76–1.21, mean ≈0.95 — no evidence of
dropped content. Hand-read spot check (n=8, printed in full) confirms the translation is
present and correct in every sample, e.g. `{%entreissen%}` → `вырывать, отнимать` (row 584,
`Cid|_cid~~h0_11_av_a#avA-1`); `{%kund thun, verkünden, berichten%}` →
`давать знать, возвещать, сообщать` (row 10603, `vid|vid~~h0_zz_pw00#1`). The Russian gloss
text is simply never wrapped in `{%...%}`, unlike the German side which always wraps it —
so this class is invisible to every downstream gloss-extraction pass exactly like D1 was,
just at ~75× the row count.

**Why this is NOT auto-fixed this pass:** unlike D1/D3 (a pure wrapper-character swap on
content that is already correctly delimited), applying `{%...%}` here requires deciding
*where in the RU text the gloss boundary falls* — the translation is not guaranteed to be
positionally parallel to DE. A concrete corruption risk: row 811
(`DA|_d_a~~h0_38_sam_a_1#9`) has DE `{%Etwas einräumen, zugeben%}: {#na samADatte#} als
<ab>Erkl.</ab> von...` — the gloss covers only the clause before the colon; a naive
"wrap the rest of the row" heuristic would swallow the following `{#...#}`/`<ab>`/`<ls>`
citation content into the gloss span, which is exactly the kind of markup corruption H1302
already treats as unacceptable (`repair-vs-requeue`, never guess). A safe fix needs
structural boundary anchoring (shared literal tokens — `<div>`, `<ab>`, the first `:` or
`{#`/`<ls>` after the gloss prefix) verified per-row at a stated precision, the same bar
H1302/H1305 met before applying at scale. **Recommendation: a follow-up handoff** scoped
to build and precision-test that boundary-anchored auto-wrap over the 2,539-row `ru_n==0`
class; out of scope for this pass, reported per the acceptance criterion ("D4 ... the rest
is a report").

## g5_batch1 — 30 flagged-cards overlap

[H1650](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1650-Opus_SanskritLexicography_h178-h180-sheet-rescreen-dedupe_26.07.26.md)
(MG-ruled, **not yet executed** as of this pass) names 30/150 `g5_batch1` rows as
machine-flagged and routes them into this queue as store defects rather than fresh human
votes. The script that produced that original 30-count
(`store_scan.py`/`screening_probe.py`, per the audit) is not committed anywhere findable
in this repo or Uprava — this session could not independently reproduce the exact 30. What
this pass DOES confirm, from the 150 `g5_batch1` row IDs recovered from
`review/g5-live-queue-batch1-2026-07-25_decisions.json`'s `row:LINEIDX:...` item ids:

- **6 of the 34 D1 rows** are `g5_batch1` rows — now repaired (line indices 10969, 10972,
  10975, 10987, 10988, 11085).
- **2 rows** fall in the D3 46-row manual-review residual (line indices 6040, 11012) —
  left untouched, same reason as the rest of that residual.
- **35 rows** carry a D4 flag (mostly the `ru_n==0` unwrapped-but-present class) — not
  acted, per the D4 disposition above.

This pass does **not** edit `g5_batch1_sheet.html` or its `decisions.json` (explicit
non-goal — that is H1650's job). The store-level defects among the 30 flagged rows that
fall under D1/D3 are resolved by this sweep regardless of the sheet's own vote state.

## Verification

- `python src/pilot/wrapper_defect_scan.py` post-fix: D1 = 0, D3 = 46 (residual), D4 =
  2,860.
- `python src/pilot/window_selftest.py`: 192/192 passed (191 pre-existing + the new
  `test_h1651_wrapper_defect_gate`).
- Row count unchanged: 11,603 before and after.
- Backup: `pwg_ru_translated.jsonl.h1651.bak` (pre-fix snapshot).

## Non-goals honored

Re-translation beyond what a wrapper repair required: none performed. `g5_batch1` /
`h178_*` sheets: not touched. `<ls>` citation wiring (H1652): not touched. D5: not
implemented.

## Addendum 26-07-2026 (Sonnet 5, `claude-sonnet-5`) — live generation-time gate

A concurrent session worked this same handoff in parallel; this addendum landed as a
separate, narrower follow-up PR (linked from the [handoffs registry](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md)
H1651 row) after discovering the collision, rather than reopening the (already-merged,
already-correct) work above.

`wrapper_defect_scan.py`/`fix_wrapper_defects.py` detect and repair D1/D3 in a periodic
store scan, but neither is wired into the live per-card generation-time audit
(`prompt_rule_audit.markup_sigla_risks`) — so a future generation run could reintroduce
Cyrillic-in-`{#..#}`, or grow the guillemet-drift residual, undetected by the pipeline
itself. Added: `cyrillic_in_sanskrit_wrapper` (HIGH_CONFIDENCE, mirrors the pre-existing
EN-side `audit_window_en.nws_de_locked()`) and `gloss_wrapper_became_guillemet`
(report-only, alongside the pre-existing `markup_wrapper_dropped`). LANG_PARITY
`wrapper_fidelity_cyrillic_and_guillemet_h1651` (SHARED). Selftest:
`test_h1651_live_gate_cyrillic_and_guillemet`, distinct from this PR's own
`test_h1651_wrapper_defect_gate` (which tests the standalone scan/fix tools, not the live
gate). No store data touched by this addendum — code-only.

_Dr. Mārcis Gasūns_
