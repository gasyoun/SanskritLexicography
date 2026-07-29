# H1210 — DeepSeek vs Claude-native on 100 stratified PWG cards: results, method, and what the numbers do (and do not) support

_Created: 29-07-2026 · Last updated: 29-07-2026_

**Executors.** Rig + the original 87 cards of each arm: Opus 4.8 (`claude-opus-4-8`) as
controller in **both** arms, Sonnet 5 (`claude-sonnet-5`) as arm-A worker, `deepseek-chat` as
arm-B generator (28-07-2026). Arm A's remaining 13 cards were filled 29-07-2026 under
[H1846](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1846-Opus_SanskritLexicography_h1210-arm-a-coverage-fill_29.07.26.md)
with the same Sonnet 5 workers but a controller that the template's alias resolved to Opus 5
(`claude-opus-5[1m]`).
Report, coverage audit, blind sheet and this document: Opus 5 1M (`claude-opus-5[1m]`),
29-07-2026. The handoff is [H1210](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1210-Opus_SanskritLexicography_pwg-ab-deepseek-vs-claude-100_17.07.26.md);
the design fork it settles was MG's ruling of 17-07-2026.

**Bottom line in one sentence:** with all 100 cards run in both arms, **the answer depends
entirely on which definition of "clean" you use** — by the canonical audit alone arm A wins
93 vs 78 and looks dominant on long entries, but by what each pipeline would actually
**ship unattended** the two arms tie (72 vs 70) and the long-entry quartile collapses for
*both* (13% vs 17%), because arm A's apparent long-entry advantage is made of cards its own
rig refused to ship.

> **Revision history.** The first version of this report (29-07-2026, 87 cards) had to lead
> with a coverage caveat: arm A had never attempted 13 cards. Those 13 have since been run
> ([H1846](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1846-Opus_SanskritLexicography_h1210-arm-a-coverage-fill_29.07.26.md)),
> the caveat is discharged, and the fill changed the conclusion — see §3.

## 1. Coverage: closed

