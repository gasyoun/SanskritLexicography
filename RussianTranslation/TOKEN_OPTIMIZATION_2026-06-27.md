# Token optimization for the pwg_ru Max bulk run — findings & decisions (2026-06-27)

Goal set by M.G. (2026-06-27): the PWG→Russian bulk run on **Sonnet/Max** must
sustain **weeks of continuous work, week after week** — not burn the Max weekly
token quota in 3–4 days. One full giant root at the current config ≈ **9–10 M
tokens**, which is too much. This doc records the measured cost driver, the
ranked optimizations, the decision taken, and the failures hit along the way.

> Companion to [`PILOT_COST.md`](PILOT_COST.md) (the $/quota model) and
> [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md) (the run loop).
> Cross-reference: [`HANDOFF_2026-06-25_pwg_ru_max.md`](HANDOFF_2026-06-25_pwg_ru_max.md).

---

## The question

> "10M tokens for one root is too much even in Sonnet mode. What optimisation of
> tokens can be made, so the work lasts all week, week after week, instead of
> stopping after 3–4 days when the Sonnet/Max quota is burned?"

## The measurement (where the tokens actually go)

Per-agent token usage from the gam smoke transcripts
(`subagents/workflows/wf_d2112a99-48a` + `wf_5cc1a120-d56`):

| agent (stage) | uncached in | output | **cache_read** | cache_create | asst turns | Read calls |
|---|---|---|---|---|---|---|
| translate (giant head) | 28 | 8 693 | **799 674** | 160 365 | 22 | 12 |
| translate (mid) | 21 | 4 231 | 572 133 | 97 172 | 15 | 7 |
| translate (small) | 11 | 2 684 | 62 464 | 107 466 | 5 | 2 |
| judge | 19 | 4 668 | 360 452 | 146 548 | 13 | 4 |

**Finding 1 — the cost is `cache_read`, and `cache_read ≈ context_size ×
number_of_turns`.** Uncached input is trivial (11–28 tok); output is modest
(2–10 k). The dominant term is `cache_read`, up to **800 k for a single agent**.

**Finding 2 — the multiplier is TURNS, not prompt size.** The expensive agents
take **11–22 assistant turns** and call the **Read tool 4–12 times**, re-reading
`raw.txt` / `portrait.json` repeatedly. Every turn re-bills the whole ~100 k
cached context. A 22-turn agent pays ~22 × 100 k of cache_read. The static
prompt (CONV + 5 HARD RULES + RENDERING GUIDANCE, ~6–8 k tok) and prompt caching
are **not** the problem — caching is already on (that is why uncached `in` is ~20).

**Finding 3 — this was not in PILOT_COST.md.** That doc anticipated *cache on*
and *sampled judge*, but assumed agents are roughly single-turn. The turn-
multiplication from tool-driven file re-reading is a new, unbudgeted driver.

## Ranked optimizations

| # | Lever | Mechanism | Est. saving | Quality trade |
|---|---|---|---|---|
| 1 | **Single-turn agents via inlined inputs** | Bake each sub-card's `raw.txt`+`portrait.json` into the prompt (the generator has fs); instruct "emit the card directly, call NO tools". Kills 4–12 Read calls + ~10–20 turns/agent. | **cache_read ↓ 5–8×** | none (same content, inline) |
| 2 | **Drop per-card LLM judge → free deterministic gates + sampled judge** | `audit_translation.py` + `nws_split.py` already catch markup/coverage/NWS-misattribution at **0 tokens**. Run them on every card; LLM-judge only a 5–10 % sample + any deterministic-gate flag. Removes ~half the agents. | **total ↓ ~2×** | mild — register/discrimination sampled, not per-card; floored by deterministic gates |
| 3 | **Single-turn judge (when sampled)** | Review the inlined card; no source re-read. | judge cache_read ↓ several× | none |
| 4 | **Batch small sub-cards per translate call** | Many sub-cards are ~9 output lines; batch ~5 small ones per agent → amortize the static prompt 5×. Heads stay solo. | small-card tail ↓ 20–40 % | slight (shared context) |
| 5 | **Opus only on deterministic-gate fails / sample** | Already near-policy; make it explicit. | marginal | none |

**Combined (1+2+3):** ~10 M/root → **~1.5–2.5 M/root (4–6×)** — the difference
between "burns out in 3–4 days" and "runs for weeks."

## Open metering question (affects how hard #1 matters)

How the **Max weekly quota** counts `cache_read` is unmeasured (PILOT_COST §6
item 1 — "never recorded numerically"). If it counts cache_read at full weight,
#1 is decisive; if at ~0.1× (the API price ratio), #1 still helps but #2 leads.
Either way #1 is strictly positive. The tyaj baseline run + the first optimized
run will bracket this.

## Failures / dead-ends hit (kept so the next session doesn't repeat them)

- **Bash `node run_pilot_wf.js` is impossible.** It is a Workflow script (uses
  `phase()`/`pipeline()`/`agent()` harness globals), not a Node program —
  `ReferenceError` on line 1 of the body. Must run via the Workflow tool.
- **Workflow tool has no `node:fs`.** The committed harness's `readFileSync` of
  the schema + manifest fails in-sandbox. Fix: inline both as literals; agents
  read their own inputs. → [`src/pilot/run_pilot_wf.workflow.js`](src/pilot/run_pilot_wf.workflow.js).
