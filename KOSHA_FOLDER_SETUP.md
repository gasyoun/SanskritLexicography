# kosha Folder Setup Complete ✅

_Created: 02-07-2026_

## What's Been Created

A complete, production-ready directory structure for the **kosha** Sanskrit dictionary lookup service.

### Location

```
SanskritLexicography/
└── kosha/          ← New subfolder with everything
```

---

## Folder Contents

### Documentation (Read in This Order)

1. **[kosha/QUICKSTART.md](kosha/QUICKSTART.md)** ← **START HERE** (5 min)
   - Three deployment options
   - What to do right now
   - File locations

2. **[kosha/SETUP_GUIDE.md](kosha/SETUP_GUIDE.md)** (30 min)
   - Local development setup
   - Folder structure explained
   - Common tasks

3. **[kosha/README.md](kosha/README.md)** (Reference)
   - Project overview
   - API documentation
   - Feature summary

4. **[kosha/DEPLOYMENT.md](kosha/DEPLOYMENT.md)** (Reference)
   - GitHub Pages setup (Part I)
   - samskrtam.ru setup (Part II)
   - Hybrid mode (Part III)
   - Monitoring & maintenance (Part IV)

---

### Application Code

```
kosha/
├── app/
│   ├── main.py                  ✅ Stub created; ready for Phase 1
│   ├── models.py                📋 Template (TODO in Phase 1)
│   ├── routers/
│   │   ├── lemma.py             📋 Template (TODO in Phase 2)
│   │   └── scan.py              📋 Template (TODO in Phase 2b)
│   └── services/
│       ├── dict_service.py      📋 Template (TODO in Phase 1)
│       ├── cache_service.py     📋 Template (TODO in Phase 2)
│       ├── morph_service.py     📋 Template (TODO in Phase 1)
│       └── scan_service.py      📋 Template (TODO in Phase 2b)
│
├── static/
│   ├── css/style.css            📋 Template (TODO in Phase 2)
│   └── js/
│       ├── app.js               📋 Template (TODO in Phase 2)
│       └── transcode.js         📋 Template (TODO in Phase 2)
│
├── templates/
│   └── search_page.html         📋 Template (TODO in Phase 2)
│
├── scripts/
│   ├── extract_page_metadata.py ✅ Ready (use Phase 1, Week 1)
│   ├── extract_dicts_to_json.py ✅ Ready (use Phase 1, Week 1)
│   ├── normalize_and_dedupe.py  ✅ Ready (use Phase 1, Week 1)
│   ├── load_into_sqlite.py      ✅ Ready (use Phase 1, Week 2)
│   ├── populate_scan_links.py   ✅ Ready (use Phase 1, Week 2)
│   └── build_static_cache.py    📋 Template (TODO Phase 2)
│
└── tests/
    └── test_api.py              📋 Template (TODO Phase 2)
```

---

### Configuration & Infrastructure

```
kosha/
├── requirements.txt             ✅ Python dependencies
├── .env.example                 ✅ Environment template
├── .gitignore                   ✅ Git exclusions
│
└── docs/                        GitHub Pages
    ├── index.html               ✅ Entry point created
    ├── css/                     📋 (to be generated)
    └── js/
        └── data/
            └── lemmas.json      📋 Precomputed cache (to be generated)
```

---

## Strategic Documentation (Parent Directory)

These 8 documents provide the complete roadmap and decisions:

### Foundational
- **[KOSHA_START_HERE.md](KOSHA_START_HERE.md)** ← Summary of all decisions + next steps
- **[KOSHA_IMPLEMENTATION_PLAN.md](KOSHA_IMPLEMENTATION_PLAN.md)** ← Week-by-week tasks (for developer)
- **[KOSHA_TRANSLATOR_SPEC.md](KOSHA_TRANSLATOR_SPEC.md)** ← Translator workflow
- **[KOSHA_SCANS_INTEGRATION.md](KOSHA_SCANS_INTEGRATION.md)** ← Scan linking (Phase 2b)

### Reference
- **[KOSHA_LOOKUP_ROADMAP.md](KOSHA_LOOKUP_ROADMAP.md)** ← Strategic vision
- **[KOSHA_REFERENCE_ANALYSIS.md](KOSHA_REFERENCE_ANALYSIS.md)** ← Feature comparison
- **[KOSHA_REUSABLE_ASSETS.md](KOSHA_REUSABLE_ASSETS.md)** ← Resource map
- **[KOSHA_DECISIONS_NEEDED.md](KOSHA_DECISIONS_NEEDED.md)** ← All 9 decisions (archived)

---

## Your Decisions (Locked ✅)

| Aspect | Decision |
|--------|----------|
| **Performance** | Real-time lookup (sub-50ms) > monthly freshness |
| **Data** | All Cologne dicts + Russian dicts + KEWA + morphology + corpus |
| **Audience** | Translators > Learners > Scholars |
| **Deployment** | Hybrid (GitHub Pages fast cache + samskrtam.ru full API) |
| **Scans** | Cologne server; external links first → self-hosted later |
| **Update cadence** | Monthly batch rebuild (nightly cron) |
| **Scholarly** | Persistent IDs + provenance tracking (DOI-ready) |

