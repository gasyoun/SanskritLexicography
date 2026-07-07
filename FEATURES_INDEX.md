# FEATURES_INDEX.md — what the Sanskrit Lexicon project actually has

_Created: 04-07-2026 · Last updated: 04-07-2026_

**Purpose.** A clickable, capability-first map of the working assets across the ~85
repositories: the **dictionaries** digitised, the **interfaces** that serve them, the
**data** already computed, and the **tools** you import rather than re-type. Where its
companion [`REUSE_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md)
answers *"don't rebuild — consume this"*, this file answers *"what exists at all?"* — the
inventory a newcomer (or a fresh session) reads to see the shape of the whole. Every asset
carries a **real example** and its **first-introduced month/year**.

- **Interactive view:** a filterable single-file HTML artifact renders this same catalogue
  (search + category tabs + status/severity/language filters + clickable tags + a changelog).
  Local/shared artifact only — not committed here.
- **Code-level "who owns this":** [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md).
- **Data-flow "who feeds whom":** [`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md).

> Sizes and counts are approximate; re-verify against a source repo before a large change.
> Some linked repos are private ([`github-spine`](https://github.com/gasyoun/github-spine),
> [`Uprava`](https://github.com/gasyoun/Uprava)).

**At a glance:** 44 dictionaries · 21 interfaces (17 live) · 37 data assets · 14 tools · 4 external stacks.

**IDs & tiers.** Every asset has a **stable ID** — a **running number within its category**
(1–N; it does *not* restart at each sub-section) prefixed by a **section letter** (`A`–`F` data ·
`G`–`K` interfaces · `L`–`M` tools; dictionaries use their code). Datasets are graded by **size** (measured
on disk, so magnitudes are comparable — rows/entries alone are not): 🟢 **large** (&gt;10 MB) · 🟡 **medium**
(1–10 MB) · ⚪ **small** (&lt;1 MB); the **Size** column carries the count and the exact MB. The **Intro** column is the asset's
first-introduced month/year from git history; for the external stacks (M10–M14) it is instead the
**last update**, each from a documented source of truth (see the † note under that table).

**How assets connect.** Many entries belong to shared clusters — the **vidyut**
lemmatization chain (`build_vidyut_fallback.py` (L6) calls the `vidyut` engine (M14), feeding
`vidyut_form2lemma.tsv` (E29) and the Zaliznyak index (E31)), the **DCS** frequency stack, the
**Heritage** oracle suite, the **roots / etymology** crosswalks. In the interactive artifact
these are clickable `#tags` that pivot the whole index to everything in a cluster.

---

## I. Data assets — query it, someone already spent the compute

Size tier: 🟢 large (&gt;10 MB) · 🟡 medium (1–10 MB) · ⚪ small (&lt;1 MB). Examples are **verbatim sample rows** from the
actual files (⚪-tier / *schema*-marked = gitignored / binary / too large, so the shape is shown).

### A · Sanskrit → Russian & translation

| ID | Asset | What it is | Size | Example (real sample) | Intro | Home |
|---|---|---|---|---|---|---|
| 🟢 A1 | `corpus_lexicon` | 1.09 M word-aligned Sa→Ru rows (per verse-pair, SLP1-keyed, ~190k keys) | 1.09 M rows · 276.6 MB | `<slp1-word>  <russian>  <verse-pair-id>` (schema; JSONL gitignored) | 06/26 | [build_corpus_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py) |
| 🟢 A2 | SanskritRussian glossary (3-layer) | Ranked Sa→Ru glossary: surface 190,838 · lemma 40,370 · root 2,021; 87% coverage | 233k entries · 61.3 MB | `A → принеси · freq 43 · ADP` (lemma layer) | 07/26 | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| 🟢 A3 | `mw_en_tm.json` | SLP1-keyed MW English-gloss translation memory behind the RU/EN kits | 187,506 · 11.1 MB | `"a": "the first letter of the alphabet · the first short vowel…"` | 06/26 | [RussianTranslation/src](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src) |
| 🟢 A4 | lemma / root glossary (DCS) | DCS lemma→gloss and root→gloss glossaries, bilingual, TSV + JSONL | lemma 16– · root · 20.3 MB | `AGozi → Распространяя звуки · verb` (root layer) | 07/26 | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |

### B · Roots & etymology

| ID | Asset | What it is | Size | Example (real sample) | Intro | Home |
|---|---|---|---|---|---|---|
| ⚪ B5 | `mw_roots.tsv` | MW verbal-root inventory: 2,113 records with explicit `verb_type` (750 genuineroot + 1363 root) | 2,113 · 75 KB | `aMS   aṃś   genuineroot   10P,10Ā` | 06/26 | [csl-orig/v02/mw](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw_roots.tsv) |
| 🟡 B6 | `mw_etymology.tsv` / `pwg_etymology.tsv` | Headword→root derivation tables (Pāṇinian), 10 dicts | ~9–11k rows each · 2.9 MB | `10   aṃśa   aMSa   aś   aS   fr-root   0Ā,0P   Y` | 06/26 | [csl-orig/v02/mw](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw_etymology.tsv) |
| 🟡 B7 | `etymology_stats` | Cross-dict aggregates: root oracle, 41-pair agreement matrix (95% CI), affix entropy/frequency | 10 dicts · 2.9 MB | `root_oracle:  A   ā   kram   kram   1   mw` | 06/26 | [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02) |
| ⚪ B8 | `etymology-oracle.json` | csl-atlas cross-dict etymology aggregator, consumed verbatim from `etymology_stats` | 67k rows · 23 KB | `{ "dictionaryCount": 10, "generatedAt": "2026-06-26…", "totals": {…} }` | 06/26 | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) |
| ⚪ B9 | `root_crosswalk.csv` + `class_concordance.csv` | MW ↔ Whitney root-class alignment + concordance with frequency | + · 53 KB | `1,aṃh,yes,114,,matched,0` | 06/26 | [MWS/root_crosswalk](https://github.com/gasyoun/MWS/tree/main/root_crosswalk) |
| ⚪ B10 | `Whitney_DCS_audit.json` | Whitney × DCS root audit vs the 935-root Whitney hub | 415 KB | `{ "root":"aṃh", "dcs_lemma":"aṃh", "status":"matched", "class_verdict":"whitney-missing" }` | 06/26 | [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) |
| ⚪ B11 | `corpus_class_verdicts.json` | Corpus-verified root-class verdicts. ⚠ unaccented DCS can't split class I vs VI | 514 KB | `{ "aṃh": { "classes": [], "verdict": "not_attested" } }` | 06/26 | [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) |
| ⚪ B12 | `dcs_ppp_verified.tsv` | Corpus-attested past-passive-participle forms + counts | 5,181 forms · 147 KB | `vac   ukta   2   P.   7734` (√vac → ukta, 7734×) | 07/26 | [VisualDCS](https://github.com/gasyoun/VisualDCS/tree/main/derived-data/Glagolnye-formy) |

### C · Headwords & crosswalks

| ID | Asset | What it is | Size | Example (real sample) | Intro | Home |
|---|---|---|---|---|---|---|
| 🟢 C13 | `union_headwords.tsv` | Cross-dict union headword index with per-dict provenance | ~323k · 11.8 MB | `A   ā   12   AP BUR CAE CCS GRA MD MW PWG PWK SCH SKD VCP   fmn` | 06/26 | [HeadwordLists/union](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) |
| 🟡 C14 | `mw_heritage_crosswalk.tsv` | MW → Sanskrit Heritage alignment: 185,803 entries, 97.6% anchor-resolved | 185.8k · 3.1 MB | `a   0` (MW headword → Heritage anchor id / coverage) | 07/26 | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv) |
| ⚪ C15 | DCS↔CDSL crosswalk | DCS lemma ↔ CDSL headword linkset, 12,946 rows (81.4% linked) | 12,946 rows · 618 KB | `37875   tad   tad   tad   1   3734   pron` | 06/26 | [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/dcs_xref/dcs_cdsl_xref.tsv) |
| ⚪ C16 | union `coverage_additions.tsv` | Headwords found beyond the core CDSL dictionaries | union · 711 KB | `5   nominal   enad   enad` | 06/26 | [HeadwordLists/union](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/union) |
| 🟢 C17 | csl-atlas `alignment-confidence.json` | Per-pair cross-dict headword alignment confidence, sharded | 164 shards · 43.0 MB | `{ "code":"mw", "label":"MW", "grammarReliable": true }` | 05/26 | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) |
| 🟢 C18 | csl-atlas low-confidence review set | Alignments flagged below threshold for a human pass | review set · 31.3 MB | the below-threshold subset of `alignment-confidence.json` (schema) | 05/26 | [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) |

### D · Heritage & morphology oracles

| ID | Asset | What it is | Size | Example (real sample) | Intro | Home |
|---|---|---|---|---|---|---|
| ⚪ D19 | `heritage_forms_oracle.tsv.gz` | Pandora → Heritage inflected-form alignment oracle, morphology-aware | 525 KB | `form ↔ Heritage lemma + morphology` (schema; gzip) | 07/26 | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| 🟡 D20 | `heritage_dico_gloss.tsv` | Heritage DICO lemma glosses — SLP1 / Devanāgarī / English | 24.5k · 4.3 MB | `akAra   DICO/1.html#akaara   [ ( a ) - kāra ] m. le son ou la lettre 'a'.   kaara` | 07/26 | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| 🟡 D21 | `heritage_forms_oracle_disagreements.tsv` | Cross-dict morphology disagreement audit | 20.5k · 1.3 MB | `ABAByAm   disagree   ABA   ABa   nominal   dcs   genuine-or-ambiguous` | 07/26 | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| 🟢 D22 | `heritage_only_forms.tsv` | Forms attested in Heritage but absent from MW/PWG/etc. | 28.9 MB | one Heritage-exclusive form per line (schema) | 11/14 | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |
| 🟢 D23 | `heritage_mirror/DATA/` frequency tables | Heritage frequency & morphology corpus TSVs (pada_freq, comp_freq, …) | 21.0 MB | `comp_freq.tsv:   a   6894` | 07/26 | [heritage_mirror](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/heritage_mirror) |
| 🟢 D24 | `sanhw1.xlsx` (Sanskrit-Hybrid Word) | Catalan-Pujol Sanskrit-Hybrid Word master headword list | 61k · 39.3 MB | xlsx: one headword per row (schema) | 11/14 | [HeadwordLists](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) |

### E · Frequency & corpus

| ID | Asset | What it is | Size | Example (real sample) | Intro | Home |
|---|---|---|---|---|---|---|
| 🟡 E25 | VisualDCS DCS ingest + lemma summary | Canonical CoNLL-U → SQLite build + `dcs_lemma_summary.json`. ⚠ Tense=Past conflates aorist/perfect | ~15.9k lemmas · 3.4 MB | `{ "A": { "freqBand": 5, "attested": true } }` | 06/26 | [import_dcs_conllu.py](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/import_dcs_conllu.py) |
| 🟡 E26 | kosha frequency layer | SLP1-keyed sidecar: whole-corpus counts + per-period vectors + core-vocab coverage (DCS M9) | 83,277 · 4.7 MB | `ca   155088   ind   1   9 Vedic=8283 · 1 -800=2897 · …   176104` | 07/26 | [kosha/data/frequency](https://github.com/gasyoun/kosha/blob/main/data/frequency/lemma_frequency.tsv) |
| 🟡 E27 | `dcs_form2lemma.tsv` | DCS form→lemma alignment, SLP1-keyed | 408k · 9.4 MB | `''jYAya   AjYA   VERB   1` | 07/26 | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| ⚪ E28 | `dcs_lemma2root.tsv` | DCS lemma → root mapping | 244 KB | `ABA   BA   suffix` | 07/26 | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| ⚪ E29 | `vidyut_form2lemma.tsv` | Stage-C fallback: forms DCS missed, resolved via the **vidyut** FST | 28.5k · 744 KB | `ABAga   ABAj   noun   2` | 07/26 | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| 🟡 E30 | `surface_dcs_misses.tsv` | DCS resolution-gap analysis — forms that failed DCS lookup | 6.5 MB | `'maratejasi   'maratejasi   1   …` | 07/26 | [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| 🟡 E31 | Zaliznyak grammar index | Compact Zaliznyak-style grammar tokens over all PWG: 98,639 headwords, 335 tokens | 98,639 rows · 5.8 MB | `a   2   f.   a   f·1   a-stem` (headword · G·T · stem-class) | 06/26 | [headword_index.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv) |
| 🟢 E32 | `correction_events_release.csv` | Correction event log: 50,953 events × 43 dicts × 210 correctors, 2014–2026 | ~52k · 58.7 MB | `1a1bd21d909e0bb0, 2014-03-18, form, apes, pain, ghad → ghaṭ` | 06/26 | [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) |
| 🟡 E38 | `<ls>` citation-frequency graph | Which classical texts each dict quotes via `<ls>`, canonicalized to shared nodes across 11 dicts; 828,505 resolved citations, 912 texts. MW non-text markers filtered | 912 texts · 1,707 edges · ~150 KB | `pwg   Mahābhārata   39130` (edge) · `Mahābhārata   56818   8   MAHĀBHĀRATA; MBh; …` (node) | 07/26 | [csl-atlas/data/citations](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations) |

### F · Text collections & other

| ID | Asset | What it is | Size | Example (real sample) | Intro | Home |
|---|---|---|---|---|---|---|
| 🟡 F33 | Indische Sprüche | All 7,537 Böhtlingk subhāṣitas as JSONL (public domain) | 7,537 · 6.9 MB | `{ "num":1, "saying_id":"Saying 1", "deva":"अंशो ऽपि दुष्टदिष्टानां…" }` | 07/26 | [indische_sprueche.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl) |
| ⚪ F34 | ortho-drift reform maps | 19th-c.→modern spelling maps: de 15,685 · ru 7,709 · fr 254 · en 71 | ~23.7k forms · 727 KB | `de_reform_map.tsv:   aachner → aachener   (×75)` | 06/26 | [SanskritSpellCheck/ortho_drift](https://github.com/drdhaval2785/SanskritSpellCheck/tree/master/ortho_drift) |
| ⚪ F35 | do-not-file corpus | 2,297 deliberately non-standard headword spellings across 33 dicts | 2,297 · 25 KB | `ABasvara` (deliberately non-standard — do not "correct") | 06/26 | [do_not_file_suppress.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/nochange/do_not_file_suppress.txt) |
| 🟢 F36 | csl-santam Tamil SQLite | MW + Cappeller + Cologne Online Tamil Lexicon combined | 321,620 · 29.9 MB | `source(mwd·cap·otl) · headword · body` (schema; Harvard-Kyoto keys) | 06/15 | [csl-santam](https://github.com/sanskrit-lexicon/csl-santam) |
| ⚪ F37 | OCR'd dictionary front-matter | Faithful Markdown + EN/RU editions of title pages, prefaces, abbreviations | multi-dict | per dict: title-page + preface + abbreviations as Markdown (schema) | 06/26 | [csl-guides](https://github.com/gasyoun/csl-guides) |

---

## II. Dictionaries — the 44 digitised from canonical source text

Roster from [`csl-guides/src/data/dictionaries.json`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/dictionaries.json),
verified against [`csl-orig/v02/`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02).
The **code is the ID** and the **Year** column is the edition's publication year. The **Example**
column links a real sample headword (or *browse*) to that dictionary's live Cologne interface
(URL pattern `…/scans/<CODE>Scan/<YEAR>/web/index.php`, MW & AP90 verified).

| Code | Dictionary | Language | Author | Year | Pages | Repo | Example |
|---|---|---|---|---:|---:|---|---|
| MW | Monier-Williams Sanskrit-English Dictionary | Skt→Eng | Monier-Williams | 1899 | 1,333 | [MWS](https://github.com/gasyoun/MWS) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/index.php) |
| PWG | Grosses Petersburger Wörterbuch | Skt→Ger | Böhtlingk & Roth | 1855 | 4,737 | [PWG](https://github.com/sanskrit-lexicon/PWG) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020/web/index.php) |
| PW | Sanskrit-Wörterbuch in kürzerer Fassung | Skt→Ger | Otto Böhtlingk | 1879 | 2,141 | [PWK](https://github.com/sanskrit-lexicon/PWK) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/PWScan/2020/web/index.php) |
| GRA | Wörterbuch zum Rig-Veda | Skt→Ger | Hermann Grassmann | 1873 | 1,775 | [GRA](https://github.com/sanskrit-lexicon/GRA) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/GRAScan/2020/web/index.php) |
| AP90 | Apte Practical Sanskrit-English Dictionary | Skt→Eng | V. S. Apte | 1890 | 1,196 | [AP90](https://github.com/sanskrit-lexicon/AP90) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/2020/web/index.php) |
| AP | Practical Sanskrit-English Dictionary (rev.) | Skt→Eng | Apte · Gode · Karve | 1957 | 1,768 | [AP](https://github.com/sanskrit-lexicon/AP) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/APScan/2020/web/index.php) |
| MW72 | Monier-Williams Sanskrit-English (1st ed.) | Skt→Eng | Monier Williams | 1872 | 1,186 | [MW72](https://github.com/sanskrit-lexicon/MW72) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/MW72Scan/2020/web/index.php) |
| WIL | Wilson Sanskrit-English Dictionary | Skt→Eng | H. H. Wilson | 1832 | 982 | [WIL](https://github.com/sanskrit-lexicon/WIL) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/WILScan/2020/web/index.php) |
| YAT | Yates Sanskrit-English Dictionary | Skt→Eng | Rev. W. Yates | 1846 | 928 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/YATScan/2020/web/index.php) |
| GST | Goldstücker Sanskrit-English Dictionary | Skt→Eng | Theodor Goldstücker | 1856 | 334 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/GSTScan/2020/web/index.php) |
| BEN | Benfey Sanskrit-English Dictionary | Skt→Eng | Theodore Benfey | 1866 | 1,145 | [BEN](https://github.com/sanskrit-lexicon/BEN) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/BENScan/2020/web/index.php) |
| LAN | Lanman's Sanskrit Reader Vocabulary | Skt→Eng | C. R. Lanman | 1884 | 403 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/LANScan/2020/web/index.php) |
| LRV | Vaidya Sanskrit-English Dictionary | Skt→Eng | L. R. Vaidya | 1889 | 889 | [LRV](https://github.com/sanskrit-lexicon/LRV) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/LRVScan/2022/web/index.php) |
| CAE | Cappeller Sanskrit-English Dictionary | Skt→Eng | Carl Cappeller | 1891 | 672 | [CAE](https://github.com/sanskrit-lexicon/CAE) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/CAEScan/2020/web/index.php) |
| MD | Macdonell Sanskrit-English Dictionary | Skt→Eng | A. A. Macdonell | 1893 | 384 | [MD](https://github.com/sanskrit-lexicon/MD) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/MDScan/2020/web/index.php) |
| SHS | Śabda-Sāgara Sanskrit-English Dictionary | Skt→Eng | J. Vidyasagara | 1900 | 839 | [SHS](https://github.com/sanskrit-lexicon/SHS) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/SHSScan/2020/web/index.php) |
| PD | Encyclopedic Dictionary of Sanskrit on Historical Principles | Skt→Eng | Ghatage · Bhatta | 1976 | 4,328 | [Cologne scan ↗](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/web/index.php) | [browse ↗](https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/web/index.php) |
| MWE | Monier-Williams English-Sanskrit Dictionary | Eng→Skt | Monier Williams | 1851 | 860 | csl-orig only | [`A` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWEScan/2020/web/index.php) |
| BOR | Borooah English-Sanskrit Dictionary | Eng→Skt | Anundoram Borooah | 1877 | 772 | [BOR](https://github.com/sanskrit-lexicon/BOR) | [`A` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/BORScan/2020/web/index.php) |
| AE | Apte Student's English-Sanskrit Dictionary | Eng→Skt | V. S. Apte | 1920 | 501 | [ApteES](https://github.com/sanskrit-lexicon/ApteES) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/AEScan/2020/web/index.php) |
| BUR | Burnouf Dictionnaire Sanscrit-Français | Skt→Fr | Burnouf · Leupol · Renou | 1866 | 781 | [BUR](https://github.com/sanskrit-lexicon/BUR) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/BURScan/2020/web/index.php) |
| STC | Stchoupak Dictionnaire Sanscrit-Français | Skt→Fr | Stchoupak · Nitti · Renou | 1932 | 904 | [STC](https://github.com/sanskrit-lexicon/STC) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/STCScan/2020/web/index.php) |
| BOP | Bopp Glossarium Sanscritum | Skt→Lat | Franz Bopp | 1847 | 420 | [BOP](https://github.com/sanskrit-lexicon/BOP) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/BOPScan/2020/web/index.php) |
| SKD | Śabdakalpadruma | Skt→Skt | Rādhākānta Deva | 1886 | 3,164 | [SKD](https://github.com/sanskrit-lexicon/SKD) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/SKDScan/2020/web/index.php) |
| VCP | Vācaspatyam | Skt→Skt | Tāranātha Tarkavācaspati | 1873 | 5,407 | [VCP](https://github.com/sanskrit-lexicon/VCP) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/VCPScan/2020/web/index.php) |
| CCS | Cappeller Sanskrit Wörterbuch | Skt→Ger | Carl Cappeller | 1887 | 541 | [CCS](https://github.com/sanskrit-lexicon/CCS) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/CCSScan/2020/web/index.php) |
| SCH | Schmidt Nachträge zum Sanskrit-Wörterbuch | Skt→Ger | Richard Schmidt | 1928 | 398 | [SCH](https://github.com/sanskrit-lexicon/SCH) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/SCHScan/2020/web/index.php) |
| ARMH | Abhidhānaratnamālā of Halāyudha | Skt→Skt | Halāyudha · Aufrecht | 1861 | — | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/ARMHScan/2020/web/index.php) |
| ABCH | Abhidhānacintāmaṇi of Hemacandra | Skt→Skt | Hemacandrācārya | 1896 | 58 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/ABCHScan/2023/web/index.php) |
| ACPH | Abhidhānacintāmaṇipariśiṣṭa | Skt→Skt | Hemacandrācārya | 1896 | 8 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/ACPHScan/2023/web/index.php) |
| ACSJ | Abhidhānacintāmaṇiśiloñcha of Jinadeva | Skt→Skt | Jinadeva | 1896 | 5 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/ACSJScan/2023/web/index.php) |
| NMMB | Nāmamālikā of Bhoja | Skt→Skt | Bhoja | 1955 | 40 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/NMMBScan/2026/web/index.php) |
| INM | Index to the Names in the Mahābhārata | Specialized | S. Sörensen | 1904 | 852 | [INM](https://github.com/sanskrit-lexicon/INM) | [`Abala` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/INMScan/2020/web/index.php) |
| VEI | Vedic Index of Names and Subjects | Specialized | Macdonell & Keith | 1912 | 560 | [VEI](https://github.com/sanskrit-lexicon/VEI) | [`Aṃśu` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/VEIScan/2020/web/index.php) |
| PUI | The Purāṇa Index | Specialized | V. R. R. Dikshitar | 1951 | 2,232 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/PUIScan/2020/web/index.php) |
| BHS | Buddhist Hybrid Sanskrit Dictionary | Specialized | Franklin Edgerton | 1953 | 634 | [BHS](https://github.com/sanskrit-lexicon/BHS) | [`a` ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/BHSScan/2020/web/index.php) |
| FRI | Friš Sanskrit Reader Vocabulary | Specialized | Oldřich Friš | 1956 | 349 | [FRI](https://github.com/sanskrit-lexicon/FRI) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/FRIScan/2025/web/index.php) |
| ACC | Aufrecht's Catalogus Catalogorum | Specialized | Theodor Aufrecht | 1962 | 1,216 | [ACC](https://github.com/sanskrit-lexicon/ACC) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/ACCScan/2020/web/index.php) |
| KRM | Kṛdantarūpamālā | Specialized | S. Ramasubba Sastri | 1965 | 1,489 | [KRM](https://github.com/sanskrit-lexicon/KRM) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/KRMScan/2020/web/index.php) |
| IEG | Indian Epigraphical Glossary | Specialized | D. C. Sircar | 1966 | 580 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/IEGScan/2020/web/index.php) |
| SNP | Meulenbeld's Sanskrit Names of Plants | Specialized | G. J. Meulenbeld | 1974 | 94 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/SNPScan/2020/web/index.php) |
| PE | Puranic Encyclopedia | Specialized | Vettam Mani | 1975 | 922 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/PEScan/2020/web/index.php) |
| PGN | Names in the Gupta Inscriptions | Specialized | Tej Ram Sharma | 1978 | 378 | csl-orig only | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/PGNScan/2020/web/index.php) |
| MCI | Mahābhārata Cultural Index | Specialized | M. A. Mehendale | 1993 | 981 | [MCI](https://github.com/sanskrit-lexicon/MCI) | [browse ↗](https://www.sanskrit-lexicon.uni-koeln.de/scans/MCIScan/2020/web/index.php) |

**By language:** Skt→Eng 14 · Eng→Skt 3 · Skt→Ger 5 · Skt→Fr 2 · Skt→Lat 1 · Skt→Skt 6 · Specialized 12.

---

## III. Interfaces — sites, search UIs, dashboards, reader apps, APIs

The **name links** to the live interface; **Intro** is the repo's first commit (or the feature's
first appearance where the repo predates it).

### G · Dictionary web & search

| ID | Interface | What it does | Status | Try | Intro | Stack · Repo |
|---|---|---|---|---|---|---|
| G1 | [Cologne Digital Sanskrit Dictionaries (CDSL)](https://www.sanskrit-lexicon.uni-koeln.de/) | Flagship multi-dictionary search over all 43 dicts | 🟢 Live | look up देव across all 43 dictionaries | 07/18 | PHP · SQLite · [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon) |
| G2 | [C-SALT / Kosh API](https://github.com/sanskrit-lexicon/csl-apidev) | REST + GraphQL API over CDSL | 🟢 Live | call the `salt_entries` / `salt_graphql` endpoints over MW | 04/18 | PHP · SQLite · [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) |
| G3 | [kosha — translator-first dictionary](https://github.com/gasyoun/kosha) | Multi-dict collapse (MW+PWG+AP90), scan-anchored | 🟡 Beta | collapse MW + PWG + AP90 for one headword | 07/26 | FastAPI · SQLite · [kosha](https://github.com/gasyoun/kosha) |

### H · Corpus & reader apps

| ID | Interface | What it does | Status | Try | Intro | Stack · Repo |
|---|---|---|---|---|---|---|
| H4 | [Samudra Manthanam](https://samskrtam.ru) | Parallel Sanskrit–Russian corpus with morphological search | 🟢 Live | regex + stem search across parallel Sa–Ru texts | 04/26 | FastAPI · SQLite FTS5 · [SamudraManthanam](https://github.com/gasyoun/SamudraManthanam) |
| H5 | [Sanskrit→Russian Glossary](https://gasyoun.github.io/SanskritRussian/) | Three-layer word-aligned glossary, fuzzy search | 🟢 Live | a form → its surface / lemma / root Russian renderings | 07/26 | Static · Fuse.js · [SanskritRussian](https://github.com/gasyoun/SanskritRussian) |
| H6 | [Russian Rāmāyaṇa portal](https://gasyoun.github.io/RussianRamayana/) | Parallel-text reader + crowdfunding portal | 🟢 Live | read Book IV with the parallel Sanskrit–Russian reader | 05/26 | Static · Leaflet · [RussianRamayana](https://github.com/gasyoun/RussianRamayana) |
| H7 | [Sanskrit Karaoke](https://gasyoun.github.io/SanskritKaraoke/) | Verse wave-diagram visualiser + karaoke exporter | 🟢 Live | wave diagram + meter detection for an anuṣṭubh verse | 04/26 | Standalone JS · Chart.js · [SanskritKaraoke](https://github.com/gasyoun/SanskritKaraoke) |

### I · Dashboards & data-viz

| ID | Interface | What it does | Status | Try | Intro | Stack · Repo |
|---|---|---|---|---|---|---|
| I8 | [CSL Observatory](https://sanskrit-lexicon.github.io/csl-observatory/) | Org-wide metrics + correction typology | 🟢 Live | the bus-factor and correction-typology charts | 05/26 | Observable · Python · [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) |
| I9 | [VisualDCS — verb-form frequency](https://github.com/gasyoun/VisualDCS) | Pareto analysis of 781,616 verb examples | 🟢 Live | the Pareto curve over 781,616 verb examples | 04/26 | Standalone HTML · Chart.js · [VisualDCS](https://github.com/gasyoun/VisualDCS) |
| I10 | [VisualDCS — paradigm browser](https://github.com/gasyoun/VisualDCS) | Interactive verb-form paradigm browser | 🟢 Live | 6 roots × 9 tenses × 9 person/number cells, flashcard mode | 04/26 | Standalone HTML · Chart.js · [VisualDCS](https://github.com/gasyoun/VisualDCS) |
| I11 | [BookIndex / Zalizniakiada](https://gasyoun.github.io/BookIndex/) | Single-file PWA over Zaliznyak's legacy | 🟢 Live | the sound-law simulator + KWIC concordance | 04/26 | D3 · Leaflet · PWA · [BookIndex](https://github.com/gasyoun/BookIndex) |
| I12 | [IndologyScholars — forum archive](https://gasyoun.github.io/IndologyScholars/) | Network analysis over 1,362 talks | 🟢 Live | the network of 1,362 talks by 270 scholars | 04/26 | Static · D3 · RDF · [IndologyScholars](https://github.com/gasyoun/IndologyScholars) |

### J · Docs & article sites

| ID | Interface | What it does | Status | Try | Intro | Stack · Repo |
|---|---|---|---|---|---|---|
| J13 | [CSL Guides](https://sanskrit-lexicon.github.io/csl-guides/) | Docusaurus docs: 43 deep dictionary pages, widgets | 🟢 Live | a deep dictionary page + the comparison widget | 06/26 | Docusaurus 3 · React 19 · [csl-guides](https://github.com/sanskrit-lexicon/csl-guides) |
| J14 | [CommentaryStrategies essays](https://github.com/gasyoun/CommentaryStrategies) | Comparative DH essays + TEI/CSV/JSON exports | 🟢 Live | the Mahābhārata translator-commentary comparison | 04/26 | HTML · Python · TEI P5 · [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies) |
| J15 | [SamudraManthanam corpus-FAQ](https://samskrtam.ru/corpus-faq/) | RU knowledge base via ZettelkastenWiki | 🟢 Live | the Russian corpus knowledge base | 07/26 | ZettelkastenWiki · [ZettelkastenWiki](https://github.com/gasyoun/ZettelkastenWiki) |
| J16 | [PWG article dashboard](https://gasyoun.github.io/SanskritLexicography/) | Per-entry PWG site with live `<ls>` scan links | 🟢 Live | a PWG entry with live `<ls>` scan-page links | 07/26 | Static (build_article_site.py) · [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) |
| J17 | [Uprava articles dashboard](https://github.com/gasyoun/Uprava/tree/main/dashboard) | Private, local-only publication-pipeline board | 🟡 Beta | (local) the publication-readiness board over ARTICLES.md | 06/26 | HTML + articles.js · [Uprava](https://github.com/gasyoun/Uprava) |
| J21 | [kosha data & tools directory](https://gasyoun.github.io/kosha/directory/) | Curated Sanskrit-NLP data + tools directory: our datasets (downloadable) + external stacks, schema.org Dataset JSON-LD | 🟢 Live | download a public dataset or find the external stack to call | 07/26 | Static (build_directory.py from datasets.json + external_tools.json) · [kosha](https://github.com/gasyoun/kosha/blob/main/scripts/build_directory.py) |

### K · Learning & platform apps

| ID | Interface | What it does | Status | Try | Intro | Stack · Repo |
|---|---|---|---|---|---|---|
| K18 | [CSL App (Flutter)](https://github.com/sanskrit-lexicon/csl-app) | Offline cross-platform dictionary, 50+ dicts | 🟢 Live | offline lookup with ITRANS / HK / SLP1 / Devanāgarī input | 03/26 | Flutter · Riverpod · sqflite · [csl-app](https://github.com/sanskrit-lexicon/csl-app) |
| K19 | [Systema Sanscriticum](https://github.com/gasyoun/Systema-Sanscriticum) | Laravel LMS for a Sanskrit school | 🟡 Beta | the student workbench + course shop | 02/26 | Laravel 10 · Filament · MySQL · [Systema-Sanscriticum](https://github.com/gasyoun/Systema-Sanscriticum) |
| K20 | [csl-santam — Tamil lexicon search](https://github.com/sanskrit-lexicon/csl-santam) | PHP/Perl search over combined Tamil SQLite | 🟡 Beta | a Harvard-Kyoto search over 321k combined entries | 06/15 | PHP · Perl · SQLite · [csl-santam](https://github.com/sanskrit-lexicon/csl-santam) |

---

## IV. Tools — import the toolkit, call the external stacks

### L · Import it — the code toolkit

| ID | Tool | What it is | Example (usage) | Intro | Reuse instead of · Home |
|---|---|---|---|---|---|
| L1 | `sanskrit-util` | Python+JS IAST ⇄ SLP1 ⇄ Devanāgarī transcode + normalization keys, parity-tested; v0.3.0 SLP1-side API | `from sanskrit_util import to_slp1; to_slp1("देव") → "deva"` | 06/26 | Re-typing the SLP1 table (62 files) · [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util) |
| L2 | csl-pywork correction pipeline | `updateByLine`, `parseheadline`, `diff_to_changes`, `make_xml`, `generate_dict.sh` | `python updateByLine.py mw.txt change.txt out.txt` | 07/19 | Forking `updateByLine.py` an 84th time · [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork/tree/main/v02/makotemplates/pywork) |
| L3 | web-endpoint template | makotemplates source for `getword`/`servepdf`/`serveimg`; 40+ dicts regenerate | `getword.php?key=deva&dict=mw → entry display` | 07/18 | Editing 37 drifted per-dict copies · [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon/tree/main/v02/makotemplates/web/webtc) |
| L4 | `kosha/app/render.py` | Python port of the PHP SAX display engine (MW/PWG/AP90), golden-snapshotted | `render(entry_xml) → IAST <s>-display HTML` | 07/26 | Re-porting Cologne entry rendering to Python · [kosha](https://github.com/gasyoun/kosha/blob/main/app/render.py) |
| L5 | `ls_resolver.py` | `<ls>` citation → scanned-edition page-URL resolver | `resolve("Spr. 1") → the boesp scan-page URL` | 07/26 | Re-implementing citation→scan mapping · [RussianTranslation/src](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src) |
| L6 | `build_vidyut_fallback.py` | Stage-C lemmatizer via the **vidyut** FST lexicon *(→ see M14 below)* | `ABAga → ABAj (noun)` — via the vidyut FST | 07/26 | Writing another lemmatization fallback · [RussianTranslation/src](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src) |
| L7 | RU translation kit | Parameterized `mw_ru`/`pwg_ru` kit over one `build_src.py` | `1_perevod → 2_qa_sudya → 3_pereperevod → 4_korpus_proverka` | 06/26 | Cloning a third kit · [RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) |
| L8 | ZettelkastenWiki | Canonical static-site generator for note/FAQ/wiki collections | `zettelkastenwiki build ./notes → ./public` | 07/26 | Writing site generator #5 · [ZettelkastenWiki](https://github.com/gasyoun/ZettelkastenWiki) |
| L9 | CI & hygiene templates | CodeQL, Dependabot (+auto-merge), pre-commit, CoC, branch protection via `/cologne-*` skills | `/cologne-codeql-all · /cologne-dependabot-all` | 06/26 | Hand-writing CI per repo · [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) |

### M · Call it — external stacks (don't clone)

| ID | Stack | What it is | Example (usage) | Intro | Reuse rule · Home |
|---|---|---|---|---|---|
| M10 | Samsaadhanii / SCL (Amba Kulkarni, UoHyd) | Morph analyzer, sandhi/segmenter, Pāṇinian parser, Amarakośa net, Dhātupāṭha | `GET …/scl/…/morph.cgi?word=Bavati → morphology` | 12/25 † | Call the live JSON APIs; don't clone the GPL source · [SAMSAADHANII_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/SAMSAADHANII_INDEX.md) |
| M11 | Sanskrit Heritage (Gérard Huet, INRIA) | Dictionary + morphology + segmenter (LGPLLR): DICO, MW-aligned pages, frequency TSVs | `DICO/1.html#akaara → Heritage gloss + morphology` | 03/25 † | Pull from the GitHub mirror (INRIA is bot-walled) · [Heritage_Resources](https://github.com/darkone23/Heritage_Resources) |
| M12 | DharmaMitra (Berkeley) | AI-translation stack; GPU morphology supplier to csl-atlas | `Translate · Deep-Research (with references) · segmentation · OCR` | 05/26 † | Reuse their MT error taxonomy; prospective Kosh-API consumer · [dharmamitra.org](https://dharmamitra.org/) |
| M13 | VedaWeb (Cologne / UZH, CC BY 4.0) | Accented Rig-Veda + per-word morphology, C-SALT-linked | `bulk-export accented RV text + per-word UZH morphology` | 10/24 † | The validation set for the Vedic accent axis — export once · [vedaweb.uni-koeln.de](https://vedaweb.uni-koeln.de/rigveda/) |
| M14 | vidyut (Ambuda) | Rust Sanskrit toolkit: kosha FST lexicon, prakriyā generator, cheda segmenter, chandas meter | `from vidyut.kosha import Kosha; k.get("Bavati")` | 01/25 † | Hand-rolling paradigm generation · [vidyut](https://github.com/ambuda-org/vidyut) |

† External stacks: **Intro** shows the **last update** (not a first-introduced date), each from a documented source of truth —
M10 [SCL site footer "Updated 25 Dec 2025"](https://sanskrit.uohyd.ac.in/scl/) ·
M11 [Heritage mirror latest commit 2025-03-02](https://github.com/darkone23/Heritage_Resources) (live INRIA site bot-walled) ·
M12 [DharmaMitra news feed — Segment View 2026-05-11](https://dharmamitra.github.io/dharmamitra-guides/news/) ·
M13 [VedaWeb Zenodo data v2, 2024-10-25](https://doi.org/10.5281/zenodo.15489124) ·
M14 [vidyut GitHub release py-0.4.0, 2025-01-22](https://github.com/ambuda-org/vidyut/releases).

*The **vidyut** engine (M14) is what `build_vidyut_fallback.py` (L6) calls, and what generates
`vidyut_form2lemma.tsv` (E29) and the Zaliznyak-index paradigms (E31) — one cluster, three entries
across two sections. The interactive artifact makes that link a clickable `#vidyut` tag.*

---

## Contributing — add your dataset, tool or interface

Anyone can propose an asset. Open an issue on
[`SanskritLexicography`](https://github.com/gasyoun/SanskritLexicography/issues/new?title=Add+asset+to+Features+Index&labels=features-index)
with these fields, and it gets added to this file and the interactive index:

| Field | Example |
|---|---|
| **Name** | `my_crosswalk.tsv` |
| **Category** | data / interface / tool |
| **One-line description** | what it is, in a sentence |
| **Size** | count + on-disk size (e.g. `12,946 rows · 618 KB`) |
| **Example** | one real sample row, or a usage snippet |
| **Repo / source URL** | the file or repo it lives in |
| **Tags** | `#topic` clusters + `@yoursurname` |
| **First introduced** | `MM/YY` |

New assets are appended to the **Changelog** below with the date they were added.

---

## Changelog

_Newest first. A dated line lands here whenever assets are added or retired — the same changelog
is rendered on the interactive artifact._

| When | Change |
|---|---|
| 07/26 | **E38** — `<ls>` citation-frequency graph (csl-atlas, [PR #220](https://github.com/sanskrit-lexicon/csl-atlas/pull/220)): 828,505 canonicalized citations → 912 texts across 11 dicts. |
| 07/26 | **Initial index** — 44 dictionaries · 20 interfaces (16 live) · 38 datasets · 14 tools + 4 external stacks catalogued, each with a real example, a severity tier, a first-introduced date and a stable per-section ID. |

---

_Sources: dictionary roster from [`csl-guides/src/data/dictionaries.json`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/dictionaries.json)
(verified vs [`csl-orig/v02/`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02); Cologne
lookup URLs verified for MW & AP90); interfaces, data and tools compiled from
[`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md),
[`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md),
[`REUSE_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md) and a repository
sweep with verbatim sample rows + git first-introduced dates (03–04-07-2026)._

_Dr. Mārcis Gasūns_
