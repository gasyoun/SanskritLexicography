# nn_api smoke-test — H1457 spike S1

_Created: 22-07-2026 · Last updated: 22-07-2026_

Spike S1 of [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pubgrade_tm_oral.md)
Step 0. Executed by Sonnet 5 (`claude-sonnet-5`) in an isolated worktree,
22-07-2026. Reproduce with `python src/nn_api.py --smoketest`.

## Result

| Backend | Serves in-env? | Path |
|---|---|---|
| **embed** (LaBSE) | ✅ yes | `sentence-transformers/LaBSE`, downloaded once from the public HF hub (no token), runs locally thereafter |
| **QE** (COMET-QE) | ❌ no | see below — three paths tried, all fail |

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

**Conclusion:** QE cannot serve in this environment via any of the three
logged paths. Per the plan's stop condition (VERIFICATION risk register,
S1 row): this **blocks A2** (COMET-QE calibration) — `tm_grade.py --qe comet`
stays a no-op falling back to `--qe proxy` (already implemented, logged at
`make_qe()`), and the grade is marked **preliminary** pending either (a) an
`HF_TOKEN` + gated-model acceptance, or (b) a compiler toolchain / newer
`unbabel-comet` release with cp314 wheels, or (c) any LLM API key for the
judge fallback. None of these are available to fix unattended.

**A5 is NOT blocked** — embed serves, so the LaBSE/Vecalign sentence-aligner
proceeds on schedule.

## `nn_api.py` interface

- `embed(texts) -> List[List[float]]` — disk-cached (`.nn_api_cache/`, gitignored-by-pattern
  since it lives under `src/`), keyed by SHA-256 of the input string.
- `qe(sa, ru) -> None` — honest stub; returns `None` rather than a fabricated
  score. Callers must handle `None` (see `tm_grade.py`'s existing
  `make_qe()` fallback-to-proxy logic, which this satisfies without change).
- `embed_available()` / `qe_available()` — liveness checks other scripts use
  to decide whether to attempt the corresponding track.

_Dr. Mārcis Gasūns_
