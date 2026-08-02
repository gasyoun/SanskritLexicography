# PWG→RU route A/B — Messages API with a cached prefix vs. the CLI-headless lane

_Created: 02-08-2026 · Last updated: 02-08-2026_

**Handoff:** [H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md) ·
**Model:** Opus 5 (`claude-opus-5`) ·
**Parents:** [H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md) ·
[H2152](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2152-Opus_RussianTranslation_c4-quota-call-shape-audit_02.08.26.md)

**Verdict: INCONCLUSIVE on the route switch — and the question itself needs rewriting.**
The API arm could not run (no credential on this machine, §5). But the CLI arm returned a
result that changes what the decision is about: **output tokens, not cache writes, are the
majority of a pwg_ru call's cost and the reason it breaches the ceiling.** H2158 was framed
around a ~$0.30/call scaffolding tax. That tax is real and measured at $0.287 — and it is
*the smaller half* of a $0.80 call.

---

## 1. What was measured

Both arms were to send byte-identical prompts from
[`build_prompt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L254);
the harness asserts that identity and refuses to measure without it. Real cards from the
committed [`h1209_slice3.manifest.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1209_slice3.manifest.json)
(`nakzatra`, `sarvatra`) — no invented prompt text, which is the H2011 trap.

### 1.1 CLI-headless, real card (`nakzatra`)

| run | ceiling | wall clock | cache create | cache read | output | outcome |
|---|---:|---:|---:|---:|---:|---|
| ×3 (2× `nakzatra`, 1× `sarvatra`) | 300 s | 300.0 s | — | — | — | **killed, no envelope, cost unevaluable** |
| ×1 `nakzatra`, diagnostic ceiling | 600 s | **375.0 s** | 46 117 | 35 220 | **34 215** | **completed, `ok`** |

The lane was never hung. It is **25 % slower than the 300 s ceiling allows**, so it dies at
the wall every time — the same shape H2011 recorded as 12 of 16 calls killed. Raising
`HARD_TIMEOUT_MS` is explicitly **not** the recommendation (§6); the 600 s run was a
diagnostic to separate *hung* from *slow*, and it is not a proposed production value.

### 1.2 Where the $0.80 actually goes

