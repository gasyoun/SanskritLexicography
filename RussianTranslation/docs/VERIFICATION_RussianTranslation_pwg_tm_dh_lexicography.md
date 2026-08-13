# VERIFICATION — PWG TM DH/Lexicography Wave 1

_Created: 13-08-2026 · Last updated: 13-08-2026_

Verification layer of the [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_tm_dh_lexicography_2026H2.md).

## Acceptance matrix

| Deliverable | Pass condition |
|---|---|
| Baseline | Existing publication validator reports 2,392/2,392 valid; TM, TMX, terminology and release-rights selftests green. |
| Migration | Exactly 2,392 records migrate; source/Russian strings, hashes, provenance and reuse semantics are lossless; stable IDs unique and deterministic. |
| Fragment model | All six classes validate; every fragment points to entry/sense/source context; no orphan or overlapping-address ambiguity. |
| Priority queue | Exactly 5,000 unique headwords; all input hashes/weights/ranks/exclusions frozen; frequency and representative strata reported. |
| Generation | Every output has exact Grok 4.6/model/prompt/source/pipeline provenance and deterministic gate receipts; no unaccounted promotion. |
| Independent quality | On 400 stratified fragments: **≥98% fidelity, ≥95% correct equivalence, ≤1% serious error** with confidence intervals and per-class counts. |
| Uncertain rows | Retained with explicit tier and reason; zero silent drops; automatic reuse forbidden unless compatible exact-address gates pass. |
| Interchange | JSON Schema, TMX validation, TEI RNG/Schematron, RDF parse + SHACL all pass; round-trip identity and `pwg_tm_export_loss` show zero lost scholarly fields. |
| FAIR release | PID/DOI resolves; metadata contains identifier, provenance, license/rights facts, version, citation, access URL and checksums; GitHub and Zenodo assets hash-match. |
| Coverage report | Headword/card, sense, fragment, token-frequency, corpus-attestation and exact-reuse coverage are separate denominators. |
| Semantic follow-up | Genuine QE reports backend and gold correlation; live retrieval A/B reports quality/error/latency/token/cost deltas without mock numbers. |

## Required proof commands

The executor may refine CLI names while preserving these proofs:

```powershell
python src/pilot/translation_memory.py validate --lang ru
python src/pilot/translation_memory.py selftest
python src/pwg_tm_migrate_v1.py --verify
python src/pwg_tm_fragmentize.py --verify
python src/pwg_tm_priority.py --verify --limit 5000
python src/pwg_tm_quality.py verify --sample 400
python src/build_tmx.py validate release/pwg_tm/*.tmx
python src/export_pwg_tm_tei.py --validate
python src/export_pwg_tm_ontolex.py --validate-shacl
python src/pwg_tm_export_loss.py --all-formats
python src/build_release_bundles.py --audit-rights
```

## Risks and required responses

| Risk | Response/default |
|---|---|
| Frequent entries are structurally harder and depress quality | Stratify by complexity; repair once; do not weaken R15. |
| Fragment reuse leaks a translation across senses | Context-bearing address + exact compatibility gates; approximate matches remain advisory. |
| Existing records cannot map cleanly to senses | Preserve entry-level record plus explicit unresolved alignment; no invented sense link. |
| TEI/RDF cannot express a local field directly | Use documented extension/property with stable URI; loss ledger must remain complete. |
| Rights are uncertain | Record known facts once and proceed, including publication. Only confirmed block classes stop. |
| Zenodo/API credentials unavailable | Freeze release candidate and checksums; retry publication without architectural change. |
| Quality floor fails | One bounded class-specific repair and rerun; if still red, halt scale track and publish the negative audit, not deficient data as green. |
| Source/canonical corruption | Stop immediately; preserve evidence; never repair by editing PWG source. |

## Autonomy-ready verdict

**PASS:** architecture, ordered steps, acceptance evidence, risks/defaults, authority and fences are specified for every Wave-1 deliverable; no blocking choice remains.

_Dr. Mārcis Gasūns_

