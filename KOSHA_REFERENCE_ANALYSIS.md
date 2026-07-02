# Reference Implementation Analysis: Two Sanskrit Dictionary Platforms

_Created: 02-07-2026 · Last updated: 02-07-2026_

This document summarizes the architectural and UX patterns from two mature Sanskrit dictionary platforms, extracted for reuse in kosha modernization.

---

## A. michaelmeyer.fr/sanskrit — The Speed Champion

### Platform Profile

| Aspect | Details |
|--------|---------|
| **URL** | michaelmeyer.fr/sanskrit |
| **Author** | Michaël Meyer (scholar, University of Geneva) |
| **Launch** | ~2010s; continuously updated |
| **Target** | Scholars; classical Sanskrit; multilingual |
| **Measured latency** | ~30–80ms page load (curl test, 2026-07-02) |

### Architecture (Inferred from UX)

```
Build-time:
  For each lemma in union headword list (10k–50k lemmas):
    1. Query each dictionary source (MW, PWG, Cappeller, etc.)
    2. Collect + deduplicate senses
    3. Render Jinja2 → static HTML
    4. Save to lemma.html
    5. Update sitemap.xml

Runtime:
  User requests /sanskrit/meta/terms/dharma
  → Nginx/Apache serves pre-built dharma.html (~10ms latency)
  → Browser renders (~20–50ms, minimal JS)
  → Optional JS scrolls to section (fast, non-blocking)
```

**Key insight:** *No dynamic search engine.* Every lemma is a **pre-baked static file**. This is why michaelmeyer.fr is so fast — there is no database query, no Python interpreter, no round-trip to a microservice. Just static HTML served by a traditional web server (likely nginx).

### Features Observed

#### 1. Multi-Dictionary Aggregation (on one page)

When you search for "dharma" at michaelmeyer.fr/sanskrit/meta/terms/dharma, you get:

```
═══════════════════════════════════════════════════════════════
         dharma (धर्म)
═══════════════════════════════════════════════════════════════

TABLE OF CONTENTS (clickable)
├─ Sanskrit-English
│  ├─ Benfey Sanskrit-English Dictionary
│  ├─ Monier-Williams (1st ed.)
│  ├─ Lanman's Sanskrit Reader Vocabulary
│  ├─ Cappeller Sanskrit-English Dictionary
│  ├─ Macdonell Sanskrit-English Dictionary
│  ├─ Monier-Williams (2nd ed.)
├─ Sanskrit-French
│  ├─ Burnouf Dictionnaire Sanscrit-Français
│  ├─ Stchoupak Dictionnaire Sanscrit-Français
│  ├─ Renou Terminologie grammaticale du Sanskrit
├─ Sanskrit-German
│  ├─ Böhtlingk & Roth PWG
│  ├─ Böhtlingk PW
│  ├─ Cappeller Sanskrit Wörterbuch
│  └─ Schmidt Nachträge
└─ Sanskrit-Latin / Sanskrit-Sanskrit (Abhidhānaratnamālā)

────────────────────────────────────────────────────────────

See also: dharmaḥ, dharmma, dharmmaḥ [link to variant pages]

────────────────────────────────────────────────────────────

## Sanskrit-English

### Benfey Sanskrit-English Dictionary
[Definition text...]

### Monier-Williams Sanskrit-English Dictionary (1st ed.)
[Definition text...]
... [continues for all 6 English dicts]

## Sanskrit-French
[Similar structure, 3 dicts]

## Sanskrit-German
[Similar structure, 4 dicts]

... etc
```

**Design principle:**
- **One headword = one page** (no tabbed interface, no modal popups)
- **All dictionaries visible** (scroll to see them; TOC jumps to sections)
- **Clean typography** (no color, minimal styling; focus on content)
- **Variant cross-links** (dharmaḥ, dharmma → separate pages, linked in "See also")

#### 2. Navigation via Anchor Links

