_Created: 24-09-2026 · Last updated: 24-09-2026_

# H5403, 24-09-2026 19:00–19:25Z: the `c1` volume wave is fully staged and its launch line is dry-run green — the `c1` probe ration is what refuses

**Handoff:** [H5403](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5403-Opus_SanskritLexicography_pwg-ru-c1-volume-waves-cards-per-hour_24.09.26.md)
**Executor:** Claude Code, Opus 5 (`claude-opus-5[1m]`), unattended drain worker 1, Mac session driving `msi` / `WIN-NJTORH3267V` over Tailscale SSH.
**Paid calls this pass: 0.** Nothing was overridden, nothing spent, no store row touched.
Predecessors in this packet: [H5403_C1_VOLUME_READINESS_GREEN_CARDS_PER_HOUR_DERIVED_24-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5403/H5403_C1_VOLUME_READINESS_GREEN_CARDS_PER_HOUR_DERIVED_24-09-2026.md) (the cards/hour tool) and §6 of [H5402_KASTURI_GATES_PASSED_STOPPED_ON_CALL_CAP_24-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5402/H5402_KASTURI_GATES_PASSED_STOPPED_ON_CALL_CAP_24-09-2026.md) (the ration finding).

## 1. What this pass settled — the expensive half is already paid for

The earlier H5403 report named the planner (~3 min per queue head, ~25–30 min per wave) as the
cost item that makes this handoff too big for a 45-minute unattended slot. **That half is now
done and verified as durable state on `msi`** — it does not have to be re-run at launch:

