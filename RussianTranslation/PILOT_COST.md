# Pilot cost & scaling to the full dictionary

## 1. What the pilot actually cost

The pilot translated **15 of the richest a-cards** (deliberately the densest — `amṛta`
53 senses, `arjuna` 37, `aṅga` 27; **303 senses total, ~20/card**, vs the
dictionary average of ~1.5–3 senses/card).

| aspect | pilot (15 cards) | per card | per sense |
|---|---|---|---|
| **LLM agents** | 30 (15 Sonnet translate + 15 Opus judge) | 2 | — |
| **Tokens** | 1,800,897 | ~120k | ~5,900 |
| **Wall-clock** | 7.9 min (≈12 agents concurrent) | ~32 s | ~1.6 s |
| **Direct $ (LLM)** | **$0** — runs on the Claude **Max** subscription, not the API | $0 | $0 |
| **Direct $ (DeepSeek)** | **$0 marginal** — the corpus lexicon is pre-built | — | — |
| tool calls | 98 | — | — |

**One-time costs already paid (amortized over the whole dictionary, not per card):**
- **Corpus word-alignment lexicon**: **$18.35 DeepSeek** (actual bill; 1.09M
  alignments, 190k keys), ~hours of build. *(The watcher's live "$37–49" was an
  over-projection — off-peak pricing + context-caching made the real $/alignment
  lower.)* Every card reuses it for free → ~**$0.0005/card** amortized.
- Gold-standard precision run: 1 workflow (~6 min). Microstructure, resolvers,
  abbreviation tables, prefaces: build effort, done.

So the pilot's **marginal money cost was ≈ $0**; the only real money in the whole
project so far is the **$18** one-time lexicon.

## 2. Per-unit economics (corrected for density)

The pilot cards are ~10× denser than average, so don't scale on "$/card" from them —
scale on **$/sense**, then multiply by the dictionary's sense count:
- ~5,900 tokens/sense includes per-card fixed overhead (reading the portrait + raw,
  the prompt). On sparse cards that overhead is amortized over fewer senses, so the
  **effective average is higher — call it ~8–10k tokens/sense**.

## 3. Scaling to all of PWG

PWG ≈ **123,366 records / ~106,000 headwords**, with an estimated **~250k–350k
senses** total (the a-section is dense; the long tail is sparse).

| | estimate | basis / caveat |
|---|---|---|
| **Tokens** | **~1.5–2.5 billion** | 300k senses × 8–10k tokens (translate+judge) |
| **LLM agents** | ~210k+ | 2 per card (translate + judge), more on re-passes |
| **Machine time** | **~300–600 h of *continuous* throughput** | pilot rate ~1.9 cards/min, faster on sparse cards; **but** the environment reaps long runs and Max has usage windows → **~1–2 months elapsed** with restarts (matches the "run Sonnet for a month" plan) |
| **Direct money** | **≈ $18 total** (the lexicon, already spent) | LLM is $0 on Max; DeepSeek is one-time |
| **Human review** | **~15–25% of cards flagged** → the real bottleneck | pilot flagged 3/15 = 20%; the 3 guards should lower it; even at 15%, ~16k cards × a few min each = **hundreds of editor-hours** |

## 4. The headline

For a **printed scholarly dictionary**, the costs rank, in order:
1. **Human editorial review** — the dominant, irreducible cost. The machine flags
   what needs a human; ~15–25% of ~106k cards is the real budget (editor-hours, over
   months). Quality—not compute—is the constraint, exactly as intended.
2. **Calendar time** — ~1–2 months of mostly-unattended machine run-time (interrupted
   by reaps/quota; resumable, lossless).
3. **Money** — **negligible**: ~$18 one-time (the DeepSeek lexicon). The Sonnet+Opus
   translation+judging is **free** on the Max subscription.

## 5. Levers (already in place or cheap)

- **Density-aware routing** — translate the long tail (1-sense cards) with a lighter
  single pass; reserve the full per-sense-discrimination + judge treatment for cards
  with real polysemy/corpus reuse (the high-value core, ~20–37k cards). Cuts machine
  time and human review materially.
