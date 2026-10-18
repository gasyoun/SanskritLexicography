# H6936 — HeadwordLists BOM/encoding audit report: 224 files measured, zero drift, zero rewrites

## Added

- **[`docs/ENCODING_BOM_AUDIT_HEADWORDLISTS_17-10-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ENCODING_BOM_AUDIT_HEADWORDLISTS_17-10-2026.md)** ([H6936](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6936-DeepSeek_SanskritLexicography_headwordlists-bom-encoding-audit_17.10.26.md)) — one row per file for the whole `HeadwordLists/` tree: path, BOM state, UTF-8 validity, line endings, exact `size_bytes`, sibling-group flag. **224 files / 220 text / 226,147,961 bytes; 6 files carry a UTF-8 BOM; 0 invalid UTF-8; 0 mixed line endings (LF in all 220 text files); 1 sibling-group flag.**
- Pointer row in [`HeadwordLists/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/README.md) § "Encoding caveat — BOM is inconsistent", so the caveat now carries its measured state and links the table instead of leaving the audit unlinked.

## Findings

- **The BOM census is unchanged since 11-07-2026.** The 6 BOM files are exactly the ones listed in [`docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md) §4 — no drift in three months, and no new BOM crept in through the September/October export waves.
- **The one sibling mismatch is the documented preservation case, not a defect.** `then-2014/MW-unique-key1-193978.txt` carries `EF BB BF` while its two `key2` twins do not. Stripping it would contradict three current sources at once: [`CLAUDE.md` § Encoding](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) ("never silently add/strip one"), [FINDINGS §37](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md), and the [H6518 write contract](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py) shipped the same day in PR [#2416](https://github.com/gasyoun/SanskritLexicography/pull/2416), which names this file as the BOM-preservation example. **No byte was rewritten by this pass**; the strip/keep call is queued as a human ruling in the report §7.

## Fixed (tool, in Uprava)

- [`Uprava/tools/encoding_bom_audit.py`](https://github.com/gasyoun/Uprava/blob/main/tools/encoding_bom_audit.py) no longer reports a valid file as non-UTF-8 when its multi-byte character straddles the 65,536-byte sniff boundary — UTF-8 validity is now a full streaming decode, and the report gained `eol` + `size_bytes` columns (Uprava PR [#5227](https://github.com/gasyoun/Uprava/pull/5227), FINDINGS §1609).

## Verified

- `python Uprava/tools/encoding_bom_audit.py SanskritLexicography/HeadwordLists` → 224 rows, summary `6 with a BOM, 0 invalid UTF-8, 0 mixed line endings, 1 flag`; `--selftest` → `selftest: OK`, including the new 64 KiB-boundary regression.
- No data diff: `git status --porcelain HeadwordLists` and `git diff --stat -- HeadwordLists` are empty in this PR (the only `HeadwordLists/` change is the README pointer row).
- Positive control: a repo-wide run (5,018 files) still flags the genuine invalid-UTF-8 file outside this tree (`RussianTranslation/src/pilot/h4342_fixes/h4213_wave_launch_ATTEMPTS_LOG_06-10.09.2026.txt`).

**Ruled 17-10-2026 (MG): keep** — the strip/keep call raised above is answered, not pending: the flag is documented, intentional state, not a defect (report §4).
