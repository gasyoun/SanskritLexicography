# H994 — PWG→Russian two-profile live-ladder measurement (rung 1–2), owner Option B

_Created: 15-07-2026 · Last updated: 15-07-2026_

> **ID note:** `RussianTranslation/.ai_state.md` pre-named this work **H963**; by mint time the atomic
> handoff counter had advanced past it (961–993 taken by other sessions), so it was minted as **H994**.
> H963 is not this work.

**Verdict: `FOUR-PROFILE ACCEPTANCE = NO-GO (owner-gated, unchanged)` · `TWO-PROFILE LADDER HALTS AT RUNG 2` · `CANARY (RUNG 3) NOT REACHED / additionally blocked` · `NO PROMOTION — canonical store unchanged at 11,605`.**

H994 is the owner-gated *live* ladder that turns H960's offline scaffolding
([v1.9.13](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.9.13)) into a measured
four-profile production GO/NO-GO. This session executed the owner-selected **Option B — two-profile
measurement only** (c1/c4; latency + the SANLOSS/TNMASK/`dropped_sanskrit_span` canary false-flag
measurement; **no promotion, no store mutation**). The measurement's honest outcome: the two-profile
ladder halts at the health rung, the canary rung is not reachable in the current fleet/input state, and
two actionable defects were surfaced. Four-profile acceptance stays owner-gated on the c5/c6 logins.

