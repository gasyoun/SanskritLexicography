# NWS attribution-parser audit — cumulative report

**Status: COMPLETE.** Every SLP1 section has been audited. Sections **b–z** are
folded in below; the a-section was the original development pilot, validated
per-key via `nws_split.py check` rather than this split-preview format. Capital
and long-vowel SLP1 sections (`A`, `I`, `K`, `S`, …) are absorbed into their
lowercase counterparts by the case-insensitive section router
(`scale_route.py`, `k1[:1].lower()`), so no separate capital pass is needed.

This is the standalone evidence dashboard for the NWS owner-attribution audit.
The per-section narrative — including every fix and the reasoning behind each
known limitation — lives in [CHANGELOG.md](CHANGELOG.md). Background on what NWS
is and where it sits in the Petersburg chain is in
[DICTIONARY_CHAIN.md](DICTIONARY_CHAIN.md).

## What the audit does

For each section, `src/nws_audit_section.py <letter>` builds the scaled manifest,
generates the merged pilot inputs (resumably), and runs a deterministic
split-preview that checks, for every NWS entry, that its owner (source citation)
is recovered. It reports four things:

- **bleeds** — a roman-numeral co-owner cite riding onto the front of the next
  gloss (`<tag> ; Name : roman >`). The owner stays correct; only the injected
  owner map is cosmetically contaminated, and the `nws_owner_map` debleed cleans
  freshly-generated maps (verified by *residual contamination: 0*).
- **no-owner** — entries whose owner could not be recovered, split into *benign*
  (empty terminal segments, no owner expected) and *real* losses.
- **OTHER** — any unclassified no-owner fragment; the only result that warrants
  investigation before recording.
- **cross-check** — owner-map entry count vs split-preview entry count, and the
  `[NWS: ?]` count vs the no-owner count. Must read OK.

## Cumulative roll-up (b–z, complete)

| sec | keys | NWS-bearing | entries | bleeds | benign | real | real % |
|---|--:|--:|--:|--:|--:|--:|--:|
| b | 4,613 | 971 | 2,655 | 0 | 4 | 7 | 0.26% |
| c | 2,366 | 719 | 1,828 | 0 | 8 | 9 | 0.49% |
| d | 6,019 | 1,439 | 3,808 | 0 | 14 | 4 | 0.10% |
| e | 663 | 203 | 470 | 0 | 2 | 1 | 0.21% |
| f | 339 | 156 | 502 | 0 | 1 | 0 | 0.00% |
| g | 3,354 | 974 | 2,866 | 2 | 8 | 1 | 0.03% |
| h | 2,027 | 466 | 1,353 | 0 | 8 | 2 | 0.15% |
| i | 777 | 281 | 1,045 | 0 | 3 | 1 | 0.10% |
| j | 2,089 | 506 | 1,207 | 0 | 6 | 0 | 0.00% |
| k | 8,637 | 2,590 | 6,530 | 3 | 28 | 11 | 0.17% |
| l | 1,464 | 286 | 735 | 0 | 6 | 5 | 0.68% |
| m | 6,350 | 1,425 | 3,495 | 0 | 17 | 11 | 0.31% |
| n | 4,278 | 1,022 | 2,407 | 0 | 24 | 3 | 0.12% |
| o | 461 | 129 | 306 | 0 | 0 | 0 | 0.00% |
| p | 11,095 | 2,878 | 6,863 | 0 | 73 | 17 | 0.25% |
| q | 105 | 18 | 42 | 0 | 1 | 1 | 2.38% |
| r | 2,905 | 656 | 1,770 | 0 | 8 | 1 | 0.06% |
| s | 18,140 | 4,297 | 10,588 | 0 | 73 | 15 | 0.14% |
| t | 3,477 | 821 | 1,968 | 0 | 12 | 3 | 0.15% |
| u | 2,903 | 1,126 | 2,656 | 0 | 34 | 5 | 0.19% |
| v | 9,658 | 2,418 | 6,526 | 0 | 65 | 14 | 0.21% |
| w | 92 | 19 | 45 | 0 | 1 | 0 | 0.00% |
| x | 3 | 2 | 9 | 0 | 0 | 0 | 0.00% |
| y | 1,810 | 420 | 1,286 | 0 | 1 | 2 | 0.16% |
| z | 302 | 64 | 112 | 0 | 1 | 1 | 0.89% |
| **Σ** | **93,927** | **23,886** | **61,072** | **5** | **398** | **114** | **0.187%** |

Notes: SLP1 consonant/vowel sections — `f` = ṛ, `q` = retroflex ḍ, `w` =
retroflex ṭ, `x` = vocalic ḷ, `z` = ṣ. The elevated rates in the tiny sections
(`q` 2.38 %, `z` 0.89 %, `l` 0.68 %) are small-base effects (a single Meister
or `*NNN` cite over 42 / 112 / 735 entries), not new gaps. All 5 bleeds (g: 2 × `gam`,
k: 3 × `kar`, all `Hillebrandt 1885 : IV`) leave the owner correct and produce
**0 residual contamination** after the debleed.

