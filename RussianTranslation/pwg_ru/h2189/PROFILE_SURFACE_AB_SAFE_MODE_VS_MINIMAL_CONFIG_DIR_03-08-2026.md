# H2189 — the headless PROFILE surface: `--safe-mode` vs a minimal `CLAUDE_CONFIG_DIR`

_Created: 03-08-2026 · Last updated: 03-08-2026_

**Handoff:** [H2189](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2189-Opus_SanskritLexicography_pwg-headless-minimal-profile_02.08.26.md)
(**Opus 5**) — PWG headless minimal `CLAUDE_CONFIG` profile A/B (strip the global prefix tax).
**Executed by:** Opus 5 (`claude-opus-5[1m]`), Claude Code.
**Playbook of record:** [PROMPT_CACHING_PWG_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md) §3 rank 1 · §4 Step B.
**Parents:** [H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md) · [Uprava FINDINGS §284](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).

**Verdict: GO for `--safe-mode`, opt-in and default OFF. REJECT of the dedicated minimal
`CLAUDE_CONFIG_DIR` as the primary lever** — it was the handoff's proposed mechanism and it
measured 4× weaker than a flag the CLI already ships, while costing a duplicated OAuth
credential and a second `ActiveCallClaim` fingerprint.

---

## 1. What the profile surface actually is

`bare_cli_cwd()` (H2158) removed **project** context from every paid spawn. Four channels
survive it, and only the first is visible by opening the profile directory:

1. **User memory** — a `CLAUDE.md` the CLI auto-discovers.
2. **Skills / commands / agents** — advertised to the model by name and description.
3. **Hooks** — `SessionStart` / `UserPromptSubmit` inject text straight into the conversation.
4. **Plugins / MCP** — more tool and skill definitions on the same budget.

Measured offline on the operator box with
[`h2189_min_profile.py --inventory`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2189_min_profile.py):

| Channel | Paid profile (`claude4`) | Minimal twin |
|---|---:|---:|
| profile `CLAUDE.md` | 0 B | 0 B |
| `settings.json` | 13 340 B | 2 B |
| hooks (total / injecting) | 63 / 9 | 0 / 0 |
| skills · commands · agents · plugins · references | 57 · 226 · 31 · 5 · 13 | 0 |
| MCP servers | 0 | 0 |

### 1.1 The finding the handoff did not anticipate — `bare_cli_cwd()` still leaks ~33 KB

The paid profile has **no `CLAUDE.md` of its own**, so the H2158 symptom (a model refusing
its task, citing an operator rule) could not have come from the config directory. It comes
from **cwd ancestry**. `bare_cli_cwd()` walks up rejecting an ancestor that carries a bare
`CLAUDE.md` or a `.git` — but **not** one carrying `.claude\CLAUDE.md`. Its directory is
`%TEMP%\pwg_ru_cli_cwd`, i.e. *under the Windows user profile*, which is exactly where the
operator's global memory lives:

```text
ancestor scan from: C:\Users\user\AppData\Local\Temp\pwg_ru_cli_cwd
  file      31625 bytes  C:\Users\user\.claude\CLAUDE.md
  dir        1154 bytes  C:\Users\user\.claude\rules
  total injectable: 32779 bytes
```

That is ~33 KB reaching **every paid call** since H2158 shipped, unnoticed because the
directory itself is empty and an `ls` of it shows nothing. A minimal `CLAUDE_CONFIG_DIR`
does not fix this at all — it changes the profile, not the ancestry.

---

## 2. Method

Five arms, each isolating **one** lever against the production baseline, plus one declared
stack. All sequential with a cooldown, never parallel — two same-prompt calls in flight
contaminate each other's cache accounting.

