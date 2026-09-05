# ROADMAP — Rig-Veda multi-translation evidence layer, 2026 H2 → 2027

_Created: 29-07-2026 · Last updated: 29-07-2026_

Wave plan for the layer specified in
[PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md).
Ruling R1 fixes the sequence: the working layer ships first, the citable artifact second, and
the Atharvaveda only after the Ṛgveda is entirely done (R3).

---

## Wave 1a — the deterministic spine (handoff [H1843](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1843-Sonnet_RussianTranslation_rv-multitranslation-spine-w1a_29.07.26.md), Sonnet tier)

No model judgment anywhere in this wave — every output is a parse or a key-exact join, so it
is reproducible byte-for-byte and can be re-run at zero risk.

| # | Deliverable | Unblocked by |
|---|---|---|
| W1.1 | **Griffith English layer.** Extract the `p.en` blocks from `rvlinks/RV_sa-hn-ru-de-en_1.html` keyed by the `p.stamp` locus (`rv01.001.01`), normalise to the VedaWeb `location` form (`1.1.1`), emit `griffith_en_1896.json` with the same shape as the three existing translation JSONs | nothing — the HTML is committed |
| W1.2 | **The spine.** `rv_stanza_translations.jsonl` (10,552 stanzas x 4 renderings) + `rv_lemma_occurrences.jsonl` (lemma -> its 164,758 token occurrences), joining on `location`. Normalised: the denormalised form measures ~65 MB, this one ~18 MB | W1.1 |
| W1.3 | **Flat mirror + schema.** `rv_translation_spine.tsv` (one row per lemma × stanza × translator) and `schemas/rv_translation_spine.schema.json` | W1.2 |
| W1.4 | **Renou locus index.** Parse Elizarenkova's commentary for the 2,213 Renou mentions; emit `rv_renou_citation_index.jsonl` with locus, the Russian context sentence, and — for the 368 that have one — the quoted French fragment | nothing |
| W1.5 | **Dictionary anchors.** Attach `id_gra` and `id_pwg` to every spine record by re-using the two existing crosswalks; no new matching logic | W1.2 |

**Wave 1a is done when** every one of the 10,552 stanzas resolves in all four translation
layers or is explicitly recorded as untranslated by that translator, and the Renou counts
reproduce (2,213 / 368).

## Wave 1b — typing, alignment, wiring (handoff [H1844](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1844-Opus_RussianTranslation_rv-multitranslation-typing-w1b_29.07.26.md), Opus tier)

| # | Deliverable | Unblocked by |
|---|---|---|
| W1.6 | **Divergence taxonomy — pilot.** Type ~2,000 stanzas across the five classes (agreement · lexical variant · semantic shift · omitted by one · added by one) | wave 1a complete |
| W1.7 | **Human gate.** 100 stanzas sampled out of the pilot into a `/review-sheet` HTML voting sheet; ≥ 80 % agreement releases the full run (R15) | W1.6 |
| W1.8 | **Full typing run.** All 10,552 stanzas, every translator pair | W1.7 passing |
| W1.9 | **Word-level layer B.** Token → span alignment per language, re-using `tm_align.py`'s calibrated confidence and the Vecalign path; 300-token gold sample scored per language (R14) | wave 1a complete — runs in parallel with W1.6 |
| W1.10 | **Judge witness.** The spine surfaces to the judge as external evidence for any RV-attested headword | W1.8 |
| W1.11 | **Contradiction gate.** A card whose Russian (or English) rendering contradicts all four translators is queued for human review rather than promoted | W1.8 |
| W1.12 | **TM tier.** A new `trust_level` value plus source-weight rows, wired for **`ru` and `en` alike** and structured so a third language is a config row, not a rewrite (R7) | W1.8 |
| W1.13 | **wisdomlib, four roles.** EN gloss tier for PWG→EN · tradition-based sense disambiguation · fifth witness in the contradiction gate · AV citation-locus source staged for wave 3 (R11) | nothing — data already downloaded |

**Wave 1b is done when** the existing test suite is green, `lang_parity_check.py` passes with
the new mechanism classified, and both the RU and EN paths see the new tier.

## Wave 2 — the citable artifact (2026 Q4, not before wave 1 is accepted)

- Package the spine + taxonomy as a FAIR dataset via `/data-release`: provenance README, per-source
  licence table, versioned release, Zenodo concept + version DOI, `CITATION.cff` round-trip.
- **Budget the subsetting step.** Because R10 put everything in one open repo with no
  rights-based split, the release must carve out a CC BY/PD-clean subset at this point rather
  than simply tagging what is there. This is the scheduling consequence recorded in
  [PLAN §5](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md).
- Register in [`kosha/data/manifest/datasets.json`](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json),
  [`Uprava/PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md) and
  [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) via `/artifact-propagate`.
- **The paper.** A 150-year diachronic study of Ṛgvedic translation practice: Grassmann 1876
  → Geldner 1951 → Elizarenkova 1989, measured, not asserted. Gets an `Axx` ID in
  [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md).

## Wave 3 — Atharvaveda (2027, opens only when the Ṛgveda is finished)

R3 is explicit: no AV work while RV work is open. When it opens:

- Text base is [`avlinks`](https://github.com/sanskrit-lexicon/avlinks) — 731 hymns, 5,933 verses, already published.
- The gap is the translation layer. VedaWeb's AV coverage must be checked before anything is
  built; Whitney's English translation is public domain and is the obvious first layer;
  wisdomlib's AV pages are the staged citation-locus source from W1.13.
- GRA's cross-references into the AV are the natural entry point on the dictionary side.

## Wave 4 — Renou EVP (2027 at the earliest)

R9 defers the full *Études védiques et pāṇinéennes* to 2027. Two prerequisites, both outside
this plan: a rights track (Renou d. 1966; in copyright in France until 2037) and OCR of 17
volumes. The wave-1 locus index is what makes this wave cheap when it opens — the loci are
already known, only the text is missing.

## Explicit non-goals across the whole roadmap

- No commits to `csl-orig`, `GRA`, `PWG` or any dictionary source repo.
- No re-pull of the VedaWeb bulk export (single-use `pickupKey`).
- No bulk use of Jamison–Brereton at any wave — sample-scale reference only (R4).
- No new repository: the layer lives in `RussianTranslation` (R2).

_Dr. Mārcis Gasūns_