## Real-loss taxonomy (all 114, final)

Every real no-owner falls into a documented known-limitation class or is bad
input. **No parser bug has been found.**

| class | count | example | code action |
|---|--:|---|---|
| Meister `(2.1)` | 51 | `Meister 1988 (2.1) : 397` | none — name with `.` inside `(2.1)` excluded by design |
| Böhtlingk `*NNN` | 9 | `Böhtlingk 1887 : *163` | none — asterisk page; admitting it regressed `ap`/`av` |
| roman page | 20 | `Walter 1893 : XXXII` | none — digit-only page; roman pages destabilise alignment |
| page-less x-ref | 24 | `duHzvapnya → s.v. duṣvápnya`; `śelu → Olivelle 2013 : śelu` | none — no numeric `: page` exists to parse |
| multi-page cite | 7 | `TPSI 3 : 19, 22`; `Ensink 1964 : 156, viii` | none — comma-joined page list; single-token page by design (see below) |
| `(pw)` lowercase name | 1 | `… Graßmann 1873 (1996). (pw) : 1531` | none — capital-initial name class by design; canonical `PW : 1531` parses |
| source-data typo | 2 | `vṛtrakhādá → … NṚV 2B : 79 (s. (2. khād )` | none — bad input → [NWS errata](#nws-source-data-errata) |

The roman-page, asterisk-page, and multi-page classes share one cause —
OWNER's page is a single digit-only token (`\d+[A-Za-z]?`) that must close the
gloss — and admitting roman/`.`/`*` tokens was each tried in `nws_split` and
reverted, because it turns co-owner segments into gloss-closers and
destabilises segment/owner alignment. The multi-page cite (`TPSI 3 : 19, 22`,
new in p, recurring in r and s) is the same family: broadening the page to a
comma-joined list would let trailing comma-separated gloss content be misread
as page numbers, so it stays out by the same design. The `(pw)` lowercase-name
case (new in s) shares the `Meister (2.1)` name-class cause: OWNER is
capital-initial, and the canonical `PW : 1531` parses. They are rare, terminal,
and confined to a few works (Meister 1988, Walter 1893, Böhtlingk 1887, TPSI,
Ensink 1964). See
[CHANGELOG.md](CHANGELOG.md) "Known limitations" for the
full rationale and the guarding selftests.

## NWS source-data errata

Defects in the NWS source itself (not parser gaps), to report to the Halle
maintainers — see [DICTIONARY_CHAIN.md](DICTIONARY_CHAIN.md) for the project.

This table lists only the defect that breaks **owner attribution** (the one this
audit is scoped to). A separate structural scan of the full NWS corpus found
**70 entries** with unbalanced delimiters (mostly a dropped closing `)`
mid-gloss, invisible to attribution). The complete located list is generated
locally by [`src/_nws_defect_list.py`](src/_nws_defect_list.py) →
`NWS_SOURCE_DEFECTS.md` (gitignored — it is a personal to-do artifact, tracked
in `../Uprava`); the consolidated report to Halle is drafted in
[NWS_ERRATUM_EMAIL.md](NWS_ERRATUM_EMAIL.md).

| headword | as printed | should read | section |
|---|---|---|---|
| `vṛtrakhādá` | `NṚV 2B : 79 (s. (2. khād )` | `NṚV 2B : 79 (s.v. 2. khād )` | k, v |

This single defect costs an owner in two section-fragments: the v-keyed
headword `vftraKAda` (= vṛtrakhāda) and the khād-root fragment `KAd` in k
(hence the two `source-data typo` losses in the taxonomy).
The two sibling entries under the same head (`amitrakhādá`, `vikhādá`) carry the
identical owner `NṚV 2B : 79` with a well-formed `(s.v. 2. khād )`, confirming
the intended form.

## Conclusion (complete)

Across **all 61,072 NWS entries in 23,886 NWS-bearing keys** of the full SLP1
universe (sections a–z), the deterministic owner-attribution parser recovers
the source for all but 114 entries (**0.187 %**), every one of which is an
accepted known limitation or a single source typo. Zero parser bugs; the 5
bleeds are cosmetic and fully cleaned (0 residual contamination, every
section). The seven loss classes — Meister `(2.1)`, Böhtlingk `*NNN`, roman
page, page-less x-ref, multi-page cite, `(pw)` lowercase name, and one
source-data typo — are all rare, terminal, and confined to a handful of works;
none warrants a code change (each was tried in `nws_split` and reverted, or is
bad input). **The NWS attribution audit is complete.**

*Coverage note:* a–z exhausts the SLP1 key space. A first-char scan of the full
merged index finds 10 keys outside a–z — punctuation/digit-leading junk (`(nu`,
`11`, `5)`), a stray `см.↑` cross-reference, and mojibake with literal-IAST or
Cyrillic initials (`Īdfkza…`, `ргаdA`, `араnI`, `расбpacati…`, `араbAD`,
`араbrU`). All 10 are non-SLP1 index artifacts and **none carries an NWS
fragment** (0 NWS entries), so they are out of scope here; they are an index
hygiene matter, not an NWS attribution one.
