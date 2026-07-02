# Deployment Guide: kosha at GitHub Pages + samskrtam.ru

_Created: 02-07-2026 · Last updated: 02-07-2026_

---

## Overview

**kosha** supports three deployment modes:

| Mode | URL | Type | Latency | Freshness | Cost |
|------|-----|------|---------|-----------|------|
| **GitHub Pages** | `gasyoun.github.io/SanskritLexicography/kosha/` | Static HTML | ~30ms (CDN) | Monthly rebuild | Free |
| **samskrtam.ru** | `samskrtam.ru/kosha/` | FastAPI server | ~50–100ms | Real-time API | Existing infra |
| **Hybrid** | Both | Fallback | 30ms (cached) + 100ms (API) | Best of both | Free + existing |

**Recommended:** Hybrid mode (GitHub Pages for top 5k lemmas; samskrtam.ru for full API).

---

## Part I: GitHub Pages Deployment

### Prerequisites

- GitHub repo: `gasyoun/SanskritLexicography` (must exist)
- GitHub Pages enabled on default branch

### Step 1: Enable GitHub Pages

```bash
# In repo settings:
# Settings > Pages > Source: Deploy from a branch
# Select: Branch "main", folder "/docs"
```

### Step 2: Prepare Static Site

```bash
# Create docs/ directory (if not exists)
mkdir -p docs

# Move/link static files
cp -r static/* docs/
cp -r templates/search_page.html docs/index.html
```

**Directory structure:**

```
docs/
├── index.html (entry point)
├── css/
│   └── style.css
├── js/
│   ├── app.js
│   ├── transcode.js
│   └── data/
│       └── lemmas.json (precomputed top 5k)
└── _config.yml (Jekyll config, optional)
```

### Step 3: Build Precomputed Lemma Cache

```bash
# scripts/build_static_cache.py
"""
Precompute JSON cache for top 5k lemmas.
Output: docs/js/data/lemmas.json (~50 MB gzipped)
"""
import json
import sqlite3
from pathlib import Path

db = sqlite3.connect('unified_dict.db')
cursor = db.cursor()

# Get top 5k lemmas by frequency
cursor.execute('''
    SELECT l.slp1_key, l.iast, 
           GROUP_CONCAT(DISTINCT e.dict_code) as dicts,
           COUNT(e.id) as entry_count
    FROM lemmas l
    LEFT JOIN entries e ON e.lemma_id = l.id
    GROUP BY l.id
    ORDER BY entry_count DESC
    LIMIT 5000
''')

lemmas_cache = {}
for slp1, iast, dicts, count in cursor.fetchall():
    # Fetch full entry data
    cursor.execute(f'''
        SELECT e.dict_code, e.page_volume, e.page_number, e.senses_text
        FROM entries e
        JOIN lemmas l ON l.id = e.lemma_id
        WHERE l.slp1_key = ?
    ''', (slp1,))
    
    entries = []
    for dict_code, vol, page, senses in cursor.fetchall():
        entries.append({
            'dict': dict_code,
            'vol': vol,
            'page': page,
            'sense': senses[:100]  # truncate for size
        })
    
    lemmas_cache[slp1] = {
        'iast': iast,
        'entries': entries
    }

# Output as minified JSON
output = Path('docs/js/data/lemmas.json')
output.parent.mkdir(parents=True, exist_ok=True)
with open(output, 'w', encoding='utf-8') as f:
    json.dump(lemmas_cache, f, separators=(',', ':'), ensure_ascii=False)

print(f"Built cache: {len(lemmas_cache)} lemmas, {output.stat().st_size / 1024 / 1024:.1f} MB")

db.close()
```

**Run it:**

```bash
python scripts/build_static_cache.py
```

### Step 4: Update Frontend to Use Cache

```javascript
// docs/js/app.js
class KoshaLookup {
    constructor() {
        this.lemmaCache = null;
        this.apiBackend = 'https://samskrtam.ru/api';  // fallback
    }
    
    async loadCache() {
        // Load precomputed lemmas on startup
        const resp = await fetch('/SanskritLexicography/kosha/js/data/lemmas.json');
        if (resp.ok) {
            this.lemmaCache = await resp.json();
            console.log(`Loaded cache: ${Object.keys(this.lemmaCache).length} lemmas`);
        }
    }
    
    async search(lemma) {
        // Try cache first (GitHub Pages)
        if (this.lemmaCache && lemma in this.lemmaCache) {
            return this.lemmaCache[lemma];
        }
        
        // Fallback to samskrtam.ru API
        try {
            const resp = await fetch(`${this.apiBackend}/lemma/${lemma}`);
            if (resp.ok) return await resp.json();
        } catch (e) {
            console.warn('API unavailable; using cache only');
        }
        
        return null;
    }
}

// Initialize
window.addEventListener('DOMContentLoaded', async () => {
    const kosha = new KoshaLookup();
    await kosha.loadCache();
});
```

