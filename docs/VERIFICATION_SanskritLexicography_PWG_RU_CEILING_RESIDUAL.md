# VERIFICATION — PWG→RU research-ceiling residual

_Created: 19-08-2026 · Last updated: 19-08-2026_

Index: [PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md).

Missing evidence is INCONCLUSIVE, never PASS
([PLAYBOOK_EVIDENCE_OF_DONE_2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/PLAYBOOK_EVIDENCE_OF_DONE_2026.md)).

## Per-unit gates

| Unit | PASS requires | FAIL looks like |
|---|---|---|
| **R5** | Three versioned frozen sets · annotator-2 freeze record (model id, prompt, params, date) · per-set κ + disagreement classes · written sampling frame per set · data statements · PROJECT_INTERLINKS rows | κ reported with the annotator-2 configuration unfrozen or undocumented · a gold set consumed by an evaluation inside the same handoff · a sampling frame left unstated |
| **R1** | Coverage table (windowed / undated-only / unresolvable) · C7 residue census with top unmapped abbreviations · 25-sense hand check against printed PWG · registration rows | A window emitted for a sense whose citations all resolve to undated works · any field phrased as sense *origin* · coverage computed only over resolvable citations |
| **R2** | Crosswalk row counts by `match_basis` **including** `unmatched` · OCR-noise class census · ≥50-row class-weighted adjudication · rights note (known vs still-human) · registration row | One merged "etymology" field mixing the traditional and modern-IE lanes · KEWA heading text committed as publishable content · an unmatched heading forced onto a near-miss headword |
| **R3** | Licence quoted **verbatim** with URL + retrieval date · fetchable inventory · `@DECIDE` row filed · parked draft + human `@DO` | A paraphrased licence · an email actually sent · a composed derived corpus before the `@DECIDE` is ruled |
| **R4** | Agreement vs the adjudicated set **and** engine-vs-engine, separately · classified disagreement table · request count + throttle interval + cache path · registration · phase-6 status flipped | An engine-vs-engine number with no reference to the adjudicated gold · an un-throttled bulk run against a live academic service · a canonical morphology overwritten |

## Programme-level gates

1. **The four source roadmaps tell the truth.**
   `python Uprava/tools/roadmap_handoff_truth.py` over all four must show no
   referenced handoff in a state the document contradicts.
2. **No silent caps.** Any shortfall against a stated sample size or scope is
   recorded in the close row. Silent truncation reads as full coverage.
3. **Every percentage carries its denominator.** A bare % anywhere in a close row
   fails this programme's reporting contract regardless of the underlying work.
4. **Claim discipline holds.** Spot-check the shipped artifacts for the five
   forbidden claims in the architecture doc's label table. A correct number under a
   wrong claim is a defect, not a rounding issue.

## The specific regressions this programme exists to prevent

**A roadmap that delegates its own mint.** Both CEILING (*"handoffs are minted after
H335 lands"*) and HERITAGE phase 6 (*"mints its own H### when its gate clears"*)
promised a mint at a future moment, and neither had a mechanism to notice that
moment. Both sat six weeks past their trigger while every mechanical scan reported
them drained — because a fully-closed handoff list reads as *finished*, not as
*waiting*.

**Standing check:** any future gate in these documents names the observable that
decides it, and where the gate is a handoff closing, the successor is queued at the
same time the gate is written.

**A blocker visible only per-card.** RESEARCH_CAPABILITY's `needs gold sample` flag
lives on individual cards; nothing at doc level says the roadmap is mostly blocked.
Its own metadoc names the consequence: a session picks a card up, gets halfway, and
discovers the blocker itself. **Standing check:** a prerequisite shared by three or
more items is stated once at document level, not only on each item.

_Dr. Mārcis Gasūns_
