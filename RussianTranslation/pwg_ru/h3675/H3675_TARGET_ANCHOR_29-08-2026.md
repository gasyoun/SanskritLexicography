# H3675 — the target-side span-drop re-anchor: the other half of the class, repaired

_Created: 29-08-2026 · Last updated: 29-08-2026_

Executor: **Opus 5 (`claude-opus-5`)**. Handoff
[H3675](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3675-Opus_SanskritLexicography_target-side-span-drop-reanchor_29.08.26.md).
**Zero paid model calls.**

Landed as **FINDINGS §610** — lower numbers were taken on `master` by other sessions
while this branch was open.

## The ruling this executes

[FINDINGS §608](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (H3665)
closed the diagnosis and left one fork open: a `{Tn}` span dropped from the **translation**
had no repair at all, and the choice was between building one and ruling that such cards
requeue. **MG ruled `reanchor`, 29-08-2026.** This is that build.

## Why this is not the PR #789 boundary guess

[PR #789](https://github.com/gasyoun/SanskritLexicography/pull/789) is a standing refusal to
reconstruct a `{%…%}` gloss boundary that the model merely omitted — there the target text is
prose, the span has no marker left in it, and finding where it starts and ends means guessing
inside a translated sentence. That refusal stands and is untouched.

This is a different problem, and the difference is not a matter of degree:

- a `{Tn}` token is **opaque and atomic** — there is no boundary to find, only a position;
- the **same sense's `german` field is a surviving parallel** that still carries every token in
  order (guaranteed: reaching this guard at all requires the german count to have already
  matched);
- senses pair **1:1 by card schema** — one `german` and one target field on the same object —
  so there is no alignment step to get wrong.

The translation is never parsed. A token is restored to the position its own parallel already
names. That is present evidence, not inference.

## The rule

Per sense: `missing = tokens(sense.german) − tokens(sense[field])`, and each missing token is
re-injected next to its nearest surviving neighbour **within that sense**, measured in that
sense's own german text — with the **sense start and sense end as virtual anchors** when
nothing survives on that side.

Both virtual anchors earn their keep, and this is where `target_anchor` is strictly better than
its german sibling rather than a copy of it:

| german (anchor) | target (dropped) | result | why |
|---|---|---|---|
| `{T1} Feuer {T2}` | `огонь {T2}` | `{T1} огонь {T2}` | `{T1}` sits at offset 0 → **head** |
| `b {T3} {T4}` | `б {T4}` | `б {T3} {T4}` | prose ahead of `{T3}` → **before its successor**, not the head |
| `{T1} unverwirrt {T2}` | `{T1} невозмутимый` | `{T1} невозмутимый {T2}` | sense end nearer than the predecessor → **tail** |

`german_anchor` anchors against the card-wide **source skeleton**, whose first span really is
the headword and which has no per-sense end to measure to, so it takes an unconditional head
branch. A per-sense german parallel offers both edges. Using them is what keeps a citation on
the correct side of the prose it belongs to — an after-the-predecessor rule would have written
`{T1} {T2} невозмутимый`.

**Refusals** (the card then rejects exactly as before, carrying the reason):
`anchor-token-repeat` · `no-senses` · `foreign-token` · `duplicate-token` · `reordered-token` ·
`nothing-missing`. Anything that is not a pure order-preserving drop is left alone.

## `hasita` — the card that cost a paid window

[`replay_hasita_target_anchor.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3675/replay_hasita_target_anchor.py),
offline against the H3659 evidence root:

```
sense 2 german : {T11} {T5} {T6} {T7}
sense 2 russian: {T11} {T5} {T6}

german_anchor.plan     -> ok=False info={"reason": "nothing-missing"}
target_anchor.reanchor -> ok=True   reinjected=['{T7}']  stamp={"reinjected": ["T7"], "head": []}

sense 2 russian -> {T11}— 2〉 {T5} смех, хохот {T6}. {T7}

VERIFIER: every sense's russian token sequence now equals its german anchor exactly.
```

`{T7}` is `<ls>GAUT.</ls>`, and it lands at the end of sense 2 — exactly where the german
parallel puts it (`… {T6}. {T7}`). **`hasita~~h0_zz_pw`, requeued as unfixable across
H858 → H3144 → H3157 → H3659, is promotable.**

## Where it lives

- [`src/target_anchor.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/target_anchor.py)
  — `plan` / `reanchor` / `stamp` / `selftest` / `js_source`, the twin of `german_anchor.py`.
- [`headless_worker.normalize_batch`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
  — repair-then-verify at the `count_card_field` guard that used to be an unconditional
  requeue.
- [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  `accept()` — the same repair on the batch lane, interpolated from that one `js_source()`
  (the C-01/C-17 don't-let-the-twins-drift lesson).

**One non-obvious fix underneath both:** `restore_card` / `restoreCard` unmask **in place**, so
the german branch was consuming the very `{Tn}` tokens the target repair needs as its anchor.
Both lanes now restore a **copy**, and a german repair already applied to a card is re-stamped
after the target repair re-restores — otherwise `german_anchor`'s provenance vanishes silently
on a card dropped on both sides. That case is pinned in both lanes.

## What the store may receive is unchanged

Only cards that count exactly right on **both** sides. The remedy changed, the guarantee did
not. A target echo that is not a pure drop still rejects, now as
`translation-fidelity-reject: target-anchor <reason>` — the prefix is preserved deliberately so
every existing reader (summaries, RUN_LOG greps, the H3665 counters) still matches.

New telemetry, mirroring §608's: `target_anchor_repairs` · `target_anchor_invocations` ·
`target_anchor_detail` · `target_anchor_outcomes` (headless).

## Evidence

- `target_anchor selftest: 10/10 OK` · `german_anchor selftest: 8/8 OK`
- `target_anchor_test: PASS` — 22 checks through the **real emitted harness**, including the
  both-sides double repair and the refused-but-counted invocation
- `headless_worker_selftest: PASS`
- `window selftest: ran 218/218 defined — 218 passed, 0 failed` (two new tests)
- `LANG PARITY LEDGER: 104 entries, no drift` — registered as `target_anchor_repair_h3675`,
  verdict **SHARED**. The target field is a parameter, never a literal; the anchor is always
  `german`, identical on both lanes; `test_h3675_target_anchor_selftest` asserts that
  mechanically (identical repair for `russian` and `english`, the german field untouched, no
  language literal in the emitted JS).
- **Zero paid model calls.** No window run, no lease consumed, no store write.

## What this does not do

No card is promoted here. `hasita` and its class are *repairable* now; actually re-running the
`no_pwg` window is a separate, paid step and wants its own handoff with its own authorization
— and the two live gates from
[FINDINGS §602](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (cost
telemetry) and §604 (v2 manifest) still stand in front of it.

The **discarded-card** defect from §608 is also still open: a `translation-fidelity-reject`
that the repair refuses still throws away the artefact that would diagnose it.

_Dr. Mārcis Gasūns_