| # | Check | Live result (19:05–19:20Z) |
|---|---|---|
| 1 | Are the volume leases registered, not just artifacts? | **Yes, four `prepared` leases**: `h5403vol25` (`kunt_i~~h0_zz_pw`), `h5403vol35` (`ma_d_uka~~h0_zz_pw`), `h5403vol39` (`matsy_akz_i~~h0_zz_pw`), `h5403vol40` (`mayo_bu~~h0_zz_pw`) — all `nominal/no_pwg_windows100`, from `coordinator.py status` (21 leases total, default data-root; `--data-root output/coordinator` is the wrong root and reports 0) |
| 2 | Does a usable plan exist? | **Yes** — `output\h5403vol\plan.json`, 3 352 B, schema `pwg.no_pwg_scale_plan.rebuilt.v1`, 4 windows × 1 projected call |
| 3 | Do the staged manifests still match the plan's claims? | **All four match byte-for-byte** (live `Get-FileHash` vs plan `manifest_sha256`): `0892620cbcbb401f…`, `9444c9d5c9873ae0…`, `d2ac2663858f7e3a…`, `f12dc54df5099f49…` |
| 4 | Route — is `c1` on Anthropic, not z.ai? | **Anthropic.** `D:\ClaudeTools\profiles\claude1\.claude\settings.json` unchanged since 23-09 20:47:52Z; 0 lines matching `BASE_URL|z\.ai|glm`; `env` keys are only `PYTHONUTF8`, `PYTHONIOENCODING`, `DEEPPAPERNOTE_OBSIDIAN_VAULT`, `ENABLE_TOOL_SEARCH`, `SHUNT_MIN_LINES`, `API_TIMEOUT_MS`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`; no `ANTHROPIC*` in the User or Machine environment |
| 5 | Credentials | `.credentials.json` rewritten **2026-09-24T14:48:44Z** (the re-login of H5402 §6.1). Still **no 200 receipt** on `c1` since then — the first canary is also the auth proof |
| 6 | Canary manifest | Built at 0 calls, `output\h5403vgate24\` (15:32:54Z): `execution_manifest.canary.json` 24 052 B, `preflight.canary.json` 2 641 B, `run_pilot_wf.canary.js` 94 164 B. Never executed — no `status.canary.json`, no `calls*.json` |
| 7 | **Ration — may `c1` probe now?** | **NO.** `legal_now: false`, `attempts_today: ["2026-09-24T15:20:17Z"]`, `next_legal_utc: "2026-09-24T21:20:17Z"`, `max_per_utc_day: 2`, `min_gap_s: 21600`, fingerprint `9321e2c138f02c1d…518acd6b`; the subcommand exits **3** ([receipt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5403/probe_ration.c1.1911Z.24-09-2026.json)) |

## 2. The launch line is proven — zero-call dry run, exit 0

Run three times, 19:12–19:22Z, on `msi` from `RussianTranslation\src\pilot`, writing its
report/checkpoint/events into `%TEMP%\h5403dry\` so the guarded `msi` checkout stayed clean:

```text
python bounded_staged_run.py --plan output\h5403vol\plan.json --coord-dir output\coordinator --coordinator coordinator.py --cwd C:\Users\user\AppData\Local\Temp\pwg-bare-h5403vol --events C:\Users\user\AppData\Local\Temp\h5403dry\dry.events.jsonl --lease-id h5403vol25 --lease-id h5403vol35 --lease-id h5403vol39 --lease-id h5403vol40 --cohort-path --cohort-width 1 --only-profile c1 --max-calls 6 --run-id h5403-vol-240924-dry --checkpoint C:\Users\user\AppData\Local\Temp\h5403dry\dry.checkpoint.json --report C:\Users\user\AppData\Local\Temp\h5403dry\dry.report.json
```

Verdict `pwg.bounded_staged_run.v1`, `mode: "dry-run (no generation call made)"`, **exit 0**:

1. `expected_windows: 4`, `expected_headwords: 4`, `expected_subcards: 4`, `projected_calls_from_plan: 4`.
2. `importable_prepared_leases: ["h5403vol25","h5403vol35","h5403vol39","h5403vol40"]`, `windows_not_prepared_skipped: []` — nothing is missing or stale.
3. `live_admission: {admitted: true, reason: "serial route (width 1)"}` — width stays 1, the parked sibling's width 2 is not touched.
4. `account_allocation.allocated: ["c1"]`, ceiling `max_calls: 6`.
5. The `--cwd` folder was created before the run (the 23-09 `WinError 267` lesson).

The only differences between that proven line and the paid one are `--execute`,
`--allow-unbounded`, a fresh `--canary-receipt`, the real repo paths for
events/checkpoint/report, and a real `--run-id` — spelled out in §4.

## 3. Why no paid wave ran: one hard gate, one contended slot

1. **The ration is a hard gate, red until 2026-09-24T21:20:17Z** (row 7). That is 2 h 14 min
   after this pass started, against a ~45-minute unit budget — the wave could not have been
   started, let alone finished, inside it. `legal_now: false` is a gate, not a nuisance;
   [rules/agent-never-self-authorizes-an-escape.md](https://github.com/gasyoun/claude-config/blob/main/rules/agent-never-self-authorizes-an-escape.md) forbids ruling past it.
2. **Only ONE `c1` probe slot is left today, and two lanes want it.** H5402's own note claims
   it for the `kast_ur_i` repair (4 paid calls, 1 card); this handoff wants it for the volume
   wave (7 paid calls, up to 4 cards). Both cannot run before the ration resets at 00:00Z.
   That collision is a human's call — see §5.
3. **Spend authorization.** MG's 24-09 ruling in chat («yes, 4 and do not reask for such minor
   spends from now on») was given on H5402's 4-call `kast_ur_i` run. This wave is 7 calls, so
   the packet states the cost and asks rather than reading that ruling as wider than its words.

## 4. The paid run a human authorizes — 7 calls, ~5 minutes

Preconditions, in order, all on `msi` in `RussianTranslation\src\pilot`:

1. At or after **21:20:17Z**: `python max_account_orchestrator.py probe-ration --account c1` must exit **0** with `legal_now: true`.
2. Re-probe the route (it has silently flipped to z.ai twice, 20-09 and 22-09): 0 hits for `BASE_URL|z\.ai|glm` in `D:\ClaudeTools\profiles\claude1\.claude\settings.json`.
3. Fresh canary (1 paid call, ≤6 h old at window start) per [/pwg-live-gate](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) Step 2 on the already-built `output\h5403vgate24\` manifest, then `canary_gate.py judge` → GO. This canary is also the first 200 receipt on `c1` since the 14:48Z re-login; a 403 here reverts the blocker to auth and belongs to a human.
4. Then the window (2 probe legs + 4 card calls = 6):

```text
python bounded_staged_run.py --plan output\h5403vol\plan.json --coord-dir output\coordinator --coordinator coordinator.py --cwd C:\Users\user\AppData\Local\Temp\pwg-bare-h5403vol --events ..\..\pwg_ru\h5403\volume.events.jsonl --lease-id h5403vol25 --lease-id h5403vol35 --lease-id h5403vol39 --lease-id h5403vol40 --execute --cohort-path --cohort-width 1 --only-profile c1 --canary-receipt output\h5403vgate24\canary_receipt.json --max-calls 6 --allow-unbounded --call-reservation output\h5403vol\calls.vol.json --run-id h5403-vol-240924 --checkpoint ..\..\pwg_ru\h5403\volume.checkpoint.json --report ..\..\pwg_ru\h5403\volume.report.json
```

5. Then the rate, from the window's own artifacts, no live call:

```text
python cards_per_hour.py --report ..\..\pwg_ru\h5403\volume.report.json --events ..\..\pwg_ru\h5403\volume.events.jsonl
```

Expected shape if it goes like the 22-09 baseline: ~4 cards promoted, ~10 store rows
(11 534 → ~11 544), ~4–5 min of wall-clock, so **~50–60 cards/hour and ~0.57 cards per paid
call** — the second measurement point that turns one number into a trend. An exit 1 with a
non-empty requeue backlog is the H5209 contract, not a failure.

## 5. Delivery (five fields)

- **Changed:** this report; the 19:11Z ration receipt [probe_ration.c1.1911Z.24-09-2026.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5403/probe_ration.c1.1911Z.24-09-2026.json); the dry-run verdict [dry_run.h5403-vol-240924.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5403/dry_run.h5403-vol-240924.json); a `changelog_queue` fragment.
- **Unchanged:** the `pwg_ru` store (11 534 rows), the `c1` probe-ration ledger (still one attempt today, 15:20:17Z), all 21 coordinator leases including the four `prepared` H5403 ones and `h4527vol14` at `requeue_prepared`, `c1`'s `settings.json` and `.credentials.json`, every file under `pilot\output` (the dry run wrote only into `%TEMP%\h5403dry\`), H5403's registry row (**still open** — DoD not met), no code.
- **Checks:** `probe-ration --account c1` → exit **3**, `legal_now false` (gate RED, expected); `bounded_staged_run.py` dry run → exit **0**, 4/4 leases importable, admission `serial route (width 1)` (PASS); `Get-FileHash` on the four execution manifests → all match the plan's `manifest_sha256` (PASS); route grep → 0 hits, Anthropic (PASS); `coordinator.py status` → four `h5403vol*` leases `prepared` (PASS).
- **Risks:** the ration resets at 00:00Z but grants only 2 attempts/day, and H5402's `kast_ur_i` repair claims the same remaining slot — whichever lane runs first parks the other until tomorrow; `c1` has silently flipped to the z.ai route twice, so step 2 of §4 is mandatory even though it is green now; the first canary is still the only auth proof since the 14:48Z re-login, so a 403 there is a live possibility.
- **Inspect:** a verifier opens this report, then re-runs the §2 dry-run line on `msi` (zero calls) and `probe-ration --account c1`; the four `importable_prepared_leases` and the four sha256 values must reproduce exactly.

## 6. What H5403 still owes

1. One paid `c1` volume wave (cohort path, width 1) with cards promoted and `msg_011C…`/`req_011C…` Anthropic ids in every transcript — blocked only on the ration window and the 7-call authorization.
2. `cards_per_hour.py` against that wave's own artifacts, appended here.
3. The money-class `## Verifier` PASS from a different session.

