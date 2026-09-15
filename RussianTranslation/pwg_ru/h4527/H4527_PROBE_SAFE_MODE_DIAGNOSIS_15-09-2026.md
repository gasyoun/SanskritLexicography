# H4527 — the readiness probe never used the lane's `--safe-mode`: diagnosis, fix, live reading

_Created: 15-09-2026 · Last updated: 15-09-2026_

**Handoff:** [H4527](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4527-Opus_RussianTranslation_pwg-ru-cohort-live-acceptance-width2_10.09.26.md), work item 1 (live serial acceptance through `--cohort-path`). **Executor:** Opus 5 (`claude-opus-5`), unattended worker on `c1`.
**Previous pass:** [H4527_LIVE_ACCEPTANCE_ATTEMPT_11-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_LIVE_ACCEPTANCE_ATTEMPT_11-09-2026.md). It ended with the acceptance window stopped by `fleet probe STOP on account c1: warm-up probe content` and prescribed «retune `_probe_prompt`».

## 1. What was wrong — the probe and the lane start the CLI differently

| | paid lane (`headless_worker.call`) | readiness probe (`max_account_orchestrator._probe_call`) |
|---|---|---|
| `--permission-mode plan` | yes | yes |
| `--json-schema`, exact model | yes | yes |
| bare cwd (H2299) | yes | yes |
| **`--safe-mode`** (H2189, default ON since H2251) | **yes** — `resolve_safe_mode(manifest)` | **never** — no reference anywhere in the module |

`claude --help` (CLI 2.1.270) defines `--safe-mode` as *«Start with all customizations (CLAUDE.md, skills, plugins, hooks, MCP servers, custom commands and agents, output styles, workflows …)»* disabled. So the probe spawns with the whole interactive `c1` profile, including the SessionStart and UserPromptSubmit hooks that inject status dumps and nudges into the turn. The lane it certifies never sends any of that. This is the defect class H2299 fixed for the cwd ("the gate priced a different call than the lane it gates"), repeated one flag over.

## 2. Evidence (read from files on disk, no new spend)

1. **The refusals name the ambient context.** H4277 recorded that the 07-09 01:41Z transcript refused a *«prompt-injection attempt layered on ambient context»*; its third stated reason was *«the surrounding system-reminders»*. H4213 §6.2–6.3 classified the same class as *«c1 profile Stop-hook noise read as injection»* and listed option (a), *«quiet hook noise on headless profiles»*.
2. **The hooks run inside the probe spawn.** The 10-09 23:36Z refused-probe envelope (`output/h963_c4_gate0_probe_raw_h4213-canary-233608.txt`) ends with a `SessionEnd hook [...sessionend_session_ledger.py] failed` traceback. A `--safe-mode` spawn runs no hooks.
3. **Profile-sized prefix.** The 11-09 18:08Z refused probe sent a first request of **50 209** tokens (`cache_creation_input_tokens`, `cache_read` 0) for a 10 729-byte prompt, of which only ≈3 K tokens are the prompt itself. The same probe on the fix (§4) sends first requests of **≈35 K**: the warm-up created 36 104 tokens, then read 34 393 on its structured-output turn, and the measured call read 59 628 + created 11 746 over two requests. The same day's safe-mode canary, carrying a *larger* real-card prompt, used 12 147 create + 25 901 read ≈ 38 K. So without the flag the probe carried roughly **15 K extra tokens of profile context per request**, and the lane never sends them.
4. **The 11-09 counterexample points here too.** Three paid lane calls succeeded on `c1` in the two hours before the refusal (canary GO 15:58Z and 16:19Z, real window 17:58Z). The 11-09 pass read this as clearing «host and hooks» and blaming the prompt text. But all three ran through `headless_worker` **with `--safe-mode`** (`status.canary.json`: `cli_safe_mode_effective: true`). What they actually clear is the route, the credentials and the host. The one input that differed was the profile surface, and the hooks sit inside that surface.

