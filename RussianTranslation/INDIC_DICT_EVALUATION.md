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

## 4. License — CLEARED (2026-06-24)

- **Granted by email (2026-06-24):** the indic-dict maintainer granted **free use with
  attribution** for **all four** Indic-gloss dictionaries (`apte-hi`, `vedic-rituals-hi`,
  `shabdArtha_kaustubha`, `samskritam-tamizham`). The grant resolves the earlier gap —
  the repo still carries no SPDX `LICENSE` and the `.babylon` headers carry only
  `#bookname`, but the maintainer's email is our authoritative provenance.
- **Attribution obligation:** each source must be credited wherever it surfaces. For
  `samskritam-tamizham`, credit **Visalakshi Ramani** (her blog
  `sanskrittotamil.wordpress.com`); for the others, credit the indic-dict packaging plus
  the named work (Apte for `apte-hi`, etc.). Record the source per card/annotation.
- The earlier "defer ingestion" hold is **lifted**. Operationally the extracted data
  still stays **local/gitignored** like the other gate inputs (cf.
  SAMUDRA_INTEGRATION.md §6) — that is build discipline, no longer a rights blocker.

> **Provenance note:** the grant lives in email, not a repo `LICENSE`. Keep the message
> (sender, date, exact wording) on file; it is the citable basis for redistribution.

## 4a. Folded — `apte_hi` + `vedic_rituals_hi` wired into the gate (2026-06-24)

Built and verified the same day the license cleared:

- **Extraction** — [src/build_indic.py](src/build_indic.py) parses the StarDict
  `.babylon` exports (Devanagari headword → Hindi gloss) into SLP1-keyed JSONL,
  reusing build_src.py's Devanagari→SLP1 transducer. Output **111,235 `apte_hi` +
  6,166 `vedic_rituals_hi`** entries (gitignored `src/*.jsonl`; `.babylon` sources
  gitignored in `research/external/`). apte-hi cites headwords in the **nominative**
  (अग्निः→`agniH`, फलम्→`…am`) while PWG keys on stems — so each entry also carries a
  `stem` key (strip nom-sg visarga / neuter `-am`) and is indexed under both.
- **Gate wiring** — [src/corpus_gate.py](src/corpus_gate.py) gains a `SENSE` index +
  `lookup_sense()`; `build_card` emits a `hindi_sense` field. It is deliberately kept
  **out** of the Russian-token `heuristic()` — soft, sense-disambiguation only, never a
  correctness vote. [pwg_ru_prompts/4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt)
  gains Rule 8 + a `hindi_sense` input field + `"Hindi"` in `corroborated_by`.
- **Measured coverage:** a Hindi sense gloss exists for **32.7 %** of PWG headwords
  (`apte_hi` 31.7 %, `vedic_rituals_hi` 2.3 %) — nearly **double** the Russian
  correctness coverage (16.4 %). Verified joins: `agni`→4 Apte senses (आग / fire-god /
  the three ritual fires / digestive fire), `arTa`, `aMSa` (incl. कंधा = «плечо»).
- **Held:** `shabdArtha_kaustubha` (Kannada) and `samskritam-tamizham` (Tamil) — not
  built; logged as available votes pending a Kannada/Tamil-reading reviewer (§5).

## 4b. Second sweep — Sanskrit synonym-kośas + Meulenbeld binomials (2026-06-24)

A full-repo survey (every `.babylon` cross-checked against csl-orig codes) found two
more reusable, non-Cologne assets. **The cross-check is the point:** four datasets that
*look* new are already Cologne — `Vedic-Index-of-Names-and-Subjects` = **vei**,
`aufrecht-catalogus-catalogorum` = **acc**, `indian-epigraphical-glossary` = **ieg**,
`Personal-and-Geographical-Names-in-the-Gupta-Inscriptions` = **pgn**; and `Meulenbeld`
itself is **SNP** (its header reads *Data from sanskrit-lexicon.uni-koeln.de*). All
skipped as dupes.

