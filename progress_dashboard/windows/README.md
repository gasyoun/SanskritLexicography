# Windows autostart — PWG→RU dashboards

_Created: 31-07-2026 · Last updated: 31-07-2026 (logon-only ruling)_

Keeps both dashboard surfaces running **without a manual start after logon** on the residential machine (WIN-NJTORH3267V / user `WIN-NJTORH3267V\user`), matching the `SL findings dashboard refresh` Task Scheduler pattern (H737).

| Task name | Trigger | What |
|---|---|---|
| `SL progress dashboard server` | logon | `run_dashboard_server.cmd` → http://127.0.0.1:8765/ (**5 s** local ops) |
| `SL progress live refresh` | logon | `run_live_refresh.cmd` → `live_refresh.py --idle-stop 0` (**60 s** web kitchen → `gh-pages/progress/`) |

Contract of the two surfaces (poll rates, public vs local): [progress_dashboard/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/README.md) · [RU deep manual §2d](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md).

## Register (once per machine / after path change)

```powershell
cd C:\Users\user\Documents\GitHub\SanskritLexicography
powershell -ExecutionPolicy Bypass -File progress_dashboard\windows\register_tasks.ps1 -StartNow
```

| Flag | Effect |
|---|---|
| `-StartNow` | Launch both tasks immediately (do not wait for next logon) |
| `-Unregister` | Remove both tasks |

## Logon mode (what is automatic vs what needs a human)

| Mode | Behaviour | Status |
|---|---|---|
| **Default (shipped)** | `InteractiveToken` — tasks run when this Windows user is **logged on** (desktop session). RestartOnFailure every 1 min × 999. `StartWhenAvailable` (missed logon fires later). | **Registered on WIN-NJTORH3267V** (31-07-2026) |
| **Logged-off / headless** | “Run whether user is logged on or not” needs stored credentials | **Not wanted** while one PC does translation (ruling 31-07-2026) — see below |

### Logged-off stored credentials — closed for now

**Ruling 31-07-2026:** when Windows is off, there is no translation on that box, so the kitchen does **not** need to keep publishing. Logon-only is enough for a single residential machine.

Revisit **only if several PCs translate at once** and an always-on publisher is required. Recipe (then, not now):

```powershell
# Type the password when prompted (*). Only if multi-PC / always-on is decided.
schtasks /Change /TN "SL progress dashboard server" /RU WIN-NJTORH3267V\user /RP *
schtasks /Change /TN "SL progress live refresh"     /RU WIN-NJTORH3267V\user /RP *
```

## Logs (gitignored)

| File | Source |
|---|---|
| `progress_dashboard/windows/dashboard_server.log` | local ops server wrapper |
| `progress_dashboard/windows/live_refresh_daemon.log` | live_refresh wrapper stdout |
| `progress_dashboard/live_refresh.log` | Python live_refresh logger |

## Behaviour

- **Dashboard server:** if port **8765** is already LISTENING, the wrapper exits 0 (single-instance). Task Scheduler restarts on failure.
- **Live refresh:** `--idle-stop 0` so the daemon **never exits** when the campaign is idle — it sleeps 60 s and keeps watching store / window_status / ledger / events mtimes. Publishes only when artifacts are young (or payload fingerprint changes). Writes **only** `gh-pages/progress/` — never spams `master`.
- **Paths:** hard-coded to `C:\Users\user\Documents\GitHub\SanskritLexicography` and prefers `C:\Python314\python.exe`. Edit the `.cmd` files + re-run `register_tasks.ps1` if the clone or Python install moves.
- **Other machines:** not registered by default; run `register_tasks.ps1` after cloning and fixing paths.

## Residual inventory (honest)

| Item | Status |
|---|---|
| Autostart while **logged on** | Done (tasks registered) |
| Autostart while **logged off** | **Closed** — not needed until multi-PC concurrent translation (ruling 31-07-2026) |
| Public Pages + local ops code | Done (H2032 PRs #927–#935) |
| Dual-surface docs interlinked | Done |
| GitHub release tags for every `1.114.x` changelog section | Optional hygiene (`/cut-release`) — not required for autostart |
| Uprava H2032 handoff on `origin/main` | May still be local-only if mint push failed |

## Related

- [progress_dashboard/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/README.md)
- [RU deep manual §2d](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
- Findings monthly twin: task `SL findings dashboard refresh`
- [MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md) subproject map

_Dr. Mārcis Gasūns_
