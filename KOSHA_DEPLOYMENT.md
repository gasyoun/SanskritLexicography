# kosha — Deployment Reference (salvaged)

_Created: 02-07-2026 · Last updated: 02-07-2026_

> **Provenance.** Salvaged 02-07-2026 from the deleted `kosha/DEPLOYMENT.md`
> (plus the API contract and `.env` keys from `kosha/README.md`) during the
> kosha triage — see
> [KOSHA_FOLDER_SETUP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_FOLDER_SETUP.md).
> The originals carried four config defects and several fabricated values; all
> are fixed below. **This is a pre-build draft** — none of it is deployed, and
> per meta-decision M2 the application will live in its own dedicated repo
> (referred to as `gasyoun/kosha` below), not in SanskritLexicography.

---

## Deployment modes

| Mode | URL (future) | Type | Freshness | Cost |
|------|-----|------|-----------|------|
| **GitHub Pages** | Pages site of the dedicated kosha repo | Static cache of top lemmas | Batch rebuild | Free |
| **samskrtam.ru** | `samskrtam.ru/kosha/` | FastAPI server | Rebuild on cadence (open: leaning nightly) | Existing infra |
| **Hybrid** | Both | Cache-then-API fallback | Best of both | Free + existing |

**NOT** `gasyoun.github.io/SanskritLexicography/kosha/` as originally written —
this repo's Pages already serves the PWG article site from `gh-pages`
(meta-decision M4).

## Part I: GitHub Pages tier (dedicated repo)

Enable Pages on the dedicated repo (Settings → Pages → deploy from branch,
`/docs` folder or an Actions workflow). Static layout:

```
docs/
├── index.html
├── css/style.css
└── js/
    ├── app.js
    ├── transcode.js        ← thin wrapper over sanskrit-util JS, NOT a new transcoder
    └── data/lemmas.json    ← precomputed top-N cache
```

Cache builder sketch (`scripts/build_static_cache.py` — canonical path is
`scripts/`, earlier docs disagreed with themselves): query the unified SQLite
DB for the top-N lemmas by entry count, emit minified JSON. Size the N to the
GitHub 100 MB file limit — the original "top 5k ≈ 50 MB gzipped" figure was a
guess; measure before committing.

Client-side hybrid lookup (cache first, API fallback):

```javascript
class KoshaLookup {
    constructor() {
        this.lemmaCache = null;
        this.apiUrl = 'https://samskrtam.ru/kosha/api';
    }
    async loadCache() {
        const resp = await fetch('js/data/lemmas.json');
        if (resp.ok) this.lemmaCache = await resp.json();
    }
    async search(lemma) {
        if (this.lemmaCache && lemma in this.lemmaCache)
            return { source: 'cache', data: this.lemmaCache[lemma] };
        try {
            const resp = await fetch(`${this.apiUrl}/lemma/${encodeURIComponent(lemma)}`);
            if (resp.ok) return { source: 'api', data: await resp.json() };
        } catch (e) { /* offline */ }
        return { error: 'Lemma not in cache and API unavailable' };
    }
}
```

Deploy = commit `docs/` and push. (The original doc's "force rebuild:
`git push --force`" troubleshooting advice is deleted — force-pushing is never
a Pages fix.)

## Part II: samskrtam.ru API tier

Prereqs: SSH, Python 3.10+, nginx.

```bash
ssh user@samskrtam.ru
sudo mkdir -p /var/www/kosha && cd /var/www/kosha
git clone https://github.com/gasyoun/kosha.git .   # dedicated repo → app at root
pip install -r requirements.txt
# build the SQLite index per the (re-planned, reuse-first) Phase-1 pipeline
```

systemd unit — `/etc/systemd/system/kosha.service`:

```ini
[Unit]
Description=kosha Sanskrit Dictionary Lookup
After=network.target

[Service]
# Original had Type=notify — uvicorn does not implement sd_notify; the unit
# would hang at start and be killed on timeout. Use exec.
Type=exec
User=www-data
WorkingDirectory=/var/www/kosha
Environment="PATH=/usr/local/bin:/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

(The original also set `WorkingDirectory=/var/www/kosha` while its own clone
steps put the app at `/var/www/kosha/kosha` — moot now that the dedicated repo
clones with the app at root.)

nginx — `/etc/nginx/sites-available/kosha`. The original nested `location`
blocks contained **no `proxy_pass`** (not inherited in nginx), so static and
API requests would 404 into the filesystem. Fixed:

```nginx
upstream kosha_backend {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name samskrtam.ru;   # add TLS via certbot; serve https in production

    location /kosha/static/ {
        proxy_pass http://kosha_backend/static/;
        expires 1h;
        add_header Cache-Control "public, max-age=3600";
    }

    location /kosha/api/ {
        proxy_pass http://kosha_backend/api/;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location /kosha/health {
        access_log off;
        proxy_pass http://kosha_backend/health;
    }

    location /kosha/ {
        proxy_pass http://kosha_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Rebuild cadence (open decision — leaning nightly):

```bash
# /etc/cron.d/kosha-rebuild — nightly at 2 AM (adjust when cadence is decided)
0 2 * * * www-data cd /var/www/kosha && python scripts/load_into_sqlite.py >> /var/log/kosha-rebuild.log 2>&1
```

Alternative: a GitHub-webhook receiver on csl-orig pushes (HMAC-verified
`X-Hub-Signature-256`, then trigger the rebuild script). Fine as a pattern,
but note the original doc simultaneously "locked" monthly cadence and
recommended the webhook — pick one when deciding cadence.

Monitoring: `sudo journalctl -u kosha -f`, `curl https://samskrtam.ru/kosha/health`.

## Appendix A: API contract (draft, salvaged from kosha/README.md)

Corrected from the original, which used an impossible "MW vol. 5, p. 32"
(MW 1899 is single-volume; `<pc>` is page,column), the nonexistent
`cologne.archive.org` domain, and IAST values labeled SLP1.

```
GET /api/lemma/banD?encoding=slp1        # SLP1 for bandh is banD, not "bandh"
{
  "slp1": "banD",
  "iast": "bandh",
  "entries": [
    {
      "dict": "mw",
      "page": 720, "column": 1,          # from <pc>720,1 — page,column; MW has no volumes
      "senses": [{ "text": "to bind, fasten" }],
      "scan": {
        "url": "https://www.sanskrit-lexicon.uni-koeln.de/...",   # via csl-websanlexicon serveimg/servepdf; resolve with ls_resolver.py
        "link_text": "p. 720, col. 1"
      }
    }
  ]
}

GET /api/lemma/form/bhagavān?encoding=iast   → { "form": "bhagavān", "lemmas": ["bhagavant-"], ... }
GET /api/search?q=banD&limit=50
GET /api/scan/banD
```

Per-dict `<pc>` formats (ground truth, 02-07-2026 audit — any comma-split
parser fails on 2 of 3): MW `720,1` = page,column (1 volume); PWG `1-0001` =
volume-page, hyphen (7 volumes); AP90 `0001-a` = page-column-letter.

## Appendix B: `.env` keys (draft)

```env
DATABASE_PATH=./unified_dict.db
CACHE_SIZE=5000
CACHE_TTL=3600
LOG_LEVEL=INFO
# Scans are served by Cologne (csl-websanlexicon serveimg/servepdf), not the
# invented cologne.archive.org of the original:
COLOGNE_SCAN_BASE=https://www.sanskrit-lexicon.uni-koeln.de
```

---

_Dr. Mārcis Gasūns_
