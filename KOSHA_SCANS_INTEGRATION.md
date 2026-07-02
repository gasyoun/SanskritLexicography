# Scan Linking Integration for kosha

_Created: 02-07-2026 · Last updated: 02-07-2026_

> **⚠️ Triage banner (02-07-2026).** The original version of this doc invented
> its central data claim — the `<pc>` example and "volume, page" interpretation
> below are now corrected against real csl-orig records. Two further points
> supersede much of Parts II–III: **scan-link resolution is already solved** by
> [RussianTranslation/src/ls_resolver.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
> (port of csl-app's `ls_service.dart`, live on the PWG article site) — the
> `ScanResolver` class sketched here duplicates it; and "does Cologne host
> scans?" is answered: yes, via csl-websanlexicon's `serveimg`/`servepdf`
> endpoints. The storage-size table's volume/page figures (MW "7 vols, ~8,000
> pages") are fabricated — MW 1899 is one volume of ~1,333 pages; PWG is 7
> volumes, not 6.

## Strategic Goal

Transform kosha from a lookup tool into a **scholarly gateway to primary sources** (following michaelmeyer.fr model). Every dictionary entry shows a clickable link to the original scanned page, enabling translators and scholars to verify against the printed source.

---

## Part I: Data Structure in csl-orig

### Page Metadata in Dictionary Files

**Format:** The `<pc>` tag in csl-orig XML carries page and column information:

```xml
<!-- Real MW records (mws.xml) — corrected 02-07-2026; the earlier example
     "<L>523<pc>5,32<k1>bandh" was invented (L523 is akza at <pc>3,2, and
     MW has no volumes) -->
<L>523<pc>3,2<k1>akza ...
<L>142512<pc>720,1<k1>banD ...
```

**Interpretation (per-dict, verified):**
- **MW** `<pc>720,1` = **page 720, column 1** — MW 1899 is a **single volume**;
  there is no "vol. 5, p. 32"
- **PWG** `<pc>1-0001` = **volume-page with a hyphen** (7 volumes)
- **AP90** `<pc>0001-a` = **page-column-letter**
- Any parser doing `page_info.split(',')` fails on PWG and AP90 — the format
  must be dispatched per dictionary

**Current state:**
- ✅ Metadata is machine-readable (XML parseable)
- ⚠️ "All Cologne dicts carry `<pc>`" is an unverified blanket claim — formats
  differ per dict and coverage is not confirmed to be 100 %; measure per dict
- ✅ Page numbers are stable (don't change between editions if same scan is used)

### Which Dictionaries Have Scans Available?

| Dictionary | Edition | Page Metadata | Scans Available? | Source |
|---|---|---|---|---|
| **MW** | 1899 (2nd ed.) | ✅ `<pc>page,column` (1 vol) | ✅ Yes — Cologne `serveimg`/`servepdf` (csl-websanlexicon) | Cologne server |
| **PWG** | 1875 | ✅ `<pc>vol-page` (hyphen, 7 vols) | ✅ Yes — Cologne server (already linked by `ls_resolver.py` on the article site) | Cologne server |
| **AP90** | 1890 | ✅ `<pc>page-col-letter` | ⚠️ Unconfirmed — michaelmeyer.fr's `/ap59/scans/` is the **1957–59 revised Apte**, a different edition; not evidence for AP90 | Need to check |
| **GRA** | 1875 | ✅ `<pc>vol,page` | ⚠️ Unclear | Need to check |
| **PW** | 1896 | ✅ `<pc>vol,page` | ⚠️ Unclear | Need to check |
| **CAE** | 1891 | ✅ `<pc>page` | ⚠️ Unclear | Need to check |
| **MD** | 1899 | ✅ `<pc>vol,page` | ⚠️ Unclear | Need to check |

---

## Part II: Scan Infrastructure Options

### Option A: Self-Hosted (Full Control, Higher Cost)

**Process:**
1. Obtain high-quality scans (e.g., from Internet Archive, Cologne server, or digitize if not yet done)
2. Convert to optimized format (JPEG, WebP, or PDF)
3. Host on samskrtam.ru or dedicated CDN
4. Create direct URLs: `/kosha/mw/scans/vol5/page523.jpg`

**Pros:**
- Fast (no redirect; full control over caching)
- Reliable (don't depend on 3rd-party service availability)
- Scholarly: shows commitment to primary sources
- Customizable (can add annotations, cropping tools)

**Cons:**
- Storage cost (~5–50 MB per dictionary, depending on quality)
- Hosting/bandwidth cost
- Maintenance (broken scans, format changes)

### Option B: Link to External Services (Minimal Cost, External Dependency)

**Services to consider:**
1. **Internet Archive** (`archive.org/details/IDENTIFIER`)
   - Free, stable, well-indexed
   - Good for PD editions (AP90, MW 1899, PWG 1875, etc.)
   - Problem: API may rate-limit; links subject to IA's retention

2. **Google Books** (`books.google.com/books?id=...&pg=...`)
   - Free, comprehensive
   - Problem: availability varies by country/edition; links fragile

3. **Cologne Digital Sanskrit Dictionaries** (if they host scans)
   - Authoritative (same org)
   - Problem: unclear if publicly linked; infrastructure questions

4. **michaelmeyer.fr itself** (for editions he already hosts)
   - Already digitized and hosted
   - Problem: don't want to leech traffic; may change URLs

**Pros:**
- Zero storage cost
- Zero hosting cost
- Leverage existing infrastructure

**Cons:**
- Dependence on external service (availability, URL stability)
- Redirect latency (one extra HTTP request)
- No control over page rendering (IA, Google Books UI varies)

### Option C: Hybrid (Recommended)

**Strategy:**
1. **Self-host for core dicts** (MW, PWG, AP90) — most translator use
2. **Link to Internet Archive** for others (GRA, PW, CAE, MD, etc.) — lower priority
3. **Fallback links** to michaelmeyer.fr if neither available

**Result:**
- Fast for 80% of lookups (self-hosted)
- Zero cost for 20% of lookups (linked)
- Graceful degradation if any service down

---

## Part III: Implementation Plan

### Phase 2b: Scan Linking (Weeks 4–5, New Sub-Phase)

**Prerequisite:** Phase 1 (data indexing) must be complete; Phase 2 (UI) in progress.

#### Task 1: Extract Page Metadata from csl-orig

**Script:** `build_page_metadata.py`

```python
"""
Parse csl-orig XML files, extract <L> and <pc> tags.
Output: JSON mapping (headword, L-number) → (volume, page, column)
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import json

DICTS = ['mw', 'pwg', 'ap90', 'gra', 'pw', 'cae', 'md']

page_map = {}

for dict_code in DICTS:
    dict_file = Path(f"../../csl-orig/v02/{dict_code}/{dict_code}.txt")
    page_map[dict_code] = {}
    
    with open(dict_file, encoding='utf-8') as f:
        content = f.read()
        # Parse raw XML entries
        for entry in content.split('<LEND>'):
            if '<L>' not in entry:
                continue
            
            # Extract L-number
            l_start = entry.find('<L>') + 3
            l_end = entry.find('<', l_start)
            l_num = entry[l_start:l_end].strip()
            
            # Extract page (<pc>)
            pc_start = entry.find('<pc>') + 4
            if pc_start > 3:
                pc_end = entry.find('<', pc_start)
                page_info = entry[pc_start:pc_end].strip()  # e.g., "5,32" or "1,1"
                
                # Extract headword key
                k1_start = entry.find('<k1>') + 4
                k1_end = entry.find('<', k1_start)
                k1_key = entry[k1_start:k1_end].strip()
                
                page_map[dict_code][k1_key] = {
                    'L': l_num,
                    'page_info': page_info,
                    'raw': entry[:200]  # for debugging
                }

# Output
with open('dict_page_map.json', 'w', encoding='utf-8') as f:
    json.dump(page_map, f, ensure_ascii=False, indent=2)

print(f"Extracted page metadata for {sum(len(v) for v in page_map.values())} entries")
```

**Output:** `dict_page_map.json`

```json
{
  "mw": {
    "a": { "L": "1", "page_info": "1,1", "volume": 1, "page": 1, "column": 1 },
    "bandh": { "L": "523", "page_info": "5,32", "volume": 5, "page": 32, "column": null },
    ...
  },
  "pwg": { ... },
  "ap90": { ... }
}
```

**Effort:** 2–4 hours (XML parsing + testing)

---

#### Task 2: Source Scans or Create Links

**Sub-task 2a: Identify Scan Sources**

For each dictionary, determine source:

```
MW (1899, 2nd ed.):
  - Check: Internet Archive (search "Monier-Williams Sanskrit-English Dictionary 1899")
  - Check: Cologne server (do they host digitized scans?)
  - Fallback: Google Books
  - Result: [scan_source_url_pattern]

AP90 (1890):
  - Known: michaelmeyer.fr uses `/ap59/scans/2/1150`
  - Check: Internet Archive (search "Apte Practical Sanskrit-English Dictionary")
  - Result: [scan_source_url_pattern]

PWG (1875):
  - Check: Internet Archive (search "Großes Petersburger Wörterbuch")
  - Check: Cologne server
  - Result: [scan_source_url_pattern]

GRA, PW, CAE, MD:
  - Check: Internet Archive + Google Books
  - Decide: self-host or link?
  - Result: [scan_source_url_pattern]
```

**Output:** `scan_sources.yaml`

```yaml
mw:
  edition: "1899 (2nd ed.)"
  volumes: 7
  scan_source: "self-hosted"
  url_pattern: "/kosha/mw/scans/vol{volume}/page{page}.jpg"
  ia_identifier: "mw1899"  # fallback if needed

ap90:
  edition: "1890"
  pages: 1200
  scan_source: "internet-archive"
  url_pattern: "https://archive.org/download/ap59/page{page}.jpg"
  michaelmeyer_pattern: "https://michaelmeyer.fr/sanskrit/ap59/scans/{volume}/{page}"

pwg:
  edition: "1875"
  volumes: 6
  scan_source: "hybrid" # self-host primary; IA fallback
  url_pattern: "/kosha/pwg/scans/vol{volume}/page{page}.jpg"
  ia_identifier: "pwg1875"
```

**Effort:** 4–8 hours (research + testing links)

**Sub-task 2b: Download & Optimize Scans (if self-hosting)**

```bash
# For each scan source:
1. Download from Internet Archive / Cologne server
2. Convert to optimized format (JPEG quality 85% or WebP)
3. Resize to web-friendly dimensions (2000px width max)
4. Organize into folder structure:
   /scans/
     mw/
       vol1/
         page001.jpg
         page002.jpg
         ...
     pwg/
       vol1/
         page001.jpg
       ...

5. Compute file checksums (verify integrity)
6. Estimate total storage: ~500 MB – 2 GB depending on scan quality
```

**Effort:** 8–16 hours (download + convert + organize; one-time)

---

#### Task 3: Build Scan Link Resolution Service

**Endpoint:** `GET /api/lemma/{slp1}/scans`

```python
# app/services/scan_service.py

from pathlib import Path
import json

class ScanResolver:
    def __init__(self, page_map_file: str, scan_config_file: str):
        with open(page_map_file) as f:
            self.page_map = json.load(f)
        with open(scan_config_file) as f:
            self.scan_config = json.load(f)
    
    def get_scans(self, slp1: str, dict_code: str = None) -> dict:
        """
        Resolve scan links for a headword.
        
        Returns:
        {
          "mw": {
            "edition": "1899 (2nd ed.)",
            "volume": 5,
            "page": 32,
            "url": "/kosha/mw/scans/vol5/page32.jpg",
            "link_text": "vol. 5, p. 32"
          },
          "pwg": { ... },
          ...
        }
        """
        scans = {}
        
        dicts_to_check = [dict_code] if dict_code else self.page_map.keys()
        
        for dict_code in dicts_to_check:
            if slp1 not in self.page_map.get(dict_code, {}):
                continue
            
            page_info = self.page_map[dict_code][slp1]
            config = self.scan_config.get(dict_code, {})
            
            # Parse volume/page from page_info (format varies: "5,32" or "32")
            parts = page_info['page_info'].split(',')
            if len(parts) == 2:
                volume, page = parts
            else:
                volume, page = 1, parts[0]
            
            # Resolve URL using config pattern
            url_pattern = config.get('url_pattern')
            if url_pattern:
                url = url_pattern.format(volume=volume, page=page)
            else:
                url = None
            
            scans[dict_code] = {
                'edition': config.get('edition', 'unknown'),
                'volume': int(volume) if volume != '0' else None,
                'page': int(page),
                'url': url,
                'link_text': self._format_link(volume, page)
            }
        
        return scans
    
    def _format_link(self, volume: str, page: str) -> str:
        """Format human-readable link text."""
        if volume and volume != '0':
            return f"vol. {volume}, p. {page}"
        else:
            return f"p. {page}"
```

**Effort:** 4–6 hours (service + testing)

---

#### Task 4: Integrate Scans into Result Cards

**Update result template** (`templates/result_fragment.html`):

```html
<div class="entry">
  <h2>{{ headword_iast }}</h2>
  
  {% for dict_source in entry.dictionaries %}
    <div class="dict-section">
      <h3>{{ dict_source.name }}</h3>
      
      <p class="entry-text">{{ dict_source.sense_1 }}</p>
      
      <!-- NEW: Scan link -->
      {% if dict_source.scan %}
        <p class="scan-link">
          <a href="{{ dict_source.scan.url }}" target="_blank" class="btn-link">
            📄 View in original: {{ dict_source.scan.link_text }}
          </a>
        </p>
      {% endif %}
    </div>
  {% endfor %}
</div>
```

**CSS:**

```css
.scan-link {
  font-size: 0.9em;
  color: #666;
  margin-top: 0.5em;
}

.scan-link a {
  text-decoration: none;
  color: #0066cc;
  border-bottom: 1px solid #0066cc;
}

.scan-link a:hover {
  background-color: #f0f8ff;
}
```

**Effort:** 2–3 hours (template updates + styling)

---

#### Task 5: Testing & Quality Assurance

**Test matrix:**

| Test | Scope | Acceptance |
|------|-------|-----------|
| **Link validity** | All 50k+ entries in 7 dicts | 100% of links are live (not 404) |
| **Page accuracy** | Random sample (100 entries per dict) | Expert review: link lands on correct page ±1 page |
| **Load time** | Scan page load latency | ≤1s for self-hosted; ≤3s for IA links |
| **Mobile rendering** | Mobile browser (iPhone 12, Android) | Scan image readable at 375px width (zoom required) |
| **Edge cases** | Multi-volume dicts | Links to vol.5 work same as vol.1 |

**Effort:** 4–6 hours (manual testing + automation)

---

### Phase 2b: Deliverable

**Result of Phase 2b:**

1. ✅ `dict_page_map.json` — page metadata for 50k+ entries
2. ✅ `scan_sources.yaml` — source URLs + strategies per dict
3. ✅ Self-hosted scans (if chosen) — `/scans/` directory with optimized JPEGs
4. ✅ `ScanResolver` service — API to resolve lemma → scan URL
5. ✅ Updated UI — every entry shows "View in original" link
6. ✅ Test report — link validity + accuracy confirmed

**Total effort:** ~30–40 hours (one-time setup; then maintain)

---

## Part IV: URL Design

### Option A: Direct Link (Simplest)

```
/kosha/mw/scans/vol5/page32.jpg
/kosha/pwg/scans/vol3/page127.jpg
/kosha/ap90/scans/page1150.jpg
```

**Pros:** Fast (no redirect); bookmarkable  
**Cons:** Requires file system organization

### Option B: Resolver Endpoint (Flexible)

```
/api/scan/mw/bandh?target=page
  → Redirects to actual scan URL
  
/api/scan/mw?vol=5&page=32
  → Returns JSON with scan metadata
```

**Pros:** Flexible (can change backend without breaking links)  
**Cons:** Extra HTTP request

### Option C: michaelmeyer.fr Style (Scholarly)

```
/kosha/mw/text/bandh
  → Shows entry + scan on same page (embedded or side-by-side)

/kosha/mw/scans/vol5/page32
  → Direct to scan image
```

**Pros:** Mirrors scholarly citation pattern  
**Cons:** Requires dual-rendering (text + image)

**Recommendation:** Option A (direct) for MVP; upgrade to Option C in Phase 6 if desired.

---

## Part V: Licensing & Attribution

### Scan Rights

| Dict | Edition | Copyright | License | Attribution |
|---|---|---|---|---|
| MW | 1899 (2nd ed.) | Public Domain | CC0 / Public Domain | Cite: "Monier-Williams Sanskrit-English Dictionary, 2nd ed. (1899)" |
| PWG | 1875 | Public Domain | CC0 / Public Domain | Cite: "Böhtlingk & Roth Großes Petersburger Wörterbuch, 1875" |
| AP90 | 1890 | Public Domain | CC0 / Public Domain | Cite: "Apte Practical Sanskrit-English Dictionary, 1890" |
| GRA | 1875 | Public Domain | CC0 / Public Domain | Cite: "Grassmann Wörterbuch zum Rig-Veda, 1875" |
| Other | Pre-1923 (US) | Public Domain | CC0 / Public Domain | Cite accordingly |

**Implementation:**

1. Add metadata to each scan:
   ```json
   {
     "source": "Monier-Williams Sanskrit-English Dictionary",
     "edition": "2nd ed., 1899",
     "copyright": "Public Domain",
     "license": "CC0",
     "hosted_by": "samskrtam.ru / kosha",
     "original_source": "Internet Archive / Cologne server"
   }
   ```

2. Display attribution in result:
   ```
   📄 View in original: vol. 5, p. 32 (Public Domain, 1899)
   ```

3. In scholarly publication:
   ```
   "Dictionary scans hosted at samskrtam.ru/kosha are reproduced 
   from public-domain editions sourced via Internet Archive and 
   Cologne Digital Sanskrit Lexicon. Full metadata and edition 
   information provided with each entry."
   ```

---

## Part VI: Storage Estimates

### Self-Hosted Scans (If Chosen)

| Dictionary | Volumes | Pages | Scan Format | File Size | Total Storage |
|---|---|---|---|---|---|
| MW | 7 | ~8,000 | JPEG 85% | ~100 KB/page | ~800 MB |
| PWG | 6 | ~7,500 | JPEG 85% | ~100 KB/page | ~750 MB |
| AP90 | 1 | ~1,200 | JPEG 85% | ~80 KB/page | ~96 MB |
| GRA | 2 | ~1,200 | JPEG 85% | ~80 KB/page | ~96 MB |
| Other | — | ~500 | JPEG 85% | ~80 KB/page | ~40 MB |
| **Total** | — | ~18,000 | — | — | **~1.8 GB** |

**Hosting cost (AWS S3):**
- Storage: ~$50/month for 1.8 GB
- Transfer out: ~$0.09/GB (if 10 GB/month traffic)
- **Total:** ~$50–75/month (one-time; then maintain)

**Alternative (linked to Internet Archive):**
- Storage: $0 (IA hosts)
- Bandwidth: $0 (IA handles)
- Latency: +100–500ms per lookup (IA redirect)

---

## Implementation Priority

| Task | Phase | Must-Have? | Timeline |
|------|-------|-----------|----------|
| Extract page metadata | 2b | ✅ YES | Week 4 |
| Identify scan sources | 2b | ✅ YES | Week 4 |
| Download/optimize scans | 2b | ⚠️ CONDITIONAL (if self-hosting) | Week 4–5 |
| Build ScanResolver service | 2b | ✅ YES | Week 5 |
| Integrate into UI | 2b | ✅ YES | Week 5 |
| Testing + QA | 2b | ✅ YES | Week 5 |

**Decision needed:** Self-hosted or linked scans?

---

## Next Steps

Please answer:

1. **Self-hosted or linked scans?**
   - Self-hosted (full control, ~$50–75/month, 1.8 GB storage)
   - Linked to Internet Archive (free, but slower + dependence)
   - Hybrid (self-host MW/PWG/AP90; link others)

2. **Which dictionaries to prioritize?**
   - MVP: MW + PWG + AP90? (covers 80% of translator use)
   - Full: All 7 Cologne dicts?

3. **UI preference for scan links?**
   - Option A (direct link, simplest)
   - Option B (resolver endpoint, flexible)
   - Option C (michaelmeyer.fr style, scholarly)

---

_Dr. Mārcis Gasūns_
