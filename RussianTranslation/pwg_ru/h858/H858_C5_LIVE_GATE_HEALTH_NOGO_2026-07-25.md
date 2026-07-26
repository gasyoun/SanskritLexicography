# H858 — c5 live gate: HEALTH_NOGO (25-07-2026), latency ~2× the ceiling

_Created: 25-07-2026 · Last updated: 25-07-2026_

Executor: Opus 5 (`claude-opus-5[1m]`). First gate ever run on **c5**, after two c4
attempts the same day returned `HEALTH_NOGO` on `rate_limit`
([c4 packet](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h858/H858_C4_LIVE_GATE_HEALTH_NOGO_2026-07-25.md)).
Gating the paid validation window still owed by
[H858 Part B](https://github.com/gasyoun/Uprava/blob/main/handoffs/H858-Opus_SanskritLexicography_pwg_ru_sense_fidelity_anchor_repair_13.07.26.md).

## Verdict

```
gate_reason = HEALTH_NOGO
verdict     = NO-GO
```

No canary. No production window. Nothing promoted. Two paid calls were made and both
**succeeded** — this is not a quota or auth failure.

## Step 1 — health: the ONE attempt taken

| Reading | Elapsed | Classification | Output | UTC |
|---|---|---|---|---|
| warm-up | **59 651 ms** | `success` | 1 651 B | 2026-07-25T18:57:56Z |
| measured | **52 960 ms** | `success` | 1 654 B | 2026-07-25T18:58:49Z |

Both readings are **~1.8–2.0× the 30 000 ms ceiling**, so both fail the strict rule
(EITHER reading ≥ 30 000 ms ⇒ NO-GO). Wall clock 112.6 s for the pair.

- Profile: `D:\ClaudeTools\profiles\claude5\.claude` · exact model `claude-sonnet-5`
- Prompt: 6 828 B actual (≥ 5 KiB floor), schema-carrying, load-representative
- Connection errors: **0**. Both calls returned a valid envelope with real output.
- Events: `src/pilot/output/h963_c5_gate0_probe_events.jsonl` (per-account series)

## The profiles fail for ORTHOGONAL reasons — that is the finding

Three profiles gated, 25-07 → 26-07. **All NO-GO, none for the same reason as its neighbour:**

| Profile | UTC | Calls | Latency | Blocker |
|---|---|---|---|---|
| **c4** | 25-07 16:02Z, 18:18Z | warm-up `rate_limit`, measured never ran | 17.9 s / 19.9 s — **fine** | quota / account state |
| **c5** | 25-07 18:56Z | warm-up + measured both `success` | 59.7 s / 53.0 s — **~2× ceiling** | route latency |
| **c1** | 26-07 02:37Z | warm-up `rate_limit`, measured never ran | 6.4 s — **fine** | quota / account state |

Neither cause is a code or pipeline defect, and they do not share a root: c4 and c1 have
latency headroom but no quota; c5 has quota but no speed. Swapping profiles therefore does
**not** unblock the window — it trades one NO-GO for a different one.

**The c1 reading also says the wait is not "until tomorrow".** It was taken at 02:37Z on a
FRESH UTC day and still returned `rate_limit`, so whatever cap is binding does not reset at
the UTC date boundary — consistent with the per-account rolling windows / weekly caps the
`.ai_state` journal records elsewhere (the 24-07 c2 session-limit note). A future session
should not assume a date change has cleared anything; it should re-probe and read the answer.

c5's numbers sit squarely in the degradation band this repo has tracked since mid-July
(H963 16-07: 104 870 ms; H1110 18-07: 98 625 ms; the c4 rows of 22-07/23-07: 59 831 ms and
168 352 ms), and match [H898](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H898-Opus_SanskritLexicography_pwg-ru-latency-characterization-payload-route-sweep_14.07.26.md)'s
finding that the breach is **size-independent route jitter**, not payload size — an
identical 6 828 B prompt read 16 621 ms on c4 at the 22-07 LIVE_GO and 53–60 s here.

**Operational note:** c5 is the profile this session itself runs on. A paid window on c5
would compete with interactive sessions for the same quota — worth weighing before
choosing it as the production lane, independently of today's latency verdict.

## Provenance caveat, stated rather than quietly fixed

The two c5 rows above carry `h963-c4-single-profile-gate0-2026-07-16/…` as their run-id
prefix: the campaign label was still c4-only when this reading was taken, and was made
account-aware (`campaign_for()`) in the same pass. The rows' own `account: c5` field is
authoritative, and they live in the c5-only events file. Rows written from now on read
`h963-c5-single-profile-gate0/…`. The reading itself is untouched — a label is not
re-derivable evidence, so it is documented, not rewritten.

## Resume condition

Unchanged and profile-independent: **make no paid translation call** until a **NEW**
representative ≥ 5 KB health call returns PASS on the profile that will run the window. A
prior GO — including H1447's 22-07 c4 LIVE_GO — authorizes nothing. Both profiles are
currently NO-GO for different reasons; c4 needs its quota window to roll, c5 needs the
route to recover.

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H858-Opus_SanskritLexicography_pwg_ru_sense_fidelity_anchor_repair_13.07.26.md and execute it.
```

_Dr. Mārcis Gasūns_
