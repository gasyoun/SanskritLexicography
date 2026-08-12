# B1 — why 7 of 16 H2591 calls reported zero usage

_Created: 12-08-2026 · Last updated: 12-08-2026_

Diagnosis of blocker **B1** of
[H2598](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2598-Opus_SanskritLexicography_pwg-prep-compare-rerun-after-usage-reporting-trustworthy_12.08.26.md),
opened by the [H2591 run](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/README.md).
Opus 5 (`claude-opus-5`), 12-08-2026.

## Headline: it was never one phenomenon

The run reported "7 of 16 calls returned zero usage". Splitting on the process exit code
separates two unrelated populations, and only one of them is a defect.

| exit | ordinals | zeroed | reading |
|---|---|---|---|
| `rc=1` | 5, 6, 7, 8, 9, 11 | 5 of 6 | the CLI **errored out** — zero usage is the documented contract |
| `rc=0` | 1, 2, 3, 4, 10, 12–16 | **2 of 10** | clean exit, valid audited card, no tokens — the real anomaly |

### The five explained calls

Every `rc=1` call is an `unstructured_result`: the envelope's `result` held an error
string, not JSON, which is exactly why parsing failed at character 0. Zero usage there is
not a bug but the org's deliberate fail-closed rule — [H2056 Q4-F5](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2056/H2056_CALL_PATH_REVIEW_2026-08.md):

> nobody can state the tokens a killed call burned … there is no wrapper, hence no number,
> and writing an estimate would fabricate data.

[H2313](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2313/HARD_TIMEOUT_MS_RECALIBRATE_07-08-2026.md)
records the identical signature — `returncode: 1 · zero usage`, with
`"You've hit your weekly limit"` in the result head. The sixth `rc=1` call reported 7 885
output tokens: partial spend before the error.

**This revises a conclusion the run itself drew.** H2591 reported that the markup-heavy
stratum "is unqualifiable at a whole-card call shape" because `Srama`/`samIpa` failed in
both arms. They did fail in both arms — but by a **non-zero CLI exit**, not by the model
declining to emit schema. Card density may be incidental. A provider-side refusal window
fits the shape better: the `rc=1` calls cluster at ordinals 5–11 with successes on either
side.

### The two anomalous calls, and why they stay UNPROVEN

Calls 01 (`SvAsa`, arm A) and 04 (`spfS`, arm A): `rc=0`, a card that passed the
deterministic audit at coverage 1.0, and every token counter zero.

**A byte-identical re-issue did not reproduce it.** Call 01's prompt was replayed from the
sealed plan (hash-verified before dispatch) with the same argv:

| | original call 01 | reproduction |
|---|---|---|
| returncode | 0 | 0 |
| wall | 358.9 s | 171.4 s |
| usage total | **0** | **75 635** |
| `subtype` / `terminal_reason` | *not captured* | `success` / `completed` |
| `num_turns` | *not captured* | 2 |
| `modelUsage` | *not read* | agrees with `usage` exactly |

So the class is **intermittent**: not prompt-determined, not card-determined, not
arm-determined. It cannot be pinned by re-issuing the same call.

**Leading hypothesis, unconfirmed:** usage reporting degrades under provider-side limit or
retry churn — the same pressure that produced the `rc=1` cluster in the same run, one
severity down. It cannot be confirmed, because the raw wrappers for those calls were
discarded and the class does not reproduce on demand.

**Refuted along the way:** "the driver read the wrong field". On a healthy call the
top-level `usage` and `modelUsage` agree *exactly* (75 635 both here; 45 677 on a separate
probe). `usage` is not systematically unreliable.

## What was fixed — capture, not a root-cause guard

The run made itself undiagnosable. The envelope carries fields the driver never kept:

- **`TERMINAL_FIELDS`** — `type`, `subtype`, `is_error`, `stop_reason`, `terminal_reason`,
  `api_error_status`, `num_turns`, `session_id`, `total_cost_usd`, and both durations. One
  `subtype` reading would have split the two populations above at the time, instead of
  three hours later.
- **`raw_result`** — for any call that yields no structured card, the returned string *is*
  the evidence. H2591 kept only the parse error, so five failures could never be diagnosed
  after the fact. Now stored truncated, never dropped.
- **`usage_cross_check`** — `modelUsage` is a **second, independent** token source. Reading
  both turns a zeroed `usage` beside a populated `modelUsage` into a detectable
  contradiction rather than a silent hole. This is the load-bearing one: a hole reads as a
  measurement and deflates whichever arm receives it.

Two classification changes follow:

- **`cli_error_exit`** is now its own failure class. Lumping `rc=1` refusals under
  `unstructured_result` is what made a provider refusal look like a model quality defect on
  a dense card. A refusal is recorded and the run **continues** — it is a provider verdict
  on one call, not evidence the ledger is lying.
- **`usage_contradiction`** classifies ahead of `missing_usage` and **stops the run**. It is
  strictly more informative: it proves the tokens existed and the accounting block was
  dropped, where `missing_usage` only says the block read empty.

Pinned by `test_b1_capture_gap_terminal_fields_raw_text_and_modelusage_crosscheck`;
matrix 14/14, window suite 211/211.

## What B1 still owes before a re-run

The symptom is now detectable and the run stops on it, but the **cause of the `rc=0` class
is not established**. A re-run is safe to attempt — it will halt loudly rather than grade a
holed comparison — but it may still halt. Before spending sixteen more calls:

