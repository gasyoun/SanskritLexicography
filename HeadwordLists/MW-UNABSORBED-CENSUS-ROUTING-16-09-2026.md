# Routing note — which MW-unabsorbed census table goes into the guide, the book chapter and the article

_Created: 16-09-2026 · Last updated: 16-09-2026_

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

## 2 · Book chapter

**Target:** [`Digital_Sanskrit_Lexicography-BOOK/chapters/ch12_apparatus_not_errors.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch12_apparatus_not_errors.md)
("MW is a structural copycat of Böhtlingk's apparatus").

| census table | lands at | as |
|---|---|---|
| ALL-LAYERS table (§3 of the widened doc) | new **§3.x "What MW left on the table"**, after the current §3 (lines 90–130, "What MW inherited — the apparatus") | the *complement* of §3: the per-layer uptake/skip counts are the quantified residual of the inheritance claim |
| HOMONYM-EXTENSIONS (571) + POS-CLASS table | new **§4.4 "The unabsorbed homonym layer"**, after §4.3 (line 156) | the one class §4 does not yet cover — words MW *heads* but whose further homonyms/senses it did not take |
| method (canary-locked MW-max-hom) + `mw_unabsorbed_census.py` | **§7 Reproducibility** (line 217) | regenerate-script link, alongside the committed forensic suite |

## 3 · Article derivation

**Target:** [`csl-atlas/docs/articles/article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md)
(journal version; the chapter is its book-form conversion — keep the two derived from one another).

| census element | article section |
|---|---|
| ALL-LAYERS + POS-CLASS tables | §4 (the omission complement) as a compact table; essay text in §5 Discussion ("what MW chose *not* to copy is as structured as what it copied") |
| the 571 homonym-extension class + the `kārin`/`kāritra` canaries | a single worked example paragraph in §4, anchored on `pw.txt#L620966` |
| builder + reproduction command | §7-equivalent reproducibility note |

## 4 · Method note (both surfaces)

The one claim that must travel with every table: **the MW `<h>` / pw `<hom>` numbering is not
proven 1:1 comparable** (the count moves 498–626 across definitions, §5 of the widened doc). Copy
the caveat, not just the number.

## 5 · Not routed here

Upstream posting to [csl-corrections#119](https://github.com/sanskrit-lexicon/csl-corrections/issues/119)
is **MG's ruling only** — this note drafts the routing, it does not post. The #119 comment already
carries the dropped-27 full list (16-09-2026); the widened census is *not* posted.

_Гасунс_
