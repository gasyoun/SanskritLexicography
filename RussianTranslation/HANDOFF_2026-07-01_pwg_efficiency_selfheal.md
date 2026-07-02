# Handoff — PWG dashboard, RU catch-up, and the self-healing translation harness

_Created: 01-07-2026 · Last updated: 01-07-2026_

**For:** a fresh chat. **Branch:** `feat/pwg-en-fu1-phase0` (off `master`).
**Orchestration:** Opus 4.8 (`claude-opus-4-8`). **Generation:** EN = Sonnet 5
(`claude-sonnet-5`, pinned on the `--lang=en` path); RU = the `sonnet` alias (matches the
existing RU corpus). **Live dashboard:** https://gasyoun.github.io/SanskritLexicography/

## ⚠️ Branch + store contention (read first)
A second (autonomous) account works this repo and **cycles the local checkout across
branches mid-session** — the local `feat/pwg-en-fu1-phase0` ref even gets deleted. **Commit
via a git worktree off `origin/feat/pwg-en-fu1-phase0`**, never by editing the main checkout:
```
git fetch origin feat/pwg-en-fu1-phase0
git worktree add --detach <tmp> origin/feat/pwg-en-fu1-phase0
# edit in <tmp>, then:
git -C <tmp> commit ... && git -C <tmp> push origin HEAD:feat/pwg-en-fu1-phase0
git worktree remove <tmp> --force && git worktree prune
```
That account also **wiped the RU store** this session: a `promote_final_cards.py` *default
(non-merge) overwrite* rebuilt [`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pwg_ru_translated.jsonl)
from a handful of on-disk `wf_output` files, replacing **10,122 rows with 472**. Recovered
from `.legacy.bak`; protected copy at `src/pwg_ru_translated.jsonl.SAFE_full10122_20260701.keep`
(the store + all `.bak` are **gitignored/local-only**, not on GitHub). I added an **overwrite
guard** to promote (refuses >50% shrink without `--force`) — but **always use `--merge`** for
per-root work. If the local store looks small again, restore from `.SAFE_...keep`.

## What's done
- **EN (FU1) coverage: 2096/2121 = 98.8%** across 46 `wf_output.en.<root>.json` stores
  (gitignored). All 30 FU1 worklist roots swept; only dense-head residual remains.
- **RU store: 10,122 rows, 46 roots.** Root-caused the gam gap (RU was 6/127 — *never
  finished*, not clobbered; confirmed via backups) and ran a **sub-90% catch-up sweep**:
  gam **6→520 senses (123/127 sub-cards)**; roots <90% dropped **13→4** (As 80 / Ap 87 /
  ji 88 / laB 88; `d_a 0%` is the dA/DA case-collision artifact — ignore).
- **Article dashboard** — [`src/pilot/build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/build_article_site.py):
  RU∪EN **union spine** (every EN sub-card + RU where present), **3-tab Deutsch/Русский/English**,
  SLP1→**IAST**, per-root **RU% coverage badges**. **Lazy-load**: `articles.js` is a 6.6 KB
  index; each root's HTML is `roots/<safe>.js` loaded on click via `<script src>` (works from
  `file://` too). Output `article_site/` is **gitignored**; published to the **`gh-pages`**
  branch (Pages source = gh-pages / root). Rebuild: `python src/pilot/build_article_site.py`;
  republish by copying `article_site/` onto gh-pages.

## Tooling built this session (all on the branch)
- [`src/pilot/ru_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/ru_coverage.py)
  — per-root RU% vs the intended card set (EN `meta.selected_keys`); flags partial roots; `--keys ROOT` lists missing. Zero LLM.
- [`src/pilot/en_residual_keys.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/en_residual_keys.py)
  — residual (no-EN) keys straight from an EN store.
- [`src/pilot/en_split_triage.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/en_split_triage.py)
  — predicts head-split need from the stores' pass/fail labels. **Finding: card size does NOT
  predict failure** (the 5 largest cards all passed) → failure is stochastic retry-cap variance.
- [`src/pilot/autosplit_requeue.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/autosplit_requeue.py)
  — per-card, in-place tiered splitter (T0 whole · T1 sense · T1b lettered sub-sense · T2
  citation, incl. a single giant sense). No rootmap churn.
- [`src/promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/promote_final_cards.py)
  — added **`--merge`** (sub-card level, safe per-root catch-up) + the **overwrite guard**.

## Efficiency levers (audit → shipped)
1. **`--selfheal`** in [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/gen_opt_harness2.py):
   on a card the batch can't translate, auto-split → translate fragments → stitch, in-harness,
   **gated (default OFF)**, with **per-fragment retry (3×)** and a completeness guard.
   **Validated LIVE:** `ji` head healed (8 fragments → 48 stitched senses, fidelity OK).
2. **Summary-return** — the harness returns `{summary:{ok,null,healed,null_keys}, results}` so
   the orchestrator reads outcome without parsing the full blob.
3. **Dashboard lazy-load** (13 MB → 6.6 KB first paint), above.

## Key gotchas (don't relearn)
- Dense-card failure is **stochastic, not size-predictable**; a giant that passes on the
  whole-card attempt is fidelity-valid but **structurally coarse** (man → 3 senses, banD → 1)
  vs a proper heal (ji → 48). Prefer the split-heal for structure.
- **RU harnesses need CRLF→LF strip before launch** (git autocrlf gives `gen_opt_harness2.py`
  CRLF → the JS template carries raw `\r`, which the Workflow-tool approval rejects). EN path is LF.
- **RU batched runs whole-batch-poison** (one dense card nulls the batch) → use `--budget=1` solo.
- Windows console is cp1251 → every script does `sys.stdout.reconfigure(encoding='utf-8')`.
- `article_site/` and the `wf_output.*`/`pwg_ru_translated.jsonl` stores are **gitignored**
  (local); code + the gh-pages branch are the durable artifacts.

## Next steps (queued)
1. **brū** — the lone EN head holdout (198 `<ls>`, 13 fragments); heal still misses it. Needs
   the fragment-**grouping** tier (below) or a hand look. 1 card.
2. **fragment-grouping** — `--selfheal` over-splits (1 atom/fragment → 85 calls for a 9.6 KB
   card; ~2.2 M tok for 6 giants). Group atoms into budget-sized fragments with order-robust
   reassembly → makes heal economical and likely closes brū.
3. **#3 binary-split batching + #5 output-keyed budget** — the last two efficiency levers;
   do as a **gated, live-validated pass** on the shared harness (don't rush; the autonomous
   account depends on it).
4. Optionally re-run `--selfheal` per-root (correct `meta.root`) over the remaining EN/RU
   dense residual with the hardened tool, then `promote_final_cards.py ... --merge`.

Full journal: [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/.ai_state.md)
(Dev Notes carry the tier ladder + undone tiers). Prior handoff:
[`HANDOFF_2026-07-01_pwg_en_fu1_finalize.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/HANDOFF_2026-07-01_pwg_en_fu1_finalize.md).

_Dr. Mārcis Gasūns_
