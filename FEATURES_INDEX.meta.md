# FEATURES_INDEX.meta.md — metadoc for `FEATURES_INDEX.md`

_Created: 18-07-2026 · Last updated: 18-07-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md).
It does not duplicate the subject's content; it records everything *around* it. Kept per the
standing "one metadoc per important document" convention (`~/.claude/CLAUDE.md`).

## Subject
- **Document:** [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md)
- **Purpose:** The clickable, capability-first inventory of every working asset across the
  ~85-repo Sanskrit Lexicon org — 44 dictionaries, 21 interfaces, 43 data assets, 14 tools,
  4 external stacks, 11 learner drill sets. Answers "what exists at all?" as distinct from
  `REUSE_INDEX.md`'s "don't rebuild — consume this."
- **Audience:** Every fresh session in any repo of the org that needs to check prior art
  before building — this is the org-root CLAUDE.md's linked answer to "see what already
  EXISTS." Also the canonical source for the generated `features_index.html` interactive
  artifact.
- **Format / contract:** Stable IDs per category (`A`–`F` data · `G`–`K` interfaces · `L`–`M`
  tools · `P` drills; dictionaries use their code), running numbers that never restart or
  shift, size-tier markers (🟢/🟡/⚪), an "Intro" first-introduced month/year column. This
  Markdown file is the canonical source — `build_features_index_html.py` generates
  `features_index.html` from it; never hand-edit the HTML.

## Provenance
- **Created:** 18-07-2026 (handoff H968, Sonnet 5 `claude-sonnet-5`) — this metadoc. The
  subject document itself dates to 04-07-2026 per its own header.
- **Next hardening:** none scheduled — this is a high-churn hub, hardened continuously by
  whichever session adds an asset; no dedicated hardening pass planned.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Keep the Markdown/HTML pair in sync on every edit | The doc's own contract states the HTML is generated and must never drift — a session editing the table without re-running `build_features_index_html.py` silently breaks the interactive artifact | parked — process discipline, not a one-off task; enforce on every edit |
| 2 | Re-verify sizes/counts against source repos periodically | The doc's own caveat: "Sizes and counts are approximate; re-verify against a source repo before a large change" | parked — no scheduled cadence; do opportunistically |
| 3 | Extend coverage as new asset families land (e.g. the ACC×NCC works-catalogue crosswalk once [ROADMAP_ACC_NCC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ACC_NCC.md) P3 ships) | New durable data/interface/tool assets should register here per the org's "post-work hub sync" reflex | parked — triggered by the producing session, not this metadoc |

## Known limitations / caveats
- This is a **high-churn, actively-referenced** doc (last updated 14-07-2026 per its header,
  ten days after creation) — any read of it should be treated as a snapshot, not a frozen
  reference; check "Last updated" before citing a count in a paper.
- Two linked companion hubs ([`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md),
  [`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md))
  live in **private** repos (`github-spine`, `Uprava`) — a reader without access to those
  repos sees dead links for the "who owns this code" / "who feeds whom" cross-references.
- The ID scheme is running-number-within-category, not stable-across-categories — e.g. `E43`
  appears twice in the table read during this metadoc's authoring (kosha corpus sandhi
  programme and the code-duplication census both carry `E43`), which looks like a duplicate-ID
  defect worth a closer look by whoever next edits this table.

## Intended use / known misuse
- **For:** the first stop before building a parser/transcoder/dataset in ANY repo of the org
  — the org CLAUDE.md's "check prior art before building" rule routes here specifically for
  "what already EXISTS."
- **Misuse:** treating a listed asset's size/count as exact without re-verifying against its
  source repo (explicitly flagged approximate); hand-editing `features_index.html` instead of
  editing this Markdown file and regenerating.

## Maintenance & sunset plan
- Owner: whoever adds a new durable asset anywhere in the org (distributed ownership by
  convention, not a single maintainer) — the org's "post-work hub sync" reflex names this file
  as one of the hubs to update after any deliverable.
- Sunset: none planned — this is a permanent living inventory; it only shrinks if an asset is
  deprecated, in which case the row is struck/annotated, not deleted (mirroring FINDINGS.md's
  append-only discipline for its own numbering, though this file's IDs are per-category not
  fully append-only).

## Deprecation status
`active` — continuously maintained hub.

## Related documents
- [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — the sibling empirical-findings registry (this doc = what exists; FINDINGS = what we've learned about it).
- [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) — cites this doc's L1 dictionary count directly.
- [features_index.html](https://github.com/gasyoun/SanskritLexicography/blob/master/features_index.html) — the generated interactive artifact.
- [build_features_index_html.py](https://github.com/gasyoun/SanskritLexicography/blob/master/build_features_index_html.py) — the generator; never hand-edit the HTML output.
- [Uprava/REUSE_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md) — companion "don't rebuild — consume this" doc.

## Revision history

| Date | Event | Who |
|---|---|---|
| 18-07-2026 | Metadoc created (backfill sweep) | Sonnet 5 (`claude-sonnet-5`), H968 |

_Dr. Mārcis Gasūns_
