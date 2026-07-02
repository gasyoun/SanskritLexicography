# Reusable Assets & External Resources for kosha Modernization

_Created: 02-07-2026 · Last updated: 02-07-2026_

---

## Part A: Your Own Repos — What's Already Built

### SamudraManthanam (samskrtam.ru)

**Path:** `C:\Users\user\Documents\GitHub\SamudraManthanam`

**What's here:**
- ✅ **FastAPI backend** (`web/app/main.py`): search service, corpus DB, morphology integration
- ✅ **SQLite FTS5 index** (`web/corpus.db`, `web/corpus.db-offline pack`): full-text search over corpus + dicts
- ✅ **Digitized dictionaries** (gitignored):
  - `dic_mw.jsonl` — Monier-Williams (ready to use)
  - `dic_apte.jsonl` — Apte
  - `kochergina.jsonl` — Russian Kochergina (29k entries)
  - `kossovich.jsonl` — Russian Kossovich (13k entries, PD 1854)
  - `warnemyr.jsonl` — Whitney roots
  - Plus Russian dicts (Knauer, Frish, Smirnov)
- ✅ **Morphological search** via Sanskrit Heritage API (`app/services/morph_service.py`)
- ✅ **Parallel corpus** (~154 texts, verse-aligned Sanskrit–Russian)

**Reuse plan:**
1. Extract `dic_mw.jsonl` + `dic_apte.jsonl` → merge into unified dict index
2. Reuse FTS5 architecture (if happy with it) or migrate to Elasticsearch (if scaling later)
3. Leverage morphology API for form expansion
4. Query corpus via existing API for citations/usage examples

**Potential improvements:**
- Currently no encoding toggle → add SLP1↔IAST↔Devanagari client-side transcoding
- No multi-dict unified view → build aggregation layer
- Search latency not measured → add Prometheus metrics

---

### SanskritLexicography

**Path:** `C:\Users\user\Documents\GitHub\SanskritLexicography`

**What's here:**
- ✅ **Union headword lists** (`HeadwordLists/`): 
  - MW unique headwords (193,978)
  - PWG unique headwords (106,085)
  - Intersection/union files
  - Homonym disambiguation files
- ✅ **Russian translation of MW** (`RussianTranslation/mw_ru.md` + output data)
  - 287,358 translated cards
  - Multi-pass LLM pipeline documented
  - Validation checksums
- ✅ **Etymology data** (in csl-atlas, cited from this repo):
  - Root crosswalks (Whitney roots ↔ Cologne lemmas)
  - Derivative chains (√ → headword)
  - Comparative etymology (PWG vs MW etymology components)
- ✅ **Corpus lexicon** (`RussianTranslation/src/corpus_lexicon.jsonl`):
  - 1.09M word-aligned Sa↔Ru pairs
  - Lemma coverage statistics
- ✅ **Frequency bands** (via VisualDCS adapter):
  - Lemma frequency quintiles (common/frequent/rare/archaic/hapax)
  - Useful for sense ranking

**Reuse plan:**
1. Union headword list → seed kosha lemma inventory
2. Frequency bands → rank senses by usage likelihood
3. Etymology data → if structured, populate etymology tree
4. Russian translation → enrich multilingual view (optional)

**Potential improvements:**
- Not yet in a structured API format → export headword lists as JSON for kosha
- Etymology data scattered across docs → consolidate into schema

---

### Sanskrit-Util (Shared Library)

**Path:** `C:\Users\user\Documents\GitHub\sanskrit-util`

**What's here:**
- ✅ **SLP1↔IAST↔Harvard-Kyoto↔Devanagari transcoders** (Python + JavaScript)
- ✅ **String normalization** (length-preserving, without losing retroflex/vowel info)
- ✅ **Siglum/abbreviation mappings** (Sanskrit → English names)

**Reuse plan:**
1. Use JS version (`sanskrit-util/js/...`) for client-side encoding toggle
2. Use Python version for backend normalization (form_key(), etc.)
3. Reference its transcodification rules to avoid reimplementing

---

### SanskritSpellCheck

**Path:** `C:\Users\user\Documents\GitHub\SanskritSpellCheck`

**What's here:**
- ✅ **Spelling correction** (19th-century to 2026 orthographic drift detector)
- ✅ **Normalization rules** (by language: Sanskrit → RU/DE/FR/LA variants)

**Reuse plan:**
- Optional: detect & suggest "did you mean?" for typos (e.g., "dharma" vs "darma")
- Low priority for v1; defer to Phase 5

---

### WhitneyRoots (Separate Repo, Sibling)

**Expected path:** `C:\Users\user\Documents\GitHub\WhitneyRoots` (if present)

**What it likely contains:**
- ✅ Whitney root inventory (938 roots)
- ✅ Gaṇa / pada classifications
- ✅ Crosswalk: Whitney root ↔ Cologne lemmas
- ✅ Paradigm data (inflection forms per root)

**Reuse plan:**
1. If building "root browser" feature → link to WhitneyRoots
2. If showing grammatical info (gaṇa, pada) → query WhitneyRoots data
3. Root identity is a key reuse point between kosha and learner's reading layer

