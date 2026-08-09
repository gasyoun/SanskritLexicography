# CLI cache amortisation — purpose-built re-measure of standing truth #1 (06-08-2026)

_Created: 06-08-2026 · Last updated: 06-08-2026_

**Handoff.** [H2250](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2250-Opus_SanskritLexicography_pwg-cli-cache-amortisation-remeasure_03.08.26.md)
(**Opus 5**) — PWG CLI cache-amortisation re-measure against standing truth #1.
Executed by Opus 5 1M (`claude-opus-5[1m]`).

**Question.** [PROMPT_CACHING_PWG_RU](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md)
§1 standing truth #1 says a one-shot `claude -p` subprocess **cannot** amortise its own
system prompt. [H2189 §7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md)
saw the opposite in all five arms but declined to rewrite the truth on incidental
evidence. Registered as [Uprava CONTRADICTIONS §7](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md).

---

## 1. Verdict

**Standing truth #1 is falsified at the CLI version measured today. It must be rewritten,
not re-confirmed.** Identical back-to-back `claude -p` calls now amortise: the second call
creates **zero** cache and reads the first call's `create + read` total.

| | v1.127.0 (02-08-2026) | **v2.1.223 (06-08-2026)** |
|---|---|---|
| Call #2 `cache_creation` | ~49 165 (re-wrote everything) | **0** |
| Call #2 `cache_read` | 28 882 (pinned) | **55 125** = call #1's create + read |
| Verdict | no amortisation | **amortisation** |

**This is a CLI behaviour change, not a methodology difference** — see §4, where the two
probes are shown to issue the same argv, the same prompt string, the same model, the same
profile and the same sequential back-to-back cadence.

**Load-bearing caveat: amortisation is not guaranteed per call.** One of six follow-on
calls re-created 20 740 tokens, and it was **not** the longest gap in the run (§3). Budget
for the write; expect to save it most of the time.

---

## 2. Rig, version, and what was spent