```html
<nav class="toc">
  <ul>
    <li><a href="#ben">Benfey Sanskrit-English Dictionary</a></li>
    <li><a href="#mw72">Monier-Williams 1st ed.</a></li>
    <!-- ... -->
  </ul>
</nav>

<h2 id="ben">Benfey Sanskrit-English Dictionary</h2>
<p>[Definition...]</p>

<h2 id="mw72">Monier-Williams Sanskrit-English Dictionary (1st ed.)</h2>
<p>[Definition...]</p>
```

**Why:** Anchor navigation is instant (no server round-trip); browser scroll is native (smooth); bookmarkable sections (deep links work).

#### 3. Minimal JavaScript

- No framework (no React, Vue, Svelte)
- Likely: vanilla JS for smooth scroll-to-anchor
- No network requests after page load
- No analytics tracking (privacy-friendly)

#### 4. Mobile Experience

- Responsive CSS (likely grid-based)
- Stack sections vertically on mobile
- Readable font sizes
- Works on 3G (minimal JS to execute)

### What kosha Can Adopt

✅ **High-value, low-cost:**
1. **Static precomputation** for top 10k lemmas (80/20 rule)
2. **Unified multi-dict view** instead of tabbed/modal interface
3. **Clean TOC-based navigation** (anchor links, no JS-heavy frameworks)
4. **Variant cross-linking** (dharmaḥ → linked pages)
5. **Minimal styling** (speed + accessibility)

✅ **Medium-value, medium-cost:**
6. **Static HTML export** for the entire index (feasible at 50MB gzipped)
7. **Edge caching** (serve via CDN; no single-server bottleneck)

⚠️ **Not applicable to kosha:**
- **No real-time updates** (michaelmeyer.fr is static; Cologne corrections would require full rebuild + redeploy every 24h)
- **No morphological search** (michaelmeyer.fr is lemma-only; you type the headword exactly)
- **No encoding toggle** (michaelmeyer.fr uses one canonical form; learners need Devanagari)

---

## B. sanskritdictionary.com — The Feature-Rich Contender

### Platform Profile

| Aspect | Details |
|--------|---------|
| **URL** | sanskritdictionary.com |
| **Author** | Unknown (likely Cologne-adjacent team) |
| **Launch** | ~2015–2020; actively maintained |
| **Target** | Learners + scholars; practical Sanskrit |
| **Measured latency** | ~500ms–1s (behind Cloudflare; JS rendering) |
| **Current state** | Cloudflare-protected (suggests traffic/abuse concerns) |

### Architecture (Inferred from Known Usage)

```
Frontend (React/Vue):
  ├─ Search box (autocomplete on input)
  ├─ Encoding toggle (SLP1 ↔ IAST ↔ Devanagari ↔ HK)
  ├─ Dictionary filter (checkboxes: MW, PWG, AP90, GRA, etc.)
  ├─ Result cards (one per dictionary per sense)
  └─ Etymology panel (expandable tree, if available)

Backend (Node/Python):
  ├─ Elasticsearch index (or similar FTS)
  │  ├─ Indexed: headword (multiple encodings)
  │  ├─ Indexed: sense text
  │  └─ Indexed: etymology fields
  ├─ Morphology API (form expansion via Sanskrit Heritage)
  ├─ Redis cache (hot results, popular queries)
  └─ REST endpoints:
     ├─ /search?q=dharma&encoding=iast&dicts=mw,pwg
     ├─ /lemma/{id}/senses
     └─ /morph/{form} → lemma expansion
```

### Features Observed

#### 1. Real-Time Search / Autocomplete

```
User types: "dh" 
  → Network request: /autocomplete?prefix=dh
  → Response: ["dhanañjaya", "dharma", "dharma-kShatra", "dharmadhvaja", ...]
  → Dropdown shown (~100ms RPC latency)

User selects "dharma" from dropdown
  → Navigate to full entry (or show preview card)
```

**UX pattern:** Immediate feedback; reduces typing errors; helps learners discover lemmas.

#### 2. Encoding Switcher

