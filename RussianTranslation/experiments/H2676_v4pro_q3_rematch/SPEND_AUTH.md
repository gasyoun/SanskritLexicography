# H2676 spend authorisation

_Created: 14-08-2026 · Last updated: 14-08-2026_

Handoff [H2676 (Grok 4.6) — W1 Pro Q3 rematch after streaming client](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2676-Grok_SanskritLexicography_deepseek-w1-pro-q3-rematch_13.08.26.md) is the written authorisation (PLAN D2). First-party DeepSeek, no USD cap, this sitting. Do not inherit H2488 or H2652 ticket counts.

**N declared before token 1:**

| Ticket | Cards | Effort | Cap on generation HTTP calls (incl. gate retries) |
|---|---:|---|---:|
| 1 main Q3 rematch | 22 frozen Q3 | high | 66 (22 × 3) |
| 2 optional max sub-arm | 3 smallest S2×Q4 | max | 9 |
| **Sitting total** | **25** | | **75** |

Ticket 2 only if ticket 1 holds transport (no IncompleteRead after 3 retries as the batch outcome). Stop at the cap. JSONL every call (arm journal + telemetry).

Promote-DRY. No TM / store write. `DEFAULT_MODEL` stays `deepseek-v4-flash`. `--model deepseek-v4-pro --reasoning-effort high --max-tokens 32768`.

After 16-08-2026 16:00 UTC: off-peak only (`refuse_if_peak`).

_Dr. Mārcis Gasūns_
