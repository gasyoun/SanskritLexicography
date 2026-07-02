# Translator-First Specification for kosha Lookup

_Created: 02-07-2026 · Last updated: 02-07-2026_

> **⚠️ Triage banner (02-07-2026).** Defects on record: this doc "locks"
> decisions and then asks six open questions about them (Q1–Q6, never
> answered — see
> [KOSHA_DECISIONS_NEEDED.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_DECISIONS_NEEDED.md)
> for the answers now recorded); its cadence lock ("real-time if no perf
> penalty") contradicts the other docs; its timeline (MVP 4 wks / full 10 wks,
> phases shifted one week early) is off-by-one vs every sibling doc; the ✅
> glyphs on phase tasks mark unbuilt work; and the five companion docs promised
> at the end were never generated. Superseded on architecture by the
> meta-decisions in
> [KOSHA_FOLDER_SETUP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_FOLDER_SETUP.md).
> The translator-workflow analysis itself (the core of this doc) remains valid.

## Your Decisions (Locked)

| Decision | Your Choice | Implication |
|----------|---|---|
| **Performance target** | Real-time search speed (sub-50ms); monthly freshness OK | Precomputation + caching critical; can rebuild nightly |
| **Data scope** | All Cologne dicts + Sanskrit-Russian dicts + KEWA + morphological parsing + corpus attestation | Larger index (~500MB); wider coverage |
| **Ownership** | Public service → scholarly publication | CC BY 4.0 licensing; full provenance tracking; DOI-ready |
| **Update cadence** | Real-time sync if no perf penalty, else periodic | Try async rebuild on csl-orig webhook; fallback to nightly cron |
| **Primary audience** | **Translators > Learners > Scholars** | Comparative glosses, fast form lookup, evidence trails |

---

## Translator Workflow (Your Primary Use Case)

**Scenario:** Translating a Sanskrit text (e.g., Bhagavad-Gita passage)

```
Translator reads:    bhagavān uvāca
                     ↓ (What does bhagavān mean here? Is it a name or adjective?)
                     
Action 1: Type "bhagavān" into kosha
  ↓
kosha recognizes: not a lemma; morphologically a nom.sg. m. of "bhagavat-"
  ↓
Shows: 
  ┌─────────────────────────────────────────────┐
  │ bhagavant- (भगवत्) [nom.sg.m: bhagavān]     │
  │                                              │
  │ MW: "blessed, fortunate, adorable; lord"   │
  │ PWG: "der Glückselige, Gesegnete; Herr"    │
  │ AP90: "adorable, blessed; lord"            │
  │ RU (Kochergina): "блаженный, владыка"      │
  │                                              │
  │ Etymology: √ bhag- (to be happy, share)    │
  │            bhag-avant- = possessing fortune│
  │                                              │
  │ Corpus: BhG 1.24, 2.1, ... (28 verses)     │
  │                                              │
  │ Grammar: m. -ant stem; nom.sg. -ān         │
  │          nominative (subject function)     │
  └─────────────────────────────────────────────┘

Action 2: Translator chooses best gloss for their target language
  ↓
  [If translating to English] pick "adorable" or "lord"?
  [If translating to Russian] use "владыка" from Kochergina
  [If translating to German] use PWG German
  
Action 3: (Optional) Translator clicks "corpus" to see how other translators rendered it
  ↓
  Shows BhG 1.24 in parallel Sanskrit–Russian translation
  ↓
  Builds confidence in choice
```

**Key friction points kosha should solve:**
1. ✅ **Fast form lookup** (type inflected form, get lemma instantly)
2. ✅ **Comparative glosses** (see all dict translations side-by-side, not tabbed)
3. ✅ **Target-language glosses** (Sanskrit-Russian, Sanskrit-German, Sanskrit-French available immediately)
4. ✅ **Morphological context** (show case/number/gender, so translator knows function)
5. ✅ **Corpus evidence** (how many other translators used this word? what senses dominate?)
6. ✅ **Etymology clarity** (is this a name, a title, or a common word? etymology helps)
7. ⚠️ **Speed** (translator workflow is real-time; if lookup > 200ms, they alt+tab to another dict)

---

## Clarifying Questions for Translator-Specific Features

### Q1: Multi-Language Comparative Glosses

**Your target languages for translation:**
- English? (always)
- Russian? (yes, SamudraManthanam has this)
- German? (PWG covers this; useful?)
- French? (Burnouf/Stchoupak/Renou available in csl-orig?)
- Other? (Chinese, Japanese, Hindi?)

**Implication:** Affects which dicts we index and render.

**Recommended:** English (primary) + Russian (your strength) + German (PWG is deep) for MVP. French + others in Phase 2.

---

