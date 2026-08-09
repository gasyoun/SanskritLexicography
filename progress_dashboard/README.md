# PWG→RU progress & kitchen dashboard

_Created: 10-07-2026 · Last updated: 06-08-2026 (H2269 dual-run: health_probe_log path)_

**Improvement backlog (measured / show / should-measure):**
[ROADMAP_PROGRESS_KITCHEN_IMPROVEMENTS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/ROADMAP_PROGRESS_KITCHEN_IMPROVEMENTS_2026.md).

## Autostart (no manual step after logon)

On the residential machine (WIN-NJTORH3267V), Task Scheduler starts both surfaces at **logon**:

| Task | Surface |
|---|---|
| `SL progress dashboard server` | local ops http://127.0.0.1:8765/ (5 s) |
| `SL progress live refresh` | web kitchen publish every 60 s while translating |

```powershell
# once per machine (or after clone path change)
powershell -ExecutionPolicy Bypass -File progress_dashboard\windows\register_tasks.ps1 -StartNow
```

- **Default (and current policy):** runs when this Windows user is **logged on** (`InteractiveToken`). When Windows is off there is no translation on that box, so the kitchen does not need to publish — ruling 31-07-2026.
- **Logged-off / multi-PC:** deferred until several PCs translate at once; recipe parked in [`windows/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/windows/README.md).
- Residual inventory: same [windows/README](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/windows/README.md) § “Residual inventory”.

Public companion to the [article site](https://gasyoun.github.io/SanskritLexicography/).
Where the article site shows the **finished** PWG→Russian translations, this shows:

1. **Progress** — honest denominators for each lane (verb funnel, store depth, coverage).
2. **Kitchen** — the process behind the work: speed, cost, idle gaps, campaign calendar,
   and the project web changelog.

## Two dashboards — do not conflate them

| Surface | URL | Browser poll | Data publisher | Audience |
|---|---|---|---|---|
| **Web kitchen (this folder)** | [gasyoun.github.io/…/progress/](https://gasyoun.github.io/SanskritLexicography/progress/) | **every 60 s** | residential [`live_refresh.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/live_refresh.py) while translation is on | anyone with the link |
| **Local ops** | `http://127.0.0.1:8765/` | **every 5 s** | live read of gitignored store/ledger on this machine | operator on the residential box |

