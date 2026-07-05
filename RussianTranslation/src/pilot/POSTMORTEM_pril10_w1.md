# Post-mortem — `pril10_w1` nominal-window cost/latency blow-up (H189)

_Created: 05-07-2026 · Last updated: 05-07-2026_

> **Model provenance.** Generation of the aborted run: **Sonnet 5 (`claude-sonnet-5`)** —
> every `agent()` call in [`run_pilot_wf.opt2.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
> pins `model:'sonnet'`. Forensics, root-cause, fix, and this write-up:
> **Opus 4.8 (`claude-opus-4-8`)**. All `$` figures use
> [`parse_workflow_cost.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py)'s
> hardcoded **Sonnet 4.x** rates ($3 / $15 / $3.75 / $0.30 per-M for input / output /
> cache-write / cache-read); Sonnet 5 list rates may differ, so treat **$ as
> order-of-magnitude**. The **token counts and the relative cost split are exact and
> model-independent.** This doc is the verified counterpart to the
> [H189 handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H189-Opus_RussianTranslation_pwg_ru_nominal_cost_blowup_postmortem_05.07.26.md).

---

## TL;DR

The first nominal production window — the **8 largest PWG headwords**
(`kAla, rasa, rUpa, brahman, arTa, sva, manas, antara`) — burned **42,316,604 tokens /
~$79.83 and produced ~3 of 8 cards in ~20 min** before it was killed by hand. Every
number in the incoming handoff's §3 was **reproduced exactly** from the transcripts, and
every §4 hypothesis is **CONFIRMED**. The dominant cause: in nominal mode all 8 cards were
routed to the fragment lane (`BATCHES = 0`), which grouped their **448 fragments into 174
tiny agent() calls** (~2.6 fragments/call) — so the ~27 K-token framework prompt was
re-cached ~230 times and **cache-write alone was 60 % of the bill**. The batching that
whole-card mode uses to amortize the framework bought nothing.

Five fixes landed (all lang-agnostic → SHARED); all pinned by
[`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)
(68/68 green):

1. **Presplit-lane re-batching** — group presplit-primary cards at 60 citation-units / 18
   fragments per call (was 12): **174 → 69 groups on `pril10_w1`**, and on real `gam` its
   2 presplit giants dropped **18 → 6 agent calls**.
2. **Kill-gate recalibration** — floor 120 s → 45 s, ceil 480 s → 180 s (MG: ">60 s
   suspicious, >3 min unacceptable").
3. **Live budget kill-switch** — the window self-aborts and requeues once agent() calls
   exceed `MAX_AGENTS = max(40, ⌈expected × 3⌉)`.
4. **Harness-size guard** — the generator warns + prints an exact key-disjoint split when
   the harness exceeds 480 KB (the `F-harness-size-limit` scriptPath cap).
5. **Preflight cost gate** — [`perf_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py)
   now estimates tokens / $ / per-card cost and flags (or, with `--refuse-over-cost`,
   refuses) a window above a per-card ceiling.

**The load-bearing lesson:** the amortization fix cuts the presplit lane ~2.5×, but 8
`kAla`-class heads are *intrinsically* expensive per card — no grouping makes them cheap.
Viability comes from **not running a window of monsters as "bulk" at all**: the cost gate
(fix 5) is what keeps such windows out of the pipeline. Typical cards were never the
problem — the batched verb runs cost ~36 K tokens/card.

---

## 1. Verified economics

Re-derived with `python src/pilot/parse_workflow_cost.py <wA> <wB> <wC>` over the three
sub-window transcript dirs (`wf_34133e5b-777`, `wf_41d050b6-722`, `wf_1640c173-628`):

| | tokens | $ (Sonnet 4.x) | % of $ |
|---|---:|---:|---:|
| fresh input | 5,306,817 | $15.92 | 20 % |
| **cache-write** | **12,738,510** | **$47.77** | **60 %** |
| cache-read | 23,668,772 | $7.10 | 9 % |
| output | 602,505 | $9.04 | 11 % |
| **TOTAL** | **42,316,604** | **$79.83** | |

Matches the handoff's §3 to the digit. **Per intended card: ~5.29 M tokens / ~$9.98.**

### Per-agent forensics (230 agents, 581 assistant turns)

