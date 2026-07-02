# kosha Implementation Plan — Week-by-Week Breakdown

_Created: 02-07-2026 · Last updated: 02-07-2026_

## Overview

**Timeline:** 11 weeks  
**Team:** 1–2 engineers (Python backend, JavaScript frontend)  
**Start:** Week of July 7, 2026  
**MVP completion (Phases 1–2b):** ~5 weeks  
**Full (Phases 1–5):** ~11 weeks

---

## Phase 1: Core Dictionary Indexing (Weeks 1–2)

### Week 1: Data Preparation & Index Schema

**Mon–Tue: Extract Dictionary Metadata**

**Task 1.1.1:** Parse `<pc>` page metadata from csl-orig

```python
# scripts/extract_page_metadata.py
"""
Parse all Cologne dict .txt files; extract L-number + <pc> tags.
Output: dict_page_map.json
"""
import re
import json
from pathlib import Path

DICTS = ['mw', 'pwg', 'ap90']  # Phase 1: priority 3

def extract_metadata(dict_code):
    """Extract (L-number, page_info, k1_key) from dict file."""
    dict_file = Path(f"../../csl-orig/v02/{dict_code}/{dict_code}.txt")
    entries = {}
    
    with open(dict_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by <LEND>
    for entry in content.split('<LEND>'):
        if '<L>' not in entry:
            continue
        
        # Extract L-number
        l_match = re.search(r'<L>([^<]+)<', entry)
        if not l_match:
            continue
        l_num = l_match.group(1).strip()
        
        # Extract page info
        pc_match = re.search(r'<pc>([^<]+)<', entry)
        page_info = pc_match.group(1).strip() if pc_match else None
        
        # Extract k1 (SLP1 key)
        k1_match = re.search(r'<k1>([^<]+)<', entry)
        k1_key = k1_match.group(1).strip() if k1_match else None
        
        if k1_key and page_info:
            entries[k1_key] = {
                'L': l_num,
                'page_info': page_info,
                'volume': page_info.split(',')[0] if ',' in page_info else '1',
                'page': page_info.split(',')[-1]
            }
    
    return entries

# Build master map
page_map = {}
for dict_code in DICTS:
    page_map[dict_code] = extract_metadata(dict_code)
    print(f"{dict_code}: {len(page_map[dict_code])} entries with page metadata")

# Output
with open('dict_page_map.json', 'w', encoding='utf-8') as f:
    json.dump(page_map, f, ensure_ascii=False, indent=2)
```

**Time:** 2–3 hours  
**Acceptance:** `dict_page_map.json` with 300k+ entries (MW: ~193k, PWG: ~106k, AP90: ~48k)

---

**Wed–Thu: Extract Dictionaries into JSON**

**Task 1.1.2:** Parse csl-orig XML; convert to normalized JSON

```python
# scripts/extract_dicts_to_json.py
"""
Parse csl-orig dict .txt files; convert XML to flat JSON lines.
Output: dicts_raw.jsonl (one JSON object per line per entry)

Format:
{
  "dict": "mw",
  "L": "523",
  "slp1_key": "bandh",
  "iast": "bandh",
  "page_info": "5,32",
  "senses_raw": "<lex>m.</lex> ¦ 9 P. (badhnāti...) to bind...",
  "citations": ["BhG 1.1", "MBh 1.5"],
  "etymology": "√ bandh-"
}
"""
import json
import re
from pathlib import Path

def parse_dict(dict_code):
    """Parse dict file; yield JSON objects."""
    dict_file = Path(f"../../csl-orig/v02/{dict_code}/{dict_code}.txt")
    
    with open(dict_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for entry in content.split('<LEND>'):
        if '<L>' not in entry:
            continue
        
        # Extract fields
        l_match = re.search(r'<L>([^<]+)<', entry)
        k1_match = re.search(r'<k1>([^<]+)<', entry)
        k2_match = re.search(r'<k2>([^<]+)<', entry)
        pc_match = re.search(r'<pc>([^<]+)<', entry)
        
        if not (l_match and k1_match):
            continue
        
        l_num = l_match.group(1).strip()
        slp1_key = k1_match.group(1).strip()
        k2_key = k2_match.group(1).strip() if k2_match else slp1_key
        page_info = pc_match.group(1).strip() if pc_match else '0,0'
        
        # Extract sense text (everything after first <L>...<k2> line)
        sense_start = entry.find('<k2>') + 30  # skip <k2>...<
        senses_raw = entry[sense_start:].strip()
        
        # Extract citations (<ls>...</ls>)
        citations = re.findall(r'<ls>([^<]+)</ls>', entry)
        
        # Extract etymology (√ marker)
        etym_match = re.search(r'√\s*([^\s,;]+)', entry)
        etymology = etym_match.group(1) if etym_match else None
        
        yield {
            'dict': dict_code,
            'L': l_num,
            'slp1_key': slp1_key,
            'k2_key': k2_key,
            'page_info': page_info,
            'senses_raw': senses_raw[:500],  # truncate for now
            'citations': citations,
            'etymology': etymology
        }

# Output JSONL
output_file = Path('dicts_raw.jsonl')
total = 0
for dict_code in ['mw', 'pwg', 'ap90']:
    with open(output_file, 'a', encoding='utf-8') as f:
        for obj in parse_dict(dict_code):
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')
            total += 1

print(f"Extracted {total} entries to dicts_raw.jsonl")
```

