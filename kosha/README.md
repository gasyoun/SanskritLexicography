# kosha — Sanskrit Dictionary Lookup Service

_Created: 02-07-2026 · Last updated: 02-07-2026_

**kosha** is a fast, translator-first Sanskrit dictionary lookup service built on Cologne Digital Sanskrit Lexicon (CDSL) data.

- **Speed:** ≤50ms lookup latency (cached), ≤100ms (cache miss)
- **Data:** All Cologne dicts (MW, PWG, AP90) + Sanskrit-Russian glosses + KEWA etymology + corpus attestation
- **UI:** Unified multi-dict view, encoding toggle (IAST ↔ Devanagari), mobile-responsive
- **Scans:** Clickable links to original dictionary pages (Cologne archive)

---

## Quick Start

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Extract dictionaries (one-time, ~20 min)
cd scripts
python extract_page_metadata.py
python extract_dicts_to_json.py
python normalize_and_dedupe.py
python load_into_sqlite.py
python populate_scan_links.py

# 3. Run server
python -m uvicorn app.main:app --reload

# 4. Open browser
http://localhost:8000
```

---

## Deployment Options

### Option A: GitHub Pages (Static, Fastest)

For read-only access (no real-time updates); precomputed lemma pages.

```bash
cd docs
# (static HTML + JS prebuilt)
git push origin gh-pages
```

Access at: `https://gasyoun.github.io/SanskritLexicography/kosha/`

**Pros:** Free, global CDN, instant  
**Cons:** Static only; rebuild needed for updates

---

### Option B: samskrtam.ru/kosha (Dynamic, Always Fresh)

For real-time lookup with latest corrections.

```bash
# Deploy to samskrtam.ru
ssh user@samskrtam.ru

# Pull latest code
cd /var/www/kosha
git pull origin main

# Rebuild indices (if csl-orig changed)
cd /var/www/kosha
python scripts/load_into_sqlite.py

# Restart service
systemctl restart kosha
```

Access at: `http://samskrtam.ru/kosha/`

**Pros:** Real-time, full API, morphological search  
**Cons:** Server-side resources

---

### Option C: Hybrid (Recommended)

- **GitHub Pages** (`gasyoun.github.io/SanskritLexicography/kosha/`) — precomputed top 5k lemmas (instant, CDN-cached)
- **samskrtam.ru/kosha** — full API (all lemmas, real-time search, morphology)
- Fallback: If samskrtam.ru down, users can still access top 5k lemmas on GitHub Pages

---

## Architecture

```
Frontend (Static HTML + JS)
  ├─ search_page.html (entry point)
  ├─ app.js (lookup logic)
  └─ style.css (responsive design)

Backend (FastAPI, optional)
  ├─ /api/lemma/{slp1} → lookup by headword
  ├─ /api/lemma/form/{form} → lookup by inflected form
  ├─ /api/scan/{slp1} → scan links
  └─ /api/search?q=X → full-text search

Database (SQLite)
  ├─ unified_dict.db (MW + PWG + AP90)
  ├─ morphological_forms (form expansion)
  └─ scan_links (Cologne archive references)
```

---

## Directory Structure

```
kosha/
├── README.md (this file)
├── DEPLOYMENT.md (setup instructions)
├── requirements.txt (Python dependencies)
├── app/
│   ├── main.py (FastAPI entry point)
│   ├── models.py (Pydantic schemas)
│   ├── routers/
│   │   ├── lemma.py (/api/lemma/*)
│   │   └── scan.py (/api/scan/*)
│   └── services/
│       ├── dict_service.py
│       ├── cache_service.py
│       ├── morph_service.py
│       └── scan_service.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── transcode.js (IAST ↔ Devanagari)
├── templates/
│   └── search_page.html
├── scripts/
│   ├── extract_page_metadata.py
│   ├── extract_dicts_to_json.py
│   ├── normalize_and_dedupe.py
│   ├── load_into_sqlite.py
│   └── populate_scan_links.py
├── tests/
│   └── test_api.py
└── docs/
    ├── index.html (GitHub Pages entry point)
    ├── build_static.py (precompute lemma pages)
    └── _data/ (precomputed lemma cache)
```

---

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Building for GitHub Pages

```bash
# Precompute top 5k lemmas as static HTML
python docs/build_static.py

# Deploy
git add docs/
git commit -m "chore: rebuild static pages"
git push origin main
```

---

## API Endpoints

### Lookup by Lemma

```bash
GET /api/lemma/bandh?encoding=iast

{
  "slp1": "bandh",
  "iast": "bandh",
  "entries": [
    {
      "dict": "mw",
      "volume": 5,
      "page": 32,
      "senses": [
        { "text": "to bind, fasten" }
      ],
      "scan": {
        "url": "https://cologne.archive.org/mw/vol5/page32.jpg",
        "link_text": "vol. 5, p. 32"
      }
    }
  ]
}
```

### Lookup by Form

```bash
GET /api/lemma/form/bhagavān?encoding=iast

{
  "form": "bhagavān",
  "lemmas": ["bhagavant-"],
  "entries": [...]
}
```

### Search

```bash
GET /api/search?q=bandh&limit=50

{
  "query": "bandh",
  "results": [...]
}
```

### Scan Links

```bash
GET /api/scan/bandh

{
  "slp1": "bandh",
  "scans": {
    "mw": { "url": "...", "link_text": "vol. 5, p. 32" },
    "pwg": { "url": "...", "link_text": "vol. 3, p. 127" }
  }
}
```

---

## Configuration

**Environment variables** (`.env`):

```env
# Database
DATABASE_PATH=./unified_dict.db

# Caching
CACHE_SIZE=5000
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO

# Cologne scan base URL
COLOGNE_SCAN_BASE=https://cologne.archive.org/dictionaries
```

---

## Contributing

1. Create a feature branch
2. Make changes + add tests
3. Run `pytest tests/ -v`
4. Submit PR

---

## License

kosha data and code are published under **CC BY 4.0** (Creative Commons Attribution).

**Attribution:**
- Dictionary data: Cologne Digital Sanskrit Lexicon (CC BY 4.0)
- Russian glosses: SamudraManthanam (mixed sources with permissions)
- Etymology: KEWA + Cologne etymon extractions
- Corpus: SamudraManthanam (mixed sources)

---

_Dr. Mārcis Gasūns_
