# H2652 — V4-Pro Q3 rematch report

_Created: 13-08-2026 · Last updated: 13-08-2026_

**Verdict: FAIL** (transport, not translation quality). Pre-declared floor was `det_gate_clean ≥ 15/22`. Measured: **1/22** clean, **4** `worker-null-death` on `IncompleteRead`/`TimeoutError`, **17** not attempted (run stopped). `would_promote` never true. **No TM / store write.**

Rule: [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2652_v4pro_rematch/VERDICT_RULE.md). Spend: [SPEND_AUTH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2652_v4pro_rematch/SPEND_AUTH.md).

## Schedule ruling this sitting also locked

After **16-08-2026 16:00 UTC** PWG DeepSeek pays **off-peak only** (or waits). Peak is never paid. Windows: 01:00–04:00 and 06:00–10:00 UTC = **03:00–06:00 and 08:00–12:00 CEST**. Versus today’s flat card the hike is about **+50 % to ~+1100 %** by model and token type (the +1100 % cell is Pro cache-hit: $0.003625 → $0.044 peak). Off-peak is half of the *new* peak and still above today. Enforced by `refuse_if_peak` in [`deepseek_arm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/deepseek_arm.py).

## What ran

| Ticket | Keys | Result |
|---|---|---|
| 1 probe | `yaTepsita` / `ya_tepsita` | **PASS capability.** Served `deepseek-v4-pro`, effort `high`, `det_issues=[]`, `pending-controller` (complexity flag). $0.0089. 9410 reasoning / 10164 completion tokens. Attempt 1 was `IncompleteRead`; attempt 2 succeeded in 187 s. |
| 2 main Q3 | 21 remaining | **Stopped after 4/21.** All four: 3/3 attempts `IncompleteRead(1–2 bytes)` or `TimeoutError` at 900 s. urllib `urlopen` cannot hold a 10+ minute thinking stream. |
| 3 max sub-arm | 3 S2×Q4 | **Not started** — high already times out. |

Control (H1210 arm B Q3 shippable 15/22) is not comparable: this sitting never reached a full 22-card free-gate sample.

## Cost honesty

Ticket 1: **$0.0089** on the Pro table (0.435 / 0.003625 / 0.87). Ticket 2 deaths returned 1–2 bytes; whether the provider billed thinking on those sockets is **unknown** (`cost_evaluable: false` for ticket 2). Do not treat a missing usage block as $0.

## Residual (not this sitting)

A streaming HTTP client (or the official SDK) must replace `urllib.request.urlopen` before another Pro `high` rematch. Requalifying after that change is a **new** sitting with its own N. Do not rerun this urllib arm.

_Dr. Mārcis Gasūns_
