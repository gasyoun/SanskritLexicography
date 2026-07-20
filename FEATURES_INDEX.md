# FEATURES_INDEX.md — what the Sanskrit Lexicon project actually has

_Created: 04-07-2026 · Last updated: 20-07-2026_

**Purpose.** A clickable, capability-first map of the working assets across the ~85
repositories: the **dictionaries** digitised, the **interfaces** that serve them, the
**data** already computed, and the **tools** you import rather than re-type. Where its
companion [`REUSE_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md)
answers *"don't rebuild — consume this"*, this file answers *"what exists at all?"* — the
inventory a newcomer (or a fresh session) reads to see the shape of the whole. Every asset
carries a **real example** and its **first-introduced month/year**.

- **Interactive view:** **built** — [`features_index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/features_index.html),
  a self-contained, filterable single-file HTML artifact (free-text search + category tabs
  Данные/Словари/Интерфейсы/Инструменты/Changelog + status/size-tier/language filters),
  theme-aware, no dependencies. It is **generated from this Markdown file** by
  [`build_features_index_html.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/build_features_index_html.py)
  (`python build_features_index_html.py`), so the two never drift — edit the Markdown,
  re-run, never hand-edit the HTML. The Markdown table below remains the canonical source.
- **Code-level "who owns this":** [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md).
- **Data-flow "who feeds whom":** [`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md).

