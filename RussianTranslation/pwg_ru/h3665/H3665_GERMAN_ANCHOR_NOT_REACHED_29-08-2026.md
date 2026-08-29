# H3665 — why `german_anchor` never fires on a span-drop card, and the counter that now says so

_Created: 29-08-2026 · Last updated: 29-08-2026_

Executor: **Opus 5 (`claude-opus-5`)**. Handoff
[H3665](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3665-Opus_SanskritLexicography_german-anchor-never-reached-span-drop-repair_29.08.26.md).
**Zero paid model calls.** Everything below is offline: two file reads, one replay against the
H3659 evidence root, one selftest.

Landed as **FINDINGS §608** — §606 and §607 were taken on `master` by an unrelated
plan-mode diagnosis and its retraction while this branch was open.

## Verdict in one line

The repair is not reached because the branch that invokes it and the branch that raises
`translation-fidelity-reject` are **disjoint by construction** — and even if it *were* invoked on
`hasita`, it would refuse with `nothing-missing`. Two independent gaps, not one.

## Step 1 — the bypass, with file:line

[`src/pilot/headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py),
`normalize_batch`. Line numbers are on `origin/master` at `5088eca8` (the pre-H3665 tree — §605
quotes L863/L798/L818, which are off by ~16 lines against the file as shipped):

| line | code | what it counts |
|---|---|---|
| **879** | `if count_card(card, '<ls') != inp['ls'] or count_card(card, '{#') != inp['sk']:` | the **`german`** field only — the gate that admits the repair |
| 888 | `ok, info = german_anchor.reanchor(masked, inp.get('skeleton') or '')` | the repair itself, reachable only from L879 |
| **902–906** | `if (count_card_field(card, field, '<ls') != inp['ls'] …): error = 'translation-fidelity-reject'` | the **`russian`/`english`** target field |

Line 901 (`if card is not None:`) is only reached when L879 was **False**, i.e. when the german
echo already counted exactly right. So a card that raises `translation-fidelity-reject` has, by
control flow, a *faithful* german echo — and the repair branch above it was never entered.
`count_card` is german-only by deliberate design (its own docstring), and
[`src/german_anchor.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/german_anchor.py)
says the same from the other side under **DELIBERATE SCOPE LIMITS**: *"The `german` field only.
The target-language field (`russian`/`english`) is NOT repaired."*

This half of the diagnosis is **already on `origin/master`** as
[FINDINGS §605](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md), landed
by H3659's own close ([PR #1952](https://github.com/gasyoun/SanskritLexicography/pull/1952),
pwg_ru 1.144.119) between H3665 being minted and being run. It is restated here with the exact
current lines rather than re-derived, and it is **confirmed**, not amended.

## Step 2 — `hasita` replayed offline

**The model's own card for `hasita~~h0_zz_pw` is not on disk anywhere.** `normalize_batch` sets
`card = None` the moment it raises the reject (L906–907), and `write_failed_envelope` fires only
on a **process-level** failure, which `hasita`'s batch was not. The H3659 evidence root
(`out.w09.json`, `status.w09.json`, `calls.w09v2.json`, `failed_envelopes/`) carries the verdict
and never the artefact — grep for `hasita` across it returns the manifest, the summary and the
harness, no card. **That is a third defect in its own right:** a content-reject discards the only
evidence that could diagnose it. The handoff's "replay the captured output" was not runnable as
written.