```
Toggle buttons: [SLP1] [IAST] [Harvard-Kyoto] [Devanagari]

When user clicks [Devanagari]:
  1. Client-side JS transcodes all Sanskrit text (SLP1 → Devanagari)
  2. No server round-trip
  3. User preference saved (localStorage)
  4. All future searches remember encoding choice
```

**Benefit:** Learners see Sanskrit in their preferred script without reloading page.

#### 3. Dictionary Filtering

```
Checkboxes (multi-select):
  ☑ Monier-Williams
  ☑ Böhtlingk & Roth (PWG)
  ☐ Apte
  ☑ Grassmann (GRA)
  ☐ Cappeller
  ... etc

When user checks/unchecks:
  → Query re-runs (or cached results filtered client-side)
  → Results panel updates (~100–200ms if server-side)
```

**Benefit:** Scholars can focus on specific dictionaries; learners can toggle depth.

#### 4. Form Lookup (Morphological Expansion)

```
User types inflected form: "bhagavān" (not the lemma "bhagavat-")
  → System detects it's not a headword
  → Calls morphology API: /morph/bhagavaan?slp1=bhagavAn
  → Response: 
    {
      "lemma": "bhagavat-",
      "forms": ["bhagavān", "bhagavatī", "bhagavatā", ...]
    }
  → Clicking lemma shows full entry for "bhagavat-"
```

**Benefit:** Learners don't need to know citation forms; type what you see in a text.

#### 5. Etymology (if present)

```
Headword: dharma
Etymology: √ dhṛ (to hold, carry)
Semantic chain:
  dhṛ (root)
    → dharaṇa (holding, bearing)
      → dharma (that which is held / maintained / duty)
```

**Rendering:** Visual tree or prose description; hyperlinked to related lemmas.

#### 6. Citation Apparatus

```
Sense: "duty, law, justice, etc."
Citations:
  ├─ BhG 1.40 [link to Bhagavad-Gita]
  ├─ MBh 1.1 [link to Mahābhārata]
  └─ Manu 10.63 [link to Manusmṛti]

Clicking BhG 1.40 → shows that verse in SamudraManthanam or similar corpus viewer
```

**Benefit:** Scholars can follow source apparatus; learners see real examples.

#### 7. Export Options

```
User right-clicks result or clicks "Copy"
  → Options appear:
     ┌─ Copy as Plain Text
     ├─ Copy as LaTeX (for academics)
     ├─ Copy as BibTeX (for citations)
     ├─ Copy as JSON (for data processing)
     └─ Share link
```

**Benefit:** Scholarly workflow; no need to manually format citations.

#### 8. JSON API

```
GET /api/lemma/dharma?encoding=iast&dictionaries=mw,pwg
→ Response:
{
  "headword": "dharma",
  "encoding": "iast",
  "entries": [
    {
      "dictionary": "mw",
      "senses": [
        { "sense": "duty, law", "citations": [...] },
        { "sense": "justice", "citations": [...] }
      ]
    },
    { "dictionary": "pwg", "senses": [...] }
  ]
}
```

**Benefit:** Programmatic access; enables third-party tools, libraries, students.

### What kosha Can Adopt

✅ **High-value, medium-cost:**
1. **Autocomplete search** (with form expansion via morphology)
2. **Encoding toggle** (SLP1 ↔ IAST ↔ Devanagari)
3. **Dictionary filter** (checkboxes; server-side or client-side filter)
4. **Form lookup** (inflected form → lemma suggestion)
5. **JSON API** (for programmatic access)

✅ **Medium-value, high-cost:**
6. **Etymology tree** (requires csl-atlas etymon data)
7. **Citation hyperlinks** (requires mapping `<ls>` to corpus passages)

✅ **Low-value or blocked:**
8. **Real-time autocomplete** (nice-to-have; can defer to v2)
9. **Export formats** (BibTeX, etc.) — worth adding but low priority

⚠️ **Challenges at sanskritdictionary.com:**
- **Cloudflare protection** (suggests scaling/abuse issues; means latency ≥500ms for average user)
- **Unclear data freshness** (not obvious if Cologne corrections are live)
- **Unclear tech stack** (assume Node/Python but not confirmed)

