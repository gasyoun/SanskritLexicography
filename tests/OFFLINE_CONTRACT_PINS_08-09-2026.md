_Created: 08-09-2026 · Last updated: 08-09-2026_

# Offline contract pins — the 62 modules outside RussianTranslation (H4353)

**Executor:** Fable 5.1 (`claude-fable-5-1`) · **Handoff:** H4353 · **Runner:** [tests/run_offline_suite.py](https://github.com/gasyoun/SanskritLexicography/blob/master/tests/run_offline_suite.py) · **CI job:** `offline-contract-pins` in [.github/workflows/ci.yml](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)

## What the suite is

`tests/` pins the parse → normalise → emit contract of every Python module in `HeadwordLists/`, `data/`, `scripts/`, `tools/`, `progress_dashboard/`, `findings_dashboard/` and `epistemic_dashboard/` that had no test before. Ground rules are enforced once in [tests/conftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/tests/conftest.py), not per test:

1. **No network.** `socket.connect`, `socket.create_connection`, `urllib.request.urlopen` and `urlretrieve` are replaced at collection time with a function that raises `NetworkDisabled`.
2. **No external mirrors.** Every environment variable the modules read for an outside root (`CSL_ORIG_V02`, `PWG_INPUT_DIR`, `DCS_LEMMA_SUMMARY`, `SSC_DIR`, `KOSHA_FREQ`, `HERITAGE_MIRROR_DATA`, `DCS_FULL_SQLITE`, `CORPUS_LEXICON_JSONL`, `ACC_TXT`, `NCC_TXT`, `PD_TXT`, `PWG_DATA_ROOT`) points at `tests/_nonexistent_external_root`. Fixtures live under [tests/fixtures](https://github.com/gasyoun/SanskritLexicography/tree/master/tests/fixtures) only.
3. **No history walks.** The clone is shallow; the one git-backed test builds its own throwaway repository in `tmp_path`.
4. **Devanagari round-trips never go through `iast_to_devanagari`** (known broken): an autouse fixture in `test_headword_snapshots.py` makes that function raise, and every triple uses `slp1_to_devanagari(to_slp1(s))`.
5. **Floors are literals.** Every regenerated list has its committed record count written as a number in `NOW_2026`, `THEN_2014_EXACT`, `OTHER_FLOORS`, `GZ_FLOORS`; a shrink fails the suite.

Module-level-executing scripts (`Catalan-Pujol/*.py`, `semdom_ak_bridge.py`, `eol_census.py`, `build_works_crosswalk.py`) are loaded by `conftest.load_defs`, which keeps imports (each wrapped in `try/except ImportError`), `def`/`class` blocks and constant assignments, and drops the analysis body.

## Runner output — network off, 0 failures

```text
$ python3 tests/run_offline_suite.py
........................................................................ [ 35%]
........................................................................ [ 71%]
.........................................................                [100%]
201 passed in 4.02s
offline suite: exit 0 · elapsed 4.3s · network disabled · external roots → …/tests/_nonexistent_external_root
```

The runner also collects `HeadwordLists/works_catalogue/test_parse_ncc.py` and `docs_site/test_docs_site.py`, so one command runs every offline test the repo has.

## Module · contract · fixture

| Module | Contract pinned | Fixture / source |
|---|---|---|
| `HeadwordLists/huet_coverage.py` | `vh_to_iast` Velthuis map, `norm_huet` vectors, `norm_key` accent strip | literal vectors |
| `HeadwordLists/headword_diff.py` | `field_set`, `key2_forms` splitting, `now_set`, `sanskrit_key` varṇa-krama order, `_SLP1_ORDER` string | literal vectors |
| `HeadwordLists/headword_snapshots` (25 now-2026 lists) | sorted by `sanskrit_key`, unique, no BOM, LF, trailing newline, filename `N` == line count, key1 has no `/` | committed lists, floors as literals |
| `HeadwordLists/then-2014` (31 lists) + 42 other lists + 3 `.gz` | exact / floor record counts | committed lists |
| now-2026 key1 round-trip | SLP1 → IAST → SLP1 and SLP1 → Devanagari → SLP1 on every 53rd headword; documented exceptions (hiatus `a`+`i`/`a`+`u`; `~` → `M`; avagraha dropped); literal triples agni/अग्नि, kfzRa/kṛṣṇa/कृष्ण, aMSu/अंशु, afRin/aṛṇin/अऋणिन् | committed lists |
| `HeadwordLists/union` | columns `slp1 iast n_dicts dicts gender fem_fold`, `n_dicts == len(dicts)`, roster ⊆ `build_union.DICTS` | committed union |
| `HeadwordLists/works_catalogue/*.jsonl` | `ncc.jsonl match_key == parse_ncc.match_key_for(iast)`, `acc.jsonl match_key == slp1_simplify(k1)` | committed jsonl |
| `HeadwordLists/Catalan-Pujol/match_rate.py` | `norm_cat` (parentheticals, √, ˚, trailing digits, NFC, hyphen join) | literal vectors |
| `HeadwordLists/Catalan-Pujol/make_uncovered_lists.py` | `categorize` classes | literal vectors |
| `HeadwordLists/Catalan-Pujol/coverage_vs_dcs.py` | `classify` | literal vectors |
| `HeadwordLists/Catalan-Pujol/accent_compare.py` | `pujol_entry` keeps diacritics (see finding 1), vowel ordinals, `slp_vowel_ordinal`, `cologne_k2` on the mini MW (comma list kept unsplit), `has_acc` | `csl_orig_mini/mw/mw.txt` |
| `HeadwordLists/Catalan-Pujol/coverage_by_dict.py` | `norm_cat` | literal vectors |
| `HeadwordLists/accent_review.py` | `accented_iast`, `has_acc`, `best`, `pujol_accents` keeps diacritics | tmp Pujol list |
| `HeadwordLists/alternate_headwords.py` | `variant_pairs` | literal vectors |
| `HeadwordLists/assemble_typo_queue.py` | `err_label` | literal vectors |
| `HeadwordLists/build_union.py` | `gender_letters`, `DICTS` roster | literal vectors |
| `HeadwordLists/coverage_additions.py` | `norm_key` | literal vectors |
| `HeadwordLists/crosstag_additions.py` | `norm_cat` | literal vectors |
| `HeadwordLists/heritage_freq_diff.py` | `wx_to_slp1` (docstring vectors; unmapped chars pass through and are counted), loaders, `_avg_ranks`, `spearman` | `freq_mini.tsv` |
| `HeadwordLists/heritage_forms_oracle.py` | `nasal_norm`, `norm_set`, `prefix_related` | literal vectors |
| `HeadwordLists/heritage_stem_extract.py` | `extract` anchors from a DICO page; `SystemExit` on an empty mirror | `heritage_mirror/DICO/1.html` |
| `HeadwordLists/heritage_mw_crosswalk.py` | `build_dico_index`, `entries_in_file` | `heritage_mirror/` |
| `HeadwordLists/heritage_dico_gloss_extract.py` | `entry_spans`, `strip_html`, `is_entry_boundary` | `heritage_mirror/` |
| `HeadwordLists/heritage_coverage_current.py` | `coverage` | `heritage_mirror/` |
| `HeadwordLists/screen_candidates.py` | `words` (phrases between punctuation, lower-cased, stop-phrases dropped) | literal vectors |
| `HeadwordLists/works_catalogue/parse_acc.py` | records, malformed header counted, `[Page` and `<b>` stripped, sigla list, `normalize_headword_for_matching` | `acc_mini.txt` |
| `HeadwordLists/works_catalogue/parse_ncc.py` | records, H1671 key repair (ramayana, never namayana), witnesses, `clean_body`, NFC | `ncc_mini.tsv` |
| `HeadwordLists/works_catalogue/build_works_crosswalk.py` | `nasal_and_geminate_fold`, `tier_d_threshold`, `TIER_C_MIN_KEY_LEN`, `load_jsonl` | tmp jsonl |
| `HeadwordLists/works_catalogue/adjudicate_p2.py` | `stem_normalize`, `score_band`, `stratum_for`, `collapse_map`, `MIN_STRATUM` | literal vectors |
| `HeadwordLists/works_catalogue/p2_precision_gate.py` | `wilson_lower` values | literal vectors |
| `HeadwordLists/works_catalogue/apply_p2_decisions.py` | `load_decisions`, `tsv_row`, `TSV_COLS`, `spotcheck_size`; `main` never run (overlay-wipe pattern) | tmp json |
| `data/semdom_ak_metrics.py` | `coarse`, `kappa` | literal vectors |
| `data/definition_typology_classifier.py` | `sentence_period_count` (abbreviation guard), `classify` classes; re-classifying the committed 500-row sample agrees on every untruncated excerpt and ≥ 450/500; gold agreement ≥ 63/79; `verify_sample` warns on an unknown gold label | `data/definition_typology_sample.tsv`, `data/definition_typology_gold.tsv` |
| `data/markup_tag_census.py` | `census_file` counts (`<ls>` = 7 on the mini MW: 6 bodies + 1 header), CLI row `mw\t5\t<ls>\t7\t1400.0` | `csl_orig_mini/` |
| `data/mw_ls_textattest.py` | entries whose only `<ls>` is `L.` → `{a, deva}` | `csl_orig_mini/` |
| `data/headword_overlap_matrix.py` | MW/PWG row `3 4 0.7500`, uniques, `union rows: 5` | `union_mini.tsv` |
| `data/witness_independence_reaudit.py` | policies, `distribution`, `cumulative_ge` | literal vectors |
| `data/semdom_ak_bridge.py` | `gloss_words`, parsers (loaded without nltk) | `amar_mini.txt`, `wn_bridge_mini.tsv` |
| `data/semdom_varga_crosswalk.py` | loaders; cache miss raises `NetworkDisabled` | fixtures |
| `data/annex_*` | `subtree_codes` | literal vectors |
| `data/build_viz_pages.py` | STOP refusals on missing inputs | tmp dir |
| `scripts/changelog_duplicate_bullets.py` | `_normalise`, `find_duplicates` (2 dupes, skipped placeholder + nested label), allowlist, CLI exit 1 / 0 / `--json` (script copied next to a tmp `CHANGELOG.md` because it checks its own repo root) | `changelog_mini.md` |
| `scripts/changelog_dupe_evidence_gate.py` | `count_entries` = 9, `find_changelogs` order | `changelog_mini.md` |
| `scripts/eol_census.py` | `is_text_tracked`, `is_binary`, `cr_candidates` on a throwaway repo, `RuntimeError` on a bad ref | tmp git repo |
| `tools/epistemic_integrity_check.py` | headings, index parity, marker, duplicates, dashboard parity, CLI on good/bad fixtures **and on the live registries** | `epistemic_ok/`, `epistemic_bad/` |
| `tools/audit_features_index_repo_cells.py` | `rows` parser, `REPO_COL`, `HEADER` | `features_index_mini.md` + live `FEATURES_INDEX.md` |
| `epistemic_dashboard/build_epistemic_dashboard.py` | fixture counts; `REFUSED` on an empty dir and on 0 findings, output file must not exist | `epistemic_ok/` |
| `findings_dashboard/build_findings_data.py` | offline `data.json` with null metrics; `FileNotFoundError` on a missing file; `REFUSED` on 0 findings; `read_source` local-first | `epistemic_ok/FINDINGS.md` |
| `findings_dashboard/backfill_ledger_metrics.py` | helpers | `ledger_mini.jsonl` |
| `progress_dashboard/live_refresh.py` | pure helpers | literal vectors |
| `progress_dashboard/build_progress_data.py` | `_load_json` null contract | tmp |
| `progress_dashboard/*_selftest.py` (7) | each runs as a subprocess and exits 0; roster pinned to the seven known names | their own fixtures |

## Deliberately uncovered (8 in-scope modules) and why

1. `HeadwordLists/heritage_crosswalk_report.py` — `main` only; it renders the crosswalk from the live Heritage mirror, no pure function to pin.
2. `HeadwordLists/works_catalogue/build_p2_sheet.py`, `build_p2_spotcheck_sheet.py` — HTML sheet renderers over the full crosswalk; the sheet is a publication artifact, not a contract.
3. `findings_dashboard/monthly_refresh.py` — does `git push`.
4. `findings_dashboard/probe_platforms.py` — network probe by design.
5. `progress_dashboard/build_kitchen_data.py`, `kitchen_slices.py` — need the gitignored RussianTranslation store; every slice is exercised by the seven `*_selftest.py` files the suite runs.
6. `scripts/pre_push_stale_base_check.py` — a 2,000-line git pre-push hook that reads `origin/*`; it has its own selftest in Uprava.

Partially covered on purpose: `progress_dashboard/live_refresh.py` `main`/`publish_gh_pages`/`rebuild` (gh-pages push), `tools/audit_features_index_repo_cells.live_repos` (gh CLI), `heritage_forms_oracle.main` (SL_morph kosha.db), `semdom_ak_bridge.candidates_for` (nltk WordNet), `changelog_dupe_evidence_gate.main` (imports `gate_evidence` from RussianTranslation), `coverage_vs_dcs`/`make_uncovered_lists` file-writing bodies.

Out of the handoff's scope (18 more `.py` files outside RussianTranslation): `EntryAnatomy/`, `LaukikaNyaya/tools/`, `papers/`, `article-comparison/`, `build_features_index_html.py` — one-shot paper and OCR builders, not listed in the H4353 mission.

## Findings

### 1. Pujol accent comparison keyed only ASCII lemmas (fixed here, sheet regeneration pending)

`accent_compare.pujol_entry` and `accent_review.pujol_accents` decomposed each Catalan lemma to NFD and dropped **every** combining mark, not only the acute and grave accents. So `kṛṣṇa` keyed as `krsna`, `śiva` as `siva`, `ātmán` as `atman`, and only lemmas spelled in pure ASCII IAST ever met their Cologne `<k2>` form. Measured on the committed 61,267-lemma list:

| Measure | Value |
|---|---|
| lemmas | 61,267 |
| lemmas with a non-ASCII letter | 50,514 |
| keys changed by the fix | 47,152 |
| lemmas carrying an accent (after fix) | 4,830 |

The fix lifts only U+0301 / U+0300 (and treats an acute on `s` as the letter ś, which NFD spells `s` + U+0301), NFC-recomposes before `to_slp1`, and is pinned by `test_accent_compare_pujol_entry_records_vowel_ordinals` and `test_accent_review_pujol_accents_keeps_diacritics`. **Not done here:** regenerating [accent_disagreements.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Catalan-Pujol/accent_disagreements.tsv) (63 rows) and the "placement mostly agrees" paragraph in [Sanskrit-Catalan-Wordlist-vs-Cologne.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md) needs the csl-orig `<k2>` data, which is outside this suite's offline fence. Both are built from a fraction of the accented lemmas and will grow. Tracked as an `[integrity]` issue in this repo.

### 2. `scripts/eol_census.py` cannot run as committed

It does `import git_ops` from its own directory; that module lives in Uprava `tools/` and is not in this repo. The pure helpers are pinned; the git-backed paths are uncovered until the import is either vendored or made optional.

### 3. Quirks pinned as they are (not defects)

1. `definition_typology_classifier.sentence_period_count` counts a period only when it is not preceded by a letter, so "a god. He rules." counts 0 and "born 1899." counts 1 — an abbreviation guard, pinned as behaviour.
2. `accent_compare.cologne_k2` keeps a comma list such as `deva, devI` as one key, while `headword_diff.key2_forms` splits it.
3. `screen_candidates.words` returns phrases between punctuation, not words.
4. `changelog_duplicate_bullets.py` checks the changelog of its own repo root and ignores a path argument.

_elapsed: about 3 h across two context windows · Fable 5.1 (`claude-fable-5-1`)_

_Dr. Mārcis Gasūns_
