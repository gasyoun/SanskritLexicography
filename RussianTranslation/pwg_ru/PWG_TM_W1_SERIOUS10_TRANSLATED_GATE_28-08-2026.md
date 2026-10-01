# PWG TM Wave 1 — translating the residue of the 10 repairs: the projected gate clears all three floors

_Created: 28-08-2026 · Last updated: 28-08-2026_

Opus 5 (`claude-opus-5`), [H3628](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3628-Opus_RussianTranslation_pwg-tm-w1-serious10-translate_28.08.26.md). Continues [H2877](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2877-Opus_RussianTranslation_pwg-tm-w1-serious-error-10-repair_16.08.26.md) (taxonomy + revert repair) and [H3611](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3611-Opus_RussianTranslation_pwg-tm-w1-serious10-rescore_28.08.26.md) (the re-score that showed the revert breaks the fidelity floor). Receipt of record for the 10 rows: [PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md).

## Status: projected n=400 PASSES all three floors — but nothing has been promoted

| Floor | H2684 before | After the revert repair (H3611) | **After translation, §12.2-compliant** |
|---|---|---|---|
| fidelity ≥ 98 % | 99.50 % PASS | 97.25 % **FAIL** | **99.00 % PASS** |
| equivalence ≥ 95 % | 95.50 % PASS | 95.75 % PASS | **97.50 % PASS** |
| serious_error ≤ 1 % | 2.50 % **FAIL** | 0.00 % PASS | **0.00 % PASS** |

Independent judge `x-ai/grok-4.5`, blind, one call per row, H3299 pinned rubric: **serious 0/10, fidelity 8/10, equivalence 8/10**. `independence_errors` `[]`; no severity-consistency violations. Spend this pass **$0.174288**; **$0.710523** across all five judge runs (H3611 plus four here).

**This is a projection over the frozen H2684 sample, not a passing gate.** The promoted dump still holds the defective rows; the sidecar does not touch it. What the numbers establish is that the repair *would* clear all three floors if applied — not that Wave 1 now passes. Turning it into a real pass means writing the 10 targets into the dump and re-running the gate, which is a Wave-1 mutation and is fenced by `WAVE1_IMMUTABLE`.

## The finding that made this pass cheap: 5 of 10 were already solved in shipped code

