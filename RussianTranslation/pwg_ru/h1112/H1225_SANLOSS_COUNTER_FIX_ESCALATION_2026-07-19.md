# H1225 addendum — the Nachtrag/corrigenda counter fix cannot be applied safely; ESCALATED

_Created: 19-07-2026 · Last updated: 19-07-2026_

**This addendum does not overwrite [H1150](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md) — it is a sibling reporting the outcome of [H1225](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1225-Sonnet_SanskritLexicography_sanloss-counter-fix-nachtrag-overcounting_18.07.26.md), which set out to fix `count_source_senses`'s over-count on H1150's 8 flagged Nachtrag/corrigenda cards.**

## Outcome

**Escalated per the handoff's own rail** ("Escalate if: the memo's proposed fix cannot be applied without also changing behaviour on the genuine whole-dropped-sense class — that is a real conflict, not a quiet call; record it and stop"). Neither of H1150's two proposed fix directions can be applied to `count_source_senses` (or to `accept()`) without either (a) leaving most of the 8 flags unfixed, or (b) provably breaking the guard's ability to ever detect a future drop on a materially large, currently-healthy class of real multi-preverb Nachtrag cards. **No code was changed.** `SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` remain `= false`, byte-unchanged.

Evidence script (read-only, no store mutation, no paid calls): [`src/pilot/sanloss_bundling_fix_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sanloss_bundling_fix_probe.py) → [`pwg_ru/h1112/sanloss_bundling_fix_probe.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/sanloss_bundling_fix_probe.json).

## Direction 1 — partition by "— {#headword#}" sub-lemma boundary: DISPROVEN

The natural reading of H1150's fix suggestion is: when a card's raw/concatenated source text carries a genuine line-opening `— {#headword#}` marker for **≥2 distinct sub-lemma names** (the exact marker [`root_segment_proto.UPA_RE`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/root_segment_proto.py) already uses to cut giant PWG root records into per-preverb sub-cards), the card is a bundled Nachtrag/Berichtigung entry and its true source-sense cardinality collapses — tested as "cap to 1".

**This correctly clears 5 of the 8:** `d_a~~h10_00_pwg00`, `d_a~~h13_00_pwg00`, `iz~~h14_00_pwg00`, `vas~~h13_00_pwg00`, `y_a~~h5_00_pwg00` (all: raw expected 2–4, cap-to-1 ⇒ no longer exceeds their emitted=1 row).

**It leaves 3 of the 8 unfixed** — a *within-one-sub-lemma* bundling shape the cross-headword signal structurally cannot see: `car~~h1_20_vi` (its own `{#vi#}` scope bundles ordinals 4 and 6 into one stored row `vi_main`, while the other 3 ordinals get their own rows — no *second* headword name ever appears), `n_i~~h5_11_pra` (same shape inside `{#pra#}`), `n_i~~h5_10_pari` (its `3-corr-8` row bundles a bare "3) *st.* 8)" corrigenda redirect with **no** `{#headword#}` marker of any kind). These three would need a semantic/content signal, not a structural one — see Direction 2.

**It also silently miscounts real cards that were never flagged and must never be capped.** Three concrete counter-examples from the live store, each a genuine multi-preverb Nachtrag/Berichtigung entry that the pipeline *did* split into several distinct stored rows (one per real correction), each of which also happens to carry ≥2 distinct `— {#headword#}` names:

| key | raw `count_source_senses` | cap-to-1 | real emitted rows | what capping would do |
|---|---:|---:|---:|---|
| `_ap~~h3_00_pwg00` | 3 | **1** | 7 | blinds the guard to a future drop of up to 6 of its 7 real preverb corrections |
| `vah~~h3_00_pwg00` | 2 | **1** | 3 | blinds the guard to a future drop of up to 2 of its 3 real corrections |
| `iz~~h8_00_pwg00` | 3 | **1** | 10 | blinds the guard to a future drop of up to 9 of its 10 real corrections |

None of these three is *currently* flagged (raw ≤ emitted already), so capping doesn't change today's false-flag count — but it silently degrades `source_senses` from a real, useful lower bound (3, 2, 3) down to a value (1) that is satisfied by *any* non-empty output, for cards that legitimately hold many real, independently-droppable senses. This is exactly "changing behaviour on the genuine whole-dropped-sense class" the handoff rail warns against, just manifesting on a population (`_ap`, `vah`, `iz~~h8`, and structurally any card of this shape) broader than the 8 named examples.