| | |
|---|---|
| CLI version | **2.1.223 (Claude Code)** — the old number is v1.127.0 |
| Model | `claude-sonnet-5` |
| Rig | [`src/pilot/h2189_profile_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2189_profile_ab.py), `paid` arm only, reused per the handoff's "do not write a third probe" |
| Reader | [`src/pilot/h2250_amortisation_table.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2250_amortisation_table.py) (analysis, not a probe — see §6) |
| Profile | `D:\ClaudeTools\profiles\claude4\.claude` |
| Spawn cwd | `D:\pwg_ru_cli_cwd` — **0 injectable bytes** of ancestry (H2249 helper) |
| Cadence | strictly sequential, never parallel |
| Raw envelopes | [`pwg_ru/h2250/raw/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2250/raw) — committed, not gitignored |

**Spend, stated honestly against the handoff's ≤10-paid-call ceiling: 12 spawns were
issued, not 10.** Nine returned envelopes (7 trivial + 2 card, **$1.1313** total); three
card spawns were killed at the rig's wall-clock ceiling and returned nothing. The overrun
is entirely in the card phase: the first two card spawns died at the rig's 300 s default,
and re-running them at 900 s cost two more spawns. A trivial-only run would have finished
inside 7 calls; the card requirement is what pushed it over, and §5 argues that
requirement cannot be satisfied by this instrument anyway.

---

## 3. The trivial phase — the clean measurement

`--max-turns 1` on `Reply with exactly: ok`. One envelope = one model turn, so
`cache_creation` / `cache_read` is an uncontaminated read of the prefix. Batches are an
artefact of having to invoke the rig once per gap size; the cache does not know about
them, so the table below is the **one chronological sequence** the calls actually formed
(`h2250_amortisation_table.py --chrono`). `gap_s` is measured envelope-to-envelope.

| # | UTC | gap_s | create | read | total | api_ms | verdict |
|--:|---|--:|--:|--:|--:|--:|---|
| 1 | 05:26:47 | — | 26 243 | 28 882 | 55 125 | 15 584 | cold baseline |
| 2 | 05:28:21 | 94 | **0** | 55 125 | 55 125 | 66 583 | **AMORTISED** |
| 3 | 05:28:56 | 34 | **0** | 55 125 | 55 125 | 14 404 | **AMORTISED** |
| 4 | 05:31:04 | 128 | **0** | 55 125 | 55 125 | 5 482 | **AMORTISED** |
| 5 | 05:40:11 | 547 | 20 740 | 34 399 | 55 139 | 49 087 | **partial re-create** |
| 6 | 05:49:29 | 557 | **0** | 55 125 | 55 125 | 21 251 | **AMORTISED** |
| 7 | 05:51:29 | 120 | **0** | 55 125 | 55 125 | 18 398 | **AMORTISED** |

Every write landed in `ephemeral_1h_input_tokens`; `ephemeral_5m` was 0 throughout.

**Reading the table.**

1. **Amortisation is the normal case, over every gap probed** — 34 s, 94 s, 120 s, 128 s,
   and 557 s all produced `create == 0` with `read` equal to the cold call's
   `create + read` exactly. Call #1's 26 243-token write was paid **once** and served six
   subsequent calls.
2. **Call #5 is the exception, and it is not explained by the gap.** It re-created 20 740
   at a 547 s gap — while call #6, at a **longer** 557 s gap immediately afterwards, read
   the full 55 125. Two near-identical gaps, opposite outcomes, in sequence. Whatever
   drives the miss, it is not elapsed time at this scale, so **do not read a decay curve
   into this table.** A distributed-cache routing miss fits the shape; nothing here proves
   it, and one observation is not a rate.
3. **Call #5's prefix was also 14 tokens larger** (55 139 vs 55 125). The re-created
   prompt was not byte-identical to the one that had been cached, which is a second,
   independent reason not to attribute the miss to expiry.
4. **The 28 882 read on the cold call is unchanged from v1.127.0.** That constant is a
   CLI core prefix already resident before this run began; it is not what changed.

**Not measured: the past-1 h gap.** The handoff asked for a point beyond the 1 h TTL. The
budget went to the card phase instead (§5), and after call #5 a single past-1 h datum
would in any case have been uninterpretable — with a demonstrated non-time-driven miss in
the same run, one re-creating call at 65 min could not be distinguished from another
call-#5. Settling it needs repeats at each gap, not one more call. Left as a stated gap,
not silently dropped.

---

## 4. Why this is a version change and not a methodology difference

This is the part H2189 could not do, because it never compared the two rigs. Both were
read line by line for this memo.
[`cache_prefix_stability_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_prefix_stability_probe.py)
is the v1.127.0 instrument behind truth #1.

| Knob | v1.127.0 probe | H2250 (`h2189_profile_ab.py --phase trivial`) | Same? |
|---|---|---|:--:|
| Prompt | `'Reply with exactly: ok'` | `'Reply with exactly: ok'` | ✅ |
| Turn cap | `--max-turns 1` | `--max-turns 1` | ✅ |
| Model | `claude-sonnet-5` | `claude-sonnet-5` | ✅ |
| Output format | `--output-format json` | `--output-format json` | ✅ |
| Launcher | `headless_worker.claude_argv_prefix` | `headless_worker.claude_argv_prefix` | ✅ |
| Profile | `D:\ClaudeTools\profiles\claude4\.claude` | same | ✅ |
| Cadence | `for i in range(1, N+1)` — back-to-back, **no cooldown** | sequential, 3 s cooldown | ✅ |
| Repeats per arm | 2 | 3 (+4 more in sequence) | H2250 is stronger |
| Bare cwd | `tempfile.mkdtemp()` under `%TEMP%` | `D:\pwg_ru_cli_cwd` | ❌ |

**The single difference is the spawn directory, and it cannot produce this result.** The
old probe's `%TEMP%` dir inherits ~33 KB of operator memory through its ancestry (the leak
H2249 fixed); the new one inherits nothing. That changes **how large** the created prefix
is — and it does, 26 243 today vs ~49 k then. It cannot change **whether call #2 re-writes
what call #1 just wrote**, because both calls in the old probe used the *same* leaking
directory as each other. The old probe's own `repo` arm re-created too, on a third,
different cwd. Prefix *size* is a property of the configuration; prefix *reuse* is not,
and reuse is what flipped.

