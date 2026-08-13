# PWG→RU drain — what actually stops it, measured after blanket spend authorization

_Created: 13-08-2026 · Last updated: 13-08-2026_

**Handoff:** [H2639](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2639-Opus_SanskritLexicography_pwg-translation-bottleneck-census-post-authorization_13.08.26.md) · Model: Opus 5 (`claude-opus-5`) · zero paid calls in this pass

A human authorized spend without reservation on 13-08-2026. This census answers the
question that authorization raises: **with money no longer a gate, why is PWG still not
being translated?** It is written against the live artifacts, not against the going
account, because three of the five blockers below turned out to be misfiled.

---

## The short answer

**Money was never the binding constraint, and the project's own cost model says so in
writing.** [PILOT_COST.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PILOT_COST.md)
§6.1: translation runs on the Claude **Max** subscription, so the marginal money cost of a
card is **≈ $0**; the API dollar figures in that file exist only to size a *reference* and
an *alternative*. Its closing line is explicit — *"the binding constraint stays the Max
weekly token quota and editor-hours, not USD."*

So authorization unlocks three specific sealed things (below) and one genuine strategic
lever (DeepSeek bulk). It does **not** restart the drain, because the drain is stopped by a
gate ruling, a per-call wall-clock ceiling, and an unmeasured quota — none of which take
payment.

---

## Where the dictionary actually stands

| Quantity | Value | Source |
|---|--:|---|
| Assembled headword cards (the universe) | **120 172** | `src/assembled_cards.jsonl` |
| TEI / OntoLex entries exported | **120 173** | `validate_interop` |
| RU store rows (sense-level, local, gitignored) | **11 603** | `src/pwg_ru_translated.jsonl` |
| Machine-ok rows in store | **11 603** | `validate_review` |
| G5 review decisions recorded | **5** / 11 163 | `preflight_remaining_gates.py` |
| Print-ready rows | **3** | same |
| G6 human gold complete | **0** / 320 | same |
| G7 double review complete | **0** / 80 | same |
| Immutable edition cut (G10) | **none** | same |
| Tier-B priority remainder (H1339) | **~5 580** unique (701 verb · 4 757 nominal-PWG · 122 no-PWG) | [pwg_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) |

Read the two scopes separately or the percentage misleads: against the **whole book** the
store covers under 10 % of cards; against the **H1339 Tier-B priority slice** the remainder
is ~5 580 units, which is a very different-sized job.

The gate snapshot moved this pass — G5 decisions **0 → 5**, print-ready **0 → 3**,
machine-ok rows **11 163 → 11 603**. The committed snapshot had been stale;
`release/gate_status_snapshot.{md,json}` is gitignored and local-only, so it only advances
when someone regenerates it on the box that holds the store.

---

## Bottleneck 1 — the c4 paid lane is administratively STOPPED, and money cannot lift it

`/pwg-live-gate`'s own retry policy stops the lane after **3 consecutive NO-GO days**. That
fired on **03-08 · 05-08 · 06-08**, and it has not been probed since. A prior GO never
authorizes resumption: the lane needs a **fresh health PASS** before any canary or bounded
window, and the only thing that produces one is running the probe.

The three NO-GOs were three *different* deaths, correctly refused as one class:

| Day | Signature | Reading |
|---|---|---|
| 03-08 | CLI returned `duration_ms` 277 894 ms, 1 146 B | route stall |
| 05-08 | 300 099 ms wall, 0 output bytes, no `duration_api_ms` | **our own kill** at `HARD_TIMEOUT_MS` + teardown |
| 06-08 | refused up front, `rate_limit`, 18 574 ms / 830 B, `$0.00` | up-front refusal, 4.3× *under* the ceiling |

