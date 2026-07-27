# DE edition-graph export profile — OntoLex-Lemon + TEI Lex-0

_Created: 26-07-2026 · Last updated: 26-07-2026_

Field-by-field mapping, provenance and limitations for
[`src/export_de_edition.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py)
(H1629) — the **German** side of the PWG edition graph, serialized for FAIR
reuse as OntoLex-Lemon (Turtle) and TEI Lex-0 (XML).

> Executor: Opus 5 (`claude-opus-5[1m]`), 26-07-2026, handoff
> [H1629](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1629-Opus_SanskritLexicography_pwg-de-graph-ontolex-tei-export_25.07.26.md).

---

## 1. What this profile is, and what it is not

The generator exports **one entry per (key1, homonym)** whose senses come from
several *editions* of the Petersburg family — PWG, PW, SCH, PWKVN, NWS — each
sense carrying the five structured German layers built by
[H1624](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md)
G1–G6. That multi-edition grouping is what makes the artifact an *edition
graph* rather than five parallel dictionaries.

It is **not** a replacement for the two existing emitters, both of which stay:

| Emitter | Scope | Relationship to this profile |
|---|---|---|
| [`export_interop.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_interop.py) `tei` | Flat RU-side TEI (`entry`/`form`/`sense`) over assembled cards | Different side (RU), much thinner markup — untouched |
| [`export_lod.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_lod.py) `de-lexicon` (H772) | German senses re-parsed from `assembled_cards.jsonl`; gloss + citation + Renou stratum only | Same German material, but **no** government / form notes / edition relations / gloss-language spans, and no edition grouping — this profile is its structured successor, not its replacement |

Both this profile and `export_lod.py` mint the **same** `lemma/<key1>` IRI, so
the DE edition graph federates with the RU lexical graph, the DCS-frequency
graph and the grammar graph on the shared lemma spine.

### Ownership boundary

Per [PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md),
`csl-standards` owns TEI/OntoLex-Lemon export *modelling* for the Petersburg
family. The **generator and its input data stay in `RussianTranslation`**; a
published graph plus SPARQL surface is `csl-standards`' side of the 2026-06-03
boundary. This profile is the generator half only — nothing here is published.

---

## 2. Rights fence (N9)

This export is DE-only, enforced at three points:

1. **Input allowlist** — `DE_FIELDS` is the only set of input fields the
   profile ever reads; every other store field (`ru`, `en`, `review_status`,
   `reviewer`, `provenance`, `evidence`, `evidence_summary`, `corpus_gate`,
   `differentia`) is dropped by `de_only()` before any emitter sees a row.
2. **Purity quarantine** — a row whose German-bearing fields carry Cyrillic is
   **quarantined**, not emitted (see §5).
3. **Post-serialization guard** — `assert_rights_safe()` re-scans the emitted
   bytes for a forbidden field *name* (JSON key, Turtle predicate or XML
   element) and for any Cyrillic character, and aborts the run on a hit. It
   deliberately does not match forbidden names appearing as *values*:
   `pwglex:glossLang "en"` and `pwglex:evidenceGrade` are legitimate.

The store's `h` field is **not** on the allowlist: the homonym is derived from
`subcard` via `edition_rel.homonym_of`, and `h` is free text that in practice
carries Russian disambiguation prose (`PW 3 (с sam, о супружеском намерении)`),
so reading it would import a contaminated field for no gain.

Licence posture per edition is emitted with the graph: PWG / PW / SCH / PWKVN
are marked `pd` (Public Domain Mark 1.0 — 19th–early-20th-c. German editions);
NWS is marked `project` (the Cologne Nachtragswörterbuch working layer).

---

## 3. Field mapping

Every layer is **recomputed from the German string** by the module that owns it
(reuse, not reimplementation). A precomputed field on the input row is used
only when present *and* structurally valid, so the export does not depend on a
particular store-annotation vintage.

### 3.1 Entry and lemma

| Source | Producer | OntoLex-Lemon | TEI Lex-0 |
|---|---|---|---|
| `key1` (SLP1) | store / fixture | `lemma/<key1>` `a ontolex:Form, lila:Lemma` · `ontolex:writtenRep`@`sa-Latn-x-slp1` · `pwglex:slp1` | `form[@type="lemma"]/orth[@xml:lang="sa-Latn-x-slp1"]` |
| `iast` | store / fixture | `ontolex:writtenRep`@`sa-Latn` · `rdfs:label` | `form[@type="lemma"]/orth[@xml:lang="sa-Latn"]` |
| homonym (from `subcard`) | [`edition_rel.homonym_of`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/edition_rel.py) | `entry/<key1>/<hom>/de` `a ontolex:LexicalEntry` · `pwglex:homonym` | `entry/@xml:id` = `entry-<key1>-<hom>` |
| `layer` | store / fixture | `pwglex:edition` → `edition/<layer>` `a pwglex:Edition` | `sense/@source` → `#edition-<layer>`, defined in `teiHeader//listBibl` |

### 3.2 Sense text

| Source | Producer | OntoLex-Lemon | TEI Lex-0 |
|---|---|---|---|
| `{%…%}` braced German equivalents | `microstructure.PCT` + `clean_de` | `pwglex:germanEquivalent`@`de` | `gloss[@xml:lang="de"]` |
| joined equivalents (fallback: cleaned body) | same | `skos:definition`@`de` | `def[@xml:lang="de"]` |
| `{#…#}` Sanskrit forms (first 4) | `microstructure.SA` | `pwglex:exampleForm`@`sa-Latn-x-slp1` | `cit[@type="example"]/quote` |
| `sense_tag` → ASCII skeleton | `sense_tag_slug` | `pwglex:senseTag` · sense IRI segment | `sense/@n`, `sense/@xml:id` |
| `page` / `volume` | store | `pwglex:page` · `pwglex:volume` | — (kept in the Turtle only) |

### 3.3 The five H1624 layers

| Layer | Producer | OntoLex-Lemon | TEI Lex-0 |
|---|---|---|---|
| **G1** `gloss_lang` spans (non-DE only) | [`pwg_mask.gloss_lang_spans`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py) | `pwglex:glossSpan` → `pwglex:GlossSpan` (`pwglex:glossLang`, `pwglex:ruleId`) | `gloss[@type="sourceGloss"][@xml:lang][@subtype=rule_id]` |
| **G2** `government` | [`government_census.extract_government`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_census.py) | `pwglex:government` → `pwglex:Government` (`pwglex:case`, **`lexinfo:case`**, `pwglex:variation`, `pwglex:connector`, `pwglex:governmentKind`, `pwglex:span`) | `gramGrp/gram[@type="government"][@subtype=kind][@norm=case]`; a variation adds `note[@type="governmentVariation"]` |
| **form** `form_notes` (nom/voc) | [`form_labels.extract_form_notes`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/form_labels.py) | `pwglex:formNote` → `pwglex:FormNote` (`pwglex:case`, `lexinfo:case`, `pwglex:formNoteKind`, `pwglex:span`) | `gramGrp/gram[@type="case"][@norm=nom\|voc]` |
| **G3** `citation_edges` | [`citation_edges.extract_citation_edges`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_edges.py) | `dct:references` → `citation/<slug>` `a pwglex:Citation, prov:Entity` (`pwglex:sourceSigla`, `pwglex:locus`, `pwglex:workId`, `pwglex:workName`, `pwglex:renouStratum`, `pwglex:bibOk`, `pwglex:resolverStatus`) | `cit[@type="citation"]/bibl[@corresp][@ana=resolver_status]` with `abbr[@type="siglum"]` + `biblScope[@unit="locus"]`; every `@corresp` resolves into `back//listBibl[@xml:id="cited-works"]` |
| **G4** `edition_rel` | [`edition_rel.classify_edition_rel`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/edition_rel.py) | `vartrans:SenseRelation` (`vartrans:source`/`target`/`category`, `pwglex:relOp`, `pwglex:relDirection`, `pwglex:editionLayer`, `pwglex:confidence`, `rdfs:comment`) | `xr[@type="editionRel"][@subtype]` with `ref[@target]` + `note[@type="relEvidence"]` |

`subtype == "base"` (the PWG skeleton layer) emits no relation on either side —
a sense relating to nothing is not a relation.

### 3.4 Conventions worth knowing

- **Raw span vs display span.** The Turtle `pwglex:span` keeps the source span
  verbatim, markup and all, as provenance. TEI element *content* carries the
  markup-stripped form (`plain()`), with the machine value in `@norm` — so
  `(<ab>Acc.</ab>)` reads as `(Acc.)` in the XML and `acc` in `@norm`.
- **Sense ids are assigned once.** `numbered_senses()` is the single source of
  truth for sense-id assignment, so the two serializations can never drift on
  identifiers they cross-reference.
- **`relEvidence`, not `evidence`.** The bare name is a store field carrying
  RU-side judge evidence and is on the forbidden list; the TEI note type is
  renamed so the rights guard stays strict.
- **Bibliography ids are short and sequential** (`bibl-001`…) over the sorted
  citation-slug set, not the hex-escaped IRI slug — readable, and stable for a
  given row set.
- **Determinism.** With a fixed `--generated-at`, two runs are byte-identical
  (asserted by the selftest), so the golden fixture is diffable.

### 3.5 TEI Lex-0 project extensions

These `@type` values are project extensions, not Lex-0 vocabulary:
`government`, `case` (on `gram`), `editionRel` (on `xr`), `sourceGloss` (on
`gloss`), `relEvidence` / `governmentVariation` (on `note`), `siglum` (on
`abbr`), `renouStratum` (on `note` in the bibliography). They are declared in
the exported `teiHeader/encodingDesc/projectDesc`, which points back at this
document.

---

## 4. Running it

```
python src/export_de_edition.py --selftest
python src/export_de_edition.py export --generated-at 2026-07-26 \
    --out-dir release/fixture/de_edition
python src/export_de_edition.py export --store src/pwg_ru_translated.jsonl --limit 500
python src/export_de_edition.py export --strict     # fail instead of quarantining
```

Outputs, per run: `pwg_de_edition.ttl`, `pwg_de_edition.tei.xml`,
`pwg_de_edition.manifest.json` (counts, quarantine list, rights block).

The committed golden set is
[`release/fixture/de_edition/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/fixture/de_edition),
generated from
[`src/fixtures/pwg_de_edition.fixture.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/fixtures/pwg_de_edition.fixture.jsonl)
— 22 DE-only rows curated to exercise **every** layer and **every** edition
layer, plus three deliberate contamination guard rows. The selftest fails if
any layer's count drops to zero, so an extractor regression cannot ship
silently.

Golden fixture counts (26-07-2026):

| | entries | senses | government | form_notes | citation_edges | gloss_spans | edition_rel |
|---|---|---|---|---|---|---|---|
| fixture | 7 | 20 | 15 | 2 | 42 | 3 | 17 |

Edition-layer coverage: `pwg` 3 · `pw` 6 · `sch` 3 · `pwkvn` 5 · `nws` 3.

---

## 5. Limitations — read before citing the output

1. **No TEI Lex-0 ODD validation is performed.** The selftest checks XML
   well-formedness, the required Lex-0 element skeleton
   (`entry`/`form[@type="lemma"]`/`orth`/`sense`/`def`/`gramGrp`/`cit`/`bibl`/`xr`),
   `xml:id` uniqueness and that no `@corresp`/`@source`/`@target` dangles. It
   does **not** validate against the Lex-0 RNG/ODD — that needs the schema and
   was not run here. Treat conformance as *structurally checked*, not *certified*.
2. **The store's German is not byte-identical to csl-orig.** Eleven store rows
   carry Russian tokens inside the `de` field (`и` for `und`, `для` for `für`,
   `в` for `in`, `С` for `Mit`); `huti` also lost its `(von 1. {#hu#})` etymology
   parenthesis. Those rows are quarantined here rather than exported, but the
   underlying corruption is upstream and unfixed — see
   [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   and the tracking integrity issue.
3. **~1% of `sense_tag` values are Russian prose** (110/11,603 store rows).
   `sense_tag_slug()` reduces every tag to its ASCII structural skeleton, so no
   Russian reaches the output, but a tag like `c) с dat. лица и instr. предмета`
   degrades to `c-dat.-instr` — informative, lossy, and honest about it. The
   manifest lists every sanitized row.
4. **The G1 `gloss_lang` layer is the least reliable of the five.** A census
   over all 15,901 `{%…%}` spans in the store's German text (26-07-2026) found
   229 classified non-DE, of which ~122 (53%) carry clear German evidence —
   concentrated in the `english_content` rule (117/153 ≈ 77% false-positive
   rate). Because `classify_pct_detail` marks `la`/`en` spans `translate: False`,
   those German glosses are also masked out of the translation path upstream.
   Consumers should treat a non-DE `gloss_lang` as a *hint*, not a fact. Filed
   as an integrity issue; **not** fixed here (changing the classifier changes
   masking behaviour pipeline-wide and needs its own measured A/B).
5. **`edition_rel` is rule-confidence only** (`confidence: "rule"`), inherited
   from H1624 G4 — the H180 typology *display names* are still unvoted, so the
   machine classes are exported under their rollup names.
6. **The base IRI is ruled but does not resolve yet.** The namespace
   `https://w3id.org/sanskrit-lexicon/repwg/` is settled
   ([issue #809](https://github.com/gasyoun/SanskritLexicography/issues/809),
   rationale in [LOD_GRAPH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LOD_GRAPH.md)
   § Namespace ruling) — `repwg` = "rePWG", a *re-edition* of PWG, deliberately
   not `pwg`. But the w3id PURL is **not registered**, so every IRI here is a
   permanent identifier that currently 404s. Do not describe the graph as having
   dereferenceable IRIs until that PR lands. Override with `--base-iri`.
7. **Scale is untested beyond the fixture.** The profile has been exercised on
   the 22-row golden fixture and on store slices, not on a full-store run.

---

## 6. Related

- [H1624](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md) — the G1–G6 layers this profile serializes
- [EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md) — the editorial fence the layers obey
- [LOD_GRAPH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LOD_GRAPH.md) — modelling notes for the sibling RU/grammar/DCS graphs
- [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) — ledger entry `de_edition_export_profile_h1629` (SHARED)
- [csl-observatory `ONTOLEX_TEI_ROUTING_CONTRACT.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ONTOLEX_TEI_ROUTING_CONTRACT.md) — the observatory-side routing contract (H1495)

_Dr. Mārcis Gasūns_