### Q2: Morphological Grammar Display

**What grammar info should be shown in results?**

Option A (Minimal):
```
bhagavān ← bhagavant- [nominative singular masculine]
Meaning: adorable, lord
```

Option B (Medium):
```
bhagavān ← bhagavant- [nominative singular masculine, -ant- stem adjective]
Grammatical function: subject, predicate adjective, vocative when addressing
Meaning: adorable, lord
```

Option C (Maximum):
```
bhagavān ← bhagavant- [nom.sg.m., -ant- stem]
Stem form: bhagavat-
Inflection class: -ant- adjective (a-series stem, m./n./f.)
Strong stem: bhagavat- | Weak stem: bhagavat-
This form (nominative): subject or predicate nominal; cannot be used attributively (accusative would be bhagavantam)
Related forms: bhagavantī (f.sg.nom), bhagavantau (m.du.nom), bhagavantaḥ (m.pl.nom)
```

**Your preference?** A / B / C?

---

### Q3: Corpus Attestation Detail

**Current samskrtam.ru shows verse references.** For translators, how much context?

Option A (Link only):
```
Corpus: BhG 1.24, 2.1, 3.40, MBh 1.1, 5.20 (28 verses total)
[Click link → view in SamudraManthanam]
```

Option B (Inline preview):
```
Corpus instances (top 3):
  1. BhG 1.24: "Arjuna uvāca bhagavān aham..."
     Russian: "Арджуна сказал: Владыка, я..."
  2. BhG 2.1: "Sañjaya uvāca tataḥ bhagavān..."
     Russian: "Санджая сказал: Затем владыка..."
  3. MBh 1.1: "...bhagavantam ṛṣiḥ..."
     Russian: "...блаженного мудреца..."
```

Option C (Statistics):
```
Corpus: 28 attestations across 8 texts
  BhG: 15 (most common)
  MBh: 8
  Ramayan: 3
  Other: 2
  
Top senses (by frequency in corpus):
  "lord" / "adorable" : 18 uses (64%)
  "blessed" : 7 uses (25%)
  [uncommon senses] : 3 uses (11%)
```

**Your preference?** A / B / C?

---

### Q4: Russian Dictionary Priority

**Which Sanskrit-Russian dicts are most important?**

Current in SamudraManthanam:
- ✅ Kochergina (29k entries, modern, authoritative)
- ✅ Kossovich (13.5k entries, PD 1854, archaic style)
- ✅ Knauer (3.3k entries, educational, simple)
- ✅ Frish (8k entries, PD 1956, literary)
- ✅ Smirnov (3.5k entries, specialized, symphonic)

Plus your RussianTranslation work:
- ✅ mw_ru (287k AI-translated cards from MW, in progress)

**For MVP kosha:**
- Kochergina only? (most authoritative, covers 90% of needs)
- Kochergina + mw_ru? (more coverage, but mw_ru is machine-translated — confidence?)
- All five + mw_ru? (comprehensive, but may overwhelm)

**Your preference?**

---

### Q5: Real-Time vs Monthly Sync: Which Dicts Change Fastest?

**Cologne correction frequency varies by dict:**
- MW: minor corrections (~10/month estimated)
- PWG: rare corrections (~2/month)
- AP90: rare corrections (~1/month)
- GRA: very rare corrections (~1/quarter)
- Sanskrit-Russian: often no corrections (PD dicts frozen; mw_ru is static output)

**Question:** Do translators *need* daily refreshes, or is monthly sufficient?

If translators are working on stable texts (published editions), monthly is likely fine. If translating works-in-progress where you're applying new Cologne corrections weekly, real-time might matter.

**Your answer:** Monthly batches sufficient, or need faster refresh?

---

### Q6: Scholarly Publication Angle

**When you publish kosha as a scholarly resource:**
- Will you cite all Cologne dicts in a methods section?
- Will kosha output include persistent identifiers (lemma URIs, entry DOIs)?
- Should each result card show provenance (which dict version, which correction batch)?

**Implication:** Affects metadata schema + export format.

**Recommended:** Yes to all three (makes kosha a *citable resource*, not just a lookup tool).

---

## Translator-Optimized Roadmap (Revised)

Given your decisions above, here's the refined roadmap:

### Phase 1: Foundation (Weeks 1–2, Translator-Optimized)

**Goal:** Fast form lookup for translators

**Tasks:**
1. ✅ Merge all Cologne dicts into single `unified_dict.db` (by SLP1 key + homonym)
2. ✅ Add morphological expansion (form → lemmas)
3. ✅ Add Russian dict integration (Kochergina primary; mw_ru secondary)
4. ✅ Build FTS5 index (on headwords + senses, all languages)
5. ✅ Measure baseline latency (target: ≤100ms for cache miss)

