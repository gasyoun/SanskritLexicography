# A frequency-graded reading layer for Sanskrit learners: joining corpus, grammar, and seven dictionaries (A32 / P6)

_Created: 25-09-2026 · Last updated: 25-09-2026_

**Status:** skeleton, readiness **2/5** (was 1/5, idea) · registered as **A32** in
[Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) · roadmap paper
**P6** in [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
· book chapter 9 in
[PROPOSAL_SYNOPSIS_TEN_CHAPTER_PLAN_LSM_BRILL_23-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/PROPOSAL_SYNOPSIS_TEN_CHAPTER_PLAN_LSM_BRILL_23-09-2026.md)
· handoff [H5337](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5337-Fable_SanskritLexicography_a32-p6-reading-layer-paper-scaffold_23.09.26.md),
epic [E014](https://github.com/gasyoun/Uprava/blob/main/handoffs/epics/E014-SanskritLexicography_atlas-fairpubs-wave-1_23.09.26.md).
**Venue:** *Lexikos* (pedagogical-lexicography track) or eLex 2027; §8.
**What this file is:** the argument, the data join as method, the related-work map, and an
**explicitly empty** user-study section. No result in this skeleton is imagined: every number
below is copied from a committed artifact, linked at the point of use, and the section that
would carry the study's findings says so and stops.

**Precondition and its live state (25-09-2026).** This scaffold was allowed to start only
because the layer's specification exists on csl-atlas `main`:
[docs/LEARNER_LAYER_V1_SPEC.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEARNER_LAYER_V1_SPEC.md)
(H5317, [PR #511](https://github.com/sanskrit-lexicon/csl-atlas/pull/511) merged
24-09-2026). The v1 **dataset build** (H5318) exists as
[PR #521](https://github.com/sanskrit-lexicon/csl-atlas/pull/521), which was **still open**
when this file was written even though the handoff registry records it as merged; the v1
**public page** (H5319) is unstarted. The paper therefore stands, today, on a spec with
measured coverage and a built-but-unmerged payload — §2 says which is which, row by row.

## 1. Claim

**The one-sentence claim the paper will defend:** a reading layer that joins a corpus
frequency band, survival-ranked dictionary senses, Whitney's root and *gaṇa*, and an attested
paradigm around each Sanskrit headword can be built from existing open resources with a
single normalised key and no re-derived figure — and when it is built honestly, the
dominant card is **sparse**: measured over 52,934 lemmas, **no lemma carries all four
layers**, 67.7 % carry frequency and dictionaries only, and the design consequence is a card
with **named absences** rather than a full card with occasional gaps.

Two sub-claims carry the argument:

1. **Method (defended now, from committed data):** the four-way join is a *contract*, not a
   script — one key (normalised SLP1), one direction of transliteration (SLP1 → IAST, never
   back), three homonym rules, closed-vocabulary absence codes, fail-closed on an upstream
   digest mismatch. Its coverage per layer is a measured property of the resources, and the
   gaps it exposes are findings about Sanskrit lexicography, not defects of the build.
2. **Use (NOT defended yet — §6 is empty by design):** whether the layer helps a learner reach
   the right sense faster, and not less accurately, than plain Cologne lookup. The protocol
   that would decide this is pre-registered
   ([USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md));
   no participant has been approached. The paper's readiness cannot pass 3/5 until §6 has
   data, and the venue choice in §8 is conditional on the same.

**What would refute sub-claim 1:** a re-run of
[scripts/measure-learner-layer-coverage.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/measure-learner-layer-coverage.mjs)
on refreshed inputs that shows a non-trivial set of lemmas with all four layers (the "zero"
is a fact about the P2 panel being 28 nominals, not a law), or a demonstration that a second
key scheme reaches materially more of the VisualDCS paradigms than the SLP1 → IAST hop.

## 2. Data inventory — every intended result and the artifact behind it

Per the `/paper-scaffold` discipline: a row with no artifact is a flagged blocker, not a hidden
one. Status is as probed on 25-09-2026.

| # | Intended result | Committed artifact | Status |
|---|---|---|---|
| D1 | The card contract: four layers, personas, join key, homonym rules, absence vocabulary | [docs/LEARNER_LAYER_V1_SPEC.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/LEARNER_LAYER_V1_SPEC.md) §§1, 3, 5, 7, 9 | **exists** (merged PR #511) |
| D2 | Per-layer coverage over the 52,934-lemma index (band 53.9 %, nominal paradigm 31.1 %, verb paradigm 1.5 %, Whitney root 1.3 %, gaṇa 1.1 %, survival 0.053 %, homonym warning 0.6 %) | spec §8 + [scripts/measure-learner-layer-coverage.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/measure-learner-layer-coverage.mjs) | **exists** (measured 24-09-2026; not in CI — reads two sibling repos, re-run before quoting) |
| D3 | Completeness tiers A/B/C/D = 28 / 541 / 16,508 / 35,857 and the "zero lemmas carry all four layers" finding | spec §8, reproduced by the H5318 validator ("verb 778 = 778, all-four 0 = 0") | **exists in spec**; validator in [PR #521](https://github.com/sanskrit-lexicon/csl-atlas/pull/521) (**open**, not merged) |
| D4 | The joined payload itself (52,957 cards, tier + absence codes, VisualDCS `releaseId` recorded) | H5318 build, [PR #521](https://github.com/sanskrit-lexicon/csl-atlas/pull/521) | **built, unmerged** — the paper cites the merge sha once it lands; until then D4 is a claim about a branch |
| D5 | The v0 baseline the study's condition B currently is (band + routing, no senses; 52,934 records, generated 2026-06-13) | [src/tools/learner-reading-layer.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/learner-reading-layer.md) over [src/data/learner/learner-index.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/learner/learner-index.json) | **exists, live** |
| D6 | Frequency bands 0–5 as consumed (not computed): DCS-2021, 83,239 lemmas, CC BY | [VisualDCS/dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json); band 0 = "not attested in DCS", never "unused" | **exists** |
| D7 | Paradigm contract pin: envelope `vdcs-learner-v1-20260809`, commit `6d19eed1`, per-payload sha256; 31,753 nominal lemmas, 7,689 roots | [learner-contracts-v1-2026-08-09.envelope.json](https://github.com/gasyoun/VisualDCS/blob/main/visual/contracts/envelopes/learner-contracts-v1-2026-08-09.envelope.json) | **exists** |
| D8 | Root + gaṇa: 930 root rows / 855 distinct SLP1 strings; 741 class rows with `certainty` | [WhitneyRoots crosswalk/roots.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv), [root_class.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/root_class.csv) | **exists** |
| D9 | Survival-ranked senses: 28-lemma panel, 807 sense rows, Jaccard ≥ 0.15, sensitivity 0.10–0.25; the honest null (within-edge z = 1.80, p = 0.072) the card must not overstate | [data/lexico/r2_h2h3.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2h3.json), [r2_h2_senses.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2_senses.json), [build-r2-h2h3.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-h2h3.mjs) | **exists** (P2 / A02 material, cited not re-analysed) |
| D10 | Homonym warning inputs: 9,839 candidates, 400 shipped, 332 matched | [src/data/dicts/homonym-split.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/homonym-split.json) | **exists**; widening the 400 is a separate unit (spec §10) |
| D11 | Study design: within-subject, 2-group Latin square, n = 24 target, pilot 6, 360 eligible items, log time-to-correct-sense primary, non-inferiority margin on accuracy | [USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md) + [data/h5336_learner_study_power.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/h5336_learner_study_power.py) | **exists (protocol only)** |
| D12 | Study results: time ratio with CI, accuracy bound, ease | — | **does not exist** — §6 is empty; blockers are the protocol's §11 prerequisites (MW sense index, gold key, human-approved consent text) and recruitment, which is a human act |
| D13 | Literature matrix (pedagogical lexicography, vocabulary profiling, dictionary-use studies) | §7 of this file, seeded from repo holdings; full matrix via `/paper-search` | **stub** — bibliographic details marked *to verify* in §7 |

The gaps are the work plan, in order: D4 merge (agent, minutes once PR #521 is reviewed) →
D13 matrix (agent, one `/paper-search` session) → D12 prerequisites (agent for the sense index
and gold-key tooling; human for consent and recruitment) → D12 data (Q2 2027 per the
roadmap).

## 3. Argument — why this is a paper and not a build log

1. **The pedagogical-lexicography literature is built on languages with learner corpora and
   learners' dictionaries; Sanskrit has neither.** It has seven digitised nineteenth-century
   scholarly dictionaries with no frequency information, a lemmatised corpus (DCS) built for
   philology, and a nineteenth-century root list (Whitney) whose class assignments the corpus
   cannot always confirm. The question the paper asks is whether the *functions* of a learner's
   dictionary — Tarp's function theory, §7 — can be assembled as a **view over evidence that
   already exists**, instead of compiled as a new dictionary.
2. **The join is the method, and the join is a contract.** One key, one transliteration
   direction, three homonym rules, five absence codes, a pinned upstream release with
   fail-closed digests (spec §§5, 7, 9). This is what distinguishes the paper from a
   mash-up: every design rule is stated as a constraint that a reader can test against the
   artifact.
3. **Honest sparsity is the finding.** The spec measured that the "complete card" exists for
   no lemma (D3). The paper argues this is the general condition for any classical language
   where the evidence layers were built by different people for different purposes, and that
   the right design is a sparse card with *reasons* — `not-in-dcs`, `no-paradigm-contract`,
   `not-a-root`, `outside-survival-panel`, `homonym-payload-truncated` — because a "—" without
   a reason is a silent lie to the first-year student (persona 1).
4. **The evidence must survive into the UI without being inflated.** The survival ranking is a
   per-sense fact with an edge and a threshold; the population claim behind it is a reported
   null (D9). A card that says "senses with citations survive more" would be misreporting the
   paper it draws on. This is the paper's link to the programme's evidence-graded stance
   (roadmap Part II; A02).
5. **The layer's usefulness is an empirical question with a pre-registered answer slot** (D11,
   §6). The paper presents the design and the measured coverage as its contribution *now*, and
   the study as the test it has committed to in advance, with its refutation condition
   written down before any data.

## 4. The data join as method — section plan with sources

Each entry: intended content in one line, then the artifact it draws on. No prose beyond
that here.

### 4.1 Resources and what each was built for

DCS (philological lemmatisation; band 0 = uncorroborated, D6); Cologne dictionaries via the
atlas lemma-lookup and dossier (I1–I2 of the spec, `minDicts` 5 → 28,512 dossier lemmas);
Whitney roots and classes (D8); VisualDCS learner contracts (D7); the P2 survival panel (D9).
Source: spec §4 table.

### 4.2 The key and the direction of transliteration

Normalised SLP1 as the one key; `slp1ToIast()` from the repo's single normaliser; SLP1 → IAST
only, because the reverse is lossy over accent and anusvāra variants — measured: 31,753
VisualDCS lemmas collapse to 30,182 distinct IAST strings before the atlas is involved.
Source: spec §5.

### 4.3 Three homonym problems, three rules

Dictionary homonyms (one card, split warning from I11 — advisory and incomplete, 400 of
9,839 shipped); Whitney root homonyms (show all, never pick: 61 lemmas hit > 1 root row);
VisualDCS `lemmaId` collisions (resolve to highest-`tokens`, disclose alternatives: 1,351
lemmas). Gaṇa never inferred from the corpus (DCS cannot separate I/VI or IV/passive).
Source: spec §7.

### 4.4 Measured coverage and the completeness tiers

The §8 table and tiers A–D verbatim from the spec, with the re-run obligation stated (the
measurement script reads sibling repos and is outside CI). Headline: zero lemmas with all four
layers; all 28 survival lemmas are nominals or derived stems, none a Whitney root; 27 of 28
have a paradigm. ~32 % of cards gain at least one layer over v0; ~1 % become
grammar-complete. Source: spec §8, D2–D3; once PR #521 merges, the validator's counts replace
the working-tree figures.

### 4.5 Sparse-state design and failure behaviour

Closed absence vocabulary; digest mismatch fails the build; unknown `contractVersion` rejects;
a survival claim without edge + threshold is a defect; CSV download. Source: spec §9.

### 4.6 The five readers and what each constraint costs

First-year student, reading-course student, teacher/course author, lexicographer, integrator
— each row a hard constraint on the card (collapse by default; keep `src` on the collapsed
card; tier as a filterable field; provenance triple on every ranked sense; stable IDs with a
migration map). Source: spec §3. **Discrepancy to resolve before the draft:** the book
proposal's Ch. 9 names a *different* five (translator, researcher, student, practitioner,
hobbyist, from the DharmaMitra workshop intake). The paper must pick one set and say why; the
spec's set is the one the artifact was built against.

## 5. Related work in pedagogical lexicography — map, not review

What a referee at *Lexikos* or eLex will expect the paper to place itself against. Holdings
marked **held** are in this repo's [literature/md/](https://github.com/gasyoun/SanskritLexicography/tree/master/literature/md)
(grep-verified 25-09-2026); everything else is *to verify* via `/paper-search` before a
sentence is written about it.

1. **Learners' dictionaries as a genre and their history.** Cowie's history of English
   learners' dictionaries (cited ≥ 9× in the Bloomsbury Companion, **held**) — the genre the
   layer borrows functions from without inheriting its compiled form.
2. **Function theory.** Tarp (2008, 2011, 2012a — cited in the Bloomsbury Companion,
   **held**): a dictionary is defined by the user situations it serves; the layer's five
   personas (§4.6) are a function-theory design made explicit. This is the paper's main
   theoretical anchor and the one the argument in §3.1 rests on.
3. **Dictionary-use research.** Lew (2004, 2010, 2011; Nesi & Tan 2011 — all cited in the Bloomsbury Companion,
   **held**): what users actually do with entries, and how to measure it. The G7 protocol's
   task design (find-the-right-sense, timed, within-subject) should be positioned against this
   line, and §6 will report in its vocabulary. *To verify:* Lew & de Schryver on dictionary
   users in the digital revolution, for the "view over evidence, not a dictionary" framing.
4. **Frequency bands and vocabulary profiling.** Nation (2006) 1,000-word BNC lists and
   Nation & Anthony (2013) mid-frequency graded readers (Szudarski, *Corpus Linguistics for
   Vocabulary*, **held**): the banding tradition the DCS bands 0–5 stand in, and the source of
   the "is it worth learning yet" question. The paper must say explicitly that DCS bands are
   corpus-attestation bands over a philological corpus, not learner-need bands over a
   pedagogical one — the distinction persona 1 depends on.
5. **Corpora in language teaching.** Sinclair (ed.) *How to Use Corpora in Language
   Teaching* and Lu, *Corpus Linguistics and SLA* (**held**): for the routing benefit the
   current v0 layer offers (which dictionary to open), and for what a corpus-informed reading
   aid has been shown to do in other languages.
6. **Sanskrit pedagogy.** Gerow, *Primary Education in Sanskrit* (**held**; Amarakośa as the
   memorised lexicon, dictionary learning as automaticity) — the indigenous baseline against
   which a "reading layer" is a foreign object; Tubb (2007, **held**) on scholastic register.
   *To verify:* Ruppel (2017) and the Cambridge/Goldman textbook tradition for what a
   first-year reader is actually given as vocabulary support.
7. **Evidence-graded and survival-ranked senses.** The programme's own P2 (A02, csl-atlas
   R2) — the paper cites its null rather than re-testing it (§3.4).
8. **Comparable joined resources for classical languages.** *To verify:* Perseus/Logeion
   frequency-in-corpus displays for Greek and Latin as the nearest prior art for "corpus
   count beside the dictionary entry"; any Latin or Greek learner's frequency layer with a
   published user evaluation. If none exists with an evaluation, that absence is itself a
   sentence in the introduction.

Literature-matrix stub (title · method · relevance) to be filled by `/paper-search
"learner dictionary frequency band user study"` and `"pedagogical lexicography function
theory classical language"`; keep = Y rows pasted here.

## 6. User study — EMPTY BY DESIGN

**This section has no content and must not acquire any until the pre-registered study has
run.** What exists is the design, fixed before any data:
[USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md),
with the analysis plan pinned in code
([data/h5336_learner_study_power.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/h5336_learner_study_power.py),
`selftest` asserting the Latin-square necessity: 45.8 % false rejection without
counterbalance vs 3.1 % with).

What the section will contain, and only then:

1. The commit sha of the layer under test, frozen for the run, and which layer it was (the
   v0 routing layer, or v1 with senses — the protocol's §2 says the hypothesis wording changes
   with it).
2. H1 time ratio with its confidence interval; H2 accuracy bound against the −0.07
   non-inferiority margin (under-powered at n = 24, reported as a bound); H3 ease.
3. The pre-declared refutation: a CI on the time ratio including 1 at target n, or an
   accuracy loss beyond the margin — **either outcome is written up here**.
4. Aggregate-only reporting, ≥ 5 per published cell, no participant identifier anywhere
   (protocol §9, 152-ФЗ).

What blocks it (protocol §11, unchanged 25-09-2026): an MW sense index for the answer
options; a double-keyed gold sense key; a human-approved Russian consent text; the timing
instrument; and recruitment from the review-pool students, which is a human act
([H5311](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H5311-OxAlpha_csl-atlas_review-pool-recruitment-post-draft-ru_23.09.26.md)
draft ready, not sent). Roadmap date: Q2 2027.

## 7. Ablation / isolation plan (method paper — required)

What can be isolated **without users**, from the committed join alone, and what cannot.

| factor | held fixed | varied | metric | expected direction | committed artifact |
|---|---|---|---|---|---|
| key scheme | inputs, normaliser | SLP1 → IAST hop vs a second normaliser | paradigms reached (of 52,934) | the sanctioned hop reaches ≥ the alternative; the reverse direction loses accent/anusvāra variants | spec §5; [lookup-normalize.js](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/lib/lookup-normalize.js) |
| survival threshold | panel, edges | Jaccard 0.15 → 0.10–0.25 | ranked-sense set per lemma | ordering stable within the grid; report where it is not | [build-r2-h2h3.mjs](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-h2h3.mjs) sensitivity grid |
| homonym rule 3 | VisualDCS payload | highest-`tokens` vs first-seen `lemmaId` | cards whose stable ID changes | disclosure count = 1,351 either way; ID churn differs | spec §7.3 |
| homonym payload | rule | 400 shipped vs full 9,839 | warnings emitted | 332 → larger; advisory label stays | D10 |
| upstream pin | join | envelope `vdcs-learner-v1-20260809` vs a later release | build outcome | fail-closed on digest mismatch, never partial | D7, spec §9.2 |
| survival panel width | rules | 28 lemmas vs a widened panel | tier A count | rises from 28; "zero all-four" may flip — the refutation condition of §1 | D9; widening is a research unit, not a build step |
| **any layer's effect on a learner** | — | — | — | **cannot be isolated without §6** — no proxy is offered | D12 |

## 8. Venue candidates

One line each; a serious shortlist is `/venue-scout`'s job later.

1. ***Lexikos*** (AFRILEX, open access; pedagogical-lexicography and function-theory papers are
   home there) — fits the §3 argument; a design-plus-coverage paper without §6 is publishable
   there as a *design* paper, honestly labelled.
2. **eLex 2027** (electronic lexicography; data-join and interface papers) — fits §4; the
   conference format tolerates a "study pre-registered, not yet run" section less well than a
   journal does, so eLex is the choice only if §6 has data by the deadline.
3. **Fallback:** *International Journal of Lexicography* once §6 exists — the dictionary-use
   line (§5.3) publishes there.

## 9. Open questions a human should decide (not blockers for the draft)

1. **Persona set:** the spec's five (built against) or the proposal's five (DharmaMitra
   intake) — §4.6.
2. **Version naming:** the roadmap's "learner's layer v2" is the spec's "v1" (v0 = the June
   2026 routing page). The paper will use the spec's numbering; the roadmap line should be
   aligned or footnoted.
3. **Whether to submit a design paper without §6** (Lexikos) or hold for the study (eLex /
   IJL) — a venue decision that becomes real only after PR #521 merges and the literature
   matrix exists.

## 10. Provenance

Scaffolded 25-09-2026 by Fable 5.1 (`claude-fable-5-1`), handoff H5337, from: the learner
layer v1 spec (csl-atlas, merged PR #511), the G7 protocol (H5336), the H5318 build PR #521
(probed OPEN at 22:10 UTC despite the registry's "merged"), the roadmap P6 row, the book
proposal Ch. 9, and grep of this repo's literature holdings. No figure here was computed in
this pass; every number is a citation.

_Dr. Mārcis Gasūns_
