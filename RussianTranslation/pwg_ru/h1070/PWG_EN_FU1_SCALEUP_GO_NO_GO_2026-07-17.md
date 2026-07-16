# PWG→EN scale-up go/no-go — methodology + verdict after the H1070 Fable adjudication

_Created: 17-07-2026 · Last updated: 17-07-2026_

**Verdict: GO (conditional)** for the next PWG→EN tranche and for FU1 Phase 2 (promote_en → dcs_freq → judge inlining → human gold), with three named guard conditions below. Evidence: [H1070_EN_GOLD_ADJUDICATION_2026-07-17.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/H1070_EN_GOLD_ADJUDICATION_2026-07-17.md) (170 rows, Fable 5 `claude-fable-5`, MW quoted per entry). This memo is the FU1-scale-up half of [H1070](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1070-Fable_RussianTranslation_pwg-en-fu1-pilot-adjudication_16.07.26.md); it gates methodology, not the MG-locked sequencing in [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) (giant-head recovery → hard-flag remediation → EN audit dashboard → Phase 2), which stands.

## 1. Decision rule (proposed as the standing EN tranche gate)

Judged on a seeded stratified sample per tranche, sense-row unit, ground truth = the PWG German:

- **GO** — wrong-sense (semantic) point rate ≤ 5% **and** no new silent error class (one that no deterministic gate or judge rubric line covers) **and** mw-tm-contamination = 0 on the tranche sample.
- **HOLD** — wrong-sense point rate in (5%, 10%], or a new silent class appears once: fix the guard/prompt, re-sample the affected stratum before generating further tranches.
- **NO-GO** — wrong-sense > 10%, or mw-tm-contamination recurs after the prompt guard, or any systematic *omission* class (sense loss) — omission is the H920 SAN-LOSS family and blocks regardless of rate.

Rationale for the 5% line: FU1's citable bar is the human-gold error rate with CI ([FU1_PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FU1_PLAN.md) §validation); a machine tranche running at >5% semantic errors would poison the G5 review economics (every fifth-to-twentieth row a real error makes human review the bottleneck the pipeline exists to remove). The RU lane's H911 gate (80% audit-clean) measures a different unit (whole-card audit flags); the EN semantic bar is deliberately stricter because EN rows feed a citable tri-lingual resource.

**Measured against the rule:** FU1 tranche wrong-sense = 3/102 = **2.94%**, Wilson 95% [1.01%, 8.29%] → point estimate comfortably under 5%; no omission class in-sample (the one suspected case resolved as a frame artifact); FU1 mw-tm-contamination = **0/102**. → **GO**, subject to §3.

## 2. Sample-size justification

- Unit = sense row (the EN convention since S7; cards vary 1–48 senses, rows are the citable unit).
- n=102 FU1 rows from 50 cards (population 1,509 cards / ~5,259 rows): at a true 5% error rate the expected count is ~5; observing ≤3 has p≈0.25, so a single tranche sample cannot *acquit* 5% — but the Wilson interval [1.0%, 8.3%] excludes the NO-GO line (10%), which is what a tranche gate must do cheaply. The standing 50-card-per-tranche recipe ([S7 memo](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FABLE_JUDGE_S7_2026-07-02.md) §5) is therefore kept, with the rotated seed making tranche samples pool: pilot+FU1 already pool to 170 rows, CI [0.92%, 5.89%].
- The tight-CI instrument remains the planned **n≈300 human gold sample with Cohen κ** ([`src/gold_sample_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_sample_en.py), built, unrun — it needs the re-merged store, i.e. Phase 2). Tranche gates screen; the human gold certifies.
- Senses/card capped at 3 (seeded) to keep the Fable reading pass within one session; the cap trades within-card coverage for card coverage — correct for a gate whose failure modes (polysemes, homographs, footnote token loss) are row-local, and declared so the cap can be dropped for the human-gold pass.

## 3. GO conditions — the three observed FU1 defects, each with its named guard

1. **German homographs/polysemes at the gloss level** (r155 «braut»→"betroth"; r119 «Vergleich»→"comparison"). No deterministic gate can see these (markup intact, fluent English). Guard: add a **German-polyseme checklist line to the EN judge rubric** in [`gen_fidelity_judge_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_fidelity_judge_en.py) (Vergleich, braut/Braut, gelten, Zug, anführen, …) under `term-mistranslation`, and a one-line prompt rule in [`tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tr_en.txt): "for polysemous German glosses, pick the sense the Sanskrit lemma licenses, never the frequent sense."
2. **`{#..#}` token loss inside `<F>` footnotes** (r102 dropped `{#uc#}` — and the fidelity guard demonstrably did not fire). Guard: verify/extend the restore-time `{#..#}` count check in the accept path to include footnote content; this is deterministic and belongs in [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py) as a HARD flag if the accept-path fix is deferred.
3. **Untranslated cross-ref/NWS residue** (12/170 rows: «Vgl. … fgg.» rows and NWS German locked in `{#..#}`). Non-blocking (meaning preserved for a reader with German), but it is the dominant residual and is *deterministically detectable* — extend the existing DE-RESIDUE gate to flag pure-cross-ref rows and NWS `{#..#}`-wrapped German as a soft class, so coverage stats stop counting them as translated.

Item 2 is the only one with silent-loss potential → it is the one **hard** condition; 1 and 3 are prompt/judge/audit lines to land with the next tranche's code pass.

## 4. What carries over from the RU-side H971 re-audit protocol, and what EN needs differently

Carries over unchanged (deterministic half, [H971 results table](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H971_QA_REAUDIT_2026-07-15.md)): `window_selftest` gate pins · TM validate · per-row provenance stamping · lang-parity no-drift check (`LANG_PARITY.md` classification of every fix as SHARED / INTENTIONAL-DIVERGENCE / GAP) · the A-1(b) date-partition check once EN rows enter the store.

EN needs **additionally** (not in the H971 protocol):

- the per-tranche adjudication gate of §1 (RU's analog is the audit-clean rate; EN's semantic bar is judge-tier);
- **MW-adversary quoting** in every judge/gold sheet (contamination is an EN-only failure mode; note the calibration rule: MW-verbatim agreement is PW-lineage signal, only German-unlicensed MW content is contamination);
- NWS-row handling (German inside `{#..#}` — EN-only, since RU never consumed NWS rows this way);
- the store merge itself: `promote_en.py` has **still never run** — the store carries 0 EN rows (checked 17-07-2026 against `pwg_ru_translated.jsonl`, 11,605 rows) — so every H971 store-level check is vacuous for EN until Phase 2 lands.

## 5. Parked (generation-gated) items — named, not retried

Per the H1070 gate check, the gen-API host remains degraded (H818/H909 lineage; latency NO-GO re-measured in [H994](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/H994_TWO_PROFILE_LIVE_MEASUREMENT_GATE_2026-07-15.md)) — **no fresh generation was attempted in this session.** Parked until the host/profile gates clear:

- giant-head recovery re-runs (gam residual etc., needs `--root-split` + live quota);
- hard-flag remediation of the 4 flagged FU1 cards (banD/gam/jan/laB);
- FU1 Phase 2 execution (promote_en → annotate_dcs_freq → judge run → human gold) — agent-runnable offline *except* the judge pass, which needs a live judge-tier session.

_Provenance: adjudication + memo by Fable 5 (`claude-fable-5`), 17-07-2026; generation under judgment: Sonnet 4.6 (`claude-sonnet-4-6`, pilot) and Sonnet 5 (`claude-sonnet-5`, FU1)._

_Dr. Mārcis Gasūns_
