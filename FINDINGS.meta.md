# FINDINGS.meta.md — metadoc for `FINDINGS.md`

_Created: 18-07-2026 · Last updated: 20-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

Note: `FINDINGS.md` is on the org's `EXEMPT_EXACT` list for the authorship-time genre-coverage
hook (it is a named hub registry, not a genre-named doc the hook flags) — this metadoc exists
because the org CLAUDE.md's "substantially edit an important doc → keep its `<name>.meta.md`"
convention applies independently of that hook, and this handoff (H968) was explicitly scoped
to cover it.

## Subject
- **Document:** [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
- **Purpose:** The cross-repo, evidence-backed empirical registry for Sanskrit-lexicon **data**
  facts — dictionary structure, encoding, corpus, morphology, per-dict tooling gotchas —
  expensive to re-discover, easy to get wrong by assumption. Currently 2,269 lines, ~448
  findings.
- **Audience:** Every session working on Sanskrit-lexicon data in any repo — the org CLAUDE.md
  routes "rely on a premise / hit a contradiction" work here (Sanskrit-data side) as opposed
  to [Uprava/FINDINGS.md](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (infra/
  process side).
- **Format / contract:** Append-only `§N` numbering — a new finding always takes the next free
  number (currently §448) regardless of section; refuted/superseded findings are struck with
  a reason, never renumbered or reused. Schema per finding: `###` heading, bold claim,
  `Evidence:`, `Implication:`, blockquoted `Source` with `— repo · date`. Colour-dot importance
  label (🔴/🟠/🟡) on both the claim line and its Index entry. An Index section at the top
  lists every finding as a clickable anchor, grouped by topic area.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`) — this metadoc. The
  subject document itself dates to 26-06-2026 per its own header.
- **Next hardening:** none scheduled — this is the org's highest-churn Sanskrit-data hub,
  appended to continuously by design ("living document — appended on a regular basis").

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Keep the Index section's anchor list in sync with the §N headings as new findings are appended | A drifted Index (missing entries, wrong importance dots) defeats the "stable citation" contract the doc promises | parked — process discipline enforced per-append, not a one-off task |
| 2 | Periodic staleness sweep — some findings reference counts/measurements that may drift as source data (csl-orig, DCS vintages) changes upstream | The doc itself warns findings are "expensive to re-discover and easy to get wrong by assumption" but does not carry an automated staleness check the way the live dashboard does for §12/§13/§21/§25/§41 | parked — the [findings_dashboard/](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard) monthly refresh already covers the time-series subset; a fuller sweep is unscoped |
| 3 | Resolve any accumulating cross-references to renumbered findings (e.g. §72/§73 noted elsewhere as "renumbered from §63/§64 on 11-07-2026") | Renumbering-on-supersession is explicitly disallowed by the doc's own rule ("never reuse its number") — any observed renumbering note elsewhere in the org is worth auditing against this file's actual current numbering | parked — needs a dedicated cross-repo grep pass, not scoped to this metadoc backfill |

## Known limitations / caveats
- This is a **2,269-line, ~448-entry, continuously-appended** file — this metadoc's author
  read only the header and the Index's first ~100 lines (grammar/morphology, corpus, dict-
  structure, etymology, encoding sections); it does not audit every individual finding's
  current accuracy.
- Distinct scope from three sibling docs the subject itself calls out: `PILOT_LESSONS.md`
  (CI/CD process, github-spine), `SHARED_CODE.md` (who-owns-what code, github-spine), and
  `Uprava/FINDINGS.md` (non-Sanskrit infra/process gotchas) — a finding filed in the wrong one
  of these four is a recurring miscategorization risk the doc's own header exists to prevent.
- The live dashboard (linked at the top of the subject) covers only a subset of findings
  (importance/section breakdown, staleness flags for §12/§13/§21/§25/§41) — most individual
  findings have no automated freshness signal.

## Intended use / known misuse
- **For:** checking whether a non-obvious Sanskrit-data gotcha (encoding collision, markup
  quirk, corpus limitation) has already been measured before re-deriving it; citing a stable
  `§N` anchor in a paper or another doc.
- **Misuse:** filing a non-Sanskrit infra/process finding here instead of `Uprava/FINDINGS.md`;
  reusing or renumbering a struck finding's `§N` instead of appending a new number; citing a
  finding's numeric claim without checking whether it has since been struck/superseded.

## Maintenance & sunset plan
- Owner: every session that measures a non-obvious Sanskrit-data fact — distributed by
  convention, not a single maintainer. The doc's own header states the append reflex is
  mandatory ("if you discovered it by running something, it belongs here").
- Sunset: none planned — this is a permanent, append-only living registry; individual findings
  are struck (never deleted) on supersession, but the file itself has no end state.

## Deprecation status
`active` — continuously appended hub, currently at §448.

## Related documents
- [Uprava/FINDINGS.md](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) — the infra/process-side sibling registry; do not cross-file.
- [github-spine/PILOT_LESSONS.md](https://github.com/gasyoun/github-spine/blob/main/PILOT_LESSONS.md) — CI/CD process lessons, explicitly out of this doc's scope.
- [github-spine/SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) — code-ownership registry, explicitly out of this doc's scope.
- [findings_dashboard/](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard) — the live dashboard generator, refreshed monthly.
- [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) — the sibling "what exists" inventory (this doc = what we've learned about it).

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |
| 20-07-2026 | **Citation-identity ruling + integrity gate (H1361).** §-number ruled a permanent citation key (append-only, one claim per number, later claim moves with a tombstone, Index = classification of record); renumbered 4 FINDINGS collisions (§80/§86/§87/§103 → §448–451) + 2 DEAD_ENDS (§8 → §9/§10); backfilled 26 Index entries; fixed the §448→§452 marker; fixed both dashboard parsers (importance from the Index dot, 95→109 findings). New [`tools/epistemic_integrity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/epistemic_integrity_check.py) gate in CI + pre-commit. Ruling: [`epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) | Opus 4.8 (`claude-opus-4-8`), H1361 |

_Dr. Mārcis Gasūns_
