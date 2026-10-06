_Created: 06-10-2026 · Last updated: 06-10-2026_

# Repo primer — full detail for the sections trimmed from CLAUDE.md

> On-demand companion extracted from [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) (H5964 budget trim, 06-10-2026). One-line forms and every DANGER/gate line stay in CLAUDE.md; this file carries the full inventory detail. Nothing here overrides a gate.

## CI and pre-commit inventory

CI ([`.github/workflows/ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)) runs:

- Markdown/YAML/Python/JS lint and link-check;
- the RussianTranslation gates (also the `master` required check that makes releases PR-only);
- docs-site pytest ([`docs_site/test_docs_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs_site/test_docs_site.py));
- the **offline contract-pins** job (H4353) running
  [`tests/run_offline_suite.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tests/run_offline_suite.py) — **201 pins** over the 62 in-scope modules outside `RussianTranslation`, network off, fixtures under `tests/fixtures` only, literal record-count floors per headword list (evidence:
  [`tests/OFFLINE_CONTRACT_PINS_08-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/tests/OFFLINE_CONTRACT_PINS_08-09-2026.md)). The pin count is verified, never retyped (H5426): `python tests/run_offline_suite.py --collect-only -q` prints the per-test-file breakdown (it summed to 201 on 24-09-2026: 6+4+18+15+30+110+11+7).

Pre-commit hooks ([`.pre-commit-config.yaml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.pre-commit-config.yaml)): `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `check-merge-conflict`, plus local `russian-translation-review-changelog`.

## Dashboard inventory

Three dashboard generators:
[`epistemic_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/epistemic_dashboard),
[`findings_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard),
[`progress_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/progress_dashboard).
Public kitchen at [/progress/](https://gasyoun.github.io/SanskritLexicography/progress/); local ops twin `dashboard_server.py` → `127.0.0.1:8765`.

## HeadwordLists/ — full filename grammar

Filenames encode source/key/count:

- `{DICT}-unique-{key1|key2}-{N}.txt` — `N` = entry/line count;
- `{DICT}-fehlerhaft-{N}.txt` — German "erroneous": flagged entries with **full XML records, not bare headwords**, e.g.
  [`PWG-fehlerhaft-1661.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/PWG-fehlerhaft-1661.txt);
- `SCH-accents-IAST-{N}.txt` — accented IAST;
- cross-dictionary joins like
  [`mw-apte-mcdonell-hk.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/mw-apte-mcdonell-hk.txt) (Harvard-Kyoto, sorted).

**key1 vs key2 (full form):** key1 = normalized computational key, may not match any printed form (used for matching/dedup/joins); key2 = closer to the printed source (retains `-`, `--`, `/` accents, e.g. `a/MSa`, `a--kAra`; used for editorial review, checking the digitized text against the scan).

Files too large for an editor: `sanhw1.xlsx`, `DCS_statistical_evaluation.htm` (~75 MB), `DCS-Moniers-roots-w-references.html` (~16 MB), PWG/PWK error lists — use streaming/CLI tools, not Read.

## mw_ru — stage detail

Per-stage prompts live in [`mw_ru_prompts/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/mw_ru_prompts), one per stage: translate → two independent QA judges → re-translate rejects. 287,358 cards, multi-pass, multi-model; production documented in [`mw_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md).

## Cyrillic proper nouns — intake method detail

Two sanctioned intakes (both refresh their JSON reports same PR):

- witness-first: [`h3985_cyr_slp1_table.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h3985_cyr_slp1_table.py) — keys transcoded from IAST present in the seed line; zero keys derived from Russian character rules;
- onomasticon-first backfill: [`h4750_cyr_slp1_backfill.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4750_cyr_slp1_backfill.py) — key COPIED verbatim from an inm/pui `<k1>`; the IAST→Cyrillic rendering is used **only** as an exact-match join to the attested spelling, never as key derivation (534 → 622 rows; `rule_derived_keys: 0`).

Never hand-add a row without an IAST witness or an onomasticon `<k1>`; render-collapsed ambiguous spellings ship disclosed, never resolved ([GAPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) §6).

## Release-tag history

`cut_release.py --apply --tag --push` on a branch tags a commit the squash-merge orphans, or the tag is never pushed (measured 09-09-2026: 22 untagged headings). Full working flow and backfill rules: [docs/agents/release-tag-flow.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/agents/release-tag-flow.md).

_Dr. Mārcis Gasūns_
