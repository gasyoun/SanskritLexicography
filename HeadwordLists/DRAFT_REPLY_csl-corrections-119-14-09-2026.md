# DRAFT reply — csl-corrections#119 (MW annexure vs PW/PWK Nachtraege)

_Created: 14-09-2026 · Last updated: 14-09-2026_

**Status: DRAFT — upstream posting is MG's ruling** (H4837 gate; a 14-09
changelog row records a posting approval for the earlier MW72-baseline reply —
this draft posts only on a fresh word from MG).

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

**2. The skipped remainder is enumerable.** Using the digitizations' own `*`
insert markers (pw.txt + pwkvn.txt) we freeze the set of Nachträge headwords
**absent from MW99**: 3,353 unique headwords. Each carries a cross-dictionary
corroboration profile over 36 Cologne dictionaries, Mahāvyutpatti-citation
flags (273 cite MAHĀVY), MW stem/near-form checks, and DCS-corpus attestation.

**3. A first adjudication pass** (artifacts:
`HeadwordLists/MW-missing-PW-Nachtrag-candidates-14-09-2026.{md,tsv}`,
`MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv`, `MW-NACHTRAG-TIERA-STUBS-14-09-2026.md`
in [gasyoun/SanskritLexicography](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists)):

- **2,743 confirmed missing** (absent verbatim and in stem-normalized space);
  889 corroborated by ≥2 other dictionaries, 349 of them without any risk flag
  — draft MW-entry stubs are written for all 889.
- **610 are stem-form doublets** (MW carries the lexeme under a different final
  form, e.g. `aścary` ↔ `aścarya`) — editorial calls, not clean omissions.
- Risk classes flagged per row: vowel-length variants that may still be distinct
  words (SLP1 `Anumati` gaṇa-entry vs `anumati`), orthographic doublets
  (metathesis, single/double consonants), the `kāritra`~`kārita` false-friend
  class (different words at fuzzy 0.92 — exactly why this tier needs human
  review), and PWK's pratyāhāra/short-form listings.

**4. Caveats we want on the record.** Absence from MW is not automatically an
MW error (MW never promised full PWK coverage); MW72 cross-checks split the
pool into ~4,112 never-seen vs 27 dropped-between-editions; and any number in
this space is tier-definition-dependent — our counts always ship with their
definition (see `MW_PWK_NACHTRAEGE_TRIAL_INDEPENDENT_RECHECK_14-09-2026.md`).

The full verdict workbook is reproducible from
`HeadwordLists/pw_nachtrag_vs_mw.py` + `pw_nachtrag_adjudicate.py` (stdlib
only, deterministic). If useful upstream, we can next turn the 349 clean adds
into a machine-usable proposal list (SLP1 + IAST + gloss + sources per entry).

---

_Gasūns (draft prepared with AI assistance, per repo convention)_
