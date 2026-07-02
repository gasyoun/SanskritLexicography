# kosha: Start Here

_Created: 02-07-2026 · Last updated: 02-07-2026_

> **⚠️ Triage banner (02-07-2026).** This doc predates the same-day audit. Read
> [KOSHA_FOLDER_SETUP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_FOLDER_SETUP.md)
> first — it records the four locked meta-decisions (docs-to-truth; code in a
> **dedicated repo**, not here; **reuse-first** over csl-apidev/Kosh,
> csl-websanlexicon, `ls_resolver.py`, sanskrit-util, the morphology glossary,
> the existing union headword index; kosha gets its **own** GitHub Pages).
> Known defects kept below for the record: the timeline (5/11 wks) conflicts
> with three other docs (4/10, 16 wks, "Week 6" checklists); "~39 person-days"
> vs "~35 days" disagree internally; the "$3k–5k" budget is ~6× understated at
> the stated rates; "333k lemmas / 347k entries / 300k+ scan_links" are
> unsupported numbers (the real 12-dict union is 323,426 rows and already
> exists); `pytest.ini` never existed; the kosha/ scaffold it points to was
> deleted. Timeline and cost figures here are historical, not binding.

## Your Vision

**Transform samskrtam.ru/kosha into a translator-first Sanskrit dictionary lookup service**, combining the speed of michaelmeyer.fr (~50ms) with the features of sanskritdictionary.com (encoding toggle, form lookup, multi-dict view), backed by all Cologne dictionaries + KEWA etymology + Cologne scan archives.

**Timeline:** 5 weeks for MVP (translator-ready); 11 weeks for full (scholarly publication).

---

## What You've Decided ✅

### Core Strategy
- **Performance:** Real-time lookup speed (sub-50ms cached) matters most; monthly correction freshness OK
- **Data scope:** All Cologne dicts + Sanskrit-Russian dicts + KEWA etymology + morphological parsing + corpus attestation
- **Ownership:** Public service → scholarly publication (CC BY 4.0; DOI-ready)
- **Primary audience:** **Translators > Learners > Scholars** (priority order)

### Technical Decisions
| Aspect | Your Choice |
|--------|---|
| **Languages (UI)** | English (Phase 1) → Russian (Phase 2) → German (Phase 3) → rest (Phase 5) |
| **Grammar display** | Toggle: default Minimal (case/number/gender), can activate Full (paradigm + syntactic notes) |
| **Corpus attestation** | Show: links to SamudraManthanam + statistics + inline preview (top 3 verses) |
| **Russian dicts** | Kochergina (primary) + Knauer + Kossovich + Frish + Smirnov (skip mw_ru) |
| **Update cadence** | ~~Monthly batches (nightly cron rebuild)~~ — self-contradictory; cadence is OPEN, leaning nightly (see [KOSHA_DECISIONS_NEEDED.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_DECISIONS_NEEDED.md) D3) |
| **Scholarly metadata** | Include persistent IDs (lemma URIs) + provenance (csl-orig version, correction batch date) |
| **Scans** | Cologne server; external links first (Phase 2b) → self-hosted fallback (Phase 5) |

---

## All Documents (In Order of Importance)

### Start with These (Foundational)

1. **[KOSHA_IMPLEMENTATION_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_IMPLEMENTATION_PLAN.md)** ← **READ THIS FIRST**
   - Week-by-week breakdown (Weeks 1–11)
   - Specific tasks with code snippets
   - MVP = 5 weeks; Full = 11 weeks
   - Ready to assign to developer

2. **[KOSHA_LOOKUP_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_LOOKUP_ROADMAP.md)**
   - Strategic overview (michaelmeyer.fr vs sanskritdictionary.com)
   - Current bottlenecks (samskrtam.ru)
   - Phase descriptions + deliverables

3. **[KOSHA_TRANSLATOR_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_TRANSLATOR_SPEC.md)**
   - Translator workflow analysis
   - How translators use dictionaries (real-world example)
   - Phase 1–5 prioritization by translator value

4. **[KOSHA_SCANS_INTEGRATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_SCANS_INTEGRATION.md)**
   - Complete scan-linking specification
   - Page metadata in csl-orig (`<pc>` tags)
   - Cologne server integration
   - Implementation tasks for Phase 2b

### Reference & Technical Details

5. **[KOSHA_REFERENCE_ANALYSIS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_REFERENCE_ANALYSIS.md)**
   - Feature-by-feature comparison (michaelmeyer.fr vs sanskritdictionary.com)
   - What to adopt, what to skip
   - Hybrid approach recommendation

6. **[KOSHA_REUSABLE_ASSETS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_REUSABLE_ASSETS.md)**
   - Your existing repos (SamudraManthanam, SanskritLexicography, sanskrit-util)
   - External resources (Sanskrit Heritage, Vedaweb, csl-atlas)
   - Data files to generate

---

## Immediate Next Steps (This Week)

### For You (Project Owner)

