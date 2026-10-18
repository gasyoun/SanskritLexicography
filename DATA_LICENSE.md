# Data license

_Created: 13-07-2026 · Last updated: 07-09-2026_

This repository's **code and tooling** (scripts under
[`RussianTranslation/src/`](RussianTranslation/src),
[`HeadwordLists/`](HeadwordLists) tooling, the dashboard generators, etc.) is
MIT-licensed — see [`LICENSE`](LICENSE).

**Derived statistics datasets released as part of FAIR Release #1** — the
markup-tag frequency census
([`data/markup_tag_census.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv)) and the
pairwise headword-overlap matrix
([`data/headword_overlap_matrix.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/headword_overlap_matrix.tsv)) — are
released under **CC-BY-4.0**, matching the convention already used for the
sibling OBS-T dataset in
[csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/DATA_LICENSE.md).
See [`data/FAIR_RELEASE_1.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md) for the full release
package, provenance, and Zenodo deposit metadata.

This CC-BY-4.0 grant covers **only** the two named derived TSV files above —
not the whole repository. FAIR Release #1 is a curated, manually-deposited
dataset release of the two files named above plus a cross-link to the
citation-graph dataset owned by
[csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) (its own CC-BY-SA-4.0
license applies there).

**Superseded 07-09-2026 ([CONTRADICTIONS §17](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md), ruled via
[H3961](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3961-Sonnet_SanskritLexicography_zenodo-governance-match-live-archival_02.09.26.md)):**
the paragraph above previously said a repo-wide Zenodo/GitHub archival
integration was **deliberately not used**, out of concern that it would sweep
in the large primary-source scans (untracked PDF reproductions occasionally
staged in this working tree) whose rights are third-party and unresolved.
That was never accurate: [`.zenodo.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/.zenodo.json) and
[`CITATION.cff`](https://github.com/gasyoun/SanskritLexicography/blob/master/CITATION.cff) show the repo-level integration **live** —
concept DOI `10.5281/zenodo.21306715`, verified against the Zenodo API
31-07-2026, minting on every release publish, with 143 `v1.14x` tags cut as
of 07-09-2026. MG ruled the live posture is the intended one; this document
is amended to match it rather than the integration being disabled.

What that archive actually contains: a GitHub release archive is a snapshot
of the **tracked git tree** at the release tag. The untracked scan PDFs this
paragraph worried about are, by construction, never part of it — they are
untracked and so never staged into a tagged tree in the first place. The
repo's own description in `.zenodo.json` also states plainly that "source
dictionary texts are corrected upstream in `csl-orig` and are not
redistributed here," so no third-party source text is at stake either way.

That does **not** make the curated two-file deposit above redundant. The
repo-level record is typed `upload_type: software`, MIT-licensed, and its
own description says explicitly: "this record's DOI covers the repository,
not any dataset within it." A CC-BY-licensed, dataset-typed, individually
citable DOI for the two TSV files is not something the repo-level software
record provides — the curated deposit described in
[`data/FAIR_RELEASE_1.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md) is still wanted for that reason, independent of the
rights concern that originally (and mistakenly) justified it.

_Dr. Mārcis Gasūns_
