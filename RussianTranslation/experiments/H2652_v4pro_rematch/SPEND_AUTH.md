# H2652 spend authorisation (this sitting + standing PWG)

_Created: 13-08-2026 · Last updated: 13-08-2026_

## This sitting (H2652)

Human ruling, 13-08-2026, this chat: spend authorised **now** for PWG DeepSeek work.

**N for this sitting (declared before token 1):**

| Ticket | Cards | Effort | Cap on generation HTTP calls (incl. gate retries) |
|---|---:|---|---:|
| 1 capability probe | 1 (smallest Q3 key) | high | 3 |
| 2 main rematch | 21 remaining Q3 | high | 63 (21 × 3) |
| 3 optional max sub-arm | 3 smallest S2×Q4 | max | 9 |
| **Sitting total** | **25** | | **80** |

Stop at the cap. Ticket 2 runs only if ticket 1 returns parseable JSON and `served_model` matches. Ticket 3 only if ticket 2 finishes under the cap.

Promote-DRY. No TM write. Default model stays `deepseek-v4-flash`.

## Standing (upcoming PWG work)

Same ruling: DeepSeek first-party (`deepseek-v4-flash` and `deepseek-v4-pro`) spend is authorised **for PWG→RU pipeline work without re-asking**, including prep, bounded rematches, and draft generation.

Still forbidden without a new explicit ruling:

- writing the TM / canonical store from a DeepSeek arm
- unattended auto-promote
- changing `DEFAULT_MODEL` to Pro
- dumping Q4 / monster heads unattended
- retargeting unpaid E1 (H2488) onto Pro
- non-PWG surfaces (papers, @DECIDE, Systema student copy)

A future sitting still **declares its N in the run folder** before the first call. The standing grant removes the permission question, not the reservation count.

_Dr. Mārcis Gasūns_