---

### csl-atlas (External, Cologne Org)

**Path:** `https://github.com/sanskrit-lexicon/csl-atlas`

**What's there:**
- ✅ **Structural analysis of all Cologne dicts**: macrostructure, microstructure
- ✅ **Sense alignments (R2 layer)**: MT-to-human aligned senses across dicts
- ✅ **Etymology extraction**: root-to-derivative chains
- ✅ **Citation apparatus**: canonical siglum table, aliases
- ✅ **Evidence grading**: observations, derivations, inferences per claim
- ✅ **Learner's reading layer**: frequency-graded sense filtering

**Reuse plan:**
1. **Sense alignment (R2):** If public, join to kosha senses (group MW sense 1 = PWG sense 2, etc.)
2. **Citation siglum table:** Essential for hyperlinked `<ls>` tags
3. **Frequency-graded filtering:** For learner view (show sense 1–2 only, hide archaic senses)
4. **Etymology data:** If exported as JSON, populate etymology tree
5. **Evidence grades:** Optional, but scholarly users love provenance

**Integration blocker:** Check whether csl-atlas is published; if not, may need to ingest via mirror or direct copy.

---

### csl-observatory (External, Cologne Org)

**Path:** `https://github.com/sanskrit-lexicon/csl-observatory`

**What's there:**
- ✅ **Cross-repo metrics**: correction counts, contributor stats
- ✅ **Changelog entries**: categorized corrections (text-correction, encoding, etc.)
- ✅ **Issue typology analytics**: bug/question/markup/enhancement counts

**Reuse plan:**
- Optional: show "last updated" timestamp for each dict in kosha (from csl-observatory)
- Scholarly users want to know: "is this entry based on the 2020 revision or 2026?"

---

### csl-orig (External, Cologne Org)

**Path:** `https://github.com/sanskrit-lexicon/csl-orig`

**What's there:**
- ✅ **Canonical source files** (per dictionary):
  - `v02/mw/mw.txt` (MW)
  - `v02/pwg/pwg.txt` (PWG)
  - `v02/ap90/ap90.txt` (Apte)
  - `v02/gra/gra.txt` (Grassmann)
  - etc.
- ✅ **XML schemas** (for validation)
- ✅ **Build pipeline** (XML generation via `csl-pywork`)

**Reuse plan:**
1. **Nightly sync**: clone/pull latest csl-orig; rebuild kosha index
2. **Revision tracking**: commit hash of csl-orig → stored in kosha metadata
3. **Validation**: reuse existing XML validation before indexing

---

## Part B: External Open-Source Resources

### Sanskrit Heritage Search (API)

**URL:** `https://sanskrit.inria.fr/` (backend API)

**What it provides:**
- ✅ Morphological analysis (lemmatization, conjugation forms)
- ✅ Compound splitting
- ✅ Sandhi analysis

**Current usage:** samskrtam.ru already uses this for morphological search. **Status:** free, academic, no API key needed.

**Reuse plan:**
- Already in use via `morph_service.py`; no changes needed
- Note: may be rate-limited; monitor usage if kosha traffic scales

---

### Vedaweb (External)

**URL:** `https://vedaweb.uni-zurich.ch/`

**What it provides:**
- ✅ Rigveda with accents (Zaliznyak system)
- ✅ Per-word morphology (Cologne DCS)
- ✅ Hyperlinked dictionary entries (to C-SALT MW)

**Reuse plan:**
- Optional: deep link from kosha RV lemmas to Vedaweb
- Show Vedic accent (á ā à) if user is looking up Rigvedic words
- Low priority; defer to Phase 5

---

### Lexonomy (Lexical Database Tool)

**URL:** `https://lexonomy.ds.uzh.ch/`

**What it provides:**
- ✅ Open-source lexical database software
- ✅ XML-based dictionary editing
- ✅ User management, versioning, export

