# E1 — DeepSeek V4 Flash 0731 vs c4 draft (H1210-head 40)

_Created: 13-08-2026 · Last updated: 13-08-2026_

**Executor:** Grok 4.6 (`grok-4.6`) · **Handoff:** [H2488 (Grok 4.5) — E1 Flash 0731 vs c4 paid ~40 stratified cards](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2488-Grok_SanskritLexicography_flash-e1-paid-run-40_08.08.26.md)

**Verdict: FAIL — no production draft-lane for Flash 0731 at the locked H1210 protocol.** Flash does not win a Q1–Q2 draft role. Prep-pack / mechanical-QA remains the ceiling (map §5 step 3).

Pre-declared rule (frozen before this run): [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/VERDICT_RULE.md). Machine copy: [verdict.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/verdict.json).

## What ran

| Item | Value |
|---|---|
| Sample | [sample_manifest.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/sample_manifest.json) — 40 keys, `keys_sha256` `a2cda36d61b8dc68…`, H1210 worklist head, not new gold |
| Arm B | `deepseek-v4-flash` via [`deepseek_arm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/deepseek_arm.py), default `max_tokens=8192`, 6 workers, `--no-tm` slice |
| Arm A (c4 CLI) | **BLOCKED_ON_C4_INFRA** — see below. Own-data c4 baseline is H1210's published 72% shippable on the parent 100-card sample |
| Controller | not run (2 cards `pending-controller`; Grok session has no H1210 Workflow) |
| TM / store | **no write** — `deepseek_arm.py` has no store/TM path; slice built with `--no-tm`; promoter never invoked |
| Wall | 2855.5 s · 113 generation calls · **$0.2317** (list price 0.14 / 0.0028 / 0.28) |

Reproduce:

```text
# inputs (gitignored) via PWG_INPUT_DIR + _pilot_gen_merged.py on the 40 SLP1 keys
python experiments/E1_deepseek_vs_c4/e1_build_slice.py
python src/pilot/h1210/deepseek_arm.py \
  experiments/E1_deepseek_vs_c4/run/e1_40.slice_payload.json \
  experiments/E1_deepseek_vs_c4/run/e1_40.manifest.json \
  experiments/E1_deepseek_vs_c4/run/arm_b \
  --env-file <ORS-FAQ/.env>
python src/pilot/h1209/canonical_audit.py \
  experiments/E1_deepseek_vs_c4/run/arm_b.slice_result.json \
  experiments/E1_deepseek_vs_c4/run/e1_40.manifest.json \
  --out experiments/E1_deepseek_vs_c4/run/arm_b.canonical_audit.json
```

## Arm B numbers (this sample)

| Metric | Flash 0731 (n=40) |
|---|---:|
| Attempted | 40/40 |
| `clean-no-review` (unattended shippable) | **4 (10%)** |
| `pending-controller` | 2 (5%) |
| `worker-null-death` | **34 (85%)** |
| Canonical promote-DRY PASS | **6/40 (15%)** |
| USD total | 0.2317 |
| USD / unattended-clean | 0.0579 |
| USD / audit-clean | 0.0386 |
| In tokens (miss / hit) | 78 622 / 512 640 |
| Out tokens | 782 914 |

Unattended-clean keys: `_s_aluqa`, `kr_urar_avin`, `vinikfntana`, `zazwivrata`.
Audit also PASS on the two pending-controller cards (`_svetakar_ra`, `tubarI`) — they are not unattended-shippable under the H1210 definition (`promote_dry` ∧ status in `{clean-no-review, clean-controller-approved}`).

## Why 85% died

Default `max_tokens=8192` (the H1210 arm-B cap; **not raised after seeing results**). Most failed calls end `finish_reason=length` and `extract_json` reports `no JSON object in response`. Even the four clean cards used 6.6k–8.1k completion tokens. Flash 0731 is too verbose for this schema at the locked cap. That is the measured defect, not a transport outage (one SSL EOF on a retry does not change the denominator).

This is the same truncation class H1210 recorded for old `deepseek-chat` on high-polysemy heads ([FINDINGS §68](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)), now the **majority** outcome on a short-to-medium 40-card head.

## Arm A — BLOCKED_ON_C4_INFRA

A fresh c4 CLI / H1210 Workflow run on these 40 keys was not executed:

1. This session has no Claude Workflow tool (`wf_template_ab.js` / `control_template.js`).
2. Production `headless_worker` still classifies Max billing as UNKNOWN unless a human authorizes it ([H2591](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/README.md)).
3. Per-card H1210 `arm_a.chunk*.slice_result.json` files are gitignored and were **not** on disk, so a 40-key subset cannot be extracted.

Own-data c4 baseline that **is** on disk: [H1210 A/B report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md) — Claude-native shippable **72%** (n=100), audit-clean 93%. These 40 keys are that worklist's head (reuse, not new gold).

## Pre-declared clauses

| # | Rule | This run |
|---|---|---|
| 1 | shippable_B ≥ shippable_A − 5pp | **FAIL** vs H1210 own-data c4 72%: 10% ≱ 67%. A fresh 40-key c4 number is missing (INCONCLUSIVE if someone refuses the parent-sample baseline); it cannot rescue Flash unless c4 on this head were ≤15%, which H1210 Q1–Q2 (100% shippable) makes implausible |
| 2 | $/shippable_B ≤ 1/20 of c4 | **INCONCLUSIVE** — no arm A dollars this pass. H1210 marked c4 USD n/a (subscription). Flash $0.0579/clean is cheap in cash and irrelevant once clause 1 fails |
| 3 | Blinded judge severity not worse at p<0.05 | **INCONCLUSIVE** — controller not run; 34 null cards have no judgeable card |

Flash wins a production draft-lane **iff ALL three**. Clause 1 fails. **FAIL. No scheduler branch (map §5 step 4).**

## store_write proof

- [`deepseek_arm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/deepseek_arm.py) writes only `{out_prefix}.slice_result.json`, `{out_prefix}.telemetry.json`, and an append-only journal. No TM, no store, no promoter.
- Slice built with `gen_opt_harness2.py --no-tm`.
- Artifacts: [arm_b.slice_result.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/run/arm_b.slice_result.json), [arm_b.telemetry.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/run/arm_b.telemetry.json), [arm_b.canonical_audit.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/run/arm_b.canonical_audit.json).

## What this does not say

- It does not say Flash is useless as **prep-pack** (H2489 spike still stands).
- It does not say a higher `max_tokens` would pass E1 — that would be a **new** pre-registered experiment.
- It does not authorize unattended Flash→TM.

_Dr. Mārcis Gasūns_