- **Web ≠ live socket.** The public page only moves when `live_refresh.py` (or a manual rebuild + gh-pages publish) has run since the last store change. A rendered page can still be **stale**.
- **Local ≠ public.** [`dashboard_server.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/dashboard_server.py) never leaves localhost; GitHub Actions cannot see the store.
- Operator depth (when to open which surface): [RUSSIANTRANSLATION_DEEP_MANUAL.md §2d](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md).
- Orientation row: [MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md) (progress_dashboard + local ops).

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
- **Cost** — mean tokens per window; optional economy-ledger agents/$ per clean card;
  absolute **total $ band** split into *clean dictionary* (first-pass clean tokens) vs
  *prep / redo* (clean=0 wasted + requeue windows); optional **subscription window $**
  from a human-pasted `economy_subscription.json` (never invent dollars — H2218 B1).
- **Idle** — current idle, last completed gap, total recorded idle, and **idle days by month**
  since campaign start; gaps between `stage_boundary` audit_end → next audit_start
  (ledger fallback). Recent windows and idle gaps lists are **1:1 length** (default 12);
  full idle-gap history expands on click. Each gap carries a **reason class** (B9):
  `human` · `weekly_cap` · `health_nogo` · `machine_off` · `waiting_requeue` · `unknown`
  (operator log and measured auto-rules only — silence stays `unknown`).
- **Article-site parity** — store unique roots vs `article_site/md/*.md` (B10); `measured: false` if the site is not built locally.
- **Lease collision / store-hit banner (OPT-8, H2229)** — red kitchen banner when
  `dashboard_events.jsonl` records a store-hit or lease-collision abort (occupied-keys
  overlap, unreadable live manifest, nominal keys already active). **Operator one-liner:**
  if the banner is red (or `collision_guard.blocked=true`), **do not start a second paid
  window** on those keys/root — wait for the live job to finish or requeue that lease.
  Fixture: [`examples/collision_events.example.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/examples/collision_events.example.jsonl).
  Selftest: `python progress_dashboard/kitchen_collision_selftest.py`.
- **Calendar** — day heatmap of cards written (store provenance) + window counts.
- **Health ribbon (K5 / B3 residual, H2240 + H2269)** — last c4 (and sibling) probe
  GO/NO-GO + recent sparkline. Writer contract: every `live_probe` reading appends to
  the **canonical**
  [`RussianTranslation/src/pilot/output/health_probe_log.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/output/health_probe_log.jsonl)
  (gitignored runtime log; created on first probe). Per-account
  `h963_*_gate0_probe_events.jsonl` / `*_probe_events.jsonl` files stay untouched for
  gate reports. Reader (`kitchen_slices.health_ribbon`) prefers the canonical file
  **exclusively** when present; falls back to the old glob scrape only on a pre-H2240
  checkout. One-time history fold:
  `python RussianTranslation/src/pilot/migrate_health_probe_log.py`
  (`--dry-run` first; `--output-dir <path>` for another checkout). Pin:
  `python progress_dashboard/health_ribbon_selftest.py`.
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
| [`build_kitchen_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_kitchen_data.py) | speed/cost/idle/calendar/changelog + K1–K8 + H2218 residual → `kitchen_data.json` |
| [`kitchen_slices.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_slices.py) | pure aggregators (operator, yield, health, subscription, idle reasons, parity, multi_lane B8, H2241 `progress_kitchen_slice`) |
| [`kitchen_progress_slice_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_progress_slice_selftest.py) | H2268 dual-run pin — progress_kitchen_slice field map / GO encoding / no review invent |
| [`kitchen_multi_lane_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_multi_lane_selftest.py) | H2231 B8 — gen_model/host/profile mix fixture pins |
| [`backfill_ledger_metrics.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/backfill_ledger_metrics.py) | best-effort historical wall-clock / gen_model backfill (dry-run; `--apply` rewrites gitignored ledger) |
| [`examples/economy_subscription.example.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/examples/economy_subscription.example.json) | paste schema for subscription $ |
| [`examples/idle_reason_log.example.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/examples/idle_reason_log.example.jsonl) | operator idle-reason log format |
| [`live_refresh.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/live_refresh.py) | 60s loop while translation is on → rebuild + push `gh-pages/progress/` |
| [`progress_data.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/progress_data.json) | progress snapshot (committed occasionally; live ticks go to gh-pages only) |
| [`progress_timeseries.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/progress_timeseries.json) | append-only daily trend rows |
| [`kitchen_data.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_data.json) | kitchen snapshot |
| [`quality_timeseries.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/quality_timeseries.json) | B4 — append-only daily fidelity/judge-coverage trend, one row per build date (`kitchen_slices.quality_timeseries_append`, sourced from `quality_slice()`'s `fidelity_aggregate.json` + ledger judge-sample counts) |
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

### Optional residual inputs (H2218)

| File (gitignored under `RussianTranslation/src/pilot/output/`) | Purpose |
|---|---|
| `economy_subscription.json` | Human-pasted weekly Max / usage total → kitchen subscription card. Copy from [`examples/economy_subscription.example.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/examples/economy_subscription.example.json); leave absent for `measured: false`. |
| `idle_reason_log.jsonl` | Operator tags for long pauses (`reason` ∈ taxonomy). Auto-rules also apply from health NO-GO probes and ledger `weekly_cap_fired` / `needs_requeue` when evidence overlaps a gap. |

Historical metric backfill (local ledger only):

```
python progress_dashboard/backfill_ledger_metrics.py           # dry-run coverage report
python progress_dashboard/backfill_ledger_metrics.py --apply   # rewrite ledger + .bak
python progress_dashboard/build_kitchen_data.py               # refresh kitchen %
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
