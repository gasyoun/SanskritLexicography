# Strategic Decisions Needed — Kosha Lookup Modernization

_Created: 02-07-2026 · Last updated: 02-07-2026_

**This document distills the six decisions that will shape the entire roadmap. Answer these before Phase 1 begins.**

> **⚠️ Triage note (02-07-2026):** the first version of this file was declared
> "archived" by other kosha docs while **all six choice blanks were empty** —
> no decision had ever been recorded here. The blanks below are now filled with
> what was actually decided during the 02-07-2026 triage (see
> [KOSHA_FOLDER_SETUP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_FOLDER_SETUP.md)
> for the four meta-decisions M1–M4). Two structural mismatches are flagged
> inline: the previously "locked" audience (*Translators*) and cadence
> (*Monthly*) were never among the options offered here.

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

**Your choice:** **Translators > Learners > Scholars** (02-07-2026). *Mismatch:
"Translators" was not an offered persona — it appeared only as a parenthetical
inside "Learner". Recorded here as the canonical answer; UI-wise this is
closest to Hybrid with the fast path tuned for translation lookups.*

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

**Your choice:** **Maximal as ambition** (all Cologne + Russian dicts + KEWA +
morphology + corpus, per the original locked table); **MVP scope = MW + PWG +
AP90** (02-07-2026).

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

**Your choice:** **OPEN — leaning Nightly Batch** (02-07-2026). *Mismatch: the
previously "locked" cadence was "Monthly batch rebuild (nightly cron)" — both
self-contradictory and never among the options above. Decide when the build
pipeline is real.*

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

**Your choice:** **Cologne forms + corpus forms via reuse** (02-07-2026, follows
from meta-decision M3): consume the existing
[RussianTranslation/glossary/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/glossary)
form→lemma layer (DCS + vidyut.kosha fallback, 86.6 % token coverage) instead
of live Sanskrit Heritage API calls. No new morphology engine.

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

**Your choice:** **OPEN — "Links only" first** (02-07-2026), reusing the
existing Cologne etymology-extraction assets (10-dict derivation extractors,
shared affix + dhātu tables) rather than new extraction. Deeper tiers deferred
past MVP.

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

**Your choice:** **Static Export + Single API hybrid, in kosha's own repo**
(02-07-2026, meta-decision M4): a dedicated repo with its own GitHub Pages for
the static cache tier, plus samskrtam.ru for the full API. *Not*
`gasyoun.github.io/SanskritLexicography/…` — this repo's Pages already serves
the PWG article site from `gh-pages` and one repo gets one Pages site.

---

## Summary Table

| Decision | Chosen Option | Rationale |
|----------|---|---|
| 1. User Audience | Translators > Learners > Scholars | Primary consumer is the PWG→RU/EN translation workflow |
| 2. Dictionary Scope | Maximal (ambition) / MW + PWG + AP90 (MVP) | Full coverage later; ship the classic trio first |
| 3. Update Cadence | OPEN — leaning Nightly | "Monthly" lock was invalid (not an option, self-contradictory) |
| 4. Morphology Depth | Cologne + corpus forms **via existing glossary** | M3 reuse-first: 86.6 % coverage already built |
| 5. Etymology Scope | OPEN — Links-only first | Reuse Cologne etymology extractors; defer deeper tiers |
| 6. Deployment Target | Own repo + Pages (static) + samskrtam.ru (API) | M4: this repo's Pages is taken by the article site |

---

## What Happens Next

The decisions above feed the reuse-first re-plan of Phase 1 — see the "Next
steps" section of
[KOSHA_FOLDER_SETUP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_FOLDER_SETUP.md).
The implementation plan
([KOSHA_IMPLEMENTATION_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_IMPLEMENTATION_PLAN.md))
exists but predates these answers and the 02-07-2026 audit — treat its
timelines and code sketches as drafts to be reconciled, not specs to code from.

---

_Dr. Mārcis Gasūns_