**Why no cap value threads this needle.** The one fact that actually separates `d_a~~h10` (correctly collapses to 1 real row) from `_ap~~h3` (correctly stays split into 7 real rows) is **the pipeline/model's own bundling-vs-splitting decision, made at generation time** — not recoverable from the raw source text's structure alone, because both cards' *raw* text has the same shape (a base scope plus several `— {#other#}` corrigenda blocks). `count_source_senses(raw)` is stamped **before** generation (`gen_opt_harness2.py` line ~1010, `INPUTS[k].source_senses = count_source_senses(raw)`, called before any `agent()` call) — the information needed to draw the line does not exist yet at the point this function runs in production. A cap of "1" fixes the 5 and breaks `_ap`/`vah`/`iz~~h8`; a cap of "count of distinct sub-lemma names" breaks nothing but also fixes 0 of the 8 (a bundled card's own distinct-name count already meets or exceeds any such cap). No value in between is derivable from text structure alone.

## Direction 2 — accept() verbatim-content check: untestable via the existing offline harness

H1150's cheaper alternative — "have `accept()` additionally check whether every 'extra' ordinal's content is verbatim present somewhere in the emitted card before counting it as a shortfall" — is architecturally sound *in production* (source is read pre-generation; the candidate is whatever the model independently returns, so a genuine drop's content is, by definition, never verbatim-findable in the candidate). But **[`softguard_falseflag_measure.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/softguard_falseflag_measure.py)'s own reconstruction makes this direction untestable offline**: `build_eligible_cases` builds both the "source" (`concat_de`, used to compute `exp`) **and** the "candidate" (`cases[]['senses']`, fed to the real `accept()`) from the *same* store rows —

```python
concat_de = '\n'.join(r.get('de') or '' for r in rows)                       # -> source
'senses': [{'german': r.get('de') or '', 'russian': r.get('ru') or ''} for r in rows]  # -> candidate
```

A verbatim-presence check comparing "source content" against "candidate content" is therefore **tautologically true for every single card measured this way** — it would report 0 false flags across the whole 865-card denominator regardless of whether `count_source_senses` itself is fixed. That is not evidence of a fix; it is evidence the harness's own reconstruction methodology cannot exercise this direction at all (documented already, independently, as the "reconstruction-boundary caveat" and "structural blind spot" in H1150's own memo — this addendum just traces the same limitation to why Direction 2 specifically can't be validated this way).

Making Direction 2 real requires the check to live in the **live** `accept()` inside [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) (where source and candidate genuinely are independent) — an edit to actively-used live-generation JS that cannot be validated without either a live (paid) generation pass or substantial new JS-side test scaffolding beyond what `accept_sensecount_test.js`'s extraction pattern already covers. Both are outside this handoff's read-only / zero-paid-calls rail.

## What would actually move this forward (human `@DECIDE`)

1. **Accept the residual 8/865 (0.9%) false-flag rate as permanent, un-fixable-by-counting noise** on this narrow Nachtrag/corrigenda-bundling shape, and factor that into the `SANLOSS_HARD_REJECT` arming decision (already queued as [ASK_BATCH_WAVE1_UNBLOCKS_2026-07.md](https://github.com/gasyoun/Uprava/blob/main/ASK_BATCH_WAVE1_UNBLOCKS_2026-07.md) B1) — e.g. arm with a documented allowlist-exception for this shape, or accept the false-positive requeue cost as cheap relative to catching real drops elsewhere.
2. **Authorize a live-accept()-JS change** (Direction 2, properly scoped) as its own handoff, with either a live paid-call test window or new JS unit-test scaffolding to validate it before arming — a materially bigger, riskier change than this handoff was scoped for.
3. **Leave SANLOSS permanently telemetry-only** for this specific bundling shape (detect the shape, but never reject on it, structurally distinct from a general arming decision) — a narrower version of (1).

No option requires urgent action; `SANLOSS_HARD_REJECT`/`TNMASK_HARD_REJECT` stay `false` regardless, so nothing is blocked today.

## Regression gate (unchanged, verified this session)

| Check | Result |
|---|---|
| `git diff` on `gen_opt_harness2.py` / `sense_count.py` | empty — no production code touched |
| `grep 'SANLOSS_HARD_REJECT = false'` / `'TNMASK_HARD_REJECT = false'` | both present, unchanged |
| `python src/pilot/window_selftest.py` | green (baseline, unaffected by a docs+evidence-script-only change) |
| `python src/pilot/lang_parity_check.py` | clean |

## Provenance

Executor: Sonnet 5 (`claude-sonnet-5`), H1225 (the handoff's own intended-executor line names Sonnet 4.6 `claude-sonnet-4-6`; this session ran as Sonnet 5 per the orchestrator's assignment — noted for the record, not a deviation this session chose). No paid calls, no live generation, no store mutation — read-only against the promoted store; the only writes are this memo and the new evidence script + its JSON output.

_Dr. Mārcis Gasūns_
