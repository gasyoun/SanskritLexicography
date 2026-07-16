# H1070 — PWG→EN gold adjudication vs the Monier-Williams TM (Fable-tier verdict)

_Created: 17-07-2026 · Last updated: 17-07-2026_

**Adjudicator:** Fable 5 (`claude-fable-5`), 17-07-2026 · **Pattern:** [/gold-adjudicate](https://github.com/gasyoun/claude-config/blob/main/commands/gold-adjudicate.md), adapted: Pass A = the machine EN, Pass B = Monier-Williams' own rendering (human, 1899, via [`src/mw_en_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_en_tm.py) → `mw_en_tm.json`, 187,506 headwords, gitignored), ground truth = **the PWG German** ([FU1 locked decision 6](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FU1_PLAN.md) — MW is adversary cross-check, never the standard). Handoff: [H1070](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1070-Fable_RussianTranslation_pwg-en-fu1-pilot-adjudication_16.07.26.md).

## Sample frame (170 sense rows, two tranches)

| tranche | frame | n rows | generation model |
|---|---|---:|---|
| pilot | the EXACT S7 judged set, verbatim ([`src/pilot/output/en_judge_set.s7.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/output/en_judge_set.s7.jsonl), 68 rows, 16 pilot roots) | 68 | Sonnet 4.6 (`claude-sonnet-4-6`), 2026-06-30 |
| fu1 | fresh 50-card stratified sample over the 30 FU1 roots (same policy as [`src/fidelity_sample_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/fidelity_sample_en.py), imported not copied; seed rotated 42→43 per the [S7 memo](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FABLE_JUDGE_S7_2026-07-02.md)'s per-tranche recipe; senses/card capped at 3, seeded) | 102 | Sonnet 5 (`claude-sonnet-5`), 2026-07-01 |

Built by [`build_worksheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/build_worksheet.py); rulings in [`en_gold_adjudication.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/en_gold_adjudication.jsonl) (per-row `ruling` + `ruling_reason`, authoritative record in [`build_gold.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/build_gold.py)); every number below recomputable via [`compute_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/compute_stats.py). MW quoted per entry in [`worksheet.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/worksheet.jsonl): direct MW subcard entry for 58 rows, MW root-article scope for 112, absent 0.

## Headline (H1070 rubric: correct / acceptable-variant / wrong-sense / register-mismatch)

| tranche | n | correct | acceptable-variant | wrong-sense | register-mismatch | clean (C+AV) | wrong-sense 95% CI (Wilson) |
|---|---:|---:|---:|---:|---:|---:|---|
| pilot (Sonnet 4.6) | 68 | 55 | 12 | **1** | 0 | 98.5% | 1.47% [0.26%, 7.87%] |
| fu1 (Sonnet 5) | 102 | 83 | 16 | **3** | 0 | 97.1% | 2.94% [1.01%, 8.29%] |
| combined | 170 | 138 | 28 | **4** | 0 | 97.6% | 2.35% [0.92%, 5.89%] |

## The four wrong-sense rows (all spot-checked against the raw `wf_output.en.*.json` — CONFIRMED, not worksheet artifacts)

1. 🔵 **r025 `g_a~~h0_14_a_byastam`** (pilot) — EN adds "(of a heavenly body)", an MW-style domain parenthetical absent from the German. This is S7's unfaithful case 3, the single confirmed **mw-tm-contamination**; independently re-confirmed here with MW quoted per entry.
2. 🟡 **r102 `vac~~h0_00_pwg00`** (fu1) — the `<F>` footnote drops `{#uc#}` from «glauben wir zu {#uc#} ziehen zu müssen» → "must be drawn in" with no target root, gutting the editorial claim. **Also evidence the `{#..#}` token guard did not fire on footnote content** — a guard-hole lead for the deterministic gate.
3. 🔵 **r119 `d_a~~h0_00_pwg01`** (fu1) — «samayam … einen **Vergleich** vorschlagen» = propose a *settlement/pact* (samaya!); EN "to propose a **comparison**" picks the wrong sense of the German polyseme. One wrong gloss inside an otherwise excellent ~25-idiom phraseology row.
4. 🔵 **r155 `su~~h0_00_pwg00`** (fu1) — «surāṃ sunoti so v. a. **braut**» (= *brews* liquor, verb *brauen*) rendered "{%**betroth**%}" — homograph trap braut (verb) / Braut (bride). Markup intact, so **no deterministic gate can see it**; judge-tier only.

A fifth suspect (r005 `_buj~~h2_01_sec_1`, apparent tail omission) **resolved as a sample-frame artifact**: the "geniessen lassen" tail is translated in the sibling split sense `caus-1-cause-to-enjoy` of the same card. S7's "zero omissions" claim stands.

## MW as adversary — what the per-entry quoting showed

- **Zero new mw-tm-contamination in the 102 FU1 rows** (the only contamination case remains pilot r025). Verbatim MW agreement (e.g. r105 `iz` "to impel, incite, animate, promote"; r111 `udAp`) is the **expected PW-lineage signal**, not contamination — MW descends from PW, and the German licenses each gloss independently. Contamination is diagnosed only where EN carries MW content the German does *not* license (r025's parenthetical).
- MW lost to us where PWG is finer: r098 `aDinivas` («zur Wohnstatt wählen» → "to choose as a dwelling place") vs MW's flat "to dwell in".
- One MW-lookup homonym artifact (r049: `udgA` "rise" quoted where MW's sing-sense sits under ud-√gai) — a worksheet lookup caveat, not a translation defect.

## Acceptable-variant classes actually observed (28 rows — the error taxonomy for the scale-up memo)

| class | pilot | fu1 | reading |
|---|---:|---:|---|
| de-residue-crossref | 4 | 8 | pure cross-ref rows («Vgl. … fgg.», «s. u. d. W.») left untranslated — the dominant residual; deterministically detectable |
| de-residue-nws-hash | 2 | 0 | NWS source wraps German glosses inside `{#..#}` Sanskrit markers → pipeline protects them verbatim (systematic in NWS supplement rows) |
| nws-prefix-metadata | 2 | 0 | added "n. [NWS: …]" prefixes — the [FINDINGS §84](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) stylistic class |
| additions (minor) | 1 | 4 | epistemic hedge («zu lesen»→"should probably be read"), Latin explication, disambiguators — the S7 "translate, don't annotate" family, none sense-changing |
| term-weak / term-minor | 2 | 1 | «dahinfahren»→"travel away"; «zu verbinden»→"to be read with" (S7's known slip, recurring); «stockend»→"halting" |
| structure / ls-loss | 0 | 2 | gloss-anchor displacement (r150); window-boundary `<ls>` drop (r101) |
| de-residue (connectives/abbrevs) | 2 | 2 | apparatus «zu / bei / ders.» and `<ab>`-wrapped German abbrevs beside their translations |

Markup degradation (`{%..%}` → `{..}` or ASCII quotes, dropped page markers) was graded **soft** (house precedent: [FINDINGS §84](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) downgraded delimiter findings to stylistic) and appears in the `classes` field of otherwise-correct rows — FU1/Sonnet 5 shows it noticeably more often than the pilot.

## Agreement with S7 (Phase-1 note)

Per-row S7 verdicts were not persisted (only the memo aggregates), so Cohen's κ is not computable — recorded honestly rather than faked. Aggregate comparison on the identical 68-row frame: S7 faithful 33 / acceptable-loss 34 / unfaithful **1**; this pass correct 55 / acceptable-variant 12 / wrong-sense **1** — the **same single unfaithful row (r025)**, i.e. perfect agreement on the blocker class. The faithful/acceptable split differs by rubric mapping only: S7 counted markup-loss rows (32/68) as acceptable-loss, while H1070 grades markup as a soft class on correct rows.

## Provenance

Pass A generation: pilot = Sonnet 4.6 (`claude-sonnet-4-6`); FU1 = Sonnet 5 (`claude-sonnet-5`). Pass B: Monier-Williams 1899 (human) via the MW TM. Adjudicator: Fable 5 (`claude-fable-5`) — three independent sources, per the house pattern. Sampling/statistics scripts committed beside the data (this directory).

Companion decision doc: [PWG_EN_FU1_SCALEUP_GO_NO_GO_2026-07-17.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/PWG_EN_FU1_SCALEUP_GO_NO_GO_2026-07-17.md).

_Dr. Mārcis Gasūns_