**Time:** 3–4 hours  
**Acceptance:** `dicts_raw.jsonl` with 300k+ entries; spot-check 10 entries manually

---

**Fri: Normalize SLP1 Keys & Homonym Deduplication**

**Task 1.1.3:** Join MW + PWG + AP90; resolve homonym conflicts

```python
# scripts/normalize_and_dedupe.py
"""
Normalize SLP1 keys (strip diacritics for matching).
Build homonym map: (slp1_key, homonym_id) → [dicts that have it]
Output: unified_headwords.json
"""
from collections import defaultdict
import json

# Load raw extracts
entries_by_dict = defaultdict(lambda: defaultdict(list))
with open('dicts_raw.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        entries_by_dict[obj['dict']][obj['slp1_key']].append(obj)

# Build union headword list
union_headwords = {}
homonym_counter = defaultdict(int)

for dict_code in ['mw', 'pwg', 'ap90']:
    for slp1_key, entries_list in entries_by_dict[dict_code].items():
        if slp1_key not in union_headwords:
            union_headwords[slp1_key] = {
                'slp1': slp1_key,
                'homonym_count': len(entries_list),
                'dicts': {}
            }
        
        union_headwords[slp1_key]['dicts'][dict_code] = {
            'entries': len(entries_list),
            'L_numbers': [e['L'] for e in entries_list],
            'coverage': len(entries_list)
        }

# Output
with open('unified_headwords.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_union': len(union_headwords),
        'by_dict_coverage': {
            'mw_only': sum(1 for h in union_headwords.values() if 'mw' in h['dicts'] and len(h['dicts']) == 1),
            'pwg_only': sum(1 for h in union_headwords.values() if 'pwg' in h['dicts'] and len(h['dicts']) == 1),
            'ap90_only': sum(1 for h in union_headwords.values() if 'ap90' in h['dicts'] and len(h['dicts']) == 1),
            'shared_mw_pwg': sum(1 for h in union_headwords.values() if 'mw' in h['dicts'] and 'pwg' in h['dicts']),
            'all_three': sum(1 for h in union_headwords.values() if len(h['dicts']) == 3)
        },
        'headwords': union_headwords
    }, ensure_ascii=False, indent=2)

print(f"Union headword list: {len(union_headwords)} unique lemmas")
```

**Time:** 2–3 hours  
**Acceptance:** `unified_headwords.json` with coverage matrix (e.g., "95k MW + PWG overlap")

---

### Week 2: SQLite Index Build & API Stub

**Mon–Tue: SQLite Schema & FTS5 Index**

**Task 1.2.1:** Design schema; build FTS5 index

```sql
-- schema.sql
CREATE TABLE IF NOT EXISTS lemmas (
  id INTEGER PRIMARY KEY,
  slp1_key TEXT NOT NULL,
  iast TEXT,
  homonym_id INTEGER,
  UNIQUE(slp1_key, homonym_id)
);

CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY,
  lemma_id INTEGER NOT NULL,
  dict_code TEXT NOT NULL,  -- 'mw', 'pwg', 'ap90'
  L_number TEXT,
  page_volume INTEGER,
  page_number INTEGER,
  senses_text TEXT,
  senses_json JSON,
  citations JSON,  -- ["BhG 1.1", "MBh 5.20"]
  etymology TEXT,
  raw_xml TEXT,  -- for later enrichment
  FOREIGN KEY(lemma_id) REFERENCES lemmas(id)
);

-- Full-text search index
CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
  headword,
  senses,
  content=entries,
  content_rowid=id
);

-- Morphological forms (from Sanskrit Heritage expansion)
CREATE TABLE IF NOT EXISTS morphological_forms (
  form_slp1 TEXT PRIMARY KEY,
  lemma_slp1 TEXT NOT NULL,
  form_type TEXT,  -- 'nom.sg', 'acc.pl', etc.
  FOREIGN KEY(lemma_slp1) REFERENCES lemmas(slp1_key)
);

-- Page metadata (for scan links)
CREATE TABLE IF NOT EXISTS scan_links (
  dict_code TEXT,
  slp1_key TEXT,
  volume INTEGER,
  page INTEGER,
  url TEXT,  -- will be filled in Phase 2b
  PRIMARY KEY(dict_code, slp1_key)
);
```

