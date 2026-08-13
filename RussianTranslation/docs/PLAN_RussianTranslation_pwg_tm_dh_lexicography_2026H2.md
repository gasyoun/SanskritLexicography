# PLAN — PWG Translation Memory to Digital-Humanities and Digital-Lexicography Standard

_Created: 13-08-2026 · Last updated: 13-08-2026_

This index turns the 13-08-2026 audit and twenty owner rulings into an unattended execution contract. The target is a fragment-first PWG German→Russian translation memory, queued by corpus frequency and attestation, with one canonical scholarly JSONL record and lossless TMX 1.4b, TEI Lex-0, and OntoLex-Lemon/vartrans exports. The first scale wave covers 5,000 frequent, corpus-attested headwords. It migrates the existing 2,392 publication records losslessly and prepares/releases the result through GitHub Releases and Zenodo.

Layer documents:

- [ROADMAP](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_pwg_tm_dh_2026H2.md)
- [ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_pwg_tm_dh_lexicography.md)
- [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pwg_tm_dh_lexicography.md)
- [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_pwg_tm_dh_lexicography.md)

## Audit verdict and denominators

The older plan's “~70% built” measured feature implementation, not PWG coverage. Current evidence requires two denominators:

| Denominator | Done | Left | Verdict |
|---|---:|---:|---|
| Publication-grade infrastructure | ~82% | ~18% | Strong substrate: canonical validators, exact/fragment reuse, manifests, TMX, terminology, rights audit, provenance, gold and alignment scaffolds exist. Residuals are real semantic QE, live retrieval measurement, stable lexicographic export, PID/discovery, and scale operations. |
| Exact-card headword coverage | 2,175 / 98,639 = **2.2%** | ~96,464 indexed headwords = **97.8%** | Corpus completeness is early. The first wave deliberately targets 5,000 high-value headwords rather than pretending whole-PWG completion. |
| Public exact + fragment TM | **2,392 / 2,392 validate** | Growing asset | 2,175 exact cards + 217 exact fragments; every publication record passed the canonical validator on 13-08-2026. |
| Corpus-derived structural TM | 1,093,391 rows | Semantic/rights metadata refinement | Reusable as evidence and prioritisation input. Russian surfaces may be used and published under the standing risk-tolerant policy unless a confirmed prohibition, explicit restricted designation, privacy issue, or platform constraint applies. |

Validation run on 13-08-2026: `translation_memory.py validate/selftest`, `build_tmx.py selftest`, `terminology_build.py selftest`, and `build_release_bundles.py selftest --audit-rights` all passed; the tracked bundles contained zero unintended grey-Russian leakage under the current partition.

## Decisions taken — owner rulings, 13-08-2026

| # | Ruling |
|---|---|
| R1 | Report infrastructure maturity and PWG coverage separately. |
| R2 | Coverage scaling first; scholarly semantic validation immediately after. |
| R3 | Require JSONL, TMX 1.4b, TEI Lex-0, and OntoLex-Lemon/vartrans. |
| R4 | Preserve uncertain translations with explicit confidence/provenance tiers; never silently discard them. |
| R5 | Full publication authority, including release and DOI actions. |
| R6 | Optimise reusable fragments first; report card/headword and fragment coverage separately. |
| R7 | One versioned scholarly JSONL record is canonical; all interchange formats are derived. |
| R8 | Queue by corpus frequency, corpus attestation, citation value, and representative strata. |
| R9 | Stable record/sense IDs, immutable manifests, and explicit supersession edges. |
| R10 | Publish through GitHub Releases and Zenodo with JSONL/TMX/TEI/RDF downloads and machine-readable metadata. |
| R11 | Wave 1 targets the top 5,000 corpus-attested headwords, then re-measures yield and quality. |
| R12 | Fragment classes: sense, definition/gloss, grammar label, citation, example, recurring formula. |
| R13 | Grok 4.6 drafts; deterministic fidelity gates; sampled independent adjudication. |
| R14 | Migrate all 2,392 existing publication records losslessly, retaining IDs and provenance. |
| R15 | Quality floor: ≥98% fragment fidelity, ≥95% correct equivalence, ≤1% serious error. |
| R16 | Independent stratified sample: 400 fragments. |
| R17 | All four exports round-trip/schema validate with zero lost scholarly fields. |
| R18 | On non-blocking ambiguity, apply the marked default, log, and continue. |
| R19 | Stop only for confirmed corruption; quality below floor after one repair; confirmed prohibition/restricted status; privacy/platform policy; or irrecoverable CI failure. |
| R20 | Full commit→PR→merge→release→Zenodo authority; never rewrite PWG source, destroy canonical stores, expose secrets/private data, or bypass a confirmed restriction. |

## Autonomy contract

**Ambiguity.** Apply the default encoded in this plan, append the decision and evidence to the run log, and continue. Do not create a new human decision for a foreseeable fork.

**Rights.** Rights uncertainty is not a stop condition, including publication. Record known facts once and proceed. Only confirmed prohibition, explicit restricted-data designation, privacy exposure, or platform-policy constraints stop an affected asset. Do not re-investigate already recorded uncertainty.

**Stop conditions.** Halt the affected track only after one bounded repair attempt if data corruption is confirmed, the R15 quality floor still fails, a confirmed block class applies, or CI cannot be recovered without leaving scope. Continue independent tracks.

**Authority.** Grok 4.6 may work in isolated branches/worktrees; commit, push, open and merge green PRs; create GitHub releases; run the publish-safety check under the standing policy; and mint/update Zenodo records when credentials permit.

**Fence.** Never edit the source PWG/csl-orig text; never overwrite or delete canonical stores or the 1.09M-row corpus asset; never expose secrets/private data; never bypass a confirmed restriction; never conceal uncertainty, provenance, exclusions, or failed quality results.

## Prior-art verdict

**PARTIAL — build only the gap.** Reuse `translation_memory.py`, `build_tmx.py`, `tm_grade.py`, `tm_align.py`, `tm_saru_align_labse.py`, the publication schema/manifests, `corpus_lexicon`, frequency assets, existing OntoLex/PROV-O fixtures, and the release/terminology builders. Build the canonical fragment model, priority queue, lossless exporters, migration, scale runner, evaluation ledger, and PID/discovery release surface. Do not build a second transcoder, TMX emitter, frequency dataset, or provenance system.

## Autonomy-readiness gate

**PASS.** Every wave-1 deliverable has an architecture contract, ordered implementation steps, acceptance proof, risks, and a default. Zero blocking `@DECIDE` items remain. External credentials are operational dependencies, not design forks; if unavailable, prepare immutable release artifacts and resume publication when available without changing architecture.

_Dr. Mārcis Gasūns_

