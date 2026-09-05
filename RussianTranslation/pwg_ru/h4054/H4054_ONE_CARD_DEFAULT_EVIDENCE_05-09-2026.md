# H4054 — one-card production default: before/after evidence

_Created: 05-09-2026 · Last updated: 05-09-2026_

**Executor:** OxAlpha lane — GLM 5.3 Flash (`glm-5.3-flash`) resolved via opencode
(`zai-coding-plan/glm-5.3-flash`). Handoff: `Uprava/handoffs/H4054-OxAlpha_SanskritLexicography_pwg-one-card-operating-contract_04.09.26.md`.
**Zero provider calls** — every check below is offline/hermetic; no store, TM, or csl-orig byte was touched.

## The verified disagreement (audit §3.3) and its resolution

| Surface | Before | After |
|---|---|---|
| [gen_opt_harness2.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) `OUTPUT_BUDGET` | `90` (batched packing; the ruled one-card shape existed only in whoever typed `--output-budget=1`) | `1` — a **no-flag** production preparation emits one original card per translate call (`meta.batches` = one key each); presplit/heal routing unchanged (floor- and sense-trigger driven, H2160/H823) |
| Multi-card batching | implicit default | **explicit experiment lane only**: `--output-budget=90` (2026-07-03 calibrated packing); legacy byte mode via `--budget=N` / `--output-budget=off` unchanged |
| [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) | "Default: the batched + masked v2 harness … output-budget 90" beside the H2152 one-card ruling | default = one card per call; batching labelled explicit experiment; −72 % gam figure re-labelled as batched-era history; concurrency note updated to one-call-per-card arithmetic |
| [RussianTranslation/AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/AGENTS.md) | one-card policy text + a loop command with no shape note + "**is the supported in-chat Workflow route**" (stale since H1110) | structural-default note; Workflow claim replaced with the headless manifest-v2 route (forensics only) |
| [pwg-drain.md](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-drain.md) | "health PASS = latency `< 30 s`" (stale across production_v2 AND production_v3) + "harness default is still 90" | health PASS derived from `probe_log.POLICIES[probe_log.CURRENT_POLICY]` (production_v3: wall 80 000 ms AND route 45 000 ms, read off the probe's own ceiling line — never restated in prose); call-shape note rewritten for the structural default |
| [pwg-bounded-run.md](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md) | "Call shape stays ONE card per call (`--output-budget=1`)" | same ruling + structural-default provenance; a batched arriving manifest is a shape deviation, not the lane default |
| Timeout agreement | (already consistent) | `--timeout 600` / `PRODUCTION_HARD_TIMEOUT_MS = 600 000` — canary builder prints it from code; skills say "read the constant"; no change needed |
| [canary_manifest_build.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/canary_manifest_build.py) | no shape pin (golden carried whatever the default was) | pins `--output-budget=1` (the one-key canary is one card per call under any default) |
| Golden canary manifest | `meta.output_budget: 90` | `1` (surgical field edit only — `config_dir_fingerprint` and `tm_available` are box-bound mint-time state and were NOT regenerated from this Mac) |

Skills inspected, all seven: `pwg-bounded-run`, `pwg-de-editorial`, `pwg-drain`, `pwg-live-gate`, `pwg-review-packet`, `pwg-slice`, `pwg-window-close`. Changed: pwg-drain (health + call shape + Phase-1 step 2), pwg-bounded-run (call-shape line + date). pwg-live-gate / pwg-window-close already derive thresholds from code; pwg-review-packet / pwg-de-editorial carry no call-shape content; pwg-slice is a stub alias of pwg-drain.

## Twins and cross-box synchronization

- **Synced (this box):** `~/.claude/commands/pwg-drain.md` + `pwg-bounded-run.md` re-copied from the canonical claude-config sources; verified the twins carried no other local drift (diff vs canonical HEAD = exactly the H4054 edits).
- **Pushed (canonical):** claude-config `commands/` changes land on GitHub; the **Windows box** must `git pull` claude-config and re-copy its `~/.claude/commands/` twins — **inaccessible from this Mac, listed as a residual** with a GTD row. Its local store/TM are box-private by design (H805), so its canary golden selftest keeps comparing against its own sidecar state; the golden edit here touches only the shape field, so the guarded diff stays green on both boxes.

## Positive controls (hermetic, all in `window_selftest.py`, isolation-guard armed)

1. `test_default_call_shape_is_one_card_per_call` (new): fresh-import `OUTPUT_BUDGET == 1` (subprocess, monkeypatch-proof); 3-key synthetic nominal build → `batches == [[k1], [k2], [k3]]`, `batch_count == 3`, `meta.output_budget == 1`, no presplit; explicit `OUTPUT_BUDGET = 90` → all three small cards pack into ONE batch, every card still owed.
2. `test_large_card_presplit_and_heal_under_one_card_default` (new): 45-`<ls>` giant → presplit lane under the default (cite floor 40, per-card), ≥3 fragment groups, each ≤ `PRESPLIT_GROUP_SENSE_CAP=18`; 3-`<ls>` companion stays a whole-card one-card batch; `selfheal_group_budget == 12` unchanged.
3. `test_h2245_canary_manifest_builder` (existing): guarded golden diff PASS with the pinned builder + refreshed golden.

## Negative control

- `test_presplit_cite_floor_and_single_ceil` (existing, H823): dropping the floor reproduces the tiny-card heal-lane misfire under budget 1 — proves the floor still guards the new default. PASS.
- Explicitness control: no test can reach a batched manifest without an explicit `--output-budget=N`/`--budget=N`; `parse_args` byte-mode compatibility (`--budget` without `--output-budget`) unchanged.

## Command outputs (Mac worktree `h4054-drain`, base `096e57ea`)

| Check | Before (master 096e57ea) | After (this branch) |
|---|---|---|
| `python3 pilot/window_selftest.py` | `ran 219/219 defined -- 219 passed, 0 failed` (EXIT 0) | `ran 221/221 defined -- 221 passed, 0 failed` (EXIT 0) |
| `python3 pilot/lang_parity_check.py` | `105 entries, all verdicts complete, no drift` | same, after re-verifying the 56 drifted entries (hash-only; `output_budget_90` mechanism text updated, SHARED re-derived: zero language-keyed tokens in the diff) |
| `python3 -m py_compile` (3 changed .py) | — | OK |
| Provider calls | 0 | 0 |

H4054 note on the parity ledger entry id: `output_budget_90` keeps its id (ledger identity), mechanism text now reads "90 calibrated 2026-07-03; 1 = one card per call since H4054, 04-09-2026".

## Residuals

1. **Windows-box twin pull + canary re-verify** (inaccessible synchronization) — GTD row minted.
2. Historical dated docs (PIPELINE_HISTORY.md, KNOB_CALIBRATION_2026-07-03.md, h963 packets, README tables) still narrate the 90-era default — deliberately untouched as dated history; operating surfaces are the runbook, AGENTS.md, and the skills, all updated.
3. Preflight cost estimates (`perf_preflight.py`) now mirror the one-card shape (more, smaller predicted calls) — honest accounting; the H189 cost gate may defer big roots that batched arithmetic used to admit. No code change made or needed.

_Dr. Mārcis Gasūns_
