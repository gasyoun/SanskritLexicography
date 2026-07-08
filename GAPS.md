# GAPS — the Sanskrit-data known-unknowns frontier

_Created: 08-07-2026 · Last updated: 08-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS is what is *known*. This file is its **negative space** — the act FINDINGS cannot hold: **not-yet-knowing**, the frontier of things we have explicitly NOT measured. The moment a gap is measured, it **graduates** to a FINDINGS row (delete it here, cite the finding there). One of the seven epistemic registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md). Its infra twin is [`Uprava/GAPS.md`](https://github.com/gasyoun/Uprava/blob/main/GAPS.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates the **value if measured** (what it would unblock).
- **Origin marker:** ⚙️ auto (a set-difference script emitted this — a dataset with no FINDINGS row) · ✍️ human (a session flagged it).

Then `Why it matters:`, `Blocker:`, `How to close:`, and a `> **Source:**` line.

**Auto-seed:** [`seed_gaps.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_gaps.py) does a set-difference — datasets present in [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) / [`kosha` manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) that have **no** FINDINGS row, plus the "per-layer statistics still to compute" backlog named in [`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md).

---

### §1. Derivative ī/ū gen.pl accent split (D3) — n=2, unresolvable
🟡 ✍️ **We have NOT measured the empirical `-īnā́m` vs `-ī́nām` split at usable n.**
Why it matters: it is the one unresolved cell blocking the ZALIZNYAK_INDEX a–f accent axis emission; would settle Whitney's own §319a/§356 contradiction ([CONTRADICTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)).
Blocker: needs a wider VedaWeb 2.0 pull — blocked mid-run by a `vedaweb.uni-koeln.de` outage; only n=2 attested forms (`raTI`, `vaDU`) so far.
How to close: resume the VedaWeb export per [`SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md), grow n, split by adjective (`bahvī́`) vs noun (`nadī́`) type.
> **Source:** [FINDINGS §54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents) · WhitneyRoots · 08-07-2026

### §2. Error population of 40 of 43 dictionaries
🟠 ✍️ **We have NOT estimated the error-prone-record population for 40 of 43 dicts.**
Why it matters: correction-campaign planning currently assumes convergence; only PW (~14% done), MW (~10%), BUR are estimable — the other 40 have <10 two-era recaptures.
Blocker: needs a corpus rerun / more overlapping corrections — Chapman mark–recapture requires ≥10 two-era recaptures per dict.
How to close: accumulate a second correction era per dict, or use a different estimator; owner csl-observatory `error_recapture.md` (paper A48).
> **Source:** [FINDINGS §46](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#46-twelve-years-of-corrections-cover-only-1014--of-the-estimated-error-population) · csl-observatory · 08-07-2026

### §3. Heritage inflected-form morphology XML — never ingested
🟠 ✍️ **We have NOT ingested Heritage's inflected-form morphology XML (1,286,615 forms / 32,837 stems).**
Why it matters: would be a third morphology witness (3× kosha's vidyut-built 426,410 forms); unblocks Heritage roadmap Phase 4; `heritage_forms_oracle` is only a partial alignment without it.
Blocker: data access — the XML is NOT in either git repo (GitHub mirror or INRIA GitLab); only downloadable behind the Anubis wall from `sanskrit.inria.fr/DATA/XML/{SL,WX}_morph.xml.gz` (v3.81).
How to close: a human browser download of the two `.xml.gz` URLs (bookmarked in §51), then ingest; LGPLLR-vs-BY-SA composition @DECIDE first.
> **Source:** [FINDINGS §47](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#47-heritage-data-is-acquirable-despite-the-anubis-wall--via-a-github-mirror-the-morphology-xml-is-not-in-it) + [§51](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#51-huet-correspondence-predates-this-session-2021--the-morphology-xml-gate-was-already-resolved-in-writing-direct-download-urls-recovered) · SanskritLexicography · 08-07-2026

### §4. Homonym token frequency beyond the 26+5 splittable groups
🟡 ✍️ **We have NOT attributed token frequency for the 33 of 38 DCS-lumped homonym groups that share a present class.**
Why it matters: token-level "N in this sense · M for the lemma" displays are impossible for these without sense/gloss adjudication; it is the ceiling on per-sense frequency accuracy.
Blocker: no tool — gaṇa is undistinguishing (unaccented corpus, §8); needs manual gloss adjudication (DCS `meanings` ↔ Warnemyr gloss).
How to close: extend the coverage≥0.55 gloss-mapping approach in `crosswalk/token_attribution.json`; owner WhitneyRoots.
> **Source:** [FINDINGS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#2-homonym-token-splitting-has-a-hard-morphological-ceiling) · WhitneyRoots · 08-07-2026

### §5. `Stopovye` parallel-passage bundle vs full export — never content-diffed
🟡 ✍️ **We have NOT content-diffed the 1.17 GB `PARA/Stopovye` bundle against `dcs-parallel-passages-full` (506,787 rows).**
Why it matters: it is the largest single derived-data bundle in VisualDCS; whether it is a stop-word-filtered variant or independent data determines if it is separately citable; its row count is still `null` (no schema-aware parse).
Blocker: no tool — needs a schema-aware per-file alignment parse, not a line count.
How to close: parse the per-passage CSV records, diff against the full-export sample; owner VisualDCS / manifest `stopovye-parallel-passages`.
> **Source:** kosha [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `stopovye-parallel-passages` note (H291) · 08-07-2026

### §6. Cyrillic-only Sanskrit name glossaries — no join key exists
🟠 ✍️ **We have NOT (and cannot safely) build a Cyrillic→SLP1 key for the 3 fully-Cyrillic name glossaries.**
Why it matters: 3 of 6 SamudraManthanam name indices (Потапова, Эрман-Темкин, Бадь Kadambari) are 100% Cyrillic — blocked from any pwg_ru corpus_gate reuse.
Blocker: no tool that is safe — practical Russian transcription collapses dental/retroflex (т = त and ट); a rule-based converter manufactures wrong keys for exactly the retroflex-bearing epic names.
How to close: a proper-noun lookup table validated against a Sanskrit onomasticon (not character rules), checked as its own artifact first.
> **Source:** [FINDINGS §60](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#60-practical-russian-transcription-of-sanskrit-names-has-no-safe-reverse-transliteration) · RussianTranslation · 08-07-2026

---

_Dr. Mārcis Gasūns_
