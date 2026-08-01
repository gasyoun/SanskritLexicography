# H2118 — Probe latency ceiling: provenance repaired, re-derivation still blocked

_Created: 01-08-2026 · Last updated: 01-08-2026_

**Executor:** Opus 5 (`claude-opus-5[1m]`), Claude Code, isolated worktree off
`origin/master` [`625fe858`](https://github.com/gasyoun/SanskritLexicography/commit/625fe858).
Handoff: [H2118](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2118-Opus_RussianTranslation_rederive-probe-latency-ceiling-946_01.08.26.md).
Issue: [#946](https://github.com/gasyoun/SanskritLexicography/issues/946).

## Verdict — split, and stated as such

| Half of the mission | Outcome |
|---|---|
| **Re-derive `PROBE_LATENCY_CEILING_MS` from clean readings** (steps 1–3) | 🔴 **INSUFFICIENT CLEAN DATA, STILL BLOCKED** — no paid call was made, no ceiling is proposed |
| **Reconcile the two `production_v1` gates** (steps 4–5) | ✅ **SHIPPED** — three hard-coded copies collapsed to one table; the policy token carries its own ceiling again |

**Zero paid calls were made.** `PROBE_LATENCY_CEILING_MS` is numerically unchanged at
**65 000 ms**. The handoff's acceptance explicitly admits this split: *"'Insufficient clean
data, still blocked' is a legitimate outcome — report it as such rather than dressing up a
number."* This report does that, and takes the naming half — which needs no measurement — to
completion instead.

## Why no ceiling was derived

The measurement method is [FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)'s:
a rate-limited CLI **hangs instead of reporting 429**, so a reading is only trustworthy when
paired with a **same-moment quota check** issued outside the CLI (the profile's OAuth token used
as a request header only, never printed, logged or written).

**That quota check could not be issued: the harness auto-mode classifier denied the credential
read.** A human was asked and chose the zero-spend path rather than grant access or take unpaired
readings. Without the pairing, every reading would be exactly the contaminated kind H2118 exists
to end — so none was taken.

### The evidence gap is worse than "no readings today"

**As of 01-08-2026 not one probe row anywhere in the tree carries `duration_api_ms`.** The
H2095 instrumentation that this mission was built to consume has never produced a single row.
All 13 c4 rows in `src/pilot/output/h963_c4_gate0_probe_events.jsonl` (gitignored evidence)
predate it:

| # | timestamp (UTC) | purpose | `elapsed_ms` | classification | `duration_api_ms` |
|---|---|---|---|---|---|
| 1 | 2026-07-22T14:57 | warmup | 21 280 | content | — |
| 2 | 2026-07-22T20:03 | warmup | 59 831 | success | — |
| 3 | 2026-07-22T20:04 | measured | 102 874 | auth | — |
| 4 | 2026-07-23T06:06 | warmup | 40 003 | success | — |
| 5 | 2026-07-23T06:09 | measured | 168 352 | success | — |
| 6 | 2026-07-24T04:23 | warmup | 10 838 | **rate_limit** | — |
| 7 | 2026-07-24T07:35 | warmup | 9 949 | **rate_limit** | — |
| 8 | 2026-07-25T03:16 | warmup | 17 587 | auth | — |
| 9 | 2026-07-25T03:18 | warmup | 10 918 | auth | — |
| 10 | 2026-07-25T16:02 | warmup | 17 878 | **rate_limit** | — |
| 11 | 2026-07-25T18:18 | warmup | 19 903 | **rate_limit** | — |
| 12 | 2026-07-31T18:59 | warmup | 94 606 | success | — |
| 13 | 2026-07-31T19:01 | measured | 78 415 | success | — |

Two measured facts worth keeping, neither of which authorises a new number:

- **Three of the five `success` readings exceed the ceiling they were used to justify.**
  Successes are 40 003 · 59 831 · 78 415 · 94 606 · 168 352 ms; **65 000 clears only two of
  five.** The four readings cited in the constant's own comment (52 815 · 104 870 · 31 623 ·
  47 953) are recorded in the H963/H994/H1447 gate reports, not in this log — so the two
  populations barely overlap, and neither is decomposable into route time vs backoff.
- **The probe *can* classify a rate limit** — rows 6, 7, 10, 11 do, at 9.9–19.9 s. §270's
  failure mode is specifically the CLI **hanging** on a 429, not a total inability to see one.
  A reading is therefore not self-certifying: a 78 415 ms `success` and a 19 903 ms
  `rate_limit` are the same account minutes apart.

## What was actually wrong — three copies, not two

The handoff describes two gates. There were **three** independent hard-coded copies of the
ceiling, and the third had been kept in step by a comment rather than by code:

| Site | Value before | Consumer |
|---|---|---|
| [`probe_log.POLICIES['production_v1']`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py) | 30 000 | `verdict_for()` — the record-integrity gate, which **refuses** to log a GO its own telemetry contradicts |
| [`max_account_orchestrator.PROBE_LATENCY_CEILING_MS`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py) | 65 000 | `live_probe` — the dispatch gate; over it, the account is parked |
| [`coordinator.PROBE_LATENCY_CEILING_MS`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) | 65 000 | probe-receipt validation |

A 50 000 ms reading **passed** `live_probe` and **failed** `verdict_for()` — while both stamped
the row `production_v1`.

## The ruling — one name per ceiling value, and one table

The judgment step 4 asks for is *"one number, or genuinely different gates needing different
policy names."* **Neither, exactly: they are one gate in two eras, and the defect is that the
name was re-pointed instead of bumped.**

The ceiling moved 30 000 → 33 000 → 65 000 in a single day while the token stayed
`production_v1`. That is not two policies — it is one policy whose meaning silently changed
three times, which is precisely why a `policy` token stopped being sufficient provenance. So:

1. **`probe_log.POLICIES` is the single source of truth.** Nothing hard-codes a probe ceiling
   anywhere else. `max_account_orchestrator` and `coordinator` now **derive** via a new
   `probe_log.ceiling_for()`; `h963_c4_gate0_probe` already derived from the orchestrator.
2. **`production_v1` is frozen at 30 000** — not "the old wrong one". Every row stamped with it
   before 31-07-2026 was genuinely judged at 30 000; moving the number would retroactively
   falsify those rows.
3. **`production_v2` = 65 000** is added and is what the live gates now stamp. The two gates
   agree **by construction**, so the 2.2× disagreement cannot recur.
4. **The 65 000 value itself is carried forward, not re-confirmed** — and both constants now say
   so in-code, naming §270. Whoever lands clean readings adds `production_v3`; the instruction
   *"do NOT edit this value"* is written at the table.

The old objection to collapsing the copies — *"coordinator must not take an import dependency on
the orchestrator"* — is satisfied: `coordinator` imports `probe_log`, a stdlib-only leaf module,
not the orchestrator.

### One deliberate behavioural consequence

`coordinator` validates that a probe receipt's `policy` equals its own. Receipts stamped
`production_v1` are now **rejected**. This is correct fail-closed behaviour — a receipt judged
at 30 000 must not authorise dispatch at 65 000 — and receipts expire after 6 h regardless
(`PROBE_RECEIPT_MAX_AGE_SECONDS`), so no live receipt is affected in practice.

### The selftest pin

`max_account_orchestrator_selftest` carried a deliberate pin asserting the two ceilings
**disagree**, designed to fire the moment they were reconciled. It has done its job and is
replaced — not deleted — by pins on the invariant that now matters: both gates derive from the
table, the tokens match, `production_v1` stays 30 000, and **no two policy names share a ceiling
value** (which would re-open #946 by another route).

## Gates run

| Gate | Result |
|---|---|
| `python src/pilot/window_selftest.py` | **198/198, 0 failed** |
| `python src/pilot/max_account_orchestrator_selftest.py` | **PASS** |
| `python src/pilot/execution_contract_selftest.py` | **PASS** (its 29 999 → GO / 30 000 → NO-GO pins ride the unchanged default policy) |

**LANG_PARITY:** 6 entries across 5 files re-derived, **SHARED stands**. Grounds re-checked
mechanically rather than asserted — every added line was grepped for a language-keyed token
(`lang` / `russian` / `english` / `--lang` / `FIELD[` / `CARD_FIELD`) and **none** appears. This
is language-agnostic dispatch infrastructure; it cannot reach the RU/EN split.

## Still owed

- **The re-derivation itself.** Residual handoff
  [H2138](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2138-Opus_RussianTranslation_probe-ceiling-paired-readings-946_01.08.26.md):
  ≥5 paired readings, then `production_v3`. It needs the credential-read permission granted **and**
  c4 not rate-limited.
- **#946 is re-scoped, not closed** — its provenance half is done, its measurement half is not.

_Dr. Mārcis Gasūns_