| Arm | Config dir | Extra flag | cwd |
|---|---|---|---|
| `paid` (baseline) | `claude4` | — | `bare_cli_cwd()` |
| `minimal` | `claude4-min` | — | `bare_cli_cwd()` |
| `safe` | `claude4` | `--safe-mode` | `bare_cli_cwd()` |
| `clean_cwd` | `claude4` | — | ancestry-clean (`D:\`) |
| `safe_clean` | `claude4` | `--safe-mode` | ancestry-clean |

**`--bare` was deliberately not an arm.** It strips the same context, but its own help
states Anthropic auth becomes strictly `ANTHROPIC_API_KEY`/apiKeyHelper and OAuth is never
read — i.e. it moves this lane off the subscription identity onto metered billing. That is
the subscription-vs-metered question [PROMPT_CACHING_PWG_RU](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md) §4
reserves for a human, not a side effect to smuggle in behind a cache optimisation. Pinned by
`h2189_profile_ab_selftest.test_bare_is_never_an_arm`.

Model `claude-sonnet-5`. Manifest [`h1209_slice3.manifest.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1209_slice3.manifest.json)
— the same one H2158 measured, so the numbers compose. Raw envelopes committed under
[`pwg_ru/h2189/raw/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2189/raw).

---

## 3. Trivial phase — the scaffolding, isolated

`--max-turns 1` on a five-token prompt. It translates nothing, so every token it bills **is**
the scaffolding. Two calls per arm; `#1` is cold, `#2` is three seconds later.

| Arm | # | create | read | out | wall ms | api ms | USD (1h write) | outcome |
|---|--:|--:|--:|--:|--:|--:|--:|---|
| `paid` | 1 | 39 532 | 28 882 | 4 | 19 877 | 5 287 | 0.2459 | **`error_max_turns`** |
| `paid` | 2 | 0 | 68 414 | 4 | 36 662 | 10 541 | 0.0206 | **`error_max_turns`** |
| `minimal` | 1 | 36 092 | 28 882 | 4 | 16 374 | 9 837 | 0.2253 | ok |
| `minimal` | 2 | 0 | 64 974 | 4 | 22 121 | 28 672 | 0.0196 | ok |
| `safe` | 1 | **4 712** | 28 882 | 4 | 17 812 | 12 721 | **0.0370** | ok |
| `safe` | 2 | 0 | 33 594 | 4 | 12 207 | 5 683 | 0.0101 | ok |
| `clean_cwd` | 1 | 26 780 | 28 882 | 4 | 22 220 | 8 315 | 0.1694 | **`error_max_turns`** |
| `clean_cwd` | 2 | 0 | 55 662 | 4 | 34 463 | 21 157 | 0.0168 | **`error_max_turns`** |
| `safe_clean` | 1 | 4 704 | 28 882 | 4 | 19 332 | 23 038 | 0.0370 | ok |
| `safe_clean` | 2 | 0 | 33 586 | 4 | 12 612 | 14 814 | 0.0101 | ok |

Cold-call `create` against the baseline:

| Lever | create | Δ vs `paid` |
|---|--:|--:|
| minimal `CLAUDE_CONFIG_DIR` | 36 092 | **−8.7 %** |
| ancestry-clean cwd | 26 780 | **−32.3 %** |
| `--safe-mode` | 4 712 | **−88.1 %** |
| `--safe-mode` + clean cwd | 4 704 | −88.1 % |

**Two independent taxes, and they have different causes.**

* The **token** tax is dominated by *memory files*. The ancestor `CLAUDE.md` (−12 752
  tokens) outweighs everything inside the config directory (−3 440). `--safe-mode`
  subsumes both, which is why stacking a clean cwd on top of it buys 8 tokens.
* The **turn** tax is caused by *hooks*. `paid` and `clean_cwd` — the two arms that keep the
  profile's 63 hooks — could not answer `Reply with exactly: ok` within one turn and died
  `error_max_turns`. `minimal` and both `safe` arms answered in one. This reproduces the
  correctness half of the H2158 complaint and localises it: the injected instruction arrives
  through **hooks**, not through a profile `CLAUDE.md` (there isn't one).

---

## 4. Card phase — the production prompt

The real production surface: `build_prompt(manifest, ['nakzatra'])`, 24 770 chars, the
manifest's own `--json-schema`, `--permission-mode plan`, argv-for-argv as
`HeadlessEngine.call` builds it.

| Arm | create | read | in | out | wall ms | api ms | USD (1h write) |
|---|--:|--:|--:|--:|--:|--:|--:|
| `paid` | 60 140 | 118 321 | 4 | 19 718 | 254 418 | 227 629 | **0.6921** |
| `safe` | 18 615 | 29 667 | 2 | 10 040 | 115 373 | 124 926 | **0.2712** |
| **Δ** | **−69.0 %** | −74.9 % | — | **−49.1 %** | **−54.7 %** | −45.1 % | **−60.8 %** |

**The baseline does not fit inside production's own ceiling.** The first `paid` attempt was
run at the harness default of 300 s — `HARD_TIMEOUT_MS`, the production ceiling — and
**timed out**. The 254 s figure above comes from a re-run at H2158's 600 s *diagnostic*
ceiling. So on this card the baseline straddles the ceiling that kills calls, while `safe`
finishes in 115 s with 2.2× headroom. No production ceiling was raised to obtain this; the
600 s value exists only inside the measurement rig.

### 4.1 The output halving is overhead, not lost card

−49 % output tokens is the kind of saving that killed lean-TR, so it was checked rather
than banked:

| | `paid` | `safe` |
|---|--:|--:|
| records | 7 | 7 |
| senses | 13 | 13 |
| senses carrying Russian | 13/13 | 13/13 |
| Russian volume | 1 940 chars | 1 956 chars (+0.8 %) |
| German verbatim | 2 163 chars | 2 120 chars (−2.0 %) |
| `stratum` annotations | 2 | 5 |
| `differentia` annotations | 3 | 6 |
| `{Tn}` masked-span token **set** | — | **identical** |
| literal `SAN-LOSS` / `UNMAPPED` | none | none |

Checked with the project's own single-sourced regexes (`promote_final_cards.TN_RE`, the
`canary_gate.LITERAL_MARKERS` list), not with a private heuristic. The `{Tn}` token *set* is
identical across arms — no masked span was dropped or invented — and `safe` carried *more*
stratum/differentia annotation, not less. The halved output is CLI agent-loop overhead
disappearing, which answers in the affirmative the question
[PROMPT_CACHING_PWG_RU](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md) §1.5
left open ("unless multi-turn loop overhead collapses").

Neither arm leaked operator vocabulary (`handoff`, `GTD`, `NEXT ISSUE`, …) into its answer,
and both returned schema-compliant cards.

### 4.2 One divergence reported, not buried

The free-text `tag` vocabulary differed between the two samples — `paid` produced
`tail / name / xref / sch-name / pwkvn-name`, `safe` produced
`cross-ref / addendum-1 / addendum-crossref / SCH-Nachtrag / PWKVN-crossref` — and a
whitespace shift appeared next to a masked token (`{T1}¦` → `{T1} ¦`). The schema types
`tag` as a bare non-empty string, so both validate.

**This is n=1 per arm and therefore unattributed:** it may be `--safe-mode`, or ordinary
sampling variation between two independent generations of the same card. It is the single
reason the wiring below ships default OFF rather than flipped.

---

## 5. What shipped

**Opt-in, default OFF**, in [`headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py):

* `execution.cli_safe_mode: true` in the manifest requests it — auditable, travels with the
  run receipt, and absent from every existing manifest, so no current behaviour changes.
* `cli_supports_safe_mode()` probes `--help` once per binary and **fails safe**: a
  requested-but-unsupported flag would die in the CLI's own argument parsing on *every*
  spawn, turning a cost optimisation into a total outage. Unsupported ⇒ historical argv.
* The downgrade is **loud** on stderr, naming H2189: a run that believes it is stripping the
  profile but is not would report these savings while paying the full tax.
* Resolved **once** in the constructor, so a mid-run CLI swap cannot leave half a window's
  calls carrying the flag.

Pinned by four tests in
[`headless_worker_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker_selftest.py):
default-OFF, carried-when-requested (with the schema and `plan` posture asserted to survive),
loud degradation, and an ancestry measurement that *reports* the ~33 KB rather than
asserting it away.

**LANG_PARITY: SHARED.** The flag changes which profile context the CLI child loads — a
property of the spawn, never of the target language. Five drifted entries re-derived and
re-stamped; the added lines carry no language-keyed token.

### 5.1 What would justify flipping the default

A canary GO receipt (`canary_gate.py`, via [`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md))
produced **on the safe-mode arm**, plus enough real cards to rule the §4.2 `tag` divergence
in or out. Until then an operator opts in per manifest.

---

## 6. Residual risks and untested levers

| Item | Status |
|---|---|
| `tag` vocabulary divergence (§4.2) | **Open**, unattributed at n=1 — the reason for default OFF |
| `bare_cli_cwd()` ancestry leak (§1.1) | **Open as its own defect.** `--safe-mode` masks it by disabling memory discovery, but the helper still hands out a directory it believes is bare. Any lane not using `--safe-mode` still pays ~33 KB/call |
| A dedicated minimal profile dir | **Rejected as the primary lever** (−8.7 %). Built and kept as a diagnostic; if ever wired it must be its own roster slot — it fingerprints differently, so `ActiveCallClaim` takes a *different* kernel lock while billing the *same* account, and two concurrent runs would bypass the one-active-call guard |
| `--exclude-dynamic-system-prompt-sections` | **Untested.** Its help scopes it to cross-*user* cache reuse; a sixth arm was not worth the spend. Not measured-and-rejected — simply not measured |
| Cross-call amortisation (§7) | **Contradicts standing truth**, flagged below |

---

## 7. Contradiction to log — call #2 amortised in every arm

[PROMPT_CACHING_PWG_RU](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md) §1
standing truth #1 states that a one-shot CLI subprocess **cannot** amortise its own system
prompt: v1.127.0 measured two identical back-to-back calls each re-creating ~49 k.

Every arm here did the opposite. Call #2 created **zero** and its `read` equalled call #1's
`create + read` **exactly**, in all five arms:

| Arm | create#1 + read#1 | read#2 |
|---|--:|--:|
| `paid` | 39 532 + 28 882 = 68 414 | 68 414 |
| `minimal` | 36 092 + 28 882 = 64 974 | 64 974 |
| `safe` | 4 712 + 28 882 = 33 594 | 33 594 |
| `clean_cwd` | 26 780 + 28 882 = 55 662 | 55 662 |
| `safe_clean` | 4 704 + 28 882 = 33 586 | 33 586 |

Same prompt shape, same seconds-apart cadence, same 1 h TTL bucket as v1.127.0 — so this
looks like a genuine CLI behaviour change, not a methodology difference. It is **not**
rewritten into the playbook here: this run was not designed to test amortisation, and
standing truth #1 carries consequences for the whole rank-2 Messages-API case. Logged as a
contradiction for a dedicated re-measurement.

---

## 8. Reproduce

```text
python src/pilot/h2189_min_profile.py --inventory
python src/pilot/h2189_min_profile.py --scan-cwd "%TEMP%\pwg_ru_cli_cwd"
python src/pilot/h2189_profile_ab_selftest.py          # offline, 12 tests
python src/pilot/h2189_profile_ab.py --check           # offline, spends nothing
python src/pilot/h2189_profile_ab.py --run --phase trivial --repeats 2
python src/pilot/h2189_profile_ab.py --run --phase card --keys 1 --repeats 1 --arms paid,safe
```

Spend for everything in this report: **$1.7551** across 12 cost-evaluable calls, plus one
timed-out `paid` card call whose cost is **unevaluable** — 13 paid spawns in total. The
timeout is reported as unevaluable rather than as `$0`, which is the same fail-closed rule
`call_reservation` applies in production: a paid call that produced no readable envelope
never reads as free.

_Dr. Mārcis Gasūns_
