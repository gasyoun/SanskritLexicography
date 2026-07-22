# Link-check baseline 2026H2 — what the weekly job's output is judged against

_Created: 22-07-2026 · Last updated: 22-07-2026_

Produced by [H741](https://github.com/gasyoun/Uprava/blob/main/handoffs/H741-Fable_SanskritLexicography_repo-wide-dead-link-sweep_11.07.26.md)
(repo-wide dead-link sweep, Fable 5 `claude-fable-5`). The weekly
[link-check workflow](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/link-check.yml)
is advisory (`continue-on-error`); this note states the accepted baseline so its
output is compared against a known state instead of re-triaged from scratch.

## Headline numbers (measured 21/22-07-2026, markdown-link-check 3.14.2)

| Run | Scope | Unique dead links | Files |
|---|---|---|---|
| Before (old config, all files) | 559 `.md` files | **16,861** | 289 |
| — of which `literature/md/` | 34 converted ebooks | 15,919 | 34 |
| — of which real project surface | 255 files | 942 | 255 |
| After (new config + exclusions + fix [PR #666](https://github.com/gasyoun/SanskritLexicography/pull/666)) | 480 `.md` files | **73** | 21 |

Goal `<100` met. The audit-era figure of "1,659 dead links" (H733, 11-07-2026)
under-counted because the CI action was rate-limited and its log truncated; the
full local run is the honest denominator.

## What was fixed vs. configured away

- **[PR #666](https://github.com/gasyoun/SanskritLexicography/pull/666)** fixed 62
  real links: archive-move repoints (now full blob URLs), gitignored-target delinks,
  pinned-SHA repoints for files deleted by
  [PR #540](https://github.com/gasyoun/SanskritLexicography/pull/540), wrong-owner
  GitHub URLs (csl-atlas/csl-observatory/csl-standards/sanskrit-util →
  `sanskrit-lexicon`; SanskritSpellCheck/kosha/WhitneyRoots → `gasyoun`), and
  genuine external 404s (Wikipedia, TMX 1.4b via Wayback, Speijer/Apte
  archive.org identifiers).
- **This PR** configures away the classes that are dead only to an unauthenticated
  bot, and excludes two path classes from the sweep (below).

## Path exclusions (workflow-level `find … -not -path`)

| Path | Dead links | Why excluded |
|---|---|---|
| `literature/md/**` | 15,919 | Third-party converted book texts (ebook-internal `#…xhtml` anchors, never-extracted images, decades-old bibliography URLs). Not project-maintained link surface; the folder's fate is [H734](https://github.com/gasyoun/Uprava/blob/main/handoffs/H734-Fable_SanskritLexicography_literature-copyright-triage_11.07.26.md)'s open Western-cluster ruling. |
| `docs_site/wiki/**` | ~30 | Verbatim copies synced by [docs_site/build_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/build_site.py) `--sync`; relative links are rewritten at build time, so checking the copies is pure noise. Originals under `RussianTranslation/research/` stay checked. |

## Config ignore-list rationale ([.github/mlc_config.json](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/mlc_config.json))

| Pattern class | Evidence | Why alive despite the status |
|---|---|---|
| Private repos: `gasyoun/{Uprava, claude-config, codex-config, github-spine, claude-memory-store, telegram-sanskrit-corpus, spoken-sanskrit-corpus, indology-archive-research-map, prefaces_ieg, ChatExport, RuWritingStyles-corpus}` | 510 unique 404s | GitHub returns 404 to unauthenticated requests for private repos. The org's clickable-links rule *mandates* these full blob URLs; they resolve for every org member. Largest single class. |
| `mailto:` | 11 | Not HTTP-checkable. |
| `doi.org`, `dx.doi.org` | 132+ 403/0 | DOIs are persistent identifiers; the resolver bot-blocks HEAD/GET from CI. |
| Paywalled/bot-blocking publishers: jstor, sciencedirect, academia.edu, brill, oed, oup, acm, degruyter, semanticscholar, loebclassics, webonary, rapidwords, id.loc.gov, claude.ai, github.com/signup | 403/405/202 in bulk; alive in a browser | Standard bot-block behaviour (403, 405 on HEAD, interstitials). Verified alive via serial re-probe with browser UA where possible. |
| Project-adjacent academic hosts: `sanskrit-lexicon.uni-koeln.de`, `vedaweb.uni-koeln.de`, `sanskrit-linguistics.org` (DCS), `hss.iitb.ac.in` (WSC 2027), `mahabharata.manipal.edu`, `sanskrit.uohyd.ac.in` (Saṁsādhanī) | 403/418/500/0/TLS-altname | Cologne's own server 403s bots; VedaWeb answers 418/500 to checkers; DCS's cert doesn't cover the `www.` alias; the rest time out from CI while being reachable interactively. Cross-reference [Uprava SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md) before re-probing. |
| `aliveStatusCodes` gains `202` | doi.org, degruyter, oup, semanticscholar | 202 Accepted is a 2xx success response some publishers return to non-browser agents. |

## Accepted survivors (73 unique, 21 files, measured 22-07-2026)

| Class | Count | Notes |
|---|---|---|
| H706-owned epistemic registries ([FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md), [CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md), [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md), [DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)) | 40 | Excluded from H741 edits per the handoff (owned by [H706](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H706-Fable_Uprava_findings-hubs-crosslink-audit_11.07.26.md)). 22 are FINDINGS' own long in-file anchors that mlc's slugifier mismatches (they work on GitHub); the rest are stale branch pointers (`chore/errata-kochergina-waiting` → now [`tree/main/GasunsDhatu_2014/revision-2026`](https://github.com/gasyoun/SanskritGrammar/tree/main/GasunsDhatu_2014/revision-2026)), one `gasyoun/csl-atlas` → `sanskrit-lexicon/csl-atlas` owner fix, one `gasyoun/csl-observatory` → `sanskrit-lexicon/csl-observatory`, and SamudraManthanam `codex/audit-hardening` branch links — all queued as a registry-hygiene follow-up, not silently rewritten here. |
| Transient `Status: 0` socket flakes | ~28 | github.com / aclanthology.org / arxiv.org / sil.org links the serial re-probe confirmed alive; they wobble per-run under load. Expect a fluctuating handful in any weekly run — treat as noise unless a link repeats across weeks. |
| Genuinely down externals | 5 | `koshashri-dc.ac.in` (×2, Deccan College PD portal — down at measurement), `darkone23/Heritage_Resources` + two others intermittent. Re-check before repointing; log persistent ones in [SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md). |

A weekly run reporting **≲75 dead links in these same classes is at baseline** —
no action needed. New dead links outside these classes are real regressions.

## @DECIDE (vetoable at PR review)

The `<100` threshold and every host added to the permanent ignore list above are
proposed by this note; MG can veto any row at PR review of the config PR, and any
later addition to the ignore list should update this table in the same commit.

_Dr. Mārcis Gasūns_
