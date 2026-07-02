# Handoff — pwg selfheal/binary-split/output-budget/partial-credit fixes, live-validated

_Created: 02-07-2026 · Last updated: 02-07-2026_

**For:** a fresh chat. **Branch:** work off `master` directly — `feat/pwg-en-fu1-phase0` was
merged and deleted mid-session (2026-07-01); it no longer exists.
**Orchestration:** Sonnet 5 (`claude-sonnet-5`). **Generation:** RU = the `sonnet` alias.
**Live dashboard:** https://gasyoun.github.io/SanskritLexicography/ (rebuilt + republished
this session — 51 roots / 14,996 senses).

## ⚠️ Read first — branch contention is real, store is local-only

Same warning as every prior handoff in this series: a second (autonomous) account works this
repo concurrently and cycles/deletes branches mid-session (confirmed again today —
`feat/pwg-en-fu1-phase0` vanished from origin between two of my own pushes). **Commit only via
a fresh git worktree off `origin/master`, never the main checkout.** Two of my own worktrees
disappeared entirely mid-session this time too (external cleanup, not the autonomous account) —
if that happens to you, `git worktree prune` then re-`git worktree add` off `origin/master`;
any *uncommitted* edits in the vanished worktree are lost, so commit early and often.

The canonical translated store
[`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_translated.jsonl)
is **gitignored — local-only, not backed up anywhere except this machine.** It was accidentally
wiped once already (2026-07-01, 10,122→472 rows via a non-merge `promote_final_cards.py`
overwrite from the other account) and recovered from a `.legacy.bak`. A fresh dated safety copy
was made this session: `src/pwg_ru_translated.jsonl.SAFE_full10614_20260702.keep` (10,614 rows,
after today's promotions — see below). **Always use `--merge` with `promote_final_cards.py`
for per-root/per-headword work; never a bare full-overwrite run.**

## What's done this session

**Four PRs landed on `master`, all fixing the same underlying pattern — a citation-dense card
or its heal fallback failing in ways the harness swallowed silently instead of surfacing:**

1. [PR #35](https://github.com/gasyoun/SanskritLexicography/pull/35) — `--selfheal`
   fragment-grouping: groups fine-grained `autosplit_requeue` fragments into fewer heal
   `agent()` calls, sized by **citation-weighted units (1+`<ls>` count)**, not bytes.
2. [PR #37](https://github.com/gasyoun/SanskritLexicography/pull/37) — `--binary-split`
   (bisect a whole-batch failure instead of flat-retrying) + `--output-budget=N` (size main
   batches by citation-weighted output, not input bytes) + `healGroup` bisection safety net.
3. [PR #38](https://github.com/gasyoun/SanskritLexicography/pull/38) — root-caused and fixed
   the `brū`/`pwg00` holdout: `autosplit_requeue.plan()` was gluing a verb's conjugation-table
   **header** onto sense 1 without ever counting the header's own citation density against
   `LS_BUDGET` — the "budgeted" first fragment was silently the densest in the card. Also
   hardened `translateBatch()` against a hard `agent()` failure that was crashing the whole
   workflow.
4. [PR #40](https://github.com/gasyoun/SanskritLexicography/pull/40) — found (via live
   investigation on `kāla`) that giant flat headwords with 40+ heal groups have near-zero
   joint success probability under the all-or-nothing "every group must succeed" design (PR
   #38's crash-guard also had a scope bug: it wrapped `resolveGroup` AND `selfHeal` in one
   try/catch, so a hard failure on the main attempt skipped `selfHeal` entirely). Fixed:
   independent exception guards at every `agent()`-touching call site, plus `selfHeal`/
   `autosplit_requeue.cmd_merge()` now return **partial credit** (`partial`/`missing_groups`
   markers) instead of all-or-nothing.

**Live validation, in order:**
- `brū` (23 subcards, the original FU1 EN holdout): **23/23 resolved, 0 nulls** after PR #38.
- `kāla`/`ka`/`śrī` (the 3 biggest non-root nominal headwords — no rootmap, single flat card
  each, previously **zero** RU coverage): all three now translated and **promoted** to the
  store (10,122→10,614 rows). `śrī` and `kāla` resolved on the whole-card attempt alone (no
  heal needed — confirms dense-card failure is stochastic variance, not a hard ceiling: this
  exact `kāla` card had failed 3 times pre-fix). `ka` (327 `<ls>`, the densest) needed
  `selfHeal` and landed PR #40's actual target case: `partial:true, missing_groups:2/41` — a
  real, mostly-complete card (39/41 groups, ~220 senses) where the pre-fix code returned
  nothing.
- Dashboard rebuilt (`build_article_site.py`) and republished to `gh-pages` — live site now
  reflects `brū` + the 3 new headwords.

**Total live-validation cost this session: ~12M tokens** across all runs (diagnosis + fixes +
re-validation + final translations). Most of that was iterative debugging on `kāla`
specifically (3 escalating failed attempts before the root cause was found) — a future similar
investigation should budget for that pattern (a stubborn card usually means a real bug, not
"just retry more").

## Known gaps / next steps

1. **All 4 fixes are on `master` and unconditionally safe to depend on** — but only `brū` and
   `kāla`/`ka`/`śrī` have been live-validated end-to-end. The wider **RU/EN dense-residual
   backlog** (roots flagged in `.ai_state.md` §"Next Steps") has NOT been re-run with the new
   stack yet. Re-running it should be strictly better than before (same defaults when the new
   flags are omitted; opt-in `--selfheal --binary-split --output-budget=N` for anything that
   previously failed).
2. **G5 human review** — all 492 new rows (and everything promoted before them) sit at
   `review_status='ai_translated'`, not `'approved'`. `export_interop.py`'s
   `approved_store()` gate keeps unreviewed AI output out of the citable edition by design.
   Nothing downstream needs code work here; it's a human review queue.
3. **`ka`'s 2 missing groups** — `PR #40`'s partial-credit path means `ka` is usable but not
   100% complete. A targeted requeue of just those 2 groups (not a full re-run) would close
   the gap; the missing-fragment-keys mechanism (`autosplit_missing_<lang>_<root>.json`) is
   built for `autosplit_requeue.cmd_merge`'s standalone path but `selfHeal`'s inline path
   doesn't currently persist which specific groups failed anywhere retrievable — that's a
   small follow-up if this specific gap matters (dashboard already shows `ka` as available;
   the 2 missing senses are just absent, not wrong).
4. **Efficiency levers are proven; no further blanket levers are queued.** Don't invent a
   "#6" — if a future card struggles, isolate to the single failing fragment/group first
   (see PR #38's lesson: "citation-dense card fails" was a `plan()` bug, not model difficulty)
   before assuming it needs a new mechanism.

## Resume commands

```sh
# fresh worktree (feat/pwg-en-fu1-phase0 no longer exists — use master)
git fetch origin master
git worktree add --detach ../SanskritLexicography-work origin/master

# generate a harness with the full validated stack for a root or nominal headword
python src/pilot/gen_opt_harness2.py <root> --selfheal --binary-split --output-budget=60 --out=<path>
python src/pilot/gen_opt_harness2.py <label> --nominal --no-grammar --keys=<safe_name> --lang=ru \
    --selfheal --binary-split --output-budget=60 --out=<path>

# run via the Workflow tool, then promote
python src/promote_final_cards.py --glob 'wf_output.<tag>.*.json' --merge

# rebuild + republish the dashboard
python src/pilot/build_article_site.py
# copy article_site/{articles.js,index.html,md/,roots/} onto a gh-pages worktree, commit, push
```

Full journal: [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md).
Prior handoff: [`HANDOFF_2026-07-01_pwg_efficiency_selfheal.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/HANDOFF_2026-07-01_pwg_efficiency_selfheal.md).

_Dr. Mārcis Gasūns_