What survives is stronger than a reconstruction guess, though: the error string pins the card's
shape by control flow. Reaching L902 requires L879 to be False, so `hasita`'s german echo was
**exactly** `<ls> 2/2, {# 2/2`, and only `russian` was short.
[`replay_hasita_german_anchor.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3665/replay_hasita_german_anchor.py)
rebuilds that proven state from the manifest skeleton (`{T1}`…`{T11}`; `<ls>` = T6/T7, `{#…#}` =
T1/T4) and runs the real `german_anchor`:

```
german echo    : {T1} {T8} {T2} {T3} {T9} {T10} {T4} {T11} {T5} {T6} {T7}  (11)
russian echo   : {T1} {T8} {T2} {T3} {T9} {T10} {T4} {T11} {T5} {T6}       (10)

german_anchor.plan     -> ok=False info={"reason": "nothing-missing"}
german_anchor.reanchor -> ok=False info={"reason": "nothing-missing"}
```

**Stated plainly, as the handoff requires: the repair CANNOT repair this card.** So the answer is
the handoff's second branch, not its first — the wiring gap is *not* the whole defect. Even with
perfect wiring, `plan()` refuses `nothing-missing`, because every source span **is** present in
`german`; the loss is in the translation, where the span has no deterministic home. This sharpens
§605 from *"cannot fire"* to *"cannot fire, and would decline if it did"* — closing the door on a
future session trying to fix this by moving the call site.

## Step 3 — the counter is now falsifiable

`german_anchor_repairs: 0` is the same number for *nothing to repair* and *never invoked*; that
ambiguity is exactly what H3144 read the wrong way. Both lanes now emit two more fields:

| summary field | meaning |
|---|---|
| `german_anchor_repairs` | unchanged — cards saved by a re-injection (stamp-derived) |
| `german_anchor_invocations` | how many cards actually entered the repair branch |
| `german_anchor_not_reached` | keys nulled by a **later** guard, so the repair never saw them |
| `german_anchor_outcomes` (headless only) | per key: `repaired` · `verify-failed` · `refused:<reason>` · `repaired-then-rejected` · `not-reached` |

Three states, three distinct summaries — `hasita` is row 3, and before this change row 3 was
byte-identical to row 1 on every `german_anchor` field:

| card | repairs | invocations | not_reached |
|---|---|---|---|
| clean | 0 | 0 | `[]` |
| german-side drop | 1 | 1 | `[]` |
| **translation-side drop (the `hasita` shape)** | **0** | **0** | **`['agni']`** |

`repaired-then-rejected` closes a fourth silent hole found while wiring this: a card the repair
*did* fix but a later guard still nulled loses its stamp along with `card = None`, so the
stamp-derived `german_anchor_repairs` silently forgets the repair ever happened.

**On §605's objection.** §605 argues the `not_reached` state "would be permanently true here and
still carry no information". The code-shape half of §605 is right and is confirmed above; this
half is not. The number is read from a *summary*, by a later session that does not have the two
docstrings in front of it — which is precisely how §604 was written. A window that reports
`repairs 0 · invocations 0 · not_reached ['hasita~~h0_zz_pw']` cannot be misread as a healthy
lane; `repairs: 0` alone was, once, at the cost of a paid window.

### Where it lives

- **Headless (production route):**
  [`headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
  — the per-key trace is written in `normalize_batch`, kept on the engine (`resolve_group`
  consumes its rows for `card`/`error` only and drops the rest), and re-attached in
  `_finish_payload`.
- **Batch JS lane:**
  [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  `accept()` — same two counters, so a summary from either route reads the same way (the C-01/C-17
  don't-let-the-twins-drift lesson).

### The pin

- `headless_worker_selftest.test_h3665_german_anchor_counter_is_falsifiable` — the three fixtures
  above, **plus the invariant itself**: every key in `summary.failures` whose reason is
  `translation-fidelity-reject` / `unmapped-token-reject` must appear in
  `german_anchor_not_reached` or carry an outcome. A rejected card can no longer leave both
  counters silently at zero.
- `german_anchor_test.js` CONTROL 2b / 2c, run through the REAL emitted harness by
  `window_selftest.test_german_anchor_repair_behavioral`.

## Evidence

- `headless_worker_selftest: PASS` (includes the new test)
- `window selftest: ran 216/216 defined — 216 passed, 0 failed`
- `german_anchor_test: PASS` (22 checks, incl. the two new ones)
- `LANG PARITY LEDGER: 103 entries, all verdicts complete, no drift` — 34 entries re-hashed after
  verifying the verdicts still hold; every change here is language-agnostic telemetry, no
  RU/EN-specific logic moved.
- **Zero paid model calls.** No window was run, no lease consumed, no store write.

## What is NOT fixed, deliberately

The target-side span drop still has **no repair at all** — that is §605's consequence (3) and it
is net-new work, not diagnosis: either a target-side re-anchor (boundary-guessing inside a
translated sense, which [PR #789](https://github.com/gasyoun/SanskritLexicography/pull/789)
refuses as a standing ruling) or an explicit ruling that target-side drops requeue rather than
repair. A human should decide which. Nothing here changes the reject; it only stops the telemetry
from hiding it.

The **discarded-card** defect from step 2 is also left open: a `translation-fidelity-reject` still
throws away the artefact that would diagnose it. Capturing rejected cards under the resolved
evidence root is the obvious next slice and wants its own handoff.

_Dr. Mārcis Gasūns_
