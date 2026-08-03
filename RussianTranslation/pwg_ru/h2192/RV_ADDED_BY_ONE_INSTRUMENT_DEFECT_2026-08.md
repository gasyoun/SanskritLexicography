# Why `added_by_one` never fires — a converse-class degeneracy in the RV divergence taxonomy

_Created: 03-08-2026 · Last updated: 03-08-2026_

**Handoff:** [H2192](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2192-Opus_RussianTranslation_askbatch-rv-residual-2026-08_02.08.26.md)
(W1-RV residual) · **Executed by:** Opus 5 (`claude-opus-5[1m]`) · **Model calls: zero.**
Every number below is derived from committed data by
[`src/rv_added_by_one_diagnosis.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_added_by_one_diagnosis.py)
(`python src/rv_added_by_one_diagnosis.py report`).

## The open question this closes

[H1844](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1844-Opus_RussianTranslation_rv-multitranslation-typing-w1b_29.07.26.md)
measured `added_by_one` at **0 of 12,000** pilot labels.
[H1901](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/DECISIONS_LOG_rv_multitranslation.md)
reproduced the zero on three independently-trained arms — **0/300, 0/300, 0/267** — and both
entries reached the same verdict: *"a prompt or taxonomy defect, not a fact about the
Rigveda"*, and *"indicts the instrument"*. Neither measured **why**, and the decisions log
named it "the first thing the step-8 gate should be read against". That is what this pass
measures.

**The cause: `added_by_one` and `omitted_by_one` are converse readings of one undirected
event, and the output schema had no field for the direction.** The two labels partition
nothing; they name the same configuration — material present on one side, absent on the
other — from opposite ends. Asked to pick one name for one event with no way to say which
side, every arm picked the same one.

## Evidence 1 — structural (no data read)

| # | Property | Holds |
|---|---|---|
| 1 | The pair key is **unordered** — 10 keys for 5 translators; nothing in `a\|b` distinguishes "a added" from "b omitted" | yes |
| 2 | The two class definitions are **converse relations**: material present in `a` and absent in `b` satisfies *both* readings | yes |
| 3 | Before the fix, the model reply shape was `{"class", "why"}` — **no direction field** | yes |
| 4 | The **deterministic arm always did** record a side (`missing_side`) | yes |
| 5 | Before the fix, `COARSE_MAP` sent `added_by_one`→`divergence` but `omitted_by_one`→`omission` | yes |

Property 4 is the sharpest of the five. Direction was expressible in this output format all
along, and was dropped in exactly the one arm — the model arm — that cannot recover it any
other way. Property 5 is a second, independent defect riding on the first: the **K3 coarse
projection was not invariant** under a semantically vacuous choice between two names for the
same fact.

## Evidence 2 — the population the class should have caught

Measured on the committed spine over the pilot's own 2,000 stanzas. Supplied-material
markers (`[…]`, `(…)`) are a **proxy** for editorially supplied material, not proof of it,
and the convention differs by edition — so this table measures *where the direction is
textually recoverable*, not *who padded more*.

| Translator | present | marked | `[…]` | `(…)` | marked % |
|---|--:|--:|--:|--:|--:|
| Grassmann 1876–77 | 2,000 | 91 | 75 | 25 | 4.5 % |
| Geldner 1951–57 | 1,999 | 802 | 9 | 797 | 40.1 % |
| Elizarenkova 1989–99 | 2,000 | 1,434 | 0 | 1,434 | **71.7 %** |
| Griffith 1896 | 2,000 | 2 | 0 | 2 | **0.1 %** |
| Jamison–Brereton 2014 | 2,000 | 1,027 | 362 | 903 | 51.4 % |

- Pairs where **exactly one** side carries a marker: **8,744**. Both sides: 2,339.
- Against that population, `added_by_one` fired **0** times.
- Largest one-sided pair: `elizarenkova_ru_1989|griffith_en_1896` at **1,436**.

**This corrects the rationale recorded in H1844/H1901, while confirming their verdict.**
Both entries argued the zero was implausible *because Griffith 1896 pads freely with supplied
and bracketed material*. In our extracted text Griffith is the **least** marked witness of the
five — 2 stanzas in 2,000 (0.1 %) — because his Victorian padding is italicised in print and
carries no delimiter at all after extraction. The padder in this data is **Elizarenkova**, whose
house style parenthesises supplied words in 71.7 % of stanzas. The defect verdict stands and is
in fact stronger: the population is 8,744 one-sided pairs, not a handful of Griffith brackets.

## Evidence 3 — the model was carrying the direction in prose the whole time

Of the **283** model-decided `omitted_by_one` rows, **283 (100.0 %)** name one of the pair's two
translators in the free-text `why` field. The direction was never missing from the model's
judgment — only from the schema. A deterministic backfill over the committed asymmetric labels
(no model call, `rv_added_by_one_diagnosis.py backfill`) recovers it for **235 of 286 (82.2 %)**:

| Source | rows | share |
|---|--:|--:|
| deterministic (`missing_side` already present) | 3 | 1.0 % |
| recovered — exactly one translator named in `why` | 232 | 81.1 % |
| ambiguous — both named, not guessed | 51 | 17.8 % |
| unrecoverable — neither named | **0** | 0.0 % |

Sidecar: [`pwg_ru/h2192/rv_divergence_direction_backfill.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2192/rv_divergence_direction_backfill.jsonl).
Additive — the pilot file is **not** mutated, and the 51 ambiguous rows are emitted as
ambiguous rather than guessed.

