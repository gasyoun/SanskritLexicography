# Judge-model policy for the pwg_ru scale-up (decided 2026-06-25)

**Decision.** The bulk QA judge = **Sonnet**. **Opus** is retained for the **repass of rejects**
and a **periodic audited sample**. Full commitment is gated on one remaining test (semantic
discrimination — see bottom). This is the target operating policy; the conservative production
default (`--judge-model opus`) stays until the gate passes, then flips.

> **IMPLEMENTED in the Max harness (2026-06-26).** The A/B gate is near-conclusive
> (κ=1.0 over 474 cards; ~0.5 % disagreement), so the flip is done:
> [`../src/pilot/run_pilot_wf.js`](../src/pilot/run_pilot_wf.js) now **judges every card with
> Sonnet** and escalates to **Opus only on a reject** (`isHard` = `ok=false || severity>=3`);
> the Opus verdict is final (becomes `judge`; Sonnet's original kept as `judge_sonnet`,
> `escalated:true`). Publishable cards (sev 1–2) spend **no Opus tokens** — the weekly-quota
> headroom that makes the bulk run feasible on one Max seat. For defence-in-depth, the current
> window loop writes a deterministic semantic review queue, `judge_sample.keys.txt`: all Python
> gate failures plus a default clean-card sample. Send only that queue to sampled semantic judging
> after mechanical gates pass.

Grounds: the four-run A/B in [`JUDGE_AB.md`](JUDGE_AB.md). Summary:

| run | what | result |
|---|---|---|
| 1 (7 cards) | clean + 2 planted defects, Opus vs Sonnet judge | κ=1.0, 0 false-clears |
| 2 (26, POS-diverse) | adj/m/f/n-noun/indecl/verb | κ=1.0, within ±1 severity, 0 false-clears |
| 3 (201, full a-section audit) | whole translated set, both judges | 191/191 agreement, κ=1.0, 0 false-clears |
| 4 (250, **ground-truth power test**) | one planted subtle defect/card, blinded | **Opus 99% recall / Sonnet 99% / 0% false-pos both; head-to-head 208-208, each missed 1 different card** |

Across **474 judged cards** Opus and Sonnet have never disagreed on an accept/reject call beyond
1–2 borderline severities, and on 200+ subtle defects with **known ground truth** their recall
and false-positive rates are identical. **No Opus power advantage was detected for the mechanical
core of judging** (gloss translated? anchors intact? citations faithful? coverage complete? Latin
kept?).

## Why Sonnet for the bulk

- **No measured quality loss** (run 4: 99% recall, 0% false-positives, same as Opus).
- **Cost/quota:** on the top-500 the judge step drops from ~$277 (Opus ×2) to ~$143 (Sonnet ×2)
  in Opus-API-reference terms. We run on **Max**, so the real win is **weekly-quota headroom** —
  far fewer Opus tokens against the cap, which is the binding constraint on scale-up speed, not
  USD. See [`../PILOT_COST.md`](../PILOT_COST.md) §7.

## Rollout (defence in depth — Sonnet bulk, Opus insurance)

1. **Sonnet judges every card** in the bulk run (translate stage stays Sonnet; judge → Sonnet).
2. **Opus re-judges every reject.** Any card Sonnet flags BAD goes to an Opus re-pass before
   re-translation — cheap (rejects are a minority) and it backstops the rare Sonnet over-flag.
3. **Sampled semantic audit of clean-passed cards.** `audit_window.py` writes
   `judge_sample.keys.txt` after each window: all Python-gate failures plus a deterministic
   clean-card sample (currently 10% by default, minimum 5 where available). If sampled judging
   finds semantic drift, halt and re-evaluate before advancing roots. This catches distribution
   drift the static A/B can't without spending Opus tokens on every clean card.
4. **Two-judge panel.** Production planned two judges (Opus + YandexGPT). Options under this
   policy: **Sonnet + YandexGPT** (cheapest), or **Sonnet + Opus-on-disagreement** (Opus only
   adjudicates where the first judge is uncertain). Decide when wiring the production panel.

## What the judge is also good for (free guardrails the A/B surfaced)

- **Homonym-mismatch detector.** Run 3 caught 13 cross-homonym pairings at sev 5 (both models).
  Use as a standing check that `de`↔`ru` are paired by the same homonym.
- **Anchor / citation / coverage vigilance.** Run 4: ~100% recall on dropped `{#…#}`, falsified
  `<ls>`, dropped `<div>` senses, mistranslated Latin — a reliable structural QA pass.

## Operational notes

- **Pair `de`↔`ru` by homonym (`key2`/`hom`), never bare `key1`** — joining on `key1` silently
  crosses homonyms (the harness bug that faked a 7% defect rate in run 3); for the all-`key2`-
  identical headword `a`, use an explicit homonym index.
- **API instability is real.** The 250-card workflow lost 14 then 5 agents to transient
  connection-closed/403 errors; the workflow's resume-with-cache recovered them. Batch judging
  (≈10 cards/agent) + resume is the resilient pattern; expect to resume once.

## Semantic discrimination — settled by mining real disagreements, NOT synthetic defects

Runs 1–4 prove Sonnet's **vigilance** (mechanical/structural defects). The remaining question is
deep **semantic** judgment: a **plausible-but-wrong gloss** — fluent Russian that is the *wrong
meaning* of the German. A **synthetic** battery for this was abandoned (2026-06-25) on the
editor's objection: a one-word gloss pair (`Theil` → часть vs доля) is **undecidable in
isolation** — deciding it needs the whole entry *and* the Sanskrit sense in that passage; the
cases that *are* decidable from inspection are the rude ones Sonnet already catches. So a planted
"subtle defect" has a contestable ground truth and tests nothing real.

**The gate instead: sample real production cards with full context.** The current window loop
does not run both judges over every clean card; it writes `judge_sample.keys.txt` for the semantic
review spend queue after deterministic Python gates. For historical Opus-vs-Sonnet comparison
runs, [`../src/judge_disagreements.py`](../src/judge_disagreements.py) still emits a full-context
adjudication queue from paired verdict files.

**Already near-conclusive on real data:** across the ~400 cards judged so far,
`judge_disagreements.py` finds **0 disagreements in run 3 (191 real a-section cards)** and **2 in
run 4 (209 cards)** — a ~0.5 % conflict rate, i.e. the adjudication queue is essentially empty.
The two models almost never disagree, so there is barely anything left to test. The gate is
therefore mostly a **standing production check**, not a blocker: review the sampled semantic
queue each mechanically clean window and revisit only if the sampled defect rate climbs.