**Time:** 3–4 hours  
**Acceptance:** `unified_dict.db` created; schema verified; tables populated with 300k+ entries

---

**Wed: Load Data into SQLite**

**Task 1.2.2:** Ingest `dicts_raw.jsonl` into database

```python
# scripts/load_into_sqlite.py
"""
Load extracted dict data into SQLite; build FTS5 index.
"""
import sqlite3
import json
from pathlib import Path

db = sqlite3.connect('unified_dict.db')
cursor = db.cursor()

# Load lemmas + entries
lemma_cache = {}
entry_count = 0

with open('dicts_raw.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        slp1_key = obj['slp1_key']
        
        # Insert lemma (once per unique key)
        if slp1_key not in lemma_cache:
            cursor.execute(
                'INSERT OR IGNORE INTO lemmas (slp1_key, iast) VALUES (?, ?)',
                (slp1_key, obj.get('iast', slp1_key))
            )
            db.commit()
            lemma_cache[slp1_key] = cursor.lastrowid
        
        lemma_id = lemma_cache[slp1_key]
        
        # Insert entry
        cursor.execute('''
            INSERT INTO entries 
            (lemma_id, dict_code, L_number, page_volume, page_number, 
             senses_text, citations, etymology, raw_xml)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lemma_id,
            obj['dict'],
            obj['L'],
            int(obj['page_info'].split(',')[0]) if ',' in obj['page_info'] else 1,
            int(obj['page_info'].split(',')[-1]) if ',' in obj['page_info'] else 0,
            obj.get('senses_raw', ''),
            json.dumps(obj.get('citations', [])),
            obj.get('etymology', None),
            obj.get('raw_xml', '')[:1000]
        ))
        entry_count += 1

db.commit()

# Build FTS5 index
cursor.execute('''
    INSERT INTO entries_fts (rowid, headword, senses)
    SELECT id, (SELECT iast FROM lemmas WHERE lemmas.id = entries.lemma_id), senses_text
    FROM entries
''')
db.commit()
db.close()

print(f"Loaded {entry_count} entries into unified_dict.db")
print("FTS5 index built successfully")
```

**Time:** 2–3 hours  
**Acceptance:** `unified_dict.db` has 300k+ entries; FTS5 index queryable

---

**Thu–Fri: Morphological Expansion Setup**

**Task 1.2.3:** Integrate Sanskrit Heritage API for form expansion

```python
# app/services/morph_service.py
"""
Query Sanskrit Heritage API for morphological forms.
Cache results; populate morphological_forms table.
"""
import requests
import json
from functools import lru_cache

HERITAGE_API = "https://sanskrit.inria.fr/api/morphoanalysis"

@lru_cache(maxsize=10000)
def expand_form(form_slp1: str):
    """
    Query Sanskrit Heritage for morphological forms.
    Returns: {"lemmas": [{"name": "dharma", "forms": ["dharma", "dharmam", ...]}]}
    """
    try:
        resp = requests.get(HERITAGE_API, params={'word': form_slp1}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None

def populate_morphological_forms():
    """
    Populate morphological_forms table from Sanskrit Heritage.
    Runs once at indexing time; results cached in DB.
    """
    import sqlite3
    db = sqlite3.connect('unified_dict.db')
    cursor = db.cursor()
    
    # Get all lemmas
    cursor.execute('SELECT slp1_key FROM lemmas')
    lemmas = [row[0] for row in cursor.fetchall()]
    
    forms_added = 0
    for lemma in lemmas:
        result = expand_form(lemma)
        if result and 'forms' in result:
            for form_variant in result.get('forms', []):
                cursor.execute('''
                    INSERT OR IGNORE INTO morphological_forms 
                    (form_slp1, lemma_slp1, form_type)
                    VALUES (?, ?, ?)
                ''', (form_variant, lemma, 'variant'))
                forms_added += 1
    
    db.commit()
    db.close()
    print(f"Added {forms_added} morphological forms to index")

if __name__ == '__main__':
    populate_morphological_forms()
```

