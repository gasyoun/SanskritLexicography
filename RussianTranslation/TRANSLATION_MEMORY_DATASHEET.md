# Translation Memory Datasheet Template

_Created: 04-07-2026_

Use this template whenever a PWG/RU translation-memory sidecar is promoted from
local speed cache to a reviewable scholarly artifact. It follows the repository
decision log in `TRANSLATION_MEMORY_DECISIONS.md`: exact TM may auto-reuse only
when gated; fuzzy/suggestion TM is advisory; MW-derived English may affect RU
only through curated Sanskrit-to-Russian terminology.

## Dataset Identity

- **Dataset name:**
- **Version/date:**
- **Maintainer/curator:**
- **Related schema:** `schemas/translation_memory.schema.json`
- **Files covered:** exact card TM, exact fragment TM, suggestion/terminology TM
- **Languages:** Sanskrit source keys; German PWG source fragments; Russian target
  translation; optional English evidence only in hidden curation steps.

## Sources And Scope

- **Primary source dictionary:** PWG source record(s), with raw input hash.
- **Derived source units:** card addresses and fragment addresses.
- **Auxiliary evidence:** curated Sanskrit-to-Russian terminology, corpus evidence,
  reviewed translation rows, and machine-gated draft rows.
- **Excluded evidence:** raw MW English in RU prompts; ungated machine output for
  publication claims; fuzzy suggestions treated as completed output.

## Provenance

For each row, preserve when available:

- source key, root, raw SHA-256, fragment SHA/address formula;
- source file or workflow file;
- model/provider alias and exact model version;
- script/gate version;
- gate status and review status;
- curator/reviewer id for human-reviewed or terminology rows;
- supersession links for replaced entries.

## Evidence And Scores

Exact TM rows are reusable only through content addresses and trust gates.
Suggestion rows must preserve separate fuzzy evidence channels:

- `score_de_fragment`: German source-fragment similarity.
- `score_sa_headword`: Sanskrit headword/key similarity.
- `score_semantic_tag`: normalized semantic-tag similarity.
- `score_combined`: optional sorting score only; never the sole evidence.

## Intended Uses

- zero-token exact reuse for draft windows when content hashes and gates match;
- advisory prompt context from fuzzy/terminology evidence;
- scholarly audit of how a translated sense entered the edition;
- later publication or release documentation after human review gates pass.

## Non-Intended Uses

- treating fuzzy suggestions as exact reuse;
- using raw MW English as RU translation evidence in prompts;
- citing machine-only rows as print-ready;
- collapsing the three fuzzy evidence channels into one opaque score.

## Known Risks

- content-addressed exact TM does not know whether a previous translation failed
  a later audit unless defect rows or denylist rows are recorded;
- fuzzy matches can be lexically close but semantically wrong;
- Sanskrit homonyms and derivationally related forms require separate evidence;
- human-reviewed rows must supersede newer machine rows when both exist.

## Validation

Before using or publishing a TM sidecar, run:

```powershell
python src\pilot\translation_memory.py validate --lang ru
python src\pilot\translation_memory.py selftest
python src\pilot\window_selftest.py
```

Publication notes should report row counts by trust tier, validation statistics,
known skipped/invalid rows, and any manual review coverage.
