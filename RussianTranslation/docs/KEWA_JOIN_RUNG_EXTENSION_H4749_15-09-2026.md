# KEWA→PWG join: the two H3169 rungs applied — 78.87 % → 83.04 %

_Created: 15-09-2026 · Last updated: 15-09-2026_

Extension of the H3169 join built under
[H4749 (OxAlpha) — KEWA +476 rows one morphological rung from PWG](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4749-OxAlpha_SanskritLexicography_xwalk-s16-kewa-476-rung_14.09.26.md).
Baseline artifact:
[KEWA index normalization + dhātu-aware join, 25-08-2026](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/KEWA_INDEX_NORMALIZATION_AND_PWG_JOIN_25-08-2026.md)
(H3169, ceiling C4, *modern IE* lane).

## 1. What changed

[§5 of the H3169 memo](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/KEWA_INDEX_NORMALIZATION_AND_PWG_JOIN_25-08-2026.md)
sized the 2,413-row unmatched residue and found **476 rows (358
`present-stem->root` + 118 `feminine-in-stem`) one unapplied rung from a PWG
headword**, putting the realistic ceiling at ≈83 %. H3169 deliberately did not
apply them: a bare rule carries no per-row morphological witness. H4749 applies
them — as the **lowest-ranked rungs of the ladder**, below every witness route,
with every matched row flagged:

| Ladder position | `match_basis` | How | Rows |
|---|---|---|---:|
| 1 | `exact` | unchanged | 2,023 |
| 2 | `sandhi/diacritic-normalized` | unchanged | 5,670 |
| 3 | `inflected-form->stem` (witness) | unchanged | 634 |
| 4 | `finite-form->root` (witness) | unchanged | 632 |
| 5 | `present-stem->root` (**new, rule**) | strip a present-class ending (`ati ate oti ute Ati Iti`) → PWG root; `Kallate` → `Kall` | **358** |
| 6 | `feminine->stem` (**new, rule**) | feminine `-ī` → masculine stem, H3169's own priority: `-in` first (`SIrI`→`SIrin`), then the bare stem — the `-vat`/`-ant` class (`gavatI`→`gavat`), then thematic `-a` (`devI`→`deva`) | **118** |
| 7 | `ambiguous-multi` | unchanged | 46 |
| 8 | `unmatched` | the honest residue, still a reportable class | 1,937 |

Safeguards kept from H3169's discipline:

- **Witness outranks rule.** The new rungs fire only after every identity,
  witness and disambiguation route has missed, so no rule can override a
  form→lemma analysis or the `-as`-stem fix.
- **Flagged, never silent.** All 476 rows carry `rule-rung-applied` in
  `flags`; the summary carries the `rule-rung-applied: 476` count next to the
  class counts.
- **No folding.** Only citation-form truncations with a stated morphological
  rule (Uprava DEAD_ENDS §7 discipline unchanged; no length or sibilant
  folding anywhere).

Changed files:
[`join_kewa_pwg.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/join_kewa_pwg.py)
(two pure rung functions + `--selftest`, 10/10),
[`sample_kewa_join.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/sample_kewa_join.py)
(two new strata, sample 72 → 84 rows, same seed 3169),
regenerated
[`kewa_pwg_crosswalk.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_pwg_crosswalk.tsv),
[`kewa_pwg_crosswalk_summary.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_pwg_crosswalk_summary.json),
[`kewa_join_adjudication_sample.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_join_adjudication_sample.tsv).

## 2. Recount vs the 78.9 % baseline

| | Baseline (H3169, 25-08-2026) | H4749 (this pass) |
|---|---:|---:|
| rows | 11,418 | 11,418 |
| matched | 9,005 | **9,481** |
| matched_pct | 78.87 % | **83.04 %** |
| unmatched | 2,413 | 1,937 |
| of which `no-nearby-pwg-headword` | 1,921 | 1,921 |

The result lands exactly on the H3169 ceiling estimate (≈83 %): the rungs
matched **precisely the 476 rows the diagnostics had sized** — 358 + 118,
neither more nor fewer — because the diagnostics and the applied rungs share
one membership test. The remaining 1,937 unmatched are the honest answer to
"what does Mayrhofer head that Böhtlingk-Roth does not".

## 3. Proof the extension is purely additive

Diff of the committed crosswalk against `HEAD` (row identity = first 6 columns):

| Invariant | Result |
|---|---|
| rows changed | **476** |
| all changed rows were `unmatched` before | yes (476/476) |
| new classes of changed rows | `present-stem->root` 358, `feminine->stem` 118 |
| changed rows flagged `rule-rung-applied` | 476/476 |
| all other rows byte-identical | 10,942/10,942 |
| every pre-existing class count unchanged | yes (exact 2,023 · sandhi 5,670 · witnesses 634/632 · ambiguous 46 · `-as` fix 129 · routes-disagree 612) |

No row moved between existing classes; nothing previously matched was
re-targeted; the residue only shrank by exactly the sized class.

## 4. Spot adjudication — 20 rows, seed 4749

**Adjudicator: GLM (zai-coding-plan/glm-5.3-flash) — the same class of
limitation H3169 declared: a competent morphological reading, not an editorial
sign-off by Dr. Gasūns.** The class is flagged in the crosswalk, so a human can
re-review all 476 rows whenever wanted.

| Class | n | Verdict |
|---|---:|---|
| `present-stem->root` | 10 | 10/10 same-lexeme (`kuñjati`→`kuñj`, `ghásati`→`ghas`, `bhárati`→`bhar`, `ruṇṭhati`→`ruṇṭh`, `ṭīkate`→`ṭīk`, …) — the `bhárati`→`bhar` / `Kallate`→`Kall` shape is H3169's own sanctioned weak-root citation equation |
| `feminine->stem` | 10 | 10/10 regular feminine↔masculine pairing (`kaṭhinī`→`kaṭhina`, `pālaṅkī`→`pālaṅka`, `cuñculī`→`cuñcula`, `karaṭī`→`karaṭin`, `janitrī`→`janitra`, …); one derivation-pointer (`Kāverī`→`kāvera`) is the regular adjective pairing, correct as a crosswalk pointer |

Sampled rows are committed in
[`kewa_join_adjudication_sample.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_join_adjudication_sample.tsv)
(84 rows; the two new strata contribute 6+6).

## 5. What is deliberately not here

- **No collapse of the remaining 1,937** onto near misses — `unmatched` stays a
  reportable class (C4 ruling, unchanged).
- **No canonical-store mutation, no `csl-orig` edit, no paid PWG run.**
- **No merged etymology field** — the crosswalk stays `lane = modern-IE`,
  KEWA-derived, heading pointers only. The rights posture of H3169 §8 is
  untouched: derived SLP1-keyed measurements only, no KEWA article text.
- **No downstream consumer rewired** — the `advises`-edge consumer
  (`card_advisory.py`) reads the crosswalk file and picks up the extension
  automatically; its union=N pattern means an absent crosswalk stays a no-op,
  and nothing else consumes `match_basis` values.

## 6. Reproduce

```bash
python RussianTranslation/src/etym/kewa_normalize.py --src <GitHub>/SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt
python RussianTranslation/src/etym/join_kewa_pwg.py --github-root <GitHub>   # --selftest for the rung checks
python RussianTranslation/src/etym/sample_kewa_join.py
```

Expected: selftest 10/10; `matched 9481 / 83.04 %`; `rule-rung-applied 476`;
`unmatched 1937`.

_Гасунс_