| metric | value |
|---|---|
| agents spawned | **230** (wA 74 + wB 99 + wC 57) vs 174 estimated (**+32 %**) |
| assistant turns | 581 → **2.53 turns/agent** (heavy in-agent retry) |
| duration (s) | median 20 · mean 34 · p90 54 · **max 390 (6.5 min)** |
| agents > 60 s / 120 s / 180 s / 300 s | **19 / 10 / 8 / 2** |
| max single agent | **902,914 tokens over 10 turns, only 9,114 output** (pure retry waste) |
| multi-turn agents | **78 %** (mode = **3 turns**; 1-turn only 20 %) |
| **first-turn (framework) cache-write** | **5,819,916 tok = 46 % of all cache-write ≈ $21.82 = 27 % of the whole bill**, at ~25.3 K tok/agent × 230 |

### Fragment structure (the mechanism)

From the harness `FRAGS`/`BATCHES` consts: **`BATCHES = 0`** — all 8 cards presplit — into
**448 fragments / 174 groups** (`= agent_expected_after_tm = 174`), ~2.6 fragments/group.

| head | fragments | groups (old, budget 12) |
|---|---:|---:|
| kAla | 130 | 32 |
| antara | 59 | 32 |
| rasa | 76 | 27 |
| brahman | 47 | 21 |
| sva | 34 | 19 |
| arTa | 41 | 18 |
| rUpa | 42 | 15 |
| manas | 19 | 10 |

Fragment weight (`1 + <ls>`) is bimodal: **median 2, p90 14, max 180** (one fragment with
179 citations). 6 fragments exceed weight 90 — themselves un-emittable in one call.

---

## 2. Hypotheses — all CONFIRMED

**1. 🔴 Batching amortization defeated by per-fragment agents — DOMINANT, CONFIRMED.**
8 cards → 174 groups → ~230 agents (~29/card). The `_group_by_budget` call built each
group at `SELFHEAL_GROUP_BUDGET = 12` citation-units, packing only ~2.6 fragments. Each of
the 174 groups re-establishes the ~25.3 K framework prompt cache → framework re-cache =
**46 % of cache-write (5.82 M tok, ~$21.82)**, and cache-write overall = **60 % of the
bill**. The whole point of "batched + masked" (amortize the framework across many cards)
was nullified because the fragment lane grouped at 12, not near the whole-card ceiling.

**2. 🔴 Presplit explodes on exactly these heads — CONFIRMED.** `BATCHES = 0`: every one of
the 8 most polysemous words in the language tripped the citation- or sense-presplit trigger
and went to the fragment lane. 448 fragments total; `kAla` alone shatters into 130. The
window was chosen as the *heaviest possible* first window (top-8 by DCS score) — worst-case,
not representative.

**3. 🟠 Kill gate far too loose — CONFIRMED.** Constants were
`FACTOR 2 · BASE 30 s · SLOPE 45 ms/byte · FLOOR 120 s · CEIL 480 s`. The budget formula
`min(480 s, max(120 s, 2·(30 s + 45 ms·skelBytes)))` gave every call **2–8 min**. The
2-min floor meant a tiny fragment could never be killed before 2 min; the worst agent ran
**390 s (6.5 min)** inside the ceiling, and **8 agents ran > 3 min**. MG's rule (">60 s
suspicious, >3 min unacceptable") was violated by construction.

**4. 🟠 Retry/heal multiplication — CONFIRMED.** 581 turns / 230 agents = 2.53; **78 % of
agents took > 1 turn, mode 3**. The pathological agent retried **10 times for 903 K tokens
and 9 K output**. Every retry re-pays the framework cache-write (compounding hypothesis 1),
and the 230-vs-174 agent gap is the binary-split/heal cascade on the pathological fragments.

**5. 🟡 No cross-agent prompt-cache reuse — CONFIRMED by construction.** Each agent() is a
fresh subagent context; its ~25.3 K framework cache-write is discarded at agent end and
re-paid by the next of the 230 calls. Nothing shares a cached prefix across a window's
agents. (Whether the runtime *could* share one is unknown and not assumed — see §4.)

---

## 3. The fix that landed

