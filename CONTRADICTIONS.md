# CONTRADICTIONS — Sanskrit-data source disagreements with no verdict

_Created: 08-07-2026 · Last updated: 02-09-2026_

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
Status: ✅ **RULED 26-08-2026 (H3555, Tier 1): all three positions are correct — their scopes are disjoint, so the "self-contradiction" dissolves under word-class control.** Whole-corpus census of the accented RV (Zurich glossed corpus via the [vedaweb-data](https://github.com/VedaWebProject/vedaweb-data) mirror; 2,159 gen.pl tokens → 477 in `-ī/ū + nām` shape): **independent derivative ī/ū-stem NOUNS keep the stem accent 44/44** (nadī́nām ×20, tanū́nām ×15, rathī́nām ×2 … — §320/§356 confirmed, zero exceptions); **devī́-declension feminines of adjectives/participles — §319a's actual word class — genuinely vacillate** (~9 ending vs ~11 stem-final, with §319a's own `bahvīnā́m` attested ending-accented ×2); monosyllables shift 8/8 by the separate §355 rule; barytones never move (62/62); máh- is the one mixed lemma (4:1). D3 emission: **stem_final as a RULE for derivative ī/ū noun lemmas**; per-lemma variant reserved for the devī́-class and máh-. Full tables: [docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md) · [FINDINGS §587](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
Blocks: nothing any more — the D3 genitive-plural cell of the ZALIZNYAK_INDEX a–f accent emission is unblocked.
↔ Interlinks: [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (the n=2 scarcity) closed by the same pass — graduated to [FINDINGS §587](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) · probe script in [WhitneyRoots scripts/](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/d3_genpl_probe.py).
> **Source:** [FINDINGS §42](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#42-whitney-self-contradicts-on-derivative-ī-stem-genpl-accent) + [§54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents) · [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §2. Varga-diachrony: 2014 dissertation prose vs its own χ² table
🟠 ✍️ **The 2014 Gasūns dissertation prose labels as "gaining popularity" exactly the vargas its own χ² p-table shows as statistically unchanged.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| Gasūns-2014 prose (§2.6/П9) | labials/cerebrals/palatals "gaining" | [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards) |
| 2026 recompute (Cramér's V = 0.037) | those vargas near-stable; high p misread as growth | [varna_freq.csv](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Fonetika/regen-2026/varna_freq.csv) |
Status: 🟡 provisional pick — the 2026 shares + p-table AGREE against the 2014 prose; the prose is the error. **Adjudicated 26-08-2026 (H3538): pick CONFIRMED at Tier 2** — two independent derived surfaces (the 2026 recompute's shares and the dissertation's own χ² p-table) agree against the 2014 prose, and the error mode is mechanical (high p misread as growth); no counter-witness at any tier. Stays 🟡 only because the downstream Table 5 / П9 correction is a canonical-text change that parks for review — not because the verdict is in doubt.
Blocks: the GasunsDhatu 2026 §2.6 Table 5 / П9 correction (manifest `varga-series-diachrony`).
↔ Interlinks: [RECIPES §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (varga diachrony) is the reproducible pass whose χ² table the prose misread · [GAPS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) is the same epoch-stability question one layer down (collocations vs vargas) · [GLOSSARY "varga"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the unit in dispute.
> **Source:** [FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards) · [SanskritGrammar](https://github.com/gasyoun/SanskritGrammar)/[VisualDCS](https://github.com/gasyoun/VisualDCS) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §3. ✅ RESOLVED → kosha PLAN D13 — generated side is `forms`, not `inflections`
✅ **Tombstone (ruled 20-07-2026, H1366; accepted by MG).** The Concordance-Q3 plan set named two different kosha tables as the generated inflection side, "5× apart" — **ruled `forms` canonical**, and the "5× apart, same side" framing was itself a conflation. Measured against `kosha.db` (Opus 4.8 `claude-opus-4-8`) the two are **different data products**, sharing only **168,034 of 426,410** non-heritage `(form, lemma)` pairs, with `inflections` holding **3,246,914** pairs `forms` never has (`forms`: 1,378,401 rows, `source` split dcs/vidyut/heritage, no morphology; `inflections`: 6,917,018 rows, ~100% single-engine `cologne_mwinflect`, full morphology, no trust split). Grounds: pipeline continuity (W2a consumes W1b/A3, built on `forms`) + the `source` trust axis only `forms` carries + engine separation (W2a *generates* morphology via `vidyut.prakriya`). `inflections` reclassified as a distinct secondary asset / optional cross-check. Verdict recorded as [kosha PLAN §2 D13 + §3a](https://github.com/gasyoun/kosha/blob/main/docs/PLAN_KOSHA_CONCORDANCE_Q3_2026H2.md) (the repo-local decisions record); ARCHITECTURE §1 diagram mislabel corrected. W2a unblocked to consume `forms`.
↔ Interlinks: [FINDINGS §94](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) is the circularity finding (93% DCS-derived generated side) from the same A3 build.
> **Source:** surfaced by [H1262](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1262-Opus_kosha_a3_attested_form_join_morphology_audit_18.07.26.md); ruled by [H1366](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1366-Opus_kosha_generated-side-forms-vs-inflections-canonical-ruling_20.07.26.md) (accepted by MG) · [kosha](https://github.com/gasyoun/kosha) · [20-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-20&until=2026-07-21) · `claude-opus-4-8`

### §4. Grammatical `<ab>` abbreviations in pwg_ru: stay-Latin (10-07 ruling) vs translate-to-RU (19-07 DA-vote notes) — ✅ RULED
✅ ✍️ **The project's own abbreviation policy gave incompatible answers eleven days apart. MG ruled it 02-09-2026.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) (MG ruling 10-07-2026) | grammatical-category abbreviations (`Caus.`, `Aor.`, …) stay international Latin, tooltip only; only editorial/cross-reference ones translate | ABBREVIATIONS_RU § "Decision: grammatical-category abbreviations stay Latin" |
| h178_da vote notes (MG, 19-07-2026) | `Caus.` = `кауз.`, `Aor.` "нельзя не переводить"; only Latin abbreviations on a **ratified unified list** stay untranslated | [H178 DA-vote register §3 N5/N8](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md) |
Status: ✅ **RULED by MG, 02-09-2026**, on the [registry-contradictions vote sheet](https://gasyoun.github.io/vote/sheets/uprava_registry_contradictions_02-09-26.html) (3 cards, all approved, 120 s), verbatim:

> **«It's mixed. Some remain Latin, none remain German, most German become Russian and do not become Latin»**

That settles the fork in favour of the 10-07 two-bucket structure, not the 19-07 "translate everything on a ratified list" reading: grammatical categories (`Caus.`, `Aor.`, `Acc.` …) **stay international Latin**, so `Caus.` = `кауз.` from the 19-07 DA-vote notes is **not** adopted. The ruling adds one constraint neither document asserted — *none remain German* — and one direction correction: a Bucket-A editorial token goes to **Russian, never to Latin**. It needed no ratified unified list, which is why the 26-08 H3538 adjudication (correctly: human-gated, not agent-rulable) sat unresolved until a human voted.
Applied: [H3959](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3959-Opus_SanskritLexicography_ab-german-residue-ru-map_02.09.26.md) (Opus 5, 🟡2 medium) closed the residue the same day — the four-bucket census over all 272 distinct `<ab>` tokens, `RU_MAP` extended to 122 entries with an explicit `BUCKET_B` (138) and a declared `RESIDUE` (14 tokens / 18 occurrences), and `python pwg_ab_ru.py census` now failing on any token that renders raw German. Details: [ABBREVIATIONS_RU.md § Ruling 02-09-2026](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md).
Unblocks: [H1303](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1303-Fable_RussianTranslation_pwg-ru-abbrev-unified-list-ratification_19.07.26.md)'s store/prompt application and the V2 regeneration gate of [H1301](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1301-Opus_RussianTranslation_pwg-ru-review-sheet-ux-standard-regen_19.07.26.md). The three explicit sets in [`pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py) **are** the unified list H1303 was to ratify; graduating them to a `D##` is the remaining bookkeeping.
> **Source:** [H1300](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1300-Fable_RussianTranslation_h178-da-vote-processing_19.07.26.md) vote processing, 19-07-2026, Fable 5 (`claude-fable-5`).

## B. A claim overturned (or split) by machine-scale evidence
*A scholarly charge or a hand-picked exemplar checked against a full machine dataset — the count adjudicates.*

### §5. Krylov's 2014 Palsule-exclusion charge vs vidyut dhātupāṭha
🟠 ✍️ **The 2014 defense review charged the concordance keeps Palsule-only roots and drops Paninian ones; the machine dhātupāṭha only partly agrees.**
Positions:
| Source | Value | Evidence loc |
|--------|-------|--------------|
| Krylov 2014 review | `ast` is a Palsule-only intruder; `4añc` wrongly dropped | [FINDINGS §63](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#63-vidyut-dhātupāṭha-adjudicates-the-2014-palsule-exclusion-dispute-five-añc-dhātus-no-and-but-ast-is-paninian) |
| vidyut dhātupāṭha (2,259 dhātu) | `asta~` (10.0169) IS Paninian; `4añc` real+recoverable; no `and-` dhātu | [PALSULE_AUDIT.md](https://github.com/gasyoun/SanskritGrammar/blob/chore/errata-kochergina-waiting/GasunsDhatu_2014/revision-2026/PALSULE_AUDIT.md) |
Status: 🟡 provisional pick — vidyut adjudicates: Krylov right on `4añc`/`2and`, wrong on `ast`. **Adjudicated 26-08-2026 (H3538): pick CONFIRMED at Tier 1** — the vidyut dhātupāṭha is a canonical machine artifact and its entries directly witness the per-root split verdict; no counter-witness at any tier has appeared since the row was opened. The residual (amending the human-facing root notes) is an editorial change to reviewed text and parks for review rather than being applied by an agent.
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
Status: 🟡 provisional pick — a record-type/genre effect, not a per-dictionary convention; the corpus count wins. **Adjudicated 26-08-2026 (H3538): pick CONFIRMED at Tier 2** — the full-corpus classifier census (SKD 53.3 % / 46.7 %, VCP 77.6 %) is a derived artifact, but it subsumes the hand-picked single-lemma exemplar (n=1) on the same axis; an exemplar can never outweigh the census it belongs to. Any tighter ruling needs the per-record-type breakdown, which would be a new measurement, not a re-reading of the existing evidence.
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
Status: 🟡 provisional pick — the paper's numbers are canonical; either way the trend is flat and school-bound. **Adjudicated 26-08-2026 (H3538): pick CONFIRMED at Tier 2** — both runs are derived measurements; the paper's run supersedes the earlier pass by declared provenance, and both agree on the only load-bearing conclusion (flat, school-bound), so nothing downstream turns on the residual delta. No Tier-1 re-measurement is warranted unless a consumer starts citing the exact coefficient rather than the trend.
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

- **§13 ruled 01-09-2026 (H3793) by direct measurement**, once the file it needed stopped being a git-LFS pointer: 1,093,391 records, sha256-matched to the very oid the row had recorded. Both figures were true of two builds (the 2026-06-26 recompute vs the post-H309 re-harvest, +1,863 rows), and **A42 — the witness filed as losing — had documented that reconciliation in its own front-matter and claims table all along**. The lesson generalises: read the losing witness's provenance block before filing a pair as unreconcilable.
- **§4 ruled 02-09-2026 by a human vote, not by evidence** — the one row H3538 had correctly marked *human-gated, not agent-rulable*. MG's «some remain Latin, none remain German, most German become Russian and do not become Latin» kept the 10-07 two-bucket structure, rejected the 19-07 `Caus.` = `кауз.` reading, and added a constraint neither document had: *none remain German*. The lesson: an adjudication pass that returns "no agent ruling is possible" is not a dead end — it is a correctly-formed ask, and it sat unresolved for a week only because nobody put it on a sheet. Applied same day by [H3959](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3959-Opus_SanskritLexicography_ab-german-residue-ru-map_02.09.26.md).
- **Most rows are 🟡 provisional; §3, §4, §8, §10, §12 and §13 are ✅ ruled** — §10 (header-row off-by-one, both-true-under-scopes) and §12 (naive-sum stage split) were adjudicated 26-08-2026 in the H3538 wave-1 pass (Fable 5, `claude-fable-5`; verdict table: [docs/CONTRADICTIONS_ADJUDICATION_WAVE1_26-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/CONTRADICTIONS_ADJUDICATION_WAVE1_26-08-2026.md), which also states the evidence tier for every open row). The file is a holding pen for live disagreements awaiting a [`CROSS_REPO_DECISIONS`](https://github.com/gasyoun/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) `D##` verdict (or, where the contradiction is repo-local, that repo's own decisions record). A resolved contradiction leaves a one-line tombstone here and moves out. §3 (kosha `forms`-vs-`inflections`) was **ruled `forms` canonical** (H1366, accepted by MG), recorded as [kosha PLAN D13](https://github.com/gasyoun/kosha/blob/main/docs/PLAN_KOSHA_CONCORDANCE_Q3_2026H2.md).
- **A third shape, opened 01-09-2026 (§17): a policy statement contradicts a committed configuration.** Not two numbers but a stated posture ("a repo-wide Zenodo integration is deliberately not used") against the tree's own `.zenodo.json` + `CITATION.cff`, which show it live. No evidence tier can rule it — both sides are deliberate human policy — so it is logged and carried, per the [rights-uncertainty policy](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md), and it blocks only FAIR release #2.
- **Two recurring shapes.** A source contradicts *itself* (§1 Whitney across §319a/§356, §2 the 2014 prose against its own χ² table), or a small claim/exemplar is *overturned by machine-scale evidence* (§5 vidyut adjudicates Krylov, §6 the corpus classifier reverses the *dharma* exemplar, §7 the canonical run corrects the earlier one). The standing lesson mirrors ASSUMPTIONS: **trust the corpus count / χ² / vidyut table over prose intuition or a single hand-picked lemma.**
- **Renumbered 20-07-2026 (H1364).** §3–§8 previously carried duplicate/out-of-order keys (two rows both keyed `§6`; §3–§5 physically sat after §6/§7). Section keys now run strictly ascending top-to-bottom: §3 = Concordance-Q3 (was §6), §4 = grammatical abbreviations (was §7), §5 = Krylov/Palsule (was §3), §6 = SKD/VCP (was §4), §7 = sense-granularity (was §5), §8 = the Ch. 14 DOI ruling (new). No external file was found citing any of these by number (checked repo-wide + Uprava hubs) — only this file's own Conclusions section needed repointing.
- **The highest-value ruling was §1, and it landed 26-08-2026 (H3555)** — the full-corpus probe (n=2 → 44/44 nouns + a genuinely mixed devī́-declension class) ruled all three Whitney positions correct with disjoint scopes, closed [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md), and unblocked the ZALIZNYAK D3 accent emission. Verdict of record: [docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md).
- **Where they point:** a ruled row exits to [CROSS_REPO_DECISIONS](https://github.com/gasyoun/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) `D##`; the unmeasured evidence that would force a ruling lives in [GAPS](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md), and the reproducible methods that adjudicate them in [RECIPES](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md).

---

### §9. Corpus kāṇḍas 6–7 are labelled "Southern (Leonov)" but their text is the Baroda critical edition

🔴 ✍️ **The same two files are consumed as the Southern recension and align, verse for verse, to the critical one.**

Positions:

| source | value | evidence loc |
|---|---|---|
| `build_ramayana_concordance.py` `SOUTHERN_FILES` + the `COVERED_TEXTS_RU.md` census | `06`/`07_ramayana-*kanda.jsonl` are the Southern recension, Leonov's translation-of-record keying | [builder](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py) |
| the files' own text | kāṇḍa 7: 2,688 of 2,690 verses pair with the DCS **critical** edition at the *identical* `sarga.verse`, 95.5% at score 1.0; kāṇḍa 6: 99.8% identity — against 1.2–3.0% for kāṇḍas 1/2/3/5 | [`ramayana_southern_critical_concordance.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_southern_critical_concordance.tsv) |
| the files' `seg` census | kāṇḍas 6 and 7 carry **0** `ru` segments, so neither can be a translation-of-record keying at all | [FINDINGS §481](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) |

Status: 🟡 provisional pick — **adjudicated 26-08-2026 (H3538): the text wins over the label; kāṇḍas 6–7 are the critical edition.** Two independent Tier-2 measurements agree — the committed concordance (kāṇḍa 7: 2,688/2,690 verses pair with the DCS critical text at identical `sarga.verse`, 95.5 % scoring 1.0; kāṇḍa 6: 99.8 % identity — against 1.2–3.0 % for kāṇḍas 1/2/3/5) and the segment census (0 `ru` segments, [FINDINGS §481](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)) — while the "Southern" reading rests on a filename/constant label alone, which is Weak-tier evidence (naming; never carries a verdict alone). Verdict: the `SOUTHERN_FILES` designation for kāṇḍas 6–7 is a mislabel of critical-edition text. The relabel itself (builder constant, coverage census, concordance caveats) changes canonical corpus consumption, so it parks for a review sheet against [issue #822](https://github.com/gasyoun/SanskritLexicography/issues/822) rather than being applied here; the row stays 🟡 until that lands.

Blocks: (a) the committed Southern↔critical concordance is, for those two kāṇḍas, **a text aligned against itself** — its 99.8%/99.9% agreement must not be read as recension evidence; (b) any consumer treating `06`/`07` as vulgate-keyed inherits the silent recension swap [FINDINGS §468](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) documents for `R.` books 3–6; (c) it decides how a future Russian uttarakāṇḍa should be keyed ([GAPS §13](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)).
> **Source:** [H1705](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1705-Opus_SanskritLexicography_ramayana-bombay-book7-etext_26.07.26.md) · [integrity issue #822](https://github.com/gasyoun/SanskritLexicography/issues/822) · 27-07-2026 · Opus 5 1M `claude-opus-5[1m]`

### §10. Union headword total: 323,425 vs 323,426

🟠 ✍️ **Two committed row counts for the same union asset, one row apart, with no document explaining the difference.**

Positions:

| Source | Value | Evidence loc |
|---|---|---|
| SanskritLexicography surfaces ([FINDINGS §29](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md), [HEADWORDLISTS_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md), [ch03](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch03_headword_inventory.md)) + kosha's own [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `union-headwords` row | **323,425** | post-fold `build_union.py` output |
| [kosha/README.md](https://github.com/gasyoun/kosha/blob/main/README.md) (twice) + three archived handoffs (H054, H105, H106) | **323,426** | kosha `lemmas` table load |
Status: ✅ **RULED 26-08-2026 (H3538) — both true under different scopes; the header row is the whole gap.** Tier 1, measured directly on the canonical asset: [union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) holds **323,426 physical lines**, of which **line 1 is a column header** (`slp1 · iast · n_dicts · dicts · gender · fem_fold`) and the file ends in a newline — so **data rows = 323,425**. Every 323,425 witness counts headwords; every 323,426 witness counts file lines (or reflects a header-inclusive load). The row's own off-by-one hypothesis is CONFIRMED. **The headword count of record is 323,425.** The kosha-side prose (README, H054/H105/H106) should read "323,425 headwords (323,426 file lines incl. header)"; that wording fix belongs to a kosha `[integrity]` pass, not this repo. Residual probe (optional, kosha-side only): `SELECT COUNT(*) FROM lemmas;` on a rebuilt kosha.db, to check whether the header was actually ingested as a row or merely counted. Local ruling per the §8 precedent — no `D##` graduation.
Blocks: any paper citing "the union" out of kosha inherits a figure that disagrees with the canonical asset by 1; A55's "323,425 rows" title-adjacent claim.
> **Source:** [H1871 methods report](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md) §3 row 1 · kosha `[integrity]` issue (same pass) · 31-07-2026 · Fable 5 `claude-fable-5`

### §11. kosha.db: manifest build vs live-build census disagree under one name

🟠 ✍️ **The kosha manifest and the org data census describe different kosha.db builds as if they were one database.**

Positions:

| Source | Value | Evidence loc |
|---|---|---|
| [kosha/data/manifest/datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) | 10 tables incl. `heritage_anchor` (185,803) · **6,917,018** inflections | manifest kosha.db row |
| [Uprava/DATA_LAYERS_CENSUS.md](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md) + [H687 census](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H687-Sonnet_kosha_koshadb-completeness-census_11.07.26.md) | live 05-07 build, **no** `heritage_anchor` · **6,916,522** inflections | census kosha.db row |
Status: 🔴 unresolved — a 496-row inflection gap plus a whole-table presence disagreement; needs one dated rebuild via `scripts/build_db.py` with per-table `COUNT(*)` published, then both surfaces repointed at it. **Adjudicated 26-08-2026 (H3538): INCONCLUSIVE — no ruling possible from documents alone.** Both surfaces are Tier-2 derived censuses of *different builds*, and no kosha.db build exists on this box to measure (no local copy; no SHADOW_ASSETS row). The already-named probe stands as the one discriminating act: one dated `scripts/build_db.py` rebuild with per-table `COUNT(*)` published, then both surfaces repointed. Missing evidence is INCONCLUSIVE, never PASS.
Blocks: [METHODS_HOW_WE_COUNT_A_TRADITION_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md) §2.8's rule that a kosha.db count names its build — currently impossible to follow, since the two published builds are not distinguished at their sources.
> **Source:** H1871 survey · kosha `[integrity]` issue (same pass) · 31-07-2026 · Fable 5 `claude-fable-5`

### §12. Petersburg-family naive sum: 285,799 vs 285,950

🟡 ✍️ **Two committed sums of the same four headword lists differ by 151 rows, unexplained.**

Positions:

| Source | Value | Evidence loc |
|---|---|---|
| [MODULES_OWNED.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/sanskrit_in_numbers/MODULES_OWNED.md) | **285,799** (vs de-duplicated 167,904, "+70.2 % inflation") | §naive-sum module |
| [WAVE1_SUMMARY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/sanskrit_in_numbers/WAVE1_SUMMARY.md) + [ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md) | **285,950** ("family (285,950 headwords)") | summary + roadmap |
Status: ✅ **RULED 26-08-2026 (H3538) — both figures are exact naive sums of the SAME now-2026 lists at two pipeline stages; the vintage/key-mixing hypothesis is REFUTED.** Tier 1, both identities verified by direct count: **285,799 = 106,054 (PWG) + 151,314 (PWK) + 28,431 (SCH)** — the per-dictionary union-ingested row counts that [MODULES_OWNED.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/sanskrit_in_numbers/MODULES_OWNED.md) itself publishes; **285,950 = 106,082 + 151,349 + 28,519** — the raw [now-2026](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/now-2026) export files' line counts (`wc -l` re-verified 26-08-2026; each equals its filename `N`). The 151-row gap is the union build's key collapse (PWG −28, PWK −35, SCH −88), not drift. The "+70.2 % inflation" headline is internally consistent — numerator and denominator both come from the union-ingested stage. Consumers: cite **285,799** beside union/de-dup figures, **285,950** when counting raw export lines, and name the stage either way. Local ruling per the §8 precedent — no `D##` graduation.
Blocks: the "naive sum vs union" inflation headline (+70.2 %) — its numerator is ambiguous by 151.
> **Source:** [H1871 methods report](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md) §3 row 9 · 31-07-2026 · Fable 5 `claude-fable-5`

### §13. corpus_lexicon row count: 1,093,391 vs 1,091,528 — ✅ RULED

🟡 ✍️ **The hub/roadmap figure and the A42 paper figure for the same 3-layer glossary differ by 1,863 rows.**

Positions:

| Source | Value | Evidence loc |
|---|---|---|
| [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) + [heritage_frequency_diff.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_frequency_diff.md) | **1,093,391** | census rows |
| [A42_corpus_lexicon_resource.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A42_corpus_lexicon_resource.md) | **1,091,528** | paper §data |
Status: ✅ **RULED 01-09-2026 (H3793) — both figures are true of two BUILDS of the same file, and the gap was never unexplained: A42 itself documents it. The count of record is 1,093,391.**

Tier 1, measured directly on the canonical asset. The 26-08-2026 blocker is gone: `RussianTranslation/src/corpus_lexicon.jsonl` **and** the `pwg-ru-data/corpus/` twin are both present as real 290,543,363-byte files (no longer a 134-byte pointer), are **byte-identical to each other**, and hash to `sha256:9f3d852f1f1424c275af2cc1823dab1b561e649320e597d3cab013068ccc4072` — the *exact* oid this row recorded from the LFS pointer it could not open. The object measured is therefore provably the one in dispute. It holds **1,093,391 records**: 1,093,391 newlines, **0 blank lines**, and the file **does end in a newline**, so the `wc -l` off-by-one trap that produced [§10](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) does not apply here — line count and record count coincide.

**What the two numbers are.** **1,091,528** = the **2026-06-26 recompute**. **1,093,391** = the build after the [H309](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H309-Sonnet_RussianTranslation_corpus-lexicon-reharvest-gaps_07.07.26.md) targeted gap re-harvest of 08-07-2026, which added **+1,863 rows across a 780-group affected population**. 1,093,391 − 1,091,528 = 1,863 exactly. Same shape as [§12](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md): two stages of one pipeline, not two rival measurements.

**The row's own "unexplained" premise was the error.** [A42](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A42_corpus_lexicon_resource.md) — filed here as the losing witness — states the reconciliation in two places of its own: its `data_source:` front-matter ("1,091,528 alignments at the 2026-06-26 recompute; 1,093,391 after the H309 targeted re-harvest of 08-07-2026") and claims-table row 2 ("Post-H309 build size — 1,093,391 rows (+1,863 in the 780-group re-harvest population) — ✅ committed"). The [H1871 methods report](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md) §3 row 15 propagated "unexplained" without reading that table, and this row inherited it. **Standing lesson: before filing a figure pair as unreconcilable, read the losing witness's own provenance block — the reconciliation is sometimes already in it.**

**Consumers:** cite **1,093,391** and name the build. A pre-H309 analysis legitimately keeps 1,091,528 *provided it says so* — the coverage and traceability findings below were genuinely run on the 06-26 build and are not wrong, only unstamped; they carry the build name as of this pass.

Blocks: **nothing — fully closed 02-09-2026.** The measurement side was settled 01-09; the one publication-facing residual (A42 leading with the superseded 1,091,528 while its own front-matter carried 1,093,391) was an authorial choice, so it was put to a human and **MG ruled «count of record» on 02-09-2026**. Applied the same pass: A42's abstract, claim 1, §4.1 headline row and claims-table row 2 now lead with **1,093,391**. The §4.1–§4.3 distributional breakdowns are **deliberately left at the 1,091,528-row 2026-06-26 measurement and labelled as such** — the `kind` split (990,499 + 101,029) sums to that build, and rescaling a distribution to a total it was never computed over would have manufactured a second, subtler inconsistency in the course of fixing the first.
> **Source:** filed from the [H1871 methods report](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md) §3 row 15 · 31-07-2026 · Fable 5 `claude-fable-5`. Adjudicated INCONCLUSIVE 26-08-2026 (H3538, Fable 5 `claude-fable-5`). **Ruled 01-09-2026 by direct measurement — [H3793](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3793-Opus_SanskritLexicography_statistics-org-census-q2-analytical-layer_31.08.26.md), Opus 5 `claude-opus-5[1m]`.**

### §14. ls-citation-graph MW lane: CANON-CORE builds on it, CITE-4AXIS rejects it as an artifact-generator

🟠 ✍️ **Two July csl-atlas promotions, one day apart, license opposite readings of the same committed file.**

Positions:

| Source | Value | Evidence loc |
|---|---|---|
| [citation_canon.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json) (CANON-CORE, 07-07-2026) | the ls-graph's 11-dict × 912-text matrix — **including MW's lane (5 resolved texts**, two of them category labels) — is a valid topology-test substrate; headline "608/912 texts private, none cited by all 11" | artifact `matrix`/`perDict`/`interpretation`; MW under-representation acknowledged only in `limitations` |
| [four_axis_citation_independence.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/four_axis_citation_independence.json) (CITE-4AXIS, 08-07-2026) | the same file's MW lane "measures resolver coverage, not canon shape" (top MW abbreviations MBh./R./BhP. unresolved; BEN~MW cosine 0.0 is an artifact) — **rejected** as primary citation-vector source | artifact `citationVectorSource.whyNotLsGraph` |
Status: 🔴 unresolved — both packets are internally honest, but CANON-CORE's "none by all 11" sub-claim is partly mechanical given MW's 5-text lane (a text in all 11 would have to be among MW's 5). Resolution path: re-run the canon topology test with MW dropped (10-dict matrix) or fed from the citation-apparatus matrix (MW fully resolved: 320,828 tagged citations); if the modular verdict holds — expected, the 10 well-resolved lanes carry it — graduate with a "direction robust, MW sub-claims resolver-shaped" ruling. **Adjudicated 26-08-2026 (H3538): INCONCLUSIVE at ruling strength — the named probe has not run, and only it can rule.** What *can* be ruled now, at Tier 2 on the packets' own declared inputs: both packets are honestly scoped, and the "none cited by all 11" sub-claim is **partly mechanical** given MW's 5-text resolver lane, so it must carry the resolver qualifier wherever quoted until the 10-dict (or apparatus-fed) re-run lands. Missing evidence is INCONCLUSIVE, never PASS.
Blocks: quoting CANON-CORE's "none cited by all 11" in A50 §4 or any paper without the resolver qualifier; the H1866 referee pass added the caveat to the [HYPOTHESIS_INDEX row](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_INDEX.md) in the same pass.
> **Source:** [H1866 referee report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/HYPOTHESIS_PROMOTIONS_JULY_2026_REFEREE.md) §Contradiction · 05-08-2026 · Fable 5 `claude-fable-5`


### §15. `nominal_batch_worklist.json`: one audit calls it a NOT-A-RISK regenerable worklist, the other shows it cannot be rebuilt at all

🟠 ✍️ **Two in-repo audits grade the same gitignored file oppositely, and the optimistic one is the better known.**

Positions:

| Source | Value | Evidence loc |
|---|---|---|
| [CONCURRENCY_REAUDIT_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CONCURRENCY_REAUDIT_2026-07-09.md) (09-07-2026) | `verb_batch_worklist.json` / `nominal_batch_worklist.json` — "LWW (advisory) — **NOT-A-RISK** — Regenerable worklists." | concurrency table row |
| [H963 C4 call graph](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_PIPELINE_CALL_GRAPH_2026-07-16.md) row D7 (16-07-2026) | "Regenerable only where FOUR external inputs coexist … **In a clean worktree it is NOT regenerable.**" | D7, deviations table |

Status: 🟢 **resolved 28-08-2026 (H3627) in favour of D7**, which names its four inputs (the gitignored store, `scale_manifest.freq.json`, out-of-repo `csl-orig/v02`, out-of-repo `VisualDCS`) while the re-audit asserts regenerability without a rebuild test. The re-audit is also narrower than it reads: it grades *concurrent-write* risk (last-writer-wins between two lanes), not *recoverability* after a write. Both can hold — a lost race is survivable only if the loser can rebuild, and D7 shows it often cannot. H3627 fixed the mechanism rather than the prose: [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py) gained `--out`, so a non-default run no longer touches the shared file at all.

Blocks: quoting the "NOT-A-RISK / regenerable" grade as licence to overwrite either worklist. Four consumers read the nominal path (FINDINGS §592); treat both worklists as shared singletons until the re-audit row is amended.

> **Source:** [reports/H3627_TM_MIRROR_REFRESH_REINGEST_QUEUE_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3627_TM_MIRROR_REFRESH_REINGEST_QUEUE_28-08-2026.md) · 28-08-2026 · Opus 5 `claude-opus-5`


### §16. Style-guide §12.2 says never translate an apparatus span; the independent gate rewards translating one, because the span is a clause fragment and not apparatus

| Source | Value | Evidence loc |
|---|---|---|
| Ratified style guide [§12.2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md) (✅ principle, H2876) | A span consisting ENTIRELY of apparatus is **never** translated as a gloss; `sanskrit_util.classify_german_metalanguage` classes bare `mit` as `function_word`, so `{%mit%}` → «с» is forbidden | detector call in [`src/pwg_tm_serious10_translate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_serious10_translate.py) `whole_span_apparatus()` |
| H3628 independent re-score (Grok 4.5, 28-08-2026) | With `{%mit%}` → «с» the `upakrama` row scores `none` / fidelity **pass**; with the German kept per §12.2 the same row scores `german_residue` / fidelity **fail** | [`pwg_ru/serious10/translated/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/serious10/translated) receipts, both runs |

The two do not actually disagree about `mit` — they disagree about **what the span is**. In PWG `upakrama` 4 the German reads `{#upopakramatvAdupadravasya#} {%weil%} {#upadrava#} {%mit%} {#upa#} {%beginnt%}` — one Śaṃkara clause, "because *upadrava* begins with *upa*", chopped into three `{%…%}` spans by the interleaved Sanskrit. `{%mit%}` is therefore a **fragment of a running clause**, not a standalone apparatus token, but §12.2's test ("is the whole span apparatus?") cannot see the difference: a one-word span containing only a preposition looks identical either way. Same root cause as [GAPS §18](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) — discontinuous glosses fragmented at markup boundaries.

Status: 🟡 **open — resolved in favour of the ratified rule for now.** H3628 keeps `{%mit%}` in German and does not translate it. The cost was measured, not guessed: projected fidelity 99.25 % → 99.00 %, still clear of the 98 % floor, so compliance costs 0.25 points and blocks nothing.

Blocks: nothing today. What a human should decide is whether §12.2 gains a carve-out for spans that are adjacent to `{#…#}` on both sides (i.e. clause fragments), or whether the fragmentizer is fixed first so the clause arrives as one span and the question disappears. The second is the better fix and is already written up as GAPS §18.

> **Source:** [pwg_ru/PWG_TM_W1_SERIOUS10_TRANSLATED_GATE_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TRANSLATED_GATE_28-08-2026.md) · [H3628](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3628-Opus_RussianTranslation_pwg-tm-w1-serious10-translate_28.08.26.md) (Opus 5 `claude-opus-5`). — SanskritLexicography · 2026-08-28


### §17. Repo-wide Zenodo archival: two governance docs say it is deliberately NOT used; the committed configuration says it is live and has minted 143 times

🔴 ✍️ **The repository's stated rights posture and its actual deposit configuration disagree, on a public surface.**

Positions:

| Source | Value | Evidence loc |
|---|---|---|
| [DATA_LICENSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DATA_LICENSE.md) (13-07-2026) and [data/FAIR_RELEASE_1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md) § "Why a manual deposit, not a GitHub→Zenodo webhook" | A repo-wide Zenodo/GitHub archival integration is **deliberately not used**, because archiving the whole repo "would sweep in content this repo does not have clear rights to redistribute" (untracked third-party scan PDFs). FAIR Release #1 is therefore a curated **file-level** deposit of two named TSVs — and its Status boxes are all still unchecked, i.e. that deposit was never made. | DATA_LICENSE.md § derived datasets; FAIR_RELEASE_1.md § rationale + § Status |
| [.zenodo.json](https://github.com/gasyoun/SanskritLexicography/blob/master/.zenodo.json) (`upload_type: software`, whole-repo description) + [CITATION.cff](https://github.com/gasyoun/SanskritLexicography/blob/master/CITATION.cff) | The repo-level integration **is live**: concept DOI `10.5281/zenodo.21306715`, with the in-file note "the Zenodo–GitHub integration is live and mints on release publish". 143 `v1.14x` tags have been cut. | `.zenodo.json` (added PR #920); `CITATION.cff` `doi:` + comment block |

Status: 🔴 unresolved — **not agent-rulable.** Both positions are deliberate human-authored policy statements about redistribution rights, not measurements, so no evidence tier can adjudicate between them; the discriminating act is a decision, not a probe. What *can* be stated at Tier 1 is that both are currently true of the committed tree simultaneously, and that the whole-repo record's own description asserts "Source dictionary texts are corrected upstream in `csl-orig` and are not redistributed here" — a narrower claim than the one `DATA_LICENSE.md` worries about (untracked scan PDFs, which a git archive would not carry in any case). That observation narrows the exposure; it does not settle the posture. Per the standing [rights-uncertainty policy](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md) this is **not a stop** — it is recorded once and carried.

Blocks: FAIR release #2 (Q2 WS2.5 of [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md)) — minting DOIs for a second dataset set while release #1's deposit and its rights rationale are both unsettled would publish the inconsistency. Resolution path (a human decides): either the repo-level integration is the intended posture, in which case `DATA_LICENSE.md` and `FAIR_RELEASE_1.md` are amended and the curated file-level deposit becomes redundant; or it is not, in which case the integration is disabled and the two-file deposit proceeds on the metadata already prepared.

> **Source:** [Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Q1_DELIVERY_AND_Q2_ANALYTICAL_LAYER_STATISTICS_CENSUS_01-09-2026.md) §3.1 · [H3793](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3793-Opus_SanskritLexicography_statistics-org-census-q2-analytical-layer_31.08.26.md) · 01-09-2026 · Opus 5 `claude-opus-5[1m]`


_Dr. Mārcis Gasūns_
