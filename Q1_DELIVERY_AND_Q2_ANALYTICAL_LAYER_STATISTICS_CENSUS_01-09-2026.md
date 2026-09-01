# Q1 delivery and the Q2 analytical layer — organisation statistics census, quarter boundary 01-09-2026

_Created: 01-09-2026 · Last updated: 01-09-2026_

**What this is.** The quarter-boundary pass on
[ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md):
Q1 (Jul–Sep 2026, *"finish the census, secure it, stand up the board"*) is closing and Q2
(Oct–Dec 2026, *"the analytical layer"*) is the next quarter. It answers two questions in
order — **what did Q1 actually deliver, per counting register** — and only then **what the
analytical layer should be**, because the roadmap's Part I is an explicitly *prioritized*
gap list and the analytical layer is item 3 on it, entered from items 1 and 2, not designed
independently of them.

Written under [H3793](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3793-Opus_SanskritLexicography_statistics-org-census-q2-analytical-layer_31.08.26.md)
by Opus 5 (`claude-opus-5[1m]`).

**Standing constraint carried through the whole document.** The unreconcilable figure pairs
in [CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
**§10–§13** are not background: they are named per workstream in §6 below, and each one that
still blocks a Q2 workstream is stated as a blocker rather than averaged away. A comparative
layer built on top of a figure whose value is disputed inherits the dispute silently — that
is precisely the failure this section exists to prevent.

---

## 1. Method — what was verified, and against what

Every status claim below was checked against a live artifact on 01-09-2026, not read off the
roadmap's own Part 0 table (which is dated *"as of the 06–12-07-2026 census re-measure"* and
carries a 13-07-2026 scoreboard paragraph). Three independent surfaces were compared:

| Surface | What it is | State on 01-09-2026 |
|---|---|---|
| Roadmap Part 0 prose | the human-authored register, 7 layers | last substantively touched 27-08-2026 (truth-pass); scoreboard paragraph still dated 13-07-2026 |
| [`stats_census_register.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/stats_census_register.csv) | the **machine-readable feed** the six live dashboard pages render from | **59 data rows, every one stamped `as_of_date` 2026-07-12/13/18 — never refreshed since Q1 began** |
| the artifacts themselves | reports, TSVs, `CITATION.cff`, `.zenodo.json`, SHADOW_ASSETS | current |

**The single most consequential finding of this pass is that those three disagree**, and the
public surface is the stale one. Detail in §3.

---

## 2. Q1 delivery, register by register

Q1's four workstreams (WS1.1 backup+dedup · WS1.2 close the descriptive rows · WS1.3
dashboard skeleton · WS1.4 FAIR release #1) cut across the seven registers. Below, each
register is stated as: **what Q1 owed it · what landed · what is still open**.

### L1 · Lexicon text (44 dictionaries)

**Owed:** the sense/polysemy and definition-typology rows; the editorial-fingerprint row is
Q2's, not Q1's.

**Landed.** Definition typology moved from ○ to ◐ and then *further* than the roadmap's own
Part II records: [`data/DEFINITION_TYPOLOGY_WS2_4_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md)
now covers **all 44 csl-orig dictionaries / 1,496,157 `<L>` records** (`--all`), superseding
the H1483 first pass over 15 core dicts / 926,759 records. Sense/polysemy stayed ◐ at 11/44
general lexica and is **genuinely capped**, not merely unfinished — 33 dictionaries carry no
structural sense markers and the `<L>` decimal-suffix shortcut was tried and confirmed
invalid. That is a measurement ceiling, and it belongs in the Q2 design as one.

**Open:** per-dict editorial fingerprint (Q2 WS2.2, prior art in §5); diachronic
first-attestation (Q2 WS2.1, ◐ at the A40 growth curve only).

**Correction owed to the roadmap (shipped this pass).** Roadmap Part II WS2.4 still quotes
the **superseded** first-pass numbers — *"15-dict distribution (926,759 records) + stratified
gold 63/79=79.7%"* — while Part 0 of the same file carries the current all-dict figures and a
gold of **55/79 = 69.6%**. Both are correct for their wave; only one is current. Accuracy fell
when scope widened from 15 core dicts to all 44, which is the expected direction and must not
be read as a regression in the classifier.

### L2 · Morphology & forms

**Owed:** paradigm-cell coverage (WS1.2).

