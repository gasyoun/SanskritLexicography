# How we count a tradition — counting conventions of the Sanskrit lexicographic corpus

_Created: 31-07-2026 · Last updated: 31-07-2026_

**What this is.** The org publishes counts of dictionaries, headwords, entries, lemmas,
senses, citations and corpus attestations across papers (A01–A58), the book
([Digital_Sanskrit_Lexicography-BOOK](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK)),
hub registries and dataset manifests — and until this report, **no document stated which
convention each figure uses**. This is the methods report other papers cite for their
denominators (the WS4.1 deliverable of
[ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md);
destined to feed the M01 monograph's methods chapter — the new-chapter-vs-Ch.2-section
`@DECIDE` stays open and is not resolved here).

**The rule.** A published count is citable only when it names, together: (1) the **object**
counted, (2) the **convention** (one of §2 below), (3) the **artifact** it was computed
over, (4) the **query** that reproduces it, and (5) the **snapshot** (commit/date) where
the artifact is live-edited. A convention stated without its query is not usable — every
convention below therefore carries an exact reproduction path, and every figure in §3
names its convention.

**What this report does NOT re-adjudicate.** Cross-paper figure drift already ruled in
[Uprava/CANONICAL_FIGURES_CROSS_PAPER_DRIFT_C7.md](https://github.com/gasyoun/Uprava/blob/main/CANONICAL_FIGURES_CROSS_PAPER_DRIFT_C7.md)
(the C7 registry) is **cited, not restated**: MW record counts (C7 row 1), the MW `<ls>`
census (row 2), the MBh commentary notes (row 5), token totals (row 8), the 44-vs-43
dictionary snapshot (row 10) and the DCS lemma denominators (row 11, the designated
MULTI-SCOPE exemplar — "any session that 'fixes' A38 has misread this registry"). This
report owns the layer C7 never covered: what each counting convention *is*, and the
headword/entry/sense divergences below the cross-paper layer.

---

## 1. The objects, at one glance

| Object | Canonical figure | Convention (§) | One-line definition |
|---|---|---|---|
| Dictionaries (corpus envelope) | 44 (2026-07) / 43 (2026-06) | §2.1 | CDSL digitizations at a dated snapshot |
| Union headwords | 323,425 | §2.4 | distinct post-fold SLP1 `<k1>` keys over 15 dicts |
| Census total (summed) | 1,206,384 (2026, 18 lists) | §2.5 | per-list line counts summed, duplicates kept |
| MW records | 286,5xx — pin the snapshot | §2.6 | `<L>` records in `mw.txt` at a named commit |
| Entry→lemma collapse | 1,496,157 → 410,259 | §2.7 | org-wide records collapsed to distinct lemmas |
| kosha.db rows | 444,773 entries · 692,403 senses | §2.8 | per-table `COUNT(*)` of a named build |
| Senses (measurable) | 692,403 rows / 11 of 44 dicts | §2.9 | structural sense-marking only |
| Citations (`<ls>`) | 828,505 → 912 texts | §2.10 | canonicalized 11-dict graph |
| DCS lemma denominators | 98,606 / 91,406 / 83,239 | §2.11 | per-release; never mixed in one table |
| Content tokens | 5,688,416 / 270 texts | §2.12 | DCS content tokens |
| Correction events | 52,498 | §2.13 | released OBS-T snapshot, 43 dicts |

---

## 2. The conventions

Each convention: **Definition · Artifact · Query · Canonical figure**. No prose-only
definitions — if the query is missing, the convention is not in this list.

### 2.1 Dictionary (corpus envelope and scopes)

- **Definition:** a CDSL dictionary digitization present in the corpus at a dated
  measurement snapshot. The envelope is **44** at 2026-07, **43** at 2026-06 — same
  population, two snapshots, both canonical for their date (C7 row 10; not an
  eligibility split).
- **Artifact:** [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md)
  dictionary table (headline row).
- **Query:** count the rows of the FEATURES_INDEX §Dictionaries table at the named commit.
- **Scopes that are NOT the envelope** (each a deliberate subset, never interchangeable):
  **15** = dicts with committed `<k1>`/`<lex>` headword exports — the union-headword scope
  ([HEADWORDLISTS_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md));
  **11** = dicts in the canonicalized `<ls>` citation graph (§2.10); **11 of 44** = dicts
  with structural sense-marking (§2.9); **41** = Meyer's external site, not CDSL
  ([kosha/README.md](https://github.com/gasyoun/kosha/blob/main/README.md)).

### 2.2 Headword, key1

- **Definition:** distinct dictionary-form headword keys — csl-orig `<k1>` (SLP1,
  underlying stem form). The comparability key for cross-dictionary joins.
- **Artifact:** [HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists)
  snapshot lists `now-2026/{DICT}_key1_{N}.txt`.
- **Query:** `python HeadwordLists/headword_diff.py` regenerates the census;
  per-file, the filename `{N}` is the true entry count — `wc -l` reports `N − 1`
  (no trailing newline;
  [HeadwordLists/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/README.md)).
- **Canonical figures (2026):** MW 194,084 · PWG 106,082 · PWK 151,349 · AP90 88,869
  ([ch03_headword_inventory.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch03_headword_inventory.md) §2).

### 2.3 Headword, key2

- **Definition:** distinct display-form keys — csl-orig `<k2>` (accented/homonym-marked
  display variant). Always ≥ key1 for the same dictionary. **Use key1 for de-dup joins,
  key2 never enters a union**
  ([ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md)).
- **Artifact / Query:** same census, `key2` file variant.
- **Canonical figures:** PWG 110,438 · PWK 155,688 · PW 104,968 · SCH 28,519.

### 2.4 Union headword (deduplicated)

- **Definition:** distinct SLP1 `<k1>` keys across the 15-dict export scope, **post-fold**
  (237 gender-confirmed *-inī* feminines folded onto their *-in* base).
- **Artifact:** [union/union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
  (mirrored as kosha manifest `union-headwords`).
- **Query:** `python HeadwordLists/build_union.py` → row count of the output TSV.
- **Canonical figure:** **323,425** (pre-fold raw keys: 323,662 — never cite the raw
  figure as "the union"). Membership counts inside the union: PWG-bearing 106,054,
  MW-bearing 193,852, MW∩PWG **94,753** — an **intersection, not a union**; older docs
  that used 94,753 as "the union" are wrong and were corrected in
  [A40](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md) §4.
  Reproduction recipe: [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) §5 — CONSUME, don't rebuild.

### 2.5 Summed snapshot lines (census total — duplicates kept)

- **Definition:** the **sum of per-list line counts** across comparable snapshot lists.
  A word in 10 dictionaries counts 10 times — this measures the *tradition's output*,
  not its vocabulary. Never compare against §2.4 without saying so.
- **Artifact:** [HeadwordLists/NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md)
  TOTAL row.
- **Query:** `python HeadwordLists/headword_diff.py` (regenerates NOW_VS_THEN).
- **Canonical figure:** **1,055,081 (2014) → 1,206,384 (2026), +14.3 %** over the **18
  comparable lists** (key-scheme-stable 2014↔2026). The 26-snapshot grand total
  **1,721,983** includes format-migrated lists and **must never enter a growth figure**
  (A40 §3.1).

### 2.6 Entry / record

- **Definition:** one `<L>`-numbered record in a csl-orig digitization. Live-edited —
  **no snapshot-free count exists**; every figure pins its commit (C7 row 1).
- **Artifact:** csl-orig `{dict}.txt` at a named commit.
- **Query:** count `<L>` records at the pinned commit (e.g. `grep -c "^<L>" mw.txt`).
- **Canonical figures:** MW 286,561 (`2e0e0f4c`, 2026-05-23) / 286,560 (2026-06-13) /
  286,525 (`392ed6b`, 2026-06-27) — each canonical for its snapshot; org-wide
  **1,496,157 records over 44 dicts** at the 2026-07 census
  ([ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) Part 0).

### 2.7 Lemma (entry→lemma collapse)

- **Definition:** distinct lemmas after collapsing the org-wide record set — measures how
  many *words* the tradition's records describe (3.65 records per lemma).
- **Artifact / Query:** `python scripts/obs/headword_multiplicity.py` over the 44-dict
  record set.
- **Canonical figure:** **1,496,157 entries → 410,259 distinct lemmas**
  ([ch02_measurement_framework.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md) §3);
  the earlier 409,649 was the pre-nmmb run (superseded, ch02 provenance note).

### 2.8 kosha.db table rows

- **Definition:** per-table row counts of a *named build* of the kosha SQLite database.
  A "kosha.db count" without its build date is not citable (see CONTRADICTIONS §11).
- **Artifact:** `kosha.db` per
  [kosha/data/manifest/datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json).
- **Query:** `python scripts/build_db.py` (kosha), then per-table
  `SELECT COUNT(*) FROM <table>;`.
- **Canonical figures (manifest build):** 444,773 entries · 323,425 lemmas ·
  692,403 senses · 1,378,401 forms · 6,917,018 inflections · 185,803 heritage_anchor.

### 2.9 Sense

- **Definition:** a structurally marked sense division. Only **11 of 44** dicts carry
  structural sense-marking — sense counts are *never* corpus-envelope-wide
  ([Uprava/DATA_LAYERS_CENSUS.md](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md), H817/E45).
- **Artifact / Query:** kosha.db `senses` table (`SELECT COUNT(*) FROM senses;`) for the
  aggregate; `sense_polysemy_per_dict.md` for the per-dict distribution.
- **Canonical figure:** **692,403** sense rows (manifest build, §2.8 caveat applies).

### 2.10 Citation / attestation (`<ls>`)

Three distinct conventions — never mix:

- **Raw `<ls>` occurrences:** literal tag count in a digitization. Org-wide raw base:
  1,496,302 (11-dict scope). Per-dict shape differs wildly (PWG 4.61 `<ls>`/entry vs MW
  1.09 — [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md));
  kośa dicts cite via `iti` with **zero** `<ls>` (SKD 80,164 `iti`), so raw `<ls>` counts
  systematically under-represent them (ch02 §3).
- **Canonicalized citation graph:** `<ls>` values canonicalized to distinct source texts.
  **Query:** csl-atlas graph build ([csl-atlas PR #220](https://github.com/gasyoun/csl-atlas/pull/220)).
  **Canonical figure: 828,505 citations → 912 texts (11 dicts, 57.8 % of raw)** —
  supersedes the first-pass 848,390 → 1,124 (8 dicts). The later figure is *smaller with
  more dictionaries* because canonicalization is stricter — not a typo (§3, row 6).
  **Composition caveat (must accompany any denominator use):** PWG alone contributes
  **536,172** of the 828,505 resolved citations (64.7 %), while MW — the corpus's largest
  dictionary — resolves to only **5 coarse placeholder nodes**
  ([H272 synthesis memo](https://github.com/gasyoun/Uprava/blob/main/handoffs/H272_SYNTHESIS_MEMO_07.07.26.md)).
  Neither fact appears in the FEATURES_INDEX or FAIR_RELEASE_1 statements of the figure;
  any paper using 828,505 as an attestation denominator inherits both.
- **MW two-shape census:** MW-specific census of record counting arabic + roman locators
  and attributed-shape tags. **Canonical: 320,828** (C7 row 2, ADJUDICATED); 312,160 is
  the csl-atlas literal-regex figure (misses MW's 8,668 attributed-shape citations) and
  311,932 the arabic-only rule — both superseded, quotable supersession sentences live in
  C7. Locator share of record: 18.96 % (60,820/320,828).

### 2.11 Corpus attestation (DCS lemma denominators)

- **Definition:** whether a headword is attested in the Digital Corpus of Sanskrit —
  always relative to a **named DCS release**. Policy (A38, verbatim header "Lemma-count
  provenance — do not conflate"): **98,606** = DCS-2026 release headline · **91,406** =
  DCS-2021 attested-by-LemmaId · **83,239** = the vendored DCS-2021 asset
  ([dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json)).
  One denominator per table, the release always stated (C7 row 11 — the exemplar).
- **Query:** row counts of the named release asset; cross-walk arithmetic verified in C7
  (89,645+1,761=91,406; 89,645+8,961=98,606).
- **Attestation-rate caveat:** union-wide attestation **61,340/323,425 = 19.0 %** is a
  **bare-lemma join — an upper bound**, not a per-token match (A40 §5). Two further
  corpus-side figures are *different objects*, not rival denominators: **95,457** =
  distinct lemmas occurring in the 5,688,416-token content-token slice (ch02 §3.6) and
  **90,349** = the exact per-token join
  ([MODULES_OWNED.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/sanskrit_in_numbers/MODULES_OWNED.md)).
  The bare "**180,176** DCS lemmas" in the statistics roadmap carries no release or query
  and is **not citable until provenanced** (flagged in §3, row 7).

### 2.12 Token

- **Definition:** DCS content tokens (function-word-filtered), the corpus-size unit.
- **Artifact / Query:** DCS-2026 ingest, per
  [ch02_measurement_framework.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md) §3.6.
- **Canonical figure:** **5,688,416 content tokens · 270 texts · 754,726 sentences**;
  "5.6M" was a truncation of this figure, not a rival measurement (C7 row 8). Hapax share
  39,987 = 41.9 % of the 95,457 corpus-slice lemmas.

### 2.13 Correction event

- **Definition:** one recorded correction to a csl-orig digitization in the OBS-T
  released snapshot (2014-03-18 → 2026-05-30, 43-dict envelope).
- **Artifact / Query:** csl-observatory OBS-T dataset build
  ([csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory)).
- **Canonical figure:** **52,498** — supersedes the pre-release 50,953 (C7 row 8 block).
  Unique correctors: **208** (C7-adjudicated against the released CSV, sha256-matched) —
  the "210 correctors" still carried by the
  [H795 WSC2027 report brief](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H795-Fable_SanskritGrammar_wsc2027-cdsl-report-remake_12.07.26.md)
  is superseded.

---

## 3. Reconciliation of divergent published figures

Figure · convention · source · why it differs. Rows marked **→ §N** could not be
reconciled and are logged as
[CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
rows rather than picked between.

| # | Quantity | Figures in print | Reconciliation |
|---|---|---|---|
| 1 | Union headwords | **323,425** · 323,662 · 323,426 · "~323k" · 94,753 | 323,425 = post-fold canonical (§2.4). 323,662 = pre-fold raw keys ([ch03](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch03_headword_inventory.md) §5; UNION.md's "in N dicts" table computes on this base). "~323k" = sanctioned rounding. 94,753 = MW∩PWG **intersection** mislabeled as union in older docs (fixed in A40 §4). **323,426 (kosha README + three handoffs) is an undocumented off-by-one → §10.** |
| 2 | Aggregate census headline | **1,055,081→1,206,384 (+14.3 %)** · 605,813→733,617 (+21.1 %) · 1,721,983 | 18-comparable-list census (A40/ch03) is canonical. The 9-list figure in [HeadwordLists/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/README.md) is an earlier, smaller comparable set — a historical subset, now cross-referenced to this report. 1,721,983 = 26-snapshot grand total, never a growth base (§2.5). |
| 3 | "Size of MW" | 194,084 · 193,852 · 187,506 · 185,803 · 286,5xx | Five different objects: key1 census (§2.2) · distinct union-contributing keys (§2.4) · English-gloss TM rows (`mw_en_tm.json`) · MW→Heritage crosswalk denominator (97.6 % anchor-resolved) · `<L>` records, snapshot-pinned (§2.6, C7 row 1). None is "wrong"; citing any without its convention is. |
| 4 | "Size of PWG" | 123,366 · 106,082 · 110,438 · 106,054 · 98,639 | Records (RENOU register census base) · key1 (§2.2) · key2 (§2.3) · union-contributing keys (§2.4) · Zaliznyak grammar-index rows ([A56](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) title figure — an *index* row count, not a headword census; A56 must state this). |
| 5 | MW `<ls>` total | **320,828** · 312,160 · 311,932 | C7 row 2, ADJUDICATED — two-shape census of record; the others are instrument artifacts with quotable supersession sentences in C7. |
| 6 | Citation graph | **828,505 → 912** (11 dicts) · 848,390 → 1,124 (8 dicts) | Supersession, not a rule dispute. Later run covers *more* dicts yet yields *fewer* resolved citations/texts because canonicalization tightened — must be stated wherever both appear. [Uprava/DATA_LAYERS_CENSUS.md](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md) still carries the superseded pair (hub-staleness fix queued, see §5). |
| 7 | DCS lemma denominator | **98,606** · 91,406 · 83,239 · 95,457 · 90,349 · 180,176 | First three: C7 row 11 per-release policy (§2.11). 95,457 and 90,349: different objects (corpus-slice lemmas; exact per-token join), now named in §2.11. **180,176** ([ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) Part 0): no release, no query — not citable until provenanced. |
| 8 | Petersburg family union | 167,904 · 167,988 | Different bases, both legitimate: 167,904 = PWG+PWK+SCH filter of the 15-dict union ([MODULES_OWNED.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/sanskrit_in_numbers/MODULES_OWNED.md)); 167,988 = the 4-layer `dict_merge.py` universe incl. PWKVN ([PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md)). Each doc now states the other exists. |
| 9 | Petersburg naive sum | 285,799 · 285,950 | **Unexplained 151-row gap between two committed sums of the same four lists → §12.** |
| 10 | Dictionary count | 44 · 43 · 41 · 15 · 11 | Snapshot split (C7 row 10) + deliberate scopes (§2.1). Open disclosure residuals (A01 abstract unqualified; FEATURES_INDEX G1 line "all 43") are C7's, not re-opened here. |
| 11 | Entry→lemma collapse | **410,259** · 409,649 | Pre-nmmb run superseded (§2.7, ch02 provenance note). |
| 12 | Apte key1 | **88,869** · 88,867 | Two-headword edit between extraction runs; census table authoritative; the open gate (pin a csl-orig SHA) is tracked at ch03 §2.4/A40 §2. |
| 13 | SCH | 28,519 · 28,455 · 28,431 | key2 (§2.3) · entries ([RussianTranslation/DICTIONARY_CHAIN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DICTIONARY_CHAIN.md)) · union-contributing keys (§2.4). |
| 14 | kosha.db inflections / tables | 6,917,018 (10 tables) · 6,916,522 (8 tables) | **Manifest and live-build census describe different builds under one name → §11.** |
| 15 | corpus_lexicon rows | 1,093,391 · 1,091,528 | **Unexplained 1,863-row gap (hub/roadmap vs [A42](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A42_corpus_lexicon_resource.md)) → §13.** |
| 16 | MW record count | 286,561 · 286,560 · 286,525 | C7 row 1 — snapshot-pinned, all three canonical for their commit; conflation forbidden. |

---

## 4. Unreconcilable pairs — logged, not picked

Per the H1871 watch-out, where two published numbers cannot be reconciled this report
logs a contradiction rather than choosing:
[CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
**§10** (union 323,425 vs 323,426), **§11** (kosha.db manifest vs live-build drift),
**§12** (Petersburg naive sum 285,799 vs 285,950), **§13** (corpus_lexicon 1,093,391 vs
1,091,528) — filed in the same pass as this report, with a kosha `[integrity]` issue for
the two kosha-owned rows.

## 5. Known stale surfaces (queued fixes, out of this report's scope)

- [Uprava/DATA_LAYERS_CENSUS.md](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md)
  still publishes the superseded 848,390/1,124 citation graph (row 6 above).
- [Uprava/CLAUDE.md](https://github.com/gasyoun/Uprava/blob/main/CLAUDE.md) mirrors an
  outdated FEATURES_INDEX headline ("20 interfaces · 37 data assets" vs the live
  "22 interfaces (17 live) · 47 data assets").
- The **public csl-guides citation-graph explainer page** shipped under
  [H715](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H715-Fable_csl-guides_citation-graph-explainer-page_11.07.26.md)
  was briefed off the superseded 848,390/1,124 run while its sibling H279 deliverable
  used the canonical 828,505/912 — the live page needs checking for the dead figure
  (a public artifact would then disagree with every paper).

## 6. Provenance

Compiled 31-07-2026 under
[H1871](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1871-Fable_SanskritLexicography_methods-report-how-we-count-a-tradition_29.07.26.md)
by Fable 5 (`claude-fable-5`), from a two-agent survey of SanskritLexicography and the
Uprava hubs (figures verified against
[A40](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md),
[ch02](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md)/[ch03](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch03_headword_inventory.md),
the [C7 registry](https://github.com/gasyoun/Uprava/blob/main/CANONICAL_FIGURES_CROSS_PAPER_DRIFT_C7.md),
[RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) and
[kosha/data/manifest/datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)).
Registered in
[ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md)
§WS4.1. Improvement backlog: sibling
[METHODS_HOW_WE_COUNT_A_TRADITION_2026.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.meta.md).

_Dr. Mārcis Gasūns_
