# PWG TM — Wave-2 defaults applied (H2721)

_Created: 14-08-2026 · Last updated: 14-08-2026_

Grok 4.6 (`grok-4.6`). Applies [H2686 (Grok 4.6) — PWG TM genuine semantic QE and live retrieval](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2686-Grok_RussianTranslation_pwg-tm-semantic-qe-retrieval-w2_13.08.26.md) defaults to the next 5,000-headword wave. Wave 1 is not rewritten.

## Policy (`pwg.tm.wave2.defaults.v1`)

| Knob | Value |
|---|---|
| Measurement QE | `deepseek` / `deepseek-v4-flash` (not comet; proxy stays ρ=-0.0351) |
| Retriever | `char4gram` until LaBSE loads |
| Formula TM context | `auto_fuzzy` |
| Gloss TM context | `advisory` |
| Sense wrappers | `off` (separate generation; no fuzzy TM) |
| Citation / example / grammar | `exact_only` |
| Short-gloss denylist | `Jmd` / `jmdm` / `jmdn` / `jemand` / `die` / `der` / `das` / `den` / `dem` / `des` / `gewachsen` |

Exact compatible-address reuse remains on except denylist and sense wrappers.

## Next 5,000 queue

Frozen as [`priority_5000_w2.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/priority_5000_w2.jsonl). Manifest sha256 `f9fdb4ff6155f2e945d4f26d5fdb07a7f96b36ad48537b5a0be43988b0335ff8`.

| Check | Result |
|---|---|
| Selected | **5000** unique k1 |
| Overlap with Wave 1 | **0** |
| Wave-1 files | not written |

## Proof

```text
python src/pwg_tm_wave2_policy.py --selftest
python src/pwg_tm_generate.py --verify
python -m pytest tests/test_pwg_tm_wave2_policy.py tests/test_pwg_tm_generate.py
python src/pwg_tm_priority.py --wave 2 --limit 5000 --exclude-jsonl release/pwg_tm_canonical/priority_5000.jsonl --out-dir release/pwg_tm_canonical
```

This session does **not** run the 5,000-key generator. That is a later drain using this queue and policy.

_Dr. Mārcis Gasūns_
