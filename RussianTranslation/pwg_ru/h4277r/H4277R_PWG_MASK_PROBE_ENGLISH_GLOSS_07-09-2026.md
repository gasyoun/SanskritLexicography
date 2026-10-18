# `pwg_mask` probe, 07-09-2026: the `_apta` sense-15 defect is a CLASSIFIER miss, not a model or prompt failure — one missing article flips English to German

_Created: 07-09-2026 · Last updated: 07-09-2026_

Executor: Opus 5 (`claude-opus-5`), interactive. **Zero paid calls** — this is entirely
offline, over `pwg_mask` and the PWG source. Follows
[H4277R_C1_APTA_4TH_WINDOW_RESULT_07-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4277r/H4277R_C1_APTA_4TH_WINDOW_RESULT_07-09-2026.md) §4,
which named the masking classifier as the suspect. **It is the culprit, and the model is
fully exonerated.**

## 1. The two spans, classified

`classify_pct_detail` on each span in its own source context:

| | sense 12 (came back verbatim ✅) | sense 15 (came back translated ❌) |
|---|---|---|
| source | `— b〉 {%equation of a degree%} <ls>WILS.</ls> — Die andern Bedeutungen …` | `— b〉 *{%equation of degree%}.` |
| `gloss_lang` | **`en`** | **`de`** |
| `rule_id` | **`wilson_en`** | **`default_de`** |
| `translate` | **`False`** | **`True`** |
| `looks_english_content` | **True** | **False** |
| WILSON cue in following text | **True** (`<ls>WILS.</ls>`) | False |
| masked skeleton | `— b〉 {T4} {T1} — Die andern …` | `— b〉 *{%equation of degree%}.` |
| span visible to the model | **No** (masked to `{T4}`) | **Yes** (survives verbatim) |

**Sense 15 was never masked.** It reached the model as a visible `{%…%}` gloss carrying
`translate: True`. The GLOSS WRAPPERS rule says every visible `{%…%}` must reappear around
its *translated* gloss — so the model did exactly what it was instructed to do. The
`{Tn}`-verbatim clause of H4277 could not apply, because there was no `{Tn}`.

**The audit is likewise not at fault.** `foreign_gloss_translated` did not fire because,
from the pipeline's point of view, this was a German gloss correctly translated. Everything
downstream behaved correctly on a wrong upstream label. §4 of the result doc framed this as
a detector gap; the probe shows the detector is sound and the fault is entirely upstream.

## 2. Root cause: the `>=2 distinct weak markers` threshold, and one missing article

`looks_english_content` returns True on a strong marker alone, or on **≥2 distinct** weak
markers from `ENGLISH_WEAK = {a, an, of, or, and, with, as, one, war}`. The ≥2 bar was set
deliberately (§464) so German and Latin residue does not take the `english_content →
translate:False` path.

- `equation of **a** degree` → weak hits `{of, a}` = **2** → English.
- `equation of degree` → weak hits `{of}` = **1** → below the bar → `default_de` → translated.

The article is the whole difference. Note that sense 12 is doubly protected — it *also* has
the `wilson_en` rule from its adjacent `<ls>WILS.</ls>` — so it would have been safe even
without the article. Sense 15 has no `<ls>` at all and no second marker.

## 3. Blast radius, measured over the whole corpus

192 763 `{%…%}` spans in `csl-orig/v02/pwg/pwg.txt`. Spans that classify `translate: True`,
carry no German markers, no strong English marker, and exactly **one** weak marker — the
sense-15 shape — number **933**. They are not one class:

| lone weak marker | count | character |
|---|---:|---|
| `an` | 678 | overwhelmingly **German** — `an demselben Tage`, `Mangel an Vertrauen`, `reich an Fasern` |
| `a` | 175 | German/Italian/Latin — `oltre a quindeci di` |
| `or` | 30 | **English** — `offence or guilt` |
| `of` | 23 | **English** — `consumer of food`, `sulphate of alumine`, `sighs of expiration` |
| `war` | 14 | mostly **German** (`war am Anfang dieses`); one English (`fear, alarm; war, battle`) |
| `and` | 6 | **English** — `milk and mangoes, mango fool` |
| `with` | 6 | **English** — `afflicted with pain`, `with delight` |
| `as` | 1 | **English** — `any aquatic weed, as Vallisneria` |

**The threshold is doing its job.** 867 of the 933 hang on `an` / `a` / `war`, which are
German words that happen to be English weak markers. Lowering the bar to 1 would push all
of those onto the verbatim path — precisely the regression §464 prevents.

## 4. The shape of a fix (proposal only — nothing changed here)

The weak set conflates two different things. `an`, `a`, `war` are **German homographs**;
`of`, `or`, `and`, `with`, `as` are **not German words at all**. Splitting the set along that
line — one hit suffices for the non-homograph subset, two still required for the homograph
subset — would catch the `equation of degree` / `offence or guilt` class (**66 spans**)
while leaving all 867 homograph spans exactly where they are.

This is **not applied**. It changes masking corpus-wide, which changes which spans reach the
model on every future window, so it wants its own handoff, a fixture pinning both directions
(`equation of degree` → en, `Mangel an Vertrauen` → de), and a `--selftest` run before any
paid call. A human decides whether to take it.

## 5. What this means for `_apta`

The card is **not** evidence that the H4277 `{Tn}`-verbatim clause failed — the clause
worked on the one span it could see. `_apta` stays on the defect list, the store stays
untouched, and no fifth window is warranted: a fifth window on the current classifier would
reproduce sense 15 exactly, because nothing about the input has changed.

## 6. Reproduce

Both probes are offline and read-only: `classify_pct_detail` / `mask` on the two spans, and
a single pass over `pwg_mask.PWG` bucketing `translate:True` spans by their lone weak marker.
Neither writes anything or issues a call.

_Dr. Mārcis Gasūns_
