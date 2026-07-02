# FINDINGS — cross-repo empirical registry

_Created: 26-06-2026 · Last updated: 02-07-2026_

Non-obvious, **evidence-backed** facts about the Sanskrit-lexicon data, corpus, dictionary
structure, encoding, and per-dict tooling — the kind of thing that is expensive to re-discover
and easy to get wrong by assumption. Distinct from
[`PILOT_LESSONS.md`](https://github.com/gasyoun/github-spine/blob/main/PILOT_LESSONS.md)
(CI/CD process), [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)
(who-owns-what code), and
[`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
(**non-Sanskrit** infra / platform / process gotchas — network blocks, API throttling,
build traps, CodeQL-has-no-PHP; add those there, not here).

> **Living document — appended on a regular basis.** Every session that *measures* a
> non-obvious fact (a probe result, a count, a structural gotcha) adds it here, same pass as
> the work that found it. If you discovered it by running something, it belongs here.

**Schema per finding:** a `###` heading (short claim — the heading anchor is the finding's
stable link, listed in the index below), then the full **claim** in bold, `Evidence:` (the
measurement, with numbers / a file + line), `Implication:` (what to do or not do), and a
**Source** link to the exact statement and/or code, with a `— repo · date` tag. Keep them
grounded (a number, a file, a probe), never a hunch. When a finding is later refuted or
superseded, strike it and say why.

## Index

**Grammar & morphology data**

- [Whitney accent-mobility rules are machine-encodable](#whitney-accent-mobility-rules-are-machine-encodable) — the Zaliznyak a–f accent axis is an encoding task, not a missing source; VedaWeb 2.0 validates.
- [Homonym token-splitting has a hard morphological ceiling](#homonym-token-splitting-has-a-hard-morphological-ceiling) — only 5 of 38 DCS-lumped groups are gaṇa-splittable; the rest need gloss adjudication.
- [The Warnemyr scrape union-smears homonym classes](#the-warnemyr-scrape-union-smears-homonym-classes) — local Whitney class files merge homonyms' classes; derive from the live paradigm pages.
- [PWG nominal grammar compresses into 335 paradigm tokens](#pwg-nominal-grammar-compresses-into-335-paradigm-tokens) — 98,639 of 123,366 entries carry a Zaliznyak-style token.

**Corpus & parallel-text data**

- [The parallel corpus rarely attests prefixed-verb forms](#the-parallel-corpus-rarely-attests-prefixed-verb-forms) — sandhi-join lookups are a no-op; ~80 % of prefixed forms miss.
- [No printed frequency dictionary of Sanskrit exists](#no-printed-frequency-dictionary-of-sanskrit-exists) — DCS-frequency ordering is genuine innovation.
- [DCS lemma data is keyed in two transliterations](#dcs-lemma-data-is-keyed-in-two-transliterations) — SLP1 vs IAST across the two frequency files.
- [Unaccented DCS cannot distinguish present class I from VI](#unaccented-dcs-cannot-distinguish-present-class-i-from-vi) — 117 spurious corpus-derived class additions were reverted.
- [DCS OccId and sent_id are not unique keys](#dcs-occid-and-sent_id-are-not-unique-keys) — PK collisions silently dropped tokens and 449 sentences before synthetic keys.
- [DCS UD tense marking conflates aorist and perfect](#dcs-ud-tense-marking-conflates-aorist-and-perfect) — both surface as Tense=Past; recover via the 2021 export.
- [DCS 2021 and 2026 vintages are not directly comparable](#dcs-2021-and-2026-vintages-are-not-directly-comparable) — one metrical line ↔ several CoNLL-U sentences; treebanks on 74/270 texts only.
- [A fifth of DCS lemmas have no CDSL headword](#a-fifth-of-dcs-lemmas-have-no-cdsl-headword) — 81.4 % link; the rest need a lemmatization fallback.
- [Sa-Ru glossary token coverage plateaus at 86.6 percent](#sa-ru-glossary-token-coverage-plateaus-at-866-percent) — DCS + vidyut is the workhorse; the unresolved 41 % of forms is only 12.9 % of tokens.
- [Renou period-state tagging covers 770k entries in 8 dicts](#renou-period-state-tagging-covers-770k-entries-in-8-dicts) — multi-signal I–V states; homograph collapse gives closed-class words spuriously broad spans.

**Dictionary structure & markup**

- [PWG encodes secondary stems inline, not in div markup](#pwg-encodes-secondary-stems-inline-not-in-div-markup) — segment on the inline ab label, not div n="m".
- [Giant verb roots sit at non-zero homonym indexes](#giant-verb-roots-sit-at-non-zero-homonym-indexes) — iterate all homonym records, never bufs[0].
- [PWG orders senses genetically, not historically](#pwg-orders-senses-genetically-not-historically) — sense-1 is oldest only 73.5 % of the time; don't re-sort.
- [Vedic-citation density separates the dictionary traditions](#vedic-citation-density-separates-the-dictionary-traditions) — PWG ≈ MW ≫ AP90 ≫ Kochergina.
- [SKD and VCP carry essentially zero Western markup](#skd-and-vcp-carry-essentially-zero-western-markup) — marker detectors score 0 by construction.
- [The ls source map recognises 72.4 percent of PWG citations](#the-ls-source-map-recognises-724-percent-of-pwg-citations) — the unrecognised tail is late secondary literature.
- [PWG citation occurrences track distinct references](#pwg-citation-occurrences-track-distinct-references) — HTML-target works are not re-cited disproportionately.
- [MW has no sense-level div markup](#mw-has-no-sense-level-div-markup) — split on ¦ inside the record.
- [Apte is three dictionaries; keys differ stem vs nominative](#apte-is-three-dictionaries-keys-differ-stem-vs-nominative) — agni vs agniH; join on key1.
- [About 9 percent of typo corrections are collisions](#about-9-percent-of-typo-corrections-are-collisions) — the "right" form often already exists as its own entry.
- [A verified correction queue decays against live csl-orig](#a-verified-correction-queue-decays-against-live-csl-orig) — ~0.8 %/week; re-verify before filing.
- [Citation density is register-bound, not comparable raw](#citation-density-is-register-bound-not-comparable-raw) — PWG 4.63 vs MW 1.09 ls/entry; SKD's ~69k citations are iti-register.
- [Sense granularity is a family trait, not a diachronic trend](#sense-granularity-is-a-family-trait-not-a-diachronic-trend) — r = 0.036 over 135 years; control by school.
- [MW inherited the PWG apparatus skeleton, not its prose](#mw-inherited-the-pwg-apparatus-skeleton-not-its-prose) — 0.81 citation-order concordance; gloss length tracks PWG no more than an independent control.
- [PWG and MW share 94,753 headwords in the union index](#pwg-and-mw-share-94753-headwords-in-the-union-index) — consume HeadwordLists/union, don't rebuild.
- [Body-text headword mining is a dead end (38.6 percent precision)](#body-text-headword-mining-is-a-dead-end-386-percent-precision) — the 376k broad index is near-ceiling; measured negative result.
- [Detector precision stratifies by digitization quality](#detector-precision-stratifies-by-digitization-quality) — mature dicts ~0.2 % real flags vs 11–15 % on poorly-digitised ones.
- [Correction events concentrate in sense text](#correction-events-concentrate-in-sense-text) — 52.7 % sense / 17.5 % markup / 17.3 % headword over 52k events.

**Etymology & derivation**

- [Indigenous dictionaries agree on derivation; Wilson is the outlier](#indigenous-dictionaries-agree-on-derivation-wilson-is-the-outlier) — 90–100 % agreement vs Wilson 23–61 %.
- [The E abbreviation tag is polysemous across dicts](#the-e-abbreviation-tag-is-polysemous-across-dicts) — Etymology / Epithet / Epic; count the meaning, not the marker.
- [Root-recovery tiers err on root form, not identity](#root-recovery-tiers-err-on-root-form-not-identity) — normalize to dhātupāṭha citation form; gate LLM roots through a known-dhātu set.

**Encoding & normalization**

- [IAST Unicode collides and normalises lossily](#iast-unicode-collides-and-normalises-lossily) — NFD + strip-Mn destroys length and retroflexion.
- [BOM state is inconsistent across exports](#bom-state-is-inconsistent-across-exports) — check head -c 3; preserve on write.
- [Injected BOMs crash the hw record parser](#injected-boms-crash-the-hw-record-parser) — "init_entries Error 2" is an encoding symptom, not a structure defect.
- [devanagari_to_slp1 mis-routes retroflex la](#devanagari_to_slp1-mis-routes-retroflex-la) — ळ → x instead of L.
- [Gloss-language spelling drift tracks reform type, not age](#gloss-language-spelling-drift-tracks-reform-type-not-age) — legislated ≫ convention ≫ none; the metric saturates post-1890 for English.

---

## Grammar & morphology data

### Whitney accent-mobility rules are machine-encodable

**Whitney's Grammar already carries machine-encodable per-case ACCENT-MOBILITY rules — the
blocker to a Zaliznyak a–f accent axis is encoding, not a missing source.**
Evidence: the ingested `WhitneyRoots/src/whitney_sections.json` declension chapters (IV–V) hold
28 sections with concrete accent rules — §§315–317 ("the accent falls upon the ending in all the
weak cases": `nāvā́, vācí, vākṣú`), §318 (participles -ánt shift only in the *weakest*: `tudatā́`
vs `tudátsu`), §319 (accented-short-vowel polysyllables *retain*: `agnínā, agnáye`), plus per-class
§350/§372/§390/§423/§446 and §314 (vocative→first syllable). These are exactly Zaliznyak's a–f
schemes, conditioned on the lemma's accent POSITION — which PWG already supplies via the udātta `/`
in `key2` (`agni/`=agní, `se/nA`=sénā).
Implication: a full Vedic accent-mobility axis is an extraction task (hand-encode ~10 rules into a
(stem-class, accent-position)→case-accent table, join with `key2` `/`, validate vs accented RV),
NOT a data-acquisition blocker. Vedic-only (Classical entries have no `/`). Earlier claim that
"Whitney might supply it but our data can't" was an overstatement — both halves are on disk.
**Validation set = VedaWeb 2.0, PROBED + CONFIRMED 2026-06-29.** API live at
`vedaweb.uni-koeln.de/api` (FastAPI, OpenAPI at `/api/openapi.json`).
`POST /api/search {"type":"quick","q":"agni"}` → 3,840 hits; e.g. RV 6.59.3 highlight from the
**Casaretto et al. (2025) annotation resource** `66695e4a14f6d337f7788740` is the udātta-marked
word-split `… índrā; nú; agnī́; ávasā; ihá; vajríṇā; vayám; devā́` — accented per-word forms,
position-aligned, with lemmatization (`679b7da2…`) + accented text (`66695c4b…`, Scarlata–Widmer/
Lubotsky) at the same locations, and bulk `GET /api/resources/{id}/export`. So per lemma you can
collect attested inflected+accented forms, bucket by morphology, and validate a generated paradigm.
**CC BY 4.0**, in-ecosystem (C-SALT/CDSL). The accent axis is *unblocked and de-risked* — only the
Whitney-rule encoding + the join remain. (The legacy `/rigveda/api/search` is superseded by 2.0.)
**Source:** [`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)
§"Vedic accent mobility" + `WhitneyRoots/src/whitney_sections.json` §§315–319 — RussianTranslation · 2026-06-29

### Homonym token-splitting has a hard morphological ceiling

**Only 5 of 38 DCS-lumped root-homonym groups are gaṇa-splittable — the other 33 share a
present class, so no morphological tool can separate their tokens.**
Evidence: of the 38 homonym groups DCS lumps under one `lemma_id`, only `pat` (3,123 tokens:
class 1 "fall" vs 4 "rule"), `khād` (369), `dīv` (110), `luṭh` (26), `akṣ` (4) are gaṇa-distinct
— 3,632 tokens, 86 % of them in `pat`. Where DCS itself keeps separate verb `lemma_id`s,
gloss-mapping (DCS `meanings` ↔ Warnemyr gloss, gaṇa fallback, coverage ≥ 0.55) yields **26
reliable splits** (vid know 9,391 / find 1,923; as be 35,466 / throw 287; kṛ make 40,555 /
scatter 211 …), audited in `crosswalk/token_attribution.json`.
Implication: token-level homonym frequency beyond these 26+5 requires sense/gloss adjudication,
not Pāṇinian generation; vidyut-prakriya's right role is paradigm **display + form-validation**
(advisory, never edits the spine), NOT gaṇa attribution. Show "N (this sense) · M for the lemma".
**Source:** [WhitneyRoots `.ai_state.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/.ai_state.md)
§token-level disambiguation + `crosswalk/token_attribution.json` — WhitneyRoots · 2026-06-14

### The Warnemyr scrape union-smears homonym classes

**The local Whitney root-class files (HTTrack scrape of lexicon.warnemyr.com) merge homonyms'
present classes into one value — per-homonym class must come from the live paradigm pages.**
Evidence: `2 √as` "throw" shows class II locally but is IV (*ásyati*); all three `√kṛ` show VI
though "make" is VIII; `kḷp` (#114) shows `—`/`—` but is class I with PPP `kḷptá`. Phase 0
re-parsed the full local Warnemyr mirror (939 paradigm pages; 930 roots keyed) and derives
per-homonym class from the full paradigm + period tags (V/B/S/E/C), keyed by the `{sense → URL}`
map; Warnemyr's `ROMAN ?` uncertainty is kept in a separate `class_uncertain` field (35 roots),
never in the asserted class.
Implication: never read verb class from `Whitney_roots_class-PP.txt` / old `app_data.json`;
treat any single-valued class on a homonym root as suspect union-smear and re-derive.
**Source:** [WhitneyRoots `DESIGN.md` §5](https://github.com/gasyoun/WhitneyRoots/blob/main/DESIGN.md)
+ `.ai_state.md` §Phase 0 — WhitneyRoots · 2026-06-13

### PWG nominal grammar compresses into 335 paradigm tokens

**98,639 of PWG's 123,366 entries carry enough `<lex>` gender/POS signal to be indexed into
just 335 Zaliznyak-style paradigm tokens.**
Evidence: reverse index over all PWG entries → 98,639 indexed (24,727 cross-refs / bare forms
skipped), 335 distinct tokens of the form `G·T S F` (e.g. `m·1b` = masculine a-stem oxytone);
top tokens `m·1+2` 12,681, `m·1` 11,496, `mfn·1` 8,346. Flag rates: `+N` compound 47.3 %
(MW 44.5 %), `*` gradation 3.6 %, `°` deviation 0.04 %.
Implication: a compact per-word grammar token is feasible for the whole dictionary and is kept
as **structured data only** — a blind A/B (Opus judge, 8 stratified headwords: grammar-OFF 5 /
tie 2 / ON 1) showed injecting it does NOT improve DE→RU translation, so portraits stay untouched.
**Source:** [`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)
(+ `src/headword_index.tsv`, `src/reverse_paradigm_index.json`) — RussianTranslation · 2026-06-29

## Corpus & parallel-text data

### The parallel corpus rarely attests prefixed-verb forms

**The parallel corpus rarely attests prefixed-verb surface forms.**
Evidence: of √man's 15 prefixed forms, only **3** (`anuman`, `abhiman`, `avaman`) appear in
the SamudraManthanam parallel corpus; the `pwg_preverb1.txt` sandhi-join produces the *same*
surface strings as a naïve `upasarga+root` concat, so spelling is not the limiter — the
corpus simply lemmatises prefixed verbs to the root or lacks them.
Implication: prefix-specific Apresjan evidence is corpus-bound; for the ~80 % that miss,
defer to the dictionary's own (German) gloss. Do **not** build a sandhi-join lookup
expecting coverage gains — it's a no-op.
**Source:** code [`subcard_portrait()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py#L237)
· statement [FREQ_TEST_RUNBOOK.md § Apresjan evidence](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/FREQ_TEST_RUNBOOK.md). — SanskritLexicography/RussianTranslation · 2026-06-24

### No printed frequency dictionary of Sanskrit exists

**No printed frequency dictionary of Sanskrit exists.**
Evidence: absent from the prefaces and literature of PWG/PW/MW/GRA/AP90 and from Kochergina;
only Hellwig's DCS corpus counts (≈2021) give per-lemma frequency.
Implication: DCS-frequency headword ordering is a genuine innovation, not a digitisation of
prior art.
**Source:** [A33 note § 1 "The question"](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md). — SanskritLexicography (A33) · 2026-06-24

### DCS lemma data is keyed in two transliterations

**DCS lemma data is keyed in two different transliterations.**
Evidence: `VisualDCS/dcs_lemma_summary.json` (`lemmas`, freqBand 1–5) is **SLP1**-keyed
(joins PWG `key1` natively); `RussianTranslation/src/dcs_lemma_renou.json` (breadth `n_texts`,
dates) is **IAST**-keyed.
Implication: a freq join must transcode SLP1↔IAST for the second; don't assume one scheme.
**Source:** [`freq_route.py` header (lines 7–8) + `iast()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/freq_route.py#L7-L8). — VisualDCS / RussianTranslation · 2026-06-24

### Unaccented DCS cannot distinguish present class I from VI

**The unaccented DCS corpus cannot distinguish present class I from VI (or IV from passive).**
Evidence: WhitneyRoots — the corpus carries no pitch accent, and the class distinction rests
on it: class I (`cárati`, guṇa + root accent) and class VI (`tudáti`, weak root + accented `-á`)
have identical surface present-stems where guṇa doesn't change the vowel. A corpus-derived
class pass produced **117 spurious I/VI additions — all reverted** (120 unsound additions
total, vs 19 kept distinct-class ones).
Implication: never write a corpus-derived verb class into reviewed data without a grammar /
Zaliznyak cross-check.
**Source:** [WhitneyRoots `REVIEWER_GUIDE.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md)
+ [`CHANGELOG.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/CHANGELOG.md) (revert of 120). — WhitneyRoots · 2026-06

### DCS OccId and sent_id are not unique keys

**DCS CoNLL-U `OccId` and `sent_id` are non-unique — using either as a primary key silently
drops data.**
Evidence: the corpus reuses `OccId` across a line's sub-sentences — the M5 pilot build over 13
texts (134,047 tokens total) lost ~20 tokens to PK collisions until the key was replaced;
`sent_id` collides *within* a single chapter — the M6 full build (270 texts) dropped
**449 sentences** before the fix. Both resolved with synthetic autoincrement PKs; cross-vintage
validation is position-based (i-th sentence per text), and 754,726 sentences then cross-walk
with 0 mismatches.
Implication: never key on `OccId`/`sent_id`; use synthetic surrogates or position-within-text.
The stable cross-corpus key is `LemmaId`.
**Source:** [`DCS_CONLLU_IMPORT_PLAN.md` §M5–M6](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/DCS_CONLLU_IMPORT_PLAN.md)
+ `reports/m5_validation.md` / `m6_validation.md` — VisualDCS · 2026-06-06

### DCS UD tense marking conflates aorist and perfect

**UD `Tense=Past` in DCS CoNLL-U conflates aorist and perfect — the distinction exists only in
the legacy 2021 relational export.**
Evidence: UD `Tense` has no Aorist/Perfect value — both surface as `Tense=Past` (**102k tokens**),
distinct only from `Tense=Impf` (47k). The 2021 export kept them apart as numeric codes
(aorist 10–13, perfect 15). The DCS-specific `feat_formation` field (root/s-aorist/reduplicated…)
is present on **< 2 % of verbs**, too sparse to re-split; separately, ~58k participle tokens carry
no tense value and defeat even the surface-ending heuristic (-ta/-na → PPP, -māna/-ant → present)
— they land in "Participle (unclassified)".
Implication: aorist-vs-perfect studies must join the 2026 corpus to the 2021 export on `LemmaId`
(code map in `m4_exports.md`) — UD features alone cannot answer; treat participle tense buckets
as heuristic.
**Source:** [`reports/m7_widgets.md` §Caveats](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/m7_widgets.md)
+ `reports/m4_exports.md` §verb code map — VisualDCS · 2026-06-06

### DCS 2021 and 2026 vintages are not directly comparable

**DCS 2021 and 2026 differ structurally — one 2021 metrical line maps to several 2026 CoNLL-U
sentences, the corpus grew ~10 %, and dependency trees exist for only 74 of 270 texts.**
Evidence: sentence counts diverge while tokens stay flat (Hitopadeśa 718 → 3,432 sentences,
tokens 24,958 → 25,040; Gītagovinda 428 → 692, tokens identical). Texts 246 → 270 (+24, mostly
Vedic Śrautasūtra/Brāhmaṇa additions); lemma Jaccard overlap **89.3 %** (89,645 shared / 100,367
union). Only **74/270 texts** (27 %) carry `HEAD`/`DEPREL` dependency annotation (Vedic Treebank
chapters); the rest are morphology-only.
Implication: never compare sentence-level metrics across vintages — use token-level or
position-based crosswalks; filter to `text.has_dependencies` for syntax work; weight diachronic
frequency comparisons by text coverage.
**Source:** [`reports/coverage_diff.md`](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/coverage_diff.md)
+ `reports/m6_validation.md` — VisualDCS · 2026-06-06

### A fifth of DCS lemmas have no CDSL headword

**18.6 % of DCS-2026 lemmas do not map to any CDSL headword — corpus vocabulary exceeds the
historical dictionaries' headword set.**
Evidence: of 15,902 DCS IAST lemmas, 12,946 (**81.4 %**) link to CDSL normalized keys; 2,956
are corpus-only (lemmatization targets, causatives, derived forms). Crosswalk built by
`build_xref.py` (reusing the transcoder from `wf1/build_wf_from_dcs.py`); frequency map
`wf0/wf.txt` (50,474 keys) → `wf1/wf.txt` (50,574).
Implication: dictionary-lookup pipelines need a lemmatization / sandhi-analysis fallback for
roughly a fifth of corpus vocabulary — headword joins alone will not reach it.
**Source:** [csl-apidev `simple-search/dcs_xref/readme.md`](https://github.com/sanskrit-lexicon/csl-apidev/blob/master/simple-search/dcs_xref/readme.md)
+ `.ai_state.md` §DCS-2026 frequency source — csl-apidev · 2026-06-11

### Sa-Ru glossary token coverage plateaus at 86.6 percent

**The Sa→Ru glossary resolves 86.6 % of the 1,091,528 aligned corpus tokens via DCS form→lemma
plus a vidyut.kosha fallback — the unresolved 41 % of FORMS is only 12.9 % of TOKENS.**
Evidence: coverage ladder — DCS morphology alone 79.1 % (80,949 forms, 42.4 %); + vidyut
fallback **86.6 %** (109,516 forms, 57.4 %); + morpheme-marker recovery 87.1 %. Unresolved:
78,842 forms (41.3 % of forms, 12.9 % token weight) — the rare long tail.
Implication: DCS + vidyut is the workhorse pair for form→lemma resolution; do not chase
form-level completeness — the residue is rare forms with little token mass. (Bulk glossary
data is git-ignored and regenerable.)
**Source:** [`glossary/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossary/README.md)
(built from `corpus_lexicon.jsonl`) — RussianTranslation · 2026-07-01

### Renou period-state tagging covers 770k entries in 8 dicts

**Multi-signal Renou I–V period-state tagging covers 770,292 entries across 8 dictionaries —
but DCS homograph collapse gives high-frequency closed-class words spuriously BROAD era spans.**
Evidence: PWG 123,366, MW 286,560, PW 170,556, AP 90,654, AP90 34,882, BEN 17,310, SCH 29,125,
BHS 17,839 entries tagged from four signals (`ls` deterministic citation, `dcs` corpus
attestation, `bhs` Edgerton, `wl` wisdomlib). State I (Vedic) share: PWG 25.2 %, MW 26.6 %,
PW 14.2 %; state V: BHS 76.3 % (as expected). A min-support gate (DCS ≥ 2 texts or confident
type) pruned 9.9 % of `dcs`-derived states — almost all spurious IV (9,736 dropped) and I
(2,923), with 0 state-II or state-V drops.
Implication: use the per-signal provenance, not the bare state; apply min-support before
trusting a `dcs` state; expect closed-class words (`ca`, `idam`) to carry the union of all
their homographs' eras — maximal I–V spans, not a usable period signal. 20 register
subsections are orthogonal to I–V and add stratum granularity.
**Source:** [`RENOU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md)
(built by `renou_pipeline.py --all`, validated by `renou_audit.py`) — RussianTranslation · 2026-07-01

## Dictionary structure & markup

### PWG encodes secondary stems inline, not in div markup

**PWG never uses `<div n="m">`; secondary stems are encoded inline.**
Evidence: 0 occurrences of `<div n="m">` in `csl-orig/v02/pwg/pwg.txt`; causative/desiderative/
intensive/participle/passive of the simple root appear as `<div n="p">— <ab>caus.</ab> {#…#}`
(a `<div n="p">` whose first token is an `<ab>` label, not a `{#upasarga#}`).
Implication: a secondary-stem segmenter keys on the inline `<ab>` label
(`SEC_DIVP_RE` + a caus/desid/intens/partic/pass/insens label set), not on `<div n="m">`.
**Source:** code [`SEC_DIVP_RE` + the comment](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/root_segment_proto.py#L28-L34)
· measured by [`verify_root_glue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/verify_root_glue.py) (570 split, 0 merged). — csl-orig (pwg) / RussianTranslation · 2026-06-24

### Giant verb roots sit at non-zero homonym indexes

**A headword's giant verb root often sits at a non-zero homonym index.**
Evidence: √i has its 114-prefix verb root at homonym **2** (homonym 0 is the particle);
√mā at index 2, √As at index 1; 19 of the top-50 freq roots have a giant homonym at
index > 0 or more than one giant homonym.
Implication: any per-record split / processing must iterate **all** homonym records, not
`bufs[0]`, or it silently misses the verb (or drops extra giant homonyms).
**Source:** code [`gen_root_split()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py#L258)
· audited by [`audit_root_split.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_root_split.py). — csl-orig (pwg) / RussianTranslation · 2026-06-24

### PWG orders senses genetically, not historically

**PWG orders senses genetically (etymological core first), not historically.**
Evidence: across 13,900 multi-sense entries, printed sense-1 is the oldest-attested only
**73.5 %** of the time; Kendall τ(printed vs date) = **0.375**; citations *within* a sense run
old→new in 76 % of adjacent pairs but are strictly sorted in only 26 %.
Implication: don't auto-re-sort senses by date or frequency (it changes the lead sense for
~1 in 4 entries and fights the source); surface attestation era as per-sense metadata instead.
**Source:** [`sense_order_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sense_order_metrics.md)
· [`analyze_sense_order.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_sense_order.py). — SanskritLexicography (A33) · 2026-06-24

### Vedic-citation density separates the dictionary traditions

**Vedic-citation density cleanly separates the dictionary traditions.**
Evidence: fraction of cited senses reaching a Vedic source — **PWG 23.4 % ≈ MW 24.8 % ≫
AP90 2.3 % ≫ Kochergina 0 %**.
Implication: PWG/MW are etymological-genetic with a real historical apparatus; Apte and
Kochergina are logical-semantic / pedagogical — do not import their sense order into a PWG
translation.
**Source:** [`cross_dict_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/cross_dict_metrics.md)
· [`analyze_cross_dict.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_cross_dict.py). — SanskritLexicography (A33 cross-dict) · 2026-06-24

### SKD and VCP carry essentially zero Western markup

**SKD and VCP carry essentially zero Western markup.**
Evidence: ~0 `<ab>`/`<div>`/`<s>`/`<ls>` tags; citations appear via `iti`/quotes, verbs via
`dhātuḥ`/`preraṇe`/`bhvādi`.
Implication: any marker-based detector scores SKD/VCP at 0 *by construction* — never read 0
as "no content"; use the indigenous cues. (Miscalled ≥4×.)
**Source:** data [`v02/skd/skd.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/skd/skd.txt)
· [`v02/vcp/vcp.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/vcp/vcp.txt) (grep: no `<ab>`/`<div>`). — SKD / VCP (csl-orig) · 2026-06

### The ls source map recognises 72.4 percent of PWG citations

**`ls_source_map.json` recognises 72.4 % of PWG's `<ls>` citations.**
Evidence: 559,243 of 772,567 `<ls>` keys map to one of 45 dated primary sources
(range −1125 → 1830); the unrecognised 27.6 % is catalogues / secondary literature
(Aufrecht's Oxford catalogue, *Indische Studien*, *Indische Sprüche*), which skews *late*.
Implication: dated-citation analyses see the most-cited primary corpus and are conservative
about the oldest stratum, not biased toward it.
**Source:** [`sense_order_metrics.md` § "Foundations check"](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sense_order_metrics.md)
· [`analyze_sense_order.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_sense_order.py). — RussianTranslation · 2026-06-24

### PWG citation occurrences track distinct references

**PWG `<ls>` citation usage frequency ≈ distinct-reference frequency — HTML-target works are
NOT cited disproportionately more than scan-target works.**
Evidence: across the displayed PWG article corpus ([gasyoun.github.io/SanskritLexicography](https://gasyoun.github.io/SanskritLexicography/))
the `<ls>` citations number **50,065 occurrences** vs **37,951 distinct references** — mean ~1.32
citations per distinct reference (most appear exactly once). Splitting resolved links by target
kind, the **scan : HTML ratio is 4.9 : 1 by occurrence vs 5.1 : 1 by distinct reference**: HTML-target
works (only ṚV., AV., P. — Rigveda / Atharvaveda / Pāṇini resolve to rendered digital text rather
than a page scan) are re-cited only marginally more per reference (1.32×) than scan works (1.26×),
*not* an order of magnitude more (a plausible-sounding hypothesis that the data refutes). Occurrence
coverage 83.2 % (41,642 / 50,065 link out = 34,560 scan + 7,082 HTML); the 16.8 % unlinked = 6,505
occurrences of 446 truly-uncovered works + 1,883 non-coordinate `<ls>` labels (edition/cross-ref
notes like "ed. Bomb.", never linkable) + 35 edge-case parse misses.
Implication: distinct-reference counts are a faithful proxy for citation frequency here — do not
occurrence-weight coverage/impact estimates by target type. When counting `<ls>`, exclude
no-coordinate labels (they are not references), and count from the deduplicated display model, not
the raw DE/RU/EN stores (which multiply each citation ~4× via translation fields + store overlap).
**Source:** [`build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py)
→ [`UNCOVERED_SOURCES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/UNCOVERED_SOURCES.md)
+ [`CITATION_SOURCES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CITATION_SOURCES.md) — SanskritLexicography · 2026-07-02

### MW has no sense-level div markup

**MW has no sense-level `<div>`; the sense unit is the record itself.**
Evidence: `csl-orig/v02/mw/mw.txt` carries **0** `<div n="m">` and only **4** `<div n="p">` across
**286,526** `<L>` records — MW essentially never subdivides an entry by sense in markup (senses are
separated by `¦` inside the single record body).
Implication: a sense-segmenter for MW must split on `¦` inside the record, not on `<div>`; and do
**not** template MW's flat structure onto subentry-rich dicts (PWG/Apte) or vice-versa — `<div>` depth
is structural, not a sense boundary, so it over-counts senses.
**Source:** measured `grep -c '<div n="m"' / '<L>'` on
[`v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt). — csl-orig (mw) · 2026-06-26

### Apte is three dictionaries; keys differ stem vs nominative

**"Apte" is three distinct dictionaries, and the same lemma keys differently across dicts
(stem vs nominative).**
Evidence: AP90 (Apte 1890), AP (Apte Revised 1957–59), and AE/ApteES (reverse English→Sanskrit Apte)
are separate `csl-orig` dicts with different markup (AP90 uses `∙²` sense markers, numeric `<pc>0002-1`
page-cols, `{%<lex>a.</lex>%}` labels). The same headword also keys differently *between* dictionaries —
MW stores the bare stem `agni`, Apte the nominative `agniH` — so a cross-dict join on the raw key
silently misses matches (independently re-hit in csl-guides and csl-apidev).
Implication: never treat "Apte" as one source — pick AP90 / AP / AE explicitly. For any cross-dict
headword join, normalise stem↔nominative and join on the `key1` computational key, not `key2`/printed form.
**Source:** csl-guides/.ai_state.md + csl-apidev/.ai_state.md (the `agni`/`agniH` resolver note); markup per
[`v02/ap90/ap90.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90.txt). — csl-guides / csl-apidev / csl-orig · 2026-06

### About 9 percent of typo corrections are collisions

**~9 % of "typo" headword corrections in the early dictionaries are really COLLISIONS — the
correct spelling already exists as its own separate entry, so a `<k1>` respell would create a
duplicate headword or clobber apparatus, not fix a typo.**
Evidence: source-verification of all 122 SanskritSpellCheck FILE-FIRST candidates vs `csl-orig`
(02-07-2026): 11/122 are dual-listings — YAT 5 (wrong+right both attested, often cross-referenced
"Idem": `vizwABU/vizWABU` even share an identical gloss 10 L-ids apart), MW 2 (`kattfRa` already
exists at L42680 beside `kattfna`; `Bawwaraka` short-a is an `L.`-sourced lexicographers' variant),
PWG 2 (the `duzWu` "entry" is an errata note about an *unrelated* correction; `pfzwavanDu`/`pfzwabanDu`
both independently glossed), PW 1 (`*hemana` is Böhtlingk's own `*`-marked constructed form). Plus
1 more (`YAT RiS`) is Dhātupāṭha ṇopadeśa root notation, not a typo. Full verdicts:
[`file_first_verified.tsv`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/corrections_draft/file_first_verified.tsv).
Implication: never bulk-respell a headword-correction list — a filing must offer a third,
*editorial* category (merge vs respell vs leave) for collision pairs; check whether the "right"
form already exists as its own entry before proposing any respell.
**Source:** [`VERIFICATION_2026_07.md`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/corrections_draft/VERIFICATION_2026_07.md) — SanskritSpellCheck · 2026-07

### A verified correction queue decays against live csl-orig

**A verified correction queue DECAYS against the live `csl-orig` — upstream fixes land between
triage and filing.**
Evidence: 1 of 122 FILE-FIRST candidates (`SHS kARqapfzwa→kARqapfzWa`, triaged June 2026) was
already fixed upstream by 02-07-2026 — the correct form exists as its own entry (id 9855), the
wrong form is gone. ~1 week of queue age ≈ 0.8 % decay on this batch.
Implication: re-verify every candidate against the current `csl-orig` immediately before filing
or applying; a stale row filed upstream reads as bot noise to the maintainers.
**Source:** [`file_first_verified.tsv`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/corrections_draft/file_first_verified.tsv) (SHS DROP row) — SanskritSpellCheck · 2026-07

### Citation density is register-bound, not comparable raw

**Per-entry citation density is register-bound — PWG carries 4.63 `<ls>` per entry vs MW's 1.09,
while the indigenous dicts' citations live in the `iti` register that `<ls>` counting misses
entirely.**
Evidence: PWG 570,830 `<ls>` at **4.63/entry** vs MW 311,933 at **1.09/entry** (rates as
published in the citation-registers paper). SKD carries **69,215 `iti`-citations** and VCP
22,070 (KRM 3.13/entry) — all scoring zero under an `<ls>` detector.
Implication: never rank dictionaries by raw `<ls>` density — control for citation register
first, or indigenous lexica are misranked as citation-poor when they are among the richest.
(Generalises the SKD/VCP zero-markup trap to *quantitative* comparisons.)
**Source:** [csl-atlas `docs/articles/paper_citation_registers.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md) — csl-atlas · 2026-06-13

### Sense granularity is a family trait, not a diachronic trend

**Sense granularity is a lexicographic-school trait, not a diachronic trend — the 1822–1957
trend is flat (r = 0.036) while family means span ~1.0–2.4 senses/entry.**
Evidence: across 11 dicts, family means — Benfey 2.42, Apte 2.12, MW 2.00, Wilson 1.71,
Cappeller 1.36, Petersburg 1.13, indigenous ≈1.00 units/entry; correlation with publication
year r = 0.036. (An earlier run in `docs/R2_FINDINGS.md` gives slightly different values —
r = 0.06, Benfey 2.53 — the paper's numbers are the canonical run.)
Implication: any cross-dict measure normalised "per sense" (definition length, citation
density) silently encodes school bias unless family-controlled; never read sense counts as
lexicographic "progress".
**Source:** [csl-atlas `docs/articles/paper_sense_inheritance.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md) — csl-atlas · 2026-06-15

### MW inherited the PWG apparatus skeleton, not its prose

**MW reproduces PWG's citation ORDER (0.81 concordance, 47.8 % of sequences identical) but not
its prose — structural inheritance of the apparatus, independent authorship of the glosses.**
Evidence: over 3,593 shared headwords, MW matches PWG's source-reference sequence at **0.811**
concordance, 47.8 % perfectly identical (chance ≈ 0.50, ~5–17 % chance-identical for ≥3 sources);
the gradient is Petersburg-specific (PWG 0.81 > PW 0.73 > BEN 0.68 > independent AP 0.42). MW's
English gloss length tracks PWG's German **no more than it tracks Apte's independent English**
(Spearman 0.564 vs 0.576, differential −0.01), and shared-error overlap is only 1.6 % (F4b). Complementary scale fact: MW (194,084 keys, 1899) contains 88–94 %
of nine other dicts' headwords (BEN 0.94, BOP 0.94, MD 0.93, GRA 0.88 …) — aggregation, not
proof of derivation.
Implication: "MW copied Böhtlingk" is true of the apparatus skeleton (headwords, citation
order, homonym divisions) and false of the content; use citation-sequence concordance — not
shared errors or headword containment — as the forensic marker of descent.
**Source:** [csl-atlas `scripts/forensic/f5_entry_comparison.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f5_entry_comparison.py)
+ [`docs/articles/article_21_apparatus_not_errors.md` §3.4](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) — csl-atlas · 2026-06-03

### PWG and MW share 94,753 headwords in the union index

**The cross-dict union index already answers headword-overlap questions — PWG∩MW = 94,753
(89 % of PWG-bearing keys are also in MW); don't rebuild it.**
Evidence: `HeadwordLists/union/union_headwords.tsv` — 323,425 union headwords over 15 dicts,
SLP1-keyed with per-dict membership + gender; PWG-bearing 106,054, MW-bearing 193,852,
both 94,753.
Implication: consume this asset for any cross-dict join or coverage estimate (the PWG→EN
pilot's MW translation-memory rides on it); a new pairwise-overlap script is reinvention.
**Source:** [`HeadwordLists/union/union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) — SanskritLexicography · 2026-06-26

### Body-text headword mining is a dead end (38.6 percent precision)

**Mining "hidden" headwords from dictionary bodies / reverse dicts yields only 38.6 % precision
— the 376k broad headword index is already near-ceiling for CDSL headword vocabulary.**
Evidence (measured 2026-06-15 during the csl-atlas broad-headword review): (1) `<k2>` is `<k1>`
re-encoded (compound em-dash, avagraha, accents) — the apparent "+152k new lemmas" was a
normalization artifact, ~0 real; (2) the big forward dicts (MW 287k, PW, PWG, VCP, SKD) already
split compounds into their own `<L>` records — bodies hold no hidden headwords; (3) a built +
filtered extractor over the dicts that DO pack compounds scored **38.6 % precision overall** by
adversarial classification (bor 18 %, bur 32 % transcode-garbage, ae 34 %, mw72 36 %
truncation-garbage, pwg 76 %) — the "new" tokens are dominated by inflected forms, glued
multi-word phrases, and IAST→SLP1 transcode/sandhi artifacts. *Provenance caveat:* the measuring
extractor (`scripts/lib/dict-body-headwords.mjs`) was deleted with the rejected experiment, so
these numbers survive only in the review session record — registered here precisely so the
negative result is not re-derived.
Implication: don't redo headword mining for coverage. A real findability gain needs different
work — a corpus inflected-form→lemma index (DCS) and/or vidyut sandhi/compound splitting —
which raises findability, not distinct-lemma count.
**Source:** csl-atlas broad-headword review session (xhigh /code-review, 2026-06-15), context
[PR #99](https://github.com/sanskrit-lexicon/csl-atlas/pull/99); index scale per
[`docs/BROAD_HEADWORD_COVERAGE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BROAD_HEADWORD_COVERAGE.md) — csl-atlas · 2026-06-15

### Detector precision stratifies by digitization quality

**Spell-detector tier-A precision stratifies by digitization quality, not dictionary age —
mature digitizations yield ~0.2–0.3 % real typos per flag, poorly-digitised ones 11–15 %.**
Evidence: across 33 triaged dicts, fileable-typo rates in the top confidence tier — MW 4/1,954
(0.2 %), PW 2/657 (0.3 %) vs SHS 37/246 (**15 %**), YAT 27/247 (11 %), ACC 22/174 (12.6 %); 122
fileable typos total, concentrated in 11 dicts (22 dicts yielded zero). The false-positive floor
on mature dicts is intentional apparatus: a **2,297-entry** `do_not_file` suppression list of
documented-intentional spellings (v.l. / w.r. / cross-refs / in-compound forms) was built from
the dicts' own `wrong_readings` apparatus; after deploying it, all four correctors re-run at
FP = 0.
Implication: point detector effort at poorly-digitised sources; on mature dicts, treat every
flag as apparatus-until-proven-typo, and check the suppression list before flagging — the FP
floor cannot be lowered without reading the entry body.
**Source:** [SanskritSpellCheck `corrections_draft/README.md`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/corrections_draft/README.md)
+ [`nochange/do_not_file_suppress.txt`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/nochange/do_not_file_suppress.txt) — SanskritSpellCheck · 2026-06-24

### Correction events concentrate in sense text

**Twelve years of Cologne corrections concentrate in sense text — 52.7 % sense vs 17.5 % markup
vs 17.3 % headword over the 33,755 derived-label events — and error profiles are location- and
dict-specific.**
Evidence: of 52,498 correction events across 43 dicts (2014–2026), the 33,755 with derived
location labels split: sense 17,778 (52.7 %), markup 5,902 (17.5 %), headword 5,823 (17.3 %),
citation 3,335 (9.9 %); top phonetic confusion b→v (341); per-dict correction density spans
PGN 160/1k entries down to BOP 45.5/1k.
Implication: "surface error" claims must specify the microstructure location — the global
minor-edit rate masks that headword repairs are structural while sense repairs are often tiny
diacritic fixes; markup errors are a real 17.5 % class, not noise.
**Source:** [csl-observatory `reports/obs_t_typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md)
(Axis A table) — csl-observatory · 2026-06-17

## Etymology & derivation

### Indigenous dictionaries agree on derivation; Wilson is the outlier

**The indigenous Sanskrit dictionaries agree on a head-word's derivation 90–100 %; Wilson 1832
is the systematic outlier (23–61 %).**
Evidence: across 10 Cologne dicts whose etymology was extracted to `<dict>_etymology.tsv`, affix
agreement on shared head-words (proportion, 95 % Wilson CI) is SKD↔VCP 93.8 % [85.2–97.6], Apte↔AP
100 % [97.9–100], VCP↔SHS 98.5 % [95.8–99.5], but WIL↔SKD only **22.9 % [14.6–34.0]** and WIL↔VCP
**61.2 % [58.7–63.7]** — the Wilson interval (≤34 %) is **disjoint** from every Sanskrit-side pair
(≥83 %), so the divergence is statistically clear, not sampling noise. Cross-tradition root
attribution: MW↔PWG (English √ vs German "Wurzel") 65 %, PWG↔PW 93 %.
Implication: the Pāṇinian analysis is a stable cross-source signal usable as a consensus/QA oracle;
Wilson's divergence is a distinct stratum, not noise.
**Source:** [`cross_dict_agreement.csv`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/cross_dict_agreement.csv)
+ [PAPER_DRAFT.md](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/PAPER_DRAFT.md)
· dashboard https://sanskrit-lexicon.github.io/csl-orig/ — csl-orig · 2026-06-26

### The E abbreviation tag is polysemous across dicts

**The same `<ab>E.</ab>` tag means different things across dicts — count the meaning, not the
marker.**
Evidence: WIL `E.` = Etymology (39,713×); but CAE `E.` = "Epithet of" (`E. of Śiva/Viṣṇu/Indra`,
584×) and MD `E.` = "Epic" (`āste (E. + I. Ā.)`). A tag-count survey wrongly flagged CAE/MD as
etymology sources; reading the entry contexts corrected it.
Implication: never infer content from a shared tag across dicts (generalises the SKD/VCP
zero-markup trap); validate a marker's *sense* per dictionary before parsing it.
**Source:** `csl-orig/v02/{cae,md}/` entry contexts — csl-orig · 2026-06-26

### Root-recovery tiers err on root form, not identity

**Inferred root-recovery tiers err on root FORM, not root identity — and an LLM root pass must
be dhātu-validated.**
Evidence: a DeepSeek-judged audit of the etymology extractor's inferred tiers gives nearest-root ≈ 69 %,
oracle-join ≈ 74 % root precision, but most "misses" are a correct root in a stem rather than citation
form (`sada` for `sad`, `kṝ` for `kṛ`) — true identity-precision is higher. A DeepSeek `resolve` pass over
the residual empties (VCP 87→97 %, SHS 59→95 %) only writes a root that validates against the canonical
dhātu list, so hallucinated non-dhātu roots are discarded, not stored.
Implication: when filling roots by inference or LLM, (1) normalize to dhātupāṭha citation form before
comparing/joining, and (2) always gate an LLM-proposed root through a known-dhātu set — never trust it raw.
Resolved by a `build_root_normalization.py` pass (CANON = `mw_roots.tsv` citation forms ONLY — vidyut's
surface forms keep the thematic `-a` and must NOT seed CANON): 622 variants folded (`sada`→`sad`),
guarded so a real distinct root (`kṝ` ≠ `kṛ`) is never collapsed; oracle-join precision then rose 74→83 %,
nearest-root stays the weakest tier (~66–75 %, genuine wrong-token grabs) and is tagged for downweighting.
**Source:** [`nearest_root_audit.json`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/nearest_root_audit.json)
+ [`build_root_normalization.py`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/build_root_normalization.py) — csl-orig · 2026-06-26

## Encoding & normalization

### IAST Unicode collides and normalises lossily

**IAST Unicode collides and lossily normalises if you're naïve.**
Evidence: `ś` = `s` + U+0301 (combining acute), which collides with a pitch-accent mark;
NFD-decompose-then-strip-Mn destroys vowel length (`ā`→`a`) and retroflex dots (`ṣ`→`s`).
Implication: use a length-preserving `form_key`, not a blanket NFD+strip-combining.
**Source:** [`form_key` in sanskrit_util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py). — sanskrit-util / shared · 2026-06

### BOM state is inconsistent across exports

**`csl-orig` files never carry a BOM; many exported HeadwordLists do.**
Evidence: `csl-orig` dict `.txt` are BOM-free; e.g. `MW-unique-key1-…txt` **has** `EF BB BF`
while its `key2` sibling does not.
Implication: check `head -c 3` before transforming; preserve the file's existing BOM state on
write; never silently add/strip one.
**Source:** [SanskritLexicography `CLAUDE.md` § "Encoding — BOM is inconsistent"](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md). — csl-orig / SanskritLexicography · 2026-06

### Injected BOMs crash the hw record parser

**A stray UTF-8 BOM slipped into a dict source by a markup commit crashes the record parser
with a cryptic "init_entries Error 2" — an encoding symptom, not a structure defect.**
Evidence: markup-correction commits introduced BOMs into 10 dictionary sources (AP, AP90, MW,
BUR, INM, KRM …); `hw.py` opens with `encoding='utf-8'` (no BOM strip), so the BOM'd first
`<L>` line fails its match, the parser skips it and dies on the next `<LEND>` as
"init_entries Error 2". BOM removal (commit `922602c` in csl-orig) resolved it; the hardening
has since shipped — `hw.py` now reads with `utf-8-sig` (csl-pywork `e6d0f30`, closes #50).
Implication: after any batch correction, verify the first 3 bytes of every touched dict file
(must not be `EF BB BF`); when a line-oriented parser fails on record 1 with a structure-sounding
error, check encoding before structure. (Complements the BOM-state finding above — this is how
the BOM gets *introduced* and what it breaks.)
**Source:** [csl-corrections `.ai_state.md`](https://github.com/sanskrit-lexicon/csl-corrections/blob/master/.ai_state.md)
§Dev Notes — csl-corrections · 2026-06-27

### devanagari_to_slp1 mis-routes retroflex la

**`devanagari_to_slp1` mis-routes ळ (ḷa).**
Evidence: a pre-existing `sanskrit-util` master bug routes ळ via IAST→`x` instead of `L`.
Implication: low-severity (affects `ocr_verify`), but don't trust ḷa round-trips until fixed
(fix in progress on branch `feat/deva-to-slp1`).
**Source:** [`devanagari_to_slp1` in sanskrit_util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py). — sanskrit-util · 2026-06

### Gloss-language spelling drift tracks reform type, not age

**Orthographic drift in a dictionary's gloss language is governed by the TYPE of the language's
spelling reform, not the dictionary's age — legislated ≫ convention ≫ none — and the metric
saturates to zero for post-1890 English.**
Evidence: drift per 1k gloss tokens against modern norms — Russian (Kossovich; 1918 legislated
reform) **358.17** ≫ German (PW era; 1901/1996 legislated) **10.26** ≫ English (WIL 1832) 0.46 /
French (BUR 1866) 0.31 (convention-only) ≫ Latin (BOP 1847) **0.00** (no reform). Regime bound:
seven 20th-century English dicts read exactly 0.00 across 1890–1990 — a full century — while
MW 1899 reads 0.01. Dating power follows: German Spearman ρ = −0.975 (±15 yr MAE) vs English
ρ = −0.642 (±40 yr, saturated).
Implication: use drift for search-normalization maps in legislated-reform languages (a 15,685-form
German 1901/1996 map exists — DTA-harvested, dic-validated); do NOT use it to date English or
French dictionaries after ~1890 — the signal is regime-bounded, not a universal clock.
**Source:** [SanskritSpellCheck `docs/ORTHO_DRIFT_FINDINGS.md`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/docs/ORTHO_DRIFT_FINDINGS.md)
+ `ortho_drift/*_drift_summary.tsv` (per-language tables) — SanskritSpellCheck · 2026-06-26

---

_Started 2026-06-26 (relocated from `Uprava/FINDINGS.md`, which now holds **non-Sanskrit**
findings). Appended on a regular basis — add findings as they're discovered; this is the
shared memory of "things we measured that aren't obvious from the code."_

_Dr. Mārcis Gasūns_
