# Publication pipeline — deep manual (papers · Brill book · docs_site)

_Created: 11-07-2026 · Last updated: 18-07-2026_

The subsystem deep manual for the **publication layer** of this workspace: the
[papers/](https://github.com/gasyoun/SanskritLexicography/tree/master/papers)
directory (article drafts, referee memos, cover letters, evidence CSVs), the
[Digital_Sanskrit_Lexicography-BOOK/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK)
folder (the Brill/De Gruyter monograph M01), and
[docs_site/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site)
(the research-conventions static site). Third item of the deep-manual queue in
[PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
(handoff H608). Audience: a maintainer or agent session doing paper/book/site
work here. Orientation-level coverage of the same ground is in
[RESEARCHER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md);
the translation pipelines that *generate* much of the paper data have their
own deep manual
([RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md),
H606), and the headword analytics are H607's
([HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists)).

All counts and states below verified against the tree on **11-07-2026**.

---

## 1. The three assets at a glance

| Asset | What it is | Contents (as of 11-07-2026) |
|---|---|---|
| [papers/](https://github.com/gasyoun/SanskritLexicography/tree/master/papers) | Working directory for article manuscripts homed in *this* repo | 21 `.md` + 3 evidence `.csv` (A36) + `a31_origin_census.py` + the `a31/` and `sanskrit_in_numbers/` subdirectories, as of 18-07-2026 — drafts/memos for A30, A31, A33–A36, A40, A42, A43, A58 plus scoping notes |
| [Digital_Sanskrit_Lexicography-BOOK/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK) | Build folder for the single-authored monograph **M01**, *Digital Sanskrit Lexicography: The Dictionary as a Layered Evidence Graph* | [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md) · [BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md) · [RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md) · [LITERATURE_CROSSWALK.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md) · [CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/CHANGELOG.md) · [chapters/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK/chapters) (12 of ~14 chapters drafted as of 18-07-2026 — only the data chapters ch03/ch11 unwritten) |
| [docs_site/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site) | ZettelkastenWiki static-site builder publishing the pwg_ru research-conventions docs | [build_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/build_site.py) (103 lines) · [test_docs_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/test_docs_site.py) (4 tests) · [wiki/research/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site/wiki/research) (10 docs, copies — sync caveats in §5.1) |

One registry rules them all:
[Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)
(§6). Nothing in these directories is a publication *act* — submission,
DOI minting, and site deployment are human-gated (§5, §7).

---

## 2. The paper lifecycle — idea to submission

Every paper has a **stable, append-only ID** (`Axx`; monographs `Mxx`) in
[Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)
and a **readiness score n/5** (1 idea · 2 outline/skeleton · 3 full draft ·
4 revising/pre-submission · 5 ready-to-send/submitted). IDs are never reused
or renumbered; a new paper takes the registry's "Next free ID" marker value
and bumps the marker.

The lifecycle, and the global skill that drives each stage:

| Stage | Skill | Produces | Readiness |
|---|---|---|---|
| Register / any status change | [/articles-update](https://github.com/gasyoun/claude-config/blob/main/commands/articles-update.md) | registry row + dashboard regen | — |
| Scaffold | [/paper-scaffold](https://github.com/gasyoun/claude-config/blob/main/commands/paper-scaffold.md) | `papers/<Axx>_<slug>.md` skeleton: **Claim · Data inventory (result → committed artifact → status) · Outline · Comparanda · Venue candidates · Provenance** | → 2 |
| Draft advance | handoff sessions (e.g. H348 → A40, H353 → A42) | sections written atop committed data | 2 → 3 |
| Hostile referee pass | [/paper-referee](https://github.com/gasyoun/claude-config/blob/main/commands/paper-referee.md) | `<Axx>_review_*.md` memo + fixes via PR; every figure recomputed from committed sources | 3 → 4 |
| Author-voice pass | [/paper-author-pass](https://github.com/gasyoun/claude-config/blob/main/commands/paper-author-pass.md) | voice rewrite via PR + `SIGNOFF_<Axx>_author_pass.md` + GTD `@DO` read-and-sign row | 4 → proposed 5 |
| Venue shortlist / package | [/venue-scout](https://github.com/gasyoun/claude-config/blob/main/commands/venue-scout.md) · [/paper-submission-pack](https://github.com/gasyoun/claude-config/blob/main/commands/paper-submission-pack.md) | venue matrix; submission bundle | — |
| Submit | **human only** (MG) | the actual submission + venue `@DECIDE`/`@DO` closure in GTD | 5 |

Two discipline points that recur in past incidents:

- **Data-first scaffolding.** The papers that reached 5/5 here stand on
  committed artifacts; the scaffold's data-inventory table (each claimed
  result → the committed file that backs it, full blob URL) is written
  *before* prose. A row with no artifact is a flagged blocker, not a hidden
  one.
- **A readiness bump is proposed by the agent, ratified by a human.** The
  author-pass SIGNOFF file lists residual human calls; the paper is not 5/5
  until the read-and-sign row closes.

### 2.1 File conventions in papers/

A mature paper is a *cluster*, not a file. A36 — the only 5/5 resident — is
the worked example:

| File | Role |
|---|---|
| [A36_latin_obscena_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena_note.md) | the manuscript (774 lines), status line + venue in the header |
| [A36_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_review_fable5.md) | pre-submission referee memo (reviewer model + verdict recorded) |
| [A36_cover_letter.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_cover_letter.md) · [A36_cover_letter_de.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_cover_letter_de.md) | submission cover letters, EN + DE (the venue publishes in five languages) |
| [A36_latin_obscena.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena.csv) (2,105 rows) · [A36_corpus_screen.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_corpus_screen.csv) (44 rows) · [A36_blunt_german.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_blunt_german.csv) (401 rows) | committed evidence tables the manuscript's figures recompute from |

Sibling patterns: a **verification note** records that a headline figure
reproduces exactly
([A34_corpus_absent_verification.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_corpus_absent_verification.md));
a **review memo may live here for a manuscript homed elsewhere**
([A35_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A35_review_fable5.md)
reviews the A35 draft in
[csl-orig/v02/etymology_stats/PAPER_DRAFT.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/PAPER_DRAFT.md)).
Newer skeletons (A40, A42, A43) carry YAML frontmatter (`paper_id`, `title`,
`status`, `readiness`, `venue`, `author`, `data_source`); older notes (A33,
A34, A36) carry the same facts as a bold header line + status blockquote.
Both are accepted; don't churn one into the other.

### 2.2 Who lives here (registry snapshot, 11-07-2026)

Papers homed in this repo per
[Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md):

| ID | Readiness | Manuscript | Note |
|---|:--:|---|---|
| A36 | 5/5 | [papers/A36_latin_obscena_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena_note.md) | **ready to send** (Nodus, *Beiträge zur Geschichte der Sprachwissenschaft*) |
| A33 | 4/5 | [papers/A33_sense_ordering_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md) | venue `@DECIDE` pending |
| A34 | 4/5 | [papers/A34_renou_register_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_renou_register_note.md) | venue `@DECIDE` + byline pending |
| A40 | 4/5 | [papers/A40_headword_inventory_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md) | data from [HeadwordLists/NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) (H607 territory) |
| A42 | 3/5 | [papers/A42_corpus_lexicon_resource.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A42_corpus_lexicon_resource.md) | data from `RussianTranslation/src/` (H606 territory) |
| A43 | 2/5 | [papers/A43_ru_dict_family.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A43_ru_dict_family.md) | figures recompute from local (uncommitted, rights-gated) JSONL |
| A30 · A31 | 3/5 · 3/5 | **full drafts merged 17-07-2026**: [papers/A30_skd_vcp_microstructure_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_skd_vcp_microstructure_note.md) (PR #503) · [papers/A31_fifty_thousand_corrections_error_origin_typology.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A31_fifty_thousand_corrections_error_origin_typology.md) + `papers/a31/` evidence + `a31_origin_census.py` (PR #506) | the ROADMAP's P4 · P5 (§3) |
| A32 | 1 | *not yet scaffolded here* | the ROADMAP's P6 (§3) |
| A58 | 3/5 | [papers/A58_semdom_amarakosha_crosswalk_paper.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A58_semdom_amarakosha_crosswalk_paper.md) | semdom × Amarakosha crosswalk (homed here) |
| A49 · A51 · A52 | 2/5 each | in [RussianTranslation/pwg_ru/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru) and [RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) | pwg_ru-pipeline papers — manuscripts live with their data, not in papers/ |
| M01 | 3/5 | the BOOK folder (§4) | the monograph itself |

**Homing rule** (from
[/paper-scaffold](https://github.com/gasyoun/claude-config/blob/main/commands/paper-scaffold.md)):
cross-dictionary metadata and non-Cologne dictionary studies → this repo's
`papers/`; repo-specific findings → that repo's own `papers/` or
`docs/articles/` convention (A16 lives in MWS, A01–A10 in csl-atlas, A12 in
csl-observatory). The pwg_ru papers keep their manuscripts next to their
pipeline data in `RussianTranslation/` — don't relocate them into `papers/`.

---

## 3. The P-number trap — always map through A-IDs

Three different documents use "P1–P6" for **different things**:

- [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
  Part III's paper table (P1 block economy · P2 sense inheritance · P3
  citation registers · P4 indigenous microstructure · P5 50k corrections ·
  P6 learner layer);
- csl-atlas's own `PUBLICATIONS.md` P-numbering (different assignment);
- the ROADMAP's 10-chapter book sketch (superseded by BOOK_PLAN's
  15-article → 14-chapter architecture).

The registry mapping as of 11-07-2026: **P1 ≈ A16, P2 ≈ A02, P3 ≈ A08,
P4 = A30 (with csl-atlas A04 adjacent), P5 = A31 (with csl-observatory A12
adjacent), P6 = A32.** [BOOK_PLAN.md §9](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
names this drift a standing risk: **cite papers and chapters by A-ID only**;
treat any P-number as a local alias that must be resolved before use. The
ROADMAP book sketch ("Ch.3 ← P1 …") is historical — the authoritative chapter
map is BOOK_PLAN §2/§3.

---

## 4. The book (M01) — how a paper becomes a chapter

### 4.1 Document map

| Document | Role | Key locked decisions |
|---|---|---|
| [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md) | the build plan: thesis, the 15-article → **14-chapter** architecture (5 parts), data→figure map, critical path | the 15 source articles approved (MG, 06-07-2026); **Ch. 7 folded into Ch. 6** — "senses: inheritance and order", A02+A33 (MG ruling 10-07-2026, 15→14 chapters); series = **De Gruyter *Lexicographica. Series Maior*** primary, Brill's Indological Library fallback; **standard subscription, not OA**; A12 confirmed sole-authored (08-07-2026) |
| [BRILL_PROPOSAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BRILL_PROPOSAL.md) | draft proposal to the Brill guideline checklist (ToC + per-chapter summaries, comparables, counts, rights disclosure) | remaining `[VERIFY]` items are the author's: final title, submission date, editors-in-post check, word count at manuscript stage |
| [RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md) | chapter → article → venue → publisher → copyright matrix | all 15 sources unpublished ⇒ copyright 100% author-held today; **no chapter rights-blocked** |
| [LITERATURE_CROSSWALK.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md) | the 37-work manuals library read against the plan (grounding map, gap analysis, positioning) | no cuts; mandatory reframes on the pre-merge Ch. 2/3/12/13/14 (BOOK_PLAN §11 wording — the crosswalk's own §0 says "2, 3, 7, 14"; the two lists never got reconciled, resolve against BOOK_PLAN §11 + the renumbered §3); the Ch. 7 keep-vs-merge fork it parked was **ruled 10-07-2026** (merged into Ch. 6); top referee risk = corpus-absence induction |
| [CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/CHANGELOG.md) | folder-local changelog | every book-folder change logs here under `[Unreleased]`, *in addition to* the repo-root [changelog.md](https://github.com/gasyoun/SanskritLexicography/blob/master/changelog.md) |
| [chapters/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK/chapters) | converted book-form chapters | 12 of ~14 exist as of 18-07-2026 (H430 samples 09-07 + the H846–H866 conversion wave 13-07; ch02 also gained §6 'The corpus as a bounded witness', H1078/PR #505). Remaining writing = the data chapters ch03/ch11 + Introduction/glue (A61 ruling: Introduction-argument, never a chapter) |

The book is a **gluing job, not a drafting job**: the 15 approved articles
map onto 14 chapters (13 one-to-one; Ch. 6 merges A02+A33), ~13 of the 15
already exist as article drafts at 4–5/5; the new writing is the
Introduction, five part-bridges, the Conclusion, and a method appendix
(BOOK_PLAN §3/§4).

### 4.2 Article → chapter conversion procedure (the H430 recipe)

Both existing chapters were converted with the same steps — follow them for
the next one:

1. Start from the article draft at its home repo (per the A-ID row in
   [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)).
2. Strip journal front/back matter (submission header, abstract, venue line,
   article-style acknowledgements).
3. Unify voice to first-person singular; re-anchor framing to the
   evidence-graph thesis and to Ch. 2's measurement framework.
4. Remap companion-*paper* pointers to sibling-*chapter* pointers.
5. Upgrade every repo link to a full `blob` URL pinned to the source's real
   branch (MWS material lives on `docs-pass`, not `master` — check before
   linking).
6. **Change no table, figure, or measured number.** Conversion is packaging;
   substance changes go through the article's own referee/author passes.
7. Log the conversion in the folder
   [CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/CHANGELOG.md).

Housekeeping trap: the book folder's **own**
[.gitignore](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/.gitignore)
ignores everything (`*`) and tracks chapters only via an allowlist line
(`!chapters/*.md`) — a new non-`.md` chapter asset needs its own allowlist
entry or it will be silently ignored. (The repo-root `.gitignore` has no
chapters rule.)

Anti-salami constraint (BOOK_PLAN §9): A02↔A33 is now *inside* Ch. 6 (the
10-07-2026 merge ruling retired it as a cross-chapter risk); the pairs still
standing are Ch. 7/8 (A04↔A35), Ch. 9 (A05↔A03/A07), and Ch. 10/11
(A08↔A50) — inside the book they must *cross-reference*, not re-derive each
other. The same discipline holds at article level (A51 vs A52; A42 vs A41 —
each carries an explicit anti-salami scope block).

### 4.3 What the rights table gates

The one standing rule
([RIGHTS_TABLE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/RIGHTS_TABLE.md)):

> When any of the 15 articles is **accepted** at a journal, before its
> chapter ships: read that venue's CTA, confirm the
> author-self-reuse-in-monograph clause, and record the exact clause + date
> in the table row.

CC-BY venues (Lexikos/eLex, LREC-COLING, JOHD) trigger nothing; the OUP
cluster (IJL/DSH) and Nodus need the two-minute CTA read at acceptance; a De
Gruyter acceptance is in-house with the book's own primary publisher. Because
publication and the book run in parallel, this is a rolling check — an
article publishing *after* the book never triggers it.

### 4.4 Critical path (state as of 11-07-2026)

From [BOOK_PLAN.md §9](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md),
updated against the registry:

1. **FAIR/DOI sprint — still the top blocker, but narrower than first
   recorded.** `CITATION.cff` now EXISTS in this repo (H817 FAIR-release prep,
   13-07-2026, PR #442) and in kosha — the missing-cff list is stale.
   ⚠️ **Unresolved cross-document conflict on the Ch. 14 DOI**
   (`10.5281/zenodo.15834721`): BOOK_PLAN (and earlier revisions of this
   manual) call it a false DOI resolving to an unrelated preprint, while
   [data/FAIR_RELEASE_1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md)
   (H817) records the same DOI as csl-observatory's genuinely minted OBS-T
   dataset DOI — one of the two is wrong, needs an online check before any
   re-mint (logged in CONTRADICTIONS.md, 18-07-2026). *Partial progress:* the
   DCS denominator's Hellwig CC-BY sign-off was obtained by email 09-07-2026
   (A38 row), so its remaining gate is the Zenodo mint itself (MG `@DO`).
2. **Rights table** — built (§4.3); only the rolling at-acceptance check
   remains.
3. **≥1–2 chapters "under review" at proposal time** — pending: nothing is
   submitted yet; A36 is the nearest (5/5, ready to send).
4. **κ / second annotator** for the `reviewed` evidence grade — open; the
   A44 IRR study (κ=0.336 five-way, 10-07-2026) is the nearest methodology
   precedent.

Open `@DECIDE` items for a human: Book B (handbook) home/timing; the
автореферат question (BOOK_PLAN §10). ~~The standalone corpus-methods-chapter
fork~~ — **closed 13-07-2026 (MG) as a marked section inside Ch. 2**, written
17-07 as ch02 §6 (H1078); both H505 forks are now shut.

---

## 5. docs_site — the research-conventions site

### 5.1 What it is

A ZettelkastenWiki site (pilot #2 of the Wave-3 consolidation angle) that
publishes the ten pwg_ru editorial-convention and metrics docs as one
navigable site (nav + search + SEO + cross-links), targeting
`https://gasyoun.github.io/SanskritLexicography/research`. Configuration
lives entirely in
[build_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/build_site.py):
the 10-doc list, `title_from_h1`, and a `source_filter` that rewrites
repo-relative Markdown links.

**Source of truth is
[RussianTranslation/research/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/research)** —
the files under
[docs_site/wiki/research/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site/wiki/research)
are copies. Edit the originals, then re-copy:

```
python docs_site/build_site.py --sync
```

Editing a wiki copy directly is a defect — the next `--sync` overwrites it.
Two sync caveats measured 11-07-2026:

- **The copies drift between syncs.** (Historical example, since fixed: two of the ten were stale at
  verification time: the source `README.md` gained a "Living monitors"
  section and `sense_order_metrics.md` a 2026-07-03 reproducibility note
  that the wiki copies lack. Run `--sync` (and re-commit) before any deploy.
- **`merge_BU.md` has no committed source at all** — the root `.gitignore`
  ignores `RussianTranslation/research/merge_*.md`, and `sync()` silently
  skips missing sources, so the wiki copy is the *only* committed version of
  that doc. For this one file the copy IS the original; `--sync` neither
  refreshes nor overwrites it.

### 5.2 Build and test (both verified 11-07-2026)

```
python docs_site/build_site.py [out_dir]      # default out: docs_site/_site
python -m pytest docs_site/test_docs_site.py  # 4 tests
```

- Requires `zettelkastenwiki`, pinned in
  [requirements.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/requirements.txt)
  to a git commit of
  [gasyoun/ZettelkastenWiki](https://github.com/gasyoun/ZettelkastenWiki)
  (v0.6.0 installed locally at verification time).
- The test module opens with `pytest.importorskip("zettelkastenwiki")` — on a
  machine without the package the 4 tests **silently skip**. In CI they DO run:
  since 11-07-2026 (H733, PR #357) the `docs-site` job in
  [ci.yml](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)
  installs `requirements.txt` (whose pinned `zettelkastenwiki` defuses the
  importorskip) and runs `pytest docs_site/test_docs_site.py -q` — a red
  docs-site job is a real site-build failure. Locally, install the pin first or
  the tests skip silently.
- Link-rewrite policy in `_rewrite_md_links`: a `[label](FILE.md)` link whose
  stem is one of the 10 site pages becomes an on-site `[[FILE|label]]` link;
  a link to any *other* repo doc is **deliberately reduced to plain text**
  (it would 404 on the static site). Do not "fix" the dropped links.

### 5.3 Publish state and procedure — NOT deployed (safety-cleared, awaiting ruling)

As of 11-07-2026 the research site is **built and tested but never
deployed**: the `gh-pages` branch (which GitHub Pages serves from its root)
has no `research/` directory.

> **Safety-check verdict (18-07-2026, H737-sibling H740, Fable 5
> `claude-fable-5`): GO — no blocker.** All five checks passed: the repo and
> all ten docs are already public on `master`; quoted third-party material is
> public-domain 19th-c. dictionaries plus a handful of short scholarly probes
> from Kochergina (citation-right scale); no personal data beyond scholars in
> scholarly context; no secrets; no gitignored bulk rides along in `_site`.
> One caveat for the ruling: the sense-order figures feed a paper in the
> pipeline — if its target venue enforces an anonymity period, a public
> authored site naming those results could conflict. **The deploy itself
> stays human-gated** — the decision row lives in
> [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md). What `gh-pages` *does* carry — the findings
dashboard, the epistemic-registries dashboard, the `md/` article site,
`progress/`, `roots/`, and the abbreviations dashboard — is deployed by
manual commits to that branch (`deploy: …` messages), plus a monthly
data-refresh workflow
([findings-dashboard.yml](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml),
3rd of each month) that commits regenerated dashboard *data* to `master` and
republishes.

To deploy the research site when a human green-lights it:

1. Run [/publish-safety-check](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md)
   first — mandatory before anything becomes public, even though these ten
   docs are already public in the repo (the check covers the *bundle*, not
   just the texts).
2. `python docs_site/build_site.py <out>` and run the pytest gate.
3. Copy `<out>` into a `gh-pages` worktree as `research/` (sibling of
   `findings/`, `episteme/`, `md/`), commit with a `deploy:` message, push.
4. Verify `https://gasyoun.github.io/SanskritLexicography/research/` serves,
   and log the deploy in the repo
   [changelog.md](https://github.com/gasyoun/SanskritLexicography/blob/master/changelog.md).

A manual-writing or documentation session **never** performs steps 3–4
(H608 hard constraint: document publishing actions, don't take them).

---

## 6. Where every artefact registers

Finishing any unit of publication work means updating the registries in the
**same pass** — this is the layer that makes the work findable next session:

| Event | Register where |
|---|---|
| Paper status/readiness change, new paper, new review memo | [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) row (via [/articles-update](https://github.com/gasyoun/claude-config/blob/main/commands/articles-update.md)) + dashboard regen (`python Uprava/tools/build_dashboard_data.py`) |
| Venue choice, byline confirmation, read-and-sign, DOI mint | [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) `@DECIDE`/`@DO` row |
| Book-folder change | folder [CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/CHANGELOG.md) `[Unreleased]` + repo [changelog.md](https://github.com/gasyoun/SanskritLexicography/blob/master/changelog.md) |
| Repo changelog edited | the [/cut-release](https://github.com/gasyoun/claude-config/blob/main/commands/cut-release.md) follow-through when a release is due (entries park under `[Unreleased]` until then) |
| Multi-session work spun off | `Uprava/handoffs/` H### file + registry row (mint via [/handoff-mint](https://github.com/gasyoun/claude-config/blob/main/commands/handoff-mint.md)) |
| Measured gotcha / derived dataset / reusable classification | the hub sweep — [/artifact-propagate](https://github.com/gasyoun/claude-config/blob/main/commands/artifact-propagate.md) or [/findings-append](https://github.com/gasyoun/claude-config/blob/main/commands/findings-append.md) |

---

## 7. Trap checklist (the ones that bite in this subsystem)

- **P-numbers are ambiguous** — map through A-IDs only (§3).
- **A-IDs are append-only** — never renumber, never reuse (§2).
- **The correction dataset's DOI is false** — `10.5281/zenodo.15834721` must
  be re-minted before anything cites it (§4.4).
- **No submission, DOI mint, Pages flip, or site deploy without a human** —
  and [/publish-safety-check](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md)
  before any publish action (§5.3).
- **docs_site wiki files are generated copies** — edit
  `RussianTranslation/research/`, then `--sync`; exception: `merge_BU.md`,
  whose only committed version is the wiki copy (§5.1).
- **CI runs the docs_site tests in the `docs-site` job** (since 11-07-2026), and they self-skip without the
  package — verify locally (§5.2).
- **Numbers in manuscripts are recomputed, never trusted** — the referee
  pass recomputes every figure from committed sources; a number with no
  committed source is a Major finding (§2).
- **Conversion changes no numbers** — article→chapter is packaging only
  (§4.2).
- **Anti-salami clusters** must cross-reference, not re-derive (§4.2).
- **Shared tree** — all of the above lands via isolated worktree + PR, never
  direct edits (workspace-wide rule, [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)).

---

## 8. Related manuals

- [MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md) — repo-wide conventions, CI, registries upkeep.
- [RESEARCHER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md) — the thesis, what's citable, orientation-level paper pipeline.
- [RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
  (H606, done 11-07-2026) — the mw_ru/pwg_ru pipelines whose data the
  A42/A43/A49/A51/A52 papers consume.
- H607 deep manual (HeadwordLists analytics) — shipped 11-07-2026 per
  [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md);
  will own the data-production side behind A40.

_Dr. Mārcis Gasūns_
