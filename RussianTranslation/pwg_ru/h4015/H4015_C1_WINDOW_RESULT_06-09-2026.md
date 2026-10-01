# H4015 — c1 `_apta` re-translation window: gate GO, window success, acceptance FAILED (wrapper dropped again)

_Created: 06-09-2026 · Last updated: 06-09-2026_

Executor: OxAlpha (`glm-5.3-flash`, opencode lane). Handoff:
[H4015](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4015-OxAlpha_SanskritLexicography_hapta-1key-retranslation-window_03.09.26.md).

**Headline: the paid call succeeded and the card is correctly refused.** DE `{%…%}` → RU plain-word
unwrapped, 7 of 8 gloss wrappers dropped with zero «» — the exact `markup_wrapper_dropped` /
never-emitted class this window was funded to clear. **Store untouched (11 519 rows). Nothing
promoted. `_apta` stays on the defect list.**

## 1. What ran (all preconditions met or waived)

| step | result |
|---|---|
| Gate attempt 1, 12:27:57Z | NO-GO — warm-up `rate_limit`, 429 "session limit · resets 7:10pm MSK". Fail-closed, no measured leg. 1 call, cost not evaluable. |
| Gate attempt 2, 18:28:42Z | **PASS** — warm-up 56 049 ms success; measured **25 736 ms** vs 80 000 wall ceiling. Spacing honoured: 6 h 0 m 45 s after attempt 1 (MG ruling in chat: wait out the ≥6 h wall; reset alone was not sufficient). |
| Canary `dq_canary_puregloss` | **GO** — 31.3 s, 3/3 senses, `null_keys: []`, receipt `h4015win/canary_receipt.json` judged 18:31Z. |
| Window `_apta` (1 key, 1 batch) | **success** — 137.2 s, first attempt, no retries, `null_keys: []`, result sha `f9f133e8baf4da47…`. |

Ration closed the day at 2 of 2 probe attempts. Durable evidence root `~/.pwg_ru_evidence/c1`
(#1034/H3663 §8 pattern — worktree-local receipts die with the worktree).

Manifest: `h4015win/execution_manifest.h4015win.json`, sha `d2372672ea1fd131…`, profile c1
(fingerprint `9321e2c1…`), nominal, `--no-tm`, `--budget=1`, model `claude-sonnet-5`, preflight
est $0.15/card, `over_ceiling: false`.

## 2. Why the acceptance fails — the measured comparison

Per-sense `{%…%}` counts across the returned card (17 senses, 2 PW records):

| | DE source | RU output |
|---|---:|---:|
| `{%…%}` gloss wrappers | **8** | **1** |
| `«…»` guillemets | — | **0** |
| `<ls>` refs | 14 | 14 (all preserved) |
| `{#san#}` spans | 16 | 16 (preserved) |
| `{#jawA#}` | present | present |

Worked example (sense rec0/s2): DE `a〉 {%ein%} <is>Arhant</is> <ls>H. 25</ls>.` → RU
`а) некий <is>Arhant</is> <ls>H. 25</ls>.` — `{%ein%}` translated correctly as `некий` but the
wrapper was **never emitted**. Translation quality is not the failure; markup fidelity is.

`audit_window.py` verdict: `PASS: 1/1 clean` on the markup-fidelity unit gate, SAN-LOSS sense-count
guard PASS, ru_style PASS — and the promotable verdict (`requeue.defect.keys.txt`) contains
**`_apta`**, clean list empty: 13 semantic risks, `high_confidence=0`, classes
`suspicious_lexicographic_with_text_signal` ×3 + `markup_wrapper_dropped` ×2.

## 3. Named stop

**AUDIT_DEFECT_REQUEUE — re-translation under the sanctioned recipe reproduces the defect.**
This is now **2 for 2 windows** (H3654 b2 and H4015) where the production prompt yields an
unwrapped-gloss card for `_apta`. H3658 Lane B ruled the class not deterministically repairable
(nothing to rewrap — no guillemets), PR #789 forbids guessing gloss boundaries, and the handoff's
own acceptance ("no `markup_wrapper_dropped` firing on the new output") is therefore not met.
Promotion and the defect-list removal (handoff §5) were **not** attempted — the guard would refuse
and the removal is gated on promotion.

Not authorized here and left to a human: another burn of the same recipe, a prompt/template change
that hardens gloss-wrapper emission (a pipeline change), or a standing-ruling change on unwrapped
glosses. The H3654 "hand-marking" option remains superseded.

## 4. Spend

5 paid calls total, all on c1: gate warm-up (429 refusal, `cost_evaluable: false`) + gate
warm-up + measured + canary + window. Per FINDINGS §597 the honest statement is "5 paid calls,
cost not evaluable" (`billing_mode: unknown_gateway` throughout); preflight estimate for the
window card was $0.15.

## 5. Coordinator lease note

The Mac's prep-only lease (`defect-repair-h4015-apta`, root `h3627-reingest`) could not prepare —
`prepare` has no path for rootless nominal keys ("no rootmap"), so it was left `blocked`. The fresh
`defect-repair:Apta` claim (12:22:40Z) expired at 18:22:40Z before the window fired at 18:35Z; the
run followed the H3663 precedent (worker directly off a tool-built manifest, no `begin-run` —
`begin-run` requires a prepared lease, which the coordinator cannot produce for this key class).

## 6. Next

A decision, not a re-run: either the prompt template gains an explicit gloss-wrapper preservation
instruction (needs its own authorized handoff + one re-test call), or `_apta` moves to human
review / hand-marking under a ruling that supersedes the 29-08 option-b line.

_Dr. Mārcis Gasūns_
