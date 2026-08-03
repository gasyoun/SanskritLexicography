# ARCHITECTURE — Rig-Veda multi-translation evidence layer

_Created: 29-07-2026 · Last updated: 03-08-2026_

Component boundaries, data model and contracts for the layer specified in
[PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md).
Every field name and count below was verified against the committed feeds on 29-07-2026, not
assumed.

---

## 1. The measured substrate

These are facts about the existing data, established by direct inspection. They are what makes
the deterministic spine deterministic.

| Fact | Value | Source |
|---|---|---|
| Stanzas in the Ṛgveda per VedaWeb | 10,552 | `contents` length of the accented-text and lemmatization exports |
| Tokens in the Ṛgveda | **164,758** | sum over `contents[i].transformContext` |
| Per-token fields already present | `form`, `lemma`, `lemma_ewaia`, `id_gra[]`, `id_mw[]`, `id_pwg[]` | `transformContext` (a JSON **string**, parse it) |
| Stanza key | `location`, dotted form `1.1.1` | every export |
| Grassmann 1876–77 coverage | 10,552 / 10,552 | `grassmann_de_1876_1877.json` |
| Elizarenkova 1989–99 coverage | 10,552 / 10,552 | `elizarenkova_ru_1989_1999.json` |
| Geldner 1951–57 coverage | **10,548 / 10,552** | `geldner_de_1951_1957.json` |
| Stanzas Geldner does not translate | **RV 10.106.5, 10.106.6, 10.106.7, 10.106.8** | set difference of the two location sets |
| Empty-text rows in any translation | 0 | all three files |

**Two consequences the implementation must not miss.**

First: the dictionary anchor is *already given per token*. `id_gra` and `id_pwg` sit on every
one of the 164,758 tokens. The GRA and PWG crosswalks in VisualDCS remain useful as
entry-level aggregates, but the layer does not need them to attach a Ṛgvedic token to a
dictionary entry — that edge already exists. No fuzzy matching is required anywhere in spine A.

Second: **RV 10.106.5–8 is the natural regression anchor for the "omitted by one" class.** It
is a real, pre-existing gap in Geldner (the notoriously obscure Aśvin hymn), it is exactly four
stanzas, and any pipeline that reports a different count for Geldner's omissions is broken. It
also proves the class is worth modelling: MG's question "who translated how, and who did not
translate at all" has a non-empty answer before any model is run.

## 2. Component boundaries

Five components, each with one job.

```
  VisualDCS/non-derived/vedaweb/        rvlinks/RV_sa-hn-ru-de-en_1.html
  (read-only feed, R17)                 (read-only source)
            |                                     |
            |                                     v
            |                          [C1] griffith_extract
            |                                     |
            v                                     v
  [C2] spine_build  <---------------------------- +
            |
            +--> rv_stanza_translations.jsonl  (10,552 stanzas x 4, canonical)
            +--> rv_lemma_occurrences.jsonl    (lemma -> 164,758 tokens, canonical)
            +--> rv_translation_spine.tsv      (flat mirror, generated)
            |
            +------------------> [C3] divergence_type
            |                              |
            +------------------> [C4] wordlevel_align
                                           |
                       [C5] pipeline_bridge <- both, + wisdomlib
                                           |
                       judge witness · contradiction gate · TM tier
```

**C1 `griffith_extract`** — HTML in, JSON out. Reads the `p.stamp` / `p.en` pairs from the
committed 5-layer HTML, normalises `rv01.001.01` → `1.1.1`, emits `griffith_en_1896.json` with
the *same* record shape as the three VedaWeb translation files
(`{createdAt, archived, text, location}` inside a `contents` list, with a `meta` block naming
Griffith, 1896, `en`, and the extraction provenance). Deterministic; no model.

**C2 `spine_build`** — the deterministic join. Reads the lemmatization export and the four
translation files; groups the 164,758 tokens by lemma; for each lemma emits every stanza it
occurs in together with all four renderings of that stanza. Records absence explicitly rather
than dropping the row. Deterministic; no model. **This is spine A of ruling R5.**

**C3 `divergence_type`** — the only component that exercises model judgment on a large scale.
Consumes the spine, emits a typed label per (stanza × translator-pair). Gated: pilot →
human agreement → full run (R13, R15).

**C4 `wordlevel_align`** — layer B of R5. For a given token and a given translation of its
stanza, propose the span of the translation that renders it, with a confidence. Re-uses the
existing calibrated machinery rather than introducing a new aligner; output is **advisory** and
is never written into reviewed data.

**C5 `pipeline_bridge`** — the three integration points of R7 plus the four wisdomlib roles of
R11. This is the only component that touches existing pipeline code.

## 3. Data model