> Sizes and counts are approximate; re-verify against a source repo before a large change.
> Some linked repos are private ([`github-spine`](https://github.com/gasyoun/github-spine),
> [`Uprava`](https://github.com/gasyoun/Uprava)).

**At a glance:** 44 dictionaries · 21 interfaces (17 live) · 44 data assets · 14 tools · 4 external stacks · 11 learner-facing drill/practice sets (P1–P11) · 30 catalogued methods/algorithms (Q1–Q30).

**IDs & tiers.** Every asset has a **stable ID** — a **running number within its category**
(1–N; it does *not* restart at each sub-section) prefixed by a **section letter** (`A`–`F` data ·
`G`–`K` interfaces · `L`–`M` tools · `P` drills · `Q` methods; dictionaries use their code). Datasets are graded by **size** (measured
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
| ⚪ B9 | `root_crosswalk.csv` + `class_concordance.csv` | MW ↔ Whitney root-class alignment + concordance with frequency | + · 53 KB | `1,aṃh,yes,114,,matched,0` | 06/26 | [MWS/root_crosswalk](https://github.com/sanskrit-lexicon/MWS/tree/master/root_crosswalk) |
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
| 🟢 C19 | semdom ↔ Amarakosha crosswalk | First SIL semantic-domains ↔ classical-thesaurus map (H742): Level A varga↔domain ID pairs (108, hand-authored) + top-6 machine candidates for all 5,590 AK synsets + 200-synset adjudicated gold (κ 0.677; bridge top-1 17.5% — a shortlist, not labels, [FINDINGS §76](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)); + the grammatical-annex symmetry counted by [semdom_ak_annex_table.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annex_table.py) (H774: AK kāṇḍa 3 46.4% of synsets vs semdom top-9 9.4% of domains, converging 10.7% vs 9.4% sans nānārtha, [FINDINGS §77](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)); CC BY-SA 4.0, feeds the H721 MDF/LIFT `\sd` layer | 108 + 5,590 + 200 rows · ~400 KB | `AK-1.4,kAlavargaH,…,8.4,…,Time,close` | 07/26 | [data/SEMDOM_AK_CROSSWALK_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md) |

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
| ⚪ E39 | markup-tag census | Markup-tag frequency census over all 44 csl-orig/v02 dicts: tag × dict counts + per-1,000-entry rates, 96 distinct tags, 17.5M tag hits, with under-marking verdicts ([report](https://github.com/gasyoun/SanskritLexicography/blob/master/data/MARKUP_TAG_CENSUS_CSLORIG_2026.md)) | 671 rows · 18 KB | `sch   29125   <ab>   2   0.07` (an abbreviation-tagging start that never happened) | 07/26 | [data/markup_tag_census.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv) |
| ⚪ E40 | headword overlap matrix + unique counts | Pairwise headword overlap over the 15-dict union (C13): 105 dict pairs with shared/union/Jaccard + per-dict unique inventories ([findings](https://github.com/gasyoun/SanskritLexicography/blob/master/data/HEADWORD_OVERLAP_UNION15_2026.md); MW∩PWG=94,753 — the figure once mislabeled as "the union"; BHS 58.7% unique, CCS 0.6%) | 105 pairs + 15 dicts · 3 KB | `CAE   CCS   27008   40211   0.6717` (the max-Jaccard pair) | 07/26 | [data/headword_overlap_matrix.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/headword_overlap_matrix.tsv) |
| ⚪ E47 | witness-independence map + corroboration re-audit | Derivation-graph over the 15-dict union operationalizing [FINDINGS §83/§97](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md): per-edge ruling + witness-family partition + a 5-rung collapse ladder (P0..P4) recomputing the union "in N dicts" corroboration over independent families ([report](https://github.com/gasyoun/SanskritLexicography/blob/master/data/WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md); machine map [witness_tiers.json](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_tiers.json)). Corroborated share 55.9% → 34.7% (MW folds into Petersburg); Apte kept independent per §83. **H1389 text-attestation regrade** (MW's non-`<ls>L.</ls>` from csl-orig, [mw_ls_textattest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/mw_ls_textattest.py)): P3 → 33.8%, 17,386 MW-listed ghost headwords | 15 dicts · 9 policies (+`-TA`) · 100 dist-rows | `P3-TA   11   0   17386` (MW-listed ghosts) | 07/26 | [data/witness_independence_reaudit.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_independence_reaudit.tsv) |
| 🟢 E41 | `correction_events_{all,typed,final}.csv` | Full correction-event log behind E32: 52,498 events (git-mined 28,057 + release diffs), one row per correction with old/new IAST, edit-op trace, corrector, latency; `_typed` adds the empirical error typology, `_final` is the canonical enriched view | 52,498 × 3 views · 178.0 MB | `1a1bd21d909e0bb0, 2014-03-18, form, apes, pain, ghad → ghaṭ (ट् instead of द्)` | 06/26 | [csl-observatory data/](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site/src/data) |
| 🟢 E42 | Kompozity `names.csv` | DCS proper-name compound (samāsa) splits with frequency vectors: surface form; constituent-stem split; part count; total corpus frequency; per-period/text tail | 168,880 · 90.7 MB | `rājendra; rājan indra;2;863;596;14;…` | 07/26 | [VisualDCS Kompozity](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Kompozity/README.md) |
| 🟡 E43 | kosha corpus sandhi (programme) | Corpus-attested, frequency-ranked sandhi rules induced from DCS gold splits — a junction-rule inducer derives the `X Y → Z` notation (**96.3 %** Gītā-gold coverage), swept over 17 texts + a graded curriculum + per-class reference. Splitter for no-gold/GRETIL texts settled by an A/B/C bake-off: DharmaMitra neural (not vidyut). | 9,840 rules · ~580k junctions | `a a → ā   vowel coalescence   35533   6.12   17` | 07/26 | [SANDHI_PROGRAMME.md](https://github.com/gasyoun/kosha/blob/main/SANDHI_PROGRAMME.md) |
| ⚪ E43 | code-duplication census + LOC/language-mix per repo | Org-wide dup census over 129 repos (transcoder ×83/9 versions, digentry ×193/5, updateByLine ×144/9, redo.sh ×204/174 …) + sanskrit-util payoff (4/19 donor sites delegate) + per-repo total LOC / dominant language / Python·JS-TS·PHP·Shell·Other split (H688; closes ROADMAP_STATISTICS_ORG_CENSUS L6 rows) | 129 repos · ~40 KB | `transcoder.py 83(62) 9(7) …` (dup family row) · `SanskritLexicography 9,267,485 HTML 187,987 …` (LOC row) | 07/26 | [csl-observatory report](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/code_duplication_census.md) + [script](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/code_duplication_census.py) |
| ⚪ E44 | POS distribution per text | UD-upos (11-tag) frequency per DCS text, all 270 texts, 5,688,416 tokens; verb%/noun% density ranking (nighaṇṭus most noun-dense, śrautasūtras most verb-dense) — closes ROADMAP_STATISTICS_ORG_CENSUS L3 row (H817) | 270 texts × 11 upos · 2,790 rows | `Mahābhārata VERB 217,081 18.91` | 07/26 | [csl-observatory data/pos_distribution_per_text.tsv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pos_distribution_per_text.tsv) + [report](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pos_distribution_per_text.md) |
| ⚪ E45 | sense/polysemy distribution per dict (11/44 general lexica) | Senses-per-entry via 4 convention-specific parsers (Western markers / lumped-gloss semicolon proxy / *iti*-prose / reverse-index), mirrored from the A02 paper's `r2_h1.json`; family trait not diachronic trend (r=0.036) — closes ROADMAP_STATISTICS_ORG_CENSUS L1 row **◐ partial**, remaining 33 dicts blocked (no structural sense-marking; `<L>` decimal suffix confirmed NOT a valid proxy, H817) | 11 dicts · 3 KB | `mw 1899 Monier-Williams 1.15 286525` | 07/26 | [csl-observatory data/sense_polysemy_per_dict.tsv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/sense_polysemy_per_dict.tsv) + [report](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/sense_polysemy_per_dict.md) |
| ⚪ E46 | paradigm-cell coverage per root | Distinct finite (tense·mood·voice·person·number) UD-tag cells attested per verb root over the DCS corpus: 8,054/11,096 lemmas ≥1 finite token, 171 distinct cells corpus-wide; kṛ/gam/bhū top coverage — quantifies org-wide what the VisualDCS 6-root paradigm browser (I10) demonstrates by hand; closes ROADMAP_STATISTICS_ORG_CENSUS L2 row (H817) | 8,054 roots · ~700 KB | `kṛ 107 19827` (root · distinct cells · finite tokens) | 07/26 | [csl-observatory data/paradigm_cell_coverage_per_root.tsv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/paradigm_cell_coverage_per_root.tsv) + [report](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/paradigm_cell_coverage.md) |
| 🟡 E48 | kosha Pāṇinian sūtra↔corpus concordance | W2b inversion of the W2a vidyut-derivation harness: one row per (sūtra, attested DCS form, corpus locus) triple, `ok`-status forms only — 221 distinct sūtras spanning 7/8 adhyāyas, chain length min 6/median 12/max 36 (H1390); ambiguous-status forms (86,857) not yet invertible — W2a's shipped output carries no chain_id for them, parked as a W2a follow-up; manifest tier public, unreleased pending a D-license `@DECIDE` | 893,482 rows · 82.0 MB | `sutra:1.2.45   dcs:651370   asurAn (chain step 1/13)   ok` | 07/26 | [kosha/data/concordance/paninian_concordance.tsv](https://github.com/gasyoun/kosha/blob/main/data/concordance/paninian_concordance.tsv) + [viewer](https://github.com/gasyoun/kosha/blob/main/concordance/panini/index.html) |

### F · Text collections & other

| ID | Asset | What it is | Size | Example (real sample) | Intro | Home |
|---|---|---|---|---|---|---|
| 🟡 F33 | Indische Sprüche | All 7,537 Böhtlingk subhāṣitas as JSONL (public domain) | 7,537 · 6.9 MB | `{ "num":1, "saying_id":"Saying 1", "deva":"अंशो ऽपि दुष्टदिष्टानां…" }` | 07/26 | [indische_sprueche.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl) |
| ⚪ F34 | ortho-drift reform maps | 19th-c.→modern spelling maps: de 15,685 · ru 7,709 · fr 254 · en 71 | ~23.7k forms · 727 KB | `de_reform_map.tsv:   aachner → aachener   (×75)` | 06/26 | [SanskritSpellCheck/ortho_drift](https://github.com/drdhaval2785/SanskritSpellCheck/tree/master/ortho_drift) |
| ⚪ F35 | do-not-file corpus | 2,297 deliberately non-standard headword spellings across 33 dicts | 2,297 · 25 KB | `ABasvara` (deliberately non-standard — do not "correct") | 06/26 | [do_not_file_suppress.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/nochange/do_not_file_suppress.txt) |
| 🟢 F36 | csl-santam Tamil SQLite | MW + Cappeller + Cologne Online Tamil Lexicon combined | 321,620 · 29.9 MB | `source(mwd·cap·otl) · headword · body` (schema; Harvard-Kyoto keys) | 06/15 | [csl-santam](https://github.com/sanskrit-lexicon/csl-santam) |
| ⚪ F37 | OCR'd dictionary front-matter | Faithful Markdown + EN/RU editions of title pages, prefaces, abbreviations | multi-dict | per dict: title-page + preface + abbreviations as Markdown (schema) | 06/26 | [csl-guides](https://github.com/gasyoun/csl-guides) |
| 🟢 F43 | `allngramtxt.txt` char-n-gram oracle | Every distinct character n-gram (all lengths, sorted by length) of the pan-CDSL headword list `sanhw1.txt` — the membership oracle of the n-gram spell-check method (a headword containing a chunk attested nowhere else is suspect; generator [listngrams.py](https://github.com/sanskrit-lexicon/CORRECTIONS/blob/master/ngram/listngrams.py)) | 6,656,616 n-grams · 82.3 MB | `aBisaMboD` (one SLP1 n-gram per line) | 06/26 | [CORRECTIONS/ngram](https://github.com/sanskrit-lexicon/CORRECTIONS/tree/master/ngram) |
| 🟢 F44 | INDOLOGY-L mailing-list archive atlas | Metadata-first atlas of the public INDOLOGY-L Pipermail archive (1990-2026): messages, threads, reply network, author normalization, Renou-axis topic tagging. Split out of IndologyScholars into its own citable repo 19-07-2026 (H460), full history preserved (`git filter-repo`) | 62,115 messages · 24,034 threads · ~200 MB | `data/processed/messages_clean.csv: normalized_author, author_id, primary_topic, thread_root_id, …` | 07/26 | [IndologyArchiveAtlas](https://github.com/gasyoun/IndologyArchiveAtlas) |
| 🟡 F45 | Laukika-nyāya (Jacob's "Handful of Popular Maxims") | All 404 laukika-nyāya popular maxims from Jacob's 3-part collection (1907-1911, PD) as JSONL, OCR-ingested and cross-referenced against the book's own back-matter index, mirroring the IndischeSprueche field style — closes the last open deliverable of the 2004 AIOC-Varanasi manifesto (H803) | 404 · ~500 KB | `{ "num":1, "nyaya_deva":"अजाकृपाणीयन्यायः", "gloss_en":"The maxim of the she-goat and the sword." }` | 07/26 | [laukika_nyaya.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/data/laukika_nyaya.jsonl) |

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
| J14 | [CommentaryStrategies essays](https://github.com/gasyoun/CommentaryStrategies) | Comparative DH essays + TEI/CSV/JSON exports + Sundarakāṇḍa two-tier apparatus pipeline (in production; per-sarga interactive HTML + role guides, see [docs/MANUAL.md](https://github.com/gasyoun/CommentaryStrategies/blob/main/docs/MANUAL.md)) | 🟢 Live | the Mahābhārata translator-commentary comparison | 04/26 | HTML · Python · TEI P5 · [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies) |
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

## V. Drills & practice content — learner-facing exercises

Where sections I–IV catalogue the *research* assets, this section catalogues the **learner-facing
drill content** — the practice sets a student actually works through. IDs use the `P` (pedagogy)
prefix. **~900+ fixed** authored drill items live across **7 repos**, plus several **dynamically
generated** drills (marked *dynamic*) and the 2,181-rule graded sandhi curriculum (P2) the kosha
drills are cut from. The literal word "drill" is rare in the tree — this content lives under
*exercises / quizzes / flashcards / karaoke / SRS*, which is why it went uncatalogued until now.
Drill **generators** (the `sandhi-*` workflow skills) are tooling, not content, and are excluded.

| ID | Drill (what it trains) | Count | Format | Status | Intro | Home |
|---|---|---|---|---|---|---|
| P1 | kosha **sandhi drills** — join / split / identify-class, graded over 10 lessons, corpus-attested with same-class distractors | **396** (132×3) + Anki | JSON·TSV·apkg·web | 🟢 Live | 07/26 | [sandhi_drills.json](https://github.com/gasyoun/kosha/blob/main/data/sandhi/sandhi_drills.json) |
| P2 | kosha **graded sandhi curriculum** — the syllabus behind P1, rules ranked by reading-coverage | 2,181 rules · 10 lessons | TSV·HTML | 🟢 Live | 07/26 | [sandhi_curriculum.tsv](https://github.com/gasyoun/kosha/blob/main/data/sandhi/sandhi_curriculum.tsv) |
| P3 | csl-guides **quiz suite** — sandhi · samāsa · devanāgarī · translit · MW-dictionary · which-dictionary · level-diagnostic · vocabulary | **208 Q** · 8 sets | JSON·React `<Quiz>` | 🟢 Live | 06/26 | [src/data/](https://github.com/sanskrit-lexicon/csl-guides/tree/main/src/data) |
| P4 | Systema **grammar exercise widgets** — gender-sort (24) · noun→pronoun agreement (18) · verb-root match (11) · cloze verb-fill (11) + build-your-own generator | **64** fixed · 4 sets + tool | HTML/JS widgets | 🟢 Live | 07/26 | [public/exercises/](https://github.com/gasyoun/Systema-Sanscriticum/tree/main/public/exercises) |
| P5 | Systema **SRS vocabulary decks** — spaced-repetition Sanskrit vocab (full FSRS engine) | 2 decks · *dynamic* cards | LMS feature | 🟢 Live | 07/26 | [SrsSanskritDeckSeeder.php](https://github.com/gasyoun/Systema-Sanscriticum/blob/main/database/seeders/SrsSanskritDeckSeeder.php) |
| P6 | Systema **Marathon diagnostic quizzes** — letters · vowel-length · real-word · IAST · frequency · sandhi | 14 steps | LMS config + Blade | 🟢 Live | 07/26 | [config/marathon.php](https://github.com/gasyoun/Systema-Sanscriticum/blob/main/config/marathon.php) |
| P7 | SanskritKaraoke **recitation & metre practice** — verse recitation + meter-ID / fill-syllable / beat-tap, with SM-2 verse recall | 13 verses + 3 quiz types (*generated*) | JSON · web player | 🟢 Live | 05/26 | [verses/data/](https://github.com/gasyoun/SanskritKaraoke/tree/main/verses/data) |
| P8 | WhitneyRoots **root↔meaning quiz** — verb-root vocabulary, 4-option MC both directions | 10/round from 935-entry pool (*generated*) | JS web feature | 🟢 Live | 05/26 | [src/core/quiz.js](https://github.com/gasyoun/WhitneyRoots/blob/main/src/core/quiz.js) |
| P9 | VisualDCS **verb-form flashcards** — surface form → root / meaning / tense-type, DCS-frequency ranked | 200 cards | Anki-compact JSON | 🟢 Live | 05/26 | [anki_compact.json](https://github.com/gasyoun/VisualDCS/blob/main/visual/anki_compact.json) |
| P10 | SanskritGrammar **interactive widgets** — SandhiCollider (vowel-sandhi, 7×11 combos) + ablaut / reduplication / heteroclisis / seṭ sandboxes | 5 widgets | React (Docusaurus) | 🟢 Live | 07/26 | [components/talmud/](https://github.com/gasyoun/SanskritGrammar/tree/main/src/components/talmud) |
| P11 | SanskritGrammar **Apte 1885 composition exercises** — Sanskrit composition/translation, digitized classic textbook (prose, not an interactive engine) | ~18 exercises + solved set | MDX textbook | ◐ Digitized | 07/26 | [Apte-Composition1885-final-lessons.mdx](https://github.com/gasyoun/SanskritGrammar/blob/main/ApteSyntax_1885/src/01_Apte/Apte-Composition1885-final-lessons.mdx) |

**Counts.** P1 (396), P3 (208), P9 (200), P4 (64), P6 (14 steps), P7 (13 verses), P11 (~18) are
**fixed** authored items, verified by reading the files. Two are **dynamic**: P5's SRS cards derive
from the runtime `DictionaryWord` table and P8 generates 10 questions/round from its 935-entry
lexicon — neither has a fixed count in-repo. P11's "~18" is a lower bound (count of "exercise"
markers in the MDX). Status: 🟢 live · ◐ digitized (not yet an interactive engine).

**Not drills (out of scope).** The `sandhi-*` workflow skills *generate* drills but hold no content;
inflection engines (csl-inflect, MWinflect, ScharfSandhi, SamudraManthanam `paradigms.py`) produce
paradigms, not learner exercises; "which course suits you" quizzes (ORS-FAQ, the Systema shop) and
BookIndex's Russian-linguistics quiz are not Sanskrit-language drills.

---

## VI. Methods & algorithms — the named procedures behind the assets

Where sections I–V catalogue *what exists*, this section catalogues **how it was computed**: the
named computational methods the project implements, adapts, or consumes — distinct from the *code
files* they live in ([`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)),
the *datasets they output* (§I above · [`datasets.json`](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)),
and the *reproduction recipes* ([`RECIPES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md)).
IDs use the **`Q`** prefix. **Origin:** **N** ours-novel / non-textbook · **S** ours, a standard
method in an in-house implementation · **A** adapted from a named external source · **X** external,
consumed not implemented. Rows collapse tight method-families; the exhaustive ~70-method sweep behind
this section (every path verified) is recorded in
[H1202](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1202-Opus_SanskritLexicography_features-index-methods-algorithms-section-q_17.07.26.md).
Several rows pair with a tool/stack entry above — Q2 ↔ L1 (`sanskrit-util`), Q15–Q16 ↔ M14 (`vidyut`),
Q5 ↔ Charles Li's helayo.

### Transliteration & normalization keys

| ID | Method | What it does | Origin | Home |
|---|---|---|---|---|
| Q1 | Normalization-key family (`norm` / `nfold` / `form_key` / `slp1_norm` / `slp1_simplify`) | Split lookup / compare / fuzzy-fold keys, each trading reversibility vs length- vs case-sensitivity | N | [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py) |
| Q2 | FSM XML transcoder | Finite-state IAST/SLP1/Devanāgarī transcode driven by XML scheme tables (dict builds; 62+ copies) | A | [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/simpleslp/transcoder.py) |
| Q3 | Longest-match roman→SLP1 | Greedy longest-prefix scheme substitution | S | [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/wf1/build_wf_from_dcs.py) |

### Alignment & witness collation (Sa↔Sa)

| ID | Method | What it does | Origin | Home |
|---|---|---|---|---|
| Q4 | Gotoh affine-gap alignment + Sanskrit near-equivalence substitution matrix | Optimal edit-path verse collation scoring ā~a, ṃ~m, ś~ṣ, n~ṇ as *near*, not mismatch | S·N | [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies/blob/main/scripts/spike_helayo_align.py) |
| Q5 | Center-Star multiple-sequence alignment | Multi-witness consensus collation for critical editions | X | [helayo](https://github.com/chchch/sanskrit-alignment) |
| Q6 | Critical-apparatus locus collapse | Aligned columns → readable `lemma ] variant` apparatus notation | N | [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies/blob/main/scripts/build_edition_apparatus.py) |
| Q7 | difflib LCS + token-set Jaccard + asymmetric containment | Verse-similarity / parallel-recovery family (containment chosen over Jaccard for ṭīkā→verse) | S·N | [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies/blob/main/scripts/sa_align.py) |
| Q8 | Char n-gram Jaccard + inverted index | Fuzzy MBH-census match of vulgate verses to App. I print apparatus | S | [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies/blob/main/scripts/verify_mbh_apparatus_against_print.py) |

### Cross-language bitext alignment & translation-memory

| ID | Method | What it does | Origin | Home |
|---|---|---|---|---|
| Q9 | DeepSeek LLM word alignment | Verse-level Sa↔Ru content-word pairing (1.09 M pairs → A1) | X | [build_corpus_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py) |
| Q10 | SimAlign mutual-argmax (mBERT cosine) | Cross-lingual word alignment from subword embeddings | A | [tm_align.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py) |
| Q11 | Composite A/B/C TM grader (+ ref-free QE proxy · consensus · grounding proxy) | Bespoke QE/consensus stack scoring each unit → publication grade A/B/C | N | [tm_grade.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py) |

### Morphology, roots, sandhi & grammar

| ID | Method | What it does | Origin | Home |
|---|---|---|---|---|
| Q12 | Flatten-all CoNLL-U morphology ingest | Dynamic-schema SQLite build; each FEATS/MISC key → its own column | N | [import_dcs_conllu.py](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/import_dcs_conllu.py) |
| Q13 | Three-way root triangulation | MW ↔ Whitney hub ↔ DCS join on the normalised root | N | [root_triangulation.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/root_triangulation.py) |
| Q14 | Homonym disambiguation (gaṇa-overlap + DCS lemma_id token-split) | Attributes corpus counts to the correct homonym via class intersection / DCS's own split | N | [dict_align.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dict_align.py) · [token_disambiguate.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/token_disambiguate.py) |
| Q15 | vidyut it-lopa two-gate paradigm binding | Binds dhātu to homonym via it-lopa derivation history + gaṇa / present-stem corroboration gates | A·N | [vidyut_paradigms.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/vidyut_paradigms.py) |
| Q16 | Preverb (upasarga) segmentation + MW cross-map | Segments a headword into preverb+root, matches MW preverbs | N | [PWG verbs01](https://github.com/sanskrit-lexicon/PWG/blob/master/verbs01/preverb1.py) |
| Q17 | `<ls>` citation-reference splitting + siglum→authority difflib matcher | Splits compound citations into per-part links; fuzzy-links unlinked sigla to canonical authorities | N·S | [link_expand.py](https://github.com/sanskrit-lexicon/MWS/blob/master/mwsissues/issue182/link_expand.py) · [link_candidates.py](https://github.com/sanskrit-lexicon/MWS/blob/master/mwauthorities/link_candidates/link_candidates.py) |
| Q18 | Vowel-sandhi coalescence + ablaut-series calculators | savarṇa / guṇa / vṛddhi / yaṇ surface + grade→surface tables (Whitney/Zaliznyak) | S | [SandhiCollider.jsx](https://github.com/gasyoun/SanskritGrammar/blob/main/src/components/talmud/SandhiCollider.jsx) |

### Classifiers, register, stylometry & phonostatistics

| ID | Method | What it does | Origin | Home |
|---|---|---|---|---|
| Q19 | DCS phono segmentation engine + varga×epoch Cramér's V | IAST→SLP1 akṣara/varṇa/ligature segmentation + diachronic association statistic | N·S | [dcs_phono_engine.py](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Fonetika/regen-2026/dcs_phono_engine.py) · [varga_engine.py](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Fonetika/varga-series-diachrony/varga_engine.py) |
| Q20 | Quantifier metalanguage register "anchoredness" method | Tags gradation quantifiers ANCHORED/UNANCHORED; window-sweep + precision/recall on a hand-scored sample | N | [harvest_quantifiers.py](https://github.com/gasyoun/SanskritGrammar/blob/main/scripts/harvest_quantifiers.py) |
| Q21 | Renou era (I–V) tagger + 20-code register classifier | Multi-label diachronic + genre-register tagging of senses. ⚠ **register classifier is defective** (unanchored `Insch?r` regex spuriously tags `épig`); era tagger has a homograph-collapse caveat | N | [renou.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou.py) · [renou_register.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_register.py) |
| Q22 | Ortho-drift transform-and-check (5 langs) + drift→year dating | Spelling-reform drift detector (Latin = negative control); regresses drift-rate to a date | N·S | [ortho_drift.py](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/detectors/ortho_drift.py) |
| Q23 | SpellCheck detector suite | Cross-lexicon error-mining over a Sanskrit confusion model: faultfinder · consensus/intra_dup/dict_vs_corpus vote · phonotactic · n-gram · noisy-channel · 3-way meter vote | N | [detectors/](https://github.com/drdhaval2785/SanskritSpellCheck/tree/master/detectors) |
| Q24 | Titov parametric core | Quantitative-lexicology core (∪ big-core / ∩ small-core of four parametric cores) | A | [titov_parametric_core.py](https://github.com/gasyoun/Uprava/blob/main/research/titov_parametric_core.py) |

### Search, ranking, OCR & ingestion

| ID | Method | What it does | Origin | Home |
|---|---|---|---|---|
| Q25 | Devanāgarī reverse-dictionary sort | Reverses akṣaras + phonological normalization, then last-letter-first collation | N | [reverse15.php](https://github.com/gasyoun/SanskritSorting/blob/master/reverse15.php) |
| Q26 | Simple-search forgiving lookup | Recursive equivalence-class variant expansion + `ngramValidate` prefix pruning + wf ranking — a recall-first Sanskrit candidate generator | N | [simple_search.php](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/v1.1/simple_search.php) |
| Q27 | Word-frequency ranking (wf0/wf1) + DCS↔CDSL xref | Orders candidates by DCS token counts; builds the DCS↔CDSL linkset (C15) | N | [build_wf_from_dcs.py](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/wf1/build_wf_from_dcs.py) · [build_xref.py](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/dcs_xref/build_xref.py) |
| Q28 | Vision-OCR pipelines (preface + commentary) | LLM vision-OCR of front-matter / translator commentaries → faithful Markdown + corpus (recognition external; orchestration + post-correction ours) | A | [CommentaryStrategies GEMINI.md](https://github.com/gasyoun/CommentaryStrategies/blob/main/docs/GEMINI.md) |
| Q29 | PPV statistical hypothesis pipeline + L1/L2 scholar classification | chi²/Fisher/Kruskal/Spearman over the scholar DB; rule-based discipline classification with uncertainty gating | S·N | [work_ppv_hypotheses.py](https://github.com/gasyoun/IndologyScholars/blob/main/article/work_ppv_hypotheses.py) · [verification.py](https://github.com/gasyoun/IndologyScholars/blob/main/pipeline/verification.py) |
| Q30 | Code-duplication census | Groups every `.py/.sh/.php` by basename + content hash to count copies / versions / drift org-wide | N | [code_duplication_census.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/code_duplication_census.py) |

**Not catalogued here (out of scope).** Trivial glue (file I/O, config parsing, plain string concat);
one-off Python-2 issue-forensics scripts (frozen 2015–2017 correction artifacts); and the *outputs*
of these methods, which are the datasets in §I. The novelty grades are the compiling session's
judgement, not a literature audit — treat **N** as "no off-the-shelf equivalent found," not a
priority claim.

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
| 07/26 | **F45** — Laukika-nyāya (Jacob's "Handful of Popular Maxims") reaches its ≥400-record target, 404 records (H803): a 21-07-2026 `prev_is_prose()` pipeline-wide fix (adversarially verified, 50-agent ultracode workflow) recovers 27 more headword boundaries with zero records lost, closing the last open deliverable of the 2004 AIOC-Varanasi manifesto («Сентенции и афористические цитаты»). |
| 07/26 | **E48** — kosha Pāṇinian sūtra↔corpus concordance (H1390, W2b): inverts the W2a vidyut-derivation harness into one row per (sūtra, attested DCS form, corpus locus) triple — 893,482 rows from 72,764 `ok`-status forms across 221 distinct sūtras, 7/8 adhyāyas; [kosha PR #155](https://github.com/gasyoun/kosha/pull/155) merged, [v0.73.0](https://github.com/gasyoun/kosha/releases/tag/v0.73.0). Independently reviewed PASS same day. Ambiguous-status forms (86,857) parked — not yet invertible from W2a's shipped output. |
| 07/26 | **E47** — witness-independence map + union corroboration re-audit (H1363): operationalizes [FINDINGS §83/§97](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) over the 15-dict union — derivation graph, witness-family partition ([witness_tiers.json](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_tiers.json)), and a P0..P4 collapse ladder recomputing "in N dicts" over independent families. Corroborated share 55.9% → 34.7% when MW folds into the Petersburg witness; Apte kept independent per §83. |
| 07/26 | **F44** — INDOLOGY-L mailing-list archive atlas (62,115 messages, 24,034 threads) split out of IndologyScholars into its own citable repo, [`IndologyArchiveAtlas`](https://github.com/gasyoun/IndologyArchiveAtlas) (H460), full history preserved. |
| 07/26 | **Q1–Q30 · Section VI** — the project's **algorithms & methods** catalogued for the first time (H1202): 30 method-family rows across transliteration/keys, Sa↔Sa alignment & collation, bitext & translation-memory, morphology/roots/sandhi, classifiers/register/phonostatistics, and search/OCR/ingestion, each graded N/S/A/X (novel · standard · adapted · external) with its home file; introduces the `Q` (methods) ID prefix and flags the known-defective Renou register classifier (Q21). Answers "what methods do we use, which are novel, which are external" — previously tracked only obliquely via SHARED_CODE (code), datasets.json (outputs), and RECIPES (reproduction). |
| 07/26 | **P1–P11 · Section V** — learner-facing **drills & practice content** catalogued for the first time: 11 sets across 7 repos (~900+ fixed items), the largest being kosha's 396-item sandhi drill pack (P1), csl-guides' 208-question quiz suite (P3), and VisualDCS' 200-card verb-form deck (P9); introduces the `P` (pedagogy) ID prefix. Excludes the `sandhi-*` drill *generator* skills (tooling, not content). |
| 07/26 | **E43–E46** — H817 WS1.2 closes 3 of 5 descriptive census rows in [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) Part 0 + registers 2 already-done rows the register hadn't caught up to: code-dup census + LOC/language-mix (E43, already done H688, register was stale), POS-per-text (E44, new), sense/polysemy per dict (E45, new, ◐ partial 11/44 — mirrors the A02 paper, the other 33 dicts lack a structural sense-marking convention), paradigm-cell coverage per root (E46, new, 8,054 roots). |
| 07/26 | **Interactive view built** — the promised filterable single-file HTML artifact now exists: [`features_index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/features_index.html), generated from this Markdown by [`build_features_index_html.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/build_features_index_html.py) (search + category tabs + status/tier/language filters, theme-aware, zero-dependency). Closes the 2004-manifesto «Каталог каталогов» deliverable. |
| 07/26 | **C19** — semdom ↔ Amarakosha crosswalk (H742): first SIL-semantic-domains ↔ classical-thesaurus map — Level A varga map (108 ID pairs) + 5,590-synset candidate table + 200-synset dual-annotated gold (κ 0.677); bridge measured as candidate-generator-only (top-1 17.5%, [FINDINGS §76](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)). |
| 07/26 | **E41 · E42 · F43** — the census-named tracked-but-uncounted trio registered (H694): csl-observatory correction-event log (52,498 × 3 views, 178 MB), Kompozity `names.csv` compound splits (168,880, 90.7 MB), CORRECTIONS `allngramtxt.txt` n-gram oracle (6,656,616, 82.3 MB). |
| 07/26 | **E40** — headword pairwise-overlap matrix + unique counts over the 15-dict union (H684): 105 pairs, Jaccard, per-dict unique inventories; resolves the stale "union 94,753" figure (= MW∩PWG). |
| 07/26 | **E39** — markup-tag frequency census over all 44 csl-orig/v02 dicts (H683): 96 distinct tags, per-1,000-entry rates, under-marking verdicts ([TSV](https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv) + [report](https://github.com/gasyoun/SanskritLexicography/blob/master/data/MARKUP_TAG_CENSUS_CSLORIG_2026.md)). |
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