**Correction to the 11-09 packet and to H4213's row:** the counterexample does **not** retire §6.3 option (a). It supports (a) and demotes (b). The prompt text was already repaired twice (H994, H4277). Retuning it a third time would have tuned against noise the lane never sees.

## 3. The fix (this PR) — the probe now matches the lane

- `_probe_call` appends `--safe-mode` exactly when `headless_worker.resolve_safe_mode({}, claude)` says the lane would. That is the lane's own resolver with no manifest, i.e. the H2251 default. The value is never hardcoded, and when the CLI does not advertise the flag the probe falls back exactly as the lane does.
- The probe row records `cli_safe_mode_effective` (one boolean, added to `run_observability.ALLOWED`). Later readings can then say which surface they were taken on.
- **Not weakened:** prompt, schema, model, plan mode, ceilings, the warm-up-STOP rule and the `{"ok": true}`-only content check are all byte-identical. The probe still refuses every regression it refused before. It just stops seeing input that production does not send.
- Pin: `max_account_orchestrator_selftest` → *«H4527 probe --safe-mode: == headless_worker.resolve_safe_mode({}) both ways»*. H2326 pin (6) was widened by one provenance key, with the reason stated inline.

## 4. Live reading on the fix (one ration attempt, `c1`)

Run from this PR's worktree code, with evidence written into the shared checkout's durable output tree (`--evidence-dir`). This is the lesson of 11-09: never write paid-call artifacts into a disposable worktree.

```
python src/pilot/h963_c4_gate0_probe.py --account c1 --evidence-dir <shared checkout>/RussianTranslation/src/pilot/output
run_id  h963-c1-single-profile-gate0/2026-09-15T01:35:11Z-pid10700   policy production_v4 (240 000 ms)
warmup   26 208 ms  success  cli_safe_mode_effective: true   (api 25 502 ms)
measured 38 468 ms  success  cli_safe_mode_effective: true   (api 37 660 ms)
GATE-0 VERDICT: PASS
host: 2914 MB free of 16229 MB · commit 81.9 %
```

| reading on `c1` | warm-up | measured | answer |
|---|---|---|---|
| 11-09 05:32Z, no safe mode | 182 372 ms | 73 075 ms | ok |
| 11-09 18:08Z, no safe mode | 113 531 ms | — (STOP) | **`{"ok": false}`**, 7 312 thinking tokens |
| **15-09 01:35Z, safe mode (this PR)** | **26 208 ms** | **38 468 ms** | ok |

**How far this reading goes:** it proves the fixed probe runs live and passes on the lane's own surface. It shows the probe is 4–7× faster than both 11-09 readings, at the same host commit charge (~81–82 %). It is **n = 1**. The pre-fix refusal was intermittent (05:32Z passed and 18:08Z refused on the same day), so one PASS does not prove the refusal rate is zero. The next real `--execute` window re-tests it at no extra cost, because `probe_fleet` runs this same `_probe_call`. **Spend:** 2 probe calls. The ledger records `cost_evaluable: false` (Max route), so the cost is not evaluable, not $0. The day's first `c1` ration attempt was used at 01:35Z, so the next attempt is due at ≥ 07:36Z.

## 5. Remaining rungs (unchanged order)

1. A human merges this PR. SanskritLexicography is PR-only for unattended workers.
2. Fresh `dq_canary_puregloss` GO receipt (≤ 6 h; the lane is untouched by this PR).
3. Re-run the prepared `h4527acc05` through `bounded_staged_run --execute --cohort-path --cohort-width 1 --only-profile c1 --max-calls 2`, ≥ 6 h after the reading in §4 (ration spacing).
4. Audit → compare against the serial route → acceptance packet → `COHORT_LIVE_ACCEPTANCE.json` with `serial_acceptance.via_cohort_path: true`.
5. Work item 2 (Codex sign-off) and the money-class `## Verifier` PASS: a different session each. Work item 3 (width 2) stays **parked** by MG's 11-09 ruling (no funded second profile).

_Гасунс_
