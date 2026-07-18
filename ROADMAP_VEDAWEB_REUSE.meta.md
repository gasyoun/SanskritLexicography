# ROADMAP_VEDAWEB_REUSE.meta.md — metadoc for `ROADMAP_VEDAWEB_REUSE.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[ROADMAP_VEDAWEB_REUSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [ROADMAP_VEDAWEB_REUSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md)
- **Purpose:** Tracks reuse of VedaWeb 2.0 (Universität zu Köln) data across the org — a
  5-phase plan (bulk export, WhitneyRoots accent validation, GRA crosswalk, meter/translation
  rights triage, plus a queued segmenter-service phase) with the feed landing in VisualDCS.
- **Audience:** Sessions consuming VedaWeb-derived data (WhitneyRoots accent rules,
  RussianTranslation's Elizarenkova witness, SanskritKaraoke meter seeds, PWG German gloss
  witness) or checking VedaWeb licensing before a new use.
- **Format / contract:** Phase 0–4 (all done) + a still-queued follow-on ("Phase 2:
  WhitneyRoots accent-validation run") — each phase carries an executable one-line handoff
  starter (`Read <path> and execute it.`) per the org's session-starters contract. Any new
  phase gets the same starter-line treatment.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`).
- **Next hardening:** none scheduled — this roadmap is functionally complete; revisit only if
  a new VedaWeb layer is proposed.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Downstream a–f accent-mobility emission into ZALIZNYAK_INDEX, gated on Phase 2's per-cell GO/NO-GO | Explicitly named in the subject's "Dependency order" section as the one still-open follow-on outside this roadmap's own scope | parked — tracked as its own follow-on, not owned by this doc |

## Known limitations / caveats
- All 5 named phases (0–4) are marked done; the doc is close to fully executed — treat it as
  near-final reference material, not an active work queue, aside from the one flagged
  follow-on above.
- Rights note: only 2/36 VedaWeb catalog resources originally carried an explicit `license`
  field; the blanket "CC BY 4.0" framing was an unverified assumption at triage time, later
  confirmed in writing by VedaWeb (Kölligan/Reinöhl) for all 4 candidate meter/translation
  layers — cite the confirmation (§ Phase 4), not the original assumption, if provenance
  matters.
- Advisory-only constraint: VedaWeb-derived signal must never be written into reviewed/human
  data (spines, `headword_index.tsv`, app data) — the doc calls this out explicitly as "the
  I/VI accent-collapse lesson."

## Intended use / known misuse
- **For:** finding what VedaWeb data already exists as a registered feed before re-scraping
  the API, and citing the correct CC BY 4.0 attribution + rights-confirmation trail for any
  VedaWeb-derived layer used in a paper or export.
- **Misuse:** re-running the Phase 0/1 API probe or bulk export from scratch — the feed is
  already landed under `VisualDCS/non-derived/vedaweb/`; consume it, don't rebuild it.

## Maintenance & sunset plan
- Owner: whoever next touches VedaWeb-derived data (VisualDCS side owns the feed; this repo
  owns the roadmap doc). No dedicated maintainer.
- Sunset: once the one remaining follow-on (accent-mobility emission) lands or is explicitly
  deprioritized, this roadmap is fully executed — retitle as archived/historical rather than
  deleting, since it is the authoritative record of the VedaWeb rights-confirmation trail.

## Deprecation status
`active` (functionally near-complete — see backlog item 1 for the one open thread).

## Related documents
- [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — §1 (API probe), §72/§73 (renumbered GRA crosswalk and rights findings) cited throughout the subject.
- [VisualDCS/non-derived/vedaweb/](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb) — the landed feed this roadmap describes.
- [WhitneyRoots crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json) — the first downstream consumer.
- [RussianTranslation/ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md) — the accent-axis emission target for the still-open follow-on.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |

_Dr. Mārcis Gasūns_
