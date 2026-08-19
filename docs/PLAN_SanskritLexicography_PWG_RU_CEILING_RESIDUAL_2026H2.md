# PLAN — PWG→RU research-ceiling residual programme, 2026 H2 (index)

_Created: 19-08-2026 · Last updated: 19-08-2026_

Authored by Opus 5 (`claude-opus-5`) under
[H3001 (Opus 5) — Stale-roadmap slice 3: full /ask replan of stale Tier-1 roadmaps](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3001-Opus_multi_stale-roadmap-s3-tier1-ask-replan_17.08.26.md).
Slice-3 index: [PLAN_UPRAVA_STALE_ROADMAP_ASK_BATCH_2026-08.md](https://github.com/gasyoun/Uprava/blob/main/docs/PLAN_UPRAVA_STALE_ROADMAP_ASK_BATCH_2026-08.md).

## Why this programme exists

Four SanskritLexicography roadmaps were flagged stale by the 17-08-2026 staging
sweep. The slice-3 truth-pass ran
[`roadmap_handoff_truth.py`](https://github.com/gasyoun/Uprava/blob/main/tools/roadmap_handoff_truth.py)
over all four: **every handoff they reference is closed ✅**. None is superseded;
all four stay living. What they share is a single structural failure —

> **Three of the four are gated on a prerequisite that has already landed, and each
> one delegates its own mint to a step that never ran.**

[ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)
says it plainly: *"Handoffs for Wave 1 items are minted after
[H335](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H335-Fable_RussianTranslation_pipeline-capability-audit_08.07.26.md)
lands (its specs set their schemas)."* H335 closed ✅ on 08-07-2026. Six weeks
later not one Wave 1 handoff existed. The same shape holds for
[HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md)
phase 6 (*"mints its own H### handoff when its gate clears"* — the gate was never
closed to begin with).

A roadmap that delegates its own mint to a future moment has no mechanism to notice
that moment arriving. This programme mints what those four documents were waiting
for.

## The five documents

| Layer | Document |
|---|---|
| Index (this) | [PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md) |
| Roadmap | [ROADMAP_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md) |
| Architecture | [ARCHITECTURE_SanskritLexicography_PWG_RU_CEILING_RESIDUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_RU_CEILING_RESIDUAL.md) |
| Implementation | [IMPLEMENTATION_SanskritLexicography_PWG_RU_CEILING_RESIDUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_RU_CEILING_RESIDUAL.md) |
| Verification | [VERIFICATION_SanskritLexicography_PWG_RU_CEILING_RESIDUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_PWG_RU_CEILING_RESIDUAL.md) |
| Metadoc | [PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.meta.md) |

## Source documents truth-passed

| Roadmap | Verdict | What was corrected |
|---|---|---|
| [ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md) | living, phasing stale | "Wave 0 (now)" read as current though H335 closed 08-07-2026. Wave 1 (C2p1, C4, C8) is mintable and now minted |
| [HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md) | living, **honest** | Body was accurate (phases 0–5 ✅ with evidence, 6 ⬜). Its **metadoc** was stale — claimed phase 3 still queued after it executed 26-07-2026. Metadoc corrected; phase 6 minted |
| [RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md) | living, **trap** | Multiple cards silently blocked on a gold set nothing marks as blocking. Blocker surfaced at doc level; gold-set build minted |
| [REVIEW_AND_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md) | living, one stale claim | "**Build (next step):** `freq_route.py`" — [`src/freq_route.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/freq_route.py) and `scale_manifest.freq.json` both exist. Corrected in place |

**Nothing was archived.** All four metadocs read `active`, and the slice-1 mechanic
(`git mv` to `archive/` + tombstone) applies to none of them —
[H2999 (Sonnet 5) — slice 1: archive superseded roadmaps](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2999-Sonnet_multi_stale-roadmap-s1-archive-superseded_17.08.26.md)
reached the same conclusion for its two SanskritLexicography candidates and skipped
them for the same reason.

## Decisions carried in (the interview)

Per slice-3 ruling **R3**, the batch rulings are the interview. Inherited from the
CEILING decision log (MG, 08-07-2026), not re-opened:

| # | Ruling carried forward |
|---|---|
| WSD approach | Both in sequence — embedding baseline first (it *becomes* the eval harness), then a DharmaMitra probe on the **same** gold set |
| DharmaMitra depth | License-gated ingest + outreach. Not API-only, not skipped |
| Sense dating | BOTH, phased — derive from existing maps now, curated scholarly table later |
| Etymology | Own cross-dictionary layer **plus** KEWA/EWA under Mayrhofer's emailed permission; two lanes, separately labelled |
| Gold / κ | Single-annotator constraint → model as annotator 2, **frozen and documented**, `/gold-adjudicate`. Human recruiting parked for 2026 |
| Sequencing | Audit → cheap derivables → model/benchmark phases after ~50 % translation coverage |
| C3, C5, C6 | **Permanent ceilings by ruling**, not temporary gaps. Do not re-propose |

## Residual units

| # | Unit | Handoff | Gate |
|---|---|---|---|
| R1 | C2 phase 1 — per-sense attestation window | [H3168 (Sonnet 5) — Ceiling C2 phase 1: per-sense attestation window](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3168-Sonnet_SanskritLexicography_ceiling-c2p1-sense-attestation-window_19.08.26.md) | none — deterministic |
| R2 | C4 — KEWA normalization + dhātu-aware join | [H3169 (Opus 5) — Ceiling C4: KEWA index normalization and join](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3169-Opus_SanskritLexicography_ceiling-c4-kewa-normalize-join_19.08.26.md) | rights known, not blocking (derived use only) |
| R3 | C8 — DharmaMitra license-gated probe + outreach draft | [H3170 (Sonnet 5) — Ceiling C8: DharmaMitra probe plus outreach draft](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3170-Sonnet_SanskritLexicography_ceiling-c8-dharmamitra-probe-outreach_19.08.26.md) | none for measuring; composition is an `@DECIDE` |
| R4 | Heritage phase 6 — segmenter-as-service cross-validation | [H3171 (Sonnet 5) — Heritage phase 6: segmenter-as-service cross-validation](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3171-Sonnet_SanskritLexicography_heritage-phase6-segmenter-service_19.08.26.md) | none — "can run whenever" |
| R5 | Shared gold sets (WSD 200 + COMET-QE slice + BLI 300) | [H3172 (Opus 5) — Shared gold sets unblocking WSD and BLI](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3172-Opus_SanskritLexicography_pwgru-shared-gold-wsd-bli_19.08.26.md) | none — the ruled protocol needs no second human |

## Not mintable — recorded so they stop being invisible

| # | What | Why an agent must not do it | The concrete human act |
|---|---|---|---|
| N1 | Rule which document owns the BLI/WSD build | Three roadmaps authored the same week (08–09-07-2026) describe overlapping BLI and WSD work under different numbering — CEILING C1, ACL_LESSONS B1, RESEARCH_CAPABILITY cards 3–4. Picking a canonical owner is an editorial judgment about a research programme's shape, not a technical fact an agent can read off the files | A human names one document as canonical for BLI and one for WSD. Until then R5 builds the gold sets all three would share, so **nothing waits on this** — only the eventual build assignment does |
| N2 | Locate and transcribe Mayrhofer's permission email verbatim | The email is not in any repo; an agent cannot search a personal mailbox, and paraphrasing licence terms is exactly what the rights discipline forbids | A human finds the email and pastes its terms into the repo. This gates **publication-tier** use of KEWA text only. R2 (derived join, no KEWA text published) proceeds without it |
| N3 | Send the Huet outreach ([H121](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H121-Opus_SanskritLexicography_OUTREACH_2026-07-03_gerard_huet_heritage_03.07.26.md)) and the DharmaMitra outreach R3 drafts | Sending correspondence to a named scholar on the org's behalf is a human act | A human reads each draft and sends or declines. Heritage phase 6 (R4) needs neither |
| N4 | Rule the DharmaMitra composition `@DECIDE` R3 files | A redistribution ruling on third-party licensed data | A human rules once R3 has quoted the licence verbatim |

## Non-goals (do not re-propose)

- **C3** (frequency outside DCS) is *STAYS PARTIAL* **forever** by ruling — DCS is a sample and widening it never closes the inference gap. Future GRETIL work does not promote C3 to BUILD.
- **C5** (register/pragmatics) *STAYS PROXY*; **C6** (consensus meaning) *STAYS OUT*. Both are permanent by ruling, not backlog.
- **Wave 2** items — C1 embedding WSD baseline, C2 phase 2 curated dating table, the C1 DharmaMitra probe — are coverage-gated at ~50 % translation and deliberately not minted here.
- No `csl-orig` dictionary text. No canonical-store mutation. No paid PWG run.

## Autonomy contract

1. **Ambiguity** → marked default, one log line, continue.
2. **Hard stop** → about to send outreach; about to publish KEWA heading text or a composed DharmaMitra corpus; about to mutate the canonical store or spend a paid PWG run; about to edit a guarded main checkout.
3. **Not a stop** → N1–N4 unruled. Rights *uncertainty* is not a stop ([standing policy](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md)); confirmed prohibition is.
4. **Commit authority** → session-unique worktree off `origin/master` → PR → merge.

_Dr. Mārcis Gasūns_
