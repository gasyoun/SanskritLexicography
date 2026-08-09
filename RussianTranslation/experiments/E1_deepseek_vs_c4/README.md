# E1 — DeepSeek V4 Flash 0731 vs c4 draft (Wave 3 scaffold)

_Created: 08-08-2026 · Last updated: 08-08-2026_

**Status:** scaffold frozen for measurement — **not** a production role grant (R2.3).
Paid bulk E1 run is a residual until budget/key window is used deliberately.

## What is frozen here

| Artifact | Role |
|---|---|
| [sample_manifest.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/sample_manifest.json) | ~40 keys = head of H1210 stratified worklist (`keys[0:40]`) — reuse, not new gold |
| [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/VERDICT_RULE.md) | Pre-declared win rule (shippable ≥ c4−5pp **and** $/shippable ≤ 1/20 c4 **and** judge severity) |

## How to run (when measuring)

```text
# Arm B default model is deepseek-v4-flash (H2439)
python src/pilot/h1210/deepseek_arm.py <slice_payload.json> <manifest.json> <out_prefix> \
  --env-file <path-to-ORS-FAQ-.env> --keys=$(paste -sd, keys-from-manifest)

# Optional: freeze a store-stratified sample instead of the H1210 head
python src/pilot/openrouter_worker.py --freeze-sample --out-dir experiments/E1b_store \
  --store <canonical pwg store> --size 40
```

Prep-only path (allowed before E1 win; no TM write):

```text
python src/pilot/h1210/prep_pack.py --worklist src/pilot/h1210/H1210_ab100_worklist.28.07.26.json \
  --limit 40 --out-dir prep/e1 --dry
```

## Policy pointers

- Multilane R1.2 / R2.3 / R3.4 E1: [PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md)
- Org pricing + roles: [DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md](https://github.com/gasyoun/Uprava/blob/main/docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md)
- H1210 prior (old `deepseek-chat`): [H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md)
- Handoff: H2439 (Sonnet 5 intended; Grok 4.5 dual-run scaffold 08-08-2026)

_Dr. Mārcis Gasūns_