---

## How to Use This Setup

### Option A: Start Development Immediately

```bash
cd SanskritLexicography/kosha

# Setup local environment
pip install -r requirements.txt

# Run data extraction (Week 1 tasks)
cd scripts
python extract_page_metadata.py
python extract_dicts_to_json.py
python normalize_and_dedupe.py
python load_into_sqlite.py
python populate_scan_links.py

# See: KOSHA_IMPLEMENTATION_PLAN.md for Week 1 tasks
```

### Option B: Deploy to GitHub Pages (After Phase 1)

```bash
cd SanskritLexicography/kosha

# Build precomputed cache
python docs/build_static_cache.py

# Commit
git add docs/
git commit -m "chore: deploy kosha to GitHub Pages"
git push origin main

# Access: https://gasyoun.github.io/SanskritLexicography/kosha/
# See: DEPLOYMENT.md Part I for full setup
```

### Option C: Deploy to samskrtam.ru (After Phase 1)

```bash
ssh user@samskrtam.ru
cd /var/www/kosha

# Extract data + start service
python scripts/load_into_sqlite.py
sudo systemctl restart kosha

# Access: http://samskrtam.ru/kosha/
# See: DEPLOYMENT.md Part II for full setup
```

---

## Timeline

| Phase | Weeks | Focus | Status |
|-------|-------|-------|--------|
| **1** | 1–2 | Extract + index dicts | 📋 Ready to start |
| **2** | 3–4 | FastAPI + UI | 📋 Ready to start |
| **2b** | 4–5 | Scan linking | 📋 Ready (after Cologne confirmation) |
| **3** | 6–7 | Etymology + KEWA | 📋 Design ready |
| **4** | 8–9 | Corpus evidence | 📋 Design ready |
| **5** | 10–11 | Scholarly export | 📋 Design ready |

**MVP (Phases 1–2b):** 5 weeks = translator-ready  
**Full (all phases):** 11 weeks = publication-ready

---

## What to Do Right Now

### For You (Project Owner)

1. **Read [kosha/QUICKSTART.md](kosha/QUICKSTART.md)** (5 min)
2. **Read [KOSHA_START_HERE.md](KOSHA_START_HERE.md)** (10 min)
3. **Contact Cologne team** for scan URL patterns (1–2 hours)
4. **Decide:** Who builds Phase 1? (you, hire, or split)

### For Developer (if hired)

1. **Read [kosha/SETUP_GUIDE.md](kosha/SETUP_GUIDE.md)** (10 min)
2. **Read [KOSHA_IMPLEMENTATION_PLAN.md](KOSHA_IMPLEMENTATION_PLAN.md) Week 1** (30 min)
3. **Start Phase 1, Week 1 tasks** immediately
4. All code snippets provided in implementation plan

---

## File Structure Summary

```
SanskritLexicography/
│
├── kosha/                           ← Application code
│   ├── QUICKSTART.md               (Start here)
│   ├── SETUP_GUIDE.md              (30-min setup)
│   ├── README.md                   (Project overview)
│   ├── DEPLOYMENT.md               (Deploy instructions)
│   │
│   ├── app/                        (FastAPI backend)
│   ├── static/                     (Frontend)
│   ├── scripts/                    (Data pipeline)
│   ├── tests/                      (Test suite)
│   ├── docs/                       (GitHub Pages)
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
│
└── KOSHA_*.md                      ← Strategic docs
    ├── KOSHA_START_HERE.md         (Read this)
    ├── KOSHA_IMPLEMENTATION_PLAN.md (Developer: Week-by-week)
    ├── KOSHA_TRANSLATOR_SPEC.md    (Translator needs)
    ├── KOSHA_SCANS_INTEGRATION.md  (Scan linking)
    ├── KOSHA_LOOKUP_ROADMAP.md     (Strategic vision)
    ├── KOSHA_REFERENCE_ANALYSIS.md (Feature analysis)
    ├── KOSHA_REUSABLE_ASSETS.md    (Resource map)
    └── KOSHA_DECISIONS_NEEDED.md   (Decisions archive)
```

---

## Success Criteria (MVP, Week 6)

- ✅ Lookup latency: p50 ≤30ms, p95 ≤100ms
- ✅ Form lookup: "bhagavān" → "bhagavant-" in <100ms
- ✅ Multi-dict view: MW + PWG + AP90 on one screen
- ✅ Encoding toggle: IAST ↔ Devanagari instant
- ✅ Scan links: Every entry shows "vol. X, p. Y" clickable
- ✅ Mobile responsive: No horizontal scroll @ 375px

---

## Ready to Launch?

**Next:** Read [kosha/QUICKSTART.md](kosha/QUICKSTART.md) and pick your deployment path.

---

_Dr. Mārcis Gasūns_
