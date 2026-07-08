# ASSUMPTIONS — unverified premises the Sanskrit-data pipelines rely on

_Created: 08-07-2026 · Last updated: 08-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS holds *measured, past-tense* facts. This file holds the act FINDINGS structurally cannot: **relying** on an unproven premise. An assumption is *depended-upon but unverified* — the moment its **Test** passes, it **graduates** to a FINDINGS row (delete it here, cite the finding there). One of the seven epistemic registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md). Its infra twin is [`Uprava/ASSUMPTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/ASSUMPTIONS.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates **blast radius**: 🔴 many downstream datasets/layers cascade if the premise is false · 🟠 one pipeline · 🟡 local.
- **Origin marker:** ⚙️ auto (a script emitted this candidate — a *candidate* until a human confirms) · ✍️ human (a session wrote it from judgment).

Then the premise as a claim, `Relied on by:`, `Verified?:` (❌ never · ⚠️ spot-checked once · ✅ → graduate to FINDINGS), `Test to confirm:`, and a `> **Source:**` line.

**Auto-seed:** [`scan_assumptions.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/scan_assumptions.py) greps the code spine for `# ASSUMES:` / `# INVARIANT:` tag comments and bare `assert` premises in dataset builders, prefilling `Relied on by` from the enclosing script. Candidates arrive as ⚙️ rows; a human promotes or deletes them.

---

### §1. DCS lemma == CDSL headword
🔴 ✍️ **Any join that treats a DCS corpus lemma as if it has a matching CDSL dictionary headword.**
Relied on by: `dcs_cdsl_xref.tsv` (kosha manifest `dcs-cdsl-xref`), `build_xref.py`, the kosha frequency LEFT-JOIN, Sa→Ru glossary form→lemma resolution.
Verified?: ⚠️ spot-checked once (11-06-2026, n=15,902 lemmas) — 81.4% link, 18.6% (2,956 lemmas) have NO CDSL headword.
Test to confirm: recount linked/total in [`dcs_cdsl_xref.tsv`](https://github.com/sanskrit-lexicon/csl-apidev/blob/master/simple-search/dcs_xref/dcs_cdsl_xref.tsv); any pipeline assuming 100% coverage silently drops ~1/5 of corpus vocabulary.
> **Source:** [FINDINGS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#12-a-fifth-of-dcs-lemmas-have-no-cdsl-headword) · csl-apidev · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §2. One transliteration scheme keys all DCS files
🔴 ✍️ **A frequency/lemma join can assume a single transliteration across the DCS-derived files.**
Relied on by: `freq_route.py`, any join between `VisualDCS/dcs_lemma_summary.json` (SLP1) and `RussianTranslation/src/dcs_lemma_renou.json` (IAST).
Verified?: ⚠️ spot-checked once (24-06-2026) — the two files are keyed in DIFFERENT schemes (SLP1 vs IAST).
Test to confirm: diff a sample of keys across both files; a raw string join misses every non-ASCII-coincident lemma unless one side is transcoded via `sanskrit-util`.
> **Source:** [FINDINGS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#7-dcs-lemma-data-is-keyed-in-two-transliterations) · VisualDCS/RussianTranslation · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §3. A dict's giant verb root lives at homonym index 0
🔴 ✍️ **A per-record split can read `bufs[0]` and assume the first homonym record holds the verb root.**
Relied on by: `gen_root_split()`, any PWG root-portrait/segmentation walk over homonym records.
Verified?: ⚠️ spot-checked once (24-06-2026, top-50 freq roots) — 19 of 50 have a giant homonym at index > 0 (√i at 2, √mā at 2, √as at 1).
Test to confirm: re-run [`audit_root_split.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_root_split.py); iterate ALL homonym records, never `bufs[0]`.
> **Source:** [FINDINGS §16](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#16-giant-verb-roots-sit-at-non-zero-homonym-indexes) · csl-orig (pwg)/RussianTranslation · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §4. A worklist built by iterating PWG keys covers the local layer universe
🔴 ✍️ **Enumerating "headwords" by walking PWG records reaches the whole pwg_ru merge universe.**
Relied on by: the verb-root worklist (`verbs01`/PWG), any pwg_ru queue builder.
Verified?: ⚠️ spot-checked once (05-07-2026, n=167,988 headwords) — ≈35,900 headwords (≈36%) carry ZERO PWG record; PW-only alone = 40,338 (24%).
Test to confirm: re-run the `dict_merge.py` index tally in [`PWG_LAYER_COMBINATIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md); PW/SCH/PWKVN-only entries need their own queue path.
> **Source:** [FINDINGS §64](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#64-pw-only-headwords-outnumber-pwg-only-ones-6-to-1-pwg-is-not-the-sole-spine-of-the-local-layer-universe) · SanskritLexicography · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §5. A shared markup tag means the same thing across dicts
🟠 ✍️ **The same `<ab>` / marker tag carries one meaning that can be counted dict-agnostically.**
Relied on by: any cross-dict tag-count survey (etymology detectors, `<ls>` density rankers, marker-based structure detectors).
Verified?: ⚠️ spot-checked once (26-06-2026) — `<ab>E.</ab>` = Etymology in WIL but "Epithet of" in CAE, "Epic" in MD; SKD/VCP score 0 on Western markers by construction, not for lack of content.
Test to confirm: read entry contexts per dict before parsing; count the meaning, not the marker.
> **Source:** [FINDINGS §34](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#34-the-e-abbreviation-tag-is-polysemous-across-dicts) + [§19](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#19-skd-and-vcp-carry-essentially-zero-western-markup) · csl-orig · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §6. A verified correction queue stays valid until filed
🟠 ✍️ **A triaged correction stays applicable against live csl-orig between triage and filing.**
Relied on by: the monthly csl-orig batch PR, the SanskritSpellCheck FILE-FIRST queue.
Verified?: ⚠️ spot-checked once (02-07-2026, n=122) — ≈0.8%/week decay; 1 candidate already fixed upstream within ~1 week.
Test to confirm: re-verify every row against current `csl-orig` immediately before filing; a stale row reads as bot noise.
> **Source:** [FINDINGS §25](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#25-a-verified-correction-queue-decays-against-live-csl-orig) · SanskritSpellCheck · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

---

_Dr. Mārcis Gasūns_
