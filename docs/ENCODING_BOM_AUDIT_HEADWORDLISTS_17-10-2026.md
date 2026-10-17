# Encoding / BOM audit — `HeadwordLists`

_Created: 17-10-2026 · Last updated: 17-10-2026_

Executor: **DeepSeek Flash (`deepseek-flash`)** — handoff [H6936](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6936-DeepSeek_SanskritLexicography_headwordlists-bom-encoding-audit_17.10.26.md), 17-10-2026. Read-only audit: **no data byte was rewritten by this pass** (see §6 for the byte receipt).

Tree: [`HeadwordLists/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) at `SanskritLexicography@5aae9100`. Tool: [`Uprava/tools/encoding_bom_audit.py`](https://github.com/gasyoun/Uprava/blob/main/tools/encoding_bom_audit.py) @ `c7da0811d4` (corrected in this pass — §5, [Uprava PR #5227](https://github.com/gasyoun/Uprava/pull/5227)).

## 1. Verdict in one screen

- **224 files** walked (220 text, 4 binary), 226,147,961 bytes.
- **6 files carry a UTF-8 BOM**, all of them the documented 2014-era specials (§3). The census is **byte-identical to the 11-07-2026 measurement** in [`HEADWORDLISTS_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md) §4 — zero BOM drift in three months.
- **0 invalid-UTF-8 files** in this tree, **0 mixed-line-ending files**; line endings are `LF = 220` throughout.
- **1 sibling-group flag**: one, and it is the *documented, deliberately preserved* `MW-unique-key1` BOM (§4) — **not** a stray defect. No file in this tree meets the stray-BOM fix predicate, so this pass rewrote nothing.

> The two handoff acceptance items that assumed a fix — *“the fix PR diff is BOM-only per file”* and *“a re-run reports zero sibling inconsistencies”* — are **not met by design**: reaching zero would require *stripping* a BOM that the repo's own rule forbids stripping (§4). That conflict is the one human ruling this pass surfaces.

## 2. What was run

```sh
# audit only — the tool is read-only and never rewrites
python tools/encoding_bom_audit.py SanskritLexicography/HeadwordLists
python tools/encoding_bom_audit.py --selftest
```

Per file the tool reports: path, BOM state, UTF-8 validity, line endings, exact `size_bytes`.

## 3. BOM census — the 6 files, and why each is not a defect

| # | file | BOM | encoding | eol | size_bytes | twin? | ruling 17-10-2026 |
|---:|---|---|---|---|---:|---|---|
| 1 | [`Catalan-Pujol/61267-Sanskrit-Catalan-Words-List.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Catalan-Pujol/61267-Sanskrit-Catalan-Words-List.txt) | UTF-8 BOM | utf-8 | LF | 836,197 | no twin in tree — single-file export | **keep** (no twin ⇒ no inconsistency) |
| 2 | [`then-2014/21562-huet-velthius.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/21562-huet-velthius.txt) | UTF-8 BOM | utf-8 | LF | 235,151 | no twin in tree — single-file export | **keep** (no twin ⇒ no inconsistency) |
| 3 | [`then-2014/MW-unique-key1-193978.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/MW-unique-key1-193978.txt) | UTF-8 BOM | utf-8 | LF | 2,049,692 | key2 siblings are BOM-free — **documented** | **keep** (FINDINGS §37 + H6518 contract) |
| 4 | [`then-2014/PWG-fehlerhaft-1661.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/PWG-fehlerhaft-1661.txt) | UTF-8 BOM | utf-8 | LF | 5,333,555 | no twin in tree — single-file export | **keep** (no twin ⇒ no inconsistency) |
| 5 | [`then-2014/PWK-fehlerhaft-2227.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/PWK-fehlerhaft-2227.txt) | UTF-8 BOM | utf-8 | LF | 2,736,464 | no twin in tree — single-file export | **keep** (no twin ⇒ no inconsistency) |
| 6 | [`then-2014/SCH-accents-IAST-20247.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/SCH-accents-IAST-20247.txt) | UTF-8 BOM | utf-8 | LF | 243,332 | no twin in tree — single-file export | **keep** (no twin ⇒ no inconsistency) |

