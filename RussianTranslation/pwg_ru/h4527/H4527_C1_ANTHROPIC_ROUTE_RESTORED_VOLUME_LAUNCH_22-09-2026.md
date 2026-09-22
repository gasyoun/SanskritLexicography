_Created: 22-09-2026 · Last updated: 22-09-2026_

# H4527: `c1` is back on the Anthropic route, and the first five-card volume launch ran

**Handoff:** [H4527](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4527-Opus_RussianTranslation_pwg-ru-cohort-live-acceptance-width2_10.09.26.md)
**Executor:** Claude Code, Opus 5 (`claude-opus-5`), interactive `/go` on the Mac, driving MSI over tailnet ssh
**Rulings (human, in chat, 22-09-2026):** «restore Anthropic», then «yes, launch» for the paid launch below.

## Why this pass ran

The 21-09 pass left one question for a human: should `c1` stay on z.ai GLM 5.3 (quota exhausted until
24-09) or go back to Anthropic? The human chose Anthropic. The volume route chosen on 21-09 («1», volume
first) then ran on the five one-card leases that pass had prepared.

## What was done, in order

| # | Step | Paid calls | Result |
|---|---|---|---|
| 1 | Live read of `c1`'s `settings.json` (key names, URL, model names only) | 0 | unchanged since 2026-09-20T13:42:30Z, still `api.z.ai`, `glm-5.3[1m]` |
| 2 | Backup + removal of the six keys the z.ai switch added | 0 | see below |
| 3 | MSI shared checkout fast-forward | 0 | `7433c250f` → `77978400c`; the four daemon-owned `progress_dashboard/*.json` were already dirty and were left untouched |
| 4 | `coordinator.py status` | 0 | `h4527vol09/10/11/14/22` all `prepared` |
| 5 | Plan frozen: `output\no_pwg_scale_plan.json` (written 21-09 19:10:52Z) copied to `output\h4527vol\plan.json` | 0 | sha256 `b1c5b813af21d3ab45f0481168ba4074a8961b283306c7a17e101a71cb06850f`; exactly the five leases are `headless`, one projected call each |
| 6 | `max_account_orchestrator.py probe-ration --account c1` | 0 | exit 0, `attempts_today: []`, `legal_now: true` at 10:13:40Z |
| 7 | `canary_manifest_build.py --profile-slot c1 --outdir src\pilot\output\h4527vgate22` | 0 | manifest sha256 `c4908c9d46ea95c680cbe7e1880c7c192966623c02fe66e3cc66b9b97c467192` |
| 8 | `headless_worker.py` canary, run `h4527-canary-220922` | **1** | `classification: success`, 64 684 ms, `cli_safe_mode_effective: true` |
| 9 | `canary_gate.py judge` | 0 | **CANARY GO** → `src\pilot\output\h4527vgate22\canary_receipt.json` |
| 10 | `bounded_staged_run.py` dry run (no `--execute`) | 0 | exit 0, `live_admission.admitted: true (serial route, width 1)`, `allocated: ["c1"]`, `max_calls: 7`, `windows_not_prepared_skipped: []` |
| 11 | `bounded_staged_run.py --execute --cohort-path --cohort-width 1`, run `h4527-vol-220922` | **7** (2 probe legs + 5 cards) | **4 cards accepted and promoted, 1 needs requeue**; store 11 524 → 11 534; exit 1 by the H5209 contract (see below) |

### Step 2: the settings change

The z.ai switch had added six keys to the `env` block that the 30-07 backup
(`settings.json.pre-ssh-sync.bak`, env = `PYTHONUTF8`, `PYTHONIOENCODING`, `DEEPPAPERNOTE_OBSIDIAN_VAULT`)
does not have. A small Python script removed exactly these, kept every other key in order, and re-parsed
the file:

`ANTHROPIC_AUTH_TOKEN` · `ANTHROPIC_BASE_URL` · `ANTHROPIC_DEFAULT_HAIKU_MODEL` ·
`ANTHROPIC_DEFAULT_SONNET_MODEL` · `ANTHROPIC_DEFAULT_OPUS_MODEL` · `API_TIMEOUT_MS`

