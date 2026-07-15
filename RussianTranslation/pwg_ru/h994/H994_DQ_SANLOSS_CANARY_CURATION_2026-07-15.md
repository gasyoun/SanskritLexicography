# H994 D-Q — a reliable silent-SAN-LOSS canary (passes fidelity, drops a sense)

_Created: 15-07-2026 · Last updated: 15-07-2026_

Resolves the **D-Q** residual from the [H994 two-profile measurement](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/H994_TWO_PROFILE_LIVE_MEASUREMENT_GATE_2026-07-15.md):
the rung-3 canary false-flag measurement needs a card that **passes the `accept()` `<ls>`/`{#` fidelity
gate while dropping a numbered source sense** — the "silent SAN-LOSS" shape the H920/H960 sense-count
soft-guard exists to catch. `darvI`/`gaRanA` are poor canaries; this curates a deterministic one.

## The mechanics the canary must satisfy

The live gate is the JS `accept()` in
[`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
(mirrored by the Python `accept()`), which applies, in order:

1. **Fidelity gate (HARD reject):** `ls = countOf(c, /<ls\b/g)`, `sk = countOf(c, /\{#/g)` counted **only
   over the emitted senses' `german`** — must equal `INPUTS[k].ls = raw.count('<ls')` and
   `INPUTS[k].sk = raw.count('{#')`. Any drift → `fidelity-reject`.
2. **SAN-LOSS gate (SOFT / telemetry):** `exp = INPUTS[k].source_senses` (deterministic,
   cross-reference-hardened [`count_source_senses`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sense_count.py)).
   If `emitted < exp` → `SANLOSS_SHORTFALLS++` (kept unless the owner-gated `SANLOSS_HARD_REJECT` is armed).

So a **silent SAN-LOSS** card is one where a dropped sense is invisible to gate 1 but visible to gate 2 —
i.e. **the dropped sense carries neither an `<ls>` citation nor a `{#…#}` masked span.**

## Why `darvI`/`gaRanA` are poor canaries

`darvI`'s three senses are `1〉 {%Löffel%}`, `2〉 {%die Haube einer Schlange%}`, `3〉 {#darvI#} N. pr.` — only
**two of three** are pure gloss. `raw.count('{#') = 1` (sense 3). So:

- If the model drops sense 1 or 2 (pure gloss) → `{#` count stays 1 → fidelity passes → **silent SAN-LOSS** ✓.
- If the model drops sense 3 (the `{#`-bearer) → `{#` count 0 ≠ 1 → **`fidelity-reject`**, not a silent loss.

Which sense the model drops is not controllable, so `darvI` reproduces the silent shape only *sometimes* —
and in the no_pwg drain it is in fact a **deterministic `fidelity-reject`** (the `{#…#}`-span-drop class,
[RUN_LOG](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md)).
A canary must remove that coupling.

## The delivered canary (deterministic)

**`dq_canary_puregloss~~h0_zz_pw`** ([raw](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw.raw.txt) ·
[portrait](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw.portrait.json)) —
three line-opening pure-gloss senses, **zero `<ls>`, zero `{#`**:

```
=== LAYER: PW ===

— 1〉 {%eine Schildkröte%}.
— 2〉 {%ein kleiner Fisch%}.
— 3〉 {%eine Wasserpflanze%}.
```

Offline build-check (real `gen_opt_harness2.build()`, no generation): `count_source_senses = 3`,
`raw.count('<ls') = 0`, `raw.count('{#') = 0`; `INPUTS` stamped `source_senses: 3, ls: 0, sk: 0`. Because
both fidelity counts are 0, the gate is `0 == 0` **whichever** sense is dropped, so:

| model emits | fidelity | SAN-LOSS | outcome |
|---|---|---|---|
| all 3 senses | pass | `emitted 3 == exp 3` | clean (no false flag) |
| drop 1st / middle / last (any 2 of 3) | **pass** | `emitted 2 < exp 3` | **silent SAN-LOSS, dropped=1** |
| drop two (1 of 3) | **pass** | `emitted 1 < exp 3` | silent SAN-LOSS, dropped=2 |

This is the reliable positive control `darvI` cannot be: **every** drop is silent + counted. It is a
synthetic control card (not a real headword) — appropriate for a canary, whose job is to force the exact
shape, not to sample the corpus.

## Using it in the live rung-3 measurement

1. Place the two files where `input_paths(key)` resolves them (the deterministic no_pwg input dir), or
   pass the key explicitly. Key: `dq_canary_puregloss~~h0_zz_pw`.
2. Generate it through the headless worker (single card, single profile is fine — the guard behaviour is
   profile-count-independent). **No promotion needed** — this is a measurement.
3. Read the guard telemetry from the run summary: `sanloss_shortfalls` and `SANLOSS_DETAIL`
   (`{key, expected, emitted, dropped}`). A faithful generation → `sanloss_shortfalls: 0` (the guard is
   correctly silent); a dropped sense → `sanloss_shortfalls: 1` with `dropped ≥ 1` (true positive).
4. The **false-flag** question the measurement answers: across a batch of *clean* cards, how often does the
   guard fire when no sense was actually dropped? Pair this canary (guaranteed true-positive on a drop)
   with a set of faithful real cards (true-negatives) to get both halves of the rate.

## Mining real multi-sense candidates (for representativeness)

The synthetic canary proves the guard; a *representative* false-flag rate also wants real headwords with
the silent-drop shape. Select from the PWG/no_pwg source any entry with **≥2 line-opening top-level senses
(`count_source_senses ≥ 2`) where at least one sense carries no `<ls>` and no `{#…#}`** — that gloss-only
sense is the silently-droppable one. Citation-free PW/SCH/NWS supplement glosses are the richest seam (the
[`sense_count.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sense_count.py)
docstring's `aklizwa`/`asakta` are single-sense cousins of this family). Filter, don't hand-pick.

## Verification

- Behavioral selftest extended: [`accept_sensecount_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/accept_sensecount_test.js)
  now drives the **real** `accept()` with this canary — faithful is clean; dropping the 1st / middle / last
  sense each keeps the card, passes fidelity, and fires SAN-LOSS (`dropped=1`); dropping two → `dropped=2`;
  and a **contrast** case proves the `darvI` `{#`-sense drop `fidelity-reject`s instead. Runs green via
  `window_selftest.test_h960_accept_sanloss_soft_gate`.
- Offline harness build-check: the canary masks losslessly and stamps `source_senses: 3 / ls: 0 / sk: 0`.

_Auto-generated by Opus 4.8 (`claude-opus-4-8[1m]`) as the H994 D-Q executor, Ultracode; offline
curation + selftest, no live generation, no promotion, no store/TM mutation._

_Dr. Mārcis Gasūns_
