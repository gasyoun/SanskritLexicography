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

## Batching A/B — the dominant lever (measured, with real $)

Built [`src/pilot/gen_batched_harness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_batched_harness.py)
(masked cards, N per agent call) and a real cost parser
[`src/pilot/parse_workflow_cost.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py)
that reads the per-agent transcript JSONL (`input` / `cache_create` / `cache_read`
/ `output`) and prices it (Sonnet $3 / $15 / $3.75 / $0.30 per MTok). A/B on **14
small gam prefix cards** (~200 chars raw each), production 1-agent-per-card vs
batched (2 calls, bin-packed at 7 k chars):

| run | calls | cache-create | cache-read | output | total tok | **$ cost** |
|---|---:|---:|---:|---:|---:|---:|
| production (1/card) | 14 (+5 retries) | 381,949 | 453,974 | 5,102 | 841,085 | **$1.645** |
| batched (2 calls) | 2 | 45,020 | 13,465 | 530 | 59,021 | **$0.181** |

**−93 % tokens, −89 % cost** for identical output. The cost is dominated by
`cache_create`: each per-card agent re-creates ~27 k tokens of system prompt +
schema; batching pays it ~2× instead of 14×. This is the single biggest lever —
far bigger than masking (−20 %) or gloss-only (~−600 tokens).

**Caveats (honest):** (a) these are *small* cards — batching's win is largest when
per-card overhead dominates; dense cards (anu) batch fewer per call, so a blended
real-root average is smaller but still large. (b) Big batches showed slightly
thinner per-card metadata (`notes`/`differentia`) — batch size needs tuning for a
depth/cost trade-off. (c) one failed batch re-does all its cards (vs one card).

## Final priority order (measured)

1. **Batch N cards per agent call** — −89 % cost on small cards. *The lever.*
2. **Masking** (lossless, removes corruption class, fixes the pwg_mask bug, −74 %
   wall-clock, no retries) — adopt; composes with batching.
3. **Gloss-only structured output** — tiny token win, but worth it for deterministic
   assembly / correctness.

Recommended next step before scaling Stage-C roots: fold batching + masking into the
production `gen_opt_harness.py` (size-budgeted batches, keep the per-card schema rich
enough), and re-measure $/card on a full mixed root.
