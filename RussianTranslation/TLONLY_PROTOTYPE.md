# Translation-only harness — prototype + token A/B (2026-06-29)

Prototype of the "Python owns ALL markup" redesign (see the design item in
[`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)).
Goal: measure the real token cost vs the production echo harness, honestly.

## What was built

- [`src/pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)
  **bug fixed**: the placeholder masker only matched bare `<ls>`/`<ab>`/`<is>`; the
  per-card inputs use **attributed** tags (`<ls n="ṚV.">…</ls>`), so 37 of `anu`'s
  citations leaked their reference numbers into the model's view. Broadened the
  opening-tag patterns to `\b[^>]*>` (backward-compatible; helps stage-0 too).
- [`src/pilot/gen_tlonly_harness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_tlonly_harness.py)
  — generates a translation-only harness: raw is masked (every `<ls>`/`<ab>`/`<is>`/
  `{#..#}` → `{Tn}`), model sees ONLY translatable German + `{Tn}` tokens, returns
  ONLY Russian-per-sense (no german echo). Reduced schema (no `german` field).
- [`src/pilot/assemble_tlonly.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/assemble_tlonly.py)
  — restores `{Tn}` (lossless) and welds german back; emits a production-shape card.

## A/B — same 6 gam cards (2 dense: anu, upa; 4 small)

| metric | production (echo) | translation-only | Δ |
|---|---:|---:|---:|
| workflow totalTokens | 208,985 | 167,337 | **−20%** |
| agent calls (retries) | 10 (4 retries) | 6 (0 retries) | simpler schema → no retries |
| wall-clock | 115 s | 30 s | **−74%** |
| input chars (raw/skeleton + portrait) | 16,658 | 8,103 | **−51%** |
| output chars (german+russian → russian) | 19,775 | 5,016 | **−75%** |

Round-trip: mask/restore lossless 6/6; assembly 0 unresolved `{Tn}`; deterministic
gate risks 12 → 3 (no quality regression).

## The honest finding

The **content** the model moves drops massively and losslessly — input −51%,
output −75% — and the corruption class is gone (the model never sees or types
markup). But the **headline totalTokens only dropped −20%**, and that number is
noisy (production paid 4 retries here). The reason the char savings don't flow
straight through:

1. **Fixed per-card overhead dominates.** Each card is a *separate subagent*
   carrying a large system prompt + the JSON schema. At ~20 k tokens/call, the
   actual translation I/O (~2–4 k tokens/card of text) is a minority of the bill.
   Masking shrinks the minority.
2. **The model still echoes the placeholder *sequence*.** With a free-text
   `russian` field, the model re-threads all `{Tn}` tokens in order (50 % of the
   already-small output). A free-text russian still reconstructs the entry shape.

## Where the real win is (priority order)

1. **Batch N cards per agent call** — amortize the fixed system-prompt + schema
   overhead. This is the single biggest lever, *larger than masking*, because the
   per-call overhead is the dominant cost.
2. **Gloss-only structured output** — model returns a list of {sense-tag → Russian
   gloss}, NOT a free-text russian that re-threads every `{Tn}`. Kills the
   placeholder echo and makes assembly fully deterministic (Python interleaves the
   source examples/citations).
3. **Masking** (this prototype) — lossless, removes the corruption class, −51 %/−75 %
   I/O, fixes a real bug, eliminates retries, −74 % wall-clock. Adopt, but as the
   third multiplier on top of 1 + 2.

**Verdict:** the redesign is validated and worth doing, but masking alone yields
~−20 % tokens (plus large reliability/latency/correctness wins). To get a big
headline-token cut, combine masking with **batching** + a **gloss-only schema**.
Next measurement to make it a $-number: capture the cache-read/create split
(totalTokens over-weights cheap cache-read).
