# GAPS — the Sanskrit-data known-unknowns frontier

_Created: 08-07-2026 · Last updated: 08-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS is what is *known*. This file is its **negative space** — the act FINDINGS cannot hold: **not-yet-knowing**, the frontier of things we have explicitly NOT measured. The moment a gap is measured, it **graduates** to a FINDINGS row (delete it here, cite the finding there). One of the seven episteme registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md); the full set is on the [episteme dashboard](https://gasyoun.github.io/SanskritLexicography/episteme/). Its infra twin is [`Uprava/GAPS.md`](https://github.com/gasyoun/Uprava/blob/main/GAPS.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates the **value if measured** (what it would unblock).
- **Origin marker:** ⚙️ auto (a set-difference script emitted this — a dataset with no FINDINGS row) · ✍️ human (a session flagged it).

Then `Why it matters:`, `Blocker:`, `How to close:`, and a `> **Source:**` line.

**Auto-seed:** [`seed_gaps.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_gaps.py) does a set-difference — datasets present in [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) / [`kosha` manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) that have **no** FINDINGS row, plus the "per-layer statistics still to compute" backlog named in [`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md).

---

## A. Blocked on data we don't yet have
*Gaps that stay open until an outage lifts, more correction eras accrue, or a walled dataset is downloaded — the blocker is data, not method.*

### §1. Derivative ī/ū gen.pl accent split (D3) — n=2, unresolvable
🟡 ✍️ **We have NOT measured the empirical `-īnā́m` vs `-ī́nām` split at usable n.**
Why it matters: it is the one unresolved cell blocking the ZALIZNYAK_INDEX a–f accent axis emission; would settle Whitney's own §319a/§356 contradiction ([CONTRADICTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)).
Blocker: needs a wider VedaWeb 2.0 pull — blocked mid-run by a `vedaweb.uni-koeln.de` outage; only n=2 attested forms (`raTI`, `vaDU`) so far.
How to close: resume the VedaWeb export per [`SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md), grow n, split by adjective (`bahvī́`) vs noun (`nadī́`) type.
↔ Interlinks: closing this gap rules [CONTRADICTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) (Whitney's own §319a/§356 self-contradiction) · [RECIPES §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (Whitney accent validation) is the pass that would consume the wider pull.
> **Source:** [FINDINGS §54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents) · [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

### §2. Error population of 40 of 43 dictionaries
🟠 ✍️ **We have NOT estimated the error-prone-record population for 40 of 43 dicts.**
Why it matters: correction-campaign planning currently assumes convergence; only PW (~14% done), MW (~10%), BUR are estimable — the other 40 have <10 two-era recaptures.
Blocker: needs a corpus rerun / more overlapping corrections — Chapman mark–recapture requires ≥10 two-era recaptures per dict.
How to close: accumulate a second correction era per dict, or use a different estimator; owner csl-observatory `error_recapture.md` (paper A48).
↔ Interlinks: [RECIPES §6](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (correction loci census) is the per-dict correction-density base this estimate builds on · [ASSUMPTIONS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (a correction queue stays valid) is the perishability that makes a second era hard to accrue.
> **Source:** [FINDINGS §46](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#46-twelve-years-of-corrections-cover-only-1014--of-the-estimated-error-population) · [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

### §3. Heritage inflected-form morphology XML — never ingested
🟠 ✍️ **We have NOT ingested Heritage's inflected-form morphology XML (1,286,615 forms / 32,837 stems).**
Why it matters: would be a third morphology witness (3× kosha's vidyut-built 426,410 forms); unblocks Heritage roadmap Phase 4; `heritage_forms_oracle` is only a partial alignment without it.
Blocker: data access — the XML is NOT in either git repo (GitHub mirror or INRIA GitLab); only downloadable behind the Anubis wall from `sanskrit.inria.fr/DATA/XML/{SL,WX}_morph.xml.gz` (v3.81).
How to close: a human browser download of the two `.xml.gz` URLs (bookmarked in §51), then ingest; LGPLLR-vs-BY-SA composition @DECIDE first.
↔ Interlinks: a third morphology witness stresses [ASSUMPTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (DCS lemma == CDSL headword — the very join whose 18.6% unlinked residue Heritage could cover) · [DEAD_ENDS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (corpus present-class attribution) is why an independent morphology source, not corpus inference, is needed.
> **Source:** [FINDINGS §47](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#47-heritage-data-is-acquirable-despite-the-anubis-wall--via-a-github-mirror-the-morphology-xml-is-not-in-it) + [§51](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#51-huet-correspondence-predates-this-session-2021--the-morphology-xml-gate-was-already-resolved-in-writing-direct-download-urls-recovered) · [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

## B. Blocked on a tool or method, not data
*The data is in hand; what's missing is a statistics pass, a schema-aware parse, or a validated lookup that doesn't exist yet.*

### §4. Homonym token frequency beyond the 26+5 splittable groups
🟡 ✍️ **We have NOT attributed token frequency for the 33 of 38 DCS-lumped homonym groups that share a present class.**
Why it matters: token-level "N in this sense · M for the lemma" displays are impossible for these without sense/gloss adjudication; it is the ceiling on per-sense frequency accuracy.
Blocker: no tool — gaṇa is undistinguishing (unaccented corpus, §8); needs manual gloss adjudication (DCS `meanings` ↔ Warnemyr gloss).
How to close: extend the coverage≥0.55 gloss-mapping approach in `crosswalk/token_attribution.json`; owner WhitneyRoots.
↔ Interlinks: [ASSUMPTIONS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (giant verb root at homonym index 0) is the record-reach premise that must hold to even enumerate these groups · [DEAD_ENDS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (corpus present-class attribution) is the refuted shortcut — gaṇa can't disambiguate them · [GLOSSARY "homonym index"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the ordinal in play.
> **Source:** [FINDINGS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#2-homonym-token-splitting-has-a-hard-morphological-ceiling) · [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

### §5. `Stopovye` parallel-passage bundle vs full export — never content-diffed
🟡 ✍️ **We have NOT content-diffed the 1.17 GB `PARA/Stopovye` bundle against `dcs-parallel-passages-full` (506,787 rows).**
Why it matters: it is the largest single derived-data bundle in VisualDCS; whether it is a stop-word-filtered variant or independent data determines if it is separately citable; its row count is still `null` (no schema-aware parse).
Blocker: no tool — needs a schema-aware per-file alignment parse, not a line count.
How to close: parse the per-passage CSV records, diff against the full-export sample; owner VisualDCS / manifest `stopovye-parallel-passages`.
↔ Interlinks: [DEAD_ENDS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (OccId/sent_id as a key) is the passage-id keying trap this schema-aware diff must avoid · [ASSUMPTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (one transliteration keys all DCS files) is the keying premise any DCS-side alignment leans on.
> **Source:** [kosha](https://github.com/gasyoun/kosha) [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `stopovye-parallel-passages` note (H291) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

### §6. Cyrillic-only Sanskrit name glossaries — no join key exists
🟠 ✍️ **We have NOT (and cannot safely) build a Cyrillic→SLP1 key for the 3 fully-Cyrillic name glossaries.**
Why it matters: 3 of 6 SamudraManthanam name indices (Потапова, Эрман-Темкин, Бадь Kadambari) are 100% Cyrillic — blocked from any pwg_ru corpus_gate reuse.
Blocker: no tool that is safe — practical Russian transcription collapses dental/retroflex (т = त and ट); a rule-based converter manufactures wrong keys for exactly the retroflex-bearing epic names.
How to close: a proper-noun lookup table validated against a Sanskrit onomasticon (not character rules), checked as its own artifact first.
↔ Interlinks: [DEAD_ENDS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (NFD-normalization as a key) is the same class of lossy character-rule bridge that manufactures wrong keys here · [GLOSSARY "SLP1 vs IAST"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) frames the scheme mismatch a Cyrillic→SLP1 map would have to cross.
> **Source:** [FINDINGS §60](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#60-practical-russian-transcription-of-sanskrit-names-has-no-safe-reverse-transliteration) · [RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

---

## ⚙️ Auto-seeded candidates (unconfirmed — `seed_gaps.py`, 08-07-2026)

Surfaced by [`seed_gaps.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_gaps.py) as a set-difference over the [kosha manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json): datasets that exist but carry **no** FINDINGS row measuring them. These are `⚙️ auto` **candidates** — a human confirms (→ `✍️`, promote to FINDINGS once measured) or deletes. Row counts are the manifest's; the "why it matters" is a first pass to be sharpened.

### §7. `dcs-stem-cooccurrence-full` (353,352 stem-pair rows) is uncharacterised
🟡 ⚙️ **We have the full Sanskrit-stem co-occurrence table (353,352 pairs, IDs 1–222342) but NO FINDINGS row on what its network structure shows.**
Why it matters: a corpus-wide collocation graph would ground compound-formation, synonym-cluster, and semantic-field claims that are currently asserted per-lemma; feeds any distributional-semantics analysis.
Blocker: no tool — needs a graph/statistics pass (degree distribution, top collocates, hapax rate), not a row count.
How to close: load the pair table, compute the obvious network statistics, append a FINDINGS row; owner VisualDCS.
↔ Interlinks: [RECIPES §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (DCS↔CDSL crosswalk) is the join a collocation graph would enrich into dictionary-grounded semantic fields · [GLOSSARY "form_key"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) is the keying the stem-pair rows must share to align.
> **Source:** manifest `dcs-stem-cooccurrence-full` (H291) · [kosha](https://github.com/gasyoun/kosha) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

### §8. DCS syntagmatic collocation tables (Прил. 6 + 7) are unanalysed
🟡 ⚙️ **We have the per-lemma collocate tables — all-corpus (`dcs-sintagmatic-appendix7`, 82,800 rows) and per-historical-period (`dcs-sintagmatic-appendix6-periods`, 19,076 rows, 7 files) — but NO FINDINGS row comparing them.**
Why it matters: the period-split vs all-corpus pair is exactly the data to test whether collocations are epoch-stable (the varga question §62, but at the lexical layer); a genuine diachronic-collocation finding.
Blocker: no tool — needs a per-period vs all-corpus diff; the appendix7 copy also has a byte-different UTF-16LE Cyrillic twin (H291) to dedup first.
How to close: align the period files against the all-corpus table, measure collocation drift; owner VisualDCS.
↔ Interlinks: [CONTRADICTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) is the same epoch-stability question one layer up (vargas) whose χ² method this reuses at the lexical layer · [RECIPES §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (varga diachrony) is the diachronic-comparison pass to mirror.
> **Source:** manifest `dcs-sintagmatic-appendix7` / `dcs-sintagmatic-appendix6-periods` (H291) · [kosha](https://github.com/gasyoun/kosha) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

### §9. `heritage-forms-crosswalk-extras` disagreement classes are uncounted
🟡 ⚙️ **We have the Heritage form-level crosswalk extras (1,037,239 rows, incl. a `heritage_forms_oracle_disagreements` form→disagreement-class table) but NO FINDINGS row on how often Heritage and kosha disagree, or on what.**
Why it matters: the disagreement rate + its classes are the missing quality metric for the Heritage morphology witness ([GAPS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)); tells us whether to trust Heritage forms as an oracle.
Blocker: data tier — `restricted` (Heritage LGPLLR composition), so the count is publishable but the rows aren't public.
How to close: tally the disagreement-class distribution, append a FINDINGS row (rate only); owner SanskritLexicography HeadwordLists.
↔ Interlinks: [ASSUMPTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (DCS lemma == CDSL headword) is the join whose quality this disagreement rate would quantify · [GLOSSARY "headword vs lemma"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the form/lemma distinction the disagreement classes turn on.
> **Source:** manifest `heritage-forms-crosswalk-extras` (H291) · [kosha](https://github.com/gasyoun/kosha) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

### §10. Which-dictionary routing benchmark has single-annotator gold, no κ
🟠 ⚙️ **The 24-scenario routing shared-task benchmark (`which-dictionary-routing-benchmark`) has single-annotator gold (Fable 5, one pass) — NO inter-annotator agreement measured over its 44-code answer space.**
Why it matters: a shared-task benchmark with no κ can't quantify its own gold reliability, which caps the credibility of any leaderboard result built on it (csl-guides `/about/shared-tasks`).
Blocker: needs a second independent annotation pass (see `/gold-adjudicate`), not just a rerun.
How to close: second-annotate the 24 scenarios, compute κ + a confusion table, append a FINDINGS row.
↔ Interlinks: [CONTRADICTIONS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) is the same "two independent passes disagree" reliability worry, there for a correlation instead of a gold set · [GLOSSARY "ls source map"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) frames the dictionary-code answer space κ would be computed over.
> **Source:** manifest `which-dictionary-routing-benchmark` (H281) · [kosha](https://github.com/gasyoun/kosha)/[csl-guides](https://github.com/sanskrit-lexicon/csl-guides) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

### §11. `dcs-verb-form-frequency-prelim` is flagged preliminary, never finalised
🟡 ⚙️ **The DCS verb-form frequency table (106 rows) is explicitly `preliminary` in the manifest — NO FINDINGS row, and no final version.**
Why it matters: verb forms are the top of the frequency dictionary (roots dominate §64/§16); a finalised verb-form frequency would directly feed the freq-first translation queue.
Blocker: unclear — the "preliminary" marker's reason isn't recorded (coverage? method?); needs the owner to state what makes it non-final.
How to close: identify the preliminary caveat, finalise or document why it can't be, append a FINDINGS row; owner VisualDCS.
↔ Interlinks: [ASSUMPTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (a PWG-key worklist covers the universe) and [ASSUMPTIONS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (the verb-root record) are the root-frequency premises a finalised verb-form table would feed the freq-first translation queue.
> **Source:** manifest `dcs-verb-form-frequency-prelim` (H291) · [kosha](https://github.com/gasyoun/kosha) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

---

## Conclusions

- **The frontier sorts by blocker, not by topic.** §1–§3 wait on **data we don't have** (a VedaWeb outage, more correction eras, a walled Heritage download); §4–§6 wait on a **tool or method that doesn't exist yet** (gloss-level token adjudication, a schema-aware bundle parse, a validated Cyrillic→SLP1 onomasticon). Naming the blocker type is what tells a reader whether the gap needs a human download or a coding pass.
- **The 🟠 rows are the pipeline-unblockers.** §2 (error population), §3 (Heritage morphology), §6 (Cyrillic name keys), §10 (routing κ) each free a whole downstream — and Heritage as a third morphology witness (§3) is the single biggest unlock, gated only on a browser download + a licence @DECIDE.
- **The ⚙️ auto-seeded §7–§11 are candidates, not confirmed gaps** — each is a manifest dataset with no FINDINGS row, awaiting a human confirm-or-delete. Several (§7, §8, §9) need only a statistics pass over data already in hand, not new acquisition.
- **Where they point:** a measured gap graduates to a [FINDINGS](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) row; several here would also settle a live [CONTRADICTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) row (§1→§1, §8→§2) or ride a method already sketched in [RECIPES](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md).

---

_Dr. Mārcis Gasūns_