The same 6-file list, and the same BOM state, as [`docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md) §4 (measured 11-07-2026). Five of the six are single-file exports with no twin, so no *sibling* inconsistency can attach to them at all.

## 4. The one sibling-group flag — and why it stays

```
then-2014/MW-unique-key1-193978.txt: UTF-8 BOM vs sibling(s) MW-unique-key2-198220.txt, MW-unique-key2-198231.txt = none — sibling BOM inconsistency
```

This is **not** an accident of history that a cleanup pass may delete. Three independent, current sources name this exact file as BOM state to *preserve*:

| Source | What it says |
|---|---|
| [`CLAUDE.md` § Encoding](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) | *“`MW-unique-key1-193978.txt` **has** BOM `EF BB BF`; its key2 sibling does **not**. … preserve the existing BOM state on write, never silently add/strip one.”* |
| [`FINDINGS.md` §37](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) | 🟠 Same rule, sourced from `CLAUDE.md`; “check `head -c 3` before transforming”. |
| [`HeadwordLists/headword_diff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py) | Write-contract #2, shipped **today** in PR [#2416](https://github.com/gasyoun/SanskritLexicography/pull/2416) (H6518): *“BOM PRESERVATION — the output byte-begins with the then-2014 sibling's BOM where that sibling has one (MW-unique-key1 does, its key2 sibling does not …); never added where absent.”* Line 252 implements it: `enc = 'utf-8-sig' if _has_bom(then_path) else 'utf-8'`. |

Consequences that made the fix step a **no-op by rule**, not by oversight:

