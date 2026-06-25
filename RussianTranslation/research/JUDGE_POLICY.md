# Judge-model policy for the pwg_ru scale-up (decided 2026-06-25)

**Decision.** The bulk QA judge = **Sonnet**. **Opus** is retained for the **repass of rejects**
and a **periodic audited sample**. Full commitment is gated on one remaining test (semantic
discrimination — see bottom). This is the target operating policy; the conservative production
default (`--judge-model opus`) stays until the gate passes, then flips.

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
3. **Periodic Opus audit of clean-passed cards.** Random ~5% of Sonnet-approved cards re-judged
   by Opus each batch, scored with [`../src/judge_ab_score.py`](../src/judge_ab_score.py); if the
   false-clear rate ever exceeds ~1% or κ drops below 0.7, halt and re-evaluate. This catches
   distribution drift the static A/B can't.
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

## Open gate before full commitment — semantic discrimination

Runs 1–4 prove Sonnet's **vigilance** (mechanical/structural defects). They do **not** test deep
**semantic** judgment: a **plausible-but-wrong gloss** — a fluent, correct-looking Russian
rendering that is the *wrong meaning* of the German. That is the likeliest place a weaker judge
could slip, and the one class I could not auto-generate with reliable ground truth. **Full
commitment to Sonnet-as-bulk-judge is contingent on Sonnet matching Opus on a semantic-defect
battery with verified ground truth** (design pending — see the open questions in this turn).
Until then: adopt the rollout above in *shadow* (Sonnet judges, Opus re-judges everything, compare)
on the first real batch, rather than trusting Sonnet unsupervised.
