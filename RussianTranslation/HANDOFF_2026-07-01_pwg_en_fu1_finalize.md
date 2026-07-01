# Handoff — finalize PWG→English FU1 (giant-heads → hard-flags → dashboard → Phase 2)

**For:** a fresh chat with Max/Workflow access.
**Branch:** `feat/pwg-en-fu1-phase0` (off `master`). `git checkout` it and confirm
`git rev-parse --abbrev-ref HEAD` ≠ `master` before any commit. A second (autonomous) account
also commits in this repo — announce, **prefer PR-only**, don't double-run a root.
**Model discipline (report tier + version at every step):** generation = **Sonnet 5
(`claude-sonnet-5`)**; judge (Phase 2) = **Opus 4.8 (`claude-opus-4-8`)**. The bare `model:'sonnet'`
alias resolved to Sonnet 4.6 on an earlier run — the EN harness now pins `claude-sonnet-5`
explicitly (probe-confirmed this environment routes that id → Sonnet 5).

## Status as of 2026-07-01 (what's DONE)

FU1 **translation is complete: 1,432 / 1,509 cards = 94.9%** across all 30 worklist roots
(three passes: first pass → small-batch requeue → EN-schema-relaxation requeue). **12 roots at
100%:** nI yA dA vas hA mA muc su siD paS laB As. Store = per-root
`RussianTranslation/wf_output.en.<root>.json` (⚠️ **`dA` is saved as
[`wf_output.en.d_a.json`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/) —
Windows case-collision with the pilot `DA` root; `promote_en` globs `wf_output.en.*.json` and
joins on German text, so the filename is fine). Outputs are **gitignored**; commit only code/docs.

Committed to the branch this session (code only):
[`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/gen_opt_harness2.py)
(EN meta language-aware + Sonnet-5 pin + **LF harness write**; EN per-sense schema relaxed) and
[`save_and_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/save_and_audit.py)
(drops null result-slots from failed batch thunks). Commits `949a473`, `88cc933`.

### ⚠️ Systemic finding (do not relearn)
Sonnet 5 hits the **StructuredOutput retry-cap (5)** on the citation-dense, HTML-entity-heavy
**main-head `pwg00` cards even solo**. The EN-schema relaxation (per-sense `required` trimmed to
`[tag, german, english]`; the 4 annotator fields optional — EN path only, RU keeps all 7) lifted
coverage 92.7%→94.9% and recovered many medium-dense cards, but the **truly-giant root-article
heads are output-size-bound, not validation-bound** — they will NOT yield to more re-runs. Some
residual is **fidelity-guard nulls** (restored `{Tn}` `<ls>`/`{#..#}` counts mismatch → the
`accept()` guard rejects rather than emit garbled markup).

### Residual (77 cards) and hard flags
- **Per-root residual** (partial roots): gam −23, viS −5, jan −5, Sru −5, vac −5, han −4, vah −4,
  iz −4, brU −4, banD −3, ji −3, jIv −3, jYA −2, diS −2, man −2, car −1, vA −1, Ap −1.
- **Hard flags: 8 on 4 cards.** AB-LOSS (dropped `<ab>` count): `ban_d~~h0_21_upasam_0` (s3, 4/6),
  `gam~~h0_24__a_1` (caus-4, 2/4), `jan~~h0_03_a_di` (s1, 12/14), `la_b~~h0_01_sec_1` (s1, 4/6).
  SENSE-DUPE (cross-part over-production) roots: **siD** (KNOWN/EXPECTED RU-h1 defect — the FU1
  plan predicted it; NOT a regression), **vac**, **su**, **laB**.

## DO THESE IN ORDER — do NOT start Phase 2 until 1–3 are done (MG-locked 2026-07-01)

