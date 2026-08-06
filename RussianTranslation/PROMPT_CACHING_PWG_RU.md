# PWG→RU prompt caching — single playbook of record

_Created: 02-08-2026 · Last updated: 06-08-2026_

**Audience.** Operators and executors about to spend tokens on the PWG→Russian
(headless / manifest-v2) lane, or about to “optimise cache” again.

**Provenance.** Grok 4.5 (`grok-4.5`) consolidation of measurements already
committed 02-08-2026 (H2152 · H2158 · v1.127.0 · FINDINGS §284). This file does
**not** re-derive those numbers; it is the one place that ranks levers, names
what is settled, and points at the Opus 5 handoffs for remaining practical work.
**Revised 06-08-2026 by Opus 5 1M (`claude-opus-5[1m]`) under
[H2250](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2250-Opus_SanskritLexicography_pwg-cli-cache-amortisation-remeasure_03.08.26.md):**
standing truth #1 was **rewritten, not re-confirmed** — it described CLI v1.127.0 and is
false of v2.1.223 — and the rank-2 row was re-based on what survives that. Truth #1 is
therefore the one entry here that *does* carry its own fresh numbers.

**Sibling sources (do not fork facts away from here).** When this file and a
sibling disagree on a *standing rule*, trust the measurement source named in the
row and open a PR that re-syncs this file — do not invent a third copy.

