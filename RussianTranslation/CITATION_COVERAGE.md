# PWG citation coverage — reports live in the PWG repo

_Created: 02-07-2026 · Last updated: 02-07-2026_

The `<ls>` literary-source **coverage reports** for the PWG article subset are
**generated from this workspace's data** but **published in the PWG repo**, next
to the rest of the literary-source work (`pwg_ls`):

- [pwg_ls/pwg_ru_coverage/](https://github.com/sanskrit-lexicon/PWG/tree/main/pwg_ls/pwg_ru_coverage) — the reports:
  - [CITATION_SOURCES.md](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/CITATION_SOURCES.md) — abbreviation → scan/HTML target + coverage.
  - [UNCOVERED_SOURCES.md](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/UNCOVERED_SOURCES.md) — most-cited works with no Cologne target.
  - [COVERAGE_COMPARISON.md](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/COVERAGE_COMPARISON.md) — covered vs uncovered + frontier + provenance.

**The generator and its data stay here** (this is the translation pipeline):

- generator: [`src/build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py)
- resolver: [`src/ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
- data: `src/pwg_ru_translated.jsonl` + `wf_output.en.*.json` (git-ignored, regenerable)

With PWG checked out as a sibling repo, the generator writes the reports into
`PWG/pwg_ls/pwg_ru_coverage/` by default (override with `--out-dir`):

```sh
python src/build_citation_index.py
```

_Dr. Mārcis Gasūns_
