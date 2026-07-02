# Strategic Decisions Needed — Kosha Lookup Modernization

_Created: 02-07-2026 · Last updated: 02-07-2026_

**This document distills the six decisions that will shape the entire roadmap. Answer these before Phase 1 begins.**

---

## Decision 1: Primary User Audience

**Question:** Who are we optimizing for?

**Options:**

| Persona | Needs | Default UI | Search Model |
|---------|-------|-----------|---|
| **Learner** (students, translators) | Speed, simple definitions, Devanagari | Lemma → 1–2 best senses | Frequency-ranked results |
| **Scholar** (researchers, lexicographers) | Etymology, full apparatus, Cologne revisions | Lemma → all senses + citations | Citation-ranked results |
| **Hybrid** (serve both) | Fast path for learners, deep path for scholars | Progressive disclosure (simple → advanced) | Dual-rank model |

**Implication:**
- **Learner-first** → Prioritize Phases 1–3, defer Phase 4 (etymology/apparatus)
- **Scholar-first** → Prioritize Phases 1–2, invest heavily in Phase 4
- **Hybrid** → All phases needed; complexity increases; timeline ~14 weeks

**Your choice:** _______________

---

## Decision 2: Dictionary Scope

**Question:** Which Cologne dictionaries must be searchable?

**Options:**

| Scope | Dictionaries | Index Size | Build Time | Why Choose |
|-------|---|---|---|---|
| **Minimal** | MW only | ~50 MB | ~5 min | Fastest; covers 70% of scholar lookups |
| **Core** | MW + PWG | ~120 MB | ~15 min | Classic European pair; complementary |
| **Extended** | MW + PWG + AP90 + GRA + PW + CAE | ~250 MB | ~30 min | Comprehensive coverage; learner variants |
| **Maximal** | All available Cologne (9–12 dicts) | ~400+ MB | ~60 min | Exhaustive; for scholarly completeness |

**Implication:**
- **Minimal** → Faster build & query; but users must cross-reference if MW missing
- **Core** → Recommended balance; covers 90% of needs
- **Extended** → Better learner experience (Apte = learner dict); slower builds
- **Maximal** → Scholarly gold standard; overkill for most users; slower performance

**Your choice:** _______________

---

## Decision 3: Real-Time Updates vs Batch

**Question:** How quickly must Cologne corrections surface?

**Options:**

| Model | Update Frequency | Freshness | Complexity | Cost |
|-------|---|---|---|---|
| **Static Snapshot** | Quarterly | ±3 months old | Low | Low (one-time build) |
| **Nightly Batch** | 1/day at 2 AM | ≤24 hours old | Medium | Low (cron job) |
| **Real-Time Sync** | Every csl-orig commit | Instant | High | Medium (webhook + rebuild) |

**Implication:**
- **Static** → Set-and-forget; good for archived editions; not suitable if Cologne actively correcting
- **Nightly** → Sweet spot; users see corrections within a day; simple to implement
- **Real-Time** → Academic standard; adds infrastructure complexity; watch out for race conditions

**Your choice:** _______________

---

## Decision 4: Morphological Lookup Depth

**Question:** Should users be able to search inflected forms (not just lemmas)?

**Options:**

| Depth | Example | Coverage | Index Size | Recall | Precision |
|-------|---------|----------|-----------|--------|-----------|
| **Lemmas only** | Search "dharma" → find धर्म (lemma) | ~30k Sanskrit lemmas | ~120 MB | Low (users must know citation form) | High |
| **Cologne forms** | Search "bhagavān" → find भगवान (lemma भगवत्) | ~100k attested forms in Cologne dicts | ~300 MB | Medium (covers dictionary headwords + subentries) | High |
| **Corpus forms** | Search "bhagavān" → also show Rigveda verses | All 5.6M corpus forms | ~500 MB + corpus.db | High (anything attested in texts) | Lower (may be rare/archaic) |