**Normalised on purpose — measured, not guessed.** The four translations average 152–171
characters per stanza. A single denormalised file carrying all four texts inline at every one
of the 164,758 token occurrences measures **~65 MB**; splitting the stanza texts out and
referencing them by `location` measures **~18 MB** for the same information. Ruling R12 asks for
JSONL plus a flat TSV mirror; it does not ask for a 65 MB blob in git. So the canonical form is
two files that join on `location`.

### 3.1 `pwg_ru/rv_stanza_translations.jsonl` — one record per stanza (10,552)

```
{
  "location": "1.1.1",
  "mandala": 1, "hymn": 1, "stanza": 1,
  "translations": {
    "grassmann_de_1876":    {"status": "present", "text": "Den Priester Agni preise ich, …"},
    "geldner_de_1951":      {"status": "present", "text": "Agni berufe ich als Bevollmächtigten, …"},
    "elizarenkova_ru_1989": {"status": "present", "text": "Агни призываю я – во главе поставленного…"},
    "griffith_en_1896":     {"status": "present", "text": "I Laud Agni, the chosen Priest, …"}
  },
  "divergence": null
}
```

`status` is one of `present` · `absent_from_source` (the translator's edition does not carry
this stanza at all — the Geldner 10.106.5–8 case) · `empty` (carried but blank). Distinguishing
`absent_from_source` from `empty` is the whole point of the field; collapsing them to a null
text destroys the "who did not translate" question this layer exists to answer.

### 3.2 `pwg_ru/rv_lemma_occurrences.jsonl` — one record per lemma

```
{
  "lemma": "agní-",
  "lemma_ewaia": "",
  "id_gra": ["79"],
  "id_pwg": ["349"],
  "id_mw": ["890"],
  "occurrence_count": 1234,
  "occurrences": [
    {"location": "1.1.1", "form": "agním", "token_index": 0, "wordlevel": null}
  ]
}
```

`divergence` (§3.1) and `wordlevel` (here) are `null` after wave 1a and filled by C3 and C4.
Keeping both keys in the schema from the start makes wave 1b an in-place enrichment rather than
a reshape.

### 3.3 `pwg_ru/rv_translation_spine.tsv` — flat mirror, generated

One row per `lemma × location × translator`. Columns: `lemma`, `id_gra`, `id_pwg`, `location`,
`form`, `translator`, `status`, `text`, `divergence_class`, `wordlevel_span`,
`wordlevel_confidence`. Denormalised on purpose — this is the artifact that gets grepped, read
into a spreadsheet, and fed to `/review-sheet`. It is generated **from** the two JSONL files,
never edited by hand and never a second source of truth. Because it is a derived view it may be
regenerated rather than committed if it proves unwieldy; the two JSONL files are the contract.

### 3.4 `pwg_ru/rv_renou_citation_index.jsonl`

**Naming, deliberately.** This repo already uses the token `renou` for something else entirely:
Louis Renou's *Histoire de la langue sanskrite* (1956) five language-states axis, indexed as
`{code}.renou.jsonl` and driven by [`src/renou_pipeline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_pipeline.py)
and [`RENOU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md).
That is a *register* axis and has nothing to do with Renou's French *translation* of the
Ṛgveda. Everything in this layer therefore carries the `rv_renou_*` prefix, and no file, script
or field here may be named `renou_*` alone.

```
{
  "location": "1.1.1",
  "mandala": 1, "hymn": 1, "stanza": 1,
  "mention_kind": "quoted_fr" | "paraphrase_ru",
  "context_ru": "…Рену: «aux ailes d'oiseau»…",
  "quote_fr": "aux ailes d'oiseau",
  "source": "elizarenkova_commentary"
}
```

`quote_fr` is populated only for the 368 mentions carrying a Latin-script quotation; the other
~1,845 are `paraphrase_ru` with `quote_fr: null`. Per PLAN §5, `context_ru` is a bounded
context window around the mention, not the surrounding commentary paragraph.

### 3.5 Divergence taxonomy — the five classes

Scoped to a **translator pair** at a **stanza**, because "divergence" between four translators
at once is not a well-formed claim.

| Class | Definition | Deterministic? |
|---|---|---|
| `agreement` | Both render the token with semantically equivalent material | no — model |
| `lexical_variant` | Same referent, different word choice (*Priester* vs *Bevollmächtigter*) | no — model |
| `semantic_shift` | The two readings are not interchangeable; a real interpretive difference | no — model |
| `omitted_by_one` | The **first**-named translator of the pair does not render material the second renders | partly — `absent_from_source` is deterministic, in-stanza omission is not |
| `added_by_one` | The **first**-named translator of the pair supplies material with no counterpart in the second | no — model |

The `absent_from_source` sub-case of `omitted_by_one` is computed by C2 without any model and
must match the measured baseline (4 stanzas for Geldner, 0 for the other three).

