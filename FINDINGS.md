# FINDINGS — cross-repo empirical registry

_Created: 26-06-2026 · Last updated: 17-07-2026_

📊 **Live dashboard:** <https://gasyoun.github.io/SanskritLexicography/findings/> —
importance/section breakdown, staleness flags, monthly time series (§12/§13/§21/§25) and the
§41 platform-liveness board; refreshed monthly (see
[findings_dashboard/](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard)).

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

**Schema per finding:** a `###` heading numbered `§N` (the number + heading anchor are the
finding's stable citation, listed in the index below), then the full **claim** in bold,
`Evidence:` (the measurement, with numbers / a file + line), `Implication:` (what to do or not
do), and a blockquoted (`> `) **Source** paragraph linking the exact statement and/or code,
with a `— repo · date` tag — the `>` gives the Source line its left indent and muted rendering
in plain Markdown; no HTML in this file, ever. Keep findings grounded (a number, a file, a
probe), never a hunch. **Importance label:** every finding carries a colour dot at the start of its claim line and its index entry — 🔴 3 important · 🟠 2 medium · 🟡 1 not that important — assign one when appending. **Numbers are append-only:** a new finding takes the next free number
(currently §448) whatever its section, so existing numbers never shift; when a finding is later
refuted or superseded, strike it and say why — never reuse its number.

## Index

**Grammar & morphology data**

- 🟠 [§1. Whitney accent-mobility rules are machine-encodable](#1-whitney-accent-mobility-rules-are-machine-encodable) — the Zaliznyak a–f accent axis is an encoding task, not a missing source; VedaWeb 2.0 validates. **Encoded 02-07-2026, validated 03-07-2026 (17/19 GO)** → WhitneyRoots `crosswalk/accent_rules.json` / `accent_validation.json`.
- 🟠 [§42. Whitney self-contradicts on derivative ī-stem gen.pl accent](#42-whitney-self-contradicts-on-derivative-ī-stem-genpl-accent) — §320 "not thrown forward" vs §319a RV "usually" shifts vs §356's own printed nadī́nām; encode as a per-lemma variant, not a rule. **Empirical split measured 03-07-2026 (n=2, too thin to resolve)** → §54.
- 🟠 [§54. Whitney accent axis validates at 18/19 matrix cells GO against attested RV accents](#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents) — VedaWeb 2.0 scoring; T8c exception resolved as a rule gap (H115); D3 split still too thin to resolve.
- 🟠 [§2. Homonym token-splitting has a hard morphological ceiling](#2-homonym-token-splitting-has-a-hard-morphological-ceiling) — only 5 of 38 DCS-lumped groups are gaṇa-splittable; the rest need gloss adjudication.
- 🟠 [§3. The Warnemyr scrape union-smears homonym classes](#3-the-warnemyr-scrape-union-smears-homonym-classes) — local Whitney class files merge homonyms' classes; derive from the live paradigm pages.
- 🟡 [§4. PWG nominal grammar compresses into 335 paradigm tokens](#4-pwg-nominal-grammar-compresses-into-335-paradigm-tokens) — 98,639 of 123,366 entries carry a Zaliznyak-style token.
- 🟡 [§63. vidyut dhātupāṭha adjudicates the 2014 Palsule-exclusion dispute](#63-vidyut-dhātupāṭha-adjudicates-the-2014-palsule-exclusion-dispute-five-añc-dhātus-no-and-but-ast-is-paninian) — five añc dhātus (4añc recoverable), no and, but ast IS Paninian; grep vidyut as `ancu`, not `aYc`.

**Corpus & parallel-text data**

- 🟠 [§5. The parallel corpus rarely attests prefixed-verb forms](#5-the-parallel-corpus-rarely-attests-prefixed-verb-forms) — sandhi-join lookups are a no-op; ~80 % of prefixed forms miss.
- 🟠 [§6. No printed frequency dictionary of Sanskrit exists](#6-no-printed-frequency-dictionary-of-sanskrit-exists) — DCS-frequency ordering is genuine innovation.
- 🔴 [§7. DCS lemma data is keyed in two transliterations](#7-dcs-lemma-data-is-keyed-in-two-transliterations) — SLP1 vs IAST across the two frequency files.
- 🔴 [§8. Unaccented DCS cannot distinguish present class I from VI](#8-unaccented-dcs-cannot-distinguish-present-class-i-from-vi) — 117 spurious corpus-derived class additions were reverted.
- 🟠 [§62. Varga distribution is almost epoch-stable (Cramér's V = 0.037)](#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards) — p-values carry no signal at DCS scale; the 2014 dissertation prose read high p as «growth»; shares agree with the p-table against the prose.
- 🔴 [§9. DCS OccId and sent_id are not unique keys](#9-dcs-occid-and-sent_id-are-not-unique-keys) — PK collisions silently dropped tokens and 449 sentences before synthetic keys.
- 🟠 [§10. DCS UD tense marking conflates aorist and perfect](#10-dcs-ud-tense-marking-conflates-aorist-and-perfect) — both surface as Tense=Past; recover via the 2021 export.
- 🟠 [§11. DCS 2021 and 2026 vintages are not directly comparable](#11-dcs-2021-and-2026-vintages-are-not-directly-comparable) — one metrical line ↔ several CoNLL-U sentences; treebanks on 74/270 texts only.
- 🟠 [§12. A fifth of DCS lemmas have no CDSL headword](#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword) — 81.4 % link; the rest need a lemmatization fallback.
- 🟡 [§13. Sa-Ru glossary token coverage plateaus at 86.6 percent](#13-sa-ru-glossary-token-coverage-plateaus-at-866-percent) — DCS + vidyut is the workhorse; the unresolved 41 % of forms is only 12.9 % of tokens.
- 🟠 [§14. Renou period-state tagging covers 770k entries in 8 dicts](#14-renou-period-state-tagging-covers-770k-entries-in-8-dicts) — multi-signal I–V states; homograph collapse gives closed-class words spuriously broad spans.

**Dictionary structure & markup**

- 🟠 [§15. PWG encodes secondary stems inline, not in div markup](#15-pwg-encodes-secondary-stems-inline-not-in-div-markup) — segment on the inline ab label, not div n="m".
- 🔴 [§16. Giant verb roots sit at non-zero homonym indexes](#16-giant-verb-roots-sit-at-non-zero-homonym-indexes) — iterate all homonym records, never bufs[0].
- 🔴 [§17. PWG orders senses genetically, not historically](#17-pwg-orders-senses-genetically-not-historically) — sense-1 is oldest only 73.5 % of the time; don't re-sort.
- 🟠 [§18. Vedic-citation density separates the dictionary traditions](#18-vedic-citation-density-separates-the-dictionary-traditions) — PWG ≈ MW ≫ AP90 ≫ Kochergina.
- 🔴 [§19. SKD and VCP carry essentially zero Western markup](#19-skd-and-vcp-carry-essentially-zero-western-markup) — marker detectors score 0 by construction.
- 🟠 [§20. The ls source map recognises 72.4 percent of PWG citations](#20-the-ls-source-map-recognises-724-percent-of-pwg-citations) — the unrecognised tail is late secondary literature.
- 🟡 [§21. PWG citation occurrences track distinct references](#21-pwg-citation-occurrences-track-distinct-references) — HTML-target works are not re-cited disproportionately.
- 🟠 [§22. MW has no sense-level div markup](#22-mw-has-no-sense-level-div-markup) — split on ¦ inside the record.
- 🔴 [§23. Apte is three dictionaries; keys differ stem vs nominative](#23-apte-is-three-dictionaries-keys-differ-stem-vs-nominative) — agni vs agniH; join on key1.
- 🔴 [§24. About 9 percent of typo corrections are collisions](#24-about-9-percent-of-typo-corrections-are-collisions) — the "right" form often already exists as its own entry.
- 🟠 [§25. A verified correction queue decays against live csl-orig](#25-a-verified-correction-queue-decays-against-live-csl-orig) — ~0.8 %/week; re-verify before filing.
- 🟠 [§26. Citation density is register-bound, not comparable raw](#26-citation-density-is-register-bound-not-comparable-raw) — PWG 4.61 vs MW 1.09 ls/entry; SKD's ~80k citations are iti-register; markup-adjacent `iti` (`<s>iti`) evades a space-preceded counter (KRM ~2/3 hidden).
- 🟠 [§27. Sense granularity is a family trait, not a diachronic trend](#27-sense-granularity-is-a-family-trait-not-a-diachronic-trend) — r = 0.036 over 135 years; control by school.
- 🟠 [§28. MW inherited the PWG apparatus skeleton, not its prose](#28-mw-inherited-the-pwg-apparatus-skeleton-not-its-prose) — 0.81 citation-order concordance; gloss length tracks PWG no more than an independent control.
- 🟠 [§29. PWG and MW share 94,753 headwords in the union index](#29-pwg-and-mw-share-94753-headwords-in-the-union-index) — consume HeadwordLists/union, don't rebuild.
- 🔴 [§30. Body-text headword mining is a dead end (38.6 percent precision)](#30-body-text-headword-mining-is-a-dead-end-386-percent-precision) — the 376k broad index is near-ceiling; measured negative result.
- 🟠 [§31. Detector precision stratifies by digitization quality](#31-detector-precision-stratifies-by-digitization-quality) — mature dicts ~0.2 % real flags vs 11–15 % on poorly-digitised ones.
- 🟡 [§32. Correction events concentrate in sense text](#32-correction-events-concentrate-in-sense-text) — 52.7 % sense / 17.5 % markup / 17.3 % headword over 52k events.
- 🟠 [§46. Twelve years of corrections cover only ~10–14 % of the estimated error population](#46-twelve-years-of-corrections-cover-only-1014--of-the-estimated-error-population) — Chapman mark–recapture over the two near-disjoint correction eras; PW ~14 %, MW ~10 % done; 40 dicts not even estimable.
- 🟠 [§43. SKD/VCP sense/citation fusion is a record-type effect, not a dictionary-level one](#43-skdvcp-sensecitation-fusion-is-a-record-type-effect-not-a-dictionary-level-one) — corpus-scale count inverted the one-lemma *dharma* exemplar's direction; never generalise a citation-register claim from one lemma.
- 🟠 [§44. Raw Latin-string tallies over gloss text include etymological false positives; Bopp lacks √yabh](#44-raw-latin-string-tallies-over-gloss-text-include-etymological-false-positives-bopp-lacks-yabh) — MW72's lone *cunnus* glosses a Lithuanian cognate, not a headword; BOP has no √*yabh* entry (all *futu-* hits are *futurum*); trust A36's curated CSV, not the raw sweep.
- 🟠 [§45. Siglum prefix-families routinely bundle several distinct works; the diacritic-stripping fold has poisoned keys](#45-siglum-prefix-families-routinely-bundle-several-distinct-works-the-diacritic-stripping-fold-has-poisoned-keys) — 26/50 top families mix 2–6 works (Bhag./BhP., Rajan./Rajat., 5 Śabda-kośas); `samk` fold merges Śaṃk°+Sāṃk°; ~120 pseudo-variants are just unstripped roman numerals; MW unknown-layer tail = only 6.5% of citation weight.
- 🔴 [§61. The reverse dictionary's 30 sources split ~18 PD vs ~10 in-copyright — the merged headword list is not automatically publishable](#61-the-reverse-dictionarys-30-sources-split-18-pd-vs-10-in-copyright--the-merged-headword-list-is-not-automatically-publishable) — rights table + 3 decision options in the H265 analysis; ruling is a human @DECIDE.
- 🟠 [§71. PWG marks case government explicitly ≈3,853 times across ≈3,222 senses — a deterministic census, not an estimate](#71-pwg-marks-case-government-explicitly-3853-times-across-3222-senses--a-deterministic-census-not-an-estimate) — 2,309 single-case parens + 40 variation groups + 1,504 mit-phrases; verbs only 417 of 1,476 marker-bearing entries; the store slot `government` is empty (0/11,261).
- 🔴 [§64. PW-only headwords outnumber PWG-only ones 6-to-1 — PWG is not the sole spine of the local layer universe](#64-pw-only-headwords-outnumber-pwg-only-ones-6-to-1-pwg-is-not-the-sole-spine-of-the-local-layer-universe) — 40,338 headwords (24%) exist in PW/SCH/PWKVN with no PWG record at all; any worklist built by iterating PWG keys silently drops ~36% of the local-layer universe; NWS adds net-new content to 20.3% of headwords.
- 🟠 [§74. The ls-graph citation matrix is degenerate for MW](#74-the-ls-graph-citation-matrix-is-degenerate-for-mw--its-top-abbreviations-sit-unresolved-use-the-citation-apparatus-siglum-matrix-for-cross-dict-citation-profiles) — MW resolves to 5 texts, top keys unresolved; BEN~MW=0.0 artifact; use the citation-apparatus siglum matrix; only 7/14 L0-edge dicts have `<ls>` adapters.
- 🔴 [§77. Amarakosha and SIL semdom both bolt a formal annex onto a semantic taxonomy — and it is the same ~10% once polysemy is set aside](#77-amarakosha-and-sil-semdom-both-bolt-a-formal-annex-onto-a-semantic-taxonomy--and-it-is-the-same-10-once-polysemy-is-set-aside) — AK kāṇḍa 3 = 46.4% of synsets vs semdom top-9 = 9.4% of domains; minus nānārtha's polysemy register the form-class annexes converge (10.7% vs 9.4%); homonymy is the one annex bucket AK needed and SIL did not.
- 🔴 [§447. PWG's own closing sense-marker glyph "〉" was never recognized by the sense-splitter — ~50% of German senses were silently merged into their first sub-sense](#447-pwgs-own-closing-sense-marker-glyph--was-never-recognized-by-the-sense-splitter--50-of-german-senses-were-silently-merged-into-their-first-sub-sense) — `microstructure.py`'s `MARK` regex only ever matched ASCII `)`, never `〉` (87,680 occurrences in `csl-orig/v02/pwg/pwg.txt`); fixed, verified 2500-card audit 2500→3738 senses (1.0→1.5/card), zero new anomalies.

**Etymology & derivation**

- 🟠 [§33. Indigenous dictionaries agree on derivation; Wilson is the outlier](#33-indigenous-dictionaries-agree-on-derivation-wilson-is-the-outlier) — 90–100 % agreement vs Wilson 23–61 %.
- 🟠 [§34. The E abbreviation tag is polysemous across dicts](#34-the-e-abbreviation-tag-is-polysemous-across-dicts) — Etymology / Epithet / Epic; count the meaning, not the marker.
- 🟠 [§35. Root-recovery tiers err on root form, not identity](#35-root-recovery-tiers-err-on-root-form-not-identity) — normalize to dhātupāṭha citation form; gate LLM roots through a known-dhātu set.

**Encoding & normalization**

- 🔴 [§36. IAST Unicode collides and normalises lossily](#36-iast-unicode-collides-and-normalises-lossily) — NFD + strip-Mn destroys length and retroflexion.
- 🟠 [§37. BOM state is inconsistent across exports](#37-bom-state-is-inconsistent-across-exports) — check head -c 3; preserve on write.
- 🟠 [§38. Injected BOMs crash the hw record parser](#38-injected-boms-crash-the-hw-record-parser) — "init_entries Error 2" is an encoding symptom, not a structure defect.
- 🟡 [§39. devanagari_to_slp1 mis-routes retroflex la](#39-devanagari_to_slp1-mis-routes-retroflex-la) — ळ → x instead of L.
- 🟠 [§40. Gloss-language spelling drift tracks reform type, not age](#40-gloss-language-spelling-drift-tracks-reform-type-not-age) — legislated ≫ convention ≫ none; the metric saturates post-1890 for English.
- 🟡 [§60. Practical Russian transcription of Sanskrit names has no safe reverse transliteration](#60-practical-russian-transcription-of-sanskrit-names-has-no-safe-reverse-transliteration) — dental/retroflex collapse in Cyrillic-only name glossaries blocks a deterministic SLP1 join key.

**External platforms & services**

- 🟠 [§41. The Sanskrit dictionary-platform landscape, probed live](#41-the-sanskrit-dictionary-platform-landscape-probed-live) — michaelmeyer.fr = 41 dicts w/ per-sense scan links; Heritage Inria bot-walled; DCS HTTPS broken; VedaWeb → Tekst; Cologne license is BY-**SA**, not NC.
- 🟠 [§47. Heritage data is acquirable despite the Anubis wall — via a GitHub mirror; the morphology XML is not in it](#47-heritage-data-is-acquirable-despite-the-anubis-wall--via-a-github-mirror-the-morphology-xml-is-not-in-it) — gitlab.inria.fr walled too; mirror [darkone23/Heritage_Resources](https://github.com/darkone23/Heritage_Resources) (03-2025, LGPLLR) has DICO + MW-aligned pages + freq TSVs; inflected-form XML only via install-time/walled page.
- 🟡 [§59. Böhtlingk's Indische Sprüche (both editions) already fully digitized in sanskrit-lexicon-scans](#59-böhtlingks-indische-sprüche-both-editions-already-fully-digitized-in-sanskrit-lexicon-scans-not-just-sanskrit-lexicon) — check funderburkjim personal repos + sanskrit-lexicon-scans org before assuming a Cologne primary source isn't digitized yet.
- 🟠 [§48. VedaWeb 2.0's resource export is an async task behind a pickup-key, not a direct GET — and the server went unresponsive mid-attempt](#48-vedaweb-20s-resource-export-is-an-async-task-behind-a-pickup-key-not-a-direct-get-and-the-server-went-unresponsive-mid-attempt)
- 🟠 [§49. MW↔Heritage coverage highlighting is a duplicate-anchor pattern, not a CSS class — and the mirror's "current" dictionary is a different-scope asset than the 2014 reader stem list](#49-mwheritage-coverage-highlighting-is-a-duplicate-anchor-pattern-not-a-css-class-and-the-mirrors-current-dictionary-is-a-different-scope-asset-than-the-2014-reader-stem-list)
- 🟠 [§50. CDSL display paths are NOT uniformly `/2020/web/` — and two new digitizations landed in June 2026](#50-cdsl-display-paths-are-not-uniformly-2020web-and-two-new-digitizations-landed-in-june-2026)
- 🟠 [§51. Huet correspondence predates this session (2021) — the morphology-XML "gate" was already resolved in writing; direct download URLs recovered](#51-huet-correspondence-predates-this-session-2021-the-morphology-xml-gate-was-already-resolved-in-writing-direct-download-urls-recovered)
- 🟡 [§52. Heritage vs kosha forms diff: the small raw overlap is mostly convention + model difference, and "disagreements" are two-thirds lemmatization policy, not error](#52-heritage-vs-kosha-forms-diff-the-small-raw-overlap-is-mostly-convention-model-difference-and-disagreements-are-two-thirds-lemmatization-policy-not-error)
- 🔴 [§53. The WIL etymology extraction's affix field is ~half noise — Wilson "outlier" figures are substantially a measurement artifact](#53-the-wil-etymology-extractions-affix-field-is-half-noise-wilson-outlier-figures-are-substantially-a-measurement-artifact)
- 🟡 [§55. `gen_opt_harness2.py` output-budget: coarser wins on both knobs, in opposite directions](#55-gen_opt_harness2py-output-budget-coarser-wins-on-both-knobs-in-opposite-directions)
- 🟡 [§56. DICO's entry anchors nest three structural roles under one HTML class — only one is a true entry boundary](#56-dicos-entry-anchors-nest-three-structural-roles-under-one-html-class-only-one-is-a-true-entry-boundary)
- 🟡 [§57. samskrtam.ru/z/ is id-addressed with no name lookup — deep-linking needs a scraped root→id table; 8 primer-basic roots are absent](#57-samskrtamruz-is-id-addressed-with-no-name-lookup-deep-linking-needs-a-scraped-rootid-table-8-primer-basic-roots-are-absent)
- 🟡 [§58. PWG-RU promoted store has input-level provenance, but old RU rows lacked exact model versions](#58-pwg-ru-promoted-store-has-input-level-provenance-but-old-ru-rows-lacked-exact-model-versions)
- 🟠 [§65. 6.6 % of the DeepSeek corpus word-alignments ground to nothing in their verse](#65-66-of-the-deepseek-corpus-word-alignments-ground-to-nothing-in-their-verse)
- 🔴 [§66. The DCS `QL` frequency workbook's `SLP1` and length columns are truncated at ṣṭh/ḍh clusters](#66-the-dcs-ql-frequency-workbooks-slp1-and-length-columns-are-truncated-at-ṣṭhḍh-clusters)
- 🟠 [§67. In PWG, article size dwarfs every "parametric" statistic you can extract from the entry](#67-in-pwg-article-size-dwarfs-every-parametric-statistic-you-can-extract-from-the-entry)
- 🟠 [§68. The Sanskrit spellchecker landscape: one dormant demo, one license-unsettled 543k wordlist, no occupant](#68-the-sanskrit-spellchecker-landscape-one-dormant-demo-one-license-unsettled-543k-wordlist-no-occupant)
- 🟡 [§69. Hand-transcribed telemetry cannot adjudicate code-vs-infra — and a local-only ledger silently swaps your denominator](#69-hand-transcribed-telemetry-cannot-adjudicate-code-vs-infra-and-a-local-only-ledger-silently-swaps-your-denominator)
- 🟡 [§70. pwg_ru TM composite grade: A is consensus-gated (5.7%), and a reference-free surface QE cannot detect wrong-sense](#70-pwg_ru-tm-composite-grade-a-is-consensus-gated-57-and-a-reference-free-surface-qe-cannot-detect-wrong-sense)
- 🟡 [§72. VedaWeb's `id_gra` token field IS the Grassmann `<L>` entry number — no fuzzy text-matching needed for a GRA↔VedaWeb crosswalk](#72-vedawebs-id_gra-token-field-is-the-grassmann-l-entry-number-no-fuzzy-text-matching-needed-for-a-gravedaweb-crosswalk)
- 🟠 [§73. VedaWeb 2.0's "CC BY 4.0 for everything" claim is not machine-confirmed — only 2/36 catalog resources carry an explicit license field](#73-vedaweb-20s-cc-by-40-for-everything-claim-is-not-machine-confirmed-only-236-catalog-resources-carry-an-explicit-license-field)
- 🟡 [§75. The full Devībhāgavata-purāṇa Sanskrit is NOT on GRETIL — only the Devigita fragment; the complete mūla lives on sanskritdocuments.org without `DbhP_` markers](#75-the-full-devībhāgavata-purāṇa-sanskrit-is-not-on-gretil-only-the-devigita-fragment-the-complete-mūla-lives-on-sanskritdocumentsorg-without-dbhp_-markers)
- 🟠 [§78. DCS 2026 sqlite carries 531,747 sense-annotated tokens (`m_wordsem`) but NO local ID→gloss inventory — gold-scored WSD against MW senses is blocked until the inventory is recovered](#78-dcs-2026-sqlite-carries-531747-sense-annotated-tokens-m_wordsem-but-no-local-idgloss-inventory--gold-scored-wsd-against-mw-senses-is-blocked-until-the-inventory-is-recovered) _(was §76, renumbered 12-07-2026 — duplicate key)_
- 🟠 [§82. MW `<e>` encodes the 1899 print's headword typography (1 = Devanāgarī entry, 2 = roman-only, 3 = run-on compound; letter suffix = continuation record)](#82-mw-e-encodes-the-1899-prints-headword-typography-1--devanāgarī-entry-2--roman-only-3--run-on-compound-letter-suffix--continuation-record)

---

## Grammar & morphology data

### §1. Whitney accent-mobility rules are machine-encodable

🟠 **Whitney's Grammar already carries machine-encodable per-case ACCENT-MOBILITY rules — the
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
**Status 02-07-2026: the encoding is DONE** — Fable 5 (`claude-fable-5`) formalized the rules as
[`crosswalk/accent_rules.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json)
(18 rules, 19-cell matrix, 16 lexical exceptions, recorded calls D1–D11) with a Sonnet-runnable
[validation spec](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_SPEC.md);
only the validation run + the a–f emission remain. One contradiction found → §42.
**Status 03-07-2026: the validation run is DONE** — 17 of 19 matrix cells GO (≥90% position
accuracy) against attested VedaWeb 2.0 RV forms, 0 NO-GO → §54. The ZALIZNYAK_INDEX a–f
emission is cleared on all 17 GO cells.

> **Source:** [`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)
> §"Vedic accent mobility" + `WhitneyRoots/src/whitney_sections.json` §§315–319 — RussianTranslation · 2026-06-29

### §2. Homonym token-splitting has a hard morphological ceiling

🟠 **Only 5 of 38 DCS-lumped root-homonym groups are gaṇa-splittable — the other 33 share a
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

> **Source:** [WhitneyRoots `.ai_state.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/.ai_state.md)
> §token-level disambiguation + `crosswalk/token_attribution.json` — WhitneyRoots · 2026-06-14

### §3. The Warnemyr scrape union-smears homonym classes

🟠 **The local Whitney root-class files (HTTrack scrape of lexicon.warnemyr.com) merge homonyms'
present classes into one value — per-homonym class must come from the live paradigm pages.**
Evidence: `2 √as` "throw" shows class II locally but is IV (*ásyati*); all three `√kṛ` show VI
though "make" is VIII; `kḷp` (#114) shows `—`/`—` but is class I with PPP `kḷptá`. Phase 0
re-parsed the full local Warnemyr mirror (939 paradigm pages; 930 roots keyed) and derives
per-homonym class from the full paradigm + period tags (V/B/S/E/C), keyed by the `{sense → URL}`
map; Warnemyr's `ROMAN ?` uncertainty is kept in a separate `class_uncertain` field (35 roots),
never in the asserted class.
Implication: never read verb class from `Whitney_roots_class-PP.txt` / old `app_data.json`;
treat any single-valued class on a homonym root as suspect union-smear and re-derive.

> **Source:** [WhitneyRoots `DESIGN.md` §5](https://github.com/gasyoun/WhitneyRoots/blob/main/DESIGN.md)
> + `.ai_state.md` §Phase 0 — WhitneyRoots · 2026-06-13

### §4. PWG nominal grammar compresses into 335 paradigm tokens

🟡 **98,639 of PWG's 123,366 entries carry enough `<lex>` gender/POS signal to be indexed into
just 335 Zaliznyak-style paradigm tokens.**
Evidence: reverse index over all PWG entries → 98,639 indexed (24,727 cross-refs / bare forms
skipped), 335 distinct tokens of the form `G·T S F` (e.g. `m·1b` = masculine a-stem oxytone);
top tokens `m·1+2` 12,681, `m·1` 11,496, `mfn·1` 8,346. Flag rates: `+N` compound 47.3 %
(MW 44.5 %), `*` gradation 3.6 %, `°` deviation 0.04 %.
Implication: a compact per-word grammar token is feasible for the whole dictionary and is kept
as **structured data only** — a blind A/B (Opus judge, 8 stratified headwords: grammar-OFF 5 /
tie 2 / ON 1) showed injecting it does NOT improve DE→RU translation, so portraits stay untouched.

> **Source:** [`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)
> (+ `src/headword_index.tsv`, `src/reverse_paradigm_index.json`) — RussianTranslation · 2026-06-29

### §42. Whitney self-contradicts on derivative ī-stem gen.pl accent

🟠 **Whitney's Grammar gives THREE mutually incompatible answers for the genitive-plural accent of
derivative oxytone ī/ū-stems — the cell must be encoded as a per-lemma variant, never a rule.**
Evidence (all read verbatim from the ingested `WhitneyRoots/src/whitney_sections.json` during the
02-07-2026 accent-axis encoding): **§320** — derivative long-vowel stems behave like short-vowel
stems "save that the tone is not thrown forward upon the ending in gen. plural"; **§319a** — "In
RV., even derivative ī-stems show usually the same shift: thus, bahvīnā́m"; **§356** — Whitney's
own Vedic paradigm prints `rathī́nām, nadī́nām, tanū́nām` (no shift). The rest of the accent system
encoded cleanly: 18 rules, only this one cell is internally contradictory.
Implication: any accent generator must treat derivative ī/ū gen.pl as free variation pending
corpus adjudication — the [ACCENT_VALIDATION_SPEC](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_SPEC.md)
marks it a measurement target (report the empirical `-īnā́m` vs `-ī́nām` split by lemma type,
adjective bahvī́-type vs noun nadī́-type). Do not "fix" the disagreement by picking a side.

> **Source:** [`crosswalk/accent_rules.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json)
> R13/D3 (+ R14) — WhitneyRoots · 2026-07-02, Fable 5 (`claude-fable-5`)

### §54. Whitney accent axis validates at 17/19 matrix cells GO against attested RV accents

🟠 **Whitney's formal accent-in-declension table (18 rules, 19 matrix cells) predicts attested
Rig-Veda accent POSITION correctly for 18 of 19 matrix cells at ≥90% accuracy, 0 cells NO-GO —
the ZALIZNYAK_INDEX a–f axis is cleared to proceed on the 18 GO cells.**
Evidence: scored [`crosswalk/accent_rules.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json)
against attested accented RV forms from VedaWeb 2.0 + Casaretto et al. (2025), joined on PWG
`key2` udātta positions (`RussianTranslation/src/headword_index.tsv`), per the method in
[`ACCENT_VALIDATION_SPEC.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_SPEC.md).
Originally 17/19 GO (12 unconditional + 3 low-confidence-per-spec-but-clean at 96.9–100%) + 1
GO-with-exceptions (`T8c·oxytone`, 82%). A mid-run scoring bug was caught and fixed: 9 of the 19
cells define case/number-specific `per_case` overrides (`G.pl`, `N.A.du.n`) that the first pass
silently ignored in favor of the generic strong/middle/weakest slot value, which had zeroed the
D3 genitive-plural split (§42) entirely (0 observations before the fix).
**Update 05-07-2026 (H115, Sonnet 5):** the `T8c·oxytone`/`samyaYc` exception was resolved as a
genuine rule gap, not lexical noise — Whitney §407b + §409b/c + §410 (read in full) show
pratyáñc-type añc-compounds (`samyáñc`, `anváñc`, `śvityáñc`, among others) shift accent to the
ending under ī/ū contraction, and §407b's "the feminine is made by adding ī to the stem-form
used in the weakest cases, and is accented like them" means the feminine declension inherits
this in ANY case/number, not just the cell's `weakest` per_case slot. `T8c·oxytone` 82.0%→100.0%,
`R10` rollup 95.6%→100.0%; **18/19 cells now GO**, 1 still measurement-only
(`T2·monosyllable`/`T4/T6·monosyllable`, 0–1 attested lemmas, expected per spec). The D3 split
(`-īnā́m` ending vs `-ī́nām` stem_final) was also relabeled: the 2 attested forms (`raTI`, `vaDU`)
were mislabeled `ending` in the original run but actually carry the accent on the ī/ū vowel
itself — the `stem_final` (§356, noun-type) pattern, not `ending` (§319a, bahvī́-type adjective).
A wider VedaWeb pull to grow n past 2 was attempted but blocked mid-run by a
`vedaweb.uni-koeln.de` outage (see
[Uprava/SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)); n
remains 2 — **still too thin to resolve Whitney's own §319a/§356 self-contradiction**, and now
directional (weakly) toward `stem_final` rather than `ending`.
Implication: 18 GO cells now drive the ZALIZNYAK_INDEX a–f emission. The D3 split still needs a
wider VedaWeb pull (blocked by the host outage, resume per SERVER_OUTAGES.md) before it can move
past measurement-only. Whitelisted-exception forms (138 in this sample) are currently excluded
from the scored denominator rather than scored against their own stated behavior — a known
pipeline simplification, not yet a defect fix.

> **Source:** [`crosswalk/accent_validation.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_validation.json) /
> [`docs/ACCENT_VALIDATION_REPORT.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_REPORT.md)
> — WhitneyRoots v1.3.0 · 2026-07-05, Sonnet 5 (`claude-sonnet-5`) (originally v1.2.0 ·
> 2026-07-03)

### §63. vidyut dhātupāṭha adjudicates the 2014 Palsule-exclusion dispute: five añc dhātus, no and, but ast IS Paninian

The 2014 defense review (Krylov, ведущая организация) charged that the Gasūns
concordance drops roots absent from Palsule (e.g. `4añc`, present in Pāṇini) while
keeping Palsule-only roots (`2and`, `ast`). The machine-readable vidyut dhātupāṭha
(2 259 dhātu) settles each case: **five** añc-family entries exist (`01.0215 ancu~
gatipUjanayoH`; `01.0998 ancu~^` / `01.0999 acu~^` / `01.1000 aci~^` all `gatO
yAcane ca`; `10.0266 ancu~ viSezaRe`) → the dropped `4añc` is real and recoverable;
no `and-` dhātu exists → `2and` confirmed Palsule-only; **but `asta~ saNGAte`
(10.0169, curādi) IS in the Paninian dhātupāṭha** — Krylov's second example was
itself imprecise. Gotcha for anyone grepping vidyut: the file lists añc
denasalized-ish as `ancu`, NOT SLP1 `aYc` (`aYc` appears only inside meaning
glosses like `saYcalane`), and anubandha marks `~ \ ^` must be stripped before
matching. Full-sweep method (concordance exclusions × vidyut × Whitney) outlined in
[GasunsDhatu_2014/revision-2026/PALSULE_AUDIT.md](https://github.com/gasyoun/SanskritGrammar/blob/chore/errata-kochergina-waiting/GasunsDhatu_2014/revision-2026/PALSULE_AUDIT.md).

> **Source:** H246 print-prep session ([SanskritGrammar PR #29](https://github.com/gasyoun/SanskritGrammar/pull/29)),
> Fable 5 `claude-fable-5` · 2026-07-07

## Corpus & parallel-text data

### §5. The parallel corpus rarely attests prefixed-verb forms

🟠 **The parallel corpus rarely attests prefixed-verb surface forms.**
Evidence: of √man's 15 prefixed forms, only **3** (`anuman`, `abhiman`, `avaman`) appear in
the SamudraManthanam parallel corpus; the `pwg_preverb1.txt` sandhi-join produces the *same*
surface strings as a naïve `upasarga+root` concat, so spelling is not the limiter — the
corpus simply lemmatises prefixed verbs to the root or lacks them.
Implication: prefix-specific Apresjan evidence is corpus-bound; for the ~80 % that miss,
defer to the dictionary's own (German) gloss. Do **not** build a sandhi-join lookup
expecting coverage gains — it's a no-op.

> **Source:** code [`subcard_portrait()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py#L237)
> · statement [FREQ_TEST_RUNBOOK.md § Apresjan evidence](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/FREQ_TEST_RUNBOOK.md). — SanskritLexicography/RussianTranslation · 2026-06-24

### §6. No printed frequency dictionary of Sanskrit exists

🟠 **No printed frequency dictionary of Sanskrit exists.**
Evidence: absent from the prefaces and literature of PWG/PW/MW/GRA/AP90 and from Kochergina;
only Hellwig's DCS corpus counts (≈2021) give per-lemma frequency.
Implication: DCS-frequency headword ordering is a genuine innovation, not a digitisation of
prior art.

> **Source:** [A33 note § 1 "The question"](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md). — SanskritLexicography (A33) · 2026-06-24

### §7. DCS lemma data is keyed in two transliterations

🔴 **DCS lemma data is keyed in two different transliterations.**
Evidence: `VisualDCS/dcs_lemma_summary.json` (`lemmas`, freqBand 1–5) is **SLP1**-keyed
(joins PWG `key1` natively); `RussianTranslation/src/dcs_lemma_renou.json` (breadth `n_texts`,
dates) is **IAST**-keyed.
Implication: a freq join must transcode SLP1↔IAST for the second; don't assume one scheme.

> **Source:** [`freq_route.py` header (lines 7–8) + `iast()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/freq_route.py#L7-L8). — VisualDCS / RussianTranslation · 2026-06-24

### §8. Unaccented DCS cannot distinguish present class I from VI

🔴 **The unaccented DCS corpus cannot distinguish present class I from VI (or IV from passive).**
Evidence: WhitneyRoots — the corpus carries no pitch accent, and the class distinction rests
on it: class I (`cárati`, guṇa + root accent) and class VI (`tudáti`, weak root + accented `-á`)
have identical surface present-stems where guṇa doesn't change the vowel. A corpus-derived
class pass produced **117 spurious I/VI additions — all reverted** (120 unsound additions
total, vs 19 kept distinct-class ones).
Implication: never write a corpus-derived verb class into reviewed data without a grammar /
Zaliznyak cross-check.

> **Source:** [WhitneyRoots `REVIEWER_GUIDE.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md)
> + [`CHANGELOG.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/CHANGELOG.md) (revert of 120). — WhitneyRoots · 2026-06

### §9. DCS OccId and sent_id are not unique keys

🔴 **DCS CoNLL-U `OccId` and `sent_id` are non-unique — using either as a primary key silently
drops data.**
Evidence: the corpus reuses `OccId` across a line's sub-sentences — the M5 pilot build over 13
texts (134,047 tokens total) lost ~20 tokens to PK collisions until the key was replaced;
`sent_id` collides *within* a single chapter — the M6 full build (270 texts) dropped
**449 sentences** before the fix. Both resolved with synthetic autoincrement PKs; cross-vintage
validation is position-based (i-th sentence per text), and 754,726 sentences then cross-walk
with 0 mismatches.
Implication: never key on `OccId`/`sent_id`; use synthetic surrogates or position-within-text.
The stable cross-corpus key is `LemmaId`.

> **Source:** [`DCS_CONLLU_IMPORT_PLAN.md` §M5–M6](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/DCS_CONLLU_IMPORT_PLAN.md)
> + `reports/m5_validation.md` / `m6_validation.md` — VisualDCS · 2026-06-06

### §10. DCS UD tense marking conflates aorist and perfect

🟠 **UD `Tense=Past` in DCS CoNLL-U conflates aorist and perfect — the distinction exists only in
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

> **Source:** [`reports/m7_widgets.md` §Caveats](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/m7_widgets.md)
> + `reports/m4_exports.md` §verb code map — VisualDCS · 2026-06-06

### §11. DCS 2021 and 2026 vintages are not directly comparable

🟠 **DCS 2021 and 2026 differ structurally — one 2021 metrical line maps to several 2026 CoNLL-U
sentences, the corpus grew ~10 %, and dependency trees exist for only 74 of 270 texts.**
Evidence: sentence counts diverge while tokens stay flat (Hitopadeśa 718 → 3,432 sentences,
tokens 24,958 → 25,040; Gītagovinda 428 → 692, tokens identical). Texts 246 → 270 (+24, mostly
Vedic Śrautasūtra/Brāhmaṇa additions); lemma Jaccard overlap **89.3 %** (89,645 shared / 100,367
union). Only **74/270 texts** (27 %) carry `HEAD`/`DEPREL` dependency annotation (Vedic Treebank
chapters); the rest are morphology-only.
Implication: never compare sentence-level metrics across vintages — use token-level or
position-based crosswalks; filter to `text.has_dependencies` for syntax work; weight diachronic
frequency comparisons by text coverage.

> **Source:** [`reports/coverage_diff.md`](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/coverage_diff.md)
> + `reports/m6_validation.md` — VisualDCS · 2026-06-06

**Addendum (12-07-2026) — three annotation layers, and the semantic layer is NOT the Vedic wave.**
A per-text census of all 270 CoNLL-U folders (VisualDCS
[`delta_annotation_layers.py`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/delta_annotation_layers.py)
→ [`annotation_layers_by_text.csv`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/annotation_layers_by_text.csv))
separates the three orthogonal annotation layers: **`WordSem`** (lexical semantic-concept IDs →
Sanskrit WordNet) on **219/270** texts — *corpus-wide, NOT Vedic-selective*; **Vedic Treebank**
(`HEAD`/`DEPREL`) on **74**; **`IsMantra`** (Bloomfield's Vedic Concordance) on **44** — the latter
two are the Vedic-selective layers. Sharp result: **29 of the 30 only-2026 ("went Vedic") texts
arrived with ZERO `WordSem`** — sole exception Atharvaveda (Paippalāda), 6,403 semantic tokens. So
the +24 % Vedic wave added raw tokens *without* the semantic layer; the `WordSem` layer is an
old-corpus asset. Implication: never assume the new Vedic tokens are WordNet-linked — they are not;
filter on the `WordSem`/`IsMantra` MISC keys + `HEAD` column per text. Full interpretation:
[`DRIFT_INTERPRETATION.md` §3b](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/DRIFT_INTERPRETATION.md)
(H686 supplement, [PR #41](https://github.com/gasyoun/VisualDCS/pull/41)).

### §12. A fifth of DCS lemmas have no CDSL headword

🟠 **18.6 % of DCS-2026 lemmas do not map to any CDSL headword — corpus vocabulary exceeds the
historical dictionaries' headword set.**
Evidence: of 15,902 DCS IAST lemmas, 12,946 (**81.4 %**) link to CDSL normalized keys; 2,956
are corpus-only (lemmatization targets, causatives, derived forms). Crosswalk built by
`build_xref.py` (reusing the transcoder from `wf1/build_wf_from_dcs.py`); frequency map
`wf0/wf.txt` (50,474 keys) → `wf1/wf.txt` (50,574).
Implication: dictionary-lookup pipelines need a lemmatization / sandhi-analysis fallback for
roughly a fifth of corpus vocabulary — headword joins alone will not reach it.

> **Source:** [csl-apidev `simple-search/dcs_xref/readme.md`](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/dcs_xref/readme.md)
> + `.ai_state.md` §DCS-2026 frequency source — csl-apidev · 2026-06-11

### §13. Sa-Ru glossary token coverage plateaus at 86.6 percent

🟡 **The Sa→Ru glossary resolves 86.6 % of the 1,091,528 aligned corpus tokens via DCS form→lemma
plus a vidyut.kosha fallback — the unresolved 41 % of FORMS is only 12.9 % of TOKENS.**
Evidence: coverage ladder — DCS morphology alone 79.1 % (80,949 forms, 42.4 %); + vidyut
fallback **86.6 %** (109,516 forms, 57.4 %); + morpheme-marker recovery 87.1 %. Unresolved:
78,842 forms (41.3 % of forms, 12.9 % token weight) — the rare long tail.
Implication: DCS + vidyut is the workhorse pair for form→lemma resolution; do not chase
form-level completeness — the residue is rare forms with little token mass. (Bulk glossary
data is git-ignored and regenerable.)

> **Source:** [`glossary/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossary/README.md)
> (built from `corpus_lexicon.jsonl`) — RussianTranslation · 2026-07-01

### §14. Renou period-state tagging covers 770k entries in 8 dicts

🟠 **Multi-signal Renou I–V period-state tagging covers 770,292 entries across 8 dictionaries —
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

> **Source:** [`RENOU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md)
> (built by `renou_pipeline.py --all`, validated by `renou_audit.py`) — RussianTranslation · 2026-07-01

### §62. Varga distribution is almost epoch-stable (Cramér's V = 0.037) — and the Gasūns-2014 dissertation prose read its own χ² table backwards

Aggregating the 25 sparśa varṇas of DCS (pin 2026-03-05; 9 940 591 stop/nasal varṇas
across time slots 1–5) into the 5 vargas gives per-epoch shares that barely move:
dentals ≈ 47–52 %, labials ≈ 24–27 %, gutturals 8.9 → 14.9 %, palatals ≈ 8–9 %,
cerebrals 4.5 → 5.9 %. Effect size for the 5×5 varga × epoch table: **Cramér's V =
0.0372** (χ² = 54 890) — on such N nearly everything is "significant", so p-values
carry no signal; the only real shifts are the dental drop Vedic→epic (−4.2 pp) and
the guttural climb through medieval (+6.0 pp total). Bonus forensic finding: the
2014 Gasūns dissertation prose (§2.6 / положение 9) systematically labels as
«набирающие популярность» exactly the vargas whose pairwise-χ² p-values were LARGE
(labials 0.26 / cerebrals 0.32 for epic; palatals 0.95 for medieval; labials 0.66
for late) — i.e. the statistically *unchanged* ones; apparently high p was read as
growth. The 2026 shares agree with the 2014 p-table **against** the 2014 prose.
Reproducible: [SanskritGrammar/GasunsDhatu_2014/revision-2026/varga_shares.py](https://github.com/gasyoun/SanskritGrammar/blob/chore/errata-kochergina-waiting/GasunsDhatu_2014/revision-2026/varga_shares.py)
over [VisualDCS derived-data/Fonetika/regen-2026/varna_freq.csv](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Fonetika/regen-2026/varna_freq.csv).

> **Source:** H246 print-prep session ([SanskritGrammar PR #29](https://github.com/gasyoun/SanskritGrammar/pull/29)),
> Fable 5 `claude-fable-5` · 2026-07-07

### §65. 6.6 % of the DeepSeek corpus word-alignments ground to nothing in their verse

🟠 **One in fifteen DeepSeek L1 word-pairs does not trace back to its own verse.**
Evidence: [`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py)
cross-checks every one of the **1,091,528** `corpus_lexicon.jsonl` word-pairs against
the L0 verse it was extracted from (rebuilt by
[`src/build_l0.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_l0.py)
from the SamudraManthanam verse-aligned source — **99,733 L0 units over 116 works**):
mean grounding confidence **0.684**, **93.4 % grounded**, but **6.6 % score 0** — the
Sanskrit citation-word is absent from the verse *and* the Russian rendering's stems are
absent from the translation. Feeding this real `alignment_confidence` into
[`tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py)
(vs the Slice-2 token-count proxy) moves publication-grade **A 5.7 % → 5.3 %** and
usage-only **C 0.3 % → 0.9 %** — the ungrounded pairs correctly demote.
Implication: a reference-free QE/consensus grade over DeepSeek alignments should carry a
grounding cross-check; the ungrounded 6.6 % are the first place to look for the
never-invent failure mode at the word-pair layer. A real embedding aligner (`embed`,
mBERT — ran on a Vedic sample) is weak on *transliterated* Sanskrit and needs XLM-R / a
Sanskrit-aware encoder before it beats the deterministic grounding proxy.

> **Source:** H215 Slice 3 ([`src/BUILD_TMX.md` § L0 + alignment](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/BUILD_TMX.md)),
> Opus 4.8 `claude-opus-4-8` · 2026-07-07

## Dictionary structure & markup

### §15. PWG encodes secondary stems inline, not in div markup

🟠 **PWG never uses `<div n="m">`; secondary stems are encoded inline.**
Evidence: 0 occurrences of `<div n="m">` in `csl-orig/v02/pwg/pwg.txt`; causative/desiderative/
intensive/participle/passive of the simple root appear as `<div n="p">— <ab>caus.</ab> {#…#}`
(a `<div n="p">` whose first token is an `<ab>` label, not a `{#upasarga#}`).
Implication: a secondary-stem segmenter keys on the inline `<ab>` label
(`SEC_DIVP_RE` + a caus/desid/intens/partic/pass/insens label set), not on `<div n="m">`.

> **Source:** code [`SEC_DIVP_RE` + the comment](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/root_segment_proto.py#L28-L34)
> · measured by [`verify_root_glue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/verify_root_glue.py) (570 split, 0 merged). — csl-orig (pwg) / RussianTranslation · 2026-06-24

### §16. Giant verb roots sit at non-zero homonym indexes

🔴 **A headword's giant verb root often sits at a non-zero homonym index.**
Evidence: √i has its 114-prefix verb root at homonym **2** (homonym 0 is the particle);
√mā at index 2, √As at index 1; 19 of the top-50 freq roots have a giant homonym at
index > 0 or more than one giant homonym. Full-population census (H702 re-test, 12-07-2026,
Fable 5 `claude-fable-5`, all 749 DCS-attested verb roots): 236 roots carry ≥1 giant homonym
(≥8 prefix divisions); **55 of them (23.3%) hold a giant at index > 0**, and 23 have NO giant
at index 0 at all — a bare `bufs[0]` read finds nothing there (e.g. As@[1], Sam@[1,3],
iz@[1,3], DA@[0,6,10]).
Implication: any per-record split / processing must iterate **all** homonym records, not
`bufs[0]`, or it silently misses the verb (or drops extra giant homonyms).

> **Source:** code [`gen_root_split()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py#L258)
> · audited by [`audit_root_split.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_root_split.py). — csl-orig (pwg) / RussianTranslation · 2026-06-24

### §17. PWG orders senses genetically, not historically

🔴 **PWG orders senses genetically (etymological core first), not historically.**
Evidence: across 13,900 multi-sense entries, printed sense-1 is the oldest-attested only
**73.5 %** of the time; Kendall τ(printed vs date) = **0.375**; citations *within* a sense run
old→new in 76 % of adjacent pairs but are strictly sorted in only 26 %.
Implication: don't auto-re-sort senses by date or frequency (it changes the lead sense for
~1 in 4 entries and fights the source); surface attestation era as per-sense metadata instead.

> **Source:** [`sense_order_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sense_order_metrics.md)
> · [`analyze_sense_order.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_sense_order.py). — SanskritLexicography (A33) · 2026-06-24

### §18. Vedic-citation density separates the dictionary traditions

🟠 **Vedic-citation density cleanly separates the dictionary traditions.**
Evidence: fraction of cited senses reaching a Vedic source — **PWG 23.4 % ≈ MW 24.8 % ≫
AP90 2.3 % ≫ Kochergina 0 %**.
Implication: PWG/MW are etymological-genetic with a real historical apparatus; Apte and
Kochergina are logical-semantic / pedagogical — do not import their sense order into a PWG
translation.

> **Source:** [`cross_dict_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/cross_dict_metrics.md)
> · [`analyze_cross_dict.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_cross_dict.py). — SanskritLexicography (A33 cross-dict) · 2026-06-24

### §19. SKD and VCP carry essentially zero Western markup

🔴 **SKD and VCP carry essentially zero Western markup.**
Evidence: ~0 `<ab>`/`<div>`/`<s>`/`<ls>` tags; citations appear via `iti`/quotes, verbs via
`dhātuḥ`/`preraṇe`/`bhvādi`.
Implication: any marker-based detector scores SKD/VCP at 0 *by construction* — never read 0
as "no content"; use the indigenous cues. (Miscalled ≥4×.)

> **Source:** data [`v02/skd/skd.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/skd/skd.txt)
> · [`v02/vcp/vcp.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/vcp/vcp.txt) (grep: no `<ab>`/`<div>`). — SKD / VCP (csl-orig) · 2026-06

### §20. The ls source map recognises 72.4 percent of PWG citations

🟠 **`ls_source_map.json` recognises 72.4 % of PWG's `<ls>` citations.**
Evidence: 559,243 of 772,567 `<ls>` keys map to one of 45 dated primary sources
(range −1125 → 1830); the unrecognised 27.6 % is catalogues / secondary literature
(Aufrecht's Oxford catalogue, *Indische Studien*, *Indische Sprüche*), which skews *late*.
Implication: dated-citation analyses see the most-cited primary corpus and are conservative
about the oldest stratum, not biased toward it.

> **Source:** [`sense_order_metrics.md` § "Foundations check"](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sense_order_metrics.md)
> · [`analyze_sense_order.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_sense_order.py). — RussianTranslation · 2026-06-24

### §21. PWG citation occurrences track distinct references

🟡 **PWG `<ls>` citation usage frequency ≈ distinct-reference frequency — HTML-target works are
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

> **Source:** [`build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py)
> → [`UNCOVERED_SOURCES.md`](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/UNCOVERED_SOURCES.md)
> + [`CITATION_SOURCES.md`](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/CITATION_SOURCES.md) — SanskritLexicography · 2026-07-02

### §22. MW has no sense-level div markup

🟠 **MW has no sense-level `<div>`; the sense unit is the record itself.**
Evidence: `csl-orig/v02/mw/mw.txt` carries **0** `<div n="m">` and only **4** `<div n="p">` across
**286,526** `<L>` records — MW essentially never subdivides an entry by sense in markup (senses are
separated by `¦` inside the single record body).
Implication: a sense-segmenter for MW must split on `¦` inside the record, not on `<div>`; and do
**not** template MW's flat structure onto subentry-rich dicts (PWG/Apte) or vice-versa — `<div>` depth
is structural, not a sense boundary, so it over-counts senses.

> **Source:** measured `grep -c '<div n="m"' / '<L>'` on
> [`v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt). — csl-orig (mw) · 2026-06-26

### §23. Apte is three dictionaries; keys differ stem vs nominative

🔴 **"Apte" is three distinct dictionaries, and the same lemma keys differently across dicts
(stem vs nominative).**
Evidence: AP90 (Apte 1890), AP (Apte Revised 1957–59), and AE/ApteES (reverse English→Sanskrit Apte)
are separate `csl-orig` dicts with different markup (AP90 uses `∙²` sense markers, numeric `<pc>0002-1`
page-cols, `{%<lex>a.</lex>%}` labels). The same headword also keys differently *between* dictionaries —
MW stores the bare stem `agni`, Apte the nominative `agniH` — so a cross-dict join on the raw key
silently misses matches (independently re-hit in csl-guides and csl-apidev).
Implication: never treat "Apte" as one source — pick AP90 / AP / AE explicitly. For any cross-dict
headword join, normalise stem↔nominative and join on the `key1` computational key, not `key2`/printed form.

> **Source:** csl-guides/.ai_state.md + csl-apidev/.ai_state.md (the `agni`/`agniH` resolver note); markup per
> [`v02/ap90/ap90.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90.txt). — csl-guides / csl-apidev / csl-orig · 2026-06

### §24. About 9 percent of typo corrections are collisions

🔴 **~9 % of "typo" headword corrections in the early dictionaries are really COLLISIONS — the
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

> **Source:** [`VERIFICATION_2026_07.md`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/corrections_draft/VERIFICATION_2026_07.md) — SanskritSpellCheck · 2026-07

### §25. A verified correction queue decays against live csl-orig

🟠 **A verified correction queue DECAYS against the live `csl-orig` — upstream fixes land between
triage and filing.**
Evidence: 1 of 122 FILE-FIRST candidates (`SHS kARqapfzwa→kARqapfzWa`, triaged June 2026) was
already fixed upstream by 02-07-2026 — the correct form exists as its own entry (id 9855), the
wrong form is gone. ~1 week of queue age ≈ 0.8 % decay on this batch.
Implication: re-verify every candidate against the current `csl-orig` immediately before filing
or applying; a stale row filed upstream reads as bot noise to the maintainers.

> **Source:** [`file_first_verified.tsv`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/corrections_draft/file_first_verified.tsv) (SHS DROP row) — SanskritSpellCheck · 2026-07

### §26. Citation density is register-bound, not comparable raw

🟠 **Per-entry citation density is register-bound — PWG carries 4.61 `<ls>` per entry vs MW's 1.09,
while the indigenous dicts' citations live in the `iti` register that `<ls>` counting misses
entirely.**
Evidence (2026-07 regeneration from the committed artifact
[`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json)):
PWG 568,730 `<ls>` at **4.61/entry** vs MW 312,160 at **1.09/entry**. SKD carries
**80,164 `iti`-citations** (1.88/entry), VCP 15,619 (0.31), KRM 12,359 (**6.00/entry**, densest
in the corpus) — all scoring zero under an `<ls>` detector; 28 of 44 csl-orig dicts have no
`<ls>` at all.
**Counting-rule trap (measured 2026-07):** an `iti` counter whose word boundary is
"preceded by space or quote" misses quotatives that sit directly after markup — KRM wraps
Sanskrit in `<s>…</s>`, so `<s>iti` hid **~2/3 of its 12,359 citations** (rule saw 4,265) and
the pre-2026-07 published triple (SKD 69,215 / VCP 22,070 / KRM 6,449) was additionally stale
against upstream csl-orig fixes. Use "not adjacent to a Latin letter" as the boundary.
Implication: never rank dictionaries by raw `<ls>` density — control for citation register
first, or indigenous lexica are misranked as citation-poor when they are among the richest.
(Generalises the SKD/VCP zero-markup trap to *quantitative* comparisons.)

> **Source:** [csl-atlas `docs/articles/paper_citation_registers.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md) + [csl-atlas PR #187](https://github.com/sanskrit-lexicon/csl-atlas/pull/187) — csl-atlas · 2026-06-13, rev. 2026-07-02

### §27. Sense granularity is a family trait, not a diachronic trend

🟠 **Sense granularity is a lexicographic-school trait, not a diachronic trend — the 1822–1957
trend is flat (r = 0.036) while family means span ~1.0–2.4 senses/entry.**
Evidence: across 11 dicts, family means — Benfey 2.42, Apte 2.12, MW 2.00, Wilson 1.71,
Cappeller 1.36, Petersburg 1.13, indigenous ≈1.00 units/entry; correlation with publication
year r = 0.036. (An earlier run in `docs/R2_FINDINGS.md` gives slightly different values —
r = 0.06, Benfey 2.53 — the paper's numbers are the canonical run.)
Implication: any cross-dict measure normalised "per sense" (definition length, citation
density) silently encodes school bias unless family-controlled; never read sense counts as
lexicographic "progress".

> **Source:** [csl-atlas `docs/articles/paper_sense_inheritance.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md) — csl-atlas · 2026-06-15

### §28. MW inherited the PWG apparatus skeleton, not its prose

🟠 **MW reproduces PWG's citation ORDER (0.81 concordance, 47.8 % of sequences identical) but not
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

> **Source:** [csl-atlas `scripts/forensic/f5_entry_comparison.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f5_entry_comparison.py)
> + [`docs/articles/article_21_apparatus_not_errors.md` §3.4](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) — csl-atlas · 2026-06-03

### §29. PWG and MW share 94,753 headwords in the union index

🟠 **The cross-dict union index already answers headword-overlap questions — PWG∩MW = 94,753
(89 % of PWG-bearing keys are also in MW); don't rebuild it.**
Evidence: `HeadwordLists/union/union_headwords.tsv` — 323,425 union headwords over 15 dicts,
SLP1-keyed with per-dict membership + gender; PWG-bearing 106,054, MW-bearing 193,852,
both 94,753.
Implication: consume this asset for any cross-dict join or coverage estimate (the PWG→EN
pilot's MW translation-memory rides on it); a new pairwise-overlap script is reinvention.

> **Source:** [`HeadwordLists/union/union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) — SanskritLexicography · 2026-06-26

### §30. Body-text headword mining is a dead end (38.6 percent precision)

🔴 **Mining "hidden" headwords from dictionary bodies / reverse dicts yields only 38.6 % precision
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

> **Source:** csl-atlas broad-headword review session (xhigh /code-review, 2026-06-15), context
> [PR #99](https://github.com/sanskrit-lexicon/csl-atlas/pull/99); index scale per
> [`docs/BROAD_HEADWORD_COVERAGE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BROAD_HEADWORD_COVERAGE.md) — csl-atlas · 2026-06-15

### §31. Detector precision stratifies by digitization quality

🟠 **Spell-detector tier-A precision stratifies by digitization quality, not dictionary age —
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

> **Source:** [SanskritSpellCheck `corrections_draft/README.md`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/corrections_draft/README.md)
> + [`nochange/do_not_file_suppress.txt`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/nochange/do_not_file_suppress.txt) — SanskritSpellCheck · 2026-06-24

### §32. Correction events concentrate in sense text

🟡 **Twelve years of Cologne corrections concentrate in sense text — 52.7 % sense vs 17.5 % markup
vs 17.3 % headword over the 33,755 derived-label events — and error profiles are location- and
dict-specific.**
Evidence: of 52,498 correction events across 43 dicts (2014–2026), the 33,755 with derived
location labels split: sense 17,778 (52.7 %), markup 5,902 (17.5 %), headword 5,823 (17.3 %),
citation 3,335 (9.9 %); top phonetic confusion b→v (341); per-dict correction density spans
PGN 160/1k entries down to BOP 45.5/1k.
Implication: "surface error" claims must specify the microstructure location — the global
minor-edit rate masks that headword repairs are structural while sense repairs are often tiny
diacritic fixes; markup errors are a real 17.5 % class, not noise.

> **Source:** [csl-observatory `reports/obs_t_typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md)
> (Axis A table) — csl-observatory · 2026-06-17

### §46. Twelve years of corrections cover only ~10–14 % of the estimated error population

🟠 **The two CDSL correction eras (2014–2019 web form; 2019–2026 git) touch nearly disjoint
record sets, and under Chapman mark–recapture that near-disjointness implies the corrected
records are a small minority of the error-prone population: PW ~78k error-prone records
(~14 % corrected), MW ~65k (~10 %), BUR saturates its entire 19,776 records (~8 %).**
Evidence: of 40,234 observed error sites (dict + headword) across 43 dicts, only PW (m=169),
MW (m=105) and BUR (m=23) have ≥10 two-era recaptures — 40 dictionaries cannot be estimated
at all; estimates are capped at csl-orig `<L>` record counts, and the Chao heterogeneity
scenario pushes the totals toward the full dictionary.
Implication: correction-campaign planning should assume the work is mostly ahead, not mostly
done; any "quality is converging" claim from correction-volume decline confuses effort decay
with error exhaustion. Order-of-magnitude only — sequential eras bias the estimate up,
correlated corrector attention biases it down.

> **Source:** [csl-observatory `reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md)
> (Chapman/Chao tables + sensitivity) — csl-observatory · 2026-07-03 · paper track A48

### §64. PW-only headwords outnumber PWG-only ones 6-to-1 — PWG is not the sole spine of the local layer universe

🔴 **A direct co-occurrence tally over the 4 local pwg_ru merge layers (PWG/PW/SCH/PWKVN) shows
PWG does not define the headword universe by itself — PW alone covers 40,338 headwords
(24.0% of the union) that have no PWG record at all, roughly 6× the 6,453 PWG-only headwords.**
Evidence: unioned `index('pwg')`/`index('pw')`/`index('sch')`/`index('pwkvn')` from
`RussianTranslation/src/dict_merge.py` over the full local layer set (167,988 headwords total).
No-PWG combinations: `pw`-only 40,338 (24.0%), `sch`-only 9,990 (5.9%), `pw+sch+pwkvn` 10,057
(6.0%), `pw+pwkvn` 875, `pw+sch` 624, `pwkvn`-only 20, `sch+pwkvn` 2 — **61,906 headwords
(36.9% of the local union) carry zero PWG record** (the "≈35,900" stated here until
12-07-2026 was an arithmetic slip: the listed combinations sum to 61,906; the tally was
re-run and reproduced combo-for-combo under H702, Fable 5 `claude-fable-5`). PWG-only is 6,453 (3.8%); the dominant
combination overall is `pwg+pw` at 91,648 (54.6%). Separately, of the 167,991 scraped NWS
JSON fragments, 34,101 (20.3%) are net-new (`has_nws_extra`) beyond all four local layers —
also far from a marginal contribution. Full breakdown + methodology:
[`PWG_LAYER_COMBINATIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md).
Implication: any pwg_ru worklist/queue builder that enumerates "headwords" by iterating PWG
records alone (as the verb-root worklist does today, via `verbs01`/PWG) will silently miss
roughly a third of the local-layer universe — PW/SCH/PWKVN-only entries need their own
explicit queue path, not incidental discovery through a PWG walk. This also reframes PW: it is
not merely a revision of existing PWG senses but an independent source of new headwords, which
matters for any "abridged tradition" retention-score analysis (don't assume PW ⊆ PWG's
headword set). NWS at 20.3% net-new means it must be budgeted as real translation volume in
cost/time forecasts, not treated as a rare bonus layer.

> **Source:** [`SanskritLexicography/PWG_LAYER_COMBINATIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md)
> (direct `dict_merge.py` index tally + NWS `has_nws_extra` scan) — SanskritLexicography · Sonnet 5 `claude-sonnet-5` · 2026-07-05

### §76. The MW→WordNet→semdom bridge is a candidate generator, not a classifier

🟠 **Automatic semdom assignment for Amarakosha synsets via MW glosses + WordNet + the
GWC-2023 bridge reaches only 17.5% top-1 exact precision (27.5% at level-2); even the full
top-6 candidate list contains the gold label under half the time (45.0% exact / 58.5%
level-2).** Measured on the 200-synset adjudicated gold sample of H742 (dual-annotated
blind, Fable 5 `claude-fable-5` × Opus 4.8 `claude-opus-4-8`, exact κ 0.677). Failure mode:
candidates key on incidental gloss words (mythological narrative, botanical Latin absent
from WordNet, polysemous English glosses) rather than the synset's concept. Both annotators
wrote in out-of-candidate codes for 42–56% of items, and voted NONE zero times — SIL's
1,792 domains have no coverage hole for the 6th-century material; the bridge, not the
taxonomy, is the weak link. Implication: never auto-assign `\sd` values from
[`data/semdom_ak_candidates.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_candidates.tsv)
without a review pass; treat it as a shortlist.

> **Source:** [`data/SEMDOM_AK_CROSSWALK_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md)
> (H742), Fable 5 `claude-fable-5` · 2026-07-11

### §447. PWG's own closing sense-marker glyph "〉" was never recognized by the sense-splitter — ~50% of German senses were silently merged into their first sub-sense

🔴 **`microstructure.py`'s `MARK` regex has never, in any git-history revision, recognized
`〉` (U+3009 RIGHT ANGLE BRACKET) as a sense-number/letter closing delimiter — only ASCII
`)` — even though `〉` is PWG's own standard notation for closing an inline sub-sense marker
("1〉", "a〉"), used **87,680 times** across `csl-orig/v02/pwg/pwg.txt`.** Every PWG record
whose sub-senses are marked this way therefore fell through `split_senses()` as a single
un-split segment.
Evidence: `_audit_micro.py` over the first 2500 PWG records — before the fix, senses
parsed = 2500 (exactly 1.0/card, every card capped at one sense); after adding `〉` to
`MARK`, senses parsed = 3738 (1.5/card), zero new anomalies (`cards with no real sense` and
`senses with no gloss+no cite` both stay 0), `<ls>` citation resolution 98.7% → 98.8%,
`<ab>` resolution unchanged at 100%. Surfaced via H879 (a 4-key `pwg_de_lexicon.ttl`
fixture drift: the committed fixture claimed 34 German senses at H772 merge time,
12-07-2026; a fresh rebuild the next day yielded only 22). The true, correct count for
those same 4 keys is **47** — `aMSa`/`aMSaka`/`rakz` match the 12-07 fixture exactly
(14/6/5); only lemma `a` (Sanskrit's single most grammatically overloaded lexeme —
interjection, negative prefix, augment, proper noun) jumps from the fixture's 9 to 22, all
independently verified as genuine distinct German glosses (e.g. `haarlos` "hairless" /
`mit wenig Haar versehen` "having little hair" / `nicht durch schönes Haar ausgezeichnet`
"not distinguished by beautiful hair" as three separate compound-sense entries), not split
artifacts.
Implication: the German PWG lexicon layer (`pwg_de_lexicon.ttl`, H772/H781) under-counted
senses by roughly a third across the entire ~120k-card corpus, not just these 4 keys.
`scale_route.py`'s `n_senses`-based complexity-routing heuristic (the only other caller of
`split_senses`/`sense_node`) was correspondingly under-informed and will now see generally
higher, more accurate counts — a quality improvement, not a regression; no pinned test
asserted the old counts. The core RU translation prompt-building path does **not** call
`split_senses`/`sense_node` and is unaffected. How the original H772 fixture reported
"34 = 34" as a passing live check against this pre-existing, unchanged-since-inception bug
is **unresolved** — most likely that verification ran against a differently-generated
`assembled_cards.jsonl` snapshot that can no longer be reconstructed — but the fix and its
correctness stand independently of that open question (audit tool, clean before/after,
zero anomalies, full `lod_acceptance.py` A/B/C/C5/C6/D/D2/D3 gate PASS).

> **Source:** [`microstructure.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure.py)
> `MARK` fix + [`_audit_micro.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_audit_micro.py)
> before/after · [`lod_acceptance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/lod_acceptance.py)
> full gate PASS. — RussianTranslation (pwg_ru / PWG++ German enrichment) · H879 · Sonnet 5
> (`claude-sonnet-5`) · 13-07-2026

## Etymology & derivation

### §33. Indigenous dictionaries agree on derivation; Wilson is the outlier

🟠 **The indigenous Sanskrit dictionaries agree on a head-word's derivation 90–100 %; Wilson 1832
is the systematic outlier (23–61 %).**
Evidence: across 10 Cologne dicts whose etymology was extracted to `<dict>_etymology.tsv`, affix
agreement on shared head-words (proportion, 95 % Wilson CI) is SKD↔VCP 93.8 % [85.2–97.6], Apte↔AP
100 % [97.9–100], VCP↔SHS 98.5 % [95.8–99.5], but WIL↔SKD only **22.9 % [14.6–34.0]** and WIL↔VCP
**61.2 % [58.7–63.7]** — the Wilson interval (≤34 %) is **disjoint** from every Sanskrit-side pair
(≥83 %), so the divergence is statistically clear, not sampling noise. Cross-tradition root
attribution: MW↔PWG (English √ vs German "Wurzel") 65 %, PWG↔PW 93 %.
Implication: the Pāṇinian analysis is a stable cross-source signal usable as a consensus/QA oracle;
Wilson's divergence is a distinct stratum, not noise.

> **Source:** [`cross_dict_agreement.csv`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/cross_dict_agreement.csv)
> + [PAPER_DRAFT.md](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/PAPER_DRAFT.md)
> · dashboard https://sanskrit-lexicon.github.io/csl-orig/ — csl-orig · 2026-06-26

### §34. The E abbreviation tag is polysemous across dicts

🟠 **The same `<ab>E.</ab>` tag means different things across dicts — count the meaning, not the
marker.**
Evidence: WIL `E.` = Etymology (39,713×); but CAE `E.` = "Epithet of" (`E. of Śiva/Viṣṇu/Indra`,
584×) and MD `E.` = "Epic" (`āste (E. + I. Ā.)`). A tag-count survey wrongly flagged CAE/MD as
etymology sources; reading the entry contexts corrected it.
Implication: never infer content from a shared tag across dicts (generalises the SKD/VCP
zero-markup trap); validate a marker's *sense* per dictionary before parsing it.

> **Source:** `csl-orig/v02/{cae,md}/` entry contexts — csl-orig · 2026-06-26

### §35. Root-recovery tiers err on root form, not identity

🟠 **Inferred root-recovery tiers err on root FORM, not root identity — and an LLM root pass must
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

> **Source:** [`nearest_root_audit.json`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/nearest_root_audit.json)
> + [`build_root_normalization.py`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/build_root_normalization.py) — csl-orig · 2026-06-26

## Encoding & normalization

### §36. IAST Unicode collides and normalises lossily

🔴 **IAST Unicode collides and lossily normalises if you're naïve.**
Evidence: `ś` = `s` + U+0301 (combining acute), which collides with a pitch-accent mark;
NFD-decompose-then-strip-Mn destroys vowel length (`ā`→`a`) and retroflex dots (`ṣ`→`s`).
Implication: use a length-preserving `form_key`, not a blanket NFD+strip-combining.

> **Source:** [`form_key` in sanskrit_util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py). — sanskrit-util / shared · 2026-06

### §37. BOM state is inconsistent across exports

🟠 **`csl-orig` files never carry a BOM; many exported HeadwordLists do.**
Evidence: `csl-orig` dict `.txt` are BOM-free; e.g. `MW-unique-key1-…txt` **has** `EF BB BF`
while its `key2` sibling does not.
Implication: check `head -c 3` before transforming; preserve the file's existing BOM state on
write; never silently add/strip one.

> **Source:** [SanskritLexicography `CLAUDE.md` § "Encoding — BOM is inconsistent"](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md). — csl-orig / SanskritLexicography · 2026-06

### §38. Injected BOMs crash the hw record parser

🟠 **A stray UTF-8 BOM slipped into a dict source by a markup commit crashes the record parser
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

> **Source:** [csl-corrections `.ai_state.md`](https://github.com/sanskrit-lexicon/csl-corrections/blob/master/.ai_state.md)
> §Dev Notes — csl-corrections · 2026-06-27

### §39. devanagari_to_slp1 mis-routes retroflex la

🟡 **`devanagari_to_slp1` mis-routes ळ (ḷa).**
Evidence: a pre-existing `sanskrit-util` master bug routes ळ via IAST→`x` instead of `L`.
Implication: low-severity (affects `ocr_verify`), but don't trust ḷa round-trips until fixed
(fix in progress on branch `feat/deva-to-slp1`).

> **Source:** [`devanagari_to_slp1` in sanskrit_util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py). — sanskrit-util · 2026-06

### §40. Gloss-language spelling drift tracks reform type, not age

🟠 **Orthographic drift in a dictionary's gloss language is governed by the TYPE of the language's
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

> **Source:** [SanskritSpellCheck `docs/ORTHO_DRIFT_FINDINGS.md`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/docs/ORTHO_DRIFT_FINDINGS.md)
> + `ortho_drift/*_drift_summary.tsv` (per-language tables) — SanskritSpellCheck · 2026-06-26

### §60. Practical Russian transcription of Sanskrit names has no safe reverse transliteration

🟡 **Cyrillic-only Sanskrit name glossaries cannot be joined to an SLP1 headword key without a
transliteration step that does not exist and is not safely buildable on the fly.**
Evidence: of 6 candidate SamudraManthanam name-index glossaries surveyed for `pwg_ru` reuse
(H184, 2026-07-05), only 2 (Гринцер, Рамаяна I-II/III) carry the IAST form inline in parens
right after the Cyrillic headword, giving a deterministic `iast_to_slp1` key (663 entries,
~72% joining a real PWG headword). The other 3 name glossaries (Потапова, Эрман-Темкин,
словарь Гринцера из Бада Кадамбари) are **100% Cyrillic-only** — 0 lines carry any Latin
script at all in the headword field. Practical Russian Indological transcription of Sanskrit
collapses dental/retroflex consonants (т = both त and ट) with no diacritic in plain text, so a
rule-based Cyrillic→SLP1 converter would silently manufacture WRONG keys for exactly the
retroflex-bearing names that are common in epic/Puranic material — a correctness-authority
signal (`corpus_gate.py`'s `INDEP`/`SPECIALIST` tiers) is the worst place to introduce silent
key corruption. (A 7th candidate, Топоров, isn't a gloss source at all — it's a name→page
index into a printed encyclopedia, `Агнихотра\t22`, with no gloss text.)
Implication: don't build a heuristic Cyrillic→Sanskrit transliterator under time pressure to
close a "wire N glossaries" task — flag the gap and stop. If it's ever wanted, it needs a
proper-noun lookup table validated against a known Sanskrit onomasticon, not a character-level
rule, and should be checked as its own artifact before any corpus_gate consumer trusts it.

> **Source:** [`SanskritLexicography/RussianTranslation/REUSE_MAP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md)
> + [`src/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/README.md#специализированные-глоссарии-имен--build_glossariespy)
> ([H184](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H184-Sonnet_RussianTranslation_pwg_ru_reuse_sources_wiring_05.07.26.md))
> — SanskritLexicography/RussianTranslation · Sonnet 5 `claude-sonnet-5` · 2026-07-05

---

## External platforms & services

### §41. The Sanskrit dictionary-platform landscape, probed live

🟠 **Twelve dictionary/DH platforms were fetched and feature-profiled on 2026-07-02; several
widely-assumed "facts" about them are wrong, and four are in degraded/migrating states.**

Evidence (every claim from a same-day fetch; full profiles + feature matrix in
[kosha/COMPARISON.md](https://github.com/gasyoun/kosha/blob/main/COMPARISON.md)):
**michaelmeyer.fr/sanskrit is 41 dictionaries** (1832–2000, both MW editions, PWG, PW, ŚKD,
VCP, Stchoupak, + 7 self-digitized indices) on one page per headword with **per-sense scan
links for 19 dicts** — not "a fast Apte site"; author = ERC-DHARMA CNRS (his own profile;
the earlier "Univ. of Geneva" claim was fabricated). **Heritage's Inria host serves an Anubis
anti-bot wall** to all programmatic clients (UoHyd mirror v3.77 is the reliable endpoint).
**DCS serves with a broken HTTPS cert** (hostname mismatch; plain HTTP only), full CoNLL-U
dump on GitHub. **VedaWeb migrated to the Tekst platform**; the original app was archived
16-02-2026. **spokensanskrit.org 301s to learnsanskrit.cc** (old-domain TLS broken);
**learnsanskrit.org/dictionary is a hard 404** (exited to Ambuda). **vidyut-kosha has no
end-user UI anywhere** — developer library only. **Ambuda's dictionary tool = 8 dicts, one at
a time.** **CDSL has a unified `/simple/` cross-dict search** (scope undocumented). And
**csl-orig's LICENSE is CC BY-SA 4.0** — Attribution-ShareAlike, commercial use *permitted*;
"Cologne is non-commercial" is a misconception (verified in the LICENSE file itself).

Implication: cite platform capabilities only from the dated survey, not from reputation;
integrate Heritage via the UoHyd mirror; treat kosha's differentiation as the composite
(collapse + morphology + corpus evidence + trilingual + open API + versioned citability),
since the read-only collapse alone is already built and closed-source; derived Cologne data
must ship BY-SA — an NC restriction cannot be added to it.

> **Source:** [kosha/COMPARISON.md](https://github.com/gasyoun/kosha/blob/main/COMPARISON.md)
> (three parallel live-fetch passes, Fable 5 `claude-fable-5`) +
> [csl-orig/LICENSE](https://github.com/sanskrit-lexicon/csl-orig/blob/master/LICENSE) —
> kosha · 2026-07-02

### §47. Heritage data is acquirable despite the Anubis wall — via a GitHub mirror; the morphology XML is not in it

🟠 **The Anubis anti-bot wall extends to INRIA's GitLab, not just the Heritage site — but a
GitHub mirror of `Heritage_Resources` exists, carries most of the data, and is LGPLLR-licensed.**

Evidence: [gitlab.inria.fr/huet/Heritage_Resources](https://gitlab.inria.fr/huet/Heritage_Resources)
returned the Anubis challenge page to a programmatic fetch (03-07-2026), same as
sanskrit.inria.fr in §41 — so "use the mirror" applies to the *data repository* too, not only
the live services. [darkone23/Heritage_Resources](https://github.com/darkone23/Heritage_Resources)
(branch `develop-main`, last updated 03-2025) mirrors it; contents verified via the GitHub API:
`DICO/` (hypertext Heritage dictionary), `MW/` (**MW pages aligned with DICO**, Heritage-covered
entries highlighted), `DATA/` (OCaml `.rem` banks incl. `mw_index.rem` **plus plain-TSV
frequency tables** `pada_freq.tsv` / `pada_morph_freq.tsv` / `pada_trans_freq.tsv` /
`comp_freq.tsv`), `CORPUS/`, `XML/` (legacy `SL_morph.dtd`/`WX_morph.dtd` + LGPLLR texts).
Per the upstream README (Huet 2021), the inflected-form XML databanks themselves are **not in
the repository** — they are generated at Platform install time and downloadable only from the
site's linguistic-resources page, i.e. behind the wall.

Implication: ingest Heritage *data* from the GitHub mirror; the morphology XML needs one manual
human-browser download (or a local Platform install) — never point an agent at
sanskrit.inria.fr or gitlab.inria.fr. License is **LGPLLR**, not CC — rule on composition with
BY-SA derived data before vendoring anything. Staged reuse plan:
[HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md).

**Update (03-07-2026, MG browser access): confirmed dead end, not just unverified.** MG
manually browsed
[gitlab.inria.fr/huet/Heritage_Resources/-/tree/master/XML](https://gitlab.inria.fr/huet/Heritage_Resources/-/tree/master/XML)
past the Anubis wall — its `XML/` tree is **byte-identical in scope** to the GitHub mirror's
(`SL_morph.dtd`, `WX_morph.dtd`, `LICENSES/`, the same README), last touched 6 years ago
(commit `ba45c546`, "New version 3.23", Huet, May 2020). The `LICENSES/` folder's own commit
message says it plainly: *"Now XML banks are constructed by Platform."* So this is not a case
of the GitHub mirror lagging GitLab — **neither repository has ever carried the inflected-form
XML databanks**; both stopped shipping them the same release. The GTD `@DO` (manual download
of current morphology XML) must go through the site's linguistic-resources page specifically
(behind the Platform's own install/session flow), not through either git repository — checking
GitLab again will not help.

> **Source:** live fetch of the GitLab URL + GitHub API listing of the mirror
> (`gh api repos/darkone23/Heritage_Resources/…`), Fable 5 (`claude-fable-5`) —
> SanskritLexicography · 2026-07-03; GitLab `XML/` cross-check via MG browser screenshot,
> Sonnet 5 (`claude-sonnet-5`) · 2026-07-03

### §43. SKD/VCP sense/citation fusion is a record-type effect, not a dictionary-level one

🟠 A corpus-scale classifier over every SKD and VCP *iti*-unit
([`build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs))
was built to promote a single hand-picked exemplar — *dharma* in Śabdakalpadruma (SKD)
fuses its synonym-run into its own authority citation, *ity Amaraḥ*; *dharma* in
Vācaspatya (VCP) keeps them structurally separate — to a full-corpus count. The
exemplar's *direction* did **not** survive the scale-up: SKD splits close to evenly
between fused and separable authority-marked units (53.3%/46.7%), while VCP skews
*toward* fusion (77.6%), the opposite of what the single lemma suggested. The reason
is registral, not a classifier bug: VCP's *dharma* entry is not a short synonym list
at all but an extended Mīmāṃsā argument that threads its citation sigla (`BA0`,
`sU0`, …) through paragraphs of discursive prose, so a citation's preceding unit is
rarely short there — while SKD mixes short encyclopaedic entries (which do fuse, like
*dharma*) with plenty of its own short citation-only units (46.7% separable).

Implication: **never trust a one-lemma exemplar to characterise a whole dictionary's
citation register** in this corpus — SKD and VCP both contain both patterns, in
different proportions driven by entry length/genre (short nominal gloss vs. discursive
commentary), not by a fixed per-dictionary convention. Any future "dictionary X marks
citations this way" claim in this project should be corpus-counted before it is
generalised, exactly as this one was, and reported honestly even when the corpus
count contradicts the exemplar's direction rather than tuned to match it.

> **Source:** [csl-atlas PR #184](https://github.com/sanskrit-lexicon/csl-atlas/pull/184)
> (A02 revision execution) —
> [data/lexico/r2_kosa_fusion.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json),
> Sonnet 5 `claude-sonnet-5` · 2026-07-02

### §44. Raw Latin-string tallies over gloss text include etymological false positives; Bopp lacks √yabh

🟠 **Two source-checked caveats on the A36 *obscaena Latine* data that any reuse of
[`A36_corpus_screen.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_corpus_screen.csv)
must respect: (1) a raw obscene-Latin string count over dictionary gloss text picks up
*etymological apparatus*, not only headword glosses — MW72's single obscene-core hit
(*cunnus*) glosses the Lithuanian cognate *pís-ti* inside an etymology
(`mw72.txt` line 215431), so the 1872 Monier-Williams screens zero headwords; (2) Bopp's
*Glossarium* (BOP) has no √*yabh* entry at all** — `grep '<k1>yaB' bop/bop.txt` = 0, and all
21 *futu-* matches are *futurum* "future"; the sex-act field is glossed with clinical Latin
(*maithuna* → *coitus*; under √*gam* "adire virum, feminam, i.e. coire, concumbere").

Evidence: verified against `csl-orig/v02/{mw72,bop,ccs,mw}/`, 02-07-2026, during the A36
pre-submission pass; every curated figure in the paper's §3/§3a/§3b re-verified exactly
against [`A36_latin_obscena.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena.csv)
(2,104 rows) in the same session.

Implication: **treat `A36_corpus_screen.csv` as raw triage tallies, never as per-dictionary
screen verdicts** — the curated eleven-dictionary CSV is the hand-vetted truth; and never
cite "Bopp glosses √*yabh*" (he cannot — the entry does not exist). Any future gloss-register
sweep should separate etymology/apparatus spans from gloss spans before counting.

> **Source:** [papers/A36_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_review_fable5.md)
> (Major 3–4) + [PR #74](https://github.com/gasyoun/SanskritLexicography/pull/74),
> Fable 5 `claude-fable-5` · 2026-07-02

---

### §45. Siglum prefix-families routinely bundle several distinct works; the diacritic-stripping fold has poisoned keys

🟠 **Adjudicating the top-50 prefix-clustered `<ls>` siglum families (≈52k+ citation mass,
cross-dict) showed the family→work assumption fails more often than it holds: 26/50 families
bundle 2–6 distinct works** (Bhag. ≠ BhP.; Rājan. = Rājanighaṇṭu ≠ Rājat.; the `panc` family
= Pañcatantra + Pañcarātra + Pañcaviṃśa-Br. + Pañcadaṇḍacchattraprabandha; five different
Śabda- kośas share one prefix), only 12/50 merge cleanly, and 7 of those 12 are not
abbreviation variants at all but **unstripped trailing roman numerals** (`dhatupxxxii`,
`paniv`, `mbhi` — ~120 pseudo-members). Two structural traps: (1) the diacritic-stripping
fold **poisons** keys — `samk` merges Śaṃk° (Śaṃkara) with Sāṃk° (Sāṃkhya-), `kaus`
collides Kauś./Kauṣ., `sank` collides Śaṅkh-school/Śaṃkara; (2) MW uses *near-identical*
sigla for different works — `Dharmaś.` (bare, kāvya glosses) = Dharmaśarmābhyudaya while
`Dharmas.` + section number = Dharmasaṃgraha. Also measured: MW's "unknown-layer" siglum
tail is 855 distinct base sigla but only **6.5% of citation instances** — a long tail, not
a coverage wall.

Evidence: 02-07-2026 adjudication of families 1–50 from
[siglum_family_candidates.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/siglum_family_candidates.csv)
against live `csl-orig/v02` contexts +
[mwauthorities_init.txt](https://github.com/sanskrit-lexicon/MWS/blob/master/mwauthorities/mwauthorities_init.txt);
verdict table in
[SIGLUM_ADJUDICATION_2026-07.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/SIGLUM_ADJUDICATION_2026-07.md);
machine-readable rulings in
[dict-source-aliases.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/dict-source-aliases.json).

Implication: **never merge sigla by fold-key or prefix similarity alone** — every merge is a
per-work identity call; quarantined keys (`samk`, `ratnam`, `burn`, `mahav`) must stay
unmerged until per-dict raw-form splits exist; and any fold-based join over `<ls>` data
(frequency tables, layer maps, link resolvers) inherits these collisions silently unless it
consults the curated alias table.

> **Source:** [csl-atlas#185](https://github.com/sanskrit-lexicon/csl-atlas/pull/185) +
> [MWS PLANNING_2026-07.md](https://github.com/sanskrit-lexicon/MWS/blob/master/planning/PLANNING_2026-07.md),
> Fable 5 `claude-fable-5` · 2026-07-02

### §48. VedaWeb 2.0's resource export is an async task behind a pickup-key, not a direct GET — and the server went unresponsive mid-attempt

🟠 **`GET /api/resources/{id}/export` does not stream a file. It returns `202` with a
`TaskRead` object (`id`, `pickupKey`, `status:"running"`); the actual bytes are fetched
later from `GET /api/platform/tasks/download?pickupKey=<key>`, which needs no auth despite
the OpenAPI spec listing `APIKeyCookie`/`OAuth2PasswordBearer` security on the export route
itself (that route worked fully anonymous in practice — the declared security is aspirational,
not enforced, at least for `GET /resources` and `GET /resources/{id}/export`).** There is no
public GET on `/platform/tasks/{id}` to poll task status (only `DELETE`); the intended
poll path is `/platform/tasks/user`, which itself requires the session cookie.

While attempting H096's bulk export (03-07-2026, ~04:06 UTC), the export task was triggered
successfully (task id `6a47354cb37f6ea98795ad7a`, resource `66695e4a14f6d337f7788740`
Casaretto accented word-split), but every subsequent call to `vedaweb.uni-koeln.de` — the
download endpoint, `/api/status`, even `/api/openapi.json`, which had answered in <1s minutes
earlier — degraded to a `504 Gateway Timeout` and then to full connection timeouts, confirmed
from two independent network paths (local `curl` and the sandbox's separate `WebFetch` egress,
both of which reached `example.com` fine in the same window). The outage is server-side at
Cologne, not local. No file was downloaded; nothing was committed to `VisualDCS`.

Implication: the next attempt at H096 must (1) build the poll/download loop around the
pickup-key mechanism, not assume a synchronous export, and (2) retry the whole sequence
fresh — a `202` response does not guarantee the export completes if the server drops
mid-task, so re-trigger `/resources/{id}/export` rather than reusing a stale pickup key.
Treat isolated `504`s on this host as retry-worthy, not as evidence the API changed.

**Update 08-07-2026 (H096 executed, Sonnet 5 `claude-sonnet-5`):** a liveness probe
(`curl -sI .../openapi.json` → `200`) confirmed the outage above had cleared; all 4
core exports + the 36-resource catalog landed at
[VisualDCS PR #17](https://github.com/gasyoun/VisualDCS/pull/17). Two new gotchas
surfaced during the run:

- **The `pickupKey` is single-use, independent of whether the download actually
  succeeds.** A `curl --max-time 30` on the `lemmatization` export (40MB) was cut off
  mid-transfer by the client-side timeout; the *next* request with the same key
  returned `404 {"key":"exportNotFound"}` even though the export itself had completed
  server-side — the first `GET .../download` call had already consumed the key. There
  is no way to "resume" or re-fetch with a stale key; the only fix is to re-trigger
  `/resources/{id}/export` for a fresh `pickupKey` and download it in one shot with a
  timeout generous enough for the file size (the retry needed `--max-time 120` for a
  41MB payload). Budget the download timeout to the resource, not a fixed short value.
- **Export readiness time varies wildly and is not correlated with `resourceType`
  alone.** The three `plainText`/`textAnnotation` exports (padapāṭha, accented text,
  Casaretto word-split) were pickup-ready within seconds of triggering. The `apiCall`
  resource (`lemmatization`, which cross-references live CDSD dictionary lookups per
  token) needed 4 total trigger attempts and ~9 minutes of elapsed wall-clock before a
  download succeeded clean — not from repeated failures, but because each earlier
  attempt's key got burned by a timeout-truncated download before the export was even
  polled again. Poll with `404 exportNotFound` as "not ready yet, keep the same key",
  and only re-trigger a fresh export after a completed-but-truncated download, not
  preemptively.

**Update (03-07-2026, same day, hours later, Sonnet 5 `claude-sonnet-5`): outage persists,
now a full HTTP-layer hang rather than `504`s.** Re-probed `https://vedaweb.uni-koeln.de/`
and `/api/openapi.json` three times over ~90s: TCP connects and the TLS handshake completes
(port 443 reachable, `curl -v` shows the request sent), but zero bytes return before a 15–25s
timeout — no `504`, just silence, suggesting the app process itself is wedged rather than a
transient gateway hiccup. `http://vedaweb.uni-koeln.de/` still answers instantly with a `301`
to the dead `https://` host. General internet (`google.com`, `github.com`) and
`https://uni-koeln.de/` root both returned `200` in the same window, isolating the failure to
the `vedaweb` subdomain/app specifically — confirmed server-side, not a local/sandbox network
issue. Nothing downloaded or committed. Treat this as an extended outage, not a blip — before
the next H096 attempt, do a single cheap liveness check
(`curl -sI --max-time 15 https://vedaweb.uni-koeln.de/api/openapi.json`) before running the
full export mission.

> **Source:** live probe against `vedaweb.uni-koeln.de/api`, [openapi.json](https://vedaweb.uni-koeln.de/api/openapi.json)
> schema inspection + task-trigger + download attempts, Sonnet 5 `claude-sonnet-5` · 2026-07-03

---

### §49. MW↔Heritage coverage highlighting is a duplicate-anchor pattern, not a CSS class — and the mirror's "current" dictionary is a different-scope asset than the 2014 reader stem list

🟠 **The Heritage mirror's own README calls Heritage-covered MW entries "the yellow
areas," but in the static `MW/*.html` there is no yellow — coverage is encoded as a
duplicate anchor pair: a covered entry carries both `<a name="H_<key>">` and
`<a name="<key>">` immediately before its `<span class="Deva">` (an uncovered entry
carries only the plain anchor).** The `H_<key>` and `DICO/*.html`'s
`<a class="navy" name="<key>">` anchors use the *same* VH-derived key, so a covered MW
entry resolves to its Heritage dictionary entry directly — no fuzzy matching or OCR
needed. Two key-normalisation traps found building the crosswalk: DICO prefixes proper
nouns with a bare `U` that MW's `H_` anchor lacks (`Uaadinaatha` vs `H_aadinaatha`), and
MW's plain anchor drops the `#N` homonym-disambiguation suffix DICO always keeps
(`a.mzaka` vs `a.mzaka#1`/`#2`) — both are worked around in
[`heritage_mw_crosswalk.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_mw_crosswalk.py), lifting anchor
resolution from 92.5% to 97.6% of covered entries.

**Separately:** the mirror's `DICO/` (current, 38,343 unique stem keys) is not a version
bump of the 2014 reader-export stem list
([`then-2014/21562-huet-velthius.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/21562-huet-velthius.txt),
21,055 keys) — it is the **full current dictionary**, a different-scope asset. Naively
diffing the two and reporting "61% more stems since 2014" would be misleading: the 2014
list is a *reader's* curated corpus-driven selection, and the fuller current dictionary
correspondingly shows **lower** CDSL/DCS coverage density (80.1%/50.1% vs. the 2014
list's 86.2%/60.0%) simply because it includes more of the dictionary's grammatical
long tail (affix entries, comparative/superlative derived forms) that the reader's
selection filtered out — not because the underlying lexicon regressed.

Evidence: [HERITAGE_MIRROR_INVENTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/HERITAGE_MIRROR_INVENTORY.md),
[Huet-INRIA-Wordlist-vs-Cologne.md §6](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Huet-INRIA-Wordlist-vs-Cologne.md#6-current-mirror-vs-the-2014-export-03-07-2026),
[mw_heritage_crosswalk.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.md) — H099 Phases 0–2,
03-07-2026.

Implication: any future MW↔Heritage alignment work should read coverage off the
duplicate-anchor pattern (not attempt to scrape a rendered "yellow" style that doesn't
exist in the static export), apply the `U`-prefix/`#N`-suffix normalisation before
joining DICO and MW keys, and never present the current-DICO-vs-2014-reader-list delta
as a same-asset time series without the scope caveat.

> **Source:** [HeadwordLists/heritage_mw_crosswalk.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_mw_crosswalk.py) +
> [heritage_coverage_current.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_coverage_current.py),
> Sonnet 5 `claude-sonnet-5` · 2026-07-03

### §50. CDSL display paths are NOT uniformly `/2020/web/` — and two new digitizations landed in June 2026

🟠 **The CDSL per-dictionary web apps do not all live under `/scans/{CODE}Scan/2020/web/`:
NMMB (added June 2026) lives under `/2026/web/` — the 2020 path 404s. Any tool that
constructs CDSL display URLs from a code must take the year from the front-page row's own
href.** Also: two new digitizations exist — **NMMB is a live catalog row** (first addition
in years; *Nāmamālikā* of Bhoja, 1955 Deccan College ed., 506 synonym groups, via the
sanskrit-kosha project), and **PWKVN** (Böhtlingk's own *Nachträge und Verbesserungen*
appendixes to PW, 24,976 records — each volume's appendix restarts at *a*, so headwords
recur) has full [csl-orig source](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pwkvn)
but **no catalog row** — only an
[experimental display](https://www.sanskrit-lexicon.uni-koeln.de/scans/csl-apidev/pwkvn/).

Evidence: `curl` 2026-07-03 — `NMMBScan/2020/web/webtc/indexcaller.php` → **404**,
`NMMBScan/2026/web/…` → 200; csl-guides' catalog generator had the 2020 hardcode and
produced dead NMMB links (fixed in
[build-catalog.mjs](https://github.com/sanskrit-lexicon/csl-guides/blob/main/scripts/build-catalog.mjs),
[PR #82](https://github.com/sanskrit-lexicon/csl-guides/pull/82)).

Implication: never assume the `/2020/web/` template for new dictionaries; parse the year
from the live front page. Watch for PWKVN (and the still-absent KOW/KNA) gaining real
catalog rows.

> **Source:** [csl-guides PR #82](https://github.com/sanskrit-lexicon/csl-guides/pull/82) audit sweep,
> Fable 5 `claude-fable-5` · 2026-07-03

---

### §80. CORRECTED — the MWScan/2020 `servepdf.php` endpoint is RIGHT (serves 1899); the 1872 first-edition scan coexists on the portal with colliding page numbers

🟠 **Corrected 15-07-2026 (same session-day as first written): the endpoint was never
wrong.** An `api=1` probe of
`/scans/MWScan/2020/web/webtc/servepdf.php?api=1&page=277` (with AND without
`dict=mw`) resolves to `MWScanpdf/mw0277-kArSNi.pdf` — the correct **1899** page for
the `mw.txt` `<pc>` locus `277,1` (*kāla*). The `page` param maps 1:1 onto 1899 print
pages; the per-page files are named `mw<page>-<first-headword>.pdf` but the endpoint
does that lookup itself, so a `{page}` URL template is fine. The endpoint's own nav
links carry `dict=mw` — include it for canonical form.

**The real, surviving trap is portal-navigation-level:** Cologne ALSO hosts the
**1872 first-edition** scan set, browsable with per-page files named `pg_NNNN.pdf`,
and both editions print their own page numbers — a manually saved "page 277" can be
either edition's 277 (1872's is *khel/gaṅgāmbhas* = `mw72.txt` pc `0277-a`; 1872
*kāla* sits at `0224–0225`). That is exactly how the wrong pages entered this session:
a browser download of `pg_0277.pdf`/`pg_0278.pdf` from the 1872 browser, initially
misattributed to the servepdf endpoint (the endpoint itself was 429-throttled for the
probing IP, so the misdiagnosis went unchecked for one release). **Identify a
manually fetched MW page by its running heads and filename pattern
(`mw<page>-<headword>.pdf` = 1899 · `pg_NNNN.pdf` = 1872), never by the corner
number.** Sibling of [[§50]] (display paths are not uniform either).

Implication: `EntryAnatomy/build_entry_anatomy.py`'s MW auto-pull is re-enabled
(v1.9.15; it was disabled in v1.9.14 on the misdiagnosis); kosha's
[`app/scan_resolver.py`](https://github.com/gasyoun/kosha/blob/main/app/scan_resolver.py)
was verified correct as-is and needs no change. The original v1.9.14 wording of this
section claimed the endpoint served 1872 — that claim is retracted.

> **Source:** H870 correction pass — `api=1` probes via independent egress
> ([SanskritLexicography PR #479](https://github.com/gasyoun/SanskritLexicography/pull/479) context),
> Fable 5 `claude-fable-5` · 15-07-2026

---

### §51. Huet correspondence predates this session (2021) — the morphology-XML "gate" was already resolved in writing; direct download URLs recovered

🟠 **MG already corresponded with Gérard Huet directly on 30-03-2021 about this exact
repository** — MG had asked why `Heritage_Resources`' `XML/` folder was empty (only DTDs);
Huet replied (from `Gerard.Huet@inria.fr`) that the XML data banks were dropped from the git
repo for space reasons and are instead generated at Platform install time, downloadable as
compressed archives from the site's linguistic-resources page — and admitted the repo's
README doesn't explain this ("Sorry about the README... not up-to-date, I shall update it").
**§47's "confirmed dead end" finding (03-07-2026) independently re-derived exactly what Huet
already told MG four years earlier** — the outreach draft this session originally prepared
wrongly stated "no prior contact found" (a memory/search gap, not a fabrication: the 2021
email lives outside any repo or session memory this project indexes).

MG then retrieved the live `https://sanskrit.inria.fr/xml.html` page in a real browser
(saved locally, past the Anubis wall a script cannot pass) and it gives **exact download
URLs**, still live: `https://sanskrit.inria.fr/DATA/XML/WX_morph.xml.gz`,
`https://sanskrit.inria.fr/DATA/XML/SL_morph.xml.gz` (+ `.txt` DTDs at the same path,
`LGPLLR.pdf`). Current dictionary version **3.81, dated 2026-06-21** — the live site is
**over a year ahead** of the GitHub mirror's `develop-main` (03-2025) and the
`Heritage_Resources` README the mirror ships is still stale exactly as Huet flagged in 2021.

Implication: (1) **check for prior correspondence in the user's own email/files before
drafting a "first approach" outreach email** — repo/session/memory search alone can miss a
years-old exchange that fully answers the question being asked; when in doubt, ask the human
rather than assert "no prior contact." (2) The morphology-XML `@DO` gate is now a **known,
bookmarked download**, not an open-ended "find the resources page" task — a human browser
visit to the two `.xml.gz` URLs above is the entire remaining step. (3) Any future Heritage
freshness comparison should note the mirror is ~14+ months stale against the live dictionary
version and flag that gap rather than treating the mirror as current.

> **Source:** MG-provided 30-03-2021 email thread + locally-saved
> `https://sanskrit.inria.fr/xml.html` (browser-passed Anubis, pasted into session
> 03-07-2026), Sonnet 5 (`claude-sonnet-5`) · 2026-07-03

**Update (03-07-2026, same day): the @DO download landed and is confirmed real,
current, and exactly the data the roadmap needs.** MG downloaded both `.xml.gz`
files + DTDs; both are valid gzip, ~184 MB decompressed each. `SL_morph.xml`
(SLP1-keyed): **1,286,615 inflected forms across 32,837 distinct stems**, dated
"21 Juin 2026" in its embedded header (matches the site's stated v3.81) —
**3× kosha's existing vidyut-built forms layer (426,410 pairs)**, confirming
this is worth ingesting as roadmap Phase 4's third morphology witness, not a
redundant re-derivation. The `stem` attribute uses the *same* `#N`
homonym-disambiguation convention as `mw_heritage_crosswalk.tsv`
(`stem="aMSaka#2"`) — directly joinable without re-normalisation. Files staged
at `HeadwordLists/heritage_mirror/manual/` (gitignored, LGPLLR rights pending
the Phase 0 @DECIDE — same restriction as the rest of the mirror). Phase 4
(forms-oracle build) is now unblocked on data; still gated on the license
@DECIDE for anything vendored beyond local/derived use.

> **Source:** files provided by MG (downloaded via browser from
> `sanskrit.inria.fr/DATA/XML/`), gzip integrity + structure verified locally,
> Sonnet 5 (`claude-sonnet-5`) · 2026-07-03

### §52. Heritage vs kosha forms diff: the small raw overlap is mostly convention + model difference, and "disagreements" are two-thirds lemmatization policy, not error

Phase 4's forms-oracle diffed Heritage's rule-generated morphology (`SL_morph.xml`
v3.81, **1,022,526** distinct SLP1 forms) against kosha's DCS+vidyut layer
(**409,978** forms), joining on the SLP1 form string. The result is
counter-intuitive and worth recording so the next session does not misread it:

- **Raw form overlap is only 94,264** (23% of kosha, 9% of Heritage) — but this is
  **not** a coverage failure. Heritage *generates the entire paradigm* of each
  stem (incl. ~half a million compound-initial `iic`/`iiv` forms a corpus never
  tokenises), so its 928k Heritage-only forms are engine surplus, not gaps.
- **The kosha-only gap is inflated by two transcription conventions.** DCS writes
  word-final/pre-consonant nasalisation as **anusvara `M`** where Heritage writes
  the phonetic homorganic nasal (`AvAsaM`/`AvAsam`, `oMkAra`/`oNkAra`): **18,636**
  kosha-only forms recover a Heritage match under nasal-normalisation. A further
  **8,264** kosha-only forms are DCS **avagraha sandhi artifacts** (leading `'`,
  e.g. `''jYAya`) that by construction never appear in a citation declension table.
- **On the 94k overlap, 78.3% agree** on ≥1 lemma. Of the 21.7% (20,496)
  disagreements, **66% are verbal-derived** (participle / finite-verb /
  verbal-indecl) — a documented **root ↔ derived-stem lemmatization-policy**
  difference (Heritage → participle-stem `garhita` / root `kf`; DCS/vidyut → root
  `garh` / causative-stem `kampay`), **not a contradiction.** The genuine-divergence
  pool is the remaining **6,966 nominal-only** disagreements, and hand-adjudication
  of 40 rows shows roughly half of *those* are both-valid ambiguities (`ābhābhyām`
  ← ābhā *or* ābha). **Net genuine one-sided divergence is low-single-digit % of
  the overlap**, and it exists on both sides: DCS corpus mis-tags
  (`vaiśvadeveṣu` → *aparāhṇika*) and Heritage stem-choice oddities
  (`goṣṭhīm` → *goṣṭha*).

Implication for reuse: (1) never compare Heritage and DCS/corpus form strings
without **anusvara/nasal normalisation** first — the raw string join understates
true overlap by tens of thousands of forms. (2) A "disjoint-lemma" disagreement is
**not** an error signal on its own; filter to **nominal-only** rows before treating
disagreements as a correction queue. (3) Heritage's precative/subjunctive/
injunctive/conditional **scope gaps** mean those DCS verb forms are kosha-only *by
design* — expected, not missing. Full write-up + reproducible script:
[heritage_forms_oracle.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle.md).

> **Source:** [HeadwordLists/heritage_forms_oracle.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle.py)
> over `SL_morph.xml` v3.81 + `kosha.db`; 40-row hand-adjudication;
> Opus 4.8 (`claude-opus-4-8`) · 2026-07-03

### §53. The WIL etymology extraction's affix field is ~half noise — Wilson "outlier" figures are substantially a measurement artifact

🔴 **`csl-orig/v02/wil/wil_etymology.tsv`'s `affix` column contains 3,375 distinct values
against a closed 23–39-item Pāṇinian vocabulary in every Sanskrit-side extraction; only
50.1 % of WIL's 19,641 affix instances are valid Pāṇinian affix names.** Any agreement or
frequency statistic computed over the raw WIL affix column inherits this noise floor:
vocabulary-filtering lifts WIL↔SKD affix agreement 22.9 → 66.7 %, WIL↔VCP 61.2 → 80.2 %.
WIL's *root* column has the analogous defect — roots captured in Wilson's thematic surface
form (`aMSa` where SKD has `aMS`), unreached by the corpus root-normalization fold — giving
WIL root "agreement" of 7.9–20 % against every dictionary **including MW at 8.4 %**
(n=1,074), which is form mismatch, not editorial divergence. Also: MD (201×) and CAE (584×)
carry the same `<ab>E.</ab>` tag WIL uses as its etymology marker, but there it means **Epic
register** — never feed them to a WIL-style E.-extractor.

Evidence: computed 03-07-2026 over the committed TSVs with the same set-intersection rule as
[stats_etymology.py](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/stats_etymology.py)
§6a; full workings + fix plan (M1/M4/m3) in
[papers/A35_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A35_review_fable5.md).

Implication: consume `wil_etymology.tsv` only after filtering `affix` against the Pāṇinian
vocabulary (union of the Sanskrit-side extractions) and treat its `root` column as
surface-form, not citation-form; quote A35's Wilson figures only in the vocabulary-filtered
version until the extractor is fixed.

> **Source:** [A35_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A35_review_fable5.md),
> Fable 5 `claude-fable-5` · 2026-07-03

---

### §56. DICO's entry anchors nest three structural roles under one HTML class — only one is a true entry boundary

🟡 **The Heritage DICO mirror's named entry anchors mark three different
structural roles that all share the same CSS class, and conflating them
truncates or over-merges entry glosses.** (1) a fresh headword anchor
immediately preceded by its own Devanagari span; (2) a compound/sub-entry
anchor immediately preceded by a bare paragraph break (no Devanagari span) —
genuinely a separate entry (e.g. `aṃśavāda`, `aṃśahara` under `aṃśa`'s letter
group); (3) an inline cross-reference anchor embedded mid-sentence in another
entry's own prose (e.g. the proper noun `Aṃśa` mentioned inside `aṃśa`'s
definition, or a dual form like `aṃsau` mentioned inline in `aṃsa`'s gloss) —
**not** a boundary. A naive per-anchor split (boundary = every anchor)
truncates entries like `aṃśa` mid-sentence before its mythological sense; the
opposite over-correction (boundary = only Devanagari-preceded anchors) merges
the compound sub-entries' distinct glosses into the parent's. The fix
distinguishes (1)/(2) from (3) by checking whether the anchor is preceded
(modulo whitespace/entity noise) by a tag close versus plain running text,
and must resolve the boundary to the **start** of the next Devanagari span
(not the anchor position itself), else the next entry's headword text leaks
into the tail of the previous gloss. Separately: DICO uses two distinct
link-color classes for genuine cross-references to other entries (inline
citation links, and trailing "see also" links) — a third color class is only
external declension/conjugation-generator CGI links, not an entry
cross-reference, and must be excluded from any `cross_refs` field.

Evidence: 24,549/24,549 crosswalk-resolved entries extracted with zero
truncation/bleed on 25 hand-checked rows (10 shortest, 10 longest up to 3,832
chars, 5 random) — full workings in
[heritage_dico_gloss.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss.md).

Implication: any future DICO HTML parser must classify anchors by their
*preceding-tag context*, not just their CSS class, before treating one as an
entry boundary.

> **Source:** [heritage_dico_gloss.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss.md),
> Sonnet 5 `claude-sonnet-5` · 2026-07-03

---

### §55. `gen_opt_harness2.py` output-budget: coarser wins on both knobs, in opposite directions

🟢 **Two untuned S10-era knobs in
[`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
calibrated by A/B — the general lesson is "coarser batching wins," but it does
NOT generalize to "coarser splitting always wins":** (1) `--output-budget`
60→90 on the 56-card `hA` root: **90 wins clearly** — 60 agent calls vs 66
(−9%), 4.03M vs 4.68M tokens (−14%), 496s vs 1,082s wall-clock (−54%),
identical quality (0/56 null both). Shipped as the new default same-session.
(2) `AUTOSPLIT_LS_BUDGET` (giant-head fragment granularity, in
[`autosplit_requeue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py))
18 (stock) vs 10 (finer) on the 150-`<ls>` giant head `gam~~h0_00_pwg00`: finer
fragmentation made it **worse** — 21 agent calls vs 13 (+62%), 1.46M vs 925K
tokens (+58%), 1,207s vs 615s wall-clock (+96%), same outcome (1/1 healed,
0 null). Kept at 18, not changed. The direction differs because
`--output-budget` controls how many *whole cards* share a batch (bigger =
more amortization of the fixed per-call system-prompt overhead), while
`AUTOSPLIT_LS_BUDGET` controls how finely ONE already-failing giant card gets
chopped (finer = more, smaller heal calls, each still paying the fixed
overhead, with no offsetting reduction in per-fragment failure rate at this
citation density).

Evidence: 4-arm live calibration (Sonnet 5 `claude-sonnet-5`), fresh worktree
off `origin/master` (branch `knob-calibration-20260703`), full numbers in
[RussianTranslation/KNOB_CALIBRATION_2026-07-03.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/KNOB_CALIBRATION_2026-07-03.md).

Implication: when tuning a batching/splitting knob in this harness, check
which of the two mechanisms it governs (amortization vs failure-isolation)
before assuming "smaller unit = more robust" — for this harness the opposite
held on the split-granularity knob.

> **Source:** [KNOB_CALIBRATION_2026-07-03.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/KNOB_CALIBRATION_2026-07-03.md),
> Sonnet 5 `claude-sonnet-5` · 2026-07-03

---

### §57. samskrtam.ru/z/ is id-addressed with no name lookup — deep-linking needs a scraped root→id table; 8 primer-basic roots are absent

🟡 **The [samskrtam.ru/z/](https://samskrtam.ru/z/) verb-root dictionary addresses entries
only as `/z/verb.php?id=N` (numeric, 905 rows) — there is no lookup-by-root URL, no slug
scheme, and the nouns/preverbs/suffixes/endings pages have no per-entry pages at all.**
Deep-linking a headword therefore requires scraping the index table once and keeping a
static root→id map. Two further traps in the index: the anchor text uses a display font
where `Ø` stands in for accented vowels (`Øs` = *as*) — the clean IAST citation lives in
the row's second cell, sometimes with homonym digits (`1 as`) or comma-separated variants
(`1 aś, aṃś`); and citation grades differ from Bühler-style full-grade forms (site has
`kṛ`/`mṛd`, a primer citing `kar`/`mard` needs an `ar`→`ṛ` fold plus an alias table —
`dhyai→dhyā`, `div→dīv`, `pracch→prach`, `marg→mārg`, `kalp→kḷp`). **Eight primer-basic
roots are simply not in the database: `arth, daṇḍ, dhe, do, gaṇ, yam, śikṣ, śubh` —
including `yam`** (grep count 0 in the raw index HTML), a gap worth fixing on the site
itself.

Evidence: measured 03-07-2026 while wiring Bühler glossary links (issue
[#2](https://github.com/alexander-myltsev/buhler-sanskrit-book/issues/2), PR
[#12](https://github.com/alexander-myltsev/buhler-sanskrit-book/pull/12)); scraper +
resolution logic committed as
[scripts/generate_samskrtam_links.py](https://github.com/gasyoun/buhler-sanskrit-book/blob/issue-2-glossary-links/scripts/generate_samskrtam_links.py)
(170/178 Bühler roots resolved).

Implication: anything that wants to link into samskrtam.ru/z/ (kosha cross-refs, other
teaching material) should reuse that generator/table rather than re-derive it; nouns can't
be linked at all until the site (or kosha P2 lemma cards, ruling D4) provides per-entry
pages; and the 8 missing roots (esp. `yam`) are a samskrtam.ru data gap for MG.

> **Source:** Bühler H101 session ([H101-Fable_buhler-sanskrit-book_buhler_ux_features_03.07.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H101-Fable_buhler-sanskrit-book_buhler_ux_features_03.07.26.md)),
> Fable 5 `claude-fable-5` · 2026-07-03

---

### §58. PWG-RU promoted store has input-level provenance, but old RU rows lacked exact model versions

🟡 **The PWG→Russian final workflow card schema does not itself require model
provenance, but the promoted store does carry the operational breadcrumb needed
for reuse and repair.** Each promoted sense row in local
`RussianTranslation/src/pwg_ru_translated.jsonl` has `provenance` fields for
model alias, generator, root/rootmap hash, raw and portrait SHA-256, generation
time, workflow file, and promotion script. That is enough for the
content-addressed translation memory to reuse unchanged inputs without
re-running Sonnet. The defect was version specificity: a live audit on
2026-07-03 measured **10,856 store rows; 10,446 RU rows with `model='sonnet'`
but no exact `model_version`; 410 RU rows already exact-versioned as
`claude-sonnet-5`; 8,574 EN provenance rows exact-versioned; 15 rows missing
input hashes; 80 partial-card rows.**

Implication: do not rerun all old cards just because model technology changed.
First run the deterministic provenance/gap audit, reuse byte-identical cards by
`provenance.input_raw_sha256`, and only retranslate changed or failed inputs.
Legacy `sonnet` aliases whose exact version cannot be proven should be marked
unresolved, not date-mapped or guessed.

> **Source:** `RussianTranslation/src/audit_translation_provenance.py` live store audit
> and conservative backfill, Codex/GPT-5 · 2026-07-03

---

### §59. Böhtlingk's *Indische Sprüche* (both editions) already fully digitized in `sanskrit-lexicon-scans`, not just `sanskrit-lexicon`

🟡 **A prior-art search that only checks local clones + the `sanskrit-lexicon`
org will miss finished Cologne-project digitizations that live in
`funderburkjim`'s personal repos or the `sanskrit-lexicon-scans` org.**
[`sanskrit-lexicon-scans/boesp1`](https://github.com/sanskrit-lexicon-scans/boesp1)
(1st ed., 1863–5, 5,419 sayings, PDF source courtesy Mārcis Gasūns) and
[`boesp2`](https://github.com/sanskrit-lexicon-scans/boesp2) (2nd ed., 1870–73,
7,613 sayings, digitized by Thomas Malten) are both live, per-verse-served
digitizations. The PWG/PWK `Spr. N` citation crosswalk was already shipped and
closed via [`sanskrit-lexicon/PWG#87`](https://github.com/sanskrit-lexicon/PWG/issues/87)
(2026-05-06): `csl-orig/v02/pwg/pwg.txt` carries 10,366 `<ls>`-wrapped `Spr.`
citations distinguishing 1st-ed. (`Spr. N`) from 2nd-ed. (`Spr. (II) N`), and
`csl-websanlexicon`'s `basicadjust.php` already generates live hrefs for them.

Implication: on 2026-07-03 (Sonnet 5, `claude-sonnet-5`) this was missed —
`SanskritLexicography/IndischeSprueche/` was built as a fresh dataset
extraction and [Uprava H143](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H143_pwg_pwk_indische_sprueche_crosswalk.md)
scoped a "new" crosswalk, both corrected/retracted same-day once MG flagged
it. Any future prior-art check touching a Cologne primary source, scan set, or
citation crosswalk must also run `gh repo list funderburkjim` and
`gh repo list sanskrit-lexicon-scans`, and grep the actual `csl-orig` source
text for existing `<ls>` markup, before assuming nothing exists.

### §70. pwg_ru TM composite grade: A is consensus-gated (5.7%), and a reference-free surface QE cannot detect wrong-sense

> _Was §60 until 11-07-2026, renumbered — duplicate key (§60 was already taken by the Russian-transcription finding)._

🟡 **Grading the 1.09M-unit Sa→Ru translation memory
([`tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py),
H215 Slice 2) with the deterministic `proxy` QE yields A 5.7% / B 94.0% / C 0.3%
over the full corpus.** All 62,503 A units satisfy the corroboration gate
(≥2 distinct works agreeing on one `(passage, slp1)`, ≥50%) — A is driven by the
multi-translation clusters (Bhagavad-gītā ×10, repeated epic verses), not by QE
score alone. Measured 06-07-2026 (Opus 4.8 `claude-opus-4-8` orchestration;
extraction upstream DeepSeek `deepseek-chat`).

Implication: **a reference-free *surface/fluency* heuristic is near-useless for
adequacy.** Calibrated on the 320-row labelled
[`gold/gold_set.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl),
the proxy separates semantically-acceptable from defective rows at only
**ranking AUC ≈ 0.58** — a `wrong-sense` gloss is as clean/short/Cyrillic as a
correct one, so the form-based signal can't tell them apart. What *does* protect
the publication-grade A stamp is (a) the consensus gate and (b) the A-gate's
conservatism (0 defective gold rows ever reached A). Anyone tempted to lean on a
cheap reference-free QE for semantic filtering should instead weight consensus /
human adjudication, and reserve a *trained adequacy* model (COMET-QE, the
`--qe comet` hook) for the real QE signal.

> **Source:** MG correction mid-session ("It exists as Jim Funderburk repo, both
> Indische Sprüche editions"), verified via `gh api`/`curl` against
> `sanskrit-lexicon-scans/boesp1`+`boesp2` and `sanskrit-lexicon/PWG#87`,
> Sonnet 5 `claude-sonnet-5` · 2026-07-03

---

### §61. The reverse dictionary's 30 sources split ~18 PD vs ~10 in-copyright — the merged headword list is not automatically publishable

🔴 **The ~266,820-word reverse Sanskrit dictionary merges 30 source dictionaries
(1822–2005) whose rights status splits ~18 safely public domain / 2 likely-PD-verify /
7 clearly in copyright (Kochergina 1978 → RF ~2088, Turner 1962–85 → ~2053, Mylius 1975,
Pujol 2005, Edgerton 1953, Stchoupak–Nitti–Renou 1932, Vettam Mani 1979) / 1 own-license
(Huet) / 2 unclear — so publishing the merged headword list openly is a genuine legal
judgment, not a default.**

Evidence: per-source classification of all 30 sources (editions + compiler/author death
years) in
[`ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md` §3.1](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md),
built from the compiler's own bibliography
([`Словари-источники.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D0%B8-%D0%B8%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%D0%B8.mdx)).

Implication: any session touching publication of merged multi-dictionary data (this list,
or a future union headword release) must route through the §3.1 rights table and the open
`@DECIDE` in
[`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
§ Waiting on Me — options: (a) publish all on the facts-not-expression reading, (b) PD-only
subset (unique-to-risky-source count = H270 step 5), (c) restricted tier (kosha pattern).
A descriptive *paper* about the resource is NOT gated by the ruling — only the data tier is.

> **Source:** H265 analysis ([PR #207](https://github.com/gasyoun/SanskritLexicography/pull/207)),
> Fable 5 `claude-fable-5` · 2026-07-07

---

### §71. PWG marks case government explicitly ≈3,853 times across ≈3,222 senses — a deterministic census, not an estimate

> _Was §62 until 11-07-2026, renumbered — duplicate key (§62 was already taken by the varga-distribution finding)._

🟠 **Böhtlingk-Roth state case government (управление; the `snih` + loc. class) explicitly
≈3,853 times in the German sense text — 2,309 parenthesized single-case markers
(`(<ab>acc.</ab>)` 1,102 · loc 385 · instr 270 · gen 245 · abl 190 · dat 117), only 40
parenthesized case-VARIATION groups (`loc. und gen.` / `oder`), and 1,504 prose
`mit (dem) <ab>case</ab>` phrases — across ≈3,222 sense units in 1,476 entries; and
verbs are a MINORITY of the marker-bearing entries (417 of 1,476; adjectives 327,
nominals 241, indeclinables 64), so a government layer restricted to verb roots would
miss ~70% of the phenomenon.**

Measured by the deterministic, selftest-gated
[`RussianTranslation/src/government_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_census.py)
over raw `csl-orig/v02/pwg/pwg.txt` (`<ls>` spans stripped; parenthesized `nom.`/`voc.`
segregated as citation-form notes); 30/30 seeded spot-check precision. Counts are a
**floor**: multi-case continuations after `mit` (e.g. `mit abl. instr. oder gen.`) count
their first case only. The per-sense schema slot `government` exists in
[`schemas/pwg_ru_final_card.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_ru_final_card.schema.json)
but is populated on **0 of 11,261** live store rows; 510 store rows carry a marker in
their `de` field (backfill must parse `de` — Russian preserves the markers in only
375/510 rows). Full tables + wiring spec:
[`RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md` §W3](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md);
build handoff [H338](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H338-Sonnet_RussianTranslation_pwg-ru-government-backfill_08.07.26.md).

> **Source:** H335 capability audit ([PR #227](https://github.com/gasyoun/SanskritLexicography/pull/227)),
> Fable 5 `claude-fable-5` · 2026-07-08

---

### §72. VedaWeb's `id_gra` token field IS the Grassmann `<L>` entry number — no fuzzy text-matching needed for a GRA↔VedaWeb crosswalk

> _Was §63 until 11-07-2026, renumbered — duplicate key (§63 was already taken by the vidyut dhātupāṭha finding)._

🟢 **VedaWeb 2.0's `lemmatization.json` export (H096) already carries a per-token
`id_gra` array resolved via its own `kosh.uni-koeln.de/cdsd/gra/restful/ids` API — and
that internal ID is exactly the Grassmann `<L>` entry number in
[`csl-orig/v02/gra/gra.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/gra/gra.txt)**
(confirmed live: `id_gra=79` → `<L>79<pc>0008<k1>agni…`; `id_gra=1824` →
`<L>1824<pc>0230<k1>Iq…`). H097 built the full crosswalk
([`gra_vedaweb_crosswalk.tsv`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/gra_vedaweb_crosswalk.tsv),
[report](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/GRA_CROSSWALK.md))
entirely from local `csl-orig` data — no bulk API calls, no accent-normalization text
matching (§36's transcoder pitfalls don't apply to a plain ID join). Coverage: 9,945/12,785
GRA entries (77.8%), 9,475/11,108 unique `key1` headwords (85.3%) attested ≥1× in RV;
192,637 linked token occurrences. Only 1,633 headwords are unattested, and a spot-check
traced these to compound-member-only stems ("enthalten in …") rather than a matching gap.

**Caveat:** `lemmatization.json`'s 164,758 tokens all carry a non-empty `id_gra` — the
export appears pre-filtered to dictionary-linkable content words, not a full RV word
census. Occurrence counts here mean "attested via VedaWeb's curated linking layer," not
an exhaustive RV frequency count.

**Implication for future GRA/PWG/MW × VedaWeb work:** the `<L>`-number-as-ID pattern likely
generalizes — `lemmatization.json` also carries `id_mw` and `id_pwg` fields with the same
kosh RESTful API backing, so an MW↔VedaWeb or PWG↔VedaWeb crosswalk (if ever queued) should
check the analogous `<L>`-number identity first rather than re-deriving a text match.

> **Source:** direct inspection of `VisualDCS/non-derived/vedaweb/lemmatization.json` +
> one live `kosh.uni-koeln.de` API probe, Sonnet 5 `claude-sonnet-5` · 2026-07-08 (H097)

---

### §73. VedaWeb 2.0's "CC BY 4.0 for everything" claim is not machine-confirmed — only 2/36 catalog resources carry an explicit license field

> _Was §64 until 11-07-2026, renumbered — duplicate key (§64 was already taken by the PW-only-headwords finding)._

🟠 **Re-checking the VedaWeb 2.0 catalog's own `license`/`licenseUrl` fields (not the
`ROADMAP_VEDAWEB_REUSE.md` summary) found `license: null` on 34 of 36 resources.** Only
the Zurich AVP Edition (Zehnder et al./Hellwig et al. 2024) and the Würzburger AV Text
(Kim 2025) carry an explicit license (`CC BY 4.0` and `CC BY-SA 4.0` respectively). The
platform's own site-notice segment (`GET /api/platform/segments/6669938faf86e41764a1502a`)
states *"Individual resources provide their own citation guidelines… please use these for
citing specific data"* — i.e. VedaWeb's stated policy is per-resource **citation**, not a
blanket redistribution **license**. No platform-wide content-license text was found
anywhere on `/api/platform` (about/footer/privacy/site-notice); the only license string
present platform-wide is for the Tekst **software** (`AGPL-3.0-or-later`), unrelated to
the hosted dictionary/translation/annotation data.

This does not retroactively invalidate the four layers [H096](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H096-Sonnet_VisualDCS_vedaweb_feed_export_03.07.26.md)
already landed (Casaretto morphology, lemmatization, Scarlata & Widmer accented text,
Lubotsky padapāṭha) — those are VedaWeb-team-authored derived scholarship, not
third-party in-copyright translator prose, a materially different rights posture. But it
does mean the blanket "CC BY 4.0" framing carried through `ROADMAP_VEDAWEB_REUSE.md` was
an unverified assumption from an early on-ramp probe, not a re-confirmed fact — a
translation like Elizarenkova's Russian Rig-Veda (translator died 2007, in copyright to
~2078 under Russian life+70 term) is a fundamentally different case than VedaWeb's own
annotation layer, regardless of how the platform's hosting terms are eventually read.

Implication: any future VedaWeb-derived feed with a `license: null` catalog entry needs
its own rights call before landing (bulk import), not an inherited blanket assumption —
see [`VisualDCS/non-derived/vedaweb/LAYERS_TRIAGE.md`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/LAYERS_TRIAGE.md)
for the full 36-layer table.

**✅ Resolved 08-07-2026:** [H359](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H359-Sonnet_Uprava_vedaweb_rights_outreach_send_08.07.26.md)'s
outreach email to VedaWeb got an explicit written reply from Prof. Daniel Kölligan
(writing also on behalf of Prof. Uta Reinöhl): the 4 candidate layers this finding flagged
as DECIDE (Metrical Data 2024, Elizarenkova RU, Geldner de, Grassmann de) are confirmed
**CC BY 4.0**, and — directly answering the "implication" above — VedaWeb confirmed the
34-null-license-field gap is a metadata omission on their side, not an absence of rights,
and committed to backfilling all 34 entries with CC BY 4.0. This retroactively confirms
H096's own blanket claim was correct, even though it had not been independently verified
at the time it was made. Full reply:
[`Uprava/handoffs/OUTREACH_2026-07-08_vedaweb_kolligan_reinohl_rights.md`](https://github.com/gasyoun/Uprava/blob/main/handoffs/OUTREACH_2026-07-08_vedaweb_kolligan_reinohl_rights.md).
The general lesson stands independent of this specific happy outcome: a `license: null`
field is not evidence of *no* rights, but it is also not evidence *of* rights — ask, don't
assume, and here asking took one email and about a day's turnaround.

> **Source:** H098 triage ([VisualDCS](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb)),
> Sonnet 5 `claude-sonnet-5` · 2026-07-08; resolution via H359, Sonnet 5 `claude-sonnet-5` · 2026-07-08

---

### §74. The ls-graph citation matrix is degenerate for MW — its top abbreviations sit unresolved; use the citation-apparatus siglum matrix for cross-dict citation profiles

> _Was §65 until 11-07-2026, renumbered — duplicate key (§65 was already taken by the DeepSeek word-alignment grounding finding)._

**Claim.** [`csl-atlas/data/citations/ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv)
(the H213 canonicalized dict×text citation graph) resolves **MW to only 5 texts**
(Ṛgveda, Buddhist, Brāhmaṇa, Inscriptions, Sāmaveda) — MW's actual top citation keys
(MBh. 22,990 · R. 9,049 · BhP. 6,979 · Kathās. 5,926 · Suśr. 5,690 …) all sit in
[`ls_citation_unresolved_top.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_unresolved_top.tsv),
because the graph's longest-prefix abbreviation resolution misses MW's dotted-siglum key.
Any pairwise similarity computed on that graph over an MW edge measures **resolver
coverage, not canon shape** — BEN~MW cosine = 0.0000 exactly, an artifact (compounded by
an unfolded `Rigveda` vs `Ṛgveda` variant on the BEN side). The H342 fourth-axis test
therefore took its citation vectors from the **citation-apparatus canonical-siglum
matrix** ([`src/data/dicts/citation-apparatus.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/citation-apparatus.json),
MW fully resolved: 320,828 tagged citations, Mahābhārata 28,058), keeping the ls-graph
cosine only as a flagged sensitivity column (rank agreement Spearman 0.7 across the 5
testable edges). Corollary measured in the same pass: only **7 of the 14** documented
L0-edge dictionaries have a validated `<ls>` citation adapter (PWG, PW, MW, AP90, AP,
SCH, BEN) — the agenda's "9 of the 13" estimate was optimistic; WIL/YAT/SHS/CCS/CAE/
MW72/BOP have none, so any per-edge citation statistic shrinks to n=5 edges. Full packet:
[`FOUR_AXIS_CITATION_INDEPENDENCE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/FOUR_AXIS_CITATION_INDEPENDENCE.md).

> **Source:** H342 PH2 CITE-4AXIS ([csl-atlas PR #233](https://github.com/sanskrit-lexicon/csl-atlas/pull/233)),
> Fable 5 `claude-fable-5` · 2026-07-08

### §66. The DCS `QL` frequency workbook's `SLP1` and length columns are truncated at ṣṭh/ḍh clusters

🔴 **[`VisualDCS/derived-data/QL/Распределение слов по длинне и частям речи.xlsx`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/QL/README.md)
silently drops everything after a ṣṭh/ḍh cluster in its `SLP1` column — and the
`Длинна в SLP1` column is computed from the truncated string.**
Evidence: `śreṣṭha → SrezW` (length 5, true `SrezWa` = 6); `yudhiṣṭhira → yuDizW` (6, true
`yuDizWira` = 9); `pṛṣṭhatas → pfzW` (4, true `pfzWatas` = 8); `āḍhya → AQ` (2, true `AQya`
= 4). **1 622 of 90 929 rows (1.8 %)** disagree with canonical
[`sanskrit_util.to_slp1`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py);
length is **under**-stated in 1 455 of them (mean −2.5 chars, max −32). Only 56 affected rows
have frequency ≥ 100, so corpus-wide statistics barely move — Spearman(len, freq) goes
−0.295 → −0.301 — but any **per-lemma** use of those two columns is simply wrong for them.
Implication: never read `SLP1` / `Длинна в SLP1` from this workbook directly; recompute from
the `IAST` column with `to_slp1`. The `Частота`, `IAST` and `Грамм.` columns are sound.

> **Source:** H457 · [`titov_length_recheck.py`](https://github.com/gasyoun/Uprava/blob/main/research/titov_length_recheck.py),
> Opus 4.8 `claude-opus-4-8` · 2026-07-10

### §67. In PWG, article size dwarfs every "parametric" statistic you can extract from the entry

🟠 **Any statistic counted off a PWG entry body (senses, glosses, cited phrases) is first and
foremost a measure of how long the article is — and article length tracks corpus frequency
(Spearman +0.497).**
Evidence: across 106 082 PWG headwords, mean entry size is **14 876 characters for the 394
headwords of Leonchenko's stable corpus core vs 439 for the rest (33.9×)**; 379/394 core
lemmas sit in the top decile of article size. Ranking the dictionary by raw entry size alone
recovers the corpus core better (**35.5 %** at top-394, tie-aware) than any counted parameter
(multiword citations 33.5 %, glosses 32.4 %, numbered senses 27.8 %, headword length 8.5 %;
random 0.37 %). Normalising per character collapses them (27.8 % → 0.8 %). At size-matched
comparison (caliper ±10 %, 372 pairs, ⟨chars⟩ 11 198 vs 11 197) sense counts **reverse sign**
— core 10.31 vs matched non-core 11.57, Wilcoxon p = 0.038 (±5 %: p = 0.030) — and cited
phrases stop discriminating altogether (p = 0.62).
Implication: any claim that a per-entry count indexes lexico-semantic structure **must** carry
an entry-size control. Without one you are measuring the lexicographer's attention, which is
itself a function of corpus frequency.

> **Source:** H457 · [`titov_control_entry_size.py`](https://github.com/gasyoun/Uprava/blob/main/research/titov_control_entry_size.py),
> data [`VisualDCS/derived-parametric-core/`](https://github.com/gasyoun/VisualDCS/blob/main/derived-parametric-core/README.md),
> full write-up in [`Uprava/research/slovar-kak-obekt-dissertacii.md`](https://github.com/gasyoun/Uprava/blob/main/research/slovar-kak-obekt-dissertacii.md) §4-quater,
> Opus 4.8 `claude-opus-4-8` · 2026-07-10

### §68. The Sanskrit spellchecker landscape: one dormant demo, one license-unsettled 543k wordlist, no occupant

> _A verbatim copy of this finding also sat earlier in the file under a duplicate "§56" heading until 11-07-2026 (double-appended by two 10-07 sessions, PRs #305/#307); the copy was removed — cite §68._

🟠 **No maintained flag-and-suggest Sanskrit spellchecker exists (verified 10-07-2026), and the
two nearest things both carry traps.** (1) The sanskrit-spellchecker.netlify.app demo M.G. named
in the 02-07 interview is the online interface of **Prasanna S., "Spellchecker for Sanskrit: The
Road Less Taken", ICON 2022** ([2022.icon-main.35](https://aclanthology.org/2022.icon-main.35/))
— identified via the paper's own footnote 14; 37,058-entry Paninian word-and-paradigm Hunspell
dictionary, **source never published, no license, dormant since ~2022** (all 117 of the author's
public repos enumerated; the announced Firefox/LibreOffice add-ons never appeared). (2)
**LibreOffice bundles a 543,758-entry `sa_IN` Hunspell pair since 10-01-2025**
([LibreOffice/dictionaries `sa_IN/`](https://github.com/LibreOffice/dictionaries/tree/master/sa_IN),
Shantanu Oak, wikipedia/wikisource-derived flat wordlist + `BREAK` stripping) whose **in-tree
license is formally unsettled** — a GPL-2 `COPYING` was added 05-05-2025 and reverted three days
later by a LibreOffice maintainer as contradicting per-file copyright; do NOT ingest that
wordlist, use it only as an evaluation baseline. Also verified absent: any `sa` pack in
wooorm/dictionaries or GNU aspell; any spellcheck component in sanscript/indic-transliteration
(transliteration-only, MIT); any suggestion surface in SCL (its old analyser-based web
spellchecker is defunct per the ICON paper) or the Heritage Platform (grey-rectangle flag only,
LGPLLR databanks). A44's related-work citation "contextual spell-checker, ISCLS 2024" was a
mis-attribution — that volume contains no spellchecking paper; corrected to Prasanna 2022.
[COLOGNE #91](https://github.com/sanskrit-lexicon/COLOGNE/issues/91) ("Hunspell for Sanskrit?")
has been open since 2016 — the demand signal for the planned SanskritSpellCheck web app, whose
niche (suggestion generation against a validated, provenance-carrying lexicon) is unoccupied.

> **Source:** [SanskritSpellCheck docs/PRIOR_ART.md](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/docs/PRIOR_ART.md)
> (H452, [PR #27](https://github.com/drdhaval2785/SanskritSpellCheck/pull/27), 3 parallel
> research agents, every claim fetch-backed), Fable 5 `claude-fable-5` · 2026-07-10

### §69. Hand-transcribed telemetry cannot adjudicate code-vs-infra — and a local-only ledger silently swaps your denominator

Two traps measured by the H462 audit of the pwg_ru launch ledgers (10-07-2026).
(1) **The decisive numbers were never in the payload.** Every H437/H442 code-vs-infra
conclusion leaned on kill-timeout and connection-error counts ("58 of 61 kill-timeouts",
"3 conn-errors") that existed only as `console.log` strings, hand-counted from Workflow
transcripts into
[`LAUNCH_FUCKUPS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
— the harness `summary` returned neither, and the ledger checker validated shape, never
classification. Re-deriving all 13 entries' classes from their own recorded evidence
overturned 2 of 13 — both from the 24 hours when hand-transcribed telemetry was
adjudicating exactly that question, and one mis-class kept the corrective effort aimed at
the heal budget for one more ~1.8 M-token launch. Rule: **any number a post-mortem will
cite must be returned by the run's payload, not transcribed from its logs** — counters are
cheap; add them the day the first post-mortem hand-counts something (fixed by returning
`kill_timeouts`/`conn_errors`/`heal_calls`/`kill_bisect_blocked` in the summary +
[`classify_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/classify_run.py)).
(2) **A gitignored ledger + worktree isolation = denominator swap.** The committed
[`LAUNCH_STATS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md)
reported "Windows launched: **3**" because it was harvested inside a worktree whose
local-only `output/window_ledger.jsonl` held just that worktree's launches — the main
checkout's ledger held **450 windows / 55 roots**, and the generated file carried no trace
of which ledger fed it. Worse, the medium50 launches of 08–10.07 (H317/H389/H437/H442,
~11 windows) exist in **no** surviving ledger at all: their worktrees' gitignored
`output/` died with the worktrees. Rule: **an auto-generated stats file must stamp its
data source and row count, and per-launch records belong in committed storage** (here:
the probe log's JSONL), never only in a worktree-local gitignored file.

> **Source:** [`RussianTranslation/LAUNCH_LEDGER_AUDIT_2026-07.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_LEDGER_AUDIT_2026-07.md)
> (H462), Fable 5 `claude-fable-5` · 2026-07-10

---

### §75. The full Devībhāgavata-purāṇa Sanskrit is NOT on GRETIL — only the Devigita fragment; the complete mūla lives on sanskritdocuments.org without `DbhP_` markers

> _Was §69 until 11-07-2026, renumbered — duplicate key (§69 was already taken by the launch-telemetry finding)._

Verified 2026-07-10 (H534, three-way check): GRETIL's own update history
([`hist.html`](http://gretil.sub.uni-goettingen.de/hist.html) #370) and TEI
catalogue ([`gretil.html`](http://gretil.sub.uni-goettingen.de/gretil.html)) list exactly
**one** Devī­bhāgavata item — "Devibhagavata-Purana: Devigita" (`sa_devIgItA.xml` /
[`dbhp_dgu.htm`](http://gretil.sub.uni-goettingen.de/gretil/1_sanskr/3_purana/dbhp_dgu.htm)),
covering **only book 7, adhyāyas 31–40**. There is **no full 12-skandha DBhP on GRETIL,
nor on any GitHub mirror** (a GRETIL mirror can only carry what GRETIL has). The
`DbhP_<skandha>,<chapter>.<verse>` marker convention exists **solely as a cross-reference
inside the Devigita file** (`= DbhP_7,31.1`); it was never applied to a complete DBhP
digitization anywhere.

The complete text (all 12 skandhas) **does** exist on **sanskritdocuments.org**
([doc_purana/devIbhAgavatam01.html … 12.html](https://sanskritdocuments.org/doc_purana/)),
as HTML carrying **Devanagari + IAST**, numbered `॥ chapter.verse ॥` **per skandha** — which
maps cleanly onto our `SKANDHA.CHAPTER.VERSE` scheme but does **not** carry `DbhP_` markers.

**Consequence for the DBhP corpus (H534):** the handoff's locked "align GRETIL Sanskrit"
decision is unexecutable as stated. The Ignatjev Russian is ingested **RU-only** (the
sanctioned per-verse fallback); the Sanskrit pane is a human `@DECIDE` (use
sanskritdocuments.org, or ship RU-only). The aligner
([`align_sanskrit.py`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/corpus_builder/align_sanskrit.py))
is already source-agnostic — it consumes any Sanskrit JSONL keyed by `SKANDHA.CHAPTER.VERSE`.

**New asset:** a reusable **PDF → canonical-JSONL → app-HTML** ingestion pipeline now exists
([`PDF_INGESTION_PIPELINE.md`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/corpus_builder/PDF_INGESTION_PIPELINE.md)),
the free-toolchain successor to the Delphi `cb.exe` for new print/PDF translations; DBhP
Skandha 1 (1181 verses, 429 comments) is ingested as
[`Data/devibhagavata-purana-1.html`](https://github.com/gasyoun/SamudraManthanam/blob/main/Index/lib/x86_64-win64/Data/devibhagavata-purana-1.html).

> **Source:** H534, Opus 4.8 (`claude-opus-4-8`), [SamudraManthanam PR #31](https://github.com/gasyoun/SamudraManthanam/pull/31) · 2026-07-10

### §78. DCS 2026 sqlite carries 531,747 sense-annotated tokens (`m_wordsem`) but NO local ID→gloss inventory — gold-scored WSD against MW senses is blocked until the inventory is recovered

> _Was §76 until 12-07-2026, renumbered — duplicate key (§76 was already taken by the MW→WordNet→semdom bridge finding, cited from FEATURES_INDEX C19; found during the H774 §77 append)._

Measured 11-07-2026 on `VisualDCS/src/DCS-data-2026/dcs_full.sqlite` (the only non-stub copy;
the repo-root and `src/` `dcs_full.sqlite` files are 0 bytes): `token.m_wordsem` is populated
on 531,747 of 5,688,416 tokens (9.3%) with bare numeric IDs (e.g. `śāstṛ`→`43017`), but the
DB's 8 tables include no decode table for them; `lemma.meanings` holds only lemma-level
`;`-separated gloss text, not the per-token sense inventory. Consequence: any
sense-disambiguation eval over DCS attestations (e.g. the H730 gloss-grounded WSD track,
[kosha docs/DEFGEN_MW_GLOSS_EVAL_PROTOCOL.md](https://github.com/gasyoun/kosha/blob/main/docs/DEFGEN_MW_GLOSS_EVAL_PROTOCOL.md))
can measure inter-model agreement only — no accuracy. The unlock is recovering the DCS
word-sense-ID inventory from the DCS CoNLL-U releases / upstream DB and mapping it onto MW
sense divisions. Until then, do not claim WSD accuracy numbers from this dump.

> Source: H730 defgen+WSD eval session · kosha/VisualDCS · 11-07-2026, Fable 5 (`claude-fable-5`).

### §77. Amarakosha and SIL semdom both bolt a formal annex onto a semantic taxonomy — and it is the same ~10% once polysemy is set aside

🔴 **Two semantic taxonomies built 1,500 years apart — the Amarakosha (~6th c. CE) and
SIL's semantic domains (semdom.org, field lexicography) — each needed a formal,
non-semantic annex their organizing principle could not absorb, and once the polysemy
register is set aside the annexes are the same relative size.**
Evidence (every number derived live by
[semdom_ak_annex_table.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annex_table.py)
from `amar.txt` + `semdom.json`; full table in
[SEMDOM_AK_CROSSWALK_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md)):
AK kāṇḍa 3 (viśeṣyanighna 326 · saṅkīrṇa 168 · nānārtha 1,995 · avyaya 103) =
2,592/5,590 synsets (46.4%); semdom top-level 9 "Grammar" = 168/1,792 domains (9.4%).
Direct branch counterparts exist only for the form-class vargas (avyaya ≈ 9.2.2 +
9.2.5–9.2.7, 8 domains; viśeṣyanighna ≈ 9.1.4 + 9.2.1, 2 domains). nānārtha (homonyms,
35.7% of the kosha on its own) has **no** semdom counterpart — semdom absorbs polysemy
structurally by listing a word under several domains — and with it set aside the
form-class annex proper converges: **AK 597/5,590 (10.7%) vs semdom 168/1,792 (9.4%)**.
Implication: for A58's §6 this is the paper's cleanest cross-epoch symmetry claim (state
it counted, never as prose analogy), and homonymy-as-a-bucket vs
homonymy-as-multiple-listing is the sharpest single design difference between a
memorized verse thesaurus and an elicitation taxonomy. Keep top-level 9 out of the
Level A crosswalk CSV — the annex parallel is a finding *about* the taxonomies, not a
semantic mapping.

> **Source:** H774 annex-table build (`data/semdom_ak_annex_table.py`, reusing
> `semdom_varga_crosswalk.py` loaders) · SanskritLexicography · 12-07-2026,
> Fable 5 (`claude-fable-5`).

---

### §79. DCS 2021→2026 "lost lemma" counts are mostly lemmatization-policy drift — a-privatives now resolve to their bases

**Naive 2021-vs-2026 DCS lemma comparisons overstate loss ~10×.** The 2026 CoNLL-U
master shows 1,761 lemma IDs attested in the 2021 relational export but absent from
the 2026 corpus (91,406 → 98,606 attested; H686). Those ids carry only **7,747 tokens
(0.17% of the 2021 corpus)**, and the highest-frequency ones are almost all
**a-privative adjectives/participles** — aprameya (284), anindita (227), avadhya
(191), aprāpta (125), asakta (94)… — words that did not leave the corpus: the 2026
lemmatization resolves privative/preverb compounds to their bases. The same policy
change makes the lemma "a" (ind) jump +18.3 per 10k (rank 112 → 32) — treat that
mover as segmentation drift, not usage drift. Genuine text loss is tiny: 4
fragmentary only-2021 commentaries, 892 tokens total; only 10 of 240 matched texts
shrank (max −873, Ṛgveda, −0.5%). Implication: any diachronic or coverage claim
built on DCS lemma-ID presence/absence across snapshots must first split
annotation-policy drift from content drift — and current statistics must come from
the 2026 master, never `DCS-data-2021/` (verdict registered in
[DRIFT_INTERPRETATION.md](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/DRIFT_INTERPRETATION.md)).

> **Source:** H686 delta supplement
> ([delta_supplement.py](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/delta_supplement.py),
> exact LemmaId cross-walk, [VisualDCS PR #40](https://github.com/gasyoun/VisualDCS/pull/40)) ·
> VisualDCS · 12-07-2026, Fable 5 (`claude-fable-5`).

---

### §80. DCS `text_sandhied` is largely DE-sandhied pada text in the Rāmāyaṇa — and locus joins fail across editions; a text-keyed 3-tier match (exact / consonant-skeleton / fuzzy) recovers it

Two traps for anyone crosswalking verse text onto the DCS corpus (hit in H759,
the НКРЯ Wave-2 annotation comparison). **(1) Loci don't join across editions:**
the Samudra Manthanam Rāmāyaṇa kāṇḍas are vulgate-numbered (77/119/75 sargas)
vs DCS's critical edition (76/111/71) — MBh 3 happens to match (both critical,
299 adhyāyas) but nothing guarantees it elsewhere. **(2) Even text matching
breaks on sandhi:** DCS's `sentence.text_sandhied` is, for the Rāmāyaṇa at
least, largely de-sandhied pada text (`sukhatantraḥ na ca alasaḥ`) where a
printed edition surface is sandhied (`sukhatantro nacālasaḥ`) — plain
normalization (strip spaces/punct) leaves exact-match rates as low as 11%
(Ayodhyā: 1,019 exact of 9,093 lines). A **consonant-skeleton tier** (delete
vowels + visarga + y/v, fold all nasals to m, guard with a ≥0.70 vowelled-string
difflib floor) recovers the sandhi class wholesale: Ayodhyā 38%→54% coverage,
MBh 3 98.3%→99.8%. The residue is then a genuine edition measurement — 795 of
801 probed unmatched Ayodhyā lines are absent from the *entire* DCS Rāmāyaṇa
(critical-edition excisions), so ~54–76% coverage on vulgate Rām kāṇḍas is the
true ceiling, not a matcher defect. Also: the 2026 DCS sqlite import carries 13
mojibake lemma strings (kḷp/ṝ-family, e.g. `kﾱp`) — filter and count them.

> **Source:** H759 3-path annotation comparison
> ([nkrya_annotate.py](https://github.com/gasyoun/SamudraManthanam/blob/main/web/corpus_builder/nkrya_annotate.py),
> [ANNOTATION_3PATH_COMPARISON.md](https://github.com/gasyoun/SamudraManthanam/blob/main/nkrya-parallel/export/ANNOTATION_3PATH_COMPARISON.md),
> [SamudraManthanam PR #43](https://github.com/gasyoun/SamudraManthanam/pull/43)) ·
> SamudraManthanam × VisualDCS · 12-07-2026, Fable 5 (`claude-fable-5`).

---

### §81. vidyut-cheda 0.4 lemmatizes derivatives to the dhātu ROOT (rāmaḥ → ram) where DCS uses the nominal stem — and over-segments epic verse 1.44×

Comparing vidyut output against DCS lemma annotation requires knowing two
systematic properties (measured on 40,269 epic half-verses, H759).
**(1) Lemma granularity:** vidyut's `Token.lemma` returns the dhātu root for
every derivative (*rāmaḥ* → *ram*, *varam* → *vṛ*, *vāk* → *vac*) where DCS
lemmatizes nominals to the stem (*rāma*, *vara*, *vāc*); for Basic
(non-kṛdanta) prātipadikas the stem is recoverable from
`Token.data.pratipadika_entry.pratipadika.text`, but kṛdantas keep the root —
any B↔C agreement metric must state which level it compares, or it measures
convention, not correctness. **(2) Segmentation quality on epic text:** vidyut
0.4 produced 293,775 tokens against 203,623 surface tokens (1.44×), shattering
long compounds and vṛddhi derivatives into short spurious roots
(*dhārtarāṣṭraiḥ* → 5 fragments); 5.4% of tokens carry no lemma; unparseable
input returns an **empty token list, not an error**. Net: B↔C lemma-set Jaccard
is only 0.28–0.35 vs DCS on fully-covered verses — fresh auto-tagging with
vidyut is not competitive with a DCS crosswalk on epic verse (per the standing
"vidyut display-only" caveat, now quantified).

> **Source:** H759 3-path annotation comparison
> ([annotation_3path_metrics.json](https://github.com/gasyoun/SamudraManthanam/blob/main/nkrya-parallel/export/annotation_3path_metrics.json)) ·
> SamudraManthanam · 12-07-2026, Fable 5 (`claude-fable-5`).

### §82. MW `<e>` encodes the 1899 print's headword typography (1 = Devanāgarī entry, 2 = roman-only, 3 = run-on compound; letter suffix = continuation record)

🟠 **The `<e>` attribute on MW `<L>` lines is the print's typographic entry level, and its
letter suffix marks body-continuation records of the same headword — one printed entry is
often several digital records.** Evidence: verified against the MW 1899 scan p. 1304
(Cologne MWScan `mw1304-hetumAtratA.pdf`) while building the EntryAnatomy specimen pages:
`heman` hom. 3 'gold' (`<e>1`, L 264121) prints with a Devanāgarī headword; `hemán` hom. 1
'impulse' (`<e>2`, L 264069) prints roman-only and capitalized; `hema—kakza` (`<e>3`,
L 264127) prints as the run-on compound "— kaksha" with the first member elided; and
L 264122–264125 (`<e>1A`) are ¦-initial continuation records the print joins to L 264121
with semicolons. Implication: renderers must group records by k1 + adjacency + the `<e>`
letter suffix to rebuild printed paragraphs (see `mw_paragraph()` in
[EntryAnatomy/build_entry_anatomy.py](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/build_entry_anatomy.py)),
and counting "MW entries" by raw `<L>` records overcounts printed entries.

> Source: EntryAnatomy specimen-page build (H780) · SanskritLexicography · 12-07-2026, Fable 5 (`claude-fable-5`).

### §83. MW and the Petersburg dictionaries are NOT independent witnesses on inventory or apparatus — do not count their agreement as corroboration; but no shared *error* has ever been found

Monier-Williams inherited Böhtlingk's **apparatus** — which words to enter, which
texts to cite and in what order, how to divide homonyms — measured six ways in
A10 ([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md)).
The new **shared-omission** cut (F9, A10 §3.5) settles the negative-space side:
on 6,941 real words attested in both indigenous kośas (SKD ∩ VCP), whether MW
enters a word is **≈8× more predicted by PWG's decision** than by an independent
compiler's (gap-sensitivity 12.3× vs Apte 1.5×). **Consequence for any downstream
analysis:** PWG/PW ↔ MW agreement — shared headwords, shared citations, shared
sense structure, "the tradition agrees" tallies (cf. the etymology-extraction
90–100% agreement, [`project_cologne_etymology_extraction`]) — is **inheritance,
not independent confirmation.** When counting how many *independent* authorities
back a reading, PWG, PW **and** MW collapse to roughly **one** European witness;
the genuinely independent European-tradition control is **Apte**, and the indigenous
kośas (SKD, VCP, Amarakośa) are the independent non-European anchor.

The **positive counter-fact**, equally load-bearing: MW carries over **none** of
Böhtlingk's mechanical errors (F4b Ahlborn ≈0%, F4a 0 shared print errors) and
recomposed its English prose (F3/F6), and it independently supplies **54.6%** of the
real indigenous words PWG omits — *more* than Apte. So the non-independence is of
**scholarship/inventory**, not of typesetting or prose. Documentary basis: Böhtlingk's
1883 *pw* preface (35 cited passages) and the Böhtlingk↔Max-Müller correspondence,
Stache-Weiske 2015 ([`papers/Stache-Weiske_Bö-MW.notes.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/Stache-Weiske_Bö-MW.notes.md)).

**On the shared-*erroneous-citation* avenue — a measured null, not a closed door.**
The Lachmann-style airtight proof (a citation *wrong* against the text, present in
both dicts) returned measured nulls on the corpora tested: 1/587 resolvable against
DCS (edition-mismatch block), and 0 shared errors against the Kinjawadekar Harivaṃśa
vulgate. That is a **recorded negative result on those candidate sets**, not evidence
of independence and not proof the avenue is exhausted — a Nilakantha-**vulgate** full
Mahābhārata e-text would reopen it (see [`DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8/§8b). The
untested shared-error surfaces remain **shared headword/gloss misprints and copied
sense-order** (F5 citation-order 0.811 is suggestive but not the meaning-order Müller
named).

> **Source:** csl-atlas A10 §3.5 / F9
> ([`f9_shared_omission.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f9_shared_omission.py),
> [`SHARED_OMISSION_TEST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SHARED_OMISSION_TEST.md),
> [csl-atlas PR #263](https://github.com/sanskrit-lexicon/csl-atlas/pull/263)) ·
> [H796](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H796-Opus_csl-atlas_boehtlingk_mw_shared_omission_test_12.07.26.md) ·
> 12-07-2026, Opus 4.8 (`claude-opus-4-8`).
> ↔ [ASSUMPTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (independence premise for tradition-agreement counts) · [DEAD_ENDS.md §8](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (shared-erroneous-citation null).

---

### §84. pwg_ru readiness audit: `[NWS:]` attribution and `{%…%}`-delimiter dropping are NOT audit-contract defects; observed token/cost economy is `not_recoverable`; store-membership ≠ audit-clean

When auditing pwg_ru no_pwg output quality (H911 LOCAL-READINESS gate), three reusable traps:

1. **Do not flag `[NWS:]` prefixes or dropped `{%…%}` gloss delimiters as fidelity defects.** The
   audit contract's STRANDED-ANCHOR class is specifically leftover `{Tn}` **mask** placeholders
   ([`stage2_pregate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/stage2_pregate.py) `ANCHOR_RE`), **not** `[NWS:]` layer markers; the semantic gate flags the *opposite* of delimiter-dropping —
   **`untranslated_braced_german_gloss`** (German left *inside* the braces). The surviving
   `no_pwg_w05_rq1` audit passed cards with both `[NWS:]` and dropped-`{%…%}` clean. The real recurring
   defect classes are **`missing_senses` (SAN-LOSS)**, `untranslated_braced_german_gloss`,
   `likely_circular_gloss`, `possible_sense_compression`, and the infra pair
   `kill-timeout`/`selfheal-nothing-resolved`.
2. **Observed per-clean economy is `not_recoverable`, never $0.** `run_events.jsonl` records calls +
   `elapsed_ms` but **no token field**; H818 dashboards carry `cost:null`. So observed calls/clean and
   $/clean cannot be measured from existing evidence — the deterministic **projection** ($58.09/100hw)
   is a separate, optimistic floor and must not be substituted for observed performance.
   **Operationalized 16-07-2026 (H963):** because observed per-window cost is usually unrecoverable
   (LAUNCH_STATS records output-tokens on 1/458 windows), the bounded staged runner treats a
   requested cost/quota ceiling as **fail-closed** — a window whose cost is UNEVALUABLE stops the run
   with `STOP_COST_UNEVALUABLE` rather than assuming $0 and continuing
   ([`bounded_staged_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run.py)
   + `bounded_supervisor.strict_cost_fn`; `economy_ledger.gate(strict=True)` is the opt-in ledger gate,
   legacy None-skip unchanged).
3. **Current-store membership is not the audit verdict and not exact provenance.** Absence ≠ audit
   rejection; presence ≠ *this* output passed. Keep reviewer quality, sealed audit verdict, and
   promotion status as **three separate** measurements; an audit-to-promotion escape needs an exact
   key + sense/card + RU-hash + promotion-provenance join to allege.

> **Source:** H911 LOCAL-READINESS quality/economy gate
> ([report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md),
> [census](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_quality_economy_census.json),
> [SanskritLexicography PR #460](https://github.com/gasyoun/SanskritLexicography/pull/460)) ·
> [H911](https://github.com/gasyoun/Uprava/blob/main/handoffs/H911-Fable_SanskritLexicography_h818-local-quality-economy-readiness-gate_14.07.26.md) ·
> 14-07-2026, Opus 4.8 (`claude-opus-4-8[1m]`, owner-authorized executor-override of minted Fable 5).

---

### §88. The DCS snapshot's UD dependency slice is real but VEDIC-SKEWED — syntax studies get counterexample hunts, not classical norms

**Probed 16-07-2026** (Fable 5 `claude-fable-5`, H1008, pinned `dcs_full.sqlite`): 74 texts
carry `has_dependencies=1`, totalling **223,751 dep-annotated tokens** across 71 UD relations,
with subordination visible in volume (acl 5,842 · advcl 4,024 · ccomp 2,884 · mark 8,124 ·
xcomp 1,392 · csubj 638). BUT every one of the top-12 dep-annotated texts is Vedic-sphere
(RV 34.7k, AV ×2, brāhmaṇas, upaniṣads, śrautasūtras) — there is effectively no classical
prose/kāvya dependency data in the snapshot. Consequence for any DCS-based syntax study:
**counterexample hunts against universals are feasible now** (a violation found in 224k
tokens refutes regardless of skew), while **classical word-order/subordination NORMS are
data-blocked** — do not present Vedic-slice rates as "Sanskrit" rates. Companion facts:
§86 (verbal-feature annotation collapse), §87 (the period map to slice by).

### §87. A curated DCS text→period map EXISTS (consume, don't rebuild) — and the purāṇas carry a measured epic-imitative signature on two independent axes

**Built 16-07-2026** (Fable 5 `claude-fable-5`, H1000): the `PERIOD_MAP` dict in
[`period_style_gradient.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/ZalizniakOcherk_1978/period_style_gradient.py)
assigns the 41 token-heaviest DCS texts (4.07M tokens = 71.6% of the pinned
`dcs_full.sqlite`) to веды/эпос/классика with a dating basis per text, purāṇas as a
separate bucket, and Buddhist-hybrid texts + lexica excluded as register-confounded.
Any DCS-based diachronic study should IMPORT this map (the H1001
[causative detector](https://github.com/gasyoun/SanskritGrammar/blob/main/ZalizniakOcherk_1978/causative_grade_detector.py)
already does) rather than re-derive text datings. **Measured bonus, replicated on two
independent axes:** the purāṇas land BETWEEN epic and classical — compound membership
48.1% vs epic 40.5% / classical 57.3% (H1000), guṇa-causative share 26.3% vs epic
25.9% / classical 20.8% (H1001) — i.e. their late verse measurably imitates epic
LANGUAGE, not just epic genre. Treat 'puranic' as its own stratum in any period
slicing; folding purāṇas into 'late classical' dilutes real diachronic signals.

### §86. DCS verbal-feature annotation density collapses for later texts — feats-based diachronic metrics measure ANNOTATION, not language

**Measured 16-07-2026** (Fable 5 `claude-fable-5`, H1000, on the pinned `dcs_full.sqlite`,
dcs-conllu 04e0778): tagged past participles (`feat_verbform=Part` + `feat_tense=Past`) fall
Ṛgveda **1,874** → Mahābhārata 465 → Kathāsaritsāgara 14 → Daśakumāracarita **0** — in a
7th-century prose text saturated with ta-participles. Person-annotation density falls in
parallel (13.9% of tokens → 6.4%). Any cross-text metric built on DCS verbal FEATURES
(finite-verb rates, participle rates, nominal-sentence detection via finiteness) therefore
tracks the corpus's annotation coverage, not Sanskrit. **upos, by contrast, is 100% complete
on every text probed**, and the mwt segmentation (surface-word spans) is likewise structural —
diachronic/style comparisons must be built on those layers, with feats-based signals at most
CONDITIONAL (internally normalized, e.g. voice share among annotated finite verbs) and never
verdict-bearing. First consumer: SanskritGrammar's
[`period_style_gradient.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/ZalizniakOcherk_1978/period_style_gradient.py)
(H1000, §207 style-gradient measurement — the naive feats-based draft produced an inverted
ta-participle "gradient" before this was caught; the shipped verdict rests on upos/mwt axes
only). Related: §81 (vidyut-cheda lemmatization divergence — a different DCS-derived-layer
trap in the same family).

### §85. A clean-looking subset is not promotable evidence when its audit or execution contract failed

The pwg_ru coordinator previously built `clean_output` from every non-null card and mapped
any such subset to `ready_partial`, regardless of whether `audit_window.py` had reported
`stale_artifact`, a crashed/blocked gate, or another non-completed state. Nominal/no-PWG
runs compounded this by omitting `--root`; the provenance checker treated that as a warning
and skipped input/rootmap validation. A stale result could therefore contain plausible cards
and cross the promotion boundary without a trustworthy completed audit.

The reusable rule is **state-boundary evidence must fail closed**: partial promotion is
allowed only from explicit completed partial states (`needs_requeue` or `transient_only`),
the result must match its prepared execution manifest (root/mode/hashes), and selected keys
must occur exactly once. Promotion must re-read the sealed audit/status artifacts and verify
the clean-output hash instead of trusting mutable coordinator state alone. The same pass also
made overwrite-style control artifacts atomic; a truncated JSON status/report must never be
interpreted as an operational verdict.

The review after PR #478 exposed the same rule at two later boundaries. First, narrowing a
two-key run to a one-key requeue creates a **new provenance contract**: reusing the initial
manifest makes the valid retry fail exact coverage, while dropping the manifest would reopen
the bypass. Keep the retry on the same lease, but mint and retain an attempt-specific manifest
and read subsequent retry files from the latest audit directory. Second, a staged plan is not
an execution set: future unprepared rows must not enter acceptance denominators, and an omitted
residual-only chunk must not consume the requested preparation quota. Scope acceptance to
prepared lease IDs and count successful preparations independently of deterministic indices.

The review after PR #482 exposed three more instances of the boundary problem. A coordinator
could still reconstruct work from mutable split-key files without proving that the keys came
from the lease's original manifest; selecting the transient lane could silently lose a pending
defect lane (or the reverse); and a hard interruption after directory creation could make the
state counter reuse an existing `rqNN-*` path. The resolution is a durable, additive backlog:
seal the attempt-zero manifest path/hash as the lease key universe, bind every pending key to
its classifying audit-report path/hash, and carry the unselected lane through the next audit and
promotion. Allocate from the maximum of state, manifest history, and disk; preserve and report
unreferenced attempt directories as orphans, never auto-adopt or delete them. Materialize the
selected keys and conservative defect fragment hashes inside the new attempt before generation.
This keeps retry cost policy split by lane without allowing one lane to erase the other.

The H963 evidence review found the same boundary error inside the card payload itself. Promotion
accepted fields that the restoration code did not cover, and the only schema validator ran in CI
against a clean fixture rather than against audited/promoted output. On the 11,605-row store this
left **668 normally recoverable rows with raw `{Tn}` placeholders, 468 rows with `h == null`, and two
`banD` rows whose placeholder index is outside the source mask map**. The reusable rule extends from
artifact state to payload shape: the restoration-field set must have one owner across generated JS
and Python, every unresolved token must fail closed, and promotion must independently validate the
exact live card rather than treating a fixture-only validator as evidence. A second evidence lesson:
kill-budget saturation is admission telemetry, not proof of route-independent undeliverability;
population claims require serial whole-card measurements, not an `n=2` ratio extrapolation.

H1080 closed the measured damage without a model call. Exact historical harness maps and
content-addressed raw inputs restored 668 placeholder rows and all 468 null owners; the two
out-of-range `banD` rows were removed into a hash-sealed quarantine. The canonical store moved
from 11,605 rows (`cc1d544e…`) to 11,603 (`f15caf7d…`) with zero raw tokens and zero null `h`, and
the RU card TM was rebuilt once. The forward rule is now executable at every boundary: audit and
promotion validate the live card; autosplit/top-up retain record owners; promotion requires an
existing store by default and independently refuses synthetic, foreign, duplicate, or malformed
inputs before a fsynced atomic replacement. The full repair evidence is tracked in
`RussianTranslation/pwg_ru/h1080/H1080_STORE_REPAIR_REPORT_2026-07-17.md`.

The launch-control follow-up closes the identity boundary as well. A friendly name such as `c4`
does not prove which credential directory or billing identity a process will use, and per-manifest
width caps do not prevent two independent manifests from spending through the same profile. New
production work therefore uses manifest v2: slot + canonical config-directory fingerprint + route/
lane/model/validation + per-key real/control class. The executor verifies the roster and sealed
fingerprint and takes one global active-call claim keyed by that fingerprint. V1 stays readable as
history but is non-promotable; controls are explicitly typed and rejected by promotion. On Windows,
an unresolved npm `.cmd` shim is a configuration failure, not a fallback. Probe GO is likewise a
derived typed verdict: named production policy, representative schema success, zero connection
errors, and latency strictly below 30 seconds.

> **Source:** RussianTranslation audit-findings implementation
> ([PR #478](https://github.com/gasyoun/SanskritLexicography/pull/478),
> [follow-up PR #482](https://github.com/gasyoun/SanskritLexicography/pull/482),
> [review-fix PR #483](https://github.com/gasyoun/SanskritLexicography/pull/483))
> ([`coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py),
> [`window_provenance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_provenance.py),
> [`window_common.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_common.py),
> [`max_account_orchestrator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py),
> [`no_pwg_scale_plan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py)) ·
> 15-07-2026, Codex/GPT-5.

### §86. Samāsa-type frequency does not exist in any org corpus — and the grammarians' canonical examples are corpus-ghosts (8/58 attested, max freq 147)

Any plan to put a frequency layer on the samāsa taxonomy — the
[SamasaChakram](https://github.com/gasyoun/SamasaChakram) wheel's 58 leaf subtypes, a
distribution table, a "which compound type is commonest" claim — runs into two independent
walls, both measured rather than assumed.

**Wall 1 — no type label anywhere.** DCS carries `token.feat_case='Cpd'` on **841 052**
compound members across 396 571 sentences, but **no samāsa-type annotation** (evidence limit
EM4, confirmed hard in
[H989](https://github.com/gasyoun/Uprava/blob/main/handoffs/H989-Opus_SanskritGrammar_sangram-p4-tatpurusa_15.07.26.md)).
The VisualDCS compound archive does not rescue this: despite its name,
[`derived-data/Kompozity/категории композитов.ods`](https://github.com/gasyoun/VisualDCS/tree/main/derived-data/Kompozity)
(401 490 rows, columns `Композит · Состав · Основ · Частота · <per-text counts>`, 417 410
compound tokens total) means by *категория* the **number of stems**, not the samāsa class —
`rājendra; rājan indra; 2; 863; …`. Composition depth is fully populated; type is absent.

**Wall 2 — the textbook examples are not corpus words.** The obvious fallback ("show each
leaf's canonical example's corpus frequency") was measured against that 401k-row table: of
the wheel's 58 canonical examples, **8 are attested at all** (14%), with frequencies of
147 (`puruṣavyāghra`), 37 (`rājaputra`), 10, 8, 1, 1, 1, and **0** (`saputra`). The other 50
— `grāmagata`, `kumbhakāra`, `yudhiṣṭhira`, `rājadanta`, `vanavāsa`, `śītoṣṇa` … — do not
occur. Matching was stem-normalized (final `ḥ/ṃ/m/ṁ` stripped, brackets/hyphens removed);
the failure is real, not an encoding artifact: 17/58 appear in the bare
[`CompDic.csv`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Kompozity/CompDic.csv)
headword list, which carries no counts.

The reusable rule: **the vyākaraṇa example inventory is a pedagogical artifact, not a corpus
sample** — these forms were minted to be minimal and memorable, and their rarity measures the
grammarians' taste, not their type's productivity. `rājaputra`'s 37 tokens say nothing about
how common ṣaṣṭhī-tatpuruṣa is (it is everywhere). So an example-frequency layer is worse
than no layer: it is a *type*-frequency claim in disguise, and it inverts the truth on the
most-taught subtypes. Frequency at the 4 coarse classes is reachable only via new annotation
(H989's κ-gated n≈120 sample, or an external labeller such as Kulkarni's SCL compound-type
identifier / the Krishna et al. 2016 labelled set — 4 classes, never 58); frequency at leaf
granularity has no path from present data at all.

> **Source:** measured 16-07-2026 while scoping a frequency layer for the
> [samāsa-cakra wheel](https://gasyoun.github.io/SamasaChakram/) — stem-normalized lookup of
> [`samasacakra-taxonomy.json`](https://github.com/gasyoun/SamasaChakram/blob/main/samasacakra/samasacakra-taxonomy.json)'s
> 58 `ex` values against `категории композитов.ods` (streamed via `iterparse`) and
> [`parts.csv`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Kompozity/parts.csv)
> (2 663 rows, 0 hits — too small a slice to matter). Corpus counts for wall 1 quoted from
> H989's scout against the pinned `dcs_full.sqlite` (`source_commit 04e0778`). Related: §66
> (a different DCS frequency-workbook trap) · Opus 4.8 (`claude-opus-4-8`).

---

_Started 2026-06-26 (relocated from `Uprava/FINDINGS.md`, which now holds **non-Sanskrit**
findings). Appended on a regular basis — add findings as they're discovered; this is the
shared memory of "things we measured that aren't obvious from the code."_

_Dr. Mārcis Gasūns_

### §87. The roadmap's "OBS-T κ=0.42" was a phantom figure — no measured agreement exists for any OBS-T axis

Found 17-07-2026 (Fable 5 `claude-fable-5`, H1074, while drafting A31). The P5 row and a G4 cell
of [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
claimed "OBS-T (50,953 corrections, two-axis typology, **κ=0.42**)" / "OBS-T already demonstrated
Fleiss κ=0.42 tooling". Neither number survives contact with the evidence base:
[`csl-observatory/validation/gold_metrics.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_metrics.json)
records **Cohen κ = 0.0 over 4 incidental pairs** (the `gold_component_2` second-annotator column
of [`gold_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv)
is entirely blank), and both OBS-T paper drafts explicitly state "We report no κ here". The
52,498-event released snapshot also supersedes the 50,953 cut the row still cited. Both cells
corrected 17-07-2026 in the same pass that shipped the A31 draft.

The reusable rule: **a roadmap/registry cell is not provenance — before citing any statistic
from a planning doc into a paper, re-derive it from the committed dataset or metrics file it
claims to summarize.** Planning docs get written ahead of the evidence and are not regenerated
when the evidence lands (or fails to land); a phantom κ that reached a Lexikos submission would
have been a retraction-class defect. Same failure class as §52 (hand-copied queue drift), on the
statistics axis.

### §89. MW writes `<ls>` citations in TWO markup shapes and locates them in roman as well as arabic — a literal `<ls>` regex undercounts its apparatus by 28.6%, and case-folding the roman test erases the `L.` hedge

**Measured 16-07-2026** (Fable 5 `claude-fable-5`, [H1076](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1076-Fable_MWS_a18-citation-registers-draft_16.07.26.md),
over `csl-orig` `v02/mw/mw.txt`; script + artifacts:
[MWS/papers/p3_citation_registers/register_census/](https://github.com/sanskrit-lexicon/MWS/blob/master/papers/p3_citation_registers/register_census/register_census.py)).
Three traps, all in *counting* MW's citation apparatus, all of which inflate how well-evidenced it looks:

1. **Two tag shapes.** MW writes both `<ls>Pāṇ. vi, 2, 161</ls>` (siglum + locator in the content) and
   `<ls n="RV.">vii, 96, 3</ls>` (siglum in `@n`, locator in the content) — and sometimes splits the
   locator across both: `<ls n="RV. viii, 96,">15</ls>`. **8,668 citations (2.7%)** use the attributed
   shape. A literal `<ls>` regex sees none of them, so MW's apparatus is **320,828**, not the widely
   quoted 312,160. ⇒ the citation's full text is `@n + content`; swapping in `<ls[^>]*>` and parsing
   the content alone is still wrong.
2. **Roman locators.** `<ls>ŚBr. xiv</ls>` is located; **4,866** plain-shape citations carry a roman-only
   locator. An arabic-digit rule (`re.compile(r"\d")`) scores every one as sourceless. Together with (1),
   MW's locator-bearing count is **60,820 (18.96%)**, not 47,289 (15.15%) — a **28.6%** undercount.
3. **The roman test MUST be case-sensitive.** MW's roman locators are lowercase. Fold case and the
   hedge `L.` reads as roman 50, and capitalised sigla (`Vi.`, `Ci.`) read as roman numerals: in this
   census's own first run that silently reclassified **~46,000** citations as attested and drove the
   `L.` stratum to **zero**. It was caught only because `<ls>L.</ls>` = 40,212 was independently known.

**Consequence.** [csl-atlas' `data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json)
MW row carries (1) and (2) — its extractor is literal at
[`parse_cslorig.py:41`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/parse_cslorig.py#L41).
Its published figures (`ls: 312160`, `lsWithLocator: 47289`) **reproduce exactly** under its own rule, which
localises the divergence to markup shape rather than a parser disagreement. Regeneration is queued as
[H1086](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1086-Sonnet_csl-atlas_mw-row-regenerate-ls-shapes_17.07.26.md)
(corpus-wide — the fix touches every `<ls>`-bearing dict). The atlas's direction and corpus-wide conclusion
are **not** in dispute; MW stays a locator-poor Register-A dictionary.

**Second-order consequence — the number that travelled.** MWS' `ROADMAP.md` + `SYNTHESIS.md` gave MW's
apparatus as "22.3% meta + **40.2%** bare-locator", implying a ~37.5% text-linkable ceiling. The 40.2% was
never an MW measurement: it is the **corpus-wide** CDSL bare share, imported from a since-superseded
**43-dictionary** revision of `CITATION_REGISTERS.md` (an aggregate dominated by PWG at 4.61 `<ls>`/entry
against MW's 1.09), and the two components were computed over different populations — so `22.3% + 40.2%`
was never a valid subtraction from 100%. MW's real ceiling is **~19%**: a scan-link programme's prize is
one citation in five, not two in five. Corrected in place 16-07-2026.

**Reusable rule.** Any figure characterising a historical apparatus must state **which markup shapes it
counted** and **what it treated as a locator**, in the same breath as the number — for MW those two
decisions move the headline by 28.6% and the ceiling by ~2×. Same defect class as the atlas's own earlier
`iti` fix (a space-or-quote rule undercounted KRM ~3× until a word-boundary rule replaced it): an
assumption about markup shape, living in a regex, read downstream as a fact about the lexicographer.
Never report a `<ls>`-derived count without the extraction rule beside it.
