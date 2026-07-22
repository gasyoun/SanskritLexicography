# H1517 — PWG→RU stripped-config cost cut + w1 3-key live economy sample (c4)

_Created: 22-07-2026 · Last updated: 22-07-2026_

**Executor:** Opus 4.8 (`claude-opus-4-8`). Generation model (translation calls): Sonnet 5 (`claude-sonnet-5`), billed through the **c4** subscription profile.
**Discipline:** OFFLINE fixtures + a **scratch** store/coordinator/TM, **no promotion**, no canonical-store write, no TM rebuild. Real committed PWG portraits (H1339 bench fixtures `fx1` = `ABAsa`/`AKu`/`ARava`) drove a real `headless_worker` call.

## 1. The cost lever — a stripped `CLAUDE_CONFIG_DIR`

Every `claude -p` call the pipeline makes (health probe **and** translation — identical argv, [`headless_worker.py:431`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)) loads the profile's full context: **9 skills + 172 commands + plugins + the project CLAUDE.md stack** (SanskritLexicography + org). MCP was already empty. That context is **~76.7 K cache-creation tokens** the model never needs for translation.

**A/B on the identical ~6.8 KB health prompt (c4):**

| | Full config | **Stripped config** | Δ |
|---|---|---|---|
| cache-creation tokens | 76,659 | 21,809 | **−71.6%** |
| cost / cold call | $0.4648 | $0.1597 | **−65.6%** |
| gate result | `{"ok":false}` → NO-GO | `{"ok":true}` → **PASS** | fixed |

**Mechanism:** point `CLAUDE_CONFIG_DIR` at a dir holding **only** the auth files (`.credentials.json` + `.claude.json` + `settings.json`) — no `skills/`, `commands/`, `plugins/`, `CLAUDE.md` — add `--strict-mcp-config`, and run from a neutral CWD (no project CLAUDE.md discovered). The heavy context was **both** the cost driver **and** the cause of the `{"ok":false}` gate failure (the model stopped following the exact instruction under 76.7 K of competing context); a clean context restores instruction-following, so **c4 passes gate-0 stripped**. The strip is strictly better: cheaper **and** healthier.

Residual ~54 K (21.8 K created + 32.5 K read) is the Claude Code agent's own base system-prompt + built-in tool schemas — inherent to billing through the CLI (a raw Messages-API call would drop it, but there is no API key on file).

## 2. w1 3-key live sample — real economy (c4, stripped, scratch store, no promotion)

`coordinator prepare … --config-dir <stripped>` binds the stripped fingerprint into the manifest; `headless_worker … --only-profile c4` inherits the cut. Result: **3/3 cards translated OK.**

| Metric | Value |
|---|---|
| cards | 3 / 3 OK (`ABAsa`, `AKu`, `ARava`) |
| headless attempts | 2 — `b0` **malformed_output** (73.3 s) → `b0.retry1` **success** (71.3 s) |
| success-call latency | 71.3 s for the 3-card batch ≈ **23.8 s / card** |
| wall incl. retry | 145 s ≈ **48 s / card** |
| pipeline-accounted cost | **$0.4095** (success call, `priced_calls:1`) = **$0.137 / card** |
| real billed incl. malformed retry | ≈ **$0.76** (retry ~same token profile, uncounted) ≈ **$0.25 / card** |
| success-call tokens | in 2 · out 6,923 · cache-create 47,232 · cache-read 33,152 · subagent 87,309 |

**Strip impact on the real run:** the ~55 K CLAUDE.md/skills overhead measured in §1 would be *added* on the full config, so the full-config per-card cost is roughly **double** — the strip approximately halves it here too.

**Quality:** markup invariant preserved (Sanskrit `{#…#}`, `<lex>`, `<ls>`, `<bot>` untouched; only German prose → Russian). E.g. `ābhāsa` "Glanz, Licht, Farbe, Aussehen" → "блеск, свет, цвет, облик"; `ākhu` "Maus, Ratze" → "мышь, крыса".

## 3. Caveats

- **Malformed-retry economy risk.** 1 of 1 batch was malformed on first attempt (retry succeeded), **doubling** the effective cost/latency. n=1 batch — not statistically strong, but at scale a high first-try malformed rate materially changes economy; worth a dedicated malformed-rate measurement before a paid medium50 window.
- **Cost accounting under-counts retries.** `summary.usage.observed_cost_usd` priced only the successful call (`priced_calls:1`); the malformed attempt billed but its usage wasn't parsed. Real billed > accounted.
- **Not a promotion.** Scratch store; nothing reached the canonical store. The medium50 gate discipline (fresh gate-0 PASS before a paid window) is unchanged — this sample used the stripped route which *does* pass gate-0.
- **c1/c5 = rate_limit, c6 = auth** at 15:02Z; c4 is the working profile.

## 4. Recommendation

Adopt the stripped-config route for the pwg_ru **production** translation calls (prepare with `--config-dir <stripped>`): it cut cold-call cost ~66%, roughly halves real per-card cost, and fixes the gate `{"ok":false}`. Next: measure the first-try malformed rate over a larger batch before authorizing a paid medium50 window.

_Dr. Mārcis Gasūns_
