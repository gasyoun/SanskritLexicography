# H1210 — DeepSeek vs Claude-native on 100 stratified PWG cards: results, method, and what the numbers do (and do not) support

_Created: 29-07-2026 · Last updated: 29-07-2026_

**Executors.** Rig + both runs: Opus 4.8 (`claude-opus-4-8`) as controller in **both** arms,
Sonnet 5 (`claude-sonnet-5`) as arm-A worker, `deepseek-chat` as arm-B generator (28-07-2026).
Report, coverage audit, blind sheet and this document: Opus 5 1M (`claude-opus-5[1m]`),
29-07-2026. The handoff is [H1210](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1210-Opus_SanskritLexicography_pwg-ab-deepseek-vs-claude-100_17.07.26.md);
the design fork it settles was MG's ruling of 17-07-2026.

**Bottom line in one sentence:** on short and medium PWG entries the two generators are
near-indistinguishable, on the longest quartile the DeepSeek arm collapses (35% vs 93%
audit-clean), and the cheap arm costs about **one cent per clean card** — but arm A never
attempted 13 of the 100 cards, including **the entire verb-root stratum**, so the two
headline percentages are *not* a fair head-to-head and must never be quoted as one.

## 1. Read this before quoting any number

Arm A completed **87 of 100** cards. Three of the ten size-bounded chunks (06, 08, 09)
never produced a `slice_result` — their cards were never attempted, not attempted-and-failed.
Because [`pack_chunks.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/pack_chunks.py)
packs by **bytes**, a missing chunk is a contiguous band of the length distribution, not a
random 13 cards. Measured by
[`coverage_gap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/coverage_gap.py):

| entry-length quartile | arm A attempted | arm B attempted | not attempted in arm A |
|---|---:|---:|---|
| Q1 (28–176 B) | 22/22 | 22/22 | — |
| Q2 (180–526 B) | 22/23 | 23/23 | tip |
| Q3 (670–4349 B) | 19/22 | 22/22 | saBAjay, viD, ras |
| Q4 (4553–11974 B) | 14/23 | 23/23 | jU, jalp, nanda, vaYc, gOra, akza, SA, las, kAS |
| no_pwg (no byte size) | 10/10 | 10/10 | — |

By selection stratum the same gap reads worse: arm A's per-stratum clean counts are
S1 58/60, S2 11/12, S3 9/10, S5 5/5 — and **S4 (verb roots) does not appear at all**. All
ten verb-root cards, the class the selection rule deliberately included as hard, are missing
from arm A. Arm B scored 5/10 on them.

So the honest comparison is the per-quartile table in §3, on the cards **both** arms
attempted — not the two headline percentages. The direction of the bias is the one that
flatters arm A.

The handoff's stop condition was one run per arm, no re-roll. Completing arm A's 13 cards
would need a fresh Workflow launch of chunks 06/08/09 and is left as an explicit, costed
follow-up rather than silently folded in — see §8.

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

## 3. The result that decides the question

Audit-clean rate by entry-length quartile, canonical promote-DRY verdicts, on what each arm
actually attempted:

| entry-length quartile | arm A clean | arm B clean |
|---|---:|---:|
| Q1 (28–176 B) | 22/22 (100%) | 21/22 (95%) |
| Q2 (180–526 B) | 22/22 (100%) | 21/23 (91%) |
| Q3 (670–4349 B) | 17/19 (89%) | 19/22 (86%) |
| Q4 (4553–11974 B) | 13/14 (93%) | 8/23 (35%) |
| no_pwg (no byte size) | 9/10 (90%) | 9/10 (90%) |

Q1–Q3 and the `no_pwg` lane are a wash — the gap is 0–5 points and runs in both directions.
Q4 is a different regime: the DeepSeek arm loses roughly two thirds of the longest entries.
Arm A's Q4 cell rests on **14 cards**, so its 93% carries a wide interval; what the data
supports is the *direction and size* of the interaction, not a precise long-entry rate for
arm A.

The defect-culprit stratum tells the same story from another angle: on S2 (the deliberately
nasty cards) arm A is 11/12 and arm B is 3/15.

## 4. Headline table (with §1 in force)

| metric | arm A — Claude-native | arm B — DeepSeek + same controller |
|---|---|---|
| generator | workers `claude-sonnet-5` / controller `claude-opus-4-8` | `deepseek-chat` / same `claude-opus-4-8` controller |
| cards attempted | **87** of 100 | **100** of 100 |
| audit-clean % (canonical promote-DRY) | 95.4% (83/87) — *not comparable, see §1* | 78.0% (78/100) |
| rig self-report clean (vs audit) | 70 (−13) | 72 (−6) |
| generation calls | 152 | 149 |
| controller calls | 94 | 50 |
| calls / clean card | 2.96 | 2.55 |
| controller share of calls | 38.2% | 25.1% |
| retries (rate/card) | 65 (0.75) | 69 (0.69) |
| escalated to review-sheet | 12 (13.8%) | 15 (15.0%) |
| worker-null-death | 5 (5.7%) | 13 (13.0%) |
| complexity-trigger false-flag rate | 77.8% (35/45) | 63.2% (36/57) |
| generation USD | n/a — subscription lane | **$0.7255** |
| USD / clean card | n/a | **$0.0093** |
| wall clock | 9,625 s (2 h 40 m), median 114 s/card | 1,255 s (21 m) |

Defect classes over the rejected cards:

