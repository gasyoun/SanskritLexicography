# H2044 — G46 reprobe: c4 health **GO**, canary unspent (02-08-2026)

_Created: 02-08-2026 · Last updated: 03-08-2026_

Executor: **Opus 5 1M** (`claude-opus-5[1m]`) ·
[H2044](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2044-Opus_SanskritLexicography_g46-pwg-live-health-reprobe_31.07.26.md) ·
goal [G46](https://github.com/gasyoun/Uprava/blob/main/GOALS_MANUAL.md) ·
skill [/pwg-live-gate](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md).

**Terminal state: `HEALTH_GO_CANARY_UNSPENT`.** 2 paid calls, **$0.7232244**. No canary,
no window, no store write, no promote. 1 call of the ≤3 cap left unspent — deliberately,
for the reason in §3.

## 1 — offline floor (0 paid)

| check | result |
|---|---|
| [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py) | **200/200** defined, 200 passed, 0 failed |
| [`h963_c4_gate0_probe.py --selftest`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py) | **7/7** OK (no live call) |
| [`lang_parity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lang_parity_check.py) | **90** entries, all verdicts complete, no drift; 25 language-aware files tracked or exempt |
| [`check_launch_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/check_launch_ledger.py) | launch failure ledger **19** entries complete |

Counts grow over time (window was 144 at H1110, 180 at H1447, 200 now) — the floor is
"all pass", never a fixed number.

## 2 — health: one probe run, no retry, no reroll

Run `h963-c4-single-profile-gate0-2026-07-16/2026-08-02T13:02:43Z-pid27240` (probe #729),
profile `c4` (`D:\ClaudeTools\profiles\claude4\.claude`), route `claude-cli-headless`,
generation model `claude-sonnet-5`, prompt 6 828 B (≥ 5 KiB floor), ceiling **65 000 ms**.

| purpose | wall `elapsed_ms` | CLI `duration_ms` | `duration_api_ms` | `api_gap_ms` | class |
|---|---:|---:|---:|---:|---|
| warmup | 62 146 | 37 756 | 32 872 | 29 274 | success |
| **measured** | **60 845** | **40 623** | **36 508** | 24 337 | success |

**GATE-0 VERDICT: PASS** — measured 60 845 ms strictly below 65 000 ms, 0 connection
errors, schema-carrying output on both readings.

**The exact complement of [H2174](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).**
Two hours earlier all three candidate gate numbers *failed* (96 520 / 77 966 / 69 137 vs
65 000); here all three *pass* (60 845 / 40 623 / 36 508). So the still-owed wall-vs-`duration_api_ms`
ruling is again not load-bearing for this window — a second reading where the numbers agree.
Four measured attempts on 02-08 now read **PASS → NO-GO → NO-GO → PASS**
(43 815 → 75 561 → 96 520 → 60 845 ms wall), which is the bimodality H2174 named, observed
recovering rather than only degrading.

The warm-up (62 146 ms) is **advisory for latency only** under MG's 31-07-2026 ruling; it
was a success with a valid envelope, so it does not veto. Under the superseded
"both readings < 30 000 ms" rule this run would have been a NO-GO — which is why
[GOALS_MANUAL](https://github.com/gasyoun/Uprava/blob/main/GOALS_MANUAL.md) G46's signal
line is corrected to the 65 000/measured-only policy in the same pass.

## 3 — why the canary was NOT fired, with a call left in budget

`/pwg-live-gate` Step 2 needs a **manifest v2** for
`dq_canary_puregloss~~h0_zz_pw`. The curated fixture exists —
[portrait](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw.portrait.json)
+ raw — but **the manifest itself does not, and neither does anything that builds it**:
`git log --all --diff-filter=A` over the whole history returns no canary manifest, and the
only `synthetic_control` JSON ever committed is
[H1447's wf_output](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1447/h1447_canary_wf_output.json)
— the *result*, not the input that produced it. Both
[H1447's packet](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1447/H1447_C4_LIVE_GATE_2026-07-22.md)
and [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md)
§A2 give the command shape and mark it "illustrative".

So firing the canary here means hand-authoring an executable manifest on the money contour
from a v1 `nominal_masked` template whose prompt does not match the canary's un-masked
pure-gloss shape. That is exactly the improvisation G46's guardrail forbids ("never guess"),
and a malformed manifest would burn the last call of the cap on a tooling error rather than
a health signal. **Not spending is the disciplined stop, not an incomplete one.**

The gap is now handoff-tracked: a committed, selftested builder that emits a valid v2 canary
manifest — see the residual named in the registry row for H2044. Once it exists, the GO
branch of G46 becomes reproducible instead of one-session folklore.

## 4 — verdict, derived (not asserted)

```
health       = PASS   (measured 60 845 ms < 65 000 ms, 0 conn errors)
canary       = NOT RUN (no committed manifest v2 / builder — §3)
gate_reason  = HEALTH_GO_CANARY_UNSPENT
verdict      = NOT LIVE_GO  (LIVE_GO requires health PASS *and* a clean canary)
```

**No paid translation call is authorized by this packet.** A bounded window still needs
(a) a fresh health PASS at spend time — this one goes stale, and on a bimodal route
"fresh" means minutes-to-hours, not "today"; (b) a canary GO receipt ≤ 6 h old, which
[`canary_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/canary_gate.py)
enforces mechanically against `bounded_staged_run.py --execute`; and (c) a prepared lease.

## 5 — spend ledger

| ordinal | purpose | output tok | cache read | cache create | `observed_cost_usd` |
|---:|---|---:|---:|---:|---:|
| 1 | probe:warmup | 977 | 29 005 | 59 162 | 0.3783345 |
| 2 | probe:measured | 1 239 | 35 563 | 52 605 | 0.3448899 |
| | **total** | **2 216** | **64 568** | **111 767** | **0.7232244** |

`cost_evaluable=true`, 0 unevaluable, 0 pending. Cap ≤3 paid calls; **2 spent, 1 unspent**.

Artifacts: [`h2044_gate0_probe_events.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2044/h2044_gate0_probe_events.jsonl) ·
[`h2044_gate0_calls.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2044/h2044_gate0_calls.json) ·
[`h2044_gate0_preflight.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2044/h2044_gate0_preflight.json).

_Dr. Mārcis Gasūns_
