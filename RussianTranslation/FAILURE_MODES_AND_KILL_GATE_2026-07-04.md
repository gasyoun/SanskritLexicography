# Whole-card StructuredOutput failure modes + the wall-clock kill gate

_Created: 04-07-2026 · Last updated: 04-07-2026_

Written after H155 (the `tyaj~~h0_zz_pw` ~7-minute stall) as MG's follow-up:
**"card complexity is sense-count, not citations — that's just a single case.
What other cases are possible? Plan in advance. And add a gate: if a
translation runs too long, kill it — don't wait for miracles."** This doc
answers both: (1) a forward-looking taxonomy of every whole-card/whole-batch
StructuredOutput failure driver, grounded in the
[`PIPELINE_HISTORY.md`](PIPELINE_HISTORY.md) timeline, and (2) the design +
calibration of a per-`agent()`-call wall-clock kill gate as the backstop for
the drivers we *haven't* characterized yet.

## The unifying failure model

A single `agent()` call carrying a StructuredOutput schema **stalls** (burns
the internal StructuredOutput retry cap, ~5 attempts, each re-emitting the
same doomed output) when the model cannot produce a valid `{cards:[…]}`
object at the root. That happens when the required **output** is too large or
too complex for the model to emit coherently within its output-token budget.
The tell (H155): the paired error `root: must have required property 'cards'`
+ `root: must NOT have additional properties` — i.e. the model emitted a bare
card object (or wrong wrapper) instead of the `{cards:[…]}` envelope, because
it ran out of room to build the whole structure.

**Output complexity is a SUM of independent contributors. Any budget keyed on
one contributor is blind to the others** — which is exactly why the
citation-only presplit metric (`1+<ls>`) waved through a 35-sense card whose
citations were trivial. Every fix so far has been "we discovered the *next*
contributor." The taxonomy below enumerates them so we stop rediscovering
them one production stall at a time.

## Taxonomy of output-complexity drivers

