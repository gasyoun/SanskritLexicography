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
- **Corpus word-alignment lexicon**: **$49 DeepSeek** (1.09M alignments, 190k keys),
  ~hours of build. Every card reuses it for free → ~**$0.0005/card** amortized.
- Gold-standard precision run: 1 workflow (~6 min). Microstructure, resolvers,
  abbreviation tables, prefaces: build effort, done.

So the pilot's **marginal money cost was ≈ $0**; the only real money in the whole
project so far is the **$49** one-time lexicon.

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
| **Direct money** | **≈ $49 total** (the lexicon, already spent) | LLM is $0 on Max; DeepSeek is one-time |
| **Human review** | **~15–25% of cards flagged** → the real bottleneck | pilot flagged 3/15 = 20%; the 3 guards should lower it; even at 15%, ~16k cards × a few min each = **hundreds of editor-hours** |

## 4. The headline

For a **printed scholarly dictionary**, the costs rank, in order:
1. **Human editorial review** — the dominant, irreducible cost. The machine flags
   what needs a human; ~15–25% of ~106k cards is the real budget (editor-hours, over
   months). Quality—not compute—is the constraint, exactly as intended.
2. **Calendar time** — ~1–2 months of mostly-unattended machine run-time (interrupted
   by reaps/quota; resumable, lossless).
3. **Money** — **negligible**: ~$49 one-time (the DeepSeek lexicon). The Sonnet+Opus
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
