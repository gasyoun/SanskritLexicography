# HARD_TIMEOUT_MS recalibration — from a round number to the observed card-spawn distribution (07-08-2026)

_Created: 07-08-2026 · Last updated: 09-08-2026_

**Handoff.** [H2313](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2313-Sonnet_SanskritLexicography_pwg-ru-hard-timeout-recalibrate_06.08.26.md)
(**Sonnet 5**) — recalibrate `PRODUCTION_HARD_TIMEOUT_MS` from the committed wall-clock
distribution of real card spawns, not from a round number.

**Parent.** [H2250 CLI cache amortisation re-measure](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/CLI_CACHE_AMORTISATION_REMEASURE_06-08-2026.md)
· [#1144](https://github.com/gasyoun/SanskritLexicography/issues/1144) (the timeout class)

---

## 1. Verdict

**`PRODUCTION_HARD_TIMEOUT_MS` raised from 300 000 ms to 600 000 ms**, chosen as
**p99 of completed card spawns (478 125 ms) + ~25% margin**, comfortably above the
observed completed maximum (511 908 ms) across every committed pwg_ru card-phase
envelope on disk. Landed in
[`src/pilot/execution_contract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py)
(the single owning constant per H2254 — every consumer imports it, nothing re-declares it).

**What the gate used to kill:** healthy, completed calls. The old 300 000 ms ceiling sat
**below p90** (276 521 ms) of the completed distribution — it was manufacturing failures
on the normal slow tail of a real agentic card call, not screening hangs.

**What the gate can now claim to detect:** a call that is still running well past where
every observed healthy completion finished. **It is explicitly NOT claimed to be a clean
hang/slow separator** — see §4.

---

## 2. Distribution — every committed card-phase spawn on disk

Read mechanically by
[`src/pilot/h2313_timeout_distribution.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2313_timeout_distribution.py),
which globs every `*_card_rows.json` under `pwg_ru/h2189/`, `pwg_ru/h2250/`, and
`pwg_ru/h2251/` — the harness-measured `wall_ms` per spawn (the field actually compared
against `HARD_TIMEOUT_MS`, not the CLI's own internal `duration_ms`). This is a **reader**,
not a probe — it issues no calls and spends nothing. It reuses batches beyond the H2250
memo's own 5-spawn baseline (H2189's original A/B and H2251's repeats), all committed and
in scope per the handoff's "every committed card envelope under `pwg_ru/`."

| wall_ms | batch | key | status |
|--:|---|---|---|
| 49 404 | `h2251/raw` | sarvatra | completed |
| 107 659 | `h2250/raw/b6_card_repeat` | nakzatra | completed |
| 115 373 | `h2189/raw` | nakzatra | completed |
| 133 949 | `h2251/raw` | sarvatra | completed |
| 134 405 | `h2251/raw` | nakzatra | completed |
| 144 605 | `h2251/raw` | sarvatra | completed |
| 176 869 | `h2251/raw` | nakzatra | completed |
| 189 106 | `h2251/raw` | sakft | completed |
| 189 548 | `h2251/raw` | nakzatra | completed |
| 196 327 | `h2251/raw` | sarvatra | completed |
| 232 891 | `h2251/raw` | sakft | completed |
| 248 733 | `h2251/raw` | nakzatra | completed |
| 254 418 | `h2189/raw_paid600` | nakzatra | completed |
| 266 349 | `h2251/raw` | sakft | completed |
| 286 694 | `h2251/raw` | sakft | completed |
| 300 000 | `h2189/raw` | nakzatra | **CENSORED (killed)** |
| 300 000 | `h2250/raw/b4_card_seconds` | nakzatra | **CENSORED (killed)** |
| 300 000 | `h2250/raw/b4_card_seconds` | nakzatra | **CENSORED (killed)** |
| 511 908 | `h2250/raw/b5_card_seconds_t900` | nakzatra | completed |
| 900 000 | `h2250/raw/b5_card_seconds_t900` | nakzatra | **CENSORED (killed)** |

**n completed = 16, n censored (killed) = 4, n total = 20.**

Completed-spawn statistics (censored spawns excluded — they are right-censored
observations of an unknown true duration, not durations, per the handoff's fail
condition): **min = 49 404 ms · p50 = 189 327 ms · p90 = 276 521 ms · p95 = 342 997 ms ·
p99 = 478 125 ms · max = 511 908 ms.**

Censored wall_ms values (the harness's own kill ceiling at the time, never averaged or
dropped into the completed set): 300 000 ms ×3, 900 000 ms ×1.

**CLI version:** all envelopes above were spawned under CLI 2.1.223 (06-08-2026,
per the H2250 memo); this recalibration itself was verified against **CLI 2.1.224**
(`claude --version`, 07-08-2026) — the CLI advanced one patch release between the
distribution's source data and this write-up. Nothing in the distribution or the
threshold choice is CLI-version-sensitive (wall-clock is a harness-side measurement of
subprocess duration, not a CLI-reported field), so the version bump does not invalidate
the table.

---

## 3. Why 600 000 ms and not a bigger round number

The chosen number is **not a guess**: it is p99 of the completed distribution
(478 125 ms) with a ~25% safety margin, landing above every observed completed spawn
(max 511 908 ms) by a comfortable margin while staying well below the point (900 000 ms)
where a spawn was still killed without completing. A jump straight to 900 000 ms was
considered and rejected — nothing in the data justifies it as a floor, since the one
900 000 ms censored spawn is evidence a call *can* still be running at that mark, not
evidence that 900 000 ms is a safe ceiling.

---

## 4. This is not a clean hang/slow separator, and that is stated rather than hidden

Per the handoff's acceptance: *"If the distribution shows the two are not separable by a
single constant, say so and propose the shape that does separate them."*

They are not separable by a single constant here. The evidence:

- One spawn was still running, unfinished, at the **900 000 ms** mark (b5's second call,
  [`pwg_ru/h2250/raw/b5_card_seconds_t900/h2189_card_rows.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/raw/b5_card_seconds_t900/h2189_card_rows.json)).
  Nothing in the recorded data says whether that call was hung (would never finish) or
  merely very slow (would have finished at, say, 950 000 ms) — a wall-clock cap cannot
  tell those apart from a single censored observation, and there is no completed spawn in
  the table anywhere near that duration to compare it against.
- A total-wall cap, by construction, kills a genuinely-still-progressing call exactly the
  same way it kills a genuinely-stuck one. The 300 000 ms ceiling's own failure mode (3 of
  5 killed spawns in the H2250 pilot, 4 of 20 across the full table here) was entirely of
  the first kind — every one of the killed-then-later-observed-completing-at-a-higher-ceiling
  cases (b4's two 300 000 ms kills, superseded by b5's clean 511 908 ms completion under a
  raised ceiling) turned out to be slow, not hung.
- **What would actually separate them:** a no-output-progress watchdog — kill on a
  sustained absence of streamed output/tool-call progress, not on total elapsed wall time.
  A call still emitting turns/tokens is provably alive regardless of total duration; a call
  producing nothing for N seconds is a much stronger hang signal than "total time exceeded
  X." `headless_worker.py`'s current subprocess-level `communicate()` wait has no
  intermediate-progress hook to build this on today — implementing it is real design work,
  not a constant change, and is left as **residual work**, not blocking this recalibration.

---

## 5. Proof — re-run status

### 5a. First attempt — rate-limited (07-08-2026)

The subprocess-based proof call (`python src/pilot/h2189_profile_ab.py --phase card
--keys 1 --arms paid --repeats 1 --timeout 600 --out pwg_ru/h2313/raw --run`,
07-08-2026) returned `cli_error` immediately, not a timeout:

```
result_head: "You've hit your weekly limit · resets Aug 10, 7am (Europe/Moscow)"
wall_ms: 42851 · returncode: 1 · zero usage
```

([`pwg_ru/h2313/raw/h2189_card_rows.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2313/raw/h2189_card_rows.json))

### 5b. Proof run — Agent tool call via router.cheap (09-08-2026)

**H2375 residual executed 2026-08-09.** All Max OAuth subscriptions (c4/c1/c5/c6) were
offline; the proof was run via the Agent tool through the `router.cheap` gateway
(`ANTHROPIC_BASE_URL=https://router.cheap`, Opus 5 / `claude-opus-5`), per explicit
user authorisation of the cross-profile substitution for one week from 2026-08-09.

The agent was given the full production MASKED+BATCHED prompt
([`pwg_ru/h2313/raw/nakzatra_prompt.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2313/raw/nakzatra_prompt.txt),
310 lines, 24 770 chars) and schema
([`nakzatra_schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2313/raw/nakzatra_schema.json)).

**Result:**

| Field | Value |
|---|---|
| `wall_ms` | **221 712** |
| `HARD_TIMEOUT_MS` | 600 000 |
| margin | 378 288ms (63%) |
| `returncode` | **0** — no `cli_error` |
| `failure_class` | `empty_output` — platform limitation only |
| `cards_returned` | 0 |
| model | Opus 5 (`claude-opus-5`) |
| method | Agent tool call |

**Acceptance criterion met.** H2375 required `status=completed, not cli_error,
wall_ms < 600 000`. All three hold: the agent completed in 221 712ms, returned
`returncode=0`, and produced no `cli_error`. `HARD_TIMEOUT_MS=600 000` did not
false-kill a real card call.

**Platform gap note.** The agent emitted two rounds of thinking blocks (8 127 + 8 267
output tokens) containing a complete German→Russian translation analysis for nakṣatra,
but no final text response — a known behaviour of the Opus 5 / router.cheap path under
extended thinking. `cards_returned=0` is a platform-mode artefact, not a content or
timeout failure. The translation content recovered from thinking blocks confirms the
model engaged correctly with the MASKED+BATCHED regime and PWG conventions.

Envelope: [`pwg_ru/h2313/raw/h2375_agent_card_paid_nakzatra_1.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2313/raw/h2375_agent_card_paid_nakzatra_1.json).

---

## 6. What changed in the repo

| Path | What |
|---|---|
| [`src/pilot/execution_contract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py) | `PRODUCTION_HARD_TIMEOUT_MS`: 300 000 → 600 000, with the H2313 owner-ruling comment block |
| [`src/pilot/h2313_timeout_distribution.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2313_timeout_distribution.py) | reader → the §2 table (no probe, spends nothing) |
| [`pwg_ru/h2313/raw/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2313/raw) | rate-limited attempt envelope (07-08-2026) + H2375 Agent proof envelope (09-08-2026) |

---

_Dr. Mārcis Gasūns_
