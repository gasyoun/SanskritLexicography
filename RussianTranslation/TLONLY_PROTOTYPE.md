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

## Integration — `gen_opt_harness2.py` (batched + masked, canonical output)

Built [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py):
reuses the FULL production `CONV`+`TR` prompt (all HARD RULES) + the rich
`FINAL_CARD_SCHEMA`, masks each card (pwg_mask), bin-packs cards into batches, and
**restores `{Tn}` to source markup inside the JS** so the returned object is already a
canonical `wf_output.json` — `audit_window.py` consumes it unchanged, no new operator step.

A/B on **8 mixed gam cards** (1 dense `anu` + 7 small), production 1-agent/card vs opt2 1 batch:

| run | input | cache-create | cache-read | output (est) | **$ cost** |
|---|---:|---:|---:|---:|---:|
| production (8×1) | 45 | 370,139 | 409,910 | 14,075 | **$1.722** |
| opt2 (1 batch) | 3 | 34,847 | 0 | 2,855 | **$0.173** |

**−90 % cost.** Verified: **0 leftover `{Tn}`, markup fidelity 8/8** (restored `<ls>`/`{#..#}`
counts match source), quality at parity (semantic-risk counts identical except +1 on each of
the 2 dense cards; Russian reads clean).

**Measurement caveat (important):** the transcript's `usage.output_tokens` *under-reports*
structured-output runs — the generated card JSON rides in a `StructuredOutput` tool-call whose
args aren't counted as output (opt2 logged `output_tokens=40` for ~2.8 k real tokens).
[`parse_workflow_cost.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py)
now estimates true output from the tool-call char size (÷4). The dominant cost is `cache_create`
of the repeated prompt, which IS logged reliably — that's where the −90 % is real and robust.

**Production hardening shipped:** model `key1` is inconsistent (sometimes the headword, not the
subkey), so the harness maps cards **positionally** (requires `cards.length === batch.length`,
else retry) and runs a **post-restore fidelity guard** — if a card's restored `<ls>`/`{#..#}`
counts don't match its source, it is nulled → deterministic requeue, never emitted garbled.

**Status:** validated, canonical, −90 % cost (small batch), quality-parity.

## Full-root rollout (measured end-to-end)

Ran the **full `gam` root** (127 cards → 18 batches) through opt2, then `audit_window.py`:

| | original per-card | opt2 batched+masked | Δ |
|---|---:|---:|---:|
| full-`gam` $ cost | **$16.14** | **$4.45** | **−72 %** |
| agent calls | 127 | 18 (33 with retries) | |

- `audit_window.py` **consumed the canonical output unchanged** — 127 cards, clean 107,
  requeue 20; nws + sense_dupes gates ran normally.
- The fidelity guard **nulled 3 cards** (restored markup ≠ source) → requeue, never garbled;
  124/124 surviving cards markup-faithful, **0 leftover `{Tn}`**.
- −72 % (vs −90 % on the small clean batch) because the dense `pw` cards are 1-per-batch and
  **~15 retries** (33 calls / 18 batches) ate savings. Fixed: a batch now retries **only its
  still-unresolved cards**, not the whole batch (one missing card no longer re-bills the rest)
  — expected to recover much of the gap on the next run.

**Wired in:** [`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md)
now names `gen_opt_harness2.py` the default generator (legacy `gen_opt_harness.py` still
supported). Open: re-measure the full root with the partial-retry fix; tune `--budget` for
dense roots.

## Cost decomposition (2026-06-29) — where the money actually is

After the lean-TR A/B (`AB_TEST_LEAN_TR.md`) showed TR-trimming saves nothing, parsed the
transcript directly. Per agent (batch): **our prompt (PREAMBLE+GRAMMAR+TR+schema+cards+
portraits) is only ~5k tokens, but `cache_creation` is ~35k** — so **~30k (86%) is the
workflow subagent's OWN framework system prompt** (agent instructions + tool infra), a FIXED
cost per agent (not in the transcript; inferred as cache_creation − our prompt). Consequences:

- TR (2.5k) / schema (1.2k) / masking / content trimming all chase the 5k slice → negligible.
- The **−72% batching win was entirely fewer agents** (127→18 amortizes the 30k), NOT masking.
- The 30k is a per-agent framework constant we can only **amortize, not remove** (barring a
  leaner `agentType`). So **the ONE cost lever is agent count = batch size**: more cards per
  agent → fewer 30k payments. (`--budget` controls packing; 24 cards → 5 batches at 9000,
  2 at 20000, 1 at 40000.) Bounded by model reliability + output limits with many/dense cards.
