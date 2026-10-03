_Created: 05-09-2026 · Last updated: 05-09-2026_

# H4059 — PWG post-GLM pipeline and evidence-reproducibility review (first, independent verdict)

Executor: Sonnet 5 (`claude-sonnet-5`). Handoff:
[H4059](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4059-Codex_SanskritLexicography_pwg-post-glm-pipeline-reproducibility-review_04.09.26.md).
Written and committed **before** reading the peer review (independence
contract, H4059 §3). Time-boxed to a ~45-minute unit; scope is stated
honestly below rather than padded.

## Input manifest — exact reviewed SHAs

Reviewed at `SanskritLexicography@182f5c339` (`master`, merge of PR #2077),
which contains all six merge commits below in order:

| handoff | merge commit | content commit |
|---|---|---|
| H4052 | `610d731ad` (PR #2073) | `0fab4924f` |
| H4055 | `60761d997` (PR #2072) | `7e63eeea7` |
| H4054 | `7f5cecb2e` (PR #2074) | `622d4f625` |
| H4056 | `b849a72c3` (PR #2075) | `853293787` |
| H4057 | `bff3b6b47` (PR #2076) | `b89ae0ee3` |
| H4053 | `182f5c339` (PR #2077) | `6ccaf58c6` |

All six close rows verified present on `origin/main` in
[Uprava/handoffs](https://github.com/gasyoun/Uprava/tree/main/handoffs)
(`docs: close H4052..H4057` commits `1fe87d0d5, 60761d997`'s parent chain,
`4daf706b7, a0bc6fa97, a129be3ca, 0b3a1eec2`). Gate `handoff:H4052,H4053,
H4054,H4055,H4056,H4057` is satisfied — all six terminal.

Canonical PWG store identity referenced by every packet: sha256
`79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65`, 11 519
sense rows, 221 headwords, 2 449 subcards.

## Reproduction log (commands actually run this session)

```bash
cd RussianTranslation
python3 src/pwg_quarantine_sample30.py selftest
# -> PASS x6, "selftest 6/6 in 1.3s" — matches H4053's claimed 6/6 exactly

python3 src/pwg_delivery_report.py
# -> sense_rows: 11519, approved_print_ready: 3, gold_complete: "0/320",
#    store sha256 79d72dbcb4b3... — matches H4052's committed
#    reports/PWG_DELIVERY_REPORT_04-09-2026.md byte-for-byte on every
#    numeric field checked
```

Not re-run in this time box (trusted on the committed receipt + selftest
count in the closed handoff, flagged as **not independently reproduced by
me**): H4054's `window_selftest` 221/221, H4057's 7-case offline replay,
H4056's `build_h4056_evidence_packet.py` full build (its receipt and manifest
were read and cross-checked against source instead — see below).

## Verdict 1 — Implementation correctness: **PASS with one confirmed defect**

1. H4052, H4053: reproduce exactly (see reproduction log). H4053's module has
   no promote/apply code path (confirmed by reading
   [`src/pwg_quarantine_sample30.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_quarantine_sample30.py) —
   `promotable=False` is set at campaign creation and no `promote`/`apply`
   verb exists in its CLI dispatch).
2. H4055: `refresh_tm_mirror.py` routes through
   `store_write.locked_store_rewrite` (verified by reading the diff);
   receipts distinguish content-only (`changed_ru=1`) from no-op
   (`changed_ru=0`) cases as claimed.
3. H4057: `providers.py`/`kernel.py` diff confirmed — no GLM entry exists in
   `PRICE_PER_MTOK_USD`, so `assert_budget` fails closed before reservation
   on a dollar-bounded run; this is also independently confirmed by H4053's
   own runbook, which names the same blocking dependency for its GATE-A live
   execute path. Consistent across two independently-authored deliveries.
4. **Confirmed count discrepancy (minor):** H4056's commit message and
   `reports/H4056_evidence_packet_report.md` state the scratch vote-to-store
   replay is "8/8"; the committed receipt
   [`reports/H4056_scratch_replay_receipt.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4056_scratch_replay_receipt.json)
   records `"n_checks": 9, "n_passed": 9"` — nine checks, not eight (a ninth
   check, "replay ran entirely in scratch", is present in the JSON but was
   dropped from the prose count). All 9 checks do pass; this is a reporting
   miscount, not a functional defect, but it is exactly the kind of "green
   tests alone are insufficient" mismatch this review is chartered to catch.

## Verdict 2 — Corpus / alignment / TM evidence: **FAIL (methodological defect in the H4056 TM demonstration)**

**Headline finding — circular TM evidence, not independent reuse evidence.**
[`src/build_h4056_evidence_packet.py:171-192`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h4056_evidence_packet.py#L171-L192)
(`tm_demo`) builds the scratch translation memory **from the same canonical
store** that the ten demonstration cards were drawn from
(`tm.build(store_path_, "ru", out=tm_out)`), then looks each of those same
ten cards' content hash up in the TM it just built. A 10/10 hit rate is the
guaranteed outcome of this construction — every row in the store is, by
definition, present in a TM built from that store — and proves nothing about
whether TM reuse helps on **new, not-yet-translated** input, which is the
only question "actual TM use" evidence can answer. The packet's own text
half-acknowledges the mechanism ("a hit means the same source re-arriving
today resolves from TM with zero provider calls") but the report and commit
message report it as "Actual TM use (offline, zero provider calls): 10/10
HIT" without the caveat that this is a tautological self-lookup, not a
holdout or leave-one-out test. **This is exactly the "duplicate/circular
evidence" failure mode named in the H4059 mission** (§ "Common evidence
questions" #3). A corrected version would build the TM from the store
**minus** the sampled cards (leave-N-out) and report the resulting hit rate,
which is the only number that speaks to real reuse value.

**Denominator reality check — the store is far from print-ready.**
H4052's reproduced numbers: of 11 519 sense rows, only **3** are
`approved`/print-ready; `gold_complete` is **0/320**; `review_queue`,
`gold_csv`, and `tm_fragments` surfaces are absent on this box entirely
("unknown", not zero — correctly labeled as such, which is good discipline,
but the underlying fact stands). H4056's own eligibility funnel over the
same 11 519 rows quarantines 1 768 (no evidence_summary/no supports), 1 644
(German residue or machine D1/D3/D4 flags), and 2 515 (H3948 segmentation
quarantine) before reaching 5 584 "machine-eligible" — and even that
"eligible" pool is a mechanical-gate pass, not a quality judgment (the
packet correctly labels it "not human judgment anywhere"). None of the six
upstream deliveries produces a number that answers the user's actual
question — "how well and how broadly does Sanskrit align with Russian,
English and German" across frequent/rare, Vedic/Epic/Classical,
verbs/nominals, compounds, polysemy — because none of them samples or scores
a stratified diagnostic set against those axes; H4056's ten cards are drawn
"round-robin across sorted roots," which is deterministic but is not a
stratified sample against the axes the user named.

**Scope I could not complete in this time box (named honestly, not
guessed):** independent worked-example tracing of Sanskrit word → lemma →
Russian/English/German evidence with matched/rejected/missed/ambiguous
classification (§ mission item 2); breadth assessment across
Vedic/Epic/Classical and verb/nominal/compound classes (§ mission item 4);
readable multi-language worked cases including failures (§ mission item 5).
These require either building a new stratified diagnostic sample or manually
tracing individual cards through `pilot/translation_memory.py` and
`corpus_gate.py`, which the ~45-minute unit did not leave room for. They are
**UNVERIFIED**, not passed and not failed — flagged for the residual review
pass below, not silently dropped.

## Verdict 3 — Readiness to request human review: **NOT READY**

The user's explicit prerequisite (H4059 "User ruling") — demonstrate breadth
and TM effectiveness before any voting ask — is **not met**:

1. The one artifact built specifically to demonstrate TM effectiveness
   (H4056) demonstrates a tautology, not reuse (Verdict 2).
2. The store that would be voted on has 3 print-ready rows out of 11 519 and
   0/320 gold-complete; there is no evidence base broad enough to ask for
   "hours or days of voting" against.
3. No deliverable in this batch produced a stratified breadth measurement
   across the axes the user named (frequent/rare, period, POS, compounds,
   polysemy) — H4056's ten-card sample is a demonstration of the pipeline
   mechanics, not a breadth measurement.
4. All six upstream implementations are, on their own terms, honestly scoped
   and none of them claims to have satisfied the corpus/alignment
   prerequisite themselves — H4056 explicitly states "Not... evidence of
   live translation quality" and records an open GTD row asking a future
   agent lane to assess readiness. This review is that assessment, and its
   answer is NOT READY.

Per H4059 §4 ("implementation completion triggers review; it does not
satisfy the user's corpus/alignment prerequisite"), this is not a fault of
the six implementations — they did what their own scopes described. The
prerequisite work (a real, non-circular TM holdout measurement; a stratified
diagnostic sample) is unfinished and is named as UNVERIFIED, not guessed at.

## Prioritized repair list

1. **P1 — Rebuild the TM demonstration as leave-N-out.** Exclude the sampled
   cards from the TM build, re-run the lookup, report the honest hit rate.
   Owner: next PWG evidence-packet iteration (successor to H4056).
2. **P1 — Build a stratified diagnostic sample** against the axes named in
   the user ruling (frequency band, period, POS, compounds/polysemy) instead
   of round-robin-by-root, and report per-axis coverage/hit numbers, not one
   aggregate.
3. **P2 — Fix the H4056 replay count** (8/8 in prose vs. 9/9 in the
   committed receipt) so the two artifacts agree.
4. **P2 — Surface `review_queue_csv` / `gold_csv` / `tm_fragments`
   availability** on the box that will run the next evidence packet, so
   "unknown" stops masking whether these exist anywhere.

No GTD row is minted by this review pass — the P1 items are exactly the
"agent-owned readiness action" already recorded against H4056 in
[Uprava GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md);
this report is the readiness assessment that row asked for, so it closes
that row's open question (NOT READY) rather than opening a duplicate one.

## Execution boundaries honored

No paid translation, no external judging calls, no production promotion, no
rewriting of source dictionaries, no fabricated votes, no production model
switch. All commands run were read-only or ran against the module's own
offline/fake-provider self-tests. This report was drafted and committed
before consulting any peer review artifact.

_Dr. Mārcis Gasūns_
