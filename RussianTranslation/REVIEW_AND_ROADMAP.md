# pwg_ru — full review and roadmap (2026-06-16)

A candid retrospective of the corpus-first build and a phased plan forward.
Companion docs: [METHODOLOGY_REVIEW.md](METHODOLOGY_REVIEW.md) (5-lens external
review), [APRESJAN.md](APRESJAN.md) (theory), [HARVEST.md](HARVEST.md) (the harvest
layer), [failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md) (defects),
[CHANGELOG.md](CHANGELOG.md) (timeline).

## 1. What was built

An end-to-end, provenance-tracked pipeline to turn the German Petersburg
Dictionary (PWG) into a corpus-attested Russian edition:

```
PWG card → pwg_mask (lossless German skeleton)
        → harvest:  5 S–R dictionaries  +  corpus lexicon (1.09M alignments, 190k keys)
        → assemble: stratified, lemma-grouped, content-filtered attested Russian
                    + an Apresjan near-synonym candidate set
        → translate (Sonnet 4.6, Max)  → judge (Opus 4.8)  → human review queue
        → rights-gated, provenance-stamped card
```

Concrete assets now on disk / in the repo:

- **Corpus word-alignment lexicon** — 1,091,528 alignments, **190,838 distinct
  SLP1 keys**, 116 works, 99% of the translatable corpus; stratified by genre
  (Renou) + date (Dharmamitra) into Vedic / Epic / Classical / Medieval;
  translation vs commentary tagged. (Gitignored data; rebuilt by code.)
- **`<ls>`→stratum map** — 45 PWG sources = 72.4% of 772k citations, 29.8%
  corpus-harvestable.
- **Harvest reader** — SLP1 key → stratified, lemma-grouped (pymorphy3),
  POS-filtered renderings, cited-stratum first; near-synonym candidate set.
- **QA** — deterministic auditor (`_audit.py`), human review state machine +
  worklist (`run_batch.py review`), per-sense rights gate + **CC BY-SA 4.0**.
- **Incremental tooling** — `add_corpus_text.py` + [ADDING_TEXTS.md](ADDING_TEXTS.md).
- **Docs** — methodology review, Apresjan grounding, failure gallery, changelog.

## 2. What is good

- **Reuse that is richer than translation.** The corpus surfaces *attested*
  senses a bilingual dictionary would otherwise miss — e.g. `aṃśa` yields not just
  часть/доля but частица, жребий, **частичное воплощение** (aṃśa-avatāra),
  луч·искра·проявление, and the Vedic deity Аṃśa — each stratified.
- **Era-correct Russian.** Stratification means a Ṛgvedic citation harvests
  Vedic Russian, an epic citation epic Russian (dharma → дхарма in Manu vs
  добродетель/долг in the Rāmāyaṇa).
- **Native theoretical backbone.** Grounded in Apresjan / the Moscow Semantic
  School — the correct standard for a Russian-target dictionary — with the
  near-synonym-discrimination method built into the harvest output.
- **QA that actually caught things.** The deterministic auditor caught an 81%
  placeholder-fabrication and was corrected for false positives without
  destroying data (gallery F1, F9). Provenance, rights, and a human queue make it
  printable-grade.
- **Reproducible, incremental, documented.** Code committed, data regenerable,
  new texts addable in one command, every decision written down.

## 3. What is bad / honest weaknesses

- **Precision is unmeasured.** There is no gold standard yet — we do not have a
  number for how often a harvested sense is correct. (Methodology rec 4.) This is
  the single most important gap before any print claim.
- **The lexicographic microstructure is designed, not built.** Cards are still a
  flat sense-bag: no sense tree, the homonym `h`-number is dropped (homographs
  pool), no `equivalence_type` (equivalent vs explanatory gloss), no diasystem
  labels. The Apresjan "portrait" is on paper. (Rec 6.)
- **Synonym discrimination is *presented*, not *performed*.** The card shows the
  candidate set (часть·частица·доля·жребий…); the actual differentiae
  (semantic / combinatorial / connotational) are not yet written. That is the
  next LLM step.
- **The 216 a-section cards are still the OLD provisional ones** — translated
  before the corpus lexicon existed. The corpus-first re-harvest + re-translate
  has not been run yet (this is the immediate next action).
- **Coverage is bounded by one corpus.** SamudraManthanam is the only source;
  Brāhmaṇas are absent, some Atharvaveda/Upaniṣad sub-areas thin. New-text tooling
  mitigates this but the gaps are real today.
- **Operational fragility.** The environment reaps long-running background tasks
  every ~15–60 min; the build needed the supervisor + manual restarts and an
  mtime-not-rowcount liveness check. Workable, but not hands-off.
- **Minor data tail.** A handful of legacy mis-tagged commentary rows (F9); the
  Vedic-merge `period` re-stamp of the data is pending (display already merged).
- **Cost ran ~30% over estimate** (~$49 vs ~$37) — comment-dense epics; acceptable
  (more evidence), but projections should use a representative sample.
- **No interoperable export yet** — no TEI Lex-0 / OntoLex, no reverse
  (Russian→Sanskrit) index, no CITATION.cff / DOI / edition freeze. (Rec 8.)

## 4. Roadmap

Machine-readable companion artifacts:
[roadmap/scientific_hardening.json](roadmap/scientific_hardening.json) is the
canonical phase/gate record; [roadmap/quality_gates.jsonl](roadmap/quality_gates.jsonl)
is the line-oriented audit/dashboard feed; validate both with
`python src/roadmap_check.py`.

**Phase A — prove the output (now).** Corpus-first re-harvest + re-translate the
216 a-section cards; ship a reviewable sample edition slice; measure first-pass
quality. *Deliverable: a-section cards with corpus-attested, stratified senses.*

**Phase B — make it scholarly.** (1) Gold standard + precision/recall with Wilson
CIs (rec 4). (2) Lexicographic microstructure — sense tree, homonym `h`-keying,
`equivalence_type`, diasystem labels (rec 6, Apresjan portrait). (3) The
synonym-discrimination step — turn candidate sets into discriminated entries
(Apresjan / *Новый объяснительный словарь синонимов* method).

**Phase C — scale + enrich.** Extend beyond the a-section across PWG; add corpus
texts via `add_corpus_text.py` (Brāhmaṇas, more kāvya, śāstra) to lift thin
strata; regular-polysemy layer to predict/audit sense extensions.

**Phase D — publish.** TEI Lex-0 / OntoLex-vartrans export (reuse csl-standards
exporters), Russian→Sanskrit reverse index, CITATION.cff + Zenodo DOI, an
immutable edition cut, and the JSONL→typeset print path.

## 5. Immediate plan — the 216 a-section cards (Phase A)

1. **Re-harvest** the a-section with the corpus-first `assemble` (done: the
   machinery is wired; cards now carry `corpus_lexicon` senses + synonym sets).
2. **Re-translate** via the Claude Code workflow (Sonnet translate + Opus judge),
   now feeding the corpus synonym set + stratum into the prompt, so the output
   reflects attested usage rather than a cold translation.
3. **(Optional) discriminate** the near-synonym sets in the same or a follow-on
   pass (Apresjan differentiae).
4. **Collect** → provenance-stamp → review queue; spot-check a sample.
5. **Review** the slice together; decide print microstructure before scaling.

Open decisions are in §questions of this turn's message.