- [ ] **Read [KOSHA_IMPLEMENTATION_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_IMPLEMENTATION_PLAN.md)** (30 min)
- [ ] **Confirm Cologne scan URL patterns** (contact Cologne team)
  - Which dicts have digitized scans?
  - What's the URL format? (e.g., `https://cologne.archive.org/dicts/mw/vol5/page32.jpg`)
  - Can we link directly or do we need to self-host?
- [ ] **Identify who will build Phase 1** (you / hire developer / time-bound budget?)

### For Developer (if hiring)

**Phase 1 (Weeks 1–2): Core Dictionary Indexing**

1. **Extract page metadata from csl-orig** (2–3 hours)
   - Script: `scripts/extract_page_metadata.py` (in implementation plan)
   - Output: `dict_page_map.json`

2. **Parse dicts into normalized JSON** (3–4 hours)
   - Script: `scripts/extract_dicts_to_json.py` (in implementation plan)
   - Output: `dicts_raw.jsonl` (300k+ entries)

3. **Build SQLite index with FTS5** (3–4 hours)
   - Schema: `schema.sql` (in implementation plan)
   - Script: `scripts/load_into_sqlite.py`
   - Output: `unified_dict.db` (queryable, indexed)

4. **Integrate morphological expansion** (2–3 hours)
   - Service: `app/services/morph_service.py` (in implementation plan)
   - Uses: Sanskrit Heritage API (free, no auth needed)
   - Output: `morphological_forms` table

**Phase 2 (Weeks 3–4): Translator UI**

5. **FastAPI endpoints** (4–6 hours)
   - `/api/lemma/{slp1}` — lookup by headword
   - `/api/lemma/form/{form}` — lookup by inflected form
   - `/api/search?q=X` — full-text search

6. **In-memory caching** (2–3 hours)
   - Preload top 5k lemmas
   - Target: ≥80% cache hit rate

7. **Frontend UI** (4–5 hours)
   - Lookup form + result cards
   - Encoding toggle (SLP1 ↔ IAST ↔ Devanagari)
   - Grammar toggle (minimal ↔ full)
   - Mobile-responsive

**Phase 2b (Weeks 4–5): Scan Linking**

8. **Cologne integration** (2–3 hours)
   - Query Cologne for scan URL patterns
   - Populate `scan_links` table

9. **Scan API + UI** (2–3 hours)
   - `/api/scan/{slp1}` endpoint
   - Display "View in original" link in results

**Total effort:** ~39 person-days for MVP (Phases 1–2b)

---

## MVP Success Criteria (5 Weeks)

| Criterion | Target | How to Verify |
|-----------|--------|---|
| **Lookup latency (p50)** | ≤30ms | Load test: 1k random queries |
| **Lookup latency (p95)** | ≤100ms | Load test: 1k random queries |
| **Cache hit rate** | ≥80% | Weighted by corpus frequency |
| **Form lookup works** | "bhagavān" → "bhagavant-" in <100ms | Manual test |
| **Comparative view** | MW + PWG + AP90 on one screen | Screenshot: compare side-by-side |
| **Encoding toggle** | Click toggle, IAST ↔ Devanagari instant | Manual test on mobile |
| **Scan links** | Every entry shows "vol. X, p. Y" link | Spot-check 10 entries |
| **Mobile responsive** | No horizontal scrolling @ 375px width | iPhone 12 Safari |
| **Dictionary coverage** | MW (193k) + PWG (106k) + AP90 (48k) searchable | Check entry counts in UI |

---

## Architecture at a Glance

```
Frontend (JavaScript)
  ├─ Lookup form (text input)
  ├─ Encoding toggle (SLP1 ↔ IAST ↔ Devanagari)
  ├─ Result cards (MW + PWG + AP90)
  └─ Scan links (clickable: "vol. 5, p. 32")

Backend (FastAPI)
  ├─ /api/lemma/{slp1} → cached results ≤50ms
  ├─ /api/lemma/form/{form} → morphological expansion
  ├─ /api/scan/{slp1} → Cologne scan links
  └─ /api/search?q=X → full-text search

Database (SQLite + FTS5)
  ├─ lemmas (333k unique headwords)
  ├─ entries (347k senses across 3 dicts)
  ├─ morphological_forms (1M+ form variants)
  ├─ scan_links (300k+ page references)
  └─ Cache (top 5k lemmas in RAM)

Data Sources
  ├─ csl-orig (Cologne dicts: MW, PWG, AP90)
  ├─ SamudraManthanam (Russian dicts, corpus)
  ├─ Sanskrit Heritage API (morphology)
  ├─ Cologne server (scan images)
  └─ VisualDCS (frequency bands, Phase 5)
```

---

## File Structure (Start)

```
SanskritLexicography/
├── KOSHA_*.md (this document + others)
├── kosha/ (new app directory)
│   ├── app/
│   │   ├── main.py (FastAPI entry point)
│   │   ├── models.py (Pydantic schemas)
│   │   ├── routers/
│   │   │   ├── lemma.py (/api/lemma/*)
│   │   │   └── scan.py (/api/scan/*)
│   │   └── services/
│   │       ├── dict_service.py
│   │       ├── cache_service.py
│   │       ├── morph_service.py
│   │       └── scan_service.py
│   ├── scripts/
│   │   ├── extract_page_metadata.py
│   │   ├── extract_dicts_to_json.py
│   │   ├── normalize_and_dedupe.py
│   │   ├── load_into_sqlite.py
│   │   └── populate_scan_links.py
│   ├── static/
│   │   ├── app.js
│   │   └── style.css
│   ├── templates/
│   │   └── search_page.html
│   ├── unified_dict.db (created during Phase 1)
│   ├── requirements.txt
│   ├── pytest.ini
│   └── tests/
│       └── test_api.py
```