### Step 5: Configure Jekyll (Optional)

```yaml
# docs/_config.yml
title: kosha - Sanskrit Dictionary Lookup
description: Fast, translator-first Sanskrit dictionary service
baseurl: /SanskritLexicography/kosha
url: https://gasyoun.github.io
theme: null  # no theme; using custom HTML

exclude:
  - README.md
  - DEPLOYMENT.md
  - /scripts
  - /tests
```

### Step 6: Deploy

```bash
# Commit changes
git add docs/
git commit -m "chore: rebuild static GitHub Pages cache"
git push origin main

# GitHub Actions will deploy automatically
# Check: Settings > Actions > All workflows > pages build and deployment
```

**Access at:** `https://gasyoun.github.io/SanskritLexicography/kosha/`

---

## Part II: samskrtam.ru Deployment

### Prerequisites

- SSH access to samskrtam.ru
- Python 3.10+ installed
- Nginx running on samskrtam.ru

### Step 1: Clone Repo

```bash
ssh user@samskrtam.ru

# Create app directory
mkdir -p /var/www/kosha
cd /var/www/kosha

# Clone repo
git clone https://github.com/gasyoun/SanskritLexicography.git .

# Go to kosha subdir
cd kosha

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Build Indices (One-Time)

```bash
# Extract dictionaries (takes ~20 min)
cd scripts
python extract_page_metadata.py
python extract_dicts_to_json.py
python normalize_and_dedupe.py
python load_into_sqlite.py
python populate_scan_links.py

# Verify database
sqlite3 unified_dict.db "SELECT COUNT(*) FROM entries;"
# Should show: 347000 (or similar)

cd ..
```

### Step 3: Create systemd Service

```bash
# /etc/systemd/system/kosha.service
[Unit]
Description=kosha Sanskrit Dictionary Lookup
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/kosha
Environment="PATH=/usr/local/bin:/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable & start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable kosha
sudo systemctl start kosha
sudo systemctl status kosha
```

### Step 4: Configure Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/kosha
upstream kosha_backend {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name samskrtam.ru;
    
    # Redirect /kosha to FastAPI
    location /kosha/ {
        proxy_pass http://kosha_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Cache static files
        location /kosha/static/ {
            expires 1h;
            add_header Cache-Control "public, max-age=3600";
        }
        
        # API: no cache
        location /kosha/api/ {
            expires off;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
    }
    
    # Health check
    location /kosha/health {
        access_log off;
        proxy_pass http://kosha_backend/health;
    }
}
```

**Enable & reload:**

```bash
sudo ln -s /etc/nginx/sites-available/kosha /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: Monthly Index Rebuild

**Option A: Cron Job (Monthly Refresh)**

```bash
# /etc/cron.d/kosha-rebuild
# Rebuild indices on 1st of each month at 2 AM
0 2 1 * * www-data cd /var/www/kosha && python scripts/load_into_sqlite.py >> /var/log/kosha-rebuild.log 2>&1
```

**Option B: Real-Time Sync (GitHub Webhook)**

```bash
# /var/www/kosha/webhook_receiver.py
"""
GitHub webhook receiver. Triggers rebuild on csl-orig push.
"""
from fastapi import FastAPI, Request
import hmac
import hashlib
import subprocess
import os

app = FastAPI()
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

@app.post("/webhook/csl-orig-push")
async def webhook(request: Request):
    """GitHub webhook: rebuild indices on csl-orig change."""
    
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256', '')
    body = await request.body()
    expected = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        return {'error': 'Invalid signature'}, 403
    
    # Trigger rebuild
    subprocess.run([
        'python', '/var/www/kosha/scripts/load_into_sqlite.py'
    ], check=True)
    
    return {'status': 'Rebuild triggered'}
```

**Setup GitHub webhook:**
1. Go to `gasyoun/SanskritLexicography` → Settings → Webhooks
2. Add webhook:
   - URL: `https://samskrtam.ru/kosha/webhook/csl-orig-push`
   - Secret: (set GITHUB_WEBHOOK_SECRET env var)
   - Events: Push events
3. Test delivery

### Step 6: Monitoring

