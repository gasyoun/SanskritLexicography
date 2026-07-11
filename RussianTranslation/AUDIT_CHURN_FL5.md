# FL5 — what "text signal" means for an attested sense, and why the churn happened

_Created: 02-07-2026 · Last updated: 11-07-2026_

Companion to the S10 audit
[`ARCHITECTURE_AUDIT_2026-07-02.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ARCHITECTURE_AUDIT_2026-07-02.md)
§3 (flag **FL5**) and the run-log finding
[`RUN_LOG.md` F-gate-nws-fp](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md).
Model: Opus 4.8 (`claude-opus-4-8`).

## The symptom

`suspicious_attested_without_text_signal` was **66 % of round-2 semantic risks** and drove
**2,152 key-requeues on 2026-06-29 alone** — requeues that **no re-translation can clear**
(`pw01` scored *worse* on a clean re-run, 810→1430, purely from emit-noise). It was the
single largest audit-side failure generator last week — more churn than every real
translation failure combined.

## Why the flag fired falsely

The check in
[`prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)
fires when a sense is `source_type=attested` but `has_text_signal()` finds no grounding.
Originally "text signal" meant **only** a literary citation (`<ls>`, ṚV, MBH, Manu, …) or a
non-empty `stratum`. Two whole classes of legitimate attested sense carry neither:

1. **Owner-cited NWS senses** (`[NWS: Graßmann 1873 (1996) : 81]`, `MW : 47`) — grounding
   lives in `equivalence_type`, which the citation scan skipped. *(Fixed in S10 — owner
   citations + a card-level signal now suppress the per-sense flag.)*
2. **Senses that assert no meaning at all** — pure cross-references
   (`{#paryanu#} <ab>s.</ab> {#paryanubanDa#}` = "paryanu, see paryanubandha"),
   editorial errata (`<ab>Z.</ab> 3 lies … <info n="rev"/>` = "line 3 read X instead of Y"),
   and structural headers (desiderative / preverb headers). These have **nothing to cite** —
   there is no attested *meaning* in a redirect — so "no text signal" is expected, not
   suspicious. A redirect can never acquire a citation, so the requeue loop was unwinnable
   by construction.

## The redesign (this PR)

**A "text signal" for an attested sense is now any of:** a literary citation, a non-empty
`stratum`, an NWS owner citation, **or a lexicographic citation** (Amara / Pāṇini / Medinī /
kośa …). A lexicographic attribution *is* textual grounding for an attested meaning, so it
counts. The card-level suppressor was widened the same way.

**And the flag only fires on a sense that makes a translatable meaning claim** — operationally,
a sense that carries a `{%…%}` gloss span, the pipeline's own marker for "this German is a
gloss to render." A sense with no gloss span asserts no meaning and is therefore exempt.

The flag stays **report-only**: it is a review hint, never a requeue trigger. This is now
enforced structurally — `suspicious_attested_without_text_signal` sits in a new
`REPORT_ONLY_RISKS` set with a module-load invariant that it can never intersect
`HIGH_CONFIDENCE_RISKS` (the only set the requeue list is built from). If a future edit
promotes it to high-confidence, the import fails loudly instead of silently re-arming the
churn loop.

## Validation against known-good cards

Measured across the **39 Slice-C `wf_output.sc.*.json`** files (1,128 cards, 5,857 attested
senses):

| | fires | nature of the fires |
|---|---:|---|
| before this PR (post-S10 card-level fix) | **37** | 21 pure cross-references + 16 errata / connective-only fragments — all noise |
| after this PR | **6** | every one a genuine `{%…%}` meaning gloss marked attested with **no** citation — the real review target |

The requeue set is provably unchanged. Same-base before/after on
`wf_output.sc.pat.json` (local-only, gitignored):
suspicious fires **7 → 3**, review-queue keys **26 → 24**, requeue set **byte-identical**
(12 keys). On `wf_output.sc.vas.json` (already clean of this flag) everything is identical.

`src/pilot/window_selftest.py` gains `test_report_only_risks_never_requeue` and
`test_attested_text_signal_redesign` (cross-ref / erratum never fire; lexicographic citation
counts; a genuine uncited meaning gloss still surfaces). Full suite green (19/19).

_Dr. Mārcis Gasūns_
