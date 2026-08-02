# Metadoc — AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026

_Created: 02-08-2026 · Last updated: 02-08-2026_

Companion record for [`AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2152/AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md).

## Purpose

Decide, in writing and on evidence, whether the PWG→RU paid lane should issue **one card per
call** or **batch several cards per call** — the question [FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
reopened against MG's 31-07-2026 instrument-everything mandate. Audit only; it authorises no
spend and moves no constant.

## Audience

A session picking up the pwg_ru paid lane, or anyone about to change `OUTPUT_BUDGET`,
`SELFHEAL_GROUP_BUDGET` or `HARD_TIMEOUT_MS`. Read §1 and §7 before touching any of the three.

## Provenance

- Handoff [H2152](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2152-Opus_RussianTranslation_c4-quota-call-shape-audit_02.08.26.md), minted by Grok 4.5 (`grok-4.5`), executed by **Opus 5 1M (`claude-opus-5[1m]`)**.
- Parent [H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md).
- One paid measurement of its own ($0.3456), mirrored to [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md); everything else reuses committed evidence.

## Limitations — read these before citing it

1. **The quota reading is n = 1 and same-moment only.** It says c4 was not throttled on
   02-08-2026. It says nothing about tomorrow, and the whole recommendation is *conditional on
   which ceiling binds*. Re-check before reusing the verdict.
2. **The 45.7 s `api_gap` is an upper bound**, not a startup measurement — the ping ran five
   turns. The 01-08 gate readings (~45 % of wall) are the comparable figure. Only the token
   counts are payload-independent.
3. **The authenticated outside-the-CLI 429 probe was never run** — credential-store read was
   refused by the harness permission classifier. §2 uses two substitutes.
4. **No option was executed.** The B/C rows are priced from committed measurements, not from a
   one-card-vs-batch A/B. There has never been such an A/B on this lane.
5. It supersedes nothing in H2011 by itself; the H2011 status block carries the cross-link.

## Improvement backlog (ranked)

1. Re-run §2 as a real A/B once `HARD_TIMEOUT_MS` is ruled on — the memo prices options, it does
   not measure them against each other.
2. Replace the n = 1 quota reading with the ≥5 paired readings [#946](https://github.com/gasyoun/SanskritLexicography/issues/946) / H2138 wants.
3. Fold in the per-call overhead figure once item 2 of §6 lands — the whole §4 table is a
   function of it, and every row moves when it changes.
4. Once [#949](https://github.com/gasyoun/SanskritLexicography/issues/949) is fixed, re-derive §4
   from real spend instead of the evaluable-calls-only floor.

## Revision history

| Date | Change | Model |
|---|---|---|
| 02-08-2026 | Created — full audit, HOLD one-card recommendation, 8 sections | Opus 5 1M (`claude-opus-5[1m]`) |
| 02-08-2026 | Folded in [PR #986](https://github.com/gasyoun/SanskritLexicography/pull/986) (landed concurrently): `subagent_tokens` is a legacy misnomer for the sum of the token fields, and the real per-call charge is **cache re-creation**. Recommendation unchanged; §6 item 2 gained a named mechanism and §2 an independent price reproduction (cache creation = **87.6 %** of the ping's cost, total reproduced to $0.3456 vs $0.3456318 recorded). | Opus 5 1M (`claude-opus-5[1m]`) |

---

_Dr. Mārcis Gasūns_
