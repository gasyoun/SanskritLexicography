# kosha Quickstart

_Created: 02-07-2026_

## What You Have

A complete, organized codebase for **kosha** — a translator-first Sanskrit dictionary lookup service.

```
SanskritLexicography/
├── kosha/                              ← START HERE
│   ├── README.md                       (Project overview)
│   ├── QUICKSTART.md                   (This file)
│   ├── SETUP_GUIDE.md                  (30-min setup)
│   ├── DEPLOYMENT.md                   (GitHub Pages + samskrtam.ru)
│   │
│   ├── app/                            (FastAPI backend)
│   ├── static/                         (Frontend: HTML/CSS/JS)
│   ├── templates/                      (Server-side templates)
│   ├── scripts/                        (Data pipeline)
│   ├── tests/                          (Test suite)
│   ├── docs/                           (GitHub Pages site)
│   │
│   ├── requirements.txt                (Dependencies)
│   ├── .env.example                    (Configuration template)
│   └── .gitignore                      (Git exclusions)
│
└── ../KOSHA_*.md                       (Strategic docs in parent)
    ├── KOSHA_IMPLEMENTATION_PLAN.md    (Week-by-week tasks)
    ├── KOSHA_TRANSLATOR_SPEC.md        (Translator needs)
    ├── KOSHA_SCANS_INTEGRATION.md      (Scan linking)
    └── ... (4 more reference docs)
```

---

## Three Ways to Deploy

### 1. **GitHub Pages** (Instant, CDN-Cached)

Fast, free read-only lookup for top 5k lemmas.

```bash
cd SanskritLexicography/kosha

# Build cache
python docs/build_static_cache.py

# Deploy
git add docs/
git commit -m "chore: rebuild static cache"
git push origin main

# Access: https://gasyoun.github.io/SanskritLexicography/kosha/
```

**Status:** ✅ Directory ready (`docs/index.html` created)  
**Next:** Implement `docs/build_static_cache.py` in Phase 2

---

### 2. **samskrtam.ru/kosha** (Full API, Real-Time)

Complete dictionary lookup with latest corrections, morphological search.

```bash
# SSH to samskrtam.ru
ssh user@samskrtam.ru

# Setup (see DEPLOYMENT.md for full instructions)
cd /var/www/kosha
git clone https://github.com/gasyoun/SanskritLexicography.git .
cd kosha

# Extract data
python scripts/load_into_sqlite.py

# Start service
sudo systemctl restart kosha

# Access: http://samskrtam.ru/kosha/
```

**Status:** ✅ Code structure ready  
**Next:** Phase 1 (extract + index dicts)

---

### 3. **Hybrid** (Recommended)

Both working together: GitHub Pages for instant cached access + samskrtam.ru for full API.

**User experience:**
- Type in GitHub Pages → instant cached result
- Or click "Full API" link → go to samskrtam.ru for all dicts

**Status:** ✅ Structure ready for both  
**Next:** Build both in parallel

---

## Roadmap at a Glance

| Week | Phase | What | Status |
|------|-------|------|--------|
| 1–2 | **Phase 1** | Extract + index dicts | 📋 Plan ready |
| 3–4 | **Phase 2** | FastAPI + UI + caching | 📋 Plan ready |
| 4–5 | **Phase 2b** | Scan links + Cologne | 📋 Plan ready |
| 6–7 | **Phase 3** | Etymology + KEWA | 📋 Plan ready |
| 8–9 | **Phase 4** | Corpus evidence | 📋 Plan ready |
| 10–11 | **Phase 5** | Scholarly export + sync | 📋 Plan ready |

**MVP (Phases 1–2b):** 5 weeks → translator-ready  
**Full (all phases):** 11 weeks → publication-ready

---

## Right Now: What to Do

### For You (Project Owner)

- [ ] **Read:** [KOSHA_IMPLEMENTATION_PLAN.md](../KOSHA_IMPLEMENTATION_PLAN.md) (30 min)
- [ ] **Contact:** Cologne team for scan URL patterns (1–2 hours)
- [ ] **Decide:** Hire developer vs DIY? (or split roles?)

### For Developer (Phase 1)

**Week 1–2: Extract & Index**

```bash
cd kosha
pip install -r requirements.txt

# Run data extraction pipeline
cd scripts
python extract_page_metadata.py      # Parse <pc> tags from csl-orig
python extract_dicts_to_json.py      # Convert to JSON lines
python normalize_and_dedupe.py       # Deduplicate homonyms
python load_into_sqlite.py           # Build FTS5 index
python populate_scan_links.py        # Add scan URLs
cd ..

# Test
python -m pytest tests/ -v
```

**Result:** `unified_dict.db` (queryable, 300k+ entries)

All code snippets provided in [KOSHA_IMPLEMENTATION_PLAN.md](../KOSHA_IMPLEMENTATION_PLAN.md).

---

## File Locations (Important)

| File | Purpose | Status |
|------|---------|--------|
| `kosha/README.md` | Project overview | ✅ Created |
| `kosha/DEPLOYMENT.md` | GitHub Pages + samskrtam.ru setup | ✅ Created |
| `kosha/SETUP_GUIDE.md` | 30-min local setup | ✅ Created |
| `kosha/app/main.py` | FastAPI entry point | ✅ Stub created |
| `kosha/docs/index.html` | GitHub Pages entry point | ✅ Created |
| `kosha/requirements.txt` | Python dependencies | ✅ Created |
| `../KOSHA_IMPLEMENTATION_PLAN.md` | Week-by-week tasks | ✅ Created |
| `../KOSHA_TRANSLATOR_SPEC.md` | Translator workflow | ✅ Created |
| `../KOSHA_SCANS_INTEGRATION.md` | Scan linking spec | ✅ Created |

---

## Next Steps (Pick One)

### ✅ I want to start coding NOW

→ Go to [KOSHA_IMPLEMENTATION_PLAN.md](../KOSHA_IMPLEMENTATION_PLAN.md)  
→ Week 1 tasks are ready to assign

### ✅ I want to understand the bigger picture first

→ Read [KOSHA_START_HERE.md](../KOSHA_START_HERE.md) (10 min)  
→ Then [KOSHA_TRANSLATOR_SPEC.md](../KOSHA_TRANSLATOR_SPEC.md) (20 min)

### ✅ I want to deploy to GitHub Pages immediately

→ See [DEPLOYMENT.md](DEPLOYMENT.md) Part I  
→ Requires Phase 1 to be done first (indices built)

### ✅ I want to deploy to samskrtam.ru

→ See [DEPLOYMENT.md](DEPLOYMENT.md) Part II  
→ Requires Phase 1 + systemd service setup

---

## Questions?

All decisions are locked and documented in [KOSHA_START_HERE.md](../KOSHA_START_HERE.md).

Your choices:
- **Performance:** Real-time lookup speed (sub-50ms) ✅
- **Data:** All Cologne dicts + Russian + KEWA ✅
- **Audience:** Translators > Learners > Scholars ✅
- **Deployment:** Hybrid (GitHub Pages + samskrtam.ru) ✅
- **Scans:** Cologne server; external links first → self-hosted later ✅

Ready to build?

---

_Dr. Mārcis Gasūns_
