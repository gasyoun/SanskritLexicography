_Created: 24-09-2026 · Last updated: 24-09-2026_

# H5403: the cards/hour figure is now derived by a tool, and `c1` is ready — the paid wave itself is not launched

**Handoff:** [H5403](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5403-Opus_SanskritLexicography_pwg-ru-c1-volume-waves-cards-per-hour_24.09.26.md)
**Executor:** Claude Code, Opus 5 (`claude-opus-5[1m]`), unattended drain worker 3 on `Claude/c1`, MSI box
**Paid calls this pass: 0.** No human was present to authorise a paid launch, and this handoff's own
guardrail («every paid launch has needed an explicit human yes … ask with cost stated») is a money-class
fence, not a confirmation ask an unattended worker may waive.

## What this pass settled

1. **The cards/hour figure H4342 (b) asked for is computed, not estimated** — and by a committed tool,
   [`RussianTranslation/src/pilot/cards_per_hour.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cards_per_hour.py),
   so every later wave reports it the same way instead of by hand.
2. **`c1` is launch-ready right now** on all three preconditions a paid window has to clear
   (route, ration, plan pipeline) — each probed live today, receipts below.
3. **What actually stops a new wave** is not readiness: it is the planner's wall-clock plus the missing
   human «yes». Both are named precisely so the next pass starts where this one stopped.

## The first honest cards/hour figure (baseline run `h4527-vol-220922`)

Derived from the two committed artifacts of that window
([`volume.report.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/volume.report.json),
[`volume.events.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/volume.events.jsonl)),
saved here as
[`cards_per_hour.h4527-vol-220922.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5403/cards_per_hour.h4527-vol-220922.json):

| Measure | Value |
|---|---|
| Cards promoted | 4 (of 5 leases attempted; `kast_ur_i~~h0_zz_pw` left in the requeue backlog) |
| Sense rows promoted | 10 (store 11 524 → 11 534) |
| Window wall-clock | 258.4 s (11:45:44.299Z → 11:50:02.675Z), probe legs included |
| Dispatch-only span | 238.3 s (first `attempt_start` → last `attempt_end`) |
| **Cards/hour, wall-clock** | **55.7** |
| Cards/hour, dispatch-only | 60.4 |
| **Cards per paid call** | **0.57** (7 paid calls: 2 probe legs + 5 card calls) |

Three deliberate choices in the tool, because a rate is only honest if its denominator is:

1. **"Cards" = cards promoted into the store**, never leases attempted. The defect card cost a paid call
   and produced no store row; counting it would flatter the lane by 25 % on this very run.
2. **Wall-clock includes the two readiness-probe legs**, because they are what a ration slot actually
   spends. The dispatch-only figure is reported beside it, never instead of it.
3. **Per-paid-call is reported separately** from per-hour: the binding constraint on this lane is the
   probe ration (2 attempts per UTC day, 6 h apart), not the clock.

**Read the figure as a per-window rate, not a throughput forecast.** 55.7 cards/hour is the rate *inside*
a five-card window at width 1; the lane cannot sustain it, because each window needs its own canary call
and a legal ration slot. The honest planning number is closer to *cards per ration slot* — 4 promoted per
window, two windows per UTC day at best.

## Live probes today (all zero-call, 14:42–14:58Z)

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Route — is `c1` on Anthropic, not z.ai? | grep for `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` in `D:\ClaudeTools\profiles\claude1\.claude\settings.json` | **Anthropic**: neither key present; only `API_TIMEOUT_MS` from that family, which routes nothing. The 22-09 restore holds. |
| 2 | Ration — may `c1` probe now? | `max_account_orchestrator.py --db max_orchestrator.sqlite probe-ration --account c1` | exit 0, `attempts_today: []`, `legal_now: true` — **both 24-09 slots free** ([receipt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5403/probe_ration.c1.24-09-2026.json)) |
| 3 | Leases — is a volume wave staged? | `coordinator.py status` | **No.** All five `h4527vol*` leases are terminal (4 `promoted`, `h4527vol14` `requeue_prepared`). A new wave needs a fresh plan. |
| 4 | Plan — can the planner still stage one? | `no_pwg_scale_plan.py --window-size 1 --limit-windows 5 --require-senses 1 --headless --dry-run --profile-slot c1 --config-dir D:\ClaudeTools\profiles\claude1\.claude --prefix h5403vol` | **Yes, and slowly** — see below |

### Probe 4 in full: the planner works, at about three minutes per window

