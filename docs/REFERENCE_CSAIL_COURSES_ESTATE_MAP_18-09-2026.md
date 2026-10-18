# CSAIL courses × Sanskrit-lexicography estate map

_Created: 18-09-2026 · Last updated: 18-09-2026_

**Purpose.** Durable answer to MG's question «что могло бы помочь нам на courses.csail.mit.edu» — which MIT CSAIL course material maps onto the estate's actual workloads, grounded in [DATA_LAYERS_CENSUS.md](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md), [PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md) and [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md). Provenance: course pages fetched 18-09-2026 ([roster](https://courses.csail.mit.edu), [6.851 Spring'21](https://courses.csail.mit.edu/6.851/spring21/)).

**Outcome already minted:** the four highest-value 6.851 units were minted as H5136–H5139 (all OxAlpha, free lane) and executed the same day — study notes + runnable prototypes in [Uprava docs/](https://github.com/gasyoun/Uprava/blob/main/docs/):

1. [6851-l15-lca-rmq-study_2026-09.md](https://github.com/gasyoun/Uprava/blob/main/docs/6851-l15-lca-rmq-study_2026-09.md) — H5136, O(1) RMQ machinery, 10,000-query selftest PASS.
2. [6851-l16-suffix-array-doc-retrieval_2026-09.md](https://github.com/gasyoun/Uprava/blob/main/docs/6851-l16-suffix-array-doc-retrieval_2026-09.md) — H5137, SA + doc retrieval over 4 Cologne dicts, 5/5 patterns PASS; verdict: SA layer is a *concordance* layer for the DCS master, not a tgrep replacement.
3. [6851-l17-l18-succinct-tries_2026-09.md](https://github.com/gasyoun/Uprava/blob/main/docs/6851-l17-l18-succinct-tries_2026-09.md) — H5138, LOUDS trie over all 12,785 gra.txt headwords at **0.47× raw size**, PASS.
4. [6851-l10-hashing-headword-lookup_2026-09.md](https://github.com/gasyoun/Uprava/blob/main/docs/6851-l10-hashing-headword-lookup_2026-09.md) — H5139, FKS perfect hashing vs dict: **dict wins**, the honest expected outcome, PASS.

---

## Part 1 — the 6.851 four, mapped estate-wide

| 6.851 unit | Estate workload it hits | Concrete assets |
|---|---|---|
| **STRINGS** — «searching for phrases in giant text» (suffix arrays, FM-index, [L15–L16](https://courses.csail.mit.edu/6.851/spring21/lectures/L16.html)) | indexed search, concordances, spell-check oracle | `tgrep` over `csl-lnum`/`csl-ldev` (1.3–1.4M files, ~1s vs rg minutes); F43 n-gram oracle (6,656,616 SLP1 n-grams, [CORRECTIONS/ngram](https://github.com/sanskrit-lexicon/CORRECTIONS/tree/master/ngram)); kosha.db (1.38M forms / 6.9M inflections); FTS5 in [vk-ors](https://github.com/gasyoun/IndologyScholars/tree/main/vk-ors); `csl-apidev` PHP+SQLite search |
| **SUCCINCT** — near-raw-size structures ([L17–L18](https://courses.csail.mit.edu/6.851/spring21/lectures/L18.html)) | the local-only giants | `archive_stopword.sqlite` (11 GB, 40.57M stop-word parallels), `dcs_full.sqlite` (5.69M tokens), `SamudraManthanam corpus.db` (580,552 verse parallels) — rank/select + compressed encodings cut these by an order of magnitude without API change (H5138 measured 0.47× on real headwords) |
| **TIME TRAVEL** — persistence & retroactivity ([L15 intro units](https://courses.csail.mit.edu/6.851/spring21/lectures/L15.html)) | the correction model, estate-wide | E41 `correction_events_{all,typed,final}.csv` = **52,498 events × 44 dicts × 210 correctors** ([csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory)); the `CORRECTIONS`/`csl-corrections` change-file audit trail; every late re-correction is a retroactive op — the lectures say which retroactive queries are cheap vs provably hard |
| **MEMORY HIERARCHY** — cache-oblivious algorithms | batch passes | the 31.58 GB `os.walk` harvests (1,599 large files), `generate_dict.sh` XML rebuilds ×44, `updateByLine.py` sweeps (×144 vendored copies per E43-dup census), Yandex inventory scans (224.5 GB) |

## Part 2 — other CSAIL courses on that server that map

| Course | Estate workload | Evidence |
|---|---|---|
| [6.046](https://courses.csail.mit.edu/6.046/) / [6.854](https://courses.csail.mit.edu/6.854/) Advanced Algorithms | sequence alignment — the estate's repeated pattern | `helayo` MSA collation (Sanskrit-aware substitution matrices, [SAMSAADHANII_INDEX](https://github.com/gasyoun/SanskritLexicography/blob/master/SAMSAADHANII_INDEX.md) sibling); Samudra AVŚ verse joins 4,031/4,516 (H4743); Bloomfield×Elizarenkova 36,680 rows (H4731); 1.09M-row `corpus_lexicon` Sa→Ru alignment; E50 Rāmāyaṇa edition maps |
| [6.856J](https://courses.csail.mit.edu/6.856/) Randomized Algorithms | near-duplicate detection done right | Renou-variant divergences 3–23% (H692/H771), byte-identical twin hunts across 1,599 large files (MinHash/fingerprinting instead of full SHA compare cascades); Bloom filters = F43's membership oracle at kilobyte scale |
| [6.871](https://courses.csail.mit.edu/6.871/) Knowledge Based Application Systems | the ontology layer already in production | OntoLex-Lemon/FrAC/RDF + SPARQL + SHACL in [csl-standards](https://github.com/sanskrit-lexicon/csl-standards); C19 semdom↔Amarakosha crosswalk; Amarakosha knowledge net in Samsaadhanii |
| [6.867](https://courses.csail.mit.edu/6.867/) Machine Learning | eval methodology, not model training | F48 defgen benchmark already worries about contamination («MW 1899 is in every model's pretraining data»), judge calibration, floor arms — the course is the formal grounding for the discipline invented ad hoc |
| [6.801/6.866](https://courses.csail.mit.edu/6.866/) Machine Vision | the scan-index campaign | 37 scan repos ≈ 11.2 GB page images ([F47 tracker](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data/pwg_scan_index_tracker), 55/82 works indexed); tesseract-5 `san` OCR (Gorresio image-only volumes, E50) |
| [6.197](https://courses.csail.mit.edu/6.197/) Performance Engineering | parallelizing the batch lanes | the Part-1 MEMORY HIERARCHY row; pairs with 6.851's cache-oblivious unit |

## Part 3 — skip without regret

6.033, 6.034, 6.821, 6.825, 6.846, 6.869, 6.888, 16.410, HST.947, the robotics/vision-lab classes and the IAP sessions — no matching estate workload. (IAP [Hacking a Google Interview](https://courses.csail.mit.edu/iap/interview/) is a fun weekend at most.)

## Part 4 — standing next steps

1. If the L16 verdict is pursued: an SA-IS concordance prototype over the DCS master (5.69M tokens) in compiled form — that is a new mint, not this doc.
2. SUCCINCT production form = a compiled rank/select library (sdsl-class) whenever one of the §2 giants needs an in-RAM index; the H5138 note fixes the encoding shape.

_Гасунс_