| defect class (canonical audit) | arm A | arm B |
|---|---:|---:|
| translation-fidelity-reject | 4 | 13 |
| fidelity-reject | 2 | 12 |
| soft: tnmask-mismatch | 2 | 11 |
| NULL-CARD | 0 | 9 |

`NULL-CARD` is arm B's alone: nine cards where the generator returned nothing usable and the
retry chain never recovered. Together with the 13 worker-null-deaths (vs arm A's 5), the
cheap arm's failures are disproportionately *absences* rather than wrong translations —
which is the easier failure class to detect, and the more expensive one to re-run.

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

1. **The rig's self-report understates cleanliness in both arms** (A: 70 self-reported vs 83
   audited; B: 72 vs 78). H1209 v1 proved the self-report could *overstate*; this run shows
   it drifting the other way once the controller is strict. Either way the conclusion is
   unchanged and now doubly evidenced: **the canonical audit is the verdict, the rig's
   `would_promote` is a hint.**
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
what the measurements actually carry:

- **A length-routed hybrid is the only option the data positively supports.** Below ~4.5 kB
  the arms are within a few points of each other and arm B costs ~1¢/clean card; above it
  arm B loses two thirds. Routing by entry size — cheap generator under the threshold, the
  Claude-native lane over it — is supported by Q1–Q4 as measured, and needs no new
  experiment to justify trying.
- **"Bury the DeepSeek arm" is not supported.** Its failure is concentrated, not diffuse: it
  is at parity across the 77 cards outside the top quartile (70 of them clean, 91%), and its
  worst class (`NULL-CARD`, null-death) is
  detectable by the free gate rather than silently wrong text.
- **"Make DeepSeek the production track" is not supported either** — not without a decided
  policy for long entries and for the 9 NULL-CARDs.
- **The blind human vote (§9) can still move this.** Every number above is machine
  adjudication; the handoff's design puts human verdicts on top as the quality arbiter, and
  they have not been cast yet.
- **Both arms' 100% figures rest on a review-sheet escalation rate of 13.8% / 15.0%** — i.e.
  roughly one card in seven still reaches a human in either design. Neither arm removes the
  human from the loop at this quality bar.

## 8. Limitations, and what each would cost to close

| limitation | why it matters | cost to close |
|---|---|---|
| arm A missing 13 cards, incl. all 10 verb roots | the two headline % are not comparable; arm A's Q4 rests on n=14 | one Workflow launch of chunks 06/08/09 (~13 cards), then re-run `ab_report.py` + `coverage_gap.py` |
| arm B's controller cost not in the $ figure | the cheap arm's true cost is understated | instrument controller token capture on the arm-B shuttle |
| one run per arm, no re-roll (by design) | run-to-run variance is unmeasured | a second run per arm, same worklist |
| wall clock mixes lane with model | the 7.7× is not a model claim | not worth closing; use tokens/calls instead |
| human vote not yet cast | the top quality layer is missing | one reviewer pass over the 40-item sheet |

None of these were silently absorbed: every one is either in a table above or a follow-up
row in the handoff's close-out.

## 9. The blind human-vote sheet (deliverable 2)

[`build_ab_review_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/build_ab_review_sheet.py)
draws **40 items — 20 per arm, interleaved and unlabelled**. The arm mapping exists only in
the committed lock
[`review/locks/h1210-ab-blind-2026-07-29.lock.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/h1210-ab-blind-2026-07-29.lock.json);
the HTML carries no arm label in any id, badge or DOM order, and item order is a
deterministic hash of `(sheet_id, key1, arm)`. Only cards the audit already passed are
offered — rating a card the free gate hard-rejected measures nothing.

The sheet renders both the Russian rendering and the German source through
`csl_pyutil.anatomy.highlight()` with a legend, and every `<ls>` citation resolves to its
scan through the repo's ported resolver
([`src/ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)) —
1,430 linked citations in this sheet; abbreviation-only citations (`MED.`, `ŚKDR.`) stay
plain rather than becoming dead links. This is the H1646/H1808 legibility standard, which
every new sheet generator has so far had to re-learn.

**Publish safety:** the HTML embeds unpublished RU/DE store-grade text and is gitignored;
only the lock is committed.

## 10. Artifacts and how to reproduce

| artifact | what it is |
|---|---|
| [`src/pilot/h1210/H1210_ab100_worklist.28.07.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_ab100_worklist.28.07.26.json) | the frozen 100-card selection — the A/B's input of record |
| [`src/pilot/h1210/H1210_AB_RESULTS.29.07.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_AB_RESULTS.29.07.26.json) | every metric in §4, machine-readable |
| [`src/pilot/h1210/H1210_length_breakdown.29.07.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_length_breakdown.29.07.26.json) | §3, machine-readable |
| [`src/pilot/h1210/H1210_coverage_gap.29.07.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/H1210_coverage_gap.29.07.26.json) | §1, machine-readable |
| [`src/pilot/h1210/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/README.md) | the rig: what each script is, the reproduce sequence, and the card-id join trap |

The one trap worth repeating from that README: **cards are keyed by safe-name stem
(`_s_aluqa`), not by `key1`** — joining the worklist, the arms' results and the audit on
`key1` matched 42 of 87 arm-A rows and would have reported arm A at 46%. Every join in
`ab_report.py`, `length_breakdown.py` and `coverage_gap.py` goes through one shared
`card_id()`; an unresolvable row is a hard error, never a silently dropped denominator.

_Dr. Mārcis Gasūns_
