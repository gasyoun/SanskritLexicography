# Roadmap — Claude Code hardening wave (pwg_ru pipeline), 2026H2

_Created: 30-08-2026 · Last updated: 30-08-2026_

Repair lane for the already-KNOWN defect backlog of the pwg_ru pipeline. Discovery of unknown defects stays with the queued OxAlpha review ([PLAN_SANSKRITLEXICOGRAPHY_OXALPHA_CODE_REVIEW_HARDENING_2026Q3.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SANSKRITLEXICOGRAPHY_OXALPHA_CODE_REVIEW_HARDENING_2026Q3.md), H3547) — the two lanes are complementary by design (ruling 2). Index: [PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md).

## Wave units

Ordered core first (W0 alone, then W1); W2–W7 are independent and may run in any order, one worktree each, never two units touching the same module family concurrently (ruling 16).

| Unit | Deliverable | Tier · effort | Unblocked by | Sources |
|---|---|---|---|---|
| **W0** | Master's epistemic integrity gate back to green | Sonnet 5 · 🟡2 | nothing — runs FIRST, alone | [#1864](https://github.com/gasyoun/SanskritLexicography/issues/1864) |
| **W1** | Evidence-carrying gate contract: shared helper; nine gates retrofitted; zero-work PASS becomes FAIL; promote read-modify-write claim hole closed; G9 duplicate-id validity fixed | Opus 5 · 🔴3 | W0 (a RED master gate hollows "merge on green") | [#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803) · [#1800](https://github.com/gasyoun/SanskritLexicography/issues/1800) · [#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798) |
| **W2** | Mechanical hardening batch: H1940-remainder items H3 (fsync checkpoints), H4 (duplicate lease-id), H5 (corrupt status swallowed to empty), H7 (hot-spin drain), H10 (bench rewrites live sidecars) + migration of all 41 sibling-path-guess modules to `sibling_root.py` | Sonnet 5 · 🔴3 | W0 | [H1811 fixlog §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1811/H1811_PIPELINE_REVIEW_FIXLOG_2026-07-29.md) · [#1804](https://github.com/gasyoun/SanskritLexicography/issues/1804) (migration half) |
| **W3** | Provenance measured, not asserted: census of the 93% unmeasured store rows + stamp-backfill design | Opus 5 · 🟡2 | W0 | [#1804](https://github.com/gasyoun/SanskritLexicography/issues/1804) (measurement half) |
| **W4** | Homonym-index logic revision: `h<N>` enumerate-index → true homonym number; full census; ledgered store rewrite + mirror refresh; `key1` degradation census (161 rows) folded | Opus 5 · 🔴3 | W0, W1 (rewrite proves itself through evidence-carrying gates) | [#1801](https://github.com/gasyoun/SanskritLexicography/issues/1801) · [#1767](https://github.com/gasyoun/SanskritLexicography/issues/1767) |
| **W5** | Relation-label logic revision: склейка labels re-derived against actual attachment (4,132 rows point at an absent sense); ledgered repair | Opus 5 · 🔴3 | W0, W1 | [#1736](https://github.com/gasyoun/SanskritLexicography/issues/1736) |
| **W6** | Fragmentizer rejoin: census of glosses interrupted only by an `<is>`…`</is>` run; FINDINGS row; `pwg_tm_fragmentize.py` rejoins them before fragmenting. Re-fragmenting existing rows OUT of scope | Sonnet 5 · 🟡2 | W0 | [GAPS §18](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) |
| **W7** | Perf: top-10 measured hotspots on real hot paths (coordinator claim/audit, ledger, TM); before/after timing per fix | Opus 5 · 🟡2 | W0; runs LAST among parallel units (touches the same files as W1/W2) | Repowise health (coordinator.py 1.0/10; 939 static I/O-in-loop findings as map, not mission) |

## Non-goals

1. No discovery review — that is H3547 (OxAlpha).
2. No live generation, paid windows, router.cheap dispatch, or Max-profile work (W-lane is 100% offline).
3. No mw_ru, frozen HeadwordLists exports, literature/, or ReverseDictionary changes.
4. No LANG_PARITY verdict edits outside the documented re-affirm flow.
5. No re-fragmenting of existing TM rows (W6 fixes the fragmentizer only).
6. No `#1680` timeout-forensics work this wave (stays an open issue).
7. No translation-prompt or semantic-policy redesign; incidental touches must be logged.

_Dr. Mārcis Gasūns_
