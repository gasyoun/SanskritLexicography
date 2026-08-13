# ROADMAP — PWG Translation Memory DH/Lexicography Completion

_Created: 13-08-2026 · Last updated: 13-08-2026_

Roadmap layer of the [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_tm_dh_lexicography_2026H2.md).

## Wave 1 — canonical substrate and first 5,000 headwords

1. Freeze the audit baseline and migrate 2,392 publication records losslessly into canonical JSONL with stable record, entry, sense, and fragment IDs.
2. Build the fragment inventory across six classes: sense, definition/gloss, grammar label, citation, example, recurring formula.
3. Rank the first 5,000 headwords by corpus frequency/attestation, PWG citation value, reuse potential, and stratified coverage; publish the frozen queue manifest.
4. Run Grok 4.6 drafting with deterministic source/markup/fidelity gates and append-only provenance.
5. Independently adjudicate a frozen 400-fragment stratified sample. Pass only at ≥98% fidelity, ≥95% correct equivalence, and ≤1% serious error; allow one bounded repair/re-run.
6. Derive and round-trip JSONL, TMX, TEI Lex-0, and OntoLex/vartrans/PROV-O with zero lost scholarly fields.
7. Publish immutable GitHub release assets and a Zenodo record/DOI with rich machine-readable metadata.

## Wave 2 — semantic validation immediately after scale

- Run a genuine reference-free semantic QE backend against the frozen gold; distinguish its result from the current proxy (`rho=-0.0351`, preliminary).
- Run the live no-TM versus graded-fragment-TM retrieval experiment on the frozen batch.
- Grow the adversarial/human gold beyond the first 400 where confidence intervals or defect clustering require it.
- Tune fragment retrieval by class and measure tokens, latency, exact reuse, edit distance, and serious-error deltas.

## Wave 3 — continued PWG coverage

- Re-rank after Wave 1 using observed reuse yield and errors.
- Drain subsequent 5,000-headword waves, retaining the same immutable manifest, audit, and release discipline.
- Keep separate dashboards for headword/card coverage, sense coverage, fragment coverage, corpus-frequency coverage, and exact-reuse events.

## Non-goals

- No direct edits to PWG/csl-orig source.
- No second TMX emitter, transcoder, frequency table, or corpus alignment store.
- No silent replacement of uncertain records; changes use supersession edges.
- No claim that 5,000 queued headwords equals complete PWG coverage.
- No rights re-adjudication where facts are already recorded; uncertainty does not block publication.

_Dr. Mārcis Gasūns_