## Evidence 4 — what the coarse-map defect cost (nothing, yet)

Recomputed on the three committed spike arms under the old map and the converse-collapsed map:

| Arm A | Arm B | n | κ old | κ fixed |
|---|---|--:|--:|--:|
| `spike.ds-v3` | `spike.gpt4o-mini` | 300 | 0.235 | 0.235 |
| `spike.ds-v3` | `spike.gemini-flash` | 267 | 0.350 | 0.350 |
| `spike.gpt4o-mini` | `spike.gemini-flash` | 267 | 0.216 | 0.216 |

Bit-identical, and the reason is the defect itself: `added_by_one` fired zero times, so the
unstable half of the map was never exercised. **H1901's published coarse kappas need no
caveat and no re-issue.** The projection was fragile, not damaged — fixing it now costs
nothing and removes a defect that would have moved every coarse number the moment the class
started firing. These three values also independently reproduce H1901's published numbers.

## The fix

In [`src/rv_divergence_type.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_divergence_type.py):

1. **`surplus_side` is mandatory** on every asymmetric label and must resolve to one of *that*
   pair's two translators. The prompt fixes the reading point at the **first** translator named
   in the pair key: surplus on the first is `added_by_one`, surplus on the second is
   `omitted_by_one`. The two names now denote different events.
2. **An unresolvable side is recorded, not coerced** — `normalise_side()` accepts the full id or
   a bare surname and otherwise returns `None` plus a note, the same posture H1901 took with
   out-of-enum classes (`class: null` for 9 Gemini replies, never snapped to a nearest class).
3. **The deterministic arm emits `surplus_side` too**, where the direction is a fact about the
   source rather than a judgment.
4. **`COARSE_MAP` sends both converse names to `omission`**, so the K3 projection is invariant
   under the relabelling.
5. The prompt states the marker conventions measured above, with the caveat that a marker is
   evidence and its absence is not counter-evidence.

**Not done, deliberately:** the pilot was **not** re-run. Re-typing 2,000 stanzas is a paid
call this handoff's fence forbids ("no paid bulk drain"), and the fix is to the instrument, not
to the data. The committed pilot keeps its labels; the backfill sidecar carries the recovered
direction beside it.

## Verification

| Gate | Result |
|---|---|
| `pytest tests/test_rv_spine.py` | **54 passed** (49 before, +5 H2192 pins) |
| The 5 new pins on **pre-fix** `rv_divergence_type.py` | **5 failed** — RED before, GREEN after |
| `python src/pilot/window_selftest.py` | **201/201 passed** |
| `python src/pilot/lang_parity_check.py` | 91 entries, all verdicts complete, **no drift** |
| `python src/rv_added_by_one_diagnosis.py selftest` | OK |

## What this does and does not settle

- It does **not** prove `added_by_one` will now fire — that needs a re-typed spike, which costs
  a paid call this handoff is fenced against. The claim proven here is that the class was
  **undecidable as specified**, and is now decidable.
- It does **not** touch the step-8 human gate, which remains unvoted and remains the blocker on
  the full 10,552-stanza run (R13). It does make that gate's reading easier: a reviewer who
  meets an asymmetric card can now see which translator holds the surplus.
- It does **not** re-open the H1901 separability verdict on
  `lexical_variant` vs `semantic_shift` — a different pair, a different defect, already ruled.

_Dr. Mārcis Gasūns_
