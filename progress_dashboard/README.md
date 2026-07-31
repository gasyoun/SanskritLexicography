# PWG→RU progress & kitchen dashboard

_Created: 10-07-2026 · Last updated: 31-07-2026_

Public companion to the [article site](https://gasyoun.github.io/SanskritLexicography/).
Where the article site shows the **finished** PWG→Russian translations, this shows:

1. **Progress** — honest denominators for each lane (verb funnel, store depth, coverage).
2. **Kitchen** — the process behind the work: speed, cost, idle gaps, campaign calendar,
   and the project web changelog.

Published at **`/progress/`** on gh-pages.

> **Caveat (still true):** a dashboard that *renders* is not a dashboard that is *current*.
> Trust the numbers only when a generator has re-run since the last store change. The fix
> for live campaigns is [`live_refresh.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/live_refresh.py)
> (rebuilds + publishes every minute while translation artifacts are moving). The HTML
> also re-fetches JSON every 60s with `cache: 'no-store'`.

## What it shows

### Progress
- **Verb lane funnel** (H151) — vetted PWG verb roots → DCS-attested → promoted → runnable / blocked.
- **Store depth** — sense-rows in the RU spine, AI-first-pass vs human-reviewed.
- **Frequency coverage** — share of PWG that is DCS-attested (first-pass ceiling).
- **Nominal lane** + corpus-lexicon / TM asset.
- **Trend** — one point per rebuild day (append-only timeseries).

### Kitchen
- **Speed** — cards last hour / 24h, mean wall-clock minutes per window.
- **Cost** — mean tokens per window; optional economy-ledger agents/$ per clean card.
- **Idle** — gaps between `stage_boundary` audit_end → next audit_start (ledger fallback).
- **Calendar** — day heatmap of cards written (store provenance) + window counts.
- **Web changelog** — recent version bullets from `RussianTranslation/CHANGELOG.md`.

For **sub-second** run/gate telemetry on the residential machine (not published), use the
local ops server:

```
python RussianTranslation/src/pilot/dashboard_server.py
# http://127.0.0.1:8765/  (polls /api/status every 5s)
```

## Files

| File | Role |
|---|---|
| [`build_progress_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_progress_data.py) | lane/store/coverage snapshot → `progress_data.json` + timeseries |
| [`build_kitchen_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_kitchen_data.py) | speed/cost/idle/calendar/changelog → `kitchen_data.json` |
| [`live_refresh.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/live_refresh.py) | 60s loop while translation is on → rebuild + push `gh-pages/progress/` |
| [`progress_data.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/progress_data.json) | progress snapshot (committed occasionally; live ticks go to gh-pages only) |
| [`progress_timeseries.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/progress_timeseries.json) | append-only daily trend rows |
| [`kitchen_data.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_data.json) | kitchen snapshot |
| [`index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/index.html) | self-contained page; polls JSON every 60s |

## Refresh

**Runs locally, not in CI.** Numbers come from gitignored / local-only artifacts under
`RussianTranslation/` that Actions never checks out.

### While a translation campaign is on (every minute)

```
# from the main checkout (or any worktree; data is read via PWG_DATA_ROOT)
python progress_dashboard/live_refresh.py
```

Behavior:
- rebuilds when store / window_status / ledger / events are younger than 15 minutes
- publishes HTML+JSON to `origin/gh-pages` `progress/` only (does **not** spam master)
- exits after 5 consecutive idle ticks (configurable `--idle-stop`)
- logs to `progress_dashboard/live_refresh.log` (gitignored if you add it)

One-shot publish even when idle:

```
python progress_dashboard/live_refresh.py --once --force
```

Rebuild without pushing:

```
python progress_dashboard/live_refresh.py --once --force --no-publish
```

### Manual builders

```
python progress_dashboard/build_progress_data.py
python progress_dashboard/build_kitchen_data.py
```

Building from an isolated worktree that lacks the gitignored data:

```
PWG_DATA_ROOT=/path/to/main/checkout python progress_dashboard/build_kitchen_data.py
```

### Monthly CI copy

[`findings-dashboard.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml)
copies whatever is committed under `progress_dashboard/` onto gh-pages `/progress/` on its
monthly run (or `workflow_dispatch`). It does **not** rebuild from the store. Live campaigns
must use `live_refresh.py`.

## Provenance

Most numbers are counted live from the pipeline's own files. Two progress denominators are
documented constants (marked `*` in the trust block): total PWG headwords (106,082) and
95.4% corpus recall (H309). "Promoted" means passed the mechanical + review gate and written
to the shipped store — not merely generated.

_Dr. Mārcis Gasūns_
