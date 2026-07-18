# REVIEW_AND_ROADMAP.meta.md — metadoc for `REVIEW_AND_ROADMAP.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[REVIEW_AND_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [REVIEW_AND_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md)
- **Purpose:** The candid retrospective + phased forward plan (A–D) for the `pwg_ru` pipeline
  (PWG → corpus-attested Russian edition) — what was built, what's good, what's honestly bad
  (unmeasured precision, flat sense-bag microstructure, the frequency-first pivot), and the
  roadmap from proving the output through publication.
- **Audience:** Anyone picking up `pwg_ru` work — this is the single-document orientation for
  "what state is this pipeline actually in," distinct from the deeper theory/methodology
  companions it names.
- **Format / contract:** §1 What was built (pipeline diagram) → §2 What is good → §3 What is
  bad / honest weaknesses → §4 Roadmap (Phase A–D) → §5 Immediate plan (frequency-first
  tranche). Companion docs are named at the top, not restated. Machine-readable companions
  (`roadmap/scientific_hardening.json`, `roadmap/quality_gates.jsonl`) are the canonical
  phase/gate record — this Markdown file is the human-readable narrative, validated against
  those JSON/JSONL files via `python src/roadmap_check.py`.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`) — this metadoc. The
  subject document itself dates to 09-07-2026 per its own header, describing a build the
  header's title labels "(2026-06-16)".
- **Next hardening:** none scheduled — revisit when Phase A (corpus-first re-harvest of the
  216 a-section cards) completes, since §3's "honest weaknesses" list is keyed to that not-yet-
  done state.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Phase A — corpus-first re-harvest + re-translate the 216 a-section cards | Explicitly named "the immediate next action" in §3; the a-section cards are still the OLD provisional translations from before the corpus lexicon existed | parked — no handoff minted at time of this metadoc; check `.ai_state.md` for current status before assuming still pending |
| 2 | Gold standard + precision/recall with Wilson CIs (Phase B item 1) | §3 flags "Precision is unmeasured... the single most important gap before any print claim" | parked — Phase B, sequenced after Phase A |
| 3 | Lexicographic microstructure (sense tree, homonym `h`-keying, `equivalence_type`, diasystem labels — Phase B item 2) | §3: "Cards are still a flat sense-bag... The Apresyan 'portrait' is on paper," not built | parked — Phase B |
| 4 | Reconcile this doc's frequency-first pivot ordering with the card-level research roadmaps ([RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md), `research/ROADMAP_ACL_LESSONS_2026.md`, `research/ROADMAP_CEILING_2026.md`) | Four `pwg_ru`-adjacent roadmap docs authored within days of each other risk sequencing conflicts if not read together | parked — needs a human decision on canonical sequencing owner |

## Known limitations / caveats
- §3's weaknesses list is a point-in-time honest assessment (dated 09-07-2026 in the header,
  describing a 2026-06-16 build) — re-check `.ai_state.md` and `CHANGELOG.md` in
  `RussianTranslation/` before assuming any listed weakness (e.g. "precision is unmeasured")
  still holds; this metadoc does not re-verify current pipeline state.
- The doc explicitly separates itself from four companion docs
  (`METHODOLOGY_REVIEW.md`, `APRESJAN.md`, `HARVEST.md`, `failures/FAILURE_GALLERY.md`,
  `CHANGELOG.md`) — reading this doc alone gives the roadmap but not the theoretical grounding
  or the failure-mode detail.
- Cost tracking in §3 ("~30% over estimate, ~$49 vs ~$37") is specific to the a-section run;
  do not extrapolate that overrun ratio to the full-PWG scale-up without re-measuring on a
  representative sample, per the doc's own caveat.

## Intended use / known misuse
- **For:** orienting a fresh session on `pwg_ru`'s actual current state and honest gaps before
  making a claim about pipeline quality or picking the next phase to work.
- **Misuse:** citing §2's "what is good" list as a print-quality claim — the doc itself states
  in §3 that precision is unmeasured and no gold standard exists yet, so quality claims are
  provisional until Phase B lands.

## Maintenance & sunset plan
- Owner: whoever is driving the `pwg_ru` pipeline (RussianTranslation subsystem). No
  dedicated maintainer named in the doc.
- Sunset: superseded when Phase D (publish: TEI Lex-0/OntoLex export, CITATION.cff, edition
  freeze) ships — at that point this becomes a historical retrospective rather than an active
  roadmap; archive with a pointer to the published edition rather than deleting.

## Deprecation status
`active` — Phase A explicitly named as the immediate next action, not yet complete as of this
metadoc's authoring.

## Related documents
- [METHODOLOGY_REVIEW.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/METHODOLOGY_REVIEW.md) — the 5-lens external review companion.
- [APRESJAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/APRESJAN.md) — the theoretical grounding companion.
- [HARVEST.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/HARVEST.md) — the harvest-layer companion.
- [RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md) — the card-level research programme this roadmap's phases feed into.
- [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) — required prior reading before touching `pwg_ru` code.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |

_Dr. Mārcis Gasūns_
