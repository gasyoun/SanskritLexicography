# H1651 — pwg_ru store wrapper-defect sweep D1–D4 (report)

_Created: 26-07-2026 · Last updated: 26-07-2026_

Handoff: [H1651](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1651-Sonnet_SanskritLexicography_pwg-ru-wrapper-defect-sweep-d1-d4_26.07.26.md)
· Model: Sonnet 5 (`claude-sonnet-5`) · Evidence base:
[VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md) §5
· Data-integrity issue: [SanskritLexicography#752](https://github.com/gasyoun/SanskritLexicography/issues/752)

## What this was

The audit's store scan (`pwg_ru_translated.jsonl`, 11,603 rows) found four defect classes no
review sheet had ever surfaced: D1 (Cyrillic wrapped in the Sanskrit `{#..#}` delimiter — 34
rows), D3 (`{%..%}` gloss wrapper rendered as guillemets — 338 rows per the audit's probe), D4
(gloss-slot count mismatch DE vs RU — 2,933 rows, flag only), D5 (excluded per the handoff —
mostly Latin/IAST false positives). This pass repairs D1, rules and gates D3, and triages D4
with a published precision figure.

## D1 — Cyrillic inside `{#..#}` (34 rows, 58 spans)

**Method:** [src/wrapper_defect_sweep.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/wrapper_defect_sweep.py)
`--d1-report`/`--d1-apply` — for every `{#..#}` span in `ru`, a Cyrillic word (`[А-Яа-яЁё]{2,}`)
inside it means the model wrapped a Russian gloss in the Sanskrit delimiter instead of `{%..%}`.
Repair is a pure delimiter swap (`{#` → `{%`, `#}` → `%}`); the content is untouched. Audited
all 34 rows / 58 spans individually before repair: **100% pure-Cyrillic gloss content, zero
genuine Sanskrit mixed in** — no ambiguity, so every hit was repaired in place rather than
parked to a requeue worklist (unlike H1302's class-b, which needed retranslation).

**Result:** a concurrent session independently applied the identical repair to the shared
canonical store (`pwg_ru_translated.jsonl.h1651.bak` — the pre-repair backup — carries the
34 broken rows verbatim, confirming the same defect set this pass measured) before this
session's own `--d1-apply` ran; this session's apply found 0 remaining and made no further
write. Post-repair rescan: **0/11,603 rows** carry Cyrillic inside `{#..#}`. Affected roots
(pre-repair): `vid` (24 rows), `dah` (3), `ahar` (2), `anaquh` (2), `brAhmI` (2), `anukampa` (1)
— matches the audit exactly.

**CI gate (stops recurrence):** `prompt_rule_audit.markup_sigla_risks` now raises
`cyrillic_in_sanskrit_wrapper` (HIGH / HIGH_CONFIDENCE — drives a requeue) whenever a live
generation's `ru` field wraps a Cyrillic word in `{#..#}`. Selftest:
`window_selftest.test_h1651_cyrillic_in_sanskrit_wrapper`.

## D3 — gloss wrapper rendered as guillemets

**Ruling:** yes, `{%..%}` is the store's structural gloss-wrapper convention — established by
every clean row in the store, by `braced_gloss_risks`' side-by-side echo logic, and by the
pre-existing `markup_wrapper_dropped` risk (which already treats a vanished `{%..%}` as a
defect). A Russian gloss rendered as bare `«..»` guillemets instead is convention drift, not an
accepted alternative rendering.

**Measured count (this session's methodology — see caveat):**

| population | rows | spans |
|---|---:|---:|
| DE `{%..%}` positions RU is missing (`markup_wrapper_dropped` universe) | 2,795 | — |
| …of those, RU has a guillemet plausibly absorbing the missing gloss (D3) | **54** | **144** |
| …of those, RU has NO guillemet — bare unwrapped prose (D4 majority, see below) | 2,741 | — |

**Caveat:** the audit's own probe reported 338 D3 rows; this session's reproduction (deficit
`len({%..%} in DE) − len({%..%} in RU)`, capped by the row's guillemet count so an unrelated
ordinary quotation elsewhere in the row is never over-attributed) finds 54. The original probe
script was not available to re-run verbatim (not committed under any repo this session could
find), and a naive "DE has a gloss AND RU has any guillemet" test overcounts to ~386–404 — so
the true figure is somewhere in this range depending on exactly how positional correspondence
is defined. **Given that spread, a store-wide mechanical `«..»` → `{%..%}` substitution was
withheld this pass** (7 of 61 sampled rows with any guillemet had it for ordinary quotation,
unrelated to a converted gloss — see D4 below) — the same "don't guess, park it" posture H1302
applied to its class-b hits.

**Disposition:** worklisted, not bulk-applied —
[H1651_D3_GUILLEMET_GLOSS_WORKLIST_2026-07-26.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1651_D3_GUILLEMET_GLOSS_WORKLIST_2026-07-26.jsonl)
(54 rows, full `de`/`ru` + estimated span count, for a future targeted repair pass with
per-row confirmation). Gated report-only (LOW, never HIGH_CONFIDENCE — the translated content
is intact either way, only the markup differs) via `gloss_wrapper_became_guillemet` in
`markup_sigla_risks`, alongside the pre-existing `markup_wrapper_dropped`. Selftest:
`window_selftest.test_h1651_gloss_wrapper_became_guillemet`. D3 count is not driven to 0 this
pass — recorded here as deferred to the worklist, per the handoff's own acceptance clause.

## D4 — gloss-slot count mismatch DE vs RU

**Measured population:** 2,860 rows have `len({%..%} in DE) != len({%..%} in RU)` (audit's own
figure: 2,933 — same population, small definitional variance, not re-derived from their
script). Split: 2,795 DE-has-more (RU deficit), 65 RU-has-more (RU surplus).

**Precision, published per sub-pattern (random samples, seed 1651/2):**

| sub-pattern | rows | sampled | finding |
|---|---:|---:|---|
| RU deficit, no guillemet (bare unwrapped drop) | 2,741 | 25 | **25/25 (100%)**: the Russian translation is present and correct, only the `{%..%}` structural wrapper is missing — zero genuine content loss in the sample. Identical to the pre-existing `markup_wrapper_dropped` risk class (already gated, LOW/report-only). |
| RU deficit, guillemet present | 54 | — | this is D3 above, not re-triaged separately |
| RU surplus (RU wraps more than DE) | 65 | 5 | all 5 are DE prose that RU renders with an *added* `{%..%}` wrapper DE never had at that spot (DE's own source markup is itself inconsistent) — benign, arguably an improvement, not a defect |

**Disposition: no repair action.** The dominant sub-pattern (2,741/2,795 = 98.1% of the RU-deficit
population) is markup-fidelity loss with content intact — already covered by the existing
`markup_wrapper_dropped` soft gate, not a new class, and explicitly out of scope per the
handoff's non-goals ("re-translating anything beyond what a wrapper repair requires"). No
sub-pattern in this triage cleared a bar that would justify a mechanical fix beyond what D1/D3
already cover.

## D5 — excluded

Not implemented, per the handoff's explicit instruction (false-positive-heavy: the sample is
mostly Latin/IAST content — `tu universum perficis`, `pra, prāpta` — that must stay untranslated).

## Deliverables checklist

- [x] D1 repaired (34/34 rows, 58/58 spans) — confirmed via rescan, landed by a concurrent
      session's independent identical fix, verified against this session's own measurement.
- [x] CI gate added (`cyrillic_in_sanskrit_wrapper`, HIGH_CONFIDENCE) + selftest.
- [x] D3 ruled ({%..%} is the convention) + gated (`gloss_wrapper_became_guillemet`, report-only)
      + worklisted (54 rows) rather than bulk-applied — count not driven to 0, deferred per
      acceptance criterion.
- [x] D4 triaged with published per-sub-pattern precision (100%/n=25 wrapper-loss-not-content-loss
      for the dominant sub-pattern; benign for the RU-surplus sub-pattern).
- [ ] Data-integrity issue [#752](https://github.com/gasyoun/SanskritLexicography/issues/752)
      closed with these numbers — done in the same PR (see PR description).
- Non-goal confirmed unviolated: no re-translation performed; D5 not implemented; sheets/H1650
  and citation wiring/H1652 untouched.

_Dr. Mārcis Gasūns_
