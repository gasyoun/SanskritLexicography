# CONTRADICTIONS — Sanskrit-data source disagreements with no verdict

_Created: 08-07-2026 · Last updated: 08-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS states *one* fact. This file holds the act FINDINGS cannot: **disagreeing** — ≥2 sources give incompatible values and no ruling has been made. The moment a contradiction is ruled, it **graduates** to a [`CROSS_REPO_DECISIONS`](https://github.com/gasyoun/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) `D##` (leave a one-line "→ D##, resolved" tombstone here). One of the seven episteme registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md); the full set is on the [episteme dashboard](https://gasyoun.github.io/SanskritLexicography/episteme/). Its infra twin is [`Uprava/CONTRADICTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md).

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

## B. A claim overturned (or split) by machine-scale evidence
*A scholarly charge or a hand-picked exemplar checked against a full machine dataset — the count adjudicates.*

### §3. Krylov's 2014 Palsule-exclusion charge vs vidyut dhātupāṭha
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

### §4. SKD/VCP citation-fusion direction: one-lemma exemplar vs corpus count
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

### §5. Sense-granularity: two runs disagree on the year-correlation
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

## Conclusions

- **Every row is 🟡 provisional, none ✅ ruled** — the file is a holding pen for live disagreements awaiting a [`CROSS_REPO_DECISIONS`](https://github.com/gasyoun/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) `D##` verdict. A resolved contradiction leaves a one-line tombstone here and moves out.
- **Two recurring shapes.** A source contradicts *itself* (§1 Whitney across §319a/§356, §2 the 2014 prose against its own χ² table), or a small claim/exemplar is *overturned by machine-scale evidence* (§3 vidyut adjudicates Krylov, §4 the corpus classifier reverses the *dharma* exemplar, §5 the canonical run corrects the earlier one). The standing lesson mirrors ASSUMPTIONS: **trust the corpus count / χ² / vidyut table over prose intuition or a single hand-picked lemma.**
- **The highest-value ruling is §1** — it blocks the ZALIZNYAK accent axis and is itself gated by [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)'s n=2 data scarcity; the two are one problem, and [RECIPES §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) is the pass that would break the tie.
- **Where they point:** a ruled row exits to [CROSS_REPO_DECISIONS](https://github.com/gasyoun/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) `D##`; the unmeasured evidence that would force a ruling lives in [GAPS](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md), and the reproducible methods that adjudicate them in [RECIPES](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md).

---

_Dr. Mārcis Gasūns_
