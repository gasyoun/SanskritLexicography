# Human Review Minimization

Date: 2026-06-28

Goal: get from "translation machine works" to defensible print-readiness
evidence with the smallest valid human workload. Do not review all PWG entries
manually. Use deterministic gates first, ranked semantic queues second, and
human judgment only where the release gates require it.

## Current Verdict

Bulk translation can continue after a fresh `sTA` Max run, but print publication
cannot happen until G5/G6/G7/G10 pass.

Current gate status:

| gate | status | blocker |
|---|---|---|
| G5 translation review | blocked | 0/11,163 review decisions; 0 print-ready rows |
| G6 human gold | blocked | 0/320 labels complete |
| G7 double review | blocked | 0/80 second reviews; no agreement report |
| G10 edition cut | blocked | waits for G5/G6/G7 |

Production status:

```powershell
python src\pilot\root_window_status.py sTA
```

Current result: `sTA` is structurally ready, but `wf_output.json` is stale.
Run the generated Max Workflow for `sTA`, save fresh `wf_output.json`, then run:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue
```

Do not advance to `BU` until fresh `sTA` passes the deterministic audit and the
semantic sample policy has been applied.

## Review Order

Use this order for every window or release slice:

1. **Python-gate failures first.** These are mechanical and fastest to fix:
   stale workflow output, missing cards, markup loss, coverage loss, duplicate
   senses, NWS owner mismatches, prompt-rule drift.
2. **High-confidence semantic risks second.** Start from
   `prompt_rule_audit.md` / the `prompt_semantic` section in
   `audit_window.report.md`; prioritize untranslated German residue, broken
   markup, translated sigla/grammar, empty Russian, and `{%...%}` gloss leaks.
3. **Clean-card semantic sample third.** Use `judge_sample.keys.txt`; do not
   browse the whole window by hand.
4. **Publication gates last.** G5/G6/G7 are release evidence gates, not a
   substitute for the production audit loop.

## G5 Translation Review

Input file: `src/_review_queue.csv`

Purpose: decide whether existing translated rows are print-ready.

The regenerated queue currently covers the full promoted translation store
(11,163 `ai_translated` rows). This is a G5 publication-review queue, **not**
the gold annotation set. Do not expand G6 to all 11,163 rows; G6 remains the
bounded, stratified 320-row gold sample unless a later methodology decision
changes the sample design.

Allowed edit columns:

| column | allowed values / use |
|---|---|
| `reviewer_id` | stable reviewer handle |
| `decision` | `approved`, `human_reviewed`, `needs_review`, `reject` |
| `edit` | optional corrected Russian text |
| `notes` | optional reviewer note |

Do not edit: `review_id`, `severity`, `ord`, `key1`, `key2`, `review_status`,
`key_match`, `placeholders_ok`, `reason`, `attested`, `ru`.

Minimum valid action:

1. Open `src/_review_queue.csv`.
2. Fill only the allowed columns.
3. Mark `approved` or `human_reviewed` only when the Russian is print-ready and
   placeholder/key integrity is preserved.
4. Validate:

```powershell
python src\run_batch.py validate_review
python src\run_batch.py review_report
python src\preflight_remaining_gates.py
```

Done when: G5 reports review decisions present and at least one print-ready row.
For a print release, all rows included in that release slice must be reviewed or
explicitly excluded.

## G6 Human Gold Labels

Input files:

- reviewer packets: `gold/reviewer_packets/gold_packet_*.csv`
- merge target: `gold/_human_gold_review.csv`

Purpose: provide a human gold standard for quality measurement.

Allowed edit columns in `gold/_human_gold_review.csv`:

| column | allowed values / use |
|---|---|
| `human_label` | `correct`, `lemma-variant`, `proper-name`, `partial`, `wrong-sense`, `hallucinated` |
| `reviewer_id` | stable reviewer handle |
| `confidence` | `low`, `medium`, `high` |
| `needs_adjudication` | `true`, `false`, `yes`, `no`, `1`, `0` |
| `human_note` | optional |

Do not edit: `id`, `slp1`, `sa`, `ru`, `kind`, `period`, `work`,
`llm_label`, `src_sa`, `src_ru`, `src_comm`.

Minimum valid action:

1. Fill packet rows in `gold/reviewer_packets/`.
2. Merge labels back into `gold/_human_gold_review.csv`.
3. Validate:

```powershell
python src\gold_status.py gold\_human_gold_review.csv
python src\gold_validate.py gold\_human_gold_review.csv
python src\gold_packet_verify.py gold\_human_gold_review.csv gold\reviewer_packets
python src\preflight_remaining_gates.py
```

Done when: `gold_status.py` reports 320/320 complete and
`gold_validate.py` passes.

## G7 Double Review

Input file: `gold/_double_review_queue.csv`

Purpose: measure independent reviewer agreement over the stratified sample.

Allowed edit columns:

| column | allowed values / use |
|---|---|
| `second_reviewer_id` | stable reviewer handle; must differ from first reviewer if present |
| `second_human_label` | same label set as G6 |
| `second_confidence` | `low`, `medium`, `high` |
| `second_needs_adjudication` | `true`, `false`, `yes`, `no`, `1`, `0` |
| `second_human_note` | optional |

Do not edit the original G6 columns or any source/context columns.

Minimum valid action:

```powershell
python src\gold_double_review_verify.py gold\_double_review_queue.csv --sample-size 80
python src\gold_ingest_double_review.py gold\_double_review_queue.csv gold\double_review_labels.jsonl
python src\gold_agreement.py
python src\preflight_remaining_gates.py
```

Done when: the 80-row double-review queue validates, labels are ingested, and
the agreement report exists.

## Minimum Human Work Policy

- Do not ask a human to inspect deterministic failures until Python has named
  the exact key and defect class.
- Do not sample semantic quality before stale/requeue defects are cleared.
- Do not review full PWG tail entries before the DCS-frequency core tranche has
  enough audited windows to estimate speed and error rate.
- Do not cut an edition with zero G5 print-ready rows, incomplete G6 labels, or
  missing G7 agreement.

## Fastest Path To Print Evidence

1. Fresh `sTA` Max output.
2. `audit_window.py` until mechanical requeue is empty.
3. Semantic sample from `judge_sample.keys.txt`.
4. G5 review rows for the core tranche.
5. G6 320-row gold complete.
6. G7 80-row double review complete.
7. `release_readiness.py`.
8. Immutable `edition_vN` cut only after G5/G6/G7 pass.