**Implication:**
- **Lemmas only** → Fast, clean; suits scholars who know citation forms; annoying for learners
- **Cologne forms** → Recommended; covers 80% of learner needs; manageable index size
- **Corpus forms** → Scholarly gold; but means form A might pull up 50 verses and user still doesn't know why; softer signal (verse-level, not per-word)

**Your choice:** _______________

---

## Decision 5: Etymology & Apparatus Scope

**Question:** How much etymological and source information should be visible?

**Options:**

| Scope | What's Shown | Complexity | Dependencies |
|-------|---|---|---|
| **None** | Headword + modern senses only | None | None |
| **Links only** | Headword → root link (e.g., "dharma ← √ dhṛ") | Low | WhitneyRoots (SanskritLexicography) |
| **Full tree** | Headword → root → alternative derivations (e.g., "dharma / dhar- / dharaṇa") | Medium | csl-atlas etymology extraction |
| **With citations** | Full tree + `<ls>` tags hyperlinked to corpus passages | High | csl-atlas + SamudraManthanam corpus |
| **Maximal** | Tree + citations + Cologne revision history (when did this meaning appear?) | Very High | csl-atlas + csl-corrections + git history |

**Implication:**
- **None** → Simplest; but sacrifices scholarly depth
- **Links only** → Recommended first step; low cost, high value
- **Full tree** → Scholarly win; requires csl-atlas etymology data (check availability)
- **With citations** → Excellent; adds hyperlinks to corpus evidence
- **Maximal** → Ideal; but technically complex (git blame across dict files)

**Your choice:** _______________

---

## Decision 6: Deployment Target & Architecture

**Question:** Where should the kosha API live?

**Options:**

| Target | Deployment | Latency | Scalability | Maintenance | Ideal For |
|--------|---|---|---|---|---|
| **Single API** | samskrtam.ru/api/kosha | ~200 ms | Medium (can add caching layer) | Simple | All users; learners OK with slight delay |
| **Static Export** | gasyoun.github.io/kosha (HTML files) | ~50 ms (edge cached) | Excellent (GitHub Pages) | Low (rebuild nightly) | Scholars; learners; read-heavy |
| **Hybrid CDN** | cdn.samskrtam.ru (static) + samskrtam.ru/api (dynamic fallback) | ~30 ms (cached) | Excellent | Medium | Optimal for all audiences |
| **Microservice** | kosha.samskrtam.ru (dedicated domain) | ~100 ms | Excellent (independent scaling) | Medium | Heavy users; can rate-limit separately |

**Implication:**
- **Single API** → Simplest ops; but all users hit same server; no geographic distribution
- **Static Export** → Ultra-fast (CDN edge); but requires nightly rebuild; no real-time updates
- **Hybrid CDN** → Best of both; top-10k cached @ edge, rest API-backed; complexity tradeoff worth it
- **Microservice** → Overkill unless kosha traffic scales to millions/day; cleaner separation but more ops

**Your choice:** _______________

---

## Summary Table

| Decision | Chosen Option | Rationale |
|----------|---|---|
| 1. User Audience | | |
| 2. Dictionary Scope | | |
| 3. Update Cadence | | |
| 4. Morphology Depth | | |
| 5. Etymology Scope | | |
| 6. Deployment Target | | |

---

## What Happens Next

Once you fill in the six decisions above, I will generate:

1. **Phase-by-phase implementation plan** (specific tasks, dependencies, file changes)
2. **Data schema** (SQLite table definitions, JSON structure)
3. **API contract** (OpenAPI spec with examples)
4. **UI mockups** (Figma-style wireframes or HTML prototypes)
5. **Testing checklist** (acceptance criteria per phase)
6. **Timeline with milestones** (realistic estimates given your choices)

**Estimated time to first decision deadline:** ~2 hours (you can skip if defaults are acceptable)

---

_Dr. Mārcis Gasūns_
