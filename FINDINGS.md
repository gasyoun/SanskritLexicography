# FINDINGS — cross-repo empirical registry

_Created: 26-06-2026 · Last updated: 28-08-2026 (§598 — a durable-evidence-root guard only protects the write target it is actually called on: `HEALTH_PROBE_LOG` never derived from the resolved `evidence_root`, so `assert_durable_evidence_root`'s refusal never fired for it even though the sibling per-account series it guarded landed durably — the #1034 defect one file over, H3642; §595 — a liveness watchdog is only meaningful against a STREAMING output format: every paid lane here spawns `--output-format json`, whose healthy call emits 0 stdout bytes for its full 49 404-511 908 ms, so the 90 s window H2878 specifies would have killed the healthy calls rather than the hung ones — derive the window from the declared format, never a per-call-site literal; §593 — a store write that removes rows leaves the `pwg-ru-data/tm/` mirror serving exactly what you just removed: H2996 + the H3593 `dA` requeue left `only_mirror` at 167, so refresh in the same pass and guard the copy; §592 — a gitignored artifact labelled "regenerable" with four hardcoded consumers is a shared singleton that the H963 C4 call graph D7 shows cannot be rebuilt in a clean worktree at all; §591 — withdrawing a false gloss clears the serious ceiling but breaks the fidelity floor: serious 2.50 %→0.00 % while fidelity 99.50 %→97.25 %, so a gate can be moved rather than passed; §562 постскриптум H2996 — применено: карантин 159 строк, 61 лемма в переингест-worklist, отложенных 0, стор 11 621 → 11 462; `junk_key1` починен на месте, а не карантинирован — печатный заголовок и есть целевая лемма, а PWG-записи для `durgA` не существует; §590 — a function-word denylist cannot fence a reuse lexicon: `{%thun%}` still returns `{%класть%}` policy-ON, and the denylist catches only 8 of the 13 rows carrying the mechanism while intercepting 4 correct fills; §589 — the R4.1 store SAN-LOSS freeze trigger is a literal-marker grep, four real SAN-LOSS rows live in the pwg_ru store unseen, spot-check task Disabled; §587 — derivative ī/ū-stem
gen.pl accent ruled at full-corpus n: oxytone noun stems 44/44 stem-final,
devī́-declension adjective/participle feminines genuinely mixed — Whitney §319a
vs §320/§356 are disjoint scopes, CONTRADICTIONS §1 ruled, GAPS §1 closed;
§588 — the VedaWebProject/vedaweb-data GitHub mirror replaces the WAF-blocked
VedaWeb API for bulk corpus pulls; §585 — paired totals N/N+1 for
the same TSV are the header-row signature: `union_headwords.tsv` is 323,426
lines incl. header, so the headword count of record is 323,425 (CONTRADICTIONS
§10 ruled); §586 — 285,799 vs 285,950 are exact sums of the SAME now-2026 lists
at two pipeline stages (raw export vs union-ingested), the 151-key gap is the
union build's key collapse, vintage drift refuted (CONTRADICTIONS §12 ruled);
§584 — a style pass applied to
CommentaryStrategies' `data/lexical/chN.json` never reaches the apparatus or the
print master: `build_sarga_apparatus.py` prefers the aggregate twins in
`data/sundara_commentary_to_add.json`, so 37 H3492 rewrites showed as 4 changed
apparatus lines until a twin-sync landed them; §581 — a dictionary index's
"SLP1" column can be Harvard-Kyoto, and joining it as SLP1 silently drops half
the headings; NFD-stripping the Vedic acute destroys ś; §582 — the damage in a
digitized index is not always OCR: KEWA's came from a Russian-locale spreadsheet,
which turned page ranges into dates and leading-hyphen headwords into `#ИМЯ?`;
§580 — AP90's `<pc>` field is a
third, distinct shape from mw/pwg — page-column-letter `NNNN-a/b/c`, not comma
or vol-page — csl-atlas's scan-URL builder silently resolved 0% of AP90 until
fixed, now 99.29%; §579 — citation density is a cliff: pwg 94.4 % of entries cite at 6.50 `<ls>`/entry and alone carries 801 788 elements, 16 dicts cite at all, 22 have literally zero; tag presence misclassifies GRA, whose printed proof lives in prose brackets)
(см./s./vide/Vgl./q.v./=) are four unrelated edge types, not one convention:
`s.`/`siehe` and `=` are genuine graph edges to a real headword, `Vgl.` is a
weaker "compare" edge frequently pointing at a citation not a lemma, `q.v.`
fragments into four incompatible tag shapes across the same printed
abbreviation, `vide` is a false positive almost everywhere it was expected
(genuine Sanskrit *vidé* in pwg/pw, zero after a word-boundary check in
ccs/sch), and gra's bare `<ab>s.</ab>` is grammatical Singular, not "see" —
the real xref is the separately-tagged `<ab n="siehe">s.</ab>` (663, not
1,643); §575 — root citation splits into
zero-grade `kf` (19/44 dicts) vs guṇa-grade `kar` confined to the PW family
(pw/pwg/pwkvn/sch); WhitneyRoots' `roots.csv` header has no pw_id/pwg_id
column at all, so pw/pwg are structurally unjoinable to the root crosswalk;
class digits fragment across four incompatible devices (MD's `<cl>` tag,
mw/wil's `<ab>cl.</ab>` text, Apte's `€1`–`€10` glyph, PWG's German "Kl."
prose); §574 — gloss-language layering:
`{%…%}` is not "German-or-English" — Burnouf (bur) wraps French prose in it,
Sircar (ieg) wraps front-matter dedications in it, and Cappeller's own English
dictionary (cae) plus MW use zero `{%…%}` at all despite dense English glosses;
the `<ab>` abbreviation layer is Latin/English in mw but German in gra, and 21
of 44 dicts tag no abbreviations at all; koch.jsonl (Kochergina) is 99.98 %
Russian by construction with a 25.8 % `см.`-cross-ref rate; §572 — homonym-splitting density spans 0–419 per 1 000 entries across the 44 dicts: 8 print an inline `<hom>N.` display, 14 split without displaying it, 22 split nothing; the high-density class (pui/inm/pe/mci/lrv/bop) is genre — name-indices splitting distinct persons, not sense-dictionaries splitting polysemy — and `agnihotra` itself splits mfn./n. in 6 dicts but stays one entry in 3, a 1:2-vs-1:1 join mismatch any headword matcher must carry; §570 — renaming a stored abbreviation stem (`Instr.`→`Ins.`) silently breaks tooltip lookup against an external authoritative table keyed on the old stem; §569 — a bracketed `[Gen, unsp]` domain/period tag collides on the letters "Gen" with the genitive-case abbreviation and needs the same masking discipline as `{#…#}` Sanskrit spans; §566 — `<div n=…>` is not a shared sense-hierarchy device: only pw/pwg/bor nest senses, PWG hides sense 1 in the head line in 25.2 % of hierarchical entries, and only PWG's own sense order may enter a pwg_ru card; §565 — meter/quantity marks; §562 — печатный заголовок опрокидывает §560: дефект — инжест чужой статьи-двойника, настоящие статьи 60+ целевых лемм отсутствуют в сторе; §559 — «смыслы MW/AP, отсутствующие у PWG-семейства»: механический счёт завышен ~в шесть раз, 83 % кандидатов — «не привязано»; §560 — key1 стора pwg_ru деградирован у 161 строки и сливает разные леммы, лучший свидетель — префикс subcard; §549 — CommentaryStrategies' published 17,863-note composition was born self-contradictory in one batch commit; §548 — PWG has two incompatible families of `<ls>` counts, cleaned-string vs work-family, and only the second partitions the dictionary; §545 — a fixture guard row proves the sanitizer runs, not that it covers every sink)_

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
(currently §599) whatever its section, so existing numbers never shift; when a finding is later
refuted or superseded, strike it and say why — never reuse its number. **Verifiability class (H1362):** every finding has a re-derivability class — **A** auto-reproducible · **B** re-probeable (live host) · **C** historically fixed · **D** not reproducible as stated — ruled in [`epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md) and machine-readable in [`epistemic_dashboard/verifiability.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/verifiability.json). **A class-D finding must be cited with its non-reproducibility named** — never as a bare `§N` carrying the authority of a recomputable row; the D findings are marked `⚠️ class D — not reproducible as stated` in place.

## Index

**GAPS graduates (H1735, 27-07-2026)**

- 🟠 [§488. DCS stem co-occurrence graph is extreme-sparse with function-word hubs](#488-dcs-stem-co-occurrence-graph-is-extreme-sparse-with-function-word-hubs)
- 🟡 [§489. Sintagmatic appendix-6 is a 6.3k-lemma core nested in the 80k all-corpus table](#489-sintagmatic-appendix-6-is-a-63k-lemma-core-nested-in-the-80k-all-corpus-table)
- 🟠 [§490. Heritage×kosha form intersection agrees 78.3%; disagreements are classifiable](#490-heritagekosha-form-intersection-agrees-783-disagreements-are-classifiable)
- 🟡 [§491. Verb-form frequency prelim is an unlabeled 42-row XLS with empty tense names](#491-verb-form-frequency-prelim-is-an-unlabeled-42-row-xls-with-empty-tense-names)
- 🟠 [§492. Stopovye is a 102-file subset of Polnorazmernye, not a stopword filter of the full 506k](#492-stopovye-is-a-102-file-subset-of-polnorazmernye-not-a-stopword-filter-of-the-full-506k)

- 🟡 [§493. Cross-vendor LLM second pass on routing gold is κ=1.0 — still not human IAA](#493-cross-vendor-llm-second-pass-on-routing-gold-is-κ10--still-not-human-iaa)
- 🟠 [§494. Homonym token-attribution residual is a 38-group single-lemma_id ceiling](#494-homonym-token-attribution-residual-is-a-38-group-single-lemma_id-ceiling)
- 🟡 [§495. Cyrillic name indices: 61 IAST-bearing seed files vs 47 pure-Cyrillic — rules still unsafe](#495-cyrillic-name-indices-61-iast-bearing-seed-files-vs-47-pure-cyrillic--rules-still-unsafe)
- 🔴 [§496. Edit-distance record linkage over Sanskrit headwords is 70–98% false matches — measure the key, don't trust it](#496-edit-distance-record-linkage-over-sanskrit-headwords-is-7098--false-matches--use-a-length-preserving-normalization-key-and-measure-the-false-match-rate-against-the-dictionarys-own-inventory)
- 🔴 [§497. The csl-orig L-number is not a join key — only 35 % of form-era L-codes still point at their own headword](#497-the-csl-orig-l-number-is-not-a-join-key--only-35--of-form-era-l-codes-still-point-at-their-own-headword)
- 🟠 [§498. Word-initial Harvard-Kyoto capitals never decode — 113 correction-event headwords entered the corpus mis-transcoded](#498-word-initial-harvard-kyoto-capitals-never-decode--113-correction-event-headwords-entered-the-corpus-mis-transcoded)
- 🔴 [§499. Gold cards without evidence yield unusable votes — 5 of 6 MQM rejects carried no typology label, 1 of 20 labels reversed on adjudication](#499-gold-cards-without-evidence-yield-unusable-votes--5-of-6-mqm-rejects-carried-no-typology-label-1-of-20-labels-reversed-on-adjudication)
- 🔴 [§500. A batch that never runs deletes a *band* of the sample, not a random subset — byte-packed chunking makes an incomplete A/B silently flatter the arm that failed](#500-a-batch-that-never-runs-deletes-a-band-of-the-sample-not-a-random-subset--byte-packed-chunking-makes-an-incomplete-ab-silently-flatter-the-arm-that-failed)
- 🔴 [§501. An A/B whose "clean" metric scores the last attempt that RETURNED, not what the pipeline would ship, can name the wrong winner — and did](#501-an-ab-whose-clean-metric-scores-the-last-attempt-that-returned-not-what-the-pipeline-would-ship-can-name-the-wrong-winner--and-did)
- ✅ [§503. A git worktree silently disables every sibling-repo lookup in `src/` — artifacts rebuilt there lose layers without failing](#503-a-git-worktree-silently-disables-every-sibling-repo-lookup-in-src--artifacts-rebuilt-there-lose-layers-without-failing)
- 🔴 [§510. A frozen local checkout is an actively misleading source for any append-only registry — read the numbering contract from `origin/`, not from disk](#510-a-frozen-local-checkout-is-an-actively-misleading-source-for-any-append-only-registry--read-the-numbering-contract-from-origin-not-from-disk) — one session, two collisions: a 177-commits-behind checkout showed §462 as the ceiling when `origin` had 166 findings, and the in-file next-free marker was stale too. Read the contract from `origin/`, derive the ceiling from the headings, and assert the marker sits above every used number.
- 🔴 [§511. MW72 carries ZERO `<ls>` source citations — every cross-dictionary citation test that names it shrinks to MW](#511-mw72-carries-zero-ls-source-citations--every-cross-dictionary-citation-test-that-names-it-shrinks-to-mw) — `csl-orig/v02/mw72/mw72.txt` is 17.2 MB and contains not one `<ls>` tag, while MW has 320,828. Any apparatus/citation comparison that lists MW72 as a target silently produces a zero, not an error. Verify a dictionary's tag layer before scoping a test around it.
- 🔴 [§515. PWG rests on WIL 1819; MW/MW72 English on WIL 1832 — CDSL has only 1832 OCR; do not treat Wilson as edition-free](#515-pwg-rests-on-wil-1819-mwmw72-english-on-wil-1832--cdsl-has-only-1832-ocr-do-not-treat-wilson-as-edition-free) — house edition-basis rule + OCR gap + preface-only scope for 1819; `L.` stays "native lexicons" with European transmission via 1819, not a Wilson siglum (`W.` is Wilson/1832).
- 🔴 [§518. A ceiling written as a LITERAL in a test silently encodes whatever the default was the day it was typed — derive it from the policy table](#518-a-ceiling-written-as-a-literal-in-a-test-silently-encodes-whatever-the-default-was-the-day-it-was-typed--derive-it-from-the-policy-table) — the PWG probe gate kept one source of truth for its ceilings and still went stale twice, because `verdict_for`'s own default and two selftests pinned the NUMBER instead of the pointer. Derive the LIVE boundary from `POLICIES[CURRENT_POLICY]`; pin only the HISTORICAL policies, whose retired numbers really did judge their rows.
- 🟠 [§519. vidyut.kosha's `lemma` for a krdanta-derived Subanta is the bare dhatu — entry-count lemma voting collapses derived nominals to verbal roots](#519-vidyutkoshas-lemma-for-a-krdanta-derived-subanta-is-the-bare-dhatu--entry-count-lemma-voting-collapses-derived-nominals-to-verbal-roots) — `janitf` gets 12 kosha entries saying lemma `jan` vs 3 saying `janitf`; even `rAmeRa` out-votes to the root `ram`. The stem-vs-collapse distinction is in `pratipadika_entry` (`Basic` vs `Krdanta`) — rank with it, never by raw entry counts.
- 🟠 [§520. UD `Tense=Past` is not the end of the aorist/perfect story — DCS's own `feat_formation` re-splits it, and the "too sparse to use" verdict was a denominator error](#520-ud-tensepast-is-not-the-end-of-the-aoristperfect-story--dcss-own-feat_formation-re-splits-it-and-the-too-sparse-to-use-verdict-was-a-denominator-error) — the seven Whitney aorist formations give Aorist 12,054 and `peri` gives Periphrastic Perfect 4,046 within the 93,329-token finite past indicative. Quote as bounds: aorist a LOWER bound, perfect an UPPER bound.
- 🟠 [§521. A code-keyed source read into a name-keyed dict is silent lossy aggregation — and the SHAPE a derived asset is serialised in decides whether consumers in other repos survive it](#521-a-code-keyed-source-read-into-a-name-keyed-dict-is-silent-lossy-aggregation--and-the-shape-a-derived-asset-is-serialised-in-decides-whether-consumers-in-other-repos-survive-it) — `timws.csv` 42 codes → 30 names lost 39,836 examples; `_8.csv` would lose 54% of 4,577,461 tokens. Republishing such a table as a name-keyed OBJECT corrupts consumers in other repos with no code change there; a duplicate-preserving LIST leaves identical consumer code correct.
- 🔴 [§516. A later PR's stale-base merge can silently revert an EARLIER PR's ledger-doc-only re-stamp while leaving that earlier PR's CODE change fully intact](#516-a-later-prs-stale-base-merge-can-silently-revert-an-earlier-prs-ledger-doc-only-re-stamp-while-leaving-that-earlier-prs-code-change-fully-intact) — H2226's SHARED re-stamp of two LANG_PARITY entries was reverted by H2227's stale-base merge while the underlying code stayed field-parameterized; detect by re-hashing the working tree against the last legitimate re-stamp commit, not by trusting the ledger's currently-recorded hash.
- 🔴 [§517. An EMPTY spawn directory is not a context-free spawn directory — verify the ancestry, not the directory](#517-an-empty-spawn-directory-is-not-a-context-free-spawn-directory--verify-the-ancestry-not-the-directory) — `bare_cli_cwd()` checked its own directory for `CLAUDE.md`/`.git` and pointed at `%TEMP%`, i.e. under the Windows user profile: 32 779 B of operator memory reached every paid call, invisible because the directory itself was empty. Enumerate what the *child* discovers and keep that marker set in ONE place; derive and verify candidates rather than hardcoding a "clean" path; and never let "could not prove it clean" collapse into "proved it clean".
- 🟠 [§504. The NWS tag layer reaches only 2.2 % of the RU store — a facet bar over it is right, but it is not the sheet's main axis](#504-the-nws-tag-layer-reaches-only-22--of-the-ru-store--a-facet-bar-over-it-is-right-but-it-is-not-the-sheets-main-axis)


**Grammar & morphology data**

- 🟠 [§1. Whitney accent-mobility rules are machine-encodable](#1-whitney-accent-mobility-rules-are-machine-encodable) — the Zaliznyak a–f accent axis is an encoding task, not a missing source; VedaWeb 2.0 validates. **Encoded 02-07-2026, validated 03-07-2026 (17/19 GO)** → WhitneyRoots `crosswalk/accent_rules.json` / `accent_validation.json`.
- 🟠 [§42. Whitney self-contradicts on derivative ī-stem gen.pl accent](#42-whitney-self-contradicts-on-derivative-ī-stem-genpl-accent) — §320 "not thrown forward" vs §319a RV "usually" shifts vs §356's own printed nadī́nām; encode as a per-lemma variant, not a rule. **Empirical split measured 03-07-2026 (n=2, too thin to resolve)** → §54.
- 🟠 [§54. Whitney accent axis validates at 18/19 matrix cells GO against attested RV accents](#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents) — VedaWeb 2.0 scoring; T8c exception resolved as a rule gap (H115); D3 split still too thin to resolve.
- 🟠 [§2. Homonym token-splitting has a hard morphological ceiling](#2-homonym-token-splitting-has-a-hard-morphological-ceiling) — only 5 of 38 DCS-lumped groups are gaṇa-splittable; the rest need gloss adjudication.
- 🟠 [§3. The Warnemyr scrape union-smears homonym classes](#3-the-warnemyr-scrape-union-smears-homonym-classes) — local Whitney class files merge homonyms' classes; derive from the live paradigm pages.
- 🟡 [§4. PWG nominal grammar compresses into 335 paradigm tokens](#4-pwg-nominal-grammar-compresses-into-335-paradigm-tokens) — 98,639 of 123,366 entries carry a Zaliznyak-style token.
- 🟡 [§63. vidyut dhātupāṭha adjudicates the 2014 Palsule-exclusion dispute](#63-vidyut-dhātupāṭha-adjudicates-the-2014-palsule-exclusion-dispute-five-añc-dhātus-no-and-but-ast-is-paninian) — five añc dhātus (4añc recoverable), no and, but ast IS Paninian; grep vidyut as `ancu`, not `aYc`.
- 🟠 [§90. A spelling-keyed join onto Whitney's roots union-smears homonyms](#90-a-spelling-keyed-join-onto-whitneys-roots-union-smears-homonyms--one-authorial-entry-lands-on-every-homonym-of-that-spelling-and-the-rows-still-read-authorial) — §3's failure class, now on an *author's own* data: «2 iṣ» asserted of iṣ¹+iṣ²; abstain on unique-*resolution*, not non-contradiction; the legitimate «gam, gach» concordance looks identical. Aggregates stayed correct — only provenance broke.

**Corpus & parallel-text data**

- 🟠 [§5. The parallel corpus rarely attests prefixed-verb forms](#5-the-parallel-corpus-rarely-attests-prefixed-verb-forms) — sandhi-join lookups are a no-op; ~80 % of prefixed forms miss.
- 🟠 [§6. No printed frequency dictionary of Sanskrit exists](#6-no-printed-frequency-dictionary-of-sanskrit-exists) — DCS-frequency ordering is genuine innovation.
- 🔴 [§7. DCS lemma data is keyed in two transliterations](#7-dcs-lemma-data-is-keyed-in-two-transliterations) — SLP1 vs IAST across the two frequency files.
- 🔴 [§8. Unaccented DCS cannot distinguish present class I from VI](#8-unaccented-dcs-cannot-distinguish-present-class-i-from-vi) — 117 spurious corpus-derived class additions were reverted.
- 🔴 [§457. DCS covers ~25% of the Poona Dictionary's citation mass but ~78% of DCS's own tokens — the classical core, not PD's encyclopedic breadth; and a siglum prefix-merge fuses MahāBhā. (Mahābhārata) with MahāBh. (Mahābhāṣya)](#457-dcs-covers-25-of-the-poona-dictionarys-citation-mass-but-78-of-dcss-own-tokens--the-classical-core-not-pds-encyclopedic-breadth-and-a-siglum-prefix-merge-fuses-mahābhā-mahābhārata-with-mahābh-mahābhāṣya) — first PD×DCS measurement (PD letter a-): residue = purāṇas/kośas/classical kāvya (Padma 3506, Mahābhāṣya 1934, no Raghuvaṃśa); ⚠️ never prefix-cluster sigla.
- 🔴 [§458. A Sanskrit dictionary’s big letters are big because they head *preverb families* — and testing entry-size decay needs an outlier-robust estimator, not a parametric regression](#458-a-sanskrit-dictionarys-big-letters-are-big-because-they-head-preverb-families--and-testing-entries-shrink-over-publication-needs-an-outlier-robust-estimator-not-a-parametric-regression-encyclopedic-dicts-have-single-300k-char-articles) — `a` 83.1% compounds is not unique (`u`/`p`/`s`/`v` close behind); every big letter heads a preverb family (`v`=vi-, `u`=ud-/upa-); SKD/VCP funding-decay REFUTED (ρ≈0.00), real in PWG/PWK/GRA.
- 🔴 [§459. PWG entry-size decay is a *smooth* funding fade (−14 %/decade), not a one-time vol-1 correction — and SKD/VCP carry ~0 digitisation markup](#459-pwgs-entry-size-decay-is-a-smooth-fundingenergy-fade-across-its-whole-20-year-run-14-decade-not-a-one-time-correction-after-the-over-detailed-first-volume--and-skdvcp-carry-0-digitisation-markup) — PWG `<pc>`→volume→year maps all 123,366 entries to a real year; vols 2-7 still −15 %/decade after dropping vol-1 (settles the §458 cause question); density = digitisation apparatus, not lexicographic depth.
- 🔴 [§460. "Gold" in this org means *frozen*, not *human-adjudicated* — 0 of 15 gold datasets have independent human annotation, and every travelling κ is model-vs-model (four contamination mechanisms)](#460-gold-in-this-org-means-frozen-not-human-adjudicated--0-of-15-gold-datasets-have-independent-human-annotation-and-every-travelling-κ-is-model-vs-model-four-contamination-mechanisms) — H1272 audit: 0 GOLD · 1 SILVER · 4 LLM-ASSISTED · 10 CONTAMINATED; the four mechanisms (self-authored gold, same-family κ as IRR, LLM output labelled human review, circular controls) are the checklist for any future eval set.
- 🟠 [§461. The r2 kośa-fusion "separable" class is substantially an orthographic sandhi artifact](#461-the-r2-kośa-fusion-separable-class-is-substantially-an-orthographic-sandhi-artifact--whether-an-skd-citation-counts-fused-depends-on-whether-the-authoritys-name-begins-with-a-vowel) — whether an SKD citation counts "fused" depends on whether the authority's name begins with a vowel.
- 🟠 [§462. On Windows, repeated repository discovery can dominate a Python pipeline](#462-on-windows-repeated-repository-discovery-can-dominate-a-python-pipeline-cache-checkout-identity-not-mutable-path-overrides) — 88 Git subprocesses cost 4.50 s of 5.29 s; cache the immutable checkout identity, not mutable path overrides.
- 🔴 [§470. The Cologne scan-viewer page PDFs can carry an embedded digitized text layer](#470-the-cologne-scan-viewer-page-pdfs-can-carry-an-embedded-digitized-text-layer--check-get_text-before-declaring-no-e-text-exists-or-commissioning-ocr) — the ramayanagorr Google-sourced page PDFs held a clean Devanagari text layer; the full Gorresio e-text (10,225 vv) was extracted with zero new OCR the same day "no e-text exists" was concluded. Check `get_text()` per VOLUME before commissioning OCR; anchor ॥N॥ segmentation to an external per-page verse index (OCR drops digits).
- 🔴 [§473. OCR the canonical page files themselves — mapping a third-party OCR of "the same" scan onto them loses to offset drift, thumbnail decoys, and digit aliasing](#473-ocr-the-canonical-page-files-themselves--mapping-a-third-party-ocr-of-the-same-scan-onto-them-loses-to-offset-drift-thumbnail-decoys-and-digit-aliasing) — the DLI vol-2 leaf offset drifts +48→+20 and verse-number anchors alias across short sargas; tesseract-5 `san` on the Cologne pages' own embedded full-res images closed the §470 vols-2/4/uk gap (e-text 10,225→19,852 vv, all 672 sargas) with zero mapping risk. Take the LARGEST embedded image, never `get_images()[0]` (thumbnail decoy); normalize `।।`→`॥` before ॥N॥ segmentation.
- 🔴 [§480. A non-empty PDF text layer proves nothing — check the SCRIPT; and "extract the largest embedded image" breaks when the PDF CROPS a 2-up scan](#480-a-non-empty-pdf-text-layer-proves-nothing--check-the-script-and-extract-the-largest-embedded-image-breaks-when-the-pdf-crops-a-2-up-scan) — the ramayanabom page PDFs return ~1,100–2,300 chars each, all of it Latin garbage from a Latin-alphabet OCR of Devanagari; and each 1128×420 pt page embeds a 4700×3500 TWO-page scan it crops in half, so §473's largest-image rule silently OCRs two pages at once. Render the page instead. Amends §470 and §473 for the next edition.
- 🔴 [§481. A corpus file's PRESENCE is not evidence of its contents — `07_ramayana-uttarakanda.jsonl` is Sanskrit-only CRITICAL-edition text under a "Southern/Leonov" label, and a handoff was minted off the filename](#481-a-corpus-files-presence-is-not-evidence-of-its-contents--07_ramayana-uttarakandajsonl-is-sanskrit-only-critical-edition-text-under-a-southernleonov-label-and-a-handoff-was-minted-off-the-filename) — 2,690 `sa` segments and 0 `ru`; 99.9% of its verses align to the DCS critical edition at the identical `sarga.verse` while kāṇḍas 1/2/3/5 sit at 1–3%. H1705 was written to "bridge the Bombay numbering" for a book whose blocker is that no Russian uttarakāṇḍa exists.
- 🟠 [§482. A count column with no stated provenance is not data — it is a ranking, and the difference decides whether you may divide by it](#482-a-count-column-with-no-stated-provenance-is-not-data-it-is-a-ranking-and-the-difference-decides-whether-you-may-divide-by-it) — a corpus count column whose provenance is unstated supports a ranking but not a rate — check before dividing by it.
- 🔴 [§483. A resolver that fails closed is a gap; one that fails *open* is a wrong answer — and only the second is an integrity defect](#483-a-resolver-that-fails-closed-is-a-gap-one-that-fails-open-is-a-wrong-answer-and-only-the-second-is-an-integrity-defect) — a resolver that returns nothing is a gap; one that returns the wrong thing is an integrity defect — only the second corrupts downstream data.
- 🔴 [§484. A quarter of the DCS nominal mass has no case at all — `feat_case='Cpd'` is a compound member, not a ninth case](#484-a-quarter-of-the-dcs-nominal-mass-has-no-case-at-all-feat_casecpd-is-a-compound-member-not-a-ninth-case) — 724,676 of 2,996,410 NOUN/ADJ tokens are `feat_case='Cpd'` compound members with no case, and 8,542 more are untagged — a "case distribution" is wrong whether it silently includes them or silently drops them.
- 🟡 [§485. The 2021-sourced "Nom.Sg = 34.6% of nominal forms, dual < 1% everywhere" does not reproduce on DCS-2026 — and the second half only survives read per cell](#485-the-2021-sourced-nomsg-346-of-nominal-forms-dual-1-everywhere-does-not-reproduce-on-dcs-2026-and-the-second-half-only-survives-read-per-cell) — recomputed on DCS-2026: Nom.Sg 33.7% (not 34.6%), dual 2.07% pooled / 0.91% at the largest cell — a non-reproduction, not a refutation, since the 2021 denominator is unstated.
- 🔴 [§486. Before OCR-ing a library scan, check whether the library already published its OCR — and measure against it rather than guessing](#486-before-ocr-ing-a-library-scan-check-whether-the-library-already-published-its-ocr--and-measure-against-it-rather-than-guessing) — the BSB publishes per-page hOCR via `seeAlso` on every IIIF canvas, 2.5× better than local tesseract 5 `san`; the scans carry no text layer, but the OCR still did not need doing.
- 🔴 [§471. A corpus-candidate matcher keyed on a dictionary's OWN bibliographic prose will bury its biggest wins in the "no corpus side exists" class](#471-a-corpus-candidate-matcher-keyed-on-a-dictionarys-own-bibliographic-prose-will-bury-its-biggest-wins-in-the-no-corpus-side-exists-class--pwgs-pāṇini-and-manu-41910-citations-sat-in-dcs-lacks) — a `Verzeichniss der Abkürzungen` names works by author in the editor's language, not by the Sanskrit title a corpus indexes; PWG's Pāṇini and Manu (41,910 citations) sat in `DCS-LACKS` until matched on the work, not the prose.
- 🔴 [§472. Choosing a confidence tier ONCE PER SENSE and then stamping it on many passages inflates the strongest tier](#472-choosing-a-confidence-tier-once-per-sense-and-then-stamping-it-on-many-passages-inflates-the-strongest-tier--413-of-h1670s-exact-verse-rows-were-chapter-level) — 4.13% of H1670's exact-verse rows were chapter-level addresses; let the level travel with the passage, and grep the strongest tier for the address shape it is supposed to exclude.
- 🔴 [§468. PWG's plain `R.` is a THREE-edition composite](#468-pwgs-plain-r-is-a-three-edition-composite--books-36-carry-gorresio-bengal-recension-numbering-so-keying-them-into-a-southern-recension-text-silently-returns-the-wrong-verse) — books 1–2 cite Schlegel, books 3–6 Gorresio (Bengal recension), book 7 Bombay (pwgbib 1.247; store sarga maxima 79/63/94 = Gorresio's counts). `citation_tm` had returned the wrong verse's RU silently for ~900 in-range R. 3/5 refs; books 3–6 now `unmapped_locus_scheme` until the Gorresio↔Southern concordance validates (H1656).
- 🔴 [§467. corpus_lexicon.jsonl gets its first intrinsic BLI quality number](#467-corpus_lexiconjsonl-gets-its-first-intrinsic-bli-quality-number--and-the-obvious-gold-source-the-corpuss-own-glossary-is-circular-so-the-fix-is-an-independent-dictionary-ranked-by-an-independent-frequency-source) — P@1 0.402 / MRR 0.539 / coverage 99.5% against an independent Kochergina+DCS gold set; the corpus's own 3-layer glossary was rejected as gold because it is built FROM this same file.
- 🔴 [§469. `to_slp1` is case-preserving, so a capitalised IAST headword transliterates into a DIFFERENT SLP1 letter](#469-to_slp1-is-case-preserving-so-a-capitalised-iast-headword-transliterates-into-a-different-slp1-letter--60-of-ncc-match-keys-are-wrong-and-14379-exact-accncc-matches-were-never-proposed) — 60% of NCC match-keys were wrong, 93.3% of Tier D was an artefact, and 14,379 true exact matches were never proposed because the corrupted key changed the blocking letter. ✅ fixed + re-run 26-07-2026 (H1671), incl. the org-wide caller audit: the library and csl-atlas already defend silently, csl-apidev does not.
- 🔴 [§463. The pwg_ru store's `de` field is NOT a faithful copy of the csl-orig German](#463-the-pwg_ru-stores-de-field-is-not-a-faithful-copy-of-the-csl-orig-german--russian-connectives-have-been-substituted-into-the-source-of-truth-string) — 11 rows have `и`/`для`/`в`/`С` substituted for German connectives and do not round-trip against csl-orig; `sense_tag` (110 rows) and `h` carry Russian prose, so `h` is unusable as a homonym key.
- 🔴 [§464. The H1624 G1 `gloss_lang` classifier mislabels German as Latin/English about half the time it fires](#464-the-h1624-g1-gloss_lang-classifier-mislabels-german-as-latinenglish-about-half-the-time-it-fires--and-those-spans-are-then-withheld-from-translation) — 122 of 229 non-DE spans are German (77% FP on `english_content`), and `la`/`en` are marked `translate: False`, so those glosses never reach the model.
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
- 🟠 [§452. csl-atlas's PWG parse-rules census is stale and incomplete — 21 real markup tags missing, several listed counts wrong](#452-csl-atlass-pwg-parse-rules-census-is-stale-and-incomplete--21-real-markup-tags-missing-several-listed-counts-wrong) — `<bot>` (5,427 occurrences) and 20 other tags absent from the census; `div`/`H`/`span` counts disagree with a live scan.
- 🟠 [§453. PWG's sense-closing glyph "〉" nests FOUR enumeration tiers, not two](#453-pwgs-sense-closing-glyph--nests-four-enumeration-tiers-not-two--greek-letters-and-roman-numeral-markers-are-unrecognised-by-the-ru-pipelines-splitter) — Greek letters (1,444 occurrences) and roman-numeral markers (30) unrecognised by `microstructure.py`'s `MARK` regex, the same bug class as §447 one tier deeper.
- 🟠 [§454. The pwg_ru RU store's `h` field has inconsistent semantics — not a reliable homograph-number join key](#454-the-pwg_ru-ru-stores-h-field-has-inconsistent-semantics--not-a-reliable-homograph-number-join-key) — holds a digit, an empty string, or a root-word string within the same file; 93.78% of store rows (10,881/11,603) touch a headword whose corrected `〉` segmentation changed sense count.
- 🟡 [§455. PWG `<ls>` citation resolution is already at 98%+, far above the previously-cited 72.4% baseline](#455-pwg-ls-citation-resolution-is-already-at-98-far-above-the-previously-cited-724-baseline) — `pwgbib.txt` grew to 4,390 entries since the 72.4% measurement; re-measure with `pwg_sources.py coverage` before citing a stale ceiling.
- 🔴 [§465. PWG sense × DCS attestation collapses from ~40% at lemma level to 0.67% at sense level — and three independent constrictions cause it](#465-pwg-sense--dcs-attestation-collapses-from-40-at-lemma-level-to-067-at-sense-level--and-three-independent-constrictions-cause-it) — measured over ALL 109,050 PWG headwords: 60.2% absent from DCS entirely, 88.8% of DCS token mass untagged. **The 0.67% sense-level figure is superseded: H1670 found it was a matcher-reach artefact (the locus tier saw 0.299% of available passages, and a dead `"RV"` map key hid the Ṛgveda) and raised it to 12.25% with no criterion changed.** The two data-availability ceilings stand. Grounding outside the aligner's reach is *unknown*, never 0%.
- 🔴 [§474. PWG's etymology parenthesis is NESTED — a first `+`-chain regex reads the inner sub-analysis, not the compound's members](#474-pwgs-etymology-parenthesis-is-nested--a-first--chain-regex-reads-the-inner-sub-analysis-not-the-compounds-members) — 344/16,738 (2.06%) of published `pwg_compound_split` gold ship an inner or neighbouring word's `+`-chain; blank balanced `[...]` before splitting; keep only the first `{#…#}` per `+`-part.
- 🟠 [§475. MW's `<k2>` carries a variant LIST after `;` and two different boundary marks — stripping the punctuation welds variants into a member that is not a word](#475-mws-k2-carries-a-variant-list-after--and-two-different-boundary-marks--stripping-the-punctuation-welds-variants-into-a-member-that-is-not-a-word) — 41/106,603 MW compound records; split on `;` first (take first variant), then em-dash; keep hyphen as deliberate non-boundary. **✅ FIXED 26-07-2026 (H1703)** — with the correction that it must be the first variant *carrying the segmentation*.
- 🟠 [§476. Repairing an extractor GROWS the disagreement queue it feeds — plan for that, not for a shrink](#476-repairing-an-extractor-grows-the-disagreement-queue-it-feeds--plan-for-that-not-for-a-shrink) — two repairs expected to shrink a 4,123-card queue grew it to 4,246 (118 left, 241 entered); re-derive the queue before sizing any human sample against it.
- 🟡 [§477. 35 cards is the floor for a 0.90 Wilson gate — and a censused stratum needs no interval at all](#477-35-cards-is-the-floor-for-a-090-wilson-gate--and-a-censused-stratum-needs-no-interval-at-all) — `wilson_lower(35,35)=0.9010` vs `0.8983` at 34, so "~30 per stratum" spends the votes and still cannot promote; a fully censused stratum promotes with its bound below threshold.
- 🟠 [§478. A blind arm stratified on an agent's own rules must not render the rule — and its card ids must come from the lock, not the frame](#478-a-blind-arm-stratified-on-an-agents-own-rules-must-not-render-the-rule--and-its-card-ids-must-come-from-the-lock-not-the-frame) — pin the no-leak rule with a test; the lock is the only id list an export can be validated against.
- 🟡 [§479. PWG's etymology parenthesis: "first `{#…#}` per `+`-part" is right until PWG writes a derivation ladder](#479-pwgs-etymology-parenthesis-first--per--part-is-right-until-pwg-writes-a-derivation-ladder) — 1,564 multi-member parts: 1,308 where first-wins is right, ~357 ladders/disjunctions where it ships a base; arbitrate by surface coverage, drop what stays ambiguous.

**Etymology & derivation**

- 🟠 [§33. Indigenous dictionaries agree on derivation; Wilson is the outlier](#33-indigenous-dictionaries-agree-on-derivation-wilson-is-the-outlier) — 90–100 % agreement vs Wilson 23–61 %.
- 🟠 [§34. The E abbreviation tag is polysemous across dicts](#34-the-e-abbreviation-tag-is-polysemous-across-dicts) — Etymology / Epithet / Epic; count the meaning, not the marker.
- 🟠 [§35. Root-recovery tiers err on root form, not identity](#35-root-recovery-tiers-err-on-root-form-not-identity) — normalize to dhātupāṭha citation form; gate LLM roots through a known-dhātu set.
- 🟠 [§103. The §83/§97 witness-collapse deflates the union's published "corroboration" 55.9% → 34.7%](#103-quantified-the-8397-witness-collapse-deflates-the-published-15-dict-union-corroboration-from-559-to-347--and-the-unions-own-table-is-pre-fold) — 68,651 "corroborated" headwords rest on one European lineage; Apte kept independent per §83; UNION.md table is pre-fold.
- 🔴 [§466. MW's `cf.` and PWG's `Vgl.` are NOT independent witnesses](#466-mws-cf-and-pwgs-vgl-are-not-independent-witnesses--they-agree-2950-above-chance-so-a-shared-cross-reference-never-counts-as-double-attestation) — they agree on the target 21.8% of the time vs 0.007% expected (≈2,953×, p < 0.005) on the 2,750 headwords both cross-reference. MW 1899 rests on Böhtlingk–Roth, so "N dictionaries agree" is not N witnesses; the containment asymmetry (~3.2×) is a set-size artifact, not direction.

**Encoding & normalization**

- 🔴 [§36. IAST Unicode collides and normalises lossily](#36-iast-unicode-collides-and-normalises-lossily) — NFD + strip-Mn destroys length and retroflexion.
- 🟠 [§37. BOM state is inconsistent across exports](#37-bom-state-is-inconsistent-across-exports) — check head -c 3; preserve on write.
- 🔴 [§100. `nfold` fuses every nasal to `n`, manufacturing false quotation matches](#100-nfold-earns-sandhi-tolerant-recall-by-fusing-every-nasal-to-n-which-manufactures-false-quotation-matches-unless-every-hit-is-re-verified-on-norm) — nfold for recall, norm for the verdict.
- 🔴 [§102. DCS `text_sandhied` is not reliably sandhied](#102-dcs-sentencetext_sandhied-is-not-reliably-sandhied-some-rows-store-analyzed-word-forms-which-silently-downgrades-verbatim-quotations-to-partial-matches) — some rows store analyzed word forms; cross-check a real-surface corpus.
- 🟠 [§38. Injected BOMs crash the hw record parser](#38-injected-boms-crash-the-hw-record-parser) — "init_entries Error 2" is an encoding symptom, not a structure defect.
- 🟡 [§39. devanagari_to_slp1 mis-routes retroflex la](#39-devanagari_to_slp1-mis-routes-retroflex-la) — ळ → x instead of L.
- 🟠 [§40. Gloss-language spelling drift tracks reform type, not age](#40-gloss-language-spelling-drift-tracks-reform-type-not-age) — legislated ≫ convention ≫ none; the metric saturates post-1890 for English.
- 🟡 [§60. Practical Russian transcription of Sanskrit names has no safe reverse transliteration](#60-practical-russian-transcription-of-sanskrit-names-has-no-safe-reverse-transliteration) — dental/retroflex collapse in Cyrillic-only name glossaries blocks a deterministic SLP1 join key.
- 🟠 [§487. A cross-scheme join is a transliteration step, not a string comparison](#487-a-cross-scheme-join-is-a-transliteration-step-not-a-string-comparison--a-naive-iast-to-slp1-match-selects-on-diacritics) — a direct IAST→SLP1 match keeps only the diacritic-free 29 % of a root catalogue and biased a token-weighted result upward by 26 points; route through `to_slp1` and report the join rate beside the result.

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
- 🟠 [§103. `10.5281/zenodo.15834721` is a false DOI, cited as genuine in two different repos](#103-105281zenodo15834721-is-a-false-doi-cited-as-genuine-in-two-different-repos) — resolves to an unrelated topology preprint, not any Sanskrit-lexicon dataset; csl-observatory's own `CITATION.cff` carried it as OBS-T's "concept DOI".
- 🔴 [§506. A complete-coverage count cannot see commentary leaking into an extracted translation layer](#506-a-complete-coverage-count-cannot-see-commentary-leaking-into-an-extracted-translation-layer) — the two checks that DID find them — a length distribution, and a terminal-punctuation rate against an independently-extracted sibling layer — are cheap enough to keep permanently.
- 🔴 [§507. Do not find hymn headings in an OCR'd Vedic translation by matching roman numerals](#507-do-not-find-hymn-headings-in-an-ocrd-vedic-translation-by-matching-roman-numerals) — 2,303 matches, overwhelmingly prose cross-references; anchoring is not enough, the heading form differs by volume, and 8 headings are destroyed outright.
- 🟠 [§508. archive.org OCR: use `/download/`, not `/stream/` — and expect no diacritics](#508-archiveorg-ocr-use-download-not-stream--and-expect-no-diacritics) — `/stream/` returns the viewer page wrapped in HTML; printed line structure is not recoverable and Latin diacritics are flattened.
- 🟠 [§509. J–B decline to translate RV 10.106.5–8 rather than omit them](#509-jb-decline-to-translate-rv-1010658-rather-than-omit-them) — transliterated Vedic, not English, at exactly the four stanzas Geldner skips — convergent evidence about the text, not about either translator.
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


**Appended findings — H1361 Index backfill (§76+ and renumbered §448–§451; append-only, uncategorised)**

- 🟠 [§76. The MW→WordNet→semdom bridge is a candidate generator, not a classifier](#76-the-mwwordnetsemdom-bridge-is-a-candidate-generator-not-a-classifier)
- 🟠 [§79. DCS 2021→2026 "lost lemma" counts are mostly lemmatization-policy drift — a-privatives now resolve to their bases](#79-dcs-20212026-lost-lemma-counts-are-mostly-lemmatization-policy-drift--a-privatives-now-resolve-to-their-bases)
- 🟠 [§80. DCS `text_sandhied` is largely DE-sandhied pada text in the Rāmāyaṇa — and locus joins fail across editions; a text-keyed 3-tier match (exact / consonant-skeleton / fuzzy) recovers it](#80-dcs-textsandhied-is-largely-de-sandhied-pada-text-in-the-rāmāyaṇa--and-locus-joins-fail-across-editions-a-text-keyed-3-tier-match-exact--consonant-skeleton--fuzzy-recovers-it)
- 🟠 [§81. vidyut-cheda 0.4 lemmatizes derivatives to the dhātu ROOT (rāmaḥ → ram) where DCS uses the nominal stem — and over-segments epic verse 1.44×](#81-vidyut-cheda-04-lemmatizes-derivatives-to-the-dhātu-root-rāmaḥ--ram-where-dcs-uses-the-nominal-stem--and-over-segments-epic-verse-144)
- 🟠 [§83. MW and the Petersburg dictionaries are NOT independent witnesses on inventory or apparatus — do not count their agreement as corroboration; but no shared *error* has ever been found](#83-mw-and-the-petersburg-dictionaries-are-not-independent-witnesses-on-inventory-or-apparatus--do-not-count-their-agreement-as-corroboration-but-no-shared-error-has-ever-been-found)
- 🟠 [§84. pwg_ru readiness audit: `[NWS:]` attribution and `{%…%}`-delimiter dropping are NOT audit-contract defects; observed token/cost economy is `not_recoverable`; store-membership ≠ audit-clean](#84-pwgru-readiness-audit-nws-attribution-and--delimiter-dropping-are-not-audit-contract-defects-observed-tokencost-economy-is-notrecoverable-store-membership--audit-clean)
- 🟠 [§85. A clean-looking subset is not promotable evidence when its audit or execution contract failed](#85-a-clean-looking-subset-is-not-promotable-evidence-when-its-audit-or-execution-contract-failed)
- 🟠 [§86. DCS verbal-feature annotation density collapses for later texts — feats-based diachronic metrics measure ANNOTATION, not language](#86-dcs-verbal-feature-annotation-density-collapses-for-later-texts--feats-based-diachronic-metrics-measure-annotation-not-language)
- 🟠 [§87. A curated DCS text→period map EXISTS (consume, don't rebuild) — and the purāṇas carry a measured epic-imitative signature on two independent axes](#87-a-curated-dcs-textperiod-map-exists-consume-dont-rebuild--and-the-purāṇas-carry-a-measured-epic-imitative-signature-on-two-independent-axes)
- 🟠 [§88. The DCS snapshot's UD dependency slice is real but VEDIC-SKEWED — syntax studies get counterexample hunts, not classical norms](#88-the-dcs-snapshots-ud-dependency-slice-is-real-but-vedic-skewed--syntax-studies-get-counterexample-hunts-not-classical-norms)
- 🟠 [§89. MW writes `<ls>` citations in TWO markup shapes and locates them in roman as well as arabic — a literal `<ls>` regex undercounts its apparatus by 28.6%, and case-folding the roman test erases the `L.` hedge](#89-mw-writes-ls-citations-in-two-markup-shapes-and-locates-them-in-roman-as-well-as-arabic--a-literal-ls-regex-undercounts-its-apparatus-by-286-and-case-folding-the-roman-test-erases-the-l-hedge)
- 🟠 [§91. DCS has no aorist TENSE value — `feat_tense='Past'` lumps aorist with the perfect; `feat_formation` is what actually separates them](#91-dcs-has-no-aorist-tense-value--feattensepast-lumps-aorist-with-the-perfect-featformation-is-what-actually-separates-them)
- 🟠 [§92. A verified claim register is not Whitney-proof — 3 of 229 verdict_fact: TRUE rows in Kochergina claims.yml contradict Whitney, and ~65 of the register/article §-refs point at the wrong section](#92-a-verified-claim-register-is-not-whitney-proof--3-of-229-erdictfact-true-rows-in-kochergina-claimsyml-contradict-whitney-and-65-of-the-registerarticle--refs-point-at-the-wrong-section)
- 🟠 [§93. Declared, validated, and never enforced — the PWG headless executor read a manifest `budgets{}` block it did not obey, and every offline gate stayed green](#93-declared-validated-and-never-enforced--the-pwg-headless-executor-read-a-manifest-budgets-block-it-did-not-obey-and-every-offline-gate-stayed-green)
- 🟠 [§94. kosha's generated `forms` is 93% DCS-derived, so its attested-form join is a round-trip — only the vidyut-engine subtotal (12.4% attested) carries signal, and A¬G cannot measure engine gaps](#94-koshas-generated-forms-is-93-dcs-derived-so-its-attested-form-join-is-a-round-trip--only-the-vidyut-engine-subtotal-124-attested-carries-signal-and-ag-cannot-measure-engine-gaps)
- 🟠 [§95. DharmaMitra `unsandhied` batches return MISALIGNED results on short inputs — doubled echoes and other texts' tokens — so every consumer must validate by surface reconstruction before display](#95-dharmamitra-unsandhied-batches-return-misaligned-results-on-short-inputs--doubled-echoes-and-other-texts-tokens--so-every-consumer-must-validate-by-surface-reconstruction-before-display)
- 🟠 [§96. SamudraManthanam's generated full-corpus JSONL has 38,288 duplicate canonical-ID groups, concentrated in `devibhagavata-purana`](#96-samudramanthanams-generated-full-corpus-jsonl-has-38288-duplicate-canonical-id-groups-concentrated-in-devibhagavata-purana)
- 🟠 [§97. Cross-dictionary attestation via Monier-Williams overstates independence — MW was compiled *from* Böhtlingk-Roth (PW/PWG), so an MW-only hit is not evidence a PW/PWG word is independently text-attested](#97-cross-dictionary-attestation-via-monier-williams-overstates-independence--mw-was-compiled-from-böhtlingk-roth-pwpwg-so-an-mw-only-hit-is-not-evidence-a-pwpwg-word-is-independently-text-attested)
- 🟠 [§98. PD's inline sigla contain a near-homograph pair that similarity-clustering silently fuses — `MahāBhā.` is the Mahābhārata, `MahāBh.` is the Mahābhāṣya, and the locator shape tells them apart mechanically](#98-pds-inline-sigla-contain-a-near-homograph-pair-that-similarity-clustering-silently-fuses--mahābhā-is-the-mahābhārata-mahābh-is-the-mahābhāṣya-and-the-locator-shape-tells-them-apart-mechanically)
- 🟠 [§99. Output gates must audit structured semantic fields, and sample-clean editorial rewrites still require a full-population ambiguity pass](#99-output-gates-must-audit-structured-semantic-fields-and-sample-clean-editorial-rewrites-still-require-a-full-population-ambiguity-pass)
- 🟠 [§101. DCS's compound dictionary carries splits whose member **order** does not match the surface form — invisible to a type-drill, fatal to any head-first analysis](#101-dcss-compound-dictionary-carries-splits-whose-member-order-does-not-match-the-surface-form--invisible-to-a-type-drill-fatal-to-any-head-first-analysis)
- 🟠 [§104. The DCS `dcs-conllu` treebank is only ~3.9 % dependency-parsed — corpus government/valency work must lean on co-occurrence, not arcs, and read absence as "unknown"](#104-the-dcs-dcs-conllu-treebank-is-only-39--dependency-parsed--corpus-governmentvalency-work-must-lean-on-co-occurrence-not-arcs-and-read-absence-as-unknown)
- 🔴 [§505. SamudraManthanam stores canonical line IDs but drops them from durable references — corpus rebuilds can silently retarget exports and corrections](#505-samudramanthanam-stores-canonical-line-ids-but-drops-them-from-durable-references--corpus-rebuilds-can-silently-retarget-exports-and-corrections)
- 🟠 [§448. CORRECTED — the MWScan/2020 `servepdf.php` endpoint is RIGHT (serves 1899); the 1872 first-edition scan coexists on the portal with colliding page numbers](#448-corrected--the-mwscan2020-servepdfphp-endpoint-is-right-serves-1899-the-1872-first-edition-scan-coexists-on-the-portal-with-colliding-page-numbers)
- 🟠 [§449. Samāsa-type frequency does not exist in any org corpus — and the grammarians' canonical examples are corpus-ghosts (8/58 attested, max freq 147)](#449-samāsa-type-frequency-does-not-exist-in-any-org-corpus--and-the-grammarians-canonical-examples-are-corpus-ghosts-858-attested-max-freq-147)
- 🟠 [§450. The roadmap's "OBS-T κ=0.42" was a phantom figure — no measured agreement exists for any OBS-T axis](#450-the-roadmaps-obs-t-κ042-was-a-phantom-figure--no-measured-agreement-exists-for-any-obs-t-axis)
- 🟠 [§451. `10.5281/zenodo.15834721` is a false DOI, cited as genuine in two different repos](#451-105281zenodo15834721-is-a-false-doi-cited-as-genuine-in-two-different-repos)
- 🟠 [§456. MW's derivation markup and the DCS corpus are productive over the *same* compound final members but with near-disjoint first members](#456-mws-derivation-markup-and-the-dcs-corpus-are-productive-over-the-same-compound-final-members-but-with-near-disjoint-first-members-median-jaccard-000-56-share-zero--and-the-corpus-unattested-mw-stratum-is-kośaparticiple-formations-not-ghost-words) — renumbered from §102 (H1328 collision, 20-07-2026).
- 🟠 [§522. A bounded re-split can be displayed honestly at per-cell granularity only because its uncertainty is DEGENERATE — DCS's unmarked perfect makes the defaulted share exactly 0% or 100%, never a fraction](#522-a-bounded-re-split-can-be-displayed-honestly-at-per-cell-granularity-only-because-its-uncertainty-is-degenerate--dcss-unmarked-perfect-makes-the-defaulted-share-exactly-0-or-100-never-a-fraction) — every `Perfect` cell in the DCS paradigm dataset is 100% inferred and every `Aorist` cell 100% attested, so the evidence flag belongs to the CATEGORY, not the cell. Measured 1,955 attested vs 3,229 defaulted cells, zero in between.
- 🟠 [§523. MW's abbreviation legend was never OCR'd — `MWS/prefaces/` stops one page before the required table](#523-mws-abbreviation-legend-list-of-works-and-authors-p-xxxiii-was-never-ocrd--mwsprefaces-stops-at-p-xxxii-one-page-short-of-the-table-every-cross-dict-legend-pipeline-expects) — the apparent MW legend-crosswalk path parses zero keys because the committed transcription ends at p. xxxii; acquire and OCR p. xxxiii+ instead of inventing a secondary-source substitute.
- 🔴 [§524. A parallel-corpus column can be misaligned against its own row key](#524-a-parallel-corpus-column-can-be-misaligned-against-its-own-row-key--griffiths-english-is-off-by-the-vālakhilya-block-for-rv-8498103-and-a-char-count-selftest-cannot-see-it) — Griffith English is displaced for 678 RV stanzas while structural counts remain perfect; cross-check content against another column, not only key/length.
- 🔴 [§525. An interactive tool outside Python's call stack needs durable intent before the call and response-bound evidence inside finalization](#525-an-interactive-tool-outside-pythons-call-stack-needs-a-durable-intent-before-the-call-and-response-bound-evidence-inside-finalization--a-saved-response-alone-cannot-prove-it-was-authorized) — persist an operation identity before spend and the response fingerprint in the same atomic update as finalization; either half alone leaves a duplicate-spend or divergent-replay crash window.
- 🔴 [§526. A second reference is the only cheap way to separate model knowledge from glossing ability](#526-a-second-reference-is-the-only-cheap-way-to-separate-the-model-knows-this-dictionary-from-the-model-can-gloss--and-the-premium-it-exposes-is-small-real-and-largest-exactly-where-memorisation-is-suspected) — rescoring frozen candidates against Heritage French preserves the arm ranking while measuring a small MW-familiarity premium (+0.13…+0.25/5), largest for the no-context memorisation arm; use a judged cross-lingual reference, not surface metrics.
- 🔴 [§527. A schema selftest written from the schema's own constants is blind to a prompt/schema contradiction — the defect it cannot see is exactly the one that burns a paid call](#527-a-schema-selftest-written-from-the-schemas-own-constants-is-blind-to-a-promptschema-contradiction--the-defect-it-cannot-see-is-exactly-the-one-that-burns-a-paid-call) — 24/24 offline cases passed, then the last authorised call failed `malformed_output` because prompt and schema disagreed on one literal; generate shared literals from the fixture once and selftest an instance built from the prompt's own text. Also: `gateway_attestation.py`'s `isSidechain` default yields `null` on harnesses that log Agent calls as main turns, and refused Agent blocks must not be counted as spent calls.
- 🔴 [§528. A top-band-only gold set for BLI reports 99.5% coverage and hides a 0%–100% per-stratum spread — the instrument cannot see what the research question asks](#528-a-top-band-only-gold-set-for-bli-reports-995-coverage-and-hides-a-0100-per-stratum-spread--the-instrument-cannot-see-what-the-research-question-asks) — H1521's top-400-by-frequency gold set could only sample the 0.96–1.00 end of a presence range that runs down to 0.00 (band-1 VERB); the stratified 500-row frame measures 64.2% frame-wide. Report per-stratum presence beside any aggregate — a near-zero cell yields coverage evidence but no P@1 signal.
- 🔴 [§529. An Agent result already carries the exact dispatch binding; widening a transcript window throws that evidence away](#529-an-agent-result-already-carries-the-exact-dispatch-binding-widening-a-transcript-window-throws-that-evidence-away) — one `tool_use.id` links to one `tool_result.tool_use_id`, whose structured `toolUseResult` carries completion status, resolved model, agent id, and usage. Bind that pair plus the ticket prompt hash; main/sidechain becomes observed metadata, adjacent turns become irrelevant, and legacy window attestations stay explicitly non-dispatch-scoped.
- 🟠 [§530. "Whole-card lane" means un-split, not one-call-per-card — production still BATCHES whole cards](#530-whole-card-lane-means-un-split-not-one-call-per-card--production-still-batches-whole-cards) — `_presplit_hit` decides whether a card is cut into fragment groups; the generator's batching decides how many cards ride one call, and for H2630's four un-split cards it emitted 2 calls. A rig issuing one card per call is not production-faithful, so its absolute wall-clock and token figures are not production figures. Check `presplit_keys` and `batches` in the manifest; do not infer the second from the first.
- 🔴 [§531. *Ārṣa prayoga* is a one-way licence — it excuses a deviant form in a POST-Vedic text by appeal to ancient usage, and never authorises describing Vedic material in classical or epic terms](#531-ārṣa-prayoga-is-a-one-way-licence--it-excuses-a-deviant-form-in-a-post-vedic-text-by-appeal-to-ancient-usage-and-never-authorises-describing-vedic-material-in-classical-or-epic-terms) — Pāṇini's `chandasi`-marked architecture, the Mahābhāṣya's `na hy eṣā iṣṭiḥ` rejecting even the reverse transfer, "classical aorist" as a category error, Nīlakaṇṭha stopping at meaning. Three carry-forward facts: `ārṣa` at A 2.4.58 is a *taddhita* affix class, not an exemption; the epic licence is Prakrit-contact/metri-causa, **not** archaism (Oberlies); epic Sanskrit has no recorded accent at all.
- 🟠 [§532. A named DeepSeek-v4-flash judge on frozen grade_gold reaches Spearman ρ=0.4195; the proxy ρ=-0.0351 stays preliminary and is never comet](#532-a-named-deepseek-v4-flash-judge-on-frozen-grade_gold-reaches-spearman-ρ04195-the-proxy-ρ-00351-stays-preliminary-and-is-never-comet) — H2686 n=80 A/B/C slice of `gold/grade_gold.jsonl`; means A 0.924 / B 0.847 / C 0.530. LaBSE failed to load (WinError 1455). Do not relabel either score as COMET.
- 🟠 [§533. H2704 Flash PREP −3.9% is a real point-estimate; the 20% dual-lane NO-GO does not make it zero](#533-h2704-flash-prep-39-is-a-real-point-estimate-the-20-dual-lane-no-go-does-not-make-it-zero) — $0.000839 vs H2675 $0.000873; same-card warm save 9.9% (CI includes 0); Pro pair +39.6% is pair-as-denominator; `ADOPTION.json` unique_clean=1 is a PREP bug.
- 🟠 [§534. H2756 re-test of Flash PREP incremental save on a fresh 50 is INCONCLUSIVE at 0.2%](#534-h2756-re-test-of-flash-prep-incremental-save-on-a-fresh-50-is-inconclusive-at-02) — ratio-of-means (cold − warm) / cold = 0.2%, bootstrap CI includes 0; 99/100 parseable; not “no economy”.
- 🟠 [§535. A CRLF key list makes every pilot input land under a phantom `~000d` stem, and the failure surfaces as "missing input", not as an encoding error](#535-a-crlf-key-list-makes-every-pilot-input-land-under-a-phantom-000d-stem-and-the-failure-surfaces-as-missing-input-not-as-an-encoding-error) — `safe_name()` is total, so a trailing CR silently forks the input namespace; strip CR before piping any key list into a generator.
- 🟠 [§536. The re-glue cards' citations were dead because nothing called the repo's own resolver — and Cologne's precomputed table would have been a downgrade](#536-the-re-glue-cards-citations-were-dead-because-nothing-called-the-repos-own-resolver--and-colognes-precomputed-table-would-have-been-a-downgrade) — `ls_resolver` 83.6% vs csl-lslink table 79.3% over 41,115 store `<ls>`, zero table-only wins, zero href disagreements; "unresolved" is two buckets and only the locus-bearing one is work. Its sizing of that bucket is superseded by §537.
- 🔴 [§537. The mintable citation gap is 60 occurrences, not ~7,000 — the resolver is at the ceiling its scan corpus allows](#537-the-mintable-citation-gap-is-60-occurrences-not-7000--the-resolver-is-at-the-ceiling-its-scan-corpus-allows) — 5,197 of 5,257 cite works Cologne never digitised; the resolver already routes to 49 of 53 hosted text scans. A prefix is not a work: first-token grouping over-counted the cheap bucket 4×, so classify by repair-and-retest, not regex.
- 🔴 [§541. The re-glue typology label is assigned independently of whether an insertion target was found, so 90 % of it asserts a relation to a sense that is not there](#541-the-re-glue-typology-label-is-assigned-independently-of-whether-an-insertion-target-was-found-so-90--of-it-asserts-a-relation-to-a-sense-that-is-not-there) — 5,054 of 5,603 supplements are `target_sense='*new'` yet still labelled `restate`; only 4.4 % are checkable. Gloss-word overlap was measured as an evidence axis and rejected (median 0.000 both classes); `{%…%}` is the German gloss, not Sanskrit — stripping it fakes a finding. **Wave 1 RESOLVED 16-08-2026** (H2879): `placement` splits the pair-claim from the label; the 90 % was three phenomena, of which only 130 rows (2.2 %) are a real defect and 383 are renumbering evidence. Attributable gain measured against identical inputs: +7 checkable pairs, not the +11 a stale baseline implied.
- 🟠 [§539. Kochergina corrections have no tracked home — the org's correction store is CDSL-scoped, and Kochergina is not a CDSL dictionary](#539-kochergina-corrections-have-no-tracked-home-the-orgs-correction-store-is-cdsl-scoped-and-kochergina-is-not-a-cdsl-dictionary) — inherited index row added by H2859; see the section for the finding.
- 🟠 [§540. Mixed-script words hide from every search that assumes one alphabet per word — and the repair map has to be transliteration, not visual shape](#540-mixed-script-words-hide-from-every-search-that-assumes-one-alphabet-per-word-and-the-repair-map-has-to-be-transliteration-not-visual-shape) — inherited index row added by H2859; see the section for the finding.
- 🟠 [§542. A review sheet's stated apply target is not the carrier set — the hand-authored strings can live in a generator, and an apply that trusts the sheet reverts on the next build](#542-a-review-sheets-stated-apply-target-is-not-the-carrier-set--the-hand-authored-strings-can-live-in-a-generator-and-an-apply-that-trusts-the-sheet-reverts-on-the-next-build) — the agni sheet named `agni.pd-min.ru.md` col. 3; the glosses are actually authored in a `GLOSS` dict in `_build_agni_ru.py`, with two more copies downstream. Grep a current cell string, not the filename, before applying any vote — the unvoted aksara/ananta/anya sheets have the same shape with a different layout again.
- 🟠 [§538. A Latin siglum inside a `{#…#}` span is silently transliterated — `pw` became `pṭ`, an abbreviation that does not exist](#538-a-latin-siglum-inside-a-span-is-silently-transliterated-pw-became-pṭ-an-abbreviation-that-does-not-exist) — inherited index row added by H2859; see the section for the finding.
- 🟠 [§543. A sense order can be right for the Vedic layer and useless for the classical one — `guda` is «кишки» in the RV and only ever the anorectal outlet in Āyurveda](#543-a-sense-order-can-be-right-for-the-vedic-layer-and-useless-for-the-classical-one--guda-is-кишки-in-the-rv-and-only-ever-the-anorectal-outlet-in-āyurveda) — 79 occurrences across 30 of 120 DCS Aṣṭāṅgahṛdaya files, zero intestinal. Check the consumer's register before ordering senses; ship a rider when the layers disagree. Plus: `guḍa`/`guda` collapse in Cyrillic, so all 8 «гуда» transcript hits were false positives.
- 🟠 [§544. rvlinks is the pāda-granular RV substrate already on disk — and a verse-granular read of it invents renderings the translator never made](#544-rvlinks-is-the-pāda-granular-rv-substrate-already-on-disk--and-a-verse-granular-read-of-it-invents-renderings-the-translator-never-made) — all 1 028 hymns with Elizarenkova/Geldner/Griffith locally, vs the Mandala I–II SamudraManthanam extract. The 2013 memo's «прямая кишка» for `guda` at RV 10.163.3 is actually her `vaniṣṭhu` — the misalignment class H2850 exists to catch.
- 🔴 [§545. A fixture guard row proves the sanitizer runs, not that it covers every sink — the leak hid in a second consumer the guard row never reaches](#545-a-fixture-guard-row-proves-the-sanitizer-runs-not-that-it-covers-every-sink--the-leak-hid-in-a-second-consumer-the-guard-row-never-reaches) — `sense_tag` was scrubbed for the IRI sink while `edition_rel` interpolated it raw into an `evidence` string emitted verbatim by both serializations. The fixture's guard row never takes an evidence-bearing branch, so no fixture run could have caught it. Enumerate a sanitizable field's sinks; reproduce the leak directly instead of trusting a fixture row to reach the branch.
- 🟠 [§546. DCS ships a 180 k-row lemma→gloss layer next to the corpus — `dcs-conllu/lookup/dictionary.csv`, and almost nothing in the org reads it](#546-dcs-ships-a-180-k-row-lemmagloss-layer-next-to-the-corpus--dcs-conllulookupdictionarycsv-and-almost-nothing-in-the-org-reads-it) — 180 178 rows of `word ⇥ grammar ⇥ meanings`, TAB-separated despite the `.csv` name. It independently reproduces the `vaniṣṭhu`=rectum / `gudā`=bowels / `pāyu`=anus split that §543/§544 established by hand. Read it before proposing to acquire or OCR a translation to settle a sense question.
- 🔴 [§547. PWG's Ṛgveda citations disagree with Elizarenkova far more often than they agree — and a third of the surface cannot be adjudicated at all](#547-pwgs-ṛgveda-citations-disagree-with-elizarenkova-far-more-often-than-they-agree--and-a-third-of-the-surface-cannot-be-adjudicated-at-all) — 2 964 RV citations across 52 entries: 1 221 diverges · 520 agrees · 1 223 undecidable; 17.9 % of pāda joins span more than one pāda, so a verse-granular join misreads one citation in five. Her printed line order is not always pāda order.
- 🔴 [§548. PWG has TWO incompatible families of `<ls>` counts — cleaned-string and work-family — and the volunteer tracker's column is the second](#548-pwg-has-two-incompatible-families-of-ls-counts--cleaned-string-and-work-family--and-the-volunteer-trackers-column-is-the-second) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§549. CommentaryStrategies' published 17,863-note composition was born self-contradictory in one batch commit — and the committed corpus's per-note page anchors are the attribution layer that settles what can be settled](#549-commentarystrategies-published-17863-note-composition-was-born-self-contradictory-in-one-batch-commit--and-the-committed-corpuss-per-note-page-anchors-are-the-attribution-layer-that-settles-what-can-be-settled) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§550. A `Nachtrag` almost never names the sense it amends, but a `1 (PW)` almost always does — so "corrections inside PWG" is two populations, not one](#550-a-nachtrag-almost-never-names-the-sense-it-amends-but-a-1-pw-almost-always-does--so-corrections-inside-pwg-is-two-populations-not-one) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🔴 [§551. The re-glue sidecar's `(subcard, sense_tag)` key is not unique — every consumer that dicts on it silently drops 468 of 6 009 rows](#551-the-re-glue-sidecars-subcard-sensetag-key-is-not-unique--every-consumer-that-dicts-on-it-silently-drops-468-of-6-009-rows) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§552. SCH does almost only supplement PWG — 3.3 % of its rows correct it — but the signal that proves it is a printed imperative, not the gender conflict the roadmap predicted](#552-sch-does-almost-only-supplement-pwg--33--of-its-rows-correct-it--but-the-signal-that-proves-it-is-a-printed-imperative-not-the-gender-conflict-the-roadmap-predicted) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§553. Cappeller (CAE/CCS) marks compounds with the Böhtlingk ring ˚ — and so do 20+ CDSL dictionaries; solid headwords, ring only for the elided member](#553-cappeller-caeccs-marks-compounds-with-the-böhtlingk-ring---and-so-do-20-cdsl-dictionaries-solid-headwords-ring-only-for-the-elided-member) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§554. PW and PWG use the same ring as Cappeller — but PWG *states* the seam (`agni + hotra`, 34 752×) and truncates word-ENDS, while PW and Cappeller flipped the ring to the front](#554-pw-and-pwg-use-the-same-ring-as-cappeller--but-pwg-states-the-seam-agni--hotra-34-752-and-truncates-word-ends-while-pw-and-cappeller-flipped-the-ring-to-the-front) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§555. Apte rings both ways (and abbreviates grammar labels with it); Monier-Williams 1899 is the one dictionary with its own system — the seam printed IN the lemma (`agni—hotra`, 73 772×) plus a mid-word sandhi-seam ring](#555-apte-rings-both-ways-and-abbreviates-grammar-labels-with-it-monier-williams-1899-is-the-one-dictionary-with-its-own-system--the-seam-printed-in-the-lemma-agnihotra-73-772-plus-a-mid-word-sandhi-seam-ring) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§556. Grassmann hyphenates the lemma itself (4 356 of 12 785 — MW's system has a Rig-Veda precedent), and Kochergina's кружок is the Petersburg Kreis arriving in Russian via Böhtlingk's own St. Petersburg typography](#556-grassmann-hyphenates-the-lemma-itself-4-356-of-12-785--mws-system-has-a-rig-veda-precedent-and-kocherginas-кружок-is-the-petersburg-kreis-arriving-in-russian-via-böhtlingks-own-st-petersburg-typography) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§557. Benfey analyzes every second entry in prose (`i. e. apa-car + in`, 9 168×) and keeps the ring for conjectures; Mylius has no measurable source in the org — named gap, not a shrug](#557-benfey-analyzes-every-second-entry-in-prose-i-e-apa-car--in-9-168-and-keeps-the-ring-for-conjectures-mylius-has-no-measurable-source-in-the-org--named-gap-not-a-shrug) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§558. Wilson closes 89 % of entries with a prose `E.` etymology and uses no graphic device at all; Macdonell runs FOUR coordinated devices — including `˚—`/`—˚` as a grammatical notation for position-in-compound](#558-wilson-closes-89--of-entries-with-a-prose-e-etymology-and-uses-no-graphic-device-at-all-macdonell-runs-four-coordinated-devices--including--as-a-grammatical-notation-for-position-in-compound) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§559. «Смыслы MW/AP, отсутствующие у PWG-семейства» — механический счёт завышен ~в шесть раз; 83 % кандидатов «отсутствует» на поверку «не привязано»](#559-смыслы-mwap-отсутствующие-у-pwg-семейства--механический-счёт-завышен-в-шесть-раз-83--кандидатов-отсутствует-на-поверку-не-привязано) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🔴 [§560. `key1` стора pwg_ru деградирован у 161 строки — и сливает разные леммы в один ключ; лучший свидетель — префикс `subcard`, но и он врёт о долготе/придыхании](#560-key1-стора-pwgru-деградирован-у-161-строки--и-сливает-разные-леммы-в-один-ключ-лучший-свидетель--префикс-subcard-но-и-он-врёт-о-долготепридыхании) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§561. Whitney has no ring at all — his device is the leading hyphen on bound stems (Roots 1885) and analysis-only hyphenation (Grammar); attested compounds are quoted solid with accent](#561-whitney-has-no-ring-at-all--his-device-is-the-leading-hyphen-on-bound-stems-roots-1885-and-analysis-only-hyphenation-grammar-attested-compounds-are-quoted-solid-with-accent) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🔴 [§562. Печатный заголовок карточки ОПРОКИДЫВАЕТ §560: дефект стора pwg_ru — не деградация key1, а инжест ЧУЖОЙ статьи-двойника; настоящие статьи 60+ целевых лемм в сторе отсутствуют](#562-печатный-заголовок-карточки-опрокидывает-560-дефект-стора-pwgru--не-деградация-key1-а-инжест-чужой-статьи-двойника-настоящие-статьи-60-целевых-лемм-в-сторе-отсутствуют) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§563. Symmetric akshara word-squares over inflected beginner vocabulary are structurally near-infeasible — word-medial syllables almost never begin words](#563-symmetric-akshara-word-squares-over-inflected-beginner-vocabulary-are-structurally-near-infeasible--word-medial-syllables-almost-never-begin-words) — inherited index row backfilled by H2983 (integrity repair); see the section for the finding.
- 🟠 [§564. skd/vcp confirm ZERO graphic compound markers — the kośas print the whole apparatus in Sanskrit: SKD spells the vigraha + class term in parentheses, VCP compresses the same grammar into ॰-abbreviations with a numeral for the vibhakti (`6 ta0` = ṣaṣṭhī-tatpuruṣa)](#564-skdvcp-confirm-zero-graphic-compound-markers--the-kośas-print-the-whole-apparatus-in-sanskrit-skd-spells-the-vigraha--class-term-in-parentheses-vcp-compresses-the-same-grammar-into--abbreviations-with-a-numeral-for-the-vibhakti-6-ta0--ṣaṣṭhī-tatpuruṣa) — skd spells the apparatus (parenthesized vigraha + spelled class term, `iti <source>` net, Bengali `iti BAzA` glosses); vcp compresses it into 167 759 ॰-abbreviations (ASCII `0` in the digitization) with a numeral for the vibhakti — `6 ta0` = ṣaṣṭhī-tatpuruṣa, class tags sense-scoped. The kośa ॰ points at the metalanguage, never the object word; Apte's `[za˚ ta˚]` is this device transliterated westward.
- 🟡 [§565. Prosody marks (breve/macron) appear in 27 dictionaries; 11 show collision risk with seam notation](#565-prosody-marks-brevemacron-appear-in-27-dictionaries-11-show-collision-risk-with-seam-notation) — 27 dicts carry breve, 25 macron; the MW-family em-dash is seam notation, not quantity — separate by context, not by character.
- 🔴 [§566. `<div n=…>` is not a shared sense-hierarchy device — only PW/PWG/BOR nest senses, and PWG leaves sense 1 outside the markup in a quarter of its hierarchical entries](#566-div-n-is-not-a-shared-sense-hierarchy-device--only-pwpwgbor-nest-senses-and-pwg-leaves-sense-1-outside-the-markup-in-a-quarter-of-its-hierarchical-entries) — 20/44 dicts carry `<div>`, only pw/pwg/bor use a numeric level; 25.2 % of hierarchical PWG entries open at `2〉` because sense 1 sits unmarked in the head line. Only PWG's own order may enter a pwg_ru card.
- 🔴 [§567. The memo's `<ls>L.</ls>` "lexicographers-only" marker does not exist in PWG — the real signal is `renou_register.py`'s own `ls`/`dcs` provenance tag](#567-the-memos-lslls-lexicographers-only-marker-does-not-exist-in-pwg--the-real-signal-is-renou_registerpys-own-lsdcs-provenance-tag) — a literal search for `<ls>L.</ls>` in `pwg.txt` finds nothing; the real lexicographers-only signal lives in `renou_register.py`'s own provenance fields.
- 🟠 [§568. Renou diachronic state V is never populated in `pwg_sense_stratum.jsonl`](#568-renou-diachronic-state-v-is-never-populated-in-pwg_sense_stratumjsonl) — `renou.py`'s canonical `STATES` tuple declares `(I, II, III, IV, V)`, but 0 of 64,296 per-sense rows ever carry state V.
- 🟠 [§569. A bracketed `[Gen, unsp]` domain/period tag collides on the letters "Gen" with the genitive-case abbreviation](#569-a-bracketed-gen-unsp-domainperiod-tag-collides-on-the-letters-gen-with-the-genitive-case-abbreviation--needs-the-same-masking-discipline-as--sanskrit-spans) — `pwg_ru_translated.jsonl`'s `ru` field carries two independent short-tag taxonomies that collide on the literal string "Gen"; needs the same `{#…#}`-style masking already used for Sanskrit spans.
- 🟠 [§570. Renaming a stored abbreviation stem (`Instr.`→`Ins.`) silently breaks tooltip lookup against an external authoritative table still keyed on the old stem](#570-renaming-a-stored-abbreviation-stem-instrins-silently-breaks-tooltip-lookup-against-an-external-authoritative-table-still-keyed-on-the-old-stem) — a render-time tooltip resolver looks the stored token up against an external ground-truth table; renaming the stored stem without updating that table silently orphans the tooltip.
- 🔴 [§571. The compound-position ring is not an inferred convention — Cappeller PRINTS its definition in 1887, six years before Macdonell](#571-the-compound-position-ring-is-not-an-inferred-convention--cappeller-prints-its-definition-in-1887-six-years-before-macdonell-the-whole-553566-census-had-never-opened-a-preface) — Cappeller's Vorrede (CCS 1887) and Symbols page (CAE 1891) both print the ring's definition in words, six years before Macdonell (1893); the §553–§566 census had counted the device without ever reading a preface.
- 🟢 [§572. Homonym-splitting density spans 0 to 419 per 1 000 entries across the 44 dicts — general dictionaries cluster at 20–65, name-indices at 89–419, and 22 dicts split none](#572-homonym-splitting-density-spans-0-to-419-per-1-000-entries-across-the-44-dicts--general-dictionaries-cluster-at-2065-name-indices-at-89419-and-22-dicts-split-none-hom-inline-markers-over-count-h-metadata-by-up-to-36) — 8 dicts print inline `<hom>N.` numbering, 14 split without displaying it, 22 split nothing; the high-density class (pui/inm/pe/mci/lrv/bop) is genre — name-indices splitting distinct persons, not sense-dictionaries splitting polysemy. `agnihotra` splits mfn./n. in 6 dicts and stays one entry in ap/vcp/wil — a 1:2-vs-1:1 join mismatch any headword matcher must carry.
- 🔴 [§573. The leading hyphen has two senses, but no dictionary marks which — Wilson is 100 % inflectional, Macdonell is 83 % compound-member/2 % inflectional/15 % a third (taddhita) class the two-way split cannot hold](#573-the-leading-hyphen-has-two-senses-but-no-dictionary-marks-which--wilson-is-100--inflectional-macdonell-is-83--compound-member2--inflectional15--a-third-taddhita-class-the-two-way-split-cannot-hold) — Wilson 49,487/49,487 leading-hyphen runs read as inflection; MD's `{@-X@}` overloads compound-member/inflection/taddhita-derivational; Whitney's Roots and Grammar use two different devices under one name. Ships a 4-rule markup-context disambiguation table.
- 🟢 [§574. Gloss-language layering: `{%…%}` is not "German-or-English" — it also carries French (Burnouf) and editorial prose (Sircar), and the Latin `<ab>` layer is itself language-specific per dictionary](#574-gloss-language-layering-is-not-german-or-english--it-also-carries-french-burnouf-and-editorial-prose-sircar-and-the-latin-ab-layer-is-itself-language-specific-per-dictionary) — `bur` wraps French prose in `{%…%}` at 100 % of entries; `mw`/`cae` use zero `{%…%}` despite dense glosses, needing tail-text extraction not tag-grepping; `<ab>` is Latin in mw but German in gra; koch.jsonl is 99.98 % Russian by construction.
- 🔴 [§575. Root citation is not "root vs 3sg present" — it's zero-grade `kf` (19/44 dicts) vs guṇa-grade `kar` (pw/pwg/pwkvn/sch), which WhitneyRoots' `roots.csv` cannot join at all; class digits fragment across four incompatible devices](#575-root-citation-is-not-root-vs-3sg-present--its-zero-grade-kf-1944-dicts-vs-guṇa-grade-kar-pwpwgpwkvnsch-which-whitneyroots-rootscsv-cannot-join-at-all-class-digits-fragment-across-four-incompatible-devices) — the same root ("to do") is lemmatized as `kf` in 19 dicts and as `kar` in the four PW-family dicts (pw/pwg/pwkvn/sch); `roots.csv`'s header has no pw_id/pwg_id column at all, so Cologne's two largest dictionaries (643K/593K lines) are currently unjoinable. Class digits: MD's `<cl>` tag, MW/WIL's `<ab>cl.</ab>` text, Apte's `€1`–`€10` glyph, PWG's German "Kl." prose — four devices, none shared.
- 🔴 [§577. A citation resolver that mints a well-formed URL is not evidence the address exists — `ls_resolver` happily places `ṚV. 99,999,999`, so "it resolves" cannot be the acceptance test for a split or a wrapper](#577-a-citation-resolver-that-mints-a-well-formed-url-is-not-evidence-the-address-exists--ls_resolver-happily-places-v-9999999-so-resolves-cannot-be-the-acceptance-test-for-a-split-or-a-wrapper) — the resolver is a formatter, not a validator: it range-checks nothing. Any pass that INVENTS an address (splitting a multi-address `<ls>`, wrapping a bare citation) and accepts it because a URL came back will mint links that work and point at the wrong place — a worse failure than no link, because it looks right. Measured on pwg.txt: a resolve-only rule proposed 2,838 splits, of which 0 were correct; page references `11087 (p. 572)`, note markers `83, N. 6` and Oxford column letters `100,a. 101,b` all "resolve". The correct population was in `pw` (141), not `pwg` (0).
- 🟠 [§580. AP90's `<pc>` field is a third, distinct shape from mw/pwg — page-column-letter (`NNNN-a/b/c`), not comma or vol-page — and a tool that assumes one shape silently drops 100% of a dict's scan links](#580-ap90s-pc-field-is-a-third-distinct-shape-from-mwpwg--page-column-letter-nnnn-abc-not-comma-or-vol-page--and-a-tool-that-assumes-one-shape-silently-drops-100-of-a-dicts-scan-links) — csl-atlas's Cologne scan-URL builder trusted only mw's `page,column` and pwg's `vol-page` shapes, so AP90 (page-column-*letter*) silently resolved 0% of 34,882 entries despite correct scan-directory registration; fixed 24-08-2026, now 99.29%; a residual 246 entries carry a *fourth* shape (`NNNN-N` numeric suffix), unresolved. Corrects §23's aside that AP90's `<pc>` is "numeric `<pc>0002-1`" — that's the 0.7% residual, not the dominant convention.
- 🔴 [§581. A dictionary index's "SLP1" column can be Harvard-Kyoto — KEWA's is, and joining it as SLP1 silently drops half the headings; separately, NFD-stripping the Vedic acute destroys ś](#581-a-dictionary-indexs-slp1-column-can-be-harvard-kyoto--kewas-is-and-joining-it-as-slp1-silently-drops-half-the-headings-separately-nfd-stripping-the-vedic-acute-destroys-ś) — KEWA's second machine-key column reads like SLP1 and is Harvard-Kyoto (ś=`z`, ṣ=`S`, ṇ=`N`, `ai`/`au`); joining it as SLP1 silently drops 5,733 of 11,418 headings, just over half, with no error anywhere — 99.99 % confirmed by round-tripping the whole column through the canonical transcoder. Second trap in the same file: NFD + "drop every U+0301" destroys **ś**, which decomposes to `s` + acute, turning every *śa*-word into an *sa*-word before the join.
- 🟠 [§582. The damage in a digitized index is not always OCR — KEWA's came from a Russian-locale spreadsheet, which turned page ranges into dates and leading-hyphen headwords into `#ИМЯ?`](#582-the-damage-in-a-digitized-index-is-not-always-ocr--kewas-came-from-a-russian-locale-spreadsheet-which-turned-page-ranges-into-dates-and-leading-hyphen-headwords-into-имя) — 9,587 of 9,588 lines parse first-pattern: there is no OCR noise to census. The real damage is a spreadsheet round-trip in a ru-RU locale — three page ranges stored back as dates (`10-11` → `10.ноя`) and five leading-hyphen headings as `#ИМЯ?` — and both classes are fully recoverable from a redundant column. An OCR-shaped audit finds none of them and reports the file clean.
- 🔴 [§583. "How many senses does this PWG lemma have?" is undefined until you fix the layer — the naive count runs 10–40× high](#583-how-many-senses-does-this-pwg-lemma-have-is-undefined-until-you-fix-the-layer--the-naive-count-runs-1040-high) — counting distinct `sense_tag` per `key1` in the pwg_ru store conflates five dictionary layers (97 of 254 lemmas straddle more than one), swallows structural apparatus (`main`, `intro`, `Nachtrag`) and derived-stem slots (`caus`, `desid`), and treats `1` and `1)` as different senses: `han` reads as 430 senses naively, 90 within `pwg`, and **11** as numbered senses in one layer. The apparent bimodality — an unpickable 300–430-sense verb-root tail — is an artifact; the store-wide maximum under the correct definition is **16**. A related trap: cross-layer duplicate subcards yield menu options that are textually identical (`[1] раздувание, вздутие` vs `[PW] раздувание, вздутие`), which is unanswerable, so any κ over them measures coin-flips.
- 🟠 [§584. A style pass applied to CommentaryStrategies' `data/lexical/chN.json` never reaches the apparatus or the print master — `build_sarga_apparatus.py` prefers the aggregate twins in `data/sundara_commentary_to_add.json`, so the source you edited is the one that loses the dedup](#584-a-style-pass-applied-to-commentarystrategies-datalexicalchnjson-never-reaches-the-apparatus-or-the-print-master--build_sarga_apparatuspy-prefers-the-aggregate-twins-in-datasundara_commentary_to_addjson-so-the-source-you-edited-is-the-one-that-loses-the-dedup) — H3498 (Fable 5 `claude-fable-5`, 25-08-2026).
- 🟠 [§585. Paired totals N and N+1 for the same TSV artifact are the header-row signature — read line 1 before hypothesizing regeneration drift](#585-paired-totals-n-and-n1-for-the-same-tsv-artifact-are-the-header-row-signature--read-line-1-before-hypothesizing-regeneration-drift) — `union_headwords.tsv` holds 323,426 physical lines of which line 1 is the column header, so the headword count of record is 323,425; every published 323,426 counted file lines, every 323,425 counted headwords, and the months-open CONTRADICTIONS §10 closed with one `wc -l` + `head -1` — H3538 (Fable 5 `claude-fable-5`, 26-08-2026).
- 🟠 [§586. Two conflicting family totals can be exact sums of the SAME files at two pipeline stages — the 285,799 vs 285,950 gap is the union build's key collapse, not vintage drift](#586-two-conflicting-family-totals-can-be-exact-sums-of-the-same-files-at-two-pipeline-stages--the-285799-vs-285950-gap-is-the-union-builds-key-collapse-not-vintage-drift) — 285,950 = 106,082+151,349+28,519 (raw now-2026 export `wc -l`) and 285,799 = 106,054+151,314+28,431 (union-ingested rows); the 151-key gap is the build's key collapse (PWG −28, PWK −35, SCH −88), vintage/key-mixing REFUTED; quote either figure only with its stage named — H3538 (Fable 5 `claude-fable-5`, 26-08-2026).
- 🟠 [§587. Derivative ī/ū-stem gen.pl accent: oxytone nouns are 44/44 stem-final, the devī́-declension adjective/participle class genuinely vacillates — Whitney §319a and §320/§356 have disjoint scopes](#587-derivative-īū-stem-genpl-accent-oxytone-nouns-are-4444-stem-final-the-devī-declension-adjectiveparticiple-class-genuinely-vacillates-whitney-319a-and-320356-have-disjoint-scopes) — full-corpus census: oxytone noun stems 44/44 stem-final `-īnā́m`, devī́-declension adjective/participle feminines genuinely mixed; Whitney §319a vs §320/§356 are disjoint scopes — CONTRADICTIONS §1 ruled, GAPS §1 closed — H3555 (Fable 5 `claude-fable-5`, 26-08-2026).
- 🟠 [§588. The VedaWebProject/vedaweb-data GitHub mirror replaces the WAF-blocked VedaWeb API for bulk corpus pulls](#588-the-vedawebprojectvedaweb-data-github-mirror-replaces-the-waf-blocked-vedaweb-api-for-bulk-corpus-pulls) — `vedaweb.uni-koeln.de` answers HTTP 418 since 12-07-2026; `rigveda/versions/zurich.xlsx` in the public GitHub mirror carries the same Zurich glossed RV (164,768 token rows) — clone it, never wait out the outage — H3555 (Fable 5 `claude-fable-5`, 26-08-2026).
- 🔴 [§591. Withdrawing a false gloss clears the serious-error ceiling and breaks the fidelity floor — a quality gate can be moved rather than passed](#591-withdrawing-a-false-gloss-clears-the-serious-error-ceiling-and-breaks-the-fidelity-floor-a-quality-gate-can-be-moved-rather-than-passed) — the 10 H2684 serious rows were all `fidelity: pass` before repair (a wrong Russian gloss reads as faithful-but-inequivalent); reverting them to German scores `german_residue` — serious 2.50 %→**0.00 % PASS** but fidelity 99.50 %→**97.25 % FAIL**, measured by an independent Grok 4.5 re-score — H3611 (Opus 5 `claude-opus-5`, 28-08-2026).
- 🟠 [§598. A durable-evidence-root guard only protects the target it is called on — a sibling constant that never runs through the resolver can still split silently](#598-a-durable-evidence-root-guard-only-protects-the-target-it-is-called-on--a-sibling-constant-that-never-runs-through-the-resolver-can-still-split-silently) — `#1034` fixed `resolve_evidence_root`/`assert_durable_evidence_root` for the per-account probe events series, but `max_account_orchestrator.HEALTH_PROBE_LOG` (the canonical cross-account log) was a separate module constant that never derived from the resolved root, so a paid probe with a perfectly durable `--evidence-dir` still lost its canonical row to a disposable worktree — H3642 (Sonnet 5 `claude-sonnet-5`, 28-08-2026).
- 🔴 [§597. `cost_evaluable: false` is a pipeline attribution gap, not absent price data — the CLI envelope carries real dollars](#597-cost_evaluable-false-is-a-pipeline-attribution-gap-not-absent-price-data--the-cli-envelope-carries-real-dollars) — a run reading `observed_cost_usd: 0.0, cost_evaluable: false` also read `usage_evaluable: true, priced_calls: 20`, and the failing call's envelope carried `total_cost_usd: 0.4131022`; scaled it corroborated the preflight at ~$5-6. "Unevaluable" is never "zero", and cache-creation (~20× read) is reported apart from cache-read — H3627 (Opus 5 `claude-opus-5`, 28-08-2026).
- 🔴 [§596. A pwg_ru window discards every paid success when one mid-window call fails schema validation](#596-a-pwg_ru-window-discards-every-paid-success-when-one-mid-window-call-fails-schema-validation) — 20 priced calls, 19 successes, then `structured_output_retry_exhausted` at `b13` and `out.json` never written, so 13 billed headwords were discarded; size a window on the variance of TOTAL LOSS, not mean cost per card — H3627 (Opus 5 `claude-opus-5`, 28-08-2026).
- 🔴 [§595. A liveness watchdog is only meaningful against a STREAMING output format — arming one on a buffered spawn kills the healthy calls, not the hung ones](#595-a-liveness-watchdog-is-only-meaningful-against-a-streaming-output-format-arming-one-on-a-buffered-spawn-kills-the-healthy-calls-not-the-hung-ones) — every paid lane here spawns `claude -p --output-format json`, which writes the whole envelope in one burst at the end, so a healthy call’s stdout is 0 bytes for its full 49 404-511 908 ms; the 90 s window H2878 specifies would have killed essentially every healthy call. Derive the window from the declared output format (`json` → observe-only, `stream-json` → 90 000 ms) rather than pinning a literal per call site — H2878 (Opus 5 `claude-opus-5`, 28-08-2026).
- 🔴 [§594. A repair pass must query EVERY shipped resolver, not just the one its rule names — H2877 reverted five rows to German that shipped code already answered](#594-a-repair-pass-must-query-every-shipped-resolver-not-just-the-one-its-rule-names-h2877-reverted-five-rows-to-german-that-shipped-code-already-answered) — `placeholder_ru()` shipped 24-08-2026 pinning `Jmd`→«кто-л.»; H2877 ran on 27-08, queried only the exact-source lexicon, found nothing (the span is denylisted — correctly) and reverted to German, leaving 5 of 10 rows unpromotable until H3628 called the shipped table — H3628 (Opus 5 `claude-opus-5`, 28-08-2026).
- 🔴 [§593. A store write that removes rows leaves the TM mirror serving exactly what you just removed](#593-a-store-write-that-removes-rows-leaves-the-tm-mirror-serving-exactly-what-you-just-removed) — the `pwg-ru-data/tm/` mirror is a copy of the canonical store, so H2996’s 159-row quarantine and the H3593 `dA` requeue left `only_mirror` at **167**; a window run with `--tm=auto` would have re-served precisely the cards just quarantined. Refresh in the same pass as the store write, and guard the copy — byte-equality of `ru` cannot tell id churn from real loss — H3627 (Opus 5 `claude-opus-5`, 28-08-2026).
- 🔴 [§592. A gitignored artifact labelled "regenerable" with hardcoded consumers is a shared singleton, and the label is often false](#592-a-gitignored-artifact-labelled-regenerable-with-hardcoded-consumers-is-a-shared-singleton-and-the-label-is-often-false) — `nominal_batch_worklist.json` is read by four consumers including the public progress kitchen, and per the H963 C4 call graph D7 it cannot be rebuilt in a clean worktree at all, so an overwrite is unrecoverable; a writer of a shared intermediate takes `--out` rather than a module constant — H3627 (Opus 5 `claude-opus-5`, 28-08-2026).
- 🔴 [§590. A denylist keyed on function words cannot fence a reuse lexicon — archaic-orthography content glosses still return unrelated targets](#590-a-denylist-keyed-on-function-words-cannot-fence-a-reuse-lexicon-archaic-orthography-content-glosses-still-return-unrelated-targets) — `pwg_tm_wave2_policy.SHORT_GLOSS_DENYLIST` fences 30 German function words, so `{%Jmd%}` is refused, but `{%thun%}` (archaic *tun*) is a content word and the policy-ON lexicon still returns `{%класть%}` for it today; the same denylist also intercepts 4 *correct* fills per 400 rows, and catches only 8 of the 13 rows that carry the mechanism — H2877 (Opus 5 `claude-opus-5`, 27-08-2026).
- 🔴 [§589. The R4.1 "any SAN-LOSS reaching the store" freeze trigger is a marker grep, not a gate — four real SAN-LOSS rows sit in the pwg_ru store unseen](#589-the-r41-any-san-loss-reaching-the-store-freeze-trigger-is-a-marker-grep-not-a-gate-four-real-san-loss-rows-sit-in-the-pwg_ru-store-unseen) — `spot_check_daily.store_san_loss_scan` greps `ru` for the literal `SAN-LOSS` string and never recomputes `{#…#}` spans; the real gate over all 11 620 rows finds 4 SAN-LOSS + 1 LS-LOSS rows (`dA` desid. head-line, `dA`+`anu`, `mA`, `pat`, `asvatantra`); the spot-check task is Disabled with 0 receipts ever — runner `audit_store_gates.py` — H3590 (Fable 5 `claude-fable-5`, 27-08-2026).
- 🟢 [§579. Citation density is a cliff, not a spectrum — 16 dicts wrap citations in `<ls>`, 22 have literally zero, and PWG alone carries 801 788 of them](#579-citation-density-is-a-cliff-not-a-spectrum--16-dicts-wrap-citations-in-ls-22-have-literally-zero-and-pwg-alone-carries-801-788-of-them-tag-presence-misclassifies-gra-whose-printed-proof-lives-in-prose) — extends §18's four-dict measurement to all 44: pwg 94.4 % of entries cite at 6.50/entry (801 788 elements, more than the next five dicts combined), mw 79.1 %, ap90 31.2 %; 22 koṣa/index dicts carry zero `<ls>`; pw-vs-pwg is abridgement depth (38.8 % vs 94.4 %); GRA proves in prose + `〔p. N〕` brackets while its `<ls>` share is only 12.0 % — the corpus's biggest citation-extraction residual.
- 🟢 [§578. Accent digitization is three incompatible devices and svarita is essentially un-digitized](#578-accent-digitization-is-three-incompatible-devices-and-svarita-is-essentially-un-digitized) — `/` is headword-field accentuation in exactly 9 of the 44 dicts (mw 47 589, pw 21 543, pwg 20 876, cae 11 313, ccs 8 476, gra 10 699, lan 2 226, sch 1 124, pwkvn 2 108 lemmas), `\` svarita survives in 17 lemma marks total (pw 5, pwg 10, pwkvn 2), and stc/fri/bur/md-style transliteration carries accent as acute vowels that never reach `<k2>`; the pw-family homonym pair `agnihotra/` n. vs `agni/hotra` mfn. makes the slash itself a sense disambiguator any join must preserve.
- 🟠 [§576. Cross-reference markers are three unrelated graphs, not one — `s.`/`Vgl.`/`q.v.`/`=` each point differently, "vide" is a false positive almost everywhere it was expected, and the ring rides inside an xref target far beyond Kochergina](#576-cross-reference-markers-are-three-unrelated-graphs-not-one--svglqv-each-point-differently-vide-is-a-false-positive-almost-everywhere-it-was-expected-and-the-ring-rides-inside-an-xref-target-far-beyond-kochergina) — `s.`/`siehe` and `=` are real graph edges to another headword; `Vgl.` is a weaker "compare" edge, often targeting a citation not a lemma; `q.v.` (the same printed abbreviation) fragments into four incompatible tag shapes across mw/cae/bhs/ap/ap90/wil/mw72/lrv/inm; `vide` is genuine Sanskrit *vidé* in pwg/pw (false positive) and vanishes to zero in ccs/sch under a word-boundary check; gra's bare `<ab>s.</ab>` (1,643) is grammatical Singular, not "see" — the real xref is `<ab n="siehe">s.</ab>` (663). Ring-in-target (§556) recurs at <1% in pwg/pw/mw/sch, not koch-specific.
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
**Recurred 17-07-2026 as [§90](#90-a-spelling-keyed-join-onto-whitneys-roots-union-smears-homonyms--one-authorial-entry-lands-on-every-homonym-of-that-spelling-and-the-rows-still-read-authorial)** —
same class, different vector: not a scrape merging classes, but a *spelling-keyed join* smearing an
author's own classification onto every homonym of that spelling. Whitney's homonym numbering defeats
anything keyed on the citation form alone; that is the general lesson, and it is not scrape-specific.

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

### §506. A complete-coverage count cannot see commentary leaking into an extracted translation layer
🔴 **`10,552/10,552, 0 unmatched` held while four separate defect classes were putting the
book's editorial matter and page furniture inside the translation text.** Evidence: extracting
Jamison–Brereton 2014 from the archive.org OCR of the three print volumes
([`src/rv_jamison_brereton_extract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_jamison_brereton_extract.py),
H1910) hit the canonical-coverage bar early and held it through every one of these:

| Defect | Extent | Longest "stanza" |
|---|---:|---:|
| Next hymn's whole heading block swallowed (its heading was OCR-destroyed) | 8 hymns | 5,751 chars |
| `Mandala N` section introduction swallowed at a mandala boundary | 9 stanzas | 4,387 |
| Hymn-**group** introduction swallowed — no heading, no metre line, no keyword | 11 detected | 2,434 |
| Page number + running head embedded mid-text (stripped at detection, not at assembly) | 1,031 stanzas | — |
| Mangled running head glued to the last word (`V111.78`, `VI.43^4`) | 16 stanzas | — |

The general lesson, applicable to any print-source extraction: **completeness and correctness
are independent, and the cheap gate only measures completeness.** Two checks did find these,
and both are cheap enough to keep permanently: (1) a length distribution — a stanza of 5,751
characters against a median of 190 is not a long stanza; (2) a **terminal-punctuation rate
compared against an independently-extracted sibling layer** — J–B measured 9.77 % of stanzas
ending without terminal punctuation against Griffith's 1.87 %, and the whole gap was embedded
furniture. Griffith works as a control precisely because a different script built it from a
different source. After the fixes: 2.50 % vs 1.87 %, longest stanza 454, and the residual is
OCR-dropped periods (298 of them mid-hymn, where the next stanza marker bounds the text and
truncation is structurally impossible).

> Opus 5 1M `claude-opus-5[1m]` · 2026-07-30

### §507. Do not find hymn headings in an OCR'd Vedic translation by matching roman numerals
🔴 **`^[IVX]+\.\d+` matches 2,303 lines in the J–B OCR, and they are overwhelmingly prose
cross-references rather than headings.** Evidence (H1910; two of these were paid for in wrong
probes before the parser existed): a parser built on that pattern reconstructs 767 hymns and
6,986 loci, all of it assembled from citations like "V.84 could be a later composition…" or
"III.31.1-3), a fact that may point…". Three compounding traps:

1. **Anchoring is not enough.** Accepting a candidate that resolves to a hymn "at or after the
   current position" still fails — a *forward*-pointing citation hijacks the pointer and every
   hymn it skipped is lost. That reading found **358 of 1,028** headings, because the general
   introduction cites hymns before Mandala I even begins.
2. **The heading form is not constant across the volumes.** Mandalas I–II use `I.l Agni` (the
   OCR renders the digit `1` as lowercase `l`); from III.8 the headings carry a continuous
   hymn serial, `IV.44(340) Asvins`; and **Mandala II is rendered as arabic `11`**
   (`11.1(192) Agni`). That serial runs 1..**1017**, not 1..1028, because J–B number the
   eleven Vālakhilya hymns (VIII.49–59) separately — so it can be recorded but never used as
   a key.
3. **Some headings are destroyed outright** — `mil (527) Agni` is VII.11, `m103(619) Frogs` is
   VII.103, `V.IO (364) Agni` is V.10. Eight of 1,028. Widening the regex to catch those tokens
   buys 8 hymns at the cost of an unknown number of false anchors, so they are better recovered
   **positionally**: group the canonical hymns under the heading that opens their line range,
   and resolve them from the last one backwards.

What does work: segment **positionally against the canonical locus set** (here VedaWeb's
`lemmatization.json`), and match stanza markers **in reverse** within a hymn's range, taking
the last candidate for each number. Reverse matching is what keeps a per-hymn introduction out
of the column — an introduction sits *before* stanza 1, so a line-initial "1." inside it is
never the last candidate for stanza 1, whereas forward-greedy silently adopts the whole
introduction as the text of stanza 1.

> Opus 5 1M `claude-opus-5[1m]` · 2026-07-30

### §508. archive.org OCR: use `/download/`, not `/stream/` — and expect no diacritics
🟠 **`/stream/<ident>/<file>_djvu.txt` returns the viewer page** — HTML wrapper, an analytics
`<script>`, and a closing `</body></html>` around the text. `/download/<ident>/<file>_djvu.txt`
returns clean text (H1910: 4.2 MB, 116,661 lines, no wrapper). Two further properties worth
knowing before planning work on an archive.org OCR: the **printed line structure is not
recoverable** — it inserts blank lines *within* a printed line as often as between them, so a
pāda/verse-line layout cannot be reconstructed and the honest output is one normalised
paragraph per unit; and **Latin diacritics are flattened**, so transliterated Sanskrit inside
the OCR is unreliable *as* transliteration (measured at RV 10.106.5–8, where J–B print
transliterated Vedic instead of a translation).

> Opus 5 1M `claude-opus-5[1m]` · 2026-07-30

### §509. J–B decline to translate RV 10.106.5–8 rather than omit them
🟠 **At the four stanzas Geldner omits (RV 10.106.5–8), Jamison–Brereton print transliterated
Vedic, not English.** Evidence (H1910): those loci are `present` in the spine, with non-empty
text carrying no English function words at all. This matters for any pairwise comparison over
the layer — a naive reading treats them as an English rendering and ends up comparing
transliteration against translation. It is also the substantive point: the stanza that made
Geldner skip is the stanza J–B refuse to render, which is convergent evidence about the text
rather than about either translator. Griffith, by contrast, does render them.

> Opus 5 1M `claude-opus-5[1m]` · 2026-07-30

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

> **Source:** data [`v02/skd/skd.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt)
> · [`v02/vcp/vcp.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt) (grep: no `<ab>`/`<div>`). — SKD / VCP (csl-orig) · 2026-06

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
> [`v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt). — csl-orig (mw) · 2026-06-26

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
> [`v02/ap90/ap90.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt). — csl-guides / csl-apidev / csl-orig · 2026-06

**Addendum (24-08-2026):** the "`<pc>0002-1` numeric page-cols" aside above
described the rare shape, not the dominant one — see
[§580](#580-ap90s-pc-field-is-a-third-distinct-shape-from-mwpwg--page-column-letter-nnnn-abc-not-comma-or-vol-page--and-a-tool-that-assumes-one-shape-silently-drops-100-of-a-dicts-scan-links)
for the measured breakdown (99.3% page-column-letter `NNNN-a/b/c`, 0.7%
numeric-suffix `NNNN-N`).

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

### §452. csl-atlas's PWG parse-rules census is stale and incomplete — 21 real markup tags missing, several listed counts wrong

_↩ **Renumbered §448 → §452** (H1362, 20-07-2026): this H1350 block (PR [#612](https://github.com/gasyoun/SanskritLexicography/pull/612), published 13:58) and the H1361 movers (PR [#615](https://github.com/gasyoun/SanskritLexicography/pull/615), 14:38) both took §448–451; the movers are the claims named by the merged [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md), so under rule 4's citation exception they keep §448–451 and this block moves. See ruling §6._

🟠 **The measured PWG markup census (`csl-atlas/data/parse-rules/pwg.json`) undercounts and omits real tags against the current `csl-orig/v02/pwg/pwg.txt`.**
Evidence: a direct regex scan of the live file found 21 element names never listed in the
census's `field_inventory`/`unmapped_tags` — `gk`(326) `bot`(5427) `ocs`(58) `arab`(117)
`mng`(40) `heb`(3) `iw`(53) `zoo`(134) `per`(7) `abot`(209) `ed`(47) `pe`(314) `rus`(22)
`ger`(1) `azoo`(3) `mong`(2) `enum`(3) `ms`(2) `ns`(2) `zen`(1) `num`(1) — `<bot>` (botanical
Latin-name markers) alone outnumbers `<h>` (homonym number, 6,499). Separately, three tags
the census DOES list disagree with a live count: `div` census=113,613 vs live=100,080; `H`
census=76 vs live=7; `span` census=88 vs live=0. The file itself is byte-identical to
`origin/main` (not a stale local clone) — the census generator ran against a different
snapshot or used a different counting method.
Implication: any downstream consumer treating this census as ground truth (a validator, a
coverage report, a data-layers plan) should live-scan the actual file rather than trust the
census numbers; a re-run of csl-atlas's census generator is a genuine `@DECIDE`/backlog item.

> **Source:** H1350 (PWG data-layers wave) step W1.2 — direct regex scan of `csl-orig/v02/pwg/pwg.txt`
> against [`csl-atlas/data/parse-rules/pwg.json`](https://github.com/gasyoun/csl-atlas/blob/main/data/parse-rules/pwg.json),
> validated by [`validate_pwg_markup.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_pwg_markup.py)
> (122,730/123,366 pass with the corrected 39-tag vocabulary, 0 unclassified). — csl-orig (pwg) / csl-atlas · 20-07-2026 · Sonnet 5 (`claude-sonnet-5`)

### §453. PWG's sense-closing glyph "〉" nests FOUR enumeration tiers, not two — Greek letters and roman-numeral markers are unrecognised by the RU pipeline's splitter

_↩ **Renumbered §449 → §453** (H1362, 20-07-2026): H1350×H1361 §448–451 collision; the H1361 movers keep the numbers per the [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) §6._

🟠 **PWG nests a real four-tier sense enumeration (digit → Latin letter → Greek letter → roman-numeral-like marker), but `microstructure.py`'s `MARK` regex only recognises the first two.**
Evidence: `validate_pwg_markup.py`'s full-corpus pass found 393 records where a `〉` glyph is
immediately preceded by a character the splitter's `MARK` regex (`(\d{1,2}|[a-z])[)〉]`,
fixed for the ASCII/`〉` distinction by H879/§447) does not match: Greek lowercase letters
(α β γ δ ε ζ η θ ι κ λ μ ν ξ ο — 1,444 occurrences corpus-wide) and single uppercase
roman-numeral-like markers (I/V/U, 30 occurrences) — e.g. `1〉` → `a〉` → `α〉` as a genuine
three-deep nested nesting, invisible to the existing splitter. Extending the glyph pattern to
`([0-9]{1,3}|[a-z]|[α-ωϑϰ]|[IVU])[)〉]` cleared all 393 to a clean parse.
Implication: `microstructure.py` (the live RU translation pipeline's sense-tree parser) still
under-splits these ~1,474 occurrences today — the same class of bug §447 fixed for the
ASCII/`〉` case, one enumeration tier deeper. Not yet applied to the production parser (a
Wave-2 change, since it would alter real sense segmentation for existing RU-store rows).

> **Source:** H1350 step W1.2 — [`validate_pwg_markup.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_pwg_markup.py)
> full-corpus run · glyph pattern verified in
> [`pwg_markup.rnc`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_markup.rnc). — csl-orig (pwg) / RussianTranslation · 20-07-2026 · Sonnet 5 (`claude-sonnet-5`)

### §454. The pwg_ru RU store's `h` field has inconsistent semantics — not a reliable homograph-number join key

_↩ **Renumbered §450 → §454** (H1362, 20-07-2026): H1350×H1361 §448–451 collision; the H1361 movers keep the numbers per the [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) §6._

🟠 **`pwg_ru_translated.jsonl`'s `h` field holds a bare homograph digit for some rows, an empty string for others, and a ROOT-WORD STRING (e.g. `"gam"`, `"han"`) for others — mixed within the same file.**
Evidence: live inspection of the first 20,000 store rows found `h` values including `"1"`,
`"3"`, `""`, and root strings like `gam`/`han`/`vid`/`vah`/`dhā` — three incompatible shapes
for what the field name implies is a single homograph-number column.
Implication: any join keyed on `(key1, h)` (as a homograph-number pair) silently fails —
`audit_sense_glyph.py`'s W1.4 pass originally assumed this join and got 0 matches on a
2,500-record test slice before the bug was found; the audit now joins on `key1` alone
(coarser, conservative-over-precise). A row-level join (exact `sense_tag`) needs the store's
upstream pipeline stage that assigns `sense_tag`/`h` reverse-engineered first — not done here.

> **Source:** H1350 step W1.4 — [`audit_sense_glyph.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_sense_glyph.py)
> · full-corpus run found 93.78% of RU-store rows (10,881/11,603, spanning 49/254 unique
> key1) touch a headword whose corrected-vs-old `〉` segmentation changed sense count — the
> row-rate is high because the affected headwords are disproportionately DCS-attested verb
> roots, which carry far more store rows each than an average nominal headword (19.29% of
> unique key1 affected vs. 93.78% of rows). Store confirmed byte-identical before/after
> (sha256 unchanged, read-only throughout, FINDINGS §9); quarantine side file only, no
> requeue. — RussianTranslation (pwg_ru) · 20-07-2026 · Sonnet 5 (`claude-sonnet-5`)

### §455. PWG `<ls>` citation resolution is already at 98%+, far above the previously-cited 72.4% baseline

_↩ **Renumbered §451 → §455** (H1362, 20-07-2026): H1350×H1361 §448–451 collision; the H1361 movers keep the numbers per the [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) §6._

🟡 **`pwg_sources.py`'s pwgbib-backed resolver already resolves 98.2% of `<ls>` citations (85.1% of distinct source keys) against the current `pwgbib.txt` (4,390 entries) — well above the 72.4% baseline cited in earlier planning docs (FINDINGS §20).**
Evidence: `pwg_sources.py coverage` run 20-07-2026: 572,546 citations, 4,042 distinct source
keys, 562,468/572,546 citations resolved (98.2%). A deterministic extension recognising
`ebend[a].` ("ebenda"/German "ibid.", 2,214 citations) as a same-as-previous-citation marker
rather than an unresolved source pushed this to 98.6%. `pwgbib.txt` was evidently extended
substantially since whatever measurement produced 72.4% — the two numbers describe different
points in time, not a discrepancy in either measurement.
Implication: don't cite 72.4% as PWG's current citation-coverage ceiling in future planning;
re-measure with `pwg_sources.py coverage` first. The residual 599 keys / 7,864 citations are
dominated by malformed multi-part continuation fragments (bare roman numerals, `(I)`/`(II)`
volume markers) that need a human bibliographer, not a smarter regex.

> **Source:** H1350 step W1.6 — [`extend_ls_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/extend_ls_coverage.py)
> · [`pwg_ls_unresolved.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pwg_ls_unresolved.tsv). — RussianTranslation (pwg_ru) · 20-07-2026 · Sonnet 5 (`claude-sonnet-5`)

### §583. "How many senses does this PWG lemma have?" is undefined until you fix the layer — the naive count runs 10–40× high

🔴 **Counting distinct `sense_tag` per `key1` in the pwg_ru store does not count senses.**
Three defects compound, and each is invisible on its own:

1. **The store spans five dictionary layers** — `pwg` 5,594 rows, `pw` 5,205, `nws` 432,
   `sch` 210, `pwkvn` 162 (of 11,603), and **97 of 254 lemmas straddle more than one**.
   A cross-layer count conflates "PWG sense 2" with "the same word as printed in PW".
2. **Many tags are not senses.** Inside `pwg` alone the tag vocabulary carries structural
   apparatus (`main`, `intro`, `head`, `tail`, `header`, `note`, `addendum`, `cross-ref`,
   `Nachtrag`) and derived-stem slots (`caus`, `desid`, `caus-1`, `*_verb`).
3. **Tags are not normalized** — `1` and `1)` are stored as distinct tags, inflating 23
   lemmas by pure punctuation.

Measured, the same lemma under three definitions:

| lemma | rows | all-layer tags | `pwg` tags | `pwg` numeric senses |
|---|---:|---:|---:|---:|
| `han` | 597 | 430 | 90 | **11** |
| `gam` | 673 | 410 | 69 | **8** |
| `viś` | 537 | 397 | 96 | **14** |
| store max | | 430 | 96 | **16** (`vah`) |

Implication: the naive count says PWG polysemy is **bimodal**, with a tail of 300–430-sense
verb roots too large for any human to choose among — which drives real design decisions
(H3172's first cut built a separate free-gloss annotation tier for that tail, with an
unavoidable shortlist-bias problem, because the tail looked unavoidable). **The tail is an
artifact.** Under "numbered sense within one layer" the store-wide maximum is 16 and every
PWG lemma is hand-checkable. A second trap rides along: cross-layer duplicate subcards
produce menu options that are *textually identical* (`[1] раздувание, вздутие` vs
`[PW] раздувание, вздутие`), which is unanswerable rather than merely redundant — two
annotators pick at random and the resulting κ measures coin-flips. Any card reasoning about
PWG polysemy, sense inventories, or MFS chance level must state its layer and tag class
first; `distinct sense_tag` alone is not a sense count.

> **Source:** H3172 — [`probe_wsd_strata.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/probe_wsd_strata.py)
> §"What counts as a sense" · protocol [WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md)
> §2–§3. — RussianTranslation (pwg_ru) · 25-08-2026 · Opus 5 (`claude-opus-5`)

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

> **Source:** [`cross_dict_agreement.csv`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/cross_dict_agreement.csv)
> + [PAPER_DRAFT.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/PAPER_DRAFT.md)
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

> **Source:** [`nearest_root_audit.json`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/nearest_root_audit.json)
> + [`build_root_normalization.py`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/build_root_normalization.py) — csl-orig · 2026-06-26

## Encoding & normalization

### §36. IAST Unicode collides and normalises lossily

🔴 **IAST Unicode collides and lossily normalises if you're naïve.**
Evidence: `ś` = `s` + U+0301 (combining acute), which collides with a pitch-accent mark;
NFD-decompose-then-strip-Mn destroys vowel length (`ā`→`a`) and retroflex dots (`ṣ`→`s`).
Implication: use a length-preserving `form_key`, not a blanket NFD+strip-combining.

> **Source:** [`form_key` in sanskrit_util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py). — sanskrit-util / shared · 2026-06

### §100. `nfold` earns sandhi-tolerant recall by fusing every nasal to `n` — which manufactures false quotation matches unless every hit is re-verified on `norm`

🔴 **`sanskrit_util.nfold` maps *every* nasal to `n`, stem-internally as well as at sandhi
boundaries. That is exactly what makes it useful for corpus matching, and exactly what makes
it unsafe as the key a verdict rests on.**

Evidence (H1212, matching Bühler's exercise sentences against DCS 2026): `nfold` folds
Bühler's `janānāṃ dhanaṃ` and the unrelated corpus string `yājamānaṃ dhānaṃjayyaḥ` close
enough to register as a shared contiguous run. Re-verifying the same run on `norm` (which is
diacritic-insensitive but keeps `m`/`n` distinct) removes it, along with its whole class:
the `adapted` bucket fell from 28 rows to 16 — **43 % of that bucket was nasal-folding
artefact**.

Implication: use `nfold` for *recall* (generating candidates, absorbing anusvāra/ṃ/m/n
sandhi variation that would otherwise hide a real quotation), then require every surviving
candidate to match on `norm` before it counts as evidence. Two keys, two jobs. A pipeline
that rules on `nfold` alone will report inflated attestation and will not look obviously
wrong — the false hits are individually plausible.

Related trap from the same pass, not specific to Sanskrit: **token-overlap scoring without
an adjacency requirement is not evidence of quotation.** IDF-weighted containment scored
`adya jīvāmaḥ` ("today we live") at 0.64 because both its tokens occur, scattered and
unrelated, somewhere in a long Aṣṭāṅgahṛdaya sentence. Requiring a contiguous run instead
halved that bucket again (56→28). For short sentences over a large corpus, co-occurrence of
common vocabulary is the null hypothesis, not the signal.

> **Source:** [`scripts/buhler_provenance.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/scripts/buhler_provenance.py)
> + [`BUHLER_SENTENCE_PROVENANCE_ADJUDICATION.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/BUHLER_SENTENCE_PROVENANCE_ADJUDICATION.md)
> — SanskritGrammar / H1212, Opus 4.8 (`claude-opus-4-8`) · 2026-07

### §102. DCS `sentence.text_sandhied` is not reliably sandhied — some rows store analyzed word forms, which silently downgrades verbatim quotations to partial matches

🔴 **The DCS column named `text_sandhied` does not always hold the sandhied surface text.
Some rows hold word-segmented, partly *un*-sandhied forms — so matching printed text
against it under-reports verbatim quotation.**

Evidence (H1344): Bühler's exercise `ācārādvicyuto vipro na vedaphalamaśnute` is a verbatim
Manusmṛti quotation. DCS stores that line as
`ācārāt vicyutaḥ vipraḥ na veda phalam aśnute` — `vicyutaḥ` not `vicyuto`, `vipraḥ` not
`vipro`, `vedaphalam` split as `veda phalam`. Matched against DCS alone it scored as a
*partial* run (verdict `invented`); matched against GRETIL's true surface text
`ācārād vicyuto vipro na vedaphalam aśnute` it is an exact hit. The verdict crossed two
buckets purely on which corpus held the same verse.

Implication: whitespace-insensitive matching is not enough — the *segmental* forms differ,
not just the word boundaries. A pipeline that treats `text_sandhied` as the printed surface
will systematically under-count quotation. Cross-check against a corpus that stores real
surface text (GRETIL plaintext) before reporting an attestation rate as final. Distinct from
§36: nothing is lost in normalization here — DCS's stored string is simply a different
string from the printed one.

**Second, transferable trap from the same pass — grammatical metalanguage collides with
commentarial metalanguage.** A sentence whose *purpose* is to display a grammatical pattern
will match any text that uses that pattern, and that is not evidence of a source. Bühler's
bahuvrīhi drill `udgataṃ mukhaṃ yasya saḥ` matched the Mugdhāvabodhinī's
`dṛḍhaṃ mukhaṃ yasyāḥ sā`: both are the standard *vigraha* formula `X mukhaṃ yasya saḥ`,
which recurs throughout commentary because it *is* the analytical formula. No similarity
threshold fixes this — it is a category error about what the string is, and the only remedy
is to classify metalanguage out of the input before matching.

> **Source:** [`scripts/buhler_provenance.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/scripts/buhler_provenance.py)
> + [`BUHLER_SENTENCE_PROVENANCE_ADJUDICATION.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/BUHLER_SENTENCE_PROVENANCE_ADJUDICATION.md)
> — SanskritGrammar / H1344, Opus 4.8 (`claude-opus-4-8`) · 2026-07

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

> **Source:** [csl-corrections `.ai_state.md`](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/.ai_state.md)
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
> [csl-orig/LICENSE](https://github.com/sanskrit-lexicon/csl-orig/blob/main/LICENSE) —
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

### §448. CORRECTED — the MWScan/2020 `servepdf.php` endpoint is RIGHT (serves 1899); the 1872 first-edition scan coexists on the portal with colliding page numbers

_↩ **Renumbered from §80 → §448** (H1361, 20-07-2026): the DCS `text_sandhied` finding (§80, H759) published first (12-07-2026) and keeps §80. Per the [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md)._

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
[`csl-orig/v02/gra/gra.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/gra/gra.txt)**
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

_⚠️ **Class D — not reproducible as stated** ([H1362 verifiability ruling](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md)): hand-transcribed telemetry over a local-only ledger that swaps its own denominator — no committed artifact re-derives the code-vs-infra split. Cite the lesson, not the number._

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

_⚠️ **Class D — not reproducible as stated** ([H1362 verifiability ruling](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md)): the promotable-subset claim rests on an audit/execution contract that FAILED; the clean-looking subset is not recoverable as evidence. Cite the lesson, not the subset._

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
errors, and latency strictly below 30 seconds. A Workflow session cannot prove its config directory
or participate in the host claim, so profile-bound v2 production is CLI/headless-only; a bound
Workflow template must abort before its first agent call rather than mislabel its billing route.

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

### §449. Samāsa-type frequency does not exist in any org corpus — and the grammarians' canonical examples are corpus-ghosts (8/58 attested, max freq 147)

_↩ **Renumbered from §86 → §449** (H1361, 20-07-2026): the DCS verbal-feature-density finding (§86, H1000) is the one the inbound §86 citation names and keeps §86. Per the [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md)._

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

### §450. The roadmap's "OBS-T κ=0.42" was a phantom figure — no measured agreement exists for any OBS-T axis

_⚠️ **Class D — not reproducible as stated** ([H1362 verifiability ruling](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md)): the κ=0.42 was never measured — no agreement computation exists to re-run. The finding's value is the phantom itself, not the figure._

_↩ **Renumbered from §87 → §450** (H1361, 20-07-2026): the DCS text→period-map finding (§87, H1000) published first (16-07-2026), is the cited one, and keeps §87. Per the [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md)._

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

**Consequence — fixed 17-07-2026** ([H1086](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1086-Sonnet_csl-atlas_mw-row-regenerate-ls-shapes_17.07.26.md),
Sonnet 5 `claude-sonnet-5`). [csl-atlas' `data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json)
MW row carried (1) and (2) — its extractor was literal at
[`parse_cslorig.py:41`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/parse_cslorig.py#L41)
(now `<ls(?:\s+n="([^"]*)")?\s*>(.*?)</ls>`, `[^"]*` not `[^>]*` so an embedded literal `>` in one
malformed mw.txt line — `<ls n=">Dhātup. iii,">4</ls>` — doesn't truncate the match), and its
locator rule at `citation_register_gaps.py:49` was arabic-digit-only (now arabic OR lowercase
roman, case-sensitive). Regenerated MW row: **ls=320,828** (exact match) / **lsWithLocator=60,822**
(18.96%, exact match to 2dp) — 2 citations off the MWS `register_census.py` "attested" count of
60,820 by design: `L. i` and `W. 1` carry an incidental locator-shaped token but MWS's stratification
excludes them (siglum ∈ MW-specific HEDGE/AUTHORITY sets `{L.}`/`{W., MW., Cat.}`). Baking those
MW-only sigla into csl-atlas' generic 44-dict rule would be exactly the kind of dictionary-specific
overfit this defect class warns against — A08's `lsWithLocator` is deliberately "any locator token
present" (an upper bound on resolvability), not MWS's stricter "genuinely a textual attestation".
This is corpus-wide, not MW-only, and PWG (the largest `<ls>` citer) moved the most: 568,730 → 801,788
(+41%), which shifts the corpus aggregate materially (~59%/41% locator split → ~67%/33%). csl-atlas
PR: see `docs/CITATION_REGISTERS.md` for the full before/after table. The atlas's direction and
corpus-wide conclusion are **not** in dispute; MW stays a locator-poor Register-A dictionary.

### §90. A spelling-keyed join onto Whitney's roots union-smears homonyms — one authorial entry lands on every homonym of that spelling, and the rows still read `authorial`

**Measured 17-07-2026** (Opus 4.8 `claude-opus-4-8`, [H1065](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1065-Opus_WhitneyRoots_alternation-type-induction-nonpaninian_16.07.26.md);
[WhitneyRoots PR #44](https://github.com/gasyoun/WhitneyRoots/pull/44), SanskritGrammar
[#348](https://github.com/gasyoun/SanskritGrammar/pull/348) · [#352](https://github.com/gasyoun/SanskritGrammar/pull/352) ·
[#353](https://github.com/gasyoun/SanskritGrammar/pull/353) · [#354](https://github.com/gasyoun/SanskritGrammar/pull/354)).
Third independent instance of the failure class [§3](#3-the-warnemyr-scrape-union-smears-homonym-classes)
already names — **a join keyed on the citation spelling cannot see Whitney's homonym numbering** — this
time smearing an *author's own* classification rather than a scrape's:

1. **Unique-spelling ≠ unique root.** Tolchelnikov's Приложение 1 indexes his entries against Whitney
   («`2 iṣ`», «`1 stu`»). An ingest that binds whenever the *spelling* matches exactly one catalog entry
   ignores that index, so **one entry lands on every homonym Whitney spells the same way**: his «2 iṣ»
   was asserted of `iṣ¹` **and** `iṣ²`; his single «1 śṛ» of `śṛ¹`, `śṛ²` **and** `śṛ³`. In
   `alternation_type.csv` v1.5.0: **15 entries → 31 records, 16 excess assertions**, each carrying
   `derivation_method=talmud_appendix1`, `grade_confidence=authorial`. Frequency-weighted it bites the
   common roots — `paś` (DCS rank 24), `pat` (38), `stu` (62), `vṛ` (65), `rudh` (184), `tan` (229).
2. **The un-indexed case smears too, and is easy to miss.** Where the author gives *no* index («`vakṣ, ukṣ`»)
   there is no number to contradict — so a homonym guard written only against the indexed case still binds
   both `ukṣ¹` and `ukṣ²`. This bug survived one round of *this* work's own homonym guard and was caught
   only by auditing the output for one-entry→many-homonym bindings. ⇒ the abstention rule must be
   *unique-resolution*, not *non-contradiction*: bind only when the spelling resolves to a single record
   (or a single homonym-less one).
3. **The legitimate multi-spelling case looks identical and must NOT be suppressed.** The same catalog
   row genuinely cross-references *several distinct citation forms* — «gam, gach», «yam, yach», «1 i, ī, ay»
   — because col4 is the author's own concordance (his [issue #50](https://github.com/gasyoun/SanskritGrammar/issues/50)
   ruling). **49 entries** are of this kind and are authorial data, not inference; the mirror-image bug is
   dropping them, which left **57 roots** — `gach`, **DCS rank 5** — with no Тип at all. The test that
   separates the two: *same spelling → several homonyms* = smear; *several spellings → one morpheme* = concordance.

**Consequence.** Two independent joins over the same two files disagreed by exactly this defect (789 vs 794),
with **0 tip-value disagreements** — the divergence was entirely *which roots may be spoken for*, which is
why value-level diffing would have shown nothing. Resolved by one canonical join
([`whitney_talmud.json`](https://github.com/gasyoun/SanskritGrammar/blob/main/TolchelnikovTalmud_2026/data/whitney_talmud.json))
that abstains on homonym divergence and emits its own audit trail (`talmud_root`/`talmud_ref`/`talmud_match`),
with the downstream feed **reading** it instead of repeating it. Final: **787/930 classified, 0 smears**;
**19 roots are Whitney-vs-author homonym divergences parked for the author's ruling** (`pā³` vs his `pā¹`/`pā²`)
— an editorial-numbering question no induction can settle. The exception rate was **10.5% before and after**,
so the paper-level finding never depended on the defect: **only the per-root provenance did, and a
provenance-only defect is invisible to aggregate checks.** ⇒ when a derived asset claims `authorial`, audit
*one-source-entry→many-target-rows* explicitly; a correct aggregate is not evidence the binding is sound.

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

---

### §91. DCS has no aorist TENSE value — `feat_tense='Past'` lumps aorist with the perfect; `feat_formation` is what actually separates them

Querying the DCS sqlite for aorist forms by `feat_tense` alone is a dead end: the aorist has no
tense code of its own and is folded into `feat_tense='Past'` together with the perfect, so a
naive tense filter either returns nothing or returns perfect forms mislabeled as aorist. An
earlier form-set matching approach (a fixed list of known aorist forms) undercounted badly —
e.g. zero hits for a text where Whitney's grammar records the aorist as attested.

The reusable key: **within `feat_tense='Past'`, `feat_formation` cleanly splits the seven aorist
classes from the perfect** —
`feat_formation IN {root, them, s, is, red, sa, sis}` = aorist (root 5,690 · thematic 2,781 ·
s 1,508 · iṣ 1,077 · reduplicated 833 · sa 124 · siṣ 41 = 12,054 finite tokens), vs.
`peri` (periphrastic perfect, 4,046) and `None` (reduplicated perfect, 85,955) = not aorist. This
raises the measured aorist frequency to **12,054 tokens / 1.2% of verbal forms** — about 5× the
2,452 / 0.31% the older form-set method produced, because that method had missed the two largest
classes (root and thematic aorists) entirely. The "classically infrequent" verdict for the aorist
still holds either way, but any prior corpus count derived from the form-set/tense-code method
should be treated as a ~5× undercount, not a ground truth.

> **Source:** SanskritGrammar Whitney-register drain, `whitney_aorist_tagger.py`
> ([PR #357](https://github.com/gasyoun/SanskritGrammar/pull/357),
> [`WhitneyGrammar_1889/whitney_aorist_tagger.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/WhitneyGrammar_1889/whitney_aorist_tagger.py)) ·
> [H1134](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1134-Opus_SanskritGrammar_whitney-aorist-per-text-tagger_17.07.26.md) ·
> 17-07-2026, Opus 4.8 (`claude-opus-4-8[1m]`).

---

### §92. A verified claim register is not Whitney-proof — 3 of 229 verdict_fact: TRUE rows in Kochergina claims.yml contradict Whitney, and ~65 of the register/article §-refs point at the wrong section

The H1228 concordance audit adjudicated **all 432 grammatical claims** of the SanskritGrammar
corpus sources against the actual text of Whitney 1889 (172 claims from 33 live Sangram
articles + all 260 entries of KocherginaUchebnik_1998/claims.yml): **364 AGREE / 42 DISAGREE /
26 WHITNEY-SILENT**. The non-obvious part is where the DISAGREEs sit: three register rows that
already carried verdict_fact: TRUE from the corpus-verification passes are contradicted by
Whitney on the systemic-fact axis — HK-31 (one-final-consonant phonotactics vs §150b urk/suhart,
radical mute retained after r), HK-35 (samahara-dvandva «always plural» vs §1253.2d neuter
singular), HK-174 (feminine of athematic present participles on the strong stem kurvanti vs
§449h–i weak stem only). Corpus-TRUE and Whitney-TRUE are different axes: a claim can match
DCS frequency reality and still misstate the grammar. Side catch of the same pass: ~65 §-refs
in the register and articles were wrong or imprecise (wrong chapter, wrong sub-letter,
neighboring-§ drift), and 7 §-anchors are missing/OCR-corrupted in the WhitneyGrammar_1889
mdx itself (§218, §235, §339, §378, §387, §465, §1053) — grep-by-anchor alone silently
misses those sections; verify by passage content.

> **Source:** [WHITNEY_CONCORDANCE_SANGRAM_KOCHERGINA_2026.md](https://github.com/gasyoun/SanskritGrammar/blob/main/WHITNEY_CONCORDANCE_SANGRAM_KOCHERGINA_2026.md)
> (fix queue § 3, digitization defects § 6; [PR #408](https://github.com/gasyoun/SanskritGrammar/pull/408),
> [v0.77.0](https://github.com/gasyoun/SanskritGrammar/releases/tag/v0.77.0)) ·
> [H1228](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1228-Fable_SanskritGrammar_whitney-concordance-audit-sangram-kochergina_18.07.26.md) ·
> 18-07-2026, Fable 5 (claude-fable-5).

### §93. Declared, validated, and never enforced — the PWG headless executor read a manifest `budgets{}` block it did not obey, and every offline gate stayed green

A spend bound that is *declared* in a manifest and *validated* at load can still be
**enforced nowhere on the live call path** — and no amount of green selftests will say so,
because the selftests exercise the declaration and the validation, not the spawn site. The
H1110 post-H1080 audit's headline finding was exactly this: the PWG→RU headless executor
parsed and validated the manifest's `budgets{}` block, then spawned model calls without ever
checking a per-lane or total agent budget against it. The money-risk guardrail existed as
text in a file that the code read and ignored.

What surfaced it was not a test but a **three-column execution-route parity table** — for
every manifest field, *where it is declared* · *where it is validated* · *where it is
actually enforced* — across 17 fields of the real call graph. Two columns populated and a
blank third is the whole defect class, and it is invisible to any check that never asks the
third question. The same sweep found the CLI timeout able to exceed the manifest's own
`timeout_ceil_ms=180000`, wrapper usage/cost telemetry discarded (so cost was silently
*unevaluable* rather than over-budget), and manifest validation comparing key **sets**, which
admits duplicate selected keys. All were declared-and-unenforced, none had a failing test.

Generalisation for any pipeline with a spend/timeout/quota bound: **grep for the enforcement
site, not the config key.** A bound whose only appearances are the schema and the loader is
decorative. Reconciling 59 prior findings against changed code needs the same discipline —
of the 59, only 8 were `fixed` and 38 still `open` once each was re-executed rather than
re-read, and 2 were outright `refuted`; a finding's age is not evidence of its status.

> **Source:** [H1110_POST_H1080_AUDIT_MEMO_2026-07-17.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1110/H1110_POST_H1080_AUDIT_MEMO_2026-07-17.md)
> § 4 (parity table, 17 fields) + § 5 (C-01…C-59 ledger) · audit [PR #524](https://github.com/gasyoun/SanskritLexicography/pull/524) ·
> enforcement landed in [PR #530](https://github.com/gasyoun/SanskritLexicography/pull/530) ·
> [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) ·
> 18-07-2026, Opus 4.8 (`claude-opus-4-8`).

### §94. kosha's generated `forms` is 93% DCS-derived, so its attested-form join is a round-trip — only the vidyut-engine subtotal (12.4% attested) carries signal, and A¬G cannot measure engine gaps

**Measured 18-07-2026** (Opus 4.8 `claude-opus-4-8`, H1262, A3 / Concordance-Q3 W1b): joining
kosha.db `forms` (non-heritage: 426,410 rows) against DCS attested **surface** forms
(`dcs_full.sqlite token.form`; 381,413 distinct) on `form_key()` equality — the length-preserving
floor tier — gives AG 401,368 / G¬A 25,042 / **A¬G 2**. The AG looks like 94% coverage, but
**93.30% of the non-heritage generated side is itself `source='dcs'`** (ingested DCS surface tokens,
several still carrying `''`-avagraha sandhi markers), so its AG is a **99.99% round-trip**. The only
research-meaningful subtotal is the **vidyut**-engine one: AG 3,550 / 28,567 = **12.43% attested**,
25,017 over-generated. Two consequences no downstream wave may forget: (1) any "coverage" headline
over the full generated side is circular — always split AG by generated-side `source` and quote
vidyut, never the total; (2) **A¬G is degenerate (=2: `oṃ` plus one German OCR token) and CANNOT
measure engine gaps from this join**, because the DCS-derived generated forms blanket the attested
surface set — reported as the finding, not hidden (0 genuine engine gaps, nothing routed to the
csl-inflect give-back H185). `tense_caveat` follows [§91](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
(DCS `Past` lumps aorist + perfect): 16,339 AG rows carry a `Past` attestation. The
`forms`-vs-`inflections` generated-side table ambiguity was logged separately in
[CONTRADICTIONS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
and is now **✅ ruled (H1366, 20-07-2026, accepted by MG): `forms` is canonical** for
the A3→A4/W2a pipeline — the two tables share only 168,034 of 426,410 non-heritage
`(form, lemma)` pairs (different data products, not two counts of one; `inflections`
is a distinct single-engine `cologne_mwinflect` paradigm asset, an optional
cross-check). Recorded as
[kosha PLAN D13](https://github.com/gasyoun/kosha/blob/main/docs/PLAN_KOSHA_CONCORDANCE_Q3_2026H2.md).

> **Source:** [morphology-attestation build report](https://github.com/gasyoun/kosha/blob/main/data/concordance/MORPHOLOGY_ATTESTATION_BUILD_REPORT.md)
> + manifest row `morphology-attestation-audit` ([datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)) ·
> [H1262](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1262-Opus_kosha_a3_attested_form_join_morphology_audit_18.07.26.md) ·
> [kosha](https://github.com/gasyoun/kosha) · 18-07-2026, Opus 4.8 (`claude-opus-4-8`).

### §95. DharmaMitra `unsandhied` batches return MISALIGNED results on short inputs — doubled echoes and other texts' tokens — so every consumer must validate by surface reconstruction before display

Building the H1279 beginner subhāṣita pack, per-chunk batched calls to the DharmaMitra
tagging API (`mode: unsandhied`, batch 32 — the same contract as kosha
`compare_sandhi_methods._dm_segment` and csl-atlas `dharmamitra_infer.py`) returned
**garbage for a substantial share of short inputs**: single words echoed doubled
(`ca` → `ca_ca`, `gavā` → `gavā_gavā`), tokens from *some other batch item* (`dadāti` →
a 20-token segmentation of a different text), non-IAST junk (`na` → `R̤`), and tokens
containing spaces — the classic batch-misalignment signature, not a modelling error.
On full sentences (the H903/H908 method-C runs) this was never observed; the failure
mode is specific to **short, context-free batch items**. Consequence for any DM consumer:
**never trust a batched segmentation without a mechanical validity gate.** The gate that
worked: a segmentation is accepted only if it (a) is IAST-charset-clean, (b) contains no
1-char morphology shavings, and (c) **rebuilds its own surface** via corpus-attested
junction rules / bare joins (DFS with pausa tail-drift tolerance) — everything else falls
back to offline vidyut-cheda under the same gate, else displays honestly unsplit
(56/1,263 chunks in the shipped pack). Poisoned entries persist in the response cache, so
add the gate at READ time, not just at query time.

> **Source:** [build_subhashita_pack.py](https://github.com/gasyoun/kosha/blob/main/scripts/build_subhashita_pack.py)
> (`accept_seg` / `label_internal_seams`) + the committed cache
> [dharmamitra_indische_sprueche.json](https://github.com/gasyoun/kosha/blob/main/data/sandhi/_cache/dharmamitra_indische_sprueche.json) ·
> [H1279](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1279-Fable_kosha_pedagogy-wave-ru-subhashita-reader_19.07.26.md) ·
> [kosha](https://github.com/gasyoun/kosha) · 19-07-2026, Fable 5 (`claude-fable-5`).

---

### §96. SamudraManthanam's generated full-corpus JSONL has 38,288 duplicate canonical-ID groups, concentrated in `devibhagavata-purana`

The 19-07-2026 audit-hardening pass ran SamudraManthanam's manual corpus gate against the
existing local corpus (668 tests collected; 66 corpus tests selected; 708.2 MiB `DB_PATH`).
After 15 corpus checks passed, `test_gate4_all_ids_unique` stopped the run with
`Duplicate IDs found (38288 groups)`. These are **duplicate groups**, not a count of duplicate
rows, and the observed IDs were concentrated in the generated `devibhagavata-purana` records.
The gate loads every record from the locally generated `web/corpus_builder/jsonl/*.jsonl`; this
is therefore a canonical-JSONL defect, not evidence about the SQLite search index and not a
rights-policy finding.

**Reusable rule.** Do not report the full-corpus suite green merely because the hermetic tests
pass. Run the manual launcher with `USE_REAL_CORPUS=1`; preserve `--maxfail=1` so the first named
data invariant stays visible, and treat Gate 4 as release-blocking until the Devībhāgavata
converter/regeneration path produces globally unique IDs. Because this run stopped on the first
failure, later corpus gates remain unadjudicated rather than implicitly passing.

> **Source:** [`test_gate4_all_ids_unique`](https://github.com/gasyoun/SamudraManthanam/blob/codex/audit-hardening/web/tests/test_converter.py#L294-L304) +
> [manual corpus launcher](https://github.com/gasyoun/SamudraManthanam/blob/codex/audit-hardening/web/scripts/run_corpus_tests.py) ·
> [SamudraManthanam PR #85](https://github.com/gasyoun/SamudraManthanam/pull/85) ·
> 19-07-2026, Codex GPT-5.

### §97. Cross-dictionary attestation via Monier-Williams overstates independence — MW was compiled *from* Böhtlingk-Roth (PW/PWG), so an MW-only hit is not evidence a PW/PWG word is independently text-attested

H1310 audited PWG's 32,690 lexicon-only headwords (attested only in koṣas per PWG's own
`<ls>` citations) against the other Cologne `csl-orig` digitisations by exact SLP1 `<k1>`
set membership. The naïve join says **91.5 % appear in some text-based dictionary** — but
**28,935 of those hits are Monier-Williams, and MW was compiled substantially FROM the
Petersburg Dictionary itself** (a standard lexicographic fact). Counting an MW hit as
independent text-attestation double-counts the same source: MW may simply have copied the word
from PW.

Separating MW into its own tier collapses the picture honestly: of 31,925 distinct lexicon-only
words, only **7,331 (23.0 %)** appear in a genuinely independent text dictionary (Apte,
Grassmann's RV, Edgerton's BHS); **21,874 (68.5 %)** are mw-only (weak); 101 kosa-only; and
**2,619 (8.2 %) appear in no other digitised dictionary at all** — of which 974 are absent from
even Böhtlingk's own kürzere Fassung (`pw`), the same-source abridgment that likewise cannot
corroborate independence.

**Reusable rule.** When measuring whether a word from dictionary X is attested "elsewhere", first
exclude every other dictionary that was *derived from* X. For the Petersburg family the derived
set is at least MW (⊃ PW) and PWK/`pw` (Böhtlingk's own abridgment); independent evidence is the
corpus-based dictionaries (Apte, Grassmann, Edgerton) and non-PW koṣa digitisations. Exact SLP1
match is a **lower bound on attestation** (variant spelling/accent misses a real hit), so treat
the pwg-unique set as candidates, not confirmed ghost-words.

**Update (v2, [SanskritGrammar PR #450](https://github.com/gasyoun/SanskritGrammar/pull/450), supersedes #447).**
The independence rule above stands, but v1's comparison corpus was too thin (koṣa side =
`skd` alone) and treated MW as an undifferentiated block. v2 adds two corrections, both of
which sharpen — not overturn — the finding:
- **Split MW's `L.` marker, don't just tier MW out.** `<ls>L.</ls>` ("lexicographers") is
  MW's own flag for a koṣa-sourced sense with no text citation — **59,697 of MW's 194,084
  headwords (30.8 %) are `L.`-only.** So genuine text attestation = a MW **non-`L.`** `<ls>`,
  not bare MW membership.
- **Join against the koṣas themselves** (7: armh/abch/acph/acsj/nmmb/vcp/skd), so "koṣa-
  corroborated" becomes measurable (10,724) rather than the near-empty `skd`-only tier (101).
- Of 32,690 lexicon-only entries: text-attested 12,606 (38.6 %) · koṣa-corroborated 10,724 ·
  dict-lexical 7,062 · **pwg-unique 2,298** (1,510 only in same-source PW; **788 absent from
  every dictionary**, ≈715 after normalisation).
- **New substantive result:** hand-adjudication + a source-token breakdown of the 2,298
  pwg-uniques shows a genuine OCR/segmentation-artifact rate of **≈0.05 %** — the rest trace to
  **koṣas/nighaṇṭus PWG cites but that are not digitised** (Rājanighaṇṭu, Trikāṇḍaśeṣa, Amara,
  Nighaṇṭu, Ratnamālā — 678 words), MS-catalogue proper nouns (*Verz. d. B. H.*, 768), and
  scholarly/technical terms (834). **Most PWG "ghost-words" are corpus gaps, not ghosts** — the
  highest-value next step is digitising those koṣas, not re-deriving the flag.

> **Source (v2):** [`data/pwg_lexicon_only_audit/build_census.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/data/pwg_lexicon_only_audit/build_census.py) +
> [`data/pwg_lexicon_only_audit/`](https://github.com/gasyoun/SanskritGrammar/tree/main/data/pwg_lexicon_only_audit)
> (README + `pwg_lexicon_only_audit.meta.md`) ·
> [SanskritGrammar PR #450](https://github.com/gasyoun/SanskritGrammar/pull/450) (supersedes
> [#447](https://github.com/gasyoun/SanskritGrammar/pull/447)) · H1310 · 19-07-2026,
> Opus 4.8 (`claude-opus-4-8[1m]`).

**Update (v3, [SanskritGrammar PR #459](https://github.com/gasyoun/SanskritGrammar/pull/459),
H1326).** v2 flagged Amara/Rājanighaṇṭu/Trikāṇḍaśeṣa/Nighaṇṭu/Ratnamālā/Hārāvalī as the
biggest remaining corpus-coverage gap. H1326 sourced **one** of these — Amarakośa (`amar`,
9,788 SLP1 headwords, GNU GPL v3.0, from [`sanskrit-kosha/kosha`](https://github.com/sanskrit-kosha/kosha)
— the same upstream project and `<syns>` annotation format already used for the existing
`abch`/`acph`/`acsj`/`nmmb` koṣas) — and joined it as an 8th koṣa:
- Of 32,690 lexicon-only entries: koṣa-corroborated **10,724 → 10,812** (+88), dict-lexical
  **7,062 → 6,978** (−84), pwg-unique **2,298 → 2,294** (−4), text-attested unchanged (12,606).
- **The gain is real but modest, and does not touch the hardest residue.** All 4
  newly-resolved pwg-uniques came from the "present only in same-source PW" fringe
  (1,510 → 1,506); the **788-word "absent from every dictionary" core is unchanged** — none
  of those 788 happen to be Amara-cited. Amara alone does not meaningfully shrink the hardest
  ghost-word residue, even though it is now methodologically joined rather than recorded as
  a gap.
- **Rājanighaṇṭu, Trikāṇḍaśeṣa, and generic Nighaṇṭu remain unsourced as bulk lemma-tagged
  data — a negative result worth recording.** A scan of all 126 reachable dictionaries in
  `sanskrit-kosha/kosha` found only 4 works have ever received `<syns>` synset annotation
  (the 3 already in `csl-orig` + Amara, now added); Trikāṇḍaśeṣa/Nighaṇṭuśeṣa/Hārāvalī/
  Medinīkośa exist there only as raw, unsegmented, sandhi-joined verse. The
  `cltk/sanskrit_text_dcs` mirror of Digital Corpus of Sanskrit raw texts has a
  `Rājanighaṇṭu.txt`, but it is a 232-byte fragment (opening invocation only); other
  nighaṇṭus mirrored there in fuller form (Dhanvantari-, Madanapāla-, Kaiyadeva-,
  Aṣṭāṅga-nighaṇṭu) are likewise raw unsegmented IAST verse. **Extracting individual
  headwords from raw metrical verse needs a real Sanskrit sandhi-segmenter, not a bulk
  download** — `sanskrit-kosha/kosha`'s own `<syns>` annotation is done by hand
  (`kosha_annotator.py` + `annotation_accuracy_log.txt`), confirming this is a genuine
  digitisation gap, not a licence or access issue.
- **Reusable rule:** when a "digitise dictionary X" backlog item names a specific work,
  check whether a *headword-tagged* (not just OCR'd/raw) digitisation exists before
  estimating effort — the `sanskrit-kosha/kosha` project holds ~140 kosa digitisations but
  has only manually lemma-annotated 5 of them; raw OCR of the other ~135 is not a substitute
  and cannot be bulk-converted without a real segmenter.

> **Source (v3):** [`data/pwg_lexicon_only_audit/kosa_extra/`](https://github.com/gasyoun/SanskritGrammar/tree/main/data/pwg_lexicon_only_audit/kosa_extra)
> (`amar.txt` + provenance/negative-result-audit `README.md`) ·
> [SanskritGrammar PR #459](https://github.com/gasyoun/SanskritGrammar/pull/459) · H1326 ·
> 19-07-2026, Sonnet 5 (`claude-sonnet-5`).

---

### §103. Quantified: the §83/§97 witness-collapse deflates the published 15-dict union "corroboration" from 55.9% to 34.7% — and the union's own table is pre-fold

🟠 §83 ruled that PWG, PW **and** MW collapse to ~one European witness, and §97 gave the
reusable rule (exclude every dictionary derived from X before calling a hit corroboration) —
but nothing downstream obeyed them: [UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)'s
"in N dicts" distribution over 323,425 headwords still treats all 15 dictionaries as
independent. Applying the ruling to those counts (a **witness-independence map** over the 15
dicts, then recomputing the distribution over independent *families*):

- **Corroborated share (≥2 independent witnesses) falls 55.9% → 34.7%** under the §83/§97
  ruling (P3, MW folded into the Petersburg witness): **68,651** headwords that look
  multiply-attested rest on a single European lineage. Intermediate rungs: CAE≡CCS same-work
  (P1) reclassifies 364; the documented Petersburg lineage PWG/PWK/SCH (P2) reclassifies
  8,934. The ≥5-witness "well-attested" tier more than halves (43,825 → 12,135).
- **Apte is NOT collapsed** — §83 names it the independent European control (gap-sensitivity
  1.5× vs MW 12.3×), so a rung folding AP would contradict the finding; the map keeps it out.
- **Second inflation channel, now MEASURED (H1389):** parsing MW's `<ls>L.</ls>` from csl-orig
  `mw.txt` reproduces §97 v2 exactly (59,697 of 194,084 MW headwords, 30.8%, carry no text
  citation) and regrades the re-audit so MW witnesses a headword only when it *cites a text*.
  The P3 corroborated share falls 34.7% → **33.8%** (the drop is larger at P2, 53.1% → 46.2%,
  where MW is still a separate witness); and **17,386 union headwords are MW-listed ghosts** —
  MW is their only dictionary and only lists them, so they have **zero text witnesses** (the
  first-pass estimate ~18,368 was close). Mask committed as `mw_non_textattested_slp1.txt`.
- **Incidental, now FIXED (H1389):** UNION.md's published "in N dicts" table was **pre-fold**
  (summed to 323,662 = 142,673 singletons + 180,989 in ≥2) vs the live post-fold
  `union_headwords.tsv` of 323,425 (237 `-inī` feminines folded); regenerated post-fold (in ≥2
  180,804, singletons 142,621), 237-headword drift closed.

The re-audit's P0 identity map reproduces the live union's own `n_dicts` column exactly
(regression anchor). **Consequence:** any "the tradition agrees / attested in N dicts" tally
over the Cologne union must collapse to witness families first — the machine-readable map is
committed for reuse.

> **Source:** H1363 —
> [`data/WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md),
> [`data/witness_independence_reaudit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_independence_reaudit.py),
> [`data/witness_tiers.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_tiers.json) ·
> [SanskritLexicography PR #602](https://github.com/gasyoun/SanskritLexicography/pull/602) ·
> 20-07-2026, Opus 4.8 (`claude-opus-4-8`). ↔ operationalizes §83, §97, §28.
> **H1389 (text-attestation regrade + post-fold table):**
> [`data/mw_ls_textattest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/mw_ls_textattest.py)
> + [`mw_non_textattested_slp1.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/mw_non_textattested_slp1.txt) ·
> 20-07-2026, Opus 4.8 (`claude-opus-4-8`).

### §98. PD's inline sigla contain a near-homograph pair that similarity-clustering silently fuses — `MahāBhā.` is the Mahābhārata, `MahāBh.` is the Mahābhāṣya, and the locator shape tells them apart mechanically

The Poona Dictionary ([PD](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt),
55 MB, 107,630 `<L>` entries) has **no `<ls>` citation layer** — unlike the 8 Cologne
dictionaries behind [`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv),
to which PD contributes zero edges. Its source sigla are inline in running prose, so any
consumer must harvest them by pattern and then normalise spelling variants into families.
A regex probe finds **5,231 distinct candidate tokens** across **416,767 occurrences**, with
**99.2 % of entries carrying at least one citation** — against a plausible real works list of
~800–1,500, i.e. roughly 3–4 tokens of noise or variance per genuine work. Variant collapsing
is therefore unavoidable, and the obvious tool (prefix/similarity clustering, as used for
[`siglum_family_candidates.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/siglum_family_candidates.csv))
**merges the two highest-value sources in the dictionary into one node.**

`MahāBhā.` (9,339 occurrences) and `MahāBh.` (1,940) differ by one character and are not
variants of the same work. Verified against the actual citation contexts, not inferred from
abbreviation convention:

| | `MahāBhā.` | `MahāBh.` |
|---|---|---|
| Work | **Mahābhārata** | **Mahābhāṣya** (Patañjali, Kielhorn ed.) |
| Locator | parvan.adhyāya.śloka — `i. 16. 9`, `iii. 3. 24`, `vii. 22. 33` | volume.page.line — `iii. 465. 17`, `i. 323. 19` |
| Diagnostic tail | none; cross-refs to `BrahmP.`, quoted by `ŚabdKaDru.`/`Vāc.` | **`({%on%} …)`** naming the commented sūtra — `({%on%} P. viii. 4. 68)`, `({%on%} ŚivSū.(Gr.) 1)` |
| Distinct locator shapes | **1,317** (wide, as an epic's citation space should be) | **72** (narrow, formulaic) |

**The mechanical discriminator is the `({%on%} …)` tail, not the siglum spelling.** A
Mahābhāṣya citation names the Pāṇini or Śivasūtra rule it comments on; a Mahābhārata citation
never does. That test is robust to the spelling collision and should gate the merge decision.

**Why this matters beyond one pair.** The failure is silent and directional: fusing them
inflates a single node to 11,279 citations and destroys the ability to distinguish PD's
largest *epic* source from its most important *grammatical* one — which is exactly the
distinction any corpus-coverage or citation-weighting measurement depends on. When harvesting
PD sigla, hand-review every merge in the top ~100 by frequency rather than trusting a
similarity threshold; `Kāśi.`/`KāśiVṛ.` and `PadmP.`/`PadmaP.` in the same head are genuine
merges, so a blanket "never merge" rule is equally wrong.

Related noise classes in the same harvest, all needing classification rather than merging:
structural tokens (`I.`, `II.`, `Ed.`, `App.`), language labels (`Skt.`, `Pr.`, `Sg.`), and
**secondary scholarship** — `EI.` (Epigraphia Indica, 3,281), `POK.` (Pokorny), `TURN.`
(Turner). The last class matters for any claim that PD's siglum list represents "works in
Sanskrit": it mostly does, but not purely.

**Standing caveat on any PD-derived denominator:** PD is published only from `a-` to about
`apaca-` (6 of 37+ planned volumes, 104,959 lemmas — [`dictionary_inventory.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary_inventory.csv)).
A harvested siglum list is *PD's canon as exercised under the letter a-*, not its full
declared canon; the printed front-matter "List of Works and Abbreviations" is what would
close that gap.

> **Source:** measured probe over `external_src/pd/pd.txt` during the scoping of
> [H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md)
> (PD-abbreviation-list vs DCS corpus coverage) · 19-07-2026, Opus 4.8 (`claude-opus-4-8`).
> Identification verified by citation-context inspection, not by convention.

---

### §99. Output gates must audit structured semantic fields, and sample-clean editorial rewrites still require a full-population ambiguity pass

The H1305 RU style gate originally scanned rendered `.merged.md` output and applied
«вместо»→«вм.» / «в значении»→«в знач.» globally after a clean 60/291 R2 sample and a
24/24 R3 census. Review exposed two independent false-positive paths. First, rendered
output contains notes, differentia, source text, headings, and footer metadata that are not
the translated sense; those fields can contain a trigger even when every Russian sense is
clean. Second, the R2 sample missed rare quoted, retained, and narrative uses. A complete
pre-sweep audit measured R2 **279 hard / 12 ambiguous** and R3 **20 hard / 4 ambiguous**.

**Reusable rule.** A gate for a semantic output field must parse the producer's structured
result and inspect that field directly (`card.records[].senses[].russian` here), aggregating
back to the original work key only after field-level classification. Rendered documents are
presentation artifacts, not an audit schema. For style substitutions that can also be
ordinary prose, use an explicit high-precision cue classifier; surface ambiguous matches as
warnings and keep them out of defect/requeue output. Before a store-wide apply, audit the
whole trigger population when it is small enough—an apparently clean random sample does not
establish absence of rare context classes.

The repair also established the write-safety pattern: reconcile an old backup to the live
store by a stable non-translation hash plus duplicate ordinal; recognize only original,
legacy-transformed, or newly scoped values; refuse the whole apply on divergence; create a
new exclusive timestamped backup on every apply; verify hash + row count; and re-hash the
live store immediately before atomic replacement. This restored 16 H1305 over-abbreviations
without overwriting later edits (11,603 rows, 0 conflicts).

> **Source:** [`RussianTranslation/src/ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py) +
> [`RU_STYLE_MECHANICAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md) ·
> 19-07-2026, Codex/GPT-5.

---

### §101. DCS's compound dictionary carries splits whose member **order** does not match the surface form — invisible to a type-drill, fatal to any head-first analysis

Measured 19-07-2026 over
[`VisualDCS/derived-data/Kompozity/names.csv`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Kompozity/names.csv)
(168 880 attested compounds, schema `surface; split; nMembers; totalFreq; …`). The
split field is **not** guaranteed to list members in the order they occur in the surface
form. Four distinct defect shapes, all with real corpus frequencies attached:

| surface | split as given | defect |
|---|---|---|
| `rājakule` | `kula rājan` | members reversed |
| `dharmālokamukhaṁ` | `āloka mukha dharma` | rotated |
| `gaur` | `go go` | member repeated beyond the surface |
| `ūrdhvaṁ` | `daśan rātra` | split belongs to a different word entirely |

**Why this went unnoticed until now.** Every prior consumer of this asset asked
order-independent questions — how many members, which lemmas participate, compound-type
frequency. Membership is correct in these rows; only sequence is wrong, so an
order-independent consumer sees clean data. The defect surfaces the moment something
depends on **which member is last** — i.e. any analysis using the standard rule that a
determinative compound's syntactic head is its final member.

**Mitigation that works despite sandhi.** A naive prefix check fails on correct rows,
because compound members are reshaped at the right edge by stem loss (`rājan` → `rāja-`)
and at the left edge by vowel sandhi (`indra` → `-endra`, in `rājendra`). Matching on the
ordered **consonant skeleton** (drop vowels, anusvāra and visarga; require each member's
first two consonants to occur in the surface skeleton in sequence) is blind to both edges
by construction and still discriminates: it accepts `rājendra ← rājan indra` while
rejecting all four rows above. At freq ≥ 5 and ≤ 4 members it rejects **209 of 6 287**
rows (3.3%).

**Rule:** any consumer of `names.csv`/`cmps.csv` that cares about member order must
verify it against the surface form and count the rejects — never reorder silently, and
never assume the last listed member is the head.

> **Source:** [H1298](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1298-Opus_SanskritGrammar_sangram-samasa-bracket-method-trainer_19.07.26.md) ·
> gate implemented as `order_ok()` in
> [`sangram/data/samasa_ladder/build_samasa_ladder.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/sangram/data/samasa_ladder/build_samasa_ladder.py),
> pinned by four regression tests in
> [`tests/test_samasa_ladder.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/tests/test_samasa_ladder.py) ·
> 19-07-2026, Opus 4.8 (`claude-opus-4-8`).

### §451. `10.5281/zenodo.15834721` is a false DOI, cited as genuine in two different repos

_↩ **Renumbered from §103 → §451** (H1361, 20-07-2026): the union-corroboration finding (§103, H1363) published first and keeps §103; this DOI claim (H1364) reused the number. Per the [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md)._

Two committed docs disagreed on this DOI's status ([CONTRADICTIONS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)):
[BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
called it a false DOI needing re-mint, while
[data/FAIR_RELEASE_1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md)
(H817) recorded it as csl-observatory's genuinely minted OBS-T dataset DOI. A live
Zenodo check 20-07-2026 (H1364) resolves the dispute: `https://doi.org/10.5281/zenodo.15834721`
redirects to a Zenodo record titled *"A Non-Surgical and Unconditional Proof of Topological
Sphericity via Entropy-Spectral Dynamics (v2.2)"* — an unrelated differential-geometry/topology
preprint deposited 08-07-2025, with no connection whatsoever to CDSL, csl-observatory, or the
OBS-T correction-event corpus.

**The false DOI had propagated further than either doc admitted.** csl-observatory's own
[`CITATION.cff`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/CITATION.cff)
carried the identical DOI in its `identifiers:` block, labeled "Concept DOI for the OBS-T
dataset (all versions)" — machine-readable citation metadata for a published repo, citing a
mathematics preprint that has nothing to do with it. Whoever copy-pasted this DOI (H817,
13-07-2026) apparently grabbed it from somewhere without resolving it first, and it was then
trusted as ground truth by a second document instead of being independently checked.

**Rule:** a DOI recorded as "already minted" for dataset X is not evidence dataset X has a
DOI — resolve `https://doi.org/<doi>` and confirm the landing page actually describes X before
citing or propagating the identifier anywhere, especially into `CITATION.cff`/`.zenodo.json`
machine metadata.

Fixed same pass: `data/FAIR_RELEASE_1.md` §Related and csl-observatory's `CITATION.cff` both
corrected to state the OBS-T dataset has **no minted DOI yet**.

> **Source:** [H1364](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1364-Sonnet_SanskritLexicography_contradictions-duplicate-section-repair-and-ch14-doi-ruling_20.07.26.md) · [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) / [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) · 20-07-2026, Sonnet 5 (`claude-sonnet-5`).

### §104. The DCS `dcs-conllu` treebank is only ~3.9 % dependency-parsed — corpus government/valency work must lean on co-occurrence, not arcs, and read absence as "unknown"

The [dcs-conllu](https://github.com/gasyoun/dcs-conllu) treebank looks like a fully parsed
dependency corpus — every `.conllu` token carries a lemma, UPOS, morphological `Case`, and
`HEAD`/`DEPREL` columns. It is not: of its **754 726 sentences (5 688 416 tokens across 15 900
files)**, only **29 433 sentences (3.9 %) actually carry dependency arcs** — the rest have `_`
in the HEAD/DEPREL columns. Measured while adjudicating Scherzl's government catalogue against
the corpus (H1372).

Consequences for any government/valency/kāraka study over this treebank:

- **A zero dep-arc count is never disconfirming on its own.** ~96 % of the corpus cannot supply
  an arc, so "verb V has no case-C dependent" is overwhelmingly a parse gap, not evidence V
  cannot govern C. Report the parse ceiling as the headline, not the confirmation rate.
- **Co-occurrence must be measured against chance, never raw.** A frequent verb co-occurs with
  every case, so raw co-occurrence is uninformative; use observed ÷ (verb_freq · corpus base-rate
  of the case). Corpus base rates (share of sentences containing the case): Nom 74 %, Acc 49 %,
  Gen 25 %, Ins 23 %, Loc 21 %, Abl 8 %, Dat 6 %. Only a *below-chance* co-occurrence is a real
  negative signal (e.g. jñā + genitive co-occurs 1 533× — never a contradiction despite no arc).

**Equivalence, so you can pick either serialisation:** `dcs-conllu` is the CoNLL-U serialisation
of the same DCS-2026 master as `VisualDCS/src/DCS-data-2026/dcs_full.sqlite` — token count
**5 688 416** and **11 096** distinct verb lemmas match the sqlite exactly. Prefer the conllu form
when you need HEAD/DEPREL (the sqlite would need a join); prefer the sqlite for lemma/preverb
lookups.

> **Source:** [H1372](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1372-Opus_SanskritGrammar_scherzl-government-relations-vs-dcs-treebank-adjudication_20.07.26.md) ·
> measured by [`aggregate_dcs_gov.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/BuhlerLeitfaden_1923/government_class_index/aggregate_dcs_gov.py),
> reported in [`SCHERZL_GOVERNMENT_CORPUS_ADJUDICATION_2026.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/BuhlerLeitfaden_1923/government_class_index/SCHERZL_GOVERNMENT_CORPUS_ADJUDICATION_2026.md) ·
> 20-07-2026, Opus 4.8 (`claude-opus-4-8`).

---

### §456. MW's derivation markup and the DCS corpus are productive over the *same* compound final members but with near-disjoint first members (median Jaccard 0.00, 56% share zero) — and the corpus-unattested MW stratum is kośa/participle formations, not ghost-words

_↩ **Renumbered §102 → §456** (H1328 collision fix, 20-07-2026): this H1328 finding (PR [#618](https://github.com/gasyoun/SanskritLexicography/pull/618)) reused §102, already held by the DCS `text_sandhied` finding (the incumbent). Per the [citation-identity ruling](epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) rule 4, the later claim moves. Caught by the new epistemic-integrity gate ([issue #624](https://github.com/gasyoun/SanskritLexicography/issues/624))._

Measured 20-07-2026 (H1328) by joining the MWderivations `issue15` **uttarapada** (compound
final-member) index — 19,177 distinct MW-kept finals, classes `UTTARAPADA` + `KRT_STEM_MEMBER`,
the bound taddhita suffixes `-tva`/`-tā`/`-vat` already excluded upstream — to the DCS Kompozity
split-list (`cmps.csv` × `names.csv`: 399,096 distinct compound word-forms, 168,481 freq-annotated,
21,958 distinct finals), keyed on the compound final member. This is the first join of these two
sides of one phenomenon; two substantive results, plus a join-hygiene trap that has to be cleared first.

**Join hygiene — two orthographic folds are mandatory or the join is fake, and two morphological
differences must NOT be folded.** A naïve string join matches only **29 %** of MW finals; almost all
of that miss is artefact, not absence. Folding **anusvāra** (MW writes `ṃ` U+1E43 *dot-below*, DCS `ṁ`
U+1E41 *dot-above*) and MW's own markup (`@` join marker, `-` hyphen, and a **leading avagraha** `'`
= elided initial *a-*, so `'bja` = *abja*) lifts the match to **33 %**. Both folds are pure orthography,
applied to both sides. What is deliberately **not** folded is morphology: final vowel-length / gender
(`sena` vs `senā`, `phalā` vs `phala`), the `vatī`/`vat` suffix shape, and junction sandhi (`cchada`
vs *chada*, `ṣṭha` vs *stha*) — folding those would *manufacture* matches. They are diagnosed as a
separate `form_variant` stratum (**1,289** finals) and **never asserted absent**. The four strata of
MW finals against the corpus:

| `corpus_status` | count | meaning |
|---|---:|---|
| `final` | 6,249 | attested as a compound-**final** member in the corpus — joinable |
| `form_variant` | 1,289 | a corpus final differing only by vowel-length / gender / junction sandhi — **not** an absence |
| `nonfinal_only` | 1,252 | occurs in the corpus but never compound-finally |
| `absent` | 10,387 | appears nowhere in the corpus as any member — the dictionary-only stratum |

**Finding 1 (headline) — dictionary and corpus are productive over the *same* finals but populate
them with *different words*.** Of the 6,249 finals **both** sides attest, the two first-member
vocabularies barely intersect: **median Jaccard = 0.00** (mean 0.10), and **3,526 of 6,249 (56 %)
share zero first members at all**. `-indra` "lord-of": MW records 2 first members, the corpus 286,
overlap **0** (3,072 corpus tokens); `-ādi` "and-the-rest": MW 13 vs corpus 2,126, overlap 5. The
well-behaved case (`-pati`, MW 358 / corpus 200 / 90 shared) is the exception, not the rule. So even
where MW's derivation markup and DCS agree that "-X" is a live compound head, they overwhelmingly
disagree about *which* words sit in front of it — "productive in the dictionary vs attested in the
corpus" made concrete at the level of the individual final member, the thing neither asset records alone.

**Finding 2 — the 10,387 corpus-unattested MW finals are a low-productivity kośa/participle stratum,
NOT ghost-words.** 86 % (**8,892 / 10,387**) are MW **hapax** finals (a single first member even inside
MW; median `mw_first_members` = 1); only **50** are productive-yet-corpus-absent (`mw_first_members ≥ 10`),
and those sort into recognisable lexicographic classes: kośa-tradition work-title / *nāma* formations
(`puṣpikā` 36, `ratnāvalī` 29, `muktāvalī` 22, `campū` 17), deverbal-participle finals DCS does not
segment (`baddha` 33, `cyuta` 25, `varjita` 24, `gṛhīta` 19), inflected adverbial finals DCS lemmatises
away (`pūrvakam`, `taram`, `kāram`), plus a residue of MW-index split artefacts (finals opening `ṃ-`,
or with a stranded `ṛ`: `rṣi` = *ṛṣi*). This directly reinforces
[§86](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#86-samāsa-type-frequency-does-not-exist-in-any-org-corpus--and-the-grammarians-canonical-examples-are-corpus-ghosts-858-attested-max-freq-147)
(the grammarians' canonical samāsa examples are themselves corpus-ghosts, 8/58 attested) and
[§97](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#97-cross-dictionary-attestation-via-monier-williams-overstates-independence--mw-was-compiled-from-böhtlingk-roth-pwpwg-so-an-mw-only-hit-is-not-evidence-a-pwpwg-word-is-independently-text-attested)
("most PWG ghost-words are corpus gaps, not ghosts"): exact normalized match is a **lower bound** on
attestation, so the 10,387 are candidates, not verdicts, and the residue is a real kośa / DCS-segmentation
stratum, not spurious words.

**The corpus side has its own junk head, mirroring MW's excluded taddhita head.** DCS over-segments
enclitics, pronoun stems and bare verb roots as compound members: `ca` (**11,057 forms / 2 tokens**),
`eva`, `idam`/`tad`, and bare roots `kṛ`/`as`/`bhū`/`gam` — all high on a form-count ranking, near-zero
on tokens. The exact twin of MW's excluded taddhita head is `-tva` (3,546 forms / 4,830 tokens) and
`-tā` (1,755 / 2,758): genuinely high-frequency, so ranking by tokens alone does **not** drop them — an
explicit stoplist (particles + pronoun stems + bare roots + `-tva`/`-tā`) is required on the corpus side,
exactly as issue15 set those suffixes aside on the dictionary side. (Same `names.csv`/`cmps.csv` asset
whose member-**order** caveat is
[§101](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#101-dcss-compound-dictionary-carries-splits-whose-member-order-does-not-match-the-surface-form--invisible-to-a-type-drill-fatal-to-any-head-first-analysis).)

> **Source:** report [`reports/uttarapada_dict_vs_corpus_divergence.md`](https://github.com/gasyoun/VisualDCS/blob/main/reports/uttarapada_dict_vs_corpus_divergence.md)
> + join [`derived-data/Kompozity/uttarapada_dict_vs_corpus.tsv`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Kompozity/uttarapada_dict_vs_corpus.tsv)
> (19,177 rows) + build [`derived-data/Kompozity/build_uttarapada_dict_vs_corpus.py`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Kompozity/build_uttarapada_dict_vs_corpus.py) ·
> dictionary side = [MWderivations `issue15/compounds_reverse_classified.tsv`](https://github.com/gasyoun/MWderivations/blob/master/issue15/compounds_reverse_classified.tsv) ·
> [H1328](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1328-Opus_VisualDCS_kompozity-mw-uttarapada-join-dict-vs-corpus_19.07.26.md)
> — VisualDCS · 20-07-2026, Opus 4.8 (`claude-opus-4-8[1m]`).

### §457. DCS covers ~25% of the Poona Dictionary's citation mass but ~78% of DCS's own tokens — the classical core, not PD's encyclopedic breadth; and a siglum prefix-merge fuses MahāBhā. (Mahābhārata) with MahāBh. (Mahābhāṣya)

🔴 First measurement, in this org or the field, of how much of the **Poona Dictionary**'s
cited source canon the **DCS** corpus holds. Over PD's published letter-`a-` volumes (107,630
entries, 398,359 citation occurrences), the two coverage numbers point in opposite directions
and answer different questions:

- **PD-citation-weighted coverage = 25.2 %** — of what PD actually cites, three-quarters
  points at works DCS does not hold.
- **DCS-token-weighted coverage = 77.9 %** (2026) / 74.1 % (2021) — of DCS's *own* token
  mass, ~78 % sits in texts PD cites (the Mahābhārata alone is 1.15 M of DCS's 5.69 M tokens).
- **Title-level = ~2.4–4.8 %** — DCS holds ~118 of the ~2,445 distinct works PD cites under
  `a-` alone.

**Reading: DCS is representative of the archaic/classical *core* but not of PD's encyclopedic
*breadth*.** The residue (75 % of PD's primary citation mass) is four clusters DCS structurally
lacks: **purāṇas** (Padma 3,506; Brahmāṇḍa 1,857; Bhaviṣya 1,558; a dozen more), the
**lexicographic tradition** (Vaijayantī, Medinī, Nānārtha), **classical kāvya/nāṭaka** (*no
Raghuvaṃśa, no Kādambarī, no Śiśupālavadha*), and the **grammatical commentary layer**
(Mahābhāṣya, the Vārttikas). Corpus work grounded in the high-frequency classical core is
well-aligned with the lexicographic gold standard; work needing purāṇic/kāvya/kośa breadth
must supplement DCS. DCS's 2021→2026 growth was concentrated in exactly PD's Vedic core
(Śatapathabrāhmaṇa 3.7k→144k tokens; +3.8 pp token-weighted coverage).

⚠️ **The reusable gotcha — never prefix-cluster Sanskrit sigla.** `MahāBhā.` (9,337 hits =
**Mahābhārata**, the epic) and `MahāBh.` (1,934 hits = **Mahābhāṣya**, Patañjali's grammar)
share a five-character prefix and differ by one vowel-length mark. Any similarity/prefix
threshold that "normalises spelling variants" will silently fuse the single largest epic with
the single most important grammatical commentary — one is covered by DCS, the other is
residue, so the merge corrupts coverage in both directions. Every siglum merge in the
high-frequency head needs eyes on it, not a threshold. (This is why the crosswalk anchors on
DCS's bounded 276-text inventory and adjudicates the head by hand rather than clustering.)

> **Source:** report [`reports/PD_DCS_CORPUS_COVERAGE_2026.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md)
> + crosswalk [`data/pd/pd_dcs_text_crosswalk.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_text_crosswalk.tsv)
> + [`pd_siglum_families.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_siglum_families.tsv)
> + [`pd_dcs_metrics.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_dcs_metrics.json) ·
> PD source = [`pd.txt`](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt) (external, read-only) ·
> DCS = [`VisualDCS` Corpus-Delta 2021–2026](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/per_text_token_delta.csv) ·
> [H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md)
> ([csl-atlas PR #276](https://github.com/sanskrit-lexicon/csl-atlas/pull/276)) — csl-atlas · 20-07-2026, Opus 4.8 (`claude-opus-4-8[1m]`).
> **Scope caveat:** PD published a–~`apaca-` only (6 of 37+ vols) — this is PD's canon *as exercised under a-*, not its full declared canon.
### §458. A Sanskrit dictionary's big letters are big because they head *preverb families* — and testing "entries shrink over publication" needs an outlier-robust estimator, not a parametric regression (encyclopedic dicts have single 300k-char articles)

🔴 **The per-letter law.** Extending [§457](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)'s
passing observation that MW's letter `a` is 83.1 % dash-marked compounds, a full per-letter
scan of MW shows `a` is the *most* compound-dense letter **but not uniquely so** — `u` (79.5 %),
`p` (78.0 %), `s` (77.9 %) and `v` (75.5 %) are right behind it, while `k` (56.4 %) falls away.
The mechanism is the **upasarga (preverb)**: every ballooning letter heads a productive preverb
family — `v` = *vi-* (38.6 % of all `v` headwords), `u` = *ud-/upa-* (62.3 % combined),
`s` = *sam-/su-*, `p` = *pra-/pari-/prati-*, `a` = *ā-/abhi-/anu-/apa-/ava-* plus the privative.
`k`, `g`, `c` head no preverb and carry no such combinatorial shadow. So "`a` is a letter of
compounds not roots" is true, but it is a property of *preverb-headed letters in general*, of
which `a` is merely the richest — not an `a`-anomaly.

⚠️ **The reusable methodological gotcha — never test entry-size decay with a parametric mean-based
regression on a Sanskrit→Sanskrit encyclopedic dictionary.** The historical claim that dictionary
entries **shrink toward the end of the work** as funding/energy fell (raised specifically for
**SKD** Śabdakalpadruma and **VCP** Vācaspatyam) must be tested with letter fixed effects (later
letters host intrinsically shorter words — a composition confound). But even a log-scale letter-FE
OLS is **wrecked by outliers**: VCP has a median entry of 112 characters and a *maximum of 310,090*
(SKD max 128,405) — a dozen page-long encyclopedic articles give VCP a spurious parametric slope of
**+733 %/traversal**, sign-flipped from its own naïve slope. The correct tool is an **outlier-robust
per-letter rank test** (Spearman of position vs size *within each letter*, aggregated by Fisher-z),
which is immune to the giant articles and removes the composition confound by construction.

**Substantive result (the arbiter test):** the funding-decay hypothesis is **REFUTED for its two
named targets** — SKD ρ = −0.001, VCP ρ = +0.001 (both non-significant) — and real & strong only
in the **German Petersburg tradition + Grassmann**: PWG ρ = −0.19 (36/38 letters negative),
PWK ρ = −0.34 (27/32), GRA ρ = −0.20 (28/30) — precisely the works with a documented editorial-
compression history (PWG's over-detailed 1855 first volume of `a-`). "Later entries are shorter" is
a Petersburg-tradition fact, not a Sanskrit-encyclopedic-dictionary one. PD is untestable this way
(confined to `a`).

> **Source:** report [`reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md)
> + feeds [`data/pd/letter_anatomy.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/letter_anatomy.tsv)
> / [`entry_size_by_position.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/entry_size_by_position.tsv)
> + generator [`scripts/letter_anatomy.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/letter_anatomy.py)
> · page `/tools/letter-anatomy` · sources = [HeadwordLists/now-2026](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026) + [csl-orig v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02) entry bodies ·
> [H1416](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1416-Opus_csl-atlas_letter-anatomy-samasa-upasarga-entrysize-decay_21.07.26.md)
> ([csl-atlas PR #282](https://github.com/sanskrit-lexicon/csl-atlas/pull/282)) — csl-atlas · 21-07-2026, Opus 4.8 (`claude-opus-4-8`).

### §459. PWG's entry-size decay is a *smooth* funding/energy fade across its whole 20-year run (−14 %/decade), not a one-time correction after the over-detailed first volume — and SKD/VCP carry ~0 digitisation markup

🔴 **The cause question [§458](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) left open is now settled for PWG.** [§458](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) measured PWG's entry-size decay against *alphabetical position*; whether that reflects funding/energy decline over time versus a one-off correction after the famously over-detailed first volume (`a-`, 1855) could not be told apart from position alone. PWG's Cologne `<pc>` field encodes the **volume (1–7)**, each with a known publication year (1855, 1858, 1861, 1865, 1868, 1871, 1875), so **all 123,366 PWG entries map to a real calendar year** (0 unparseable). Regressing log entry-length on year: **−14.3 %/decade** (95 % CI [−15.0, −13.7], p ≈ 0). The **editorial-compression counter-test resolves the cause**: dropping vol-1 entirely, **volumes 2–7 still shrink −15.3 %/decade** (and the vol-1→later median drop is only −18 %). So the decline is a **smooth fade across the entire 20-year publication**, consistent with (though not proof of) the funding/energy-decline narrative — *not* a single policy break after vol-1. PWK/SKD/VCP lack any per-fascicule date map (only overall spans), so real-time regression is impossible for them — the [§458](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) alphabetical-position decay remains their only signal.

⚠️ **Reusable gotcha for cross-dictionary "depth" metrics — markup density measures the *digitisation apparatus*, not lexicographic depth.** A per-entry density fingerprint across MW/AP/PWG/PWK/SKD/VCP shows PWG carries the richest apparatus (**20 markup tags/entry**), PWK the tersest body (**43 chars/entry**, the *kürzere Fassung* condensing as designed) — but **SKD and VCP carry ~0 Cologne markup** (0.1 tags, 0 `<s>`/`{#}` spans): they are plain Sanskrit→Sanskrit encyclopedic text with no structural tagging. So any cross-dictionary "depth" or "richness" metric built on markup counts silently ranks SKD/VCP at zero for a *digitisation* reason, not a lexicographic one. The robust cross-tradition depth signal is **chars/entry (median)** — on which the encyclopedics (SKD 169, VCP 112) run far longer than the terse EN/DE working dictionaries (MW 46, PWK 40).

> **Source:** csl-atlas [H1423](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1423-Opus_csl-atlas_dict-macrostructure-anatomy-exec_21.07.26.md) ([PR #290](https://github.com/sanskrit-lexicon/csl-atlas/pull/290)); report [`LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md §7`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md); feeds [`entry_size_by_year.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/entry_size_by_year.tsv) + [`density_fingerprint.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/density_fingerprint.tsv); generators [`entry_size_chronology.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/entry_size_chronology.py) / [`density_fingerprint.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/density_fingerprint.py) · pages `/tools/letter-anatomy` (Wave-B chart) + `/tools/dictionary-density` — csl-atlas · 21-07-2026, Opus 4.8 (`claude-opus-4-8`).

### §460. "Gold" in this org means *frozen*, not *human-adjudicated* — 0 of 15 gold datasets have independent human annotation, and every travelling κ is model-vs-model (four contamination mechanisms)

🔴 **The H1272 cross-repo provenance audit ruled every dataset the org trades as "gold"/adjudicated: 0 GOLD · 1 SILVER · 4 LLM-ASSISTED · 10 CONTAMINATED · 0 UNDOCUMENTED** (61 raw candidates → 15 canonical datasets across 10 repos). The only human-annotated set is the kosha Gītā gold master — single annotator (MG), no second pass → SILVER. Every κ that travels as a reliability number in the org's papers is **model-vs-model**, not human IRR. The one good surprise: 0 UNDOCUMENTED — provenance was recoverable for every dataset; the org's record-keeping is strong, what it records is the problem. Full census + per-dataset evidence: [GOLD_PROVENANCE_AUDIT_2026H2.md](https://github.com/gasyoun/SanskritGrammar/blob/main/GOLD_PROVENANCE_AUDIT_2026H2.md) + [verdicts JSON](https://github.com/gasyoun/SanskritGrammar/blob/main/GOLD_PROVENANCE_AUDIT_2026H2_verdicts.json).

⚠️ **The reusable part is the four contamination mechanisms — the checklist for any future eval set, because the repairs differ per mechanism.** **(1) The evaluated system authored its own gold** — MW defgen: `deepseek-chat` is a generation arm *and* the sole blinded judge of all arms including its own; semdom ↔ Amarakośa: both annotators saw the bridge's top-6 candidates and kept one for ~half the rows, so ~half the "gold" labels are the bridge's own output; csl-guides routing: Fable 5 annotated against an Opus 4.8 answer key — same family on both sides of a 100% accuracy claim. **(2) Same-family agreement reported as inter-annotator agreement** — A65's κ 0.877 is Claude-vs-Claude; A44's 0.336/0.663 is Sonnet 5 + Fable 5 vs Opus 4.8; the one genuinely cross-family number (A26, DeepSeek vs Claude, 0.670) is also the lowest — agreement rises as annotators become more similar, which is exactly what a reliability statistic must not measure. **(3) LLM output labelled as human review** — csl-observatory's "390 human-annotated events" were one pass of an uncommitted Sonnet-4.6-co-authored rule classifier (commit `5b5b280`), zero humans; csl-atlas's "human-reviewed gold subset" behind a precision of 1.000 is 130/147 `codex` + 7/147 `Antigravity` = 93% machine, with notes openly saying "Automated resolution based on nasalization normalization" — re-derived from the very normalization logic the evaluated pipeline uses. **(4) Circular controls** — the pwg_ru judge-battery's 76 OK controls were declared clean by the same Opus/Sonnet judges the battery exists to compare; its travelling κ = 1.00 belongs to a different card set entirely. Corollary vocabulary rule: **an LLM annotator is not a human annotator** — two blind LLM passes plus an LLM adjudicator is not GOLD, whatever the κ; where two labels fit, the worse wins, and CONTAMINATED outranks all.

> **Source:** [H1272](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1272-Fable_SanskritGrammar_gold-provenance-contamination-audit_18.07.26.md) audit, census/verdicts by Fable 5 (`claude-fable-5`) subagents 18–19-07-2026, report synthesis Opus 4.8 (`claude-opus-4-8`), merged as [SanskritGrammar PR #431](https://github.com/gasyoun/SanskritGrammar/pull/431); 10/10 CONTAMINATED verdicts adversarially refutation-tested (the last, csl-atlas overlay queues, closed 21-07-2026 by Fable 5 `claude-fable-5`). Repairs are parked as `@DECIDE` rows in [Uprava GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md), never self-executed — gold files themselves untouched · 21-07-2026, Fable 5 (`claude-fable-5`).

### §461. The r2 kośa-fusion "separable" class is substantially an orthographic sandhi artifact — whether an SKD citation counts "fused" depends on whether the authority's name begins with a vowel

🔴 **Three instrument artifacts in the [`r2_kosa_fusion.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json) classifier behind A30/A02's 53.3 % (SKD) / 77.6 % (VCP) *iti*-fusion headline, all visible in its own committed 102-row sample.** (1) *Sandhi severance:* the unit splitter cuts after every standalone `iti`, while SKD authority detection keys on the sandhi-fused `ity<word>` pattern — so *ityamaraḥ* (obligatory sandhi before a vowel-initial name) stays with its definition and can class "fused", but *iti medinī* / *iti hemacandraḥ* (no sandhi before consonants) is severed, its name-tail landing in "separable" at offset 0: ~24 of the 34 sampled separable rows are bare `medinI`/`hemacandraH` tails of philologically *fused* citations. (2) *Recall ceiling:* SKD authority detection = a 16-name curated list + the `ity`-regex; the `other-no-authority` class (80 % of SKD units) visibly contains severed citations of Halāyudha, Rājanirghaṇṭa, Trikāṇḍaśeṣa, Durgādāsa, Sāyaṇa and others the list misses — the fusion denominator (24,087) is a biased ~30 % subsample of the 80,164-citation register A08 counts independently. (3) *Formula false-positives:* `\bity[a-zA-Z]{3,}\b` matches *ityarthaḥ* / *ityādi* (sample row L8904 is authority-marked via `ityarTaH`, a gloss formula).

⚠️ **Reusable rules.** Never consume the fused/separable split as a register property of SKD-vs-VCP — the "units" are different objects (SKD *iti*-micro-segments, 2.88/record, vs VCP mostly whole-record `lumped-proxy` blobs, 1.31/record) detected by different instruments (curated names + `ity`-regex vs the `<name>0` siglum regex), and the ≥20-non-whitespace-chars fusion threshold makes "fused" quasi-monotone in unit length. Corollary for prose: the committed corpus stats *invert* the "short SKD entry vs long VCP commentary" story ([`dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json): SKD meanChars 531 > VCP 493, medians 221 > 162, and VCP has MORE records, 50,135 > 42,531 — VCP's discursive register is a tail phenomenon, maxChars 312,261). Any segmenter for indigenous citation formulas must split *name-aware* (keep `iti <name>` together), not on bare `iti`.

> **Source:** hostile referee pass [papers/A30_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_review_fable5.md) (M1–M5) + model-labelled sample [papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md), verified against csl-atlas `origin/main` `a56444f` ([`build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs), [`build-r2-source-anchors.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-source-anchors.mjs), [`r2_kosa_fusion_sample.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion_sample.json)) · [H1382](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1382-Fable_SanskritLexicography_a30-hostile-referee-pass-skd-vcp_20.07.26.md) ([PR #662](https://github.com/gasyoun/SanskritLexicography/pull/662)) — SanskritLexicography · 21-07-2026, Fable 5 (`claude-fable-5`).

### §462. On Windows, repeated repository discovery can dominate a Python pipeline: cache checkout identity, not mutable path overrides

⚠️ **Reusable performance gotcha.** A small PWG→Russian preflight launched **88 Git subprocesses**
only to rediscover the same main-worktree identity; those launches consumed **4.50 s of 5.29 s**.
The safe cache boundary is narrower than “cache the resolved store path”: cache only the immutable
checkout relationship, keyed by normalized absolute directory, for the life of the process. Keep
`PWG_RU_STORE` / TM environment overrides outside that cache so test and operator overrides remain
live, and never cache a blank/failed Git lookup as “not a linked worktree” — one transient failure
would otherwise pin the process to a worktree-local store. The same audit found two unnecessary
scans of the 26 MB canonical JSONL around promotion even though the atomic child transaction already
reported exact before/after row counts; consuming the validated receipt avoids reopening the store
without weakening the audit trail.

The frozen H1339 smoke fixture kept the exact output signature
`da1341e6ac112bf83c7c521d194f698aa39da067075b636463fa6748c43fb629` while the combined safe wins
reduced one-run total time **17.842→11.354 s (−36.4%)**. Treat that as a smoke result, not a stable
benchmark: `warmups=0`, `runs=1`. A further case-exact lookup fix snapshots output-directory names
once after collection instead of rebuilding `set(os.listdir(...))` for every card; it landed after
the frozen comparison and is therefore excluded from the percentage.

> **Source:** [`docs/PIPELINE_AUDIT_pwg_ru_2026-07-21.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PIPELINE_AUDIT_pwg_ru_2026-07-21.md) +
> [`RussianTranslation/src/store_path.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py) +
> [`RussianTranslation/src/pilot/coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) — offline Codex audit, 21-07-2026; no live/model/promotion/store call.

### §463. The pwg_ru store's `de` field is NOT a faithful copy of the csl-orig German — Russian connectives have been substituted into the source-of-truth string

🚨 **Data-integrity.** Eleven of 11,603 pwg_ru store rows (0.09%) carry Cyrillic **inside the
German `de` field**, and the substitutions are German function words replaced by their Russian
equivalents: `и` for `und`, `для` for `für`, `в` for `in`, `С` for `Mit`, plus a literal
`корригенда`. Verified against upstream: csl-orig `v02/pwg/pwg.txt` line 570640 reads
`{%Opfer%} in {#sarva˚#} **und** {#havirhuti#}` for `huti`, while the store row reads `… **и** …`
— *and* silently drops the `(von <hom>1.</hom> {#hu#})` etymology parenthesis. So the store's
German is a **mangled derivative**, not a verbatim carry-through, in at least these rows.

Two DE-side *structural* fields are contaminated at a higher rate: `sense_tag` in 110 rows
(0.95%) — e.g. `c) с dat. лица и instr. предмета`, `Mit <div n="p"> — корригенда` — and `h`,
which carries free-text Russian disambiguation prose such as `PW 3 (с sam, о супружеском
намерении)`. `h` is therefore unusable as a homonym key; derive the homonym from `subcard`
(`edition_rel.homonym_of`) instead.

**Why it matters beyond cosmetics.** Every German-side derivation — the H1624 G1–G6 layers, any
FAIR export, any "compare the store against the scan" audit — treats `de` as the public-domain
source of truth. A German string that has been partly Russified is a silently corrupted
canonical field: it will not round-trip against csl-orig, and it leaks Russian into anything
built on the German side. **Any DE export must therefore validate purity rather than assume it**
— `export_de_edition.py` quarantines `de`-contaminated rows, reduces a contaminated `sense_tag`
to its ASCII skeleton, and drops `h` from its input allowlist entirely.

> **Source:** measured 26-07-2026 (H1629, Opus 5 `claude-opus-5[1m]`) over the full 11,603-row
> canonical store, cross-checked against
> [`csl-orig v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt);
> tables in [`RussianTranslation/RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md);
> guard in [`RussianTranslation/src/export_de_edition.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py).

### §464. The H1624 G1 `gloss_lang` classifier mislabels German as Latin/English about half the time it fires — and those spans are then withheld from translation

🚨 **Data-integrity.** A census of all 15,901 `{%…%}` glosses in the pwg_ru store's German text
found 229 (1.44%) classified non-German by
[`pwg_mask.gloss_lang_spans`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py).
Of those, ~122 (53.3%) carry unambiguous German evidence:

| lang | rule_id | spans | German-looking | FP rate |
|---|---|---|---|---|
| en | `english_content` | 153 | 117 | **76.5%** |
| la | `botany_binomial` | 68 | 5 | 7.4% |
| ambig | `homograph_ambig` | 8 | 0 | 0.0% |

Misfires are not marginal cases: `bis an's Ziel bringen` and `an sich nehmen, empfangen,
erlangen, erhalten` are classified **English**; `Gelegenheit gefunden habend` and `Willens
sein` are classified as **Latin botany binomials**.

**The consequence is silent, not cosmetic.** `classify_pct_detail` returns `translate: False`
for both `la` and `en`, so a false positive means a genuinely German gloss is masked to `{Tn}`
and **never reaches the translation model** — content dropped from the output with no error and
no counter. The `english_content` rule is the dominant contributor and the right place to look
first. Fixing it changes masking behaviour pipeline-wide, so it needs its own measured A/B
rather than an in-passing patch; downstream consumers should meanwhile treat a non-DE
`gloss_lang` as a hint, not a fact.

Caveat on the number: "German-looking" is a heuristic proxy (umlaut/eszett, a German function
word, or an `-en`/`-eln`/`-ern` verb ending, excluding genuine binomial shape), so 53.3% is
±; the sampled examples leave the direction beyond doubt.

> **Source:** measured 26-07-2026 (H1629, Opus 5 `claude-opus-5[1m]`) over the full canonical
> store; table + examples in
> [`RussianTranslation/RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md);
> limitation recorded in
> [`RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md) §5.

---

### §465. PWG sense × DCS attestation collapses from ~40% at lemma level to 0.67% at sense level — and three independent constrictions cause it

🔴 **Lemma-level corpus attestation for PWG is essentially free; sense-level attestation is
not, and the gap is caused by two ceilings that must not be conflated — one inside the
dictionary, one in the corpus.** Anyone promising "corpus frequency per PWG sense" is
promising something the current data cannot deliver at scale.

`Evidence:` measured on the frozen H1455/H1456 500-headword pilot frame (reused verbatim, not
re-derived). Of 943,877 DCS tokens under those lemmas, **102,085 (10.8%)** carry a
`m_wordsem` sense tag at all — the hard ceiling on any sense-level claim over this corpus.
Only **52 of 7,746 PWG leaf senses (0.67%)** are grounded to a DCS attestation by a shared
locus; against the other denominator, 52/5,201 DCS `wn` senses in frame (1.00%). Meanwhile
**500/500** groups attest at lemma level — but that is **true by construction**: every frame
row carries `dcs_attested=1`, so the frame was *selected* DCS-attested.

**Update 26-07-2026 (same handoff) — the unbiased frames now exist, and the real lemma-level
rate is ~40%, not 100%.** Re-run over a seeded uniform sample (2,000 groups) and over **every
PWG headword (109,050 groups)**: **43,352/109,050 = 39.8%** of PWG headwords have a DCS lemma,
so **60.2% have no DCS attestation at any granularity** — for those no sense-level join is even
conceivable. The 2,000-group sample estimates 40.4% (±2.2% at 95%), an interval that covers the
population value, so the sampling frame is sound. The `m_wordsem` mass ceiling is **stable
across all three frames** (10.8% / 11.9% / 11.2%), confirming it is a property of the corpus
annotation rather than of headword selection. Sense-level grounding did **not** scale and is
deliberately **not** reported as zero outside the H1455 aligner's 500-headword run (class
`R0_grounding_not_computed`) — a 0% there would be the absence of a job, not a measurement.
Full comparison:
[`PWG_SENSE_DCS_FRAME_COMPARISON.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_FRAME_COMPARISON.md).

**⚠️ Update 26-07-2026 (H1670) — the 0.67% was a MATCHER-REACH artefact, not a data limit.
Corrected figure: 7,372 grounded leaf senses, 12.25%.** Two independent limits, neither of
them data availability, had capped the number:

- **Passage depth.** The aligner compared each sense's `<ls>` against only the **3 passages
  per DCS lemma** that `dcs_kwic()` sampled *for the viewer* — **3,435 of 1,148,630
  available passages, 0.299%**. The exact-verse test was measuring the sample, not the corpus.
- **A dead map key.** `PWG_TO_DCS_TEXT` keyed the Ṛgveda as ASCII `"RV"` while PWG's abbrev
  is `ṚV`, so the corpus's most canonically-numbered text — **50,972 `<ls>` citations, 6.89%
  of the dictionary's total, second only to the Mahābhārata** — never matched anything.

With the **same** `verse_equal()` predicate, the same tiers and no heuristic added, running
the aligner at full passage depth over a 32× wider frame (16,208 groups, identical selection
query) gives **52 → 7,372 grounded leaf senses (0.67% → 12.25%)**, of which 5,647 are
exact-verse. Dictionary-wide, `R0_grounding_not_computed` fell **18,438 → 10,515 (−43.0%)**
and `R4_grounded_alignment` rose **50 → 5,058**. Attribution per lever, plus the three
precision defects the wider scan exposed and fixed (named books collapsing into one numbering
space; chapter-level matches mis-reported as exact-verse; the `ṚV` key):
[`PWG_SENSE_DCS_GROUNDING_LEVERS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_GROUNDING_LEVERS.md).

**What did NOT move — and this is the durable half of the finding.** `R1_lemma_absent_from_dcs`
fell by 52 groups and `R2_no_wordsem_tag` by 754, out of 109,050. Those two are genuine
data-availability constrictions and no amount of matcher reach touches them; the ~40%
lemma-level rate and the ~11% `m_wordsem` mass ceiling below stand exactly as measured. The
lesson generalises: **before concluding "the data cannot support this", check what fraction
of the data the measurement actually looked at.** Ceiling 2 below is also partly corrected —
it names Kathāsaritsāgara as a text DCS lacks, but DCS carries it (111,298 tokens); the
obstacle is its numbering. The remaining reach work (443 cited texts DCS carries but the map
never pointed at, 13.9% of `<ls>` mass) is
[H1691](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1691-Opus_kosha_pwg-dcs-text-crosswalk-beyond-five_26.07.26.md).

The two ceilings:

1. **Inside the dictionary, before DCS is consulted.** **12,953** `<ls>` citations hang on a
   *structural parent* sense node — a numbered sense like `1〉 m.` that has lettered children
   `1a`/`1b` and carries the citation itself. PWG never assigns these to a leaf sense, so no
   join can. A perfect corpus with perfect locus matching would still leave them lemma-level.
2. **In the corpus.** **86.8%** of groups are class `R3`: DCS *has* sense-tagged tokens, PWG
   *has* senses, and no shared locus links them — because PWG cites texts DCS lacks
   (Pañcatantra, Kathāsaritsāgara, kośa literature) or cites the Mahābhārata in continuous
   Böhtlingk–Roth numbering whose vulgate↔BORI-critical drift yields only adhyāya-level
   corroboration (H1455 wave-1.5). This is missing *evidence*, not absence of the sense.

Two further traps found while building it, both of which silently distort the denominator:

- **Structural parents are not leaf senses.** Counting every `sense_id` from
  `microstructure.leaf_senses` inflates the sense inventory ~16% (8,859 vs 7,746 on this
  frame), because a numbered node with lettered children is a container carrying only
  gender/grammar. The child test must be an *alphabetic* suffix — sense `11` is not a child
  of sense `1` (PWG entries reach 70+ numbered senses).
- **The committed `pwg_sense_loci.sample.tsv` is not the pilot frame.** It samples a
  *different* 500 headwords and overlaps the H1455 frame in **16 keys**. Joining it yields a
  near-zero coverage that is an artefact of the wrong input, not a fact about PWG; regenerate
  the frame's rows with `research/export_frame_sense_loci.py`.

`Implication:` do **not** promise per-sense corpus frequency for PWG, and do not read H1455's
concordance as corpus attestation — its dominant `ls` tier (85,472 rows in frame) is PWG
citing *itself*, excellent evidence for the dictionary's sense division and none at all that
DCS attests it. Growing sense-level coverage means **adding texts and locus crosswalks**, not
tuning a matcher. When quoting the "mass under a grounded lemma" figure (4.2%), quote it as the
upper bound it is — a grounded link identifies one sense at one locus, not every token of the
lemma.

**Scaling settled it (26-07-2026): three independent constrictions multiply, and compute fixes
none of the first two.** (1) 60.2% of PWG headwords are absent from DCS entirely. (2) 88.8% of
DCS token mass carries no `m_wordsem` tag — upstream annotation coverage, 219/270 texts.
(3) Only the *residue* after those two is a matcher/locus problem, and it needs texts and
crosswalks (Pañcatantra, Kathāsaritsāgara, vulgate↔BORI drift), not a better algorithm. So the
honest ceiling for any sense-level PWG×DCS product is set by (1) and (2) long before matcher
quality matters — running the pilot over the whole dictionary raised confidence in the
diagnosis, not the coverage.

**"Get a bigger corpus" is NOT an available lever for (1) — MG, 26-07-2026.** DCS already *is*
the largest **tagged** Sanskrit corpus; the corpora that are bigger carry **no markup**
(wisdomlib, currently under scrape). An untagged corpus therefore **can** raise *lemma-level*
attestation — shrinking the 60.2% "absent everywhere" class, which is a real and separate
result — but **cannot** raise *sense-level* grounding, because there are no sense tags to bind
to and none to be had without lemmatising and tagging it ourselves. Treating an untagged corpus
as a fix for the sense-level number is a category error; keep the two rates in separate tables.
This repo already consumes a `wl` wisdomlib signal for period-state tagging (§14) — extend that
lane rather than opening a second one, and check the Cloudflare reality
([Uprava FINDINGS §4](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)) before any
scrape. Follow-on:
[H1670](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1670-Opus_SanskritLexicography_pwg-dcs-sense-grounding-scale-levers_26.07.26.md).

**Update 26-07-2026 (H1691) — 7,372 → 8,208 grounded leaf senses (+11.3%), and the "no corpus
side exists" class was itself unreliable.** Working H1670's 443-abbrev crosswalk backlog
top-down mapped 12 further texts, each verified against its `pwgbib` entry, ~20 real `<ls>`
samples, address containment, and a competitive rank against all 270 DCS texts, then
hand-checked at ≥10 rows apiece (120/120 confirmed). The two largest additions — Pāṇini
(21,305 citations) and Manu (20,605) — had been classified `DCS-LACKS`, "a genuine corpus gap
that no crosswalk can close": see §471, which is the transferable lesson. `MAPPED` rose from
36.4% to **44.7%** of the dictionary's `<ls>` mass and the actionable backlog above 0.05% is
now empty. Two caveats belong with the number: the Aṣṭādhyāyī rows attest that Pāṇini *treats*
a word at a sūtra, not that a passage uses it in the glossed sense (excluding them the delta is
+483, +6.6%), and the net is +1,152 newly grounded senses against **316 relocated** to a
sibling sense of the same entry, because the aligner assigns one sense per (headword,
DCS-lemma) link. Full report:
[`PWG_DCS_TEXT_CROSSWALK_H1691.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_DCS_TEXT_CROSSWALK_H1691.md).

> **Source:** H1632 pilot join + 26-07-2026 scale-up (random + full-PWG frames,
> [PR #763](https://github.com/gasyoun/SanskritLexicography/pull/763)),
> Opus 5 (`claude-opus-5[1m]`) ·
> [`RussianTranslation/research/PWG_SENSE_DCS_ATTESTATION_PILOT.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_ATTESTATION_PILOT.md)
> + generator
> [`pwg_sense_dcs_attestation_pilot.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_sense_dcs_attestation_pilot.py)
> ([PR #755](https://github.com/gasyoun/SanskritLexicography/pull/755)); deterministic, no LLM
> in the measurement path, five inputs SHA-256 pinned. Consumes §78's successor state — the
> `m_wordsem` decode inventory recovered in H1453 — and the DCS master
> `VisualDCS/src/DCS-data-2026/dcs_full.sqlite` (the `src/` and repo-root copies are 0-byte
> decoys and were not read).
### §466. MW's `cf.` and PWG's `Vgl.` are NOT independent witnesses — they agree ~2,950× above chance, so a shared cross-reference never counts as double attestation

⚠️ **Kills a whole class of "two dictionaries agree, therefore it's real" argument.** A csl-atlas
review sheet asked a human to confirm an MW↔PWG cross-reference edge on the grounds that "both
dictionaries, **independently**, print a cross-reference … two editorial traditions made the same
link". MG rejected that outright (26-07-2026): **MW depends on PWG and PW** — Monier-Williams 1899
was built on Böhtlingk–Roth, so a shared reference can be one tradition copied, not two agreeing.

Measured rather than argued
([`m9_xref_marker_agreement.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m9_xref_marker_agreement.py)
→ [`xref_marker_agreement.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_marker_agreement.json),
full `xref_edges.csv`, normalisation shared with `m6_xref_lineage.py`, seed 20260726):

| Measure | Value |
|---|---|
| MW `cf.` edges (normalized, deduped) | 7,637 |
| PWG `Vgl.` + `s.` edges | 25,766 |
| Headwords cross-referenced in **both** | 2,750 |
| MW edges on those headwords | 3,184 |
| …whose target PWG also points to | **694 (21.8%)** |
| Expected under a degree-preserving null (200 draws) | 0.235 (**0.007%**) |
| Enrichment | **≈2,953×** |
| Null draws ≥ observed | 0/200 (p < 0.005) |

**Two traps this finding also closes.** (1) The raw containment asymmetry — 11.2% of MW's edges
appear somewhere in PWG vs 3.5% the other way, ≈3.2× — looks like directional evidence but is
almost exactly the 3.4× edge-count ratio, i.e. a **set-size artifact**. Do not cite it as showing
who copied whom; direction comes from the bibliographic record, not this statistic. (2) Enrichment
proves non-independence, **not** copying specifically: both dictionaries recording the same
language facts would also produce it. What it does establish is that the *count* of agreeing
dictionaries is not evidence you may add up.

**Reusable rule.** For any MW/PW/PWG-family corroboration claim, "N dictionaries agree" is not N
witnesses. State what a shared record actually asserts (here: the edge is *real and lexical*) and
drop the independence premise. The same caution applies to any derived dataset that scores
confidence by counting dictionaries in the Petersburg lineage.

Companion trap on the same pipeline: MW and PWG follow **opposite** headword conventions in four
cases documented by Patel 2016 (śatṛ `-at`/`-a`, vatup/matup `-vat`/`-v`, ṛ-stems `-ṛ`/`-ar`,
vas/yas `-vas`/`-vaṃs`) which the normaliser does not reconcile — so the 641-edge MW∩PWG
intersection is an **undercount**, and a ṛ-stem edge cannot intersect at all. (The pool was
quoted as 642 when this entry first landed — a `wc -l` counting the CSV header as a data
row; the packet now computes it and a docs-vs-data test pins the prose to it.) See
[XREF_SHARED_CORE_LABEL_TAXONOMY.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_SHARED_CORE_LABEL_TAXONOMY.md).

_26-07-2026 · [H1648](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1648-Opus_csl-atlas_xref-sheet-ru-and-mw-pwg-dependence_26.07.26.md) · csl-atlas [PR #310](https://github.com/sanskrit-lexicon/csl-atlas/pull/310), [v0.11.0](https://github.com/sanskrit-lexicon/csl-atlas/releases/tag/v0.11.0) · Opus 5 (1M context) `claude-opus-5[1m]`_

### §467. corpus_lexicon.jsonl gets its first intrinsic BLI quality number — and the obvious gold source (the corpus's own glossary) is circular, so the fix is an independent dictionary ranked by an independent frequency source

🔴 **`RussianTranslation/src/corpus_lexicon.jsonl` (1.09M Sa→Ru word-alignment pairs, feeds the
3-layer glossary, the translation memory, and `mw_ru`) had never been quantitatively evaluated
before H1521. First measurement, over a frozen 400-lemma gold set: P@1 = 0.402, MRR = 0.539,
coverage = 0.995 (398/400).** Ranking method: for each gold Sanskrit lemma, rank the corpus's
attested Russian renderings by raw alignment count (the file carries no per-pair weight — a
`head -1` on `corpus_lexicon.jsonl` confirmed this), then match the ranked list's top hit(s)
against the gold lemma's Russian content-word tokens (Cyrillic, ≥4 letters — a lenient
free-text-gloss-vs-single-rendering overlap proxy, not exact string equality).

⚠️ **The default gold-set choice named in the H1521 handoff turned out to be circular and had
to be overridden by inspection.** The repo's own 3-layer Sa→Ru glossary
([`glossary/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossary/README.md))
is a direct group-by/count aggregation *of*
`corpus_lexicon.jsonl` itself
([`build_surface_glossary.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_surface_glossary.py):
"Direct group-by on corpus_lexicon.jsonl ... no lemmatizer needed") — grading the lexicon
against a glossary built FROM the lexicon would score P@1 ≈ 1.0 by construction, a variant of
the [§460](#460-gold-in-this-org-means-frozen-not-human-adjudicated--0-of-15-gold-datasets-have-independent-human-annotation-and-every-travelling-κ-is-model-vs-model-four-contamination-mechanisms)
"evaluated system authored its own gold" contamination mechanism, just with a deterministic
aggregation standing in for an LLM judge. The fix used two *independent* sources instead: gold
CONTENT from Kochergina's published Sanskrit-Russian dictionary (`src/koch.jsonl`, 29,177
entries, never derived from this corpus), and the "high-frequency" SELECTION criterion from
VisualDCS's `dcs_lemma_summary.json` (Hellwig's DCS ~2021 whole-corpus frequency bands — a
different, much larger corpus than the 1.09M-pair translated subset). Both axes of
independence mattered: an earlier pass that ranked candidate gold lemmas by their own frequency
*inside* `corpus_lexicon.jsonl` produced coverage = 1.0 by construction (every selected lemma
was guaranteed present) — a second, subtler circularity that the DCS-frequency swap fixed
(coverage dropped to the genuine 0.995 above). Unlike the org's audited "gold" sets, Kochergina
is a bona fide human-scholarly source (V. A. Kochergina's printed dictionary), not an LLM
label — so this gold set's *content* provenance is stronger than most in [§460](#460-gold-in-this-org-means-frozen-not-human-adjudicated--0-of-15-gold-datasets-have-independent-human-annotation-and-every-travelling-κ-is-model-vs-model-four-contamination-mechanisms)'s
audit, though the word-overlap match criterion is still a lenient proxy, not exact-gloss
agreement.

> **Source:** [H1521](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1521-Sonnet_RussianTranslation_bli-eval-corpus-lexicon-p1-mrr_23.07.26.md),
> [`src/eval/bli_eval.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/bli_eval.py) +
> [`src/eval/build_gold_koch.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/build_gold_koch.py) +
> [`src/eval/gold_sa_ru_koch_400.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/gold_sa_ru_koch_400.tsv) —
> RussianTranslation · 26-07-2026, Sonnet 5 (`claude-sonnet-5`).
### §468. PWG's plain `R.` is a THREE-edition composite — books 3–6 carry Gorresio (Bengal-recension) numbering, so keying them into a Southern-recension text silently returns the wrong verse

🔴 **PWG's plain `R.` is not one citation scheme: books 1–2 cite Schlegel, books 3–6 cite
Gorresio's Bengal recension, book 7 the Bombay edition — so `citation_tm.py` had been
returning the wrong verse's Russian translation, silently and in-range, for ~900 R. 3/5
refs.** PWG's own bibliography (pwgbib 1.247) says it plainly: without further indication, `R.` cites
**Schlegel's edition for books 1–2** and **Gorresio's for books 3–6** (book 7 → Bombay ed.);
Cologne's scan links have always routed accordingly
([`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
sends R. 3–6 to the `ramayanagorr` viewer). But Gorresio prints the **Gauḍīya/Bengal
recension**, whose sarga divisions and verse numbers differ from the Southern/vulgate text
behind Leonov's Russian translation — so any consumer that treats an `R.` locus as
Southern-keyed for books 3–6 gets the **wrong verse**, in-range and error-free.

Empirical check (H1656, current pwg_ru store): the maximum sarga cited per book is 77 (R. 1),
115 (R. 2), **79 (R. 3), 63 (R. 4), 94 (R. 5)**, 112 (R. 6) — books 3–5 land exactly on the
Gorresio sarga counts (79 / 63 / 95) and **past** the Southern ones (75 / – / 68).
`citation_tm.py` had been resolving in-range book-3/5 loci against the Southern corpus and
returning that verse's Russian translation as a clean `hit` — ~900 refs were exposed; fixed by
returning `unmapped_locus_scheme` for books 3–6
([issue #770](https://github.com/gasyoun/SanskritLexicography/issues/770),
[PR #769](https://github.com/gasyoun/SanskritLexicography/pull/769)).

Corollary: the explicit `R. GORR.` abbreviation clusters ~98% in books 1–2 (139+230 of 375
store loci) — Böhtlingk only wrote "GORR." where plain `R.` would have meant Schlegel. So the
Gorresio↔Southern concordance is load-bearing for ~2,200 refs (657 R. GORR. + ~1,560 plain-R.
books 3–6), not 657. Reusable rule: **an `<ls>` abbreviation names a citation *scheme*, not a
text — resolve the edition per book/coordinate-range before keying into any aligned corpus.**

_26-07-2026 · [H1656](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1656-Opus_SanskritLexicography_gorresio-southern-critical-concordances_26.07.26.md) · [PR #769](https://github.com/gasyoun/SanskritLexicography/pull/769), [issue #770](https://github.com/gasyoun/SanskritLexicography/issues/770) · Fable 5 `claude-fable-5`_

### §469. `to_slp1` is case-preserving, so a capitalised IAST headword transliterates into a DIFFERENT SLP1 letter — 60% of NCC match-keys are wrong and 14,379 exact ACC×NCC matches were never proposed

🔴 **Feeding capitalised IAST into `sanskrit_util.to_slp1` silently produces a different word.**
SLP1 uses uppercase letters as distinct phonemes (`K` = kh, `G` = gh, `C` = ch, `J` = jh,
`T` = th, `D` = dh, `P` = ph, `B` = bh, `N` = ṅ, `Y` = ñ, `R` = ṇ, `E` = ai, `O` = au), and
`to_slp1` passes an uppercase ASCII initial through untouched rather than mapping it — so
`slp1_simplify` then reads that capital as the *other* letter. Non-ASCII capitals (`Ś`, `Ī`,
`Ā`, `Ṛ`, `Ṇ`, `Ṭ`, `Ḍ`, `Ṣ`, `Ṃ`) are not transliterated at all and survive verbatim into the
key. The failure is silent, produces a plausible-looking ASCII string, and has no error path:

```python
su.slp1_simplify(su.to_slp1("Rāmāyaṇa"))          # -> 'namayana'   (wrong)
su.slp1_simplify(su.to_slp1("Rāmāyaṇa".lower()))  # -> 'ramayana'   (correct)
```

⚠️ **Measured blast radius in the ACC×NCC works crosswalk**, whose
[`parse_ncc.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/parse_ncc.py)
keys off the raw (capitalised) NCC headword: **91,548 of 152,526 keys (60.0%) are wrong**,
20,571 (13.5%) still contain non-ASCII. Two opposite consequences, and the recall one is the
serious one:

| effect | measured |
|---|---:|
| Tier D rows that are actually EXACT title matches (the inserted `h` was the whole edit distance) | 40,757 of 43,666 — **93.3%** |
| exact-key (Tier A) overlap as shipped | 8,397 keys |
| exact-key overlap once the keys are repaired | **22,775 keys** |
| true matches never proposed as candidates at all | **14,379** |

The recall loss is structural, not marginal: where the corruption changes the FIRST letter,
`build_works_crosswalk.py`'s Tier D first-letter blocking and Tier C prefix bisect never
compare the pair, so no candidate row is generated for a human or an agent to adjudicate.
Every `Rāmāyaṇa`, `Yoga-`, `Ekā-` and `Ś-` initial NCC work is currently invisible to the
crosswalk. **Generalisable lesson: a normalisation bug upstream of a blocking key does not
degrade a fuzzy match, it deletes the candidate** — and the deletion is invisible downstream,
because a pair that was never proposed looks exactly like a pair that does not exist.
**✅ Fixed and re-run 26-07-2026 ([H1671](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1671-Opus_SanskritLexicography_acc-ncc-p0p1-ncc-key-repair-rerun_26.07.26.md)).**
`parse_ncc.match_key_for` now case-folds + NFC-normalizes before transliteration, pinned by
[`test_parse_ncc.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/test_parse_ncc.py).
P0→P1→P2 re-ran on the repaired keys and every prediction in the table above held to the row:
exact overlap 8,397 → **22,775**, Tier D 43,666 → **1,575** rows of which 40,757 migrated
straight to Tier A, the adjudication set fell 49,019 → 10,614, and the
`exact_after_key_repair` rule now fires **zero** times. All 3,711 candidate rows the repair
*removed* were classified and none was a true link — 1,382 were collisions the corruption
manufactured (ACC `Nāmamuktāvalī` had been matching NCC `Rāmamuktāvali`), the other 2,329 were
superseded by P1's tier partition. Before/after:
[`NCC_KEY_REPAIR_MIGRATION_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/NCC_KEY_REPAIR_MIGRATION_2026.md).

**Org-wide caller audit (H1671 deliverable 2, done 26-07-2026).** Every `to_slp1` call site in
the org was checked. The trap is real, but the blast radius outside this repo is small — and
the striking part is that the library and two of its consumers *already work around it,
silently*:

| caller | input | status |
|---|---|---|
| `sanskrit_util.iast_to_devanagari` (the library itself) | any IAST | **already defends** — calls `to_slp1(text.lower())` |
| [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) `lookup-normalize.js` `iastToSlp1()` | user lookup value | **already defends** — `.normalize("NFC").trim().toLowerCase()`, with no comment saying why |
| csl-atlas `sanskrit-util.js:155` `iastToDeva()` | any IAST | **already defends** — `.toLowerCase()` |
| [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) `app.js` `rowSlp1()` | **user-typed IAST search term** | was undefended — ✅ **fixed 26-07-2026** ([H1695](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1695-Opus_csl-apidev_rowslp1-iast-case-fold_26.07.26.md), [PR #127](https://github.com/sanskrit-lexicon/csl-apidev/pull/127)) |
| WhitneyRoots `emit_crosswalk.py` · VisualDCS `import_archive.py` / `build_lsc_pilot.py` · Uprava `titov_parametric_core.py` · SanskritGrammar `build_rq4_item_bank.py` | roots / DCS lemmas | safe in practice — these arrive lowercase, but none of them *asserts* it |
| SanskritLexicography `parse_ncc.py` | capitalised NCC headword | **was the victim; fixed** |

**Ruling: keep `to_slp1` byte-compatible; make the trap loud instead.** Lowercasing inside a
transcoder shared by ~8 repos would silently change every caller's output — the same class of
unannounced semantic change that caused this bug. What is actually wrong is that the behaviour
is *unspecified*: `to_slp1` is documented as "IAST → SLP1" with no word on case, and its tests
only ever pass lowercase, so nothing pins what a capital does. Upstream should gain a
documented case-folding entry point plus a test pinning the current passthrough — **still
unclaimed**. **Generalisable lesson: when a library's own code defends against its own
function — `iast_to_devanagari` calling `to_slp1(text.lower())` — that defence is a bug report
nobody filed.**

**Correction, 26-07-2026 ([H1695](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1695-Opus_csl-apidev_rowslp1-iast-case-fold_26.07.26.md)):
the csl-apidev row above originally read "a silent lookup miss, no corrupted data". That
understated it.** Tracing the value through `app.js` showed *both* consumers were hit:
`renderHeadword()` **displayed the wrong headword** — `Rāma` → `RAma` → rendered back as
**ṇāma**, `Bhāgavata` as `bhhāgavata`, `Ekāvalī` as `aikāvalī` — and the `dalglob|` lookup and
cache key addressed the wrong entry. Visible corruption in the results list, not a silent
miss. `IAST_RE` there deliberately auto-detects capitalised input (it lists
`ĀĪŪṚṜḶḸṂṄṆṢṬṰḌŚ`), so the path was reachable by design. Fixed by
[PR #127](https://github.com/sanskrit-lexicon/csl-apidev/pull/127): `foldIast()` (NFC +
lowercase) before transcoding, SLP1 input explicitly never folded, and a zero-dependency
`app/rowSlp1.check.js` wired into CI — because the root cause here was never the bug, it was
that nothing pinned what a capital does. **Second-order lesson: an audit that classifies a
call site by reading only the call line will under-rate it — the severity lives in what
consumes the return value.**

> **Source:** [H1657](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1657-Opus_SanskritLexicography_acc-ncc-p2-agent-adjudication-49k_26.07.26.md)
> (measurement) + [H1671](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1671-Opus_SanskritLexicography_acc-ncc-p0p1-ncc-key-repair-rerun_26.07.26.md)
> (repair, re-run, caller audit),
> [integrity issue #779](https://github.com/gasyoun/SanskritLexicography/issues/779),
> [`NCC_KEY_REPAIR_MIGRATION_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/NCC_KEY_REPAIR_MIGRATION_2026.md),
> [`P2_AGENT_ADJUDICATION_REPORT.md` §0](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P2_AGENT_ADJUDICATION_REPORT.md) —
> SanskritLexicography · 26-07-2026, Opus 5 1M (`claude-opus-5[1m]`).

### §470. The Cologne scan-viewer page PDFs can carry an embedded digitized text layer — check `get_text()` BEFORE declaring "no e-text exists" or commissioning OCR

The H1656 first pass concluded (and MG believed) that **no Gorresio Rāmāyaṇa e-text
exists** — GRETIL has none, archive.org has only scans with rough tesseract OCR. Both
true — and beside the point: the [sanskrit-lexicon-scans/ramayanagorr](https://github.com/sanskrit-lexicon-scans/ramayanagorr)
per-page PDFs (`pdfpages/rgorr_*.pdf`), sourced from **Google Books** digitizations,
carry an embedded, clean Devanagari **text layer** — a full e-text was extractable the
same day with zero new OCR (10,225 verses;
[src/gorresio_etext.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gorresio_etext.jsonl)).
Caveats that made it work, all reusable for the next edition trapped in scans:

- **Coverage follows the SCAN SOURCE, not the viewer**: only the Google-sourced volumes
  (1/3/5 — Bāla, Ayodhyā 1–9, Āraṇya, Kiṣkindhā-part, Yuddha) have the layer; the
  DLI/digitale-sammlungen volumes (2/4/uk) are image-only, and their archive.org
  tesseract `_djvu.txt` is too noisy to trust (heavy akshara confusion, no page
  separators). Per-volume check, not per-work.
- **OCR drops digits in verse numbers** (॥91॥ reads as ॥1॥), so ॥N॥ segmentation must
  be anchored to an external per-page verse-range index — here the viewer's own
  hand-made `ksverse.js` (kāṇḍa/sarga/verse-range per page) — with parsed numbers
  trusted only inside the page's known range.
- **Extraction speed**: PyMuPDF `get_text()` is ~100× faster than pypdf on these
  (0.03 s vs 3 s per page — 2,822 pages in ~90 s vs ~2.4 h).
- The uttarakāṇḍa volume is filed as `rgorr_uk.*` while the page index calls it
  volume "6" — map before fetching.

_26-07-2026 · [H1656](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1656-Opus_SanskritLexicography_gorresio-southern-critical-concordances_26.07.26.md) · [PR #784](https://github.com/gasyoun/SanskritLexicography/pull/784) · Fable 5 `claude-fable-5`_

### §471. A corpus-candidate matcher keyed on a dictionary's OWN bibliographic prose will bury its biggest wins in the "no corpus side exists" class — PWG's Pāṇini and Manu, 41,910 citations, sat in `DCS-LACKS`

🔴 **When you auto-classify a dictionary's cited sources against a corpus, never derive the
candidate from the dictionary's bibliography text.** A `Verzeichniss der Abkürzungen` names
works the way a 19th-century philologist would introduce them — by author, in the editor's
language — not by the Sanskrit title a corpus indexes them under. Match on the prose and the
most-cited authorities in the dictionary silently land in the class you have labelled
"a genuine corpus gap that no crosswalk can close", where nobody will ever look again.

`Evidence:` H1670's [`build_ls_text_crosswalk_backlog.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/build_ls_text_crosswalk_backlog.py)
classified all 4,207 PWG `<ls>` abbrevs against DCS by prefix-matching the resolved `pwgbib`
entry. PWG's entries read "PĀṆINI'S acht Bücher grammatischer Regeln" and "MANU'S Gesetzbuch
in der Ausg. von LOISELEUR DESLONGCHAMPS" — neither contains *Aṣṭādhyāyī* or *Manusmṛti*, both
of which DCS carries. So `P.` (21,305 citations, 2.88% of the dictionary's `<ls>` mass) and
`M.` (20,605, 2.79%) were filed as `DCS-LACKS`. Mapped in H1691 they contribute **827 of the
1,152 newly grounded senses** — the two largest crosswalk wins available, hidden in the class
declared untouchable.

The same generator fails the other way too, and both failures are one-line habits worth
banning outright:

- **`max(candidates, key=tokens)`** — picking the *largest* name-alike paired `SĀṂKHYAK` with
  the Sāṃkhyakārikā**bhāṣya** when DCS also carries the bare kārikā.
- **prefix-matching a name-alike at all** — six abbrevs were paired with a *different work*
  whose correct counterpart DCS also carries (`TBR` with the Taittirīya**saṃhitā** not the
  **brāhmaṇa**; likewise `KĀTY. ŚR`, `ĀŚV. ŚR`, `ŚĀṄKH. BR`, `ŚĀṄKH. GṚHY`, `TAITT. ĀR`/`UP`).
  Spelling variation defeats it as well: DCS spells the Āśvalāyana Śrautasūtra
  *Āśvālāyana*śrautasūtra, so the prefix never fired.

`So:` treat such a class as **"no name-alike was found"**, never as a fact about the corpus,
and say so in the column header. Adjudicate against the corpus's own text list, and commit the
verdicts to a sidecar the generator reads back so a regeneration cannot discard them
([`pwg_ls_dcs_scheme_verdicts.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_ls_dcs_scheme_verdicts.tsv)).
Re-classified, `DCS-LACKS` fell from 367,670 citations (49.7%) to 275,268 (37.2%) — and it is
*still* only an upper bound, because the remaining 3,735 abbrevs were not audited.

_26-07-2026 · [H1691](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1691-Opus_kosha_pwg-dcs-text-crosswalk-beyond-five_26.07.26.md) · [`PWG_DCS_TEXT_CROSSWALK_H1691.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_DCS_TEXT_CROSSWALK_H1691.md) · Opus 5 `claude-opus-5[1m]`_

### §472. Choosing a confidence tier ONCE PER SENSE and then stamping it on many passages inflates the strongest tier — 4.13% of H1670's exact-verse rows were chapter-level

🔴 **A tier is a property of a row, not of a sense.** H1670 correctly separated exact-verse
matches from chapter-level ones into `locus` (conf 0.90) and `locus-chapter` (0.70). But the
decision was taken once per sense and then applied to every passage that sense matched — and a
single sense routinely matches several passages whose addresses bottom out at different levels
(20.9% of DCS's Ṛgveda and 24.1% of its Atharvaveda sentences carry no `sent_counter` at all).

`Evidence:` 507 of the 12,280 `locus` rows in H1670's wide-frame run (**4.13%**) carried an
address with no `sent_counter` — i.e. a chapter-level address published in the exact-verse tier
at confidence 0.90. 504 were Aitareyabrāhmaṇa, which an independent containment test shows is a
chapter-level-only text for PWG's citation scheme (verse 0.3%, chapter 95.9%). Fixed in H1691
by letting the level travel with the passage: after the fix **zero** exact-verse rows carry a
counter-less address, 522 rows moved to `locus-chapter`, and the grounded-sense count is
unchanged (8,208 either way) because the fix relabels within the locus family rather than
adding or removing groundings. Wave-1 is provably unaffected — its run contains 0 such rows.

`So:` whenever a per-item confidence is derived from a per-group decision, assert the invariant
in the writer, not in the reviewer's memory. The cheap regression test is the one that caught
this: `grep` the strongest tier's rows for an address shape that tier is supposed to exclude.

_26-07-2026 · [H1691](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1691-Opus_kosha_pwg-dcs-text-crosswalk-beyond-five_26.07.26.md) · [`build_sense_corpus_concordance.py`](https://github.com/gasyoun/kosha/blob/main/scripts/build_sense_corpus_concordance.py) · Opus 5 `claude-opus-5[1m]`_

### §473. OCR the canonical page files themselves — mapping a THIRD-PARTY OCR of "the same" scan onto them loses to offset drift, thumbnail decoys, and digit aliasing

Closing the Gorresio vols-2/4/uk e-text gap (the §470 residue) looked cheapest via
archive.org's ready-made tesseract derivatives of the same physical scans (DLI vol 2,
`bub_gb` vol 4) — per-page hOCR/DjVu-XML exists and the Devanagari quality is fine. It
still lost to the direct route, for reasons that generalize to any "reuse someone
else's OCR of the same book" plan:

- **Leaf↔page offsets are NOT constant across a volume.** The DLI vol-2 copy drifts
  from +48 to +20 relative to the Cologne page files (extra/missing leaves), and in
  the drift zone the only per-page anchor — printed verse numbers — **aliases**:
  short sargas restart 1…9, 10…19, so a wrong offset still "agrees". A banded
  monotone DP found A mapping (mean agreement 0.635) but its transition zone was
  provably smeared. Vol 4 happened to be constant (+26); you can't know in advance
  which kind you have.
- **Printed page numbers in the running heads don't rescue it** — the ९↔१↔४ digit
  confusions are exactly the glyphs page numbers are made of.
- **The direct route is trivially correct by construction**: the Cologne per-page
  PDFs carry the full-resolution scan image inside (2,900×4,700 px class), so
  extracting the embedded image and running tesseract 5 `san` keys every output by
  `(vol, page)` with no mapping step at all. 1,427 pages OCRed locally in ~25 min
  (6 workers), 99–100% of pages yield verse markers; the concordance consumer
  (8-gram fuzzy matching, 0.25 floor) is insensitive to the residual noise.
  12/12 sampled new mappings verified true.
- **Two extraction traps**: (1) some pages embed a low-res THUMBNAIL alongside the
  scan — `page.get_images()[0]` silently returns it (vol 4 first-pass yield: 8% of
  pages with verse markers, vs 100% after taking the largest image by pixel area);
  (2) tesseract renders the double daṇḍa ॥ as two single daṇḍas often enough that a
  `॥N॥`-splitter loses whole verses — normalize `।।` → `॥` before segmenting.

`So:` when a canonical page-keyed store already exists, OCR **its own pages** and pay
the compute; reuse third-party OCR of "the same" edition only when you can anchor
every page independently, not via a constant offset you haven't proven. And when
mining images out of PDFs, always take the largest image on the page, never `[0]`.

_26-07-2026 · [H1689](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1689-Opus_SanskritLexicography_gorresio-vols-2-4-uk-ocr-etext_26.07.26.md) · [`build_ramayana_concordance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py) · Fable 5 `claude-fable-5`_
### §474. PWG's etymology parenthesis is NESTED — a "first `+`-chain" regex reads the inner sub-analysis, not the compound's members

🔴 **`({#akftta#} [<hom>3.</hom> {#a#} + {#kftta#} …] + {#ruc#})` is `akftta + ruc`, not `a + kftta`.**
Böhtlingk & Roth decompose a *member* inside square brackets, and they also write a *different
word's* parenthesis in the same entry head (`{#aDikazAzwika#}¦ <lex>adj.</lex> von {#aDikazazwi#}
({#aDika#} + {#zazwi#})` — those members compose `aDikazazwi`, not the headword). A regex that
takes the first `{#…#} + {#…#}` chain in the entry head therefore captures the wrong analysis,
and a "first member is a lead-compatible prefix of the headword" filter does not catch it,
because the privative `a` *is* such a prefix.

`Evidence:` a bracket-aware re-parse of every entry behind
[`SanskritGrammar/data/pwg_compound_split/`](https://github.com/gasyoun/SanskritGrammar/blob/main/data/pwg_compound_split/README.md),
joined by `L_id`: **344 of 16,738 rows (2.06%) ship an inner or a neighbouring word's chain**,
and a further 368 (2.20%) resolve to no verifiable top-level chain — 4.25% of a dataset whose
README offers it as high-precision splitter gold to kosha and SanskritSpellCheck. Issue
[SanskritGrammar#527](https://github.com/gasyoun/SanskritGrammar/issues/527).

`So:` anchor on the headword's own `{#…#}¦`, take the **balanced** paren, blank every balanced
`[...]` before splitting on `+`, and keep only the FIRST `{#…#}` of each `+`-part — what follows
it is PWG's annotation of that member (`<ab>acc.</ab> von {#agni#}`, `<lex>f.</lex> von
{#agamya#}`, `= {#loman#}`), not a second member. Reference implementation: `pwg_toplevel()` in
[`adjudicate_compound_differs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/adjudicate_compound_differs.py).

_26-07-2026 · [H1681](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1681-Opus_SanskritLexicography_pwg-compound-differs-b2-full-queue-adjudication_26.07.26.md) · Opus 5 1M `claude-opus-5[1m]`_

### §475. MW's `<k2>` carries a variant LIST after `;` and two different boundary marks — stripping the punctuation welds variants into a member that is not a word

🟠 **`gaRa—kAri; gaRakAri` is one compound written twice, not a three-member compound.**
MW `<k2>` uses `—` (em-dash) for a member boundary and `-` (hyphen) for a juncture where MW
deliberately does *not* put one (`a-kAma—karSana` = the privative bound to member 1). It also
lists spelling/accent variants inside the same field, separated by `; `. Splitting on the
em-dash first and stripping punctuation second fuses the variants: `mw_compounds._clean_member`
removes `;` **and the space**, so `gaRa—kAri; gaRakAri` yields the member `kArigaRakAri`.

`Evidence:` 41 of 106,603 MW compound records (0.04%) — small, but each produces a member string
that is not a Sanskrit word and an arity that is wrong, which then propagates into
`compound:N_members` and the Zaliznyak `+N` index (`citpati` shipped as 3 members). Issue
[SL#801](https://github.com/gasyoun/SanskritLexicography/issues/801).

`So:` split `<k2>` on `;` first and take the first variant, then on the em-dash. Keep the hyphen
rather than stripping it — it is MW stating where a boundary is *not*, which is usable evidence
when reconciling MW's segmentation against another dictionary's.

`✅ FIXED 26-07-2026` (H1703, [PR #817](https://github.com/gasyoun/SanskritLexicography/pull/817),
[v1.87.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.87.0)) — with one
correction to the `So:` above: take the first variant that **carries the segmentation**, not
simply the first variant. MW sometimes lists the unsegmented spelling first
(`gaRakAri; gaRa—kAri`), and "first variant wins" silently drops those records instead of
fixing them. All 41 records corrected (22 arity-corrected); `--selftest` pins the case.
The hyphen is still stripped in `mw_compounds.py` — only the adjudicator's `mw_variants()`
keeps it — so the second half of this finding remains open, deliberately: changing the member
spelling downstream is a bigger change than the defect warranted.

_26-07-2026 · [H1681](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1681-Opus_SanskritLexicography_pwg-compound-differs-b2-full-queue-adjudication_26.07.26.md) · Opus 5 1M `claude-opus-5[1m]`_

### §476. Repairing an extractor GROWS the disagreement queue it feeds — plan for that, not for a shrink

🟠 **Two upstream repairs were expected to shrink a 4,123-card PWG-vs-MW disagreement queue.
They grew it by 3 %.**
A repair does two things at once: it removes rows that only disagreed because of the defect,
and it *adds* rows that were previously absent or unresolvable and now produce a real
comparison. The second effect is easy to forget when writing the plan, because the defect is
what you are thinking about.

`Evidence:` after [SanskritGrammar#527](https://github.com/gasyoun/SanskritGrammar/issues/527)
(PWG chain now headword-anchored: 512 rows dropped, **879 added**) and
[SL#801](https://github.com/gasyoun/SanskritLexicography/issues/801) (MW variant fusion),
the `differs` queue moved 4,123 → **4,246 cards**: 118 left, 241 entered (163 brand-new PWG
comparisons, 74 that previously had no PWG chain, 4 from `agrees`). The defect strata did
vanish as predicted — `pwg_layer_inner_chain` 75 → 0, `pwg_layer_no_headword_paren` 82 → 2,
`mw_variant_fusion` 10 → 0 — so both halves of the prediction were individually right and the
net was still the wrong sign.

`So:` when a handoff says "land the repair first, the queue will shrink", treat the shrink as
an unmeasured assumption, and re-derive the queue before sizing any human sample against it. A
blind arm drawn against the pre-repair queue keeps its value in the strata that survive, but
some of its cards will have left the queue entirely (9 of 200 here) — count them and say so
rather than reporting the arm at full size.

_27-07-2026 · [H1703](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1703-Opus_SanskritLexicography_compound-differs-second-arm-and-sheet-binding_26.07.26.md) · Opus 5 1M `claude-opus-5[1m]`_

### §477. 35 cards is the floor for a 0.90 Wilson gate — and a censused stratum needs no interval at all

🟡 **`wilson_lower(35, 35) = 0.9010`; `wilson_lower(34, 34) = 0.8983`.**
When promotion is gated on a per-stratum Wilson-95 % lower bound ≥ 0.90, a stratum sampled with
34 cards cannot clear the gate *even if the human agrees with every single card*. Sizing a
review arm at "about 30 per stratum" therefore buys nothing: the votes are spent and the
stratum still cannot promote.

`Evidence:` the H1628 arm put 16, 11, 10, 10, 1 and 0 cards into six of eight strata — every
one of them unpriceable at the 0.90 gate, capping promotion at 3,018 of 4,226 rows however the
human voted. Re-drawing at 35/stratum lifted all of them past 0.90 (0.901–0.906) for 232 cards
of human time.

`So:` derive the per-stratum floor from the gate before drawing, not after. And note the
corollary that is easy to miss: **a stratum small enough to census does not need an interval
at all** — if every row in it carries a human vote there is nothing to extrapolate to, so it
promotes by census while its Wilson bound is still below the threshold. The 31-row
`granularity_ic_vs_full_decomposition` stratum promotes on `promotion_basis: census` with a
bound of 0.890; reporting it as "unpromotable" because 0.890 < 0.90 would be wrong.

_27-07-2026 · [H1703](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1703-Opus_SanskritLexicography_compound-differs-second-arm-and-sheet-binding_26.07.26.md) · Opus 5 1M `claude-opus-5[1m]`_

### §478. A blind arm stratified on an agent's own rules must not render the rule — and its card ids must come from the lock, not the frame

🟠 **Stratifying a verification sample by the agent's classification is right; showing that
classification on the card destroys the thing being measured.**
An arm exists to price the agent. If the card displays the stratum, the rule, the verdict or
the reason, the human is being asked to agree with a labelled claim rather than to judge the
evidence, and the resulting precision is unmeasurable.

`Evidence:` the H1703 arm is stratified on the H1681 rule ladder (`mw_cut_leaves_nonword`,
`pwg_lexeme_vs_mw_suffixed_tail`, …). Those names are self-fulfilling as prompts. The card
therefore carries only the two member lists, the source PWG parenthesis, the source MW `<k2>`
and neutral badges (length, DCS frequency, member-count class); the stratum, rule and verdict
live in the frame TSV. A selftest asserts no card JSON contains any of them.

`So:` two rules for any blind arm built on top of an agent pass — (1) the sampling key never
appears on the voting surface, and it is worth pinning that with a test rather than a comment,
because the natural way to build a card is to reuse the row dict that already carries the
label; (2) take the arm's card ids from the **committed lock**, not the frame TSV. The lock is
what `validate_decisions.py` checks the human's export against, so it is the only list that can
actually pay out — an unbound sheet must count as pricing nothing rather than silently falling
back to its frame, which is how the unbound-sheet defect (H1703 item 1) stayed invisible until
someone went looking.

_27-07-2026 · [H1703](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1703-Opus_SanskritLexicography_compound-differs-second-arm-and-sheet-binding_26.07.26.md) · Opus 5 1M `claude-opus-5[1m]`_

### §479. PWG's etymology parenthesis: "first `{#…#}` per `+`-part" is right until PWG writes a derivation ladder

🟡 **`(von {#BAnumant#} oder von {#BAnu#} + {#mati#})` — first-wins ships `BAnumant`, but the
compound is `BAnu + mati`.**
Extracting PWG's member chain needs three rules, and only the first is obvious. (a) Blank every
balanced `[...]` — PWG nests a member's own sub-analysis there. (b) Within a `+`-part, the
member is normally the *first* `{#…#}`; what follows is PWG's annotation of it
(`{#agnim#} <ab>acc.</ab> von {#agni#}`, `{#Sira#} = {#Siras#}`). (c) But PWG also writes
disjunctions and derivation ladders inside a part — `von X oder von Y`,
`von X und dieses von Y` — where the first `{#…#}` is a *base*, not a member.

`Evidence:` over the whole of `pwg.txt`, 1,564 `+`-parts carry more than one `{#…#}`: 1,056
`von`-annotations and 252 `=`-glosses where first-wins is correct, against ~357 ladders and
disjunctions where it is not. Settling the ambiguous ones against the headword's surface —
first-wins if the members account for the headword within ±1 char per seam, else the unique
candidate chain that does, else **drop** — resolves `BAnumatin` → `BAnu + mati` correctly and
drops `DvajAgravatI` (a *derivative* of a compound: nothing composes it, so it is not surface
segmentation gold at all). Also measured: PWG's analysis paren does **not** always sit
immediately after the headword's `¦` (`{#BUsuta#}¦ 1〉 <lex>m.</lex> ({#BU#} + {#suta#})`), so
requiring adjacency loses ~2,500 correct rows; accepting it across annotation-only material,
and across a citation or gloss only when the chain composes the headword, keeps them without
re-admitting the neighbouring-word defect.

`So:` do not treat "first `{#…#}` per part" as the whole rule, and never guess when a part is
ambiguous — drop and count by reason. The extractor
([`pwg_compound_split.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/scripts/pwg_compound_split.py))
and the adjudicator
([`adjudicate_compound_differs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/adjudicate_compound_differs.py))
must stay in sync on all of this: if they disagree about what PWG says, the PWG-vs-MW queue
measures the extractors instead of the dictionaries.

_27-07-2026 · [H1703](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1703-Opus_SanskritLexicography_compound-differs-second-arm-and-sheet-binding_26.07.26.md) · Opus 5 1M `claude-opus-5[1m]`_

### §480. A non-empty PDF text layer proves nothing — check the SCRIPT; and "extract the largest embedded image" breaks when the PDF CROPS a 2-up scan

🔴 **§470 and §473 were both written off one edition's page PDFs (ramayanagorr) and both
mis-fire on the next one (ramayanabom).** The recipes are still right; what was missing is
the check that tells you which branch you are on. Two traps, each of which silently
produces plausible output:

- **The text layer is a decoy.** Every `pdfpagesv3/ram-III-NNN.pdf` returns 1,100–2,300
  characters from `page.get_text()` — a §470 check keyed on "is `get_text()` non-empty?"
  passes with room to spare. The characters are Latin:
  `*kitihtell18.1b1,1111qhMakkhd-lie Ifkkt12111414A 11W,Ilkihk11/1111 II`. Google's
  digitisation OCRed this Devanagari page with a Latin-alphabet model, and the result is
  embedded as a real, searchable text layer. **So: §470's check is on the SCRIPT of the
  returned text, not its length** — one `re.search(r'[ऀ-ॿ]', txt)` is the whole
  fix, and without it a session concludes "e-text recovered, zero OCR needed" and ships
  noise.
- **The largest embedded image can be the WRONG UNIT.** §473 says take the largest image
  by pixel area, never `get_images()[0]` — correct, and still insufficient. Each page here
  is 1128×420 pt (pothi/landscape, aspect 2.69) but embeds a single 4700×3500 image
  (aspect 1.34) that is a **2-up scan of two printed pages**, which the PDF crops in half.
  Extracting it yields two pages of text keyed to one page number, and nothing errors.
  Verified by geometry (image aspect = exactly half the page aspect) and by rendering.
  **So: when the embedded image's aspect ratio does not match the page rect's, the PDF is
  cropping — render the page (`get_pixmap(dpi=…)`) and let the crop apply.** Here
  `dpi=300` is native resolution, so rendering costs no fidelity.

Corollaries measured on the same volume, all reusable: `ram-III-NNN.pdf` **is** printed
page N (offset 0, verified visually at pp. 505 and 810); the index's folio column
**restarts at 1 for each kāṇḍa** inside a volume, so a volume-wide page→folio map is ~250
folios out at the tail; a commentary edition prints **three verse-numbered zones per page**
(commentary above, mūla, commentary below), so a whole-page `॥N॥` split multiplies the
verse count (14 markers vs 3 in the mūla band on p. 600; 22 vs 1 on p. 700) and word-height
filtering under `--psm 6` does not separate them — tesseract merges lines across zones on a
wide layout; and resolution is **not uniform** across a volume (most pages DeviceGray/JBIG2
at 4700×3500, some sepia DeviceRGB JPEG at half that, which OCR to nothing unbinarised).

_27-07-2026 · [H1705](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1705-Opus_SanskritLexicography_ramayana-bombay-book7-etext_26.07.26.md) · [`pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md) · Opus 5 1M `claude-opus-5[1m]`_

### §481. A corpus file's PRESENCE is not evidence of its contents — `07_ramayana-uttarakanda.jsonl` is Sanskrit-only CRITICAL-edition text under a "Southern/Leonov" label, and a handoff was minted off the filename

🔴 **H1705 was written on the sentence "the corpus HAS `07_ramayana-uttarakanda.jsonl`, so
the missing piece is the Bombay-numbering bridge, not the RU side."** The file exists. Both
inferences from its existence are false, and the code that consumes it already said so —
[`citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py)
carries a comment stating that no Russian translation of kiṣkindhā, yuddha or uttara exists
at all. The handoff was minted off a directory listing; the contradiction sat one `grep`
away.

| check | kāṇḍas 1 / 2 / 3 / 5 | kāṇḍa 6 | kāṇḍa 7 |
|---|---|---|---|
| `sa` segments | 2,268 / 4,307 / 2,447 / 2,859 | 4,436 | 2,690 |
| `ru` segments | **same count, fully paired** | **0** | **0** |
| rows identical to the DCS critical ed. (same `sarga.verse`) | 1.2–3.0% | **99.8%** | **99.9%** (95.5% at score 1.0) |

So kāṇḍas 6–7 were ingested from a different source than 1/2/3/5 — they are the Baroda
critical text, carrying a label ("Southern", the Leonov translation-of-record keying) that
is true of the other four. Two consequences beyond the wasted handoff: the committed
`ramayana_southern_critical_concordance.tsv` is, for those two kāṇḍas, **a text aligned
against itself** — its 99.8%/99.9% agreement is not evidence that the recensions agree; and
any consumer treating `06`/`07` as vulgate-keyed inherits a silent recension swap of the
kind §468 documents for R. books 3–6.

`So:` **before planning work against a corpus asset, measure the asset, not the manifest** —
segment counts per language, and an identity check against whatever else claims to be the
same text. Both are one pass over the file. The generalisable form: a filename, a manifest
row and a directory listing are all *claims*; a handoff premised on one of them without a
read is a handoff premised on nothing. Related: §471 (a class label that is a fact about
the matcher, not about the corpus), §472 (a tier decided once per group and stamped on
rows).

Integrity issue: [SL#822](https://github.com/gasyoun/SanskritLexicography/issues/822).

_27-07-2026 · [H1705](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1705-Opus_SanskritLexicography_ramayana-bombay-book7-etext_26.07.26.md) · [`pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md) · Opus 5 1M `claude-opus-5[1m]`_

### §482. A count column with no stated provenance is not data — it is a ranking, and the difference decides whether you may divide by it

🔴 **The PWG scan-index tracker's `Citation count` column reproduces no extraction that
exists in this org.** Measured against the full-dictionary `<ls>` extraction
([`sortedcrefs.txt`](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_dhaval/abbrvwork/abbrvoutput/sortedcrefs.txt),
9,321 cleaned citation strings, 344,229 occurrences) the sheet/extraction ratio spreads
from **1.2× to 433×** with a median of 2.09×, and a leading-abbreviation rollup does not
close it either. The two count different objects: the extraction keys on a *cleaned
citation string* (canto and śloka numbers stripped, section letters kept — so `MED.`,
`MED. k.`, `MED. im ŚKDR.` are three keys for one book), the sheet keys on a *book*.

| `<ls>` code | sheet | bare-string occurrences | ratio |
|---|--:|--:|--:|
| `MED.` | 12,990 | 30 | 433× |
| `H. an.` | 9,781 | 1,907 | 5.1× |
| `NAIGH.` | 1,477 | 1,227 | 1.2× |

**The temptation this kills.** With the campaign's indexed mass at 197,876 and a
dictionary-wide total of 344,229 sitting right there, "**57.5 % of PWG's citations are now
page-indexed**" writes itself — a clean, quotable, and entirely unsupported headline,
because numerator and denominator come from different counting rules. The published report
carries a coverage-of-the-tracked-set figure instead (73.7 %), states the denominator it is
*not* using, and records the provenance question as open.

`So:` **a count you did not derive is usable for ORDER and unusable for RATIO until its
provenance is written down.** Ranking only needs monotonicity, which survives an unknown
scale factor; any percentage needs numerator and denominator to count the same object,
which an unknown scale factor destroys. The test is one question — *what would I have to
believe for this division to be valid?* — and when the answer is "that two numbers I
cannot reconcile measure the same thing", the division does not get published. Do not
paper the gap over with a plausible mechanism either: "book vs abbreviation" explains a
2× ratio, not a 433× one, and offering it as *the* explanation would have converted an
open question into a false answer. Related: §481 (a filename is a claim, not a
measurement), §471 (a label that is a fact about the matcher, not the corpus).

Registry, report §6.2 and the full ratio table:
[csl-observatory `data/pwg_scan_index_tracker/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data/pwg_scan_index_tracker).
The provenance question is an open MG `@DECIDE` in
[GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) — it needs whoever
built the column, not more computation.

_27-07-2026 · [H1706](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1706-Opus_csl-observatory_pwg-scan-index-tracker-reuse_26.07.26.md) · Opus 5 1M (`claude-opus-5[1m]`)_

### §483. A resolver that fails closed is a gap; one that fails *open* is a wrong answer — and only the second is an integrity defect

🔴 **A Ṛgveda-Prātiśākhya citation in PWG does not fail to resolve — it resolves to an
Ṛgveda *hymn* anchor.** Auditing which of the 37 scan directories the citation resolver is
wired to, 36 came back fine and one came back worse than missing:
[`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
contains the string `rvps` zero times, and the only Prātiśākhya-shaped pattern routes to
the `rvlinks` hymn pages. So the reader is handed a link to a different text, silently.
The undotted `RV. PRAT.` spelling reaches the same wrong place by a second route, emitting
a `rv00.*` mandala-00 URL that does not exist.

Four further codes were found failing **closed** in the same audit (`TS.` and `TBR.`
resolve only at 4-parameter arity, `PANCAR.` only at 3; `amara_col` is reachable only via
`COL.`, never from a bare `AK.`), plus 38 of 90 prefix-map values whose dispatch branch can
never fire. Those are backlog. The Prātiśākhya case is not.

`So:` **when auditing a resolver, sort the misses by failure direction before sorting them
by frequency.** A `None` is visible to the caller and costs a missing link; a
plausible-looking URL to the wrong text is invisible and costs the reader's trust in every
other link on the page. The audit that finds both should escalate only the second — and
should assert the emitted *host and path*, not merely "not None", or the test suite will
happily bless the wrong answer. Errors here are swallowed by design
(`_warn_swallowed`, suppressible with `LS_RESOLVER_QUIET=1`), which is exactly why the
defect survived until an outside pass looked.

Method: the module was imported and `generate_href()` called for ~110 probe citations
across every tracked code at every plausible arity, each result classified with the
resolver's own `link_type()` — not read off the source. The canonical
[`csl-app/lib/core/ls_service.dart`](https://github.com/sanskrit-lexicon/csl-app/blob/main/lib/core/ls_service.dart),
of which this file is a port, was **not** audited; fixing only the port would leave the
app wrong and create fork drift.

Integrity issue: [SL#826](https://github.com/gasyoun/SanskritLexicography/issues/826) ·
fix shipped [H1714](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1714-Sonnet_SanskritLexicography_ls-resolver-rvps-mislink-wiring-fix_27.07.26.md) ([PR #840](https://github.com/gasyoun/SanskritLexicography/pull/840)) ·
per-directory table: [`scan_target_audit.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/scan_target_audit.tsv).

_27-07-2026 · [H1706](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1706-Opus_csl-observatory_pwg-scan-index-tracker-reuse_26.07.26.md) · Opus 5 1M (`claude-opus-5[1m]`)_

### §484. A quarter of the DCS nominal mass has no case at all — `feat_case='Cpd'` is a compound member, not a ninth case

🔴 **NOUN + ADJ = 2,996,410 tokens; only 2,263,192 (75.5%) carry a case. 724,676 (24.2%) are
`feat_case='Cpd'`, and 8,542 (0.3%) carry no case tag.**
`Cpd` marks a token's membership in a compound, where it is caseless by construction; 733,218
NOUN/ADJ tokens likewise have `feat_number IS NULL`, almost exactly the same set. So a "case
distribution over the DCS nominals" is wrong in both directions: include `Cpd` and a quarter of
the mass is counted as a case it does not have; drop it silently and the reader is shown 75.5%
of the nominal layer as if it were all of it.

`Evidence:` the H1472 nominal grid, built over the pinned master (`04e0778`). Per-class the
share varies sharply — `-a` 512,037 `Cpd` against 1,467,730 cased (25.9%), `-in` 5,115 against
47,676 (9.7%) — so the correction is not a constant that can be applied after the fact.

`So:` state the three buckets and assert they sum to the universe. Any nominal slice owes
`grid + Cpd + untagged == COUNT(*)`; a query that returns only the grid has not measured the
nominal layer, it has measured the case-bearing part of it. The same discipline that makes
E46's verbal cells honest applies here — and the assertion is not decorative: it is what caught
a NULL-logic complement silently dropping the 8,542 untagged tokens from *both* sides of the
split (the infra form of that trap is [Uprava FINDINGS §218](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)).

_27-07-2026 · [H1472](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1472-Opus_VisualDCS_nominal-paradigm-case-number-dashboard_22.07.26.md) · [`reports/paradigm_nominal_build.md`](https://github.com/gasyoun/VisualDCS/blob/main/reports/paradigm_nominal_build.md) · Opus 5 1M `claude-opus-5[1m]`_

### §485. The 2021-sourced "Nom.Sg = 34.6% of nominal forms, dual < 1% everywhere" does not reproduce on DCS-2026 — and the second half only survives read per cell

🟡 **Measured on the 2026 master over the 2,263,192-token cased grid: Nom.Sg = 761,605 =
33.7%. Dual pooled across all eight cases = 46,909 = 2.07%; the largest single dual cell
(Nom.Dual, 20,590) = 0.91%.**
Both numbers have been quoted for a year from a 2021 `cs.csv` note carried in VisualDCS'
`roadmap.md` and re-printed on its landing page. The first does not reproduce. The second
reproduces only under the per-cell reading — pooled, the dual is more than twice the claimed
ceiling, and "dual < 1%" is the kind of claim a reader will apply to the category, not the cell.

`Evidence:` recomputed 27-07-2026 in the H1472 build report, denominator stated explicitly.
The residual gap on the first figure is not diagnosed here: the 2021 note does not say whether
its denominator included `Cpd` members (§482), and no attempt was made to reconstruct the 2021
computation — so this is a non-reproduction, not a refutation of the 2021 number on its own
terms.

`So:` a corpus statistic quoted without its denominator is not re-checkable, and one quoted
across a corpus vintage is not portable. When re-printing an inherited figure, restate the
denominator and the vintage or drop the figure.

_27-07-2026 · [H1472](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1472-Opus_VisualDCS_nominal-paradigm-case-number-dashboard_22.07.26.md) · [`reports/paradigm_nominal_build.md`](https://github.com/gasyoun/VisualDCS/blob/main/reports/paradigm_nominal_build.md) · Opus 5 1M `claude-opus-5[1m]`_

### §486. Before OCR-ing a library scan, check whether the library already published its OCR — and measure against it rather than guessing

🔴 **The Bayerische Staatsbibliothek publishes per-page hOCR for every page it scans, and
it is 2.5× better than what tesseract 5 `san` produces locally.** H1715 was written to OCR
two 19th-century Sanskrit kośa editions from the `sanskrit-lexicon-scans` page images. The
scans genuinely carry no text layer (0 chars, 0 fonts, one embedded JPEG per page — checked
by [[§480]]'s script-test, not by length). But the OCR did not need doing: every canvas in
the BSB IIIF manifest carries a `seeAlso` pointing at
`https://api.digitale-sammlungen.de/ocr/<bsb_id>/<n>`, full hOCR with word-level bounding
boxes, free.

| engine, same 12 pages, same metric | tokens | valid Sanskrit | rate |
|---|--:|--:|--:|
| tesseract 5 `san`, local | 658 | 117 | **17.8 %** |
| BSB's published per-page hOCR | 722 | 316 | **43.8 %** |
| _control — reference text through the same tokenizer_ | 1,071 | 1,071 | _100.0 %_ |

The metric is a **valid-token rate**, not a CER: the share of extracted Devanagari tokens
that are real Sanskrit words, scored against the same work's already-digitized e-text in
`csl-orig` (`abch` + `acph` + `acsj`) plus MW headwords. That instrument cost nothing and
needed no hand transcription — which matters, because 1839/1847 Devanagari with archaic
orthography is not material one can transcribe reliably enough to serve as ground truth,
and a CER asserted off an unreliable transcription is worse than no CER.

An 18-configuration sweep (dpi × psm × {raw, Otsu, aggressive threshold}) topped out at
30.5 % — and that configuration scored higher only by emitting half as many tokens. The low
rate is the material, not the settings: show-through from the reverse leaf is visible on
every page of the 1847 printing, and thresholding it away removes ink with it.

`So:` **three rules, in order.** (1) A scanned book has a provenance chain — repo →
digitising library → IIIF manifest — and the manifest is a *machine-readable* claim about
what else the library ships. Read it before generating what it already gives you; two HTTP
calls settled a question a week of OCR would have answered worse. (2) When two engines are
in play, an *existing e-text of the same work* is a free comparison instrument even when it
is a different edition — the absolute level is conservative, but scoring both engines
against the identical reference makes the comparison sound. (3) Report the metric you
actually computed. "Valid-token rate, n=12 pages, edition-variant caveat stated" is
publishable; a CER invented from a transcription one cannot vouch for is not.
Related: [[§480]] (test the script of `get_text()`, not its length), §473 (the OCR recipe
this supersedes for library-scanned material), §59 (the prior-art check that catches this
class).

Verdict, report and the reproducible probe:
[csl-observatory `reports/pwg_kosa_etext_pilot.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_kosa_etext_pilot.md)
· [`scripts/pwg_kosa_ocr_probe.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_kosa_ocr_probe.py).
Re-scoped execution: [H1720](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1720-Sonnet_csl-observatory_pwg-kosa-bsb-hocr-ingest-align_27.07.26.md).

**Provenance to carry, not a gate.** The page images are the Bayerische
Staatsbibliothek's (`bsb10250868`, `bsb10250953`), and both scan repositories already
credit the library in their own `app1/info.html` — derived artifacts keep that credit.
Publication of everything derived from them was ruled open on 27-07-2026; there is no
rights gate on this line of work.

_27-07-2026 · [H1715](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1715-Opus_csl-observatory_pwg-kosa-etext-pilot-amara-abhidhana_27.07.26.md) · Opus 5 1M (`claude-opus-5[1m]`)_

### §487. A cross-scheme join is a transliteration step, not a string comparison — a naive IAST-to-SLP1 match selects on diacritics

🟠 **Joining an IAST-spelled root list straight onto SLP1 lemma keys matched 29 % of the
catalogue and inflated the answer by 26 points — because the matches are exactly the
diacritic-free roots, which are frequency-enriched by construction.**

Measuring PM6 (how much of the Талмуд's 745-root Приложение 1 the Zaliznyak on-ramp's four
taught ablaut rows actually cover) needs the catalogue joined to kosha's
[`lemma_frequency.tsv`](https://github.com/gasyoun/kosha/blob/main/data/frequency/lemma_frequency.tsv)
for token counts. The catalogue spells roots in **IAST** (`akṣ`, `īṅkh`, `ṛt`); the frequency
table keys on **SLP1** (`akz`, `INK`, `ft`). A direct string join runs without error and
returns a plausible-looking 218 of 745 roots — and reported the on-ramp's rows as carrying
**82.7 %** of verb-root token mass.

Through the canonical [`sanskrit_util.to_slp1`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py)
the same join matches 616 of 745 and the answer is **56.2 %**. The naive join was off by
**+26.5 points** — and in the direction that flatters the deliverable.

`Why:` the direct join is not a random sample of the catalogue. IAST and SLP1 coincide
**exactly on the roots that contain no diacritic** — so the join silently selects the
ASCII-spellable subset (short, old, high-frequency roots: `yat`, `vat`, `kal`) and discards
every retroflex, long vowel and syllabic liquid. The surviving sample is frequency-enriched
by construction, so any token-weighted statistic computed over it is biased upward. Nothing
in the run signals this: no exception, no empty result, a 29 % match rate that reads as
"partial coverage, as expected" rather than "systematically the wrong 29 %".

`So:` **a cross-scheme join is a transliteration step, never a string comparison** — route
every one through the canonical converter, and *report the join rate next to the result*
(the number that would have exposed this was 29 % vs 82.7 %, printed side by side). The
general form: when a join key can be spelled two ways and one spelling is a subset of the
other's character set, silent non-matches are **selection on that character set**, not
random loss. Sanity-check by asking what the unmatched rows have in common — here, a single
glance at `akṣ`/`īṅkh`/`ṛt` versus `yat`/`kal` answers it.

Related: §59 (the prior-art check — the converter already existed and
[`build_rq4_item_bank.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/TolchelnikovTalmud_2026/tools/build_rq4_item_bank.py)
already imported it for this exact catalogue).

Committed as a reproducible probe with the trap in its docstring:
[`measure_onramp_scope.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/TolchelnikovTalmud_2026/tools/measure_onramp_scope.py).

_27-07-2026 · [H1476](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1476-Opus_SanskritGrammar_pedagogy-aspect-measurable-result-metrics_22.07.26.md) · Opus 5 1M (`claude-opus-5[1m]`)_

### §488. DCS stem co-occurrence graph is extreme-sparse with function-word hubs

🟠 **The full Sanskrit-stem co-occurrence table (dcs-stem-cooccurrence-full) is a directed L/R adjacency list over 176,676 stems (353,352 directed rows): 57.2% of directed rows have degree 0, median degree is 0, mean ~9.2, and the degree tail is dominated by function words (ca, 	ad, eva, iti, 	u, api).** Class A.

Evidence: Tab-separated file VisualDCS/derived-data/Sochetaemost-sanskritskih-osnov/NEW/1-222342.csv (36.3 MB). Schema per row: id \t stem \t L|R \t degree \t (partner_id \t count)*. Counts on 27-07-2026 (H1735, Grok 4.5 grok-4.5):
- directed rows = 353,352; unique stem ids = 176,676; sides L=R=176,676 (every stem has both left and right rows)
- degree-0 rows = 202,049 (57.18%); degree buckets: 0→202049, 1→69410, 2–5→42817, 6–20→20854, 21–100→12450, 100+→5772
- min/p50/p90/p99/max degree = 0 / 0 / 7 / 173 / 20,984; mean = 9.198; partner-edge slots (sum of pairs) = 3,250,000
- top degrees: ca L 20984 / R 18929; 	ad L 13160 / R 12728; eva L 8899; iti L 8830; 	u L 7763; api L 7587

Implication: any collocation / distributional-semantics claim over this table must down-weight or remove the function-word hub set; the typical stem has **no** recorded partner on a given side. Do not treat the table as a dense network. Reproducible with a stdlib TSV pass over the path above.

> **Source:** graduates [GAPS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) · manifest dcs-stem-cooccurrence-full · [VisualDCS](https://github.com/gasyoun/VisualDCS) · H1735 · 27-07-2026 · Grok 4.5 (grok-4.5)

### §489. Sintagmatic appendix-6 is a 6.3k-lemma core nested in the 80k all-corpus table

🟡 **DCS syntagmatic appendix 7 (all-corpus) has 79,985 lemmas; the seven period files of appendix 6 cover a 6,338-lemma union that is almost entirely nested in appendix 7 (6,337/6,338), while period-to-period lemma Jaccard is low (1∩3=0.23, 1∩7=0.17, 3∩7=0.30).** Class A.

Evidence: VisualDCS/derived-data/Lexical-Cores/Prilozhenie-7-…/DCS_Sintagmatic.csv — 82,800 lines / 79,985 distinct lemmas; row schema lemma;n1;n2;collocate count;… with collocate-list length min/median/max = 1 / 3 / 6,795. Top lemmas by col1: ādi 5252, mahat 4637, rājan 4526, artha 4328, deva 3989. Appendix-6 period files (1.csv…7.csv) lemma counts: 1823, 2226, 2259, 3300, 2961, 3359, 2387 — each period’s lemmas ⊆ appendix 7 except 1 stray form per some files. Period-only outside s7 = 1; s7-only = 73,648.

Implication: appendix 6 is a **frequency-core slice by historical period**, not an independent collocation inventory. Diachronic collocation drift must be measured on the **intersection** of period cores (thousands of lemmas), not on the full 80k. The UTF-16LE Sinonimy twin remains a byte-duplicate family (H291), not a second analysis surface.

> **Source:** graduates [GAPS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) · manifest dcs-sintagmatic-appendix7 / dcs-sintagmatic-appendix6-periods · [VisualDCS](https://github.com/gasyoun/VisualDCS) · H1735 · 27-07-2026 · Grok 4.5 (grok-4.5)

### §490. Heritage×kosha form intersection agrees 78.3%; disagreements are classifiable

🟠 **On the 94,264-form Heritage∩kosha intersection, 78.26% agree on lemma and 21.74% (20,496) disagree; disagreement classes are genuine-or-ambiguous 12,905 (63.0%), stem-granularity 7,132 (34.8%), 
asal-variant 459 (2.2%), with participles the largest Heritage category among disagreements (8,289).** Class A (re-derive from committed TSV + stats JSON).

Evidence: re-counted SanskritLexicography/HeadwordLists/heritage_forms_oracle_disagreements.tsv (20,496 data rows; header form_slp1, flag, heritage_stems, kosha_lemmas, heritage_category, kosha_sources, disagreement_class) matches committed heritage_forms_oracle_stats.json exactly. Broader context from the same stats: Heritage 1,022,526 distinct forms / kosha 409,978; intersection 94,264; Heritage-only 928,262; kosha-only 315,714; kosha coverage by Heritage 22.99% (25.4% after nasal normalisation).

Implication: Heritage is usable as a third morphology witness for **agreement-class forms** and for its huge Heritage-only surplus, but the 21.7% disagree set needs class-aware handling — stem-granularity and 
asal-variant are mostly mechanical, genuine-or-ambiguous needs human/lexicographic adjudication. Rate-only FINDINGS are publishable under restricted tier; row dump stays restricted (LGPLLR pending).

> **Source:** graduates [GAPS §9](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) · [heritage_forms_oracle_stats.json](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle_stats.json) · H1735 · 27-07-2026 · Grok 4.5 (grok-4.5)

### §491. Verb-form frequency prelim is an unlabeled 42-row XLS with empty tense names

🟡 **The file registered as dcs-verb-form-frequency-prelim is OLE2 Excel (magic d0cf11e0), mis-suffixed .csv, with 42 data rows whose Tense/Mood column is entirely empty — only numeric IDs 1–42 and frequencies (sum 781,618; max 233,080 on ID 19; four IDs at frequency 0). It cannot be finalised as a labelled tense/mood frequency table without recovering the ID→label legend from an external source.** Class A.

Evidence: VisualDCS/derived-data/Glagolnye-formy/Частота появления глагольных форм в корпусе (Предварительные данные).csv opened via xlrd (sheet «Лист1», 43×3). Header: ID | Tense/Mood | Частота появления в корпусе. All 42 Tense/Mood cells blank. Zero-frequency IDs: 17, 18, 31, 34. Sibling folder has richer verb-form DBs (Bazadannyh-glagolnyh-form-Korpusa/, class lists) that are **not** this prelim table.

Implication: keep the manifest preliminary marker; do not feed this table into a freq-first translation queue until the legend is recovered (or rebuild frequencies from the full verb-form database with explicit tense tags). The gap is **label recovery**, not row count.

> **Source:** graduates [GAPS §11](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) · manifest dcs-verb-form-frequency-prelim · [VisualDCS](https://github.com/gasyoun/VisualDCS) · H1735 · 27-07-2026 · Grok 4.5 (grok-4.5)

### §492. Stopovye is a 102-file subset of Polnorazmernye, not a stopword filter of the full 506k

🟠 **PARA/Stopovye is a proper subset of PARA/Polnorazmernye by filename (102 of 245 CSVs; 0 stop-only names), with 139,817 stop rows vs 506,787 full rows (~27.6%); content is related but not identical (sample first-500 line Jaccard 0.23–0.50; some orthographic ṃ/m drift and extra commentary lines).** Class A.

Evidence: census 27-07-2026 (H1735):
- Polnorazmernye: 245 CSVs, 506,787 lines, 0 non-CSV
- Stopovye: 102 CSVs + 11 split .7z.001 members (~1.17 GB with compressed leftovers), 139,817 lines in the plain CSVs
- filename overlap = 102; only_full = 143; only_stop = 0
- shared samples: 107_1--1.csv full 52 / stop 54 lines, Jaccard@500 = 0.50; 10_1--1.csv 119/119, Jaccard 0.25 (ṃ vs m); 112_1--1.csv 16/16, Jaccard 0.23 with an extra Ratnaṭīkā line in stop

Implication: Stopovye is **not** «the full parallel export with stopwords removed» in the sense of the same 506,787-row table filtered — it is a **partial work-set** (102/245 files) with per-file content that sometimes diverges. Cite Stopovye and Polnorazmernye separately; do not treat row-count null as unknown — plain-CSV rows = 139,817 (plus unrehydrated 7z members).

> **Source:** graduates [GAPS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) · manifest stopovye-parallel-passages / dcs-parallel-passages-full · [VisualDCS](https://github.com/gasyoun/VisualDCS) · H1735 · 27-07-2026 · Grok 4.5 (grok-4.5)



### §493. Cross-vendor LLM second pass on routing gold is κ=1.0 — still not human IAA

🟡 **A Grok 4.5 second annotation of the 24-scenario which-dictionary routing benchmark agrees with Fable 5 gold on 24/24 (Cohen's κ = 1.0 strict); this is cross-vendor LLM agreement, not human inter-annotator reliability.** Graduates GAPS §10 only partially.

Evidence: independent second-pass labels committed before scoring (`tools/gaps_measure_out/h1745_routing_kappa.json` in Uprava H1745 pack; mirror in csl-guides). Answer space 44 codes; splits 18 dev + 6 test. Strict agree 24/24; lenient agree 24/24.

Implication: the scenarios are **highly determinate** for current model families — κ=1 does not prove gold is human-reliable. A human second pass remains required before treating the benchmark as IAA-grounded. Kin: FINDINGS contamination note on same-family κ as reliability statistic.

> **Source:** graduates [GAPS §10](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (partial — human IAA still open) · [routing-benchmark.json](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/routing-benchmark.json) · H1745 · 27-07-2026 · Grok 4.5 (grok-4.5)

### §494. Homonym token-attribution residual is a 38-group single-lemma_id ceiling

🟠 **Of 72 homonym groups in WhitneyRoots `token_attribution.json`, 26 are reliable and 46 are not: 38 fail because DCS exposes a single verb lemma_id for the whole lump, and 8 collapse onto one homonym under the current gloss map. Lowering the coverage≥0.55 floor cannot create splits when n_lemma_id=1.**

Evidence: re-count H1747 (`crosswalk/gaps_s4_homonym_ceiling_report.json`): reliable=26, unreliable=46, reasons={'DCS lumps (1 verb lemma_id)': 38, 'collapses onto one homonym': 8}. Sample lumps: gam, paś, ji, i, pat, stu (DCS single lemma_id). Extends FINDINGS §2 morphological ceiling into the post-gloss-mapping residual.

Implication: residual work is **sense/gloss gold or DCS sense-level IDs**, not more morphology or coverage-threshold tuning. GAPS §4 stays open for the adjudication work itself; the ceiling is now measured.

> **Source:** measures [GAPS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) · [token_attribution.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/token_attribution.json) · H1747 · 27-07-2026 · Grok 4.5 (grok-4.5)

### §495. Cyrillic name indices: 61 IAST-bearing seed files vs 47 pure-Cyrillic — rules still unsafe

🟡 **A filesystem probe of SamudraManthanam + RussianTranslation name-like files found 61 files with inline IAST parentheses (seedable for a proper-noun lookup table) and 47 Cyrillic-heavy files with zero IAST hits; character-rule reverse transcription remains unsafe (FINDINGS §60 stands).**

Evidence: H1746 probe scanned 152 candidate files (`RussianTranslation/tools/gaps_s6_cyrillic_name_probe.json`). Recoverable path = validated lookup seeded from IAST-bearing indices, not dental/retroflex-collapsing transcription.

Implication: GAPS §6 is not closed — the 3 fully-Cyrillic glossaries still need human-validated onomasticon rows — but the seed inventory exists and rules-based conversion is reconfirmed as a dead end.

> **Source:** measures [GAPS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) · [FINDINGS §60](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) · H1746 · 27-07-2026 · Grok 4.5 (grok-4.5)

### §496. Edit-distance record linkage over Sanskrit headwords is 70–98 % false matches — use a length-preserving normalization key and measure the false-match rate against the dictionary's own inventory

⚠️ **Reusable method gotcha, and a load-bearing one:** any join between two spellings of the same
Sanskrit headword (correction logs, OCR vs. clean text, cross-dictionary crosswalks, spell-check
candidate generation) is tempting to do with edit distance. Measured on the OBS-T correction corpus,
an edit-distance-1 join between the two correction eras produced **606 false links of 863 in PWG's
big brother PW, 474 of 616 in MW, 128 of 220 in BUR** — 70–98 % of links joined two *real, distinct
headwords* of the same dictionary (`nāman`/`yāman`, `kṛṣ`/`tṛṣ`, `nīla`/`nīca`, `imam`/`idam`).
The reason is structural, not incidental: a morphologically dense headword inventory of 20k–290k
records is saturated with minimal pairs, so "one edit away" is the *normal* distance between two
different words, not evidence of a misspelling. Attestation-gating the join (link only strings the
dictionary does not attest) does not rescue it — the surviving links still mix obvious repairs
(`divasaksaya`→`divasakṣaya`) with arbitrary ones (`moka`→`loka`, `mari`→`mati`).

**What does work, in the order it should be tried:**

1. **Decode, don't guess.** `f`, `F`, `q`, `Q`, `w`, `W`, `x`, `X`, `z` cannot occur in IAST, so a
   cell containing one is *provably* still in SLP1/HK and can be transcoded outright. In this corpus
   3,905 form-era headword cells were in that state (`prakfti` → `prakṛti`, `āQaka` → `āḍhaka`,
   `sPuwavaktar` → `sphuṭavaktar`); decoding them is a zero-false-match step that alone won +21/+13/+7
   recaptures for pw/mw/bur. This is the same partial transcode behind the documented `R`=ṇ trap
   ([SHARED_CODE §12](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)).
2. **Fold only what is not phonemic.** `sanskrit_util.form_key` (anusvāra + homorganic nasals → n,
   final visarga, pitch accents; **vowel length and retroflexion preserved**) collides 0.2–0.4 % of a
   dictionary's own records. `sanskrit_util.norm`, which drops every combining mark, collides
   **9–16 %** — roughly one record in nine made ambiguous, measured across 18 dictionaries. Length
   and retroflexion are the load-bearing distinctions; nasal class and pitch are not.
3. **Use the payload, not the string.** Where a correction is attributed to the headword itself, the
   corrected *value* names the record directly — content-grounded linkage that needs no similarity
   judgement at all.

**The measurement itself is the transferable part.** Both false-match measurements are fully offline
and need no human annotation: (a) the **key-collision rate** — how often the key merges two distinct
`<k1>` records of that same dictionary, a property of key × dictionary; and (b) the **attestation
test** on the pairs actually matched — if both strings are attested, distinct headwords, the link
joined two different records. Any repo doing headword matching (SanskritSpellCheck candidate
generation, csl-atlas crosswalks, WhitneyRoots form matching, kosha joins) can compute both from
`csl-orig` in one streaming pass and should report them rather than asserting a matcher is "fuzzy
but fine".

**Downstream consequence worth noting:** in a capture–recapture estimator the linkage error rate is
not cosmetic — it moves the headline number in a *known direction*. Missed true matches inflate the
population estimate; false matches deflate it. Switching PW/MW/BUR/CAE to the measured key moved BUR
off its record-count ceiling entirely (23 → 44 recaptures, ~19,776 → ~17,247), showing that ceiling
had been an artefact of the join rather than a fact about the dictionary.

> **Source:** [csl-observatory `scripts/headword_linkage.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/headword_linkage.py) +
> [`linkage_ladder.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/linkage_ladder.csv) +
> [`headword_key_collisions.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/headword_key_collisions.csv) +
> the "Site linkage" section of [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md) ·
> [H1477](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1477-Opus_csl-observatory_capture-recapture-fuzzy-linkage-corrector-pair_22.07.26.md)
> ([PR #120](https://github.com/sanskrit-lexicon/csl-observatory/pull/120)) — csl-observatory · 27-07-2026, Opus 5 1M (`claude-opus-5[1m]`).

### §497. The csl-orig L-number is not a join key — only 35 % of form-era L-codes still point at their own headword

⚠️ **The most tempting key in the corpus, and the worst.** Joining two records of the same
dictionary by their csl-orig `<L>` number looks strictly better than any string key: every
correction event carries one, it is ~99 % populated in both OBS-T eras, it is an exact integer, and
it involves no similarity judgement at all — so none of the false-match failure modes of
[§496](#496-edit-distance-record-linkage-over-sanskrit-headwords-is-7098--false-matches--use-a-length-preserving-normalization-key-and-measure-the-false-match-rate-against-the-dictionarys-own-inventory)
appear to apply. They do not need to. **The L-numbers themselves have drifted.**

Measured over all 22,826 form-era (2014–2019 web-form) correction events carrying an L-code, asking
only whether that `<L>` record in *current* csl-orig v02 still carries the headword the event claims:

| Dict | Events with an L-code | Still valid | Valid % |
|---|---:|---:|---:|
| pw | 11,775 | 6,343 | **53.9 %** |
| mwe | 53 | 26 | 49.1 % |
| mw | 1,382 | 654 | 47.3 % |
| pui | 643 | 245 | 38.1 % |
| inm | 73 | 27 | 37.0 % |
| bur | 693 | 215 | 31.0 % |
| sch | 73 | 22 | 30.1 % |
| pwg | 150 | 39 | 26.0 % |
| ben | 462 | 78 | 16.9 % |
| ap90 | 413 | 47 | 11.4 % |
| gra | 378 | 32 | 8.5 % |
| ccs | 2,229 | 136 | 6.1 % |
| wil | 1,132 | 18 | 1.6 % |
| ap | 495 | 6 | 1.2 % |
| cae | 1,298 | 3 | **0.2 %** |
| **TOTAL (26 dicts ≥ 25 events)** | **22,826** | **7,978** | **35.0 %** |

**Even the best dictionary is a coin flip.** Two thirds of form-era L-codes no longer resolve to
their own headword, and in cae, ap, wil, yat, skd and ieg the key is essentially noise (≤ 2.3 %).
Record numbers were renumbered, split and merged across a decade of csl-orig editing; the number in
a 2014 submission is a *historical* address, not a stable identifier. Anything that treats a stored
`<L>` as a durable foreign key — crosswalks, citation resolvers, correction back-references,
"same record" joins across snapshots — is resolving addresses that mostly no longer exist.

**The spread is itself the control.** A broken lookup would read ~0 % everywhere; a range of
0.2 %–53.9 % across dictionaries, on a single code path, measures per-dictionary renumbering
history rather than a bug in the measurement. (No non-form OBS-T layer stores an L-code, so a direct
same-method control on the git era is not available — the git-era join reads `<L>` out of csl-orig
at build time and is stable by construction.)

**Method, fully offline and annotation-free** — build `lcode → {<k1> spellings}` for the dictionary
from current csl-orig v02, then for each event ask whether the claimed headword is among them. The
comparison is deliberately generous (exact, Harvard-Kyoto-decoded and diacritic-folded spellings all
count as a match) and an L-code absent from csl-orig counts as invalid, so **35 % is an upper bound
on validity, i.e. a lower bound on drift.**

> **Source:** re-derived independently over
> [`correction_events.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events.csv)
> (24,441 events) against [csl-orig v02](https://github.com/sanskrit-lexicon/csl-orig) ·
> [H1766](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1766-Opus_csl-observatory_h1477-salvage-lcode-drift-hk-residue_27.07.26.md)
> — salvaged from a duplicate [H1477](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1477-Opus_csl-observatory_capture-recapture-fuzzy-linkage-corrector-pair_22.07.26.md)
> session whose figures were re-measured, not imported · 27-07-2026, Opus 5 1M (`claude-opus-5[1m]`).

### §498. Word-initial Harvard-Kyoto capitals never decode — 113 correction-event headwords entered the corpus mis-transcoded

🐛 **A live data defect with a one-character cause.** `build_correction_events.looks_hk` decides
whether a roman cell is Harvard-Kyoto and needs transcoding to IAST:

```python
if any(c.isupper() for c in tok[1:]):
    return True
return 'z' in tok
```

`tok[1:]` skips index 0 **by construction**, so a token whose only capital is *word-initial* is
never recognised as HK. In Harvard-Kyoto the capitals at word-initial position are exactly the long
vowels and vocalic r — `A` = ā, `I` = ī, `U` = ū, `R` = ṛ — which is precisely the set that matters
for Sanskrit headwords. `Adeya` (= ādeya) and `Ahnika` (= āhnika) therefore reach the corpus
un-decoded, keep their ASCII spelling, and can never match their git-era twin.

571 form-era cells sit in this state. Attestation-testing each against the dictionary's own `<k1>`
inventory — the decoded form is a real headword of that dictionary and the raw form is not —
confirms **113 of them across 14 dictionaries as proven missed decodes (84 distinct pairs), with
zero ambiguous cases** where both spellings are attested:

| Dict | Proven | Examples |
|---|---:|---|
| pw | 81 | `Acidoha` → ācidoha, `Adeya` → ādeya, `Adinava` → ādinava, `Amantrayitavya` → āmantrayitavya |
| bur | 6 | `Adi` → ādi, `Ahnika` → āhnika |
| ap90 | 4 | `Ama` → āma, `Atmaka` → ātmaka |
| ben | 4 | `Alambana` → ālambana, `Una` → ūna |
| gra | 4 | `At` → āt, `Im` → īm |
| ap · mw | 3 each | `Ayus` → āyus, `Adya` → ādya, `Atura` → ātura |
| ccs · inm · pe · vei | 1 each | `Adideva` → ādideva, `Urjavya` → ūrjavya |

**The naive fix is wrong and would corrupt data.** Firing `looks_hk` on any word-initial capital
would transcode ordinary capitalised English cells (`Tear` → ṭear), which is how a handful of
single-letter and English-headword hits — mwe, wil, cae — enter the count above as artefacts of
applying an SLP1→IAST decode to dictionaries whose `<k1>` is English; the Sanskrit-headword core
(pw, bur, ap90, ben, gra, ap, mw ≈ 105 of the 113) is unaffected by that caveat. **The safe fix is
attestation-gated:** decode a word-initial capital only when the token is otherwise all-lowercase
ASCII *and* the decoded form is attested as a `<k1>` of that dictionary while the raw form is not —
the same measure-don't-guess discipline §496 argues for, applied to the decoder itself.

**Direction of the error is known:** each missed decode suppresses a true recapture, and missed
matches inflate a capture–recapture population estimate ([§496](#496-edit-distance-record-linkage-over-sanskrit-headwords-is-7098--false-matches--use-a-length-preserving-normalization-key-and-measure-the-false-match-rate-against-the-dictionarys-own-inventory)),
so every affected dictionary's published "work remaining" is biased *upward* — small against pw's
11.7k events, but the defect is in the shared ingest path, not in one report.

> **Source:** confirmed at source in
> [`scripts/build_correction_events.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/build_correction_events.py)
> and measured over
> [`correction_events.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events.csv)
> with attestation against [csl-orig v02](https://github.com/sanskrit-lexicon/csl-orig) ·
> [H1766](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1766-Opus_csl-observatory_h1477-salvage-lcode-drift-hk-residue_27.07.26.md)
> · tracked as a csl-observatory `[integrity]` issue · 27-07-2026, Opus 5 1M (`claude-opus-5[1m]`).

### §499. Gold cards without evidence yield unusable votes — 5 of 6 MQM rejects carried no typology label, 1 of 20 labels reversed on adjudication

🔴 **Two independent defects in one review instrument, both measured on the first real G6
vote** ([`g6-mqm-gold-starter-2026-07-25`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/g6-mqm-gold-starter-2026-07-25.lock.json),
20 cards, voted 28-07-2026). The card showed exactly three things: the Sanskrit form, the Russian
rendering, and the LLM's typology label. Nothing else — no dictionary sense, no root, no attested
context, no visible source work.

**Defect 1 — the correct label lives in an unenforced prose convention, and reviewers do not follow
it.** The G6 contract is "on `reject`, write the correct label as the FIRST word of the note"
(`build_g6_mqm_gold_sheet.py`, enforced downstream by `apply_decisions.py`). The sheet's own
strict-review policy requires a note on reject but cannot require its *shape*, because
`csl_pyutil.render_review_sheet` has no label control — only a free-text box. Result: **5 of 6
rejects** opened with `aruṇāmśub` / `kāpālika` / `na` / `Почему` / `звуки` instead of a label, and since
`apply_decisions.py` is deliberately all-or-nothing, **the whole 20-card file failed to apply** —
including the 14 clean approves. The votes were recoverable only through a second human round.
Extrapolated to the n=400 store cut (H1665) at the observed 83 % non-compliance, that is ~100+
unusable rejects and a second full reviewer pass.

**Defect 2 — withholding the evidence does not test the reviewer, it corrupts the label.** Card 122
(`na` → «словно», work `08_rigveda`) was rejected with «na это всегда нет, никогда не словно».
In Rigvedic usage `na` is a regular particle of comparison (Grassmann s.v. `na` 2; Macdonell §180,
`śyeno na` «словно сокол») — a fact the project already owns in GRA, and one the card never
showed. Presented with it at adjudication the reviewer reversed the vote and left the LLM's
`correct` in force. **Had the sheet been machine-applied as cast, the gold standard would carry a
wrong label on a Rigvedic function word** — the class of word most likely to recur in any downstream
evaluation. Four further cards of the same 20 carry the identical complaint unprompted (id 3: «не
говоришь от какого корня … не приводишь контексты, а у нас их десятки, если не сотни»; id 6:
«Недостаточно данных для однозначного ответа»; id 92: «не видя контекста, а он у тебя есть, но
отсутствует у меня»; id 1 on stems vs case forms) — so the reversal is the visible tip of a
5-in-20 low-information-vote rate, not a one-off.

**The rule this settles (MG, 28-07-2026):** «Это все надо давать ДО, а не ПОСЛЕ» — evidence the
project already holds belongs **in the card**, not in the post-hoc adjudication. This is the
epistemic twin of the V9 screening gate (do not ask a human what an agent could decide): do not ask
a human to decide *without* the data the repo already has.

**Generalises past this sheet.** Any label-confirmation instrument — MQM typology, sense
disambiguation, gloss adjudication, spell-check verdicts — inherits both defects: a free-text
"answer in the note" convention is unenforceable, and an evidence-free card measures the
reviewer's recall rather than the datum. Fixes are structural, not editorial: a required label
control in the emitter ([H1802](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1802-Sonnet_csl-pyutil_review-sheet-reject-label-picker_28.07.26.md))
and an evidence panel joined from the dictionaries/roots/corpus the project already publishes
([H1801](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1801-Opus_SanskritLexicography_g6-gold-card-evidence-panel_28.07.26.md)).
Both now gate the n=400 store gold cut.

> **Source:** measured on the applied labels
> ([`gold/decisions_g6-mqm-gold-starter-2026-07-25.labels.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.labels.jsonl),
> 20 rows: 16 confirmed / 3 overturned / 1 deferred; LLM label accuracy 16/19 = 84.2 %,
> Wilson 95 % [62.4 %, 94.5 %] — a starter packet, not a precision figure of record) and on the
> reviewer's own note text · full audit record
> [`review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md)
> · [H1796](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1796-Opus_SanskritLexicography_g6-mqm-gold-starter-vote-apply_28.07.26.md)
> · 28-07-2026, Opus 5 1M (`claude-opus-5[1m]`).
>
> **Correction (29-07-2026, H1801, Opus 5 1M `claude-opus-5[1m]`):** the reversed card is id
> **122**, not 118 — the H1796 commit message, the H1801 handoff and this section's first
> version all carried the same slip. Card **118** is `aruRAmSub` / `raghuvamsha` / Classical,
> ruled `defer` with `needs_adjudication=true`; card **122** is `na` / `08_rigveda` / Vedic,
> the one reversed on withheld Rigvedic evidence. Checked against rows 11 and 18 of
> [`gold/decisions_g6-mqm-gold-starter-2026-07-25.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.csv).
> The ruling and every count above are unaffected — only the id was misrecorded.

### §500. A batch that never runs deletes a *band* of the sample, not a random subset — byte-packed chunking makes an incomplete A/B silently flatter the arm that failed

🔴 **An arm that completes 87 of 100 cards has not run "87 % of the experiment."** Measured on
the H1210 PWG A/B (DeepSeek vs Claude-native, 28-07-2026). Arm A's harness packs its work into
size-bounded chunks — equal BYTES per chunk, not equal card counts, because a length-stratified
slice makes equal-count chunks unusable. Three of ten chunks never produced a `slice_result`, so
13 cards were never attempted. Those 13 were not spread across the sample: **9 of them fell in
the top length quartile, and all ten cards of the verb-root stratum were among them.** The arm
completed every short card and skipped the hardest band.

The consequence is a number that looks like a result and is not one: arm A scored 95.4 %
(83/87) against arm B's 78.0 % (100/100), while the per-quartile comparison on cards *both*
arms attempted shows them level everywhere except the longest quartile (Q1–Q3: 100/100/89 % vs
95/91/86 %). The uncompleted band is exactly where both arms degrade, so the incomplete arm is
flattered by construction — and the direction is not luck. **Any size-aware batching has this
property**: chunk index correlates with the payload dimension, so a failed chunk removes a
contiguous interval of that dimension. The same holds for frequency-ordered, alphabetical, and
date-ordered batching.

**Why it survives review:** a per-stratum summary prints missing strata as *absent rows*, not as
zeros. Arm A's stratum table read `S1 58/60 · S2 11/12 · S3 9/10 · S5 5/5` — nothing on that line
says S4 exists and scored nothing. The omission is invisible unless the report joins back to the
selection worklist and names what is not there.

**The cheap defence, in the emitter rather than the reader:** compute `attempted` against the
frozen worklist and report the gap per stratum *by name* before any rate
([`coverage_gap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/coverage_gap.py)),
and make an unresolvable row a hard error instead of a dropped denominator. Generalises to every
chunked run in this repo — bounded windows, cohort barriers, residual drains — not only to A/Bs.

> **Source:** [`H1210_coverage_gap.29.07.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_coverage_gap.29.07.26.json)
> + [`H1210_length_breakdown.29.07.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_length_breakdown.29.07.26.json)
> · full report
> [`pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md)
> · [H1210](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1210-Opus_SanskritLexicography_pwg-ab-deepseek-vs-claude-100_17.07.26.md)
> · runs 28-07-2026 (controller Opus 4.8 `claude-opus-4-8`, workers Sonnet 5 `claude-sonnet-5`,
> generator `deepseek-chat`); coverage audit 29-07-2026, Opus 5 1M (`claude-opus-5[1m]`).

### §503. A git worktree silently disables every sibling-repo lookup in `src/` — artifacts rebuilt there lose layers without failing

✅ **RESOLVED 30-07-2026 (H1902, Sonnet 5 `claude-sonnet-5`).** All 11 modules now call one
shared resolver, [`sibling_root.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sibling_root.py)
(`$CSL_SIBLING_ROOT` override → upward marker-directory auto-detection → the historical guess as
last resort), so the auto-detection path fixes the worktree case even with **no env var set at
all** — verified from inside a real `git worktree` (`g5_card_render.py` /
`build_g5_review_sheet.py --selftest` both report "pwgab table present · pwgbib bibliography
present"). `require_sibling()` also lands the "stronger fix" this entry called for: a table
missing when `CSL_SIBLING_ROOT` is explicitly set now raises `FileNotFoundError` rather than
degrading, applied to `pwg_ab.table()`, `pwg_sources.bib()`, and
`part_b_xref_discovery.iter_records()`. Closes [SanskritLexicography#875](https://github.com/gasyoun/SanskritLexicography/issues/875).

🔴 **`GH = normpath(join(HERE, '..', '..', '..'))` resolves to `GitHub/` only in the canonical
checkout.** A worktree created the way this org's shared-tree rule *requires*
(`git worktree add ../<Repo>-h###-<pid>`) lands beside `GitHub/`, not inside it, so that same
expression resolves to `Documents/` — where no sibling repo exists. Eleven modules under
`RussianTranslation/src/` compute their sibling root this way ([`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py),
[`pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py),
`ls_coverage.py`, `citation_tm.py`, `corpus_gate.py`, `annotate_genres.py`,
`build_mbh_concordance.py`, `part_b_xref_discovery.py`, `rv_griffith_extract.py`,
`rv_renou_citations.py`, `rv_spine_build.py`).

**The failure is silent by design.** These lookups are *optional* — a missing `pwgab`/`pwgbib`
table degrades to "no tooltip" rather than crashing, because CI checks out only this repo (§ the
H1308 rule). That is right for CI and wrong for a worktree: the operator has the tables, believes
they are in use, and ships a thinner artifact. Measured on the H1847 pinned re-issue of the G5
batch1v3 sheet, same command, same inputs, only the checkout differing:

| Layer in the 150-card sheet | built in a worktree | built with `CSL_SIBLING_ROOT` set |
|---|---:|---:|
| `<ab>` abbreviation spans with German/Russian expansion | 0 | 253 |
| unlinked-citation marks (needs `pwgbib`) | 1 | 8 |
| Cologne `<ls>` links (needs neither) | 988 | 988 |

The sheet was byte-valid, passed its own drift check 150/150, and would have gone to a reviewer
missing exactly the layer that reviewer had asked for two days earlier (H1808).

`So:` both tables now honour a `CSL_SIBLING_ROOT` env override, and any worktree-based rebuild of
a reader-facing artifact must set it — `$env:CSL_SIBLING_ROOT="C:\Users\user\Documents\GitHub"`.
The other nine modules still carry the bare three-levels-up guess; porting the override is queued,
not done. A stronger fix would make an *expected-but-absent* table a hard error when an env var
says the operator expects it, so this cannot degrade quietly again.

_29-07-2026 · [H1847](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1847-Opus_SanskritLexicography_nws-tag-vocabulary-facets_29.07.26.md) · Opus 5 1M (`claude-opus-5[1m]`)_

### §504. The NWS tag layer reaches only 2.2 % of the RU store — a facet bar over it is right, but it is not the sheet's main axis

🟠 **255 of 11,603 translated rows carry an NWS `[diasystem, domain]` bracket at all.** The tag
vocabulary the whole-corpus census measured (48,214 tagged senses over 34,101 scraped NWS lemma
cards) is a property of the *Nachträge* layer, not of the PWG rows our translation queue is made
of — so on a 150-card G5 slice exactly 4 cards (2.7 %) show any tag, and the facet bar built for
them offers 7–8 chips. The feature is still the right one (those 4 cards were previously
unfindable), but sizing expectations off the census's 48k would be a category error: that number
counts senses in the source dictionary, not cards in the review queue.

What the store's own slice contains, and how it differs from the corpus:

| Slot | distinct in the RU store | top values (store) | note |
|---|---:|---|---|
| diasystem | 10 | `Ved` 115 · `Śā` 67 · `Gen` 33 · `Buddh` 16 | `mahat` ×1 is parse residue |
| domain | 12 | `unsp` 170 · `Med` 34 · `Soc` 15 · `Ling` 12 | 17 rows are half-translated (below) |
| position | 2 | `ifc` 3 · `Bhvr` 1 | the corpus has ~10 more this slice never shows |

Two data defects fell out of the same pass, both store-side, neither repaired here:

1. **Half-translated machine-readable tags** — `без уточн` ×13, `Мед` ×2, `Линг` ×1, `Лингв` ×1.
   The census flagged 12+2 corpus-wide; the RU store has 17. A tag that is sometimes Latin and
   sometimes Russian cannot be grouped, counted, or faceted without an alias table.
2. **One malformed bracket** — `[Gen, unsp , 1349 A.D. , Delhi]`, where a date and a place ran
   into the domain slot. Harmless in a tooltip, a defect as a *control*: it would have rendered a
   facet chip labelled `unsp , 1349 A.D. , Delhi`. The tag index now rejects values carrying
   digits/commas while the tooltips still gloss whatever is present.

🟢 **Repaired store-side by [H1903](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1903-Sonnet_SanskritLexicography_nws-tag-halftranslation-store-repair_29.07.26.md)
(30-07-2026).** [H1809](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1809-Sonnet_SanskritLexicography_nws-bare-citation-ls-markup_28.07.26.md)
had already migrated the 17 *domain-only* half-translations the census counted here — but its
`_BRACKET_TAG_DOMAIN` regex anchored on a **Latin** diasystem in slot 1, so it silently skipped
every row where the diasystem was *also* mistranslated (`[Будд., без уточн.]`) or the header used
the unbracketed `DIA , DOM >` form — leaving 17 more rows (both slots, or dropped entirely) plus a
distinct source-fidelity class (a manuscript date+place genuinely embedded in the source's own
`[Jin, unsp, DATE, PLACE]` header — confirmed against the raw `pilot/nws/br_ahm_i.json` card — split
2-slot `[Jin, unsp]` + `(DATE, PLACE)` restored to the body) and the `mahat` gloss-bracket
false-positive (reformatted `[…]`→`(…)` so it no longer collides with the tag-detector shape).
0 Cyrillic / 0 comma-digit-bearing tag slots remain, verified two ways: a standalone scan AND
`validate_final_card_schema.nws_tag_defects()`, a new write-time guard wired into
`validate_sense()` so a future generation run rejects the row instead of landing it. The
compensating Cyrillic aliases in `g5_card_render.DOMAIN_RU` are retired (the corpus is
German/English/French by construction, so nothing can re-need them).

`So:` facet a tag vocabulary off what the *cards in hand* carry (with the corpus share beside it
for context), never off the corpus inventory — a chip that selects nothing is a dead control, and
a corpus-sized expectation makes a working feature look broken.

_29-07-2026 · [H1847](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1847-Opus_SanskritLexicography_nws-tag-vocabulary-facets_29.07.26.md) · Opus 5 1M (`claude-opus-5[1m]`)_

### §501. An A/B whose "clean" metric scores the last attempt that RETURNED, not what the pipeline would ship, can name the wrong winner — and did

🔴 **Same 100 cards, same two arms, two defensible definitions of clean, opposite conclusions.**
Measured on the H1210 PWG A/B once arm A's coverage gap was filled
([H1846](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1846-Opus_SanskritLexicography_h1210-arm-a-coverage-fill_29.07.26.md), 29-07-2026).

The rig's per-card loop keeps `rec.card` from the last attempt that **returned**, while
`final_status` records how the card **ended**. A card whose controller rejected attempt 1 and
whose attempt 2 died mid-stream ends `worker-null-death` and still carries attempt 1's text
into `cards_out` — which is exactly what `canonical_audit.py` scores. So:

| metric | arm A | arm B |
|---|---:|---:|
| audit-clean (`promote_dry`) | 93/100 | 78/100 |
| shippable (`promote_dry` AND rig ended clean) | **72/100** | **70/100** |
| Q4 long entries, audit-clean | 20/23 (87%) | 8/23 (35%) |
| Q4 long entries, shippable | **3/23 (13%)** | **4/23 (17%)** |

A 15-point lead becomes a 2-card tie, and the long-entry quartile — the one the first report
called decisive — **reverses**. The gap is not noise: 21 of arm A's 93 audit-clean cards were
ones its own pipeline refused (vs 8 in arm B), because the arms fail differently (arm A
retries into API transport failures; arm B returns unusable output outright). Any metric that
scores *text produced at some point* rather than *what the pipeline delivers* silently rewards
the arm that fails later in the chain.

**The rule this yields:** for any pipeline A/B, report the pair — the artifact-quality metric
AND the delivery metric — and state which population each describes. Where they agree, the
result is robust; where they diverge, the divergence IS the finding. Reporting only the one
that flatters a conclusion is not a summary, it is a selection.
[`status_vs_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/status_vs_audit.py)
(per-card cross-tab) and
[`dual_metric_breakdown.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/dual_metric_breakdown.py)
(both metrics per stratum) are the reusable form. Companion to
[§500](#500-a-batch-that-never-runs-deletes-a-band-of-the-sample-not-a-random-subset--byte-packed-chunking-makes-an-incomplete-ab-silently-flatter-the-arm-that-failed):
that one is about which cards enter the denominator, this one about which cards count as
success.

> **Source:** [`H1210_dual_metric.29.07.26b.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_dual_metric.29.07.26b.json)
> · full report
> [`pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md)
> · 29-07-2026, Opus 5 1M (`claude-opus-5[1m]`); the 13 filled cards ran with workers
> `claude-sonnet-5` and a controller the template's alias resolved to `claude-opus-5[1m]`.

### §505. SamudraManthanam stores canonical line IDs but drops them from durable references — corpus rebuilds can silently retarget exports and corrections

🔴 **The corpus has a stable-identity field, but the paths expected to survive an ingest still
persist only mutable ordinals.** The FTS5 `corpus_lines` schema includes `canonical_id`, while:

- [`search_service.py`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/app/services/search_service.py)
  selects `source_id`, `line_num`, and `link_id`, but not `canonical_id`;
- [`models.py`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/app/models.py) has no
  canonical identity field on `SearchResultItem`;
- [`search.py`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/app/routers/search.py)
  exports ordinal `source_id` + `line_num`; and
- [`state_db.py`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/app/state_db.py) plus
  [`corrections.py`](https://github.com/gasyoun/SamudraManthanam/blob/main/web/app/routers/corrections.py)
  retain the same ordinal pair for correction proposals.

The corpus table is rebuildable. If source ordering or a source's line structure changes, an old
ordinal may still resolve successfully — to different content. This is worse than a broken link:
the failure is plausible and silent, even though a stable identity was already computed.

`So:` every durable external reference must carry
`{source_slug, canonical_id, corpus_version}`. Migration must map every retained legacy ordinal to
that identity and fail on any orphan or ambiguity; it must never silently fall back to the new
content at the old ordinal. The architecture audit adopted this as a zero-orphan Wave-1 gate in
[PR #116](https://github.com/gasyoun/SamudraManthanam/pull/116), with implementation packet
[`H1920`](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1920-Codex_SamudraManthanam_durable-reference-zero-orphan_30.07.26.md).
The owning defect is tracked as
[SamudraManthanam #117](https://github.com/gasyoun/SamudraManthanam/issues/117).

### §510. A frozen local checkout is an actively misleading source for any append-only registry — read the numbering contract from `origin/`, not from disk

🔴 **Two consecutive §-number collisions in one session, both from reading a stale working
copy.** Evidence (H1910, 30-07-2026): the propagation pass needed the next free FINDINGS
number, read `FINDINGS.md` in `GitHub/SanskritLexicography` — a checkout the session-start
scan had already reported as diverged and unable to fast-forward — and saw a highest number
of **§462**. On `origin/master` the file carried **166** findings and §463–§466 were all
taken, so four numbers briefly held two different claims each, which
[`tools/epistemic_integrity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/epistemic_integrity_check.py)
exists to catch. The repair then hit the *same class of error a second time*: the file's own
`(currently §505)` marker was itself stale, because a concurrent session had appended §505
without bumping it.

Three things follow, and they generalise past this file to every append-only registry in the
org (handoff IDs, `Axx`/`Mxx` article IDs, review-sheet ids, DEAD_ENDS/GAPS numbering):

1. **Never read an ID contract from a local working tree.** `git show origin/<default>:<file>`
   costs one command and is immune to a clone that is days behind. A dirty-or-diverged clone
   does not announce itself at the point of the read — this repo's checkout was 177 commits
   behind and still served a perfectly well-formed file.
2. **The in-file "next free" marker is a cache, not the truth.** It is only correct if every
   previous appender remembered to bump it, and one had not. Derive the ceiling from the
   actual headings (`max`) and treat the marker as a cross-check that must agree — then
   assert, as a post-condition, that the marker sits *above* every used number.
3. **A count is not a coverage check.** Renumbering left the total at 166 either way; only
   `uniq -d` over the heading numbers distinguished four-numbers-used-twice from
   four-numbers-appended. Same shape as [§506](#506-a-complete-coverage-count-cannot-see-commentary-leaking-into-an-extracted-translation-layer).

This is the registry-side twin of §503 (a `git worktree` silently disabling sibling-repo
lookups in `src/`): both are cases where the *location* of the checkout, not the code, decided
the outcome — and in both the failure was silent rather than loud.

> Opus 5 1M `claude-opus-5[1m]` · 2026-07-30


### §511. MW72 carries ZERO `<ls>` source citations — every cross-dictionary citation test that names it shrinks to MW

🔴 **A dictionary named in a plan is not a dictionary that carries the tag layer the plan
needs.** Evidence (H1827, 31-07-2026, csl-atlas): the PET-MW-CITE citation-truncation
handoff scoped its test as "PWG/PW/PWK ↔ MW/MW72". A one-line count before writing the
builder:

| dict | file | `<ls>` tags |
|---|---|---:|
| PWG | `csl-orig/v02/pwg/pwg.txt` (54.6 MB) | 801,788 |
| MW | `csl-orig/v02/mw/mw.txt` (50.2 MB) | 320,828 |
| PWK | `csl-orig/v02/pw/pw.txt` (31.5 MB) | 98,485 |
| PWKVN | `csl-orig/v02/pwkvn/pwkvn.txt` | 17,627 |
| **MW72** | `csl-orig/v02/mw72/mw72.txt` (17.2 MB) | **0** |

MW72 is a full 17.2 MB digitisation with 55,390 entries and a working `<h>` homonym index —
it is not a stub. It simply has no tagged source-citation layer at all. csl-atlas's
`scripts/lib/dict-feature-adapters.mjs` already encodes this (MW72 appears under `homonyms`
and `senses`, and is **absent** from `citations`), but the absence is a missing key, not a
stated fact, so a plan written from the dictionary roster rather than from the adapter table
will name MW72 as a citation target and read nothing back.

Three consequences worth carrying:

1. **A missing tag layer produces a zero, not an error.** Every `<ls>`-driven metric —
   apparatus density, source overlap, citation cosine, truncation depth — evaluates cleanly
   to 0 / empty for MW72. Without an explicit guard the packet ships a confident zero. The
   fix that generalises: assert the tag layer per dictionary *before* the loop and fail loudly
   on a dictionary declared tagged that yields nothing, rather than validating totals after.
2. **Report the shrinkage in the artifact, in both directions.** The csl-atlas packet carries
   an `excludedDictionaries` block naming MW72 and its reason, and its validator checks the
   contract *both* ways — a zero-citation dictionary must be listed as excluded, and a listed
   one must have zero citations. A one-way check lets a silent re-inclusion pass.
3. **"PW" and "PWK" are one digitisation** (csl-orig code `pw`), so a plan naming
   "PWG/PW/PWK" is naming two works, not three. PWKVN, the *kürzere-Fassung* Nachträge, is the
   third Petersburg witness with a validated `<ls>` adapter.

Same shape as [§503](#503-a-git-worktree-silently-disables-every-sibling-repo-lookup-in-src--artifacts-rebuilt-there-lose-layers-without-failing)
and [§510](#510-a-frozen-local-checkout-is-an-actively-misleading-source-for-any-append-only-registry--read-the-numbering-contract-from-origin-not-from-disk):
the failure is silent and comes from *what the input actually is*, not from the code. Measure
the input's capability first; it costs one `grep -c`.

Shipped in [csl-atlas#325](https://github.com/sanskrit-lexicon/csl-atlas/pull/325)
([`data/lexico/citation_truncation_hapax.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/citation_truncation_hapax.json),
[`scripts/build-citation-truncation.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-truncation.mjs)).

> Opus 5 1M `claude-opus-5[1m]` · 2026-07-31


_30-07-2026 · repository architecture audit · Codex GPT-5_

---

### 512. A ruling that reaches a register but never reaches the card is re-litigated by the next human (N1 loop)

**Measured defect (H1650 / pramuc, 26-07 → 01-08-2026).** Card `muc|muc~~h0_20_pra|8` was
**N1 in the 19-07 H178 DA vote register**: reuse SamudraManthanam RU for R./MBH. citations.
H1304 shipped `citation_tm.py` the same day. The voting sheet was never re-rendered with the
attested line, so MG had to write the same objection again in `pramuc.md`.

**Rule:** if a human ruling is about what the *next* sheet must show, the sheet generator is
part of the delivery — register rows alone are not. H1650 wires `citation_evidence_panel()`
into h178/h180 generators and a screening banner (csl-pyutil ≥0.8.0).

> Grok 4.5 (`grok-4.5`) · 01-08-2026 · H1650

---

### 513. A lock that guards a path, not the file — and a delta gate that counts rows, not bytes

**Two measured exposures from the H2025 dual-run pipeline audit
([memo](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_AUDIT_PWG_RU_H2025_01-08-2026.md), rev `b4db4259`).**

1. **`PromoteClaim` is acquired by every promote entry point — and by nothing else.** 13
   non-promote store mutators (`annotate_*`, `fix_*`, `backfill_tn_residue`,
   `mark_reconstructed_headwords`, `ru_style_sweep`, `repair_h178_da_cards`) plus the human
   overlay writer `apply_editorial_decisions.py` write `pwg_ru_translated.jsonl` with no lock,
   no backup, no fsync. Concurrent with a promote they are last-writer-wins. Meanwhile
   `merge_store_rows` decides replacement purely on `_attempt_quality` and never reads
   `review_status`/`reviewer` — the live store's 5 human-reviewed rows would come back
   `ai_translated` on re-promote (the overlay-wipe class, still live).
2. **A row-count delta gate is blind to content.** `h1809.bak` → live store: both 11,603
   rows, yet 26,198,939 → 24,904,391 bytes — a 1.29 MB change (apparently JSON-separator
   compaction; writer unidentified) passed every promote invariant. Rows and field-name sets
   identical; `ru`/`de` content moved 149 bytes.

**Rule:** a mutual-exclusion claim protects a *file* only if every writer of that file
acquires it — audit writers, not entry points. And a promote delta gate must bound content
mass (bytes/chars), not just cardinality: identical row counts are compatible with megabytes
of silent change.

> Fable 5 (`claude-fable-5`) · 01-08-2026 · H2025

### 514. PWG's own `R.` (Rāmāyaṇa) siglum is edition-ambiguous — Arabic vs. Roman book numbers route to different critical editions

**Measured directly against `ls_resolver.generate_href` while building the H1909 NWS
bare-citation discriminator
([nws_ls_markup.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nws_ls_markup.py)).**
`R.` resolves in PWG's own bibliography and `ls_resolver` accepts more than one locus
spelling for it — but they are NOT interchangeable:

- `generate_href('pwg', 'R. 1,44,6', '')` → `ramayanaschl` (**Schlegel** edition).
- `generate_href('pwg', 'R. i,44,6', '')` → `ramayanagorr` (**Gorresio** edition) — same
  book/chapter/verse, lowercase Roman book number instead of Arabic.

The NWS-layer store cites this convention as uppercase Roman + period-separated locus
(`'R I.44.6'`), which matches NEITHER accepted form — `href_ramayana`'s regex wants
`[iv]+[ ,]+` (lowercase, space/comma), so naively normalising the visible Roman numeral to
Arabic (the standard move for every OTHER PWG siglum, e.g. `ṚV`/`AV` mandala numbers) would
silently pick the Schlegel edition for a citation whose original spelling gives no signal
either way. H1909's discriminator deliberately does NOT guess here — 4 such spans (`R
I.44.6`, `R VII.21.42`, `R II.12.110`, `R III.61.3`) are left as honest residue
(`residue_no_href`) rather than auto-linked to a possibly-wrong edition.

**Rule:** a siglum resolving in PWG's bibliography + `ls_resolver` accepting SOME locus
spelling for it is NOT sufficient evidence to auto-normalise a differently-spelled locus for
the same siglum — check whether the accepted spellings are actually the SAME target first
(same edition/source), not just "some href exists." `R.`/Rāmāyaṇa is the one measured case in
this pipeline where they aren't.

> Sonnet 5 (`claude-sonnet-5`) · 02-08-2026 · H1909

### §515. PWG rests on WIL 1819; MW/MW72 English on WIL 1832 — CDSL has only 1832 OCR; do not treat Wilson as edition-free

🔴 **Wilson is two print editions that feed two different European lines; CDSL digitises only one of them.** Treating "Wilson" as a single text confounds PWG-side vs MW-side ancestry work.

| Edition | Role | Full body at Cologne/CDSL? |
|---|---|---|
| **WIL 1819** (1st, Calcutta) | **Print base of PWG**; European intermediate for the dictionary-tradition stream MW compresses under `<ls>L.</ls>` | **No** |
| **WIL 1832** (2nd, Calcutta) | **English-gloss base of MW72** (with PWG matter added); MW1899 brings English meanings forward from MW72; MW `W.` / CDSL `wil` | **Yes** — `csl-orig/v02/wil/wil.txt` |

**Do not collapse markers:**

- MW **`L.`** = *native lexicons only* (MW 1899 preface) — not a Wilson siglum. Transmission path of that European stream: **WIL 1819 → PWG (named koshas) → MW `L.` hedge**.
- MW **`W.`** = Wilson's authority; CDSL text for comparison is **1832**.

**Scope discipline (MG, 02-08-2026):** full WIL 1819 body digitisation is **not** needed now; the **1819 preface** is the bounded next OCR unit (`/cologne-preface-ocr`). Sample residue only: [WIL `WIL_1819_page59_iast.pdf`](https://github.com/sanskrit-lexicon/WIL/blob/main/WIL_1819_page59_iast.pdf).

Canonical note: [WIL `docs/WIL_EDITION_LINEAGE_1819_1832.md`](https://github.com/sanskrit-lexicon/WIL/blob/main/docs/WIL_EDITION_LINEAGE_1819_1832.md). Cross-wired into [MWS DICT_PROFILE](https://github.com/sanskrit-lexicon/MWS/blob/master/DICT_PROFILE.md), [PWG README](https://github.com/sanskrit-lexicon/PWG/blob/main/README.md), [MW72 README](https://github.com/sanskrit-lexicon/MW72/blob/master/README.md). Related: [§511](#511-mw72-carries-zero-ls-source-citations--every-cross-dictionary-citation-test-that-names-it-shrinks-to-mw) (MW72 has zero `<ls>`).

> Grok 4.5 (`grok-4.5`) · 02-08-2026 · MG standing note (edition lineage + OCR scope)

### §516. A later PR's stale-base merge can silently revert an EARLIER PR's ledger-doc-only re-stamp while leaving that earlier PR's CODE change fully intact

H2226/OPT-4 (`dc81f89a`, 02-08-2026, Grok 4.5) correctly field-parameterized
`RussianTranslation/src/pilot/h1209/wf_template.js` + `h1210/wf_template_ab.js` +
`h1210/control_template.js` (TARGET_FIELD/CONTROLLER_PROMPT from the payload instead of a
hardcoded `russian`) and, in the SAME commit, re-stamped the two `LANG_PARITY.md` ledger
entries this closed (`h1209_controller_worker_rig`, `h1210_ab_arm_scaffold`) from GAP to
SHARED with the new file hashes. The very next `LANG_PARITY.md`-touching commit,
H2227/OPT-2 (`72c8311d`), was authored/rebased against a base that predated H2226's ledger
edit — when it landed, git's merge silently carried the OLDER (pre-H2226) content of just
those two ledger entries forward, reverting `verdict`/`languages`/`verified_sha256` back to
GAP and the old hashes, **while H2226's actual code files were never touched and stayed
fully parameterized**. `lang_parity_check.py` correctly flagged the resulting hash mismatch
as "drift" on the next `origin/master` checkout ([H2243](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2243-Sonnet_SanskritLexicography_pwg-lang-parity-drift-reverify_03.08.26.md)),
but the mechanical drift-check gives no signal on WHICH side moved — a naive
`--update-hash` re-stamp at that point would have accepted the reverted-to-GAP verdict as
current truth, permanently losing H2226's SHARED determination in the ledger's own history.
The only way to tell "code drifted, re-verify the verdict" apart from "the ledger doc itself
regressed under the code" was to directly re-hash the current working-tree files and compare
against the LAST commit that legitimately re-stamped them (`dc81f89a`), not just diff
against the ledger's own currently-recorded (possibly-reverted) hash.

**Detection recipe:** when a ledger/registry `--update-hash`-style drift-checker flags an
entry, before blindly re-stamping, `git log --oneline -N -- <file>` on every tracked file in
that entry and read each intervening commit's diff — if a commit touched the doc file itself
(not just the tracked source files), check whether IT reverted a sibling entry rather than
advancing it. A merge/rebase that predates a doc-only re-stamp is a silent-revert vector for
any append-only-in-intent but git-merged registry (LANG_PARITY-style ledgers, `CROSS_REPO_DECISIONS`-style
files, hand-maintained `verified_sha256` snapshots) — the failure mode is invisible to a
plain `git diff` review of the newer PR alone, since that PR's author never edited those
lines on purpose and the PR's own file-list looks unrelated.

> Sonnet 5 (`claude-sonnet-5`) · 03-08-2026 · H2243 LANG_PARITY drift re-verify

### §517. An EMPTY spawn directory is not a context-free spawn directory — verify the ancestry, not the directory

`headless_worker.bare_cli_cwd()` (H2158) existed to spawn the paid CLI from a directory with
no project context, and it checked exactly that: no `CLAUDE.md`, no `.git`, walking up from
the candidate. It shipped pointing at `%TEMP%\pwg_ru_cli_cwd` — an empty directory, and on
Windows a directory **under the user profile**. The CLI's own memory discovery does not stop
at `CLAUDE.md`: `.claude\CLAUDE.md`, `.claude\CLAUDE.local.md` and `.claude\rules` are
picked up from any ancestor too, and `C:\Users\<user>\.claude\CLAUDE.md` is precisely
where an operator's global memory lives. Result: **32 779 B of operator memory in every paid
call** for the life of the helper, with no signal of any kind — `ls` on the spawn directory
showed nothing, the selftest asserting "no `CLAUDE.md` in the cwd" passed, and the cost showed
up only as prefix tax nobody could attribute.

Three transferable rules, none of them specific to this pipeline:

1. **A marker-set check is only as good as the marker set**, and the marker set belongs to
   the tool being spawned, not to the spawner. Enumerate what the *child* discovers
   (`h2189_min_profile.ANCESTOR_MEMORY_RELPATHS` / `ANCESTOR_MEMORY_DIRS` here), keep it in
   ONE place, and have the spawn path consume that same list — two half-updated marker lists
   is how a fix in one silently fails to reach the other.
2. **Emptiness is a property of a directory; context is a property of its ancestry.** Any
   "clean room" directory derived from `tempfile.gettempdir()` on Windows is under the user
   profile by default and inherits from it. The cheapest clean ancestry on a Windows box is a
   **drive root**, but a hardcoded drive letter degrades silently to nothing on another
   machine — derive candidates, verify each, and return `None` rather than an unverified one.
3. **"Could not prove it clean" and "proved it clean" must not collapse into the same
   answer.** A verifier that fails open (an ImportError swallowed, a scan exception treated as
   "no hits") converts a safety check into a no-op with no observable difference. Fail closed,
   and say so on stderr.

Sibling class, same shape: the "inert by construction" gate named in
[H2160](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2160-Opus_RussianTranslation_whole-card-b0-hang-and-medium50-completion_02.08.26.md),
where a check runs, passes, and was never capable of failing. Here the check ran, passed, and
was never capable of *seeing* the thing it guarded against — the always-pass variant costs
money silently instead of hiding a defect loudly. Diagnostic: `python src/pilot/h2189_min_profile.py --scan-cwd <dir>` prints every injectable
ancestor file with byte sizes, offline and free.

> Opus 5 (`claude-opus-5[1m]`) · 03-08-2026 · [H2249](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2249-Opus_SanskritLexicography_pwg-bare-cwd-ancestry-leak-fix_03.08.26.md) · [PR #1090](https://github.com/gasyoun/SanskritLexicography/pull/1090)

### §518. A ceiling written as a LITERAL in a test silently encodes whatever the default was the day it was typed — derive it from the policy table

The PWG probe gate keeps one source of truth for its ceilings (`probe_log.POLICIES`) and a
pointer at the live one (`CURRENT_POLICY`). H2118 built that table precisely because three
hard-coded copies of the number had already drifted apart. It worked — and the *tests* still
went stale, twice, because they pinned the number instead of the pointer.

**What was found (H2173 G10, 03-08-2026).** `probe_log.verdict_for`'s own `policy=` default
was frozen at `production_v1` while `CURRENT_POLICY` advanced to v2 (65 000) and then v3
(80 000 wall + 45 000 route). Nothing was wrongly admitted — v1's 30 000 ms is the
*strictest* of the three, so the drift failed in the safe direction — but every default-lane
receipt named a gate retired since 31-07-2026, and v3's `api_ceil_ms` guard could never fire
because v1 declares none. The CLI compounded it: `api_ms` was a `verdict_for` parameter with
**no `--api-ms` flag**, so the route guard was unreachable on the one path that writes
receipts.

**The part worth generalising.** Correcting that default immediately broke
`execution_contract_selftest`, whose assertions read `verdict_for(29999, …) == 'GO'` and
`verdict_for(30000, …) == 'NO-GO'`. Those had never been *about* 30 000; they were about
"strictly under passes, at the ceiling fails" — but by writing the boundary as a literal and
omitting `policy=`, they silently encoded the stale default and passed for the wrong reason.
A test that pins a literal cannot distinguish "the boundary rule holds" from "the default
never moved", so it goes green through exactly the drift it looks like it is guarding.

**Rule.** Derive a boundary from the same table production reads:

```python
live = probe_log.POLICIES[probe_log.CURRENT_POLICY]
assert verdict_for(live['latency_ceil_ms'] - 1, …)[0] == 'GO'
assert verdict_for(live['latency_ceil_ms'], …)[0] == 'NO-GO'
```

Retired policies still get pinned at their historical numbers — rows stamped `production_v1`
were genuinely judged at 30 000, and re-pointing a name retroactively falsifies them. So:
**derive the LIVE boundary, pin the HISTORICAL ones.**

Same shape in prose: `/pwg-live-gate` restated "65 000 ms" and was wrong within a day of
H2138 deriving v3, having already been wrong at 30 000 before that. Any document naming a
number that a table owns is a copy waiting to rot — name the derivation, quote the number as
a convenience, and say which it is.

> Opus 5 (`claude-opus-5`) · 03-08-2026 · [H2173](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2173-Opus_SanskritLexicography_pwg-audit-tail-g5-g8-g9-g10_02.08.26.md) · [PR #1083](https://github.com/gasyoun/SanskritLexicography/pull/1083)

### §519. vidyut.kosha's `lemma` for a krdanta-derived Subanta is the bare dhatu — entry-count lemma voting collapses derived nominals to verbal roots

**The trap.** For an inflected nominal form, `Kosha.get(form)` returns one `PadaEntry_Subanta`
per parse, and for every parse whose pratipadika is **krdanta-derived**, `entry.lemma` is the
underlying **dhatu**, not the nominal stem. Because a productive root generates many krdanta
parses, the collapsed dhatu **outnumbers** the true stem in the entry list: `janitf` (janitṛ,
agent noun) yields **12** entries with lemma `jan` vs **3** with lemma `janitf`; `liNgin`
yields 4×`liNg` + 4×`liNgi` (both collapses) vs 2×`liNgin`; even `rAmeRa` (rāmeṇa, "by
Rāma") out-votes to the root `ram` ("to delight"), 6 vs 4. Any consumer that picks a lemma by
majority over kosha entries — the obvious first implementation — therefore systematically
lemmatizes derived nominals to bare verbal roots. This was the measured **defect class 2** of
the Sa→Ru gloss wave-2 panel ([gold/saru_gloss_precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/saru_gloss_precision_report.md)):
the vidyut tier's lemma precision sat at **71.8 %** against 94.9 % (dcs) / 93.3 % (marker),
and the panel's ruling is that the nominal stem, not the root, is the lemma.

**The rule.** The distinction is machine-readable on every entry: `entry.pratipadika_entry`
is `PratipadikaEntry.Basic` for a real nominal stem and `PratipadikaEntry.Krdanta` for a
collapse (Tinanta/avyaya entries carry none). Rank lemma candidates **with** that field —
when any Basic-backed noun candidate exists, a Krdanta-only noun candidate is a derivation
trail, not a lemma vote. Keep the demoted dhatu in the ambiguity trail (it is genuine
derivational information), and leave verb candidates alone: a Tinanta's lemma really is its
dhatu. Fixed this way in
[`RussianTranslation/src/build_vidyut_fallback.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_vidyut_fallback.py)
(`pick_primary_and_alts(lp, basic)`, regression-pinned by Fixture D of
[`RussianTranslation/tests/test_saru_gloss_pipeline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_saru_gloss_pipeline.py)
with the real kosha-0.4.0 tallies). Caveat: when kosha holds **no** Basic parse for the form
(`viDunvAna` → only `viDu`, a wrong krdanta collapse), re-ranking cannot help — that residue
is a kosha-coverage gap, not a ranking defect.

> Fable 5 (`claude-fable-5`) · 04-08-2026 · [H2194](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2194-Fable_RussianTranslation_askbatch-saru-gloss-residual-2026-08_02.08.26.md) · [PR #1113](https://github.com/gasyoun/SanskritLexicography/pull/1113)

### §520. UD `Tense=Past` is not the end of the aorist/perfect story — DCS's own `feat_formation` re-splits it, and the "too sparse to use" verdict was a denominator error

UD's `Tense` inventory has no Aorist or Perfect value, so both Sanskrit past tenses surface as
`Tense=Past` (111,167 tokens in DCS-2026). VisualDCS, its README, its M7 report and the A38
release paper all recorded this as terminal, on the ground that the DCS-specific `feat_formation`
is "present on **<2%** of verbs — too sparse to re-split them". **That figure divided 16,100 tags
by ALL ~1.01M verb tokens.** `feat_formation` only ever applies to the finite past indicative
(`upos=VERB`, `Tense=Past`, `Mood=Ind`, no `VerbForm`) — 93,329 tokens — where coverage is
**17.25%** and the split is real. Before writing off a feature as too sparse, divide by the
population it actually has to resolve.

The tag values, verified against attestations (H1486, VisualDCS
[#68](https://github.com/gasyoun/VisualDCS/pull/68)):

| value | reading | n (Tense=Past) | example |
|---|---|---:|---|
| `root` · `them` · `red` · `s` · `is` · `sis` · `sa` | Whitney's **seven aorist types** (ch. IX §§824–930) | 12,054 | `abhūt`, `avocat`, `ajījanat`, `akārṣīt`, `avadhīt` |
| `peri` | **periphrastic perfect** | 4,046 | `cintayāmāsa` |
| *(untagged)* | the **simple/reduplicated perfect** — DCS's unmarked default | 77,229 | `uvāca`, `babhūva`, `cakāra` |

**Three traps, each capable of inverting a result:**

1. **`peri` is tense-dependent.** On `Tense=Past` it is the periphrastic *perfect*; on `Tense=Fut`
   the same string is the periphrastic *future* (1,340 tokens). A query on `feat_formation` that
   does not guard on tense silently merges two different categories.
2. **`red` is the reduplicated AORIST, not the reduplicated perfect** — only 833 tokens
   (`ajījanat`, `avīvṛdhat`). The far commoner reduplicated *perfect* carries **no tag at all**.
   Reading `red` as "perfect" inverts the whole split.
3. **Untagged ≠ unknown, but untagged ≠ certain either.** The `NULL → perfect` default is sound —
   the independent 2021 DCS dump (`visual/paradigm_endings.json`) partitions the past the same
   nine ways and its own unmarked past category is likewise the simple perfect — but it is
   measurably imperfect: **1.13%** of untagged tokens carry a surface form attested *elsewhere in
   the same bucket* as a tagged aorist (`ajani` ×52, `abhūt` ×38, `avocat` ×18), and **3.54%**
   carry a form attested as `Tense=Impf` (`abravīt`, `abhavat`, `āsīt`) — an upstream
   tense-tagging inconsistency no re-split can repair.

**So quote these as bounds, never as counts: aorist is a LOWER bound, perfect an UPPER bound.**
Both floors are form-transfer measurements and therefore floors only — an untagged aorist whose
surface form never appears tagged anywhere is invisible to them. Consumers needing aorist≠perfect
must read `feat_formation` with these bounds; reading it off `Tense=Past` alone remains wrong.
A further 8,726 non-indicative `Tense=Past` tokens (Jus/Imp/Sub/Opt/Prec) carry no formation tag
at all and stay unresolved. Method, per-formation counts and the four validation checks:
[`reports/past_tense_resplit_validation.md`](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/past_tense_resplit_validation.md),
regenerable via `validate_past_tense_resplit.py`. Sibling prior art that reached the same
taxonomy independently: SanskritGrammar's `sg_mo_018_aorist.py` / `sg_mo_019_aorist_types.py`.

> Opus 5 (`claude-opus-5`) · 04-08-2026 · [H1486](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1486-Opus_VisualDCS_aorist-perfect-formation-resplit_22.07.26.md) · [VisualDCS PR #68](https://github.com/gasyoun/VisualDCS/pull/68) · measured on `dcs_full.sqlite` pin `04e0778d…`, SHA-256 `8f3b06bd…`

### §521. A code-keyed source read into a name-keyed dict is silent lossy aggregation — and the SHAPE a derived asset is serialised in decides whether consumers in other repos survive it

🟠 **Keying a code-indexed table by its human-readable names cannot fail loudly: the dict just
gets shorter. The corollary is the load-bearing half — when such a table is republished as a
derived asset, serialising it as a name-keyed OBJECT silently corrupts every downstream consumer
in every other repo, with no code change on their side; serialising it as a duplicate-preserving
LIST leaves the identical consumer code correct.**

Evidence: the [VisualDCS #70](https://github.com/gasyoun/VisualDCS/issues/70) sweep (H2293,
05-08-2026) classified all 12 readers of the DCS-2021 dump in VisualDCS and SanskritGrammar by
(the source's true key) vs (the dict key it is read into). Three measurements:

- **`timws.csv`** carries 42 tense/mood **codes** but only 30 distinct names. The name-keyed
  last-wins read in `read_2021_verbcats` dropped **39,836 examples** (2021 Imperfect Active
  reported as 4,442 instead of 35,921 + 4,442 = 40,363) — [§520](#520-ud-tensepast-is-not-the-end-of-the-aoristperfect-story--dcss-own-feat_formation-re-splits-it-and-the-too-sparse-to-use-verdict-was-a-denominator-error)'s
  companion defect, fixed in [VisualDCS PR #68](https://github.com/gasyoun/VisualDCS/pull/68).
- **`_8.csv` is the same trap 63× larger.** It is keyed by (lemma, POS) — 90,954 rows, 83,275
  distinct lemma strings, 6,340 colliding (`vid` appears 6× as `6.Ā.`/`adj`/`2.Ā.`/`adj`/`f`).
  A last-wins name-keyed read retains 2,085,186 of **4,577,461** tokens: **54.4% silently
  dropped**. Nothing was wrong in practice only because every live consumer already accumulates.
- **`tense_case_data.json` is the counter-example that proves the corollary.** VisualDCS
  republishes the 42 codes as a **list of 38 rows preserving duplicate labels** (`Imperfect`
  twice: 35,921 + 4,442; `Aorist Act.` twice: 721 + 583; zero-count codes 17/18/31/34 omitted,
  totals reconcile at 781,618 both sides). Four SanskritGrammar `verify_claims_dcs.py` scripts
  consume it **by exact label name** — the highest-risk-looking pattern in the sweep — and are
  correct, because `sum_labels()` iterates the list and therefore sums the duplicates
  (imperfect 42,803, aorist 2,452). Had that same data been emitted as `{label: n}`, those four
  scripts would have silently read the pre-fix numbers with no edit in SanskritGrammar at all.

Implication: when the natural key of a source is a **code**, either key the dict by the code or
**accumulate** — never assign. When republishing such a table as a derived asset, prefer a list
of records over a name-keyed object, because the object shape moves the defect out of the
producing repo, where it is reviewable, and into consumers that cannot see it. Two cheap guards,
now live in [`read_2021_verbcats`](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/regen_widgets.py):
print every key carrying more than one code with its breakdown, and reconcile the parsed total
against an **independently documented** figure (the 781,616 Excel-derived headline, ±10). The
second is verified by negative control — the corrupted 741,782 is a −39,834 delta and trips it,
i.e. the original defect was catchable at parse time for the years it shipped.

Residual, stated rather than implied: **cross-repo agreement of derived numbers is unmonitored.**
`KocherginaUchebnik_1998/verify_claims_dcs.py` aggregates the same table over explicit code lists
(`TOK[4] + TOK[8] + …`) and so held **40,363** — the correct figure — for the entire period
VisualDCS published 4,442. Nothing compared the two. No mechanism proposed here closes that.

> Opus 5 (`claude-opus-5`) · 05-08-2026 · [H2293](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2293-Opus_VisualDCS_name-keyed-reader-sweep-issue-70_05.08.26.md) · [VisualDCS PR #72](https://github.com/gasyoun/VisualDCS/pull/72) · [SanskritGrammar PR #589](https://github.com/gasyoun/SanskritGrammar/pull/589) · sweep report [`reports/name_keyed_reader_sweep_2021_dump.md`](https://github.com/gasyoun/VisualDCS/blob/main/reports/name_keyed_reader_sweep_2021_dump.md) · class A (auto-reproducible from `src/DCS-data-2021/`)

### §522. A bounded re-split can be displayed honestly at per-cell granularity only because its uncertainty is DEGENERATE — DCS's unmarked perfect makes the defaulted share exactly 0% or 100%, never a fraction

🟠 **`Perfect` is DEFINED as the untagged residue, so no `Perfect` cell can carry formation
evidence and no `Aorist` cell can lack it. That is not a convenient approximation — it makes
the per-cell defaulted share exactly 0.0 or 1.0, which is the only reason a per-CATEGORY
evidence flag is honest at per-cell granularity. Check this property before deciding how a
bounded inference may be shown to a learner; if it fails, per-cell marking is mandatory.**

Context: [§520](#520-ud-tensepast-is-not-the-end-of-the-aoristperfect-story--dcss-own-feat_formation-re-splits-it-and-the-too-sparse-to-use-verdict-was-a-denominator-error)
established that DCS's `feat_formation` re-splits UD's merged `Tense=Past`, and that the
result must be quoted as **bounds** (Aorist a LOWER bound, Perfect an UPPER bound). That is
sufficient for an aggregate widget, which can carry an error bar in a caption. It is **not**
sufficient for a per-root, per-cell **paradigm trainer**: a single cell rendered as plain
"Perfect" asserts to a learner exactly the thing that was inferred.

The measurement that resolves it (H2294, 05-08-2026, over the pinned `dcs_full.sqlite`),
across the **5,184** emitted (root, category, number, person) past-indicative cells of
[visual/paradigm_attested.json](https://github.com/gasyoun/VisualDCS/blob/main/visual/paradigm_attested.json):

| defaulted share of the cell | cells |
|---|--:|
| 0% (every token formation-tagged) | 1,955 |
| anything in between | **0** |
| 100% (no token tagged) | 3,229 |

**The distribution is two-valued, and it is two-valued by construction, not by luck.** The
classifier reads `feat_formation ∈ {root, them, red, s, is, sis, sa} → Aorist`,
`peri → Periphrastic Perfect`, `NULL → Perfect`. Since the third rule is the complement of the
first two, a cell is either wholly tagged or wholly untagged. Consequences worth reusing:

- **The honest marker is a category-level flag, and a per-cell error bar would carry zero
  extra information** — it could only ever print 0 or 100. The dataset therefore ships a
  `cellEvidence` map (`formation-attested` | `defaulted`) and the trainer badges it on the
  browse grid, the flashcard, **and the exported deck**, which is where the bound would
  otherwise be lost the moment the cards leave the page.
- **Assert the degeneracy in the build, don't assume it.** If DCS ever tags a simple perfect,
  or leaves an aorist type untagged inside a tagged class, the share goes fractional and a
  category flag silently starts misdescribing individual cells. `assert_evidence_degenerate()`
  fails the build at that point rather than shipping a flag that quietly stopped being true.
- **A "100% defaulted" category is not a defective one** — it is a well-founded default (V1 of
  the H1486 validation showed the independent 2021 DCS annotation uses the same unmarked
  category for the simple perfect). What is defective is displaying it *unmarked*.
- The generalisation beyond Sanskrit: **before choosing between a per-item and a per-class
  uncertainty marker, measure the within-class variance of the uncertainty.** Zero variance
  means the cheap marker is also the exact one; non-zero means the cheap marker lies.

Scope note: this concerns the **display** category only. The finite-cell identity used for the
csl-observatory E46 cross-check was deliberately left untouched, and the reconciliation re-ran
byte-identical (6,454 roots match, 0 disagree).

> Opus 5 (`claude-opus-5`) · 05-08-2026 · [H2294](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2294-Opus_VisualDCS_paradigm-attested-aorist-perfect-propagation_05.08.26.md), landed as [VisualDCS PR #74](https://github.com/gasyoun/VisualDCS/pull/74), release [paradigm-attested-resplit-2026-08-05](https://github.com/gasyoun/VisualDCS/releases/tag/paradigm-attested-resplit-2026-08-05), manifest row [kosha PR #243](https://github.com/gasyoun/kosha/pull/243). Instruments: [reports/paradigm_attested_build.md](https://github.com/gasyoun/VisualDCS/blob/main/reports/paradigm_attested_build.md) (the distribution table) and [src/DCS-data-2026/reports/past_tense_resplit_validation.md](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/past_tense_resplit_validation.md) (the bounds: ≥1.13% aorist leakage, ≥3.54% imperfect contamination). Cross-repo twin on the pipeline mechanics: [Uprava FINDINGS §322](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).

### §523. MW's abbreviation legend ("List of Works and Authors", p. xxxiii+) was never OCR'd — `MWS/prefaces/` stops at p. xxxii, one page short of the table every cross-dict legend pipeline expects

[csl-guides](https://github.com/sanskrit-lexicon/csl-guides)'s `pref_abbr_crosscheck.py` already lists `MW` in its `DICT_CATALOG` (pointed at [`MWS/prefaces`](https://github.com/sanskrit-lexicon/MWS/tree/main/prefaces), prefix `mwpref`) alongside PWG/PW/AP90/GRA/…, so running `--dict MW` looks like it should just work. It parses **0 keys**, and not from a parser bug: `mwpref01..29.md` transcribes only the title page, Preface, and Introduction (pp. v–xxxii) of the 1899 MW. `mwpref29.md` itself names the missing page — "the names of which will be found in the List of Works and Authors at p. xxxiii" — and the live CDSL toctree (`sanskrit-lexicon.uni-koeln.de/.../prefaces/mwpref.html`) confirms upstream also stops at p. xxxii; the legend was never scanned/OCR'd into this transcription at all. It is not embedded in [`csl-orig/v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt) either — the body opens directly on entry `a`, no legend preamble.

**Consequence for any future cross-dictionary work-identity / legend-crosswalk effort (UC-2 in csl-guides, or a fresh attempt elsewhere):** MW cannot join that pipeline until p. xxxiii+ is OCR'd into `MWS/prefaces/` as `mwpref30.md`+ (or wherever the page count lands) following the existing page-per-file convention. Do not hand-type a substitute legend from a secondary source — the acceptance bar for this class of pipeline is a committed OCR artifact, not an invented one. This is a genuine `@DO`: someone with access to a legible p. xxxiii scan needs to transcribe it before this class of MW work becomes possible.

> Sonnet 5 (`claude-sonnet-5`) · 06-08-2026 · [H2279](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2279-Sonnet_csl-guides_mw-legend-emit-uc2-unlock_04.08.26.md), landed as [csl-guides PR #164](https://github.com/sanskrit-lexicon/csl-guides/pull/164), release [v0.13.1](https://github.com/sanskrit-lexicon/csl-guides/releases/tag/v0.13.1). Delta documented in [`scripts/pref_abbr_crosscheck.py`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/scripts/pref_abbr_crosscheck.py) header and [preface-front-matter-enrichment-use-cases.md](https://github.com/sanskrit-lexicon/csl-guides/blob/main/docs/dictionaries/preface-front-matter-enrichment-use-cases.md) UC-2.

### §524. A parallel-corpus column can be misaligned against its OWN row key — Griffith's English is off by the vālakhilya block for RV 8.49–8.103, and a char-count selftest cannot see it

[`pwg_ru/griffith_en_1896.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/griffith_en_1896.json) was extracted (H1843) from a multi-language RV HTML table and keys each stanza `mandala.sūkta.verse`. The H2334 EN citation-TM pilot maps a PWG `ṚV.` citation onto it by stripping the mandala's zero-pad and treating sūkta/verse as identical — `01_rigveda:1.1` → `1.1.1`. That holds for 9,874 stanzas and **fails for 678**: in mandala 8 from sūkta 49 the English column carries the eleven vālakhilya hymns *appended at the end* while the key numbers them *inline* at 8.49–8.59, so everything from 8.49 to 8.103 is displaced by eleven hymns. `lookup('ṚV.', '8,60,1', lang='en')` returns `status=hit`, `rights_flag=pd` and a fluent English verse **of the wrong hymn**, with no signal at the call site — the exact failure the same module's `_RAMA_GORRESIO_BOOKS` comment refuses to allow on the Rāmāyaṇa side ("an in-range locus would return the WRONG verse's translation silently"), where books 3–6 are held `UNMAPPED` instead.

**Two transferable lessons, and the second is the one that generalises past Sanskrit.**

- **A row key proves the row exists, not that every column in it belongs to that row.** When a derived asset is a *column extracted out of a parallel table*, the key travelled with the skeleton and the content travelled with the column; the two can drift independently and nothing in the file records that they did. Verse counts per sūkta matched **103/103** in mandala 8 — the structure was perfect and the content still wrong, so a structural check is not evidence of alignment.
- **A char-count assertion cannot distinguish the right passage from a wrong one of similar length.** The pilot's selftest pinned `1.1.1` and `10.90.1` on status, rights flag, resolved location and `len(text)`, and both units sit outside the break. The check that finds this costs one query: compare the extracted column against **another column of the same row** — here Griffith's English against the Sanskrit at the same `canonical_id`, scored language-independently on deity-name anchors (~92% on aligned material, **19.8%** on 8.49–8.103). Any parallel-corpus extraction can be audited this way without a human reading either language.

Instrument: [`src/audit_griffith_en_alignment.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_griffith_en_alignment.py) (`--selftest` exits non-zero on the live break — deliberately not yet wired into CI). The RU lane is unaffected: it reads `#ru` from `corpus.db`, whose columns agree throughout. Nothing consumes the EN lane yet — [`corpus_gate._citation_reuse`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py) still calls `consult_card()` with the default `lang='ru'` — which is the only reason a wrong verse has not already reached a card. The other language columns of the same source HTML should be re-checked before any of them is promoted to an of-record lane.

> Opus 5 (`claude-opus-5`) · 07-08-2026 · [H2361](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2361-Opus_SanskritLexicography_griffith-en-rv-mandala8-valakhilya-misalignment_07.08.26.md), from a code review of the shipped H2334 pilot ([v1.144.15](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md), [PR #1182](https://github.com/gasyoun/SanskritLexicography/pull/1182)). Full evidence: [GRIFFITH_EN_RV_MANDALA8_VALAKHILYA_MISALIGNMENT_07-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2361/GRIFFITH_EN_RV_MANDALA8_VALAKHILYA_MISALIGNMENT_07-08-2026.md).

### §525. An interactive tool outside Python's call stack needs a durable intent before the call and response-bound evidence inside finalization — a saved response alone cannot prove it was authorized

`GatewayCall.invoke()` originally made one correct in-process sequence: reserve, call,
validate, finalize. The router.cheap Agent tool lives outside that stack, so neither half of
the obvious manual workaround is safe. Calling first and pasting the response later has no
pre-spend authorization; reserving first and finalizing from a later process loses the identity
of the response if that process dies after ledger finalization but before saving its envelope.

The reusable transaction shape has **two independent idempotency keys**. Prepare atomically
stores an operation hash in the reservation (run, ceiling, route, model, purpose, provenance,
timeout, waiver, request and schema) and derives its nonce from that durable reservation. Record
atomically stores a second fingerprint with finalization (ticket + complete public response +
semantic envelope). The first prevents competing/resumed prepares from spending twice; the
second prevents a different response from occupying the crash window after finalization. A
read-only report must distinguish a reserved call with no ticket from a pending ticket, because
the former is ambiguous spend, never a reusable free slot.

Two details generalize. First, an artifact cannot literally contain the SHA-256 of its own final
bytes; define the in-envelope `saved_envelope_sha256` over the canonical envelope with that field
omitted, and separately hash transport/file bytes when needed. Second, an accounting waiver is a
predicate over exact provenance, not a default value: absent usage on the authorized route maps to
`cost_evaluable=false` and envelope `observed_cost_usd=null`, while the numeric ledger floor stays
separate. Reusing the waiver on c4 or turning unknown into `$0` is a contract failure.

> Codex Sol (`gpt-5.6-sol`) · 10-08-2026 · H2533 (Codex) — durable router.cheap two-phase Agent bridge, then mint the Opus canary. Instrument and 11-group fault matrix: [`gateway_external.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_external.py) · [`ROUTER_CHEAP_TWO_PHASE_AGENT_BRIDGE_10-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2533/ROUTER_CHEAP_TWO_PHASE_AGENT_BRIDGE_10-08-2026.md).

### §526. A second reference is the only cheap way to separate "the model knows this dictionary" from "the model can gloss" — and the premium it exposes is small, real, and largest exactly where memorisation is suspected

Every number in the org's definition-generation eval (H730/H752/H972) was scored against
Monier-Williams 1899 — a public-domain text certainly present in every model's pretraining
data. That design cannot separate *reproduction of MW's wording* from genuine sense coverage:
the A1−A2 delta isolates what corpus attestations add, but nothing inside an MW-only design
isolates what memorisation contributes. The published caveat said so and stopped there.

**Measured (H2408, n=333 of the frozen 500, 5 arms, 333/333 judged, 0 nulls):** re-scoring the
same *frozen* candidate glosses against Gérard Huet's **French** Heritage glosses — a different
lexicographer, century and language — costs one judge pass, no regeneration, and answers the
question directly.

1. **The arm ranking is reference-invariant.** `F1_fable_ctx > A1_chat_ctx > A3_reasoner_ctx >
   A2_chat_noctx > A0_random_floor`, identically under the MW judge and the cross-lingual
   French judge. Before this, the strongest available claim was "F1 leads on the dictionary it
   was scored against".
2. **The MW-familiarity premium is real but small:** paired per-item
   `Δ = adequacy_MW − adequacy_FR` is **+0.13…+0.25** on a 0–5 scale (bootstrap 95% CI over
   5,000 resamples excludes 0 for all four system arms; exact two-sided sign test
   p ≤ 1.5e-4). That is ~3–5% of scale — enough to bias a reported number, nowhere near enough
   to manufacture a ranking.
3. **The floor's premium is NOT significant** (+0.030, CI includes 0) — as it must be, since a
   seeded derangement of MW glosses has no sense coverage to be credited for against *either*
   reference. That asymmetry is what rules out "the judge simply prefers English candidates
   when the reference is English" as the explanation, and makes the premium a property of
   systems producing MW-shaped content rather than a judge artefact.
4. **It is largest where memorisation is most suspected.** `A2_chat_noctx` — given no
   attestations, so its only route to a gloss is parametric recall of MW — carries the biggest
   premium (+0.246); the best arm carries the smallest (+0.132). Contamination inflates
   MW-scored numbers slightly and inflates the memorisation arm most, which is the direction
   the caveat predicted rather than a new confound.

⚠️ **The reusable methodological rule: a cross-lingual second reference is a JUDGED
measurement, not a surface-metric one.** Against French, token-F1 collapses to 0.012–0.037
(vs 0.101–0.338 against MW) and chrF compresses every arm into 7.26–12.09 with the floor at
8.73 — a 3.4-point spread that cannot survive noise, even though it does still happen to order
the arms correctly. Multi-reference chrF is dominated by the same-language reference (+0.76 for
the best arm) and adds essentially nothing. Reference divergence itself is chrF 17.72 /
token-F1 0.040: two independent glosses of one headword share almost no tokens across a
language gap. So report the judge, gate it (floor separation held across the language gap:
0.165 vs 3.99–4.54), and treat cross-lingual chrF as decoration.

Two further transferable pieces. **The frequency-gradient inversion is diagnosable only with a
second reference** — per-cell chrF-MW rises as frequency *falls* (low/mono 45.22 > mid/mono
37.09 > high/mono 26.32), which reads as skill at rare words; against French the same cells
compress to 11.49–17.34, confirming it as an artefact of MW's gold-length distribution
(high-frequency MW entries have much longer, more complex gold). And **a restricted reference
can be consumed without redistributing it**: the eval commits `mw_key1` + entry anchor +
**SHA-256** + word count instead of Heritage's LGPLLR gloss text, and the scorer *refuses to
run* when a digest stops matching the local checkout — rights compliance that also makes the
join reproducible, rather than a reason to park the work.

Residual, stated rather than implied: one judge model (`deepseek-chat`) scored both references,
so a judge-side French-vs-English asymmetry would masquerade as an MW premium. The floor result
argues against a large one, but a second judge family is what would settle it — and the
human-scored subsample remains owed before any paper-grade claim. Heritage is also not
causally unrelated to MW's tradition; "independent" here means independent authorship, century
and language.

> Fable 5 (`claude-fable-5`) · 09-08-2026 · [H2408](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2408-Fable_kosha_definition-gen-gloss-wsd-pilot_07.08.26.md) — Heritage second reference for the defgen eval. Protocol + all numbers: [DEFGEN_HERITAGE_SECOND_REFERENCE_EVAL.md](https://github.com/gasyoun/kosha/blob/main/docs/DEFGEN_HERITAGE_SECOND_REFERENCE_EVAL.md) · harness [defgen_heritage_ref.py](https://github.com/gasyoun/kosha/blob/main/scripts/defgen_heritage_ref.py) + [defgen_heritage_delta.py](https://github.com/gasyoun/kosha/blob/main/scripts/defgen_heritage_delta.py) · [kosha PR #364](https://github.com/gasyoun/kosha/pull/364), [v0.110.0](https://github.com/gasyoun/kosha/releases/tag/v0.110.0).

### §527. A schema selftest written from the schema's own constants is blind to a prompt/schema contradiction — the defect it cannot see is exactly the one that burns a paid call

The router.cheap two-ticket canary froze its Ticket 2 output schema only after a 24-case
selftest passed: one golden instance accepted, 23 deterministic defects rejected (dropped,
merged, reordered and extra senses; untranslated German; Latin leak; empty Russian; `{Tn}`
placeholder leakage; stripped markup; key drift; promotion claim; invented `government`;
provenance-hash drift; additional properties at three nesting levels). The very next paid call
failed the gate anyway, on `malformed_output`.

The cause was invisible to that selftest by construction. The prompt told the model to
reproduce each sense's German skeleton line **exactly as inlined**, and the fixture's lines
open with a sense marker — `— 1〉 {%eine Schildkröte%}.` The frozen schema pinned `german` to
the gloss alone — `{%eine Schildkröte%}.` Both artifacts were authored in the same session and
each was internally consistent; they simply disagreed, and since every selftest fixture was
built *from the schema's constants*, no case ever compared the schema against the prompt. The
model obeyed the prompt verbatim and rendered a clean 3/3 (черепаха / небольшая рыба / водное
растение) with zero defects in any of the 13 enumerated classes. The gate was right to fire and
the sitting was still NO-GO — the loss was the last authorised reservation, spent proving that
two of our own strings differed.

Two generalizations. First, **any literal shared between a prompt and its validating schema
must be generated once from the source fixture, never hand-typed into both** — and the selftest
must include at least one instance assembled from the prompt's own inlined text, which is the
only fixture that can fail this way. Second, a defect taxonomy is not coverage: 23 rejection
cases created real confidence about *model* misbehaviour while saying nothing about *harness*
self-consistency, and confidence in the wrong axis is what let the freeze proceed.

Adjacent, same sitting: `gateway_attestation.py` filters transcript turns to
`isSidechain: true`, but this harness records `Agent` calls as **main turns** (101 main, 0
sidechain in the whole session), so the default filter observed 0 turns and returned
`model_matches_request: null` — NO-GO under the canary contract, from a tool that was working
as designed against a transcript shape it did not expect. `--include-main-turns` recovers an
attestation (`claude-opus-5`, matching, on both tickets) but widens the window to turns the
session itself occupies, so it attests the served model for *the window*, not provably for *the
single dispatch inside it*. Closing that needs a per-dispatch identifier binding one `tool_use`
id to one served-model record, not a wider time range. Relatedly, three `Agent` tool_use blocks
backed two paid dispatches — one blocked by a subspawn guard, one rejected because the ticket's
route label `router-cheap-agent` is not a harness `subagent_type` — so call counts must be read
from each block's `tool_result`, never from the block count.

> Opus 5 (`claude-opus-5`) · 10-08-2026 · H2539 (Opus 5) — attested router.cheap two-ticket live canary at v1.144.28, verdict NO-GO. Report: [CANARY_QUALIFICATION_REPORT_ROUTER_CHEAP_NO-GO_10-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/CANARY_QUALIFICATION_REPORT_ROUTER_CHEAP_NO-GO_10-08-2026.md) · selftest [t2_schema_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/t2_schema_selftest.py) · attribution audit [t2_defect_audit.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t2_defect_audit.txt).

### §528. A top-band-only gold set for BLI reports 99.5% coverage and hides a 0%–100% per-stratum spread — the instrument cannot see what the research question asks

`corpus_lexicon.jsonl`'s automatic 400-lemma gold set (H1521, top-400 by DCS frequency band)
returned coverage = 0.995 — so high it looked like a system property. It isn't. Probing the
full candidate frame (12,939 glossable Koch × DCS lemmas) across all five frequency bands
shows per-stratum presence in the lexicon runs from 1.00 (band-5 ADV) all the way down to
**0.00** (band-1 VERB). The top-band set can only sample from the 0.96–1.00 end of that
range, so its coverage figure describes the frame, not the lexicon. Frame-wide for the
stratified 500-row B1 gold set: **321/500 = 64.2%**.

**Implication.** A headline coverage number from a non-stratified BLI gold set is not
portable to other lemma populations. Report per-stratum presence alongside any aggregate; a
cell with near-zero presence yields coverage evidence but no P@1 signal, and mixing the two
silently downgrades retrieval failures to absence.

**Source.** [BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md)
§1/§7 · [`frame_presence_report.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/frame_presence_report.py)
· [SanskritLexicography PR #1634](https://github.com/gasyoun/SanskritLexicography/pull/1634),
[v1.144.30](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.144.30).

> Fable 5 (`claude-fable-5`) · 10-08-2026 · [H2401 (Fable 5) — ACL B1: BLI gold-set design and annotation protocol](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2401-Fable_SanskritLexicography_bli-b1-gold-set-design_07.08.26.md) · full per-stratum table and scripts in the protocol doc linked above.

### §529. An Agent result already carries the exact dispatch binding; widening a transcript window throws that evidence away

H2539's v1 attestor searched assistant turns inside a start/end window and inferred a served
model only when every selected turn agreed. That lost the harness's stronger native relation.
The Agent call appears as one `tool_use` block with an immutable `id`; its user-side result has
the same value in `tool_result.tool_use_id`, while the event's structured `toolUseResult`
contains `status`, `resolvedModel`, `agentId`, and usage. The result event also names the source
assistant UUID. Those fields identify the dispatch directly; time-window consensus and
`isSidechain` filtering are unnecessary and can only add unrelated turns.

H2554 binds the ticket's exact prompt SHA-256 to that one tool use, requires exactly one use and
one result, requires a matching source UUID and `status=completed`, and carries the dispatch ID
through wrapper, v2 attestation, sealed envelope, recovery report, and JSON Schemas. Missing,
wrong, duplicate, replayed, incomplete, refused, prompt-substituted, or malformed-transcript
records fail closed. Main and sidechain calls share one path; the flag is evidence, not an
assumption about where calls live. H2539 replay found both successful calls uniquely, but their
operator prompts contained rather than byte-equalled the old ticket prompt, so the old v1
artifacts remain explicitly `legacy_window`, `dispatch_attested=false`, and non-promotable.

> Codex Sol (`gpt-5.6-sol`) · 10-08-2026 · H2554 (Codex) — router.cheap canary contract and exact-dispatch attestation repair. Instrument: [`gateway_attestation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_attestation.py) · report: [`ROUTER_CHEAP_CANARY_CONTRACT_DISPATCH_ATTESTATION_REPAIR_10-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2554/ROUTER_CHEAP_CANARY_CONTRACT_DISPATCH_ATTESTATION_REPAIR_10-08-2026.md).

### §530. "Whole-card lane" means un-split, not one-call-per-card — production still BATCHES whole cards

The pwg_ru presplit predicate (`gen_opt_harness2._presplit_hit`) splits a citation-dense card
into fragment groups, and the natural reading of "the cards production takes whole" is that each
such card is one agent call. **It is not.** The generator packs whole cards into batches before
dispatch: for H2630's four-card manifest it emitted `batches: [["idAnIm","prasU"],
["rAtra","spfS"]]` with `presplit_keys: []`, i.e. **2 agent calls for 4 un-split cards**.

Two distinct properties are being conflated by the one phrase:

| property | what decides it | H2630's four cards |
|---|---|---|
| **un-split** — the card is not cut into fragment groups | `_presplit_hit` (cite floor, sense budget) | yes, all four |
| **one card per call** — the call carries exactly one card | the generator's batching, an output-budget pack | **no** — 2 per call |

Why it matters beyond one handoff: any rig that issues **one card per call** and calls itself
production-faithful for the whole-card lane is measuring a call shape production does not use,
and its absolute wall-clock and token figures are not production figures. H2598 made exactly
this inference when tabling its Option A ("production-faithful, honest"), and the manifest
refuted it a day later. A paired A-vs-B comparison survives — both arms are equally affected —
but the absolutes do not, and a receipt that quotes them as production cost is wrong.

**Check it, don't infer it.** The manifest already answers both questions directly:
`presplit_keys` for the split question and `batches` for the call-shape question. Reading the
first and assuming the second is the error.

> Opus 5 (`claude-opus-5`) · 13-08-2026 · [H2630 (Opus 5) — PREP compare Option A: 4 pairs on the 4 whole-card cards](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2630-Opus_SanskritLexicography_prep-compare-whole-card-4-pairs-option-a_13.08.26.md) · evidence: [h2630/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2630/README.md) · [PR #1670](https://github.com/gasyoun/SanskritLexicography/pull/1670). Sealed into the plan's `known_non_equivalences`, so a later reader of `plan.json` cannot re-make the inference.

### §531. *Ārṣa prayoga* is a one-way licence — it excuses a deviant form in a POST-Vedic text by appeal to ancient usage, and never authorises describing Vedic material in classical or epic terms

The tempting move, when an automated reviewer or a rubric flags "classical rules applied to a
Ṛgvedic hymn", is to answer that the tradition itself legitimises such deviations — «язык
аршея», the language of the ṛṣis, by which the Rāmāyaṇa's departures from Pāṇini are excused.
**That defence does not reach the Vedic direction.** Four independent grounds, none of which
depends on the others:

1. **Pāṇini's architecture makes Vedic the *marked* domain.** The Aṣṭādhyāyī's default object is
   the *bhāṣā*; Vedic material enters only under explicit domain markers (`chandasi`, `mantre`,
   `nigame`, `brāhmaṇe`) plus open variation rules — `bahulaṃ chandasi`, `chandasi śāyaj api`
   (3.1.84), `vyatyayo bahulam` (3.1.85). Rules run classical → *extended to* → Vedic; nothing
   projects classical norms back onto the Veda as a standard it must meet (Bronkhorst,
   [*Pāṇini and the Veda reconsidered*](https://www.researchgate.net/publication/263470324_Panini_and_the_Veda_reconsidered)).
2. **The tradition's one explicit rule about direction is a prohibition, and it runs the other
   way.** The Mahābhāṣya cites `chandovat kavayaḥ kurvanti` — "poets do as in the Veda" — and
   rejects it: `na hy eṣā iṣṭiḥ`, Vedicizing in non-Vedic language is a *doṣa* (Kawamura,
   *JIBS* 65.3 (2017): 1059–1065). A tradition that refuses even Vedic→classical transfer a
   fortiori licenses no classical→Vedic one.
3. **The categories are not there to be applied.** RV has a productive subjunctive (*leṭ*), an
   injunctive, a large infinitive inventory and a living aorist with distinct functions — lost or
   vestigial in classical Sanskrit (Whitney, chs. VIII, XI). "Classical aorist" in an RV verse
   names a category the classical language does not possess in that function: a **category
   error, not a liberty**.
4. **The boldest traditional Veda→epic reader stops short of it.** Nīlakaṇṭha Caturdhara
   (*Mantrarāmāyaṇa*, *Mantrabhāgavata*, Harivaṃśa commentary) reads epic *meaning* into ~60 RV
   verses and never claims RV *morphology* follows classical rules (Minkowski, HAZU 2005).

**Three facts worth carrying separately from the ruling.** (a) **`ārṣa` in Pāṇini is not this
concept at all** — it occurs once, at **A 2.4.58**, as a label for a *taddhita* affix class
denoting descent from a ṛṣi; in the Prātiśākhya/Bhāṣya layer it names the *Saṃhitā* text against
the *padapāṭha*. The "exempted despite the rules" sense is a later commentarial extension, so
citing Pāṇini for the exemption is itself an anachronism. (b) **An attested instance of the
excuse-move**, verbatim: Śrīdhara Svāmin's *Bhāvārthadīpikā* glosses `hari-viriñci-hareti
saṃjñāḥ` with `sandhiḥ ārṣaḥ` — "the sandhi is that of the ṛṣis" (*hara* + *iti* → *hareti*);
verse number unconfirmed, the quotation attested. (c) **Where the epic licence actually comes
from**: epic deviations are "generally considered to be on account of interference from Prakrits,
or innovations, and **not** because they are pre-Pāṇinian" (Oberlies, *A Grammar of Epic
Sanskrit*, de Gruyter 2003, via reviews). So a style rule or passport clause that grants epic
latitude must call it epic-specific (metri causa, Middle-Indic contact) and must **not** claim
the deviations are archaisms.

**Also load-bearing for any epic-vs-Vedic checker:** *epic Sanskrit has no recorded accent at
all*. A claim that a hymn's accent follows «нормы эпического языка» is not a debatable
periodisation — it describes a norm that does not exist.

**Not verified, do not report as settled:** the exact Mahābhāṣya locus of `chandovat kavayaḥ
kurvanti | na hy eṣā iṣṭiḥ` (known via Kawamura 2017; PDFs 403'd); any named MBh verse where
Nīlakaṇṭha writes *ārṣa* (his commentary is not searchable text); any named Rām verse where
Govindarāja or Maheśvaratīrtha does; Oberlies' own pages on *ārṣa*; the verse number of the
Śrīdhara gloss.

> Opus 4.8 (`claude-opus-4-8`) evidence pass 19-07-2026 · written up by Opus 5 (`claude-opus-5`) 14-08-2026 · [H1325 (Opus 5) — does *ārṣa prayoga* invalidate the `vedic-classical-anachronism` gold-case rubric](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1325-Opus_RuWritingStyles_arsa-prayoga-vedic-gold-case-validity_19.07.26.md) · ruling: [RuWritingStyles docs/arsa-prayoga-vedic-gold-case-ruling.md](https://github.com/gasyoun/RuWritingStyles/blob/main/docs/arsa-prayoga-vedic-gold-case-ruling.md) · [PR #157](https://github.com/gasyoun/RuWritingStyles/pull/157). Hypothesis `R2607-05` in [QUESTIONS_LOG.md](https://github.com/gasyoun/Uprava/blob/main/QUESTIONS_LOG.md) resolves **refuted**. The eval-methodology half — a rubric that names one of two planted claims — is [Uprava FINDINGS §386](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).

### §532. A named DeepSeek-v4-flash judge on frozen grade_gold reaches Spearman ρ=0.4195; the proxy ρ=-0.0351 stays preliminary and is never comet

🟠 **The first genuine named semantic QE that served on this box against the frozen A/B/C gold is DeepSeek `deepseek-v4-flash` (reference-free JSON judge), Spearman ρ = 0.4195 on a deterministic n=80 A/B/C slice of [`gold/grade_gold.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/grade_gold.jsonl) (full-gold sha256 `72c282933c395702324db1072dcfe49cae1feac3bb8db50e9737f7b75ecb6ed7`). Mean score by grade is monotone: A 0.9241 / B 0.8465 / C 0.5295. That clears the 0.40 defensible floor.** The surface-shape proxy on the same gold remains ρ=**-0.0351**, labelled preliminary ([§70](#70-pwg_ru-tm-composite-grade-a-is-consensus-gated-57-and-a-reference-free-surface-qe-cannot-detect-wrong-sense)). Neither number is COMET-QE: `unbabel-comet` still has no cp314 wheel, and LaBSE (`sentence-transformers/LaBSE`) failed to load here with WinError 1455 (pagefile). `--qe comet` must keep returning the proxy under the name `proxy`.

Implication: next-wave measurement uses `--qe deepseek`, never relabels proxy or LaBSE as comet, and treats Wave 1 as immutable. A live no-TM vs graded-fragment-TM run on the frozen H2684 sample (n=9 translatable cards) moved quality 0.590 → 0.800, edit 0.609 → 0.471, serious-error 6/9 → 5/9, at $0.004138 (`deepseek-v4-flash`, price card `pre-1608`, 36 billed calls). Recurring formulas took the gain; long sense wrappers still returned empty hypotheses.

> Grok 4.6 (`grok-4.6`) · 14-08-2026 · [H2686 (Grok 4.6) — PWG TM genuine semantic QE and live retrieval evaluation after first scale wave](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2686-Grok_RussianTranslation_pwg-tm-semantic-qe-retrieval-w2_13.08.26.md) · [GRADE_CALIBRATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/GRADE_CALIBRATION.md) · [RETRIEVAL_EVAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/RETRIEVAL_EVAL.md) · class A (re-run `python src/tm_grade.py calibrate-gold --qe deepseek` against the committed slice; live retrieval needs `DEEPSEEK_API_KEY`).

### §533. H2704 Flash PREP −3.9% is a real point-estimate; the 20% dual-lane NO-GO does not make it zero

🟠 **The H2704 product adoption verdict is NO-GO (both lanes miss a 20% cheaper-than-one-shot bar). That is not the same statement as “Flash cache saved nothing.”** On the sealed 50-pair Flash PREP ledger, cost per unique parseable card is **$0.000839** against the H2675 one-shot **$0.000873** (**−3.9%**). Same-card incremental save (cold $0.000441 − warm $0.000397) / cold is **9.9%**; cache-hit tokens rose 87 → 445. The paired USD 95% CI **[−$0.000134, +$0.000040] includes zero**, so the *magnitude* is INCONCLUSIVE at n=50, not a licence to write 0%. Generation Pro at **$0.02780**/`det_clean` vs H2676 **$0.01991** is **+39.6%** because the pair *buys two Pro generations per card*, and the first slot already had ~13.6k cache-hit tokens — not an empty-prefix cold. First-200 local TM yield was **0/200**. `ADOPTION.json` `unique_clean: 1` / `$0.041929` per PREP card is a generation-style `det_clean` leak; quote the report’s 50-card figure.

Implication: keep `DEFAULT_MODEL` = Flash and keep canonical hashes unchanged. Do not AND the next Flash sitting to a Pro pair. The re-test shipped as [H2756 (Grok 4.6) — H2754 title-collision residual: Flash PREP one-shot vs incremental warm](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2756-Grok_SanskritLexicography_h2754-flash-oneshot-vs-warm-residual_14.08.26.md) ([§534](#534-h2756-re-test-of-flash-prep-incremental-save-on-a-fresh-50-is-inconclusive-at-02)). Process twin: [Uprava FINDINGS §401](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).

> Grok 4.6 (`grok-4.6`) · 14-08-2026 · [H2704 REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2704_prep/REPORT.md) · [CONCLUSIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/CONCLUSIONS.md) · [H2703 REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/REPORT.md) · [SanskritLexicography#1710](https://github.com/gasyoun/SanskritLexicography/pull/1710) · class A (recompute from the sealed `prep50/run/summary.json` + H2675/H2676 reports; no live host).

### §534. H2756 re-test of Flash PREP incremental save on a fresh 50 is INCONCLUSIVE at 0.2%

🟠 **A fresh 50-miss Flash PREP pair sitting (first-200 minus the H2704 50, salt `h2756-prep-50-v1`) does not show a same-card incremental save whose CI excludes zero.** Reliability **99/100** parseable, served `deepseek-v4-flash` on every parseable slot, retry amplification 1.0, $0.038405, canonical hashes unchanged. Primary metric B is the H2704 ratio-of-means: (mean cold − mean warm) / mean cold on 49 complete pairs = **0.2%**; bootstrap 95% CI **[−40.0%, +23.8%]** includes 0. Dollar delta mean +$0.000001, CI crosses zero. That is **INCONCLUSIVE**, not “no economy”. Mean-of-ratios is not scored (small-cold / noisy-warm pairs explode it to a fake −60%). Denominator A (pair cost / unique cards, *not scored*) is $0.000784 vs H2675 $0.000873 (−10.2%). One `iz` cold slot was empty transport; its warm sibling is excluded from B. Product NO-GO from H2704 is unchanged. `DEFAULT_MODEL` stays Flash. H2754 could not run: precheck exit 4 on [SanskritLexicography#1713](https://github.com/gasyoun/SanskritLexicography/pull/1713) (docs residual).

Implication: do not adopt provider prefix cache for Flash PREP repeats from this sitting; do not write 0%. Keep the 0.2% point estimate. Do not re-run H2754.

> Grok 4.6 (`grok-4.6`) · 14-08-2026 · [H2756 REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2756_flash/REPORT.md) · [H2756 (Grok 4.6) — H2754 title-collision residual](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2756-Grok_SanskritLexicography_h2754-flash-oneshot-vs-warm-residual_14.08.26.md) · class A (recompute from `h2756/run/summary.json` via `cache_prep_h2756.paired_save_metrics`).

### §535. A CRLF key list makes every pilot input land under a phantom `~000d` stem, and the failure surfaces as "missing input", not as an encoding error

🟠 **Any reproduce recipe of the form `python src/_pilot_gen_merged.py $(tr '\n' ' ' < <keys>.txt)` is CRLF-fragile on Windows, and it fails far from the cause.** The key lists under [`src/pilot/h1210/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pilot/h1210) have CRLF line endings, so `tr '\n' ' '` leaves a `\r` welded to every key. Nothing rejects it: `safe_name()` in [`src/safe_filename.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/safe_filename.py) is a *total* function that escapes any non-`[a-z0-9-]` character as `~%04x`, so `SAluqa\r` becomes the perfectly valid stem `_s_aluqa~000d` (`0x0d` = CR). The generator then reports success — "wrote 90 merged pilot inputs" — and the next step dies with a bare `FAIL: missing input for _s_aluqa`, which reads like repo drift, a renamed asset, or a deleted gitignored input. Measured 15-08-2026 while rebuilding the H1210 A/B rig: 85 of 100 frozen card ids resolved only as `~000d` variants, 10 more looked missing, 5 matched by luck (their keys were the last line, unterminated).

Implication: in every recipe that pipes a key list into a generator, strip CR first — `tr -d '\r' < keys.txt | tr '\n' ' '`, and `tr -d '\r' < card_ids.txt | paste -sd,` for the comma form. With the CR stripped, all 100 frozen H1210 ids resolve exactly, so a `~000d` (or any `~00xx`) stem appearing in [`src/pilot/input/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pilot) is a **diagnostic**: it means a control character reached `safe_name()`, not that the key is exotic. The general trap: a total escaping function converts an input-hygiene bug into a silent namespace fork, so the loud error lands one step downstream of the code that could have caught it.

> Opus 5 (`claude-opus-5`) · 15-08-2026 · [H2787 (Opus 5) — Funded re-run of the H1210 DeepSeek-vs-Claude A/B](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2787-Opus_SanskritLexicography_h1210-ab-rerun-funded-both-arms_15.08.26.md) · class A (reproduce: run either form of the recipe and list `src/pilot/input/`).

### §536. The re-glue cards' citations were dead because nothing called the repo's own resolver — and Cologne's precomputed table would have been a downgrade

🟠 **`ls_resolver.py` resolves 83.6 % of the pwg_ru store's `<ls>` citations; Cologne's precomputed [csl-lslink](https://github.com/sanskrit-lexicon/csl-lslink) table resolves 79.3 % and wins ZERO citations the resolver misses.** Measured 15-08-2026 by [`ls_coverage_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_coverage_probe.py) over all **41,115** `<ls>` occurrences in `pwg_ru_translated.jsonl` (11,603 rows): both resolve 32,586 (79.3 %) · resolver-only 1,789 (4.4 %) · **table-only 0 (0.0 %)** · neither 6,740 (16.4 %). On the 32,586 both resolve they disagree on **0** hrefs — that mutual agreement across two independently-built resolvers is the strongest evidence the repo's Dart→Python port is faithful that exists anywhere in the org.

Two traps this measurement disarms, both of which cost real time before the numbers existed:

1. **The table looks like the obvious source and is not.** It is Cologne's own artifact, 277,468 rows, generated from `pwg.xml` — every instinct says use it. It is strictly dominated. Worse, a naive literal-string join against it hits only **5.1 %**, because PWG keeps its sentence-final period *inside* the element (`<ls>MBH. 12,8081.</ls>`) while the Cologne key does not; stripping that one character lifts the same join to 79.3 %. A 5 % result therefore means "the join is wrong", never "the data is missing".
2. **"Unresolved" is two buckets, not one, and only one is work.** Of the 16.4 % that resolve nowhere, **1,484 occurrences (3.6 %) are bare abbreviations with no locus at all** (`<ls>GORR.</ls>`, `<ls>ed. Bomb.</ls>`) — unlinkable by construction, nothing to point at, no research will ever fix them. The remaining **~7,000 (17.1 % of all occurrences, counting near-misses) carry a real locus no pattern covers** — that, and only that, is the mintable gap. Reporting one undifferentiated "unresolved" number overstates the work by roughly a fifth.

Implication: **never write a second `<ls>` resolver.** Call [`ls_resolver.generate_href`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py) (via [`ls_links.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py) for rendering, or `pilot/build_article_site.py::_ls_href` inside the site). Keep the csl-lslink table only as a cross-check oracle — `LsLinks(verify=True)` records disagreements — and re-run the probe before trusting either number again. The reason the published [re-glue sheet](https://gasyoun.github.io/vote/sheets/h180_reglue.html) showed dead citations was never a data gap: the renderer simply never called the resolver the repo already had, which is exactly the failure mode [/prior-art](https://github.com/gasyoun/claude-config/blob/main/commands/prior-art.md) exists to catch.

> Opus 5 (`claude-opus-5`) · 15-08-2026 · [H2827 (Opus 5) — H180 re-glue vote v2: join Cologne ls-links, surface the glue typology, normalize NWS gloss separators](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2827-Opus_SanskritLexicography_reglue-vote-v2-ls-links-typology_15.08.26.md) · class A (reproduce: `python src/ls_coverage_probe.py`).
>
> ⚠️ **Point 2's sizing is superseded by [§537](#537-the-mintable-citation-gap-is-60-occurrences-not-7000--the-resolver-is-at-the-ceiling-its-scan-corpus-allows).** "The mintable gap" is real as a *category*, but it is 60 occurrences, not ~7,000: measured, almost all of it cites works Cologne has never scanned. The point-2 framing implied a research workstream that does not exist.

### §537. The mintable citation gap is 60 occurrences, not ~7,000 — the resolver is at the ceiling its scan corpus allows

🔴 **Of the 5,257 `<ls>` occurrences that carry a real locus and resolve nowhere, exactly 60 (1.1 %) can be reached by writing code. The other 5,197 cite books Cologne has never digitised.** So the ceiling for any code-only citation effort is 83.6 % → **~84.7 %**, and "mint the remaining 17 %" is not a project that exists. Measured 15-08-2026 by [`ls_gap_repair.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_gap_repair.py) over all 41,115 store occurrences; full write-up in [LS_CITATION_GAP_MINE_2026-08-15.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/LS_CITATION_GAP_MINE_2026-08-15.md).

Two independent checks agree that the residue is a digitisation limit, not a code limit:

1. **The works are simply absent.** The 15 biggest unresolved sources are Suśruta (280), Śāṅkhāyana (241), Chāndogya (198), Āśvalāyana (197), Prabodhacandrodaya (170), Kauśika (157), Mṛcchakaṭikā (146) and so on — **309 distinct works**, none with a scan in the [sanskrit-lexicon-scans](https://github.com/sanskrit-lexicon-scans) org.
2. **The resolver is not the bottleneck.** Cologne hosts 101 scan repos, of which 53 are citable text scans (the rest are the CDSL dictionaries and infrastructure). The resolver already routes to **49 of the 53**; the four it misses are alternate editions of works already routed, unlocking **zero** additional citations ([`ls_gap_unrouted_viewers.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_gap_unrouted_viewers.py)). There is no hidden inventory.

**The methodological half is the more reusable finding: a prefix is not a work, so classifying citation gaps by first-token grouping over-counts the cheap bucket.** The first cut of this analysis did exactly that — "the source resolves elsewhere, so this is a format problem" — and reported **262** cheap gaps, wrong by more than 4×. The counter-example: `TS. PRĀT.` shares its first token with `TS.` (Taittirīya Saṃhitā, 391 resolving citations) but the Taittirīya *Prātiśākhya* is a different work with no scan. Any heuristic keyed on the leading abbreviation silently absorbs every sub-work sharing that prefix. The fix is to stop classifying and **repair-and-retest**: apply one named, reversible normalization and ask the real resolver again, so "cheap" becomes an experiment with a falsifiable outcome instead of an opinion. The four repairs that survive that test — `expand_pratis` (36: PWG abbreviates the Ṛgveda-Prātiśākhya two ways, only one of which routes), `drop_alt_numbering` (15: `41 (40),5` — the parenthetical is the other edition's chapter, apparatus not coordinate), `uppercase_prefix` (7: the resolver's prefix map is case-sensitive, so the store's `MBh.`/`Śāk.` miss), `drop_edition_tail` (2) — are each verified end-to-end down to an HTTP 200 on the resulting scan page.

Implication: do not open a citation-coverage workstream; the constraint is the world's supply of digitised Sanskrit editions. If coverage ever becomes a priority the lever is upstream — which editions get scanned next, ranked in [`ls_gap_unrepairable_by_source.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/ls_gap_unrepairable_by_source.tsv) (Suśruta alone would light up 280 citations). The four repairs are deliberately **not** wired into `ls_links.py`: each rewrites a citation before resolving it, and a wrong rewrite invents a reference to the wrong book — worse than leaving it dark. Promoting one into the resolver is a human's call, one rule at a time.

> Opus 5 (`claude-opus-5`) · 15-08-2026 · [H2835 (Opus 5) — Mine the mintable `<ls>` citation gaps: classify the 17 % unresolved into format-gap vs no-target, rank by yield](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2835-Opus_SanskritLexicography_ls-citation-gap-mine_15.08.26.md) · class A (reproduce: `python src/ls_gap_repair.py`).

### §541. The re-glue typology label is assigned independently of whether an insertion target was found, so 90 % of it asserts a relation to a sense that is not there

🔴 **5,054 of 5,603 supplements (90.2 %) carry `target_sense='*new'` — the pipeline's own marker for "no PWG sense to attach to" — and are still labelled `restate`, i.e. "PW abridging restatement of PWG".** The subtype comes from a layer default (`layer=pw` ∧ no gender conflict ⇒ `restate`, [ADDENDA_TYPOLOGY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ADDENDA_TYPOLOGY.md) §5) that never consults the insertion result, so the label and the insertion point contradict each other: one claims a relationship to a PWG sense, the other says there is no such sense. Measured 16-08-2026 over `RussianTranslation/src/pwg_ru_relationships.jsonl` (local-only, gitignored); full write-up in [REGLUE_SPEC §9](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md).

This is the label-side half of what [REGLUE_SPEC §5a](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md) already measured from the placement side. §5a concluded "supplements fall to `*new`, **nothing lost**" — true of the *text*, but the **label did not fall back with the placement**, and nothing flagged the mismatch because the two are computed independently.

Consequences, all measured:

| bucket | supplements | share |
|---|---:|---:|
| no PWG target (`*new`) | 4,690 | 83.7 % |
| target exists, German too thin to compare | 303 | 5.4 % |
| **genuinely checkable** | **246** | **4.4 %** |

`nws/foreign_fragment` (62) and `pw/pw_correct` (1) have **zero** checkable pairs — including the single `pw_correct`, the only cancellation in the whole corpus, which therefore cannot be verified against any PWG sense.

**Two method lessons worth more than the counts.** (1) *An evidence axis has to be measured before it is shipped.* Gloss-word overlap (Jaccard over German content words) was the obvious way to make ≈-vs-＋ checkable; it does not discriminate — median 0.000 for **both** classes — because a PWG sense body has a median of **3 content words** and 16 % have none, so two short German synonym lists share no surface forms even when one restates the other. It is kept reproducible in [`reglue_overlap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_overlap.py) and deliberately **not** rendered on a card: a number that looks like evidence and isn't is worse than no number. (2) *`{#…#}` and `{%…%}` are opposites and a stripper must not treat them alike* — `{#…#}` is Sanskrit, `{%…%}` is the German meaning gloss. The first cut of the measurement stripped both, deleting exactly the text under comparison and producing a spurious 0.000 across 95 % of pairs that read like a finding; it was caught only by reading actual pairs instead of trusting the aggregate.

Implication: do not put the typology chip to a human vote as it stands — 90 % of the claims are unaskable, not merely unevidenced. Either make the label consult the insertion result (so a `*new` supplement stops claiming to restate anything), or drop the layer-default label for un-placed supplements. The vote that *is* answerable is the 246-pair checkable slice, which [`build_reglue_evidence_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_evidence_sheet.py) now samples with the German original of both sides on the card.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · [H2859 (Opus 5) — Give the re-glue vote real evidence: measure PWG-vs-supplement gloss/citation overlap, rank cards by chip-vs-measurement disagreement](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2859-Opus_SanskritLexicography_reglue-vote-evidence-overlap_15.08.26.md) · class A (reproduce: `python src/build_reglue_evidence_sheet.py`).
>
> **Tracking issue: [#1736](https://github.com/gasyoun/SanskritLexicography/issues/1736)** (in Russian) — names the two lines that cause it ([`edition_rel.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/edition_rel.py) L146 sets `target_sense='*new'`, L187 sets `subtype='restate'` without reading it), splits the mass into its two failure modes (**4,618 literal `*new`** · **436 dangling numeric targets** · 549 that resolve), and puts four fix options to a human. The recommended one, **C**, separates the two claims the `subtype` field currently conflates: *"PW abridges PWG"* is a property of the layer and is always true (already carried by `direction`), while *"this supplement restates **that** sense"* is a claim about a pair and needs a found target. C fixes both failure modes and is **orthogonal to** the deferred content-alignment gold pass — a perfect alignment would still leave a label that never consults it.

**RESOLVED (wave 1), 16-08-2026 — option C shipped, and the honest gain is 3 % of what the headline suggests.** `placement` / `placement_reason` / `placement_hypothesis` now carry the pair-claim; `subtype` keeps only the kind-claim and must be read together with `placement` ([REGLUE_SPEC §10](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md)). Over 6,009 sidecar rows: `found` 595 · `no_target_marker` 4,901 · `out_of_range` 383 · `not_found` 130.

Three things are worth more than the fix itself:

1. **The 90 % was never one phenomenon.** Splitting it, only **130 rows (2.2 %)** are genuinely unexplained. **383** are `out_of_range` — the target number is *above* PWG's highest sense in that article, i.e. the later edition really does have more senses. That is direct evidence for the renumbering thesis, and it had been sitting inside a bucket labelled "broken". A count that merges a real phenomenon with a defect hides the phenomenon, not the defect.
2. **Measure the fix against the same inputs, or the number is fiction.** The published baseline (246 checkable of 5,603) came from a sidecar built 06-07-2026 against a store from 02-08-2026. Re-running both rules over one identical store and sidecar attributes **+7 checkable pairs (250 → 257)** to this change; the rest of the apparent jump was a stale artifact being refreshed. Had the before/after been quoted as published, wave 1 would have claimed roughly four times the effect it had.
3. **The conservative normaliser closes almost nothing — and that was the right call anyway.** Stripping trailing punctuation newly placed **12 rows**, all in one article (`vA`, skeleton written `3)`–`7)`). The alternative, a looser matcher, buys coverage by risking a silent `placement=true` on the wrong sense — a lie that no reviewer would catch, unlike an honest `placement=false`. Pinned by negative selftests (`1-sub-…`, `1 (PW)`, `Nachtrag`, `caus-1` must never merge). The `placement_hypothesis` field, built to record near-misses, fires on **0** real rows.

Acceptance is re-runnable: [`placement_axis_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/placement_axis_check.py) re-proves every criterion — including the two stop conditions, that no target-less row became placed and that the canonical store stayed byte-identical (`rows=11,603`, sha256 `811bbc21…`).

> Opus 5 (`claude-opus-5`) · 16-08-2026 · [H2879 (Opus 5) — Волна 1: развести ось привязки и метку типологии + нормализация тегов смыслов](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2879-Opus_SanskritLexicography_placement-axis-split-w1_16.08.26.md) · class A (reproduce: `python src/placement_axis_check.py`). Issue #1736 stays open — waves 2–4 (edits inside PWG, SCH, MW/AP) are untouched.

### §538. A Latin siglum inside a `{#…#}` span is silently transliterated — `pw` became `pṭ`, an abbreviation that does not exist

🔴 **Any Latin-script token that ends up inside a Sanskrit span is read as SLP1 and
transliterated, with no error and no visible seam.** The store holds `{#gā (=pw gā 1)#}`, where
`pw` is the siglum of the *Petersburger Wörterbuch* in Böhtlingk's shorter recension. SLP1 maps
`w` → `ṭ`, so the published vote card offered the reader **`pṭ`** — a plausible-looking
abbreviation of nothing. It was caught by a human reading a card and asking what `pṭ` stood
for, not by any gate.

Reproduced against the canonical renderer before the fix:

```
print_panel('{#gA (=pw gA 1)#} idti')
  -> '<div class="printview"><i class=sa>gā (=pṭ gā 1)</i> idti</div>'
```

**The trap in the fix is worse than the bug.** The obvious remedy — an allow-list of sigla
exempted from transliteration — is unsafe, because several sigla are also real SLP1 words.
`ap` is the stem *ap-* "water", attested in this very store at `apta` («от 2. {#ap#}»); `br`
prefixes `brū`; `gra` occurs inside `ugra`. A naive allow-list would corrupt genuine Sanskrit
in order to fix a rendering slip. **Anchor on the syntax, not the token:** the guard fires only
on `(=<siglum>`, the cross-reference form, which is what all 14 real sites use.

**Measured, and smaller than it first looked.** A first ASCII-boundary scan of the
11,603-entry store reported 21 sites; reading every one showed **6 were false positives of the
scan itself** — the boundary assertions `(?<![A-Za-z])` / `(?![A-Za-z])` pass freely against
non-ASCII IAST and German, so `brū`, `śap`, `hyu^gra` and German `schützen` inside spans all
matched — and one (`ap` at `apta`) was correct Sanskrit. The real defect is **14 occurrences,
every one of the form `(=pw <headword> <n>)`**. The general lesson: an ASCII word-boundary
regex is not a word boundary in a mixed IAST/Cyrillic/German corpus, and a census built on one
must be read row by row before its number is quoted.

Implication: fixed in the canonical converter
([`slp1_iast`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py)),
not in the sheet builder, so the public article site gets the same repair. Implemented by
transliterating **piecewise** around the match rather than substituting a placeholder — a
placeholder must be a character the char map ignores, and every such choice is an invisible
literal in source. Pinned by fixtures in `g5_card_render --selftest`, including negative
controls that genuine Sanskrit is *not* shielded and that a bare `pw` with no `(=` anchor is
still SLP1. The store is **not** edited: `pw` is correct there; only the render was wrong.

> Opus 5 (`claude-opus-5`) · 15-08-2026 · [H2848 (Sonnet 5) — Latin sigla trapped in `{#…#}` render as Sanskrit (`pw` → `pṭ`) + NWS entry deep links](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2848-Sonnet_SanskritLexicography_sigla-in-sanskrit-span-translit-bug-and-nws-deeplinks_15.08.26.md), under [H2843 (Opus 5) — MG crosswalk review umbrella](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2843-Opus_Uprava_mg-crosswalk-review-8-point-vote-contour-umbrella_15.08.26.md) · class A (reproduce: `python src/g5_card_render.py --selftest`).


### §539. Kochergina corrections have no tracked home — the org's correction store is CDSL-scoped, and Kochergina is not a CDSL dictionary

Measured 15-08-2026 (Opus 5 `claude-opus-5`), closing prerequisite 2 of
[H798](https://github.com/gasyoun/Uprava/blob/main/handoffs/H798-Sonnet_SanskritLexicography_h779-apply-okas-guda-sphic-decisions_12.07.26.md),
which has sat 🟡 QUEUED since 12-07-2026 with four approved corrections
(`okas` · `okya` · `guda` · `sphic`) and nowhere to write them.

**Kochergina is present in the org three times, and none of them is a correction ledger.**

| Where | What it is | Correctable? |
|---|---|---|
| [`CORRECTIONS/Kochergina-1987_29007.txt`](https://github.com/sanskrit-lexicon/CORRECTIONS/blob/main/Kochergina-1987_29007.txt) | a 29 006-line letter-spaced **headword list** | no — a word list, no entry bodies, no sense structure |
| `SanskritGrammar/KocherginaUchebnik_1998/` | the 1998 **textbook** (methodichka, exercise coverage, gradation metalanguage) | no — pedagogy, not the 1987 dictionary |
| the BLI B1 gold set | **500 of 500 cards** carry a `Kochergina` gloss label | it is the *consumer*, not the source |

**Why the obvious home does not fit.** [CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS)
is purpose-built for exactly this — "where every correction ever accepted across the whole
project is recorded, per dictionary, as a durable audit trail". But its `dictionaries/`
tree and its `cfr.tsv` correction-form report are keyed by **CDSL dictionary codes**
(`ACC AE AP AP90 BEN BHS BOP BOR BUR CAE CCS GRA GST IEG INM KRM MCI MD MW MW72 MWE PD PE
PGN PUI PW PWG SCH SHS SKD` …). Kochergina 1987 is a third-party Russian dictionary Cologne
does not publish, so it has **no code, no `dictionaries/` slot, and zero rows in
`cfr.tsv`** — only that stray headword list. The correction store is scoped to what CDSL
owns; this dictionary sits outside it by construction, not by oversight.

**The integration need H798 said would justify creating a store now exists.** H798's
prerequisite 2 offered "create a lightweight store now vs. defer until a real integration
need appears". The BLI B1 gold set is that need: Kochergina is the gloss authority on
**every one of its 500 cards**, that set is live in the Do Today queue awaiting human
annotation, and it feeds P@1/P@5/MRR scoring. Two of the four pending corrections are
sense-level (`okas` — drop the unattested «родина»; `guda` — sense order), so an uncorrected
Kochergina propagates straight into gold and then into the retrieval metric.

**How to apply:** the four votes are blocked on a human ruling about *where*, not on
lexicography — treat "no store" as the finding, never as licence to edit blind (H798's own
instruction). Two caveats survive into whatever store is chosen: H779's canonical
re-verification **REFUTED** the `guda` gender defect (Kochergina already carries a separate
`gudā` f. entry, so "m.pl.→f.pl." is likely a no-op — verify before applying), and MG's
17-07 notes require cross-checks against Elizarenkova's Ригведа for `okas` and Druzhinin's
Aṣṭāṅgahṛdaya for `guda` before the sense wording is final. Kin: the CDSL-scoped store is
also why `learnsanskrit.ru` errata have never had a home.

> Opus 5 (`claude-opus-5`) · 15-08-2026 · H798 prerequisite 2 (store located: none exists).
> Evidence: `CORRECTIONS/dictionaries/` listing + `cut -f2 cfr.tsv | sort -u` (no Kochergina
> code); `grep -c Kochergina` over the BLI B1 500-card sheet = 500/500. §540 takes the next number.

### §540. Mixed-script words hide from every search that assumes one alphabet per word — and the repair map has to be transliteration, not visual shape

One reviewer comment on a Sundarakāṇḍa ballot card («`saketakodDālakа` — что за
мусор с транслитерацией?») turned out to name a corpus-wide class. That single
word carries **two** independent defects: `odDālaka` is leaked HK/SLP1
camelCase, and its final «а» is Cyrillic sitting inside a Latin word. Neither is
visible to the eye, and neither is findable by grep, because a search for
`saketakoddālaka` assumes one alphabet per word and a search for the Cyrillic
form assumes the other. Scanning every note-bearing JSON in CommentaryStrategies
found **643 such places**, of which 553 were mechanically repairable.

Three things generalise to any bilingual corpus in this org:

1. **The repair map is transliteration, not visual shape.** Cyrillic «р» looks
   exactly like Latin `p`, but in every real instance of this corpus it stands
   for `r`: `dhарmic` is `dharmic`, `niрvā` is `nirvā`, `Раghuvamsha` is
   `Raghuvamsha`. The first version of the fixer used the homoglyph (visual) map
   and proposed writing `dhapmic` into 201 places — caught only because the run
   printed its proposals before applying them. **Always preview a bulk
   normalisation as a word→word list.**
2. **Ambiguous letters are settled by the corpus, not by preference.** «с» reads
   as both `s` and `c`: `Кālidāса` is `Kālidāsa`, but `saṃcukoсa` is
   `saṃcukoca`. Forking the word into every candidate and keeping the one the
   corpus already spells cleanly resolves most; the rest go to a report. Ninety
   did, mostly Russian transcription carrying IAST retroflexes (`пāṭхāнтара`,
   `брахмаṇḍа`) — a guess there silently invents a reading.
3. **Decide on the parsed tree, apply to the raw text.** The parse supplies the
   field name, without which camelCase cannot be judged at all: it is a defect in
   `note_ru` and correct in `stem`, where 1 687 legitimate SLP1 keys live — scoping
   by field turned 2 368 false positives into 18 real ones. But writing the repair
   through `json.dump` reformatted files whose content never changed (32 000 diff
   lines in one untouched index), and a diff nobody can read is a diff nobody
   checks.

Detector + fixer, reusable and CI-ready as `--check`:
[CommentaryStrategies/scripts/translit_hygiene.py](https://github.com/gasyoun/CommentaryStrategies/blob/main/scripts/translit_hygiene.py).
Residue list:
[data/analysis/translit_hygiene_report.md](https://github.com/gasyoun/CommentaryStrategies/blob/main/data/analysis/translit_hygiene_report.md).

> Opus 5 (`claude-opus-5`) · 15-08-2026 · H2831, from votes/sarga.md п.14.
> Evidence: 643 found / 553 repaired / 90 reported, over 235 source JSONs;
> [PR #170](https://github.com/gasyoun/CommentaryStrategies/pull/170). §541 takes
> the next number.

### §542. A review sheet's stated apply target is not the carrier set — the hand-authored strings can live in a generator, and an apply that trusts the sheet reverts on the next build

The agni gloss sheet says where accepted votes go, in two places: the card
footer («/decisions-apply вносит принятые правки в
`article-comparison/agni.pd-min.ru.md`, колонка «Русский»») and the `schema`
string of the manifest that generates it. Both name **one** file. Applying the
nine approved edits there would have passed every check — the diff is right, the
file is the canonical one, the sheet agrees — and been silently undone the next
time anyone ran the builder.

The Russian glosses are not authored in the markdown. They live in a hardcoded
`GLOSS` dict in
[`RussianTranslation/src/_build_agni_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_build_agni_ru.py),
which writes the table; `agni.persense-ru.md` holds a third copy of the same
strings beside its corpus column. Four carriers, one of them the actual source:

| Carrier | What it is |
|:--|:--|
| `article-comparison/agni.pd-min.ru.md` | the file the sheet names — **generated output** |
| `article-comparison/agni.persense-ru.md` | second generated view, same strings |
| `RussianTranslation/src/_build_agni_ru.py` | the `GLOSS` dict — **the actual source** |
| `article-comparison/gloss_review_items.json` | the manifest; without a stamped verdict a closed row returns on the next sheet round |

Two things generalise:

1. **Before applying a vote, ask what writes the target.** `git grep` one of the
   current cell strings, not the filename. A single hit means the file is
   authored; more than one means you are looking at output. Here the string
   «ахаванья» appeared in five files.
2. **The routing note is a convenience, not an inventory,** and it ages worse
   than the code — this one was written 18-07-2026 against a repo whose builders
   changed afterwards. The three sibling sheets (`aksara`, `ananta`, `anya`) are
   still unvoted and have the same shape with a *different* layout again: one
   shared `RU` dict in `_build_skeletons_ru.py` covering all three, not a
   per-word builder. Whoever applies them must re-derive the carrier set rather
   than reuse agni's.

> Opus 5 (`claude-opus-5`) · 15-08-2026 · H2861, applying the agni gloss vote.
> Evidence: 9 approved edits × 4 carriers;
> [PR #1732](https://github.com/gasyoun/SanskritLexicography/pull/1732), audit
> record
> [agni_decisions_applied_15-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/agni_decisions_applied_15-08-2026.md).
> §543 takes the next number.

### §543. A sense order can be right for the Vedic layer and useless for the classical one — `guda` is «кишки» in the RV and only ever the anorectal outlet in Āyurveda

🟠 **Ordering a Russian equivalent by etymology or by Vedic attestation can leave the
reader with the wrong sense in 100 % of the occurrences they will actually meet.**

The H798 vote ruled Kochergina's `guda` should read кишки → толстая кишка → анус, on PWG
plus the Vasmer/KEWA etymology, and against the RV: Elizarenkova renders `gudā́bhyaḥ` at
RV 10.163.3 «из твоих **кишок**». That is correct for the Vedic layer. In DCS's
lemma-annotated **Aṣṭāṅgahṛdayasaṃhitā** — 79 occurrences across 30 of its 120 files —
the intestinal sense occurs **zero** times. The text defines `guda` against the intestine
rather than as one (`gudaḥ sthūlāntrasaṃśrayaḥ`, `sthūlāntrabaddhaḥ … gudaḥ`), groups it
with penis and vagina as a lower orifice (`meḍhrayonigudair adhaḥ`), has it prolapse and be
pushed back (`gudaṃ bhraṣṭaṃ … praveśayet`), and uses it as the enema route
(`gude praṇihitaḥ snehaḥ`). «Кишки» there is `antra` / `sthūlāntra` / `pakvāśaya` /
`koṣṭha`, all of which occur contrastively beside it.

Generalises to any lemma whose corpus spans Vedic and śāstric registers: **check the
register the consumer works in before ordering senses**, and if the two disagree, ship a
register rider rather than picking a winner. The fix here was a rider on the correction
row, not a re-vote.

Two traps met on the way, worth carrying:

1. **`guḍa` (गुड, jaggery) and `guda` (गुद, rectum) collapse in Cyrillic.** Every one of
   the 8 «гуда» hits in a Russian Āyurveda transcript corpus was `guḍa`/`guḍūcī` or
   Russian «гудеть» — none was the anatomical word. A Cyrillic-transcript search for a
   Sanskrit term is a **retro-transliteration** problem, and the retroflex/dental contrast
   is exactly what it loses. Search the concept's Russian medical vocabulary instead.
2. **A lemma count taken from a filename glob is not an occurrence count.** The handoff
   carried «42 files carry `guda`»; the annotation itself says 30 files / 79 occurrences.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H2863, closing the Kochergina cross-checks.
> Evidence: [KOCHERGINA_CORRECTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOCHERGINA_CORRECTIONS.md)
> § Cross-check closures; DCS `dcs-conllu/files/Aṣṭāṅgahṛdayasaṃhitā/` (120 files).
> §544 takes the next number.

### §544. rvlinks is the pāda-granular RV substrate already on disk — and a verse-granular read of it invents renderings the translator never made

🟠 **[rvlinks](https://github.com/sanskrit-lexicon/rvlinks) carries Elizarenkova, Geldner
and Griffith side by side for all 1 028 RV hymns, verse by verse, locally.** Two sessions
before this one concluded the org did not hold Elizarenkova's Russian, then found the
[SamudraManthanam](https://github.com/gasyoun/SamudraManthanam/blob/main/Index/Updater/Data/01_rigveda.no_tags)
`no_tags` extract — which is real, but is **Mandalas I–II only**, so 6 of the 8 `okya`
loci and RV 10.163.3 are simply absent from it. `rvlinks/rvhymns/rv<MM>.<HHH>.html`
covers everything and is the right substrate for any RV-citation work, including
[H2850](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2850-Opus_SanskritLexicography_rv-citation-pada-alignment-elizarenkova-rvlinks_15.08.26.md).
Caveat measured here: a few verses carry `-ru-` instead of Russian (RV 9.86.45 is one), so
coverage is near-total, not total.

The alignment half is the sharper point. The 2013 attestation memo
[NAGARI_LIST_2013_ATTESTATION_VS_GLOSS_OKAS_GUDA.md](https://github.com/gasyoun/Uprava/blob/main/history/NAGARI_LIST_2013_ATTESTATION_VS_GLOSS_OKAS_GUDA.md)
records Elizarenkova as rendering `guda` «прямая кишка» at RV 10.163.3. She does not.
«Прямая кишка» is her rendering of `vaniṣṭhóḥ`; `gudā́bhyaḥ` is «кишок». Geldner splits
them the same way (`Därmen` / `Mastdarm`); Griffith conflates. The error is what a
**verse-granular** read produces: four Russian words for four Sanskrit organs in one pāda,
and picking the wrong one is invisible unless the join is pāda-level. That is the exact
defect class H2850 exists to eliminate, and RV 10.163.3 is now a worked specimen for it.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H2863. Evidence:
> [rvlinks/rvhymns/rv10.163.html](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv10.163.html#rv10.163.03)
> vs the memo's claim; 1 028 hymn files counted on disk.
> §545 takes the next number.


### §545. A fixture guard row proves the sanitizer runs, not that it covers every sink — the leak hid in a second consumer the guard row never reaches

🔴 **[`export_de_edition.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py)
had a documented, tested, *working* Cyrillic sanitizer, and still emitted Russian into a
public artifact.** The first full-store run of the H1635 release export aborted on
`assert_rights_safe` — correctly, and on the 110th row of a store the fixture suite had
declared clean for three weeks.

The module classifies `sense_tag` as **sanitizable** (as opposed to blocking): ~1% of store
rows carry Russian free text there, so `sense_tag_slug()` reduces it to an ASCII skeleton and
the German survives. That is right, and it was verified — the fixture carries a dedicated
Cyrillic-`sense_tag` guard row and the selftest asserts `sanitized_tag_rows == 1`.

But the slug is not the only consumer of the raw tag.
[`edition_rel.classify_edition_rel`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/edition_rel.py)
builds an `evidence` string by interpolating the tag with `%r`
(`"PW abridging restatement; sense_tag=%r"`), and the exporter emits that string **verbatim**
in both serializations — `rdfs:comment` in Turtle, `@relEvidence` in TEI. One field, two
sinks; the sanitizer guarded the IRI/`xml:id` sink and nothing guarded the prose sink.

**Why no fixture run could have caught it.** The guard row exists, but its `(layer, sense_tag,
de)` combination does not take an evidence-bearing branch of the classifier — so the guard row
and the vulnerable code path never met. The fixture proved the sanitizer *ran*; it could not
prove the sanitizer *sufficed*, and a green selftest was read as if it had. Only full-store
scale produced a row that was contaminated **and** classified into an evidence-bearing branch.

Transferable rule: when a field is declared *sanitizable rather than blocking*, enumerate its
sinks and pin each one, and write the regression test to **reproduce the leak directly** rather
than trusting a fixture row to wander onto the branch. The fix here scrubs at the single choke
point both the precomputed and freshly-classified relation pass through, and the new selftest
constructs the leaking row explicitly.

Second-order: the byte-level `assert_rights_safe` post-check is what turned a silent rights
breach into a loud build failure. A field allowlist alone would have shipped this — the
allowlist *permits* `sense_tag`; the breach was what a downstream module did with it. Keep
both layers.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H1635. Evidence: full-store export abort at byte
> 1 649 758 of `pwg_de_edition.ttl`; `sanitized_tag_rows: 110` in the shipped
> [manifest](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_de_sidecars/manifest.json);
> fix + selftest section 4b in [PR #1738](https://github.com/gasyoun/SanskritLexicography/pull/1738).
> §546 takes the next number.

### §546. DCS ships a 180 k-row lemma→gloss layer next to the corpus — `dcs-conllu/lookup/dictionary.csv`, and almost nothing in the org reads it

🟠 **The DCS mirror is not only annotated text. [`dcs-conllu/lookup/`](https://github.com/gasyoun/dcs-conllu/tree/main/lookup) carries `dictionary.csv` — 180 178 rows of `id ⇥ word ⇥ grammar ⇥ preverbs ⇥ meanings` — plus `word-senses.csv` (WordNet 2.1 links + supersenses), `sembank-*`, and `chapter-info.xml`.** It is tab-separated despite the `.csv` extension, so a naive comma parser reads every row as one field and finds nothing; that alone is enough to make it look empty.

Why it matters where a translation is missing: it is a **lemma-level gloss authority already on disk**, needing no acquisition. When the Russian AHS lane died ([DEAD_ENDS §14](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)) it independently reproduced the distinctions that had cost a full corpus read to establish:

| lemma | DCS grammar | DCS meanings |
|:--|:--|:--|
| `guda` | mn | an intestine; entrail; rectum; anus; [medic.] name of a kṣudraroga |
| `gudā` | f | the bowels |
| `vaniṣṭhu` | m | a part of the entrails …; entrails; **the rectum**; Dickdarm |
| `pāyu` | mn | **the anus** |
| `sthūlāntra` | n | the larger intestine near the anus |
| `antra` | n | entrail; intestine |

Three things fall out at once. **(1)** `vaniṣṭhu` = "the rectum" confirms mechanically what [§544](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) had to establish by hand from the pādas — «прямая кишка» at RV 10.163.3 is Elizarenkova's `vaniṣṭhu`, not her `guda`. **(2)** `gudā` f. "the bowels" is exactly her «кишок», and is the separate feminine entry that made H779 rule the Kochergina gender claim *refuted*. **(3)** `guda`'s own gloss order — intestine before rectum/anus — matches the corrected Kochergina order, while AHS *usage* is anorectal throughout; the lexicon and the register disagree in precisely the way [§543](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) describes, and the disagreement is visible in two committed files.

Generalises: **before proposing to acquire or OCR a translation to settle a sense question, read `lookup/dictionary.csv` first.** It will not give per-locus rendering — that still needs a translation — but it settles which lemma owns which gloss, which is what the misalignment class in §544 gets wrong.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H2863 follow-up, after MG ruled the Russian AHS
> lane closed. Evidence: `lookup/dictionary.csv` 180 178 rows, pinned upstream commit
> `04e0778d3dc971030229179e25eea043d06ff397` (2026-03-05) per
> [dcs-conllu PROVENANCE.md](https://github.com/gasyoun/dcs-conllu/blob/main/PROVENANCE.md);
> rows quoted verbatim above.
> §547 takes the next number.

### §547. PWG's Ṛgveda citations disagree with Elizarenkova far more often than they agree — and a third of the surface cannot be adjudicated at all

🔴 **Over the 2 964 Ṛgveda-Saṃhitā verse citations in the live `pwg_ru` store (52 entries,
2 482 distinct loci), aligning each quotation to Elizarenkova's published Russian at pāda
granularity gives 1 221 `diverges` · 520 `agrees` · 1 223 `undecidable`.** Divergence is the
majority verdict among the decidable ones, roughly 2.3 : 1 against agreement. The specimen MG
raised is one of them: PWG glosses `parigā` «прийти, достигнуть, настигнуть кого-либо» and cites
`ṚV. 7,84,1`, whose pādas c+d Elizarenkova renders «Полная жира (жертвенная ложка,) которую
держат в руках, / (Принимая) разные формы, **кружит около** вас» — `jigāti` read as circum-motion,
not arrival.

**Evidence.** [`rv_pada_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_pada_align.py)
`report`, 16-08-2026, over `pwg_ru_translated.jsonl` (11 603 rows): 1 856 joins land on specific
pādas (62.6 %), 333 of those span more than one pāda (17.9 %) — so a verse-granular join would
have been wrong about which lines to show on nearly one citation in five, before any question of
sense. 171 citations have no published Russian at all (124 verses rvlinks leaves untranslated,
plus khila/miscounted-hymn references). The 50-citation audit sample
([`reports/rv_pada_alignment_sample50_2026-08-16.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/rv_pada_alignment_sample50_2026-08-16.txt))
scores pāda selection at 47 correct · 2 wrong · 1 correctly declined.

**Implication.** Three things, in order.

1. The `diverges` count is **not** a defect list. `agrees`/`diverges` is a lexical-support
   SCREEN, not a semantic judgment: PWG glosses the lemma across its whole range while
   Elizarenkova renders one occurrence in context, so the two disagreeing is the normal case and
   the interesting one. It ranks the corpus for a human, nothing more.
2. `undecidable` at 1 223 is the real finding about coverage — 775 of those citations quote no
   Sanskrit at all, so nothing narrows them below the whole verse. A citation without a
   `{#…#}` span cannot be aligned at pāda granularity by any method; that is a property of PWG,
   not of the join.
3. **Elizarenkova's printed line order is not always the pāda order.** At RV 7.33.10 her first
   line renders pāda b and her second renders pāda a; at RV 3.33.9 and RV 10.108.5 a speaker
   attribution («Сарама:», «Р е к и:» — 163 such lines across the 1 028 hymns) occupies a line of
   its own and shifts every later line off its pāda. Filtering the attributions is mechanical and
   is done; the inversions are not detectable from the Russian alone and remain the residual
   error class, 1 of 50 in the audit.

**Extent correction.** The handoff states «1 526 RV citations across 62 entries». Re-measured on
the same store: **2 964** Saṃhitā verse citations across **52** entries, out of 3 760 ṚV-siglum
`<ls>` occurrences once hymn-level references and the sub-works (Prātiśākhya, Anukramaṇī,
Vālakhilya) are excluded. Neither of the handoff's two numbers reproduces under any counting rule
tried; the measured pair is the one to cite.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H2850. Evidence:
> [`RV_PADA_ALIGNMENT_AUDIT_2026-08-16.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/RV_PADA_ALIGNMENT_AUDIT_2026-08-16.md)
> and the 2 964-row [`rv_pada_alignment.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/rv_pada_alignment.jsonl);
> selftest 49/49 including the gate negative control.

### §548. PWG has TWO incompatible families of `<ls>` counts — cleaned-string and work-family — and the volunteer tracker's column is the second

🔴 **Counting PWG's citation apparatus gives two legitimate, wildly different numbers for the
same work, and nothing in the repository labels which is which.** `MED.` has **30**
occurrences in one family and **12,990** in the other. Both are correct.

| Family | Generator | Keys on | Dictionary total |
|---|---|---|--:|
| **cleaned citation string** | `pwg_ls/pwg_dhaval/abbrvwork/abbrv3.py` → [`sortedcrefs.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/pwg_ls/pwg_dhaval/abbrvwork/abbrvoutput/sortedcrefs.txt) | the `<ls>` text with numbers stripped, under a restrictive "starts with a capital" proper-reference filter — so one book scatters over `MED.`, `MED. k.`, `MED. kh.`, `MED. im ŚKDR.` … | 344,229 |
| **work family** | [`lsextract_all.py`](https://github.com/sanskrit-lexicon/PWG/blob/master/pwgissues/issue94/lsextract_all.py) → `lsextract_all.txt` | the **longest bibliography abbreviation in `pwgbib_input.txt` that prefixes the element**, `n="…"` prepended first; digits → `NUMBER`, no prefix → `UNKNOWN` | 739,056 (2024-09-11) |

Only the second **partitions** the dictionary, so only its `ALL` is a denominator. The first
is a distribution over citation strings and has no work-level total at all.

**This is how the PWG scan-index tracker's `Citation count` column sat "unprovenanced" for
three weeks.** H1706 compared it against the cleaned-string family, measured a 1.2×–433×
spread, and concluded the provenance was unrecoverable without the coordinator who built the
column. The spread *was* the answer: the column is the work-family count, and 66 of its 67
valued rows match
[`pwgissues/issue74/lsextract_all.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/pwgissues/issue74/lsextract_all.txt)
digit for digit.

**Rules.**

1. **Never compare across the two families**, and never call the resulting ratio a
   disagreement. Check which generator produced a count before treating it as evidence
   about another count.
2. **A work-family count is not row-additive.** `AK. Deslongchamps ed.` and
   `AK. Colebrooke ed.` both read `AK.`'s total; fold by bibliography abbreviation first.
3. **Divide only by the `ALL` of the same snapshot.** The counts move: between 2024-09-11
   and 2026-06-24, `an.` falls 1,797 → 1 while `H. an.` rises 2,075 with a byte-identical
   bibliography entry on both sides — a **re-tagging** of the dictionary, not a recount.
   Refreshing a frozen column in place would rewrite the campaign's own history.
4. **Case is meaningful and case-folding is lossy.** `Ś.`/`ś.`, `Uṇ.`/`UṆ.`, `KAP.`/`Kap.`
   are different bibliography entries and 15 such pairs are cited on both sides; a
   case-insensitive lookup silently picks one of two real works.

**Method note worth more than the finding.** The recovery took one mechanical sweep — compare
the column against *every* count table in the repository — after reasoning about which
extraction "ought" to have been used had failed. When a number's provenance is open, diff it
against the whole candidate set before concluding it needs a human.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H2874. Evidence:
> [`reports/pwg_citation_count_provenance.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_citation_count_provenance.md)
> (five-hypothesis log) + the 82-row
> [`pwg_citation_count_provenance.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_citation_count_provenance.tsv);
> gate `python scripts/pwg_citation_count_provenance.py --check`,
> port fidelity `python scripts/pwg_ls_counts.py --verify-port`.

### §549. CommentaryStrategies' published 17,863-note composition was born self-contradictory in one batch commit — and the committed corpus's per-note page anchors are the attribution layer that settles what can be settled

The five sub-corpus totals, the 17,863 headline, the rubric percentages, AND the per-page
essays that contradict them all entered git in a single commit (`77062da`, 24-04-2026,
«Anatoliy Batch») importing an uncommitted March-2026 «automatic categorization». Reconciling
against the lowest committed source — SamudraManthanam's hash-pinned canonical JSONL (single
commit 20-06-2026) — split the claims into three classes: **exactly confirmable** (Кальянов
7,424 — to the note), **definition errors** (Васильков–Невелева «5,574» silently includes
1,685 notes of «XII(б). Мокшадхарма», a book absent from its own declared 9-book list, which
yields 3,885), and **irreproducible-by-construction** (Гринцер 2,245 contradicts its own
page's table 2,220; the rubric shares 3.4 %/7.7 % and 40.2 %/27.8 % have no committed
per-note assignments — the n=50 gold sample's CI covers both sides of each).

Three reusable lessons: (1) a derived statistic published without committing the run that
produced it can become *permanently* unadjudicable — mark such values as dated snapshots
rather than picking the cleaner number; (2) the digitized corpus's per-note HTML anchors
(`title="Махабхарата 2009 (VI): 338"`) are a committed edition-attribution layer — one
sweep over them resolved a three-way publisher conflict (Эрман кн. VI = **М.: Ладомир,
2009**; «М.: Наука, 1977» and «СПб.: Наука, 2009» retired) and unmasked a non-Syrkin
upanishad (`jabala-up`, 2025) inside the «Syrkin» file set; (3) duplicate lineages exist by
design — `bhagavadgita-erman` (301 notes) re-hosts the Bhīṣmaparva BG chapters' notes (319),
so summing works without an anchor census double-counts.

> Fable 5 (`claude-fable-5`) · 16-08-2026 · H2872. Evidence:
> [`docs/CORPUS_TRUTH_RECONCILIATION_17863.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/docs/CORPUS_TRUTH_RECONCILIATION_17863.md)
> + machine table
> [`data/analysis/corpus_truth_reconciliation.json`](https://github.com/gasyoun/CommentaryStrategies/blob/main/data/analysis/corpus_truth_reconciliation.json);
> regression gate `python scripts/corpus_truth_census.py --check` (CI-wired);
> PR [gasyoun/CommentaryStrategies#186](https://github.com/gasyoun/CommentaryStrategies/pull/186).
> §550 takes the next number.

### §550. A `Nachtrag` almost never names the sense it amends, but a `1 (PW)` almost always does — so "corrections inside PWG" is two populations, not one

🟠 **365 rows carried on the `pwg` layer of the `pwg_ru` store are not senses of
PWG at all** — they are the authors' own later supplements (`Nachtrag` 184,
`addendum` 88, `corrigendum` 7) or material the PW edition contributed at a PWG
sense (`1 (PW)` / `PW` / `PW-1`, 86). Every one of them was rendered as an
ordinary skeleton sense, so a card asserted the existence of a PWG sense called
"Nachtrag" — the [§541](#541) axis defect one layer down.

**Only 66 of 365 (18.1 %) name a target sense; 290 (79.5 %) carry no target
marker at all.** The aggregate hides the real result, which is the split:

| marker | rows | names a target | share |
|---|---:|---:|---:|
| `nachtrag` | 184 | 6 | **3.3 %** |
| `addendum` | 88 | 18 | 20.5 % |
| `corrigendum` | 7 | 1 | 14.3 % |
| `pw_provenance` | 86 | 41 | **47.7 %** |

A `Nachtrag` is printed as free-standing supplementary material and simply does
not cite the sense it amends; a `1 (PW)` tag **is** a sense number, so it places
about half the time. Treating the two as one class and quoting 18 % would
describe neither. Where the tag names nothing the row stays `placement=false`
with a reason — the wave-1 contract — never a guess.

**The trap.** `Nachtrag-1`, `addendum-2`, `PW-1`, `Nachtrag §75-1` all carry a
digit and in none of them is it a sense number: it is the ordinal of the
addendum, or a section reference. Any rule that extracts "a digit" rather than a
*leading* digit silently attaches ~200 rows to sense 1. The existing `lead_int`
already declines them, so the fix was to pin that with negative selftests, not to
write a new extractor.

Two adjacent traps worth naming: a `PW` marker must be anchored whole-string or
it fires on `PWG`/`PWKVN` and empties the skeleton of its real senses; and `op`
must not be `correct`, because `build_reglue` renders `correct`/`delete` with a
"cancels PWG" strikethrough — a Nachtrag amends its sense, it does not withdraw
it.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H2880 (wave 2 of issue
> [#1736](https://github.com/gasyoun/SanskritLexicography/issues/1736)). Full
> write-up: [REGLUE_SPEC §11](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md).
> Re-runnable: `python src/placement_axis_check.py --store-rows 11603` (W2a–W2d).
> §551 takes the next number.

### §551. The re-glue sidecar's `(subcard, sense_tag)` key is not unique — every consumer that dicts on it silently drops 468 of 6 009 rows

🔴 **133 `(subcard, sense_tag)` pairs occur more than once in
`pwg_ru_relationships.jsonl`, shadowing 468 rows (7.8 %).**
[`build_reglue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue.py)
`load()` builds `rel = {}` keyed by exactly that pair, so the last row wins and
the other 467 never reach a card. The worst case is 25 rows collapsing to one
(`_d_a~~h0_zz_pw01`, `Mit <div n="p">`); `vas~~h0_zz_pw01` loses 13 rows on each
of senses 1 and 2. The loss is concentrated in `pw` (559 of the rows living under
a duplicated key), with `nws` 26, `pwkvn` 14, `sch` 2.

This is **pre-existing and orthogonal to the placement axis** — measured on wave
1's own code re-run over the current store, and unchanged by wave 2 (identical
133 keys / 468 rows before and after). It is recorded rather than fixed because
de-duplicating changes which supplement reaches every card, i.e. it moves
published review artifacts and needs its own gate.

**Related, same class:** the committed lock for the published sheet
`h180-reglue-evidence-2026-08-15` binds `sha256:d7c003ee…`, but that generation
reproduces from **no** current code state — pristine `origin/master` and wave 2
both render `sha256:61f32513…` over the same store. Nothing is invalidated today
(no `decisions.json` exists for it, so no votes were cast), but the lock's
promise — "check out the commit that created it and re-run" — does not currently
hold, and the first voter to try would discover that.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H2880. Measured over the wave-1
> baseline sidecar rebuilt from `origin/master` (6 009 rows) and the wave-2
> sidecar (6 374 rows), same store `sha256 811bbc21…`.

**Both halves fixed — H3300, 23-08-2026.** The writer
[`build_relationships.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_relationships.py)
now stamps every sidecar row with a unique `row_key` (`"<subcard>::<sense_tag>#<ordinal>"`)
plus `dup_ordinal` (the pair's occurrence index in store order), and every
dicting consumer joins on it while staying tolerant of legacy bare-pair rows:
`build_reglue.RelSidecar`, [`reglue_delta.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_delta.py),
and the evidence sheet (whose committed lock carried `vas~~h0_zz_pw01::1`
**twice** and `vid~~h0_zz_pw01::2` twice — two cards sharing one vote slot;
`vas::1` now votes as `#0` and `#11`). Refreshed sidecar: 6 374 rows / 133
duplicate pairs / **601 rows under them** (layer split pw 559 · nws 26 · pwkvn 14 · sch 2,
§551's split exactly, grown from 468 by the wave-2/3 row additions), zero
unreachable. Gates W7a–W7c in
[`placement_axis_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/placement_axis_check.py)
assert key presence/uniqueness/well-formedness and file-order ordinals.
The lock half is closed by a deliberate unvoted re-cut bound at
`sha256:961f8b4a…`, proven reproducible by a second force-free run rendering
the same hash through the collision guard; sample movement vs the published cut
is attributed on identical inputs to exactly the duplicated-pair rows regaining
their own German body in the `pw/restate` pool (236 → 257 members).
### §552. SCH does almost only supplement PWG — 3.3 % of its rows correct it — but the signal that proves it is a printed imperative, not the gender conflict the roadmap predicted

🟠 **`classify_edition_rel` could return only `sch_star` or `derived_sense` for
the `sch` layer, both additive.** "SCH only supplements PWG" was therefore not a
measurement of the edition; it was a property of the classifier, and no data
could have contradicted it. Measured over all 210 SCH rows in the `pwg_ru`
store, the claim is **almost** true and now falsifiable: **7 rows (3.3 %) edit
PWG rather than supplement it** — 6 `sch_correct`, 1 `sch_cancel`.

**The predicted signal does not exist on this layer.** The roadmap expected wave
3 to reuse `pw_correct`'s criterion — a `<lex>` gender conflict against PWG.
**Zero of the 210 SCH rows carry a `<lex>` token at all**, so that path can never
fire here and was deliberately not wired up. The layer does contain exactly one
gender correction — `ahiphena`, "lies n. statt m." — but it is stated in prose,
not in markup, and is caught by the printed-cue rule instead.

**The criterion is a speech act, not a keyword.** SCH prints instructions to the
reader of PWG: `lies` ("S. 152, Sp. 1, Z. 2 lies {%abhíhita%}"), `Druckfehler
für`, `zu lesen`, and for withdrawal `streiche` ("— Mit {%abhyupa%} 3. streiche
<ls>Med.</ls>"). The distinction is load-bearing, because the near-misses are
common: 11 of the 210 rows carry a look-alike token that means something else —
bare `statt` describing a metrical variant (`metrisch statt {%na gan˚%}`), the
abbreviation `St.` for *Indische Studien*, and `vgl.` pointing at literature. A
keyword-built cue set would convict all 11 of withdrawing material they add.

**Two rows are deliberately left additive.** In a compressed multi-preverb
article (`— Mit {%anvā%} … — Mit {%samā%} Z. 3 lies 231,16. — Mit {%ud%} …`) the
correction clause governs one section, not the row. Classifying the row as a
correction would assert SCH withdraws material it in fact adds, so the cue is
scoped to the leading segment and the residue is flagged
(`contains_correction_clause`) rather than dropped — gate W3e reports it.

**Independent corroboration, unplanned:** the Russian already renders these seven
rows as corrections (`читай`, `вычеркни`, `опечатка вм.`), translated long before
this classification existed and by a process that never saw it.

Unlike wave 2's `amend`, `op` here is `correct`/`delete`: these rows really do
withdraw the printed reading, so build_reglue's "cancels PWG" strikethrough is
honest. Note that an *unplaced* correction shows no strikethrough — it never
identified a sense to strike, which is wave 1's contract working as intended.

Waves 1 and 2 are provably untouched, not assumed to be: the placement census
(found 661 · no_target_marker 5 191 · out_of_range 387 · not_found 135) and
`pwg_internal_correction` (365, 18.1 % placed) reproduce exactly. Canonical store
untouched (rows 11 603, `sha256 811bbc21…`). Window suite 211/211.

**Side effect, named rather than slipped in:** re-cutting the evidence sheet
re-binds the lock §551 recorded as unreproducible. The sheet legitimately drops
one card (47 → 46) — `jñā · SCH → смысл 3` is now a correction, and "does this
supplement sit at the right PWG sense?" is not a question to ask of one — and the
new lock reproduces from current code, which the committed `d7c003ee…` did not.
Re-cut under PLAN decision 8 with the vote gate checked first: no `decisions.json`
exists for the sheet, so no votes were invalidated.

> Opus 5 (`claude-opus-5`) · 16-08-2026 · H2881. Measured over the wave-2
> sidecar (6 374 rows) and the wave-3 rebuild, same store `sha256 811bbc21…`.
> Gates W3a–W3e in `src/placement_axis_check.py`.
### §553. Cappeller (CAE/CCS) marks compounds with the Böhtlingk ring ˚ — and so do 20+ CDSL dictionaries; solid headwords, ring only for the elided member

🟢 **Both Cappeller dictionaries use the ring.** In the CDSL digitizations
([csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)),
`cae.txt` (Sanskrit–English 1891) carries **9 848** ring characters (U+02DA)
over 40 069 entries and `ccs.txt` (Sanskrit-Wörterbuch 1887) **6 664** over
30 010. The device is the Petersburg one: the ring replaces the *shared /
elided compound member*, never decorates the headword. Specimen (CAE `<L>238`):
`{#agnisAt#} adv. into fire; {#˚kf#} burn` — ˚kṛ = agnisāt-kṛ; CCS `<L>161`:
`{#agnyADAna#} … {#˚De/ya#} n.` — ˚dheya = agnyādheya. **Headwords themselves
are printed solid** (agnihotrahavaṇī, no hyphen, no seam): in neither Cappeller
does `<k1>` ever contain a seam marker. The `/` inside `<k2>` (`agni/hotra`) is
the *accent* digitization, not a compound seam.

**Census over all 44 v02 digitizations** (count of U+02DA ring · U+00B0 degree ·
U+0970 devanāgarī abbreviation sign · hyphens inside `<k1>`; zero-practice dicts
omitted):

| dict | ring ˚ | degree ° | ॰ | hyph-k1 | entries |
|---|---|---|---|---|---|
| pwg | 83 398 | 11 | 0 | 0 | 123 366 |
| mw | 53 307 | 0 | 0 | 0 | 286 525 |
| stc | 24 754 | 3 | 0 | 0 | 24 574 |
| pw | 23 706 | 14 | 0 | 0 | 170 556 |
| bhs | 22 103 | 1 | 0 | 0 | 17 839 |
| mw72 | 21 099 | 14 | 0 | 0 | 55 390 |
| inm | 19 533 | 0 | 0 | 0 | 12 647 |
| sch | 15 193 | 9 254 | 0 | 0 | 29 125 |
| **cae** | **9 848** | 11 | 0 | 0 | 40 069 |
| **ccs** | **6 664** | 15 | 0 | 0 | 30 010 |
| ap | 5 150 | 3 | 7 | 0 | 90 843 |
| md | 4 827 | 0 | 0 | 0 | 20 749 |
| ap90 | 4 051 | 3 | 0 | 0 | 34 882 |
| pwkvn | 2 203 | 0 | 0 | 0 | 24 976 |
| lrv | 1 004 | 2 | 0 | 0 | 53 441 |
| ben | 506 | 0 | 0 | 0 | 17 310 |
| ae | 0 | 245 | 0 | 0 | 11 359 |
| bop | 0 | 0 | 82 | 0 | 8 961 |
| bor | 0 | 0 | 0 | 1 229 | 24 609 |
| mwe | 0 | 0 | 0 | 2 340 | 32 378 |

(Minor users ≤200: acc 135 · fri 154 · gst 161 · ieg 45 · mci 67 · vei 5 ·
krm/shs/yat 1–3. Zero practice: abch, acph, acsj, armh, **gra**, lan, nmmb, pe,
pgn, pui, skd, snp, bur/vcp/wil have only stray degrees.)

**Reading the table.** (1) The ring is the *Petersburg tradition* and it won:
Böhtlingk (pwg/pw, 107k uses) → Monier-Williams (mw/mw72, 74k) → Cappeller
(cae/ccs, 16.5k) → Apte (ap/ap90) → Macdonell (md) → the 20th-century
specialists (bhs Edgerton, stc Stchoupak, inm/vei Söhnen-Macdonell indices) —
Kochergina's кружок (the h2805 sheet's G1 `˚`) is the direct continuation.
(2) `sch` (Schmidt's Nachträge) is the one *mixed* digitization — 15 193 ˚
alongside 9 254 °, both meaning the same device. (3) The three hyphen/ring-free
practices are principled, not sloppy: **gra** (Grassmann) *analyzes* words with
plain hyphens in running text (`á-tas, á-tra, a-dyá`) and needs no
abbreviation device; **bor/mwe/ae** are English→Sanskrit, so their `<k1>`
hyphens are English (`absent-minded`), a false positive for this question;
**bop** (Bopp 1847) digitizes the device as the devanāgarī sign `॰` (82). No
dictionary marks the seam *inside the printed headword* — the lemma is always
solid; the graphical device exists only to *abbreviate the repeated member*.

**Answer to the practical question this census served (h2805 glyph vote):**
`˚` U+02DA is what 20+ CDSL digitizations already use, including both
Cappellers; `°` U+00B0 appears as a digitization variant (sch, ae), `॰` U+0970
only in Bopp.

> Fable 5 (`claude-fable-5`) · 16-08-2026 · census script over
> `csl-orig/v02/*/<dict>.txt` (counts of U+02DA / U+00B0 / U+0970 / `-` inside
> `<k1>`); specimens quoted from cae.txt L237–246, ccs.txt L155–161, gra.txt L2.
### §554. PW and PWG use the same ring as Cappeller — but PWG *states* the seam (`agni + hotra`, 34 752×) and truncates word-ENDS, while PW and Cappeller flipped the ring to the front

🟢 **Same sign, three different grammars of use.** Follow-up to §553, measured
over the same [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
digitizations (`{#˚` = ring replaces the elided FIRST member, `˚#}` = ring
truncates the word's END; counts do not sum to total because rings also sit
mid-span and inside `{%…%}`):

| dict | entries | ring total | `{#˚` lead | `˚#}` trail | `X + Y` analysis |
|---|---|---|---|---|---|
| pwg | 123 366 | 83 398 | 19 491 | **51 170** | **34 752** |
| pw | 170 556 | 23 706 | **18 135** | 3 893 | 55 |
| cae | 40 069 | 9 848 | **3 003** | 22 | 3 |
| ccs | 30 010 | 6 664 | **3 652** | 68 | 0 |

**Three findings.** (1) **The explicit decomposition is a PWG-only device.**
Nearly every PWG compound article opens with a parenthesized analysis —
`{#agnihotra/#} ({#agni#} + {#hotra#})`, 34 752 occurrences — so the seam is
*stated*, not inferred. PW (Böhtlingk's own shorter redaction) dropped it
almost entirely (55), and Cappeller never adopted it (CAE 3, CCS 0): there the
reader reconstructs the seam alone. (2) **The ring points opposite ways.** In
PWG the dominant use is *trailing* truncation (51 170 `˚#}` vs 19 491 lead) —
cutting the tail of a quoted or corrected word (`lies {#agnihotrogni˚#}`,
`metrisch statt {%na gan˚%}`). PW flipped the profile: 18 135 leading vs 3 893
trailing — the ring now mostly *replaces the shared first member* of compound
runs. Cappeller took the PW convention to its endpoint: leading-only in
practice (CAE 3 003 vs 22, CCS 3 652 vs 68) — the §553 `{#agnisAt#} … {#˚kf#}`
pattern. (3) **Density.** PWG uses a ring every ~1.5 entries, CAE/CCS every
~4–4.5, PW every ~7 — the big Petersburg quotes and corrects far more running
text; the concise dictionaries only abbreviate sub-lemma runs. Constant across
all four (and §553's 20+ ring dictionaries): the printed headword stays solid —
`<k1>` never carries a ring or hyphen.

**Practical residue:** a parser that treats the ring as "compound-member
elision" is right almost always for CAE/CCS/PW and only ~a quarter of the time
for PWG, where the majority sense is "word truncated at the end" inside
citations and corrections. The two senses need separate handling in any
reglue/expansion pass.

> Fable 5 (`claude-fable-5`) · 16-08-2026 · counts: literal `#} + {#`, `{#˚`,
> `˚#}`, U+02DA totals over `pwg.txt`/`pw.txt`/`cae.txt`/`ccs.txt`; specimens
> pwg.txt L2413–2436 (PWG L490–492), pw.txt L2563–2576 (PW L681–684).
### §555. Apte rings both ways (and abbreviates grammar labels with it); Monier-Williams 1899 is the one dictionary with its own system — the seam printed IN the lemma (`agni—hotra`, 73 772×) plus a mid-word sandhi-seam ring

🟢 **Closes the §553/§554 series for the two remaining majors.** Measured over
[csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02);
NOTE the markup correction — §554's `{#˚`/`˚#}` metric silently missed MW,
whose lemmas are `<s>…</s>` (mw72: `{%…%}`), so MW showed 0/0 there. Recounted
in each dictionary's own markup:

| dict | entries | ring total | lead | trail | mid-word | seam in lemma (`<k2>`) |
|---|---|---|---|---|---|---|
| mw (1899) | 286 525 | 53 307 | 12 100 | 9 088 | **6 935** | **73 772** em-dash |
| mw72 (1872) | 55 390 | 21 099 | 75 | 846 | 1 | 0 |
| ap (rev.) | 90 843 | 5 150 | 2 353 | 1 290 | — | 61 |
| ap90 | 34 882 | 4 051 | 2 116 | 871 | — | 1 414 |

**Apte: leading dominates but the tail is alive, and the ring is not
compound-only.** ap90 2 116 lead vs 871 trail (`{#zazWa˚#}` = ṣaṣṭha°), ap
2 353 vs 1 290 — unlike Cappeller (§554: trailing rings are single-digit
noise), Apte keeps both directions in real use. Two Apte-specific practices:
(1) the ring also abbreviates *grammatical labels* — `[<sab>{#za˚ ta˚#}</sab>]`
= ṣaṣṭhī-tatpuruṣa, tatpuruṣa — so an Apte ring is not always a compound
member; (2) compounds live in the printed **—Comp.** block as hyphen-led
sub-lemmas, which the revised-Apte digitization renders as a `+` join:
`{#aMSaH#} + {#-aMSaH#}` — 36 248 such joins in ap (§554's "plus-analysis"
count for ap is this device, NOT a PWG-style etymology).

**Monier-Williams 1899 is structurally different from the whole §553 field.**
(1) It is the only dictionary that prints the compound seam *inside the lemma
itself*: `<k2>agni/—hotra`, em-dash, **73 772** of 286 525 lemmas, with nested
seams (`agni—hotrI—vatsa/`) and mixed dash+hyphen depth (`agni—hotra/-prAyaRa`).
Everyone else (§553) keeps the headword solid. (2) Its ring has THREE uses:
leading member-elision as in Cappeller (12 100), trailing truncation (9 088),
and — unique to MW — **6 935 mid-word rings** marking the seam where sandhi
fused the vowels and a dash cannot be printed: `<s>aM˚so<srs/>ccaya</s>` =
aṃsa + uccaya → aṃsôccaya (mw72 has exactly 1 such). (3) The 1872 edition
predates the system: no dashed lemmas at all, and its ring is a generic
"supply the rest of the word", both directions — the dictionary's own symbol
list says so verbatim: *"˚ that the rest of a word is to be supplied, e.g.
˚ri- in˚ after karīndra is for kari-indra"* (mw72.txt front matter, L1643).

**Practical residue:** (a) for MW-1899 the compound seam should be read from
the `<k2>` dashes, not reconstructed — it is the one CDSL source where the
lemma itself carries the analysis; (b) an MW mid-word ring is a *sandhi-seam*
marker, a third sense on top of §554's two — expansion passes must not treat
it as elision; (c) Apte rings require a label-vs-member disambiguation step
(`<sab>` context) before any expansion.

> Fable 5 (`claude-fable-5`) · 16-08-2026 · counts in native markup
> (`<s>˚`/`˚</s>` + letter-adjacent mid for mw; `{%˚`/`˚%}` for mw72; `{#˚`/`˚#}`
> for ap/ap90; `-` inside `<k2>`); specimens mw.txt L356, L4137–4160,
> mw72.txt L1643 (symbol list) + L50848, ap.txt L111, ap90.txt L115.
### §556. Grassmann hyphenates the lemma itself (4 356 of 12 785 — MW's system has a Rig-Veda precedent), and Kochergina's кружок is the Petersburg Kreis arriving in Russian via Böhtlingk's own St. Petersburg typography

🟢 **Closes the §553–§555 series.** Two dictionaries the census misread or
could not see:

**Grassmann (1873–75) prints the seam in the lemma — §553 undercounted him as
"no practice".** The seam lives in `<k2>`, which §553's `<k1>`-only metric
missed: **4 356 of 12 785** lemmas are hyphenated — `<k2>agni-jihva/`,
`agni-ta/p`, `agni/-dUta` (accent riding on either member). Rings and degree
signs: **zero**. So Grassmann is the pure-hyphenation pole of the field: every
compound analyzed in its own headword, no abbreviation device at all — and
running text hyphen-analyzes even derivation (`á-tas, á-tra, a-dyá`, gra.txt
L2). Consequence for §555: **MW-1899's seam-in-lemma system is not sui generis
— it generalizes Grassmann's Rig-Veda practice to the whole language**, 24
years later, upgrading the hyphen to an em-dash hierarchy and adding the
mid-word sandhi ring for the cases a hyphen cannot express. (MW-1872, before
Grassmann's influence sank in, has zero dashed lemmas — the 1899 redesign is
exactly the Grassmann move.)

**Kochergina (1978/1987): the digitization
([RussianTranslation/src/koch.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/koch.jsonl),
29 177 rows) carries 136 degree signs `°` (U+00B0; U+02DA absent — same
digitization split as sch/ae, §553) in three PW-shaped uses:**

1. *Leading elision in cross-references*: `-ṣṭhīvi … см. °ष्ठीव` — the ° stands
   for the elided first member, exactly PW's dominant profile (§554).
2. *Bound second members as headwords with a leading hyphen*: `-zWIvi`,
   `-varzIya` — the lemma itself is marked as "second member of a compound".
3. *Trailing continuation on prefixes*: `अ° /a-/ (перед гласными अन्°)` — the
   rest of the word is to be supplied, Böhtlingk's trailing truncation.

**Where her кружок comes from.** The sign is Böhtlingk's Kreis (§554), and the
transmission is direct, not typological: PW/PWG were typeset and published by
the Imperial Academy of Sciences **in St. Petersburg** (1855–75; PW 1879–89),
so the ° entered Russian academic Sanskrit typography at the source — Russian
indology inherited Böhtlingk's printing conventions with his books, and
Kochergina's dictionary (ред. В. И. Кальянов, of the same Petersburg school;
its preface names Böhtlingk's dictionaries among its sources) reproduces the
малый-PW usage profile measured above: leading elision as the main sense,
trailing truncation as the secondary. Her sense ORDER diverges from the
tradition (§18, §~769: logical-pedagogical, not chronological) — the
*typography* is the thing she kept.

**Practical residue:** (a) any §553-style census must read `<k2>`, not `<k1>`
(two corrections now: MW §555, GRA here) — `<k1>` is normalized-solid by CDSL
convention and never shows the source's own practice; (b) koch.jsonl's
leading-hyphen lemmas (`-zWIvi`) are a *lemma-class marker*, not noise — a
matcher joining Kochergina to CDSL headwords must strip the hyphen but keep
the "bound second member" bit.

> Fable 5 (`claude-fable-5`) · 17-08-2026 · counts: `-` inside `<k2>` of
> gra.txt (4 356/12 785), U+02DA/U+00B0 over gra.txt (0/0) and koch.jsonl
> (0/136); specimens gra.txt L412–454, koch.jsonl rows for -zWIvi/-varzIya/a-.
> Kochergina provenance: measured profile + documented Petersburg publication
> chain; her print's front matter not re-read this pass.
### §557. Benfey analyzes every second entry in prose (`i. e. apa-car + in`, 9 168×) and keeps the ring for conjectures; Mylius has no measurable source in the org — named gap, not a shrug

🟢 **Benfey (1866) is a third analytical pole, distinct from both Böhtlingk's
ring and Grassmann's lemma-hyphen.** Measured over `ben.txt` (17 316 entries):

- **9 168 entries — 53 % — open with a prose analysis** `<ab>i. e.</ab>` giving
  the derivation with hyphens for compound seams and `+` for suffixes, and with
  **sandhi undone**: `abhyantara, i. e. abhi-antara` · `apacārin, i. e.
  apa-car + in` · `abhrāvakāśika, i. e. abhra-avakāśa + ika` · `āgatva, i. e.
  ā-ga + tva (vb. gam)`. Counts: 10 884 `+`-joins and 9 353 hyphen-bearing
  analysis spans inside `{%…%}`. This is richer than PWG's `(agni + hotra)`
  (§554): Benfey decomposes to derivational morphology, not just the compound
  seam, and resolves the sandhi in the analysis.
- **The headword stays solid** (0 hyphens in 17 310 `<k2>`, §556's lesson
  applied) — the analysis lives in the body, unlike Grassmann/MW.
- **The ring is marginal and bidirectional: 506 total** (255 leading / 221
  trailing inside `{%…%}` spans), and its habitat is *text-critical notes*, not
  compound runs: `read {%ābhy˚%}` · `corr. {%˚cāriṇaḥ%}` · `instead of
  {%˚śnīy˚%}, on account of the metre` · `{%cā˚%} must be read instead of
  {%nā˚%}`. Benfey uses the Kreis the way PWG's *trailing* majority does
  (§554) — word truncation in citations — at 1/30th the density.

**Mylius (Wörterbuch Sanskrit-Deutsch, 1975): cannot be measured here — the
org holds no digitization of his dictionary's structure.** He exists in the org
exactly once, as an *unmarked, cannot-be-isolated* rights-risk source of the
ReverseDictionary (H1153 rights ledger: his contribution carries no source
code, so it cannot even be subtracted). Any statement about his compound
typography would be from memory, not data — the census answer for Mylius is
**"no source, no claim"**; measuring him needs a scan/copy of the printed book
(in copyright, so acquisition is a separate rights-aware step, not a scrape).

> Fable 5 (`claude-fable-5`) · 17-08-2026 · counts over ben.txt: `<ab>i.
> e.</ab>` 9 168, `+`-joins in `{%…%}` 10 884, hyphen-analysis spans 9 353,
> rings 506 (255 `{%˚` / 221 `˚%}`); specimens ben.txt L1550, L2992, L4080,
> L4205, L5834, L6659. Mylius: absence verified against csl-orig/v02 dict list
> and hub_grep (only H1153/H270 rights rows).
### §558. Wilson closes 89 % of entries with a prose `E.` etymology and uses no graphic device at all; Macdonell runs FOUR coordinated devices — including `˚—`/`—˚` as a grammatical notation for position-in-compound

🟢 **Fifth entry of the §553–§557 series; these two close the majors.**

**Wilson (1832/1855) is the prose-etymology pole, before any graphic device
existed in Sanskrit–English lexicography.** 0 rings, 0 degrees, `<k2>` solid
(0/44 577); instead **39 713 of 44 577 entries — 89 % — end with an
`<ab>E.</ab>` etymology section**: `agnihotra … E. agni and hotra oblation
with fire, burnt offerings` (wil.txt L312). The leading-hyphen forms in his
bodies (`({#-traM#})`, `({#-traH#})`) abbreviate *inflection*, not compound
members. Benfey's `i. e.` analysis (§557) is Wilson's `E.` condensed and made
morphological; MW grew out of Wilson's chair — the English line starts here,
analysis in prose, headword untouched.

**Macdonell (1893) is the most engineered typography in the whole census —
four devices with distinct semantics** (md.txt, 20 749 entries):

1. **~13 119 hyphenated transliterated lemmas**: the SLP1 headword stays solid
   but the romanized repeat carries the analysis with accent —
   `agni-hotrá`, `agni-hotra-hávaṇī` (L1147–L1160). Grassmann's seam-in-lemma
   (§556) adopted into a classical-Sanskrit concise dictionary.
2. **2 852 underties `‿`** marking the sandhi-fused seam: `a-kravya‿ad`
   (L596) — the same problem MW-1899 solves with its 6 935 mid-word rings
   (§555), *older* (1893 < 1899) and with a dedicated sign instead of an
   overloaded ring.
3. **`˚—` (409) and `—˚` (4 258) as positional grammar labels**: `˚—` = "as
   prior member of a compound" (`a-kāraṇa … ˚—, -tas, -m` L304), `—˚` = "at
   the end of compounds" (`akṣa m. n. organ of sense: —˚ = ákṣi, eye` L652).
   The ring+dash pair here is not abbreviation — it is a **grammatical
   notation for position-in-compound**, the exact semantic the pwg_ru
   compound-position marker (h2805 Q3) encodes; Macdonell is its closest
   historical precedent in the census.
4. Classic elision rings for sub-forms: `{#˚da#} -da` (137 leading in `{#…#}`),
   plus the prefix lemma `a˚ / an˚` (L11–12).

**Practical residue:** (a) Macdonell's translit layer, not his SLP1 `<k2>`, is
where his analysis lives — a §553-style census must scan the body translit for
md (third markup correction after MW §555 and GRA §556); (b) the `˚—`/`—˚`
pair is prior art for any "какой глиф ставим на позицию в композите" decision
— it distinguishes *initial* vs *final* position with one sign-order flip;
(c) `‿` vs mid-word ring vs nothing is a three-way split (md/mw/everyone else)
for the sandhi-fused seam — crosswalks between md and mw lemma analyses must
normalize it.

> Fable 5 (`claude-fable-5`) · 17-08-2026 · counts over wil.txt/md.txt:
> `<ab>E.</ab>` 39 713/44 577; md underties U+203F 2 852, `<ab>˚—</ab>` 409,
> `—˚` 4 258, rings 4 827, hyphenated translit lemmas ~13 119 (regex over the
> post-`¦` lemma repeat); specimens wil.txt L312, md.txt L11–12, L304, L324,
> L596, L652, L1147–1160.

### §559. «Смыслы MW/AP, отсутствующие у PWG-семейства» — механический счёт завышен ~в шесть раз; 83 % кандидатов «отсутствует» на поверку «не привязано»

🟢 **Волна 4 (issue #1736, H2882).** По 261 истинной лемме стора pwg_ru
(11 603 смысловые строки слоёв pwg/pw/sch/pwkvn/nws) детерминированное
выравнивание «якорением на санскрите» (метод csl-atlas
[A09](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PAPER_SENSE_ALIGNMENT.md):
SLP1-токены цитируемых форм + нормализованные `<ls>`-якоря; глоссы не
используются — §541) даёт: MW 1 482 единицы смысла → 127 matched, 1 023
unalignable, 100 family_thin, **232 absent_candidate**; AP90 1 285 → 203 /
708 / 74 / **300**; лемм целиком нет в MW — 8, в AP90 — 119. Ручная
адъюдикация случайной выборки 30 кандидатов: лишь **5/30 (~17 %)** —
правдоподобно настоящие лакуны; остальное — тот же смысл с непересекающимся
цитатным аппаратом (37 %), омоним/заглушка окна среза (23 %), артефакт
деградированного ключа леммы (23 %, §560). Экстраполяция: настоящих смысловых
добавок MW+AP на весь срез — **порядка 40–90**, на порядок ниже наивных 532.
Профиль выживших добавок жанровый, не случайный: MW — Rājataraṅgiṇī и
лексикализация ifc.-композитов; Апте — аланкара-шастра (Sāhityadarpaṇa) и
джьотиша («знак Тельца» у anaḍuh). Сходится с A09-H3 («потомки копируют или
сжимают») и §97 (MW составлен из PW/PWG). Метод сертифицирует **присутствие**
(matched-точность 8/8 по выборке), но не отсутствие — absent_candidate есть
верхняя граница. Полный отчёт:
[RussianTranslation/pwg_ru/MW_AP_SENSE_COVERAGE_W4.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/MW_AP_SENSE_COVERAGE_W4.md);
датасет: [mw_ap_sense_coverage.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/mw_ap_sense_coverage.jsonl).

> Fable 5 (`claude-fable-5`) · 17-08-2026 ·
> [mw_ap_sense_coverage.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_ap_sense_coverage.py)
> (selftest 11/11) над csl-orig mw.txt / ap90.txt + стором pwg_ru; адъюдикация
> 30 кандидатов seed=4.

### §560. `key1` стора pwg_ru деградирован у 161 строки — и сливает разные леммы в один ключ; лучший свидетель — префикс `subcard`, но и он врёт о долготе/придыхании

🔴 **Integrity-находка волны 4** ([issue #1767](https://github.com/gasyoun/SanskritLexicography/issues/1767)).
В каноническом сторе `pwg_ru_translated.jsonl`
поле `key1` у 161 из 11 603 строк — уплощённая форма леммы (`apta` вместо
`Apta`, `gawa` вместо `Gawa`, `asru` вместо `aSru`), а у трёх ключей уплощение
**сливает разные слова**: `vasa` = vāsā/vāsa/vaśā/vaśa/vasā (пять лемм!),
`bara` = bhāra/bhara/bāṇa, `vasin` = vāsin/vaśin. Одна строка несёт в `key1`
вообще мусор субкарты (`durg_a~~h0_zz_sch`). Поле `iast` тоже местами
деградировано (`gaṭa` при de-тексте {#Gawa#}, `manorata` при {#manoraTa#}).
Самый надёжный свидетель — **префикс `subcard` до `~~`** с декодом `_c` →
заглавная C (проверено: 11 442/11 603 строк совпадают с key1, все расхождения —
в пользу subcard), но и он недостоверен у меньшинства строк по
долготе/придыханию: subcard даёт `Atura`/`satkAra`/`utTa`/`havyavAha` там, где
de-текст держит a/tura «nicht reich» / satkara / utta / havyavaha. **Любой
consumer, группирующий стор по `key1`, смешивает статьи разных слов.**
Обнаружено сличением с `<k1>` MW/AP90 (волна 4, §559): четверть ложных
«absent» — прямое следствие. Канонический стор по забору волн — read-only;
починка ключей — отдельная волна с голосованием, не тихий фикс.

> Fable 5 (`claude-fable-5`) · 17-08-2026 · верификация декода subcard по всем
> 11 603 строкам + выборочное сличение de-текста; см. §559.
### §561. Whitney has no ring at all — his device is the leading hyphen on bound stems (Roots 1885) and analysis-only hyphenation (Grammar); attested compounds are quoted solid with accent

🟢 **Sixth entry of the §553–§558 series: Böhtlingk's two dictionaries vs
Whitney.** Whitney is a different *kind* of book on both counts, and his
typography follows the function:

**Roots 1885 (read from the print scan
[csl-whitroot/jpg/whit-023-kft2.jpg](https://github.com/sanskrit-lexicon/csl-whitroot/blob/master/jpg/whit-023-kft2.jpg),
p. 23, the kṛ/kṛt/kṛp/kṛś/kṛṣ block).** Nominal compounds are not registered
at all — the unit is the root, with preverb combinations as a bare upasarga
list (the org's own
[roots-with-upasargas.txt](https://github.com/sanskrit-lexicon/csl-whitroot/blob/master/misc/roots-with-upasargas.txt):
`√ 1 kṛ (skṛ) "make" (adhi, anu, apa, abhi, ā, upa, ni, nis, pari, pra, vi,
sam)`). In the `Deriv.:` columns, **a leading hyphen marks a stem that occurs
only as the final member of a compound**: `-kartin c.`, `-karttṛ E.+`,
`-kṛnta B.`, `-kṛṣya s.+`, `-kraṣṭṛ c.`, `karṣin, -ṣí B.+` — free-standing
stems sit solid beside them (`kartá v.+`, `kṛntátra v.B.`). No ring, no
degree, anywhere; a cited preverb-compound word is printed solid
(`Samskṛtatrá v¹`).

**Grammar (2nd/3rd ed.; measured over
[WhitneyRoots/src/wg_text.txt](https://github.com/gasyoun/WhitneyRoots/blob/main/src/wg_text.txt)).**
Attested compounds are QUOTED SOLID with their accent — `devasenā́`,
`yamadūtá`, `jīvaloká`, `brahmagavī́`, `mitrā́váruṇā`, `indrāgnī́` (§1264,
§1255 examples). Hyphens appear in exactly two analytic functions: (1)
sandhi-resolved decomposition in parentheses, Benfey-style — `rājendra
(rāja-indra)`, `maharṣiḥ (mahā-ṛṣiḥ)`, and occasional analytic spellings like
`deva-nāgarī`; (2) leading-hyphen citation of bound members — `-arthe and
-kṛte` (§1116 adverbial locatives), `-kṛtya, -çrútya`, and the index
convention `-kṛt, see 1105`. **OCR caveat, named:** wg_text.txt line-wrap
hyphens (`indra-` / `dhanús` across a break) look identical to analytic
hyphens — any automated count over this file must join wrapped lines first.

**The contrast with PW/PWG (§554) in one line:** Böhtlingk abbreviates
(ring = "do not reprint what is shared"), Whitney classifies (hyphen = "this
stem is bound") — the Petersburg ring's elision job simply has no equivalent
in Whitney because his book never lists compound runs to abbreviate.
Kochergina's hyphen-led lemmas (`-ṣṭhīvi`, §556 use 2) sit on Whitney's line
of the tradition, while her ° sits on Böhtlingk's — she inherited both.

> Fable 5 (`claude-fable-5`) · 17-08-2026 · print scan whit-023 (p. 23) read
> directly; wg_text.txt specimens L682, L2045–2047, L4050, L18955, L20861,
> L21729–21755, L23245–23247; upasarga list csl-whitroot/misc. The Roots
> full text is NOT digitized in the org (scan images + root inventory only) —
> the scan page is the evidence of record for the hyphen convention.

### §562. Печатный заголовок карточки ОПРОКИДЫВАЕТ §560: дефект стора pwg_ru — не деградация key1, а инжест ЧУЖОЙ статьи-двойника; настоящие статьи 60+ целевых лемм в сторе отсутствуют

🔴 **Ревизия §560 по третьему свидетелю** (печатный заголовок `{#lemma#}¦` в
самом de-тексте карточки). §560 утверждал «все расхождения — в пользу
subcard»; проверка заголовков показала обратное: в **61 из 73** групп
расхождений заголовок согласен с **key1** против subcard. Причина — дефект не
в ключе, а в **инжесте**: пайплайн, идя за целевой леммой (сохранена в
префиксе subcard: vāsā, bhāra, āpta, aśru…), по уплощённому ключу вытащил
**статью-двойника** (vasa, bara, apta, asru…) и записал её контент под
сабкарту целевой леммы. Где один уплощённый ключ покрывал несколько целевых
лемм, один и тот же неверный контент лёг **побайтово несколько раз**: крошечный
стаб *vasa* (nom. act.) лежит в сторе пять раз — под vāsā/vāsa/vaśā/vaśa/vasā,
чьи настоящие (большие!) статьи PWG в сторе, следовательно, **отсутствуют**;
то же bara→bhāra/bhara/bāṇa, vasin→vāsin/vaśin. Механическая классификация
([key1_repair_proposals.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/key1_repair_proposals.py)):
3 доказанные дубликации + 52 одиночных «чужая статья» + 1 мусорный key1 = 56
предложений, ровно 161 затронутая строка. **Уточнение (ruling MG, 17-08-2026):**
«чужая статья» — это ДВЕ разные ситуации, и метить их одинаково нельзя:
(а) *случайный двойник* — слова не родственны, их связала только коллизия
уплощения (advan «essend» от √ad ≠ adhvan «дорога»: d/D), 44 карточки;
(б) *родственная отсылка* — попавший стаб сам печатает целевую лемму
(anukampa «s. anukampA» — пара m./f.; asru «s. aSru»; всего 8: anukampā,
arśas, aśru, kalaśa, menā, parihāra, rāmaṭha, vedikā). Детектор механический:
целевая лемма как точный токен в {#…#}-материале карточки. Следствие для §559 (волна 4): для
этих ~60 лемм сравнение MW/AP шло против контента двойника — их вердикты
недействительны в обе стороны. Починка = **переингест + карантин**, не
переименование ключей; голосуется листом
[key1_repair_vote_2026-08-17.html](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/key1_repair_vote_2026-08-17.html)
(issue [#1767](https://github.com/gasyoun/SanskritLexicography/issues/1767)); стор не тронут.

**Постскриптум 28-08-2026 (H2996) — применено.** Голосование не понадобилось:
все 56 карточек прошли гейт печатного заголовка, отложенных — **0**. Карантин
159 строк (44 `wrong_entry` · 8 `wrong_entry_xref` · 3 `wrong_entry_dup`),
стор 11 621 → 11 462 (−159, ожидаемо: карантин не удаляет — строки сохранены
дословно с блоком `_quarantine`); 61 целевая лемма поставлена в переингест-
worklist. Ни одной строки, тронутой человеком, не удалено (все 161 были
`ai_translated`, `reviewer: None`). LANG_PARITY: вердикт
**INTENTIONAL-DIVERGENCE** (запись `wrong_entry_quarantine_reingest_h2996`) —
EN-стора не существует вовсе, портировать некуда; при появлении EN-стора вердикт
пересматривается.

**Гейты — и ошибка измерения, которую пришлось исправлять.** `window_selftest`
213/213 до и после. `placement_axis_check` сначала **упал**: карантин 159 строк
осиротил 30 строк производного сайдкара `src/pwg_ru_relationships.jsonl`, чей
`placement: true` указывал на смыслы, только что покинувшие стор, а гейт строит
индекс смыслов **из стора** — A2 FAIL, exit 1. В первой версии отчёта, этого
постскриптума, changelog и комментария к issue гейт был записан как «OK». Это
было неверно: exit-код читался после **конвейера** (`| tail`), то есть измерялся
`tail`, а не гейт, и отсутствие строки `placement_axis_check: OK` было принято
за её наличие. CI это не ловит — там гоняется только `window_selftest`, а
placement-гейт ручной и над gitignored-стором. Починено в корне: сайдкар —
**чистая производная** стора (`build_relationships.py` ничего не переводит, все
6374 строки `confidence: llm`, ни одного человеческого поля), поэтому он просто
перестраивается, и `apply_key1_repair.py` теперь делает это сам после записи
стора (`--no-sidecar-refresh` отключает). После перестройки: 6374 → 6320 строк,
661 → 633 placed, A2 = 0, **exit 0**.

**Производные: две чистые, две нет.** `.enriched` и `.renou` (по 217 строк) не
содержат ни одной карантинной строки. Сайдкар содержал 30 висячих привязок —
починен выше. **TM-зеркало `pwg-ru-data/tm/` по-прежнему держит все 159
карантинных строк** (`only_mirror` 6 → 167) — оно в другом репозитории, вне
забора этого handoff'а, и НЕ обновлено. Это важно: окно переингеста с
`--tm=auto` пере-выдаст ровно те карточки, которые только что вынесены в
карантин (ловушка, которую `requeue_from_audit.py` обходит обязательным
`--no-tm`), поэтому каждая единица worklist'а несёт требование `--no-tm`.
Обновление зеркала — долг, не закрытый здесь.

**Уточнение к §562:** `junk_key1` (`durg_a~~h0_zz_sch`) —
единственный класс, который НЕ карантинится: его печатный заголовок и есть
целевая лемма (`durgā`), т.е. контент верен, испорчен только ключ; к тому же
карточка слоя `sch`, и обход всех 123 366 записей PWG показал, что для `durgA`
записи-источника нет — переингест было бы нечем закрыть. Исправлено на месте
(`key1 = durgA`). Переводы НЕ выполнялись: переингест идёт штатным пайплайном,
платное окно требует live-gate GO, поэтому вердикты волны 4 (§559) по этим ~60
леммам остаются недействительными до тех окон. Протокол:
[reports/H2996_WRONG_ENTRY_QUARANTINE_REINGEST_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H2996_WRONG_ENTRY_QUARANTINE_REINGEST_28-08-2026.md);
проход [src/apply_key1_repair.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/apply_key1_repair.py).
Историческое место уплощения ключа **не найдено** и исправленным не считается —
worklist обезврежен конструктивно (точный SLP1-ключ + контракт «сопоставлять
`<k1>` строго, без сворачивания регистра»).

> Opus 5 (`claude-opus-5`) · 28-08-2026 · постскриптум H2996.

> Fable 5 (`claude-fable-5`) · 17-08-2026 · три свидетеля на группу
> (key1 / subcard-декод / печатный заголовок + iast через sanskrit_util);
> дубликация доказана идентичными (sense_tag, de)-наборами под разными
> сабкартами; полные дампы vasa/bara в сессии H2882-продолжении.
> (superseded: §563 assigned below)

### §563. Symmetric akshara word-squares over inflected beginner vocabulary are structurally near-infeasible — word-medial syllables almost never begin words

Measured while composing a 4×4 "sarvatobhadra-lite" for
[/crossword/bandha/](https://samskrtam.ru/crossword/bandha/) (H2944): over a
curated 74-form pool of 4-akshara beginner word forms (stems, textbook
inflections, transparent compounds; register grounded in kosha
`lemma_frequency.tsv` core_rank), BOTH search modes returned **0 solutions** —
(a) symmetric square (rows = columns, each row a real word), (b) double word
square (rows and columns independent words, prefix-pruned DFS). The finder was
self-tested against a synthetic known-good square before trusting the zero.

Cause is structural, not pool size: Sanskrit inflection concentrates
word-INITIAL syllables on a small CV set (`ka/va/na/ga/sa/ma…`) while
word-MEDIAL syllables are dominated by conjuncts and matra-heavy shapes
(`ṣya`, `sya`, `nā`, `ne`, `ccha`) that essentially never begin a word — yet a
square needs every medial syllable of one word to head another. Enlarging the
pool does not fix the intersection; classical sarvatobhadras evade it by using
CONTINUOUS verse text under sandhi (full kāvya difficulty), not dictionary
words. Consequence for future puzzle/composition work: an akshara word-square
generator over vocabulary lists is a dead end; either compose verse-style
continuous text or drop to letter-level (losing the akshara-cell principle).
A solvable gomūtrikā, by contrast, is easy (only even-position syllables must
coincide across two lines) — one shipped the same pass
([docs/RESULTS_BANDHA_FILLIN_H2944_17.08.26.md](https://github.com/gasyoun/Uprava/blob/main/docs/RESULTS_BANDHA_FILLIN_H2944_17.08.26.md)).

> Fable 5 (`claude-fable-5`) · 17-08-2026 · search script + pool in the H2944
> session scratchpad; goal-line 2-attempt budget honoured (form ships
> explorer-only). §564 takes the next number.

### §564. skd/vcp confirm ZERO graphic compound markers — the kośas print the whole apparatus in Sanskrit: SKD spells the vigraha + class term in parentheses, VCP compresses the same grammar into ॰-abbreviations with a numeral for the vibhakti (`6 ta0` = ṣaṣṭhī-tatpuruṣa)

🟢 **Seventh entry of the §553–§558/§561 series; census item §5.6 (H2983,
Fable 5, `claude-fable-5`).** The §553 sweep measured skd (Śabdakalpadruma, Calcutta
1821–57) and vcp (Vācaspatya, Calcutta 1873–84) at zero Western markers.
Read directly, the two Sanskrit-Sanskrit kośas turn out to run a COMPLETE
compound-marking apparatus — in the object language itself. Method as
bound by the series: entry-wise parse of
[v02/skd/skd.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt)
and
[v02/vcp/vcp.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt)
(SLP1 transliteration of an all-devanāgarī print), OCR line-wraps joined
before counting (64 884 wrap-hyphen lines in skd, 126 597 in vcp), counts in
each file's own markup, `<k2>` checked separately.

**The zero, sharpened.** skd: 0×`˚` 0×`°` 0×`॰`, 0 hyphenated `<k2>` of
42 531 entries. vcp: 0×`˚`, 4×`°` (stray), 0×`॰`, 2 hyphenated `<k2>` of
50 135. Headwords solid, `<k2>` = `<k1>` in both. But the print DOES use the
devanāgarī abbreviation sign ॰ — the digitization renders it as ASCII
**`0`**, which no Unicode glyph census can see. That is where the apparatus
lives, and the two kośas divide it exactly as their generations suggest.

**Counts (whole files, entry-parsed):**

| device | skd (42 531 entries) | vcp (50 135 entries) |
|---|---|---|
| headword delimiter `¦` (U+00A6) | 42 196 | 48 384 |
| single daṇḍa `.` | 443 340 | 373 705 |
| double daṇḍa `..` | 199 538 | 2 141 |
| `iti` (free) + fused `ity`- | 80 130 + 24 319 | 15 575 + 22 860 |
| `“…”` quote blocks (opens) | 53 135 | 76 772 |
| `yaTA` example introducer | 31 553 | 9 089 |
| `+` derivation joins | 29 771 | 10 275 |
| `--` morpheme seams (letter--letter) | 346 (124 entries, root tag-chains) | 23 328 (19 174 entries — 38 % of the book) |
| ॰-abbreviations (`letter0` in the digitization) | 4 633 (dhātu apparatus only) | **167 759** (~3.3 per entry) |
| parenthesis opens | 58 688 | 10 560 |
| spelled compound-class terms | ≈1 300 | ≈500 |
| ॰-abbreviated class tags (`N ta0`/`na0 ta0`/`ba0`/`karma0`/`sa0`) | 0 | ≈9 100 |
| numbered senses | postpositive synonym lists | prepositive `. N gloss` — 35 050 hits in 17 243 entries |

**SKD article grammar — the parenthesis is the apparatus.** Shape:
`headword¦, gender, ( vigraha . class-term . derivation ) sense . sense .
iti <source-in-full> .` — everything grammatical sits inside `(…)`, spelled
out, with the analysis as a Sanskrit sentence and the compound class as a
Sanskrit noun:

- `agnirakzaRaM¦, klI, (agneH rakzaRam . zazWItatpuruzaH .)`
  ([skd.txt:1912](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L1912),
  L244) — genitive vigraha, then the class, each closed by daṇḍa.
- `agnihotraM¦, klI, (agnaye hotram atra iti bahuvrIhiH .)` and deeper in
  the same article `agnaye hotraM homo yasmin karmmaRIti
  vyaDikaraRabahuvrIhiH`
  ([skd.txt:2106](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L2106),
  L267) — the entry argues TWO competing vigrahas, subtype named
  (vyadhikaraṇa-bahuvrīhi).
- `agrajanmA¦, [na] puM, (agre janma yasya sa bahuvrIhiH,) (jan + BAve
  manin)`
  ([skd.txt:2263](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L2263),
  L283) — vigraha parenthesis + separate `+`-chain derivation parenthesis
  (the layer the org's
  [SKD/VCP etymology extractor](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/README_etymology.md)
  already mines; 2 214 skd derivations, not re-counted here).
- `akupyaM¦, klI, (na kupyaM, kupyAdanyadityarTaH . naYsamAsaH .)`
  ([skd.txt:549](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L549),
  L73) — nañ-compound named, gloss via `ityarTaH` (919× in skd).
- `agnisaKaH¦, puM, (agneH saKA iti samAse rAjAhaHsaKiByazwac iti
  samAsAntazwac .)`
  ([skd.txt:2041](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L2041),
  L260) — the justification is a Pāṇini rule quoted BY TEXT inside the
  vigraha; elsewhere sūtras carry daṇḍa-separated numeric loci:
  `(Saka + “SakisahoSca .” 3 . 1 . 99 . iti yat .)`
  ([skd.txt:477942](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L477942),
  L34692).
- `rAjahaMsaH¦, puM, (haMsAnAM rAjA SrezWatvAt . rAjadantAditvAt
  paranipAtaH .) … ityamaraH . 2 . 5 . 24 ..`
  ([skd.txt:396453](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L396453),
  L29488) — irregular member ORDER flagged by rule name (paranipāta,
  43×), and the Amarakośa locus printed as daṇḍa-separated digits: the
  daṇḍa doubles as sentence-end AND decimal separator (16 452 numeric
  `x . y . z` loci in 10 760 entries — a hard parser trap).
- `pawalaprAntaM … CA~ci iti BAzA . tatparyyAyaH . valIkam 2 nIvram 3 .`
  ([skd.txt:238176](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L238176),
  L19985) — `iti BAzA` closes a BENGALI vernacular gloss (3 683× — a
  whole gloss layer invisible to any Latin-script census), and synonym
  runs number POSTPOSITIVELY (`valIkam 2 nIvram 3`), the reverse of vcp.
- Root articles are the one place skd itself abbreviates:
  `rewa¦, f Ya yAce … (BvA0-uBa0-dvika0-sew .)`
  ([skd.txt:405209](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L405209),
  L29854) — hyphen/`--`-chained ॰-tags (bhvādi-ubhayapadī-dvikarmaka-seṭ);
  all 4 633 skd `0`-abbreviations are of this dhātupāṭha kind (`uRA0` 885,
  `saka0` 836, `para0` 765, `BvA0` 656…).

Spelled class terms across skd: `naYsamAsa` 386, `karm(m)aDAraya` 288,
`tatpuruza` 222 (116 as `zazWItatpuruza`), `dvandva` 119, `bahuvrIhi` 88,
`upapadasamAsa` 71, `samAsAnta` 47, `paranipAta` 43, `avyayIBAva` 39.
(`dvigu` is uncountable by grep — swamped by `dviguRa` "double".)

**VCP article grammar — the same apparatus, compressed ~30 years later.**
Shape: `headword¦ gender0 vigraha derivation--seam class0 . 1 sense-locus 2
sense-locus`. Everything skd spells, vcp ॰-abbreviates — gender (`pu0`
21 885, `tri0` 14 952, `na0` 11 620, `avya0` 1 108, `puMstrI0` 926),
sources (`rAjani0` = rājanirghaṇṭa 5 090, `medi0` 2 851, `hemaca0` 2 161,
`trikA0` 1 824, `Sabdaca0` 1 330, `Sabdara0` 1 143, `BAvapra0` 1 054,
`amara` spelled), grammar authorities (`pA0` = pāṇini 2 142, `sU0` 2 504,
`si0 kO0` = siddhāntakaumudī 1 631/846, `pfzo0` = pṛṣodarādi 1 122,
`vArtti0`), citation loci (`a0` = adhyāya 6 853, `BA0 … 56 a0`, `f0 1 .
61 . 14` for the Ṛgveda) — and, the census payload, the **compound class
with a numeral carrying the vibhakti of the first member**:

- `agnihotra¦ na0 agnaye hUyate'tra hu--tra 4 ta0 .`
  ([vcp.txt:2770](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L2770),
  L350) — vigraha, root--affix seam, then `4 ta0` = caturthī-tatpuruṣa;
  the article then argues the same bahuvrīhi/tatpuruṣa split as skd but
  from the Taittirīya-brāhmaṇa, with `bahuvrIhivyutpattyA … iti
  tatpuruzavyutpattyA` spelled out.
- `agrajAti¦ pu0 agrA SrezWA jAtiryasya, jana--ktin karma0 . vipre .`
  ([vcp.txt:3145](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L3145),
  L380) — vigraha FIRST, unparenthesized; class ॰-tagged (`karma0` 937×).
- `aMSasavarRRana¦ … atulyacCedayoH rASyoH samacCedakaraRam 6 ta0 .`
  ([vcp.txt:93](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L93),
  L8) — `6 ta0` = ṣaṣṭhī-tatpuruṣa. Numeric-vibhakti tags total 3 701:
  `6 ta0` 3 086 · `7 ta0` 285 · `3 ta0` 191 · `5 ta0` 106 · `4 ta0` 18 ·
  `2 ta0` 14 — ṣaṣṭhī at 83 %, the whole vibhakti system productive.
  Plus `na0 ta0` (nañ-tatpuruṣa) 1 192, `na0 ba0` (nañ-bahuvrīhi) 252,
  `ba0` 1 273 total, `sa0` = samāsa 2 016 (`upa0 sa0` 368, `aluk sa0` 48,
  `mayU0` = mayūravyaṃsakādi 42, `asama0 sa0` — asamartha — 15).
- `akarttana¦ … na0 ta0 . uccaviroDihrasvatvavati Karve . kfta--BAve lyuw
  na0 ba0 . CedanAkarttari tri0 .`
  ([vcp.txt:399](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L399),
  L55) — one article, per-SENSE reclassification: the same surface word
  read as nañ-tatpuruṣa in one sense and nañ-bahuvrīhi in the next. The
  class tag is sense-scoped, not entry-scoped.
- `rAjahaMsa¦ puMstrI0 haMsAnAM rAjA SrezWatvAtrAjada0 para0 . … 2
  kalahaMse ca medi0 .`
  ([vcp.txt:453301](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L453301),
  L39539) — skd's spelled `rAjadantAditvAt paranipAtaH` compressed to
  `rAjada0 para0`; prepositive sense numbers with ॰-tagged sources.
- `pItAmbara¦ pu0 pItamambaraM yasya . 1 SrIkfzRe amara 2 SElUze nawe ca
  medi0 3 haridrABavastrayukte tri0 karma0 . 4 pItevasage na0 .`
  ([vcp.txt:401693](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L401693),
  L32328) — senses 1–2 ride the opening bahuvrīhi vigraha; sense 3
  re-derives the SAME word as karmadhāraya with its own gender. Compare
  skd's version of the same lemma
  ([skd.txt:264057](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/skd.txt#L264057),
  L21731), which conveys the karmadhāraya reading by verse quotation
  instead.
- `gajAnana¦ … iBAnanaSabde 981 pf0 dfSyam .`
  ([vcp.txt:225675](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L225675),
  L16764) — internal PAGE cross-reference `<word>Sabde NNN pf0 dfSyam`
  ("see under X, p. NNN"), 1 116 of these — vcp's reference graph is
  page-numbered, unlike skd's purely lemma-based `iti`-net.

**The finding in one line: the kośas DO have a "ring" — it is ॰, but it
points the other way.** The European dictionaries aim `˚` at the OBJECT
word (elide/truncate the repeated member, §553–§555); the kośas aim ॰ at
the METALANGUAGE (gender terms, source titles, rule names, class labels)
and never abbreviate the object word — headwords and compounds are always
printed whole. skd (1821–57) still spells most of the apparatus; vcp
(1873–84) industrializes ॰ to 3.3 abbreviations per entry, with the numeral
innovation for vibhakti. Apte's `[za˚ ta˚]` class tags (§555) are this
native device stepping westward — Poona 1890 transliterates what Calcutta
1873 printed as `६ त॰`, swapping the numeral back to a spelled ordinal.
Grammar of the sign, per the §553 conclusion's method: same glyph family,
third distinct grammar — Böhtlingk's "do not reprint", MW's "seam here",
and the kośas' "expand this label".

**Parser taxonomy (what a converter needs, per device):** (1) `¦` =
headword/article boundary, >99 % reliable in both. (2) In skd, `(…)` scopes
the ENTIRE grammatical apparatus — vigraha sentence, spelled class noun,
`+`-chain derivation; outside parens, `.` segments senses/synonyms, `iti
<source> .` closes attribution blocks, `..` closes quotes/articles, `iti
BAzA` marks Bengali glosses. (3) In skd, digit runs between daṇḍas after a
source name are LOCI (`2 . 5 . 24` = 2.5.24) and must be joined before any
daṇḍa-based segmentation; postpositive digits after synonyms are list
indices. (4) In vcp, every `letter+0` token is a ॰-abbreviation — an
expansion table is required (top-40 inventoried this pass; families:
gender / source / authority / class / dhātu tags / loci); `--` is a
morpheme seam (root--affix); `N ta0` decodes as vibhakti-N tatpuruṣa;
prepositive `N` before a gloss is a sense number; `Sabde N pf0` is a page
xref; `{{Lbody=N}}` marks digitization sub-entries. (5) Class tags are
sense-scoped in vcp — a per-entry "compound type" column is WRONG by
construction.

**Residue (named, unmeasured):** the full ॰-expansion table (only top-40
forms inventoried; a complete vcp abbreviation lexicon is a bounded
follow-up); skd `<C1>…<C11>` tabular arrays and 5 `<pic>` diagrams
unprofiled; vcp `{{Lbody}}` sub-entry structure uncounted; the digitization
renders ALL numerals as ASCII, so devanāgarī vs Arabic digits in the print
are indistinguishable from the files (a scan check would be needed); vcp
source attribution is split between the `iti`-net (15 575) and ॰-tags, so
`iti`-based source ranking undercounts vcp; `dvigu` grep-uncountable in
both (swamped by `dviguRa`).

> Fable 5 (`claude-fable-5`) · 17-08-2026 · H2983. Census scripts
> (entry parser + device counter + specimen prober) in the session
> scratchpad, throwaway; recipe: parse `<L>…<LEND>`, join EOL-hyphen wraps
> (keep `--`), count per pattern; ≥25 entries read in full per kośa across
> the alphabet (skd L1–L39675, vcp L2–L46294). §565 takes the next number.

### §565. Prosody marks (breve/macron) appear in 27 dictionaries; 11 show collision risk with seam notation

🟡 **Concludes the §553–§561 compound-marker census series (H2986).** Measured
over [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
— the mw72 preface explicitly names breve `˘` and macron `—` as quantity marks
for meter. Census counts breve (U+02DA ˘) and macron/em-dash (U+2014 —) across
all dictionaries:

| Measurement | Count | Major dictionaries |
|---|---|---|
| **Breve marks** | 27 dicts | AP (5150), AP90 (4051), MW (53357), MWS (22179), PWG (83398), PW (23706), SCH (15193), BHS (22103), STÉ (24754), CAE (9848), CCS (6664) |
| **Macron marks** | 25 dicts | PWG (97747), PW (144758), MW (257107), MWS (60513), GRA (14938), PWKVN (1160), MD (5872) |
| **Collision risk** | 11 dicts | MW, MWS, PW, PWG, SCH, BHS, CAE, CCS, MD, INM, PWKVN |

**Three notes.** (1) **Collision risk is real but non-trivial.** MW's 257,107
em-dashes are seam notation (`agni—hotra`, §555), not quantity marks — yet MW
also carries 53,357 breve marks for true prosody usage. A parser must not
conflate the two: em-dash signals compound structure (MW-unique notation), breve
signals quantity (meter/prosody). In AP90/CAE/CCS, both marks coexist but serve
different roles (ring abbreviation vs prosody). (2) **Breve distribution is
skewed toward Apte-family dicts.** AP, AP90, and CAE/CCS (Böhtlingk minor
redactions) dominate breve usage; PW and PWG also carry substantial counts. The
major Western-notation dicts (GRA, PWK, MD) mark quantity primarily via
macron, not breve. (3) **No mixed seam-vs-quantity collision found inline**
(checked per-line where both marks appear). The risk is at the dictionary level:
a parser reading MW must not mistake seam-notation dashes for meter marks, but
the two appear in different article regions and are separable by context
(lemma vs body, element position).

**Practical residue:** prosody marks are not a standard feature across the CDSL
canon (only 27 of 44 dicts). Do not assume inline meter notation when
normalizing headwords; check the dictionary's own markup style first. For
MW-like systems with both seam notation (em-dash) and prosody marks (breve),
**distinguish by context, not by character alone**.

> Haiku 4.5 (`claude-haiku-4-5-20251001`) · 17-08-2026 · H2986. Census
> scripts (character count + per-dict markup detection + specimen extraction)
> in the session scratchpad. Recipe: regex over `csl-orig/v02/<dict>/<dict>.txt`
> for U+02DA (breve) and U+2014 (macron/em-dash), extract 3 specimens per dict
> with line numbers; specimens: ap.txt L94 + L111 + L119 (compound ring +
> grammar abbreviation usage), mw72.txt L1638 + L1643 + L1644 (preface
> definition), ap90.txt L115 + L139 + L140 (quantity marks in lemma-suffix
> notation). Verifiability: class A (reproducible from v02 text files via regex).

### §566. `<div n=…>` is not a shared sense-hierarchy device — only PW/PWG/BOR nest senses, and PWG leaves sense 1 outside the markup in a quarter of its hierarchical entries

🔴 **The `<div n="…">` tag carries four unrelated jobs across the CDSL canon, and only three
dictionaries use it as a sense hierarchy at all. In PWG — the one dictionary whose sense order
pwg_ru actually translates — 25.2 % of hierarchical entries do not open their `<div>` run at
`1〉`, because sense 1 is printed in the head line outside any `<div>`.** A splitter that reads
`<div>` as "sense" therefore drops sense 1 and shifts every later number by one in 4,184 PWG
entries.

Measured over all 44 [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
digitizations (plus `RussianTranslation/src/koch.jsonl`, local-only, for the Kochergina row of
the ruling table). Per the §553 method: counted in each dictionary's own markup, never from
`<k1>`.

#### 1. Two syntactic devices that must never be summed

20 of 44 dictionaries carry a `<div>` at all; the tag splits into an **open** form and a
**self-closing** form, and they are different animals:

| Form | Dicts | Meaning |
|---|---|---|
| **open** `<div n="K">`, no `</div>` | pw · pwg · bor · gra · cae · wil · bop · gst · inm · krm · mci (11) | block opener; `n` is a level **or** a type |
| **self-closing** `<div n="K"/>` | mw · mw72 · fri · lan · pe · pgn · pui · snp · vei (9) | line break / segment marker — **never** a hierarchy |
| none at all | the remaining 24 (ap, ap90, md, mwe, sch, shs, skd, vcp, yat, …) | — |

Only **bor** ever emits `</div>` (71,019 open / 71,019 close) — and its levels are types
(`I` Roman section, `xs`/`xe` quotation start/end), depth 1. So even the one dictionary with
well-formed nesting does not nest *senses*.

#### 2. `n` is a level in three dictionaries and a type in the other seventeen

Numeric `n` — a real sense level — exists only in **pw, pwg, bor**. Everywhere else `n` is a
category tag: `to` (11,000 in mw = "to X" root-gloss line), `vp` (3,792 = verb prefix), `TS`
(34,044 in gra = *Textstellen*), `NI`, `P`, `pfx`, `H`, `Pf`, `W`. Even inside pw/pwg the tag
is multiplexed across four axes — sense level (numeric), preverb block `p`, morphological
derivative `m` (Caus./Desid.), etymological note `v` (`Vgl.`), `conj`:

| Dict | `<div>` total | numeric (= sense) | non-numeric (= other axis) | non-numeric share |
|---|---:|---:|---:|---:|
| **pwg** | 100,080 | 76,183 | 23,897 (`v` 14,624 · `p` 9,198 · `conj` 67 · 8 stray) | **23.9 %** |
| **pw** | 131,443 | 120,346 | 11,097 (`p` 8,438 · `m` 2,641 · `o` 18) | **8.4 %** |

Counting `<div>` as "senses" therefore over-counts PWG by nearly a quarter.

#### 3. Depth profile — per-entry maximum numeric level

| Dict | entries | depth 0 | depth 1 | depth 2 | depth 3 | depth 4 |
|---|---:|---:|---:|---:|---:|---:|
| **pwg** | 123,366 | 103,629 (84.00 %) | 14,656 (11.88 %) | 4,750 (3.85 %) | 331 (0.27 %) | — |
| **pw** | 170,556 | 145,295 (85.19 %) | 17,627 (10.34 %) | 6,585 (3.86 %) | 1,048 (0.61 %) | 1 (0.00 %) |
| **bor** | 24,609 | 14,930 (60.67 %) | 9,679 (39.33 %) | — | — | — |

Branching, over entries that reach the level: pwg L1 mean 2.73 / median 2 / max 244; L2 mean
4.29 / max 96; L3 mean 4.26 / max 36. pw L1 mean 3.10 / max 423; L2 mean 5.00 / max 211; L3
mean 3.69 / max 45.

The printed label alphabet is strictly tiered, and the glyph is **U+3009 `〉`** (CJK right angle
bracket), *not* U+232A — a census that greps the wrong codepoint scores zero:

| level | pw | pwg |
|---|---|---|
| 1 | Arabic `1〉 2〉 3〉 …` | Arabic `1〉 …` (max label seen: 25) |
| 2 | Latin `a〉 b〉 c〉 …` | Latin `a〉 …` |
| 3 | Greek `α〉 β〉 γ〉 …` | Greek `α〉 …` |
| 4 | Roman `I〉 II〉` (one entry, [pw.txt:491989](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L491989)) | — |

#### 4. The finding that bites: PWG's unmarked sense 1

| Measure | pwg | pw |
|---|---:|---:|
| entries with at least one level-1 `<div>` | 19,455 | 25,260 |
| first level-1 `<div>` labelled `1〉` | 14,561 (**74.8 %**) | 25,251 (**99.96 %**) |
| first `<div>` labelled `2〉` or higher | 4,894 (**25.2 %**) | 9 (0.04 %) |
| …of those, `1〉` present in the head line | 4,184 (85.5 %) | 0 |
| level-2 `<div>` with no level-1 sibling in the entry | 2,334 / 21,740 (**10.7 %**) | 2 / 38,148 (0.005 %) |
| first level-1 `<div>` carrying a *level-2* label (`2〉a`, `3〉b`) | 400 entries | 0 |

**PW regularised what PWG left typographic.** Böhtlingk's shorter recension opens essentially
every hierarchical article at `1〉`; the *Großes Petersburger Wörterbuch* prints sense 1 in the
head line, unmarked, and starts the `<div>` run at `2〉`. The nine PW exceptions are not the
same phenomenon at all — they are cross-references *into another article's* numbering
([pw.txt:8171](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L8171):
`atIvAda = ativAda` … `— 3〉`, i.e. "sense 3 of *ativāda*"), which is a second, independent trap
for a sense-splitter.

#### 5. What the flat dictionaries use instead

| Dict | device | coverage | depth |
|---|---|---:|---:|
| **ap** (Apte 1957) | `∙²N` sense · `∙³({%a%})` subsense | 25,752 / 90,843 entries (28.3 %); 91,503 + 1,186 markers | 2 |
| **ap90** (Apte 1890) | `{N}` | 1,461 / 34,882 entries (**4.2 %**); 12,539 markers | 1 |
| **gra** (Grassmann) | senses numbered `1〉 2〉` **inline in the prose**; `<div n="TS">` indexes the *inflected form* and back-references those numbers | 43,390 `〉` labels; 34,044 TS divs | 1 (inverted axis) |
| **fri** | `<div n="1"/>` + plain digit — a **language** switch (cs/ru/en), not a sense | 23,013 | 0 |
| **lan** | `<div n="2"/>{@—N.@}` | 2,031 numbers, max 12 | 1 |
| **koch** (Kochergina, local-only) | `N)` inside the gloss string | 11,061 / 29,177 entries (37.9 %), mean 2.88, max 21 | **1** — no lettered sublevel exists |
| **skd · vcp** and 22 others | none | 0 | 0 — sense order is pure text order |

Grassmann is the sharp case: he has the richest sense numbering of the Vedic dictionaries and
it is *invisible to any `<div>`-based reader*, because his `<div>` axis is form, not sense
([gra.txt:10–17](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/gra/gra.txt#L10)).

#### 6. Ruling — which sense orders may enter a pwg_ru card

[§18](#18-vedic-citation-density-separates-the-dictionary-traditions) already forbade importing
Apte's and Kochergina's sense order on *principle* (their order is logical-pedagogical, not
etymological-genetic — Vedic-citation density 2.3 % and 0 % against PWG's 23.4 %). This pass
adds the *structural* half, and the two agree:

| Source | May its sense ORDER enter a pwg_ru card? | Why |
|---|---|---|
| **PWG** | **Yes — it is the source** | but only through a parser that treats the head line as sense 1 whenever the first `<div n="1">` is labelled `2〉` or higher (4,184 entries), and that ignores the 23.9 % non-numeric `<div>`s |
| **PW** | **Cross-check only** | same tradition, same `1〉/a〉/α〉` alphabet, but PW is Böhtlingk's *re-ordering* of PWG; using it as the order silently substitutes the shorter recension's judgement |
| **MW / MWS** | **No** | carries no numeric `<div>` at all (self-closing `to`/`vp`, 1.5 % of entries). Any "MW sense order" is reconstructed from prose punctuation — a derived artefact, and §557's no-source rule applies |
| **AP / AP90** | **Never** | §18 principle *and* structure: AP's 2-level device reaches 28.3 % of entries, AP90's single level 4.2 % — there is no comparable ordering to import |
| **GRA** | **No — evidence only** | order is Vedic-attestation-driven and lives in prose; the `<div>` axis is form. Import senses as *witnesses*, never as sequence |
| **Kochergina** | **Never** | §18 (0 % Vedic) *and* structure: a single flat level, no subsenses at all — it cannot express PWG's `a〉/α〉` tiers |
| **BOR · FRI · LAN · PE · PUI · CAE · WIL · …** | **Nothing to import** | no sense hierarchy exists in the markup |
| **SKD · VCP** | **No** | §19/§564 — zero Western markup; sequence is the kośa's śloka order, not semantic |

**Practical residue.** (1) The only importable sense order is PWG's own. (2) Any pwg_ru
sense-splitter must be tested against an entry whose first `<div n="1">` is labelled `2〉` —
[pwg.txt:181–184](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L181)
(`2. a/Msa`, sense 1 `Schulter` in the head line) is the canonical fixture. (3) Never count
`<div>` to estimate polysemy: 84 % of PWG entries have no numeric `<div>` at all, and a quarter
of the tags that do exist are preverb/etymology blocks. (4) Grep the label with **U+3009**, not
U+232A.

**Specimens** (file:line in [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)):
[pwg.txt:181–184](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L181) entry opens at `2〉` ·
[pwg.txt:612–615](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L612) `a/kUpAra`, head-line `1〉` then `2〉` then `a〉` ·
[pwg.txt:1019–1022](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L1019) depth-3 `α〉 β〉 γ〉 δ〉` ·
[pwg.txt:9](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L9) orphan level-2 `a〉` with no level-1 above it ·
[pwg.txt:54](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L54) `<div n="v">` = etymological `Vgl.`, not a sense ·
[pwg.txt:218](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L218) `<div n="p">` = preverb `vi` block ·
[pw.txt:491989](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L491989) the only depth-4 entry (`I〉/II〉`) ·
[pw.txt:190](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L190) `<div n="m">` = `Caus.`/`Desid.` derivative ·
[pw.txt:8171](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L8171) `— 3〉` pointing into *another* article ·
[mw.txt:366](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L366) self-closing `<div n="to"/>` root-gloss line ·
[fri.txt:15–17](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/fri/fri.txt#L15) `<div n="1"/>` = cs/ru/en language switch ·
[lan.txt:55](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/lan/lan.txt#L55) `{@—1.@}` bold sense number ·
[ap.txt:8](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L8) `∙²1` and
[ap.txt:31](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L31) `∙³({%a%})` ·
[ap90.txt:207](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt#L207) `{1}` ·
[bor.txt:88](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/bor/bor.txt#L88) the only real `</div></div>` nesting ·
[gra.txt:12–13](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/gra/gra.txt#L12) `<div n="TS">` back-referencing inline sense numbers.

> Opus 5 (`claude-opus-5`) · 18-08-2026 · H2980. Census scripts (throwaway, session
> scratchpad): per-dict `<div>` inventory splitting `<div n="K">` from `<div n="K"/>`;
> per-entry max numeric level between `<L>` and `<LEND>`; first-level-1-label extraction using
> the U+3009 `〉` glyph; orphan-level detection; `∙²`/`∙³`, `{N}` and `N)` device counts.
> Recipe: regex over `csl-orig/v02/<dict>/<dict>.txt` — `<div n="([^"]*)"/?>`, entry frames on
> `^<L>` / `^<LEND>`, label as the 1–4 non-space characters before U+3009 immediately after the
> opening tag with a leading U+2014 stripped. Verifiability: class A (fully reproducible from
> the v02 text files; the koch row needs the local-only `koch.jsonl`).

### §567. The memo's `<ls>L.</ls>` "lexicographers-only" marker does not exist in PWG — the real signal is `renou_register.py`'s own `ls`/`dcs` provenance tag

🔴 **A literal search of `csl-orig/v02/pwg/pwg.txt` for the exact string `<ls>L.</ls>` returns
0 hits.** The only 5 `<ls>L. …</ls>` matches are a manuscript siglum (`L. JĀT. 13,1`, etc.),
unrelated to lexicography. "L." is heavily overloaded in PWG's own `<ab>` abbreviation table —
Landessprache, Lebensstadium, Logik, Loblieder, Lärm — never "Lexicographen" (which appears 267
times as free prose, "Die indischen Lexicographen …", never as a short tag). A future session
asked to extract "the L. marker" from PWG source will find nothing and should not invent a
regex to force a match.

The actual "lexicographers-only-citation" signal that already exists in committed data is the
`ls`/`dcs` **provenance** tag `renou_register.py`/`renou_glossary.py` computes per Renou state
(`src/pwg.renou.jsonl`, `renou_provenance` field: `ls` = the state is warranted only by another
lexicographer's citation, `dcs` = corpus-attested). Operationalised as `ls_only` (≥1 state `ls`,
0 states `dcs`) for [H2856](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2856-Sonnet_SanskritLexicography_ghost-headword-census-translation-drift-survival_15.08.26.md):
**42,357 / 106,082 (39.9 %)** of PWG headwords are `ls_only`, and carry **2.36×** the odds
(95 % CI [2.28, 2.45], IRLS logistic, n=106,082) of being corpus-absent (exact-match against
`src/corpus_lexicon.jsonl`) versus a headword with at least one corpus-attested state.

> Sonnet 5 (`claude-sonnet-5`) · 18-08-2026 · H2856. Full census + model:
> [`RussianTranslation/research/H2856_E4_GHOST_HEADWORD_CENSUS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/H2856_E4_GHOST_HEADWORD_CENSUS.md).
> Verifiability: class B — the driver (`src/h2856_e4_ghost_census.py`) is committed and
> reproducible, but two of its four inputs (`src/corpus_lexicon.jsonl`, `src/pwg.renou.jsonl`)
> are gitignored, local-only stores.

### §568. Renou diachronic state V is never populated in `pwg_sense_stratum.jsonl`

📊 **`renou.py`'s canonical `STATES` tuple is `(I, II, III, IV, V)`, but 0 of 64,296 per-sense
rows in `RussianTranslation/src/pwg_sense_stratum.jsonl` ever carry `renou_oldest` or
`renou_youngest` == `"V"`** — every dated span tops out at IV. A consumer that assumes all five
canonical states are populated everywhere (e.g. a diachronic figure that reserves a 5th "V" x-axis
tick) will silently render an always-empty band. Found while building the
[H2856](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2856-Sonnet_SanskritLexicography_ghost-headword-census-translation-drift-survival_15.08.26.md)
V6 sense-survival streamgraph — chart I–IV only for this specific artifact; do not assume the
same holds for other `*.renou.jsonl`/`*_stratum.jsonl` files without re-checking (`pwg.renou.jsonl`
DOES use `V`, e.g. its `renou_dcs`/`renou_provenance` fields — this is a property of the
per-*sense*-stratum build specifically, not of the Renou state system in general).

> Sonnet 5 (`claude-sonnet-5`) · 18-08-2026 · H2856. Streamgraph + counts:
> [`RussianTranslation/research/H2856_V6_SENSE_SURVIVAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/H2856_V6_SENSE_SURVIVAL.md).
> Recipe: scan every sense's `renou_oldest`/`renou_youngest` for the literal string `"V"` —
> zero hits. Verifiability: class B (driver committed; input `pwg_sense_stratum.jsonl` is a
> gitignored, local-only store).

### §569. A bracketed `[Gen, unsp]` domain/period tag collides on the letters "Gen" with the genitive-case abbreviation — needs the same masking discipline as `{#…#}` Sanskrit spans

📊 **`pwg_ru_translated.jsonl`'s `ru` field carries TWO independent short-tag taxonomies that
share a letter sequence.** Grammatical-category case markers (`Gen`, `Dat`, `Abl`, …, per
[ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
Bucket B) sit in plain parenthetical usage notes and inside `<ab>` tags. Separately, an
MW-style bracketed period/genre tag list — `[Ved, unsp]`, `[Buddh, Phil]`, `[Jin]`, `[Reg]`,
`[Tan]`, `[Epigr]`, and **`[Gen, unsp]`** — uses `Gen` to mean *"General"* (a text-period
label), never genitive case. A naive `\bGen\b` sweep matched **38** of these domain-tag `Gen`
occurrences alongside the 173 genuine genitive-case ones, and — because both convert to the
identical-looking `Gen.` — the collision is invisible after the fact; only distinguishable by
excluding it *during* the sweep. Detection rule that worked: a token is a domain tag (skip it)
when it sits inside a bracket span containing **only** bare Latin tag words joined by `,`/`:`
— `\[(?:[A-Za-z]+\.?)(?:\s*[:,]\s*[A-Za-z]+\.?)*\]` — never Cyrillic, parens, or `=`. A future
sweep of this or a similarly-sourced MW-format store should mask this bracket class the same
way `{#…#}`/`{%…%}` Sanskrit spans are already masked, not just check the surrounding tag.

> Sonnet 5 (`claude-sonnet-5`) · 19-08-2026 · H2849. Sweep write-up:
> [`RussianTranslation/ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
> §"German case-abbreviation compliance sweep". Verifiability: class B (driver not committed —
> a one-off scratch sweep script — but the excluded/included counts and the 40-row eyeball
> sample are recorded in the doc; input is a gitignored, local-only store).

### §570. Renaming a stored abbreviation stem (`Instr.`→`Ins.`) silently breaks tooltip lookup against an external authoritative table still keyed on the old stem

📊 **A render-time tooltip resolver that looks the STORED token up in an external ground-truth
table breaks silently, not loudly, when an editorial rename changes the stored token but not
the table.** `pilot/build_article_site.py`'s `_ab_display()` calls `pwg_ab.resolve(tok)` with
whatever string sits inside the RU column's own `<ab>` tag; `pwg_ab.py`'s table is sourced from
[`csl-pywork/v02/distinctfiles/pwg/pywork/pwgab/pwgab_input.txt`](https://github.com/sanskrit-lexicon/csl-pywork/blob/main/v02/distinctfiles/pwg/pywork/pwgab/pwgab_input.txt)
— PWG's own authoritative print-abbreviation list, out of this repo's control, keyed `Instr.`
for the instrumental case. When [H2849](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2849-Sonnet_SanskritLexicography_german-case-abbreviations-to-latin-compliance-sweep_15.08.26.md)
renamed the RU-column token from `Instr.` to `Ins.` (per a newer review instruction), every one
of the 261 affected `<ab>Ins.</ab>` tags would have silently lost its tooltip — `resolve()`
returns `None` on a miss, no exception, no test failure, nothing renders visibly wrong except a
missing `title=` attribute a human would have to hover to notice. Fixed with a one-entry alias
(`RENAME_ALIASES = {'Ins.': 'Instr.'}` in `resolve()`), not by touching the external table.
**General lesson:** before any editorial rename of a token that also serves as a lookup key
into an external/upstream table, grep that table for the OLD key first — a clean data sweep and
a clean render-time regression are not the same verification.

> Sonnet 5 (`claude-sonnet-5`) · 19-08-2026 · H2849. Fix:
> [`RussianTranslation/src/pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py)
> `resolve()`. Verified: `python src/pwg_ab.py lookup "Ins."` resolves to the same
> `Instrumental / instrumental (case)` expansion as `lookup "Instr."`. Verifiability: class A
> (driver committed, reproducible, no gitignored input required for this specific check).

### §571. The compound-position ring is not an inferred convention — Cappeller PRINTS its definition in 1887, six years before Macdonell; the whole §553–§566 census had never opened a preface

📊 **A typographic census built only from digitized markup can measure a sign perfectly and
still miss that its author defined it in words.** FINDINGS §553–§558 / §561 / §564–§566 and the
consolidated
[`docs/COMPOUND_MARKER_TYPOGRAPHY_CENSUS_CDSL_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/COMPOUND_MARKER_TYPOGRAPHY_CENSUS_CDSL_2026.md)
were derived entirely by counting U+02DA / U+00B0 / U+0970 / seam characters inside
[`csl-orig/v02`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02) `<k2>` and bodies.
Zero preface citations (`grep -c 'pref' ` on the census doc = 0) — even though the org has OCRed
Cologne front matter for **33 dictionary codes** under `GitHub/*/prefaces/` via
[`/cologne-preface-ocr`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-preface-ocr.md).
Two of those prefaces state the compound convention outright:

- **CCS**, Vorrede, Jena, 3 July 1887 —
  [`ccspref05.md`](https://github.com/sanskrit-lexicon/CCS/blob/master/prefaces/ccspref05.md):
  «Das Zeichen ○ geht immer auf das Stichwort oder einen sich von selbst verstehenden Teil
  desselben; ○— und —○ bedeuten also resp. das Stichwort am Anfang oder am Ende eines
  Compositums (wobei auch die Verbindung eines Verbums mit einer Präposition als solches gilt).»
- **CAE**, "Symbols", 1891 —
  [`caepref06.md`](https://github.com/sanskrit-lexicon/CAE/blob/master/prefaces/caepref06.md):
  «◦— the principal word of an article to be supplied at the beginning of a compound. / —◦ the
  same supplied at the end of a compound.»

Three consequences. **(1) Priority.** §558 called Macdonell's `˚—` / `—˚` (409 / 4 258) "the
closest historical precedent" for a positional marker; Cappeller prints the identical device in
1887 (German) and 1891 (English), and Macdonell's dictionary is 1893. Macdonell is the largest
attestation, not the first. **(2) Convention vs usage.** §553–554 described Cappeller as
"leading-only in practice" — accurate as a count, wrong as a description of the system: he
declares both positions, distinguished by which side the em-dash falls on, exactly as the pwg_ru
[h2805_q3_deploy](https://gasyoun.github.io/vote/sheets/h2805_q3_deploy.html) cards propose.
**(3) Glyph variance goes down to the front matter.** The same printed circle is OCRed `○`
U+25CB in ccspref05 and `◦` U+25E6 in caepref06 — one more reason the digitization glyph
(U+02DA vs U+00B0 vs U+0970) is an encoding artefact and not evidence about the printed sort.

Negative result worth keeping: **PWG's own Vorrede does not define the ring.** Its preface pages
only *use* `॰` in errata (pwgpref13–14, "streiche das Zeichen ॰"). So §4-1's finding that the PWG
ring means truncation ~¾ of the time genuinely had to be counted — there was nothing to read.
Same for KRM (pref02/24, `॰` inside Sanskrit name abbreviations) and GST (pref06, errata).

**General lesson:** before a distributional census of any printed convention, grep the OCRed
front matter for the glyph. It costs one `grep -rl` over `GitHub/*/prefaces/` and can replace an
inference with a quotation — or prove, as with PWG, that no quotation exists.

> Opus 5 (`claude-opus-5`) · 19-08-2026 · H3143. Method:
> `grep -rl -e '˚' -e '○' -e '॰' -e '∘' --include=*.md */prefaces/ prefaces_*/` over the local
> clones — 5 codes hit (CCS, CAE, PWG, KRM, GST), of which 2 define the sign. Coverage census of
> `*/prefaces/` and `prefaces_*/` recorded in census §4.5. Verifiability: class A for the
> quotations (committed OCR pages with `source_url` frontmatter pointing at the Cologne scan);
> class B for the 33-code coverage count (derived from local clones, some staging dirs are not on
> any remote).

### §572. Homonym-splitting density spans 0 to 419 per 1 000 entries across the 44 dicts — general dictionaries cluster at 20–65, name-indices at 89–419, and 22 dicts split none; `<hom>` inline markers over-count `<h>` metadata by up to 3.6×

🟢 **Eighth entry of the §553–§571 compound/typography census series; census item
§5.2 (H2979).** `<h>` is a per-entry meta-line tag (`<L>…<k1>…<k2>…<h>N`) present
only on entries that are one of a numbered set sharing a headword — it is the
authoritative "this entry is a homonym split" signal. `<hom>N.</hom>` is a
separate inline body-text tag that prints the number; MW's own schema doc
(`mw-meta2.txt:89-94`) states it "also appears in cross-references," so `<hom>`
counts run higher than `<h>` counts wherever cross-refs cite split entries —
confirmed: pwg `<h>`=6,499 vs `<hom>`=23,438 (3.6×), pw `<h>`=8,012 vs
`<hom>`=10,052 (1.25×), mw `<h>`=5,738 vs `<hom>`=11,517 (2.0×). **Counting
`<hom>` as "how many entries are split" over-counts by that factor; `<h>` is
the entry-level denominator.**

Counted over all 44 `v02/*/​*.txt` data files (excluding `*-meta*`/`*hwextra*`
schema/appendix files, which contaminate raw grep counts — e.g. `ae`, `ben`,
`ieg`, `krm`, `mwe`, `pgn`, `snp`, `bor` show a spurious `<h>`=1 each, entirely
from the tag-schema documentation line `<L>,<e>,<h>,<k1>,<k2>,<pc>,<LEND>` in
their `*-meta2.txt`, not from any real split — the §557 Mylius rule bites on
`grep` output too, not only on prose claims):

| Class | Dicts (n) | `<h>` density /1 000 entries | Examples |
|---|---|---|---|
| Splits, prints inline `<hom>N.` | 8 | 0.1–52.7 | mw 20.0, pw 47.0, pwg 52.7, gra 39.3, md 44.3, bhs 5.3, pwkvn 36.7, ap 0.1 |
| Splits (`<h>` present), no inline `<hom>` display | 14 | 0.3–419.0 | pui 419.0, inm 339.9, pe 330.7, lrv 150.9, mci 120.7, bop 88.5, vei 81.9, mw72 66.0, cae 63.9, ccs 59.9, lan 42.3, gra-adjacent gst 3.7, ap90 0.3, stc 46.8 |
| No splitting at all (`<h>`=0 everywhere) | 22 | 0 | abch, acc, acph, acsj, ae, armh, ben, bor, bur, fri, ieg, krm, mwe, nmmb, pgn, sch, shs, skd, snp, vcp, wil, yat |

8 + 14 + 22 = 44. **The class-2/class-3 split is not "some dicts split more,
some less" — it is genre.** pui (Purāṇa Index), inm (Index to the Names in the
Mahābhārata), pe (Puranic Encyclopedia), mci (Mahābhārata Cultural Index),
lrv, bop are name-indices, not sense-dictionaries: their high density (89–419
per 1 000, i.e. up to 42 % of entries) reflects many *distinct persons*
sharing one name, not polysemy. General dictionaries (mw/pw/pwg/gra/md/bhs)
cluster an order of magnitude lower (5–53 per 1 000). Mixing the two classes
in one "homonym density" ranking would misread genre difference as
lexicographic-policy difference. skd/vcp (Sanskrit-Sanskrit kośas, §564) and
wil (Wilson) split zero — consistent with §564's finding that they encode
sense structure through the vigraha/quotation apparatus, not through the
homonym-number device at all.

**Specimen: `agnihotra` — the exact cross-dictionary-join case the handoff
named.** mw/pw/pwg/md/cae/ccs split it into `<h>1` (mfn., "sacrificing to
Agni," `<s1>Agni</s1>`) and `<h>2` (n., "oblation to Agni") — six
independently-digitized editions agree on the n./adj. split:
- [mw/mw.txt:4137](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L4137) `<hom>1.</hom> agni/—hotra ¦ mfn. … sacrificing to Agni`
- [mw/mw.txt:4146](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L4146) `<hom>2.</hom> agni—hotra/ ¦ n., … oblation to Agni`
- [pwg/pwg.txt:2413](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L2413) / [:2421](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt#L2421) — `<h>1` / `<h>2`
- [pw/pw.txt:2563](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L2563) / [:2568](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pw/pw.txt#L2568) — `<h>1` / `<h>2`
- [md/md.txt:1147](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/md/md.txt#L1147) / [:1151](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/md/md.txt#L1151) — `<h>1` / `<h>2`
- [cae/cae.txt:770](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/cae/cae.txt#L770) / [:773](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/cae/cae.txt#L773) — `<h>1` / `<h>2`, no inline `<hom>` (class 2)
- [ccs/ccs.txt:656](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ccs/ccs.txt#L656) / [:660](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ccs/ccs.txt#L660) — same

### §573. The leading hyphen has two senses, but no dictionary marks which — Wilson is 100 % inflectional, Macdonell is 83 % compound-member/2 % inflectional/15 % a third (taddhita) class the two-way split cannot hold

🟢 **Ninth entry of the §553–§572 compound/typography census series; census
item §5.8 (H2985).** The leading hyphen (`{#-X#}` / `{@-X@}` / `<s>-X</s>`
depending on dict) reads as EITHER "this abbreviates a compound's second
member" OR "this abbreviates an inflected/derived form of the SAME headword" —
and the two readings require opposite expansion rules (join to a NEW headword
vs join to the SAME headword). No dict marks which sense is meant; it must be
inferred from what follows the hyphen run.

**Wilson (wil.txt, `{#-X#}` markup) is unambiguously the inflection pole.**
49,487 leading-hyphen occurrences total; 48,878 (98.8 %) sit inside a
`(…)` immediately after a bare `<lex>` gender/number tag with no gloss of
their own — a declension-paradigm listing, not a second compound member:
[wil/wil.txt:48](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L48)
`<lex>m.</lex> ({#-kaH#})`,
[wil/wil.txt:2399](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L2399)
`<ab>nom.</ab> ({#-tA#})`,
[wil/wil.txt:4299](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L4299)
`{%Adverbial.%} ({#-sraM#})`. The remaining 609 (1.2 %) miss the regex only
because an intervening `<ab>`/`<lex>` abbreviation sits between hyphen and
gloss — reading the specimens confirms every one is still a paradigm form of
the SAME headword (`<ab>fem.</ab> {#-KI#}`, `<ab>pl.</ab> {#-ttAH#}`). **0 of
49,487 read as a compound second member.** Śabdasāgara (shs.txt) inherits the
identical convention verbatim (
[shs/shs.txt:22](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/shs/shs.txt#L22)
`m. ({#-SaH#})`), confirming this is Wilson's device, not shs's own.

**Macdonell (md.txt, `{@-X@}` markup) is the opposite case: the SAME device
covers three distinct morphological classes, and only 83 % of them are
compound members.** Of 32,177 `{@-X,@}` runs: **608 (1.9 %)** are `X` drawn
from a closed set of case/adverb suffixes (`-tas`, `-m`, `-ena`, `-e`, `-āt`
…) immediately tagged `<lex>ad.</lex>` or a bare case abbreviation
(`<ab>in./ab./lc./ac.</ab>`) with NO independent gloss beyond the case sense —
these are inflected/derived ADVERBS of the same headword:
[md/md.txt:312](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/md/md.txt#L312)
`a-kārya … misdeed: {@-tas,@} <lex>ad.</lex> by doing wrong`. **26,690
(82.9 %)** are `X` tagged with a full `<lex>m./f./n./a.</lex>` and an
INDEPENDENT gloss unrelated to case — true compound second members:
[md/md.txt:840](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/md/md.txt#L840)
`akṣauhiṇī … {@-pati,@} <lex>m.</lex> lord of an army, general` (=
akṣauhiṇī-pati, a new two-member compound headword). **4,879 (15.2 %) are
NEITHER** — taddhita/derivational suffixes (`-tā`, `-tva`, `-ka`, `-ya`,
`-ita`, `-vat`, `-maya` …) that derive a new abstract noun or adjective STEM
from the headword, e.g.
[md/md.txt:2880](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/md/md.txt#L2880)
`{@-tā,@} <lex>f.</lex> <ab>abst. ɴ.</ab>` — grammatically tagged as a noun
with its own gloss (so the compound-member rule over-classifies these; they
pass the mechanical test above but are a third class the census flags as
residue, not silently folded into "compound"). The `<ab>˚—</ab>` ring+dash
marker (§558, "as prior member of a compound") and the leading-hyphen run are
DIFFERENT devices printed side by side —
[md/md.txt:324](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/md/md.txt#L324)
`a-kāla … <ab>˚—</ab>, {@-tas,@} <ab>lc.</ab> unseasonably` uses `˚—` for
"used as compound-prior-member" and `-tas` for the case-suffixed adverb, in
the same entry, meaning different things.

**Whitney is two different devices under one name (extends §561).** *Roots
1885* (Deriv. columns, read from
[csl-whitroot/jpg/whit-023-kft2.jpg](https://github.com/sanskrit-lexicon/csl-whitroot/blob/master/jpg/whit-023-kft2.jpg)):
leading hyphen marks a stem attested ONLY as a compound's final member
(`-kartin c.`, `-karttṛ E.+`) — pure compound-member, no inflectional use
found in this column (§561). *Grammar* (
[WhitneyRoots/src/wg_text.txt](https://github.com/gasyoun/WhitneyRoots/blob/main/src/wg_text.txt))
splits again: L4050/L18955 `-arthe or -kṛte` (§1116) cite an adverbially-used
LOCATIVE case form — inflection — while
[wg_text.txt:23245](https://github.com/gasyoun/WhitneyRoots/blob/main/src/wg_text.txt#L23245)
`-kṛt, see 1105.` is an index cross-reference to a kṛt-suffix derivative
class — closer to the compound/derivational-suffix reading than to case
inflection.

**Disambiguation rule for an expansion pass (the deliverable):**
1. Leading hyphen inside a parenthetical directly after a bare `<lex>`
   gender/number tag, with no gloss of its own → **inflection** (paradigm
   form of the SAME headword). Wilson/shs pattern.
2. Leading hyphen where `X` is a closed-class case/adverb suffix (`-tas`,
   `-m`, `-ena`, `-e`, `-āt`, `-bhis` …) followed by an adverb/case
   abbreviation tag and NO independent gloss → **inflection** (case-derived
   adverb of the SAME headword). MD/Whitney-Grammar `-arthe`/`-kṛte` pattern.
3. Leading hyphen where `X` is followed by a full part-of-speech tag AND an
   independent gloss naming a different concept than the headword →
   **compound second member** — expand to a NEW join headword
   (`{headword}{X}`). MD `-pati` / Whitney-Roots `-kartin` pattern.
4. Taddhita/derivational suffixes (`-tā`, `-tva`, `-ka`, `-ya`, `-ita`,
   `-vat`, `-maya` …) satisfy rule 3's surface test (full POS tag + gloss)
   but name neither a compound nor a case form — **flag as a third class**
   and do not auto-expand into either bucket without a human check; ≈15 % of
   MD's inventory falls here and the fraction is unmeasured for other dicts.

**Breadth (unclassified this pass — named, not counted into the rule
above):** the same ambiguity is present, at larger raw counts, in dicts this
item did not name: ap `{#-#}`=48,726; ap90 `{#-#}`=36,060 + `{@-@}`=53,697;
shs `{#-#}`=52,406 (confirmed Wilson-pattern); mwe `{#-#}`=16,997; gst
`{#-#}`=7,519; mw `<s>-</s>`=18,242 — and MW's own convention diverges from
its Wilson ancestor: [mw/mw.txt:1572](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt#L1572)
`(<ab>cf.</ab> <s>-karRa</s>, <s>-BA</s>, <s>-BAga</s>)` is a compound-member
cross-reference list, not a declension paradigm. A future pass must re-run
rules 1–4 per dict before trusting any cross-dict aggregate.

> Sonnet 5 (`claude-sonnet-5`) · 19-08-2026 · regex counts over
> [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
> `wil/wil.txt` (`{#-[^#]*#}`, tail-context match on `<lex>` gender tags) and
> `md/md.txt` (`{@-[^@]*@}`, tail-context match on case-abbreviation vs
> noun/adj tags against a closed case-suffix set); Whitney read from
> [WhitneyRoots/src/wg_text.txt](https://github.com/gasyoun/WhitneyRoots/blob/main/src/wg_text.txt)
> line grep plus the §561 scan-read of Roots 1885. Breadth table: raw
> occurrence counts only, not classified. Verifiability: class A for wil/md/mw
> specimens (reproducible from the public csl-orig checkout); the Roots 1885
> compound-member claim is class B (scan-read, not machine-countable, carried
> from §561).

Three dictionaries keep it **one entry**, no `<h>` at all:
[ap/ap.txt:4560](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap/ap.txt#L4560),
[vcp/vcp.txt:2769](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp.txt#L2769),
[wil/wil.txt:2386](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/wil/wil.txt#L2386).
**A headword-join keyed only on `<k1>`/`<k2>` (agnihotra=agnihotra) is a 1:2
join against mw/pw/pwg/md/cae/ccs and a 1:1 join against ap/vcp/wil — any
matcher that assumes one row per dictionary per headword silently drops the
mfn./n. distinction on the split side, or silently merges two senses into one
row on the joined side.** This is exactly the pwg_ru / kosha headword-matcher
risk the handoff named, now with file:line proof instead of prediction.

**Specimen: numbering convention differs by dict-class.** General dicts use
Arabic `<h>1`/`<h>2`/…; the name-index pui uses Roman numerals — 5 distinct
figures named Indra get `<h>I`…`<h>V`
([pui/pui.txt:10544](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pui/pui.txt#L10544)–[:10838](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pui/pui.txt#L10838)),
and [pui/pui.txt:74](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pui/pui.txt#L74)–88
gives `akṛtavraṇa` `<h>I`–`<h>IV` (4 distinct persons). A homonym-count script
that assumes `<h>` values are always small integers will silently mis-sort or
mis-parse pui/inm-family Roman numerals.

**Residue for pwg_ru / kosha:** (1) any cross-dictionary headword join must
carry the `<h>` cardinality per side, not just the key match — a 1:N join is
not an error, it is the data; (2) `<h>` (not `<hom>`) is the correct
entry-level denominator for "how many rows does this headword occupy in dict
X"; (3) name-index dicts (pui/inm/pe/mci/lrv/bop) need a separate
"distinct-referent count," not "sense count," when their `<h>` cardinality is
used downstream — conflating the two would read Indra-I..V as five senses of
one word rather than five different gods/kings/sages named Indra.

> Sonnet 5 (`claude-sonnet-5`) · 19-08-2026 · H2979. Method: `grep -o '<h>'` /
> `grep -o '<hom'` / `grep -o '<L>'` over every `v02/<dict>/<dict>.txt` (main
> data file only, `*-meta*`/`*hwextra*` excluded) across all 44 dict codes in
> [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02);
> density = `<h>` count / `<L>` count × 1000; dict-code→title resolved via
> [SanskritLexicography/FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md).
> Verifiability: class A (every count and specimen reproducible from the
> public [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) checkout with
> the one-line `grep -o` commands above; no literature claim, per §557).

### §574. Gloss-language layering: `{%…%}` is not "German-or-English" — it also carries French (Burnouf) and editorial prose (Sircar), and the Latin `<ab>` layer is itself language-specific per dictionary

🟢 **The `{%…%}` span is the CDSL digitizers' generic "running prose / translation" wrapper, not a language-typed tag.** Measured over all 44
[csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
digitizations, per-entry (entry = one `<L>` block, language of an entry's
`{%…%}` spans scored by German- vs English-function-word majority — `ambig`
when the span carries no scored function word, e.g. a single noun phrase):

| dict | entries | %`{%…%}` | de | en | ambig | %`<ab>` |
|---|---|---|---|---|---|---|
| **bur** | 19 776 | 100.0 | 450 | 3 560 | **15 765** | 93.8 |
| ieg | 7 935 | 100.0 | 201 | 1 847 | 5 884 | 38.3 |
| mw72 | 55 390 | 100.0 | 15 345 | 22 826 | 17 216 | 0.0 |
| pgn | 485 | 100.0 | 4 | 122 | 359 | 0.0 |
| pui | 17 512 | 100.0 | 252 | 2 086 | 15 174 | 0.0 |
| sch | 29 125 | 100.0 | 291 | 4 017 | 24 817 | 0.0 |
| ben | 17 316 | 99.9 | 115 | 6 588 | 10 604 | 96.3 |
| mwe | 32 378 | 99.8 | 0 | 12 172 | 20 151 | 0.0 |
| yat | 45 206 | 99.8 | 1 | 13 683 | 31 440 | 0.0 |
| lan | 4 944 | 97.2 | 7 | 2 659 | 2 138 | 95.4 |
| bop | 8 961 | 87.7 | 24 | 1 457 | 6 376 | 0.0 |
| lrv | 53 441 | 83.1 | 0 | 9 083 | 35 345 | 0.0 |
| mci | 2 643 | 81.5 | 160 | 857 | 1 137 | 0.0 |
| ccs | 30 010 | 78.2 | 2 657 | 108 | 20 689 | 0.0 |
| gra | 12 785 | 76.4 | 2 983 | 239 | 6 546 | 85.2 |
| vei | 3 834 | 67.7 | 280 | 945 | 1 370 | 0.0 |
| **pwg** | 123 366 | 66.0 | **48 926** | 1 628 | 30 885 | 59.0 |
| **pw** | 170 556 | 64.9 | **64 289** | 1 895 | 44 546 | 33.7 |
| bhs | 17 839 | 55.2 | 27 | 5 623 | 4 206 | 85.7 |
| ap90 | 34 882 | 47.0 | 1 | 10 412 | 5 970 | 60.2 |
| md | 20 749 | 46.6 | 2 | 8 543 | 1 124 | 60.6 |
| inm | 12 647 | 45.3 | 54 | 1 298 | 4 373 | 0.0 |
| stc | 24 574 | 44.1 | 451 | 2 447 | 7 942 | 94.1 |
| pwkvn | 24 976 | 41.5 | 5 700 | 202 | 4 465 | 19.4 |
| ap | 90 843 | 34.4 | 1 | 19 406 | 11 806 | 24.0 |
| bor | 24 609 | 30.4 | 16 | 6 001 | 1 458 | 0.0 |
| wil | 44 577 | 13.2 | 19 | 545 | 5 311 | 93.4 |
| **cae** | 40 069 | **0.0** | 0 | 0 | 0 | 31.5 |
| **mw** | 286 525 | **0.0** | 0 | 0 | 0 | 38.7 |

(Remaining zero-or-near-zero-`{%…%}` dicts: gst 17.9 %, pe 6.7 %, acc 1.9 %,
krm 0.1 %, and eight with none at all — abch, acph, acsj, ae, armh, fri,
nmmb, shs, skd, vcp.)

**Three residues the task's own framing ("German/English spans") missed.**

1. **A third Western language is in scope: French.** `bur` (Burnouf's
   *Dictionnaire Classique Sanscrit-Français*, 1866) wraps its French prose in
   `{%…%}` at 100 % of entries — `bur.txt` line 2–3:
   `{#a#}¦ {%a%} 1ʳᵉ lettre de l'alphabet sanscrit, nommée {%akāra.%}`. The
   German/English word-majority heuristic correctly refuses to call this
   either language (79.7 % of its `{%…%}` entries score `ambig`, 7th-highest
   of the 25 dicts with >500 wrapped entries — a high ambig share alone is
   not proof of a third language, since ccs/pui/sch/bop score higher from
   short noun-phrase glosses under either heuristic). The confirmation is the
   digitization's own title metadata, not the classifier: **an ambig-heavy
   dict only becomes a hidden-language finding once cross-checked against
   `<title>` metadata** — verified against `burheader.xml` line 8–11
   (`<title type="key">Burnouf 1866</title>`, `<name>Burnouf,
   Émile</name>`).
2. **`{%…%}` also wraps non-gloss editorial prose.** `ieg` (Sircar's *Indian
   Epigraphical Glossary*) hits 100 % `{%…%}` coverage not because every
   entry has a translation span but because its front matter is wrapped the
   same way — `ieg.txt` line 9–10:
   `{%Carmichael Professor and Head of the Department of Ancient%}
   {%Indian History and Culture, University of Calcutta%}` (a dedication, not
   a gloss). The tag marks *any running prose distinct from the Sanskrit/
   citation/abbreviation spans*, not "translation" specifically — a parser
   that treats every `{%…%}` as a sense gloss will ingest dedications and
   colophons as word meanings.
3. **The Cappeller pair diverges on whether English gets the wrapper at
   all.** `ccs` (Cappeller's German *Sanskrit-Wörterbuch*, 1887) wraps its
   German glosses (78.2 % of entries, `ccs.txt` line 657:
   `{#agnihotra/#}¦ {%n.%} Feueropfer.`); `cae` (Cappeller's *English*
   Sanskrit-English dictionary, 1891, same lexicographer, one year earlier)
   has **zero** `{%…%}` spans anywhere in 40 069 entries — its English gloss
   is bare running text, `cae.txt` line 764–765:
   `{#agnisAt#}¦ <ab>adv.</ab> into fire; {#˚kf#} burn.` `mw` (876 976 lines,
   286 525 entries) is the same pattern at scale: zero `{%…%}`, English
   glosses printed as unwrapped text after the last `<ab>`/`<ls>` tag. The
   practical rule for a pwg_ru pivot-gloss extractor: **`{%…%}` presence is a
   per-digitization markup choice, not a property of "having a translatable
   gloss" — mw and cae must be read by extracting the tail text after the
   entry's structural tags, not by grepping `{%…%}`.**

**The `<ab>` abbreviation layer is itself language-specific, not uniformly
Latin.** `mw`'s `<ab>` stock (38.7 % of entries carry at least one) is Latin/
English lexicographic shorthand — `cf.` 11 620×, `id.` 4 401×, `q.v.` 3 542×,
`v.l.` 3 542× (`mw.txt` line 29: `<ab>cf.</ab> <s>a/-karRa</s>`). `gra`
(Grassmann, German) uses **German** abbreviations in the same tag — `d.`
("das"), `u. s. w.` ("und so weiter"), `Vgl.` ("Vergleiche") — `gra.txt`
line 11 and 19. A downstream abbreviation-expansion table keyed only on Latin
forms (`cf.`, `e.g.`, `ib.`) will silently fail on `gra`, `pwg` (59.0 %
`<ab>` coverage), and `pw` (33.7 %) — the Latin abbreviation set from §558 is
an MW/English-family fact, not a cross-dict one. 21 of 44 dicts carry no
`<ab>` tag at all (0.0 % column above), meaning their abbreviations — if any
— are inline plain text, structurally invisible to a tag-based scan.

**Russian layer: `koch` is the one source that is Russian by construction,
not by markup.**
[pwg-ru-data/corpus/koch.jsonl](https://github.com/gasyoun/pwg-ru-data/blob/main/corpus/koch.jsonl)
(Kochergina 1978/2005, digitized as flat JSONL, not TEI — no `{%…%}` markup
exists) holds 29 177 entries; **29 171 (99.98 %)** contain Cyrillic in the
`gloss` field, the 6 exceptions being bare cross-reference stubs with no
prose (e.g. `go-yajYa`: `गोयज्ञ /go-yajña/ m. /gomed_a/` — headword +
grammar tag + a pointer, no Russian sentence). 7 522 entries (25.8 %) open
with `см.` ("see") as a cross-reference marker — the Russian-tradition
equivalent of MW's `<ab>cf.</ab>`/`q.v.` and PWG's `s.`. Grammatical labels
inside the Russian gloss are still Latin-script shorthand
(`(А. pr. /ghaṭṭate/ — I fut. /ghaṭṭiṣyate/, pf. /jaghaṭṭe/, aor.
/aghaṭṭiṣṭa/, pp. /ghaṭṭita/)`, `-Gaww` entry) — Russian prose plus IAST plus
Devanāgarī plus Latin-abbreviated grammar, four scripts/languages in one
entry, none of them wrapped in a distinguishing tag the way `{%…%}` at least
attempts to for the TEI-digitized dicts.

**Router/pivot-gloss reading.** For a pwg_ru or mw_ru pivot pass: `pwg`/`pw`
are the only large sources whose German layer is both high-coverage (66.0 % /
64.9 %) and tag-delimited (`{%…%}`); `mw`/`cae` are high-coverage English but
require tail-text extraction, not tag-grepping, because neither uses
`{%…%}`; `koch` is the only Russian-native source and needs no language
classifier — every entry is Russian by construction, only the cross-ref rate
(25.8 %) needs masking before treating a `см.`-opening gloss as a sense.
`bur` is French and out of scope for a DE/EN/RU router unless a French pivot
is added.

> Sonnet 5 (`claude-sonnet-5`) · 19-08-2026 · census script over
> `csl-orig/v02/*/<dict>.txt` — per-`<L>`-entry split, `{%…%}` span extraction,
> German/English function-word majority vote (ambig when no scored word
> present), `<ab>` tag presence; koch.jsonl (Kochergina) scanned separately for
> Cyrillic coverage and `см.` cross-ref rate. Specimens quoted from pwg.txt
> L2418, ccs.txt L657, mw72.txt L44, wil.txt L958-959, bur.txt L2-3,
> burheader.xml L8-11, mw.txt L29, gra.txt L11 and L19, cae.txt L764-765,
> ieg.txt L9-10, koch.jsonl (slp1 keys `-aSrika`, `-Gaww`, `go-yajYa`).
> Verifiability: class A (every count and specimen reproducible from the
> public [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) checkout and
> the private `pwg-ru-data/corpus/koch.jsonl`; per §557, no claim made about a
> source with no measurable text).

### §575. Root citation is not "root vs 3sg present" — it's zero-grade `kf` (19/44 dicts) vs guṇa-grade `kar` (pw/pwg/pwkvn/sch), which WhitneyRoots' `roots.csv` cannot join at all; class digits fragment across four incompatible devices

🔴 **The census item's own framing ("who lemmatizes roots vs 3sg forms") does not
match what's on the page.** No dictionary in [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
lemmatizes a verb under its 3rd-singular-present form. The real split is
**which grade of the root** gets the headword: 19 of 44 dicts cite the
zero-grade root (`kf`, SLP1 for kṛ "to do"), the four PW-family dicts cite the
**guṇa-grade** root (`kar`) instead, and 3 dicts carry both as independent
headwords. Measured by grepping `√` (the root-sign glyph) and testing
`<k1>kf<` / `<k1>kar<` as literal headword keys across all 44 `<dict>.txt`
files, then reading the actual entries for the one root ("to do") common to
every dictionary that has *any* root notation at all:

| dict | `√` | class-digit device (n) | `kf` head | `kar` head | citation form |
|---|---|---|---|---|---|
| **mw** | 14,290 | `<ab>cl.</ab>` text (2,129) | 5 | 0 | zero-grade root |
| **pw** | 4,347 | none (narrative "Präsenstämme:" list instead) | 0 | 11 | guṇa-grade root |
| **pwg** | 2,083 | German ordinal + `<ab>Kl.</ab>` (6) | 0 | 15 | guṇa-grade root |
| lan | 2,376 | none | 3 | 0 | zero-grade root, no class digit at all |
| md | 1,595 | dedicated `<cl>` tag, Unicode roman numerals (750) | 2 | 0 | zero-grade root |
| gra | 916 | none | 12 | 2 | zero-grade root dominant; `kar` also an independent headword |
| fri | 504 (+31 `✓`-glyph variant) | roman numeral after `v.` (24) | 1 | 2 | zero-grade root, inline 3sg-present gloss + guṇa cross-ref |
| wil | 0 | `<ab>cl.</ab>` text, ordinal ("5th cl.") (2,055) | 1 | 0 | zero-grade root, Pāṇinian indicatory-letter form (`kfY`) |
| ap | 0 | `€N` glyph, full €1–€10 range (3,913) | 1 | 0 | zero-grade root |
| ap90 | 0 | (not separately re-measured; same lineage as ap) | 1 | 0 | zero-grade root |
| pwkvn | 0 | none | 0 | 6 | guṇa-grade (PW-derived supplement) |
| sch | 0 | none | 0 | 3 | guṇa-grade (PW-derived supplement; near-identical wording to pwkvn) |
| ccs | 0 | none | 1 | 3 | both grades attested as independent headwords |
| ben | 0 | `<ab>cl.</ab>` text (2, noise-level) | 2 | 0 | zero-grade root |
| bur | 0 | `<ab>cl.</ab>` text (2, noise-level) | 2 | 0 | zero-grade root |
| bop | 0 | none | 2 | 0 | zero-grade root |
| cae | 0 | none | 3 | 0 | zero-grade root |
| lrv | 0 | none | 2 | 0 | zero-grade root |
| mw72 | 0 | none | 3 | 0 | zero-grade root |
| shs | 0 | none | 1 | 0 | zero-grade root |
| skd | 0 | none | 3 | 0 | zero-grade root |
| stc | 0 | none | 1 | 0 | zero-grade root |
| vcp | 0 | none | 3 | 0 | zero-grade root |

(Remaining 21 dicts show zero `√`, zero class-digit device, and zero `kf`/`kar`
headword hits — no verb-root lemmatization of any kind: abch, acc, acph,
acsj, ae, armh, bhs, bor, gst, ieg, inm, krm, mci, mwe, nmmb, pe, pgn, pui,
snp, vei, yat. Several of these are the same proper-noun/name-index genre
§572 already identified splitting persons, not analyzing verbal morphology.)

**Four incompatible class-digit devices, only one machine-clean.** `mw.txt`
line 186069: `<hom>1.</hom> <s>kf</s> ¦ <lang>Ved.</lang> I) <ab>cl.</ab>
2. <ab>P.</ab>` — class as inline English abbreviation text inside prose
structure markers (`I)`/`II)`/`III)`/`IV)`), not a dedicated tag.
`md.txt` line 24759: `{#kf#}¦ <hom>1.</hom> KṚ (skṛ after upa, pari, sam),
<cl>Ⅷ.</cl> 🞄{@káro@} {%strong%}, {@kuru@} {%weak%}; <ab>V.</ab> +
<cl>Ⅰ.</cl> {@kára,@} <cl>Ⅱ.</cl> 🞄{@kár,@} <cl>Ⅴ.</cl> {@kṛṇó@}` — the
**only** dedicated `<cl>` tag in the corpus (750 occurrences total), and its
Unicode roman-numeral values (Ⅷ, Ⅰ, Ⅱ, Ⅴ) map almost directly onto
WhitneyRoots' own `class` column format (see below). `ap.txt` line 152237:
`{#kf#}¦ I. €5 <ab>U.</ab> ({#kfRoti-kfRute#}) To hurt, injure, kill.
━II. €8 <ab>U.</ab>` — a private glyph `€N` standing in for the class
number, confirmed to span the full Pāṇinian range (`€1`…`€10`, 2,083–634
occurrences each, 3,913 total) by `grep -oE "€[0-9]+" ap.txt | sort | uniq -c`.
`wil.txt` line 87225: `{#kf#}¦ <lex>r.</lex> 5th <ab>cl.</ab> ({#Y#})
{#kfY#} ({#kfRoti kfRute#})` — English ordinal prose, and the headword
itself carries a **Pāṇinian indicatory letter** (`kfY`, the dhātupāṭha
citation form, not bare `kf`) that neither mw nor md attach. `pwg.txt` line
73408: `<div n="1"> I〉 nach der 2ten <ab>Kl.</ab> <ab>praes.</ab>` — German
ordinal + `<ab>Kl.</ab>` (6 occurrences of the exact `Nten <ab>Kl.</ab>`
pattern; `pw.txt` has **zero**, describing the same four-way present-stem
split as unlabelled "Präsenstämme:" prose instead, `pw.txt` line 95653).
`fri.txt` line 10592 is the single most compact citation in the corpus:
`√kṛ karoti v. I kar` — root sign, 3sg-present gloss, roman-numeral class,
and a cross-reference to the guṇa-grade headword, all four census-item
components in one four-word line (24 occurrences of the `v. [IVX]+ ` pattern
corpus-wide, e.g. `fri.txt` line 7019: `ucchvasiti = ud + śvasiti, v. I
śvas`); `fri.txt` line 6914 additionally shows a **checkmark variant** `✓`
used interchangeably with `√` (`✓uṃd v. II ud`), 31 occurrences separate from
the 504 `√` count above.

**The PW family cites a different root grade, verified on the shared
lemma, not inferred from the header-key test alone.** `pwg.txt` line
73407: `<hom>1.</hom> √{#kar#}¦ ({#kf#} <ls>DHĀTUP. 30,10</ls>… {#kfv#}
<ls n="DHĀTUP.">15,89</ls>)` — PWG's own entry opens under `kar` and glosses
`kf` as a cross-reference *inside* that entry, i.e. this is a deliberate
citation-form choice, not a missing zero-grade entry. `pw.txt` line
95652–95653 confirms the identical choice for the larger dictionary:
`<L>24527…<k1>kar<k2>kar<h>1` / `√{#kar#} (√{#skar#})¦, Präsenstämme: {#kar#}
({#kur, kf#}), {#ka/ra, karo/, kuru#}…`. Checking `<k1>kf<` immediately
before `kar` in the pw.txt alphabetical run (line 118320–118323) confirms
`kf` is **absent** as its own headword in PW — the sort jumps straight from
`kUhA` to `kfka`, skipping the zero-grade root entirely. `pwkvn.txt` line
9509 and `sch.txt` line 30279 carry the **same** partial entry
(`{#kar#}¦ mit {#pratyapa#} {%sich rächen an%}…`) as a PW-derived
supplement, confirming both inherit the guṇa-grade citation policy from the
PW tradition rather than choosing it independently.

**The practical bite: WhitneyRoots' own `roots.csv` already joins the
zero-grade dicts and has no column for the guṇa-grade ones at all.**
[WhitneyRoots/crosswalk/roots.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv)
line 106: `106,kṛ,kf,1,I|II|V|VIII,,make,kṛtá,AV|B|C|E|RV|S|V,0,
root_1_k_r.html,40799,1,1|2|6,…,54148,11373,…` — `root_slp1` is `kf`
(zero-grade, confirming `mw_id` 54148 is exactly the `<L>54148` line found
above for MW's own `kf` entry, and `apte_id` 11373 likewise resolves against
ap's `€`-glyph entry). The header row —
`whitney_no,root_iast,root_slp1,homonym,class,class_uncertain,gloss_short,
ppp,period_tags,grouped,warnemyr_url,dcs_freq,dcs_rank,dcs_class_tag,
attested_forms,mw_id,apte_id,senses,section_refs` — has **no `pw_id` or
`pwg_id` field at all** (`grep -in "pw" <header>` returns nothing). Cologne's
two largest and most authoritative dictionaries (pw 643,112 lines, pwg
593,596 lines — both bigger than mw's 877,233-line file once entry density
is accounted for) are therefore **structurally unjoinable** to the root
crosswalk today, not merely unjoined: there is nowhere in the schema to put
the id even if someone built the guṇa-grade lookup.

**Implication.** Two separate gaps, not one: (1) a **citation-form
normalization layer** — a small ablaut table (zero-grade ↔ guṇa-grade, the
same handful of vowel-gradation rules Whitney's own Grammar documents) is a
prerequisite for joining pw/pwg/pwkvn/sch to `roots.csv`; without it, any
mechanical join on `root_slp1` silently drops the two largest dictionaries.
(2) a **class-digit extractor per device**, not one regex: MD's `<cl>` tag
is already machine-clean and near-identical in shape to `roots.csv`'s own
`class` column (`I|II|V|VIII` vs `<cl>Ⅷ.</cl>`/`<cl>Ⅰ.</cl>`/…, needing only
Unicode-roman-numeral→ASCII normalization); mw/wil's `<ab>cl.</ab>` text and
ap's `€N` glyph each need their own parser; pwg's German "Nten `<ab>Kl.</ab>`"
covers only 6 of its root entries, so pw/pwg class data will mostly have to
come from parsing the narrative present-stem lists directly rather than any
tagged field. Per §557 (Mylius rule): no claim is made about the 21
zero-signal dicts beyond "no root notation measured" — they may still carry
verb entries under some other undiscovered device, that possibility is out
of scope for this pass.

> Sonnet 5 (`claude-sonnet-5`) · 19-08-2026 · `grep -c "√"` and
> `grep -c "<k1>kf<"` / `<k1>kar<"` over all 44 `csl-orig/v02/*/<dict>.txt`
> files; class-digit device counts via `grep -c "<cl>"`, `grep -c
> "<ab>cl\.</ab>"`, `grep -oE "€[0-9]+" | sort | uniq -c`, and `grep -c
> "[0-9]ten <ab>Kl\."`; citation-form policy confirmed by reading every `kf`/
> `kar` entry for the shared lemma "to do" (kṛ) rather than trusting the
> header-key count alone. Specimens quoted from mw.txt L186067-186069,
> pw.txt L95652-95653 and L118320-118323, pwg.txt L73406-73408, gra.txt
> L15663-15664, md.txt L24758-24759, lan.txt L5543-5548, fri.txt L10591-10592
> and L6914 and L7019, wil.txt L87223-87225, ap.txt L152236-152237,
> pwkvn.txt L9508-9509, sch.txt L30278-30279, and
> [WhitneyRoots/crosswalk/roots.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv)
> header row and line 106. Verifiability: class A (every grep, every quoted
> line, and the `roots.csv` header/row are reproducible from the public
> [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) and
> [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) checkouts).

### §576. Cross-reference markers are three unrelated graphs, not one — `s.`/`Vgl.`/`q.v.`/`=` each point differently, "vide" is a false positive almost everywhere it was expected, and the ring rides inside an xref target far beyond Kochergina

🟠 **The item's own marker list (см./s./vide/Vgl./q.v./=) is not one
cross-reference convention with six spellings — it is at least four
semantically distinct edge types, unevenly tagged, and two of the six named
markers are largely noise once markup is checked instead of the bare string.**
Measured over [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
(`<ab>`-tag counts where the dictionary tags the marker, raw-text counts with
word boundaries where it doesn't) plus `RussianTranslation/src/koch.jsonl`
(local-only, gitignored, per [§574](#574-gloss-language-layering-is-not-german-or-english--it-also-carries-french-burnouf-and-editorial-prose-sircar-and-the-latin-ab-layer-is-itself-language-specific-per-dictionary)):

| dict | `s.`/`siehe` ("see") | `Vgl.`/`vergl.` ("compare") | `q.v.`/`vide` ("which see") | `=` (identity) | ring rides in target |
|---|---|---|---|---|---|
| pwg | 4,650 `<ab>s.</ab>` | 18,234 (18,230 `Vgl.` + 4 `vergl.`) | 0 | 23,108 `= {#…#}` | 11 (`s.`) / 17 (`Vgl.`) |
| pw | 839 | 2,471 (2,470 + 1) | 0 | 10,460 | 11 / 19 |
| gra | 663 `<ab n="siehe">s.</ab>` — **disambiguated from 1,643 false-positive bare `<ab>s.</ab>` = grammatical Singular, not "see"** | 1,593 (239 `Vgl.` + 1,354 lowercase `vgl.`) | 0 | 0 | not measured |
| pwkvn | 98 | 311 | 0 | not measured | not measured |
| sch | 0 tagged — genuine `Vgl.` exists but as bare text, never `<ab>`-wrapped | 633 (bare text) | 0 | not measured | ≥1 (`Vgl. {%avakarṇa˚%}`) |
| cae | 313 `<ab>s.</ab>` — **target is prose ("side, flank"), not a headword pointer; likely Latin *scilicet* ("namely"), not *siehe* — unresolved, flagged not asserted** | 0 | 384 `<ab>q.v.</ab>` | 1,609 `= {#…#}` | not measured |
| ccs | 0 | 10 bare + 3 `{%Vgl.%}` | 0 | not measured | not measured |
| mw | 0 | 0 | 3,506 `<ab>q.v.</ab>` | 14,524 `= <s>…` | ≥1 (`<ab>q.v.</ab>, <s>rAja-k˚</s>`) |
| mw72 | 0 | 0 | 2,342 bare `q. v.` (spaced, untagged) | not measured | not measured |
| ap | 0 | 0 | 1,020 `<ab>q. v.</ab>` (spaced) + rare genuine bare `vide` | 995 | not measured |
| ap90 | 0 | 0 | 917 `<ab>q. v.</ab>` | not measured | not measured |
| wil | 0 | 0 | 78 `<ab>q. v.</ab>` | 0 | not measured |
| bhs | 0 | 0 | 2,599 `<ab>q.v.</ab>` | not measured | not measured |
| lrv | 0 | 0 | 985 bare `q.v.` (untagged) | not measured | not measured |
| inm | 0 | 0 | 246 bare `(q.v.)`, parenthetical | not measured | not measured |
| koch | 7,642 `см.` (26.2 % of 29,177 rows — confirms §574's 25.8 %, small counting-method variance) | — | — | — | 18 `см. °…` |

**Four unrelated devices, not one convention:**
1. **`s.`/`siehe`** (pwg/pw/pwkvn/gra) points *forward* to another headword's
   own `{#…#}` fragment, frequently ring-abbreviated — a genuine, mechanically
   resolvable graph edge. pwg.txt L417660 `<ab>s.</ab> {#˚lIyamAnaka#}`; pw.txt
   L28707 `<ab>s.</ab> {#˚zyanda#}`; gra.txt L70 stacks three: `(<ab
   n="siehe">s.</ab> <ab n="das">d.</ab> <ab n="vorige">v.</ab>)` — "see, this,
   the previous [entry]," a deictic cluster, not a literal target string.
2. **`Vgl.`/`vergl.`/lowercase `vgl.`** (pwg/pw/gra/pwkvn tagged; sch/ccs
   bare-text only) is a *weaker, comparative* edge — "compare," not "is the
   same as." pwg.txt L21 `<ab>Vgl.</ab> über die Betonung noch <ls>P.
   6,2,155</ls>—…` points at a grammar citation, not a headword at all; gra.txt
   L64 `(<ab>vgl.</ab> <ls>Cu. 〔166〕</ls>)` likewise. Tagging is inconsistent
   even within one dictionary: sch.txt L142 `— Vgl. {%avakarṇa˚%}.` and ccs.txt
   L7643 `{%Vgl.%} 1. {#kar#} {%u.%} {#BU#}.` never get an `<ab>` wrapper.
3. **`q.v.`** (English/Latin tradition: mw/mw72/ap/ap90/wil/bhs/lrv/inm/cae) is
   *anaphoric* — it follows the just-named headword within the same sentence
   ("(pragṛhya, q.v.)," mw.txt L11) rather than opening a new clause, but still
   asserts a real edge to that word's own entry. Markup for the identical
   device fragments into four incompatible forms across dicts that share one
   printed abbreviation: tag-wrapped no-space (`<ab>q.v.</ab>` — mw, cae, bhs),
   tag-wrapped spaced (`<ab>q. v.</ab>` — ap, ap90, wil), bare spaced untagged
   (`q. v.` — mw72.txt L5918 `(fr. {%aṇu,%} q. v.), minuteness`), and bare
   unspaced untagged (`q.v.` — lrv.txt L3356 `same as {#aDas#} q.v.`, inm.txt
   L326 `of {%Sṛñjaya%} (q.v.), to whom`). **`vide` is a false positive in the
   German tradition, not a marker**: pwg.txt L109576 and pw.txt L428298 read
   `vide/` — the genuine Sanskrit verb form *vidé* (√vid, "to know/find," a
   Rig-Vedic 3rd-sg. perfect), not the Latin imperative "see." A raw
   case-insensitive `vide` count over pwg/pw (508/225 in the item's naive
   first pass) is 100 % noise; word-boundary re-checks on ccs/sch (32/28 raw)
   also collapse to **zero** — those were substring hits inside unrelated
   words. `vide` is genuine only in the English tradition and at low rate
   there (ap.txt L318818 `({%vide%} <ls>K. P. 9</ls>`).
4. **`=`** (pwg/pw/mw/cae/ap; absent in gra/wil) is the *tightest* edge — a
   literal identity assertion between two headword forms, not "see" or
   "compare": pw.txt L128 `<ab>N. pr.</ab> = {#cARakya#}.`; pwg.txt L11431 `{#anamitaMpaca#} = {#mitaMpaca, anasUri#} … = {#sUri#}` (two chained
   identities in one entry, §554's negation-compound discussion).

**The ring-in-target pattern (§556's `см. °…`) is not koch-specific — it is
the same device wherever a ring-tradition dictionary (§554) also runs an
`s.`/`Vgl.` xref**, at a comparably low rate in every family measured: pwg
11/17, pw 11/19, koch 18/7,642, plus at least one confirmed hit each in mw
(`<ab>q.v.</ab>, <s>rAja-k˚</s>`, L174883) and sch (`Vgl. {%avakarṇa˚%}`,
L142, ring inside sch's own `{%…%}` span rather than `{#…#}`). The rate stays
under ~1 % of xref instances everywhere it was measured — ring-elision inside
a cross-reference target is a marginal but structurally recurring
combination, not a Kochergina peculiarity.

**Implication for csl-lslink-adjacent link extraction.** Three tiers of
graph-forming reliability, not one: `=` is the highest-confidence edge (exact
identity, resolvable directly against `<k1>`/`<k2>`); `s.`/`siehe`/`q.v.` are
real edges but need per-dict markup handling (ring-expansion for pwg/pw/koch
targets, four different tag shapes for the one `q.v.` device); `Vgl.`/`vgl.`
targets are frequently *not* headwords at all (grammar citations, other
compared lemmas) and should not be treated as equivalent to `s.`/`q.v.` edges
without a target-type check. `cae`'s `s.` needs its own disambiguation pass
before being trusted as "see" — the sampled targets read as glosses, not
pointers, and no Cappeller preface page has been re-read to confirm which
sense he intends (§557 Mylius-style caution: flagged unresolved, not
asserted). `gra`'s bare `<ab>s.</ab>` is a **named trap**: it is grammatical
Singular in every sampled instance (100 % of a 10-specimen check), and any
census that counts it as a cross-reference inflates gra's xref rate by
~2.5×the true `<ab n="siehe">` figure — the same class of error the census's
own `<k1>`-vs-`<k2>` lesson (§555/§556/§558) warns against, here in a tag
rather than a key.

> Sonnet 5 (`claude-sonnet-5`) · 19-08-2026 · `grep -c`/`grep -o` over
> `<ab>` tag variants and word-boundary raw text across `csl-orig/v02/*/<dict>.txt`
> (pwg, pw, gra, pwkvn, sch, cae, ccs, mw, mw72, ap, ap90, wil, bhs, lrv,
> inm) and `RussianTranslation/src/koch.jsonl` (local-only, gitignored);
> ring-in-target via `<ab>MARKER</ab> {#˚…#}`-shaped patterns per dict's own
> `{#…#}`/`{%…%}` markup. Specimens quoted from pwg.txt L417660, L109576,
> L11431 and L21; pw.txt L28707, L428298 and L128; gra.txt L70, L64, L689
> (false-positive Singular) and L228; sch.txt L142; ccs.txt L7643; cae.txt
> L950; mw.txt L11 and L174883; mw72.txt L5918; ap.txt L1760 and L318818;
> wil.txt L48635; bhs.txt L28; lrv.txt L3356; inm.txt L326; koch.jsonl row
> 135 (slp1 `-zWIvi`, the exact specimen §556 already quoted, re-verified
> with its jsonl row number). Verifiability: class A (every grep and quoted
> line reproducible from the public
> [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) checkout; koch.jsonl
> is local-only per §574 but its row content is quoted verbatim). Per §557's
> Mylius rule: cae's `s.` sense and ap90/bhs/lrv/inm's full `q.v.` markup
> shape are reported as measured counts only, not asserted as resolved
> "see"-graph edges without a preface cross-check.

### §577. A citation resolver that mints a well-formed URL is not evidence the address exists — `ls_resolver` happily places `ṚV. 99,999,999`, so "it resolves" cannot be the acceptance test for a split or a wrapper

🔴 **`generate_href` is a formatter, not a validator.** Asked for
`ṚV. 99,999,999` it returns
`rvlinks/rvhymns/rv99.999.html#rv99.999.999` — a well-formed URL for a maṇḍala
that does not exist. It range-checks nothing, and it is right not to: for a
citation the source already wrapped, the address came from PWG and is presumed
real, so the resolver's job is to format it.

The trap is any pass that **invents** an address and then uses the resolver as
its acceptance test. Two such passes were built in H3152 — splitting a
multi-address `<ls>` into one element per address, and wrapping a bare
Ṛgveda/Atharvaveda address that carries no element at all. Both are shaped so
that "the resolver gave me a href" feels like proof. It is not. It only proves
the string was formattable.

**Measured, on `csl-orig/v02/pwg/pwg.txt`.** A resolve-only split rule proposed
**2,838 lines**. Every one of them would have produced a second link that
resolves — and points somewhere else entirely:

| element | what the resolve-only rule produced | what it actually is |
|---|---|---|
| `<ls>P. 4,3,66, <is n="Vārttika">Vārtt.</is> 2. 3</ls>` | `<ls n="P.">3</ls>` → Pāṇini **sūtra** 3 | Vārttika 3 |
| `<ls n="MBH. 3,">11087 (p. 572)</ls>` | `572)` as a second address | a page reference |
| `<ls n="HARIV.">83, N. 6</ls>` | `6` as a second address | a note marker |
| `Verz. d. Oxf. H. 100,a. 101,b` | a pair of addresses | catalogue column letters |

Under a rule that additionally requires every address to be **purely numeric**,
all addresses to share a **component count**, and the element body to carry **no
nested markup**, `pwg` proposes **zero** — its genuine multi-address citations
already use the `n=` continuation form. The real population was in the sibling
dictionary `pw`: **141 lines**, all correct. Aiming at the dictionary the plan
named, on the strength of "it resolves", would have queued 2,838 lines of damage
into a corrections batch.

**The generalisation.** For a derived link, the acceptance test must be a
property of the *address* (does this book/hymn/verse exist; is this shape a
sibling of its neighbours), never a property of the *URL* (did a string come
back). A wrapper that mints its own citations therefore carries its own range
table — `ṚV` ≤ 10 maṇḍalas, `AV` ≤ 20 books — even though the resolver it calls
does not.

**Corollary already in force elsewhere:** the same asymmetry decides
recension identity. `AV(P) 9.10,10` is Paippalāda; the Śaunaka `avlinks` URL for
`AV. 9,10,10` would format perfectly and assert a false identity between two
recensions, so it is refused rather than linked.

Evidence: `RussianTranslation/src/ls_split.py::splittable` and its selftest (every
refusal is pinned on a real `pwg.txt` line), `nws_citation_wrap.py::_accept`
(`_MAX_BOOK`), and `ls_split_changefile.py --dict pwg|pw --count`. Full write-up:
`RussianTranslation/pwg_ru/H3152_REGLUE2_CITATION_LAYER_TYPOLOGY_REPORT_19-08-2026.md`.

### §578. Accent digitization is three incompatible devices and svarita is essentially un-digitized — `/` lives in `<k2>` of exactly 9 dicts, `\` survives in 17 lemma marks total, and the German-school translit dicts carry accent as acute vowels that never reach the headword field

Measured over all 44 v02 dictionaries (`csl-orig/v02/*/DICT.txt`, main files;
cae front/middle/back parts not included — residue). Method: parse each entry's
head line fields (`<k1>`/`<k2>`, unclosed-tag convention) and body until
`<LEND>`; count `/` and `\` inside `<k2>` and inside each dictionary's own
Sanskrit-span flavors (`{#…#}`, `<s>…</s>`, `{@…@}`) after stripping
self-closing tags (`<info lex="m"/>`), tag internals (attributes such as
`<per n="3ten/dritten">`) and `{%…%}` English italics — the noise classes that
inflate naive greps by orders of magnitude (mw alone has 106 693 raw
slash-bearing body lines, most of them markup).

**Device 1 — slash in the headword field (`<k2>`), 9 dicts:**

| dict | entries | `<k2>` w/ `/` | share |
|---|---:|---:|---:|
| mw | 286 525 | 47 589 | 16.6 % |
| pw | 170 556 | 21 543 | 12.6 % |
| pwg | 123 366 | 20 876 | 16.9 % |
| cae | 40 069 | 11 313 | 28.2 % |
| ccs | 30 010 | 8 476 | 28.2 % |
| gra | 12 785 | 10 699 | **83.7 %** |
| lan | 4 944 | 2 226 | 45.0 % |
| sch | 29 125 | 1 124 | 3.9 % |
| pwkvn | 24 976 | 2 108 | 8.4 % |

The other 34 dicts have zero slash accents anywhere (ap, wil, vcp, shs, skd,
bop, pe, pui, lrv, mci, …). Gra's 83.7 % is what a genuinely Vedic lexicon
looks like when accent survives digitization; sch's 3.9 % shows the same Vedic
ambition reduced to fragments.

**Device 2 — acute-vowel transliteration, slashes absent:** stc 13 116,
gra 11 418, bur 9 018, md 6 651, fri 6 102, lan 2 920 entries carry accented
vowels (á/í/ú) in body prose but plain unaccented `<k2>` fields. Specimen:
md.txt L1147 `<k1>agnihotra<k2>agnihotra` (no accent) vs md.txt L1148 body
`{#agnihotra#}¦ <hom>1.</hom> agni-hotrá, <lex>n.</lex>` — the accent exists
only in prose, so a k2-keyed join loses it silently.

**Device 3 — svarita `\` is essentially un-digitized:** exactly **17 lemma
marks corpus-wide** — pw 5 (`tva\` L197505, `tu\a\` L197510, `sa\ma\ha\`
L501712, plus `{#tA\pi\n#}` L586274 and `{#ma\ryA\s#}` L636099 in bodies),
pwkvn 2 (mirroring pw: `tA\pi\n` L18667, `ma\ryA\s` L68035), pwg 10 — all pwg
occurrences sit inside Vedic *quotation* spans, not lemmas
(`{#ra\yiM Ba\rAMSa\…#}` L44 ff.). No dictionary digitizes svarita as a
systematic layer.

**Where the accent sits in compounds — the handoff's disagreement, resolved by
specimen:** the slash position IS the homonym disambiguator in the PW family.
pw.txt L2563/L2568, pwg.txt L2413/L2421, cae.txt L770/L773, ccs.txt L656/L660
all print the same pair: `<k2>agnihotra/` (n., final accent) vs
`<k2>agni/hotra` (mfn., first-member accent). In pw/pwg/cae/ccs/pwkvn the
compound slash lands in the first member **100 % of the time** (later-member
count 0). MW mirrors the device with an em-dash division:
mw.txt L4137 `<k2>agni/—hotra<h>1`, L4146 `<k2>agni—hotra/<h>2` — 41 539
first-member vs 6 050 later-member. GRA is the outlier: hyphenated members
with the accent free to land in the second member — gra.txt L18949
`gotra-Bi/d`, L33018 `ni/tya-stotra`, L17301 `kzRo/tra`; 8 583 first vs
**2 116 later-member (~20 %)**. lan hyphenates but keeps final placement:
lan.txt L173 `agni-hotra/`. Any cross-dict headword join must therefore carry
the slash as data, not strip it: normalizing `agni/hotra` to `agnihotra`
merges two distinct senses in every PW-family dict.

**Noise classes excluded (the "distinguish accent from other slashes" rule):**
self-closing tags (`<info lex="m"/>`), tag attributes (`n="3ten/dritten"`),
ccs.txt L1 Windows path residue `E:\SANSKRIT\CAPPELLE\CCS.AL1`, and gra
revision metadata (`<chg type="chg" n="194">`). SLP1 cross-check per
SANSKRIT_CONTEXT_PRIMER: post-vocalic `/` marks udātta on the preceding vowel
(`aha/m` → ahám), consistent across all 9 slash dicts.

**Residue:** cae part-files uncounted; gra's own agnihotra entry not located
under that exact spelling (case/spelling drift — device verified via
gotra/stotra/aMSa families); `{@…@}` hits in ap are `<ab>Comp.</ab>` markup
artifacts, ap carries zero real accent marks; etymology_stats holds no entry
text. Per §557's Mylius rule the acute-body counts are reported as measured
occurrences, not asserted as a complete accent inventory of those editions.

Verifiability: class A — every grep and quoted line reproducible from the
public csl-orig checkout. Driver logic is the method paragraph above
(field-after-tag parser + span flavors + noise strippers); counts reconcile:
per-dict `k2_slash ≤ k2_total`, and all 17 svarita marks are individually
line-cited.

### §579. Citation density is a cliff, not a spectrum — 16 dicts wrap citations in `<ls>`, 22 have literally zero, and PWG alone carries 801 788 of them; tag-presence misclassifies GRA, whose printed proof lives in prose

Extends the [§18](#18-vedic-citation-density-separates-the-dictionary-traditions)
four-dictionary measurement (PWG ≈ MW ≫ AP90 ≫ Kochergina) to every v02
dictionary (`csl-orig/v02/*/DICT.txt`; Kochergina itself is not in v02 —
koch.jsonl stays local-only per §574, so the fourth tradition keeps its §18
number). Method: same entry parser as §578 (head-line fields + body until
`<LEND>`); count `<ls …>` elements per ENTRY over head line and body joined;
page-ref subclass = an `<ls>` whose body matches explicit page markers
(`p./pp./S. N`, `col. N`, `pag. N`) — verse addresses such as
`<ls>P. 1,1,14</ls>` are source citations, not page refs.

| dict | entries | entries w/ `<ls>` | share % | total `<ls>` | ls/entry | w/ page mark |
|---|---:|---:|---:|---:|---:|---:|
| pwg | 123 366 | 116 519 | **94.4** | **801 788** | 6.50 | 56 554 |
| ieg | 7 932 | 7 339 | 92.5 | 11 390 | 1.44 | 0 |
| bhs | 17 839 | 16 291 | 91.3 | 48 419 | 2.71 | 1 |
| sch | 29 125 | 26 034 | 89.4 | 31 041 | 1.07 | 1 057 |
| mw | 286 525 | 226 712 | 79.1 | 320 828 | 1.12 | 102 |
| ben | 17 310 | 13 234 | 76.5 | 49 234 | 2.84 | 0 |
| pwkvn | 24 976 | 13 576 | 54.4 | 17 627 | 0.71 | 1 148 |
| lan | 4 944 | 2 546 | 51.5 | 5 912 | 1.20 | 0 |
| pw | 170 556 | 66 188 | 38.8 | 98 485 | 0.58 | 5 347 |
| ap | 90 843 | 28 696 | 31.6 | 68 273 | 0.75 | 700 |
| ap90 | 34 882 | 10 867 | 31.2 | 43 892 | 1.26 | 464 |
| lrv | 53 441 | 9 086 | 17.0 | 16 650 | 0.31 | 0 |
| gra | 12 785 | 1 539 | 12.0 | 2 341 | 0.18 | 50 |
| ae | 11 359 | 771 | 6.8 | 1 141 | 0.10 | 267 |
| bor | 24 609 | 377 | 1.5 | 526 | 0.02 | 0 |
| md | 20 749 | 53 | 0.3 | 58 | 0.00 | 0 |
| wil | 44 577 | 6 | 0.0 | 6 | 0.00 | 1 |

The remaining 22 dicts — abch acc acph acsj armh bop bur cae ccs fri gst inm
krm mci mw72 mwe nmmb pe pgn pui shs skd snp stc vcp vei yat (zero `<ls>`
elements at all) — assert without any citation markup: the koṣa tradition
(skd/vcp/shs/amara-family), the poetic-index pairs cae/ccs, and the
name-indices (pe/pui/inm/mci/lrv) prove nothing because they claim nothing.

**Top/bottom deciles:** top = {pwg, ieg, bhs, sch}, bottom = {stc, vcp, vei,
yat} (of 44 ranked by share).

**Three readings the raw ranking would hide:**

1. **PWG is not first among equals — it is half of the corpus.** Its 801 788
   `<ls>` elements exceed the next five dicts (mw 320 828, pw 98 485,
   bhs 48 419, ap 68 273, ap90 43 892) *combined*. Any citation-graph build
   (§576 edges, ls_resolver links) is demographically a PWG project.
2. **pw vs pwg is abridgement depth, not school.** Same Böhtlingk tradition,
   yet pw cites in only 38.8 % of entries at 0.58/entry against pwg's
   94.4 % / 6.50 — the seven-volume PW proved senses the abridged PW chose to
   assert.
3. **Tag presence is a markup artefact for GRA.** Grassmann's printed entries
   teem with realia citations, but they live as prose plus `〔p. N〕` brackets:
   gra has `<ls>` in only 12.0 % of entries (0.18/entry) while its body text
   carries thousands of unwrapped citations. Classifying GRA "asserting" from
   markup alone would be wrong — it is the corpus's biggest
   citation-extraction residual (its 50 page-marked `<ls>` show the shape:
   gra.txt L3401 `<ls>Cu. 〔p. 411〕</ls>`).

**Page-marker subclass:** 65 000-ish elements corpus-wide carry explicit page
references (pwg 56 554 = 7.1 % of its own, pw 5 347, pwkvn 1 148,
sch 1 057, ap 700, ap90 464) — these are the resolvable-to-scan candidates;
the rest resolve only through a work's internal numbering (sūtra/verse
addresses).

**Specimens (file:line):** pwg.txt L3 `<ls>P. 1,1,14</ls>` (sūtra address);
mw.txt L50826 `<ls>Saṃhitop. p. 7</ls>`, mw.txt L89247
`<ls>Siddh. ii, p. 393, l. 21</ls>` (work + page + line);
ap90.txt L2215 `<ls>Bṛ. S. 33</ls>`, ap90.txt L3703 `<ls>K. P. 10</ls>`;
gra.txt L3401 `<ls>Cu. 〔p. 411〕</ls>`, gra.txt L5592
`<ls>Max Müller the sixth hymn 〔p. 4〕</ls>` (prose-work + bracketed page);
gra.txt L7901 `<ls>Pauli, Körpertheile 〔p. 24〕</ls>`.

**Residue:** counting is element-level per entry; multi-entry lines do not
occur (one head line per entry, verified by the §578 parser); `<j>` and
`<div>`-nested `<ls>` counted where they fall inside the entry body; per
§548, PWG's `<ls>` counts split into incompatible families (cleaned-string vs
work-family) — this census reports the raw markup family, which partitions
every dictionary but must not be equated with either §548 family; per §557 no
claim is made about dictionaries whose printed editions cite differently from
their digital markup (GRA being the standing example).

Verifiability: class A — reproducible greps over the public csl-orig
checkout; every specimen line-cited above.

### §580. AP90's `<pc>` field is a third, distinct shape from mw/pwg — page-column-LETTER (`NNNN-a/b/c`), not comma or vol-page — and a tool that assumes one shape silently drops 100% of a dict's scan links

🟠 **csl-atlas's Cologne scan-URL builder trusted only two `<pc>` shapes — mw's
`page,column` and pwg's `vol-page` — so AP90, whose `<pc>` is
page-column-**letter** (`0001-a`, `0001-b`, `0001-c`), silently resolved 0% of
its 34,882 entries despite being correctly registered as a known scan
directory.** Not a missing-data gap: the coordinates were 100% present, the
parser just didn't recognise the shape.
Evidence: [`scripts/lib/cologne-links.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs)
`scanPageFromPc()` required either a bare digit string or a `page,column`
split; AP90's actual `<pc>` values in
[`v02/ap90/ap90.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt)
fail both. Fixed 24-08-2026 (csl-atlas
[PR #414](https://github.com/sanskrit-lexicon/csl-atlas/pull/414), H2368-A10)
by stripping the trailing column letter(s) and keeping the page digits
verbatim (leading zeros preserved). Re-running csl-atlas's
`scripts/metalex/l8_scan_link_census.py` moved AP90 from 0% → **99.29%**
atlas-resolvable (34,636 of 34,882 entries). A residual **246** entries carry
a *fourth* shape, `NNNN-N` (numeric suffix, e.g. `0220-1`, first hit at
`ap90.txt` L5719 `<pc>0220-1`) — left unresolved rather than guessed at; its
meaning is not yet established.
Implication: **never infer one csl-orig dict's `<pc>` convention from
another's.** At minimum four incompatible shapes are attested across the
corpus — mw `page,column`, pwg `vol-page`, ap90 `page-column-letter`
(dominant) plus ap90's own residual `page-N` numeric-suffix outlier. Any tool
building print-page or scan-page links from `<pc>` must check each dict's
shape empirically (e.g. `grep -oP '<pc>\K[^<]+' v02/<dict>/<dict>.txt | sed
's/[0-9]/N/g' | sort | uniq -c`) rather than reusing an mw/pwg-shaped parser.
This corrects §23's aside that AP90's `<pc>` is "numeric `<pc>0002-1`
page-cols" — that shape is the rare (0.7%) residual, not AP90's dominant
convention.

> **Source:** csl-atlas
> [`data/metalex/L8_SCAN_LINK_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/metalex/L8_SCAN_LINK_CENSUS.md)
> (H2368 census, re-measured H2368-A10) +
> [`scripts/lib/cologne-links.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lib/cologne-links.mjs). — csl-atlas / csl-orig · 2026-08-24

### §581. A dictionary index's "SLP1" column can be Harvard-Kyoto — KEWA's is, and joining it as SLP1 silently drops half the headings; separately, NFD-stripping the Vedic acute destroys ś

The OCRed KEWA heading index
(`SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt`, 9,587 blocks →
11,418 headings) ships **two** slashed machine-key columns per heading. The
second sits exactly where an SLP1 column would sit and reads like SLP1 —
`aMzaH`, `akSauhiNI`, `akSNoti`. It is **Harvard-Kyoto**: ś is `z` (SLP1 `S`),
ṣ is `S` (SLP1 `z`), ṇ is `N` (SLP1 `R`), ṭ is `T` (SLP1 `w`), and the
diphthongs stay `ai`/`au` (SLP1 `E`/`O`).

Converting HK→SLP1 and comparing against the canonical
[`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util)
transcoder's output on the IAST column agrees on **9,930 of 9,931 headings
(99.99 %)** — the one exception, `hvātar-` keyed `hvaAtar`, is a source typo.
The two encodings coincide on every letter outside that set, so **5,684
headings look fine and 5,733 are silently wrong** if the column is joined
against SLP1 data such as `csl-orig`. Just over half a dictionary, lost with no
error anywhere.

**Implication:** never infer a machine-key column's scheme from the fact that
it is ASCII and sits beside IAST. Test it — one round-trip through the
canonical transcoder over the whole column tells you in seconds, and the
agreement rate is the proof. HK and SLP1 are *both* ASCII, *both* lowercase-ish
and differ on exactly the letters a Sanskrit index is full of.

**The second trap, in the same file.** KEWA marks the udātta with a combining
acute (U+0301) over the accented vowel. The obvious way to strip it —
`unicodedata.normalize("NFD", s)`, drop every U+0301, recompose — also destroys
**ś**, because ś decomposes to `s` + U+0301 too. Every *śa*-word silently
becomes an *sa*-word before the join. The first pipeline run reported 5,731
"transcoder disagreements" that were entirely this bug and nothing else. Strip
the acute only when the base letter is a vowel (`a i u e o`, plus the vocalic
`ṛ`/`ḷ` written base + dot-below):
[`kewa_accent.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/kewa_accent.py).
The same trap is waiting in any accented-IAST source — SCH's accented headwords,
Grassmann, Renou.

> **Source:** [KEWA_INDEX_NORMALIZATION_AND_PWG_JOIN_25-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/KEWA_INDEX_NORMALIZATION_AND_PWG_JOIN_25-08-2026.md)
> §2a (H3169, Opus 5 `claude-opus-5`). — SanskritLexicography / SamudraManthanam · 2026-08-25

### §582. The damage in a digitized index is not always OCR — KEWA's came from a Russian-locale spreadsheet, which turned page ranges into dates and leading-hyphen headwords into `#ИМЯ?`

H3169 was scoped to census "OCR noise (broken diacritics, run-together
headings, page-furniture lines)" in the KEWA index. **There is none.** 9,587 of
9,588 lines parse against the first pattern tried; the exception is the header
comment. No hyphenation debris, no running heads, no column bleed.

What the file does carry is the signature of a round-trip through a spreadsheet
opened in a **Russian locale**:

| Class | Rows | Damage | Recovery |
|---|---:|---|---|
| page-range → date | 3 | `10-11` stored back as `10.ноя`; also `11.дек`, `дек.13` | the image filename kept it: `2-010-11-05.jpg` → pages 10–11 |
| leading hyphen → formula error | 5 blocks | `-ā`, `-īm`, `-tṛp`, `-dhṛk`, `-prāṇi` parsed as formulas, stored as `#ИМЯ?` (`#NAME?`) | the machine-key column was not damaged and carries the true form |
| legacy-font Latin leak | 3 | a Devanāgarī consonant present as literal `Z` (`मद्गुZअ-`, `Zअरणः`) — the legacy-font code point for श/ष never mapped | none; flagged, key marked unusable |

All eight Cyrillic-contaminated rows in the file come from those two classes,
and both are **fully recoverable** from a redundant column that the spreadsheet
did not touch.

**Implication, and it generalizes past this file:** audit a digitized asset for
the pipeline it actually went through, not the pipeline its provenance note
names. A `#NAME?`, a `#ИМЯ?`, a `10.ноя`, a right-aligned number that should be
text, a leading `-`/`+`/`=` turned into an error — these say *spreadsheet*, and
they cluster on exactly the rows a Sanskrit index is most likely to have
(bound forms beginning with a hyphen, page *ranges*). An OCR-shaped audit —
diacritic checks, character-confusion matrices, line-shape heuristics — will
find none of them and report the file clean. Grep for the locale's error tokens
and month abbreviations first; it costs one command.

> **Source:** [KEWA_INDEX_NORMALIZATION_AND_PWG_JOIN_25-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/KEWA_INDEX_NORMALIZATION_AND_PWG_JOIN_25-08-2026.md)
> §2 (H3169, Opus 5 `claude-opus-5`). — SanskritLexicography / SamudraManthanam · 2026-08-25

### §584. A style pass applied to CommentaryStrategies' `data/lexical/chN.json` never reaches the apparatus or the print master — `build_sarga_apparatus.py` prefers the aggregate twins in `data/sundara_commentary_to_add.json`, so the source you edited is the one that loses the dedup

H3492 (Fable 5 `claude-fable-5`, 25-08-2026) rewrote 37 lexical notes in
`data/lexical/ch2.json`…`ch5.json`, the files every handoff and the repo
CLAUDE.md name as *the* source ("edit JSON, never the generated outputs"). The
audit went 0 → all-keep-cards-clean, the PR merged, the release was cut. Then
`python scripts/build_sarga_apparatus.py 2 3 4 5` changed **4 lines** in
`sarga_02.json`, 4 in `sarga_04.json`, 0 in `sarga_05.json` — the apparatus
and the print master still carried the old texts.

Cause, in the builder's own docstring: the lexical layer is
`data/sundara_commentary_to_add.json` (book-level aggregate, `subtype !=
cross_text`) **∪** `data/lexical/ch{N}.json`, "deduped on
`(shloka, lemma_iast)`" — and the aggregate wins the dedup. The aggregate holds
a *copy* of nearly every `chN.json` card (sargas 2–5: 14/10/7/7 twins for
16/13/8/7 cards). So the file the conventions say to edit is exactly the file
whose edits are discarded whenever a twin exists. H2833 had hit the same wall
on sarga 1 and solved it with a one-off
[`scripts/sync_grintser_pass_book_s1.py`](https://github.com/gasyoun/CommentaryStrategies/blob/main/scripts/sync_grintser_pass_book_s1.py)
("build_sarga_apparatus.py prefers them over data/lexical/ch1.json in its
dedup, so the pass must land here too") — recorded in that script's
docstring and nowhere a sarga-2 session would read it.

Two corollaries measured the same day:

1. **A lemma typo lives twice.** `V.3.5 lemma_iast = bhujagācārita` (verse:
   *bhujagācaritām*) and `V.3.12 vasvokaṣārā` (verse: *vasvokasārā*) were wrong in
   `ch3.json` *and* in the aggregate twin; fixing one leaves a dedup key that no
   longer matches, so the apparatus would then show **both** the old and the new
   card. Any `lemma_iast` repair must touch both files in one commit.
2. **The print master had been stale for nine days.** `data/book/sundarakanda_print_master.md`
   was last regenerated 10-07 (before H2833 on 16-08); the 25-08 rebuild diffed
   402 lines, most of them H2833's sarga-1 texts arriving late. CI's
   "every generator reproduces its artifact" gate does not cover
   `build_sarga_apparatus.py` / `build_book_apparatus.py`, so nothing flags a
   source–derived drift there.

**Rule:** after any edit to `data/lexical/chN.json`, run
`python scripts/sync_grintser_pass_book.py --chapter N --handoff <id>`
([generalised in H3498](https://github.com/gasyoun/CommentaryStrategies/blob/main/scripts/sync_grintser_pass_book.py))
or otherwise land the same change on the aggregate twin, then rebuild
`build_sarga_apparatus.py N` and `build_book_apparatus.py`, and check the
derived diff is the size you expect — a 4-line apparatus diff after a
14-card rewrite is the signature of this trap, not of a small change. Verified
fix: 31 twins synced, apparatus diffs 28/26/16/14 lines, remaining `MW:` inline
in apparatus lexical notes = the 7 `reject`/`park` cards only.

> **Source:** [CommentaryStrategies PR #197](https://github.com/gasyoun/CommentaryStrategies/pull/197)
> (H3498, Fable 5 `claude-fable-5`) after
> [PR #195](https://github.com/gasyoun/CommentaryStrategies/pull/195) (H3492);
> report [data/lexical/style_pass_h3492/REPORT.md](https://github.com/gasyoun/CommentaryStrategies/blob/main/data/lexical/style_pass_h3492/REPORT.md).
> — CommentaryStrategies · 2026-08-25

### §585. Paired totals N and N+1 for the same TSV artifact are the header-row signature — read line 1 before hypothesizing regeneration drift

🟠 **When two published counts for one tabular file differ by exactly 1, the
first probe is `head -1`, not a rebuild.** The union headword total circulated
for months as both 323,425 (SanskritLexicography surfaces + kosha's own
`datasets.json`) and 323,426 (kosha README twice, three archived handoffs) —
open as CONTRADICTIONS §10, with regeneration drift as a live hypothesis.
Measured directly on the canonical asset:
[union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
holds **323,426 physical lines**, line 1 is the column header
(`slp1 · iast · n_dicts · dicts · gender · fem_fold`), the file ends in a
newline — so **data rows = 323,425**, the headword count of record. Every
323,425 witness counts headwords; every 323,426 witness counts file lines (or a
header-inclusive load). Both sides were "right"; neither named what it counted.

Implication: an exactly-1 gap between counts of the same artifact is a *shape*
signature, and it is the cheapest contradiction class there is — one `wc -l`
plus one `head -1` closes it (class A, auto-reproducible). Rebuilding the
pipeline to explain it is the expensive wrong move. Corollary for prose: a
count published next to a tabular artifact should say which of the two it is —
"323,425 headwords (323,426 file lines incl. header)".

> **Source:** [CONTRADICTIONS.md §10](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
> ruling + verdict table [docs/CONTRADICTIONS_ADJUDICATION_WAVE1_26-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/CONTRADICTIONS_ADJUDICATION_WAVE1_26-08-2026.md)
> (H3538, Fable 5 `claude-fable-5`). — SanskritLexicography · 2026-08-26

### §586. Two conflicting family totals can be exact sums of the SAME files at two pipeline stages — the 285,799 vs 285,950 gap is the union build's key collapse, not vintage drift

🟠 **Before explaining a totals mismatch as "different vintages" or "mixed key
types", test whether both figures are exact sums of the same file set at two
pipeline stages.** The Petersburg-family naive sum was published as 285,799
(MODULES_OWNED, "+70.2 % inflation" module) and 285,950 (WAVE1_SUMMARY +
roadmap) — open as CONTRADICTIONS §12, with vintage drift and key1/key2 mixing
as the live hypotheses. Both identities verified by direct count:
**285,950 = 106,082 (PWG) + 151,349 (PWK) + 28,519 (SCH)** — the raw
[now-2026](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/now-2026)
export files' `wc -l`, each equal to its filename `N`; **285,799 = 106,054 +
151,314 + 28,431** — the union-*ingested* per-dictionary row counts that
MODULES_OWNED itself publishes. The 151-key gap is the union build's key
collapse (PWG −28, PWK −35, SCH −88), not drift; the vintage/key-mixing
hypothesis is REFUTED. The inflation headline is internally consistent —
numerator and denominator both come from the ingested stage.

Implication: a pipeline with a lossy stage (dedup, fold, key collapse) mints a
*legitimate* pair of totals for every artifact that crosses it, and any prose
quoting one without naming the stage will eventually "contradict" prose quoting
the other. The discriminating probe is arithmetic on the candidate stage sums
(class A) — cheaper than any provenance archaeology. Cite 285,799 beside
union/de-dup figures, 285,950 when counting raw export lines, and name the
stage either way.

> **Source:** [CONTRADICTIONS.md §12](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
> ruling + verdict table [docs/CONTRADICTIONS_ADJUDICATION_WAVE1_26-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/CONTRADICTIONS_ADJUDICATION_WAVE1_26-08-2026.md)
> (H3538, Fable 5 `claude-fable-5`). — SanskritLexicography · 2026-08-26

### §587. Derivative ī/ū-stem gen.pl accent: oxytone nouns are 44/44 stem-final, the devī́-declension adjective/participle class genuinely vacillates — Whitney §319a and §320/§356 have disjoint scopes

🟠 **Whitney's "self-contradiction" on the `-īnā́m` vs `-ī́nām` gen.pl
dissolves under word-class control, at full-corpus n.** Census of all 2,159
gen.pl tokens of the accented RV (Zurich glossed corpus, Casaretto et al.
2025): **independent derivative ī/ū-stem nouns (nadī́-, tanū́-, rathī́-,
vadhū́- …) keep the accent on the stem vowel — 44/44 oxytone tokens
`-ī́nām`, zero exceptions** (§320/§356 confirmed); **devī́-declension
feminines of adjectives/participles — §319a's own word class — genuinely
vacillate** (~9 ending vs ~11 stem-final tokens, with §319a's own example
`bahvīnā́m` attested ending-accented ×2: 01.095.04, 06.075.05); monosyllabic
roots (dhī́-, śrī́-) shift 8/8 by the separate §355 rule; barytones never
move (62/62); máh- is the one genuinely mixed lemma (mahī́nām ×4 vs mahīnā́m
×1). The D3 cell of the ZALIZNYAK a–f accent axis emits stem_final as a
*rule* for derivative ī/ū noun lemmas; the per-lemma-variant encoding is
reserved for the devī́-declension class and máh-. Tier 1 (whole-corpus
census, reproducible script). Full per-lemma tables:
[docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md);
script [d3_genpl_probe.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/d3_genpl_probe.py).

> **Source:** [CONTRADICTIONS.md §1](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
> ruled + [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) closed
> (H3555, Fable 5 `claude-fable-5`). — SanskritLexicography/WhitneyRoots · 2026-08-26

### §588. The VedaWebProject/vedaweb-data GitHub mirror replaces the WAF-blocked VedaWeb API for bulk corpus pulls

🟠 **When `vedaweb.uni-koeln.de` answers HTTP 418 (WAF block, ongoing since
12-07-2026, re-probed 26-08-2026), do not wait out the outage — the full
corpus data is public in the
[VedaWebProject/vedaweb-data](https://github.com/VedaWebProject/vedaweb-data)
GitHub repo.** `rigveda/versions/zurich.xlsx` (12.6 MB, 164,768 token rows
× 32 columns) is the same Zurich morphologically glossed RV (Casaretto et
al. 2025, CC BY 4.0) the API serves as corpus resource
`66695e4a14f6d337f7788740`, with per-token case/number/gender
(`belege::kasus/numerus/genus bestof`), surface form, pāda, locus, and
classical lemma — everything the accent-validation and D3 probes needed
from the API, minus pagination and rate limits. One `git clone` (or raw
download) beats any API resume plan; the mirror is Tier 1 primary data.

> **Source:** probe method in [docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md)
> · [SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md) vedaweb row
> (H3555, Fable 5 `claude-fable-5`). — SanskritLexicography · 2026-08-26

### §589. The R4.1 "any SAN-LOSS reaching the store" freeze trigger is a marker grep, not a gate — four real SAN-LOSS rows sit in the pwg_ru store unseen

🔴 **`store_san_loss_scan()` in [`RussianTranslation/src/pilot/spot_check_daily.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/spot_check_daily.py) implements the unconditional lane-freeze condition as a regex for the literal strings `SAN-LOSS` / `UNMAPPED` inside `ru`. It never recomputes `{#…#}` span preservation against `de`.** Re-running the actual gate ([`markup_fidelity_gates.markup_span_flags`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/markup_fidelity_gates.py), the RU thresholds) over all 11 620 rows of the live store finds **4 SAN-LOSS + 1 LS-LOSS rows** (`dA` desiderative head-line with four P./VOP. citations, `dA`+`anu` preverb head, `mA` hom. 5 root variant, `pat` present stem, `asvatantra` fem. ending) — identical in the `pwg-ru-data/tm/` mirror, so they pre-date H3500 and passed every window close; `spot_check_daily` reports `san_loss_in_store=False` for the same store. Compounding it: the `PWG-RU spotcheck pc lane` scheduled task is **Disabled** on the box and `pwg-ru-data/telemetry/` holds zero `spotcheck_*.json` — the surveillance H2264 re-wired after H2246 found it dead is dead again, and its sample frame (`*.PROMOTED.json` auto-promotion records) is empty for supervised windows anyway. Store-level runner: [`RussianTranslation/src/audit_store_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_store_gates.py) (exit 1 on any hard flag; also diffs src against the mirror — see [GAPS §16](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) for the 289-row `Instr.`→`Ins.` drift it surfaced). Pattern class: a control whose predicate is a *label* of the defect rather than the defect (cf. §263 informal-label invisibility).

> **Source:** [reports/PWG_RU_TRANSLATION_STORE_AUDIT_27-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/PWG_RU_TRANSLATION_STORE_AUDIT_27-08-2026.md)
> · [H3590](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3590-Fable_RussianTranslation_pwg-ru-translation-store-audit_27.08.26.md)
> (Fable 5 `claude-fable-5`). — SanskritLexicography · 2026-08-27

### §590. A denylist keyed on function words cannot fence a reuse lexicon — archaic-orthography content glosses still return unrelated targets

🔴 **A source-reuse denylist enumerated as function words is a *lexical* fence around a *structural* defect, and the two do not coincide.** The defect is exact-source reuse returning a Russian string that belongs to a longer collocation in the publication record. [`RussianTranslation/src/pwg_tm_wave2_policy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_wave2_policy.py) fences it by listing 30 German articles, pronouns and prepositions in `SHORT_GLOSS_DENYLIST`. **Evidence:** query the source lexicon with that policy *switched on* and `{%Jmd%}` is correctly refused while `{%thun%}` — archaic *tun*, a content word the list cannot reach — still returns `{%класть%}` ("to put") for a gloss meaning "to do". Measured over the frozen H2684 gate sample by [`src/pwg_tm_serious10.py reach`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_serious10.py): **13 of 400 rows carry the mechanism, of which the judge flagged only 8 serious** (a sixth `{%Jmd%}` → `{%поручать кому-л.%}` corruption drew no flag at all), and **4 of the 13 interceptions are of *correct* fills** (`bei`→«у», `und`→«и», `zu`→«к», `wie`→«как»). **Implication:** the denylist is worth keeping — it trades 4 trivially re-derivable correct fills for 9 false semantic claims — but never cite it as coverage for the reuse defect, and expect a Wave-2 quarantine rate slightly above the Wave-1 baseline as *correct* behaviour, not a regression. A structural fence (require the source span to be a full lexical unit, or require the reuse target's source to be the whole publication fragment) is what would actually close the class; an enumeration only ever closes the tokens someone remembered. Same shape as §589: a control whose predicate is a *label* of the defect rather than the defect.

> **Source:** [pwg_ru/PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md)
> · [H2877](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2877-Opus_RussianTranslation_pwg-tm-w1-serious-error-10-repair_16.08.26.md)
> (Opus 5 `claude-opus-5`) · [PR #1911](https://github.com/gasyoun/SanskritLexicography/pull/1911). — SanskritLexicography · 2026-08-27

### §591. Withdrawing a false gloss clears the serious-error ceiling and breaks the fidelity floor — a quality gate can be moved rather than passed

🔴 **A repair that removes a defect class can push a *different* floor below its threshold, so "the ceiling now passes" is not "the gate now passes".** [H2877](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2877-Opus_RussianTranslation_pwg-tm-w1-serious-error-10-repair_16.08.26.md) repaired the 10 serious-error rows of the H2684 n=400 gate deterministically, by withdrawing each false Russian gloss and restoring its German source. **Evidence:** an independent `x-ai/grok-4.5` re-score under the H3299 pinned rubric ([`src/pwg_tm_serious10_rescore.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_serious10_rescore.py), $0.138366, real tokens) scores those rows **0/10 serious** — nine `german_residue`, pinned non-serious, plus one clean `none`. But all ten had been scored `fidelity: pass` *before* the repair: to that judge a wrong Russian gloss is faithful-but-inequivalent, while an untranslated German span is **unfaithful**. Splicing the new verdicts over the frozen sample (`project` subcommand) gives fidelity **99.50 %→97.25 %** (floor 98 %, FAIL), equivalence 95.50 %→95.75 % (PASS), serious_error **2.50 %→0.00 %** (ceiling 1 %, PASS). The gate still fails — it has moved from the ceiling to the floor. **Implication:** never report a single-metric improvement from a repair without re-deriving *every* gate metric on the same sample; a withdrawal is the correct cure for a false *claim* but converts it into a completeness miss, so it can only pass a gate whose floors tolerate untranslated source. Where a floor does not, the rows need real translation, not withdrawal — here 9 of 10 do, and only `taruRa` (an `<ab>` copy-through) was actually finished. Corollary for judging: `fidelity` and `equivalence` are not ordered here, and a row can lose fidelity while gaining equivalence.

> **Source:** [pwg_ru/PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md)
> · [H3611](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3611-Opus_RussianTranslation_pwg-tm-w1-serious10-rescore_28.08.26.md)
> (Opus 5 `claude-opus-5`) · [PR #1919](https://github.com/gasyoun/SanskritLexicography/pull/1919). — SanskritLexicography · 2026-08-28

### §592. A gitignored artifact labelled "regenerable" with hardcoded consumers is a shared singleton, and the label is often false

🔴 **Before overwriting any gitignored intermediate, grep for its literal path: "gitignored, regenerable" in a docstring is an author's intent, not a verified property.** [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py) wrote unconditionally to `src/pilot/output/nominal_batch_worklist.json`, documented exactly that way. **Evidence:** four independent consumers read that literal path — [`progress_dashboard/build_progress_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_progress_data.py), [`kitchen_slices.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_slices.py), [`kitchen_nominal_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_nominal_selftest.py) and [`h963_c4_pilot_candidates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_pilot_candidates.py) — so a 61-row re-ingest run would have silently redefined the **public** progress kitchen's nominal counts. And the file is not regenerable: [H963 C4 call graph](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_PIPELINE_CALL_GRAPH_2026-07-16.md) row D7 shows rebuilding it needs four external inputs (the gitignored store, `scale_manifest.freq.json`, out-of-repo `csl-orig/v02`, out-of-repo `VisualDCS`) — **in a clean worktree it cannot be rebuilt at all**, so an overwrite is unrecoverable, not a rerun away. `gitignored` also means git can neither warn nor restore. **Implication:** a writer of a shared intermediate takes an `--out` parameter (default unchanged, so the standing lane is untouched) rather than a module constant; any non-default run passes it. Two smells that a "regenerable" label is stale: a hardcoded consumer that is not the writer, and an input the writer needs that a fresh clone does not have. See CONTRADICTIONS §15 for the two audits that grade this same file oppositely.

> **Source:** [reports/H3627_TM_MIRROR_REFRESH_REINGEST_QUEUE_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3627_TM_MIRROR_REFRESH_REINGEST_QUEUE_28-08-2026.md)
> · H3627 (Opus 5 `claude-opus-5`). — SanskritLexicography · 2026-08-28

### §593. A store write that removes rows leaves the TM mirror serving exactly what you just removed

🔴 **The `pwg-ru-data/tm/` mirror is a copy of the canonical store, so every store write that *deletes* rows opens drift a later `--tm=auto` run silently converts back into the defect you repaired.** **Evidence:** two independent passes left the same debt unpaid and both flagged it in prose — [H2996](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H2996_WRONG_ENTRY_QUARANTINE_REINGEST_28-08-2026.md) quarantined 159 wrong-entry rows ("Refreshing the mirror is owed and not done here"), and the H3593 `dA` requeue retranslated two subcards ("the mirror is now stale by these rows and still needs its own refresh"). Measured together at H3627: `audit_store_gates.py` `only_mirror` **167** — 159 quarantined + 2 old-key `durg_a~~h0_zz_sch` + 6 superseded `dA`. A window run with `--tm=auto` would have re-served precisely the cards H2996 had just quarantined. **Implication:** the refresh belongs in the same pass as the store write, not in a follow-up handoff — [`src/refresh_tm_mirror.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/refresh_tm_mirror.py) is the tool and `audit_store_gates.py`'s `only_mirror` is the check that the debt is paid. **A refresh is a copy, so guard it:** the risk is copying *away* a mirror-only row that is wanted. Byte-equality of `ru` is too strict a survivor test — id churn (a re-parse that moves `sense_tag` or edits `de`, both of which feed the row id) is indistinguishable from real loss by that test alone. Adjudicate the residue row by row into a committed ack file and keep the guard live, rather than passing `--force` and spending the guard on a single run.

> **Source:** [reports/H3627_TM_MIRROR_REFRESH_REINGEST_QUEUE_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3627_TM_MIRROR_REFRESH_REINGEST_QUEUE_28-08-2026.md)
> · H3627 (Opus 5 `claude-opus-5`) · [pwg-ru-data `5346cba`](https://github.com/gasyoun/pwg-ru-data/commit/5346cba). — SanskritLexicography · 2026-08-28

### §594. A repair pass must query EVERY shipped resolver, not just the one its rule names — H2877 reverted five rows to German that shipped code already answered

🔴 **A deterministic repair is only as complete as the set of resolvers it consults, and "my rule found nothing" is not "no answer exists".** [H2877](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2877-Opus_RussianTranslation_pwg-tm-w1-serious-error-10-repair_16.08.26.md) repaired the 10 serious-error rows of the H2684 gate with a rule (R2) that queried the exact-source lexicon and, on a miss, reverted the span to its German source. **Evidence:** for `{%Jmd%}` the lexicon miss was *correct* — the span is denylisted by `SHORT_GLOSS_DENYLIST` precisely because reusing it is unsafe — but a different shipped resolver already held the right answer: [H3299](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3299-Fable_SanskritLexicography_pwgtm-wave2-regenerate-regate_22.08.26.md) added `PLACEHOLDER_RU` / `placeholder_ru()` to [`src/pwg_tm_generate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_generate.py) on 24-08-2026, pinning `Jmd`→«кто-л.» for exactly this argument-slot class. H2877 ran three days later and never called it. Cost: 5 of the 10 rows (`arTay`, `krand`, `saYj`, `gam`, `vid`) carried German instead of correct Russian, which [H3611](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3611-Opus_RussianTranslation_pwg-tm-w1-serious10-rescore_28.08.26.md) then measured as a fidelity-floor break (99.50 %→97.25 %, FAIL). Calling the shipped table in [H3628](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3628-Opus_RussianTranslation_pwg-tm-w1-serious10-translate_28.08.26.md) scored all five `none`/`fidelity: pass` and moved the projected gate to a full three-floor PASS. **Implication:** before a repair rule falls back to any degraded outcome — revert, quarantine, "unfilled" — enumerate the module's *other* resolvers for the same input shape and try each; a denylist that blocks one path exists to route around it, not to end the search. Denylist and lookup table are complements, and the fallback belongs after both. Same failure family as §590 (a fence mistaken for coverage), one layer up: there a table was over-trusted, here a table was never consulted.

> **Source:** [pwg_ru/PWG_TM_W1_SERIOUS10_TRANSLATED_GATE_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TRANSLATED_GATE_28-08-2026.md)
> · [H3628](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3628-Opus_RussianTranslation_pwg-tm-w1-serious10-translate_28.08.26.md)
> (Opus 5 `claude-opus-5`) · [PR #1922](https://github.com/gasyoun/SanskritLexicography/pull/1922). — SanskritLexicography · 2026-08-28

### §595. A liveness watchdog is only meaningful against a STREAMING output format — arming one on a buffered spawn kills the healthy calls, not the hung ones

🔴 **"No output for N seconds" means a spawn is dead only if that spawn was ever going to speak before it finished.** A no-output-progress watchdog is the correct remedy for the H2313 problem that a total-wall ceiling cannot separate a hung call from a slow one — [`execution_contract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py) names it as residual work in the `PRODUCTION_HARD_TIMEOUT_MS` comment. But the window measures nothing unless the spawn emits incrementally, and **every paid lane in this tree fails that precondition**: `headless_worker`, `max_account_orchestrator._probe_call` and `gen_opt_harness2` all run `claude -p --output-format json`, which buffers the entire CLI result envelope and writes it in ONE burst when the call finishes. **Evidence:** under that format a healthy card spawn produces **0 stdout bytes for its whole duration**, and H2313 measured that duration at **49 404-511 908 ms (p50 189 327, p90 276 521)** across 16 completed spawns. The 90 000 ms window [H2878](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2878-Opus_RussianTranslation_pwg-c1-no-output-progress-watchdog_16.08.26.md) specifies would therefore have killed essentially every healthy call — the identical defect H2313 diagnosed in the 300 000 ms ceiling ("killing HEALTHY card spawns, not hung ones"), roughly six times more aggressive, and shipped as the *fix* for it. **Implication:** derive the window from the spawn's declared output format instead of pinning a literal at each call site — `progress_window_ms_for('json')` → `None`, `('stream-json')` → 90 000 ms. That leaves the buffered lanes **observe-only** — they still record `bytes_seen` and `quiet_ms`, which is what turns the eventual arming decision into a measurement rather than a bet — and makes a lane that adopts `stream-json` arm the watchdog by doing so, with no way to arm one against a buffered format by copying a constant. **The general rule, beyond this pipeline:** before shipping any bound of the form "no X for N seconds", verify that a HEALTHY instance of the watched thing actually produces X *while running*. `bytes_seen` on a **successful** call is the cheap check — if it stays 0 until the very end, the window has nothing to observe and can only fire on the healthy. Same family as §590: a guard installed without first confirming it can see the quantity it claims to guard. **MEASURED 28-08-2026 (no longer a derivation):** a live c1 probe pair, both `success`, both well inside their ceilings, spent **96.8 %** (20 083 of 20 754 ms) and **94.4 %** (13 774 of 14 587 ms) of their wall clock producing zero result bytes, with `bytes_seen` equal to `output_bytes` in both rows — every byte in one terminal burst. At that silent share a healthy CARD spawn at H2313's p50 of 189 327 ms sits silent for roughly **180 s, twice the 90 000 ms window**: arming it would have killed the median healthy call, not a marginal one. Series: [pwg_ru/h2878/H2878_C1_PROBE_EVENTS_28-08-2026.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2878/H2878_C1_PROBE_EVENTS_28-08-2026.jsonl). The reading is evidence and stays evidence — it measures the CLI's output SHAPE, not a latency budget, and no constant may be derived from it.

> **Source:** [pwg_ru/h2878/H2878_NO_OUTPUT_PROGRESS_WATCHDOG_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2878/H2878_NO_OUTPUT_PROGRESS_WATCHDOG_28-08-2026.md)
> · [H2878](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2878-Opus_RussianTranslation_pwg-c1-no-output-progress-watchdog_16.08.26.md)
> (Opus 5 `claude-opus-5`) · issue #1680. — SanskritLexicography · 2026-08-28

### §596. A pwg_ru window discards every paid success when one mid-window call fails schema validation

🔴 **`headless_worker` holds results in memory and writes `--output` only on clean completion, so a single `structured_output_retry_exhausted` late in a window throws away every card already paid for.** **Evidence (H3627, 28-08-2026):** a 23-key window ran 50 minutes, made **20 priced calls with 19 successes**, then exited 1 at batch `b13` (`_sr_avaka`) on the CLI's `terminal_reason: structured_output_retry_exhausted` ("Failed to provide valid structured output after 5 attempts"). `out.h3627.json` was never written and **no per-batch intermediate exists anywhere on disk**, so 13 completed headwords were billed and discarded; the store stayed at 11 462 rows. Token cost of the discarded work: 266 739 output / 600 653 cache-creation / 1 754 675 cache-read. **Implication:** never size a large window on projected cost alone — the risk is not mean cost per card but the **variance of total loss**, which scales with window length. The deferred 38-key "monster" lane at ~$409 carries identical all-or-nothing exposure at 45× the price. Two cheap fixes make windows resumable: persist each batch's result as it succeeds, and treat `structured_output_retry_exhausted` as park-and-continue rather than window-fatal — `gen_opt_harness2.parked_queue` already implements that shape for missing inputs. The same schema-validation failure family produced the 25-07 gate NO-GO and the H3361 `vivAda` spawn-state defect.

> **Source:** [reports/H3627_C1_WINDOW_ATTEMPT_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3627/H3627_C1_WINDOW_ATTEMPT_28-08-2026.md)
> · H3627 (Opus 5 `claude-opus-5`). — SanskritLexicography · 2026-08-28

### §597. `cost_evaluable: false` is a pipeline attribution gap, not absent price data — the CLI envelope carries real dollars

🔴 **Do not report a pwg_ru run as "unpriced" or, worse, as costing zero: `usage_evaluable` and the per-call CLI envelope can both be true while `cost_evaluable` is false.** **Evidence (H3627):** a window whose usage block read `observed_cost_usd: 0.0, cost_evaluable: false` also read `usage_evaluable: true, priced_calls: 20, missing_usage_calls: 0`, and the failing call's own envelope reported `total_cost_usd: 0.4131022`, itemised `claude-sonnet-5 $0.4001562` + `claude-haiku-4-5 $0.012946` with `cache_creation.ephemeral_1h_input_tokens: 39265`. Scaling that single real data point by the run totals put the window at **~$5-6**, independently corroborating `perf_preflight.py`'s ~$5.08 projection for the same keys. **Implication:** the preflight is trustworthy for sizing; it is the actual-cost *plumbing* that is blind, and the fix is to lift `total_cost_usd` out of the envelope rather than call the lane unpriceable. Two reporting rules follow: **"unevaluable" is never "zero"** (a missing figure and a measured $0 are different claims — an earlier draft of this very handoff published a reader bug as a verified zero), and **cache-creation is reported separately from cache-read** — creation bills ~20× read and dominates, while the `ephemeral_1h` vs `_5m` bucket distinguishes "prefix unstable" from "cache expired".

> **Source:** [reports/H3627_C1_WINDOW_ATTEMPT_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3627/H3627_C1_WINDOW_ATTEMPT_28-08-2026.md)
> · H3627 (Opus 5 `claude-opus-5`). — SanskritLexicography · 2026-08-28

### §598. A durable-evidence-root guard only protects the target it is called on — a sibling constant that never runs through the resolver can still split silently

🟠 **A refusal wired onto ONE resolved path does not protect a SECOND write target unless that target is derived from the same resolution.** [#1034](https://github.com/gasyoun/SanskritLexicography/issues/1034) taught `h963_c4_gate0_probe.resolve_evidence_root` / `assert_durable_evidence_root` to route the per-account probe-events series through an explicit `--evidence-dir` / `$PWG_EVIDENCE_DIR` / checkout-relative-default precedence, and to REFUSE a paid run whose resolved root sits inside a disposable git worktree — closing the class where a session's own append-only evidence dies with its checkout. **Evidence (H2878, 28-08-2026):** a c1 GATE-0 PASS ran with an explicit `--evidence-dir`; the guard correctly validated that root, and the per-account events series landed there durably. But `max_account_orchestrator.HEALTH_PROBE_LOG` — the canonical CROSS-ACCOUNT log every probe call also writes, added by H2240 — was a plain module-level constant computed once at import time from `os.path.dirname(__file__)`, wired to nothing the resolver produced. The guard that ran was checking the events path, not this one, so its PASS said nothing about where the canonical row would land: it landed in the disposable worktree and never reached the checked-out repo, silently. **Implication:** when a fix adds a durable-root resolver + refusal for one write target, audit every OTHER target the same call graph writes to before declaring the class closed — a second constant that merely happens to look similar (same directory, same file family) is not covered by construction just because it sits nearby in the source. The fix (H3642) makes the second target LITERALLY DERIVE from the first target's resolved root (`resolve_health_probe_log(explicit_root)`, called with the exact value `resolve_evidence_root` produced) rather than adding a parallel, independently-maintained resolution — collapsing "two targets that must be kept in sync by hand" into "one root, two filenames" removes the drift surface rather than merely re-checking it. A defense-in-depth assert on the derived target is cheap insurance against a FUTURE change re-introducing the split, but the real fix is eliminating the second independent resolution, not doubling the guard count.

> **Source:** [pwg_ru/h2878/H2878_NO_OUTPUT_PROGRESS_WATCHDOG_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2878/H2878_NO_OUTPUT_PROGRESS_WATCHDOG_28-08-2026.md) (residual 2)
> · [PR #1936](https://github.com/gasyoun/SanskritLexicography/pull/1936) · H3642 (Sonnet 5 `claude-sonnet-5`). — SanskritLexicography · 2026-08-28
