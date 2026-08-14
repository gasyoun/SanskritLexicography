# PWG TM Grok 4.6 — Track B 5,000-key wave (H2684)

_Created: 14-08-2026 · Last updated: 14-08-2026_

Grok 4.6 (`grok-4.6`). Track B of [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pwg_tm_dh_lexicography.md). Frozen queue from [H2683](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2683-Grok_RussianTranslation_pwg-tm-canonical-fragment-priority-w1_13.08.26.md) / [PR #1688](https://github.com/gasyoun/SanskritLexicography/pull/1688). First-slice apparatus: [PR #1689](https://github.com/gasyoun/SanskritLexicography/pull/1689).

## Status: WAVE ACCOUNTED — independent n=400 FAIL after one repair

All 5,000 frozen headwords were processed. Every extracted fragment is either promoted or retained in the uncertain quarantine. The independent 400-fragment gate (Grok 4.5, not Grok 4.6) meets fidelity and equivalence floors and **fails** the serious-error ceiling after one bounded repair. That is a halt, not a second repair.

## Route

| Item | Value |
|---|---|
| Route | `grok-4.6` (explicit `--route`; not a default production path) |
| Model | Grok 4.6 (`grok-4.6`) |
| Prompt | [`src/pwg_tm_prompts/grok46_fragment_v1.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_prompts/grok46_fragment_v1.txt) |
| Prompt SHA-256 | `55ae95622093169a50ad2a622ba6c083dcecece256c0b49a76da59b8465b4c38` |
| Pipeline | `pwg_tm_generate.v1` |
| Gate | `pwg.tm.gate.v1` |
| Frozen manifest | `f024ec4b0b2e58f75868462d84fd51858e4de473d07c0dd825a487f3b73d952a` |
| Independent judge | Grok 4.5 (`grok-4.5`), 8 shards × 50 |

`XAI_API_KEY` was unset. Drafts are session-drafted Grok 4.6. Token counts are 0; cost is **not evaluable**, not zero.

## Wave accounting

| Check | Result |
|---|---|
| Queue / processed / missing source | **5000 / 5000 / 0** |
| Extracted fragments | **753111** |
| Accounted (promoted + quarantine) | **753111** |
| Silent drops | **0** |
| Unaccounted promotions | **0** |
| Promoted | **655332** |
| Quarantine (uncertain tier) | **97779** |

Fill (diagnostic, cumulative): deterministic 632596 · exact address reuse 953 · exact source-string reuse 19718 · session drafts ~250 · sense-merge 4835 · remaining unfilled ~94800 (almost all long sense wrappers still in quarantine).

Resumable dumps stay gitignored under [`release/pwg_tm_canonical/wave1_b/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/pwg_tm_canonical/wave1_b). Compact receipt: [`wave1_b_receipt/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/pwg_tm_canonical/wave1_b_receipt).

New runner commands: `drain` (windowed merge resume), `needed`, `refill`. `run` still overwrites a single window.

## Independent n=400

Stratified stream sample from the finished 753111-row pool (seed 2684). All six classes; accepted 272 / rejected 128 before the repair refill. After one repair the sample has **0 empty targets**.

| Floor | Result | Verdict |
|---|---|---|
| Fidelity ≥98% | **398/400 = 99.5%** (Wilson 98.2–99.9%) | pass |
| Equivalence ≥95% | **382/400 = 95.5%** (Wilson 93.0–97.1%) | pass |
| Serious error ≤1% | **10/400 = 2.5%** (Wilson 1.4–4.5%) | **fail** |

Per class (fid / eq / serious / n): citation 48/48/0/48 · example 48/48/0/48 · grammar_label 48/48/0/48 · recurring_formula 80/79/1/80 · definition_gloss 96/91/5/96 · sense 78/68/4/80.

## One bounded repair

1. Exact source-string lexicon from the existing 2392 publication records (gloss/formula only; not sense wrappers).
2. Extra formula metalanguage (`demin.`, `personif.`, `Uebertr.`/`uebertr.`, …).
3. Session drafts for the 48 sample glosses plus 38 leftover sample senses/formulas; `refill` re-gated the whole quarantine.

Moved to promoted by refill: 863 + 62. The independent gate was run **after** this repair.

## Why serious_error stays above the floor

Ten Grok 4.5 serious flags. Dominant class is **unsafe short-gloss source reuse** from the publication TM:

| Source | Target reused | Judge note |
|---|---|---|
| `{%Jmd%}` (×3 + one sense) | `{%поручать кому-л.%}` | *jemand* dative, not “entrust” |
| `{%die%}` | `{%боги%}` | article, not “gods” |
| `{%gewachsen%}` | `{%соответствующий, способный справиться%}` | “grown”, not “equal-to/capable” |
| `<ab>v. a.</ab>` | `<ab>т. е.</ab>` | judge reads *vor allem*; house table had *videlicet* |
| two long senses | mixed leftover German / wrong verb | residual wrapper prose |

A second repair would be a denylist on short/ambiguous gloss reuse. That is **out of this handoff** (one-repair halt).

## Proof

```text
python src/pwg_tm_generate.py --verify
python src/pwg_tm_quality.py --selftest
python src/pwg_tm_quality.py verify --sample 400 --adjudication release/pwg_tm_canonical/wave1_b_receipt/adjudication400.jsonl --sample-meta release/pwg_tm_canonical/wave1_b_receipt/sample400.jsonl.meta.json
pytest tests/test_pwg_tm_generate.py tests/test_pwg_tm_canonical.py
```

Verify exits 1 on `independent_gate=fail`. That is the honest apparatus.

_Dr. Mārcis Gasūns_
