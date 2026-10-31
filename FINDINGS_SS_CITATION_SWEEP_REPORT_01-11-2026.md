# FINDINGS §N citation-identity sweep — stale-pointer report (H7595)

_Created: 01-11-2026 · Last updated: 01-11-2026_

_Executor: GLM-5.3-Flash (ZCode) · handoff minted for DeepSeek — tier provenance retained, H3688 warn-and-proceed._

**Verdict.** 6,042 in-scope `FINDINGS §N` citations across 4 repos validate 93.8 % clean; 321 resolve
validly in the sibling space; hand-verification of the 56 raw STALE flags yields **13 genuine stale
citations** (4 distinct numbers), **4 PENDING** (§689 announced-not-filled), **39 parser-gap false
positives** (sections exist in row formats the parser missed), and **187 broken in-file anchors** in
SanskritLexicography/FINDINGS.md's own index. The §103→§451 renumber class that motivated this sweep
is contained: zero live citations point at renumbered-away numbers; the residual risk is the
date-dependent §451 shadow (rule documented below). Read-only sweep per mission — no citation target
was edited; fixes are the follow-up list in §8.

## 1. Mission and method

Cross-repo sweep of FINDINGS §N citations: grep §<digits> across SanskritLexicography (code/docs/comments),
Uprava (handoffs included), kosha, csl-atlas; validate each target against the owning space's section
rows; emit stale-pointer report with proposed re-points. Read-only; fixes follow-up. Tool: one-off
sweep script (as-run copy committed alongside as
[FINDINGS_SS_CITATION_SWEEP_SCRIPT_01-11-2026.py](FINDINGS_SS_CITATION_SWEEP_SCRIPT_01-11-2026.py) — see §9), patterns inline below.

**Rev basis at sweep time (2026-10-31 ~23:05–23:35Z):** SL `origin/master` 80450ca1; Uprava
`origin/main` as fetched 23:0xZ (re-verified post-fetch 9335328fac2 — fleet pushes advanced main
between runs; drift re-validated the §659/§1573/§823 class only, census numbers are rev-anchored to
the sweep run); kosha d5cd6728d; csl-atlas 254f216.

**In-scope citations** (2,266 candidate lines → 6,042 cites):
- explicit `FINDINGS §N` pattern, case-insensitive, `\s+` between the words (catches NBSP-space cites — a real subset);
- SL FINDINGS.md's own index anchors `(#N-...)`;
- bare §N inside SL repo files was EXCLUDED — SL prose cites Whitney's Grammar §N bare all over
  (§§315–319, §407b, §1116, §1253.2d...) — the Whitney §N-space shadows any bare-§N validation;
- other prefixed spaces (plan §N, ARCHITECTURE §N, addendum §N, design/spec §N, GAPS/CONTRADICTIONS §N) excluded.

## 2. The §N-space topology is multi-space, not single-space

The mission modeled one FINDINGS §N-space (SL) cited estate-wide. Reality: **two big FINDINGS §N-spaces** —
SL FINDINGS.md (306 rows, §1–§652) and Uprava FINDINGS.md (896+ rows, §1–§1663) — plus textbook spaces
(Whitney, Macdonell) and per-doc spaces (plan/addendum/design/spec §N). FORIGN-VALID 321 = cites whose
number is valid in the sibling space (e.g. "Uprava FINDINGS §218" cited inside SL files, or "SL FINDINGS §218" cited inside Uprava files — both targets exist).

## 3. Section-row format census (Uprava FINDINGS.md)

Uprava FINDINGS.md's §N rows use at least six formats — the format diversity is itself the
load-bearing finding: a mechanical validator needs N formats of section-row detection to validate
against it:

1. `## §N — Title` heading rows (~450);
2. `## §N - Title` (ASCII dash) and `## §N` (bare) heading rows;
3. status-emoji bold rows `🔴/🟠/🟡/🟢/⚪/🔵/🧿 **§N. ...` (~450);
4. `✅ **§N. RESOLVED...` resolved-rows (e.g. §659);
5. bare-line rows `§N Title` (e formats like §1573);
6. announced-not-filled rows: "§689 takes the next number" (PENDING — announced number without body).

## 4. Citation census by repo (bullet census; tables avoided per authoring-channel limits)
- SL repo — 1,144 in-scope: OK 1,038; FOREIGN-VALID 104; raw STALE 2 → both = vendored Uprava-guard copies (scripts/pre_push_stale_base_check.py §659 cites, valid in Uprava space) → genuine 0.
- Uprava repo — 4,758 in-scope: OK 4,523; FOREIGN-VALID 185; raw STALE 50 → hand-verified: 33 EXISTS (parser-gap incl. the 6 vendored-guard §659 rows counted under siblings), 4 PENDING (§689), genuine 13.
- kosha — 101 in-scope: OK 80; FOREIGN-VALID 19; raw STALE 2 → both vendored-guard §659 cites → genuine 0.
- csl-atlas — 39 in-scope: OK 24; FOREIGN-VALID 13; raw STALE 2 → both vendored-guard §659 cites → genuine 0.
- Totals: 6,042 in-scope · OK 5,665 (93.8%) · FOREIGN-VALID 321 · raw STALE 56 = 39 EXISTS + 4 PENDING + 13 genuine.

## 5. Genuine stale citations (13) — all in Uprava repo
- §176 ×5 — never existed in either space; intended target unresolvable mechanically:
  - tools/handoff_auto_resume.py:208 (live code comment "H2970 / FINDINGS §176")
  - CHANGELOG.md:5609 + CHANGELOG_ARCHIVE.md:621 + handoffs/archive/H2819-...md:26 + H2970-...md:27 (historical)
  - tools_generic_domain_census.json:8972 (data-key)
