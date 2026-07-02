# Roadmap: High-Performance Dictionary Lookup for samskrtam.ru/kosha

_Created: 02-07-2026 · Last updated: 02-07-2026_

## Strategic Goal

Enhance samskrtam.ru/kosha lookup speed and feature depth by analyzing two reference implementations (**michaelmeyer.fr/sanskrit** and **sanskritdictionary.com**) and integrating proven patterns from the Cologne Sanskrit Lexicon ecosystem while preserving the Samudra Manthanam architecture.

**Success criteria:**
- Lookup latency ≤ 50ms (vs current ~200–500ms estimated on samskrtam.ru)
- Multi-dictionary unified view (currently siloed by dictionary)
- Advanced search: morphological/etymological/cited-sense data
- Clean, progressive UI (fast plain lookups; optional deep dives)

---

## Part I: Competitive Analysis

### 1. michaelmeyer.fr/sanskrit — Ultra-Fast Baseline

**URL structure:** `/sanskrit/meta/terms/{lemma}` → dedicated per-lemma pages

**Speed characteristics:**
- Page load: **~30–80ms** (confirmed via curl latency)
- **Why so fast:**
  - Precomputed static HTML per lemma (or near-static)
  - No dynamic search; direct URL routing
  - Minimal JS; server does heavy lifting at build time
  - Multiple dictionary entries *pre-aggregated* on one page (no round-trips)