[H3299](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3299-Fable_SanskritLexicography_pwgtm-wave2-regenerate-regate_22.08.26.md) shipped `PLACEHOLDER_RU` and `placeholder_ru()` in [`src/pwg_tm_generate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_generate.py) on 24-08-2026, pinning `Jmd → кто-л.` for exactly the argument-slot placeholder that caused this defect class. **H2877 ran three days later and never consulted it** — its R2 rule queried only the exact-source lexicon, found nothing (correctly, the span is denylisted), and reverted to German.

So five of the ten rows (`arTay`, `krand`, `saYj`, `gam`, `vid`) needed no authoring at all: one call to shipped code gives the right answer, and the judge scored all five `none` with `fidelity: pass`. That is the cost of the prior-art miss — an entire deterministic answer sitting unused while the rows sat unpromotable.

## What each row needed

| Provenance | Spans | What it is |
|---|---|---|
| `placeholder_ru` | 5 | Shipped H3299 table. `{%Jmd%}` → `{%кто-л.%}`. Deterministic. |
| `authored` | 6 | Claude-authored Russian, each with a written rationale. |
| `span_fix` | 2 | Wave-1 translation defects in `vid` that the H2684 gate never flagged, surfaced by this pass's judge. |
| `bare_prose` | 1 | Apparatus connective *outside* any gloss span. |
| `unrepairable_kept_german` | 1 | `viSveSa` 2 — see below. |

The six authored spans:

| Span | Russian | Why |
|---|---|---|
| `{%gewachsen%}` | `{%выросший%}` | PWG `ruh` 3 "wachsen"; the past participle "grown". The Wave-1 target read it as the *gewachsen sein + dat.* idiom "equal to / capable", a different sense this bare gloss does not carry. |
| `{%Antritt, Anfang, Beginn%}` | `{%вступление, начало, зачин%}` | Three near-synonyms for commencement; the Russian keeps the same three-step gradation. |
| `{%mit%}` | `{%с%}` | Inside Śaṃkara's gloss "upadrava **mit** upa beginnt". |
| `{%beginnt%}` | `{%начинается%}` | Finite verb of the same gloss. |
| `{%an sich, zu sich, auf sich%}` | `{%к себе, себе, на себя%}` | `ātmasāt` adv. — the German reflexive triplet with matching Russian reflexives. |
| `{%thun%}` | `{%делать%}` | Archaic *tun*, glossing `{#kar#}`. The Wave-1 «класть» ("to put") came from unsafe exact-source reuse — [FINDINGS §590](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md). |

Two defects in `vid` that the original gate missed, and this judge caught: `{%angemeldet von%}` → `{%возвещённый%}` had dropped the agentive *von*, and `{%meldet, dass%}` → `{%возвещает, что%}` rendered an imperative (`{#AvedayaDvaM#}`, 2 pl.) as a 3 sg. indicative. Corrected to `{%возвещённый от%}` and `{%сообщите, что%}`. Worth noting on its own: **a re-score of repaired rows surfaces defects the original adjudication never flagged**, because the judge re-reads the whole fragment rather than the one span under repair.

One apparatus connective: `Nur in Verbindung mit` → `Только в соединении с`, sitting outside any `{%…%}` span in `AtmasAt`. Wave 1 only ever translated gloss spans, so every such connective stayed German — the H2787/H2876 metalanguage class, and the reason `AtmasAt` still failed fidelity after its gloss spans were correct.

## `viSveSa` 2: not repairable at this layer, and measured to be so

PWG reads:

```text
<hom>2.</hom> {#viSveSa#}¦ (wie eben) <lex>adj.</lex> {%die%} <is>Viśve Devāḥ</is> {%zur Gottheit habend%}
```

That is **one discontinuous gloss** — "having the Viśve Devāḥ as deity" — which the fragmentizer split at the `<is>` boundary, leaving a bare German definite article as a standalone `definition_gloss` fragment. Russian has no articles, so no faithful word-level target exists. All three candidates were put to the independent judge rather than argued:

| Candidate | Judge verdict |
|---|---|
| invent a word (`{%боги%}`) | the original H2684 serious defect |
| elide to `{%%}` | `sense_absent_or_inverted` — **serious** ("source gloss entirely dropped") |
| keep `{%die%}` | `german_residue` — **non-serious** |

So the German is retained deliberately: it is the only option that neither invents content nor reads as sense-loss. This is the one row of ten that stays `uncertain`, and it costs the fidelity floor 0.25 points — 99.25 % against a 98 % floor, so it does not block the gate. The real fix is upstream: rejoin discontinuous glosses across `<is>` *before* fragmenting. Logged as GAPS §18.


## Style-guide §12.2 audit — one authored span was a rule violation

The first cut of this pass rendered `{%mit%}` as «с», and the independent judge liked it: the `upakrama` row scored `none` / fidelity **pass**. Auditing the authored set against the ratified [style guide §12.2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md) showed that was **forbidden**: a span consisting entirely of apparatus is never translated as a gloss, and the canonical detector `sanskrit_util.classify_german_metalanguage` classes bare `mit` as a `function_word`.

The rule wins over the better reading. `{%mit%}` now keeps its German, and the cost was measured rather than guessed:

| | fidelity | equivalence | serious |
|---|---|---|---|
| `{%mit%}` → «с» (violates §12.2) | 99.25 % | 97.75 % | 0.00 % |
| `{%mit%}` kept German (§12.2-compliant) | **99.00 %** | **97.50 %** | **0.00 %** |

Compliance costs 0.25 fidelity points and **all three floors still clear**. Two spans now keep their German by rule rather than by failure — `{%die%}` (`unrepairable_kept_german`) and `{%mit%}` (`apparatus_not_translated`) — and the judge scores both `german_residue`, which the rubric pins non-serious.

Both are the same underlying defect seen twice: `{%die%}` and `{%mit%}` are *fragments of running clauses* chopped at markup boundaries, not apparatus tokens. §12.2's whole-span test cannot tell the two apart, which is filed as **CONTRADICTIONS §16**; the durable fix is the fragmentizer change in **GAPS §18**, after which the question disappears.

`--selftest` now enforces §12.2 mechanically — it calls the canonical detector over every entry in the authored table and fails if any is whole-span apparatus — so this class cannot be re-introduced by hand.

## What this does not claim

- **Not** that Wave 1 passes. The projection is arithmetic over a frozen sample; the promoted dump is unchanged and `--verify` still exits 1 on the recorded `independent_gate=fail`.
- **Not** a new measurement of the corpus. Ten of 400 rows were re-judged; the other 390 keep their original verdicts, and n=400 samples 753,111 fragments.
- **Not** independently verified Russian *style*. The judge scored fidelity and equivalence, not register. Six targets are Claude-authored; a Russian-native editorial pass against the [style guide of record](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md) is the next quality step, not something this pass performed.
- **Not** self-adjudicated. Claude authored six targets; `x-ai/grok-4.5` judged all ten. The `x-ai/grok-4.6` self-score is recorded separately and is rejected by `independence_errors` on every row, as it must be — it dissents on `vid` (`wrong_lexical_meaning`), and since 4.6 generated the Wave-1 target it is judging, that dissent carries no independent weight.

## Reproduce

```text
cd RussianTranslation
python src/pwg_tm_serious10_translate.py --selftest
python src/pwg_tm_serious10_translate.py apply \
  --sidecar pwg_ru/serious10/serious10_sidecar.jsonl --out pwg_ru/serious10
python src/pwg_tm_serious10_rescore.py run \
  --sidecar pwg_ru/serious10/serious10_translated.jsonl \
  --out pwg_ru/serious10/translated
python src/pwg_tm_serious10_rescore.py project \
  --adjudication release/pwg_tm_canonical/wave1_b_receipt/adjudication400.jsonl \
  --rescore pwg_ru/serious10/translated/serious10_rescore_grok45.jsonl
```

`--selftest` pins that the shipped `placeholder_ru` table wins over any authored entry, that a pinned placeholder is never re-authored here, and that the unrepairable article is kept rather than elided.

Artefacts: [`serious10_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/serious10_translated.jsonl) · [`translated/serious10_rescore_grok45.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/translated/serious10_rescore_grok45.jsonl) · [`translated/serious10_rescore_receipt.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/translated/serious10_rescore_receipt.json) · [`translated/serious10_projection.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/serious10/translated/serious10_projection.json) · tool [`src/pwg_tm_serious10_translate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_serious10_translate.py).

_Dr. Mārcis Gasūns_
