# FINDINGS dashboard

_Created: 02-07-2026 · Last updated: 18-07-2026_

Recurring visualization of the
[FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
registry — importance/section breakdown, staleness flags, monthly time series for the
re-measurable findings, and the §41 platform-liveness board.

**Live page:** <https://gasyoun.github.io/SanskritLexicography/findings/>

**Scope:** the public SanskritLexicography registry only. The
[Uprava/FINDINGS.md](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) infra registry
is a private repo (network-topology findings) and is deliberately NOT rendered here.

## Pieces

| File | Role |
|---|---|
| [build_findings_data.py](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/build_findings_data.py) | Parses FINDINGS.md → `data.json`; collects the tracked metrics (§12 DCS→CDSL linkage, §13 glossary coverage, §21 citation coverage, §25 queue decay) from their owning repos (local sibling first, raw.githubusercontent.com fallback) and appends one snapshot/month to `timeseries.json`. |
| [probe_platforms.py](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/probe_platforms.py) | Probes the 12 platforms of §41 → `platform_status.json`. **Residential machine only** — several hosts block GitHub Actions IPs (Uprava §1). |
| [monthly_refresh.py](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/monthly_refresh.py) | Local Task-Scheduler entrypoint: throwaway worktrees → build + probe → commit `master` → publish `gh-pages/findings/`. Never touches the main checkout's branch. |
| [index.html](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/index.html) | The dashboard — single file, vanilla JS + inline SVG charts, no build step, no external deps. |
| [findings-dashboard.yml](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml) | GitHub Actions monthly cron (3rd, 06:17 UTC): registry meta + metric snapshot + publish. No probes (blocked egress). |

## Refresh model — "monthly, mixed"

- **GitHub Actions** (3rd of month): everything reachable from a datacenter — the registry
  parse and the four metric collectors (all raw.githubusercontent.com fetches of public repos).
- **This machine** (Task Scheduler, 3rd of month 09:30, task name `SL findings dashboard
  refresh`): the platform probes, which need residential egress; runs the full
  `monthly_refresh.py` pipeline, so it also doubles as a fallback if the Action fails.

A failed collector records `null` and the build continues — a chart simply skips that month.

**Backfill note (18-07-2026, H737):** every snapshot before 2026-07-18 recorded
`dcs_cdsl_linkage_pct: null` because the §12 collector regex never matched its source
(fixed by H733). The 2026-07-11 snapshot is kept as `source: "backfill"` with the value
recomputed from the source's git history (81.4%, csl-apidev `ec56968`, unchanged
2026-07-03→11); the superseded 2026-07-10 bot snapshot (`c91d62a`) had identical inputs.
No earlier snapshots exist, so nothing else was recoverable.

## Staleness

`data.json` flags findings whose newest Source date is older than **180 days** — the
dashboard lists them 🔴-first as candidates for re-measurement (registry §25 measured how
fast a verified queue decays; the same logic applies to the findings themselves).

_Dr. Mārcis Gasūns_
