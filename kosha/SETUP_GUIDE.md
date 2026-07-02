# kosha Setup Guide — Quick Start

_Created: 02-07-2026_

## 30-Minute Setup (Local Development)

### 1. Install Dependencies

```bash
cd SanskritLexicography/kosha
pip install -r requirements.txt
```

### 2. Extract Dictionaries (First Time Only)

```bash
cd scripts
python extract_page_metadata.py      # 2 min
python extract_dicts_to_json.py      # 5 min
python normalize_and_dedupe.py       # 2 min
python load_into_sqlite.py           # 10 min
python populate_scan_links.py        # 3 min
cd ..
```

**Result:** `unified_dict.db` created (~300 MB)

### 3. Run Server

```bash
python -m uvicorn app.main:app --reload
```

**Open browser:** `http://localhost:8000`

---

## Folder Structure

```
kosha/
├── README.md                    # Project overview
├── DEPLOYMENT.md                # GitHub Pages + samskrtam.ru setup
├── SETUP_GUIDE.md              # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git exclusions
│
├── app/                         # FastAPI application
│   ├── main.py                 # Entry point
│   ├── models.py               # Pydantic schemas (TODO)
│   ├── routers/
│   │   ├── lemma.py            # /api/lemma/* endpoints (TODO)
│   │   └── scan.py             # /api/scan/* endpoints (TODO)
│   └── services/
│       ├── dict_service.py     # Dictionary lookup logic (TODO)
│       ├── cache_service.py    # In-memory caching (TODO)
│       ├── morph_service.py    # Morphological expansion (TODO)
│       └── scan_service.py     # Scan link resolution (TODO)
│
├── static/                      # Client-side files
│   ├── css/
│   │   └── style.css           # Responsive styling (TODO)
│   └── js/
│       ├── app.js              # Lookup logic (TODO)
│       └── transcode.js        # IAST ↔ Devanagari (TODO)
│
├── templates/
│   └── search_page.html        # Server-rendered template (TODO)
│
├── docs/                        # GitHub Pages static site
│   ├── index.html              # Entry point
│   ├── css/
│   └── js/
│       └── data/
│           └── lemmas.json     # Precomputed cache (generated)
│
├── scripts/                     # Data pipeline
│   ├── extract_page_metadata.py
│   ├── extract_dicts_to_json.py
│   ├── normalize_and_dedupe.py
│   ├── load_into_sqlite.py
│   ├── populate_scan_links.py
│   └── build_static_cache.py   # For GitHub Pages (TODO)
│
├── tests/                       # Pytest suite
│   └── test_api.py             # API tests (TODO)
│
└── unified_dict.db             # SQLite database (generated)
```

---

## Deployment Options

### Option 1: Local Development Only

```bash
python -m uvicorn app.main:app --reload
# Access at http://localhost:8000
```

### Option 2: GitHub Pages (Static, Free)

```bash
# Build precomputed cache
python docs/build_static_cache.py

# Commit
git add docs/
git commit -m "chore: update static cache"
git push origin main

# Access at https://gasyoun.github.io/SanskritLexicography/kosha/
```

### Option 3: samskrtam.ru (Full API, Real-Time)

```bash
# See DEPLOYMENT.md for detailed instructions
# Quick summary:
# 1. SSH to samskrtam.ru
# 2. Clone repo + extract dictionaries
# 3. Create systemd service
# 4. Configure Nginx reverse proxy
# 5. Access at http://samskrtam.ru/kosha/
```

### Option 4: Hybrid (Recommended)

Both GitHub Pages + samskrtam.ru working together. See **DEPLOYMENT.md**.

---

## Common Tasks

### Run Tests

```bash
pytest tests/ -v
```

### Update Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### Rebuild Database

```bash
cd scripts
python load_into_sqlite.py
cd ..
```

### Check Database Size

```bash
ls -lh unified_dict.db
sqlite3 unified_dict.db "SELECT COUNT(*) FROM entries;"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port 8000 already in use** | `python -m uvicorn app.main:app --port 8001` |
| **Database not found** | Run `scripts/load_into_sqlite.py` |
| **Import errors** | `pip install -r requirements.txt` |
| **Slow startup** | Database is loading cache; be patient first run |

---

## Next Steps

1. **Complete Phase 1:** Implement data extraction + SQLite indexing
2. **Complete Phase 2:** Build FastAPI endpoints + UI
3. **Complete Phase 2b:** Add scan linking
4. **Deploy:** Push to GitHub Pages + samskrtam.ru

See [KOSHA_IMPLEMENTATION_PLAN.md](../KOSHA_IMPLEMENTATION_PLAN.md) for detailed task breakdown.

---
