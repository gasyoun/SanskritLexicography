_Created: 23-09-2026 · Last updated: 23-09-2026_

# H4527 repair run, 23-09-2026: `darv_i` re-made on Anthropic and promoted; `kast_ur_i` blocked by an audit-gate false positive

Run `h4527-repair-230923`, driven by `bounded_staged_run.py --repair-lease h4527vol14 --repair-lease h4527dr01 --execute --cohort-path --cohort-width 1 --only-profile c1 --max-calls 4`. It ran on MSI from the human's own PowerShell after the Mac session's permission classifier refused the paid call. Follows [H4527_REPAIR_DRIVER_SHIPPED_DRY_RUN_GREEN_C1_ZAI_AGAIN_22-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_REPAIR_DRIVER_SHIPPED_DRY_RUN_GREEN_C1_ZAI_AGAIN_22-09-2026.md) §4.

## 1. Route and canary (Mac session over ssh, 01:36–01:38Z)

1. Human ruling in chat: «restore Anthropic». `c1`'s `settings.json` still had `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic` (written 22-09 13:06:49Z). The same six keys as on 22-09 were removed: `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, three `ANTHROPIC_DEFAULT_*_MODEL`, `API_TIMEOUT_MS`. The z.ai file is kept as `settings.json.pre-h4527-restore-anthropic-23-09.bak`. Only key names were printed.
2. `probe-ration --account c1`: `attempts_today: []`, `legal_now: true`.
3. Canary `h4527-canary-230923` (1 paid call): `classification: success`, 14 203 ms. `canary_gate.py judge` → **CANARY GO**. Receipt: [canary_receipt.230923.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/canary_receipt.230923.json), sha256 `89056998cf1cd638e3161d22017664f426b4286035e4dde53ac51924a41a5ba4`.
4. Zero-call dry run: `scope.lease_ids = [h4527vol14, h4527dr01]`, `projected_calls_from_plan: 2`, `windows_not_prepared_skipped: []`.

## 2. First launch attempt: crashed before any call

`NotADirectoryError: [WinError 267]` from `mao.coordinator_command`: the `--cwd` folder `C:\Users\user\AppData\Local\Temp\pwg-bare-h4527rep` did not exist. The dry run never uses `--cwd`, so it passed. The empty folder was created, and no reservation, lease change or call happened. **Driver defect:** `bounded_staged_run.py` should refuse a missing `--cwd` during the dry run, not crash after preflight on `--execute`.

## 3. The paid run (01:48–01:50Z): 4 calls, the cap

| Item | Result |
|---|---|
| Reservation ledger | `calls_spent 4` of `max_calls 4`: 2 probe legs + 2 cards ([calls.repair.230923.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/calls.repair.230923.json), sha256 `fb602541e79699fd841b7b120876a654f7fcd85bdf92d9efbebbcd22788354df`) |
| Route proof | all 4 `c1` transcripts written 01:48–01:49Z carry `msg_011CfK…` / `req_011CfK…`, which is Anthropic's id format, not z.ai's `msg_2026…` |
| `h4527dr01` (`darv_i~~h0_zz_pw`, defect-repair, TM off) | audit **clean**: every gate PASS (final_schema, nws, translation 1/1, stage2, coverage 1/1, sense_dupes, sense_loss, ru_style). Lease `ready` → **promoted** 01:50:05Z. `BATCH PROMOTE: 1 subcard, 3 sense rows; store 11534 -> 11534`. The three GLM-made rows from 20-09 were replaced in place. The new rows' provenance: `root nominal_h4527dr01`, `model_version claude-sonnet-5`, `source_commit 646f69740` |
| `h4527vol14` (`kast_ur_i~~h0_zz_pw`, requeue `rq01-defect`) | audit **needs_requeue**: `prompt_semantic` exit 1, 2× `untranslated_braced_german_gloss`, the same gate as its first run on 22-09. Lease → `needs_requeue` |
| Driver report | [repair.report.230923.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/repair.report.230923.json), sha256 `128b350e4fa2b3279f27705b807d26a7cbb87b9f6e883f4ce8c8239ff0b3a0a3`, `peak_concurrency 1`, `effective_width 1`. That sha is of the MSI file (CRLF); the committed LF copy is `a90f6a3ba95f62c0e3a0f3f7a5304fd8304ff198d32153ad92166eb3850f0c25`. The other two files are byte-identical |

The collect step's pilot-judge row for `darv_i` shows `n`/`?` columns and "publishable 0/1". That table is the sampled judge summary, and no judge verdict was produced for it. It is not one of the audit gates listed above, which all passed.

## 4. `kast_ur_i`: the card is right, the gate is wrong

The two flagged risks are exactly:

- `German braced gloss appears untranslated: {<bot>Amaryllis zeylanica</bot>}`
- `German braced gloss appears untranslated: {<bot>Hibiscus abelmoschus</bot>}`

Senses 2 and 3 of `kast_ur_i` are Latin species names, and the Russian correctly keeps them verbatim: `*{%<bot>Hibiscus abelmoschus</bot>%}`. The detector misreads them because of the `<bot>` wrapper. Reproduced on `origin/master` `646f69740`:

| `value` | `looks_foreign_literal` | `looks_german_gloss` |
|---|---|---|
| `<bot>Hibiscus abelmoschus</bot>` | False | **True** |
| `Hibiscus abelmoschus` | True | False |
| `<bot>Amaryllis zeylanica</bot>` | False | **True** |
| `Amaryllis zeylanica` | True | False |

`LATIN_BINOMIAL.match(value)` is anchored at the start of the string, so a leading `<bot>` defeats it. The shared `pwg_mask.classify_pct_detail` classifier does not strip the tag either. **Retrying `kast_ur_i` fails every time, so it is not retried.** The fix belongs in [`prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py) `looks_foreign_literal`: strip markup, or treat `<bot>` as a Latin signal. It needs a selftest pin both ways and an independent logic critic, because it relaxes a publication gate. After the fix, the existing `rq01-defect` output is re-audited with 0 paid calls. This is H4527's next step.

## 5. State after the run

- `h4527dr01` promoted. `h4527vol14` `needs_requeue`. Store 11 534 rows.
- `c1` on Anthropic at 01:50Z. It was silently reverted once before, so re-probe before every paid window.
- The collect step printed three `pipeline drift` warnings: prompt, glossary and script shas moved without a `pipeline_versions.json` bump. They are pre-existing and not caused by this run. The rows carry the current shas in `provenance.pipeline`.

_Гасунс_