- **The 3 guards** (this run) — fewer judge failures → fewer re-passes → less time +
  less human review.
- **Coverage-first ordering** — do the ~20–37k cards with dict/corpus reuse first
  (highest value per hour), long tail last.
- **DeepSeek already amortized** — no further API spend for the lexicon; new corpus
  texts cost a few $ each (off-peak halves it), only if added.
- **Human review is gateable** — the `review_status` state machine + severity-sorted
  worklist means humans touch only the flagged minority, not all 106k.

## 6. Measurement-grounded update (2026-06-23) — tokens, days, and what we still lack

The §3 figure ("1.5–2.5 B") extrapolated the **dense head** as typical. Real per-card
measurement (6 coverage-first cards via the Agent path) plus the actual input-size
distribution corrects it.

**Measured:** translate cost ≈ **0.78 tokens per input byte**. The 6 cards averaged
**129 KB input each (~100 k tokens)** — but the a-section **average card is 3.3 KB**,
**~39× smaller**. Coverage-first front-loads the giants; the long tail is tiny. So a
flat "100 k/card" massively overstates the bulk.

| | cards | translate | +Opus judge (~1×) | total |
|---|---|---|---|---|
| **a-section** | 12,156 | ~0.25–0.4 B | ~0.25–0.4 B | **~0.5–0.8 B** |
| **whole PWG dict** | **106,083** (8.7×) | ~2–3.5 B | ~2–3.5 B | **~4–7 B** |

Content tokens alone are only ~270 M dict-wide; the band is dominated by **fixed
per-card overhead** (prompt + reading two files + reasoning + output floor), which is
unmeasured for small cards.

**Wall-clock / throughput.** Measured durations: dense cards 2–11.5 min; the average
card ~1–2.5 min. At a ~12-card concurrency cap and ~2.5 min/card → **~290 cards/h ≈
~7 k cards/day at 24/7** → whole dict **~15 days of *continuous* running**. That is the
*optimistic* floor and assumes no reaps, no gaps, **and no quota**.

**The real ceiling is the Max weekly token quota**, which we *hit* this session but
never recorded numerically. Whole dict in 2 weeks ⇒ 2–3.5 B tokens/week — far above a
single Max plan's weekly allowance. So on one Max seat the dictionary is **quota-bound
to ~1–2 months, not 2 weeks**. The a-section (~0.5–0.8 B) plausibly fits ~1–2 weekly
windows.

**Can 2 months of Max finish the whole dictionary? Unknown — and here is exactly what
we lack to decide it:**

| # | Missing datum | How to get it | Source |
|---|---|---|---|
| 1 | **Max weekly token quota** (the divisor in `weeks = total ÷ quota`) | record cumulative tokens at the moment the weekly cap fires | **Max only** |
| 2 | **Per-card cost on a *typical* (small) card** | run ~10 small cards, record `subagent_tokens` | now (Agent) |
| 3 | **Whole-dict total input bytes** | generate all-section inputs / extrapolate the size distribution | now |
| 4 | **Reject / re-pass rate** (rework multiplier) | accrues as gated windows run (1/6 so far) | falls out of the run |
| 5 | **Judge policy** — every card vs sample + gate-flagged only | a decision; halves the total | editorial call |

**The one experiment that collapses the uncertainty:** run the prepped 50-card Max
window *instrumented* — record (a) tokens, (b) wall-clock, (c) keep running windows
until the cap fires and note the cumulative-token number. That single run yields the
per-card cost (item 2), the real harness throughput, **and** the weekly quota (item 1)
together → `2-months feasible? ⇔ refined_total ÷ measured_weekly_quota ≤ 8` becomes a
clean yes/no.

**Levers to fit 2 months / 2 weeks** (compounding): drop per-card Opus judging in favor
of the deterministic F12 gate + a judged *sample* (halves to ~2–4 B); coverage-first so
the high-value core lands first; or move the **bulk to the DeepSeek API** (parallel, no
weekly cap, ≈ **$1.5–4 k** for the whole dict) and reserve Max/Opus for hard/flagged
cards. The a-section stays the Max-validated gold reference either way.
