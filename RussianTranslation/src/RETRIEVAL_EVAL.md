# RETRIEVAL_EVAL — H1457 A6 retrieval measurement

_Created: 22-07-2026 · Last updated: 22-07-2026_

Harness: `tm_retrieval_eval.py` (Sonnet 5, `claude-sonnet-5`), H1457 Track A6. Fixed eval batch: 20 grade-A rows from `gold/grade_gold.jsonl` (`RETRIEVAL_EVAL_BATCH.jsonl`).

## Status: BLOCKED — no live translation engine available in this environment

A6 needs a LIVE translation-engine call for both arms (no-TM baseline vs graded-TMX-as-fuzzy-context). Per [`research/nn_api_smoketest.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/nn_api_smoketest.md) (spike S1) and [`src/GRADE_CALIBRATION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/GRADE_CALIBRATION.md) (A2), this environment has no `DEEPSEEK_API_KEY` (`build_corpus_lexicon.py` expects one in a repo-local `.env`; none exists in this worktree or the main checkout) and no Anthropic API key. No fabricated quality/wall-clock numbers are reported here — that would misrepresent a measurement that never ran.

## What IS built and tested

- `cmd_batch`: reproducible eval-batch construction from the frozen gold (deterministic, id-sorted, grade-A only).
- `run_arm` / `fuzzy_context`: the measurement loop (wall-clock per card, token accounting, mean quality), engine-agnostic via a pluggable `translate_fn`/`judge_fn` pair.
- `selftest` exercises the full loop with deterministic MOCK engines (a fixed-latency mock translator + a mock judge that scores context-aided output higher), proving the harness correctly computes the deltas it is designed to report.

## To activate

Supply a real `translate_fn(card, context) -> {text, tokens}` and `judge_fn(card, output) -> float` (e.g. wrapping the existing `build_corpus_lexicon.py` DeepSeek client once a key is configured, or an Anthropic client), then `run_arm(cards, translate_fn, judge_fn)` for the no-TM arm and `run_arm(cards, translate_fn, judge_fn, tm_index)` for the with-TM arm — no other code changes needed.

_Dr. Mārcis Gasūns_
