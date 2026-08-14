# H2676 — W1 Pro Q3 rematch after streaming client

_Created: 14-08-2026 · Last updated: 14-08-2026_

**Verdict: PASS** (D16 dual floor). Official OpenAI SDK stream held a 22-card Pro `high` rematch that urllib could not (H2652 FAIL). `det_gate_clean` **21/22**, `$/clean` **$0.01991** ≤ **$0.0465** (5× H1210 Flash/chat $0.0093). `store_write` never true. `would_promote` 0/22 (promote-DRY). This is **Q3 draft-assist** under the frozen rule, not a production Q1–Q2 draft-lane (E1 / H2488 still FAIL).

Rule: [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/VERDICT_RULE.md). Spend: [SPEND_AUTH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/SPEND_AUTH.md). Summary: [summary.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/summary.json).

## Prerequisite canary

[H2674 (Grok 4.6) — W0 OpenAI SDK stream + max_tokens 32k + PRICE after-1608](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2674-Grok_SanskritLexicography_deepseek-w0-openai-stream-price_13.08.26.md) canary **PASS**: [H2674 REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2674_w0_stream/REPORT.md) — 3/3, $0.0006, 0 `IncompleteRead`, `DEFAULT_MODEL` still Flash. This sitting did **not** rerun urllib.

## Frozen floors (before token 1)

| Clause | Floor | Measured | Hold |
|---|---|---|:---:|
| Attempted | 22/22 | 22/22 | yes |
| `det_gate_clean` | ≥ 15/22 | **21/22** | yes |
| `$/det_gate_clean` | ≤ $0.0465 (5× $0.0093) | **$0.01991** | yes |
| Served model | `deepseek-v4-pro` | every successful call | yes |
| Price table | Pro `pre-1608` 0.435 / 0.003625 / 0.87 | same | yes |
| Store / TM | `store_write` never true | false; `would_promote` 0/22 | yes |

Transport: `openai-sdk-stream`, `max_tokens=32768`, `--reasoning-effort high`, workers 2, timeout 1800 s. Wall **6350.7 s**. Generation calls **29**. Cost **$0.4181** on Pro `pre-1608`. `IncompleteRead` count: **0**.

## Per-card (payload `key1`)

| key1 | status | attempts | det_clean | reasoning_tokens | latency_s |
|---|---|---:|:---:|---:|---:|
| ya_tepsita | pending-controller | 1 | yes | 10604 | 752.97 |
| vi_svaha | pending-controller | 1 | yes | 8180 | 727.54 |
| vi_sa | pending-controller | 1 | yes | 15041 | 198.3 |
| dr_ava_ra | pending-controller | 1 | yes | 15708 | 203.36 |
| par_rin | worker-null-death | 3 | no | 14718 | 192.65 |
| sa_msargin | pending-controller | 1 | yes | 9514 | 127.9 |
| kakz_ivant | pending-controller | 1 | yes | 9753 | 750.69 |
| a_ngaja | pending-controller | 1 | yes | 11791 | 165.39 |
| vyatyaya | pending-controller | 1 | yes | 9456 | 139.81 |
| roza | pending-controller | 1 | yes | 8110 | 124.15 |
| pras_u | pending-controller | 1 | yes | 12248 | 183.33 |
| div_a | pending-controller | 1 | yes | 9617 | 145.13 |
| vazawk_ara | pending-controller | 1 | yes | 11485 | 1960.76 |
| anar_ta | pending-controller | 2 | yes | 15429 | 171.43 |
| sa_b_ajay | pending-controller | 2 | yes | 13968 | 155.8 |
| vi_d | pending-controller | 1 | yes | 14927 | 166.64 |
| d_ikz_a | pending-controller | 2 | yes | 13546 | 170.73 |
| p_avana | pending-controller | 1 | yes | 18687 | 239.17 |
| pf_tak | pending-controller | 1 | yes | 12497 | 176.08 |
| yatna | pending-controller | 1 | yes | 15293 | 179.95 |
| ras | pending-controller | 1 | yes | 14050 | 169.21 |
| vicitra | pending-controller | 3 | yes | 15292 | 190.99 |

`pending-controller` with empty `det.issues` is `det_gate_clean` (complexity flag; Opus controller not run). `would_promote` stays false unless `clean-no-review`.

## Failures and transport

- **par_rin** — only non-clean. Attempt 1 served Pro and stopped; free gate failed on missing `{T34}` in german and russian. Attempts 2–3: `APIConnectionError`. Final `worker-null-death`. Quality miss, not urllib `IncompleteRead`.
- **anar_ta#1** — `ReadTimeout`; attempt 2 clean.
- **vicitra** — 3 attempts, still clean.
- No `IncompleteRead` on any of 29 calls.

## Cost honesty

Pro table only (`price_model=deepseek-v4-pro`, `price_card=pre-1608`):

| Token class | Count | USD / 1M | Share |
|---|---:|---:|---:|
| cache-miss in | 151 584 | 0.435 | $0.0659 |
| cache-hit in | 225 024 | 0.003625 | $0.0008 |
| out (incl. thinking) | 403 889 | 0.87 | $0.3514 |
| **Total** | | | **$0.4181** |

`$0.4181 / 21 clean = $0.01991` (2.14× H1210 Flash/chat $0.0093; ceiling 5×). Do not reprice with Flash PRICE_*.

## What this does **not** authorise

- TM / store write
- Auto-promote
- Unattended Q4 / `max` sub-arm (not run; cannot flip D16)
- Flipping `DEFAULT_MODEL` off Flash
- Production Q1–Q2 draft-lane (E1 still FAIL)

Artifacts: [q3.telemetry.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/run/q3.telemetry.json), [q3.slice_result.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/run/q3.slice_result.json), [q3.journal.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2676_v4pro_q3_rematch/run/q3.journal.jsonl).

_Dr. Mārcis Gasūns_
