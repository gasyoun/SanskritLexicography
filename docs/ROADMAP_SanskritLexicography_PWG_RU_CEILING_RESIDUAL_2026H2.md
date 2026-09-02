# ROADMAP — PWG→RU research-ceiling residual, 2026 H2

_Created: 19-08-2026 · Last updated: 02-09-2026_

> **Truth-pass 02-09-2026** (H3775) — `roadmap_handoff_truth.py --check` flagged this
> page drained but still living: **8 of 8 referenced handoffs have shipped, zero remain OPEN**.
> Kept at this path per MG ruling 31-08-2026 (do not archive) — the strategy/plan
> layer still holds even though its backlog has fully closed. A future session
> reopening work here should mint a fresh H### rather than un-close these.

Index: [PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md).

**Status 02-09-2026 ([H3794](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3794-Sonnet_SanskritLexicography_pwg-ceiling-residual-waveb-derivables_31.08.26.md)): R1–R5 are all ✅ shipped** — every unit below closed before H3794 was picked up; H3794's residual work was verifying that and correcting the four source roadmaps' stale status text (CEILING, HERITAGE, RESEARCH_CAPABILITY, ACL_LESSONS), not new engineering.

## Wave A — the yardstick (launch first)

| Unit | Deliverable | Unblocks |
|---|---|---|
| **R5** ✅ [H3172](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3172-Opus_SanskritLexicography_pwgru-shared-gold-wsd-bli_19.08.26.md) shipped 25-08-2026 | Three frozen gold sets (WSD ~200 tokens · COMET-QE A/B/C slice · BLI 300 Sa→Ru), one documented annotator-2, per-set κ | CEILING C1, RESEARCH_CAPABILITY cards 1 and 3 — three items across two roadmaps, all silently blocked on this one artifact. **Frames only, no labels** — per-set κ NOT reported (labels are MG pass-1, a human act); residual is human annotation, not engineering. |

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
| **R1** ✅ [H3168](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3168-OxAlpha_SanskritLexicography_ceiling-c2p1-sense-attestation-window_19.08.26.md) shipped 23-08-2026 | Per-sense attestation window from `<ls>` × `ls_source_map` (45 works), plus the C7 unresolved-citation census | C2 phase 2's curated dating table later (**also shipped, 01-09-2026, [H3790](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3790-Opus_SanskritLexicography_ceiling-c2-phase2-work-dating-table_31.08.26.md)**); an honest "when is this sense attested" answer now |
| **R2** ✅ [H3169](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3169-Opus_SanskritLexicography_ceiling-c4-kewa-normalize-join_19.08.26.md) shipped 25-08-2026 | KEWA index normalized + dhātu-aware join; *modern IE* lane of C4's two-lane etymology | C4; the EWA crosswalk shape when EWA lands |
| **R3** ✅ [H3170](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3170-OxAlpha_SanskritLexicography_ceiling-c8-dharmamitra-probe-outreach_19.08.26.md) shipped 24-08-2026 | DharmaMitra licence quoted verbatim + fetchable inventory + composition `@DECIDE` + parked outreach draft | C8; and the C1 DharmaMitra probe, which cannot be scoped before the licence is known |
| **R4** ✅ [H3171](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3171-OxAlpha_SanskritLexicography_heritage-phase6-segmenter-service_19.08.26.md) shipped 23-08-2026 | Heritage segmenter cross-validated against DharmaMitra morphology and the glossary adjudication set | A second independent morphology witness for csl-atlas and RussianTranslation |

These four are mutually independent. R3 and R4 both touch external services and
both carry the same etiquette requirement (cache, throttle, identify) — running
them in the same session is efficient but not required.

## Wave C — coverage-gated (not minted)

| Item | Gate |
|---|---|
| C1 embedding-WSD baseline + P@1 harness | ~50 % translation coverage |
| C1 DharmaMitra probe on the same gold set | above, plus R3's licence answer |
| ~~C2 phase 2 — curated per-work dating table with scholarly sources~~ ✅ shipped early, 01-09-2026, [H3790](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3790-Opus_SanskritLexicography_ceiling-c2-phase2-work-dating-table_31.08.26.md) | was Wave 2; turned out not to be coverage-gated (reads scholarship + R1's store, touches no model) — see ROADMAP_CEILING_2026.md §Wave 2 note |

Still deliberately unminted for the two items above. The sequencing ruling put
model/benchmark phases after coverage, and minting them now would produce
handoffs that sit blocked and rot — the exact failure this programme is correcting.

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

## Exit condition — MET 02-09-2026

R1–R5 are all closed (dates above) and the four source roadmaps' status text now
matches reality (H3794): CEILING's Wave 1 mini-table (C8 row) now carries its ✅,
HERITAGE already carried its ✅ for phase 6, RESEARCH_CAPABILITY's blocker note now
says the gold sets are frame-only pending human labeling rather than "unblocked",
and ACL_LESSONS' B1 gold-set build is flagged as already shipped ahead of Wave 2.
CEILING now has only Wave 2 (coverage-gated: C1's two model items) plus its
permanent ceilings; HERITAGE is fully executed and stands as a historical record of
the integration **plus** the LGPLLR×BY-SA rights ruling other sessions cite —
retitle, never delete; RESEARCH_CAPABILITY's cards 1 and 3 are individually
pickable once the human labeling pass lands — the engineering blocker is gone, the
human-annotation one is not.

## Standing correction this programme installs

**A roadmap may not delegate its own mint to an unobserved future moment.** Both
CEILING ("handoffs are minted after H335 lands") and HERITAGE phase 6 ("mints its
own H### when its gate clears") did exactly that, and both sat six weeks past their
trigger. Any future gate in these documents names the observable that decides it
and, where the gate is a handoff closing, the mint is queued at the same time as
the gate is written — not promised for later.

_Dr. Mārcis Gasūns_
