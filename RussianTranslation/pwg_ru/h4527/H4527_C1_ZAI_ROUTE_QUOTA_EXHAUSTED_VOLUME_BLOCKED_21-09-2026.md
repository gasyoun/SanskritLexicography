_Created: 21-09-2026 · Last updated: 21-09-2026_

# H4527: the c1 profile routes to z.ai GLM 5.3, that plan's quota is exhausted, and the volume wave cannot start

**Handoff:** [H4527](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4527-Opus_RussianTranslation_pwg-ru-cohort-live-acceptance-width2_10.09.26.md)
**Executor:** Claude Code, Opus 5 (`claude-opus-5`), interactive `/go` on the Mac, driving MSI over tailnet ssh
**Paid calls spent:** 0. The one canary attempt was rejected with HTTP 429 before any tokens were produced.

## Why this pass ran

On 21-09-2026 a human rejected the «leave it parked» ruling for H4527 and chose the volume route instead:
put `c1` to work on real PWG-RU cards, several per launch, instead of spending its daily ration
on one-card acceptance windows. Width 2 still cannot run, because the engine allows one active
call per profile and `c1` is the only funded profile.

## What was done (zero paid calls)

| # | Step | Result |
|---|---|---|
| 1 | `probe-ration --account c1` | exit 0, `attempts_today: []`, `legal_now: true` at 19:07:29Z |
| 2 | MSI shared checkout fast-forward | `2b5b44278` → `7433c250f`, tree clean |
| 3 | `no_pwg_scale_plan.py --window-size 1 --limit-windows 5 --require-senses 1 --headless --dry-run --profile-slot c1 --config-dir D:\ClaudeTools\profiles\claude1\.claude --prefix h4527vol` | walked 21 queue heads and found **5 eligible**: `h4527vol09` `gl_ana`, `h4527vol10` `hasita`, `h4527vol11` `jaw_ayus`, `h4527vol14` `kast_ur_i`, `h4527vol22` `ku_rqal_i` (each `~~h0_zz_pw`, one sub-card) |
| 4 | `canary_manifest_build.py --profile-slot c1` into `src\pilot\output\h4527vxgate` | manifest sha256 `c6cb295a85c7dc253e9f7f79c60a58d35e6c4d6a0e49843cd34aa0ff4728edfb` |
| 5 | `headless_worker.py` canary, run `h4527vx-canary-210921` | **`classification: rate_limit`, HTTP 429, exit 21, 213 700 ms, 0 tokens** |

The 429 body, verbatim:

```
API Error: Request rejected (429) · [1310][Weekly/Monthly Limit Exhausted. Your limit will reset at 2026-09-24 02:13:42]
```

## The finding: `c1` is not an Anthropic profile any more

`D:\ClaudeTools\profiles\claude1\.claude\settings.json` (last written **2026-09-20T13:42:30Z**)
now carries, in its `env` block:

```
"ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
"ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-5.3-flash[1m]",
"ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5.3[1m]",
"ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.3[1m]",
```

Only the base URL and model names were read. No token value was read or copied. None of the three
older backups (`settings.json.bak` 30-07, `settings.json.pre-h1803.bak` 28-07,
`settings.json.pre-ssh-sync.bak` 30-07) contains `ANTHROPIC_BASE_URL`, so the z.ai route is new.
Who wrote it on 20-09, and why, is not recorded anywhere this pass could find.

Error code `[1310]` and the «Weekly/Monthly Limit Exhausted» wording are z.ai's format, not
Anthropic's. The rejection is therefore a quota wall on a GLM coding plan, not a Claude Max rate
limit. The reset stamp has no time zone. If it is Beijing time (UTC+8), the reset is
**2026-09-23 18:13:42Z**. That is unverified.

## What this does to earlier evidence

The 20-09 acceptance window (`h4527-acc-200920`, first clean card, store 11521 → 11524) ran at
18:01Z, **after** the 13:42Z settings change. The profile's session transcripts for that window
record `"model": "claude-sonnet-5"` (5–9 messages per file, 17:59Z–18:02Z). But the request went to
`api.z.ai`, and the `model` field in a transcript is whatever the endpoint echoed back. So the transcript alone
cannot tell whether that card was translated by Claude Sonnet 5 or by GLM 5.3. A separate
interactive session on `c1` at 16:50Z the same day recorded `glm-5.3` ×214, so the route was live
before the window ran.

**The canary answers whether the headless lane picks up the route.** This pass's canary went
through `headless_worker.py` with safe mode at the lane default, and z.ai rejected it in z.ai's own
format. So the headless route **does** inherit the profile's `settings.json` `env` block. The
settings file has not been written since 20-09 13:42:30Z, so the 18:01Z window took the same route.
z.ai's Anthropic-compatible endpoint serves only GLM models. **Inference, high confidence, not
proven from a response header:** the 20-09 acceptance card `darv_i~~h0_zz_pw`, and every `c1` card
promoted since 20-09 13:42Z, was produced by GLM 5.3 under a `claude-sonnet-5` label. That matters
for H4527 work item 2: the reviewed window's `gen_model` field is wrong.

## Mechanical side effects this pass caused, and what was restored

1. **`--dry-run` registered the leases anyway.** Step 3 was meant to make no coordinator change, but
   `coordinator.py status` afterwards lists `h4527vol09/10/11/14/22` as `prepared`. A follow-up real
   preparation under prefix `h4527vx` then stopped at `h4527vx09` (exit 1), because `gl_ana` already
   had an active lease. That refusal is the stale-lease guard working, and it left one unregistered
   artifact directory, `output\coordinator\artifacts\h4527vx09`. The five `h4527vol*` leases are
   **left prepared** for the next legal window. They are exactly the eligible set.
2. **`progress_dashboard/*.json` was rewritten three times**, by the dry run and by both preparation
   attempts (−2144/+998 lines). The tree was clean at the start of the pass, and the file mtimes
   matched this pass's commands to the second. Each time the files were restored with
   `git checkout -- progress_dashboard`. The shared tree ends clean.

## Next step, once a human settles the route

The five prepared leases can run in one launch through the cohort path at width 1:
`--lease-id h4527vol09 --lease-id h4527vol10 --lease-id h4527vol11 --lease-id h4527vol14 --lease-id h4527vol22`,
with `--max-calls 7`, a fresh canary GO receipt, and the 16-09 corrected form (`--coordinator`, a bare
`--cwd`, `--events`). Nothing may launch until the route question is answered. Launching on the z.ai
route either hits the same 429 or produces GLM cards under a Claude label.

_Гасунс_