```bash
# Log tailing
tail -f /var/log/kosha.log

# API test
curl http://samskrtam.ru/kosha/api/lemma/bandh

# Health check
curl http://samskrtam.ru/kosha/health

# Database check
sqlite3 /var/www/kosha/unified_dict.db "SELECT COUNT(*) FROM entries;"
```

---

## Part III: Hybrid Mode (GitHub Pages + samskrtam.ru)

### User Experience

```
User types "bhagavān" at GitHub Pages
  ↓
JavaScript checks local cache (docs/js/data/lemmas.json)
  ├─ IF CACHED (top 5k lemmas):
  │   → Show result instantly (~30ms)
  │   → (Optional) "Full API available at samskrtam.ru"
  │
  └─ IF NOT CACHED:
      → Fallback to samskrtam.ru API
      → (Or show "Not in quick cache; visit samskrtam.ru")
```

### Implementation

**docs/js/app.js:**

```javascript
class KoshaLookup {
    constructor() {
        this.cacheMode = 'hybrid';  // or 'github-pages-only', 'api-only'
        this.apiUrl = 'https://samskrtam.ru/kosha/api';
    }
    
    async search(lemma) {
        if (this.cacheMode !== 'api-only') {
            // Try cache first
            const cached = await this.getCached(lemma);
            if (cached) {
                return {
                    source: 'cache',
                    data: cached,
                    notice: 'Loaded from cache. <a href="' + this.apiUrl + '">View full API</a>'
                };
            }
        }
        
        if (this.cacheMode !== 'github-pages-only') {
            // Try API
            try {
                const data = await this.fetchAPI(lemma);
                return {
                    source: 'api',
                    data: data,
                    notice: null
                };
            } catch (e) {
                return {
                    error: 'Offline: lemma not in cache and API unavailable'
                };
            }
        }
        
        return { error: 'Lemma not found' };
    }
}
```

### Benefits

- **Resilience:** Even if samskrtam.ru is down, users can access top 5k lemmas
- **Speed:** GitHub Pages cache loads instantly (CDN-cached)
- **Freshness:** Full API always has latest corrections
- **Cost:** GitHub Pages free; samskrtam.ru existing infrastructure
- **Scaling:** If traffic spikes, GitHub Pages can absorb it

---

## Part IV: Maintenance & Updates

### Monthly Workflow

```bash
# 1. Pull latest csl-orig corrections
cd /var/www/kosha
git pull origin main
cd scripts
python load_into_sqlite.py

# 2. Rebuild GitHub Pages cache
cd ../../
python docs/build_static_cache.py
git add docs/
git commit -m "chore: monthly cache rebuild"
git push origin main

# 3. Restart samskrtam.ru service
ssh user@samskrtam.ru
sudo systemctl restart kosha

# 4. Verify
curl https://samskrtam.ru/kosha/api/lemma/bandh
curl https://gasyoun.github.io/SanskritLexicography/kosha/
```

### Monitoring

```bash
# Check API health
watch -n 5 'curl -s https://samskrtam.ru/kosha/api/lemma/bandh | jq ".slp1"'

# Check cache size
du -sh docs/js/data/lemmas.json

# Monitor database size
ls -lh /var/www/kosha/unified_dict.db

# View logs
sudo journalctl -u kosha -f
```

---

## Part V: Troubleshooting

### API returns 404

```bash
# Check service is running
sudo systemctl status kosha

# Check database exists
ls -la /var/www/kosha/unified_dict.db

# Check Nginx config
sudo nginx -t

# View logs
sudo journalctl -u kosha -n 50
```

### Slow lookups (>500ms)

```bash
# Check cache hit rate
curl https://samskrtam.ru/kosha/api/stats

# Increase cache size (in app/services/cache_service.py)
# capacity: int = 10000  # was 5000

# Restart
sudo systemctl restart kosha
```

### GitHub Pages not updating

```bash
# Check Actions
https://github.com/gasyoun/SanskritLexicography/actions

# Force rebuild
git push origin main --force

# Clear browser cache
# Ctrl+Shift+Delete (Chrome) or equivalent
```

---

## Summary

| Environment | URL | Setup Time | Maintenance |
|---|---|---|---|
| **GitHub Pages** | `gasyoun.github.io/SanskritLexicography/kosha/` | 30 min | Monthly rebuild |
| **samskrtam.ru** | `samskrtam.ru/kosha/` | 1–2 hours | Webhook (automatic) |
| **Hybrid** | Both | 2 hours | Both |

**Recommended for launch:** Hybrid (GitHub Pages + samskrtam.ru)

---

_Dr. Mārcis Gasūns_
