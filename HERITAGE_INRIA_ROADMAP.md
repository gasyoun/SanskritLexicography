# Sanskrit Heritage (INRIA) reuse roadmap

_Created: 03-07-2026 · Last updated: 11-07-2026_

What of [sanskrit.inria.fr](https://sanskrit.inria.fr) (Gérard Huet's Sanskrit Heritage
Platform) we already reuse, and the staged plan for the rest. The Phase 5 DICO
gloss layer was delivered on 03-07-2026 (H106). Rulings by MG 03-07-2026
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
  **✅ RESOLVED 03-07-2026: Gérard Huet approved the LGPLLR × BY-SA composition**
  in reply to the [outreach email](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H121-Opus_SanskritLexicography_OUTREACH_2026-07-03_gerard_huet_heritage_03.07.26.md)
  (sent same day) — derived crosswalks/frequency joins embedding Heritage
  keys/anchors may ship alongside CC BY-SA Cologne-derived data. Exact wording of
  Huet's reply (attribution phrasing, any conditions) not transcribed into this
  repo yet — add verbatim when available. **Unblocks Phases 4–5 vendoring**, not
  just local/derived use.

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

| # | Phase | What | Consumer | Gate | Status |
|---|---|---|---|---|---|
| 0 | Acquisition + rights | Clone the GitHub mirror locally (gitignored, no vendoring yet); LGPLLR×BY-SA composition **@DECIDE**; manual browser download of the current morphology XML + current stem list **@DO**; `/outreach-draft` to Huet **@DO approve+send** | — | none — start now | ✅ **Done 03-07-2026** — mirror sparse-cloned (`DATA/ MW/ DICO/ XML/`, gitignored); inventory in [HERITAGE_MIRROR_INVENTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/HERITAGE_MIRROR_INVENTORY.md); Huet outreach drafted and parked ([H121-Opus_SanskritLexicography_OUTREACH_2026-07-03_gerard_huet_heritage_03.07.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H121-Opus_SanskritLexicography_OUTREACH_2026-07-03_gerard_huet_heritage_03.07.26.md), **not sent** — GTD @DO); @DECIDE + @DO rows confirmed live in GTD |
| 1 | Stem-list refresh | Current stems vs the 2014 snapshot (delta in the [NOW_VS_THEN](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) manner); rerun [huet_coverage.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/huet_coverage.py); extend [COVERAGE_ADDITIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/COVERAGE_ADDITIONS.md) | HeadwordLists | Phase 0 download (mirror's DICO index is a fallback source of current stems) | ✅ **Done 03-07-2026 (mirror-fallback path — the @DO manual download had not landed yet)** — 38,343 current stems extracted ([heritage_stem_extract.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_stem_extract.py)); delta in [Huet-INRIA-Wordlist-vs-Cologne.md §6](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Huet-INRIA-Wordlist-vs-Cologne.md#6-current-mirror-vs-the-2014-export-03-07-2026); 187 unvetted candidates parked in [COVERAGE_ADDITIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/COVERAGE_ADDITIONS.md#heritage-inria-current-mirror-candidates-03-07-2026-unvetted). Rerun against the human-downloaded export once it lands (@DO row in GTD). |
| 2 | MW↔Heritage crosswalk | Parse `MW/*.html` coverage highlighting (+ `DATA/mw_index.rem` if decodable) → entry-level MW↔Heritage crosswalk TSV + coverage numbers | kosha, csl-atlas | mirror only — no gate | ✅ **Done 03-07-2026** — [mw_heritage_crosswalk.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv) (185,803 MW entries, 25,140 Heritage-covered, 97.6% anchor-resolved); report in [mw_heritage_crosswalk.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.md); `DATA/mw_index.rem` (OCaml `Marshal` binary) not decoded — out of scope, see [HERITAGE_MIRROR_INVENTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/HERITAGE_MIRROR_INVENTORY.md) |
| 3 | Frequency tables | Ingest the `DATA/*.tsv` pada/compound/transition frequencies; diff against VisualDCS M1–M8 and `corpus_lexicon`; register the feed in [PROJECT_INTERLINKS](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md) | VisualDCS, csl-atlas | mirror only — no gate | ⬜ queued, own H### |
| 4 | Morphology databanks | Current inflected-form XML banks → forms oracle for SanskritSpellCheck + third witness beside kosha's vidyut-built forms layer (426,410 pairs) — diff, never overwrite | SanskritSpellCheck, kosha | ~~Phase 0 @DO download; @DECIDE for anything vendored~~ **both cleared 03-07-2026** | ✅ **Done 03-07-2026 (H105, Opus 4.8 `claude-opus-4-8`)** — oracle built: 1,022,526 Heritage forms vs 409,978 kosha forms; **94,264 overlap, 78.3% agree**; the small raw overlap is engine-surplus + anusvara/avagraha convention (18,636 recover under nasal-norm), and 66% of disagreements are root↔derived-stem lemmatization policy, not error (40-row hand-adjudication). Deliverables [heritage_forms_oracle.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle.md) + `.tsv.gz`/`.py`; [FINDINGS §52](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md). kosha-ingest of Heritage's 928k surplus forms is a **GTD @DECIDE**, not built. |
| 5 | Heritage dictionary (DICO) | French gloss layer + entry structure as an additional witness/gloss source for kosha entries | kosha | ~~@DECIDE ruling + Huet outreach reply~~ **both cleared 03-07-2026** | ✅ **Done 03-07-2026 (H106, Sonnet 5 `claude-sonnet-5`)** — [heritage_dico_gloss.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss.tsv): 24,549/24,549 crosswalk-resolved entries extracted (100 %), 99.98 % join kosha's `lemmas` (7.59 % of the 323,425-row table); 25-row hand-verified, zero truncation/bleed after fixing a 3-way anchor-role ambiguity (fresh headword vs. compound sub-entry vs. inline cross-reference — see [FINDINGS §54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)). Report: [heritage_dico_gloss.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss.md). kosha UI surfacing flagged as GTD @DECIDE, not built. |
| 6 | Segmenter as service | UoHyd-mirror segmenter/lemmatizer cross-validation vs DharmaMitra GPU morphology (csl-atlas #89/#92 lineage) and the RussianTranslation glossary adjudication set — polite: cache, throttle, identify | csl-atlas, RussianTranslation | none; live-service etiquette | ⬜ queued |

Phases 1–5 are done (1–3 off the mirror; 4 off the human-downloaded morphology
XML; 5 off the DICO mirror); 6 can run whenever a session needs the second
morphology witness.
Consumer follow-ons flagged by Phase 2 (kosha ingest of the crosswalk, csl-atlas witness
column) are **not built** — they mint their own H### handoffs per the roadmap's original
scope note.

## 4. Execution

Phases 0–2 executed 03-07-2026 (handoff
[H099](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H099-Sonnet_SanskritLexicography_heritage_inria_phase0_2_03.07.26.md),
Sonnet 5 `claude-sonnet-5`) — see the Status column above and
[FINDINGS.md §49](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
Phases 3–6 mint their own H### handoffs when their gates clear.

_Dr. Mārcis Gasūns_
