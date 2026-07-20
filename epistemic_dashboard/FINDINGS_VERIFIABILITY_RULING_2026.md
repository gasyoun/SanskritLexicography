# FINDINGS verifiability ruling — the re-derivability class of every finding

_Created: 20-07-2026 · Last updated: 20-07-2026_

Ruling for [H1362](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1362-Opus_SanskritLexicography_findings-rederivability-class-and-staleness-verifiability-axis_20.07.26.md) (Opus 4.8 `claude-opus-4-8`). It gives the epistemic-registry family the one axis it lacked: **whether, and how, each [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) finding can be re-verified.** Until now every finding was cited with equal authority — a number that recomputes from committed code in one command sat beside a figure whose underlying data was never committed. This ruling separates them.

Its machine-readable companion is [`verifiability.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/verifiability.json) (keyed by finding number); it drives the **Re-check recipe** column of [STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md) and the `verifiability` block of the [epistemic dashboard](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/index.html). It is the re-derivability sibling of the [citation-identity ruling](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) (which governs the §-number as a citation key); this one governs the §-number as a *reproducibility claim*.

## 1. The four classes

Every finding is exactly one of:

- **A — auto-reproducible.** A committed script plus committed, manifest-registered, or deterministically regenerable data reruns the finding. The number is reproducible in principle by anyone with repo + manifest access. This is the bulk of the registry.
- **B — re-probeable.** Re-verifying needs a **live external host, API, or site** whose state can move between runs — VedaWeb, CDSL, Heritage, GRETIL, DharmaMitra, a Zenodo DOI, a bank/scan endpoint. The finding is a snapshot of something outside the repo; a re-run is a fresh probe, not a rerun of committed inputs.
- **C — historically fixed.** A dated correspondence, a print/publication fact, or a standing scholarly conclusion (including a bibliographic negative — "no such resource exists"). No committed script re-derives it and no probe decays it; it changes only if the scholarly record itself changes.
- **D — not reproducible as stated.** The method, ledger, intermediate, or figure was never committed in recoverable form, or was invalidated. A fresh session hits a dead end: a hand-transcribed ledger that swaps its own denominator, a subset whose audit contract failed, a figure that was never actually measured. **This is the class the registry most needed to name** — a D finding must not be cited as if it were an A.

### The A/D boundary (the load-bearing distinction)

D is reserved for **evidentiary-integrity failure**, not mere storage inconvenience. A finding whose input is a real, regenerable, rights-restricted or large *local* asset (a gitignored translation store, the single-copy `corpus_lexicon.jsonl`, the 920 MB DCS sqlite) is still **A** — the method is committed and the asset holder can rerun it deterministically — but flagged **·R (restricted input)** so a third party knows it is not runnable without that asset. D is only for findings that *no one* can reproduce from any committed or registered artifact, because the evidence never existed in recoverable form. Script existence is **not** the test: §69's `classify_run.py` exists and the finding is still D, because the ledger it consumed was local-only and its denominator is unrecoverable.

## 2. Citation rule for class D (now in the FINDINGS schema)

**A class-D finding must be cited with its non-reproducibility named** — never as a bare `§N` carrying the same authority as an auto-reproducible row. The FINDINGS schema paragraph now carries this sentence, and the three D rows are marked in place. The point is not to strike them (each records a real lesson) but to stop them being *load-bearing* under a citation that implies they recompute.

## 3. Counts — the honest denominator

**114 distinct findings** (post-[H1361](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1361-Opus_SanskritLexicography_findings-section-number-collision-ruling-and-dashboard-audit_20.07.26.md) citation-identity ruling **and** the H1350×H1361 §448–451 collision resolved by this pass — see the ruling doc §6, which renumbered the H1350 PWG block to §452–455). The earlier published boards read 77 (a 12-07 regeneration frozen while the file grew) and 109 (H1361, before the §452–455 split); neither is the true count now.**

| Class | Count | Share |
|-------|-------|-------|
| **A** auto-reproducible | 95 | 83.3% |
| **B** re-probeable | 12 | 10.5% |
| **C** historically fixed | 4 | 3.5% |
| **D** not reproducible | 3 | 2.6% |
| **Total** | **114** | 100% |

Of the 95 class-A findings, **7** carry a restricted local input (·R): §13, §58, §65, §70, §78, §84, §454.

## 4. Method

Each finding was adjudicated from its own `> **Source:**` blockquote (the cited script / dataset / probe), not from its prose claim. For every class-A finding the **primary cited script was checked to actually exist** — `git ls-tree` over this repo and the sibling repos it names (WhitneyRoots, VisualDCS, csl-atlas, SanskritGrammar, kosha, sanskrit-util, Uprava, SamudraManthanam, SanskritSpellCheck, MWS, csl-pywork, csl-orig). All 94 resolved to a real committed file; the `script_exists` column in `verifiability.json` records the outcome per row. A missing script would have forced a downgrade — none did.

## 5. The per-finding table

`Re-check path`: for class A, the [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) row that reproduces it, else its own primary script (never `§TBD`). For B, the host to re-probe. For C/D, why it does not rerun. `·R` marks a restricted local input.

| § | Class | Re-check path | Script ✓ | Claim |
|---|-------|---------------|----------|-------|
| [§1](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Whitney accent-mobility rules are machine-encodable |
| [§2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Homonym token-splitting has a hard morphological ceiling |
| [§3](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | The Warnemyr scrape union-smears homonym classes |
| [§4](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | PWG nominal grammar compresses into 335 paradigm tokens |
| [§5](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `_pilot_gen_merged.py` | ✓ | The parallel corpus rarely attests prefixed-verb forms |
| [§6](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **C** | C · fixed (no decay) | — | No printed frequency dictionary of Sanskrit exists |
| [§7](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `freq_route.py` | ✓ | DCS lemma data is keyed in two transliterations |
| [§8](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Unaccented DCS cannot distinguish present class I from VI |
| [§9](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | DCS OccId and sent_id are not unique keys |
| [§10](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | DCS UD tense marking conflates aorist and perfect |
| [§11](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `delta_annotation_layers.py` | ✓ | DCS 2021 and 2026 vintages are not directly comparable |
| [§12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | RECIPES §2 | ✓ | A fifth of DCS lemmas have no CDSL headword |
| [§13](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Sa-Ru glossary token coverage plateaus at 86.6 percent |
| [§14](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `renou_pipeline.py` | ✓ | Renou period-state tagging covers 770k entries in 8 dicts |
| [§15](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `root_segment_proto.py` | ✓ | PWG encodes secondary stems inline, not in div markup |
| [§16](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `_pilot_gen_merged.py` | ✓ | Giant verb roots sit at non-zero homonym indexes |
| [§17](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `analyze_sense_order.py` | ✓ | PWG orders senses genetically, not historically |
| [§18](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `analyze_cross_dict.py` | ✓ | Vedic-citation density separates the dictionary traditions |
| [§19](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | SKD and VCP carry essentially zero Western markup |
| [§20](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `analyze_sense_order.py` | ✓ | The ls source map recognises 72.4 percent of PWG citations |
| [§21](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `build_citation_index.py` | ✓ | PWG citation occurrences track distinct references |
| [§22](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | MW has no sense-level div markup |
| [§23](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Apte is three dictionaries; keys differ stem vs nominative |
| [§24](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | About 9 percent of typo corrections are collisions |
| [§25](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | A verified correction queue decays against live csl-orig |
| [§26](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Citation density is register-bound, not comparable raw |
| [§27](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Sense granularity is a family trait, not a diachronic trend |
| [§28](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `f5_entry_comparison.py` | ✓ | MW inherited the PWG apparatus skeleton, not its prose |
| [§29](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | RECIPES §5 | — | PWG and MW share 94,753 headwords in the union index |
| [§30](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Body-text headword mining is a dead end (38.6 percent precision) |
| [§31](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Detector precision stratifies by digitization quality |
| [§32](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Correction events concentrate in sense text |
| [§33](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Indigenous dictionaries agree on derivation; Wilson is the outlier |
| [§34](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | The E abbreviation tag is polysemous across dicts |
| [§35](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `build_root_normalization.py` | ✓ | Root-recovery tiers err on root form, not identity |
| [§36](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `__init__.py` | ✓ | IAST Unicode collides and normalises lossily |
| [§37](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | BOM state is inconsistent across exports |
| [§38](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `hw.py` | ✓ | Injected BOMs crash the hw record parser |
| [§39](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `__init__.py` | ✓ | devanagari_to_slp1 mis-routes retroflex la |
| [§40](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Gloss-language spelling drift tracks reform type, not age |
| [§41](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe live dictionary platforms | — | The Sanskrit dictionary-platform landscape, probed live |
| [§42](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Whitney self-contradicts on derivative ī-stem gen.pl accent |
| [§43](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | SKD/VCP sense/citation fusion is a record-type effect, not a dictionary-level one |
| [§44](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Raw Latin-string tallies over gloss text include etymological false positives; Bopp lacks √yabh |
| [§45](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Siglum prefix-families routinely bundle several distinct works; the diacritic-stripping fold has poisoned keys |
| [§46](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Twelve years of corrections cover only ~10–14 % of the estimated error population |
| [§47](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe Heritage GitLab/GitHub mirror | — | Heritage data is acquirable despite the Anubis wall — via a GitHub mirror; the morphology XML is not in it |
| [§48](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe VedaWeb 2.0 API | — | VedaWeb 2.0's resource export is an async task behind a pickup-key, not a direct GET — and the server went unresponsive  |
| [§49](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe Heritage site HTML | ✓ | MW↔Heritage coverage highlighting is a duplicate-anchor pattern, not a CSS class — and the mirror's "current" dictionary |
| [§50](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe CDSL display paths | — | CDSL display paths are NOT uniformly `/2020/web/` — and two new digitizations landed in June 2026 |
| [§51](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **C** | C · fixed (no decay) | — | Huet correspondence predates this session (2021) — the morphology-XML "gate" was already resolved in writing; direct dow |
| [§52](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `heritage_forms_oracle.py` | ✓ | Heritage vs kosha forms diff: the small raw overlap is mostly convention + model difference, and "disagreements" are two |
| [§53](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `stats_etymology.py` | ✓ | The WIL etymology extraction's affix field is ~half noise — Wilson "outlier" figures are substantially a measurement art |
| [§54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | RECIPES §1 | — | Whitney accent axis validates at 17/19 matrix cells GO against attested RV accents |
| [§55](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `gen_opt_harness2.py` | ✓ | `gen_opt_harness2.py` output-budget: coarser wins on both knobs, in opposite directions |
| [§56](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe Heritage DICO HTML | — | DICO's entry anchors nest three structural roles under one HTML class — only one is a true entry boundary |
| [§57](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe samskrtam.ru/z/ | ✗ | samskrtam.ru/z/ is id-addressed with no name lookup — deep-linking needs a scraped root→id table; 8 primer-basic roots a |
| [§58](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `audit_translation_provenance.py` | ✓ | PWG-RU promoted store has input-level provenance, but old RU rows lacked exact model versions |
| [§59](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **C** | C · fixed (no decay) | — | Böhtlingk's *Indische Sprüche* (both editions) already fully digitized in `sanskrit-lexicon-scans`, not just `sanskrit-l |
| [§60](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **C** | C · fixed (no decay) | ✓ | Practical Russian transcription of Sanskrit names has no safe reverse transliteration |
| [§61](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | The reverse dictionary's 30 sources split ~18 PD vs ~10 in-copyright — the merged headword list is not automatically pub |
| [§62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | RECIPES §4 | ✓ | Varga distribution is almost epoch-stable (Cramér's V = 0.037) — and the Gasūns-2014 dissertation prose read its own χ²  |
| [§63](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | vidyut dhātupāṭha adjudicates the 2014 Palsule-exclusion dispute: five añc dhātus, no and, but ast IS Paninian |
| [§64](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `dict_merge.py` | ✓ | PW-only headwords outnumber PWG-only ones 6-to-1 — PWG is not the sole spine of the local layer universe |
| [§65](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | RECIPES §3 | ✓ | 6.6 % of the DeepSeek corpus word-alignments ground to nothing in their verse |
| [§66](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `__init__.py` | ✓ | The DCS `QL` frequency workbook's `SLP1` and length columns are truncated at ṣṭh/ḍh clusters |
| [§67](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | RECIPES §7 | ✓ | In PWG, article size dwarfs every "parametric" statistic you can extract from the entry |
| [§68](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe external spellchecker projects | — | The Sanskrit spellchecker landscape: one dormant demo, one license-unsettled 543k wordlist, no occupant |
| [§69](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **D** | D · not reproducible | ✓ | Hand-transcribed telemetry cannot adjudicate code-vs-infra — and a local-only ledger silently swaps your denominator |
| [§70](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `tm_grade.py` | ✓ | pwg_ru TM composite grade: A is consensus-gated (5.7%), and a reference-free surface QE cannot detect wrong-sense |
| [§71](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | RECIPES §8 | ✓ | PWG marks case government explicitly ≈3,853 times across ≈3,222 senses — a deterministic census, not an estimate |
| [§72](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | VedaWeb's `id_gra` token field IS the Grassmann `<L>` entry number — no fuzzy text-matching needed for a GRA↔VedaWeb cro |
| [§73](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | VedaWeb 2.0's "CC BY 4.0 for everything" claim is not machine-confirmed — only 2/36 catalog resources carry an explicit  |
| [§74](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | The ls-graph citation matrix is degenerate for MW — its top abbreviations sit unresolved; use the citation-apparatus sig |
| [§75](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe GRETIL / sanskritdocuments.org | ✓ | The full Devībhāgavata-purāṇa Sanskrit is NOT on GRETIL — only the Devigita fragment; the complete mūla lives on sanskri |
| [§76](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | The MW→WordNet→semdom bridge is a candidate generator, not a classifier |
| [§77](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `semdom_ak_annex_table.py` | ✓ | Amarakosha and SIL semdom both bolt a formal annex onto a semantic taxonomy — and it is the same ~10% once polysemy is s |
| [§78](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | DCS 2026 sqlite carries 531,747 sense-annotated tokens (`m_wordsem`) but NO local ID→gloss inventory — gold-scored WSD a |
| [§79](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `delta_supplement.py` | ✓ | DCS 2021→2026 "lost lemma" counts are mostly lemmatization-policy drift — a-privatives now resolve to their bases |
| [§80](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `nkrya_annotate.py` | ✓ | DCS `text_sandhied` is largely DE-sandhied pada text in the Rāmāyaṇa — and locus joins fail across editions; a text-keye |
| [§81](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | vidyut-cheda 0.4 lemmatizes derivatives to the dhātu ROOT (rāmaḥ → ram) where DCS uses the nominal stem — and over-segme |
| [§82](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `build_entry_anatomy.py` | ✓ | MW `<e>` encodes the 1899 print's headword typography (1 = Devanāgarī entry, 2 = roman-only, 3 = run-on compound; letter |
| [§83](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `f9_shared_omission.py` | ✓ | MW and the Petersburg dictionaries are NOT independent witnesses on inventory or apparatus — do not count their agreemen |
| [§84](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `stage2_pregate.py` | ✓ | pwg_ru readiness audit: `[NWS:]` attribution and `{%…%}`-delimiter dropping are NOT audit-contract defects; observed tok |
| [§85](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **D** | D · not reproducible | ✓ | A clean-looking subset is not promotable evidence when its audit or execution contract failed |
| [§86](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `period_style_gradient.py` | ✓ | DCS verbal-feature annotation density collapses for later texts — feats-based diachronic metrics measure ANNOTATION, not |
| [§87](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `period_style_gradient.py` | ✓ | A curated DCS text→period map EXISTS (consume, don't rebuild) — and the purāṇas carry a measured epic-imitative signatur |
| [§88](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | The DCS snapshot's UD dependency slice is real but VEDIC-SKEWED — syntax studies get counterexample hunts, not classical |
| [§89](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | RECIPES §9 | ✓ | MW writes `<ls>` citations in TWO markup shapes and locates them in roman as well as arabic — a literal `<ls>` regex und |
| [§90](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | A spelling-keyed join onto Whitney's roots union-smears homonyms — one authorial entry lands on every homonym of that sp |
| [§91](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `whitney_aorist_tagger.py` | ✓ | DCS has no aorist TENSE value — `feat_tense='Past'` lumps aorist with the perfect; `feat_formation` is what actually sep |
| [§92](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | A verified claim register is not Whitney-proof — 3 of 229 erdict_fact: TRUE rows in Kochergina claims.yml contradict Wh |
| [§93](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Declared, validated, and never enforced — the PWG headless executor read a manifest `budgets{}` block it did not obey, a |
| [§94](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | kosha's generated `forms` is 93% DCS-derived, so its attested-form join is a round-trip — only the vidyut-engine subtota |
| [§95](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe DharmaMitra API | ✓ | DharmaMitra `unsandhied` batches return MISALIGNED results on short inputs — doubled echoes and other texts' tokens — so |
| [§96](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `test_converter.py` | ✓ | SamudraManthanam's generated full-corpus JSONL has 38,288 duplicate canonical-ID groups, concentrated in `devibhagavata- |
| [§97](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `build_census.py` | ✓ | Cross-dictionary attestation via Monier-Williams overstates independence — MW was compiled *from* Böhtlingk-Roth (PW/PWG |
| [§98](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | PD's inline sigla contain a near-homograph pair that similarity-clustering silently fuses — `MahāBhā.` is the Mahābhārat |
| [§99](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `ru_style_sweep.py` | ✓ | Output gates must audit structured semantic fields, and sample-clean editorial rewrites still require a full-population  |
| [§100](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `buhler_provenance.py` | ✓ | `nfold` earns sandhi-tolerant recall by fusing every nasal to `n` — which manufactures false quotation matches unless ev |
| [§101](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `build_samasa_ladder.py` | ✓ | DCS's compound dictionary carries splits whose member **order** does not match the surface form — invisible to a type-dr |
| [§102](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `buhler_provenance.py` | ✓ | DCS `sentence.text_sandhied` is not reliably sandhied — some rows store analyzed word forms, which silently downgrades v |
| [§103](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `witness_independence_reaudit.py` | ✓ | Quantified: the §83/§97 witness-collapse deflates the published 15-dict union "corroboration" from 55.9% to 34.7% — and  |
| [§104](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `aggregate_dcs_gov.py` | ✓ | The DCS `dcs-conllu` treebank is only ~3.9 % dependency-parsed — corpus government/valency work must lean on co-occurren |
| [§447](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `microstructure.py` | ✓ | PWG's own closing sense-marker glyph "〉" was never recognized by the sense-splitter — ~50% of German senses were silentl |
| [§448](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe MWScan/2020 servepdf.php endpoint | ✓ | CORRECTED — the MWScan/2020 `servepdf.php` endpoint is RIGHT (serves 1899); the 1872 first-edition scan coexists on the  |
| [§449](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · self (see Source) | — | Samāsa-type frequency does not exist in any org corpus — and the grammarians' canonical examples are corpus-ghosts (8/58 |
| [§450](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **D** | D · not reproducible | — | The roadmap's "OBS-T κ=0.42" was a phantom figure — no measured agreement exists for any OBS-T axis |
| [§451](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **B** | B · re-probe Zenodo DOI resolution | — | `10.5281/zenodo.15834721` is a false DOI, cited as genuine in two different repos |
| [§452](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `validate_pwg_markup.py` | ✓ | csl-atlas's PWG parse-rules census is stale and incomplete — 21 real markup tags missing, several listed counts wrong |
| [§453](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `microstructure.py` | ✓ | PWG's sense-closing glyph "〉" nests FOUR enumeration tiers, not two — Greek letters and roman-numeral markers are unreco |
| [§454](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `audit_sense_glyph.py` | ✓ | The pwg_ru RU store's `h` field has inconsistent semantics — not a reliable homograph-number join key |
| [§455](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `pwg_sources.py` | ✓ | PWG `<ls>` citation resolution is already at 98%+, far above the previously-cited 72.4% baseline |
| [§456](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | **A** | A · `build_uttarapada_dict_vs_corpus.py` | ✓ | MW's derivation markup and the DCS corpus are productive over the *same* compound final members but with near-disjoint f |

## 6. What consumes this

- [STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md) — the **Re-check recipe** column is now filled from `verifiability.json` (zero `§TBD` in the class-A set), and the snapshot counts the true 114-finding denominator.
- [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) — three new rows (§7 →§67, §8 →§71, §9 →§89) mint reproduction paths for high-value class-A findings that had none.
- [epistemic dashboard](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/index.html) — a `verifiability` block renders the A/B/C/D split beside the staleness board.
- [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — the schema paragraph carries the class-D citation rule; the D rows are marked.

_Dr. Mārcis Gasūns_

