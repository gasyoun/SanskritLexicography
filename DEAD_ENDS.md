# DEAD_ENDS — the Sanskrit-data negative-results graveyard

_Created: 08-07-2026 · Last updated: 08-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS is *confirmed-true*. This file holds the act FINDINGS cannot: **abandoning** an approach — a whole method that was tried and does not work, so the next session does not pay to rediscover the failure. Distinct from a single refuted hypothesis (that lives per-row in [`Uprava/QUESTIONS_LOG.md`](https://github.com/gasyoun/Uprava/blob/main/QUESTIONS_LOG.md)); a dead end is per-*approach*. One of the seven epistemic registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md). Its infra twin is [`Uprava/DEAD_ENDS.md`](https://github.com/gasyoun/Uprava/blob/main/DEAD_ENDS.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates the **cost of a naive re-attempt** (🔴 = expensive to rediscover that it fails).
- **Origin marker:** ⚙️ auto (harvested from a QUESTIONS_LOG refuted row / reverted branch) · ✍️ human (a session wrote it).

Then `Failed because:`, `Evidence:`, `Don't retry unless:`, and a `> **Source:**` line.

**Auto-seed:** [`seed_dead_ends.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_dead_ends.py) harvests [`QUESTIONS_LOG.md`](https://github.com/gasyoun/Uprava/blob/main/QUESTIONS_LOG.md) **refuted** rows, [`SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md) **permanently-dead** hosts, and git-log reverted feature branches (merged-then-reverted) across repos.

---

### §1. Body-text / reverse-dict headword mining — abandoned
🔴 ✍️ **Mining "hidden" headwords from dictionary bodies to grow the CDSL lemma vocabulary.**
Failed because: 38.6% precision overall (bor 18%, bur 32% transcode-garbage, ae 34%, mw72 36%); `<k2>` is just `<k1>` re-encoded (the "+152k new lemmas" was a normalization artifact, ~0 real); big forward dicts already split compounds into their own `<L>` records.
Evidence: adversarial classification, csl-atlas broad-headword review (15-06-2026); the measuring extractor `scripts/lib/dict-body-headwords.mjs` was deleted with the rejected experiment (numbers survive only in the review record).
Don't retry unless: you have a fundamentally different signal — a corpus inflected-form→lemma index (DCS) or vidyut sandhi/compound splitting, which raises findability, not distinct-lemma count.
> **Source:** [FINDINGS §30](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#30-body-text-headword-mining-is-a-dead-end-386-percent-precision) · csl-atlas · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §2. Corpus-derived present-class attribution — abandoned
🔴 ✍️ **Deriving verb present-class (I vs VI, IV vs passive) from the DCS corpus.**
Failed because: the corpus carries no pitch accent, and the class distinction rests on it — class I (`cárati`) and VI (`tudáti`) have identical surface stems where guṇa doesn't change the vowel.
Evidence: a corpus-derived class pass produced 117 spurious I/VI additions — all reverted (120 unsound total vs 19 kept); WhitneyRoots CHANGELOG revert.
Don't retry unless: you have a grammar / Zaliznyak cross-check for every corpus-derived class — never write one into reviewed data raw.
> **Source:** [FINDINGS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#8-unaccented-dcs-cannot-distinguish-present-class-i-from-vi) · WhitneyRoots · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §3. Sandhi-join lookup for prefixed-verb corpus evidence — abandoned
🟠 ✍️ **Building a `upasarga+root` sandhi-join lookup to gain prefixed-verb corpus attestations.**
Failed because: it's a no-op — the corpus lemmatizes prefixed verbs to the root or lacks them; the sandhi-join produces the SAME surface strings as a naïve concat, so spelling was never the limiter. Of √man's 15 prefixed forms only 3 appear in the corpus; ~80% miss.
Evidence: `pwg_preverb1.txt` join measured in `subcard_portrait()` / FREQ_TEST_RUNBOOK.
Don't retry unless: a different corpus that keeps prefixed surface forms is available; otherwise defer to the dictionary's own gloss for the ~80%.
> **Source:** [FINDINGS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#5-the-parallel-corpus-rarely-attests-prefixed-verb-forms) · RussianTranslation · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §4. Bulk-respell of "typo" headword-correction lists — abandoned
🔴 ✍️ **Applying a spell-check typo list as blind `<k1>` respells.**
Failed because: ~9% of "typo" corrections are collisions — the "correct" spelling already exists as its own entry, so a respell creates a duplicate headword or clobbers apparatus rather than fixing anything.
Evidence: source-verification of all 122 FILE-FIRST candidates vs csl-orig (02-07-2026) — YAT 5, MW 2, PWG 2, PW 1 dual-listings; `file_first_verified.tsv`.
Don't retry unless: the filing offers a third editorial category (merge vs respell vs leave) and checks whether the "right" form already exists as its own entry first.
> **Source:** [FINDINGS §24](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#24-about-9-percent-of-typo-corrections-are-collisions) · SanskritSpellCheck · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §5. NFD-decompose-then-strip-Mn as a Sanskrit normalization key — abandoned
🔴 ✍️ **Using blanket NFD + strip-combining-marks to make an IAST comparison/join key.**
Failed because: it destroys vowel length (`ā`→`a`) and retroflex dots (`ṣ`→`s`), and `ś` = `s`+U+0301 collides with the pitch-accent mark — lossy, manufactures false matches.
Evidence: the `form_key` design note in sanskrit_util; the recurring failure mode behind poisoned siglum folds (§45: `samk` merges Śaṃk°+Sāṃk°).
Don't retry unless: you use a length-preserving `form_key` (never blanket NFD+strip); for `<ls>` sigla, consult the curated alias table, never fold-key similarity.
> **Source:** [FINDINGS §36](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#36-iast-unicode-collides-and-normalises-lossily) + [§45](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#45-siglum-prefix-families-routinely-bundle-several-distinct-works-the-diacritic-stripping-fold-has-poisoned-keys) · sanskrit-util/csl-atlas · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

### §6. `OccId` / `sent_id` as a DCS primary key — abandoned
🔴 ✍️ **Keying the DCS CoNLL-U import on `OccId` or `sent_id`.**
Failed because: both are non-unique — `OccId` is reused across a line's sub-sentences (M5 lost ~20 tokens); `sent_id` collides within a chapter (M6 dropped 449 sentences) — silently, before the keys were replaced.
Evidence: `DCS_CONLLU_IMPORT_PLAN.md` §M5–M6, `m5_validation.md`/`m6_validation.md`.
Don't retry unless: never — use synthetic autoincrement surrogates or position-within-text; the stable cross-corpus key is `LemmaId`.
> **Source:** [FINDINGS §9](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#9-dcs-occid-and-sent_id-are-not-unique-keys) · VisualDCS · 08-07-2026 · Opus 4.8 (`claude-opus-4-8`)

---

## ⚙️ Auto-seeded candidates (unconfirmed — `seed_dead_ends.py`, 08-07-2026)

Surfaced by [`seed_dead_ends.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_dead_ends.py) from `QUESTIONS_LOG.md` **refuted** rows. `⚙️ auto` **candidates** — a human confirms the refutation generalises to a whole *approach* (→ `✍️`) or deletes it. (Several of the seeder's raw rows were duplicates of §1–§6 above or malformed table-cell grabs; only the one genuinely new approach is transcribed here.)

### §7. Generalising dictionary-level sense-inheritance direction to corpus scale — refuted
🟠 ⚙️ **Assuming the sense-inheritance *descent direction* observed at the dictionary level (the *dharma* exemplar) holds at corpus scale.**
Failed because: it did NOT hold — the classifier over the full corpus reversed the exemplar (SKD 53.3% fused vs VCP 77.6% fused); §7 of the fusion analysis was re-scoped to record-type-dependent, not dictionary-level. This is the corpus-scale twin of [CONTRADICTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).
Evidence: R2606-06 (refuted 02-07-2026), `r2_kosa_fusion.json`, [csl-atlas PR #184](https://github.com/sanskrit-lexicon/csl-atlas/pull/184).
Don't retry unless: you compute the direction at corpus scale from the start — never generalise a single hand-picked lemma's fusion direction to a dictionary-level rule.
> **Source:** [QUESTIONS_LOG R2606-06](https://github.com/gasyoun/Uprava/blob/main/QUESTIONS_LOG.md) · csl-atlas · 08-07-2026 · auto (seed_dead_ends.py)

---

_Dr. Mārcis Gasūns_
