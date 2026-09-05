# KEWA index normalization + dhātu-aware join to PWG headwords

_Created: 25-08-2026 · Last updated: 25-08-2026_

The **modern IE** lane of ceiling item **C4**, built under
[H3169 (Opus 5) — Ceiling C4: KEWA index normalization + dhātu-aware join to PWG headwords](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3169-Opus_SanskritLexicography_ceiling-c4-kewa-normalize-join_19.08.26.md).
Programme:
[PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md)
· roadmap row
[ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)
C4.

Source: **M. Mayrhofer, _Kurzgefaßtes etymologisches Wörterbuch des
Altindischen_ (KEWA), 1953–1980** — the OCRed heading index only, at
`SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt`. No article text was
read, and none is emitted (see Rights below).

## 1. What was built

| Artifact | Rows | What it is |
|---|---:|---|
| `data/etym/kewa_index_normalized.tsv` — **local-only, gitignored** | 11,418 | one row per **heading** (the source has one line per printed *block*, which may head several variants). It carries the printed headings themselves, so it stays out of the repository while the permission terms are untranscribed; [`kewa_index_normalized.manifest.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_index_normalized.manifest.json) commits its row count, columns and sha256 instead, and `kewa_normalize.py` regenerates it in seconds |
| [`data/etym/kewa_noise_census.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_noise_census.json) | — | the noise-class census of §2 |
| [`data/etym/kewa_pwg_crosswalk.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_pwg_crosswalk.tsv) | 11,418 | the join, one `match_basis` per row, `lane = modern-IE` |
| [`data/etym/kewa_pwg_crosswalk_summary.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_pwg_crosswalk_summary.json) | — | counts of §3 |
| [`data/etym/kewa_join_adjudication_sample.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_join_adjudication_sample.tsv) | 72 | the class-weighted adjudication sample of §4 (seed 3169) |
| [`data/etym/etym_lane_coverage.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/etym_lane_coverage.json) | — | the two-lane overlap of §6 |

