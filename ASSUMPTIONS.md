# ASSUMPTIONS — unverified premises the Sanskrit-data pipelines rely on

_Created: 08-07-2026 · Last updated: 11-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS holds *measured, past-tense* facts. This file holds the act FINDINGS structurally cannot: **relying** on an unproven premise. An assumption is *depended-upon but unverified* — the moment its **Test** passes, it **graduates** to a FINDINGS row (delete it here, cite the finding there). One of the seven episteme registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md); the full set is on the [episteme dashboard](https://gasyoun.github.io/SanskritLexicography/episteme/). Its infra twin is [`Uprava/ASSUMPTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/ASSUMPTIONS.md).

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
Verified?: ⚠️ spot-checked once (11-06-2026, n=15,902 lemmas) — 81.4% link, 18.6% (2,956 lemmas) have NO CDSL headword.
Test to confirm: recount linked/total in [`dcs_cdsl_xref.tsv`](https://github.com/sanskrit-lexicon/csl-apidev/blob/master/simple-search/dcs_xref/dcs_cdsl_xref.tsv); any pipeline assuming 100% coverage silently drops ~1/5 of corpus vocabulary.
↔ Interlinks: [RECIPES §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) reproduces the 81.4% number that bounds this premise · [GLOSSARY "headword vs lemma"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the distinction this assumption blurs · the unlinked 18.6% is the frontier next to [GAPS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (Heritage as a third witness).
> **Source:** [FINDINGS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword) · [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §2. One transliteration scheme keys all DCS files
🔴 ✍️ **A frequency/lemma join can assume a single transliteration across the DCS-derived files.**
Relied on by: `freq_route.py`, any join between `VisualDCS/dcs_lemma_summary.json` (SLP1) and `RussianTranslation/src/dcs_lemma_renou.json` (IAST).
Verified?: ⚠️ spot-checked once (24-06-2026) — the two files are keyed in DIFFERENT schemes (SLP1 vs IAST).
Test to confirm: diff a sample of keys across both files; a raw string join misses every non-ASCII-coincident lemma unless one side is transcoded via `sanskrit-util`.
↔ Interlinks: [GLOSSARY "SLP1 vs IAST"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) is the term this premise trips over · [DEAD_ENDS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) is the *wrong* way to bridge schemes (NFD+strip) · [RECIPES §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) shows the transcode-then-join done right.
> **Source:** [FINDINGS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#7-dcs-lemma-data-is-keyed-in-two-transliterations) · [VisualDCS](https://github.com/gasyoun/VisualDCS)/[RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## B. Dictionary-record-structure assumptions
*Premises about how a dictionary's records are laid out — what a walk over them will reach.*

### §3. A dict's giant verb root lives at homonym index 0
🔴 ✍️ **A per-record split can read `bufs[0]` and assume the first homonym record holds the verb root.**
Relied on by: `gen_root_split()`, any PWG root-portrait/segmentation walk over homonym records.
Verified?: ⚠️ spot-checked once (24-06-2026, top-50 freq roots) — 19 of 50 have a giant homonym at index > 0 (√i at 2, √mā at 2, √as at 1).
Test to confirm: re-run [`audit_root_split.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_root_split.py); iterate ALL homonym records, never `bufs[0]`.
↔ Interlinks: [GLOSSARY "homonym index"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the ordinal this premise mis-assumes · [GAPS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (homonym token frequency) is what stays unreachable while this holds.
> **Source:** [FINDINGS §16](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#16-giant-verb-roots-sit-at-non-zero-homonym-indexes) · [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) (pwg)/[RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §4. A worklist built by iterating PWG keys covers the local layer universe
🔴 ✍️ **Enumerating "headwords" by walking PWG records reaches the whole pwg_ru merge universe.**
Relied on by: the verb-root worklist (`verbs01`/PWG), any pwg_ru queue builder.
Verified?: ⚠️ spot-checked once (05-07-2026, n=167,988 headwords) — ≈35,900 headwords (≈36%) carry ZERO PWG record; PW-only alone = 40,338 (24%).
Test to confirm: re-run the `dict_merge.py` index tally in [`PWG_LAYER_COMBINATIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md); PW/SCH/PWKVN-only entries need their own queue path.
↔ Interlinks: [RECIPES §5](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (union headword index) is the asset that *measures* the true universe this premise underestimates.
> **Source:** [FINDINGS §64](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#64-pw-only-headwords-outnumber-pwg-only-ones-6-to-1-pwg-is-not-the-sole-spine-of-the-local-layer-universe) · [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## C. Cross-dict & temporal-validity assumptions
*Premises that a symbol means one thing across dictionaries, or that a measurement stays true over time.*

### §5. A shared markup tag means the same thing across dicts
🟠 ✍️ **The same `<ab>` / marker tag carries one meaning that can be counted dict-agnostically.**
Relied on by: any cross-dict tag-count survey (etymology detectors, `<ls>` density rankers, marker-based structure detectors).
Verified?: ⚠️ spot-checked once (26-06-2026) — `<ab>E.</ab>` = Etymology in WIL but "Epithet of" in CAE, "Epic" in MD; SKD/VCP score 0 on Western markers by construction, not for lack of content.
Test to confirm: read entry contexts per dict before parsing; count the meaning, not the marker.
↔ Interlinks: [CONTRADICTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) is the same "tag effect is record-type-bound" trap at corpus scale · [GLOSSARY "`<ls>` / iti register"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) is the register confound this premise ignores.
> **Source:** [FINDINGS §34](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#34-the-e-abbreviation-tag-is-polysemous-across-dicts) + [§19](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#19-skd-and-vcp-carry-essentially-zero-western-markup) · [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §6. A verified correction queue stays valid until filed
🟠 ✍️ **A triaged correction stays applicable against live csl-orig between triage and filing.**
Relied on by: the monthly csl-orig batch PR, the SanskritSpellCheck FILE-FIRST queue.
Verified?: ⚠️ spot-checked once (02-07-2026, n=122) — ≈0.8%/week decay; 1 candidate already fixed upstream within ~1 week.
Test to confirm: re-verify every row against current `csl-orig` immediately before filing; a stale row reads as bot noise.
↔ Interlinks: this is the ASSUMPTIONS-layer restatement of the *decay* that [STALENESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md) makes generic across all findings · [DEAD_ENDS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (blind typo respell) is what happens when a stale queue is filed unchecked · [RECIPES §6](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (correction loci) is the census this queue feeds.
> **Source:** [FINDINGS §25](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#25-a-verified-correction-queue-decays-against-live-csl-orig) · [SanskritSpellCheck](https://github.com/drdhaval2785/SanskritSpellCheck) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## Conclusions

- **Every premise here is a keying or scope assumption, and every one has already been measured false at least once.** §1/§2 (join keys), §3/§4 (record reach), §5 (symbol meaning) — the recurring failure mode is *treating a machine key or a symbol as universal when it is scheme-, dict-, or record-type-bound*. The standing lesson: **transcode/normalize through [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) and count meanings, not markers.**
- **The 🔴 blast-radius rows §1–§4 are the dangerous ones** — they sit under the frequency and translation pipelines, so a silent violation drops ~1/5 to ~1/3 of the data with no error.
- **None has graduated yet** (all ⚠️ spot-checked, none ✅): each needs a *full* verification, not a sample, before it becomes a FINDINGS fact. §6 is the one that decays continuously — treat it as perishable.
- **Where they point:** the assumptions feed forward into [RECIPES](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (how to check them), sideways into [CONTRADICTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) and [DEAD_ENDS](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (what breaks when they fail), and their unmeasured residue into [GAPS](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md).

### §7. «Рамаяна. Книга 5. Сундараканда 2026.html» — финальная редакция перевода
🔴 ✍️ **Весь двухъярусный аппарат считает этот файл финальной редакцией перевода Леонова.**
Relied on by: все 1058 якорей яруса-1, dedup 897 нот яруса-2, цель плотности ~37%, печатный мастер, kosha-манифест `sundarakanda-two-tier-apparatus` — при более свежей редакции якоря и dedup частично инвалидируются.
Verified?: ❌ никогда — подтверждение запрошено у Леонова (задача 2 [issue №58](https://github.com/gasyoun/CommentaryStrategies/issues/58)), ждём с 10-07-2026.
Test to confirm: одно письмо Леонова «да, финал» — или присланная новая редакция → diff по стихам → пере-якорение затронутых нот.
> **Source:** ✍️ H497/H533, 10-07-2026; registered via /artifact-propagate epistemic pass 11-07-2026 (Fable 5 `claude-fable-5`).

---

_Dr. Mārcis Gasūns_
