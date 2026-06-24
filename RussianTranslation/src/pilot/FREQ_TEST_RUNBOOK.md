# Freq-queue 10-article test — runbook (Max)

A bounded end-to-end test of the frequency-first pipeline: **8 single-card nouns + the
giant root `man` (27 sub-cards)** = **35 translation units**. Exercises the common path
(fast, ≈43k of 44k headwords look like this) AND one full giant `split → translate → glue`,
and yields per-card timing to extrapolate the full run.

> **Why this set, not the literal top-10.** The top-10 freq articles are all giant verb
> roots = **992** translation calls (i alone = 204). This mix is ~35 calls and proves the
> same pipeline. Full-queue estimate: ≈43k single-card + ~1,163 giants × ~85 ≈ **~140k
> calls** — the giants are the cost and they're front-loaded by frequency.

## Already done (committed)
- **Inputs generated** in `pilot/input/` (gitignored): the 8 noun whole-cards + `man~~h0_*`
  (27 sub-cards, head split into single-pass parts; max sub-card 131 lines, nouns 126–266).
- **Manifest**: [`pilot/output/scale_manifest.freqtest.json`](output/scale_manifest.freqtest.json)
  — 35 entries, each `key1` = the input stem the workflow iterates (noun `safe_name`, or a
  `man` sub-card subkey verbatim).
- **Sub-card plumbing wired**: `run_pilot_wf.js` (`fileOf`) and `_pilot_collect.py` now keep
  a `~~`-containing sub-card stem verbatim instead of re-`safe_name`-ing it, so
  `<subkey>.raw.txt` → `<subkey>.merged.md` flows straight into `root_glue_translated.py`.

The 8 nouns: `nara jana idam kArya vIra na iti loka` (all comfortably single-pass; the
bigger high-freq nouns `kAla`/`ka` were left out — at ~520 lines they risk overflowing a
single pass, which is a separate "extend the head-splitter to large non-giant entries"
follow-up, not part of this test).

## Run it (on Max)

**1. Point the workflow at the test manifest.** In [`run_pilot_wf.js`](run_pilot_wf.js) set:
```js
const SECTION = 'freqtest'   // was 'a'
const OFFSET  = 0
const LIMIT   = 35           // all 35 units
```
(Revert to `'a'` / `50` afterwards to resume the a-section.)

**2. Translate + judge** through your harness; save the JSON result to `wf_output.json`.
Translate = Sonnet (per-sense Russian + Apresjan discrimination); Judge = Opus.
**Record wall-clock + token totals** — that's the scaling number we're after.

**3. Render to `.merged.md`:**
```sh
python run_real_test.py audit wf_output.json
```
Writes one `<stem>.merged.md` per unit into `pilot/output/` (sub-card stems kept verbatim).

**4. Glue the giant into a NESTED article:**
```sh
python root_glue_translated.py man      # -> pilot/output/man.NESTED.md
```
The 8 nouns need no glue — each `<noun>.merged.md` is already its final article.

## What to check
- **Coverage**: 8 noun cards present; `man.NESTED.md` assembles all 27 sub-cards in order —
  homonym dividers (`# Омоним N`), simple-verb head parts, then prefixed verbs, supplements
  (PW/SCH/PWKVN) last. Pending slots only if a sub-card failed.
- **No overflow**: every unit ≤ ~270 lines, so each should translate in one pass (the old
  slow run was the now-deleted 820-line monolithic `_b_u~~00.raw.txt`).
- **Quality**: judge severity ≤ 2; sigla/IAST kept verbatim; NWS owner-map rows one-per-entry.
- **Timing**: per-unit wall-clock × the queue profile → full-run cost.

## Known limitation (expected, not a bug)
Split sub-cards carry an **empty `portrait.json`** (`[]`), so they translate from the raw
German only — no corpus-synonym candidate evidence for the per-sense Apresjan discrimination.
The 8 nouns carry full portraits. Wiring per-sub-card portraits is the next refinement if the
giant-root translations need the corpus evidence.
