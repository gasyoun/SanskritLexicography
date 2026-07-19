_Created: 19-07-2026 · Last updated: 19-07-2026_

# ARCHITECTURE — PWG data layers

Cover: [PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md).

## 1. Anatomy of a PWG card — the model this wave formalises

A PWG record is the span `<L>…<LEND>` in [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt) — 123,366 records. Its markup vocabulary (measured, [`csl-atlas/data/parse-rules/pwg.json`](https://github.com/gasyoun/csl-atlas/blob/main/data/parse-rules/pwg.json)):

| Tag | Role | Count | Parse adequacy |
|-----|------|-------|----------------|
| `<L>` / `<LEND>` | record boundary | 123,366 | clean |
| `<k1>` / `<k2>` | headword keys (Devanāgarī / SLP1) | per record | clean |
| `<h>` | homograph number | 6,499 | clean |
| `<hom>` | homonym marker | 82 | clean |
| `<lex>` | grammar / part-of-speech | 131,189 | clean |
| `<div>` | sense division | 113,613 | clean |
| `<ls>` | literature citation | 772,567 | **lossy** (72.4% recognised) |
| `<ab>` | abbreviation (diasystem) | 185,563 | partial |
| `<is>` | inflected/stem surface | 53,947 | surfaced, not dropped |
| `{#…#}` | SLP1 → IAST Sanskrit | inline | clean |
| `{%…%}` | German-vs-Latin gloss | inline | clean |
| `〉` | **sense-closing glyph** | 87,680 | **historically unparsed** |
| `[Page…]` / `<pc>` | volume/column locus | per record | clean |

Three descriptions of this anatomy exist and are **reused, not rebuilt**:

- **Pedagogical** — [`EntryAnatomy/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/README.md), 24 named elements, human-facing.
- **Machine-measured** — the parse-rules `pwg.json` above, every tag with counts + MDF adequacy.
- **Working parser** — [`RussianTranslation/src/microstructure.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure.py), flat record → Apresjan "lexicographic portrait" (homonym-keyed card, grammar, diasystem, numbered/lettered sense tree), validated by [`schemas/pwg_ru_lexicographic_portrait.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_ru_lexicographic_portrait.schema.json).

W1.1 (`PWG_CARD_ANATOMY.md`) is the **index + measured crosswalk** over these three — a coverage matrix showing, per anatomy element, which of the three describes it and where they diverge. The three stay as-is.

## 2. Build-vs-reuse verdict per piece (prior-art check — `/prior-art` evidence)

| Piece | Verdict | Consume, don't rebuild |
|-------|---------|------------------------|
| Card anatomy description | **reuse ×3** | The three above. New doc only crosswalks them. |
| Record splitter / masker | **reuse** | [`pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py) (`<L>…<LEND>` split, `{Tn}` masking, 123,365/123,366 lossless round-trip). |
| Portrait parser | **reuse** | `microstructure.py`. The JSON Schema extension (W1.3) formalises *its* output. |
| `<ab>` resolver | **reuse** | [`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py) (791 abbreviations from `pwgab_input.txt`). |
| `<ls>` resolver | **extend** | [`pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py) (`pwgbib.txt`, ~2.7k) + [`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py) (1266 ln). W1.6 mines the unrecognised tail against these; no new resolver. |
| `<pc>` page/column | **reuse** | [`pwg_page_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_page_index.py). (Note the open `page=(column+1)//2` per-volume-offset `@DO`.) |
| Sense records | **extend** | [`csl-atlas/data/lexico/senses_pwg.jsonl`](https://github.com/gasyoun/csl-atlas/blob/main/data/lexico/senses_pwg.jsonl) (`senseId`, `parserFamily`, `splitConfidence`, `sanskritAnchors`). |
| Xref edges | **extend** | `csl-atlas/data/lexico/xref_edges.csv` + [`scripts/lexico/m3_xrefs.py`](https://github.com/gasyoun/csl-atlas/blob/main/scripts/lexico/m3_xrefs.py). |
| Government / Rektion | **extend** | The H1308 government index (~3,853 markings / ~3,222 senses, [FINDINGS §71](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)). |
| OntoLex sidecar | **extend** | [`export_lod.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_lod.py) `de-lexicon`, emitting `pwg_de_lexicon.ttl` (H772, [PWG_PLUS_GERMAN_ENRICHMENT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_PLUS_GERMAN_ENRICHMENT.md)). |
| Formal grammar (RNG) | **NEW** — the one genuine gap | No DTD/XSD/RNG exists anywhere in csl-orig (audit-confirmed). Only the TEI header references `tei_all.rnc`. This is net-new and non-duplicative. |
| Defect-report packaging | **reuse pattern** | The [`NWS_ERRATUM_EMAIL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NWS_ERRATUM_EMAIL.md) precedent + [/cologne-correction-queue](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-correction-queue.md) change-file format. |

**Nothing scheduled rebuilds an existing asset.** The single NEW component is the RelaxNG grammar.

## 3. Component boundaries

```
csl-orig/v02/pwg/pwg.txt   (READ-ONLY source, 123,366 records)
        │
        ├─▶ pwg_mask.py ──▶ microstructure.py ──▶ portrait (JSON)
        │                        │
        │                        ├─▶ [W1.3] pwg_portrait.schema.json  ──▶ pwg_portrait_validation.json
        │                        └─▶ [W1.4] corrected 〉-splitter      ──▶ sense_glyph_audit.json
        │                                                                 + pwg_ru_glyph_quarantine.jsonl (side file)
        ├─▶ [W1.2] pwg_markup.rnc (NEW) ──▶ pwg_markup_validation.json (typed failure buckets)
        │                                          │
        │                                          └─▶ [W1.9] csl-corrections change files (STAGED, no PR)
        │
        ├─▶ [W1.6] ls_source_map + pwgbib ──▶ citations layer (≥85% recognised)
        ├─▶ [W1.7] senses / xref / government layers
        │
        └─▶ [W1.8] export_lod.py de-lexicon ──▶ pwg_de_lexicon.ttl
                   (entry/<key1>/de nodes on shared lemma/<key1> spine — additive, German never mutated)
```

The `lemma/<key1>` spine (SLP1 `form_key`) is the join key for every layer — **not** the Russian, **not** the presence of a PWG record. A headword with no PWG record still gets its other-layer nodes; the German node is emitted only when a PWG record exists.

## 4. Data model — new/changed artifacts

| Artifact | Path | Shape |
|----------|------|-------|
| Anatomy reference | `docs/PWG_CARD_ANATOMY.md` | Markdown: element × source coverage matrix + divergence notes |
| RNG grammar | `RussianTranslation/schemas/pwg_markup.rnc` | RelaxNG compact syntax over the `<L>…<LEND>` tag language |
| Markup validation | `RussianTranslation/reports/pwg_markup_validation.json` | `{record_id, status: pass|fail, failure_type, span}` per record |
| Portrait validation | `RussianTranslation/reports/pwg_portrait_validation.json` | same shape, over the parsed portrait |
| `〉` audit | `RussianTranslation/reports/pwg_sense_glyph_audit.json` | per-record merged-sense count + store-contamination totals |
| Quarantine marker | `RussianTranslation/reports/pwg_ru_glyph_quarantine.jsonl` | `{key1, senseId, reason}` — **side file, store untouched** |
| Citations layer | extend `csl-atlas/data/lexico/senses_pwg.jsonl` / a `pwg_citations.jsonl` | `{key1, ls_raw, resolved_source, confidence}` |
| Xref edges | extend `csl-atlas/data/lexico/xref_edges.csv` | `{src_key1, redirect_type: s|vgl, tgt_key1, resolved: bool}` |
| Government layer | extend the H1308 index | `{key1, senseId, case, kind: single|variation}` |
| OntoLex graph | `RussianTranslation/release/fixture/pwg_de_lexicon.ttl` | additive properties on `entry/<key1>/de` |
| Staged defects | `csl-corrections/…/batch_pending/` change files | change-file format per correction-workflow.md |

## 5. Key risks (full register in the verification doc)

- **R1 — the `〉` re-segmentation over-corrects.** Mitigation: the ≤50-card LLM sanity check (W1.5) + a deterministic diff against the first-2500 fix already verified in [FINDINGS §447](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
- **R2 — RNG can't express a genuinely-irregular but valid record**, inflating false failures. Mitigation: the 100%-parse-or-typed-bucket bar treats "unexpected but attested" as its own bucket, not a defect; a human reviews buckets before any change file ships.
- **R3 — citation resolver plateaus below 85%.** Mitigation: D8 accepts ~85–90% as the honest ceiling; the tail is catalogued as a typed gap, not forced.
- **R4 — shared-tree contention** on `csl-atlas` (external actor commits mid-session). Mitigation: csl-atlas edits go through a worktree off `origin/main`; PRs, never direct pushes to a live tree.

_Dr. Mārcis Gasūns_
