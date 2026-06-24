# indic-dict / stardict-sanskrit — evaluation for the Sa→Ru compilation

What [`indic-dict/stardict-sanskrit`](https://github.com/indic-dict/stardict-sanskrit)
offers the Russian-translation compilation, and what (if anything) we should take.
Evaluated 2026-06-24. **Decision: nothing is ingested yet** — license is unspecified
across the whole repo (see §4); this doc records the technical assessment and the
deferred-ingestion plan.

## 1. What the repo is — and why most of it duplicates what we already have

`stardict-sanskrit` is a **StarDict packaging** repo: CI builds each dictionary's
`.babylon`/`.txt` into StarDict/Aard2 artifacts on `gh-pages`. It is organized by
**headword language**, then by **gloss language**:

| Tree | Gloss langs | Net-new to us? |
|------|-------------|----------------|
| [`en-head/`](https://github.com/indic-dict/stardict-sanskrit/tree/master/en-head) | EN→SA reverse indexes (`apte-english-sanskrit-cologne`, `mw-english-sanskrit`, `borooah`, `carl`, `computer-shrIkAnta`, `dhAturatnAkara-RSS`) | **No** — the `-cologne`/`mw` ones are generated from Cologne; we hold the fresher source in [csl-orig](../../csl-orig). Reverse direction anyway. |
| [`sa-head/en\|french\|german\|sa-entries`](https://github.com/indic-dict/stardict-sanskrit/tree/master/sa-head) | EN / FR / DE / SA | **No** — almost all Cologne-generated (MW, Apte, PW…); csl-orig is newer. |
| [`sa-head/other-entries`](https://github.com/indic-dict/stardict-sanskrit/tree/master/sa-head/other-entries) | `bopp`, `frish` | **No** — these are **BOP** and **FRI** in our own dictionary table. |
| [`sa-head/other-indic-entries`](https://github.com/indic-dict/stardict-sanskrit/tree/master/sa-head/other-indic-entries) | Hindi / Tamil / Kannada | **Yes** — the only genuinely non-Cologne content in the repo. |

So the whole en-head tree and the EN/FR/DE/SA gloss sets are a no-op for us: we
already have their canonical, fresher sources. The **only** material worth assessing
is the four Indic-language gloss dictionaries.

## 2. The four net-new Indic-gloss dictionaries

Metadata read from the `.babylon` headers and file sizes via the GitHub API
(2026-06-24). Note: two `bookname` language tags are wrong in the source — corrected
here from the actual gloss script.

| Dict | `bookname` tag | Real gloss lang | Size | Source |
|------|----------------|-----------------|------|--------|
| [`apte-hi`](https://github.com/indic-dict/stardict-sanskrit/tree/master/sa-head/other-indic-entries/apte-hi) | `sa-hi` ✓ | **Hindi** | 19.6 MB | आप्टे — Apte, rendered into Hindi |
| [`vedic-rituals-hi`](https://github.com/indic-dict/stardict-sanskrit/tree/master/sa-head/other-indic-entries/vedic-rituals-hi) | `sa-sa` ✗ | **Hindi** (Vedic-ritual domain) | 3.3 MB | Vedic ritual terminology, Hindi gloss |
| [`shabdArtha_kaustubha`](https://github.com/indic-dict/stardict-sanskrit/tree/master/sa-head/other-indic-entries/shabdArtha_kaustubha) | `sa-kn` ✓ | **Kannada** | 34.9 MB | शब्दार्थकौस्तुभः |
| [`samskritam-tamizham_dictionary`](https://github.com/indic-dict/stardict-sanskrit/tree/master/sa-head/other-indic-entries/samskritam-tamizham_dictionary) | `sa-sa` ✗ | **Tamil** | 0.75 MB | Visalakshi Ramani, `sanskrittotamil.wordpress.com` (blog scrape) |

None of these is Sanskrit→Russian, so **none is a translation source** — our Russian
comes from the German Petersburg chain (see [DICTIONARY_CHAIN.md](DICTIONARY_CHAIN.md))
plus the Sa→Ru gate dictionaries. They can only ever be a **cross-check signal**.

## 3. Role: a cross-lingual *sense* signal in the stage-4 gate

The `pwg_ru` gate (see [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md) §2) currently
votes on **correctness** with four Sa→Ru dictionaries (Кочергина / Кнауэр / Фриш /
Смирнов) that match a *Russian* head-term directly. The Indic-gloss dicts **cannot do
that** — they gloss in Hindi/Tamil/Kannada, not Russian. Their value is one notch
softer and different in kind:

- **They are a cross-lingual *sense-disambiguation* vote, not a gloss match.** When PWG
  carries several senses and our Russian picks a primary, an independent third-language
  gloss corroborates *which sense is primary* — it never confirms the Russian wording.
  This sits **below** the Sa→Ru dictionary verdict and **alongside** the verse-level
  corpus signal (§2.2 there): soft, non-blocking, annotate-only, never overrides.
- **`apte-hi` is the standout** and the only one with structural leverage. It is *Apte*
  rendered into Hindi, and Apte is already in our orbit (csl-orig `ap90`/apte). That
  lets us align **Apte sense N ↔ apte-hi sense N ↔ our Russian sense N** — a *structured*
  sense cross-check, not just a bag-of-words vote. Hindi is also Indo-Aryan, so its
  glosses are cognate-rich with the Sanskrit and legible to most Russian Sanskritists.
- **`vedic-rituals-hi`** is niche but pointed: Hindi votes on **Vedic-ritual headwords**,
  exactly where modern Sa→Ru coverage (Кочергина 14.4 %) is thinnest while the
  Petersburg chain is densest. Small (3.3 MB), so cheap to fold.
- **`shabdArtha_kaustubha` (Kannada)** and **`samskritam-tamizham` (Tamil)** are
  genuine independent votes but **weak in practice**: Dravidian, and few of our
  reviewers read them, so a disagreement is hard for a human to adjudicate. Tamil is
  additionally a small blog scrape needing explicit author attribution.

**Gate-fit ranking:** `apte-hi` ≫ `vedic-rituals-hi` > `shabdArtha_kaustubha` >
`samskritam-tamizham`.

## 4. License — the blocker, ingestion deferred

- The repo has **no SPDX license** (`gh api …/repos/… .license` → `none`), and the
  `.babylon` headers carry **no** `#author`/`#description`/`#website`/license field —
  only `#bookname`. So all four are **license-unspecified**.
- `samskritam-tamizham` is explicitly a scrape of an individual's blog and *requires*
  attribution to Visalakshi Ramani — redistribution terms unclear.
- Per the standing decision: **note the gap, evaluate the technical fit (done above),
  defer actual ingestion** until per-dictionary licensing is cleared. Nothing from
  indic-dict enters the build or the gate yet.

This matches our existing discipline: gate inputs are local/gitignored and only enter
publishable card bodies once rights are confirmed (cf. SAMUDRA_INTEGRATION.md §6).

## 5. Recommendation / phased plan

1. **Skip en-head and the EN/FR/DE/SA gloss sets entirely** — pure Cologne duplication,
   we hold fresher copies. No action.
2. **Clear licensing first** for the four Indic-gloss dicts — a short query to the
   indic-dict maintainers (Vishvas Vasuki) on terms + upstream provenance, plus the
   Visalakshi Ramani attribution question for Tamil. Draft ready in
   [indic_dict_license_query.md](indic_dict_license_query.md).
3. **If cleared, fold `apte-hi` first** as a structured Apte-aligned Hindi sense signal:
   join on the SLP1 key, map sense-by-sense against our Apte structure, emit a soft
   `sense_corroborated_by=apte-hi` annotation in the stage-4 verdict. Never blocking,
   never overriding the Sa→Ru verdict.
4. **Add `vedic-rituals-hi`** as a domain top-up on Vedic-ritual headwords.
5. **Hold `shabdArtha_kaustubha` / `samskritam-tamizham`** unless a Kannada/Tamil-reading
   reviewer joins — log them as available independent votes, don't wire them in.

All four stay **query/annotate-only** and **gitignored** like the other gate inputs;
none is a translation source and none touches csl-orig.