**Amendment, H2192 (03-08-2026) — the last two classes are DIRECTIONAL.** As originally worded
they were converse readings of one undirected event ("one translator omits" and "one translator
supplies" describe the same configuration from opposite ends), the pair key is unordered, and
the model reply carried no direction field. The consequence was measured, not theorised:
`added_by_one` fired **0 of 12,000** times in the H1844 pilot and 0/300, 0/300, 0/267 across
H1901's three independently-trained arms, while **8,744** pilot pairs carry supplied material on
exactly one side. Both classes now carry a mandatory `surplus_side` naming which of that pair's
two translators holds the surplus, read from the **first** translator in the pair key; and
`COARSE_MAP` sends both to `omission`, so the K3 projection cannot move under a semantically
vacuous relabelling. This amends the wording of two rows — no class was added, removed or
merged, and the five-class taxonomy stands. Full measurement:
[`pwg_ru/h2192/RV_ADDED_BY_ONE_INSTRUMENT_DEFECT_2026-08.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2192/RV_ADDED_BY_ONE_INSTRUMENT_DEFECT_2026-08.md).

### 3.6 TM tier extension

Not a new subsystem. [`schemas/translation_memory.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/translation_memory.schema.json)
already defines `trust_level` (`reviewed_exact` · `machine_exact` · `legacy_promoted` ·
`suggestion`), `reuse_policy`, and `lang: [ru, en]`; and
[`src/tm_source_weights.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_source_weights.json)
already carries `rigveda: 0.72` and `atharvaveda: 0.72` under `by_work_contains`.

The extension is therefore: one new `trust_level` value (`corpus_translation_witness`), a
`reuse_policy` of `suggest_only` for it, and per-translator weight rows. Because `lang` is
already an enum over `[ru, en]` and the weights file is keyed by work rather than by language,
**R7's "not for Russian only" requirement is satisfied by configuration, and a third language
is a new enum member plus a weights row — not a rewrite.** Any change here must be classified
in [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
as SHARED / INTENTIONAL-DIVERGENCE / GAP before the work is called done; `lang_parity_check.py`
enforces it in the test suite.

## 4. Build-vs-reuse verdict per component

| Component | Verdict | Evidence |
|---|---|---|
| C1 `griffith_extract` | **Build** — small, ~100 lines | Nothing extracts the `p.en` layer today; it exists only inside the HTML |
| C2 `spine_build` | **Build on top of existing feeds** | The join keys (`location`, `id_gra`, `id_pwg`) all pre-exist; no matching logic is invented |
| C3 `divergence_type` | **Build** — genuinely new | No divergence typing exists anywhere in the org; `pwg_vedaweb_gloss_crosswalk.tsv` puts Geldner and Grassmann in one row but never compares them |
| C4 `wordlevel_align` | **REUSE — do not write a new aligner** | [`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py) ships a per-pair LaBSE confidence calibrated at `agreement >= 0.20` ([ALIGN_GATE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ALIGN_GATE.md)); [`src/tm_saru_align_labse.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_saru_align_labse.py) ships a Vecalign monotone DP at precision 0.966 ([LABSE_ALIGN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/LABSE_ALIGN.md)) |
| C5 `pipeline_bridge` | **Extend, do not fork** | TM schema, source weights and the parity ledger already have the shape; adding a tier is configuration plus a wiring commit |
| wisdomlib access | **REUSE** | Crawler, index and `word_traditions.jsonl` exist in SamudraManthanam; wave 1 reads them and performs no crawl (R17) |

## 5. Interfaces and contracts

- **Feed access is sibling-path and read-only.** The layer reads
  [`VisualDCS/non-derived/vedaweb/`](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb)
  through a resolved sibling path with a graceful "feed absent" failure — the same pattern
  WhitneyRoots uses for `dcs_ppp_verified.tsv`. It never writes there and never calls the
  VedaWeb API (the bulk export's `pickupKey` is single-use).
- **The spine is generated, never hand-edited.** Both artifacts are outputs of C2. A human
  correction goes into the generator or into a committed override file, never into the JSONL.
- **Layer B is advisory by construction.** `wordlevel.*` fields carry a `confidence` and a
  `low_confidence` flag; nothing downstream may promote a `low_confidence` span into reviewed
  data. This is the same posture the Elizarenkova lookup already has in this repo.
- **The contradiction gate queues, it never rejects.** Its output is a review queue entry, not
  a verdict on the card.

## 6. Where this sits relative to what exists

The layer is a **sibling of** `pwg_vedaweb_gloss_crosswalk.tsv`, not a replacement. That
crosswalk answers "which PWG entries are RV-attested, and what did the two Germans say about an
example locus" at entry granularity. This layer answers "for this lemma, at every one of its
occurrences, what did all four translators do, and where did they part company" at
lemma × stanza granularity. The crosswalk stays where it is and keeps its consumers.

_Dr. Mārcis Gasūns_