**Time:** 2–3 hours  
**Acceptance:** `morphological_forms` table populated; test query `bhagavān` → `bhagavant-` works

---

**Week 1–2 Deliverables:**

- ✅ `dict_page_map.json` (page metadata extracted)
- ✅ `dicts_raw.jsonl` (300k+ entries normalized)
- ✅ `unified_dict.db` (SQLite with FTS5 index)
- ✅ `morphological_forms` populated (form → lemma mapping)
- ✅ Baseline latency measured (target: ≤200ms for cache miss, ≤10ms for cache hit)

---

## Phase 2: Translator UI & Fast Lookup (Weeks 3–4)

### Week 3: API Endpoints & Caching

**Task 2.1.1:** FastAPI endpoints for lookup

```python
# app/routers/lemma.py
from fastapi import APIRouter, Query
from app.services.dict_service import DictService
from app.services.cache_service import CacheService

router = APIRouter(prefix="/api/lemma", tags=["lemma"])
dict_svc = DictService()
cache_svc = CacheService()

@router.get("/{slp1}")
async def get_lemma(
    slp1: str,
    encoding: str = Query("slp1", regex="^(slp1|iast|devanagari|hk)$"),
    dicts: str = Query("mw,pwg,ap90")
):
    """
    Get lemma entry from all requested dictionaries.
    
    Returns:
    {
      "slp1": "bandh",
      "iast": "bandh",
      "encoding": "iast",
      "entries": [
        {
          "dict": "mw",
          "volume": 5,
          "page": 32,
          "senses": [
            { "sense_id": "1", "text": "to bind, fasten", "citations": ["BhG 1.1"] }
          ],
          "grammar": { "class": "9P", "conjugation": "parasmaipada" },
          "etymology": "√ bandh-"
        },
        ...
      ]
    }
    """
    # Check cache first
    cache_key = f"lemma:{slp1}:{dicts}:{encoding}"
    cached = cache_svc.get(cache_key)
    if cached:
        return cached
    
    # Query database
    result = dict_svc.get_lemma_entries(slp1, dicts.split(','))
    
    # Transcode to requested encoding
    result['encoding'] = encoding
    # (transcode logic here)
    
    # Cache for 1 hour
    cache_svc.set(cache_key, result, ttl=3600)
    
    return result

@router.get("/form/{form}")
async def lookup_form(
    form: str,
    encoding: str = Query("slp1", regex="^(slp1|iast|devanagari|hk)$")
):
    """
    Lookup an inflected form (not a lemma).
    Expands form morphologically; returns matching lemmas.
    """
    lemmas = dict_svc.expand_form(form)
    
    results = []
    for lemma in lemmas:
        result = await get_lemma(lemma, encoding)
        results.append(result)
    
    return {
        'form': form,
        'lemmas': [r['slp1'] for r in results],
        'entries': results
    }

@router.get("/search")
async def search(
    q: str,
    dicts: str = Query("mw,pwg,ap90"),
    limit: int = Query(50, le=5000)
):
    """
    Full-text search across all dictionaries.
    """
    results = dict_svc.search_fts(q, dicts.split(','), limit)
    return {
        'query': q,
        'results': results,
        'count': len(results)
    }
```

**Time:** 4–6 hours  
**Acceptance:** Endpoints live at `http://localhost:8000/api/lemma/bandh`; latency ≤200ms

---

**Task 2.1.2:** In-memory caching for top 5k lemmas

```python
# app/services/cache_service.py
import json
from functools import lru_cache
from typing import Optional

class CacheService:
    def __init__(self, capacity: int = 5000):
        self.cache = {}
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[dict]:
        value = self.cache.get(key)
        if value:
            self.hits += 1
            return value
        self.misses += 1
        return None
    
    def set(self, key: str, value: dict, ttl: int = 3600):
        if len(self.cache) >= self.capacity:
            # Evict least-recently-used (simple FIFO for now)
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key] = value
    
    def preload_top_lemmas(self, db, count: int = 5000):
        """
        On startup, preload top N lemmas by frequency.
        """
        cursor = db.cursor()
        cursor.execute('''
            SELECT l.slp1_key
            FROM lemmas l
            LEFT JOIN entries e ON e.lemma_id = l.id
            GROUP BY l.id
            ORDER BY COUNT(e.id) DESC
            LIMIT ?
        ''', (count,))
        
        for (slp1,) in cursor.fetchall():
            # Populate cache
            result = dict_svc.get_lemma_entries(slp1, ['mw', 'pwg', 'ap90'])
            self.set(f"lemma:{slp1}:mw,pwg,ap90:iast", result)
    
    def stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'size': len(self.cache)
        }
```

