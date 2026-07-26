Found while rebuilding the coordinator fixtures for the Codex hardening branch (step 2, branch `codex/step2-sealing`). **Not yet on master** — the change that causes it is unlanded, so this is a "do not land without the fix" note rather than a live incident.

## What changed

`coordinator.promote_ready` used to shell out to `promote_final_cards --batch-manifest`. On the hardening branch it calls **`promote_final_cards.batch_promote(...)` in-process**.

That is a reasonable change on its own. The consequence for the test suite is not.

## Why it is dangerous

Two facts combine:

1. **The fixtures' isolation was the subprocess boundary.** `test_h1420_p10_promote_rebuilds_tm_in_finally` (and its siblings) stub `coordinator.run_cmd` with a fake that intercepts `--batch-manifest` and writes a canned report. With promotion in-process, that fake is **inert** — real `batch_promote` runs.
2. **The store path is not test-scoped.** `promote_final_cards.DEFAULT_STORE = canonical_store(...)`, and [`store_path.canonical_store`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py) resolves `PWG_RU_STORE` → **main-worktree store** → local default. `window_selftest` sets no `PWG_RU_STORE`, so it resolves to the **real canonical `pwg_ru_translated.jsonl`** (~11.6k rows).

So the promotion tests read the live store. They currently *refuse* rather than write — I hit `promotion would create 4 duplicate sense identity/identities`, which is the guard comparing my fixture rows against **real store rows**. That refusal is luck, not isolation: with a fixture whose identities don't collide, `batch_promote` proceeds to `_atomic_write_rows` against the canonical path.

## Fix applied on the branch

`window_selftest` now pins a scratch store **before any repo import** (`DEFAULT_STORE` is resolved at import time), and creates it, because a *missing* store is itself refused:

```python
_SCRATCH_STORE = os.path.join(tempfile.gettempdir(), 'window_selftest_scratch_store.jsonl')
os.environ.setdefault('PWG_RU_STORE', _SCRATCH_STORE)
if not os.path.exists(os.environ['PWG_RU_STORE']):
    open(os.environ['PWG_RU_STORE'], 'a', encoding='utf-8').close()
```

## Worth generalising

This is the third instance of the same shape in two days:

- [#726](https://github.com/gasyoun/SanskritLexicography/issues/726) — a selftest appending to the tracked `no_pwg_residuals.jsonl`
- [#729](https://github.com/gasyoun/SanskritLexicography/issues/729) — a gate probe reading readings it did not take
- this one — a selftest reaching the canonical store because an isolation boundary moved

The common cause is that **isolation is incidental** — it depends on a subprocess boundary, a filename, or an env var that no one owns. A `conftest`-style guard that refuses to run any selftest unless `PWG_RU_STORE` (and the coordinator dir, and the residual ledger) point outside the repo would convert all three from "spot it in review" to "cannot happen".
