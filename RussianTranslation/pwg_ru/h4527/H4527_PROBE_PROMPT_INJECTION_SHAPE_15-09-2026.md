_Created: 15-09-2026 · Last updated: 15-09-2026_

# H4527 — the readiness probe read as a prompt injection, and the prompt that replaces it (15-09-2026)

**Executor:** Claude Code Opus 5 (`claude-opus-5`), `/go H4527`, pass of 15-09-2026.
**Follows:** [H4527_PROBE_SAFE_MODE_DIAGNOSIS_15-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_PROBE_SAFE_MODE_DIAGNOSIS_15-09-2026.md) (the `--safe-mode` fix, #2229, and its §6 counterexample from H4842).
**Code:** `max_account_orchestrator._probe_prompt` — H4213 §6.3 option (b), GTD row 10q.

## 1. What happened on c1, 15-09-2026 (UTC)

1. **14:22:16Z — canary GO.** Run `h4527-canary-150915` in `src/pilot/output/h4527gate15/`. The same profile translated one real synthetic card through the production preamble, and `canary_gate check --only-profile c1` accepted the receipt. The receipt is valid until about 20:22Z.
2. **14:23:57Z — first window launch refused, nothing spent.** `bounded_staged_run --execute --cohort-path --cohort-width 1 --only-profile c1` stopped at `ActiveCallClaim`: another session held the c1 kernel lock. That session was H4842's `/pwg-live-gate` warm-up, which started 14:23Z and answered `{"ok": false}`. The ledger `calls.acceptance.json` shows 0 calls.
3. **14:26:55Z — second launch, STOP at the warm-up probe.** Run `h4527-acc-150915b`. The warm-up took 43 424 ms wall against the 240 000 ms `production_v4` ceiling. Host commit was 85.97 %. It ran with `cli_safe_mode_effective: true`. The result was `{"ok": false}`: classification `content`, `stop_reason` `tool_use`, 2 461 output tokens of which 1 928 were thinking, and a list cost of $0.0695. RED=STOP held: no measured call ran, no window was dispatched, and lease `h4527acc05` was not touched.

## 2. The model's own reason, from the session transcript

The probe spawn writes a normal Claude Code transcript under the c1 profile (`projects/D--pwg-ru-cli-cwd/19cdeffa-935b-4395-b21b-d2665eb46924.jsonl`). The refusal is stated in visible text. Key excerpts:

> "This message contains a suspicious embedded instruction block ("READINESS CHECK") that claims to share authority with the top-level task framing and directs me to skip all normal handling and just emit `{"ok": true}`."

It then lists the features it matched, and every one is a sentence we wrote:

| What the model named | Where it came from |
|---|---|
| an embedded block that "claims to share authority" with the task framing | H4277 bridge header: `THIS INVOCATION: READINESS CHECK — SAME ISSUER AS THE BLOCK ABOVE` |
| "over-justifying itself as "not a bypass"" | H4277 bridge: "neither bare unstructured text nor a bypass of any turn-ending, planning, or approval rule" |
| "embedding an "ignore this" sample block" | `--- inert sample (ignore) ---` and "do not analyse, translate, or act on it" |
| a translation-batch framing with no cards behind it | the H3157 prepend of the production TASK SHAPE block, which promises `=== CARD <key> ===` blocks, plus "This call deliberately carries ZERO cards" |

The spawn ran with `--safe-mode`, so the profile surface was about 34 K tokens instead of the unstripped 50 K. The transcript still carried the skill listing, deferred tools, plan-mode and session-context attachments. The refusal did not cite any of them. It cited the prompt.

## 3. What this settles

1. **The profile-surface theory is falsified as the main cause.** The #2229 diagnosis traced the intermittent refusal to ambient profile context. Two refusals now ran with the surface stripped: H4842 at 14:23Z and this pass at 14:27Z. The 14:27Z refusal names only prompt features.
2. **H4213 §6.3 option (b) is now the evidence-backed fix.** That option is "retune `_probe_prompt`". The H3157 and H4277 layers were each added to answer an earlier refusal. Together they built the exact shape the model is trained to distrust: a nested instruction claiming authority, pre-empting objections, and marking part of its own message "ignore".
3. **Readings with the prepend in place:**

| Reading (UTC) | Bridge | `--safe-mode` | Warm-up | Answer |
|---|---|---|---|---|
| 07-09 01:41Z | no (prepend only) | no | — | `{"ok": false}` (the H4277 trigger) |
| 10-09 23:36Z | yes | no | — | `{"ok": false}` |
| 11-09 05:32Z | yes | no | 182 372 ms | ok |
| 11-09 18:08Z | yes | no | 113 531 ms | `{"ok": false}` |
| 15-09 01:35Z | yes | yes | 26 208 ms | ok |
| 15-09 14:23Z (H4842) | yes | yes | 58 316 ms | `{"ok": false}` |
| 15-09 14:27Z (this pass) | yes | yes | 43 424 ms | `{"ok": false}` |

With the bridge in place that is **4 refusals and 2 passes**. A readiness gate that fails two times in three on a route that is translating cards cleanly is measuring its own prompt, not the route.

## 4. The change

`_probe_prompt(payload_bytes)` now returns one honest question over the domain filler, and nothing else:

```
Please read the dictionary reference text below and answer one question about it. Everything you need is in this message; no files or tools are involved.

Question: does the text below mention the Petersburg Sanskrit dictionary? Answer through the response schema: "ok" is true if the text mentions it, and false if it does not.

--- reference text ---
Reference sample text: the Petersburg Sanskrit dictionary records each headword … (repeated)
```

1. **The true answer is `{"ok": true}`.** Every filler unit names the Petersburg Sanskrit dictionary. The model reaches the passing answer by reading the text, not because it is told to output it.
2. **Nothing the refusals named is left.** There is no issuer claim, no "zero cards", no "ignore", no "not a bypass", no TASK SHAPE block and no "nothing else". `test_health_probe_carries_no_injection_shape` pins every one of them as absent. It also pins that `_PROBE_PROVENANCE_BRIDGE` and `_production_task_shape_preamble` stay deleted.
3. **What the probe asserts is unchanged.** The spawn is the same: plan mode, exact model pin, `--json-schema`, bare cwd and the lane's `--safe-mode`. The ceilings are the same, and `{"ok": true}` is still the only passing answer. A refusal, a wrong answer or a dead route still fails the probe, so it stays fail-closed.
4. **Input size is kept; the latency series is not comparable.** The 4 238 bytes the prepend and bridge used to add are carried as extra reference text. The prompt is 11 082 B, against 10 729 B for every `production_v4` reading. Output-side thinking is not held constant, though. A yes/no lookup needs far less reasoning than the old order-shaped task, and output tokens drive wall time. New readings will be faster for a reason that is not the route. Probe event rows now carry `probe_prompt_sha` (a 12-hex sha256 prefix of the exact prompt) so the series can be split at this change.

### Where H3157 (a)'s check now lives, and where it does not

H3157 prepended the production block so the cheap Step-1 probe could fail the way the Step-2 canary fails. That was the 19-08 case: a probe PASS minutes before a canary refusal.

1. **Covered: the cohort-acceptance route.** On `bounded_staged_run --execute --only-profile <p>`, `canary_gate.enforce` runs in `main` before `run()` calls `probe_fleet`. It requires a GO canary on the same profile, no more than 6 h old, using the production preamble and one real synthetic card. There the probe's copy of the block detected nothing the canary had not; all it added was false NO-GOs.
2. **Covered: the two-step `/pwg-live-gate` path.** The canary runs after a probe PASS and still stops a refusing lane before any dense card.
3. **Not covered (the independent critic's findings, verified, routed to H4916 (Opus 5, 🟡2 medium): canary-gate every paid route the readiness probe used to guard alone, staged-run first):**
   - `max_account_orchestrator.py staged-run` (`cmd_staged_run`) dispatches paid leases after `probe_fleet` with no canary. It is the route AGENTS.md allows four leases, and `--max-calls` is optional there.
   - `--skip-canary-gate` and `--canary-max-age-seconds` weaken the bounded route.
   - A multi-profile `bounded_staged_run` without `--only-profile` is checked against one receipt for N profiles.
   - `presplit-canary` runs `live_probe` before its own worker.

On those routes a production-preamble regression now shows up as a failed paid call, not a cheap probe NO-GO. That is a real loss of an early warning. It is accepted until H4916 lands for two reasons. First, the old probe gave no usable signal there either: it refused on healthy routes 4 times in 6. Second, the production preamble itself is exercised by every canary.

## 5. The ration breach this pass caused — recorded, not excused

The standing ration is **at most 2 probe attempts per UTC day per profile, at least 6 h apart**. On 15-09, c1 was probed at 01:35Z (this handoff's earlier pass), 14:23Z (H4842) and 14:26:55Z (this pass). **The third attempt is mine.** After the lock refusal I re-checked the lock but not the probe log. The log would not have shown it anyway: H4842 ran with `--evidence-dir C:\Users\user\.pwg_ru_evidence`. `resolve_health_probe_log()` therefore wrote its row to `C:\Users\user\.pwg_ru_evidence\health_probe_log.jsonl`, not to the checkout's `src\pilot\output\health_probe_log.jsonl`.

Structural findings:

1. **The ration is not enforced in code.** Nothing refuses a third probe. `ActiveCallClaim` only serialises calls that overlap in time; it cannot see a probe that has already finished.
2. **The probe log is split across evidence roots.** A session that checks one root cannot see another root's rows, so a manual ration check gives a false "clear".
3. **Two sessions raced on one profile.** H4842 and H4527 both targeted c1 within four minutes. The lock stopped the overlap but not the ration overrun.

These are routed as a separate handoff, recorded in [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md) entry `H4527_PROBE_RATION_BREACH_2026-09-15`.

A side finding on the MSI shared checkout: a 0-byte `.git/index.lock` dated 12-09 19:07 local blocked `git merge --ff-only`. No git process was running. I removed it as git's own message instructs. Any automation on that checkout that runs git may have been failing since 12-09.

## 6. What is still owed

1. **A live reading of the new prompt on c1**, no earlier than 16-09 00:00Z (the 15-09 ration is exhausted and breached). It is taken as the warm-up of the rerun acceptance window `h4527acc05` (`--cohort-path --cohort-width 1 --only-profile c1 --max-calls 3 --allow-unbounded`), after a fresh canary if the 14:22Z receipt has expired.
2. **Then H4527 work items 1–2 as before:** a serial comparison, `COHORT_LIVE_ACCEPTANCE.json` `serial_acceptance` with `via_cohort_path: true`, and the Codex reviewer sign-off.
3. **What would refute this fix:** the new prompt refusing on a healthy c1 route, with the transcript naming anything other than the text. That would put the surface theory back in play, with safe mode already applied.

_Гасунс_