- **Markup-stripping fidelity fail.** First smoke: Sonnet rendered `german` as
  clean prose, dropping `{#}`/`<ls>` → `audit_translation.py` 0/3 (LS-LOSS
  0/150). Root cause: HARD RULE 3 enforced sigla fidelity only at content level;
  schema said "trimmed". Fix committed `c69ac30` (MARKUP DELIMITERS VERBATIM +
  schema reword). Re-run: 2/2 gates green.
- **Stray backticks broke the Workflow parser.** Wrapping `` `german` `` inside
  the TR template literal closed the string; `node --check` passed but the
  Workflow parser flagged `Unexpected token (218:589)`. Fix: no backticks in
  prompt prose.
- **Transient `Connection closed mid-response`** dropped one translate agent
  (`gam`/`tyaj` head). Not a logic fault — re-queue.

## Baseline (unoptimized tyaj, A in the A/B)

`run_pilot_wf.run.js` on all 14 tyaj sub-cards, current config (per-card Sonnet
judge + Opus-on-reject, agents read their own files):

- **28 agents · ~998 834 subagent_tokens · 88 tool calls · 6.6 min wall.**
- **3 / 14 agents failed** on transient `Connection closed mid-response`
  (`tr:tyaj~~h0_00_pwg00` head, `tr:tyaj~~h0_zz_pw`, `judge:…_01_sama_bi`).
- ⇒ ~1 M tokens for one *small* (14-subcard) giant root. gam (230) extrapolates
  to **~16–20 M** on this metric — confirms the run is quota-bound.

**Finding 4 — ~10–20 % transient agent-failure rate.** Across gam (1/7) and tyaj
(3/14) runs, agents die on `Connection closed mid-response`. For a multi-week
unattended run this MUST be handled: a failed agent returns `null` and the card
silently vanishes. The optimized harness adds **1 automatic retry** per stage +
a post-run **missing-key re-queue**.

## Decision (M.G., 2026-06-27)

- **Optimization tier: BALANCED.** Apply (1) single-turn inlined inputs
  [quality-neutral] + (2) drop the per-card LLM judge → free Python gates
  (`audit_translation.py` + `nws_split.py`) on EVERY card + a **10 % Sonnet
  judge sample** and any Python-gate flag; Opus only on flags. Target
  **~1.5–2.5 M → ~0.2–0.4 M per small root** (the bulk pass becomes translate-
  only + free gates).
- **Sequencing:** let the tyaj baseline finish (done, above), then re-run tyaj
  **optimized** as the clean A/B "after" on the same root before scaling.
- **Reliability:** add 1 retry + re-queue for the transient API failures
  (Finding 4).

### Architecture of the optimized run

1. **Bulk translate** — single workflow, `model=sonnet`, **inputs inlined**
   (no Read calls), **1 retry** on failure. No judge, no Opus in this pass.
2. **Free deterministic gates** on 100 % of cards — `run_real_test.py audit`
   (renders `.merged.md`, NWS owner-map quarantine) + `audit_translation.py`
   (markup/coverage/Russian-present). Zero tokens. Re-queue any fail.
3. **Sampled LLM judge** — a separate small workflow over ~10 % of cards +
   every deterministic-gate flag; Sonnet judges, Opus adjudicates only its
   rejects. The only LLM QA spend in the optimized path.
4. **Glue** — `root_glue_translated.py <root>` → `<root>.NESTED.md`.

## A/B RESULT — tyaj baseline vs optimized (measured 2026-06-27)

`cache_read` (the real quota driver — see Finding 1) and turns, from the agent
transcripts:

| metric | baseline | optimized | reduction |
|---|---|---|---|
| agents | 28 | 14 | 2.0× |
| assistant turns | 138 | 47 | 2.9× |
| **Read calls** | 60 | **19** | 3.2× |
| **cache_read** | 2 737 196 | **847 540** | **3.2×** |
| cache_create | 1 676 479 | 717 690 | 2.3× |
| output | 46 132 | 25 151 | 1.8× |
| subagent_tokens (harness metric) | 998 834 | 482 398 | 2.1× |
| wall-clock | 6.6 min | 2.5 min | 2.6× |
| transient failures | 3 | **0** | — |

**Net: ~2× on the headline token metric, ~3.2× on cache_read, 2.6× faster, and
the retry eliminated the API-failure dropouts.** The single-turn directive cut
Reads 60→19 but not to 0 — **some agents still re-read files despite the inlined
content** (residual lever: restrict the Read tool to force true single-turn).

### Quality (deterministic gates on the optimized translate-only output)
- NWS owner-map gate: **PASS** (0 F12 misattribution).
- Fidelity gate: **12/14 clean.** Failures = (a) `pwg00` giant head dropped
  ~94 % of citations in one pass (LS 7/125, SAN 12/91), (b) `ni` tiny card
  SAN 2/3 borderline. Both **caught**, both re-queue.

**Finding 5 — giant HEAD cards (`*_pwg00`, ~1 per root) overflow a single pass**
and shed their citation apparatus. The deferred head-splitter is now required
*for heads specifically*; the ~43 k normal sub-cards are fine single-turn. Route
heads to a split / multi-pass / higher-effort lane; keep the cheap single-turn
path for the body.

### Verdict
Balanced delivers the weeks-not-days goal at ~2–3× with quality held on normal
cards. Remaining headroom: (i) restrict Read tool → true single-turn (push the
residual 19 reads → 0); (ii) head-splitter for `*_pwg00`; (iii) optional
Aggressive batching of tiny sub-cards. The sampled-judge pass (step 3) is built
into the plan but not yet run.
