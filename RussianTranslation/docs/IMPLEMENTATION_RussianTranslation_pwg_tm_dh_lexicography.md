# IMPLEMENTATION — PWG TM DH/Lexicography Wave 1

_Created: 13-08-2026 · Last updated: 13-08-2026_

Implementation layer of the [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_tm_dh_lexicography_2026H2.md).

## Track A — canonical migration and priority queue

1. Add `schemas/pwg_tm_canonical.schema.json` and fixtures; define persistent IDs, fragment classes, provenance, trust, rights facts, and supersession.
2. Add `src/pwg_tm_migrate_v1.py`; migrate the 2,392 publication records without changing source/Russian strings or losing hashes/provenance. Emit a reconciliation receipt: 2,392 in = 2,392 out, zero orphan IDs, zero lost fields.
3. Add `src/pwg_tm_fragmentize.py`; extract the six fragment classes deterministically and retain entry/sense context.
4. Add `src/pwg_tm_priority.py`; reuse canonical frequency, corpus-attestation, citation and lexical-core assets; emit a frozen top-5,000 manifest plus denominator/stratum report.

## Track B — Grok 4.6 scale generation and quality

5. Extend the existing bounded generation runner with a manifest-pinned Grok 4.6 route; never alter default production routes implicitly. Stamp exact model identity, prompt, context hashes, cost/usage, and outputs.
6. Process the 5,000 queue in resumable bounded windows. Run source anchoring, markup parity, Sanskrit preservation, sense/fragment completeness, duplication, residue, and provenance gates before canonical promotion.
7. Preserve below-threshold candidates in a quarantined evidence tier with explicit failure reasons; never silently discard or promote them.
8. Freeze a 400-fragment stratified sample spanning all six fragment classes, frequency bands, source complexity, confidence tiers, and accepted/rejected rows. Independent adjudication must not see Grok's self-assessment.
9. If the quality floor fails, diagnose by class, implement one bounded repair, rerun the affected slice and sample once; then halt that track honestly if still below floor.

## Track C — lossless interchange and release

10. Refactor `build_tmx.py` to consume canonical JSONL without duplicating export logic; retain existing compatibility behavior.
11. Add `src/export_pwg_tm_tei.py` plus ODD/RNG validation assets following TEI Lex-0 structure and a complete TEI header/revision history.
12. Add `src/export_pwg_tm_ontolex.py` using OntoLex, vartrans, lexicog only where necessary, and PROV-O. Add SHACL shapes and deterministic RDF serialization.
13. Add `src/pwg_tm_export_loss.py`; compare canonical field paths to all four exports and fail on unaccounted scholarly data.
14. Build immutable release artifacts and checksums; update datasheet/CITATION.cff/DataCite metadata; run the publish-safety gate under the standing risk-tolerant rights policy.
15. Tag and publish a GitHub release, mint/update the Zenodo record, verify DOI resolution and asset hashes, then update hubs/state with release and PR links.

## Track D — scholarly validation immediately after Wave 1

16. Activate a genuine semantic-QE backend and calibrate it against frozen gold; never label proxy results COMET.
17. Run `tm_retrieval_eval.py` with real translation/judge routes on the frozen batch, no-TM versus graded fragment-TM, and report quality, serious errors, latency, tokens and cost.
18. Use results to set the next 5,000-headword wave's ranking/reuse defaults; do not retroactively rewrite Wave 1.

## Operational discipline

Use isolated worktrees and targeted commits. Update `.ai_state.md` at each completed track. Never write source PWG/csl-orig. Keep the 1.09M corpus lexicon read-only. Append decisions/defaults to the run log. Rights uncertainty proceeds; confirmed block classes stop only the affected material.

_Dr. Mārcis Gasūns_

