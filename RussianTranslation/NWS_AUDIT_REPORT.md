# NWS attribution-parser audit — cumulative report

**Status: living document.** Updated as each alphabet section is audited.
Last section folded in: **n** (sections **b–n** complete; the a-section was the
original development pilot, validated per-key via `nws_split.py check` rather
than this split-preview format).

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

## Cumulative roll-up (b–n)

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
| **Σ** | **42,976** | **11,038** | **28,901** | **5** | **129** | **55** | **0.190%** |

Notes: `f` = SLP1 `f` = ṛ. The 0.68% in `l` is the small-base effect of one
`*NNN` cluster over just 735 entries, not a new gap. All 5 bleeds (g: 2 × `gam`,
k: 3 × `kar`, all `Hillebrandt 1885 : IV`) leave the owner correct and produce
**0 residual contamination** after the debleed.

## Real-loss taxonomy (all 55)

Every real no-owner falls into a documented known-limitation class or is bad
input. **No parser bug has been found.**

| class | count | example | code action |
|---|--:|---|---|
| Meister `(2.1)` | 27 | `Meister 1988 (2.1) : 397` | none — name with `.` inside `(2.1)` excluded by design |
| Böhtlingk `*NNN` | 7 | `Böhtlingk 1887 : *163` | none — asterisk page; admitting it regressed `ap`/`av` |
| roman page | 11 | `Walter 1893 : XXXII` | none — digit-only page; roman pages destabilise alignment |
| page-less x-ref | 9 | `duHzvapnya → s.v. duṣvápnya` | none — benign; no `: page` exists to parse |
| source-data typo | 1 | `vṛtrakhādá → … NṚV 2B : 79 (s. (2. khād )` | none — bad input → [NWS errata](#nws-source-data-errata) |

The first three classes were each tried in `nws_split` and reverted: admitting
the token (a `.` inside the name, a roman page, an asterisk page) turns co-owner
segments into gloss-closers and destabilises segment/owner alignment. They are
rare, terminal, and confined to a few works (Meister 1988, Walter 1893,
Böhtlingk 1887). See [CHANGELOG.md](CHANGELOG.md) "Known limitations" for the
full rationale and the guarding selftests.

## NWS source-data errata

Defects in the NWS source itself (not parser gaps), to report to the Halle
maintainers — see [DICTIONARY_CHAIN.md](DICTIONARY_CHAIN.md) for the project.

| headword | as printed | should read | section |
|---|---|---|---|
| `vṛtrakhādá` | `NṚV 2B : 79 (s. (2. khād )` | `NṚV 2B : 79 (s.v. 2. khād )` | k |

The two sibling entries under the same head (`amitrakhādá`, `vikhādá`) carry the
identical owner `NṚV 2B : 79` with a well-formed `(s.v. 2. khād )`, confirming
the intended form.

## Conclusion (so far)

Across **28,901 NWS entries in 11,038 NWS-bearing keys**, the deterministic
owner-attribution parser recovers the source for all but 55 entries
(**0.190%**), every one of which is an accepted known limitation or a single
source typo. Zero parser bugs; bleeds are cosmetic and fully cleaned. The
audit continues through the remaining sections (o–z).
