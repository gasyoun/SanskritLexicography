# PWG TM Wave 1 Track B — the 10 serious-error rows: taxonomy and sidecar repair

_Created: 27-08-2026 · Last updated: 28-08-2026_

Opus 5 (`claude-opus-5`), [H2877](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2877-Opus_RussianTranslation_pwg-tm-w1-serious-error-10-repair_16.08.26.md). Gate under repair: the H2684 independent n=400 sample recorded in [PWG_TM_GROK46_WAVE1_TRACK_B_14-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_GROK46_WAVE1_TRACK_B_14-08-2026.md).

## Status: 10/10 classified and repaired in a sidecar — the gate is NOT re-scored

Every one of the ten Grok 4.5 serious flags is typed, span-localised and repaired. The repairs live in a sidecar. **The promoted Wave-1 dump is unchanged, so the n=400 serious-error rate is still 10/400 = 2.5 percent and the independent gate still fails.** Nothing here licenses a claim that Wave 1 now clears the 1 percent ceiling; see [What this does not claim](#what-this-does-not-claim).

| Result | Value |
|---|---|
| Sample | 400 (H2684, seed 2684), serious 10 = 2.5 % |
| Rows classified | 10 / 10 |
| Judge-named defect spans left unaddressed | **0** |
| Repair actions | 13 across the 10 rows |
| Rows changed | 10 |
| False Russian claims standing after repair | **0** |
| Rows that become `uncertain` (untranslated German residue) | 9 |
| Same mechanism elsewhere in the sample, unflagged and out of scope | 5 rows (13/400 carry it; 8 were flagged) |
| Paid Claude generations | **0** |
| Grok 4.5 after-score (independent) | **0/10 serious** — run 28-08-2026, $0.138366, `cost_evaluable: true` (H3611) |
| Projected n=400 if the repairs were applied | serious 2.50 %→**0.00 %** PASS, but fidelity 99.50 %→**97.25 %** — **gate still FAILS** |
| Wave-1 Track B artefacts byte-identical before/after | yes (20 files) |

## Every serious error is one `{%…%}` span

The single most useful structural fact: **all ten flags localise to a single span**, and in nine of ten cases the rest of the fragment is already correct. Wave-1 targets preserve span count and order against their German source, so a positional span alignment isolates the defect exactly. The dominant mechanism is not bad translation — it is the exact-source reuse lexicon returning a Russian string that belongs to a longer collocation.

## Typed taxonomy

`Covered by` names the already-shipped policy that would prevent the class on a later wave. `—` is a live gap.

| Code | Class | Rows | Mechanism | Covered by |
|---|---|---|---|---|
| **T1** | unsafe short-gloss source reuse | 5 | A whole-fragment short or function-word German span matched the exact-source lexicon; the Russian it carried belongs to a longer collocation in the publication record. | `pwg.tm.wave2.defaults.v1` `SHORT_GLOSS_DENYLIST` |
| **T2** | short-gloss defect propagated into a sense wrapper | 3 | Sense-class exact-source reuse is off, but `merge_glosses` copies the gloss map into the wrapper, so a T1 defect resurfaces at sense level. | same denylist, transitively |
| **T3** | untranslated German residue promoted inside a sense wrapper | 3 | A *promoted* sense wrapper still carries source-language `{%…%}` spans. No gate rejects a wrapper for source-language residue. | **—** |
| **T4** | archaic-orthography content gloss reuse | 1 | `thun` (archaic *tun*) is a content word, so the function-word denylist does not reach it, and the lexicon reused an unrelated Russian target. | **—** |
| **T5** | ambiguous abbreviation collision | 1 | The house table read `<ab>v. a.</ab>` as *videlicet* and emitted a translated Russian abbreviation. PWG uses it for *vor allem* — and house convention is to copy `<ab>` tokens verbatim in any case. | **—** |

T1 and T2 — eight of the ten — are **already fixed forward**. `SHORT_GLOSS_DENYLIST` in [`src/pwg_tm_wave2_policy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_wave2_policy.py) (H2721, extended by H3434 wave 3) denies `jmd`, `die`, `gewachsen` and `mit`. Those four tokens are exactly the T1/T2 offenders. Wave 1 is immutable, so the rows survive in the promoted dump, but the mechanism cannot re-enter on Wave 2 and later.

T3, T4 and T5 — three rows — are **not covered by anything shipped**. That is the finding worth carrying forward.

### T4 is demonstrably live, not historical

The check that settles it: query the source lexicon **with the wave-2 policy switched on** and it still returns the bad target.

```text
definition_gloss  {%thun%}   denied=False  ->  {%класть%}
definition_gloss  {%Jmd%}    denied=True   ->  None
```

`thun` passes the denylist because it is a content word, and the lexicon happily hands back `{%класть%}` (“to put”) for a gloss that means “to do”. A Wave-2 or Wave-3 run over any headword whose entry carries a bare `{%thun%}` gloss reproduces this defect today. The same shape reaches every archaic-orthography content word PWG uses (`thun`, `Thier`, `Theil`, `giebt`, …); only the four function words above are fenced.

## How far the class reaches beyond the ten flags

The judge flags rows; the denylist describes a mechanism. Those two footprints are not the same, and the difference is measurable — `reach` counts every row whose span alignment shows a denylisted German span taking a different Russian target, bucketed by what the judge said about that row.

| Population | Rows | Carry a denylisted-span defect | Judge verdict on them |
|---|---|---|---|
| `adjudication400.jsonl` (the gate sample) | 400 | **13 (3.25 %)** | 8 serious · 2 equivalence-fail non-serious · **3 scored clean** |
| `wave1_b_slice/promoted.jsonl` (first slice) | 679 | **0** | — |

| Count | Span | Wave-1 target | Reading |
|---|---|---|---|
| 6 | `{%Jmd%}` | `{%поручать кому-л.%}` | corruption — but only **5** rows were flagged serious |
| 1 | `{%gewachsen%}` | `{%соответствующий, способный справиться%}` | corruption |
| 1 | `{%die%}` | `{%боги%}` | corruption |
| 1 | `{%mit%}` | `{%имевший половую связь с%}` | corruption |
| 1 | `{%bei%}` | `{%у%}` | **correct** |
| 1 | `{%und%}` | `{%и%}` | **correct** |
| 1 | `{%zu%}` | `{%к%}` | **correct** |
| 1 | `{%wie%}` | `{%как%}` | **correct** |

Two things follow, and both are new.

**The sixth `{%Jmd%}` is unflagged.** Six rows in the sample carry the identical `{%Jmd%}` → `{%поручать кому-л.%}` corruption; five drew a serious flag and one did not. This is the severity inconsistency [FULL_DH_STANDARDS_AUDIT_PWG_RU_22-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FULL_DH_STANDARDS_AUDIT_PWG_RU_22-08-2026.md) (H3291, Fable 5) noticed on qualitative re-adjudication, now counted. **This handoff repairs the ten flagged rows only** — the sixth `Jmd` row is outside its named scope and is left untouched and stated here rather than silently swept in.

**The denylist is coarse, and its cost is now measured.** On this sample it intercepts 9 corrupt fills and 4 correct ones (`bei`→«у», `und`→«и», `zu`→«к», `wie`→«как»). That trade is clearly worth taking — the corrupt fills are false semantic claims and the correct ones are trivially re-derivable — but it is a trade, and nobody had priced it before. It also means a Wave-2 quarantine rate slightly above the Wave-1 baseline is expected behaviour, not a regression.

The slice reading (0 / 679) is genuine but must not be over-read: `wave1_b_slice` is the earlier first-slice population, not a random draw from the 655,332 promoted rows, so it bounds nothing about the full dump.

### Cross-check against the independent re-adjudication

H3291 re-scored all 20 decisive rows of this same receipt on 22-08-2026 and reached the same mechanism from the other direction — it named "the corrupted deterministic fill that renders the argument-slot placeholder `Jmd` as «поручать кому-л.»" a **template bug in the fill path, not model noise**, present in ≥5 of the 20 decisive rows across two fragment classes. That is T1 and T2 here, independently identified. It also judged 2 of the 10 borderline-overcalled — bare `{%gewachsen%}` as an idiom choice, and the severity inconsistency above — and showed the gate still fails at 8/400 = 2.0 % even if both are zeroed. Nothing in this pass depends on those two rows: `gewachsen` reverts to source like the rest, which is a safe outcome whether the flag was right or overcalled.

## The repairs

Deterministic only, four rules, applied in priority order. Anything outside a defect span stays byte-identical.

1. **R1 `ab_copy_through`** — an `<ab>…</ab>` metalanguage token is copied verbatim. This is the standing house convention, stated in the pilot translation prompt: keep the token, never expand it to its Russian meaning.
2. **R2 `revert_to_source`** — a denylisted span retries the policy-ON lexicon (which by construction refuses it), then reverts to the German source span and the fragment is marked `uncertain`.
3. **R3 `residue-refill`** — a target span still identical to its German source retries the policy-ON lexicon; on a miss it is left standing and the fragment is marked `uncertain`.
4. **R4 `attributed_revert`** — a span the Grok 4.5 note names as wrong that R1–R3 did not reach, and whose Wave-1 target the policy-ON lexicon still reproduces byte-for-byte. That byte match is the proof of unsafe-reuse provenance, so the lexicon is never consulted for the fix; the span reverts to source.

| # | Class | Headword | Defect span (German) | Wave-1 target | Repair | Rule | After |
|---|---|---|---|---|---|---|---|
| 1 | T1 | `arTay` | `{%Jmd%}` | `{%поручать кому-л.%}` | revert to source | R2 | `{%Jmd%}` |
| 2 | T1 | `krand` | `{%Jmd%}` | `{%поручать кому-л.%}` | revert to source | R2 | `{%Jmd%}` |
| 3 | T1 | `ruh` | `{%gewachsen%}` | `{%соответствующий, способный справиться%}` | revert to source | R2 | `{%gewachsen%}` |
| 4 | T1 | `saYj` | `{%Jmd%}` | `{%поручать кому-л.%}` | revert to source | R2 | `{%Jmd%}` |
| 5 | T1 | `viSveSa:2` | `{%die%}` | `{%боги%}` | revert to source | R2 | `{%die%}` |
| 6 | T2 | `gam` | `{%Jmd%}` | `{%поручать кому-л.%}` | revert to source | R2 | `{%Jmd%}` |
| 7 | T3 | `upakrama` | `{%Antritt, Anfang, Beginn%}` | `{%Antritt, Anfang, Beginn%}` | left as is | R3 | `{%Antritt, Anfang, Beginn%}` |
| 8 | T2 | `upakrama` | `{%mit%}` | `{%имевший половую связь с%}` | revert to source | R2 | `{%mit%}` |
| 9 | T3 | `upakrama` | `{%beginnt%}` | `{%beginnt%}` | left as is | R3 | `{%beginnt%}` |
| 10 | T2 | `vid` | `{%Jmd%}` | `{%поручать кому-л.%}` | revert to source | R2 | `{%Jmd%}` |
| 11 | T3 | `AtmasAt` | `{%an sich, zu sich, auf sich%}` | `{%an sich, zu sich, auf sich%}` | left as is | R3 | `{%an sich, zu sich, auf sich%}` |
| 12 | T4 | `AtmasAt` | `{%thun%}` | `{%класть%}` | revert to source | R4 | `{%thun%}` |
| 13 | T5 | `taruRa` | `<ab>v. a.</ab>` | `<ab>т. е.</ab>` | ab copy through | R1 | `<ab>v. a.</ab>` |

`{%имевший половую связь с%}` for `{%mit%}` (row 8) is the clearest illustration of the whole class: the bare preposition *mit* matched a publication record where “mit …” introduced a sexual-union sense, and the Russian came across whole.

### Why nine repairs restore German rather than supply Russian

Because supplying Russian here would be a generation, and a generation is exactly what the handoff fences. The rule the deliverable holds to: **a serious error is a false semantic claim, and the deterministic cure for a false claim is to withdraw it, not to replace it with a better guess.** Eight of the nine reverted spans have no safe lexicon target by policy; the ninth (`thun`) has one and it is wrong. So the repaired rows carry an honest untranslated German span and drop to the `uncertain` tier, which is where the Wave-2 policy would have put them in the first place.

Only `taruRa` (row 13) comes out fully clean and stays a promotion candidate, because copy-through *is* the correct target for an `<ab>` token.

| Headword | Tier after repair | Residue |
|---|---|---|
| `taruRa` | promoted candidate | — |
| `arTay`, `krand`, `saYj`, `gam`, `vid` | uncertain | `{%Jmd%}` |
| `ruh` | uncertain | `{%gewachsen%}` |
| `viSveSa:2` | uncertain | `{%die%}` |
| `upakrama` | uncertain | `{%Antritt, Anfang, Beginn%}` · `{%mit%}` · `{%beginnt%}` |
| `AtmasAt` | uncertain | `{%an sich, zu sich, auf sich%}` · `{%thun%}` |

## No paid generation was needed

The handoff allows at most one paid Claude generation **if any row is still empty**. No row was empty — all ten carried a target, and the defect was that the target was wrong, not missing. The paid branch therefore never opened. `paid_claude_calls: 0` in the receipt is a measured field, not an aspiration.

## Grok 4.5 after-score: not run in the H2877 pass

`XAI_API_KEY` is unset — absent from the process environment and from the one untracked `src/.env`, which carries `DEEPSEEK_API_KEY` and `OPENROUTER_API_KEY` and nothing else. The handoff's fence for that case is explicit: leave repairs as candidates, do not self-score. So the sidecar carries `after_score: null` and `after_score_status: "candidate_unscored"` on all ten rows, and no Claude adjudication was performed on Claude's own repairs.

An OpenRouter key **is** present and could in principle reach a Grok slug. It was deliberately not used *in this pass*: that is a different route from the one the H2684 gate recorded (`grok-4.5` direct, 8 shards × 50), it would have been an unbudgeted paid call on a money path this handoff never authorised, and a re-score on an unrecorded route is not comparable to the before-score it would be measured against. Firing it is a human decision, not an agent one.

> **Superseded 28-08-2026 — the spend was authorised, and the attempt is now blocked on account credit rather than on policy.** See the section below and [H3611](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3611-Opus_RussianTranslation_pwg-tm-w1-serious10-rescore_28.08.26.md).

What a future Grok 4.5 pass has to decide is narrow and stated: whether withdrawing a false Russian claim in favour of an untranslated German span clears `serious_error` for that row, or merely converts it into a fidelity miss. The nine reverts stand or fall together on that one question; `taruRa` is independent of it.

Under the H3299 pinned rubric that question already has a *pinned* answer — `german_residue` is listed non-serious, while `placeholder_rendered_as_content` and `wrong_lexical_meaning` are serious — so the expected result is that all nine reverts clear `serious_error`. That is a prediction, not a measurement, and confirming or refuting it is exactly what the re-score is for.

## The authorised re-score (28-08-2026): built, blocked on credit

MG authorised a paid re-score on 28-08-2026, naming **Grok 4.6**. Two facts reshaped that instruction, and both are recorded rather than quietly worked around.

**Grok 4.6 cannot be the independent judge — this repo's own gate refuses it.** [`src/pwg_tm_quality.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_quality.py) carries `FORBIDDEN_INDEPENDENT_JUDGES`, and `independence_errors()` rejects any `judge_model` beginning `grok-4.6`, because Grok 4.6 generated these Wave-1 targets. A 4.6 adjudication is a **self-score** by definition and cannot pass `verify`. It is still worth having — it was what was asked for, and 4.5-vs-4.6 agreement is informative — so the tool runs it into its own file, flags it non-independent, and never feeds it to the gate.

**`x-ai/grok-4.5` is reachable on the same key at the same price**, so the independent judge that actually answers the question needs no new credential.

The tool is [`src/pwg_tm_serious10_rescore.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_serious10_rescore.py). It follows the H3299 protocol rather than inventing one: each row is judged **blind** in its own call — the judge never sees that a repair happened, what the previous target was, or how H2877 classified it (`--selftest` asserts that absence) — the judge labels exactly one `defect_class`, and `serious_error` is **derived locally** from `SEVERITY_RUBRIC`, never taken from the model's reply (also selftest-asserted).

It first failed on money: the OpenRouter account was $0.26 overdrawn and *every* model returned HTTP 402, not only Grok — an account balance, not a model gate, with nothing charged. A funded key was supplied on 28-08-2026 and the run went through.

### Result: 0/10 serious — and the gate fails anyway, on a different floor

| Judge | Serious | Fidelity pass | Equivalence correct | Defect classes |
|---|---|---|---|---|
| `x-ai/grok-4.5` — **independent** | **0 / 10** | 1 / 10 | 1 / 10 | `german_residue` 9 · `none` 1 |
| `x-ai/grok-4.6` — self-score, non-independent | 1 / 10 | 1 / 10 | 1 / 10 | `german_residue` 8 · `none` 1 · `sense_absent_or_inverted` 1 |

`independence_errors` returns `[]` on the 4.5 file and flags **all ten** rows of the 4.6 file — the guard fires exactly as designed. Severity-consistency violations: none on either. Spend: **$0.138366** total ($0.052628 independent + $0.085738 self-score, 10,541 input / 16,471 output tokens over 20 calls), so this receipt is `cost_evaluable: true` — the first in this programme, against H2684's `calls: 65` with zero tokens.

**Every serious error is gone.** The nine reverts all score `german_residue`, which the H3299 rubric pins non-serious, and `taruRa` scores `none` — clean, exactly as the copy-through repair intended. The prediction the repair rested on is confirmed by an independent judge, not asserted.

**But the repair trades one failing floor for another.** Splice those verdicts over the frozen sample (`pwg_tm_serious10_rescore.py project`) and:

| Floor | Before (H2684) | Projected with the 10 repairs | |
|---|---|---|---|
| fidelity ≥ 98 % | 398/400 = **99.50 %** PASS | 389/400 = **97.25 %** | **FAIL** |
| equivalence ≥ 95 % | 382/400 = 95.50 % PASS | 383/400 = 95.75 % | PASS |
| serious_error ≤ 1 % | 10/400 = **2.50 %** FAIL | 0/400 = **0.00 %** | PASS |

All ten rows scored `fidelity: pass` *before* the repair — the judge considered a wrong Russian gloss faithful-but-inequivalent. Restoring the German makes nine of them unfaithful, so fidelity drops 2.25 points straight through its floor. **The gate still fails; it has merely moved from the serious-error ceiling to the fidelity floor.**

That is the substantive finding of this pass, and it is a limit on the method, not a defect in it. Withdrawing a false claim is the right deterministic cure for a *serious* error and it demonstrably works. It cannot make Wave 1 pass, because nine of these rows do not need a withdrawal — they need an actual Russian translation of `{%Jmd%}`, `{%die%}`, `{%gewachsen%}`, `{%mit%}`, `{%thun%}`, `{%Antritt, Anfang, Beginn%}`, `{%beginnt%}` and `{%an sich, zu sich, auf sich%}`. Only `taruRa` is genuinely finished.

The two judges agree on 9 of 10 rows (0.90 class, 0.90 severity). The single split is `vid`: 4.5 calls it `german_residue` (non-serious), 4.6 calls it `sense_absent_or_inverted` (serious). Since 4.6 generated the target it is judging, its verdict carries no independent weight here — but the disagreement marks `vid` as the one row worth a human eye if these are ever promoted.

Artefacts: [`serious10_rescore_grok45.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_rescore_grok45.jsonl) · [`serious10_rescore_grok46.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_rescore_grok46.jsonl) · [`serious10_rescore_receipt.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_rescore_receipt.json) · [`serious10_projection.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_projection.json).

A no-cost alternative remains available for any future re-score: `pwg_tm_serious10_rescore.py packet` emits [`serious10_blind_packet.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_blind_packet.jsonl) and a self-contained [`serious10_judge_brief.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_judge_brief.md) that a Grok 4.5 session executes with no key at all — which is what H2684 itself did.

## What this does not claim

- **Not** that the n=400 serious-error rate has fallen. It is still 10/400 = 2.5 percent. The sidecar does not touch the sample or the dump.
- **Not** that the independent gate now passes. It fails, and `pwg_tm_generate.py --verify` still exits 1 on `independent_gate=fail`.
- **Not** a bulk repair. Ten rows, named by record id, drawn from the H2684 sample — no new draw, no second wave.
- **Not** a Wave-2 policy change. `thun` is *not* added to `SHORT_GLOSS_DENYLIST` here; that is a Wave-2 write and out of scope. It is recorded as a gap below.
- **Not** self-scored. No Claude judgement stands behind any repair's correctness.

## Wave-1 immutability

The repair tool hashes every Wave-1 Track B artefact on disk before and after the run and refuses to exit 0 unless the two snapshots are identical.

| Directory | State | Files hashed |
|---|---|---|
| `wave1_b_slice/` | present | 15 |
| `wave1_b_receipt/` | present | 5 |
| `wave1_b/` | **absent from disk** | 0 |

Stated plainly: the full 655,332-row promoted dump is **no longer on disk** — the gitignored resumable dump directory is gone; only the 1.5 MB slice and the compact receipt survive. Byte-identity is therefore *proven by hash* for the 20 artefacts that exist, and *asserted by absence of any write path* for the full dump, which this pass never opens. The committed lock on its contents remains the reconciliation receipt: manifest `f024ec4b…3d952a`, promoted 655,332, quarantine 97,779, accounted 753,111 / 753,111.

## Gaps routed forward

Three classes have no shipped defence. None is fixed here; all three are Wave-2-or-later writes.

1. **T4 — archaic-orthography content glosses.** `{%thun%}` returns `{%класть%}` from the policy-ON lexicon today. The denylist fences function words only; archaic content-word spellings need their own guard, and a token-frequency census over the source side would size it.
2. **T5 — `<ab>` tokens must never be translated.** House convention says copy through; the Wave-1 pipeline translated one anyway. A gate assertion — no `<ab>…</ab>` target may differ from its source — is a one-line mechanical check that would have caught this row at generation time.
3. **T3 — source-language residue in a *promoted* wrapper.** A sense wrapper reached the promoted tier carrying untranslated German. Promotion should require zero German `{%…%}` spans in the target.

## Reproduce

```text
cd RussianTranslation
python src/pwg_tm_serious10.py --selftest
python src/pwg_tm_serious10.py report \
  --receipt release/pwg_tm_canonical/wave1_b_receipt \
  --out-root release/pwg_tm_canonical \
  --out pwg_ru/serious10
python src/pwg_tm_serious10.py reach \
  release/pwg_tm_canonical/wave1_b_receipt/adjudication400.jsonl
python -m pytest tests/test_pwg_tm_generate.py tests/test_pwg_tm_canonical.py
```

`--selftest` asserts the taxonomy derivation, all four repair rules, and that R4 degrades to plain T3 residue when lexicon provenance is absent. `report` exits non-zero if any Wave-1 artefact hash moved. `reach` reproduces the 13/400 footprint table. The two existing suites (24 tests) pass unchanged — this pass adds a module and touches no shipped code path.

The gitignored inputs (`wave1_b_receipt/`, `wave1_b_slice/`, the publication TM) live only in the main clone; from a worktree, pass absolute `--receipt` / `--out-root` / `--publication` paths pointing at it.

Artefacts: [`pwg_ru/serious10/serious10_sidecar.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_sidecar.jsonl) (10 rows, before/after with SHA-256 on each target) · [`pwg_ru/serious10/serious10_receipt.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_receipt.json) · tool [`src/pwg_tm_serious10.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_serious10.py).

_Dr. Mārcis Gasūns_
