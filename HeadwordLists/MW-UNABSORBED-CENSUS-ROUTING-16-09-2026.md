# Routing note — which MW-unabsorbed census table goes into the guide, the book chapter and the article

_Created: 16-09-2026 · Last updated: 17-09-2026_

H5011 deliverable (MG 16-09-2026 routing ruling): the csl-corrections#119 answers must become
(1) part of guides, (2) part of the book / the MW-copycat article. This note names **exactly**
which artefact lands in which surface. Source artefacts:
[`MW-UNABSORBED-CENSUS-WIDENED-16-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-WIDENED-16-09-2026.md) +
its three TSVs (POS-CLASS, HOMONYM-EXTENSIONS, ALL-LAYERS).

## 1 · Guide surface (chosen, with the reason)

**Chosen:** [`MANUAL_LEXICON_WORKSPACE_AGENTS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_AGENTS.md),
new **§7 · How to check MW against the PW/PWK Nachträge — the five-class taxonomy**.

_Rejected:_ the `csl-guides` repo. Reason: the manual is the workspace's own agent-facing
"canonical-doc index / where results go" surface (its §2 and §6), it is the sheet a next session
actually reads before touching MW↔PW comparisons, and the taxonomy is operational (how to *run*
the check) rather than a general CSL guide. The Russian human twin
[`MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md)
gets a pointer line to §7 in a follow-up translation pass — flagged as a residual, not done here
(translation is a separate lane).

## 2 · Book chapter — ruled 17-09-2026

**Target:** [`Digital_Sanskrit_Lexicography-BOOK/chapters/ch12_apparatus_not_errors.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch12_apparatus_not_errors.md)
("MW is a structural copycat of Böhtlingk's apparatus"). **MG ruled the chapter home is ch12 §3** —
the *inheritance* part, **not** §4 ("the errors": the census measures omissions, not errors) and not
ch14 (OCR-typology by Katre) or ch11 (Nachträge as borrowed-key dictionaries).

| census element | lands at | as |
|---|---|---|
| the 571 homonym-extension class + the class list (§1, §3, §4 of the widened doc) | new **§3.5 "The unabsorbed residual"**, after §3.4 | the *negative space* of §3.3, which measures where MW's homonym splits **match** Petersburg (64–77 %); §3.5 measures where they do not |
| ALL-LAYERS table + POS-CLASS table | **appendix** (BOOK_PLAN §6 appendix mechanism), cited from §3.5 | **the chapter stays prose** — ch12 is the least table-dense chapter (9 pipe-lines vs ch01's 188); tables are the appendix's business |
| method (canary-locked MW-max-hom) + `mw_unabsorbed_census.py` | **§7 Reproducibility** | regenerate-script link, alongside the committed forensic suite |

**Ruled numbers for the chapter:** the **571** class **plus the class list** (8,406 new · 4,112
never-seen · 27 dropped · 610 fold-twin · 2,743 starred residue) — one prose paragraph, not a table.

## 3 · Article derivation — ruled 17-09-2026

**Target:** [`csl-atlas/docs/articles/article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md)
(journal version; the chapter is its book-form conversion — keep the two derived from one another).
The article **already owns "shared omission" at §3.5**, with a `data/forensic/` companion
(`SHARED_OMISSION_TEST.md`) — the Nachträge census is that section's digitization-era complement.

| census element | article section |
|---|---|
| the 571 class (one number + the canary) | **folded into the existing §3.5**, not a new subsection |
| the full census (TSVs + method) | a **companion file in `data/forensic/`**, same pattern as `SHARED_OMISSION_TEST.md` / `SENSE_ORDER_TEST.md` |
| builder + reproduction command | §7-equivalent reproducibility note |

## 4 · Method note (both surfaces)

The one claim that must travel with every table: **the MW `<h>` / pw `<hom>` numbering is not
proven 1:1 comparable** (the count moves 498–626 across definitions, §5 of the widened doc). Copy
the caveat, not just the number.

## 5 · Posted (superseded the "not posted" note)

The widened census **was posted** to [csl-corrections#119](https://github.com/sanskrit-lexicon/csl-corrections/issues/119)
on MG's ruling «постим» (16-09-2026) — [comment 5704062630](https://github.com/sanskrit-lexicon/csl-corrections/issues/119#issuecomment-5704062630):
the 564→571 correction with the full 498–626 band, the POS cross-cut, the 36-dict corroboration,
the all-layer table and the class list.

## 6 · MG rulings, 17-09-2026 (grillme transcription — verbatim answers)

| # | question | ruling |
|---|---|---|
| 1 | which chapter owns it | **ch12 §3** |
| 2 | table or conclusions | **tables → appendix** (chapter stays prose) |
| 3 | where inside ch12 | **new §3.5** |
| 4 | article shape | **number into §3.5 + companion file** |
| 5 | which numbers | **571 + class list** |
| 6 | routing note §4.4 | **re-point to §3.x** (done in this pass) |
| 7 | Brill/DOI | **GitHub footnote now, DOI in the FAIR sprint** |
| 8 | mint shape | **one H###, both surfaces, OxAlpha** |

Rulings 1–6 are applied to this note in the same pass; ruling 8 is the mint; ruling 7 files a GTD
candidate row for the FAIR/DOI sprint (the census TSVs join the deposit list).

_Гасунс_
