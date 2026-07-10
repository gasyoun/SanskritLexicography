# PWG→RU progress dashboard

_Created: 10-07-2026 · Last updated: 10-07-2026_

Public companion to the [article site](https://gasyoun.github.io/SanskritLexicography/).
Where the article site shows the **finished** PWG→Russian translations, this shows
**how far along the work is** — the honest denominators for each lane.

Published at **`/progress/`** on gh-pages once the workflow runs (see below).

## What it shows

- **Verb lane funnel** (H151) — vetted PWG verb roots → DCS-attested (in scope) →
  promoted → runnable / blocked-on-rootmap.
- **Store depth** — sense-rows translated into the RU spine, split by AI-first-pass
  vs human-reviewed.
- **Frequency coverage** — what share of PWG is DCS-attested (the first-pass ceiling).
- **Nominal lane** + the corpus-lexicon / TM asset.
- **Trend** — one point per rebuild (append-only timeseries).

## Files

| File | Role |
|---|---|
| [`build_progress_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_progress_data.py) | reads local-only pipeline artifacts, emits the two JSONs below |
| [`progress_data.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/progress_data.json) | one snapshot of every lane/metric (committed) |
| [`progress_timeseries.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/progress_timeseries.json) | append-only, one row per build date, for trend lines |
| [`index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/index.html) | self-contained page; fetches the two JSONs |

## Refresh

**Runs locally, not in CI.** The numbers come from gitignored / local-only artifacts
(`RussianTranslation/src/pwg_ru_translated.jsonl`, the `*_batch_worklist.json`
snapshots, the frequency manifest) that GitHub Actions never checks out — exactly
like [`build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py).

```
python progress_dashboard/build_progress_data.py
```

Then commit the refreshed `progress_data.json` + `progress_timeseries.json`. The
[`findings-dashboard.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml)
workflow **copies** the committed HTML+JSON onto gh-pages `/progress/` on its monthly
run (or `workflow_dispatch`); it does **not** rebuild them.

Building from an isolated worktree that lacks the gitignored data? Point the script
at the checkout that has it:

```
PWG_DATA_ROOT=/path/to/main/checkout python progress_dashboard/build_progress_data.py
```

## Provenance

Most numbers are counted live from the pipeline's own files. Two are documented
constants (marked `*` in the trust block): the frequency **denominator** (106,082
total PWG headwords, from `RussianTranslation/.ai_state.md`) and the **95.4% corpus
recall** (measured in H309). "Promoted" means passed the mechanical + review gate and
written to the shipped store — not merely generated.

_Dr. Mārcis Gasūns_
