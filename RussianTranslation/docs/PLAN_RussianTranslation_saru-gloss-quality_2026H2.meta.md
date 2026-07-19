# Metadoc — PLAN_RussianTranslation_saru-gloss-quality_2026H2.md

_Created: 19-07-2026 · Last updated: 19-07-2026_

**Subject doc:** [PLAN_RussianTranslation_saru-gloss-quality_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_saru-gloss-quality_2026H2.md)

## Purpose
Execution-ready plan for the Sa→Ru gloss-layer quality uplift — the index a fresh agent reads to
run waves 1–4 unattended (5–8 h). Produced by `/ask` (heavy up-front interview → layered plan).

## Audience
The execution agent (Opus 4.8, per handoff H1349) and MG for the gated republish decision (D8).

## Provenance
- Interview: 19-07-2026, Opus 4.8 (`claude-opus-4-8`), 4 rounds × 4 questions, all ruled.
- Audit inputs: two Explore agents (data repo `gasyoun/SanskritRussian` + pipeline
  `RussianTranslation/`), prior-art probe confirming `vidyut.cheda` v0.4.0 + `kosha` segmentation bench.
- Handoff: [H1349-Opus_RussianTranslation_saru-gloss-quality-uplift_19.07.26](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1349-Opus_RussianTranslation_saru-gloss-quality-uplift_19.07.26.md).

## Ranked improvement backlog (for the plan itself)
1. After wave 2 lands a real precision number, fold it into the goal paragraph (currently states only the 84.4 % upstream ceiling).
2. If MG approves the D8 republish, add a wave-1.5 "regen + v2.0.0 release" section.
3. Wave 4's pwg_ru integration surface may collide with the open safety-plan PRs (#547/#550); revisit the fence once those merge.

## Limitations
- The autonomy-gate PASS assumes the fenced inputs (`dcs_full.sqlite`, vidyut kosha, corpus_lexicon) are present at run time; the plan makes their absence a stop-condition rather than pre-verifying at authoring time beyond the prior-art probe.
- Waves 2–4 step lists are sketches; each wave authors its own full step list at start (by design — the plan front-loads decisions, not every keystroke).

## Related docs
- [[ROADMAP_RussianTranslation_saru-gloss_2026H2]] · [[ARCHITECTURE_RussianTranslation_saru-gloss]] · [[IMPLEMENTATION_RussianTranslation_saru-gloss]] · [[VERIFICATION_RussianTranslation_saru-gloss]]
- Canonical data/method doc (after W1.4): `gasyoun/SanskritRussian/README.md`

## Revision history
| Date | Change | By |
|---|---|---|
| 19-07-2026 | Created with the plan set (`/ask`) | Opus 4.8 |

_Dr. Mārcis Gasūns_
