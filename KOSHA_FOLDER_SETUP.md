# kosha — Status After Triage (was: "Folder Setup Complete")

_Created: 02-07-2026 · Last updated: 02-07-2026_

> **⚠️ This document replaces an earlier version that was factually false.**
> The original (generated 02-07-2026) claimed a "complete, production-ready
> directory structure" with five pipeline scripts marked "✅ Ready". A same-day
> audit against the filesystem found that **none of those scripts existed** —
> `kosha/scripts/`, `tests/`, `templates/`, `static/css|js/`, `app/routers/`,
> `app/services/` were all empty directories. The only real code was a 67-line
> FastAPI stub. This rewrite records what actually exists, what was decided,
> and what was deleted.

---

## What actually exists (ground truth, 02-07-2026)

| Artifact | State |
|---|---|
| 8 strategy documents `KOSHA_*.md` (repo root) | Real, but see the per-doc triage banners — timelines, latency targets, cadence, and several data claims are mutually contradictory or fabricated |
| [KOSHA_DEPLOYMENT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_DEPLOYMENT.md) | Salvaged from the deleted `kosha/DEPLOYMENT.md` with its four config defects fixed |
| `kosha/` application scaffold | **Deleted 02-07-2026** — it was empty directories plus a stub; code will start life in a dedicated repo (recoverable from git history at commit `707039d` if ever needed) |

The audit report's key fabrications, so nobody codes from them again:

- **`<pc>` semantics were invented.** MW `<pc>` is `page,column` in a
  **single-volume** work (real record: `<L>142512<pc>720,1<k1>banD`); the docs'
  recurring "MW vol. 5, p. 32" example is physically impossible. PWG uses
  `vol-page` with a **hyphen** (`1-0001`, 7 volumes not 6); AP90 uses
  `page-column-letter` (`0001-a`). Any `split(',')` parser fails on 2 of 3 dicts.
- **Invented endpoints/domains:** `sanskrit.inria.fr/api/morphoanalysis` (real:
  `…/cgi-bin/SKT/sktlex.cgi`, already integrated in SamudraManthanam), and
  `cologne.archive.org` (does not exist; scans come from
  `sanskrit-lexicon.uni-koeln.de` via csl-websanlexicon `serveimg`/`servepdf`).
- **"slp1_key": "bandh"** — that is IAST; SLP1 is `banD`. The encoding examples
  conflate the two throughout.
- **Budget arithmetic:** "~$3k–5k for 35 contractor days at $100–150/hr" is off
  by ~6× (≥$28k at the stated rate).

## Decisions

### Locked 02-07-2026 (triage meta-decisions, M.G.)

| # | Decision |
|---|---|
| M1 | **Docs corrected to truth**; empty scaffold deleted until code is real |
| M2 | **Application code lives in a new dedicated repo** (e.g. `gasyoun/kosha`), not in SanskritLexicography — this repo's charter forbids source code |
| M3 | **Reuse-first, new glue only**: build on csl-apidev (C-SALT **Kosh** API already integrated there), csl-websanlexicon endpoints, [ls_resolver.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py), `sanskrit-util` transcoding, [RussianTranslation/glossary/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/glossary) form→lemma (86.6 % token coverage), `corpus_lexicon.jsonl`, and the **already-built** [HeadwordLists/union/union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) (323,426 rows). No re-extraction, no transcoder #63, no rebuilt union index |
| M4 | **kosha gets its own repo/Pages.** This repo's GitHub Pages already serves the PWG article site from `gh-pages` and stays untouched |

### Earlier product decisions (from the original table — kept where coherent)

| Aspect | Decision | Status |
|---|---|---|
| Data | All Cologne dicts + Russian dicts + KEWA + morphology + corpus | Kept as ambition; MVP scope = MW + PWG + AP90 |
| Audience | Translators > Learners > Scholars | Kept (note: the "decisions archive" never offered "Translators" as an option — recorded here as the canonical answer) |
| Scans | Cologne server; external links first → self-hosted later | Kept; resolved by `ls_resolver.py` + csl-websanlexicon, no need to "contact Cologne for URL patterns" |
| Scholarly | Persistent IDs + provenance tracking (DOI-ready) | Kept |
| Performance | ~~"sub-50ms"~~ | **Open.** The docs carried four incompatible targets (sub-50 ms, p50 ≤30 ms/p95 ≤100 ms, ≤200 ms miss, ≤50 ms for 80 %). Pick one measurable SLO when architecture is real |
| Update cadence | ~~"Monthly batch rebuild (nightly cron)"~~ | **Open.** Self-contradictory as written, and "monthly" was never among the offered options (quarterly/nightly/real-time). Leaning nightly; decide at build time |
| Deployment | ~~GitHub Pages (this repo) + samskrtam.ru hybrid~~ | Superseded by M4: own repo/Pages + samskrtam.ru |

[KOSHA_DECISIONS_NEEDED.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_DECISIONS_NEEDED.md)
now carries the filled summary table (its six blanks were never actually
answered before being declared "archived").

## What was deleted and why

`kosha/` contained: empty skeleton directories; a stub `main.py` (recreatable
in minutes, and carrying its own defects — bare `except:`, wildcard CORS with
credentials); stale 2023 dependency pins; and four Markdown docs of which
QUICKSTART and SETUP_GUIDE were near-verbatim duplicates of root docs,
README's only unique value (API contract + `.env` keys) and DEPLOYMENT's
Parts I–IV (systemd/nginx/cron/webhook — the only genuinely novel content)
were salvaged into
[KOSHA_DEPLOYMENT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_DEPLOYMENT.md)
with their defects fixed (`Type=notify` on a non-sd_notify server, missing
nginx `proxy_pass`, wrong `WorkingDirectory`, a "force-push to fix Pages"
anti-recipe).

## Next steps

1. **Re-plan Phase 1 under M3 (reuse-first).** The original "2 weeks to
   extract + index dicts" collapses to days once the union headword index,
   glossary, and Salt/Kosh API are consumed instead of rebuilt.
2. **Create the dedicated repo** only when Phase-1 code work is actually
   approved and starting — not before.
3. **One reconciliation pass** over
   [KOSHA_IMPLEMENTATION_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_IMPLEMENTATION_PLAN.md) /
   [KOSHA_LOOKUP_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_LOOKUP_ROADMAP.md) /
   [KOSHA_TRANSLATOR_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/KOSHA_TRANSLATOR_SPEC.md)
   to a single timeline and SLO once the reuse-first scope is drawn; until
   then their week/latency/cadence figures are historical, not binding.

---

_Dr. Mārcis Gasūns_