Both arms now stand at **100 of 100 cards attempted**, verified by
[`coverage_gap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/coverage_gap.py):

| entry-length quartile | arm A attempted | arm B attempted | not attempted in arm A |
|---|---:|---:|---|
| Q1 (28–176 B) | 22/22 | 22/22 | — |
| Q2 (180–526 B) | 23/23 | 23/23 | — |
| Q3 (670–4349 B) | 22/22 | 22/22 | — |
| Q4 (4553–11974 B) | 23/23 | 23/23 | — |
| no_pwg (no byte size) | 10/10 | 10/10 | — |

The original gap was not a random 13 cards:
[`pack_chunks.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/pack_chunks.py)
packs by **bytes**, so the three chunks that never ran (06, 08, 09) removed a contiguous
length band — 9 of the 13 in the top quartile and **all ten S4 verb-root cards**. That
mechanism is worth keeping even though the gap is closed: it is
[FINDINGS §500](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
and [integrity issue #863](https://github.com/gasyoun/SanskritLexicography/issues/863),
and it generalises to every chunked run in this repo.

**Two properties of the fill to carry into every number below.** (1) Its controller ran on
a later tier than the original 87 — measured, not assumed: `arm_a.telemetry.json` now records
per-chunk model ids, and the three filled chunks report controller `claude-opus-5[1m]`
against the original chunks' Opus 4.8 (`claude-opus-4-8`), with workers `claude-sonnet-5`
throughout. (2) **8 of the 13 filled cards lost at least one worker attempt to an API
transport failure** (`Response stalled mid-stream`, `Connection closed mid-response`) — an
infrastructure outcome, not a translation-quality one, and concentrated in exactly the
longest cards. Both properties depress arm A's *pipeline* metric below and neither is a
statement about model quality.

## 2. What was compared

One variable changes: **the generator**. Everything else is shared by construction —
the same 100-card worklist, the same prompt and output schema, the same free deterministic
gate, the same ≤2-retry chain, the **same** Opus 4.8 controller with the same accept/reject
gates, and the same authoritative post-run audit
([`h1209/canonical_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1209/canonical_audit.py)).

- **Arm A — Claude-native:** Sonnet 5 workers under the Opus 4.8 controller, the
  [H1209](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1209-Opus_SanskritLexicography_pwg-ru-controller-worker-canary_17.07.26.md)
  rig with two named deltas (parallel card loop, 900 s agent deadline).
- **Arm B — DeepSeek + the same controller:** `deepseek-chat` over the existing
  OpenAI-compatible path generates; the identical Opus 4.8 controller accepts or rejects on
  top. No Anthropic API key was used or requested anywhere (standing rule).

Selection was **stratified, not random**: 10 byte-deciles × 6 (S1, 60 cards), 15
defect-class culprits (S2 — the H858 `{#…#}` span class, H920 sense-loss, citation density),
10 `no_pwg` supplement cards (S3), 10 verb roots (S4), 5 cards overlapping the H317 medium50
worklist for direct comparability (S5). Declared cap: entries above 12,000 B were excluded
(248 monster heads), so the deciles are cut over the runnable pool, not the full universe.

Nothing from either arm was promoted to the store — both runs are **promote-DRY**.

## 3. The result that decides the question — and the metric that decides the result

Two definitions of "clean" are defensible here, and they disagree about who wins:

- **audit-clean** — `canonical_audit.py` says the card is promote-DRY. This is what the
  first version of this report published, on the H1209 v1 grounds that the rig's own
  `would_promote` had been caught lying.
- **shippable** — audit-clean **and** the rig ended the card in a clean status
  (`clean-no-review` / `clean-controller-approved`): what the pipeline would actually have
  written to the store unattended.

The gap between them is not bookkeeping. `canonical_audit.py` scores `cards_out`, and the
rig's per-card loop keeps the **last successful attempt's** card even when the card ends as
`worker-null-death` (a later attempt died) or `escalate-review-sheet` (the controller
rejected it). So "audit-clean" counts cards the pipeline refused to ship — **21 of them in
arm A, 8 in arm B**. Measured by
[`dual_metric_breakdown.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/dual_metric_breakdown.py):

| entry-length quartile | A audit-clean | B audit-clean | A shippable | B shippable |
|---|---:|---:|---:|---:|
| Q1 (28–176 B) | 22/22 (100%) | 21/22 (95%) | 22/22 (100%) | 21/22 (95%) |
| Q2 (180–526 B) | 23/23 (100%) | 21/23 (91%) | 23/23 (100%) | 21/23 (91%) |
| Q3 (670–4349 B) | 19/22 (86%) | 19/22 (86%) | 15/22 (68%) | 15/22 (68%) |
| Q4 (4553–11974 B) | 20/23 (87%) | 8/23 (35%) | **3/23 (13%)** | **4/23 (17%)** |
| no_pwg | 9/10 (90%) | 9/10 (90%) | 9/10 (90%) | 9/10 (90%) |
| **TOTAL** | **93/100** | **78/100** | **72/100** | **70/100** |

Read the two right-hand columns before believing the two left-hand ones. The headline
"93 vs 78" and the spectacular Q4 gap (87% vs 35%) live entirely in the audit-only metric.
Under the pipeline metric:

- the arms **tie overall** — 72 vs 70, a 2-card difference on n=100;
- Q1/Q2 are unchanged (short entries are easy for both, and nothing gets refused);
- Q3 drops for both arms identically (68% vs 68%);
- **Q4 reverses**: 13% for arm A against 17% for arm B. Neither pipeline can ship the
  longest entries unattended. The earlier reading — "arm B collapses on long entries" — was
  an artifact of scoring text that arm A's own rig had thrown away.

Arm A's Q4 shippability is further depressed by the API transport failures noted in §1
(8 of the 13 filled cards lost an attempt that way), so **13% is a floor, not an estimate of
the model's ceiling**. That cuts the other way too: it is exactly why the honest conclusion
is "neither arm ships long entries", not "arm B is better on long entries".

The defect-culprit stratum S2 (15 cards, the H858 span class + H920 sense-loss + citation
density) behaves the same way, and it is the sharpest single illustration in the run:

| S2, n=15 | audit-clean | shippable | refused but audit-clean |
|---|---:|---:|---:|
| arm A | 13 | **4** | 9 |
| arm B | 3 | **2** | 1 |

A +10-card margin under the audit metric shrinks to +2 under the pipeline metric. Nine of
arm A's thirteen "clean" S2 cards are ones its own rig would not have shipped.

## 4. Headline table (100 vs 100)

| metric | arm A — Claude-native | arm B — DeepSeek + same controller |
|---|---|---|
| generator | workers `claude-sonnet-5`; controller `claude-opus-4-8` (87 cards) + `claude-opus-5[1m]` (the 13 filled) | `deepseek-chat` / controller `claude-opus-4-8` |
| cards attempted | **100** of 100 | **100** of 100 |
| **audit-clean %** | **93.0% (93/100)** | **78.0% (78/100)** |
| **shippable % (audit-clean AND rig-clean)** | **72.0% (72/100)** | **70.0% (70/100)** |
| audit-clean cards the rig refused | **21** | 8 |
| generation calls | 188 | 149 |
| controller calls | 104 | 50 |
| calls / audit-clean card | 3.14 | 2.55 |
| controller share of calls | 35.6% | 25.1% |
| retries (rate/card) | 88 (0.88) | 69 (0.69) |
| escalated to review-sheet | 14 (14.0%) | 15 (15.0%) |
| complexity-trigger false-flag rate | 71.9% (41/57) | 63.2% (36/57) |
| generation USD | n/a — subscription lane | **$0.7255** |
| USD / audit-clean card | n/a | **$0.0093** |
| wall clock | 17,974 s agent-time (chunks overlapped) | 1,255 s |

Defect classes over the cards the audit rejected:

| defect class (canonical audit) | arm A | arm B |
|---|---:|---:|
| translation-fidelity-reject | 4 | 13 |
| fidelity-reject | 2 | 12 |
| soft: tnmask-mismatch | 2 | 11 |
| NULL-CARD | 3 | 9 |

Arm A's three `NULL-CARD`s are cards where *every* attempt failed, so nothing reached the
audit; the eight further filled cards that ended `worker-null-death` still carried an earlier
attempt's text, which is precisely how they land in the audit-clean column while being
unshippable (§3).

**Do not read the wall-clock or retry rows as model comparisons.** Arm A's 17,974 s is
summed agent-time across chunks that ran concurrently, its retry rate is inflated by the API
transport failures of §1, and arm B's `$0.0093` covers generation only — its controller ran
uncosted on the subscription lane. The rows are kept because they are what was measured, not
because they support a ranking.

## 5. Cost and speed, stated honestly

- **Arm B's $0.7255 is generation only.** Its controller is the same Opus 4.8 running on the
  subscription lane, and those 50 calls carry no exposed per-call price. The cash figure
  therefore covers one of the two stages; the true arm-B cost is `$0.73 + (50 controller
  calls on the plan)`.
- **Arm A has no USD at all**, for the same reason at both stages — the Workflow `agent()`
  lane exposes tokens, not dollars. Its comparable quantity is **16.54 M subagent tokens**
  (11.82 M worker + 4.72 M controller; the controller is 28.5% of tokens but 38.2% of calls).
- Arm B's token profile: 2.75 M cache-hit input, 11.9 k cache-miss input, 482 k output,
  priced at the published `deepseek-chat` table ($0.07 / $0.27 / $1.10 per Mtok).
- **7.7× wall-clock difference** (21 m vs 2 h 40 m) is real but not a clean model comparison:
  arm A ran through the Workflow agent harness with per-agent scheduling overhead and a
  900 s deadline, arm B through a direct HTTP loop. Read it as *lane* latency, not
  *model* latency.

## 6. Two findings that belong to neither arm

1. **The rig and the audit are not scoring the same object** — the finding that turned out
   to matter most. The first version of this report recorded that the rig "understates"
   cleanliness (A 72 self-reported vs 93 audited; B 72 vs 78) and read that as the rig being
   conservative. It is not conservatism: `canonical_audit.py` scores `cards_out`, the last
   attempt that *returned*, while `final_status` records how the card *ended*. A card whose
   controller rejected attempt 1 and whose attempt 2 died mid-stream ends `worker-null-death`
   while still carrying attempt 1's text into the audit. So the audit measures **text that
   was produced at some point**; the rig measures **what the pipeline would deliver**. Both
   are legitimate; quoting only the first is what made arm A look dominant (§3).
2. **The complexity trigger fires mostly for nothing** — 77.8% of arm A's flags and 63.2% of
   arm B's were cards the audit passed with no soft flag and no deterministic issue. It is
   currently buying retries and controller attention it does not earn, in both arms, so
   re-tuning it is generator-independent work.
3. **There is a quality axis neither arm's numbers can see: gloss arity.** Both gates check
   the `{Tn}` mask as a multiset — every German token present, none invented — which catches
   sense loss and invention and is blind to a card whose mask is perfect while each German
   gloss has become two or three Russian ones (`erblickend` → «узревающий, взирающий»;
   `hinausschaffen` → «вынести, удалить, выдворить»). A probe over one card (`kAS`, arm B,
   523 tokens, no mask defects at all) turned up **15 candidate arity drifts** —
   [`qc_gloss_arity.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/qc_gloss_arity.py).
   That is a probe, not a rate: one card, one arm, no comparison. It is recorded here because
   inflation of this kind reads as fluent Russian, passes every gate in this A/B, and would
   therefore never appear in any table above — the blind human vote is currently the only
   instrument in the design that could catch it.

## 7. What the numbers support — a human decides

The handoff asks for a table and a recommendation with figures, not a verdict. Ranked by
what the measurements actually carry — and revised after the 13-card fill, which reversed
the earlier reading:

- **On the pipeline metric the two arms are indistinguishable: 72 vs 70 on n=100.** A
  2-card difference is not a basis for choosing a production track. The generator is
  simply not where this pipeline's quality is decided at present.
- **Neither arm can ship long entries unattended — 13% and 17% on Q4.** This, not the
  generator choice, is the finding with operational consequences. Any plan that assumes
  long-entry throughput from either lane is unfunded by this experiment.
- **The earlier "length-routed hybrid" recommendation is withdrawn.** It rested on arm A
  scoring 93% on Q4 against arm B's 35%; under the pipeline metric that inverts (13% vs
  17%), so routing long entries to the Claude-native lane buys nothing measurable. Routing
  by length may still be right for *cost* reasons — that is a different argument, on
  different evidence.
- **"Bury the DeepSeek arm" remains unsupported, and is now weaker still.** At 70 vs 72
  shippable, and ~1¢ per audit-clean card, the cheap arm delivers what the expensive one
  delivers on this sample.
- **What would actually move the numbers is the retry/transport layer, not the model.**
  Arm A lost 8 of 13 filled cards' attempts to API stream failures, and 21 of its 93
  audit-clean cards never became shippable. Making a null attempt resumable (rather than
  consuming one of three) is generator-independent work with a larger expected effect than
  swapping generators.
- **The blind human vote (§9) can still move this.** Every number above is machine
  adjudication; the design puts human verdicts on top as the quality arbiter, and they have
  not been cast yet.
- **~1 card in 7 reaches a human in either design** (14.0% / 15.0% escalation). Neither arm
  removes the human from the loop at this quality bar.

## 8. Limitations, and what each would cost to close

| limitation | why it matters | cost to close |
|---|---|---|
| ~~arm A missing 13 cards~~ | **closed 29-07-2026** by [H1846](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1846-Opus_SanskritLexicography_h1210-arm-a-coverage-fill_29.07.26.md) — both arms are at 100/100, and the fill reversed the conclusion | — |
| the filled 13 ran on a later controller tier (`claude-opus-5[1m]` vs `claude-opus-4-8`) | their retry/escalation counts are not strictly comparable to the original 87; the audit metric is unaffected (deterministic re-run) | not closable retroactively — the template pins aliases, so a version-pinned re-run of all 100 would be needed |
| 8 of the 13 filled cards lost attempts to API transport failures | arm A's Q4 *shippable* 13% is a floor, not a model ceiling | re-run the affected cards on a healthy link, or make a null attempt resumable instead of attempt-consuming |
| arm B's controller cost not in the $ figure | the cheap arm's true cost is understated | instrument controller token capture on the arm-B shuttle |
| one run per arm, no re-roll (by design) | run-to-run variance is unmeasured — and a 2-card gap (72 vs 70) is well inside plausible variance | a second run per arm, same worklist |
| wall clock mixes lane with model | not a model claim; arm A's figure is summed agent-time over overlapping chunks | not worth closing; use tokens/calls instead |
| human vote not yet cast | the top quality layer is missing | one reviewer pass over the 40-item sheet |

None of these were silently absorbed: every one is either in a table above or a follow-up
row in the handoff's close-out. The second and third rows are new, and they are the reason
the 72-vs-70 tie should be read as "no measured difference", not as "arm B proven equal".

## 9. The blind human-vote sheet (deliverable 2)

[`build_ab_review_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/build_ab_review_sheet.py)
draws **40 items — 20 per arm, interleaved and unlabelled**. The arm mapping exists only in
the committed lock
[`review/locks/h1210-ab-blind-100card-2026-07-29.lock.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/h1210-ab-blind-100card-2026-07-29.lock.json);
the HTML carries no arm label in any id, badge or DOM order, and item order is a
deterministic hash of `(sheet_id, key1, arm)`. Only cards the audit already passed are
offered — rating a card the free gate hard-rejected measures nothing.

**The sample is deliberately balanced across the two populations of §3**, because a uniform
draw over audit-clean cards would under-represent exactly the disputed one:

| | shippable | refused but audit-clean | pool |
|---|---:|---:|---|
| arm A | 10 | 10 | 72 / 21 |
| arm B | 12 | 8 | 70 / 8 |

Arm B carries only 8 refused cards in total, so its sample takes all of them and backfills
with shippable ones — reported here rather than silently rebalanced. Like the arm, the class
is recorded **only in the lock**: the HTML contains no occurrence of `shippable`,
`refused-but-audit-clean`, or any rig status, so a reviewer cannot infer which population a
card comes from. That is the point — human verdicts on the refused half are the only way to
settle whether text the pipeline threw away was actually publishable.

The earlier 87-card sheet ([`…blind-2026-07-29.lock.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/h1210-ab-blind-2026-07-29.lock.json))
was never voted and is **superseded**, with that reason recorded in the lock itself: its
arm-A sample was drawn before the fill and so excluded the top length band entirely.

The sheet does not render its own panels: it calls
[`src/g5_card_render.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/g5_card_render.py),
the module H1808 made canonical for review cards, so the A/B vote and the G5 vote show
markup the same way. The Russian goes through `print_panel` (the renderer the public
article site uses — Cologne scan links with a bibliography tooltip, `<ab>` in Russian,
italic IAST), the German through `de_panel`, and the sheet carries that module's legend and
CSS. In this sheet: **715 linked citations**, plus 204 citations that carry a bibliography
tooltip but no link because their sigla resolve to no scan (`RĀJAN.`, `ŚKDR.`) — an honest
gap rather than a guessed URL.

The first version of this generator hand-rolled its own colouring and linking, which is the
defect H1646 and H1808 already fixed twice; it was replaced with the shared renderer once
that module landed on `master` mid-session. Measured on arm B's cards, the shared path also
links strictly more (2,227 of 2,992 citation spans) than the hand-rolled one did.

**Blinding verified, not asserted:** the rendered HTML contains no arm-revealing token
(`deepseek`, `claude`, `sonnet`, `opus`, `arm_a/arm_b`), all 40 item ids appear exactly
once, and the arm sequence by item id is a real interleave — `AABAAAABBABAAABBABBBABABBBAABBAAABBAABBB`,
longest same-arm run 4, 20/20 split. The lock binds the sheet by content hash
(`sha256:37194f2a89a0…`), so a regenerated sheet that does not match cannot be voted into it.

**Publish safety:** the HTML embeds unpublished RU/DE store-grade text and is gitignored;
only the lock is committed.

## 10. Artifacts and how to reproduce

| artifact | what it is |
|---|---|
| [`src/pilot/h1210/H1210_ab100_worklist.28.07.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_ab100_worklist.28.07.26.json) | the frozen 100-card selection — the A/B's input of record |
| [`src/pilot/h1210/H1210_AB_RESULTS.29.07.26b.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_AB_RESULTS.29.07.26b.json) | every metric in §4, machine-readable (the `.29.07.26` twin is the pre-fill 87-card state, kept) |
| [`src/pilot/h1210/H1210_dual_metric.29.07.26b.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_dual_metric.29.07.26b.json) | §3's audit-clean vs shippable table, machine-readable |
| [`src/pilot/h1210/H1210_length_breakdown.29.07.26b.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_length_breakdown.29.07.26b.json) | per-quartile audit-clean rates |
| [`src/pilot/h1210/H1210_coverage_gap.29.07.26b.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_coverage_gap.29.07.26b.json) | §1 — now 100/100 in both arms |
| [`status_vs_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/status_vs_audit.py) · [`dual_metric_breakdown.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/dual_metric_breakdown.py) | the rig-vs-audit cross-tab and the two-metric table — the analysis that overturned §7 |
| [`refresh_after_fill.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/refresh_after_fill.py) | recomputes the whole chain after a fill, so no artifact is left stale |
| [`src/pilot/h1210/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/README.md) | the rig: what each script is, the reproduce sequence, and the card-id join trap |

The one trap worth repeating from that README: **cards are keyed by safe-name stem
(`_s_aluqa`), not by `key1`** — joining the worklist, the arms' results and the audit on
`key1` matched 42 of 87 arm-A rows and would have reported arm A at 46%. Every join in
`ab_report.py`, `length_breakdown.py` and `coverage_gap.py` goes through one shared
`card_id()`; an unresolvable row is a hard error, never a silently dropped denominator.

_Dr. Mārcis Gasūns_
