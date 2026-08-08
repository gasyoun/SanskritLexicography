# `src/pilot/h1210/` — the DeepSeek-vs-Claude A/B rig (H1210)

_Created: 29-07-2026 · Last updated: 08-08-2026_

Everything needed to reproduce the [H1210](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1210-Opus_SanskritLexicography_pwg-ab-deepseek-vs-claude-100_17.07.26.md)
A/B: **one variable changes — the generator.** Arm A is the Claude-native
[H1209](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1209/canonical_audit.py)
rig (Sonnet workers under an Opus controller); arm B replaces the worker with DeepSeek
(default **`deepseek-v4-flash`** as of H2439 / 08-08-2026; H1210 historical run used
`deepseek-chat` — pass `--model deepseek-chat` to reproduce) and keeps the prompt, the
output schema, the free deterministic gate, the ≤2-retry chain, the **same** Opus
controller, and the same authoritative post-run audit.

Results, method and the human-vote design:
[`pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md).

## What is where

| File | Role |
|---|---|
| [`select_ab100.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/select_ab100.py) | the stratified 100-card selection (length deciles · defect-class culprits · no_pwg · verb roots · medium50 overlap) |
| [`H1210_ab100_worklist.28.07.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_ab100_worklist.28.07.26.json) | the frozen worklist it produced — the A/B's input of record |
| [`pack_chunks.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/pack_chunks.py) | size-bounded repack of a `prep_slice` payload (equal-COUNT chunks are unusable on a length-stratified slice) |
| [`wf_template_ab.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/wf_template_ab.js) | arm A — the H1209 v2 template with two named deltas (parallel card loop, 900 s agent deadline) |
| [`det_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/det_gate.py) | Python twin of the in-JS free gate, so arm B is gated identically (`selftest` asserts the branches) |
| [`deepseek_arm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/deepseek_arm.py) | arm B — DeepSeek generation + the same retry chain + per-call cost/latency telemetry (default Flash 0731 + PRICE 0.14/0.0028/0.28) |
| [`prep_pack.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_pack.py) · [`prep_pack.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_pack.schema.json) | Map §3.1 **Flash PREP** → `prep/{key}.json` (senses, TM hits, flags, optional draft) **+ free `det_gate`** (no Claude): prep-level always; full H1210 twin when a draft card exists. Modes: `fill` / `live` / `dry`; `--gate-only` re-runs gate. **Never** writes TM store (R4.3a); `det.claude` always false |
| [`det_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/det_gate.py) | Free Python twin of the H1209 JS gate — used by arm B **and** prep_pack (no Claude) |
| E1 Flash sample | [`experiments/E1_deepseek_vs_c4/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/) — frozen ~40 keys + pre-declared win rule |
| [`control_template.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/control_template.js) | the shared Opus controller, lifted out so arm B passes through the *same* stage |
| [`arm_b_control.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/arm_b_control.py) | the `build` / `apply` shuttle between arm B and that controller (rounds) |
| [`collect_arm_a.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/collect_arm_a.py) · [`extract_verdicts.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/extract_verdicts.py) | lift Workflow return values + per-role token usage out of the task-output files |
| [`ab_report.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/ab_report.py) | the comparative table (audit-clean %, defect classes, $/clean, calls/clean, retry/escalation, controller share) |
| [`length_breakdown.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/length_breakdown.py) | audit-clean rate by entry-length quartile — the interaction the headline % hides |
| [`coverage_gap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/coverage_gap.py) | which cards each arm never attempted, per quartile and by name — run it BEFORE quoting any rate ([FINDINGS §500](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)) |
| [`qc_gloss_arity.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/qc_gloss_arity.py) | one-card probe for gloss-arity drift — the axis the `{Tn}` multiset gate cannot see |
| [`build_ab_review_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/build_ab_review_sheet.py) | the BLIND human-vote sheet (arm labels exist only in `review/locks/…lock.json`) |

## Reproduce

