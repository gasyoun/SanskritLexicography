# Account-switch packet — medium50 LIVE STOP

_Created: 25-07-2026 · Last updated: 25-07-2026_

**Purpose:** Durable resume after Max-account weekly-limit exhaustion. Prepared by Grok 4.5 (`grok-4.5`) for `/account-switch` so a second Max account can continue without re-deriving context.

## What froze

| Field | Value |
|---|---|
| Work | PWG→RU **medium50** — all five windows offline-prepped; live run stopped |
| Stop reason | Gate-0 **NO-GO**: `auth` / HTTP **403 Request not allowed** on c1/c2/c4/c5; prior c2 w1 fix-run hit **rate_limit** / session limit (24-07) |
| Stop rule | **No canary, no paid translation, no store write** until LIVE_GO |
| Repo | [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) → `RussianTranslation/` |
| Claude project dir | `%USERPROFILE%\.claude\projects\C--Users-user-Documents-GitHub-SanskritLexicography-RussianTranslation` |
| Session ID (resume this) | `bf83a5e7-b9ea-4183-b812-945d7e86535a` |
| Session transcript mtime | 25-07-2026 ~06:22 |
| Freeze record | `%USERPROFILE%\.claude\limit-relaunch\frozen-250726-0953.json` (mode=resume, pending) |
| Credentials backup (exhausted account) | `%USERPROFILE%\.claude\.credentials.max-exhausted.20260725-0953.bak.json` |

## Files protected this pass

Committed on branch `ai-wip/medium50-account-switch-*` (see PR/push note in chat):

- `RussianTranslation/.ai_state.md` — Next Steps: medium50 LIVE STOP + resume recipe pointer
- `RussianTranslation/RESULTS_LOG.md` — 25-07 LIVE STOP entry + 24-07 max-agents forensics
- `RussianTranslation/GENERATION_API_PROBE_LOG.md`
- `RussianTranslation/src/pilot/generation_api_probe_log.jsonl`
- `RussianTranslation/MEDIUM50_ACCOUNT_SWITCH_RESUME_2026-07-25.md` — **tracked** copy of the gitignored pilot resume recipe

## Disk-only (gitignored — do not delete)

Still under the **main** checkout path  
`C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot\output\`:

- `MEDIUM50_NO_MAX_AGENTS_RESUME_2026-07-25.md` (original gitignored copy)
- `coordinator/artifacts/h1447-m50-w1` … `h1447-m50-w5` — 48 keys, harnesses + execution manifests

Account switch does **not** move these; they stay on the filesystem.

## Exact resume after second Max login

### A. Switch identity (human, terminal — works at 0% quota)

```powershell
# 1) Confirm exhausted-account backup exists
Get-Item "$env:USERPROFILE\.claude\.credentials.max-exhausted.*.bak.json"

# 2) Remove live credentials (backup already made)
Remove-Item "$env:USERPROFILE\.claude\.credentials.json" -ErrorAction SilentlyContinue

# 3) Start Claude → OAuth as the OTHER Max account
cd C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation
claude
# complete login in browser
```

### B. Resume the SAME conversation (preferred)

```powershell
cd C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation
claude --resume bf83a5e7-b9ea-4183-b812-945d7e86535a
```

Or interactive picker (safer if unsure):

```powershell
claude --resume
```

**Do not use `claude --continue`** unless you are sure nothing else ran in this directory after the freeze.

Sanity-check after resume: ask the model what last completed (transcript tail may be truncated at limit).

### C. If resuming a fresh chat instead of the session

```text
Read C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\ACCOUNT_SWITCH_PACKET_2026-07-25.md and execute the medium50 resume (auth → live-gate → w1–w5 without --max-agents).
```

Also read:

- [`MEDIUM50_ACCOUNT_SWITCH_RESUME_2026-07-25.md`](MEDIUM50_ACCOUNT_SWITCH_RESUME_2026-07-25.md)
- [`.ai_state.md`](.ai_state.md) Next Steps

### D. Paid resume sequence (when `claude -p` works)

1. Confirm auth: `claude -p "ping"` (or any one-shot) — must not return **403**.
2. Fresh `/pwg-live-gate` (health + canary). Canary may use `--max-agents 1` for the single synthetic key only.
3. Only on **LIVE_GO**: headless **w1→w5 without `--max-agents`** per `MEDIUM50_ACCOUNT_SWITCH_RESUME_2026-07-25.md`.
4. Audit each window; `/pwg-window-close` only after clean audit; keep **stop-before-promote**.
5. **Never** copy canary `--max-agents 1` onto multi-key windows (H1610 / H1618).

## Other unfinished surfaces (do NOT cleanup yet)

| Surface | State | Action after medium50 |
|---|---|---|
| SL main checkout branch `docs/pwg-german-layers-clickable` | Tip commit; dirty RT files mirrored into this packet commit | Reconcile branch / open PR if still needed |
| SL stashes | `stash@{0,1}` pwg manuals truth-pass 24-07; `stash@{2}` h1610 forensics | Inspect before `stash drop` or worktree-gc |
| Uprava main | **ahead ~448 / behind ~223**, ~112 dirty, ~63 untracked handoffs | Separate recovery — **do not** `reset --hard` or mass worktree-gc |
| csl-guides #125 / #130 | CONFLICTING; #130 CI fail | PR babysit later |
| SanskritGrammar-h1611…h1614 worktrees | Freeze-probe cluster | Check before gc |

## Switching back to the exhausted account later

```powershell
Copy-Item "$env:USERPROFILE\.claude\.credentials.json" "$env:USERPROFILE\.claude\.credentials.second-max.bak.json"
Copy-Item "$env:USERPROFILE\.claude\.credentials.max-exhausted.20260725-0953.bak.json" "$env:USERPROFILE\.claude\.credentials.json" -Force
```

(Or re-OAuth.) Never delete backups until both accounts have been restored successfully once.

## Non-goals this packet

- Does not schedule a same-account `/limit-relaunch` fire (other Max account is available).
- Does not run paid headless windows.
- Does not reconcile Uprava divergence.
- Does not merge open csl-guides / csl-orig PRs.

_Dr. Mārcis Gasūns_
_Auto-generated by Grok 4.5 (`grok-4.5`) for account-switch prep._