All in [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
+ [`perf_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py),
pinned in [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py),
classified SHARED in [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
(`presplit_lane_amortization_and_budget_guards_h189`).

| # | fix | mechanism | measured effect |
|---|---|---|---|
| B | **presplit-lane re-batching** | presplit-primary cards group at `PRESPLIT_GROUP_CITE_BUDGET=60` **and** `PRESPLIT_GROUP_SENSE_CAP=18` (both under the proven-safe whole-card 90/20 ceiling), via `_group_by_budget(..., count_cap=)`. Heal-of-a-failed-whole-card keeps the conservative budget 12. | `pril10_w1` **174 → 69 groups**; real `gam` giants **18 → 6 agents**. Framework re-cache ~4.7 M → ~1.9 M tok. |
| C1 | **kill-gate recalibration** | `FLOOR 120 s → 45 s`, `CEIL 480 s → 180 s`, `BASE 30 s → 20 s`. Kill → the abandoned call's cards fall to the fragment lane / binary-split (**requeued, never dropped**). | tiny fragment hard-killed ~60–70 s; nothing past 3 min. |
| C4 | **live budget kill-switch** | harness counts agent() calls; past `MAX_AGENTS = max(40, ⌈expected × 3⌉)` every call throws `BudgetExceeded` (0 tokens, not an `isKill` → no more fragment spawns); remaining cards null with a `budget-kill-switch` reason for the normal requeue. `summary.budget_kill_switch_tripped` surfaces it. | a 174-estimate window aborts at ~522 calls; the real 230 would have been well within, but a true runaway now self-terminates instead of a manual kill. |
| C3 | **harness-size guard** | at write time, if the harness > `MAX_HARNESS_BYTES = 480 KB` the generator prints a concrete key-disjoint split (N sub-windows, exact `--keys=` each); `--refuse-oversize` makes it a hard error. | surfaces `F-harness-size-limit` at generation, not launch. |
| C2 | **preflight cost gate** | `perf_preflight.py` estimates tokens/$ (184 K tok, $0.347/agent from this run, ×1.35 realism) and a **per-translated-card cost**; flags `OVER-CEILING` above `$2/card` or `$25/window`; `--refuse-over-cost` exits nonzero. | flags `pril10_w1` (~$4/card **even post-fix**) → routed to a human-budgeted lane; passes cheap high-count windows (`as`: $0.11/card). |

Also fixed in passing: `_slp1_lex_for_key` crashed on an **empty-list portrait `[]`** (the
real `tyaj~~h0_zz_pw` / addenda shape) via the PR #155 `nominal_keymap` emission — a latent
generation crash for any nominal window containing such a card, surfaced only because a
fresh checkout's selftest aborts on missing `gam` data before reaching that test.

---

## 4. Residual & forward guidance

- **Monster cards need their own lane.** Amortization makes *moderate* presplit cards
  cheaper, but a `kAla` (130 fragments) is intrinsically expensive. The cost gate flags
  such windows; the intended follow-up is a **human-budgeted lane** for the `kAla`-class
  handful, keeping them out of the bulk pipeline (handoff §5.B option 4). The first nominal
  window should be *typical* heads, not the top-8 by size.
- **Monster fragments (weight > 90) should sub-split.** 6 fragments carry > 90 citations
  (max 179); each is alone in its group and can still blow one call. A within-sense
  citation-batch sub-split for fragments above a threshold would remove the retry tail;
  until then the recalibrated kill gate + binary-split bound them.
- **Framework shrink / cross-agent cache (hypotheses 5, §5.B option 2)** are the next lever
  but runtime-dependent (whether a cached system prefix can be shared across a window's
  agents is unverified). Not attempted here; the amortization + gate fixes are runtime-safe.
- **TM-resolved cards still inline their input**, bloating the harness (gam: 124/127 cached
  yet 1.1 MB). Not translated, but they push the file over the size cap — a candidate future
  optimization (omit `INPUTS` for TM-resolved keys).
- **The $ rate basis is Sonnet 4.x.** Reconfirm `parse_workflow_cost.py`'s rate table and
  the cost-gate constants against Sonnet 5 list rates before trusting absolute $ (token
  counts and per-card ratios are already model-independent).

---

## 5. How to reproduce / validate

```
# economics (exact)
python src/pilot/parse_workflow_cost.py <wf_34133e5b-777> <wf_41d050b6-722> <wf_1640c173-628>

# the fix, end-to-end
python src/pilot/window_selftest.py          # 68/68 green (incl. the 6 H189 tests)
python src/pilot/lang_parity_check.py         # 20 entries, no drift
python src/pilot/perf_preflight.py gam han as vid   # cost columns + gate verdicts
```

Transcripts:
`C:\Users\user\.claude\projects\C--Users-user-Documents-GitHub\8f358868-0537-4497-a2f8-08cb4a0a7583\subagents\workflows\`
(`wf_34133e5b-777` = wA `kAla,rasa` · `wf_41d050b6-722` = wB `brahman,antara,sva` ·
`wf_1640c173-628` = wC `arTa,rUpa,manas`).

_Dr. Mārcis Gasūns_
