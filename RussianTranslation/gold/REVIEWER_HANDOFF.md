# Reviewer Handoff

This handoff prepares the remaining human gates. Do not change IDs, Sanskrit
source text, Russian source text, period/kind/work metadata, or machine labels.

## G5 Translation Review

Use `src/_review_queue.csv`.

Fill only:

- `reviewer_id`: stable reviewer handle.
- `decision`: one of `approved`, `human_reviewed`, `needs_review`, `reject`.
- `edit`: optional corrected Russian text.
- `notes`: optional reviewer note.

Do not mark a row `approved` or `human_reviewed` unless the Russian text is
print-ready and the row keeps placeholder/key integrity.

Helpful file: `review_readiness_report.md`.

## G6 Human Gold Labels

Use the packets in `gold/reviewer_packets/`, then merge labels back into
`gold/_human_gold_review.csv`.

Fill only:

- `human_label`: one of `correct`, `lemma-variant`, `proper-name`, `partial`,
  `wrong-sense`, `hallucinated`.
- `reviewer_id`: stable reviewer handle.
- `confidence`: one of `low`, `medium`, `high`.
- `needs_adjudication`: one of `true`, `false`, `yes`, `no`, `1`, `0`.
- `human_note`: optional.

Do not edit `id`, `slp1`, `sa`, `ru`, `kind`, `period`, `work`, `llm_label`,
`src_sa`, `src_ru`, or `src_comm`.

## G7 Double Review

Use `gold/_double_review_queue.csv` for the independent second review.

Fill only:

- `second_reviewer_id`
- `second_human_label`
- `second_confidence`
- `second_needs_adjudication`
- `second_human_note`

The second reviewer must differ from the first reviewer when `reviewer_id` is
already present.

## Validation Commands

```powershell
python src/run_batch.py validate_review
python src/gold_status.py gold/_human_gold_review.csv
python src/gold_packet_verify.py gold/_human_gold_review.csv gold/reviewer_packets
python src/gold_double_review_verify.py gold/_double_review_queue.csv --sample-size 80
python src/preflight_remaining_gates.py
```
