# H4270 — c1 `_apta` re-test with the hardened prompt: the funded wrapper defect is FIXED, the audit requeues on a NEW single-sense defect (masked English span translated)

_Created: 06-09-2026 · Last updated: 06-09-2026_

Executor: OxAlpha (`glm-5.3-flash`, opencode lane). Handoff:
[H4270](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4270-OxAlpha_SanskritLexicography_apta-gloss-wrapper-prompt-hardening-retest_06.09.26.md) ·
prior window: [H4015](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4015/H4015_C1_WINDOW_RESULT_06-09-2026.md).

**Headline: the prompt hardening did exactly what it was funded to do — and the window still
does not ship.** All 7 model-visible German `{%…%}` wrappers are now preserved in the Russian
output (H4015: 1 of 8), `markup_wrapper_dropped` **does not fire anywhere**. The requeue now
comes from a **different, new, single-sense defect**: for the one ENGLISH masked span the model
**invented a `{%…%}` wrapper and translated it** (`{%equation of a degree%}` →
`{%уравнение степени%}`) instead of echoing the `{Tn}` token for deterministic restore.
Named stop: **AUDIT_DEFECT_REQUEUE, 3rd occurrence** — no third window; residual back to MG.

## 1. What ran

| step | result |
|---|---|
| Prompt hardening | `MASK_PREAMBLE` gains the GLOSS WRAPPERS `{%…%}` preservation block (GAPS §17 GLOSS-DE-RESIDUE) + the `{%ein%}`→`{%некий%}` worked example; `window_selftest` 221/222 (only the red-by-design parity gate fails), canary golden regenerated; commit `c9fdb9ff9` |
| Gate | Fresh c1 GO receipt from the 18:37Z sitting reused (health PASS 25 736 ms wall / 11 179 ms api; canary GO 3/3) — today's probe ration was exhausted (2/2), receipt valid ≤ 6 h |
| RAM | 3 148 MB free < the 3.5 GB floor; **MG ruled in chat 06-09: fire** (H4015 ran clean at 2 736 MB, same single-child shape; H3654 death was 1.7 GB with 6 concurrent children) |
| Window `_apta` | **success** — 139.9 s, first attempt, `null_keys: []`, 1 paid call (reservation `2bce110e…` finalized, `cost_evaluable: false`), manifest sha `9523136b…`, run `h4270-apta-20260906T2030Z` |

## 2. The funded defect — FIXED

Per-sense counts across the returned card (17 senses, 2 PW records):

| | DE source | RU output (H4015) | RU output (H4270) |
|---|---:|---:|---:|
| `{%…%}` gloss wrappers | 8 (7 DE + 1 EN-masked) | **1** | **8** |
| `«…»` guillemets | — | 0 | 0 |
| `<ls>` paired refs | 7 | 7 (preserved) | 7 (preserved; 14 whole-card incl. the `german` echo) |
| `{#san#}` spans | 8 | 8 (preserved) | 8 (preserved) |
| `{#jawA#}` | present | present | present |
| `markup_wrapper_dropped` | — | ×2 (hard requeue) | **0 (gate silent)** |

## 3. The NEW defect — one sense, rule over-application on a masked span

`audit_window.py` (canonical `PWG_INPUT_DIR`, H4015 finding honoured):

| gate | exit | requeue |
|---|---:|---:|
| final_schema / nws / sense_loss / translation / stage2_mechanical / sense_dupes / ru_style | 0 | 0 |
| prompt_semantic | 1 | 1 — high-confidence `foreign_gloss_translated` |
| coverage | 1 | 1 — `COVERAGE-OVER(17/7)`, **identical in H4015** (pre-existing shape, not new) |

The one high-confidence risk (sense 4b):

```
DE: b〉 *{%equation of a degree%}.      (EN span — pwg_mask classifies it English → masked to {Tn})
RU: б) *{%уравнение степени%}.          (model INVENTED a wrapper and translated the masked content)
expected RU: б) *{%equation of a degree%}.   ({Tn} echoed → deterministic restore, EN literal kept)
```

The GAPS convention for non-German `{%…%}` (Latin/English) is mask + verbatim restore — the
model must never see or translate them. The new GLOSS WRAPPERS rule ("every `{%…%}` span MUST
reappear around its translation") was over-applied to this span the model could not see:
it fabricated a wrapper with a Russian translation inside. The `{Tn}` multiset guard is SOFT,
so the card was kept and the deterministic audit caught it — the gate chain worked as designed.

Score context: semantic risk score 170 (H4015: 67), high-confidence 1 (H4015: 0) — the single
4b risk alone crosses the confidence line; the other 7 risks are the known medium
`suspicious_lexicographic_with_text_signal` class (report-only per handoff).

## 4. Named stop

**AUDIT_DEFECT_REQUEUE — 3rd occurrence (H3654 b2, H4015, H4270). Per the handoff: no re-burn;
the residual goes back to MG.** Promotion, TM refresh, store gates and the defect-list removal
were NOT attempted. `_apta` stays on `H3654_defect_keys.txt` and the store is untouched.

## 5. The decision now on MG's desk

The original fork (option b hand-marking / option c unwrapped-acceptance) is now joined by a
third, precisely-scoped option — the defect class shrank from "7 wrappers dropped everywhere"
to "1 masked span mishandled":

1. **One-clause rule tightening + one 4th window** (needs authorization): append to the same
   GLOSS WRAPPERS block — "this rule applies ONLY to `{%…%}` spans visible in your masked
   source; a `{Tn}` masked span stays `{Tn}` verbatim — never translate it, never wrap it"
   (+ selftest fixture pinning the clause). Same 1-key shape, ~$0.15.
2. Option b: human hand-marking of `_apta` (supersedes the 29-08 line).
3. Option c: unwrapped-acceptance ruling.

_Dr. Mārcis Gasūns_
