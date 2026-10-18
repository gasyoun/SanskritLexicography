# sandhi-bench v2 — public junction-recovery benchmark

_Created: 06-10-2026 · H6063 · public release per ruling B4 (grill research-widening, 04-10-2026)_

**One line:** given a sandhied continuous surface token in its sentence
context, recover the original two-word junction `LEFT+RIGHT` — graded by
deterministic exact match against DCS-derived gold.

The gold lineage is the [kosha sandhi programme](https://github.com/gasyoun/kosha/blob/main/SANDHI_PROGRAMME.md):
DCS CoNLL-U `Unsandhied=` fields → method-A junction-rule inducer
(96.3 % Gītā-gold coverage) → per-text tables → **this bench** (junction-level
harvest, 7,979 items, text-disjoint splits).

## The task

```json
{"id": "sb-000170", "text": "amarakosa", "sent": "bhaginīpatir ābutto bhāvo vidvānathāvukaḥ",
 "sandhied": "vidvānathāvukaḥ", "category": "visarga", "rule": "ḥ a → n a",
 "gold": "vidvāḥ+atha"}
```

Answer format: a single string `LEFT+RIGHT` — one plus sign, no spaces.
Grading: NFC → casefold → whitespace-collapse, then exact string equality
(the same casefold decision the SSB W3.2 identifiability review locked for
IAST sandhi answers). Unanswered = wrong.

Items whose DCS-side stem is `_` (empty placeholder — not a two-word
junction) are excluded at build time (57 candidates dropped).

## Splits (text-disjoint)

| split | items | texts | role |
|---|---|---|---|
| `train` | 5,561 | 33 | learning / few-shot source |
| `dev` | 478 | 4 | model selection |
| `test` | 1,940 | 5 | reported |

A work appears in exactly one split, so surface-form memorisation cannot
leak across splits (enforced at build time and re-audited by
`audit_gold.py` check A2). Seed: `20261004` (first seed satisfying
per-split category coverage).

Categories (share of all items): `consonant / other`, `vowel coalescence`,
`visarga`, `anusvāra / nasal` — every category present in every split.

## Reproduce everything

```bash
python sandhi-bench/build_dataset.py                        # rebuild splits + manifest
python sandhi-bench/audit_gold.py                           # A1–A4 gold audit → results/gold_audit.json
python sandhi-bench/baselines/mfs_baseline.py --split test  # MFS floor
python sandhi-bench/baselines/mfs_baseline.py --split dev
python sandhi-bench/baselines/llm_baseline.py --run --split test --sample 100   # local ollama, opt-in
python sandhi-bench/build_leaderboard.py                    # regenerate leaderboard.html
python sandhi-bench/evaluate.py --pred YOUR.jsonl --split test   # grade a submission
```

`build_dataset.py` needs a local kosha clone (`SANDHI_BENCH_KOSHA=<path>`
or a sibling checkout of the main repo); everything else is offline.
Source pin: kosha `790203061a99` (recorded in `data/manifest.json`).

## Baselines shipped (measured 06-10-2026)

| system | test exact acc | test macro | dev | notes |
|---|---|---|---|---|
| **Gold ceiling** | 100 % | — | — | by construction (induced DCS gold) |
| **MFS** (most-frequent split per surface, train-only) | **57.3 %** | 59.6 % | 9.4 % | surface-OOV on test 42.5 % — 99.7 % exact on seen surfaces, 0.0 % on OOV (identity fallback never matches); dev's 4 texts are 90.2 % OOV — the honest floor |
| **LLM local · qwen2.5:7b-instruct** (5-shot, temp 0) | **3.0 %** | 1.3 % | — | 100-item seeded subsample (seed 20261006), 4 unanswered; well-formed but lexically wrong splits |

The MFS floor is high on test because frequent compounds repeat across
works — 57.5 % of test surfaces also occur in train, MFS answers 99.7 %
of those exactly, and its identity fallback scores 0.0 % on the 42.5 %
OOV residue. A system must beat 57.3 % exact to claim it does anything
beyond lexical lookup. The 7B local LLM
shows the task is not solvable by generic plausibility: both stems must be
lexically exact.

**External context, not comparable rows:** the kosha splitter bake-off
measured token-level F1 on full-text splitting — vidyut-cheda 0.282 ·
DharmaMitra neural 0.795 (precision 0.90–0.97). Different metric, different
unit; kept here so nobody re-runs that comparison against this leaderboard.

**Contamination honesty:** the source texts are in every frontier LLM's
pretraining data. As with the F48 defgen bench, these numbers measure
*sandhi competence including memorisation*, never generation from corpus
evidence alone.

## Leaderboard

[`leaderboard.html`](leaderboard.html) — self-contained, regenerated from
`results/*.json` by `build_leaderboard.py` (derived-don't-store; hand edits
are overwritten).

**Submission protocol:** PR adding
`sandhi-bench/results/<system>_results_test.json` + your predictions jsonl,
then run `build_leaderboard.py`. No test answers in prompts; dev is for
model selection only. Report the exact model/version and the protocol block
unchanged from the runner output.

## Licenses (verified)

| what | license |
|---|---|
| bench **data** (`data/*.jsonl`, manifest, results) | **CC BY-SA 4.0** — inherits the share-alike of the DCS source ([Digital Corpus of Sanskrit](https://sanskrit.uohyd.ac.in/sciencecs/), Oliver Hellwig, CC BY-SA 4.0) via the kosha tables ([kosha manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)) |
| bench **code** (this directory) | **MIT** — repository [`LICENSE`](../LICENSE) |
| redistribution scope | **derived measurements only** — junction records harvested from the kosha aggregate tables; the raw DCS dump is not redistributed (same `derived_only` rights shape as the SSB pilot tasks) |

## Scope exclusions (deliberate)

- **No Vedic sandhi** — ruling B5 reserves it as a separate split/bench.
- **ScharfSandhi dataset** — ruling B10 says include it; not yet in the
  estate, tracked as a follow-up row (FEATURES_INDEX F52 residual).
- **Multi-annotator κ gold** — ruling B8 targets 3-annotator κ; today's
  gold is single-source DCS-derived, audited by the automated A1–A4 audit
  plus the inducer's 96.3 % Gītā-gold coverage. A human-κ pass on a
  subsample is the natural v2.1 step.

## Layout

```
sandhi-bench/
  build_dataset.py        # harvest kosha tables → text-disjoint splits + manifest
  audit_gold.py           # A1 provenance · A2 split hygiene · A3 identity · A4 manifest
  evaluate.py             # deterministic grader (exact match, casefold-normalized)
  baselines/mfs_baseline.py    # MFS floor (train-only lookup)
  baselines/llm_baseline.py    # local-ollama LLM reference (opt-in --run)
  build_leaderboard.py    # results/*.json → leaderboard.html
  data/{train,dev,test}.jsonl · data/manifest.json
  results/                # committed baseline results + gold audit
  leaderboard.html
```

Tests: [`tests/test_sandhi_bench.py`](../tests/test_sandhi_bench.py)
(11 offline checks — grader, parser, split disjointness, manifest parity,
MFS determinism, leakage-detector positive control).

---

_Dr. Mārcis Gasūns · Sanskrit Lexicon Project_
