# Human gold-set protocol for `pwg_ru`

This protocol turns the existing LLM-judged scaffold
[`gold_set.jsonl`](gold_set.jsonl) into a human-checked precision set. Until this
human pass is complete, [`precision_report.md`](precision_report.md) remains an
LLM-estimate and must not be cited as print-grade scientific precision.

## Goal

Freeze a stratified, human-reviewed sample of corpus-lexicon alignments and use
it to report precision with Wilson 95% confidence intervals. The gold set
measures whether a Sanskrit token or lemma was aligned to an acceptable Russian
rendering in its actual source context.

## Inputs

- `gold_set.jsonl` — committed minimal scaffold: id, SLP1, Sanskrit surface,
  Russian rendering, kind, period, work, and current LLM label.
- `src/gold_sample.jsonl` — gitignored context sample when present: source
  Sanskrit/Russian verse or commentary context.
- `_human_gold_review.csv` — generated spreadsheet view for human reviewers.

Generate the reviewer spreadsheet with:

```powershell
python src\gold_review_csv.py
```

## Labels

Use exactly one label per row:

| label | Meaning |
|---|---|
| `correct` | The Russian rendering is a correct contextual equivalent. |
| `lemma-variant` | The rendering is correct after normal inflection/lemma normalization. |
| `proper-name` | The item is a proper name or title rendered acceptably. |
| `partial` | The rendering is related but incomplete, over-broad, too narrow, or contextually marginal. |
| `wrong-sense` | The rendering belongs to the wrong sense in this context. |
| `hallucinated` | The Russian item is unsupported by the source context. |

For precision reporting, `correct`, `lemma-variant`, and `proper-name` count as
good; `partial` is reported separately; `wrong-sense` and `hallucinated` count
as errors.

## Review Workflow

1. Export `_human_gold_review.csv`.
2. Assign every row to one reviewer and assign at least 10% of rows, stratified
   by `period × kind`, to a second reviewer.
3. Reviewers fill only the human columns:
   `human_label`, `reviewer_id`, `confidence`, `needs_adjudication`, and
   `human_note`.
4. Valid `confidence` values are `high`, `medium`, and `low`.
5. Set `needs_adjudication` to `yes` when the reviewer is uncertain, the source
   context is insufficient, or two reviewers disagree.
6. The lead editor resolves every adjudication row and records the final label
   before precision is reported.

## Acceptance Criteria

- Every row has a valid final human label.
- Every label outside the LLM scaffold is traceable to a reviewer id.
- At least 10% of rows have independent second review, balanced across period
  and kind as far as the current sample allows.
- Disagreements are counted and reported; agreement is reported as percent
  agreement at minimum, with Cohen/Fleiss kappa if the reviewer layout supports it.
- The final report clearly separates human-confirmed precision from the older
  LLM-judged estimate.