The token had to go too: with the base URL gone, a z.ai key left in `ANTHROPIC_AUTH_TOKEN` would have been
sent to Anthropic as the bearer. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `ENABLE_TOOL_SEARCH` and
`SHUNT_MIN_LINES` stay; none of them routes a call. The file went from 29 214 to 28 878 bytes, with no BOM,
LF and a 2-space indent both before and after. The untouched original sits beside it as
`settings.json.pre-h4527-restore-anthropic-22-09.bak` (byte-identical copy, verified), so going back to
z.ai is one copy. No token value was printed or read into this session.

### Step 8: proof that the canary went to Anthropic

The artifacts and the transcripts both say `claude-sonnet-5` on either route, because they echo the
requested name. The response **id format** tells the two apart:

| Transcript (`claude1\.claude\projects\`) | `message.model` | `message.id` | `requestId` | `service_tier` |
|---|---|---|---|---|
| 22-09 10:15:24Z, this canary | `claude-sonnet-5` | `msg_011CfJ…` | `req_011CfJ…` | `standard` |
| 20-09 17:59:59Z, the z.ai era | `claude-sonnet-5` | `msg_202609…` | none | `standard` |
| 19-09 08:04:17Z, before the switch | `<synthetic>` | uuid | `req_011CfC…` | — |

`msg_011C…` with a `req_011C…` request id is Anthropic's format. A timestamp-prefixed id with no request
id is not. That turns the 21-09 packet's «very likely» into evidence: **the 20-09 acceptance window ran on
z.ai GLM 5.3**, so the card it promoted (`darv_i~~h0_zz_pw`, run `h4527-acc-200920`) is in the store under
a `claude-sonnet-5` label it did not earn. This pass does not touch that card. Removing or re-making it is
a separate decision for a human.

### Step 11: why `--allow-unbounded` is on the command line

`bounded_staged_run.py --execute` refuses a paid run unless it has both `--max-calls` and `--cost-ceiling`,
or `--allow-unbounded` (H2157). On this route the cost is not evaluable (`cost_evaluable: false`), and a
`--cost-ceiling` fails closed on unevaluable cost, which would stop the run after the first card. So the
run is bounded by `--max-calls 7` (two readiness-probe legs plus five one-call cards), which is the same
pairing the 16-09 and 20-09 windows used. The auto-mode classifier refused the flag once; the launch ran
only after the human's «yes, launch».

The exact argv is kept on MSI as `src\pilot\output\h4527vol\argv.txt`, and the full stdout+stderr as
`src\pilot\output\h4527vol\execute.log`. That closes one of the two retention gaps the 21-09 Codex
review named.

## Results of run `h4527-vol-220922` (11:45:13Z → 11:50:10Z, about 5 minutes)

Both readiness-probe legs passed (warm-up 29 609 ms, measured 19 667 ms, `policy: production_v4`,
`cli_safe_mode_effective: true`). This was `c1`'s first probe attempt of the 22-09 UTC day, so one
attempt is left today. Then the cohort path dispatched the five leases one at a time
(`peak_concurrency 1`, `effective_width 1`):

| Lease | Card | Model call | Audit | Promoted rows |
|---|---|---|---|---|
| `h4527vol09` | `gl_ana~~h0_zz_pw` | success, 26 170 ms | clean | 2 |
| `h4527vol10` | `hasita~~h0_zz_pw` | success, 61 375 ms | clean | 2 |
| `h4527vol11` | `jaw_ayus~~h0_zz_pw` | success, 57 084 ms | clean | 3 |
| `h4527vol14` | `kast_ur_i~~h0_zz_pw` | success, 35 044 ms | **defect**: `untranslated_braced_german_gloss` ×2 | 0, left `needs_requeue` |
| `h4527vol22` | `ku_rqal_i~~h0_zz_pw` | success, 51 720 ms | clean | 3 |

One batch promote for the four clean leases: 4 subcards, 10 sense rows, **store 11 524 → 11 534**, prior
store backed up as `pwg_ru_translated.jsonl.premerge.20260922T115005.154431Z.p15804.37bcb90f6308.bak`,
`gen_model_version: claude-sonnet-5`, TM rebuilt (`wave.promoted` and `wave.tm_done` true).
`calls_spent 5 == calls_reserved 5` on the card ledger; with the two probe legs that is 7 paid calls,
exactly the `--max-calls 7` ceiling, plus the one canary call in step 8.

**All seven transcripts of the run carry Anthropic ids** (`msg_011CfJ…` and `req_011CfJ…` at 11:45:44,
11:46:03, 11:46:30, 11:47:34, 11:48:32, 11:49:09 and 11:50:02Z). So these four cards are Sonnet 5 output
and their `claude-sonnet-5` label is true.

### Exit 1 is correct this time

The process exited 1. This is **not** the FINDINGS §642 defect; H5209 has since given the cohort route
its own exit contract (`cohort_exit_code` in `bounded_staged_run.py`), and that contract returns 1 when
`requeue_backlog_keys` is non-empty. `kast_ur_i~~h0_zz_pw` is in it, so a caller gating on the exit code
correctly sees "not fully drained".

### The one defect card

`kast_ur_i` came back from the model on time, but the audit found two German glosses in braces left
untranslated. It is filed as a **defect**, not a transient (`requeue.defect.keys.txt`), and its lease is
`needs_requeue`. This pass did not requeue it: that would be a sixth card call outside the five-card launch
the human approved. It is the only open item from this launch.

### Retained artifacts (sha256)

The three run files are committed beside this packet: `volume.report.json`, `volume.events.jsonl`
(22 events: 2 `probe_call`, 5 each of `attempt_start`, `model_call`, `model_call_key`, `attempt_end`) and
`volume.checkpoint.json`. The card bodies stay on MSI in gitignored directories, recorded here by hash only,
which is the manifest route the 21-09 Codex review suggested:

```text
b931a1a223abfb47b6f9e9df4d3bebf8c634718e75cf6b11039d6ef011ff4fc4  src\pilot\output\h4527vol\argv.txt
1d77c70e8ce7bed5da2c576febf112784f88c6f1dd2e685dae8b6c04e12453e3  src\pilot\output\h4527vol\execute.log
ab9f0a6d9a10a168e2c5653cba4fa2adce046bb77ca68749eee2c19b22fd3810  src\pilot\output\h4527vgate22\canary_receipt.json
bcc83b2b5e9dcff03d65c8d6b3c77df1f75e9a595c4b5edd804adce314da3540  src\pilot\output\h4527vgate22\out.canary.json
278ba3ae9281b7a0f776b012d63883dae6aa774aee4a66004d79570dea9705a2  src\pilot\output\coordinator\artifacts\h4527vol09\wf_output.h4527vol09.json
09ca3db72508aeee190103a0c45ec3ebf038fa7afdde659c26408707a1b23a8d  src\pilot\output\coordinator\artifacts\h4527vol10\wf_output.h4527vol10.json
5bd3b21a2d8bfe5b1bd2deba111da93438088e72efdae7fe0b491a70bd32bb8c  src\pilot\output\coordinator\artifacts\h4527vol11\wf_output.h4527vol11.json
0d250235da2b95214c3ea994349f5f6103a7908ddfca9bec2ccf3221e7a16c7f  src\pilot\output\coordinator\artifacts\h4527vol14\wf_output.h4527vol14.json
546f2b9e701b17de4af343f427dc1d17544317f22dd80b68e601b84245ab9dca  src\pilot\output\coordinator\artifacts\h4527vol22\wf_output.h4527vol22.json
```

The executed argv, verbatim (run from `RussianTranslation\src\pilot` on MSI):

```text
python bounded_staged_run.py --plan output\h4527vol\plan.json --coord-dir output\coordinator --coordinator coordinator.py --cwd C:\Users\user\AppData\Local\Temp\pwg-bare-h4527vol --events ..\..\pwg_ru\h4527\volume.events.jsonl --lease-id h4527vol09 --lease-id h4527vol10 --lease-id h4527vol11 --lease-id h4527vol14 --lease-id h4527vol22 --execute --cohort-path --cohort-width 1 --only-profile c1 --canary-receipt output\h4527vgate22\canary_receipt.json --max-calls 7 --allow-unbounded --call-reservation output\h4527vol\calls.vol.json --run-id h4527-vol-220922 --checkpoint ..\..\pwg_ru\h4527\volume.checkpoint.json --report ..\..\pwg_ru\h4527\volume.report.json
```

### Side effects, and what was left alone

1. The four `progress_dashboard/*.json` files in the MSI checkout were already modified before this
   pass touched anything. They are daemon-owned and were left as found.
2. The run left an untracked `src\pilot\translation_memory.frag.ru.jsonl.lock`. It is the usual lock-file
   leftover of a TM rebuild; the run's own process had exited when it was seen.
3. The coordinator shows `h4527sen08` (`darv_i`, 20-09) as the only lease promoted during the z.ai
   window, so the wrongly labelled card is limited to that one, at least on the coordinator path.

## What remains on H4527

1. **`kast_ur_i` requeue**: approved by a human on 22-09 («yes»). The requeue is prepared (see the
   afternoon addendum below); the run waits on a driver change.
2. **The 20-09 `darv_i` card**: GLM-made under a Sonnet label. On 22-09 a human chose to re-make it on
   Anthropic in the same run as `kast_ur_i`. Same wait as item 1.
3. **Check D (`byte_identical_to_serial`)** stays unanswered, as the 21-09 ruling chose. It is also now moot
   for the 20-09 window, because that window ran on a different model than its record would claim.
   `COHORT_LIVE_ACCEPTANCE.json` stays unwritten, and width 2 stays fail-closed.
4. **The money-class `## Verifier` PASS**: owed by a different session.

## Afternoon addendum (22-09-2026, ~13:00–14:30Z, 0 paid calls): the redo is prepared, the driver cannot run it yet

A human ruled «yes» on the `kast_ur_i` retry and chose to re-make `darv_i` on Anthropic in the same run.
One run for both is required: the `c1` probe ration allows two attempts per UTC day, six hours apart, and
the second 22-09 slot opens at 17:45:13Z.

1. **`kast_ur_i`:** `coordinator.py prepare-requeue h4527vol14 --defect` built attempt `rq01-defect`
   (1 card, harness and v2 execution manifest under
   `output/coordinator/artifacts/h4527vol14/requeue/rq01-defect/`). The lease is now `requeue_prepared`.
   As designed, the step appended a `blocked` row for the key to `src/pilot/no_pwg_residuals.jsonl` (it
   keeps the next volume plan from preparing the card twice) and one TM-denylist address. The ledger row
   is committed from the Mac byte-identical to the MSI line.
2. **The driver gap.** A zero-call dry run of `bounded_staged_run.py` with all five `h4527vol*` lease ids
   lists `importable_prepared_leases: []` and skips `h4527vol14`; `--lease-id h4527vol14` alone is refused
   («--lease-id set does not match the staged plan»). A requeue runs only as an in-run supervisor item
   (`window['requeue']` → `materialize_requeue`) on the serial route. The cohort engine records
   `requeue_backlog_keys` and reloads them on `--resume`, but never dispatches them.
3. **`darv_i`:** lease `h4527sen08` is `promoted`, and the planner excludes promoted headwords. A
   `coordinator.py claim --kind defect-repair` lease exists for exactly this case, but no plan window can
   point the driver at it.
4. **The store side is already safe.** `promote_final_cards.py merge_store_rows` is better-attempt-wins:
   ties favour the incoming attempt, and only human-touched rows are protected. The three `darv_i` rows
   are `ai_translated` with `reviewer: null`, so a complete Anthropic attempt replaces them without
   `--override-reviewed`.
5. **Not done:** running the harness or `max_account_orchestrator.py` directly, because that skips the
   probe ration, the canary receipt and the call cap. The driver change is specified as H4527's next step
   in the [handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4527-Opus_RussianTranslation_pwg-ru-cohort-live-acceptance-width2_10.09.26.md)
   (section «Progress — 22-09-2026 (2)»).

_Гасунс_
