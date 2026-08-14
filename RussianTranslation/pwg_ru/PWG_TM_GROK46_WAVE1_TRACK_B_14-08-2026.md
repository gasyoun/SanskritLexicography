# PWG TM Grok 4.6 — Track B first slice (H2684)

_Created: 14-08-2026 · Last updated: 14-08-2026_

Grok 4.6 (`grok-4.6`). Track B of [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pwg_tm_dh_lexicography.md). Frozen queue from [H2683](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2683-Grok_RussianTranslation_pwg-tm-canonical-fragment-priority-w1_13.08.26.md) / [PR #1688](https://github.com/gasyoun/SanskritLexicography/pull/1688) (`d30086e15`).

## Status: PARTIAL

The runner, deterministic gates, resumable checkpoint, and independent-sample apparatus shipped. The frozen 5,000-headword wave is **not** finished. The independent n=400 quality gate is **not_run** — Grok 4.6 did not adjudicate its own sample.

## Route

| Item | Value |
|---|---|
| Route | `grok-4.6` (explicit `--route` required; not a default production path) |
| Model | Grok 4.6 (`grok-4.6`) |
| Prompt | [`src/pwg_tm_prompts/grok46_fragment_v1.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_prompts/grok46_fragment_v1.txt) |
| Prompt SHA-256 | `55ae95622093169a50ad2a622ba6c083dcecece256c0b49a76da59b8465b4c38` |
| Pipeline | `pwg_tm_generate.v1` |
| Gate | `pwg.tm.gate.v1` |
| Frozen manifest | `f024ec4b0b2e58f75868462d84fd51858e4de473d07c0dd825a487f3b73d952a` |

`bounded_staged_run.py` is unchanged. Headless/Max defaults stay as they were.

## First bounded slice

Ten compact keys, two from each frozen stratum:

| Stratum | Keys |
|---|---|
| attested_high | `BAvya`, `Aqambara` |
| lexical_core | `Ayuta`, `Sabara` |
| rare_attested | `Antara`, `jambuka` |
| complex | `AlAna`, `AhAva` |
| index_tail | `Ayuzmant`, `akzama` |

| Check | Result |
|---|---|
| Requested / found / missing source | **10 / 10 / 0** |
| Extracted fragments | **734** |
| Accounted (promoted + quarantine) | **734** |
| Silent drops | **0** |
| Unaccounted promotions | **0** |
| Promoted | **679** |
| Quarantine (uncertain tier) | **55** |

Fill: deterministic 587 · Grok 4.6 gloss drafts 65 · sense-merge 42 · unfilled 40. Quarantine is mostly long sense wrappers with leftover German prose, plus two non-German `{%the%}` / `{%star%}` spans left unfilled on purpose.

Draft origin is **session-drafted** Grok 4.6. `XAI_API_KEY` was unset; no xAI HTTP call. Token counts are 0; cost is **not evaluable**, not zero.

Artifacts: [wave1_b_slice/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/pwg_tm_canonical/wave1_b_slice). Resume state lists the remaining 4,990 queue keys in `checkpoint.json`.

## Independent 400-fragment sample

A stratified 400-row sample was frozen from this slice pool (all six classes; accepted 347 / rejected 53; seed 2684). The blind packet strips Grok generation/gate self-assessment.

| Independent gate | Result |
|---|---|
| Floors | ≥98% fidelity, ≥95% equivalence, ≤1% serious error |
| Adjudication | **not_run** |
| Why | No non-Grok judge file. Self-scores are refused (`judge_model=grok-4.6` → `refused_not_independent`). |

The packet is [independent_packet.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/wave1_b_slice/independent_packet.jsonl). A later session fills `adjudication.judge_model` with a human or a different model, then `python src/pwg_tm_quality.py verify --sample 400 --adjudication FILE`.

This 400 is a sample of the **10-key first slice**, not of a finished 5,000-headword wave.

## Proof

```text
python src/pwg_tm_gates.py --selftest
python src/pwg_tm_generate.py --verify
python src/pwg_tm_quality.py --selftest
python src/pwg_tm_quality.py verify --sample 400
pytest tests/test_pwg_tm_generate.py tests/test_pwg_tm_canonical.py
```

All green. Quality verify exits 0 with `independent_gate=not_run` when no adjudication file is supplied — that is the honest apparatus, not a pass.

## Remaining

1. Resume `pwg_tm_generate.py run --route grok-4.6 --resume` over the other 4,990 keys (needs `XAI_API_KEY` or further session drafts).
2. Independent judge (human or non-Grok model) on a 400-row packet from the finished wave.
3. One bounded repair if that independent gate is below the floor.
4. Track C (TEI / OntoLex / release) is out of this handoff.

_Dr. Mārcis Gasūns_
