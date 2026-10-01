# H4733 — Wisdomlib L8 × CDSL headwords crosswalk report

_Created: 15-09-2026 · tier: OxAlpha (opencode/z-ai/glm-5.3-flash)_

## Inputs (provenance)

| input | sha256 (first 12) | rows |
|---|---|---|
| wisdomlib-sanskrit-layers L8 `l8_definitions_index.tsv` (CC BY 4.0, Zenodo DOI 10.5281/zenodo.22117832) | `92341459134e` | 255348 |
| dcs-cdsl-xref `dcs_cdsl_xref_v2__pending-upstream.tsv` (CC BY-SA 4.0, DOI 10.5281/zenodo.22105641) | `c897582b3504` | 98606 (56377 in_cdsl=1) |

Join key bridge: dcs-cdsl-xref slp1 keys (never re-derived); transliteration via
canonical `sanskrit_util` (to_slp1/from_slp1/norm/strip_slp1_accents), never forked.

## Result

| metric | value |
|---|---|
| L8 definition rows parsed | 255348 |
| L8 rows matched to ≥1 CDSL headword | 41649 (**16.3 %**) |
| L8 rows unmatched | 194907 |
| L8 rows hitting only DCS lemmas with no CDSL headword (in_cdsl=0, excluded) | 18792 |
| xwalk output pairs (row × headword) | 41697 |
| rows matching >1 CDSL headword | 47 |
| tier1 exact IAST→SLP1 | 40096 |
| tier2 hyphen/space-stripped exact | 30 |
| tier3 accentless SLP1 | 0 |
| tier4 ASCII-folded recall | 1523 |
| in_cdsl=1 pairs | 41697 |

## Verify: 50-definition hand sample

`h4733_sample50.tsv` — random.Random(42) sample, every row mechanically
revalidated (variant→SLP1 relation + xref membership + in_cdsl=1):
**50/50 PASS**.

## License note

Inputs mix CC BY 4.0 (L8) and CC BY-SA 4.0 (dcs-cdsl-xref). This derivative
linkset inherits the stricter share-alike term on the key side: ship as
**CC BY-SA 4.0** with wisdomlib + csl-apidev provenance, per LICENSE-DATA norms.

## Risks

- L8 headword titles are page titles, not lemmatized forms — matched headwords
  are witness-level (EN sense-alignment input), not sense-level alignment.
- tier4 folds vowel length/retroflexion — recall-only tier; filter `tier<=3`
  for strict use.
- EN witness for sense-alignment remains UNRUN downstream (this is the key bridge).
