# ROADMAP_VEDAWEB_REUSE.meta.md — metadoc for `ROADMAP_VEDAWEB_REUSE.md`

_Created: 18-07-2026 · Last updated: 01-08-2026_

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
- **Format / contract:** Phase 0–4 are all done (Phase 2 hub checkbox ticked 01-08-2026;
  validation itself shipped 03-07-2026 as H063). Historical phase bodies keep archive links;
  executed handoffs use `🔴 EXECUTED:` rather than live starters.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`).
- **Next hardening:** none scheduled — this roadmap is functionally complete; revisit only if
  a new VedaWeb layer is proposed.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Downstream a–f accent-mobility emission into ZALIZNYAK_INDEX, gated on Phase 2's per-cell GO/NO-GO | Explicitly named in the subject's "Dependency order" section as the one still-open follow-on outside this roadmap's own scope | **unblocked** 01-08-2026 (Phase 2 GO/NO-GO landed) — still parked as its own workstream, not owned by this roadmap |

## Known limitations / caveats
- All named phases (0–4) are marked done; treat the subject as **reference material**, not an
  active checkbox queue. The only residual is the external ZALIZNYAK a–f emission follow-on.
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
`active` (phases complete; residual is external follow-on only — backlog item 1).

## Related documents
- [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — §1 (API probe), §72/§73 (renumbered GRA crosswalk and rights findings) cited throughout the subject.
- [VisualDCS/non-derived/vedaweb/](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb) — the landed feed this roadmap describes.
- [WhitneyRoots crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json) — the first downstream consumer.
- [RussianTranslation/ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md) — the accent-axis emission target for the still-open follow-on.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |
| 01-08-2026 | Phase 2 hub tick already on master (#951); summary → COMPLETE; Phase 2 numbers corrected to 17/19 GO; H063 starter → EXECUTED; backlog item 1 unblocked | Grok 4.5 (`grok-4-1-thinking-0309-reasoning`), H2099 `/drain tier 1` |

_Dr. Mārcis Gasūns_
