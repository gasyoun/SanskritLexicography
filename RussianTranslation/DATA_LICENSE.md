# pwg_ru data & edition licence

`SPDX-License-Identifier: CC-BY-SA-4.0`

The **pwg_ru dataset and edition** — the assembled cards, the Russian translations
produced by this pipeline, the stratification and `<ls>`→stratum maps, and the
documentation in this directory — are licensed under the **Creative Commons
Attribution-ShareAlike 4.0 International** licence (CC BY-SA 4.0).

- Full text: <https://creativecommons.org/licenses/by-sa/4.0/legalcode>
- Summary: <https://creativecommons.org/licenses/by-sa/4.0/>

You may share and adapt this material for any purpose, provided you (a) give
appropriate credit to the pwg_ru project and the underlying **Petersburg
Dictionary** (PWG, Böhtlingk–Roth), and (b) license your contributions under the
same terms.

## Scope and third-party rights (important)

This licence covers **only the pwg_ru project's own work**. It does **not**
relicense third-party material:

- **The source dictionary PWG** (Böhtlingk–Roth) is in the public domain; we
  credit it, we do not own it.
- **Modern Sanskrit–Russian reference dictionaries** (Kochergina, Smirnov,
  Frisch) remain third-party works, but the project has copyright approvals for
  extensive use in the publishable `pwg_ru` edition. They are therefore **not**
  limited to evidence-only use, and their approved text may appear in card body
  material with source attribution/provenance. See
  [RIGHTS_APPROVALS.md](RIGHTS_APPROVALS.md).
- **Public-domain sources** — **Knauer** (d. 1917) and **Kossowich** (d. 1883)
  — may be quoted verbatim, with attribution, as before.
- **Modern corpus translations** remain tied to their source corpus/project
  permissions. Keep citation/provenance metadata on every reused passage.
- **Elizarenkova's Russian Rig-Veda translation** (accessed via
  [`src/vedaweb_ru_witness.py`](src/vedaweb_ru_witness.py), sourced from VedaWeb 2.0,
  Universität zu Köln) is **CC BY 4.0**, confirmed explicitly for that specific hosted
  resource (see [`CORPUS_PROVENANCE.md`](CORPUS_PROVENANCE.md#rv-citation-witness-vedaweb-cc-by-40--distinct-from-the-corpus-above)).
  This is a separate copy/rights posture from the Elizarenkova text inside the
  `SamudraManthanam` corpus (grey-rights, not redistributed here or anywhere public).

The **code** in this repository is licensed separately; see the repository's
top-level `LICENSE`.

## How to cite

> *pwg_ru: a Russian edition of the Sanskrit–German Petersburg Dictionary (PWG,
> Böhtlingk–Roth), produced with corpus-attested sense harvesting.* Sanskrit
> Lexicon / Cologne Digital Sanskrit Dictionaries. CC BY-SA 4.0.

A machine-readable [CITATION.cff](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CITATION.cff)
sits beside this file and declares the same `CC-BY-SA-4.0` licence. It stays at
`version: unreleased` until the immutable edition cut is archived and a DOI is
registered against it — see [DOI_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DOI_PLAN.md).