**Landed.** Paradigm-cell coverage is ✅ in the roadmap — 8,054/11,096 roots, 171 distinct
finite cells, with a live page at
[`/paradigm-cell-coverage`](https://sanskrit-lexicon.github.io/csl-observatory/paradigm-cell-coverage)
(H817 + H1524). The kosha.db, DCS, Heritage and vidyut headline counts were all ✅ before Q1.

**Open:** form→lemma ambiguity rate — ○, no handoff ever minted for it. This is the one L2
row Q1 did not touch and Q2 does not claim either; it is named in §8 as an unowned residual
rather than quietly folded into a Q2 workstream.

**Blocked, not open.** The kosha.db counts this register publishes are the subject of
**CONTRADICTIONS §11** (manifest build vs live-build census, 496-row inflection gap plus a
whole-table presence disagreement) — still 🔴 unresolved and adjudicated **INCONCLUSIVE**
26-08-2026 because no kosha.db build exists on this box to measure. See §6.

### L3 · Corpus & usage

**Owed:** POS distribution per text (WS1.2).

**Landed.** POS-per-text is ✅ (270/270 texts, 5,688,416 tokens), page live at
[`/pos-by-text`](https://sanskrit-lexicon.github.io/csl-observatory/pos-by-text).

**Open:** lemma/root frequency bands *per text* (◐ — whole-corpus done at E26); meter/prosody
statistics (○, SanskritKaraoke-side); Vedic accent coverage (○, gated on
[ROADMAP_VEDAWEB_REUSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md)
Phase 2/6 landing first — an external dependency, not a scheduling choice).

**Ceiling to carry forward.** Unaccented DCS cannot split verb class I/VI or IV/passive, and
UD `Tense=Past` conflates aorist and perfect. The roadmap already names these under Risks;
the Q2 layer must cite them at the point of use, not once in a preamble.

### L4 · Translation

**Owed:** nothing specific in Q1; the register was already largely ✅.

**Landed.** No status change during Q1. The six ✅ rows (corpus_lexicon alignment, 3-layer
glossary, RU-gloss gap-list, mw_ru cards, per-dict RU coverage) stand as measured.

**Open:** coverage trajectory over time / translation velocity (○); QA-judge inter-rater
agreement κ (◐ — two-judge design exists, κ never reported). **κ is the higher-value of the
two** because it is the only rows in this register that would let a paper state a reliability
figure, and it is cheap: the judge outputs already exist.

**~~Blocked~~ — unblocked the same day.** The `corpus_lexicon` row count was
**CONTRADICTIONS §13** (1,093,391 vs 1,091,528). **Ruled 01-09-2026 by direct measurement:**
the canonical file is no longer an LFS pointer, hashes to the exact oid §13 had recorded, and
holds **1,093,391** records. The two figures are two *builds* — the 2026-06-26 recompute and
the post-H309 re-harvest of 08-07-2026 (+1,863 rows). L4 velocity and coverage-trajectory work
may proceed on 1,093,391, naming the build. See §6.

### L5 · Roots & etymology

**Owed:** nothing in Q1. All six rows were ✅ before the roadmap was written.

**Landed / open:** unchanged. The one caveat already carried — corpus root-class verdicts are
**capped** by accent collapse (B11) — is the same ceiling named under L3.

### L6 · Repo-meta & process

**Owed:** code-duplication census and LOC/language mix (WS1.2).

**Landed — and this is the register's own lesson.** Both rows turned out to be **already
done before the roadmap was authored** (H688, 11-07-2026, csl-observatory PR #85); the
register was simply stale, and they were re-registered as FEATURES_INDEX E43 under H817.
Two of the five rows Q1 targeted cost nothing to "deliver" because they had already shipped.
The same failure mode recurs in this pass (§3) and is the reason the Q2 entry conditions in
§4 lead with a feed refresh rather than with new measurement.

**Open:** publication-pipeline health as a **time series** (◐ — a dashboard exists, but it is
a snapshot, not a series).

### L7 · Product & funnel

**Owed:** nothing — Q1 deliberately scheduled this stream for Q3 and fenced it as separable.

**Landed:** nothing, as planned. The one ✅ row (ORS-FAQ Telegram export, H693) predates Q1.

**Open:** four of five rows — telegram-sanskrit-corpus grade stats (tooling ✅ / data 0, no
harvest has run), Systema LMS enrollment/funnel, samskrte.ru marketing funnel, course
engagement/retention. Three of the four are gated on host credentials, which is why the
roadmap keeps the stream separable. **That fence held through Q1 and should hold through Q2**
— L7 is not an analytical-layer input.

---

## 3. Q1 against its own four targets

The roadmap states four Q1 targets. Measured on 01-09-2026:

| Q1 target | Verdict | Evidence |
|---|---|---|
| 100 % of *descriptive* rows → ✅ | **MISSED, and the residue is mostly structural** | 9 rows still `not_started` and 8 `partial` in the machine feed; but 4 of the 9 are L7 (deliberately deferred) and 2 more are externally gated (Vedic accent on VedaWeb; meter/prosody on SanskritKaraoke). The genuinely-in-scope descriptive misses are **form→lemma ambiguity (L2)** and **translation velocity + κ (L4)**. |
| ≥1 single-copy giant backed up | **✅ MET, and exceeded** | `corpus_lexicon.jsonl` (290 MB, not rebuildable) is now **three-copy**: git-tracked twin in `pwg-ru-data` (H3316), a `D:\Backups` mirror (H1998), and a digest-verified **off-machine** copy at `samskrtam.ru/guhya` ([H3389](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3389-OxAlpha_Uprava_kosha-guhya-restricted-backup-upload_23.08.26.md), restore-rehearsed 43 s, sha256 triple-match). Recorded in [SHADOW_ASSETS_POINTERS.md](https://github.com/gasyoun/Uprava/blob/main/SHADOW_ASSETS_POINTERS.md). **The roadmap's highest-listed risk is closed and the roadmap does not say so.** |
| ≥6 observatory stat-pages live | **✅ MET** | 36 pages in [`observatory/site/src/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site/src), of which the WS1.3 census family is 6 (`census-overview` + `census-l1`…`census-l5`) and three further dedicated stat pages landed under H1524 (`sense-polysemy`, `paradigm-cell-coverage`, `pos-by-text`). |
| FAIR release #1 metadata prepared, deposit `@DO` | **✅ metadata; ✗ deposit — and the stated rationale has since been overtaken by events** | See §3.1. |

### 3.1 The FAIR-release contradiction Q1 leaves behind

[`data/FAIR_RELEASE_1.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md)
still has all three Status boxes unchecked: the curated two-file Zenodo deposit was never
made. Its rationale section, *"Why a manual deposit, not a GitHub→Zenodo webhook"*, is
explicit that a whole-repo archive **"would sweep in content this repo does not have clear
rights to redistribute"**, and
[`DATA_LICENSE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DATA_LICENSE.md)
repeats it verbatim: *"A repo-wide Zenodo/GitHub archival integration is deliberately **not**
used here for that reason."*

**It is used.** The repository carries a committed
[`.zenodo.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/.zenodo.json)
(added under PR #920), and
[`CITATION.cff`](https://github.com/gasyoun/SanskritLexicography/blob/master/CITATION.cff)
records a concept DOI **10.5281/zenodo.21306715** with the note *"the Zenodo–GitHub
integration is live and mints on release publish"*. The repo has cut **143 `v1.14x` releases**.

This is a live disagreement between committed governance documents and committed
configuration, on a rights question, on a public surface — logged this pass as
[CONTRADICTIONS §17](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).
Per the standing
[rights-uncertainty policy](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md)
this is **not a stop** for Q2 work; it is a disclosure that must be recorded once and carried,
and it is not an agent's call to resolve, because the two positions are both deliberate
human-authored policy statements.

### 3.2 Three denominators, no count of record

The register is counted three different ways in three places, and none of them agrees:

| Source | Total | Breakdown |
|---|--:|---|
| Roadmap Part 0 scoreboard prose (13-07-2026) | ~48 | ~32 ✅ · ~6 ◐ · ~10 ○ |
| Roadmap Part IV KPI table (baseline 12-07-2026) | 48 | "~28 / 48 (~58 %)" |
| [`stats_census_register.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/stats_census_register.csv) — the feed that renders the public pages | **59** | **42 done · 8 partial · 9 not_started** |

The feed is the only machine-readable one and therefore the only one a KPI can be computed
against; it is also the one nobody has updated. **A KPI whose denominator is ambiguous by 11
rows cannot report a percentage**, which is why §4 makes reconciling this an entry condition
rather than a Q2 deliverable.

Per-layer, from the feed:

| Layer | done | partial | not_started | total |
|---|--:|--:|--:|--:|
| L1 Lexicon text | 7 | 2 | 2 | 11 |
| L2 Morphology | 8 | 1 | 1 | 10 |
| L3 Corpus | 9 | 2 | 2 | 13 |
| L4 Translation | 6 | 1 | 1 | 8 |
| L5 Roots | 6 | 0 | 0 | 6 |
| L6 Repo-meta | 5 | 1 | 0 | 6 |
| L7 Product | 1 | 1 | 3 | 5 |
| **Total** | **42** | **8** | **9** | **59** |

### 3.3 The feed understates delivery on at least three rows

Comparing the feed against the roadmap's own Part 0 and against the artifacts:

| Row | Feed says | Reality | Evidence |
|---|---|---|---|
| L1 Definition typology | `not_started` | **◐ partial** — rubric + all 44 dicts / 1,496,157 records + n=79 gold | [DEFINITION_TYPOLOGY_WS2_4_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md) |
| L2 Paradigm-cell coverage | `partial` | **✅ done** — 8,054/11,096 roots, 171 cells, page live | H817 / H1524; [`/paradigm-cell-coverage`](https://sanskrit-lexicon.github.io/csl-observatory/paradigm-cell-coverage) |
| L3 POS distribution per text | `partial` | **✅ done** — 270/270 texts | H817 / H1524; [`/pos-by-text`](https://sanskrit-lexicon.github.io/csl-observatory/pos-by-text) |

All three drift in the same direction — the public observatory publishes *less* progress than
was actually made. This is the exact recurrence of the L6 lesson in §2 (H688's census was
"re-done" because the register was stale), and it is why the first Q2 act is a feed refresh,
not a measurement.

---

## 4. Entry conditions for Q2 — what must be true before the analytical layer is built

Part I of the roadmap orders the year: *provenance and backup first, then finish the
descriptive rows, then the analytical layer*. Items 1 and 2 are the entry conditions, and
both are now nearly satisfied — but "nearly" has to be made precise, because the analytical
layer consumes the descriptive layer's numbers.

1. **Refresh the machine feed before anything renders from it.** Correct the three rows in
   §3.3, restamp `as_of_date`, and pick one denominator (the feed's 59) as the count of
   record so the Part IV KPI can be computed. Until this lands, every analytical page built
   on the feed inherits a scoreboard that is seven weeks stale and wrong in three places.
   *Cost: small, mechanical, csl-observatory-side.*
2. **The backup precondition is met** — record it. The roadmap still lists "Backup gap
   (highest)" as an open risk; `corpus_lexicon.jsonl` is three-copy with a rehearsed restore.
   Q2 does not inherit this risk.
3. **Do not treat the two remaining in-scope descriptive misses as Q2 blockers.**
   Form→lemma ambiguity (L2) and translation velocity + κ (L4) are genuinely unfinished
   Q1 work, but no Q2 workstream consumes them. They stay descriptive residuals (§8), not
   analytical-layer prerequisites — folding them into Q2 would be how a quarter's scope
   silently doubles.
4. **Accept that two register rows are capped, not pending.** Sense/polysemy at 11/44 dicts
   and corpus root-class at the accent ceiling will never reach ✅. The Part 0 contract of
   "drive every ○ and ◐ to ✅" is unachievable as written; the honest form is a **capped**
   status distinct from **partial**, so the KPI stops chasing an unreachable 100 %.

---

## 5. The Q2 analytical layer — designed against the named gaps

The roadmap's Q2 lists WS2.1–WS2.5. Each is restated below with **what already exists**
(checked, not assumed), **what the actual gap is**, and **what it must not claim**. The
ordering is by Part I's logic — the analytical layer's job is to answer the gaps Part I
names, not to invent metrics.

### WS2.1 — Diachronic lexicography (first-attestation, growth curve)

- **Exists:** the A40 growth curve; the 18-comparable-list census
  (1,055,081 → 1,206,384, +14.3 %) with its conventions pinned in
  [METHODS_HOW_WE_COUNT_A_TRADITION_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md) §2.5.
- **Gap:** per-headword first-attestation across the 44 dicts 1832–1976 — i.e. *which
  dictionary coins a headword*, which the growth curve aggregates away.
- **Must not claim:** a growth figure computed on the 26-snapshot grand total (1,721,983).
  §2.5 forbids it explicitly; only the 18 comparable lists are key-scheme-stable 2014↔2026.
- **Paper feed — re-pointed.** The roadmap's Q2 target says *"A40 → 5/5"*. On 29-07-2026 MG
  ruled **«A38 counts, drop A40 from the fifteen»** — A40 is out of the degree portfolio
  ([ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)). Taking A40 from
  4/5 to 5/5 remains executable and worth doing, but it no longer advances the fifteen, and
  the Q2 target should say so rather than implying a portfolio gain.

### WS2.2 — Editorial fingerprints (citation × markup × error, per dict)

**This is the workstream where the prior-art check changes the plan most.**
[csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) already holds a large part of it:

| Existing artifact | What it covers |
|---|---|
| [`data/L0/convention_fingerprint.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/convention_fingerprint.csv) | **35 dicts × 33 dimensions**, per-cell `value/source/confidence` |
| [`data/L0/fingerprint_summary.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/L0/fingerprint_summary.json) | 1,050 cells, 590 auto-filled, **460 unknown — fill fraction 0.562**; 3 dicts have no source (KNA, KOW, AMAR); dims 15 and 18 flagged constant |
| [`data/lexico/microstructure_profile.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/microstructure_profile.csv) | ~63 k rows of per-entry microstructure |
| `microstructure_fingerprint.json` · `period_signatures.json` · `data/pd/density_fingerprint.tsv` | aggregate markup/period/density profiles |

- **Gap — three things, not "build a fingerprint table":** (a) coverage from **35 → 44**
  dicts, and closing enough of the 460 unknown cells that a comparative claim is not
  half-imputed; (b) the **error-typology axis is not joined in at all** — the 52,498-event
  OBS-T corpus in [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory)
  covers 43 dicts and has never been joined to the convention fingerprint; (c) the citation
  axis cannot be taken from the `<ls>` graph without the qualifier in §6 below.
- **Must not claim:** a 44-row table when 3 dicts have no source at all and 43.8 % of cells
  are unknown. Publish the fill fraction beside the table or the comparison is not readable.

### WS2.3 — Citation-graph network statistics (centrality, co-citation, communities)

- **Exists:** the canonicalized 11-dict × 912-text graph
  ([`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv),
  `ls_citation_nodes.tsv`) and a topology test already built on it —
  [`citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json)
  (CANON-CORE, `scripts/build-citation-canon.mjs`).
- **Entry-blocked by [CONTRADICTIONS §14](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).**
  MW — the corpus's largest dictionary — resolves to **5 coarse placeholder nodes** in this
  graph, while PWG alone contributes **536,172 of the 828,505** resolved citations (64.7 %).
  Any centrality, co-citation or community statistic computed on the graph as it stands is
  measuring **resolver coverage as much as canon shape**, and CANON-CORE's *"none cited by
  all 11"* is already known to be partly mechanical for that reason. §14 is
  🔴 unresolved and was adjudicated **INCONCLUSIVE** 26-08-2026 because the discriminating
  probe has not been run.
- **The discriminating act is already named and is cheap relative to the workstream:**
  re-run with MW dropped (a 10-dict matrix) **or** feed MW from the citation-apparatus matrix
  where it is fully resolved (320,828 tagged citations). **WS2.3 should be sequenced after
  that probe, not before it** — this is the single highest-leverage re-ordering in the Q2
  plan, because every network statistic produced before the probe would have to be recomputed
  after it.
- **Must not claim:** any "the tradition cites X" statement without the resolver qualifier,
  in A50 §4 or anywhere else.

### WS2.4 — Definition typology

- **Exists — further than the roadmap says:** all 44 dicts / 1,496,157 records, rubric
  documented, n=79 stratified gold at **55/79 = 69.6 %**, classifier committed at
  [`data/definition_typology_classifier.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_classifier.py).
- **Gap:** the three named residuals — the Wilson `E.` peel, the sense-level split, and the
  **ATLAS 300×7 double-keyed review pool**. Only the last raises the precision figure to
  something a paper can cite; the current gold is explicitly *single-pass, not independent
  double-key*.
- **Must not claim:** 69.6 % as a publication-grade precision. It is a first-cut, and the
  report says so.

### WS2.5 — FAIR release #2 (analytical datasets, DOIs)

- **Blocked upstream by its own predecessor.** FAIR release #1's curated file-level deposit
  was never made (§3.1), and the rights rationale for choosing that form over a repo-level
  integration is now contradicted by the live integration. Minting DOIs for a *second* set of
  datasets while the first release's deposit and its rights posture are both unsettled would
  publish the inconsistency rather than resolve it.
- **Sequencing:** WS2.5 enters only after a human settles §17 — either the whole-repo
  integration is the intended posture (in which case `DATA_LICENSE.md` and `FAIR_RELEASE_1.md`
  are amended and the file-level deposit becomes redundant), or it is not (in which case the
  integration is disabled and the curated deposit proceeds). **An agent cannot choose between
  two deliberate human policy statements**, and this document does not.

### Revised Q2 targets

The roadmap's stated Q2 targets are *"A40 → 5/5 and A50 → 4/5 (assisted); ≥4 analytical
dashboard pages; FAIR release #2."* Measured against reality on 01-09-2026 — A08 is 4/5
(unchanged, awaiting a human sign-off), A50 is **3/5** (unchanged since the 12-07 baseline),
A40 is 4/5 but outside the fifteen — the honest restatement is:

| Target | Restated | Why |
|---|---|---|
| A40 → 5/5 | keep, but **not counted as portfolio progress** | dropped from the fifteen 29-07-2026 |
| A50 → 4/5 | keep — it is the live one | 3/5 today; WS2.3 is its direct feed, **after** the §14 probe |
| ≥4 analytical dashboard pages | keep, **conditional on the feed refresh** (§4.1) | pages render from a feed that is stale in three rows |
| FAIR release #2 | **hold** pending the §17 human decision | see WS2.5 |

---

## 6. Contradictions carried forward — what the analytical layer must not paper over

Four unreconcilable pairs were logged from the Q1 methods report, plus one opened by this
pass. Each is stated with its **current** status (three of the five have moved since they
were filed) and what it forbids.

| # | Pair | Status on 01-09-2026 | What Q2 must not do |
|---|---|---|---|
| **§10** | Union headwords **323,425** vs 323,426 | ✅ **RULED 26-08-2026** (H3538, Tier 1) — both true under different scopes; line 1 of `union_headwords.tsv` is a column header, so data rows = 323,425. **The headword count of record is 323,425.** | Do not cite kosha-side prose that still reads 323,426 as a headword count. The residual is a kosha `[integrity]` wording fix, not a re-measurement. |
| **§11** | kosha.db manifest build vs live-build census (496-row inflection gap; `heritage_anchor` present in one, absent in the other) | 🔴 **unresolved**; adjudicated **INCONCLUSIVE** 26-08-2026 — no kosha.db build exists on this box to measure | Do not publish an L2 morphology statistic that names "kosha.db" without naming *which build*. METHODS §2.8's rule ("a kosha.db count names its build") is currently impossible to follow, and an analytical layer that averages the two builds would erase the disagreement. Discriminating act: one dated `scripts/build_db.py` rebuild with per-table `COUNT(*)` published. |
| **§12** | Petersburg naive sum **285,799** vs 285,950 | ✅ **RULED 26-08-2026** (H3538, Tier 1) — both are exact naive sums of the same now-2026 lists at **two pipeline stages**; the 151-row gap is the union build's key collapse (PWG −28, PWK −35, SCH −88) | Cite 285,799 beside union/de-dup figures and 285,950 when counting raw export lines — and **name the stage either way**. The "+70.2 % inflation" headline is only readable with the stage named. |
| **§13** | `corpus_lexicon` rows **1,093,391** vs 1,091,528 | ✅ **RULED 01-09-2026, this pass, Tier 1 (measured)** — two *builds*, not a gap: 1,091,528 = the 2026-06-26 recompute, **1,093,391** = the post-H309 re-harvest of 08-07-2026, +1,863 rows over a 780-group population. The canonical file is no longer an LFS pointer; both local copies are byte-identical and hash to `sha256:9f3d852f…`, the exact oid §13 itself recorded, holding 1,093,391 records with 0 blank lines and a terminating newline (so no `wc -l` off-by-one) | Cite **1,093,391** and **name the build**. A pre-H309 analysis keeps 1,091,528 *provided it says so* — the L4 coverage findings were genuinely computed on the older build and now carry that stamp. L4 velocity work is unblocked. **And a caution:** §13 was filed as an *unexplained* gap while A42 — the witness filed as losing — documented the reconciliation in its own front-matter and claims table. Read the losing witness's provenance block before filing a pair as unreconcilable. |
| **§17** | Whole-repo Zenodo integration **live** vs `DATA_LICENSE.md` + `FAIR_RELEASE_1.md` saying it is *deliberately not used* | 🔴 **new, opened this pass** | Do not mint FAIR release #2 DOIs while the repository's rights posture is stated two ways in committed files. Human decision, not an agent ruling. |

**Update, same day: §13 is ruled.** It was settled a few hours after this document first
shipped, by the probe named in its own row — which is the point of naming the discriminating
act rather than logging a dispute. Of the five rows, **§11 is now the only one still 🔴 on
measurement grounds** (it needs one dated `kosha.db` rebuild), and §17 is 🔴 on a decision a
human owns. Three (§10, §12, §13) are ruled.

**Why this table is here rather than in a footnote.** Three of the five rows constrain a
specific Q2 workstream (§11 → WS2.2's morphology inputs, §13 → WS2.1/L4 trajectories,
§17 → WS2.5), and two of them (§10, §12) are *resolved* in a way that changes which figure a
Q2 page should print. Carrying them as prose in a preamble is how they get papered over.

---

## 7. What stays human

- **M01 chapter form** — new chapter vs a section of Ch. 2 for the methods report. An open
  `@DECIDE` since Q1; the WS4.1 internal report
  ([METHODS_HOW_WE_COUNT_A_TRADITION_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md))
  shipped 31-07-2026 and is the chapter's source text either way, so nothing is blocked by
  the decision staying open. A human should decide, and this pass does not touch it.
- **CONTRADICTIONS §17 — the rights posture.** Two deliberate, human-authored policy
  statements disagree. An agent may log the disagreement (done) but may not pick.

---

## 8. Residuals — named, owned, not folded into Q2

| Residual | Where it belongs | Cost |
|---|---|---|
| ~~Refresh `stats_census_register.csv`: 3 status corrections + restamp `as_of_date` + adopt 59 as the count of record~~ | ✅ **DONE 01-09-2026** — [csl-observatory#199](https://github.com/sanskrit-lexicon/csl-observatory/pull/199), released `v1.13.2`; register now 44 done · 7 partial · 8 not_started. `capped` recorded as prose, not a fourth status value | — |
| Form→lemma ambiguity rate (L2) — never had a handoff | descriptive residual, not Q2 | unscoped |
| Translation velocity + QA-judge κ (L4) | descriptive residual, not Q2; κ is the cheap half | small (κ), medium (velocity) |
| ~~Settle §13~~ | ✅ **DONE 01-09-2026** — ruled by direct measurement of the canonical file (1,093,391 records, sha256-matched to §13's own oid); two builds, not a gap. Losing witnesses in FINDINGS / RECIPES / the RU deep manual now carry their build stamp | — |
| **A42 leads with the superseded 1,091,528** in its abstract, title figure and §data table while its own front-matter and claims row 2 carry 1,093,391 | **human-gated** — which figure a paper leads with is authorial, not an agent's call; no urgency under the article-submit freeze to 2026-11-01 | small, but not ours |
| Settle §11 with one dated `kosha.db` rebuild + per-table `COUNT(*)` | unblocks L2 statistics and METHODS §2.8 | small, kosha-side |
| Sequence the §14 MW-resolver probe (10-dict re-run or apparatus-fed MW) **before** WS2.3 | Q2 WS2.3 precondition | medium |
| Add a **capped** status distinct from **partial** to the register | Q2 entry condition §4.4 | small |

## Related

- [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) — the subject
- [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.meta.md) — its metadoc
- [METHODS_HOW_WE_COUNT_A_TRADITION_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md) — WS4.1, the conventions every figure above names
- [CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) — §10–§14, §17
- [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) — what exists (44 dictionaries · 23 interfaces · 47 data assets)
- [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) — A08 / A40 / A50 / M01 readiness
- [Uprava/SHADOW_ASSETS_POINTERS.md](https://github.com/gasyoun/Uprava/blob/main/SHADOW_ASSETS_POINTERS.md) — the three-copy `corpus_lexicon` record

_Dr. Mārcis Gasūns_
