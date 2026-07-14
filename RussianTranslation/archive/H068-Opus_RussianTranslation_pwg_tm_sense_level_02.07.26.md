# Handoff — PWG translation-memory: sub-card sense/fragment reuse (the next TM increment)

_Created: 02-07-2026 · Last updated: 02-07-2026_

> ✅ **SPENT — do NOT re-execute (executed 2026-07-02, Opus 4.8 `claude-opus-4-8`).**
> Fragment-level TM shipped on branch `feat/pwg-tm-fragment-reuse`: `frag_address` +
> `build_frags`/`load_frag_tm` in `translation_memory.py`, `frag_prov` channel + `FRAG_TM`
> reuse in `gen_opt_harness2.py`, `window_selftest.py` 25/25, live-proven
> (`gam~~h0_02_sec_2`: 5 agents/312k tok → **0 agents/0 tok**, card byte-identical). One
> deliberate deviation from §Suggested-approach step 2: the `plan()` header is NOT stripped —
> with approach (a) it is real translated source of fragment 0 on both sides, so stripping it
> would break the address round-trip. Details in `.ai_state.md` (fragment-TM bullet).

**How M.G. runs me:** open a NEW chat with working dir
`C:\Users\user\Documents\GitHub\SanskritLexicography`, pick **Opus 4.8** (`claude-opus-4-8`) or
Sonnet 5 in the model picker, and type exactly:

```
Read C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\H068-Opus_RussianTranslation_pwg_tm_sense_level_02.07.26.md and execute it.
```

**Agent, first action:** state this session's model tier + exact resolved version from the
environment block (never from memory), and pin it in every log line / promotion
(`--gen-model-version`).

## Context — what already exists (do NOT rebuild it)

The **card-level** translation-memory sidecar is DONE and merged
([PR #87](https://github.com/gasyoun/SanskritLexicography/pull/87), 2026-07-02, Opus 4.8
`claude-opus-4-8`):

- [`src/pilot/translation_memory.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py)
  — content-addressed cache, key = `f"{lang}:{input_raw_sha256}"`, harvested from the
  local-only store (**2,121 cards / 10,841 senses / 49 roots**). Build:
  `python src/pilot/translation_memory.py build --lang ru`.
- [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  `--tm[=PATH]` (OFF by default) — pre-resolves whole cards whose source SHA is cached, into a
  `TM_RESOLVED` lane with **no `agent()` call**; total-accounting invariant preserved.
- `window_selftest.py` **24/24** (incl. `test_translation_memory_addressing`,
  `test_tm_pre_resolves_cards`).
- Live-proven: **gam 127→3** cards translate; **jIv 17/17 from TM at 0 tokens / 70 ms**.

Read the module docstrings and `.ai_state.md`'s top "Next Steps" bullet before touching
anything — the design rationale (why card-level, why content-addressed) is written there.

## Mission — sub-card (sense/fragment) reuse

Card-level reuse skips a card only when its ENTIRE source is byte-identical to a cached one.
The higher-value reuse the memory
([resume-vs-fresh-run](https://github.com/gasyoun/Uprava/blob/main/handoffs)) asked for is
**within a card**: a giant flat headword (kAla / ka / śrī — one card, 40+ selfheal groups)
that partially failed should re-run only its **missing** fragments, and the **same meaning**
in a root and its derived noun should be reused instead of re-translated.

**The blocker (measured, do not re-measure):** the store's per-sense `de` does **not** align
byte-for-byte with the harness's deterministic `autosplit_requeue.plan()` fragments — a sample
card gave **3/7 exact** matches (the first fragment carries the card's `=== LAYER … ===`
header; tier-2 citation-batching splits one sense's `de` across several fragments). So you
**cannot** key a sense-level TM on `plan()` fragment text and expect hits. Solve that
alignment first; everything else is downstream.

### Suggested approach (validate before building — this is a design task, not a mechanical one)

1. **Add a fragment-provenance channel.** When `selfHeal`/`healOnly` resolve a fragment,
   the resolved sense(s) already restore to exact source markup. Persist, per resolved
   fragment, `{lang, fragment_source_sha256, sense(s)}` — either (a) have `save_and_audit.py`
   emit a `translation_memory.frag.<lang>.jsonl` sidecar as it ingests `wf_output`, or
   (b) recompute the fragment→sense mapping deterministically at harvest by re-running
   `plan()` on the card source and aligning by restored-markup token multiset. Prefer (a):
   it records ground truth at the moment of success, no re-alignment guesswork.
2. **Key fragments on `sha256(lang + '\x00frag\x00' + fragment_source)`** where
   `fragment_source` is the exact `plan()` chunk text (strip the injected `=== LAYER … ===`
   header first — it is generation scaffolding, not source, and is what broke 4/7 of the
   sample matches).
3. **Inject in `gen_opt_harness2.build()`**: for each `--tm` card that is NOT a whole-card
   hit, look up each of its precomputed `FRAGS` fragments; pass the cached ones into the JS
   as pre-resolved (a `FRAG_TM[k]` map) so `healGroup` **skips** cached fragments and only
   calls `agent()` for the uncached — the exact "inject cached fragments as pre-resolved"
   the memory specifies. Keep the fidelity guards (per-fragment `{Tn}` multiset check must
   still pass on injected fragments).
4. **Test-drive it** in `window_selftest.py` (pin: a card with 1 cached + 1 uncached fragment
   → only the uncached fragment reaches a translate lane; accounting still balances).
5. **Live-validate** on a genuinely-partial giant card (e.g. `ka`'s 2 missing heal groups —
   see [H055-Opus_SanskritLexicography_pwg_audit_tail_02.07.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H055-Opus_SanskritLexicography_pwg_audit_tail_02.07.26.md))
   with a **dated SAFE store backup first** and **`--merge` promotion only**.

## Guardrails (unchanged, non-negotiable)

- **Branch contention is real** — an autonomous account cycles/deletes branches mid-session.
  Never push `master` directly; branch + PR for every tracked-file change; commit early.
  If a push is rejected or a worktree vanishes, use
  [`/branch-contention-recover`](https://github.com/gasyoun/SanskritLexicography).
- **The RU store `src/pwg_ru_translated.jsonl` is gitignored, local-only, wiped once already
  this week.** Before ANY promotion: `cp` a dated
  `pwg_ru_translated.jsonl.SAFE_<desc>_<yyyymmdd>.keep`. ALWAYS `--merge`, never a bare
  overwrite. **Rebuild the TM (`translation_memory.py build`) after every promotion** or it
  goes stale (stale = misses, never wrong reuse — but you lose the savings).
- **Model provenance:** the `sonnet` alias DRIFTS — read the resolved version from the run's
  own workflowProgress and pass `--gen-model-version` explicitly on every promotion.
- ≤3-wide Workflow concurrency, always. `csl-orig` is irrelevant here.

## Definition of done

- Fragment-level TM built + `--tm` skips cached fragments inside a partial card (live-proven
  token drop on one real giant card, with per-key outcomes in
  [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)).
- `window_selftest.py` green with a new pinning test.
- Store SAFE-backed-up; TM rebuilt; delivered by PR.
- Session closed with `/handoff`; this handoff's GTD row flipped.

Full journal: [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md).
Prior handoff: [`H038-Sonnet_RussianTranslation_pwg_selfheal_fixes_02.07.26.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/archive/H038-Sonnet_RussianTranslation_pwg_selfheal_fixes_02.07.26.md).

_Dr. Mārcis Gasūns_