1. `then-2014/` is a **frozen** snapshot — the manual's standing trap #6: *“regenerating ‘fixes’ it into meaninglessness”*.
2. A BOM is **not** a cosmetic byte here: an injected BOM crashes the headword record parser ([`FINDINGS.md` §38](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — “`init_entries Error 2` is an encoding symptom, not a structure defect”).
3. `headword_diff.py` propagates this file's BOM into every future `now-2026/` regeneration; stripping it silently changes what the next regeneration writes.

**Ruling needed (MG):** keep the flag as documented behaviour, or explicitly authorise a one-time strip of the 3 bytes in a *separate* handoff that also re-pins `headword_diff.py`'s write contract. This pass did not pre-empt that decision.

## 5. Tool defect found and fixed in this pass

The audit's first run reported a **false** non-UTF-8 file:

- `HeadwordLists/Catalan-Pujol/Catalan-uncovered/02-compound-2.md` → `non-UTF-8?`

The file is valid UTF-8 (`113,871` bytes, decodes clean). The cause was the tool's sniff: it read a fixed **65,536-byte prefix** and decoded it. Here byte 65,536 falls *inside* a multi-byte sequence, so `UnicodeDecodeError` fired on the cut, not on the content — a check that reports the chunking of the reader instead of the encoding of the file.

Fixed in [`Uprava/tools/encoding_bom_audit.py`](https://github.com/gasyoun/Uprava/blob/main/tools/encoding_bom_audit.py):

- UTF-8 validity is now decided by a **full streaming decode** in 1 MiB chunks through an incremental decoder (constant memory, split sequences are legal, a real bad byte still fails).
- New `eol` column (`LF` / `CRLF` / `CR` / `mixed` / `none` / `binary`), counted byte-wise in chunks, including the case where `CRLF` straddles a chunk edge.
- New exact `size_bytes` column; summary line reports text/binary split, BOM count, invalid-UTF-8 count, mixed-EOL count and total bytes.
- `--selftest` gained the regression: a multi-byte character placed at the 64 KiB boundary must come back `utf-8`; plus genuinely-invalid bytes, `LF`/`CRLF`/`mixed`, the split-`CRLF` chunk edge, and exact byte sizes.

Positive control that the checker still catches real bad bytes: a repo-wide run (5,018 files, 4,975 text) still flags a genuine one outside this tree — [`RussianTranslation/src/pilot/h4342_fixes/h4213_wave_launch_ATTEMPTS_LOG_06-10.09.2026.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4342_fixes/h4213_wave_launch_ATTEMPTS_LOG_06-10.09.2026.txt) → `non-UTF-8?`. The same run finds **9** BOM files repo-wide: the 6 below plus three outside `HeadwordLists/` (`DCS-Moniers-roots-w-references.html`, `DCS_statistical_evaluation.htm`, `RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.csv`).

## 6. Byte receipt — nothing was rewritten

```sh
git -C SanskritLexicography status --porcelain HeadwordLists   # → empty
git -C SanskritLexicography diff --stat -- HeadwordLists       # → empty
```

No deleted BOM, no added BOM, no re-encoded file, no line-ending normalisation. The audit is read-only by contract, and the fix predicate (*“valid UTF-8 **and** the only defect is a stray BOM”*) matched **no** file in this tree.

## 7. Human-ruling queue

| # | item | why it is not auto-fixable |
|---:|---|---|
| 1 | `then-2014/MW-unique-key1-193978.txt` BOM (3 bytes) vs its BOM-free `key2` twins | Stripping is forbidden by `CLAUDE.md` § Encoding + FINDINGS §37, and the H6518 write contract (PR #2416) names this file as the preservation example. §4. |
| 2 | Repo-wide (out of scope here): `RussianTranslation/src/pilot/h4342_fixes/h4213_wave_launch_ATTEMPTS_LOG_06-10.09.2026.txt` is invalid UTF-8 | Needs a re-encode decision on the file's own ownership lane; listed, never rewritten. |

## 8. Per-file table — every file in the tree

`224` rows, sorted by path. `eol = binary` marks the 4 non-text files.

| path | BOM? | encoding | eol | size_bytes | sibling-group flag |
|---|---|---|---|---:|---|
| `ALTERNATE_HEADWORDS.md` | none | utf-8 | LF | 2,673 |  |
| `A_TYPO_QUEUE.md` | none | utf-8 | LF | 29,907 |  |
| `BHS-CORROBORATED-MISSING-95-17-09-2026.tsv` | none | utf-8 | LF | 8,291 |  |
| `BHS_ANNEXURE_DECOMPOSITION_17-09-2026.md` | none | utf-8 | LF | 6,670 |  |
| `COVERAGE_ADDITIONS.md` | none | utf-8 | LF | 6,316 |  |
| `Catalan-Pujol/61267-Sanskrit-Catalan-Words-List.txt` | UTF-8 BOM | utf-8 | LF | 836,197 |  |
| `Catalan-Pujol/Catalan-uncovered-by-CDSL.txt` | none | utf-8 | LF | 264,524 |  |
| `Catalan-Pujol/Catalan-uncovered/00-suspect-char.md` | none | utf-8 | LF | 5,953 |  |
| `Catalan-Pujol/Catalan-uncovered/01-simple.md` | none | utf-8 | LF | 59,652 |  |
| `Catalan-Pujol/Catalan-uncovered/02-compound-2.md` | none | utf-8 | LF | 113,871 |  |
| `Catalan-Pujol/Catalan-uncovered/03-long-compound-3plus.md` | none | utf-8 | LF | 36,935 |  |
| `Catalan-Pujol/Catalan-uncovered/04-root.md` | none | utf-8 | LF | 1,767 |  |
| `Catalan-Pujol/Catalan-uncovered/05-prefixed-root.md` | none | utf-8 | LF | 5,118 |  |
| `Catalan-Pujol/DCS-attested-no-CDSL.md` | none | utf-8 | LF | 8,058 |  |
| `Catalan-Pujol/PROVENANCE.md` | none | utf-8 | LF | 1,708 |  |
| `Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md` | none | utf-8 | LF | 24,678 |  |
| `Catalan-Pujol/accent_compare.py` | none | utf-8 | LF | 5,449 |  |
| `Catalan-Pujol/accent_disagreements.tsv` | none | utf-8 | LF | 4,360 |  |
| `Catalan-Pujol/coverage_by_dict.py` | none | utf-8 | LF | 2,490 |  |
| `Catalan-Pujol/coverage_vs_dcs.py` | none | utf-8 | LF | 7,590 |  |
| `Catalan-Pujol/make_uncovered_lists.py` | none | utf-8 | LF | 6,553 |  |
| `Catalan-Pujol/match_rate.py` | none | utf-8 | LF | 3,243 |  |
| `DRAFT_REPLY_csl-corrections-119-14-09-2026.md` | none | utf-8 | LF | 4,220 |  |
| `ENRICHMENT_METRICS_REGISTRY.md` | none | utf-8 | LF | 11,515 |  |
| `HERITAGE_MIRROR_INVENTORY.md` | none | utf-8 | LF | 4,764 |  |
| `Huet-INRIA-Wordlist-vs-Cologne.md` | none | utf-8 | LF | 7,514 |  |
| `MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv` | none | utf-8 | LF | 477,008 |  |
| `MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv` | none | utf-8 | LF | 657,540 |  |
| `MW-NACHTRAG-PROPOSALS-15-09-2026.tsv` | none | utf-8 | LF | 47,174 |  |
| `MW-NACHTRAG-SPOTCHECK-30-14-09-2026.tsv` | none | utf-8 | LF | 1,797 |  |
| `MW-NACHTRAG-SPOTCHECK-30-15-09-2026.tsv` | none | utf-8 | LF | 2,445 |  |
| `MW-NACHTRAG-TIERA-STUBS-14-09-2026.md` | none | utf-8 | LF | 96,508 |  |
| `MW-NACHTRAG-TIERA-STUBS-15-09-2026.md` | none | utf-8 | LF | 96,508 |  |
| `MW-NACHTRAG-TYPOLOGY-15-09-2026.md` | none | utf-8 | LF | 21,093 |  |
| `MW-STARRED-NACHTRAG-ADJUDICATION-14-09-2026.tsv` | none | utf-8 | LF | 486,802 |  |
| `MW-STARRED-NACHTRAG-SPOTCHECK-30-14-09-2026.tsv` | none | utf-8 | LF | 2,160 |  |
| `MW-STARRED-NACHTRAG-TIERA-STUBS-14-09-2026.md` | none | utf-8 | LF | 164,853 |  |
| `MW-UNABSORBED-CENSUS-ALL-LAYERS-16-09-2026.tsv` | none | utf-8 | LF | 344 |  |
| `MW-UNABSORBED-CENSUS-HOMONYM-EXTENSIONS-16-09-2026.tsv` | none | utf-8 | LF | 48,289 |  |
| `MW-UNABSORBED-CENSUS-POS-CLASS-16-09-2026.tsv` | none | utf-8 | LF | 1,598 |  |
| `MW-UNABSORBED-CENSUS-ROUTING-16-09-2026.md` | none | utf-8 | LF | 5,458 |  |
| `MW-UNABSORBED-CENSUS-WIDENED-16-09-2026.md` | none | utf-8 | LF | 13,263 |  |
| `MW-missing-PW-Nachtrag-candidates-14-09-2026.md` | none | utf-8 | LF | 7,206 |  |
| `MW-missing-PW-Nachtrag-candidates-14-09-2026.tsv` | none | utf-8 | LF | 240,626 |  |
| `MW72-CLASSES-ADJUDICATION-15-09-2026.tsv` | none | utf-8 | LF | 415,652 |  |
| `MW72-CLASSES-SPOTCHECK-30-15-09-2026.tsv` | none | utf-8 | LF | 1,881 |  |
| `MW72-CLASSES-TIERA-STUBS-15-09-2026.md` | none | utf-8 | LF | 130,700 |  |
| `MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md` | none | utf-8 | LF | 16,969 |  |
| `MW_PWK_CORRIGENDA_PAIRS_11-09-2026.md` | none | utf-8 | LF | 8,468 |  |
| `MW_PWK_NACHTRAEGE_MISSING_ENTRIES_TRIAL_14-09-2026.md` | none | utf-8 | LF | 11,608 |  |
| `MW_PWK_NACHTRAEGE_TRIAL_INDEPENDENT_RECHECK_14-09-2026.md` | none | utf-8 | LF | 10,571 |  |
| `NATIVE_DICTS_MW99_ENRICHMENT_17-09-2026.md` | none | utf-8 | LF | 7,677 |  |
| `NOW_VS_THEN.md` | none | utf-8 | LF | 21,307 |  |
| `PRINT_READINESS.md` | none | utf-8 | LF | 7,821 |  |
| `PWG_MW99_ENRICHMENT_17-09-2026.md` | none | utf-8 | LF | 7,763 |  |
| `README.md` | none | utf-8 | LF | 27,711 |  |
| `accent_review.py` | none | utf-8 | LF | 5,286 |  |
| `alternate_headwords.py` | none | utf-8 | LF | 4,834 |  |
| `assemble_typo_queue.py` | none | utf-8 | LF | 5,595 |  |
| `bhs_dcs_mw_key2_crosswalk.py` | none | utf-8 | LF | 9,604 |  |
| `bhs_dcs_mw_key2_crosswalk.tsv` | none | utf-8 | LF | 981,867 |  |
| `bhs_dcs_mw_key2_crosswalk_report_15-09-2026.md` | none | utf-8 | LF | 4,646 |  |
| `bhs_dcs_mw_key2_crosswalk_stats.json` | none | utf-8 | LF | 7,208 |  |
| `bhs_enrichment_decompose.py` | none | utf-8 | LF | 17,525 |  |
| `build_union.py` | none | utf-8 | LF | 11,123 |  |
| `build_union16.py` | none | utf-8 | LF | 8,124 |  |
| `cdsl_index.py` | none | utf-8 | LF | 14,507 |  |
| `coverage_additions.py` | none | utf-8 | LF | 5,298 |  |
| `crosstag_additions.py` | none | utf-8 | LF | 3,604 |  |
| `enrichment_compare.py` | none | utf-8 | LF | 14,889 |  |
| `enrichment_matrix_17-09-2026.tsv` | none | utf-8 | LF | 493 |  |
| `enrichment_metrics_registry_17-09-2026.json` | none | utf-8 | LF | 4,738 |  |
| `enrichment_metrics_registry_17-09-2026.tsv` | none | utf-8 | LF | 820 |  |
| `f_candidates/MW_fem_masc.tsv` | none | utf-8 | LF | 183,692 |  |
| `f_candidates/MW_multi_k2.tsv` | none | utf-8 | LF | 22 |  |
| `f_candidates/MW_orphan_fem.tsv` | none | utf-8 | LF | 569,351 |  |
| `f_candidates/MW_variants.tsv` | none | utf-8 | LF | 39,391 |  |
| `f_candidates/README.md` | none | utf-8 | LF | 1,588 |  |
| `f_candidates/SKD_fem_masc.tsv` | none | utf-8 | LF | 6,380 |  |
| `f_candidates/SKD_multi_k2.tsv` | none | utf-8 | LF | 22 |  |
| `f_candidates/SKD_orphan_fem.tsv` | none | utf-8 | LF | 203,516 |  |
| `f_candidates/SKD_variants.tsv` | none | utf-8 | LF | 21,832 |  |
| `headword_diff.py` | none | utf-8 | LF | 17,867 |  |
| `headword_diff_selftest.py` | none | utf-8 | LF | 10,186 |  |
| `heritage_coverage_current.py` | none | utf-8 | LF | 4,010 |  |
| `heritage_crosswalk_report.py` | none | utf-8 | LF | 2,789 |  |
| `heritage_current_candidates_no_cdsl.txt` | none | utf-8 | LF | 1,663 |  |
| `heritage_current_stems.txt` | none | utf-8 | LF | 411,800 |  |
| `heritage_dico_gloss.md` | none | utf-8 | LF | 7,152 |  |
| `heritage_dico_gloss.tsv` | none | utf-8 | LF | 4,488,576 |  |
| `heritage_dico_gloss_extract.py` | none | utf-8 | LF | 6,253 |  |
| `heritage_forms_oracle.md` | none | utf-8 | LF | 11,272 |  |
| `heritage_forms_oracle.py` | none | utf-8 | LF | 12,403 |  |
| `heritage_forms_oracle.tsv.gz` | binary | binary | binary | 538,102 |  |
| `heritage_forms_oracle_disagreements.tsv` | none | utf-8 | LF | 1,378,585 |  |
| `heritage_forms_oracle_stats.json` | none | utf-8 | LF | 1,843 |  |
| `heritage_freq_diff.py` | none | utf-8 | LF | 11,093 |  |
| `heritage_frequency_diff.md` | none | utf-8 | LF | 10,430 |  |
| `heritage_frequency_diff.tsv` | none | utf-8 | LF | 3,596,361 |  |
| `heritage_mw_crosswalk.py` | none | utf-8 | LF | 5,248 |  |
| `heritage_only_forms.tsv` | none | utf-8 | LF | 29,341,368 |  |
| `heritage_stem_extract.py` | none | utf-8 | LF | 2,105 |  |
| `huet_coverage.py` | none | utf-8 | LF | 4,583 |  |
| `mw72_baseline_sup7.py` | none | utf-8 | LF | 5,976 |  |
| `mw72_baseline_sup7.tsv` | none | utf-8 | LF | 373,850 |  |
| `mw72_classes_adjudicate.py` | none | utf-8 | LF | 13,867 |  |
| `mw72_uptake_evolution.tsv` | none | utf-8 | LF | 315 |  |
| `mw_heritage_crosswalk.md` | none | utf-8 | LF | 4,503 |  |
| `mw_heritage_crosswalk.tsv` | none | utf-8 | LF | 3,078,150 |  |
| `mw_nachtrag_typology.py` | none | utf-8 | LF | 10,149 |  |
| `mw_pw_sup7_missing_entries.py` | none | utf-8 | LF | 6,743 |  |
| `mw_pw_sup7_missing_entries.tsv` | none | utf-8 | LF | 1,454,586 |  |
| `mw_pw_sup7_reverse_overlap.tsv` | none | utf-8 | LF | 75,663 |  |
| `mw_pwk_corrigenda_pairs.py` | none | utf-8 | LF | 7,511 |  |
| `mw_pwk_corrigenda_pairs.tsv` | none | utf-8 | LF | 23,573,110 |  |
| `mw_pwk_nachtraege_adjudicate.py` | none | utf-8 | LF | 19,131 |  |
| `mw_pwk_nachtraege_candidates_14-09-2026.tsv` | none | utf-8 | LF | 261,002 |  |
| `mw_pwk_nachtraege_missing_entries.py` | none | utf-8 | LF | 12,946 |  |
| `mw_pwkvn_missing_entries.py` | none | utf-8 | LF | 7,108 |  |
| `mw_pwkvn_missing_entries.tsv` | none | utf-8 | LF | 792,412 |  |
| `mw_pwkvn_sup_overlap.tsv` | none | utf-8 | LF | 338,741 |  |
| `mw_unabsorbed_census.py` | none | utf-8 | LF | 18,270 |  |
| `nachtrag_dcs_samples.tsv` | none | utf-8 | LF | 3,371 |  |
| `nachtrag_uptake_details.py` | none | utf-8 | LF | 9,237 |  |
| `native_dicts_mw99_enrichment_17-09-2026.json` | none | utf-8 | LF | 4,163 |  |
| `native_dicts_mw99_enrichment_17-09-2026.tsv` | none | utf-8 | LF | 392 |  |
| `now-2026/AP-unique-key1-88867.txt` | none | utf-8 | LF | 862,262 |  |
| `now-2026/AP-unique-key2-88828.txt` | none | utf-8 | LF | 863,653 |  |
| `now-2026/BHS-unique-key2-18188.txt` | none | utf-8 | LF | 196,028 |  |
| `now-2026/BUR-unique-key2-19251.txt` | none | utf-8 | LF | 148,603 |  |
| `now-2026/CAE-unique-key2-39280.txt` | none | utf-8 | LF | 363,364 |  |
| `now-2026/CCS-unique-key2-29233.txt` | none | utf-8 | LF | 256,981 |  |
| `now-2026/GRA-unique-key1-11108.txt` | none | utf-8 | LF | 85,616 |  |
| `now-2026/GRA-unique-key2-11453.txt` | none | utf-8 | LF | 101,780 |  |
| `now-2026/INM-unique-key2-9454.txt` | none | utf-8 | LF | 95,309 |  |
| `now-2026/MD-unique-key2-20107.txt` | none | utf-8 | LF | 159,340 |  |
| `now-2026/MW-unique-key1-194084.txt` | none | utf-8 | LF | 2,050,081 |  |
| `now-2026/MW-unique-key2-198489.txt` | none | utf-8 | LF | 2,512,664 |  |
| `now-2026/NOW_COUNT_DELTA.md` | none | utf-8 | LF | 3,582 |  |
| `now-2026/PD-unique-key1-104959.txt` | none | utf-8 | LF | 1,476,413 |  |
| `now-2026/PD-unique-key2-104968.txt` | none | utf-8 | LF | 1,478,291 |  |
| `now-2026/PWG-unique-key1-106082.txt` | none | utf-8 | LF | 1,021,661 |  |
| `now-2026/PWG-unique-key2-110438.txt` | none | utf-8 | LF | 1,075,184 |  |
| `now-2026/PWK-unique-key1-151349.txt` | none | utf-8 | LF | 1,551,540 |  |
| `now-2026/PWK-unique-key2-155688.txt` | none | utf-8 | LF | 1,640,248 |  |
| `now-2026/README.md` | none | utf-8 | LF | 3,721 |  |
| `now-2026/SCH-unique-key2-28519.txt` | none | utf-8 | LF | 287,711 |  |
| `now-2026/SKD-unique-key1-40817.txt` | none | utf-8 | LF | 386,104 |  |
| `now-2026/SKD-unique-key2-40817.txt` | none | utf-8 | LF | 386,109 |  |
| `now-2026/VCP-unique-key1-48636.txt` | none | utf-8 | LF | 442,212 |  |
| `now-2026/VCP-unique-key2-48638.txt` | none | utf-8 | LF | 442,255 |  |
| `now-2026/VEI-unique-key1-3704.txt` | none | utf-8 | LF | 31,980 |  |
| `now-2026/VEI-unique-key2-3704.txt` | none | utf-8 | LF | 31,980 |  |
| `pw_nachtrag_adjudicate.py` | none | utf-8 | LF | 9,117 |  |
| `pw_nachtrag_vs_mw.py` | none | utf-8 | LF | 10,588 |  |
| `pwg_mw99_enrichment_17-09-2026.json` | none | utf-8 | LF | 881 |  |
| `pwg_mw99_enrichment_17-09-2026.tsv` | none | utf-8 | LF | 139 |  |
| `sanhw1.xlsx` | binary | binary | binary | 41,221,158 |  |
| `screen_candidates.py` | none | utf-8 | LF | 3,524 |  |
| `then-2014/21562-huet-velthius.txt` | UTF-8 BOM | utf-8 | LF | 235,151 |  |
| `then-2014/AP-unique-key1-36030.txt` | none | utf-8 | LF | 296,415 |  |
| `then-2014/AP-unique-key2-36704.txt` | none | utf-8 | LF | 303,026 |  |
| `then-2014/BHS-unique-key2-17784.txt` | none | utf-8 | LF | 237,732 |  |
| `then-2014/BUR-unique-key2-19238.txt` | none | utf-8 | LF | 148,559 |  |
| `then-2014/CAE-unique-key2-39256.txt` | none | utf-8 | LF | 362,987 |  |
| `then-2014/CCS-unique-key2-29317.txt` | none | utf-8 | LF | 258,543 |  |
| `then-2014/GRA-unique-key1-10315.txt` | none | utf-8 | LF | 79,240 |  |
| `then-2014/GRA-unique-key2-10526.txt` | none | utf-8 | LF | 94,766 |  |
| `then-2014/INM-unique-key2-9466.txt` | none | utf-8 | LF | 95,374 |  |
| `then-2014/MD-unique-key2-20748.txt` | none | utf-8 | LF | 162,479 |  |
| `then-2014/MW-unique-key1-193978.txt` | UTF-8 BOM | utf-8 | LF | 2,049,692 | ⚠️ sibling BOM inconsistency |
| `then-2014/MW-unique-key2-198220.txt` | none | utf-8 | LF | 2,465,454 |  |
| `then-2014/MW-unique-key2-198231.txt` | none | utf-8 | LF | 2,465,600 |  |
| `then-2014/PD-unique-key1-104936.txt` | none | utf-8 | LF | 1,476,251 |  |
| `then-2014/PD-unique-key2-104941.txt` | none | utf-8 | LF | 1,478,111 |  |
| `then-2014/PWG-fehlerhaft-1661.txt` | UTF-8 BOM | utf-8 | LF | 5,333,555 |  |
| `then-2014/PWG-unique-key1-106085.txt` | none | utf-8 | LF | 1,021,623 |  |
| `then-2014/PWG-unique-key2-110402.txt` | none | utf-8 | LF | 1,074,839 |  |
| `then-2014/PWK-fehlerhaft-2227.txt` | UTF-8 BOM | utf-8 | LF | 2,736,464 |  |
| `then-2014/PWK-unique-key1-131918.txt` | none | utf-8 | LF | 1,325,613 |  |
| `then-2014/PWK-unique-key2-133741.txt` | none | utf-8 | LF | 1,386,733 |  |
| `then-2014/SCH-accents-IAST-20247.txt` | UTF-8 BOM | utf-8 | LF | 243,332 |  |
| `then-2014/SCH-unique-key2-28495.txt` | none | utf-8 | LF | 329,381 |  |
| `then-2014/SKD-unique-key1-40551.txt` | none | utf-8 | LF | 383,655 |  |
| `then-2014/SKD-unique-key2-40595.txt` | none | utf-8 | LF | 389,067 |  |
| `then-2014/VCP-unique-key1-47107.txt` | none | utf-8 | LF | 427,867 |  |
| `then-2014/VCP-unique-key2-47145.txt` | none | utf-8 | LF | 436,225 |  |
| `then-2014/VEI-unique-key1-3703.txt` | none | utf-8 | LF | 31,979 |  |
| `then-2014/VEI-unique-key2-3770.txt` | none | utf-8 | LF | 41,455 |  |
| `then-2014/mw-apte-mcdonell-hk.txt` | none | utf-8 | LF | 2,213,332 |  |
| `union-16dicts/UNION16_OVERLAP_REPORT_19-09-2026.md` | none | utf-8 | LF | 5,562 |  |
| `union-16dicts/headword_overlap_matrix.tsv` | none | utf-8 | LF | 3,171 |  |
| `union-16dicts/headword_unique_counts.tsv` | none | utf-8 | LF | 393 |  |
| `union-16dicts/per_dict_profile.tsv` | none | utf-8 | LF | 1,193 |  |
| `union-16dicts/union_headwords_16.tsv` | none | utf-8 | LF | 8,854,601 |  |
| `union/UNION.md` | none | utf-8 | LF | 3,157 |  |
| `union/coverage_additions.tsv` | none | utf-8 | LF | 728,520 |  |
| `union/coverage_additions_crosstagged.tsv` | none | utf-8 | LF | 14,300 |  |
| `union/fold_candidates.tsv` | none | utf-8 | LF | 200,444 |  |
| `union/folded_feminines.tsv` | none | utf-8 | LF | 9,977 |  |
| `union/low_candidates_screened.tsv` | none | utf-8 | LF | 46,457 |  |
| `union/union_headwords.tsv` | none | utf-8 | LF | 12,397,206 |  |
| `works_catalogue/NCC_KEY_REPAIR_MIGRATION_2026.md` | none | utf-8 | LF | 11,359 |  |
| `works_catalogue/P0_COUNTS.md` | none | utf-8 | LF | 3,793 |  |
| `works_catalogue/P1_COUNTS.md` | none | utf-8 | LF | 2,010 |  |
| `works_catalogue/P2_AGENT_ADJUDICATION_REPORT.md` | none | utf-8 | LF | 15,482 |  |
| `works_catalogue/P2_COUNTS.md` | none | utf-8 | LF | 2,088 |  |
| `works_catalogue/P2_PRECISION.md` | none | utf-8 | LF | 2,693 |  |
| `works_catalogue/adjudicate_p2.py` | none | utf-8 | LF | 22,258 |  |
| `works_catalogue/apply_p2_decisions.py` | none | utf-8 | LF | 8,089 |  |
| `works_catalogue/build_p2_sheet.py` | none | utf-8 | LF | 13,612 |  |
| `works_catalogue/build_p2_spotcheck_sheet.py` | none | utf-8 | LF | 11,003 |  |
| `works_catalogue/build_works_crosswalk.py` | none | utf-8 | LF | 16,296 |  |
| `works_catalogue/crosswalk_candidates.jsonl.gz` | binary | binary | binary | 22,652,203 |  |
| `works_catalogue/p2_agent_verdicts.jsonl.gz` | binary | binary | binary | 1,547,659 |  |
| `works_catalogue/p2_precision_gate.py` | none | utf-8 | LF | 12,038 |  |
| `works_catalogue/p2_spotcheck_manifest.json` | none | utf-8 | LF | 149,864 |  |
| `works_catalogue/parse_acc.py` | none | utf-8 | LF | 5,467 |  |
| `works_catalogue/parse_ncc.py` | none | utf-8 | LF | 5,926 |  |
| `works_catalogue/sanskritlexicography-acc_ncc_p2_spotcheck.lock.json` | none | utf-8 | LF | 30,430 |  |
| `works_catalogue/test_parse_ncc.py` | none | utf-8 | LF | 3,423 |  |
| `works_catalogue/works_crosswalk.tsv` | none | utf-8 | LF | 12,896,553 |  |
| `works_catalogue/works_crosswalk_agent_proposed.tsv` | none | utf-8 | LF | 1,116,430 |  |
| `works_catalogue/works_crosswalk_rejected.tsv` | none | utf-8 | LF | 69 |  |

## 9. Reproduce

```sh
python Uprava/tools/encoding_bom_audit.py SanskritLexicography/HeadwordLists
python Uprava/tools/encoding_bom_audit.py --selftest
```

Re-running must reproduce §1's numbers exactly: 224 files / 220 text / 6 BOM / 0 invalid UTF-8 / 0 mixed EOL / 1 flag. Any drift means a new export landed — check `head -c 3` before touching it.

_Dr. Mārcis Gasūns_
