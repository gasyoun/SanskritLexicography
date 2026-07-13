# «Санскрит в цифрах» — a quantitative portrait of Sanskrit, after Duden's *Sprache in Zahlen*

## Roadmap 2026–2027 · public portrait + book/monograph appendix

_Created: 12-07-2026 · Last updated: 13-07-2026_

> **What this is.** A plan to build the Sanskrit analog of Duden's *Sprache in Zahlen* — the
> quantitative "language in numbers" appendix that closes the [Duden Universalwörterbuch](https://www.duden.de/)
> (the model PDF is filed at [`papers/Sprache in Zahlen.pdf`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/Sprache%20in%20Zahlen.pdf)).
> Where Duden portrays German from **one dictionary (≈140,000 headwords) + one corpus (the
> 5.2-billion-word Dudenkorpus)**, we portray Sanskrit from **the Petersburg dictionary family
> (Böhtlingk: PWG + PW + PWK + SCH) + the Digital Corpus of Sanskrit (DCS)**.
>
> **Audit-grounded, interview-ruled.** Phase-1 audit of this repo, the paper hub
> ([Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)), and the DCS
> assets ([gasyoun/VisualDCS](https://github.com/gasyoun/VisualDCS)) established what already
> exists; two interview rounds (12-07-2026) settled the six forks recorded in
> [§2 Decisions taken](#2-decisions-taken). This roadmap is executable — [§7](#7-wiring)
> wires wave 1 to a handoff and to GTD.

---

## 1. The model and the mapping

*Sprache in Zahlen* is not one statistic but a **ten-module portrait**. Sanskrit has a faithful
analog for every module — and, being an inflecting, compounding, accented classical language,
it has *richer* answers for several. Crucially, **most of the underlying measurement already
exists or is in flight** in this org, so this project is largely **assembly + presentation of the
new modules**, not measurement from zero.

| # | Duden module (*Sprache in Zahlen*) | Sanskrit analog | Basis | Status / owner |
|---|---|---|---|---|
| 1 | Lemma vs token (*Grundform/Wortform*) | lemma vs inflected *pada* | DCS | **exists** — [VisualDCS](https://github.com/gasyoun/VisualDCS) type/token split |
| 2 | Vocabulary size (*Umfang des Wortschatzes*) | headword inventory of the family; union ≠ naive sum | Petersburg family | **owned** — cite [A40](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md) census + [A55](https://github.com/gasyoun/kosha/blob/main/papers/A55_UNION_HEADWORDS_DATA_PAPER_JOHD.md) union index |
| 3 | Most frequent words (Zipf: 100 words ≈ ½ of text) | most frequent lemmas + coverage curve | DCS | **partial** — [dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json); build the coverage curve |
| 4 | Frequency by POS **and by genre** | by POS; Vedic vs Classical vs epic vs śāstra | DCS | **partial** — DCS text-genre metadata |
| 5 | Letter frequency (*e, n, i, r…*) | **akṣara / phoneme frequency** | family headwords + DCS | **NEW** |
| 6 | Longest words (*Bandwurmwörter*, 79 chars) | **longest compounds (samāsa)** — Sanskrit's signature | DCS corpus | **NEW** |
| 7 | POS distribution in the dictionary (nouns 72.8 %…) | grammar-category distribution | family `<gram>`/`<ab>` markup | **owned** — cite [A56](https://github.com/gasyoun/kosha/blob/main/papers/A56_ZALIZNYAK_GRAMMAR_INDEX_DATA_PAPER_JOHD.md) grammar-token index |
| 8 | Gender distribution (fem 46 / masc 34 / neut 20; multi-gender words) | m / f / n + multi-gender headwords | family gender markers | **NEW** |
| 9 | Compound formation (*Fugenzeichen* types) | **samāsa types + sandhi at the juncture** | DCS / vidyut segmentation | **NEW (hard)** |
| 10 | Verb classes (weak 76.7 / strong 17.2; *haben* vs *sein*) | **10 gaṇas + parasmaipada vs ātmanepada** | family + [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) | **NEW** |

**Why Sanskrit is a good subject for this genre.** Module 6 (compounds) and module 10 (verb
classes + voice) are far more striking in Sanskrit than in German: the *Bandwurmwort* record is a
curiosity in German but a defining feature of Sanskrit prose (Bāṇa, Subandhu). The
parasmaipada/ātmanepada split is a cleaner analog of *haben/sein* than German's own. And modules
5/9 expose the sandhi machine that has no German counterpart at all.

---

## 2. Decisions taken

Recorded verbatim from the 12-07-2026 interview (two rounds). These are the plan-of-record; a
future session does **not** re-litigate them.

| # | Fork | Ruling | Rationale |
|---|---|---|---|
| D1 | Primary deliverable | **Public «Санскрит в цифрах» portrait + appendix in the M01 monograph** (no standalone journal paper) | Mirrors Duden's own genre — the numbers live as an *appendix to a book*, not a paper. Two book homes: the popular Gasuns Sanskrit Manual (учебник) and the scholarly [M01 monograph](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md). |
| D2 | Reference-dictionary + corpus basis | **Petersburg family (PWG + PW + PWK + SCH) + DCS** | The Böhtlingk tradition is the philological gold standard (cf. [`papers/Stache-Weiske_Bö-MW.pdf`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/Stache-Weiske_B%C3%B6-MW.pdf)); the org owns deep PWG tooling ([`RussianTranslation/pwg_ru/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation)). DCS is the only large attested Sanskrit corpus. |
| D3 | Module scope vs sibling papers | **Full 10-module portrait, citing siblings** for the modules they own (2 → A40/A55, 7 → A56) | A complete portrait for the reader, zero salami-slicing. Scholarly novelty concentrates in the five NEW modules (5, 6, 8, 9, 10). |
| D4 | Primary language | **Russian primary; English + German after** | The samskrte.ru student audience is Tier 0; EN serves the monograph, DE closes the loop with the Duden/Böhtlingk German heritage. |
| D5 | Public portrait home | **samskrte.ru (web) + PDF booklet as an appendix to the Gasuns Sanskrit Manual** | Puts the portrait in front of the paying student audience and inside the учебник — the exact structural place *Sprache in Zahlen* holds in the Duden. |
| D6 | Which Böhtlingk exactly | **The whole Petersburg family (PWG + PW + PWK + SCH)** | Portrays the tradition as it actually layered (cf. [A49](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)); accepts the fuzzy-union caveat below in exchange for completeness. |

**Caveat forced by D2 + D6 (state it on the portrait's face).** Summing family headword counts
double-counts massively — PWK abridges PWG, PW abridges further, SCH is addenda. The honest
"vocabulary size" number is the **de-duplicated union**, which must be read from the pairwise
overlap matrix ([HEADWORD_OVERLAP_UNION15_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/HEADWORD_OVERLAP_UNION15_2026.md), A40 §4.5 / A55), **never** as
`PWG + PW + PWK + SCH`.

---

## 3. The data basis (the *Universalwörterbuch + Dudenkorpus* analog)

### 3.1 Reference dictionary — the Petersburg family

Counts from this repo's [`HeadwordLists/now-2026/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)
(key2 = closer-to-print; use key1 for de-dup joins):

| Dict | Full name | Headwords (key2, 2026) | Note |
|---|---|---|---|
| PWG | große Petersburger Wörterbuch (Böhtlingk-Roth, 1855–75) | **110,438** | the 7-volume "big" PW — the *Universalwörterbuch*-scale anchor |
| PWK | Böhtlingk, kürzere Fassung (1879–89) | **155,688** | the abridgement is *larger* by headword count (finer splitting) |
| SCH | Schmidt, *Nachträge* | **28,519** | addenda layer |
| PW / PD | kleineres PW | ≈ 104,941 (2014 export) | **prerequisite: needs a now-2026 re-export** — see [§8](#8-open-decisions--prerequisites) |

The de-duplicated union is **not** the sum; it comes from the A40/A55 overlap matrix.

### 3.2 Corpus — the Digital Corpus of Sanskrit (DCS)

From [gasyoun/VisualDCS](https://github.com/gasyoun/VisualDCS) (DCS-2026 release):

- **270 texts · 5,688,416 tokens · 754,726 sentences · 98,606 attested lemmas · 74-treebank**.
- Canonical consumer summary: [dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json) (83,239 lemmas with frequencies).

**Honest scale caveat (module 1 header material).** The Dudenkorpus is **5.2 billion** word
forms; DCS is **5.7 million** — roughly a thousandfold smaller. Sanskrit has no
billion-word reference corpus, and it never will have a *balanced contemporary* one because it is
a classical language. The portrait must say this plainly and treat DCS as *the attested classical
corpus*, not *the language*. Corpus-unattested ≠ non-existent (the A40 caveat): a headword absent
from DCS is unattested-in-our-corpus, not a ghost word.

---

## 4. Waves

Each wave states what unblocks it. Waves 0–1 are agent-doable now; waves 2–4 gate on human/rights
inputs.

### Wave 0 — Assemble the "already-owned" modules (agent-doable, now) — ✅ DONE 13-07-2026

*Unblocked by:* nothing — all inputs are committed.

- Pull modules **2** (vocab size → A40 census + A55 union), **7** (POS distribution → A56
  grammar-token index), **1** (lemma/token → VisualDCS), and a first cut of **3/4** (frequency →
  `dcs_lemma_summary.json`) into a single **`papers/sanskrit_in_numbers/` data table**, RU-labelled.
- Deliverable: [`papers/sanskrit_in_numbers/MODULES_OWNED.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/sanskrit_in_numbers/MODULES_OWNED.md) — one row per module, each citing its source artifact with n + date (the house trust-block discipline). Shipped under [H813](https://github.com/gasyoun/Uprava/blob/main/handoffs/H813-Sonnet_SanskritLexicography_sanskrit_in_numbers_wave1_new_modules_12.07.26.md) (Sonnet 5 `claude-sonnet-5`): Petersburg-family de-duplicated union 167,904 vs. naive sum 285,799 (+70.2% double-count inflation, the D2/D6 caveat now quantified); the new Zipf coverage curve shows DCS's top-100 lemmas cover 36.1% of the corpus (vs. Duden's ~50% for German).

### Wave 1 — Build the five NEW modules (agent-doable, now — **the core measurement**) — ✅ DONE 13-07-2026

*Unblocked by:* wave 0's basis lock; PWG/PWK/SCH markup already present in the org dict repos.

A committed dataset + one figure per module, computed reproducibly from the family markup + DCS.
Shipped under [H813](https://github.com/gasyoun/Uprava/blob/main/handoffs/H813-Sonnet_SanskritLexicography_sanskrit_in_numbers_wave1_new_modules_12.07.26.md) (Sonnet 5 `claude-sonnet-5`) — headline numbers + trust blocks in
[`papers/sanskrit_in_numbers/WAVE1_SUMMARY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/sanskrit_in_numbers/WAVE1_SUMMARY.md):

- **Module 5 — akṣara / phoneme frequency.** Phoneme histogram over family headwords (SLP1/key1)
  and over DCS tokens; report both *graphemic* (Devanagari akṣara) and *phonemic* counts, since
  sandhi makes them diverge — the Sanskrit-specific twist on Duden's letter chart. Shipped:
  family (285,950 headwords) + DCS corpus (5,688,416 tokens) histograms both computed; the two
  layers genuinely diverge (e.g. phonemic `a` at 21–24% vs. no single akṣara exceeding 5.5%).
- **Module 6 — longest compounds.** Longest samāsa in DCS (with a ≥5-occurrence honesty floor, as
  Duden does), plus the length distribution; the show-stopper module. Shipped: 39-char/16-akṣara
  record at the floor (*sāgaravaradharabuddhivikrīḍitābhijñasya*, n=5) vs. a 50-char hapax without
  the floor — demonstrating why the floor matters.
- **Module 8 — gender distribution.** m / f / n shares from family gender markers; the
  multi-gender headword set (the analog of Duden's *der/die/das Joghurt*). Shipped from the
  already-released A56 zaliznyak-grammar-index `lex` column (98,639 headwords): masc 54.6% / neut
  23.4% / fem 22.0% (of 64,488 gendered nouns); 482 multi-gender headwords.
- **Module 10 — verb classes + voice.** gaṇa (10-class) distribution and
  parasmaipada/ātmanepada/ubhayapada shares, from [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots)'
  own digitized Whitney (1885) classification (857 roots) + vidyut-prakriya-generated paradigms
  (419 roots corroborated) — not re-parsed from raw PWG prose, per the honest-method note in
  WAVE1_SUMMARY.md; the direct *haben/sein* analog. Shipped: gaṇa I dominates at 72.0%; pada split
  parasmaipada 61.1% / ātmanepada 20.5% / ubhayapada 18.4%.
- **Module 9 — samāsa types (best-effort).** Distribution of tatpuruṣa / bahuvrīhi / dvandva /
  … over a DCS-segmented sample (vidyut / DCS analyses); flagged best-effort because full
  compound typing needs segmentation, not markup. The *Fugenzeichen* analog: sandhi transformation
  at the juncture. Shipped: DCS's own UD-style `compound:coord` tag gives a reliable dvandva count
  (2,044 relations, 92.3% of tagged compound relations) — genuinely new, not heuristic; the
  tatpuruṣa/bahuvrīhi split is explicitly NOT auto-classified (would risk fabricated percentages)
  and is left as a flagged follow-up with a hand-typing sample included.

### Wave 2 — The RU portrait (gates on wave 1 + Manual home)
*Unblocked by:* all 10 module datasets; confirmation of the Manual repo/build (see §8).

- Assemble the 10 modules into the **«Санскрит в цифрах»** page: RU prose in the *Sprache in
  Zahlen* register (a question header per module, a chart, a trust block: source · n · date).
- Two renders from one source: an interactive **web page for samskrte.ru** and a **print PDF
  booklet** sized as an appendix to the Gasuns Sanskrit Manual.

### Wave 3 — EN + DE + monograph appendix (gates on wave 2)
*Unblocked by:* the frozen RU portrait.

- Translate to **EN** (monograph register) and **DE** (the Duden/Böhtlingk parallel).
- Fold the EN portrait into **M01** as the *Sanskrit in Numbers* appendix; wire it into the
  monograph's evidence-graded-lexicography spine.

### Wave 4 — Publish (gates on rights + design)
*Unblocked by:* [`/publish-safety-check`](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md) GO; a Zenodo dataset DOI.

- Design pass; per-figure trust blocks; Zenodo deposit of the module datasets ([`/data-release`](https://github.com/gasyoun/claude-config/blob/main/commands/data-release.md) + [`/cut-release`](https://github.com/gasyoun/claude-config/blob/main/commands/cut-release.md)); GO/NO-GO before samskrte.ru go-live.

---

## 5. Anti-salami boundary

This portrait **cites, never re-derives**, the modules siblings own:

- **Module 2 (vocabulary size, growth, corpus-grounding)** → [A40](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md) (12-year census) and the union index [A55](https://github.com/gasyoun/kosha/blob/main/papers/A55_UNION_HEADWORDS_DATA_PAPER_JOHD.md).
- **Module 7 (grammar-category distribution)** → [A56](https://github.com/gasyoun/kosha/blob/main/papers/A56_ZALIZNYAK_GRAMMAR_INDEX_DATA_PAPER_JOHD.md) (Zaliznyak-style grammar-token index).
- **The self-layering of the Petersburg family** (why PWK > PWG in count, etc.) → [A49](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) (operation typology of the Petersburg tradition).

The portrait's own contribution is the **five NEW modules (5, 6, 8, 9, 10)** and the **assembly**
of all ten into a single public-facing numeric portrait — the first of its kind for Sanskrit.

---

## 6. Non-goals

Considered and ruled out — a future session should not re-propose these without a new decision:

- **A standalone A60 journal paper.** Ruled out by D1: the scholarly home is the M01 appendix, the
  public home is the portrait. (If the new-module measurement turns out to carry a paper on its
  own, re-open — but not by default.)
- **MW as the basis.** Ruled out by D2 in favour of the Petersburg family.
- **Re-deriving vocab-size / POS / overlap from scratch.** Ruled out by D3 — cite A40/A55/A56.
- **Claiming DCS ≈ "the Sanskrit language."** Explicitly disavowed (§3.2 scale caveat).
- **A full dependency/treebank syntactic portrait.** Out of scope; the DCS treebank layer is a
  separate axis (VisualDCS), not part of a *words-in-numbers* portrait.

---

## 7. Wiring

- **Wave 0 + 1 → handoff** (agent-doable measurement): minted this session — see [§ handoff footer](#session-starter). Isolate in a worktree per this repo's shared-tree guard.
- **Human decisions/actions →** [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md): the Manual-home `@DECIDE` (§8) and the samskrte.ru publish `@DO`.
- **M01 →** note the planned *Sanskrit in Numbers* appendix under the monograph's entry in [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md).

---

## 8. Open decisions / prerequisites

1. **Gasuns Sanskrit Manual — repo + build path.** No dedicated repo was found in the org for the
   учебник that the PDF booklet appends to (D5). **`@DECIDE`:** name its repo/build (is it a
   Systema-Sanscriticum asset, an ORS-FAQ asset, or a separate LaTeX/book project?). Blocks
   wave 2's PDF render only — not wave 0/1.
2. **PW / PD now-2026 re-export.** The kleineres PW headword list exists only as a 2014 export
   ([`then-2014/PD-unique-key2-104941.txt`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014)). Re-run the extractor for a current count before the vocabulary-size table is frozen.
3. **samskrte.ru publish surface + rights.** samskrte.ru is Systema/LMS territory; confirm the
   publish surface and run [`/publish-safety-check`](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md) before go-live (wave 4).
4. **Module 9 depth.** Decide whether best-effort samāsa typing (segmentation-based) is enough for
   v1 or whether it waits for a dedicated pass. Recommendation: ship best-effort in v1, flagged.

---

## 9. Provenance

Roadmap authored 12-07-2026 by Opus 4.8 (`claude-opus-4-8`) via [`/roadmap-interview`](https://github.com/gasyoun/claude-config/blob/main/commands/roadmap-interview.md), from a Phase-1
audit of [gasyoun/SanskritLexicography](https://github.com/gasyoun/SanskritLexicography),
[Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md), and
[gasyoun/VisualDCS](https://github.com/gasyoun/VisualDCS), plus two interview rounds recorded in
[§2](#2-decisions-taken). Model tier + version stated per org convention.

_Dr. Mārcis Gasūns_