1. Check whether the account was under a limit window during 07:53–11:40 UTC on
   12-08-2026 (the `rc=1` cluster is the strongest available proxy).
   **DONE 12-08-2026, and it came back negative — see [H2598's README](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2598/README.md).**
   Two corrections to this item as written: the run actually ran **13:25:56–14:26:19 UTC**
   (no call was spent in the window named above), and a single limit window is **refuted**,
   not merely unconfirmed — ordinal 10 returned `rc=0` with 75 580 tokens at 14:12:37,
   between refusals 9 and 11. The churn is per-call, not per-window.
2. If the next run halts on `usage_contradiction`, the envelope will now carry `subtype`,
   `terminal_reason`, `api_error_status` and the raw text — read those before re-running.
3. The `rc=1` reading also weakens B2's premise: the markup-heavy cards may not need the
   presplit lane at all, they may simply have been refused. Re-check before re-selecting.

Cost of this diagnosis: two probe calls (~$1.40 list-equivalent, billing `unknown_gateway`),
outside the sealed ledger — a diagnostic probe must not consume a reservation from a run
that is already finalized.

---

## Update, same day — the child transcripts DO exist, and they settle B1

**Correction to this document's own claim.** It said the CLI wrote no transcript, so that
evidence path was closed. That was wrong: it looked under `~/.claude`, but this session runs
under the **`claude1` profile on `D:`**, and all sixteen child calls wrote transcripts to
`D:\ClaudeTools\profiles\claude1\.claude\projects\D--pwg-ru-cli-cwd\`. Nothing was lost.

### The account was NOT rate limited

Every `rc=1` call carries an explicit API error in its own transcript:

| ord | time (UTC) | card | error recorded by the CLI |
|---|---|---|---|
| 5 | 13:49 | Srama A | `The response stopped arriving. The response above may be incomplete.` |
| 6 | 13:54 | Srama B | `The response stopped arriving…` |
| 7 | 13:59 | samIpa B | `Connection lost mid-response…` |
| 8 | 14:01 | samIpa A | `The response stopped arriving…` |
| 9 | 14:06 | vyavasTA A | **`529 Overloaded. This is a server-side issue, usually temporary`** |
| 11 | 14:15 | SudDi B | `Connection lost mid-response…` |

One **529 Overloaded** plus five streaming truncations, inside a 29-minute band
(13:49:17 → 14:18:38 UTC) that is bounded by clean calls on both sides and contains one
clean call (ord 10) in its middle. **No rate-limit or usage-limit message appears anywhere
in the window** — the H2313 weekly-limit signature this document floated as the leading
hypothesis is *absent*. The cause is transient provider-side degradation.

The real run window was **13:25:56 → 14:26:19 UTC**, not the 07:53–11:40 quoted earlier
(that was the handoff *claim* time, not the run).

This also settles ord 9's missing `returned_model`: a 529 means no response arrived, so
there was no model to attest.

### B2's premise is now refuted, not merely weakened

`Srama`/`samIpa` failed in both arms because the **stream died**, not because a
234-placeholder card defeats a whole-card call. Note the confound the frozen order created:
the strata were scheduled contiguously, so the four dense cards occupy exactly the ordinals
that fall inside the outage band — card class and wall-clock time are perfectly confounded
in this run. The API errors break the tie in favour of *time*. **A re-run should randomise
or interleave the key order** so a future outage cannot masquerade as a stratum effect.

### The token axis is recoverable — and it says NO-GO

The transcripts prove calls 1 and 4 really spent tokens while their envelopes reported
zeros. Transcript totals must first be **deduped**: each assistant message is written twice
(verified — one `message_id` with identical `output_tokens` appearing `x 2`), and the
transcript total is *exactly* 2× the envelope total on all nine healthy calls, which
calibrates the correction against a known-good reference.

Deduped output tokens for the two anomalous calls: **ord 1 ≈ 7 161**, **ord 4 ≈ 5 797** —
real spend the receipt recorded as zero.

With both recovered, no evidence hole remains: the five `rc=1` calls genuinely spent ~nothing
(their transcripts show 0–2 output tokens), so their zeros are TRUE rather than dropped.

| | arm A (baseline) | arm B (PREP) |
|---|---|---|
| non-cache tokens, all calls | 43 752 | 73 002 |
| non-cache tokens, 4 cards both arms returned | 21 202 | **60 340** |

**PREP costs ~1.7× the non-cache tokens overall and ~2.8× on the like-for-like subset.**

And it reframes the wall-clock margin that produced the original GO. On `SvAsa`, arm A spent
358.9 s to emit 7 161 output tokens (≈20 tok/s) while arm B spent 454.9 s to emit 40 421
(≈89 tok/s). Arm A was not doing more work more slowly; it was **stalling**. On the two cards
where output volume is comparable (`rAtra`, `zoqaSan`) arm B was both faster and cheaper.

**Verdict implication:** the GO rule needs PREP to lose ≤1 audited card *and* improve wall or
non-cache tokens by >10%. Cards tie 4–4; tokens are decisively worse; the wall margin is an
artifact of arm A stalling and of failure durations. That is a **NO-GO**, not an
INCONCLUSIVE — but the sealed receipt is left as it stands, because it is the honest record
of what the run itself could know. Re-grading belongs to the H2598 re-run, with the recovery
method above available to it.

_Dr. Mārcis Gasūns_