| # | Driver | What it is | First seen | Caught by | Status |
|---|--------|-----------|-----------|-----------|--------|
| 1 | **Citation density** | `<ls>` count per card; long citation lists per sense | Phase 0/4 — 150–200+ `<ls>` `pwg00` heads failed even solo | presplit citation trigger (`1+<ls> > OUTPUT_BUDGET`) + citation-weighted batch sizer | ✅ handled |
| 2 | **Sense / fragment count** | numbered senses + prefix sub-blocks = one `sense` object each | H155 — `tyaj~~h0_zz_pw`, 35 senses / 11 `<ls>` | presplit **sense** trigger (`frag_count > SENSE_PRESPLIT_BUDGET`, H155) | ✅ handled per-card · ⚠️ **batch-level gap** (see #6) |
| 3 | **Gloss-prose volume** | total `{%…%}` chars ≈ masked skeleton bytes; the model ECHOES german **and** writes russian ≈ 2× the skeleton | latent — a card with few senses/citations but long verbose definitions is large in *output tokens* | nothing structural today (input-byte size was refuted as a splitter heuristic in Phase 4, but that was INPUT bytes incl. portrait, not output gloss volume) | 🩹 kill-gate backstop only |
| 4 | **Masked-token count** | `{Tn}` placeholders to reproduce verbatim, in order, in both fields | latent | partially — `accept()` fidelity guard rejects miscounts (a *different*, caught failure), but a `{Tn}`-heavy card can still stall before that | 🩹 partial + kill-gate backstop |
| 5 | **Structural nesting / multi-layer** | multiple `<hom>` homonyms or stacked `=== LAYER: ===` blocks (PW/SCH/PWKVN addenda) | `_zz_pw` / `_zz_sch` class | insofar as layers inflate fragment count (→ #2); a 2-layer card with moderate senses each is not directly gated | 🩹 partial + kill-gate backstop |
| 6 | **Batch-level SUM of any of the above** | several individually-fine cards whose combined output exceeds the limit | Phase 0 (original per-card-budget failures) | batch sizer sums **citations** only (`OUTPUT_BUDGET`); blind to summed **senses / gloss volume** | ⚠️ **gap — fixed this session for senses** (see below) |
| — | *(non-stall failure classes, listed to avoid conflation)* | model calling file-read tools (Phase 2 yuj blowup, fixed: `tools:[]`); concurrency 429 transient nulls (Phase 3, process fix ≤3-wide); gate false-positives (Phases 5–6) | — | — | ✅ out of scope here |

**The pattern across #1–#6:** they are all the same disease (too much output),
surfacing through whichever attribute happened to spike first. A truly robust
structural fix is a *composite* complexity estimate; but each additive change
to the batch sizer risks re-calibrating the A/B-tuned `OUTPUT_BUDGET`, so we
extend conservatively (per-card presplit triggers + a sense-aware batch
sizer) and lean on the kill gate for the long tail.

## Two-layer defense

1. **Structural triggers (proactive).** Route a card to the fragment lane
   *before* running it when a known driver predicts whole-card failure. Cheap,
   deterministic, no wasted tokens. Covers #1 (citations) and #2 (senses)
   today; #6 (batch senses) added this session. Can never cover an
   *un-characterized* driver.
2. **Wall-clock kill gate (reactive backstop).** For every driver we haven't
   turned into a structural trigger (#3, #4, #5, and whatever #7 turns out to
   be), detect the stall *at runtime* — "this call is taking far longer than a
   call of its complexity should" — abandon it, and fall to the bounded
   fragment lane instead of waiting out the full retry cap. This is MG's "if
   it runs too long, kill it, don't wait for miracles."

## Kill-gate design

### Runtime constraints (probed 04-07-2026, `probe_runtime.js`)

| Capability | Result | Consequence |
|---|---|---|
| `setTimeout` / `clearTimeout` | ✅ available | a **relative** timeout is possible — no `Date.now()` needed (which is banned in Workflow scripts, would break resume) |
| `Promise.race([...])` | ✅ works | `Promise.race([agent(...), timeout])` cleanly returns whichever finishes first |
| `AbortController` | ❌ undefined | **cannot truly cancel** the underlying agent — a killed call keeps running in the background until it dies on its own retry cap. But the harness stops *blocking* and the card recovers immediately via fragments. This is the accepted cost. |
| `performance` | ❌ undefined | no high-res timer; irrelevant given `setTimeout` suffices |

### Mechanism

Wrap every schema-bearing `agent()` call in a race against a relative
`setTimeout`:

```
budgetMs = clamp(KILL_FLOOR_MS, KILL_FACTOR × expectedMs(units), KILL_CEIL_MS)
Promise.race([ agent(prompt, opts), rejectAfter(budgetMs) ])
  → on timeout: noteFail(k, 'kill-timeout …') and route to the SAME fallback
    as a hard agent() failure (selfheal for a batch, mark-missing for a heal
    group). Never emit a partial/garbled card.
```

- `units` = the call's summed complexity in the same currency the sizer uses
  (citations + senses), so the budget scales with what the call actually has
  to emit.
- `expectedMs(units)` = a linear model `base + slope × units` fitted from the
  benchmark below.
- `KILL_FACTOR = 2` — MG's "200% higher". A legit call should finish well
  under 2× its expected time; a doomed stall (≥5× on H155) blows past it.
- `KILL_FLOOR_MS` — a generous floor so network jitter on a tiny card never
  trips it. `KILL_CEIL_MS` — a hard ceiling; nothing should ever run past it.
- Default ON; `--no-kill` disables, `--kill-factor=N` tunes. Applies to the
  main batch lane and the heal-group lane.

### Why this is the right backstop, not a replacement for the triggers

The kill gate does **not** save the tokens the doomed call already burned up
to the timeout — without `AbortController` it can't. It saves the *rest*
(the remaining retries and the binary-split cascade) and, crucially, unblocks
the run so the card is recovered the cheap way. The structural triggers remain
the primary defense (they spend **zero** doomed tokens); the kill gate is the
net under the trapeze for drivers not yet on the trigger list.

## Benchmark — per-`agent()`-call speed vs complexity

Method: one full `tyaj` run (`--no-tm`, so every card genuinely translates),
19 cards across all lanes; per-agent wall-clock = last − first `timestamp` in
each `agent-*.jsonl` transcript, correlated to the call's complexity units.

13 agent calls, `--no-tm`, 0 nulls. Skeleton bytes vs wall-clock (main-batch
calls; fragment-lane calls omitted — their skel-byte attribution is per-group,
not whole-card):

| lane | cards/frags | Σ `<ls>` | Σ senses | skel bytes | wall-clock | ms / skel byte |
|---|---|---|---|---|---|---|
| batch | 3 | 34 | 1 | 744 | 15.7 s | 21.1 |
| batch | 3 | 34 | 6 | 1182 | 19.8 s | 16.8 |
| batch | 4 | 20 | 5 | 1118 | 27.0 s | 24.2 |
| batch (`pari`, citation-dense) | 1 | 86 | 8 | 1801 | 32.5 s | 18.1 |
| heal group (`sam`) | — | 34 | 6 | 1182 | 52.0 s | 44.0 ← slowest/byte |
| batch | 5 | 83 | 4 | 1828 | 60.7 s | 33.2 |
| batch (11 tiny no-fallback cards) | 11 | 62 | 5 | 2929 | 83.8 s | 28.6 |
| `zz_pw` fragment groups (presplit) | 9–13 frags | — | — | — | 70–108 s | — |

**Read:** wall-clock tracks **skeleton bytes** far better than `<ls>` or sense
count alone (the citation-dense `pari` at 86 `<ls>` ran *faster* than the
low-citation 11-card batch — because output volume, not citation count, is what
takes time). Centre ≈ 25 ms/skel-byte; observed ceiling ≈ 44; nothing legit
ran past 84 s. skeleton bytes are therefore the kill-gate's complexity signal.

## Decisions

Calibrated constants (in [`gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py),
emitted into every harness; tunable via `--kill-factor=N` / `--no-kill`):

| const | value | rationale |
|---|---|---|
| `KILL_FACTOR` | 2.0 | MG's "200%" — kill at 2× expected-for-complexity |
| `KILL_BASE_MS` | 30 000 | fixed per-call latency (spin-up + framing) |
| `KILL_SLOPE_MS` | 45 | ms per skel byte — set *above* the 44 ms/byte observed ceiling |
| `KILL_FLOOR_MS` | 120 000 | never kill before 2 min (jitter guard on tiny calls) |
| `KILL_CEIL_MS` | 480 000 | hard 8-min ceiling regardless of size |

Resulting budgets (`FACTOR × (BASE + SLOPE × skelBytes)`, clamped): 744 B →
127 s · 1182 B → 166 s · 1828 B → 225 s · 2929 B → 324 s · 3956 B → 416 s ·
≥8 kB → 480 s (ceil). Every observed legit call (≤ 84 s) sits **far** under its
budget; a stall at the full ~5-deep retry cap (the original `zz_pw` ~7 min at
3956 B) blows past. Conservative on purpose — a false kill costs one selfheal,
and we want *zero* on rollout; tighten `--kill-factor` once real runs confirm
the envelope holds.

**On kill:** `resolveGroup` marks the call's cards pending and `break`s so
`BINARY_SPLIT` isolates the slow card (halves get proportionally smaller
budgets), bottoming out to per-card selfheal; `healGroup` bisects the fragment
group. A killed card is therefore **recovered**, never dropped. Proven in a
zero-token behavioural test (`kill_mechanism_test.mjs`, 9/9) and a static
harness-wiring selftest (`test_kill_gate_wired`).

### What the kill gate is NOT

It does **not** recover the tokens the doomed call already spent up to the
timeout (no `AbortController`). It bounds the *tail* (remaining retries +
binary-split cascade) and unblocks the run. The structural presplit triggers
(#1, #2) remain the primary, zero-waste defense; the kill gate is the backstop
for #3–#5 and the unknown. When a *new* stall class shows up in a real run,
promote it from "caught by the kill gate" to its own structural trigger (as
H155 did for senses) so the next occurrence spends zero doomed tokens.

_Dr. Mārcis Gasūns_
