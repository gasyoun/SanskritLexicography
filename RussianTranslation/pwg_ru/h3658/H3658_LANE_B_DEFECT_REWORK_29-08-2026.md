# H3658 Lane B — the three H3654 content defects, reworked deterministically

_Created: 29-08-2026 · Last updated: 29-08-2026_

Executor: Opus 5 (`claude-opus-5`). Source handoff:
[H3658](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3658-Opus_SanskritLexicography_h3654-residual-16keys-and-3-defects_28.08.26.md).
Window under rework: the H3654 c1 re-run, whose three convicted keys are listed at
[`H3654_defect_keys.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3654/H3654_defect_keys.txt).

**No model call was spent on this lane.** Every repair below is either an existing ruled
deterministic function or a pipeline fix; nothing was re-translated and nothing was guessed at.

## 1. Verdict per key

| key | defect | outcome | how |
|---|---|---|---|
| `pa_tin` | `empty_russian`, `dropped_sanskrit_span` | **fixed in the pipeline** | new `render_xref_ru` — both flags now clear |
| `_atura` | `markup_wrapper_dropped`, `gloss_wrapper_became_guillemet`, `R1_yo` | **fixed by existing ruled repairs** | `fix_d3` ×9 + `apply_no_yo` ×2 — both wrapper flags clear |
| `_apta` | `markup_wrapper_dropped` ×2, `suspicious_lexicographic_with_text_signal` ×3 | **NOT deterministically repairable** | its wrappers were never converted, only omitted — the class PR #789 deliberately refused to guess |

## 2. `pa_tin` — a pipeline defect, exactly as the handoff called it

`pa_tin` is the window's single `degenerate_passthrough`: the no-LLM cross-reference lane in
[`gen_opt_harness2.degenerate_passthrough_card`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
handled it, so no model ever saw it. Its source body is pure apparatus:

```
{#paTin#}¦ <ab>s. u.</ab> <hom>2.</hom> {#paT#}.
```

H1422 ruling **P3** made that lane emit an **empty** target field, on the reasoning that there is
nothing to translate and verbatim German must never leak into the Russian column. Correct about
German — but the consequence was that *every* xref stub then failed the window audit on
`empty_russian` (an empty `russian`) plus `dropped_sanskrit_span` (both `{#..#}` spans present in
the German, none in the empty Russian), landed on `requeue.defect.keys.txt`, and — the defect
guard being all-or-nothing — could block an entire paid batch.

The apparatus is renderable without inventing any gloss content, because the classifier has
already proven the residue is nothing but the closed
[`xref_vocab.DEGENERATE_XREF_WORDS`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/xref_vocab.py)
set. `render_xref_ru` (added to that same shared module, so the RU harness and the EN auditor
still cannot drift) copies `{#..#}` spans and whole `<ab>` / `<ls>` / `<hom>` regions **verbatim**
and rewrites only a bare, untagged closed-vocabulary German word. `<ab>` deliberately stays as it
is: the article site resolves it to Russian at render time via
[`pwg_ab_ru.RU_MAP`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py)
(`s. u.` → `см.`, MG 10-07-2026,
[ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) §1),
so rewriting it here would double-translate it. When the renderer meets anything outside the
closed set it returns `None` and the card falls straight back to P3's empty field — **the
German-leak guarantee P3 bought is unchanged.**

Measured on the real card:

| | `russian` | flags from `prompt_rule_audit.semantic_risks` |
|---|---|---|
| before | `''` | `dropped_sanskrit_span`, `empty_russian` |
| after | `{#paTin#}¦ <ab>s. u.</ab> <hom>2.</hom> {#paT#}.` | **(none)** |

The phrase table is why this is safe on `s. u.`: a standalone `u.` is *und* → «и», but `s. u.` is
*siehe unter* → «см.», so phrases are matched before single words and a word-by-word map that
would produce «см. и» is impossible by construction. `python src/pilot/xref_vocab.py` proves
12/12, including a drift guard asserting the phrase map agrees with `pwg_ab_ru.RU_MAP` on all
4 shared keys. Registered in CI.

## 3. `_atura` — cleared by rules that already existed

`_atura`'s translation is substantively good; the defects were glyph-level. Both repairs were
already ruled and implemented in this repo, so nothing new was written:

* `fix_d3` in
  [`fix_wrapper_defects.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_wrapper_defects.py)
  — rewrap `«…»` to `{%…%}` **iff** the DE gloss count equals the RU guillemet count (PR #789,
  26-07-2026; `{%…%}` is the store's documented convention, a guillemet rendering is drift).
  9 spans rewrapped, every sense count-matched, so none was left for review.
* `apply_no_yo` in
  [`ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py)
  — the H1305 `R1_yo` rule. 2 ё removed (`повреждённый`, `влюблённый`).

| | flags |
|---|---|
| before | `gloss_wrapper_became_guillemet`, `markup_wrapper_dropped`, `suspicious_lexicographic_with_text_signal` |
| after | `suspicious_lexicographic_with_text_signal` |

Both wrapper flags clear. The residual is a soft report-only signal that was present before the
rework as well, so this lane neither introduced nor was asked to remove it.

## 4. `_apta` — deliberately NOT repaired

`_apta`'s two `markup_wrapper_dropped` firings are **not** the guillemet class: `fix_d3` reports
0 eligible spans because there are no guillemets at all. The Russian gloss text is present but was
written *unwrapped* — e.g. DE `{%Quotient%}` → RU `частное` with no `{%…%}` around it, and
`{%Haarwulst%}` → `валик волос` inside a longer sense that also carries `{#jawA#}` and two `<ls>`
references.

Wrapping those mechanically would mean **guessing the gloss boundary inside a translated sense**,
which is precisely what PR #789 refused to do when it left ~46–54 count-mismatch rows for manual
review rather than risk a positional swap corrupting content. That refusal is a standing ruling,
so `_apta` was not touched. It needs one of:

1. a re-translation of the affected senses (a model call — blocked with Lane A, see §5), or
2. human review of the seven senses listed above.

## 5. Lane A is blocked twice over, and the second blocker is the harder one

Lane A (the 16 never-attempted keys) did not run. Two independent blockers, found in this order:

1. **Host RAM.** The handoff's hard precondition is ≥ ~4 GB free physical memory. Measured
   **2.38 GB, then 1.61 GB** of 15.85 GB with 6 live `claude.exe` (~2.9 GB resident) — the same
   condition that produced H3654's `0xC0000142` (`STATUS_DLL_INIT_FAILED`) at 53 ms. Clearing this
   is mechanical: close harness windows and re-measure.
2. **A cost-bounded window on this lane is currently *unrunnable*, whatever the RAM does.** While
   this session worked, [H3659](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3659-Opus_SanskritLexicography_h3157-residual-c1-paid-no-pwg-window_28.08.26.md)
   fired the c1 gate for real and got a clean **GO** (health 23 252 ms, route 7 296 ms, canary
   `LIVE_GO`) — and the window still stopped `STOP_COST_UNEVALUABLE` with **zero generation
   calls**. `bounded_supervisor` tests `budget_cap is not None and not _durable_cost_evaluable` at
   the top of the drain loop, before pulling any work; `--cost-ceiling` sets `budget_cap`, and
   Max-route calls carry no usage telemetry, so the reservation ledger is never priced and the
   first iteration ends the run. FINDINGS §602.

That is decisive for this handoff, because H3658 explicitly instructs Lane A to **"check the cost
gate before spending"** — i.e. to run bounded. A bounded run cannot start. The disclosed escape is
`--allow-unbounded` (calls and windows still bind; only dollars go unmeasurable), which H3659
deliberately did not take because the authorization on record said *bounded*, and swapping one for
the other on an agent's judgment is the H2851 guard-tunnelling defect. The same reasoning binds
here, so Lane A stops rather than escaping the guard.

**And the ration moved.** When this session checked, nothing had been logged for the 29-08 UTC day.
H3659 has since spent one — c1 is now at **1 of 2** for the day, so a further attempt should not be
fired casually, and the ≥ 6 h spacing runs from H3659's probe, not from the 28-08 one.

## 6. What was NOT done, and why

* **Nothing was promoted into the live store.** `_atura`'s repair is proven in-memory only. The
  promotion should happen once, together with Lane A's 16 keys, rather than writing the store
  twice; and `_apta` still has no verdict, so the batch is not yet clean end-to-end.
* **The repairs were not auto-wired into the generation lane.** `prompt_rule_audit` deliberately
  *detects* the wrapper classes at generation time while the *repair* stays an explicit pass —
  auto-healing inline would mask the signal that stops the residual growing. Changing that is a
  policy decision, not a defect fix.
* **The English lane is unchanged.** `render_xref_ru` fires only for `field == 'russian'`; an EN
  twin would need its own vocabulary ruling.

## 7. Caveat on the flag numbers

The before/after flag sets above come from `prompt_rule_audit.semantic_risks` run directly on the
card, not from the full `audit_window` pass that produced
[`H3654_C1_RERUN_28-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3654/H3654_C1_RERUN_28-08-2026.md).
The two agree on every flag this lane set out to clear, but the window audit reports
`suspicious_lexicographic_with_text_signal` for `_apta` only, while the direct call reports it for
`_atura` too — so treat the residual counts, not the cleared ones, as approximate.

_Dr. Mārcis Gasūns_