**Time:** 2–3 hours  
**Acceptance:** Cache preloads on startup; hit rate ≥80% for random queries

---

### Week 4: UI Components & Encoding Toggle

**Task 2.2.1:** Frontend: Lookup form + result cards

```html
<!-- templates/search_page.html -->
<!DOCTYPE html>
<html>
<head>
    <title>kosha — Sanskrit Dictionary Lookup</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>kosha</h1>
        
        <!-- Search input -->
        <div class="search-box">
            <input type="text" id="lemma-input" placeholder="Type Sanskrit lemma or form...">
            <select id="encoding-select">
                <option value="slp1">SLP1</option>
                <option value="iast" selected>IAST</option>
                <option value="devanagari">Devanagari</option>
                <option value="hk">Harvard-Kyoto</option>
            </select>
            <button id="search-btn">Search</button>
        </div>
        
        <!-- Grammar toggle -->
        <div class="controls">
            <label>
                <input type="checkbox" id="grammar-toggle"> Show full grammar
            </label>
        </div>
        
        <!-- Results -->
        <div id="results" class="results"></div>
    </div>
    
    <script src="/static/app.js"></script>
</body>
</html>
```

```javascript
// static/app.js
class KoshaLookup {
    constructor() {
        this.input = document.getElementById('lemma-input');
        this.encodingSelect = document.getElementById('encoding-select');
        this.grammarToggle = document.getElementById('grammar-toggle');
        this.resultsDiv = document.getElementById('results');
        
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.search();
        });
        document.getElementById('search-btn').addEventListener('click', () => this.search());
        this.grammarToggle.addEventListener('change', () => this.renderResults());
    }
    
    async search() {
        const lemma = this.input.value.trim();
        if (!lemma) return;
        
        const encoding = this.encodingSelect.value;
        const resp = await fetch(`/api/lemma/${lemma}?encoding=${encoding}`);
        
        if (!resp.ok) {
            this.resultsDiv.innerHTML = `<p class="error">Not found: ${lemma}</p>`;
            return;
        }
        
        this.data = await resp.json();
        this.renderResults();
    }
    
    renderResults() {
        if (!this.data) return;
        
        const showFullGrammar = this.grammarToggle.checked;
        const encoding = this.encodingSelect.value;
        
        let html = `<h2>${this.transcodeText(this.data.slp1, encoding)}</h2>`;
        
        for (const entry of this.data.entries) {
            html += this.renderEntry(entry, showFullGrammar, encoding);
        }
        
        this.resultsDiv.innerHTML = html;
    }
    
    renderEntry(entry, showFullGrammar, encoding) {
        const dictName = {
            'mw': 'Monier-Williams',
            'pwg': 'Böhtlingk & Roth PWG',
            'ap90': 'Apte Practical'
        }[entry.dict];
        
        let sensesHtml = '';
        for (const sense of entry.senses) {
            sensesHtml += `<li class="sense">${sense.text}</li>`;
        }
        
        let grammarHtml = '';
        if (showFullGrammar && entry.grammar) {
            grammarHtml = `
                <div class="grammar-full">
                    <strong>Grammar:</strong> ${entry.grammar.class} ${entry.grammar.conjugation}
                </div>
            `;
        }
        
        return `
            <div class="entry">
                <h3>${dictName}</h3>
                <p class="ref">vol. ${entry.volume}, p. ${entry.page}</p>
                <ul class="senses">${sensesHtml}</ul>
                ${grammarHtml}
            </div>
        `;
    }
    
    transcodeText(text, encoding) {
        // Use sanskrit-util JS library
        switch (encoding) {
            case 'iast': return SanskritUtil.slp1ToIast(text);
            case 'devanagari': return SanskritUtil.slp1ToDevanagari(text);
            case 'hk': return SanskritUtil.slp1ToHK(text);
            default: return text;
        }
    }
}

window.addEventListener('DOMContentLoaded', () => {
    new KoshaLookup();
});
```

**Time:** 4–5 hours  
**Acceptance:** UI loads; search works; encoding toggle switches IAST ↔ Devanagari instantly

---

**Task 2.2.2:** CSS styling + mobile responsiveness

