# CONTRADICTIONS — Sanskrit-data source disagreements with no verdict

_Created: 08-07-2026 · Last updated: 20-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS states *one* fact. This file holds the act FINDINGS cannot: **disagreeing** — ≥2 sources give incompatible values and no ruling has been made. The moment a contradiction is ruled, it **graduates** to a [`CROSS_REPO_DECISIONS`](https://github.com/gasyoun/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) `D##` (leave a one-line "→ D##, resolved" tombstone here). One of the seven episteme registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md); the full set is on the [episteme dashboard](https://gasyoun.github.io/SanskritLexicography/episteme/). Its infra twin is [`Uprava/CONTRADICTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates the **impact of leaving it unresolved**.
- **Origin marker:** ⚙️ auto (a crosswalk-mismatch script emitted this candidate) · ✍️ human (a session flagged it).

Then a `Positions:` table (source · value · evidence loc), a `Status:` line (🔴 unresolved · 🟡 provisional pick · ✅ → `D##`), a `Blocks:` line, and a `> **Source:**` line.

**Auto-seed:** [`seed_contradictions.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_contradictions.py) runs over existing crosswalks (`mw_roots`, `union_headwords`, DCS↔Whitney) — rows where two datasets keyed on the same `form_key()` carry different values become ⚙️ candidate contradictions.

---

## A. A source disagrees with itself
*Intra-source contradictions — one authority gives incompatible answers within its own pages.*

### §1. Derivative ī/ū-stem gen.pl accent (Whitney, internal)
🟠 ✍️ **Whitney's Grammar gives three incompatible answers for the same cell.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| Whitney §320 | tone NOT thrown forward onto ending | [FINDINGS §42](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#42-whitney-self-contradicts-on-derivative-ī-stem-genpl-accent) |
| Whitney §319a (RV) | "usually" shifts (`bahvīnā́m`) | same |
| Whitney §356 (own paradigm) | prints `rathī́nām, nadī́nām` (no shift) | same |
Status: 🟡 provisional pick — encode as a per-lemma variant, NOT a rule; §54 weakly favours `stem_final` but n=2.
Blocks: the D3 genitive-plural cell of the ZALIZNYAK_INDEX a–f accent emission.
↔ Interlinks: [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) is the n=2 data scarcity that keeps this unrulable — close that and this resolves · [RECIPES §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (Whitney accent validation) is the pass that measures which of the three answers the corpus supports.
> **Source:** [FINDINGS §42](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#42-whitney-self-contradicts-on-derivative-ī-stem-genpl-accent) + [§54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents) · [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §2. Varga-diachrony: 2014 dissertation prose vs its own χ² table
🟠 ✍️ **The 2014 Gasūns dissertation prose labels as "gaining popularity" exactly the vargas its own χ² p-table shows as statistically unchanged.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| Gasūns-2014 prose (§2.6/П9) | labials/cerebrals/palatals "gaining" | [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards) |
| 2026 recompute (Cramér's V = 0.037) | those vargas near-stable; high p misread as growth | [varna_freq.csv](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Fonetika/regen-2026/varna_freq.csv) |
Status: 🟡 provisional pick — the 2026 shares + p-table AGREE against the 2014 prose; the prose is the error.
Blocks: the GasunsDhatu 2026 §2.6 Table 5 / П9 correction (manifest `varga-series-diachrony`).
↔ Interlinks: [RECIPES §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (varga diachrony) is the reproducible pass whose χ² table the prose misread · [GAPS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) is the same epoch-stability question one layer down (collocations vs vargas) · [GLOSSARY "varga"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the unit in dispute.
> **Source:** [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards) · [SanskritGrammar](https://github.com/gasyoun/SanskritGrammar)/[VisualDCS](https://github.com/gasyoun/VisualDCS) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §3. ✅ RESOLVED → kosha PLAN D13 — generated side is `forms`, not `inflections`
✅ **Tombstone (ruled 20-07-2026, H1366; accepted by MG).** The Concordance-Q3 plan set named two different kosha tables as the generated inflection side, "5× apart" — **ruled `forms` canonical**, and the "5× apart, same side" framing was itself a conflation. Measured against `kosha.db` (Opus 4.8 `claude-opus-4-8`) the two are **different data products**, sharing only **168,034 of 426,410** non-heritage `(form, lemma)` pairs, with `inflections` holding **3,246,914** pairs `forms` never has (`forms`: 1,378,401 rows, `source` split dcs/vidyut/heritage, no morphology; `inflections`: 6,917,018 rows, ~100% single-engine `cologne_mwinflect`, full morphology, no trust split). Grounds: pipeline continuity (W2a consumes W1b/A3, built on `forms`) + the `source` trust axis only `forms` carries + engine separation (W2a *generates* morphology via `vidyut.prakriya`). `inflections` reclassified as a distinct secondary asset / optional cross-check. Verdict recorded as [kosha PLAN §2 D13 + §3a](https://github.com/gasyoun/kosha/blob/main/docs/PLAN_KOSHA_CONCORDANCE_Q3_2026H2.md) (the repo-local decisions record); ARCHITECTURE §1 diagram mislabel corrected. W2a unblocked to consume `forms`.
↔ Interlinks: [FINDINGS §94](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) is the circularity finding (93% DCS-derived generated side) from the same A3 build.
> **Source:** surfaced by [H1262](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1262-Opus_kosha_a3_attested_form_join_morphology_audit_18.07.26.md); ruled by [H1366](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1366-Opus_kosha_generated-side-forms-vs-inflections-canonical-ruling_20.07.26.md) (accepted by MG) · [kosha](https://github.com/gasyoun/kosha) · [20-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-20&until=2026-07-21) · `claude-opus-4-8`

### §4. Grammatical `<ab>` abbreviations in pwg_ru: stay-Latin (10-07 ruling) vs translate-to-RU (19-07 DA-vote notes)
🔴 ✍️ **The project's own abbreviation policy gives incompatible answers eleven days apart.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) (MG ruling 10-07-2026) | grammatical-category abbreviations (`Caus.`, `Aor.`, …) stay international Latin, tooltip only; only editorial/cross-reference ones translate | ABBREVIATIONS_RU § "Decision: grammatical-category abbreviations stay Latin" |
| h178_da vote notes (MG, 19-07-2026) | `Caus.` = `кауз.`, `Aor.` "нельзя не переводить"; only Latin abbreviations on a **ratified unified list** stay untranslated | [H178 DA-vote register §3 N5/N8](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md) |
Status: 🔴 unresolved — the 19-07 notes are later and more specific but explicitly delegate to a not-yet-existing ratified list; neither doc has been amended.
Blocks: [H1303](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1303-Fable_RussianTranslation_pwg-ru-abbrev-unified-list-ratification_19.07.26.md)'s store/prompt application, and the V2 regeneration gate of [H1301](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1301-Opus_RussianTranslation_pwg-ru-review-sheet-ux-standard-regen_19.07.26.md) benefits from the ruling landing first. Resolution path: H1303's inventory → per-token proposal → MG ratification sheet → graduate to a `D##`.
> **Source:** [H1300](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1300-Fable_RussianTranslation_h178-da-vote-processing_19.07.26.md) vote processing, 19-07-2026, Fable 5 (`claude-fable-5`).

## B. A claim overturned (or split) by machine-scale evidence
*A scholarly charge or a hand-picked exemplar checked against a full machine dataset — the count adjudicates.*

### §5. Krylov's 2014 Palsule-exclusion charge vs vidyut dhātupāṭha
🟠 ✍️ **The 2014 defense review charged the concordance keeps Palsule-only roots and drops Paninian ones; the machine dhātupāṭha only partly agrees.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| Krylov 2014 review | `ast` is a Palsule-only intruder; `4añc` wrongly dropped | [FINDINGS §63](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#63-vidyut-dhātupāṭha-adjudicates-the-2014-palsule-exclusion-dispute-five-añc-dhātus-no-and-but-ast-is-paninian) |
| vidyut dhātupāṭha (2,259 dhātu) | `asta~` (10.0169) IS Paninian; `4añc` real+recoverable; no `and-` dhātu | [PALSULE_AUDIT.md](https://github.com/gasyoun/SanskritGrammar/blob/chore/errata-kochergina-waiting/GasunsDhatu_2014/revision-2026/PALSULE_AUDIT.md) |
Status: 🟡 provisional pick — vidyut adjudicates: Krylov right on `4añc`/`2and`, wrong on `ast`.
Blocks: the GasunsDhatu 2014 revision's response to the ведущая организация review.
↔ Interlinks: [GLOSSARY "dhātupāṭha citation form"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the citation form the charge turns on · [ASSUMPTIONS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) is the parallel verb-root record premise the same dhātu data underlies.
> **Source:** [FINDINGS §63](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#63-vidyut-dhātupāṭha-adjudicates-the-2014-palsule-exclusion-dispute-five-añc-dhātus-no-and-but-ast-is-paninian) · [SanskritGrammar](https://github.com/gasyoun/SanskritGrammar) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §6. SKD/VCP citation-fusion direction: one-lemma exemplar vs corpus count
🟠 ✍️ **The hand-picked *dharma* exemplar's fusion direction reverses at corpus scale.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| *dharma* exemplar | SKD fuses citation into synonym-run; VCP keeps separate | [FINDINGS §43](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#43-skdvcp-sensecitation-fusion-is-a-record-type-effect-not-a-dictionary-level-one) |
| Full-corpus classifier | SKD 53.3%/46.7% even; VCP skews TOWARD fusion 77.6% | [r2_kosa_fusion.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json) |
Status: 🟡 provisional pick — a record-type/genre effect, not a per-dictionary convention; the corpus count wins.
Blocks: any "dictionary X marks citations this way" generalization from a single lemma.
↔ Interlinks: [ASSUMPTIONS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) is the same "a shared tag/convention means the same across dicts" premise this refutes at record-type level · [DEAD_ENDS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (sense-inheritance at corpus scale) is the sibling generalization that also failed when scaled up.
> **Source:** [FINDINGS §43](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#43-skdvcp-sensecitation-fusion-is-a-record-type-effect-not-a-dictionary-level-one) · [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

## C. Two runs disagree
*The same measurement, recomputed, gives two numbers — a reproducibility contradiction to reconcile before either is cited.*

### §7. Sense-granularity: two runs disagree on the year-correlation
🟠 ✍️ **Two runs disagree on the sense-count↔year correlation, and both refute the intuitive "senses grow over time" reading.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| paper canonical run | r = 0.036 over 1822–1957; family means 1.0–2.4 | [FINDINGS §27](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#27-sense-granularity-is-a-family-trait-not-a-diachronic-trend) |
| earlier `docs/R2_FINDINGS.md` run | r = 0.06, Benfey 2.53 | same |
Status: 🟡 provisional pick — the paper's numbers are canonical; either way the trend is flat and school-bound.
Blocks: any per-sense-normalized cross-dict metric that doesn't family-control.
↔ Interlinks: [DEAD_ENDS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (sense-inheritance at corpus scale) is the neighbouring sense-count claim that also collapsed · [GAPS §10](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) is the same "two independent passes disagree" reliability worry for a benchmark's gold.
> **Source:** [FINDINGS §27](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#27-sense-granularity-is-a-family-trait-not-a-diachronic-trend) · [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

### §8. The Ch. 14 correction-dataset DOI: false-and-unminted vs genuinely minted (BOOK_PLAN vs FAIR_RELEASE_1) — ✅ RULED
🟠 ✍️ **Two committed docs gave incompatible accounts of the same Zenodo DOI `10.5281/zenodo.15834721`; a live Zenodo check settles it.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| [BOOK_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md) (+ pre-18-07 revisions of the publication deep manual) | a **false DOI** resolving to an unrelated preprint; must be re-minted | BOOK_PLAN §rights |
| [data/FAIR_RELEASE_1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md) (H817, 13-07-2026) | the same DOI is csl-observatory's **genuinely minted** OBS-T dataset DOI | FAIR_RELEASE_1 §csl-observatory |
Status: ✅ **BOOK_PLAN is correct — `10.5281/zenodo.15834721` is a false DOI, not the OBS-T dataset's.** Live Zenodo check 20-07-2026 (H1364): the DOI resolves to *"A Non-Surgical and Unconditional Proof of Topological Sphericity via Entropy-Spectral Dynamics (v2.2)"* — an unrelated differential-geometry/topology preprint, deposited 08-07-2025, with zero connection to CDSL, csl-observatory, or the OBS-T correction-event corpus. `FAIR_RELEASE_1.md` §csl-observatory was wrong, and the same false DOI had also propagated into [csl-observatory's own `CITATION.cff`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/CITATION.cff) `identifiers:` block — both fixed same pass (H1364). No `CROSS_REPO_DECISIONS` `D##` graduation: that registry has never actually been used for a graduated contradiction (checked all three CONTRADICTIONS.md siblings 20-07-2026 — zero `D##` tombstones exist anywhere), so this ruling stays local rather than inventing the first entry in an unused scheme.
Blocks: — (unblocked) the FAIR/DOI sprint's re-mint decision: csl-observatory's OBS-T dataset has **no genuinely minted DOI yet** and needs a real Zenodo deposit; the correction dataset (Ch. 14/15) separately needs its own re-mint, as BOOK_PLAN already said.
> **Source:** H1245 estate refresh, 18-07-2026, Fable 5 (`claude-fable-5`) — surfaced by the publication-manual fact-check. Ruled: H1364, 20-07-2026, Sonnet 5 (`claude-sonnet-5`), live Zenodo fetch.

## Conclusions

- **Most rows are 🟡 provisional; §3 and §8 are ✅ ruled** — the file is a holding pen for live disagreements awaiting a [`CROSS_REPO_DECISIONS`](https://github.com/gasyoun/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) `D##` verdict (or, where the contradiction is repo-local, that repo's own decisions record). A resolved contradiction leaves a one-line tombstone here and moves out. §3 (kosha `forms`-vs-`inflections`) was **ruled `forms` canonical** (H1366, accepted by MG), recorded as [kosha PLAN D13](https://github.com/gasyoun/kosha/blob/main/docs/PLAN_KOSHA_CONCORDANCE_Q3_2026H2.md).
- **Two recurring shapes.** A source contradicts *itself* (§1 Whitney across §319a/§356, §2 the 2014 prose against its own χ² table), or a small claim/exemplar is *overturned by machine-scale evidence* (§5 vidyut adjudicates Krylov, §6 the corpus classifier reverses the *dharma* exemplar, §7 the canonical run corrects the earlier one). The standing lesson mirrors ASSUMPTIONS: **trust the corpus count / χ² / vidyut table over prose intuition or a single hand-picked lemma.**
- **Renumbered 20-07-2026 (H1364).** §3–§8 previously carried duplicate/out-of-order keys (two rows both keyed `§6`; §3–§5 physically sat after §6/§7). Section keys now run strictly ascending top-to-bottom: §3 = Concordance-Q3 (was §6), §4 = grammatical abbreviations (was §7), §5 = Krylov/Palsule (was §3), §6 = SKD/VCP (was §4), §7 = sense-granularity (was §5), §8 = the Ch. 14 DOI ruling (new). No external file was found citing any of these by number (checked repo-wide + Uprava hubs) — only this file's own Conclusions section needed repointing.
- **The highest-value ruling is §1** — it blocks the ZALIZNYAK accent axis and is itself gated by [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)'s n=2 data scarcity; the two are one problem, and [RECIPES §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) is the pass that would break the tie.
- **Where they point:** a ruled row exits to [CROSS_REPO_DECISIONS](https://github.com/gasyoun/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) `D##`; the unmeasured evidence that would force a ruling lives in [GAPS](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md), and the reproducible methods that adjudicate them in [RECIPES](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md).

---

_Dr. Mārcis Gasūns_