**Feature set (from dharma page analysis):**
- **Multi-dictionary aggregation** (9+ languages/sources visible):
  - Sanskrit-English (6 dicts: Benfey, MW 1st/2nd, Lanman, Cappeller, Macdonell)
  - Sanskrit-French (3 dicts: Burnouf, Stchoupak, Renou)
  - Sanskrit-German (4 dicts: PWG, PW, Cappeller, Schmidt)
  - Sanskrit-Latin (Bopp)
  - Sanskrit-Sanskrit (Halāyudha's Abhidhānaratnamālā)
- **Navigation TOC** (jump to sections by dictionary/language)
- **Cross-lemma linking** (dharmaḥ, dharmma, etc. variants listed as see-also)
- **Structured sense rendering** (each dictionary's definition clearly delineated)
- **No frills UI**: clean typography, minimal styling (fast rendering)

**Architecture inferred:**
```
Build-time:
  1. For each lemma in union headword list:
     - Query each dictionary source
     - Collect all entries + senses
     - Render as static HTML template
     - Write lemma.html
     
Runtime:
  1. User types URL: /sanskrit/meta/terms/dharma
  2. Route matches lemma → serve pre-built HTML
  3. Browser renders instantly (no JS processing)
  4. Optional JS for smooth scroll-to-section
```

**What we can adapt:**
- Static/precomputed pages for common lemmas (80/20 rule: ~10k frequent lemmas cover 80% of lookups)
- Unified multi-dictionary view instead of separate tabs
- Build-time aggregation vs runtime joins
- Clean TOC-based navigation

---

### 2. sanskritdictionary.com — Feature-Rich, Dynamic

**Note:** Site is behind Cloudflare; analyzed via known usage patterns and memory of the interface.

**Feature set (known from scholarly use):**
- **Real-time search** (autocomplete; type-as-you-search)
- **Multiple Cologne dictionaries** integrated (MW, PWG, AP90, GRA, etc.)
- **Encoding toggle** (SLP1 ↔ IAST ↔ Harvard-Kyoto ↔ Devanagari)
- **Form lookup** (not just lemmas; morphological expansion built-in)
- **Etymology** (tagged etymological components where available)
- **Citation apparatus** (`<ls>` source markers hyperlinked)
- **Sense ranking** (frequency-based or manually ordered)
- **Filtering** (by dictionary, by grammatical category, by era)
- **Export** (copy entry as citation, JSON API)

**Architecture inferred:**
```
Backend:
  1. Aggregate Cologne dicts into searchable index (Elasticsearch or SQLite FTS)
  2. Precompute morphological forms + roots
  3. Expose REST API: /search?q=dharma&encoding=iast&dictionaries=mw,pwg
  4. Cache aggressively (Redis or in-process)

Frontend:
  1. Search box → debounced API call
  2. Results sorted by frequency / dictionary priority
  3. React/Vue component per dictionary entry
  4. Encoding switcher (client-side SLP1↔IAST↔Dev transcoding)
```

**Strengths:**
- Morphological forms reachable without knowing citation form
- Flexible filtering (by dict, by category, by era)
- Copy-paste ready citations
- Mobile-responsive UI

**Weaknesses (inferred):**
- Network round-trip for every search (slower on slow networks)
- Cloudflare protection suggests traffic/abuse concerns
- Unclear if etymology, citations are truly integrated or just present

---

## Part II: Current samskrtam.ru/kosha Architecture

### Existing assets

**SamudraManthanam (samskrtam.ru) today:**

1. **FastAPI backend** (`web/app/main.py`)
   - SQLite FTS5 search (corpus.db, corpus.db-offline pack)
   - Search modes: plain, regex, morphological
   - Per-source search (Rigveda, MBh, etc. as separate indices)
   - Result limit: 5,000 entries

2. **Digitized dictionaries** (embedded, gitignored)
   - `dic_mw.jsonl` (Monier-Williams)
   - `dic_apte.jsonl` (Apte)
   - `kochergina.jsonl` (Russian)
   - `kossovich.jsonl` (Russian, PD 1854)
   - 5+ others (SLP1-keyed, ~57k entries total)
   - Source: `web/corpus_builder/jsonl/`

3. **Corpus database** (verse-aligned parallel Sanskrit–Russian)
   - ~154 texts (Rigveda, Mahābhārata, Rāmāyaṇa, Upaniṣads, etc.)
   - Morphological search via Sanskrit Heritage API integration
   - Verse-level alignment (soft signal, not per-word)

4. **Web UI** (Jinja2 templates, minimal JS)
   - `search_page.html` (main interface)
   - `result_fragment.html` (result rendering)
   - `compare_index.html` (multi-source comparison)
   - No autocomplete; no encoding toggle

### Bottlenecks

| Issue | Impact | Priority |
|-------|--------|----------|
| **Dictionary not searchable by form** | Users must know citation form; Cologne corrections not exposed | High |
| **No unified view** | Each dict queried separately; no integrated lookup | High |
| **No encoding switcher** | SLP1-only input; learners need Devanagari/IAST | High |
| **No sense ranking** | Results shown in citation order, not frequency/usefulness | Medium |
| **No etymology** | Etymology work in csl-atlas/SanskritLexicography not surfaced | Medium |
| **Citation link rot** | `<ls>` markers not hyperlinked to source passages | Medium |
| **Mobile UX** | Responsive design incomplete; slow on mobile networks | Medium |
| **No API** | No JSON endpoints for programmatic access | Low |
| **Search latency** | ~200–500ms per query estimated (no metrics) | High |

---

## Part III: Strategic Decisions (Ask User for Clarification)

Before building the roadmap, **I need your input on these questions:**

### Q1: Scope & Audience
**Who is the primary user?**
- Scholars (need etymology, full apparatus, Cologne corrections)?
- Learners (need frequency, simple definitions, pronunciation)?
- Translators (need comparative dicts, sense ranking)?
- All of the above (must support all three)?

**→ Decision:** Affects feature priority. Learners = speed + filtering; scholars = depth + provenance.

### Q2: Dictionary Coverage
**Which Cologne dictionaries should be included in unified lookup?**
- Core: MW + PWG only?
- Extended: + AP90, GRA, PW, CAE, MD, etc.?
- Lightweight: MW only + optional PWG?

**→ Decision:** Affects indexing strategy and latency.

### Q3: Real-time vs Precomputed
**How fresh do corrections need to be?**
- Real-time sync with csl-orig (every edit immediately searchable)?
- Nightly batch updates (acceptable delay)?
- Static snapshots (quarterly releases)?

**→ Decision:** Real-time = complex; static = fast but stale.

### Q4: Morphology & Inflection
**How deep should morphological lookup go?**
- Lemmas only (cite what you know)?
- All attested forms (expansive, may be noisy)?
- Filtered forms (only Cologne-documented paradigms)?

**→ Decision:** Affects search index size and query time.

### Q5: Scope of Etymology & Apparatus
**Which data layers should be searchable?**
- Etymology only (derivative roots)?
- Full Cologne apparatus (`<ls>`, citations, alternate forms)?
- Integrated corpus evidence (verses containing the word)?
- All three?

**→ Decision:** Adds complexity and data dependencies.

### Q6: Deployment Target
**Where will kosha live?**
- samskrtam.ru subdomain (alongside corpus)?
- Separate fast-lookup service (cdn.samskrtam.ru)?
- Published to scholar's GitHub Pages (static export)?

**→ Decision:** Affects architecture (monolithic vs microservice vs static).

---

## Part IV: Proposed Architecture (Conditional on Q1–Q6)

### Tier-1: Fast Path (≤50ms lookups)

**For the 80% case: learners seeking one entry**

```
User types "dharma" → Lookup Service
                         ├─ Check precomputed lemma cache (Redis/in-process)
                         ├─ If hit: render cached HTML snippet (~10ms)
                         └─ If miss: query FTS5 index, cache result (~50ms)
                         
Result:
  - Headword + primary sense (first sense, all dictionaries)
  - Frequency band (DCS or usage corpus)
  - Quick links to full entry, etymology, citations
```

**Precomputed set:**
- Top 10k lemmas (80% of searches, extrapolated from corpus frequency)
- Nightly rebuild from csl-orig + DCS frequency
- Baked as a single `index.json` (or SQLite blob for zero deserialization)

### Tier-2: Deep Path (200–500ms, on-demand)

**For scholars wanting full apparatus**

```
User clicks "full entry" or uses advanced search
                         ├─ Query all dictionaries in parallel (async/await)
                         ├─ Resolve citations to corpus verses (SamudraManthanam FTS)
                         ├─ Fetch etymology from csl-atlas layer
                         └─ Aggregate into unified sense tree
                         
Result:
  - Full entry from each dictionary (MW, PWG, AP90, etc.)
  - Sense alignment (R2 layer from csl-atlas if available)
  - Corpus citations (verse refs, aligned Russian)
  - Etymology lineage
  - Cologne revision history (if csl-corrections tracked)
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ Input: Cologne dicts (csl-orig) + DCS + csl-atlas + corrections     │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
        ┌──────────────────────┐  ┌──────────────────────┐
        │ Nightly Build Phase  │  │ Precomputation Phase │
        ├──────────────────────┤  ├──────────────────────┤
        │ - Extract MW + PWG   │  │ - DCS frequency band │
        │ - Normalize SLP1     │  │ - Sense ranking      │
        │ - Expand forms       │  │ - Frequency labels   │
        │ - Resolve senses     │  │ - Citation groups    │
        │ - Join etymology     │  │                      │
        └──────────────────────┘  └──────────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌──────────────────────┐
                    │   Index Build        │
                    ├──────────────────────┤
                    │ 1. SQLite FTS5       │ ← plain/morphological search
                    │ 2. Precomputed Cache │ ← top 10k lemmas
                    │ 3. Sense Tree        │ ← sense relations
                    └──────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
        ┌──────────────────────┐  ┌──────────────────────┐
        │  Fast Lookup API     │  │  Deep Lookup API     │
        ├──────────────────────┤  ├──────────────────────┤
        │ /search?q=X          │  │ /lemma/X/full        │
        │ ← 50ms, cached       │  │ ← 200–500ms, async   │
        └──────────────────────┘  └──────────────────────┘
```

---

## Part V: Implementation Roadmap (By Phase)

### Phase 1: Foundation & Data Integration (Weeks 1–3)

**Goals:** Unify dictionary indexing; baseline speed measurement.

**Tasks:**

1. **Audit existing dictionary data** (SanskritLexicography)
   - [ ] Verify SLP1 key coverage across MW, PWG, AP90, GRA
   - [ ] Measure headword overlap (union size, homonym conflicts)
   - [ ] Check for Cologne revisions (csl-corrections applied?)
   - [ ] Output: `DICT_AUDIT_2026-07-02.md` (coverage matrix)

2. **Create unified dictionary index**
   - [ ] Merge MW + PWG + AP90 into single SQLite table (keyed by SLP1 + homonym key)
   - [ ] Schema: `(slp1_key, homonym_id, dict_source, headword_iast, senses, raw_xml)`
   - [ ] Preserve original XML (no lossy flattening)
   - [ ] Build FTS5 index on headword + sense text
   - [ ] Output: `unified_dict.db` (~200MB estimated)

3. **Integrate with Cologne corrections**
   - [ ] Read csl-corrections change files (per-dict)
   - [ ] Apply to index at build time (no runtime patching)
   - [ ] Mark revision version in metadata
   - [ ] Output: index carries `csl_orig_commit_hash`

4. **Link Samudra corpus data**
   - [ ] Query SamudraManthanam corpus for each lemma
   - [ ] Store verse citations (SLP1 key → `[{verse_id, sa_text, ru_text}]`)
   - [ ] Output: `dict_lemma_corpus_links.json`

5. **Measure baseline latency**
   - [ ] Query samskrtam.ru FTS5 index for 100 random lemmas
   - [ ] Record p50/p95/p99 latencies
   - [ ] Output: `BASELINE_LATENCY_2026-07-02.md`

**Deliverable:** `unified_dict.db` + citation links + audit report

---

### Phase 2: Fast-Path Caching & Precomputation (Weeks 4–6)

**Goals:** Hit ≤50ms latency for common lookups.

**Tasks:**

1. **DCS frequency integration**
   - [ ] Join VisualDCS frequency band (common/rare/archaic) to each lemma
   - [ ] Tag lemmas by frequency quintile
   - [ ] Output: `lemma_frequency_bands.json`

2. **Precompute top-10k entries**
   - [ ] Rank by DCS frequency + citation count
   - [ ] For each top lemma:
     - Fetch all dictionary senses (MW, PWG, AP90, etc.)
     - Render sense aggregation (unified view)
     - Include 3–5 top corpus examples
     - Bake as JSON blob
   - [ ] Output: `top_10k_cache.json` (~50–100MB)

3. **Deploy in-process cache**
   - [ ] Load `top_10k_cache.json` on server startup
   - [ ] Implement lookup: `dict[slp1_key] → precomputed entry`
   - [ ] Fallback to FTS5 query for cache misses
   - [ ] Add HTTP caching headers (ETag, max-age=3600)

4. **Benchmark cache hit rate**
   - [ ] Simulate 1000 random queries (weighted by corpus frequency)
   - [ ] Measure % hitting cache (target: ≥80%)
   - [ ] Measure latency for cache hits vs misses
   - [ ] Output: `CACHE_PERFORMANCE_2026-07-15.md`

**Deliverable:** In-process cache + API returning ≤50ms for 80% of lookups

---

### Phase 3: UI Enhancements (Weeks 7–9)

**Goals:** Learner-friendly, responsive, feature-complete.

**Tasks:**

1. **Encoding switcher**
   - [ ] Add UI toggle: SLP1 ↔ IAST ↔ Harvard-Kyoto ↔ Devanagari
   - [ ] Client-side transcoding (reuse `sanskrit-util` lib)
   - [ ] Persist user preference (localStorage)
   - [ ] Output: `templates/search_page.html` (updated)

2. **Sense ranking & filtering**
   - [ ] Reorder senses by frequency (DCS band) + citation count
   - [ ] Add filters: by dictionary, by category (nouns/verbs), by era
   - [ ] Highlight primary sense (frequency-based or Cologne priority)
   - [ ] Output: updated result rendering

3. **Unified multi-dictionary view** (inspired by michaelmeyer.fr)
   - [ ] Replace tabbed interface with single-page TOC
   - [ ] Each dictionary's entry in a collapsible section
   - [ ] Shared headword at top; each dict's gloss + senses below
   - [ ] Smooth scroll-to-section JS
   - [ ] Output: new template component

4. **Mobile responsiveness**
   - [ ] Test on mobile (375px width)
   - [ ] Stack sections vertically
   - [ ] Readable font sizes (≥16px)
   - [ ] Touch-friendly tap targets (≥44px)
   - [ ] Output: CSS media queries

5. **Form lookup**
   - [ ] User types inflected form (e.g., "bhagavān")
   - [ ] UI suggests lemma (via morphological expansion)
   - [ ] Clicking lemma performs lookup
   - [ ] Output: autocomplete dropdown

**Deliverable:** Modern, fast, mobile-ready UI with advanced search options

---

### Phase 4: Etymology & Advanced Features (Weeks 10–13)

**Goals:** Integrate Cologne etymology; surface Cologne revision history.

**Tasks:**

1. **Etymology layer** (from csl-atlas work)
   - [ ] Extract etymology data: root → derivatives (from csl-orig/etymology/)
   - [ ] Link each headword to its root + derivation path
   - [ ] Render as tree/graph (visual or textual)
   - [ ] Output: `lemma_etymology_links.json`

2. **Citation hyperlinks**
   - [ ] Parse `<ls>` tags in senses
   - [ ] Resolve abbreviation (via Cologne citation siglum table)
   - [ ] Create deep links to corpus passages in SamudraManthanam
   - [ ] Make `<ls>BhG 1.1</ls>` clickable → /corpus/bhagavad-gita#1.1
   - [ ] Output: enhanced sense rendering

3. **Cologne revision history**
   - [ ] For each headword, list revisions (date, change type, csl-corrections ref)
   - [ ] Show "as of X revision" date
   - [ ] Optional: diff view (old vs new)
   - [ ] Output: `lemma_revision_history.json`

4. **API endpoints** (for programmatic access)
   - [ ] `GET /api/lemma/{slp1}` → full entry JSON
   - [ ] `GET /api/search?q=X&encoding=Y&dicts=MW,PWG` → search results
   - [ ] `GET /api/corpus/{slp1}` → corpus verses containing form
   - [ ] Output: OpenAPI spec + working endpoints

5. **Scholarly export**
   - [ ] Copy-as-BibTeX (for LaTeX users)
   - [ ] Copy-as-JSON (for data processing)
   - [ ] Copy-as-plain-text (with formatting)
   - [ ] Output: JS handlers + server-side formatters

**Deliverable:** Deep scholarly features (etymology, citations, API, exports)

---

### Phase 5: Performance & Scale (Weeks 14–16)

**Goals:** Sub-100ms p99 latency under load; analytics for real-world usage.

**Tasks:**

1. **Load testing**
   - [ ] Spin up load test (via Apache Bench or k6)
   - [ ] 100 concurrent users, 10-second ramp-up
   - [ ] Measure p50/p95/p99 latencies
   - [ ] Identify bottlenecks (CPU? DB lock? network?)
   - [ ] Output: `LOAD_TEST_2026-07-31.md`

2. **Database optimization**
   - [ ] Add indices if missing (on `slp1_key`, `headword_iast`)
   - [ ] Profile FTS5 query time for slow queries
   - [ ] Consider caching layer (Redis) if latency still >100ms
   - [ ] Output: optimized schema + query plans

3. **Static pre-rendering** (optional)
   - [ ] For top-1k lemmas, pre-render as static HTML
   - [ ] Deploy to CDN (Cloudflare Pages, GitHub Pages)
   - [ ] Fallback to API for dynamic queries
   - [ ] Benefit: global edge caching, minimal server load
   - [ ] Output: `build_static_pages.py` + deployment config

4. **Monitoring & alerting**
   - [ ] Log query latencies (structured JSON)
   - [ ] Alert if p95 latency > 500ms or error rate > 1%
   - [ ] Track popular queries (frequency heatmap)
   - [ ] Output: Prometheus metrics + dashboard

5. **Analytics**
   - [ ] Anonymous query logging (no IP/user tracking, just lemma + timestamp)
   - [ ] Track most-searched lemmas, encoding preferences, time-of-day patterns
   - [ ] Monthly report: "Most requested entries", "Popular encodings"
   - [ ] Output: `ANALYTICS_MONTHLY_2026-07-31.md`

**Deliverable:** Production-grade performance monitoring + analytics

---

## Part VI: Data Dependencies

### From SanskritLexicography

**Required:**
- `HeadwordLists/` — union headword coverage (MW, PWG, AP90, GRA, etc.)
- `RussianTranslation/mw_ru.md` — Russian MW translation (not strictly needed for English lookup, but enriches multilingual capability)
- Etymology data (from csl-atlas, if available) — root crosswalks, derivative relations

**Optional (nice-to-have):**
- Sense ranking data (R2 alignments from csl-atlas, if published)
- Grammar layer (Whitney roots, gaṇa/pada from csl-atlas)
- Frequency-graded reading-layer filters

### From SamudraManthanam

**Required:**
- `web/corpus.db` / `web/corpus_builder/jsonl/` — digitized dictionaries (MW, Apte, Russian dicts)
- Morphological search API — form expansion for lookup
- Parallel corpus — verse attestations + references

**Optional:**
- Etymology data (`warnemyr.jsonl` from SamudraManthanam if available)

### From Cologne (csl-orig, csl-corrections)

**Required:**
- csl-orig latest snapshots (MW, PWG, AP90, GRA)
- csl-corrections change files (to surface latest revisions)
- Citation siglum table (abbreviation → full source)

**Optional:**
- Digitized scans (for edition-of-origin links)
- OCR data (for historical edit tracking)

---

## Part VII: Open Questions & Trade-offs

| Question | Option A (Fast) | Option B (Deep) | Recommendation |
|----------|-----------------|-----------------|---|
| **Morphology depth** | Lemmas only | All attested forms | B (→ form lookup works) |
| **Real-time updates** | Nightly batch | Real-time sync | A (nightly sufficient, faster) |
| **Etymology completeness** | Links only | Full etymon trees | A (links first, graph v2) |
| **Citation hyperlinks** | Yes, to passages | Yes, + to commentary | A (passages only, simpler) |
| **Encoding support** | IAST + SLP1 | + Harvard-Kyoto + Dev | B (learners need Devanagari) |
| **API rate limiting** | Yes (100/min) | Unlimited (trusted) | A (prevent scraping) |
| **Multi-language glosses** | English + Russian | + German + French | B (leverage Cologne polyglot) |
| **Version branching** | Single (latest) | Multiple (by year) | A (single, reduces complexity) |

---

## Part VIII: Success Metrics

By end of Phase 5 (Q4 2026):

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Lookup latency (p50)** | ≤ 30ms | Load test, 1k queries |
| **Lookup latency (p95)** | ≤ 100ms | Load test, 1k queries |
| **Cache hit rate** | ≥ 80% | Weighted by corpus freq |
| **Mobile render time** | ≤ 2s | 3G network simulation |
| **Dictionaries indexed** | ≥ 5 (MW, PWG, AP90, etc.) | Coverage audit |
| **Search result relevance** | Top-1 relevance ≥ 90% | 50-lemma sample, expert judge |
| **User satisfaction** (if user study) | ≥ 4/5 stars | Learner feedback form |
| **Uptime** | ≥ 99.5% | Monitoring dashboard |

---

## Part IX: Resource Estimates

### Time

| Phase | Duration | Person-days |
|-------|----------|-------------|
| Phase 1: Data integration | 3 weeks | 12–15 |
| Phase 2: Caching & precomputation | 3 weeks | 8–10 |
| Phase 3: UI enhancements | 3 weeks | 10–12 |
| Phase 4: Etymology & advanced | 4 weeks | 12–16 |
| Phase 5: Performance & scale | 3 weeks | 8–10 |
| **Total** | **16 weeks** | **50–63 days** |

**Parallelization potential:** Phases 2 & 3 can overlap (data work independent of UI work). Estimate: 12–14 weeks wall-clock if 2-3 people involved.

### Storage

| Asset | Size | Notes |
|-------|------|-------|
| `unified_dict.db` | ~200 MB | All 5+ Cologne dicts, SLP1-indexed |
| `top_10k_cache.json` | ~50–100 MB | Precomputed entries, gzipped |
| `lemma_etymology_links.json` | ~5 MB | Root crosswalks |
| `lemma_corpus_links.json` | ~20–50 MB | Verse citations |
| Total (disk) | ~280–350 MB | Easily fits in most VPS |
| Total (RAM cache) | ~100 MB | Top-10k in memory for hot path |

### Computational

- **Build time (nightly):** ~10–30 minutes (merge dicts + recompute frequency + cache)
- **Query time (99th percentile):** ≤ 100ms (cached) or ≤ 500ms (FTS5 miss)

---

## Next Steps (Conditional on Your Answers to Q1–Q6)

Please answer the six strategic questions in **Part III** so I can:

1. **Refine scope** (which dictionaries, which features, which audience?)
2. **Build implementation tasks** (with specific file paths, schema, API contracts)
3. **Create detailed timelines** (per-task dependencies, team assignments)
4. **Identify blockers** (copyright/data access for certain dictionaries?)

Once you clarify priorities, I'll generate:
- **IMPLEMENTATION_PLAN.md** — task-level breakdown with acceptance criteria
- **DATA_SCHEMA.md** — SQLite/JSON schema for unified index
- **API_SPEC.md** — OpenAPI definition for endpoints
- **UI_WIREFRAMES.md** — mockups of new UI components
- **TESTING_PLAN.md** — acceptance tests per phase

---

_Dr. Mārcis Gasūns_