Auto start-index resolved to 35. In 900 s it walked `h5403vol35` … `h5403vol41` and prepared **three**
windows (`h5403vol35`, `h5403vol39`, `h5403vol40` — execution manifest `v2` + harness written under
`src\pilot\output\coordinator\artifacts\`), omitting three (`vol36`, `vol37`, `vol38`: «no unpromoted
subcard declares 1+ source sense(s)» — the `--require-senses 1` gate doing its job). It was **SIGTERMed
at the 900 s `timeout` I set**, mid-`meKalA` (`FAIL: command exited 143`), which is this session's ceiling,
not a planner defect.

Two facts for the next pass:

1. **Rate: ~3 minutes of planner wall-clock per queue head walked**, and roughly half the heads are
   omitted by the sense gate — so staging five eligible one-card leases costs **~25–30 minutes** before
   a single paid call. That is the real cost item this handoff's 180-minute estimate hides.
2. **`--dry-run` registers no leases.** The three prepared windows above exist as artifacts only; the
   coordinator still shows no `h5403vol*` lease. The launching pass must re-run the same command
   **without `--dry-run`** (same cost again), then plan-freeze, canary, dry run, window.

## Why no paid wave ran

Two independent reasons, either one sufficient:

1. **No human yes.** This is a `class: money` handoff whose recipe states that every paid launch so far
   has needed an explicit human authorisation, because `bounded_staged_run.py --execute` needs
   `--allow-unbounded` on this route (cost is not evaluable, and a `--cost-ceiling` fails closed after the
   first card). An unattended worker supplying its own authorisation for a spend is the shape
   [rules/agent-never-self-authorizes-an-escape.md](https://github.com/gasyoun/claude-config/blob/main/rules/agent-never-self-authorizes-an-escape.md)
   exists to refuse. Withheld deliberately, ration untouched — **both of `c1`'s 24-09 slots are still free.**
2. **Budget.** This worker's unit budget was ~45 minutes; the planner alone needs ~25–30 of them before
   the first paid call. A window started inside that budget would have been a window abandoned mid-flight.

Nothing in this pass touched the store, the ration ledger, the coordinator leases, or `c1`'s
`settings.json`.

## Delivery (five fields)

- **Changed:** new tool
  [`cards_per_hour.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cards_per_hour.py);
  new packet directory `RussianTranslation/pwg_ru/h5403/` with this report, the derived
  `cards_per_hour.h4527-vol-220922.json` and the `probe_ration.c1.24-09-2026.json` receipt.
- **Unchanged:** the `pwg_ru` store (11 534 rows), the probe-ration ledger (0 attempts on 24-09), every
  coordinator lease, `c1`'s `settings.json`, H5403's registry row (still open — DoD not met).
- **Checks:** `cards_per_hour.py` on the 22-09 artifacts → PASS (figures in the table above, reproducible
  from committed inputs); `probe-ration --account c1` → exit 0 / `legal_now: true`; route grep → Anthropic;
  planner dry run → exit 0 with three windows prepared, one SIGTERM at the session timeout.
- **Risks:** the ~3 min/window planner cost makes «plan + canary + window» a ≥45-minute unit, so a future
  unattended slot must be sized for it or the planning half must be pre-staged by an earlier pass; the
  55.7 cards/hour figure is per-window and will be misread as a lane forecast unless the ration caveat
  travels with it.
- **Inspect:** a verifier opens this report, then
  [`cards_per_hour.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cards_per_hour.py)
  and re-runs it against `pwg_ru/h4527/volume.report.json` + `volume.events.jsonl` — the figures must
  reproduce byte-for-byte from committed inputs, with no live call.

## What H5403 still owes

1. One paid `c1` volume wave (cohort path, width 1) with cards promoted and Anthropic ids in every
   transcript — the DoD line this pass did not meet.
2. The same `cards_per_hour.py` run against that wave's own artifacts, appended to this packet.
3. The money-class `## Verifier` PASS from a different session.

## Следующий шаг — человеку

**Что делать** — разрешить (или не разрешать) один платный прогон перевода на профиле `c1`. Это
пять карточек-словарных статей, которые модель переводит и кладёт в хранилище; оплата идёт
подпиской-квотой аккаунта, отдельного счёта не выставляется.

1. Ответьте в чате словами: «да, запускай волну H5403» — или «нет».
2. Если «да», исполняющая сессия сначала заново соберёт план (это ~25–30 минут без единого платного
   вызова), потом сделает канарейку и запустит окно на 7 платных вызовов.

**Если разрешите:** появится вторая точка замера — сегодняшние 55,7 карточек/час перестанут быть
единственным числом, и станет видно, устойчива ли эта скорость. В хранилище прибавится ~10 строк смыслов.
Сегодняшние два слота у `c1` свободны, так что запуск возможен в любой момент суток UTC.
**Если не разрешите:** ничего не ломается — инструмент и цифра уже в репозитории, H5403 остаётся открытым,
и волну можно запустить в любой другой день.
**Откат:** отдельного отката не нужно — карточки промоутятся только после чистого аудита, а дефектные
остаются в очереди на перезапуск.

_Гасунс_
