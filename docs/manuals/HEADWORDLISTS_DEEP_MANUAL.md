# HeadwordLists deep manual — SanskritLexicography

_Created: 11-07-2026 · Last updated: 11-07-2026_

Subsystem depth for
[HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists)
— the analytical core of the repo. The orientation layer is
[DATA_REUSE_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md)
§1–2 (read that first for the five-minute version); this manual is the H607
deep pass ([PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
queue) for anyone who must **(a)** regenerate a list from source, **(b)** run a
cross-dictionary join without the key/BOM/transliteration traps, or **(c)** know
which artefacts are frozen snapshots and which are regenerable. Every count
below was re-measured on 11-07-2026 in this pass unless it links to the
committed doc that carries it.

## 0. The one-screen map

Seven families live in the directory. Everything is UTF-8; one line = one
record throughout.

| Family | Where | What | Status |
|---|---|---|---|
| 2014 exports | [then-2014/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014) | 31 `.txt`: key1/key2 exports for 16 dict codes + 2 `fehlerhaft` + SCH accents + the HK join + the Huet list | **frozen** (extracted 2014-10-05) |
| 2026 regenerations | [now-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026) | 23 `.txt`: current csl-orig key1+key2 for 15 dicts (PD absent) | regenerable |
| Cross-dict union | [union/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/union) | the merged 323,425-headword index + fold/coverage sidecars — **the print target** | regenerable |
| Alternate/feminine candidates | [f_candidates/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/f_candidates) | MW + SKD fem↔masc / orphan-fem / variant TSVs (print-readiness item F) | regenerable |
| External spines | [Catalan-Pujol/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/Catalan-Pujol) + [Huet-INRIA-Wordlist-vs-Cologne.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Huet-INRIA-Wordlist-vs-Cologne.md) | Pujol Sanskrit–Catalan lemma list; INRIA Heritage 2014 stem list; their CDSL/DCS coverage studies | raw lists **frozen imports**; analyses regenerable |
| Heritage/INRIA layer | `heritage_*` at [HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists) root | MW↔Heritage crosswalk, French-gloss witness, inflected-forms oracle | regenerable from the **gitignored** mirror (§7) |
| Works catalogue | [works_catalogue/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/works_catalogue) | ACC×NCC works-title crosswalk (not headwords — Sanskrit *work titles*) | regenerable |

QA/decision docs sit at the directory root:
[README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/README.md) (master doc) ·
[NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) (2014→2026 drift) ·
[PRINT_READINESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/PRINT_READINESS.md) (gates A–F) ·
[A_TYPO_QUEUE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/A_TYPO_QUEUE.md) ·
[COVERAGE_ADDITIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/COVERAGE_ADDITIONS.md) ·
[ALTERNATE_HEADWORDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/ALTERNATE_HEADWORDS.md).
One binary: `sanhw1.xlsx` (41,221,158 B — load with a library, never an editor).

## 1. Naming grammar, keys, and the count invariant

```
{DICT}-unique-{key1|key2}-{N}.txt      the main export pattern
{DICT}-fehlerhaft-{N}.txt              flagged entries — FULL XML records, not bare headwords
SCH-accents-IAST-{N}.txt               accented IAST forms
{N}-huet-velthius.txt                  count as PREFIX; Velthuis; non-Cologne
{N}-Sanskrit-Catalan-Words-List.txt    count as PREFIX; accented IAST; non-Cologne
mw-apte-mcdonell-hk.txt                no N; Harvard-Kyoto; MW ∪ Apte ∪ Macdonell join
```

- **`N` is the true entry count** — verified this pass on 7 files across all
  families (key1, key2, fehlerhaft, accents, both prefix-count externals):
  Python line iteration equals `N` exactly in every case. `wc -l` reports
  `N − 1` because the last line has no trailing newline — that off-by-one is
  why prose in older docs sometimes cites one less (e.g. "61,266 lines" for
  the 61,267-entry Catalan file). Trust the filename.
- **key1** = normalized machine key (raw `<k1>`, accent-stripped). Use for
  matching, dedup, joins. **key2** = print/citation form (keeps `/` udātta,
  `-`/`—` compound markers, `(...)`, `*`, `˚`). Use for editorial review,
  citation, scan checking. Semantics:
  [GLOSSARY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md).
- Seven dicts ship **key2 only** (BHS, BUR, CAE, CCS, INM, MD, SCH); PD exists
  only in `then-2014/` (not in csl-orig); `fehlerhaft` exists only for PWG/PWK
  (PWG 1,661 + PWK 2,227 XML records — these are the "PWG/PWK error lists" the
  root README warns about, 5.3 MB and 2.7 MB).
- **Two MW key2 snapshots** sit in `then-2014/`
  ([198220](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/MW-unique-key2-198220.txt)
  vs [198231](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/MW-unique-key2-198231.txt)
  — totals differ by 11, but the content set-diff is 129 entries: 59 only in
  the smaller file, 70 only in the larger, measured 11-07-2026) — confirm
  which you want before relying on either; for anything current use
  [now-2026/MW-unique-key2-198489.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/now-2026/MW-unique-key2-198489.txt).

**Transliteration matrix** — five schemes coexist; never join across families
without transcoding (via [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util)):

| Family | Scheme | Example |
|---|---|---|
| key1/key2 (2026, and 2014 key1) | SLP1 | `aMSa`, key2 `aMSu—ma/t` |
| key2 (2014 snapshots) | **mixed legacy conventions** | BHS/SCH/VEI substantially legacy Cologne numeric (`am2s4a` = aṃśa); MW and most others are SLP1 with older markers (`--` where 2026 has `—`). Measured 11-07-2026: zero digit-keys in MW's 2014 key2 — NOW_VS_THEN's blanket "legacy numeric" verdict phrasing overstates it; the operative fact stands: then-vs-now key2 line-diffs are format migrations, not headword changes |
| SCH-accents / Catalan-Pujol | accented IAST | `ū́ḍhi` · `áṃśa-` |
| mw-apte-mcdonell-hk.txt | Harvard-Kyoto | `aMza` (`z` = ś) |
| 21562-huet-velthius.txt | Velthuis | `a.mza` (`.m` = ṃ, `z` = ś, `f` = ṅ) |

## 2. Frozen vs regenerable — what you may regenerate, and from what

| Artefact | Verdict | Source of truth | How to regenerate |
|---|---|---|---|
| `then-2014/*` | **FROZEN — never regenerate or edit.** The 2014 extraction is the comparison baseline; its value *is* its staleness. | itself | n/a |
| `then-2014/21562-huet-velthius.txt`, `Catalan-Pujol/61267-Sanskrit-Catalan-Words-List.txt` | **FROZEN external imports** (INRIA 2014 export; Pujol spine mirrored from the `sanskrit-lexicon/CORRECTIONS` repo — see [PROVENANCE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Catalan-Pujol/PROVENANCE.md)) | upstream | n/a |
| `now-2026/*` | regenerable | csl-orig `v02` | `python headword_diff.py now` |
| [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) + `_diff/` (gitignored word-level diffs) | regenerable | csl-orig vs `then-2014/` | `python headword_diff.py` |
| `union/union_headwords.tsv` + fold sidecars + [UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md) | regenerable | csl-orig `<k1>` + `<lex>` of all 15 dicts | `python build_union.py` |
| `union/coverage_additions*.tsv` | regenerable | union + `VisualDCS/dcs_lemma_summary.json` + external spines | `coverage_additions.py` → `crosstag_additions.py` |
| `f_candidates/*` | regenerable | csl-orig via the 2026 key sets | `python alternate_headwords.py [DICT]` |
| `heritage_*` TSVs/docs | regenerable **only if the gitignored mirror is present** (§7) | `heritage_mirror/` sparse checkout | the six `heritage_*.py` scripts |
| `works_catalogue/{acc,ncc}.jsonl`, `crosswalk_candidates.jsonl.gz` | regenerable | csl-orig `acc.txt` + VisualDCS NCC file | `parse_acc.py` / `parse_ncc.py` / `build_works_crosswalk.py` |
| [A_TYPO_QUEUE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/A_TYPO_QUEUE.md) | regenerable | sibling repo [SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) `corrections_draft/` | `python assemble_typo_queue.py` |

Scripts read csl-orig at `CSL_ORIG_V02` (default
`C:/Users/user/Documents/GitHub/csl-orig/v02`) and `sanskrit-util` at
`SANSKRIT_UTIL_PY`. The `DICT`→csl-orig mapping is in `headword_diff.py`'s
`CODE2DIR`: note **PWK = csl-orig `pw`** (Böhtlingk's *kürzere Fassung*) and
**PD = None** (the Deccan dictionary has no csl-orig source).

**The count-drift trap.** csl-orig is continuously corrected, so two
regeneration runs weeks apart differ by a handful of lines: the on-disk
[AP-unique-key1-88867.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/now-2026/AP-unique-key1-88867.txt)
carries 88,867 while the later NOW_VS_THEN run measured 88,869 from the same
recipe. Neither is wrong — each `N` is true *for its run date*. Cite the file
you actually used, never "the AP count"; refresh both together when it matters.

## 3. Script census — all 25, what they read and write

All scripts are **read-only toward their sources** (csl-orig, VisualDCS, the
mirror, sibling repos) and write only derived outputs inside `HeadwordLists/`
— every one is safe to re-run; there are no seeders or wipers here. One
write-location exception: `build_p2_sheet.py` writes its HTML review sheet to
the repo-root `review/` directory, not inside `HeadwordLists/`. All 25 follow
the repo Windows-encoding rule (`sys.stdout.reconfigure(encoding='utf-8')`).

**Root — export/diff/union/print-readiness (10):**

| Script | Reads | Writes |
|---|---|---|
| [headword_diff.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py) | csl-orig, `then-2014/` | `now-2026/*`, `_diff/`, drives NOW_VS_THEN.md |
| [build_union.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/build_union.py) | csl-orig `<k1>`/`<lex>` ×15 | `union/union_headwords.tsv`, `folded_feminines.tsv`, `UNION.md` |
| [alternate_headwords.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/alternate_headwords.py) | csl-orig (2026 key sets) | `f_candidates/<D>_*.tsv` |
| [assemble_typo_queue.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/assemble_typo_queue.py) | SanskritSpellCheck drafts | `A_TYPO_QUEUE.md` |
| [coverage_additions.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/coverage_additions.py) | union + DCS lemma summary | `union/coverage_additions.tsv` |
| [crosstag_additions.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/crosstag_additions.py) | additions + Catalan + Huet lists | `union/coverage_additions_crosstagged.tsv` |
| [screen_candidates.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/screen_candidates.py) | `fold_candidates.tsv` + MW glosses | `union/low_candidates_screened.tsv` |
| [accent_review.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/accent_review.py) | Catalan list + csl-orig `<k2>` | `Catalan-Pujol/accent_disagreements.tsv` |
| [huet_coverage.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/huet_coverage.py) | Huet list, csl-orig, DCS | the Huet study; exports the **only Velthuis→IAST→SLP1 transcoder** — other scripts import it |
| [heritage_stem_extract.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_stem_extract.py) | mirror `DICO/*.html` | `heritage_current_stems.txt` |

**Root — Heritage phases 1–5 (5):**
[heritage_coverage_current.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_coverage_current.py) (current-vs-2014 stem coverage) ·
[heritage_mw_crosswalk.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_mw_crosswalk.py) (→ `mw_heritage_crosswalk.tsv`) ·
[heritage_crosswalk_report.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_crosswalk_report.py) (coverage vs DCS + kosha frequency) ·
[heritage_dico_gloss_extract.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss_extract.py) (→ `heritage_dico_gloss.tsv`) ·
[heritage_forms_oracle.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle.py) (Heritage `SL_morph.xml` vs kosha forms — **comparison only, never merges**).

**Catalan-Pujol/ (5):** `coverage_by_dict.py` · `match_rate.py` ·
`make_uncovered_lists.py` · `coverage_vs_dcs.py` (dict × DCS cross-tab →
[DCS-attested-no-CDSL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Catalan-Pujol/DCS-attested-no-CDSL.md)) ·
`accent_compare.py` — see the
[Catalan-Pujol study](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md).

**works_catalogue/ (5):** [parse_acc.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/parse_acc.py) ·
[parse_ncc.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/parse_ncc.py) ·
[build_works_crosswalk.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/build_works_crosswalk.py) ·
[build_p2_sheet.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/build_p2_sheet.py) (HTML review sheet) ·
[apply_p2_decisions.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/apply_p2_decisions.py)
(the one script with an input gate: it requires a human `decisions.json` from
the review sheet — don't invoke without one).

## 4. Encoding — the measured BOM census

The org "csl-orig never has BOMs" rule does **not** hold here. Full census
(first 3 bytes of every `.txt`, measured 11-07-2026): **exactly 6 files carry
`EF BB BF`**, all 2014-era "special" exports —

- `then-2014/MW-unique-key1-193978.txt` (its key2 siblings do **not**)
- `then-2014/PWG-fehlerhaft-1661.txt` and `then-2014/PWK-fehlerhaft-2227.txt`
- `then-2014/SCH-accents-IAST-20247.txt`
- `then-2014/21562-huet-velthius.txt`
- `Catalan-Pujol/61267-Sanskrit-Catalan-Words-List.txt`

Everything else — all of `now-2026/`, all other `then-2014/` exports, the HK
join, all TSVs — has no BOM. Rules: check `head -c 3 file | xxd` before
transforming; **preserve the file's existing BOM state on write**; never
silently add or strip one
([FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) §37).
An injected BOM crashes downstream headword parsers with misleading errors
("init_entries Error 2" — FINDINGS §38), so a BOM mistake surfaces far from
its cause.

## 5. Recipe — a cross-dict join that dodges every trap

1. **Join on key1, from `now-2026/`** unless you specifically need the 2014
   baseline. key2 is for display/citation, not joining
   ([FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   §23: stem vs nominative keying differs across dicts).
2. **Compare by set, never raw `diff`** — `now-2026/` is Sanskrit-collated,
   `then-2014/` is not; use `comm` on `sort`-ed copies or a Python set-diff.
3. **Never line-diff a 2014 key2 file against its 2026 regeneration** — the
   legacy conventions differ (§1 matrix: numeric keys in BHS/SCH/VEI, older
   markers elsewhere), so the big deltas are format migrations
   ([NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md)).
4. **Transcode external lists before matching** (§1 matrix). The Catalan list
   additionally carries an editorial layer — strip `√`, accents, homonym
   digits, and segmentation hyphens (the existing normalizers in
   `Catalan-Pujol/*.py` and `huet_coverage.py` do this; reuse them).
5. **Check the BOM first** (§4) — a BOM'd first line silently fails an exact
   match on the first headword.
6. **Don't rebuild the union** to answer "which dicts attest X" — that's one
   lookup in `union/union_headwords.tsv`
   ([FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   §29: consume, don't rebuild; PWG∩MW = 94,753 within the union).
7. Mining entry **bodies** for extra headwords is a measured dead end — 38.6 %
   precision ([DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §1,
   FINDINGS §30). The corpus side has its own trap: DCS lemma ≠ CDSL headword
   ([ASSUMPTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) §1,
   FINDINGS §12 — 18.6 % of DCS lemmas map to no CDSL headword).

## 6. The union and print-readiness — current state

[union/UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md):
**323,425** headwords across all 15 csl-orig dicts (`slp1, iast, n_dicts,
dicts, gender, fem_fold`), after auto-folding 237 gender-confirmed
`-inī`→`-in` feminines; 180,989 headwords in ≥2 dicts, 142,673 singletons.
The remaining editor worklists: 3,995 ranked `-ā/-ī` fold candidates (the 426
low-confidence ones gloss-screened down to **7** to eyeball), plus per-dict
alternate/variant candidates in `f_candidates/` (MW: 5,036 fem↔masc pairs,
1,217 variant-spelling pairs).

[PRINT_READINESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/PRINT_READINESS.md)
is the gate tracker (A typos · B coverage · C accents · D key2-as-SLP1 ✅ ·
E scope=union ✅ · F feminine policy). As of 11-07-2026 **all agent prep is
done**; what remains is human verification: file the 122 assembled typos
(spine MW 4 + PWG 12 first), rule on ~8 coverage adds and ~7 fold candidates,
confirm the 63 accent adjudications if printing udātta. Headline findings:
the MW/PWG spine is stable (2014→2026 key1 drift +0.1 %/−0.0 %) and
near-print-ready; AP was re-digitised (+146.6 %) and PWK grew +14.7 %, so any
union print must cut from a dated `now-2026/` snapshot; CDSL coverage is
essentially complete (of 21,759 DCS-only lemmas, ~8 are genuinely missing
real words — the rest are lemmatisation artifacts).

## 7. Heritage/INRIA layer — the gitignored-mirror dependency

The raw source — a sparse checkout of
[darkone23/Heritage_Resources](https://github.com/darkone23/Heritage_Resources)
(`DATA/ MW/ DICO/ XML/`, ~167 MB) at `HeadwordLists/heritage_mirror/` — is
**gitignored**: a fresh clone cannot re-run the `heritage_*.py` scripts until
it re-fetches the mirror per
[HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md)
Phase 0 — and `heritage_forms_oracle.py` additionally needs the manually
downloaded `heritage_mirror/manual/SL_morph.xml.gz` (~184 MB decompressed),
which the sparse checkout does not include. What IS committed are the derived witnesses (mirror contents:
[HERITAGE_MIRROR_INVENTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/HERITAGE_MIRROR_INVENTORY.md)):

| Artefact | Rows (data) | What |
|---|--:|---|
| [mw_heritage_crosswalk.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv) | 185,803 | per-MW-entry Heritage coverage flag + DICO anchor (25,140 covered = 13.5 %) — [doc](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.md) |
| [heritage_dico_gloss.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss.tsv) | 24,549 | French gloss prose per covered entry — [doc](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss.md) |
| `heritage_forms_oracle.tsv.gz` + [disagreements](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle_disagreements.tsv) (20,496) | 1,022,526 forms | third inflected-forms witness vs kosha — [doc](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle.md); **oracle only, never merged** |
| [heritage_current_stems.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_current_stems.txt) | 38,343 | current DICO stem inventory (vs the 2014 export's 21,562) |

**Rights:** Heritage data is LGPLLR. Raw mirror data stays gitignored pending
the licence-composition @DECIDE. In the kosha data-hub manifest
([datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json))
the tiers split: `mw_heritage_crosswalk.tsv` is **public** (our own derived
coverage flags — shipped in the `data-v0.1.0` release), while the mirror
itself and the gloss/forms extras (`heritage_dico_gloss`,
`heritage_forms_oracle_disagreements`, `heritage_only_forms`) are
**restricted** — do not republish those, and keep the per-file Heritage
attribution when deriving further.

## 8. works_catalogue/ — ACC×NCC, a works crosswalk (not headwords)

The odd one out: rows are Sanskrit **work titles**, crosswalking Aufrecht's
Catalogus Catalogorum (ACC, from csl-orig, 49,833 rows) against the New
Catalogus Catalogorum (NCC, from VisualDCS, 152,526 rows). Pipeline P0→P2:
parse → tiered fuzzy match (A exact / B nasal+geminate fold / C prefix /
D edit-distance; 169,260 candidate rows) → human review sheet → adjudicated
`works_crosswalk.tsv`. Measured counts:
[P0_COUNTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P0_COUNTS.md) ·
[P1_COUNTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P1_COUNTS.md);
plan: [ROADMAP_ACC_NCC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ACC_NCC.md).
`ncc.jsonl` is 79.6 MB — stream it, don't Read it.

## 9. External spines — Catalan-Pujol and the Huet control

Two independent, non-Cologne headword spines measured the same two ways
(CDSL coverage; DCS-corpus attestation), so each acts as the other's control:

| Spine | Size | CDSL-covered | MW alone | DCS-attested |
|---|--:|--:|--:|--:|
| [Pujol Sanskrit–Catalan](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md) (2005) | 61,267 lines | 91 % | 88.5 % | 46.4 % |
| [Huet/INRIA Heritage stems](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/Huet-INRIA-Wordlist-vs-Cologne.md) (2014 export) | 21,562 lines | 86.2 % | 83.5 % | 60.0 % |

Shared findings worth reusing: both are MW-subsets in practice; roughly half
of dictionary Sanskrit is corpus-unattested "dark matter"; the tiny
corpus-attested-but-no-CDSL corner triages almost entirely to lemmatisation
convention, not missing words. The Catalan study §6 documents Pujol's 11
headword conventions and §7 the udātta comparison (~97 % agreement with
Cologne). The uncovered residue is bucketed in
[Catalan-uncovered/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/Catalan-Pujol/Catalan-uncovered).

## 10. Consumers — who reads these files (change with care)

- **kosha data hub** — `union_headwords.tsv` is registered as
  "THE headword master" and shipped as a release asset; kosha's DCS↔CDSL
  concordance (74,520 links) is built **against** it
  ([PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)).
  Schema changes to the union TSV break downstream joins in another repo.
- **[SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck)** —
  its `union=N` evidence tags come from the union; the typo queue (§6, item A)
  flows back the other way.
- **[csl-atlas](https://github.com/gasyoun/csl-atlas)** — cross-dictionary
  headword atlas (multiplicity, overlap cladogram) consumes the same space.
- **In-repo:** `RussianTranslation/src/corpus_gate.py` pins
  `PWG-unique-key1-106085.txt` — its path predates the `then-2014/` move and
  is **currently broken** (measured 11-07-2026; fix task spun off). The
  lesson generalizes: the 2014→subdirectory reorganisation means any external
  pin to a flat `HeadwordLists/<file>` path must be re-checked.
- **Registries:** dataset rows C13–C17 and D19–D24 in
  [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md);
  reproduction recipe in
  [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) §5;
  the headword-inventory paper draft
  [papers/A40_headword_inventory_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md)
  cites these numbers — keep it in sync if you regenerate.

## 11. Traps checklist (the ones that actually bite)

1. Filename `N` is the true count; `wc -l` = `N − 1` (§1).
2. BOM is inconsistent — 6 files have it; check + preserve (§4).
3. key1 joins, key2 displays — never the reverse (§1, §5).
4. 2014 key2 = mixed legacy conventions; set-compare only, never line-diff (§5).
5. Five transliteration schemes coexist — transcode before matching (§1).
6. `then-2014/` is frozen; regenerating "fixes" it into meaninglessness (§2).
7. Counts drift with csl-orig; stamp every cited count with its run date (§2).
8. The union exists — look up, don't rebuild (§5).
9. `heritage_mirror/` is gitignored — fresh clones can't re-run Heritage
   scripts without the Phase-0 re-fetch; derived TSVs are restricted-tier (§7).
10. `ncc.jsonl` (79.6 MB), `sanhw1.xlsx` (41 MB), and the repo-root giants
    (`DCS_statistical_evaluation.htm` ~75 MB,
    `DCS-Moniers-roots-w-references.html` ~16 MB) — stream, never Read.
11. Flat `HeadwordLists/<file>` pins broke when files moved into
    `then-2014/` — audit any consumer path older than the reorg (§10).

_Dr. Mārcis Gasūns_
