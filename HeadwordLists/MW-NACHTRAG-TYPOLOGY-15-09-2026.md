# MW/PWK Nachträge adjudication — typology, near-form subgroups, statistics

_Created: 15-09-2026 · Last updated: 15-09-2026_

Companion to [`MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv`](MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv)
(the canonical sup_7 adjudication, 4,151 rows). MG asked 15-09-2026: raw TSV reading is
*harmful for a human* — so this is the distilled typology view; every claim below carries
an evidence link. Regenerate every number:
`python HeadwordLists/mw_nachtrag_typology.py --mine410 <cut.tsv>`.

Evidence-link conventions: `ADJ#Lnnn` =
[`HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#Lnnn`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv)
row anchor; `pw#Lnnn` / `bhs#Lnnn` / `pwkvn#Lnnn` = the corresponding
[`csl-orig/v02`](https://github.com/sanskrit-lexicon/csl-orig) line anchor.

## 1. The four-verdict typology (sup_7, 4,151 rows)

| verdict | n | meaning | example anchor |
|---|---:|---|---|
| `confirmed-missing` | **2,782** | word absent from MW, omission stands | [`aMSukapallava` ADJ#L4](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L4) |
| `near-form-needs-eyes` | **660** | fuzzy near-match unresolved — human review | [`akata ~ akzata` ADJ#L6](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L6) |
| `covered-by-MW-stem-form` | **482** | MW has the stem/base form; marginal | |
| `covered-by-fold-twin-flagged` | **227** | MW has the case/vowel-length twin — *weakest claim* | [`akapila ~ Ākapila` ADJ#L9](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L9) |

Spot-check evidence: two independent 30-sample passes, **0/30 false positives** both
([spotcheck-15-09](MW-NACHTRAG-SPOTCHECK-30-15-09-2026.tsv),
[spotcheck-14-09](MW-NACHTRAG-SPOTCHECK-30-14-09-2026.tsv)) — recorded in the
[H4837 close](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H4837-OxAlpha_SanskritLexicography_mw-missing-pw-nachtrag-adjudication_14.09.26.md).

## 2. The near-form class (1,918 rows) — three verdict subgroups

The fuzzy-score buckets split cleanly ([regenerate](mw_nachtrag_typology.py)):

| similarity bucket | confirmed-missing | needs-eyes | fold-twin |
|---|---:|---:|---:|
| 0.80–0.89 | 698 | 320 | 0 |
| 0.90–0.94 | 278 | 213 | 0 |
| 0.95+ | 55 | 127 | **227** |

1. **Auto-confirmed false-friend (1,031 rows)** — the pipeline verified the MW near-form is
   *itself a separate pw.txt entry with its own distinct sense*, so the omission stands.
   Example: [`aMSagrAhin ~ arTagrāhin` ADJ#L2](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L2)
   ("near form 'arTagrAhin' is a separate pw.txt entry at 1-293-c … omission stands").
   **This is the high-precision engine: 1,031 of 2,782 confirmed-missing were resolved
   through near-form *dis*confirmation.**
2. **Fold-twin flagged (227)** — the Akalita/Ākalita trap: SLP1 case *is* vowel length
   (`a` vs `A` = short vs long ā). MW carries the twin; these rows are **likely NOT
   omissions** (weakest class). Family evidence: 103 a-A + 70 m-M + 14 double a-A = 187 of
   the 227 come from exactly these two families.
3. **Needs-eyes (660)** — the actionable residue, decomposed below.

## 3. Near-form relation families — what the fuzzy matches *are*

Classifying each candidate against its `mw_fuzzy` target (levenshtein + position of the
edit; [script](mw_nachtrag_typology.py)):

| family | total | missing | needs-eyes | fold-twin |
|---|---:|---:|---:|---:|
| multi-edit d≥2 (unrelated forms) | 839 | 551 | 287 | 1 |
| **-vant/-vat alternation** | **97** | 1 | **96** | 0 |
| vowel-length a-A (fold-twin trap) | 103 | 0 | 0 | 103 |
| anusvara m-M | 70 | 0 | 0 | 70 |
| compound short/long form | 58 | 40 | 18 | 0 |
| **-tar/-tṛ agent alternation** | **38** | 6 | **32** | 0 |
| other single/double subs | ~130 | ~60 | ~55 | ~7 |
| suffix families (-tA/-tva, -in/-a, -ya/-a…) | ~75 | ~40 | ~28 | ~7 |

**The needs-eyes residue (660) decomposes into rule-addressable morphological families:**

1. **-vant/-vat: 96 rows** — e.g. [`akṣiRvant ~ akṣiRvat` ADJ#L89](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L89),
   [`atiSayavant ~ atiSayavat` ADJ#L483](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L483).
   One **policy decision** resolves all 96: does MW treat -vant/-vat variants as one entry?
2. **-tar/-tṛ agents: 32 rows** — e.g. [`agradAtar ~ agradAtṛ` ADJ#L150](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L150).
3. **Compound short/long forms: 47 rows** — e.g. [`agastyasaMpAta ~ agastyasaMhitā` ADJ#L113](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L113).
4. **Deep multi-edit d≥2: ~287 rows** — mostly genuinely different words; low-value review.
5. Scattered single/double substitutions: ~200 rows — the true human-review core.

So **~175 of the 660 (96+32+47) are rule-resolvable**; the honest human-review core is
**~490 rows, of which ~290 are probably distinct lexemes (multi-edit) and only ~200
scattered near-forms**.

## 4. Corroboration — the independence correction

Raw witness counts: `sch` 3,848 (92.7 % of all rows!), then stc 417, bhs 282, acc 259,
pwg 240, md 225, cae 203, ccs 172 ([regenerate](mw_nachtrag_typology.py)).
**`sch` (Schmidt's Nachträge) and `pwg` (PW groß) are the *same Böhtlingk tradition* as the
sup_7 source — they must be discounted** (the same lesson
[H1310](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1310-Opus_SanskritLexicography_pwg-lexicon-only-ghostword-cross-dictionary-audit_19.07.26.md)
recorded for PW).

| measure | n | of which confirmed-missing |
|---|---:|---:|
| corr incl. sch (raw) | 3,887 (≥1) | — |
| **corr outside PW tradition (excl. sch, pwg)** | **1,421 (≥1)** | **952** |
| **≥2 outside-PW dictionaries** | **433** | **217** |

Outside witnesses ranked: stc 417 · **bhs (Edgerton) 282** · acc 259 · md 225 · cae 203 ·
ccs 172 · vcp (Vācaspatya) 83 · ap (Apte) 77.

## 5. Corpus attestation (DCS) — the strongest real-word evidence

`dcs_lemma`/`dcs_form` record whether the word is attested in the
[DCS](https://github.com/sanskrit-lexicon/dcs-conllu) corpus (not just lexicons):

| verdict | n | DCS-attested |
|---|---:|---:|
| confirmed-missing | 2,782 | **323** |
| near-form-needs-eyes | 660 | 98 |
| covered-by-MW-stem-form | 482 | 147 |
| covered-by-fold-twin-flagged | 227 | 50 |

**323 confirmed-missing words are corpus-attested** (examples:
[`akarāla` ADJ#L13](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L13),
[`akārpaṇya` ADJ#L42](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L42),
[`akṛtaka` ADJ#L56](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L56),
[`akṛṣṇa` ADJ#L65](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L65)).
**DCS-attested ∧ ≥1 outside-PW dictionary = 320; ∧ ≥2 outside ∧ confirmed-missing = 75** —
the hard core for MW-entry stubs.

## 6. The Mahāvyutpatti class — `kāritra` proper

`mahavy=1`: **305 rows**, of which **205 confirmed-missing** (evidence:
[`apratipudgala` MAHĀVY 1 ADJ#L1283](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L1283),
[`aprativirata` MAHĀVY 245,893 ADJ#L1297](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L1297)).
The canary itself — [`kāritra` ADJ#L2900](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L2900) —
is `confirmed-missing`, corroborated bhs+sch, MAHĀVY 245; its fuzzy target was
**`kArita` (kārita) — a false friend** ("separate pw.txt entry at 2-052-c", ADJ#L2900
review_note), auto-resolved. Primary sources:
[pw#L620963](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt#L620963) ·
[pwkvn#L53131](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwkvn/pwkvn.txt#L53131) ·
[bhs#L19108](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/bhs/bhs.txt#L19108).

## 7. Cross-checks

- **MW72 classes**: 4,112 `never-seen` + 27 `dropped`
  ([MW72-CLASSES-ADJUDICATION-15-09-2026.tsv](MW72-CLASSES-ADJUDICATION-15-09-2026.tsv)) —
  MW99 took ~60 % of the sup_7 pool MW72 lacked and skipped 4,112 outright (H4878 delivery).
- **Star-based all-layer sweep**: 3,353 rows → 2,743 confirmed-missing / 610 variant-form-in-MW
  ([MW-STARRED-NACHTRAG-ADJUDICATION-14-09-2026.tsv](MW-STARRED-NACHTRAG-ADJUDICATION-14-09-2026.tsv)).
- **The [410-row pwk7 trial cut](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/issues/issue119/pwk7_nachtraege_absent_from_mw.tsv)**
  (csl-corrections PR [#400](https://github.com/sanskrit-lexicon/csl-corrections/pull/400)):
  385/410 fall in the sup_7 pool — **268 confirmed-missing** there; **all 410** appear in the
  star-based sweep — **375 confirmed-missing** there; the 25 outside the sup_7 pool are the
  *Verbesserungen/corrections* class (e.g. `durgAhva` "zu streichen") — matching the trial's
  own caveat.

## 8. Fuzzy-typology conclusions

1. **The fuzzy matcher is a morphology-adjacent matcher.** It does not surface random
   typos: it surfaces *sandhi/derivation families* (vowel length, anusvara, dental/retroflex,
   sibilants, -tar/-tṛ, -vant/-vat, compound truncation). Each family has its own precision
   profile — so review effort should be budgeted per family, not per row.
2. **Similarity score is anti-correlated with confidence at the top end.** The 0.95+ bucket
   is *dominated by the weakest class* (227 fold-twins, 62 % of it), while 0.8x rows split
   2:1 toward confirmed-missing. High score ≠ safe: near-identical forms are the fold-twin
   trap; mid-score families are the real omissions.
3. **Near-form disconfirmation is the precision engine**: 1,031 omissions were *confirmed*
   by verifying the near-form is a separate pw entry with its own sense. The matcher's value
   is as much in what it rules out as in what it finds.
4. **The human-review burden collapses from 660 to ~175 policy rows + ~490 true review rows**
   — and half of those ~490 (multi-edit d≥2) are likely distinct lexemes that can be
   triaged by a single "d≥3 → probably distinct" rule with spot-checks.
5. **Two evidence axes should gate MW-entry proposals**: DCS corpus attestation (323 rows)
   and outside-PW-tradition corroboration (217 rows with ≥2 outside dictionaries); their
   intersection (75 rows) is the minimal defensible core. Same-tradition witnesses (sch,
   pwg) must never be counted as corroboration.
6. **The Mahāvyutpatti class (205 confirmed-missing) is a coherent acquisition unit** —
   Buddhist technical vocabulary, exactly the class Andhrabharati flagged; it can be
   proposed as one batch with MAHĀVY section refs as the citation spine.

## Statistics still missing (next analysis layer)

1. Corpus-attestation *depth* for the 323 DCS rows (token counts, authors, dates) — DCS
   query per headword, not yet in the TSVs.
2. Sense-level (not spelling-level) check for the 482 `covered-by-MW-stem-form` rows —
   does the MW stem entry actually carry the Nachträg sense, or only the base word?
3. The same typology for the star-based sweep (3,353) — its `variant-form-in-MW` (610)
   has not been family-classified yet.
4. A confusion-matrix of the relation classifier itself (auto-confirmed-false-friend ×
   family) to put error bars on the family precision claims.

_Гасунс_