**Executor:** Opus 4.8 (`claude-opus-4-8[1m]`), Ultracode, orchestrating live probes of the exact
generation model `claude-sonnet-5`. Ran from a fresh worktree off `origin/master` (`564dd2f3`, includes
#476 v1.9.13 + #483). **No promotion, no store/TM mutation** — the canonical store
`RussianTranslation/src/pwg_ru_translated.jsonl` is unchanged at **11,605 rows** (mtime 2026-07-14 07:22)
before and after; every probe pinned `PWG_RU_STORE` to a scratch path as belt-and-suspenders and none
wrote it.

## Rung 1 — auth (read-only, `claude auth status`)

| Profile | `CLAUDE_CONFIG_DIR` | `loggedIn` | Tier |
|---|---|---|---|
| **c1** | `D:\ClaudeTools\profiles\claude1\.claude` | ✅ true (`sanskrit.research.institute@gmail.com`) | max |
| **c4** | `D:\ClaudeTools\profiles\claude4\.claude` *(this session's own profile)* | ✅ true | max |
| **c5** | `D:\ClaudeTools\profiles\claude5\.claude` | ❌ **false** (`authMethod: none`) | — |
| **c6** | `D:\ClaudeTools\profiles\claude6\.claude` | ❌ **false** (`authMethod: none`) | — |

- **Four-profile acceptance = NO-GO** — rung 6 (`multi-profile-20` across c1/c4/c5/c6) is unreachable
  until the owner logs in c5 and c6 (`claude auth login` per `CLAUDE_CONFIG_DIR`; agents never handle the
  login URL/code/token). This is **unchanged** from the H960 note ("c5/c6 were logged out on 15-07").
- **Two-profile subset (c1/c4) auth = PASS** — both authenticated Max. `auth status` is a pure read
  (no tokens); it does **not** reveal an active rate-limit (that surfaces only on a real call — see rung 2).

## Rung 2 — latency / health (D-K two-phase `live_probe`, exact model `claude-sonnet-5`, 30 000 ms ceiling)

Raw probe events (`run_id=h963-two-profile-latency`):

| Profile | Phase | elapsed | classification | reading |
|---|---|---|---|---|
| **c1** | warm-up | 11 051 ms | **`rate_limit`** | account parked/rate-limited at probe time → STOP |
| **c4** | warm-up | 8 007 ms | `success` | fast, healthy |
| **c4** | measured | 7 913 ms | **`content`** | valid envelope, structured payload `ok ≠ true` → NO-GO |

**On the strict acceptance-probe reading both profiles fail rung 2, so the two-profile ladder halts here.**
But the two failures are different in kind, and one is a probe artifact:

- **c1 — genuinely rate-limited.** The warm-up call returned a rate-limit envelope (780 output bytes,
  11 s). c1 is unusable until its limit resets. Not re-probed (a re-probe on a parked account can extend
  the park).
- **c4 — a FALSE NO-GO from a probe-design defect, not ill health.** A targeted diagnostic (two raw
  `claude -p --json-schema --model claude-sonnet-5 --permission-mode plan` calls on c4) shows:
  - The **degenerate acceptance-probe prompt** (`Return JSON {"ok":true}. Preserve this padding as inert
    input.` + 6 491 `x` padding bytes) makes Sonnet-5 under **plan mode** *refuse*, returning prose —
    `"I'm not going to call that tool on demand like this… there's still no actual task here… Plan mode is
    active, and its explicit rule is that my turn should only end via AskUserQuestion…"` — with
    `structured_output=None`, and burning **53 924 ms** (the refusal itself generates a long answer, so it
    also breaches the 30 s ceiling). This is the `content`/`timeout`/`malformed` NO-GO the acceptance probe
    reports.
  - A **natural prompt** (`Reply with the JSON object {"ok": true} and nothing else.`) on the same profile
    returns `structured_output={'ok': True}` in **12 097 ms** — clean.
  - **Conclusion (as recorded at first measurement — see the correction below):** c4's rung-2 NO-GO is a
    probe-prompt artifact, not a refusal-vs-health question. The "~8–12 s sub-ceiling" gloss on that first
    pass was itself wrong — corrected next.

> **UPDATE 15-07-2026 — D-P FIXED, and the "sub-30 s c4" conclusion CORRECTED (Opus 4.8 `claude-opus-4-8[1m]`).**
> The D-P probe-prompt defect is fixed in
> [`max_account_orchestrator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py)
> ([v1.9.17](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.9.17)): `_probe_call` now sends
> a natural, load-representative task (one unambiguous "reply with exactly `{"ok": true}` and nothing else"
> instruction + ≥5 KB of inert, domain-shaped filler) under the **same `--permission-mode plan` the real
> generation path (`headless_worker.call`) uses**, with a `D-P readiness prompt` selftest. Re-probing c4
> with the FIXED probe: warm-up **29 743 ms** / measured **52 815 ms**, both `success`, output 1 483 B (no
> refusal, no over-generation). **This corrects the "~8–12 s, first sub-ceiling reading" claim above:** the
> old `'x'`-padding BPE-compresses to few tokens (artificially fast ~8 s) and the 12 s figure came from a
> *payload-free* diagnostic — neither is load-representative. Under a representative ≥5 KB payload c4 is
> **~30–53 s (high variance, at/over the 30 s ceiling)** — consistent with H818/H895's ~40 s NO-GOs, **NOT**
> sub-ceiling. So the D-P fix's value is twofold: it removes the false-*refusal* NO-GO **and** restores an
> honest latency reading. The latency rung remains a genuine NO-GO (H818/H909 foreign-route territory),
> independent of the c5/c6 logins.

## Rung 3 — canary false-flag measurement — NOT REACHED / additionally blocked

Rung 2 did not cleanly pass, so the ladder does not gate into rung 3. Independently, the canary
false-flag measurement is **not cleanly runnable in the current state**, for three reasons — recording
them so the next session does not re-derive:

1. **Only one usable profile.** c1 is rate-limited → c4 is the only live profile → any run now is
   **single-profile**, a deviation from the two-profile framing (the guard false-flag *rate* is
   profile-count-independent, but the "two-profile" label would not hold).
2. **The named canaries are known-negatives.** `darvI` is a documented **deterministic `fidelity-reject`**
   (the `{#…#}`-span-drop class — [RUN_LOG `no_pwg_w10`/`w02` blocks](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md);
   "a requeue reproduces the identical failure; needs the unshipped Tier-1 german-field source-anchoring
   fix"). Generating it live reproduces a known negative and burns cost for a null card — the exact waste
   the RUN_LOG repeatedly warns against — and a fidelity-rejected null never reaches the `accept()`
   SANLOSS soft-guard path the measurement is meant to exercise.
3. **Canary inputs are absent.** `src/pilot/input/` is gitignored and does not exist in a fresh worktree,
   so no canary portrait is present; running one would first require rebuilding the no_pwg input pipeline
   (`dict_merge` → portrait) for the chosen keys.

**Prerequisites to actually run rung 3 cleanly (next session):**

- Fix the rung-2 probe defect first (below) so the health gate gives an honest reading.
- Either wait for c1's rate-limit to reset (→ true two-profile) or take an explicit owner OK for a
  **single-profile-c4** measurement.
- Select a canary set that exercises the **silent** SAN-LOSS `accept()` path — a card that *passes*
  fidelity while dropping a source sense (the H818 fc1 `darv_i` "output 2/3 passed clean" shape that
  H920/H960 instrumented), **not** a deterministic fidelity-reject — and rebuild its input portrait.

## Defects surfaced this session

1. **D-P · acceptance-probe prompt fragility (rung 2) — ✅ FIXED 15-07-2026 ([v1.9.17](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.9.17)).**
   `_probe_call`'s degenerate padding prompt (`"Return JSON {ok:true}. Preserve this padding as inert
   input." + N×'x'`) tripped Sonnet-5's `--permission-mode plan` refusal, yielding a false
   `content`/`timeout`/`malformed` NO-GO on a healthy profile. **Fix:** `_probe_call` now sends a natural,
   load-representative task via a new `_probe_prompt()` helper — one unambiguous "reply with exactly
   `{"ok": true}` and nothing else" instruction + ≥5 KB of inert, domain-shaped filler — under the **same
   `--permission-mode plan` the real generation path (`headless_worker.call`) uses**, with a `D-P readiness
   prompt` selftest that captures the argv + stdin. Live-verified on c4: both probe phases return `success`
   (no refusal, 1 483 B output). **Bonus correction:** the fix also exposed that the old `'x'`-padding gave
   *artificially fast* latency (few tokens after BPE) — under the fixed representative payload c4 is ~30–53 s
   (latency NO-GO), not the sub-30 s the first pass reported. See the Rung 2 UPDATE block above.
2. **D-Q · canary-set selection (rung 3).** The named canaries (`darvI`/`gaRanA`) are poor choices for the
   SAN-LOSS *soft-guard* measurement: `darvI` is a deterministic fidelity-reject (never reaches the
   passing-card `accept()` path). The measurement needs a curated canary that *passes* fidelity while
   dropping a sense. Curate it before the live rung.

## What this moves

| Gate | Before this session | After (measured live) |
|---|---|---|
| four-profile auth | assumed c5/c6 out (H960 note) | **confirmed NO-GO** — c1/c4 Max, c5/c6 `loggedIn:false` (unchanged 15-07) |
| home-route latency | ~40 s honest NO-GO ×2 (H818/H895) | ~~c4 sub-30 s~~ **CORRECTED: c4 ~30–53 s under a representative payload → latency NO-GO** (the sub-30 s pass was an `'x'`-padding artifact); consistent with H818/H895 |
| acceptance-probe reliability | assumed sound | **defect found (D-P) AND ✅ fixed** ([v1.9.17](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.9.17)) — natural load-representative prompt; false-refusal gone; honest latency restored |
| canary readiness | assumed runnable | **blocked** — c1 rate-limited + known-negative canary set + inputs absent (D-Q + prereqs) |
| canonical store | 11,605 | **11,605 (untouched)** — no promotion, no mutation |

## Limitations

- Single measurement pass; c1 not re-probed (avoids extending its park). c1's rate-limit is transient —
  its state may differ minutes/hours later.
- c4's health is established by two diagnostic calls, not a full generation; "healthy" here means fast +
  returns valid structured output on a natural prompt, which is the precondition for — not proof of — a
  clean card generation.
- No canary generation was run, so **no live SAN-LOSS drop-rate or guard false-flag rate was measured**;
  rung 3 remains the open measurement, with the prerequisites above.
- Four-profile acceptance and H255 unfreezing are unchanged: both still require the owner c5/c6 logins and
  the full live ladder (rungs 3–6).

_Auto-generated by Opus 4.8 (`claude-opus-4-8[1m]`) as the H963 executor, Ultracode; two-profile live
rung-1/2 measurement only, no canary generation, no promotion, no store/TM mutation._

_Dr. Mārcis Gasūns_
