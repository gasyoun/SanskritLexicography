# DRAFT reply — csl-corrections#119 (MW annexure vs PW/PWK Nachtraege)

_Created: 14-09-2026 · Last updated: 16-09-2026_

**Status: POSTED 15-09-2026** —
<https://github.com/sanskrit-lexicon/csl-corrections/issues/119#issuecomment-5676473420>
(posted by gasyoun; MG ruling 15-09-2026 «Да, постить сейчас», H4883. The text
below the fold is the comment verbatim.)

**Signature replaced 16-09-2026** — MG's final form is
`Dr. Mārcis Gasūns (draft prepared with a little help from my Chinese friend)`;
it now stands in both the live comment and the verbatim text below.

Posting account: gasyoun. Comment text below the fold.

---

Thank you for this hypothesis — we can now answer it with data rather than
anecdote. Short version: **yes, MW99's annexure demonstrably draws on the
Nachträge, and we can also enumerate what it skipped** — including `kāritra`
itself, which is absent from `mw.txt` entirely while present as PW 7-331-d and
Nachträge (Mahāvyutpatti 245, 844, = ceṣṭita).

**1. The dependency hypothesis holds, measurably.** Crossing the complete
Nachträge layers (22,611 `sup_1..7`-tagged PW entries; 13,208 in the letzte
Nachträge) with MW: ~30 % of MW99's annexure headwords are verbatim Nachträge
headwords (1,800 of 6,082; 29.6–30 % under every counting convention we tried).
A Nachträge headword is ~7.8× more likely to sit in the MW annexure than in
MW's main body (32.5 % vs 4.1 %, on the standalone Nachträge digitization).
And MW72 cross-checks show MW99 took ~60 % of the sup_7 pool MW72 lacked —
while skipping 4,112 words outright (the `kāritra` class proper; 27 more were
dropped between MW editions).

**2. The skipped remainder is enumerated and adjudicated.** On the
deterministic `sup_7` pipeline, 4,151 candidate rows were each given a verdict
(artifacts:
`HeadwordLists/MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv`,
`MW-NACHTRAG-TIERA-STUBS-14-09-2026.md`,
`MW_PWK_NACHTRAEGE_MISSING_ENTRIES_TRIAL_14-09-2026.md` in
[gasyoun/SanskritLexicography](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists)):

- **1,751 confirmed missing** from MW (verbatim, stem- and near-form space);
  **572 of them corroborated by ≥2 of 36 other Cologne dictionaries** — draft
  MW-entry stubs are written for these, many with Mahāvyutpatti or
  Buddhist-Hybrid-Sanskrit corroboration (`kāritra` itself: BHS + Śabdakalpadruma).
- **482 are stem-form doublets** (MW carries the lexeme under a different final
  form) — editorial calls, not clean omissions.
- **227 case/vowel-length twins** of MW headwords (the `akalita`/`Akalita`
  trap — SLP1 case is phonemic, so some are distinct words) and **1,691
  near-form matches** flagged for human eyes, since fuzzy ~0.9 cannot separate
  orthographic variants from different words (`kāritra` vs causative
  `kārita` at 0.92 is exactly that case).
- Each row carries a cross-dictionary corroboration profile, Mahāvyutpatti
  citation flags, and DCS-corpus lemma/form attestation.

**3. A second, wider sweep** over the digitizations' own `*` insert markers
(pw.txt + pwkvn.txt across all layers) freezes 3,353 unique absent headwords
with per-row verdicts (`MW-missing-PW-Nachtrag-candidates-14-09-2026.{md,tsv}`,
`MW-STARRED-NACHTRAG-ADJUDICATION-14-09-2026.tsv`) — 349 of them corroborated
Tier-A adds without any risk flag. A stratified 30-sample hand spot-check of
both passes showed **0/30 false positives**.

**4. Caveats we want on the record.** Absence from MW is not automatically an
MW error (MW never promised full PWK coverage); many `sup_7` entries are
homonym-number extensions; and any number in this space is
tier-definition-dependent — our counts always ship with their definition (see
`MW_PWK_NACHTRAEGE_TRIAL_INDEPENDENT_RECHECK_14-09-2026.md` §0).

The full verdict workbook is reproducible from
`HeadwordLists/mw_pwk_nachtraege_missing_entries.py` +
`mw_pwk_nachtraege_adjudicate.py` (stdlib only, deterministic, byte-identical
rerun verified). If useful upstream, we can next turn the corroborated adds
into a machine-usable proposal list (SLP1 + IAST + gloss + sources per entry).

---

_Gasūns (draft prepared with a little help from my Chinese friend)_
