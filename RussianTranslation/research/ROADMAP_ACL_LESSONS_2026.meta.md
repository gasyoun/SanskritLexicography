# ROADMAP_ACL_LESSONS_2026.meta.md — metadoc for `ROADMAP_ACL_LESSONS_2026.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[ROADMAP_ACL_LESSONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md)
("Roadmap B"). It does not duplicate the subject's content; it records everything *around*
it. Kept per the standing "one metadoc per important document" convention
(`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [ROADMAP_ACL_LESSONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md)
- **Purpose:** "Roadmap B" — maps three ACL-adjacent literatures (BLI evaluation, sense-
  benchmark/WordNet lineage, Lexical Linked Data) onto layers `pwg_ru` already has, with a
  ground-truth section correcting naive assumptions (OntoLex already exists as a flat export,
  per-sense dating exists as a Renou proxy, DCS genre is per-lemma not per-sense) and a
  ruled decision log from an 08-07-2026 MG session.
- **Audience:** Whoever picks up B1 (BLI evaluation), B2 (sense-benchmark), or B3 (LLOD
  upgrade) work on `pwg_ru`'s interoperability exports.
- **Format / contract:** Explicitly complementary to
  [ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)
  ("Roadmap A") and
  [ACL_ANTHOLOGY_MONITOR.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ACL_ANTHOLOGY_MONITOR.md)
  — the doc states explicitly "complement, don't duplicate." A ground-truth section, three
  ranked work items (B1/B2/B3), a phasing table (Wave 0/1/2), and a decision log at the
  bottom (never edited retroactively — new decisions append as new rows).

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`) — this metadoc. The
  subject document itself dates to 08-07-2026 per its own header.
- **Next hardening:** none scheduled — revisit at the "Wave 2 (after ~50% coverage)" trigger
  named in the doc's own phasing table.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | B3 milestones 1–3 (real IRIs via w3id.org, `vartrans` sense-links, PROV-O provenance) | Named "Wave 1 (parallel with translation)" — the doc calls this a "quick win," deterministic edits to one exporter + its selftest | parked — Wave 1, no handoff minted at time of this metadoc |
| 2 | IndoWordNet rights check before the B2 synset crosswalk | Doc flags "Rights first" — IndoWordNet's license is restrictive; needs a Samsaadhanii/Kulkarni contact check before building | parked — Wave 1, `@DECIDE` on composition pending the license quote |
| 3 | B1 gold set + P@1/MRR scoring for `corpus_lexicon` | Named "Wave 2 (after ~50% coverage)" — sequenced deliberately after translation coverage, not a Wave-0/1 item | parked — Wave 2, coverage-gated |
| 4 | Reconcile with [RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md), which independently proposes overlapping BLI-evaluation work (its cards 2–3) one day later | Two sibling roadmaps under different numbering schemes describing the same B1/BLI work risks drift | parked — needs a human decision on which doc owns the actual BLI build task |

## Known limitations / caveats
- The doc's own "Ground truth" section is itself a correction of an earlier, more pessimistic
  reading of what `pwg_ru` already has (e.g. "OntoLex already exists... Upgrade, not
  stand-up") — treat the Ground truth section as the current authoritative baseline, not the
  original framing it corrects.
- Wave-gating (Wave 0 now / Wave 1 parallel-with-translation / Wave 2 after ~50% coverage)
  means B1/B2's headline gold-set work is intentionally not startable yet; check translation
  coverage in `RussianTranslation/.ai_state.md` before assuming Wave 2 is unlocked.
- Overlaps with `RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md` (see backlog item 4) — this doc
  and that one were not obviously cross-referenced against each other at authoring time.

## Intended use / known misuse
- **For:** understanding what ACL-literature-informed upgrade path exists for `pwg_ru`'s
  interoperability exports (OntoLex/TEI Lex-0) and sense-evaluation benchmarks before
  proposing a new one from scratch.
- **Misuse:** starting B1/B2 gold-set work before the Wave-2 coverage gate — the doc
  deliberately sequences model/benchmark phases after ~50% translation coverage, not before.

## Maintenance & sunset plan
- Owner: whoever drives `pwg_ru` ACL-literature-informed research work. No dedicated
  maintainer.
- Sunset: superseded once B1–B3 all land, or folded into
  [ACL_ANTHOLOGY_MONITOR.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ACL_ANTHOLOGY_MONITOR.md)
  if that becomes the standing complement doc's permanent home for this material.

## Deprecation status
`active` — Wave 0 in progress per the doc's phasing, Waves 1–2 not started.

## Related documents
- [ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md) — "Roadmap A," the explicit companion this doc cross-references.
- [ACL_ANTHOLOGY_MONITOR.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ACL_ANTHOLOGY_MONITOR.md) — the standing complement doc named at the top of the subject.
- [RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md) — overlapping BLI-evaluation scope, see backlog item 4.
- [REVIEW_AND_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md) — the higher-level pipeline roadmap this feeds into.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |

_Dr. Mārcis Gasūns_
