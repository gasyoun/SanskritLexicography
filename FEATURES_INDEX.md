# FEATURES_INDEX.md — what the Sanskrit Lexicon project actually has

_Created: 04-07-2026 · Last updated: 04-07-2026_

**Purpose.** A clickable, capability-first map of the working assets across the ~85
repositories: the **dictionaries** digitised, the **interfaces** that serve them, the
**data** already computed, and the **tools** you import rather than re-type. Where its
companion [`REUSE_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md)
answers *"don't rebuild — consume this"*, this file answers *"what exists at all?"* — the
inventory a newcomer (or a fresh session) reads to see the shape of the whole.

- **Interactive view:** a filterable single-file HTML artifact renders this same catalogue
  (full-text search + category tabs + per-section status/language filters). Local/shared
  artifact only — not committed here.
- **Code-level "who owns this":** [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md).
- **Data-flow "who feeds whom":** [`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md).

> Sizes and counts are approximate; re-verify against a source repo before a large change.
> Some linked repos are private ([`github-spine`](https://github.com/gasyoun/github-spine),
> [`Uprava`](https://github.com/gasyoun/Uprava)).

**At a glance:** 44 dictionaries · 20 interfaces (16 live) · 37 data assets · 14 tools · 4 external stacks.

**Status key** — 🟢 **Live** deployed & reachable · 🟡 **Beta / local** in development or
local-only · ⚪ **Source / library** a dataset, package or spine with no UI of its own.

---

## I. Data assets — query it, someone already spent the compute

### Sanskrit → Russian & translation

| Asset | What it is | Size | Home |
|---|---|---|---|
| `corpus_lexicon` | 1.09 M word-aligned Sa→Ru rows (per verse-pair, SLP1-keyed, ~190k keys). The alignment asset. | 1.09 M rows | [build_corpus_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py) |
| SanskritRussian glossary (3-layer) | Ranked Sa→Ru glossary: surface 190,838 · lemma 40,370 · root 2,021; 87% token coverage | 233k entries | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| `mw_en_tm.json` | SLP1-keyed MW English-gloss translation memory — the fuzzy-match TM behind the RU/EN kits | 187,506 · 12 MB | [RussianTranslation/src](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src) |
| lemma / root glossary (DCS) | DCS lemma→gloss and root→gloss glossaries, bilingual, TSV + JSONL | lemma 16–26 MB · root 5 MB | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |

### Roots & etymology

| Asset | What it is | Size | Home |
|---|---|---|---|
| `mw_roots.tsv` | MW verbal-root inventory: 2,113 records with explicit `verb_type` (750 genuineroot + 1363 root) | 2,113 · 76 KB | [csl-orig/v02/mw](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw_roots.tsv) |
| `mw_etymology.tsv` / `pwg_etymology.tsv` | Headword→root derivation tables (Pāṇinian), extracted across 10 dicts | ~9–11k rows each | [csl-orig/v02/mw](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw_etymology.tsv) |
| `etymology_stats` | Cross-dict aggregates: root_norm, root productivity oracle, 41-pair agreement matrix (95% CI), affix entropy/frequency | 10 dicts | [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02) |
| `etymology-oracle.json` | csl-atlas cross-dict etymology aggregator, consumed verbatim from `etymology_stats` | 67k rows · 23 KB | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) |
| `root_crosswalk.csv` + `class_concordance.csv` | MW ↔ Whitney root-class alignment + Whitney class concordance with frequency | 37 KB + 18 KB | [MWS/root_crosswalk](https://github.com/gasyoun/MWS/tree/main/root_crosswalk) |
| `Whitney_DCS_audit.json` | Whitney × DCS root audit — corpus attestation vs the 935-root Whitney hub | 415 KB | [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) |
| `corpus_class_verdicts.json` | Corpus-verified root-class verdicts. ⚠ unaccented DCS can't split class I vs VI | 514 KB | [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) |
| `dcs_ppp_verified.tsv` | 5,181 corpus-attested past-passive-participle forms + counts (confirms han→hata, dā→datta 1471×) | 5,181 forms | [VisualDCS](https://github.com/gasyoun/VisualDCS/tree/main/derived-data/Glagolnye-formy) |

### Headwords & crosswalks

| Asset | What it is | Size | Home |
|---|---|---|---|
| `union_headwords.tsv` | Cross-dict union headword index — every CDSL headword with per-dict provenance | ~323k | [HeadwordLists/union](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) |
| `mw_heritage_crosswalk.tsv` | MW → Sanskrit Heritage alignment: 185,803 MW entries, 25,140 Heritage-covered, 97.6% anchor-resolved | 185.8k · 3.2 MB | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv) |
| DCS↔CDSL crosswalk | DCS lemma ↔ CDSL headword linkset, 12,946 rows (81.4% linked) — reusable LOD linkset | 12,946 rows | [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/dcs_xref/dcs_cdsl_xref.tsv) |
| union `coverage_additions.tsv` | Headwords found beyond the core CDSL dictionaries | union | [HeadwordLists/union](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/union) |
| csl-atlas `alignment-confidence.json` | Per-pair cross-dict headword alignment confidence scores, sharded | 164 shards | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) |
| csl-atlas low-confidence review set | Alignments flagged below threshold for manual review | review set | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) |

### Heritage & morphology oracles

| Asset | What it is | Size | Home |
|---|---|---|---|
| `heritage_forms_oracle.tsv.gz` | Pandora → Heritage inflected-form alignment oracle, morphology-aware | 526 KB gz | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| `heritage_dico_gloss.tsv` | Heritage DICO lemma glosses — SLP1 / Devanāgarī / English | 24.5k · 4.4 MB | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| `heritage_forms_oracle_disagreements.tsv` | Cross-dictionary morphology disagreement audit | 20.5k · 1.4 MB | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| `heritage_only_forms.tsv` | Forms attested in Heritage but absent from MW/PWG/etc. | 29 MB | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| `heritage_mirror/DATA/` frequency tables | Heritage frequency & morphology corpus TSVs (pada_freq, comp_freq, comp_morph_freq, …) | 22 MB | [heritage_mirror](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/heritage_mirror) |
| `sanhw1.xlsx` (Sanskrit-Hybrid Word) | Catalan-Pujol Sanskrit-Hybrid Word master headword list | 61k · 40 MB | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |

### Frequency & corpus

| Asset | What it is | Size | Home |
|---|---|---|---|
| VisualDCS DCS ingest + lemma summary | Canonical CoNLL-U → SQLite build + `dcs_lemma_summary.json`. ⚠ UD Tense=Past conflates aorist/perfect | ~15.9k lemmas | [import_dcs_conllu.py](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/import_dcs_conllu.py) |
| kosha frequency layer | SLP1-keyed sidecar: whole-corpus counts + per-period vectors + core-vocab coverage (DCS M9) | 83,277 · 4.7 MB | [kosha/data/frequency](https://github.com/gasyoun/kosha/blob/main/data/frequency/lemma_frequency.tsv) |
| `dcs_form2lemma.tsv` | DCS form→lemma alignment, SLP1-keyed — backbone of surface-form resolution | 408k · 9.4 MB | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| `dcs_lemma2root.tsv` | DCS lemma → root mapping | 245 KB | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| `vidyut_form2lemma.tsv` | Stage-C fallback: forms DCS missed, resolved via the vidyut FST lexicon | 28.5k · 745 KB | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| `surface_dcs_misses.tsv` | DCS resolution-gap analysis — forms that failed DCS lookup | 6.6 MB | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| Zaliznyak grammar index | Compact Zaliznyak-style grammar tokens over all PWG: 98,639 headwords, 335 paradigm tokens; FAIR package | 98,639 rows | [headword_index.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv) |
| `correction_events_release.csv` | Correction event log: 50,953 events × 43 dicts × 210 correctors, 2014–2026 (pending Zenodo DOI) | ~52k · 59 MB | [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) |

### Text collections & other

| Asset | What it is | Size | Home |
|---|---|---|---|
| Indische Sprüche | All 7,537 Böhtlingk subhāṣitas as JSONL (public domain), with translation + metadata | 7,537 · 6.9 MB | [indische_sprueche.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl) |
| ortho-drift reform maps | 19th-c.→modern spelling maps: de 15,685 · ru 7,709 · fr 254 · en 71 (search-normalization asset) | ~23.7k forms | [SanskritSpellCheck/ortho_drift](https://github.com/drdhaval2785/SanskritSpellCheck/tree/master/ortho_drift) |
| do-not-file corpus | 2,297 deliberately non-standard headword spellings across 33 dicts | 2,297 | [do_not_file_suppress.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/nochange/do_not_file_suppress.txt) |
| csl-santam Tamil SQLite | Combined Tamil-facing lexicon: MW + Cappeller + Cologne Online Tamil Lexicon | 321,620 · 30 MB | [csl-santam](https://github.com/sanskrit-lexicon/csl-santam) |
| OCR'd dictionary front-matter | Faithful Markdown + EN/RU editions of title pages, prefaces, abbreviation lists per dict | multi-dict | [csl-guides](https://github.com/gasyoun/csl-guides) |

---

## II. Dictionaries — the 44 digitised from canonical source text

Roster from [`csl-guides/src/data/dictionaries.json`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/dictionaries.json),
verified against [`csl-orig/v02/`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02).
Dictionaries without a dedicated working repo live in `csl-orig` only.

| Code | Dictionary | Language | Author | Year | Pages | Repo |
|---|---|---|---|---:|---:|---|
| MW | Monier-Williams Sanskrit-English Dictionary | Skt→Eng | Monier-Williams | 1899 | 1,333 | [MWS](https://github.com/gasyoun/MWS) |
| PWG | Grosses Petersburger Wörterbuch | Skt→Ger | Böhtlingk & Roth | 1855 | 4,737 | [PWG](https://github.com/sanskrit-lexicon/PWG) |
| PW | Sanskrit-Wörterbuch in kürzerer Fassung | Skt→Ger | Otto Böhtlingk | 1879 | 2,141 | [PWK](https://github.com/sanskrit-lexicon/PWK) |
| GRA | Wörterbuch zum Rig-Veda | Skt→Ger | Hermann Grassmann | 1873 | 1,775 | [GRA](https://github.com/sanskrit-lexicon/GRA) |
| AP90 | Apte Practical Sanskrit-English Dictionary | Skt→Eng | V. S. Apte | 1890 | 1,196 | [AP90](https://github.com/sanskrit-lexicon/AP90) |
| AP | Practical Sanskrit-English Dictionary (rev.) | Skt→Eng | Apte · Gode · Karve | 1957 | 1,768 | [AP](https://github.com/sanskrit-lexicon/AP) |
| MW72 | Monier-Williams Sanskrit-English (1st ed.) | Skt→Eng | Monier Williams | 1872 | 1,186 | [MW72](https://github.com/sanskrit-lexicon/MW72) |
| WIL | Wilson Sanskrit-English Dictionary | Skt→Eng | H. H. Wilson | 1832 | 982 | [WIL](https://github.com/sanskrit-lexicon/WIL) |
| YAT | Yates Sanskrit-English Dictionary | Skt→Eng | Rev. W. Yates | 1846 | 928 | csl-orig only |
| GST | Goldstücker Sanskrit-English Dictionary | Skt→Eng | Theodor Goldstücker | 1856 | 334 | csl-orig only |
| BEN | Benfey Sanskrit-English Dictionary | Skt→Eng | Theodore Benfey | 1866 | 1,145 | [BEN](https://github.com/sanskrit-lexicon/BEN) |
| LAN | Lanman's Sanskrit Reader Vocabulary | Skt→Eng | C. R. Lanman | 1884 | 403 | csl-orig only |
| LRV | Vaidya Sanskrit-English Dictionary | Skt→Eng | L. R. Vaidya | 1889 | 889 | [LRV](https://github.com/sanskrit-lexicon/LRV) |
| CAE | Cappeller Sanskrit-English Dictionary | Skt→Eng | Carl Cappeller | 1891 | 672 | [CAE](https://github.com/sanskrit-lexicon/CAE) |
| MD | Macdonell Sanskrit-English Dictionary | Skt→Eng | A. A. Macdonell | 1893 | 384 | [MD](https://github.com/sanskrit-lexicon/MD) |
| SHS | Śabda-Sāgara Sanskrit-English Dictionary | Skt→Eng | J. Vidyasagara | 1900 | 839 | [SHS](https://github.com/sanskrit-lexicon/SHS) |
| PD | Encyclopedic Dictionary of Sanskrit on Historical Principles | Skt→Eng | Ghatage · Bhatta | 1976 | 4,328 | [Cologne scan ↗](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/web/index.php) |
| MWE | Monier-Williams English-Sanskrit Dictionary | Eng→Skt | Monier Williams | 1851 | 860 | csl-orig only |
| BOR | Borooah English-Sanskrit Dictionary | Eng→Skt | Anundoram Borooah | 1877 | 772 | [BOR](https://github.com/sanskrit-lexicon/BOR) |
| AE | Apte Student's English-Sanskrit Dictionary | Eng→Skt | V. S. Apte | 1920 | 501 | [ApteES](https://github.com/sanskrit-lexicon/ApteES) |
| BUR | Burnouf Dictionnaire Sanscrit-Français | Skt→Fr | Burnouf · Leupol · Renou | 1866 | 781 | [BUR](https://github.com/sanskrit-lexicon/BUR) |
| STC | Stchoupak Dictionnaire Sanscrit-Français | Skt→Fr | Stchoupak · Nitti · Renou | 1932 | 904 | [STC](https://github.com/sanskrit-lexicon/STC) |
| BOP | Bopp Glossarium Sanscritum | Skt→Lat | Franz Bopp | 1847 | 420 | [BOP](https://github.com/sanskrit-lexicon/BOP) |
| SKD | Śabdakalpadruma | Skt→Skt | Rādhākānta Deva | 1886 | 3,164 | [SKD](https://github.com/sanskrit-lexicon/SKD) |
| VCP | Vācaspatyam | Skt→Skt | Tāranātha Tarkavācaspati | 1873 | 5,407 | [VCP](https://github.com/sanskrit-lexicon/VCP) |
| CCS | Cappeller Sanskrit Wörterbuch | Skt→Ger | Carl Cappeller | 1887 | 541 | [CCS](https://github.com/sanskrit-lexicon/CCS) |
| SCH | Schmidt Nachträge zum Sanskrit-Wörterbuch | Skt→Ger | Richard Schmidt | 1928 | 398 | [SCH](https://github.com/sanskrit-lexicon/SCH) |
| ARMH | Abhidhānaratnamālā of Halāyudha | Skt→Skt | Halāyudha · Aufrecht | 1861 | — | csl-orig only |
| ABCH | Abhidhānacintāmaṇi of Hemacandra | Skt→Skt | Hemacandrācārya | 1896 | 58 | csl-orig only |
| ACPH | Abhidhānacintāmaṇipariśiṣṭa | Skt→Skt | Hemacandrācārya | 1896 | 8 | csl-orig only |
| ACSJ | Abhidhānacintāmaṇiśiloñcha of Jinadeva | Skt→Skt | Jinadeva | 1896 | 5 | csl-orig only |
| NMMB | Nāmamālikā of Bhoja | Skt→Skt | Bhoja | 1955 | 40 | csl-orig only |
| INM | Index to the Names in the Mahābhārata | Specialized | S. Sörensen | 1904 | 852 | [INM](https://github.com/sanskrit-lexicon/INM) |
| VEI | Vedic Index of Names and Subjects | Specialized | Macdonell & Keith | 1912 | 560 | [VEI](https://github.com/sanskrit-lexicon/VEI) |
| PUI | The Purāṇa Index | Specialized | V. R. R. Dikshitar | 1951 | 2,232 | csl-orig only |
| BHS | Buddhist Hybrid Sanskrit Dictionary | Specialized | Franklin Edgerton | 1953 | 634 | [BHS](https://github.com/sanskrit-lexicon/BHS) |
| FRI | Friš Sanskrit Reader Vocabulary | Specialized | Oldřich Friš | 1956 | 349 | [FRI](https://github.com/sanskrit-lexicon/FRI) |
| ACC | Aufrecht's Catalogus Catalogorum | Specialized | Theodor Aufrecht | 1962 | 1,216 | [ACC](https://github.com/sanskrit-lexicon/ACC) |
| KRM | Kṛdantarūpamālā | Specialized | S. Ramasubba Sastri | 1965 | 1,489 | [KRM](https://github.com/sanskrit-lexicon/KRM) |
| IEG | Indian Epigraphical Glossary | Specialized | D. C. Sircar | 1966 | 580 | csl-orig only |
| SNP | Meulenbeld's Sanskrit Names of Plants | Specialized | G. J. Meulenbeld | 1974 | 94 | csl-orig only |
| PE | Puranic Encyclopedia | Specialized | Vettam Mani | 1975 | 922 | csl-orig only |
| PGN | Names in the Gupta Inscriptions | Specialized | Tej Ram Sharma | 1978 | 378 | csl-orig only |
| MCI | Mahābhārata Cultural Index | Specialized | M. A. Mehendale | 1993 | 981 | [MCI](https://github.com/sanskrit-lexicon/MCI) |

**By language:** Skt→Eng 14 · Eng→Skt 3 · Skt→Ger 5 · Skt→Fr 2 · Skt→Lat 1 · Skt→Skt 6 · Specialized 12.

---

## III. Interfaces — sites, search UIs, dashboards, reader apps, APIs

### Dictionary web & search

| Interface | What it does | Status | Stack | Repo |
|---|---|---|---|---|
| [Cologne Digital Sanskrit Dictionaries (CDSL)](https://www.sanskrit-lexicon.uni-koeln.de/) | Flagship multi-dictionary search over all 43 dicts — lookup, entry display, scan-page links | 🟢 Live | PHP · SQLite | [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon) |
| [C-SALT / Kosh API](https://github.com/sanskrit-lexicon/csl-apidev) | REST + GraphQL API over CDSL: SALT-compatible endpoints, scan resolution, citation IDs | 🟢 Live | PHP · SQLite | [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) |
| [kosha — translator-first dictionary](https://github.com/gasyoun/kosha) | Multi-dict collapse (MW+PWG+AP90), scan-anchored, form lookup, evidence layer. P1 API done (115 tests) | 🟡 Beta | FastAPI · SQLite · static Pages | [kosha](https://github.com/gasyoun/kosha) |

### Corpus & reader apps

| Interface | What it does | Status | Stack | Repo |
|---|---|---|---|---|
| [Samudra Manthanam](https://samskrtam.ru) | Parallel Sanskrit–Russian corpus: full-text + morphological-stem search, scholarly reader, line anchors | 🟢 Live | FastAPI · SQLite FTS5 · Pascal desktop | [SamudraManthanam](https://github.com/gasyoun/SamudraManthanam) |
| [Sanskrit→Russian Glossary](https://gasyoun.github.io/SanskritRussian/) | Three-layer word-aligned glossary (surface · lemma · root), fuzzy search, per-letter TSV/JSONL download | 🟢 Live | Static HTML · Fuse.js · JSONL | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| [Russian Rāmāyaṇa portal](https://gasyoun.github.io/RussianRamayana/) | Parallel-text reader + crowdfunding portal for Leonov's translation (Books IV–VII), journey map | 🟢 Live | Static HTML · Leaflet · CSL-JSON | [RussianRamayana](https://github.com/gasyoun/RussianRamayana) |
| [Sanskrit Karaoke](https://gasyoun.github.io/SanskritKaraoke/) | Verse wave-diagram visualiser + karaoke exporter: meter detection, syllable timing, MP4, SM-2 review | 🟢 Live | Standalone JS · Chart.js | [SanskritKaraoke](https://github.com/gasyoun/SanskritKaraoke) |

### Dashboards & data-viz

| Interface | What it does | Status | Stack | Repo |
|---|---|---|---|---|
| [CSL Observatory](https://sanskrit-lexicon.github.io/csl-observatory/) | Org-wide metrics: repos, issues, PRs, contributors, bus-factor, taxonomy + correction typology | 🟢 Live | Observable Framework · Python | [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) |
| [VisualDCS — verb-form frequency](https://github.com/gasyoun/VisualDCS) | Pareto analysis of 781,616 verb examples across 38 tense/mood categories | 🟢 Live | Standalone HTML · Chart.js | [VisualDCS](https://github.com/gasyoun/VisualDCS) |
| [VisualDCS — paradigm browser](https://github.com/gasyoun/VisualDCS) | Interactive 6-root × 9-tense × 9-person verb-form browser, flashcard mode, CSV/MD export | 🟢 Live | Standalone HTML · Chart.js | [VisualDCS](https://github.com/gasyoun/VisualDCS) |
| [BookIndex / Zalizniakiada](https://gasyoun.github.io/BookIndex/) | Single-file PWA: scholar network, sound-law simulator, accent reconstructor, KWIC over 27 lectures | 🟢 Live | D3 · Leaflet · PWA | [BookIndex](https://github.com/gasyoun/BookIndex) |
| [IndologyScholars — forum archive](https://gasyoun.github.io/IndologyScholars/) | Network analysis over 1,362 talks by 270 scholars (2004–26), hypotheses register, JSON-LD | 🟢 Live | Static HTML · D3 · GeoJSON · RDF | [IndologyScholars](https://github.com/gasyoun/IndologyScholars) |

### Docs & article sites

| Interface | What it does | Status | Stack | Repo |
|---|---|---|---|---|
| [CSL Guides](https://sanskrit-lexicon.github.io/csl-guides/) | Docusaurus docs: 5 audience sidebars, 43 deep dictionary pages, quizzes, comparison & citation widgets | 🟢 Live | Docusaurus 3 · React 19 | [csl-guides](https://github.com/sanskrit-lexicon/csl-guides) |
| [CommentaryStrategies essays](https://github.com/gasyoun/CommentaryStrategies) | Comparative DH essays on Russian translators' commentary strategies + TEI/CSV/JSON exports | 🟢 Live | HTML · Python · TEI P5 | [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies) |
| [SamudraManthanam corpus-FAQ](https://samskrtam.ru/corpus-faq/) | Knowledge base (RU) generated by ZettelkastenWiki, deployed alongside the corpus site | 🟢 Live | ZettelkastenWiki static | [ZettelkastenWiki](https://github.com/gasyoun/ZettelkastenWiki) |
| [PWG article dashboard](https://gasyoun.github.io/SanskritLexicography/) | Per-entry PWG article site with live `<ls>` scan links (ls_resolver), on the gh-pages slot | 🟢 Live | Static HTML (build_article_site.py) | [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) |
| [Uprava articles dashboard](https://github.com/gasyoun/Uprava/tree/main/dashboard) | Private, local-only publication-pipeline board over ARTICLES.md. Deliberately not on Pages | 🟡 Beta | HTML + generated articles.js | [Uprava](https://github.com/gasyoun/Uprava) |

### Learning & platform apps

| Interface | What it does | Status | Stack | Repo |
|---|---|---|---|---|
| [CSL App (Flutter)](https://github.com/sanskrit-lexicon/csl-app) | Offline cross-platform dictionary (Android/iOS/desktop/web): 50+ downloadable dicts, multi-scheme translit | 🟢 Live | Flutter · Riverpod · sqflite | [csl-app](https://github.com/sanskrit-lexicon/csl-app) |
| [Systema Sanscriticum](https://github.com/gasyoun/Systema-Sanscriticum) | Laravel LMS: student workbench, course shop, loyalty wallet, teacher analytics, certificates | 🟡 Beta | Laravel 10 · Filament · Livewire · MySQL | [Systema-Sanscriticum](https://github.com/gasyoun/Systema-Sanscriticum) |
| [csl-santam — Tamil lexicon search](https://github.com/sanskrit-lexicon/csl-santam) | PHP/Perl search over combined SQLite (MW + Cappeller + Cologne Online Tamil Lexicon), HK input | 🟡 Beta | PHP · Perl · SQLite | [csl-santam](https://github.com/sanskrit-lexicon/csl-santam) |

---

## IV. Tools — import the toolkit, call the external stacks

### Import it — the code toolkit

| Tool | What it is | Reuse instead of | Home |
|---|---|---|---|
| `sanskrit-util` | One Python+JS package: IAST ⇄ SLP1 ⇄ Devanāgarī transcode + normalization keys (`norm`/`form_key`), parity-tested; v0.3.0 adds the full SLP1-side API | Re-typing the SLP1 table (62 files) or re-deriving the ś-vs-acute / NFD length-loss traps | [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util) |
| csl-pywork correction pipeline | `updateByLine`, `parseheadline`, `diff_to_changes`, `make_xml`, `generate_dict.sh` | Forking `updateByLine.py` an 84th time — pull the vendored original | [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork/tree/main/v02/makotemplates/pywork) |
| web-endpoint template | makotemplates source for `getword`/`servepdf`/`serveimg`; 40+ dicts regenerate from it | Editing 37 drifted per-dict copies — fix the template, regenerate | [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon/tree/main/v02/makotemplates/web/webtc) |
| `kosha/app/render.py` | Code-faithful Python port of the PHP SAX display engine (MW/PWG/AP90), golden-snapshotted | Re-porting Cologne entry rendering to Python | [kosha](https://github.com/gasyoun/kosha/blob/main/app/render.py) |
| `ls_resolver.py` | `<ls>` citation → scanned-edition page-URL resolver | Re-implementing citation→scan mapping | [RussianTranslation/src](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src) |
| `build_vidyut_fallback.py` | Stage-C lemmatizer resolving DCS-missed forms via the vidyut FST lexicon | Writing another lemmatization fallback | [RussianTranslation/src](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src) |
| RU translation kit | Parameterized `mw_ru`/`pwg_ru` kit — translate / QA-judge / re-translate / corpus-check over one `build_src.py` | Cloning a third kit — parameterize the existing one | [RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) |
| ZettelkastenWiki | Canonical static-site generator for note/FAQ/wiki collections: stdlib core, render hooks, i18n, pytest harness | Writing site generator #5 (csl-guides stays Docusaurus by design) | [ZettelkastenWiki](https://github.com/gasyoun/ZettelkastenWiki) |
| CI & hygiene templates | CodeQL, Dependabot (+auto-merge), pre-commit, CoC, CONTRIBUTING, branch protection via `/cologne-*` skills | Hand-writing CI per repo — run the skill (PHP repos use Semgrep) | [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) |

### Call it — external stacks (don't clone)

| Stack | What it is | Reuse rule | Home |
|---|---|---|---|
| Samsaadhanii / SCL (Amba Kulkarni, UoHyd) | Morph analyzer, sandhi/segmenter, compound processor, Pāṇinian parser, Amarakośa net, Dhātupāṭha — already consumes our dicts | Call the live JSON APIs / cross-validate; don't clone the GPL source | [SAMSAADHANII_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/SAMSAADHANII_INDEX.md) |
| Sanskrit Heritage (Gérard Huet, INRIA) | Dictionary + morphology + segmenter (LGPLLR): DICO hypertext dict, MW-aligned pages, frequency TSVs, OCaml banks | Pull from the GitHub mirror — sanskrit.inria.fr is Anubis bot-walled | [Heritage_Resources](https://github.com/darkone23/Heritage_Resources) |
| DharmaMitra (Berkeley) | AI-translation stack (MT, Deep Research w/ references, parallel-passage Explore, segmentation, OCR); GPU morphology supplier to csl-atlas | Reuse their MT error taxonomy (wired into pwg_ru/mw_ru judges); prospective Kosh-API consumer | [dharmamitra.org](https://dharmamitra.org/) |
| VedaWeb (Cologne / UZH, CC BY 4.0) | Accented Rig-Veda + per-word morphology (Casaretto word-split, Lubotsky padapāṭha), C-SALT-linked | The validation set that unblocks the Vedic accent axis — bulk-export once | [vedaweb.uni-koeln.de](https://vedaweb.uni-koeln.de/rigveda/) |
| vidyut (Ambuda) | Rust Sanskrit toolkit (kosha FST lexicon, prakriyā generator, cheda segmenter, chandas meter) — engine behind the RU kits & Zaliznyak index | Hand-rolling paradigm generation — call vidyut for declensions & PPP validation | [vidyut](https://github.com/ambuda-org/vidyut) |

---

_Sources: dictionary roster from [`csl-guides/src/data/dictionaries.json`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/dictionaries.json)
(verified vs [`csl-orig/v02/`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)); interfaces, data
and tools compiled from [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md),
[`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md),
[`REUSE_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md) and a three-agent repository
sweep (03–04-07-2026)._

_Dr. Mārcis Gasūns_
