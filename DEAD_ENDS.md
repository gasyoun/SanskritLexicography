# DEAD_ENDS — the Sanskrit-data negative-results graveyard

_Created: 08-07-2026 · Last updated: 10-07-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS is *confirmed-true*. This file holds the act FINDINGS cannot: **abandoning** an approach — a whole method that was tried and does not work, so the next session does not pay to rediscover the failure. Distinct from a single refuted hypothesis (that lives per-row in [`Uprava/QUESTIONS_LOG.md`](https://github.com/gasyoun/Uprava/blob/main/QUESTIONS_LOG.md)); a dead end is per-*approach*. One of the seven epistemic registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md). Its infra twin is [`Uprava/DEAD_ENDS.md`](https://github.com/gasyoun/Uprava/blob/main/DEAD_ENDS.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates the **cost of a naive re-attempt** (🔴 = expensive to rediscover that it fails).
- **Origin marker:** ⚙️ auto (harvested from a QUESTIONS_LOG refuted row / reverted branch) · ✍️ human (a session wrote it).

Then `Failed because:`, `Evidence:`, `Don't retry unless:`, and a `> **Source:**` line.

**Auto-seed:** [`seed_dead_ends.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_dead_ends.py) harvests [`QUESTIONS_LOG.md`](https://github.com/gasyoun/Uprava/blob/main/QUESTIONS_LOG.md) **refuted** rows, [`SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md) **permanently-dead** hosts, and git-log reverted feature branches (merged-then-reverted) across repos.

**Categories** (below) group the abandoned approaches by *what went wrong* — a signal that was never there, a key that was never unique, a normalization that was lossy — so a reader can scan by failure class rather than by discovery order.

---

## A. Missing-signal approaches (the data never carried what the method needed)
*Approaches abandoned because the source simply lacks the distinguishing signal — accent, corpus attestation, or genuinely new vocabulary — no amount of cleverness recovers it.*

### §1. Body-text / reverse-dict headword mining — abandoned
🔴 ✍️ **Mining "hidden" headwords from dictionary bodies to grow the CDSL lemma vocabulary.**
Failed because: 38.6% precision overall (bor 18%, bur 32% transcode-garbage, ae 34%, mw72 36%); `<k2>` is just `<k1>` re-encoded (the "+152k new lemmas" was a normalization artifact, ~0 real); big forward dicts already split compounds into their own `<L>` records.
Evidence: adversarial classification, csl-atlas broad-headword review (15-06-2026); the measuring extractor `scripts/lib/dict-body-headwords.mjs` was deleted with the rejected experiment (numbers survive only in the review record).
Don't retry unless: you have a fundamentally different signal — a corpus inflected-form→lemma index (DCS) or vidyut sandhi/compound splitting, which raises findability, not distinct-lemma count.
↔ Interlinks: [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) is the broad-headword-coverage frontier this mining tried and failed to move · [RECIPES §5](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (union headword index) is the *real* asset that measures true distinct-lemma count · [ASSUMPTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (PWG-worklist scope) is the adjacent "what covers the universe" premise.
> **Source:** [FINDINGS §30](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#30-body-text-headword-mining-is-a-dead-end-386-percent-precision) · [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §2. Corpus-derived present-class attribution — abandoned
🔴 ✍️ **Deriving verb present-class (I vs VI, IV vs passive) from the DCS corpus.**
Failed because: the corpus carries no pitch accent, and the class distinction rests on it — class I (`cárati`) and VI (`tudáti`) have identical surface stems where guṇa doesn't change the vowel.
Evidence: a corpus-derived class pass produced 117 spurious I/VI additions — all reverted (120 unsound total vs 19 kept); WhitneyRoots CHANGELOG revert.
Don't retry unless: you have a grammar / Zaliznyak cross-check for every corpus-derived class — never write one into reviewed data raw.
↔ Interlinks: [CONTRADICTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) (Whitney gen.pl accent) is the sibling case where the missing accent signal bites · [GLOSSARY "SLP1 vs IAST"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) covers why the corpus surface strings carry no pitch · [RECIPES §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) is the accent-validation path that *does* have the signal (attested RV forms).
> **Source:** [FINDINGS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#8-unaccented-dcs-cannot-distinguish-present-class-i-from-vi) · [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §3. Sandhi-join lookup for prefixed-verb corpus evidence — abandoned
🟠 ✍️ **Building a `upasarga+root` sandhi-join lookup to gain prefixed-verb corpus attestations.**
Failed because: it's a no-op — the corpus lemmatizes prefixed verbs to the root or lacks them; the sandhi-join produces the SAME surface strings as a naïve concat, so spelling was never the limiter. Of √man's 15 prefixed forms only 3 appear in the corpus; ~80% miss.
Evidence: `pwg_preverb1.txt` join measured in `subcard_portrait()` / FREQ_TEST_RUNBOOK.
Don't retry unless: a different corpus that keeps prefixed surface forms is available; otherwise defer to the dictionary's own gloss for the ~80%.
↔ Interlinks: [ASSUMPTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (one transliteration keys all DCS files) is the join premise this attestation walk sat on · [GAPS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) (homonym token frequency) is a neighbouring corpus-coverage gap · [GLOSSARY "headword vs lemma"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) frames why the corpus lemmatizes prefixed verbs away.
> **Source:** [FINDINGS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#5-the-parallel-corpus-rarely-attests-prefixed-verb-forms) · [RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §8. Verifying Petersburg citations against the DCS corpus (shared-*erroneous*-citation test) — abandoned for this candidate set
🔴 ✍️ **Resolving PWG/PW `<ls>` verse citations to a DCS passage locus to check the cited lemma is present there (the "airtight shared-error" upgrade for A10, MW←Böhtlingk).**
Failed because: the candidate pool is 96% Harivaṃśa cited by the Petersburg **Calcutta-vulgate** continuous śloka number (to 16 291), while DCS carries the **critical** edition (118 chapters, ~6 073 verses, per-chapter numbering). 298 refs provably exceed the entire DCS Harivaṃśa; the rest have no vulgate↔critical concordance to map a continuous number onto a (chapter, verse) locus. Of 587 candidates only **1** resolved — a Caurapañcaśikā recension artifact, not an editor-independent wrong locus. Net: **0 adjudicated shared errors; A10 not upgraded** (stays 3/5; F1 apparatus + F5 order remain its evidence).
Evidence: `VisualDCS/src/DCS-data-2026/dcs_shared_citation_errors.py` + reports (H203, 10-07-2026); verdict `reports/F4_DCS_SHARED_CITATION_ERRORS_VERDICT.md`; csl-atlas A10 §6 ([PR #235](https://github.com/sanskrit-lexicon/csl-atlas/pull/235)).
Don't retry unless: a digital **vulgate** Harivaṃśa (the edition Böhtlingk cited), token-lemmatized to its own continuous numbering, OR a vulgate↔critical Harivaṃśa verse concordance, exists — otherwise the citation number can never be mapped to a DCS locus.
↔ Interlinks: [§6](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (DCS `OccId`/`sent_id` not a key) and [FINDINGS §45](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#45-siglum-prefix-families-routinely-bundle-several-distinct-works-the-diacritic-stripping-fold-has-poisoned-keys) (siglum-prefix families bundle distinct works) are the adjacent "DCS keys don't line up with dictionary refs" cases.
> **Source:** [H203](https://github.com/gasyoun/Uprava/blob/main/handoffs/H203-Opus_VisualDCS_dcs_shared_citation_errors_05.07.26.md) · [VisualDCS](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/F4_DCS_SHARED_CITATION_ERRORS_VERDICT.md) · [csl-atlas A10 §6](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) · 10-07-2026 · `claude-opus-4-8`

---

## B. Bad-key / lossy-key approaches (a machine key that silently drops or merges data)
*Approaches abandoned because the chosen join/normalization key was non-unique or lossy — a respell that collides, an NFD fold that erases length, a corpus id reused across sub-sentences.*

### §4. Bulk-respell of "typo" headword-correction lists — abandoned
🔴 ✍️ **Applying a spell-check typo list as blind `<k1>` respells.**
Failed because: ~9% of "typo" corrections are collisions — the "correct" spelling already exists as its own entry, so a respell creates a duplicate headword or clobbers apparatus rather than fixing anything.
Evidence: source-verification of all 122 FILE-FIRST candidates vs csl-orig (02-07-2026) — YAT 5, MW 2, PWG 2, PW 1 dual-listings; `file_first_verified.tsv`.
Don't retry unless: the filing offers a third editorial category (merge vs respell vs leave) and checks whether the "right" form already exists as its own entry first.
↔ Interlinks: [ASSUMPTIONS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (a verified correction queue stays valid) is the premise a blind bulk respell violates · [RECIPES §6](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (correction loci census) is the audited path these corrections should flow through instead.
> **Source:** [FINDINGS §24](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#24-about-9-percent-of-typo-corrections-are-collisions) · [SanskritSpellCheck](https://github.com/drdhaval2785/SanskritSpellCheck) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §5. NFD-decompose-then-strip-Mn as a Sanskrit normalization key — abandoned
🔴 ✍️ **Using blanket NFD + strip-combining-marks to make an IAST comparison/join key.**
Failed because: it destroys vowel length (`ā`→`a`) and retroflex dots (`ṣ`→`s`), and `ś` = `s`+U+0301 collides with the pitch-accent mark — lossy, manufactures false matches.
Evidence: the `form_key` design note in sanskrit_util; the recurring failure mode behind poisoned siglum folds (§45: `samk` merges Śaṃk°+Sāṃk°).
Don't retry unless: you use a length-preserving `form_key` (never blanket NFD+strip); for `<ls>` sigla, consult the curated alias table, never fold-key similarity.
↔ Interlinks: [ASSUMPTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (one transliteration keys all files) is the join premise this is the *wrong* way to satisfy · [GLOSSARY "form_key"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) and [GLOSSARY "SLP1 vs IAST"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) define the length-preserving key that replaces it.
> **Source:** [FINDINGS §36](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#36-iast-unicode-collides-and-normalises-lossily) + [§45](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#45-siglum-prefix-families-routinely-bundle-several-distinct-works-the-diacritic-stripping-fold-has-poisoned-keys) · [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util)/[csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

### §6. `OccId` / `sent_id` as a DCS primary key — abandoned
🔴 ✍️ **Keying the DCS CoNLL-U import on `OccId` or `sent_id`.**
Failed because: both are non-unique — `OccId` is reused across a line's sub-sentences (M5 lost ~20 tokens); `sent_id` collides within a chapter (M6 dropped 449 sentences) — silently, before the keys were replaced.
Evidence: `DCS_CONLLU_IMPORT_PLAN.md` §M5–M6, `m5_validation.md`/`m6_validation.md`.
Don't retry unless: never — use synthetic autoincrement surrogates or position-within-text; the stable cross-corpus key is `LemmaId`.
↔ Interlinks: [ASSUMPTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (DCS lemma == CDSL headword) is the join layer these ids were meant to feed · [RECIPES §3](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (DeepSeek alignment grounding) is a DCS-import pipeline that depends on a stable per-token key.
> **Source:** [FINDINGS §9](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#9-dcs-occid-and-sent_id-are-not-unique-keys) · [VisualDCS](https://github.com/gasyoun/VisualDCS) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · `claude-opus-4-8`

---

## ⚙️ Auto-seeded candidates (unconfirmed — `seed_dead_ends.py`, 08-07-2026)

Surfaced by [`seed_dead_ends.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_dead_ends.py) from `QUESTIONS_LOG.md` **refuted** rows. `⚙️ auto` **candidates** — a human confirms the refutation generalises to a whole *approach* (→ `✍️`) or deletes it. (Several of the seeder's raw rows were duplicates of §1–§6 above or malformed table-cell grabs; only the one genuinely new approach is transcribed here.)

### §7. Generalising dictionary-level sense-inheritance direction to corpus scale — refuted
🟠 ⚙️ **Assuming the sense-inheritance *descent direction* observed at the dictionary level (the *dharma* exemplar) holds at corpus scale.**
Failed because: it did NOT hold — the classifier over the full corpus reversed the exemplar (SKD 53.3% fused vs VCP 77.6% fused); §7 of the fusion analysis was re-scoped to record-type-dependent, not dictionary-level. This is the corpus-scale twin of [CONTRADICTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).
Evidence: R2606-06 (refuted 02-07-2026), `r2_kosa_fusion.json`, [csl-atlas PR #184](https://github.com/sanskrit-lexicon/csl-atlas/pull/184).
Don't retry unless: you compute the direction at corpus scale from the start — never generalise a single hand-picked lemma's fusion direction to a dictionary-level rule.
↔ Interlinks: [CONTRADICTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) (SKD/VCP fusion) is the corpus-scale contradiction this refuted approach became · [ASSUMPTIONS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (a shared tag means one thing across dicts) is the same "record-type-bound, not dictionary-level" trap.
> **Source:** [QUESTIONS_LOG R2606-06](https://github.com/gasyoun/Uprava/blob/main/QUESTIONS_LOG.md) · [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_dead_ends.py)

---

## C. Wrong-witness approaches (the method interrogated the wrong text)
*Approaches abandoned because the evidence was sought in an edition/recension other than the one the claim is about — so every answer comes back ambiguous no matter how good the tooling.*

### §8. Resolving PWG/MW `HARIV.` citations against DCS to find shared **erroneous** citations — abandoned
🔴 ✍️ **Testing whether MW and PWG share a *wrong* Harivaṃśa verse number by resolving `HARIV. N` against the DCS corpus — and, the deeper trap, proposing a vulgate↔critical *concordance* as the fix.**

Failed because: PWG (15,415 numbered refs, range 1–16,369) and MW (1,053 numbered refs) both cite the **Calcutta vulgate** by *continuous śloka number* (16,374 ślokas, 271 adhyāyas). DCS carries **Vaidya's critical edition** (118 adhyāyas, 6,073 ślokas ≈ ⅓ of the vulgate). Only **1 of 587** shared rare refs resolved. The obvious repair — build a vulgate↔critical concordance — **cannot work**: a concordance maps a vulgate address to a critical address *on the assumption the address is correct*, which is precisely the proposition under test. An **erroneous** citation maps to a critical verse lacking the headword; a **correct** citation pointing at vulgate-only material maps to `ABSENT`. Both emit the same observable ("not found"), so no concordance — however perfect, however verse-level — can separate *Böhtlingk wrote the wrong number* from *Vaidya cut this verse*. With ⅔ of the vulgate absent from the critical text, the `ABSENT` branch swamps the signal.

Evidence: [`data/forensic/shared_rare_citations.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_rare_citations.csv) (587 rows, 565 `HARIV.`); [`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) §6; DCS chapter census = 118 files in [`VisualDCS`](https://github.com/gasyoun/VisualDCS) `src/DCS-data-2026/conllu/files/Harivaṃśa/`; full citation-form census in [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md) (10-07-2026).

Don't retry unless: you adjudicate the citation against **the vulgate itself**, never against the critical edition. A numbered vulgate text makes the concordance unnecessary — the test becomes "does the headword occur at vulgate śloka `N`, and if not, at what offset δ?", and a shared *nonzero* δ across both dictionaries is the airtight shared-mistake result. The free Kinjawadekar (Chitrashala 1936) vulgate e-text at [mahabharata-resources.org](https://mahabharata-resources.org/harivamsa/harivamsa-cs-index.html) covers **11,646 of 16,374 verses (71.1%)** and reaches **474 of the 565 shared refs (83.9%)** — against 1 of 587 via DCS. Executable path: [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md).

↔ Interlinks: the wrong-witness twin of category A — there the signal was absent from the source, here it is present but *in a different book*. Same species of unexamined cross-resource identification as [ASSUMPTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (DCS lemma == CDSL headword).
> **Source:** [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) A10 · [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md) · [10-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-10&until=2026-07-11) · `claude-opus-4-8`

---

## Conclusions

- **Three recurring failure classes account for every abandoned approach.** Category A (§1–§3) fails because *the source never carried the signal* — no new vocabulary in dictionary bodies, no pitch accent in the corpus, no prefixed surface forms; category B (§4–§6) fails because *the machine key was collision-prone or lossy* — a respell that already exists, an NFD fold that erases length, a corpus id reused across sub-sentences; category C (§8) fails because *the wrong text was interrogated* — the claim was about the vulgate, the evidence was sought in the critical edition. Naming the class up front is the cheapest way to not re-pay the failure.
- **§8 adds a nastier shape: the plausible repair that is structurally incapable of repairing.** A vulgate↔critical concordance is a real, buildable, scholarly-respectable artifact — and it still cannot answer the question, because it presupposes the correctness of the very address under test. Before building an intermediate mapping, ask what it *assumes*; if it assumes the thing you are testing, it cannot test it.
- **The 🔴 rows are 🔴 precisely because a naive re-attempt looks plausible and fails silently** — 38.6% precision that reads like success (§1), a class pass that writes 117 spurious rows before revert (§2), an NFD key that manufactures false matches with no error (§5), ids that drop tokens before anyone notices (§6). The expensive part is always the *silence*, not the failure.
- **The standing escape hatch is a better witness or a better key, not more effort.** §1 wants a corpus inflected-form index (DCS); §2 wants a grammar/Zaliznyak cross-check; §5/§6 want a length-preserving `form_key` / a stable `LemmaId` — each dead end names the concrete different-signal condition that would reopen it.
- **Where they point:** the abandoned keys are the mirror of [RECIPES](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (the paths that *do* reproduce), the violated premises live in [ASSUMPTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md), and §7's corpus-scale reversal is already a [CONTRADICTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) row.

---

_Dr. Mārcis Gasūns_