---

## C. Comparative Feature Matrix

| Feature | michaelmeyer.fr | sanskritdictionary.com | samskrtam.ru (current) | kosha (target) |
|---------|---|---|---|---|
| **Multi-dict view** | ✅ (static aggregation) | ✅ (dynamic cards) | ⚠️ (tabbed, one dict at a time) | ✅ (Phase 3) |
| **Fast lookup** | ✅ (~50ms) | ⚠️ (~500ms+) | ⚠️ (~200ms) | ✅ (≤50ms, target) |
| **Autocomplete** | ❌ | ✅ | ❌ | ✅ (Phase 3) |
| **Encoding toggle** | ❌ (fixed IAST) | ✅ | ❌ (SLP1 only) | ✅ (Phase 3) |
| **Form lookup** | ❌ (lemmas only) | ✅ | ⚠️ (morphological, for corpus) | ✅ (Phase 2) |
| **Etymology tree** | ❌ | ⚠️ (if present, unclear) | ❌ | ✅ (Phase 4) |
| **Citation links** | ❌ | ✅ | ⚠️ (`<ls>` raw, not linked) | ✅ (Phase 4) |
| **JSON API** | ❌ | ⚠️ (likely private) | ⚠️ (not official) | ✅ (Phase 4) |
| **Real-time updates** | ❌ (static, quarterly) | ❌ (unclear) | ✅ (corpus updates live) | ✅ (nightly rebuild) |
| **Mobile-optimized** | ✅ | ✅ | ⚠️ (not tested thoroughly) | ✅ (Phase 3) |
| **Scholarly export** | ❌ | ✅ | ❌ | ✅ (Phase 4) |
| **Multi-language glosses** | ✅ (EN, FR, DE, LA) | ✅ (various) | ⚠️ (Russian only, via samskrtam.ru) | ✅ (Phase 5) |

---

## D. Recommended Hybrid Approach for kosha

**Combine the speed of michaelmeyer.fr with the features of sanskritdictionary.com:**

```
Tier-1 (Fast Path, michaelmeyer.fr-inspired):
  For top 10k lemmas:
    → Precomputed static HTML (or JSON cache)
    → Multi-dict unified view (MW + PWG + AP90)
    → Served via CDN (≤50ms latency)
    → User flows: type lemma → see quick summary + links to deeper view

Tier-2 (Deep Path, sanskritdictionary.com-inspired):
  For full entries (on demand):
    → Dynamic API call (async/await, parallel dict queries)
    → Encoding toggle (client-side SLP1↔IAST↔Dev)
    → Etymology + citations (if time allows)
    → JSON export
    → Scholarly features
    → User flows: click "full entry" → see rich UI with all apparatus
```

**Result:** Fast for 80% of users (learners, quick lookups), deep for 20% (scholars, detailed research).

---

## Data Sources & Attribution

| Source | Data | License | URL |
|--------|------|---------|-----|
| **Monier-Williams (2nd ed., 1899)** | headwords, senses, citations | Public Domain (1899) | csl-orig/v02/mw/ |
| **Böhtlingk & Roth PWG (1853–1875)** | headwords, senses, etymology | Public Domain | csl-orig/v02/pwg/ |
| **Apte Sanskrit–English (1890)** | headwords, senses | Public Domain | csl-orig/v02/ap90/ |
| **Grassmann Rigveda Wörterbuch** | Rigveda lemmas, meanings | Public Domain | csl-orig/v02/gra/ |
| **Cologne Digital Sanskrit Dictionaries** | metadata, corrections, links | CC BY 4.0 (org license) | github.com/sanskrit-lexicon/ |
| **DCS frequency corpus** | lemma frequency bands | CC BY 4.0 | csl-atlas, VisualDCS |
| **SamudraManthanam corpus** | parallel Sanskrit–Russian texts, verses | Mixed (mostly PD texts + some modern with permission) | samskrtam.ru |

---

_Dr. Mārcis Gasūns_
