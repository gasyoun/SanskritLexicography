# Handoff — execute FU1 (PWG→English bulk run)

**For:** a fresh agent session with **Max/Workflow access** (or the autonomous account).
**Goal:** translate the 30 already-RU'd PWG roots that still lack English, to citable-DH
standard, then merge + judge + validate. **All design decisions are MG-locked** — see
[`FU1_PLAN.md`](FU1_PLAN.md) for the rationale; this doc is the *execution* runbook.
Everything lives in `SanskritLexicography/RussianTranslation/`.

## Status (2026-06-30)

- FU2 (`src/pilot/audit_window_en.py`, EN audit gate) + FU3 (`src/promote_en.py`, tri-lingual
  merge) are **merged to `master`** (PR #25, squash). The in-process sense-dupe perf fix +
  this plan are in **PR #26** (`docs/pwg-en-fu1-plan`).
- FU1 is **not started**. Branch off **`master`** (the old `recover/slicec-top3-pat-ga-vad`
  branch was deleted on the #25 squash-merge).

## ⚠️ Read first — guardrails

- **Branch check before every commit:** `git rev-parse --abbrev-ref HEAD` must be your FU1
  branch, **not `master`**. A second (autonomous) account also commits here — announce, don't
  double-run a root, **prefer PR-only**.
- **csl-orig is READ-ONLY** (`mw.txt`, `pwg.txt`): extract, never modify/stage.
- **≤3-wide Workflow concurrency.** Slice-D's 18× fan-out caused a 117-null collapse;
  single/low-width = 0 nulls. Run roots sequentially or ≤3 at a time.
- **Outputs are gitignored regenerable artifacts** (`wf_output*.json`, the stores, `*.json`
  freq tables) — commit only **code/docs**.
- **Report the model tier at every step** (Sonnet for generation, Opus for the judge) — grep
  the actual `model:` in the harness/judge, don't trust the harness description.

## Locked decisions (do not re-litigate — full rationale in `FU1_PLAN.md`)

1. **EN-only + merge** for this tranche (all in scope already have RU). Bilingual single-pass is
   the standing policy for *future* freq roots beyond current RU coverage, **not** this run.
2. **Sonnet generate + Opus judge.**
3. **Scope = match current RU coverage** (the worklist below).
4. **Validation = FU2 audit + Opus judge + human gold sample** (Cohen κ + error rate).
5. **Full per-sense provenance** (`en_provenance`).
6. **Ground truth = faithful to the PWG German** (Monier-Williams = cross-check only); PWG
   sense order preserved (Renou-badge rule, never re-sort).

## Phase 0 — build the scaffolding FIRST (no Max quota)

**Check prior art — adapt, don't reinvent.** The RU pipeline already has every piece; each FU1
tool is an EN adaptation:

| FU1 tool | Adapt from | EN change |
|---|---|---|
| **Opus EN judge** | [`src/fidelity_sample.py`](src/fidelity_sample.py) + [`src/pilot/gen_fidelity_judge.py`](src/pilot/gen_fidelity_judge.py) + `src/pilot/fidelity_aggregate.py` | sample `(de, en)` not `(de, ru)`; rubric = **does `english` faithfully render the German sense** (markup/sigla + PWG sense order = hard sub-checks; MW divergence = soft). Keep the verdict schema `{key, ok, severity, issues, note}` and the `judge_ab_score` BAD rule (`ok=false || severity>=3`) so aggregation/Wilson-CI reuse unchanged. |
| **Provenance-aware merge** | [`src/promote_en.py`](src/promote_en.py) | alongside `en`, attach `en_provenance = {model:'sonnet', judge:{model:'opus', verdict, score}, generated_at, harness_sha256, mw_used:bool}`. Keep `en` a plain string so `export_interop.py` is unaffected. `review_status` stays `ai_translated`. |
| **Human gold sample + κ** | [`src/gold_sample.py`](src/gold_sample.py), [`src/gold_packet.py`](src/gold_packet.py), [`src/gold_validate.py`](src/gold_validate.py), [`src/gold_ingest.py`](src/gold_ingest.py), [`src/gold_agreement.py`](src/gold_agreement.py) | stratify the EN store by **DCS freq band × source_type × stratum**, fixed seed, n≈300; reviewer sheet shows **de + en + headword, MW HIDDEN** (no anchoring); labels judge faithful-to-German; second annotator → `gold_agreement.py` already computes precision + double-review agreement (κ). Emit a short METHODS note. |

Acceptance for Phase 0: each new script has a `--selftest`/`--dry-run`, `python -c "import ast…"`
parses, and a dry-run over the 16 existing EN roots produces a sane sample/judge harness.

## Phase 1 — generate (Max, ≤3-wide)

**Worklist: 30 roots / 1,260 subcards / 5,259 sense rows, ~$42 Sonnet. None exceed the 512 KB
`scriptPath` limit (max 96 subcards) → no `--keys` split needed.**

Freq order: `nI yA dA han car viS jYA vas hA vA diS mA vah iz muc su Ap jan banD man Sru siD vac
ji paS brU laB jIv As gam`

Per root (no deviation):
```sh
git rev-parse --abbrev-ref HEAD                          # your FU1 branch, NOT master
python src/pilot/root_window_status.py <root>            # rootmap + masked inputs must exist;
                                                         # if missing: python src/_pilot_gen_merged.py --manifest freq --root-split --limit N
python src/pilot/gen_opt_harness2.py <root> --lang en --out=src/pilot/run_pilot_wf.en_<root>.js
# → run run_pilot_wf.en_<root>.js via the in-chat Workflow tool, ≤3-wide
python save_and_audit.py <root> <task-output-file> en    # runs audit_window_en.py (FU2); fix HARD flags, re-run nulls
```
- Confirm live cost after the first 2–3 roots against the ~$0.033/card estimate.
- ⚠️ **siD** mirrors the known RU h1 sense-dupe defect (pwg02 over-produces pwg00/pwg03 senses) —
  expect a SENSE-DUPE FAIL until the RU-side h1 dedup lands; don't treat it as an EN regression.

## Phase 2 — merge, judge, validate

```sh
python src/promote_en.py            # attach en + en_provenance onto the RU store rows
python src/annotate_dcs_freq.py     # re-attach dcs_freq (language-agnostic, idempotent)
# Opus judge (Phase-0 tool): sample → gen judge harness → run via Workflow → aggregate
# Human gold: stratified sample → reviewer packets (MW hidden) → 2 annotators → gold_agreement (κ)
```

## Done criteria

- All 30 roots EN-translated; `audit_window_en.py` run per root with **0 hard flags**; nulls
  re-queued; EN merged with `en_provenance`; `dcs_freq` re-annotated.
- Opus judge run on all; precision + 95% Wilson CI reported; verdicts inlined per sense.
- Human gold sample double-annotated; **κ + point error rate (with CI) documented** in a METHODS
  note; ground truth = faithful-to-German.
- G5 human review flips approved rows to `review_status='approved'` — only then does
  `export_interop.py` publish them as the citable tri-lingual edition.

## Pointers

- Plan + decisions: [`FU1_PLAN.md`](FU1_PLAN.md) · parent handoff:
  [`HANDOFF_2026-06-30_pwg_en_followups.md`](HANDOFF_2026-06-30_pwg_en_followups.md)
- EN harness: [`src/pilot/gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py) (`--lang en`) ·
  prompt [`src/pilot/tr_en.txt`](src/pilot/tr_en.txt) · MW TM [`src/mw_en_tm.py`](src/mw_en_tm.py)
- EN audit gate: [`src/pilot/audit_window_en.py`](src/pilot/audit_window_en.py) ·
  merge: [`src/promote_en.py`](src/promote_en.py) · save: [`save_and_audit.py`](save_and_audit.py)
- concurrency doctrine: [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md) ·
  journal: [`.ai_state.md`](.ai_state.md)
