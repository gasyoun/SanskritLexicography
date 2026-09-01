# Statistics for the Sanskrit Lexicon — a 12-month org-wide census & analytics roadmap 2026–2027

_Created: 12-07-2026 · Last updated: 01-09-2026_

> **Truth-pass 27-08-2026** (Grok 4.6 `grok-4.6`). Closed references checked against the combined registry. Kept in place ([FINDINGS §475](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) clause 3). Not archived.

> **Q1→Q2 quarter boundary, 01-09-2026** ([H3793](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3793-Opus_SanskritLexicography_statistics-org-census-q2-analytical-layer_31.08.26.md), Opus 5 `claude-opus-5[1m]`). Q1 delivery is stated per register, and the Q2 analytical layer is designed against Part I's named gaps, in
> [Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md).
> Three things in *this* file were found stale by that pass and are corrected below: the WS2.4 figures (Part II quoted the superseded 15-dict wave), the Q1-target verdicts, and the backup risk (now closed). Two it could **not** fix from here: the machine feed
> [`stats_census_register.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/stats_census_register.csv),
> which drives the six live dashboard pages, is stamped 12–18-07-2026 and understates three rows; and the register is counted three ways (this file's prose ~48, the Part IV KPI 48, the feed **59**), so no KPI percentage is computable until one denominator is adopted.

**What this is.** The *measurement* counterpart to the two existing hubs. Where
[`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md)
answers "what assets exist?" and
[`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md)
answers "what large data sits uncounted on disk?", this file answers **"what statistics
can we compute over all of it, in what order, delivered how, over the next year?"** It is
deliberately *not* the publications roadmap — that is
[`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md),
which owns the evidence-graded-lexicography programme and the Axx paper pipeline. This
roadmap *feeds* those papers with numbers; it does not compete with them.

**Scope & decisions baked in** (from the 12-07-2026 intake interview): **whole org (~85
repos)**; serves **all four purposes at once** — publications, a public statistics
observatory, internal QA/data-health, and product/funnel analytics; **all three ambition
tiers** — descriptive census, comparative/analytical, and publishable-novel; delivered as
**live dashboards + FAIR data releases + an internal methods report/monograph chapter**
(refereed papers are the downstream, routed through ARTICLES, not a primary artifact of
this roadmap).

**The one-line thesis.** *We have already counted ~60 % of the descriptive surface (the
H683–H695 July push). The year is: finish the census and back it up, lift it to a
comparative/analytical layer that feeds A40/A50/A08, mine the genuinely novel findings, and
land the whole thing as a citable observatory + FAIR release set + a methods chapter.*

---

## Part 0 — The counting register (everything, counted)

Seven data layers. Each headline statistic carries its live count and a status:
**✅ computed · ◐ partial · ○ not started**. This table is the living scoreboard — the
year's job is to drive every ○ and ◐ to ✅. Counts are as of the 06–12-07-2026 census
re-measure; re-verify before a large change.

### L1 · Lexicon text (44 dictionaries)