**The hypothesis that justified the stop is now refuted.** The 12-08 forensics
([PR #1659](https://github.com/gasyoun/SanskritLexicography/pull/1659)) recovered the child
transcripts — they were never lost, they were written under the `claude1` profile on `D:`,
not `~/.claude` — and every failing call carries an explicit API error: one
`529 Overloaded (server-side, usually temporary)` plus five stream truncations, inside a
29-minute band bounded by clean calls on both sides. **No rate-limit or usage-limit message
appears anywhere in the window.** The weekly-cap signature that the lane stop leaned on is
absent from the evidence.

That does not automatically re-open the lane — the stop clause is written against NO-GO
*days*, not against a cause — but it removes the reason to believe another probe is
futile. Cost of finding out: **~$0.55**, ration ≤2 attempts per UTC day, ≥6 h apart.

**Do not respond to this by re-deriving the ceiling.** The clause's default remedy is an
H2138 re-fit, and it is wrong for all three shapes: 05-08 produced no number to fit (a
0-byte kill is the constant plus teardown, so fitting to it fits the ceiling to itself),
and 06-08 came back 4.3× under the ceiling.

## Bottleneck 2 — `HARD_TIMEOUT_MS` = 300 000 ms now sits BELOW one real card

This is the structural one, and it is not about money either. H2250 measured a clean
`nakzatra` card at **511 s wall with 3 of 5 spawns killed**. The per-call ceiling was raised
180 s → 300 s and then **bounded at 300 s as an absolute maximum** by an owner ruling
(H2254 — a request above it is now REFUSED pre-spawn rather than silently clamped). So on
dense cards the pipeline is killing its own calls by design, and a killed call still bills.

The mitigation already exists and is measured: the `--safe-mode` arm ran **−55 % wall on
this exact card** and took a CANARY GO under H2251. That makes safe-mode **load-bearing,
not optional** — but it was qualified before the lane stopped, so it has never driven a
production window.

## Bottleneck 3 — the metered-transport alternative does not exist on this box

If the Max lane is quota-bound, the obvious escape is a metered API route. It is blocked by
a **credential** problem, not a decision:

- H2504 (NO-GO, 0 calls, $0.00) measured that `credential_status()` reports
  `auth_token_present=False` **inside the interactive harness session**, same as in a
  subprocess — `ANTHROPIC_AUTH_TOKEN` is absent from every Python-reachable environment
  here. The harness lends it only to its own Agent tool.
- Wrapping the Agent tool returns assistant *text* with no per-call `usage` and no
  `total_cost_usd`. The locked contract classes absent usage as `cost_evaluable=false`, so
  that route is a **NO-GO by construction** — which is why call 1 was withheld rather than
  spent.
- The capture side is proven ready: the adapter selftest is **PASS 10/10**, and H2537
  landed independent served-model + usage attestation (field now computed `true`/`false`/
  `null`, never asserted).

What this needs is a credential readable by Python against a route that returns a `usage`
block. Authorization does not create one.

## Bottleneck 4 — the actual divisor has never been measured

[PILOT_COST.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PILOT_COST.md)
§6 lists five missing data points for the "can N months finish the book" question. Item 1 —
**the Max weekly token quota**, the divisor in `weeks = total ÷ quota` — is obtainable *only*
by running windows until the cap fires and recording the cumulative token count. It never
has been. Every schedule estimate for the whole dictionary is therefore unfounded in the one
number that decides it.

The prescribed experiment collapses items 1, 2 and 4 at once: run an instrumented window,
record tokens + wall-clock, keep going until the cap fires. It is blocked behind
Bottleneck 1, not behind money.

## Bottleneck 5 — human review gates block PRINT, not the drain

G5 / G6 / G7 / G10 are all blocked, and at first glance they look like the wall. They are
not the wall for the ruled default path. The quality bar was ruled **machine-preview, not
production-grade** ([DECISIONS_PWG_RU_QUALITY_BAR.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DECISIONS_PWG_RU_QUALITY_BAR.md)
D2), and the finish-line table picks **A — machine-preview book** as the default, with ~0
human time per card. G5–G10 gate finish-line **B/C** (sample-gold and print).

The cheapest single motion against them remains the one the 28-07 brief named: vote the
**20-card G6 MQM starter sheet** (~15–20 min), which is the gold instrument the whole
G6 → G7 → G10 chain hangs from. That is a human's ~20 minutes, not a budget line.

---

## What the authorization genuinely unlocks, today

| Item | Calls | State |
|---|--:|---|
| **H2630** — whole-card lane, 8 % of the pool, sealed plan `3eb569a3…` | 8 | Was the only plan at the `--authorize-unknown-billing` gate; **now authorized** |
| **H2534** — router.cheap two-ticket live canary | 2 | Authorization no longer the blocker; **transport still is** (Bottleneck 3) |
| **H2263** — w1 acceptance run for the H2248 call-weight cap on the `--safe-mode` arm | window | Lease intact and unconsumed; blocked behind the lane stop (Bottleneck 1) |

And one strategic lever that money *does* buy, which nothing above does: **DeepSeek bulk**,
costed in PILOT_COST §6 at **≈ $1.5–4 k for the whole dictionary**, parallel, with **no
weekly cap** — reserving Max/Opus for hard and gate-flagged cards. Note precisely what is
and is not already wired: H2490 retargeted the **L03–L07 corpus/RV layers** to
`deepseek-v4-flash`; the **PWG card-translation lane itself is not on that route**. So this
is a costed proposal with adjacent precedent, not a switch to flip.

---

## What is NOT a bottleneck (three findings that closed this month)

1. **A cheaper call shape.** Three qualification runs in a row found none. H2591
   INCONCLUSIVE (its GO was an artefact of how fast each arm *failed*); **H2612 NO-GO** on
   the fragment lane where 92 % of cards go — paired wall **+4.25 %**, paired non-cache
   tokens **+3.34 %**, against a pre-registered 10 % threshold, zero evidence holes;
   H2630 sealed for the remaining 8 %. PREP context does not earn a route change. The drain
   would run at today's economics, and there is no optimization worth waiting for.
2. **The GO arithmetic itself** — fixed. It fired on an artefact twice, so `build_receipt`
   now keys the verdict off **paired deltas** over units where *both* arms returned schema.
   An arm total silently rewards the arm that fails faster.
3. **The zero-usage class** — identified and recovered. Transcripts prove calls that
   reported all-zero usage really spent tokens; a run now stops on all-zero usage instead of
   silently deflating an arm.

---

## Ranked, with what each actually costs to clear

| # | Bottleneck | Clears with | Cost |
|---|---|---|---|
| 1 | c4 lane stopped since 06-08 | one health probe; the rate-limit premise behind the stop is refuted | **~$0.55** |
| 2 | 300 s ceiling below one card | drive a window on the qualified `--safe-mode` arm (−55 % wall) | needs #1 |
| 3 | Max weekly quota unmeasured | instrumented window run until the cap fires | needs #1 |
| 4 | no metered transport | a Python-readable credential on a `usage`-returning route | a credential |
| 5 | G5–G10 print gates | the 20-card G6 MQM starter sheet | ~20 min, a human |

**The first row is the whole story: the drain is stopped by a rule whose evidentiary basis
was withdrawn the day before yesterday, and re-testing it costs about half a dollar.**

_Dr. Mārcis Gasūns_
