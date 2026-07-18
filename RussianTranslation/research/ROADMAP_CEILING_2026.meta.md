# ROADMAP_CEILING_2026.meta.md — metadoc for `ROADMAP_CEILING_2026.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)
("Roadmap A"). It does not duplicate the subject's content; it records everything *around*
it. Kept per the standing "one metadoc per important document" convention
(`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)
- **Purpose:** "Roadmap A" — an honest ceiling analysis of what the PWG→RU dictionary
  *cannot* answer without an external model or dated corpus bolted on (in-context WSD,
  sense chronology, frequency outside DCS, modern etymology, register/pragmatics, scholarly
  consensus, citation residue, cross-lingual vocabulary), with each of 8 items (C1–C8) ruled
  by MG on 08-07-2026 as BUILD / PARTIAL / STAYS-OUT, plus the bolt-on named for each.
- **Audience:** Whoever needs to know, before making a claim, whether `pwg_ru` can actually
  answer a given question (e.g. "which sense is live in this passage") or whether that
  requires an explicitly named external bolt-on.
- **Format / contract:** A single ceiling-item table (C1–C8: Verdict + bolt-on), a phasing
  section (Wave 0/1/2), and a decision log (MG rulings, 08-07-2026) at the bottom — the
  decision log is append-only, ruled forks are not re-litigated without a new MG session.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`) — this metadoc. The
  subject document itself dates to 08-07-2026 per its own header.
- **Next hardening:** none scheduled — revisit at the "Wave 2 (after ~50% translation
  coverage)" trigger named in the doc's own phasing table.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | C2 Phase 1 — join each sense's `<ls>` citations to `ls_source_map.json`'s date/period/renou fields for a per-sense attestation window | Named "Wave 1 (parallel with translation, cheap derivables)" — deterministic, no external dependency | parked — Wave 1, no handoff minted at time of this metadoc |
| 2 | C4 — KEWA normalization + join using the already-OCRed KEWA index | Rights are unlocked (MG holds written Mayrhofer permission); the index already exists on disk — this is a "locate + quote terms verbatim, then join" task, not new acquisition | parked — Wave 1; GTD `@DO` to locate/quote the permission terms verbatim before publication-tier use |
| 3 | C8 — DharmaMitra license-gated probe + outreach draft | Named Wave 1; rights-gated, so gated on `/license-gated-ingest` + `/outreach-draft` completing first | parked — Wave 1, rights-gated |
| 4 | C1 embedding-WSD baseline + gold set (Wave 2) | Sequenced deliberately after ~50% translation coverage per the doc's own phasing — the highest-value ceiling item (in-context WSD) but intentionally not startable yet | parked — Wave 2, coverage-gated |

## Known limitations / caveats
- Every C-item verdict (BUILD / PARTIAL / STAYS-OUT / STAYS-PROXY / MEASURE+SHRINK / PROBE)
  was a human ruling on 08-07-2026, not a technical default — re-litigating a verdict (e.g.
  "why can't we just build C6 consensus-meaning resolution") needs a new MG session, not a
  unilateral re-read of the ceiling table.
- C3 ("Frequency outside DCS") is explicitly "STAYS PARTIAL forever" by design — DCS is a
  sample, and the doc is explicit that widening it (GRETIL ingestion) "never closes the
  inference gap." Do not read future GRETIL work as eventually promoting C3 to BUILD.
- Overlaps with `ROADMAP_ACL_LESSONS_2026.md`'s B1 (BLI, adjacent to but distinct from this
  doc's C1 WSD) — the two roadmaps share a phasing rhythm (Wave 0/1/2) and were authored the
  same day, but cover different ceiling items; cross-check both before assuming either is
  exhaustive for "what pwg_ru's research programme covers."

## Intended use / known misuse
- **For:** checking, before publishing a claim from `pwg_ru`, whether the dictionary alone
  supports it or whether it needs an explicitly named external bolt-on (and what that bolt-on
  is) per the C1–C8 table.
- **Misuse:** treating a "PARTIAL" or "STAYS PROXY" verdict as eventually resolvable to full
  coverage — several items (C3, C5) are explicitly permanent ceilings by the ruling, not
  temporary gaps.

## Maintenance & sunset plan
- Owner: whoever drives `pwg_ru`'s research-capability work. No dedicated maintainer.
- Sunset: individual C-items get struck/updated as their bolt-ons land (e.g. C4 once KEWA
  join ships); the doc as a whole sunsets only if a future ruling session revisits and
  re-rules the ceiling wholesale.

## Deprecation status
`active` — Wave 0 in progress per the doc's phasing, Waves 1–2 not started.

## Related documents
- [ROADMAP_ACL_LESSONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md) — "Roadmap B," the explicit companion this doc cross-references.
- [ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json) — the per-work dating source C2 Phase 1 joins against.
- [LEARNER_APPARATUS_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/LEARNER_APPARATUS_SPEC.md) — documents the KEWA dhātu-form join gotcha referenced under C4.
- [REVIEW_AND_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md) — the higher-level pipeline roadmap this feeds into.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |

_Dr. Mārcis Gasūns_