### 1. Giant-head recovery (head-splitter → toward ~100%)
The infrastructure exists in
[`src/_pilot_gen_merged.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/_pilot_gen_merged.py):
`--root-split`, `HEAD_CIT_BUDGET` (default 18 `<ls>`/head-sense-part), `_citation_batches()`,
`batch_of`. The giant heads that still cap are single sub-cards whose ONE head sense is too large
to emit as valid JSON. Split those head senses more finely (lower `HEAD_CIT_BUDGET`, e.g. 8–10, or
force citation-batching on the failing keys), **regenerate only the failing keys**, then requeue
EN with the relaxed schema at `--budget=6000`.
```sh
git rev-parse --abbrev-ref HEAD                          # feat/pwg-en-fu1-phase0, NOT master
# recompute residual keys per root from the store (rootmap selected_keys − non-null keys)
# for the giant-head roots (start with gam), regenerate finer head-split sub-cards:
HEAD_CIT_BUDGET=8 python src/_pilot_gen_merged.py --root-split gam   # then viS, jan, Sru, ...
python src/pilot/gen_opt_harness2.py gam --lang=en --keys=<missing> --budget=6000 --out=src/pilot/run_pilot_wf.en_gam_rq3.js
# run via in-chat Workflow tool, ≤3-wide; then:
python save_and_audit.py gam <task-output-file> en --merge
```
Gotchas: harness gen needs **`--lang=en`** (with `=`; the space form silently falls back to RU).
Build `--keys` with **`tr -d '\r'`** (the missing-key files were written with CRLF — a trailing
`\r` makes `gen_opt_harness2 --keys` match only the last key). Verify each harness: `grep -c
'"english"'`=1, `'"russian"'`=0, `node --check` passes, 0 `\r` bytes (the generator now writes LF).

### 2. Hard-flag remediation (4 cards)
- **AB-LOSS ×4** (`banD upasam_0`, `gam __a_1`, `jan a_di`, `laB sec_1`): the English dropped an
  `<ab>…</ab>` the German had. Re-translate just those cards (relaxed schema) and re-check; if it
  persists, hand-patch the missing `<ab>` sigla into the `english` field (they are verbatim tokens).
- **SENSE-DUPE** on **vac, su, laB** (and **siD = expected**, leave as documented known-issue):
  cross-part sense over-production — same class as the RU `jan`/`siD` defect. Fix with a rootmap
  `batch_of` exemption (see
  [`src/pilot/rootmap_overrides.json`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/rootmap_overrides.json)
  and `audit_sense_dupes.py`) OR document as known-issue if the duplication is faithful to PWG.
- Gate to clear: `python save_and_audit.py <root> <out> en` (or
  [`src/pilot/audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/audit_window_en.py))
  → **0 hard flags** (siD's expected SENSE-DUPE excepted).

### 3. Dashboard — wire the EN audit into :8765
[`src/pilot/dashboard_server.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/dashboard_server.py)
(running on `http://127.0.0.1:8765/`) reads the RU-pipeline artifacts
(`window_status.json`, `window_ledger.jsonl`, RU `audit_window.report.json`, G5–G10 gates) and so
shows **stale RU state, not the EN run**. Make the EN gate emit `dashboard_events.jsonl` +
`window_status.json` (the RU `audit_window.py` already does; `audit_window_en.py` is report-only)
so the dashboard reflects FU1-EN per-root coverage/flags. Reuse `dashboard_events.read_events` /
`window_common` writers.

### 4. THEN Phase 2 (validation) — only after 1–3
Per the runbook
[`HANDOFF_2026-06-30_pwg_en_fu1_run.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/HANDOFF_2026-06-30_pwg_en_fu1_run.md)
§Phase 2 and the locked plan
[`FU1_PLAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/FU1_PLAN.md):
```sh
python src/promote_en.py            # attach en + en_provenance onto the RU store rows (join on German)
python src/annotate_dcs_freq.py     # re-attach dcs_freq (idempotent)
# Opus 4.8 judge (Phase-0 tools): fidelity_sample_en.py -> gen_fidelity_judge_en.py -> Workflow -> fidelity_aggregate.py --sample ...
# human gold: gold_sample_en.py -> gold_packet.py -> 2 annotators -> gold_agreement.py (Cohen kappa + error rate)
```
Ground truth = **faithful to the PWG German** (MW = cross-check only). `review_status` stays
`ai_translated` (G5); only human sign-off flips rows to `approved` for `export_interop.py`.

## Guardrails / gotchas (learned this run)
- **≤3-wide Workflow concurrency** (roots, not intra-root batches). Slice-D's 18× fan-out caused a
  null collapse.
- **csl-orig is READ-ONLY** (`pwg.txt`/`mw.txt`): extract, never modify/stage.
- Working dir resets between Bash calls on this host — **prefix every command with `cd`**.
- The Workflow-tool approval **rejects raw `\r`** in the script — harnesses must be LF (generator
  now does this; older `.js` need CRLF→LF normalization before launch).

## Pointers
- Journal: [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/.ai_state.md)
  (top Queue entry = FU1 result + this finding).
- EN harness gen: [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/gen_opt_harness2.py)
  (`--lang=en`) · prompt [`src/pilot/tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/tr_en.txt) ·
  save/audit [`save_and_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/save_and_audit.py) ·
  EN gate [`src/pilot/audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/audit_window_en.py) ·
  merge [`src/promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/promote_en.py).
- Schema: [`schemas/pwg_ru_final_card.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/schemas/pwg_ru_final_card.schema.json)
  (EN path relaxes per-sense `required` in-code, not in the file).