| Role | Path |
|---|---|
| Operator runbook (do-this-before-spend) | [`src/pilot/RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) § Current operating truth |
| Pipeline narrative | [`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) § H2152/H2158 |
| Measurement tables | [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md) (02-08-2026 cache prefix) |
| Route A/B report | [`pwg_ru/h2158/ROUTE_AB_MESSAGES_API_VS_CLI_HEADLESS_02-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2158/ROUTE_AB_MESSAGES_API_VS_CLI_HEADLESS_02-08-2026.md) |
| Org finding | [Uprava FINDINGS §284](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) |
| Workflow postmortem (cross-agent cache) | [`src/pilot/POSTMORTEM_pril10_w1.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/POSTMORTEM_pril10_w1.md) |
| Lean-TR rejection | [`AB_TEST_LEAN_TR.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/AB_TEST_LEAN_TR.md) |

---

## 1. Standing truth (do not re-open without new measurement)

1. **A one-shot CLI subprocess DOES amortise its own system prompt — usually. Rewritten
   06-08-2026 ([H2250](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2250-Opus_SanskritLexicography_pwg-cli-cache-amortisation-remeasure_03.08.26.md))
   on a purpose-built run: the old "cannot" was true of CLI v1.127.0 and is false of
   v2.1.223.** Identical back-to-back `claude -p` calls now create **zero** and read the
   first call's `create + read` exactly. Over a 7-call sequence at gaps of 34 s / 94 s /
   120 s / 128 s / 557 s, the cold call wrote **26 243** (read 28 882, total **55 125**)
   and six later calls reused it — five of them for a `create` of **0**.
   **Do not read a decay curve into that.** One call re-created **20 740** at a 547 s gap
   while the very next call, at a *longer* 557 s gap, read the full 55 125 — the miss is
   not driven by elapsed time at this scale, and its prefix was also 14 tokens larger than
   the cached one. **So: budget for the write, expect to save it most of the time.** The
   past-1 h gap is deliberately **not** measured — with a demonstrated non-time-driven miss
   in the same run, one datum there would be uninterpretable. Every write still lands in
   `ephemeral_1h_input_tokens`; `ephemeral_5m` is 0.
   **A version change, not a methodology difference** — the two rigs were compared knob by
   knob and issue the same prompt, turn cap, model, launcher, profile and back-to-back
   cadence; the only difference is the spawn cwd, which changes how *large* the prefix is,
   not whether call #2 re-writes it.
   **The real card prompt settles nothing either way** — a card call is a multi-turn
   agentic loop whose envelope sums over turns (3 vs 4 turns on two identical prompts), so
   its totals are not comparable quantities. That needs per-turn `iterations[]`
   decomposition, not more paid calls.
   Report + committed envelopes:
   [pwg_ru/h2250/CLI_CACHE_AMORTISATION_REMEASURE_06-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/CLI_CACHE_AMORTISATION_REMEASURE_06-08-2026.md).
   Resolves [Uprava CONTRADICTIONS §7](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md),
   supersedes the v1.127.0 reading (H2152 follow-on), confirms
   [H2189 §7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md).
   **Consequence for rank 2 below: the cache-write argument for the Messages-API port is
   gone — re-argue it on wall-clock and turn-count.**
2. **Bare project cwd is free and shipped — and since H2249 it is actually bare.**
   The first shipping version checked only the immediate directory, so an empty dir
   under `%TEMP%` still inherited 32 779 B of operator memory from its ancestors; the
   helper now verifies the whole ancestry and returns `None` rather than a directory
   that only looks bare. Repo cwd injects `CLAUDE.md` + git
   state (~11–17 k volatile tokens/call). Bare cwd measured **−33 % cost,
   −30 % wall**. Code: `headless_worker.bare_cli_cwd()`; selftest pins
   both the spawn cwd and its ancestry.
3. **Call shape is not the cache lever.** One card per call (H2152). Do not
   batch N cards to “share cache” — wall-clock binds; one bad call destroys
   per-card attribution for all N.
4. **Lean TR is rejected.** Quality regression; TR is a small slice of
   `cache_create` once framework + card body dominate.
5. **On a real card, output tokens dominate cost.** `nakzatra` completed at
   **$0.8005**: cache create **34.6 %**, output **64.1 %**. A Messages API
   port that only fixes cache-write cannot touch that majority unless multi-turn
   loop overhead collapses (unmeasured until the API arm runs).
6. **1 h cache writes bill at 2× base ($6/M), not the 5 m table ($3.75).**
   `PRICE['cache_write']` is the 5 m rate; pricing 1 h writes at 5 m understates
   CLI cost by ~1.6×. **Shipped 02-08-2026 (H2190):** `parse_workflow_cost` now
   carries `cache_write_5m` / `cache_write_1h` derived from `PRICE['input']`,
   plus `cache_write_rate(ttl)`, `split_cache_creation()` and
   `usage_cost(usage, unknown_ttl=…)`. Reporting keeps the 5 m fallback for
   TTL-less legacy envelopes (history stays put); **cost gates must pass
   `unknown_ttl='1h'`** and fail closed. Pinned against the vendor's own
   `modelUsage.costUSD` on the committed `nakzatra` envelope.

---

## 2. Cost anatomy of one production-shaped call

| Component | Typical role | Rate (list, Sonnet-class basis) |
|---|---|---|
| Cache **create** (`ephemeral_1h`) | Framework + injected context re-written every CLI call | **$6.00 / Mtok** |
| Cache **read** | Stable core (~29 k) when anything hits | $0.30 / Mtok |
| Input (uncached) | Residual | $3.00 / Mtok |
| **Output** | Translation + multi-turn agent loop on CLI | **$15.00 / Mtok** |

Trivial-call floor (bare cwd, ~5-token prompt, translates nothing): ~**$0.20–0.30**
— pure scaffolding tax. Real card (`nakzatra`, diagnostic 600 s ceiling): **375 s**,
$0.80, with create 46 117 · read 35 220 · output 34 215.

Task prompt itself is small (~6–8 k tokens of translation work) against a CLI
prefix that can exceed **100 k** once profile context is included.

---

## 3. Ranked levers

| Rank | Lever | Status | Expected effect | Handoff / owner |
|---:|---|---|---|---|
| 0 | **Bare cwd** for every headless spawn | ✅ Shipped | −33 % cost / −30 % wall on fixed overhead | none — already in `bare_cli_cwd()` |
| 1 | **Strip the profile surface** — shipped as `--safe-mode`, **not** as a minimal profile dir | ✅ Measured 03-08-2026, wired **opt-in (default OFF)** | Real card: create **−69 %**, output **−49 %**, wall **−55 %**, cost **−61 %** ($0.6921 → $0.2712) with identical card content. A dedicated minimal `CLAUDE_CONFIG_DIR` measured only **−8.7 %** and was REJECTED as the lever | [H2189](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2189-Opus_SanskritLexicography_pwg-headless-minimal-profile_02.08.26.md) · [report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md) |
| 1b | **`bare_cli_cwd()` ancestry leak** — the helper rejected an ancestor with `CLAUDE.md`/`.git`, not one with `.claude\CLAUDE.md`, and its `%TEMP%` dir sits under the Windows user profile | ✅ Fixed 03-08-2026 | Was **32 779 B of operator memory in every paid call** since H2158. The helper now derives candidates and returns one only after `cwd_ancestry_scan` proves the whole ancestry clean, else `None`; **0 injectable bytes** on this box. `--safe-mode` only *masked* it and is no longer the thing standing in the way | [H2249](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2249-Opus_SanskritLexicography_pwg-bare-cwd-ancestry-leak-fix_03.08.26.md) · [H2189 report §1.1](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md) |
| 2 | **Messages API + explicit `cache_control` (1 h)** on stable prefix | 🟡 Open — **case re-based 06-08-2026 (H2250)**; API arm still needs credential | **"Turn create→read on framework" is no longer a win this lever can claim — truth #1 above now says the CLI does that by itself, for free.** What survives: typed HTTP failures, the single-completion output cut, and the *new* lead argument — **wall-clock and turn-count**. The one clean card call cost **511 s wall over 3 turns**, and 3 of 5 card spawns were killed at 300–900 s; the multi-turn loop overhead behind that is exactly what a direct API call removes. Re-argue rank 2 on throughput, not on cache-write | [H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md) · [H2250 report §7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/CLI_CACHE_AMORTISATION_REMEASURE_06-08-2026.md) |
| 3 | **Dual-rate cost tools** (`cache_write_5m` + `cache_write_1h`) | ✅ Shipped 02-08-2026 | Stopped understating CLI bills 1.6× ($0.6967 computed vs $0.8005 billed on `nakzatra`) | [H2190](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2190-Opus_SanskritLexicography_pwg-cache-write-1h-pricing_02.08.26.md) · [PR #1032](https://github.com/gasyoun/SanskritLexicography/pull/1032) |
| 4 | **Stable prefix reorder** (`preamble` → `translation` → `grammar` before card) | ✅ Shipped 03-08-2026, offline | Cross-**window** stable head **1 226 → 12 249 chars** (4.9 % → 49.5 % of a representative prompt). Within one window: no change. **Not** lean-TR — no byte dropped | [H2191](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2191-Opus_SanskritLexicography_pwg-prompt-prefix-reorder_02.08.26.md) |
| 5 | TM / frag-TM / fewer agent calls | ✅ Standing | Zero-call reuse where hashes match | existing pipeline |
| 6 | Presplit group budget (60 cite / 18 sense) | ✅ Shipped post-pril10 | Fewer framework re-caches on fragment lane | `gen_opt_harness2.py` |
| — | Trim TR / NWS for cache | ❌ Rejected | Noise floor; quality risk | `AB_TEST_LEAN_TR.md` |
| — | Multi-card batch to share cache | ❌ Rejected | Opposite of wall-clock bind | H2152 |
| — | Raise `HARD_TIMEOUT_MS` to “fit” cache overhead | ❌ Guard weaken | Hides hang class | H2158 fail criteria |

---

## 4. Practical steps (executor checklist)

Execute in order. Do **not** skip rank 0–1 to chase rank 2 without a human
subscription-vs-metered ruling.

### Step A — Verify bare cwd (mechanical, no handoff)

```text
# production path must pass a bare cwd into the CLI spawn
# selftest: headless_worker_selftest.test_cli_spawns_from_a_bare_cwd
```

If a spawn still inherits the repo, that is a **bug fix**, not a research topic.

### Step B — Strip the profile surface → ✅ [H2189](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2189-Opus_SanskritLexicography_pwg-headless-minimal-profile_02.08.26.md), measured 03-08-2026

Done, but **not** the way this step originally proposed. Full numbers:
[PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md).

- A dedicated minimal `CLAUDE_CONFIG_DIR` was **rejected as the lever**: −8.7 % cold-call
  `create`, against −88.1 % for the `--safe-mode` flag the CLI already ships. It also costs
  a duplicated OAuth credential and a second `ActiveCallClaim` fingerprint (same account,
  different kernel lock — two concurrent runs would bypass the one-active-call guard).
- The paid profile has **no `CLAUDE.md` of its own**. The H2158 instruction-override came
  from its **hooks**: the two arms keeping all 63 hooks could not answer a five-token
  prompt within one turn (`error_max_turns`); every hook-free arm answered in one.
- The bigger token leak is **cwd ancestry, not the profile** — see rank 1b above.
- Wired opt-in via manifest `execution.cli_safe_mode`, default OFF, with a `--help` support
  probe that fails safe to the historical argv and warns loudly. Flipping the default needs
  a canary GO on the safe-mode arm (report §5.1).
- `--bare` was NOT adopted: it forces `ANTHROPIC_API_KEY` auth, i.e. moves this lane off the
  subscription identity — a human ruling, not a cache tweak.

### Step C — Finish H2158 route A/B → [H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md)

- Prerequisite: metered `ANTHROPIC_API_KEY` (human).
- Run: `python src/pilot/h2158_route_ab.py --run --keys 2 --repeats 2`
- Byte-identity: `prefix + tail == build_prompt(...)` already asserted.
- Report must answer: (1) create→read amortisation, (2) whether CLI multi-turn
  **output** collapses on single-completion API, (3) failure-class (429 vs hang).
- **Do not** flip production route inside H2158 without human GO.

### Step D — Dual-rate pricing → ✅ [H2190](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2190-Opus_SanskritLexicography_pwg-cache-write-1h-pricing_02.08.26.md), shipped 02-08-2026

Done in [PR #1032](https://github.com/gasyoun/SanskritLexicography/pull/1032):
`cache_write_5m` / `cache_write_1h` derived from `PRICE['input']`;
`cache_write_rate(ttl)` refuses an unknown TTL rather than guessing;
`split_cache_creation()` reads the envelope's own `ephemeral_*_input_tokens`
buckets; `tally()` reports `cost` **and** `cost_unknown_at_1h` side by side, and
the H2158 harness/report import these rates instead of re-deriving `×2.0`.
Pinned by `h809_selftest.test_cache_write_is_ttl_priced_and_reconciles_with_the_vendor`,
which also asserts the old flat-5 m arithmetic **fails** to reconcile — so a
revert to a TTL-blind constant cannot pass the test written to catch it.

### Step E — Prefix reorder → ✅ [H2191](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2191-Opus_SanskritLexicography_pwg-prompt-prefix-reorder_02.08.26.md), shipped 03-08-2026 (offline only, no paid call)

`build_prompt` now emits **`preamble + translation + grammar + [nws] + cards`**
(was `preamble + grammar + translation + …`); per-card grammar stays inside
`card_block`. Reorder only — every segment is still sent, byte for byte; lean-TR
stays rejected.

**Four lanes carried the same assembly and all four were moved** (each would have
drifted independently — the reason this step was worth more than a one-line edit):

| Lane | Surface |
|---|---|
| production CLI | `headless_worker.build_prompt` |
| heal / fragment | `headless_worker.HeadlessEngine.fragment_prompt` |
| generated harness JS ×2 | `gen_opt_harness2.py` (batch + `healGroup`) |
| manifest-v2 payload | `h1209/prep_slice.prompt_common` |

Plus the two prefix computations that must agree with it byte-for-byte:
`h2158_route_ab.split_prompt` and `h2158_route_ab_report.prompt_shape`.

**Measured offline** on the committed `h1209_slice3` manifest — the cross-**window**
stable head (the leading bytes two windows with *different* grammar blocks still share)
goes **1 226 → 12 249 chars**, i.e. 4.9 % → **49.5 %** of a 24 770-char representative
prompt. Within a single window the order changes nothing (every call there already
shares the whole framework), and this nominal fixture has an empty shared `grammar`,
so its own prompt bytes are unchanged. Chars, not tokens: this sizes the **lever**, not
a billed saving — turning it into money needs the rank-2 Messages API arm or a
provider that partial-prefix-matches the CLI route.

**Gates:** `headless_worker_selftest` PASS (new
`test_h2191_prompt_is_assembled_stable_left` pins the order, single-occurrence of every
segment, the `split_prompt` byte-identity and the absence of the old JS order) ·
`window_selftest` 202/202 · `h2189_profile_ab_selftest` 12/12 ·
`h2158_route_ab.py --check` byte-identical on 3 real cards · LANG_PARITY 91 entries,
32 re-derived (SHARED/GAP stand; zero language-keyed tokens in the diff).

### Step F — Instrument every paid A/B (standing, all handoffs)

- Cache **create** vs **read** separately + TTL bucket (`1h` / `5m`).
- Wall clock + `duration_api_ms` + `api_gap_ms`.
- Sequential arms with cooldown; never parallel same-prompt cost A/Bs.
- Commit raw envelopes (not gitignored) — H2158 durability rule.

---

## 5. Harness map (where cache behaviour lives)

| Surface | File | Note |
|---|---|---|
| Production spawn + `build_prompt` | [`src/pilot/headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) | bare cwd; prompt assembly |
| Prefix stability probe | [`src/pilot/cache_prefix_stability_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_prefix_stability_probe.py) | settled unstable-prefix vs TTL |
| Messages API A/B | [`src/pilot/h2158_route_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2158_route_ab.py) | `cache_control` ttl=1h on prefix |
| Cost rates | [`src/pilot/parse_workflow_cost.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py) | `cache_write_rate('1h'\|'5m')`; `PRICE['cache_write']` is the legacy 5 m alias |
| Workflow / opt2 (forensics) | [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) | PREAMBLE + GRAMMAR + CONV_TR order |

---

## 6. Handoffs for Opus 5 (practical steps)

| Step | Handoff | Effort | Depends on |
|---|---|---|---|
| B | [H2189](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2189-Opus_SanskritLexicography_pwg-headless-minimal-profile_02.08.26.md) minimal profile | medium | bare cwd shipped |
| C | [H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md) Messages API A/B + port | hard | human API credential for Phase 1 API arm |
| D | ✅ [H2190](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2190-Opus_SanskritLexicography_pwg-cache-write-1h-pricing_02.08.26.md) dual-rate 1 h pricing — **shipped 02-08-2026**, [PR #1032](https://github.com/gasyoun/SanskritLexicography/pull/1032) | medium | none |
| E | ✅ [H2191](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2191-Opus_SanskritLexicography_pwg-prompt-prefix-reorder_02.08.26.md) stable-left prefix reorder — **shipped 03-08-2026** | medium | none (independent of API port) |

Recommended launch order: ~~**H2190** (offline)~~ ✅ done → ~~**H2191** (offline)~~ ✅ done →
**H2189** (small paid A/B) → **H2158** (needs credential + human GO for route flip).

### Starters

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H2190-Opus_SanskritLexicography_pwg-cache-write-1h-pricing_02.08.26.md and execute it.
```

🔴 EXECUTED: [H2191-Opus_SanskritLexicography_pwg-prompt-prefix-reorder_02.08.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2191-Opus_SanskritLexicography_pwg-prompt-prefix-reorder_02.08.26.md)

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H2189-Opus_SanskritLexicography_pwg-headless-minimal-profile_02.08.26.md and execute it.
```

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md and execute it.
```

Opus 5 (`claude-opus-5`) · worktree off SanskritLexicography `origin/master` ·
read this playbook first.

---

## 7. What “done” looks like for the programme

- [x] Single playbook of record (this file)
- [x] Bare cwd in production spawn path
- [ ] Minimal profile measured + wired or rejected with numbers
- [ ] H2158 two-arm A/B complete + human GO/NO-GO on route
- [ ] Cost tools never silently price 1 h writes at 5 m rates
- [x] Prefix order stable-left; LANG_PARITY SHARED note if both surfaces touch (H2191, 03-08-2026)
- [ ] RUN_FREQ_MAX + PIPELINE_HISTORY point here (no third narrative)

---

_Dr. Mārcis Gasūns_
