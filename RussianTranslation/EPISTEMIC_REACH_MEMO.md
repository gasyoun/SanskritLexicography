# Epistemic reach of a citation-resolved, corpus-linked PWG → Russian dictionary

_Created: 08-07-2026 · Last updated: 08-07-2026_

A repo-anchored research-agenda memo for [`RussianTranslation`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) (the `pwg_ru` PWG→RU/EN pipeline). It answers a two-part owner question — *what can a translated, `<ls>`-resolved, corpus-linked PWG actually answer, and what can it not?* — and turns the answer into a build agenda under four locked decisions taken this session:

1. **Genre = three namespaced taxonomies with a crosswalk** — DCS computational text-type · traditional Sanskrit philological (`kāvya`/`śāstra`/`śruti`/`smṛti`/`itihāsa`/`purāṇa`/`āgama`/`tantra`/`nāṭya`) · a library-science subject layer. Not one winner — map them.
2. **Three deliverables** — an LREC/ACL-style paper (sense-genre attribution + BLI-evaluated alignment lexicon), an OntoLex/LOD queryable dataset, and a `samskrte.ru` reader feature.
3. **WSD = full in-context token→sense tagging** (needs a trained model + a gold sense-annotated sample).
4. **Architecture = OntoLex-Lemon + a LiLa-style Lemma Bank as the spine.**

The dependency order that governs everything below: **LiLa/OntoLex spine → inventory + per-sense attestation substrate → in-context WSD last.** WSD cannot tag tokens to senses that are not yet addressable and evidence-graded; the spine is what makes the senses linkable.

