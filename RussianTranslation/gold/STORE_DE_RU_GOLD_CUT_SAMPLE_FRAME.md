# Store DE→RU gold cut — stratified sample frame (design, parked for sign-off)

_Created: 26-07-2026 · Last updated: 26-07-2026_

Designed by Fable 5 (`claude-fable-5`) under
[H1633](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1633-Fable_SanskritLexicography_pwg-human-gold-cut-methods-packet_25.07.26.md)
(parent programme
[H1624](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md)).
**Status: DESIGN ONLY.** No sample has been drawn, no sheet generated, no label
collected. Every number below is either cited from a committed artifact or an
arithmetic consequence of a stated formula — nothing is a measurement.

## 1. What this frame licenses — and what it does not

The paper
[A51](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PAPER_LLM_LEXICOGRAPHY.md)
needs a **human-measured precision figure for the DE→RU translation store**.
Today no such figure exists; the three gold artifacts already in this repo
measure *different objects*, and conflating them would be the exact
over-claiming this frame exists to prevent:

| Gold artifact | Object measured | Status |
|---|---|---|
| [`gold_set.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl) + [precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md) (320 rows, G6/G7 machinery) | **Sa→Ru harvest alignment** (corpus token → Russian rendering) | LLM-estimated 84.4% (95% CI 80.0–87.9); human pass 0/320 |
| [`grade_gold.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/grade_gold.jsonl) ([GRADE_GOLD_MEMO.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/GRADE_GOLD_MEMO.md), 320 rows) | TM **grade** (A/B/C) of harvest rows | agent-adjudicated, PRELIMINARY |
| **This frame** (new) | **DE→RU store sense rows** — is the Russian a print-acceptable rendering of the German sense? | designed, not executed |

Licensed once executed: a per-sense precision estimate with Wilson 95% CI for
the machine-clean promoted store, plus a typed error profile. **Not licensed
even after execution:** any "AI better than human/KOW" claim (N13 needs a
comparative adjudicated design, out of scope) and any claim about rows the
deterministic gates rejected (§2).

## 2. Population and unit