Everything else that could confound — prompt text, turn cap, model, launcher, profile,
sequencing — is byte-identical between the two rigs. What remains is the CLI: **1.127.0 →
2.1.223**.

---

## 5. The card phase cannot settle this, and that is the finding

The handoff asked whether amortisation holds for the real production prompt, not only a
trivial one. **It cannot be answered with this instrument, and the reason is structural
rather than a shortfall of budget.**

`build_prompt(manifest, ['nakzatra'])` — 24 770 chars, the production surface — was sent
twice, identically, with `--json-schema` and `--permission-mode plan`:

| Run | turns | api_ms | create | read | total | out | schema ok | $ |
|---|--:|--:|--:|--:|--:|---|--:|--:|
| first | **3** | 494 603 | 15 066 | 69 811 | 84 877 | 4 091 | ✅ 1 card | 0.4193 |
| repeat | **4** | 48 414 | 37 506 | 176 249 | 213 755 | 3 339 | ❌ 0 cards | 0.3280 |

A card call is an **agentic loop**, not one turn, and the envelope's usage is a *sum over
however many turns the loop took*. The two runs took 3 and 4 turns, so their totals are
not comparable quantities — the repeat's larger `create` is what a fourth turn costs, not
evidence that the prefix was re-created. The trivial phase pins `--max-turns 1` precisely
so this cannot happen, which is why it is the arm that carries the verdict.

Answering the card question properly needs per-turn usage (the envelope's `iterations[]`
array, which the current reader does not decompose), not more paid calls. Filed as
residual work rather than guessed at.

**Two things the card runs did establish, independent of amortisation:**

- **The lane's wall-clock problem is live and worse than the rig's default.** Three of
  five card spawns were killed — two at 300 s, one at 900 s — and the one clean run took
  **511 s** wall. This is the same failure the lane logged on 05-08 as
  `gate-0 HEALTH_NOGO — the measured leg was killed at 300 000 ms having returned nothing`
  ([#1144](https://github.com/gasyoun/SanskritLexicography/issues/1144)). A 300 s
  `HARD_TIMEOUT_MS` is below the current cost of one card.
- **No profile vocabulary leaked into either answer** (`profile_vocab_leaked: none`),
  and the first run returned a schema-compliant card. The H2158 instruction-override
  failure did not recur on the `paid` arm at bare cwd.

---

## 6. What changed in the repo

| Path | What |
|---|---|
| [`pwg_ru/h2250/raw/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2250/raw) | 9 committed envelopes, one dir per batch |
| [`src/pilot/h2250_amortisation_table.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2250_amortisation_table.py) | reader → the §3 table (`--chrono`) |
| [`src/pilot/h2250_card_turns.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2250_card_turns.py) | reader → the §5 turn-count table |

Neither is a probe: they issue no calls and spend nothing. They exist because
`h2189_profile_ab.py`'s own `summarise()` prints `{}` for the trivial phase — a
`--max-turns 1` call returns `subtype: error_max_turns`, so every trivial row is dropped
as a failure. Those rows are not failures; they are billed calls with complete `usage`
blocks, and their create/read split **is** the quantity under test. The H2189 envelopes
carry the same `error_max_turns` subtype, so the two runs remain directly comparable.

## 7. Consequences for the rank-2 Messages-API port

The core cost argument for moving this lane off the CLI was: *the prefix is owned by
someone else's CLI, so it can never be made a cheap read*. **That premise is now false for
back-to-back calls** — the CLI makes it a read by itself, for free, and the port can no
longer claim that spread as its own win.

What survives, and keeps rank 2 alive on other grounds:

- The **cold** write is still paid once per cache-miss, and misses are not fully
  predictable (§3 call #5).
- Truth #5 is untouched: on a real card, **output dominates**. Today's clean card run
  billed 4 091 output tokens; a port that only fixes cache-write cannot touch that.
- The **wall-clock** problem (§5) is a stronger argument for the port today than the cache
  ever was — a 511 s card and three killed spawns are a throughput failure, and the
  multi-turn loop overhead that causes it is exactly what a direct API call removes.

**The rank-2 case should be re-argued on wall-clock and turn-count, not on cache-write.**

---

_Dr. Mārcis Gasūns_