**Provenance.** Authored by Opus 4.8 (`claude-opus-4-8`), 08-07-2026, after a full data-layer ground-truth sweep — several first-draft "net-new" claims were *corrected against reality* (OntoLex and per-sense dating already exist; see below). Anchored on the [RENOU H1–H7 programme](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_HYPOTHESES.md) + [findings F1–F6](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_FINDINGS.md), [`USE_CASES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md), [`REUSE_MAP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md), the per-sense card schemas in [`schemas/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/schemas), the existing [`research/ACL_ANTHOLOGY_MONITOR.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ACL_ANTHOLOGY_MONITOR.md) lit-tracker, and the parent [`ROADMAP_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_2026_2027.md) (paper pipeline P1–P6, FAIR gaps G1–G8).

---

## 1. Executive summary — the five highest-leverage moves

1. **Upgrade the existing flat OntoLex/TEI export into a real LOD graph and interlink it to a LiLa-style Lemma Bank.** [`release/ontolex.ttl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/ontolex.ttl) (726k lines, populated) and `release/tei_lex0.xml` already exist via [`src/export_interop.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_interop.py) — but with a **placeholder IRI namespace** (`example.org`), string-only `ontolex:usage`, no `vartrans` sense-links, no PROV-O evidence, and no query surface. The move is real IRIs + `vartrans` + PROV-O grades + LiLa lemma link + a SPARQL endpoint. This is the foundation; everything else becomes a *view* over it. *[backlog #1]*
2. **Evaluate `corpus_lexicon.jsonl` as bilingual lexicon induction** with P@1/MRR against a frozen gold Sa→Ru set — the 1.09 M-pair asset is *consumed everywhere and measured nowhere* (grep for `P@1`/`MRR` returns zero hits). One evaluation makes it citable and bounds its reliability. *[backlog #2]*
3. **Lift sense-genre attribution from lemma to sense.** DCS genre is joined **per lemma today** (`dcs_freq_dims.json`) — exactly the W4 gap. The per-sense `<ls>` in [`assembled_cards.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/assembled_cards.jsonl) (120,173 cards) → works → genre gives the *primary* per-sense lane; DCS per-lemma genre becomes the second, frequency-weighted lane. This is the paper's headline and the portal's data source in one. *[backlog #3]*
4. **Build the multi-taxonomy genre crosswalk with inter-taxonomy κ.** MG ruled 08-07-2026 that the library-science lane is **three anchors, each with a distinct job** — **УДК/UDC** (Russian libraries + `samskrte.ru`), **LCSH** (WorldCat + LOD URIs at [id.loc.gov](https://id.loc.gov/authorities/subjects.html)), and a **bespoke indigenous spine modelled on the [New Catalogus Catalogorum](https://en.wikipedia.org/wiki/New_Catalogus_Catalogorum)** (NCC) *viṣaya*/śāstra arrangement. The NCC spine *becomes* the authoritative indigenous lane, upgrading the coarse traditional buckets derivable from [`ls_source_map.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json); DCS text-type stays the computational lane (`dcs_freq_dims.json`). The crosswalk is thus **DCS × NCC-indigenous × UDC × LCSH**, κ pairwise — NCC as fidelity anchor, UDC + LCSH as the two interoperability anchors. Measuring agreement empirically answers "can we use several?" — yes, and the disagreement cells are the finding. *[backlog #4]*
5. **Ship the `samskrte.ru` entry-portrait feature** — headword → sense cards, each with a genre badge, corpus attestation, Russian gloss, stratum label, and an RDF export link — as the public face of the graph. *[backlog #6]*

WSD (token→sense) is move 7, deliberately last: it is the most ambitious, needs a trained model, and is the only item gated on a second annotator.

---

## 2. What the dictionary *can* and *cannot* answer (the framing)

Reach comes from four axes being simultaneously machine-readable — **headword → sense → citation (→ work → genre) → Russian gloss** — plus a frequency lane (DCS, per lemma) and a morphology lane (Zaliznyak / VedaWeb, [`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)). Critically, `<ls>` citations sit **per sense** in each card, and per-sense **dating** already exists as a Renou-stratum span in [`pwg_sense_stratum.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sense_stratum.jsonl) (23,461 senses: oldest/youngest state, `stratum_label`, date min/max, dated-citation count). Per-sense Russian translation exists in `pwg_ru_translated.jsonl` (11,261 subcards, with `equivalence_type`/`stratum`/`differentia`).

**Can answer (buildable on committed data):**
- Sense-by-sense Russian meaning with the German original alongside (translation-drift auditable).
- Reverse dictionary Ru→Sa off the gloss layer; synonym clusters by shared gloss.
- Which works are cited for a headword *and for which sense*, resolved to scan pages via [`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py).
- Which senses are attested in `kāvya` vs `śāstra` vs `śruti` (W4), under three taxonomies.
- **Relative sense chronology** via the Renou stratum span per sense (Vedic → classical), and which senses are the oldest/youngest on a headword.
- DCS frequency of a lemma; frequency-weighted sense ranking; the corpus-absent "ghost-headword" census.
- Böhtlingk–Roth's own citation profile and its inheritance into MW (RENOU H5).

**Cannot answer (out of reach without a new model or external data):**
- **In-context sense disambiguation** — the dictionary lists senses; tagging a running-text token to one is a *model*, not a lookup (this is why WSD is scoped net-new, decision 3). The only prior mention is a lit note in [`LITERATURE_FOR_PWG_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LITERATURE_FOR_PWG_RU.md); no code exists.
- **Absolute / fine sense dating** — the Renou stratum gives a *relative* era span from dated `<ls>`; it does not date a sense to a century or order two senses within one stratum.
- **Frequency outside DCS** — DCS is a sample; a zero is "unattested in DCS", not "nonexistent".
- **Modern etymology** — PWG carries the 1855–75 reading, not Mayrhofer/EWA (KEWA is a parked future add, [`REUSE_MAP.md` §5](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md)).
- **Consensus meaning where scholars disagree**; the unresolved `<ls>` residue and citation *correctness* (the resolver points at a page, it does not verify the citation).
- Register/pragmatics beyond genre proxy; cross-lingual (Tibetan/Chinese) equivalents; post-~1875 vocabulary.

The load-bearing line for the paper's introduction: the resource answers *"what senses exist, where are they cited, and in which era"* well, and *"which sense is live in this passage"* only after a WSD model is trained on the sense inventory it already structures.

---

## 3. New testable hypotheses

Seven, each citing its nearest existing ID and the delta that makes it new. Join key throughout is the SLP1 lemma (`key1`), or dict-siglum × headword for cross-dictionary joins.

### E1 — the alignment lexicon has a measurable BLI ceiling that degrades with polysemy
**Claim.** `corpus_lexicon.jsonl` evaluated as bilingual lexicon induction achieves P@1 above a most-frequent-translation baseline, and P@1 falls monotonically with a headword's PWG sense count. **Data.** [`corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py) (1,091,528 pairs) × a frozen 300-pair gold Sa→Ru set drawn from Kochergina agreement (κ-checked) — note the existing [`gold/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/gold) set is *translation-fidelity*, not BLI, so a new gold slice is required. **Method.** BLI P@1/MRR ([Glavaš et al. 2019](https://aclanthology.org/P19-1070/)); polysemy from per-sense card count. **Figure.** P@1-vs-polysemy scatter + headline P@1. **Research read:** first intrinsic evaluation of the asset — citable, and bounds every downstream signal that consumes it. **Learner read:** "how often does the automatic gloss match the dictionary?" is a learner's trust question. **Nearest ID + delta:** none — `corpus_lexicon` is a *signal* in [`corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md), never BLI-evaluated (grep confirms zero `P@1`/`MRR`). **Readiness:** data present; needs the gold slice (κ).

### E2 — sense-level genre predicts corpus survival better than lemma-level genre
**Claim.** A sense's genre profile (from its *own* `<ls>` → works → genre) predicts whether that sense is attested in the living DCS corpus better than the lemma's aggregate genre does. **Data.** Per-sense `<ls>` in `assembled_cards.jsonl` × [`ls_source_map.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json) (per-work genre/period/Renou) × `dcs_freq_dims.json` (per-lemma genre). **Method.** Two logistic models (lemma-genre vs sense-genre features) predicting DCS attestation; compare AUC. **Figure.** ROC pair + per-genre lift. **Research read:** validates the W4 thesis that per-sense citations are the right granularity — the DCS genre lane is per-lemma today, so this closes a real gap. **Learner read:** ranks a headword's senses by "still used vs antiquarian". **Nearest ID + delta:** RENOU **H4** / finding **F6** (citation bias) and roadmap **P2** (sense inheritance) work at lemma/register level; E2 moves the unit to the **sense** and reframes as prediction. **Readiness:** all inputs committed.

### E3 — in-context sense is predictable above the MFS baseline, and the genre prior helps
**Claim.** A DCS token's PWG sense is predictable from collocational context above a most-frequent-sense baseline, and the per-sense `<ls>`-derived genre/stratum prior of the host text improves accuracy. **Data.** DCS tokenized corpus × the per-sense inventory (`pwg_ru_translated.jsonl`) × a gold sense-annotated sample (≥200 tokens over ~30 polysemous high-frequency lemmas, double-annotated). **Method.** WSD in the [Raganato et al. 2017](https://aclanthology.org/E17-1010/) unified-evaluation shape; MFS baseline per [McCarthy et al. 2004](https://aclanthology.org/P04-1036/); report accuracy + κ. **Figure.** Confusion matrix + MFS-delta bar. **Research read:** the first Sanskrit dictionary-grounded WSD benchmark — LREC/ACL-grade. **Learner read:** "which of these five meanings applies *here*" is the most-requested reading aid. **Nearest ID + delta:** nothing exists — RENOU tags at lemma/register, never token→sense; the only prior trace is a lit note. **Readiness:** *gated* — needs the gold sample + a second annotator; the E2 substrate must land first.

### E4 — ghost headwords cluster by citation register
**Claim.** A measurable fraction of PWG headwords are corpus-absent, and absence is predicted by citation register — the lexicographers-only `<ls>L.</ls>` marker and the epigraphic/Jaina registers over-predict absence. **Data.** Full PWG headword set × `corpus_lexicon.jsonl` presence × register from the glossary `states`/`provenance` columns ([`glossaries/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/glossaries): `epigraphic_vocabulary.md`, `jaina_vocabulary.md`, `kavya_lexicon.tsv`). **Method.** Absence census + logistic model; report the `<ls>L.` odds ratio. **Figure.** Treemap of headwords by register, present vs absent. **Research read:** quantifies the "dictionary-only word" as a philological category with a predictor. **Learner read:** flags headwords a beginner will never meet in a real text. **Nearest ID + delta:** RENOU **H3** / finding **F2** measure *register-vocabulary Jaccard* (epig self-contained); E4 reframes as a **headword-level census over all of PWG** with a predictive model tied to `<ls>L.`. **Readiness:** inputs committed.

### E5 — three-way translation drift is systematic
**Claim.** The Russian gloss diverges from the German original systematically (sense-splitting, register normalization), and divergence is larger on headwords where PWG-ru and Kochergina disagree. **Data.** Per-sense `de_skeleton` vs Russian gloss (`pwg_ru_translated.jsonl`) vs Kochergina (`koch`, 29,177 records, [`REUSE_MAP.md` §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md)). **Method.** Alignment-based drift score (sense-count delta, gloss-length ratio, register shift) correlated with a PWG-ru↔Kochergina disagreement flag; the `pwg_ru_relationships.jsonl` restate/abridge typology feeds the sense-split axis. **Figure.** Alluvial de senses → ru senses → Kochergina. **Research read:** first measured PWG-de vs PWG-ru vs Kochergina drift — a translation-studies contribution. **Learner read:** surfaces where the Russian is interpretation, not mirror. **Nearest ID + delta:** none for `pwg_ru`; the mw_ru drift was never quantified. **Readiness:** inputs committed.

### E6 — the three genre taxonomies crosswalk with measurable, informative disagreement
**Claim.** The four genre/subject taxonomies — DCS computational, NCC-indigenous, UDC, LCSH — crosswalk above chance, and disagreement concentrates on boundary genres (`itihāsa`/`purāṇa`, `śāstra`/`tantra`). **Data.** Work list from `ls_source_map.json` (coarse traditional genre already per work) × `dcs_freq_dims.json` genre (DCS) × the NCC *viṣaya* subject per work × UDC codes × LCSH headings. **Method.** Pairwise inter-taxonomy κ ([Artstein & Poesio 2008](https://aclanthology.org/J08-4004/)); confusion matrix per pair. **Figure.** Chord / confusion matrix over the four lanes. **Research read:** empirically settles "use several?" — the disagreement cells *are* the finding (contested texts). **Learner read:** genre is a lens, not a fact. **Nearest ID + delta:** RENOU's 20-register lattice is *one* taxonomy; E6 is the multi-taxonomy crosswalk with κ *between* taxonomies. **Readiness:** the coarse traditional + DCS lanes are derivable; the NCC spine, UDC, and LCSH lanes are the labelling work. **Rights flag:** the NCC subject *scheme* (its category list) is a usable taxonomy, but bulk-ingesting NCC's per-work subject assignments is rights-sensitive and may lack a machine-readable source — route through `/license-gated-ingest` and confirm availability before auto-populating; else hand-map the scheme. Reconcile with `csl-atlas` semantic-field work to avoid a parallel taxonomy.

### E7 — the export upgrades to a real LOD graph and round-trips losslessly
**Claim.** The existing flat `ontolex.ttl` can be upgraded to a real LOD graph (proper IRIs, `vartrans` sense-links, PROV-O evidence grades, LiLa lemma-bank link) and round-tripped back with every per-sense `<ls>`, stratum, and evidence grade preserved. **Data.** [`release/ontolex.ttl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/ontolex.ttl) + [`pwg_ru_lexicographic_portrait.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_ru_lexicographic_portrait.schema.json). **Method.** Extend `export_interop.py`; lossless-round-trip assertion (the repo's re-glue byte-identity discipline applied to RDF); a federated SPARQL query as the acceptance demo, LiLa-style. **Figure.** Coverage table: card fields mapped / lossy / unmapped, before vs after. **Research read:** produces the "what the Petersburg apparatus needs that Lex-0/Lemon lacks" note (publishable) and closes roadmap **G2** properly (it is currently a one-way string export, not queryable LOD). **Learner read:** none directly — infrastructure; its learner payoff is the portal (V7). Flagged honestly, not padded. **Nearest ID + delta:** roadmap **G2** + the existing flat export; E7 is the LOD/LiLa upgrade, routed to `csl-standards`. **Readiness:** TTL + schema + generator committed; the upgrade is the work.

---

## 4. Visualisation proposals

Seven; repo stack = Matplotlib/SVG for paper figures (RENOU convention) + the existing [gasyoun.github.io/SanskritLexicography](https://gasyoun.github.io/SanskritLexicography) portrait site / `samskrte.ru` for interactive ones. At least one over an unsurfaced dataset (V1) and one diachronic (V6).

| # | Title | Home | Data + loader | Chart | Mockup | Research read | Learner read | Effort |
|---|---|---|---|---|---|---|---|---|
| V1 | **Sense × genre heatmap per headword** | `research/figures/reach/` + portal | per-sense `<ls>` (via [`_build_persense_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_build_persense_ru.py), prototype-only, **unsurfaced**) | heatmap, senses × 3 taxonomies | rows = senses of `agni`, cols = genres, cell = citation count | the W4 result made visible | "which meaning belongs to poetry vs ritual" | M |
| V2 | **BLI P@1 vs polysemy** | paper fig | E1 output | scatter + fit | x = sense count, y = P@1, downward trend | the reliability ceiling | trust curve | S |
| V3 | **Ghost-headword treemap by register** | portal | E4 census | treemap, present/absent split | big `<ls>L.` + epig blocks mostly "absent" | dictionary-only vocabulary at a glance | "you won't meet these" | M |
| V4 | **Translation-drift alluvial** | paper fig | E5 output | alluvial, 3 columns | de senses → ru senses → Kochergina, ribbons split/merge | where Russian reinterprets | German↔Russian honesty | M |
| V5 | **Genre-taxonomy crosswalk matrix** | paper fig + portal | E6 output | chord / confusion | three-way, hot cells on `itihāsa`/`purāṇa` | the "use several" answer | genre as lens | M |
| V6 | **Sense-survival streamgraph (diachronic)** | paper fig | `pwg_sense_stratum.jsonl` strata (I→II→III→IV) | streamgraph | Vedic senses narrowing, classical widening | flagship diachronic figure (LSC-framed) | which meanings are archaic | M |
| V7 | **Entry portrait (the `samskrte.ru` feature)** | `samskrte.ru` | full card + E2/E3 tags + stratum + RDF link | interactive card | headword → sense cards: genre badge · corpus freq · stratum · Russian gloss · "export RDF" | the public face of the graph | the actual reading tool | L |

V6 becomes an easy win — `pwg_sense_stratum.jsonl` already carries the strata, so the diachronic figure is a load, not a derivation. Any public push goes through `/publish-safety-check` first — the underlying stores are gitignored for rights reasons.

---

## 5. ACL-Anthology method crosswalk

Every method verified against a live ACL Anthology / W3C source this session (08-07-2026). Complements the repo's existing [`research/ACL_ANTHOLOGY_MONITOR.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ACL_ANTHOLOGY_MONITOR.md) tracker — new rows there should point back here.

| Method | Source | Applies to (committed data) | Enables | Repo's nearest today (gap delta) |
|---|---|---|---|---|
| **BLI evaluation** (P@1/MRR, strong baselines) | [Glavaš et al. 2019](https://aclanthology.org/P19-1070/); [Artetxe et al. 2019](https://aclanthology.org/P19-1494/) | `corpus_lexicon.jsonl` | E1, V2 | consumed as a signal, never evaluated — **no intrinsic metric** |
| **WSD unified evaluation** | [Raganato et al. 2017](https://aclanthology.org/E17-1010/) | per-sense inventory × DCS tokens | E3, V6 | **nothing** — no token→sense lane (lit note only) |
| **Predominant / MFS baseline** | [McCarthy et al. 2004](https://aclanthology.org/P04-1036/) | per-sense cards + `dcs_freq.json` | E3 baseline | frequency-weighting partial (RENOU H6); no MFS-as-baseline |
| **OntoLex-Lemon / LLOD** | [W3C 2016](https://www.w3.org/2016/05/ontolex/); [McCrae et al. 2017](https://elex.link/elex2017/wp-content/uploads/2017/09/paper36.pdf); [DBnary / Globalex 2020](https://aclanthology.org/volumes/2020.globalex-1/) | `release/ontolex.ttl` | E7, the spine | **flat one-way export exists**; missing `vartrans`, real IRIs, PROV-O, query surface |
| **LiLa lemma-bank interlinking** | [LiLa Lemma Bank (JOHD)](https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.145); [Lexicala→LiLa 2025](https://aclanthology.org/2025.ldk-1.21/) | SLP1 lemma spine | architecture (decision 4) | no interoperable lemma hub, no `rdflib`/SPARQL |
| **Inter-coder agreement (κ/α)** | [Artstein & Poesio 2008](https://aclanthology.org/J08-4004/) | every human-labelled sample | E1 gold, E3 gold, E6 crosswalk | translation-fidelity gold exists; no BLI/κ-between-taxonomy (roadmap G4/G5) |
| **Lexical semantic change detection** | [SemEval-2020 Task 1 (incl. **Latin**)](https://aclanthology.org/2020.semeval-1.1/) | `pwg_sense_stratum.jsonl` strata | V6, the diachronic frame | RENOU H1 survival is adjacent but not LSC-framed |

**What to adopt first, and why.** The LiLa lemma-bank + LOD upgrade, before any analysis. LiLa is the closest working analogue to what `pwg_ru` should become — a lemma-centric knowledge base linking a dictionary, a corpus, morphology, and citations through a shared lemma bank, published as queryable LOD. The repo already emits OntoLex/TEI *strings*; the gap is the *graph*. Adopting LiLa first means E1–E6 compute *over the graph* and publish *as the graph*, turning three deliverables into three views of one artifact: the paper reports metrics over the graph, the LOD dataset *is* the graph, `samskrte.ru` renders a query. SemEval-2020 Task 1's inclusion of Latin is the proof that classical-language diachronic work clears ACL review — directly relevant to V6.

---

## 6. New sections mining additional layers

- **Per-sense corpus-attestation section** (from `_build_persense_ru.py`, prototype → surfaced). *Claim → Evidence → Source:* each Russian rendering hangs under the PD sense it supports, cited to `corpus_lexicon` rows. *ETL:* generalize the four-word prototype (`agni`/`anya`/`akṣara`/`ananta`) to the frequency-window roots. *Owner:* this repo. *Reads:* per-sense usage evidence (research) / real example sentences under the right meaning (learner).
- **LOD/RDF graph section.** *Reuse + join:* SLP1 lemma → LiLa lemma bank; **owner = `csl-standards`** per boundary rules (exports live there). Routing contract, not an in-repo build.
- **Genre-crosswalk reference section.** *Source:* `ls_source_map.json` per-work genre + DCS + library-science. *Owner:* this repo labels; reconcile the traditional vocabulary with `csl-atlas` (M8/H4 semantic fields).
- **Accent/morphology module (VedaWeb).** Already specified in [`USE_CASES.md` §13](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md); the OntoLex spine gives it a home as a morphology module, not a sidecar.

---

## 7. Prioritised build backlog

Ranked by leverage. Build handoffs are *not* minted here except the umbrella [H350](https://github.com/gasyoun/Uprava/blob/main/handoffs/H350-Opus_RussianTranslation_epistemic_reach_lila_ontolex_wsd_08.07.26.md); individual items carry `H###` placeholder starters to mint when picked up.

| # | Item | Leverage | Effort | Depends on | Owner | Tier | Starter |
|--:|---|---|---|---|---|---|---|
| 1 | LOD-graph upgrade of `ontolex.ttl` + LiLa link (E7) | ★★★ foundation | L | — | csl-standards | Opus (architecture) | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H350-Opus_RussianTranslation_epistemic_reach_lila_ontolex_wsd_08.07.26.md and execute it.` |
| 2 | BLI evaluation of `corpus_lexicon` (E1) | ★★★ citable asset | S | gold slice (κ) | RussianTranslation | Sonnet | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-Sonnet_RussianTranslation_bli_eval_corpus_lexicon_DD.MM.YY.md and execute it.` |
| 3 | Sense-level genre attribution (E2) + V1 | ★★★ paper headline | M | #1 helpful | RussianTranslation | Sonnet | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-Sonnet_RussianTranslation_sense_genre_attribution_DD.MM.YY.md and execute it.` |
| 4 | Three-taxonomy genre crosswalk + κ (E6) + V5 | ★★ settles "use several" | M | library-science labelling | RussianTranslation + csl-atlas | Opus (labelling judgment) | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-Opus_RussianTranslation_genre_taxonomy_crosswalk_DD.MM.YY.md and execute it.` |
| 5 | Ghost-headword census (E4) + V3; translation drift (E5) + V4; survival streamgraph (V6) | ★★ | M | — | RussianTranslation | Sonnet | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-Sonnet_RussianTranslation_ghost_drift_survival_DD.MM.YY.md and execute it.` |
| 6 | `samskrte.ru` entry-portrait feature (V7) | ★★★ deliverable-3 | L | #1, #3 | samskrte.ru | Opus | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-Opus_samskrte_entry_portrait_feature_DD.MM.YY.md and execute it.` |
| 7 | In-context WSD benchmark (E3) + confusion matrix | ★★★ but gated | L | #1, #3, gold sample, 2nd annotator | RussianTranslation | Opus | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-Opus_RussianTranslation_wsd_benchmark_DD.MM.YY.md and execute it.` |

---

## 8. Deferred / out-of-scope appendix

- **Second annotator** for E3/E6 gold work — no candidate through 2026 per the standing deferral; E3 (WSD) is gated on it and stays last regardless of technical readiness.
- **KEWA/EWA etymology layer** — parked future add ([`REUSE_MAP.md` §5](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md)); would extend E5 to etymological drift; not scoped here.
- **OntoLex/LOD ownership** — belongs to `csl-standards`, not this repo (boundary contract); backlog #1 is a routing spec.
- **Library-science taxonomy choice** — ✅ **RESOLVED 08-07-2026 (MG): use all three** — УДК/UDC (Russian libraries), LCSH (WorldCat/LOD), and a bespoke indigenous spine on the New Catalogus Catalogorum *viṣaya* arrangement (which absorbs the coarse traditional lane as the authoritative indigenous taxonomy). See E6 and exec-summary move 4. Remaining sub-question is the NCC ingest rights/availability (build-time, routed to `/license-gated-ingest`), not the taxonomy set.
  - **⚠️ Competing recommendation surfaced same day (Sonnet 5 `claude-sonnet-5`, 08-07-2026) — flagged, not applied.** Judging the three lane options purely on the axis this lane exists for (LOD interoperability, not domain fidelity) argues *against* the bespoke/NCC leg: id.loc.gov gives dereferenceable SKOS URIs the OntoLex/LiLa spine needs and real Sanskrit-genre headings (Puranas, Vedas, Sanskrit poetry, Sanskrit drama, Hindu law); a bespoke NCC spine has no LOD identity until published+maintained (new bus-factor) and largely duplicates the traditional lane the memo already has (defeats the interop lane's own purpose). Recommendation would be **LCSH-primary + UDC-secondary, bespoke NCC dropped** — with the traditional lane (already domain-native) crosswalked directly to LCSH URIs in E6, rather than routed through a new bespoke NCC layer. **This directly conflicts with the "use all three" ruling above and is not self-resolving — a human should decide** whether to keep NCC (fidelity, but no LOD payoff and an ingest-rights risk already flagged) or drop it in favor of the leaner LCSH+UDC pair. Not escalated via `/decision-record` yet; do so if/when picked up.
- **Compound-length / VisualDCS-dependent** questions (RENOU H2) stay in VisualDCS; not re-scoped.

_Dr. Mārcis Gasūns_
