# SAMSAADHANII_INDEX.md — what Amba Kulkarni's SCL toolchain teaches our repos

_Created: 02-07-2026 · Last updated: 02-07-2026_

**Prior-art index (external).** [Amba Kulkarni](https://sanskrit.uohyd.ac.in/faculty/amba/)
(Prof. & Head, Dept. of Sanskrit Studies, University of Hyderabad) leads
**Samsaadhanii / Sanskrit Computational Linguistics (SCL)** — the most mature
computational-Sanskrit toolchain outside our own ecosystem. This file exists so a
future session (or Fable) **consumes what SCL already built instead of reinventing
it**, and knows which of our repos each capability maps onto.

It lives in [`SanskritLexicography`](https://github.com/gasyoun/SanskritLexicography) —
the Sanskrit-NLP umbrella repo — because the tools indexed here (segmentation,
morphology, compound/parse, root & synonym networks) are exactly the NLP layers new
subfolders of this repo will lean on. Same spirit as the internal reuse hubs
[`SHARED_CODE.md`](https://github.com/gasyoun/github-spine) ("don't write transcoder
#63") and [`Uprava/PROJECT_INTERLINKS.md`](https://github.com/gasyoun/github-spine)
(internal data-flow) — but for an **external** toolchain we should link into, not clone.

---

## Where it lives

| Resource | URL |
|---|---|
| Faculty page (bio, publications, theses, lecture notes) | https://sanskrit.uohyd.ac.in/faculty/amba/ |
| SCL platform (all live tools) | https://scl.samsaadhanii.in/scl/ |
| SCL mirror | https://sanskrit.uohyd.ac.in/scl/ |
| **Source code (GPL, reusable)** | https://github.com/samsaadhanii |
| Course "Samsaadhanii Praveshikaa" lecture notes | https://sanskrit.uohyd.ac.in/IOE-2024/lecture_notes.html |
| ORCID | https://orcid.org/0000-0001-7617-3918 |

**License note.** SCL code on GitHub is GPL — we can study, run, and adapt it, but
GPL-derived code cannot be silently vendored into a permissive/unlicensed repo. Prefer
**calling the live services** or cross-validating against their **data outputs** over
copying source.

---

## Capability → SCL tool → our repo (the reuse map)

| SCL capability | Their tool | Consume it in… | Concrete action |
|---|---|---|---|
| **surface form → lemma + full morphology** (sandhi split first) | Morphological Analyzer + Segmenter | [`RussianTranslation`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) glossary layer, [`VisualDCS`](https://github.com/gasyoun/VisualDCS) | We already fall back to `vidyut.kosha` + DCS form→lemma (~87% token coverage). SCL is a **second independent analyzer** — use to raise coverage / adjudicate disagreements, don't build a third. |
| **compound (samāsa) split** | Compound Processor (analyzer + generator) | RussianTranslation, dict frontends | Our glossaries choke on compounds; SCL's constituency/dependency split is the reference implementation — call it before hand-rolling a splitter. |
| **kāraka / dependency parse** (constraint-based, Pāṇinian) | Sanskrit Dependency Parser | [`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) etymology extractors (SKD/VCP kāraka), corpus alignment | Our kāraka-derivation extractors and Sa→Ru alignment can **validate** against SCL's parser output as gold-ish structure. |
| **word-by-word interlinked reader** that already pulls **Cologne dictionaries** (MW etc.) | Sanskrit Reading Aid | our `csl-app` / dict-web frontends | This is the model UX for dictionary lookup: text → segment → morph → dict gloss, all clickable. Study it before designing any new reader; note **they already integrate our dictionaries** — a downstream consumer to be aware of. |
| **synonym / semantic network** | Amarakosha Knowledge Network (jñāna-jāla) | headword crosswalks, [`SanskritLexicography`](https://github.com/gasyoun/SanskritLexicography) | A ready structured thesaurus graph — link our headwords into it for synonyms/sense-linking instead of mining synonyms from scratch. |
| **verb-root authority** | Pāṇinīya Dhātupāṭha e-concordance + Dhātuvṛtti concordance | `mw_roots.tsv` (SHARED_CODE §11), [`WhitneyRoots`](https://github.com/gasyoun/WhitneyRoots), grammar crosswalk | A third independent root source — **cross-validate** our MW/Whitney/DCS root crosswalk against it; flag divergences, don't overwrite reviewed data. |
| **normalized DCS + normalized Ṛgveda-saṃhitā** | SCL validation/normalization datasets | [`VisualDCS`](https://github.com/gasyoun/VisualDCS), VedaWeb work | Their normalization decisions are a cross-check for our DCS ingest (occ-id / lemma normalization gotchas). |
| **inflection / paradigm generation** | Subanta/Tiṅanta generators, Aṣṭādhyāyī simulator | grammar/paradigm display (currently `vidyut`) | Pāṇinian generator as an alternative/validator to vidyut paradigms. |

---

## Deep dive 02-07-2026 — what the index missed

### 1. The `datasets` repo — gold kāraka treebanks + DCS×Heritage alignment

[github.com/samsaadhanii/datasets](https://github.com/samsaadhanii/datasets) —
**not code, data** — three folders:

- [`Annotated-data/`](https://github.com/samsaadhanii/datasets/tree/main/Annotated-data)
  — ~15 human-annotated texts as word-level CSVs (WX notation): **Sundarakāṇḍa
  (6.5 MB)**, Ṛgveda (4.2 MB), Bhagavadgītā, Kumārasambhava, Raghuvaṃśa, two MBh
  parvans, Upaniṣads, Aṣṭāṅgahṛdaya, Līlāvatī… Columns: `anvaya_no, word,
  sandhied_word, morph_analysis, morph_in_context, kaaraka_sambandha,
  possible_relations, sloka refs`. This is a **gold dependency treebank with
  disambiguated morphology** — note the morph analysis carries the **verb class
  (gaṇa)**, e.g. `iR1{karwari;lit;…;xivAxiH}`.
- [`dcs_sh_alignment/parallel_corpus/`](https://github.com/samsaadhanii/datasets/tree/main/dcs_sh_alignment/parallel_corpus)
  — **130,270 DCS sentences with ground-truth segmentation** (IAST TSV, 14 MB)
  from aligning DCS with the Sanskrit Heritage Segmenter; per-sentence graphml
  segmentation lattices + JSON analyses on Google Drive.
- [`dcs_sh_alignment/frequencies/`](https://github.com/samsaadhanii/datasets/tree/main/dcs_sh_alignment/frequencies)
  — word/compound-component frequency tables **plus sandhi-transition frequency
  tables** (`pada_trans_freq.tsv`, `comp_trans_freq.tsv`) and
  (stem, inflection, base, derivation) tuple frequencies.

⚠️ **The `datasets` repo has no LICENSE file** — rights unclear; ask upstream
before redistributing (validation-only local use is the safe default).

### 2. JSON APIs — documented, callable today

[API_DOC.pdf](https://sanskrit.uohyd.ac.in/scl/API_DOC/API_DOC.pdf) documents
CGI endpoints returning JSON, all accepting `encoding`/`outencoding`
(WX/SLP/KH/IAST/Unicode/Itrans):

| Tool | Endpoint |
|---|---|
| Morphological analyzer | `https://sanskrit.uohyd.ac.in/cgi-bin/scl/morph/morph.cgi` |
| Sandhi splitter | `https://sanskrit.uohyd.ac.in/cgi-bin/scl/MT/prog/sandhi_splitter/sandhi_splitter.cgi` |
| Sandhi joiner | `https://sanskrit.uohyd.ac.in/cgi-bin/scl/sandhi/sandhi_json.cgi` |
| Verb generator | `https://sanskrit.uohyd.ac.in/cgi-bin/scl/skt_gen/verb/verb_gen.cgi` |
| Noun generator | `https://sanskrit.uohyd.ac.in/cgi-bin/scl/skt_gen/noun/noun_gen.cgi` |
| Anusaaraka MT (Sa→Hi) | `https://sanskrit.uohyd.ac.in/cgi-bin/scl/MT/anusaaraka.cgi` |

So "call the live service" is not hypothetical — batch adjudication scripts can
hit these directly (be polite: cache, throttle, identify ourselves).

### 3. Data folders inside the GPL `scl` repo

[`amarakosha/`](https://github.com/samsaadhanii/scl/tree/master/amarakosha),
[`dhaatupaatha/`](https://github.com/samsaadhanii/scl/tree/master/dhaatupaatha),
[`kosha_concordance/`](https://github.com/samsaadhanii/scl/tree/master/kosha_concordance)
live inside the GPL-licensed source repo — the **data** there (synonym graph,
root concordance) is what we'd diff against; GPL covers the code, but treat the
data as GPL too until clarified with upstream.

---

## The five things it actually teaches us

1. **Don't build a Sanskrit morphological analyzer, sandhi splitter, or compound
   splitter from scratch.** SCL (plus [`vidyut`](https://github.com/ambuda-org/vidyut))
   already own this. Our job is dictionaries + translation + alignment — call theirs,
   adjudicate between them.
2. **The Reading Aid is the reference UX** for turning a dictionary into a reader:
   text → segment → morph → *our* gloss. And it **already consumes Cologne data**, so
   we are upstream of them — a reason to keep our exports clean and stable.
3. **Amarakosha Knowledge Network** is a free structured synonym/sense graph — a
   linking target for our headwords, not something to re-mine.
4. **Their Dhātupāṭha/root concordances are a third witness** for the MW/Whitney/DCS
   root crosswalk — treat as validation, never as an overwrite of human-reviewed data
   (per the data-integrity rule).
5. **Interoperability by transliteration:** SCL accepts SLP1/WX/IAST/Devanāgarī/KH
   interchangeably — same discipline our
   [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) enforces;
   confirms SLP1 as the safe interchange key.

---

## For Fable / next session — how to reuse this

- **Recall trigger:** anything touching *segmentation, sandhi, morphology, compounds,
  dependency/kāraka parsing, root authority, or a "Sanskrit reader" UX* → open this file
  first and prefer an SCL call over a new implementation.
- **Before coding a Sanskrit-NLP helper:** check (a) `vidyut` / `sanskrit-util`
  internally, then (b) this SCL map. Two independent engines already cover most needs.
- **When validating a derived asset** (root table, lemma map, parse): SCL is an
  independent gold-ish witness — diff against it, log divergences, don't auto-correct
  canonical data.
- **License gate:** live-service call or data cross-check = fine; copying GPL source
  into our repos = ask first.

_Dr. Mārcis Gasūns_