**Reuse plan:**
- Not needed for v1 kosha (you're not building an editing interface)
- Relevant only if you later want scholar contributors to edit entries (Phase 6+)
- Watch for ideas on dict representation

---

### OntoLex-Lemon (Standard)

**What it is:**
- W3C standard for representing lexical data in RDF/OWL
- Used by ELEXIS and other FAIR lexical resources

**Reuse plan:**
- Optional: export kosha data as OntoLex (RDF) for scholarly interoperability
- Deferred to Phase 5; not urgent for MVP
- Supports reusability across scholarly tools

---

### Open Sanskrit Project (GitHub)

**URL:** `https://github.com/orgs/sanskrit-coders/`

**What's there:**
- ✅ Sanskrit corpus tools
- ✅ Morphological analyzers
- ✅ Text processing libraries

**Reuse plan:**
- Check if any morphology tools are better than Sanskrit Heritage
- May have overlapping code; worth a quick audit

---

## Part C: Data Files You Should Export/Generate

### Priority 1 (Needed for Phase 1)

1. **`dict_inventory.json`** — from SanskritLexicography
   ```json
   {
     "dictionaries": [
       { "code": "mw", "name": "Monier-Williams", "headwords": 193978, "records": 207000 },
       { "code": "pwg", "name": "PWG", "headwords": 106085, "records": 180000 },
       ...
     ]
   }
   ```

2. **`union_headwords.tsv`** — from HeadwordLists
   ```
   slp1_key   iast        dict_coverage       frequency_band
   dharma     dharma      mw,pwg,ap90         common
   bhagavat   bhagavat    mw,pwg              frequent
   ...
   ```

3. **`frequency_bands.json`** — from VisualDCS
   ```json
   {
     "lemmas": [
       { "slp1": "dharma", "band": "common", "rank": 1, "corpus_count": 45000 },
       ...
     ]
   }
   ```

### Priority 2 (Needed for Phase 2–3)

4. **`senses_aligned.json`** — from csl-atlas (if available)
   ```json
   {
     "alignments": [
       {
         "mw_sense_id": "mw1-001",
         "pwg_sense_id": "pwg1-001",
         "confidence": 0.95,
         "gloss_english": "duty, law"
       }
     ]
   }
   ```

5. **`etymology_chains.json`** — from csl-atlas or reconstruct
   ```json
   {
     "dharma": {
       "root": "dhṛ",
       "chain": ["dhṛ", "dharaṇa", "dharma"],
       "sources": ["pwg:X.Y"]
     }
   }
   ```

6. **`siglum_table.json`** — from Cologne citation apparatus
   ```json
   {
     "BhG": { "full_name": "Bhagavad-Gītā", "alt_names": ["BGS", "Bg."], "corpus_id": "bhagavad-gita" },
     "MBh": { "full_name": "Mahābhārata", "alt_names": ["Mbh.", "MBh."], "corpus_id": "mahabharata" },
     ...
   }
   ```

### Priority 3 (Nice-to-have for Phase 4+)

7. **`learner_reading_layer.json`** — from csl-atlas learner layer
   ```json
   {
     "lemma": "dharma",
     "frequency_band": "common",
     "primary_senses": [
       { "sense_id": "1", "definition": "duty, law", "freq_rank": 1 },
       { "sense_id": "2", "definition": "justice", "freq_rank": 2 }
     ],
     "grammar": { "gender": "m.", "class": "root-noun" }
   }
   ```

---

## Part D: GitHub Searches for Related Projects

### Search queries (to find similar implementations):

```bash
# Python Dict/Lexicon projects
github: "sanskrit" "dictionary" "python" "fastapi"
github: "kollegienforschung" "lexicon" "flask"

# Sanskrit morphology/NLP
github: "sanskrit" "morphology" "lemmatization"
github: "sanskrit-coders" "morphology"

# Multilingual dict lookup
github: "multilingual" "dictionary" "search" "rest-api"
github: "lexicography" "digital" "json"

# Static site generators for reference docs
github: "dictionary" "static" "jekyll"
github: "reference" "sphinx" "build"
```

### Known related projects (curated list):

| Project | Language | Focus | Relevant For |
|---------|----------|-------|---|
| **Sanskrit Heritage Search** | Java/C | Morphology API | Form expansion, reuse existing |
| **Vedaweb** | JavaScript/React | Vedic corpus + linked dict | Optional deep-linking Phase 5 |
| **Cologne DCS** | Python/XML | Corpus tools, frequency | Frequency band integration |
| **Sanskrit-Coders projects** | Python | Morphology libraries | Alternative to Sanskrit Heritage |
| **ELEXIS** | n/a | FAIR standards | Export/interop Phase 5 |

---

## Part E: Build & Deployment Tools You Already Have

### Python Tools (in your repos)

- ✅ `updateByLine.py` — apply corrections to dict files (reuse for correction ingestion)
- ✅ `diff_to_changes_dict.py` — track changes between dict versions (for revision history)
- ✅ `make_xml.py` (csl-pywork) — validate XML (use before indexing)

### Build Tools

- ✅ `.github/workflows/` (CI/CD) — already set up for SanskritLexicography; reuse for kosha
- ✅ `pre-commit` hooks — use for data validation

### Deployment Options

- ✅ samskrtam.ru domain + FastAPI server (already live)
- ✅ GitHub Pages + static exports (for kosha static HTML, if needed)
- ✅ GitHub Releases + Docker image (package kosha as a container)

---

## Summary Checklist

Before starting Phase 1, **ensure you have**:

- [ ] Access to SamudraManthanam `dic_mw.jsonl` + `dic_apte.jsonl` (extract & verify)
- [ ] Latest csl-orig snapshot (clone or sync)
- [ ] Union headword lists from SanskritLexicography (or regenerate)
- [ ] VisualDCS frequency bands (or derive from corpus)
- [ ] Confirmation from you: answers to 6 strategic decisions (Part III of KOSHA_LOOKUP_ROADMAP.md)
- [ ] Access to csl-atlas data (check if public/private; if private, plan extraction)
- [ ] Cologne citation siglum table (may need to extract from existing sources)

---

_Dr. Mārcis Gasūns_