Scripts, all in
[`RussianTranslation/src/etym/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/etym):
[`kewa_parse.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/kewa_parse.py) ·
[`kewa_accent.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/kewa_accent.py) ·
[`kewa_hk.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/kewa_hk.py) ·
[`kewa_normalize.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/kewa_normalize.py) ·
[`join_kewa_pwg.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/join_kewa_pwg.py) ·
[`sample_kewa_join.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/sample_kewa_join.py) ·
[`lane_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/lane_coverage.py).
Transliteration goes through the canonical
[`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) package
(SHARED_CODE §1) — no local SLP1 table was retyped.

Reproduce, in order:

1. `python RussianTranslation/src/etym/kewa_normalize.py`
2. `python RussianTranslation/src/etym/join_kewa_pwg.py`
3. `python RussianTranslation/src/etym/sample_kewa_join.py`
4. `python RussianTranslation/src/etym/lane_coverage.py`

## 2. OCR-noise census — the index is clean, its *spreadsheet history* is not

The handoff expected OCR noise (broken diacritics, run-together headings, page
furniture). **That expectation is wrong for this file.** 9,587 of 9,588 lines
parse on the first pattern; the one exception is the header comment. There is
no page furniture, no run-together heading, no hyphenation debris.

What the file does carry is damage from a **round-trip through a spreadsheet in
a Russian locale**, which is a different failure class entirely and would have
been invisible to an OCR-shaped audit:

| Class | Rows | What happened | Recoverable? |
|---|---:|---|---|
| `page-date-coerced` | 3 | the page range `10-11` was read as a date and written back as `10.ноя` (also `11.дек`, `дек.13`) | **yes** — the image filename kept `2-010-11-05.jpg`, and the repair reads the page back out of it |
| `spreadsheet-name-error` | 5 blocks / 6 headings | a heading beginning with a hyphen (`-ā`, `-īm`, `-tṛp`, `-dhṛk`, `-prāṇi`) was parsed as a formula and stored as `#ИМЯ?` (`#NAME?`) | **yes** — the machine-key column survived and carries the true form |
| `legacy-font-latin-leak` | 3 | a Devanāgarī consonant is present as a literal Latin `Z` (`मद्गुZअ-`, `Zअरणः`) — the legacy-font code point for श/ष never got mapped | no — flagged, key marked unusable |
| `machine-key-unalignable` | 3 blocks | the two key columns cannot be split N/N against the headings | no — falls back to the printed IAST, flagged |
| `printed-iast-collapses-variants` | 15 blocks | the printed IAST prints one form with a breve (`kākaciñcī̆`) where the Devanāgarī prints two headings | not damage — handled by keying off the machine column, which expands both |

`bound-prefix-or-stem` (995) and `bound-suffix` (37) are editorial notation, not
noise: KEWA's trailing/leading hyphen marking a bound form. The marker is
stripped for the join key and kept as a flag.

### 2a. Two traps worth carrying elsewhere

**The second key column is Harvard-Kyoto, not SLP1.** It reads like SLP1 and
sits where an SLP1 column would sit, but it writes ś as `z`, ṣ as `S`, ṇ as `N`
and the diphthongs as `ai`/`au`. Converting it HK→SLP1 and comparing against
the canonical transcoder's output on the IAST column agrees on **9,930 of 9,931
headings (99.99 %)**; the single exception (`hvātar-`, keyed `hvaAtar`) is a
one-row typo in the source. Joining that column straight against `csl-orig`
(SLP1) would silently drop every headword containing one of those letters —
**5,733 of 11,418 headings, just over half.** The auditor is
[`kewa_hk.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/kewa_hk.py);
it exists to prove the point, not to become a second transcoder.

**Stripping the Vedic accent destroys ś if you do it the obvious way.** KEWA
marks the udātta with a combining acute. NFD-decompose and drop every U+0301
and you also destroy **ś**, which decomposes to `s` + U+0301 — silently turning
every *śa*-word into an *sa*-word before the join. The first run of this
pipeline reported 5,731 "SLP1 disagreements" that were entirely this bug. The
fix is to drop the acute only when the base letter is a vowel (`a i u e o`, and
the vocalic `ṛ`/`ḷ` written base + dot-below):
[`kewa_accent.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/kewa_accent.py).

## 3. The join and its `match_basis`

KEWA heads its **verbal** articles with a finite form (`bhavati`, `śṛṇoti`)
where PWG keys the **root** (`BU`, `Sru`), and its **nominal** articles with the
nominative singular (`aṃśaḥ`) where PWG keys the **stem** (`aMSa`). A surface
join therefore drops not only the verbal core the handoff warned about, but
most of the nominal core too — and the numbers show it:

| `match_basis` | Rows | Share | How it was reached |
|---|---:|---:|---|
| `exact` | 2,023 | 17.7 % | the KEWA key *is* a PWG key1 headword |
| `sandhi/diacritic-normalized` | 5,670 | 49.7 % | final visarga / anusvāra / neuter `-m` dropped, then exact |
| `inflected-form->stem` | 634 | 5.6 % | a form→lemma witness gives a **nominal** PWG headword |
| `finite-form->root` | 632 | 5.5 % | no nominal reading lands in PWG, a **verbal** one does — the dhātu step |
| `ambiguous-multi` | 46 | 0.4 % | the chosen route reaches >1 PWG headword — reported, never picked |
| `unmatched` | 2,413 | 21.1 % | none of the above |
| **matched** | **9,005** | **78.9 %** | |

**A naive surface join would have found 17.7 %.** The ladder takes it to
78.9 %, and the two morphological rungs alone (`inflected-form->stem` +
`finite-form->root`, 1,266 rows) are the part that no amount of string
normalization would have reached.

Witnesses for the morphological rungs are the two form→lemma tables
`SanskritRussian/dcs_form2lemma.tsv` (381,411 forms) and
`SanskritRussian/vidyut_form2lemma.tsv` (28,567). The summary records
`present: true/false` per witness, so a later reader can tell a real zero from
an absent sibling clone.

**No length or sibilant folding is used anywhere**, per
[Uprava DEAD_ENDS §7](https://github.com/gasyoun/Uprava/blob/main/DEAD_ENDS.md) —
folding collapses exactly the minimal pairs that define Sanskrit lexical
identity. The only string operations applied are morphological truncations of a
citation form.

Every row also carries `lemma_route` (what the witness route *would* have said)
and `routes_agree`, so the rung that lost is never thrown away. 612 rows have
the two routes disagreeing; §4 adjudicates twelve of them.

## 4. Hand adjudication — 72 rows, class-weighted

Sample: [`kewa_join_adjudication_sample.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/etym/kewa_join_adjudication_sample.tsv),
drawn by
[`sample_kewa_join.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/etym/sample_kewa_join.py)
with seed 3169, weighted toward `finite-form->root`, `ambiguous-multi` and the
`routes-disagree` flag — the three places where a wrong join fabricates an
etymology.

**Adjudicator: Opus 5 (`claude-opus-5`), not a human.** That is a real
limitation and is stated rather than papered over: it is a competent
morphological reading, not an editorial sign-off by Dr. Gasūns.

| Stratum | n | Verdict |
|---|---:|---|
| `finite-form->root` | 20 | 20/20 root correct (`acati`→`aYc`, `dadAti`→`dA`, `hinasti`→`hiMs`, `SfRoti`→`Sru`, …) |
| `ambiguous-multi` | 20 | 20/20 candidate sets **contain** the correct PWG headword; 0 silently collapsed |
| `routes-disagree` | 12 | 12/12 correct **after** the two fixes below (3/12 were wrong before) |
| `inflected-form->stem` | 6 | 6/6 correct (`BaginI`→`Bagin`, `varivaH`→`varivas`, …) |
| `sandhi/diacritic-normalized` | 6 | 6/6 correct |
| `unmatched` | 6 | 5/6 genuinely absent from PWG; 1 false negative (`Kallate`, PWG has the root `Kall`) |
| `exact` | 2 | 2/2 correct |

### Two defects the adjudication caught, both fixed

1. **The witness route outranked identity.** `aknaH` (KEWA अक्नः) was sent to
   the root `aYc` by DCS while PWG's own headword `akna` sat one visarga away.
   A truncation that lands on a PWG headword is an identity on the same lexeme;
   a form→lemma analysis is a morphological *claim* that may pick a different
   one. The rule rung now outranks the witness rung, and the witness result is
   kept in `lemma_route`.
2. **The `-as` homograph trap.** Truncating the visarga off a neuter `-as`
   stem's nominative lands on a *different, existing* PWG headword: `enaḥ` →
   `ena` (a real headword) when the word is `enas`; likewise `adhaḥ`→`adhas`,
   `avaḥ`→`avas`. Whenever the truncation plus `s` is one of the witness
   lemmas, that `-as` stem now wins over the homograph. **129 rows** changed,
   flagged `as-stem-disambiguated`.

Both fixes left the total match rate unchanged at 78.9 % — they move rows
between classes and correct their targets, they do not inflate coverage.

### Sub-classes inside `ambiguous-multi`

Adjudicating all 46 candidates in the 20 sampled rows separates three things
the single class currently conflates, and a future rung should split them:

- **stem-variant duplicates** (6/20) — `devavant`/`devavat`, `arvāñc`/`arvāk`,
  `prāñc`/`prāk`, `dharma`/`dharman`, `vṛṣa`/`vṛṣan`: one lexeme, two PWG
  stem-class headwords. Not ambiguity.
- **spurious witness lemmas** (4/20) — DCS offers `madhu` for `etat`, `iti` for
  `devā`, `tathāvidha` for `saṃdhyā`, `i` for `yantā`. Corpus-tagging noise.
- **genuine ambiguity** (10/20) — including one suppletive pair worth keeping:
  `paśyati` → `dṛś` **and** `paś`, both correct.

## 5. The unmatched residue — 2,413 rows, and how much of it is real

`unmatched` is a reportable class, never collapsed onto a near miss. Sizing it
with truncations the join deliberately does **not** apply (they would need a
morphological witness per row):

| Diagnostic | Rows | Reading |
|---|---:|---|
| `present-stem->root` | 358 | a finite verb heading whose root **is** in PWG, but which no form→lemma witness covers (`Kallate` → PWG `Kall`) |
| `feminine-in-stem` | 118 | a feminine `-ī` whose masculine stem is in PWG (`SIrI` → PWG `SIrin`) |
| `no-nearby-pwg-headword` | 1,921 | genuinely not in PWG key1 (`cUlA`, `JaRati`, `davaraH`, `kuqyapucCA`) |
| `key-unusable` | 16 | the legacy-font leaks and unalignable blocks of §2 |

So **476 rows (19.7 % of the residue) sit one unapplied rung away from a PWG
headword**, which puts the realistic ceiling for this join at ≈83 %, not 79 %.
The remaining ~1,921 are the honest answer to "what does Mayrhofer head that
Böhtlingk-Roth does not": largely Middle- and Modern-Indic forms, tribal and
personal names, and lexicographers' hapaxes.

## 6. Two lanes, separately labelled — and they barely overlap

The C4 ruling requires *traditional* (the Cologne 19th-c. extractors) and
*modern IE* (KEWA, later EWA) never to merge into one undifferentiated
`etymology` field. The crosswalk carries `lane = modern-IE` in column 1 so the
separation is a property of the data, not of a convention someone must remember.

Measured against the traditional lane
(`csl-orig/v02/pwg/pwg_etymology.tsv`, 11,527 rows) over PWG key1:

| | PWG headwords |
|---|---:|
| reached by **modern IE** (KEWA) | 7,157 |
| reached by **traditional** (Cologne) | 11,087 |
| **both lanes** | **1,665** |
| modern IE only | 5,492 |
| traditional only | 9,422 |
| neither | 89,503 |

The two traditions agree on which headword deserves an etymology **only 1,665
times** — 23 % of the modern lane, 15 % of the traditional one. They are
complementary, not redundant, which is the strongest argument yet for keeping
them as two labelled fields rather than one merged one.

## 7. EWA — the crosswalk shape it will need

EWA (Mayrhofer, _Etymologisches Wörterbuch des Altindoarischen_, 1986–2001) is
out of scope here. When it lands it should reuse this pipeline unchanged except
for three things:

1. **A `source` column** (`KEWA` / `EWA`) beside `lane`, because both are the
   *modern IE* lane and a reader must still be able to ask which of the two
   said it — and where they differ, since EWA revises KEWA rather than merely
   extending it.
2. **A `supersedes` relation**, not a merge: an EWA row for the same headword
   marks the KEWA row superseded, and both stay. A merged field would silently
   destroy the 1953–1980 vs 1986–2001 distinction that makes the pair useful.
3. **The same volume/page pointer discipline** — EWA's three volumes number
   independently, so `vol` must stay a string, not an integer.

Nothing in the current schema blocks any of that.

## 8. Rights

**What is known.** MG holds written permission from Mayrhofer covering KEWA and
EWA. The OCRed heading index is already committed, publicly, in
[gasyoun/SamudraManthanam](https://github.com/gasyoun/SamudraManthanam), and the
page images it points at are served from `samskrtam.ru`, both under that
permission.

**What is not known.** The permission email has not been located or transcribed,
so its exact terms are not quoted anywhere in any repository. That remains a
human `@DO` — an agent cannot locate MG's correspondence.

**What is committed, and what is not.** The crosswalk, the censuses, the
adjudication sample and the lane-coverage report are committed — they are
derived measurements keyed on SLP1. The normalized index, which carries the
Devanāgarī and printed-IAST headings, is **gitignored**; only its manifest
(rows, columns, sha256) is committed, and it regenerates from the public source
in seconds. That is a deliberate minimization, not a claim that the headings are
secret — they are already public in SamudraManthanam.

**What this handoff did about it.** Per
[STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md),
the uncertainty is recorded and the build proceeded. The artifacts carry
**headings, volume and page pointers only** — no KEWA article text, no
etymological content, no image payload was read or emitted. Untranscribed terms
gate **publication-tier** surfacing of KEWA text (a reader UI showing article
text, a redistributed index), not this internal derived layer.

## 9. What is deliberately not here

- **No evaluation of the crosswalk against anything.** Building the yardstick
  and using it in one pass is how a yardstick gets bent.
- **No canonical-store mutation, no `csl-orig` edit, no paid PWG run.**
- **No merged `etymology` field.** See §6.
- **No collapse of an unmatched heading onto a near-miss headword** to raise
  coverage. 21.1 % unmatched is the honest number, and §5 says how much of it is
  reachable and how.

_Dr. Mārcis Gasūns_