## 7. Следующий шаг — человеку

**Что делать** — решить, кому отдать единственный оставшийся на сегодня платный слот профиля `c1`.
«Слот» здесь — это разрешённая попытка обращения к API: их всего две за сутки UTC, одна уже
израсходована в 15:20Z, вторая открывается **сегодня в 21:20:17Z по UTC (00:20 мск)** и закрывается
в полночь UTC. Два дела ждут одного слота:

1. **Волна перевода H5403** — 4 карточки-словарные статьи (`kunt_i`, `ma_d_uka`, `matsy_akz_i`,
   `mayo_bu`), 7 платных вызовов, ~5 минут работы. Всё уже подготовлено и проверено
   вхолостую сегодня: план, четыре брони, канарейка — осталось нажать. Даст вторую точку
   замера скорости (сегодняшние 55,7 карточек/час перестанут быть единственным числом).
2. **Починка карточки `kast_ur_i`** (это H5402) — 1 карточка, 4 платных вызова. Она висит
   недоделанной с 22-09.

Ответьте в чате словами — «H5403, волну» или «H5402, kast_ur_i» (или «обе, по очереди» —
в один слот обе не влезают, вторая уйдёт на 25-09).

**Если ответите:** исполняющая сессия в 21:20Z прогонит выбранное — проверку маршрута,
канарейку, потом окно; карточки попадут в хранилище, и появится строка «карточек в час».
**Если не ответите:** слот просто не будет использован, ничего не сломается — оба дела
подготовлены и ждут следующих суток; но платный слот, не потраченный сегодня, не переносится
на завтра (лимит 2 в сутки обнуляется, а не накапливается).
**Откат:** отката не требуется — карточки промоутятся только после чистого аудита, дефектные
остаются в очереди на перезапуск.

```text
Решение по единственному оставшемуся платному слоту c1 на 24-09 (открывается 21:20:17Z / 00:20 мск):

1. H5403, волна перевода — 4 карточки (kunt_i, ma_d_uka, matsy_akz_i, mayo_bu), 7 платных вызовов, ~5 минут. Всё подготовлено и проверено вхолостую. Даст вторую точку замера скорости.
2. H5402, починка kast_ur_i — 1 карточка, 4 платных вызова. Висит с 22-09.

Ответьте словами: «H5403, волну» или «H5402, kast_ur_i». В один слот обе не влезают.

Если ответите: в 21:20Z сессия прогонит проверку маршрута, канарейку и окно; карточки попадут в хранилище.
Если не ответите: ничего не сломается, оба дела ждут 25-09; но слот на сутки не накапливается.
Откат: не требуется, дефектные карточки остаются в очереди на перезапуск.
```

_Гасунс_