```css
/* static/style.css */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #333;
    line-height: 1.6;
    background: #f9f9f9;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    font-size: 2em;
    margin-bottom: 20px;
    text-align: center;
}

.search-box {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.search-box input {
    flex: 1;
    padding: 12px;
    font-size: 1em;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-box select {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-box button {
    padding: 12px 24px;
    background: #0066cc;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.search-box button:hover {
    background: #0052a3;
}

.entry {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
}

.entry h3 {
    font-size: 1.2em;
    margin-bottom: 8px;
    color: #0066cc;
}

.entry .ref {
    font-size: 0.9em;
    color: #666;
    margin-bottom: 12px;
}

.senses {
    list-style: none;
    padding-left: 20px;
}

.sense {
    margin-bottom: 8px;
    padding-left: 20px;
    position: relative;
}

.sense:before {
    content: "•";
    position: absolute;
    left: 0;
}

.grammar-full {
    background: #f0f8ff;
    padding: 12px;
    border-left: 4px solid #0066cc;
    margin-top: 12px;
    font-size: 0.9em;
}

/* Mobile */
@media (max-width: 768px) {
    .search-box {
        flex-direction: column;
    }
    
    .search-box input,
    .search-box select,
    .search-box button {
        width: 100%;
    }
    
    h1 {
        font-size: 1.5em;
    }
    
    .entry {
        padding: 12px;
    }
}
```

**Time:** 2–3 hours  
**Acceptance:** UI looks good on mobile (375px width); no horizontal scrolling

---

**Week 3–4 Deliverables:**

- ✅ `/api/lemma/{slp1}` endpoint working (sub-100ms for cached entries)
- ✅ `/api/lemma/form/{form}` endpoint for inflected forms
- ✅ In-memory cache preloaded with top 5k lemmas
- ✅ Frontend UI with search + encoding toggle
- ✅ Mobile-responsive design
- ✅ Encoding toggle switches IAST ↔ Devanagari in real-time

---

## Phase 2b: Scan Linking (Weeks 4–5)

### Week 4: Page Metadata & Cologne Integration

**Task 2b.1.1:** Contact Cologne; obtain scan URL patterns

```python
# scripts/cologne_scan_config.py
"""
Query Cologne server for available scans + URL patterns.
Output: scan_config.json
"""

COLOGNE_SCAN_BASE = "https://cologne.archive.org/dictionaries"  # TBD: confirm with Cologne

SCAN_CONFIG = {
    'mw': {
        'name': 'Monier-Williams Sanskrit-English Dictionary',
        'edition': '1899 (2nd ed.)',
        'volumes': 7,
        'scan_source': 'cologne',
        'url_pattern': f'{COLOGNE_SCAN_BASE}/mw/vol{{volume}}/page{{page:04d}}.jpg'
    },
    'pwg': {
        'name': 'Böhtlingk & Roth Großes Petersburger Wörterbuch',
        'edition': '1875',
        'volumes': 6,
        'scan_source': 'cologne',
        'url_pattern': f'{COLOGNE_SCAN_BASE}/pwg/vol{{volume}}/page{{page:04d}}.jpg'
    },
    'ap90': {
        'name': 'Apte Practical Sanskrit-English Dictionary',
        'edition': '1890',
        'volumes': 1,
        'scan_source': 'internet-archive',
        'url_pattern': 'https://archive.org/download/ap90/page{{page}}.jpg'
    }
}

import json
with open('scan_config.json', 'w') as f:
    json.dump(SCAN_CONFIG, f, indent=2)
```

**Time:** 2–3 hours (mostly waiting for Cologne response)  
**Acceptance:** `scan_config.json` with confirmed URL patterns

---

**Task 2b.1.2:** Populate scan_links table

```python
# scripts/populate_scan_links.py
"""
Populate scan_links table using page metadata + config.
"""
import sqlite3
import json

db = sqlite3.connect('unified_dict.db')
cursor = db.cursor()

with open('scan_config.json') as f:
    scan_config = json.load(f)

# For each dict, populate scan_links
for dict_code, config in scan_config.items():
    url_pattern = config['url_pattern']
    
    cursor.execute(f'''
        INSERT INTO scan_links (dict_code, slp1_key, volume, page, url)
        SELECT ?, e.lemma_id, e.page_volume, e.page_number,
               REPLACE(
                   REPLACE('{url_pattern}', '{{volume}}', CAST(e.page_volume AS TEXT)),
                   '{{page:04d}}', PRINTF('%04d', e.page_number)
               )
        FROM (
            SELECT DISTINCT l.slp1_key, e.page_volume, e.page_number
            FROM entries e
            JOIN lemmas l ON l.id = e.lemma_id
            WHERE e.dict_code = ?
        ) e
        WHERE e.page_volume IS NOT NULL AND e.page_number > 0
    ''', (dict_code, dict_code))

db.commit()
cursor.execute('SELECT COUNT(*) FROM scan_links')
count = cursor.fetchone()[0]
print(f"Populated {count} scan links")
db.close()
```