- §7363 ×6 — never existed; LOW-confidence re-point §736 (tgrep-context mismatch):
  - reports/H6310_TGREP_GUARD_ACCEPTANCE_2026-10-11.md:7; reports/MATURITY_TGREP_2026-10-09.md:79/:89
  - tools/test_tgrep_guard.py:4; tools/tgrep_stale_check.py:38/:333 (live code)
- §6297 ×1 — never existed; LOW-confidence re-point §629 (orphan-census/backlog semantics plausible):
  - reports/CENSUS_LIVENESS_REGISTRY_06-09-2026.md:22
- §886 ×1 — never existed; historical: handoffs/REGISTRY_ARCHIVE.md

## 6. Broken in-file anchors (187) — SL FINDINGS.md index and body links
- Rule: `(#N-fragment)` in FINDINGS.md must equal slug of the current `### §N. Title` heading
  (GitHub slugger: lowercase; drop non-word chars except hyphen; spaces→hyphens; § and "." dropped, "N" kept).
- 187 anchor fragments fail the equality; clicks land on FINDINGS.md top (broken on GitHub).
- Hand-verified samples: §494 (row anchor has "single-lemmaid", heading slug has "single-lemma_id"),
  §495 (row anchor single hyphen, heading slug "pure-cyrillic--rules" double hyphen after em-dash).
- Cause class: hand-typed or stale anchors surviving retitles; same class as the §103 index row struck 01-11 (PR #2481).
- Fix spec (follow-up, mechanical): for each flagged anchor recompute slug(§N + ". " + title) and replace;
  187 replacements over ~160 rows; also apply to FOREIGN repo files linking SL anchors (163 in Uprava files, 20 in csl-atlas).

## 7. Renumber maps and the §451 date-rule
- SL renum: §80→§448, §86→§449, §87→§450, §102→§456 (H1361/H1328, 20-07-2026);
  H1362 same-day divend: §448–451→§452–455 (H1350 originals), H1361 movers keep their numbers.
- §451 date-rule: a cite written before 20-07-2026 means the old §451 (now §455); post-20-07 cites = current §451 (false-DOI finding).
- Shadow band {§80/86/87/102/103/448–451}: today's numbers all exist; pre-20-07 cites may mean moved content — per-line git-blame = follow-up, not in-sweep.
- Uprava renum: §351→§352. ZERO live in-scope cites of renumbered-away numbers in either space — the motivating §103→§451 class is contained.

## 8. Follow-ups (explicitly NOT in-sweep — mission says read-only sweep + report)
1. Anchor-fix pass: 187 SL FINDINGS.md in-file anchors + 183 foreign links to SL anchors
   (163 Uprava + 20 csl-atlas files) — mechanical slug recompute + replace, low-risk, high UX value.
2. §N-format standardization: Uprava FINDINGS.md rows use ≥6 formats (## §N —; ## §N -; ## §N bare;
   emoji-bold **§N.**; ✅/🧿-bold; bare-line §N; announced "takes the next number") —
   normalize or accept documented N-format validation cost.
3. Re-point adjudication for §176/§7363/§6297/§886 (13 cites): human/MG verdict on intended targets;
   §7363→§736 and §6297→§629 are LOW-confidence candidates, semantics-mismatched; §176 no candidate.
4. §689 PENDING: fill the announced section or strike the announcement row.
5. Per-line git-blame of the §451 shadow band (cites written pre-20-07 of §448–451/§103).
6. Findings-append row: the multi-space topology + format-diversity finding deserves a §653 SL row
   (next SL number); minted via findings-append route, not in this read-only sweep.
7. Data-key census: tools_generic_domain_census.json §176 data-key + vendored-guard §659 cite-sync
   (6 rows, 4 repos) — decide whether vendored copies re-point on sync.

## 9. Evidence and inspect-first pointers
- Sweep script as-run: [FINDINGS_SS_CITATION_SWEEP_SCRIPT_01-11-2026.py](FINDINGS_SS_CITATION_SWEEP_SCRIPT_01-11-2026.py) —
  also at /tmp/h7595/sweep_v2.py on this Mac; outputs JSON census.
- Repo revs at sweep time: SL 80450ca1 (origin/master), Uprava origin/main re-verified 9335328fac2,
  kosha d5cd6728d, csl-atlas 254f216 (2026-10-31 23:05–23:42Z).
- Verify anchors claim: on GitHub, click any flagged index anchor in
  [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — most flagged rows land on file top.
- Verify §7363 claim: `git grep -niE 'findings §7363' origin/main -- tools/ reports/` in Uprava (NBSP-space caveat: use `git grep -nP 'FINDINGS\xa0§7363'` for the NBSP subset).
- Verify PENDING §689: grep Uprava FINDINGS.md line ~6546 "§689 takes the next number".
- Verify parser-gap class: Uprava FINDINGS.md §659 row is `✅ **§659.` format — not matched by 2-regex parsers.
- Full per-row data (56 raw flags, 187 anchors): /tmp/h7595/v2_full.json — stale_rows + toc_bad arrays.
- Machine verdicts: 6,042 in-scope cites = 5,665 OK + 321 FOREIGN-VALID + 56 raw STALE (hand-verified split 39/4/13).
_Machine census + hand-verification by GLM-5.3-Flash (ZCode), 2026-10-31 23:0x–23:5xZ; handoff H7595 (minted for DeepSeek, executed by GLM per H3688 warn-and-proceed)._