- **Population:** the G5-eligible pool of the promoted store — the review
  queue **after** the H1655/P1 residue gate
  ([`review_residue_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_residue_gate.py)):
  machine-flagged cards (reader-visible German residue; D1/D3/D4 flags) are
  auto-rejected before any human sheet, per MG's P1 ruling of 26-07-2026. As of
  26-07-2026 that pool is 7,286 of 11,163 queue rows; both numbers move with
  the store, so the cut **recomputes the pool at generation time** and stamps
  the counts into the report.
- **Consequence stated honestly:** the precision estimate is *conditional on
  the deterministic gates* — it measures what the pipeline offers for print,
  not raw model output. The excluded strata are already routed to repair
  (H1651), not silently dropped.
- **Unit:** one queue row = one sense row (`review_id`-keyed) presented with
  its full card context. Binding to `review_id`, never positional `ord`, per
  the queue-generations lesson
  ([REVIEW_GOLD_VOTING_DEEP_MANUAL.md §4.2](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.md)).

## 3. Stratification

Three dimensions, all computable from committed metadata at generation time
(no manual labeling to build the frame):

| Dimension | Levels | Source |
|---|---|---|
| entry class | verbal root · nominal/other | store card metadata |
| edition layer | PWG-main · supplement (PW/SCH/PWKVN/NWS pooled) | L1 labels / G4 `edition_rel` ([REGLUE_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md)) |
| DE gloss length | terciles (short/medium/long), cut on the pool's own distribution | raw DE span length |

2 × 2 × 3 = **12 strata**, allocation **proportional** to pool share with a
**floor of 15 rows per stratum** (floors trade a little variance for the
ability to say anything per-stratum at all). Per-source supplement splits
(PW vs SCH vs NWS) are reported descriptively, not powered.

**Cluster control:** sense rows cluster by lemma. Cap **≤ 4 sampled rows per
lemma** (the h178 precedent) so no giant polysemous root dominates. Seeded,
deterministic draw (seed recorded in the lock).

## 4. Size — justified, with the cluster penalty stated

Planning arithmetic (Wald half-width `e = 1.96·√(p(1−p)/n)`; reporting uses
Wilson intervals as everywhere else in this repo):

| n | half-width at p̂=0.85 | at p̂=0.90 | with DEFF 1.3 (worst-case cluster penalty) at p̂=0.85 |
|---|---|---|---|
| 320 | ±3.9 pp | ±3.3 pp | ±4.5 pp |
| **400** | **±3.5 pp** | **±2.9 pp** | **±4.0 pp** |
| 600 | ±2.9 pp | ±2.4 pp | ±3.3 pp |

DEFF 1.3 = `1+(m−1)·ρ` at cap m=4 and an *assumed* intra-lemma correlation
ρ=0.1; the real ρ is unknown until labels exist, so the report must carry both
the naive Wilson CI and a **lemma-level cluster bootstrap CI**, and the wider
one is the headline.

**Recommendation: n = 400** (≈ 5.5% of the current eligible pool). Rationale:
at the LLM-estimated precision neighborhood (0.85–0.90) it keeps the honest
(DEFF-adjusted) half-width at ~±4 pp, which separates "high-80s" from
"low-70s" — the decision-relevant distinction for a print go/no-go — while
staying within one reviewer's realistic budget (the G6 precedent fixed 320 as
the bounded human workload; 400 is the same order). 600 buys ±0.7 pp for +50%
work. **The final n is a human's call at sign-off.**

## 5. Instrument and labels — needs a D6-style ruling

Per ruling D6 (one instrument per gate,
[REVIEW_GOLD_VOTING_DEEP_MANUAL.md §4.1](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.md)),
gold needs **typed** errors → MQM-style typology sheet, exactly like G6. But
the G6 six-label vocabulary (`correct / lemma-variant / proper-name / partial /
wrong-sense / hallucinated`) was built for Sa→Ru *alignments*;
`lemma-variant` and `proper-name` do not transfer to DE→RU sense translation.
**Proposed** store vocabulary (six labels, same arithmetic shape):

| Label | Meaning (DE→RU sense row) | Counts as |
|---|---|---|
| `correct` | print-acceptable contextual equivalent of the German sense | good |
| `acceptable-variant` | correct after synonymy/register/inflection normalization | good |
| `partial` | related but incomplete, over-broad, or too narrow | reported separately |
| `wrong-sense` | fluent Russian, wrong meaning of the German | error |
| `residue-format` | German leak-through, broken markup, placeholder damage | error (and a live check on the residue gate itself) |
| `hallucinated` | content unsupported by the German source | error |

Precision = good / n; `partial` never silently folded into either side.
**This vocabulary is a proposal, not policy** — adopting it (or amending it)
is a ruling for a human, recorded like D6, before the sheet is generated.

## 6. Dual annotation and the κ plan — no invented numbers

Standing constraint, stated plainly: the second-annotator recruiting deferral
for 2026
([EVALUATION_PROTOCOL.md §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EVALUATION_PROTOCOL.md))
means a human×human κ **may not be measurable in 2026**. The plan is
therefore tiered, and each tier's figure keeps its channel label — the
[GRADE_GOLD_MEMO.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/GRADE_GOLD_MEMO.md)
κ=−0.0044 episode is the standing example of why channels are never relabeled:

1. **If a second reviewer exists:** 80-row stratified double-review queue (20%
   of n=400; the G7 machinery pattern —
   `gold_double_review_queue.py` → `gold_agreement.py`), unweighted Cohen κ on
   the six labels **and** on the binarized good/not-good call, each with a
   bootstrap CI. Whatever κ comes out is reported as measured.
2. **Single-annotator fallback (allowed by the deferral):** MG test–retest —
   the same 80 rows relabeled by MG ≥ 14 days later, reported as
   **intra-rater** κ, never presented as inter-annotator agreement.
3. **Secondary channel:** DeepSeek (`deepseek-chat`) model labels over the
   full sample, reported strictly as **human×model** agreement (the
   h178 convention).

Adjudication: `needs_adjudication` rows and all double-review disagreements
resolved by the lead editor before the report; disagreement counts published.

**Hard rule (the H1633 goal line): no κ target, no placeholder κ, no κ from a
channel that does not exist yet.** Until labels are ingested, every κ cell in
any draft stays `—`.

## 7. Mechanics — the H1404 binding standard, verbatim

New generator (`build_store_gold_sheet.py`, to be written at execution time)
follows the five-line standard in
[REVIEW_GOLD_VOTING_DEEP_MANUAL.md §7](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.md):
emit via `csl_pyutil.render_review_sheet`, `stamp()` + `write_lock()`, sheet id
series `store-gold-cut-<batch>-<date>`, HTML gitignored (embeds unpublished
RU), lock committed. Votes export as `decisions.json` →
`validate_decisions.py` → `apply_decisions.py` with an **explicit out path**
(`gold/store_gold_labels.jsonl` — separate from the 320-row harvest gold and
its hard count gate). Report lands as `gold/store_precision_report.md` with
the sampled pool counts, seed, both CIs, and the label distribution.

Gate wiring: this cut is release evidence for the **store**, sitting beside —
not replacing — G6/G7 (harvest) in the G10 arithmetic.
[HUMAN_REVIEW_MINIMIZATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/HUMAN_REVIEW_MINIMIZATION.md)
owns gate arithmetic; folding this cut in as a named gate is an edit to that
file at sign-off, not something this frame decides.

## 8. What sign-off must decide (blocking execution)

1. Final **n** (recommended 400) and the 15-row stratum floor.
2. The **label vocabulary** of §5 — adopt/amend, recorded as a ruling.
3. **Double-review staffing** — second reviewer in 2026 yes/no (picks tier 1
   vs tier 2 of §6).
4. Whether the cut becomes a **named gate** in HUMAN_REVIEW_MINIMIZATION.md.
5. Sequencing vs the live G5 batch votes (the cut samples the same pool; both
   can run, but sheet-generation freezes must not cross a voted, unapplied
   batch — voted.md item 2).

## 9. Non-goals

- No mass re-translation, no auto-adjudication of anything human-gated
  (compound `differs`, H1306 style) — unchanged from H1633.
- No claim about the gate-rejected strata beyond "routed to repair".
- No N13 comparative claim; no publication of the gitignored store (N9).

_Dr. Mārcis Gasūns_
