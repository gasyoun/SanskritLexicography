# Why the compound review sheet was unanswerable — and the gate that stops it recurring

_Created: 29-07-2026 · Last updated: 29-07-2026_

_Measured by Opus 5 (1M context) (`claude-opus-5[1m]`) for [H1887](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1887-Opus_SanskritLexicography_compound-differs-sheet-evidence-recut_29.07.26.md).
Deterministic; no LLM in the measurement path. Scripts:
[`src/review_evidence_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_evidence_preflight.py),
[`src/pilot/build_compound_rule_ratification_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_compound_rule_ratification_sheet.py)._

## The complaint

MG, voting
[`sanskritlexicography-pwg-compound-differs_stratified200`](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md)
(H1628, 200 cards): «Я не понимаю, зачем мне голосовать». Then nine numbered
points, and the general ruling that a sheet reusing nothing we already know, with
no hyperlinks, is a waste of human time.

Every point was checked against the data. All nine hold, and two are worse than
stated.

## The headline: the answers already existed

[`research/pwg_compound_differs_adjudication.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_adjudication.tsv)
(H1681, 26-07-2026) had already adjudicated the **entire** 4,246-row queue from the
**same two input files the sheet itself reads**, with a named rule and cited
evidence per row.

| | |
|---|---:|
| cards on the sheet | 200 |
| cards that already had a machine verdict, rule and reason | **191 (96 %)** |
| evidence fields available per card, rendered by the sheet | **0 of 7** |

Available and unrendered, per card: `mw_k2_raw` (191/191), `pwg_source_paren`
(191/191), `reason` (191/191), `mw_first_variant` (191/191), `L_id` (191/191),
`evidence` (181/191), `dcs_freq` (72/191).

MG's own two examples, in full:

| | `bṛhatkāya` | `sapāduka` |
|---|---|---|
| shown to him | `bfhant + kAya` vs `bfhat + kAya` | `sa + pAdukA` vs `sa + pAduka` |
| verdict on disk | `pwg_members-right` | `pwg_members-right` |
| rule on disk | `same_split_pwg_lemma_form` | `same_split_pwg_lemma_form` |
| PWG's own text | `({#bfhant#} + {#kAya#})` | `(<hom>2.</hom> {#sa#} + {#pAdukA#})` |
| MW's own text | `bfhat—kAya` | `sa—pAduka` |
| reason on disk | "both sources cut the word in the same place; the members differ only in form" | same |

## Point 3 and 17: a third of the sheet was not a decision

Strict per-member equivalence relations (each named and auditable; verified that
`dāna`/`dānin` correctly stays a **real** difference, so the classifier is not
over-collapsing):

| class | in the 4,246-row queue | on the 200 shown |
|---|---:|---:|
| same split, spelling convention only | **1,482 (34.9 %)** | **69 (34.5 %)** |
| — vowel length (`pādukā`/`pāduka`) | 516 | |
| — stem class (`bṛhant`/`bṛhat`) | 461 | |
| — sandhi form (`akutas`/`akuto`) | 396 | |
| — final -m / mixed | 109 | |
| different member count | 76 (1.8 %) | 20 |
| genuine boundary shift | 54 (1.3 %) | 1 |
| genuinely different material | 2,634 (62.0 %) | 110 |

Both examples MG picked unprompted land in the first row.

## Points 2 and 12–13: the «Пāṇini» line was fabricated half the time

`panini_sutras` comes from
[`SanskritGrammar/data/pwg_panini_crosswalk/`](https://github.com/gasyoun/SanskritGrammar/tree/main/data/pwg_panini_crosswalk).
The Aṣṭādhyāyī is 8 adhyāyas × 4 pādas, ~3,983 sūtras. Measured at source:

| | count | share |
|---|---:|---:|
| distinct "sūtra" keys in `pwg_panini_sutra2word.tsv` | 14,417 | |
| structurally impossible (adhyāya > 8) | 5,766 | 40.0 % |
| structurally impossible (pāda > 4) | 4,968 | 34.5 % |
| **total impossible** | **10,735** | **74.5 %** |

The extractor's regex takes every `a,b,c`-shaped citation in the entry, so Vedic
and epic references were relabelled as grammar. `indrasena → P.10.85.38` is
**ṚV 10.85.38**, the Sūryā bridal hymn where Indrasenā actually occurs.
`haryaśva` carries `P.4.1.104` (real, corroborated by gaṇa `bidādiḥ`) plus six
Ṛgveda citations. On the sheet: 44 of 200 cards showed a «Пāṇini» line, **18 of
them impossible** — including MG's `bṛhatkāya` (`P.9.21.22`). Upstream repair is
[H1888](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1888-Sonnet_SanskritGrammar_panini-crosswalk-nonpanini-citation-purge_29.07.26.md);
downstream, impossible references are now suppressed and counted, never shown.

## Points 14 and 15: the data MG asked for was already on the card, unlabelled

«Членение в указателе (index) — что это за такой указатель?» and «Funderburk
подготовил отдельную разбивку самас… их тут нужно задействовать».

The "index" **is** Funderburk's work: `headword_index.compound_members` comes from
`mw_compounds.py`, Jim Funderburk's em-dash segmentation of MW's `<k2>`. So the
card was already showing PWG against MW/Funderburk — with neither side named.
Confirmed independently by joining MW key2 dash-truth onto the queue: the index
matches MW's own hyphenation on 1,363 rows and PWG's on 2. It is not a third
opinion to fetch; it is one of the two already there.

The two sides were never built to one specification, which is the whole story:
**PWG names the members as lexemes** (etymology parenthesis, lemma form);
**MW/Funderburk segments the surface** (members concatenate back to the headword
by construction). Most of the queue is two conventions meeting, not a dispute.

## Why nothing caught it

| layer | why it did not fire |
|---|---|
| the two scripts | `compound_differs_review_sample.py` and `adjudicate_compound_differs.py` are siblings reading the same inputs and sharing 4,246/4,246 row ids; nothing makes the sheet read the adjudicator's output |
| handoff order | sheet minted first (H1628, 25-07), adjudicated second (H1681, 26-07), never re-cut; the index still read "Awaiting vote" |
| the standard | V1–V8 + H1808 are **entirely presentation** — type scale, anatomy colour, tooltips, ids, note height. The H1628 sheet is fully standard-compliant and still unanswerable |
| the hook | `posttooluse_review_sheet_legibility.py` lints escaped markup and link presence; it cannot see a file two directories away |
| the prose rule | "check prior art before building" existed and did not fire — it depends on the author remembering to look |

## The gate

[`review_evidence_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_evidence_preflight.py)
runs **before** a sheet is written and raises rather than returning a warning.
Six checks: mechanical prior-art overlap · evidence floor · script purity ·
transliteration-scheme leakage · citation linkability · structural validity of
cited references.

The prior-art check is the load-bearing one and is deliberately mechanical: given
the sheet's row ids, it scans the repo for every other artifact keyed on the same
ids and demands each be either **joined** or **omitted with a stated reason**. A
conceptual omission ("no DCS sentence map exists") has no path and cannot silence a
found file — only `declare_omitted_path()` can, so a real artifact is never waved
away by a vaguely-worded note.

Run against the sheet MG complained about, with the manifest the H1628 generator
would have produced (it declared nothing), it returns **12 blocking findings** —
finding 9 being `research/pwg_compound_differs_adjudication.tsv`, 192 of 200 ids,
96 %. It also names the mixed script, the SLP1 leak, and six impossible citations.

It caught two real defects in the replacement sheet during development
(raw-SLP1 source cells, undeclared sibling artifacts), which is the point.

## The replacement ask

[`build_compound_rule_ratification_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_compound_rule_ratification_sheet.py)
— **30 cards, not 200**. Per MG's ruling of 29-07-2026, the human ratifies the
seven auto-resolving **rules**, not the rows:

| rule | rows it resolves | cards |
|---|---:|---:|
| `same_split_pwg_lemma_form` | 3,152 | 10 |
| `pwg_lexeme_vs_mw_suffixed_tail` | 334 | 4 |
| `mw_cut_leaves_nonword` | 293 | 4 |
| `mw_anusvara_right_of_boundary` | 107 | 3 |
| `mw_cut_absorbs_initial_vowel` | 67 | 3 |
| `mw_splits_derivational_suffix` | 14 | 3 |
| `mw_splits_bound_morph` | 8 | 3 |
| **total** | **3,975** | **30** |

Each card carries both splits in IAST, both dictionaries' own printed text
(transliterated, exact SLP1 on hover), what each convention is, the glossed
difference, DCS frequency or a stated reason there is none, and 157 links across
the sheet (kosha co-location, PWG scan column, Cologne MW, ashtadhyayi.com).
`<ab>` abbreviations are glossed through `pwg_ab_ru.display()`.

## Known gaps, stated rather than hidden

- **No per-headword samāsa type.** SamasaChakram has a 58-subtype taxonomy and 20
  worked plates but no headword→subtype mapping exists in any repo. The card says
  so and links the wheel.
- **No per-compound DCS sentence.** The DCS attestation tables in `research/` are
  sense-level for PWG entries, not headword-level for compounds. Frequency is
  joined; an attested sentence is not available.
- **Two emitter strings stay English** — the per-card "Defer" button and the
  "Reason" select label are not reachable through `csl_pyutil` 0.7.0's
  `UI_STRINGS`. Folded into
  [H1889](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1889-Opus_csl-pyutil_review-sheet-v9-evidence-gate_29.07.26.md)
  rather than patched with per-caller post-processing.
- **`w`/`q` are not SLP1 leak markers.** English `sw`/`tw`/`dw` clusters are too
  common; an all-lowercase w/q token can slip. In practice it shares a card with
  an uppercase-marked member, which is caught.

_Dr. Mārcis Gasūns_
