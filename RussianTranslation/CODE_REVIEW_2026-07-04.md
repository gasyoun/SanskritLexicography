# Code review — pwg_ru pipeline (2026-07-04)

_Created: 04-07-2026 · Last updated: 07-07-2026_

Full-tree review of `RussianTranslation/src` (34,668 LOC, ~90 Python files) by
five parallel reviewers (Opus 4.8, `claude-opus-4-8`), each scoped to one
subsystem, cross-checked and deduplicated. Findings are ranked by severity.
`CONFIRMED` = traced in code / reproduced; `SUSPECTED` = strong but not executed
to failure.

**Fixed in this pass** (branch `fix/review-2026-07-04-dataloss-latinmask`): the
🔴 data-loss trio + the 🟠 Latin-mask quality bug. Everything else is a
prioritized backlog below, to be worked before/alongside the next scale run.

---

## ✅ Fixed in this PR

| # | File | Defect | Fix |
|---|---|---|---|
| F1 | [promote_en.py:299](src/promote_en.py) | Non-atomic `open('w')` truncate-write of the whole tri-lingual store; a crash mid-write with `--no-backup` = total loss (the "EN layer wiped" scar). | Stream to `.tmp` + `os.replace` (atomic). |
| F2 | [promote_final_cards.py:324](src/promote_final_cards.py) | Same non-atomic truncate-write on the RU→store bridge. | `.tmp` + `os.replace`. |
| F3 | [run_batch.py:152](src/run_batch.py) | `cmd_collect` called `.get()` on a possibly-JSON-string `result`, crashing and stranding the run's generation output (the "run lost / re-driven" class); sibling loaders all handle the string case. | Normalise `result` (str→`json.loads`, non-dict→raw); also single-parse the batch file and coalesce per-row appends into one write to shrink the torn-last-line window. |
| F4 | [pwg_mask.py:98](src/pwg_mask.py) | `classify_pct` looked for the Latin cue (`<ab>lat.</ab>`) in the already-masked body, so it saw `{Tn}` not `lat.` → **33 Latin/Greek cognate glosses across PWG** (e.g. `ignis`, `uncus`, `ansa`) were leaked into the translator prompt as German. | Expand trailing `{Tn}` placeholders + strip tags in the classify context. Round-trip stays lossless. Pinned by `window_selftest.test_pwg_mask_latin_cue_behind_ab_tag`; SHARED parity entry `latin_cue_masking`. |

**Fixed in H169** (branch `fix/qa-gate-teeth`): the two 🟠 QA-gate-teeth
defects below (real `DUP` hard flag + RU-gate verdict-parse guard).

| # | File | Defect | Fix |
|---|---|---|---|
| F5 | [audit_window_en.py:252](src/pilot/audit_window_en.py) | Advertised HARD `DUP` gate never emitted — two senses with identical english passed `--strict`; the only signal was soft SAME-GLOSS, gated on `>=3` content words. | Emit a real `DUP` hard flag on any identical-english pair within a record, independent of word count; added to `HARD`. Pinned by `window_selftest.test_en_gate_dup_has_teeth`; SHARED parity entry `en_dup_hard_gate_20260704`. |
| F6 | [audit_window.py:71](src/pilot/audit_window.py) | RU gate recovered child-auditor verdicts by regex-scraping prose stdout (`\| flagged: ...`) — any wording drift in `audit_translation.py` / `audit_coverage.py` / `audit_sense_dupes.py` silently returned `[]`, dropping flagged cards from the requeue with the gate reporting clean. | Child auditors now also emit a strict machine-readable `FLAGGED_JSON: [...]` line; the parent parses it strictly and treats a missing/malformed line as unparseable — requeueing every card in the window and marking the gate crashed rather than silently passing. Dead `parse_nws` removed. Pinned by `window_selftest.test_ru_gate_fails_loud_on_unparseable_child`. |

---

## ✅ Resolved in H321 (2026-07-07, Opus 4.8 `claude-opus-4-8`, [PR to master](https://github.com/gasyoun/SanskritLexicography/pulls))

The [H321 handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H321-Opus_RussianTranslation_pwg-ru-correctness-backlog_07.07.26.md) worked the open 🔴/🟡 items below. Several were already closed by intervening PRs (verified against current `master`); the rest were fixed or measured this pass. Each fix lands behind a `window_selftest.py` pin + a [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) ledger entry.