**Time:** 1–2 hours  
**Acceptance:** `scan_links` table has 200k+ entries with URLs

---

### Week 5: Scan API & UI Integration

**Task 2b.2.1:** ScanResolver service

```python
# app/services/scan_service.py
import sqlite3
import json

class ScanResolver:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_scans(self, slp1: str, dicts: list[str] = None):
        """
        Resolve scan links for a headword.
        Returns: {"mw": {...}, "pwg": {...}, ...}
        """
        if dicts is None:
            dicts = ['mw', 'pwg', 'ap90']
        
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        scans = {}
        for dict_code in dicts:
            cursor.execute('''
                SELECT volume, page, url FROM scan_links
                WHERE slp1_key = ? AND dict_code = ?
            ''', (slp1, dict_code))
            
            row = cursor.fetchone()
            if row:
                volume, page, url = row
                scans[dict_code] = {
                    'volume': volume,
                    'page': page,
                    'url': url,
                    'link_text': self._format_link(volume, page)
                }
        
        db.close()
        return scans
    
    def _format_link(self, volume, page):
        if volume and volume > 0:
            return f"vol. {volume}, p. {page}"
        return f"p. {page}"

# app/routers/scan.py
from fastapi import APIRouter
from app.services.scan_service import ScanResolver

router = APIRouter(prefix="/api/scan", tags=["scan"])
scan_resolver = ScanResolver('unified_dict.db')

@router.get("/{slp1}")
async def get_scans(slp1: str):
    """Get scan links for a lemma."""
    scans = scan_resolver.get_scans(slp1)
    return {
        'slp1': slp1,
        'scans': scans,
        'count': len(scans)
    }
```

**Time:** 2–3 hours  
**Acceptance:** `/api/scan/bandh` returns URLs for all 3 dicts

---

**Task 2b.2.2:** Update result template with scan links

```html
<!-- templates/result_fragment.html (updated) -->
{% for entry in entries %}
    <div class="entry">
        <h3>{{ entry.dict_name }}</h3>
        
        <div class="senses">
            {% for sense in entry.senses %}
                <div class="sense">{{ sense.text }}</div>
            {% endfor %}
        </div>
        
        <!-- NEW: Scan link -->
        {% if entry.scan %}
            <p class="scan-link">
                <a href="{{ entry.scan.url }}" target="_blank" rel="noopener">
                    📄 View in original: {{ entry.scan.link_text }}
                </a>
            </p>
        {% endif %}
    </div>
{% endfor %}
```

```javascript
// static/app.js (updated)
async search() {
    const lemma = this.input.value.trim();
    if (!lemma) return;
    
    const encoding = this.encodingSelect.value;
    
    // Get entry data
    const entryResp = await fetch(`/api/lemma/${lemma}?encoding=${encoding}`);
    if (!entryResp.ok) {
        this.resultsDiv.innerHTML = `<p class="error">Not found: ${lemma}</p>`;
        return;
    }
    this.data = await entryResp.json();
    
    // Get scan links
    const scanResp = await fetch(`/api/scan/${lemma}`);
    this.scans = scanResp.ok ? await scanResp.json() : null;
    
    this.renderResults();
}

renderEntry(entry, showFullGrammar, encoding) {
    // ... existing code ...
    
    // Add scan link
    let scanHtml = '';
    if (this.scans && this.scans.scans[entry.dict]) {
        const scan = this.scans.scans[entry.dict];
        scanHtml = `
            <p class="scan-link">
                <a href="${scan.url}" target="_blank">
                    📄 View in original: ${scan.link_text}
                </a>
            </p>
        `;
    }
    
    return `
        <div class="entry">
            <h3>${dictName}</h3>
            <p class="ref">vol. ${entry.volume}, p. ${entry.page}</p>
            <ul class="senses">${sensesHtml}</ul>
            ${scanHtml}
            ${grammarHtml}
        </div>
    `;
}
```

**Time:** 2–3 hours  
**Acceptance:** Every result card shows "View in original" link; clicking opens Cologne scan

---

**Phase 2b Deliverables:**

- ✅ `scan_config.json` with URL patterns (confirmed with Cologne)
- ✅ `scan_links` table populated (200k+ entries)
- ✅ `/api/scan/{slp1}` endpoint
- ✅ UI shows scan links in result cards
- ✅ Clicking link opens Cologne scan in new tab

---

