# H2138 — the probe ceiling, re-derived: one number could never have worked

_Created: 03-08-2026 · Last updated: 03-08-2026_

**Model:** Opus 5 1M (`claude-opus-5[1m]`), executing
[H2138](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2138-Opus_RussianTranslation_probe-ceiling-paired-readings-946_01.08.26.md)
(residual of [H2118](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2118-Opus_RussianTranslation_rederive-probe-latency-ceiling-946_01.08.26.md),
closing the measurement half of [#946](https://github.com/gasyoun/SanskritLexicography/issues/946)).

**ZERO paid calls. Nothing spent.** Every reading used here was already bought by H2011 /
H2152 / H2158 / H2174. Reproduce the whole derivation offline with
[`h2138_ceiling_derive.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2138_ceiling_derive.py).

---

## 1. Verdict

| | |
|---|---|
| **Landed** | `probe_log.POLICIES['production_v3']` — `latency_ceil_ms` **80 000**, `api_ceil_ms` **45 000**; `CURRENT_POLICY` points at it |
| **Derived from** | the 8-reading measured c4 series (5 of them decomposable), not from a ruling |
| **Headline** | **the ceiling was never the bug — the single-number *shape* was.** Wall time is two independent quantities summed, and a threshold on the sum cannot express the thing the gate is for |

`production_v1` (30 000) and `production_v2` (65 000) are untouched and stay frozen: rows
stamped with them were genuinely judged at those ceilings.

## 2. Why one number could not work

    wall elapsed_ms  =  duration_api_ms  +  api_gap_ms
                        (route health)     (in-CLI scaffolding)

The two move independently — measured api/wall ratio **0.25 … 0.72** (median 0.55), so **no
fixed factor converts one into the other** (H2174). Two readings make the failure concrete:

- **02-08 12:46** — `duration_api_ms` **16 445 ms**, the *fastest API reading ever recorded on
  c4*, wall 66 291 ms. **NO-GO at 65 000.** A perfectly healthy route was refused a window on
  49 846 ms of scaffolding.
- **02-08 11:06** — `duration_api_ms` **69 137 ms**, a genuinely degraded route. A wall-only
  gate cannot tell this apart from the row above except by accident of where the scaffolding
  landed.

At 65 000 the gate passed **2/8**, with its median reading ~12 s *above* the ceiling — a ~25 %
lottery at ~$1.09 a pull. That is not a gate; it is a toll.

## 3. The evidence base

All 8 measured c4 readings in the append-only series
([`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md)):

| date (UTC) | wall `elapsed_ms` | `duration_api_ms` | `api_gap_ms` | v2 | **v3** |
|---|---:|---:|---:|---|---|
| 2026-07-22 20:04 | 102 874 | — | — | NO-GO | NO-GO |
| 2026-07-23 06:09 | 168 352 | — | — | NO-GO | NO-GO |
| 2026-07-31 19:01 | 78 415 | — | — | NO-GO | **GO** |
| 2026-08-01 20:21 | 50 336 | 27 557 | 22 779 | GO | GO |
| 2026-08-02 05:48 | 43 815 | 26 386 | 17 429 | GO | GO |
| 2026-08-02 07:49 | 75 561 | 29 069 | 46 492 | NO-GO | **GO** |
| 2026-08-02 11:06 | 96 520 | 69 137 | 27 383 | NO-GO | NO-GO |
| 2026-08-02 12:46 | 66 291 | 16 445 | 49 846 | NO-GO | **GO** |

| statistic | wall | `duration_api_ms` | `api_gap_ms` |
|---|---:|---:|---:|
| n | 8 | 5 | 5 |
| min | 43 815 | 16 445 | 17 429 |
| median | 76 988 | 27 557 | 27 383 |
| max | 168 352 | 69 137 | 49 846 |

## 4. The derivation

Both rules are mechanical and live in the script, not in prose.

**ROUTE ceiling — `api_ceil_ms` = 45 000.** The API readings separate at their largest
*multiplicative* gap (scale-free, unlike an additive cut): healthy cluster
`16 445 · 26 386 · 27 557 · 29 069`, degraded `69 137` — a 2.38× step. Ceiling = cluster max
× 1.5, rounded up. Admits 4/5.

**WALL ceiling — `latency_ceil_ms` = 80 000.** The worst *legitimate* call is a healthy route
carrying the largest scaffolding tax ever observed: 29 069 + 49 846 = 78 915 → **80 000**.
Admits 5/8 (62 %). Derived from components, not fitted to make any particular run pass.

**This is not a weakened guard.** Every reading `production_v2` rejected for genuine route
degradation is still rejected. What v3 stops rejecting is the healthy-route / slow-scaffolding
class that a wall number is structurally unable to identify. And v3 adds a fail condition that
v2 did not have at all.

## 5. Honest limits — read these before trusting the number

1. **No same-moment quota check was taken.** H2138 asked for one per reading. The probe it
   specified was *invalidated by its own correction* (commit
   [`fe054f2c`](https://github.com/gasyoun/Uprava/commit/fe054f2c364867eb1f4aa5afdb809d73642278a4),
   02-08 08:37): a Claude Code OAuth token returns `429` **unconditionally** without the
   identifying system prompt, so that probe reports "rate-limited" always. Reading the token to
   run the *corrected* probe was refused by the harness permission classifier — the third
   session in a row (H2118, H2152, this one). What stands in its place is weaker but real:
   every reading above **returned a full envelope with real usage**, and the
   [§270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) throttle signature is a
   silent hang with *no* return. None of these readings is a hang.
2. **The ROUTE guard changes no historical verdict.** The one degraded-route reading (69 137)
   also breached the wall ceiling, so the new condition is a **forward** guard for a class the
   series proves exists but has not yet been seen in isolation. It is pinned by four selftest
   cases so it cannot rot before it first fires.
3. **n = 5 decomposable readings**, all from a 3-day window on one account. The wall ceiling
   leans on a single `max_gap` observation (49 846). More readings should move it.
4. **A GO still certifies only the instant it was taken.** c4 is bimodal on a timescale of
   hours (H2174); no ceiling value fixes that, and this one does not claim to.

## 6. What this does NOT fix — and the number that matters more

A health-gate ceiling predicts nothing about whether a *production card* completes. The only
decomposed real card measured to date ([H2158](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2158/ROUTE_AB_MESSAGES_API_VS_CLI_HEADLESS_02-08-2026.md))
ran **359 212 ms wall with 356 727 ms of it inside the API** — a 0.7 % scaffolding share, the
mirror image of the health-call profile, and **2× over `HARD_TIMEOUT_MS = 180 000`**. So:

- the gate population (43–168 s) and the production population (~359 s) are **disjoint**;
- on real work the wall ceiling is *almost pure route time*, so "the wall measures the machine,
  not the route" — H2138's own step-3 hypothesis — **is false for production cards**, however
  true it is for trivial pings;
- the binding constraint remains **output tokens** (64 % of a card's cost, H2158 §6.1), not any
  ceiling.

Landing v3 makes the gate honest. It does not open a window, and it must not be read as
evidence that the lane can finish one.

## 7. Changed

| file | change |
|---|---|
| [`probe_log.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py) | `production_v3` (+`api_ceil_ms` on every policy); `CURRENT_POLICY` → v3; `verdict_for(..., api_ms=)` second condition |
| [`h963_c4_gate0_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py) | `API_CEILING_MS` derived from the policy table; `derive_fails` applies it; 4 new selftest pins; removed a hard-coded `65000` that H2138 would otherwise have silently staled |
| [`h2138_ceiling_derive.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2138_ceiling_derive.py) | new — the derivation, reproducible offline |
| [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) | 2 entries re-verified SHARED (route health is language-agnostic) |

**Gates:** `window_selftest` **200/200** · `max_account_orchestrator_selftest` **PASS** ·
`execution_contract_selftest` **PASS**. (The 198/198 baseline H2138 quotes was against a
200-test suite with a pre-existing LANG_PARITY drift, which this pass also cleared.)

## 8. Open for a human

**The wall ceiling moved 65 000 → 80 000, and that is a raise.** It is derived rather than
ruled, and it is paired with a new tighter route guard, but a human should decide whether the
derivation's premise is acceptable: *a call whose route is healthy should not be refused for
scaffolding the production path pays anyway.* Rejecting that premise means keeping a gate that
fails 75 % of the time on healthy routes.

This does **not** reopen the clock (wall vs API) — settled, MG 02-08-2026, H2160 option A.

---

_Dr. Mārcis Gasūns_
