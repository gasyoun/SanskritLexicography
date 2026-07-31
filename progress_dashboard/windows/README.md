# Windows autostart — PWG→RU dashboards

_Created: 31-07-2026 · Last updated: 31-07-2026_

Keeps both dashboard surfaces running **without a manual start** on the residential machine (WIN-NJTORH3267V), matching the "SL findings dashboard refresh" Task Scheduler pattern (H737).

| Task name | At | What |
|---|---|---|
| `SL progress dashboard server` | logon | `run_dashboard_server.cmd` → http://127.0.0.1:8765/ (**5 s** local ops) |
| `SL progress live refresh` | logon | `run_live_refresh.cmd` → `live_refresh.py --idle-stop 0` (**60 s** web kitchen to gh-pages) |

## Register (once per machine / after path change)

```powershell
cd C:\Users\user\Documents\GitHub\SanskritLexicography
powershell -ExecutionPolicy Bypass -File progress_dashboard\windows\register_tasks.ps1 -StartNow
```

- **`-StartNow`** — also launches both tasks immediately (do not wait for next logon).
- **`-Unregister`** — remove both tasks.
- LogonType = `InteractiveToken` (runs when this user is logged on). Stored-credentials "run whether logged on or not" is a human @DO if needed later.

## Logs

| File | Source |
|---|---|
| `progress_dashboard/windows/dashboard_server.log` | local ops server |
| `progress_dashboard/windows/live_refresh_daemon.log` | wrapper stdout |
| `progress_dashboard/live_refresh.log` | Python live_refresh logger |

All three are gitignored under `progress_dashboard/windows/*.log` and the existing `live_refresh.log` rule.

## Behaviour

- **Dashboard server:** if port 8765 is already LISTENING, the wrapper exits 0 (single-instance). Task Scheduler restarts on failure every 1 min (count 999).
- **Live refresh:** `--idle-stop 0` so the daemon never exits when the campaign is idle — it sleeps 60 s and keeps watching store/ledger mtimes. Only publishes when artifacts are young (or fingerprint changes). Does **not** spam master; only `gh-pages/progress/`.
- **Paths:** hard-coded to `C:\Users\user\Documents\GitHub\SanskritLexicography` (this residential clone). Edit the `.cmd` files + re-run `register_tasks.ps1` if the clone moves.

## Related

- [progress_dashboard/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/README.md) — 5 s vs 60 s contract
- [RU deep manual §2d](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
- Findings monthly twin: task `SL findings dashboard refresh`

_Dr. Mārcis Gasūns_
