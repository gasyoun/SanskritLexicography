# A/B test — nominal grammar layer injected into the translation harness

**Question.** Does injecting the nominal grammar layer (`nominal_grammar.py`: stem class,
Whitney §§, MW compound segmentation, irregularity flags) into the DE→RU translation prompt
**improve translation quality**? This is the adoption gate for wiring it into the bulk harness
(the analog of `whitney_grammar.py`'s root injection).

**Variable under test (one only):** per-card nominal grammar block ON (arm B) vs OFF (arm A),
via `gen_opt_harness2.py --nominal [--no-grammar]`. Same 8 cards, same masked+batched harness,
same TR, Sonnet translator. Methodology follows `AB_TEST_LEAN_TR.md` (sequential cold runs;
deterministic gates + blind pairwise judge).

## Sample (8 PWG headwords, stratified by stem class)

| key | iast | stem class | note |
|---|---|---|---|
| abad_da | abaddha | a-stem adj. | privative |
| abad_damu_ka | abaddhamukha | a-stem adj. | **compound** (MW: abadDa+muKa, bahuvrīhi) |
| abalya | abalya | a-stem n. | |
| abal_iya_ms | abalīyaṃs | consonant-stem adj. | comparative |
| aban_du | abandhu | u-stem adj. | privative |
| aba_d_a | abadhā | ā-stem f. | geometry term |
| abud_di | abuddhi | i-stem f. | privative |
| aciram | aciram | indeclinable adv. | |

Caveat: an `a`-section slice, heavy on **privative adjectives** — not representative of the
full noun space (no deep tatpuruṣa, no declension-irregular consonant stems).

## Results

**Deterministic (both arms):** 8/8 cards translated, **0 nulls, markup fidelity 100%** in both.
The grammar layer neither broke nor fixed markup. Sense counts at parity (A=B except abad_da 11 vs 10).

**Cost:** noise-dominated at N=1. Arm A 134k tok / 4 agents / 112s (one retry); arm B 102k tok /
3 agents / 62s. The retry in A confounds the comparison — exactly the trap `AB_TEST_LEAN_TR.md`
flagged. The grammar payload adds ~3.2 KB prompt/run; on a clean run B should cost *slightly more*.

**Blind pairwise Opus judge** (rendering 1 vs 2, arm identity hidden, alternating blind by card
index; 8 judges, un-blinded in Python):

| dimension | B (grammar ON) wins | A (OFF) wins | tie |
|---|---:|---:|---:|
| **overall winner** | **1** | **5** | 2 |
| correctness | 0 | 2 | 6 |
| completeness | 0 | 3 | 5 |
| register | 0 | 2 | 6 |
| grammar_notes | 1 | 4 | 3 |

**B wins+ties = 3/8 = 37.5% < 50% → FAILS the adoption rule.** Worse, the dimension the layer
exists to help — `grammar_notes` — went to **A 4-1**.

### Why the layer didn't help (judge reasons)

1. **Redundant on compounds.** On `abaddhamukha` (the one compound), A won — both arms correctly
   produced the bahuvrīhi, because the **source German already prints `abadDa + muKa`**. The MW
   `<k2>` segmentation block added nothing the source didn't already carry. (A compound whose
   segmentation is NOT in the source would be the real test of the MW-join — untested here.)
2. **PWG's German already encodes the grammar.** For prose DE→RU, the entry text carries the
   gender/derivation cues the translator needs; the §§/stem-class block is parallel information,
   not new.
3. **Mild distraction.** In `abalya` arm B misread PW form-variants as added senses; in `abud_di`
   it relabeled segments. Small slips, plausibly noise — but the extra prompt content did not buy
   accuracy and may have diluted attention.

## Decision

**REJECT auto-injecting the nominal grammar layer into the translation harness.** On this
evidence it gives no quality gain, carries a small added prompt cost, and a mild regression risk.
`--nominal`/`--no-grammar` stay in `gen_opt_harness2.py` for the record; the **default for
nominal windows is grammar OFF** (same prompt as roots, minus the root block).

**This does NOT retire the nominal grammar layer.** The A/B tested ONE use — prose-translation
enrichment — and only that use is rejected. The layer's primary justification is **structured
grammatical data** (stem-class index, vidyut paradigm, MW compound segmentation, Whitney §§ /
exception citations) for the dictionary's grammatical apparatus, declension display, reverse
indexing, and FAIR export — the Scope B/C deliverable, independent of translation. That value
stands; build the export/display consumer, not a translation injection.

**Caveats on strength:** N=1 per arm, 8 privative-heavy cards, the one compound self-defeating
(segmentation already in source). A larger, genre-diverse sample with source-opaque compounds
could shift the margin — but the direction (no gain on translation) is clear enough to not
auto-adopt now.

## Artifacts

- arms: `src/pilot/output/wf_nominal_{A,B}.json` (8 cards each, canonical)
- pairs / blinding: `src/pilot/output/nominal_ab_pairs.json`, `nominal_judge_mapping.json`
- judge: `src/pilot/gen_nominal_judge.py` → `run_nominal_judge.js`; verdicts
  `src/pilot/output/nominal_ab_verdict.json`
- harness: `gen_opt_harness2.py --nominal [--no-grammar] --keys=…`
