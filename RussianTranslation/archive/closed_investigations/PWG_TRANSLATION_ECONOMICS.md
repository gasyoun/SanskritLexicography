# PWG translation economics & timeline (measured 2026-07-01)

Grounded from the FU1 PWG→English run on **Sonnet 5 (`claude-sonnet-5`)** and repo counts.
Primary deliverable is **PWG→Russian**; English is a test harness (see §Sequencing).

> **04-07-2026 correction for the hard 30-day SLA.** The throughput math below still
> makes a full PWG→RU pass plausible under continuous operation, but it is not a
> license to widen live LLM/Workflow concurrency. The locked production ceiling is
> **≤3 concurrent translation lanes**; wider parallelism is allowed only for
> deterministic prep/audit/rootmap/validation work. The live H151 worklist also
> exposed a current blocker: many remaining verb roots were visible in the backlog
> but not runnable because rootmaps were missing. The SLA plan therefore treats
> rootmap generation and non-root/noun bulk coverage as separate workstreams:
> [`FULL_PWG_RU_30_DAY_SLA_PLAN.md`](../../FULL_PWG_RU_30_DAY_SLA_PLAN.md).

## Measured throughput (FU1 EN run — same harness/economics as RU)

Audit tool: `python src/pilot/parse_workflow_cost.py <workflow_transcript_dir>...` (computed
on demand from transcripts; no persistent cost file). Over the 76 FU1 workflows:

| Metric | Value |
|---|---|
| Tokens | 98.7 M (6.6M in / 22.2M cache-wr / 66.3M cache-rd / 3.6M out) — **cache-dominated** |
| Cost @ Sonnet 5 **intro** rates ($2/$10 per M, through 2026-08-31) | **$118** |
| Cost @ standard rates ($3/$15) | $177 |
| Net cards produced | 1,432 (30 roots) |
| Cost **per card, clean single-pass** | **~$0.031** (yA cost-check, no retries) |
| Cost **per card, all-in this run** (3 passes: first + 2 requeues) | ~$0.082 |
| Wall-clock throughput @ **≤3-wide** | ~**800–1,000 cards/hour** |

The $0.082 reflects one-time discovery waste (finding+fixing the StructuredOutput cap). A clean
production run lands near **$0.03–0.05/card**. Do **not** extrapolate this into a live
10-wide Workflow run: Slice-D already proved that wide LLM fan-out collapses. Use the
≤3-wide measured lane as the production ceiling; use wider parallelism only for deterministic
preparation and validation.

## Scope (grounded, not estimated)

- **`src/assembled_cards.jsonl` = 120,173 headword-cards** = whole PWG.
- DCS-attested subset (41.4%, the frequency-first "worth-first" tier) ≈ **~49,000 headword-cards**.
- **Translation units ≠ headword-cards.** Nouns/adjectives (the vast majority) = 1 sub-card each;
  verbal roots explode (the 30 FU1 roots = 30 headwords → 1,509 sub-cards, ~50×, but those are the
  most extreme top-frequency verbs). Realistic exploded totals:
  - Full PWG: **~120k–160k sub-cards** (use ~140k midpoint).
  - DCS subset: **~49k–66k sub-cards** (use ~57k midpoint).
- **RU already done: ~46 roots** (8,592 sense-rows in `src/pwg_ru_translated.jsonl`) ≈ ~2.5k
  sub-cards — **<2% of scope**; treat remaining ≈ full totals above.

## Timeline (start 2026-07-01, RU first, ≤3-wide, clean pipeline)

Cards/day = throughput × productive hours/day. The operating regime is the dominant variable:

| Regime | ~cards/day | DCS subset (~57k) | Full PWG (~140k) |
|---|---|---|---|
| Part-time (~3 h/day) | ~2,500 | ~23 days → **~late Jul 2026** | ~56 days → **~late Aug 2026** |
| **Attended ~8 h/day (headline)** | **~6,000** | **~10 days → ~Jul 14** | **~24 days → ~Aug 4–6** |
| Semi-autonomous ~16 h/day | ~13,000 | ~5 days → ~Jul 6 | ~11 days → ~Jul 14 |
| ~24/7 (if caps allow) | ~20,000 | ~3 days → ~Jul 4 | ~7 days → ~Jul 9 |

Dates are working-throughput; wall-clock adds weekends/rate-limit pauses. **Cost, RU full pass:**
~140k × $0.03–0.05 ≈ **$4,200–7,000** at intro rates (Batch API halves this for the noun bulk).

### ⚠️ Timeline risks
- ~~**RU schema NOT relaxed.**~~ **DONE 2026-07-01** — the StructuredOutput-cap relaxation
  (per-sense `required` → `[tag, german, <field>]`, the 4 annotator fields optional) is now
  applied to **both** the RU and EN paths in `gen_opt_harness2.py`, with the RU validation gate
  (`validate_final_card_schema.py`) and the canonical `schemas/pwg_ru_final_card.schema.json`
  relaxed to match (annotator fields validated only when present; selftest passes). RU giant-head
  cards now validate with the same fix, so the RU bulk run starts clean (no repeat of the
  2-requeue-round waste). Trade-off: on the few giant cards recovered only via the relaxation,
  some annotator metadata (equivalence_type/source_type/stratum/differentia) may be absent (the
  model still fills them on most cards; they are re-derivable). For **zero** metadata loss on the
  giant heads, additionally wire the head-splitter (`_pilot_gen_merged.py --root-split`, lower
  `HEAD_CIT_BUDGET`) so each part satisfies the full schema.
- The FU1 30 roots are the *worst case* (verb-heavy, dense heads); the noun bulk of the dict is
  cheaper and faster per card, so these estimates are conservative for the full sweep.
- Max **weekly caps** throttle sustained 24/7; the realistic sustained regime is the 8–16 h/day band.

## Sequencing — RU first, EN after (confirmed)

Doing RU and EN as **two separate passes ≈ 2× time/cost** (you translate every card twice). The
user's instinct is correct: **finish RU fully first, then run EN as a second sweep** — fastest to
the RU milestone. One nuance: a **bilingual single-pass** (RU+EN in one workflow call, shared
masking/segmentation, per-card cache-create paid once) costs ~**1.3–1.5×**, not 2× — cheaper than
two passes if you ever want both delivered together. But for "finish RU ASAP," RU-only first wins.
The FU1 plan already reserves bilingual single-pass for *future* roots where RU and EN extend
together; the standing decision is EN-only-after-RU for the primary push.