**Deliverable:** `unified_dict.db` + morphological index; API returns translations in <100ms

---

### Phase 2: Translator UI (Weeks 3–4)

**Goal:** Comparative glosses, fast switching

**Tasks:**
1. ✅ Build unified entry view (MW + PWG + AP90 + Russian side-by-side, not tabbed)
2. ✅ Add morphological grammar display (case/number/gender, stem info)
3. ✅ Encoding toggle (SLP1 ↔ IAST ↔ Devanagari)
4. ✅ Quick corpus link (BhG 2.1, etc. → clickable to SamudraManthanam)
5. ✅ Pronunciation guide (optional; IPA + audio if available)

**Deliverable:** Modern UI optimized for translator workflow

---

### Phase 3: Etymology & KEWA (Weeks 5–6)

**Goal:** Deep etymology for choice confidence

**Tasks:**
1. ✅ Integrate KEWA etymon data (roots, cognate families)
2. ✅ Link headwords to roots (√ bhag- → bhagavant- → related words)
3. ✅ Show semantic chains ("fortune" → "lord" via etymology)
4. ✅ Annotate source (Cologne etymology vs KEWA vs modern scholarship)

**Deliverable:** Etymology tree visible in entry view

---

### Phase 4: Corpus Deep Dive (Weeks 7–8)

**Goal:** Evidence for translation choices

**Tasks:**
1. ✅ Inline corpus preview (top 3–5 verse examples with Russian translations)
2. ✅ Sense frequency (show which senses dominate in corpus)
3. ✅ Related words in context (translations of synonyms in same passages)
4. ✅ Optional: export to CAT tool format (for professional translators using Trados/MemoQ)

**Deliverable:** Corpus-backed evidence layer

---

### Phase 5: Scholarly Export & Sync (Weeks 9–10)

**Goal:** Publication-ready; real-time or monthly sync

**Tasks:**
1. ✅ Real-time csl-orig sync (GitHub webhook → rebuild index on changes)
2. ✅ Fallback to nightly cron if webhook unreliable
3. ✅ DOI registration (Zenodo deposit for data; persistent links)
4. ✅ Export formats (JSON, TSV, BibTeX, TEI XML)
5. ✅ Provenance tracking (every entry shows csl-orig version, correction batch date)

**Deliverable:** Production-ready; publication-ready; transparent provenance

---

## Implementation Priority (Translator-First)

| Phase | MVP? | Translator Value | Effort | Timeline |
|-------|------|---|---|---|
| 1. Core indexing + form lookup | ✅ YES | 🔴 Critical (this is 80% of translator workflow) | Medium | Week 2 |
| 2. Comparative UI | ✅ YES | 🔴 Critical (translators need fast switching) | Medium | Week 4 |
| 3. Etymology + KEWA | ⚠️ Phase 2 | 🟡 Nice-to-have (builds confidence) | Medium | Week 6 |
| 4. Corpus evidence | ⚠️ Phase 2 | 🟡 Nice-to-have (context helps) | High | Week 8 |
| 5. Scholarly export | ⚠️ Phase 3 | 🟢 Low (not translator workflow) | Medium | Week 10 |

**MVP = Phases 1–2 (4 weeks)**  
**Full = Phases 1–5 (10 weeks)**

---

## Storage & Performance (Translator-Optimized)

| Component | Size | Latency (uncached) | Latency (cached) |
|-----------|------|---|---|
| All Cologne dicts + Russian | ~300 MB | ≤200ms (FTS5) | ≤10ms (RAM cache) |
| Morphological index | ~50 MB | ≤50ms | ≤5ms |
| Precomputed top-5k entries | ~100 MB | n/a | ≤50ms |
| **Total on disk** | ~450 MB | — | — |
| **RAM cache (hot)** | ~150 MB | — | ≤20ms p99 |

**Translator workflow latency target:** ≤50ms (cache hit) or ≤200ms (cache miss)  
**Acceptable?** (Most translators can wait 200ms; anything >500ms → alt+tab to alternative)

---

## Next Steps

Please answer the 6 clarifying questions above (Q1–Q6). Once I have your answers, I'll generate:

1. **TRANSLATOR_IMPLEMENTATION_PLAN.md** — task-by-task breakdown
2. **KOSHA_SCHEMA.md** — SQLite + JSON schema for all data
3. **KOSHA_API_SPEC.md** — OpenAPI definition (REST endpoints)
4. **KOSHA_UI_MOCKUP.md** — wireframe of translator-optimized UI
5. **KOSHA_TESTING_CHECKLIST.md** — acceptance criteria per phase

Ready to start Phase 1?

---

_Dr. Mārcis Gasūns_
