# Data statement — Reverse Dictionary of Sanskrit

_Created: 07-07-2026 · Last updated: 07-07-2026_

A [Bender & Friedman (2018)](https://aclanthology.org/Q18-1041/)-style data statement,
following the current [schema v3 (2024)](https://techpolicylab.uw.edu/data-statements/)
(17 fine-grained elements from Curation Rationale through Dataset Maintenance, grouped
below under their core headings). Written per
[`ACL_DH_COMPATIBILITY_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md)
§4 step 4 ([H270](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H270-Sonnet_SanskritLexicography_reverse-dict-publication-prep_07.07.26.md)),
which explicitly calls for honesty about undecided distribution status rather than
waiting for the licensing ruling — several elements below are marked **undecided** on
purpose, not left blank by oversight.

## A. Curation rationale

Compiled to fill an acknowledged gap in Indological reference tooling: no reverse
(suffix-sorted) dictionary of Sanskrit existed at this scale before this project
(Schwarz 1974's ~130,000-word German reverse dictionary was the prior state of the art).
A reverse index supports word-formation research, verse/meter composition (finding
words ending in a given syllable), and identifying partial word-forms in damaged
manuscripts — uses a front-alphabetized dictionary cannot serve. Selection criterion:
every headword attested in any of ~30 merged source dictionaries, normalized to stem
form, with ~20,000 inflected "false" forms manually removed. Full rationale in the
compiler's preface,
[`Обратный словарь санскрита.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9E%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D1%8B%D0%B9%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D1%8C%20%D1%81%D0%B0%D0%BD%D1%81%D0%BA%D1%80%D0%B8%D1%82%D0%B0.mdx).

## B. Language variety

Sanskrit (classical + Vedic; individual source dictionaries span both registers without
a per-headword register tag). BCP-47: `sa`. Transliteration: IAST (International
Alphabet of Sanskrit Transliteration), not the Devanagari script — a Devanagari edition
was estimated (832 pp.) but never typeset (see
[`README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md)
"Towards a 2-volume book").

## C. Speaker demographic

Not applicable — this is a compiled lexicographic resource drawing on published
dictionaries, not elicited or transcribed speech/text from living speakers.

## D. Annotator demographic

**Compiler:** Mārcis Gasūns (primary compilation, editorial rulings on sandhi-final
ambiguity, homonym handling). **Algorithmic sorting:** Dhaval Patel (reverse-Devanagari
sort engine,
[`reverse15.php`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/reverse15.php),
2013). **Statistical appendices:** Anton Pilyuganov. No further annotator demographic
data (age, gender, training) is on record for this project — typical for a
single/small-team lexicographic compilation rather than a crowd-annotation effort.

## E. Speech situation / F. Text characteristics

Not applicable in the usual NLP sense (no recorded speech, no running text corpus) —
the unit of data is the isolated headword, drawn from 30 published Sanskrit dictionaries
spanning 1822–2005 (see the source table in
[`SCHEMA.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/SCHEMA.md)).
Each source dictionary has its own compilation era, editorial register, and scholarly
convention (e.g. PWG/PWK are 19th-c. German-school Sanskritology; Kochergina is a
Soviet-era Russian pedagogical dictionary) — this heterogeneity is inherent to a
merged-dictionary reverse index and is not normalized away.

## G. Recording quality

Not applicable (no audio/video).

## H. Other quality control

Cross-checking against Monier-Williams as a control list surfaced digitization/print
errors in other sources, some fed back upstream to the `sanskrit-lexicon` GitHub
organization's own correction workflow (per the compiler's preface). A known outstanding
errata sheet (2018, "typos not fixed by that summer") was investigated this pass
([`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CHANGELOG.md))
and found to already be reflected in the current canonical list. NFC-normalization and
exact/near-duplicate audits were run directly against the canonical file (documented in
`SCHEMA.md`) — zero duplicate lines, zero duplicate words, 100% NFC-conformant.

## I. Provenance appendix

Merge pipeline is **not algorithmically reproducible end-to-end**: most of the 30
sources cannot be freely redistributed, and many editorial rulings (sandhi-final
ambiguity, homonym/POS disambiguation, which of ~20,000 inflected forms to strip) were
manual, not scripted. What *is* documented and reusable: the sort algorithm
([`reverse15.php`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/reverse15.php))
and the editorial rulebook
([`Состав и строй словаря.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BE%D1%81%D1%82%D0%B0%D0%B2%20%D0%B8%20%D1%81%D1%82%D1%80%D0%BE%D0%B9%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D1%8F.mdx),
§1–§10: sort order, exclusions, homonym handling, accent-mark sourcing). Source
coverage stops at 2005 — the Cologne Digital Sanskrit Dictionaries project has
continued digitizing/correcting dictionaries since (the same `sanskrit-lexicon` org
this repo's parent tree serves); a currency check against present-day `csl-orig` would
likely surface both new source dictionaries and corrections, and has not been done in
this pass.

## J. Distribution — **undecided, documented honestly**

**Not currently distributed in any tier.** Publication tier is gated on a pending
human ruling among three options (§3.1 of
[`ACL_DH_COMPATIBILITY_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md)):
**(a)** publish the full 266,820-word list openly (facts-not-expression reading),
**(b)** publish a PD-only subset (drop headwords unique to the ~10 sources still in
copyright somewhere — this pass measured that cost, see
`ACL_DH_COMPATIBILITY_ANALYSIS.md` §5 and the mirrored
[`GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
`@DECIDE` row), or **(c)** keep the data restricted-tier and publish only a descriptive
paper + statistics (the org's existing
[kosha `tier: restricted`](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)
pattern). This data statement, `SCHEMA.md`, and `CITATION.cff` are written now,
independent of that ruling, so the documentation exists regardless of which tier is
chosen — and so the [Responsible NLP Research checklist](https://aclrollingreview.org/responsibleNLPresearch/)
§B (per-artifact license/provenance disclosure) can be satisfied honestly once a
paper is drafted.

## K. Maintenance — **undecided, documented honestly**

No maintenance commitment currently exists — this is unpublished personal research
material (see `README.md` "This is a data/research workspace, not a finished
publication"). If a distribution tier is ruled and the dataset is registered (kosha
manifest / `FEATURES_INDEX.md`, per the analysis's step 7), maintenance would follow
the org's existing pattern for other registered derived datasets — versioned releases
via [`/cut-release`](https://github.com/gasyoun/github-spine/blob/main/CLAUDE.md), a
single maintainer (Gasūns) with corrections routed through the same GitHub-issue
workflow the org already uses for the Cologne dictionaries. No commitment beyond that
exists today.

---

_Dr. Mārcis Gasūns_