## Phase 3: Etymology + KEWA (Weeks 6–7)

**TODO: Detailed tasks for etymology integration**
- Extract KEWA etymon data
- Link headwords to roots
- Render etymology tree
- Add root crosswalks (from WhitneyRoots if available)

---

## Phase 4: Corpus Evidence (Weeks 8–9)

**TODO: Detailed tasks for corpus integration**
- Query SamudraManthanam for attestations
- Inline corpus preview (top 3–5 verses)
- Sense frequency statistics
- Display in result cards

---

## Phase 5: Scholarly Export & Sync (Weeks 10–11)

**TODO: Detailed tasks for publication readiness**
- Monthly batch sync from csl-orig
- DOI registration (Zenodo)
- Export formats (JSON, BibTeX, TEI XML)
- Provenance metadata (`csl_orig_commit_hash`, `correction_batch_date`)

---

## Testing & QA

### Phase 1–2b Acceptance Tests

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_lemma_lookup_mw():
    """Test MW lemma lookup."""
    resp = client.get('/api/lemma/bandh?encoding=iast')
    assert resp.status_code == 200
    data = resp.json()
    assert data['slp1'] == 'bandh'
    assert any(e['dict'] == 'mw' for e in data['entries'])

def test_form_lookup():
    """Test inflected form lookup."""
    resp = client.get('/api/lemma/form/bhagavān?encoding=iast')
    assert resp.status_code == 200
    data = resp.json()
    assert 'bhagavant-' in data['lemmas']

def test_encoding_toggle():
    """Test encoding conversion."""
    resp = client.get('/api/lemma/bandh?encoding=devanagari')
    assert resp.status_code == 200
    data = resp.json()
    assert data['encoding'] == 'devanagari'
    # TODO: verify actual transcoding

def test_scan_links():
    """Test scan link resolution."""
    resp = client.get('/api/scan/bandh')
    assert resp.status_code == 200
    data = resp.json()
    assert 'mw' in data['scans']
    assert 'url' in data['scans']['mw']

def test_cache_hit_rate():
    """Test cache performance."""
    # Query top 100 lemmas
    from app.services.cache_service import CacheService
    cache = CacheService()
    # Preload
    cache.preload_top_lemmas(count=5000)
    
    # Benchmark
    import random
    for _ in range(100):
        lemma = random.choice(['dharma', 'bandh', 'arjuna', ...])
        client.get(f'/api/lemma/{lemma}')
    
    stats = cache.stats()
    assert float(stats['hit_rate'].strip('%')) >= 80
```

**Time:** 4–6 hours (writing + running tests)  
**Acceptance:** ≥95% tests passing; latency ≤50ms for 80% of queries

---

## Deployment & Launch

### Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Build indices
python scripts/extract_page_metadata.py
python scripts/extract_dicts_to_json.py
python scripts/normalize_and_dedupe.py
python scripts/load_into_sqlite.py
python scripts/populate_scan_links.py

# Run server
python -m uvicorn app.main:app --reload

# Open browser
http://localhost:8000
```

### Production Deployment

```bash
# samskrtam.ru deployment
# 1. Build indices on samskrtam.ru server
# 2. Deploy FastAPI app to production
# 3. Configure Nginx as reverse proxy
# 4. Enable HTTPS
# 5. Set up monitoring + logging
```

---

## Summary: Phase 1–2b (MVP)

| Phase | Duration | Effort | Deliverables |
|-------|----------|--------|---|
| **Phase 1: Indexing** | 2 weeks | 15 person-days | unified_dict.db (300k entries) |
| **Phase 2: UI** | 2 weeks | 12 person-days | FastAPI + frontend + caching |
| **Phase 2b: Scans** | 1 week | 8 person-days | Scan links + Cologne integration |
| **Testing** | ongoing | 4 person-days | ≥95% tests passing |
| **Total MVP** | **5 weeks** | **39 person-days** | **Translator-ready kosha** |

**MVP Features:**
- ✅ Fast form lookup (bhagavān → bhagavant-) in <100ms
- ✅ Unified multi-dict view (MW + PWG + AP90)
- ✅ Encoding toggle (SLP1 ↔ IAST ↔ Devanagari)
- ✅ Grammar display toggle (minimal ↔ full)
- ✅ Scan links to Cologne server (vol., page clickable)
- ✅ Mobile-responsive UI

**Optional (Phases 3–5):**
- Etymology + KEWA (weeks 6–7)
- Corpus evidence (weeks 8–9)
- Scholarly export + sync (weeks 10–11)

---

_Dr. Mārcis Gasūns_