```
# 0. inputs (gitignored, regenerable)
python src/_pilot_gen_merged.py $(tr '\n' ' ' < src/pilot/h1210/keys_pwg.txt)
python src/_pilot_gen_merged.py $(tr '\n' ' ' < src/pilot/h1210/keys_nopwg.txt)

# 1. manifest + payload  (--no-selfheal keeps 1 card = 1 unit in BOTH arms)
python src/pilot/gen_opt_harness2.py _nominal --nominal --no-selfheal \
  --keys=$(paste -sd, src/pilot/h1210/card_ids.txt) \
  --manifest-out=src/pilot/h1210/h1210_ab100.manifest.json \
  --out=src/pilot/h1210/h1210_ab100.opt2.js
python src/pilot/h1209/prep_slice.py src/pilot/h1210/h1210_ab100.manifest.json \
  src/pilot/h1210/slice_payload.json
python src/pilot/h1210/pack_chunks.py src/pilot/h1210/slice_payload.json src/pilot/h1210/ab100

# 2. arm A — one Workflow launch per chunk
for f in src/pilot/h1210/ab100.chunk*.json; do
  python src/pilot/h1209/build_args.py $f src/pilot/h1210/h1210_ab100.manifest.json ${f%.json}.args.json
  python src/pilot/h1209/inject_payload.py src/pilot/h1210/wf_template_ab.js ${f%.json}.args.json ${f%.json}.wf.js
done
# ...run each .wf.js through the Workflow tool, then:
python src/pilot/h1210/collect_arm_a.py chunk01 <task_output.json> ...

# 3. arm B — generation, then controller rounds
python src/pilot/h1210/deepseek_arm.py src/pilot/h1210/slice_payload.json \
  src/pilot/h1210/h1210_ab100.manifest.json src/pilot/h1210/arm_b --env-file <path/to/.env>
python src/pilot/h1210/arm_b_control.py build src/pilot/h1210/arm_b.slice_result.json 1
# ...run arm_b.control_r1.wf.js, then:
python src/pilot/h1210/extract_verdicts.py <task_output.json> src/pilot/h1210/arm_b.control_r1.verdicts.json
python src/pilot/h1210/arm_b_control.py apply src/pilot/h1210/arm_b.slice_result.json \
  src/pilot/h1210/arm_b.control_r1.verdicts.json --payload src/pilot/h1210/arm_b.control_r1.payload.json \
  --slice-payload src/pilot/h1210/slice_payload.json --manifest src/pilot/h1210/h1210_ab100.manifest.json \
  --env-file <path/to/.env> --null-retry
# repeat build/apply until no card is `pending-controller`

# 4. authoritative verdict + report + blind sheet
python src/pilot/h1209/canonical_audit.py src/pilot/h1210/arm_a.chunk*.slice_result.json \
  src/pilot/h1210/h1210_ab100.manifest.json --out src/pilot/h1210/arm_a.canonical_audit.json
python src/pilot/h1209/canonical_audit.py src/pilot/h1210/arm_b.slice_result.json \
  src/pilot/h1210/h1210_ab100.manifest.json --out src/pilot/h1210/arm_b.canonical_audit.json
python src/pilot/h1210/ab_report.py --arm-a-result src/pilot/h1210/arm_a.chunk*.slice_result.json ...
python src/pilot/h1210/build_ab_review_sheet.py --arm-a-audit ... --arm-b-audit ... --per-arm 20
```

## Things that will bite you

- **Card ids are safe-name stems, not SLP1 keys.** The harness, both arms and the audit key
  on `_s_aluqa` / `arvant~~h0_zz_pw`; only the worklist keeps `SAluqa`. Join through
  `ab_report.card_id()` — joining on `key1` matches almost nothing and silently drops cards
  into an unknown stratum.
- **The API key never enters this directory.** `--env-file` points at a `.env` outside the
  repo; no key is written into any artifact, log or telemetry file.
- **The review-sheet HTML is gitignored** (unpublished RU) — only its lock is committed.
- Everything here is **promote-DRY**: no card from either arm was promoted to the store.

_Dr. Mārcis Gasūns_