**(i) Sanskrit synonym-kośas → the gate's `skd_vcp_synonyms` channel (Rule 5).**
[src/build_kosha.py](src/build_kosha.py) parses the **4 true synonym (nāmamālā-genre)
kośas** — Amarakośa `amara-onto` (which carries an explicit `समानार्थक:` field),
`nAmamAlikA`, and the two Abhidhānacintāmaṇi supplements (`pariShiShTa`/`shilonCha`) —
into an SLP1-keyed synonym index: **88,839 rows → 7.8 % of PWG headwords** get a
Sanskrit synonym set. This populates the gate's previously-empty `skd_vcp_synonyms`
(the *first* real Sanskrit-side corroboration source — SKD/VCP were never wired).
Verified: `arka`→अरुण/अर्यमन्/अंशुमालिन् (sun), `deva`→अमर/अमर्त्य, `aMSa`→भाग,
`svarga`→नाक/त्रिदिव/सुरलोक.
  - **Excluded by a data-quality audit (2026-06-24)** — 6 candidates whose groups are
    *not* synonymy and would inject misleading corroboration: `anekArthadhvanimanjarI`
    (a homonym/polysemy lexicon — `svarga`↦गो/अक्षि/जल = cow/eye/water), `bhUtasankhyA`
    (number-code words — grouped only as "0"), `upasargArthachandrikA` (root↔prefixed-
    root pairs), `jhaLkI-bhIma-nyAya-koshaH` (word↔its-own-visarga-variant, trivial),
    `vaiShNava`/`shaiva-kosha` (HTML-table *category* labels — विष्णु "≈" ब्रह्मन्).
    Also not synonym sources at all: `amara-sudhA` (Pāṇinian prakriyā/derivation —
    value for *paradigm* work), `laxaNa-sangraha` (nyāya definitions),
    `ekAkSharanAmamAlA` (verse-only), `e-bhAratI-sampat` (~3 rows). The first-pass
    inclusion of all 10 over-counted by ~1.6 pp (9.4 %→7.8 %); the audit pruned it.

**(ii) Meulenbeld plant → Latin binomial (= SNP).**
[src/build_meulenbeld.py](src/build_meulenbeld.py) parses the pre-extracted plant
glossary into **453 plant headwords, 235 with a Latin binomial** (`ajamodā`→*Apium
graveolens*, `agaru`→*Commiphora roxburghii*). Surfaces as `latin_binomials` on the
gate card — a deterministic fix for the binomial-left-untranslated failure mode
(`Hedysarum gangeticum`). Source is our own SNP; the indic-dict packaging is just the
convenient pre-extracted form.

Both stay gitignored (`src/*.jsonl`), kept out of the Russian heuristic, attribution
on file. Coverage lines added to `corpus_gate.py coverage`.

## 5. Recommendation / phased plan

1. **Skip en-head and the EN/FR/DE/SA gloss sets entirely** — pure Cologne duplication,
   we hold fresher copies. No action.
2. ~~**Clear licensing first**~~ **DONE (2026-06-24)** — free use with attribution
   granted for all four by email (§4). Query draft kept in
   [indic_dict_license_query.md](indic_dict_license_query.md) for the record.
3. ~~Fold `apte-hi` first~~ **DONE (2026-06-24, §4a)** — SLP1+stem join, `hindi_sense`
   on the card, Rule 8 in the stage-4 prompt; 31.7 % coverage.
4. ~~Add `vedic-rituals-hi`~~ **DONE (2026-06-24, §4a)** — Vedic-ritual top-up, +2.3 %.
5. **Hold `shabdArtha_kaustubha` / `samskritam-tamizham`** unless a Kannada/Tamil-reading
   reviewer joins — logged as available votes, not wired in.

All four stay **query/annotate-only** and **gitignored** like the other gate inputs;
none is a translation source and none touches csl-orig.