| Statistic | Count / status | Where |
|---|---|---|
| Dictionaries digitized | **44** ✅ (14 Skt→Eng · 6 Skt→Skt · 5 Skt→Ger · 3 Eng→Skt · 2 Skt→Fr · 1 Skt→Lat · 12 specialized) | FEATURES_INDEX §II |
| Union headwords (15-dict) | **323,425** ✅ | [`union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) |
| Pairwise overlap matrix + Jaccard | **105 pairs** ✅ (H684, E40) | [`headword_overlap_matrix.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/headword_overlap_matrix.tsv) |
| Markup-tag frequency census | **96 tags · 17.5 M hits** ✅ (H683, E39) | [`markup_tag_census.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv) |
| `<ls>` citation-frequency graph | **828,505 citations → 912 texts** (11 dicts) ✅ (E38) | [csl-atlas `data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations) |
| Correction-event log | **52,498 events · 43 dicts · 210 correctors · 2014–2026** ✅ (E41) | [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) |
| n-gram membership oracle | **6,656,616 n-grams** ✅ (F43) | [CORRECTIONS/ngram](https://github.com/sanskrit-lexicon/CORRECTIONS/tree/master/ngram) |
| Sense-count / polysemy distribution per dict | ◐ partial (11/44 general lexica; A02 paper, mirrored H817 — FEATURES_INDEX E45) · **dashboard live 23-07-2026 (H1524)** | report [sense_polysemy_per_dict.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/sense_polysemy_per_dict.md) · page [`/sense-polysemy`](https://sanskrit-lexicon.github.io/csl-observatory/sense-polysemy) |
| Diachronic first-attestation (which dict coins a headword) | ◐ partial (A40 growth curve only) | ARTICLES A40 |
| Definition typology (synonym vs equivalent vs encyclopedic) | ◐ 24-07-2026 (H1483) — rubric + **all 44 csl-orig dicts / 1,496,157 records** (`--all`) + gold 55/79=69.6%; double-key pool still open | report [DEFINITION_TYPOLOGY_WS2_4_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md) · script [definition_typology_classifier.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_classifier.py) |
| Per-dict editorial fingerprint (citation × markup × error) | ○ not started | — |

### L2 · Morphology & forms (kosha · DCS · Heritage · vidyut)

| Statistic | Count / status | Where |
|---|---|---|
| kosha.db | **444,773 entries · 692,403 senses · 1,378,401 forms · 6,916,522 inflections** ✅ (H687 audit) | [KOSHA_DB_COMPLETENESS_AUDIT.md](https://github.com/gasyoun/kosha/blob/main/docs/KOSHA_DB_COMPLETENESS_AUDIT.md) |
| DCS lemmas / forms | **180,176 lemmas · 408 k form→lemma rows** ✅ | [SanskritRussian `dcs_form2lemma.tsv`](https://github.com/gasyoun/SanskritRussian) |
| Heritage form oracle + DICO gloss | **24.5 k DICO lemmas · form-alignment oracle** ✅ (D19–D24) | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| vidyut FST fallback | **28,500 forms** ✅ (E29) | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| Paradigm-cell coverage (which cells attested per root) | ✅ (H817 — FEATURES_INDEX E46, 8,054/11,096 roots, 171 distinct finite cells) · **dashboard live 23-07-2026 (H1524)** | report [paradigm_cell_coverage.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/paradigm_cell_coverage.md) · page [`/paradigm-cell-coverage`](https://sanskrit-lexicon.github.io/csl-observatory/paradigm-cell-coverage) |
| Form→lemma ambiguity rate (how polysemous is a surface form) | ○ not started | — |

### L3 · Corpus & usage (DCS · SamudraManthanam)

| Statistic | Count / status | Where |
|---|---|---|
| DCS full corpus | **5,688,416 tokens · 754,726 sentences · 1,024,841 MWT · 270 texts** ✅ | [VisualDCS `dcs_full.sqlite`](https://github.com/gasyoun/VisualDCS) |
| SamudraManthanam Sa↔Ru corpus | **580,552 lines · 152 sources** ✅ | [SamudraManthanam](https://github.com/gasyoun/SamudraManthanam) |
| Stop-word parallels | **40,573,260** ✅ | [VisualDCS M9](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/m9_archive_ingest.md) |
| Frequency layer (per-period vectors) | **83,277 lemmas** ✅ (E26) | [kosha `lemma_frequency.tsv`](https://github.com/gasyoun/kosha/blob/main/data/frequency/lemma_frequency.tsv) |
| 2021→2026 corpus delta | ✅ (H686) | [Corpus-Delta report](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/REPORT.md) |
| POS distribution per text | ✅ (H817 — FEATURES_INDEX E44, 270/270 texts, 5,688,416 tokens) · **dashboard live 23-07-2026 (H1524)** | report [pos_distribution_per_text.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pos_distribution_per_text.md) · page [`/pos-by-text`](https://sanskrit-lexicon.github.io/csl-observatory/pos-by-text) |
| Lemma/root frequency bands **per text** (not just whole-corpus) | ◐ partial (whole-corpus done in E26) | kosha |
| Meter / prosody statistics | ○ not started | SanskritKaraoke |
| Vedic accent coverage | ○ not started (VedaWeb reuse pending) | VedaWeb M13 |

### L4 · Translation (RU/EN kits · alignment · glossaries)

| Statistic | Count / status | Where |
|---|---|---|
| corpus_lexicon Sa→Ru alignment | **1,093,391 rows** ✅ (A1) | [RussianTranslation/src](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src) |
| 3-layer glossary + coverage | **233 k entries · 87 % coverage** ✅ (A2) | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| RU-gloss gap-list (untranslated keys) | **242,726 keys (36,974 DCS-attested)** ✅ (H685) | [glossary README](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossary/README.md) |
| mw_ru cards | **287,358** ✅ | [RussianTranslation/mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md) |
| Per-dict RU coverage % | ✅ (GRA 76.8 % … SKD 16.5 %) (H685) | glossary README |
| Coverage trajectory over time (translation velocity) | ○ not started | — |
| QA-judge inter-rater agreement (κ) | ◐ partial (two-judge design exists; κ not reported) | LANG_PARITY |

### L5 · Roots & etymology

| Statistic | Count / status | Where |
|---|---|---|
| MW verbal-root inventory | **2,113 roots** ✅ (B5) | [`mw_roots.tsv`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw_roots.tsv) |
| Etymology derivation tables | **10 dicts · ~9–11 k rows each** ✅ (B6) | [csl-orig v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02) |
| Root-oracle agreement matrix (41-pair, 95 % CI) | ✅ (B7) | csl-orig v02 |
| Whitney × DCS root audit | **935-root hub audited** ✅ (B10) | [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) |
| Corpus root-class verdicts | ✅ but **capped** — unaccented DCS can't split class I/VI (B11) | WhitneyRoots |
| Affix entropy / frequency | ✅ (B7) | csl-orig v02 |

### L6 · Repo-meta & process

| Statistic | Count / status | Where |
|---|---|---|
| Correction typology | ✅ (empirical error taxonomy) | csl-observatory |
| Bus-factor census | ✅ (**65/76 repos bus-factor-1**) | csl-observatory |
| Data footprint | **~27.5 GB · 1,343 large files · 70 % local-only** ✅ | this census §1 |
| Code-duplication census (transcoder ×62, digentry ×170) | ✅ **already done before this roadmap was authored** — H688 (11-07-2026, csl-observatory PR #85), register was stale; re-registered H817 as FEATURES_INDEX E43 | [csl-observatory code_duplication_census.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/code_duplication_census.md) |
| Publication-pipeline health (readiness, handoff aging) | ◐ partial (dashboard exists, not time-series) | Uprava dashboard |
| LOC & language mix per repo | ✅ **already done before this roadmap was authored** — H688 §4, register was stale; re-registered H817 as FEATURES_INDEX E43 | [csl-observatory code_duplication_census.md §4](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/code_duplication_census.md) |

### L7 · Product & funnel

| Statistic | Count / status | Where |
|---|---|---|
| ORS-FAQ Telegram export | **3,180 chats · 170,017 msgs · 8,729 contacts · 2022→2026** ✅ (H693) | [ORS-FAQ provenance](https://github.com/gasyoun/ORS-FAQ/blob/main/docs/telegram_export_result_json_provenance.md) |
| telegram-sanskrit-corpus grade stats | **tooling ✅, data 0** — no harvest has run (H690) | [CORPUS_STATS.md](https://github.com/gasyoun/telegram-sanskrit-corpus/blob/main/docs/CORPUS_STATS.md) |
| Systema LMS enrollment / funnel | ○ not started (gated on host DB creds) | Systema-Sanscriticum |
| samskrte.ru marketing funnel | ○ not started | — |
| Course engagement / retention | ○ not started | — |

**Scoreboard (updated 13-07-2026, H817 WS1.2):** ~32 statistics ✅ computed · ~6 ◐ partial ·
~10 ○ not started. Of this pass's 5 targeted descriptive rows, 2 (code-duplication census,
LOC & language mix) turned out **already done** before this roadmap was authored — H688,
11-07-2026 — the register simply hadn't caught up; 2 more (POS-per-text, paradigm-cell
coverage) are newly closed; 1 (sense/polysemy per dict) is ◐ partial — done for the 11/44
general lexica where a sense-marking convention exists, genuinely blocked for the other 33
(no structural sense markers; the `<L>` decimal-suffix shortcut was tried and confirmed
invalid). The open surface is overwhelmingly **analytical, product, and
process** — which is exactly what the four quarters below target.

---

## Part I — The gap, prioritized

The QA ordering inherited from the census §3 stands, and the year respects it:

1. **Provenance & backup come before statistics.** The single genuine single-copy,
   non-rebuildable giant — `corpus_lexicon.jsonl` (290 MB, DeepSeek-aligned, append-only) —
   is still MG-gated behind [H235](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
   No amount of downstream statistics is worth more than not losing the input. **Q1, first.**
2. **Finish the descriptive ○ rows** (code-dup census, POS-per-text, polysemy, paradigm
   coverage, LOC) — cheap, foundational, closes the register.
3. **The analytical layer** (diachronic, editorial fingerprints, network stats, definition
   typology) — the highest-value middle, and the direct feed to A40/A50/A08.
4. **Publishable-novel** (error-typology model, lemmatization-policy comparison,
   corpus-grounding of the lexicon) — highest novelty, coordinate against ARTICLES anti-salami.
5. **Product/funnel** — a *separable* stream, gated on host access (Systema DB creds,
   Telegram harvest); scheduled but never allowed to block the lexicon/corpus work.

---

## Part II — The 12-month plan

Quarters are calendar quarters from now. Each workstream names its **home repo**, its
**deliverable form** (📊 dashboard · 📦 FAIR release · 📄 report/chapter · ➡️ feeds a paper),
and gets one handoff at execution time.

### Q1 · Jul–Sep 2026 — "Finish the census, secure it, stand up the board"

*Theme: descriptive completeness + QA-first backup + the dashboard skeleton.*

- **WS1.1 — Backup + dedup (QA #1).** Back up `corpus_lexicon.jsonl` (MG-gated H235); dedup
  the `assembled_cards*` / `*.renou*` pipeline variants (~1.4 GB recoverable) and reconcile
  the `.`-vs-`_` naming drift. 📦 + hygiene. Home: SanskritLexicography.
- **WS1.2 — Close the descriptive ○ rows.** Code-duplication census (L6 flagship —
  transcoder ×62, digentry ×170 → the sanskrit-util payoff baseline); POS distribution per
  text (L3); sense/polysemy distribution per dict (L1); paradigm-cell coverage (L2); LOC &
  language mix (L6). 📄 + 📊. Home: csl-observatory + SanskritLexicography.
- **WS1.3 — Statistics dashboard skeleton. ✅ done 13-07-2026 (Sonnet 5 `claude-sonnet-5`,
  H817).** 6 Observable pages shipped in
  [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) (PR
  [#89](https://github.com/sanskrit-lexicon/csl-observatory/pull/89), merged): a
  census overview + one page per L1–L5 layer, seeded from a new
  `stats_census_register.csv` feed (~60 rows across all 7 layers), each figure
  carrying the house trust block (source artifact, n, date) + a filterable
  data-table fallback + CSV download (the `/viz-page` pattern). L6 already has
  extensive dedicated coverage (repo health, org shape, community pages); L7
  is mostly ○ not started / gated, tracked in the register but no dedicated
  page yet. 📊.
- **WS1.4 — FAIR release #1. Metadata prepared 13-07-2026 (Sonnet 5
  `claude-sonnet-5`, H817); deposit itself parked `@DO` (Zenodo account/token,
  MG-gated).** `CITATION.cff` + `DATA_LICENSE.md` added to this repo;
  [`data/FAIR_RELEASE_1.md`](data/FAIR_RELEASE_1.md) packages the markup-tag
  census (E39) + headword-overlap matrix (E40) as one curated, file-level
  Zenodo deposit (CC-BY-4.0, deposit-ready metadata JSON included) —
  deliberately **not** a whole-repo GitHub→Zenodo integration, since this repo
  mixes in third-party-rights-uncertain scan PDFs a full archive would sweep
  in. The citation graph (E38, csl-atlas) is cross-linked, not duplicated;
  csl-atlas already carries its own prepared `.zenodo.json` for a
  repo-level integration there — enabling it + cutting a release is a
  separate `@DO`. Directly attacks ATLAS_FAIR **G1** (no persistent
  identifiers). 📦.

**Q1 targets — measured at the quarter boundary, 01-09-2026 (H3793):**

| Target | Verdict | Evidence |
|---|---|---|
| 100 % of *descriptive* rows → ✅ | **MISSED** — 9 `not_started` + 8 `partial` in the feed, but 4 are L7 (deliberately deferred) and 2 externally gated (Vedic accent → VedaWeb; meter/prosody → SanskritKaraoke). Genuinely in-scope misses: **form→lemma ambiguity (L2)** and **translation velocity + QA-judge κ (L4)** | feed counts, §3.2 of the Q1/Q2 pass |
| ≥1 single-copy giant backed up | **✅ MET, exceeded** — `corpus_lexicon.jsonl` is now **three-copy** (git twin in `pwg-ru-data` H3316 · `D:\Backups` mirror H1998 · digest-verified off-machine `samskrtam.ru/guhya` [H3389](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3389-OxAlpha_Uprava_kosha-guhya-restricted-backup-upload_23.08.26.md), restore-rehearsed 43 s, sha256 triple-match) | [SHADOW_ASSETS_POINTERS.md](https://github.com/gasyoun/Uprava/blob/main/SHADOW_ASSETS_POINTERS.md) |
| ≥6 observatory stat-pages live | **✅ MET** — 36 pages in [`observatory/site/src/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site/src); the WS1.3 census family is 6, plus 3 dedicated stat pages under H1524 | csl-observatory tree |
| FAIR release #1 metadata prepared, deposit `@DO` | **✅ metadata · ✗ deposit** — and the stated rationale is now contradicted by a live repo-wide Zenodo integration ([CONTRADICTIONS §17](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md), opened 01-09-2026) | [data/FAIR_RELEASE_1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md) § Status |

**Two register rows are capped, not pending** — sense/polysemy at 11/44 dicts (33 dicts carry
no structural sense markers) and corpus root-class (accent collapse). "Drive every ○ and ◐ to
✅" is unachievable as written; the register needs a **capped** status distinct from
**partial** before the KPI can stop chasing an unreachable 100 %.

### Q2 · Oct–Dec 2026 — "The analytical layer"

*Theme: comparative / diachronic / network — the interesting middle; feed the papers.*

- **WS2.1 — Diachronic lexicography.** First-attestation of each headword across the 44
  dicts 1832–1976; the vocabulary growth curve. ➡️ takes **A40** (CDSL headword 12-yr growth)
  to 5/5. Home: SanskritLexicography + VisualDCS.
- **WS2.2 — Editorial fingerprints.** A 44-row comparative table: each dict's citation
  profile × markup style × error typology. ➡️ feeds **A50** tradition profiles and **A08**
  citation-register work. Home: csl-atlas.
- **WS2.3 — Citation-graph network statistics.** Centrality, co-citation, text communities
  over the 912-text `<ls>` graph. ➡️ takes **A50** (what the tradition cites) to 4/5. 📊.
- **WS2.4 — Definition typology.** Synonym-gloss vs equivalent vs encyclopedic per dict —
  the classic microstructural axis the ATLAS_FAIR audit flags as absent. 📄.
  **◐ 24-07-2026 (H1483), two waves — cite the current one:** the H1483 first pass covered
  15 core dicts / 926,759 records at gold 63/79 = 79.7 %; the committed `--all` table
  **supersedes it** at **44/44 csl-orig dicts · 1,496,157 `<L>` records · gold 55/79 = 69.6 %**
  in [data/DEFINITION_TYPOLOGY_WS2_4_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md)
  (accuracy falls as scope widens from 15 core dicts to all 44 — the expected direction, not a
  classifier regression). Gold is single-pass, **not** double-keyed, so 69.6 % is not a
  publication-grade precision. Remaining: Wilson `E.` peel, sense-level split, ATLAS 300×7
  double-key pool — only the last raises precision to a citable figure.
- **WS2.5 — FAIR release #2** (analytical datasets, DOIs). 📦.

**Q2 targets — restated 01-09-2026 (H3793) against measured readiness.** Full design, with
the prior art already committed for each workstream, in
[Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md) §5.

| Target | Restated | Why |
|---|---|---|
| A40 → 5/5 | keep, but **not counted as portfolio progress** | MG ruled «A38 counts, drop A40 from the fifteen» 29-07-2026 ([ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)) — the uplift no longer advances the degree set |
| A50 → 4/5 | keep — this is the live one | 3/5 today, unmoved since the 12-07 baseline; WS2.3 is its direct feed, **after** the §14 resolver probe |
| ≥4 analytical dashboard pages | keep, **conditional** on refreshing the machine feed first | the pages render from `stats_census_register.csv`, stale since 12–18-07-2026 and wrong in three rows |
| FAIR release #2 | **hold** | blocked by [CONTRADICTIONS §17](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) — a human decides the rights posture first |

**Sequencing note (the one re-ordering that matters).** WS2.3 must follow the
[CONTRADICTIONS §14](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
probe, not precede it: MW resolves to **5 coarse placeholder nodes** in the `<ls>` graph while
PWG contributes **536,172 of 828,505** resolved citations (64.7 %), so any centrality,
co-citation or community statistic computed on the graph as it stands measures resolver
coverage as much as canon shape — and would have to be recomputed after the 10-dict (or
apparatus-fed) re-run lands.

### Q3 · Jan–Mar 2027 — "Publishable-novel + open the product stream"

*Theme: inferential/novel findings + the product/funnel analytics family.*

- **WS3.1 — Error-typology model.** Over the 52,498 correction events: which entries are
  error-prone, and why (predictive, not just descriptive). ➡️ csl-observatory OBS-T lineage.
- **WS3.2 — Lemmatization-policy & access-structure comparison.** What counts as a lemma
  (root vs stem vs 3sg) across the 9 core dicts; alphabetization/anusvāra-sort regimes —
  the ATLAS_FAIR macro-gaps. 📄 ➡️ book.
- **WS3.3 — Corpus-grounding of the lexicon.** Union headwords × DCS attestation: which
  headwords are corpus-attested vs ghost-words. ➡️ learner's frequency layer + A40. 📊.
- **WS3.4 — Product/funnel analytics** (separable, gated). Run the Telegram harvest (H690
  gate), Systema enrollment/funnel, samskrte.ru funnel — a distinct **local-only** dashboard
  family (never published without `/publish-safety-check`; carries personal data). 📊.
- **WS3.5 — Meter/prosody + Vedic accent** (SanskritKaraoke + VedaWeb reuse). 📊.

**Q3 targets:** ≥1 publishable-novel finding drafted (new Axx or folded per anti-salami);
product dashboard live *if* creds land, otherwise parked with the blocker named.

### Q4 · Apr–Jun 2027 — "Synthesis: report, chapter, observatory launch"

*Theme: consolidate the year into durable, citable outputs.*

- **WS4.1 — Internal methods report → monograph chapter.** "How we count a lexicographic
  tradition" — the corpus-methods chapter (**M01** `@DECIDE`, currently new-chapter-vs-
  Ch.2-section). 📄. **Internal report SHIPPED 31-07-2026 (H1871):**
  [METHODS_HOW_WE_COUNT_A_TRADITION_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md)
  — every counting convention with artifact + exact query, 16-row reconciliation table,
  CONTRADICTIONS §10–§13 for the unreconcilable pairs. The M01 chapter-form `@DECIDE`
  stays open; the report is the chapter's source text.
- **WS4.2 — Public observatory launch.** The whole statistics board goes public after
  `/publish-safety-check`, every figure citing its FAIR DOI. 📊 (public).
- **WS4.3 — Complete the FAIR release set.** Every derived stat dataset versioned on Zenodo
  with a DOI; closes ATLAS_FAIR **G1** fully. 📦.
- **WS4.4 — Payoff retro.** Re-run the Q1 code-dup census → measure the actual sanskrit-util
  dedup payoff; report κ/inter-annotator on any human-reviewed statistics.

**Q4 targets:** methods report shipped; observatory public; FAIR set complete; the Part 0
register final (all ✅).

---

## Part III — Delivery architecture

| Form | Where | House pattern |
|---|---|---|
| 📊 **Dashboards** | [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) (Observable+Plot), [csl-guides](https://github.com/sanskrit-lexicon/csl-guides) (Docusaurus MDX) | committed feed → build-time figure → trust block (source artifact · n · date) → data-table fallback with CSV download → smoke/bundle verify (the `/viz-page` skill) |
| 📦 **FAIR releases** | Zenodo, per dataset | concept + version DOI, `CITATION.cff` (ORCID byline), per-dataset licence field; each release also *backs up* the derived stat dataset — kills two ATLAS_FAIR gaps (G1 identifiers, G6 dataset-level licensing) at once |
| 📄 **Report / chapter** | SanskritLexicography (report) → monograph (M01 chapter) | dated Markdown methods report; every claim re-verified against the committed feed; becomes one book chapter |
| ➡️ **Paper feed** | [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) | statistics advance A40/A50/A08/A35; **anti-salami** — coordinate, never spawn a competing paper for a number that an existing slot already owns |

---

## Part IV — Governance, KPIs, risks

**Model tiers per workstream.** Mechanical census + dashboards → Fable 5
(`claude-fable-5`) / Sonnet 5 (`claude-sonnet-5`); analytical → Sonnet 5; publishable-novel
& the methods chapter → Opus 4.8 (`claude-opus-4-8`) / Fable 5. One `H###` handoff per
workstream, minted at execution via `mint_handoff.py`; concurrency isolated in worktrees
per the shared-tree guard.

**KPIs (year-end targets).**

| KPI | Baseline (12-07-2026) | Target (30-06-2027) |
|---|--:|--:|
| Statistics register ✅ ⚠️ **denominator disputed** — see note below | ~28 / 48 (~58 %) | 48 / 48 (100 %) |
| Live dashboard stat-pages | 0 dedicated | ~20 (all 7 layers) |
| FAIR datasets with DOIs | 0 | ~15 (every derived stat dataset) |
| Single-copy giants backed up | 0 / 1 genuine | 1 / 1 |
| Papers advanced | A40 4/5 · A50 3/5 · A08 4/5 | A40 5/5 · A50 4/5 · A08 5/5 · ≥1 new |

**⚠️ The register KPI has no denominator of record (01-09-2026, H3793).** The register is
counted three ways and none agrees: this file's Part 0 scoreboard prose says ~48 (~32 ✅ · ~6 ◐
· ~10 ○), the KPI row above says 48, and the machine feed
[`stats_census_register.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/stats_census_register.csv)
— the only machine-readable surface, and the one the public dashboard pages render from —
carries **59 rows (42 done · 8 partial · 9 not_started)**. A percentage cannot be reported
until one is adopted; the feed's 59 is the only candidate a script can recompute. The feed is
also stale (stamped 12–18-07-2026) and understates three rows: L1 definition typology reads
`not_started` though it is ◐ over all 44 dicts, and L2 paradigm-cell coverage and L3
POS-per-text read `partial` though both are ✅ since H817/H1524.

**Risks & mitigations.**

- ~~**Backup gap (highest).** `corpus_lexicon.jsonl` is single-copy and not rebuildable —
  Q1-WS1.1, MG-gated (H235).~~ **✅ CLOSED — verified 01-09-2026 (H3793).** The file is
  **three-copy**: a git-tracked twin in `pwg-ru-data` (H3316), a `D:\Backups` mirror (H1998),
  and a digest-verified off-machine copy at `samskrtam.ru/guhya`
  ([H3389](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3389-OxAlpha_Uprava_kosha-guhya-restricted-backup-upload_23.08.26.md);
  restore rehearsed in 43 s, sha256 triple-match), recorded in
  [SHADOW_ASSETS_POINTERS.md](https://github.com/gasyoun/Uprava/blob/main/SHADOW_ASSETS_POINTERS.md).
  Q2 does not inherit this risk. Everything else in §2 regenerates from git-tracked sources.
- **Rights posture is stated two ways (new, 01-09-2026).** A repo-wide Zenodo/GitHub
  integration is live and minting while `DATA_LICENSE.md` and `data/FAIR_RELEASE_1.md` both say
  it is deliberately not used —
  [CONTRADICTIONS §17](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).
  Not a stop for measurement work; it does hold WS2.5 until a human settles it.
- **Salami / self-overlap.** The analytical layer feeds A40/A50/A08; enforce the ARTICLES
  anti-salami discipline — a statistic feeds the paper that already owns its question.
- **Product stream gated on creds.** Systema DB env + Telegram harvest depend on host
  access; keep WS3.4 separable so a credential wait never blocks lexicon/corpus stats.
- **Known measurement ceilings.** Unaccented DCS cannot split verb class I/VI or IV/passive
  (accent collapse); UD Tense=Past conflates aorist/perfect. Do not over-claim on root-class
  or tense statistics — cite the ceiling.
- **Bus factor 1** (ATLAS_FAIR G8, 65/76 repos). Every stat must be script-reproducible so
  the number survives one person; name a co-maintainer for the dashboard builds by Q4.

---

## Related

- [`Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md) — the Q1→Q2 quarter-boundary pass: Q1 delivery per register, the Q2 analytical layer against Part I's gaps, and the contradictions carried forward
- [`CONTRADICTIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) — §10–§14 and §17, the figure and posture disagreements this roadmap's numbers inherit
- [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) — what assets exist (the register's asset IDs)
- [`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md) — what data sits uncounted on disk (the §3 stats-to-add table this roadmap operationalizes)
- [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) — the publications / evidence-graph programme this feeds
- [`ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) — the paper pipeline (A40/A50/A08/A35)
- [`ROADMAP_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/ROADMAP_INDEX.md) — catalogue of all roadmaps (register this one here)

_Dr. Mārcis Gasūns_
