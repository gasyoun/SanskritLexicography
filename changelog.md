# Changelog

All notable changes to SanskritLexicography are documented here.

Entries use dated, versioned releases. Keep upcoming work under [Unreleased],
then **cut a new version every time the changelog is updated** (promote
[Unreleased] to the next `x.y.z` with today's date and start a fresh
[Unreleased]).

Historical note on the version sequence: 1.0.0–1.1.3 were cut mid-June 2026, the
lane then dropped to 0.0.1–0.0.42 snapshot tags (18-06 … 02-07) before resuming
at 1.1.4 on 03-07 — the dip is baked into the published tags and is intentional,
not an error.

## [Unreleased]

## [1.142.8] - 2026-08-04

### Fixed
- **Figure 7.2's axis labels recovered from a shifted symbol font — and re-extraction tested and rejected (Opus 5 `claude-opus-5`, 04-08-2026).** Asked to re-extract the Routledge PDF, the measurement said not to: PyMuPDF's text for the caption page **does not contain the axis labels at all** (`LOG LIKELIHOOD present=False`), so re-extracting would have **deleted** this content rather than repaired it, and `pdftotext` returned an empty page. The `.md` bytes were recoverable instead. The garbled run was a font offset by **exactly +32** — `)TERATION` → `ITERATION`, `,OG` → `LOG`, `-ODEL` → `MODEL`, `0OST` → `POST`, with `\x9f`/`\x99` as minus and multiplication — decoding to Figure 7.2's real axes: tick marks `0…1200` and `−1200…−950`, `ITERATION (× 10000)`, `LOG LIKELIHOOD`, `MODEL A: POST-BURN-IN HARMONIC MEAN = −1001`, `MODEL B: … = −1025`. 63 control characters in that region → **0**, 194 bytes of gibberish → readable text, everything outside the bounded span byte-identical. **The shift is region-local, which is itself the evidence**: applying it to neighbouring prose damages it (`probabilities.` → `probabilitiesN`), confirming only the figure's label run uses the offset font. **The file stays `binary`, and the reason is now measured rather than guessed:** 5 452 control codepoints across **3 818 runs** (~35 KB, 1.4 % of the file), and they are **not one defect** — the bulk is comparative phonetic transcription (Tibeto-Burman cognate tables: `Jmuh 'bone'`, `k²a9`, `sùp sum`) rendered through non-Unicode fonts, plus at least one block on a *different* offset. Each needs its own font mapping, so a blanket +32 would corrupt them. A full repair is a re-typesetting/OCR project, not an encoding fix.

## [1.142.7] - 2026-08-04

### Fixed
- **NUL bytes stripped from both `literature/md/` offenders — which fixed one of them and proved the other was never a NUL problem (Opus 5 `claude-opus-5`, 04-08-2026).** Follow-up to [#1127](https://github.com/gasyoun/SanskritLexicography/pull/1127), which had declared both `binary` as a holding action. **The two files needed opposite treatments**, and a blanket strip would have damaged one: in `Общий синтаксис/AEK_et_al_corrected_2020.md` the 2 NULs sat **alone on their own line** between blank lines, immediately before `Рисунок 1.2.` — a PDF image-extraction artefact standing where a figure was, so they were **deleted** (2 666 859 → 2 666 857 bytes). In `Lexicography-Manuals/THE ROUTLEDGE HANDBOOK OF HISTORICAL LINGUISTICS.md` the 15 NULs are interspersed through an already-garbled symbol-font table (`,OG\0,IKELIHOOD`, `\0HARMONIC\0MEAN\0` — i.e. "LOG LIKELIHOOD", "HARMONIC MEAN" with the leading glyph mangled), where NUL is doing the job of the **word separator**; deleting would have fused tokens into `,OG,IKELIHOOD`, so each was **replaced with a space** (length unchanged). **Outcome differs per file, and that is the finding:** AEK reclassified to `i/lf` and its `binary` exemption is **removed** — it is now ordinary `text eol=lf` like every other `.md`. Routledge stayed `i/-text` even with zero NULs, because its garbled region is dense with control bytes (`\x08 \x10 \x11 \x15 \x1a`) that git's binary heuristic reads as binary independently of NUL — so **NUL was never that file's blocker**, its exemption is retained with the corrected reason, and the real repair is re-extracting the source PDF. Verified: zero NUL bytes in both committed blobs; `git check-attr` confirms `binary: unspecified` for AEK and `binary: set` for Routledge.

## [1.142.6] - 2026-08-04

### Fixed
- **The last two permanently-dirty `literature/md/` files declared `binary` — they carry NUL bytes and were never normalizable (Opus 5 `claude-opus-5`, 04-08-2026).** After [#1125](https://github.com/gasyoun/SanskritLexicography/pull/1125) cleared all 29 renormalizable blobs, two files still read as modified on every checkout: `Общий синтаксис/AEK_et_al_corrected_2020.md` and `Lexicography-Manuals/THE ROUTLEDGE HANDBOOK OF HISTORICAL LINGUISTICS.md`. Cause: they contain **2 and 15 NUL bytes** respectively, which trips git's binary heuristic, so git classifies them `-text` **regardless of the `*.md text eol=lf` rule** and `git add --renormalize` silently skips them. They were simultaneously invisible to the standard audit, which greps `i/crlf|i/mixed` and never matches `i/-text` — a file can be permanently dirty *and* absent from every census of the problem. Declared `binary` so git's actual behaviour is on the books rather than leaving a rule that cannot apply. **Removing the NUL bytes was deliberately not done**: that is a content edit to source documents, not a whitespace fix, and it remains open should the bytes turn out to be extraction artefacts worth deleting. One pattern is quoted (`"…HISTORICAL LINGUISTICS.md" binary`) because `.gitattributes` splits pattern from attributes on whitespace, so an unquoted path containing spaces parses as a different pattern plus stray attribute tokens; the other uses `**/` so the space-bearing Cyrillic directory never has to appear. Verified with `git check-attr` (`binary: set`, `text: unset`) and by each pattern matching exactly one tracked file.

## [1.142.5] - 2026-08-04

### Fixed
- **The `literature/md/` renormalization finished — #1123 converted nothing that reached the commit (Opus 5 `claude-opus-5`, 04-08-2026):** the pass below reported 31 files renormalized, but the blobs at that very commit (`15c596f43`) were still CRLF: `git ls-files --eol` showed **29** files flagged `i/mixed` against `attr/text eol=lf` immediately afterwards, and a fresh `git add --renormalize` on one of them (`Speyer-Syntax1886.md`, explicitly part of #1123) produced 31 299 changed lines. So the conversion was computed and then lost before it landed — the commit rewrote 333 343 lines while leaving the stored objects CRLF. Only **10** of the 29 still-flagged files even overlapped #1123's set; the other **19** were never touched by it. All 29 are now converted in one pass. **Proof the change is line-terminator-only, not content:** `git diff --cached --ignore-cr-at-eol` is empty, no git-detected binary appears in the staged set, and the byte delta per file equals its CRLF count exactly (`Speyer-Syntax1886.md`: 830 402 → 800 294 bytes = 30 108 lost bytes against 30 108 CRLF pairs — one byte per CR, nothing else). Path handling was the trap worth noting: these names carry spaces and Cyrillic, and git's octal-quoted output (`"literature/md/\320\222…"`) fed back into `cat-file` resolves to nothing and silently reads as "0 CRs", so every measurement here used `core.quotePath=false` with explicit argv. Same class as [Uprava FINDINGS §299/§305](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md), but a **different cause**: Uprava's blobs were re-created by a plumbing writer, whereas these simply never had their conversion committed.
- **CRLF-committed `literature/md/` blobs renormalized to `eol=lf` (Sonnet 5 `claude-sonnet-5`, 04-08-2026, [PR #1123](https://github.com/gasyoun/SanskritLexicography/pull/1123)) — PARTIAL, completed by the entry above:** 31 files under `literature/md/` were committed with CRLF, violating this repo's own `.gitattributes` (`*.md text eol=lf`) — making them permanently phantom-dirty on every fresh checkout, on any branch, regardless of local `core.autocrlf`. Found while diagnosing RED entries in [Uprava H2033](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2033-Sonnet_Uprava_tidy-worktree-gc-full-backlog_31.07.26.md)'s dirty-tree-sweep backlog; same bug class as [Uprava FINDINGS.md §299/§305](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md). Fixed via `git add --renormalize .`, verified byte-for-byte that every staged blob equals `HEAD content with CRLF replaced by LF` — zero semantic content change.

## [1.142.4] - 2026-08-04
### Changed
- **H2238 — progress kitchen B7: nominal + medium-50 burn-down with structured pause reasons (Sonnet 5 `claude-sonnet-5`, override dual-run of a Grok 4.5-tagged handoff, 04-08-2026):** `progress_dashboard/build_progress_data.py`'s `nominal_lane()` and the new `progress_dashboard/kitchen_slices.py:eta_nominal()` add live burn-down fields (`remaining`/`pct`, mirroring the verb lane's `universe`/`promoted`/`runnable` shape) and a "Nominal burn-down" ETA panel in `index.html`, alongside the existing verb one. The medium-50 band's promoted count is now **live-measured** (H317 worklist keys intersected against `pwg_ru_translated.jsonl`, confirmed matching the prior hardcoded 2/50) instead of a hardcoded constant, and its pause reason is a structured `{code, label, detail, docs, doc_urls}` object (`killgate_cascade`, H437/H442/H462) rendered as a badge + tooltip, not prose-only. `medium50_measured`/fallback-constant flags preserve the existing `est()` "documented constant" convention when the live worklist file is absent.

### Added
- **H2240 — canonical `health_probe_log.jsonl` writer for the progress kitchen's health ribbon (B3 residual; Sonnet 5 `claude-sonnet-5`, override dual-run of a Grok 4.5-tagged handoff, 04-08-2026):** `kitchen_slices.health_ribbon` used to glob-scrape every `h963_*_gate0_probe_events.jsonl` / `*_probe_events.jsonl` under `pilot/output` per account. `live_probe`'s `_emit` (`RussianTranslation/src/pilot/max_account_orchestrator.py`) now ALSO appends every probe reading (any account, any script) into ONE canonical `output/health_probe_log.jsonl`, best-effort alongside the existing per-account file — which stays untouched since gate reports (H1110/H1447/H858) cite it by path and its exact-run_id read discipline (#729) is unrelated. `health_ribbon` (`progress_dashboard/kitchen_slices.py`) now prefers the canonical file **exclusively** when present, falling back to the old glob scrape only for a pre-H2240 checkout. `RussianTranslation/src/pilot/migrate_health_probe_log.py` folds any pre-existing per-account history into the canonical file once, idempotently (dedupe key `run_id, purpose, account`). Pinned by `progress_dashboard/health_ribbon_selftest.py` (3/3) plus the unchanged `h963_c4_gate0_probe.py --selftest` (7/7). **Dual-run note:** this handoff is filename-locked to Grok 4.5; executed here on Sonnet 5 per MG override — residual [H2269](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2269-Grok_SanskritLexicography_h2240-sonnet-dual-run-compare_04.08.26.md) requires an independent Grok 4.5 re-run + comparison.

## [1.142.2] - 2026-08-04
### Added
- **H2241 — progress-kitchen K-slice points in `progress_timeseries.json` (Sonnet 5 `claude-sonnet-5`, override dual-run of a Grok 4.5-locked handoff, 04-08-2026):** [`build_progress_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_progress_data.py) now reads the sibling `kitchen_data.json` build and appends four daily kitchen fields to each `progress_timeseries.json` row — `kitchen_yield_clean_pct`, `kitchen_health_last_verdict` + `kitchen_health_last_go` (1/0), `kitchen_idle_hours`. [`index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/index.html) trend charts gained two new lines (clean-window % and idle hours). [PR #1112](https://github.com/gasyoun/SanskritLexicography/pull/1112) · [H2241](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2241-Grok_SanskritLexicography_progress-kitchen-timeseries-slices_03.08.26.md). Filename-locked to Grok 4.5, executed on Sonnet 5 per human override; Grok 4.5 dual-run/compare residual open at [H2268](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2268-Grok_SanskritLexicography_h2241-dual-run-compare_04.08.26.md).

## [1.142.1] - 2026-08-04
### Fixed
- **H2194 — Sa→Ru gloss vidyut tier: krdanta-collapse lemma guard (Fable 5 `claude-fable-5`, 04-08-2026):** the wave-2 panel's lemma-defect class 2 (derived nominals lemmatized to a bare verbal root — `janitṛ`→jan, `liṅgin`→liṅg; the vidyut tier's 71.8 % lemma precision, worst of the three tiers) is a ranking defect in [`build_vidyut_fallback.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_vidyut_fallback.py): kosha lists a krdanta-derived Subanta under the bare **dhatu** as its lemma, so entry-count voting lets the collapses outnumber the real stem (`janitf`: 12 × `jan` vs 3 × `janitf`; even `rAmeRa` lemmatized to the root `ram`, not `rAma`). `pick_primary_and_alts` now takes the set of candidates backed by a `PratipadikaEntry.Basic` (real nominal stem) and demotes krdanta-only noun candidates whenever a Basic one exists — demoted lemmas stay in the `vidyut_ambiguity.tsv` trail, verbs are never touched, forms with no Basic candidate keep the old pick, and `basic=None` reproduces the pre-fix ranking exactly. 5 new Fixture-D regression tests (real kosha-0.4.0 tallies) bring [`tests/test_saru_gloss_pipeline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_saru_gloss_pipeline.py) to 12 passing; before/after table in [`RussianTranslation/RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md). Published data not regenerated (D8 gate); classes 1 and 3 remain open wave-3 targets. Ask-batch residual W1-GL of [PLAN_RussianTranslation_ask_batch_residual_2026-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_ask_batch_residual_2026-08.md) · [H2194](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2194-Fable_RussianTranslation_askbatch-saru-gloss-residual-2026-08_02.08.26.md).

## [1.142.0] - 2026-08-03

### Fixed
- **H2249 — `bare_cli_cwd()` now verifies the ANCESTRY, closing the 32 779 B/call operator-memory leak H2189 §1.1 could only report (Opus 5 1M `claude-opus-5[1m]`, 03-08-2026):** the open defect logged one section below is closed. H2158's ancestor walk rejected a parent carrying a bare `CLAUDE.md` or a `.git` — but **not** one carrying `.claude\CLAUDE.md`, `.claude\CLAUDE.local.md` or `.claude\rules` — and the directory it returned lives under `%TEMP%`, i.e. *under the Windows user profile*, which is exactly where the operator's global memory sits. `C:\Users\user\.claude\CLAUDE.md` (31 625 B) + `.claude\rules` (1 154 B) reached **every headless call** for the day between H2158 and this fix, invisible because the spawn directory itself is empty. [`bare_cli_cwd()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) now **derives** candidates — an operator `PWG_RU_CLI_CWD` override, then the historical `%TEMP%` location (behaviour unchanged wherever temp is already clean, e.g. POSIX `/tmp`), then each **FIXED** filesystem root the OS reports via `GetLogicalDrives`/`GetDriveTypeW` with the system drive last (so a removable or disconnected network drive is never probed and cannot stall the walk) — and returns one **only after** [`h2189_min_profile.cwd_ancestry_scan`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2189_min_profile.py) proves the whole ancestry carries no memory marker; otherwise `None`, the historical inherited-cwd behaviour. **No drive letter is hardcoded** — `D:\ClaudeTools\pwg_ru_clean_cwd` was the H2189 A/B arm and is the cheapest clean ancestry on this box, but a drive letter in the source degrades silently to `None` on any other machine. **No second ancestor walker**: `cwd_ancestry_scan` stays the single source, so a marker added there reaches the spawn path automatically instead of drifting into two half-updated lists — and its import fails **closed and loud**, because "could not prove it clean" and "proved it clean" must never collapse into the same answer on the path that decides what the model is handed. Verified offline, **no paid window spent**: `--scan-cwd` reports **0 injectable bytes** for the resolved `D:\pwg_ru_cli_cwd` against **32 779 B** for the old `%TEMP%` path. The H2189 pin `test_bare_cwd_ancestry_is_reported_even_though_it_is_not_yet_clean` shipped as a deliberate *measurement* — it would have failed on the very box it ships to — and is now the assertion `test_bare_cwd_ancestry_is_clean_or_none`, joined by `test_bare_cwd_candidates_are_derived_not_hardcoded` and `test_bare_cwd_refuses_a_dirty_ancestry_rather_than_returning_it` (synthetic `.claude/CLAUDE.md` ancestor, empty child fed through the override, refusal required). Gates: `window_selftest` **209/209**, `headless_worker_selftest` PASS, `lang_parity_check` 92 entries no drift (5 entries re-derived on `headless_worker.py`, every verdict SHARED, **0** language-keyed tokens in the diff — the change alters *where* the CLI child is spawned from, a property of the spawn and never of the target language). `--safe-mode` only **masked** this and is untouched: it remains the separate, opt-in **profile**-surface lever, and is no longer what stands between the operator's global `CLAUDE.md` and a paid call. [PR #1090](https://github.com/gasyoun/SanskritLexicography/pull/1090) · [H2249](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2249-Opus_SanskritLexicography_pwg-bare-cwd-ancestry-leak-fix_03.08.26.md).

## [1.141.10] - 2026-08-03

## [1.141.11] - 2026-08-03
### Fixed
- **H2173 — the H2025 audit tail: unaccountable payload rows, an unchecked promote route, and a classifier that was inert on the live lane (Opus 5 `claude-opus-5`, 03-08-2026):** closes gaps **G5/G8/G9/G10** of the [H2025 pipeline audit](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_AUDIT_PWG_RU_H2025_01-08-2026.md). **G5 (S1-3):** `workflow_payload` dropped any result row that was not a dict or carried a falsy `key` via a bare `continue` — counted in **neither** `keys` nor `nulls`, so a **paid** card vanished from every accounting surface. Such rows are now materialised as failures under a synthetic key, in both lists, with the original row preserved as `malformed_row_raw` evidence; this is H2089's envelope/card hardening completed at row granularity. **G8 (F-1):** promotion checked `execution_route` for *is-a-non-blank-string* only, so a v2-**shaped** artifact from any other route (the retired Max-Workflow lane, a hand-built envelope) satisfied every contract check and could enter the canonical store — it is now compared against `execution_contract.HEADLESS_ROUTE`, the same constant the launch gate reads. **G10 (F-B4/B5/B7/B8):** `probe_log.verdict_for` and the CLI `--policy` both defaulted to `production_v1` while `CURRENT_POLICY` had advanced to v2 then v3 — quiet in the *safe* direction (v1's 30 000 ms is the strictest ceiling, so nothing was wrongly admitted) but every default-lane receipt named a retired gate and v3's route guard could never fire; `--api-ms` was added because `api_ms` was a `verdict_for` parameter with **no CLI path**. `state['translation_limit']` was serialized, defaulted and echoed in status while enforcement read the module constant (`preparation_limit` two frames down already honoured state) — now bound. `budgets.max_agents` was **read** by `headless_worker` and written by nobody; now written, with the honest note that it changes no behaviour because `max_agents == max_translate + max_heal` makes it an *implied* bound, never an independent one. **`classify_run` was worse than the audit recorded:** three of its inputs (`heal_calls`, `agents_spent`, `budget_kill_switch_tripped`) are absent from the headless summary, and since `heal_calls` sits in `TELEMETRY_FIELDS`, **every live window answered `unclassifiable`** — it never adjudicated a headless run at all. Fixed by normalising at read time so historical JS payloads stay classifiable under their original vocabulary. Boundary tests for the probe gate now **derive** from `POLICIES[CURRENT_POLICY]` rather than pinning a literal — the same latent trap re-found in `execution_contract_selftest`, whose 29999/30000 assertions were silently encoding the stale default. Per-knob adjudication of all nine declared budgets — including the correction that **four are read** (by requeue/preflight, not the executor), so the genuinely dead count is **three**, not nine: [BUDGET_HYGIENE_VERDICTS_PWG_RU_H2173_03-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/BUDGET_HYGIENE_VERDICTS_PWG_RU_H2173_03-08-2026.md). 5 new `window_selftest` pins (206/206), 9 sibling selftests green, LANG_PARITY 68 entries re-derived / 91 no drift. **No paid calls — fixtures only.**

### Changed
- **H2173 G9 — doc/skill truth pass on drifts D1-D6 (Opus 5 `claude-opus-5`, 03-08-2026):** [PIPELINE_ARCHITECTURE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md) **demoted to historical** on a human ruling (option 1 of three: banner + fix only the actively-misleading lines, no rewrite — it had already been re-bannered once on 02-07 and went stale within a week because it duplicates a fast-moving lane two other documents own). Three claims corrected in place rather than left for a reader who lands mid-document: the "current production architecture" section is the **retired** Max-Workflow route (D1); "Translation runner — **TODO (no runner yet)**" describes what is now the **money path**, `headless_worker.py` (D2); and there is **no per-card Opus judge loop** — acceptance is deterministic gates plus a *sampled* judge queue, on pinned `claude-sonnet-5` (D3). Skills: `/pwg-live-gate` had gone stale a **second** time — it named `production_v2`'s 65 000 ms after H2138 derived `production_v3` (80 000 ms wall **+ 45 000 ms route**), and still carried "do NOT gate on `duration_api_ms`" plus an "option C is future work" note for a guard that had already shipped; `/pwg-drain` asserted `deferred_monsters.jsonl` does **not** exist when [window_common.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_common.py) defines it and appends a deduped `pwg.deferred_monsters.v1` row per defer (D5); `/pwg-window-close` now names the **dual TM semantics** — the coordinator promote path rebuilds the TM automatically under the held claim, the manual `--glob` path does **not** (D6). The 02-08 **180 → 300 s** per-call relaxation was documented in `/pwg-live-gate` while `/pwg-drain` and `/pwg-bounded-run` still instructed `--timeout 180`, which re-pins the retired ceiling by hand — the exact defect behind a paid window that returned zero cards with 12 of 16 calls killed at 180 s ([#983](https://github.com/gasyoun/SanskritLexicography/issues/983)); all three now say 300. Stale literals in `h963_c4_gate0_probe.py` and `max_account_orchestrator.py` comments replaced with the derivation they annotate.

## [1.141.10] - 2026-08-03
### Fixed
- **H2233 override (Sonnet 5 `claude-sonnet-5`, 03-08-2026):** progress-kitchen `eta_verb()` (`progress_dashboard/kitchen_slices.py`) divided remaining DCS-attested verb roots by mean cards/active-day — an apples/oranges rate (roots numerator, cards denominator) that produced a nonsense ~0.8-day estimate for 701 remaining roots and an explicit in-code "units differ, not a schedule" caveat. Replaced with a same-unit rate: mean verb roots promoted per active day, derived from `pwg_ru_translated.jsonl` provenance timestamps of roots already in `verb_batch_worklist.json`'s `done_promoted` list. New fields `mean_roots_promoted_per_active_day` / `roots_promoted_active_days_sampled` / `estimated_days_at_roots_per_day_rate` replace the old cards-rate fields; `index.html`'s ETA strip updated to match. [PR #1085](https://github.com/gasyoun/SanskritLexicography/pull/1085). Dual-run residual for the intended Grok 4.5 executor: [H2258](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2258-Grok_SanskritLexicography_h2233-dual-run-compare_03.08.26.md).

### Added
- **Metadoc for the cache playbook + the contradiction now points at its registry row (Opus 5 1M `claude-opus-5[1m]`, 03-08-2026, H2189 propagation sweep):** [`RussianTranslation/PROMPT_CACHING_PWG_RU.meta.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.meta.md) — the playbook of record had none, so its provenance (a Grok 4.5 consolidation, extended by H2190 and H2189), its five-item improvement backlog and its limitations lived only in whoever last read it. The sharpest limitation is now written down: **every truth in §1 is a snapshot against a third-party binary**, which is exactly what truth #1 is living through — measured on CLI v1.127.0, contradicted two versions later. §1 truth #1 additionally links [Uprava CONTRADICTIONS §7](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md) and the re-measurement handoff [H2250](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2250-Opus_SanskritLexicography_pwg-cli-cache-amortisation-remeasure_03.08.26.md), so a reader of the playbook reaches the open question without knowing to look in the org hub.

## [1.141.2] - 2026-08-03
### Fixed
- **H2192 — `added_by_one` fired 0/12,000 because it and `omitted_by_one` are one undirected class (Opus 5 1M `claude-opus-5[1m]`, 03-08-2026):** the RV divergence taxonomy's two asymmetric labels are converse readings of the SAME configuration — material present on one side, absent on the other — the pair key is unordered, and the model reply shape was `{"class", "why"}` with **no direction field**. A model that correctly saw surplus material had no way to say which side, so every arm collapsed the event onto one name (H1844 pilot 0/12,000; H1901 arms 0/300, 0/300, 0/267). The sharpest evidence it was an oversight rather than a design: the *deterministic* arm always emitted `missing_side` — direction was expressible in this format all along and was dropped in exactly the one arm that cannot recover it otherwise. Fixed by making `surplus_side` mandatory on both asymmetric classes (resolved against that pair's own two translators; bare surname accepted, anything else recorded as a gap rather than coerced), fixing the prompt's reading point at the first translator in the pair key, emitting `surplus_side` from the deterministic arm too, and sending **both** converse names to `omission` in `COARSE_MAP` — the K3 projection previously moved under a semantically vacuous relabelling. **Diagnosed with zero model calls and $0.00** via the new [`src/rv_added_by_one_diagnosis.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_added_by_one_diagnosis.py). Two measurements worth keeping: **283 of 283** model-decided `omitted_by_one` rows name a translator in the free-text `why`, so a deterministic backfill recovers the side for **235/286 (82.2 %)** with none unrecoverable (additive sidecar — the pilot is not mutated); and the coarse-map defect has cost **nothing yet** — recomputed on the three committed spike arms, κ is bit-identical under both maps (0.235 / 0.350 / 0.216), so H1901's published kappas need no caveat. **Correction to the record:** H1844 and H1901 both blamed Griffith's freely supplied material; measured, Griffith is the *least*-marked of the five witnesses (0.1 % of stanzas — his padding is italicised in print and carries no delimiter after extraction) while Elizarenkova parenthesises supplied words in 71.7 %. The verdict stands and gets stronger: **8,744** pilot pairs carry a marker on exactly one side. The 2,000-stanza pilot was **not** re-typed — the fix is to the instrument, not the data. 5 new pins, each verified RED on pre-fix master; `tests/test_rv_spine.py` **54/54**, `window_selftest` **201/201**, `lang_parity_check` 91 entries no drift. Report: [RV_ADDED_BY_ONE_INSTRUMENT_DEFECT_2026-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2192/RV_ADDED_BY_ONE_INSTRUMENT_DEFECT_2026-08.md).

## [1.141.1] - 2026-08-03
### Changed
- **H2230 override (Sonnet 5 `claude-sonnet-5`, 03-08-2026):** progress-kitchen `instrumentation_coverage()` (`progress_dashboard/kitchen_slices.py`) split its blended `wall_clock_coverage_pct`/`token_coverage_pct` into `post_cut` (rows stamped by the H1553/H2212 auto-derive path, keyed on presence of a `wall_clock_source` field) vs `historical` (pre-instrumentation rows, where a null was never recoverable) buckets, so the coverage card no longer conflates "legitimately unknown" with "should have it but missing". The dense-instrumentation requirement itself (`append_ledger` always stamping `wall_clock_minutes`/`max_total_tokens`) was already shipped in H2212, and the optional historical backfill script (`backfill_ledger_metrics.py`) already existed from H2218 R4 — H2230's only real remaining gap was this honesty split. `progress_dashboard/index.html` now renders the `post_cut`/`historical` split alongside the blended figure. Dual-run residual for the intended Grok 4.5 executor: [H2255](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2255-Grok_SanskritLexicography_h2230-grok-dual-run-compare_03.08.26.md).
## [1.140.0] - 2026-08-03
### Added
- **H2189 — the headless profile surface, measured: `--safe-mode` wins, a minimal `CLAUDE_CONFIG_DIR` loses (Opus 5 1M `claude-opus-5[1m]`, 03-08-2026):** the handoff proposed a dedicated minimal profile directory; measured against the CLI's own `--safe-mode` flag it came **fourth of four levers**. Cold-call cache `create`, five sequential arms, bare cwd, `claude-sonnet-5`: baseline **39 532** → minimal profile dir **36 092 (−8.7 %)** → ancestry-clean cwd **26 780 (−32 %)** → **`--safe-mode` 4 712 (−88 %)**. On the real production prompt (`nakzatra`, 24 770 chars, argv-for-argv as `HeadlessEngine.call` builds it): create **60 140 → 18 615 (−69 %)**, output **19 718 → 10 040 (−49 %)**, wall **254 s → 115 s (−55 %)**, cost **$0.6921 → $0.2712 (−61 %)** — and the baseline **timed out at `HARD_TIMEOUT_MS` (300 s)** on its first attempt, so the 254 s figure needed H2158's 600 s *diagnostic* ceiling; no production ceiling was raised. **The output halving is agent-loop overhead, not lost card**, checked rather than banked: 7 records / 13 senses on both arms, 13/13 senses carrying Russian, Russian volume +0.8 %, the `{Tn}` masked-span token **set identical**, zero `SAN-LOSS`/`UNMAPPED` — verified with the project's own single-sourced `promote_final_cards.TN_RE` and `canary_gate.LITERAL_MARKERS`, not a private heuristic. Wired **opt-in, default OFF** via manifest `execution.cli_safe_mode`, with a `--help` support probe that fails safe to the historical argv and warns loudly (an unsupported flag would die in argument parsing on *every* spawn, turning a cost optimisation into an outage). Default stays OFF because the quality case is n=1 per arm and one divergence is unattributed — the free-text `tag` vocabulary differed between the two samples; flipping it needs a canary GO on the safe-mode arm. **`--bare` was deliberately not adopted:** it forces `ANTHROPIC_API_KEY` auth, moving this lane off the subscription identity — a human ruling, not a cache tweak (pinned by a selftest that refuses to let it become an arm). Four new pins in `headless_worker_selftest.py`, 12 in the new offline `h2189_profile_ab_selftest.py`; LANG_PARITY **SHARED**, 5 entries re-derived and re-stamped, 91 entries no drift. Spend: **$1.7551** over 12 cost-evaluable calls plus one unevaluable timeout. Report: [PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md).

### Fixed
- **H2189 §1.1 — `bare_cli_cwd()` has been leaking ~33 KB of operator memory into every paid call since H2158 (Opus 5 1M `claude-opus-5[1m]`, 03-08-2026):** found offline, for free, before a single paid call. The helper walks up rejecting an ancestor that carries a bare `CLAUDE.md` or a `.git` — but **not** one carrying `.claude\CLAUDE.md` — and its directory is `%TEMP%\pwg_ru_cli_cwd`, i.e. *under the Windows user profile*, which is exactly where the operator's global memory lives. Measured: **32 779 B** (`C:\Users\user\.claude\CLAUDE.md` 31 625 B + `.claude\rules` 1 154 B) reaching every spawn, invisible because the directory itself is empty. This also relocates the H2158 instruction-override diagnosis: the paid profile has **no `CLAUDE.md` of its own**, and the two A/B arms that kept the profile's 63 hooks could not answer a five-token prompt within one turn (`error_max_turns`) while every hook-free arm answered in one — so the override arrives through **hooks**, not through a profile memory file. Reported and pinned as a measurement (`test_bare_cwd_ancestry_is_reported_even_though_it_is_not_yet_clean`) rather than asserted away, since a test demanding clean ancestry would fail on the very box this ships to; new diagnostic `python src/pilot/h2189_min_profile.py --scan-cwd <dir>`. `--safe-mode` masks it by disabling memory discovery outright; **any lane not using that flag still pays it**, so the helper itself remains an open defect.

### Changed
- **H2189 — a contradiction logged against a standing truth, not a silent correction (Opus 5 1M `claude-opus-5[1m]`, 03-08-2026):** [PROMPT_CACHING_PWG_RU](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md) §1 truth #1 and the [RUN_FREQ_MAX](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) twin both state a one-shot CLI subprocess **cannot** amortise its own system prompt (v1.127.0: two identical back-to-back calls each re-created ~49 k). In **all five** H2189 arms the opposite happened — call #2 created **zero** and its `read` equalled call #1's `create + read` *exactly* (`paid` 68 414 · `minimal` 64 974 · `safe` 33 594 · `clean_cwd` 55 662 · `safe_clean` 33 586) — at the same seconds-apart cadence and the same 1 h TTL bucket, which reads as a CLI behaviour change rather than a methodology difference. Both documents now carry the contradiction inline. The truth is **left standing**: this run was not designed to test amortisation, and truth #1 underpins the whole rank-2 Messages-API case, so it earns a dedicated re-measurement rather than a drive-by rewrite.

## [1.138.1] - 2026-08-03
### Fixed
- **H2116 dual-run compare — independent re-verify of PR #964's offline pwg_ru batch (Sonnet 5 `claude-sonnet-5`, 03-08-2026):** residual for the H2005/gloss_lang-§464/glyph-quarantine override lane Grok 4.5 executed in [#964](https://github.com/gasyoun/SanskritLexicography/pull/964). All 5 deliverables independently re-verified against source + selftests and classified identical/equivalent/conflicting/net-new: `build_article_site._ls_visible_display` (H2005 RU `ed. Bomb.` display) + its selftest — **equivalent** (7/7 pass, resolver/store correctly isolated from RU display). `pwg_mask.looks_english_content` strong/weak split (§464 FP fix) — **equivalent**, plus a **net-new** full-corpus re-measurement (192,763 spans vs. §464's original 15,901) that PR #964 never ran — 0% German-looking false positives post-fix on both spans FINDINGS §464 named by example, closing the "needs its own measured A/B" gap §464 explicitly deferred. Glyph quarantine sample script/report — **conflicting (minor)**: fixed a literal `%%` in the report template that rendered `93%%` instead of `93%`. A2/A6 already-shipped verify memo — **conflicting (minor)**: fixed a mis-citation crediting the O(n²) residual-ledger fix to H1811 (it is actually H1940, commit `a75eaa17`). No deliverable required re-implementation. Memo: [H2116_DUAL_RUN_COMPARE_2026-08-03.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H2116_DUAL_RUN_COMPARE_2026-08-03.md) · [PR #1068](https://github.com/gasyoun/SanskritLexicography/pull/1068).

## [1.137.13] - 2026-08-03

### Changed
- **H2138 (#946) — the probe ceiling, derived at last: `production_v3`, and the number was never the bug (Opus 5 1M `claude-opus-5[1m]`, 03-08-2026):** the single-number *shape* was. `wall = duration_api_ms + api_gap_ms`, and the two move independently — measured api/wall **0.25…0.72** — so no fixed factor converts one into the other and a threshold on the *sum* cannot express route health. The 02-08 12:46 reading is the proof: `duration_api_ms` **16 445 ms**, the fastest API reading ever recorded on c4, **NO-GO at 65 000** on 49 846 ms of in-CLI scaffolding — a healthy route refused a window. At 65 000 the gate passed **2/8** with its median ~12 s *above* the ceiling: a ~25 % lottery at ~$1.09 a pull. So [`probe_log.POLICIES`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py) gains **`production_v3`** — `latency_ceil_ms` **80 000** *plus a new second, independent* **`api_ceil_ms` 45 000** — with `CURRENT_POLICY` repointed; `production_v1`/`v2` stay frozen, since rows stamped with them were genuinely judged at those ceilings. **ZERO paid calls:** derived offline from the 8-reading measured series (5 decomposable) that H2011/H2152/H2158/H2174 already bought, reproducible via the new [`h2138_ceiling_derive.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2138_ceiling_derive.py). **Derivation:** route = round_up(healthy-cluster max 29 069 × 1.5) = 45 000, the cluster `16 445 · 26 386 · 27 557 · 29 069` separating from the degraded `69 137` at a 2.38× multiplicative gap; wall = round_up(29 069 + largest observed scaffolding 49 846) = 80 000, the worst *legitimate* call — from components, not fitted to make a run pass. Pass rate 2/8 → 5/8. **Not a weakened guard:** every v2 rejection for genuine route degradation still fails, and v3 adds a condition v2 never had; what stops being rejected is the healthy-route/slow-scaffolding class a wall number is structurally unable to identify. Wired into [`h963_c4_gate0_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py)'s `derive_fails` — the **live gate path**, since `verdict_for` alone would have left it dead code — with 4 selftest pins (wall-ok + route-degraded, absent instrumentation, warm-up advisory), and a hard-coded `65000` in its `#729` pin replaced by the derived value: exactly the staleness class H2118 exists to prevent. **Honest limits:** no same-moment quota check — H2138's specified probe was invalidated by its own 02-08 correction (a Claude Code OAuth token returns `429` *unconditionally* without the identifying system prompt) and reading the token was refused by the harness permission classifier for the **third** session running (H2118, H2152, this one); what stands in its place is that every reading returned a full envelope, whereas the [§270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) throttle signature is a silent hang. The route guard changes no historical verdict, so it is a **forward** guard. n=5 decomposable, one account, three days. **This does not open a window** — the gate population (43–168 s) and the production population (~359 s wall, 99.3 % of it API) are disjoint, and the binding constraint remains output tokens. `window_selftest` **201/201** · orchestrator + contract **PASS** · LANG_PARITY 91 entries no drift. Memo: [H2138_PROBE_CEILING_DERIVATION_2026-08-03.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2138/H2138_PROBE_CEILING_DERIVATION_2026-08-03.md) · table in [RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md) · [PR #1061](https://github.com/gasyoun/SanskritLexicography/pull/1061).

### Added
- **H1956 — wire `sibling_root.py --selftest` into CI (Sonnet 5 `claude-sonnet-5`, 03-08-2026):** the H1902 worktree-safe root resolver ([FINDINGS §503](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#503-a-git-worktree-silently-disables-every-sibling-repo-lookup-in-src--artifacts-rebuilt-there-lose-layers-without-failing), merged via [#892](https://github.com/gasyoun/SanskritLexicography/pull/892)) shipped without a CI regression guard for its own selftest — the RussianTranslation gates job now runs `python src/sibling_root.py --selftest` alongside the other capability-card selftests.

## [1.137.11] - 2026-08-03

### Added
- **H2044 — the fifth c4 measured reading of 02-08 is a GO on all three numbers, and the canary is exposed as the unbuildable half of G46 (Opus 5 1M `claude-opus-5[1m]`, 02-08-2026):** the [G46](https://github.com/gasyoun/Uprava/blob/main/GOALS_MANUAL.md) reprobe fired **one** health run (2 paid calls, **$0.7232244**) and stopped at `HEALTH_GO_CANARY_UNSPENT`. Measured **60 845 ms** wall vs the 65 000 ms ceiling, CLI `duration_ms` 40 623, `duration_api_ms` 36 508 — **all three candidate gate numbers pass**, the exact mirror of the 11:06 reading where all three failed (96 520 / 77 966 / 69 137). Sequence for the day: **PASS → NO-GO → NO-GO → NO-GO → PASS** (43 815 → 75 561 → 96 520 → 66 291 → 60 845 ms wall), i.e. **2/5**, consistent with H2174's second-pass finding that the ceiling's implied pass rate is ~25 % and the route is bimodal on a timescale of hours. Operationally: a GO authorizes a window of **minutes**, not a day, and the ceiling-value question stays [H2138](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2138-Opus_RussianTranslation_probe-ceiling-paired-readings-946_01.08.26.md)'s. **The third paid call was deliberately left unspent.** `/pwg-live-gate` Step 2 needs a manifest v2 for `dq_canary_puregloss~~h0_zz_pw`, and `git log --all --diff-filter=A` finds **no canary manifest and no builder anywhere in the history** — only [H1447's wf_output](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1447/h1447_canary_wf_output.json), the result rather than the input; both H1447's packet and [RUN_FREQ_MAX §A2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) mark the command shape "illustrative". Hand-authoring one on the money contour from a v1 `nominal_masked` template would risk spending the cap's last call on a tooling error — so the health leg is the cheap half of G46 and **the canary is the blocked half**, which since H2159 blocks every paid window. Offline floor green in the same pass: `window_selftest` **200/200**, probe `--selftest` **7/7**, `lang_parity_check` **90 entries no drift**, launch ledger **19 complete**. Packet: [H2044_C4_HEALTH_GO_CANARY_UNSPENT_2026-08-02.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2044/H2044_C4_HEALTH_GO_CANARY_UNSPENT_2026-08-02.md) · trend table in [RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

## [1.137.10] - 2026-08-03
### Added
- **OPT-8 kitchen lease-collision banner (H2229, Grok 4.5 `grok-4.5`, 02-08-2026):** store-hit / occupied-keys / nominal lease collision aborts now append typed `dashboard_events` rows and surface as a red **DO NOT START A SECOND PAID WINDOW** banner on the public kitchen (`collision_guard` on `pwg.kitchen.v2`). Display-only — no spend-path change. Fixture + `python progress_dashboard/kitchen_collision_selftest.py`. Inventory residual closed on OPT-8. [PR #1054](https://github.com/gasyoun/SanskritLexicography/pull/1054).

## [1.137.9] - 2026-08-03
### Fixed
- **OPT-4 H1209/H1210 JS field + controller prompt parameterize (H2226, Grok 4.5 `grok-4.5`, 02-08-2026):** `wf_template.js`, `wf_template_ab.js`, `control_template.js` take `TARGET_FIELD` + `CONTROLLER_PROMPT` from the payload (`prep_slice` / `arm_b_control`); no second EN scaffold. `js_field_param_selftest` + `det_gate` EN path; RU 3-card canary fixture still clean. LANG_PARITY `h1209_controller_worker_rig` + `h1210_ab_arm_scaffold` → SHARED.

## [1.137.8] - 2026-08-03
### Fixed
- **OPT-6 citation coverage single source of truth (H2225, Grok 4.5 `grok-4.5`, 02-08-2026):** `build_citation_index.py` extracts pure `coverage_key` + `coverage_bucket` + shared kernel so `CITATION_SOURCES` / `UNCOVERED_SOURCES` cannot disagree on covered vs truly-uncovered vs non-coordinate labels. Labels no longer inflate distinct-ref `unresolved`. `python src/build_citation_index.py --selftest` green. [PR #1049](https://github.com/gasyoun/SanskritLexicography/pull/1049).

## [1.137.7] - 2026-08-03
### Fixed
- **OPT-1 EN promote parity (H2224, Grok 4.5 `grok-4.5`, 02-08-2026):** `promote_en.py` gains B08 better-attempt-wins, B20 model-identity cross-check, and H1553 defect-key refuse (+ optional ready_partial filter); helpers single-sourced from `promote_final_cards` (EN stays attach-overlay). LANG_PARITY `h1339_en_promote_parity_gap` + `h1553_wall_clock_defect_ready_partial` → SHARED. [PR #1047](https://github.com/gasyoun/SanskritLexicography/pull/1047).
- **Master CI red: LANG_PARITY re-affirm for H2212 window_reports.py drift (H2210, Grok 4.5 grok-4.5, 02-08-2026):** five ledger hashes re-stamped; SHARED/GAP verdicts stand. RussianTranslation gates unblocked.

## [1.137.6] - 2026-08-02
### Added
- **PWG translation duplication → optimization inventory (H2222, Grok 4.5 `grok-4.5`, 02-08-2026):** durable map of intentional vs unjustified duplication so optimization hunts **code/logic twins** (EN promote GAP, audit_window fork, H1209 JS field, citation coverage SoT), not edition restates or style doublets. Doc: [`RussianTranslation/PWG_TRANSLATION_DUPLICATION_OPTIMIZATION_INVENTORY_2026-08.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_TRANSLATION_DUPLICATION_OPTIMIZATION_INVENTORY_2026-08.md). [PR #1043](https://github.com/gasyoun/SanskritLexicography/pull/1043).

## [1.137.5] - 2026-08-02
### Added
- **Progress kitchen residual B1+B9+B10 + historical metric backfill (H2218, Grok 4.5 `grok-4.5`, 02-08-2026):** optional subscription-window $ card from gitignored `economy_subscription.json` (never invent dollars); idle-gap **reason** classes (`human` · `weekly_cap` · `health_nogo` · `machine_off` · `waiting_requeue` · `unknown`) from operator log + measured auto-rules; store-vs-`article_site` root parity card; [`backfill_ledger_metrics.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/backfill_ledger_metrics.py) best-effort wall-clock/gen_model recovery with provenance flags. Additive keys on `pwg.kitchen.v2`. Examples under [`progress_dashboard/examples/`](https://github.com/gasyoun/SanskritLexicography/tree/master/progress_dashboard/examples).
- **Progress kitchen K1–K8 full implement (H2212, Grok 4.5 `grok-4.5`, 02-08-2026):** public `/progress/` gains operator strip (root/state/next_action), yield/requeue mix + top roots, three-way review bar (approved/needs_review/ai_translated), verb burn-down estimate, c4 health GO/NO-GO sparkline, instrumentation coverage, calendar idle overlay, cost sample-size badge, quality/gates panel. Builders: [`kitchen_slices.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/kitchen_slices.py) + [`build_kitchen_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_kitchen_data.py) schema `pwg.kitchen.v2`; audit path always stamps production_metrics keys ([`window_reports.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_reports.py)). Roadmap: [ROADMAP_PROGRESS_KITCHEN_IMPROVEMENTS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/ROADMAP_PROGRESS_KITCHEN_IMPROVEMENTS_2026.md).
- **FINDINGS §515 — WIL 1819 vs 1832 edition-basis split** (Grok 4.5 `grok-4.5`, 02-08-2026): PWG ← WIL 1819; MW72/MW English ← WIL 1832; CDSL OCR is 1832 only; full 1819 body out of scope; 1819 preface is the bounded next OCR unit; `L.`/`W.` kept distinct. Canonical: [WIL docs/WIL_EDITION_LINEAGE_1819_1832.md](https://github.com/sanskrit-lexicon/WIL/blob/main/docs/WIL_EDITION_LINEAGE_1819_1832.md).

## [1.137.4] - 2026-08-02

### Added
- **H2174 second pass — the c4 health ceiling is ~12 s BELOW the median measured reading (Opus 5 `claude-opus-5[1m]`, 02-08-2026):** gate attempt 4 returned NO-GO by **1 291 ms (2.0 %)** — not overridden. Across all 8 measured c4 readings the ceiling's implied pass rate is **2/8 (25 %)** and **median − ceiling = +11 988 ms**, so the gate is *expected* to fail ~75 % of the time and more attempts cannot fix it. The 12:46 reading is the tell: wall 66 291 ms but `duration_api_ms` **16 445 ms**, the fastest API reading ever recorded on c4, with 49 846 ms of in-CLI scaffolding — a healthy route failed on overhead. **The clock is settled and not reopened** (gate on wall, MG 02-08-2026 / H2160 option A); what was never fitted is the ceiling *value*, which belongs to [H2138](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2138-Opus_RussianTranslation_probe-ceiling-paired-readings-946_01.08.26.md) — not to H2174, and not to be fixed by raising a guard so one's own run passes. **H2138's requested dataset now exists at zero further cost:** 5 paired readings, api/wall **0.25 → 0.72** and `api_gap_ms` **17 429 → 49 846 ms**, disproving the standing "~45 % is scaffolding" constant in both directions. Distribution + quantile tables in [RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md). Probe run from the canonical checkout so rows land in the real per-account series ([#1034](https://github.com/gasyoun/SanskritLexicography/issues/1034)).

## [1.137.3] - 2026-08-02

### Fixed
- **PWG cost tools priced 1 h cache writes at the 5 m rate — a silent 1.6× under-report on every CLI call (H2190, Opus 5 `claude-opus-5`, 02-08-2026):** `PRICE['cache_write'] = 3.75` is the **five-minute** rate (1.25× base); every write the pwg_ru lane produces lands in `ephemeral_1h_input_tokens`, billed at 2× base = **$6.00/Mtok**. The memos quoted $6 in prose while anything **computed** used 3.75 — so the redundancy that should have caught the drift instead vouched for it. Repriced against the vendor's own `modelUsage.costUSD` on the two committed H2158 envelopes: **$0.753261 computed vs $0.857308 billed — a $0.104047 gap, 12.1 % of the true bill**, always cheap-side, feeding `--refuse-over-cost` gates and GO/NO-GO projections. [`parse_workflow_cost`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py) gains `cache_write_5m`/`cache_write_1h` **derived from** `PRICE['input']`, `cache_write_rate(ttl)` that raises rather than guessing, `split_cache_creation()`, and `usage_cost(usage, unknown_ttl=…)`; `tally()` splits per TTL and emits `cost` **and** `cost_unknown_at_1h`. Fallback is asymmetric by design: **reporting** keeps 5 m for TTL-less legacy envelopes (the $79.83 golden window and every pre-split figure unchanged), **cost gates** pass `unknown_ttl='1h'` and fail closed. Pinned by `h809_selftest.test_cache_write_is_ttl_priced_and_reconciles_with_the_vendor`, which also asserts the **old** arithmetic still fails to reconcile, so a revert cannot pass it. h809 4/4 · `window_selftest` 200/200 · economy_ledger OK. [PR #1032](https://github.com/gasyoun/SanskritLexicography/pull/1032) · [FINDINGS §289](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) · table in [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

### Changed
- **Progress kitchen idle + spend cards + equal lists (H2204, Grok 4.5 `grok-4.5`, 02-08-2026):** public `/progress/` kitchen now shows **last idle** beside current idle, **idle days by month** (UTC, open idle counted in the current month), absolute **total $ band** split into *clean dictionary* vs *prep/redo* (wasted clean=0 + requeue tokens), and keeps **Recent windows** / **Idle gaps** at the same length (12) with a click-to-expand full gap history. Builder: [`build_kitchen_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_kitchen_data.py); page: [`progress_dashboard/index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/index.html). Handoff: [H2204](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2204-Grok_SanskritLexicography_progress-kitchen-idle-spend-lists_02.08.26.md).

## [1.137.2] - 2026-08-02

### Added
- **H2174 — second consecutive c4 health NO-GO recorded; the presplit fix stays undemonstrated (Opus 5 `claude-opus-5[1m]`, 02-08-2026):** [H2174](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2174-Opus_RussianTranslation_medium50-presplit-live-run-after-health-pass_02.08.26.md)'s own `Fail =` clause ("a second health NO-GO") fired at Step 1, so no canary, no window and no store write followed — 2 paid probe calls, $1.0929. Measured 96 520 ms against the 65 000 ms ceiling. **New:** this is the first measured c4 row where `duration_api_ms` (69 137 ms) *also* breaches the ceiling — together with the CLI's own `duration_ms` (77 966 ms), **all three** candidate gate numbers fail, so the still-open "which number gates?" ruling would not have unblocked this window. The 21-row per-account series shows three measured attempts on 02-08 going PASS → NO-GO → NO-GO (43 815 → 96 520 ms wall, same profile/prompt/ceiling, 5¼ h apart): c4 is **bimodal on a timescale of hours**, not down. `api_gap_ms` is itself unstable (17 429 → 192 682 ms), so wall and api are not related by a fixed correction factor. Also verified offline: the five prepared `h1447-m50-w{1..5}` artifacts are still **10/48 keys presplit** (pre-fix), confirming regeneration is a genuine prerequisite. Trend + per-call tables in [RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md). H2174 stays open (its goal is unchanged and a mint of the residual was correctly refused by the semantic-collision guard as a duplicate of itself); what is newly owed is two *human* rulings, tabled in [GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) — which number gates, and what the retry policy is against a demonstrably bimodal route. Status on [SanskritLexicography#983](https://github.com/gasyoun/SanskritLexicography/issues/983).

## [1.136.1] - 2026-08-02

### Changed
- **PWG nonstop plan amendments R5.1/R5.2 (Fable 5 `claude-fable-5`, 02-08-2026):** Claude CLI profile fallback roster c4 -> c1 -> c5 -> c6; Wave-0 key @DO resolved without human input — DeepSeek key found live in `ORS-FAQ/.env`, OpenRouter key on Systema prod `.env` (via /ssh). [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md) decisions table + metadoc updated.

## [1.137.1] - 2026-08-02

### Added
- **H1909 NWS bare-citation vs. provenance-note discriminator (Sonnet 5 `claude-sonnet-5`, 02-08-2026):** `classify_general_bare_citation()` in [nws_ls_markup.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nws_ls_markup.py) — H1809 follow-on — tells genuine bare PWG citations apart from author/year provenance-note fragments across the 929-span NWS-layer `g5_card_render._BARE_CIT` sample (bracket-position + bare-year-locus signals, plus a single measured-false-positive siglum exclusion `'H'`; a blanket short-siglum rule was tried and rejected — see [FINDINGS §514](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) for why). Every accepted span validated via `pwg_sources` + `ls_resolver` before marking (0/195 measured false positives, full inspection). Applied to the canonical `pwg_ru_translated.jsonl` store: 110/11,603 rows changed, 195 `<ls>` wraps, byte-identical elsewhere, verified idempotent. [SanskritLexicography#1012](https://github.com/gasyoun/SanskritLexicography/pull/1012); report [pwg_ru/H1909_NWS_BARE_CITATION_DISCRIMINATOR_REPORT_2026-08-02.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1909_NWS_BARE_CITATION_DISCRIMINATOR_REPORT_2026-08-02.md).

## [1.136.0] - 2026-08-02

### Added
- **PWG→RU nonstop multilane plan (`/ask`, Fable 5 `claude-fable-5`, 02-08-2026):** 5-doc layered plan under [RussianTranslation/docs/](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md) — PLAN (16 interview rulings + autonomy contract) · ROADMAP (waves 0–4) · ARCHITECTURE (3 lanes: PC / samskrte.ru / Anthropic routines, `pwg-ru-data` private LFS data repo, build-vs-reuse table) · IMPLEMENTATION (15 ordered wave-1 steps) · VERIFICATION (acceptance criteria, pre-declared E1–E3 experiment verdict rules) + PLAN metadoc. Key rulings: subscription-only (never Claude API), auto-promote 1-week trial with 10% daily spot-check + freeze-lane halt rule, routines also translate via gated auto-merge PRs, DeepSeek/Grok lanes gated on pre-registered A/B wins. Execution: [H2175](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2175-Opus_RussianTranslation_pwg-nonstop-multilane-wave1_02.08.26.md) (Opus 5 `claude-opus-5`).
- **H2158 pwg_ru route A/B, Phase 1 (Opus 5 `claude-opus-5`, 02-08-2026):** `h2158_route_ab.py` (byte-identity-asserted two-arm harness, CLI-headless vs Messages API with an explicit 1h `cache_control` prefix), `h2158_route_ab_report.py`, `h2158_liveness_probe.py`; committed raw envelopes under `pwg_ru/h2158/`; report `ROUTE_AB_MESSAGES_API_VS_CLI_HEADLESS_02-08-2026.md`. **Measured:** a real card completes in **375 s** (never hung — 25 % past the 300 s ceiling) at **$0.8005**, of which **output tokens are 64 %** and cache-write only 34.6 % — so the Messages API port addresses the smaller half. API arm **not run** (no credential); verdict **INCONCLUSIVE**, interim NO-GO. Also: `PRICE['cache_write']` is the 5-minute rate, but this lane's writes are `ephemeral_1h` (2× base), understating CLI cost 1.6×; and bare-cwd strips *project* but not *profile* context — the profile `CLAUDE.md` overrode an explicit task instruction in a probe call.
- **H1650 h178/h180 rescreen (Grok 4.5 `grok-4.5`, 01-08-2026):** `sheet_screening.py` (citation_tm evidence panel + screening= block); h178 A2 skip of retired mqm/likert/pairwise on regen + `agent_pass` + compute labels agent-vs-human/agent-only; h180/g5 pass screening=; FINDINGS §512 N1 loop; `pwg_ru/SCREENING_H1650.md`.

### Added
- **ZALIZNYAK full a–f accent-mobility emission (H2103, Grok 4.5 `grok-4.5`, 01-08-2026):** `nominal_grammar._accent_scheme` now emits Whitney schemes `a`/`b`/`c`/`d`/`f` (plus `—` unmarked) from the 19-cell matrix in WhitneyRoots `accent_rules.json`, joined on `(T-code, accent_position)` + lexical exceptions. Regenerated `headword_index.tsv` / reverse index / paradigm stats (98,639 headwords; `—` 80,014 · `a` 9,885 · `b` 8,346 · `d` 349 · `c` 43 · `f` 2). Docs: [ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md). Gated on VedaWeb Phase 2 GO (H063/H115). Advisory only — never written into reviewed spine.

## [1.114.10] - 2026-08-01

### Changed
- **ROADMAP_VEDAWEB_REUSE Phase 2 closeout polish (H2099, Grok 4.5 `grok-4-1-thinking-0309-reasoning`, `/drain tier 1`):** hub checkbox was already ticked on master via [#951](https://github.com/gasyoun/SanskritLexicography/pull/951) after WhitneyRoots [PR #24](https://github.com/gasyoun/WhitneyRoots/pull/24)/[#29](https://github.com/gasyoun/WhitneyRoots/pull/29) (H063/H115). This pass rewrites the stale "Where we stand: PARTIAL" summary to **COMPLETE**, corrects the Phase 2 score line to **17/19 GO / 0 NO-GO**, marks H063 `🔴 EXECUTED`, and updates the metadoc backlog (ZALIZNYAK a–f emission **unblocked**).

## [1.114.9] - 2026-08-01

### Changed
- **RUSSIANTRANSLATION_DEEP_MANUAL residual re-verify (H2071, Grok 4.5 `grok-4.5`, 01-08-2026):** LAST_VERIFIED stamp + metadoc backlog row 1 closed — production steps remain headless/manifest-v2 only (Workflow forensics); no production-path rewrite required.

## [1.114.8] - 2026-07-31

### Changed

- **Dashboard logon-only policy** (31-07-2026, Grok 4.5 `grok-4.5`): kitchen/local ops stay **`InteractiveToken`** (run at logon). When Windows is off there is no translation on that box, so logged-off stored credentials are **not** an open `@DO`. Revisit only for multi-PC concurrent translation. Docs: [windows/README](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/windows/README.md), [progress_dashboard/README](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/README.md), [RU deep manual §2d](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md). Closes the residual filed as Uprava GTD PR #1574.

## [1.114.7] - 2026-07-31

### Changed

- **Dashboard autostart residual documented (human `@DO` for logged-off run)** (31-07-2026, Grok 4.5 `grok-4.5`, H2032 follow-up): [`progress_dashboard/windows/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/windows/README.md) now carries the honest residual inventory + the exact `schtasks /Change /RU … /RP *` commands for “run whether logged on or not”; §2d of the [RU deep manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md), [progress_dashboard/README](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/README.md), [MAINTAINER_MANUAL](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md), and both HTML dual-surface banners link that residual and name the Task Scheduler task titles.

## [1.114.6] - 2026-07-31

### Added

- **Task Scheduler autostart for both PWG→RU dashboards** (31-07-2026, Grok 4.5 `grok-4.5`, H2032 follow-up): no manual start required after logon. New [`progress_dashboard/windows/`](https://github.com/gasyoun/SanskritLexicography/tree/master/progress_dashboard/windows) — `run_dashboard_server.cmd` (single-instance on :8765), `run_live_refresh.cmd` (`live_refresh.py --idle-stop 0`), and `register_tasks.ps1` which creates **`SL progress dashboard server`** + **`SL progress live refresh`** (logon trigger, StartWhenAvailable, RestartOnFailure every 1 min × 999, InteractiveToken, same shape as `SL findings dashboard refresh` / H737). Register once: `powershell -ExecutionPolicy Bypass -File progress_dashboard\windows\register_tasks.ps1 -StartNow`. Docs: windows/README + progress_dashboard/README + RU deep manual §2d.

## [1.114.5] - 2026-07-31

### Fixed

- **ROOT CAUSE of the c4 gate stall — the account is RATE-LIMITED, and the "≈65 s is CLI startup" conclusion is RETRACTED** (31-07-2026, Opus 5 `claude-opus-5[1m]`, [H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md)): an authenticated request issued **outside** the CLI with the profile's own OAuth token returns **HTTP 400 in 892 ms** on an invalid body (proving token, scopes, tunnel and authenticated path all healthy) and **HTTP 429 `rate_limit_error` in 754–1 103 ms** on a real 1-token completion (tier `default_claude_max_20x`). The API refuses in under a second; the CLI evidently retries with backoff instead of surfacing it, so `claude -p` *appears* to hang for 120–300 s. This **withdraws** the sixth reading's inference that ~65 s of a call is process startup — `--version` returns in 1 071 ms, `auth status` in 1 106 ms, an authenticated call in <1.1 s, so the wall-clock gap is retry delay, not launch cost. Consequences: the 78 415 ms "measured latency" is mostly backoff rather than model time; **the whole latency series is contaminated**, since any reading taken while rate-limited measured retry delay rather than route health, which puts the 15-07 / 16-07 / 31-07 figures in doubt as route evidence and means the 30 000 → 65 000 ms ceiling was calibrated partly against backoff; the intermittency (18:56Z worked, 15:03Z and 19:45Z did not) is explained by whether the retry loop lands in a window with capacity. Practical consequence for the campaign: probe with the authenticated one-liner (~1 s) instead of the 300 s representative call, do not raise the ceiling again, and re-examine the one-card-per-call lane, which maximises call count exactly when call count is the binding constraint. No rate-limit reset headers are exposed on the 429. Recorded in [`H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md) § "ROOT CAUSE"; generalised as [Uprava FINDINGS §269](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).

## [1.114.4] - 2026-07-31

### Fixed

- **h1306_style ratification sheet remade for vote** (31-07-2026, Grok 4.5 `grok-4.5`): the 21-07 Phase-1 local sheet was unstamped (no H1404 `content_hash`/lock), lacked `font_scale`, and had blanket `mark_cyrillic` on pure-Russian policy prose (464 yellow marks / 9 cards — unreadable). Zero votes cast, so supersession-by-remake is legal (H1655). New committed generator [`RussianTranslation/src/build_h1306_style_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h1306_style_sheet.py) re-emits the same A1–C3 cards from the research memo, on current emitter + binding; lock at [`RussianTranslation/review/locks/h1306_style.lock.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/h1306_style.lock.json) (`sha256:c760510d…`). Sibling `h1682_abbrev_rules` re-verified reproduce-stable against its #917 lock (`sha256:14403a33…`). HTML remains gitignored under `review/`; regen from `RussianTranslation/`.

## [1.114.3] - 2026-07-31

### Fixed

- **Local ops URL on the public kitchen is a real link** (31-07-2026, Grok 4.5 `grok-4.5`, H2032 follow-up, [#930](https://github.com/gasyoun/SanskritLexicography/pull/930)/[#931](https://github.com/gasyoun/SanskritLexicography/pull/931)): `/progress/` dual-surface callout had rendered `127.0.0.1:8765` as monospace text (`<span>`), so it looked linked but was not clickable. All three sites (callout, table, footer) now use `href="http://127.0.0.1:8765/"` (opens the *viewer's* localhost when `dashboard_server.py` is running). `.ai_state.md` updated with H2032 Completed + operator Next Step.

## [1.114.2] - 2026-07-31

### Changed

- **Documented and interlinked the dual PWG→RU dashboards** (31-07-2026, Grok 4.5 `grok-4.5`, H2032 follow-up): **local ops = 5 s** (`dashboard_server.py` → `127.0.0.1:8765`) vs **web kitchen = 60 s** ([`/progress/`](https://gasyoun.github.io/SanskritLexicography/progress/) + `live_refresh.py`). Both HTML UIs now carry a dual-surface callout with cross-links; [`progress_dashboard/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/README.md) opens with the comparison table; operator depth is [RUSSIANTRANSLATION_DEEP_MANUAL.md §2d](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md); orientation rows in [MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md) + root [README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/README.md); `dashboard_server.py` module docstring matches.

## [1.114.1] - 2026-07-31

### Added

- **Sixth c4 gate-0 reading — and the decomposition showing ~65 s of a headless call is CLI startup, not the route** (31-07-2026, Opus 5 `claude-opus-5[1m]`, [H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md)): after the host-wide stall cleared, a fresh representative reading came back **warm-up 94 606 ms / measured 78 415 ms, both `success`** — a real c4 latency NO-GO at 1.21× the 65 000 ms ceiling, and the session's second consecutive NO-GO (H2011's stop condition). The recovery ping's own result envelope splits the wall clock: **70 987 ms total vs `duration_api_ms` 4 028 ms**, i.e. ≈65 s spent outside the API call. Under this host's load the ceiling is therefore consumed by process launch before a token moves, so c4 cannot pass regardless of route health — which promotes the abandoned-`claude`-process cleanup from housekeeping to the actual blocker. Explicitly **not** a reason to raise the ceiling again: the fix is to reduce startup cost or gate on `duration_api_ms`, which the envelope already carries. Economics captured per H2011's instrument-everything mandate: 2 calls, **$0.5848** (~$0.29/call), 4 input / 1 507 output tokens, 64 237 cache-read and **90 485 cache-creation** tokens — a ~90 k-token fixed scaffolding overhead per call that the one-card-per-call window will pay once per card. Reading taken from the main tree on purpose, so the two rows join the surviving 11-row series instead of dying in a worktree. Recorded in [`H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md).

## [1.114.0] - 2026-07-31

### Added

- **PWG→RU progress kitchen + minute-level live refresh** (31-07-2026, Grok 4.5 `grok-4.5`, [H2032](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2032-Grok_SanskritLexicography_progress-kitchen-live-refresh_31.07.26.md)): public `/progress/` now shows the **kitchen** behind the article site — speed (cards/hour & /24h, mean min/window), cost (tokens/window + economy-ledger agents/$ band per clean card), idle gaps (stage_boundary audit_end→start), campaign calendar heatmap, and a web changelog feed from `RussianTranslation/CHANGELOG.md`. New builders [`build_kitchen_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/build_kitchen_data.py) + [`live_refresh.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/live_refresh.py) rebuild from local store/ledger and push **only** `gh-pages/progress/` every 60s while translation artifacts are moving (no master spam). The page re-fetches JSON every minute with `cache: 'no-store'` and surfaces a stale/idle/on chip. Closes the standing caveat that a rendered dashboard is not automatically current.

## [1.113.1] - 2026-07-31

### Added

- **Fifth dated c4 gate-0 reading — a NO-GO that is *not* a c4 health signal** (31-07-2026, Opus 5 `claude-opus-5[1m]`, [H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md)): `/pwg-live-gate` Step 1 returned `gate_reason = HEALTH_NOGO` on a warm-up **timeout** (300 544 ms, 0 output bytes, reservation finalised `UNEVALUABLE`), so no canary and no bounded window ran. A 15-row diagnostic ladder of deliberately non-representative tiny calls then classified it: every `-p` invocation hung — bare `-p` as well as the full probe argv, the native `bin/claude.exe` as well as the Node shim, a **second config directory** as well as c4, and a **main tree trusted for months** as well as the minutes-old worktree — while `--version` returned rc 0 and a same-minute probe completed a TLS 1.3 handshake to `api.anthropic.com` in 748 ms. So the fault is neither c4-specific, nor flag-specific, nor the Windows shim, nor cwd/trust, nor raw connectivity: the reading says nothing about c4, and the four earlier latency readings stand unrevised. Census taken during the stall: **21 live `claude` processes**, oldest six days old, several at 4 000–6 850 CPU-seconds — self-contention is the probable cause and is a campaign-level throughput variable, not housekeeping. Recorded in [`H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md) with the raw event row copied in, because each run's events log lives in its own gitignored worktree path and dies with the worktree.

## [1.113.0] - 2026-07-31
### Added

- **Counting-conventions methods report shipped (H1871)** (31-07-2026): [METHODS_HOW_WE_COUNT_A_TRADITION_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/METHODS_HOW_WE_COUNT_A_TRADITION_2026.md) — the WS4.1 deliverable of the statistics roadmap. Defines every counting convention in use (dictionaries, headwords key1/key2, union, summed census, entries/records, lemmas, kosha.db rows, senses, `<ls>` citations, DCS denominators, tokens, correction events), each with artifact + exact reproduction query; reconciles 16 groups of divergent published figures; logs the four unreconcilable pairs as [CONTRADICTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) §10–§13 instead of picking. New surfaced caveats: the 828,505-citation graph is 64.7 % PWG with MW at 5 placeholder nodes; "210 correctors" is superseded (208); the bare "180,176 DCS lemmas" roadmap figure is unciteable until provenanced. Cites, does not restate, the [C7 drift registry](https://github.com/gasyoun/Uprava/blob/main/CANONICAL_FIGURES_CROSS_PAPER_DRIFT_C7.md). Fable 5 (`claude-fable-5`).

## [1.112.1] - 2026-07-31
### Changed

- **c4 live-gate latency ceiling raised twice, gate now PASSES** (31-07-2026, [#921](https://github.com/gasyoun/SanskritLexicography/pull/921), [#922](https://github.com/gasyoun/SanskritLexicography/pull/922), [#923](https://github.com/gasyoun/SanskritLexicography/pull/923)): gate-0's third dated `/pwg-live-gate` reading came back NO-GO (5.4% near-miss on the original 30,000 ms ceiling). MG ruling raised the ceiling 30,000→33,000 ms and made warm-up advisory rather than a NO-GO input, then raised both ceilings again to 65,000 ms — the gate now PASSES.
- **pwg_ru `h1682_abbrev_rules` sheet lock re-bound to a fresh generation** (31-07-2026, [#917](https://github.com/gasyoun/SanskritLexicography/pull/917)): deliberate `REVIEW_LOCK_FORCE=1` re-cut for the MG vote — the committed 26-07 generation (#802) could not be reproduced locally (gitignored HTML absent, inputs since drifted).

### Fixed

- **Zenodo concept DOI recorded; "not wired" claim corrected** (31-07-2026, [#916](https://github.com/gasyoun/SanskritLexicography/pull/916) closes #915, plus [#920](https://github.com/gasyoun/SanskritLexicography/pull/920) pinning `.zenodo.json`): the Zenodo-GitHub integration is live for this repo and has been minting DOIs — a prior note claiming otherwise was wrong. `.zenodo.json` added to pin deposit metadata that Zenodo's inference was already producing correctly.

## [1.112.0] — 2026-07-31

### Added
- **PWG-RU Russian style guide of record** (31-07-2026, Fable 5 `claude-fable-5`, [H1859](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1859-Fable_SanskritLexicography_pwg-ru-russian-style-guide-of-record_29.07.26.md)). [`RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md) (+ sibling metadoc) consolidates every ratified pwg_ru Russian style rule — R1–R4 mechanical orthography/terseness (H1305), German-residue rules (H1302), abbreviation architecture + the 19-07 vote principles (H1303 stream), doublet/`v. l.`/Comp.-formula status (H1306), `{%…%}` gloss-boundary conventions previously report/code-only (H1651/H1702), `<ls>` store-immutability, H858 field-integrity consequences, D2 machine-preview labelling — each rule citing the vote/handoff/PR that ruled it; append-only ledger governance. Honest-status finding baked in: neither `h1303_abbrev.decisions.json` nor `h1306_style.decisions.json` exists on disk (31-07-2026), so the per-token abbreviation list and the A1/B1/C1 recommendations are recorded as awaiting-vote proposals, and the open 10-07 vs 19-07 abbreviation contradiction ([CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) §4) is surfaced, not silently harmonised. Pointers added from [`pwg_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) §9b, [`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md), [`RU_STYLE_MECHANICAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md), [`STYLE_RESEARCH_DOUBLETS_VL_COMP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md).

## [1.111.5] — 2026-07-31

### Fixed
- **pwg_ru offline-pipeline hardening backlog closed — H1940 Phase 2 in full** (30/31-07-2026; H9/H2a/H8/H1/H7/H4/H3 + the O(n²) ledger item by Opus 5 `claude-opus-5[1m]`, H2b by OpenAI GPT-5.6 Sol `openrouter/openai/gpt-5.6-sol`; [H1940](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1940-Opus_RussianTranslation_pwg-ru-h1811-integrate-verify_30.07.26.md)). Eight surgical concurrency/durability fixes in the live orchestration path, each with a selftest pin verified RED against pre-fix master: a transient cohort probe failure could strand leases forever and silently ([#899](https://github.com/gasyoun/SanskritLexicography/pull/899)); a heal-budget stop was filed as a content defect on presplit cards ([#900](https://github.com/gasyoun/SanskritLexicography/pull/900)); one hung preflight could wedge every coordinator operation ([#903](https://github.com/gasyoun/SanskritLexicography/pull/903)); a malformed manifest crashed the worker with no status file while the orchestrator burned retries on it ([#904](https://github.com/gasyoun/SanskritLexicography/pull/904)); a translate-budget retry erased the card's real content diagnosis ([#906](https://github.com/gasyoun/SanskritLexicography/pull/906)); a stalled window hot-spun through its whole 1000-iteration ceiling instead of stopping ([#910](https://github.com/gasyoun/SanskritLexicography/pull/910)); and finally `claim` accepting a duplicate `--lease-id`, the three checkpoint/status writers never flushing to disk, and the residual ledger re-reading itself once per key ([#911](https://github.com/gasyoun/SanskritLexicography/pull/911)). Full per-item detail in [`RussianTranslation/CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md) and the [H1811 fixlog §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1811/H1811_PIPELINE_REVIEW_FIXLOG_2026-07-29.md). Gates held across the whole backlog: `window_selftest` 194/194, `lang_parity_check` 89 entries no drift, h1339 offline-bench per-lease outcomes and deterministic signature `9bd2a14297` byte-identical. `cohort_engine_selftest` is 10/10 green for the first time since [#761](https://github.com/gasyoun/SanskritLexicography/pull/761), a stale EVIDENCE baseline having been re-stamped rather than weakened. **Known residual, deliberately not fixed here:** `window_common.atomic_write_text` omits `newline=` from `os.fdopen`, so every file it writes is CRLF on Windows and LF in CI — correcting it migrates `manifest_sha256` and the preflight-evidence hashes, so it is recorded as [Uprava FINDINGS §262](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) rather than done as a drive-by.
- **NWS `[diasystem, domain]` tags still translated into Russian in 34 more places after H1809** (30-07-2026, [#901](https://github.com/gasyoun/SanskritLexicography/pull/901)).
- **The audit timeout could not cancel the audit, and provenance stamps could go stale** (H1957, 30-07-2026) — the H1811 S1/S3 optimisations reverted after review.

### Changed
- **Binary-samāsa ruling applied to the compound adjudicator** (H1918, 30-07-2026) and **offline pipeline speed + hermeticity: in-proc audit chain, stamp memo, `PWG_OUTPUT_DIR`** (H1811, 30-07-2026).

## [1.111.4] — 2026-07-30

### Changed
- **ACC×NCC P2 blind spot-check re-drawn larger so a 0.95 Wilson bar is attainable** (30-07-2026, Grok 4.5 `grok-4.5`, [H1951](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1951-Grok_SanskritLexicography_acc-ncc-p2-larger-sample_30.07.26.md)). MG vote 4c (H1948) chose re-draw over locking 0.85/0.90: at n=50 max Wilson LB is 0.929, so 0.95 promoted nothing by sample construction. New frame: **1,111 cards · 17 strata · n=73** per side (seed `19512026`; min n with perfect-agreement LB ≥ 0.95). Prior unvoted 698-card frame superseded. Sheet stamped + locked (H1404). Feasibility: on a perfect vote, bar 0.95 promotes **858/920** approve rows (62-row census stratum tops out at LB 0.942). No crosswalk rows promoted in this handoff — human votes the sample, then sets the bar. See [`P2_PRECISION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P2_PRECISION.md).
- **Binary-samāsa ruling applied to the compound adjudicator** (30-07-2026, Sonnet 5 `claude-sonnet-5`, [H1918](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1918-Sonnet_SanskritLexicography_compound-binary-samasa-rule-rerun_30.07.26.md)). MG's ruling: a samāsa's vigraha is always binary (dvandva excepted, and a dvandva is never detectable from arity alone). New `mw_recursive_decomposition` rule in [`RussianTranslation/src/pilot/adjudicate_compound_differs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/adjudicate_compound_differs.py): when PWG's own list is binary and MW lists more members that concatenate to the same string, the verdict is `pwg_members-right` — MW's extra granularity is the recursive decomposition of the first member (`goṣṭhīpati` = `goṣṭhī + pati`; MW's `go + ṣṭhī + pati` also decomposes `goṣṭhī` itself), not a rival split of the headword. The 11 rows where PWG itself gives >2 members (possible dvandva) stay out of scope, left for a human. `--selftest` green; `--write` regenerated [`RussianTranslation/research/pwg_compound_differs_adjudication.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_adjudication.tsv) — 28 rows now carry `mw_recursive_decomposition`, moving out of `unresolved`. [`RussianTranslation/src/pilot/build_compound_rule_ratification_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_compound_rule_ratification_sheet.py) re-cut with the rule's Russian gloss + claim added to its `RULES` book (8 rules, 30 cards); preflight gate stays green. Per-stratum Wilson bounds in [`RussianTranslation/research/pwg_compound_differs_promotion_plan.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_promotion_plan.json) were recomputed by the same `--write`, not carried forward from the old stratification.

## [1.111.3] — 2026-07-30

### Fixed
- **All 11 `RussianTranslation/src/` sibling-root guesses now share one resolver, and a missing table under an explicit `CSL_SIBLING_ROOT` raises instead of silently degrading** (30-07-2026, Sonnet 5 `claude-sonnet-5`, [H1902](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1902-Sonnet_SanskritLexicography_sibling-root-worktree-hardening_29.07.26.md)). H1847 fixed the env-override half in two modules (`pwg_ab.py`, `pwg_sources.py`); the other nine (`ls_coverage.py`, `citation_tm.py`, `corpus_gate.py`, `annotate_genres.py`, `build_mbh_concordance.py`, `part_b_xref_discovery.py`, `rv_griffith_extract.py`, `rv_renou_citations.py`, `rv_spine_build.py`) each still hardcoded `os.path.join(HERE, '..', '..', '..')`, true only in the canonical checkout — a `git worktree` (which the org's shared-tree rule requires for this repo) lands the checkout somewhere that guess misses, and every optional sibling table then silently "disappears" without failing the build (measured: a pinned G5 sheet re-issue shipped 0 `<ab>` spans instead of 253). New [`RussianTranslation/src/sibling_root.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sibling_root.py) is the one canonical resolver — `$CSL_SIBLING_ROOT` override, then upward marker-directory auto-detection (works with no env var at all), then the historical guess as a last resort — and all 11 modules now call it; `rv_org_root.find_github_root` (used by two of them) is now a thin compatibility wrapper delegating to the same helper, keeping `$GITHUB_ROOT` as a legacy alias. `require_sibling()` upgrades a missing-table degrade to a `FileNotFoundError` specifically when `CSL_SIBLING_ROOT` was explicitly set (an operator assertion the siblings exist), applied to `pwg_ab.table()`, `pwg_sources.bib()`, and `part_b_xref_discovery.iter_records()`; the unset/CI path is unchanged (warn-and-continue). Proven from inside a real worktree: `g5_card_render.py` and `build_g5_review_sheet.py --selftest` both report "pwgab table present · pwgbib bibliography present" with no env var set (auto-detection working), and `sibling_root.py --selftest` plus a scratch check on `pwg_ab.py` prove both `require_sibling` directions (unset → False, no raise; set-but-missing → raises). Closes [SanskritLexicography#875](https://github.com/gasyoun/SanskritLexicography/issues/875); FINDINGS §503 ticked resolved.

## [1.109.0] — 2026-07-29

### Fixed
- **Gate sheet v4 — two contrast bugs I introduced, and a 10-line header cut to one** (29-07-2026, Opus 5 `claude-opus-5[1m]`). MG could not read white text on the yellow highlight, nor the pale "В чём разница" text on its pale-blue panel. Both were the same defect: v2/v3 set a `background` on `mark.rv-hit`, `.rv-why`, `.rv-asym` and `.rv-chrono` and left the foreground to `inherit`, so each block took the theme's colour. Every coloured block now sets **both** background and an explicit dark `color`. The 10-line subtitle is reduced to one line (item count + the 80 % bar) with the full methodology — highlighting, chronology, sampling — moved to a `.rv-method` block at the **end** of the page.

## [1.107.0] — 2026-07-29

### Added
- **Chronology as a first-class dimension of the divergence gate, and the Jamison–Brereton gap stated out loud** (29-07-2026, Opus 5 `claude-opus-5[1m]`, [H1908](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1908-Opus_RussianTranslation_rv-gate-chronology-jamison-brereton_29.07.26.md)). MG: *"the chronology matters a lot and must be noted and used"*. The four translators run **Grassmann 1876–77 → Griffith 1896 → Geldner 1951–57 → Elizarenkova 1989–99**, and each later one could read the earlier — Griffith worked from Grassmann and Wilson, Elizarenkova argues explicitly with Geldner and Renou. So a divergence between a later and an earlier rendering is **not symmetric**: the later translator is often departing *knowingly*. ARCHITECTURE §3.5 defines the classes purely pairwise with no notion of precedence, so nothing in the taxonomy could express that. Sheet v3 now puts a **deterministic chronology band** on every card (computed from publication years, never asked of a model) and orders the two renderings **earliest-first** instead of by arbitrary pair-key order. Separately, the epistemic consequence of R4's rights decision is now stated rather than implied: Griffith 1896 is the layer's **only** English witness while the current standard is **Jamison–Brereton 2014**, deliberately excluded as in-copyright — so every English-side finding rests on a translation **118 years older** than the standard, and the 66 of 100 cards involving Griffith say so. Full reasoning and the three consequences for wave 2 in [`docs/DECISIONS_LOG_rv_multitranslation.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/DECISIONS_LOG_rv_multitranslation.md).

## [1.105.0] — 2026-07-29

### Fixed
- **The divergence gate sheet made a human re-derive what the model had already computed — v2 highlights the differing span and explains it in Russian** (29-07-2026, Opus 5 `claude-opus-5[1m]`, [H1906](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1906-Opus_RussianTranslation_rv-gate-sheet-v2-highlight-explain_29.07.26.md)). MG's verdict on v1: *«нужна подсветка и мотивация, я не буду 100 раз читать 4 перевода, выискивая глазами то, что ты уже и так пометил»* — and it was worse than a missing feature: the typer **already stored a `why` on every pair** (e.g. *"Grassmann has 'nehmet wahr' (perceive), Geldner 'versteht euch auf' (understand)"*) and the sheet discarded all 12,000 of them. New [`src/rv_divergence_explain.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_divergence_explain.py) re-queries only the 100 sheet items for a **verbatim** `span_a`/`span_b`, a Russian `why_ru`, and an `asymmetry_note` for pairs spanning a large era/quality gap (MG: comparing Griffith 1896 with a modern critical translation is not symmetric — 22 of 100 cards carry one). Spans are **verified as exact substrings, not trusted**: 20 of 100 came back non-verbatim and are quoted rather than force-highlighted, with the count stated in the sheet's own subtitle. v2 renders 109 highlight marks and 100 explanation blocks; sheet id `rv_divergence_gate_2026-07-29-v2`, freshly locked, same 100 item ids so no vote is lost. Cost $0.024.

## [1.104.0] — 2026-07-29

### Changed
- **Spike S2 answered on three model arms — the fine divergence classes are NOT separable, reversing the same-day H1844 ruling** (29-07-2026, Opus 5 `claude-opus-5[1m]`, [H1901](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1901-Opus_RussianTranslation_rv-divergence-s2-three-arm-kappa_29.07.26.md)). With an OpenRouter key supplied, the second and third arms ran on the same seeded 50-stanza sample: `deepseek-chat` ↔ `openai/gpt-4o-mini` ↔ `google/gemini-2.5-flash`. Cohen's κ for `lexical_variant` vs `semantic_shift` is **0.089 / −0.012 / 0.256** (mean ≈ 0.11, one below chance) — K3 fires. H1844 had declined to collapse the taxonomy on the grounds that the pilot *used* `lexical_variant` 6.0 % of the time; **usage rate is not separability**, and that provisional ruling (explicitly flagged NOT-YET pending this arm) is withdrawn. Collapsing to coarse only reaches κ 0.216–0.350 — "fair", not reliable — so the step-8 human gate becomes more load-bearing, not less; it still awaits a vote and the full run stays queued (R13). `added_by_one` fires **0 times in all three arms** (0/300, 0/300, 0/267), confirming it as a prompt/taxonomy defect rather than a fact about the Ṛgveda. Recorded caution: raw agreement on that subset reads 85.7–95.1 % and is worthless — under this base-rate skew percent-agreement measures the skew, not the agreement. Tables in [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md), reasoning in [`docs/DECISIONS_LOG_rv_multitranslation.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/DECISIONS_LOG_rv_multitranslation.md). Two new arms cost **$0.054**.

## [1.103.0] — 2026-07-29

### Changed
- **The blind A/B vote sheet redrawn on the 100-card data, and balanced across the §501 split** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1846](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1846-Opus_SanskritLexicography_h1210-arm-a-coverage-fill_29.07.26.md)): the previous sheet was drawn from arm A's 87-card audit, so its arm-A sample excluded the top length band entirely; it was never voted and is now marked superseded in its own lock. The new sheet [`h1210-ab-blind-100card-2026-07-29`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/h1210-ab-blind-100card-2026-07-29.lock.json) draws 20 per arm **half from `shippable` cards and half from `refused-but-audit-clean` ones** (arm A 10+10 of a 72/21 pool; arm B 12+8 of 70/8, taking all 8 it has and backfilling — reported, not silently rebalanced). Whether the refused half is publishable is the one question the machine cannot settle, and a uniform draw would have under-sampled it. Blinding verified on both axes: the HTML contains no arm token **and** no class or rig-status token; 40 unique ids, longest same-arm run 5, lock bound by content hash.

### Fixed
- **The sheet builder re-introduced the rig's own key-join trap** (29-07-2026, same handoff): `pick()` looked rig `final_status` up by the audit's `key1`, but the audit reports a third key form, so most lookups missed and the misses defaulted into `refused` — the split read **38/55 instead of the true 72/21**. Caught by comparing against [`status_vs_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/status_vs_audit.py) before the sheet was published. Both audits are now resolved through `ab_report.audit_index` — the one place that knows all three key forms and hard-errors on an unresolvable row instead of dropping it.

## [1.102.0] — 2026-07-29

### Added
- **NWS tag vocabulary reaches the reviewer: an in-card legend and a faceted browse** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1847](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1847-Opus_SanskritLexicography_nws-tag-vocabulary-facets_29.07.26.md)): the H1808 tooltips answered «что такое `[Gen, unsp]`» only for a reviewer who thinks to hover, one tag at a time, and not at all in print. Every G5 card carrying NWS tags now gets a fourth panel spelling them out — each tag glossed, with its share of the whole NWS corpus beside it — and the sheet gets a facet bar above the cards: multi-select within a slot (OR), intersected across slots (AND), so «Vedic senses standing at the end of a compound» is one click each. The census aggregate ships as counts-only JSON ([`pwg_ru/NWS_TAG_VOCABULARY_CENSUS_2026-07.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/NWS_TAG_VOCABULARY_CENSUS_2026-07.json), 37 kB, no dictionary text) so the shares survive in a clone without the gitignored 168k-card corpus. The facet machinery is shared, not local — [csl-pyutil#12](https://github.com/sanskrit-lexicon/csl-pyutil/pull/12), v0.7.0, which the CI pin now tracks. Sheet re-issued with `--pin-ids`, 150/150 card digests byte-identical, so votes already cast still bind.
- **FINDINGS §504 — the NWS tag layer reaches 2.2 % of the RU store** (29-07-2026, same handoff): 255 of 11,603 translated rows carry a tag bracket at all, and 4 of the 150 cards on the live G5 sheet. The feature is right — those 4 cards were previously unfindable — but the census's 48,214 tagged senses count senses in the source dictionary, not cards in the review queue. Two store-side defects fell out: 17 half-translated tags (`без уточн` ×13, `Мед` ×2, `Линг`/`Лингв`), and one malformed bracket (`[Gen, unsp , 1349 A.D. , Delhi]`) that would otherwise have rendered as a facet chip. Measurements in [`RussianTranslation/RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

### Fixed
- **A git worktree silently disabled every sibling-repo lookup — FINDINGS §503** (29-07-2026, same handoff): `GH = join(HERE, '..', '..', '..')` resolves to `GitHub/` only in the canonical checkout; a worktree created the way the org's shared-tree rule *requires* lands beside it, so eleven `src/` modules quietly found no sibling repo. Because those tables are deliberately optional (CI checks out one repo), the degradation never fails — it just ships a thinner artifact. Caught when a pinned re-issue of the G5 sheet produced **0** `<ab>` expansion spans and **1** citation mark instead of **253** and **8** — byte-valid, 150/150 drift-clean, and on its way to the reviewer who had asked for exactly that layer two days earlier. [`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py) and [`pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py) now honour a `CSL_SIBLING_ROOT` override; the other nine modules still carry the bare guess (queued, not done).

## [1.101.0] — 2026-07-29

### Added
- **H1844 — RV multi-translation evidence layer, wave 1b: divergence typing, advisory layer B, and the pwg_ru/en pipeline wiring** (29-07-2026; orchestration and adjudication Opus 5 `claude-opus-5[1m]`, divergence generator `deepseek-chat`, alignment `bert-base-multilingual-cased` + `sentence-transformers/LaBSE`; [H1844](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1844-Opus_RussianTranslation_rv-multitranslation-typing-w1b_29.07.26.md)). Typed 12,000 (stanza × translator-pair) labels over a seeded 2,000-stanza pilot for **$1.06** ([`src/rv_divergence_type.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_divergence_type.py), provider-pluggable over DeepSeek/OpenRouter, reusing the committed H1210 arm-B HTTP client); the 100-item human calibration gate is generated and bound ([`src/build_rv_divergence_gate_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_rv_divergence_gate_sheet.py)) and **awaits a vote** — the full 10,552-stanza run stays queued behind it (R13), not self-approved. New TM tier `corpus_translation_witness` / `suggest_only` with per-translator priors keyed by work, classified **SHARED** in [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) and reachable on `ru` and `en` alike (R7). Judge witness + unanimous-only contradiction gate as tested pure functions ([`src/rv_pipeline_bridge.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_pipeline_bridge.py)). 33 tests green in [`tests/test_rv_spine.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_rv_spine.py); `window_selftest.py` 193/193.

### Changed
- **Layer B ships flagged `low_confidence` and excluded from the contradiction gate — stop condition 3, measured not assumed.** The 300-token frequency-stratified gold scored **de 29.2 % · ru 19.2 % · en 10.5 %** against an 85 % bar ([`gold/rv_wordlevel_precision_report.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/rv_wordlevel_precision_report.md)). The failure is systematic — the aligner returns the stanza's salient proper noun whatever the source token was — and swapping `bert-base-multilingual-cased` for LaBSE reproduces it, so the ~8.8 h full-scale pass was **not** run and the 0.20 `ALIGN_GATE` was **not** re-tuned to rescue the number. Spine A is unaffected, exactly as R5 designed. Two further measured findings: that gate drops **0 of 9,400** alignments on Vedic, and a 300-observation spike wrongly read `lexical_variant` as dead (0.3 %) where the 12,000-label pilot puts it at 6.0 % — so the five-class taxonomy was **not** collapsed. `added_by_one` is inert at 0/12,000 and is flagged as a prompt/taxonomy defect. Details: [`docs/DECISIONS_LOG_rv_multitranslation.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/DECISIONS_LOG_rv_multitranslation.md), tables in [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).
- **wisdomlib's four R11 roles are unpopulated, and W1.13 cannot be met as written** ([`src/rv_wisdomlib_bridge.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_wisdomlib_bridge.py)). The on-disk feed is a catalogue of works plus a 63-word Vajrayāna Buddhist probe set, not a Sanskrit gloss resource; intersected with the RV's 9,539 lemmas it is correctly empty, and the join key was verified sound in both directions so the zero is a data fact rather than a bug. Unblocking a real EN gloss tier needs a `definitions.py` crawl, which R17 forbids inside this run and which should be scoped as its own handoff.

## [1.100.0] — 2026-07-29

### Changed
- **H1210's conclusion is overturned by its own coverage fill — the A/B is a tie, and the "length-routed hybrid" recommendation is withdrawn** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1846](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1846-Opus_SanskritLexicography_h1210-arm-a-coverage-fill_29.07.26.md)): arm A's 13 unattempted cards were run from the frozen payloads, putting both arms at **100/100**. The new cards barely moved the audit metric (93 vs 78) — but running them exposed *why* that metric flatters arm A. `canonical_audit.py` scores `cards_out`, which holds the last attempt that **returned**, while `final_status` records how the card **ended**; a card whose controller rejected attempt 1 and whose attempt 2 died mid-stream ends `worker-null-death` yet still carries attempt 1's text into the audit. Counting only cards each pipeline would actually ship unattended (`promote_dry` AND a clean rig status): **arm A 72/100, arm B 70/100 — a tie**, and the long-entry quartile **reverses** (A 3/23 = 13%, B 4/23 = 17%). The S2 defect-culprit stratum shows it sharpest: arm A 13 audit-clean → 4 shippable. Full revision in [the report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md) §3/§7 and a new [`RESULTS_LOG`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md) row. Caveats that bound the tie: the 13 filled cards ran on a later controller tier (`claude-opus-5[1m]` vs `claude-opus-4-8`) and **8 of them lost attempts to API transport failures**, so arm A's Q4 13% is a floor.

### Added
- **FINDINGS §501 — an A/B whose "clean" metric scores the last attempt that RETURNED, not what the pipeline would ship, can name the wrong winner** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`): the generalised form of the above, with the rule it yields — report the artifact-quality metric AND the delivery metric, and where they diverge, the divergence *is* the finding. Reusable tooling: [`status_vs_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/status_vs_audit.py) (per-card rig-vs-audit cross-tab) and [`dual_metric_breakdown.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/dual_metric_breakdown.py) (both metrics per stratum). Companion to §500: that one is about which cards enter the denominator, this one about which cards count as success.

### Fixed
- **Arm-A telemetry asserted its model ids instead of measuring them** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1846](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1846-Opus_SanskritLexicography_h1210-arm-a-coverage-fill_29.07.26.md)): [`collect_arm_a.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/collect_arm_a.py) hardcoded `workers claude-sonnet-5 / controller claude-opus-4-8` into `arm_a.telemetry.json` — the string the A/B report prints as its "generator model" row. But [`wf_template_ab.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/wf_template_ab.js) pins harness **aliases** (`model: 'sonnet'`, `model: 'opus'`), which resolve to whatever each tier currently is, so the recorded ids were an assumption that silently decays with every model release. It now reads the real per-agent `model` off each chunk's task-output rows, and — when only some chunks carry them, as when a run is refilled later — names **both populations with their card counts** rather than collapsing to one string that misattributes whichever population is silent.

### Added
- **`refresh_after_fill.py`** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1846](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1846-Opus_SanskritLexicography_h1210-arm-a-coverage-fill_29.07.26.md)): the post-fill recompute of the H1210 A/B as ONE chain — collect → telemetry → canonical audit over all ten chunks → `ab_report` + `length_breakdown` + `coverage_gap`. Collecting a chunk without re-auditing, or re-auditing without refreshing the coverage table, is precisely how a stale denominator survives into a report ([FINDINGS §500](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)); the script also stamps its outputs with a new date so the 87-card artifacts behind that finding stay reproducible.

## [1.99.0] — 2026-07-29

### Added
- **RV multi-translation evidence spine, wave 1a** (29-07-2026, [H1843](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1843-Opus_RussianTranslation_rv-multitranslation-evidence-w1a_29.07.26.md), [PR #867](https://github.com/gasyoun/SanskritLexicography/pull/867)): griffith / stanza / lemma / renou layers — see the [v1.99.0 release notes](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.99.0) for the full description. _Recorded here after the fact (H1846, 29-07-2026): that release was tagged without promoting its entries into this file, so the changelog had no 1.99.0 section at all while a published release carried the number._

## [1.98.0] — 2026-07-29

### Added
- **H1210 — the DeepSeek-vs-Claude-native A/B on 100 stratified PWG cards, reported** (runs 28-07-2026, report 29-07-2026; controller Opus 4.8 `claude-opus-4-8` in **both** arms, arm-A workers Sonnet 5 `claude-sonnet-5`, arm-B generator `deepseek-chat`; report + coverage audit Opus 5 1M `claude-opus-5[1m]`, [H1210](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1210-Opus_SanskritLexicography_pwg-ab-deepseek-vs-claude-100_17.07.26.md)): one variable changed — the generator; same worklist, prompt, free gate, retry chain, controller and canonical audit. Result: the arms are level below ~4.5 kB and diverge on the longest quartile (arm A **93 %** on n=14 vs arm B **35 %** on n=23; defect-culprit stratum S2 11/12 vs 3/15), and arm B costs **$0.0093 per clean card**, generation-only — its controller runs uncosted on the subscription lane. Full method, limitations and what the numbers do *not* support: [`pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md); summary row in [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md). Both arms promote-DRY. A length-routed hybrid is the only option the data positively supports; the blind 40-item human vote (lock committed, HTML gitignored) is generated and still pending, and can move the conclusion.
- **FINDINGS §500 — a batch that never runs deletes a *band* of the sample, not a random subset** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`): arm A of the H1210 A/B completed 87 of 100 cards, and because chunks pack by **bytes**, the 13 missing cards were a contiguous length band — 9 in the top quartile and **all ten S4 verb-root cards** — i.e. exactly where both arms degrade, flattering the incomplete arm by construction. Per-stratum summaries hide it (a missing stratum prints as an absent row, not a zero). Defence: compute `attempted` against the frozen worklist and report the gap per stratum by name before any rate — [`coverage_gap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/coverage_gap.py). Generalises to every chunked run here (bounded windows, cohort barriers, residual drains), not just A/Bs.

### Fixed
- **The blind A/B vote sheet was unreviewable — now rendered by the shared H1808 renderer** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`): [`build_ab_review_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/build_ab_review_sheet.py) printed raw CDSL markup as escaped text with dead `<ls>` citations — the third generator in a row to re-introduce the defect H1646 (csl-atlas) and H1808 (here) had already settled. It now calls [`src/g5_card_render.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/g5_card_render.py) (`print_panel` for RU, `de_panel` for DE, plus that module's legend and CSS) instead of rendering its own, so the A/B vote and the G5 vote show markup identically: **715 linked citations** in this sheet, plus 204 carrying a bibliography tooltip where the sigla resolve to no scan. A first pass hand-rolled the colouring and linking; it was replaced once H1808 landed on `master` mid-session — measured on arm B, the shared path links strictly more (2,227 of 2,992 citation spans). LANG_PARITY entry `h1210_ab_arm_scaffold` re-affirmed (the fix is language-neutral; the GAP is unchanged).

## [1.97.0] — 2026-07-29

### Added
- **G6 gold cards carry their evidence BEFORE the vote** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1801](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1801-Opus_SanskritLexicography_g6-gold-card-evidence-panel_28.07.26.md)): MG's ruling «Это все надо давать ДО, а не ПОСЛЕ». New [`RussianTranslation/src/gold_evidence_panel.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_evidence_panel.py) joins four panels onto every card from assets the project already owns — a period-routed dictionary sense list (Vedic ⇒ GRA first, Classical/Epic/Medieval ⇒ MW + PWG), a Whitney root line (DCS `lemma2root` + `mw_etymology` + `pwg_etymology` → `mw_roots.tsv` → MW↔Whitney `root_crosswalk` → Whitney's own gloss), attested contexts from the card's own work with their published Russian, and the ranked A2/A4 Sa→Ru glossary. Nothing new is derived. Starter re-cut as `g6-mqm-gold-starter-evidence-picker-2026-07-29` (same 20 ids; carries H1802's required reject-label picker too, since both follow-ups re-cut one sheet). Coverage: glossary 20/20, dictionary 16/20, contexts 14/20, root 8/20 — the 12 rootless cards are proper names, a pronoun and a particle. Report: [`RussianTranslation/review/G6_EVIDENCE_PANEL_DIFF_2026-07-28.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/G6_EVIDENCE_PANEL_DIFF_2026-07-28.md). Closes hard gate 2 of [H1665](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1665-Fable_SanskritLexicography_pwg-store-gold-cut-execute-r1-r5_26.07.26.md); with H1802 merged, the n=400 store cut is unblocked.

### Fixed
- **The reversed G6 card is id 122, not 118** (29-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1801](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1801-Opus_SanskritLexicography_g6-gold-card-evidence-panel_28.07.26.md)): the H1796 commit message, the H1801 handoff, FINDINGS §499 and the 1.96.0 section below all recorded the card reversed on withheld Rigvedic evidence as "card 118". Card **118** is `aruRAmSub` / `raghuvamsha` / Classical, ruled `defer` with `needs_adjudication=true`; the reversed card is **122** (`na` → «словно», `08_rigveda`). Verified against rows 11 and 18 of [`gold/decisions_g6-mqm-gold-starter-2026-07-25.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.csv). The ruling and every count are unaffected — only the id was misrecorded.
- **Two evidence guards earned while building the panels** (29-07-2026, same handoff): DCS homographs below 10 % of the top candidate's corpus count are now rejected out loud — unfiltered, the panel served Grassmann's √mad *"wallen, sprudeln"* as a sense of the particle `na`, on the very card the work exists to fix; and whole-compound keys are tried before compound parts, after `avAkSAKa` *"having shoots turned downwards"* lost to the part `avAk` *"downwards"* on the card voted «с ветвями вниз».

## [1.96.0] — 2026-07-28

### Added
- **G6 MQM gold starter — MG's vote applied, first human gold labels for pwg_ru** (28-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1796](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1796-Opus_SanskritLexicography_g6-mqm-gold-starter-vote-apply_28.07.26.md)): 20/20 cards of sheet `g6-mqm-gold-starter-2026-07-25` bound to their lock and ingested — [`gold/decisions_g6-mqm-gold-starter-2026-07-25.labels.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.labels.jsonl) (16 LLM labels confirmed, 3 overturned, 1 deferred; LLM label accuracy 16/19 = 84.2 %, Wilson 95 % [62.4 %, 94.5 %] — a starter packet, **not** a precision figure of record). Audit record: [`review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md). Satisfies hard gate 1 (R5) of [H1665](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1665-Fable_SanskritLexicography_pwg-store-gold-cut-execute-r1-r5_26.07.26.md).
- **PWG→RU finish action brief** (28-07-2026, Grok 4.5 `grok-4.5`, [H1778](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1778-Grok_SanskritLexicography_pwg-ru-finish-action-brief_28.07.26.md)): ADHD-shaped checklist of remaining human votes, costs, open handoffs, and do-not-vote rules — [`RussianTranslation/PWG_RU_FINISH_ACTION_BRIEF_28-07-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_FINISH_ACTION_BRIEF_28-07-2026.md).

### Fixed
- **FINDINGS §499 — the G6 review card is the defect, not the reviewer** (28-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1796](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1796-Opus_SanskritLexicography_g6-mqm-gold-starter-vote-apply_28.07.26.md)): two measured defects in one instrument — 5 of 6 rejects carried no typology label (the "correct label as the first word of the note" convention is unenforceable free text, and `apply_decisions.py` is all-or-nothing, so all 20 votes failed to apply), and card 122 (`na` → «словно», `08_rigveda`; recorded as 118 at the time — corrected in 1.97.0) was rejected only because the card withheld the Rigvedic comparison-particle evidence the project already owns — reversed at adjudication. Both now gate the n=400 store cut via [H1801](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1801-Opus_SanskritLexicography_g6-gold-card-evidence-panel_28.07.26.md) (evidence panel) and [H1802](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1802-Sonnet_csl-pyutil_review-sheet-reject-label-picker_28.07.26.md) (required label control in `csl_pyutil`). Dashboards regenerated (157 findings), `epistemic_integrity_check.py` green.

## [1.95.0] — 2026-07-28

### Fixed
- **Epistemic-integrity gate repair — FINDINGS §488–§498 headings were missing their `§` marker** (28-07-2026, Sonnet 5 `claude-sonnet-5`, [H1752](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1752-Sonnet_SanskritLexicography_red-branch-repair-findings-488-492-dangling-index_27.07.26.md)): `master` went red at PR #845/H1735's GAPS→FINDINGS graduation — the checker reported §488–§492 (later §488–§498) as dangling Index rows with no heading. The section bodies were never missing; eleven headings were written as `### 488.` instead of `### §488.` (`§` required by `epistemic_integrity_check.py`'s heading regex), so heading↔Index parity failed. Fixed by adding the missing `§`, bumping the next-free marker to §499, and regenerating both dashboards (156 distinct FINDINGS headings, up from the stale 124). `python tools/epistemic_integrity_check.py --dir .` now reports 0 defects.

## [1.94.0] — 2026-07-27

### Added
- **FINDINGS §497–§498 — the csl-orig L-number is not a join key, and word-initial Harvard-Kyoto capitals never decode** (27-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1766](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1766-Opus_csl-observatory_h1477-salvage-lcode-drift-hk-residue_27.07.26.md)): salvaged from a **duplicate H1477 session** that ran concurrently with the one that shipped §496 and never pushed — both figures re-measured independently rather than imported. **§497** — of 22,826 form-era correction events carrying an `<L>` code, only **7,978 (35.0 %)** still point at their own headword in current csl-orig; the best dictionary is a coin flip (pw 53.9 %) and six are noise (cae 0.2 %, ap 1.2 %, wil 1.6 %). A stored `<L>` is a historical address, not a stable foreign key — relevant to any crosswalk, citation resolver or cross-snapshot join. **§498** — `build_correction_events.looks_hk` tests `tok[1:]`, so a word-initial HK capital (`A`=ā, `I`=ī, `U`=ū, `R`=ṛ — exactly the Sanskrit-relevant set) never triggers the decode: **113 attestation-proven mis-transcoded headwords** across 14 dictionaries (`Adeya` → ādeya, `Ahnika` → āhnika), zero ambiguous. Filed as a csl-observatory `[integrity]` issue; the naive fix would corrupt capitalised English cells, so the safe fix is attestation-gated.
- **FINDINGS §496 — edit-distance record linkage over Sanskrit headwords is 70–98% false matches** (27-07-2026, Opus 5 1M `claude-opus-5[1m]`, [H1477](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1477-Opus_csl-observatory_capture-recapture-fuzzy-linkage-corrector-pair_22.07.26.md) / [csl-observatory PR #120](https://github.com/sanskrit-lexicon/csl-observatory/pull/120)): measured on the OBS-T correction corpus — 606/863 pw, 474/616 mw, 128/220 bur edit-distance-1 links join *distinct real headwords*, because a 20k–290k-record Sanskrit inventory is saturated with minimal pairs. The entry gives what works instead (decode provable SLP1 residue; fold only non-phonemic features — `form_key` collides 0.2–0.4% of a dictionary's own records where `norm` collides 9–16%; use the correction payload where available) and, more importantly, the two annotation-free ways to *measure* any headword matcher's false-match rate against `csl-orig`. Applies to SanskritSpellCheck candidate generation, csl-atlas crosswalks, WhitneyRoots form matching and kosha joins.
- **GAPS residual H1745–H1747** (27-07-2026, Grok 4.5): FINDINGS §493–§495 (routing κ=1.0 LLM second pass; homonym 38 single-lemma_id ceiling; Cyrillic name seed inventory 61/47).

### Changed
- **H1724 worktree backlog drain** (27-07-2026, Sonnet 5 `claude-sonnet-5`): re-measured the 23-row H1724 inventory — 20 of 23 were already resolved by other sessions between mint and execution; landed the 1 genuinely-unlanded worktree (PR [#847](https://github.com/gasyoun/SanskritLexicography/pull/847), FINDINGS §496) and removed 1 clean/already-merged worktree; escalated the remaining 3 (`h1080-raw624`/`h1080-raw629` detached 434/458-commit parallel histories, `rt-harden-codex` live 30-dirty-file Codex session) to a human per the handoff's own escalation rule.


## [1.93.0] — 2026-07-27

### Added
- **[ASSUMPTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) category D — evaluation-threshold assumptions (§9, §10)** (Opus 5 1M `claude-opus-5[1m]`, 27-07-2026, from [H1476](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1476-Opus_SanskritGrammar_pedagogy-aspect-measurable-result-metrics_22.07.26.md)). The registry's first rows about a **ruler** rather than about the data. **§9** — *a threshold set by argument is a decision rule*: the digital-pedagogy field's PM1–PM12 bars are relied on as pass/fail marks, but only **4 of 12** rest on a measurement, 1 is a disclosure rule, and **7 are argued with no anchor**; test = compute PM8 and PM12 (both derivable from data already on disk) and compare against their proposed bars. **§10** — *a gold-agreement rate transfers between aspects*: PM1's ≥90 % sandhi bar is PM2's measured 90.7 % keyed share borrowed across aspects, which looks measured precisely because it carries a real decimal from a real corpus. Both carry a **calendar gate (27-09-2026)** instead of a re-check recipe, and the Conclusions record why: a keying assumption fails loudly the moment anyone looks, whereas a threshold assumption never fails because nothing tests it — **the premises that decay silently are the ones about your instruments, not your data.**

### Changed
- **H1724 worktree backlog drain (Sonnet 5 `claude-sonnet-5`, 27-07-2026):** 20 of 23 linked worktrees resolved — 17 turned out already-landed under a different squash-commit (PRs #692/#695/#697/#715–#724/#746/#815/#719), removed with zero content loss; 2 stale drafts (a superseded release-notes scratch file, a retroactive changelog footnote for a burnt `v1.15.0` tag) parked as patches in [`Uprava/parked_patches/`](https://github.com/gasyoun/Uprava/tree/main/parked_patches) and removed; 1 genuinely unlanded H1437 phase-3 branch handed off for rebase-through-conflicts and PR. 3 escalated for a human ruling, not resolved: a disconnected 2014–2026 parallel git history (434/458 commits, no shared ancestor with `master`) and a Codex worktree carrying 30 uncommitted files that look like live in-progress work. Full disposition table: [H1724](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1724-Sonnet_SanskritLexicography_worktree-backlog-drain-unpushed-work_27.07.26.md).

## [1.92.0] — 2026-07-27

### Added
- **[FINDINGS §487](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — a cross-scheme join is a transliteration step, not a string comparison** (Opus 5 1M `claude-opus-5[1m]`, 27-07-2026, from [H1476](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1476-Opus_SanskritGrammar_pedagogy-aspect-measurable-result-metrics_22.07.26.md)). Joining an IAST-spelled root catalogue straight onto SLP1 lemma keys in kosha's [`lemma_frequency.tsv`](https://github.com/gasyoun/kosha/blob/main/data/frequency/lemma_frequency.tsv) runs clean, matches **218 of 745** roots, and answers **82.7 %**; through [`sanskrit_util.to_slp1`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py) it matches **616 of 745** and answers **56.2 %** — a **26.5-point** error, in the direction that flatters the deliverable. The matches are not a random sample: IAST and SLP1 coincide exactly on the diacritic-free roots, so the join silently selects a frequency-enriched subset and biases any token-weighted statistic upward. The generalisation — when one spelling of a join key is a subset of the other's character set, silent non-matches are *selection on that character set*, not random loss — plus the practice that would have caught it: report the join rate next to the result.

## [1.91.0] — 2026-07-27

### Fixed
- **[`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) §II — three wrong Repo cells, found by the H1475 consolidation spike and repaired under H1722** (Opus 5 1M `claude-opus-5[1m]`, 27-07-2026). `PUI` and `IEG` were marked "csl-orig only" and `PD` linked a Cologne **scan** where a repo link belongs — all three repos exist ([PUI](https://github.com/sanskrit-lexicon/PUI), [IEG](https://github.com/sanskrit-lexicon/IEG), [PD](https://github.com/sanskrit-lexicon/PD), the last with 31 files of real OCR-comparison work). Not a cosmetic defect: the "csl-orig only" marker is the field the **13 repo-less dictionaries** count is derived from, so a wrong cell silently moves that figure.
- **All 44 Repo cells re-verified mechanically against the live org, not just the three known-bad** — `gh repo list sanskrit-lexicon` + `gasyoun`, every cell's link resolved or its "csl-orig only" claim confirmed. Result: **3 defective, 41 correct**, and 0 after the fix. The audit is re-runnable rather than a one-off eyeball.

### Changed
- **The Repo column now says what it means.** A dictionary repo in this org is normally an **issue venue**, not a data repo — the text lives in [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) either way — so `csl-orig only` (no repo of any kind, 13 dictionaries) is now distinguished from "— venue only" (repo exists, holds only issues and a Pages shell: `PUI`, `IEG`), with the verification date recorded and a pointer to the [consolidation spike](https://github.com/gasyoun/Uprava/blob/main/CONSOLIDATION_SPIKE_REPOLESS_DICTIONARIES_THIN_VIEW_REPOS_2026Q3.md) that enumerates the 13.

## [1.90.1] — 2026-07-27

### Fixed
- **Review sheets are now default-denied in `.gitignore`, not enumerated per
  generator.** `RussianTranslation/.gitignore` listed each sheet family by prefix
  (`h178_`/`h1303_`/`h1306_`/`h1682_`/`g5_`/`g6_`) plus one line per
  compound-differs sheet, so every *new* generator leaked until someone remembered
  to add a line — the gorresio southern-map audit sheet did exactly that and sat
  stageable in a public repo. Replaced with three shape rules
  (`review/*_sheet.html`, `review/*_review.html`, `review/*_decisions.json`) plus
  an explicit `!` allowlist for the three sheets that are intentionally published
  (renou pilot ×2, kochergina 4rows). Publishing a sheet is now a deliberate act;
  the H1404 `review/locks/` and `*_frame.tsv` counterparts stay committed.
  Verified: all 8 leaking local artifacts are ignored, and every currently-tracked
  file under `RussianTranslation/review/` is still trackable.

## [1.90.0] — 2026-07-27


### Added
- **H1705 artifact propagation — the deliverable registered on every surface that
  applies.** `FEATURES_INDEX.md` gains **E50**, one row for the whole Rāmāyaṇa
  edition-alignment family (Gorresio inventory + 19,852-verse e-text + Gorresio↔Southern
  verse map + the new Bombay inventory + Southern↔critical map) — H1656 and H1689 had
  never been registered there either, so this closes three handoffs' worth of index gap
  at once. The epistemic residue is now recorded rather than left in a report:
  **DEAD_ENDS §13** (the Bombay concordance route, with the "don't retry unless" order of
  operations), **GAPS §13** (no Russian Uttarakāṇḍa — an external, human blocker, with
  what it would unblock: 288 kāṇḍa-6 references are already mapped and waiting), and
  **CONTRADICTIONS §9** (the "Southern"-labelled critical text, 🔴 unresolved, blocking
  three downstream reads). Plus a metadoc for the verdict doc — limitations first, since
  the doc's subject is a *non*-action whose reasoning leaves no other artifact — and the
  `RussianTranslation/.ai_state.md` entry, flagged **not next-actionable** so the lane is
  not re-opened as a numbering task.

## [1.89.1] — 2026-07-27

### Fixed
- **H1705 counting correction (same day).** v1.89.0 reported **1,781** plain `R.`
  book-7 citations out of 39,845. The abbreviation regex ended in a bare `R\.`
  alternative, so `R. ed. Bomb.` and `R. SCHL.` were folded into the plain-`R.`
  bucket — 16 book-7 refs, 623 across all books. Re-counted with every edition
  qualifier split out: **1,765 plain of 39,222**, plus 16 edition-qualified book-7
  refs. The 127 out-of-range (sarga >100) figure and every conclusion in the
  verdict are unchanged. Recorded separately because it is independently useful:
  PWG carries **319** explicit `R. ed. Bomb.` citations across all books, only 14
  of them in book 7 — Böhtlingk names the Bombay edition well outside the book-7
  default. Corrected in
  [`pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md`](RussianTranslation/pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md)
  and `pwg_ru/COVERED_TEXTS_RU.md`.

## [1.89.0] — 2026-07-27

### Added
- **H1705 — R. (Bomb.) book 7: measured verdict, no OCR spent.** The Bombay
  uttarakāṇḍa does **not** map ≈1:1 onto the corpus text (111 sargas + 13
  interpolated vs 100; identical verse count in 11/100 shared sargas; delta
  −14…+18, mean +4.7), so the direct-with-offset option is rejected. The
  concordance option was rejected too, on a ground the handoff did not consider:
  `07_ramayana-uttarakanda.jsonl` holds **2,690 Sanskrit segments and 0 Russian**
  (kāṇḍa 6 likewise), so a Bombay↔corpus map would have no consumer — there is no
  Russian uttarakāṇḍa, and none is in the RussianRamayana pipeline. Full numbers,
  including the 1,781 plain `R.` book-7 citations (127 of them naming a sarga
  >100 that a 100-sarga text cannot carry):
  [`RussianTranslation/pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md`](RussianTranslation/pwg_ru/H1705_RAMAYANA_BOMBAY_BOOK7_VERDICT_2026-07-27.md).
- **`RussianTranslation/src/ramayana_bombay_inventory.tsv`** — Bombay (1859)
  structural inventory, 658 sargas across all 7 kāṇḍas (kāṇḍa → sarga →
  n_verses → volume/page/folio span + flags), read off the ramayanabom
  scan-viewer's hand-made per-page index with **no OCR**. Built by the new
  `build-bombay` command in `build_ramayana_concordance.py`; 9 selftest checks,
  two of which pin the verdict (111 consecutive sargas; exceeds the corpus by 11).

### Changed
- **`citation_tm.py` retypes the Rāmāyaṇa 4/6/7 miss** from `locus-not-in-corpus`
  to **`ru-translation-unpublished`**, with a `blocker` field naming the kāṇḍa.
  The old string was shared with genuine corpus-coverage holes, and reading book
  7's miss as an ingest/numbering gap is what got a Bombay-concordance handoff
  minted for a book whose real blocker is that nobody has translated it. Plain
  `R.` book 7 now lands on the same typed miss as `R. GORR.` book 7 (5 selftest
  checks, one an out-of-corpus-range sarga).

### Fixed
- **Documented an upstream index typo** in ramayanabom's `indexv3.txt`: the last
  uttarakāṇḍa sarga is typed `11` where `111` is meant (pages 810–812), colliding
  with the genuine sarga 11 at pages 538–541. Repaired explicitly in the builder
  (`BOM_INDEX_REPAIRS`, flag `index_typo_111`) against the page-810 colophon, and
  asserted in selftest.

### Notes
- **[integrity] [#822](https://github.com/gasyoun/SanskritLexicography/issues/822)** —
  corpus kāṇḍas 6–7 are Sanskrit-only **critical-edition** text under a
  "Southern/Leonov" label (99.8%/99.9% identical to DCS critical at the same
  `sarga.verse`, vs 1.2–3.0% for kāṇḍas 1/2/3/5), so
  `ramayana_southern_critical_concordance.tsv` aligns those two kāṇḍas against
  themselves. FINDINGS §480 (the ramayanabom scan traps: a Latin-garbage text
  layer that passes a non-empty check, and a 2-up embedded image the PDF crops)
  and §481 (measure the asset, not the manifest).

## [1.88.0] — 2026-07-27

### Fixed
- **[integrity] a sheet generator could rewrite a LIVE lock in silence, invalidating votes
  already cast** (H1703 follow-on, Opus 5 1M `claude-opus-5[1m]`). A generator reads live
  data, so re-running one after its inputs moved re-cuts the sheet — and
  `review_binding.write_lock()` overwrote the existing lock without a word. Found
  concretely: re-running `compound_differs_review_sample.py --write` on `master` after the
  H1703 extractor repairs renders `sha256:68a6297b…` where the committed lock binds
  `sha256:31c106bb…`, i.e. a different 200 cards. Any votes in flight would have stopped
  validating with no signal until `validate_decisions.py` rejected the export — the same
  failure shape as the unbound sheet H1703 item 1 fixed, one step later. `write_lock()`
  now raises `LockCollision` on a differing hash (same-hash rewrite still allowed, so
  idempotent regeneration is unaffected; deliberate re-cut takes `force=True` /
  `REVIEW_LOCK_FORCE=1`), with three selftest cases pinning it. Protects every sheet in
  the estate. Also recorded: **arm 1 reproduces only at
  [v1.83.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.83.0)**
  (verified byte-for-byte), arm 2 on `master` — both sheets' HTML regenerated and placed
  so their `file:///` links in
  [REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md)
  resolve (neither existed in the working checkout; both are gitignored by contract).

### Added
- **FINDINGS §476–§479 — the reusable half of H1703** (Opus 5 1M `claude-opus-5[1m]`).
  Four measured findings a future session in any repo would otherwise rediscover:
  **§476** repairing an extractor *grows* the disagreement queue it feeds (4,123 → 4,246
  cards here) — a plan that assumes a shrink is asserting something unmeasured;
  **§477** `wilson_lower(35,35)=0.901` vs `0.898` at 34 makes 35 the floor for a 0.90
  per-stratum gate, and a censused stratum promotes with no interval at all (so a 0.890
  bound is not "unpromotable"); **§478** a blind arm stratified on an agent's own rules
  must never render the rule, and must take its card ids from the committed lock rather
  than the frame TSV; **§479** PWG's etymology paren needs three rules, not one — bracket
  masking, first-`{#…#}`-per-part, and surface-coverage arbitration for the derivation
  ladders and disjunctions where first-wins ships a base instead of a member. §475
  (MW `<k2>` variant fusion) marked ✅ FIXED with the one correction the original `So:`
  needed: take the first variant that *carries the segmentation*, not simply the first.

## [1.87.0] — 2026-07-26

### Fixed
- **[integrity] MW `<k2>` variant fusion welded a non-word compound member**
  ([#801](https://github.com/gasyoun/SanskritLexicography/issues/801), H1703, Opus 5 1M
  `claude-opus-5[1m]`). MW lists spelling/accent variants of a headword inside one `<k2>`
  separated by `; ` (`gaRa—kAri; gaRakAri`);
  [`mw_compounds.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_compounds.py)
  split on the em-dash first and cleaned second, and `_ACCENT_STRIP` removes both `;` and
  the space — so the variants fused into a member that is not a word (`gaRa` +
  **`kArigaRakAri`**). The bogus member also inflated the arity, so
  `nominal_grammar._irregularities` emitted `compound:3_members` and the Zaliznyak index
  `+3` for a two-member compound (`citpati` shipped as `m·3a+3`). **41 of 106,603** MW
  compound records corrected, 22 of them arity-corrected;
  [`headword_index.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv)
  (36 rows), `paradigm_stats.tsv` and `reverse_paradigm_index.json` regenerated. New
  `--selftest` (7 fixtures) wired into CI. [PR #817](https://github.com/gasyoun/SanskritLexicography/pull/817).

### Added
- **H1703 — second, rule-stratified blind arm: every stratum of the compound `differs`
  queue can now be priced** (Opus 5 1M `claude-opus-5[1m]`). The H1628 arm samples along
  length × DCS-frequency × member-count, i.e. **across** the H1681 adjudicator's rules: it
  lands 139 cards in one stratum and 0–16 in each of the other seven, so it could promote
  3,018 of 4,226 rows and no more, however the human voted. New
  [`compound_differs_arm2_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_arm2_sample.py)
  (seed 1703) draws **232 cards**, 35 per unpriced stratum — 35 because
  `wilson_lower(35, 35) = 0.901` and `wilson_lower(34, 34) = 0.898` — disjoint from arm 1,
  stamped + locked, and **blind** (no stratum, rule, verdict or reason on any card,
  asserted by selftest). **All 4,353 rows now sit in a priceable stratum**; the 31-row
  `granularity_ic_vs_full_decomposition` is censused in full, recorded as
  `promotion_basis: census` rather than pretending its 0.890 bound cleared. Binding
  verified end-to-end on both sheets (valid export accepted; tampered hash, missing vote
  and unknown card id each rejected). Queue re-adjudicated against both repaired
  extractors — the three defect strata are gone (`pwg_layer_inner_chain` 75 → 0,
  `pwg_layer_no_headword_paren` 82 → 2, `mw_variant_fusion` 10 → 0) — and it did **not**
  shrink as H1703 predicted: 118 cards left, 241 entered, 4,123 → **4,246 cards**. Report:
  [PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md §8](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md).
  Upstream half: [SanskritGrammar#529](https://github.com/gasyoun/SanskritGrammar/pull/529)
  (closed [#527](https://github.com/gasyoun/SanskritGrammar/issues/527)). Nothing applied
  to the store; neither sheet voted.

## [1.86.0] — 2026-07-26

### Added
- **H1707 probe — the Calcutta Mahābhārata is obtainable after all, and PWG's citation
  scheme is already indexed** (Opus 5 1M `claude-opus-5[1m]`). Same-day successor to the
  H1652 rejection. [sanskrit-lexicon-scans/mbhcalc](https://github.com/sanskrit-lexicon-scans/mbhcalc)
  ships the 1834–39 printing as 3,006 page PDFs plus `parvanverse.js`, a
  `(parvan, continuous śloka) → page` index in **PWG's own citation scheme**:
  **3,007 of 3,009 distinct `MBH.` loci (99.9%) resolve to a scan page** with no OCR and
  no alignment. The PDFs carry no text layer (a one-page tesseract-5 `san` probe confirmed
  OCR is feasible but noisy), and it is not needed:
  [sujoysarkarai/mahabharatace](https://github.com/sujoysarkarai/mahabharatace) (ISCLS 2026,
  CC) releases a verse-level Calcutta alignment of the Dutta/Itihāsa text whose
  `ce_verse_number` **is** the continuous per-parvan śloka. Proved end-to-end on the
  citation that started H1652: `MBH. 5,7331` → its `manual_anchor` CE lines → verbatim in
  `05_mahabharata-udyogaparva:5.187.1-4#sa` → an existing Russian translation of record.
  The H1652 measurement stands; its "needs the Calcutta text" conclusion is now a task,
  not a blocker.

## [1.85.0] — 2026-07-26

### Added
- **H1683 source-check of the article-comparison gloss edits.** All 32 proposed
  RU gloss edits across the four finalist articles (`article-comparison/gloss_review_items.json`
  — agni 11 · akṣara 6 · ananta 9 · anya 6) now carry an agent verdict
  (source-confirms/source-contradicts/needs-human) with the governing PD line
  quoted verbatim from `<w>.verbatim.md`. 0 contradicted, 19 confirmed (14
  L-severity auto-accepted, 5 H/M-severity routed to a blind spot-check), 13
  genuinely need a human. Reduced human ask: 18 of 32 — see
  [`article-comparison/README.md`](article-comparison/README.md#source-check-pass-h1683-26-07-2026--reduced-human-ask)
  for the full table and the correction against H1664's ~8 pre-execution
  estimate. No edit was applied to any `pd-min.ru.md`, no vote was cast.

## [1.84.0] — 2026-07-26

### Added
- **H1652 — the MBH Calcutta↔critical map: built, measured, rejected**
  ([H1652](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1652-Opus_SanskritLexicography_citation-tm-ramayana-mbh-concordance-wiring_26.07.26.md),
  Opus 5 1M `claude-opus-5[1m]`). MG ruled 21-07-2026 to *build* the concordance that
  would let PWG's 5,512 Mahābhārata citations reuse their Russian translation of record.
  The prior artifact MG recalled is real — CommentaryStrategies ships an eighteen-parvan
  Nīlakaṇṭha-vulgate↔critical verse concordance, never wired into anything here — so the
  candidate map was built on top of it (a cumulative adhyāya-length table, committed as
  [`src/mbh_vulgate_cumulative.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mbh_vulgate_cumulative.tsv))
  and measured against the store: **11.2%** of 1,327 locatable citations within ±2 verses
  against a **2.5%** uniform-random null, 16.3% under a fitted per-parvan rescale scored
  on a held-out half, **1 of 43** on the anchors whose true verse is unambiguous. The
  vulgate witness is shorter than the text PWG counts in 8/18 parvans (Vanaparvan 11,859
  against a citation reaching 17,471), so 145 citations have no ordinal at all. The links
  below the failing step were verified independently (vulgate 6.26.47 → critical 6.24.47
  → the corpus line that is Bhagavadgītā 2.47). **`MBH.` stays `unmapped_locus_scheme`**;
  closing the gap needs the Calcutta text itself, not arithmetic over a different witness.
  New [`src/build_mbh_concordance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_mbh_concordance.py)
  (`build`/`validate`/`selftest`, CI-wired); full tables in
  [H1652_MBH_CALCUTTA_VALIDATION_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1652_MBH_CALCUTTA_VALIDATION_2026-07-26.md).

### Fixed
- **H1652 — `citation_tm` no longer fabricates a `canonical_id` for Rāmāyaṇa kāṇḍas 6
  and 7.** `_RAMA_GORR_WORK` named `06_ramayana-yuddhakanda` and `07_ramayana-uttarakanda`,
  works `corpus.db` does not carry; the lookup returned a resolved-looking key for a
  passage nobody can fetch. The census behind the fix corrects the handoff's own premise:
  kāṇḍas 4, 6 and 7 are a **translation** gap, not an ingest queue — Gryntser's Russian
  stopped after book 3 and Leonov's covers book 5, so no translation of record exists for
  kiṣkindhā, yuddha or uttara. Those kāṇḍas now return a typed `locus-not-in-corpus` miss
  with no id, pinned by three new selftest checks. Kāṇḍa 6 is the near miss: H1656's
  concordance already maps 2,295 Gorresio verses onto Southern yuddha loci, so 288 PWG
  references become reusable the day a Russian yuddhakāṇḍa exists — costed in
  [COVERED_TEXTS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/COVERED_TEXTS_RU.md)
  § Rāmāyaṇa kāṇḍas 4, 6, 7.

## [1.83.0] — 2026-07-26

### Fixed
- **The compound-`differs` blind arm is re-cut, deduped and BOUND (H1681 follow-up,
  MG ruling `re-cut`, 26-07-2026, Opus 5 1M `claude-opus-5[1m]`).**
  [`compound_differs_review_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_review_sample.py)
  never called `stamp()`/`write_lock()`, so `validate_decisions.py` would have rejected the
  export **after** the human had spent all 200 votes; it also sampled a frame whose rows
  could collapse onto one card id. Both fixed: `dedupe_by_card_id()` runs before sampling
  and `--write` now stamps + locks. Sheet bound at `sha256:31c106bb13cd2bad…`, 200 distinct
  ids, gate `G6-compound`, lock committed. The duplicate card turned out to be the visible
  end of a queue-wide mismatch — `headword_index.tsv` carries a row per part-of-speech
  reading while a card id is only `(k1, hom)`, so **the 4,226 `differs` rows are 4,123
  distinct cards**; the adjudication is unaffected (all 103 duplicate rows agree with their
  twin on members and verdict). Promotion ceiling unchanged at 3,018/4,226 (71.4 %).

## [1.82.0] — 2026-07-26

**H1689 — OCR e-text for Gorresio vols 2/4/uk; `gorresio-etext-gap` extinct** ([PR #805](https://github.com/gasyoun/SanskritLexicography/pull/805))

- tesseract 5.5 `san` on the 1,427 image-only Cologne pages' full-resolution embedded images; [gorresio_etext.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gorresio_etext.jsonl) 10,225 → **19,852 verses (all 672 sargas)**
- [Verse map](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_verse_map.tsv) 4,066 → **5,926 mapped** (k2 s10–127 +581 · Sundara +345 · Uttara +760); 12/12 sampled new pairs verified
- R. GORR. 2,16,46 → honest `no-southern-counterpart` (Bengal-only, best Southern score 0.109); R. GORR. 5,10,1 → `05_ramayana-sundarakanda:2.51`
- Audit-vetoed pairs re-applied by the build itself (pair-keyed); `।।`→`॥` segmentation hardening; method + traps in [FINDINGS §473](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)

Also promotes **H1682** (h1303_abbrev review-sheet rule-collapse, [PR #802](https://github.com/gasyoun/SanskritLexicography/pull/802)).

Fable 5 (`claude-fable-5`), user-overridden Opus lock.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## [1.81.0] — 2026-07-26

### Added
- **H1681 — all 4,226 PWG-vs-MW compound `differs` rows adjudicated by rule, with the
  four upstream defects behind them measured**
  ([H1681](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1681-Opus_SanskritLexicography_pwg-compound-differs-b2-full-queue-adjudication_26.07.26.md),
  Opus 5 1M `claude-opus-5[1m]`). New adjudicator
  [`src/pilot/adjudicate_compound_differs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/adjudicate_compound_differs.py)
  (20 rules, `--selftest` wired), verdicts TSV + promotion-plan JSON in `research/`,
  method + limitations in
  [PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md).
  3,724 `pwg_members-right` · 180 `index_members-right` · 322 `unresolved`. **No store
  field changed; the 200-card blind arm untouched.** The queue turns out to be two
  conventions meeting (PWG names lexemes, MW segments the surface — MW's members
  reconstruct the headword in 99.7 % of rows, PWG's in 1.9 %) plus four defects:
  `pwg_compound_split.py` is not bracket-aware (344/16,738 rows ship an inner or a
  neighbouring word's chain, 368 more unverifiable), `mw_compounds._clean_member` fuses
  `;`-separated MW `<k2>` variants (41/106,603), 12 transcription typos inside PWG's own
  member strings, and the H1628 blind-arm sheet is unbound (no lock ⇒
  `validate_decisions.py` would reject its export) with a duplicate card. Honest
  promotion arithmetic: the existing 200 votes can close **3,018 of 4,226 rows (71.4 %)**,
  not all of them — a stratum needs ≥ 35 arm cards to clear a Wilson-95 % lower bound
  of 0.90.

## [1.80.0] — 2026-07-26

### Added
- **H1691 — PWG's remaining DCS-carried cited texts adjudicated; 52 abbreviations, 12 mapped
  (26-07-2026, Opus 5 `claude-opus-5[1m]`).** Report
  [`PWG_DCS_TEXT_CROSSWALK_H1691.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_DCS_TEXT_CROSSWALK_H1691.md),
  adjudications
  [`pwg_ls_dcs_scheme_verdicts.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_ls_dcs_scheme_verdicts.tsv),
  and three evidence generators (`probe_dcs_text_scheme.py`, `probe_pwg_ls_scheme.py`,
  `probe_scheme_overlap.py` with a competitive-rank test against all 270 DCS texts) plus
  `h1691_handcheck.py`. Grounded PWG leaf senses 7,372 → **8,208** (+11.3%) on H1670's wide
  frame; `MAPPED` citation mass 36.4% → **44.7%**; the actionable backlog above 0.05% is empty.


### Fixed
- **`build_ls_text_crosswalk_backlog.py` mis-classified in both directions and now reads back
  the adjudicated verdicts.** Its candidate came from prefix-matching PWG's GERMAN `pwgbib`
  prose, so Pāṇini (21,305 citations) and Manu (20,605) — the two largest crosswalk wins in the
  dictionary — sat in `DCS-LACKS`, "a genuine corpus gap that no crosswalk can close"; and
  `max(candidates, key=tokens)` picked the wrong work six times over. `DCS-LACKS` fell from
  49.7% to 37.2% of citation mass and is now labelled for what it is: "no name-alike was
  found". New finding [§471](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md);
  tier-stamping defect recorded as §472; §465 updated with the new grounding figure.

## [1.79.0] — 2026-07-26

> Numbering note: this content was prepared as v1.78.0, but a concurrent session
> tagged v1.78.0 (H1670 grounding) without a changelog section — the changelog is
> repaired in this release's cut commit (audit section renumbered 1.78.0 → 1.79.0,
> H1670 section backfilled). See Uprava FINDINGS §104/§212 for the failure class.

### Changed — Gorresio map audit round 1: 28/32 approve; 4 half-verse-shift rows switched off (26-07-2026)

- The 32-card audit sheet was voted (agent vote by Fable 5 `claude-fable-5` on MG's
  direct delegation) — 28 approve incl. all 5 scan-verified gold anchors; the 4 rejects
  are a single OCR-segmentation sub-class (merged half-verses pairing with the tail
  verse) now marked `audit-rejected` in
  [ramayana_gorresio_southern_verse_map.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_verse_map.tsv)
  and inert for reuse (selftest pins the 4 rows). Detection heuristic queued into
  [H1689](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1689-Opus_SanskritLexicography_gorresio-vols-2-4-uk-ocr-etext_26.07.26.md).

### Added — H1651 store wrapper-defect sweep D1-D4, live gate follow-up (26-07-2026)

- Main pass ([#789](https://github.com/gasyoun/SanskritLexicography/pull/789)): D1
  repaired (34 rows/58 spans, closes
  [#752](https://github.com/gasyoun/SanskritLexicography/issues/752)); D3 ruled and
  bulk-applied (343/463 rows, 46 residual); D4 triaged (2,860 rows, no auto-fix — see
  [pwg_ru/H1651_WRAPPER_DEFECT_SWEEP_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1651_WRAPPER_DEFECT_SWEEP_REPORT_2026-07-26.md)).
- Addendum (this follow-up): new `cyrillic_in_sanskrit_wrapper` (HIGH_CONFIDENCE) and
  `gloss_wrapper_became_guillemet` (report-only) risks wired into the live per-card
  generation-time audit.

PRs: [#793](https://github.com/gasyoun/SanskritLexicography/pull/793), [#792](https://github.com/gasyoun/SanskritLexicography/pull/792) · Model (audit + release): Fable 5 (`claude-fable-5`)

## [1.78.0] — 2026-07-26

### Changed
- **FINDINGS §469 corrected — the csl-apidev call site was under-rated (H1695, 26-07-2026).**
  H1671'''s org-wide `to_slp1` audit classified [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev)'''s
  `rowSlp1()` as "a silent lookup miss, no corrupted data". Tracing the value showed both
  consumers were hit: the results list **rendered the wrong headword** (`Rāma` → `RAma` →
  displayed as **ṇāma**) and the `dalglob|` key addressed the wrong entry. Fixed upstream in
  [csl-apidev PR #127](https://github.com/sanskrit-lexicon/csl-apidev/pull/127); the finding
  now carries the correction and the second-order lesson (an audit that reads only the call
  line under-rates severity — it lives in what consumes the return value).

- **H1670 — PWG-sense × DCS grounding: 0.67% → 12.25%, and the 0.67% was our own bug**
  ([H1670](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1670-Opus_SanskritLexicography_pwg-dcs-sense-grounding-scale-levers_26.07.26.md),
  Opus 5 `claude-opus-5[1m]`). H1632 concluded that sense-level grounding was capped by data
  availability and could not be raised by scaling. It could: the aligner's `locus` tier was
  comparing each sense's `<ls>` against only the 3 passages per lemma sampled for the viewer
  (**0.299%** of those available), and a dead `"RV"` map key had hidden the Ṛgveda —
  6.89% of PWG's citation mass. With the **same** predicate and tiers, run at full passage
  depth over a 32× wider frame (16,208 groups, identical selection query), grounded PWG leaf
  senses go **52 → 7,372** (5,647 of them exact-verse). Dictionary-wide,
  `R0_grounding_not_computed` falls **18,438 → 10,515 (−43.0%)**. Per-lever attribution:
  [`PWG_SENSE_DCS_GROUNDING_LEVERS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_GROUNDING_LEVERS.md).
  **The data-availability half of §465 stands** — `R1_lemma_absent_from_dcs` moved by 52
  groups and `R2_no_wordsem_tag` by 754 out of 109,050; the ~40% lemma-level rate and the
  ~11% `m_wordsem` ceiling are unchanged. FINDINGS §465 updated;
  [`PWG_SENSE_DCS_FRAME_COMPARISON.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_FRAME_COMPARISON.md)
  carries the correction (it had also named Kathāsaritsāgara as a text DCS lacks — DCS
  carries it, 111,298 tokens).

### Added
- **H1670 — measurement harness + crosswalk backlog.** `pwg_sense_dcs_attestation_pilot.py`
  gains `--frame-mode file` / `--frame` / `--concordance`, and reports exact-verse grounding
  separately from adhyāya/hymn corroboration (`locus-chapter`), so neither can be quoted
  without the other; of H1632's 52 grounded senses only **5** were exact-verse.
  New [`build_ls_text_crosswalk_backlog.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/build_ls_text_crosswalk_backlog.py)
  classifies all 739,503 `<ls>` citations: 36.4% mapped, **13.9% point at texts DCS carries
  but the aligner never mapped** (443 abbrevs — the queue for
  [H1691](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1691-Opus_kosha_pwg-dcs-text-crosswalk-beyond-five_26.07.26.md)),
  49.7% at texts DCS genuinely lacks. Untagged corpora (wisdomlib) are reported as a
  lemma-level lever only and were deliberately not consumed here.

## [1.77.0] — 2026-07-26

### Added — H1656 follow-on: Gorresio e-text recovered; Rāmāyaṇa citation reuse ON (26-07-2026)

- **MG ruled: reuse always ON by default** — the validation gate is an audit, not a
  months-long blocker. And the "no Gorresio OCR exists" premise fell the same day:
  the Cologne [ramayanagorr](https://github.com/sanskrit-lexicon-scans/ramayanagorr)
  page PDFs carry an embedded Google **text layer**. New `build-gorresio` subcommand
  ([src/build_ramayana_concordance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py))
  extracts the full **Gorresio e-text**
  ([src/gorresio_etext.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gorresio_etext.jsonl),
  10,225 verses) and builds a **CONTENT-BASED Gorresio↔Southern verse concordance**
  ([src/ramayana_gorresio_southern_verse_map.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_verse_map.tsv)):
  **4,066 verses mapped** (1,857 matched + 2,209 fuzzy), 4,955 Bengal-only, 200
  `moved` excluded. All scan-verified gold anchors reproduce. `citation_tm` resolves
  R. GORR. + plain R. books 3–6 through the map — hits carry `map` class+score;
  misses are typed (`no-southern-counterpart`, `gorresio-etext-gap`). Vols 2/4/uk
  (image-only scans) → [H1689](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1689-Opus_SanskritLexicography_gorresio-vols-2-4-uk-ocr-etext_26.07.26.md).

### Fixed — shingle phase-parity bug in the concordance aligner (26-07-2026)

- Candidate retrieval indexed AND probed shingles on the same stride, so shared runs
  at an off-phase relative shift were invisible — G 1,22,1 ↔ S 19,1 scored 0.774 yet
  was never retrieved. Index now covers every offset. Southern↔Critical rebuilt:
  **81.4% matched/fuzzy** (was 74%). See
  [FINDINGS §470](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  (text-layer discovery) and Uprava FINDINGS §213 (the stride trap).

PRs: [#784](https://github.com/gasyoun/SanskritLexicography/pull/784) (+ [#769](https://github.com/gasyoun/SanskritLexicography/pull/769) in v1.73.0) · Handoff: [H1656](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1656-Opus_SanskritLexicography_gorresio-southern-critical-concordances_26.07.26.md) · Model: Fable 5 (`claude-fable-5`)

## [1.76.0] — 2026-07-26

### Added
- **H1664 — voting-queue triage: a verdict for every pending review sheet (26-07-2026).**
  Fable 5 (`claude-fable-5`). All 42 pending sheets (2,962 queued human judgments) ruled
  AGENT-RULEABLE (1) / HYBRID-В2 (20) / HUMAN-ONLY (21), each with its enabling dataset,
  in [VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md);
  human bill drops to ~1,329 (−55 %) once the routed adjudications (H1681–H1688) execute,
  on top of the acc_ncc lane already banked by H1657 — post-H1671 key repair: 10,614 Tier C/D rows agent-adjudicated, human owes the fresh blind 698-card sample. SL lanes routed:
  compound-`differs` В2 (H1681), h1303 abbrev rule-collapse (H1682), article-comparison
  source-check (H1683). Detail table:
  [RussianTranslation/RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

### Fixed
- **H1671 — the NCC `match_key` case bug is repaired and the whole ACC×NCC pipeline
  re-ran on corrected keys (26-07-2026, closes [integrity issue #779](https://github.com/gasyoun/SanskritLexicography/issues/779)).**
  [`parse_ncc.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/parse_ncc.py)
  transliterated the *capitalised* NCC headword, and `sanskrit_util.to_slp1` is
  case-preserving — so the capital fell through into the SLP1 string where
  `slp1_simplify` read it as a different phoneme (`Rāmāyaṇa` → `namayana`). **91,548 of
  152,526 keys (60.0%) were wrong.** `match_key_for` now case-folds + NFC-normalizes
  first, pinned by a new
  [`test_parse_ncc.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/test_parse_ncc.py)
  that asserts both the correct key and the absence of the specific corrupt one.
  P0 → P1 → P2 re-ran end to end: **exact-key overlap 8,397 → 22,775** distinct keys
  (+14,379 pairs that were never proposed, because the corrupted key changed P1's
  blocking letter), Tier D **43,666 → 1,575** rows as its 40,757 disguised exact matches
  moved up to Tier A, the Tier C/D adjudication set **49,019 → 10,614**, and
  `works_crosswalk.tsv` **120,241 → 249,802** rows (⚠️ a +107.7% delta for kosha, which
  consumes it). All 3,711 candidate rows the repair *removed* are individually accounted
  for and none was a true link. H1657's 686-card spot-check sample is **void** (never
  voted, so no human work lost) and is replaced by a fresh blind 698-card sample over 17
  strata; nothing is promoted until a human rules the precision bar. Full before/after:
  [`NCC_KEY_REPAIR_MIGRATION_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/NCC_KEY_REPAIR_MIGRATION_2026.md).

### Changed
- **`to_slp1`'s uppercase passthrough audited across the org (H1671).** Ruling: keep
  `to_slp1` byte-compatible rather than lowercasing inside a transcoder shared by ~8
  repos, and make the trap loud instead — the behaviour is undocumented and untested, not
  wrong. Recorded in [`FINDINGS.md` §469](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  with the call-site table: `sanskrit_util.iast_to_devanagari` and two csl-atlas call
  sites already defend with a silent `.toLowerCase()`; csl-apidev's `rowSlp1()` is the one
  undefended caller found (a user typing `Rāma` searches for `RAma`).
- **`adjudicate_p2.py` no longer carries its own copy of the key repair**, delegating to
  `parse_ncc.match_key_for` so the two cannot drift; its `ncc_key_was_corrupt` field is now
  the invariant proving P0 shipped repaired keys (0.0% on this run, was 87.7%).
- **`build_works_crosswalk.py`'s Tier A cross-check reads P0's measured figure** from
  `P0_COUNTS.md` instead of a hardcoded `8397` — that constant silently went stale the
  moment the keys were repaired, and a cross-check that cannot notice its own reference
  value has drifted is not a cross-check.

## [1.75.0] — 2026-07-26

### Added
- **H1657 — ACC×NCC P2 agent adjudication of all 49,019 Tier C/D rows (26-07-2026).**
  Per MG's ruling В2, the adjudicator moves from a human to an agent while the
  09-07-2026 full-coverage ruling stands: every row carries a verdict with cited
  evidence (41,947 approve / 7,072 reject, zero skipped), emitted by
  [`adjudicate_p2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/adjudicate_p2.py).
  A blind 686-card stratified sample over 16 strata
  ([`build_p2_spotcheck_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/build_p2_spotcheck_sheet.py))
  measures the adjudicator, and
  [`p2_precision_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/p2_precision_gate.py)
  publishes Wilson 95% lower bounds per stratum and gates promotion — it refuses to
  run without an explicit `--bar`, because the threshold is a human ruling.
  **Nothing is promoted yet:** all 49,019 rows sit in
  `works_crosswalk_agent_proposed.tsv` awaiting that ruling. Report:
  [`P2_AGENT_ADJUDICATION_REPORT.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P2_AGENT_ADJUDICATION_REPORT.md).

### Fixed
- `apply_p2_decisions.py` gained a third destination (`works_crosswalk_agent_proposed.tsv`)
  and a provenance passthrough, so an ungated agent verdict can never be mistaken for a
  promoted crosswalk row. `build_p2_sheet.py` was refactored behind a `main()` guard and
  now exports its renderer, so the spot-check sheet reuses it instead of forking a copy.

### Changed
- ⚠️ **P0/P1 are documented as running on corrupted NCC keys.**
  [`parse_ncc.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/parse_ncc.py)
  transliterates the capitalised NCC headword, and `sanskrit_util.to_slp1` is
  case-preserving, so uppercase IAST initials are read as different SLP1 letters
  (`Rāmāyaṇa` → `namayana`). **60.0% of NCC match-keys are wrong**; 93.3% of Tier D is
  an artefact of it and **14,379 true exact matches were never proposed as candidates**
  (exact overlap is 22,775 keys, not 8,397). Filed as
  [integrity issue #779](https://github.com/gasyoun/SanskritLexicography/issues/779),
  recorded as [FINDINGS §468](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md),
  repair queued as
  [H1671](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1671-Opus_SanskritLexicography_acc-ncc-p0p1-ncc-key-repair-rerun_26.07.26.md).
  Nothing published is wrong — it is incomplete, and `ROADMAP_ACC_NCC.md` now says so.

## [1.74.0] — 2026-07-26

### Fixed — "a bigger corpus" was the wrong lever for H1632 constriction 1 (26-07-2026)

- The H1632 frame-comparison report and SL FINDINGS §465 said the 60.2% of PWG
  headwords absent from DCS needs "a bigger corpus". **Misleading as written**
  (MG): *DCS already is the largest **tagged** Sanskrit corpus*; the corpora that
  are bigger carry **no markup** — wisdomlib, currently under scrape.
- Both now state the split precisely: an untagged corpus **can** raise
  *lemma-level* attestation (shrinking the "absent everywhere" class) but
  **cannot** raise *sense-level* grounding, since there are no sense tags to bind
  to. Conflating the two is a category error; the rates stay in separate tables.
- Points at the existing `wl` wisdomlib period-state signal (§14) so a second
  wisdomlib lane is not opened, and at the Cloudflare constraint before any scrape.
- Follow-on work minted as
  [H1670](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1670-Opus_SanskritLexicography_pwg-dcs-sense-grounding-scale-levers_26.07.26.md):
  the only real levers on the sense-level number are running the H1455 aligner
  past its own 500 headwords, and adding texts / locus crosswalks.

### Added — H1666: Wave-2 coverage monitor + monthly cloud routine (26-07-2026)

- [`research/WAVE2_COVERAGE_MONITOR.md`](research/WAVE2_COVERAGE_MONITOR.md) tracks
  `verb_worklist.py`'s promoted/749-DCS-root % against
  [ROADMAP_ACL_LESSONS_2026.md](research/ROADMAP_ACL_LESSONS_2026.md)'s Wave-2
  "~50% coverage" trigger — currently 48/749 ≈ 6.4%, stalled since 04-07-2026. A
  monthly `claude.ai` cloud routine (RemoteTrigger) recomputes and appends a row,
  and flags a GTD `@DECIDE` in Uprava once coverage crosses 50%. Registered in
  `research/README.md`'s Living monitors table.

## [1.73.0] — 2026-07-26

### Added — H1656 Rāmāyaṇa recension concordances (Gorresio↔Southern + Southern↔Critical) (26-07-2026)

- MG ruled 21-07-2026 (weekly `@DECIDE`): build the Gorresio↔Southern concordance —
  «NEVER propose to skip» citation reuse. New
  [src/build_ramayana_concordance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py)
  builds three committed, metadata-only TSVs: the **Gorresio structural inventory**
  (672 sargas, verse counts + volume/page, from the Cologne
  [ramayanagorr](https://github.com/sanskrit-lexicon-scans/ramayanagorr) scan-viewer
  page index — no OCR chased, none exists), the **Southern↔Critical verse
  concordance** (18,993 Southern verses vs DCS critical, content-based, 74%
  matched; 98.7% agreement with the H783 Sundara concordance), and a
  **Gorresio↔Southern sarga map** (DTW over verse-count profiles,
  DRAFT-STRUCTURAL: 319 plausible / 212 weak / 165 unpaired). Selftest wired into
  the CI gates job. R. GORR. stays `unmapped_locus_scheme` until the validation
  gate in [pwg_ru/COVERED_TEXTS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/COVERED_TEXTS_RU.md)
  § R. GORR. passes (≥30-pair scan spot-check + human review sheet).

### Fixed — plain R. books 3–6 are Gorresio-keyed; resolver was silently wrong (26-07-2026)

- **Integrity find (H1656, [issue #770](https://github.com/gasyoun/SanskritLexicography/issues/770)):**
  PWG's plain `R.` is a three-edition composite (pwgbib 1.247): books 1–2 Schlegel,
  **books 3–6 Gorresio (Bengal recension)**, book 7 Bombay. Verified against the
  store's cited sarga ranges (R. 3 → 79, R. 4 → 63, R. 5 → 94 = exactly Gorresio's
  counts; Southern has 75/–/68). `citation_tm.py` keyed in-range book-3/5 loci into
  the Southern corpus and returned the **wrong verse's RU translation** silently —
  ~900 refs exposed. Books 3–6 now return `unmapped_locus_scheme` (selftest fixture
  added) until the Gorresio↔Southern concordance validates. ~2,200 refs total ride
  on that concordance (657 R. GORR. + ~1,560 plain-R. books 3–6). Full write-up:
  [FINDINGS.md §468](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

PR: [#769](https://github.com/gasyoun/SanskritLexicography/pull/769) · Handoff: [H1656](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1656-Opus_SanskritLexicography_gorresio-southern-critical-concordances_26.07.26.md) · Model: Fable 5 (`claude-fable-5`)

## [1.72.0] — 2026-07-26

### Added
- **H1633 human gold-cut design + A51 methods packet (26-07-2026).** First sampling
  design for a human-measured DE→RU store precision figure
  ([RussianTranslation/gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md),
  n=400 recommended, 12 strata, tiered κ plan with no invented metrics, parked for
  sign-off) + the A51 methods-section draft with a 10-row claims register
  ([RussianTranslation/pwg_ru/A51_METHODS_DRAFT_DE_LAYERS_RU_PIPELINE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/A51_METHODS_DRAFT_DE_LAYERS_RU_PIPELINE.md)).
- **H1491 Leonchenko Sinonimy evidence lane** (see RussianTranslation/CHANGELOG.md).

## [1.71.0] — 2026-07-26

### Added
- **First intrinsic BLI quality gate for RussianTranslation's `corpus_lexicon.jsonl` (H1521, 26-07-2026).**
  [`RussianTranslation/src/eval/bli_eval.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/bli_eval.py)
  streams the 1.09M-pair Sa→Ru lexicon and scores P@1/MRR/coverage against a frozen
  400-lemma gold set built from the independent Kochergina dictionary + VisualDCS's
  independent frequency ranking (the corpus's own 3-layer glossary was rejected as a
  gold source — it is derived FROM `corpus_lexicon.jsonl`, so grading against it would
  be circular). **Result: P@1 = 0.402, MRR = 0.539, coverage = 0.995 (398/400)** — the
  lexicon's first quantitative quality number. Fixture selftest wired into CI.

## [1.70.0] — 2026-07-26

### Added

- **Selftest isolation guard — production data unreachable by construction (26-07-2026).**
  New [`selftest_isolation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/selftest_isolation.py),
  wired into all 10 selftests that can reach the store, coordinator or residual registry.
  **Belt:** pin every redirectable production path to scratch before any repo import (several
  modules resolve those constants at import time); a path pointing *inside* the checkout is a
  hard refusal, not a silent override. **Braces:** an exit tripwire over the production files
  that have no override — the C-49 residual ledger's path is computed from `__file__`, which is
  why [#726](https://github.com/gasyoun/SanskritLexicography/issues/726) was possible — failing
  the run even when every assertion passed. Verified by reproducing #726 against it: the fixture
  passed every assertion and the run still exited 9 naming the modified file.

### Fixed

- **[#760](https://github.com/gasyoun/SanskritLexicography/issues/760) — in-process promotion
  made `window_selftest` reach the LIVE canonical store.** `coordinator.promote_ready` now calls
  `promote_final_cards.batch_promote` in-process instead of shelling out to `--batch-manifest`;
  the promotion fixtures' isolation *was* that subprocess boundary, and `DEFAULT_STORE` resolves
  to the main worktree's real `pwg_ru_translated.jsonl` unless `PWG_RU_STORE` is set. The tests
  read the live ~11.6k-row store and, on a fixture whose sense identities did not collide, would
  have written it. Closed by the guard above.
- **The 7 coordinator/promotion fixtures the sealing invalidated.** Preflight evidence and
  sealed-v2 binding are mandatory now; the fixtures still passed placeholder paths and v1
  outputs. Five were contract updates (a real self-validating preflight artifact, explicit
  cost-gate schema, `--result-sha256`, a fake that answers `perf_preflight.py`, sealed meta on
  the *workflow output* rather than the manifest). The sixth — the P10 "TM rebuild in a
  `finally`" test — was **rewritten**: promotion is journal-phased now, so the TM survives a
  post-commit failure *by construction* rather than via a `finally`, and the test pins that
  instead of a shape the code no longer has. `window_selftest` **189/189**.

## [1.69.0] — 2026-07-26

> Version numbering follows the repository's **git tag** sequence (…v1.67.0,
> v1.68.0), which had drifted ahead of the version headings in this file (last
> heading was `[1.62.0]`). Continuing the tag sequence, per `/cut-release`.

### Added — H1632 scale-up: unbiased random frame + full-PWG run (26-07-2026)

- The original H1632 pilot ran on a frame **selected DCS-attested**, so its "100%
  attested at lemma level" was true by construction. Two unbiased frames now
  answer the question it could not — a seeded random sample (2,000 groups) and
  **every PWG headword (109,050 groups)**. Synthesis:
  [research/PWG_SENSE_DCS_FRAME_COMPARISON.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_FRAME_COMPARISON.md).
- **Lemma-level attestation is ~40%, not 100%.** 43,352 / 109,050 PWG headword
  groups (39.8%) have a DCS lemma — so **60.2% have no DCS attestation at any
  granularity**. The 2,000-group sample estimates 40.4% (±2.2% at 95%) and its
  interval covers the population value, validating the sampling frame.
- **The sense-tag ceiling is a corpus property, not a frame artefact** — 10.8% /
  11.9% / 11.2% of DCS token mass across the three frames.
- **Grounding is reported as *unknown*, never as zero.** The H1455 aligner covers
  500 of 109,050 groups; the rest are classed `R0_grounding_not_computed`.
  Publishing 0% there would manufacture a dictionary-wide rate out of the absence
  of a job. Selftest asserts the join rates come back `None`, not `0.0`.
- New `--frame-mode kosha|random|all` (+ `--n`/`--seed`) on the pilot script,
  `--all` on the loci exporter, and
  [research/compare_frames.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/compare_frames.py),
  which reads the three `meta.json` files so the synthesis cannot drift from the runs.

### Added — edition-diff reading surface over edition_rel (H1631, N14 pilot, 26-07-2026)

- New
  [`src/pilot/build_edition_diff_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_edition_diff_site.py):
  a fixture-driven static page showing the PWG sense skeleton with PW/SCH/PWKVN/NWS
  supplements attached at their `edition_rel` insertion point, each badged with its
  H1624 G4 subtype (`base`/`restate`/`pw_correct`/`sch_star`/`derived_sense`/`a2a`/
  `nws_at_sense`/`foreign_fragment`) — no new typology, no re-translation, DE text
  read-only. `--selftest` uses a synthetic fixture (never real store content — N9) and
  is wired into CI. See [RESULTS_LOG.md](RESULTS_LOG.md) 26-07-2026 for the pilot
  subtype counts (7 REGLUE_SPEC roots, 1077 rows). Partial N14 close — see
  [`pwg_ru/REGLUE_SPEC.md`](pwg_ru/REGLUE_SPEC.md) Sec.7.

### Added — H1632 PWG-sense × DCS attestation pilot join (26-07-2026)

- New
  [research/PWG_SENSE_DCS_ATTESTATION_PILOT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_ATTESTATION_PILOT.md)
  + generator
  [research/pwg_sense_dcs_attestation_pilot.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_sense_dcs_attestation_pilot.py)
  and input builder
  [research/export_frame_sense_loci.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/export_frame_sense_loci.py):
  the first join of **PWG's own sense divisions** to DCS attestation *and*
  frequency, on the frozen H1455/H1456 500-headword frame.
- **The number: sense-level attribution collapses.** 500/500 groups attest at
  lemma level (by construction — the frame was selected DCS-attested), but only
  **52 of 7,746 PWG leaf senses (0.67%)** are grounded to a DCS attestation by a
  shared locus. 10.8% of the frame's 943,877 DCS tokens carry a `m_wordsem` tag
  at all — that is the ceiling on *any* sense-level claim over this corpus.
- **Two ceilings separated.** 12,953 `<ls>` citations hang on structural parent
  sense nodes, unattributable to a leaf sense by PWG's own structure — before DCS
  is consulted at all. The corpus-side residue (86.8% of groups, class `R3`) fails
  on missing texts and vulgate↔BORI locus drift, not on absence of evidence.
- Reuses, never rebuilds: H1453 `sense_frequency.tsv` (`wn` = `m_wordsem` gold),
  H1455 `sense_corpus_concordance.tsv`, H1456 `microstructure.leaf_senses`.
  Deterministic, no LLM in the measurement path; all five inputs SHA-256 pinned.

### Hardened — Codex pipeline-hardening audit, step 1 of 2 (26-07-2026)

- New
  [PIPELINE_HARDENING_AUDIT_2026-07-25.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HARDENING_AUDIT_2026-07-25.md):
  a current-code audit of the single-Max-account headless route, its
  coordinator/audit/promotion boundary, and the offline orchestration cost —
  with the actual one-profile call graph and P0/P1/P2 findings.
- **Two P0-class fixes landed from it.** (1) A Windows timeout could leave a
  **paid descendant alive**, so a killed generation attempt risked an orphaned
  grandchild still burning quota —
  [`proc_tree.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py)
  tree-kill hardening. (2) An unguarded `future.result()` in the threaded audit
  gates meant one worker exception lost the **whole durable audit report**; it now
  becomes a durable rc=3 gate result that conservatively requeues that gate's
  exact keys, and an NWS-quarantine replace failure preserves the previous
  destination instead of destroying it.
- The audit's own release verdict stands: **live promotion is NO-GO** until the
  store/coordinator/TM close seam has a durable journal and startup
  reconciliation. That sealing is **step 2** — it invalidates 7 existing fixtures
  that still pass placeholder preflight paths and v1 outputs, tracked in
  [pwg_ru/CODEX_HARDENING_REBASE_STATUS_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/CODEX_HARDENING_REBASE_STATUS_2026-07-26.md).

### Added — DE edition-graph export profile: OntoLex-Lemon + TEI Lex-0 (H1629)

- New
  [src/export_de_edition.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py):
  serializes the **German** edition graph — one entry per (key1, homonym) over the
  PWG/PW/SCH/PWKVN/NWS editions — carrying all five H1624 layers (`gloss_lang`
  spans G1, `government` G2, `form_notes`, `citation_edges` G3, `edition_rel` G4)
  as OntoLex-Lemon Turtle **and** TEI Lex-0 XML, plus a manifest. Federates with
  the existing RU / DCS-frequency / grammar graphs on the shared `lemma/<key1>` IRI.
- Rights fence (N9): input allowlist → Cyrillic quarantine → post-serialization
  guard on the emitted bytes. The store's `h` field is deliberately excluded (it
  carries Russian prose); a Russian `sense_tag` is reduced to its ASCII skeleton
  and logged in the manifest rather than exported.
- Golden fixture
  [release/fixture/de_edition/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/fixture/de_edition)
  from a 22-row DE-only fixture that exercises every layer and every edition
  layer; `--selftest` fails if any layer's count drops to zero, if a TEI pointer
  dangles, or if the output stops being byte-deterministic.
- Mapping + provenance + limitations:
  [DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md)
  (+ metadoc). LANG_PARITY entry `de_edition_export_profile_h1629` (SHARED).
- **Not** done: TEI Lex-0 ODD validation (structure-checked only), RDF-parser /
  SHACL round-trip, full-store run, base-IRI `@DECIDE`.

### Documented — data-integrity findings surfaced by the DE export (H1629)

- Measured and reported, **not** silently worked around: 11 store rows carry
  Russian tokens inside the German `de` field; ~110 rows carry Russian
  `sense_tag` prose; and the G1 `gloss_lang` classifier mislabels ~122 of 229
  non-DE spans as Latin/English (77% false-positive rate on the
  `english_content` rule), which also masks those German glosses out of the
  translate path upstream. See
  [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  and the tracking integrity issues
  ([#749](https://github.com/gasyoun/SanskritLexicography/issues/749),
  [#750](https://github.com/gasyoun/SanskritLexicography/issues/750)).

### Documented — German-side editorial principles datasheet (H1634)

- New
  [pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md)
  (+ metadoc): field inventory after H1624 G1–G6 — **derived / voted / undecided**
  with confidence, design fence, G5 (H1306) and G7 (Palsule) blockers, form_notes
  and form_labels. Cross-linked from [pwg_ru.md](pwg_ru.md) §8.0 / §8.4 and deep
  manual §2c.
- Does **not** invent style or abbrev policy; does not rewrite the store.

## [1.68.0] — 2026-07-26

### Added
- **Machine-flag layer in the review-sheet gate + G5 batch1v3 (H1655, P1 ruling 26-07-2026).**
  MG ruled the voting-queue triage `@DECIDE` «auto-reject»: a card carrying a machine-findable
  store flag never reaches a human sheet. `review_residue_gate.machine_flags` now detects the
  screening-audit classes — D1 Cyrillic inside `{#...#}` (20 queue rows), D3 gloss-wrapper
  drift to guillemets (370), D4 DE↔RU gloss-slot count mismatch (3,236 total with D-classes;
  flag-only, waits for [H1651](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1651-Sonnet_SanskritLexicography_pwg-ru-wrapper-defect-sweep-d1-d4_26.07.26.md)
  triage) — and `build_g5_review_sheet.py` applies it as a second hard pre-filter. Eligible
  pool: 7,286 of 11,163. batch1v2 (German-only gate) superseded UNVOTED by
  `g5-live-queue-batch1v3-2026-07-26` (150 cards, verified 0 leaks across both layers); the
  v2 lock is removed so a stray v2 export can no longer validate. D5 (gloss byte-identical to
  German) deliberately not flagged — audit-measured as mostly false positives.
## [1.67.0] — 2026-07-26

### Added
- **Reader-visible German-residue gate for review sheets (H1655, 26-07-2026).** MG aborted
  G5 live-queue batch 1 at 5/150 votes: cards reached the human with visible German. New
  [`review_residue_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_residue_gate.py)
  (H1302 prose scan class-b + H1303 `ab`-token classification vs `RU_MAP` + `ls`-tail
  `fg./fgg.`) now hard-filters every candidate BEFORE it reaches a sheet; live-queue sweep
  flagged 637/11,163 (5.7%). `build_g5_review_sheet.py` also renders the RU panel as print
  shows it (`RU_MAP` applied, original in tooltip) with raw markup in a second panel, skips
  already-decided cards, and shipped batch1v2 (`g5-live-queue-batch1v2-2026-07-26`, 150
  cards, all verified German-free). H1404 selftest lane (binding · validate · apply ·
  residue gate · H1302 scan) wired into CI. Audit:
  [decisions_applied_2026-07-26_g5-batch1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-26_g5-batch1.md).

### Fixed
- **Positional review-ids drift across store generations (H1655, 26-07-2026).** `row:NNNNNN:`
  review-ids embed the store line position at queue-mint time; the store grew 11,163 → 11,603
  between queue mint (06-07) and vote apply (26-07), so 2/5 batch-1 votes resolved to
  nothing. `run_batch.py` review lookups (`validate_review` / `review_report` /
  `apply_review`) now fall back to the stable `subcard:<sub>#<tag>` tail when the positional
  prefix is stale (ambiguous tails refused, never guessed); pinned by a drift case in
  `apply_decisions.py --selftest`.

## [1.66.0] — 2026-07-26

### Fixed
- **P0 — a Windows timeout could leave a PAID descendant alive (26-07-2026).** Landed from the
  Codex hardening branch, step 1 of 2:
  [`proc_tree.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py)
  tree-kill hardening — a killed generation attempt no longer risks an orphaned grandchild
  still burning quota. Pinned by the existing D-J tree-kill selftest.
- **An audit-gate worker exception could lose the whole durable report (26-07-2026).** Landed
  from the same branch: an unguarded `future.result()` in the threaded gates now becomes a
  durable rc=3 gate result that conservatively requeues that gate's exact keys, and an
  NWS-quarantine replace failure preserves the previous destination instead of destroying it.
  Pinned by two new tests. Classified **INTENTIONAL-DIVERGENCE** in
  [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md):
  RU-only *by construction* — the EN twin runs no threaded gate and has no NWS quarantine, so
  neither mechanism exists there to harden.

### Added
- **The Codex pipeline-hardening audit** —
  [`PIPELINE_HARDENING_AUDIT_2026-07-25.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HARDENING_AUDIT_2026-07-25.md):
  the one-profile call graph plus the P0/P1/P2 findings behind this work. Step 2 (coordinator +
  promotion sealing, and the 7 fixtures it invalidates) is tracked in
  [`pwg_ru/CODEX_HARDENING_REBASE_STATUS_2026-07-26.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/CODEX_HARDENING_REBASE_STATUS_2026-07-26.md)
  and draft [PR #744](https://github.com/gasyoun/SanskritLexicography/pull/744).

### Added

## [1.65.0] — 2026-07-26

### Added
- **Heritage (INRIA) frequency-tables ingest + diff (26-07-2026, H1490).** Roadmap
  Phase 3: 7 `DATA/*.tsv` files decoded out of Heritage's internal WX romanization
  (new WX→SLP1 transcoder) and diffed against VisualDCS's M1–M8 `dcs_full.sqlite`
  and `RussianTranslation/src/corpus_lexicon.jsonl` — Spearman ρ 0.70–0.74 vs DCS
  across surface-form/lemma/compound-stem series, 0.53 vs `corpus_lexicon`.
  [`heritage_frequency_diff.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_frequency_diff.md) /
  [`.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_frequency_diff.tsv) /
  [`heritage_freq_diff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_freq_diff.py).

## [1.64.0] — 2026-07-25

### Added
- **Editorial-principles datasheet for the H1624 German-side layers (25-07-2026, H1634).**
  [`pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md)
  states, per G1–G6 field, whether it is deterministic extraction (`derived`), waiting on a
  human vote (`voted` — G5 H1306 tags, unratified), or derived-with-an-undecided-flag (G6
  `needs_human`, measured 4,226/39,539 = 10.69% compound-split disagreement, never
  auto-adjudicated). Cross-linked from
  [`pwg_ru.md` §8.0](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md)
  and
  [`RUSSIANTRANSLATION_DEEP_MANUAL.md` §2c](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md).
- **Gate-0 probe is profile-parameterised (25-07-2026).**
  [`h963_c4_gate0_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py)
  takes `--account` / `--config-dir` (c4 remains the default and is byte-unchanged in behaviour),
  so the serial multi-profile assessment `/pwg-live-gate` already specifies no longer needs a copy
  of the script per profile. Each account keeps its OWN events log and campaign label — sharing
  one across profiles would re-create the #729 contamination a level up, a c5 row answering for a
  c4 verdict. A missing profile dir or absent credentials is refused BEFORE any call, as a
  provisioning state rather than a health reading (free — no paid `profile_status` call).
  Selftest 7/7.
- **First c5 gate reading — `HEALTH_NOGO`, and it is orthogonal to c4's.** c5 warm-up 59 651 ms /
  measured 52 960 ms, both `success` with real output and zero connection errors, both ~2× the
  30 000 ms ceiling; c4 the same day was `rate_limit` with healthy 17.9–19.9 s latency. c4 has
  headroom but no quota, c5 has quota but no speed — **swapping profiles does not unblock the
  window**. Packet:
  [`pwg_ru/h858/H858_C5_LIVE_GATE_HEALTH_NOGO_2026-07-25.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h858/H858_C5_LIVE_GATE_HEALTH_NOGO_2026-07-25.md).

## [1.63.0] — 2026-07-25

### Fixed
- **#729 — the c4 health gate could pass on a stale reading (25-07-2026).**
  [`h963_c4_gate0_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py)
  pinned a CONSTANT `RUN_ID`, appended to that one bucket and re-read it keeping the last
  row per purpose — so a run could pair its own warm-up with a **stale** `measured` from days
  earlier. Observed harmlessly (a NO-GO citing a 23-07 reading of 168 352 ms for a call never
  made); the hazard is the inverse, where a stale *passing* measured yields
  `GATE-0 VERDICT: PASS` → `LIVE_GO` → authorized paid spend off a two-day-old number.
  The run id is now minted per invocation and the reader matches it exactly; the old constant
  survives as `CAMPAIGN`, a grouping label the H1110/H1447 reports cite, never a read scope.
  Verdict derivation extracted to a pure `derive_fails()`; module `--selftest` seeds the exact
  hazard log and proves both halves; pinned by `window_selftest.test_c4_gate0_probe_run_scope`
  (**186/186**). Importing the module no longer fires a paid probe.

## [1.62.0] — 2026-07-25

### Fixed
- **Gate-probe integrity, reported not yet repaired (25-07-2026).** A `/pwg-live-gate c4` run
  for the H858 validation window returned **HEALTH_NOGO** (c4 `rate_limit` on the warm-up,
  17 878 ms — not a latency block) and, in doing so, exposed that
  [`h963_c4_gate0_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py)
  hardcodes `RUN_ID`: it re-reads the whole append-only history and keeps the last row per
  purpose, so a run can pair its own warm-up with a **stale** `measured` reading. Today that
  only mis-stated a NO-GO reason; the inverse would print `GATE-0 VERDICT: PASS` off a
  two-day-old number and authorize paid spend ([#729](https://github.com/gasyoun/SanskritLexicography/issues/729)).
  Gate packet:
  [`pwg_ru/h858/H858_C4_LIVE_GATE_HEALTH_NOGO_2026-07-25.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h858/H858_C4_LIVE_GATE_HEALTH_NOGO_2026-07-25.md).

## [1.61.0] — 2026-07-25

### Added
- **H858 Part B — source-anchored repair of a dropped `german` span (Opus 5 `claude-opus-5`, 25-07-2026).**
  New [`RussianTranslation/src/german_anchor.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/german_anchor.py):
  a card whose `german` echo dropped a masked `{Tn}` span is repaired from the source skeleton
  instead of being nulled by the `<ls>`/`{#` fidelity count — the dominant retry-RESISTANT null
  class (6 of 7 residual nulls in `no_pwg_w10`, H1283; a `--max-wide` requeue provably cannot fix
  it). Repair-then-verify (runs only on a card that already failed the count, the same count re-run
  as the verifier, so a passing card is byte-untouched) and refused unless the echo is a strict
  order-preserving subsequence of the source. Wired into both lanes from ONE authored source —
  `headless_worker.normalize_batch` (production) and the harness `accept()` via
  `german_anchor.js_source()`, the C-01/C-17 injection pattern. Every repair is stamped into the
  promoted row's provenance (`german_anchor`) and counted in `summary.german_anchor_repairs`.
  SHARED in [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md).
  Offline-green on both lanes (`window_selftest` 185/185, `german_anchor_test.js`,
  `headless_worker_selftest`, `promote_final_cards --selftest`); the handoff's live no_pwg
  validation window is PAID and stays gated on a fresh live-gate GO.

### Fixed
- **`window_selftest` polluted the tracked residual registry (integrity, 25-07-2026).** The
  coordinator-requeue test ran a real `--defect` requeue without `--no-residual`, so every suite
  run appended a junk `{"key": "a", "source_window": "nominal_selftest"}` row to
  [`no_pwg_residuals.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_residuals.jsonl)
  — the registry that decides which keys are BLOCKED from requeue. Flag added; the polluting row reverted.
### Added

- **PWG→RU paid-route and promotion hardening (unreleased implementation,
  25-07-2026; no paid translation started):** all probes and generation calls
  now share a durable `pwg.call_reservation.v1` ledger. `max_calls` is consumed
  atomically before each process spawn and is never refunded after a crash;
  `--cost-ceiling` is explicitly an observed-cost stop after completed calls,
  not a strict pre-spend dollar cap, and missing/invalid cost telemetry stops
  cost-capped runs as unevaluable. The same profile lock covers each warm-up +
  measured probe pair and each worker generation run. Paid manifest-v2
  dispatch also binds the run ID, manifest hash, preflight hash/scope, profile,
  result hash, and reservation ledger before output can be recorded.
- **PWG→RU crash closure (unreleased implementation, 25-07-2026):** Windows
  Claude subprocesses are placed in a kill-on-close Job Object before their
  first instruction, so timeout/exception cleanup reaches the native child
  tree. Sequential `record-output-batch` reports its exact durably committed
  prefix. Promotion now uses `pwg.promotion_journal.v1`
  (`prepared → store_committed → derived_validated →
  coordinator_committed → complete`), startup-reconciles the single incomplete
  journal, holds one canonical-store claim through `complete`, and seals the
  store, backup, TM/denylist, coordinator state, and deterministic promotion
  registry identities for idempotent recovery. Store or coordinator bytes that
  match neither sealed before nor expected-after state fail closed.

### Changed
- **H1623 docs-freshness (Grok 4.5 grok-4.5, 25-07-2026):** re-verify big-manuals estate — LAST_VERIFIED 25-07-2026 on workspace AGENTS/HUMAN_RU + 6 docs/manuals deep manuals; RT deep metadoc COMMANDS_SPOT_RUN forced to integer 4 (was free-text, broke manual_staleness.py); MAINTAINER papers range updated A30-A67.

## [1.60.0] — 2026-07-24

### Added

- **H1618 unpaid four tracks (pwg_ru control plane).** Offline multi-profile
  [`cohort_engine.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cohort_engine.py)
  (7/7 fake-worker pins); C-49
  [`no_pwg_residual_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_residual_ledger.py)
  + residual backfill; FEATURES_INDEX **L11**.

### Fixed

- **max-agents starvation footgun (H1610 forensics → H1618 guard).** `--max-agents N` is a
  total spawn ceiling; multi-key `N < selected_keys` is refused before paid calls; soft
  selfheal stamps no longer clobber `budget_exceeded*` notes. Ledger stamps
  translate/heal/`budget_stops`. EN audit wires wall_clock metrics + defect fsha emit.

## [1.59.0] — 2026-07-24

### Added

- **Definition typology classifier WS2.4 (H1483).** Rubric + **all 44 csl-orig dicts / 1,496,157 records** (`--all`) + stratified gold **55/79 = 69.6%** (after linear apparatus strip; ACC citation-chain hang fixed). Report [`data/DEFINITION_TYPOLOGY_WS2_4_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/DEFINITION_TYPOLOGY_WS2_4_2026.md); script [`data/definition_typology_classifier.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_classifier.py). FEATURES_INDEX **E49**; README + metadoc registered.

- **Markup-tag heatmap + RU-gloss gap cards (H1527).** Offline single-file HTML under
  [`data/viz/`](https://github.com/gasyoun/SanskritLexicography/tree/master/data/viz) charting the
  committed E39/H683 TSV and H685 `ru_gloss_gap_stats.json` (Trust Blocks, raw download links;
  no re-crawl, no gitignored gap list). Linked from findings/progress dashboards and
  [`data/FAIR_RELEASE_1.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md).
  Rebuild: `python data/viz/build_viz_pages.py`.

### Fixed

- **H1483 report accuracy figure.** Docs previously quoted a pre-tune 49/79=62.0%; live `--verify` against the committed gold is **63/79=79.7%** (residual precision 100%). Report, roadmaps, and changelog aligned. (All-dict linear strip later reports gold **55/79 = 69.6%** on the same sample file — see report.)

## [1.58.0] — 22-07-2026

### Added
- **pwg_ru live-route economy: stripped-`CLAUDE_CONFIG_DIR` cost cut + w1 3-key sample (H1517, Opus 4.8 `claude-opus-4-8`).** Measured that every `claude -p` call loads ~76.7 K cache-creation tokens of profile context (9 skills + 172 commands + plugins + project CLAUDE.md stack) it never needs for translation. Stripping to an auth-only config dir + `--strict-mcp-config` + neutral CWD cut the cold-call cost **$0.4648 → $0.1597 (−65.6%)** on c4 and **fixed the gate-0 `{"ok":false}`** (now PASSES). A real 3-key sample (`ABAsa`/`AKu`/`ARava`, scratch store, no promotion) translated 3/3 at **~$0.137/card** accounted (≈$0.25/card incl. a malformed-retry), **~24 s/card**. Evidence + caveats: [`pwg_ru/h1517/H1517_STRIPPED_CONFIG_ECONOMY_SAMPLE_2026-07-22.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1517/H1517_STRIPPED_CONFIG_ECONOMY_SAMPLE_2026-07-22.md).

## [1.57.0] — 22-07-2026

### Fixed

- **`bounded_staged_run.py` CLI: `--claude-bin` was dereferenced but never defined** — the
  `--execute` path handed `args.claude_bin` to the fleet probe and `RunContext`, but the
  parser never added the flag, so the live CLI crashed with `AttributeError` before any
  call; invisible to every selftest because they all injected `RunContext` directly
  (H1447, the H1386 "a selftest with an injected runner proves the loop, not the path"
  lesson class). Parser extracted to `build_parser()`, flag added with the
  `max_account_orchestrator` convention, pinned by `bounded_staged_run_selftest` test (n)
  that asserts every attr the `--execute` path reads is CLI-defined.

### Added

- **H1447 c4 live-gate packet + medium50 serial-c4 prepared plan**
  ([`pwg_ru/h1447/H1447_C4_LIVE_GATE_2026-07-22.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1447/H1447_C4_LIVE_GATE_2026-07-22.md)):
  fresh gate-0 health PASS (warm-up 17 972 ms / measured 16 621 ms, 0 conn errors), first
  live `dq_canary_puregloss` synthetic-control call through the headless manifest-v2 c4
  route — 3/3 senses, all deterministic audit gates PASS, $0.5730 observed,
  **`LIVE_GO` derived mechanically** — then a bounded starter attempt stopped honestly at
  the fleet probe (`content` warm-up flake, **zero production calls**). The full medium50
  worklist (48 remaining keys) is prepared and unconsumed: 5 leases `h1447-m50-w1…w5`
  (3+12+11+11+11), every harness < 512 KB, payload-v3 chunk evidence exact, preflight
  `--refuse-over-cost` ok ($0.36/card est., 0 deferred monsters), plan + preflight + probe
  events committed as evidence beside the packet; plan builder at
  [`src/pilot/h1447/build_plan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1447/build_plan.py).
  Resume requires a NEW representative c4 health PASS (a stale GO never authorizes).

## [1.56.0] — 22-07-2026

### Added

- Alexey Vigasin corpus (`literature/md/Alexey_Vigasin/`) — full-text `.mdx` conversions of
  all 26 files of *Изучение Индии в России (очерки и материалы)* plus *Работы разных лет*
  fragments ([H1443](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1443-Sonnet_IndologyScholars_vigasin-corpus-extract-route_22.07.26.md),
  Sonnet 5 `claude-sonnet-5`), cross-routed into
  [IndologyScholars](https://github.com/gasyoun/IndologyScholars) `sources/vigasin/`. Published
  full text with the repo owner's rights risk explicitly accepted 22-07-2026.

## [1.55.0] — 22-07-2026

### Fixed

- pwg_ru offline control-plane audit + hardening (Codex Sol `gpt-5.6-sol`, 21-07 audit
  [`docs/PIPELINE_AUDIT_pwg_ru_2026-07-21.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PIPELINE_AUDIT_pwg_ru_2026-07-21.md);
  stranded branch salvaged, rebased onto the merged H1386 landing set and re-gated by Fable 5
  `claude-fable-5`): profile-bound manifest-v2 claim binding (an account can no longer claim a
  manifest bound to another profile; unavailable/parked/unprobed/busy owners fail loudly),
  corrupt/missing audit evidence and a crashed sense-shortfall detector fail the bounded run
  before checkpointing (was a synthetic zero-clean success), cost telemetry read at its real
  `summary.usage` schema path with unevaluable/negative/NaN/infinite figures fail-closed, and
  store-path/promotion perf (cached immutable main-worktree discovery, one case-exact
  output-dir snapshot per audit, receipt row counters instead of two full 26 MB store scans —
  frozen-fixture smoke 17.842→11.354 s, −36.4%, identical output signature; FINDINGS §462).
  Union of this branch + the H1386 set re-gated green: `window_selftest` 180/180 twice under
  random hash seeds, `lang_parity_check` 73 entries no drift (38 hashes re-affirmed post-rebase),
  orchestrator/bounded/supervisor/headless/promote/store_path selftests all PASS.

## [1.54.0] — 22-07-2026

### Fixed

- pwg_ru post-H1339 review landing set
  ([H1386](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1386-Fable_RussianTranslation_pwg-ru-post-h1339-resume-fixes-prepare-speed_20.07.26.md),
  Fable 5 `claude-fable-5`), every fix test-first with a pinned failing regression. Confirmed
  P1s: C1 — bounded `--resume` passed the staged-plan-scope **dict** to `cmd_recover`, so
  crash recovery matched ZERO jobs and a crashed window checkpointed COMPLETED with zero
  output (now the lease-id set; `_scope_sql` rejects dict/str; a None-output window fails
  loudly); C2 — a requeue item whose origin lease had already recorded/promoted wedged every
  `--resume` in `materialize_requeue` (post-audit states with a completed `::rq` job now
  resume to the existing attempt job); C3 — the B12 fragment unblock re-served gate-flagged
  senses: `build_frags` now treats a currently-denied fsha as not-cached, the harvest glob is
  recursive (`artifacts/**`) so requeue outputs two dirs deep are harvested at all, and
  `best_reusable` breaks same-second ties toward the newer row. Also: D2 identity-checked
  atomic-rename promote-lock reclaim (TOCTOU), D3 per-lease `store_delta` from the batch
  report (was bundle-wide stamped N times), D4 `PWG_COORDINATOR_DIR` injected into all three
  bounded coordinator subprocesses (the A7 class), D5 `--batch-manifest` refuses
  `--dry-run`/`--force`/`--init-store` instead of silently mutating the store, and the P3
  sweep (P3b canonical `mw_en_tm` resolution, P3c `reset-failed` origin-lease matching +
  full failed-job ids in fail-closed messages, P3d/P3e `run_py_inproc` KeyboardInterrupt +
  string-exit semantics, P3g batch null-subcard gate, P3h stale_check v2
  execution/provenance cross-check, P3j `probe_log` falsy-zero clean recovery).

### Added

- pwg_ru medium50 start-today enabler (H1386 D1): h1209 payload v3 hoists the shared ~12 KB
  preamble/translation boilerplate into ONE `prompt_common` (was duplicated into every
  card), `inject_payload.py` hard-refuses an emitted script over `WORKFLOW_SCRIPT_CAP`
  (512 KB) with the split remedy, `prep_slice.py --keys`/`--chunk N` auto-splits a big
  manifest into cap-sized sub-payloads, and `canonical_audit.py` merges several chunk
  slice_results into one audit.
- pwg_ru prepare-stage batching (H1386 OPT): `coordinator prepare-batch` prepares N claimed
  leases in ONE coordinator process with the perf_preflight/gen_opt_harness2 children run
  in-process (the H1339 runpy-gates pattern applied to the prepare stage H1339's closeout
  named as the remaining dominant spawn cost), A/B-benched against the per-lease shape:
  **prepare −72.0% median** (11.669 s → 3.263 s; total −22.0%), 2 warmups + 10 measured
  runs per mode, identical deterministic output signature across both modes (semantic
  store equality proven) — evidence in
  [`pwg_ru/h1339/H1386_PREPARE_BATCH_BENCH_2026-07-22.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1339/H1386_PREPARE_BATCH_BENCH_2026-07-22.md).
  Clears the H1339 25% stage gate with no guard weakened; combined with H1339's measured
  −23.0%, the offline-path total is now well past the original ≥25% target.
- pwg_ru hermetic offline bench (H1386 P3f): `h1339_offline_bench.py` now sandboxes its
  fixture inputs (`PWG_INPUT_DIR`, honored by all 14 previously hand-copied input-dir
  sites) and its events ledger (`PWG_EVENTS_PATH`), with a `finally:` teardown — a bench
  run leaves the checkout byte-identical (previously it froze 12 fixture bodies into the
  live `src/pilot/input/` and appended to the live `dashboard_events.jsonl`).
## [1.53.0] — 22-07-2026

### Added

- [`LINK_CHECK_BASELINE_2026H2.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LINK_CHECK_BASELINE_2026H2.md)
  ([H741](https://github.com/gasyoun/Uprava/blob/main/handoffs/H741-Fable_SanskritLexicography_repo-wide-dead-link-sweep_11.07.26.md),
  Fable 5 `claude-fable-5`): the stated baseline the weekly link-check job is judged against —
  full-repo measurement 16,861 unique dead links (15,919 in `literature/md/` ebook conversions,
  942 in real project surface) drained to **73 accepted survivors in 21 files** (goal <100);
  survivor classes, ignore-list rationale, and path-exclusion rulings documented per row.

### Changed

- Weekly [link-check workflow](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/link-check.yml)
  rebuilt (H741): explicit find-based `markdown-link-check@3.14.2` invocation excluding
  `literature/md/**` (third-party book texts, H734 territory) and `docs_site/wiki/**`
  (build_site `--sync` copies); [`mlc_config.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/mlc_config.json)
  gains ignore patterns for the 11 private `gasyoun/*` repos (unauthenticated-404-by-design),
  `mailto:`, DOI resolvers, bot-blocking publishers, and flaky project-adjacent academic hosts;
  `aliveStatusCodes` gains 202.

### Fixed

- 62 CI-visible dead links across 31 files
  ([PR #666](https://github.com/gasyoun/SanskritLexicography/pull/666), H741 bucket A):
  archive-move relative links → full blob URLs; gitignored-by-design targets delinked;
  PR #540-deleted gloss-reviews → pinned pre-deletion SHAs; wrong-owner GitHub URLs
  (csl-atlas / csl-observatory / csl-standards / sanskrit-util / MWS → `sanskrit-lexicon`;
  SanskritSpellCheck / kosha / WhitneyRoots → `gasyoun`); Wikipedia/TMX/archive.org 404s
  repointed to verified targets; two broken in-file anchors.

## [1.52.0] — 21-07-2026

### Added

- **Restored the nine Russian/Soviet full-text conversions removed by [PR #481](https://github.com/gasyoun/SanskritLexicography/pull/481).** Owner ruling on the [Uprava weekly @DECIDE sheet 20-07-2026](https://github.com/gasyoun/Uprava/blob/main/review/weekly/archive/uprava-weekly-decide_20-07-2026_review.html): «bring back, I take the risk» — the copyright risk is explicitly accepted, consistent with the same-day rulings that kept Kumar 1976 + Meenakshi 1983 and left the ~30-work Western academic-press cluster on tip. Files recovered from `68a88c94^` and verified byte-identical to their pre-removal state: four under `literature/md/Вспомогательное/` (Zaliznyak & Paducheva 1975, Jakobson 1987, Mitrenina 2008 + 2010) and five under `literature/md/Общий синтаксис/` (Kibrik et al. 2020, Entsiklopedicheskiy slovar 1984, Testelets, Lomov, Sintaksis-2009). The nine `*_DIGEST.md` files added at removal time are **kept** — they now sit beside their full texts rather than standing in for them. `.gitignore` unchanged (PR #481 touched only a comment there; `!literature/md` still stands); both READMEs corrected — `Вспомогательное/` 15 → 19 files, `Общий синтаксис/` 6 → 11, total referenced 67 → 76.

## [1.51.0] — 21-07-2026

### Added

- pwg_ru abbreviation ↔ ЛЭС-1990 comparison layer: standalone [`pwg_ru/ABBREV_LES1990_SRAVNENIE_2026-07.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ABBREV_LES1990_SRAVNENIE_2026-07.md)
  plus a summary врезка in [`pwg_ru/ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md)
  (Opus 4.8 `claude-opus-4-8`, `/ask`): benchmarks the 269-token unified list against the
  «Список основных сокращений» of the Linguistic Encyclopedic Dictionary (ЛЭС, ed. В. Н. Ярцева,
  1990). 24 tokens match ЛЭС verbatim (см./ср./напр./изд./ред. + the case Latinisms
  акк./ген./абл./лок.); the Sanskrit verbal apparatus (аорист/каузатив/медий) lies outside ЛЭС
  jurisdiction (там эталон — классическая индоевропеистика); jurisdictional divergences (spacing
  «т. е.», ед.→ед. ч., стр.→с., дат.→дат. п., герунд.→абс.) parked as a non-binding
  harmonization-candidate list — voted H1303 tables untouched.
- A30 hostile referee pass ([H1382](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1382-Fable_SanskritLexicography_a30-hostile-referee-pass-skd-vcp_20.07.26.md),
  Fable 5 `claude-fable-5`): [`papers/A30_review_fable5.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_review_fable5.md)
  — verdict **major revision, 4/5 gate not cleared as drafted**; C1–C4/C6 CONFIRMED (the
  53.3 %/77.6 % *iti*-fusion contrast rests on a classifier with three artifact classes
  visible in its own committed sample — severed sandhi citations, a 16-name recall ceiling,
  formula false-positives — and §7's "fewer, longer" VCP claim is contradicted by the
  corpus's committed length stats), C5 downgraded to CLEAN, C7 re-derived CLEAN; every §1–§5
  figure verified exact against csl-atlas `origin/main`. Includes the edition-facts check
  (SKD "from 1822" → corrected 1821/22–1858; VCP 1873–1884 confirmed).
- SKD *iti* adjudication sample, model pass ([`papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md)):
  102 rows labelled citational 81 / grammatical 6 / unclear 15 — explicitly **not** the human
  gold (that gate stays open); sheet-readiness defects reported (severed-before-name rows,
  missing post-stratification weights).

## [1.50.0] — 21-07-2026

### Added

- pwg_ru style-research memo [`pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md)
  ([H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md)
  phase 1, Fable 5 `claude-fable-5`): doublet-gloss policy grounded in Апресян 1995 (с. 95, 218,
  verified verbatim) + Берков 2004 «синонимит» (с. 149–153) + Щерба 1940; `v. l.` ruling with the
  Дворецкий abbreviation-list precedent (verbatim) vs the dead prompt rule (0/252 store cards obey
  it); the *im Comp., vorangehend* formula measured at ~2.1k corpus-wide (not "tens of thousands");
  KATHĀS. 26,9 attested-citation arbiter worked example via SamudraManthanam (Серебряков). 9-card
  ratification sheet `review/h1306_style_sheet.html` (`sheet_id h1306_style`, csl-pyutil 0.3.1,
  local-only + gitignored) awaits MG's vote → `pwg_ru/eval/h1306_style.decisions.json`.

- FINDINGS §459 (csl-atlas H1423, [PR #290](https://github.com/sanskrit-lexicon/csl-atlas/pull/290)):
  PWG's entry-size decay is a **smooth funding/energy fade** across its whole 20-year run
  (−14 %/decade; vols 2–7 still −15 %/decade after dropping the over-detailed vol-1) — settling the
  §458 cause question — measured by mapping all 123,366 PWG entries to a real publication year via
  the `<pc>`→volume→year field. Plus the reusable gotcha that cross-dictionary markup-density
  measures the *digitisation apparatus*, not lexicographic depth (SKD/VCP carry ~0 Cologne markup).

## [1.49.0] — 2026-07-21

### Fixed — coordinator concurrency/durability plausibles P2/P10/P11 (H1420)

- Three PLAUSIBLE findings from the Opus 4.8 adversarial pwg_ru bug-hunt
  ([issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632); C1–C9 shipped in
  v1.47.0), each verified real against the code + callers and fixed in
  [`coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py),
  one selftest pinned per defect:
  - **P2** — `_win32_pid_alive` reported DEAD for *every* `OpenProcess` error except `ERROR_ACCESS_DENIED`
    (5), contradicting its own fail-safe comment: a transient/unexpected probe error would falsely reclaim a
    **live** lock into two writers (the A1 double-writer window, H1283). It now leans ALIVE on any error
    except the definitively-dead `ERROR_INVALID_PARAMETER` (87 = no such pid); the classification is extracted
    to a pure `_win32_alive_on_openprocess_error` and pinned by
    `test_h1420_p2_win32_openprocess_error_leans_alive`.
  - **P10** — `promote_ready` commits the store in one all-or-nothing batch, then rebuilt the RU TM *after* the
    per-lease state loop; a raise between the store commit and the rebuild (unreadable batch report,
    no-landed-subcards, a per-lease state error) left store and TM divergent until the next clean run. The
    rebuild now runs in a `finally` (extracted to `rebuild_ru_translation_memory`), pinned by
    `test_h1420_p10_promote_rebuilds_tm_in_finally`.
  - **P11** — `record-output` gated only on `state=='running'`, so after a run was released/recovered and the
    lease re-run, a stale `workflow_result` from the prior run could record against the new run (silent
    misattribution). A new optional `--run-id` (the identity sealed at `begin-run`) must now match the running
    lease's `run_id`; a mismatch is refused before any state is persisted. Pinned by
    `test_h1420_p11_record_output_binds_run_id`.
- All three are lang-agnostic coordinator/lock/promotion machinery (no RU/EN divergence); the two
  `coordinator.py` `LANG_PARITY.md` SHARED entries were re-verified and re-hashed. `window_selftest` 175/175;
  `lang_parity_check` no drift.

### Fixed — EN promotion store write is now durable (fsync-before-replace); P1 verified already-fixed (H1421)

- **P9 (bug-hunt plausible, now fixed):** [`promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py)'s
  tri-lingual store write was a bare `open('w')` + `os.replace` — **atomic but not durable**: a
  crash/power-loss between the write and the metadata flush could leave a non-durable/truncated
  store even after the rename (and under `--no-backup` that write is the ONLY thing between an
  interrupted write and total loss). It now reuses the RU lane's fsynced `_atomic_write_rows`
  (imported from [`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) —
  `flush()`+`os.fsync()` before `os.replace`), single-sourcing the store writer across both lanes
  (as a bonus both now write `\n` newlines; the old EN write CRLF-translated on Windows). Pinned by
  a new P9 block in `promote_en.selftest()` (fsync-called + round-trip + single-source identity).
  The `promotion_scripts_separate` LANG_PARITY note records the SHARED reuse.
- **P1 (bug-hunt plausible, verified already-fixed):** the concern that `merge_store_rows` replaced
  by sub-card unconditionally — silently downgrading a complete store card when an older/partial
  `wf_output` is re-promoted — was **already resolved upstream by B08 (H1339)**: `merge_store_rows`
  is better-attempt-wins (complete > partial, fewer missing fragments win, ties favour the incoming
  attempt) with pinned regression selftests. No code change needed; recorded for the audit trail.

### Changed — EN/RU convergence W2: shared cross-reference vocabulary + audit reassessment (H1425)

- The cross-reference / degenerate-passthrough vocabulary (`s.`, `vgl.`, `u.`, `Nachträge`, …)
  was two **byte-identical independently-authored copies** — `gen_opt_harness2._DEGENERATE_WORDS`
  (RU generation lane) and `audit_window_en._XREF_WORDS` (EN auditor) — the C-01 drift class the
  codebase already consolidated `portrait_key_iast` for. Extracted to a **dependency-free** shared
  module
  [`xref_vocab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/xref_vocab.py)
  both import (the EN auditor deliberately can't pull in the harness's heavy `pwg_mask`/`corpus_gate`
  stack). Behaviour-preserving; pinned by `test_degenerate_xref_vocab_single_source` (asserts object
  identity). New SHARED ledger entry `degenerate_xref_vocab_shared`.
- **Reassessment finding (recorded in the ledger):** reading both auditors showed W2's convergence
  target is materially smaller than first scoped. `audit_window_en`'s reusable surfaces are *already*
  shared — the German-residue word list via `foreign_literal_guards.py`, the whole-dropped-sense
  SAN-LOSS gate via `sense_count.py` — and its remaining gates (`DUP`/`MISSING-EN`/`MARKUP-LOSS`/
  `xref_only`/`nws_de_locked`) are EN-audit-time-specific **by architecture** (RU per-card fidelity is
  *generation-time* in the harness `accept()`/`countOfField`, not a symmetric Python auditor), i.e.
  intentional divergence — not a wholesale reimplementation to force-merge.

### Changed — EN/RU convergence W1: card-done coverage rule extracted to one shared `--lang` kernel (H1425)

- First wave of shrinking the EN-reimplementation surface (the root cause of the RU/EN drift the
  coverage guard polices). The **FL4 coverage-complete rule** — a card is done iff it has ≥1 slot
  and *every* German-bearing slot carries the target field (not the old ">=1 translated sense" rule
  that hid a 1/40 card) — was an EN-only reimplementation inside `en_residual_keys.py`. Extracted to
  a shared `--lang`-parameterized kernel
  [`card_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/card_coverage.py)
  (`slot_coverage`/`card_done(card, field)`); `en_residual_keys.py` is now a thin `field='english'`
  consumer (output **byte-identical**, verified against the pre-refactor inline logic). A fix to the
  rule now reaches any language that calls it. The `en_coverage_card_done_semantics` ledger entry
  flips **INTENTIONAL-DIVERGENCE → SHARED**. Pinned by `test_card_coverage_lang_symmetric`. NOTE:
  `ru_coverage.py` does a *different*, coarser check (per-root sub-card presence) and still carries
  the FL4 per-slot blindspot this kernel fixes — wiring it in is a tracked H1425 follow-up (a
  behaviour change to a live gate, deferred from this warm-up).

### Added — LANG_PARITY coverage guard: new RU/EN-lane files can't silently escape the ledger

- The parity ledger's drift check only re-verifies files **already** tracked; a brand-new
  language-aware file (a fresh `*_en.py` reimplementation, or a new `--lang`-branching gate) could
  escape parity tracking entirely — the exact hole the C1–C9 EN findings (`audit_window_en.py`,
  `promote_en.py`) grew in. New **coverage guard** in
  [`lang_parity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lang_parity_check.py)
  (`coverage_check`, wired as `test_lang_parity_coverage`): every language-aware pipeline `.py`
  under `src/`/`src/pilot/` must be **either** referenced by a ledger entry's `files:` **or** listed
  in a new `lang_parity_coverage` `exempt` map with a one-line reason — else CI fails and names the
  file. The 8 existing untracked candidates were classified by an Opus 4.8 (`claude-opus-4-8`)
  8-agent fan-out + adversarial audit: **7 exempt** (read-only samplers / benchmarks / QA-sheet
  generators, each with a recorded reason) and **1 promoted to a ledger entry**
  (`en_residual_keys.py` → `en_coverage_card_done_semantics`, the EN twin of `ru_coverage.py` whose
  card-done semantics must stay aligned). Ledger now 71 entries; coverage 22 language-aware files,
  all tracked or exempt. Verified end-to-end (a synthetic new `*_en.py` fails the guard).

### Fixed — build-frags glob (C7) + German-as-Latin mask drop (C8) + EN backup collision (C9) (H1418)

- **C7 — `build-frags` built the fragment TM from the wrong tree under a custom coordinator dir.**
  In [`coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py)
  `promote_ready`, the `frag_prov` **detection** globbed `paths()['artifacts']` (honors
  `PWG_COORDINATOR_DIR`) but the **build-frags** call hardcoded the default-tree glob — so a
  per-run/worktree coordinator dir detected fragments yet built the fragment TM from the empty
  default tree, silently dropping the just-promoted window's fragments. Both sides now use one
  `_frag_prov_glob()` derived from `paths()['artifacts']`.
- **C8 — German glosses opening `In…`/`Ab…`/`Ex…`/`Sub…`/`Pro…` were masked as Latin and dropped.**
  [`pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)'s
  `LATIN_PHRASE` matched German-capitalized homographs of Latin prepositions, so a `{%In den
  Schlusssatz einfallen%}`-style gloss was masked to `{Tn}` and never translated — invisibly
  (restore reinserts the identical German, so the round-trip stayed "100% lossless"). Fixed: a
  homograph opener stays Latin only if **no** German function word follows; `De …` (not a German
  word) remains an unguarded Latin opener. Measured **1 of 192,763** `{%…%}` spans, now kept inline.
- **C9 — the EN store backup could clobber an earlier recovery copy.**
  [`promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py)
  named the backup with a **second-resolution** timestamp and wrote it with a plain `open('w')`, so
  two lock-serialized runs in the same second overwrote the earlier `.preEN` backup. Fixed to a
  µs+pid+uuid name (`_en_backup_path`) plus the RU lane's **O_EXCL** fsynced copier
  (`_fsynced_backup`, imported — single source).
- Found by the Opus 4.8 (`claude-opus-4-8`) adversarial bug-hunt review (C7/C8/C9 of
  [issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632)) — the last of the 9
  confirmed findings (C1–C6 shipped in #634/#636/#638). Selftests: `window_selftest`
  (`test_frag_prov_glob_honors_coordinator_dir_c7`, `test_pwg_mask_german_homograph_not_latin_c8`)
  and `promote_en --selftest` (C9 block).

### Fixed — audit/mask robustness plausibles P3–P8, verified and fixed (H1422)

Six LOW-severity PLAUSIBLE findings from the same Opus 4.8 adversarial bug-hunt
([issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632)) that shipped C1–C9
above — verified against real code/callers, all six real, all fixed:

- **P3 — the degenerate cross-reference pass-through lane leaked German into the RU/EN field.**
  [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  `degenerate_passthrough_card` assigned `field: body` — the German source text, verbatim — for
  stubs it correctly identified as untranslatable (`vgl.`/`s.`/`ff.` cross-reference particles).
  These German tokens are not even covered by `german_residue_scan.py`'s wordlist (it requires
  3+-letter function words), so the leak was previously undetectable by any existing audit. Now
  the target field stays empty; the German remains visible via the `german` key for editorial
  reference.
- **P4 — sense-tier splitting had no open-span guard, unlike the citation-batch tier.**
  [`autosplit_requeue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py)
  `_blocks` detected sense boundaries purely from lines matching `_SENSE` ("1)", "2)", …), with no
  `_span_open` awareness — unlike `_cit_parts` (H155). A multi-line `<ls>`/`{#..#}` citation whose
  interior contained a `_SENSE`-shaped locator could be torn across two (sub)sense blocks. Fixed
  by applying the same balanced-span deferral to sense-boundary detection.
- **P5 — `audit_sense_dupes.norm()` stripped `)`/`〉` but not a trailing `.`.**
  [`audit_sense_dupes.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_sense_dupes.py):
  tag `1.` and plain `1` hashed to different buckets, so a real cross-part duplicate with
  mismatched locator punctuation was missed by the dupe check. Now strips trailing `.`/`)` in
  any order; an interior period (`caus. 2`) stays untouched.
- **P6 — `audit_window.run_py`'s subprocess call had no error handling.**
  [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py):
  a `TimeoutExpired`/`OSError` re-raised straight through `collect_cards`/`root_glue_translated.py`
  and crashed the whole audit with no report or requeue, even though `main()`'s gate loop already
  handles a non-`{0,1}` returncode gracefully. Now converts either exception into that same result
  shape (returncode `124`/`-1`) instead of propagating.
- **P7 — the EN `MISSING-EN` hard gate treated cross-ref/abbrev residue as translatable prose.**
  [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py):
  `has_gloss` fired on ANY non-empty German prose residue, including a bare cross-reference
  apparatus (`vgl. {#foo#} fgg.`) that `xref_only()` already recognizes as non-target — hard-failing
  a sense that was never a translation target the moment its english field was correctly left
  empty. Now `has_gloss` also requires `not xref_only(g)`.
- **P8 — EN `MARKUP-LOSS` summed two marker classes before comparing, letting one mask the other.**
  [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py):
  `{%..%}` gloss-wrapper count and `<div>` count were added into one combined number, so a dropped
  gloss wrapper could be masked by an unrelated `<div>` gained in the english (net count unchanged).
  Now counts and compares each marker class separately.

LANG_PARITY.md re-verified: `target_field_markup_fidelity_parity_c1` (P3's degenerate lane is
structurally exempt from the C1 fidelity guard — it bypasses `translateBatch`/`healOnly`
entirely) and `subprocess_and_bom_hardening_h316` (P6 only adds error handling around the
existing `encoding='utf-8'`/`timeout=1800` call, both left unchanged) verdicts confirmed to
still hold; 49 stale hashes re-verified and updated. Selftests: `window_selftest`
(`test_degenerate_passthrough_no_german_in_target`, `test_sense_split_never_tears_open_span`,
`test_sense_dupe_norm_strips_trailing_period`, `test_run_py_survives_timeout_and_oserror`,
`test_p7_missing_en_not_fired_on_xref_only_residue`, `test_p8_markup_loss_not_masked_by_unrelated_div`).

### Fixed — EN DUP gate false-flags distinct referents (C2) + EN promote {Tn} guard (C6) (H1414)

- **C2 — the EN within-card `DUP` HARD gate false-flagged distinct proper-name senses.**
  [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py)
  keyed the duplicate check on `prose(english)`, which **strips** `{#..#}` Sanskrit and `<ls>`
  citations — so two senses distinguished only by their referent (`N. of a serpent-demon
  {#vāsuki#}` vs `…{#takṣaka#}`) normalized to one string and the second was reported as a HARD
  `DUP`, failing `--strict` on faithful output (310 real within-record cases across the EN
  wf files). Fixed to key the DUP `seen`-dict on the normalized **raw** english (referent
  preserved), matching the gate's own contract ("the exact same english"); the `CIRCULAR` check
  keeps prose-`norm`, and a true identical-english duplicate is still caught HARD.
- **C6 — the EN promote lane had no unrestored-`{Tn}` guard.** `promote_en.py` `attach()` wrote
  `r['en'] = en` with no residue check, while the RU lane refuses a card carrying a `{Tn}` mask
  placeholder (`promote_final_cards` C-01 → `UnrestoredPlaceholder`). Fixed by **importing** the
  RU lane's exact `TN_RE` + `UnrestoredPlaceholder` (single source — a look-alike copy is the
  drift that C3 was) and refusing loudly, before any backup/store write.
- Found by the Opus 4.8 (`claude-opus-4-8`) adversarial bug-hunt review (findings C2/C6 of
  [issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632)). Selftests:
  `window_selftest` (`test_en_dup_gate_preserves_sanskrit_referent_c2`) and
  `promote_en --selftest` (C6 refusal block). Recorded in
  [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
  (`en_dup_hard_gate_20260704`, `promotion_scripts_separate`).
### Fixed — dead EN card-TM (C3) and rate-limit job-stranding busy-loop (C4) (H1413)

- **C3 — EN whole-card translation memory was 100% dead.** `translation_memory.py build --lang en`
  wrote each sense's translation under the store **column** name (`FIELD['en']=='en'`) instead of
  the **card** field name `'english'`, but the serve-side guard (`tm_card_sane`) and the final-card
  schema require `'english'` — so every EN card-TM hit was silently refused (`sense missing
  english`) and the EN lane re-translated whole cards it already had (wasted spend; RU was
  unaffected). Fixed with a single `CARD_FIELD = {'ru': 'russian', 'en': 'english'}` used by both
  the card builder and the fragment lane (`_FRAG_TRANSLATION_FIELD` now aliases it, so the two
  can't drift again). Classified SHARED in
  [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md).
- **C4 — a rate-limited job could become permanently unclaimable and busy-loop `staged-run`.**
  `max_account_orchestrator.py` incremented `attempts` at claim time but the 429/rate-limit path
  called `finish(…, 'pending', …)` without giving the attempt back (unlike `release_db_claims`), so
  after `max_attempts` rate-limits a job sat `pending` with `attempts == max_attempts` — never
  re-selected by `claim` (`WHERE attempts < max_attempts`), never marked `failed` — permanently
  stranded, and `cmd_staged_run` spun on the un-drainable `pending` count. Fixed by treating a 429
  as a non-defective attempt (`requeue_rate_limited` decrements `attempts` atomically), plus a
  no-progress poll backstop so any residual unclaimable-but-pending state polls instead of
  hot-spinning.
- Found by the Opus 4.8 (`claude-opus-4-8`) adversarial bug-hunt review (findings C3/C4 of
  [issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632)). Selftests:
  `window_selftest` (`test_en_card_tm_serves_english_field_c3`) and
  `max_account_orchestrator_selftest` (C4 rate-limit block).
### Fixed — target-field markup-fidelity guard ported to every promotable lane (C1 / H1412)

- The `<ls>`/`{#..#}` markup-count fidelity guard now runs over the actual **target-language
  field** (`russian`/`english`), not only the `german` source-echo, on **every** lane that can
  promote a card. Previously only the JS batch `accept()` lane carried this check (H1152); the
  heal/presplit stitch, the headless `normalize_batch` (now the production route) and its
  selfheal stitch, and both autosplit stitch writers (`cmd_merge` + `stitch_topup`) counted
  only `german` — so a translation faithful in the German echo but missing a Sanskrit/citation
  span in the Russian/English column (the live H1070 r102 pattern: german 33/33, english 32/33)
  was stitched and promoted with the span silently dropped. All off-batch lanes now reject →
  requeue on a target-field span mismatch. Found by the Opus 4.8 (`claude-opus-4-8`) adversarial
  bug-hunt review; the autosplit change also closes the `<ls>`-only / non-blocking gap (C5).
  Selftests: `window_selftest` (`test_heal_lane_target_field_fidelity_wired`,
  `test_autosplit_stitch_topup_rejects_target_field_drop`,
  `test_autosplit_merge_rejects_target_field_drop`) and `headless_worker_selftest`
  (`test_normalize_batch_translation_fidelity_reject`,
  `test_headless_heal_stitch_translation_fidelity_reject`); classified SHARED in
  [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
  (`target_field_markup_fidelity_parity_c1`).

### Added — speed & orchestration audit: bottleneck ledger + verified action map (H1403)

- [`PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md)
  (Fable 5 `claude-fable-5`, 22-agent ultracode workflow: 5 miners → synthesis → 2 adversarial
  lenses per recommendation). **0/8 recommendations survived unmodified (6 weakened, 2 refuted)**
  — the speed frontier is executing already-minted work, not new design: run H1209 medium50
  (parked since 18-07), finish H390 rule 4(a) instrumentation, close three operator-loop
  residues; generation is only ~12–22 % of chain calendar. Registered
  [DEAD_ENDS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
  (H1225 SANLOSS counter fix) and landed the dangling §11 (W3 vidyut-cheda NO-GO).

### Added — Sa→Ru gloss layer wave-4 read-only TM lookup (H1349 W4 — H1349 complete)

- `src/saru_gloss_tm.py` (`GlossTM`) exposes the lemma + root gloss layers as a **read-only**
  lookup for the pwg_ru/mw_ru card path: a Sanskrit lemma/root (SLP1) → ranked candidate
  Russian renderings. Additive consumer only — does not touch the harness TM / store / the
  safety-plan #547/#550 coordinator runtime. Smoke-tested on the published SanskritRussian
  data (`gam`→пришел/отправился/…, `karman`→действия/деяния/…); fixture-backed regression
  test `tests/test_saru_gloss_tm.py` wired into CI. Closes H1349 (waves 1–4).

### Added — Sa→Ru gloss layer wave-3 coverage spike: vidyut-cheda NO-GO (H1349 W3)

- Measured whether `vidyut.cheda` compound segmentation can recover the 78,842 unresolved
  forms. `src/build_compound_split.py` applies a strict precision gate (≥2 tokens + every
  member glossable) and recovers 36.4% (28,673 forms) — but a 2-judge panel scored those
  recoveries at **18% gloss precision / 60% outright wrong**, vs the wave-2 baseline of 85.3%.
  **NO-GO: not wired into the rollup** — vidyut-cheda is a running-text segmenter and shatters
  isolated OOV forms into stem + spurious glossable particle. The 85% layer stays unregressed;
  recommended path (backlog) is the DharmaMitra neural segmenter over the aligned verse text.
  Finding: `gold/saru_gloss_wave3_cheda_coverage.md`; gate has a regression test
  (`tests/test_saru_gloss_wave3.py`, wired into CI).

### Added — Sa→Ru gloss layer measured precision (H1349 wave 2)

- **First accuracy measurement** of the gloss layer (every prior number was coverage). A
  new tier×frequency stratified sampler (`src/saru_gloss_sample.py`) + panel aggregator
  (`src/saru_gloss_aggregate.py`) run a **model-vs-model LLM panel** (Opus 4.8 / Sonnet 5 /
  Haiku 4.5, adversarially adjudicated by Fable 5) over 110 resolutions, judging lemmatization
  and gloss separately (D6). Result: lemmatization **86.1%** (95% CI 78.3–91.4), gloss **85.3%**
  (77.5–90.8) — with the **vidyut** tier the lemmatization weak spot (71.8% vs dcs 94.9% /
  marker 93.3%). Report: `gold/saru_gloss_precision_report.md`; numbers in `RESULTS_LOG.md`.
- `build_rollup_glossaries.py` now also emits `surface_resolution.tsv` (per-form tier · lemma ·
  top-gloss) as the sampling frame — backward-compatible (a new output; existing ones unchanged).
- Panel labels + the frozen sample committed under `gold/` as the scaffold for a human
  spot-check; runs cleanly through the existing `gold_agreement.py` double-review machinery.
  Wave-2 scaffold has its own regression tests (`tests/test_saru_gloss_wave2.py`, wired into CI).

### Fixed — Sa→Ru gloss layer wave-1 defects (H1349 W1.1–W1.3)

- **Pseudo-roots (W1.1).** `build_dcs_maps.py` no longer keeps prefixed verb lemmas that
  fail the root-suffix match as their own roots: the 434 self-mapped `unresolved` rows are
  split into `dcs_lemma2root_unresolved.tsv`, and `build_rollup_glossaries.py` excludes them
  from the root layer (root inventory 3,570 → 3,147 distinct keys; `root_glossary` 1,853).
- **Homograph completeness (W1.2).** The rollup's ambiguity report inspected only the single
  runner-up `cands[1]`; a genuine 3rd+ homograph was silently dropped. It now records the
  full trail over `cands[1:]` (9,521 → 11,289 alternate rows across 9,733 forms).
- **Vidyut ambiguity trail (W1.3).** `build_vidyut_fallback.py` incremented a bare
  `ambiguous` counter; it now writes the competing `(lemma, pos, n)` candidates to
  `vidyut_ambiguity.tsv` (5,952 rows over 4,133 forms), mirroring the DCS schema.
- Each fix carries a regression test in `tests/test_saru_gloss_pipeline.py` (wired into the CI
  RussianTranslation-gates job); `vidyut`/`indic_transliteration` are now imported lazily so
  the pure helpers are testable without the heavy deps. Before/after in
  [RESULTS_LOG.md](RESULTS_LOG.md); the pipeline `glossary/README.md` is now a build runbook
  pointing at the canonical [gasyoun/SanskritRussian](https://github.com/gasyoun/SanskritRussian)
  doc. Published data is **not** regenerated (D8 fences republish behind a human GO).

### Fixed — scoped RU style gate and conflict-safe H1305 repair

- The `ru_style` workflow gate now audits only structured
  `card.records[].senses[].russian` values. Rendered Markdown notes, `differentia`, German
  source text, headings, and footer metadata are excluded. Multiple violating senses still
  aggregate to one original workflow key; ambiguous R2/R3 matches are diagnostic warnings,
  never `FLAGGED_JSON` defects. The EN audit path is unchanged.
- R2/R3 now share one high-precision contextual classifier between rewriting and auditing.
  Matches inside `«…»` or `{%…%}` are protected; only the ratified correction,
  replacement-object, and lexical-use cues are hard. A complete re-audit corrected H1305's
  sampled false-positive claim: of 291 pre-sweep «вместо» occurrences, 279 are hard and 12
  ambiguous; of 24 «в значении» occurrences, 20 are hard and 4 ambiguous.
- Added dry-run-by-default `--repair-from` reconciliation against the original H1305 backup.
  Stable row hashes exclude translation/review/provenance fields and use occurrence ordinals
  for duplicates. Only original, legacy-swept, or newly scoped values are recognized;
  divergent later edits fail the entire apply. The canonical repair restored all 16 reviewed
  ambiguous occurrences with 0 conflicts and preserved the 11,603-row population. Final
  store audit: 0 hard violations, 12 R2 + 4 R3 warnings.
- Every apply now makes an exclusive UTC-timestamped backup, verifies its SHA-256 and row
  count, re-hashes the live store immediately before atomic replacement, and writes an
  ignored JSON evidence report. Consecutive applies were verified to create distinct backups.
  The derived RU card translation memory was rebuilt and validated after repair.

### Added — mechanical RU style sweep: no-ё, terse editorial metalanguage (H1305)

- **Four ratified, deterministic RU style rules applied store-wide and wired for future
  generation** (MG's DA-vote, register rows N7/N12 + the terseness half of N4):
  **R1** no letter ё anywhere in RU output — write е everywhere; the only exception is the
  standalone token «всё»/«Всё» (disambiguating все/всё); the edge case «всё-таки» defaults
  to е («все-таки») like every other ё-word, per the ruling. **R2** «вместо» → «вм.» and
  **R3** «в значении» → «в знач.» in editorial metalanguage. The original sampled
  **0/60** and **0/24** false-positive claim and unrestricted application are superseded by
  the review fix above: the full population contains 12 ambiguous R2 and 4 ambiguous R3
  cases, all restored and now non-blocking. **R4** `ed. Bomb.` → «Бомбейская ред.» in
  **free prose only** — 282 of 283 occurrences (221 standalone `<ls>ed. Bomb.</ls>` + 61
  embedded in a longer citation, e.g. `<ls>R. ed. Bomb. 3,69,4</ls>`) sit inside
  `<ls>…</ls>` and were left **verbatim**: [`src/pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py)'s
  `source_key()`/`resolve()` key the citation off that exact Latin text against PWG's own
  bibliography (`pwgauth/pwgbib.txt`, all-Latin index) — rewriting to Cyrillic would break
  source resolution outright; only the store's single genuine free-prose occurrence was
  swept. The in-`<ls>` population (282 occurrences) is a render-time display concern,
  explicitly out of scope here and NOT covered by [H1307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1307-Opus_RussianTranslation_pwg-ru-ls-link-enrichment-panini-spr-dhatup_19.07.26.md)
  either — handed off as a PROPOSED follow-up.
- **Initially applied to the canonical store** (11,603 rows, row count unchanged): 2,029
  substitutions across 1,485 rows (R1=1,713, R2=291, R3=24, R4=1). The scoped repair above
  restored 16 ambiguous R2/R3 values, leaving 2,013 ratified substitutions
  (R1=1,713, R2=279, R3=20, R4=1) and 0 hard residual violations.
- **New** [`src/ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py)
  (stdlib-only; dry-run default, `--apply`, `--selftest`, `--wf` for the window-gate mode) —
  resolves the store via `store_path.canonical_store` (prints the resolved path before
  writing, per the H805/w06 worktree-loss guard) and exposes `scan_violations()`, a
  read-only detector reused verbatim by the new `ru_style` gate.
- **New `ru_style` gate** in
  [`src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)'s
  RU gate commands (same `.merged.md`-reading / `FLAGGED_JSON` shape as
  `translation`/`stage2_mechanical`/`coverage`/`sense_dupes`) — RU-only, deliberately never
  wired into `audit_window_en.py`. Tests in
  [`src/pilot/window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)
  (`test_h1305_ru_style_mechanical`) cover ё-word flagging, the «всё»/«Всё» whitelist, the
  «всё-таки» edge case, metalanguage «вместо»/«в значении» flagging, in-`<ls>` `ed. Bomb.`
  (standalone AND embedded) staying unflagged, and a genuine free-prose `ed. Bomb.` hit —
  150/150 green.
- **Prompt HARD RULE 9** added to the `CONV`/`TR` template in
  [`src/pilot/run_pilot_wf.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js)
  states R1–R4 for the model; `gen_opt_harness2.py` extracts `TR` from this file by regex,
  so every future-generated optimized harness inherits the rule automatically (verified by
  direct extraction — no separate derivative file to keep in sync). Pinned in
  [`src/pilot/prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)'s
  `RULES` (`ru_style_no_yo` / `ru_style_terse_metalanguage` / `ru_style_ed_bomb_siglum`) so
  a future template edit that drops the rule fails `--fail-on-missing`.
- **LANG_PARITY** entry `ru_style_mechanical_yo_terseness` (INTENTIONAL-DIVERGENCE) — the
  gate-wiring MECHANISM is SHARED-capable (a slot in `audit_window.py`'s existing commands
  list), but the RULES THEMSELVES have no EN counterpart by construction (EN output carries
  no Cyrillic, no ё, no «вместо»/«в значении» abbreviation question). `lang_parity_check.py`
  green (59 entries, no drift after re-affirming 38 pre-existing entries whose tracked
  files' sha256 drifted from this session's additive edits — none of those entries'
  described behavior was touched).
- Full rule table, false-positive measurement, and `ed. Bomb.` markup-placement analysis:
  [`pwg_ru/RU_STYLE_MECHANICAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md).
  Provenance: [H1305](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1305-Sonnet_RussianTranslation_pwg-ru-style-mechanical-yo-terseness-sweep_19.07.26.md), Sonnet 5 `claude-sonnet-5`.

## [1.48.0] — 21-07-2026

### Fixed
- **H1397 — reattached FINDINGS §456's orphaned body + regenerated stale dashboards.** The 20-07-2026 §102→§456 collision fix ([PR #618](https://github.com/gasyoun/SanskritLexicography/pull/618), issue #624) moved only §456's header + tombstone note, leaving the actual finding body (H1328's uttarapada dict-vs-corpus Jaccard analysis) orphaned as headerless text between §457 and §458 — invisible to `epistemic_integrity_check.py`'s heading scan but genuine duplicate/dead content. Moved the body back under its own §456 header (pure relocation, no content change); regenerated `findings_dashboard/data.json`/`timeseries.json` and `epistemic_dashboard/epistemic.json` (stale 115/116 headings before this fix). `epistemic_integrity_check.py --dir .` now reports full `OK`. ([SanskritLexicography PR #642](https://github.com/gasyoun/SanskritLexicography/pull/642), Sonnet 5 `claude-sonnet-5`)

## [1.47.0] — 21-07-2026

### Fixed — PWG→RU/EN pipeline bug-hunt: all 9 confirmed findings (C1–C9)

- An Opus 4.8 (`claude-opus-4-8`) adversarial code review of the pwg_ru translation pipeline (9
  finder groups + per-finding verification) surfaced 9 confirmed bugs, all now fixed and merged
  ([issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632); component-level detail
  in [`RussianTranslation/CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md)):
  - **C1** (subsumes C5) — the `<ls>`/`{#..#}` markup-fidelity guard only checked the German
    source-echo on every lane except the JS batch `accept()`; ported the target-language-field
    check to the heal/presplit, headless `normalize_batch` (production route), and autosplit stitch
    lanes, so a translation faithful in German but missing a Sanskrit/citation span in the
    Russian/English column can no longer be promoted silently ([PR #638](https://github.com/gasyoun/SanskritLexicography/pull/638)).
  - **C2** — the EN `DUP` gate keyed on `prose()` (which strips `{#..#}`), false-flagging distinct
    proper-name senses (310 real cases); now keys on the raw english. **C6** — the EN promote lane
    gained the RU lane's unrestored-`{Tn}` refusal ([PR #634](https://github.com/gasyoun/SanskritLexicography/pull/634)).
  - **C3** — EN card-TM was written under the store column `en` instead of the card field
    `english`, so 100 % of EN card-TM hits were silently refused. **C4** — a rate-limited job never
    got its attempt back, permanently stranding it and busy-looping `staged-run` ([PR #636](https://github.com/gasyoun/SanskritLexicography/pull/636)/[#637](https://github.com/gasyoun/SanskritLexicography/pull/637)).
  - **C7** — `build-frags` built the fragment TM from the default tree, ignoring
    `PWG_COORDINATOR_DIR`. **C8** — German glosses opening `In…`/`Ab…` were masked as Latin and
    dropped (1 of 192,763 spans). **C9** — the EN store backup could clobber a same-second recovery
    copy; now µs+pid+uuid + O_EXCL ([PR #640](https://github.com/gasyoun/SanskritLexicography/pull/640)).

### Added

- FINDINGS §458 (H1416, [csl-atlas PR #282](https://github.com/sanskrit-lexicon/csl-atlas/pull/282)):
  the per-letter law — a Sanskrit dictionary's big letters (`a`, `u`, `p`, `s`, `v`) are big
  because they head **preverb families**, so `a`'s 83.1 % compound share is not unique; plus the
  reusable methodological gotcha that testing "entries shrink over serial publication" needs an
  outlier-robust per-letter rank estimator (encyclopedic SKD/VCP have single 300k-char articles
  that give a parametric regression a spurious +733 % slope). Funding-decay hypothesis **refuted
  for SKD/VCP**, real in PWG/PWK/GRA.

- **H803 CLOSED: LaukikaNyaya reaches its ≥400-record target, 404 records (Sonnet 5 `claude-sonnet-5`, picked up via `/next-task`).** Implements the `prev_is_prose()` pipeline-wide fix [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md)'s 20-07-2026 pass had explicitly deferred (verification cost). Root cause: the heuristic rejected any index-crossref candidate whose preceding line was heavy Devanagari, conflating "sits mid-citation" with "immediately follows a different entry's own closing verse." Fix: only reject when that preceding line does NOT itself close with a verse-final daṇḍa/double-daṇḍa. Re-running the fixed pipeline recovers 27 more headword boundaries (base lane 302 → 329) with **zero records lost** (verified by diffing the full boundary set before/after). Because Sanskrit verse padas commonly end in a daṇḍa even mid-citation, every one of the 18 brand-new candidates beyond the known-12 was independently checked by a 2-stage adversarial review (1 initial classifier + 2 skeptic/refuters per GENUINE verdict, 50 agent calls, Sonnet 5 `claude-sonnet-5` ultracode workflow) against the raw OCR context, the book's own back-matter index, and the committed dataset: 15 confirmed genuine (previously swallowed verbatim into the preceding entry's runaway explanation field), 3 rejected as duplicates of content already present under a different OCR lane/spelling. Combined with the 3 of the original hand-verified 12 the fix still can't auto-recover (kept as a documented manual addition), the corrected 329-record base lane reconciles against the unchanged 301-record clean-scan lane to **404 records**, crossing the ≥400 Definition-of-Done target for the first time. New [`LaukikaNyaya/tools/apply_h803_followup2_prevprose_fix.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/tools/apply_h803_followup2_prevprose_fix.py) documents the exclusions/additions. Registered as [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) F45 — closes the last open deliverable of the 2004 AIOC-Varanasi manifesto («Сентенции и афористические цитаты»).

## [1.46.0] — 20-07-2026

### Added

- **PWG→RU speed & orchestration audit — bottleneck ledger + adversarially verified action map (H1403, Fable 5 `claude-fable-5`, 22-agent ultracode workflow).** [`RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md): 5 subsystem miners → synthesis → two adversarial lenses per recommendation. Headline: **0/8 synthesized recommendations survived unmodified (6 weakened, 2 refuted)** — dominant reason "already shipped or already minted", i.e. the speed frontier is executing queued work (H1209 medium50, H390 rule 4(a) instrumentation, three operator-loop residues), not new mechanisms. Ledger top-3: transport availability (6 days at 0 promoted cards with the validated controller-worker lane parked), operator serial loop (generation only ~12–22 % of chain calendar), and the blended clean-rate metric hiding content-clean ~83 % vs transport yield. Also registers the H1225 SANLOSS counter-fix escalation as [`DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §12 — the audit's own synthesis re-proposed that disproven fix, proving the registry gap's cost live — and lands the missing §11 (H1349 W3 vidyut-cheda NO-GO), which `.ai_state.md` referenced but never wrote.

## [1.45.0] — 20-07-2026

### Fixed
- **§102 duplicate-heading collision resolved — the new integrity gate's first live catch (Opus 4.8 `claude-opus-4-8`).** [PR #618](https://github.com/gasyoun/SanskritLexicography/pull/618) (H1328, MW uttarapada × DCS Kompozity divergence) appended a **second** `### §102`, colliding with the incumbent DCS `text_sandhied` §102 and turning the epistemic-integrity gate red on `master` — caught the moment the [v1.44.0 gate](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/epistemic-integrity.yml) went live ([issue #624](https://github.com/gasyoun/SanskritLexicography/issues/624)). Per the [citation-identity ruling](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) rule 4 the later claim moves: the H1328 finding renumbered **§102 → §456** (tombstone + Index entry 🟠), marker → §457. Regenerated `verifiability.json` (114 findings: A 95 · B 12 · C 4 · D 3), STALENESS (114 rows), and both dashboards; integrity gate green.

## [1.44.0] — 20-07-2026

### Added
- **H1362 follow-up: epistemic-integrity gate now runs on every PR + push to master (Opus 4.8 `claude-opus-4-8`).** New [`.github/workflows/epistemic-integrity.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/epistemic-integrity.yml) runs `tools/epistemic_integrity_check.py --structural-only` on any PR touching the registries/dashboards **and** on every push to `master`, opening a tracking issue if `master` ever goes red. Before this the check ran only from the monthly `findings-dashboard` workflow + the local pre-commit hook — which is exactly why the concurrent H1350×H1361 §448–451 collision could merge through two isolated-green PRs and sit red on `master` until noticed. Closes the residual follow-up from the [citation-identity ruling](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) §6.

## [1.43.0] — 20-07-2026

### Added
- **H803 LaukikaNyaya: newly-discovered back-matter index cross-referenced, 377 → 389 records (Sonnet 5 `claude-sonnet-5`).** The `handfulofpopular03jacoiala` clean-scan source turns out to carry its own "ALPHABETICAL LIST OF NYAYAS EXPLAINED IN PARTS I, II & III" at leaves 169-176 — [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LaukikaNyaya/README.md)'s prior "no back-matter index in this source" claim only checked the literal last ~6 pages and missed it (same index already used by `build_laukika_nyaya.py`'s own cross-reference pass, reprinted a second time in this scan). Cross-referencing it against the 377 committed headwords via the project's own rigorous skeleton+gloss-corroboration matcher surfaced **12 genuinely new, individually-verified records** — see [`tools/append_h803_followup_records.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LaukikaNyaya/tools/append_h803_followup_records.py) for the full methodology and root-cause analysis (a `prev_is_prose()` false-negative class in the existing extraction pipeline). FEATURES_INDEX registration still withheld — 389/400 = 97.25%, closest yet.

### Added
- **H1362 FINDINGS verifiability axis — every finding classed by re-derivability (Opus 4.8 `claude-opus-4-8`).** New [`epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md) + machine-readable [`epistemic_dashboard/verifiability.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/verifiability.json) classify all **113** findings into **A** auto-reproducible (94) · **B** re-probeable (12) · **C** historically fixed (4) · **D** not reproducible as stated (3, §69/§85/§450) — each adjudicated from its `> **Source:**` blockquote, and for every class-A finding the cited script was `git ls-tree`-verified to exist (all 94 resolved). The [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) schema now carries the class-D citation rule (a D finding must be cited with its non-reproducibility named); the three D rows are marked in place. Three new [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) rows (§7 →§67, §8 →§71, §9 →§89) reproduce high-value class-A findings that had none. [`derive_staleness.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/derive_staleness.py) gains `--verifiability`: STALENESS's **Re-check recipe** column is now filled from the class (zero `RECIPES §TBD` in the class-A set) and the snapshot counts the true **113**-finding denominator (was a frozen 77). The [epistemic dashboard](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/index.html) renders a `verifiability` block beside the staleness board.

### Fixed
- **H1362 resolved the H1350×H1361 §448–451 collision that left CI red (Opus 4.8 `claude-opus-4-8`).** [H1350](https://github.com/gasyoun/SanskritLexicography/pull/612) (13:58) and [H1361](https://github.com/gasyoun/SanskritLexicography/pull/615) (14:38) concurrently assigned **different** findings to §448–451, and `origin/master` shipped with duplicate headings — the epistemic-integrity gate failing on `master`. Per the citation-identity ruling's rule-4 citation exception (the merged ruling doc itself names the H1361 movers at §448–451, the strongest anchor), the H1361 movers keep §448–451 and the **H1350 PWG block moved to §452–455** with in-place tombstones; the next-free marker advanced `§452 → §456`; the ruling doc gained a §6 documenting it. Integrity check now green (113 distinct headings, Index parity, dashboards in sync).

### Added
- **H1361 epistemic-registry integrity gate + citation-identity ruling (Opus 4.8 `claude-opus-4-8`).** New [`tools/epistemic_integrity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/epistemic_integrity_check.py) enforces the §-number contract over FINDINGS + the seven sibling registries — duplicate-number, heading↔Index parity, dangling-index, next-free-marker, and dashboard↔file count/importance parity — import-free, exits non-zero with a per-defect report; wired into [`findings-dashboard.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml) (structural gate before the builders, full parity check after) and `.pre-commit-config.yaml`. The ruling is [`epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) (append-only · one claim per number · later claim moves with a tombstone · the Index is the classification of record).
- **H1389 union corroboration: text-attestation regrade + post-fold table (Opus 4.8 `claude-opus-4-8`), follow-up to H1363.** (1) **Regrade:** new [`data/mw_ls_textattest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/mw_ls_textattest.py) parses MW's `<ls>L.</ls>` from csl-orig `mw.txt`, reproducing [FINDINGS §97 v2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) exactly (59,697/194,084 = 30.8% of MW headwords carry no text citation); the committed mask [`mw_non_textattested_slp1.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/mw_non_textattested_slp1.txt) drives new `-TA` policies in [`witness_independence_reaudit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_independence_reaudit.py) that count MW as a witness only when it *cites a text*. **Measured result** (supersedes the H1363 ~18,368 estimate): P3 corroborated share 34.7% → **33.8%** (larger drop at P2, 53.1% → 46.2%, where MW is still separate); **17,386 union headwords are MW-listed ghosts** — MW's only dictionary, only listed, **zero text witnesses**. (2) **Post-fold table:** regenerated UNION.md's pre-fold "in N dicts" table on the live post-fold 323,425 file (in ≥2 180,804, singletons 142,621), closing the 237-headword drift. Updates the H1363 report, `witness_tiers.json`, and FINDINGS §103 with measured figures.

### Fixed
- **H1361: FINDINGS/DEAD_ENDS §-number collisions ruled + dashboards corrected.** [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) carried four duplicate numbers (§80, §86, §87, §103) and [DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) three §8 headings; the later/non-cited claim in each moved (FINDINGS → **§448–§451**, DEAD_ENDS → **§9/§10**) with in-place tombstones, the winner keeping the number (published-first / cited). Fixed the `currently §448 → §452` next-free marker, and **backfilled 26 Index entries** (22 headings §76+ absent from the Index, plus the four renumbered). Both dashboard parsers ([`build_findings_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/build_findings_data.py), [`build_epistemic_dashboard.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/build_epistemic_dashboard.py)) now read importance from the Index dot (34 findings carried it only there), so the 27/23 `null`-importance findings are classified and the count is the true distinct-heading total: **95 → 109**, `by_importance` {🔴18, 🟠74, 🟡17} now sums to 109. Regenerated `findings_dashboard/data.json` + `epistemic_dashboard/epistemic.json`. CONTRADICTIONS §6×2 was already resolved by [H1364](https://github.com/gasyoun/SanskritLexicography/pull/604) — extended, not re-touched.

## [1.41.0] — 2026-07-20

## H1389 — union corroboration: text-attestation regrade + post-fold table

Follow-up to H1363, executing the two items it deferred.

**Text-attestation regrade.** [`data/mw_ls_textattest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/mw_ls_textattest.py) parses MW's `<ls>L.</ls>` from csl-orig, reproducing [FINDINGS §97 v2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) **exactly** (59,697 of 194,084 MW headwords, 30.8%, carry no text citation). New `-TA` policies count MW as a witness only when it *cites a text*: the P3 corroborated share falls **34.7% → 33.8%** (measured, superseding the H1363 ~18,368 estimate), and **17,386 union headwords are MW-listed ghosts** — MW's only dictionary, only listed, with **zero text witnesses**.

**Post-fold table.** Regenerated UNION.md's pre-fold "in N dicts" table on the live 323,425 file (in ≥2 180,804, singletons 142,621), closing the 237-headword drift.

Updates the H1363 report, `witness_tiers.json`, FINDINGS §103, FEATURES_INDEX E47.

## [1.40.0] — 20-07-2026

### Added
- **H1363 dictionary witness-independence map + re-audit of the 15-dict union corroboration (Opus 4.8 `claude-opus-4-8`).** The published union "in N dicts" distribution ([`HeadwordLists/union/UNION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)) is read as corroboration, but the 15 dictionaries are not 15 independent witnesses. New [`data/WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md) operationalizes the standing ruling of [FINDINGS §83/§97](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) ("PWG, PW and MW collapse to roughly one European witness"; MW compiled *from* Böhtlingk-Roth) — building the derivation graph and recomputing the corroboration distribution under a 5-rung independence ladder (P0 published 15 → P1 CAE≡CCS → P2 Petersburg lineage → **P3 = §83/§97 ruling, MW folded, 11 clusters** → P4 strict +MD, 10) via [`data/witness_independence_reaudit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_independence_reaudit.py) (+ two derived TSVs). Apte is kept independent per §83 (its named independent control). **Finding:** corroborated share (≥2 witnesses) falls from **55.9%** (published) to **53.1%** (documented Petersburg collapse) to **34.7%** under the established §83/§97 ruling — 68,651 headwords that look multiply-attested rest on a single European lineage; the ≥5-witness "well-attested" tier more than halves. P0 identity map reproduces the live file's `n_dicts` column exactly (regression anchor). Also surfaced: UNION.md's published table is **pre-fold** (sums to 323,662 vs the live post-fold 323,425) — noted in-place. Extends FAIR dataset E40.

### Fixed
- **H1364: CONTRADICTIONS.md duplicate `§6` key repaired + Ch. 14 Zenodo DOI ruled.** Two unrelated rows both used `§6` (Concordance-Q3 plan-set vs the Ch. 14 correction-dataset DOI); §3–§8 renumbered strictly ascending. Live Zenodo check resolves the dispute the collision had buried: `10.5281/zenodo.15834721` is a **false DOI** (resolves to an unrelated topology preprint) — BOOK_PLAN was right, `data/FAIR_RELEASE_1.md` was wrong, and csl-observatory's own `CITATION.cff` carried the same false DOI. All three corrected; see [FINDINGS §103](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## [1.42.0] — 20-07-2026

### Added
- **H1350 PWG data-layers wave (Sonnet 5 `claude-sonnet-5`) — card anatomy, the first formal PWG grammar, full-corpus validation, and four extended extraction layers.** [`docs/PWG_CARD_ANATOMY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PWG_CARD_ANATOMY.md) crosswalks the three existing anatomy descriptions. [`RussianTranslation/schemas/pwg_markup.rnc`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_markup.rnc) is the first RelaxNG grammar `csl-orig` has ever had (39 element tags, including 21 not in csl-atlas's own census); [`validate_pwg_markup.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_pwg_markup.py) and [`validate_pwg_portrait.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_pwg_portrait.py) validate all 123,366 records (122,730+123,366 pass, 0 unclassified). [`audit_sense_glyph.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_sense_glyph.py) full-measured the `〉` sense-glyph fix at corpus scale (93.78% of RU-store rows touch an affected headword) with a read-only, byte-identical-verified store join and a side-file quarantine. [`extend_ls_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/extend_ls_coverage.py) confirmed citation resolution already at 98%+ (not the previously-cited 72.4%) and added a deterministic ibid rule. [`resolve_xrefs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/resolve_xrefs.py) resolved 2,845 new PWG `<ab>s.</ab>` cross-reference edges (shipped as [csl-atlas#274](https://github.com/sanskrit-lexicon/csl-atlas/pull/274)). [`extend_ontolex_xrefs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/extend_ontolex_xrefs.py) layers those edges onto the OntoLex graph as an additive sidecar. Four new FINDINGS entries (§452–455, renumbered from §448–451 per H1362 to resolve the H1350×H1361 concurrent collision). Full plan: [PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md); three follow-on `@DECIDE`s filed in Uprava GTD.

## [1.39.0] — 20-07-2026

### Fixed
- **H1339 Tier-B factory hardening — 20 of 21 still-reproducing H1283 Tier-B defects fixed test-first, including both P0s (adjudication + orchestration Fable 5 `claude-fable-5`; 44 finder/verifier agents on Fable 5 `claude-fable-5`).** Highlights: TM-served whole cards are schema-complete at build AND refused fail-closed at serve (B03, P0 — one TM hit used to poison the whole window at the save gate); heal-stitched cards carry schema-required `iast`/`notes` on both twins (B02); `record.grammar` joined `PROMOTED_COMMON` so the promote-time `{Tn}` residue backstop and `backfill_tn_residue` cover the full store write-set (B21 — the H1283 verifier conflict, resolved); the canonical-store `--merge` is better-attempt-wins (B08); TM sidecars and the RU coverage gate resolve worktree-safely via canonical resolvers (B04/B09 — a fresh-worktree run used to get 0 TM hits and an empty-store coverage verdict); `save_and_audit` refreshes the requeue singletons (B10); `stage2_pregate`/`audit_translation` resolve merged output with the dual `safe_name` lookup (B19); a crashed audit's blast-radius requeue list is refused, and the TM denylist gained an unblock lifecycle cleared by gate-passing promotions (B11/B12); the `translated_source_siglum` trigger fires only on citation-shaped Russian (B13); `perf_preflight` prices per lane — healthy 60K-tok vs pril10 monster 184K-tok calibration (B14); all-null probe-log outcome rows are refused with note-kv recovery (B15); the dispatch roster filters parked/unvalidated accounts before slicing (B16); h1209 lane: null-worker retries, sticky controller rejections, agent deadlines, null-card-tolerant canonical audit (B05/B06/B07); heal/presplit fragment prompts carry per-card grammar + portrait evidence on both lanes (B01). B17 (6h probe-receipt expiry, direct `cmd_staged_run` lane only) deferred with a recorded rationale. `window_selftest` 150 → 157; 9 new `LANG_PARITY` entries; every fix carries a failing-first regression. Matrix + evidence: [`RussianTranslation/pwg_ru/h1339/H1339_TIER_B_STATUS_2026-07-19.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1339/H1339_TIER_B_STATUS_2026-07-19.md).
- **H1339 B23 (P0, found by the new offline benchmark's first end-to-end run): manifest-v2 leases were unauditable.** `window_provenance.stale_check` and `coordinator.read_execution_manifest` accepted only manifest v1 while production profile-bound `prepare` emits v2 — every v2 lease audited `stale_artifact`, so the headless factory chain could never have passed its own audit on a live run (unnoticed because the c4 ladder NO-GO'd before any live `record-output` and all audit fixtures were v1). Both loaders now accept v1+v2; the benchmark exercises the v2 chain end-to-end on every run.

### Added
- **H1339 real unattended requeue materialisation (the H1283 A4 completion).** A bounded-loop requeue work-item now materialises a REAL coordinator requeue attempt (`prepare-requeue`, transient lane before defect) plus a runnable `<lease>::rqNN-<kind>` orchestrator job via the new `import-requeue` command — idempotent at every crash seam, loud when unmaterialisable, with `coordinator_lease_id()` mapping at every coordinator command site; new audited `reset-failed` command is the ONLY exit from the terminal failed-job state (scoped, mandatory reason, events-ledger row). Selftest-pinned end to end.
- **H1339 frozen offline benchmark** — [`src/pilot/h1339_offline_bench.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1339_offline_bench.py) + committed hermetic fixture (12 real PWG keys, 5 leases: clean/requeue/TM-hit/presplit/multi-lease) driving the REAL prepare→audit→promote chain in a per-run sandbox with zero model calls and a deterministic semantic output signature.
- **H1339 hash-pinned population rederivation** — [`src/pilot/h1339_population_rederive.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1339_population_rederive.py): the refuted "~10,199 remaining" premise is replaced by **5,580 unique remaining headwords** (701 verb roots + 4,757 nominal PWG-rooted + 122 no-PWG supplement-chain; the three nominal cores are nested — 6,772-lemma double-count avoided), content hash pinned.

### Changed
- **H1339 measured offline speed — total −23.0% (measured PARTIAL vs the ≥25% target), semantic store equality proven.** Batched multi-lease promotion (`promote_final_cards --batch-manifest` + `coordinator.promote_ready` bundling: one claim → one store read → one better-attempt merge → one backup → one atomic replacement, all-or-nothing, per-lease attribution) cut the store-write stage **−49.8%**; the five audit child gates run in-process via `runpy` (identical script code, captured stdout, same strict parsers/fail-loud path) cutting the gate stack 3.05 s → 0.25 s (audit stage −19.8%). Same-session frozen-fixture medians: 12.08 s → 9.30 s. No concurrency cap or safety gate touched; the remaining dominant stage (per-lease `perf_preflight`/`gen` subprocess spawns) is recorded for the successor.

## [1.38.0] — 19-07-2026

### Added
- **H803 clean-scan lane — LaukikaNyaya 302 → 377 records, real per-entry page citations for the first time (Sonnet 5 `claude-sonnet-5`).** Independently found and OCR'd a different, cleaner archive.org source — three University of California Libraries scans (`handfulofpopular01/02/03jacoiala`, one per Jacob "handful") — after re-confirming the primary `YKTn_...` item's image backend was still down; this alternate source's own OCR text layer is Devanagari-blind, but its IIIF backend worked (a different datanode), so all 378 page images were fetched and OCR'd locally with Tesseract's Sanskrit-aware `san+eng` model. Reconciled against the corrected 302-record file: 223 matched (193 body-upgraded, all gaining a real page citation), 78 genuinely new, 79 kept as-is, minus 3 pre-existing visarga-differing near-duplicate pairs in the 302-set exposed and resolved along the way → **377 records (94.25% of the ≥400 target, the closest yet)**. Also completed the real image-based 20-record-class spot-check the handoff's Definition of Done always asked for (blocked in every earlier pass by the outage), finding and disclosing 2 real OCR errors and fixing 2 real recall gaps (an invisible zero-width non-joiner silently broke the headword-line regex) live. FEATURES_INDEX registration correctly still withheld — target not yet met. See [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md) "Clean-scan lane methodology" for the full writeup, including a caught-and-fixed false-positive in the reconciliation matcher itself.

## [1.37.0] — 19-07-2026

### Fixed
- **H803 dedup + false-positive correction — LaukikaNyaya 390 → 302 records, `/dual-run-salvage`'s reconciliation had two verified defects (Sonnet 5 `claude-sonnet-5`).** The dual-run reconciliation directly below (240+300→390) turned out to contain 57 same-`_ocr_line` duplicate pairs (114 records for 57 physical occurrences, 0 content differences once whitespace is normalized — a dedup-by-`nyaya_slp1` miss caused by two lanes formatting headword whitespace differently) plus 31 further false-positive lines matching the same length-based false-positive signature already established for the unbounded `index-crossref-prefix` strategy. Every one of the 88 removed records is individually accounted for (57 duplicate, 31 false positive) — none dropped without a specific, checkable reason; 0 lines are unique to the corrected 302 that weren't already in the 390's set, i.e. this only ever removes, never misses relative coverage. The dataset is now produced by a single `python build_laukika_nyaya.py` invocation with no manual merge step. See [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md) "19-07-2026 dedup + false-positive correction" for the full audit.

## [1.36.0] — 19-07-2026

### Added
- **H803 dual-run reconciliation — LaukikaNyaya 240 + 300 records merged to 390 (`/dual-run-salvage`, Sonnet 5 `claude-sonnet-5`).** Two independent extraction passes ([PR #577](https://github.com/gasyoun/SanskritLexicography/pull/577), merged; [PR #576](https://github.com/gasyoun/SanskritLexicography/pull/576), open/conflicted) diverged from the same 151-record baseline unaware of each other. Reconciled as a union deduplicated on `nyaya_slp1` (150 records in common, 0 gloss-identity conflicts, 90+150 net-new) — the merged file is a manual reconciliation, not directly reproducible by a single [`tools/build_laukika_nyaya.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/tools/build_laukika_nyaya.py) run. See [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md) for the full accounting.

## [1.35.0] — 19-07-2026

### Added
- **FINDINGS §97 v3 update — PWG lexicon-only audit joins Amara, Rājanighaṇṭu/Trikāṇḍaśeṣa/Nighaṇṭu confirmed unsourceable (H1326, Sonnet 5 `claude-sonnet-5`).** Appends the [SanskritGrammar PR #459](https://github.com/gasyoun/SanskritGrammar/pull/459) result to [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) §97: joining Amarakośa (GNU GPL v3.0, `sanskrit-kosha/kosha`) as an 8th koṣa moved pwg-unique 2,298→2,294 and koṣa-corroborated 10,724→10,812, but left the hardest 788-word "absent from every dictionary" core unchanged. Records the negative result that Rājanighaṇṭu/Trikāṇḍaśeṣa/generic Nighaṇṭu have **no bulk lemma-tagged headword set anywhere checked** (a 126-dictionary scan of `sanskrit-kosha/kosha`, the `cltk/sanskrit_text_dcs` DCS mirror, web search) — only raw unsegmented sandhi-joined verse — and the reusable rule that a "digitise dictionary X" backlog item needs a headword-tagged-vs-raw-OCR check before estimating effort.

## [1.34.0] — 19-07-2026

### Added
- **[FINDINGS §98](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — PD's inline sigla contain a near-homograph pair that similarity-clustering silently fuses** (19-07-2026, Opus 4.8 `claude-opus-4-8`, harvested while scoping [H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md)). The Poona Dictionary has **no `<ls>` citation layer** — it contributes zero edges to [`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv) — so any consumer must regex-harvest sigla from running prose and then normalise variants (measured: 107,630 entries, **99.2 % carry a citation**, 5,231 distinct tokens over 416,767 occurrences, against a plausible ~800–1,500 real works). The obvious normalisation tool fuses the dictionary's two highest-value sources:
  - **`MahāBhā.` (9,339) is the Mahābhārata; `MahāBh.` (1,940) is Patañjali's Mahābhāṣya.** One character apart, not variants. **Verified against actual citation contexts rather than inferred from abbreviation convention** — `MahāBhā.` carries parvan.adhyāya.śloka locators (`vii. 22. 33`) and cross-refs to `BrahmP.`/`ŚabdKaDru.`; `MahāBh.` carries Kielhorn vol.page.line plus an **`({%on%} …)` tail naming the commented rule** (`({%on%} P. viii. 4. 68)`). 1,317 vs 72 distinct locator shapes.
  - **The `({%on%} …)` tail is the robust mechanical discriminator**, not the siglum spelling — a Mahābhāṣya citation names the sūtra it comments on, a Mahābhārata citation never does.
  - Fusing them inflates one node to 11,279 citations and destroys the epic-vs-grammatical distinction that any corpus-coverage or citation-weighting measurement depends on. A blanket "never merge" rule is equally wrong: `Kāśi.`/`KāśiVṛ.` and `PadmP.`/`PadmaP.` in the same frequency head are genuine merges.
  - Also records the other harvest noise classes (structural tokens, language labels, and **secondary scholarship** — `EI.` 3,281, `POK.`, `TURN.`) and the standing caveat that PD is published only `a-` to ~`apaca-`, so any harvested siglum list is PD's canon *as exercised under one letter*, not its full declared canon.

## [1.33.0] — 19-07-2026

### Added
- **One-click case-government (Rektion) index + PW capitalized-marker gap closed (19-07-2026, Opus 4.8 `claude-opus-4-8`, [H1308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1308-Opus_RussianTranslation_pwg-ru-valency-government-index_19.07.26.md))**:
  answers DA-vote row N2 (card `vas~~h0_zz_pw00|samava`) — a searchable government surface plus
  the fix for the PW `zz_pw*` supplement stratum, which writes case markers CAPITALIZED
  (`(<ab>Instr.</ab>)`) that the lowercase-only extractor missed entirely (0 of 1,123 store
  rows, incl. the N2 card). Made the marker regexes in
  [`government_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_census.py)
  case-insensitive (new `_cases()` lowercase-normaliser; one change serves both
  `extract_government()` over the store and `run_census()` over raw `pwg.txt`). Store
  government rows **508 → 1,756** (614 → 2,129 markers); raw `pwg.txt` ceiling **3,853 → 3,905**
  (the +52 are sentence-initial "Mit dem `<ab>…</ab>`" prose government previously missed).
  New `government.html`/`government.js` via `emit_government()` in
  [`build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py):
  case chips → every governing card (Instr. one-click returns 218 cards incl. vas/samava),
  `index.html#g=<safe>` deep-links to the full entry, honest floor-vs-ceiling coverage banner;
  cross-linked with the abbreviations dashboard. `census_stats.json` re-frozen; government
  sidecar regenerated (local-only). SHARED in LANG_PARITY; census + site-builder selftests
  wired into CI.

### Changed
- **LaukikaNyaya phrase-tier recall broadened — 151 → 240 records (19-07-2026, Sonnet 5 `claude-sonnet-5`, [H803](https://github.com/gasyoun/Uprava/blob/main/handoffs/H803-Sonnet_SanskritLexicography_laukika-nyaya-jacob-ingest_12.07.26.md) continuation)**:
  the non-`न्याय` phrase-tier headword gate in [`build_laukika_nyaya.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/tools/build_laukika_nyaya.py)
  was broadened from a literal `"The maxim of"` opener match (4/199 candidates recovered) to
  `looks_like_gloss_sentence()`, verified against all 113 surviving candidates and their 8
  specific identified false positives — named-tier count unchanged (147) confirming the change
  is scoped. `_page_numbers.json` sidecar fetched and found genuinely unusable (11/360 leaves
  page-numbered, none in the body); image-level scan cross-check still blocked by an archive.org
  image-server outage (logged in [Uprava/SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)).
  Still short of the ≥400 stop condition (240/400, 60%) — root cause is a source-availability
  ceiling, not extraction effort; see [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md)
  "19-07-2026 follow-up pass" for full detail. FEATURES_INDEX.md registration remains deferred.

## [1.32.0] — 19-07-2026

### Added
- **Mechanical RU style sweep — no-ё, terse editorial metalanguage (19-07-2026, Sonnet 5 `claude-sonnet-5`, [H1305](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1305-Sonnet_RussianTranslation_pwg-ru-style-mechanical-yo-terseness-sweep_19.07.26.md))**:
  MG's DA-vote (N7/N12 + the terseness half of N4) ratified four deterministic RU style
  rules, applied store-wide and wired for future generation. R1: no letter ё anywhere in
  RU output (whitelist: standalone «всё»/«Всё» only; «всё-таки» defaults to е like every
  other ё-word). R2/R3: «вместо»→«вм.» and «в значении»→«в знач.» in editorial
  metalanguage — measured 0/60 and 0/24 false positives on the canonical store (well under
  the 2% restriction threshold), so both apply unrestricted. R4: `ed. Bomb.` → «Бомбейская
  ред.» in free prose ONLY — 282/283 occurrences sit inside `<ls>…</ls>` citation spans that
  [`pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py)
  keys against PWG's bibliography, so rewriting them would break source resolution; only
  the store's 1 genuine free-prose occurrence was swept. Applied to the canonical store
  (11,603 rows, unchanged): 2,029 substitutions across 1,485 rows, 0 residual violations
  after apply. New
  [`ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py)
  (store sweep + shared violation detector, `--apply`/`--selftest`/`--wf`); new `ru_style`
  gate in
  [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py);
  prompt HARD RULE 9 in
  [`run_pilot_wf.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js)
  (auto-inherited by every future generated harness), pinned in
  [`prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py).
  RU-only by construction — `LANG_PARITY.md` `ru_style_mechanical_yo_terseness`
  INTENTIONAL-DIVERGENCE. Full rule table + measurement:
  [`RU_STYLE_MECHANICAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md).

## [1.31.0] — 2026-07-19

### Investigated — SANLOSS Nachtrag/corrigenda counter fix ESCALATED, no safe fix found (H1225)

- **[H1225](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1225-Sonnet_SanskritLexicography_sanloss-counter-fix-nachtrag-overcounting_18.07.26.md) set out to fix `count_source_senses`'s over-count on H1150's 8 flagged Nachtrag/corrigenda cards — escalated instead, per the handoff's own conflict rail.** Both of H1150's proposed fix directions were tested against the live store and disproven as *general* fixes: partitioning by `— {#headword#}` sub-lemma boundary (cap to 1 on ≥2 distinct names) fixes 5/8 flags but silently caps three real, currently-healthy, genuinely multi-row Nachtrag cards (`_ap~~h3_00_pwg00` 7 rows→1, `vah~~h3_00_pwg00` 3→1, `iz~~h8_00_pwg00` 10→1), blinding SANLOSS to a future drop of nearly all their real senses; the content-verbatim-check alternative is untestable via the existing offline harness, since `softguard_falseflag_measure.py`'s own reconstruction builds "source" and "candidate" from the *same* store rows, making any verbatim-presence comparison tautologically true. Root cause: the fact that actually distinguishes a bundled-into-one-row card from a genuinely-split-into-many-rows card is the model's own generation-time decision, unknowable when `count_source_senses(raw)` runs pre-generation. **No code changed** — `SANLOSS_HARD_REJECT`/`TNMASK_HARD_REJECT` remain `= false`, byte-unchanged. Evidence: [`src/pilot/sanloss_bundling_fix_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sanloss_bundling_fix_probe.py) → [`pwg_ru/h1112/sanloss_bundling_fix_probe.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/sanloss_bundling_fix_probe.json); full writeup: [`pwg_ru/h1112/H1225_SANLOSS_COUNTER_FIX_ESCALATION_2026-07-19.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1225_SANLOSS_COUNTER_FIX_ESCALATION_2026-07-19.md). Provenance: Sonnet 5 (`claude-sonnet-5`), H1225.

### Added — pre-restore {Tn} pairing persisted so the TNMASK false-flag rate is measurable (H1226)

- **`accept()` now persists the pre-restore `{Tn}` pairing TNMASK compares** — the candidate multiset (`got`, `cardTokens(c)`) vs the masked-skeleton multiset (`want`, `tokensOf(INPUTS[k].skeleton)`), stamped on the card as `c.tnmask` **before** `restoreCard` in [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py). Both promote lanes carry it to `provenance.tnmask` on every store row ([`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) RU + [`promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py) EN). [H1150](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md) returned **`DO_NOT_ARM` (denominator 1)** precisely because the store dropped this transient pairing — only post-restore text survived; this makes the rate **measurable offline** going forward. **Braces stripped** (`'T1 T2'`, never `'{T1} {T2}'`) so it never reads as a raw `{Tn}` residue in the store; equality is preserved (same bijection both sides). **Additive + backward-compatible:** the 11,603 existing rows are unaffected and **not** back-filled (0 carry the field; the rate stays honestly UNMEASURABLE, not a fabricated 0, until real windows accrue it).
- **Why only `accept()`:** the heal path's `acceptFrag` hard-rejects fragment `{Tn}` mismatches, so no un-rejected expansion reaches a healed/cached card — the main soft-guard path is the only one where a measurable flag survives. Design note: [`pwg_ru/h1226/H1226_TNMASK_PROVENANCE_DESIGN_2026-07-19.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1226/H1226_TNMASK_PROVENANCE_DESIGN_2026-07-19.md).
- **Offline reader** [`src/pilot/tnmask_offline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tnmask_offline.py) applies the *same* equality (`got != want`) off a promoted row (`tnmask_mismatch` / `tnmask_measurable` / `rate_over_rows`); a future H1150-style pass computes `#mismatch / #measurable`. Proven by [`src/pilot/tnmask_persist_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tnmask_persist_test.js) (extracts the real `accept()` from a generated harness — cannot drift) + `window_selftest.test_tnmask_persist_and_offline_detect` (GREEN with the field, RED/not-measurable without it). LANG_PARITY entry `tnmask_provenance_persistence` (SHARED). **`SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` both remain `= false`** — this makes arming decidable on evidence; arming stays a human `@DECIDE`. Provenance: [H1226](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1226-Opus_SanskritLexicography_tnmask-preserve-prerestore-candidates_18.07.26.md), Opus 4.8 `claude-opus-4-8[1m]`.

### Fixed — German-prose-residue store sweep + 3 rejected-card repair (H1302)

- **Store-wide German-prose-residue sweep** ([report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1302_GERMAN_RESIDUE_SWEEP_REPORT_2026-07-19.md), answering H178 DA-vote rows N16/N17/N19): new detector [`src/pilot/german_residue_scan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/german_residue_scan.py) flags untranslated German prose in the `ru` field outside protected markup (citation *zu*/*bei*, *mit dem <ab>acc.</ab>*, *so v. a.*, connectives, *mit Ergänzung von*), classing each hit a=deterministic / b=retranslate / c=proper-name-FP. **Detector precision 50/50 = 1.00** on a hand-classified sample; the deterministic [`fix_german_connectives.py --store`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_german_connectives.py) pass fixed **690 hits across 486 rows** in the canonical store (citation `zu`→«к», `bei`→«у», `mit Ergänzung von`→«с восполнением», `Mit {#prefix#}`→«С», und/oder/ohne/auch). 465 class-b hits (273 rows / 45 roots) parked to a committed requeue worklist for the next `--no-tm` window.
- **3 rejected cards repaired + re-promoted in place** ([`repair_h178_da_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/repair_h178_da_cards.py)): `nI|…|5)` "Schol. zu"→«Schol. к» (N16), `DA|…|8` "mit Ergänzung von"→«с восполнением» (N19), `gam|…|1` doublet→single attested «возвышаться» (N17); each keeps `review_status=ai_translated` with a `provenance.repairs` note. KATHĀS. 26,9 (N17 arbiter) is absent from every local TM → citation check deferred to [H1304](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1304-Fable_RussianTranslation_pwg-ru-covered-texts-citation-tm-registry_19.07.26.md).
- **Prevention (SHARED RU+EN):** shared residue token list in [`foreign_literal_guards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/foreign_literal_guards.py) wired into the RU gate (`prompt_rule_audit`) and EN gate (`audit_window_en`, German-only subset); LANG_PARITY entry `german_prose_residue_h1302` (SHARED); prompt rule added to `1_perevod.txt`/`run_pilot_wf.js` with `prompt` component bumped 1.0.0→1.1.0; `window_selftest.py` fixture added (148/148 green). Provenance: [H1302](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1302-Opus_RussianTranslation_pwg-ru-german-residue-sweep-reject-repair_19.07.26.md), Opus 4.8 `claude-opus-4-8[1m]`.

### Added — citation translation-memory: reuse RU translations of record for PWG citations (H1304)

- **[`pwg_ru/COVERED_TEXTS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/COVERED_TEXTS_RU.md)** — census of every text with a Russian translation asset, crossing PWG `<ls>` citation frequency (36,546 distinct refs / 709 abbreviations, via `build_citation_index.py`) against the 119 verse-aligned works in SamudraManthanam `corpus.db` and the 23-work Ignatiev archive. The high-value intersections (MBH. 5,512 refs · ṚV. 3,433 · R. 2,970 · KATHĀS. 1,419 · Manu 1,444 · AV. 1,110 — all verse-aligned) plus the gaps (ŚAT. BR. 1,620 · HARIV. 867 · SUŚR. 277 — no RU; MBH-continuous-Calcutta and R. GORR.-Bengal-recension — no locus concordance). Includes the Ignatiev ingestion queue (Bhāgavata-purāṇa = the top gap), the translation-of-record policy + card schema (`citation_ru` / `citation_ru_src` / `divergence_note`), the per-text locus-mapping scheme, and the retro-application plan. Metadata/counts/loci only — no in-copyright translation text (public repo).
- **[`src/citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py)** — `lookup(prefix, locus)` maps a PWG citation to its corpus passage and returns the RU translation of record (generation-time consult only, never persisted). Two layers: a DB-independent resolver (R./ṚV./AV./Manu clean; KATHĀS. best-effort) and a DB-gated `corpus.db` fetch. Typed non-hits: `text-not-covered` (TS., N18), `locus-not-in-corpus` (uningested Rāmāyaṇa kāṇḍas), `unmapped_locus_scheme` (MBH. Calcutta↔critical + R. GORR. Bengal recension — documented concordance GAPs, **not** misses). `consult_card()` is wired into `corpus_gate.build_card` as an additive, import-guarded `citation_reuse` field. `python src/citation_tm.py selftest` (R. 2,91,26 → hit · TS. 2,3,1,4 → clean miss · MBH./R. GORR. → unmapped) hooked into the CI gates job; parity ledger records the RU-only lookup as INTENTIONAL-DIVERGENCE (no EN citation-TM corpus exists). Provenance: [H1304](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1304-Fable_RussianTranslation_pwg-ru-covered-texts-citation-tm-registry_19.07.26.md), Opus 4.8 `claude-opus-4-8` (Fable-locked handoff, MG-authorized tier override).

### Added — gaṇa membership wired into the pwg_ru derivation layer (H1282 follow-up)

- **`pwg_derivation_layer.py` + `enrich_portrait_derivation.py` now carry the Pāṇinian gaṇa** from the external Gaṇapāṭha join ([SanskritGrammar PR #445](https://github.com/gasyoun/SanskritGrammar/pull/445)). The sidecar gains `ganas · gana_sutras · gana_corroborated`, and the portrait block a `gana` sub-block (gaṇa(s) + governing sūtra(s) + a `corroborated` flag when PWG cites that sūtra). **3,264 index rows** get a gaṇa (k1-level — membership is lexical). e.g. aṃśa → saṅkāśādiḥ / P.4.2.80. `--selftest` extended. Opus 4.8 `claude-opus-4-8[1m]`.

### Changed — PWG derivation layer now homonym-precise (H1282 follow-up)

- **`pwg_derivation_layer.py` + `enrich_portrait_derivation.py` upgraded from k1-only attach-all to homonym-precise** via the new SanskritGrammar [`pwg_lid_hom_map`](https://github.com/gasyoun/SanskritGrammar/tree/main/data/pwg_lid_hom_map) (PWG states each entry's homonym as `<h>N`; 100 % of this index's `(k1, hom)` pairs resolve). Derivation and compound carry per-occurrence `L_id`, so each is now pinned to the **exact `(k1, hom)`** — **21,915 of the sidecar's rows are homonym-pinned** (was 0); the enrich script matches each portrait's homonym from its `~~h<N>` filename token and attaches the matching block, k1-level fallback otherwise. Pāṇini stays k1-level by design (its `word2sutra` is headword-aggregated). Sidecar column `homonym_ambiguous` → `homonym_precise`. `--selftest` extended (filename-homonym parse). Opus 4.8 `claude-opus-4-8[1m]`.

### Added — PWG derivation layer for the lexicographic portraits (H1282)

- **PWG derivation/Pāṇini/compound layer joined onto the headword index** ([`src/pwg_derivation_layer.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_derivation_layer.py) → committed sidecar [`src/pwg_derivation_layer.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_derivation_layer.tsv)). Joins the three SanskritGrammar PWG data layers onto `src/headword_index.tsv` by `k1`: **39,266 headwords** gain ≥1 layer — derivation (taddhita base+suffix+class+`<ls>` citation) **5,730**, Pāṇini licensing sūtra(s) **22,322**, PWG compound split **16,788**. Compound is a **cross-check** against the index's existing `compound_members` (47% filled): PWG **agrees 6,176 · fills 6,382 gaps · differs 4,230** (the differs are a review queue). Homonyms: attach-all-and-flag (`homonym_ambiguous`), the same policy as `enrich_portrait_grammar.py`, since no `L_id↔hom` map is committed upstream. Deterministic; reads the canonical SanskritGrammar datasets read-only.
- **[`src/pilot/enrich_portrait_derivation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/enrich_portrait_derivation.py)** bakes a `derivation` block (sibling of `grammar`/`corpus_synonyms`) into a headword's local portraits from the sidecar, following the `enrich_portrait_grammar.py` pattern (dry-run / `--apply`). The portrait store (`pilot/input/`) is local-only, so `--apply` runs on the maintainer's local portraits; a `--selftest` proves the block-attachment logic (attaches to every homonym, preserves fields, sidecar parses). Provenance: [H1282](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1282-Opus_SanskritLexicography_pwg-ru-derivation-portrait-enrichment_19.07.26.md), Opus 4.8 `claude-opus-4-8[1m]`.

### Added — H1110 Phase 6 terminal record + Phase 3/7 residue closed

- **Phase 6 bounded c4 ladder terminated at `HEALTH_NOGO_BY_ENVIRONMENT`** ([PR #534](https://github.com/gasyoun/SanskritLexicography/pull/534),
  confirmation reading [PR #538](https://github.com/gasyoun/SanskritLexicography/pull/538)). The c4 profile is
  mechanically proven bound (`config_dir_fingerprint e96ee464…`, validated roster slot) and every offline
  gate is green, but the measured c4 health latency is **98,625 ms against the strict 30,000 ms ceiling** —
  a `success`/pure-latency reading, not auth or connection, and essentially unchanged from the 16-07
  reading of 104,870 ms. **1 paid confirmation call; canary and batch unspent; zero promotions, zero
  canonical-store writes, zero TM rebuilds.** Resume is one health probe per demonstrated-recovery
  window, never a reroll. Terminal record:
  [H1110_PHASE6_C4_LADDER_HEALTH_NOGO_BY_ENVIRONMENT_2026-07-18.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1110/H1110_PHASE6_C4_LADDER_HEALTH_NOGO_BY_ENVIRONMENT_2026-07-18.md).
- **The production execution route is now the headless CLI (manifest v2)**; the Workflow-from-session
  run route is retired and is forensics metadata only. Recorded as a standing section in
  [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
  so an older runbook's "run it as one `agent()` call from THIS session" no longer reads as current.
- **FINDINGS §93 — declared, validated, and never enforced.** The audit's headline finding (the headless
  executor read a manifest `budgets{}` block it did not obey, with every offline gate green) generalised
  into the execution-route parity discipline: grep for the *enforcement* site, not the config key.

### Added — enforceable coordinator runtime state machine

- Prepared translation leases are now reservations, not runtime. `begin-run` atomically moves a
  batch to `running`; `record-output` requires that reservation and releases it through `auditing`.
  Ordinary execution is capped globally at three. A fourth slot exists only for `staged-run` with
  a fresh, run- and lease-scoped four-profile probe receipt; a fifth lease always fails closed.
- `release-run --confirm-dead --reason ...` records abandoned attempts and restores their prior
  prepared state. `recover-operation --confirm-dead` recovers stale preparation/audit tokens, while
  compare-and-swap completion checks prevent an old subprocess from overwriting newer lease state.
- Preflight, harness generation, normalization, requeue generation, and audit now run outside the
  coordinator state lock with explicit 10-minute preparation and 30-minute audit timeouts.
  Dashboards distinguish reserved and running leases and retain `active_translation_leases` as a
  one-cycle deprecated alias of the running count.
- The four-profile orchestrator writes a credential-safe probe receipt, reserves every dispatch
  batch before workers start, releases retryable/failed workers, and routes successful workers
  through the required audit transition. Real contention tests also closed the mkdir/`owner.json`
  lock-creation race that could previously admit two simultaneous claimers.

### Fixed — canonical-store backup and nominal lease collision safety

- Promotion backups now use exclusive, collision-resistant names and never move or overwrite
  the live canonical store. Identical recovered workflow cards deduplicate, while divergent
  translations or generation provenance fail closed before promotion.
- Nominal coordinator leases persist every canonical input key in `reserved_keys`. Legacy
  active leases are migrated from claim details or execution manifests; an unresolved active
  reservation blocks new nominal work instead of permitting an overlapping paid run.

### Added — H1150 W1-B: offline false-flag rate for `SANLOSS_*`/`TNMASK_*`, with a per-guard arming recommendation

- **Measures; does not arm.** `SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` in
  [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  both remain `= false`, byte-unchanged. Arming stays a human `@DECIDE`.
- New committed measurement scripts: `src/pilot/softguard_falseflag_measure.py` (verifies
  `pwg_ru/h963/artifact_manifest.sha256` against the git **blob** content first — the
  Windows `core.autocrlf` checkout makes a raw `sha256sum -c` spuriously fail on every text
  file — then recomputes SANLOSS `source_senses` via the real, imported
  `sense_count.count_source_senses` over the promoted store) and
  `src/pilot/softguard_falseflag_accept_run.js` (runs the **REAL** `accept()`, extracted
  verbatim out of an offline-generated harness, the `accept_sensecount_test.js` technique —
  never a hand-copied re-implementation, the [Uprava FINDINGS §82](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
  anti-pattern).
- **SANLOSS: `FIX_COUNTER_FIRST`.** 8/8 flags found in the frozen promoted-store evidence
  (865-card denominator) are false flags (0 true drops) — every one is a Nachtrag/corrigenda
  card bundling correction points across multiple distinct sub-lemma blocks into one stored
  sense; `count_source_senses` correctly finds each sub-block's own line-opening ordinal (a
  class H960's mid-prose cross-reference hardening doesn't target), inflating the expected
  count even though no content is missing. Fix suggestion recorded in the report.
- **TNMASK: `DO_NOT_ARM`.** Zero usable frozen evidence: TNMASK's real check compares the
  pre-restore candidate to the masked source skeleton, and the promoted store holds only
  post-restore text — that pairing is not preserved for any real historical card. Zero
  residual `{Tn}` tokens across all 11603 promoted rows (corroborating H1110 C-42) and zero
  non-zero `tnmask_mismatches` readings anywhere in the tracked repo. Insufficient-evidence
  verdict, not a verdict on the guard's expected quality.
- Output: [`pwg_ru/h1112/softguard_falseflag_rate.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/softguard_falseflag_rate.json) +
  [`H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md).
  Honest limit stated in both: frozen evidence is one route under one payload regime — the
  rate bounds the false-flag class, it does not prove the live rate. Regression gate
  re-measured green: `window_selftest.py` 142/142, `lang_parity_check.py` clean, both
  `HARD_REJECT` consts unchanged.

### Added — H1152: the EN lane's three offline guards named by H1070's conditional GO (scaffolding, not activation)

- **Honest framing, stated once and not softened anywhere in this entry:** none of this
  unblocks the EN lane. The store still carries **0 EN rows**; `promote_en.py` was not run
  (`git diff origin/master --stat -- src/pilot/promote_en.py` is empty); no live judge call was
  made. This is offline scaffolding so H1070's conditional GO is cashable the hour a
  judge-tier profile frees — a human `@DO`, not something this session performed.
- **Guard 2 (the only hard guard) — root cause, not a counter patch.** `accept()`'s
  `<ls>`/`{#..#}` fidelity check (`countOf()` in
  [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py))
  counted spans **only in `sense.german`**, the source-echo field the model reproduces
  verbatim — never in the actual translation field (`sense.english`/`sense.russian`). Proven
  against the live H1070 r102 row (`vac~~h0_00_pwg00`): `german` carried 33/33 expected
  `{#..#}` spans (the pre-existing check passed clean) while `english` carried only 32/33 —
  the `{#uc#}` inside a `<F>` footnote was dropped **only** from the field this guard never
  inspected. Added `countOfField(card, field, re)` and a second hard check in `accept()`
  running the identical count over the real target-language field (`TARGET_FIELD`, the same
  `field` constant already used to build `RESTORE_SPEC`). Landed in the accept path (not the
  `audit_window_en.py` HARD-flag fallback H1070 named) — SHARED code, both lanes get the
  fix. Fixture: [`accept_sensecount_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/accept_sensecount_test.js)
  reproduces the exact r102 shape, proven RED before this change (against the pre-fix
  `accept()` via a `git stash` diff, the fixture is silently accepted) and GREEN after.
- **Guard 1 (cheap):** a German-polyseme checklist under `term-mistranslation` in
  [`gen_fidelity_judge_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_fidelity_judge_en.py)'s
  judge RUBRIC (Vergleich, braut/Braut, gelten, Zug, anführen, …) and a matching HARD RULE 5
  in [`tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tr_en.txt):
  pick the sense the Sanskrit lemma licenses, never the frequent German sense. Markup stays
  intact and the English reads fluently for this error class (H1070 r155/r119) — no
  deterministic gate can see it, so this is judge-rubric + prompt only.
- **Guard 3 (cheap):** extended
  [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py)'s
  soft-flag machinery with `XREF-ONLY` (a sense whose German is nothing but a
  cross-reference apparatus — "Vgl. {#foo#} fgg.") and `NWS-DE-LOCKED` (German prose trapped
  inside a `{#..#}` span — an NWS masking miss that never reached the translator), so
  coverage stats stop counting H1070's dominant residual class (12/170 FU1 rows) as
  translated. Both SOFT — never `--strict`-blocking.
- [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md):
  3 new ledger rows (guard 2 `SHARED`; guards 1 and 3 `INTENTIONAL-DIVERGENCE`, each with its
  EN-only rationale) plus 38 collateral hash refreshes (`--update-hash`, no logic touched —
  pure same-file co-location drift from this session's purely-additive diff, individually
  confirmed against the diff before refreshing). `lang_parity_check.py` clean at 53 entries
  (baseline **50**, not the handoff-cited 49 — `origin/master` has moved since H1152 was
  minted).
- `window_selftest.py`: 2 new content-check tests
  (`test_h1152_guard1_en_polyseme_checklist`, `test_h1152_guard3_xref_only_and_nws_de_locked`);
  the existing `test_h960_accept_sanloss_soft_gate` now also exercises guard 2 via the
  updated `accept_sensecount_test.js`. Full suite: **139/139 green** (baseline measured this
  session: **137/137**, not the handoff-cited 135/135 — same staleness).

### Added — H1110 Phase 2: enforce headless fidelity and spend bounds (12 live-route gaps)

The post-H1080 audit ([PR #524](https://github.com/gasyoun/SanskritLexicography/pull/524)) ranked 12
live-route gaps; this fix closes them, each behavior-pinned (assert the value at the executing
boundary, not a constant):

- **R3 agent-budget enforcement** — `headless_worker.py` enforces `manifest['budgets']`
  (`max_translate_agents`/`max_heal_agents`/`max_agents`) + a `--max-agents` override at the `call()`
  choke point; a refused call consumes no spawn. The budgets block was previously never read by the
  executor.
- **R4 timeout clamp** — every subprocess clamped to `min(operator, budgets.timeout_ceil_ms, 180000 ms)`.
- **R5 cost telemetry** — the CLI wrapper's usage/cost survive into `summary['usage']` (summed across
  calls, authoritative `observed_cost_usd`, `cost_evaluable`, `missing_usage_calls`) instead of being
  discarded — no more silent `STOP_COST_UNEVALUABLE`.
- **R2 grammar-token twin** — `card_token_multiset` counts `record.grammar` + `sense.german` via the
  shared `card_fields.TOKEN_FIDELITY_FIELDS`, matching JS `cardTokens`.
- **R6 fragment-TM v2** — per-sense `owners[]` flow harvest → sidecar → serve → stitch; a v1
  (ownerless) row is a live cache miss (re-translated, still audit-readable), so a warm stitch no
  longer regenerates null-`h` rows.
- **R7 degenerate-card schema** — a degenerate stub emits `{h:'', grammar:''}` (honest source
  identity), so `validate_final_card_schema` passes and one xref stub cannot refuse a whole paid window.
- **R8 / P-1 manifest gates** — duplicate `selected_keys` rejected (multiset via `Counter`);
  `batches`/`presplit` keys outside `selected_keys` refused before any spawn.
- **R9 kernel-backed active-call lock** — `ActiveCallClaim` holds an OS lock (fcntl/msvcrt) the kernel
  releases on process death (no PID/TTL/stale reclaim), so a tree-kill no longer strands a permanent
  per-profile DoS. This is also the P-2 cross-process serialization ("two launches on one fingerprint
  serialise"); `max_wide`/`stagger` are marked advisory intra-process hints.
- **P-3 route enforcement** — a foreign `execution_route` is refused at execution, before any call.
- **R10 `--stop-before-promote`** — skips promotion and writes a durable, self-hashing, hash-bound
  `AWAITING_REVIEW` terminal checkpoint after a clean audit (store and TM untouched; audit-rejected
  output never becomes AWAITING_REVIEW).

### Changed

- Operator docs (`AGENTS.md`, `README.md`) now name the **headless / manifest-v2** route as
  production; the Max-Workflow lane (`run_pilot_wf.opt2.js`) is retained for forensics only.

## [1.30.0] — 19-07-2026

### Added
- **`<ls>` link enrichment — Pāṇini deep/browse links + Spr. (II) full-text tooltips (19-07-2026, Opus 4.8 `claude-opus-4-8`, [H1307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1307-Opus_RussianTranslation_pwg-ru-ls-link-enrichment-panini-spr-dhatup_19.07.26.md))**:
  MG's DA-vote (N14/N3(b)/N15) enrichment for three `<ls>` citation classes in the pwg_ru render
  layer. Pāṇini `P. a,p,s` deep links to [ashtadhyayi.com](https://ashtadhyayi.com) were already
  100% (25,061/25,061); guarded 2-param/1-param patterns add the pāda/adhyāya browse routes
  (`/sutraani/a/p`, `/sutraani/a`) — pada 1–4, adhyāya 1–8 guarded so page-refs like `P. II, S. 3`
  never mislink. Every `Spr. (II) N` (8,684, 100% linked) gains an IAST+German hover tooltip from
  [`indische_sprueche.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl)
  (7,537 sayings) behind a 1st-edition guard (plain `Spr. N` never resolves against the 2nd-ed corpus).
  URL forms verified against the ashtadhyayi.com backing data repo (the site is a client-side SPA) and
  the boesp1/boesp2 viewer JS (bare `?N` is the only form working for both editions). `DHĀTUP.` → Palsule
  exited as a committed acquisition spec (no machine-readable Palsule list exists org-wide; the Westergaard
  gaṇa-level link stays). New [`spr_fulltext.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/spr_fulltext.py),
  [`ls_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_coverage.py),
  fixture selftest in CI; coverage table + spec in
  [`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md).

## [1.29.0] — 19-07-2026

### Changed
- **Renou Step-0 pilot sheet remade (v2) — per-state named evidence (19-07-2026, Fable 5 `claude-fable-5`, [H1311](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1311-Fable_RussianTranslation_renou-pilot-evidence-remake_19.07.26.md))**:
  MG voted 3/70 v1 cards (all reject, [review/decisions.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions.md))
  — all three rejections traced to one defect: the evidence panel showed lemma-global
  facts (oldest text overall, bare counts) under a question about one specific state.
  New [`renou_pilot_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_pilot_evidence.py)
  collects the full per-text DCS attestation list per sampled lemma (name, date, state,
  confidence, registers; text→state resolution imported from `build_dcs_renou` verbatim)
  and joins the SanskritGrammar [pwg_register_genre](https://github.com/gasyoun/SanskritGrammar/blob/main/data/pwg_register_genre/README.md)
  layer by SLP1 k1; the rebuilt sheet names the contested-state texts, lists the full
  attestation surface, states a per-state judgment criterion (état II: Aṣṭādhyāyī
  quotation suffices — per the S0-002 ruling; Manusmṛti is état III, never Vedic — per
  S0-001), and renders the three v1 notes as prior-vote context. Sheet_id →
  `renou-pilot-v2-2026-07-19`; v1 3-vote export committed as the methodology record.
  Response doc incl. the ACC/NCC source-markup design answer:
  [`RENOU_PILOT_EVIDENCE_REMAKE_19.07.26.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_PILOT_EVIDENCE_REMAKE_19.07.26.md).
- **One review-sheet standard: every pending SanskritLexicography sheet remade on csl-pyutil v0.3.0 (19-07-2026, Fable 5 `claude-fable-5`, [H1313](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1313-Fable_SanskritLexicography_review-standard-v030-orgwide-remake_19.07.26.md), executing [H1301](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1301-Opus_RussianTranslation_pwg-ru-review-sheet-ux-standard-regen_19.07.26.md) per MG's direct order)**:
  the V1–V8 rulings from the h178_da vote ([register §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md))
  shipped as [csl-pyutil v0.3.0](https://github.com/sanskrit-lexicon/csl-pyutil/releases/tag/v0.3.0)
  (rating 1–5 below the card with approve-coupling + `rating` export field, visible id
  chips, clickable IAST headword links, taller notes, `mark_cyrillic()` RU highlighting,
  sheet_id+save-path banner) and consumed here: new shared helper
  [`RussianTranslation/src/review_sheet_standard.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_sheet_standard.py)
  (root→PWG-column kosha deep links, SLP1→IAST); ports of
  [`h178_eval_bakeoff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h178_eval_bakeoff.py)
  (DA slider → emitter 1–5 rating; RUBRIC_JS export carries `rating`),
  [`build_h180_review_sheets.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h180_review_sheets.py)
  (hand-rolled donor → emitter consumer, fixing its bare `decisions.json` download name),
  [`build_renou_pilot_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_renou_pilot_sheet.py),
  NEW [`build_kochergina_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_kochergina_sheet.py)
  (the hand-authored 4-row sheet gains a generator AND its missing decisions export, with a
  localStorage vote-migration shim), and
  [`article-comparison/_build_gloss_review_sheets.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/_build_gloss_review_sheets.py);
  13 pending sheets regenerated. The h178 sheets render the frozen 30-gloss sample, so
  bake-off comparability with the voted DA arm is preserved — the remaining three h178
  votes are now UNBLOCKED. csl-atlas (JS stack) and SanskritGrammar (hand-authored
  skeleton) ports queued as
  [H1314](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1314-Opus_csl-atlas_review-sheets-standard-port_19.07.26.md)/[H1315](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1315-Opus_SanskritGrammar_review-sheets-standard-port_19.07.26.md);
  two SanskritGrammar sheets found already fully voted on disk (precative 7/7,
  w2-core-11 12/12, index rows were stale) → apply handoff
  [H1316](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1316-Opus_SanskritGrammar_apply-voted-precative-w2core-visas_19.07.26.md).

## [1.28.0] — 19-07-2026

### Added
- **H178 DA-sheet vote processed → 8-handoff work-stream fan-out H1301–H1308 (19-07-2026, Fable 5 `claude-fable-5`, [H1300](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1300-Fable_RussianTranslation_h178-da-vote-processing_19.07.26.md))**:
  MG's first bake-off vote (`h178_da`, 30 promoted pwg_ru glosses: 27 approve / 3 reject,
  partial 15/30 DA numeric channel) filed to the
  [H274](https://github.com/gasyoun/Uprava/blob/main/handoffs/H274-Fable_DO_RussianTranslation_pwg_ru_bakeoff_compute_07.07.26.md)
  contract path (local-only `pwg_ru/eval/h178_da.decisions.json`; evidence copies under
  `D:\ClaudeTools\evidence\`); all 8 sheet-system rulings (DA 1–5 buttons below card,
  visible card IDs, IAST headword links, Publishable→DA≥4, RU-token highlighting,
  sheet↔decisions binding standard) + 20 content issues (German residue in RU fields,
  abbreviation policy, citation-translation reuse incl. Elizarenkova/KATHĀS./Leonov,
  no-ё + terseness style, doublet policy per Apresyan, Pāṇini/Spr./DHĀTUP. link
  enrichment, valency index) extracted into
  [`RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md)
  and fanned out into nine atomically-minted handoffs (H1300–H1308) with execution
  gates (sheet regeneration only after the German-residue + mechanical-style sweeps
  land). The 10-07 stay-Latin abbreviation ruling vs the 19-07 translate-them vote
  notes logged as [CONTRADICTIONS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
  (resolution path: H1303 ratification sheet).

## [1.27.0] — 19-07-2026

### Added
- **A67 negative-results methods paper drafted + full failure adjudication (18/19-07-2026, Fable 5 `claude-fable-5`, [H1268](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1268-Fable_SanskritLexicography_negative-results-dead-ends-methods-paper_18.07.26.md))**: the programme's first negative-results paper, [papers/A67_negative_results_computational_sanskrit_lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_computational_sanskrit_lexicography.md) — 46 recorded failure candidates harvested from both DEAD_ENDS registries, both CONTRADICTIONS registries, FINDINGS, and the ⚫ RETIRED work-registry rows, each adjudicated INTRINSIC / INCIDENTAL / UNDERPOWERED / REVERSED / OUT-OF-SCOPE with per-row rationale in the committed audit trail [papers/A67_negative_results_adjudication_table.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_adjudication_table.md). Verdict distribution 21+1 enter / 12+5 excluded / 7 out-of-scope — fewer than half of recorded failures survive as scientific negative results, itself the paper's first result. Four-class taxonomy (missing-signal · lossy-key · wrong-witness · statistical-artifact), the §8b MBH reversal as the falsifiability case study, venue shortlist (Insights from Negative Results in NLP · LRE · DSH). Fact-check pass ran before commit: a read-only verification agent checked every number/attribution against its cited source; its 10 findings (one invented detail, one wrong availability statement, a missed candidate, the I12 arithmetic wrinkle in DEAD_ENDS §8's 37.7%, and attribution fixes) are applied and disclosed in both files. Registered as **A67** (readiness 2/5) in [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) the same pass.

## [1.26.0] — 18-07-2026

### Added
- **M01 monograph complete in draft — Ch. 3 + Ch. 11 written, 14 of 14 chapters in book form (18-07-2026, Fable 5 `claude-fable-5`, [H1240](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1240-Fable_SanskritLexicography_m01-ch03-a40-ch11-a50-data-chapter-prose_18.07.26.md))**: the last two chapters land as [ch03_headword_inventory.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch03_headword_inventory.md) (← A40: the 2014-vs-2026 census +14.3 %, the 15-dictionary union's overlap structure, and the corpus-grounding bridge — attestation VEI 69.8 % … SKD 14.1 % on the DCS-2021 denominator, read as coverage geometry under ch02 §6.2; the reverse DCS↔CDSL crosswalk stated at its true 13-text-pilot scope with wf0-floor semantics) and [ch11_citation_frequency_graph.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch11_citation_frequency_graph.md) (← A50: the 828,505-citation / 912-text frequency graph written to ch02 §6.3's effect-sizes-first contract; the text→tradition map stated as **inferred, 0/119 human-reviewed**, in text and tables; the ch10-vs-graph-builder `<ls>` extraction conventions reconciled — bare vs attribute-bearing tags). Both turned out to be journal→book **conversions** (A40 full prose per H675, A50 per H677 — the "data-only, first-drafting" premise was stale). Same pass: the Part II/IV bridge ⚠️ boxes resolved against the merged chapters; an **attestation/absence semantics inversion fixed** in ch02 §6.2/§6.4 and BRILL_PROPOSAL (the 69.8 %…14.1 % range is attestation, not absence, per A40 §4.4); book CHANGELOG, BOOK_PLAN §11 done-entry + still-to-do renumber, and BOOK_PLAN.meta backlog #1/#2 ticked.

## [1.25.0] — 18-07-2026

### Added
- **M01 monograph glue drafted — Introduction + 5 part-bridges + Conclusion (18-07-2026, Fable 5 `claude-fable-5`, [H1241](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1241-Fable_SanskritLexicography_m01-introduction-part-bridges-conclusion-glue_18.07.26.md))**: the connective tissue that turns the 12 committed chapters into a monograph rather than an anthology — 7 new files in [Digital_Sanskrit_Lexicography-BOOK/chapters/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK/chapters). The [Introduction](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch00_introduction_two_civilizations.md) is seeded from **A61's serial-infrastructural-conversion argument** per MG's 18-07 ruling (chronicle/testimony/quotations stay in the WSC paper; no A61 permission gate touched; the book does not cite A61 — the ruled ordering has A61 citing the book). The [Part III bridge](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/bridge_part3_microstructure_civilizations.md) carries the crosswalk §4.1 comparative upgrade (Baalbaki order/witness/copying, Ferri per-essay, Dickey). Part II/IV bridges flag their H1240-pending Ch. 3/11 sections at plan altitude with boxed ⚠️ revision obligations. The [Conclusion](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/conclusion_evidence_graph.md) argues the evidence graph as a general model with explicit transfer conditions and an honest FAIR/κ self-audit. All 12 vetoable framing calls parked for the author in [SIGNOFF_M01_glue_framing_calls.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/SIGNOFF_M01_glue_framing_calls.md) (MG `@DO`); book CHANGELOG, BOOK_PLAN §11, BOOK_PLAN.meta backlog #5 and `.ai_state.md` ticked in the same pass.

## [1.24.1] — 18-07-2026

### Added
- **H1110 closeout residue — Phase 6 record propagated, Phase 2 doc gaps closed (18-07-2026, Opus 4.8 `claude-opus-4-8`)**: an independent 6-phase fulfilment verification of [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) (10 agents, adversarial refutation per COMPLETE verdict) found Phases 1–6 delivered but three documentation obligations from Phase 2 item 11 and Phase 7 never landed. Closed here: **[FINDINGS §93](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)** (declared-validated-never-enforced; the execution-route parity discipline that surfaced it, plus the 8-fixed/38-open/2-refuted shape of the C-01…C-59 re-execution), a standing **execution-route section in [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)** recording that the headless CLI (manifest v2) replaced the retired Workflow-from-session route and that degradation is now measured per run rather than asserted from a date, and the **Phase 6 `HEALTH_NOGO_BY_ENVIRONMENT` entry** in the pwg_ru changelog. Verification also **refuted three further reported gaps as stale-clone artefacts** — the github-spine `SKILLS_INDEX.md` rows, the Uprava G46 wiring, and H1110 Phase 3's Codex half ([codex-config PR #2](https://github.com/gasyoun/codex-config/pull/2)) were each already delivered on their default branches, and only appeared missing when read from a local clone lagging behind (the H1245 false-FAIL class; the canonical SanskritLexicography clone sat on a *deleted* branch 78 commits behind `origin/master`, which is also what made `goals_check.py` report G46's on-disk pilot scripts as stale). A redundant Codex re-port authored against the stale clone was discarded rather than pushed. **Standing lesson: `git fetch` before believing an absence — a verification agent reading a working tree measures the clone, not the repo.** No paid call was made; the c4 ladder remains host-blocked.

## [1.24.0] — 18-07-2026

### Added
- **H1209 controller-worker canary — rig built and VALIDATED on the 3-card promote-DRY slice (18-07-2026, orchestration Fable 5 `claude-fable-5` resuming an Opus 4.8 `claude-opus-4-8[1m]` session; workers Sonnet 5 `claude-sonnet-5`, controller agents Opus 4.8 `claude-opus-4-8`, [PR #553](https://github.com/gasyoun/SanskritLexicography/pull/553))**: first measured probe of the «инжиниринг контроля» concept ([H1209](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1209-Opus_SanskritLexicography_pwg-ru-controller-worker-canary_17.07.26.md)) — Workflow rig under [`RussianTranslation/src/pilot/h1209/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1209/canonical_audit.py) reusing the production prompt invariants verbatim (manifest-driven), with FREE deterministic retry gates and Opus review only for surviving cards. The v1 slice exposed a **`gate-bug`**: a non-canonical EQUALITY sense gate (naive `senses` glyph count) made workers displace source `{Tn}` spans into unrestorable `card.notes` — workflow self-report 3/3 vs **canonical audit 1/3** (incident `H1209_SLICE_V1_2026-07-18` in [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)). v2 gates are direction-aligned with `accept()` (HARD `{Tn}`-multiset fidelity german+russian, shortfall-only vs `source_senses`); v2 rerun `wf_e858f3cf-6af`: **canonical 3/3 PASS, self-report == canonical** (8 agents, 544,056 tok). `canonical_audit.py` (card_fields C-01 restore + `accept()` battery + schema) is the authoritative promote-DRY verdict, independently adversarially reviewed 7/7 faithful. `window_selftest` 142/142, `lang_parity_check` 0 drift (GAP `h1209_controller_worker_rig`), `check_launch_ledger` clean. Promote-DRY only; medium50 RU + mini-EN deferred. Full narrative: [RUN_LOG.md 2026-07-18](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md).

## [1.23.0] — 18-07-2026

### Changed
- **H1245 big-manuals estate refresh (18-07-2026, Fable 5 `claude-fable-5`)** — all 10 manual
  files refreshed against the 221-commit drift window, one adversarial `fact-check-against-source`
  agent per manual, **every confirmed finding fixed** (39 across the seven manuals: manifest-v2
  promotion refusal + mechanized H255 guards + H818 model-pin closure + 53-entry parity in the
  RussianTranslation deep manual; docs-site CI job, A30/A31/A58, 12/14 chapters, closed
  corpus-methods `@DECIDE`, the flagged Zenodo-DOI conflict → [CONTRADICTIONS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
  in the publication manual; per-list key2 verdicts + era-split `wc -l` rule + RIGHTS_LEDGER
  gate in data-reuse; release-stance + CI + FINDINGS-§N-breach warning in maintainer; book/venue/
  registries in researcher; MW-key2 measurement + same-day corpus_gate fix in headwordlists;
  post-incident ReverseDictionary reality in the student manual). Root sheets **re-thinned**:
  AGENTS §4 → live-pointer rule, §5 + HUMAN_RU §8 folded into the deep manual as §13–§14;
  phantom A51 and stale "draft PR #264" framing corrected. **9 per-manual `.meta.md` metadocs
  created**, each with a `LAST_VERIFIED` block (spot-run counts recorded); set-level
  [README.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.meta.md)
  narrowed; router gains the H1029 onboarding row.

### Added
- [CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
  §6: the `10.5281/zenodo.15834721` mint-status conflict (BOOK_PLAN vs FAIR_RELEASE_1) —
  unresolved, needs one online Zenodo check.

## [1.22.0] — 18-07-2026

### Added
- **H968 — 11 metadocs backfilled for hook-flagged genre-named docs (18-07-2026, Sonnet 5 `claude-sonnet-5`)**: sibling `<name>.meta.md` companions authored for every currently-missing metadoc in scope — [FEATURES_INDEX.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.meta.md), [FINDINGS.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.meta.md), [HERITAGE_INRIA_ROADMAP.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.meta.md), [ROADMAP_ACC_NCC.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ACC_NCC.meta.md), [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.meta.md), [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.meta.md), [ROADMAP_VEDAWEB_REUSE.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.meta.md), and three RussianTranslation roadmaps ([RESEARCH_CAPABILITY_ROADMAP_2026-07-09.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.meta.md), [REVIEW_AND_ROADMAP.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.meta.md), [research/ROADMAP_ACL_LESSONS_2026.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.meta.md), [research/ROADMAP_CEILING_2026.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.meta.md)). Each carries purpose/audience/format, a ranked improvement backlog with real owners (`H###` or `parked — <reason>`), known limitations read from the actual subject text, deprecation status, and related-doc links; two cross-doc overlaps were surfaced (BLI-evaluation work duplicated across `RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md` and `research/ROADMAP_ACL_LESSONS_2026.md`) as backlog items rather than silently resolved.

## [1.21.0] — 18-07-2026

### Changed
- **H1110 Phase 6 — c4 bounded live-acceptance attempted, deferred at `HEALTH_NOGO_BY_ENVIRONMENT` (18-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, [PR #534](https://github.com/gasyoun/SanskritLexicography/pull/534) · [#538](https://github.com/gasyoun/SanskritLexicography/pull/538) · [#545](https://github.com/gasyoun/SanskritLexicography/pull/545))**: the c4 profile was mechanically proven — a validated roster slot in `max_accounts.sqlite` bound to `config_dir_fingerprint e96ee464…`, `validate_profile` clean — and every offline gate is green (`window_selftest` **142/142**, headless/execution/bounded selftests PASS, `lang_parity_check` 0 drift). But the Anthropic host is degraded: a confirmation health probe read **98,625 ms (~98.6 s, 3.3× the 30 s ceiling)**, a success/pure-latency NO-GO unchanged from H963's 16-07 104,870 ms. The bounded paid ladder is therefore **deferred** — **1 confirmation c4 call, canary + batch unspent, no production translation** — with the terminal record + exact resume in [`pwg_ru/h1110/H1110_PHASE6_C4_LADDER_HEALTH_NOGO_BY_ENVIRONMENT_2026-07-18.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1110/H1110_PHASE6_C4_LADDER_HEALTH_NOGO_BY_ENVIRONMENT_2026-07-18.md). (The H1110 Phase 1–5 code — headless CLI/manifest-v2 production route, R6 null-owner exec-gate, R9 kernel-backed active-call lock, R10 durable `AWAITING_REVIEW` checkpoint — shipped in v1.18.0–v1.20.0; this entry records the live-acceptance outcome.)

### Added
- **H1150 W1-B — offline false-flag rate for `SANLOSS_*`/`TNMASK_*` guards (measure, don't arm) (18-07-2026, [PR #544](https://github.com/gasyoun/SanskritLexicography/pull/544))**: measures the offline false-flag rate for the sense-count / TNMASK hard-reject guards with a per-guard arming recommendation. Both `SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` remain `= false` (byte-unchanged in `gen_opt_harness2.py`); arming stays a human `@DECIDE`.

## [1.20.0] — 18-07-2026

### Added
- **docs_site research wiki: publish-safety GO verdict recorded, deploy decision surfaced (18-07-2026, Fable 5 `claude-fable-5`, [H740](https://github.com/gasyoun/Uprava/blob/main/handoffs/H740-Fable_SanskritLexicography_docs-site-research-deploy_11.07.26.md))**: `/publish-safety-check` run over the 10 published research docs — **GO, no blocker** (all content already public on `master`; PD 19th-c. sources + citation-scale Kochergina probes; no personal data, secrets, or gitignored bulk in the `_site` bundle), with one anonymity-period caveat surfaced for the ruling; verdict recorded in [PUBLICATION_PIPELINE_DEEP_MANUAL.md § 5.3](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md) ([PR #541](https://github.com/gasyoun/SanskritLexicography/pull/541)). The previously invisible deploy-or-don't decision + the 10-vs-16 scope fork now sit as `@DECIDE` rows in [Uprava GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md); the site stays undeployed pending the ruling. Also: 7 stale wiki copies re-synced (`--sync` — closes the audit's README "Living monitors" / sense_order_metrics staleness), 4/4 site tests green; documented that `merge_BU.md` never had a `research/` source (wiki-only doc, `--sync` skips it).

## [1.19.0] — 18-07-2026

### Added

- **article-comparison gloss-review goes interactive (H739).** The four finalist words'
  hand-authored RU sense-gloss reviews are now one committed dataset,
  [article-comparison/gloss_review_items.json](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/gloss_review_items.json)
  (32 votable edits: agni 11 · akṣara 6 · ananta 9 · anya 6, each with severity + rationale
  + per-word FYI defect lists), rendered by
  [article-comparison/_build_gloss_review_sheets.py](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/_build_gloss_review_sheets.py)
  into four interactive HTML voting sheets (shared csl-pyutil emitter, gitignored
  `review/`). The missing ananta/anya editorial passes were authored in the same pass —
  Fable 5 (`claude-fable-5`); headline findings: ananta m. 17B «окончательно добавленный
  аугмент» mistranslates the positional *finally added* (PD's own note: Pāṇini's
  kit-āgama, P. 1.1.46), and anya 5Biii «противосложение» is a music-theory false friend
  for *countersubject*.

### Removed

- **Markdown ✓/✗ gloss-review sheets retired (H739):** `article-comparison/agni.gloss-review.md`
  and `aksara.gloss-review.md` deleted — checkbox sheets are banned for gating artifacts;
  their proposals live on (rationales translated to Russian) in `gloss_review_items.json`
  and the generated HTML sheets.

## [1.18.1] — 18-07-2026

### Fixed
- **RussianTranslation/src script hygiene — path anchoring, encoding, orphan triage, full CI compile gate (18-07-2026, Fable 5 `claude-fable-5`, [H738](https://github.com/gasyoun/Uprava/blob/main/handoffs/H738-Fable_RussianTranslation_src-script-hygiene-refactor_11.07.26.md))**: the 8 gitignored/untracked audit scripts (`audit2/3/4/5/7`, `audit_fidelity`, `inspect_ru`, `inspect_verse`) re-anchored the SamudraManthanam corpus path on `__file__` instead of `os.getcwd()` and got the `sys.stdout.reconfigure(encoding='utf-8')` preamble (edited in place in the shared checkout — outside the PR by nature); the org-mandated UTF-8 preamble added to tracked [promote_lock.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py), [roadmap_check.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/roadmap_check.py), [slp1_norm.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/slp1_norm.py); the only two absolute-path literals among ~170 top-level src scripts removed — [build_src.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_src.py) and [build_glossaries.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_glossaries.py) now derive `DEFAULT_SM` from `__file__` (argv override kept).

### Changed
- **CI "Compile gate scripts" step covers ALL tracked top-level `RussianTranslation/src` scripts** via `git ls-files ':(glob)RussianTranslation/src/*.py'` (was a hand-picked list of 23; `pilot/` keeps its explicit list) — [ci.yml](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml).
- **Orphan triage (H738 audit list of 14)**: `_nws_watch.py` deleted as provably dead (zero references org-wide, watcher of a long-finished NWS scrape); 5 orphans parked with written reasons and 2 hub-cited scripts (`a43_family_stats.py`, `build_pwg_freq_order.py`) documented in a new [src README section](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/README.md); `safe_filename.py` (27 importers) registered in the org [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md). Untracked scratch deletion (`audit6.py`) left to a human — unrecoverable.

## [1.18.0] — 18-07-2026

### Fixed
- **Findings/epistemic/progress dashboard refresh chain repaired end-to-end (18-07-2026, Fable 5 `claude-fable-5`, [H737](https://github.com/gasyoun/Uprava/blob/main/handoffs/H737-Fable_SanskritLexicography_findings-dashboard-refresh-repair_11.07.26.md))**: the three CONFIRMED breaks from the H733 audit are closed. **(a)** `dcs_cdsl_linkage_pct` — dead (null) in every snapshot since day one despite H733's regex fix — now records **81.4** in a fresh 18-07 snapshot, with the 11-07 snapshot kept as `source: "backfill"` recomputed from csl-apidev git history and the provenance documented in [`findings_dashboard/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/README.md) ([PR #532](https://github.com/gasyoun/SanskritLexicography/pull/532)). **(b)** the `SL findings dashboard refresh` scheduled task — which had NEVER completed a run (0xC000013A, Interactive-only, Temp log purged) — re-registered with `StartWhenAvailable`, explicit working directory, 2h cap and a durable gitignored log at `findings_dashboard/refresh.log`, then **proved one clean run** (Last Result 0, 7/12 platform probes ok, master + gh-pages pushed); the stored-credentials upgrade for logged-off runs is a GTD `@DO` ([PR #533](https://github.com/gasyoun/SanskritLexicography/pull/533)). **(c)** published gh-pages all re-serve fresh data — [`/findings/`](https://gasyoun.github.io/SanskritLexicography/findings/) + [`/episteme/`](https://gasyoun.github.io/SanskritLexicography/episteme/) `generated_at` 18-07 (DEAD_ENDS 11 = registry, post-H616 keys), [`/progress/`](https://gasyoun.github.io/SanskritLexicography/progress/) now a real 2-point series (senses 11,275→11,603, roots 147→254; [PR #535](https://github.com/gasyoun/SanskritLexicography/pull/535)). Refresh-cadence (monthly→weekly) and progress-nudge proposals filed as GTD `@DECIDE`, not applied.

## [1.17.0] — 18-07-2026

### Fixed
- **Canonical reverse-dictionary dataset recovered — the H733 "data loss" was a stranded fast-forward backup (18-07-2026, Fable 5 `claude-fable-5`, H736)**: `266820-reverse-Gasuns.txt` (4,135,335 bytes, 266,820 data lines, SHA-256 `925e696f…e150b9970`) plus every `.doc`/`.pdf` milestone (250,026 / 255,882) and reference corpus was found intact in `C:\Users\user\Documents\GitHub\ReverseDictionary.untracked-backup.20260707T093250\` — a Codex fast-forward on 07-07-2026 09:32 had moved the whole untracked dump there when `origin/master` began tracking `ReverseDictionary/`, and no repo doc recorded it, so the 11-07 audit ([H733](https://github.com/gasyoun/Uprava/blob/main/handoffs/H733-Fable_SanskritLexicography_full-repo-audit-fix-pass_11.07.26.md)) and the 17-07 rights ledger both reported the dataset unlocatable. Canonical `.txt` restored to the working tree (still gitignored by design), full dump mirrored to `D:\ReverseDictionary.untracked-backup.20260707T093250\` (470/470 files, hash-verified), dead blob links in [`ReverseDictionary/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md) repointed to a new "Data location, integrity & backups" section, [`DATA_REUSE_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md) "not in a clone" claim corrected, and the recovery recorded in [`ReverseDictionary/CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CHANGELOG.md). Off-machine backup (Yandex WebDAV) and the distribution-tier ruling remain open — see [H736](https://github.com/gasyoun/Uprava/blob/main/handoffs/H736-Fable_SanskritLexicography_reverse-dictionary-dataset-recovery_11.07.26.md).

### Added
- **FEATURES_INDEX Section VI (Q1–Q30) — methods & algorithms inventory (17-07-2026, Opus 4.8 `claude-opus-4-8`, H1202)**: catalogues the named computational methods behind the assets for the first time — 30 method-family rows (transliteration/keys · Sa↔Sa alignment & collation · bitext/translation-memory · morphology/roots/sandhi · classifiers/register/phonostatistics · search/OCR/ingestion), each graded **N/S/A/X** (novel · standard-in-house · adapted · external-consumed) with its verified home file, in [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) (+ regenerated [`features_index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/features_index.html)). Introduces the `Q` ID prefix; flags the known-defective Renou register classifier (Q21, unanchored regex). Compiled from a 5-agent read-only sweep across ~85 repos; the exhaustive ~70-method backing inventory is in [H1202](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1202-Opus_SanskritLexicography_features-index-methods-algorithms-section-q_17.07.26.md). Answers the standing "do we track algorithms as an asset?" gap — previously visible only obliquely via SHARED_CODE (code), datasets.json (outputs), and RECIPES (reproduction).
- **H963 offline launch-readiness report recovered from an abandoned worktree (17-07-2026, Opus 4.8 `claude-opus-4-8`)**: [`RussianTranslation/pwg_ru/h963/H963_OFFLINE_LAUNCH_READINESS_REPORT_2026-07-16.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_OFFLINE_LAUNCH_READINESS_REPORT_2026-07-16.md) — a read-only planning snapshot (cheapest safe first tranche, plus full-drain cost in calls and agents) found uncommitted in the `SanskritLexicography-h963-resume` worktree during an org-wide worktree sweep; the only at-risk artifact across 154 repos swept. Committed under its own brief's exception ("keep runtime reports uncommitted **unless repository policy explicitly tracks them**" — the six sibling `H963_C4_*.md` reports in the same directory are tracked and nothing there is gitignored), and its self-declared "UNCOMMITTED" status header rewritten to state this rather than ship a false claim. Makes no generation call, promotes nothing, writes to no store, and does **not** lift the launch NO-GO gate (`c5`/`c6` logged out; `c4` latency ~30–53 s against the ≤ 30 s ceiling — both owner-gated). Delivered via [PR #518](https://github.com/gasyoun/SanskritLexicography/pull/518).

## [1.16.0] — 2026-07-17

pwg_ru release. Two entries:

- **H1151 (premise-stale close, [PR #523](https://github.com/gasyoun/SanskritLexicography/pull/523))** — the H858 grammar-`{Tn}` stranding defect was found already fixed by the C-01 centralization; this pins the fixed behaviour with a behavioral test extracting the REAL emitted restore path from a generated harness (8 checks incl. the live gokzuraka shape and the C-42 boundary), wired into `window_selftest.py` (136/136 green). Blast radius report-only: 0 `{Tn}` tokens anywhere in the 11,603-row store; store untouched. Model: Fable 5 (`claude-fable-5`).
- **H1080 follow-up ([PR #517](https://github.com/gasyoun/SanskritLexicography/pull/517))** — `provenance.h_reconstructed` markers on the 468 derived headwords (owner-authorised), making the reconstruction auditable.

Full changelog: [RussianTranslation/CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md)

## [1.15.0] — 2026-07-17

First Fable-tier verdict on the PWG→EN tranches ([PR #507](https://github.com/gasyoun/SanskritLexicography/pull/507), merge e9d65d96; [H1070](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1070-Fable_RussianTranslation_pwg-en-fu1-pilot-adjudication_16.07.26.md)): 170 sense rows adjudicated against the PWG German with Monier-Williams quoted per entry as adversary — wrong-sense 4/170 = 2.35% Wilson [0.92%, 5.89%] (FU1/Sonnet 5 tranche 3/102 = 2.94%), zero new MW-TM contamination, zero register-mismatch. Verdict **GO (conditional)** with a standing per-tranche decision rule and three named guards. Evidence: [RussianTranslation/pwg_ru/h1070/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h1070). Adjudicator Fable 5 (claude-fable-5).

## [1.14.1] — 17-07-2026

### Added
- **FINDINGS §91 — DCS `feat_formation` isolates the aorist from the perfect within `feat_tense='Past'` (17-07-2026, Sonnet 5 `claude-sonnet-5`)**:
  harvested from [H1134](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1134-Opus_SanskritGrammar_whitney-aorist-per-text-tagger_17.07.26.md)
  ([SanskritGrammar PR #357](https://github.com/gasyoun/SanskritGrammar/pull/357)) via the
  registry-audit reference-harvest reflex, so the technique survives handoff archival. DCS has no
  aorist tense code — `feat_tense='Past'` conflates aorist and perfect — but `feat_formation IN
  {root, them, s, is, red, sa, sis}` cleanly isolates the seven aorist classes (12,054 finite
  tokens / 1.2% of verbal forms), correcting the earlier form-set method's 2,452 / 0.31% undercount
  (it missed the two largest classes). See [FINDINGS.md §91](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## [1.14.0] — 17-07-2026

### Added
- **M01 Ch. 2 §6 *The corpus as a bounded witness* — the monograph's canonical corpus-epistemics section (17-07-2026, Fable 5 `claude-fable-5`, H1078)**:
  executes MG's 13-07-2026 ruling (b) on the corpus-methods fork
  ([LITERATURE_CROSSWALK.md §4.2](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md)).
  ~7 pp. of book-only new writing in
  [ch02_measurement_framework.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md):
  the DCS 2026 disclosure (5,688,416 content tokens · 270 texts · 95,457 disambiguated
  lemmas · 41.9 % hapax share, per the committed
  [VisualDCS census](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Leksicheskie-issledovaniya/Gapaksy-DCS-2026/README.md)),
  the absence-inference rule (bounded DCS-coverage statements, never "non-existent" —
  McEnery & Brezina), the five-clause statistical-practice contract (effect sizes, not bare
  p-values at corpus N — Kilgarriff 2005), and the Ch. 3/5/11/13 binding map; ch02's old
  §6–§9 renumbered §7–§10, 9 references added. Proposal ToC (Ch. 2 bullet), BOOK_PLAN §11,
  crosswalk §4.2 (15→14-chapter consumer numbering made explicit), BOOK_PLAN.meta backlog
  #3 and the book CHANGELOG all ticked in the same pass.

## [1.13.0] — 17-07-2026

### Added
- **A31/P5 Lexikos draft — error-origin typology over the OBS-T correction corpus (17-07-2026,
  Fable 5 `claude-fable-5`, H1074)**: full draft
  [papers/A31_fifty_thousand_corrections_error_origin_typology.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A31_fifty_thousand_corrections_error_origin_typology.md)
  adds a third, origin axis (print-source / digitization / conversion-markup / undetermined,
  never guessed) on top of OBS-T's location x edit-type design. Census computed by
  [papers/a31_origin_census.py](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31_origin_census.py)
  over the released 52,498-event snapshot: 58.4% classified, per-class precision 0.90-0.97
  (micro 0.933) on a 120-row hand-checked stratified sample (single-annotator, kappa pending
  the org's standing second-annotator recruit). Headline findings: form-era workflow preserved
  origin testimony for 98.9% of its events vs 23.1% for the git era; digitization-era slips
  outnumber inherited print errors >10:1; high per-dictionary print-error shares (BEN 46.9%,
  PD 37.2%, BUR 32.6%) are single-collator campaign fingerprints (top corrector 94-100%).
- **FINDINGS §87 — the roadmap's "OBS-T κ=0.42" was a phantom figure**: no measured agreement
  exists for any OBS-T axis (gold second-annotator column blank, κ=0.0 over 4 incidental
  pairs); both roadmap cells corrected, rule logged (re-derive statistics from committed
  metrics files, never cite planning-doc cells into papers).

## [1.12.0] — 17-07-2026

### Added
- **A30 full paper draft — "When Zero Means Nothing: Recovering the Indigenous Microstructure
  of the *Śabdakalpadruma* and the *Vācaspatya*" (17-07-2026, Fable 5 `claude-fable-5`, H1073)**:
  [`papers/A30_skd_vcp_microstructure_note.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_skd_vcp_microstructure_note.md)
  — roadmap P4 taken from outline (2/5) to full IJL/WSC-2027 draft (3/5 proposed). Claims the
  record-level indigenous microstructure (entry template, front-matter megastructure key, the
  *iti*-unit, SKD-vs-VCP register contrast); every figure read from committed csl-atlas
  artifacts, no new computation; scope coordinated against A04 (root grammar) / A35 (affixes)
  / A02 (sense inheritance) / A08 (citation registers).
- **FINDINGS §86 — samāsa-type frequency does not exist in any org corpus; the canonical
  examples are corpus-ghosts (16-07-2026, Opus 4.8 `claude-opus-4-8`)**: measured while
  scoping a frequency layer for the [samāsa-cakra wheel](https://gasyoun.github.io/SamasaChakram/).
  Two walls, both measured: DCS has 841 052 compound members but no type label (EM4, per H989),
  and VisualDCS's `категории композитов.ods` means *stem count* by "категория", not samāsa class;
  the fallback of showing each leaf's example frequency dies at **8/58 attested** (max 147,
  min 0). Records why an example-frequency layer is worse than none — it is a type-frequency
  claim in disguise that inverts the truth on the most-taught subtypes.
- **`ONBOARDING_NEW_CONTRIBUTOR_RU.md` — gentle Russian on-ramp for a non-technical Sanskrit contributor (16-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, H1029)**:
  fills the gap between the git-assuming English `CONTRIBUTING.md` and the deep-project
  `MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md` — a 5-rung ladder (talk-to-Claude → GitHub issues →
  browser PRs → Claude Code → independent contributor) with a beginner-safe first task
  (OCR/scan-quality error reporting, no deep lexical judgment required). Pointer added from
  `CONTRIBUTING.md`.
  - **Follow-up (16-07-2026):** added "Вариант Б" for a **zero-Sanskrit** beginner —
    proofreading the English/Latin side of entries (Apte/MW) against the scan, plus a
    simplest fallback (flag illegible scans / dead cross-reference links). Makes the first
    task reachable without reliable Devanagari.
  - **First-task redesign (16-07-2026):** replaced the open-ended "open 5–10 entries and
    hunt for OCR errors" (unbounded, low-yield, unclear done) with a **bounded verification
    task against the live `HeadwordLists/A_TYPO_QUEUE.md` worklist** — verify the 4
    MW-flagged suspect headwords vs the scan (confirm → files a correction; refute → clears
    a false positive), directly feeding print-readiness gate A. Both variant B and the
    fallback rebounded to a page/column unit rather than "read the whole dictionary".

## [1.11.0] — 2026-07-16

H1066: Minimal mockups for the pwg_ru research interfaces (affix explorer/quiz token re-points + capability observatory) under RussianTranslation/research/mockups/. Non-style bytes identical, scripts parse-checked, non-destructive. affix_poster (print artifact) and the pilot dashboard (app-gated) recorded out of scope. This delivers the LAST row of the H563 dashboard-redesign direction map. PR #501. Fable 5 (claude-fable-5).

## [1.10.0] — 2026-07-16

H1063: three CSS-only Dark data-app mockups for the SanskritLexicography ops surfaces — epistemic_dashboard, findings_dashboard, and the generated FEATURES_INDEX artifact. Non-style content byte-identical modulo declared data-path prefixes; non-destructive, pending promotion (FEATURES_INDEX promotion = fold tokens into the generator). PR #499. Fable 5 (claude-fable-5).

## [1.9.19] - 2026-07-15

### Fixed
- **D-P follow-through — `latency_payload_sweep.py` `actual_prompt_bytes` + latency runbook hardened for the v1.9.17 probe (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, Ultracode)**:
  the D-P fix (v1.9.17) changed `_probe_call`'s prompt but left `latency_payload_sweep.py` with a stale
  mirror constant (`PREFIX_LEN + padding_bytes`) that **miscounted `actual_prompt_bytes`** (the field the
  `latency_sweep_analyze.py` payload-size axis reads) — reporting 6554 when the real prompt is 6828 B.
  Now derived from the SAME `_probe_prompt` (single source of truth, cannot drift):
  `actual_prompt_bytes = len(_probe_prompt(padding_bytes))`. Also updated
  `PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md` (the H909 owner runbook): Method step 2 now
  **requires a probe ≥ v1.9.17** on both hosts (a pre-fix `'x'`-padding probe is artificially-fast on
  compliance and refusal-bimodal under `--permission-mode plan`, confounding route latency), records the
  first honest home reading (**c4 ~30–53 s**, over the 30 s ceiling), and caveats the prior home-route
  sweep/variance results (the 8.9 s→59.2 s spread is partly that probe artifact) as needing a re-baseline.
  No behaviour change to the probe itself; diagnostic-tooling + runbook correctness only.

## [1.9.18] - 2026-07-15

### Added
- **D-Q (H994) — reliable silent-SAN-LOSS canary for the rung-3 measurement (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, Ultracode)**:
  the rung-3 false-flag measurement needs a card that *passes* `accept()`'s `<ls>`/`{#` fidelity gate while
  *dropping* a numbered source sense (the silent SAN-LOSS the H920/H960 sense-count soft-guard catches).
  `darvI`/`gaRanA` are unreliable — `darvI` carries `{#darvI#}` in sense 3, so dropping it `fidelity-reject`s
  instead of silently losing a sense. Curated a **deterministic** canary
  `RussianTranslation/pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw` (three pure-gloss senses, **zero
  `<ls>`, zero `{#`**): dropping *any* sense keeps the fidelity gate at `0==0` while `source_senses` stays 3,
  so SAN-LOSS is the only catch. Extended `accept_sensecount_test.js` to prove it against the **real**
  `accept()` (faithful clean; drop 1st/middle/last each → kept + fidelity-clean + `SANLOSS dropped=1`; drop
  two → `dropped=2`; contrast: the `darvI` `{#`-sense drop `fidelity-reject`s) — green via
  `test_h960_accept_sanloss_soft_gate`; offline harness build-check stamps `source_senses:3 / ls:0 / sk:0`.
  Curation doc: `RussianTranslation/pwg_ru/h994/H994_DQ_SANLOSS_CANARY_CURATION_2026-07-15.md`. Both H994
  probe/canary defects (D-P, D-Q) now closed; the live rung-3 gates only on the latency rung + a usable
  profile. No live generation, no store mutation.

## [1.9.17] - 2026-07-15

### Fixed
- **D-P (H994) — PWG-RU acceptance-probe prompt fragility (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, Ultracode)**:
  `max_account_orchestrator._probe_call`'s degenerate readiness prompt (`"Return JSON {ok:true}. Preserve
  this padding as inert input." + N×'x'`) tripped Sonnet-5's `--permission-mode plan` refusal (prose citing
  the "end your turn via AskUserQuestion" rule, `structured_output=None`), producing a **false
  `content`/`timeout`/`malformed` NO-GO on a genuinely responding profile**. Replaced with a new
  `_probe_prompt()` helper: one unambiguous "reply with exactly `{"ok": true}` and nothing else" instruction
  + ≥5 KB of inert, domain-shaped filler, under the **same `--permission-mode plan` the real generation path
  (`headless_worker.call`) uses**. Added a `D-P readiness prompt` selftest (captures the real argv + stdin;
  asserts the completable task, ≥5 KB payload, plan mode retained, degenerate `x`-padding gone). Live-verified
  on c4: both probe phases now return `success` (no refusal, 1 483 B output).
  **Correction it surfaced:** the old `'x'`-padding BPE-compresses to few tokens, giving *artificially fast*
  latency (~8 s) — the H994 v1.9.16 "c4 sub-30 s, first sub-ceiling reading" was that artifact. Under the
  fixed load-representative payload c4 measures **~30–53 s (latency NO-GO)**, consistent with H818/H895's
  ~40 s NO-GOs; the latency rung remains a genuine blocker (H818/H909 foreign-route), independent of the
  c5/c6 logins. No store mutation.

## [1.9.16] - 2026-07-15

### Added
- **H994 (pre-named H963) — PWG-RU two-profile live-ladder measurement, owner Option B (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, Ultracode; measurement-only, no promotion — store unchanged at 11,605)**:
  ran the owner-gated live ladder's rungs 1–2 on profiles c1/c4 (no canary generation, no store/TM
  mutation). **Rung 1 auth:** c1/c4 ✅ Max, **c5/c6 ❌ `loggedIn:false`** → four-profile acceptance stays
  **NO-GO** (owner must `claude auth login` c5/c6). **Rung 2 latency:** c1 `rate_limit` (parked); **c4
  genuinely healthy at ~8–12 s — the first sub-30 s pwg-ru probe reading ever** (H818/H895 were ~40 s
  NO-GO ×2). **Two defects surfaced:** **D-P** — the D-K acceptance probe's degenerate padding prompt
  (`"Return JSON {ok:true}" + N×'x'` under `--permission-mode plan`) trips Sonnet-5's plan-mode refusal,
  producing a *false* `content`/`timeout` NO-GO on a healthy fast profile; **D-Q** — `darvI`/`gaRanA` are
  poor SAN-LOSS soft-guard canaries (`darvI` is a deterministic fidelity-reject), so a canary that *passes*
  fidelity while dropping a sense must be curated before rung 3. Rung 3 canary **not reached**. Report:
  [pwg_ru/h994/H994_TWO_PROFILE_LIVE_MEASUREMENT_GATE_2026-07-15.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/H994_TWO_PROFILE_LIVE_MEASUREMENT_GATE_2026-07-15.md).
  No code shipped (measurement + docs only); H255 stays frozen until the four-profile ladder passes.

## [1.9.15] - 2026-07-15

### Fixed
- **H870 correction — FINDINGS §80 retracted-and-rewritten; MW facsimile auto-pull re-enabled (15-07-2026, Fable 5 `claude-fable-5`)**:
  an `api=1` probe via an independent egress disproved v1.9.14's diagnosis — the
  `MWScan/2020` `servepdf.php` endpoint correctly serves **1899** pages
  (`page=277` → `MWScanpdf/mw0277-kArSNi.pdf`), with or without `dict=`. The wrong
  1872 pages that prompted the diagnosis came from the portal's separate first-edition
  browser (`pg_NNNN.pdf` files) — a manual-navigation hazard, not an endpoint bug.
  [`EntryAnatomy/build_entry_anatomy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/build_entry_anatomy.py)
  MW auto-pull re-enabled (URLs now carry `dict=` like the endpoint's own nav links);
  [FINDINGS §80](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  rewritten as the navigation-level cross-edition trap with an explicit retraction.
  Verified downstream: kosha's `app/scan_resolver.py` links are correct as-is — no
  change needed there.

## [1.9.14] - 2026-07-15

### Added
- **H870 follow-up — mw-kAla specimen gets its 1899 print inset; MW scan auto-pull disabled over a cross-edition trap (15-07-2026, Fable 5 `claude-fable-5`)**:
  [`mw-kAla-specimen`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-kAla-specimen.html)
  rebuilt with the genuine 1899 p. 277 facsimile (owner-supplied scan, committed as
  [`assets/mw_kala_p277.jpg`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/assets/mw_kala_p277.jpg);
  running heads *kārshṇi/kālikā-purāṇa* verified). The v1.9.12 scan-server auto-pull for
  MW turned out to point at the **1872 first-edition** scan whose page numbers silently
  collide with 1899 `<pc>` loci — `--markup` MW builds now require `--facsimile`, and the
  trap is documented as [FINDINGS §80](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## [1.9.13] - 2026-07-15

### Added
- **H960 — four-profile PWG→Russian production-readiness (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, offline)**:
  verified H920 (every offline gate green) and closed the six load-bearing gaps blocking four-profile
  nonstop scale, each a **SOFT / report-only** guard pinned by a selftest and wired into CI (arming any
  hard reject stays owner-gated — a silent pass → visible requeue changes throughput, measured on live
  traffic first). (1) [`accept()` sense-count](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  (H920's deferred deepest fix): stamps the hardened `source_senses`, records a `SANLOSS_SHORTFALLS`
  shortfall (`SANLOSS_HARD_REJECT` owner-gated); [`sense_count.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sense_count.py)'s
  counter hardened to skip cross-reference ordinals (~4.78%-of-cards over-count). (2) grammar `{Tn}`
  multiset check on the main `accept()` path (`TNMASK_MISMATCHES`), catching a dropped `<lex>` span the
  `<ls>/{#` count misses. (3) [`dropped_sanskrit_span`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)
  — content-multiset German `{#..#}` source-vs-target diff, LOW/report-only, head-label FP class excluded.
  (4) new [`economy_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/economy_ledger.py)
  derives `agents_per_clean` + a bounded `$/clean` band from the frozen probe log. (5) four-profile
  [`staged-run`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py):
  guard relaxed to ≥1 account, `probe_fleet()` STOP-on-any-NO-GO, `only_accounts` dispatch filter. (6) new
  [`bounded_supervisor.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_supervisor.py)
  injectable-seam nonstop loop with crash-resume. An adversarial correctness-review pass fixed 2 bugs +
  a CodeQL ReDoS. Residual NO-GO = the owner-gated live ladder (auth→latency→canary→arm→10→20→multi-profile).
  [PR #475](https://github.com/gasyoun/SanskritLexicography/pull/475); gate report:
  [pwg_ru/h960/H960_FOUR_PROFILE_PRODUCTION_READINESS_GATE_2026-07-15.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h960/H960_FOUR_PROFILE_PRODUCTION_READINESS_GATE_2026-07-15.md).

## [1.9.12] - 2026-07-15

### Added
- **H870 — /entry-specimen visual engine (15-07-2026, Fable 5 `claude-fable-5`)**:
  [`EntryAnatomy/build_entry_anatomy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/build_entry_anatomy.py)
  extended with the two /entry-specimen modes on top of the H780 callout/leader/`@page`
  engine: `--markup <dict> <headword>` re-typesets ANY `<k1>` headword from csl-orig
  (MW `<e>`-level paragraph grouping, PWG one-paragraph-per-record; auto-proposed
  callout first pass marked "proposed — verify", or a `--callouts` JSON/TSV spec;
  facsimile inset auto-pulled from the Cologne scan server with soft 429 fallback),
  and `--image <path>` annotating a supplied picture or rasterized PDF page with
  region-anchored (`{x,y,w,h}` fractions) callouts. One HTML source serves both
  outputs: print-faithful single-sheet PDF (headless Chrome) and theme-aware
  interactive web (hover/click callout↔target sync, leader reflow on resize,
  light/dark via `prefers-color-scheme` + toggle). New committed exemplars:
  [`mw-kAla-specimen`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-kAla-specimen.html)
  (39 records, 2 print paragraphs) and
  [`duden-faser-image-specimen`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/duden-faser-image-specimen.html)
  (the Duden *Faser* plate annotated in image mode, 13 regions located via the
  PDF text layer).

## [1.9.11] - 2026-07-14

### Fixed
- **H937 — H178 RUBRIC_JS note-clobber fix (14-07-2026, Sonnet 5 `claude-sonnet-5`)**: h178's
  `RUBRIC_JS` widget script wrote rubric values (MQM severities, Likert, DA, pairwise) into
  `localStorage` directly, bypassing the shared `csl_pyutil` core template's closure-private
  `state` object — core's `vote()`/`save()` (any approve/reject/defer click, on ANY card)
  unconditionally overwrote the entire stored record with stale in-memory `state`, wiping the
  note field; a second, more severe variant clobbered a *different* card's already-written
  note on any vote elsewhere on the sheet. Fixed entirely within `RUBRIC_JS` (core template
  untouched): `rubricNote()` derives the note purely from a card's current DOM widget values,
  `healAll()` re-merges every touched card's note into fresh `localStorage` on every vote
  click, and the Download button is clone-and-replaced to export fresh from `localStorage`
  instead of core's stale `state`. Browser-verified via Blob interception across same-card,
  cross-card, textarea-edit-last, and rubric-less `pairwise` scenarios.
- **H937 follow-up — download-filename regression (14-07-2026, Sonnet 5 `claude-sonnet-5`)**:
  H937's rubric-note-clobber fix cloned+replaced h178's Download button to strip the shared
  `csl_pyutil` core template's stale-state listener, but the new listener's `a.download`
  reverted to the literal `'decisions.json'` — reintroducing the exact generic-filename
  collision [csl-pyutil#1](https://github.com/sanskrit-lexicon/csl-pyutil/issues/1)/H933 had
  just fixed in the shared emitter (the two fixes shipped independently within the same hour
  and didn't compose). Now `SHEET_ID + '_decisions.json'`, matching convention. Browser-verified
  (synthetic 2-card sheet): vote-after-rubric-edit no longer clobbers a different card's note,
  and the exported filename is correctly `<sheet_id>_decisions.json`.

## [1.9.10] - 2026-07-14

### Added
- **Methodology lineage — Apresyan's systematic lexicography ↔ ACL computational lexicography**
  (H942): new Part II subsection in
  [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
  with an Apresyan-concept → ACL-resource crosswalk and a 9-item verified ACL Anthology reading
  list (WordNet, FrameNet, PropBank, VerbNet, Kilgarriff, WSD eval, lexical functions, definition
  modelling, LLM definitions). Gives the "system, not a list" thesis its genealogy and seeds the
  monograph's evidence-graded-method framing chapter.

## [1.9.9] - 2026-07-14

### Fixed
- **PWG→Russian no-PWG promotion safety** — planner manifests now emit an explicit
  single-window workflow glob and exact generation model id; merge promotions refuse the
  implicit repo-root glob that repeatedly ingested unrelated stale workflow artifacts.

## [1.9.8] - 2026-07-14

### Added
- **pwg_ru latency-policy investigation — payload-size sweep executed (H898)** —
  31 diagnostic `claude-sonnet-5` plain-probes (new
  `RussianTranslation/src/pilot/latency_payload_sweep.py` + `latency_sweep_analyze.py`,
  reusing `max_account_orchestrator._probe_call`; raw JSONL committed as durable
  evidence) settle the ~40 s measured-probe breach that NO-GO'd H818 acceptance
  twice: it is **not** payload-size-driven (a 93 B call hit 52.8 s; all-data R²=0.02)
  and **not** a flat ~40 s floor (range 8.9–59.2 s) — a modest input-size throughput
  floor (~+1 ms/byte) superimposed on a dominant, size-independent, time-clustered
  route jitter (CV 0.53) that spikes even tiny payloads over the ceiling (11/31
  breaches in-window). Results + verdict in
  `RussianTranslation/PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md`. Policy
  unchanged (30 000 ms ceiling kept; fix is the H818 foreign-route, not smaller
  payloads); step 3 (foreign-route comparison) stays human-gated.
- **FAIR Release #1 metadata (H817 WS1.4)** — `CITATION.cff`, `DATA_LICENSE.md`,
  and `data/FAIR_RELEASE_1.md` prepared for a curated Zenodo dataset deposit of
  the markup-tag census (E39) and headword-overlap matrix (E40), cross-linked
  to the csl-atlas citation graph (E38). Deliberately a file-level deposit,
  not a whole-repo GitHub→Zenodo integration — this repo mixes in
  third-party-rights-uncertain scan PDFs a full archive would sweep in. The
  Zenodo upload itself is parked `@DO` (account/token gate).

### Changed
- **H817 WS1.2** — `FEATURES_INDEX.md` registers E43–E46 (code-duplication census +
  LOC/language mix, already done pre-roadmap via H688 but unregistered; POS-per-text,
  sense/polysemy per dict, paradigm-cell coverage, both new via H817); flips 5 rows in
  `ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md` Part 0 from ○/◐ to ✅/◐ and bumps its
  `Last updated`.

## [1.9.7] - 2026-07-13

### Added
- **H813 — «Санскрит в цифрах» Wave 0 + Wave 1 (Sanskrit-in-Numbers, the Duden
  *Sprache in Zahlen* analog).** New `papers/sanskrit_in_numbers/`: Wave 0 assembles
  the already-owned modules (vocab size → A40/A55, POS → A56, lemma/token +
  a new Zipf coverage curve → VisualDCS) into `MODULES_OWNED.md`; Wave 1 ships
  the five NEW modules with reproducible generator scripts + committed JSON
  datasets — akṣara/phoneme frequency (Module 5), longest compounds with a
  ≥5-occurrence honesty floor (Module 6), gender distribution (Module 8),
  samāsa types best-effort via DCS's UD-style `compound:coord` tag (Module 9,
  explicitly flagged — no fabricated tatpuruṣa/bahuvrīhi split), and verb
  classes + parasmaipada/ātmanepada/ubhayapada voice from WhitneyRoots (Module
  10). See `WAVE1_SUMMARY.md` for headline numbers + trust blocks.

## [1.9.6] - 2026-07-13

### Fixed
- **H852 — the four H818 Windows headless-invocation defects, fixed and verified
  live.** `claude_argv_prefix()` resolves a Windows `.cmd`/`.ps1` launcher to
  `[node, cli-wrapper.cjs]` (bypassing cmd.exe, which corrupted the `--json-schema`
  arg); `--claude-bin` is threaded through `staged-run → run_once → run_claimed`;
  rate-limit detection (`is_rate_limited`) trusts the worker classification / raw
  stderr instead of matching the `manifest_sha256` hash; `staged-run` halts cleanly
  when all accounts are parked instead of busy-looping. Re-run on Windows: presplit
  canary GO, 1-headword generation `done`/`success`, no false park, no livelock —
  the invocation baseline is now functional (residual non-GO was a content-hard card,
  not invocation). Adds D-A/D-C unit tests. Report:
  [`RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md).

## [1.9.5] - 2026-07-13

### Added
- **H818 Windows live acceptance — NO-GO on four Windows/robustness defects
  (auth now resolved).** First live Windows run to get past the prior `401`:
  `init` (auth + minimal `claude -p --model claude-sonnet-5`) and the ≥5 KB
  `live_probe` passed, all offline gates green, canonical store present (11,562
  rows), 149 net-additive unpromoted headwords. Headless generation is
  non-functional on Windows — presplit canary and the first promoting window
  failed before any promotion; store unchanged, real Max account healthy.
  Defects: `claude.cmd` batch-shim cmd.exe corruption of the `--json-schema`
  argv; `run_claimed` not forwarding `--claude-bin`; `RATE_LIMIT` regex matching
  the `manifest_sha256` hash; `staged-run` parked-account livelock. Report:
  [`RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md);
  fixes tracked in
  [H852](https://github.com/gasyoun/Uprava/blob/main/handoffs/H852-Opus_SanskritLexicography_h818-windows-headless-invocation-fix_13.07.26.md).
  H841/H842/H843 remain gated on a Windows-baseline GO.

## [1.9.4] - 2026-07-12

### Changed
- **Renou stage-redundancy audit (H692) `@DECIDE` — closed in the audit doc with
  a pointer to the authoritative H771 verdict: the 25-06 canonical
  `{code}.renou.jsonl` regeneration is a CORRECTION, not a regression.** The
  primary org-wide adjudication is H771's
  [`RENOU_DCS_INDEX_REGRESSION_INVESTIGATION_12.07.26.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_DCS_INDEX_REGRESSION_INVESTIGATION_12.07.26.md)
  ([PR #394](https://github.com/gasyoun/SanskritLexicography/pull/394): 28,662/646,926
  rows = 4.4% divergent, all pure low-confidence DCS-noise removal, 0 anomalies;
  `renou_ls` positionally byte-identical). The audit doc's § ADJUDICATION adds an
  independent DCS-axis corroboration (all 26,290 index-resolvable `mw` rows:
  canonical `renou_dcs` == the `DCS_MIN_SUPPORT=2` projection of the lossless
  `dcs_lemma_renou.json`, 0 mismatches). Canonical files trustworthy downstream;
  the old underscore chain's deletion (H771) was safe.

## [1.9.3] - 2026-07-12

### Added — interactive "Каталог каталогов" over FEATURES_INDEX.md
- [`features_index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/features_index.html) —
  a self-contained, filterable single-file HTML view of the capability inventory
  (free-text search + category tabs Данные/Словари/Интерфейсы/Инструменты/Changelog
  + status/size-tier/language filters), theme-aware, zero-dependency.
- [`build_features_index_html.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/build_features_index_html.py) —
  the generator that parses [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md)
  into that artifact, so the two never drift (edit the Markdown, re-run).
- Closes the interactive-view item long marked "planned / not built yet" in
  FEATURES_INDEX.md — and the «Каталог каталогов» deliverable of the 2004
  AIOC-Varanasi programme manifesto.

## [1.9.2] - 2026-07-12

### Added — Kochergina okas/okya/guda/sphic attestation-verify review sheet (H779)
- New [`RussianTranslation/review/sanskritlexicography-kochergina-okas-guda-sphic_4rows_review.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/sanskritlexicography-kochergina-okas-guda-sphic_4rows_review.html):
  re-verification of the 2013 Nagari-list forum thread's 4 dictionary-correction
  candidates (okas, okya, guda, sphic/sphigī/sphij) against RV attestation
  (VedaWeb accented corpus) and MW/Apte/KEWA — okas/okya senses confirmed
  unattested and flagged for change; guda's claimed gender defect **refuted**
  (Kochergina already carries a correctly separated `gudā` f. entry); sphic
  confirmed missing as a headword plus a newly found gloss error on `sphigī`.
  Interactive approve/reject/defer sheet, registered in
  [Uprava/REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md).

## [1.9.1] - 2026-07-12

### Added — Böhtlingk item-#1 shared-omission finding + Stache-Weiske notes (H796)
- [FINDINGS §83](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md):
  MW and the Petersburg dictionaries are **not** independent witnesses on inventory/apparatus
  (do not count their agreement as corroboration) — but no shared *error* has ever been found.
  Grounded in the new csl-atlas shared-omission test (A10 §3.5 / F9,
  [csl-atlas PR #263](https://github.com/sanskrit-lexicon/csl-atlas/pull/263)): on 6,941 real
  indigenous-attested words, MW's omissions track PWG's ≈8× more than the independent Apte's, yet
  MW independently supplies 54.6% of PWG's gaps.
- Reading notes on the source paper:
  [`papers/Stache-Weiske_Bö-MW.notes.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/Stache-Weiske_Bö-MW.notes.md)
  — the itemised 1881–83 charge (omission/error/sense-order) mapped to each A10 test, with the
  remaining open clause (sense-order) and the 35-Stellen gold-set flagged as actionable.

## [1.9.0] - 2026-07-12

### Added — Duden-style entry-anatomy specimen pages for PWG, MW and the CDSL record (H780)
- New [`EntryAnatomy/`](https://github.com/gasyoun/SanskritLexicography/tree/master/EntryAnatomy):
  three annotated "how to read an entry" pages after the Duden
  *Universalwörterbuch* specimen-spread model
  ([`papers/duden_deutsches_universalworterbuch-page.pdf`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/duden_deutsches_universalworterbuch-page.pdf)) —
  [`pwg-entry-anatomy.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/pwg-entry-anatomy.html)
  (24 callouts, *heman* homograph cluster + √*cumb*),
  [`mw-entry-anatomy.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-entry-anatomy.html)
  (21 callouts, same lemma family for cross-tradition comparison), and
  [`cdsl-record-anatomy.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/cdsl-record-anatomy.html)
  (the digital record layer: key1/key2, SLP1 accents, `<e>` levels, `<info>`).
  Each self-contained (facsimile insets from the Cologne scan server embedded)
  with a single-sheet print PDF; generator
  [`EntryAnatomy/build_entry_anatomy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/build_entry_anatomy.py)
  re-typesets records straight from csl-orig v02. MW `<e>`-semantics finding
  logged as FINDINGS §82. Fable 5 (`claude-fable-5`).

## [1.8.1] - 2026-07-12

### Added — A58 paper skeleton + grammatical-annex counted table (H767/H774)
- A58 paper skeleton over the H742 crosswalk tables:
  [`papers/A58_semdom_amarakosha_crosswalk_paper.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A58_semdom_amarakosha_crosswalk_paper.md)
  — claim, 12-row claim→artifact data inventory, outline, verified comparanda.
- Grammatical-annex parallel counted:
  [`data/semdom_ak_annex_table.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annex_table.py)
  derives AK kāṇḍa 3 (2,592/5,590 synsets, 46.4%) vs semdom top-level 9
  (168/1,792 domains, 9.4%), converging to 10.7% vs 9.4% with nānārtha's
  polysemy register set aside; table embedded in
  [`data/SEMDOM_AK_CROSSWALK_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md),
  finding logged as FINDINGS §77.

### Fixed
- FINDINGS duplicate-§76 key: the DCS `m_wordsem` finding renumbered to §78
  (renumber note in place; STALENESS link updated); §76 stays the
  MW→WordNet→semdom bridge finding cited from FEATURES_INDEX C19.
- `data/semdom.json` / `wn-links` fetch caches actually gitignored (the
  docstrings already claimed they were).

## [1.8.0] - 2026-07-11

### Added — semdom ↔ Amarakosha crosswalk, Level A + Level B gold pilot (H742)
- First crosswalk between SIL's 1,792 semantic domains and a classical
  thesaurus: [`data/SEMDOM_AK_CROSSWALK_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md)
  (README of record) + ID-pair tables — Level A varga map
  ([`data/semdom_varga_crosswalk.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_varga_crosswalk.csv),
  20 thematic vargas, hand-authored with evidence), Level B machine candidates
  for all 5,590 synsets
  ([`data/semdom_ak_candidates.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_candidates.tsv))
  and a 200-synset adjudicated gold sample
  ([`data/semdom_ak_gold.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_gold.tsv),
  dual-annotated blind Fable 5 `claude-fable-5` × Opus 4.8 `claude-opus-4-8`,
  exact κ 0.677 / level-2 κ 0.806). Key numbers: 96.4% synsets get ≥1
  candidate, 0 NONE gold votes, structure agreement 67.0%, bridge top-1
  precision 17.5% (candidate generator, not classifier). Results also in
  [`papers/SEMDOM_KOSHA_CROSSWALK_SCOPING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SEMDOM_KOSHA_CROSSWALK_SCOPING.md)
  §7. Feeds the H721 MDF/LIFT `\sd` layer; paper A58. Per
  [Uprava H742](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H742-Fable_SanskritLexicography_semdom-kosha-crosswalk-build_11.07.26.md).

## [1.7.0] - 2026-07-11

### Added
- CodeQL SAST workflow for the repo's Python/JS tooling
  ([PR #329](https://github.com/gasyoun/SanskritLexicography/pull/329)).
- H607 HeadwordLists analytics deep manual —
  [`docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md)
  ([PR #339](https://github.com/gasyoun/SanskritLexicography/pull/339)).
- SIL MDF ecosystem correlation map (Coward–Grimes 2000 vs the CDSL workbench;
  MG rulings 11-07-2026; H721–H727 program) —
  [`papers/SIL_MDF_ECOSYSTEM_CORRELATION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SIL_MDF_ECOSYSTEM_CORRELATION.md)
  ([PR #342](https://github.com/gasyoun/SanskritLexicography/pull/342)).
- DEAD_ENDS §8b: full MBH locus census blocked — no free vulgate e-text (H610)
  ([PR #343](https://github.com/gasyoun/SanskritLexicography/pull/343)).
- Markup-tag frequency census over all 44 Cologne v02 dictionaries (H683)
  ([PR #345](https://github.com/gasyoun/SanskritLexicography/pull/345)).
- [`DICTIONARY_REVIEWS_BIBLIOGRAPHY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DICTIONARY_REVIEWS_BIBLIOGRAPHY.md)
  — published reviews of the Sanskrit dictionaries (H731)
  ([PR #346](https://github.com/gasyoun/SanskritLexicography/pull/346)).
- Headword pairwise-overlap matrix over the 15-dict union (H684)
  ([PR #347](https://github.com/gasyoun/SanskritLexicography/pull/347)).
- E41/E42/F43 registered — correction-events trio, Kompozity `names.csv`,
  `allngramtxt` n-gram oracle (H694)
  ([PR #350](https://github.com/gasyoun/SanskritLexicography/pull/350)).
- Coward & Grimes 2000 (MDF lexicography guide) digested into the literature
  notes (H723)
  ([PR #351](https://github.com/gasyoun/SanskritLexicography/pull/351)).

### Changed
- papers: A40 headword-inventory prose completed over locked data, readiness
  3/5 → 4/5 (H675)
  ([PR #348](https://github.com/gasyoun/SanskritLexicography/pull/348)).
- pwg_ru H255 no_pwg_w03 drain: requeue of no_pwg_w02's 27 transient keys,
  11/27 promoted
  ([PR #344](https://github.com/gasyoun/SanskritLexicography/pull/344)).
- pwg_ru H255: fresh 6-headword no_pwg_w03 window + rq1 requeue, 9 clean
  promoted ([PR #352](https://github.com/gasyoun/SanskritLexicography/pull/352));
  pre-launch warm-up probe logged (21.05 s, GO)
  ([PR #353](https://github.com/gasyoun/SanskritLexicography/pull/353)).

### Fixed
- H255: [`RussianTranslation/src/pilot/no_pwg_scale_plan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py)
  STORE path — dedup was silently reading the wrong store
  ([PR #349](https://github.com/gasyoun/SanskritLexicography/pull/349)).
- Full-repo audit fix pass (H733): dead-link/doc-hygiene/CI/code fixes,
  `ROADMAP_2026_2027.md` → `ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`
  rename, `WSC2025_Reviews_7.pdf` rename — see
  [Uprava H733](https://github.com/gasyoun/Uprava/blob/main/handoffs/H733-Fable_SanskritLexicography_full-repo-audit-fix-pass_11.07.26.md).

## [1.6.0] - 2026-07-11

### Added — publication-pipeline deep manual (H608)
- New [`docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md):
  subsystem deep manual for the publication layer —
  [`papers/`](https://github.com/gasyoun/SanskritLexicography/tree/master/papers)
  lifecycle (stable A-IDs, readiness scale, the scaffold→referee→author-pass
  skill chain), the M01 Brill/De Gruyter book build (article→chapter recipe,
  rights-table trigger rule, FAIR/DOI critical path as of 11-07-2026), and
  [`docs_site/`](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site)
  build/test/deploy state (built + tested, **not yet deployed** — no
  `research/` on `gh-pages`). Router row added, PROFILE deep-manual queue row
  flipped, metadoc revision logged. Third item of the H604 queue; per
  [Uprava H608](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H608-Fable_SanskritLexicography_papers-book-publication-deep-manual_11.07.26.md).

## [1.5.2] - 2026-07-11

### Added — RussianTranslation deep manual (H606)
- New [`docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md):
  first subsystem deep manual per the
  [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
  queue — mw_ru covered as a finished-pipeline post-mortem, pwg_ru as the live
  operator procedure (production window step-by-step with traps inline, lanes +
  medium50 pause state, kill-gate mechanics, RU/EN parity contract, 216-script
  census with destructive-on-rerun table, data-assets/rights boundary).
  Fact-checked against sources; router row, PROFILE queue flip, and metadoc
  revision row in the same change. Fable 5 (`claude-fable-5`), 11-07-2026.

## [1.5.1] - 2026-07-11

### Fixed — FINDINGS.md duplicate section keys (H616)
- Repaired the seven accidentally duplicated `§N` citation keys found by the
  H604 fact-check: the later twin of each pair renumbered to a fresh key with a
  one-line tombstone under the renamed heading — §60→§70 (pwg_ru TM composite
  grade), §62→§71 (PWG case-government census), §63→§72 (VedaWeb `id_gra` =
  GRA `<L>`), §64→§73 (VedaWeb license fields), §65→§74 (ls-graph degeneracy
  for MW), §69→§75 (Devībhāgavata not on GRETIL). The second "§56" was a
  verbatim double-append of §68 (spellchecker landscape, PRs #305/#307) and was
  removed with a tombstone under §68. Header max-number marker corrected
  (§65→§75); stale citations of the renamed twins repointed in
  [`STALENESS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md),
  [`ROADMAP_VEDAWEB_REUSE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md),
  [`RussianTranslation/PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md),
  [`RussianTranslation/USE_CASES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md)
  and `RussianTranslation/.ai_state.md`; duplication caveats dropped from
  [`docs/manuals/MAINTAINER_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md) §3
  and [`docs/manuals/RESEARCHER_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md) §5;
  metadoc backlog item 4 closed.

## [1.5.0] - 2026-07-11

### Added — audience manuals
- New [`docs/manuals/`](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals):
  four deep, standalone manuals for distinct audiences — maintainer, researcher,
  student (Russian), and data-reuser — plus a
  [router README](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md).
  Linked from the root README documentation map. Language follows audience
  (student = Russian; the rest English). Built under
  [Uprava H535](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H535-Opus_SanskritLexicography_audience-manuals-quartet_10.07.26.md).

### Changed — CLAUDE.md reflects the repo is now hybrid (data + code)
- Corrected the stale "no source code (no `.py`…)" and "Python/JS lint jobs …
  never fire because no such files exist" claims in
  [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md):
  the repo now carries substantial Python (263 tracked `.py`, a root
  `requirements.txt`) and CI's Python lint + RussianTranslation gates do fire.
  Follow-up flagged under H535 (already noted in the maintainer manual).

### Added — other highlights since v1.4.0 (synthesized from git log; the tagged pwg_ru releases v1.2.0–v1.4.0 themselves are backfilled as sections below)
- Public PWG→RU translation **progress dashboard**
  ([PR #315](https://github.com/gasyoun/SanskritLexicography/pull/315)).
- pwg_ru article site: `<ab>`/`<ls>` tooltips + RU-column abbreviation purity per
  [`RussianTranslation/ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
  ([PR #308](https://github.com/gasyoun/SanskritLexicography/pull/308)); multi-second
  freeze on large articles fixed ([PR #320](https://github.com/gasyoun/SanskritLexicography/pull/320)).
- M01 literature crosswalk + 37-manual library metadoc, H505
  ([PR #319](https://github.com/gasyoun/SanskritLexicography/pull/319)).
- FINDINGS §66–§69 (QL SLP1 truncation, PWG article-size confound, spellchecker
  landscape, DBhP absence from GRETIL) and DEAD_ENDS/GAPS/ASSUMPTIONS episteme
  entries for the Sundara apparatus and F4-DCS edition-mismatch dead ends.
- Editorial rule applied repo-wide: drop `ё` (keep the всё/все distinction), H543
  ([PR #324](https://github.com/gasyoun/SanskritLexicography/pull/324)).

## [1.4.0] - 2026-07-06

pwg_ru pipeline release (tagged "pwg_ru 1.4.0"); section backfilled 11-07-2026
from the [GitHub release](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.4.0).
Full detail in
[`RussianTranslation/CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md).

### Added — no-PWG supplement-chain lane (H214)
- PWG-missing headwords with a PW/SCH/PWKVN/NWS record now render as standalone
  supplement-chain sub-cards (`<key>~~h0_zz_<layer>`), no fabricated PWG base
  portrait. Per-card `source_profile` (`no_pwg_supplement_chain` /
  `pwg_with_supplements` / `pwg_only` / `pwg_supplement_subcard`) on every
  promoted row; the 232 PWG-miss lemmas become a `no_pwg_runnable` lane. First
  live run validated end-to-end, 5 verified-clean sub-cards promoted; residual
  low single-card throughput tracked in H220.

### Added — upstream-change watcher (H182)
- [`RussianTranslation/src/pilot/watch_upstream.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/watch_upstream.py):
  monthly Cologne + NWS drift detection → stale-worklist; flag-only, on a
  scheduled workflow.

### Fixed
- `{{Lbody=NNNN}}` alternate-headword-pointer leak (`dict_merge.resolve_lbody()`)
  and the nominal audit crash (`audit_window.py` now skips glue for no-rootmap
  windows). PRs
  [#174](https://github.com/gasyoun/SanskritLexicography/pull/174),
  [#178](https://github.com/gasyoun/SanskritLexicography/pull/178),
  [#183](https://github.com/gasyoun/SanskritLexicography/pull/183),
  [#185](https://github.com/gasyoun/SanskritLexicography/pull/185).

## [1.3.0] - 2026-07-05

Section backfilled 11-07-2026 from the
[GitHub release](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.3.0).

### Changed — nominal-window guardrails (H191 verified, optimized, staged)
- H189 `pril10_w1` post-mortem verified deterministically: the aborted
  top-size nominal run reproduces to 42,316,604 tokens / ~$79.83, confirming
  fragment-level `agent()` fan-out plus repeated cache writes caused the
  blow-up.
- Generated harness size reduced for cached/retry windows: non-agent cards
  omitted from `INPUTS`/`PH`; TM-resolved and degenerate pass-through cards
  stay self-contained in `TM_RESOLVED` / `DEGENERATE_RESOLVED`.
- Monster handling hardened in two places: citation-dense single-line senses
  split only at complete `<ls>...</ls>` spans, and `perf_preflight.py` emits
  `cost_partition.run_now` / `cost_partition.defer_monster` grouped totals, so
  mixed windows run their cheap cards while `kAla`-class cards route to a
  human-budgeted lane.
- First safe nominal follow-up staged:
  [`RussianTranslation/src/pilot/NOMINAL_W1_100SMALL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/NOMINAL_W1_100SMALL.md)
  — 100 small Приложение 5 heads, 95 live inputs, 5 degenerate pass-through
  cards, 0 deferred monsters, 3 expected agents, ~745k tokens / ~$1.41
  estimated; the downstream Sonnet/Max run delegated to Uprava H201.

## [1.2.0] - 2026-07-04

Section backfilled 11-07-2026 from the
[GitHub release](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.2.0).

### Added — production ramp planning (runnable work, not wishful work)
- Live PWG→RU ramp planner `ramp_plan.py` (since retired) for the
  100 → 1,000 → 10,000 card progression, pricing each runnable root with the
  same preflight machinery used before Max spend; 10,000-card mode marked as a
  root-by-root drain (default concurrency 1, hard ceiling 3).
- H151 verb-root worklist made runnable-aware
  ([`RussianTranslation/src/pilot/verb_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py)):
  702 DCS-attested verb roots remained, 13 runnable, 689 blocked on rootmap
  generation/recovery. First controlled ramp target locked to runnable roots
  `tyaj`, `dah`, `kzip` (106 cards/sub-cards, 45 expected agents).

### Changed — QA gates fail loud, then requeue
- RU audit gate hardened: child auditors must emit strict `FLAGGED_JSON`;
  missing/malformed verdict lines crash loud and requeue the whole window.
- Real EN duplicate-sense hard gate added and gate-bug fixes ported across the
  EN path (language parity); Latin/Greek cue-masking leak fixed
  (`<ab>lat.</ab>` behind a placeholder is expanded for classification);
  collection/store writes made safer (robust JSON-string parsing, one parsed
  batch pass, coalesced appends).

### Added — schema-validated translation-memory publication assets
- Publication + terminology export commands for the TM lane: RU publication
  feed checksum-locked and schema-validated under `release/translation_memory/`
  (2,392 publication records pass validation); the `sa_ru_terminology` DOI lane
  intentionally empty until curated term suggestions exist; fuzzy TM matches
  advisory-only until validated.

### Added — review discipline + pipeline versioning
- Blocking
  [`RussianTranslation/src/review_changelog_guard.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_changelog_guard.py)
  hook: major review/audit edits must update the changelog in the same diff (or
  carry an auditable `Changelog: not applicable` marker); wired into pre-commit
  and CI.
- [`RussianTranslation/src/pipeline_version.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_version.py)
  + manifest `src/pipeline_versions.json`: a semver per output-affecting
  component family (prompt / glossary / script), orthogonal to the model
  version, stamped into every stored row's `provenance.pipeline` by both store
  producers — answers "which stored translations predate this tooling fix and
  need a batch re-run?". Forgotten-bump guard (content-SHA freeze + `check`
  warning), stale-row reporting, explicit-only backfill for legacy rows; store
  at introduction: 10,794 rows bucketed unversioned-legacy (not falsely marked
  stale), baseline frozen at v1.0.0.

## [1.1.5] - 2026-07-03

### Added — Indische Sprüche dataset
- New [`IndischeSprueche/`](https://github.com/gasyoun/SanskritLexicography/tree/master/IndischeSprueche)
  data asset: the full Böhtlingk *Indische Sprüche* collection (2nd ed. 1870–1873),
  7,537 sayings exported from `VisualDCS` archive.sqlite's `subhashita` table (D4)
  via the new `VisualDCS/src/DCS-data-2026/export_subhashita_jsonl.py`, as
  [`IndischeSprueche/data/indische_sprueche.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl).
  PWG cites this collection 6,666 times and PWK 138 times as `Spr. N` — see
  [`IndischeSprueche/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/README.md)
  for provenance and the scoped PWG/PWK citation-crosswalk follow-on
  ([Uprava H143](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H143_pwg_pwk_indische_sprueche_crosswalk.md)).

## [1.1.4] - 2026-07-03

## [0.0.42] - 2026-07-02

### Changed — A36 ready to send (Fable S9 pre-submission pass)
- [`papers/A36_latin_obscena_note.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena_note.md)
  reaches **5/5 ready-to-send** for *Beiträge zur Geschichte der Sprachwissenschaft*: referee-style
  review [`papers/A36_review_fable5.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_review_fable5.md)
  (7 major + 7 minor findings, all applied same pass — history-first retitle, Liddell–Scott /
  Cambridge-Greek-Lexicon comparandum in §0, Bopp-has-no-√yabh + MW72-etymological-*cunnus*
  source corrections against csl-orig, Adams register set re-defined, §3c table repaired; every
  table figure re-verified against the three CSVs). Cover letters (EN/DE) synced.
  ([PR #74](https://github.com/gasyoun/SanskritLexicography/pull/74)) — Fable 5 (`claude-fable-5`).

### Added — FINDINGS §44
- Raw Latin-string tallies over gloss text include etymological false positives (MW72's lone
  *cunnus* glosses a Lithuanian cognate); Bopp lacks √*yabh* entirely — reuse caveats for
  [`papers/A36_corpus_screen.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_corpus_screen.csv).
  ([PR #76](https://github.com/gasyoun/SanskritLexicography/pull/76))

## [0.0.41] - 2026-07-02

### Fixed — dashboard: single-snapshot charts no longer render as a floating dot
- With only one monthly snapshot, each tracked-metric chart drew a lone centered dot in an
  empty box (looked broken). Single-snapshot metrics now render as a stat card (big value +
  "trend line appears with the next monthly refresh"); real multi-point series gain min/max
  axis labels, first/last month labels, gridlines, and an emphasized last point. Both states
  browser-verified (the multi-point branch against a synthetic two-snapshot series).

## [0.0.40] - 2026-07-02

### Added — FINDINGS dashboard (recurring visualization of the registry)
- New [`findings_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard):
  a single-file dashboard (vanilla JS + inline SVG, no build step) live at
  <https://gasyoun.github.io/SanskritLexicography/findings/> — importance × section matrix,
  staleness flags (> 180 days, 🔴-first), monthly time series for the re-measurable findings
  (§12 DCS→CDSL linkage, §13 glossary coverage, §21 citation coverage, §25 queue decay,
  registry size), and the §41 platform-liveness board (12 platforms).
- **Refresh = monthly, mixed:** GitHub Actions cron
  ([`findings-dashboard.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml),
  3rd of month) for registry meta + metric collection; a local Task-Scheduler run
  ([`monthly_refresh.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/monthly_refresh.py))
  for the platform probes, which need residential egress (GHA IPs are blocked by several
  hosts). Collectors verified against live values (81.4 / 86.6 / 83.2 / 0.82 %).
- Scope: public SL registry only — the private Uprava infra registry is deliberately excluded.
- Built by Fable 5 (`claude-fable-5`); page render browser-verified before publish.

## [0.0.39] - 2026-07-02

### Added — FINDINGS.md: importance labels on every finding
- Every finding (§1–§43) now carries a 3-level colour dot at the start of its claim line and
  index entry — 🔴 3 important · 🟠 2 medium · 🟡 1 not that important — mirroring the issue
  taxonomy's severity palette (minor/medium/hard). Legend + assign-on-append rule added to the
  schema. Same treatment in
  [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (§1–§9).
  Plain emoji — no HTML; heading anchors untouched (dots live outside the headings).

## [0.0.38] - 2026-07-02

### Changed — FINDINGS.md: HTML Source styling reverted to plain blockquotes
- The v0.0.37 `<div align="right">` + `<sub>` Source styling was **rejected on review**
  ("looks ugly, never repeat") and removed same day. Every **Source** paragraph in
  [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  (and [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)) is now
  a plain blockquote `> **Source:** …` — left indent + GitHub's muted rendering, zero HTML.
  The no-HTML-in-md rule is restored as absolute (global rule, md-hygiene skill, and memory
  updated with the tested-and-rejected verdict). § numbering from 0.0.37 stays.

## [0.0.37] - 2026-07-02

### Changed — FINDINGS.md: § signs + right-aligned small Source lines
- Every finding number now carries the paragraph sign (`### §16. …`, mirrored in the index;
  anchors unchanged — GitHub strips `§` from slugs). Every **Source** paragraph is right-aligned
  small type via `<div align="right">` + `<sub>` — the one **sanctioned HTML** in the FINDINGS
  registries (grey text is impossible on GitHub around clickable links; right+small is the
  agreed stand-in). Same treatment in
  [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (§1–§8).
  The global no-HTML-in-md rule, the md-hygiene skill, and memory carry the matching carve-out.

## [0.0.36] - 2026-07-02

### Changed — FINDINGS.md: numbered findings + Source as own paragraph
- Every finding in [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  now carries a paragraph number in its heading (1–40, **append-only** — a new finding takes
  the next free number, existing numbers never shift, mirrored in the index anchors), and each
  **Source** line is its own paragraph so it renders on a separate line. Same treatment applied
  to the [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) infra
  registry (8 findings).

## [0.0.35] - 2026-07-02

### Changed — FINDINGS.md restructured into an indexed, anchored registry
- [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md):
  every finding is now a `###` heading with a stable anchor, plus a MEMORY-style one-line
  index at the top (40 findings) — recall without reading bodies. Dated header + byline
  added; the intro's `PILOT_LESSONS`/`SHARED_CODE` links upgraded to full blob URLs.
- Re-sectioned: the four Sanskrit-data findings mis-filed under "Tooling & infra" moved to a
  new **Etymology & derivation** section / "Dictionary structure & markup"; the CodeQL-has-no-PHP
  finding moved to [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
  (infra registry), leaving a pointer.

### Added — 15 new verified findings from a six-repo sweep
- Sweep of WhitneyRoots, VisualDCS, SanskritSpellCheck, csl-atlas, csl-apidev, csl-observatory,
  csl-corrections + this repo (6 parallel Fable 5 `claude-fable-5` Explore agents, then a
  dedicated Fable 5 fact-check agent re-verified every number against its source file — 12
  agent-reported inaccuracies corrected before commit). Highlights: DCS `OccId`/`sent_id` non-unique (134,047
  tokens / 449 sentences dropped pre-fix); UD `Tense=Past` conflates aorist/perfect; homonym
  token-split ceiling (5/38 gaṇa-splittable); Sa→Ru glossary 86.6 % token coverage; PWG∩MW
  union = 94,753; MW inherited PWG's apparatus skeleton (0.81 citation-order concordance);
  gloss-language ortho-drift ∝ reform type (RU 358/1k ≫ DE 10.3 ≫ FR/EN ≤ 0.5 ≫ LA 0);
  body-text headword mining dead end (38.6 % precision — negative result rescued from a
  deleted review artifact).
## [0.0.34] - 2026-07-02

### Changed — kosha planning-corpus triage (audit, 4 locked meta-decisions, scaffold removed)
- `KOSHA_FOLDER_SETUP.md` rewritten as an honest status doc (was "Setup Complete" over empty
  directories); `KOSHA_DECISIONS_NEEDED.md` blanks filled with real decisions (M1–M4;
  cadence/etymology left OPEN).
- Triage banners + inline fixes: real `<pc>` formats (MW page/column single-volume; PWG
  volume-page hyphen; AP90 page-column-letter), real Heritage/Cologne endpoints, current
  headword counts, VedaWeb/Lexonomy URLs, `union_headwords` marked already-built.
- `KOSHA_DEPLOYMENT.md` added: salvage of `kosha/DEPLOYMENT.md` + README API contract with
  4 config defects fixed (`Type=notify`, missing `proxy_pass`, `WorkingDirectory`,
  force-push advice).
- The `kosha/` scaffold in this repo deleted until code is real (M2: dedicated `kosha` repo;
  M4: own Pages). (Fable 5 `claude-fable-5`.)

## [0.0.33] - 2026-06-29

### Added — grammar-layer FAIR package + VedaWeb accent-axis probe (follow-up to 0.0.32)
- **Declension display** shipped (`nominal_grammar.py --table`, `reverse_index.py --show`) — vidyut
  paradigm table per headword / per paradigm token. Per-word grammar dataset materialized into
  `headword_index.tsv` (98,639 rows; kept out of translation — portraits untouched).
- **FAIR data package** `RussianTranslation/src/datapackage.json` (Frictionless, CC-BY-SA-4.0) over
  the five grammar resources with field schemas, sources, and deterministic-rebuild provenance;
  archivable on its own DOI track.
- **VedaWeb accent-axis probe CONFIRMED**: VedaWeb 2.0 API live (`vedaweb.uni-koeln.de/api`); the
  Casaretto et al. (2025) annotation layer returns udātta-marked, position-aligned per-word forms
  (RV 6.59.3: `…agnī́; ávasā; …devā́`) with co-located lemma+morphology and a bulk export — the
  accent a–f axis is de-risked (only the Whitney-rule encoding + join remain). Turnkey API path +
  resource IDs recorded in `ZALIZNYAK_INDEX.md` and `FINDINGS.md`.

## [0.0.32] - 2026-06-29

### Added — pwg_ru structured grammar layer (nominal grammar, Zaliznyak index, reverse dictionary)
- **Nominal grammar layer**: `RussianTranslation/src/nominal_grammar.py` (stem class, Whitney §§,
  vidyut subanta paradigm with the `nyap` fix for feminine ā/ī/ū stems) + `src/mw_compounds.py`
  (106,603 MW `<k2>` compound segmentations). Whitney exception §§ folded into the root layer
  (`whitney_grammar.json`, 289 records). Docs: `GRAMMAR_LAYER.md` (hub).
- **A/B test → grammar-in-translation REJECTED** (`NOMINAL_GRAMMAR_AB.md` +
  `NOMINAL_GRAMMAR_AB_DETAIL.md`): blind Opus judge over 8 stratified headwords, arm A (grammar
  OFF) 5 / tie 2 / arm B (ON) 1; both arms 0 nulls, 100% markup fidelity. Nominal windows run
  grammar **OFF**; the layer is kept as structured data only (portraits left untouched).
- **Zaliznyak inflection index** (`ZALIZNYAK_INDEX.md`): compact per-word token `G·T S F`
  (e.g. `m·8n*`); **reverse dictionary** over all 123,366 PWG entries → 98,639 indexed → 335
  paradigm tokens; per-word FAIR dataset `headword_index.tsv` + `reverse_paradigm_index.json` +
  `paradigm_stats.tsv`; **declension display** via vidyut (`--show` / `--table`).
- **Accent a–f axis** spec'd + unblocked: Whitney's per-case accent §§ already ingested + PWG
  `key2` accents + **VedaWeb** (CC BY 4.0) as the validation set; logged in `FINDINGS.md`.

## [0.0.31] - 2026-06-26

### Fixed — stale-doc cleanup across the pwg_ru planning/runbook set
- Aligned the `RussianTranslation/` docs with the current pipeline after the judge-escalation +
  harvest-port changes: corrected present-tense "Opus judges every card" claims to the
  Sonnet-bulk + Opus-on-reject policy (STRATEGY.md, FREQ_TEST_RUNBOOK.md, HANDOFF); marked the
  four prompt nits and the `--root-split` hook as done; noted the dropped `pwg_preverb1.txt`
  sandhi-join follow-up; added superseded-pointers to the pre-Max-harness plans
  (IMPLEMENTATION_PLAN.md, PIPELINE_ARCHITECTURE.md) and a "now-implemented" note to PILOT_COST §7.
  Correct historical statements (the Opus-run validation passes) were left intact;
  `research/JUDGE_POLICY.md` is the single source of truth for the judge policy.

## [0.0.30] - 2026-06-26

### Changed — pwg_ru judge escalation: Sonnet bulk, Opus only on hard cases
- Implemented the decided judge policy (`RussianTranslation/research/JUDGE_POLICY.md`) in the Max
  harness (`RussianTranslation/src/pilot/run_pilot_wf.js`): **Sonnet judges every card; Opus
  re-judges ONLY the rejects** (`ok=false || severity>=3`), Opus verdict final. Publishable cards
  (sev 1–2) spend no Opus tokens — the weekly-quota headroom that makes the bulk run feasible on one
  Max seat. Justified by the κ=1.0 / 474-card A/B (`JUDGE_AB.md`). Pipeline now 3-stage
  (Translate · Judge · Adjudicate); `node --check` clean. Runbook + policy docs marked implemented.

## [0.0.29] - 2026-06-26

### Changed — pwg_ru bulk-run preflight: harvest ported into the production harness
- **Launch-readiness audit** of the PWG→Russian bulk run (translator = Sonnet, judge =
  Opus 4.8). Verdict: GREEN to start the first instrumented window. Confirmed all four
  "pre-run prompt nits" already encoded in the Max harness and all gate scripts wired.
- **Literature-harvest refinements ported into the live harness**
  (`RussianTranslation/src/pilot/run_pilot_wf.js`, which inlines its own prompt and does not
  read `pwg_ru_prompts/*.txt`): samāsa right-headedness, the *yad…tad* correlative map,
  śāstric formula equivalents, synonym-string cardinality, comma/semicolon sense-grouping,
  manner/position forcing, plus a soft judge check. `node --check` clean.
- **Runbook + docs updated:** `RUN_FREQ_MAX.md` window loop (SECTION warning + fidelity-gate
  step); [`MANUALS_FIVE_DEEP_DIVE.md`](RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md) closing
  section rewritten as a per-finding pipeline-status table (live / ported / deferred);
  `pwg_ru.md` gains a theoretical-basis pointer to the literature docs.

## [0.0.28] - 2026-06-26

### Added — literature shelf mined for the Sanskrit→Russian dictionary
- **Per-manual audit + theory deep-dive for pwg_ru.** Three new docs under
  `RussianTranslation/`: [`LITERATURE_FOR_PWG_RU.md`](RussianTranslation/LITERATURE_FOR_PWG_RU.md)
  (three-pass full-text harvest of the whole `literature/md/` shelf, distilled by pipeline
  insertion point), [`MANUALS_FOR_PWG_RU.md`](RussianTranslation/MANUALS_FOR_PWG_RU.md) (all
  **37** `Lexicography-Manuals/` walked one at a time — 19 drive theory, 2 marginal, 15 serve
  other repos, 1 OCR-blocked), and
  [`MANUALS_FIVE_DEEP_DIVE.md`](RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md) (detailed,
  text-grounded theory of the five load-bearing manuals — Apresjan, Riemer, Hartmann & James,
  Gonda–Vogel, Klosa — for making a Sanskrit–Russian dictionary).
- **Harvest folded into the live pipeline:** the pwg_ru translator and QA-judge prompts plus a
  new hand-curated glossary `RussianTranslation/glossaries/de_ru_translation_aids.md` (samāsa
  types, case-absolute constructions, śāstric formulas, the *yad…tad* correlative map, the
  19th-c. German orthography decoder).
- **Literature index refreshed.** [`literature/md/INDEX.md`](literature/md/INDEX.md) gains the
  **⚠ blocked** convention (5 files un-mineable until re-OCR'd / re-extracted), RuTrans tags on
  Renou/Apresjan/Tubb, and ✓-fixed notes on the two re-sliced NLP-proceedings bundles
  (Adapting-NLP, Performance-POS). README documentation-map updated to point at the new docs.

## [0.0.27] - 2026-06-26

### Fixed — doc consolidation
- **Broken relative links repaired.** `union/UNION.md` (generated) linked its scripts and
  sibling TSVs with HeadwordLists-relative paths although the file lives in `union/`; fixed
  in `build_union.py`'s md generation (`../build_union.py`, `../screen_candidates.py`,
  same-dir TSVs) and the Catalan §7 `accent_review.py` link → `../accent_review.py`. All **143
  internal links across the 19 HeadwordLists md files now resolve** (0 broken).
- **`.ai_state.md`** gains a "Current status (2026-06-26)" header: HeadwordLists print-readiness
  agent-prep complete (A–F), pwg_ru Track A ongoing.
## [0.0.26] - 2026-06-26

### Added — accent disagreements rendered for adjudication (item C)
- [`accent_review.py`](HeadwordLists/accent_review.py) → [`Catalan-Pujol/accent_disagreements.tsv`](HeadwordLists/Catalan-Pujol/accent_disagreements.tsv):
  the **63** Pujol-vs-Cologne accent-position disagreements (32 vs GRA, 31 vs MW), each
  rendered as **accented IAST on both sides** (`bhagá` vs `bhága`) with the vowel ordinal and
  a `recommend` column (Cologne RV/MW canonical). The print list (the union) already uses the
  Cologne `<k2>` accents, so item C resolves to: **use Cologne accents; the 63 are a QA list
  for the Catalan editors**, not a change to the print list. §7 + PRINT_READINESS C updated.
- **All PRINT_READINESS agent-prep is now complete** (A–F): the remaining work is human
  verification/decisions, and the two headline findings stand — CDSL coverage of attested
  vocabulary is essentially complete (B), and the MW/PWG spine is gated only by 16 typos (A).
## [0.0.25] - 2026-06-26

### Changed — typo queue extended to all 122; coverage additions cross-tagged
- **A — all 122 typos.** [`assemble_typo_queue.py`](HeadwordLists/assemble_typo_queue.py) now
  auto-discovers every dict's FILE-FIRST queue → [`A_TYPO_QUEUE.md`](HeadwordLists/A_TYPO_QUEUE.md)
  is the full **122 across 11 dicts** (spine MW 4 + PWG 12 first, then SHS 37, YAT 27, ACC 22,
  MCI 10, SKD 3, WIL 3, PW 2, GST 1, VCP 1), each with IAST + error type + entry-body evidence.
- **B — cross-tagged.** [`crosstag_additions.py`](HeadwordLists/crosstag_additions.py) tags the 416
  priority additions with Catalan/Huet external attestation
  ([`union/coverage_additions_crosstagged.tsv`](HeadwordLists/union/coverage_additions_crosstagged.tsv)).
  **Only 25/416 (6 %) are externally corroborated, and ~8 are genuine real words** (`karkandhū`
  jujube, `maṇikā` jar, `cittamātra`, `nistaraṅga`…); the rest are verb roots / Pāṇinian affixes
  (`ghañ`, `ktvā`) Catalan/Huet also headword. **Conclusion: CDSL coverage of attested vocabulary
  is essentially complete — the print list needs ~nothing added.**
## [0.0.24] - 2026-06-26

### Added — MW+PWG typo queue assembled (item A)
- [`assemble_typo_queue.py`](HeadwordLists/assemble_typo_queue.py) consolidates the print
  spine's body-confirmed FILE-FIRST typos from
  [SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) into
  [`A_TYPO_QUEUE.md`](HeadwordLists/A_TYPO_QUEUE.md): **16 (MW 4 + PWG 12)**, each with SLP1 +
  IAST, an **error-type** label (n→ṇ, vowel-length, sibilant, b↔v, aspirate) and the
  dictionary's **own entry-body evidence**. PWG's are mostly **b↔v** (Fraktur-OCR). Verify on
  scan → flip `n`→`y` → file to csl-corrections (workflow stays in SanskritSpellCheck). The
  spine's "don't print known typos" pass is now a 16-row checklist.
## [0.0.23] - 2026-06-26

### Added — coverage additions ranked by DCS band (item B)
- [`coverage_additions.py`](HeadwordLists/coverage_additions.py) → DCS-corpus lemmas absent
  from all 15 CDSL dicts (the union, with folded feminines added back to the baseline),
  ranked by frequency band: [`COVERAGE_ADDITIONS.md`](HeadwordLists/COVERAGE_ADDITIONS.md) +
  [`union/coverage_additions.tsv`](HeadwordLists/union/coverage_additions.tsv).
- **21,759 absent**, but the high-frequency end is **lemmatisation artifacts** (causative `-ay`
  stems, prefixed/desiderative roots, bīja, indeclinables — flagged by a `kind` column), not
  real gaps. Genuine **nominal** additions concentrate low-band; the **actionable priority =
  409 band-3 nominal** (e.g. `bhasmasūta`, `bhṛgutīrtha`, `āntarika`). Confirms the Catalan §5
  pattern: real coverage gaps are rare words. PRINT_READINESS B marked ranked.
## [0.0.22] - 2026-06-26

### Added — gloss pre-screen of the low-confidence fold candidates
- [`screen_candidates.py`](HeadwordLists/screen_candidates.py) pulls the short **MW gloss** for
  both forms of each of the 426 low-confidence `-ā/-ī` fold candidates →
  [`union/low_candidates_screened.tsv`](HeadwordLists/union/low_candidates_screened.tsv). Result:
  **419 likely-distinct** (reject at a glance — `ārā` "awl" vs `āra` "brass"; `īṣā` "carriage-pole"
  vs `īṣa` "the month Āśvina") and **7 MAYBE-related** to eyeball (`tālikā`/`tālika` same gloss;
  `adharmā`/`adharma`). Cuts the editor's low-set review from 426 to ~7; the gloss is the first MW
  sense (text after `</lex>`, before the first `<ls>` citation, etymology stripped).
## [0.0.21] - 2026-06-26

### Changed — union now covers all 15 dicts + fold candidates ranked
- **Fuller union.** `build_union.py` now reads `<k1>` directly from current csl-orig for
  **all 15 dicts** with a source (adds the 7 key2-only dicts BHS/BUR/CAE/CCS/INM/MD/SCH to
  the original 8) → **323,425** headwords (was 295,298), 180,989 in ≥2 dicts.
- **Fold candidates ranked for review.** The `-ā`/`-ī` candidates in
  [`union/fold_candidates.tsv`](HeadwordLists/union/fold_candidates.tsv) now carry a
  `confidence` (+ `n_shared_dicts`, `masc_gender`): **3,569 high** (the masculine base is
  itself `mfn`, so the `-ā/-ī` genuinely is its feminine — `parā←para`) vs **426 low** (masc
  `m`-only → likely a distinct lexeme like `āśā`≠`āśa`). Review high first. 237 `-inī`
  auto-folded. Gender is MW/AP-driven (BUR has no `<lex>`).
## [0.0.20] - 2026-06-26

### Added — cross-dict UNION headword index (scope E) with feminine fold (F)
- **Scope decided = union**, feminines folded under the masculine. [`build_union.py`](HeadwordLists/build_union.py)
  merges the 8 key1 dicts (AP GRA MW PWG PWK SKD VCP VEI) from `now-2026/` into a single
  **295,298-headword** index with per-headword **provenance** (which dicts attest it) and
  **gender** aggregated from each dict's `<lex>` (parsed per multi-line `<L>` record).
  → [`union/UNION.md`](HeadwordLists/union/UNION.md), `union/union_headwords.tsv`
  (`slp1, iast, n_dicts, dicts, gender, fem_fold`).
- **Feminine fold, gender-driven and split for safety:** only the unambiguous **`-inī`→`-in`**
  (238, gender-confirmed) is auto-folded — the masculine base gets an `mf(ī)` marker; the
  **3,993 `-ā`/`-ī`** cases go to [`union/fold_candidates.tsv`](HeadwordLists/union/fold_candidates.tsv)
  for editor review, because a feminine `-ā` noun often shares a stem with an unrelated
  masculine `-a` (e.g. `āśā` "hope" ≠ feminine of `āśa` "corner"). Auto-fold audit in
  `union/folded_feminines.tsv`. Covers the 8 key1 dicts; key2-only dicts mergeable next.
## [0.0.19] - 2026-06-26

### Added — item-F candidate lists (`alternate_headwords.py` + `f_candidates/`)
- Generated the editor worklists for PRINT_READINESS item **F**:
  [`alternate_headwords.py`](HeadwordLists/alternate_headwords.py) emits, from the 2026
  key1 sets, feminine↔masculine pairs, orphan feminines, variant-spelling pairs
  (b~v / ś~ṣ / geminate), and multi-`<k2>` alternate groups (SLP1 + IAST) into
  [`f_candidates/`](HeadwordLists/f_candidates/), summarised in
  [`ALTERNATE_HEADWORDS.md`](HeadwordLists/ALTERNATE_HEADWORDS.md). **MW: 5,036
  feminine↔masculine pairs, 22,298 orphan feminines, 1,217 variant pairs, 0 multi-`<k2>`**
  (alternate comma-lists negligible). SKD generated as a union-case sample. These are
  candidates to filter (morphological-shape pairing includes semantic non-pairs); the
  fold/keep/merge policy stays human.
## [0.0.18] - 2026-06-26

### Changed — PRINT_READINESS: add alternate/feminine headword gate (F)
- New checklist item **F — alternate & feminine headword policy** in
  [`PRINT_READINESS.md`](HeadwordLists/PRINT_READINESS.md). MW (2026) is **~14 % ā/ī-stems**
  (18,186 `-ā` + 9,148 `-ī`) and CDSL headwords feminines *inconsistently* — only 24 % of
  `-ā` feminines have a separate masculine base, 30 % of `-inī` have the `-in`. Pujol/INRIA
  list feminines separately; the corpus attests feminines CDSL omits. Plus variant/alternate
  spellings (b~v ≈ 397 MW pairs) and same-lemma multi-`<k2>` forms (comma-lists in SKD/VCP,
  which the now-2026 key2 split into separate lines). Policy (headword separately / fold with
  `mf(ā/ī)` / merge-and-cross-ref) is human; the candidate pair-lists are agent-doable. The
  MW/PWG print spine is largely unaffected (MW key2 = one clean form per entry).
## [0.0.17] - 2026-06-26

### Added — key2 re-extracted as SLP1 + a print-readiness checklist
- **key2 now regenerated as clean SLP1** into [`now-2026/`](HeadwordLists/now-2026/) for
  every dict (was key1-only). The 2014 key2 files are legacy numeric transliteration; the
  current `<k2>` is SLP1 but a naïve `<k2>([^<]*)` over-captured entry-body text / `{#..#}`
  compound blobs (a 64 MB dump). Fixed in `headword_diff.py` (`key2_forms`): stop the
  capture at the `¦` separator, strip `{#..#}`, split comma-lists → clean **print/citation
  form** keeping `/` accent, `-`/`—`, `(...)`, `*`, `˚` (e.g. `aMSa—karaRa`; SKD recovered
  40,817 vs the 64 MB blob). 23 now-2026 files (key1+key2; PD has no source).
- **[`HeadwordLists/PRINT_READINESS.md`](HeadwordLists/PRINT_READINESS.md)** — consolidates
  the A–E checks for publishing a printed headword list, with per-dictionary verdicts.
  **MW/PWG are the print-ready spine** (stable, +0.1 %/−0.0 % since 2014); the gates are
  human/editorial — **A** clear SanskritSpellCheck's 122 fileable typos (the "don't print
  known typos" pass, highest value), **B** coverage additions, **C** accents, **E** scope —
  while **D** (key2 as SLP1) is now closed.

## [0.0.16] - 2026-06-26

### Changed — foldered the snapshots (`then-2014/` + `now-2026/`) + % and TOTAL columns
- **Dated the snapshots.** The committed headword lists were verified (git) to have been
  extracted **2014-10-05** ("Cologne headwords"), so all 31 root `*.txt` now live in
  [`HeadwordLists/then-2014/`](HeadwordLists/then-2014/), and the current regeneration in
  [`HeadwordLists/now-2026/`](HeadwordLists/now-2026/) (was `now/`). Paths updated across
  the README, the Huet doc, and `huet_coverage.py`.
- **`NOW_VS_THEN.md` gains a `growth %` column and a TOTAL row.** Net change per list
  (e.g. **AP +146.6 %**, PWK +14.7 %, MW +0.1 %) and the aggregate over the 9 comparable
  lists: **605,813 → 733,617 (+21.1 %)**; grand total of all 26 snapshots' then-counts =
  1,721,983.

## [0.0.15] - 2026-06-26

### Added — `HeadwordLists/now/` current regeneration of the key1 snapshots
- Regenerated the **key1** lists from the **current** csl-orig into
  [`HeadwordLists/now/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)
  (renamed `now-2026/` in 0.0.16; filename = now-count), Sanskrit-collated;
  the parent THEN files are kept frozen so the two can be compared directly.
  `headword_diff.py now` produces them.
- **key1 only, deliberately** — it's the genuinely comparable set (THEN and NOW both
  SLP1 `<k1>`). key2 is skipped: the THEN `<k2>` is legacy numeric transliteration
  (format migration, not a headword diff), and several dicts' raw `<k2>` is `{#..#}`
  compound blobs, not lemmas (a naïve dump was 64 MB of markup). 8 written
  (AP, GRA, MW, PWG, PWK, SKD, VCP, VEI); PD has no csl-orig source.
- Notable now-counts: **AP 88,867** (was 36,030), **PWK 151,349** (was 131,918),
  **MW 194,084**, PWG 106,082, VCP 48,636. `now/README.md` documents scope + the
  Sanskrit-collation (compare by set, not line-diff) caveat; refreshed `NOW_VS_THEN.md`
  to match (csl-orig had drifted a little since the previous run).

## [0.0.14] - 2026-06-26

### Added — `HeadwordLists/` drift tooling, Huet/INRIA control, accent check, use cases
- **Now-vs-then diff of the `*-unique-key{1,2}-N.txt` snapshots.** `headword_diff.py`
  regenerates each list from current csl-orig; `NOW_VS_THEN.md` is the summary. The
  **key1** (SLP1) lists are comparable and have drifted: **AP 36,030 → 88,701**,
  **PWK 131,918 → 151,349** (large real growth), **MW 193,978 → 194,084** (+753/−647),
  PWG/GRA/SKD/VCP/VEI small. The **key2** snapshots are in the *legacy Cologne numeric
  transliteration* (`am2s4a` = aṃśa) vs current SLP1 — a format migration, flagged not
  reported. PD is not in csl-orig. (`removed`-word lists embedded for QA; scratch
  `_diff/` dumps gitignored.)
- **Huet / INRIA Heritage wordlist** — a non-Cologne control alongside Catalan-Pujol.
  `huet_coverage.py` decodes Huet's VH/Velthuis (`z`=ś, `f`=ṅ, `.s`=ṣ, `aa/ii/uu`) to
  IAST→SLP1 and runs the same coverage. 21,055 keys, **MW 83.5 % / all CDSL 86.2 %,
  DCS-attested 60.0 %**. Headline ([`Huet-INRIA-Wordlist-vs-Cologne.md`]): both are MW
  subsets, but the reader's lexicon is far more corpus-attested than Pujol's full
  dictionary spine (60 % vs 46 %) — less dictionary "dark matter".
- **Catalan-Pujol additions.** The full 177-lemma corpus-attested-no-CDSL list
  (`DCS-attested-no-CDSL.md`, §5, triaged); the **accent comparison** (§7,
  `accent_compare.py`): Pujol marks udātta with a combining acute, Cologne with `/`
  after the vowel, but **~97 %** agree on position (GRA 96.9 %, MW 97.1 %).
- **Use-case sections** added to all three studies: Catalan-Pujol §8 (CDSL gloss layer,
  corpus-confirmed candidate headwords, editor QA list, morphology overlay, learner's
  layer), Huet §5 (corpus-weighted core vocab, VH↔SLP1 bridge, benchmark), and
  `NOW_VS_THEN.md` (snapshot refresh, removed-word audit, re-transcoding triage).

## [0.0.13] - 2026-06-26

### Added — `HeadwordLists/Catalan-Pujol/` dataset + full coverage analysis
- **The dataset.** An external Sanskrit headword spine and its CDSL/corpus coverage
  analysis: the **61,266-lemma list** of the *Diccionari Sànscrit–Català* (Òscar Pujol,
  Enciclopèdia Catalana, 2005 — the first Sanskrit→Catalan dictionary), mirrored from
  `sanskrit-lexicon/CORRECTIONS`. In accented IAST with `√`-roots, Vedic udātta, and
  Pujol's compound-segmenting hyphens; UTF-8 **with BOM**.
- **Dictionary axis** — the list is essentially a Monier-Williams subset: **MW alone
  covers 88.5 %**, all 15 compared CDSL dicts together 91.0 %; the ~4,680 lemmas no CDSL
  dictionary covers are bucketed (simple / compound / root / prefixed-root / suspect-char)
  under `Catalan-uncovered/`. Two transcoding traps documented (display-added line
  numbers; `ś`=s+U+0301 accent collision; match rate 78 %→89 % after the fix).
- **Corpus axis (vs DCS)** — only **46.4 %** of the list is attested in the DCS-2021
  corpus though 91 % sits in a dictionary; **44.9 % is dictionary-listed but
  corpus-unattested** ("lexicographic dark matter"). The 0.3 % (177) corpus-attested with
  no CDSL entry is **triaged**: ~55 lemmatisation/morphology convention (41 prefixed/
  denominative verb roots, 9 productive `-tā/-tva/-tara/-tama/-vat`, 5 bīja), 29
  unheadworded compounds, ~93 simple/feminine — within which a genuine residue of
  corpus-attested **rare lexemes absent from all 43 CDSL dictionaries** (plant/animal
  names: `alasāndra-` cowpea, `kustumburī-` coriander, `kaṅkolī-`, `udumbarī-`, …) are
  real candidate additions.
- **Pujol's 11 headword conventions documented** (§6): `√`-roots, preverb+root
  segmentation with `√` on the final root, sandhi-resolution parens, Vedic udātta,
  compound hyphens, stem/feminine/productive-suffix forms, homograph numbering, bīja
  syllables, BOM + precomposed-`ś` encoding, and export artifacts.
- **Scripts** (repo-portable, IAST→SLP1 via `sanskrit-util`): `coverage_by_dict.py`,
  `match_rate.py`, `make_uncovered_lists.py`, and `coverage_vs_dcs.py` (dictionary ×
  corpus cross-tab against `VisualDCS/dcs_lemma_summary.json`). Full write-up in
  `HeadwordLists/Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md`; indexed in
  `HeadwordLists/README.md`.

> Provenance note: the dataset files were first committed in `56564a0` (initially via an
> accidental `git add -A`), then adopted and refactored repo-portable by a parallel
> session (`75b917d`); kept by decision. This entry consolidates all Pujol work.

## [0.0.12] - 2026-06-26

### Changed
- **`article-comparison/*.table.md` — rows ordered chronologically by edition year**
  (oldest → newest), so the side-by-side reads as the lexicographic tradition
  developing: WIL 1832 → YAT 1846 → BOP 1847 → PWG (Bd. I) 1855 → … → AP 1957 →
  PE 1975 → PD 1976. The `#` column renumbers to the new order. Sorting is in
  `_build_tables.py` (stable on the prior order for same-year ties, e.g. BUR/BEN 1866,
  GRA/VCP 1873, pw/PWK 1879).

## [0.0.11] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — full, untruncated entries.** The side-by-side
  tables previously capped each cell at ~800 chars with a trailing ` …`, so longer
  entries (e.g. STC, PWG, AP90, VCP, PE) showed only a fragment. Every cell now
  carries the **complete** condensed entry (citations in `[ ]` stripped, SLP1→IAST,
  paragraphs joined with ▸); PD remains its full sense skeleton (its verbatim entry is
  20–234 KB and stays in the verbatim/IAST files). 40 truncated cells expanded.

### Added
- **`RussianTranslation/src/_build_tables.py`** — the table builder, now committed (it
  never was). Regenerates all four tables from the full `*.iast.md` sections (+ the
  `*.pd-min.md` skeleton for the PD row), reproducing the original condensation but
  without the length cap, and with **nested-citation-safe** bracket stripping (fixes a
  stray `]` the old run left on `[m., [RāmatUp.]]`-style nested refs, e.g. akṣara/MW).

## [0.0.10] - 2026-06-25

### Added
- **`article-comparison/agni.gloss-review.md` — agent draft review of agni's 130
  hand-authored RU sense-glosses.** An Opus-4.8 editorial pass against the English PD
  sense + Sanskrit term + Russian Indological norm (Kochergina / Elizarenkova),
  produced as a **sign-off worklist** (the glosses themselves are untouched — they
  remain the draft they were flagged as). Findings: 1 factual category error (the
  *agnicayana* altar↔rite mix-up at senses 4i/4vi), 3 transliteration/precision fixes
  (ахаванья→ахавания; hotṛ "возливатель"→"призыватель"; udātta), 3 optional polish,
  4 optional add-glosses, and 6 English-source OCR typos already corrected in the RU.
  This is the agent-doable half of the Track B gloss review; final scholarly sign-off
  is the human step.

## [0.0.9] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — multi-volume Petersburg dictionaries now name
  the volume, not just the span.** A 7-volume dictionary's true year is the year of
  the *volume* containing the headword's letter. All four study words are a-stems, so
  the PWG / pw / PWK labels now read **Bd./Th. I** with the volume-1 year (PWG
  `Bd. I, 1855`; pw/PWK `Th. I, 1879`) instead of a bare year that read as the whole
  1855–1875 / 1879–1889 run. Header note explains the volume convention.

## [0.0.8] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — every quote now carries its dictionary's
  edition year.** Previously only a few EN dictionaries showed a year (MW 1899,
  AP90 1890, WIL 1832, MW72 1872); the Dictionary column now labels all 20 sources
  with their CDSL edition year — e.g. PWG 1855, pw/PWK 1879, GRA 1873, VCP 1873,
  SKD 1886, SHS 1900, BUR 1866, CAE 1891, BEN 1866, YAT 1846, BOP 1847, STC 1932,
  AP 1957, PE 1975, PD 1976. Years are taken from the authoritative
  [CDSL front page](https://www.sanskrit-lexicon.uni-koeln.de/) catalog (via
  `csl-guides/src/data/dictionaries.json`), the same source as the existing labels;
  a provenance note was added to each table header.

## [0.0.7] - 2026-06-25

### Changed
- **`article-comparison/` — Max-LLM residual per-sense pass (Track B tail).** Each
  attested Russian rendering the deterministic matcher left in the
  `### Не привязано к значению` bucket of every `*.persense-ru.md` was adjudicated
  by an Opus-4.8 pass against the full bilingual PD sense skeleton and routed to a
  specific sense — or kept as honest "other" (function-word / context / off-headword
  name). Per-sense coverage rises to **97–100 %** (`agni` 100 %, `akṣara` 99 %,
  `anya`/`ananta` 97 %). Implemented as a reproducible `LLM_ASSIGN` override map in
  `RussianTranslation/src/_build_persense_ru.py` (surface form → sense ordinal,
  mirroring `SYN`/`ROUTE`); LLM-assigned renderings carry a **°** marker and the
  coverage line reports the deterministic-vs-LLM split.

## [0.0.6] - 2026-06-25

> Backfilled to match tag `v0.0.6` (cut by a parallel actor against the project
> narrative `RussianTranslation/CHANGELOG.md`); this section records the same scope
> in the semver changelog.

### Added
- **Renou *register* axis** — an orthogonal multi-label `renou_register` field
  (20-code lattice: épigraphique, bhāṣya, jaina, …) parallel to the I–V Renou
  *state*, per `RussianTranslation/RENOU_SUBSECTIONS_PLAN.md`. Two provenance-tagged
  detector routes (DCS corpus `build_dcs_renou.py` + `<ls>` citation
  `renou_register.py`) plus a dedicated `épig` detector; wired end-to-end through
  `renou_audit.py` (register mode) and `renou_portrait.py`. The state axis is
  unchanged.

### Changed
- **Judge-model A/B settled — Sonnet bulk judge + Opus repass/audit.** Across
  ~650 judged cards a Sonnet QA judge is statistically indistinguishable from Opus
  (κ = 1.0 on real cards; both 99 % recall / 0 % FP on a 250-item ground-truth
  defect battery). Policy: Sonnet judges the bulk, Opus re-judges every reject + a
  ~5 % audited sample. New `src/judge_disagreements.py` / `src/judge_ab_score.py`.
  The synthetic semantic-defect test was dropped (a word-pair gloss is undecidable
  out of context). See `RussianTranslation/research/JUDGE_AB.md` / `JUDGE_POLICY.md`.

## [0.0.5] - 2026-06-25

### Added
- **`article-comparison/` — one headword across every CDSL dictionary.** A study
  comparing four "a-" headwords — `agni`, `anya` (non-samāsa) and `akṣara`,
  `ananta` (a-samāsa / nañ-privative) — each chosen as most-frequent in DCS 2026
  **and** present in the unfinished Deccan **PD** dictionary (PD's "a" stops at
  ~`apaca-`, the real constraint). Six views per word: `.table.md` (side-by-side
  all dicts, SLP1→IAST), `.pd-min.md` (PD `{@..@}` sense skeleton),
  `.pd-min.ru.md` (bilingual EN/RU), `.corpus-ru.md` (attested Russian from the
  DeepSeek word-alignment lexicon + published SamudraManthanam verse pairs),
  `.persense-ru.md` (each rendering hung under its PD sense, 88–99 % coverage),
  `.verbatim.md`/`.iast.md` (full). Builders in `RussianTranslation/src/`
  (`_build_corpus_ru.py`, `_build_skeletons_ru.py`, `_build_agni_ru.py`,
  `_build_persense_ru.py`). Audited; 2 per-sense assignment bugs fixed. Headline:
  the per-sense attested-RU split (`agni`→Агни/огонь, `akṣara`→слог/Непреходящее,
  `ananta`→бесконечный/Ананта).
- `RussianTranslation/src/run_batch.py review_csv` exports the existing
  `_review_queue.jsonl` human worklist to `_review_queue.csv` for spreadsheet
  review. The CSV keeps the severity-sorted machine evidence and adds blank
  `reviewer_id` / `decision` / `edit` / `notes` columns without advancing any
  review state.
- `RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md` and
  `RussianTranslation/src/gold_review_csv.py` define and export the human
  precision-review scaffold: 320 balanced `period × kind` rows, LLM labels kept
  separate from blank human-label/adjudication columns.
- `RussianTranslation/schemas/pwg_ru_lexicographic_portrait.schema.json` and
  `RussianTranslation/src/validate_portrait_schema.py` define a v1 Apresjan
  portrait contract and validate live `microstructure.portrait()` output.

## [0.0.4] - 2026-06-23

_(Backfilled 2026-06-25 — this release was tagged and published on GitHub but
not previously recorded here.)_

### Fixed
- **NWS attribution: the `av` `+ upa` owner slide root-caused & gated.**
  `compile_translatable.mask_nws_gloss` strips the leading owner *bleed* — a
  roman-numeral co-owner cite (`Rivelex (2) : XLV`) that `nws_split`'s digit-only
  OWNER can't tag was riding onto the next gloss's prose and misleading the LLM
  assembly. `nws_split` OWNER now stops at `;`; `check` uses word-boundary locator
  matching (kills the `apāṃ`-in-`apāṃpitta` false MISATTRIBUTION).

### Added
- **NWS attribution gate** (`run_real_test.py audit`): a fresh non-protected card
  whose NWS owners disagree with the deterministic `nws_split` parse is rejected
  (→ `<safe>.merged.REJECTED.md`, re-queued; run exits non-zero); protected
  hand-authored cards are audited but never quarantined.

## [0.0.3] - 2026-06-19

### Added
- `RussianTranslation/src/pilot/run_real_test.py` — driver for the real-conditions
  pilot test (run locally on the Max subscription, two phases, one command each):
  `prep [N] [OFFSET]` selects a coverage-first a-section batch, marks fresh vs
  protected (hand-authored `aMSa`/`anna`/`ap`) cards, and sets the workflow's
  `OFFSET`/`LIMIT`; `audit <wf_output.json>` renders via `_pilot_collect.py`,
  runs `nws_split.py check` per card, and reports judge pass rate +
  NWS-attribution (F12) clean count + misattributions.
- The audit phase was pre-flighted with a synthetic `ap` workflow output:
  collect → protected-card preservation → `nws_split.py check` → report. Result:
  publishable 1/1, NWS audit CLEAN 1, F12 misattribution 0.
- Materialized the human-review worklist with `run_batch.py review`: 217
  `legacy_needs_review` cards, severity-sorted, with no reviewer decisions
  advanced.

### Changed
- `RussianTranslation/src/pilot/run_pilot_wf.js` — the translate→judge workflow is
  now **manifest-driven** instead of a hardcoded 15-key list: it reads
  `scale_route.py`'s coverage-first `scale_manifest.<section>.json` and runs a
  `[OFFSET, OFFSET+LIMIT)` slice (editable consts), so the full a-section's 12,155
  inputs can be translated in successive batches. Falls back to the original 15-key
  pilot list if the manifest can't be read. Verified: a 30-card batch resolves
  30/30 inputs on disk via the shared `safeName()` stem.
- `run_pilot_wf.js` translator prompt — new **HARD RULE 5 (NWS layer format)**:
  render the NWS "Kleines Zitat" fragment as ONE entry per source, tagged `[NWS:]`,
  keeping each OWNER citation (`Author year : page`) verbatim as the last citation,
  never merging/compressing owners, never sliding the owner onto the next gloss
  (failure F12 reading-direction trap), sub-lemmas as first-class rows. Encodes the
  format the deterministic `nws_split.py` auditor requires — found while validating
  the loop manually on card `ap` (2026-06-19): the translation was sound but the
  first draft failed the audit purely on output format; the rule makes future cards
  audit-ready (re-checked: `nws_split.py check ap` → CLEAN, 0 misattributions).
- `_pilot_collect.py` now writes audited `<safe>.merged.md` files directly using
  the shared `safe_name()` encoder; `run_real_test.py` no longer uses the brittle
  external `<key>.md` → `<key>.merged.md` copy bridge.
- `run_real_test.py prep` was refreshed for the June-22 batch window
  (`OFFSET=0`, `LIMIT=10`): `as As Ap api amfta agni Atman anu arjuna arTa`,
  now correctly all fresh after exact-case output checks.

### Fixed
- Legacy `.merged.md` compatibility checks now require exact filenames, avoiding
  Windows case-insensitive false positives such as `Ap` being treated as protected
  because `ap.merged.md` exists.
- Generated the missing writable a-section input for `arI|a` (`|` escaped as
  `~007c`); pilot inputs now cover 12,156/12,156 a-section manifest cards.

## [0.0.2] - 2026-06-19

### Fixed
- **Case-collision in pilot input filenames (F10) — silently dropped 1,237 of
  12,156 a-section cards.** SLP1 headword keys are case-sensitive (`api`/`Api`/`ApI`,
  `as`/`As`/`aS`) but Windows filenames are not, so `_pilot_gen_merged.py` writing
  `<key>.raw.txt` made case-variants overwrite each other — including high-value
  heads (`api`, `arTa`, `As`, `aNga`), whose translation inputs held the wrong
  variant's content. Applied the NWS scraper's proven `safe_name()` (uppercase →
  `_`+lower, injective) across every reader/writer of these files
  (`_pilot_gen_merged.py`, the superseded `_pilot_gen.py`, `nws_split.py`, and the
  JS workflow `run_pilot_wf.js` with a matching `safeName()`); Python/JS encodings
  verified identical. The full a-section regenerated CLEAN (12,155 distinct files =
  12,155 by-key lookups, no collisions; 1 unwritable, `arI|a`, which contains a `|`).
  Also added per-card error-resilience so a single unwritable key no longer aborts
  an 11k-card run.

### Added
- `_pilot_gen_merged.py` now supports a manifest-driven scaled mode
  (`--manifest <section> --limit N`) driven by `scale_route.py`'s coverage-first
  order, used to generate the **full a-section** merged+NWS inputs (12,155 cards;
  PW 90 % / SCH 13 % / PWKVN 10 % / NWS-extra 35 %). `nws_split.py` (deterministic
  NWS "Kleines Zitat" splitter, F12 audit tool) is now tracked.

## [0.0.1] - 2026-06-18

### Added
- **NWS layer fully scraped, drift-validated, and folded into the merge spine.**
  `RussianTranslation/src/nws_scrape.py section all` captured all **167,990**
  headwords of the *Nachtragswörterbuch des Sanskrit* (Halle); `_nws_audit.py all`
  = CLEAN (0 missing / 0 case-collisions / 0 dups / 0 refusals), net-new
  `has_nws_extra` = 34,101 (20 %). `_nws_drift.py all` confirms the a-section's "LOW
  staleness" finding across the whole dictionary (Schmidt 96.7 % identical, mean
  Jaccard 0.987; pw 80.9 % overlap, only 0.1 % NWS-only). `dict_merge.merged()` now
  appends NWS as a 5th "external" layer — net-new only, per-key on demand, kept out
  of `LAYERS` since it adds no new headwords. (NWS scraped data stays gitignored and
  provisional pending a formal Halle data request.)
- **Merged+NWS pilot scaled from 6 hardcoded keys to a manifest-driven run.**
  `_pilot_gen_merged.py --manifest <section> --limit N` consumes `scale_route.py`'s
  coverage-first manifest to generate full layered inputs (PWG+PW+SCH+PWKVN+NWS) at
  volume, resumable. On the top-300 dense a-section heads, NWS-extra coverage reaches
  95 % (vs 20 % dict-wide). `RussianTranslation/DICTIONARY_CHAIN.md` updated with the
  all-sections scrape/drift/fold status.

### Fixed
- `_pilot_gen_merged.py` resumable skip now verifies a pre-existing `<key>.raw.txt`
  is actually in merged (`=== LAYER:`) format. The superseded PWG-only `_pilot_gen.py`
  writes the same filenames in `=== RECORD` format; trusting mere file existence
  silently skipped ~17 of the top-300 cards (e.g. `api`, `Atman`), leaving them
  un-merged. Now those stale files are regenerated.

## [1.1.3] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — `tune` now draws a reproducible
  random sample (same fixed seed as `coverage`) instead of the first N keys, so
  mid-size runs are representative. A random 4000-sample matches the full-PWG
  agreement shape (head-term Jaccard ≥0.5 ≈3.6% vs the full 3.7%); `n ≥ total`
  still reports the full run (106,085 headwords, 2,585 ≥2-dict pairs). Completes
  the random-sampling fix begun for `coverage` in 1.1.2.

## [1.1.2] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — `coverage` now draws a **random**
  sample (fixed seed, reproducible) instead of the first N keys. PWG headwords are
  SLP1-sorted and the `a-` section is over-covered (especially KOW), so first-N
  coverage badly overstated true numbers (3000-sample KOW was 39.8% vs the full
  8.0%). The corpus signal also gets its own random sub-sample. A random
  3000-sample now matches the full run (independent correctness 16.6% vs 16.4%,
  KOW 7.0% vs 8.0%, corpus ~15%). Full-PWG coverage of 106,085 headwords:
  independent correctness ≈16%, KOW reference ≈8%, corpus ≈15%.

## [1.1.1] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — the stage-4 corpus query returned 0
  aligned verses for common headwords (agni, rāma, kṛṣṇa, deva). `corpus_lines`
  (FTS) also holds dictionary rows (no `#sa`/`#ru` suffix); the query did
  `MATCH ? LIMIT 400` with no `#sa` filter in SQL, so for high-frequency words the
  first 400 matches were all dictionary rows and the Python `#sa` filter discarded
  every one. Pushed the `#sa` filter into SQL so `LIMIT` captures Sanskrit verse
  lines. Found while validating the gate end-to-end (lookup/card/coverage/tune all
  run; 5 dictionaries = 57,640 entries; coverage on a 3000-key sample: independent
  correctness 20.4%, KOW reference 39.8%, corpus 20.7%).

## [1.1.0] - 2026-06-14

### Added
- `RussianTranslation/pwg_ru.md` + `RussianTranslation/pwg_ru_prompts/` — scaffold
  for the **planned** Russian translation of the German Petersburg dictionary
  (PWG, Böhtlingk–Roth), mirroring the `mw_ru` kit. Editor-facing doc
  (`pwg_ru.md`: a card-format guide for a German source — the `{%…%}`
  German-gloss vs. Latin rule, the placeholder scheme, the `mw_ru`-seed
  mechanism) plus five stage prompts: `1_perevod.txt` (German→Russian translate
  with a 179+80-pair DE→RU glossary), the two QA judges
  (`2_qa_sudya_opus.txt`, `2_qa_sudya_yandexgpt.txt`),
  `3_pereperevod_opus.txt` (re-translate rejects), and a new
  `4_korpus_proverka.txt` — a non-blocking, two-signal Sanskrit→Russian corpus
  gate (independent-correctness + KOW reference-agreement). The translation
  pipeline itself is framed as planned/not-yet-run.
- `RussianTranslation/src/` — the stage-4 corpus-gate layer (code only; the
  `*.jsonl` dictionary data is gitignored, regenerated by `build_src.py`):
  `build_src.py` extracts five SLP1-keyed Sanskrit→Russian dictionaries from the
  sibling SamudraManthanam corpus (Kochergina 29,177; Kossovich/KOW 13,488;
  Knauer 3,271; Frisch/FRI 8,156; Smirnov 3,548 — ≈57,640 entries); `corpus_gate.py`
  joins a PWG headword to those dictionaries (+ optional SamudraManthanam parallel
  corpus) and emits the `4_korpus_proverka.txt` input, with coverage/tune modes.
- `RussianTranslation/SAMUDRA_INTEGRATION.md` — roadmap for how the sibling
  SamudraManthanam parallel-corpus tool feeds the Russian-translation projects
  (`pwg_ru`, `mw_ru`) and the WhitneyRoots crosswalk; separates built from
  planned, with verified extraction counts only.

### Notes
- The PWG corpus-check gate (stage 4) is designed as a **non-blocking annotator**
  emitting two separate signals per card: (1) *correctness* against independently
  compiled Sanskrit→Russian dictionaries (Kochergina, FRI, KNA), and
  (2) *reference-agreement* against KOW — itself a partial human PWG→Russian
  translation (Wilson-derived), so used only as a secondary, non-decisive
  reference, never to decide correctness. SKD/VCP are Sanskrit→Sanskrit and serve
  as Sanskrit-side sense corroboration only, never as a Russian authority. The
  five correctness/reference dictionaries are now extracted into
  `RussianTranslation/src/` from SamudraManthanam (≈57,640 SLP1-keyed entries);
  coverage is measured at ingest, not a blocker.

## [1.0.2] - 2026-06-14

### Added
- `HeadwordLists/README.md` — index of the headword exports: SLP1/Velthuis
  encoding, the `{DICT}-unique-{key1|key2}-{N}` naming (with the `wc -l` = N−1
  trailing-newline caveat), variant patterns (`fehlerhaft` = full XML records,
  `accents-IAST`, count-prefix, the HK aggregate, the 41 MB `sanhw1.xlsx`),
  key1/key2 semantics, the two-MW-key2 version note, the BOM-inconsistency
  caveat, and a 16-code dictionary table cross-checked against the CDSL site
  (resolves PD = Encyclopedic Dictionary on Historical Principles, CCS =
  Cappeller Sanskrit→German).
- `REFERENCES.md` — provenance (source, date, producer, size) for the root
  reference assets (`CDSL-2025.pdf`, the two DCS HTML exports,
  `helpmorphids.html`, `gasuns_cologne-zograf_2019.pdf`, and the previously
  unlisted `WSC 2025 Reviews 7.pdf`, since renamed `WSC2025_Reviews_7.pdf`),
  read from each file's own metadata with
  inferred descriptions flagged; linked from the README Contents table.
- `README.md` — new "Documentation map" section grouping every doc by purpose
  (Orientation; Contributors & agents; Material by area) with a one-line hook
  and link each, so a newcomer can find the right entry point.

### Changed
- `CONTRIBUTING.md` — expanded from the 3-step stub: formalised the data-change
  provenance expectation (source + transformation + counts/checksums) that
  previously lived only in README prose, plus filename-count and BOM conventions,
  a Documentation-changes section, and a Hygiene section.

## [1.0.1] - 2026-06-14

### Added
- `CLAUDE.md` — repository-level guidance for Claude Code. Documents what is
  specific to this data/research workspace (no source code): `HeadwordLists/`
  naming and key1/key2 semantics, the inconsistent UTF-8 BOM state across
  exports, the `mw_ru` translation format invariant, and the lint-only
  CI/pre-commit expectations. Ecosystem/workflow/taxonomy conventions are
  deferred to the org-level `../CLAUDE.md`.
- `Syntax-Lectures/sanskrit_particles_explorer.html` — a self-contained,
  Russian-language interactive explorer that digests the particle lectures for
  students: a clickable positional map (Zaliznyak / Wackernagel) over 16
  particles, with per-particle function, examples (deep-linked to the Gītā/Manu
  parallel corpus, Whitney, Speyer, Archive.org and DCS), Gonda/König/Hock
  citations, the full bibliography, and the folded-in Apte (1957) dictionary
  entries for the seven particles that have them. Built from
  `sanskrit_particles_lectures.md`, `sanskrit_particles_schema.html`, and the
  `Apte_1957-*_RU.md` series.
- `Syntax-Lectures/README.md` — Russian index of the particle materials: a
  start-here pointer to the lectures conspect, a table of the three primary
  files (lectures, the Zaliznyak positional schema, the interactive explorer),
  and a mapping of the seven `Apte_1957-*_RU.md` particle entries (those of the
  16 explorer particles that have an Apte article).
- `RussianTranslation/mw_ru.md` — new section 7 "Внешние документы", an
  appendix tabling the six files referenced from the mw_ru docs that live in
  the separate working repo (`kosha_ai_translation.md`, `improvements.md`,
  `yandex_api.md`, the two glossary JSONs, the QA scripts): what each is and
  where it is cited.

### Fixed
- mw_ru docs: demoted four dead links pointing at external working-repo files
  to plain text (`improvements.md` and `docs/yandex_api.md` in `qa_judge_v4.md`;
  two glossary JSONs in `mw_ru.md`), so all relative links in
  `RussianTranslation/` now resolve. Added `qa_judge_v4.md` to the prompts
  `README.md` index, marked as a proposed v4 update to the stage-2 judge.

## [1.0.0] - 2026-06-13

### Added
- Added this changelog so repository-level changes have a stable home.
- Recorded the current repository purpose: Research and data workspace for Sanskrit digital lexicography, with a focus on Cologne Digital Sanskrit Lexicon headword lists, cross-dictionary comparison, and teaching materials for Sanskrit lexical and syntactic study.

### Recent Git History
- 2026-06-12 Add 12-month research roadmap: csl-atlas DH review, paper pipeline P1-P6, book plan
- 2026-05-29 ai-wip: add .pre-commit-config.yaml (yaml-only)
- 2026-05-29 ai-wip: add .github/dependabot.yml for GitHub Actions auto-updates
- 2026-05-29 ai-wip: add CODE_OF_CONDUCT.md (Contributor Covenant 2.1)
- 2026-05-29 ai-wip: add CI workflow (generic-text)
