# Superseded modules — archived 06-07-2026

_Created: 06-07-2026 · Last updated: 06-07-2026_

Two tracked-but-dead modules moved here by the [H188 audit](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/CODEX_AUDIT_2026-07-05.md)
(finding F5) after an importer sweep confirmed **zero live importers or callers** for each.
Archived rather than deleted so the history is one `git mv` away; they are kept only as
reference for how the current live modules evolved.

| Archived module | Superseded by | Verified 0 importers |
|---|---|---|
| `gen_opt_harness.py` (was `src/pilot/`) | [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) — the canonical production harness (see [`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md)) | `grep -rn "import gen_opt_harness\b"` → only its own docstring + a stale ASCII-diagram comment in `run_real_test.py` |
| `_pilot_gen.py` (was `src/`) | [`src/_pilot_gen_merged.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py) — the live 5-layer merged-source generator (imported by `audit_root_split.py` + `window_selftest.py`) | `grep -rn "import _pilot_gen\b"` → 0 matches |

Do not import from here. If a live module ever needs this logic, lift it back out with
`git mv` (history is preserved) rather than importing across the `archive/` boundary.

_Dr. Mārcis Gasūns_
