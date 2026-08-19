# ROADMAP — PWG→RU research-ceiling residual, 2026 H2

_Created: 19-08-2026 · Last updated: 19-08-2026_

Index: [PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md).

## Wave A — the yardstick (launch first)

| Unit | Deliverable | Unblocks |
|---|---|---|
| **R5** | Three frozen gold sets (WSD ~200 tokens · COMET-QE A/B/C slice · BLI 300 Sa→Ru), one documented annotator-2, per-set κ | CEILING C1, RESEARCH_CAPABILITY cards 1 and 3 — three items across two roadmaps, all silently blocked on this one artifact |

R5 goes first because it is the **only** unit here that other units are waiting on,
and because the trap it removes is active right now: a session can pick up card 1
or card 3 today, get halfway, and discover the blocker itself. Nothing in either
roadmap marks those cards as blocked.

R5 does **not** wait on ~50 % translation coverage. Coverage gates *running* the
WSD baseline, not *building the yardstick* — and building the yardstick early is
what makes the coverage checkpoint actionable when it arrives.

## Wave B — the cheap derivables (parallel, any order)

| Unit | Deliverable | Unblocks |
|---|---|---|
| **R1** | Per-sense attestation window from `<ls>` × `ls_source_map` (45 works), plus the C7 unresolved-citation census | C2 phase 2's curated dating table later; an honest "when is this sense attested" answer now |
| **R2** | KEWA index normalized + dhātu-aware join; *modern IE* lane of C4's two-lane etymology | C4; the EWA crosswalk shape when EWA lands |
| **R3** | DharmaMitra licence quoted verbatim + fetchable inventory + composition `@DECIDE` + parked outreach draft | C8; and the C1 DharmaMitra probe, which cannot be scoped before the licence is known |
| **R4** | Heritage segmenter cross-validated against DharmaMitra morphology and the glossary adjudication set | A second independent morphology witness for csl-atlas and RussianTranslation |

These four are mutually independent. R3 and R4 both touch external services and
both carry the same etiquette requirement (cache, throttle, identify) — running
them in the same session is efficient but not required.

## Wave C — coverage-gated (not minted)

| Item | Gate |
|---|---|
| C1 embedding-WSD baseline + P@1 harness | ~50 % translation coverage |
| C1 DharmaMitra probe on the same gold set | above, plus R3's licence answer |
| C2 phase 2 — curated per-work dating table with scholarly sources | Wave 2; contested datings each become an `@DECIDE` |

Deliberately unminted. The sequencing ruling put model/benchmark phases after
coverage, and minting them now would produce handoffs that sit blocked and rot —
the exact failure this programme is correcting.

## Sequencing

```
R5 (yardstick) ──┬──▶ unblocks C1 / card 1 / card 3 when Wave C opens
                 │
R1 ──┐           │
R2 ──┼─(independent, any order)
R3 ──┤           │
R4 ──┘           │
                 └──▶ Wave C at ~50% coverage
```

## Exit condition

Complete when R1–R5 close and the four source roadmaps' status text matches
reality. At that point CEILING has only Wave 2 (coverage-gated) plus its permanent
ceilings; HERITAGE is fully executed and becomes a historical record of the
integration **plus** the LGPLLR×BY-SA rights ruling other sessions cite — retitle,
never delete; RESEARCH_CAPABILITY's cards become individually pickable with their
shared blocker gone.

## Standing correction this programme installs

**A roadmap may not delegate its own mint to an unobserved future moment.** Both
CEILING ("handoffs are minted after H335 lands") and HERITAGE phase 6 ("mints its
own H### when its gate clears") did exactly that, and both sat six weeks past their
trigger. Any future gate in these documents names the observable that decides it
and, where the gate is a handoff closing, the mint is queued at the same time as
the gate is written — not promised for later.

_Dr. Mārcis Gasūns_
