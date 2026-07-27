# ASSUMPTIONS — unverified premises the Sanskrit-data pipelines rely on

_Created: 08-07-2026 · Last updated: 27-07-2026_ (H702 cheap-test sweep: §1–§4 re-verified with full local evidence — the §4 re-tally corrected the recorded no-PWG count ≈35,900→61,906 and §3 got a full-749-root census; §5–§7 annotated with concrete test costs; Fable 5 `claude-fable-5`, two passes) (27-07-2026, [H1476](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1476-Opus_SanskritGrammar_pedagogy-aspect-measurable-result-metrics_22.07.26.md): **category D — evaluation-threshold assumptions** added, §9/§10 — the first rows here about a *ruler* rather than about the data; Opus 5 1M `claude-opus-5[1m]`)

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS holds *measured, past-tense* facts. This file holds the act FINDINGS structurally cannot: **relying** on an unproven premise. An assumption is *depended-upon but unverified* — the moment its **Test** passes, it **graduates** to a FINDINGS row (delete it here, cite the finding there). One of the seven episteme registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md); the full set is on the [episteme dashboard](https://gasyoun.github.io/SanskritLexicography/episteme/). Its infra twin is [`Uprava/ASSUMPTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/ASSUMPTIONS.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates **blast radius**: 🔴 many downstream datasets/layers cascade if the premise is false · 🟠 one pipeline · 🟡 local.
- **Origin marker:** ⚙️ auto (a script emitted this candidate — a *candidate* until a human confirms) · ✍️ human (a session wrote it from judgment).

Then the premise as a claim, `Relied on by:`, `Verified?:` (❌ never · ⚠️ spot-checked once · ✅ → graduate to FINDINGS), `Test to confirm:`, an `↔ Interlinks:` line (how the premise ties into the other episteme docs), and a `> **Source:**` line.

**Categories** (below) group the premises by *what kind of thing is being assumed*, so a reader can scan by concern rather than by discovery order. **Auto-seed:** [`scan_assumptions.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/scan_assumptions.py) greps the code spine for `# ASSUMES:` / `# INVARIANT:` tags.

---

## A. DCS-corpus keying assumptions
*Premises about how the DCS corpus joins to the CDSL dictionaries — the join layer that every frequency/lemma pipeline sits on.*

### §1. DCS lemma == CDSL headword
🔴 ✍️ **Any join that treats a DCS corpus lemma as if it has a matching CDSL dictionary headword.**
Relied on by: `dcs_cdsl_xref.tsv` (kosha manifest `dcs-cdsl-xref`), `build_xref.py`, the kosha frequency LEFT-JOIN, Sa→Ru glossary form→lemma resolution.
Verified?: ✅ refuted as a universal, twice-measured — 11-06-2026 (n=15,902): 81.4% link; **re-verified 12-07-2026 (H702, full `in_cdsl` recount): 12,945/15,902 linked = 81.4%, 2,957 unlinked (18.6%)** — the bound is stable; the measured fact lives at FINDINGS §12, this row stays as the do-not-assume guard.
Test to confirm: recount linked/total in [`dcs_cdsl_xref.tsv`](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/dcs_xref/dcs_cdsl_xref.tsv); any pipeline assuming 100% coverage silently drops ~1/5 of corpus vocabulary.
↔ Interlinks: [RECIPES §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) reproduces the 81.4% number that bounds this premise · [GLOSSARY "headword vs lemma"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the distinction this assumption blurs · the unlinked 18.6% is the frontier next to [GAPS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (Heritage as a third witness).
> **Source:** [FINDINGS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword) · [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §2. One transliteration scheme keys all DCS files
🔴 ✍️ **A frequency/lemma join can assume a single transliteration across the DCS-derived files.**
Relied on by: `freq_route.py`, any join between `VisualDCS/dcs_lemma_summary.json` (SLP1) and `RussianTranslation/src/dcs_lemma_renou.json` (IAST).
Verified?: ✅ refuted, re-verified 12-07-2026 (H702) — `dcs_lemma_summary.json` lemma map = SLP1 (83,239 keys, zero non-ASCII); `dcs_lemma_renou.json` = IAST (90,346 keys, e.g. `abadhyamāna`). Schemes still differ; transcode via `sanskrit-util` before any join.
Test to confirm: diff a sample of keys across both files; a raw string join misses every non-ASCII-coincident lemma unless one side is transcoded via `sanskrit-util`.
↔ Interlinks: [GLOSSARY "SLP1 vs IAST"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) is the term this premise trips over · [DEAD_ENDS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) is the *wrong* way to bridge schemes (NFD+strip) · [RECIPES §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) shows the transcode-then-join done right.
> **Source:** [FINDINGS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#7-dcs-lemma-data-is-keyed-in-two-transliterations) · [VisualDCS](https://github.com/gasyoun/VisualDCS)/[RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §8. A lemma's declension class can be read off its citation form
🟠 ✍️ **Any grouping of DCS nominals by "stem type" / "declension class" — the corpus carries no such tag.**
Relied on by: SanskritGrammar's Sangram G2 asset (`stem_final` in [`sg_g2_declension_cell_coverage.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/scripts/sg_g2_declension_cell_coverage.py), FEATURES_INDEX **E52**) and, reusing the same tag list, VisualDCS' nominal case×number grid (**E51**) and the declension articles SG-MO-001/002/006/010.
Verified?: ⚠️ **unverifiable as stated, and known false at the edges** — DCS tags case, number and gender only, so the class is inferred from the last one-to-three characters of the citation form. Two failure modes are measured rather than assumed: the master cites the *same* stem two ways (`bhagavant` and `bhagavat` are separate `lemma_id`s, both genuinely `-ant`), and one orthographic bucket holds two paradigms (`-ī` pools devī-type with monosyllabic śrī-type). Both are recorded, not silently split — see [GAPS §13](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md).
Test to confirm: re-run the G2 reconciliation in [`gen_paradigm_nominal.py`](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/gen_paradigm_nominal.py) — it must stay at 57,144 lemma_ids matched / 0 disagreements, with the only re-bucketing being the documented `-ant` extension (279 lemma_ids). A drift there means one of the two taxonomies moved without the other.
↔ Interlinks: the class taxonomy is shared across two repos, so this premise is also a *sync* hazard — [FINDINGS §482](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) covers the companion denominator trap in the same layer.
> **Source:** [H1048](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1048-Opus_SanskritGrammar_sangram-g2-declension-cell-coverage_16.07.26.md) (taxonomy) · [H1472](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1472-Opus_VisualDCS_nominal-paradigm-case-number-dashboard_22.07.26.md) (reuse + reconciliation) · 27-07-2026 · `claude-opus-5[1m]`

---

## B. Dictionary-record-structure assumptions
*Premises about how a dictionary's records are laid out — what a walk over them will reach.*

### §3. A dict's giant verb root lives at homonym index 0
🔴 ✍️ **A per-record split can read `bufs[0]` and assume the first homonym record holds the verb root.**
Relied on by: `gen_root_split()`, any PWG root-portrait/segmentation walk over homonym records.
Verified?: ✅ refuted, re-verified 12-07-2026 (H702) — `audit_root_split.py` re-run over 60 giant roots: non-zero-index giants persist (√gam [0,2,3], √kzip [0,2], √aS [0,1]); the split path now correctly iterates all homonym records. Original 24-06-2026 sample: 19/50 at index > 0. Full-population census (H702 second pass, same day, all 749 DCS-attested verb roots): 236 giant roots; **55 (23.3%) hold a giant homonym at index > 0, and 23 have NO giant at index 0 at all** — recorded in FINDINGS §16.
Test to confirm: re-run [`audit_root_split.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_root_split.py); iterate ALL homonym records, never `bufs[0]`.
↔ Interlinks: [GLOSSARY "homonym index"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the ordinal this premise mis-assumes · [GAPS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (homonym token frequency) is what stays unreachable while this holds.
> **Source:** [FINDINGS §16](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#16-giant-verb-roots-sit-at-non-zero-homonym-indexes) · [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) (pwg)/[RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §4. A worklist built by iterating PWG keys covers the local layer universe
🔴 ✍️ **Enumerating "headwords" by walking PWG records reaches the whole pwg_ru merge universe.**
Relied on by: the verb-root worklist (`verbs01`/PWG), any pwg_ru queue builder.
Verified?: ✅ refuted, re-tallied 12-07-2026 (H702 second pass, full `dict_merge.py` tally re-run) — **61,906 of 167,988 headwords (36.9%) carry ZERO PWG record**; PW-only alone = 40,338 (24.0%), reproduced exactly. The "≈35,900" this row carried from the 05-07-2026 tally was an arithmetic slip (the measured combinations sum to 61,906) — corrected here, in FINDINGS §64 and in PWG_LAYER_COMBINATIONS.md the same pass. Re-run only when the merge universe changes.
Test to confirm: re-run the `dict_merge.py` index tally in [`PWG_LAYER_COMBINATIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md); PW/SCH/PWKVN-only entries need their own queue path.
↔ Interlinks: [RECIPES §5](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (union headword index) is the asset that *measures* the true universe this premise underestimates.
> **Source:** [FINDINGS §64](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#64-pw-only-headwords-outnumber-pwg-only-ones-6-to-1-pwg-is-not-the-sole-spine-of-the-local-layer-universe) · [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## C. Cross-dict & temporal-validity assumptions
*Premises that a symbol means one thing across dictionaries, or that a measurement stays true over time.*

### §5. A shared markup tag means the same thing across dicts
🟠 ✍️ **The same `<ab>` / marker tag carries one meaning that can be counted dict-agnostically.**
Relied on by: any cross-dict tag-count survey (etymology detectors, `<ls>` density rankers, marker-based structure detectors).
Verified?: ⚠️ spot-checked once (26-06-2026) — `<ab>E.</ab>` = Etymology in WIL but "Epithet of" in CAE, "Epic" in MD; SKD/VCP score 0 on Western markers by construction, not for lack of content. _H702 (12-07-2026): not machine-testable — meaning-vs-marker needs per-dict reading; refutation stands on FINDINGS §34+§19; the rule is count meanings, not markers._
Test to confirm: read entry contexts per dict before parsing; count the meaning, not the marker.
↔ Interlinks: [CONTRADICTIONS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) is the same "tag effect is record-type-bound" trap at corpus scale · [GLOSSARY "`<ls>` / iti register"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) is the register confound this premise ignores.
> **Source:** [FINDINGS §34](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#34-the-e-abbreviation-tag-is-polysemous-across-dicts) + [§19](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#19-skd-and-vcp-carry-essentially-zero-western-markup) · [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §6. A verified correction queue stays valid until filed
🟠 ✍️ **A triaged correction stays applicable against live csl-orig between triage and filing.**
Relied on by: the monthly csl-orig batch PR, the SanskritSpellCheck FILE-FIRST queue.
Verified?: ⚠️ spot-checked once (02-07-2026, n=122) — ≈0.8%/week decay; 1 candidate already fixed upstream within ~1 week. _H702 (12-07-2026): perishable by design — a fresh decay recount only means anything at filing time, so it belongs to each `/cologne-batch-pr` window (which already mandates the pre-filing re-verify), not to a sweep._
Test to confirm: re-verify every row against current `csl-orig` immediately before filing; a stale row reads as bot noise.
↔ Interlinks: this is the ASSUMPTIONS-layer restatement of the *decay* that [STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md) makes generic across all findings · [DEAD_ENDS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (blind typo respell) is what happens when a stale queue is filed unchecked · [RECIPES §6](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (correction loci) is the census this queue feeds.
> **Source:** [FINDINGS §25](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#25-a-verified-correction-queue-decays-against-live-csl-orig) · [SanskritSpellCheck](https://github.com/drdhaval2785/SanskritSpellCheck) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## D. Evaluation-threshold assumptions
*Premises not about the data but about the **rulers** laid against it — that a pass/fail bar set by argument can be used as a decision rule. A keying assumption fails loudly once you look; a threshold assumption never fails at all, because nothing ever tests it. It just gets quoted.*

### §9. A threshold set by argument is a decision rule
🔴 ✍️ **That a metric crossing its proposed bar means the aspect genuinely progressed — i.e. that a number nobody calibrated can decide pass/fail.**
Relied on by: the **PM1–PM12** register in [`DIGITAL_SANSKRIT_PEDAGOGY_FIELD_2026.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/DIGITAL_SANSKRIT_PEDAGOGY_FIELD_2026.md) §4e, the §4a matrix metric column, every future "aspect X progressed" claim in the digital-pedagogy field, and A62's evaluation section once [H1731](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1731-Opus_SanskritGrammar_a62-metric-register-into-evaluation-section_27.07.26.md) lands.
Verified?: ❌ never — and the exposure is counted, not hand-waved: **4 of 12 bars rest on a measurement** (PM2 on the 90.7 % keyed share · PM3 on the 30-of-top-100 function-word count · PM4 between the measured τ ≈ 0.05 frequency floor and the 0.446 weakest textbook pair · PM7 from a zero baseline), **1 is a disclosure rule with no threshold** (PM6), and **7 are argued with no anchor at all** (PM1, PM5, PM8, PM9, PM10, PM11, PM12). §4e′ records each bar's anchor and its strength.
Test to confirm: compute **PM8** (cumulative DCS conjunct-token coverage of the first 50 taught conjuncts) and **PM12** (faultfinder false-positive rate over ≥5 000 correct learner-level forms) — both derivable from data already on disk, no new build — and compare each measured value against its proposed bar. Landing far from the bar means the argued thresholds are placeholders rather than decision rules, and the five remaining unanchored bars inherit that verdict. Ratification gate: `@DECIDE` in [`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md), opens **27-09-2026**.
↔ Interlinks: [FINDINGS §487](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) is the same class one layer down — a plausible number that survived until someone re-derived it · [STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md) tracks decay by *source drift*; this row decays by **disuse** — nothing upstream moves, the number simply never gets tested, which is why it needs a calendar gate rather than a re-check recipe.
> **Source:** [`DIGITAL_SANSKRIT_PEDAGOGY_FIELD_2026.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/DIGITAL_SANSKRIT_PEDAGOGY_FIELD_2026.md) §4e′ · [SanskritGrammar](https://github.com/gasyoun/SanskritGrammar) · [H1476](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1476-Opus_SanskritGrammar_pedagogy-aspect-measurable-result-metrics_22.07.26.md), 27-07-2026 · `claude-opus-5[1m]`

### §10. A gold-agreement rate transfers between aspects
🟠 ✍️ **That an answer-key agreement rate measured on one task is a fair expectation for a different one — PM1's ≥90 % sandhi bar is PM2's *measured* 90.7 %, borrowed across aspects.**
Relied on by: PM1's bar; by extension any future PM that adopts a sibling metric's number instead of measuring its own.
Verified?: ❌ never, and the two tasks differ in kind: a paradigm cell has **one** authoritative form from a generator checked against attestation, whereas a sandhi split is a segmentation whose genuinely ambiguous cases no second segmenter resolves by construction. A borrowed number looks measured — it carries a real decimal from a real corpus — which is exactly what makes it harder to notice than a round guess.
Test to confirm: build the ≥200-item sandhi gold set PM1 names and measure agreement. A result far from 90 % means the number was transplanted, not derived; the fix is to set PM1's bar from its own gold set and record the old value in the metadoc history.
↔ Interlinks: §9 is the general case and this is its sharpest instance — the one unanchored bar that does not *look* unanchored · [FINDINGS §487](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (a number that looked measured because the join really ran).
> **Source:** [`DIGITAL_SANSKRIT_PEDAGOGY_FIELD_2026.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/DIGITAL_SANSKRIT_PEDAGOGY_FIELD_2026.md) §4e′ (PM1 row, "measured, but **borrowed**") · [SanskritGrammar](https://github.com/gasyoun/SanskritGrammar) · [H1476](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1476-Opus_SanskritGrammar_pedagogy-aspect-measurable-result-metrics_22.07.26.md), 27-07-2026 · `claude-opus-5[1m]`

---

## Conclusions

- **§1–§8 are all keying or scope assumptions, and every one has already been measured false at least once.** §1/§2 (join keys), §3/§4 (record reach), §5 (symbol meaning), §8 (class inferred from a citation form) — the recurring failure mode is *treating a machine key or a symbol as universal when it is scheme-, dict-, or record-type-bound*. The standing lesson: **transcode/normalize through [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) and count meanings, not markers.**
- **The 🔴 blast-radius rows §1–§4 are the dangerous ones** — they sit under the frequency and translation pipelines, so a silent violation drops ~1/5 to ~1/3 of the data with no error.
- **Sweep state (H702, 12-07-2026, Fable 5 `claude-fable-5`, two passes):** §1–§4 are now ✅ refuted-with-fresh-full-evidence (xref recount, scheme census, 749-root homonym census, layer-tally re-run) — their measured bounds live in FINDINGS (§12/§7/§16/§64), the rows stay as guards; the §4 re-tally caught and corrected an arithmetic slip (≈35,900→61,906 no-PWG headwords). §5 is not machine-testable; §6 decays by design and re-tests at each filing window (12-07 point: the n=15 pending ap90 batch, 1 day old, shows 0 stale rows — consistent with 0.8%/week); §7 waits on an external human. §6 is the one that decays continuously — treat it as perishable.
- **Where they point:** the assumptions feed forward into [RECIPES](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (how to check them), sideways into [CONTRADICTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) and [DEAD_ENDS](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (what breaks when they fail), and their unmeasured residue into [GAPS](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md).
- **Category D (added 27-07-2026, H1476) is a different animal from §1–§8, and the difference is the point.** A keying assumption fails *loudly* the moment someone looks — the join returns 29 % instead of 83 %, the walk misses a fifth of the data, and the row graduates to a measured FINDINGS bound. A **threshold** assumption never fails, because nothing tests it; an argued bar simply gets quoted until it is the standard. That is why §9/§10 carry a **calendar gate (27-09-2026)** where §1–§6 carry a re-check recipe: the trigger cannot be "when the source moves", since nothing upstream moves at all. Every registry of this kind should expect the same asymmetry — **the premises that decay silently are the ones about your instruments, not your data.**

### §7. «Рамаяна. Книга 5. Сундараканда 2026.html» — финальная редакция перевода
🔴 ✍️ **Весь двухъярусный аппарат считает этот файл финальной редакцией перевода Леонова.**
Relied on by: все 1058 якорей яруса-1, dedup 897 нот яруса-2, цель плотности ~37%, печатный мастер, kosha-манифест `sundarakanda-two-tier-apparatus` — при более свежей редакции якоря и dedup частично инвалидируются.
Verified?: ❌ никогда — подтверждение запрошено у Леонова (задача 2 [issue №58](https://github.com/gasyoun/CommentaryStrategies/issues/58)), ждем с 10-07-2026. _H702 (12-07-2026): локально не тестируется — цена = одно письмо-подтверждение, иначе diff по стихам + пере-якорение затронутых нот._
Test to confirm: одно письмо Леонова «да, финал» — или присланная новая редакция → diff по стихам → пере-якорение затронутых нот.
> **Source:** ✍️ H497/H533, 10-07-2026; registered via /artifact-propagate epistemic pass 11-07-2026 (Fable 5 `claude-fable-5`).

---

_Dr. Mārcis Gasūns_