---

## Budget & Resources

### Hosting (samskrtam.ru)

| Resource | Cost | Notes |
|---|---|---|
| SQLite database (300 MB) | $0 (local disk) | Already on samskrtam.ru |
| FastAPI server | $0 (existing VPS) | Reuse samskrtam.ru infrastructure |
| Scan images (Phase 5, if self-hosted) | ~$50–75/month | 1.8 GB @ AWS S3; link to Cologne for now |
| **Total (MVP)** | **$0** | Link to Cologne scans; scale storage in Phase 5 |

### Development

| Phase | Effort | Role | Who |
|---|---|---|---|
| Phase 1 (indexing) | ~15 days | Backend | Python engineer |
| Phase 2 (UI) | ~12 days | Backend + Frontend | Python + JS engineer |
| Phase 2b (scans) | ~8 days | Backend | Python engineer |
| **Total MVP** | **~35 days** | — | 1–2 people, 5 weeks |

**Alternatives:**
- DIY: Your time (if available)
- Hire: Budget ~$3k–5k (contractor rates: $100–150/hr × 35 days)
- Split: You do indexing (Phase 1), hire for UI + scans (Phases 2–2b)

---

## Risk & Mitigation

| Risk | Likelihood | Mitigation |
|---|---|---|
| **Cologne scan URLs change** | Low | Confirm URLs in writing; build URL resolution abstraction (easy to change later) |
| **Sanskrit Heritage API rate-limit** | Medium | Cache results; pre-compute all forms at index time (one-time) |
| **SQLite FTS5 too slow at 300k entries** | Low | Benchmarking in Phase 1 will catch this; Elasticsearch as backup plan |
| **Mobile UI doesn't load fast enough** | Low | Test on 3G early; optimize JS + CSS |
| **Homonym conflicts break lookups** | Low | Careful testing in Phase 1b; implement fallback search by entry count |

---

## Launch Checklist (Week 6)

- [ ] All Phase 1–2b tests passing (≥95%)
- [ ] API latency verified: p50 ≤30ms, p95 ≤100ms
- [ ] Mobile UI tested on iPhone + Android
- [ ] Scan links confirmed working (click 10 random entries)
- [ ] Documentation written (README, API docs)
- [ ] Deployed to samskrtam.ru/kosha (or staging URL)
- [ ] User testing with 1–2 translators (feedback on UX)
- [ ] Monitoring + logging enabled (Prometheus, logs)

---

## What Comes Next (Beyond MVP)

### Phase 3 (Weeks 6–7): Etymology + KEWA
- KEWA etymon data integration
- Root crosswalks (√ bhag- → bhagavant-, bhagavat-)
- Semantic derivation chains

### Phase 4 (Weeks 8–9): Corpus Evidence
- Inline verse examples (top 3–5 with Russian translation)
- Sense frequency across corpus
- Related words in same passages

### Phase 5 (Weeks 10–11): Scholarly Export
- Real-time or monthly sync with csl-orig (via webhook or cron)
- DOI registration (Zenodo deposit)
- Export formats (JSON, BibTeX, TEI XML)
- Persistent lemma URIs + provenance metadata

---

## Questions Before Starting?

**Common questions:**

1. **Do we need to contact Cologne directly?**  
   Yes. Confirm scan availability and URL format (should be quick, 1–2 hours).

2. **Can I start Phase 1 before confirming scans?**  
   Yes! Scan linking is Phase 2b; Phase 1 (indexing) is independent. Start Phase 1 immediately; Phase 2b waits for Cologne confirmation.

3. **What if we want real-time sync instead of monthly batches?**  
   Possible (Phase 5). Requires webhook on csl-orig + async rebuild. Start with monthly; upgrade in Phase 5 if needed.

4. **Can we add more dictionaries later?**  
   Yes. Schema is designed for 7+ dicts. Just re-run extraction scripts for new dicts (e.g., `gra`, `pw`, `cae`, `md`).

5. **What's the fallback if Cologne scans are unavailable?**  
   Link to Internet Archive for PD editions. Code handles missing scans gracefully (no link shown).

---

## Ready to Start?

**Next action:** Assign Phase 1 to a Python engineer. They can start immediately with [KOSHA_IMPLEMENTATION_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_IMPLEMENTATION_PLAN.md).

**In parallel:** You contact Cologne team for scan URLs.

**In 5 weeks:** kosha MVP launches. Translators can lookup any Sanskrit form, see all dictionaries at once, switch to Devanagari with one click, and verify against scanned pages.

**In 11 weeks:** Full scholarly publication-ready resource with etymology, corpus evidence, and persistent citations.

---

_Dr. Mārcis Gasūns_