| Item | Disposition |
|---|---|
| 🔴 Positional card misassignment (`resolveGroup`/`healGroup`) | **Already fixed** — `resolveGroup` matches on `byKey1(res.cards)` only (`missing-or-mismatched-key` on miss, never positional); `healGroup`'s `exactCard` positional fallback requires the candidate to echo the exact key. Pinned by `test_generated_harness_strict_key_matching` (present on `master`). Verified, no change needed. |
| 🔴 `tm_card_sane` zero-`<ls>` bypass | **Already fixed** in [PR #175](https://github.com/gasyoun/SanskritLexicography/pull/175) — the guard now compares `<ls>`/`{#` against the source count unconditionally (no `if ls and …`). Pinned by `test_tm_card_sane_rejects_zero_marker_drift`. Verified. |
| 🟡 Whole card dropped on one blank sense (`translation_memory.py:265`) | **Deliberate NO-CHANGE (measured):** 0/2313 sub-cards in the live 11,261-row store carry a blank non-partial sense — zero incidence. Caching a blank-sense card is also unsafe: `tm_card_sane` refuses it at serve, so it would churn or force serving incomplete output. Kept as-is; a code comment now records this. |
| 🟡 Partial card content-addressed as exact hit (`:1204`) | **Already fixed** — `reconstruct_cards` excludes `partial_card`/`missing_fragments`/`missing_groups` from the exact TM (pinned by `translation_memory.selftest` `skipped['partial-card']`). Verified. |
| 🟡 `frag_prov` first-seen, no fidelity (`:481`) | **Fixed (H321)** — `frag_senses_sane` gates harvest AND serve; a corrupt/blanked `wf_output` is refused, and a later good harvest overrides a previously-cached corrupt row. Pinned by `test_frag_tm_fidelity_gate_and_override`; ledger `frag_tm_fidelity_gate_h321`. |
| 🟡 `ls_resolver` RV/AV substring + bare `except: pass` | **Fixed (H321)** — anchored `_is_rv_prefix` (startswith), and both swallowed excepts surface via `_warn_swallowed`. Pinned by `test_ls_resolver_rv_av_anchored`; ledger `ls_resolver_rv_av_anchor_h321`. |
| FL7 corpus-gate silent evidence degradation | **Fixed (H321)** — `build_card` marks `evidence_status` (`evidence_unavailable`) + `corpus_status` (`db_absent`/`db_error`/`skipped_short_term`/`ok`). Pinned by `test_corpus_gate_evidence_and_db_markers`; ledger `corpus_gate_evidence_markers_fl7_h321` (INTENTIONAL-DIVERGENCE, RU-only gate). |

Not in H321 scope (still open): the 🟠 broken-validator items, `supersedes` string-iteration (latent), `degenerate_passthrough` German-in-RU, and the 🟡 data-builder items below.

## 🔴 Backlog — correctness (wrong output under a headword)

- ✅ **Positional card misassignment** — see the H321 table above (already fixed; verified). ~~[gen_opt_harness2.py:1259](src/pilot/gen_opt_harness2.py) (`resolveGroup`) and `healGroup` :1098. When the model drops/reorders a card, the `res.cards[i]` positional fallback assigns content to the wrong `key`.~~
- ✅ **`tm_card_sane` zero-`<ls>` guard bypass** — see the H321 table above (fixed in PR #175). ~~[gen_opt_harness2.py:585](src/pilot/gen_opt_harness2.py).~~

## 🟠 Backlog — broken validators (green light on defective output)

- **`--min-cards` mode skips the count-integrity check** — [validate_assembled_export.py:163](src/validate_assembled_export.py). Bounded runs can't catch dropped/duplicated cards (only a `>=` floor). *Fix: still assert exact count when known.*
- **`reverse_index --show` entirely dead** — [reverse_index.py:155](src/reverse_index.py). A 4-vs-8 column guard is never true → `_representative` always `(None, None)`. *Fix: index the correct column (`parts[4]`).*

## 🟡 Backlog — TM reuse & quality

- ✅ **Whole card dropped from cache on one empty sense** — [translation_memory.py:265](src/pilot/translation_memory.py). H321: deliberate NO-CHANGE (0/2313 incidence measured; unsafe — see the H321 table above).
- ✅ **Partial/incomplete card content-addressed as an exact hit** — already fixed: `reconstruct_cards` excludes `partial:true`/`missing_*` (see the H321 table above).
- **`supersedes` string→char-iteration** — [translation_memory.py:190](src/pilot/translation_memory.py). Iterates a string SHA character-by-character, defeating supersession. **Latent** (0 store rows carry a string `supersedes` today — verified), but the TM is now a published schema; *coerce to list defensively.* (Still open — not in H321 scope.)
- ✅ **`frag_prov` senses harvested with no fidelity check, first-seen-wins** — [translation_memory.py:481](src/pilot/translation_memory.py). H321: fixed (`frag_senses_sane` at harvest+serve, later-good override) — see the H321 table above.
- **`degenerate_passthrough` can emit German as the Russian field** — [gen_opt_harness2.py:519](src/pilot/gen_opt_harness2.py). A borderline stub bypasses the LLM with German copied into the RU field, no downstream gate. *Fix: tighten the allowlist / gate passthrough rows.*

## 🟡 Backlog — data builders (correctness)

- **Cross-builder Unicode key mismatch** — `build_dcs_freq*` (`norm_lemma`, no NFC) vs `build_corpus_lexicon` (`form_key`) vs `build_dcs_renou` (raw CoNLL-U lemma). Three "co-keyed" tables normalized three ways → the same lemma counts as two. *Fix: one shared normalizer + NFC pass.*
- **Silent lemma loss on genre join-key miss** — [build_dcs_freq_dims.py:133](src/build_dcs_freq_dims.py). A text whose name doesn't normalize-match gets zero genre attribution, indistinguishable from the intended register-less tail. *Fix: log unmatched `text_id`s.*
- **Homograph Ru-gloss attribution is winner-take-all + nondeterministic tie order** — [build_rollup_glossaries.py:60](src/build_rollup_glossaries.py) `most_common` sorts by count only; equal-count lemmas ordered by file order. *Fix: stable tiebreak; split near-tied distributions.*
- **Citation index dedup semantics disagree across two code paths** — [build_citation_index.py:136](src/build_citation_index.py) vs `occurrence_stats()`; `CITATION_SOURCES.md` and `UNCOVERED_SOURCES.md` can disagree on coverage. *Fix: single source of truth for coverage.*
- ✅ **`ls_resolver` Ṛgveda/Atharva disambiguation is substring-based** — [ls_resolver.py](src/ls_resolver.py). H321: fixed (anchored `_is_rv_prefix`; bare excepts now surface via `_warn_swallowed`) — see the H321 table above.

## ⚡ Backlog — performance

- **Biggest win: three full DCS-token-table scans** — `build_dcs_freq` (general) + `build_dcs_freq_dims` (POS + genre). Collapse to one indexed pass; verify indices on `token.lemma_id`, `token.sentence_id`, `sentence.chapter_id`.
- **Source read + masked up to 3× per card** — [gen_opt_harness2.py:662/757/764](src/pilot/gen_opt_harness2.py). Cache the masked skeleton per key.
- **`build_corpus_lexicon buildall` re-scans the full 1.09M-row lexicon per text** — [build_corpus_lexicon.py:188](src/build_corpus_lexicon.py). Build the resume set once.
- **`assemble build` rebuilds whole-corpus caches every invocation** — [assemble.py:47](src/assemble.py); `--offset` with no N silently overwrites the whole export ([:296](src/assemble.py)); two-file publish not atomic ([:336](src/assemble.py)).

## 🟢 Backlog — linguistic edge cases (lower frequency)

- `compile_translatable.py` `REF` regex over-masks German like "Buch V, Kapitel" ([:111](src/compile_translatable.py)); `IAST_ONLY` can drop a German gloss containing one diacritic ([:104](src/compile_translatable.py)).
- `corpus_gate.py` `_RU_END` lists `ого` twice and strips only one suffix ([:270](src/corpus_gate.py)); FTS `LIMIT 400` prefilter can under-report high-frequency coverage ([:249](src/corpus_gate.py)).
- `microstructure.py` module-load `json.load(open(...))` raises at import if `ls_source_map.json` absent, taking down every importer ([:27](src/microstructure.py)); `MARK` regex can mis-split `a) … b)` German enumerations ([:40](src/microstructure.py)).
- `pwg_mask.py` unclosed `<ls>` greedy `.*?` can span records ([:33](src/pwg_mask.py)); `records()` drops the first record if the file ever carries a BOM ([:45](src/pwg_mask.py)).
- `nominal_grammar.py` `_stem_class` on raw (non-`form_key`) k1 misclassifies anusvāra/visarga/punctuated finals ([:225](src/nominal_grammar.py)).

## Notes cleared (checked, NOT bugs)

- Content-addressing (`lang:raw_sha256`) genuinely prevents stale reuse on source change.
- The `parallel`/backfill invariant in the harness guards the whole-batch null-vanish loss the project's memory warns about.
- `form_key` (corpus_gate) is correctly length-preserving (NFC + strip U+0300–036F only) — no NFD vowel-length/retroflex-dot loss.
- The `devanagari_to_slp1` ळ→x gotcha does **not** touch these files (only `build_kosha`/`build_meulenbeld`/`build_indic`).

_Dr. Mārcis Gasūns_
