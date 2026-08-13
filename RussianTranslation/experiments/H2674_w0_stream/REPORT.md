# H2674 — W0 OpenAI SDK stream + 32k cap + PRICE after-1608

_Created: 13-08-2026 · Last updated: 13-08-2026_

**Verdict: PASS** (transport). Official OpenAI Python SDK `stream=True` replaced urllib in `DeepSeek.chat`. Offline mock holds 9000 thinking chars. Live N=3 canary: **3/3**, 0 `IncompleteRead`, `$0.0006`, `DEFAULT_MODEL` still `deepseek-v4-flash`. No TM / store write.

## What landed

| Item | Result |
|---|---|
| Transport | `openai-sdk-stream` (`stream=True`, `stream_options.include_usage`) |
| Cap | `DEFAULT_MAX_TOKENS = 32768`; `prep_pack --live` uses the same client + cap (was 2048) |
| Prices | `price_card` `pre-1608` / `after-1608-offpeak` / `after-1608-peak`; `refuse_if_peak` unchanged |
| Default model | `deepseek-v4-flash` (not flipped) |
| Dep | `openai>=1.55.0,<2` in [`RussianTranslation/requirements.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/requirements.txt) only |

## Offline

```text
python src/pilot/h1210/deepseek_arm.py --selftest
python src/pilot/h1210/test_deepseek_stream.py
python src/pilot/h1210/prep_pack.py --selftest
```

All PASS. Mock stream: 9000 thinking chars, no urllib.

## Live canary N=3

Keys: `yaTepsita`, `viSvaha`, `viSa`. Model `deepseek-v4-flash`, effort `high`, `max_tokens=32768`. Compact JSON-mode prompt (transport hold, not a full-card rematch).

| key1 | ok | attempts | reasoning_tokens | chunks | latency_s |
|---|---|---:|---:|---:|---:|
| yaTepsita | true | 1 | 1476 | 1511 | 25.07 |
| viSvaha | true | 1 | 81 | 111 | 3.75 |
| viSa | true | 1 | 420 | 449 | 6.89 |

Wall 35.7 s. Cost `$0.0006` on `pre-1608` Flash table. Artifacts: [canary.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2674_w0_stream/canary.jsonl), [canary.summary.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2674_w0_stream/canary.summary.json).

The live prompts did **not** emit >8192 thinking tokens (compact canary). The >8k hold is the offline mock. H2652's urllib `IncompleteRead` was a 10+ minute Pro `high` card; that rematch is [H2676 (Grok 4.6) — W1 Pro Q3 rematch after streaming client](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2676-Grok_SanskritLexicography_deepseek-w1-pro-q3-rematch_13.08.26.md).

Canary runtime used the machine's already-installed OpenAI SDK 2.41.1 (Chat Completions API identical to the 1.x pin). Do not leave a user-site 1.x install that breaks `litellm`.

_Dr. Mārcis Gasūns_
