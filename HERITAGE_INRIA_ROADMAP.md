# Sanskrit Heritage (INRIA) reuse roadmap

_Created: 03-07-2026 · Last updated: 03-07-2026_

What of [sanskrit.inria.fr](https://sanskrit.inria.fr) (Gérard Huet's Sanskrit Heritage
Platform) we already reuse, and the staged plan for the rest. Rulings by MG 03-07-2026
(interview in-session); authored by Fable 5 (`claude-fable-5`). Companion to
[SAMSAADHANII_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/SAMSAADHANII_INDEX.md)
— Heritage is the second mature external computational-Sanskrit stack after SCL.

## 0. Access reality (verified 03-07-2026)

- **The INRIA site AND its GitLab are bot-walled.** [sanskrit.inria.fr](https://sanskrit.inria.fr)
  serves an Anubis anti-bot wall to programmatic clients
  ([FINDINGS §41](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)),
  and — new measurement — [gitlab.inria.fr/huet/Heritage_Resources](https://gitlab.inria.fr/huet/Heritage_Resources)
  is behind the same wall ([FINDINGS §47](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
  The **UoHyd mirror (v3.77)** is the reliable live endpoint for the *services*.
- **A GitHub mirror of the data exists:**
  [darkone23/Heritage_Resources](https://github.com/darkone23/Heritage_Resources)
  (default branch `develop-main`, last updated 03-2025). Contents verified via API:
  `BOOK/` (Heritage dictionary PDF), `DICO/` (hypertext Heritage dictionary, HTML),
  `MW/` (hypertext **Monier-Williams aligned with DICO** — Heritage-covered entries
  highlighted), `DATA/` (OCaml `.rem` persistent banks incl. `mw_index.rem`,
  `roots.rem`, `nouns.rem`, **plus plain-TSV frequency tables**: `pada_freq.tsv`,
  `pada_morph_freq.tsv`, `pada_trans_freq.tsv`, `comp_freq.tsv`, …), `CORPUS/`,
  `XML/` (legacy DTDs `SL_morph.dtd`/`WX_morph.dtd` + LGPLLR license texts).
- **The current morphology XML databanks are NOT in the repository** — per its README
  they are generated at Platform install time and downloadable from the site's
  linguistic-resources page, i.e. behind the wall → one manual browser download (human
  passes Anubis) or a local Platform install.
- **License: LGPLLR** (Lesser GPL for Linguistic Resources) — redistribution allowed
  with attribution and share-alike-style terms for the *resources*; composition with
  our CC BY-SA derived-data rule needs an explicit ruling (Phase 0 @DECIDE).

## 1. Already integrated — build on, don't redo

1. **Stem-list coverage study + VH↔SLP1 bridge** (26-06-2026):
   [HeadwordLists/Huet-INRIA-Wordlist-vs-Cologne.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Huet-INRIA-Wordlist-vs-Cologne.md)
   measured the reader's 21,562-lemma stem list (a **~2014-era export**) against CDSL
   (86.2 % covered, MW-dominated) and DCS (60.0 % attested). The validated
   Velthuis→IAST→SLP1 transcoder lives in
   [HeadwordLists/huet_coverage.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/huet_coverage.py)
   and already feeds
   [HeadwordLists/COVERAGE_ADDITIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/COVERAGE_ADDITIONS.md).
2. **Platform probe** (02-07-2026): §41 above — the "use the UoHyd mirror" ruling.
3. **DCS×Heritage alignment** (130,270 sentences, ground-truth segmentation) in
   [samsaadhanii/datasets](https://github.com/samsaadhanii/datasets) — license-blocked
   (no LICENSE; Kulkarni outreach drafted), pilot queued as **SCL pilot 2** in
   [GTD Agent-Ready](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
   That asset stays in the SCL track; this roadmap covers the Heritage-side originals.

## 2. Rulings (MG, 03-07-2026)

- **Scope:** all four asset families — morphology databanks, Heritage dictionary
  entries, segmenter-as-service, and the alignment (via SCL track).
- **Consumers:** all four — [kosha](https://github.com/gasyoun/kosha),
  [SanskritSpellCheck](https://github.com/drdhaval2785/SanskritSpellCheck),
  HeadwordLists here, [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) /
  [VisualDCS](https://github.com/gasyoun/VisualDCS).
- **Outreach to Gérard Huet: yes** — license clarification + current-export door-opener.
- **Priority: ahead of the four queued Samsaadhanii pilots.**

## 3. Phases

| # | Phase | What | Consumer | Gate |
|---|---|---|---|---|
| 0 | Acquisition + rights | Clone the GitHub mirror locally (gitignored, no vendoring yet); LGPLLR×BY-SA composition **@DECIDE**; manual browser download of the current morphology XML + current stem list **@DO**; `/outreach-draft` to Huet **@DO approve+send** | — | none — start now |
| 1 | Stem-list refresh | Current stems vs the 2014 snapshot (delta in the [NOW_VS_THEN](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) manner); rerun [huet_coverage.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/huet_coverage.py); extend [COVERAGE_ADDITIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/COVERAGE_ADDITIONS.md) | HeadwordLists | Phase 0 download (mirror's DICO index is a fallback source of current stems) |
| 2 | MW↔Heritage crosswalk | Parse `MW/*.html` coverage highlighting (+ `DATA/mw_index.rem` if decodable) → entry-level MW↔Heritage crosswalk TSV + coverage numbers | kosha, csl-atlas | mirror only — no gate |
| 3 | Frequency tables | Ingest the `DATA/*.tsv` pada/compound/transition frequencies; diff against VisualDCS M1–M8 and `corpus_lexicon`; register the feed in [PROJECT_INTERLINKS](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md) | VisualDCS, csl-atlas | mirror only — no gate |
| 4 | Morphology databanks | Current inflected-form XML banks → forms oracle for SanskritSpellCheck + third witness beside kosha's vidyut-built forms layer (426,410 pairs) — diff, never overwrite | SanskritSpellCheck, kosha | Phase 0 @DO download; @DECIDE for anything vendored |
| 5 | Heritage dictionary (DICO) | French gloss layer + entry structure as an additional witness/gloss source for kosha entries | kosha | @DECIDE ruling + Huet outreach reply |
| 6 | Segmenter as service | UoHyd-mirror segmenter/lemmatizer cross-validation vs DharmaMitra GPU morphology (csl-atlas #89/#92 lineage) and the RussianTranslation glossary adjudication set — polite: cache, throttle, identify | csl-atlas, RussianTranslation | none; live-service etiquette |

Phases 1–3 are pure-data, agent-doable now off the mirror; 4–5 are gated on the Phase-0
human items; 6 can run whenever a session needs the second morphology witness.

## 4. Execution

Phases 0–2 are bundled as handoff
[H099](https://github.com/gasyoun/Uprava/blob/main/handoffs/H099_heritage_inria_phase0_2.md):

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H099_heritage_inria_phase0_2.md and execute it.
```

Sonnet 5+ or Opus 4.8 chat, `cd` into `SanskritLexicography/`. Phases 3–6 mint their own
H### handoffs when their gates clear.

_Dr. Mārcis Gasūns_
