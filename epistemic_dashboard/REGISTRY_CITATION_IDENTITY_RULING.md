# Registry citation-identity ruling — the §-number is a permanent citation key

_Created: 20-07-2026 · Last updated: 20-07-2026_

Ruling for [H1361](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1361-Opus_SanskritLexicography_findings-section-number-collision-ruling-and-dashboard-audit_20.07.26.md)
(Opus 4.8 `claude-opus-4-8`), settling the section-number collisions across
[`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
and its epistemic sibling registries, and the `§447`/`§448` next-free-marker anchor.

## 1. The numbering contract (was implicit in the schema; made explicit here)

A registry §-number is a **permanent, unique citation key**, not a position:

1. **Append-only.** A new entry takes the next free number, whatever thematic
   section it lands in. Gaps are legal and expected; the number never encodes order.
2. **One claim per number.** No two `### §N.` headings in one file may share `N`.
   A number that already labels a published claim is spent forever.
3. **Never shift a published number.** Renumbering an existing entry would break
   every inbound `§N` citation and every dashboard anchor already in the wild.
4. **On a collision, the *later* claim moves.** When two claims were assigned the
   same `N`, the one **published first at that number keeps it** (it owns the
   existing citations); the later reuse is renumbered to a fresh next-free number
   and carries a **tombstone line** naming its old number, the winner, and this
   ruling. When an inbound citation demonstrably names one of the two claims, that
   claim keeps the number regardless of date (the citation is the stronger anchor).
5. **The Index is the classification of record.** Every `### §N.` heading has
   exactly one `## Index` entry and vice versa; a finding's importance dot
   (🔴/🟠/🟡) lives in the Index — 34 findings carry it *only* there — so the Index,
   not the body, is what the dashboards read.

Enforced mechanically by [`tools/epistemic_integrity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/epistemic_integrity_check.py)
(duplicate-number · heading↔Index parity · dangling-index · next-free-marker ·
dashboard↔file count/importance parity), wired into CI before the dashboard builders
and into `pre-commit`.

## 2. The §447 / §448 marker verdict

[§447](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (PWG's
`〉` closing sense-marker glyph) is a **genuine, published finding**, not a typo. Under
rule 1 (append-only, gaps legal) and rule 3 (never shift a published number), **§447
stays**. The otherwise-continuous §1–§104 sequence with a lone §447 is contract-compliant,
not a defect. The "currently §N" next-free marker therefore correctly reads **max heading
+ 1**. After this ruling the four renumbered claims occupy §448–§451, so the marker moves
`§448 → §452`; the validator enforces `marker == max(heading) + 1` going forward.

## 3. Collisions ruled

Each **later / non-cited** claim moved to a fresh number with an in-place tombstone; the
**first-published / cited** claim kept the number. Measured against `origin/master`
20-07-2026.

| File | Number | Keeps it (published first / cited) | Renumbered → | Why the mover moved |
|---|---|---|---|---|
| FINDINGS | §80 | DCS `text_sandhied` (H759, 12-07-2026) | MWScan-`servepdf` CORRECTED (H870, 15-07-2026) → **§448** | later; §80 had zero external citations, so pure publication-date rule |
| FINDINGS | §86 | DCS verbal-feature-density collapse (H1000) | Samāsa-type-frequency ghosts (H989) → **§449** | the one inbound §86 citation (FINDINGS line ~2305) names "verbal-feature annotation collapse" → binds §86 to the density finding |
| FINDINGS | §87 | DCS text→period map (H1000, 16-07-2026) | OBS-T κ=0.42 phantom (H1074/H1076, 17-07-2026) → **§450** | later; and the inbound §87 citation names "the period map" |
| FINDINGS | §103 | union-corroboration deflation (H1363) | `zenodo.15834721` false-DOI (H1364) → **§451** | H1364 appended its claim at an already-taken §103; H1363 published first |
| DEAD_ENDS | §8 | Petersburg-citation shared-error test (10-07-2026) + its **§8b** MBh-locus continuation | PWG/MW `HARIV.` citation test (10-07-2026) → **§9**; Gemini-OCR Sundarakāṇḍa (08-07-2026) → **§10** | §8 kept for the §8/§8b structural pair (moving §8 would orphan §8b); the Gemini entry is marginally older but has no `§Nb` dependent, so it is the safe mover — the one place date yields to structural integrity, logged here per rule 4 |

**CONTRADICTIONS §6×2 — already resolved, not re-touched.** The sibling handoff
[H1364](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1364-Sonnet_SanskritLexicography_contradictions-doi-repair_20.07.26.md)
(PR [#604](https://github.com/gasyoun/SanskritLexicography/pull/604), merged) already
renumbered the duplicate CONTRADICTIONS §6 and ruled the Ch.14 Zenodo DOI dispute;
[CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
is now 8 distinct headings with no duplicate. Per the H1361 coordination note, this pass
extends the shared validator's coverage rather than authoring a competing fix.

## 4. Index backfill

22 headings (§76, §79–§81, §83–§89, §91–§99, §101, §104) were absent from the `## Index`
"stable citation list", plus the four renumbered §448–§451 — **26 entries** backfilled into
an append-only, uncategorised Index subsection. For the backfilled findings that carry **no
importance dot in their body** (a measured-caveat majority), importance was set to **🟠
(important)** as the honest default for this class — none is a trivial 🟡, and blanket 🔴
would overstate; adjust per finding later if warranted.

## 5. What the parsers now do

Both dashboard builders
([`findings_dashboard/build_findings_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/build_findings_data.py),
[`epistemic_dashboard/build_epistemic_dashboard.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/build_epistemic_dashboard.py))
now read importance from the **Index dot** first (body-dot fallback), so the 27/23 findings
that previously parsed to `null` importance are classified, and — with duplicates gone — the
finding count is the true distinct-heading count (95 → **109**). The published board
([/episteme/](https://gasyoun.github.io/SanskritLexicography/episteme/),
[/findings/](https://gasyoun.github.io/SanskritLexicography/findings/)) regenerates to match.

## 6. Follow-on collision — H1350 × H1361 both took §448–§451 (ruled by H1362, 20-07-2026)

This ruling (H1361, PR [#615](https://github.com/gasyoun/SanskritLexicography/pull/615), merged
14:38) assigned §448–§451 to its four movers believing those numbers free. It did not — 40
minutes earlier the **H1350** PWG data-layers wave (PR
[#612](https://github.com/gasyoun/SanskritLexicography/pull/612), merged **13:58**) had already
appended four PWG findings at **§448–§451** (parse-rules census, four-tier `〉` nesting, `h`-field
semantics, `<ls>` 98% coverage). Neither session saw the other; both merged, and `origin/master`
carried duplicate §448–§451 with the integrity gate red — the exact concurrent-append failure
class this ruling was written to prevent, landing on the ruling itself.

**Verdict (rule 4 citation exception).** By publication date alone the H1350 block (13:58) precedes
the movers (14:38) and would keep the numbers. But rule 4's second clause governs: *when an inbound
citation demonstrably names one of the two claims, that claim keeps the number regardless of date.*
The movers are the claims named by **this merged, authoritative ruling** (§3 table) — the strongest
possible citation anchor, since it is the numbering contract of record — as well as the H1361
changelog entry and [FINDINGS.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.meta.md)
history row. The H1350 block's only inbound citations were a session journal and its own changelog
entry, both in-repo and fixable in the same pass. So the **movers keep §448–§451**, and the **H1350
block moved to §452–§455** with in-place tombstones. The next-free marker advances `§452 → §456`.

| Was | Now | Claim (H1350) |
|---|---|---|
| §448 | **§452** | csl-atlas PWG parse-rules census stale/incomplete |
| §449 | **§453** | PWG `〉` nests four enumeration tiers |
| §450 | **§454** | pwg_ru store `h` field inconsistent semantics |
| §451 | **§455** | PWG `<ls>` resolution already 98%+ |

Lesson for the validator, already true in code: the gate is only protective if it runs **on
`master` after every merge**, not just in each PR's own pre-merge CI — two PRs green in isolation
can still collide. Tracked as the residual follow-up; this pass restores green by renumbering.

_Dr. Mārcis Gasūns_
