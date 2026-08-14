# nn_api smoke-test — H1457 spike S1

_Created: 22-07-2026 · Last updated: 14-08-2026_

Spike S1 of [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pubgrade_tm_oral.md)
Step 0. Executed by Sonnet 5 (`claude-sonnet-5`) in an isolated worktree,
22-07-2026. Reproduce with `python src/nn_api.py --smoketest`.

## Result

| Backend | Serves in-env? | Path |
|---|---|---|
| **embed** (LaBSE) | ✅ yes | `sentence-transformers/LaBSE`, downloaded once from the public HF hub (no token), runs locally thereafter |
| **QE** (`labse`) | ❌ no (14-08-2026) | `sentence-transformers/LaBSE` load hits WinError 1455 (pagefile). Named, not comet. |
| **QE** (`comet`) | ❌ no | still no cp314 `unbabel-comet` wheel; gated HF not used as fallback |
| **QE** (`deepseek`) | ✅ yes (H2686 repair) | `deepseek-v4-flash` reference-free JSON judge; ρ=0.4195 on n=80 gold slice |

## Embedding probe (5 Sa/Ru pairs + 1 mismatch)

```
dharmakSetre kurukSetre <-> на поле дхармы, на поле Куру   cosine 0.3056
karma <-> действие                                          cosine 0.5780
yogaH karmasu kauSalam <-> йога есть искусность в действиях cosine 0.5191
Sabda <-> звук                                               cosine 0.3950
AtmA <-> атман, я                                            cosine 0.4217

mismatch (each sa vs "слон идёт в лес по широкой дороге"):   cosine 0.0332-0.1803
```

Every true pair scores above every mismatched pair (min true 0.3056 > max
mismatch 0.1803) — the probe separates cleanly. **LaBSE is the S1-chosen
embedding backend for A5** (and B3's oral aligner).

## QE probe — all three paths fail, logged

1. **`unbabel-comet` package** — install fails: it pins `numpy<2`, which has no
   prebuilt wheel for this machine's Python 3.14 (cp314); building numpy from
   source needs a C compiler (meson found none of `cl`/`gcc`/`clang`/`icl` on
   this Windows box). Not a code bug — an environment gap; installing a full
   MSVC/Build-Tools toolchain to unblock one package is out of scope for an
   unattended agent run.
2. **HF Inference API** (`https://router.huggingface.co/hf-inference/models/Unbabel/wmt22-cometkiwi-da`)
   — `401 Unauthorized` unauthenticated. COMET-QE checkpoints are gated
   (license click-through + token), not served on the free anonymous tier.
   No `HF_TOKEN` is configured in this environment.
3. **LLM-as-judge fallback** (DeepSeek or Claude scoring (sa, ru) pairs) —
   needs a key. `build_corpus_lexicon.py` already documents the DeepSeek path
   requires `DEEPSEEK_API_KEY` in a repo-local `.env`; no such file exists
   here (checked both this worktree and the main `SanskritLexicography`
   checkout). No Anthropic API key is present either (per standing org
   guidance, this account has none).

**Conclusion (updated 14-08-2026, H2686):** COMET-QE still does not serve.
LaBSE QE does not serve on this box (WinError 1455). The one authorized
repair is DeepSeek `deepseek-v4-flash`, which **does** serve as a named
reference-free judge (`--qe deepseek`). `--qe comet` still falls back to
the proxy and keeps the name `proxy`. Proxy ρ=-0.0351 remains preliminary.

**A5** is pagefile-blocked in the same process that cannot load LaBSE; that
is a host constraint, not a missing embed API.

## `nn_api.py` interface

- `embed(texts) -> List[List[float]]` — disk-cached (`.nn_api_cache/`, gitignored-by-pattern
  since it lives under `src/`), keyed by SHA-256 of the input string.
- `qe(sa, ru, backend='labse')` — named backends only. `labse` and `comet`
  return `None` here; do not invent a score. DeepSeek QE lives in `tm_grade.make_qe('deepseek')`.
- `embed_available()` / `qe_available(backend)` — liveness checks. Default
  backend is `labse`, never silently `comet`.

_Dr. Mārcis Gasūns_