Repriced from [`parse_workflow_cost.PRICE`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py#L28)
so both routes are compared on one rate table:

| component | tokens | rate ($/Mtok) | cost | share |
|---|---:|---:|---:|---:|
| cache **create** | 46 117 | 6.00 (1-hour TTL) | $0.2767 | 34.6 % |
| cache **read** | 35 220 | 0.30 | $0.0106 | 1.3 % |
| **output** | **34 215** | **15.00** | **$0.5132** | **64.1 %** |
| | | | **$0.8005** | |

**The Messages API cannot touch the 64 %.** Output tokens bill identically on both routes.
The port addresses the 34.6 % cache-write line and nothing else — unless the output volume
is itself an artifact of the route (§4), which is exactly what the missing arm would settle.

**Output dominates *because Phase 0 worked*.** H2011's live-gate card, measured the same day
but **before** the bare-cwd change, decomposed to `$0.8660853` with **cache creation at
73.5 % (106 072 tokens)**:

| | H2011 (pre-bare-cwd) | H2158 (post-bare-cwd) | change |
|---|---:|---:|---:|
| cache create (tokens) | 106 072 | 46 117 | **−57 %** |
| cache create (share) | 73.5 % | 34.6 % | — |
| total per card | $0.8661 | $0.8005 | −7.6 % |

So this is not a contradiction of [#986](https://github.com/gasyoun/SanskritLexicography/pull/986)/H2011's
"cache creation is most of the cost" — it is what that finding looks like *after* the fix
they motivated. The cache half was cut by more than half; what remains standing is output.
Note the total moved only −7.6 %: **cutting creation 57 % bought 7.6 %**, because output was
always underneath. That is the clearest single argument for reordering the backlog (§6).

### 1.3 Rate-table correction (applies beyond this handoff)

`PRICE['cache_write'] = 3.75` is the **5-minute** cache-write rate (1.25× base). Every write
this lane produces lands in `ephemeral_1h_input_tokens`, and the 1-hour TTL bills at **2×
base = $6.00/Mtok**. Pricing 1h writes at the 5m rate understates the CLI lane by 1.6×.

**The prose already knows this; the code constant does not.** H2011's changelog entry and
`RUN_FREQ_MAX.md` both price cache creation at $6/M and explicitly note the write is
`ephemeral_1h` — but `PRICE`, the table every cost script imports, still carries 3.75 with no
TTL dimension. So a hand-written memo gets it right while anything computed from `PRICE`
silently under-reports. This harness emits both figures side by side
(`cost_usd_1h_write`, `cost_usd_5m_write`) rather than picking one; the durable fix is to
give `PRICE` a TTL-aware write rate so the two cannot diverge again.

### 1.4 Trivial-call floor — the scaffolding tax, isolated

Two five-token calls (`Reply with exactly: ok`), bare cwd, same profile:

| call | wall | create | read | output | envelope cost |
|---|---:|---:|---:|---:|---:|
| `--max-turns 1` | 35.9 s | 37 769 | 28 882 | 4 | **$0.2353** |
| clean | 63.8 s | 126 | **133 302** | 1 070 | $0.0568 |

Two things fall out. **A five-token prompt costs $0.235** — that is the per-call floor no
card can go below on this route. And the second call **read 133 302 cached tokens instead of
re-creating them**, cutting cost 4.1×: after the Phase-0 bare-cwd change the prefix *does*
sometimes carry across invocations, which softens v1.127.0's "nothing carried over". The two
calls were not an identical pair (`--max-turns` differed), so this is a signal to re-test,
not a refutation.

### 1.5 Bare cwd strips project context, not profile context

The clean trivial call **refused its own instruction**, citing a rule about emitting a
`⭐ Next: <action> (<owner>, <repo>)` line — a convention from the *profile's* global
`CLAUDE.md`, not from this repo. [`bare_cli_cwd()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L82)
removes repo context; it cannot remove the config dir the paid lane is bound to. So every
pwg_ru call still carries the operator's global instruction set — ~133 k tokens of prefix
against a ~6–7 k-token translation prompt, and instructions with enough force to override an
explicit task directive. **This is a correctness exposure, not only a cost one.** Kin but
distinct: [FINDINGS §237](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) covers the
same `CLAUDE_CONFIG_DIR` profile root failing to wire *hooks*; this is that root's *prompt
content* reaching a headless translation call, which no current entry records.

---

## 2. Prompt shape (offline, exact — no call required)

| card | cacheable prefix | volatile card block | total | cacheable share | German words |
|---|---:|---:|---:|---:|---:|
| `nakzatra` | 12 249 | 12 521 | 24 770 | 49 % | 413 |
| `sarvatra` | 12 249 | 8 961 | 21 210 | 58 % | 189 |

Mean **22 990 prompt chars / 301 German words** per card ≈ **5 700–7 700 prompt tokens**.
Against the CLI's ~133 k-token prefix, **the translation task is ~5 % of what the route
sends.** Note also that only ~half the *task* prompt is cacheable — the card block is
per-card volatile — so an API port's cache win is bounded well below "the whole prompt".

---

## 3. Failure-class comparison

| | CLI-headless | Messages API |
|---|---|---|
| Ceiling breach | **silent kill, no envelope, cost unevaluable** (3/3 here) | n/a — HTTP request either returns or raises |
| Rate limit | hangs to the ceiling, indistinguishable from slow ([FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)) | `429` + `retry-after`, caught as `http_429` |
| Overload / 5xx | same undifferentiated hang | typed status code |
| Diagnosis cost | one 300 s burn per attempt | immediate |

This axis is **not** inconclusive. The CLI route destroys the failure signal; the API route
returns a status code. The harness already classifies both ([`h2158_route_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2158_route_ab.py)).
Separating *hung* from *slow* took a deliberate 600 s diagnostic run here — on the API route
it would have been a header.

---

## 4. Campaign projection — a range, with its assumptions exposed

**Assumptions** (attack these, not the arithmetic): remaining bulk **140 000 German words**
(H2152 §6.6); cards resemble this manifest at **301 words/card → ≈ 465 cards**; **one call
per card** (H2152: HOLD one-card); **Sonnet 5 list rates**, introductory $2/$10 promo *not*
applied, matching `PRICE`'s basis; **zero retries or heals**. Every real campaign has both,
so all figures are **floors**.

| route | basis | $/card | ≈465-card campaign |
|---|---|---:|---:|
| CLI-headless | **MEASURED**, n=1 completed | $0.8005 | **≈ $372** |
| Messages API, output unchanged | modelled | ≈ $0.523 | ≈ $243 |
| Messages API, output single-completion | modelled | ≈ $0.07 | ≈ $33 |

The API band is **$33–$243, a 7× spread**, and the spread is *entirely* the unmeasured
output question: the CLI runs a multi-turn agent loop whose 34 215 output tokens accumulate
across turns, whereas a Messages API call is one completion. If most of those 34 k tokens are
loop overhead, the port is transformative; if the translation genuinely needs them, the port
saves ~35 %. **Nothing in this report can distinguish those two, and no amount of reasoning
substitutes for the call.** That is the whole remaining value of the API arm — and it is a
sharper question than the one H2158 set out to ask.

For scale: **$372 is the CLI floor**, against a subscription that currently produces this
work at no marginal invoice but cannot finish a card inside its own ceiling.

---

## 5. Why the A/B is incomplete — one concrete prerequisite

The API arm needs a credential. Measured on this machine: `ANTHROPIC_API_KEY` and
`ANTHROPIC_AUTH_TOKEN` are both unset, and the `ant` CLI is absent, so no OAuth profile can
be resolved either. The harness **refuses** to run one-armed rather than emit a half-table
that reads like an A/B.

This is a human prerequisite, not an engineering gap: obtaining a metered API credential is
itself part of the subscription-vs-metered decision H2158 is blocked on. Once one exists,
the arm is one command (§7) and needs no code change.

---

## 6. Recommendation

**NO-GO on switching the bulk route today** — not because the API route looks worse, but
because the decisive quantity was never measured, and the measured evidence says the port
was aimed at the smaller half of the problem.

Ranked, and deliberately *not* what the handoff assumed:

1. **Cut output tokens.** 64 % of cost and the entire ceiling breach. Untouched by any route
   change and never examined by H2011/H2152, both of which chased input-side cache. This is
   now the highest-value open question in the arc.
2. **Run the API arm** (§7) — one call, and it converts the $33–$243 band into a number.
   Cheap, and it also answers (1) by revealing single-completion output volume.
3. **Investigate profile-context injection** (§1.5) — a correctness exposure, plus a large
   share of the ~133 k prefix.
4. **Do not raise `HARD_TIMEOUT_MS`.** A 375 s card fits a 300 s ceiling only by shrinking
   output, which is item 1. Raising the wall to fit the work is the weaken-a-guard move this
   whole arc exists to refuse.

Explicitly **not done here**, per the handoff's own fail conditions: no production route
flip, no bulk campaign, no ceiling raise, no re-litigation of the settled H2152 call-shape
conclusion.

---

## 7. Reproduce

```
python src/pilot/h2158_route_ab.py --check                      # offline: auth + byte-identity
python src/pilot/h2158_liveness_probe.py --timeout 120          # is the lane alive
python src/pilot/h2158_route_ab.py --run --arms cli --keys 1 --repeats 1 --timeout 600
python src/pilot/h2158_route_ab.py --run --keys 2 --repeats 2   # both arms, once a key exists
python src/pilot/h2158_route_ab_report.py                       # regenerate the tables
```

Raw envelopes are **committed** under [`pwg_ru/h2158/raw/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2158/raw)
and [`raw_slow/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2158/raw_slow),
not gitignored — the durability gap that made the pre-H2095 gate series undecomposable.

## 8. Evidence checklist

- [x] A/B table, same cards, per-card cost + wall clock + cache read/create — **CLI arm only**
- [x] Full-campaign projection as a range with assumptions written out
- [x] Failure-class comparison — settled in the API route's favour
- [ ] GO/NO-GO on the route switch — **INCONCLUSIVE**; interim NO-GO with a reordered backlog
- [x] Raw envelopes committed, not gitignored

---

_Dr. Mārcis Gasūns_
